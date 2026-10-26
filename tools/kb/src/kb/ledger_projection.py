"""Serialize the JK08A ledger projections and curated aliases from native owners."""

from collections import defaultdict
import csv
import io

from kb import compile, match, repo, store, tokens, vocab
from kb.adapters import curated, ledgers
from kb.model import SymbolKey
from kb.repo import KbError

HEADERS = {
    "funcs": "addr,role,semantics,contract,contract_conf,contract_evidence,confidence,evidence,note",
    "vars": "addr,semantics,units,confidence,evidence,note",
    "findings": "addr,family,width,height,storagetype,accessor,confidence,evidence,role,semantics,units,scale_expr,to_byte,scale_conf,scale_evidence,note",
    "axes": "addr,kind,units,scale_expr,to_byte,scale_conf,scale_evidence,note",
    "dtc": "index,dtc,record_addr,attribute_addr,stock_attribute,disabled_attribute,group,confidence,note,evidence",
    "diagnostic-bindings": "id,kind,firmware_label,firmware_addr,diagnostic_label,diagnostic_key,source_claim_label,source_claim_id,confidence,applicability,rom_scope,priority,evidence,note",
    "curated": "addr,name,note",
}
CURATED_HEADER = """# Curated function names of layout 7mfk, whose L0 image is JK08A.
# RenameFuncs.java applies them to a Ghidra program of the layout; the Memgraph
# loaders and the ROM atlas read them with tools/rom_sources.py.
# Format: addr,name,note (addr is eight hexadecimal digits; note becomes the
# function plate comment and holds no comma).
"""
PLACEMENT = ("addr", "record_addr", "index", "attribute_addr", "stock_attribute")
COLUMNS = {"semantics": "summary", "units": "unit", "confidence": "level",
           "contract_conf": "contract_level", "family": "access", "width": "cols",
           "height": "rows", "storagetype": "storage", "kind": "quantity",
           "scale_expr": "scale", "to_byte": "to_raw", "scale_conf": "scale_level",
           "dtc": "code", "disabled_attribute": "disabled"}
LABELS = {"fn": "Func", "ram": "Reg", "reg": "Reg", "tbl": "Map", "axis": "Axis"}
REGISTRY_KINDS = {"funcs": ("fn",), "vars": ("ram", "reg"), "findings": ("tbl",),
                  "axes": ("axis",), "dtc": ("dtc",), "curated": ("fn",),
                  "diagnostic-bindings": tuple(LABELS)}


def subject(model, registry, row):
    """The reviewed symbol a source row places."""
    if registry == "diagnostic-bindings":
        address = int(row["firmware_addr"], 16)
        kinds = ledgers.LEGACY_KINDS[row["firmware_label"]]
        return next(model.symbols[SymbolKey(ledgers.LAYOUT, kind, address)]
                    for kind in kinds if SymbolKey(ledgers.LAYOUT, kind, address) in model.symbols)
    kind = {"funcs": "fn", "findings": "tbl", "axes": "axis", "dtc": "dtc"}.get(registry)
    address = int(row["record_addr"] if registry == "dtc" else row["addr"], 16)
    if kind:
        return model.symbols[SymbolKey(ledgers.LAYOUT, kind, address)]
    return next(model.symbols[SymbolKey(ledgers.LAYOUT, kind, address)] for kind in ("ram", "reg")
                if SymbolKey(ledgers.LAYOUT, kind, address) in model.symbols)


def _offset(symbol, address, value, text):
    """The selected spelling of a numeric offset, validated against its fact."""
    text = str(value) if text is None else text
    if (not isinstance(text, str) or not tokens.INDIRECT_BASE.fullmatch(address + "+" + text)
            or int(text, 16 if text.startswith("0x") else 10) != value):
        raise KbError(f"{symbol.key.key}: ledger offset spelling disagrees with its value",
                      code=3)
    return text


