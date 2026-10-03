"""The JK08A architecture (tools/kb/SPEC.md, sections 7.9 and 20.6).

- Each `[[stage]]` gives the `stage` entity of its `id` with `name` as
  `title`, `lane`, `summary`, and its position from 1 as `order`.
- Each `[[block]]` gives the `block` entity of its `id` with underscores for
  hyphens, `name` as `title`, `summary`, `specs`, `generic` where set, `home`
  as the layout of `rom`, and a `stage` reference. `functions` becomes the
  `block` key of each `fn` meaning, `signals` of each `ram` or `reg` meaning,
  and `maps` of each `tbl` or `axis` meaning.
- Each `[[endpoint]]` gives the `endpoint` entity of its `id` with `name` as
  `title`, `direction`, `peripheral`, `summary`, `specs`, and `block`,
  `registers`, and `functions` references.
- Each `[[chain]]` gives the `chain` entity of its `id` with `name` as
  `title`, `summary`, `quantity`, `specs`, `home`, an `output` reference,
  and its steps in order: `from`, `to`, and `via` references with `effect`,
  `sign`, `note`, and `specs`.
- A reference is an address with an optional prefix: `function`, `map`,
  `axis`, `signal`, and `register` name the `fn`, `tbl`, `axis`, `ram`, and
  `reg` symbol of the address, which must exist. Without a prefix, a block or
  endpoint list names a symbol of its kinds, which must exist, and a chain
  names the symbol of the first kind in `fn`, `tbl`, `axis`, `ram`, `reg`,
  `const` at the address, or else an implicit symbol of the kind its address
  admits. `via` names functions.
- The top-level `summary` describes the architecture view and stays with its
  generator; `[sources]` is dropped, since the compiler knows its inputs.
"""

from pathlib import Path
import re
import tomllib

from kb import vocab
from kb.model import SymbolKey

ARCHITECTURE = Path("defs/JK08A.architecture.toml")
SCHEMA_VERSION = 1
CANONICAL = "7mfk"
DOCUMENT_KEYS = frozenset({"schema_version", "rom", "summary", "sources", "stage", "block",
                           "endpoint", "chain"})
STAGE_KEYS = frozenset({"id", "name", "lane", "summary"})
BLOCK_KEYS = frozenset({"id", "name", "stage", "summary", "specs", "functions", "maps",
                        "signals", "generic"})
ENDPOINT_KEYS = frozenset({"id", "name", "direction", "block", "peripheral", "summary",
                           "registers", "functions", "specs"})
CHAIN_KEYS = frozenset({"id", "name", "summary", "quantity", "output", "specs", "step"})
STEP_KEYS = frozenset({"from", "to", "effect", "sign", "via", "note", "specs"})
REFERENCE = re.compile(r"(?:(function|map|axis|signal|register):)?([0-9a-f]{8})")
PREFIXES = {"function": "fn", "map": "tbl", "axis": "axis", "signal": "ram", "register": "reg"}
CHAIN_KINDS = ("fn", "tbl", "axis", "ram", "reg", "const")
# The kinds of the meanings that each list of a block pins to it.
BLOCK_LISTS = {"functions": ("fn",), "signals": ("ram", "reg"), "maps": ("tbl", "axis")}


def inputs(root):
    return [ARCHITECTURE.as_posix()]


def slug(identifier):
    return identifier.replace("-", "_")


def declare(b, root):
    """The architecture resolves in `relate`, when every symbol is declared."""
    b.stash[__name__] = tomllib.loads((root / ARCHITECTURE).read_text(encoding="utf-8"))


def relate(b, root):
    relate_architecture(b, b.stash.get(__name__, {}), ARCHITECTURE.as_posix())


def relate_architecture(b, document, src):
    if document.get("schema_version") != SCHEMA_VERSION:
        b.issue("schema", src, "schema_version",
                f"schema_version {document.get('schema_version')!r}; the adapter reads "
                f"{SCHEMA_VERSION}")
        return
    for name in sorted(set(document) - DOCUMENT_KEYS):
        b.issue("schema", src, name, "unknown key")
    if document.get("rom") not in b.layouts[CANONICAL].images:
        b.issue("schema", src, "rom", f"{document.get('rom')!r} is no image of {CANONICAL}")
        return
    stages = set()
    for order, item in enumerate(document.get("stage", ()), start=1):
        if _keys(b, src, "stage", item, STAGE_KEYS, STAGE_KEYS):
            stages.add(slug(item["id"]))
            b.entity("stage", slug(item["id"]), src, props={
                "title": item["name"], "lane": item["lane"], "summary": item["summary"],
                "order": order})
    blocks = set()
    for order, item in enumerate(document.get("block", ()), start=1):
        if not _keys(b, src, "block", item, BLOCK_KEYS,
                     {"id", "name", "stage", "summary", "functions"}):
            continue
        name = slug(item["id"])
        subject = f"block.{item['id']}"
        blocks.add(name)
        refs = {}
        if slug(item["stage"]) in stages:
            refs["stage"] = [("stage", slug(item["stage"]))]
        else:
            b.issue("references", src, subject, f"stage {item['stage']!r} is no stage")
        b.entity("block", name, src, props={
            "title": item["name"], "summary": item["summary"], "specs": item.get("specs"),
            "generic": item.get("generic") or None, "home": CANONICAL,
            "order": order}, refs=refs)
        for field, kinds in BLOCK_LISTS.items():
            for text in item.get(field, ()):
                key = _listed(b, src, f"{subject}.{field}", text, kinds)
                if key is not None:
                    b.props(key, {"block": f"{name}/block"}, src)
    for order, item in enumerate(document.get("endpoint", ()), start=1):
        if not _keys(b, src, "endpoint", item, ENDPOINT_KEYS,
                     {"id", "name", "direction", "block", "peripheral", "summary"}):
            continue
        subject = f"endpoint.{item['id']}"
        refs = {field: [key for text in item.get(field, ())
                        if (key := _listed(b, src, f"{subject}.{field}", text, kinds))]
                for field, kinds in (("registers", ("reg", "ram")), ("functions", ("fn",)))}
        if slug(item["block"]) in blocks:
            refs["block"] = [("block", slug(item["block"]))]
        else:
            b.issue("references", src, subject, f"block {item['block']!r} is no block")
        b.entity("endpoint", slug(item["id"]), src, props={
            "title": item["name"], "direction": item["direction"],
            "peripheral": item["peripheral"], "summary": item["summary"],
            "specs": item.get("specs"), "order": order},
            refs={name: keys for name, keys in refs.items() if keys})
    for order, item in enumerate(document.get("chain", ()), start=1):
        if _keys(b, src, "chain", item, CHAIN_KEYS, CHAIN_KEYS - {"specs"}):
            _chain(b, src, item, order)


