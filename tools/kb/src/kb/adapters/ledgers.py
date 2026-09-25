"""The JK08A ledgers (tools/kb/SPEC.md, sections 20.2 and 20.7).

Every row is a symbol of layout `7mfk` whose meaning takes the row's keys.
Terminal evidence tokens become evidence items of the symbol, and dependency
tokens become links stored at the end that the link type names, or `trace`
evidence. A token target without a row becomes an implicit symbol.

The `units` of a `vars` row becomes `unit` unless the telemetry profile states
the unit of the symbol's meaning, which the scale of its field does
(`telemetry_units` of the stash).
"""

import csv
from pathlib import Path

from kb import tokens, vocab

LAYOUT = "7mfk"
PATHS = {
    name: Path(f"defs/JK08A.{name}.csv")
    for name in ("funcs", "vars", "findings", "axes", "dtc", "diagnostic-bindings")
}
DATUM = ("ram", "reg", "tbl", "axis", "const")
LEGACY_KINDS = {"Func": ("fn",), "Reg": ("ram", "reg"), "Map": ("tbl",), "Axis": ("axis",)}
CENSUS_OPERANDS = ("bt_r4", "bt_r5", "bt_r6", "df_r4", "df_r5", "df_r6", "df_r7")
UNITS = f"{__name__}.units"


def inputs(root):
    return [path.as_posix() for path in PATHS.values()]


def rows(root, name):
    with (root / PATHS[name]).open(newline="", encoding="utf-8") as source:
        yield from csv.DictReader(source)


def _address(text):
    return int(text, 16)


def _integer(text):
    return int(text) if text not in (None, "") else None


def _level(text):
    return text or None


def census_operands(root, layout):
    """Addresses that a census call of the layout passes as an operand."""
    found = set()
    base = root / "l0" / layout
    for path in sorted(base.glob("accessors.*.csv")):
        with path.open(newline="", encoding="utf-8") as source:
            for row in csv.DictReader(source):
                for column in CENSUS_OPERANDS:
                    if row[column]:
                        found.add(int(row[column], 16))
    return found


def declare(b, root):
    pending = b.stash.setdefault(__name__, [])
    manual = b.config.get("tokens", {}).get("manual", ())

    def record(key, row, columns, src):
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
                    item = {"kind": item.pop("kind"), "supports": supports, **item,
                            "legacy": token.text}
                    b.symbol(key.layout, key.kind, key.address, src, evidence=[item])

    src = PATHS["funcs"].as_posix()
    for row in rows(root, "funcs"):
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
    for row in rows(root, "vars"):
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
    for row in rows(root, "findings"):
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
    bound = census_operands(root, LAYOUT)
    for row in rows(root, "axes"):
        address = _address(row["addr"])
        key = b.symbol(LAYOUT, "axis", address, src)
        b.props(key, {
            "quantity": row["kind"],
            "unit": row["units"],
            "scale": row["scale_expr"],
            "to_raw": row["to_byte"],
            "scale_level": _level(row["scale_conf"]),
            "level": "code" if address in bound else "candidate",
            "note": row["note"],
        }, src)
        record(key, row, ("scale_evidence",), src)

    src = PATHS["dtc"].as_posix()
    for row in rows(root, "dtc"):
        key = b.symbol(LAYOUT, "dtc", _address(row["record_addr"]), src, props={
            "index": _integer(row["index"]),
            "attribute": row["attribute_addr"],
        })
        b.props(key, {
            "code": row["dtc"],
            "group": row["group"],
            "disabled": row["disabled_attribute"],
            "level": _level(row["confidence"]),
            "title": row["note"],
        }, src)

    src = PATHS["diagnostic-bindings"].as_posix()
    for row in rows(root, "diagnostic-bindings"):
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
                binding["evidence"].append({**item, "legacy": token.text})
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
    """Map one dependency token of a ledger row by the table of section 20.7."""
    role = token.role
    to = b.resolve(row.layout, token.address, tokens.TARGET_KINDS[role], src)
    if to is None:
        b.issue("references", src, row.key,
                f"{token.text}: no symbol of kind {'/'.join(tokens.TARGET_KINDS[role])} "
                f"at {row.layout}:{token.address:08x}")
        return
    props = {"relies": token.relies, "supports": supports}
    legacy = {"legacy": token.text}

    def link(owner, type_, target, stated="owner", **extra):
        b.link(owner, type_, target, src, props={**props, **extra}, stated=stated)

    rk, tk = row.kind, to.kind
    if role == "trace":
        b.symbol(row.layout, row.kind, row.address, src, evidence=[
            {"kind": "trace", "supports": supports, "to": to, "relies": token.relies,
             **legacy}])
    elif role == "writes" and rk in ("ram", "reg") and tk == "fn":
        link(row, "writer", to)
    elif role == "writes" and rk == "fn" and tk in ("ram", "reg"):
        link(to, "writer", row, stated="to")
    elif role == "writes" and rk in ("tbl", "axis") and tk in ("ram", "reg"):
        link(to, "lookup", row, stated="to")
    elif role == "consumer" and rk in DATUM and tk == "fn":
        link(row, "reader", to)
    elif role == "indexed_by" and rk in ("tbl", "axis") and tk in ("ram", "reg"):
        link(row, "index", to)
    elif role == "indexed_by" and rk in ("ram", "reg") and tk in DATUM:
        link(row, "input", to)
    elif role == "indexed_by" and rk == "fn" and tk in ("ram", "reg"):
        link(to, "reader", row, stated="to", role="indexed_by")
    elif role == "from_map" and rk in ("ram", "reg") and tk in ("tbl", "axis"):
        table_tokens = b.row_tokens.get((to.layout, to.address), set())
        if ("indexed_by", row.address) in table_tokens:
            link(to, "index", row, stated="to")
        elif ("writes", row.address) in table_tokens:
            link(row, "lookup", to)
        else:
            link(row, "input", to)
    elif role == "from_map" and rk == "fn" and tk in ("tbl", "axis"):
        link(to, "reader", row, stated="to")
    elif role == "selector" and tk in DATUM:
        link(row, "selector", to)
    elif role == "threshold" and tk in vocab.LINK_TYPES["threshold"][1]:
        link(row, "threshold", to)
    elif role == "base" and rk == "ram" and tk == "ram":
        link(row, "base", to, offset=token.offset or 0)
    else:
        link(row, "depends", to, role=role)