def terminal(model, symbol, item, offset_text=None, meaning_index=None):
    """A selected typed item as a legacy token, without granting a new claim."""
    kind = item["kind"]
    if kind in ("l0-context", "unverified-site"):
        if kind == "l0-context":
            failure = match.verify(model, symbol, item)
            if failure:
                raise KbError(f"{symbol.key.key}: {failure}", code=3)
        return "site:" + item["at"].split(":")[1]
    if kind == "l0":
        return "site:" + item["at"].split(":")[1]
    if kind == "rom-bytes":
        return f"rom_const:{item['at'].split(':')[1]}={item['value']}"
    if kind == "unbound-constant":
        return f"rom_const:{item['value']}"
    if kind in ("spec", "arithmetic", "manual", "hardware"):
        value = item.get("key", item.get("value"))
        return "spec:" + ("hardware-results:" if kind == "hardware" else "") + str(value)
    if kind == "registry":
        return f"registry:{item.get('path', item.get('value'))}"
    if kind == "indirect":
        if item.get("mode") != "base":
            raise KbError(f"{symbol.key.key}: a ledger indirect token requires mode base", code=3)
        address = item['at'].split(':')[1]
        return f"indirect_base:{address}+{_offset(symbol, address, item['value'], offset_text)}"
    if kind == "test":
        return f"test:{item['path']}#{item['key']}"
    if kind == "trace":
        to = item["to"]
        if isinstance(to, SymbolKey):
            address = to.address
        elif "/" in str(to):
            name, kind, layout = str(to).split("/")
            if meaning_index is None:
                meaning = next(item for item in model.meanings if item.key == f"{name}/{kind}")
            else:
                meaning = meaning_index.get(f"{name}/{kind}")
                if meaning is None:
                    raise StopIteration
            address = meaning.symbols[layout].address
        else:
            address = int(str(to).split(":")[1], 16)
        prop = next(key for key, value in tokens.RELIES.items() if value == item["relies"])
        return f"{item.get('note', 'trace')}:{address:08x}@{prop}"
    raise KbError(f"{symbol.key.key}: no ledger token for {kind}", code=3)


def dependency(model, symbol, item, lookup=None):
    """Project a selected claim only while the corresponding link holds."""
    to = (lookup[0].get(item["to"]) if lookup is not None else
          next((meaning for meaning in model.meanings if meaning.key == item["to"]), None))
    if to is None or ledgers.LAYOUT not in to.symbols:
        raise KbError(f"{symbol.key.key}: ledger dependency {item['to']} has no 7mfk symbol", code=3)
    target, role = to.symbols[ledgers.LAYOUT], item["role"]
    if (role not in tokens.DEPENDENCY or role == "trace"
            or item["supports"] not in tokens.SUPPORTS.values()
            or item["relies"] not in vocab.RELIES
            or item["end"] not in ("owner", "to") or item["type"] not in vocab.LINK_TYPES):
        raise KbError(f"{symbol.key.key}: invalid ledger dependency end or type", code=3)
    offset = item.get("offset")
    if offset is not None and (isinstance(offset, bool) or not isinstance(offset, int)
                               or offset < 0):
        raise KbError(f"{symbol.key.key}: invalid ledger dependency offset", code=3)
    row_tokens = {}
    if role == "from_map" and symbol.kind in ("ram", "reg"):
        if item["type"] in ("index", "lookup"):
            row_tokens[target.layout, target.address] = {
                ("indexed_by" if item["type"] == "index" else "writes", symbol.address)}
    token = tokens.Token(role, "", target.address, offset, item["relies"])
    _, type_, _, end, props = ledgers.dependency(symbol.key, target.key, token,
                                               item["supports"], row_tokens)
    if (type_, end, props.get("role")) != (item["type"], item["end"], item.get("link_role")):
        raise KbError(f"{symbol.key.key}: ledger dependency disagrees with its token role",
                      code=3)
    owner, other = ((symbol.meaning, to) if item["end"] == "owner"
                    else (to, symbol.meaning))
    prefix = "reverse_" if item["end"] == "to" else ""
    expected_offset = (offset or 0) if item["type"] == "base" else None

    def claims(props, roles):
        relies = props.get(prefix + "relies")
        supports = props.get(prefix + "supports", "identity")
        supports = supports if isinstance(supports, list) else [supports]
        return (relies in vocab.RELIES and item["relies"] in vocab.RELIES
                and vocab.RELIES.index(relies) >= vocab.RELIES.index(item["relies"])
                and item["supports"] in supports
                and ("link_role" not in item or item["link_role"] in roles))

    candidates = [link for link in (lookup[1].get(id(owner), ()) if lookup is not None
                                    else model.links)
                  if link.owner is owner and link.to is other and link.type == item["type"]
                  and link.offset == expected_offset and ledgers.LAYOUT in link.stated
                  and claims(link.props, link.roles)]
    self_claim = owner is other and any(
        model.by_node.get(fact.owner) is owner and fact.type == item["type"]
        and fact.props.get("offset") == expected_offset
        and ledgers.LAYOUT in (fact.layouts or (getattr(fact.owner, "layout", owner.home),))
        and claims({("reverse_" + key if fact.stated == "to" and key in ("relies", "supports")
                     else key): value for key, value in fact.props.items()},
                   {fact.props.get("role")}) for fact in model.self_links)
    if not candidates and not self_claim:
        raise KbError(f"{symbol.key.key}: ledger dependency {item['to']} has no matching "
                      "link and claim", code=3)
    prop = next(key for key, value in tokens.RELIES.items() if value == item["relies"])
    address = f"{target.address:08x}"
    if offset is not None:
        address += "+" + _offset(symbol, address, offset, item.get("offset_text"))
    return f"{role}:{address}@{prop}"


