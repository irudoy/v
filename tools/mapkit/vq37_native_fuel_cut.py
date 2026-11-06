#!/usr/bin/env python3
"""Load exact VQ37 native fuel-cut maps for editor definitions."""

from __future__ import annotations

import copy
from dataclasses import dataclass
import hashlib
from pathlib import Path
import re
import tomllib

from tools.mapkit import rom as romkit


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = ROOT / "defs" / "vq37-native-fuel-cut.toml"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SUPPORTED_TARGETS = frozenset({"JK78C", "1ND0A", "1ND3B", "1ME3B"})
TARGET_FIELDS = frozenset({
    "stock_sha256",
    "function_address",
    "function_size",
    "function_sha256",
    "coordinator_address",
    "coordinator_pointer_site",
    "coordinator_predicate_ordinal",
    "predicate_call_site",
    "predicate_instruction_ordinal",
    "selector_address",
    "rpm_address",
    "state_address",
    "state_active_mask",
    "state_armed_mask",
    "delay_address",
    "delay_calibration_address",
    "delay_calibration_value",
    "axis_address",
    "axis_values",
    "caps_address",
    "caps_values",
    "curves_address",
    "curve_values",
    "pointer_bindings",
    "ram_pointer_bindings",
    "evidence",
})


class NativeFuelCutError(ValueError):
    """Raised when native VQ37 fuel-cut evidence is incomplete or stale."""


@dataclass(frozen=True)
class PointerBinding:
    site: int
    target: int


@dataclass(frozen=True)
class Target:
    rom: str
    stock_sha256: str
    function_address: int
    function_size: int
    function_sha256: str
    coordinator_address: int
    coordinator_pointer_site: int
    coordinator_predicate_ordinal: int
    predicate_call_site: int
    predicate_instruction_ordinal: int
    selector_address: int
    rpm_address: int
    state_address: int
    state_active_mask: int
    state_armed_mask: int
    delay_address: int
    delay_calibration_address: int
    delay_calibration_value: int
    axis_address: int
    axis_values: tuple[int, ...]
    caps_address: int
    caps_values: tuple[int, ...]
    curves_address: int
    curve_values: tuple[int, ...]
    pointer_bindings: tuple[PointerBinding, ...]
    ram_pointer_bindings: tuple[PointerBinding, ...]
    evidence: str


def _address(value, context, *, ram=False):
    valid = (
        0xFFFE0000 <= value < 0x100000000
        if ram and type(value) is int
        else type(value) is int and 0 <= value < 0x180000
    )
    if not valid:
        raise NativeFuelCutError(f"{context}: invalid address")
    return value


def _word_values(value, length, context):
    if (
        not isinstance(value, list)
        or len(value) != length
        or any(type(item) is not int or not 0 <= item <= 0xFFFF for item in value)
    ):
        raise NativeFuelCutError(
            f"{context}: expected {length} uint16 values"
        )
    return tuple(value)


def _bsr_target(data, site, context):
    word = int.from_bytes(data[site : site + 2], "big")
    if word >> 12 != 0xB:
        raise NativeFuelCutError(f"{context}: expected SH BSR instruction")
    displacement = word & 0x0FFF
    if displacement & 0x0800:
        displacement -= 0x1000
    return site + 4 + displacement * 2


