"""The in-memory model that the compiler builds from its inputs.

Adapters state facts about symbols, groups, links, statuses, designed entities,
and feature targets through a `Builder`, in two passes: every adapter declares
its symbols first, and then relates them, so that the target of a link
resolves against the symbols of every registry. `Builder.finish` joins symbols
into meanings over their group keys, names the meanings, lifts links to
meanings, and returns the `Model`.

A group key is a tuple whose first element is the kind of its meaning. Every
symbol that an adapter places in a group joins the group's meaning: a meaning
file, a key of a symbol table, a native table id, a field source, or a hook
key. Joins apply in the order of their strength, and a join that would give
one meaning two symbols of one layout is refused and goes to the audit.

A file states references as text (tools/kb/SPEC.md, section 5.2). A `Ref`
holds one until `finish` has named the meanings: the `to` of a link resolves
to the meaning, and a value to the symbol of the meaning on the layout of its
context, or else to the home symbol, as the adapters state references.
"""

from collections import defaultdict
from dataclasses import dataclass, field
import re

from kb import vocab

# Name tiers in precedence order (tools/kb/SPEC.md, section 20.1): the name of
# a meaning file wins over every registry name, and a former name that a file
# records only reserves the name.
TIERS = ("file", "native", "hook", "symbol_key", "curated", "field", "former")
TIER_RANK = {tier: rank for rank, tier in enumerate(TIERS)}
# Join strengths, strongest first: meaning files, correspondence rows with
# homology evidence, native table ids, field sources, registry keys, and
# correspondence rows that bind a target-specific role.
STRENGTHS = ("file", "homology", "native", "field", "key", "role")
STRENGTH_RANK = {strength: rank for rank, strength in enumerate(STRENGTHS)}
# Prose keys accumulate across registries; every other key states one fact.
PROSE = ("title", "summary", "note")
# Keys of a feature target that name the symbols the feature needs on its
# layout: tables of symbols, and tables of entries with a symbol.
NEEDED_TABLES = ("families", "symbols")
NEEDED_ENTRIES = {"roles": "symbol", "hooks": "hook"}
# Reference forms of files: a symbol `<name>/<kind>/<layout>` and a meaning or
# designed entity `<name>/<kind>`.
SYMBOL_REF = re.compile(r"(?P<name>[a-z][a-z0-9_-]*)/(?P<kind>[a-z]+)/(?P<layout>[0-9a-z]+)")
MEANING_REF = re.compile(r"(?P<name>[a-z][a-z0-9_-]*)/(?P<kind>[a-z]+)")


@dataclass(frozen=True, order=True)
class SymbolKey:
    layout: str
    kind: str
    address: int

    @property
    def key(self):
        return f"{self.layout}-{self.address:08x}/{self.kind}"

    @property
    def location(self):
        return f"{self.layout}:{self.address:08x}"


@dataclass
class Symbol:
    key: SymbolKey
    props: dict = field(default_factory=dict)
    evidence: list = field(default_factory=list)
    sources: set = field(default_factory=set)
    implicit: bool = True
    name: str | None = None
    generated: str | None = None
    former: tuple = ()
    meaning: "Meaning | None" = None

    @property
    def layout(self):
        return self.key.layout

    @property
    def kind(self):
        return self.key.kind

    @property
    def address(self):
        return self.key.address

    def value(self, name):
        """A key on the symbol's layout: its override, or else the key of its
        meaning."""
        if name in self.props:
            return self.props[name]
        return self.meaning.props.get(name) if self.meaning is not None else None


@dataclass(frozen=True)
class Ref:
    """A reference that a file states, which `Builder.finish` resolves;
    `layout` is the layout of its context, whose symbol a meaning reference
    names there."""

    text: str
    src: str
    layout: str | None = None


@dataclass
class LinkFact:
    """A link that a registry states. `owner` is a symbol key or a group key,
    `to` a symbol key or a `Ref`, and `layouts` the layouts that state it when
    the owner is no symbol of one layout."""

    owner: "SymbolKey | tuple"
    type: str
    to: "SymbolKey | Ref"
    props: dict
    evidence: list
    src: str
    stated: str
    layouts: frozenset | None = None


