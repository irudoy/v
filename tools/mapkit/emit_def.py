#!/usr/bin/env python3
# Definition generator (Stage 8, section 9 of tools/map-flag-pipeline.md):
# Memgraph (facts) + defs/<rom>.dtc.csv (DTC) + defs/<rom>.overrides.toml (presentation)
# -> defs/<rom>.xml (RomRaider) + defs/<rom>.xdf (TunerPro).
#
# Source separation is the reason this step exists (P5). Declare each fact once: address,
# shape, element, axes, scaling, and confidence live in the graph, populated by the resolver
# census and the manual layer; name, category, order, and editor increments live in overrides.
# The definition file is not a source for either set, and edits to it do not survive the next
# run.
#
# Emission gate (section 9): emit a table when it can be interpreted, meaning it has the
# table role, semantics, and scaling. Without semantics a map is only an address and shape;
# without scaling it is a grid of raw bytes. Both already belong in the ledger. The report
# lists rejected maps because silent omission could be read as absence.
#
# Put confidence labels where each assertion appears:
#   map confidence     -> generated comment above the table;
#   scaling below code -> unit suffix " [cand]": the multiplier is not established by code.
# Categories remain functional and do not partition tables by confidence.
#
# Translate wrapper axes to RomRaider axes as established from finishers; see
# defs/<rom>.notes.md. A finisher addresses a cell as
# cell = table + idxY + width*idxX, where idxX is the position on the r5 axis. Therefore,
# the r5 axis (graph :AXIS_X) defines rows and the r6 axis (:AXIS_Y) defines columns, while
# RomRaider calls columns X Axis and rows Y Axis. The mapping crosses:
# :AXIS_X -> Y Axis and :AXIS_Y -> X Axis. A one-dimensional map has one axis, which
# RomRaider calls X Axis. The manual direct-row-major family stores X as the inner dimension
# and has no axis edges: width -> sizex, height -> sizey, and overrides define both static
# axes.
#
# Invocation:
# uv run --no-project --with neo4j python tools/mapkit/emit_def.py \
#   [<rom>] [<romraider-out>] [<tunerpro-out>]
import csv
import html
import os
import sys
import textwrap
import tomllib
from neo4j import GraphDatabase

BOLT = "bolt://localhost:7687"
HERE = os.path.dirname(os.path.abspath(__file__))
DEFS = os.path.join(HERE, "..", "..", "defs")
if __package__:
    from . import presentation, rom as romkit, tunerpro
    from tools import diagnostic_context
else:
    sys.path.insert(0, os.path.dirname(HERE))
    from mapkit import presentation, rom as romkit, tunerpro
    import diagnostic_context

LEVELS = ("pattern", "candidate", "code", "silicon")   # confidence ladder from section 5

ROMID_FIELDS = ("xmlid", "internalidaddress", "internalidstring", "ecuid", "caseid",
                "make", "model", "submodel", "market", "transmission", "memmodel",
                "endian", "flashmethod", "filesize", "author", "version")
CHECKSUM_FIELDS = (
    "type", "path", "expectedsize",
    "start", "end", "skiploc", "sumloc", "xorloc",
)
SWITCH_FIELDS = (
    "name", "category", "storageaddress", "storagetype", "sizex", "sizey",
    "endian", "userlevel",
)
SWITCH_REQUIRED_FIELDS = (
    "name", "category", "storageaddress", "storagetype", "endian", "userlevel",
)
SWITCH_SIZE_FIELDS = ("sizex", "sizey")
SWITCH_STORAGE_BYTES = {"uint8": 1, "uint16": 2, "uint32": 4}
DTC_FIELDS = (
    "index", "dtc", "record_addr", "attribute_addr", "stock_attribute",
    "disabled_attribute", "group", "confidence", "note",
)
DTC_RECORD_SIZE = 12
DTC_ATTRIBUTE_SIZE = 2
DTC_CATEGORY = "Diagnostics / DTC"
MASKED_VIEW_FIELDS = (
    "source", "name", "category", "mask", "units", "expression", "to_byte",
    "format", "fine", "coarse",
)
# Axis name derived from its semantics. Several maps can share an axis, so define its name
# once here rather than per map; [axis.<addr>] in overrides handles a special case.
AXIS_NAMES = {"rpm": "Engine Speed [RPM]", "load": "Engine Load",
              "temp": "Temperature", "raw": "Axis (raw)"}


def att(v):
    return html.escape(str(v), quote=True)


def hexa(a):
    """Convert a graph address (eight hexadecimal digits) to RomRaider form."""
    text = f"{a:X}" if isinstance(a, int) else str(a).upper()
    return "0x" + text.lstrip("0").rjust(5, "0")


