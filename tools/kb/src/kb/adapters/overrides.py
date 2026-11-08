"""The JK08A presentation layer of the editor definitions (tools/kb/SPEC.md,
section 7.8).

`tools/kb/projections.toml` registers the generated presentation registry.

- `[table.<address>]` and `[axis.<address>]` give `[editor]` of the `7mfk`
  `tbl` or `axis` symbol at the address, a key that the meaning lifts from
  its home symbol. `static_axis_operand` names the `ram` or `reg` meaning
  whose value the static axis labels.
- Each `[[masked_view]]` gives an entry of `[[editor.view]]` of the table at
  its `source`, with `units`, `expression`, and `to_byte` as `unit`, `scale`,
  and `to_raw`.
- `[logparam.<address>]` gives `[logparam]` of the `ram` or `reg` symbol at
  the address, with `units` as `unit`.
- An address without a symbol of its kind fails the `references` check, and a
  key outside the table of section 7.8 fails the `schema` check.
- `[presentation]` gives `default_emit` of the `definitions` feature, and each
  `[[switch]]` without its storage address an entry of its `switches`, under
  the slug that `SWITCH_NAMES` of `tools/mapkit/definition_projections.py`
  gives its name, with its position among the switches as `order`. The
  module is read with `ast`, not imported.
- The JK08A entry in `images` of the `definitions` target of `7mfk` takes the
  keys of a projection entry: `[rom]` as `rom` with its comment as `note`,
  `[[checksum]]` as `checksums` with each `comment` as `note`, the storage
  address of each switch under `switch`, and `enabled` of `[map_switching]`
  and `[rolling_launch]` as `map_switching` and `rolling_launch`. A note is
  one paragraph. These keys replace those of the entity files, and the entry
  keeps the other keys of the files, as `basis`.

From stage 4 the file is a projection of the `[editor]` and `[logparam]`
tables of the `7mfk` symbols and of `definitions` (`presentation`): the
sections of the feature and of the image, `[logparam.<address>]` by address,
the switches by `order`, `[table.<address>]` by `order` of the editor and by
address with the masked views of each table after it, and `[axis.<address>]`
by address. `static_axis_operand` names the address of the `7mfk` symbol of
its meaning; a note, wrapped as the definition projections wrap theirs,
becomes the `comment` of its checksum and the `text` of the ROM comment; and
the file has no other comments than its header.
"""

import ast
from decimal import Decimal
from pathlib import Path
import textwrap
import tomllib

from kb import repo, store, vocab
from kb.model import SymbolKey
from kb.repo import KbError
from kb.values import hexed

OVERRIDES = Path("defs/JK08A.overrides.toml")
PROJECTIONS = Path("tools/mapkit/definition_projections.py")
ROM = "JK08A"
CANONICAL = "7mfk"
FEATURE = "definitions"
KINDS = {"table": "tbl", "axis": "axis"}
FEATURES = ("map_switching", "rolling_launch")
DOCUMENT_KEYS = frozenset({*KINDS, *FEATURES, "presentation", "masked_view", "logparam", "rom",
                           "checksum", "switch"})
PRESENTATION_KEYS = frozenset({"default_emit"})
FEATURE_KEYS = frozenset({"enabled"})
# Registry spellings of keys of section 7.8.
VIEW_NAMES = {"units": "unit", "expression": "scale", "to_byte": "to_raw"}
LOGPARAM_NAMES = {"units": "unit"}
OPERAND = "static_axis_operand"
DATA_KINDS = ("ram", "reg")
CHECKSUM_KEYS = frozenset({"type", "path", "expectedsize", "start", "end", "skiploc", "sumloc",
                           "xorloc", "comment"})
CHECKSUM_ADDRESSES = ("start", "end", "skiploc", "sumloc", "xorloc")
SWITCH_KEYS = frozenset({"name", "category", "storageaddress", "storagetype", "sizex", "sizey",
                         "endian", "userlevel", "description", "state"})
SWITCH_ADDRESS = "storageaddress"


def inputs(root):
    return [OVERRIDES.as_posix(), PROJECTIONS.as_posix()]


def switch_names(root):
    """{name: slug} of the switches that a projection may relocate."""
    tree = ast.parse((root / PROJECTIONS).read_text(encoding="utf-8"))
    for node in tree.body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "SWITCH_NAMES"):
            return {name: slug for slug, name in ast.literal_eval(node.value).items()}
    return {}


