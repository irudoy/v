"""Native meanings and symbols (tools/kb/SPEC.md, sections 7.2 and 7.3).

`tools/kb/projections.toml` registers their generated native registries.

The table registry also covers JK00C and JK00D of the 8MFK family for the
target-native tables that their relocated JK08A definition cannot state, such
as word curves on an explicit axis; the fuel-cut registry covers the VQ37VHR
images only.

- Each table and axis entry of `defs/vq37-native-tables.toml` gives a `tbl`
  or `axis` symbol on the layout of its target image, and its id joins the
  symbols of every target into one meaning with the strength of a native
  table id and names it. The meaning takes `home` from the first target that
  carries the id. Geometry, scale, level, `semantics` as `summary`, and
  `[editor]` are keys of the symbol, which the meaning lifts from its home
  symbol, so a target whose text differs keeps its summary as an override;
  the images of one layout state one `semantics` text. `note` becomes the
  note of the symbol, prefixed with its image where the images of one layout
  state different text. An entry that only some images of a layout carry
  gives the symbol `images`.
- `values_sha256` must equal the digest of the block of the image that the
  geometry and the storage of the entry give.
- A pointer binding gives the symbol `l0` evidence at its site, or `indirect`
  evidence with mode `base` and the offset as `value` where the accessor
  displaces the literal, and a `reader` link to the accessor with the same
  evidence. The accessor takes `l0` identity evidence at the first census
  call of its layout that it makes with an entry bound to it as an operand.
  `axis_x` and `axis_y` give `axis` links with `l0` evidence at the first
  census call of the layout that passes the entry and the axis.
- `[target.<ROM>.absent]` gives the meaning of each id the status `absent`
  with `l0` evidence at each function entry of the layout that its text
  names, or else `registry` evidence.
- Each target of `defs/vq37-native-fuel-cut.toml` gives the `fn`, `ram`,
  `tbl`, and `axis` symbols of its fuel-cut mechanism, joined across targets
  by registry key, and the state byte names its armed and active bits. The
  call site gives the predicate function `l0` evidence with the ordinal of
  the predicate in the coordinator as `value` and the target's `evidence` as
  `note`; the site lies the instruction ordinal of the call from the
  coordinator entry. The scheduler word gives the coordinator `rom-bytes`
  evidence with the coordinator address as `value`. Each datum takes `l0`
  evidence at the first instruction of the function body whose L0
  references hold its address. The curves take the axis as their `x` axis,
  with `l0` evidence at the first census call of the layout that passes
  both. The values of the axis, the caps, the curves, and the delay
  calibration must equal the image bytes, and their number gives the
  geometry of their symbols. Each pointer binding gives the symbol at its
  target `l0` evidence at its site and a `reader` link to the predicate
  function. The function size and digest must equal L0, and the targets of
  the images of one layout state one evidence text.
- The stock digest of every target must equal the image catalog.
- `render_tables` and `render_fuel_cut` write a registry document in the
  form of its file: targets, entries, and absent ids in document order, the
  keys of an entry in a fixed order, and addresses as eight uppercase
  hexadecimal digits. The files list the entries of a target by address,
  the pointer bindings of an entry by site and offset, and the absent ids by
  name.

The compiler leaves out this adapter (`adapters.CONVERTED`), so this module
is no compiler input, and `kb.convert` runs `declare` and `relate` to compile
the model before the conversion. `tables` and `fuel_cut` render the files as
projections of the model. The tables list for each target an entry of every
`tbl` and `axis` meaning with `[editor]` whose home is the layout of a
target, where the image carries its symbol: the keys of the symbol, the
pointer bindings from the evidence of its `reader` links with the role
`accessor`, the axes from its `axis` links that the layout states, the note
from the file entry of the symbol, and `values_sha256` from the image; and
the meanings absent on the layout. The fuel cut lists for each target the
symbols of the fuel-cut meanings on its layout, the call and the scheduler
word from their evidence, the masks from the bits of the state, the values
from the image by the geometry of their symbols, the size and the digest of
the function from L0, and the pointer bindings from the evidence of the
`reader` links to the function that carry no role.
"""

from collections import defaultdict
from functools import lru_cache
import hashlib
from pathlib import Path
import re
import tomllib

from kb import derive, l0, match, repo, sites, store, vocab

TABLES = Path("defs/vq37-native-tables.toml")
FUEL_CUT = Path("defs/vq37-native-fuel-cut.toml")
SCHEMA_VERSIONS = {TABLES: 4, FUEL_CUT: 1}
KINDS = {"table": "tbl", "axis": "axis"}
EDITOR = ("name", "category", "order", "format", "fine", "coarse", "mask", "constant_content",
          "static_axis", "static_axis_name", "static_axis_x", "static_axis_x_name",
          "static_axis_y", "static_axis_y_name")
