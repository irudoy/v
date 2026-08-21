#!/usr/bin/env python3
# Definition generator contract: tools/map-analysis-pipeline.md.
# Memgraph (facts) + defs/<rom>.dtc.csv (DTC) + defs/<rom>.overrides.toml (presentation)
# -> defs/<rom>.xml (RomRaider) + defs/<rom>.xdf (TunerPro).
#
# Declare each fact once: address,
# shape, element, axes, scaling, and confidence live in the graph, populated by the resolver
# census and the manual layer; name, category, order, and editor increments live in overrides.
# The definition file is not a source for either set, and edits to it do not survive the next
# run.
#
# Definition output has two independent gates. The presentation layer can explicitly hide maps
# that are not intended for tuner-facing definitions; every other map reaches the definition
# gate, which requires table role, semantics, scaling, confidence, and complete geometry. Maps
# hidden by presentation remain available in the canonical graph and ledger. An explicit
# emit=true is strict: a selected map that cannot be rendered stops generation. Default-visible
# maps that lack sufficient evidence are rejected and reported without blocking valid output.
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
# axes. For an implicit one-dimensional map, a reviewed static_axis override may replace
# the generated raw input nodes with physical labels; the lookup step and geometry remain
# graph facts.
#
# Invocation:
# uv run python tools/mapkit/emit_def.py \
#   [<rom>|all|--all] [<romraider-out>] [<tunerpro-out>]
import copy
import csv
from dataclasses import dataclass
import html
import os
import sys
import tempfile
import textwrap
import tomllib
from neo4j import GraphDatabase

BOLT = "bolt://localhost:7687"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DEFS = os.path.join(ROOT, "defs")
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if __package__:
    from . import (
        definition_targets,
        definition_projections,
        map_switching,
        presentation,
        rolling_launch,
        rom as romkit,
        tunerpro,
    )
    from tools import diagnostic_context
else:
    sys.path.insert(0, os.path.dirname(HERE))
    from mapkit import (
        definition_targets,
        definition_projections,
        map_switching,
        presentation,
        rolling_launch,
        rom as romkit,
        tunerpro,
    )
    import diagnostic_context
from tools import rom_sources

LEVELS = ("pattern", "candidate", "code", "silicon")   # confidence ladder from section 5

ROMID_FIELDS = definition_targets.ROMID_FIELDS
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
BITWISE_SWITCH_FIELDS = (
    "name", "category", "storageaddress", "storagetype", "endian",
    "userlevel",
)
BITWISE_SWITCH_REQUIRED_FIELDS = BITWISE_SWITCH_FIELDS
BITWISE_SWITCH_STORAGE_BITS = {"uint8": 8, "uint16": 16, "uint32": 32}
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
PRESENTATION_FIELDS = ("default_emit",)
MAP_SWITCHING_FIELDS = ("enabled",)
ROLLING_LAUNCH_FIELDS = ("enabled",)
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
            presentation.romraider_category_name(entry[key])
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