def _keys(b, src, kind, item, known, required):
    subject = f"{kind}.{item.get('id', '?')}"
    unknown, missing = sorted(set(item) - known), sorted(required - set(item))
    if unknown or missing:
        b.issue("schema", src, subject, f"missing {missing}; unknown {unknown}")
        return False
    if (kind, slug(item["id"])) in b.entities:
        b.issue("schema", src, subject, f"a second {kind} of the id")
        return False
    return True


def _chain(b, src, item, order=1):
    name = slug(item["id"])
    subject = f"chain.{item['id']}"
    output = _reference(b, src, f"{subject}.output", item["output"], CHAIN_KINDS)
    entity = b.entity("chain", name, src, props={
        "title": item["name"], "summary": item["summary"], "quantity": item["quantity"],
        "specs": item.get("specs"), "home": CANONICAL, "order": order},
        refs={"output": [output]} if output else None)
    for order, step in enumerate(item["step"], start=1):
        where = f"{subject}.step.{order}"
        unknown = sorted(set(step) - STEP_KEYS)
        missing = sorted({"from", "to", "effect", "sign"} - set(step))
        if unknown or missing:
            b.issue("schema", src, where, f"missing {missing}; unknown {unknown}")
            continue
        for field, allowed in (("effect", vocab.STEP_EFFECTS), ("sign", vocab.STEP_SIGNS)):
            if step[field] not in allowed:
                b.issue("schema", src, where, f"{field} {step[field]!r}")
        ends = [_reference(b, src, f"{where}.{field}", step[field], CHAIN_KINDS)
                for field in ("from", "to")]
        via = [_reference(b, src, f"{where}.via", text, ("fn",)) for text in step.get("via", ())]
        if None in ends or None in via:
            continue
        entity.steps.append({"from": ends[0], "to": ends[1], "effect": step["effect"],
                             "sign": step["sign"], "via": via, "note": step.get("note"),
                             "specs": step.get("specs")})


def _parse(b, src, subject, text):
    match = REFERENCE.fullmatch(text if isinstance(text, str) else "")
    if match is None:
        b.issue("schema", src, subject, f"reference {text!r}")
        return None, None
    return match[1], int(match[2], 16)


def _prefixed(b, src, subject, text, prefix, address, kinds):
    kind = PREFIXES[prefix]
    if kind not in kinds:
        b.issue("references", src, subject, f"{text} names a {kind}; the list holds "
                f"{'/'.join(kinds)}")
        return None
    if SymbolKey(CANONICAL, kind, address) not in b.at(CANONICAL, address):
        b.issue("references", src, subject, f"no {kind} symbol of {CANONICAL} at {address:08x}")
        return None
    return b.symbol(CANONICAL, kind, address, src)


def _listed(b, src, subject, text, kinds):
    """The declared symbol that an entry of a block or endpoint list names."""
    prefix, address = _parse(b, src, subject, text)
    if address is None:
        return None
    if prefix:
        return _prefixed(b, src, subject, text, prefix, address, kinds)
    present = {key.kind for key in b.at(CANONICAL, address)}
    kind = next((kind for kind in kinds if kind in present), None)
    if kind is None:
        b.issue("references", src, subject, f"no {' or '.join(kinds)} symbol of {CANONICAL} "
                f"at {address:08x}")
        return None
    return b.symbol(CANONICAL, kind, address, src)


def _reference(b, src, subject, text, kinds):
    """The symbol that a chain names, implicit where no registry declares it."""
    prefix, address = _parse(b, src, subject, text)
    if address is None:
        return None
    if prefix:
        return _prefixed(b, src, subject, text, prefix, address, kinds)
    key = b.resolve(CANONICAL, address, kinds, src)
    if key is None:
        b.issue("references", src, subject, f"{address:08x} admits no {'/'.join(kinds)} "
                f"symbol of {CANONICAL}")
    return key
