#!/usr/bin/env python3
"""Pure provenance model for code and calibration-layer claims.

CSV remains the source of truth. This module parses evidence, builds a claim graph,
computes effective confidence from the weakest link, and calculates reverse impact.
Memgraph is not imported here: the loader and unit tests use the same model.
"""
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
import keyword
import re

LEVELS = ("pattern", "candidate", "code", "silicon")
LEVEL_RANK = {level: rank for rank, level in enumerate(LEVELS)}
RANKED_PROPS = frozenset({"confidence", "contract_conf", "scale_conf"})
STRUCTURAL = "structural"
TARGET_PROPS = RANKED_PROPS | {STRUCTURAL}

PROPS_BY_LABEL = {
    "Func": frozenset({"confidence", "contract_conf"}),
    "Reg": frozenset({"confidence"}),
    "Map": frozenset({"confidence", "scale_conf"}),
    "Axis": frozenset({"confidence", "scale_conf"}),
}

# Label order matches address-resolution precedence in load_code.py.
EDGE_ROLES = {
    "consumer": ("Func", "Reg"),
    "writes": ("Reg", "Func"),
    "indexed_by": ("Reg", "Axis", "Func", "Map"),
    "selector": ("Reg", "Func"),
    "threshold": ("Reg", "Map"),
    "from_map": ("Map", "Axis"),
    "homolog": ("Func",),
    "trace": ("Func",),
    "base": ("Reg",),
    "match": ("Map", "Axis"),
}
CATALOG_ROLES = frozenset({"from_map", "match"})
TERMINAL = frozenset({"rom_const", "spec", "registry", "site", "indirect_base", "test"})
PROCESS = frozenset({"wave", "arg"})
VOCAB = frozenset(EDGE_ROLES) | TERMINAL | PROCESS

ADDR_RE = re.compile(r"^[0-9a-f]{8}$")
EDGE_REF_RE = re.compile(r"^([0-9a-f]{8})(?:\+(?:0x[0-9a-f]+|\d+))?$")
INDIRECT_BASE_RE = re.compile(r"([0-9a-f]{8})\+(0x[0-9a-f]+|[0-9]+)")
TEST_RE = re.compile(r"((?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\.py)#([A-Za-z_][A-Za-z0-9_]*)")
ROM_CONST_SCALAR = r"(?:-?\d+|0x[0-9a-f]+|[0-9a-f]+)"
ROM_CONST_BINDING_RE = re.compile(
    rf"^([0-9a-f]{{8}})=(?:{ROM_CONST_SCALAR}|\d+(?:\*\d+)+|"
    rf"\[(?:{ROM_CONST_SCALAR})(?:,(?:{ROM_CONST_SCALAR}))*\])$"
)


class ProvenanceError(ValueError):
    """Schema error or claim-graph inconsistency."""


@dataclass(frozen=True, order=True)
class ClaimKey:
    rom: str
    label: str
    addr: str
    prop: str

    def __post_init__(self):
        if self.label not in PROPS_BY_LABEL:
            raise ProvenanceError(f"unknown claim label {self.label!r}")
        if not ADDR_RE.match(self.addr):
            raise ProvenanceError(f"claim address is not eight hexadecimal digits: {self.addr!r}")
        if self.prop not in RANKED_PROPS:
            raise ProvenanceError(f"claim property is not ranked: {self.prop!r}")
        if self.prop not in PROPS_BY_LABEL[self.label]:
            raise ProvenanceError(
                f"{self.label}.{self.prop} does not exist; allowed: "
                f"{sorted(PROPS_BY_LABEL[self.label])}"
            )

    def short(self):
        return f"{self.label}:{self.addr}.{self.prop}"


@dataclass(frozen=True, order=True)
class EvidenceToken:
    source_prop: str
    role: str
    value: str
    target_addr: str | None = None
    target_prop: str | None = None

    @property
    def is_dependency(self):
        return self.role in EDGE_ROLES

    @property
    def is_terminal(self):
        return self.role in TERMINAL

    @property
    def is_process(self):
        return self.role in PROCESS


