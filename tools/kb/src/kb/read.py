"""The read commands of `kb` (tools/kb/SPEC.md, section 12.2).

Each command resolves its references against the graph of the working tree and
returns an `Answer`. The command line prints the answer within its budget, and
`--json` prints `Answer.data`. Elements that are not claims carry their
producer: `[l0]`, `[derived]`, or `[candidate]`.
"""

from collections import Counter, defaultdict, deque
import csv
import math
import re
import tomllib

from kb import names, project, refs, repo, spec, store, targets
from kb.answer import DETAIL, EVIDENCE, FACTS, IDENTITY, LINKS, Answer
from kb.refs import location_ref, symbol_ref
from kb.repo import KbError

BENCH = "tools/kb/bench.toml"
LINK_TYPES = ("WRITER", "READER", "INPUT", "COPY", "INDEX", "AXIS", "LOOKUP", "SELECTOR",
              "THRESHOLD", "BASE", "TARGET", "SOURCE", "MONITOR", "DEPENDS")
# "<owner> FORWARD[type] <to>" and "<to> BACKWARD[type] <owner>" for a link
# stored at its owner.
FORWARD = {
    "WRITER": "written by", "READER": "read by", "INPUT": "computed from", "COPY": "copy of",
    "INDEX": "indexed by", "AXIS": "has axis", "LOOKUP": "lookup of", "SELECTOR": "selected by",
    "THRESHOLD": "compares with", "BASE": "based at", "TARGET": "points at", "SOURCE": "returns",
    "MONITOR": "set by", "DEPENDS": "depends on", "CITES": "cites", "OBSERVES": "observes",
    "CARRIES": "carries", "SERVES": "serves", "TARGETS": "targets", "BLOCK": "in block",
    "STAGE": "in stage", "REGISTER": "registers", "FUNCTION": "functions", "OUTPUT": "computes",
    "REQUIRES": "requires",
}
BACKWARD = {
    "WRITER": "writes", "READER": "reads", "INPUT": "input of", "COPY": "copied to",
    "INDEX": "indexes", "AXIS": "axis of", "LOOKUP": "looked up into", "SELECTOR": "selects",
    "THRESHOLD": "threshold of", "BASE": "base of", "TARGET": "target of", "SOURCE": "source of",
    "MONITOR": "sets", "DEPENDS": "needed by", "CITES": "cited by", "OBSERVES": "observed by",
    "CARRIES": "carried by", "SERVES": "served by", "TARGETS": "targeted by", "BLOCK": "holds",
    "STAGE": "holds", "REGISTER": "register of", "FUNCTION": "function of",
    "OUTPUT": "output of", "REQUIRES": "required by",
}
# The `to` end of a reader link depends on its owner; for every other type the
# owner depends on `to`. A `depends` link takes its direction from its legacy
# role, and a symmetric role states no dependency.
TO_DEPENDS = {"READER"}
TO_DEPENDS_ROLES = {"consumer", "writes"}
SYMMETRIC_ROLES = {"homolog", "match"}
# The derived names of the access modes of L0: a site that both producers
# attest shows one mode.
MODE_NAMES = {"read": "load", "write": "store", "read_write": "update"}
STORE_MODES = {"store", "update"}
LOAD_MODES = {"load", "update", "data", "param", "copy"}
SHAPE_KEYS = {
    "ram": ("width", "signed", "unit"), "reg": ("width", "signed", "unit"),
    "tbl": ("cols", "rows", "storage"), "axis": ("points", "storage", "quantity"),
    "fn": ("role",), "const": ("width", "count", "storage"), "hook": ("width",),
    "did": ("number", "width"), "dtc": ("code", "group"),
}
FACT_KEYS = ("unit", "scale", "to_raw", "scale_level", "access", "contract", "contract_level",
             "disabled", "index", "attribute")
# Keys that a symbol states for its own layout: the images it applies to and
# the overrides of the keys of its meaning.
SYMBOL_KEYS = ("images", "width", "signed", "storage", "cols", "rows", "points", "count",
               "quantity", "unit", "scale", "to_raw", "scale_level", "index", "attribute",
               "interp", "editor", "bit")
STORAGE_BYTES = {"uint8": 1, "int8": 1, "uint16": 2, "int16": 2, "uint32": 4, "int32": 4,
                 "float32": 4}
HUB_PERCENTILE = 99
# Shortest paths that `kb path` ranks before it prints the first `--limit`.
PATH_CANDIDATES = 64
SENTENCE = re.compile(r"(?<=[.;])\s")
WORD = re.compile(r"[a-z0-9]+")


# Text ------------------------------------------------------------------------------

def field(label, value):
    """One labelled line of an answer."""
    return f"  {label:<15} {value}"


def headline(node, limit=96):
    """The title of a node, or else the first sentence of its summary."""
    if not node:
        return ""
    text = node.get("title") or node.get("summary") or ""
    if not node.get("title"):
        text = SENTENCE.split(text, maxsplit=1)[0]
    return text if len(text) <= limit else text[:limit - 3].rstrip() + "..."


def merged(symbol, meaning):
    """The keys of a symbol: its meaning's keys with the symbol's overrides."""
    return {**(meaning or {}), **(symbol or {})}


def shape(node):
    parts = []
    kind = node.get("kind")
    if kind in ("ram", "reg") and node.get("width"):
        parts.append(f"{node['width']}-bit")
        if "signed" in node:
            parts.append("signed" if node["signed"] else "unsigned")
    elif kind == "tbl" and node.get("cols"):
        parts.append(f"{node['cols']}x{node.get('rows') or 1}")
    elif kind == "axis" and node.get("points"):
        parts.append(f"{node['points']} points")
    elif kind == "did" and node.get("number") is not None:
        parts.append(f"DID {node['number']:04x}")
        if node.get("width"):
            parts.append(f"{node['width']}-byte response")
    for key in SHAPE_KEYS.get(kind, ()):
        if key in ("width", "signed", "cols", "rows", "points", "number") or key not in node:
            continue
        if key == "unit" and kind in ("ram", "reg"):
            continue
        parts.append(str(node[key]))
    return " ".join(parts)


def bits_text(bits):
    return ", ".join(f"{item.get('bit')} {item.get('name')}" for item in bits)


def symbol_keys_text(symbol):
    """The keys that a symbol states for its layout; a table prints its name."""
    parts = []
    for key in SYMBOL_KEYS:
        value = symbol.get(key)
        if value in (None, "", [], {}):
            continue
        if key == "bit":
            parts.append(f"bits {bits_text(value)}")
        elif key == "images":
            parts.append(f"images {', '.join(value)}")
        elif isinstance(value, (dict, list)):
            parts.append(key)
        else:
            parts.append(f"{key} {value}")
    return ", ".join(parts)


def identity_line(symbol, meaning):
    keys = merged(symbol, meaning)
    parts = [symbol_ref(symbol), " ".join(filter(None, (symbol["kind"], shape(keys))))]
    if keys.get("level"):
        parts.append(keys["level"])
    if symbol.get("implicit"):
        parts.append("implicit")
    return "  ".join(parts)


def meaning_line(meaning):
    parts = [meaning["key"]]
    if meaning.get("level"):
        parts.append(meaning["level"])
    if meaning.get("home"):
        parts.append(f"home {meaning['home']}")
    parts.append("semantic " + meaning["tier"] if meaning.get("semantic") else "generated name")
    return "  ".join(parts)


def node_ref(node):
    """The full reference of a Symbol, Meaning, or Entity node, or the L0 key."""
    if node is None:
        return "?"
    if "layout" in node and "kind" in node and "name" in node and "address" in node:
        return symbol_ref(node)
    return node.get("key", "?")


EVIDENCE_KEYS = ("supports", "at", "to", "relies", "count", "value", "mode", "path", "key")


def evidence_line(item):
    parts = [item.get("kind", "?")]
    for key in EVIDENCE_KEYS:
        if item.get(key) not in (None, ""):
            parts.append(f"{key} {item[key]}")
    return "  ".join(parts)


def evidence_lines(items, names=None, limit=8):
    """Evidence items that differ only in `at`, one line per group with the
    addresses of `at`. `names` maps symbol keys of `to` to full references."""
    groups = {}
    for item in items:
        if names and item.get("to") in names:
            item = {**item, "to": names[item["to"]]}
        rest = tuple((key, str(item.get(key))) for key in ("kind",) + EVIDENCE_KEYS
                     if key != "at" and item.get(key) not in (None, ""))
        groups.setdefault(rest, []).append(item.get("at"))
    lines = []
    for rest, places in groups.items():
        item = dict(rest)
        text = evidence_line(item)
        places = [place for place in places if place]
        if places:
            layout = places[0].split(":")[0]
            addresses = [place.split(":")[-1] for place in places]
            shown = " ".join(addresses[:limit])
            extra = f" +{len(addresses) - limit}" if len(addresses) > limit else ""
            text += f"  at {layout}:{shown}{extra}"
        lines.append(text)
    return lines


def hexes(sites, limit=6):
    shown = " ".join(f"{site:08x}" for site in sites[:limit])
    return shown + (f" +{len(sites) - limit}" if len(sites) > limit else "")


# Graph reads -------------------------------------------------------------------------

def symbol_names(graph, keys):
    """{symbol key: full reference} of the keys that name symbols."""
    if not keys:
        return {}
    return {row["s"]["key"]: symbol_ref(row["s"]) for row in graph.run(
        "MATCH (s:Kb:Symbol) WHERE s.key IN $keys RETURN s", keys=sorted(keys))}


def symbols_at(graph, layout, address):
    return [(row["s"], row["m"]) for row in graph.run(
        "MATCH (s:Kb:Symbol {layout: $layout, address: $address}) "
        "OPTIONAL MATCH (m:Kb:Meaning)-[:HAS]->(s) RETURN s, m ORDER BY s.kind",
        layout=layout, address=address)]


def symbol_links(graph, key):
    """Links of a symbol in both directions: (direction, type, verified, other)."""
    rows = graph.run(
        "MATCH (s:Kb:Symbol {key: $key})-[r]->(o:Kb:Symbol) "
        "RETURN 'out' AS dir, type(r) AS type, r.verified AS verified, r.role AS role, o AS other "
        "UNION ALL MATCH (s:Kb:Symbol {key: $key})<-[r]-(o:Kb:Symbol) "
        "RETURN 'in' AS dir, type(r) AS type, r.verified AS verified, r.role AS role, o AS other "
        "UNION ALL MATCH (s:Kb:Symbol {key: $key})<-[:HAS]-(:Kb:Meaning)<-[r:CITES]-(o) "
        "RETURN 'in' AS dir, type(r) AS type, null AS verified, null AS role, o AS other "
        "UNION ALL MATCH (s:Kb:Symbol {key: $key})<-[:HAS]-(:Kb:Meaning)<-[r]-(o:Kb:Entity) "
        "RETURN 'in' AS dir, type(r) AS type, null AS verified, null AS role, o AS other",
        key=key)
    return rows


def meaning_links(graph, key):
    rows = graph.run(
        "MATCH (m:Kb:Meaning {key: $key})-[r]->(o:Kb:Meaning) "
        "RETURN 'out' AS dir, type(r) AS type, properties(r) AS props, o AS other "
        "UNION ALL MATCH (m:Kb:Meaning {key: $key})<-[r]-(o:Kb:Meaning) "
        "RETURN 'in' AS dir, type(r) AS type, properties(r) AS props, o AS other "
        "UNION ALL MATCH (m:Kb:Meaning {key: $key})<-[r]-(o:Kb:Entity) "
        "RETURN 'in' AS dir, type(r) AS type, properties(r) AS props, o AS other", key=key)
    return rows


