#!/usr/bin/env python3
"""Project canonical editor facts onto reviewed relocated ROM addresses.

Exact-code inheritance and relocated definition projection are deliberately
separate contracts. This module consumes only tracked address correspondences,
binds them to exact stock-image hashes, and produces an in-memory target model.
It does not create target semantic claims in Memgraph.
"""

from __future__ import annotations

import argparse
import copy
import csv
from dataclasses import dataclass, replace
import hashlib
from pathlib import Path
import re
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import map_switching_layout
from patches import rolling_launch_layout
from patches import rom_address_profiles
from patches import rom_checksums
from tools.mapkit import rom as romkit


DEFAULT_REGISTRY = ROOT / "defs" / "definition-projections.toml"
ADDRESS_FIELDS = (
    "entity",
    "source",
    "target",
    "variant",
    "status",
    "sites",
    "function_kinds",
    "evidence",
)
PROJECTION_FIELDS = frozenset(
    {
        "source",
        "source_sha256",
        "target_sha256",
        "addresses",
        "checksum",
        "romraider_checksum",
        "map_switching",
        "rolling_launch",
        "switch",
        "comment",
        "evidence",
    }
)
ENTITIES = frozenset({"Map", "Axis"})
MAPPED_STATUSES = frozenset(
    {"homologous-call", "homologous-exact-chain", "reviewed-target"}
)
STATUS_UNSUPPORTED = "unsupported"
ADDRESS_RE = re.compile(r"^[0-9a-f]{8}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SWITCH_NAMES = {
    "developer_immobilizer": "Developer Immobilizer",
    "can_telemetry_startup": "CAN Telemetry at Startup",
}


class DefinitionProjectionError(ValueError):
    """Raised when a relocated definition projection is not exact or complete."""


@dataclass(frozen=True)
class AddressBinding:
    entity: str
    source: str
    target: str
    variant: str
    status: str
    sites: int
    function_kinds: str
    evidence: str

    @property
    def mapped(self):
        return self.status in MAPPED_STATUSES


@dataclass(frozen=True)
class DefinitionProjection:
    target: str
    source: str
    source_sha256: str
    target_sha256: str
    address_path: Path
    checksum: bool
    romraider_checksum: bool
    map_switching: bool
    rolling_launch: bool
    switch_addresses: tuple[tuple[str, int], ...]
    comment: str
    evidence: str
    bindings: tuple[AddressBinding, ...]

    @property
    def switch_address_by_key(self):
        return dict(self.switch_addresses)

    @property
    def unsupported_maps(self):
        return frozenset(
            binding.source
            for binding in self.bindings
            if binding.entity == "Map"
            and binding.status == STATUS_UNSUPPORTED
        )


@dataclass(frozen=True)
class AppliedAddressProjection:
    maps: dict
    axes: dict
    overrides: dict
    mapped_map_count: int
    mapped_axis_count: int
    unsupported_required_maps: tuple[str, ...]


