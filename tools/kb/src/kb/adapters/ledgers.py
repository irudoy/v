"""The JK08A ledgers (tools/kb/SPEC.md, sections 7.8 and 14).

`kb.tokens` owns the token grammar. `dependency` owns the dependency-role
mapping shared by this importer and `kb.ledger_projection`.
`tools/kb/projections.toml` registers the generated ledger views.

Every row is a symbol of layout `7mfk` whose meaning takes the row's keys.
Terminal evidence tokens become evidence items of the symbol, and dependency
tokens become links stored at the end that the link type names, or `trace`
evidence. A token target without a row becomes an implicit symbol. An axis
that a call of the accessor census passes is `code` with `l0` identity
evidence at the first such call, and `candidate` otherwise.

The `units` of a `vars` row becomes `unit` unless the converted numeric
telemetry source owns its unit, including its absence, or a legacy telemetry
profile states it (`telemetry_units` of the stash).
"""

import csv
import importlib.util
import io
from pathlib import Path
import sys

from kb import derive, tokens, vocab
from kb.adapters import curated, native

DTC_DECODER = Path("tools/mapkit/dtc_projection.py")

LAYOUT = "7mfk"
PATHS = {
    name: Path(f"defs/JK08A.{name}.csv")
    for name in ("funcs", "vars", "findings", "axes", "dtc", "diagnostic-bindings")
}
DATUM = ("ram", "reg", "tbl", "axis", "const")
LEGACY_KINDS = {"Func": ("fn",), "Reg": ("ram", "reg"), "Map": ("tbl",), "Axis": ("axis",)}
UNITS = f"{__name__}.units"


def _dtc_decoder(root):
    name = "kb_dtc_projection"
    spec = importlib.util.spec_from_file_location(name, root / DTC_DECODER)
    module = importlib.util.module_from_spec(spec)
    # Dataclasses resolve their annotations through sys.modules.
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(name, None)
    return module


def inputs(root):
    return [path.as_posix()
            for path in (*PATHS.values(), curated.DIRECTORY / "7mfk.csv",
                         DTC_DECODER, _dtc_decoder(root).LAYOUTS)]


def rows(root, name, overlay=None):
    if overlay and PATHS[name] in overlay:
        yield from csv.DictReader(io.StringIO(overlay[PATHS[name]]))
        return
    with (root / PATHS[name]).open(newline="", encoding="utf-8") as source:
        yield from csv.DictReader(source)


def _address(text):
    return int(text, 16)


def _integer(text):
    return int(text) if text not in (None, "") else None


def _level(text):
    return text or None