def bitwise_switches(overrides):
    """Validate and normalize native RomRaider bitwise switches."""
    entries = overrides.get("bitwise_switch", [])
    if isinstance(entries, dict):
        entries = [entries]
    if not isinstance(entries, list):
        sys.exit("bitwise_switch must be a table or an array of tables")

    normalized = []
    for index, entry in enumerate(entries, 1):
        if not isinstance(entry, dict):
            sys.exit(f"bitwise_switch #{index} must be a TOML table")
        unknown = sorted(
            set(entry) - set(BITWISE_SWITCH_FIELDS) - {"description", "bit"}
        )
        if unknown:
            sys.exit(
                f"bitwise_switch #{index} contains unknown fields "
                + ", ".join(unknown)
            )
        missing = [
            key for key in BITWISE_SWITCH_REQUIRED_FIELDS if key not in entry
        ]
        if missing:
            sys.exit(
                f"bitwise_switch #{index} is missing fields "
                + ", ".join(missing)
            )
        storage_bits = BITWISE_SWITCH_STORAGE_BITS.get(entry["storagetype"])
        if storage_bits is None:
            sys.exit(
                f"bitwise_switch #{index}: unsupported storagetype "
                f"{entry['storagetype']}"
            )
        try:
            address = int(str(entry["storageaddress"]), 0)
        except ValueError:
            sys.exit(
                f"bitwise_switch #{index}: storageaddress must be hexadecimal"
            )
        if address < 0:
            sys.exit(f"bitwise_switch #{index}: storageaddress is negative")

        bits = entry.get("bit", [])
        if isinstance(bits, dict):
            bits = [bits]
        if not isinstance(bits, list) or not bits:
            sys.exit(
                f"bitwise_switch #{index}: bit must be a non-empty array"
            )
        normalized_bits = []
        names = set()
        positions = set()
        for bit_index, bit in enumerate(bits, 1):
            if not isinstance(bit, dict):
                sys.exit(
                    f"bitwise_switch #{index}, bit #{bit_index} must be a table"
                )
            unknown_bit = sorted(set(bit) - {"name", "position"})
            if unknown_bit:
                sys.exit(
                    f"bitwise_switch #{index}, bit #{bit_index} contains unknown "
                    "fields " + ", ".join(unknown_bit)
                )
            missing_bit = [
                key for key in ("name", "position") if key not in bit
            ]
            if missing_bit:
                sys.exit(
                    f"bitwise_switch #{index}, bit #{bit_index} is missing fields "
                    + ", ".join(missing_bit)
                )
            name = str(bit["name"]).strip()
            try:
                position = int(bit["position"])
            except (TypeError, ValueError):
                sys.exit(
                    f"bitwise_switch #{index}, bit #{bit_index}: position must "
                    "be an integer"
                )
            if not name:
                sys.exit(
                    f"bitwise_switch #{index}, bit #{bit_index}: name is empty"
                )
            if name in names:
                sys.exit(
                    f"bitwise_switch #{index}: duplicate bit name {name}"
                )
            if position in positions:
                sys.exit(
                    f"bitwise_switch #{index}: duplicate bit position {position}"
                )
            if position < 0 or position >= storage_bits:
                sys.exit(
                    f"bitwise_switch #{index}, bit #{bit_index}: position "
                    f"{position} is outside {entry['storagetype']}"
                )
            names.add(name)
            positions.add(position)
            normalized_bits.append({"name": name, "position": position})

        normalized_entry = dict(entry)
        normalized_entry["storageaddress"] = f"0x{address:X}"
        normalized_entry["bit"] = normalized_bits
        normalized.append(normalized_entry)
    return normalized


def bitwise_switch_xml(entry, index):
    """Build one TableBitwiseSwitch containing independent checkboxes."""
    attrs = ['type="BitwiseSwitch"']
    for key in BITWISE_SWITCH_FIELDS:
        value = (
            presentation.romraider_category_name(entry[key])
            if key == "category"
            else entry[key]
        )
        attrs.append(f'{key}="{att(value)}"')
    out = wrap("    ", "<table", attrs, ">")
    if entry.get("description"):
        out.append(f"      <description>{att(entry['description'])}</description>")
    for bit in entry["bit"]:
        out += wrap(
            "      ",
            "<bit",
            [
                f'name="{att(bit["name"])}"',
                f'position="{bit["position"]}"',
            ],
            "/>",
        )
    out.append("    </table>")
    return out


