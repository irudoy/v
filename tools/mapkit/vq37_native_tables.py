#!/usr/bin/env python3
"""Load exact VQ37 target-native calibration tables and axes for editor definitions."""

from __future__ import annotations

import copy
from dataclasses import dataclass
import hashlib
from pathlib import Path
import re
import tomllib

from tools.mapkit import rom as romkit


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = ROOT / "defs" / "vq37-native-tables.toml"
SCHEMA_VERSION = 4
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
IDENTIFIER_RE = re.compile(r"^[a-z][a-z0-9_]*$")
SUPPORTED_TARGETS = frozenset({"JK78C", "1ND0A", "1ND3B", "1ME3B"})
TARGET_FIELDS = frozenset({"stock_sha256", "table"})
OPTIONAL_TARGET_FIELDS = frozenset({"axis", "absent"})
AXIS_KINDS = frozenset({"rpm", "load", "temp", "raw"})
SCALE_FIELDS = frozenset({"units", "scale_conf", "scale_expr", "to_byte"})
REQUIRED_TABLE_FIELDS = frozenset({
    "id",
    "address",
    "width",
    "height",
    "storagetype",
    "values_sha256",
    "pointer_bindings",
    "name",
    "category",
    "order",
    "format",
    "fine",
    "coarse",
    "confidence",
    "semantics",
    "note",
})
OPTIONAL_TABLE_FIELDS = SCALE_FIELDS | frozenset({
    "axis_x",
    "axis_y",
    "mask",
    "constant_content",
    "static_axis_name",
    "static_axis",
    "static_axis_x_name",
    "static_axis_x",
    "static_axis_y_name",
    "static_axis_y",
})
REQUIRED_AXIS_FIELDS = frozenset({
    "id",
    "address",
    "length",
    "storagetype",
    "values_sha256",
    "pointer_bindings",
    "name",
    "kind",
    "format",
    "fine",
    "coarse",
    "confidence",
    "note",
})
POINTER_FIELDS = frozenset({"site", "accessor"})
OPTIONAL_POINTER_FIELDS = frozenset({"offset"})


class NativeTableError(ValueError):
    """Raised when target-native VQ37 table evidence is incomplete or stale."""


@dataclass(frozen=True)
class PointerBinding:
    site: int
    accessor: int
    offset: int = 0


@dataclass(frozen=True)
class NativeTable:
    identifier: str
    address: int
    width: int
    height: int
    storagetype: str
    values_sha256: str
    pointer_bindings: tuple[PointerBinding, ...]
    axis_x: tuple[int, ...]
    axis_y: tuple[int, ...]
    name: str
    category: str
    order: int
    format: str
    fine: float
    coarse: float
    units: str | None
    confidence: str
    scale_conf: str | None
    scale_expr: str | None
    to_byte: str | None
    static_axis_name: str
    static_axis: tuple[int | str, ...]
    static_axis_x_name: str
    static_axis_x: tuple[int | str, ...]
    static_axis_y_name: str
    static_axis_y: tuple[int | str, ...]
    mask: str
    constant_content: bool
    semantics: str
    note: str


@dataclass(frozen=True)
class NativeAxis:
    identifier: str
    address: int
    length: int
    storagetype: str
    values_sha256: str
    pointer_bindings: tuple[PointerBinding, ...]
    name: str
    kind: str
    format: str
    fine: float
    coarse: float
    units: str | None
    confidence: str
    scale_conf: str | None
    scale_expr: str | None
    to_byte: str | None
    note: str


@dataclass(frozen=True)
class Target:
    rom: str
    stock_sha256: str
    tables: tuple[NativeTable, ...]
    axes: tuple[NativeAxis, ...]
    absent: dict[str, str]


def _address(value, context):
    if type(value) is not int or not 0 <= value < 0x180000:
        raise NativeTableError(f"{context}: invalid address")
    return value


def _text(value, context):
    if not isinstance(value, str) or not value.strip():
        raise NativeTableError(f"{context} is empty")
    return value.strip()


EVIDENCE_LEVELS = frozenset({"code", "candidate"})


def _evidence(value, context):
    if value not in EVIDENCE_LEVELS:
        raise NativeTableError(
            f"{context} must be one of {sorted(EVIDENCE_LEVELS)}"
        )
    return value


