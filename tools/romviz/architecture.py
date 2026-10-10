#!/usr/bin/env python3
"""Derive, validate, and query the firmware architecture model.

`defs/JK08A.architecture.toml` projects the owned architecture entities. This
module validates that view against the ledger projections and supplies node
and edge helpers. Placed native meanings extend the reviewed inventory when
they have no legacy ledger row. The view places reviewed functions, declares peripheral
endpoints, and binds calculation chains with effects and signs. Layout
atlases read actual symbols and relations from kb through `graph_atlas.py`.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
import csv
from dataclasses import dataclass, field
import json
from pathlib import Path
import re
import sys
import tomllib


if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.memgraph import provenance
from kb import compile, repo


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = ROOT / "defs" / "JK08A.architecture.toml"
SCHEMA_VERSION = 1
ID_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
ADDRESS_RE = re.compile(r"^[0-9a-f]{8}$")
REFERENCE_RE = re.compile(
    r"^(?:(function|map|axis|signal|register):)?([0-9a-f]{8})$"
)
SPEC_ADDRESS_RE = re.compile(
    r"(?<![0-9A-Za-z_])(?:0x([0-9A-Fa-f]{1,8})"
    r"|(?:thunk_FUN|FUN|DAT|LAB)_([0-9A-Fa-f]{4,8})"
    r"|([0-9A-Fa-f]{8}))(?![0-9A-Za-z_])"
)
LANES = ("flow", "support")
DIRECTIONS = ("input", "output", "bidirectional")
SIGNS = ("positive", "negative", "none")
EFFECTS = (
    "adds",
    "compares",
    "converts",
    "copies",
    "detects",
    "drives",
    "feeds",
    "filters",
    "gates",
    "indexes",
    "integrates",
    "learns",
    "limits",
    "looks-up",
    "masks",
    "multiplies",
    "overrides",
    "receives",
    "scales",
    "schedules",
    "selects",
    "stores",
    "subtracts",
    "transmits",
)
EDGE_KINDS = ("data", "control", "call", "access", "pair")
FLOW_KINDS = frozenset({"data", "control"})
REVIEWED_KINDS = ("function", "map", "axis", "signal", "register")
NODE_KINDS = REVIEWED_KINDS + ("ram", "io", "rom", "other")
KIND_ORDER = {kind: index for index, kind in enumerate(NODE_KINDS)}
IO_BASE = 0xFFFFC000
RAM_BASE = 0xFFFE0000
ROM_LIMIT = 0x00200000
CONTRACT_PREFIX = "Not arithmetic: "
SOURCE_KEYS = ("functions", "variables", "findings", "maps", "axes", "presentation")
TOP_KEYS = frozenset(
    {"schema_version", "rom", "summary", "sources", "stage", "block", "endpoint", "chain"}
)
STAGE_KEYS = frozenset({"id", "name", "lane", "summary"})
BLOCK_KEYS = frozenset(
    {"id", "name", "stage", "summary", "specs", "functions", "maps", "signals", "generic"}
)
ENDPOINT_KEYS = frozenset(
    {"id", "name", "direction", "block", "peripheral", "summary", "registers", "functions", "specs"}
)
CHAIN_KEYS = frozenset({"id", "name", "summary", "quantity", "output", "specs", "step"})
STEP_KEYS = frozenset({"from", "to", "effect", "sign", "via", "note", "specs", "research"})
# Evidence columns per ledger: (row kind, ranked property, evidence column).
EVIDENCE_COLUMNS = {
    "functions": (("confidence", "evidence"), ("contract_conf", "contract_evidence")),
    "variables": (("confidence", "evidence"),),
    "findings": (("confidence", "evidence"), ("scale_conf", "scale_evidence")),
    "axes": (("scale_conf", "scale_evidence"),),
}
LABEL_KINDS = {
    "Func": ("function",),
    "Reg": ("signal", "register"),
    "Map": ("map",),
    "Axis": ("axis",),
}
# The blocks of this stage hold reviewed components whose functional role the
# ledgers do not establish yet; a map they read has a block but no role.
UNATTRIBUTED_STAGE = "unattributed"


class ArchitectureError(ValueError):
    """Raised when the architecture source disagrees with the tracked ledgers."""

    def __init__(self, errors):
        self.errors = list(errors)
        super().__init__("\n".join(self.errors))


def _repo_path(value):
    path = Path(value).expanduser()
    return path if path.is_absolute() else ROOT / path


def _display_path(path):
    path = Path(path)
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def _read_csv(path):
    with Path(path).open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        rows = []
        for row in reader:
            row["_line"] = reader.line_num
            rows.append(row)
    return rows


def first_sentence(value, fallback="", limit=96):
    """Return the first sentence of a ledger statement, shortened to a label."""
    text = " ".join((value or "").strip().split())
    if not text:
        return fallback
    sentence = re.split(r"(?<=[.!?])\s", text, maxsplit=1)[0]
    if len(sentence) <= limit:
        return sentence
    return sentence[: limit - 3].rstrip() + "..."


def _contract_statement(row):
    """Return a function contract without its classification prefix."""
    text = row.get("contract", "").strip()
    if text.startswith(CONTRACT_PREFIX):
        text = text[len(CONTRACT_PREFIX):]
        text = text[:1].upper() + text[1:]
    return text


def address_kind(value):
    """Classify an address that no ledger row names."""
    number = int(value, 16)
    if number >= IO_BASE:
        return "io"
    if number >= RAM_BASE:
        return "ram"
    if number < ROM_LIMIT:
        return "rom"
    return "other"


def _normalize(address):
    return f"{int(address, 16):08x}"


def spec_addresses(text):
    """Return every address a specification names in a normalized form."""
    found = set()
    for match in SPEC_ADDRESS_RE.finditer(text):
        value = next(group for group in match.groups() if group)
        if match.group(3) and not any(character.isdigit() for character in value):
            continue
        found.add(_normalize(value))
    return found


def combine_sign(first, second):
    """Compose the signs of two consecutive chain steps."""
    if "none" in (first, second):
        return "none"
    return "positive" if first == second else "negative"


def merge_signs(signs):
    """Collapse the composed signs of every path into one impact statement."""
    signs = set(signs)
    if not signs:
        return None
    if len(signs) == 1:
        return next(iter(signs))
    return "mixed"


@dataclass
class Node:
    id: str
    kind: str
    addr: str
    label: str
    text: str = ""
    note: str = ""
    confidence: str = ""
    role: str = ""
    units: str = ""
    source: str = ""
    meta: dict = field(default_factory=dict)
    block: str | None = None
    pinned: bool = False

    @property
    def reviewed(self):
        return self.kind in REVIEWED_KINDS


@dataclass
class Edge:
    source: str
    target: str
    kind: str
    roles: set = field(default_factory=set)
    origins: set = field(default_factory=set)


@dataclass
class Stage:
    id: str
    name: str
    lane: str
    summary: str


@dataclass
class Block:
    id: str
    name: str
    stage: str
    summary: str
    specs: tuple
    functions: tuple
    maps: tuple
    signals: tuple
    generic: bool


@dataclass
class Endpoint:
    id: str
    name: str
    direction: str
    block: str
    peripheral: str
    summary: str
    registers: tuple
    functions: tuple
    specs: tuple


@dataclass
class Step:
    source: str
    target: str
    effect: str
    sign: str
    via: tuple
    note: str
    specs: tuple
    support: str = ""
    research: dict | None = None


@dataclass
class Chain:
    id: str
    name: str
    summary: str
    quantity: str
    output: str
    specs: tuple
    steps: list
    impact: dict = field(default_factory=dict)


class Ledgers:
    """Tracked ledger rows keyed by normalized address."""

    def __init__(self, sources, rom):
        self.paths = {key: _repo_path(sources[key]) for key in SOURCE_KEYS}
        self.rows = {
            key: {
                row["addr"].strip().lower(): row
                for row in _read_csv(self.paths[key])
            }
            for key in ("functions", "variables", "findings", "axes")
        }
        self.map_rows = {
            row["table"].strip().lower(): row
            for row in _read_csv(self.paths["maps"])
        }
        with self.paths["presentation"].open("rb") as source:
            document = tomllib.load(source)
        self.presentation = {
            _normalize(key): {
                name: str(value).replace("{target_rom}", rom)
                for name, value in table.items()
                if name in {"name", "category"}
            }
            for key, table in document.get("table", {}).items()
        }

    @property
    def functions(self):
        return self.rows["functions"]

    @property
    def variables(self):
        return self.rows["variables"]

    @property
    def findings(self):
        return self.rows["findings"]

    @property
    def axes(self):
        return self.rows["axes"]


class Architecture:
    """Curated functional structure bound to the derived ledger graph."""

    def __init__(self, source=DEFAULT_SOURCE):
        self.source = _repo_path(source)
        self.errors = []
        with self.source.open("rb") as handle:
            self.raw = tomllib.load(handle)
        self._check_top()
        self.rom = self.raw.get("rom", "")
        self.summary = self.raw.get("summary", "")
        self.ledgers = Ledgers(self.raw["sources"], self.rom)
        self.nodes = {}
        self.edges = {}
        self._spec_cache = {}
        self._load_nodes()
        self._load_native_nodes()
        self._load_edges()
        self._index_edges()
        self.stages = self._load_stages()
        self.blocks = self._load_blocks()
        self.endpoints = self._load_endpoints()
        self.chains = self._load_chains()
        self._check_coverage()
        self._derive_blocks()
        self._check_map_attribution()
        self.flows = self._derive_flows()
        for chain in self.chains:
            chain.impact = self._chain_impact(chain)

    # Source schema.

    def _error(self, message):
        self.errors.append(f"{_display_path(self.source)}: {message}")

    def _check_top(self):
        raw = self.raw
        missing = sorted({"schema_version", "rom", "sources", "stage", "block"} - set(raw))
        extra = sorted(set(raw) - TOP_KEYS)
        if raw.get("schema_version") != SCHEMA_VERSION or missing or extra:
            raise ArchitectureError([
                f"{_display_path(self.source)}: unsupported architecture source; "
                f"schema_version={raw.get('schema_version')!r}; "
                f"missing={missing}; extra={extra}"
            ])
        sources = raw["sources"]
        if not isinstance(sources, dict) or set(sources) != set(SOURCE_KEYS):
            raise ArchitectureError([
                f"{_display_path(self.source)}: sources must name exactly "
                f"{list(SOURCE_KEYS)}"
            ])
        missing_files = [
            value for value in sources.values() if not _repo_path(value).is_file()
        ]
        if missing_files:
            raise ArchitectureError([
                f"{_display_path(self.source)}: missing ledger source {value}"
                for value in missing_files
            ])

    def _table(self, context, value, keys, required):
        if not isinstance(value, dict):
            self._error(f"{context} must be a table")
            return None
        missing = sorted(required - set(value))
        extra = sorted(set(value) - keys)
        if missing or extra:
            self._error(f"{context}: missing={missing}; extra={extra}")
            return None
        return value

    def _text(self, context, value, name, required=True):
        text = value.get(name, "")
        if not isinstance(text, str) or (required and not text.strip()):
            self._error(f"{context}.{name} must be a nonempty string")
            return ""
        return " ".join(text.split())

    def _identifier(self, context, value, seen):
        identifier = value.get("id", "")
        if not isinstance(identifier, str) or not ID_RE.fullmatch(identifier):
            self._error(f"{context}.id {identifier!r} is not a lowercase kebab identifier")
        elif identifier in seen:
            self._error(f"{context}.id {identifier!r} is duplicated")
        seen.add(identifier)
        return identifier

    def _list(self, context, value, name):
        items = value.get(name, [])
        if not isinstance(items, list) or any(not isinstance(item, str) for item in items):
            self._error(f"{context}.{name} must be an array of strings")
            return ()
        return tuple(item.strip() for item in items)

    def _specs(self, context, value):
        specs = self._list(context, value, "specs")
        for spec in specs:
            if not _repo_path(spec).is_file():
                self._error(f"{context}.specs names missing file {spec}")
        return specs

    # Ledger nodes.

    def _add_node(self, node):
        self.nodes[node.id] = node
        return node

    def _load_nodes(self):
        ledgers = self.ledgers
        path = _display_path(ledgers.paths["functions"])
        for addr, row in ledgers.functions.items():
            self._add_node(Node(
                id=f"function:{addr}",
                kind="function",
                addr=addr,
                label=first_sentence(
                    row["semantics"] or _contract_statement(row), f"FUN_{addr}"
                ),
                text=row["semantics"],
                note=row.get("note", ""),
                confidence=row.get("confidence", ""),
                role=row.get("role", ""),
                source=f"{path}:{row['_line']}",
                meta={
                    "contract": row.get("contract", ""),
                    "contractConfidence": row.get("contract_conf", ""),
                },
            ))
        path = _display_path(ledgers.paths["findings"])
        for addr, row in ledgers.findings.items():
            presentation = ledgers.presentation.get(addr, {})
            ledger = ledgers.map_rows.get(addr, {})
            self._add_node(Node(
                id=f"map:{addr}",
                kind="map",
                addr=addr,
                label=presentation.get("name")
                or first_sentence(row["semantics"], f"Map 0x{int(addr, 16):X}"),
                text=row["semantics"],
                note=row.get("note", ""),
                confidence=row.get("confidence", ""),
                role=row.get("role", ""),
                units=row.get("units", ""),
                source=f"{path}:{row['_line']}",
                meta={
                    "category": presentation.get("category", ""),
                    "dimension": ledger.get("dim", ""),
                    "storage": row.get("storagetype", ""),
                    "scale": row.get("scale_expr", ""),
                    "scaleConfidence": row.get("scale_conf", ""),
                    "family": row.get("family", ""),
                },
            ))
        path = _display_path(ledgers.paths["axes"])
        for addr, row in ledgers.axes.items():
            units = row.get("units", "")
            kind_name = row.get("kind", "").replace("_", " ").strip()
            self._add_node(Node(
                id=f"axis:{addr}",
                kind="axis",
                addr=addr,
                label=(units if units and units != "raw" else f"{kind_name.capitalize() or 'Axis'} axis 0x{int(addr, 16):X}"),
                text=row.get("note", ""),
                confidence=row.get("scale_conf", ""),
                role=row.get("kind", ""),
                units=units,
                source=f"{path}:{row['_line']}",
                meta={"scale": row.get("scale_expr", "")},
            ))
        path = _display_path(ledgers.paths["variables"])
        for addr, row in ledgers.variables.items():
            kind = "register" if int(addr, 16) >= IO_BASE else "signal"
            self._add_node(Node(
                id=f"{kind}:{addr}",
                kind=kind,
                addr=addr,
                label=first_sentence(row["semantics"], f"0x{int(addr, 16):08X}"),
                text=row["semantics"],
                note=row.get("note", ""),
                confidence=row.get("confidence", ""),
                units=row.get("units", ""),
                source=f"{path}:{row['_line']}",
            ))

    def _reviewed_id(self, addr, kinds=REVIEWED_KINDS):
        for kind in kinds:
            node_id = f"{kind}:{addr}"
            if node_id in self.nodes:
                return node_id
        return None

    def _load_native_nodes(self):
        """Placed canonical owners without a legacy row remain reviewed.

        Legacy rows retain their node metadata and relation contract. A native
        placement must resolve to an owned home-layout symbol, rather than an
        address appearing only in a literal, L0, or another layout.
        """
        knowledge = compile.cached(repo.ROOT)
        kinds = {"fn": "function", "tbl": "map", "axis": "axis",
                 "ram": "signal", "reg": "register"}
        for meaning in sorted(knowledge.meanings, key=lambda item: item.key):
            if not meaning.props.get("block") or meaning.kind not in kinds:
                continue
            symbol = meaning.symbols.get("7mfk")
            if symbol is None:
                continue
            owners = sorted(source for source in meaning.sources
                            if source.startswith("kb/"))
            if not owners:
                continue
            kind, addr = kinds[meaning.kind], f"{symbol.address:08x}"
            node_id = f"{kind}:{addr}"
            if node_id in self.nodes:
                continue
            summary = symbol.value("summary") or ""
            self._add_node(Node(
                id=node_id, kind=kind, addr=addr,
                label=first_sentence(summary, meaning.name or addr),
                text=summary, note="\n".join(symbol.value("note") or ()),
                confidence=symbol.value("level") or "",
                role=symbol.value("role") or "", units=symbol.value("unit") or "",
                source=";".join(owners),
                meta={"meaning": meaning.key, "layout": "7mfk", "origin": "kb"},
            ))

    def _unreviewed(self, addr):
        kind = address_kind(addr)
        node_id = f"{kind}:{addr}"
        if node_id not in self.nodes:
            names = {"ram": "Unreviewed RAM", "io": "Unreviewed I/O register", "rom": "Unreviewed ROM", "other": "Unreviewed address"}
            self._add_node(Node(
                id=node_id,
                kind=kind,
                addr=addr,
                label=f"{names[kind]} 0x{int(addr, 16):08X}",
            ))
        return node_id

    def _token_target(self, role, addr):
        kinds = tuple(
            kind
            for label in provenance.EDGE_ROLES[role]
            for kind in LABEL_KINDS[label]
        )
        return (
            self._reviewed_id(addr, kinds)
            or self._reviewed_id(addr)
            or self._unreviewed(addr)
        )

    # Derived relations.

    def _add_edge(self, source, target, kind, role, origin):
        if source == target:
            return
        edge = self.edges.get((source, target, kind))
        if edge is None:
            edge = self.edges[(source, target, kind)] = Edge(source, target, kind)
        edge.roles.add(role)
        edge.origins.add(origin)

    @staticmethod
    def _edge_rule(row_kind, role, target_kind):
        """Return (reverse, kind) for one evidence token, or None to skip it.

        `reverse` is true when data moves from the token target to the row.
        """
        target_class = (
            "code" if target_kind in {"function", "rom"}
            else "table" if target_kind in {"map", "axis"}
            else "data"
        )
        if role in {"homolog", "match"}:
            return None
        if role in {"indexed_by", "from_map"}:
            return True, "data"
        if role in {"selector", "threshold"}:
            return True, "control"
        if role == "base":
            return False, "pair"
        if row_kind == "function":
            if role == "writes":
                return False, "data"
            if role == "trace":
                return False, "call"
            if role == "consumer":
                return (False, "call") if target_class == "code" else (True, "data")
        if role == "trace":
            return False, "access"
        if role == "writes":
            return (True, "data") if target_class == "code" else (False, "data")
        if role == "consumer":
            return False, "data"
        return None

    def _load_edges(self):
        ledgers = self.ledgers
        for ledger, columns in EVIDENCE_COLUMNS.items():
            path = _display_path(ledgers.paths[ledger])
            for addr, row in ledgers.rows[ledger].items():
                row_id = {
                    "functions": f"function:{addr}",
                    "findings": f"map:{addr}",
                    "axes": f"axis:{addr}",
                    "variables": self._reviewed_id(addr, ("signal", "register")),
                }[ledger]
                row_kind = self.nodes[row_id].kind
                for prop, column in columns:
                    text = row.get(column, "") or ""
                    if not text.strip():
                        continue
                    context = f"{path}:{row['_line']}"
                    try:
                        tokens = provenance.parse_evidence(text, prop, context)
                    except provenance.ProvenanceError as error:
                        self._error(f"evidence cannot be parsed: {error}")
                        continue
                    for token in tokens:
                        if not token.is_dependency:
                            continue
                        target = self._token_target(token.role, token.target_addr)
                        rule = self._edge_rule(row_kind, token.role, self.nodes[target].kind)
                        if rule is None:
                            continue
                        reverse, kind = rule
                        source, sink = (target, row_id) if reverse else (row_id, target)
                        self._add_edge(source, sink, kind, token.role, context)
        path = _display_path(ledgers.paths["maps"])
        for addr, row in ledgers.map_rows.items():
            map_id = f"map:{addr}"
            if map_id not in self.nodes:
                self._error(f"{path}:{row['_line']}: map {addr} has no findings row")
                continue
            context = f"{path}:{row['_line']}"
            for accessor in filter(None, (row.get("accessors") or "").split(";")):
                target = self._reviewed_id(_normalize(accessor.strip()), ("function",))
                target = target or self._unreviewed(_normalize(accessor.strip()))
                self._add_edge(map_id, target, "data", "accessor", context)
            for column in ("axis_x", "axis_y"):
                for axis in filter(None, (row.get(column) or "").split(";")):
                    axis_id = self._reviewed_id(_normalize(axis.strip()), ("axis",))
                    axis_id = axis_id or self._unreviewed(_normalize(axis.strip()))
                    self._add_edge(axis_id, map_id, "data", column, context)

    def _index_edges(self):
        self.outgoing = defaultdict(list)
        self.incoming = defaultdict(list)
        self.adjacent = defaultdict(set)
        for edge in self.edges.values():
            self.outgoing[edge.source].append(edge)
            self.incoming[edge.target].append(edge)
            self.adjacent[edge.source].add(edge.target)
            self.adjacent[edge.target].add(edge.source)

    # Curated structure.

    def _load_stages(self):
        stages = []
        seen = set()
        for index, value in enumerate(self.raw.get("stage", [])):
            context = f"stage[{index}]"
            value = self._table(context, value, STAGE_KEYS, STAGE_KEYS)
            if value is None:
                continue
            identifier = self._identifier(context, value, seen)
            lane = value.get("lane")
            if lane not in LANES:
                self._error(f"{context}.lane {lane!r} is not one of {list(LANES)}")
            stages.append(Stage(
                identifier,
                self._text(context, value, "name"),
                lane,
                self._text(context, value, "summary"),
            ))
        return stages

    def _resolve(self, context, text, kinds=None, allow_unreviewed=False):
        """Resolve a source reference to a node id."""
        match = REFERENCE_RE.fullmatch(text or "")
        if not match:
            self._error(f"{context}: {text!r} is not an eight-digit lowercase address")
            return None
        prefix, addr = match.groups()
        if prefix:
            node_id = f"{prefix}:{addr}"
            if node_id not in self.nodes:
                self._error(f"{context}: {text} is not a reviewed {prefix}")
                return None
            if kinds and prefix not in kinds:
                self._error(f"{context}: {text} is a {prefix}, expected {'/'.join(kinds)}")
                return None
            return node_id
        node_id = self._reviewed_id(addr, kinds or REVIEWED_KINDS)
        if node_id:
            return node_id
        if allow_unreviewed:
            return self._unreviewed(addr)
        other = self._reviewed_id(addr)
        if other:
            self._error(f"{context}: {text} is a {self.nodes[other].kind}, expected {'/'.join(kinds)}")
        else:
            expected = "/".join(kinds or REVIEWED_KINDS)
            self._error(f"{context}: {text} is not a reviewed {expected} in the ledgers")
        return None

    def _load_blocks(self):
        blocks = []
        seen = set()
        stage_ids = {stage.id for stage in self.stages}
        for index, value in enumerate(self.raw.get("block", [])):
            context = f"block[{index}]"
            value = self._table(
                context, value, BLOCK_KEYS, {"id", "name", "stage", "summary", "functions"}
            )
            if value is None:
                continue
            identifier = self._identifier(context, value, seen)
            context = f"block {identifier}"
            stage = value.get("stage")
            if stage not in stage_ids:
                self._error(f"{context}.stage {stage!r} is not a declared stage")
            generic = value.get("generic", False)
            if type(generic) is not bool:
                self._error(f"{context}.generic must be a boolean")
            functions = tuple(
                node_id
                for text in self._list(context, value, "functions")
                if (node_id := self._resolve(f"{context}.functions", text, ("function",)))
            )
            maps = tuple(
                node_id
                for text in self._list(context, value, "maps")
                if (node_id := self._resolve(f"{context}.maps", text, ("map", "axis")))
            )
            signals = tuple(
                node_id
                for text in self._list(context, value, "signals")
                if (node_id := self._resolve(f"{context}.signals", text, ("signal", "register")))
            )
            for name, items in (("functions", functions), ("maps", maps), ("signals", signals)):
                repeated = sorted(item for item, count in Counter(items).items() if count > 1)
                if repeated:
                    self._error(f"{context}.{name} repeats {repeated}")
            blocks.append(Block(
                identifier,
                self._text(context, value, "name"),
                stage,
                self._text(context, value, "summary"),
                self._specs(context, value),
                functions,
                maps,
                signals,
                bool(generic),
            ))
        return blocks

    def _load_endpoints(self):
        endpoints = []
        seen = set()
        block_ids = {block.id for block in self.blocks}
        for index, value in enumerate(self.raw.get("endpoint", [])):
            context = f"endpoint[{index}]"
            value = self._table(
                context,
                value,
                ENDPOINT_KEYS,
                {"id", "name", "direction", "block", "peripheral", "summary"},
            )
            if value is None:
                continue
            identifier = self._identifier(context, value, seen)
            context = f"endpoint {identifier}"
            direction = value.get("direction")
            if direction not in DIRECTIONS:
                self._error(f"{context}.direction {direction!r} is not one of {list(DIRECTIONS)}")
            block = value.get("block")
            if block not in block_ids:
                self._error(f"{context}.block {block!r} is not a declared block")
            registers = tuple(
                node_id
                for text in self._list(context, value, "registers")
                if (node_id := self._resolve(f"{context}.registers", text, ("register", "signal")))
            )
            functions = tuple(
                node_id
                for text in self._list(context, value, "functions")
                if (node_id := self._resolve(f"{context}.functions", text, ("function",)))
            )
            if not registers and not functions:
                self._error(f"{context} names neither registers nor functions")
            endpoints.append(Endpoint(
                identifier,
                self._text(context, value, "name"),
                direction,
                block,
                self._text(context, value, "peripheral"),
                self._text(context, value, "summary"),
                registers,
                functions,
                self._specs(context, value),
            ))
        return endpoints

    def _spec_index(self, spec):
        if spec not in self._spec_cache:
            self._spec_cache[spec] = spec_addresses(
                _repo_path(spec).read_text(encoding="utf-8")
            )
        return self._spec_cache[spec]

    def _connected(self, nodes):
        """Return true when ledger relations join the step inside its node set."""
        allowed = set(nodes)
        start, goal = nodes[0], nodes[1]
        seen = {start}
        queue = deque([start])
        while queue:
            current = queue.popleft()
            if current == goal:
                return True
            for neighbor in self.adjacent.get(current, ()):
                if neighbor in allowed and neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
        return False

    def _load_chains(self):
        chains = []
        seen = set()
        for index, value in enumerate(self.raw.get("chain", [])):
            context = f"chain[{index}]"
            value = self._table(
                context,
                value,
                CHAIN_KEYS,
                {"id", "name", "summary", "quantity", "output", "step"},
            )
            if value is None:
                continue
            identifier = self._identifier(context, value, seen)
            context = f"chain {identifier}"
            specs = self._specs(context, value)
            output = self._resolve(f"{context}.output", value.get("output"), allow_unreviewed=True)
            steps = []
            raw_steps = value.get("step", [])
            if not isinstance(raw_steps, list) or not raw_steps:
                self._error(f"{context} declares no steps")
                raw_steps = []
            pairs = set()
            for number, raw in enumerate(raw_steps, 1):
                step_context = f"{context} step {number}"
                raw = self._table(
                    step_context, raw, STEP_KEYS, {"from", "to", "effect", "sign"}
                )
                if raw is None:
                    continue
                source = self._resolve(f"{step_context}.from", raw.get("from"), allow_unreviewed=True)
                target = self._resolve(f"{step_context}.to", raw.get("to"), allow_unreviewed=True)
                via = tuple(
                    node_id
                    for text in self._list(step_context, raw, "via")
                    if (node_id := self._resolve(f"{step_context}.via", text, allow_unreviewed=True))
                )
                effect = raw.get("effect")
                sign = raw.get("sign")
                if effect not in EFFECTS:
                    self._error(f"{step_context}.effect {effect!r} is not one of {list(EFFECTS)}")
                if sign not in SIGNS:
                    self._error(f"{step_context}.sign {sign!r} is not one of {list(SIGNS)}")
                note = raw.get("note", "")
                if not isinstance(note, str):
                    self._error(f"{step_context}.note must be a string")
                    note = ""
                step_specs = self._specs(step_context, raw)
                if not source or not target:
                    continue
                if source == target:
                    self._error(f"{step_context} joins {raw.get('from')} to itself")
                    continue
                if (source, target) in pairs:
                    self._error(f"{step_context} repeats {raw.get('from')} -> {raw.get('to')}")
                pairs.add((source, target))
                step = Step(source, target, effect, sign, via, " ".join(note.split()), step_specs)
                if 'research' in raw:
                    from kb import research
                    record = raw['research']
                    if not isinstance(record, dict) or set(record) != research.KEYS or record.get('state') != 'unresolved':
                        self._error(f'{step_context}.research needs one unresolved source-bound record')
                    else:
                        step.research = record
                members = (source, target, *via)
                if self._connected(members):
                    step.support = "ledger"
                else:
                    named = step_specs + specs
                    addresses = {self.nodes[node].addr for node in members}
                    backing = [
                        spec for spec in named if addresses <= self._spec_index(spec)
                    ]
                    if backing:
                        step.support = "specification"
                    else:
                        self._error(
                            f"{step_context} ({raw.get('from')} -> {raw.get('to')}) has no "
                            "ledger relation inside its from/to/via nodes, and no named "
                            "specification states all of them"
                        )
                steps.append(step)
            chain = Chain(
                identifier,
                self._text(context, value, "name"),
                self._text(context, value, "summary"),
                self._text(context, value, "quantity"),
                output,
                specs,
                steps,
            )
            if output and steps and output not in {
                node for step in steps for node in (step.source, step.target)
            }:
                self._error(f"{context}.output is not a node of its steps")
            if self._cyclic(steps):
                self._error(f"{context} steps form a cycle")
            chains.append(chain)
        return chains

    @staticmethod
    def _cyclic(steps):
        following = defaultdict(list)
        for step in steps:
            following[step.source].append(step.target)
        state = {}

        def visit(node):
            state[node] = 1
            for target in following[node]:
                if state.get(target) == 1:
                    return True
                if target not in state and visit(target):
                    return True
            state[node] = 2
            return False

        return any(node not in state and visit(node) for node in list(following))

    def _check_coverage(self):
        placed = Counter(
            function for block in self.blocks for function in block.functions
        )
        repeated = sorted(node for node, count in placed.items() if count > 1)
        for node in repeated:
            owners = [block.id for block in self.blocks if node in block.functions]
            self._error(f"{self.nodes[node].addr} is placed in several blocks: {owners}")
        unplaced = sorted(
            node_id
            for node_id, node in self.nodes.items()
            if node.kind == "function" and node_id not in placed
        )
        for node_id in unplaced:
            node = self.nodes[node_id]
            self._error(
                f"reviewed function {node.addr} has no block: {first_sentence(node.text, limit=72)}"
            )
        if unplaced:
            self._error(
                "place each reviewed function in one block; "
                "`uv run python tools/romviz/architecture.py suggest` ranks candidate blocks"
            )
        for block in self.blocks:
            if not block.functions and not any(
                endpoint.block == block.id for endpoint in self.endpoints
            ):
                self._error(f"block {block.id} has neither functions nor endpoints")

    # Derived ownership, flows, and impact.

    @staticmethod
    def _vote(owners, order, generic):
        """Return the block with most owners; shared kernels own no derived node."""
        votes = Counter(owner for owner in owners if owner and owner not in generic)
        if not votes:
            return None
        return min(votes, key=lambda owner: (-votes[owner], order[owner]))

    def _derive_blocks(self):
        order = {block.id: index for index, block in enumerate(self.blocks)}
        generic = {block.id for block in self.blocks if block.generic}
        for block in self.blocks:
            for node_id in (*block.functions, *block.maps, *block.signals):
                node = self.nodes[node_id]
                node.block = block.id
                node.pinned = True
        for endpoint in self.endpoints:
            for node_id in endpoint.registers:
                node = self.nodes[node_id]
                if not node.pinned:
                    node.block = endpoint.block
                    node.pinned = True

        def function_owner(node_id):
            node = self.nodes[node_id]
            return node.block if node.kind == "function" else None

        for node in self.nodes.values():
            if node.pinned or node.kind != "map":
                continue
            readers = [
                function_owner(edge.target)
                for edge in self.outgoing.get(node.id, ())
                if edge.kind in FLOW_KINDS
            ]
            node.block = self._vote(readers, order, generic) or self._vote(
                [function_owner(other) for other in self.adjacent.get(node.id, ())],
                order,
                generic,
            )
        for node in self.nodes.values():
            if node.pinned or node.kind != "axis":
                continue
            owners = [
                self.nodes[edge.target].block
                for edge in self.outgoing.get(node.id, ())
                if self.nodes[edge.target].kind == "map"
            ]
            node.block = self._vote(owners, order, generic) or self._vote(
                [function_owner(other) for other in self.adjacent.get(node.id, ())],
                order,
                generic,
            )
        data_kinds = {"signal", "register", "ram", "io"}
        pending = []
        for node in self.nodes.values():
            if node.pinned or node.kind not in data_kinds:
                continue
            writers = [
                function_owner(edge.source)
                for edge in self.incoming.get(node.id, ())
                if edge.kind == "data"
            ]
            node.block = self._vote(writers, order, generic)
            if node.block is None:
                pending.append(node)
        # A copy written only by a generic block, such as a scheduler snapshot,
        # belongs to the block that owns the value it copies.
        changed = True
        while changed:
            changed = False
            for node in pending:
                if node.block:
                    continue
                sources = [
                    self.nodes[edge.source].block
                    for edge in self.incoming.get(node.id, ())
                    if edge.kind == "data" and self.nodes[edge.source].kind in data_kinds
                ]
                owner = self._vote(sources, order, generic)
                if owner:
                    node.block = owner
                    changed = True
        for node in pending:
            if node.block is None and node.kind in {"register", "io"}:
                node.block = self._vote(
                    [
                        function_owner(edge.target)
                        for edge in self.outgoing.get(node.id, ())
                        if edge.kind in FLOW_KINDS
                    ],
                    order,
                    generic,
                )

    def _check_map_attribution(self):
        """Every code-confidence map outside the dead role reaches a block."""
        orphans = sorted(
            (
                node
                for node in self.nodes.values()
                if node.kind == "map"
                and node.block is None
                and node.confidence == "code"
                and node.role != "dead"
            ),
            key=lambda node: node.addr,
        )
        for node in orphans:
            self._error(f"code-confidence map {node.addr} has no block: {node.label}")
        if orphans:
            self._error(
                "place a function that reads each such map in a block, "
                "or pin the map in the maps array of a block"
            )

    def _derive_flows(self):
        generic = {block.id for block in self.blocks if block.generic}
        flows = {}
        for edge in self.edges.values():
            if edge.kind not in FLOW_KINDS:
                continue
            source = self.nodes[edge.source]
            target = self.nodes[edge.target]
            if not source.block or not target.block or source.block == target.block:
                continue
            if source.block in generic or target.block in generic:
                continue
            carrier = edge.source if source.kind != "function" else edge.target
            key = (source.block, target.block)
            flow = flows.setdefault(key, {"weight": 0, "carriers": Counter()})
            flow["weight"] += 1
            flow["carriers"][carrier] += 1
        return flows

    def _chain_impact(self, chain):
        following = defaultdict(list)
        for index, step in enumerate(chain.steps):
            following[step.source].append((index, step))
        memo = {}

        def signs(node, stack=()):
            if node == chain.output:
                return {"positive": set()}
            if node in memo:
                return memo[node]
            if node in stack:
                return {}
            result = defaultdict(set)
            for index, step in following[node]:
                for sign, used in signs(step.target, stack + (node,)).items():
                    composed = combine_sign(step.sign, sign)
                    result[composed] |= used | {index}
            memo[node] = dict(result)
            return memo[node]

        collected = defaultdict(lambda: defaultdict(set))
        for step in chain.steps:
            for node in (step.source, step.target):
                if node != chain.output:
                    for sign, used in signs(node).items():
                        collected[node][sign] |= used
        # A function named in `via` performs its step: its calibration acts
        # with the step sign composed with the downstream sign of the target.
        for index, step in enumerate(chain.steps):
            for sign, used in signs(step.target).items():
                composed = combine_sign(step.sign, sign)
                for node in step.via:
                    if node != chain.output:
                        collected[node][composed] |= used | {index}
        return {
            node: {
                "sign": merge_signs(paths),
                "steps": sorted(set().union(*paths.values())),
            }
            for node, paths in sorted(collected.items())
            if paths
        }

    # Queries.

    def block(self, identifier):
        for block in self.blocks:
            if block.id == identifier:
                return block
        raise KeyError(identifier)

    def members(self, block_id):
        return sorted(
            (node for node in self.nodes.values() if node.block == block_id),
            key=lambda node: (KIND_ORDER[node.kind], node.addr),
        )

    def lookup(self, text):
        """Resolve a query token to node ids, accepting 0x and FUN_ forms."""
        text = text.strip()
        match = re.fullmatch(r"(?:(function|map|axis|signal|register|ram|io|rom|other):)?(?:0x|FUN_|DAT_)?([0-9A-Fa-f]{1,8})", text)
        if not match:
            return []
        prefix, value = match.groups()
        addr = _normalize(value)
        if prefix:
            node_id = f"{prefix}:{addr}"
            return [node_id] if node_id in self.nodes else []
        return sorted(
            (node_id for node_id, node in self.nodes.items() if node.addr == addr),
            key=lambda node_id: KIND_ORDER[self.nodes[node_id].kind],
        )

    def _relay(self, node_id):
        """Shared kernels and the scheduler serve every block, so a derived
        path through them does not describe a data flow of the callers."""
        node = self.nodes[node_id]
        if node.kind != "function" or not node.block:
            return True
        return not any(block.generic for block in self.blocks if block.id == node.block)

    def downstream(self, node_id, limit=40):
        """Breadth-first data and control reach toward the actuator endpoints."""
        endpoints = defaultdict(set)
        for endpoint in self.endpoints:
            if endpoint.direction in {"output", "bidirectional"}:
                for register in endpoint.registers:
                    endpoints[register].add(endpoint.id)
        distance = {node_id: 0}
        queue = deque([node_id])
        reached = []
        while queue:
            current = queue.popleft()
            if distance[current] >= limit or (current != node_id and not self._relay(current)):
                continue
            for edge in self.outgoing.get(current, ()):
                if edge.kind not in FLOW_KINDS or edge.target in distance:
                    continue
                distance[edge.target] = distance[current] + 1
                queue.append(edge.target)
                reached.append(edge.target)
        blocks = Counter(self.nodes[node].block for node in reached if self.nodes[node].block)
        hits = {}
        for node in reached:
            for endpoint in endpoints.get(node, ()):
                hits.setdefault(endpoint, distance[node])
        ordered = sorted(hits, key=lambda endpoint: (hits[endpoint], endpoint))
        return {
            "distance": distance,
            "blocks": blocks,
            "endpoints": ordered,
            "endpointDistance": hits,
        }

    def path(self, source, target):
        previous = {source: None}
        queue = deque([source])
        while queue:
            current = queue.popleft()
            if current == target:
                break
            if current != source and not self._relay(current):
                continue
            for edge in self.outgoing.get(current, ()):
                if edge.kind in FLOW_KINDS and edge.target not in previous:
                    previous[edge.target] = (current, edge)
                    queue.append(edge.target)
        if target not in previous:
            return None
        steps = []
        current = target
        while previous[current] is not None:
            parent, edge = previous[current]
            steps.append(edge)
            current = parent
        return list(reversed(steps))

    def suggestions(self, node_ids=None):
        """Rank candidate blocks for functions by ledger coupling and spec mentions."""
        placed = {node for block in self.blocks for node in block.functions}
        if node_ids is None:
            node_ids = sorted(
                node_id
                for node_id, node in self.nodes.items()
                if node.kind == "function" and node_id not in placed
            )
        generic = {block.id for block in self.blocks if block.generic}
        result = {}
        for node_id in node_ids:
            votes = Counter()
            reasons = defaultdict(list)
            for neighbor in self.adjacent.get(node_id, ()):
                other = self.nodes[neighbor]
                if not other.block:
                    continue
                weight = 2 if other.kind == "function" else 1
                votes[other.block] += weight
                reasons[other.block].append(other.addr)
            addr = self.nodes[node_id].addr
            for block in self.blocks:
                if any(addr in self._spec_index(spec) for spec in block.specs):
                    votes[block.id] += 1
                    reasons[block.id].append("spec")
            ranked = sorted(
                votes.items(),
                key=lambda item: (item[0] in generic, -item[1], item[0]),
            )
            result[node_id] = [
                (block, score, sorted(set(reasons[block]))[:6])
                for block, score in ranked[:3]
            ]
        return result

    # Export.

    def export(self):
        """Return the JSON model that the atlas and agents consume."""
        ordered = sorted(
            self.nodes.values(), key=lambda node: (KIND_ORDER[node.kind], node.addr)
        )
        index = {node.id: position for position, node in enumerate(ordered)}
        edge_rows = sorted(
            (
                index[edge.source],
                index[edge.target],
                EDGE_KINDS.index(edge.kind),
                "+".join(sorted(edge.roles)),
            )
            for edge in self.edges.values()
        )
        roles = sorted({row[3] for row in edge_rows})
        role_index = {role: position for position, role in enumerate(roles)}
        stage_order = {stage.id: position for position, stage in enumerate(self.stages)}

        def node_row(node):
            row = {
                "id": node.id,
                "kind": node.kind,
                "addr": node.addr,
                "label": node.label,
            }
            for key, value in (
                ("text", node.text),
                ("note", node.note),
                ("confidence", node.confidence),
                ("role", node.role),
                ("units", node.units),
                ("source", node.source),
                ("block", node.block),
            ):
                if value:
                    row[key] = value
            meta = {key: value for key, value in node.meta.items() if value}
            if meta:
                row["meta"] = meta
            if node.pinned:
                row["pinned"] = True
            return row

        return {
            "id": self.rom,
            "source": _display_path(self.source),
            "summary": self.summary,
            "ledgers": {key: _display_path(path) for key, path in self.ledgers.paths.items()},
            "edgeKinds": list(EDGE_KINDS),
            "edgeRoles": roles,
            "stages": [
                {"id": stage.id, "name": stage.name, "lane": stage.lane, "summary": stage.summary}
                for stage in self.stages
            ],
            "blocks": [
                {
                    "id": block.id,
                    "name": block.name,
                    "stage": block.stage,
                    "summary": block.summary,
                    "specs": list(block.specs),
                    "generic": block.generic,
                    "members": [index[node.id] for node in self.members(block.id)],
                }
                for block in sorted(
                    self.blocks, key=lambda block: stage_order.get(block.stage, 0)
                )
            ],
            "nodes": [node_row(node) for node in ordered],
            "edges": [
                [source, target, kind, role_index[role]]
                for source, target, kind, role in edge_rows
            ],
            "flows": [
                {
                    "from": source,
                    "to": target,
                    "weight": flow["weight"],
                    "carriers": [
                        index[node]
                        for node, _count in sorted(
                            flow["carriers"].items(),
                            key=lambda item: (-item[1], item[0]),
                        )
                    ],
                }
                for (source, target), flow in sorted(self.flows.items())
            ],
            "endpoints": [
                {
                    "id": endpoint.id,
                    "name": endpoint.name,
                    "direction": endpoint.direction,
                    "block": endpoint.block,
                    "peripheral": endpoint.peripheral,
                    "summary": endpoint.summary,
                    "registers": [index[node] for node in endpoint.registers],
                    "functions": [index[node] for node in endpoint.functions],
                    "specs": list(endpoint.specs),
                }
                for endpoint in self.endpoints
            ],
            "chains": [
                {
                    "id": chain.id,
                    "name": chain.name,
                    "summary": chain.summary,
                    "quantity": chain.quantity,
                    "output": index[chain.output],
                    "specs": list(chain.specs),
                    "steps": [
                        {
                            "from": index[step.source],
                            "to": index[step.target],
                            "effect": step.effect,
                            "sign": step.sign,
                            "via": [index[node] for node in step.via],
                            "note": step.note,
                            "support": step.support,
                            "specs": list(step.specs),
                            **({'research': step.research} if step.research else {}),
                        }
                        for step in chain.steps
                    ],
                    "impact": {
                        str(index[node]): value for node, value in sorted(chain.impact.items())
                    },
                }
                for chain in self.chains
            ],
        }


def load(source=DEFAULT_SOURCE, strict=True):
    """Load an architecture source; strict mode raises on any gate error."""
    architecture = Architecture(source)
    if strict and architecture.errors:
        raise ArchitectureError(architecture.errors)
    return architecture


# Command line.


def _describe(architecture, node_id):
    node = architecture.nodes[node_id]
    block = f" [{node.block}]" if node.block else ""
    return f"{node.kind} {node.addr}{block}: {node.label}"


def _print_check(architecture):
    steps = [step for chain in architecture.chains for step in chain.steps]
    support = Counter(step.support for step in steps)
    kinds = Counter(node.kind for node in architecture.nodes.values())
    owned = Counter(node.kind for node in architecture.nodes.values() if node.block)
    print(
        f"architecture {architecture.rom}: {len(architecture.stages)} stages, "
        f"{len(architecture.blocks)} blocks, {len(architecture.endpoints)} endpoints, "
        f"{len(architecture.chains)} chains"
    )
    print(
        f"  functions placed: {owned['function']}/{kinds['function']}; "
        f"maps attributed: {owned['map']}/{kinds['map']}; "
        f"signals attributed: {owned['signal']}/{kinds['signal']}"
    )
    pending = {
        block.id for block in architecture.blocks if block.stage == UNATTRIBUTED_STAGE
    }
    maps = [node for node in architecture.nodes.values() if node.kind == "map"]
    open_maps = [node for node in maps if node.block in pending]
    unowned = [node for node in maps if node.block is None]
    print(
        f"  maps without a functional role: {len(open_maps)} in stage "
        f"{UNATTRIBUTED_STAGE} ({sum(node.confidence == 'code' for node in open_maps)} "
        f"at code confidence), {len(unowned)} without a block "
        f"({sum(node.role == 'dead' for node in unowned)} dead)"
    )
    print(
        f"  chain steps: {len(steps)} ({support['ledger']} ledger-bound, "
        f"{support['specification']} specification-bound); "
        f"relations: {len(architecture.edges)}; inter-block flows: {len(architecture.flows)}"
    )


def _command_check(architecture, _args):
    if architecture.errors:
        for error in architecture.errors:
            print(error, file=sys.stderr)
        print(f"architecture gate failed with {len(architecture.errors)} errors", file=sys.stderr)
        return 1
    _print_check(architecture)
    return 0


def _command_blocks(architecture, _args):
    for stage in architecture.stages:
        print(f"{stage.id} ({stage.lane}): {stage.name}")
        for block in architecture.blocks:
            if block.stage != stage.id:
                continue
            members = Counter(node.kind for node in architecture.members(block.id))
            print(
                f"  {block.id}: {block.name} - {members['function']} functions, "
                f"{members['map']} maps, {members['signal'] + members['register']} signals"
            )
    return 0


def _command_block(architecture, args):
    try:
        block = architecture.block(args.block)
    except KeyError:
        print(f"unknown block {args.block}", file=sys.stderr)
        return 1
    print(f"{block.id}: {block.name} (stage {block.stage})")
    print(f"  {block.summary}")
    if block.specs:
        print(f"  specs: {', '.join(block.specs)}")
    for kind in ("function", "map", "axis", "signal", "register", "ram", "io"):
        members = [node for node in architecture.members(block.id) if node.kind == kind]
        if members:
            print(f"  {kind}s:")
            for node in members:
                print(f"    {node.addr}  {node.label}")
    inbound = sorted(
        (flow["weight"], source)
        for (source, target), flow in architecture.flows.items()
        if target == block.id
    )
    outbound = sorted(
        (flow["weight"], target)
        for (source, target), flow in architecture.flows.items()
        if source == block.id
    )
    if inbound:
        print("  inputs from: " + ", ".join(f"{name} ({weight})" for weight, name in reversed(inbound)))
    if outbound:
        print("  outputs to: " + ", ".join(f"{name} ({weight})" for weight, name in reversed(outbound)))
    return 0


def _resolve_query(architecture, text):
    matches = architecture.lookup(text)
    if not matches:
        print(f"{text} names no node", file=sys.stderr)
        return None
    return matches[0]


def _command_node(architecture, args):
    node_id = _resolve_query(architecture, args.address)
    if node_id is None:
        return 1
    node = architecture.nodes[node_id]
    print(_describe(architecture, node_id))
    for label, value in (
        ("confidence", node.confidence),
        ("units", node.units),
        ("source", node.source),
    ):
        if value:
            print(f"  {label}: {value}")
    if node.text:
        print(f"  {node.text}")
    for title, edges, pick in (
        ("inputs", architecture.incoming.get(node_id, ()), lambda edge: edge.source),
        ("outputs", architecture.outgoing.get(node_id, ()), lambda edge: edge.target),
    ):
        if edges:
            print(f"  {title}:")
            for edge in sorted(edges, key=lambda edge: (edge.kind, pick(edge))):
                print(f"    {edge.kind:7} {'+'.join(sorted(edge.roles)):18} {_describe(architecture, pick(edge))}")
    return 0


def _command_impact(architecture, args):
    node_id = _resolve_query(architecture, args.address)
    if node_id is None:
        return 1
    print(_describe(architecture, node_id))
    found = False
    for chain in architecture.chains:
        members = {
            node for step in chain.steps for node in (step.source, step.target, *step.via)
        }
        if node_id not in members:
            continue
        found = True
        output = architecture.nodes[chain.output].addr
        if node_id == chain.output:
            print(f"  chain {chain.id}: this node is the output ({chain.quantity})")
            continue
        impact = chain.impact.get(node_id)
        if not impact:
            print(f"  chain {chain.id}: no step path from this node reaches output {output}")
            continue
        print(f"  chain {chain.id} ({chain.quantity}): {impact['sign']}")
        for index in impact["steps"]:
            step = chain.steps[index]
            via = f" via {', '.join(architecture.nodes[node].addr for node in step.via)}" if step.via else ""
            print(
                f"    {architecture.nodes[step.source].addr} -{step.effect}/{step.sign}-> "
                f"{architecture.nodes[step.target].addr}{via}"
                + (f"  ({step.note})" if step.note else "")
            )
    if not found:
        print("  no chain step names this node")
    reach = architecture.downstream(node_id)
    if reach["endpoints"]:
        print(
            "  derived reach, unsigned (relations to the nearest register): "
            + ", ".join(
                f"{endpoint} ({reach['endpointDistance'][endpoint]})"
                for endpoint in reach["endpoints"]
            )
        )
    if reach["blocks"]:
        print(
            "  downstream blocks: "
            + ", ".join(f"{block} ({count})" for block, count in reach["blocks"].most_common(12))
        )
    return 0


def _command_path(architecture, args):
    source = _resolve_query(architecture, args.start)
    target = _resolve_query(architecture, args.end)
    if source is None or target is None:
        return 1
    steps = architecture.path(source, target)
    if steps is None:
        print("no directed data or control path", file=sys.stderr)
        return 1
    print(_describe(architecture, source))
    for edge in steps:
        print(f"  -{edge.kind}/{'+'.join(sorted(edge.roles))}-> {_describe(architecture, edge.target)}")
    return 0


def _command_chains(architecture, args):
    for chain in architecture.chains:
        if args.chain and chain.id != args.chain:
            continue
        print(f"{chain.id}: {chain.name} -> {chain.quantity} at {architecture.nodes[chain.output].addr}")
        if args.chain:
            print(f"  {chain.summary}")
            for number, step in enumerate(chain.steps, 1):
                via = f" via {', '.join(architecture.nodes[node].addr for node in step.via)}" if step.via else ""
                print(
                    f"  {number:2}. {_describe(architecture, step.source)}\n"
                    f"      -{step.effect}/{step.sign} [{step.support}]{via}-> "
                    f"{_describe(architecture, step.target)}"
                )
                if step.note:
                    print(f"      {step.note}")
    return 0


def _command_suggest(architecture, args):
    node_ids = None
    if args.address:
        node_ids = []
        for text in args.address:
            node_id = _resolve_query(architecture, text)
            if node_id is None:
                return 1
            node_ids.append(node_id)
    suggestions = architecture.suggestions(node_ids)
    if not suggestions:
        print("every reviewed function is placed")
    for node_id, ranked in suggestions.items():
        print(_describe(architecture, node_id))
        for block, score, reasons in ranked:
            print(f"    {block:24} {score:3}  {', '.join(reasons)}")
        if not ranked:
            print("    no coupled block")
    return 0


def _command_json(architecture, args):
    text = json.dumps(architecture.export(), indent=1, ensure_ascii=False) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Validate and query the firmware architecture model."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help=f"architecture source (default: {_display_path(DEFAULT_SOURCE)})",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check", help="run the architecture gate")
    commands.add_parser("blocks", help="list stages and blocks")
    block = commands.add_parser("block", help="show one block")
    block.add_argument("block")
    node = commands.add_parser("node", help="show one node and its relations")
    node.add_argument("address")
    impact = commands.add_parser("impact", help="show the chain impact and downstream reach of a node")
    impact.add_argument("address")
    path = commands.add_parser("path", help="shortest data or control path between two nodes")
    path.add_argument("start", metavar="FROM")
    path.add_argument("end", metavar="TO")
    chains = commands.add_parser("chains", help="list chains or show one chain")
    chains.add_argument("chain", nargs="?")
    suggest = commands.add_parser("suggest", help="rank candidate blocks for unplaced functions")
    suggest.add_argument("address", nargs="*")
    export = commands.add_parser("json", help="write the exported model")
    export.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        architecture = Architecture(args.source)
    except ArchitectureError as error:
        for message in error.errors:
            print(message, file=sys.stderr)
        return 1
    handler = {
        "check": _command_check,
        "blocks": _command_blocks,
        "block": _command_block,
        "node": _command_node,
        "impact": _command_impact,
        "path": _command_path,
        "chains": _command_chains,
        "suggest": _command_suggest,
        "json": _command_json,
    }[args.command]
    if args.command not in {"check", "suggest"} and architecture.errors:
        print(
            f"warning: the architecture gate reports {len(architecture.errors)} errors; "
            "run the check command",
            file=sys.stderr,
        )
    return handler(architecture, args)


if __name__ == "__main__":
    raise SystemExit(main())