def evidence_lines(m, axes, source_rom):
    """Describe what is known about a map and at which confidence level."""
    shape = (f'{m["width"]}x{m["height"]}' if m["dims"] == 2 else f'{m["width"]}')
    via = ""
    if m["wrappers"]:
        via = (f'; entry {", ".join(hexa(w) for w in sorted(m["wrappers"]))} '
               f'({m["family"]}, core {", ".join(hexa(k) for k in sorted(m["kernels"]))})')
    source = m.get("map_switching_source")
    slot = m.get("map_switching_slot")
    if source is not None:
        lines = [
            f'{hexa(m["addr"])}  {shape} {m["storagetype"]}  '
            f'common-definition Map {slot} storage projected from '
            f'{hexa(source)} '
            f'[{m["confidence"]}]'
        ]
        if slot == 1:
            lines.append("Map 1 uses canonical stock storage")
        else:
            lines.append(
                "Stock firmware does not reference this erased allocation; "
                "runtime use requires the project map-switching patch"
            )
    else:
        lines = [f'{hexa(m["addr"])}  {shape} {m["storagetype"]}  '
                 f'map [{m["confidence"]}]{via}']
    if m["accessors"]:
        prefix = "canonical accessor " if source is not None else "accessor "
        lines.append(prefix + ", ".join(hexa(a) for a in sorted(m["accessors"]))
                     + "; r4 operand: " + ", ".join(sorted(m["resolver_kinds"])))
    if source is not None:
        lines.append(
            "Runtime redirection and storage ownership - "
            "patches/map-switching-selector.md"
        )
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
    lines.append(f"Analysis and method - defs/{source_rom}.notes.md")
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
        # An implicit axis has no ROM array. Presentation may replace its raw
        # nodes with reviewed physical labels while preserving table geometry.
        if "static_axis" in o:
            out += static_axis_xml(
                o["static_axis"], o.get("static_axis_name", "X Axis")
            )
        else:
            step = m["steps"][0]
            out += static_axis_xml([i * step for i in range(m["width"])],
                                   f"Raw input (step {step})")
    else:
        # A direct no-axis family obtains labels from the presentation layer.
        out += static_axis_xml(
            o["static_axis"], o.get("static_axis_name", "Selector")
        )
    return out


def table_xml(m, ovr, axes, source_rom):
    o = ovr["table"][m["addr"]]
    cat = presentation.romraider_category_name(o["category"])
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
    out = [comment(evidence_lines(m, axes, source_rom))]
    out += wrap("    ", "<table", attrs, ">")
    out.append(scaling(m["units"], m["scale_expr"], m["to_byte"], m["scale_conf"],
                       o.get("format", "0"), o.get("fine"), o.get("coarse"), 6))

    # The emission gate permits exactly one axis per map edge, so only such maps reach here.
    out += table_axes_xml(m, o, ovr, axes)
    out.append("    </table>")
    return out