def _read_addresses(path):
    try:
        with path.open(newline="", encoding="utf-8") as source:
            reader = csv.DictReader(source)
            if tuple(reader.fieldnames or ()) != ADDRESS_FIELDS:
                raise DefinitionProjectionError(
                    f"{path}: header differs; expected {list(ADDRESS_FIELDS)}"
                )
            raw_rows = list(reader)
    except OSError as error:
        raise DefinitionProjectionError(
            f"definition correspondence cannot be read: {path}"
        ) from error

    bindings = []
    target_keys = set()
    source_rows = {}
    for row_number, row in enumerate(raw_rows, 2):
        context = f"{path}:{row_number}"
        if None in row or any(value is None for value in row.values()):
            raise DefinitionProjectionError(
                f"{context}: field count differs from the header"
            )
        entity = row["entity"]
        source_address = row["source"]
        target_address = row["target"]
        status = row["status"]
        if entity not in ENTITIES:
            raise DefinitionProjectionError(f"{context}: invalid entity")
        if not ADDRESS_RE.fullmatch(source_address):
            raise DefinitionProjectionError(
                f"{context}: invalid source address {source_address!r}"
            )
        if status == STATUS_UNSUPPORTED:
            if entity != "Map" or target_address or row["variant"]:
                raise DefinitionProjectionError(
                    f"{context}: only a source Map may be unsupported"
                )
        elif status in MAPPED_STATUSES:
            if not ADDRESS_RE.fullmatch(target_address):
                raise DefinitionProjectionError(
                    f"{context}: invalid target address {target_address!r}"
                )
        else:
            raise DefinitionProjectionError(
                f"{context}: unsupported status {status!r}"
            )
        try:
            sites = int(row["sites"])
        except ValueError as error:
            raise DefinitionProjectionError(
                f"{context}: sites must be decimal"
            ) from error
        if sites < 0 or not row["evidence"].strip():
            raise DefinitionProjectionError(
                f"{context}: sites or evidence is invalid"
            )

        binding = AddressBinding(
            entity=entity,
            source=source_address,
            target=target_address,
            variant=row["variant"],
            status=status,
            sites=sites,
            function_kinds=row["function_kinds"],
            evidence=row["evidence"],
        )
        key = (entity, source_address)
        source_rows.setdefault(key, []).append(binding)
        if binding.mapped:
            target_key = (entity, target_address)
            if target_key in target_keys:
                raise DefinitionProjectionError(
                    f"{context}: duplicate target {entity} {target_address}"
                )
            target_keys.add(target_key)
        bindings.append(binding)

    if not bindings:
        raise DefinitionProjectionError(f"{path}: no address bindings")
    for key, rows in source_rows.items():
        mapped = [row for row in rows if row.mapped]
        unsupported = [row for row in rows if row.status == STATUS_UNSUPPORTED]
        if mapped and unsupported:
            raise DefinitionProjectionError(
                f"{path}: {key[0]} {key[1]} is both mapped and unsupported"
            )
        if len(mapped) > 1:
            variants = [row.variant for row in mapped]
            if not all(variants) or len(set(variants)) != len(variants):
                raise DefinitionProjectionError(
                    f"{path}: duplicate source {key[0]} {key[1]} needs "
                    "unique variants"
                )
    return tuple(bindings)


def _parse_projection(target, row, path):
    context = f"{path} [projection.{target}]"
    if not isinstance(row, dict) or set(row) != PROJECTION_FIELDS:
        actual = set(row) if isinstance(row, dict) else set()
        raise DefinitionProjectionError(
            f"{context}: fields differ; "
            f"missing={sorted(PROJECTION_FIELDS - actual)}; "
            f"extra={sorted(actual - PROJECTION_FIELDS)}"
        )
    source = row["source"]
    if not isinstance(source, str) or not source or source == target:
        raise DefinitionProjectionError(f"{context}.source is invalid")
    for key in ("source_sha256", "target_sha256"):
        if not isinstance(row[key], str) or not SHA256_RE.fullmatch(row[key]):
            raise DefinitionProjectionError(f"{context}.{key} is not a SHA-256")
    for key in (
        "checksum",
        "romraider_checksum",
        "map_switching",
        "rolling_launch",
    ):
        if type(row[key]) is not bool:
            raise DefinitionProjectionError(f"{context}.{key} must be a boolean")
    if row["romraider_checksum"] and not row["checksum"]:
        raise DefinitionProjectionError(
            f"{context}.romraider_checksum requires checksum support"
        )
    address_name = row["addresses"]
    if (
        not isinstance(address_name, str)
        or Path(address_name).name != address_name
        or not address_name.endswith(".csv")
    ):
        raise DefinitionProjectionError(
            f"{context}.addresses must name one CSV beside the registry"
        )
    switches = row["switch"]
    if not isinstance(switches, dict):
        raise DefinitionProjectionError(f"{context}.switch must be a table")
    unknown_switches = sorted(set(switches) - set(SWITCH_NAMES))
    if unknown_switches:
        raise DefinitionProjectionError(
            f"{context}.switch contains unknown keys {unknown_switches}"
        )
    switch_addresses = []
    for key, address in switches.items():
        if type(address) is not int or not 0 <= address < 0x180000:
            raise DefinitionProjectionError(
                f"{context}.switch.{key} is not a ROM address"
            )
        switch_addresses.append((key, address))
    for key in ("comment", "evidence"):
        if not isinstance(row[key], str) or not row[key].strip():
            raise DefinitionProjectionError(f"{context}.{key} is empty")
    address_path = path.parent / address_name
    return DefinitionProjection(
        target=target,
        source=source,
        source_sha256=row["source_sha256"],
        target_sha256=row["target_sha256"],
        address_path=address_path,
        checksum=row["checksum"],
        romraider_checksum=row["romraider_checksum"],
        map_switching=row["map_switching"],
        rolling_launch=row["rolling_launch"],
        switch_addresses=tuple(sorted(switch_addresses)),
        comment=row["comment"].strip(),
        evidence=row["evidence"].strip(),
        bindings=_read_addresses(address_path),
    )