@dataclass(eq=False)
class Link:
    owner: "Meaning"
    type: str
    to: "Meaning"
    slot: str | None
    offset: int | None
    props: dict = field(default_factory=dict)
    evidence: list = field(default_factory=list)
    stated: set = field(default_factory=set)
    sources: set = field(default_factory=set)
    roles: set = field(default_factory=set)


@dataclass
class Status:
    layout: str
    state: str
    props: dict = field(default_factory=dict)
    evidence: list = field(default_factory=list)
    sources: set = field(default_factory=set)


@dataclass(eq=False)
class Meaning:
    kind: str
    name: str | None = None
    semantic: bool = False
    tier: str | None = None
    props: dict = field(default_factory=dict)
    symbols: dict = field(default_factory=dict)
    statuses: dict = field(default_factory=dict)
    links: list = field(default_factory=list)
    groups: set = field(default_factory=set)
    sources: set = field(default_factory=set)
    other_names: list = field(default_factory=list)
    # The files and registries that state the semantic name.
    name_sources: tuple = ()
    tables: dict = field(default_factory=dict)

    @property
    def key(self):
        return f"{self.name}/{self.kind}"

    @property
    def home(self):
        if "home" in self.props:
            return self.props["home"]
        if "7mfk" in self.symbols:
            return "7mfk"
        return min(self.symbols) if self.symbols else None

    @property
    def home_symbol(self):
        home = self.home
        return self.symbols.get(home) if home else None


@dataclass
class Entity:
    kind: str
    slug: str
    props: dict = field(default_factory=dict)
    refs: dict = field(default_factory=dict)
    steps: list = field(default_factory=list)
    sources: set = field(default_factory=set)

    @property
    def key(self):
        return f"{self.slug}/{self.kind}"


@dataclass
class Target:
    feature: str
    layout: str
    status: str | None = None
    props: dict = field(default_factory=dict)
    sources: set = field(default_factory=set)

    def needs(self):
        """The symbols that the feature needs on the layout of the target, in
        order: its key tables, the symbols of its roles and hooks, and
        `requires` (section 7.9)."""
        found = []
        for key in NEEDED_TABLES:
            found += self.props.get(key, {}).values()
        for key, name in NEEDED_ENTRIES.items():
            found += [entry[name] for entry in self.props.get(key, {}).values()
                      if isinstance(entry, dict) and name in entry]
        return found + list(self.props.get("requires", ()))


@dataclass(frozen=True, order=True)
class Issue:
    """A check failure, or with check `audit` a disagreement between registries."""

    check: str
    path: str
    subject: str
    message: str


class Union:
    def __init__(self):
        self.parent = {}

    def add(self, item):
        self.parent.setdefault(item, item)

    def find(self, item):
        self.parent.setdefault(item, item)
        root = item
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[item] != root:
            self.parent[item], item = root, self.parent[item]
        return root

    def join(self, left, right):
        left, right = self.find(left), self.find(right)
        if left != right:
            if _order(right) < _order(left):
                left, right = right, left
            self.parent[right] = left


def _order(node):
    return (isinstance(node, SymbolKey), repr(node))


