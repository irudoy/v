"""Definition projection for the JK08A Rolling Launch configuration.

The runtime stores one enable bit per map and the RPM hold hysteresis in its
validated configuration record. This module adds one five-bit switch and one
synthetic hysteresis calibration to the common JK08A RomRaider and TunerPro
models. It does not write definitions or ROM images.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass

from patches import rolling_launch as contract
from patches import rolling_launch_layout


@dataclass(frozen=True)
class DefinitionProjection:
    maps: dict
    overrides: dict
    configuration_address: str
    enable_mask_address: str
    hysteresis_address: str
    table_count: int
    masked_view_count: int
    bitwise_switch_count: int
    enable_bit_count: int

    @property
    def editor_view_count(self):
        return self.table_count + self.bitwise_switch_count


def address_key(address):
    return f"{address:08x}"


def load_layout():
    return rolling_launch_layout.load_layout()


def _bitwise_switch_entries(overrides):
    entries = overrides.get("bitwise_switch", [])
    if isinstance(entries, dict):
        entries = [entries]
    if not isinstance(entries, list):
        raise ValueError(
            "bitwise_switch must be a table or an array of tables"
        )
    return entries


def _enable_switch(address):
    return {
        "name": "Rolling Launch Enable by Map",
        "category": "Rolling Launch / Map Enable",
        "storageaddress": f"0x{address:X}",
        "storagetype": "uint8",
        "endian": "big",
        "userlevel": "5",
        "description": (
            "Exact JK08A. Each checkbox independently enables Rolling Launch "
            "for one map and preserves the other bits. Bits 5 through 7 must "
            "remain clear; the runtime rejects the configuration otherwise."
        ),
        "bit": [
            {
                "name": f"Map {slot} - Rolling Launch Enable",
                "position": slot - 1,
            }
            for slot in range(1, contract.SLOT_COUNT + 1)
        ],
    }


def _hysteresis_model(address):
    return {
        "addr": address_key(address),
        "family": "direct-scalar",
        "dims": 1,
        "width": 1,
        "height": None,
        "storagetype": "uint16",
        "confidence": "code",
        "role": "table",
        "semantics": (
            "Rolling Launch fuel-cut restore hysteresis in the validated "
            "runtime configuration record"
        ),
        "units": "RPM",
        "scale_expr": "x*12.5",
        "to_byte": "x/12.5",
        "scale_conf": "code",
        "note": (
            "The runtime computes Restore = Cut - hysteresis, accepts only "
            "0 < hysteresis_native < min_rpm_native, and rejects the entire "
            "configuration otherwise. The default value is 8 native counts, "
            "or 100 RPM."
        ),
        "wrappers": [],
        "kernels": [],
        "steps": [],
        "accessors": [],
        "resolver_kinds": [],
        "axis_x": [],
        "axis_y": [],
        "diagnostic_bindings": [],
        "rolling_launch_configuration": True,
    }


def _hysteresis_presentation():
    return {
        "name": "Rolling Launch RPM Hysteresis",
        "category": "Rolling Launch / RPM Hold",
        "order": 900010,
        "emit": True,
        "format": "0.0",
        "fine": 12.5,
        "coarse": 100,
        "static_axis_name": "Configuration",
        "static_axis": ["Hysteresis"],
    }


def project_definition_model(maps, overrides, layout=None):
    """Add Rolling Launch enable and hysteresis controls to a definition model."""
    layout = layout or load_layout()
    projected_maps = deepcopy(maps)
    projected_overrides = deepcopy(overrides)
    table_overrides = projected_overrides.get("table")
    if not isinstance(table_overrides, dict):
        raise ValueError("definition overrides must contain a table mapping")

    configuration_address = layout.configuration.start
    enable_mask_address = configuration_address + 4
    hysteresis_address = configuration_address + 0x10
    enable_key = address_key(enable_mask_address)
    hysteresis_key = address_key(hysteresis_address)
    if enable_key in projected_maps or enable_key in table_overrides:
        raise ValueError(
            f"Rolling Launch enable-switch address {enable_key} collides"
        )
    if hysteresis_key in projected_maps or hysteresis_key in table_overrides:
        raise ValueError(
            f"Rolling Launch hysteresis address {hysteresis_key} collides"
        )

    projected_maps[hysteresis_key] = _hysteresis_model(hysteresis_address)
    table_overrides[hysteresis_key] = _hysteresis_presentation()

    existing_switches = _bitwise_switch_entries(projected_overrides)
    if any(
        int(str(entry.get("storageaddress", "-1")), 0)
        == enable_mask_address
        for entry in existing_switches
    ):
        raise ValueError(
            f"Rolling Launch enable-switch address {enable_key} collides"
        )
    projected_overrides["bitwise_switch"] = (
        deepcopy(existing_switches) + [_enable_switch(enable_mask_address)]
    )

    projection = DefinitionProjection(
        maps=projected_maps,
        overrides=projected_overrides,
        configuration_address=address_key(configuration_address),
        enable_mask_address=enable_key,
        hysteresis_address=hysteresis_key,
        table_count=1,
        masked_view_count=0,
        bitwise_switch_count=1,
        enable_bit_count=contract.SLOT_COUNT,
    )
    validate_projection(projection, maps, overrides, layout)
    return projection


def validate_projection(projection, source_maps, source_overrides, layout=None):
    """Validate synthetic controls, five independent bits, and preservation."""
    layout = layout or load_layout()
    expected_configuration = address_key(layout.configuration.start)
    expected_enable = address_key(layout.configuration.start + 4)
    expected_hysteresis = address_key(layout.configuration.start + 0x10)
    if projection.configuration_address != expected_configuration:
        raise ValueError("Rolling Launch configuration address differs")
    if projection.enable_mask_address != expected_enable:
        raise ValueError("Rolling Launch enable-mask address differs")
    if projection.hysteresis_address != expected_hysteresis:
        raise ValueError("Rolling Launch hysteresis address differs")
    if projection.table_count != 1:
        raise ValueError(
            "Rolling Launch projection must contain one calibration table"
        )
    if projection.masked_view_count != 0:
        raise ValueError("Rolling Launch projection must not contain masked views")
    if projection.bitwise_switch_count != 1:
        raise ValueError(
            "Rolling Launch projection must contain one bitwise switch"
        )
    if projection.enable_bit_count != contract.SLOT_COUNT:
        raise ValueError("Rolling Launch bitwise switch must contain five bits")
    if expected_enable in projection.maps:
        raise ValueError("Rolling Launch raw enable-mask table is visible")
    if projection.maps.get(expected_hysteresis) != _hysteresis_model(
        layout.configuration.start + 0x10
    ):
        raise ValueError("Rolling Launch hysteresis model differs")
    if projection.overrides["table"].get(
        expected_hysteresis
    ) != _hysteresis_presentation():
        raise ValueError("Rolling Launch hysteresis presentation differs")

    projected_switches = [
        entry
        for entry in _bitwise_switch_entries(projection.overrides)
        if int(str(entry.get("storageaddress", "-1")), 0)
        == layout.configuration.start + 4
    ]
    if projected_switches != [_enable_switch(layout.configuration.start + 4)]:
        raise ValueError("Rolling Launch per-map bitwise switch differs")
    positions = [
        bit["position"] for bit in projected_switches[0]["bit"]
    ]
    if positions != list(range(contract.SLOT_COUNT)):
        raise ValueError("Rolling Launch enable-bit positions differ")

    for address, model in source_maps.items():
        if projection.maps.get(address) != model:
            raise ValueError(
                f"source map {address} changed during Rolling Launch projection"
            )
    for address, presentation in source_overrides.get("table", {}).items():
        if projection.overrides["table"].get(address) != presentation:
            raise ValueError(
                f"source presentation {address} changed during Rolling Launch projection"
            )
    return projection