def _notes(value):
    return [] if value is None else [value] if isinstance(value, str) else list(value)


def _indices(symbol, selected, values, label):
    """A view selects existing entries with nonnegative, unique integer indices."""
    if (not isinstance(selected, list) or any(isinstance(index, bool)
            or not isinstance(index, int) or index < 0 or index >= len(values)
            for index in selected) or len(set(selected)) != len(selected)):
        raise KbError(f"{symbol.key.key}: invalid {label} selection", code=3)
    return [values[index] for index in selected]


def _row(model, symbol, document, marker, lookup=None):
    registry = marker["registry"]
    row = dict.fromkeys(HEADERS[registry].split(","), "")
    row["record_addr" if registry == "dtc" else "addr"] = f"{symbol.address:08x}"
    for column in marker["fields"]:
        if column not in row:
            raise KbError(f"{symbol.key.key}: unknown {registry} column {column}", code=3)
        if column == "accessor":
            links = [link for link in symbol.meaning.links if link.owner is symbol.meaning
                     and link.type == "reader" and "accessor" in link.roles]
            if len(links) != 1:
                raise KbError(f"{symbol.key.key}: {len(links)} accessor links", code=3)
            value = f"{links[0].to.symbols[ledgers.LAYOUT].address:08x}"
        elif column == "name":
            value = marker.get("name", symbol.meaning.name)
            known = {symbol.meaning.name, *(name for name, _, _ in symbol.meaning.other_names)}
            if value not in known:
                raise KbError(f"{symbol.key.key}: ledger name is neither current nor former", code=3)
        elif column == "note" and registry == "dtc":
            value = symbol.value("title")
        elif column == "units" and "storage_description" in marker:
            value = marker["storage_description"]
        else:
            value = symbol.value(COLUMNS.get(column, column))
            if column == "storagetype" and value == "float32":
                value = "float"
        row[column] = "" if value is None else str(value)
    notes = _notes(document.get("note"))
    if marker.get("notes"):
        row["note"] = " ".join(_indices(symbol, marker["notes"], notes, "ledger note"))
    if marker.get("title"):
        row["note"] = symbol.value("title")
    entry = next(item for item in document["symbol"] if item["layout"] == ledgers.LAYOUT)
    offsets = {}
    for selected in marker.get("offset", ()):
        index = selected["evidence"]
        if (isinstance(index, bool) or not isinstance(index, int) or index < 0
                or index >= len(entry.get("evidence", ()))
                or entry["evidence"][index].get("kind") != "indirect" or index in offsets
                or not any(index in marker.get(supports, ()) for supports in tokens.SUPPORTS.values())):
            raise KbError(f"{symbol.key.key}: invalid ledger offset selection", code=3)
        offsets[index] = selected["text"]
    for column, supports in tokens.SUPPORTS.items():
        if column not in row:
            continue
        try:
            indices = marker.get(supports, [])
            items = _indices(symbol, indices, entry.get("evidence", []), column)
            if any(item.get("supports", "identity") != supports for item in items):
                raise KbError(f"{symbol.key.key}: {column} selects another claim", code=3)
            selected = [terminal(model, symbol, item, offsets.get(index),
                                 lookup[2] if lookup is not None else None)
                        for index, item in zip(indices, items)]
        except (IndexError, KeyError, TypeError) as error:
            raise KbError(f"{symbol.key.key}: invalid {column} selection", code=3) from error
        selected += [dependency(model, symbol, item, lookup) for item in marker.get("dependency", ())
                     if item["supports"] == supports]
        row[column] = tokens.canonical("; ".join(selected))
    if registry == "dtc":
        row["index"] = str(symbol.value("index"))
        row["attribute_addr"] = str(symbol.value("attribute"))
        address = int(row["attribute_addr"], 16)
        row["stock_attribute"] = match.code(ledgers.LAYOUT, model.root).data[
            address:address + 2].hex()
    return row