def declare(b, root):
    curated.declare_layout(b, root, LAYOUT)
    pending = b.stash.setdefault(__name__, [])
    manual = b.config.get("tokens", {}).get("manual", ())

    def record(key, row, columns, src, *, typed=False):
        for column in columns:
            try:
                parsed = tokens.parse(row.get(column) or "")
            except tokens.TokenError as error:
                b.issue("schema", src, key.key, f"{column}: {error}")
                continue
            supports = tokens.SUPPORTS[column]
            for token in parsed:
                if token.role in tokens.DEPENDENCY:
                    b.row_tokens[(key.layout, key.address)].add((token.role, token.address))
                    pending.append((key, token, supports, src))
                    continue
                item = tokens.evidence(token, key.layout, manual)
                if item is not None:
                    item = {"kind": item.pop("kind"), "supports": supports, **item}
                    if not typed and token.role not in tokens.TYPED_TERMINAL:
                        item["legacy"] = token.text
                    b.symbol(key.layout, key.kind, key.address, src, evidence=[item])

    src = PATHS["funcs"].as_posix()
    for row in rows(root, "funcs", b.overlay):
        key = b.symbol(LAYOUT, "fn", _address(row["addr"]), src)
        b.props(key, {
            "role": row["role"],
            "summary": row["semantics"],
            "contract": row["contract"],
            "contract_level": _level(row["contract_conf"]),
            "level": _level(row["confidence"]),
            "note": row["note"],
        }, src)
        record(key, row, ("evidence", "contract_evidence"), src)

    src = PATHS["vars"].as_posix()
    units = b.stash.setdefault(UNITS, [])
    for row in rows(root, "vars", b.overlay):
        address = _address(row["addr"])
        kind = b.data_kind(LAYOUT, address)
        if kind is None:
            b.issue("symbols", src, row["addr"], "a variable outside RAM and the peripherals")
            continue
        key = b.symbol(LAYOUT, kind, address, src)
        b.props(key, {
            "summary": row["semantics"],
            "level": _level(row["confidence"]),
            "note": row["note"],
        }, src)
        units.append((key, row["units"], src))
        record(key, row, ("evidence",), src)

    src = PATHS["findings"].as_posix()
    for row in rows(root, "findings", b.overlay):
        key = b.symbol(LAYOUT, "tbl", _address(row["addr"]), src)
        b.props(key, {
            "access": row["family"] or "explicit",
            "cols": _integer(row["width"]),
            "rows": _integer(row["height"]),
            "storage": vocab.storage(row["storagetype"]),
            "role": row["role"],
            "level": _level(row["confidence"]),
            "summary": row["semantics"],
            "unit": row["units"],
            "scale": row["scale_expr"],
            "to_raw": row["to_byte"],
            "scale_level": _level(row["scale_conf"]),
            "note": row["note"],
        }, src)
        record(key, row, ("evidence", "scale_evidence"), src)
        if row["accessor"]:
            pending.append((key, "accessor", _address(row["accessor"]), src))

    src = PATHS["axes"].as_posix()
    for row in rows(root, "axes", b.overlay):
        address = _address(row["addr"])
        call = native.census_call(LAYOUT, root, {address})
        key = b.symbol(LAYOUT, "axis", address, src, evidence=[call] if call else [])
        b.props(key, {
            "quantity": row["kind"],
            "unit": row["units"],
            "scale": row["scale_expr"],
            "to_raw": row["to_byte"],
            "scale_level": _level(row["scale_conf"]),
            "level": "code" if call else "candidate",
            "note": row["note"],
        }, src)
        record(key, row, ("scale_evidence",), src)

    src = PATHS["dtc"].as_posix()
    dtc_projection = _dtc_decoder(root)
    tables = dtc_projection.canonical_tables(root)
    image_size = len(derive.image_bytes(b.layouts[LAYOUT], root))
    seen = set()
    for row in rows(root, "dtc", b.overlay):
        try:
            dtc_projection.canonical_evidence(row, tables, image_size)
            index = _integer(row["index"])
            if index in seen:
                raise dtc_projection.DtcProjectionError(f"duplicate index {index}")
            seen.add(index)
        except dtc_projection.DtcProjectionError as error:
            b.issue("schema", src, f"index {row.get('index', '')}", str(error))
            continue
        key = b.symbol(LAYOUT, "dtc", _address(row["record_addr"]), src, props={
            "index": index,
            "attribute": row["attribute_addr"],
        })
        b.props(key, {
            "code": row["dtc"],
            "group": row["group"],
            "disabled": row["disabled_attribute"],
            "level": _level(row["confidence"]),
            "title": row["note"],
        }, src)
        record(key, row, ("evidence",), src, typed=True)

    src = PATHS["diagnostic-bindings"].as_posix()
    for row in rows(root, "diagnostic-bindings", b.overlay):
        address = _address(row["firmware_addr"])
        kinds = LEGACY_KINDS.get(row["firmware_label"])
        if kinds is None:
            b.issue("schema", src, row["id"], f"firmware_label {row['firmware_label']!r}")
            continue
        kind = b.data_kind(LAYOUT, address) if kinds == ("ram", "reg") else kinds[0]
        if kind is None:
            b.issue("symbols", src, row["id"], "a binding outside RAM and the peripherals")
            continue
        key = b.symbol(LAYOUT, kind, address, src)
        binding = {
            "id": row["id"],
            "kind": row["kind"],
            "label": row["diagnostic_label"],
            "key": row["diagnostic_key"],
            "claim": {"label": row["source_claim_label"], "id": row["source_claim_id"]},
            "applicability": row["applicability"],
            "scope": row["rom_scope"],
            "priority": _integer(row["priority"]),
            "level": _level(row["confidence"]),
            "note": row["note"],
            "evidence": [],
        }
        try:
            parsed = tokens.parse(row["evidence"])
        except tokens.TokenError as error:
            b.issue("schema", src, row["id"], f"evidence: {error}")
            parsed = []
        for token in parsed:
            if token.role in tokens.DEPENDENCY:
                pending.append((key, ("diagnostic", binding), token, src))
                continue
            item = tokens.evidence(token, LAYOUT, manual)
            if item is not None:
                if token.role not in tokens.TYPED_TERMINAL:
                    item["legacy"] = token.text
                binding["evidence"].append(item)
        b.table(key, "diagnostic", binding, src)