def declare(b, root):
    declare_overrides(b, tomllib.loads((root / OVERRIDES).read_text(encoding="utf-8")),
                      switch_names(root), OVERRIDES.as_posix())


def declare_overrides(b, document, names, src):
    """The keys of `definitions`; the tables of meanings wait in the stash
    for `relate`, when every symbol is declared."""
    for name in sorted(set(document) - DOCUMENT_KEYS):
        b.issue("schema", src, name, "unknown key")
    presentation = document.get("presentation", {})
    for name in sorted(set(presentation) - PRESENTATION_KEYS):
        b.issue("schema", src, f"presentation.{name}", "unknown key")
    switches, addresses = {}, {}
    for index, item in enumerate(document.get("switch", ())):
        subject = f"switch.{item.get('name', index)}"
        slug = names.get(item.get("name"))
        if slug is None:
            b.issue("schema", src, subject, f"no slug of SWITCH_NAMES in {PROJECTIONS}")
            continue
        for name in sorted(set(item) - SWITCH_KEYS):
            b.issue("schema", src, subject, f"unknown key {name}")
        switches[slug] = {"order": index + 1, **{
            name: value for name, value in item.items()
            if name in SWITCH_KEYS and name != SWITCH_ADDRESS}}
        addresses[slug] = hexed(_number(item.get(SWITCH_ADDRESS)))
    b.entity("feature", FEATURE, src, props={"default_emit": presentation.get("default_emit"),
                                            "switches": switches})
    entry = {"rom": {name: value for name, value in document.get("rom", {}).items()
                     if name != "comment"},
             "note": _paragraph(document.get("rom", {}).get("comment", {}).get("text", "")),
             "checksums": [_checksum(b, src, index, item)
                           for index, item in enumerate(document.get("checksum", ()))],
             "switch": addresses}
    for feature in FEATURES:
        table = document.get(feature, {})
        for name in sorted(set(table) - FEATURE_KEYS):
            b.issue("schema", src, f"{feature}.{name}", "unknown key")
        entry[feature] = table.get("enabled")
    target = b.target(FEATURE, CANONICAL, src, status="supported")
    images = target.props.setdefault("images", {})
    images[ROM] = {**images.get(ROM, {}), **{name: value for name, value in entry.items()
                                             if value not in (None, "", [], {})}}
    b.stash[__name__] = (src, document)


def _number(value):
    return int(value, 16) if isinstance(value, str) else value


def _checksum(b, src, index, item):
    for name in sorted(set(item) - CHECKSUM_KEYS):
        b.issue("schema", src, f"checksum.{index}", f"unknown key {name}")
    found = {name: hexed(_number(value)) if name in CHECKSUM_ADDRESSES else value
             for name, value in item.items() if name in CHECKSUM_KEYS - {"comment"}}
    if item.get("comment", "").strip():
        found["note"] = _paragraph(item["comment"])
    return found


def _paragraph(text):
    return " ".join(text.split())


def relate(b, root):
    src, document = b.stash.get(__name__, (OVERRIDES.as_posix(), {}))
    editors = {}
    for section, kind in KINDS.items():
        for text, item in document.get(section, {}).items():
            subject = f"{section}.{text}"
            key = _symbol(b, src, subject, text, (kind,))
            if key is None:
                continue
            editor = {}
            for name, value in item.items():
                if name not in vocab.EDITOR_KEYS:
                    b.issue("schema", src, subject, f"unknown key {name}")
                    continue
                editor[name] = value
            if OPERAND in editor:
                editor[OPERAND] = _operand(b, src, subject, editor[OPERAND])
            editors[key] = {name: value for name, value in editor.items() if value is not None}
    for index, item in enumerate(document.get("masked_view", ())):
        subject = f"masked_view.{item.get('name', index)}"
        key = _symbol(b, src, subject, item.get("source", ""), ("tbl", "const"))
        if key is None:
            continue
        view = {}
        for name, value in item.items():
            name = VIEW_NAMES.get(name, name)
            if name == "source":
                continue
            if name not in vocab.VIEW_KEYS:
                b.issue("schema", src, subject, f"unknown key {name}")
                continue
            view[name] = value
        editors.setdefault(key, {}).setdefault("view", []).append(view)
    for key, editor in editors.items():
        b.keys(key, {"editor": editor}, src)
    for text, item in document.get("logparam", {}).items():
        subject = f"logparam.{text}"
        key = _symbol(b, src, subject, text, DATA_KINDS)
        if key is None:
            continue
        logparam = {}
        for name, value in item.items():
            name = LOGPARAM_NAMES.get(name, name)
            if name not in vocab.LOGPARAM_KEYS:
                b.issue("schema", src, subject, f"unknown key {name}")
                continue
            logparam[name] = value
        b.keys(key, {"logparam": logparam}, src)