def _diagnostic(model, symbol, binding, meaning_index=None):
    row = {"id": binding["id"], "kind": binding["kind"],
           "firmware_label": LABELS[symbol.kind], "firmware_addr": f"{symbol.address:08x}",
           "diagnostic_label": binding["label"], "diagnostic_key": binding["key"],
           "source_claim_label": binding["claim"]["label"],
           "source_claim_id": binding["claim"]["id"], "confidence": binding["level"],
           "applicability": binding["applicability"], "rom_scope": binding["scope"],
           "priority": str(binding["priority"]), "note": binding["note"]}
    row["evidence"] = tokens.canonical("; ".join(terminal(model, symbol, item, meaning_index=meaning_index)
                                                for item in binding["evidence"]))
    return row


def render(model):
    """Every JK08A ledger and the 7mfk curated names, from entity files."""
    rows = {name: [] for name in HEADERS}
    orders = {name: set() for name in HEADERS}
    unusual_orders = set()
    links = defaultdict(list)
    for link in model.links:
        links[id(link.owner)].append(link)
    last, first = {}, {}
    for meaning in model.meanings:
        key = meaning.key
        last[key] = meaning
        first.setdefault(key, meaning)
    lookup = last, links, first
    for kind, name, markers, src in model.stash.get("ledger_rows", ()):
        meaning = model.files[kind, name][0]
        symbol = meaning.symbols.get(ledgers.LAYOUT)
        if symbol is None:
            raise KbError(f"{meaning.key}: ledger view has no 7mfk symbol", code=3)
        document = store.load(model.root, src, model.overlay)
        for marker in markers:
            registry, order = marker.get("registry"), marker.get("order")
            if (registry not in HEADERS or isinstance(order, bool) or not isinstance(order, int)
                    or order < 0 or symbol.kind not in REGISTRY_KINDS[registry]
                    or (order in orders[registry]
                        if type(order) is int and registry not in unusual_orders
                        else any(index == order for index, _ in rows[registry]))):
                raise KbError(f"{symbol.key.key}: invalid or duplicate ledger row selector", code=3)
            if marker["registry"] == "diagnostic-bindings":
                bindings = [item for item in meaning.tables.get("diagnostic", ())
                            if item["id"] == marker.get("binding")]
                if len(bindings) != 1:
                    raise KbError(f"{symbol.key.key}: ledger selects no unique diagnostic binding",
                                  code=3)
                row = _diagnostic(model, symbol, bindings[0], lookup[2])
            else:
                row = _row(model, symbol, document, marker, lookup)
            row_registry = marker["registry"]
            entries = rows[row_registry]
            row_order = marker["order"]
            entries.append((row_order, row))
            if type(row_order) is int:
                orders[row_registry].add(row_order)
            else:
                unusual_orders.add(row_registry)
    output = {}
    for name, entries in rows.items():
        out = io.StringIO(newline="")
        if name == "curated":
            out.write(CURATED_HEADER)
        columns = HEADERS[name].split(",")
        writer = csv.DictWriter(out, columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(row for _, row in sorted(entries, key=lambda entry: entry[0]))
        path = curated.DIRECTORY / "7mfk.csv" if name == "curated" else ledgers.PATHS[name]
        output[path.as_posix()] = out.getvalue()
    return output


def registries(root=repo.ROOT):
    """The six JK08A registries of the current compiler model."""
    return {path: text for path, text in render(compile.cached(root)).items()
            if path.startswith("defs/")}


def curated_names(root=repo.ROOT):
    """The 7mfk curated-name view of the current compiler model."""
    return render(compile.cached(root))[(curated.DIRECTORY / "7mfk.csv").as_posix()]


def validate_conversion(path, original, generated):
    """Only process history may leave a canonical CSV; all facts remain."""
    def read(text):
        return list(csv.DictReader(line for line in io.StringIO(text)
                                   if not line.startswith("#")))
    old, new = read(original), read(generated)
    for row in old:
        for column in tokens.SUPPORTS:
            if column in row:
                row[column] = tokens.canonical("; ".join(token.text for token in tokens.parse(
                    row[column]) if token.role not in tokens.PROCESS))
    if old != new:
        changed = [row for row in old if row not in new]
        added = [row for row in new if row not in old]
        raise KbError(f"{path}: conversion changes {len(changed)} source rows and adds "
                      f"{len(added)} rows; nothing is written\n"
                      + "\n".join(repr(row) for row in [*changed[:2], *added[:2]]), code=3)


def normalize(text):
    """A CSV with only evidence cells changed to canonical token order."""
    source = csv.DictReader(io.StringIO(text))
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, source.fieldnames, lineterminator="\n")
    writer.writeheader()
    for row in source:
        for column in tokens.SUPPORTS:
            if column in row:
                row[column] = tokens.canonical(row[column])
        writer.writerow(row)
    return output.getvalue()