def load_registry(path=DEFAULT_REGISTRY):
    path = Path(path)
    try:
        with path.open("rb") as source:
            document = tomllib.load(source)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise DefinitionProjectionError(
            f"definition projection registry cannot be loaded: {path}: {error}"
        ) from error
    if set(document) != {"schema_version", "projection"}:
        raise DefinitionProjectionError(
            f"{path}: expected only schema_version and projection"
        )
    if document["schema_version"] != 3:
        raise DefinitionProjectionError(f"{path}: unsupported schema_version")
    rows = document["projection"]
    if not isinstance(rows, dict) or not rows:
        raise DefinitionProjectionError(f"{path}: no projections")
    return {
        target: _parse_projection(target, row, path)
        for target, row in rows.items()
    }


def projection_for_rom(rom, path=DEFAULT_REGISTRY):
    """Return a relocated definition projection, or None for other ROMs."""
    return load_registry(path).get(rom)


def verify_image_binding(projection):
    """Bind a projection to exact source and target stock image hashes."""
    for rom, expected in (
        (projection.source, projection.source_sha256),
        (projection.target, projection.target_sha256),
    ):
        image = romkit.load(rom)
        actual = hashlib.sha256(image.data).hexdigest()
        if actual != expected:
            raise DefinitionProjectionError(
                f"{rom}: definition projection SHA-256 is {expected}, "
                f"stock image is {actual}"
            )


def _downgrade(value, binding):
    if binding.status in {"homologous-call", "homologous-exact-chain"}:
        return "candidate" if value == "code" else value
    return value


def _variant_label(variant):
    return variant.replace("_", " ").title()


def _append_projection_note(note, projection, binding):
    statement = (
        f"Definition address projected from {projection.source} "
        f"{binding.source} through {projection.address_path.name}: "
        f"{binding.evidence}."
    )
    return f"{note.rstrip()} {statement}".strip()


def _select_axis_binding(rows, variant, map_source):
    if len(rows) == 1:
        return rows[0]
    matches = [row for row in rows if row.variant == variant]
    if len(matches) != 1:
        raise DefinitionProjectionError(
            f"{map_source}: axis projection for variant {variant!r} is ambiguous"
        )
    return matches[0]