def phrase(direction, kind, roles=()):
    """The phrase of a link seen from one end: `out` from its owner, `in`
    from its `to` end. A `depends` link reads by its legacy role."""
    if kind != "DEPENDS":
        return (FORWARD if direction == "out" else BACKWARD)[kind]
    roles = set(roles or ())
    if roles & SYMMETRIC_ROLES:
        return f"{', '.join(sorted(roles))} of"
    owner_depends = not roles & TO_DEPENDS_ROLES
    return depends_phrase(owner_depends == (direction == "out"), roles)


def depends_phrase(depends, roles):
    """`depends on (<roles>)` from the dependent end, else `needed by (<roles>)`."""
    role = ", ".join(sorted(roles)) or "unspecified"
    return f"depends on ({role})" if depends else f"needed by ({role})"


def link_lines(rows, other_ref, limit=None):
    """Lines of links grouped by type and direction: `  <phrase>  <refs>`."""
    groups = defaultdict(list)
    for row in rows:
        role = row.get("role") or (row.get("props") or {}).get("role")
        phrase_text = phrase(row["dir"], row["type"], role)
        text = other_ref(row)
        if row.get("verified") is False:
            text += " (unverified)"
        groups[phrase_text].append(text)
    lines = []
    for text in sorted(groups, key=lambda item: (-len(groups[item]), item)):
        items = sorted(set(groups[text]))
        shown = items if limit is None else items[:limit]
        extra = f" +{len(items) - len(shown)}" if len(items) > len(shown) else ""
        lines.append(field(text, ", ".join(shown) + extra))
    return lines


def accessors(graph, layout, address):
    """The functions that access a location, one entry per function with the
    union of its producers, modes, and sites."""
    rows = graph.run(
        "MATCH (:Kb:Location {key: $key})<-[a:ACCESS]-(f:Kb:Function) "
        "OPTIONAL MATCH (s:Kb:Symbol {kind: 'fn'})-[:AT]->(f) "
        "RETURN f.key AS function, f.address AS address, a.producer AS producer, "
        "a.modes AS modes, a.sites AS sites, s AS symbol",
        key=location_ref(layout, address))
    found = {}
    for row in rows:
        entry = found.setdefault(row["function"], {
            "function": row["function"], "address": row["address"], "symbol": row["symbol"],
            "producers": set(), "modes": set(), "sites": {}})
        entry["producers"].add(row["producer"])
        entry["modes"].update(MODE_NAMES.get(mode, mode) for mode in row["modes"] or ())
        for site in row["sites"] or ():
            entry["sites"].setdefault(site["site"], set()).add(
                MODE_NAMES.get(site["mode"], site["mode"]))
    return sorted(found.values(), key=lambda entry: (-len(entry["sites"]), entry["address"]))


def function_ref(entry):
    return symbol_ref(entry["symbol"]) if entry.get("symbol") else f"{entry['function']} [l0]"


def access_summary(entries):
    readers = [entry for entry in entries if entry["modes"] & LOAD_MODES]
    writers = [entry for entry in entries if entry["modes"] & STORE_MODES]
    taken = [entry for entry in entries if entry["modes"] == {"literal"}]

    def sites(group, modes):
        return sum(1 for entry in group for found in entry["sites"].values() if found & modes)

    parts = []
    if readers:
        parts.append(f"readers: {sites(readers, LOAD_MODES)} sites in {len(readers)} functions")
    if writers:
        parts.append(f"writers: {sites(writers, STORE_MODES)} sites in {len(writers)} functions")
    if taken:
        parts.append(f"address in the literal pool only: {len(taken)} functions")
    return "; ".join(parts) or "no accesses"


def access_line(entry):
    by_mode = defaultdict(list)
    for site, modes in sorted(entry["sites"].items()):
        for mode in modes:
            by_mode[mode].append(site)
    producers = "+".join(sorted(entry["producers"]))
    parts = [f"{mode} {hexes(sites, 4)}" for mode, sites in sorted(by_mode.items())]
    return f"  [{producers}] {function_ref(entry)}  {'; '.join(parts)}"


def function_facts(graph, layout, address):
    rows = graph.run(
        "MATCH (f:Kb:Function {key: $key}) "
        "OPTIONAL MATCH (f)<-[c:CALL]-(g:Kb:Function) WITH f, count(g) AS callers "
        "OPTIONAL MATCH (f)-[d:CALL]->(h:Kb:Function) WITH f, callers, count(h) AS callees "
        "OPTIONAL MATCH (f)-[a:ACCESS]->(l:Kb:Location) "
        "RETURN f, callers, callees, count(DISTINCT l) AS locations",
        key=location_ref(layout, address))
    return rows[0] if rows else None


def callers(graph, layout, address):
    return graph.run(
        "MATCH (:Kb:Function {key: $key})<-[c:CALL]-(g:Kb:Function) "
        "OPTIONAL MATCH (s:Kb:Symbol {kind: 'fn'})-[:AT]->(g) "
        "RETURN g.key AS function, g.address AS address, c.sites AS sites, s AS symbol "
        "ORDER BY g.address", key=location_ref(layout, address))


def location_node(graph, layout, address):
    rows = graph.run("MATCH (l:Kb:Location {key: $key}) RETURN l",
                     key=location_ref(layout, address))
    return rows[0]["l"] if rows else None


# L0 files ------------------------------------------------------------------------------

def instructions_at(layout, address, root=repo.ROOT):
    """(function entry, ordinal, instruction) of every L0 function whose body
    holds an instruction at the address."""
    data = (root / repo.L0 / layout / "function_tokens.csv").read_bytes()
    pattern = re.compile(rb"^([0-9a-f]{8}),%b,(\d+),[^,]*,(.*)$" % f"{address:08x}".encode(),
                         re.M)
    return [(int(found.group(1), 16), int(found.group(2)),
             found.group(3).decode().strip('"')) for found in pattern.finditer(data)]


def references_to(layout, address, root=repo.ROOT):
    """Instructions of L0 that reference an address: pool reads, data and
    parameter references, and calls."""
    data = (root / repo.L0 / layout / "function_references.csv").read_bytes()
    pattern = re.compile(rb"^([0-9a-f]{8}),([0-9a-f]{8}),\d+,([^,]*),%b,(\d*),([0-9a-f]*),"
                         rb"(\w+)$" % f"{address:08x}".encode(), re.M)
    return [{"function": int(found.group(1), 16), "site": int(found.group(2), 16),
             "mnemonic": found.group(3).decode(), "width": found.group(4).decode(),
             "value": found.group(5).decode(), "type": found.group(6).decode()}
            for found in pattern.finditer(data)]


def literal_references_to(layout, value, root=repo.ROOT):
    """Exact exported 32-bit ROM load values, without interpreting their use."""
    expected = f"{value:08x}"
    found = {}
    with (root / repo.L0 / layout / "function_references.csv").open(
            newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source):
            if (row["width"] != "4" or row["ref_type"] != "read"
                    or row["mnemonic"] != "mov.l" or row["value_hex"].lower() != expected):
                continue
            key = (int(row["func_addr"], 16), int(row["ins_addr"], 16),
                   int(row["ordinal"]), row["mnemonic"], int(row["ref_addr"], 16))
            found[key] = {"function": key[0], "site": key[1], "ordinal": key[2],
                          "mnemonic": key[3], "pool": key[4], "width": 4,
                          "value_hex": expected, "ref_type": row["ref_type"]}
    return [found[key] for key in sorted(found)]


def containing_datum(graph, layout, address):
    """A table, axis, or constant symbol whose extent covers the address."""
    rows = graph.run(
        "MATCH (s:Kb:Symbol {layout: $layout}) WHERE s.kind IN ['tbl', 'axis', 'const'] "
        "AND s.address < $address AND s.address >= $low "
        "OPTIONAL MATCH (m:Kb:Meaning)-[:HAS]->(s) RETURN s, m ORDER BY s.address DESC LIMIT 16",
        layout=layout, address=address, low=address - 0x1000)
    for row in rows:
        keys = merged(row["s"], row["m"])
        size = STORAGE_BYTES.get(keys.get("storage"), 1)
        count = (keys.get("cols") or 1) * (keys.get("rows") or 1)
        if keys.get("kind") == "axis":
            count = keys.get("points") or 1
        if keys.get("kind") == "const":
            count = keys.get("count") or 1
        if row["s"]["address"] <= address < row["s"]["address"] + size * count:
            return row["s"], row["m"], address - row["s"]["address"]
    return None


def allocations_at(graph, layout, address):
    """[(reference, start, width)] of the feature allocations on a layout that
    hold an address."""
    found = []
    for row in graph.run(
            "MATCH (f:Kb:Entity {kind: 'feature'})-[t:TARGETS]->(:Kb:Layout {key: $layout}) "
            "WHERE t.allocations IS NOT NULL RETURN f.slug AS feature, "
            "t.allocations AS allocations ORDER BY feature", layout=layout):
        for name, entry in sorted(row["allocations"].items()):
            start = int(entry["address"], 16)
            if start <= address < start + entry["width"]:
                found.append((f"{row['feature']}.{name}", start, entry["width"]))
    return found


def neighbours(graph, layout, address):
    rows = graph.run(
        "MATCH (s:Kb:Symbol {layout: $layout}) WHERE s.address < $address "
        "RETURN s ORDER BY s.address DESC LIMIT 1 "
        "UNION ALL MATCH (s:Kb:Symbol {layout: $layout}) WHERE s.address > $address "
        "RETURN s ORDER BY s.address LIMIT 1", layout=layout, address=address)
    return [row["s"] for row in rows]


# kb at -----------------------------------------------------------------------------------

def _location_of(graph, ref, root):
    if ref.kind == "meaning":
        home = ref.node.get("home")
        found = refs.resolve(graph, f"{ref.node['key']}/{home}", root=root) if home else None
        if found is None or found.kind != "symbol":
            raise KbError(f"{ref.text} has no symbol to locate", code=5)
        return found.layout, found.address
    if ref.kind == "entity":
        raise KbError(f"{ref.text} is a designed entity without an address", code=2)
    return ref.layout, ref.address


def at(graph, text, layout=None, root=repo.ROOT, *, literal=False):
    found = refs.resolve(graph, text, layout, root, many=True)
    first = found[0] if isinstance(found, list) else found
    layout, address = _location_of(graph, first, root)
    loc = location_ref(layout, address)
    answer = Answer(f"kb show {loc}")
    at_symbols = symbols_at(graph, layout, address)
    space = _space(layout, address, root)
    data = {"location": loc, "space": space, "symbols": [], "l0": {}}
    if first.note:
        answer.section(None, IDENTITY, [f"note: {first.note}"])
    for symbol, meaning in at_symbols:
        keys = merged(symbol, meaning)
        lines = [identity_line(symbol, meaning)]
        if headline(keys):
            lines.append(field("title" if keys.get("title") else "summary", headline(keys)))
        answer.section(None, IDENTITY, lines)
        facts = [field(key, keys[key]) for key in ("unit", "scale", "scale_level")
                 if keys.get(key) not in (None, "")]
        answer.section(None, FACTS, facts)
        rows = symbol_links(graph, symbol["key"])
        answer.section(None, LINKS, link_lines(rows, lambda row: node_ref(row["other"]), 3))
        data["symbols"].append({"ref": symbol_ref(symbol), "keys": keys,
                                "links": [{"dir": row["dir"], "type": row["type"].lower(),
                                           "verified": row["verified"],
                                           "other": node_ref(row["other"])} for row in rows]})
    if not at_symbols:
        answer.section(None, IDENTITY, [f"{loc}  {space or 'outside the MCU'}  no symbol"])
        allocated = allocations_at(graph, layout, address)
        data["allocations"] = [{"ref": ref, "address": f"{start:08x}", "width": width}
                               for ref, start, width in allocated]
        answer.section(None, FACTS, [
            f"  allocation {ref}  {width} byte{'s' * (width != 1)} at {start:08x}"
            + (f" (offset {address - start})" if address != start else "")
            for ref, start, width in allocated])
        answer.section(None, FACTS, _containing(graph, layout, address, space, root, data))
    l0 = []
    if space in ("ram", "io") or location_node(graph, layout, address):
        entries = accessors(graph, layout, address)
        data["l0"]["accessors"] = [_access_data(entry) for entry in entries]
        l0.append(f"  [l0] {access_summary(entries)}" +
                  (f" (kb show {loc} lists them)" if entries else ""))
        answer.section(None, LINKS, l0)
        answer.section(None, DETAIL, [access_line(entry) for entry in entries[:6]])
    facts = function_facts(graph, layout, address)
    if facts:
        node = facts["f"]
        data["l0"]["function"] = {**node, "callers": facts["callers"],
                                  "callees": facts["callees"], "locations": facts["locations"]}
        answer.section(None, LINKS, [
            f"  [l0] function entry: {node.get('size')} bytes, {node.get('instructions')} "
            f"instructions, {facts['callers']} callers, {facts['callees']} callees, "
            f"{facts['locations']} locations"])
    if literal:
        matches = literal_references_to(layout, address, root)
        data["l0"]["literal"] = {"value_hex": f"{address:08x}", "width": 4,
                                  "classification": "unclassified", "matches": matches}
        answer.section(None, FACTS, [
            f"  [l0] literal value {address:#010x}: {len(matches)} exported 32-bit read matches",
            "  value use is unclassified; zero matches do not establish absence of runtime access"])
        answer.section(None, DETAIL, [
            f"  function {location_ref(layout, item['function'])} "
            f"site {item['site']:08x} pool {item['pool']:08x} ordinal {item['ordinal']} "
            f"{item['mnemonic']} width {item['width']} raw {item['value_hex']} "
            f"ref_type {item['ref_type']}" for item in matches])
    answer.data = data
    return answer