# Symbol keys and the entry keys that state them.
GEOMETRY = {"tbl": (("cols", "width"), ("rows", "height")),
            "axis": (("points", "length"), ("quantity", "kind"))}
KEYS = (("unit", "units"), ("scale", "scale_expr"), ("to_raw", "to_byte"),
        ("scale_level", "scale_conf"), ("level", "confidence"), ("summary", "semantics"))
# The axis entries of the registry state no semantics; the meaning keeps its
# summary.
SYMBOL_KEYS = {"tbl": KEYS, "axis": tuple(pair for pair in KEYS if pair[0] != "summary")}
ENTRY_KEYS = frozenset({"id", "address", "width", "height", "length", "kind", "storagetype",
                        "values_sha256", "pointer_bindings", "axis_x", "axis_y", "note",
                        *EDITOR, *(source for _, source in KEYS)})
TARGET_KEYS = frozenset({"stock_sha256", *KINDS, "absent"})
FUNCTION = re.compile(r"\bFUN_([0-9A-Fa-f]{8})\b")
# Fuel-cut keys that give symbols, with their kind; None takes the kind of the
# address space.
FUEL_CUT_SYMBOLS = (("function_address", "fn"), ("coordinator_address", "fn"),
                    ("selector_address", None), ("rpm_address", None),
                    ("state_address", None), ("delay_address", None),
                    ("delay_calibration_address", "tbl"), ("caps_address", "tbl"),
                    ("curves_address", "tbl"), ("axis_address", "axis"))
BITS = (("state_armed_mask", "armed"), ("state_active_mask", "active"))
# Fuel-cut data with the key of its values and their storage.
FUEL_CUT_DATA = (("axis_address", "axis_values", "uint16"),
                 ("caps_address", "caps_values", "uint16"),
                 ("curves_address", "curve_values", "uint16"),
                 ("delay_calibration_address", "delay_calibration_value", "uint8"))
BINDINGS = {"pointer_bindings": ("tbl", "axis", "const"), "ram_pointer_bindings": ("ram", "reg")}
FUEL_CUT_KEYS = frozenset({
    "stock_sha256", "function_size", "function_sha256", "coordinator_pointer_site",
    "coordinator_predicate_ordinal", "predicate_call_site", "predicate_instruction_ordinal",
    "delay_calibration_value", "axis_values", "caps_values", "curve_values", "evidence",
    *(name for name, _ in FUEL_CUT_SYMBOLS), *(name for name, _ in BITS), *BINDINGS})


def inputs(root):
    return [TABLES.as_posix(), FUEL_CUT.as_posix()]


def declare(b, root):
    catalog = repo.images(root)
    declare_tables(b, _document(b, root, TABLES), TABLES.as_posix(), catalog)
    declare_fuel_cut(b, root, _document(b, root, FUEL_CUT), FUEL_CUT.as_posix(), catalog)


def _document(b, root, path):
    document = tomllib.loads((root / path).read_text(encoding="utf-8"))
    version = document.get("schema_version")
    if version != SCHEMA_VERSIONS[path]:
        b.issue("schema", path.as_posix(), "schema_version",
                f"schema_version {version!r}; the adapter reads {SCHEMA_VERSIONS[path]}")
    return document


def _location(layout, address):
    return f"{layout}:{address:08x}"


@lru_cache(maxsize=None)
def _image(path):
    return path.read_bytes()


def _values(data, address, storage, count):
    """`count` unsigned big-endian elements of `storage` at an address."""
    width = match.STORAGE_BYTES[storage]
    return [int.from_bytes(data[address + width * index:address + width * (index + 1)], "big")
            for index in range(count)]


# Operand columns of the accessor census.
OPERANDS = ("bt_r4", "bt_r5", "bt_r6", "df_r4", "df_r5", "df_r6", "df_r7")


@lru_cache(maxsize=None)
def census(layout, root=repo.ROOT):
    """(callsite, accessor, operands) of every census call of a layout, by
    callsite."""
    base = root / repo.L0 / layout
    calls = []
    for kernel in l0.census(layout, root).kernels:
        for row in derive.read_rows(base / l0.Census.file(kernel)):
            calls.append((int(row["callsite"], 16), int(row["accessor"], 16),
                          frozenset(int(row[column], 16) for column in OPERANDS if row[column])))
    return tuple(sorted(calls))


def census_call(layout, root, operands, accessor=None):
    """The `l0` identity item at the first census call of a layout that passes
    every address of `operands`, or, with `accessor`, that the accessor makes
    with one of them; None when no call does."""
    for site, caller, passed in census(layout, root):
        if accessor is None and operands <= passed or caller == accessor and operands & passed:
            return {"kind": "l0", "supports": "identity", "at": _location(layout, site)}
    return None