def _target_checksums(rom, source_checksums):
    try:
        layout = rom_checksums.layout_for_rom(rom)
    except rom_checksums.ChecksumError as error:
        raise DefinitionProjectionError(str(error)) from error
    comments = {
        entry.get("type"): entry.get("comment")
        for entry in source_checksums
        if isinstance(entry, dict)
    }
    runtime_b = {
        "type": "alt",
        "start": f"0x{layout.runtime_b_start:X}",
        "end": f"0x{layout.runtime_b_end:X}",
        "sumloc": f"0x{layout.runtime_b_sum_field:X}",
        "xorloc": f"0x{layout.runtime_b_xor_field:X}",
    }
    runtime_a = {
        "type": "alt2",
        "start": f"0x{layout.sum16_a_field:X}",
        "end": f"0x{layout.rom_size:X}",
        "skiploc": f"0x{layout.sum16_b_field:X}",
        "sumloc": f"0x{layout.runtime_a_sum_field:X}",
        "xorloc": f"0x{layout.runtime_a_xor_field:X}",
    }
    if comments.get("alt"):
        runtime_b["comment"] = comments["alt"]
    if comments.get("alt2"):
        runtime_a["comment"] = comments["alt2"]
    return [runtime_b, runtime_a]


def _target_switches(projection, source_switches, image):
    entries = source_switches
    if isinstance(entries, dict):
        entries = [entries]
    if not isinstance(entries, list):
        raise DefinitionProjectionError("definition switches must be a list")
    by_name = {entry.get("name"): entry for entry in entries}
    projected = []
    for key, address in projection.switch_addresses:
        name = SWITCH_NAMES[key]
        source = by_name.get(name)
        if source is None:
            raise DefinitionProjectionError(
                f"{projection.target}: source switch {name!r} is absent"
            )
        entry = copy.deepcopy(source)
        entry["storageaddress"] = f"0x{address:X}"
        if key == "developer_immobilizer":
            expected = bytes.fromhex(entry["state"][0]["data"])
            actual = image.data[address : address + len(expected)]
            if actual != expected:
                raise DefinitionProjectionError(
                    f"{projection.target}: {name} stock bytes at "
                    f"{address:#x} are {actual.hex()}, expected {expected.hex()}"
                )
        projected.append(entry)
    return projected