def masked_view_xml(m, view, ovr, axes, source_rom):
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
    source_address = m.get("map_switching_source")
    source_text = (
        f'; common-definition Map {m["map_switching_slot"]} storage '
        f'projected from '
        f'{hexa(source_address)}'
        if source_address is not None
        else ""
    )
    lines = [
        f'{hexa(m["addr"])}  {shape} {m["storagetype"]}  masked view '
        f'0x{view["mask"]} [{m["confidence"]}]{source_text}',
        f'Semantics source: {m["semantics"]}',
    ]
    _, diagnostic = diagnostic_context.summarize(
        m.get("diagnostic_bindings", [])
    )
    if diagnostic:
        lines.append("Static diagnostic context: " + "; ".join(diagnostic))
    lines.append(f"Analysis and method - defs/{source_rom}.notes.md")
    attrs = [
        f'type="{dims}"',
        f'name="{att(view["name"])}"',
        f'category="{att(presentation.romraider_category_name(view["category"]))}"',
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


def presentation_default_emit(ovr):
    """Return the default tuner-definition visibility selected by the presentation layer."""
    entry = ovr.get("presentation", {})
    if not isinstance(entry, dict):
        sys.exit("presentation must be a TOML table")
    unknown = sorted(set(entry) - set(PRESENTATION_FIELDS))
    if unknown:
        sys.exit("presentation contains unknown fields " + ", ".join(unknown))
    value = entry.get("default_emit", True)
    if not isinstance(value, bool):
        sys.exit("presentation.default_emit must be a boolean")
    return value


def table_emit_enabled(entry, default, address=None):
    """Apply an optional per-table visibility override to the presentation default."""
    value = entry.get("emit", default)
    if not isinstance(value, bool):
        prefix = f"[table.{address}]: " if address else ""
        sys.exit(prefix + "emit must be a boolean")
    return value


def map_switching_enabled(overrides):
    """Return whether the common definition includes map-switching slots."""
    config = overrides.get("map_switching")
    if config is None:
        return False
    if not isinstance(config, dict):
        sys.exit("map_switching must be a TOML table")
    unknown = sorted(set(config) - set(MAP_SWITCHING_FIELDS))
    if unknown:
        sys.exit(
            "map_switching contains unknown fields "
            + ", ".join(unknown)
        )
    enabled = config.get("enabled", False)
    if not isinstance(enabled, bool):
        sys.exit("map_switching.enabled must be a boolean")
    return enabled


def rolling_launch_enabled(overrides):
    """Return whether the common definition includes Rolling Launch controls."""
    config = overrides.get("rolling_launch")
    if config is None:
        return False
    if not isinstance(config, dict):
        sys.exit("rolling_launch must be a TOML table")
    unknown = sorted(set(config) - set(ROLLING_LAUNCH_FIELDS))
    if unknown:
        sys.exit(
            "rolling_launch contains unknown fields "
            + ", ".join(unknown)
        )
    enabled = config.get("enabled", False)
    if not isinstance(enabled, bool):
        sys.exit("rolling_launch.enabled must be a boolean")
    return enabled


@dataclass(frozen=True)
class AppliedDefinitionProjections:
    maps: dict
    overrides: dict
    map_switching: object | None
    rolling_launch: object | None

    @property
    def slot_table_count(self):
        return self.map_switching.slot_table_count if self.map_switching else 0

    @property
    def slot_masked_view_count(self):
        return (
            self.map_switching.slot_masked_view_count
            if self.map_switching else 0
        )

    @property
    def slot_editor_view_count(self):
        return (
            self.map_switching.slot_editor_view_count
            if self.map_switching else 0
        )


def apply_definition_projections(
    rom,
    maps,
    overrides,
    layout_rom=None,
    map_layout=None,
    launch_layout=None,
):
    """Apply optional derived layouts inside the common ROM definition."""
    layout_rom = layout_rom or rom
    switching_enabled = map_switching_enabled(overrides)
    launch_enabled = rolling_launch_enabled(overrides)
    if not switching_enabled and not launch_enabled:
        return maps, overrides, None

    launch_projection = None
    if launch_enabled:
        launch_layout = launch_layout or rolling_launch.load_layout()
        if launch_layout.rom != layout_rom:
            sys.exit(
                f"Rolling Launch layout targets {launch_layout.rom}, "
                f"not canonical source {layout_rom}"
            )
        launch_projection = rolling_launch.project_definition_model(
            maps, overrides, launch_layout, target_rom=rom
        )
        maps, overrides = launch_projection.maps, launch_projection.overrides

    switching_projection = None
    if switching_enabled:
        switching_layout = map_layout or map_switching.load_layout()
        if switching_layout.rom != layout_rom:
            sys.exit(
                f"map-switching layout targets {switching_layout.rom}, "
                f"not canonical source {layout_rom}"
            )
        switching_projection = map_switching.project_definition_model(
            maps, overrides, switching_layout
        )
        maps, overrides = (
            switching_projection.maps,
            switching_projection.overrides,
        )

    projection = AppliedDefinitionProjections(
        maps=maps,
        overrides=overrides,
        map_switching=switching_projection,
        rolling_launch=launch_projection,
    )
    return maps, overrides, projection


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
    # A one-dimensional map axis is defined by an array (explicit), an input
    # step (implicit), or static labels for a manually traced direct family.
    static_families = {"compare", "direct-indexed", "direct-scalar"}
    if m["dims"] == 1 and not (
        m["axis_x"] or m["steps"] or m["family"] in static_families
    ):
        return "axis is defined by neither an array nor a step"
    return None


def definition_failure(m, axes, ovr=None):
    """Return why a presentation-visible map cannot be rendered, or None."""
    ovr = ovr or {}
    why = emittable(m, axes, ovr)
    if why:
        return why
    if not ovr.get("name") or not ovr.get("category"):
        return "missing presentation name/category"
    # For a map without an axis, only an override can provide cell labels.
    if m["dims"] == 1 and not (m["axis_x"] or m["steps"]):
        if len(ovr.get("static_axis", [])) != m["width"]:
            return f'a static_axis with {m["width"]} labels is required'
    elif m["dims"] == 1 and "static_axis" in ovr:
        if m["axis_x"]:
            return f'static_axis overlaps graph axis {hexa(m["axis_x"][0])}'
        if len(ovr["static_axis"]) != m["width"]:
            return f'static_axis must contain {m["width"]} labels'
    if m["dims"] == 2 and m["axis_x"] and m["axis_y"]:
        static_keys = {"static_axis_x", "static_axis_y"} & set(ovr)
        if static_keys:
            return "static axis overlaps graph axes: " + ", ".join(sorted(static_keys))
    return None


def emit_target(
    rom,
    romraider_path=None,
    tunerpro_path=None,
    facts_cache=None,
    display_paths=None,
):
    """Generate one target-specific RomRaider XML and TunerPro XDF."""
    romraider_path = romraider_path or os.path.join(DEFS, f"{rom}.xml")
    tunerpro_path = tunerpro_path or os.path.splitext(romraider_path)[0] + ".xdf"
    try:
        target = definition_targets.load_target(rom)
    except definition_targets.DefinitionTargetError as error:
        sys.exit(str(error))
    source_rom = target.source
    ovr_path = os.path.join(DEFS, f"{source_rom}.overrides.toml")
    if not os.path.exists(ovr_path):
        sys.exit(f"presentation layer not found: {ovr_path}")
    with open(ovr_path, "rb") as f:
        ovr = definition_targets.materialize_overrides(
            target, tomllib.load(f)
        )

    if facts_cache is None:
        maps, axes = fetch(source_rom)
    else:
        if source_rom not in facts_cache:
            facts_cache[source_rom] = fetch(source_rom)
        maps, axes = copy.deepcopy(facts_cache[source_rom])
    source_catalog_map_count = len(maps)
    if target.source_model.inherited:
        map_rows = rom_sources.materialize_rows(
            target.source_model, "Map", list(maps.values())
        )
        axis_rows = rom_sources.materialize_rows(
            target.source_model, "Axis", list(axes.values())
        )
        maps = dict(zip(maps, map_rows))
        axes = dict(zip(axes, axis_rows))

    address_projection = None
    map_layout = None
    launch_layout = None
    layout_rom = source_rom
    if target.definition_projection is not None:
        source_table_overrides = ovr.get("table", {})
        if not isinstance(source_table_overrides, dict):
            sys.exit(f"{os.path.basename(ovr_path)}: table must be a TOML table")
        source_default_emit = presentation_default_emit(ovr)
        required_maps = {
            address
            for address, calibration in maps.items()
            if table_emit_enabled(
                source_table_overrides.get(address, {}),
                source_default_emit,
                address,
            )
            and definition_failure(
                calibration,
                axes,
                source_table_overrides.get(address, {}),
            ) is None
        }
        try:
            address_projection = definition_projections.apply_projection(
                target.definition_projection,
                maps,
                axes,
                ovr,
                target.image,
                required_maps=required_maps,
            )
            maps, axes, ovr = (
                address_projection.maps,
                address_projection.axes,
                address_projection.overrides,
            )
            if target.definition_projection.map_switching:
                map_layout = (
                    definition_projections.map_switching_definition_layout(
                        target.definition_projection
                    )
                )
            if target.definition_projection.rolling_launch:
                launch_layout = (
                    definition_projections.rolling_launch_definition_layout(
                        target.definition_projection
                    )
                )
            layout_rom = rom
        except definition_projections.DefinitionProjectionError as error:
            sys.exit(str(error))

    catalog_map_count = len(maps)
    maps, ovr, definition_projection = apply_definition_projections(
        rom,
        maps,
        ovr,
        layout_rom=layout_rom,
        map_layout=map_layout,
        launch_layout=launch_layout,
    )
    table_overrides = ovr.get("table", {})
    if not isinstance(table_overrides, dict):
        sys.exit(f"{os.path.basename(ovr_path)}: table must be a TOML table")
    unknown = sorted(set(table_overrides) - set(maps))
    if unknown:
        sys.exit("override exists for a map absent from the graph: "
                 + ", ".join(f"[table.{a}]" for a in unknown))
    default_emit = presentation_default_emit(ovr)
    emit, hidden, skipped = [], [], []
    for a, m in sorted(maps.items()):
        o = table_overrides.get(a, {})
        if not table_emit_enabled(o, default_emit, a):
            hidden.append(m)
            continue
        why = definition_failure(m, axes, o)
        if why:
            skipped.append((a, m["semantics"] or "unidentified map", why))
            if o.get("emit") is True:
                sys.exit(f"[table.{a}]: visible override does not pass the "
                         f"definition gate: {why}")
            continue
        emit.append(m)
    for a in sorted(ovr.get("axisview", {})):
        if a not in axes:
            sys.exit(f"[axisview.{a}] overrides an axis absent from the graph")
        if not axes[a]["kind"]:
            sys.exit(f"[axisview.{a}]: the axis is not annotated in "
                     f"{source_rom}.axes.csv "
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
    native_bitwise_switches = bitwise_switches(ovr)
    image = target.image
    dtc_rom = rom if target.definition_projection is not None else source_rom
    dtc_manifest = os.path.join(DEFS, f"{dtc_rom}.dtc.csv")
    records = dtc_records(
        rom, image=image, manifest_path=dtc_manifest
    )
    dtc_entries = dtc_switches(rom, records=records)
    switches = list(native_switches)
    switches += dtc_entries

    body = []
    for index, entry in enumerate(switches, 1):
        body += switch_xml(entry, index) + [""]
    for index, entry in enumerate(native_bitwise_switches, 1):
        body += bitwise_switch_xml(entry, index) + [""]
    for m in sorted(emit, key=lambda m: (ovr["table"][m["addr"]].get("order", 1 << 20),
                                         m["addr"])):
        body += table_xml(m, ovr, axes, source_rom) + [""]
        for view in views_by_source.get(m["addr"], []):
            body += masked_view_xml(m, view, ovr, axes, source_rom) + [""]
    for a in sorted(ovr.get("axisview", {}),
                    key=lambda a: (ovr["axisview"][a].get("order", 1 << 20), a)):
        o, x = ovr["axisview"][a], axes[a]
        category = presentation.romraider_category_name(o["category"])
        body += [comment([f'{hexa(a)}  axis with {x["len"]} points {x["storagetype"]}, '
                          f'{x["kind"]}' + (f' [{x["scale_conf"]}]'
                                            if x["scale_conf"] else ""),
                          x["note"] or "", f"Analysis and method - defs/{source_rom}.notes.md"])]
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
    sources = [
        "Memgraph (facts)"
        if source_rom == rom
        else f"Memgraph {source_rom} (canonical facts)"
    ]
    if target.definition_projection is not None:
        sources.append(
            f"defs/{target.definition_projection.address_path.name} "
            "(reviewed target addresses)"
        )
    if dtc_entries:
        sources.append(f"defs/{dtc_rom}.dtc.csv (DTC)")
    sources.append(f"defs/{source_rom}.overrides.toml (presentation)")
    sources.append("defs/rom-identities.toml (target identity)")
    if (
        definition_projection is not None
        and definition_projection.map_switching is not None
    ):
        sources.append(
            (
                "patches/rom-address-profiles.toml "
                "(target runtime map slots)"
                if target.definition_projection is not None
                else "patches/map-switching-layout.toml "
                "(common map-switching slots)"
            )
        )
    if (
        definition_projection is not None
        and definition_projection.rolling_launch is not None
    ):
        sources.append(
            "patches/rolling-launch-layout.toml (Rolling Launch controls)"
        )
    head = [comment([f"RomRaider definition for {rom}. Generated by tools/mapkit/emit_def.py from "
                     + ", ".join(sources) + ".",
                     "Edits to this file do not survive the next run.",
                     f"Edit the canonical sources under defs/{source_rom}.* and "
                     "the target identity in defs/rom-identities.toml.", ""]
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
        native_bitwise_switches,
        source_rom=source_rom,
        dtc_rom=dtc_rom,
        definition_projection=target.definition_projection,
    )
    with open(tunerpro_path, "w") as f:
        f.write(xdf)

    shown_xml, shown_xdf = display_paths or (romraider_path, tunerpro_path)
    print(f"{os.path.relpath(shown_xml)}: {len(emit)} calibration tables, "
          f"{len(dtc_entries)} DTC switches, "
          f"{len(view_entries)} masked views, {len(ovr.get('axisview', {}))} reference axes, "
          f"{len(switches)} switches, "
          f"{len(native_bitwise_switches)} bitwise switches")
    print(
        f"{os.path.relpath(shown_xdf)}: "
        f"{xdf_stats['calibration_tables']} calibration tables, "
        f"{xdf_stats['masked_views']} masked views, "
        f"{xdf_stats['bitwise_flags']} bitwise flags, "
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
    print(f"  catalog: {catalog_map_count} maps; "
          f"projected model: {len(maps)} maps; visible: {len(emit)}; "
          f"hidden by presentation: {len(hidden)}; "
          f"rejected by definition gate: {len(skipped)}")
    if address_projection is not None:
        print(
            "  relocated definition source: "
            f"source catalog={source_catalog_map_count}; "
            f"mapped maps={address_projection.mapped_map_count}; "
            f"mapped axes={address_projection.mapped_axis_count}; "
            "unsupported visible homologs="
            f"{len(address_projection.unsupported_required_maps)}"
        )
    if (
        definition_projection is not None
        and definition_projection.map_switching is not None
    ):
        print(
            "  common map-switching definition: "
            f"slot tables={definition_projection.slot_table_count}; "
            f"slot masked views={definition_projection.slot_masked_view_count}; "
            f"slot editor views={definition_projection.slot_editor_view_count}"
        )
    if (
        definition_projection is not None
        and definition_projection.rolling_launch is not None
    ):
        launch = definition_projection.rolling_launch
        print(
            "  Rolling Launch definition: "
            f"configuration tables={launch.table_count}; "
            f"switches={launch.switch_count}; "
            f"bitwise switches={launch.bitwise_switch_count}; "
            f"enable bits={launch.enable_bit_count}; "
            f"editor views={launch.editor_view_count}"
        )
    for a, sem, why in skipped:
        print(f"    {hexa(a)} {sem}: {why}")
    nosem = sum(1 for m in maps.values() if not m["semantics"] and m["role"] == "table")
    print(f"    {nosem} table-role maps lack semantics and remain open ledger work")


def emit_all(output_dir=DEFS):
    """Generate every registered target without partial output on render failure."""
    output_dir = os.fspath(output_dir)
    targets = definition_targets.registered_targets()
    facts_cache = {}
    with tempfile.TemporaryDirectory(
        prefix=".emit-def-", dir=output_dir
    ) as stage_dir:
        staged = []
        for rom in targets:
            final_xml = os.path.join(output_dir, f"{rom}.xml")
            final_xdf = os.path.join(output_dir, f"{rom}.xdf")
            stage_xml = os.path.join(stage_dir, f"{rom}.xml")
            stage_xdf = os.path.join(stage_dir, f"{rom}.xdf")
            emit_target(
                rom,
                stage_xml,
                stage_xdf,
                facts_cache=facts_cache,
                display_paths=(final_xml, final_xdf),
            )
            staged.append((stage_xml, final_xml))
            staged.append((stage_xdf, final_xdf))
        for staged_path, final_path in staged:
            os.replace(staged_path, final_path)


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        args = ["all"]
    if args[0].lower() in {"all", "--all"}:
        if len(args) != 1:
            sys.exit("all mode does not accept explicit output paths")
        emit_all()
        return
    if len(args) > 3:
        sys.exit(
            "usage: emit_def.py [<rom>|all|--all] "
            "[<romraider-out>] [<tunerpro-out>]"
        )
    emit_target(*args)


if __name__ == "__main__":
    main()
