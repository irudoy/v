"""Definition projections and their address correspondences
(tools/kb/SPEC.md, section 20.3).

The registries state:

- Each `[projection.<ROM>]` of `defs/definition-projections.toml` gives the
  entry of its image in `images` of the `definitions` target of the image's
  layout: the source image, both digests, the checksum and feature switches,
  the switch addresses of `[projection.<ROM>.switch]`, its `comment` as a
  `note` of one paragraph, and its `evidence` as `basis`. The digests must
  equal the image catalog, and `addresses` must name the address file of the
  layout.
- Each row of the address file that a projection names gives the symbol of
  its entity on the image's layout: `Map` a `tbl` and `Axis` an `axis`
  symbol, so an address that is both a table and an axis operand gives one of
  each. The meaning of the `7mfk` symbol at `source` enters `requires` of the
  target. A `homologous` row joins the symbol to that meaning with homology
  evidence of the kind that `function_kinds` names; a `reviewed-target` row
  joins an anchor with `l0` evidence; an `unsupported` row gives the status
  that `function_kinds` names, except that `stock-inert-path` joins the
  homologous surface that its evidence names, which `omitted` of the target
  lists. A `variant` enters `variants` of the target.

From their conversion the registries are projections of the files:

- The address file `defs/<source>-<LAYOUT>.definition-addresses.csv` of the
  `definitions` target of a layout has a row for each meaning that the
  target requires. The row item of a symbol is its first evidence item that
  is homology evidence toward the `7mfk` symbol of its meaning or `l0`
  identity evidence on its own layout. A symbol that `omitted` lists gives an
  `unsupported` row with the reason as `function_kinds`; another symbol a
  `homologous` or `reviewed-target` row with the kind of its row item as
  `function_kinds`, the instructions that touch its storage
  (`kb.match.touching`) as `sites`, and its variant; a status an
  `unsupported` row with its state. `evidence` is the note of the row item
  or of the status. Rows follow the order of entity, source, variant, and
  target.
- `defs/definition-projections.toml` has `[projection.<ROM>]` for each image
  of a `definitions` target in the order of the ROM keys, with the address
  file of its layout, its note wrapped greedily within 79 columns as
  `comment`, and its switch addresses in the order of the switches of the
  feature.
"""

import csv
import io
from pathlib import Path
import re
import textwrap
import tomllib

from kb import match, repo
from kb.model import SymbolKey
from kb.repo import KbError
from kb.values import hexed

PROJECTIONS = Path("defs/definition-projections.toml")
DEFS = Path("defs")
ADDRESSES = "JK08A-*.definition-addresses.csv"
SCHEMA_VERSION = 3
CANONICAL = "7mfk"
FEATURE = "definitions"
KINDS = {"Map": "tbl", "Axis": "axis"}
ENTITIES = {kind: entity for entity, kind in KINDS.items()}
HOMOLOGOUS = "homologous"
REVIEWED = "reviewed-target"
UNSUPPORTED = "unsupported"
# The evidence kinds of a homologous row (kb.match.typed), and the states of
# the status of an unsupported row.
HOMOLOGY_KINDS = (*match.TYPED, "l0")
STATES = ("absent", "unresolved")
INERT = "stock-inert-path"
SURFACE = re.compile(r"\bhomologous surface ([0-9a-f]{8})\b")
IMAGE_KEYS = ("source", "source_sha256", "target_sha256", "checksum", "romraider_checksum",
              "map_switching", "rolling_launch")
PROJECTION_KEYS = frozenset({*IMAGE_KEYS, "addresses", "comment", "evidence", "switch"})
FIELDS = ("entity", "source", "target", "variant", "status", "sites", "function_kinds",
          "evidence")
# The columns within which a projection comment wraps its note.
COMMENT_WIDTH = 79


def inputs(root):
    return [PROJECTIONS.as_posix()] + [path.relative_to(root).as_posix()
                                        for path in sorted((root / DEFS).glob(ADDRESSES))]


def address_file(source, layout):
    """The name of the address file of a layout whose definitions relocate
    the image `source`."""
    return f"{source}-{layout.upper()}.definition-addresses.csv"