def apply_projection(
    projection,
    maps,
    axes,
    overrides,
    image,
    *,
    required_maps=(),
):
    """Return a target-addressed definition model from canonical source facts."""
    if image.rom != projection.target:
        raise DefinitionProjectionError(
            f"projection targets {projection.target}, image is {image.rom}"
        )
    mapped_rows = [binding for binding in projection.bindings if binding.mapped]
    required = set(required_maps)
    selected_sources = set(required)
    switching = overrides.get("map_switching", {})
    if (
        projection.map_switching
        and isinstance(switching, dict)
        and switching.get("enabled", False)
    ):
        selected_sources.update(
            f"{family.canonical_address:08x}"
            for family in map_switching_layout.load_layout().families
        )

    # The Ghidra operand correspondence is intentionally broader than the
    # editor model. Apply only visible tables and mandatory runtime families;
    # the remaining rows stay available as durable analysis evidence.
    map_rows = [
        binding
        for binding in mapped_rows
        if binding.entity == "Map"
        and binding.source in maps
        and binding.source in selected_sources
    ]
    needed_axes = {
        address
        for binding in map_rows
        for key in ("axis_x", "axis_y")
        for address in maps[binding.source].get(key, [])
    }
    # Direct-row-major tables can expose an operand that is represented as a
    # reviewed static axis rather than an :Axis fact. Such rows are not needed
    # by the target editor model.
    axis_rows = [
        binding
        for binding in mapped_rows
        if binding.entity == "Axis"
        and binding.source in axes
        and binding.source in needed_axes
    ]
    unsupported = projection.unsupported_maps
    covered = {binding.source for binding in map_rows} | set(unsupported)
    missing = sorted(required - covered)
    if missing:
        raise DefinitionProjectionError(
            f"{projection.target}: visible source maps lack correspondence: "
            + ", ".join(missing)
        )

    axis_by_source = {}
    for binding in axis_rows:
        axis_by_source.setdefault(binding.source, []).append(binding)

    projected_axes = {}
    projected_axis_overrides = {}
    source_axis_overrides = overrides.get("axis", {})
    if not isinstance(source_axis_overrides, dict):
        raise DefinitionProjectionError("definition axis overrides must be a table")
    for binding in axis_rows:
        axis = copy.deepcopy(axes[binding.source])
        axis["addr"] = binding.target
        axis["confidence"] = _downgrade(axis.get("confidence"), binding)
        axis["scale_conf"] = _downgrade(axis.get("scale_conf"), binding)
        axis["note"] = _append_projection_note(
            axis.get("note", ""), projection, binding
        )
        projected_axes[binding.target] = axis
        if binding.source in source_axis_overrides:
            projected_axis_overrides[binding.target] = copy.deepcopy(
                source_axis_overrides[binding.source]
            )

    source_tables = overrides.get("table", {})
    if not isinstance(source_tables, dict):
        raise DefinitionProjectionError("definition table overrides must be a table")
    projected_maps = {}
    projected_tables = {}
    map_targets = {}
    for binding in map_rows:
        source_map = maps.get(binding.source)
        if source_map is None:
            raise DefinitionProjectionError(
                f"{projection.address_path}: source Map {binding.source} is absent"
            )
        calibration = copy.deepcopy(source_map)
        calibration["addr"] = binding.target
        calibration["confidence"] = _downgrade(
            calibration.get("confidence"), binding
        )
        calibration["scale_conf"] = _downgrade(
            calibration.get("scale_conf"), binding
        )
        for key in ("axis_x", "axis_y"):
            remapped = []
            for source_axis in calibration.get(key, []):
                rows = axis_by_source.get(source_axis, [])
                if not rows:
                    raise DefinitionProjectionError(
                        f"{projection.target}: Map {binding.source} uses "
                        f"unmapped Axis {source_axis}"
                    )
                remapped.append(
                    _select_axis_binding(
                        rows, binding.variant, binding.source
                    ).target
                )
            calibration[key] = remapped
        calibration["wrappers"] = []
        calibration["kernels"] = []
        calibration["accessors"] = []
        calibration["resolver_kinds"] = []
        calibration["diagnostic_bindings"] = []
        calibration["note"] = _append_projection_note(
            calibration.get("note", ""), projection, binding
        )
        if binding.variant:
            label = _variant_label(binding.variant)
            calibration["semantics"] = (
                f"{calibration['semantics']} Target variant: {label}."
            )
        projected_maps[binding.target] = calibration
        map_targets.setdefault(binding.source, []).append(binding)

        source_override = source_tables.get(binding.source)
        if source_override is not None:
            target_override = copy.deepcopy(source_override)
            if binding.variant and target_override.get("name"):
                target_override["name"] = (
                    f"{target_override['name']} - "
                    f"{_variant_label(binding.variant)}"
                )
            projected_tables[binding.target] = target_override

        element_size = romkit.ELEM[calibration["storagetype"]]
        length = calibration["width"] * (calibration.get("height") or 1)
        start = int(binding.target, 16)
        end = start + length * element_size
        if end > len(image):
            raise DefinitionProjectionError(
                f"{projection.target}: mapped Map {binding.target} is "
                "outside the stock image"
            )
        values = image.values(binding.target, length, calibration["storagetype"])
        if romkit.erased(values, calibration["storagetype"]):
            raise DefinitionProjectionError(
                f"{projection.target}: mapped Map {binding.target} is erased"
            )

    for binding in axis_rows:
        axis = projected_axes[binding.target]
        start = int(binding.target, 16)
        end = start + axis["len"] * romkit.ELEM[axis["storagetype"]]
        if end > len(image):
            raise DefinitionProjectionError(
                f"{projection.target}: mapped Axis {binding.target} is "
                "outside the stock image"
            )
        values = image.values(binding.target, axis["len"], axis["storagetype"])
        if romkit.erased(values, axis["storagetype"]):
            raise DefinitionProjectionError(
                f"{projection.target}: mapped Axis {binding.target} is erased"
            )
        if not romkit.monotone(values):
            raise DefinitionProjectionError(
                f"{projection.target}: mapped Axis {binding.target} is not monotone"
            )
        axis["values"] = values

    projected_overrides = copy.deepcopy(overrides)
    projected_overrides["table"] = projected_tables
    if projected_axis_overrides:
        projected_overrides["axis"] = projected_axis_overrides
    else:
        projected_overrides.pop("axis", None)

    source_axis_views = overrides.get("axisview", {})
    if not isinstance(source_axis_views, dict):
        raise DefinitionProjectionError("definition axisview must be a table")
    projected_axis_views = {}
    for source_axis, value in source_axis_views.items():
        for binding in axis_by_source.get(source_axis, []):
            projected_axis_views[binding.target] = copy.deepcopy(value)
    if projected_axis_views:
        projected_overrides["axisview"] = projected_axis_views
    else:
        projected_overrides.pop("axisview", None)

    source_views = overrides.get("masked_view", [])
    if isinstance(source_views, dict):
        source_views = [source_views]
    if not isinstance(source_views, list):
        raise DefinitionProjectionError("masked_view must be a list")
    target_views = []
    for view in source_views:
        for binding in map_targets.get(str(view.get("source", "")).lower(), []):
            target_view = copy.deepcopy(view)
            target_view["source"] = binding.target
            if binding.variant:
                target_view["name"] = (
                    f"{target_view['name']} - {_variant_label(binding.variant)}"
                )
            target_views.append(target_view)
    if target_views:
        projected_overrides["masked_view"] = target_views
    else:
        projected_overrides.pop("masked_view", None)

    if projection.romraider_checksum:
        source_checksums = overrides.get("checksum", [])
        if isinstance(source_checksums, dict):
            source_checksums = [source_checksums]
        projected_overrides["checksum"] = _target_checksums(
            projection.target, source_checksums
        )
    else:
        projected_overrides.pop("checksum", None)
    projected_overrides["switch"] = _target_switches(
        projection, overrides.get("switch", []), image
    )
    projected_overrides["map_switching"] = {
        "enabled": projection.map_switching
    }
    projected_overrides["rolling_launch"] = {
        "enabled": projection.rolling_launch
    }
    projected_overrides["rom"]["comment"] = {"text": projection.comment}

    return AppliedAddressProjection(
        maps=projected_maps,
        axes=projected_axes,
        overrides=projected_overrides,
        mapped_map_count=len(projected_maps),
        mapped_axis_count=len(projected_axes),
        unsupported_required_maps=tuple(sorted(required & unsupported)),
    )