def _space(layout, address, root):
    spaces = _spaces(root)[repo.layout(layout, root).mcu]
    for name in ("rom", "ram", "io"):
        start, end = spaces[name]
        if start <= address < end:
            return name
    return None


def _spaces(root):
    from kb import compile

    return compile.spaces(repo.config(root))


def _containing(graph, layout, address, space, root, data):
    lines = []
    if space == "rom":
        for entry, ordinal, instruction in instructions_at(layout, address, root):
            owner = symbols_at(graph, layout, entry)
            name = symbol_ref(owner[0][0]) if owner else f"{location_ref(layout, entry)} [l0]"
            lines.append(f"  in {name}  instruction {ordinal}: {instruction}")
            data.setdefault("in", []).append({"function": location_ref(layout, entry),
                                              "ordinal": ordinal, "instruction": instruction})
        datum = containing_datum(graph, layout, address)
        if datum:
            symbol, _, offset = datum
            lines.append(f"  inside {symbol_ref(symbol)} at offset {offset}")
            data["inside"] = {"ref": symbol_ref(symbol), "offset": offset}
        for item in references_to(layout, address, root):
            if item["type"] in ("unconditional_call", "computed_call"):
                continue
            owner = symbols_at(graph, layout, item["function"])
            name = (symbol_ref(owner[0][0]) if owner
                    else f"{location_ref(layout, item['function'])} [l0]")
            value = f" value {item['value']}" if item["value"] else ""
            lines.append(f"  [l0] {item['type']} by {name} at {item['site']:08x} "
                         f"({item['mnemonic']}{value})")
            data.setdefault("references", []).append(item)
    for symbol in neighbours(graph, layout, address):
        delta = symbol["address"] - address
        lines.append(f"  nearest {symbol_ref(symbol)} ({delta:+d})")
    return lines


def _access_data(entry):
    return {"function": entry["function"],
            "symbol": symbol_ref(entry["symbol"]) if entry.get("symbol") else None,
            "producers": sorted(entry["producers"]), "modes": sorted(entry["modes"]),
            "sites": {f"{site:08x}": sorted(modes) for site, modes in sorted(entry["sites"].items())}}


# kb show ----------------------------------------------------------------------------------

def analogs_of(graph, meaning):
    """Hints in either direction; they are not dataflow or homology edges."""
    rows = graph.run(
        'MATCH (:Kb:Meaning {key: $key})-[r:ANALOG]-(m:Kb:Meaning) '
        'RETURN m.key AS to, m.name AS name, r.note AS note ORDER BY to, note',
        key=meaning['key'])
    return [dict(item) for item in {tuple(sorted(row.items())): row for row in rows}.values()]


def show(graph, text, layout=None, root=repo.ROOT):
    ref = refs.resolve(graph, text, layout, root)
    if ref.kind == "location":
        return _show_location(graph, ref, root)
    if ref.kind == "entity":
        return _show_entity(graph, ref)
    meaning = ref.meaning if ref.kind == "symbol" else ref.node
    answer = Answer(f"kb show {ref.text} --layout <layout>" if ref.kind == "meaning"
                    else f"kb raw {ref.text}")
    data = {"ref": ref.text, "meaning": meaning, "symbols": [], "statuses": [], "links": []}
    head = []
    if ref.note:
        head.append(f"note: {ref.note}")
    if ref.kind == "symbol":
        head.append(identity_line(ref.node, meaning))
        head.append(field('meaning', meaning_line(meaning)))
    else:
        head.append(meaning_line(meaning))
        if shape(meaning):
            head.append(field('shape', shape(meaning)))
    keys = merged(ref.node if ref.kind == "symbol" else None, meaning)
    if keys.get("title"):
        head.append(field('title', keys['title']))
    answer.section(None, IDENTITY, head)
    facts = [field(key, keys[key]) for key in FACT_KEYS if keys.get(key) not in (None, "")]
    if keys.get("bit"):
        facts.append(field('bits', bits_text(keys['bit'])))
    if keys.get("former"):
        facts.append(field('former', ', '.join(keys['former'])))
    if keys.get("block"):
        stage = graph.run("MATCH (:Kb:Entity {key: $key})-[:STAGE]->(s:Kb:Entity) "
                          "RETURN s.key AS stage", key=keys["block"])
        data["block"] = {"block": keys["block"], "stage": stage[0]["stage"] if stage else None}
        facts.append(field("block", "  stage ".join(filter(None, data["block"].values()))))
    data["steps"] = steps_through(graph, meaning["key"])
    facts.extend(field("step", step_text(row, chain=True)) for row in data["steps"])
    data["roles"] = roles_of(graph, meaning)
    facts.extend(field("role", role_text(row)) for row in data["roles"])
    if keys.get("summary"):
        facts.append(field('summary', keys['summary']))
    answer.section(None, FACTS, facts)
    members = graph.run(
        "MATCH (m:Kb:Meaning {key: $key})-[:HAS]->(s:Kb:Symbol) RETURN s ORDER BY s.layout",
        key=meaning["key"])
    statuses = graph.run(
        "MATCH (m:Kb:Meaning {key: $key})-[r:STATUS]->(l:Kb:Layout) "
        "RETURN l.key AS layout, properties(r) AS props ORDER BY l.key", key=meaning["key"])
    layouts = []
    for row in members:
        symbol = row["s"]
        parts = [symbol_ref(symbol), symbol.get("level") or keys.get("level") or "",
                 symbol_keys_text(symbol)]
        layouts.append(f"  {symbol['layout']:<6} " + "  ".join(filter(None, parts)))
        own = symbol.get("note") or []
        layouts.extend(f"{'':9}note: {note}" for note in (own if isinstance(own, list) else [own]))
        data["symbols"].append(symbol)
    for row in statuses:
        layouts.append(f"  {row['layout']:<6} {_status_text(row['props'])}")
        data["statuses"].append({"layout": row["layout"], **row["props"]})
    answer.section("layouts", FACTS, layouts)
    rows = (symbol_links(graph, ref.node["key"]) if ref.kind == "symbol"
            else meaning_links(graph, meaning["key"]))
    answer.section("links", LINKS, link_lines(rows, lambda row: node_ref(row["other"])))
    data['analogs'] = analogs_of(graph, meaning)
    answer.section('analogs', DETAIL,
                   [f'  {item["to"]}: {item["note"]}' for item in data['analogs']])
    data["links"] = [{"dir": row["dir"], "type": row["type"].lower(),
                      "other": node_ref(row["other"]), "verified": row.get("verified")}
                     for row in rows]
    tables = [field(name, _table_text(name, keys[name]))
              for name in ("interp", "editor", "logparam", "diagnostic") if keys.get(name)]
    answer.section("tables", DETAIL, tables)
    if ref.kind == "symbol":
        _l0_sections(graph, answer, ref.layout, ref.address, data, root)
    notes = meaning.get("note") or []
    answer.section("notes", DETAIL, [f"  {note}" for note in notes])
    evidence = []
    shown = [row["s"] for row in members
             if ref.kind != "symbol" or row["s"]["key"] == ref.node["key"]]
    names = symbol_names(graph, {item.get("to") for symbol in shown
                                 for item in symbol.get("evidence") or () if item.get("to")})
    for symbol in shown:
        evidence.extend(f"  {symbol['layout']:<6} {line}"
                        for line in evidence_lines(symbol.get("evidence") or (), names))
    answer.section("evidence", EVIDENCE, evidence)
    answer.data = data
    return answer


ENTITY_OWN = ("key", "kind", "slug", "title", "summary", "note", "producer", "src")
STEP_ROWS = ("MATCH (s)-[:FROM]->(f:Kb:Meaning) MATCH (s)-[:TO]->(t:Kb:Meaning) "
             "OPTIONAL MATCH (s)-[call:THROUGH]->(v:Kb:Meaning) "
             "WITH c, st, s, f, t, v, call.order AS via_order ORDER BY via_order "
             "WITH c, st, s, f, t, collect(v.key) AS via "
             "RETURN c.key AS chain, st.order AS order, f.key AS from, t.key AS to, "
             "s.effect AS effect, s.sign AS sign, s.note AS note, s.research AS research, via "
             "ORDER BY chain, order")


def steps_through(graph, key):
    """The chain steps whose from, to, or via is a meaning, in chain order."""
    return graph.run(
        "MATCH (c:Kb:Entity)-[st:STEP]->(s:Kb:Step)-[:FROM|TO|THROUGH]->(:Kb:Meaning {key: $key}) "
        "WITH DISTINCT c, st, s " + STEP_ROWS, key=key)


def chain_steps(graph, key):
    return graph.run("MATCH (c:Kb:Entity {key: $key})-[st:STEP]->(s:Kb:Step) " + STEP_ROWS,
                     key=key)


def step_text(row, chain=False):
    """One step: its chain and order when read from a meaning, its ends, its
    effect and sign, the functions it runs through, and its note."""
    parts = [f"{row['chain']} #{row['order']}" if chain else f"#{row['order']}",
             f"{row['from']} -> {row['to']}", f"{row['effect']} {row['sign']}"]
    if row["via"] and not chain:
        parts.append(f"via {', '.join(row['via'])}")
    if row["note"]:
        parts.append(row["note"])
    if row.get('research'):
        parts.append('unresolved semantics; the complete original statement remains source-bound')
    return "  ".join(parts)


def roles_of(graph, meaning):
    """[{feature, key, symbol, layouts}] of the feature roles that a symbol of
    the meaning fills, and of the roles of its name that another meaning fills
    on a layout."""
    own = {meaning["key"], *(row["key"] for row in graph.run(
        "MATCH (:Kb:Meaning {key: $key})-[:HAS]->(s:Kb:Symbol) RETURN s.key AS key",
        key=meaning["key"]))}
    found = defaultdict(list)
    for row in graph.run(
            "MATCH (f:Kb:Entity {kind: 'feature'})-[t:TARGETS]->(l:Kb:Layout) "
            "WHERE t.roles IS NOT NULL RETURN f.slug AS feature, l.key AS layout, "
            "t.roles AS roles ORDER BY feature, layout"):
        for key, role in sorted(row["roles"].items()):
            fills = role["symbol"] in own
            if fills or key == meaning.get("name"):
                found[(row["feature"], key, None if fills else role["symbol"])].append(
                    row["layout"])
    return [{"feature": feature, "key": key, "symbol": symbol, "layouts": layouts}
            for (feature, key, symbol), layouts in sorted(
                found.items(), key=lambda item: (item[0][0], item[0][1], item[0][2] or ""))]