def declare(b, root):
    src = PROJECTIONS.as_posix()
    document = tomllib.loads((root / PROJECTIONS).read_text(encoding="utf-8"))
    layout_of = {rom: layout.id for layout in b.layouts.values() for rom in layout.images}
    catalog = repo.images(root)
    images, files = {}, {}
    for rom, projection in sorted(document.get("projection", {}).items()):
        subject = f"projection.{rom}"
        layout = layout_of.get(rom)
        if layout is None:
            b.issue("schema", src, subject, "no layout holds the image")
            continue
        for key in sorted(set(projection) - PROJECTION_KEYS):
            b.issue("schema", src, subject, f"unknown key {key}")
        if layout_of.get(projection.get("source")) != CANONICAL:
            b.issue("schema", src, subject, f"source {projection.get('source')!r} is no image "
                    f"of {CANONICAL}")
        for key, image in (("source_sha256", projection.get("source")), ("target_sha256", rom)):
            known = catalog.get(image)
            if known is None or projection.get(key) != known.sha256:
                b.issue("audit", src, subject, f"{key} disagrees with the image catalog")
        derived = address_file(projection.get("source"), layout)
        if projection.get("addresses") != derived:
            b.issue("schema", src, subject, f"addresses {projection.get('addresses')!r} is "
                    f"not the address file {derived} of {layout}")
            continue
        path = (DEFS / derived).as_posix()
        files[path] = layout
        entry = {key: projection[key] for key in IMAGE_KEYS if key in projection}
        entry["switch"] = hexed(dict(projection.get("switch", {})))
        entry["note"] = " ".join(projection.get("comment", "").split())
        entry["basis"] = projection.get("evidence")
        images.setdefault(layout, {})[rom] = entry
    for layout in sorted(images):
        paths = sorted(path for path, owner in files.items() if owner == layout)
        found = {"requires": [], "variants": [], "omitted": []}
        for path in paths:
            _declare_rows(b, root, path, layout, found)
        b.entity("feature", FEATURE, src)
        target = b.target(FEATURE, layout, src, status="supported",
                          props={"images": images[layout], **found})
        target.sources.update(paths)


def _declare_rows(b, root, path, layout, found):
    with (root / path).open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    for number, row in enumerate(rows, start=2):
        where = f"{path}:{number}"
        subject = f"{row['entity']}:{row['source']}"
        kind = KINDS.get(row["entity"])
        if kind is None:
            b.issue("schema", where, subject, f"unknown entity {row['entity']}")
            continue
        origin = b.symbol(CANONICAL, kind, int(row["source"], 16), path)
        if origin not in found["requires"]:
            found["requires"].append(origin)
        status, text, stated = row["status"], row["evidence"], row["function_kinds"]
        if status == UNSUPPORTED:
            if stated == INERT:
                surface = SURFACE.search(text)
                if surface is None:
                    b.issue("schema", where, subject, "the evidence names no homologous surface")
                    continue
                symbol = b.symbol(layout, kind, int(surface.group(1), 16), path, evidence=[{
                    "kind": "l0", "supports": "homology", "to": origin, "note": text,
                    "legacy": INERT}])
                b.join(origin, symbol, where)
                found["omitted"].append({"symbol": symbol, "reason": INERT})
            elif stated in STATES:
                b.status(origin, layout, stated, path, props={"note": text},
                         evidence=[{"kind": "registry", "supports": "identity", "path": path,
                                    "key": subject, "note": text}])
            else:
                b.issue("schema", where, subject, f"unknown state {stated}")
            continue
        if not row["target"]:
            b.issue("schema", where, subject, f"a {status} row without target")
            continue
        if status == HOMOLOGOUS:
            if stated not in HOMOLOGY_KINDS:
                b.issue("schema", where, subject, f"a homologous row of the kind {stated}")
                continue
            evidence = [{"kind": stated, "supports": "homology", "to": origin, "note": text,
                         "legacy": f"{status}:{stated}"}]
        elif status == REVIEWED:
            if stated != "l0":
                b.issue("schema", where, subject, f"a reviewed-target row of the kind {stated}")
                continue
            evidence = [{"kind": "l0", "supports": "identity", "note": text, "legacy": REVIEWED}]
        else:
            b.issue("schema", where, subject, f"unknown status {status}")
            continue
        symbol = b.symbol(layout, kind, int(row["target"], 16), path, evidence=evidence)
        b.join(origin, symbol, where)
        if row["variant"]:
            found["variants"].append({"symbol": symbol, "variant": row["variant"]})


def relate(b, root):
    pass


# Projections ---------------------------------------------------------------


def _targets(model):
    """The `definitions` targets of the layouts that relocate a definition;
    the target of `7mfk` holds the source image."""
    return [(layout, target) for (feature, layout), target in sorted(model.targets.items())
            if feature == FEATURE and layout != CANONICAL]


def _toward(item):
    """The layout that the `to` of an evidence item locates."""
    to = item.get("to")
    if isinstance(to, SymbolKey):
        return to.layout
    found = match.location(to)
    return found[0] if found else None


def row_item(symbol):
    """(status, item) of the row of a target symbol: its first evidence item
    that is homology evidence toward the `7mfk` symbol of its meaning,
    `homologous`, or `l0` identity evidence on its own layout,
    `reviewed-target`; (None, None) without one."""
    for item in symbol.evidence:
        kind, supports = item.get("kind"), item.get("supports", "identity")
        if supports == "homology" and kind in HOMOLOGY_KINDS and _toward(item) == CANONICAL:
            return HOMOLOGOUS, item
        if supports == "identity" and kind == "l0":
            at = match.location(item.get("at"))
            if at is not None and at[0] == symbol.layout:
                return REVIEWED, item
    return None, None