def map_switching_definition_layout(projection):
    """Materialize the target's five-slot editor storage layout."""
    source = map_switching_layout.load_layout()
    profile = rom_address_profiles.profile_for_rom(projection.target)
    if source.rom != profile.layout_source:
        raise DefinitionProjectionError(
            f"{projection.target}: map layout source differs from address profile"
        )
    families = []
    for family in source.families:
        if family.key == "exhaust_cvtc_target":
            common = {
                "stock_container_start": profile.map_family_by_key[
                    "exhaust_cvtc_target_even"
                ],
                "stock_container_size": family.stock_container_size,
            }
            families.append(
                replace(
                    family,
                    key="exhaust_cvtc_target_even",
                    name=f"{family.name} Bank 1",
                    canonical_address=profile.map_family_by_key[
                        "exhaust_cvtc_target_even"
                    ],
                    copies=tuple(
                        address + profile.rom_delta for address in family.copies
                    ),
                    pointer_table=family.pointer_table + profile.rom_delta,
                    **common,
                )
            )
            families.append(
                replace(
                    family,
                    key="exhaust_cvtc_target_odd",
                    name=f"{family.name} Bank 2",
                    canonical_address=profile.map_family_by_key[
                        "exhaust_cvtc_target_odd"
                    ],
                    copies=profile.extra_exhaust_storage.copies,
                    pointer_table=profile.extra_exhaust_storage.pointer_table,
                    stock_container_start=profile.map_family_by_key[
                        "exhaust_cvtc_target_odd"
                    ],
                    stock_container_size=family.stock_container_size,
                )
            )
            continue
        target_address = profile.map_family_by_key[family.key]
        families.append(
            replace(
                family,
                canonical_address=target_address,
                copies=tuple(
                    address + profile.rom_delta for address in family.copies
                ),
                pointer_table=family.pointer_table + profile.rom_delta,
                stock_container_start=(
                    profile.map_symbol_by_key["throttle_container"]
                    if family.key == "rev_limit_throttle_cut"
                    else target_address
                ),
            )
        )
    return replace(
        source,
        rom=projection.target,
        source_sha256=projection.target_sha256,
        families=tuple(families),
    )