@dataclass(frozen=True, order=True)
class Dependency:
    source: ClaimKey
    role: str
    target_label: str
    target_addr: str
    target_prop: str
    ref: str

    def __post_init__(self):
        if self.role not in EDGE_ROLES:
            raise ProvenanceError(f"relationship role is outside the vocabulary: {self.role!r}")
        if self.target_label not in EDGE_ROLES[self.role]:
            raise ProvenanceError(
                f"role {self.role} cannot target {self.target_label}"
            )
        if not ADDR_RE.match(self.target_addr):
            raise ProvenanceError(f"target address is not eight hexadecimal digits: {self.target_addr!r}")
        if edge_target(self.ref) != self.target_addr:
            raise ProvenanceError(
                f"reference {self.ref!r} does not address target {self.target_addr}"
            )
        if self.target_prop not in TARGET_PROPS:
            raise ProvenanceError(f"unknown target property {self.target_prop!r}")
        if (self.target_prop != STRUCTURAL
                and self.target_prop not in PROPS_BY_LABEL[self.target_label]):
            raise ProvenanceError(
                f"{self.target_label}.{self.target_prop} does not exist"
            )
        if self.role == "from_map" and self.target_prop != STRUCTURAL:
            raise ProvenanceError("from_map must reference @structural")

    @property
    def target(self):
        if self.target_prop == STRUCTURAL:
            return None
        return ClaimKey(
            self.source.rom,
            self.target_label,
            self.target_addr,
            self.target_prop,
        )

    @property
    def target_identity(self):
        """Return the complete target, including structural identity, for reverse impact."""
        if self.target_prop == STRUCTURAL:
            return StructuralKey(
                self.source.rom, self.target_label, self.target_addr
            )
        return self.target

    def projection_key(self):
        return (
            self.source.label,
            self.source.addr,
            self.source.prop,
            self.role,
            self.target_label,
            self.target_addr,
            self.target_prop,
            self.ref,
        )


@dataclass(frozen=True, order=True)
class StructuralKey:
    rom: str
    label: str
    addr: str

    def __post_init__(self):
        if self.label not in PROPS_BY_LABEL:
            raise ProvenanceError(f"unknown structural label {self.label!r}")
        if not ADDR_RE.match(self.addr):
            raise ProvenanceError(f"structural address is not eight hexadecimal digits: {self.addr!r}")

    @property
    def prop(self):
        return STRUCTURAL

    def short(self):
        return f"{self.label}:{self.addr}.{STRUCTURAL}"


@dataclass
class ClaimAnalysis:
    effective: dict[ClaimKey, str]
    weakest: dict[ClaimKey, ClaimKey]
    grounded: dict[ClaimKey, bool]
    component: dict[ClaimKey, int]
    cyclic_components: list[tuple[ClaimKey, ...]]
    ungrounded_cycles: list[tuple[ClaimKey, ...]]

    def below_declared(self, levels):
        return {
            claim: self.effective[claim]
            for claim, declared in levels.items()
            if LEVEL_RANK[self.effective[claim]] < LEVEL_RANK[declared]
        }


def edge_target(ref):
    """Return the target start address from `addr` or `addr+offset`."""
    match = EDGE_REF_RE.match(ref)
    return match.group(1) if match else None


