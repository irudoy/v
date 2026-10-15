"""The graph of the model (tools/kb/SPEC.md, sections 9 and 10).

`sync` compiles the inputs and loads the instance of the working tree. Every
node the compiler writes carries the label `Kb`, and the loader deletes and
replaces only `Kb` elements, so the graph of the legacy loaders stays intact.

- The L0 part of a layout, its functions, calls, locations, and accesses,
  reloads when its L0 files, its images, the address spaces of its MCU, or the
  modules that build its rows change.
- The claim part, the meanings and symbols with their links, statuses, and
  citations, reloads as a whole when the fingerprint changes.
- `AT` joins symbols to the L0 nodes at their addresses, and the loader
  verifies the writer and reader links of symbols against the accesses.
- `:Meta` is deleted first and written last, so a graph without it is stale.
"""

from collections import defaultdict
from datetime import datetime, timezone
import re
import time

import kb
from kb import compatibility_state, compile, fingerprint, instance, l0graph, lock, names, repo, retirement
from kb.model import SymbolKey
from kb.values import properties

BATCH = 5000
LABELS = ("Meta", "Family", "Layout", "Image", "Meaning", "Symbol", "Entity", "Step", "Retired",
          "Function", "Location", "Candidate", compatibility_state.LABEL)
INDEXES = (
    ("Symbol", ("layout", "address")),
    ("Symbol", ("name",)),
    ("Meaning", ("name",)),
    ("Location", ("layout", "address")),
    ("Function", ("layout", "address")),
    ("Function", ("layout",)),
    ("Location", ("layout",)),
)
CLAIM_LABELS = ("Meaning", "Symbol", "Entity", "Step", "Retired")
STORE_MODES = ("store", "update", "write", "read_write")
LOAD_MODES = ("load", "update", "read", "read_write", "literal", "data", "param")
L0_VERIFIED = {"WRITER": STORE_MODES, "READER": LOAD_MODES}
# Modules whose change reloads the L0 part of every layout.
L0_CODE = ("derive.py", "l0graph.py", "sh2.py", "values.py")
# Clauses and commands that change a graph; `kb cypher` refuses them.
WRITES = re.compile(
    r"(?<![.$:\w])(CREATE|MERGE|DELETE|DETACH|SET|REMOVE|DROP|FOREACH|LOAD\s+\w+|"
    r"FREE\s+MEMORY|STORAGE\s+MODE|ANALYZE\s+GRAPH|(?:UN)?LOCK\s+DATA|GRANT|REVOKE|DENY|"
    r"BEGIN|COMMIT|ROLLBACK)\b(?!\s*:)",
    re.IGNORECASE)