def _symbol(b, src, subject, text, kinds):
    """The declared `7mfk` symbol of one of `kinds` at an address."""
    try:
        address = int(text, 16)
    except ValueError:
        b.issue("schema", src, subject, f"address {text!r}")
        return None
    present = {key.kind for key in b.at(CANONICAL, address)}
    kind = next((kind for kind in kinds if kind in present), None)
    if kind is None:
        b.issue("references", src, subject, f"no {' or '.join(kinds)} symbol of {CANONICAL} at "
                f"{address:08x}")
        return None
    return b.symbol(CANONICAL, kind, address, src)


def _operand(b, src, subject, text):
    key = b.resolve(CANONICAL, int(text, 16), DATA_KINDS, src)
    if key is None:
        b.issue("references", src, subject, f"{OPERAND} {text} is no RAM or register address "
                f"of {CANONICAL}")
    return key


# Projection ----------------------------------------------------------------

HEADER = """\
# JK08A definition presentation layer: names, categories, ordering, editor steps,
# and the ROM identification block. Facts such as address, shape, element, axes,
# scaling, and confidence do not belong here. The graph carries them, and sources
# diverge precisely when one fact is declared twice.
#
# Read by tools/mapkit/emit_def.py for both RomRaider XML and TunerPro XDF. The
# merge key is the graph map or axis address: eight lowercase hexadecimal digits.
"""
# The file spellings of the keys of section 7.8.
VIEW_SPELLINGS = {name: spelling for spelling, name in VIEW_NAMES.items()}
LOGPARAM_SPELLINGS = {name: spelling for spelling, name in LOGPARAM_NAMES.items()}
# The keys of each table of the file: those of section 7.8 in its order, and
# the others in the order of the editor definitions.
TABLE_ORDER = vocab.EDITOR_KEYS
VIEW_ORDER = ("source", *(VIEW_SPELLINGS.get(name, name) for name in vocab.VIEW_KEYS))
LOGPARAM_ORDER = tuple(LOGPARAM_SPELLINGS.get(name, name) for name in vocab.LOGPARAM_KEYS)
ROM_ORDER = ("xmlid", "internalidaddress", "internalidstring", "ecuid", "caseid", "make",
             "model", "submodel", "market", "transmission", "memmodel", "endian", "filesize",
             "author", "version")
CHECKSUM_ORDER = ("type", "path", "expectedsize", "start", "end", "skiploc", "sumloc", "xorloc",
                  "comment")
SWITCH_ORDER = ("name", "category", "storageaddress", "storagetype", "sizex", "sizey", "endian",
                "userlevel", "description", "state")
STATE_ORDER = ("name", "data")
# An array whose line would be wider holds eight items on each line.
WIDTH = 80
ROW = 8
# The width of the lines of a note, that of the definition projections.
NOTE_WIDTH = 79
# The place of a table without an editor order.
LAST = 1 << 20


def presentation_document(model):
    """The document of the file from the `definitions` feature, its `7mfk`
    target, and the `[editor]` and `[logparam]` tables of the `7mfk`
    symbols."""
    feature = model.entities.get(("feature", FEATURE))
    target = model.targets.get((FEATURE, CANONICAL))
    image = (target.props.get("images") or {}).get(ROM) if target is not None else None
    if feature is None or image is None:
        raise KbError(f"the model holds no {FEATURE} feature with the {ROM} image of its "
                      f"{CANONICAL} target", code=3)
    document = {"presentation": {"default_emit": feature.props.get("default_emit")}}
    for name in FEATURES:
        if name in image:
            document[name] = {"enabled": image[name]}
    logparams, tables, axes = {}, [], {}
    for key, symbol in sorted(model.symbols.items()):
        if key.layout != CANONICAL:
            continue
        logparam = symbol.value("logparam") if key.kind in DATA_KINDS else None
        if logparam:
            logparams[f"{key.address:08x}"] = {LOGPARAM_SPELLINGS.get(name, name): value
                                               for name, value in logparam.items()}
        editor = symbol.value("editor")
        if not editor:
            continue
        if key.kind not in KINDS.values():
            raise KbError(f"{key.key}: the file holds no editor of a {key.kind}", code=3)
        entry = {name: _address(model, key, value) if name == OPERAND else value
                 for name, value in editor.items() if name != "view"}
        if key.kind == "axis":
            axes[f"{key.address:08x}"] = entry
        else:
            tables.append((entry.get("order", LAST), key.address, entry, editor.get("view", ())))
    document["logparam"] = logparams
    rom = dict(image.get("rom") or {})
    if image.get("note"):
        rom["comment"] = {"text": _wrapped(image["note"])}
    document["rom"] = rom
    document["checksum"] = [_checksum_entry(item) for item in image.get("checksums", ())]
    document["switch"] = _switches(feature, image)
    document["table"], document["masked_view"] = {}, []
    for _, address, entry, views in sorted(tables, key=lambda item: item[:2]):
        document["table"][f"{address:08x}"] = entry
        document["masked_view"] += [{"source": f"{address:08x}", **{
            VIEW_SPELLINGS.get(name, name): value for name, value in view.items()}}
            for view in views]
    document["axis"] = axes
    return document


