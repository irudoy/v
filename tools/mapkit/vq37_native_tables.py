#!/usr/bin/env python3
"""Load exact VQ37 target-native calibration tables for editor definitions."""

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
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
IDENTIFIER_RE = re.compile(r"^[a-z][a-z0-9_]*$")
SUPPORTED_TARGETS = frozenset({"JK78C", "1ND0A", "1ND3B"})
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
    "units",
    "confidence",
    "scale_conf",
    "scale_expr",
    "to_byte",
    "semantics",
    "note",
})
OPTIONAL_TABLE_FIELDS = frozenset({
    "axis_x",
    "axis_y",
    "static_axis_name",
    "static_axis",
})


class NativeTableError(ValueError):
    """Raised when target-native VQ37 table evidence is incomplete or stale."""


@dataclass(frozen=True)
class PointerBinding:
    site: int
    accessor: int


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
    units: str
    confidence: str
    scale_conf: str
    scale_expr: str
    to_byte: str
    static_axis_name: str
    static_axis: tuple[int, ...]
    semantics: str
    note: str


@dataclass(frozen=True)
class Target:
    rom: str
    stock_sha256: str
    tables: tuple[NativeTable, ...]


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


def _number(value, context):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise NativeTableError(f"{context} is not a number")
    if value <= 0:
        raise NativeTableError(f"{context} is not positive")
    return value


def _address_key(address):
    return f"{address:08x}"


def _parse_table(row, context):
    if not isinstance(row, dict):
        raise NativeTableError(f"{context}: table is not a mapping")
    actual = set(row)
    missing = REQUIRED_TABLE_FIELDS - actual
    extra = actual - REQUIRED_TABLE_FIELDS - OPTIONAL_TABLE_FIELDS
    if missing or extra:
        raise NativeTableError(
            f"{context}: fields differ; missing={sorted(missing)}; "
            f"extra={sorted(extra)}"
        )
    identifier = _text(row["id"], f"{context}.id")
    if not IDENTIFIER_RE.fullmatch(identifier):
        raise NativeTableError(f"{context}.id is not a lowercase identifier")
    context = f"{context} {identifier}"
    if not SHA256_RE.fullmatch(str(row["values_sha256"])):
        raise NativeTableError(f"{context}.values_sha256: invalid SHA-256")
    width = row["width"]
    height = row["height"]
    for key, value in (("width", width), ("height", height)):
        if type(value) is not int or value <= 0:
            raise NativeTableError(f"{context}.{key} is invalid")
    storagetype = _text(row["storagetype"], f"{context}.storagetype")
    if storagetype not in romkit.ELEM:
        raise NativeTableError(f"{context}.storagetype is unsupported")
    order = row["order"]
    if type(order) is not int or order < 0:
        raise NativeTableError(f"{context}.order is invalid")
    raw_pointers = row["pointer_bindings"]
    if not isinstance(raw_pointers, list) or not raw_pointers:
        raise NativeTableError(f"{context}.pointer_bindings is empty")
    pointers = []
    for index, pointer in enumerate(raw_pointers):
        pointer_context = f"{context}.pointer_bindings[{index}]"
        if not isinstance(pointer, dict) or set(pointer) != {"site", "accessor"}:
            raise NativeTableError(f"{pointer_context}: fields differ")
        pointers.append(PointerBinding(
            site=_address(pointer["site"], f"{pointer_context}.site"),
            accessor=_address(pointer["accessor"], f"{pointer_context}.accessor"),
        ))
    if len({pointer.site for pointer in pointers}) != len(pointers):
        raise NativeTableError(f"{context}.pointer_bindings repeat a site")
    axes = {}
    for key in ("axis_x", "axis_y"):
        value = row.get(key)
        axes[key] = (
            () if value is None
            else (_address(value, f"{context}.{key}"),)
        )
    if bool(axes["axis_x"]) != bool(axes["axis_y"]):
        raise NativeTableError(f"{context}: axis pair is incomplete")
    if axes["axis_x"] and height == 1:
        raise NativeTableError(f"{context}: one-dimensional table declares axes")
    static_axis = row.get("static_axis")
    static_axis_name = row.get("static_axis_name")
    if (static_axis is None) != (static_axis_name is None):
        raise NativeTableError(f"{context}: static axis declaration is incomplete")
    if static_axis is None:
        static_axis = ()
        static_axis_name = ""
    else:
        static_axis_name = _text(static_axis_name, f"{context}.static_axis_name")
        if (
            not isinstance(static_axis, list)
            or len(static_axis) != width
            or any(type(item) is not int for item in static_axis)
        ):
            raise NativeTableError(
                f"{context}.static_axis: expected {width} integers"
            )
        static_axis = tuple(static_axis)
        if not romkit.monotone(static_axis):
            raise NativeTableError(f"{context}.static_axis is not monotone")
    if axes["axis_x"] and static_axis:
        raise NativeTableError(f"{context}: static axis overlaps a graph axis")
    if not axes["axis_x"] and not static_axis:
        raise NativeTableError(f"{context}: no axis is declared")
    return NativeTable(
        identifier=identifier,
        address=_address(row["address"], f"{context}.address"),
        width=width,
        height=height,
        storagetype=storagetype,
        values_sha256=row["values_sha256"],
        pointer_bindings=tuple(pointers),
        axis_x=axes["axis_x"],
        axis_y=axes["axis_y"],
        name=_text(row["name"], f"{context}.name"),
        category=_text(row["category"], f"{context}.category"),
        order=order,
        format=_text(row["format"], f"{context}.format"),
        fine=_number(row["fine"], f"{context}.fine"),
        coarse=_number(row["coarse"], f"{context}.coarse"),
        units=_text(row["units"], f"{context}.units"),
        confidence=_evidence(row["confidence"], f"{context}.confidence"),
        scale_conf=_evidence(row["scale_conf"], f"{context}.scale_conf"),
        scale_expr=_text(row["scale_expr"], f"{context}.scale_expr"),
        to_byte=_text(row["to_byte"], f"{context}.to_byte"),
        static_axis_name=static_axis_name,
        static_axis=static_axis,
        semantics=_text(row["semantics"], f"{context}.semantics"),
        note=_text(row["note"], f"{context}.note"),
    )