class Builder:
    def __init__(self, layouts, spaces, functions, calibration, config=None):
        self.layouts = layouts
        self.spaces = spaces
        self.functions = functions
        self.calibration = calibration
        self.config = config or {}
        self.stash = {}
        self.symbols = {}
        self.nodes = {}
        self.edges = []
        self.group_kind = {}
        self.names = []
        self.meaning_props = []
        self.symbol_keys = []
        self.meaning_tables = []
        self.link_facts = []
        self.status_facts = []
        self.entities = {}
        self.targets = {}
        self.issues = []
        self.row_tokens = defaultdict(set)
        self._at = defaultdict(set)
        # Generated names by symbol key, of `kb/names.csv` and of the files,
        # which references resolve through.
        self.generated = {}
        # The names that files give symbols: {symbol key: (generated name or
        # None, former names, file)}, and the meaning files by kind and name.
        self.file_names = {}
        self.files = {}
        # The symbols whose file entries state evidence.
        self.file_evidence = set()
        # {repository path: text, or None} of the entity files that a change
        # replaces or removes before it writes them (`kb.write`).
        self.overlay = {}

    # Addresses -------------------------------------------------------------

    def issue(self, check, path, subject, message):
        self.issues.append(Issue(check, str(path), str(subject), message))

    def space(self, layout, address):
        """The address space of a location on the MCU of its layout: rom, ram,
        io, or None."""
        mcu = self.spaces[self.layouts[layout].mcu]
        for name in ("rom", "ram", "io"):
            start, end = mcu[name]
            if start <= address < end:
                return name
        return None

    def data_kind(self, layout, address):
        """ram or reg for a RAM or peripheral address, None elsewhere."""
        return {"ram": "ram", "io": "reg"}.get(self.space(layout, address))

    def is_function(self, layout, address):
        return address in self.functions.get(layout, ())

    def rom_data_kind(self, layout, address):
        """tbl for an unregistered ROM datum inside the calibration region of the
        layout's family, const outside it."""
        start, end = self.calibration.get(layout, (0, 0))
        return "tbl" if start <= address < end else "const"

    # Facts -----------------------------------------------------------------

    def symbol(self, layout, kind, address, src, group=None, props=None, evidence=None,
               implicit=False, strength="key"):
        key = SymbolKey(layout, kind, address)
        symbol = self.symbols.get(key)
        if symbol is None:
            symbol = self.symbols[key] = Symbol(key)
            self.nodes.setdefault(key)
            self._at[(layout, address)].add(key)
        if not implicit:
            symbol.implicit = False
        symbol.sources.add(str(src))
        for name, value in (props or {}).items():
            self._merge(symbol.props, name, value, src, key.key)
        for item in evidence or ():
            if item not in symbol.evidence:
                symbol.evidence.append(item)
            self._untyped(key, item, src)
        if group is not None:
            self.group(group, key, src, strength)
        return key

    def _untyped(self, key, item, src):
        """An evidence item mapped from a legacy token without the keys of its
        kind goes to the `untyped` section of the audit under its registry."""
        if "legacy" not in item:
            return
        required, _ = vocab.EVIDENCE_KINDS.get(item.get("kind"), ((), None))
        absent = [name for name in required if name not in item]
        if absent:
            self.issue("untyped", src, key.key, f"token {item['legacy']} gives {item['kind']} "
                       f"evidence without {', '.join(absent)}")

    def at(self, layout, address):
        return self._at.get((layout, address), set())

    def index(self, keys):
        """Let `at` and `resolve` answer symbols that another model declares,
        as a conversion relates a registry to the model before it."""
        for key in keys:
            self._at[(key.layout, key.address)].add(key)

    def group(self, group, key, src=None, strength="key"):
        src = str(src) if src is not None else ";".join(sorted(self.symbols[key].sources))
        if group[0] != key.kind:
            self.issue("schema", src, key.key,
                       f"a {key.kind} symbol cannot join the {group[0]} group {group[1:]}")
            return
        self._anchor(group)
        self._edge(group, key, src, strength)

    def join(self, left, right, src, strength="homology"):
        """Join two symbols of one meaning, as a correspondence row does."""
        if left.kind != right.kind:
            self.issue("schema", src, right.key,
                       f"joins a {right.kind} symbol to the {left.kind} symbol {left.key}")
            return
        self._edge(left, right, str(src), strength)

    def _edge(self, left, right, src, strength):
        self.edges.append((STRENGTH_RANK[strength], len(self.edges), left, right, src))

    def name(self, anchor, name, tier, src, rank=0):
        """A semantic name of the meaning of an anchor. Names of a better tier
        win, within a tier a lower `rank`, and then the name that sorts first."""
        self._anchor(anchor)
        self.names.append((anchor, name, tier, str(src), rank))

    def props(self, anchor, props, src):
        """Keys of the meaning of an anchor, a symbol key or a group key."""
        self._anchor(anchor)
        self.meaning_props.append((anchor, dict(props), str(src)))

    def keys(self, key, props, src):
        """Keys that a registry states for one symbol. The meaning takes each
        key from its home symbol, or else from the first symbol that states it,
        and a symbol whose value differs keeps it as an override."""
        self.symbol_keys.append((key, dict(props), str(src)))

    def table(self, anchor, name, value, src):
        """A feature table of a meaning: editor, logparam, or diagnostic."""
        self._anchor(anchor)
        self.meaning_tables.append((anchor, name, value, str(src)))

    def link(self, owner, type_, to, src, props=None, evidence=None, stated="owner",
             layouts=None):
        """A link from the meaning of `owner`, a symbol key or a group key, to
        the meaning of `to`. `layouts` are the layouts that state it, by
        default the layout of an owning symbol or else the home layout."""
        if not isinstance(owner, SymbolKey):
            self._anchor(owner)
        self.link_facts.append(LinkFact(owner, type_, to, dict(props or {}),
                                        list(evidence or ()), str(src), stated,
                                        None if layouts is None else frozenset(layouts)))

    def status(self, anchor, layout, state, src, props=None, evidence=None, yields=False):
        """A status of the meaning of an anchor on a layout. A status that
        `yields` gives way to a symbol of the meaning on that layout."""
        self._anchor(anchor)
        self.status_facts.append((anchor, layout, state, dict(props or {}),
                                  list(evidence or ()), str(src), yields))

    def entity(self, kind, slug, src, props=None, refs=None):
        key = (kind, slug)
        entity = self.entities.get(key)
        if entity is None:
            entity = self.entities[key] = Entity(kind, slug)
        entity.sources.add(str(src))
        for name, value in (props or {}).items():
            self._merge(entity.props, name, value, src, f"{slug}/{kind}")
        entity.refs.update(refs or {})
        return entity

    def target(self, feature, layout, src, status=None, props=None):
        key = (feature, layout)
        target = self.targets.get(key)
        if target is None:
            target = self.targets[key] = Target(feature, layout)
        target.sources.add(str(src))
        if status is not None:
            if target.status not in (None, status):
                self.issue("audit", src, f"{feature}@{layout}",
                           f"status {status} disagrees with {target.status}")
            target.status = target.status or status
        for name, value in (props or {}).items():
            current = target.props.get(name)
            if isinstance(value, dict) and (current is None or isinstance(current, dict)):
                # A table of named entries, as `allocations`, takes the entries
                # of every source; an entry that two sources state must agree.
                held = target.props.setdefault(name, {})
                for key, item in value.items():
                    self._merge(held, key, item, src, f"{feature}@{layout} {name}")
                continue
            self._merge(target.props, name, value, src, f"{feature}@{layout}")
        return target

    def _anchor(self, anchor):
        self.nodes.setdefault(anchor)
        if not isinstance(anchor, SymbolKey):
            self.group_kind.setdefault(anchor, anchor[0])

    def _merge(self, props, name, value, src, subject, same=None):
        """Merge one key; `same` compares a value that differs from the
        current one, as references to the symbols of one meaning compare."""
        if value is None or value == "" or value == [] or value == ():
            return
        current = props.get(name)
        if name in PROSE:
            if name == "note":
                items = props.setdefault("note", [])
                for item in value if isinstance(value, list) else [value]:
                    if item not in items:
                        items.append(item)
            elif current is None:
                props[name] = value
            elif current != value:
                items = props.setdefault("note", [])
                if value not in items:
                    items.append(value)
            return
        if current is None:
            props[name] = value
        elif current != value and not (same and same(current, value)):
            self.issue("audit", src, subject, f"{name} = {value!r} disagrees with {current!r}")

    # Resolution ------------------------------------------------------------

    def resolve(self, layout, address, kinds, src):
        """The symbol that a dependency on a location names: the registered
        symbol of the first kind in `kinds`, or else an implicit symbol of the
        first kind that the address admits."""
        present = {key.kind for key in self.at(layout, address)}
        for kind in kinds:
            if kind in present:
                return SymbolKey(layout, kind, address)
        if self.is_function(layout, address):
            actual = "fn"
        elif self.space(layout, address) == "rom":
            actual = self.rom_data_kind(layout, address)
            if actual not in kinds:
                actual = next((kind for kind in kinds if kind in ("tbl", "axis", "const")),
                              actual)
        else:
            actual = self.data_kind(layout, address)
        if actual not in kinds:
            return None
        return self.symbol(layout, actual, address, src, implicit=True)

    # Meanings --------------------------------------------------------------

    def _components(self):
        """Apply the joins by strength; refuse a join that would give one
        meaning two symbols of one layout."""
        union = Union()
        held = {}
        for node in self.nodes:
            union.add(node)
            held[node] = {node.layout: node} if isinstance(node, SymbolKey) else {}
        seen = set()
        for _, _, left, right, src in sorted(self.edges, key=lambda edge: edge[:2]):
            if (left, right) in seen:
                continue
            seen.add((left, right))
            a, b = union.find(left), union.find(right)
            if a == b:
                continue
            clash = sorted(layout for layout in held[a].keys() & held[b].keys()
                           if held[a][layout] != held[b][layout])
            if clash:
                layout = clash[0]
                self.issue("audit", src, _node(right),
                           f"refused join with {_node(left)}: one meaning would hold "
                           f"{held[a][layout].key} and {held[b][layout].key}")
                continue
            merged = held.pop(a) | held.pop(b)
            union.join(a, b)
            held[union.find(a)] = merged
        components = defaultdict(set)
        for node in self.nodes:
            components[union.find(node)].add(node)
        return components

    def finish(self):
        components = self._components()
        meanings = {}
        for root, nodes in components.items():
            symbols = sorted(node for node in nodes if isinstance(node, SymbolKey))
            groups = sorted((node for node in nodes if not isinstance(node, SymbolKey)),
                            key=repr)
            kinds = {key.kind for key in symbols} | {self.group_kind[g] for g in groups}
            if len(kinds) != 1:
                self.issue("schema", "model", repr(root), f"one meaning joins kinds {sorted(kinds)}")
                continue
            meaning = Meaning(kinds.pop(), groups=set(groups))
            meanings[root] = meaning
            for key in symbols:
                symbol = self.symbols[key]
                if key.layout in meaning.symbols:
                    other = meaning.symbols[key.layout]
                    self.issue("symbols", ";".join(sorted(symbol.sources | other.sources)),
                               key.key, f"one meaning holds {other.key.key} and {key.key}")
                    continue
                symbol.meaning = meaning
                meaning.symbols[key.layout] = symbol
                meaning.sources |= symbol.sources
        by_node = {}
        for root, meaning in meanings.items():
            for node in components[root]:
                by_node[node] = meaning
        model = Model(self.layouts, self.symbols, self.entities, self.targets, self.issues)
        model.stash = self.stash
        model.meanings = list(meanings.values())
        model.files = {name: (by_node.get(group), src) for name, (group, src) in self.files.items()}
        model.file_names = self.file_names
        model.file_evidence = self.file_evidence
        self._semantic_names(by_node, model)
        resolver = Resolver(self, by_node, model)
        self._resolve(resolver)
        same = lambda left, right: _meant(left, by_node) == _meant(right, by_node)
        for anchor, props, src in self.meaning_props:
            meaning = by_node.get(anchor)
            if meaning is None:
                continue
            meaning.sources.add(src)
            for name, value in props.items():
                self._merge(meaning.props, name, value, src, _subject(meaning), same)
        self._lift(model, same)
        for anchor, name, value, src in self.meaning_tables:
            meaning = by_node.get(anchor)
            if meaning is not None:
                meaning.tables.setdefault(name, []).append(value)
                meaning.sources.add(src)
        for anchor, layout, state, props, evidence, src, yields in self.status_facts:
            meaning = by_node.get(anchor)
            if meaning is None:
                continue
            if layout in meaning.symbols:
                if yields:
                    continue
                self.issue("symbols", src, _subject(meaning),
                           f"status {state} on {layout}, where the meaning has "
                           f"{meaning.symbols[layout].key.key}")
                continue
            status = meaning.statuses.get(layout)
            if status is None:
                meaning.statuses[layout] = Status(layout, state, props, evidence, {src})
            elif status.state != state:
                self.issue("audit", src, _subject(meaning),
                           f"status {state} on {layout} disagrees with {status.state}")
            else:
                status.sources.add(src)
                status.evidence.extend(item for item in evidence if item not in status.evidence)
        self._links(by_node, model, resolver)
        model.by_node = by_node
        return model

    def _resolve(self, resolver):
        """Replace the references that files state in every fact by the symbol
        keys they name."""
        value = resolver.value
        self.meaning_props = [(anchor, value(props), src)
                              for anchor, props, src in self.meaning_props]
        self.symbol_keys = [(key, value(props), src) for key, props, src in self.symbol_keys]
        self.meaning_tables = [(anchor, name, value(item), src)
                               for anchor, name, item, src in self.meaning_tables]
        self.status_facts = [(anchor, layout, state, value(props), value(evidence), src, yields)
                             for anchor, layout, state, props, evidence, src, yields
                             in self.status_facts]
        for symbol in self.symbols.values():
            symbol.props = value(symbol.props)
            symbol.evidence = value(symbol.evidence)
        for fact in self.link_facts:
            fact.props = value(fact.props)
            fact.evidence = value(fact.evidence)
        for target in self.targets.values():
            target.props = value(target.props)
        for entity in self.entities.values():
            entity.props = value(entity.props)
            entity.refs = {name: [resolver.entity(item) if isinstance(item, Ref) else item
                                  for item in items]
                           for name, items in entity.refs.items()}

    def _lift(self, model, same):
        stated = defaultdict(dict)
        for key, props, src in self.symbol_keys:
            symbol = self.symbols[key]
            if symbol.meaning is None:
                continue
            symbol.meaning.sources.add(src)
            for name, value in props.items():
                self._merge(stated[key], name, value, src, key.key, same)
        for meaning in model.meanings:
            found = [(layout, stated[symbol.key]) for layout, symbol in
                     sorted(meaning.symbols.items(), key=lambda item: item[0] != meaning.home)
                     if symbol.key in stated]
            for name in sorted({name for _, keys in found for name in keys}):
                values = [(layout, keys[name]) for layout, keys in found if name in keys]
                current = meaning.props.setdefault(name, values[0][1])
                for layout, value in values:
                    if not same(current, value):
                        meaning.symbols[layout].props[name] = value

    def _semantic_names(self, by_node, model):
        candidates = defaultdict(set)
        for anchor, name, tier, src, rank in self.names:
            meaning = by_node.get(anchor)
            if meaning is not None:
                candidates[id(meaning)].add((TIER_RANK[tier], rank, name, tier, src))
        for meaning in model.meanings:
            found = sorted(candidates.get(id(meaning), ()))
            if not found:
                continue
            _, _, name, tier, _ = found[0]
            meaning.name = name
            meaning.semantic = True
            meaning.tier = tier
            meaning.name_sources = tuple(sorted({src for _, _, other, _, src in found
                                                 if other == name}))
            meaning.other_names = sorted({(other, other_tier, src)
                                          for _, _, other, other_tier, src in found
                                          if other != name})

    def _links(self, by_node, model, resolver):
        lifted = {}
        for fact in self.link_facts:
            owner = by_node.get(fact.owner)
            to = resolver.meaning(fact.to) if isinstance(fact.to, Ref) else by_node.get(fact.to)
            if owner is None or to is None:
                continue
            if owner is to:
                model.self_links.append(fact)
                # A base relation can use the owning word as the base of
                # another byte at a nonzero offset. It remains a real link.
                if fact.type != "base":
                    continue
            slot = fact.props.get("slot")
            offset = fact.props.get("offset")
            key = (id(owner), fact.type, id(to), slot, offset)
            link = lifted.get(key)
            if link is None:
                link = lifted[key] = Link(owner, fact.type, to, slot, offset)
                owner.links.append(link)
            link.sources.add(fact.src)
            link.evidence.extend(item for item in fact.evidence if item not in link.evidence)
            if fact.layouts is not None:
                link.stated |= fact.layouts
            elif isinstance(fact.owner, SymbolKey):
                link.stated.add(fact.owner.layout)
            elif owner.home:
                link.stated.add(owner.home)
            for name, value in fact.props.items():
                if name in ("slot", "offset"):
                    continue
                if name == "role":
                    link.roles.add(value)
                    continue
                if fact.stated == "to" and name in ("relies", "supports"):
                    name = "reverse_" + name
                if name == "via":
                    merged = link.props.setdefault("via", [])
                    merged.extend(item for item in value if item not in merged)
                    continue
                current = link.props.get(name)
                if current is None:
                    link.props[name] = value
                elif current == value:
                    continue
                elif name in ("relies", "reverse_relies"):
                    # A level dependency includes the structural one, and a
                    # contract or scale dependency names its own property.
                    link.props[name] = max(current, value, key=vocab.RELIES.index)
                elif name in ("supports", "reverse_supports"):
                    link.props[name] = sorted({*_listed(current), *_listed(value)})
        model.links = [link for meaning in model.meanings for link in meaning.links]