def _targets(b, src, document, catalog, known):
    """(ROM, layout, target) of each target in file order."""
    layout_of = {rom: layout.id for layout in b.layouts.values() for rom in layout.images}
    for rom, target in document.get("target", {}).items():
        subject = f"target.{rom}"
        layout = layout_of.get(rom)
        if layout is None:
            b.issue("schema", src, subject, "no layout holds the image")
            continue
        for key in sorted(set(target) - known):
            b.issue("schema", src, subject, f"unknown key {key}")
        image = catalog.get(rom)
        if image is None or target.get("stock_sha256") != image.sha256:
            b.issue("audit", src, subject, "stock_sha256 disagrees with the image catalog")
        yield rom, layout, target


# Native tables -------------------------------------------------------------

def declare_tables(b, document, src, catalog):
    pending = b.stash.setdefault(__name__, [])
    targets = list(_targets(b, src, document, catalog, TARGET_KEYS))
    found = defaultdict(list)
    for rom, layout, target in targets:
        for name, kind in KINDS.items():
            for entry in target.get(name, ()):
                subject = f"target.{rom}.{name}.{entry.get('id')}"
                for key in sorted(set(entry) - ENTRY_KEYS):
                    b.issue("schema", src, subject, f"unknown key {key}")
                found[(kind, entry["id"])].append((rom, layout, entry))
    kinds = defaultdict(set)
    for kind, name in found:
        kinds[name].add(kind)
    for (kind, name), entries in found.items():
        _declare_id(b, src, kind, name, entries, pending, catalog)
    for rom, layout, target in targets:
        for name, text in target.get("absent", {}).items():
            subject = f"target.{rom}.absent.{name}"
            if len(kinds.get(name, ())) != 1:
                b.issue("schema", src, subject, "no single table or axis of a target carries "
                        "the id")
                continue
            _declare_absent(b, src, subject, (*kinds[name], "native", name), layout, text)


def _declare_id(b, src, kind, name, entries, pending, catalog):
    group = (kind, "native", name)
    _, home, _ = entries[0]
    b.name(group, name, "native", src)
    b.props(group, {"home": home}, src)
    carried = defaultdict(list)
    for rom, layout, entry in entries:
        carried[(layout, entry["address"])].append((rom, entry))
    for (layout, address), images in carried.items():
        own = [rom for rom, _ in images]
        if len({entry.get("semantics") for _, entry in images}) > 1:
            b.issue("schema", src, f"{name}@{layout}", "the images of one layout state "
                    "different semantics")
        notes = _notes(images)
        props = {"note": notes} if notes else {}
        if set(own) != set(b.layouts[layout].images):
            props["images"] = [rom for rom in b.layouts[layout].images if rom in own]
        key = b.symbol(layout, kind, address, src, group=group, props=props, strength="native")
        for rom, entry in images:
            b.keys(key, _keys(kind, entry), src)
            if ("values_sha256" in entry
                    and _digest(kind, entry, catalog.get(rom)) != entry["values_sha256"]):
                b.issue("audit", src, f"target.{rom}.{name}", "values_sha256 differs from the "
                        "digest of the image block")
            for binding in entry.get("pointer_bindings", ()):
                item = _binding(layout, binding)
                b.symbol(layout, kind, address, src, evidence=[item])
                pending.append(("reader", key, binding["accessor"], item, src))
            for slot in ("x", "y"):
                if f"axis_{slot}" in entry:
                    pending.append(("axis", key, slot, entry[f"axis_{slot}"], src))


def _keys(kind, entry):
    keys = {name: entry.get(source) for name, source in GEOMETRY[kind] + KEYS}
    keys["storage"] = vocab.storage(entry.get("storagetype"))
    editor = {name: entry[name] for name in EDITOR if name in entry}
    if editor:
        keys["editor"] = editor
    return {name: value for name, value in keys.items() if value not in (None, "")}


def _digest(kind, entry, image):
    """The digest of the image block of an entry, or None without the image or
    the geometry."""
    storage = vocab.storage(entry.get("storagetype"))
    count = entry.get("length") if kind == "axis" else (
        entry.get("width") or 0) * (entry.get("height") or 0)
    if image is None or storage not in match.STORAGE_BYTES or not count:
        return None
    start = entry["address"]
    return hashlib.sha256(
        _image(image.path)[start:start + count * match.STORAGE_BYTES[storage]]).hexdigest()


def _notes(images):
    """Notes of one symbol from the notes of its images: a text that every
    image states alike once, and otherwise each image's text after its name."""
    texts = [(rom, entry.get("note")) for rom, entry in images]
    if len({text for _, text in texts}) == 1:
        return [text for _, text in texts[:1] if text]
    return [f"{rom}: {text}" for rom, text in texts if text]


def _binding(layout, binding):
    """The evidence of a pointer binding: the literal at its site names the
    entry, or a base that the accessor displaces by `offset`."""
    at = _location(layout, binding["site"])
    if binding.get("offset"):
        return {"kind": "indirect", "supports": "identity", "at": at, "mode": "base",
                "value": binding["offset"]}
    return {"kind": "l0", "supports": "identity", "at": at}