def _note(text, subject):
    if not isinstance(text, str) or not text.strip():
        raise KbError(f"the row of {subject} has no note", code=3)
    return text


def _row(model, layout, key, omitted, variants):
    """The address row of a meaning that the target of a layout requires."""
    meaning = model.meaning_of(key)
    origin = meaning.symbols.get(CANONICAL) if meaning is not None else None
    if origin is None or meaning.kind not in ENTITIES:
        raise KbError(f"the {FEATURE} target of {layout} requires "
                      f"{key.key if isinstance(key, SymbolKey) else key}, which is no tbl or "
                      f"axis meaning with a {CANONICAL} symbol", code=3)
    head = (ENTITIES[meaning.kind], f"{origin.address:08x}")
    subject = f"{meaning.key} on {layout}"
    symbol = meaning.symbols.get(layout)
    if symbol is None:
        status = meaning.statuses.get(layout)
        if status is None:
            raise KbError(f"the {FEATURE} target of {layout} requires {meaning.key}, which has "
                          "neither a symbol nor a status there", code=3)
        return (*head, "", "", UNSUPPORTED, "0", status.state,
                _note(status.props.get("note"), subject))
    state, item = row_item(symbol)
    if item is None:
        raise KbError(f"{symbol.key.key} has neither homology evidence toward {CANONICAL} nor "
                      f"l0 identity evidence on {layout}", code=3)
    note = _note(item.get("note"), subject)
    if symbol.key in omitted:
        return (*head, "", "", UNSUPPORTED, "0", omitted[symbol.key], note)
    return (*head, f"{symbol.address:08x}", variants.get(symbol.key, ""), state,
            str(len(match.touching(model, symbol))), item["kind"], note)


def _source(layout, target):
    sources = {entry.get("source") for entry in target.props.get("images", {}).values()}
    if len(sources) != 1:
        raise KbError(f"the images of the {FEATURE} target of {layout} name the sources "
                      f"{', '.join(sorted(map(str, sources))) or 'none'}; the address file "
                      "belongs to one source", code=3)
    return sources.pop()


def render_addresses(model):
    """{path: text} of the address file of every `definitions` target."""
    found = {}
    for layout, target in _targets(model):
        omitted = {entry["symbol"]: entry.get("reason", INERT)
                   for entry in target.props.get("omitted", ())}
        variants = {entry["symbol"]: entry.get("variant", "")
                    for entry in target.props.get("variants", ())}
        rows = sorted((_row(model, layout, key, omitted, variants)
                       for key in target.props.get("requires", ())),
                      key=lambda row: (row[0], row[1], row[3], row[2]))
        out = io.StringIO()
        writer = csv.writer(out, lineterminator="\n")
        writer.writerow(FIELDS)
        writer.writerows(rows)
        found[(DEFS / address_file(_source(layout, target), layout)).as_posix()] = \
            out.getvalue()
    return found


def _scalar(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


def render_projections(model):
    """The text of `defs/definition-projections.toml`: `[projection.<ROM>]`
    for each image of a `definitions` target, in the order of the ROM keys."""
    images = {rom: (layout, entry) for layout, target in _targets(model)
              for rom, entry in target.props.get("images", {}).items()}
    feature = model.entities.get(("feature", FEATURE))
    order = list(feature.props.get("switches") or ()) if feature is not None else []
    blocks = [f"schema_version = {SCHEMA_VERSION}"]
    for rom in sorted(images):
        layout, entry = images[rom]
        values = {**entry, "addresses": address_file(entry.get("source"), layout)}
        lines = [f"[projection.{rom}]"]
        for key in ("source", "source_sha256", "target_sha256", "addresses", *IMAGE_KEYS[3:]):
            if key in values:
                lines.append(f"{key} = {_scalar(values[key])}")
        if entry.get("note"):
            note = textwrap.fill(entry["note"], COMMENT_WIDTH, break_long_words=False,
                                 break_on_hyphens=False)
            note = note.replace("\\", "\\\\").replace('"""', '""\\"')
            lines += ['comment = """', note, '"""']
        if entry.get("basis"):
            lines.append(f"evidence = {_scalar(entry['basis'])}")
        blocks.append("\n".join(lines))
        switch = entry.get("switch") or {}
        if switch:
            keys = [key for key in order if key in switch] + sorted(set(switch) - set(order))
            blocks.append("\n".join([f"[projection.{rom}.switch]"] + [
                f"{key} = 0x{_address(switch[key]):08X}" for key in keys]))
    return "\n\n".join(blocks) + "\n"


def _address(value):
    return value if isinstance(value, int) else int(str(value), 16)


def addresses(root=repo.ROOT):
    """{path: text} of the address file of every `definitions` target."""
    from kb import compile
    return render_addresses(compile.cached(root))


def projections(root=repo.ROOT):
    """The text of `defs/definition-projections.toml` from the model."""
    from kb import compile
    return render_projections(compile.cached(root))