def role_text(row):
    """A role that the meaning fills, or that `symbol` fills for it."""
    where = f"{row['feature']}.{row['key']} on {', '.join(row['layouts'])}"
    return f"fills {where}" if row["symbol"] is None else f"{where} is {row['symbol']}"


def _show_entity(graph, ref):
    """A designed entity: its keys, its relationships, and for a signal the
    DIDs that return an observed meaning."""
    node = ref.node
    answer = Answer(f"kb raw {ref.text}")
    answer.section(None, IDENTITY, [f"{ref.text}  {node.get('title', '')}"])
    facts = [field(key, compact(node[key])) for key in sorted(node)
             if key not in ENTITY_OWN and node[key] not in (None, "", [])]
    data = {"entity": node, "links": []}
    if node.get("kind") == "signal":
        numbers = [row["number"] for row in graph.run(
            "MATCH (:Kb:Entity {key: $key})-[:OBSERVES]->(:Kb:Meaning)<-[:SOURCE]-"
            "(d:Kb:Meaning {kind: 'did'}) RETURN DISTINCT d.number AS number ORDER BY number",
            key=node["key"])]
        facts.append(field("dids", ", ".join(f"{number:04x}" for number in numbers) or "none"))
        data["dids"] = numbers
    if node.get("summary"):
        facts.append(field("summary", node["summary"]))
    answer.section(None, FACTS, facts)
    rows = graph.run(
        "MATCH (:Kb:Entity {key: $key})-[r]->(o) WHERE o:Meaning OR o:Entity OR o:Layout "
        "RETURN 'out' AS dir, type(r) AS type, properties(r) AS props, o AS other "
        "UNION ALL MATCH (:Kb:Entity {key: $key})<-[r]-(o) WHERE o:Meaning OR o:Entity "
        "RETURN 'in' AS dir, type(r) AS type, properties(r) AS props, o AS other",
        key=node["key"])
    answer.section("links", LINKS, link_lines(rows, lambda row: node_ref(row["other"])))
    data["links"] = [{"dir": row["dir"], "type": row["type"].lower(),
                      "other": node_ref(row["other"])} for row in rows]
    if node.get("kind") == "chain":
        data["steps"] = chain_steps(graph, node["key"])
        answer.section("steps", FACTS, [f"  {step_text(row)}" for row in data["steps"]])
    answer.section("notes", DETAIL, [f"  {note}" for note in node.get("note") or ()])
    answer.data = data
    return answer


def _status_text(props):
    parts = [props.get("state", "?")]
    for key in ("method", "target", "count", "candidate", "l0"):
        if props.get(key) not in (None, ""):
            parts.append(f"{key} {props[key]}")
    if props.get("producer") == "derived":
        parts.append("[derived]")
    return "  ".join(str(part) for part in parts)


def _table_text(name, value):
    if name == "diagnostic":
        items = value if isinstance(value, list) else [value]
        return "; ".join(f"{item.get('id')} {item.get('label', '')}".strip() for item in items)
    if isinstance(value, list):
        value = value[0] if value else {}
    return ", ".join(f"{key} {compact(entry)}" for key, entry in sorted(value.items()))


def compact(value):
    """A nested value in one line: a table of tables and a list of tables by
    the names of their entries; `kb raw` prints them whole."""
    if isinstance(value, dict) and value and all(isinstance(entry, dict)
                                                 for entry in value.values()):
        return ", ".join(sorted(value))
    if isinstance(value, list) and value and all(isinstance(entry, dict) for entry in value):
        return "; ".join(str(entry.get("name") or entry.get("id") or "?") for entry in value)
    if isinstance(value, list):
        return ", ".join(str(entry) for entry in value)
    return value


def _l0_sections(graph, answer, layout, address, data, root):
    entries = accessors(graph, layout, address)
    if entries:
        data["accessors"] = [_access_data(entry) for entry in entries]
        answer.section(f"l0 accessors: {access_summary(entries)}", DETAIL,
                       [access_line(entry) for entry in entries])
    facts = function_facts(graph, layout, address)
    if facts:
        node = facts["f"]
        rows = callers(graph, layout, address)
        data["function"] = {**node, "callers": [row["function"] for row in rows]}
        lines = [f"  [l0] {node.get('size')} bytes, {node.get('instructions')} instructions, "
                 f"{facts['callees']} callees, {facts['locations']} locations"]
        lines.extend(f"  [l0] called by {function_ref(row)} at {hexes(row['sites'] or [])}"
                     for row in rows)
        answer.section("l0 function", DETAIL, lines)


def _show_location(graph, ref, root):
    answer = at(graph, ref.text, root=root)
    answer.rest = f"kb show {ref.text} --budget <tokens>"
    for section in answer.sections:
        if section.priority == DETAIL:
            section.lines = []
    entries = accessors(graph, ref.layout, ref.address)
    answer.section("l0 accessors", DETAIL, [access_line(entry) for entry in entries])
    rows = callers(graph, ref.layout, ref.address)
    answer.section("l0 callers", DETAIL,
                   [f"  [l0] {function_ref(row)} at {hexes(row['sites'] or [])}" for row in rows])
    return answer


# kb where ------------------------------------------------------------------------------------

def where(graph, text, root=repo.ROOT):
    ref = refs.resolve(graph, text, root=root)
    if ref.kind == "location":
        raise KbError(f"{ref.text} holds no symbol; kb at {ref.text} shows its L0 facts", code=5)
    meaning = ref.meaning if ref.kind == "symbol" else ref.node
    answer = Answer(f"kb show {meaning['key']}")
    head = ["  ".join(filter(None, (meaning["key"], meaning.get("level"),
                                    f"home {meaning.get('home')}", headline(meaning))))]
    if ref.note:
        head.insert(0, f"note: {ref.note}")
    answer.section(None, IDENTITY, head)
    members = {row["s"]["layout"]: row["s"] for row in graph.run(
        "MATCH (:Kb:Meaning {key: $key})-[:HAS]->(s:Kb:Symbol) RETURN s", key=meaning["key"])}
    statuses = {row["layout"]: row["props"] for row in graph.run(
        "MATCH (:Kb:Meaning {key: $key})-[r:STATUS]->(l:Kb:Layout) "
        "RETURN l.key AS layout, properties(r) AS props", key=meaning["key"])}
    lines, data = [], {"meaning": meaning["key"], "layouts": {}}
    for layout in repo.layouts(root):
        if layout in members:
            symbol = members[layout]
            first = next(iter(symbol.get("evidence") or ()), None)
            parts = [f"{layout:<6}", f"{symbol['address']:08x}",
                     symbol.get("level") or meaning.get("level") or ""]
            if symbol["name"] != meaning["name"]:
                parts.append(symbol_ref(symbol))
            if first:
                parts.append(evidence_line(first))
            lines.append("  ".join(filter(None, parts)))
            data["layouts"][layout] = {"symbol": symbol_ref(symbol)}
        elif layout in statuses:
            lines.append(f"{layout:<6}  {_status_text(statuses[layout])}")
            data["layouts"][layout] = statuses[layout]
        else:
            lines.append(f"{layout:<6}  -")
    answer.section(None, FACTS, lines)
    data['analogs'] = analogs_of(graph, meaning)
    answer.section('analogs', DETAIL,
                   [f'  {item["to"]}: {item["note"]}' for item in data['analogs']])
    answer.data = data
    return answer


# Link graphs for impact and path ---------------------------------------------------------------

class LinkGraph:
    """The typed links of one layout's symbols, or of the meanings, as edges
    from what a change starts at to what it reaches (section 7.5).

    Edge categories: `value` joins two data, `read` a datum and a function
    that depends on it, `write` a function and a datum or DTC it produces,
    `call` two functions, and `cite` an entity and a claim whose evidence
    names it. A node whose degree exceeds the 99th percentile of its kind is
    a hub (section 12.4).
    """

    def __init__(self, graph, layout=None):
        if layout is None:
            nodes = graph.run("MATCH (m:Kb:Meaning) RETURN m.key AS key, m.kind AS kind, "
                              "m.name AS name")
            rows = graph.run("MATCH (a:Kb:Meaning)-[r]->(b:Kb:Meaning) "
                             "RETURN a.key AS a, type(r) AS type, b.key AS b, r.role AS role, "
                             "null AS verified")
            self.refs = {row["key"]: row["key"] for row in nodes}
        else:
            nodes = graph.run("MATCH (s:Kb:Symbol {layout: $layout}) RETURN s.key AS key, "
                              "s.kind AS kind, s.name AS name, s.layout AS layout, "
                              "s.address AS address", layout=layout)
            rows = graph.run("MATCH (a:Kb:Symbol {layout: $layout})-[r]->(b:Kb:Symbol) "
                             "RETURN a.key AS a, type(r) AS type, b.key AS b, r.role AS role, "
                             "r.verified AS verified", layout=layout)
            self.refs = {row["key"]: symbol_ref(row) for row in nodes}
        self.kinds = {row["key"]: row["kind"] for row in nodes}
        self.edges = defaultdict(lambda: defaultdict(list))
        self.degree = defaultdict(int)
        for row in rows:
            edge = self._edge(row)
            if edge is None:
                continue
            parent, child, category, fact = edge
            self.degree[parent] += 1
            self.degree[child] += 1
            self.edges[category][parent].append((child, row["type"], fact, row["verified"]))
        for category in self.edges.values():
            for items in category.values():
                items.sort(key=lambda item: (item[0], item[1]))
        by_kind = defaultdict(list)
        for key, kind in self.kinds.items():
            by_kind[kind].append(self.degree.get(key, 0))
        self.threshold = {kind: _percentile(values, HUB_PERCENTILE)
                          for kind, values in by_kind.items()}

    def _edge(self, row):
        """(parent, child, category, fact) of a link, or None."""
        owner, kind, to = row["a"], row["type"], row["b"]
        roles = set(row["role"] or ())
        if kind not in FORWARD or kind == "DEPENDS" and roles & SYMMETRIC_ROLES:
            return None
        if kind == "DEPENDS":
            if roles & TO_DEPENDS_ROLES:
                parent, child = owner, to
            else:
                parent, child = to, owner
            fact = f"{self.ref(child)} {depends_phrase(True, roles)} {self.ref(parent)}"
        elif kind in TO_DEPENDS:
            parent, child = owner, to
            fact = f"{self.ref(to)} {BACKWARD[kind]} {self.ref(owner)}"
        else:
            parent, child = to, owner
            fact = f"{self.ref(owner)} {FORWARD[kind]} {self.ref(to)}"
        if kind == "CITES":
            return parent, child, "cite", fact
        functions = (self.kinds.get(parent) == "fn", self.kinds.get(child) == "fn")
        category = {(False, False): "value", (False, True): "read", (True, False): "write",
                    (True, True): "call"}[functions]
        return parent, child, category, fact

    def hub(self, key):
        return self.degree.get(key, 0) > self.threshold.get(self.kinds.get(key), math.inf)

    def ref(self, key):
        return self.refs.get(key, key)

    def step(self, key, categories):
        for category in categories:
            yield from self.edges[category].get(key, ())


def _percentile(values, percent):
    ordered = sorted(values)
    if not ordered:
        return math.inf
    index = max(0, math.ceil(percent / 100 * len(ordered)) - 1)
    return ordered[index]


def _start(graph, ref, root):
    """(layout or None, start key) of a reference in a LinkGraph."""
    if ref.kind == "symbol":
        return ref.layout, ref.node["key"]
    if ref.kind == "meaning":
        if ref.layout:
            raise KbError(f"{ref.node['key']} has no symbol on {ref.layout}", code=5)
        return None, ref.node["key"]
    if ref.kind == "entity":
        raise KbError(f"{ref.text} holds no symbol; kb show {ref.text} lists its links", code=5)
    raise KbError(f"{ref.text} holds no symbol; kb at {ref.text} shows its L0 facts", code=5)