def relate(b, root):
    scaled = b.stash.get("telemetry_units", ())
    for key, unit, src in b.stash.get(UNITS, ()):
        if key not in scaled:
            b.props(key, {"unit": unit}, src)
    for entry in b.stash.get(__name__, ()):
        if entry[1] == "accessor":
            key, _, address, src = entry
            to = b.resolve(key.layout, address, ("fn",), src)
            if to is None:
                b.issue("references", src, key.key, f"accessor {address:08x} is no function entry")
            else:
                b.link(key, "reader", to, src, props={"role": "accessor"})
            continue
        if isinstance(entry[1], tuple):
            key, (_, binding), token, src = entry
            to = b.resolve(key.layout, token.address, tokens.TARGET_KINDS[token.role], src)
            if to is None:
                b.issue("references", src, binding["id"], f"{token.text}: no symbol")
                continue
            binding["evidence"].append({"kind": "trace", "to": to, "relies": token.relies,
                                        "note": token.role, "legacy": token.text})
            continue
        key, token, supports, src = entry
        relate_token(b, key, token, supports, src)


def relate_token(b, row, token, supports, src):
    """Resolve a ledger token and apply `dependency` or trace evidence."""
    role = token.role
    to = b.resolve(row.layout, token.address, tokens.TARGET_KINDS[role], src)
    if to is None:
        b.issue("references", src, row.key,
                f"{token.text}: no symbol of kind {'/'.join(tokens.TARGET_KINDS[role])} "
                f"at {row.layout}:{token.address:08x}")
        return
    if role == "trace":
        b.symbol(row.layout, row.kind, row.address, src, evidence=[
            {"kind": "trace", "supports": supports, "to": to, "relies": token.relies,
             "legacy": token.text}])
        return
    owner, type_, target, stated, props = dependency(row, to, token, supports, b.row_tokens)
    b.link(owner, type_, target, src, props=props, stated=stated)


def dependency(row, to, token, supports, row_tokens):
    """The canonical link and claiming end selected by one legacy token.

    This function owns the dependency-role mapping for legacy import and
    `kb.ledger_projection` validation of selected ledger claims.
    """
    props = {"relies": token.relies, "supports": supports}

    def link(owner, type_, target, stated="owner", **extra):
        return owner, type_, target, stated, {**props, **extra}

    role, rk, tk = token.role, row.kind, to.kind
    if role == "writes" and rk in ("ram", "reg") and tk == "fn":
        return link(row, "writer", to)
    elif role == "writes" and rk == "fn" and tk in ("ram", "reg"):
        return link(to, "writer", row, stated="to")
    elif role == "writes" and rk in ("tbl", "axis") and tk in ("ram", "reg"):
        return link(to, "lookup", row, stated="to")
    elif role == "consumer" and rk in DATUM and tk == "fn":
        return link(row, "reader", to)
    elif role == "indexed_by" and rk in ("tbl", "axis") and tk in ("ram", "reg"):
        return link(row, "index", to)
    elif role == "indexed_by" and rk in ("ram", "reg") and tk in DATUM:
        return link(row, "input", to)
    elif role == "indexed_by" and rk == "fn" and tk in ("ram", "reg"):
        return link(to, "reader", row, stated="to", role="indexed_by")
    elif role == "from_map" and rk in ("ram", "reg") and tk in ("tbl", "axis"):
        table_tokens = row_tokens.get((to.layout, to.address), set())
        if ("indexed_by", row.address) in table_tokens:
            return link(to, "index", row, stated="to")
        elif ("writes", row.address) in table_tokens:
            return link(row, "lookup", to)
        else:
            return link(row, "input", to)
    elif role == "from_map" and rk == "fn" and tk in ("tbl", "axis"):
        return link(to, "reader", row, stated="to")
    elif role == "selector" and tk in DATUM:
        return link(row, "selector", to)
    elif role == "threshold" and tk in vocab.LINK_TYPES["threshold"][1]:
        return link(row, "threshold", to)
    elif role == "base" and rk == "ram" and tk == "ram":
        return link(row, "base", to, offset=token.offset or 0)
    else:
        return link(row, "depends", to, role=role)
