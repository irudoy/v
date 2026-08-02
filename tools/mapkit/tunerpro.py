"""TunerPro XDF projection for the shared ECU definition model.

The caller supplies graph-backed maps and axes, the presentation overrides, and
validated DTC records. This module only translates that model to XDF 1.70. It
does not read Memgraph or treat the generated XDF as an annotation source.
"""

from collections import defaultdict
import re
import sys
import xml.etree.ElementTree as ET
import zlib

from .presentation import category_name


STORAGE_BITS = {"uint8": 8, "uint16": 16, "uint32": 32}
STORAGE_BYTES = {name: bits // 8 for name, bits in STORAGE_BITS.items()}

DTC_INDIVIDUAL_CATEGORY = "Diagnostics / DTC / Individual"
DTC_GROUP_CATEGORY = "Diagnostics / DTC / Disable Groups"
DTC_GROUP_NAMES = {
    "catalyst": "Catalyst",
    "evap": "EVAP",
    "manufacturer_specific": "Manufacturer Specific",
    "misfire": "Misfire",
    "nats": "NATS",
    "rear_o2": "Rear O2",
    "rear_o2_heater": "Rear O2 Heater",
}


class IdAllocator:
    """Allocate deterministic TunerPro-compatible 16-bit object identifiers."""

    def __init__(self):
        self.used = {0}

    def get(self, key):
        candidate = zlib.crc32(key.encode("utf-8")) & 0xFFFF
        candidate = candidate or 1
        while candidate in self.used:
            candidate = (candidate + 1) & 0xFFFF
            candidate = candidate or 1
        self.used.add(candidate)
        return f"0x{candidate:X}"


def node(parent, tag, text=None, **attributes):
    """Append an XML element and optionally set its text."""
    child = ET.SubElement(
        parent, tag, {key: str(value) for key, value in attributes.items()}
    )
    if text is not None:
        child.text = str(text)
    return child


def xdf_address(value):
    """Format an integer or hexadecimal string as an XDF address."""
    address = value if isinstance(value, int) else int(str(value), 16)
    return f"0x{address:X}"


def data_hex(data):
    return bytes(data).hex().upper()


def normalized_expression(expression):
    """Use one conventional raw-data variable name without changing functions."""
    return re.sub(r"\bx\b", "X", str(expression))


def decimal_places(fmt):
    text = str(fmt or "0")
    return len(text.rsplit(".", 1)[1]) if "." in text else 0


def units_with_confidence(units, confidence):
    if confidence and confidence != "code":
        return f"{units} [cand]"
    return units


def table_shape(calibration):
    """Return TunerPro row and column counts for the stored cell order."""
    if calibration["dims"] == 2 and calibration["family"] == "direct-row-major":
        return calibration["height"], calibration["width"]
    if calibration["dims"] == 2:
        return calibration["width"], calibration["height"]
    return 1, calibration["width"]


def dtc_entry_ranges(record):
    """Return every mutable range needed to disable one validated DTC record."""
    ranges = [{
        "name": f"{record['dtc']} [{record['index']}] descriptor",
        "address": record["record_addr"],
        "basedata": record["record"],
        "patchdata": bytes(len(record["record"])),
    }]
    if record["stock_attribute"] != record["disabled_attribute"]:
        ranges.append({
            "name": f"{record['dtc']} [{record['index']}] attribute",
            "address": record["attribute_addr"],
            "basedata": record["stock_attribute"],
            "patchdata": record["disabled_attribute"],
        })
    return ranges


def dtc_patches(rom, records):
    """Build one patch per DTC and one patch per manifest group."""
    individual = []
    grouped = defaultdict(list)
    for record in records:
        ranges = dtc_entry_ranges(record)
        individual.append({
            "key": f"dtc:{record['index']}",
            "title": (
                f"DTC {record['dtc']} [index {record['index']}] - "
                f"{record['note']}"
            ),
            "description": (
                f"Exact {rom} only. Applying this patch suppresses the DTC "
                "descriptor and its mutable attribute as one operation. It does "
                "not disable the physical monitor. This patch overlaps its DTC "
                "group patch; use individual or group scope consistently."
            ),
            "category": DTC_INDIVIDUAL_CATEGORY,
            "entries": ranges,
        })
        grouped[record["group"]].append(record)

    groups = []
    for group in sorted(grouped):
        group_records = grouped[group]
        entries = [
            entry
            for record in group_records
            for entry in dtc_entry_ranges(record)
        ]
        title = DTC_GROUP_NAMES.get(
            group, group.replace("_", " ").title()
        )
        members = ", ".join(
            f"{record['dtc']} [{record['index']}]" for record in group_records
        )
        groups.append({
            "key": f"dtc-group:{group}",
            "title": (
                f"Disable DTC group: {title} "
                f"({len(group_records)} record"
                f"{'' if len(group_records) == 1 else 's'})"
            ),
            "description": (
                f"Exact {rom} only. Atomically disables these records: {members}. "
                "The patch contains every mutable descriptor and attribute range "
                "for the group and does not disable physical monitors. It overlaps "
                "the corresponding individual DTC patches; use individual or group "
                "scope consistently."
            ),
            "category": DTC_GROUP_CATEGORY,
            "entries": entries,
        })
    return individual, groups


def parse_switch_state(entry, state, expected_bytes, switch_index, state_index):
    try:
        raw = bytes.fromhex(str(state["data"]))
    except (KeyError, TypeError, ValueError):
        raw = b""
    if len(raw) != expected_bytes:
        sys.exit(
            f"switch #{switch_index}, state #{state_index}: data must contain "
            f"{expected_bytes} hexadecimal bytes"
        )
    return raw


def switch_patches(switches):
    """Translate two-state presentation switches to reversible XDF patches."""
    patches = []
    for index, entry in enumerate(switches, 1):
        states = entry.get("state", [])
        if len(states) != 2:
            sys.exit(
                f"switch #{index}: TunerPro projection requires exactly two states"
            )
        size_fields = [field for field in ("sizex", "sizey") if field in entry]
        if len(size_fields) != 1:
            sys.exit(
                f"switch #{index}: exactly one of sizex or sizey is required"
            )
        element_bytes = STORAGE_BYTES.get(entry.get("storagetype"))
        if element_bytes is None:
            sys.exit(f"switch #{index}: unsupported storagetype for TunerPro")
        expected_bytes = int(entry[size_fields[0]]) * element_bytes
        base = parse_switch_state(entry, states[0], expected_bytes, index, 1)
        patched = parse_switch_state(entry, states[1], expected_bytes, index, 2)
        patches.append({
            "key": f"switch:{entry['name']}:{entry['storageaddress']}",
            "title": entry["name"],
            "description": (
                f"{entry.get('description', '')} Base state: {states[0]['name']}. "
                f"Patched state: {states[1]['name']}."
            ).strip(),
            "category": entry["category"],
            "entries": [{
                "name": entry["name"],
                "address": int(str(entry["storageaddress"]), 16),
                "basedata": base,
                "patchdata": patched,
            }],
        })
    return patches


def add_math(parent, expression, variables=("X",), **attributes):
    math = node(
        parent, "MATH", equation=normalized_expression(expression), **attributes
    )
    for variable in variables:
        node(math, "VAR", id=variable)
    return math


def add_static_axis(parent, axis_id, values, units=""):
    axis = node(parent, "XDFAXIS", id=axis_id, uniqueid="0x0", flags="0x0")
    node(
        axis, "EMBEDDEDDATA",
        mmedelementsizebits="8",
        mmedmajorstridebits="-32",
        mmedminorstridebits="0",
    )
    if units:
        node(axis, "units", units)
    node(axis, "indexcount", len(values))
    node(axis, "decimalpl", 0)
    node(axis, "outputtype", 1)
    node(axis, "datatype", 0)
    node(axis, "unittype", 0)
    node(axis, "DALINK", index=0)
    for index, value in enumerate(values):
        node(axis, "LABEL", index=index, value=value)
    add_math(axis, "X")


def add_embedded_axis(parent, axis_id, axis_info, override):
    axis = node(parent, "XDFAXIS", id=axis_id, uniqueid="0x0", flags="0x0")
    bits = STORAGE_BITS[axis_info["storagetype"]]
    node(
        axis, "EMBEDDEDDATA",
        mmedaddress=xdf_address(axis_info["addr"]),
        mmedelementsizebits=bits,
        mmedcolcount=axis_info["len"],
        mmedmajorstridebits=bits,
        mmedminorstridebits=0,
    )
    node(
        axis,
        "units",
        units_with_confidence(
            axis_info["units"], axis_info.get("scale_conf")
        ),
    )
    node(axis, "indexcount", axis_info["len"])
    node(axis, "decimalpl", decimal_places(override.get("format", "0")))
    node(axis, "outputtype", 1)
    node(axis, "embedinfo", type=1)
    node(axis, "datatype", 0)
    node(axis, "unittype", 0)
    node(axis, "DALINK", index=0)
    add_math(axis, axis_info["scale_expr"])


def add_table_axes(table, calibration, presentation, overrides, axes):
    if calibration["dims"] == 2:
        if calibration["axis_x"] and calibration["axis_y"]:
            x_info = axes[calibration["axis_y"][0]]
            y_info = axes[calibration["axis_x"][0]]
            add_embedded_axis(
                table, "x", x_info,
                overrides.get("axis", {}).get(x_info["addr"], {}),
            )
            add_embedded_axis(
                table, "y", y_info,
                overrides.get("axis", {}).get(y_info["addr"], {}),
            )
        else:
            add_static_axis(
                table, "x", presentation["static_axis_x"],
                presentation.get("static_axis_x_name", "X Axis"),
            )
            add_static_axis(
                table, "y", presentation["static_axis_y"],
                presentation.get("static_axis_y_name", "Y Axis"),
            )
        return

    if calibration["axis_x"]:
        axis_info = axes[calibration["axis_x"][0]]
        add_embedded_axis(
            table, "x", axis_info,
            overrides.get("axis", {}).get(axis_info["addr"], {}),
        )
    elif calibration["steps"]:
        if "static_axis" in presentation:
            add_static_axis(
                table,
                "x",
                presentation["static_axis"],
                presentation.get("static_axis_name", "X Axis"),
            )
        else:
            step = calibration["steps"][0]
            add_static_axis(
                table, "x",
                [index * step for index in range(calibration["width"])],
                f"Raw input (step {step})",
            )
    else:
        add_static_axis(
            table,
            "x",
            presentation["static_axis"],
            presentation.get("static_axis_name", "Selector"),
        )
    add_static_axis(table, "y", [0], "Series")


def masked_equation(expression, mask, bits):
    """Build an invertible expression that preserves bits outside the view.

    X is the cell being edited. B is the current raw value of the same cell read
    as an address variable. Keeping the complementary field in B makes solving
    for X preserve that field during a calculated-value edit.
    """
    full_mask = (1 << bits) - 1
    if mask <= 0 or mask > full_mask:
        raise ValueError(f"mask {mask:#x} is outside uint{bits}")
    if mask == full_mask:
        return normalized_expression(expression)
    shift = (mask & -mask).bit_length() - 1
    field_mask = mask >> shift
    if field_mask & (field_mask + 1):
        raise ValueError(f"mask {mask:#x} is not a contiguous bit field")
    other = full_mask ^ mask
    raw_field = f"((X-(B&{other}))/{1 << shift})"
    normalized = normalized_expression(expression)
    return re.sub(r"\bX\b", f"({raw_field})", normalized)


def add_data_axis(
    table,
    calibration,
    units,
    expression,
    fmt,
    mask=None,
):
    rows, columns = table_shape(calibration)
    bits = STORAGE_BITS[calibration["storagetype"]]
    axis = node(table, "XDFAXIS", id="z")
    node(
        axis, "EMBEDDEDDATA",
        mmedaddress=xdf_address(calibration["addr"]),
        mmedelementsizebits=bits,
        mmedrowcount=rows,
        mmedcolcount=columns,
        mmedmajorstridebits=0,
        mmedminorstridebits=0,
    )
    node(axis, "units", units)
    node(axis, "decimalpl", decimal_places(fmt))
    node(axis, "outputtype", 1)

    full_mask = (1 << bits) - 1
    parsed_mask = full_mask if mask is None else int(str(mask), 16)
    if parsed_mask == full_mask:
        add_math(axis, expression)
        return

    # XDF has no table mask attribute. A default expression is required, then
    # every cell receives a conversion that preserves the complementary field.
    add_math(axis, "X")
    element_bytes = bits // 8
    equation = masked_equation(expression, parsed_mask, bits)
    base_address = int(calibration["addr"], 16)
    for row in range(rows):
        for column in range(columns):
            address = base_address + (row * columns + column) * element_bytes
            math = node(
                axis, "MATH",
                row=row + 1,
                col=column + 1,
                equation=equation,
            )
            node(math, "VAR", id="X")
            node(
                math, "VAR",
                id="B",
                type="address",
                address=xdf_address(address),
            )


def map_description(rom, calibration, mask=None):
    rows, columns = table_shape(calibration)
    description = (
        f"Exact {rom}. Address {xdf_address(calibration['addr'])}; "
        f"{rows} rows x {columns} columns; {calibration['storagetype']}; "
        f"map confidence {calibration['confidence']}. "
        f"{calibration['semantics']}"
    )
    source = calibration.get("map_switching_source")
    slot = calibration.get("map_switching_slot")
    if source is not None:
        if slot == 1:
            description += (
                " Common-definition Map 1 uses the canonical stock storage."
            )
        else:
            description += (
                f" Common-definition Map {slot} storage is projected from "
                f"{xdf_address(source)}. Stock firmware does not reference "
                "this allocated storage; it becomes runtime-active only with "
                "the project map-switching patch."
            )
    if mask is not None:
        bits = STORAGE_BITS[calibration["storagetype"]]
        if int(str(mask), 16) != (1 << bits) - 1:
            description += (
                f" This view edits mask 0x{str(mask).upper()} and preserves "
                "the other bits in each cell."
            )
    if calibration.get("note"):
        description += f" {calibration['note']}"
    diagnostic = calibration.get("diagnostic_context", [])
    if diagnostic:
        description += " Static diagnostic context: " + "; ".join(diagnostic) + "."
    return description


def add_calibration_table(
    root,
    ids,
    categories,
    rom,
    calibration,
    presentation,
    overrides,
    axes,
    view=None,
):
    if view is None:
        title = presentation["name"]
        category = category_name(presentation["category"])
        units = units_with_confidence(
            calibration["units"], calibration.get("scale_conf")
        )
        expression = calibration["scale_expr"]
        fmt = presentation.get("format", "0")
        mask = presentation.get("mask")
        key = f"map:{calibration['addr']}"
    else:
        title = view["name"]
        category = category_name(view["category"])
        units = units_with_confidence(
            view["units"], calibration.get("confidence")
        )
        expression = view["expression"]
        fmt = view.get("format", "0")
        mask = view["mask"]
        key = f"masked-view:{calibration['addr']}:{mask}:{title}"

    table = node(
        root, "XDFTABLE",
        uniqueid=ids.get(key),
        flags="0x0",
    )
    node(table, "title", title)
    node(table, "description", map_description(rom, calibration, mask))
    node(table, "CATEGORYMEM", index=0, category=categories[category])
    add_table_axes(table, calibration, presentation, overrides, axes)
    add_data_axis(
        table,
        calibration,
        units,
        expression,
        fmt,
        mask=mask,
    )


def add_axis_view(
    root,
    ids,
    categories,
    rom,
    address,
    axis_info,
    presentation,
):
    table = node(
        root, "XDFTABLE",
        uniqueid=ids.get(f"axis-view:{address}"),
        flags="0x0",
    )
    node(table, "title", presentation["name"])
    node(
        table,
        "description",
        (
            f"Exact {rom}. Reference-axis view at {xdf_address(address)} with "
            f"{axis_info['len']} {axis_info['storagetype']} points; "
            f"confidence {axis_info['confidence']}."
        ),
    )
    node(
        table, "CATEGORYMEM", index=0,
        category=categories[category_name(presentation["category"])],
    )
    add_static_axis(table, "x", range(axis_info["len"]), "Index")
    add_static_axis(table, "y", [0], "Series")
    calibration = {
        "addr": address,
        "storagetype": axis_info["storagetype"],
        "dims": 1,
        "width": axis_info["len"],
        "height": 0,
        "family": "axis-view",
    }
    add_data_axis(
        table,
        calibration,
        units_with_confidence(
            axis_info["units"], axis_info.get("scale_conf")
        ),
        axis_info["scale_expr"],
        presentation.get("format", "0"),
    )


def add_patch(root, ids, categories, patch):
    element = node(
        root, "XDFPATCH",
        uniqueid=ids.get(patch["key"]),
        flags="0x0",
    )
    node(element, "title", patch["title"])
    node(element, "description", patch["description"])
    node(
        element, "CATEGORYMEM", index=0,
        category=categories[category_name(patch["category"])],
    )
    for entry in patch["entries"]:
        node(
            element,
            "XDFPATCHENTRY",
            name=entry["name"],
            address=xdf_address(entry["address"]),
            datasize=f"0x{len(entry['patchdata']):X}",
            patchdata=data_hex(entry["patchdata"]),
            basedata=data_hex(entry["basedata"]),
        )


def render(
    rom,
    image,
    calibrations,
    axes,
    overrides,
    views_by_source,
    dtc_records,
    switches,
):
    """Render a complete TunerPro XDF and return it with emission statistics."""
    individual_patches, group_patches = dtc_patches(rom, dtc_records)
    other_patches = switch_patches(switches)
    patches = other_patches + individual_patches + group_patches

    categories_in_use = {
        category_name(patch["category"]) for patch in patches
    }
    for calibration in calibrations:
        presentation = overrides["table"][calibration["addr"]]
        categories_in_use.add(category_name(presentation["category"]))
        categories_in_use.update(
            category_name(view["category"])
            for view in views_by_source.get(calibration["addr"], [])
        )
    categories_in_use.update(
        category_name(presentation["category"])
        for presentation in overrides.get("axisview", {}).values()
    )
    categories = {
        category: index
        for index, category in enumerate(sorted(categories_in_use), 1)
    }

    root = ET.Element("XDFFORMAT", {"version": "1.70"})
    header = node(root, "XDFHEADER")
    node(header, "flags", "0x1")
    node(header, "deftitle", f"{rom} - VQ HR ECU")
    node(
        header,
        "description",
        (
            f"Exact {rom} definition generated from Memgraph, defs/{rom}.dtc.csv, "
            f"and defs/{rom}.overrides.toml. Individual and group DTC patches "
            "overlap by design. No editor-side checksum is declared; the flashing "
            "workflow handles checksum correction."
            + (
                " The common definition includes Map 1 through Map 5 storage "
                "from patches/map-switching-layout.toml. Map 2 through Map 5 "
                "are inactive erased ranges in stock firmware and require the "
                "project map-switching patch."
                if overrides.get("map_switching", {}).get("enabled")
                else ""
            )
        ),
    )
    node(header, "author", overrides["rom"]["author"])
    node(header, "BASEOFFSET", offset=0, subtract=0)
    node(
        header, "DEFAULTS",
        datasizeinbits=8,
        sigdigits=2,
        outputtype=1,
        signed=0,
        lsbfirst=0,
        float=0,
    )
    node(
        header, "REGION",
        type="0xFFFFFFFF",
        startaddress="0x0",
        size=f"0x{len(image):X}",
        regioncolor="0x0",
        regionflags="0x0",
        name="Binary File",
        desc=f"Exact {rom} {len(image):#x}-byte ROM image",
    )
    for category, index in categories.items():
        node(header, "CATEGORY", index=f"0x{index - 1:X}", name=category)

    ids = IdAllocator()
    for patch in patches:
        add_patch(root, ids, categories, patch)

    ordered_calibrations = sorted(
        calibrations,
        key=lambda calibration: (
            overrides["table"][calibration["addr"]].get("order", 1 << 20),
            calibration["addr"],
        ),
    )
    for calibration in ordered_calibrations:
        presentation = overrides["table"][calibration["addr"]]
        add_calibration_table(
            root, ids, categories, rom, calibration, presentation,
            overrides, axes,
        )
        for view in views_by_source.get(calibration["addr"], []):
            add_calibration_table(
                root, ids, categories, rom, calibration, presentation,
                overrides, axes, view=view,
            )

    ordered_axis_views = sorted(
        overrides.get("axisview", {}),
        key=lambda address: (
            overrides["axisview"][address].get("order", 1 << 20),
            address,
        ),
    )
    for address in ordered_axis_views:
        add_axis_view(
            root,
            ids,
            categories,
            rom,
            address,
            axes[address],
            overrides["axisview"][address],
        )

    ET.indent(root, space="  ")
    xml = ET.tostring(
        root,
        encoding="unicode",
        xml_declaration=True,
        short_empty_elements=True,
    ) + "\n"
    stats = {
        "calibration_tables": len(calibrations),
        "masked_views": sum(len(views) for views in views_by_source.values()),
        "axis_views": len(ordered_axis_views),
        "other_patches": len(other_patches),
        "individual_dtc_patches": len(individual_patches),
        "group_dtc_patches": len(group_patches),
        "group_dtc_ranges": sum(
            len(patch["entries"]) for patch in group_patches
        ),
    }
    return xml, stats