def _expanded(graph, texts, layout, root):
    keys = set()
    for text in texts or ():
        ref = refs.resolve(graph, text, layout, root)
        keys.add(ref.node["key"] if ref.kind in ("symbol", "meaning") else ref.text)
    return keys


# kb impact -------------------------------------------------------------------------------------

def impact(graph, text, layout=None, expand=(), root=repo.ROOT):
    """What a change to a reference reaches: the data computed from it through
    value links, transitively; the functions that read the reference or any of
    those data; the functions that consume a function reference; the claims
    whose evidence cites it; and the fields that carry the reference or one of
    those data and the features that require any of them. A field or a
    feature reaches the features that require it (`_entity_impact`)."""
    ref = refs.resolve(graph, text, layout, root)
    if ref.kind == "entity" and ref.node.get("kind") in ("field", "feature"):
        return _entity_impact(graph, ref, layout, root)
    scope, start = _start(graph, ref, root)
    links = LinkGraph(graph, scope)
    opened = _expanded(graph, expand, scope, root)
    depth = {start: 0}
    values, hubs = [], {}
    queue = deque([start])
    while queue:
        key = queue.popleft()
        if key != start and links.hub(key) and key not in opened:
            hubs[key] = links.degree[key]
            continue
        categories = ("value", "write") if key == start else ("value",)
        for child, kind, fact, verified in links.step(key, categories):
            if child in depth:
                continue
            depth[child] = depth[key] + 1
            values.append((depth[child], child, fact, verified))
            queue.append(child)
    readers = {}
    for key in [start] + [child for _, child, _, _ in values]:
        for child, kind, fact, verified in links.step(key, ("read",)):
            readers.setdefault(child, (key, fact, verified))
    consumers = list(links.step(start, ("call",)))
    cites = list(links.step(start, ("cite",)))
    carried, required = dependents(
        graph, _meaning_keys(graph, scope, [start, *(child for _, child, _, _ in values)]),
        scope)
    answer = Answer(f"kb impact {ref.text} --budget <tokens>")
    head = [f"impact of {ref.text}: {len(values)} data, {len(readers)} reading functions"
            + (f", {len(consumers)} consuming functions" if consumers else "")
            + (f", {len(cites)} citing claims" if cites else "")
            + (f", {_counted(len(carried), 'field')}" if carried else "")
            + (f", {_counted(len({row[0] for row in required}), 'feature')}"
               if required else "")
            + (f"; {len(hubs)} hubs not expanded" if hubs else "")]
    if ref.note:
        head.insert(0, f"note: {ref.note}")
    answer.section(None, IDENTITY, head)
    # The fields and features precede the insertion points, which a budget
    # cuts first among sections of one priority.
    answer.section("fields", FACTS, [f"  {field} carries {meaning}" for field, meaning in carried])
    answer.section("features", FACTS, _requirement_lines(required, scope))
    points = _insertion_points(graph, ref, root)
    answer.section("insertion points", FACTS, points)
    levels = defaultdict(list)
    for level, child, fact, verified in values:
        levels[level].append(f"  {fact}" + (" (unverified)" if verified is False else ""))
    for level in sorted(levels):
        answer.section(f"data at depth {level}", max(DETAIL + 1, LINKS + 5 - level),
                       levels[level])
    answer.section("reading functions", DETAIL + 2, [
        f"  {fact}" + (" (unverified)" if verified is False else "")
        for _, (_, fact, verified) in sorted(readers.items(), key=lambda item: item[1][1])])
    answer.section("consuming functions", DETAIL + 1, [f"  {fact}" for _, _, fact, _ in consumers])
    answer.section("hubs not expanded", DETAIL, _hub_lines(links, hubs))
    answer.section("citing claims", EVIDENCE, [f"  {fact}" for _, _, fact, _ in cites])
    answer.data = {
        "ref": ref.text, "insertion_points": points,
        "fields": [{"field": field, "meaning": meaning} for field, meaning in carried],
        "features": _requirement_data(required),
        "data": [{"depth": level, "ref": links.ref(child), "fact": fact}
                 for level, child, fact, _ in values],
        "readers": {links.ref(child): fact for child, (_, fact, _) in readers.items()},
        "consumers": [fact for _, _, fact, _ in consumers],
        "cites": [fact for _, _, fact, _ in cites],
        "hubs": {links.ref(key): degree for key, degree in hubs.items()}}
    return answer


def _counted(count, noun):
    return f"{count} {noun}" + ("" if count == 1 else "s")


def _meaning_keys(graph, scope, keys):
    """The meaning keys of the start and the closure: the keys themselves over
    meanings, the meanings of the symbols over one layout."""
    if scope is None:
        return set(keys)
    return {row["key"] for row in graph.run(
        "MATCH (m:Kb:Meaning)-[:HAS]->(s:Kb:Symbol) WHERE s.key IN $keys "
        "RETURN DISTINCT m.key AS key", keys=sorted(keys))}


def dependents(graph, keys, layout=None):
    """The fields and features that depend on the meanings or entities of
    `keys` (section 12.4): [(field, meaning)] of the fields that carry a
    meaning of `keys`, and [(feature, required, layouts)] of the features
    that require a key, one of those fields, or a feature that they reach,
    transitively. `layouts` is None where the feature requires it on every
    target, and otherwise lists the targets that require it; over one layout
    the requirements of the other targets drop."""
    carried = [(row["field"], row["meaning"]) for row in graph.run(
        "MATCH (f:Kb:Entity {kind: 'field'})-[:CARRIES]->(m:Kb:Meaning) WHERE m.key IN $keys "
        "RETURN f.key AS field, m.key AS meaning ORDER BY field, meaning", keys=sorted(keys))]
    reached = set(keys) | {field for field, _ in carried}
    frontier, required = set(reached), {}
    while frontier:
        rows = graph.run(
            "MATCH (e:Kb:Entity {kind: 'feature'})-[r:REQUIRES]->(x) WHERE x.key IN $keys "
            "RETURN e.key AS feature, x.key AS required, r.layouts AS layouts",
            keys=sorted(frontier))
        frontier = set()
        for row in rows:
            if layout is not None and row["layouts"] and layout not in row["layouts"]:
                continue
            pair = (row["feature"], row["required"])
            # A requirement of the feature itself holds on every target.
            if row["layouts"] is None or required.get(pair, ()) is None:
                required[pair] = None
            else:
                required[pair] = sorted({*required.get(pair, ()), *row["layouts"]})
            if row["feature"] not in reached:
                reached.add(row["feature"])
                frontier.add(row["feature"])
    return carried, [(feature, key, layouts)
                     for (feature, key), layouts in sorted(required.items())]


def _requirement_lines(required, scope=None):
    return [f"  {feature} requires {key}"
            + (f" on {', '.join(layouts)}" if layouts and scope is None else "")
            for feature, key, layouts in required]


def _requirement_data(required):
    return [{"feature": feature, "requires": key, "layouts": layouts}
            for feature, key, layouts in required]


def _insertion_points(graph, ref, root=repo.ROOT):
    """Per layout, the instructions that access the reference's symbol: the
    accesses of its location, or the calls of its function. A meaning states
    every layout: its status, or the absence of one, where it has no
    symbol."""
    if ref.kind == "symbol":
        members, statuses = {ref.node["layout"]: ref.node}, {}
        layouts = [ref.node["layout"]]
    else:
        members = _members(graph, ref.node["key"])
        statuses = _statuses(graph, ref.node["key"])
        layouts = list(repo.layouts(root))
    lines = []
    for layout in layouts:
        symbol = members.get(layout)
        if symbol is None:
            lines.append(f"  {layout:<6} {_absence(statuses.get(layout))}")
            continue
        address = symbol["address"]
        if symbol["kind"] == "fn":
            rows = callers(graph, layout, address)
            lines.extend(f"  {layout:<6} [l0] call {hexes(row['sites'] or [])} in "
                         f"{function_ref(row)}" for row in rows)
            if not rows:
                lines.append(f"  {layout:<6} entry {address:08x}, no L0 caller")
            continue
        entries = accessors(graph, layout, address)
        lines.extend(f"  {layout:<6}{access_line(entry)[1:]}" for entry in entries)
        if not entries:
            lines.append(f"  {layout:<6} no L0 access of {address:08x}")
    return lines


def _members(graph, key):
    """{layout: symbol} of a meaning."""
    return {row["s"]["layout"]: row["s"] for row in graph.run(
        "MATCH (:Kb:Meaning {key: $key})-[:HAS]->(s:Kb:Symbol) RETURN s", key=key)}


def _statuses(graph, key):
    """{layout: {status, current}} of a meaning, as `gap_detail` reads them."""
    return {row["layout"]: row for row in graph.run(
        "MATCH (:Kb:Meaning {key: $key})-[r:STATUS]->(l:Kb:Layout) "
        "RETURN l.key AS layout, properties(r) AS status, substring(l.l0, 0, 16) AS current",
        key=key)}


def _absence(row):
    """The status of a meaning on a layout where it has no symbol."""
    if row is None:
        return "no symbol and no status"
    status = row["status"]
    return "  ".join(filter(None, (
        status.get("state", "unknown"), gap_detail(row),
        "[derived]" if status.get("producer") == "derived" else None)))


def _entity_impact(graph, ref, layout, root):
    """What a change to a field or a feature reaches: the features that
    require it, transitively, and the signal that a field serves. The
    insertion points of a field are its source on every layout that such a
    feature targets (`_field_points`), and those of a feature its target on
    every layout with the hook sites (`_feature_points`)."""
    node, kind = ref.node, ref.node["kind"]
    _, required = dependents(graph, {node["key"]}, layout)
    features = sorted({feature for feature, _, _ in required})
    layouts = [item for item in repo.layouts(root) if layout in (None, item)]
    signals = []
    if kind == "field":
        signals = [row["signal"] for row in graph.run(
            "MATCH (:Kb:Entity {key: $key})-[:SERVES]->(s:Kb:Entity) RETURN s.key AS signal "
            "ORDER BY signal", key=node["key"])]
        points = _field_points(graph, node, features, layouts)
    else:
        points = _feature_points(graph, node, layouts)
    answer = Answer(f"kb impact {ref.text} --budget <tokens>")
    answer.section(None, IDENTITY, [
        f"impact of {ref.text}: {_counted(len(features), 'feature')}"
        + (f", {_counted(len(signals), 'signal')}" if signals else "")])
    answer.section("features", FACTS, _requirement_lines(required, layout))
    answer.section("signals", FACTS, [f"  {ref.text} serves {signal}" for signal in signals])
    answer.section("insertion points", FACTS, points)
    answer.data = {"ref": ref.text, "insertion_points": points, "fields": [],
                   "features": _requirement_data(required), "signals": signals, "data": [],
                   "readers": {}, "consumers": [], "cites": [], "hubs": {}}
    return answer