def _address(model, key, operand):
    """The address of the `7mfk` symbol of the meaning of an operand."""
    meaning = model.meaning_of(operand) if isinstance(operand, SymbolKey) else None
    symbol = meaning.symbols.get(CANONICAL) if meaning is not None else None
    if symbol is None:
        raise KbError(f"{key.key}: {OPERAND} {operand} names no meaning with a {CANONICAL} "
                      "symbol", code=3)
    return f"{symbol.address:08x}"


def _checksum_entry(item):
    found = {}
    for name, value in item.items():
        if name == "note":
            found["comment"] = _wrapped(value)
        elif name in CHECKSUM_ADDRESSES:
            found[name] = f"0x{int(value, 16):X}"
        else:
            found[name] = value
    return found


def _wrapped(note):
    return textwrap.fill(note, NOTE_WIDTH, break_long_words=False,
                         break_on_hyphens=False) + "\n"


def _switches(feature, image):
    """The switches by `order`, each with the storage address of the image."""
    switches = feature.props.get("switches") or {}
    addresses = image.get("switch") or {}
    found = []
    for slug in sorted(switches, key=lambda slug: (switches[slug].get("order", LAST), slug)):
        if slug not in addresses:
            raise KbError(f"the {ROM} image names no address of the switch {slug}", code=3)
        entry = {name: value for name, value in switches[slug].items() if name != "order"}
        entry[SWITCH_ADDRESS] = f"0x{int(addresses[slug], 16):05X}"
        found.append(entry)
    return found


def _scalar(value, subject):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return format(Decimal(repr(value)), "f")
    if isinstance(value, str):
        return f'"{store.escape(value)}"'
    raise KbError(f"{subject}: no presentation form of {value!r}", code=3)


def _inline(item, subject):
    unknown = sorted(set(item) - set(STATE_ORDER))
    if unknown:
        raise KbError(f"{subject}: no presentation form of {unknown}", code=3)
    return "{ " + ", ".join(f"{key} = {_scalar(item[key], subject)}"
                            for key in STATE_ORDER if key in item) + " }"


def _lines(key, value, subject):
    """The lines of one key: a string with newlines as a multiline string, an
    array of tables with one inline table on each line, and an array of
    values on one line or with eight values on each line."""
    if isinstance(value, str) and "\n" in value:
        body = value.replace("\\", "\\\\").replace('"""', '""\\"')
        return [f'{key} = """\n{body}"""']
    if isinstance(value, list):
        if value and all(isinstance(item, dict) for item in value):
            return [f"{key} = ["] + [f"  {_inline(item, subject)}," for item in value] + ["]"]
        items = [_scalar(item, subject) for item in value]
        line = f"{key} = [{', '.join(items)}]"
        if len(line) <= WIDTH:
            return [line]
        return [f"{key} = ["] + ["  " + ", ".join(items[start:start + ROW]) + ","
                                 for start in range(0, len(items), ROW)] + ["]"]
    return [f"{key} = {_scalar(value, subject)}"]


def _block(header, item, order, subject):
    """The lines of one table of the file with the keys of `order`."""
    unknown = sorted(set(item) - set(order))
    if unknown:
        raise KbError(f"{subject}: no presentation form of {unknown}", code=3)
    return "\n".join([header] + [line for key in order if key in item
                                 for line in _lines(key, item[key], subject)])


