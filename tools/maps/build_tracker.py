#!/usr/bin/env python3
"""Canonical-ROM map ledger projected from the graph catalog.

The graph is a reproducible projection of tracked sources and exact image
measurements. load_maps.py stores maps, interpolation wrappers, axes, and
accessors from resolver censuses and the reviewed source layer. The ledger is a readable projection of this catalog: a reviewable
reverse-engineering worklist visible in diffs. Do not edit it directly. Geometry
and findings live in the canonical source resolved by
defs/rom-inheritance.toml; this script only renders the graph.

Open work consists of candidate rows with empty semantics. There is no separate
status column because it would merely render confidence, role, and semantics,
duplicating adjacent facts and creating another source of divergence.

The vals column is the cell range measured from the exact image. It
partitions open work: an all-zero or all-0xFF table requires different analysis
from a populated surface.

Usage: uv run python tools/maps/build_tracker.py \
          [<rom>|all|--all] [<output.csv>]
"""
import csv
import os
import sys
import tempfile
from kb import reader

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from tools import diagnostic_context, rom_sources  # noqa: E402
from tools.mapkit import definition_targets  # noqa: E402

FIELDS = ["table", "family", "via", "kernel", "dim", "storagetype", "vals", "scaling",
          "axis_x", "axis_y", "accessors", "sites", "confidence", "role", "semantics",
          "diag_priority", "diagnostic_context", "note"]

# Resolved work appears first and open work last. Sort tables by confidence and
# semantic presence, then non-tunable bases such as comparator thresholds and
# calibration-disabled branches.
LEVEL_ORDER = {"silicon": 0, "code": 1, "candidate": 2, "pattern": 3}
ROLE_ORDER = {"table": 0, "threshold": 1, "dead": 2}

QUERY = """
MATCH (m:Map {rom:$rom})
OPTIONAL MATCH (m)-[:VIA]->(w:Interp {rom:$rom})
OPTIONAL MATCH (w)-[:KERNEL]->(k:Interp {rom:$rom})
OPTIONAL MATCH (m)-[:AXIS_X]->(ax:Axis {rom:$rom})
OPTIONAL MATCH (m)-[:AXIS_Y]->(ay:Axis {rom:$rom})
OPTIONAL MATCH (f:Func {rom:$rom})-[a:ACCESSES]->(m)
RETURN m.addr AS table, m.family AS family, m.width AS width, m.height AS height,
       m.storagetype AS storagetype, m.confidence AS confidence, m.role AS role,
       m.semantics AS semantics, m.note AS note, m.vmin AS vmin, m.vmax AS vmax,
       m.units AS units, m.scale_expr AS scale_expr, m.scale_conf AS scale_conf,
       collect(DISTINCT w.addr) AS via, collect(DISTINCT k.addr) AS kernel,
       collect(DISTINCT ax.addr) AS axis_x, collect(DISTINCT ay.addr) AS axis_y,
       collect(DISTINCT f.addr) AS accessors, count(DISTINCT a) AS sites
"""


def shape(width, height):
    """Format a 2D grid or a 1D axis-point count."""
    if width is None:
        return ""
    return f"{width}x{height}" if height else f"1D-{width}"


def scaling(r):
    """Format scaling on one line using its own confidence, not map confidence."""
    if not r["scale_expr"] or r["scale_expr"].strip() == "x":
        return ""
    return (f"{r['scale_expr']} {r['units']}"
            + (f" [{r['scale_conf']}]" if r["scale_conf"] else ""))


def project(rows):
    out = []
    for r in rows:
        priority, context = diagnostic_context.summarize(
            r.get("diagnostic_bindings", [])
        )
        out.append({
            "table": r["table"],
            "family": r["family"],
            "via": ";".join(sorted(r["via"])),
            "kernel": ";".join(sorted(r["kernel"])),
            "dim": shape(r["width"], r["height"]),
            "storagetype": r["storagetype"] or "",
            "vals": f"{r['vmin']}..{r['vmax']}",
            "scaling": scaling(r),
            "axis_x": ";".join(sorted(r["axis_x"])),
            "axis_y": ";".join(sorted(r["axis_y"])),
            "accessors": ";".join(sorted(r["accessors"])),
            "sites": str(r["sites"]),
            "confidence": r["confidence"],
            "role": r["role"],
            "semantics": r["semantics"],
            "diag_priority": str(priority) if priority else "",
            "diagnostic_context": "; ".join(context),
            "note": r["note"],
        })
    out.sort(key=lambda r: (ROLE_ORDER.get(r["role"], 9),
                            LEVEL_ORDER.get(r["confidence"], 9),
                            -int(r["diag_priority"] or 0),
                            r["semantics"] == "", r["family"], r["dim"], r["table"]))
    return out