def parse_evidence(text, source_prop, context="evidence"):
    """Parse claim-specific evidence into typed tokens.

    An address token must name its target property: `role:addr@target_prop`.
    Terminal and process-metadata tokens have no target property.
    """
    if source_prop not in RANKED_PROPS:
        raise ProvenanceError(f"{context}: unknown source property {source_prop!r}")
    tokens = []
    seen = set()
    for raw in text.split(";"):
        raw = raw.strip()
        if not raw:
            continue
        if ":" not in raw:
            raise ProvenanceError(f"{context}: token has no class: {raw!r}")
        role, value = raw.split(":", 1)
        value = value.strip()
        if role not in VOCAB:
            raise ProvenanceError(
                f"{context}: class {role!r} is outside vocabulary {sorted(VOCAB)}"
            )
        if not value:
            raise ProvenanceError(f"{context}: empty value for {role}:")
        if role in EDGE_ROLES:
            if "@" not in value:
                raise ProvenanceError(
                    f"{context}: address token lacks @target_prop: {raw!r}"
                )
            ref, target_prop = value.rsplit("@", 1)
            target = edge_target(ref)
            if target is None:
                raise ProvenanceError(
                    f"{context}: reference does not have form addr[+offset]: {ref!r}"
                )
            if target_prop not in TARGET_PROPS:
                raise ProvenanceError(
                    f"{context}: target property {target_prop!r} is outside "
                    f"{sorted(TARGET_PROPS)}"
                )
            if role == "from_map" and target_prop != STRUCTURAL:
                raise ProvenanceError(
                    f"{context}: from_map depends on structure and requires @structural"
                )
            token = EvidenceToken(
                source_prop, role, ref, target, target_prop
            )
        else:
            if "@" in value:
                raise ProvenanceError(
                    f"{context}: terminal/metadata tokens do not accept @target_prop: {raw!r}"
                )
            if role == "indirect_base" and not INDIRECT_BASE_RE.fullmatch(value):
                raise ProvenanceError(
                    f"{context}: expected indirect_base:<address>+<offset>: {raw!r}"
                )
            if role == "test":
                found = TEST_RE.fullmatch(value)
                if (found is None or any(part in (".", "..") for part in found.group(1).split("/"))
                        or keyword.iskeyword(found.group(2))):
                    raise ProvenanceError(
                        f"{context}: expected test:<safe-relative-python-path>#<function>: {raw!r}"
                    )
            token = EvidenceToken(source_prop, role, value)
        if token in seen:
            raise ProvenanceError(f"{context}: duplicate evidence token {raw!r}")
        seen.add(token)
        tokens.append(token)
    return tokens


def format_evidence_token(token):
    """Serialize a typed evidence token in canonical form."""
    if token.is_dependency:
        return f"{token.role}:{token.value}@{token.target_prop}"
    return f"{token.role}:{token.value}"


def canonical_evidence_tokens(text, source_prop, context="evidence"):
    """Parse evidence with the shared parser and return canonical tokens in source order."""
    return [
        format_evidence_token(token)
        for token in parse_evidence(text, source_prop, context)
    ]


def evidence_machine_anchor(token):
    """Return a machine address when token grammar defines one without heuristics."""
    if token.is_dependency:
        return token.target_addr
    if token.role == "site" and ADDR_RE.fullmatch(token.value):
        return token.value
    if token.role == "indirect_base":
        match = INDIRECT_BASE_RE.fullmatch(token.value)
        if match:
            return match.group(1)
    if token.role == "rom_const":
        match = ROM_CONST_BINDING_RE.fullmatch(token.value)
        if match:
            return match.group(1)
    return None


def target_property_allowed(label, prop):
    return prop == STRUCTURAL or prop in PROPS_BY_LABEL.get(label, ())