LITERALS = re.compile(r"'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"|`[^`]*`|//[^\n]*|/\*.*?\*/",
                      re.DOTALL)
PROCEDURE_CODE = re.compile(r"'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"|//[^\n]*|/\*.*?\*/",
                            re.DOTALL)
CALL_TOKEN = re.compile(r"`(?:``|[^`])*`|\bCALL\b", re.IGNORECASE)
PROCEDURE_NAME = re.compile(
    r"CALL\s+((?:[A-Za-z_]\w*|`(?:``|[^`])+`)(?:\s*\.\s*(?:[A-Za-z_]\w*|`(?:``|[^`])+`))*)",
    re.IGNORECASE)


class Graph:
    """A session factory over the working tree's instance."""

    def __init__(self, root=repo.ROOT):
        from neo4j import GraphDatabase
        from neo4j.exceptions import DriverError

        self.uri = instance.uri(root)
        self.driver = None
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=("", ""))
            self.driver.verify_connectivity()
        except (DriverError, OSError) as error:
            if self.driver is not None:
                self.driver.close()
            raise repo.KbError(f"no graph answers at {self.uri} ({error}); "
                               "start it with `uv run kb instance up`", code=6) from None

    def run(self, query, **params):
        with self.driver.session() as session:
            return [record.data() for record in session.run(query, params)]

    def rows(self, query, rows, **params):
        """Run a query over `$rows` in batches; return the summed `count`."""
        total = 0
        for start in range(0, len(rows), BATCH):
            found = self.run(query, rows=rows[start:start + BATCH], **params)
            total += sum(record.get("count", 0) for record in found)
        return total

    def drain(self, match):
        """DETACH DELETE the nodes of a MATCH clause in batches."""
        total = 0
        while True:
            [record] = self.run(f"{match} WITH n LIMIT {BATCH} DETACH DELETE n "
                                "RETURN count(*) AS count")
            total += record["count"]
            if record["count"] < BATCH:
                return total

    def close(self):
        self.driver.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


# Claims --------------------------------------------------------------------------

def _families(root):
    import tomllib

    document = tomllib.loads((root / repo.HOMOLOGY).read_text(encoding="utf-8"))
    return document["family"]


def structure_rows(model, root=repo.ROOT):
    """Family, Layout, and Image nodes with their IN relationships."""
    families = _families(root)
    catalog = repo.images(root)
    homology = repo.HOMOLOGY.as_posix()
    nodes = {"Family": [], "Layout": [], "Image": []}
    links = []
    for family in sorted({layout.family for layout in model.layouts.values()}):
        row = families[family]
        nodes["Family"].append({"key": family, "kind": row["kind"], "mcu": row["mcu"],
                                "producer": "claim", "src": homology})
    for layout in model.layouts.values():
        manifest = root / repo.L0 / layout.id / "manifest.toml"
        nodes["Layout"].append({"key": layout.id, "family": layout.family,
                                "l0": repo.sha256_file(manifest), "producer": "claim",
                                "src": homology})
        links.append(("Layout", layout.id, "Family", layout.family))
        for image in layout.images:
            links.append(("Image", image, "Layout", layout.id))
    for image in sorted(catalog.values(), key=lambda item: item.rom):
        nodes["Image"].append({"key": image.rom, "sha256": image.sha256, "producer": "claim",
                               "src": repo.CATALOG.as_posix()})
    return nodes, links


def _src(sources):
    return sorted(sources) or ["model"]


def meaning_node(model, meaning):
    """The Meaning node; `former` holds the names that other registries give the
    meaning, which its conversion records as former names, and a reference in a
    key names the meaning of its symbol."""
    props = {**_referenced(model, meaning.props), **meaning.tables}
    for reserved in ("key", "kind", "name", "former", "producer", "src"):
        props.pop(reserved, None)
    return properties({
        **props, "key": meaning.key, "kind": meaning.kind, "name": meaning.name,
        "semantic": meaning.semantic, "tier": meaning.tier, "home": meaning.home,
        "former": sorted({name for name, _, _ in meaning.other_names}),
        "producer": "claim", "src": _src(meaning.sources)})


def symbol_node(model, symbol):
    """The Symbol node; `name` is the name of its full reference, the semantic
    name of its meaning or its generated name, and a generated name that a
    semantic name supersedes joins `former`."""
    props = _referenced(model, symbol.props)
    for reserved in ("key", "kind", "name", "layout", "address", "producer", "src"):
        props.pop(reserved, None)
    former = list(symbol.former)
    if symbol.generated and symbol.generated != symbol.name:
        former.append(symbol.generated)
    return properties({
        **props, "key": symbol.key.key, "kind": symbol.kind, "layout": symbol.layout,
        "address": symbol.address, "name": symbol.name, "generated": symbol.generated,
        "implicit": symbol.implicit, "former": former, "evidence": symbol.evidence,
        "producer": "claim", "src": _src(symbol.sources)})


def entity_node(entity):
    props = dict(entity.props)
    for reserved in ("key", "kind", "slug", "producer", "src"):
        props.pop(reserved, None)
    return properties({**props, "key": entity.key, "kind": entity.kind, "slug": entity.slug,
                       "producer": "claim", "src": _src(entity.sources)})


def _referenced(model, item):
    """A value with each symbol key replaced by the key of its meaning."""
    if isinstance(item, SymbolKey):
        meaning = model.meaning_of(item)
        return meaning.key if meaning is not None and meaning.name else item.key
    if isinstance(item, dict):
        return {key: _referenced(model, entry) for key, entry in item.items()}
    if isinstance(item, (list, tuple)):
        return [_referenced(model, entry) for entry in item]
    return item


# Relationships of designed entities: the reference key that states each, and
# the label of the node it reaches.
# A reference key whose relationships reach both labels lists them.
ENTITY_LINKS = {"observes": ("OBSERVES", "Meaning"), "source": ("CARRIES", "Meaning"),
                "signal": ("SERVES", "Entity"), "stage": ("STAGE", "Entity"),
                "block": ("BLOCK", "Entity"), "registers": ("REGISTER", "Meaning"),
                "functions": ("FUNCTION", "Meaning"), "output": ("OUTPUT", "Meaning"),
                "requires": ("REQUIRES", ("Meaning", "Entity"))}
# The relationships of a chain step to the meanings of its keys.
STEP_LINKS = (("from", "FROM"), ("to", "TO"), ("via", "THROUGH"))


def _family_of(model):
    return {layout.id: layout.family for layout in model.layouts.values()}


def claim_rows(model):
    """Meaning, Symbol, Entity, and Step nodes, HAS, the links between meanings
    and their materialization between symbols, statuses, citations, the
    relationships of designed entities, of chain steps, and of blocks to their
    meanings, and the targets of features."""
    family = _family_of(model)
    meanings, symbols, has = [], [], []
    links = defaultdict(list)
    symbol_links = defaultdict(list)
    statuses, analogs, cites = [], [], defaultdict(list)
    entity_links = defaultdict(list)
    for meaning in model.meanings:
        if not meaning.name:
            continue
        meanings.append(meaning_node(model, meaning))
        for item in meaning.tables.get('analog', ()):
            analogs.append({'from': meaning.key, 'to': item['to'], 'props': {
                'note': item['note'], 'producer': 'claim', 'src': _src(meaning.sources)}})
        block = meaning.props.get("block")
        if block:
            entity_links[("BLOCK", "Meaning", "Entity")].append(
                {"from": meaning.key, "to": block,
                 "props": {"producer": "claim", "src": _src(meaning.sources)}})
        for layout, symbol in sorted(meaning.symbols.items()):
            symbols.append(symbol_node(model, symbol))
            has.append({"from": meaning.key, "to": symbol.key.key})
            for item in symbol.evidence:
                if isinstance(item.get("to"), SymbolKey):
                    cites[("Symbol", "Symbol")].append({
                        "from": symbol.key.key, "to": item["to"].key,
                        "props": properties({"kind": item["kind"], "supports": item.get("supports"),
                                             "relies": item.get("relies"), "producer": "claim",
                                             "src": _src(symbol.sources)})})
        for binding in meaning.tables.get("diagnostic", ()):
            for item in binding.get("evidence", ()):
                if isinstance(item.get("to"), SymbolKey):
                    cites[("Meaning", "Symbol")].append({
                        "from": meaning.key, "to": item["to"].key,
                        "props": properties({"kind": item["kind"], "supports": item.get("supports"),
                                             "relies": item.get("relies"),
                                             "binding": binding.get("id"),
                                             "producer": "claim", "src": _src(meaning.sources)})})
        for layout, status in sorted(meaning.statuses.items()):
            statuses.append({"from": meaning.key, "to": layout, "props": properties({
                **status.props, "state": status.state, "evidence": status.evidence,
                "producer": "claim", "src": _src(status.sources)})})
    by_key = {meaning.key: meaning for meaning in model.meanings if meaning.name}
    for (key, layout), requirements in sorted(model.required().items()):
        if layout not in by_key[key].statuses:
            statuses.append({"from": key, "to": layout, "props": {
                "state": "unknown", "required": sorted(requirements),
                "producer": "derived", "src": "required-meanings"}})
    for link in model.links:
        if not (link.owner.name and link.to.name):
            continue
        kind = link.type.upper()
        links[kind].append({"from": link.owner.key, "to": link.to.key, "props": properties({
            **link.props, "slot": link.slot, "offset": link.offset, "role": link.roles,
            "evidence": link.evidence, "stated": link.stated,
            "producer": "claim", "src": _src(link.sources)})})
        allowed = link.props.get("layouts")
        for layout in sorted(set(link.owner.symbols) & set(link.to.symbols)):
            if allowed and layout not in allowed:
                continue
            siblings = {other for other in link.stated if family[other] == family[layout]}
            from kb import copy_evidence
            proof = copy_evidence.accepted(model, link.owner.symbols[layout],
                link.to.symbols[layout], copy_evidence.claim_fields(link, layout))
            symbol_links[kind].append({
                "from": link.owner.symbols[layout].key.key,
                "to": link.to.symbols[layout].key.key,
                "props": properties({
                    "layout": layout, "role": link.roles, "slot": link.slot,
                    "offset": link.offset,
                    "verified": bool(proof) or kind not in L0_VERIFIED and bool(siblings),
                    "copy_proof": proof['proof'] if proof else None,
                    "copy_callsite": proof['callsite'] if proof else None,
                    "verification_scope": proof['scope'] if proof else None,
                    "producer": "derived", "src": "links"})})
    entities, steps = [], []
    for _, entity in sorted(model.entities.items()):
        entities.append(entity_node(entity))
        claim = {"producer": "claim", "src": _src(entity.sources)}
        for name, (kind, labels) in ENTITY_LINKS.items():
            refs = entity.refs.get(name, ())
            for label in (labels,) if isinstance(labels, str) else labels:
                # An entity reference is a (kind, slug) tuple; any other
                # reference is a symbol key of a meaning.
                if label == "Meaning":
                    keys = sorted(_named_keys(model, [
                        ref for ref in refs if not isinstance(ref, tuple)]))
                else:
                    keys = sorted(model.entities[ref].key for ref in refs
                                  if isinstance(ref, tuple) and ref in model.entities)
                entity_links[(kind, "Entity", label)].extend(
                    {"from": entity.key, "to": key, "props": claim} for key in keys)
        for order, step in enumerate(entity.steps, start=1):
            key = f"{entity.slug}#{order}"
            steps.append(properties({
                "key": key, "effect": step["effect"], "sign": step["sign"],
                "note": step.get("note"), "specs": step.get("specs"), **claim}))
            if 'research' in step:
                steps[-1].update(properties({'research': step['research']}))
            entity_links[("STEP", "Entity", "Step")].append(
                {"from": entity.key, "to": key, "props": {"order": order, **claim}})
            for name, kind in STEP_LINKS:
                refs = step[name] if isinstance(step[name], list) else [step[name]]
                for index, reference in enumerate(refs, start=1):
                    meaning = model.meaning_of(reference)
                    if meaning is not None and meaning.name:
                        entity_links[(kind, 'Step', 'Meaning')].append({
                            'from': key, 'to': meaning.key,
                            'props': {**claim, **({'order': index} if name == 'via' else {})}})
    targets, required = [], defaultdict(lambda: (set(), set()))
    for (feature, layout), target in sorted(model.targets.items()):
        props = {key: value for key, value in target.props.items() if key != "requires"}
        targets.append({"from": f"{feature}/feature", "to": layout, "props": properties({
            **_referenced(model, props), "status": target.status,
            "producer": "claim", "src": _src(target.sources)})})
        for key in _named_keys(model, target.needs()):
            layouts, sources = required[(feature, key)]
            layouts.add(layout)
            sources.update(target.sources)
    # The meanings that the targets of a feature require: REQUIRES with the
    # layouts of those targets.
    for (feature, key), (layouts, sources) in sorted(required.items()):
        entity_links[("REQUIRES", "Entity", "Meaning")].append({
            "from": f"{feature}/feature", "to": key, "props": {
                "layouts": sorted(layouts), "producer": "claim", "src": _src(sources)}})
    return {"meanings": meanings, "symbols": symbols, "has": has, "links": dict(links),
            "symbol_links": dict(symbol_links), "statuses": statuses, "cites": dict(cites),
            "entities": entities, "steps": steps, "entity_links": dict(entity_links),
            "targets": targets, 'analogs': analogs}


def _named_keys(model, refs):
    """The keys of the named meanings of symbol keys, in their order, once each."""
    found = []
    for ref in refs:
        meaning = model.meaning_of(ref)
        if meaning is not None and meaning.name and meaning.key not in found:
            found.append(meaning.key)
    return found


def at_rows(model):
    rows = {"Function": [], "Location": []}
    for key in model.symbols:
        symbol = model.symbols[key]
        if symbol.meaning is None or not symbol.meaning.name:
            continue
        label = "Function" if key.kind == "fn" else "Location"
        rows[label].append({"from": key.key, "to": key.location})
    return rows


# Loading ---------------------------------------------------------------------------

def ensure_schema(graph):
    constraints = {(row["label"], tuple(_listed(row["properties"])))
                   for row in graph.run("SHOW CONSTRAINT INFO")}
    indexes = {(row["label"], tuple(_listed(row["property"])))
               for row in graph.run("SHOW INDEX INFO") if row.get("label")}
    if "Kb" not in {row["label"] for row in graph.run("SHOW INDEX INFO")
                    if row.get("property") in (None, [])}:
        graph.run("CREATE INDEX ON :Kb")
    for label in LABELS:
        if (label, ("key",)) not in constraints:
            graph.run(f"CREATE CONSTRAINT ON (n:{label}) ASSERT n.key IS UNIQUE")
        if (label, ("key",)) not in indexes:
            graph.run(f"CREATE INDEX ON :{label}(key)")
    for label, props in INDEXES:
        if (label, props) not in indexes:
            graph.run(f"CREATE INDEX ON :{label}({', '.join(props)})")


def _listed(item):
    if item is None:
        return []
    return item if isinstance(item, list) else [item]


def meta(graph):
    found = graph.run("MATCH (m:Kb:Meta {key: 'meta'}) RETURN m")
    return dict(found[0]["m"]) if found else None


def stale(current, fp):
    return (current is None or current.get("fingerprint") != fp.value
            or current.get("schema") != compile.SCHEMA)


def proof_stale(current, root=repo.ROOT):
    from kb import copy_evidence
    return current is None or current.get('copy_proof_state') != copy_evidence.proof_state(root)


def _create_nodes(graph, label, rows):
    return graph.rows(f"UNWIND $rows AS row CREATE (n:Kb:{label}) SET n = row "
                      "RETURN count(n) AS count", rows)


def _create_links(graph, kind, left, right, rows):
    if not re.fullmatch(r"[A-Z_]+", kind):
        raise repo.KbError(f"relationship type {kind!r}")
    return graph.rows(
        f"UNWIND $rows AS row MATCH (a:{left} {{key: row.from}}) "
        f"MATCH (b:{right} {{key: row.to}}) CREATE (a)-[r:{kind}]->(b) "
        "SET r = coalesce(row.props, {}) RETURN count(r) AS count", rows)


def l0_part(fp, layout, images, spaces):
    """The digest of one layout's L0 part: its L0 files, its images, the address
    spaces of its MCU, and the modules that build its rows."""
    prefix = f"{repo.L0.as_posix()}/{layout}/"
    code = {f"{compile.PACKAGE}/{name}" for name in L0_CODE}
    files = fp.part(lambda path: path.startswith(prefix) or path in images or path in code)
    bounds = ",".join(f"{name}={start:x}:{end:x}" for name, (start, end) in sorted(spaces.items()))
    return fingerprint.digest([("files", files), ("spaces", bounds)])


def load(graph, model, fp, root=repo.ROOT, full=False, log=print):
    """Load the model into the graph; return a summary per part."""
    from kb import copy_evidence
    with copy_evidence.consuming(root):
        return _load(graph, model, fp, root, full, log)


def _load(graph, model, fp, root, full, log):
    ensure_schema(graph)
    previous = meta(graph)
    from kb import copy_evidence
    proof_before = copy_evidence.proof_state(root)
    graph.run("MATCH (m:Kb:Meta) DELETE m")
    if full:
        graph.drain("MATCH (n:Kb)")
    nodes, structure_links = structure_rows(model, root)
    loaded = {row["key"]: row["loaded"] for row in
              graph.run("MATCH (l:Kb:Layout) RETURN l.key AS key, l.loaded AS loaded")}
    gone = sorted(set(loaded) - set(model.layouts))
    for layout in gone:
        graph.drain(f"MATCH (n:Kb) WHERE (n:Function OR n:Location) AND n.layout = '{layout}'")
    for label in ("Family", "Image", "Layout"):
        graph.run(f"MATCH (n:Kb:{label}) WHERE NOT n.key IN $keys DETACH DELETE n",
                  keys=[row["key"] for row in nodes[label]])
        graph.rows(f"UNWIND $rows AS row MERGE (n:Kb:{label} {{key: row.key}}) "
                   "SET n += row RETURN count(n) AS count", nodes[label])
    graph.run("MATCH (:Kb)-[r:IN]->(:Kb) DELETE r")
    for left, right in (("Layout", "Family"), ("Image", "Layout")):
        rows = [{"from": a, "to": b, "props": {"producer": "claim", "src": repo.HOMOLOGY.as_posix()}}
                for kind_a, a, kind_b, b in structure_links if (kind_a, kind_b) == (left, right)]
        _create_links(graph, "IN", left, right, rows)
    summary = {}
    catalog = repo.images(root)
    changed = False
    for layout in model.layouts.values():
        images = {catalog[image].path.relative_to(root).as_posix() for image in layout.images
                  if image in catalog}
        digest = l0_part(fp, layout.id, images, model.spaces[layout.mcu])
        if not full and loaded.get(layout.id) == digest:
            continue
        started = time.monotonic()
        graph.run("MATCH (l:Kb:Layout {key: $key}) SET l.loaded = null", key=layout.id)
        graph.drain(f"MATCH (n:Kb) WHERE (n:Function OR n:Location) AND n.layout = '{layout.id}'")
        rows = l0graph.l0_rows(layout, model.spaces[layout.mcu], root)
        counts = {
            "functions": _create_nodes(graph, "Function", rows["functions"]),
            "locations": _create_nodes(graph, "Location", rows["locations"]),
            "calls": _create_links(graph, "CALL", "Function", "Function", rows["calls"]),
            "accesses": _create_links(graph, "ACCESS", "Function", "Location", rows["accesses"]),
            "shared RAM": _create_links(graph, "SHARED_RAM", "Function", "Function",
                                        rows["shared_ram"]),
        }
        graph.run("MATCH (l:Kb:Layout {key: $key}) SET l.loaded = $digest",
                  key=layout.id, digest=digest)
        summary[f"l0 {layout.id}"] = (counts, time.monotonic() - started, rows["outside"])
        changed = True
    if (full or previous is None or previous.get("fingerprint") != fp.value
            or previous.get('copy_proof_state') != proof_before):
        started = time.monotonic()
        for label in CLAIM_LABELS:
            graph.drain(f"MATCH (n:Kb:{label})")
        rows = claim_rows(model)
        counts = {
            "meanings": _create_nodes(graph, "Meaning", rows["meanings"]),
            "symbols": _create_nodes(graph, "Symbol", rows["symbols"]),
            "has": _create_links(graph, "HAS", "Meaning", "Symbol", rows["has"]),
            "links": sum(_create_links(graph, kind, "Meaning", "Meaning", items)
                         for kind, items in rows["links"].items()),
            "symbol links": sum(_create_links(graph, kind, "Symbol", "Symbol", items)
                                for kind, items in rows["symbol_links"].items()),
            "statuses": _create_links(graph, "STATUS", "Meaning", "Layout", rows["statuses"]),
            'analogs': _create_links(graph, 'ANALOG', 'Meaning', 'Meaning', rows['analogs']),
            "citations": sum(_create_links(graph, "CITES", left, right, items)
                             for (left, right), items in rows["cites"].items()),
            "entities": _create_nodes(graph, "Entity", rows["entities"]),
            "steps": _create_nodes(graph, "Step", rows["steps"]),
            'retired': _create_nodes(graph, 'Retired', retirement.nodes(model)),
            "entity links": sum(_create_links(graph, kind, left, right, items)
                                for (kind, left, right), items in rows["entity_links"].items()),
            "targets": _create_links(graph, "TARGETS", "Entity", "Layout", rows["targets"]),
        }
        summary["claims"] = (counts, time.monotonic() - started, {})
        changed = True
    if changed:
        graph.run("MATCH (:Kb:Symbol)-[r:AT]->() DELETE r")
        found = at_rows(model)
        at = sum(_create_links(graph, "AT", "Symbol", label, rows) for label, rows in found.items())
        for kind, modes in L0_VERIFIED.items():
            graph.run(
                f"MATCH (d:Kb:Symbol)-[r:{kind}]->(g:Kb:Symbol) "
                "OPTIONAL MATCH (d)-[:AT]->(:Location)<-[a:ACCESS]-(:Function)<-[:AT]-(g) "
                "WITH r, collect(a) AS accesses "
                "SET r.verified = coalesce(r.copy_proof, '') <> '' OR "
                "any(a IN accesses WHERE any(m IN a.modes WHERE m IN $modes))",
                modes=list(modes))
        summary["at"] = ({"at": at}, 0.0, {})
    if copy_evidence.proof_state(root, live=True) != proof_before:
        raise repo.KbError('copy execution proof changes during graph construction; Meta is absent', code=6)
    return publish(graph, model, fp, root, summary,
                   full or previous is None or previous.get("fingerprint") != fp.value, log,
                   proof_before=proof_before)


def publish(graph, model, fp, root, summary, changed, log=print, *, proof_before=None):
    """Publish freshness only after every retained layer and source check passes."""
    if changed:
        from kb import compatibility
        summary.update(compatibility.load(graph, model, root, log))
    after = fingerprint.compute(root)
    if after.value != fp.value:
        raise repo.KbError("compiler inputs change during graph construction; Meta is absent", code=6)
    from kb import copy_evidence
    proof_after = copy_evidence.proof_state(root, live=True)
    if proof_before is not None and proof_after != proof_before:
        raise repo.KbError('copy execution proof changes before Meta publication', code=6)
    commit, head = fingerprint.head(root)
    graph.run("CREATE (m:Kb:Meta) SET m = $props", props={
        "key": "meta", "fingerprint": fp.value, "commit": commit,
        "copy_proof_state": proof_after,
        "dirty": bool(fingerprint.dirty(fp, head)), "compiler": kb.__version__,
        "schema": compile.SCHEMA, "worktree": str(root),
        "loaded_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "producer": "derived", "src": "compiler"})
    return summary


def sync(root=repo.ROOT, full=False, log=print):
    """Compile the inputs, complete kb/names.csv, and load the graph."""
    with lock.held(root):
        return sync_held(root, full, log)


def sync_held(root=repo.ROOT, full=False, log=print, model=None):
    """`sync` under a lock that the caller holds, loading `model` when the
    caller has compiled the working tree."""
    model = model or compile.build(root)
    added = names.enroll(model, model.names, root)
    if added:
        model.names = model.names + added
        names.write(model.names, root)
        names.assign(model, model.names)
        log(f"{names.PATH}: {len(added)} generated names")
    fp = fingerprint.compute(root)
    with Graph(root) as graph:
        summary = load(graph, model, fp, root, full, log)
        log(f"graph: {graph.uri}")
    for part, (counts, seconds, outside) in summary.items():
        text = ", ".join(f"{count} {name}" for name, count in counts.items())
        extra = "".join(f"; {count} {name} addresses outside the MCU spaces"
                        for name, count in outside.items())
        log(f"{part}: {text} ({seconds:.1f} s){extra}")
    if not summary:
        log("graph: every part is current")
    log(f"meta: fingerprint {fp.value[:16]}")
    return model, fp


def refusal(query, write_procedures=()):
    """Why `kb cypher` refuses a query, or None for a read-only one."""
    code = LITERALS.sub(" ", query)
    found = WRITES.search(code)
    if found:
        clause = " ".join(found.group(1).split()).upper()
        return f"the query writes ({clause}); kb cypher is read-only"
    writers = {name.casefold() for name in write_procedures}
    procedure_code = PROCEDURE_CODE.sub(' ', query)
    for token in CALL_TOKEN.finditer(procedure_code):
        if token.group().startswith('`'):
            continue
        matched = PROCEDURE_NAME.match(procedure_code, token.start())
        if matched is None:
            continue
        parts = re.findall(r'`((?:``|[^`])+)`|([A-Za-z_]\w*)', matched.group(1))
        name = '.'.join((quoted or bare).replace('``', '`') for quoted, bare in parts)
        if name.casefold().startswith('periodic.'):
            return f"the procedure {name} executes nested queries; kb cypher is read-only"
        if name.casefold() in writers:
            return f"the procedure {name} writes; kb cypher is read-only"
    return None


def read_query(graph, query, params=None):
    """(keys, records) of a read-only query, run in a transaction that is
    rolled back."""
    writers = {row["name"] for row in graph.run(
        "CALL mg.procedures() YIELD name, is_write WHERE is_write RETURN name")}
    reason = refusal(query, writers)
    if reason:
        raise repo.KbError(reason, code=2)
    from neo4j.exceptions import Neo4jError

    with graph.driver.session() as session:
        transaction = session.begin_transaction()
        try:
            result = transaction.run(query, params or {})
            keys = result.keys()
            records = list(result)
        except Neo4jError as error:
            raise repo.KbError(f"cypher: {error.message}", code=2) from None
        finally:
            transaction.rollback()
    return keys, records


def fresh(root=repo.ROOT, no_sync=False, log=print, held=False):
    """A Graph whose `:Meta` matches the fingerprint of the working tree,
    syncing a stale graph unless `no_sync`; `held` when the caller holds the
    lock."""
    fp = fingerprint.compute(root)
    graph = Graph(root)
    current = meta(graph)
    if not stale(current, fp) and not proof_stale(current, root):
        return graph
    graph.close()
    if no_sync:
        raise repo.KbError("the graph is stale for this working tree; run `uv run kb sync`",
                           code=6)
    if held:
        sync_held(root, log=log)
    else:
        sync(root, log=log)
    return Graph(root)
