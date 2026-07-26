#!/usr/bin/env python3
"""Чистая модель провенанса заявок слоя кода и калибровок.

Источник истины остаётся в CSV. Этот модуль разбирает evidence, строит граф заявок,
вычисляет эффективную уверенность по слабейшему звену и обратный impact. Memgraph
здесь не импортируется: загрузчик использует ту же модель, что и unit-тесты.
"""
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
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

# Порядок меток совпадает с приоритетом разрешения адреса в load_code.py.
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
TERMINAL = frozenset({"rom_const", "spec", "registry", "site"})
PROCESS = frozenset({"wave", "arg"})
VOCAB = frozenset(EDGE_ROLES) | TERMINAL | PROCESS

ADDR_RE = re.compile(r"^[0-9a-f]{8}$")
EDGE_REF_RE = re.compile(r"^([0-9a-f]{8})(?:\+(?:0x[0-9a-f]+|\d+))?$")
ROM_CONST_SCALAR = r"(?:-?\d+|0x[0-9a-f]+|[0-9a-f]+)"
ROM_CONST_BINDING_RE = re.compile(
    rf"^([0-9a-f]{{8}})=(?:{ROM_CONST_SCALAR}|\d+(?:\*\d+)+|"
    rf"\[(?:{ROM_CONST_SCALAR})(?:,(?:{ROM_CONST_SCALAR}))*\])$"
)


class ProvenanceError(ValueError):
    """Ошибка схемы или несогласованность графа заявок."""