def _strongly_connected(nodes, adjacency):
    """Compute Tarjan SCCs with deterministic traversal order."""
    index = 0
    indices = {}
    low = {}
    stack = []
    on_stack = set()
    components = []

    def visit(node):
        nonlocal index
        indices[node] = low[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for target in sorted(adjacency[node]):
            if target not in indices:
                visit(target)
                low[node] = min(low[node], low[target])
            elif target in on_stack:
                low[node] = min(low[node], indices[target])
        if low[node] == indices[node]:
            comp = []
            while True:
                member = stack.pop()
                on_stack.remove(member)
                comp.append(member)
                if member == node:
                    break
            components.append(tuple(sorted(comp)))

    for node in sorted(nodes):
        if node not in indices:
            visit(node)
    return components


def analyze_claims(levels, dependencies, grounded_claims=()):
    """Compute effective confidence on the claim graph's condensation DAG.

    A cycle does not substantiate itself: an SCC receives the minimum of local confidence
    levels and all external dependencies. Grounding is tracked separately from confidence.
    """
    levels = dict(levels)
    for claim, level in levels.items():
        if level not in LEVEL_RANK:
            raise ProvenanceError(f"{claim.short()}: confidence {level!r} is outside the ladder")
    adjacency = {claim: set() for claim in levels}
    self_loops = set()
    for dep in dependencies:
        if dep.source not in levels:
            raise ProvenanceError(f"source claim not found: {dep.source.short()}")
        target = dep.target
        if target is None:
            continue
        if target not in levels:
            raise ProvenanceError(
                f"{dep.source.short()}: target claim {target.short()} has no confidence level"
            )
        adjacency[dep.source].add(target)
        if dep.source == target:
            self_loops.add(dep.source)

    components = _strongly_connected(levels, adjacency)
    component = {
        claim: cid for cid, members in enumerate(components) for claim in members
    }
    outgoing = {cid: set() for cid in range(len(components))}
    for source, targets in adjacency.items():
        for target in targets:
            a, b = component[source], component[target]
            if a != b:
                outgoing[a].add(b)

    local_ground = {cid: False for cid in range(len(components))}
    for claim in grounded_claims:
        if claim in component:
            local_ground[component[claim]] = True
    for dep in dependencies:
        if dep.target_prop == STRUCTURAL:
            local_ground[component[dep.source]] = True

    comp_effective = {}
    comp_weakest = {}
    comp_grounded = {}

    def resolve(cid):
        if cid in comp_effective:
            return
        for target in sorted(outgoing[cid]):
            resolve(target)
        members = components[cid]
        weakest = min(members, key=lambda c: (LEVEL_RANK[levels[c]], c))
        rank = LEVEL_RANK[levels[weakest]]
        for target in sorted(outgoing[cid]):
            target_weakest = comp_weakest[target]
            target_rank = LEVEL_RANK[comp_effective[target]]
            if (target_rank, target_weakest) < (rank, weakest):
                rank, weakest = target_rank, target_weakest
        comp_effective[cid] = LEVELS[rank]
        comp_weakest[cid] = weakest
        comp_grounded[cid] = local_ground[cid] or any(
            comp_grounded[target] for target in outgoing[cid]
        )

    for cid in range(len(components)):
        resolve(cid)

    cyclic = []
    for cid, members in enumerate(components):
        if len(members) > 1 or any(member in self_loops for member in members):
            cyclic.append(members)
    ungrounded = [
        members for members in cyclic if not comp_grounded[component[members[0]]]
    ]
    return ClaimAnalysis(
        effective={claim: comp_effective[component[claim]] for claim in levels},
        weakest={claim: comp_weakest[component[claim]] for claim in levels},
        grounded={claim: comp_grounded[component[claim]] for claim in levels},
        component=component,
        cyclic_components=cyclic,
        ungrounded_cycles=ungrounded,
    )


def dependency_path(source, target, dependencies):
    """Return the shortest deterministic path of ranked dependencies between claims."""
    adjacency = defaultdict(set)
    for dep in dependencies:
        ranked_target = dep.target
        if ranked_target is not None:
            adjacency[dep.source].add(ranked_target)
    previous = {source: None}
    queue = deque([source])
    while queue:
        current = queue.popleft()
        if current == target:
            path = []
            while current is not None:
                path.append(current)
                current = previous[current]
            return list(reversed(path))
        for nxt in sorted(adjacency[current]):
            if nxt in previous:
                continue
            previous[nxt] = current
            queue.append(nxt)
    return []


def reverse_impact(changed, dependencies):
    """Return dependent claims and minimum depth from the changed claim identity."""
    incoming = defaultdict(set)
    for dep in dependencies:
        incoming[dep.target_identity].add(dep.source)
    depth = {changed: 0}
    queue = deque([changed])
    while queue:
        target = queue.popleft()
        for source in sorted(incoming[target]):
            if source in depth:
                continue
            depth[source] = depth[target] + 1
            queue.append(source)
    return depth


@dataclass
class ProjectionDiff:
    missing: Counter
    extra: Counter
    duplicate_expected: Counter
    duplicate_actual: Counter

    @property
    def clean(self):
        return not (self.missing or self.extra
                    or self.duplicate_expected or self.duplicate_actual)


def compare_projection(expected, actual):
    """Compare projections exactly, including duplicates and stale relationships."""
    exp, got = Counter(expected), Counter(actual)
    return ProjectionDiff(
        missing=exp - got,
        extra=got - exp,
        duplicate_expected=Counter({k: n for k, n in exp.items() if n > 1}),
        duplicate_actual=Counter({k: n for k, n in got.items() if n > 1}),
    )