def comment(lines, indent=4):
    """Build an XML comment, replacing forbidden internal '--' sequences with '-'."""
    pad = " " * indent
    body = []
    for l in lines:
        l = l.replace("--", "-").rstrip()
        body += textwrap.wrap(l, 96 - indent - 5) or [""]
    while body and not body[-1]:
        body.pop()
    out = [(f"{pad}<!-- " + body[0]).rstrip()]
    out += [(pad + "     " + l).rstrip() for l in body[1:]]
    return "\n".join(out) + " -->"


def wrap(pad, head, attrs, tail):
    """Wrap tag attributes to line width with continuations aligned under the first attribute."""
    lines, cur = [], pad + head
    for a in attrs:
        if len(cur) + 1 + len(a) > 96:
            lines.append(cur)
            cur = pad + " " * len(head)
        cur += " " + a
    lines.append(cur + tail)
    return lines


def scaling(units, expr, to_byte, conf, fmt, fine, coarse, indent):
    """Build a <scaling> block, suffixing units when code does not establish the multiplier."""
    if conf and conf != "code":
        units += " [cand]"
    a = [f'units="{att(units)}"', f'expression="{att(expr)}"',
         f'to_byte="{att(to_byte)}"', f'format="{att(fmt)}"']
    if fine is not None:
        a.append(f'fineincrement="{att(fine)}"')
    if coarse is not None:
        a.append(f'coarseincrement="{att(coarse)}"')
    return "\n".join(wrap(" " * indent, "<scaling", a, "/>"))


def fetch(rom):
    """Fetch calibration-layer facts: candidate maps, their axes, and context."""
    driver = GraphDatabase.driver(BOLT, auth=("", ""))
    with driver.session() as s:
        maps = {r["a"]: dict(r["m"]) for r in s.run(
            "MATCH (m:Map {rom:$rom}) RETURN m.addr AS a, m AS m", rom=rom)}
        for r in s.run(
                """
                MATCH (m:Map {rom:$rom})-[:VIA]->(w:Interp {rom:$rom})
                OPTIONAL MATCH (w)-[:KERNEL]->(k:Interp {rom:$rom})
                RETURN m.addr AS a, collect(DISTINCT w.addr) AS wrappers,
                       collect(DISTINCT w.step) AS steps,
                       collect(DISTINCT k.addr) AS kernels
                """, rom=rom):
            maps[r["a"]].update(wrappers=r["wrappers"], steps=[x for x in r["steps"] if x],
                                kernels=r["kernels"])
        for r in s.run(
                """
                MATCH (f:Func)-[e:ACCESSES]->(m:Map {rom:$rom})
                RETURN m.addr AS a, collect(DISTINCT f.addr) AS accessors
                """, rom=rom):
            maps[r["a"]]["accessors"] = r["accessors"]
        for address, bindings in diagnostic_context.map_bindings(
            s, rom
        ).items():
            maps[address]["diagnostic_bindings"] = bindings
        axes = {r["a"]: dict(r["x"]) for r in s.run(
            "MATCH (x:Axis {rom:$rom}) RETURN x.addr AS a, x AS x", rom=rom)}
        # An edge may have more than one axis when branching selects the axis and the resolver
        # sees a different one at each site. This is geometry ambiguity rather than a loader
        # error. Stage 6 resolves it; here it simply prevents map emission.
        for edge in ("AXIS_X", "AXIS_Y"):
            for r in s.run(
                    f"""
                    MATCH (m:Map {{rom:$rom}})-[:{edge}]->(x:Axis {{rom:$rom}})
                    RETURN m.addr AS a, collect(DISTINCT x.addr) AS ax
                    """, rom=rom):
                maps[r["a"]][edge.lower()] = r["ax"]
    driver.close()
    for m in maps.values():
        for k in (
            "wrappers", "kernels", "steps", "accessors",
            "axis_x", "axis_y", "diagnostic_bindings",
        ):
            m.setdefault(k, [])
        _, m["diagnostic_context"] = diagnostic_context.summarize(
            m["diagnostic_bindings"]
        )
    return maps, axes


def axis_xml(kind, x, ovr, size_attr, indent=6):
    """Build a ROM-array axis: address, element, and length are facts; name is presentation."""
    o = ovr.get("axis", {}).get(x["addr"], {})
    name = o.get("name") or AXIS_NAMES[x["kind"]]
    pad = " " * indent
    out = wrap(pad, "<table", [f'type="{kind}"', f'name="{att(name)}"',
                               f'storagetype="{att(x["storagetype"])}"',
                               f'storageaddress="{hexa(x["addr"])}"',
                               f'{size_attr}="{x["len"]}"', 'endian="big"'], ">")
    out.append(scaling(x["units"], x["scale_expr"], x["to_byte"], x["scale_conf"],
                       o.get("format", "0"), o.get("fine"), o.get("coarse"), indent + 2))
    out.append(f"{pad}</table>")
    return out