def load_registry(path=DEFAULT_REGISTRY):
    path = Path(path)
    try:
        with path.open("rb") as source:
            document = tomllib.load(source)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise NativeFuelCutError(
            f"native fuel-cut registry cannot be read: {path}"
        ) from error
    if set(document) != {"schema_version", "target"} or document["schema_version"] != 1:
        raise NativeFuelCutError(f"{path}: unsupported registry schema")
    rows = document["target"]
    if not isinstance(rows, dict) or not rows:
        raise NativeFuelCutError(f"{path}: no targets")
    if set(rows) != SUPPORTED_TARGETS:
        raise NativeFuelCutError(
            f"{path}: target set differs; "
            f"actual={sorted(rows)} expected={sorted(SUPPORTED_TARGETS)}"
        )
    result = {}
    for rom, row in rows.items():
        context = f"{path} [target.{rom}]"
        if not isinstance(row, dict) or set(row) != TARGET_FIELDS:
            actual = set(row) if isinstance(row, dict) else set()
            raise NativeFuelCutError(
                f"{context}: fields differ; missing={sorted(TARGET_FIELDS - actual)}; "
                f"extra={sorted(actual - TARGET_FIELDS)}"
            )
        for key in (
            "stock_sha256",
            "function_sha256",
        ):
            if not isinstance(row[key], str) or not SHA256_RE.fullmatch(row[key]):
                raise NativeFuelCutError(f"{context}.{key}: invalid SHA-256")
        function_size = row["function_size"]
        ordinal = row["coordinator_predicate_ordinal"]
        instruction_ordinal = row["predicate_instruction_ordinal"]
        if type(function_size) is not int or function_size <= 0:
            raise NativeFuelCutError(f"{context}.function_size is invalid")
        if function_size % 2:
            raise NativeFuelCutError(f"{context}.function_size is not aligned")
        if type(ordinal) is not int or ordinal <= 0:
            raise NativeFuelCutError(
                f"{context}.coordinator_predicate_ordinal is invalid"
            )
        if type(instruction_ordinal) is not int or instruction_ordinal < 0:
            raise NativeFuelCutError(
                f"{context}.predicate_instruction_ordinal is invalid"
            )
        pointer_groups = {}
        for key, allowed_lengths, ram_target in (
            ("pointer_bindings", {3}, False),
            ("ram_pointer_bindings", {3, 4}, True),
        ):
            raw_pointers = row[key]
            if (
                not isinstance(raw_pointers, list)
                or len(raw_pointers) not in allowed_lengths
            ):
                raise NativeFuelCutError(f"{context}.{key} is invalid")
            pointers = []
            for index, pointer in enumerate(raw_pointers):
                pointer_context = f"{context}.{key}[{index}]"
                if (
                    not isinstance(pointer, dict)
                    or set(pointer) != {"site", "target"}
                ):
                    raise NativeFuelCutError(f"{pointer_context}: fields differ")
                pointers.append(PointerBinding(
                    site=_address(pointer["site"], f"{pointer_context}.site"),
                    target=_address(
                        pointer["target"],
                        f"{pointer_context}.target",
                        ram=ram_target,
                    ),
                ))
            pointer_groups[key] = tuple(pointers)
        evidence = row["evidence"]
        if not isinstance(evidence, str) or not evidence.strip():
            raise NativeFuelCutError(f"{context}.evidence is empty")
        target = Target(
            rom=rom,
            stock_sha256=row["stock_sha256"],
            function_address=_address(
                row["function_address"],
                f"{context}.function_address",
            ),
            function_size=function_size,
            function_sha256=row["function_sha256"],
            coordinator_address=_address(
                row["coordinator_address"],
                f"{context}.coordinator_address",
            ),
            coordinator_pointer_site=_address(
                row["coordinator_pointer_site"],
                f"{context}.coordinator_pointer_site",
            ),
            coordinator_predicate_ordinal=ordinal,
            predicate_call_site=_address(
                row["predicate_call_site"],
                f"{context}.predicate_call_site",
            ),
            predicate_instruction_ordinal=instruction_ordinal,
            selector_address=_address(
                row["selector_address"],
                f"{context}.selector_address",
                ram=True,
            ),
            rpm_address=_address(
                row["rpm_address"],
                f"{context}.rpm_address",
                ram=True,
            ),
            state_address=_address(
                row["state_address"],
                f"{context}.state_address",
                ram=True,
            ),
            state_active_mask=row["state_active_mask"],
            state_armed_mask=row["state_armed_mask"],
            delay_address=_address(
                row["delay_address"],
                f"{context}.delay_address",
                ram=True,
            ),
            delay_calibration_address=_address(
                row["delay_calibration_address"],
                f"{context}.delay_calibration_address",
            ),
            delay_calibration_value=row["delay_calibration_value"],
            axis_address=_address(row["axis_address"], f"{context}.axis_address"),
            axis_values=_word_values(
                row["axis_values"], 8, f"{context}.axis_values"
            ),
            caps_address=_address(row["caps_address"], f"{context}.caps_address"),
            caps_values=_word_values(
                row["caps_values"], 2, f"{context}.caps_values"
            ),
            curves_address=_address(
                row["curves_address"], f"{context}.curves_address"
            ),
            curve_values=_word_values(
                row["curve_values"], 16, f"{context}.curve_values"
            ),
            pointer_bindings=pointer_groups["pointer_bindings"],
            ram_pointer_bindings=pointer_groups["ram_pointer_bindings"],
            evidence=evidence.strip(),
        )
        if not romkit.monotone(target.axis_values):
            raise NativeFuelCutError(f"{context}.axis_values are not monotone")
        if any(value > 0xFF for value in target.axis_values):
            raise NativeFuelCutError(f"{context}.axis_values exceed selector range")
        if target.caps_values[0] <= target.caps_values[1]:
            raise NativeFuelCutError(
                f"{context}: activation cap does not exceed release cap"
            )
        if target.curve_values[:8] != (target.caps_values[0],) * 8:
            raise NativeFuelCutError(
                f"{context}: stock activation curve differs from its cap"
            )
        if target.curve_values[8:] != (target.caps_values[1],) * 8:
            raise NativeFuelCutError(
                f"{context}: stock release curve differs from its cap"
            )
        if (
            type(target.state_active_mask) is not int
            or type(target.state_armed_mask) is not int
            or not 0 < target.state_active_mask <= 0x80
            or not 0 < target.state_armed_mask <= 0x80
            or target.state_active_mask & (target.state_active_mask - 1)
            or target.state_armed_mask & (target.state_armed_mask - 1)
            or target.state_active_mask & target.state_armed_mask
        ):
            raise NativeFuelCutError(f"{context}: state masks are invalid")
        if (
            type(target.delay_calibration_value) is not int
            or not 0 <= target.delay_calibration_value <= 0xFF
        ):
            raise NativeFuelCutError(
                f"{context}: delay calibration value is invalid"
            )
        pointer_targets = tuple(
            binding.target for binding in target.pointer_bindings
        )
        expected_pointer_targets = {
            (
                target.caps_address,
                target.caps_address + 2,
                target.curves_address,
            ),
            (
                target.caps_address,
                target.curves_address,
                target.curves_address + 16,
            ),
        }
        if pointer_targets not in expected_pointer_targets:
            raise NativeFuelCutError(
                f"{context}: calibration pointer topology differs"
            )
        ram_bases = tuple(
            binding.target for binding in target.ram_pointer_bindings
        )
        if any(
            not any(base <= address < base + 0x100 for base in ram_bases)
            for address in (
                target.selector_address,
                target.rpm_address,
                target.state_address,
                target.delay_address,
            )
        ):
            raise NativeFuelCutError(
                f"{context}: native RAM state lies outside bound bases"
            )
        all_pointer_sites = (
            target.coordinator_pointer_site,
            *(binding.site for binding in target.pointer_bindings),
            *(binding.site for binding in target.ram_pointer_bindings),
        )
        if len(all_pointer_sites) != len(set(all_pointer_sites)):
            raise NativeFuelCutError(f"{context}: pointer sites are not unique")
        if target.function_address + target.function_size > 0x180000:
            raise NativeFuelCutError(f"{context}: function range is invalid")
        word_addresses = (
            target.function_address,
            target.coordinator_address,
            target.predicate_call_site,
            target.rpm_address,
            target.axis_address,
            target.caps_address,
            target.curves_address,
        )
        if any(address % 2 for address in word_addresses):
            raise NativeFuelCutError(f"{context}: word address is not aligned")
        if any(address % 4 for address in all_pointer_sites):
            raise NativeFuelCutError(
                f"{context}: long-pointer site is not aligned"
            )
        if target.predicate_call_site != (
            target.coordinator_address
            + target.predicate_instruction_ordinal * 2
        ):
            raise NativeFuelCutError(
                f"{context}: predicate call ordinal differs"
            )
        result[rom] = target
    return result