def render_presentation(document):
    """The text of `defs/JK08A.overrides.toml` from its document."""
    blocks = [HEADER + "\n" + _block("[presentation]", document.get("presentation", {}),
                                     tuple(PRESENTATION_KEYS), "presentation")]
    blocks += [_block(f"[{name}]", document[name], tuple(FEATURE_KEYS), name)
               for name in FEATURES if name in document]
    blocks += [_block(f"[logparam.{address}]", item, LOGPARAM_ORDER, f"logparam.{address}")
               for address, item in document.get("logparam", {}).items()]
    rom = dict(document.get("rom", {}))
    comment = rom.pop("comment", None)
    blocks.append(_block("[rom]", rom, ROM_ORDER, "rom"))
    if comment is not None:
        blocks.append(_block("[rom.comment]", comment, ("text",), "rom.comment"))
    blocks += [_block("[[checksum]]", item, CHECKSUM_ORDER, f"checksum.{index}")
               for index, item in enumerate(document.get("checksum", ()))]
    blocks += [_block("[[switch]]", item, SWITCH_ORDER, f"switch.{item.get('name')}")
               for item in document.get("switch", ())]
    views = {}
    for item in document.get("masked_view", ()):
        views.setdefault(item.get("source"), []).append(item)
    for address, item in document.get("table", {}).items():
        blocks.append(_block(f"[table.{address}]", item, TABLE_ORDER, f"table.{address}"))
        blocks += [_block("[[masked_view]]", view, VIEW_ORDER, f"masked_view.{view.get('name')}")
                   for view in views.pop(address, ())]
    if views:
        raise KbError(f"masked views of no table: {', '.join(sorted(views))}", code=3)
    blocks += [_block(f"[axis.{address}]", item, TABLE_ORDER, f"axis.{address}")
               for address, item in document.get("axis", {}).items()]
    return "\n\n".join(blocks) + "\n"


def dropped(text, rendered):
    """([(line, comment)] of the comments of `text` that `rendered` lacks,
    [(key, text before, text after)] of the notes that `rendered` wraps
    anew); a rendering that parses to another document than `text` beyond
    the wrapping of its notes refuses."""
    held, found = tomllib.loads(text), tomllib.loads(rendered)
    wrapped = [(key, before, after) for key, before, after in _notes(held, found)
               if before != after]
    path = _differs(_plain(held), _plain(found), ())
    if path is not None:
        raise KbError(f"the projection of {OVERRIDES.as_posix()} differs from the file at "
                      f"{'.'.join(map(str, path)) or 'its top'}", code=3)
    kept = [line for line in rendered.splitlines() if line.startswith("#")]
    comments = []
    for number, line in enumerate(text.splitlines(), 1):
        if not line.startswith("#"):
            continue
        if line in kept:
            kept.remove(line)
        else:
            comments.append((number, line))
    return comments, wrapped


def _notes(held, found):
    """[(key, text of `held`, text of `found`)] of the notes of two documents."""
    pairs = [("rom.comment.text", held.get("rom", {}).get("comment", {}).get("text"),
              found.get("rom", {}).get("comment", {}).get("text"))]
    for index, (left, right) in enumerate(zip(held.get("checksum", ()),
                                              found.get("checksum", ()))):
        pairs.append((f"checksum.{index}.comment", left.get("comment"), right.get("comment")))
    return pairs


def _plain(document):
    """A document with each note as one paragraph."""
    found = dict(document)
    comment = found.get("rom", {}).get("comment", {})
    if isinstance(comment.get("text"), str):
        found["rom"] = {**found["rom"], "comment": {**comment,
                                                    "text": _paragraph(comment["text"])}}
    found["checksum"] = [{**item, "comment": _paragraph(item["comment"])}
                         if isinstance(item.get("comment"), str) else item
                         for item in found.get("checksum", ())]
    return found


def _differs(held, found, path):
    """The key path of the first value that differs, or None."""
    if isinstance(held, dict) and isinstance(found, dict):
        for key in [*held, *(key for key in found if key not in held)]:
            if key not in held or key not in found:
                return (*path, key)
            inner = _differs(held[key], found[key], (*path, key))
            if inner is not None:
                return inner
        return None
    if isinstance(held, list) and isinstance(found, list) and len(held) == len(found):
        for index, (left, right) in enumerate(zip(held, found)):
            inner = _differs(left, right, (*path, index))
            if inner is not None:
                return inner
        return None
    return None if held == found and type(held) is type(found) else path


def presentation(root=repo.ROOT):
    """The text of `defs/JK08A.overrides.toml` from the model."""
    from kb import compile
    return render_presentation(presentation_document(compile.cached(root)))