def _listed(value):
    return value if isinstance(value, list) else [value]


def _meant(item, by_node):
    """A value with each symbol key replaced by its meaning, so that references
    to the symbols of one meaning on different layouts compare equal."""
    if isinstance(item, SymbolKey):
        return by_node.get(item, item)
    if isinstance(item, dict):
        return {key: _meant(entry, by_node) for key, entry in item.items()}
    if isinstance(item, (list, tuple)):
        return [_meant(entry, by_node) for entry in item]
    return item


def _node(node):
    """A symbol key or a group key as the audit prints it."""
    if isinstance(node, SymbolKey):
        return node.key
    return f"{' '.join(str(part) for part in node[1:])}/{node[0]}"


def _subject(meaning):
    if meaning.name:
        return meaning.key
    first = min(meaning.symbols.values(), key=lambda symbol: symbol.key, default=None)
    return first.key.key if first else f"?/{meaning.kind}"


class Resolver:
    """Resolves the references of files against the named meanings: a semantic
    name, the generated name of a symbol, or a former name, which the
    `references` check refuses. A reference that names nothing stays text and
    fails the `references` check."""

    def __init__(self, builder, by_node, model):
        self.builder = builder
        self.by_node = by_node
        self.names, self.formers = {}, {}
        for meaning in model.meanings:
            if meaning.semantic:
                self.names.setdefault((meaning.kind, meaning.name), meaning)
            for name, _, _ in meaning.other_names:
                self.formers.setdefault((meaning.kind, name), meaning)
        self.generated = {(key.kind, name): key for key, name in builder.generated.items()}
        # `home` is a key of the meaning, which merges after the references
        # resolve.
        self.homes = {}
        for anchor, props, _ in builder.meaning_props:
            if "home" in props and anchor in by_node:
                self.homes.setdefault(id(by_node[anchor]), props["home"])

    def _meaning(self, ref, kind, name):
        found = self.names.get((kind, name))
        if found is None and (kind, name) in self.generated:
            found = self.by_node.get(self.generated[(kind, name)])
        if found is None and (kind, name) in self.formers:
            found = self.formers[(kind, name)]
            self.builder.issue("references", ref.src, ref.text,
                               f"{name} is a former name of {found.key}")
        return found

    def meaning(self, ref):
        """The meaning that a reference names, or None."""
        match = SYMBOL_REF.fullmatch(ref.text) or MEANING_REF.fullmatch(ref.text)
        found = None
        if match and match.group("kind") in vocab.MEANING_KINDS:
            found = self._meaning(ref, match.group("kind"), match.group("name"))
        if found is None:
            self.builder.issue("references", ref.src, ref.text, "names no meaning")
        return found

    def _symbol(self, ref):
        match = SYMBOL_REF.fullmatch(ref.text)
        if match:
            found = self._meaning(ref, match.group("kind"), match.group("name"))
            symbol = found.symbols.get(match.group("layout")) if found else None
            if symbol is None:
                self.builder.issue("references", ref.src, ref.text, "names no symbol")
                return ref.text
            return symbol.key
        match = MEANING_REF.fullmatch(ref.text)
        if match and match.group("kind") in vocab.DESIGNED_KINDS:
            if (match.group("kind"), match.group("name")) not in self.builder.entities:
                self.builder.issue("references", ref.src, ref.text, "names no designed entity")
            return ref.text
        found = None
        if match and match.group("kind") in vocab.MEANING_KINDS:
            found = self._meaning(ref, match.group("kind"), match.group("name"))
        symbol = None
        if found is not None:
            home = self.homes.get(id(found))
            symbol = (found.symbols.get(ref.layout) if ref.layout else None) \
                or (found.symbols.get(home) if home else found.home_symbol)
        if symbol is None:
            self.builder.issue("references", ref.src, ref.text, "names no meaning")
            return ref.text
        return symbol.key

    def entity(self, ref):
        """The key that a reference of an entity names: (kind, slug) of a
        designed entity, or else the symbol key of a meaning, on the layout
        of the reference where it has one; the text for none."""
        match = MEANING_REF.fullmatch(ref.text)
        if match and match.group("kind") in vocab.DESIGNED_KINDS:
            key = (match.group("kind"), match.group("name"))
            if key in self.builder.entities:
                return key
            self.builder.issue("references", ref.src, ref.text, "names no designed entity")
            return ref.text
        return self._symbol(ref)

    def value(self, item):
        """A value with each reference replaced by the symbol key it names."""
        if isinstance(item, Ref):
            return self._symbol(item)
        if isinstance(item, dict):
            found = {key: self.value(entry) for key, entry in item.items()}
            return item if all(found[key] is item[key] for key in item) else found
        if isinstance(item, list):
            found = [self.value(entry) for entry in item]
            return item if all(new is old for new, old in zip(found, item)) else found
        return item