def _field_points(graph, node, features, layouts):
    """Per layout that a feature of `features` targets, the source that the
    field reads there. An `ecu_ram` field reads the symbol that fills its role
    in a target, or else the symbol of its source meaning; where the meaning
    has only a status, the field is unavailable. A field of another origin
    reads its allocation (`_allocation_points`)."""
    targeted = defaultdict(list)
    for row in graph.run(
            "MATCH (f:Kb:Entity {kind: 'feature'})-[t:TARGETS]->(l:Kb:Layout) "
            "WHERE f.key IN $features RETURN f.slug AS feature, l.key AS layout, "
            "t.roles AS roles ORDER BY feature", features=features):
        targeted[row["layout"]].append(row)
    layouts = [layout for layout in layouts if layout in targeted]
    if node.get("origin") != "ecu_ram":
        return _allocation_points(graph, node, layouts)
    sources = [row["key"] for row in graph.run(
        "MATCH (:Kb:Entity {key: $key})-[:CARRIES]->(m:Kb:Meaning) RETURN m.key AS key "
        "ORDER BY key", key=node["key"])]
    if not sources:
        return [f"  {layout:<6} the field carries no meaning" for layout in layouts]
    source = sources[0]
    roles = {(layout, row["feature"]): row["roles"][node["slug"]]
             for layout, rows in targeted.items() for row in rows
             if (row["roles"] or {}).get(node["slug"])}
    filled = {role["symbol"] for role in roles.values()}
    members = {key: _members(graph, key) for key in {source, *filled}}
    statuses = _statuses(graph, source)
    lines = []
    for layout in layouts:
        found = [(feature, role) for (at, feature), role in sorted(roles.items())
                 if at == layout]
        for feature, role in found:
            symbol = members[role["symbol"]].get(layout)
            lines.append(f"  {layout:<6} "
                         + (symbol_ref(symbol) if symbol else
                            f"{role['symbol']}, which has no symbol,")
                         + f" fills {feature}.{node['slug']}")
        if found:
            continue
        symbol = members[source].get(layout)
        if symbol is not None:
            lines.append(f"  {layout:<6} {symbol_ref(symbol)}")
        elif layout in statuses:
            lines.append(f"  {layout:<6} unavailable: {source} {_absence(statuses[layout])}")
        else:
            lines.append(f"  {layout:<6} {source} has no symbol and no status")
    return lines


def _allocation_points(graph, node, layouts):
    """Per layout, the allocation `<feature>.<name>` that a field of another
    origin than `ecu_ram` reads: the address that the target of the feature
    states there, or else its `7mfk` address moved by the `ram_delta` or the
    `rom_delta` of the `runtime` target of the layout, whichever span of the
    `7mfk` runtime holds it."""
    owner, _, name = str(node.get("source") or "").partition(".")
    stated = {row["layout"]: (row["allocations"] or {}).get(name) for row in graph.run(
        "MATCH (:Kb:Entity {key: $key})-[t:TARGETS]->(l:Kb:Layout) "
        "RETURN l.key AS layout, t.allocations AS allocations", key=f"{owner}/feature")}
    runtime = {row["layout"]: row["target"] for row in graph.run(
        "MATCH (:Kb:Entity {key: 'runtime/feature'})-[t:TARGETS]->(l:Kb:Layout) "
        "RETURN l.key AS layout, properties(t) AS target")}
    base = stated.get(targets.CANONICAL)
    if base is None:
        return [f"  {layout:<6} {node.get('source')} is no allocation of a "
                f"{targets.CANONICAL} target" for layout in layouts]
    address, width = int(base["address"], 16), base["width"]
    canonical = runtime.get(targets.CANONICAL) or {}
    delta = None
    for space in ("ram", "rom"):
        start = canonical.get(f"injected_{space}_start")
        end = canonical.get(f"injected_{space}_end")
        if start and end and int(start, 16) <= address < int(end, 16):
            delta = f"{space}_delta"
    lines = []
    for layout in layouts:
        entry = stated.get(layout)
        if entry is not None:
            lines.append(f"  {layout:<6} {node['source']} at {entry['address']}, "
                         f"{_counted(entry['width'], 'byte')}")
        elif delta and isinstance((runtime.get(layout) or {}).get(delta), int):
            moved = runtime[layout][delta]
            lines.append(f"  {layout:<6} {node['source']} at {address + moved:08x}, "
                         f"{_counted(width, 'byte')}  [derived] {delta} {moved:+#x}")
        else:
            lines.append(f"  {layout:<6} {node['source']} has no address on the layout")
    return lines


def _feature_points(graph, node, layouts):
    """Per layout, the target of a feature: its status, the spans of an
    injected runtime, and the hook sites with their replacements."""
    found = {row["layout"]: row["target"] for row in graph.run(
        "MATCH (:Kb:Entity {key: $key})-[t:TARGETS]->(l:Kb:Layout) "
        "RETURN l.key AS layout, properties(t) AS target", key=node["key"])}
    hooks = sorted({entry["hook"] for target in found.values()
                    for entry in (target.get("hooks") or {}).values()})
    sites = {(row["meaning"], row["s"]["layout"]): row["s"] for row in graph.run(
        "MATCH (m:Kb:Meaning)-[:HAS]->(s:Kb:Symbol) WHERE m.key IN $keys "
        "RETURN m.key AS meaning, s", keys=hooks)}
    lines = []
    for layout in layouts:
        target = found.get(layout)
        if target is None:
            lines.append(f"  {layout:<6} no target")
            continue
        spans = [f"{label} {target[f'injected_{space}_start']}..{target[f'injected_{space}_end']}"
                 for space, label in (("rom", "ROM"), ("ram", "RAM"))
                 if target.get(f"injected_{space}_start") and target.get(f"injected_{space}_end")]
        entries = sorted((target.get("hooks") or {}).items())
        lines.append(f"  {layout:<6} " + "; ".join([str(target.get("status")), *spans]
                                                   + ([] if entries else ["no hook"])))
        for key, entry in entries:
            symbol = sites.get((entry["hook"], layout))
            lines.append(f"  {layout:<6} {key} at "
                         + (symbol_ref(symbol) if symbol else
                            f"{entry['hook']}, which has no symbol")
                         + (f"  replacement {entry['replacement']}"
                            if entry.get("replacement") else ""))
    return lines


# kb path ------------------------------------------------------------------------------------------

# Searches of `kb path` in order: dataflow from the first reference to the
# second, then from the second to the first, then links in any direction.
# Every search follows value links and the links of the functions that read,
# write, and call; among paths of one length it prefers value links.
SEARCHES = (("dataflow", False, False), ("reverse dataflow", True, False),
            ("undirected", False, True))
PATH_CATEGORIES = ("value", "read", "write", "call")


def path(graph, first, second, layout=None, expand=(), limit=3, root=repo.ROOT):
    a = refs.resolve(graph, first, layout, root)
    b = refs.resolve(graph, second, layout, root)
    scope_a, start = _start(graph, a, root)
    scope_b, goal = _start(graph, b, root)
    if scope_a != scope_b:
        raise KbError(f"{a.text} and {b.text} lie on different layouts; "
                      "name meanings or pass --layout", code=2)
    links = LinkGraph(graph, scope_a)
    opened = _expanded(graph, expand, scope_a, root)
    answer = Answer(f"kb path {first} {second} --budget <tokens>")
    found, hubs, through = None, set(), None
    for label, reverse, undirected in SEARCHES:
        edges = _edges(links, PATH_CATEGORIES, undirected)
        ends = (goal, start) if reverse else (start, goal)
        paths, cut = _shortest(links, edges, *ends, opened, limit)
        hubs |= cut
        shortcuts, _ = _shortest(links, edges, *ends, None, PATH_CANDIDATES)
        if shortcuts and (not paths or len(shortcuts[0]) < len(paths[0])):
            shortcut = min(shortcuts, key=lambda steps: _hub_cost(links, steps, opened))
            if through is None or len(shortcut) < len(through[1]):
                through = (label, shortcut)
        if paths:
            found = (label, ends, paths)
            break
    head = [f"note: {ref.note}" for ref in (a, b) if ref.note]
    hint = _through_hubs(links, through, opened)
    if found is None:
        head.append(f"no path between {a.text} and {b.text} through typed links without hubs")
        answer.section(None, IDENTITY, head)
        answer.section("through hubs", FACTS, hint)
        answer.section("hubs not expanded", DETAIL, _hub_lines(links, dict.fromkeys(hubs)))
        answer.data = {"from": a.text, "to": b.text, "paths": [],
                       "through_hubs": _through_data(links, through, opened)}
        return answer
    label, (source, target), paths = found
    source_ref, target_ref = links.ref(source), links.ref(target)
    count = f"{len(paths)} shortest path" + ("s" if len(paths) > 1 else "")
    head.append(f"path {source_ref} -> {target_ref}: {count} of {len(paths[0])} links, {label}"
                + (f" (the first {limit})" if len(paths) == limit else ""))
    answer.section(None, IDENTITY, head)
    answer.section("shorter through hubs", LINKS, hint)
    for number, steps in enumerate(paths, 1):
        answer.section(f"path {number}", LINKS - number,
                       [f"  {fact}" + (" (unverified)" if verified is False else "")
                        for _, _, fact, verified in steps])
    answer.section("hubs not expanded", DETAIL, _hub_lines(links, dict.fromkeys(hubs)))
    answer.data = {"from": source_ref, "to": target_ref, "search": label,
                   "paths": [[fact for _, _, fact, _ in steps] for steps in paths],
                   "through_hubs": _through_data(links, through, opened),
                   "hubs": {links.ref(key): links.degree[key] for key in hubs}}
    return answer


def _hub_cost(links, steps, opened):
    """Order of the paths through hubs: fewer hubs, then lower degrees."""
    hubs = _hubs_on(links, steps, opened)
    return len(hubs), sum(links.degree[key] for key in hubs)


def _hubs_on(links, steps, opened):
    """The hubs that a path passes through, in path order."""
    inner = [parent for parent, _, _, _ in steps[1:]]
    return [key for key in inner if links.hub(key) and key not in opened]


def _through_hubs(links, through, opened):
    if through is None:
        return []
    label, steps = through
    hubs = _hubs_on(links, steps, opened)
    options = " ".join(f"--expand {links.ref(key)}" for key in hubs)
    lines = [f"  {len(steps)} links, {label}, through "
             + ", ".join(f"{links.ref(key)} (degree {links.degree[key]})" for key in hubs),
             f"  {options} shows it"]
    return lines


def _through_data(links, through, opened):
    if through is None:
        return None
    label, steps = through
    return {"search": label, "links": len(steps),
            "hubs": [links.ref(key) for key in _hubs_on(links, steps, opened)]}


def _hub_lines(links, hubs, limit=5):
    ordered = sorted(hubs, key=lambda key: (-links.degree[key], key))
    lines = [f"  {links.ref(key)}  degree {links.degree[key]}  (--expand {links.ref(key)})"
             for key in ordered[:limit]]
    if len(ordered) > limit:
        lines.append(f"  +{len(ordered) - limit} more hubs")
    return lines


def _edges(links, categories, undirected):
    """Adjacency of the categories: key -> [(other, category, fact, verified)]."""
    edges = defaultdict(list)
    for category in categories:
        for parent, children in links.edges[category].items():
            for child, _, fact, verified in children:
                edges[parent].append((child, category, fact, verified))
                if undirected:
                    edges[child].append((parent, category, fact, verified))
    return edges


def _shortest(links, edges, source, target, opened, limit):
    """Up to `limit` shortest paths from source to target as lists of
    (parent, category, fact, verified) edges, those with more value links
    first. Hubs other than the source and the keys of `opened` are not
    expanded; `opened=None` expands every hub. Returns the paths and the hubs
    met closer to the source than the target."""
    distance = {source: 0}
    parents = defaultdict(list)
    hubs = set()
    queue = deque([source])
    while queue:
        key = queue.popleft()
        if key == target:
            continue
        if target in distance and distance[key] >= distance[target]:
            continue
        if opened is not None and key != source and links.hub(key) and key not in opened:
            hubs.add(key)
            continue
        for child, category, fact, verified in sorted(edges.get(key, ()),
                                                      key=lambda item: (item[0], item[2])):
            if child not in distance:
                distance[child] = distance[key] + 1
                queue.append(child)
            if distance[child] == distance[key] + 1:
                parents[child].append((key, category, fact, verified))
    if target not in distance:
        return [], hubs
    found = []

    def walk(key, tail):
        if len(found) >= PATH_CANDIDATES:
            return
        if key == source:
            found.append(list(reversed(tail)))
            return
        for parent, category, fact, verified in parents[key]:
            walk(parent, tail + [(parent, category, fact, verified)])

    walk(target, [])
    found.sort(key=lambda steps: (sum(category != "value" for _, category, _, _ in steps),
                                  [fact for _, _, fact, _ in steps]))
    return found[:limit], {hub for hub in hubs if distance.get(hub, math.inf) < distance[target]}


