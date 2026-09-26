"""Definition projections and their address correspondences
(tools/kb/SPEC.md, section 20.3).

- Each `[projection.<ROM>]` of `defs/definition-projections.toml` gives the
  entry of its image in `images` of the `definitions` target of the image's
  layout: the source image, both digests, the checksum and feature switches,
  the switch bytes of `[projection.<ROM>.switch]`, and its prose. The digests
  must equal the image catalog.
- Each row of the address file that a projection names gives the symbol of
  its entity on the image's layout: `Map` a `tbl` and `Axis` an `axis`
  symbol, so an address that is both a table and an axis operand gives one of
  each. A `homologous` row joins it to the meaning of the `7mfk` symbol at
  `source` with homology evidence of the kind that `function_kinds` names; a
  `reviewed-target` row joins an anchor with `l0` evidence; an `unsupported`
  row gives the status that `function_kinds` names, except that
  `stock-inert-path` joins the homologous surface that its evidence names,
  which the target leaves out.
"""

import csv
from pathlib import Path
import re
import tomllib

from kb import match, repo
from kb.values import hexed

PROJECTIONS = Path("defs/definition-projections.toml")
DEFS = Path("defs")
ADDRESSES = "JK08A-*.definition-addresses.csv"
CANONICAL = "7mfk"
FEATURE = "definitions"
KINDS = {"Map": "tbl", "Axis": "axis"}
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


def inputs(root):
    return [PROJECTIONS.as_posix()] + [path.relative_to(root).as_posix()
                                        for path in sorted((root / DEFS).glob(ADDRESSES))]


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
        path = (DEFS / projection["addresses"]).as_posix()
        if files.setdefault(path, layout) != layout:
            b.issue("schema", src, subject, f"{path} serves the layouts {files[path]} and {layout}")
            continue
        entry = {key: projection[key] for key in IMAGE_KEYS if key in projection}
        entry["switch"] = hexed(dict(projection.get("switch", {})))
        entry["note"] = projection.get("comment", "").strip()
        entry["evidence"] = projection.get("evidence")
        images.setdefault(layout, {})[rom] = entry
    for layout in sorted(images):
        paths = sorted(path for path, owner in files.items() if owner == layout)
        found = {"variants": [], "omitted": []}
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
                found["omitted"].append({"symbol": symbol, "reason": INERT, "note": text})
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
            found["variants"].append({"symbol": symbol, "variant": row["variant"], "note": text})


def relate(b, root):
    pass