def static_axis_xml(values, name="Index", axis_type="Static X Axis",
                    size_attr="sizex", indent=6):
    pad = " " * indent
    out = [f'{pad}<table type="{att(axis_type)}" name="{att(name)}" '
           f'{size_attr}="{len(values)}">']
    for i in range(0, len(values), 4):
        out.append(pad + "  " + "".join(f"<data>{att(v)}</data>"
                                        for v in values[i:i + 4]))
    out.append(f"{pad}</table>")
    return out


def hex_bytes(data):
    """Format bytes for descriptions and TableSwitch state data."""
    return " ".join(f"{byte:02X}" for byte in data)


def dtc_records(rom, image=None, manifest_path=None):
    """Load and validate code-level DTC records against the exact stock ROM."""
    manifest_path = manifest_path or os.path.join(DEFS, f"{rom}.dtc.csv")
    if not os.path.exists(manifest_path):
        return []
    image = image or romkit.load(rom)
    with open(manifest_path, newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        missing = [field for field in DTC_FIELDS
                   if field not in (reader.fieldnames or [])]
        if missing:
            sys.exit(f"{os.path.basename(manifest_path)}: missing fields "
                     + ", ".join(missing))
        rows = list(reader)

    records = []
    for row_index, row in enumerate(rows, 2):
        if row["confidence"] != "code":
            continue
        try:
            record_index = int(row["index"], 10)
            record_addr = int(row["record_addr"], 16)
            attribute_addr = int(row["attribute_addr"], 16)
            dtc_code = int(row["dtc"][1:], 16)
            stock_attribute = bytes.fromhex(row["stock_attribute"])
            disabled_attribute = bytes.fromhex(row["disabled_attribute"])
        except (TypeError, ValueError):
            sys.exit(f"{os.path.basename(manifest_path)}:{row_index}: "
                     "invalid DTC, address, or attribute")
        if record_index < 0:
            sys.exit(f"{os.path.basename(manifest_path)}:{row_index}: "
                     "DTC index must be non-negative")
        if len(stock_attribute) != DTC_ATTRIBUTE_SIZE:
            sys.exit(f"{os.path.basename(manifest_path)}:{row_index}: "
                     "attribute must occupy two bytes")
        if len(disabled_attribute) != DTC_ATTRIBUTE_SIZE:
            sys.exit(f"{os.path.basename(manifest_path)}:{row_index}: "
                     "disabled attribute must occupy two bytes")
        record = image.data[record_addr:record_addr + DTC_RECORD_SIZE]
        if len(record) != DTC_RECORD_SIZE:
            sys.exit(f"{os.path.basename(manifest_path)}:{row_index}: "
                     "descriptor extends beyond ROM")
        if int.from_bytes(record[6:8], "big") != dtc_code:
            sys.exit(f"{os.path.basename(manifest_path)}:{row_index}: "
                     f"descriptor at {record_addr:#x} does not contain {row['dtc']}")
        actual_attribute = image.data[
            attribute_addr:attribute_addr + len(stock_attribute)
        ]
        if actual_attribute != stock_attribute:
            sys.exit(f"{os.path.basename(manifest_path)}:{row_index}: "
                     f"attribute at {attribute_addr:#x} does not match stock")

        note = row["note"].split(";", 1)[0].rstrip(".")
        records.append({
            "index": record_index,
            "dtc": row["dtc"],
            "record_addr": record_addr,
            "attribute_addr": attribute_addr,
            "record": record,
            "stock_attribute": stock_attribute,
            "disabled_attribute": disabled_attribute,
            "group": row["group"],
            "note": note,
        })
    return records


def dtc_switches(rom, image=None, manifest_path=None, records=None):
    """Build explicit descriptor and attribute switches for each DTC record.

    The descriptor and attribute occupy independent ROM ranges, so each mutable range
    is represented by its own native TableSwitch. The paired names keep both controls
    adjacent in the common DTC category without exposing raw table cells.
    """
    records = records if records is not None else dtc_records(
        rom, image=image, manifest_path=manifest_path
    )
    entries = []
    for record_info in records:
        record_index = record_info["index"]
        record = record_info["record"]
        stock_attribute = record_info["stock_attribute"]
        disabled_attribute = record_info["disabled_attribute"]
        base_name = f"DTC {record_info['dtc']} [index {record_index}]"
        common_description = (
            f"Exact {rom} only. Internal DTC record {record_index} "
            f"({record_info['group']}): {record_info['note']}. "
        )
        paired_description = (
            "Set both the Descriptor and Attribute controls to the same state "
            "before saving. "
        )
        has_attribute_switch = stock_attribute != disabled_attribute
        entries.append({
            "name": (
                f"{base_name} - 1/2 Descriptor"
                if has_attribute_switch
                else f"{base_name} - Descriptor"
            ),
            "category": DTC_CATEGORY,
            "storageaddress": hexa(record_info["record_addr"]),
            "storagetype": "uint8",
            "sizey": str(DTC_RECORD_SIZE),
            "endian": "big",
            "userlevel": "5",
            "description": (
                common_description
                + (paired_description
                   if has_attribute_switch
                   else
                   f"The associated attribute at "
                   f"{hexa(record_info['attribute_addr'])} "
                   "is already disabled in stock. ")
                + "DTC suppression does not disable the physical monitor."
            ),
            "state": [
                {"name": "Enabled (Stock)", "data": hex_bytes(record)},
                {
                    "name": "Disabled",
                    "data": hex_bytes(bytes(DTC_RECORD_SIZE)),
                },
            ],
        })
        if has_attribute_switch:
            entries.append({
                "name": f"{base_name} - 2/2 Attribute",
                "category": DTC_CATEGORY,
                "storageaddress": hexa(record_info["attribute_addr"]),
                "storagetype": "uint8",
                "sizey": str(DTC_ATTRIBUTE_SIZE),
                "endian": "big",
                "userlevel": "5",
                "description": (
                    common_description
                    + paired_description
                    + "DTC suppression does not disable the physical monitor."
                ),
                "state": [
                    {
                        "name": "Enabled (Stock)",
                        "data": hex_bytes(stock_attribute),
                    },
                    {
                        "name": "Disabled",
                        "data": hex_bytes(disabled_attribute),
                    },
                ],
            })
    return entries


def switch_xml(entry, index):
    """Build a TableSwitch from overrides or the DTC registry with named states."""
    if not isinstance(entry, dict):
        sys.exit(f"switch #{index} must be a TOML table")
    unknown = sorted(set(entry) - set(SWITCH_FIELDS) - {"description", "state"})
    if unknown:
        sys.exit(f"switch #{index} contains unknown fields {', '.join(unknown)}")
    missing = [k for k in SWITCH_REQUIRED_FIELDS if k not in entry]
    if missing:
        sys.exit(f"switch #{index} is missing fields {', '.join(missing)}")
    size_fields = [key for key in SWITCH_SIZE_FIELDS if key in entry]
    if len(size_fields) != 1:
        sys.exit(f"switch #{index}: exactly one of these fields is required: "
                 + ", ".join(SWITCH_SIZE_FIELDS))
    size_field = size_fields[0]
    try:
        element_count = int(entry[size_field])
    except (TypeError, ValueError):
        sys.exit(f"switch #{index}: {size_field} must be an integer")
    element_size = SWITCH_STORAGE_BYTES.get(entry["storagetype"])
    if element_count <= 0 or element_size is None:
        sys.exit(f"switch #{index}: invalid size or storagetype")
    expected_bytes = element_count * element_size
    states = entry.get("state", [])
    if not isinstance(states, list) or len(states) < 2:
        sys.exit(f"switch #{index}: state must be an array with at least two states")

    attrs = ['type="Switch"']
    for key in SWITCH_FIELDS:
        if key not in entry:
            continue
        value = (
            presentation.category_name(entry[key])
            if key == "category"
            else entry[key]
        )
        attrs.append(f'{key}="{att(value)}"')
    out = wrap("    ", "<table", attrs, ">")
    if entry.get("description"):
        out.append(f"      <description>{att(entry['description'])}</description>")
    for state_index, state in enumerate(states, 1):
        if not isinstance(state, dict):
            sys.exit(f"switch #{index}, state #{state_index} must be a TOML table")
        unknown_state = sorted(set(state) - {"name", "data"})
        if unknown_state:
            sys.exit(f"switch #{index}, state #{state_index} contains unknown fields "
                     + ", ".join(unknown_state))
        missing_state = [k for k in ("name", "data") if k not in state]
        if missing_state:
            sys.exit(f"switch #{index}, state #{state_index} is missing fields "
                     + ", ".join(missing_state))
        tokens = str(state["data"]).split()
        try:
            raw = (bytes.fromhex(" ".join(tokens))
                   if all(len(token) == 2 for token in tokens) else b"")
        except ValueError:
            raw = b""
        if len(tokens) != expected_bytes or len(raw) != expected_bytes:
            sys.exit(f"switch #{index}, state #{state_index}: data must contain "
                     f"{expected_bytes} hexadecimal bytes")
        out += wrap("      ", "<state",
                    [f'name="{att(state["name"])}"', f'data="{att(state["data"])}"'],
                    "/>")
    out.append("    </table>")
    return out


def evidence_lines(m, axes, rom):
    """Describe what is known about a map and at which confidence level."""
    shape = (f'{m["width"]}x{m["height"]}' if m["dims"] == 2 else f'{m["width"]}')
    via = ""
    if m["wrappers"]:
        via = (f'; entry {", ".join(hexa(w) for w in sorted(m["wrappers"]))} '
               f'({m["family"]}, core {", ".join(hexa(k) for k in sorted(m["kernels"]))})')
    lines = [f'{hexa(m["addr"])}  {shape} {m["storagetype"]}  '
             f'map [{m["confidence"]}]{via}']
    if m["accessors"]:
        lines.append("accessor " + ", ".join(hexa(a) for a in sorted(m["accessors"]))
                     + "; r4 operand: " + ", ".join(sorted(m["resolver_kinds"])))
    scale = f'scaling {m["scale_expr"]} {m["units"]}'
    if m["scale_conf"]:
        scale += f' [{m["scale_conf"]}]'
    for role, key in (("Y", "axis_x"), ("X", "axis_y")):
        for x in (axes[a] for a in m[key]):
            lbl = "axis" if m["dims"] == 1 else f"{role} Axis"
            scale += (f'; {lbl} {hexa(x["addr"])} {x["kind"]}'
                      + (f' [{x["scale_conf"]}]' if x["scale_conf"] else ""))
    lines.append(scale)
    _, diagnostic = diagnostic_context.summarize(
        m.get("diagnostic_bindings", [])
    )
    if diagnostic:
        lines.append("static diagnostic context: " + "; ".join(diagnostic))
    if m["note"]:
        lines.append(m["note"])
    lines.append(f"Analysis and method - defs/{rom}.notes.md")
    return lines


def table_axes_xml(m, o, ovr, axes):
    """Build table axes: graph axes for interpolated maps and static axes for direct row-major."""
    out = []
    if m["dims"] == 2:
        if m["axis_x"] and m["axis_y"]:
            out += axis_xml("X Axis", axes[m["axis_y"][0]], ovr, "sizex")
            out += axis_xml("Y Axis", axes[m["axis_x"][0]], ovr, "sizey")
        else:
            out += static_axis_xml(
                o["static_axis_x"], o.get("static_axis_x_name", "X Axis"),
                "Static X Axis", "sizex",
            )
            out += static_axis_xml(
                o["static_axis_y"], o.get("static_axis_y_name", "Y Axis"),
                "Static Y Axis", "sizey",
            )
    elif m["axis_x"]:
        out += axis_xml("X Axis", axes[m["axis_x"][0]], ovr, "sizex")
    elif m["steps"]:
        # Implicit axis: no array exists; points are 0..(n-1) at the input step.
        step = m["steps"][0]
        out += static_axis_xml([i * step for i in range(m["width"])],
                               f"Raw input (step {step})")
    else:
        # Compare family: no lookup exists; branching selects cells and overrides label branches.
        out += static_axis_xml(o["static_axis"], "Selector")
    return out


def table_xml(m, ovr, axes, rom):
    o = ovr["table"][m["addr"]]
    cat = presentation.category_name(o["category"])
    dims = "3D" if m["dims"] == 2 else "2D"
    # RomRaider shape: sizex is columns (r6 axis), while sizey is rows (r5 axis).
    # A one-dimensional map has one axis whose length is sizex.
    if m["dims"] == 2 and m["family"] == "direct-row-major":
        size = [f'sizex="{m["width"]}"', f'sizey="{m["height"]}"']
    elif m["dims"] == 2:
        size = [f'sizex="{m["height"]}"', f'sizey="{m["width"]}"']
    else:
        size = [f'sizex="{m["width"]}"']
    attrs = [f'type="{dims}"', f'name="{att(o["name"])}"',
             f'category="{att(cat)}"',
             f'storagetype="{att(m["storagetype"])}"',
             f'storageaddress="{hexa(m["addr"])}"'] + size + ['endian="big"']
    if o.get("mask"):
        attrs.append(f'mask="{att(o["mask"])}"')
    out = [comment(evidence_lines(m, axes, rom))]
    out += wrap("    ", "<table", attrs, ">")
    out.append(scaling(m["units"], m["scale_expr"], m["to_byte"], m["scale_conf"],
                       o.get("format", "0"), o.get("fine"), o.get("coarse"), 6))

    # The emission gate permits exactly one axis per map edge, so only such maps reach here.
    out += table_axes_xml(m, o, ovr, axes)
    out.append("    </table>")
    return out


def masked_view_xml(m, view, ovr, axes, rom):
    """Build an additional masked view of the same cells without duplicating the Map fact."""
    source = ovr["table"][m["addr"]]
    dims = "3D" if m["dims"] == 2 else "2D"
    if m["dims"] == 2 and m["family"] == "direct-row-major":
        size = [f'sizex="{m["width"]}"', f'sizey="{m["height"]}"']
    elif m["dims"] == 2:
        size = [f'sizex="{m["height"]}"', f'sizey="{m["width"]}"']
    else:
        size = [f'sizex="{m["width"]}"']
    shape = (f'{m["width"]}x{m["height"]}' if m["dims"] == 2 else f'{m["width"]}')
    lines = [
        f'{hexa(m["addr"])}  {shape} {m["storagetype"]}  masked view '
        f'0x{view["mask"]} [{m["confidence"]}]',
        f'Semantics source: {m["semantics"]}',
    ]
    _, diagnostic = diagnostic_context.summarize(
        m.get("diagnostic_bindings", [])
    )
    if diagnostic:
        lines.append("Static diagnostic context: " + "; ".join(diagnostic))
    lines.append(f"Analysis and method - defs/{rom}.notes.md")
    attrs = [
        f'type="{dims}"',
        f'name="{att(view["name"])}"',
        f'category="{att(presentation.category_name(view["category"]))}"',
        f'storagetype="{att(m["storagetype"])}"',
        f'storageaddress="{hexa(m["addr"])}"',
    ] + size + ['endian="big"', f'mask="{att(view["mask"])}"']
    out = [comment(lines)]
    out += wrap("    ", "<table", attrs, ">")
    out.append(scaling(
        view["units"], view["expression"], view["to_byte"], m["confidence"],
        view.get("format", "0"), view.get("fine"), view.get("coarse"), 6,
    ))
    out += table_axes_xml(m, source, ovr, axes)
    out.append("    </table>")
    return out


def masked_views(ovr, emitted):
    """Validate presentation-only masked views and group them by source map."""
    entries = ovr.get("masked_view", [])
    if isinstance(entries, dict):
        entries = [entries]
    if not isinstance(entries, list):
        sys.exit("masked_view must be a table or an array of tables")
    by_source = {}
    for index, entry in enumerate(entries, 1):
        if not isinstance(entry, dict):
            sys.exit(f"masked_view #{index} must be a TOML table")
        unknown = sorted(set(entry) - set(MASKED_VIEW_FIELDS))
        if unknown:
            sys.exit(f"masked_view #{index} contains unknown fields "
                     + ", ".join(unknown))
        required = ("source", "name", "category", "mask", "units", "expression", "to_byte")
        missing = [key for key in required if key not in entry]
        if missing:
            sys.exit(f"masked_view #{index} is missing fields " + ", ".join(missing))
        view = dict(entry)
        view["source"] = str(view["source"]).lower()
        view["mask"] = str(view["mask"]).upper()
        if view["source"] not in emitted:
            sys.exit(f"masked_view #{index}: source map {view['source']} "
                     "does not pass the emission gate")
        try:
            mask = int(view["mask"], 16)
        except ValueError:
            sys.exit(f"masked_view #{index}: mask is not a hexadecimal number")
        bits = {"uint8": 8, "uint16": 16, "uint32": 32}.get(emitted[view["source"]]["storagetype"])
        if not bits or mask <= 0 or mask >= (1 << bits):
            sys.exit(f"masked_view #{index}: mask is outside "
                     f"{emitted[view['source']]['storagetype']}")
        primary_mask = ovr["table"][view["source"]].get("mask")
        if primary_mask and int(str(primary_mask), 16) & mask:
            sys.exit(f"masked_view #{index}: mask overlaps the primary table")
        by_source.setdefault(view["source"], []).append(view)
    return entries, by_source


def emittable(m, axes, ovr=None):
    """Return the section 9 emission-gate failure reason, or None when a map can be emitted."""
    ovr = ovr or {}
    if m["role"] != "table":
        return f'role {m["role"]}'
    if not m["semantics"]:
        return "missing semantics"
    if not m["scale_expr"]:
        return "missing scaling"
    if LEVELS.index(m["confidence"]) < LEVELS.index("candidate"):
        return f'confidence {m["confidence"]}'
    for key in ("axis_x", "axis_y"):
        if len(m[key]) > 1:
            return (f'branching selects the axis: {", ".join(hexa(a) for a in m[key])} '
                    f'- Stage 6 input')
        for a in m[key]:
            if LEVELS.index(axes[a]["confidence"]) < LEVELS.index("candidate"):
                return f'axis {hexa(a)} exists only as fallback evidence'
            if not axes[a]["kind"]:
                return f'axis {hexa(a)} is not annotated'
    if m["dims"] == 2 and not (m["axis_x"] and m["axis_y"]):
        if m["axis_x"] or m["axis_y"]:
            return "only one axis was recovered for a 2D map"
        if m["family"] != "direct-row-major":
            return "not every axis was recovered for a 2D map"
        if len(ovr.get("static_axis_x", [])) != m["width"]:
            return f'a Static X Axis with {m["width"]} points is required'
        if len(ovr.get("static_axis_y", [])) != m["height"]:
            return f'a Static Y Axis with {m["height"]} points is required'
    # A one-dimensional map axis is defined by an array (explicit), an input step (implicit),
    # or not at all for the compare family, where branching selects cells without a lookup.
    if m["dims"] == 1 and not (m["axis_x"] or m["steps"] or m["family"] == "compare"):
        return "axis is defined by neither an array nor a step"
    return None


def main():
    rom = sys.argv[1] if len(sys.argv) > 1 else "JK08A"
    romraider_path = (
        sys.argv[2] if len(sys.argv) > 2 else os.path.join(DEFS, f"{rom}.xml")
    )
    tunerpro_path = (
        sys.argv[3] if len(sys.argv) > 3
        else os.path.splitext(romraider_path)[0] + ".xdf"
    )
    ovr_path = os.path.join(DEFS, f"{rom}.overrides.toml")
    if not os.path.exists(ovr_path):
        sys.exit(f"presentation layer not found: {ovr_path}")
    with open(ovr_path, "rb") as f:
        ovr = tomllib.load(f)

    maps, axes = fetch(rom)
    emit, skipped = [], []
    for a, m in sorted(maps.items()):
        o = ovr.get("table", {}).get(a, {})
        why = emittable(m, axes, o)
        if why:
            if m["semantics"] and m["role"] == "table":
                skipped.append((a, m["semantics"], why))
            continue
        if not o.get("name") or not o.get("category"):
            sys.exit(f"map {hexa(a)} ({m['semantics']}) passes the emission gate but has "
                     f"no name or category; declare [table.{a}] in "
                     f"{os.path.basename(ovr_path)}")
        # For a map without an axis, only an override can provide cell labels: branching
        # names them rather than the graph.
        if m["dims"] == 1 and not (m["axis_x"] or m["steps"]):
            if len(o.get("static_axis", [])) != m["width"]:
                sys.exit(f"[table.{a}]: the map has no axis and branching selects cells; "
                         f"static_axis with {m['width']} labels is required")
        elif m["dims"] == 1 and "static_axis" in o:
            sys.exit(f"[table.{a}]: static_axis overlaps graph axis "
                     f"{hexa((m['axis_x'] or ['-'])[0])}; overrides must not replace it")
        if m["dims"] == 2 and m["axis_x"] and m["axis_y"]:
            static_keys = {"static_axis_x", "static_axis_y"} & set(o)
            if static_keys:
                sys.exit(f"[table.{a}]: static axis overlaps graph axes: "
                         + ", ".join(sorted(static_keys)))
        emit.append(m)
    unknown = sorted(set(ovr.get("table", {})) - {m["addr"] for m in emit})
    if unknown:
        sys.exit("override exists for a map not emitted into the definition: "
                 + ", ".join(f"[table.{a}]" for a in unknown)
                 + " - either the address is wrong or the map does not pass the gate")
    for a in sorted(ovr.get("axisview", {})):
        if a not in axes:
            sys.exit(f"[axisview.{a}] overrides an axis absent from the graph")
        if not axes[a]["kind"]:
            sys.exit(f"[axisview.{a}]: the axis is not annotated in {rom}.axes.csv "
                     f"and cannot be emitted")

    view_entries, views_by_source = masked_views(
        ovr, {m["addr"]: m for m in emit}
    )
    native_switches = ovr.get("switch", [])
    if isinstance(native_switches, dict):
        native_switches = [native_switches]
    if not isinstance(native_switches, list):
        sys.exit(f"{os.path.basename(ovr_path)}: switch must be a table "
                 "or an array of tables")
    native_switches = list(native_switches)
    image = romkit.load(rom)
    records = dtc_records(rom, image=image)
    dtc_entries = dtc_switches(rom, records=records)
    switches = list(native_switches)
    switches += dtc_entries

    body = []
    for index, entry in enumerate(switches, 1):
        body += switch_xml(entry, index) + [""]
    for m in sorted(emit, key=lambda m: (ovr["table"][m["addr"]].get("order", 1 << 20),
                                         m["addr"])):
        body += table_xml(m, ovr, axes, rom) + [""]
        for view in views_by_source.get(m["addr"], []):
            body += masked_view_xml(m, view, ovr, axes, rom) + [""]
    for a in sorted(ovr.get("axisview", {}),
                    key=lambda a: (ovr["axisview"][a].get("order", 1 << 20), a)):
        o, x = ovr["axisview"][a], axes[a]
        category = presentation.category_name(o["category"])
        body += [comment([f'{hexa(a)}  axis with {x["len"]} points {x["storagetype"]}, '
                          f'{x["kind"]}' + (f' [{x["scale_conf"]}]'
                                            if x["scale_conf"] else ""),
                          x["note"] or "", f"Analysis and method - defs/{rom}.notes.md"])]
        body += wrap("    ", "<table", ['type="2D"', f'name="{att(o["name"])}"',
                                        f'category="{att(category)}"',
                                        f'storagetype="{att(x["storagetype"])}"',
                                        f'storageaddress="{hexa(a)}"',
                                        f'sizex="{x["len"]}"', 'endian="big"'], ">")
        body.append(scaling(x["units"], x["scale_expr"], x["to_byte"], x["scale_conf"],
                            o.get("format", "0"), o.get("fine"), o.get("coarse"), 6))
        body += static_axis_xml(list(range(x["len"])))
        body += ["    </table>", ""]

    romid = ovr["rom"]
    missing = [f for f in ROMID_FIELDS if f not in romid]
    if missing:
        sys.exit(f"{os.path.basename(ovr_path)}: [rom] is missing fields {', '.join(missing)}")
    sources = ["Memgraph (facts)"]
    if dtc_entries:
        sources.append(f"defs/{rom}.dtc.csv (DTC)")
    sources.append(f"defs/{rom}.overrides.toml (presentation)")
    head = [comment([f"RomRaider definition for {rom}. Generated by tools/mapkit/emit_def.py from "
                     + ", ".join(sources) + ".",
                     "Edits to this file do not survive the next run.",
                     "Edit the sources: defs/<rom>.findings.csv, <rom>.axes.csv, "
                     "<rom>.interp.csv, <rom>.dtc.csv, <rom>.overrides.toml.", ""]
                    + romid.get("comment", {}).get("text", "").split("\n"), indent=0),
            "<roms>", "  <rom>", "    <romid>"]
    head += [f"      <{f}>{att(romid[f])}</{f}>" for f in ROMID_FIELDS]
    head += ["    </romid>", ""]
    checksums = ovr.get("checksum", [])
    if isinstance(checksums, dict):
        checksums = [checksums]
    if not isinstance(checksums, list):
        sys.exit(f"{os.path.basename(ovr_path)}: checksum must be a table "
                 "or an array of tables")
    for i, c in enumerate(checksums, 1):
        unknown = sorted(set(c) - set(CHECKSUM_FIELDS) - {"comment"})
        if unknown:
            sys.exit(f"{os.path.basename(ovr_path)}: checksum #{i} contains "
                     f"unknown fields {', '.join(unknown)}")
        required = (
            ("type", "path", "expectedsize",
             "l1loc", "l1stock", "l1patched",
             "l2loc", "l2stock", "l2patched")
            if "path" in c else
            ("type", "start", "end", "sumloc", "xorloc")
        )
        missing = [k for k in required if k not in c]
        if missing:
            sys.exit(f"{os.path.basename(ovr_path)}: checksum #{i} is missing fields "
                     f"{', '.join(missing)}")
        if "comment" in c:
            head.append(comment(c["comment"].split("\n")))
        head += wrap("    ", "<checksum",
                     [f'{k}="{att(c[k])}"' for k in CHECKSUM_FIELDS if k in c],
                     "/>") + [""]

    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n' + "\n".join(head + body).rstrip()
           + "\n  </rom>\n</roms>\n")
    with open(romraider_path, "w") as f:
        f.write(xml)

    xdf, xdf_stats = tunerpro.render(
        rom,
        image,
        emit,
        axes,
        ovr,
        views_by_source,
        records,
        native_switches,
    )
    with open(tunerpro_path, "w") as f:
        f.write(xdf)

    print(f"{os.path.relpath(romraider_path)}: {len(emit)} calibration tables, "
          f"{len(dtc_entries)} DTC switches, "
          f"{len(view_entries)} masked views, {len(ovr.get('axisview', {}))} reference axes, "
          f"{len(switches)} switches")
    print(
        f"{os.path.relpath(tunerpro_path)}: "
        f"{xdf_stats['calibration_tables']} calibration tables, "
        f"{xdf_stats['masked_views']} masked views, "
        f"{xdf_stats['axis_views']} reference axes, "
        f"{xdf_stats['individual_dtc_patches']} individual DTC patches, "
        f"{xdf_stats['group_dtc_patches']} group DTC patches "
        f"({xdf_stats['group_dtc_ranges']} group ranges), "
        f"{xdf_stats['other_patches']} other patches"
    )
    lvl = {}
    for m in emit:
        lvl[m["confidence"]] = lvl.get(m["confidence"], 0) + 1
    print("  confidence levels: " + ", ".join(f"{k}={lvl[k]}" for k in LEVELS if k in lvl))
    cand = [m for m in emit if m["scale_conf"] and m["scale_conf"] != "code"]
    print(f"  scaling not established by code: {len(cand)} "
          f"({', '.join(hexa(m['addr']) for m in cand)})")
    print(f"  catalog: {len(maps)} maps; not emitted: {len(maps) - len(emit)}")
    for a, sem, why in skipped:
        print(f"    {hexa(a)} {sem}: {why}")
    nosem = sum(1 for m in maps.values() if not m["semantics"] and m["role"] == "table")
    print(f"    {nosem} additional table-role maps lack semantics and remain open ledger work")


if __name__ == "__main__":
    main()