# kb find ---------------------------------------------------------------------------------------

def _trigrams(text):
    return {text[index:index + 3] for index in range(len(text) - 2)}


def find(graph, words, limit=15, root=repo.ROOT):
    query = [word for word in WORD.findall(" ".join(words).lower())]
    if not query:
        raise KbError("kb find needs at least one word", code=2)
    rows = graph.run(
        "MATCH (m:Kb:Meaning) OPTIONAL MATCH (m)-[:HAS]->(s:Kb:Symbol) "
        "WITH m, collect(s) AS symbols "
        "RETURN m.key AS key, m.name AS name, m.kind AS kind, m.home AS home, m.title AS title, "
        "m.summary AS summary, m.former AS former, symbols, false AS designed "
        "UNION ALL MATCH (e:Kb:Entity) "
        "RETURN e.key AS key, e.slug AS name, e.kind AS kind, null AS home, e.title AS title, "
        "e.summary AS summary, [] AS former, [] AS symbols, true AS designed")
    docs = []
    for row in rows:
        fields = [row["name"] or "", " ".join(row["former"] or ()), row["title"] or "",
                  row["summary"] or ""]
        home = next((symbol for symbol in row["symbols"] if symbol["layout"] == row["home"]),
                    None)
        text = [field.lower() for field in fields]
        docs.append({"key": row["key"], "fields": text, "row": row, "home": home,
                     "tokens": [WORD.findall(field.replace("_", " ").replace("-", " "))
                                for field in text]})
    grams = [_trigrams(word) for word in query]
    phrase = " ".join(query)
    ident = "_".join(query)

    def has(doc, word):
        return any(token.startswith(word) for tokens in doc["tokens"] for token in tokens)

    frequency = {word: sum(1 for doc in docs if has(doc, word)) for word in query}
    idf = {word: math.log((len(docs) + 1) / (frequency[word] + 1)) + 1 for word in query}
    total = sum(idf.values())
    ranked = []
    for doc in docs:
        blob = " ".join(doc["fields"])
        if not any(gram <= _trigrams(blob) or len(word) < 3
                   for word, gram in zip(query, grams)):
            continue
        matched = [word for word in query if has(doc, word)]
        if not matched:
            continue
        name, former, title, summary = doc["fields"]
        names = [name] + former.split()
        if ident in names or phrase == title:
            tier = 0
        elif any(item.startswith(ident) for item in names) or title.startswith(phrase):
            tier = 1
        elif any(ident in item for item in names) or phrase in title or phrase in summary:
            tier = 2
        else:
            tier = 3
        score = (sum(idf[word] for word in matched) / total) ** 2
        field = min(index for index, tokens in enumerate(doc["tokens"])
                    if any(token.startswith(word) for word in matched for token in tokens))
        ranked.append((tier, -score, field, doc["key"], score, doc))
    ranked.sort(key=lambda item: item[:4])
    answer = Answer(f"kb find {' '.join(words)} --budget <tokens>")
    head = [f"find {' '.join(query)}: {len(ranked)} matches"
            + (f", first {limit}" if len(ranked) > limit else "")]
    if len(ranked) > 1 and ranked[0][0] == ranked[1][0] and ranked[1][4] >= 0.9 * ranked[0][4]:
        close = sum(1 for item in ranked if item[0] == ranked[0][0]
                    and item[4] >= 0.9 * ranked[0][4])
        head.append(f"ambiguous: {close} matches score within 10 percent of the first")
    answer.section(None, IDENTITY, head)
    lines, data = [], []
    for tier, _, field, key, score, doc in ranked[:limit]:
        row = doc["row"]
        ref = symbol_ref(doc["home"]) if doc["home"] else key
        lines.append(f"  {ref}  {headline(row, 72)}")
        data.append({"ref": ref, "entity" if row["designed"] else "meaning": key,
                     "tier": ("exact", "prefix", "substring", "words")[tier],
                     "score": round(score, 4), "field": ("name", "former", "title",
                                                         "summary")[field]})
    answer.section(None, FACTS, lines)
    answer.data = {"query": query, "results": data, "total": len(ranked)}
    return answer


# kb gaps ----------------------------------------------------------------------------------------

# The order of the status groups: no search yet, a search without a unique
# result, a mechanism that the layout lacks, and a field source that the
# target of the layout does not support.
GAP_STATES = ("unknown", "unresolved", "absent", "unsupported")
FAMILY = "family"


def gap_rows(graph, feature=None, layout=None):
    """[{feature, layout, field, meaning, status, current}] of the required
    meanings unavailable on a layout: those a feature requires directly or
    through the `requires` of its target on the layout without a symbol
    there, the source meanings of its fields by the rule of
    `matrix.unavailable`, and without `feature`, those a symbol on another
    layout of the family requires. A field source that the target lists as
    `unsupported` has the status `unsupported` with the note of the entry; a
    field whose role a symbol of the target fills is available. `current` is
    the L0 digest of the layout, which a stale search does not match."""
    rows = graph.run(
        "MATCH (f:Kb:Entity {kind: 'feature'})-[t:TARGETS]->(l:Kb:Layout) "
        "WHERE ($feature IS NULL OR f.slug = $feature) AND ($layout IS NULL OR l.key = $layout) "
        "MATCH (f)-[q:REQUIRES]->(x) WHERE q.layouts IS NULL OR l.key IN q.layouts "
        "OPTIONAL MATCH (x)-[:CARRIES]->(c:Kb:Meaning) "
        "WITH f, l, t, x, CASE WHEN x:Meaning THEN x ELSE c END AS m WHERE m IS NOT NULL "
        "OPTIONAL MATCH (m)-[:HAS]->(s:Kb:Symbol) WHERE s.layout = l.key "
        "WITH f, l, t, x, m, s, CASE WHEN x:Meaning THEN [] ELSE "
        "[entry IN coalesce(t.unsupported, []) WHERE entry.symbol = m.key | entry.note] "
        "END AS unsupported WHERE s IS NULL OR size(unsupported) > 0 "
        "OPTIONAL MATCH (m)-[r:STATUS]->(l) "
        "RETURN f.slug AS feature, l.key AS layout, "
        "CASE WHEN x:Meaning THEN null ELSE x.key END AS field, m.key AS meaning, "
        "properties(r) AS status, substring(l.l0, 0, 16) AS current, "
        "NOT x:Meaning AND x.slug IN keys(coalesce(t.roles, {})) AS filled, unsupported",
        feature=feature, layout=layout)
    rows = [row for row in map(_target_gap, rows) if row is not None]
    if feature is None:
        listed = {(row["meaning"], row["layout"]) for row in rows}
        rows += [row for row in graph.run(
            "MATCH (m:Kb:Meaning)-[r:STATUS {state: 'unknown'}]->(l:Kb:Layout) "
            "WHERE ($layout IS NULL OR l.key = $layout) AND $family IN r.required "
            "RETURN $family AS feature, l.key AS layout, null AS field, m.key AS meaning, "
            "properties(r) AS status, substring(l.l0, 0, 16) AS current",
            layout=layout, family=FAMILY) if (row["meaning"], row["layout"]) not in listed]
    return sorted(rows, key=lambda row: (row["feature"] == FAMILY, row["feature"],
                                         row["layout"], row["field"] or "", row["meaning"]))


def _target_gap(row):
    """A required row of a target as `matrix.unavailable` judges its field:
    an `unsupported` entry of the target first, then a role that a symbol of
    the target fills; None for an available field."""
    row = dict(row)
    notes, filled = row.pop("unsupported", None) or [], row.pop("filled", False)
    if notes:
        return {**row, "status": {"state": "unsupported", "note": notes[0]}}
    return None if filled else row


def gap_detail(row):
    """The note of an `unsupported` field, the search of an `unresolved`
    status, or the first evidence of an `absent` one; a status without either
    names its evidence kinds."""
    status = row["status"] or {}
    if status.get("state") == "unsupported":
        return status.get("note") or ""
    if status.get("method"):
        parts = [status["method"], status.get("target")]
        if status.get("count") is not None:
            parts.append(f"count {status['count']}")
        if status.get("candidate"):
            parts.append(f"candidate {status['candidate']}")
        if status.get("l0") and row.get("current") and status["l0"] != row["current"]:
            parts.append("stale")
        return "  ".join(str(part) for part in parts if part not in (None, ""))
    evidence = status.get("evidence") or ()
    typed = [item for item in evidence if item.get("kind") != "registry"]
    if typed:
        item = typed[0]
        return "  ".join(str(part) for part in (item["kind"], item.get("at") or item.get("to"))
                         if part)
    return " ".join(sorted({item.get("kind", "?") for item in evidence}))


def gap_summary(rows):
    """Totals of the same required binding rows that `kb gaps` lists."""
    def counts(key):
        return dict(sorted(Counter(row[key] for row in rows).items()))

    states = Counter((row["status"] or {}).get("state", "unknown") for row in rows)
    return {"total": len(rows), "features": counts("feature"), "layouts": counts("layout"),
            "states": {state: states[state] for state in
                       GAP_STATES + tuple(sorted(set(states) - set(GAP_STATES)))}}


def gap_priorities(graph, rows, limit=5):
    """Missing bindings ranked by affected features, fields, then link degree.
    Family-only requirements follow requirements of project features."""
    bindings = {}
    for row in rows:
        key = row["meaning"], row["layout"]
        item = bindings.setdefault(key, {"meaning": row["meaning"], "layout": row["layout"],
                                        "state": (row["status"] or {}).get("state", "unknown"),
                                        "features": set(), "fields": set()})
        item["features"].add(row["feature"])
        if row["field"]:
            item["fields"].add(row["field"])
    if not bindings:
        return []
    degrees = {row["key"]: row["degree"] for row in graph.run(
        "MATCH (m:Kb:Meaning) WHERE m.key IN $keys OPTIONAL MATCH (m)-[r]-(:Kb:Meaning) "
        "RETURN m.key AS key, count(r) AS degree", keys=sorted({key[0] for key in bindings}))}
    ranked = sorted(bindings.values(), key=lambda item: (
        -len(item["features"] - {FAMILY}), -len(item["fields"]),
        -degrees.get(item["meaning"], 0), item["layout"], item["meaning"]))
    return [{**item, "features": sorted(item["features"]), "fields": sorted(item["fields"]),
             "degree": degrees.get(item["meaning"], 0)} for item in ranked[:limit]]


def gaps(graph, feature=None, layout=None, root=repo.ROOT):
    if feature is not None and not graph.run(
            "MATCH (f:Kb:Entity {kind: 'feature', slug: $feature}) RETURN f.key AS key",
            feature=feature):
        raise KbError(f"no feature {feature}; kb find {feature} lists near names", code=5)
    if layout is not None and layout not in repo.layouts(root):
        raise KbError(f"no layout {layout}", code=2)
    rows = gap_rows(graph, feature, layout)
    subject = " ".join(filter(None, (feature, f"on {layout}" if layout else None)))
    features = sorted({row["feature"] for row in rows})
    layouts = sorted({row["layout"] for row in rows})
    head = f"{len(rows)} required meanings unavailable"
    if not layout and rows:
        head += f" on {len(layouts)} layouts"
    if not feature and len(features) > 1:
        counts = defaultdict(int)
        for row in rows:
            counts[row["feature"]] += 1
        head += " (" + ", ".join(f"{name} {counts[name]}" for name in features) + ")"
    answer = Answer("kb gaps --feature <feature> --layout <layout>")
    answer.section(None, IDENTITY, [f"{subject}: {head}" if subject else head])
    groups = defaultdict(list)
    for row in rows:
        state = (row["status"] or {}).get("state", "unknown")
        columns = [f"{row['layout']:<6}" if not layout else None,
                   row["feature"] if not feature and len(features) > 1 else None,
                   row["field"], row["meaning"], gap_detail(row)]
        groups[state].append("  " + "  ".join(part for part in columns if part))
    for state in GAP_STATES + tuple(sorted(set(groups) - set(GAP_STATES))):
        if groups.get(state):
            answer.section(f"{state}: {len(groups[state])}", FACTS, groups[state])
    answer.data = {"gaps": [{**row, "state": (row["status"] or {}).get("state", "unknown")}
                            for row in rows], "gap_summary": gap_summary(rows)}
    return answer