def _declare_absent(b, src, subject, group, layout, text):
    evidence = []
    for match in dict.fromkeys(FUNCTION.findall(text)):
        address = int(match, 16)
        if b.is_function(layout, address):
            evidence.append({"kind": "l0", "supports": "identity",
                             "at": _location(layout, address)})
        else:
            b.issue("references", src, subject, f"FUN_{match} is no function entry of "
                    f"l0/{layout}/funcs.csv")
    if not evidence:
        evidence = [{"kind": "registry", "supports": "identity", "path": src, "key": subject}]
    b.status(group, layout, "absent", src, props={"note": text}, evidence=evidence)


# Fuel cut ------------------------------------------------------------------

def declare_fuel_cut(b, root, document, src, catalog):
    pending = b.stash.setdefault(__name__, [])
    signatures = {}
    evidence = {}
    for rom, layout, target in _targets(b, src, document, catalog, FUEL_CUT_KEYS):
        subject = f"target.{rom}"
        if evidence.setdefault(layout, target["evidence"]) != target["evidence"]:
            b.issue("schema", src, f"{subject}.evidence", "the targets of one layout state "
                    "different evidence texts")
        keys = {}
        for name, kind in FUEL_CUT_SYMBOLS:
            address = target[name]
            kind = kind or b.data_kind(layout, address)
            if kind is None:
                b.issue("symbols", src, f"{subject}.{name}", "an address outside RAM and the "
                        "peripherals")
                continue
            keys[name] = b.symbol(layout, kind, address, src, group=(kind, "fuel-cut", name))
        if layout not in signatures:
            signatures[layout] = repo.signatures(layout, root)
        stated = (target["function_size"], target["function_sha256"])
        if signatures[layout].get(target["function_address"]) != stated:
            b.issue("audit", src, subject, "function_size and function_sha256 disagree with "
                    f"l0/{layout}/function_signatures.csv")
        bits = []
        for name, bit in BITS:
            mask = target[name]
            if mask <= 0 or mask & (mask - 1):
                b.issue("schema", src, f"{subject}.{name}", f"mask {mask:#x} holds no single bit")
                continue
            bits.append({"bit": mask.bit_length() - 1, "name": bit})
        if "state_address" in keys and bits:
            b.keys(keys["state_address"], {"bit": sorted(bits, key=lambda item: item["bit"])},
                   src)
        function = keys["function_address"]
        site = target["predicate_call_site"]
        if site != target["coordinator_address"] + 2 * target["predicate_instruction_ordinal"]:
            b.issue("schema", src, f"{subject}.predicate_call_site", "the call site is not "
                    "predicate_instruction_ordinal instructions from the coordinator entry")
        b.symbol(layout, "fn", function.address, src, evidence=[{
            "kind": "l0", "supports": "identity", "at": _location(layout, site),
            "value": target["coordinator_predicate_ordinal"], "note": target["evidence"]}])
        b.symbol(layout, "fn", target["coordinator_address"], src, evidence=[{
            "kind": "rom-bytes", "supports": "identity",
            "at": _location(layout, target["coordinator_pointer_site"]),
            "value": f"{target['coordinator_address']:08x}"}])
        _declare_data(b, src, subject, rom, target, keys, catalog)
        body = sites.bodies(layout, root).get(function.address, ())
        found = sites.references(layout, root)
        for name, key in keys.items():
            if key.kind == "fn":
                continue
            reference = next((site for site in body if key.address in found.get(site, ())), None)
            if reference is None:
                b.issue("references", src, f"{subject}.{name}", "the function body holds no "
                        f"reference to {key.address:08x}")
                continue
            b.symbol(layout, key.kind, key.address, src, evidence=[{
                "kind": "l0", "supports": "identity", "at": _location(layout, reference)}])
        if "curves_address" in keys and "axis_address" in keys:
            curves, axis = keys["curves_address"], keys["axis_address"]
            item = census_call(layout, root, {curves.address, axis.address})
            if item is None:
                b.issue("references", src, f"{subject}.axis_address", "no census call of "
                        f"{layout} passes the curves and the axis")
            b.link(curves, "axis", axis, src, props={"slot": "x"},
                   evidence=[item] if item else None)
        for name, kinds in BINDINGS.items():
            for binding in target.get(name, ()):
                item = {"kind": "l0", "supports": "identity",
                        "at": _location(layout, binding["site"])}
                pending.append(("binding", layout, binding["target"], kinds, function, item,
                                src))