def _address_key(address):
    return f"{address:08x}"


def _model(target, address, width, height, semantics, note, axis_y=()):
    return {
        "addr": _address_key(address),
        "family": "direct-row-major" if height > 1 else "direct-indexed",
        "dims": 2 if height > 1 else 1,
        "width": width,
        "height": height if height > 1 else None,
        "storagetype": "uint16",
        "confidence": "code",
        "role": "table",
        "semantics": semantics,
        "units": "RPM",
        "scale_expr": "x*12.5",
        "to_byte": "x/12.5",
        "scale_conf": "code",
        "note": note,
        "wrappers": [],
        "kernels": [],
        "steps": [],
        "accessors": [_address_key(target.function_address)],
        "resolver_kinds": ["reviewed-target"],
        "axis_x": [],
        "axis_y": [_address_key(address) for address in axis_y],
        "diagnostic_bindings": [],
    }


def apply_target(rom, maps, overrides, image, path=DEFAULT_REGISTRY):
    """Append exact target-native VQ37 maps to a projected editor model."""
    target = load_registry(path).get(rom)
    if target is None:
        return maps, overrides
    if image.rom != rom:
        raise NativeFuelCutError(
            f"native fuel-cut target is {rom}, image is {image.rom}"
        )
    actual_sha256 = hashlib.sha256(image.data).hexdigest()
    if actual_sha256 != target.stock_sha256:
        raise NativeFuelCutError(
            f"{rom}: stock SHA-256 is {actual_sha256}, expected {target.stock_sha256}"
        )
    function = image.data[
        target.function_address : target.function_address + target.function_size
    ]
    if hashlib.sha256(function).hexdigest() != target.function_sha256:
        raise NativeFuelCutError(f"{rom}: native fuel-cut function bytes differ")
    coordinator_pointer = int.from_bytes(
        image.data[
            target.coordinator_pointer_site : target.coordinator_pointer_site + 4
        ],
        "big",
    )
    if coordinator_pointer != target.coordinator_address:
        raise NativeFuelCutError(
            f"{rom}: coordinator pointer at {target.coordinator_pointer_site:#x} "
            f"is {coordinator_pointer:#x}, expected {target.coordinator_address:#x}"
        )
    predicate_target = _bsr_target(
        image.data,
        target.predicate_call_site,
        f"{rom}.predicate_call_site",
    )
    if predicate_target != target.function_address:
        raise NativeFuelCutError(
            f"{rom}: predicate call targets {predicate_target:#x}, "
            f"expected {target.function_address:#x}"
        )
    delay_calibration = image.data[target.delay_calibration_address]
    if delay_calibration != target.delay_calibration_value:
        raise NativeFuelCutError(
            f"{rom}: delay calibration is {delay_calibration:#x}, "
            f"expected {target.delay_calibration_value:#x}"
        )
    axis_values = tuple(
        image.values(_address_key(target.axis_address), 8, "uint16")
    )
    caps_values = tuple(
        image.values(_address_key(target.caps_address), 2, "uint16")
    )
    curve_values = tuple(
        image.values(_address_key(target.curves_address), 16, "uint16")
    )
    if axis_values != target.axis_values:
        raise NativeFuelCutError(f"{rom}: native fuel-cut axis bytes differ")
    if caps_values != target.caps_values:
        raise NativeFuelCutError(f"{rom}: native fuel-cut cap bytes differ")
    if curve_values != target.curve_values:
        raise NativeFuelCutError(f"{rom}: native fuel-cut curve bytes differ")
    for pointer in target.pointer_bindings:
        actual = int.from_bytes(image.data[pointer.site : pointer.site + 4], "big")
        if actual != pointer.target:
            raise NativeFuelCutError(
                f"{rom}: pointer at {pointer.site:#x} is {actual:#x}, "
                f"expected {pointer.target:#x}"
            )
    for pointer in target.ram_pointer_bindings:
        actual = int.from_bytes(image.data[pointer.site : pointer.site + 4], "big")
        if actual != pointer.target:
            raise NativeFuelCutError(
                f"{rom}: RAM pointer at {pointer.site:#x} is {actual:#x}, "
                f"expected {pointer.target:#x}"
            )

    result_maps = copy.deepcopy(maps)
    result_overrides = copy.deepcopy(overrides)
    tables = result_overrides.setdefault("table", {})
    if not isinstance(tables, dict):
        raise NativeFuelCutError("definition table overrides must be a table")
    base_note = (
        f"Exact {rom} native fuel-cut model at {target.function_address:#x}; "
        f"selector {target.selector_address:#x}, shared axis {target.axis_address:#x}. "
        f"{target.evidence}"
    )
    caps_key = _address_key(target.caps_address)
    curves_key = _address_key(target.curves_address)
    if (
        caps_key in result_maps
        or curves_key in result_maps
        or caps_key in tables
        or curves_key in tables
    ):
        raise NativeFuelCutError(
            f"{rom}: native fuel-cut address collides with projection"
        )
    result_maps[caps_key] = _model(
        target,
        target.caps_address,
        2,
        1,
        "Native VQ37 fuel-cut activation and release scalar caps.",
        base_note,
    )
    result_maps[curves_key] = _model(
        target,
        target.curves_address,
        8,
        2,
        "Native VQ37 fuel-cut activation and release curves on the filtered raw "
        "oil-thermistor code; a lower code is a higher oil temperature.",
        base_note
        + " The two rows are interpolated independently; "
        "no interpolation occurs between rows.",
        axis_y=(target.axis_address,),
    )
    tables[caps_key] = {
        "name": "Engine Speed Limit - Fuel Cut Caps",
        "category": "Limiters / Engine Speed / Driving",
        "order": 200,
        "emit": True,
        "format": "0.0",
        "fine": 12.5,
        "coarse": 125,
        "static_axis": ["Activation", "Release"],
    }
    tables[curves_key] = {
        "name": "Engine Speed Limit - Fuel Cut Curves",
        "category": "Limiters / Engine Speed / Driving",
        "order": 201,
        "emit": True,
        "format": "0.0",
        "fine": 12.5,
        "coarse": 125,
        "static_axis_y_name": "Transition",
        "static_axis_y": ["Activation", "Release"],
    }
    return result_maps, result_overrides
