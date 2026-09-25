"""The JK08A presentation layer of the editor definitions (tools/kb/SPEC.md,
sections 7.8 and 20.5).

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
  gives its name. The module is read with `ast`, not imported.
- The JK08A entry in `images` of the `definitions` target of `7mfk` takes the
  keys of a projection entry: `[rom]` as `rom` with its comment as `note`,
  `[[checksum]]` as `checksums` with each `comment` as `note`, the storage
  address of each switch under `switch`, and `enabled` of `[map_switching]`
  and `[rolling_launch]` as `map_switching` and `rolling_launch`.
"""

import ast
from pathlib import Path
import tomllib

from kb import vocab
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
        switches[slug] = {name: value for name, value in item.items()
                          if name in SWITCH_KEYS and name != SWITCH_ADDRESS}
        addresses[slug] = hexed(_number(item.get(SWITCH_ADDRESS)))
    b.entity("feature", FEATURE, src, props={"default_emit": presentation.get("default_emit"),
                                            "switches": switches})
    entry = {"rom": {name: value for name, value in document.get("rom", {}).items()
                     if name != "comment"},
             "note": document.get("rom", {}).get("comment", {}).get("text", "").strip(),
             "checksums": [_checksum(b, src, index, item)
                           for index, item in enumerate(document.get("checksum", ()))],
             "switch": addresses}
    for feature in FEATURES:
        table = document.get(feature, {})
        for name in sorted(set(table) - FEATURE_KEYS):
            b.issue("schema", src, f"{feature}.{name}", "unknown key")
        entry[feature] = table.get("enabled")
    target = b.target(FEATURE, CANONICAL, src, status="supported")
    target.props.setdefault("images", {})[ROM] = {name: value for name, value in entry.items()
                                                  if value not in (None, "", [], {})}
    b.stash[__name__] = (src, document)


def _number(value):
    return int(value, 16) if isinstance(value, str) else value


def _checksum(b, src, index, item):
    for name in sorted(set(item) - CHECKSUM_KEYS):
        b.issue("schema", src, f"checksum.{index}", f"unknown key {name}")
    found = {name: hexed(_number(value)) if name in CHECKSUM_ADDRESSES else value
             for name, value in item.items() if name in CHECKSUM_KEYS - {"comment"}}
    if item.get("comment", "").strip():
        found["note"] = item["comment"].strip()
    return found


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