def _declare_data(b, src, subject, rom, target, keys, catalog):
    """The geometry of the fuel-cut data from the number of their values,
    which must equal the image bytes."""
    points = len(target["axis_values"])
    if not points or len(target["curve_values"]) % points:
        b.issue("schema", src, f"{subject}.curve_values", "the curve values fill no whole "
                "number of rows over the axis")
        return
    geometry = {"axis_address": {"points": points},
                "caps_address": {"cols": len(target["caps_values"]), "rows": 1},
                "curves_address": {"cols": points, "rows": len(target["curve_values"]) // points},
                "delay_calibration_address": {"cols": 1, "rows": 1}}
    image = catalog.get(rom)
    for name, values, storage in FUEL_CUT_DATA:
        stated = target[values] if isinstance(target[values], list) else [target[values]]
        if image is not None and _values(_image(image.path), target[name], storage,
                                         len(stated)) != stated:
            b.issue("audit", src, f"{subject}.{values}", "differs from the image bytes")
        if name in keys:
            b.keys(keys[name], {**geometry[name], "storage": storage}, src)


# Relations -----------------------------------------------------------------

def relate(b, root):
    pending = b.stash.get(__name__, ())
    bound = defaultdict(set)
    for entry in pending:
        if entry[0] == "reader":
            _, key, accessor, _, _ = entry
            bound[(key.layout, accessor)].add(key.address)
    for entry in pending:
        if entry[0] == "reader":
            _, key, accessor, item, src = entry
            to = b.resolve(key.layout, accessor, ("fn",), src)
            if to is None:
                b.issue("references", src, key.key, f"accessor {accessor:08x} is no function "
                        "entry")
                continue
            call = census_call(key.layout, root, bound[(key.layout, accessor)], accessor)
            if call is None:
                b.issue("references", src, to.key, "no census call of the accessor passes an "
                        "entry bound to it")
            b.symbol(key.layout, "fn", accessor, src, evidence=[call] if call else None)
            b.link(key, "reader", to, src, props={"role": "accessor"}, evidence=[item])
        elif entry[0] == "axis":
            _, key, slot, address, src = entry
            to = b.resolve(key.layout, address, ("axis",), src)
            if to is None:
                b.issue("references", src, key.key, f"axis_{slot} {address:08x} is no axis")
                continue
            call = census_call(key.layout, root, {key.address, address})
            if call is None:
                b.issue("references", src, key.key, f"no census call of {key.layout} passes "
                        f"it with axis_{slot} {address:08x}")
            b.link(key, "axis", to, src, props={"slot": slot}, evidence=[call] if call else None)
        else:
            _, layout, address, kinds, function, item, src = entry
            datum = b.resolve(layout, address, kinds, src)
            if datum is None:
                b.issue("references", src, _location(layout, address),
                        f"a pointer binding of {function.key} names no {'/'.join(kinds)}")
                continue
            b.symbol(layout, datum.kind, datum.address, src, evidence=[item])
            b.link(datum, "reader", function, src, evidence=[item])


# Rendering -----------------------------------------------------------------

# Keys of the entries and targets in the order of their files.
TABLE_ORDER = ("id", "address", "width", "height", "storagetype", "values_sha256",
               "pointer_bindings", "axis_x", "axis_y", "mask", "constant_content", "name",
               "category", "order",
               "format", "fine", "coarse", "units", "confidence", "scale_conf", "scale_expr",
               "to_byte", "static_axis_name", "static_axis", "static_axis_x_name",
               "static_axis_x", "static_axis_y_name", "static_axis_y", "semantics", "note")
AXIS_ORDER = ("id", "address", "length", "storagetype", "values_sha256", "pointer_bindings",
              "name", "kind", "format", "fine", "coarse", "units", "confidence", "scale_conf",
              "scale_expr", "to_byte", "note")
FUEL_CUT_ORDER = (
    "stock_sha256", "function_address", "function_size", "function_sha256",
    "coordinator_address", "coordinator_pointer_site", "coordinator_predicate_ordinal",
    "predicate_call_site", "predicate_instruction_ordinal", "selector_address", "rpm_address",
    "state_address", "state_active_mask", "state_armed_mask", "delay_address",
    "delay_calibration_address", "delay_calibration_value", "axis_address", "axis_values",
    "caps_address", "caps_values", "curves_address", "curve_values", "pointer_bindings",
    "ram_pointer_bindings", "evidence")
ENTRY_ADDRESSES = frozenset({"address", "axis_x", "axis_y"})
# Elements per line of the curve values.
CURVE_ROW = 8


def render_tables(document):
    """The text of `defs/vq37-native-tables.toml` from its document: the
    targets in document order, each with its tables, axes, and absent ids in
    document order, and the keys of an entry in the order of the file."""
    lines = [f"schema_version = {document['schema_version']}"]
    for rom, target in document["target"].items():
        lines += ["", f"[target.{rom}]", f"stock_sha256 = {_string(target['stock_sha256'])}"]
        for name, order in (("table", TABLE_ORDER), ("axis", AXIS_ORDER)):
            for entry in target.get(name, ()):
                _known(entry, order, f"target.{rom}.{name}")
                lines += ["", f"[[target.{rom}.{name}]]"]
                lines += [f"{key} = {_entry_value(key, entry[key])}"
                          for key in order if key in entry]
        if target.get("absent"):
            lines += ["", f"[target.{rom}.absent]"]
            lines += [f"{key} = {_string(text)}" for key, text in target["absent"].items()]
    return "\n".join(lines) + "\n"


def render_fuel_cut(document):
    """The text of `defs/vq37-native-fuel-cut.toml` from its document."""
    lines = [f"schema_version = {document['schema_version']}"]
    for rom, target in document["target"].items():
        _known(target, FUEL_CUT_ORDER, f"target.{rom}")
        lines += ["", f"[target.{rom}]"]
        for key in FUEL_CUT_ORDER:
            value = target[key]
            if key in BINDINGS:
                lines.append(f"{key} = [")
                lines += [f"  {{ site = {_address(item['site'])}, "
                          f"target = {_address(item['target'])} }}," for item in value]
                lines.append("]")
            elif key == "curve_values":
                lines.append(f"{key} = [")
                lines += ["  " + ", ".join(str(item) for item in value[start:start + CURVE_ROW])
                          + "," for start in range(0, len(value), CURVE_ROW)]
                lines.append("]")
            elif key.endswith("_mask"):
                lines.append(f"{key} = 0x{value:02X}")
            elif key.endswith(("_address", "_site")):
                lines.append(f"{key} = {_address(value)}")
            else:
                lines.append(f"{key} = {_plain(value)}")
    return "\n".join(lines) + "\n"


def _known(entry, order, subject):
    unknown = sorted(set(entry) - set(order))
    if unknown:
        raise repo.KbError(f"{subject}: no rendering of {', '.join(unknown)}", code=3)


def _address(value):
    return f"0x{value:08X}"


def _string(text):
    return f'"{store.escape(text)}"'


def _plain(value):
    """A string, a boolean, a number, or an array of them."""
    if isinstance(value, str):
        return _string(value)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        return "[" + ", ".join(_plain(item) for item in value) + "]"
    if not isinstance(value, (int, float)):
        raise repo.KbError(f"no rendering of {value!r}", code=3)
    return repr(value)


def _entry_value(key, value):
    if key in ENTRY_ADDRESSES:
        return _address(value)
    if key == "pointer_bindings":
        return "[" + ", ".join(_pointer(item) for item in value) + "]"
    return _plain(value)


def _pointer(item):
    parts = [f"site = {_address(item['site'])}", f"accessor = {_address(item['accessor'])}"]
    if item.get("offset"):
        parts.append(f"offset = 0x{item['offset']:X}")
    return "{ " + ", ".join(parts) + " }"


# Projections ---------------------------------------------------------------

# Target images in the order of the registry files: the table registry holds
# the VQ37VHR images and the 8MFK images, the fuel-cut registry the VQ37VHR
# images.
FUEL_CUT_TARGETS = ("JK78C", "1ND0A", "1ND3B", "1ME3B")
TARGETS = (*FUEL_CUT_TARGETS, "JK00C", "JK00D")
# The meaning of the symbol at each fuel-cut key; the axis is the x axis of
# the curves.
FUEL_CUT_MEANINGS = (("function_address", "rev_fuel_cut_state_machine/fn"),
                     ("coordinator_address", "fuel_cut_coordinator/fn"),
                     ("selector_address", "rev_fuel_cut_selector/ram"),
                     ("rpm_address", "rpm/ram"),
                     ("state_address", "rev_fuel_cut_state/ram"),
                     ("delay_address", "rev_fuel_cut_delay/ram"),
                     ("delay_calibration_address", "rev_limit_fuel_cut_delay_calibration/tbl"),
                     ("caps_address", "rev_limit_fuel_cut_caps/tbl"),
                     ("curves_address", "rev_limit_fuel_cut_curves/tbl"))
# The registry spelling of a kb storage.
STORAGE_TYPES = {storage: registry for registry, storage in vocab.STORAGE_ALIASES.items()}


def tables(root=repo.ROOT):
    """The text of `defs/vq37-native-tables.toml` from the model."""
    from kb import compile
    return render_tables(tables_document(compile.cached(root)))


def fuel_cut(root=repo.ROOT):
    """The text of `defs/vq37-native-fuel-cut.toml` from the model."""
    from kb import compile
    return render_fuel_cut(fuel_cut_document(compile.cached(root)))


def targets(model, roms=TARGETS):
    """(ROM, layout, image) of each target image of the table registry, or of
    the images that `roms` names."""
    catalog = repo.images(model.root)
    layout_of = {rom: layout.id for layout in model.layouts.values() for rom in layout.images}
    return [(rom, layout_of[rom], catalog[rom]) for rom in roms]


def meanings(model):
    """The meanings of the native tables: the `tbl` and `axis` meanings with
    `[editor]` whose home is the layout of a target."""
    layouts = {layout for _, layout, _ in targets(model)}
    return [meaning for meaning in model.meanings
            if meaning.kind in KINDS.values() and meaning.home in layouts
            and ("editor" in meaning.props
                 or any("editor" in symbol.props for symbol in meaning.symbols.values()))]


def file_notes(model, chosen):
    """{symbol key: notes} that the files of the chosen meanings state for their
    symbols."""
    paths = {id(meaning): Path(src) for meaning, src in model.files.values()
             if meaning is not None}
    found = {}
    for meaning in chosen:
        if id(meaning) not in paths:
            continue
        for entry in store.load(model.root, paths[id(meaning)], model.overlay).get("symbol", ()):
            note = entry.get("note")
            if note:
                key = (entry["layout"], meaning.kind, int(entry["address"], 16))
                found[key] = note if isinstance(note, list) else [note]
    return found


def _site(item, layout):
    """The address of an evidence item on a layout, or None elsewhere."""
    at = item.get("at")
    if not isinstance(at, str) or not at.startswith(f"{layout}:"):
        return None
    return int(at.split(":", 1)[1], 16)


def _note(notes, carriers, rom, subject):
    """The note of one image from the notes of its symbol: the text after the
    image's name where the notes name the images, and otherwise the one note."""
    named = [text for text in notes
             if any(text.startswith(f"{image}: ") for image in carriers)]
    texts = ([text.removeprefix(f"{rom}: ") for text in named if text.startswith(f"{rom}: ")]
             if named else list(notes))
    if len(named) not in (0, len(notes)) or len(texts) > 1:
        raise repo.KbError(f"{subject}: the notes of the symbol give {rom} no single note",
                           code=3)
    return texts[0] if texts else None


def _axis(meaning, layout, slot, subject):
    """The axis symbol of a slot on a layout, or None."""
    found = [link.to.symbols[layout] for link in meaning.links
             if link.type == "axis" and link.slot == slot and layout in link.stated
             and layout in link.to.symbols]
    if len(found) > 1:
        raise repo.KbError(f"{subject}: {len(found)} axes of slot {slot} on {layout}", code=3)
    return found[0] if found else None


def _accessor_bindings(meaning, layout, subject):
    """The pointer bindings of a table on a layout: the evidence of its reader
    links with the role `accessor`, by site and offset."""
    found = []
    for link in meaning.links:
        if link.type != "reader" or "accessor" not in link.roles:
            continue
        for item in link.evidence:
            site = _site(item, layout)
            if site is None:
                continue
            accessor = link.to.symbols.get(layout)
            if accessor is None:
                raise repo.KbError(f"{subject}: the accessor {link.to.key} has no symbol on "
                                   f"{layout}", code=3)
            binding = {"site": site, "accessor": accessor.address}
            if item.get("kind") == "indirect":
                binding["offset"] = item["value"]
            found.append(binding)
    return sorted(found, key=lambda item: (item["site"], item.get("offset", 0)))


def _table_entry(meaning, symbol, rom, image, notes, carriers):
    """The entry of a symbol for one image of the images that carry it."""
    subject = f"target.{rom}.{meaning.name}"
    entry = {"id": meaning.name, "address": symbol.address}
    for name, source in GEOMETRY[symbol.kind] + SYMBOL_KEYS[symbol.kind]:
        value = symbol.value(name)
        if value is not None:
            entry[source] = value
    storage = symbol.value("storage")
    entry["storagetype"] = STORAGE_TYPES.get(storage, storage)
    entry["values_sha256"] = _digest(symbol.kind, entry, image)
    bindings = _accessor_bindings(meaning, symbol.layout, subject)
    if bindings:
        entry["pointer_bindings"] = bindings
    for slot in ("x", "y"):
        axis = _axis(meaning, symbol.layout, slot, subject)
        if axis is not None:
            entry[f"axis_{slot}"] = axis.address
    editor = symbol.value("editor") or {}
    entry.update({name: editor[name] for name in EDITOR if name in editor})
    note = _note(notes.get((symbol.layout, symbol.kind, symbol.address), ()), carriers, rom,
                 subject)
    if note is not None:
        entry["note"] = note
    return entry


def tables_document(model, notes=None):
    """The document of `defs/vq37-native-tables.toml`: for each target, an
    entry of every native meaning with a symbol on its layout that the image
    carries and whose effective editor policy permits publication, by address,
    and the native meanings absent there, by name.
    `notes` gives the notes of the symbols, by default those of the files."""
    chosen = meanings(model)
    notes = file_notes(model, chosen) if notes is None else notes
    layout_images = {layout.id: layout.images for layout in model.layouts.values()}
    document = {"schema_version": SCHEMA_VERSIONS[TABLES], "target": {}}
    for rom, layout, image in targets(model):
        target = {"stock_sha256": image.sha256}
        for name, kind in KINDS.items():
            entries = []
            for meaning in chosen:
                symbol = meaning.symbols.get(layout)
                if meaning.kind != kind or symbol is None:
                    continue
                if (symbol.value("editor") or {}).get("emit", True) is False:
                    continue
                carriers = symbol.props.get("images") or list(layout_images[layout])
                if rom not in carriers:
                    continue
                entries.append(_table_entry(meaning, symbol, rom, image, notes, carriers))
            if entries:
                target[name] = sorted(entries, key=lambda entry: entry["address"])
        absent = {}
        for meaning in chosen:
            status = meaning.statuses.get(layout)
            if status is not None and status.state == "absent":
                absent[meaning.name] = status.props["note"]
        if absent:
            target["absent"] = dict(sorted(absent.items()))
        document["target"][rom] = target
    return document


def fuel_cut_document(model):
    """The document of `defs/vq37-native-fuel-cut.toml`: for each target, the
    fuel-cut symbols of its layout, the call and the scheduler word from their
    evidence, the values from the image, and the pointer bindings from the
    evidence of the reader links to the predicate function."""
    by_key = {meaning.key: meaning for meaning in model.meanings}
    document = {"schema_version": SCHEMA_VERSIONS[FUEL_CUT], "target": {}}
    for rom, layout, image in targets(model, FUEL_CUT_TARGETS):
        subject = f"target.{rom}"
        found = {}
        for name, key in FUEL_CUT_MEANINGS:
            meaning = by_key.get(key)
            symbol = meaning.symbols.get(layout) if meaning is not None else None
            if symbol is None:
                raise repo.KbError(f"{subject}: {key} has no symbol on {layout}", code=3)
            found[name] = symbol
        function, coordinator = found["function_address"], found["coordinator_address"]
        axis = _axis(found["curves_address"].meaning, layout, "x", subject)
        if axis is None:
            raise repo.KbError(f"{subject}: the curves have no x axis on {layout}", code=3)
        found["axis_address"] = axis
        calls = [item for item in function.evidence if item.get("kind") == "l0"
                 and isinstance(item.get("value"), int) and _site(item, layout) is not None]
        words = [item for item in coordinator.evidence if item.get("kind") == "rom-bytes"
                 and item.get("value") == f"{coordinator.address:08x}"
                 and _site(item, layout) is not None]
        if len(calls) != 1 or len(words) != 1:
            raise repo.KbError(f"{subject}: {len(calls)} predicate calls and {len(words)} "
                               "scheduler words on the layout", code=3)
        [call], [word] = calls, words
        site = _site(call, layout)
        size, digest = repo.signatures(layout, model.root)[function.address]
        masks = {item["name"]: 1 << item["bit"] for item in found["state_address"].value("bit")}
        data = _image(image.path)
        values = {}
        for name, key, _ in FUEL_CUT_DATA:
            symbol = found[name]
            count = (symbol.value("points") if symbol.kind == "axis"
                     else symbol.value("cols") * symbol.value("rows"))
            values[key] = _values(data, symbol.address, symbol.value("storage"), count)
        target = {"stock_sha256": image.sha256, "function_size": size,
                  "function_sha256": digest,
                  "coordinator_pointer_site": _site(word, layout),
                  "coordinator_predicate_ordinal": call["value"],
                  "predicate_call_site": site,
                  "predicate_instruction_ordinal": (site - coordinator.address) // 2,
                  "state_active_mask": masks["active"], "state_armed_mask": masks["armed"],
                  **{name: symbol.address for name, symbol in found.items()},
                  **values, "delay_calibration_value": values["delay_calibration_value"][0],
                  **_function_bindings(model, function, layout, data),
                  "evidence": call["note"]}
        document["target"][rom] = target
    return document


def _function_bindings(model, function, layout, data):
    """The pointer bindings of the predicate function on a layout: the evidence
    of the reader links to its meaning without a role, by site. A ROM pointer
    takes its target from the stock word at the site, which may address a row
    inside the storage of the owner."""
    found = {name: [] for name in BINDINGS}
    for link in model.links:
        if link.type != "reader" or link.to is not function.meaning or link.roles:
            continue
        group = next(name for name, kinds in BINDINGS.items() if link.owner.kind in kinds)
        for item in link.evidence:
            site = _site(item, layout)
            if site is None:
                continue
            symbol = link.owner.symbols[layout]
            target = symbol.address
            if group == "pointer_bindings":
                target = int.from_bytes(data[site:site + 4], "big")
                size = match.storage_size(symbol) or 1
                if not symbol.address <= target < symbol.address + size:
                    raise repo.KbError(f"the word {target:08x} at {layout}:{site:08x} lies "
                                       f"outside the storage of {link.owner.key}", code=3)
            found[group].append({"site": site, "target": target})
    return {name: sorted(items, key=lambda item: item["site"]) for name, items in found.items()}