class Model:
    def __init__(self, layouts, symbols, entities, targets, issues):
        self.layouts = layouts
        self.symbols = symbols
        self.entities = entities
        self.targets = targets
        self.issues = issues
        self.meanings = []
        self.links = []
        self.self_links = []
        self.by_node = {}
        # {(kind, name): (meaning, file)} of the meaning files, the names that
        # files give symbols (`Builder.file_names`), and the symbols whose file
        # entries state evidence.
        self.files = {}
        self.file_names = {}
        self.file_evidence = set()
        # The texts that replace files of the working tree (`compile.build`).
        self.overlay = {}
        # The facts that adapters pass to the checks (`Builder.stash`).
        self.stash = {}

    def meaning_of(self, key):
        symbol = self.symbols.get(key)
        return symbol.meaning if symbol else None

    def required(self):
        """{(meaning key, layout): requirements} of the named meanings that are
        required on a layout where they have no symbol (section 7.4). A
        requirement is `family` when the meaning has a symbol on another layout
        of the family, `<feature>` when a feature that targets the layout
        requires it or its target on the layout needs it (`Target.needs`), and
        `<feature> via <field>/field` when the feature requires a field whose
        `source` it is."""
        family = {layout.id: layout.family for layout in self.layouts.values()}
        found = defaultdict(set)
        for meaning in self.meanings:
            if not meaning.name:
                continue
            families = {family[layout] for layout in meaning.symbols}
            for layout in self.layouts:
                if layout not in meaning.symbols and family[layout] in families:
                    found[(meaning.key, layout)].add("family")
        targeted = defaultdict(list)
        for feature, layout in self.targets:
            targeted[feature].append(layout)
        for (kind, slug), entity in sorted(self.entities.items()):
            if kind != "feature":
                continue
            for ref in entity.refs.get("requires", ()):
                if isinstance(ref, tuple):
                    field = self.entities.get(ref)
                    sources = field.refs.get("source", ()) if field is not None else ()
                    requirement = f"{slug} via {ref[1]}/{ref[0]}"
                else:
                    sources, requirement = (ref,), slug
                for source in sources:
                    meaning = self.meaning_of(source)
                    if meaning is None or not meaning.name:
                        continue
                    for layout in targeted[slug]:
                        if layout not in meaning.symbols:
                            found[(meaning.key, layout)].add(requirement)
        for (feature, layout), target in sorted(self.targets.items()):
            for ref in target.needs():
                meaning = self.meaning_of(ref)
                if meaning is not None and meaning.name and layout not in meaning.symbols:
                    found[(meaning.key, layout)].add(feature)
        return dict(found)
