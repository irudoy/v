"""VQ37VHR native registries (tools/kb/SPEC.md, section 20.4).

- Each table and axis entry of `defs/vq37-native-tables.toml` gives a `tbl`
  or `axis` symbol on the layout of its target image, and its id joins the
  symbols of every target into one meaning with the strength of a native
  table id and names it. The meaning takes `home` and `summary` from the
  first target that carries the id. Geometry, scale, level, and `[editor]`
  are keys of the symbol, which the meaning lifts from its home symbol. The
  `semantics` of another target, where it differs from the summary, and
  `note` become notes of the symbol, each prefixed with its image where the
  images of one layout state different text. An entry that only some images
  of a layout carry gives the symbol `images`.
- A pointer binding gives the symbol `l0` evidence at its site, or `indirect`
  evidence with mode `base` and the offset as `value` where the accessor
  displaces the literal, and a `reader` link to the accessor with the same
  evidence. `axis_x` and `axis_y` give `axis` links.
- `[target.<ROM>.absent]` gives the meaning of each id the status `absent`
  with `l0` evidence at each function entry of the layout that its text
  names, or else `registry` evidence.
- Each target of `defs/vq37-native-fuel-cut.toml` gives the `fn`, `ram`,
  `tbl`, and `axis` symbols of its fuel-cut mechanism, joined across targets
  by registry key, and the state byte names its armed and active bits. The
  call site gives the predicate function `l0` evidence with the instruction
  ordinal as `value` and the target's `evidence` as `note`; the scheduler
  word gives the coordinator `l0` evidence. Each pointer binding gives the
  symbol at its target `l0` evidence at its site and a `reader` link to the
  predicate function. The function size and digest must equal L0.
- The stock digest of every target must equal the image catalog.
"""

from collections import defaultdict
from pathlib import Path
import re
import tomllib

from kb import repo, vocab

TABLES = Path("defs/vq37-native-tables.toml")
FUEL_CUT = Path("defs/vq37-native-fuel-cut.toml")
SCHEMA_VERSIONS = {TABLES: 3, FUEL_CUT: 1}
KINDS = {"table": "tbl", "axis": "axis"}
EDITOR = ("name", "category", "order", "format", "fine", "coarse", "mask", "static_axis",
          "static_axis_name")
# Symbol keys and the entry keys that state them.
GEOMETRY = {"tbl": (("cols", "width"), ("rows", "height")),
            "axis": (("points", "length"), ("quantity", "kind"))}
SCALE = (("unit", "units"), ("scale", "scale_expr"), ("to_raw", "to_byte"),
         ("scale_level", "scale_conf"), ("level", "confidence"))
PROSE = ("semantics", "note")
ENTRY_KEYS = frozenset({"id", "address", "width", "height", "length", "kind", "storagetype",
                        "values_sha256", "pointer_bindings", "axis_x", "axis_y", *PROSE,
                        *EDITOR, *(source for _, source in SCALE)})
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
        _declare_id(b, src, kind, name, entries, pending)
    for rom, layout, target in targets:
        for name, text in target.get("absent", {}).items():
            subject = f"target.{rom}.absent.{name}"
            if len(kinds.get(name, ())) != 1:
                b.issue("schema", src, subject, "no single table or axis of a target carries "
                        "the id")
                continue
            _declare_absent(b, src, subject, (*kinds[name], "native", name), layout, text)


def _declare_id(b, src, kind, name, entries, pending):
    group = (kind, "native", name)
    _, home, first = entries[0]
    summary = first.get("semantics")
    b.name(group, name, "native", src)
    b.props(group, {"home": home, "summary": summary}, src)
    carried = defaultdict(list)
    for rom, layout, entry in entries:
        carried[(layout, entry["address"])].append((rom, entry))
    for (layout, address), images in carried.items():
        own = [rom for rom, _ in images]
        props = {"note": _notes(images, summary)}
        if set(own) != set(b.layouts[layout].images):
            props["images"] = [rom for rom in b.layouts[layout].images if rom in own]
        key = b.symbol(layout, kind, address, src, group=group, props=props, strength="native")
        for rom, entry in images:
            b.keys(key, _keys(kind, entry), src)
            for binding in entry.get("pointer_bindings", ()):
                item = _binding(layout, binding)
                b.symbol(layout, kind, address, src, evidence=[item])
                pending.append(("reader", key, binding["accessor"], item, src))
            for slot in ("x", "y"):
                if f"axis_{slot}" in entry:
                    pending.append(("axis", key, slot, entry[f"axis_{slot}"], src))


def _keys(kind, entry):
    keys = {name: entry.get(source) for name, source in GEOMETRY[kind] + SCALE}
    keys["storage"] = vocab.storage(entry.get("storagetype"))
    editor = {name: entry[name] for name in EDITOR if name in entry}
    if editor:
        keys["editor"] = editor
    return {name: value for name, value in keys.items() if value not in (None, "")}


def _notes(images, summary):
    """Notes of one symbol from the prose of its images: a text that every
    image states alike once, and otherwise each image's text after its name."""
    notes = []
    for field in PROSE:
        texts = [(rom, entry.get(field)) for rom, entry in images]
        if field == "semantics":
            texts = [(rom, None if text == summary else text) for rom, text in texts]
        if len({text for _, text in texts}) == 1:
            notes.extend(text for _, text in texts[:1] if text)
        else:
            notes.extend(f"{rom}: {text}" for rom, text in texts if text)
    return notes


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
    for rom, layout, target in _targets(b, src, document, catalog, FUEL_CUT_KEYS):
        subject = f"target.{rom}"
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
        b.symbol(layout, "fn", function.address, src, evidence=[{
            "kind": "l0", "supports": "identity",
            "at": _location(layout, target["predicate_call_site"]),
            "value": target["predicate_instruction_ordinal"], "path": src, "key": subject,
            "note": target["evidence"]}])
        b.symbol(layout, "fn", target["coordinator_address"], src, evidence=[{
            "kind": "l0", "supports": "identity",
            "at": _location(layout, target["coordinator_pointer_site"])}])
        for name, kinds in BINDINGS.items():
            for binding in target.get(name, ()):
                item = {"kind": "l0", "supports": "identity",
                        "at": _location(layout, binding["site"])}
                pending.append(("binding", layout, binding["target"], kinds, function, item,
                                src))


# Relations -----------------------------------------------------------------

def relate(b, root):
    for entry in b.stash.get(__name__, ()):
        if entry[0] == "reader":
            _, key, accessor, item, src = entry
            to = b.resolve(key.layout, accessor, ("fn",), src)
            if to is None:
                b.issue("references", src, key.key, f"accessor {accessor:08x} is no function "
                        "entry")
                continue
            b.link(key, "reader", to, src, props={"role": "accessor"}, evidence=[item])
        elif entry[0] == "axis":
            _, key, slot, address, src = entry
            to = b.resolve(key.layout, address, ("axis",), src)
            if to is None:
                b.issue("references", src, key.key, f"axis_{slot} {address:08x} is no axis")
                continue
            b.link(key, "axis", to, src, props={"slot": slot})
        else:
            _, layout, address, kinds, function, item, src = entry
            datum = b.resolve(layout, address, kinds, src)
            if datum is None:
                b.issue("references", src, _location(layout, address),
                        f"a pointer binding of {function.key} names no {'/'.join(kinds)}")
                continue
            b.symbol(layout, datum.kind, datum.address, src, evidence=[item])
            b.link(datum, "reader", function, src, evidence=[item])