@dataclass(frozen=True, order=True)
class ClaimKey:
    rom: str
    label: str
    addr: str
    prop: str

    def __post_init__(self):
        if self.label not in PROPS_BY_LABEL:
            raise ProvenanceError(f"неизвестная метка заявки {self.label!r}")
        if not ADDR_RE.match(self.addr):
            raise ProvenanceError(f"адрес заявки не 8 hex-цифр: {self.addr!r}")
        if self.prop not in RANKED_PROPS:
            raise ProvenanceError(f"свойство заявки не ранжируется: {self.prop!r}")
        if self.prop not in PROPS_BY_LABEL[self.label]:
            raise ProvenanceError(
                f"{self.label}.{self.prop} не существует; допустимо "
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
            raise ProvenanceError(f"роль ребра вне словаря: {self.role!r}")
        if self.target_label not in EDGE_ROLES[self.role]:
            raise ProvenanceError(
                f"роль {self.role} не может адресовать {self.target_label}"
            )
        if not ADDR_RE.match(self.target_addr):
            raise ProvenanceError(f"адрес цели не 8 hex-цифр: {self.target_addr!r}")
        if edge_target(self.ref) != self.target_addr:
            raise ProvenanceError(
                f"ссылка {self.ref!r} не адресует цель {self.target_addr}"
            )
        if self.target_prop not in TARGET_PROPS:
            raise ProvenanceError(f"неизвестное свойство цели {self.target_prop!r}")
        if (self.target_prop != STRUCTURAL
                and self.target_prop not in PROPS_BY_LABEL[self.target_label]):
            raise ProvenanceError(
                f"{self.target_label}.{self.target_prop} не существует"
            )
        if self.role == "from_map" and self.target_prop != STRUCTURAL:
            raise ProvenanceError("from_map обязан ссылаться на @structural")

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
        """Полная цель, включая structural, для обратного impact."""
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
            raise ProvenanceError(f"неизвестная метка структуры {self.label!r}")
        if not ADDR_RE.match(self.addr):
            raise ProvenanceError(f"адрес структуры не 8 hex-цифр: {self.addr!r}")

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
    """Адрес начала цели из `addr` либо `addr+offset`."""
    match = EDGE_REF_RE.match(ref)
    return match.group(1) if match else None


def parse_evidence(text, source_prop, context="evidence"):
    """Разобрать claim-specific evidence в типизированные токены.

    Адресный токен обязан назвать свойство цели: `role:addr@target_prop`.
    Терминал и метаданные процесса свойства цели не имеют.
    """
    if source_prop not in RANKED_PROPS:
        raise ProvenanceError(f"{context}: неизвестное source property {source_prop!r}")
    tokens = []
    seen = set()
    for raw in text.split(";"):
        raw = raw.strip()
        if not raw:
            continue
        if ":" not in raw:
            raise ProvenanceError(f"{context}: токен без класса: {raw!r}")
        role, value = raw.split(":", 1)
        value = value.strip()
        if role not in VOCAB:
            raise ProvenanceError(
                f"{context}: класс {role!r} вне словаря {sorted(VOCAB)}"
            )
        if not value:
            raise ProvenanceError(f"{context}: пустое значение {role}:")
        if role in EDGE_ROLES:
            if "@" not in value:
                raise ProvenanceError(
                    f"{context}: адресный токен без @target_prop: {raw!r}"
                )
            ref, target_prop = value.rsplit("@", 1)
            target = edge_target(ref)
            if target is None:
                raise ProvenanceError(
                    f"{context}: ссылка не имеет формы addr[+offset]: {ref!r}"
                )
            if target_prop not in TARGET_PROPS:
                raise ProvenanceError(
                    f"{context}: target property {target_prop!r} вне "
                    f"{sorted(TARGET_PROPS)}"
                )
            if role == "from_map" and target_prop != STRUCTURAL:
                raise ProvenanceError(
                    f"{context}: from_map зависит от структуры, нужен @structural"
                )
            token = EvidenceToken(
                source_prop, role, ref, target, target_prop
            )
        else:
            if "@" in value:
                raise ProvenanceError(
                    f"{context}: терминал/метаданные не принимают @target_prop: {raw!r}"
                )
            token = EvidenceToken(source_prop, role, value)
        if token in seen:
            raise ProvenanceError(f"{context}: повтор evidence-токена {raw!r}")
        seen.add(token)
        tokens.append(token)
    return tokens


def format_evidence_token(token):
    """Сериализовать типизированный evidence-токен в каноническую форму."""
    if token.is_dependency:
        return f"{token.role}:{token.value}@{token.target_prop}"
    return f"{token.role}:{token.value}"


def canonical_evidence_tokens(text, source_prop, context="evidence"):
    """Разобрать evidence единым parser и вернуть канонические токены в исходном порядке."""
    return [
        format_evidence_token(token)
        for token in parse_evidence(text, source_prop, context)
    ]


def evidence_machine_anchor(token):
    """Вернуть машинный адрес, если он определён грамматикой токена без эвристики."""
    if token.is_dependency:
        return token.target_addr
    if token.role == "site" and ADDR_RE.fullmatch(token.value):
        return token.value
    if token.role == "rom_const":
        match = ROM_CONST_BINDING_RE.fullmatch(token.value)
        if match:
            return match.group(1)
    return None


def target_property_allowed(label, prop):
    return prop == STRUCTURAL or prop in PROPS_BY_LABEL.get(label, ())


def _strongly_connected(nodes, adjacency):
    """Tarjan SCC с детерминированным порядком обхода."""
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
    """Вычислить effective confidence на condensation DAG графа заявок.

    Цикл не подтверждает себя: SCC получает минимум локальных уровней и всех внешних
    зависимостей. Grounding считается отдельно от уровня.
    """
    levels = dict(levels)
    for claim, level in levels.items():
        if level not in LEVEL_RANK:
            raise ProvenanceError(f"{claim.short()}: уровень {level!r} вне лестницы")
    adjacency = {claim: set() for claim in levels}
    self_loops = set()
    for dep in dependencies:
        if dep.source not in levels:
            raise ProvenanceError(f"нет исходной заявки {dep.source.short()}")
        target = dep.target
        if target is None:
            continue
        if target not in levels:
            raise ProvenanceError(
                f"{dep.source.short()}: целевая заявка {target.short()} не имеет уровня"
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
    """Кратчайший детерминированный путь ranked-зависимостей между заявками."""
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
    """Зависимые заявки и минимальная глубина от изменённой claim identity."""
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
    """Точное сравнение проекции, включая дубликаты и stale-рёбра."""
    exp, got = Counter(expected), Counter(actual)
    return ProjectionDiff(
        missing=exp - got,
        extra=got - exp,
        duplicate_expected=Counter({k: n for k, n in exp.items() if n > 1}),
        duplicate_actual=Counter({k: n for k, n in got.items() if n > 1}),
    )