def _scale(row, context):
    """Keep an absent conversion distinct from a complete scale claim."""
    present = SCALE_FIELDS & row.keys()
    if not present:
        return {key: None for key in SCALE_FIELDS}
    if present != SCALE_FIELDS:
        raise NativeTableError(f"{context}: engineering conversion is incomplete")
    level = row["scale_conf"]
    if level not in EVIDENCE_LEVELS | {"unknown", "pattern"}:
        raise NativeTableError(f"{context}.scale_conf is unsupported")
    return {
        "units": _text(row["units"], f"{context}.units"),
        "scale_expr": _text(row["scale_expr"], f"{context}.scale_expr"),
        "to_byte": _text(row["to_byte"], f"{context}.to_byte"),
        "scale_conf": level,
    }


def _stored_count(entity):
    return entity.scale_conf not in EVIDENCE_LEVELS


def _editor_scale(entity):
    """Render storage without asserting an engineering unit or evidence level."""
    if _stored_count(entity):
        return {
            "units": "Stored count", "scale_expr": "x", "to_byte": "x",
            "scale_conf": None, "stored_count": True,
        }
    return {key: getattr(entity, key) for key in SCALE_FIELDS}


def _editor_presentation(entity):
    if _stored_count(entity):
        name = re.sub(r"\s*\[[^\]]*\]", "", entity.name)
        return {"name": f"{name} [stored count]", "format": "0", "fine": 1, "coarse": 10}
    return {key: getattr(entity, key) for key in ("name", "format", "fine", "coarse")}


def _editor_note(entity, note):
    if _stored_count(entity):
        return note + " Editor values are stored counts; no engineering conversion is established."
    return note


def _number(value, context):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise NativeTableError(f"{context} is not a number")
    if value <= 0:
        raise NativeTableError(f"{context} is not positive")
    return value


def _address_key(address):
    return f"{address:08x}"


def _identifier(row, context):
    identifier = _text(row["id"], f"{context}.id")
    if not IDENTIFIER_RE.fullmatch(identifier):
        raise NativeTableError(f"{context}.id is not a lowercase identifier")
    return identifier


def _fields(row, context, required, optional):
    if not isinstance(row, dict):
        raise NativeTableError(f"{context}: entry is not a mapping")
    actual = set(row)
    missing = required - actual
    extra = actual - required - optional
    if missing or extra:
        raise NativeTableError(
            f"{context}: fields differ; missing={sorted(missing)}; "
            f"extra={sorted(extra)}"
        )


def _sha256(value, context):
    if not SHA256_RE.fullmatch(str(value)):
        raise NativeTableError(f"{context}: invalid SHA-256")
    return value


def _storagetype(value, context):
    storagetype = _text(value, context)
    if storagetype not in romkit.ELEM:
        raise NativeTableError(f"{context} is unsupported")
    return storagetype


def _pointers(raw_pointers, context):
    if not isinstance(raw_pointers, list) or not raw_pointers:
        raise NativeTableError(f"{context}.pointer_bindings is empty")
    pointers = []
    for index, pointer in enumerate(raw_pointers):
        pointer_context = f"{context}.pointer_bindings[{index}]"
        if not isinstance(pointer, dict):
            raise NativeTableError(f"{pointer_context}: fields differ")
        actual = set(pointer)
        if POINTER_FIELDS - actual or actual - POINTER_FIELDS - OPTIONAL_POINTER_FIELDS:
            raise NativeTableError(f"{pointer_context}: fields differ")
        offset = pointer.get("offset", 0)
        if type(offset) is not int or offset < 0:
            raise NativeTableError(f"{pointer_context}.offset is invalid")
        pointers.append(PointerBinding(
            site=_address(pointer["site"], f"{pointer_context}.site"),
            accessor=_address(pointer["accessor"], f"{pointer_context}.accessor"),
            offset=offset,
        ))
    # One literal pool word may reach several entities by displacement, so a
    # binding is unique by site and offset rather than by site alone.
    if len({(pointer.site, pointer.offset) for pointer in pointers}) != len(pointers):
        raise NativeTableError(f"{context}.pointer_bindings repeat a site")
    return tuple(pointers)