def rolling_launch_definition_layout(projection):
    """Return the target configuration address used by editor controls."""
    source = rolling_launch_layout.load_layout()
    profile = rom_address_profiles.profile_for_rom(projection.target)
    return replace(
        source,
        rom=projection.target,
        source_sha256=projection.target_sha256,
        configuration=replace(
            source.configuration,
            start=source.configuration.start + profile.rom_delta,
            end=source.configuration.end + profile.rom_delta,
        ),
    )


def validate_registry(path=DEFAULT_REGISTRY):
    """Validate every declared projection and its exact image bindings."""
    projections = load_registry(path)
    stats = {}
    for target, projection in projections.items():
        verify_image_binding(projection)
        source_image = romkit.load(projection.source)
        target_image = romkit.load(target)
        for binding in projection.bindings:
            if int(binding.source, 16) >= len(source_image):
                raise DefinitionProjectionError(
                    f"{target}: source {binding.entity} {binding.source} "
                    "is outside the stock image"
                )
            if binding.mapped and int(binding.target, 16) >= len(target_image):
                raise DefinitionProjectionError(
                    f"{target}: target {binding.entity} {binding.target} "
                    "is outside the stock image"
                )
        map_layout = (
            map_switching_definition_layout(projection)
            if projection.map_switching
            else None
        )
        launch_layout = (
            rolling_launch_definition_layout(projection)
            if projection.rolling_launch
            else None
        )
        if projection.checksum:
            rom_checksums.layout_for_rom(target)
        stats[target] = {
            "bindings": len(projection.bindings),
            "mapped": sum(binding.mapped for binding in projection.bindings),
            "unsupported": len(projection.unsupported_maps),
            "checksum": projection.checksum,
            "romraider_checksum": projection.romraider_checksum,
            "map_families": len(map_layout.families) if map_layout else 0,
            "rolling_configuration": (
                launch_layout.configuration.start if launch_layout else None
            ),
        }
    return stats


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Validate SHA-bound relocated definition projections"
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("--check is required")
    for target, values in validate_registry(args.registry).items():
        rolling_configuration = values["rolling_configuration"]
        rolling_text = (
            f"{rolling_configuration:#x}"
            if rolling_configuration is not None
            else "disabled"
        )
        print(
            f"{target}: bindings={values['bindings']}, "
            f"mapped={values['mapped']}, "
            f"unsupported={values['unsupported']}, "
            f"checksum={'verified' if values['checksum'] else 'unknown'}, "
            "romraider_checksum="
            f"{'enabled' if values['romraider_checksum'] else 'disabled'}, "
            f"map_families={values['map_families']}, "
            f"rolling_configuration={rolling_text}"
        )
    print("status=PASS; no default target selected")


if __name__ == "__main__":
    main()