def load_registry(path=DEFAULT_REGISTRY):
    """Return the validated target-native table registry keyed by ROM."""
    path = Path(path)
    try:
        with path.open("rb") as source:
            document = tomllib.load(source)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise NativeTableError(
            f"native table registry cannot be read: {path}"
        ) from error
    if set(document) != {"schema_version", "target"} or document["schema_version"] != 1:
        raise NativeTableError(f"{path}: unsupported registry schema")
    rows = document["target"]
    if not isinstance(rows, dict) or set(rows) != SUPPORTED_TARGETS:
        actual = sorted(rows) if isinstance(rows, dict) else []
        raise NativeTableError(
            f"{path}: target set differs; "
            f"actual={actual} expected={sorted(SUPPORTED_TARGETS)}"
        )
    result = {}
    identifier_sets = {}
    for rom, row in rows.items():
        context = f"{path} [target.{rom}]"
        if not isinstance(row, dict) or set(row) != {"stock_sha256", "table"}:
            actual = set(row) if isinstance(row, dict) else set()
            raise NativeTableError(
                f"{context}: fields differ; "
                f"missing={sorted({'stock_sha256', 'table'} - actual)}; "
                f"extra={sorted(actual - {'stock_sha256', 'table'})}"
            )
        if not SHA256_RE.fullmatch(str(row["stock_sha256"])):
            raise NativeTableError(f"{context}.stock_sha256: invalid SHA-256")
        raw_tables = row["table"]
        if not isinstance(raw_tables, list) or not raw_tables:
            raise NativeTableError(f"{context}: no tables")
        tables = tuple(
            _parse_table(entry, f"{context}.table[{index}]")
            for index, entry in enumerate(raw_tables)
        )
        identifiers = {table.identifier for table in tables}
        if len(identifiers) != len(tables):
            raise NativeTableError(f"{context}: table identifiers repeat")
        if len({table.address for table in tables}) != len(tables):
            raise NativeTableError(f"{context}: table addresses repeat")
        identifier_sets[rom] = identifiers
        result[rom] = Target(
            rom=rom,
            stock_sha256=row["stock_sha256"],
            tables=tables,
        )
    # Every VQ37 image carries the same architectural insertion, so a target
    # that omits one of the registered roles is stale rather than different.
    expected = set.union(*identifier_sets.values())
    for rom, identifiers in identifier_sets.items():
        if identifiers != expected:
            raise NativeTableError(
                f"{path} [target.{rom}]: roles differ; "
                f"missing={sorted(expected - identifiers)}"
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
        "units": table.units,
        "scale_expr": table.scale_expr,
        "to_byte": table.to_byte,
        "scale_conf": table.scale_conf,
        "note": note,
        "wrappers": [],
        "kernels": [],
        "steps": [],
        "accessors": [
            _address_key(pointer.accessor) for pointer in table.pointer_bindings
        ],
        "resolver_kinds": ["reviewed-target"],
        "axis_x": [_address_key(address) for address in table.axis_x],
        "axis_y": [_address_key(address) for address in table.axis_y],
        "diagnostic_bindings": [],
    }