def _mask(value, storagetype, context):
    """Return the uppercase contiguous bit-field mask of a table, or ""."""
    if value is None:
        return ""
    if not isinstance(value, str) or not re.fullmatch(r"[0-9A-Fa-f]+", value):
        raise NativeTableError(f"{context} is not a hexadecimal string")
    bits = 8 * romkit.ELEM[storagetype]
    field = int(value, 16)
    low = field & -field
    if not 0 < field < (1 << bits) - 1 or (field // low) & (field // low + 1):
        raise NativeTableError(
            f"{context} is not a contiguous partial bit field of uint{bits}"
        )
    return value.upper()


def _static_axis(row, key, length, context):
    """The labels and the name of the static axis `key` of `length` cells, or
    ((), "") when the row declares none. The labels are increasing integers or
    non-empty texts."""
    labels = row.get(key)
    name = row.get(f"{key}_name")
    if (labels is None) != (name is None):
        raise NativeTableError(f"{context}: {key} declaration is incomplete")
    if labels is None:
        return (), ""
    name = _text(name, f"{context}.{key}_name")
    numbers = isinstance(labels, list) and all(type(item) is int for item in labels)
    texts = isinstance(labels, list) and all(
        isinstance(item, str) and item.strip() for item in labels
    )
    if not (numbers or texts) or len(labels) != length:
        raise NativeTableError(
            f"{context}.{key}: expected {length} integers or {length} labels"
        )
    labels = tuple(labels)
    if numbers and not romkit.monotone(labels):
        raise NativeTableError(f"{context}.{key} is not monotone")
    return labels, name


def _parse_table(row, context):
    _fields(row, context, REQUIRED_TABLE_FIELDS, OPTIONAL_TABLE_FIELDS)
    identifier = _identifier(row, context)
    context = f"{context} {identifier}"
    width = row["width"]
    height = row["height"]
    for key, value in (("width", width), ("height", height)):
        if type(value) is not int or value <= 0:
            raise NativeTableError(f"{context}.{key} is invalid")
    order = row["order"]
    if type(order) is not int or order < 0:
        raise NativeTableError(f"{context}.order is invalid")
    axes = {}
    for key in ("axis_x", "axis_y"):
        value = row.get(key)
        axes[key] = (
            () if value is None
            else (_address(value, f"{context}.{key}"),)
        )
    if height > 1 and bool(axes["axis_x"]) != bool(axes["axis_y"]):
        raise NativeTableError(f"{context}: axis pair is incomplete")
    if height == 1 and axes["axis_y"]:
        raise NativeTableError(f"{context}: one-dimensional table declares axis_y")
    static_axis, static_axis_name = _static_axis(row, "static_axis", width, context)
    static_x, static_x_name = _static_axis(row, "static_axis_x", width, context)
    static_y, static_y_name = _static_axis(row, "static_axis_y", height, context)
    # A one-dimensional table labels its cells with static_axis; a
    # two-dimensional table without graph axes labels its columns with
    # static_axis_x and its rows with static_axis_y.
    if height == 1 and (static_x or static_y):
        raise NativeTableError(
            f"{context}: one-dimensional table declares static_axis_x or static_axis_y"
        )
    if height > 1 and static_axis:
        raise NativeTableError(f"{context}: two-dimensional table declares static_axis")
    if bool(static_x) != bool(static_y):
        raise NativeTableError(f"{context}: static axis pair is incomplete")
    static = static_axis or static_x
    if axes["axis_x"] and static:
        raise NativeTableError(f"{context}: static axis overlaps a graph axis")
    if not axes["axis_x"] and not static:
        raise NativeTableError(f"{context}: no axis is declared")
    storagetype = _storagetype(row["storagetype"], f"{context}.storagetype")
    mask = _mask(row.get("mask"), storagetype, f"{context}.mask")
    constant_content = row.get("constant_content", False)
    if constant_content is not True and "constant_content" in row:
        raise NativeTableError(f"{context}.constant_content must be true when present")
    return NativeTable(
        identifier=identifier,
        address=_address(row["address"], f"{context}.address"),
        width=width,
        height=height,
        storagetype=storagetype,
        values_sha256=_sha256(row["values_sha256"], f"{context}.values_sha256"),
        pointer_bindings=_pointers(row["pointer_bindings"], context),
        axis_x=axes["axis_x"],
        axis_y=axes["axis_y"],
        name=_text(row["name"], f"{context}.name"),
        category=_text(row["category"], f"{context}.category"),
        order=order,
        format=_text(row["format"], f"{context}.format"),
        fine=_number(row["fine"], f"{context}.fine"),
        coarse=_number(row["coarse"], f"{context}.coarse"),
        confidence=_evidence(row["confidence"], f"{context}.confidence"),
        **_scale(row, context),
        static_axis_name=static_axis_name,
        static_axis=static_axis,
        static_axis_x_name=static_x_name,
        static_axis_x=static_x,
        static_axis_y_name=static_y_name,
        static_axis_y=static_y,
        mask=mask,
        constant_content=constant_content,
        semantics=_text(row["semantics"], f"{context}.semantics"),
        note=_text(row["note"], f"{context}.note"),
    )


def _parse_axis(row, context):
    _fields(row, context, REQUIRED_AXIS_FIELDS, SCALE_FIELDS)
    identifier = _identifier(row, context)
    context = f"{context} {identifier}"
    length = row["length"]
    if type(length) is not int or length <= 1:
        raise NativeTableError(f"{context}.length is invalid")
    kind = _text(row["kind"], f"{context}.kind")
    if kind not in AXIS_KINDS:
        raise NativeTableError(f"{context}.kind must be one of {sorted(AXIS_KINDS)}")
    return NativeAxis(
        identifier=identifier,
        address=_address(row["address"], f"{context}.address"),
        length=length,
        storagetype=_storagetype(row["storagetype"], f"{context}.storagetype"),
        values_sha256=_sha256(row["values_sha256"], f"{context}.values_sha256"),
        pointer_bindings=_pointers(row["pointer_bindings"], context),
        name=_text(row["name"], f"{context}.name"),
        kind=kind,
        format=_text(row["format"], f"{context}.format"),
        fine=_number(row["fine"], f"{context}.fine"),
        coarse=_number(row["coarse"], f"{context}.coarse"),
        confidence=_evidence(row["confidence"], f"{context}.confidence"),
        **_scale(row, context),
        note=_text(row["note"], f"{context}.note"),
    )


def _parse_absent(raw, context):
    if raw is None:
        return {}
    if not isinstance(raw, dict) or not raw:
        raise NativeTableError(f"{context}.absent is not a mapping of roles")
    absent = {}
    for identifier, reason in raw.items():
        if not IDENTIFIER_RE.fullmatch(str(identifier)):
            raise NativeTableError(
                f"{context}.absent.{identifier} is not a lowercase identifier"
            )
        absent[identifier] = _text(reason, f"{context}.absent.{identifier}")
    return absent


def _parse_target(rom, row, context):
    if not isinstance(row, dict):
        raise NativeTableError(f"{context}: target is not a mapping")
    actual = set(row)
    missing = TARGET_FIELDS - actual
    extra = actual - TARGET_FIELDS - OPTIONAL_TARGET_FIELDS
    if missing or extra:
        raise NativeTableError(
            f"{context}: fields differ; missing={sorted(missing)}; "
            f"extra={sorted(extra)}"
        )
    raw_tables = row["table"]
    if not isinstance(raw_tables, list) or not raw_tables:
        raise NativeTableError(f"{context}: no tables")
    tables = tuple(
        _parse_table(entry, f"{context}.table[{index}]")
        for index, entry in enumerate(raw_tables)
    )
    raw_axes = row.get("axis", [])
    if not isinstance(raw_axes, list):
        raise NativeTableError(f"{context}: axis is not a list")
    axes = tuple(
        _parse_axis(entry, f"{context}.axis[{index}]")
        for index, entry in enumerate(raw_axes)
    )
    entities = (*tables, *axes)
    identifiers = [entity.identifier for entity in entities]
    if len(set(identifiers)) != len(identifiers):
        raise NativeTableError(f"{context}: identifiers repeat")
    if len({table.address for table in tables}) != len(tables):
        raise NativeTableError(f"{context}: table addresses repeat")
    if len({axis.address for axis in axes}) != len(axes):
        raise NativeTableError(f"{context}: axis addresses repeat")
    absent = _parse_absent(row.get("absent"), context)
    overlap = set(absent) & set(identifiers)
    if overlap:
        raise NativeTableError(
            f"{context}: absent roles are present: {sorted(overlap)}"
        )
    return Target(
        rom=rom,
        stock_sha256=_sha256(row["stock_sha256"], f"{context}.stock_sha256"),
        tables=tables,
        axes=axes,
        absent=absent,
    )


def load_registry(path=DEFAULT_REGISTRY):
    """Return the validated target-native registry keyed by ROM."""
    path = Path(path)
    try:
        with path.open("rb") as source:
            document = tomllib.load(source)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise NativeTableError(
            f"native table registry cannot be read: {path}"
        ) from error
    if (
        set(document) != {"schema_version", "target"}
        or document["schema_version"] != SCHEMA_VERSION
    ):
        raise NativeTableError(f"{path}: unsupported registry schema")
    rows = document["target"]
    if not isinstance(rows, dict) or set(rows) != SUPPORTED_TARGETS:
        actual = sorted(rows) if isinstance(rows, dict) else []
        raise NativeTableError(
            f"{path}: target set differs; "
            f"actual={actual} expected={sorted(SUPPORTED_TARGETS)}"
        )
    result = {
        rom: _parse_target(rom, row, f"{path} [target.{rom}]")
        for rom, row in rows.items()
    }
    # Every VQ37 image is reviewed against the same role set. A role that a
    # target neither carries nor declares absent with a reason is stale rather
    # than different, and an absence that no target contradicts is stale too.
    present = {
        rom: {entity.identifier for entity in (*target.tables, *target.axes)}
        for rom, target in result.items()
    }
    expected = set.union(*present.values())
    for rom, target in result.items():
        covered = present[rom] | set(target.absent)
        if covered != expected:
            raise NativeTableError(
                f"{path} [target.{rom}]: roles differ; "
                f"missing={sorted(expected - covered)}; "
                f"unknown={sorted(covered - expected)}"
            )
    return result


def _model(table, note):
    return {
        "addr": _address_key(table.address),
        "family": "direct-row-major" if table.height > 1 else "direct-indexed",
        "dims": 2 if table.height > 1 else 1,
        "width": table.width,
        "height": table.height if table.height > 1 else None,
        "storagetype": table.storagetype,
        "confidence": table.confidence,
        "role": "table",
        "semantics": table.semantics,
        **_editor_scale(table),
        "note": _editor_note(table, note),
        "wrappers": [],
        "kernels": [],
        "steps": [],
        "accessors": sorted({
            _address_key(pointer.accessor) for pointer in table.pointer_bindings
        }),
        "resolver_kinds": ["reviewed-target"],
        "axis_x": [_address_key(address) for address in table.axis_x],
        "axis_y": [_address_key(address) for address in table.axis_y],
        "diagnostic_bindings": [],
    }


def _axis_model(axis, values, note):
    return {
        "addr": _address_key(axis.address),
        "kind": axis.kind,
        **_editor_scale(axis),
        "scale_evidence": "" if _stored_count(axis) else "registry:target-native",
        "storagetype": axis.storagetype,
        "len": axis.length,
        "confidence": axis.confidence,
        "note": _editor_note(axis, note),
        "values": list(values),
        "monotonic": True,
    }


def _presentation(table):
    override = {
        **_editor_presentation(table),
        "category": table.category,
        "order": table.order,
        "emit": True,
    }
    if table.static_axis:
        override["static_axis_name"] = table.static_axis_name
        override["static_axis"] = list(table.static_axis)
    if table.static_axis_x:
        override["static_axis_x_name"] = table.static_axis_x_name
        override["static_axis_x"] = list(table.static_axis_x)
        override["static_axis_y_name"] = table.static_axis_y_name
        override["static_axis_y"] = list(table.static_axis_y)
    if table.mask:
        override["mask"] = table.mask
    return override


def _axis_presentation(axis):
    return _editor_presentation(axis)


def _sorted_bindings(bindings):
    return sorted(bindings, key=lambda pointer: (pointer.site, pointer.offset))


def _describe_bindings(rom, entity, address, bindings, note):
    return (
        f"Exact {rom} target-native {entity} at {address:#x} bound to "
        + ", ".join(
            f"accessor {pointer.accessor:#x} through literal {pointer.site:#x}"
            + (f" + {pointer.offset:#x}" if pointer.offset else "")
            for pointer in _sorted_bindings(bindings)
        )
        + f". {note}"
    )


def _verify_block(rom, image, key, address, length, storagetype, expected_sha256,
                  constant_content=False):
    """Return the stock values of an entity. An all-ones block is erased flash
    unless the entry states constant_content as a reviewed calibration value."""
    element = romkit.ELEM[storagetype]
    end = address + length * element
    if end > len(image.data):
        raise NativeTableError(f"{rom}: native entity {key} is outside the stock image")
    block = image.data[address:end]
    if hashlib.sha256(block).hexdigest() != expected_sha256:
        raise NativeTableError(f"{rom}: native entity {key} values differ")
    values = image.values(key, length, storagetype)
    if romkit.erased(values, storagetype) and not constant_content:
        raise NativeTableError(f"{rom}: native entity {key} is erased")
    return values


def _verify_bindings(rom, image, address, bindings):
    for pointer in bindings:
        actual = int.from_bytes(image.data[pointer.site : pointer.site + 4], "big")
        if actual + pointer.offset != address:
            raise NativeTableError(
                f"{rom}: pointer at {pointer.site:#x} is {actual:#x}"
                + (f" + {pointer.offset:#x}" if pointer.offset else "")
                + f", expected {address:#x}"
            )
        # SH-2 PC-relative loads reach forward only, so a valid literal
        # pool site always follows its accessor entry point.
        if not pointer.accessor < pointer.site < len(image.data) - 4:
            raise NativeTableError(
                f"{rom}: pointer site {pointer.site:#x} does not follow "
                f"accessor {pointer.accessor:#x}"
            )


def table_axis_keys(rom, path=DEFAULT_REGISTRY):
    """Return the address keys of every axis that a native table of the ROM indexes."""
    target = load_registry(path).get(rom)
    if target is None:
        return frozenset()
    return frozenset(
        _address_key(axis)
        for table in target.tables
        for axis in table.axis_x + table.axis_y
    )


def apply_target(rom, maps, axes, overrides, image, path=DEFAULT_REGISTRY):
    """Append exact target-native VQ37 tables and axes to a projected editor model."""
    target = load_registry(path).get(rom)
    if target is None:
        return maps, axes, overrides
    if image.rom != rom:
        raise NativeTableError(
            f"native table target is {rom}, image is {image.rom}"
        )
    actual_sha256 = hashlib.sha256(image.data).hexdigest()
    if actual_sha256 != target.stock_sha256:
        raise NativeTableError(
            f"{rom}: stock SHA-256 is {actual_sha256}, expected {target.stock_sha256}"
        )

    result_maps = copy.deepcopy(maps)
    result_axes = copy.deepcopy(axes)
    result_overrides = copy.deepcopy(overrides)
    tables = result_overrides.setdefault("table", {})
    if not isinstance(tables, dict):
        raise NativeTableError("definition table overrides must be a table")
    axis_overrides = result_overrides.setdefault("axis", {})
    if not isinstance(axis_overrides, dict):
        raise NativeTableError("definition axis overrides must be a table")

    for axis in target.axes:
        key = _address_key(axis.address)
        values = _verify_block(
            rom, image, key, axis.address, axis.length, axis.storagetype,
            axis.values_sha256,
        )
        if not romkit.monotone(values):
            raise NativeTableError(f"{rom}: native axis {key} is not monotone")
        _verify_bindings(rom, image, axis.address, axis.pointer_bindings)
        if key in result_axes or key in axis_overrides:
            raise NativeTableError(
                f"{rom}: native axis {key} collides with the projection"
            )
        result_axes[key] = _axis_model(
            axis, values,
            _describe_bindings(rom, "axis", axis.address, axis.pointer_bindings, axis.note),
        )
        axis_overrides[key] = _axis_presentation(axis)

    names = {
        override.get("name")
        for override in tables.values()
        if isinstance(override, dict)
    }
    for table in target.tables:
        key = _address_key(table.address)
        presentation = _presentation(table)
        if presentation["name"] in names:
            raise NativeTableError(
                f"{rom}: native table {key} repeats the table name {table.name!r}"
            )
        names.add(presentation["name"])
        _verify_block(
            rom, image, key, table.address, table.width * table.height,
            table.storagetype, table.values_sha256, table.constant_content,
        )
        _verify_bindings(rom, image, table.address, table.pointer_bindings)
        for axis in table.axis_x + table.axis_y:
            axis_key = _address_key(axis)
            if axis_key not in result_axes:
                raise NativeTableError(
                    f"{rom}: native table {key} uses unprojected axis {axis_key}"
                )
        if key in result_maps or key in tables:
            raise NativeTableError(
                f"{rom}: native table {key} collides with the projection"
            )
        result_maps[key] = _model(
            table,
            _describe_bindings(rom, "table", table.address, table.pointer_bindings, table.note),
        )
        tables[key] = presentation
    if not axis_overrides:
        result_overrides.pop("axis")
    return result_maps, result_axes, result_overrides
