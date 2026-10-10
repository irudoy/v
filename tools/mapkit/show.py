#!/usr/bin/env python3
# Print a map or axis in physical units using graph metadata (address, shape,
# element, axes, and scaling) plus image values. This is an analysis tool rather
# than a generator and writes nothing to Git.
#
# One address can be both a map and an axis. JK08A has 18 such addresses, with
# seven pairs read in both directions (defs/JK08A.notes.md, "Reverse lookup").
# The use site defines the role, not the array, so every graph role is printed.
#
# Scaled values appear beside rather than instead of raw values. Half of the map
# multipliers have candidate confidence, and replacing bytes with them would
# present an inference as a measurement.
#
# Usage: uv run python tools/mapkit/show.py [<rom>] <addr>...
import os
import sys

from kb import reader

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mapkit import rom as romkit          # noqa: E402 - adjacent, uninstalled package



def hexa(a):
    return "0x" + a.upper().lstrip("0").rjust(5, "0")


def phys(v, expr):
    """Apply graph scaling; the loader validates the expression vocabulary."""
    if not expr or expr.strip() == "x":
        return None
    return eval(expr, {"__builtins__": {}}, {"x": v})


def num(v):
    return f"{v:.4g}" if isinstance(v, float) else str(v)


def cell(raw, expr):
    v = phys(raw, expr)
    return num(raw) if v is None else num(v)


def labels(ax, n):
    """Return axis-point labels, or ordinal numbers when no axis exists."""
    if not ax:
        return [str(i) for i in range(n)]
    vals, expr = ax
    return [cell(v, expr) for v in vals]


def scale_note(units, expr, conf):
    if not expr or expr.strip() == "x":
        return "no scaling; raw values"
    return f"scaling {expr} -> {units}" + (f" [{conf}]" if conf else "")


def show_axis(x, img, head="axis"):
    vals = img.values(x["addr"], x["len"], x["storagetype"])
    print(f"  {head} {hexa(x['addr'])}: {x['len']} points {x['storagetype']}"
          f", {x['kind'] or 'semantics unresolved'} [{x['confidence']}]"
          f", {scale_note(x['units'], x['scale_expr'], x['scale_conf'])}")
    print("    raw:", " ".join(num(v) for v in vals))
    if phys(vals[0], x["scale_expr"]) is not None:
        print(f"    {x['units']}:", " ".join(num(phys(v, x["scale_expr"])) for v in vals))
    if x["note"]:
        print(f"    {x['note']}")
    return vals


def grid(cells, expr, head, lbl):
    """Print a labeled grid. In 2D, rows use r5 and columns use r6."""
    body = [[cell(v, expr) for v in r] for r in cells]
    w = max(len(s) for s in head + [c for r in body for c in r])
    pad = max((len(s) for s in lbl), default=0)
    print("  " + " " * pad + " | " + " ".join(s.rjust(w) for s in head))
    print("  " + "-" * (pad + 1) + "+" + "-" * (len(head) * (w + 1) + 1))
    for i, r in enumerate(body):
        print(f"  {(lbl[i] if lbl else '').rjust(pad)} | "
              + " ".join(c.rjust(w) for c in r))


def show_map(m, axes, img):
    shape = f"{m['width']}x{m['height']}" if m["dims"] == 2 else f"1D-{m['width']}"
    print(f"{hexa(m['addr'])}  {m['semantics'] or '(semantics unresolved)'}  "
          f"[{m['confidence']}]")
    print(f"  {shape} {m['storagetype']}, {m['family']}, values {m['vmin']}..{m['vmax']}"
          f"; {scale_note(m['units'], m['scale_expr'], m['scale_conf'])}")
    if m["note"]:
        print(f"  {m['note']}")
    rows_ax = cols_ax = None
    for edge, key in (("AXIS_X", "axis_x"), ("AXIS_Y", "axis_y")):
        for a in m[key]:
            x = axes[a]
            head = ("r5 axis (rows, definition Y Axis)" if edge == "AXIS_X"
                    else "r6 axis (columns, definition X Axis)") if m["dims"] == 2 else "axis"
            vals = show_axis(x, img, head)
            if edge == "AXIS_X" and rows_ax is None:
                rows_ax = (vals, x["scale_expr"])
            elif edge == "AXIS_Y" and cols_ax is None:
                cols_ax = (vals, x["scale_expr"])
    if len(m["axis_x"]) > 1 or len(m["axis_y"]) > 1:
        print("  WARNING: an edge has multiple axes selected by branching (Stage 6);"
              " the grid uses the first")
    if m["dims"] == 1 and not m["axis_x"] and m["steps"]:
        print(f"  implicit axis: points 0..{m['width'] - 1} with step {m['steps'][0]}")
        cols_ax = ([i * m["steps"][0] for i in range(m["width"])], "x")
    # A one-dimensional map has no height property; Memgraph omits nulls.
    cells = img.table(m["addr"], m["width"], m.get("height"), m["storagetype"])
    # A one-dimensional map has one row and its axis labels columns. In 2D, r5
    # labels rows and r6 labels columns, as defined by finisher geometry in rom.py.
    if m["dims"] == 1:
        grid(cells, m["scale_expr"], labels(cols_ax or rows_ax, m["width"]), [])
    else:
        grid(cells, m["scale_expr"], labels(cols_ax, m["height"]),
             labels(rows_ax, m["width"]))


def fetch(s, rom, addr):
    m = s.run("""
        MATCH (m:Map {rom:$rom, addr:$a})
        OPTIONAL MATCH (m)-[:AXIS_X]->(x:Axis) OPTIONAL MATCH (m)-[:AXIS_Y]->(y:Axis)
        OPTIONAL MATCH (m)-[:VIA]->(w:Interp)
        RETURN m AS m, collect(DISTINCT x.addr) AS axis_x,
               collect(DISTINCT y.addr) AS axis_y,
               [s IN collect(DISTINCT w.step) WHERE s IS NOT NULL] AS steps
        """, rom=rom, a=addr).single()
    x = s.run("MATCH (x:Axis {rom:$rom, addr:$a}) RETURN x", rom=rom, a=addr).single()
    return m, x


def main():
    args = sys.argv[1:]
    try:
        known = {r["rom"] for r in romkit.registry() if r["rom"]}
    except ValueError as e:
        sys.exit(str(e))
    # The registry, not syntax, distinguishes a ROM label from an address:
    # 0xB33A and JK08A both look hexadecimal, so shape-based parsing is ambiguous.
    rom = args.pop(0) if args and args[0] in known else "JK08A"
    if not args:
        sys.exit(f"address required: show.py [<rom>] <addr>...; ROM labels: "
                 f"{', '.join(sorted(known))}")
    try:
        img = romkit.load(rom)
    except ValueError as e:
        sys.exit(str(e))
    with reader.session() as s:
        for a in args:
            addr = "%08x" % int(a, 16)
            m, x = fetch(s, rom, addr)
            if not m and not x:
                print(f"{hexa(addr)}: address not found in the {rom} graph")
                continue
            if m:
                d = dict(m["m"], axis_x=m["axis_x"], axis_y=m["axis_y"], steps=m["steps"])
                axes = {a2: dict(s.run("MATCH (x:Axis {rom:$rom, addr:$a}) RETURN x",
                                       rom=rom, a=a2).single()["x"])
                        for a2 in d["axis_x"] + d["axis_y"]}
                show_map(d, axes, img)
            if x:
                # The same address can be another map's axis; use sites define roles.
                if m:
                    print("  also an axis for other maps:")
                show_axis(dict(x["x"]), img)
            print()


if __name__ == "__main__":
    main()