def _presentation(table):
    override = {
        "name": table.name,
        "category": table.category,
        "order": table.order,
        "emit": True,
        "format": table.format,
        "fine": table.fine,
        "coarse": table.coarse,
    }
    if table.static_axis:
        override["static_axis_name"] = table.static_axis_name
        override["static_axis"] = list(table.static_axis)
    return override


def apply_target(rom, maps, axes, overrides, image, path=DEFAULT_REGISTRY):
    """Append exact target-native VQ37 tables to a projected editor model."""
    target = load_registry(path).get(rom)
    if target is None:
        return maps, overrides
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
    result_overrides = copy.deepcopy(overrides)
    tables = result_overrides.setdefault("table", {})
    if not isinstance(tables, dict):
        raise NativeTableError("definition table overrides must be a table")

    for table in target.tables:
        key = _address_key(table.address)
        length = table.width * table.height
        element = romkit.ELEM[table.storagetype]
        end = table.address + length * element
        if end > len(image.data):
            raise NativeTableError(
                f"{rom}: native table {key} is outside the stock image"
            )
        block = image.data[table.address : end]
        if hashlib.sha256(block).hexdigest() != table.values_sha256:
            raise NativeTableError(f"{rom}: native table {key} values differ")
        values = image.values(key, length, table.storagetype)
        if romkit.erased(values, table.storagetype):
            raise NativeTableError(f"{rom}: native table {key} is erased")
        for pointer in table.pointer_bindings:
            actual = int.from_bytes(
                image.data[pointer.site : pointer.site + 4], "big"
            )
            if actual != table.address:
                raise NativeTableError(
                    f"{rom}: pointer at {pointer.site:#x} is {actual:#x}, "
                    f"expected {table.address:#x}"
                )
            # SH-2 PC-relative loads reach forward only, so a valid literal
            # pool site always follows its accessor entry point.
            if not pointer.accessor < pointer.site < len(image.data) - 4:
                raise NativeTableError(
                    f"{rom}: pointer site {pointer.site:#x} does not follow "
                    f"accessor {pointer.accessor:#x}"
                )
        for axis in table.axis_x + table.axis_y:
            axis_key = _address_key(axis)
            if axis_key not in axes:
                raise NativeTableError(
                    f"{rom}: native table {key} uses unprojected axis {axis_key}"
                )
        if key in result_maps or key in tables:
            raise NativeTableError(
                f"{rom}: native table {key} collides with the projection"
            )
        note = (
            f"Exact {rom} target-native table at {table.address:#x} bound to "
            + ", ".join(
                f"accessor {pointer.accessor:#x} through literal "
                f"{pointer.site:#x}"
                for pointer in table.pointer_bindings
            )
            + f". {table.note}"
        )
        result_maps[key] = _model(table, note)
        tables[key] = _presentation(table)
    return result_maps, result_overrides