def report(out, tracker):
    tally = {}
    for r in out:
        tally[r["confidence"]] = tally.get(r["confidence"], 0) + 1
    fam, role = {}, {}
    for r in out:
        fam[r["family"]] = fam.get(r["family"], 0) + 1
        role[r["role"]] = role.get(r["role"], 0) + 1
    print(f"{os.path.relpath(tracker)}: {len(out)} maps")
    print("  confidence: " + ", ".join(f"{k}={tally[k]}" for k in LEVEL_ORDER if k in tally))
    print("  roles: " + ", ".join(f"{k}={role[k]}" for k in ROLE_ORDER if k in role))
    print("  families: " + ", ".join(f"{k}={fam[k]}" for k in sorted(fam)))
    named = sum(1 for r in out if r["semantics"])
    empty = sum(1 for r in out if not r["via"] and not r["accessors"])
    print(f"  with semantics: {named}/{len(out)}")
    diagnostic = sum(1 for r in out if r["diagnostic_context"])
    print(f"  with static diagnostic context: {diagnostic}/{len(out)}")
    print(f"  open (candidate without semantics): "
          f"{sum(1 for r in out if r['confidence'] == 'candidate' and not r['semantics'])}")
    if empty:
        print(f"WARNING: {empty} maps have no wrapper or accessor and are orphan graph nodes")


def emit_tracker(rom, tracker=None, display_tracker=None):
    """Generate one canonical map ledger."""
    try:
        source_model = rom_sources.resolve(rom)
        rom_sources.verify_image_binding(source_model)
    except ValueError as error:
        sys.exit(str(error))
    if tracker is None and source_model.inherited:
        sys.exit(
            f"{rom} inherits annotations from {source_model.source}; "
            "its ledger is not stored in defs, so specify a temporary output.csv"
        )
    if tracker is None:
        tracker = os.path.join(ROOT, "defs", f"{rom}.maps.csv")

    with reader.session() as s:
        rows = [r.data() for r in s.run(QUERY, rom=rom)]
        bindings = diagnostic_context.map_bindings(s, rom)
    if not rows:
        sys.exit(f"no maps for rom={rom} in graph; tools/memgraph/load_maps.py builds the layer")
    for row in rows:
        row["diagnostic_bindings"] = bindings.get(row["table"], [])

    out = project(rows)
    with open(tracker, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    report(out, display_tracker or tracker)


def emit_all(output_dir=None):
    """Generate all canonical ledgers without partial output on render failure."""
    output_dir = os.fspath(output_dir or os.path.join(ROOT, "defs"))
    sources = definition_targets.registered_sources()
    with tempfile.TemporaryDirectory(
        prefix=".build-tracker-", dir=output_dir
    ) as stage_dir:
        staged = []
        for rom in sources:
            final_path = os.path.join(output_dir, f"{rom}.maps.csv")
            stage_path = os.path.join(stage_dir, f"{rom}.maps.csv")
            emit_tracker(
                rom,
                tracker=stage_path,
                display_tracker=final_path,
            )
            staged.append((stage_path, final_path))
        for staged_path, final_path in staged:
            os.replace(staged_path, final_path)


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        args = ["all"]
    if args[0].lower() in {"all", "--all"}:
        if len(args) != 1:
            sys.exit("all mode does not accept an explicit output path")
        emit_all()
        return
    if len(args) > 2:
        sys.exit(
            "usage: build_tracker.py [<rom>|all|--all] [<output.csv>]"
        )
    emit_tracker(*args)


if __name__ == "__main__":
    main()