# kb brief ---------------------------------------------------------------------------------------

def bench(root=repo.ROOT):
    return tomllib.loads((root / BENCH).read_text(encoding="utf-8"))


def brief(graph, root=repo.ROOT):
    from kb import graph as kbgraph

    answer = Answer("kb brief --budget <tokens>")
    meta = kbgraph.meta(graph) or {}
    data = {"meta": meta}
    answer.section(None, IDENTITY, [
        f"graph {graph.uri}: fingerprint {str(meta.get('fingerprint', '?'))[:16]}, commit "
        f"{str(meta.get('commit', '?'))[:10]}{' dirty' if meta.get('dirty') else ''}, loaded "
        f"{meta.get('loaded_at', '?')}, compiler {meta.get('compiler', '?')}, schema "
        f"{meta.get('schema', '?')}"])
    functions = {row["layout"]: row["n"] for row in graph.run(
        "MATCH (f:Kb:Function) RETURN f.layout AS layout, count(f) AS n")}
    symbols = defaultdict(dict)
    for row in graph.run("MATCH (s:Kb:Symbol) RETURN s.layout AS layout, s.kind AS kind, "
                         "count(s) AS n"):
        symbols[row["layout"]][row["kind"]] = row["n"]
    statuses = defaultdict(dict)
    for row in graph.run("MATCH (:Kb:Meaning)-[r:STATUS]->(l:Kb:Layout) "
                         "RETURN l.key AS layout, r.state AS state, count(r) AS n"):
        statuses[row["layout"]][row["state"]] = row["n"]
    lines = []
    for layout, info in repo.layouts(root).items():
        kinds = symbols.get(layout, {})
        text = ", ".join(f"{kinds[kind]} {kind}" for kind in sorted(kinds, key=lambda k: -kinds[k]))
        states = ", ".join(f"{count} {state}" for state, count in sorted(statuses[layout].items()))
        lines.append(f"  {layout:<6} {info.family:<18} {functions.get(layout, 0):>5} functions  "
                     f"{sum(kinds.values()):>5} symbols ({text or 'none'})"
                     + (f"  statuses: {states}" if states else ""))
    answer.section("layouts", FACTS, lines)
    data["layouts"] = {layout: {"functions": functions.get(layout, 0), "symbols": symbols[layout],
                                "statuses": statuses[layout]} for layout in repo.layouts(root)}
    config = bench(root)
    owners = [{"registry": spec.plain(row[0]), "owner": spec.plain(row[2])}
              for row in spec.table(spec.OWNERSHIP, root)]
    answer.section("fact owners", FACTS,
                   [f"  {row['registry']}: {row['owner']}" for row in owners])
    data["owners"] = owners
    research_rows = graph.run(
        "MATCH (c:Kb:Entity {kind: 'chain'})-[:STEP]->(s:Kb:Step) "
        "WHERE s.research IS NOT NULL RETURN c.key AS chain, count(s) AS n ORDER BY chain")
    research_total = sum(row['n'] for row in research_rows)
    answer.section(f"unresolved semantic review: {research_total} source-bound steps", FACTS,
                   [f"  {row['chain']}: {row['n']}" for row in research_rows] or ['  none'])
    data['research'] = {'total': research_total, 'chains': research_rows}
    required = gap_rows(graph)
    summary = gap_summary(required)
    priorities = gap_priorities(graph, required)
    unresolved = graph.run(
        "MATCH (m:Kb:Meaning)-[r:STATUS {state: 'unresolved'}]->(l:Kb:Layout) "
        "RETURN m.key AS key, l.key AS layout, r.l0 AS l0, substring(l.l0, 0, 16) AS current")
    stale = [row for row in unresolved if row["l0"] and row["l0"] != row["current"]]
    candidates = graph.run("MATCH (c:Kb:Candidate) RETURN count(c) AS n")[0]["n"]
    def totals(counts):
        return ", ".join(f"{key} {value}" for key, value in counts.items()) or "none"

    head = f"open gaps: {summary['total']} required meanings unavailable"
    if required:
        head += f" on {len(summary['layouts'])} layouts"
    answer.section(head, FACTS, [f"  by {key[:-1]}: {totals(summary[key])}"
                                for key in ("features", "layouts", "states")])
    answer.section("priority gaps: affected features, fields, then link degree", LINKS, [
        f"  {row['meaning']} on {row['layout']}  {row['state']}  "
        f"features {', '.join(row['features'])}; fields {', '.join(row['fields']) or 'none'}; "
        f"degree {row['degree']}" for row in priorities] or ["  none"])
    # A new L0 of a layout leaves every search of its statuses stale, so the
    # text counts them per layout and the data lists each one.
    stale_layouts = dict(sorted(Counter(row["layout"] for row in stale).items()))
    answer.section(f"stale searches: {len(stale)}; pending candidates: {candidates}", LINKS,
                   [f"  by layout: {totals(stale_layouts)}",
                    "  kb brief --json lists each search under stale"] if stale else ["  none"])
    data.update({"gaps": [{**row, "state": (row["status"] or {}).get("state", "unknown")}
                          for row in required], "gap_summary": summary,
                 "gap_priorities": priorities, "stale": stale, "candidates": candidates})
    questions = []
    for item in config["question"]:
        questions.append(f"  {item['id']:>2}  {item['command']:<46} {item['budget']:>5}"
                         f"  {item['question']}")
    answer.section("questions: command, budget in tokens", DETAIL, questions)
    data["questions"] = config["question"]
    answer.data = data
    return answer


# kb log and kb raw --------------------------------------------------------------------------------

def log(graph, text, root=repo.ROOT):
    from kb import history

    ref = refs.resolve(graph, text, root=root)
    if ref.kind == "location":
        raise KbError(f"{ref.text} holds no symbol", code=5)
    answer = Answer(f"kb show {ref.text}")
    lines = [ref.text]
    if ref.note:
        lines.append(f"  resolved: {ref.note}")
    meaning = (ref.meaning if ref.kind == "symbol" else ref.node) or {}
    for name in meaning.get("former") or ():
        lines.append(f"  {'former':<15} meaning name {name}")
    members = ([ref.node] if ref.kind == "symbol" else [row["s"] for row in graph.run(
        "MATCH (:Kb:Meaning {key: $key})-[:HAS]->(s:Kb:Symbol) RETURN s ORDER BY s.layout",
        key=meaning.get("key"))]) if ref.kind != "entity" else []
    symbols = []
    for node in members:
        former = history.former_references(node, meaning.get("src") or (), root)
        generated = node.get("generated")
        if generated == node.get("name"):
            generated = None
        if former or generated:
            current = symbol_ref(node)
            lines.append(f"  symbol          {current}")
            for previous in former:
                full = refs.FULL.fullmatch(previous)
                lines.append(f"  former          symbol {'reference' if full else 'name'} "
                             f"{previous}" + (f" -> {current}" if full else ""))
            if generated:
                lines.append(f"  generated name {generated}")
            symbols.append({"ref": current, "former": former, "generated": generated})
    changes = history.profile_changes(graph, meaning["key"], ref.layout if ref.kind == "symbol"
                                      else None, root) if meaning.get("key") and members else []
    sources = sorted(set(meaning.get("src") or ()) | set(
        (ref.node.get("src") or ()) if ref.kind == "symbol" else ()))
    lines.append(f"  sources: {', '.join(sources)}")
    if len(lines) == 2 + bool(ref.note) and not changes:
        lines.insert(1 + bool(ref.note), "  no rename or redirect recorded")
    answer.section(None, IDENTITY, lines)
    answer.section("recorded profile address corrections", FACTS, [
        f"  {item['commit'][:7]}  {item['layout']}  {item['table']}.{item['key']}: "
        f"{item['old']} -> {item['new']}  {item['source']}" for item in changes])
    answer.data = {"ref": ref.text, "former": list(meaning.get("former") or ()),
                   "symbols": symbols, "history": changes, "sources": sources}
    return answer


def _stored(path):
    """Whether a source path is an entity file of `kb/`."""
    return path.startswith(f"{store.TREE.as_posix()}/") and path.endswith(".toml")


def raw(graph, text, root=repo.ROOT):
    """The records of an entity: its canonical file under `kb/`, and the rows
    of the registries that state it before their conversion, `kb/names.csv`
    included. A symbol reads with its meaning, whose file holds it."""
    ref = refs.resolve(graph, text, root=root)
    if ref.kind == "location":
        raise KbError(f"{ref.text} holds no symbol", code=5)
    symbol = ref.node if ref.kind == "symbol" else None
    owner = (ref.meaning if ref.kind == "symbol" else ref.node) or {}
    sources = set(owner.get("src") or ())
    rows = {}
    if ref.kind == "entity":
        slug = owner["key"].split("/")[0]
        for path in sorted(sources):
            if not _stored(path):
                rows.update(((path, number), line)
                            for number, line in _records(root, path, slug, whole=True))
    else:
        members = [symbol] if symbol else [row["s"] for row in graph.run(
            "MATCH (:Kb:Meaning {key: $key})-[:HAS]->(s:Kb:Symbol) RETURN s", key=owner["key"])]
        for member in members:
            address = f"{member['address']:08x}"
            member_sources = set(member.get("src") or ())
            sources |= member_sources
            for path in sorted(member_sources | set(owner.get("src") or ())
                               | {names.PATH.as_posix()}):
                if not _stored(path):
                    rows.update(((path, number), line) for number, line in _records(
                        root, path, address, (member["layout"], member["kind"])))
    records = [f"  {path}:{number}: {line}" for (path, number), line in sorted(rows.items())]
    files = {path: (root / path).read_text(encoding="utf-8")
             for path in sorted(sources) if _stored(path) and (root / path).is_file()}
    answer = Answer(f"kb raw {ref.text} --budget <tokens>")
    answer.section(None, IDENTITY, [ref.text])
    for path, content in files.items():
        answer.section(f"--- {path}", FACTS, content.rstrip("\n").split("\n"))
    answer.section("--- registry rows" if files else None, DETAIL,
                   records or ([] if files else ["  no file or registry row states it"]))
    answer.data = {"ref": ref.text, "files": files, "records": records}
    return answer


def _records(root, path, address, key=None, whole=False):
    """(line number, line) of the rows of a registry that state an address, or
    with `whole` a slug as a whole word, after the header of a CSV file; a row
    of `kb/names.csv` states the layout and the kind of `key` too."""
    file = root / path
    if not file.is_file():
        return []
    lines = file.read_text(encoding="utf-8").splitlines()
    out = []
    if path.endswith(".csv"):
        numbered = [(number, line) for number, line in enumerate(lines, 1)
                    if not line.startswith("#")]
        for number, line in numbered[1:]:
            row = next(csv.reader([line]), [])
            cells = {cell.lower().removeprefix("0x") for cell in row}
            if address in cells and (path != names.PATH.as_posix() or tuple(row[:2]) == key):
                out.append((number, line))
        return [numbered[0], *out] if out else []
    word = re.compile(rf"(?<![\w-]){re.escape(address)}(?![\w-])")
    return [(number, line.strip()) for number, line in enumerate(lines, 1)
            if (word.search(line.lower()) if whole else address in line.lower())]
