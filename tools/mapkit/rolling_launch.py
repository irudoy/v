"""Definition projection for the JK08A Rolling Launch enable mask.

The runtime stores one enable bit per map in its validated configuration
record. This module adds a single synthetic one-byte calibration source and
five masked editor views to the common JK08A RomRaider and TunerPro models.
It does not write definitions or ROM images.
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
    table_count: int
    masked_view_count: int

    @property
    def editor_view_count(self):
        return self.table_count + self.masked_view_count


def address_key(address):
    return f"{address:08x}"


def load_layout():
    return rolling_launch_layout.load_layout()


def _masked_view_entries(overrides):
    entries = overrides.get("masked_view", [])
    if isinstance(entries, dict):
        entries = [entries]
    if not isinstance(entries, list):
        raise ValueError("masked_view must be a table or an array of tables")
    return entries


def _enable_mask_model(address):
    return {
        "addr": address_key(address),
        "family": "direct-scalar",
        "dims": 1,
        "width": 1,
        "height": None,
        "storagetype": "uint8",
        "confidence": "code",
        "role": "table",
        "semantics": (
            "Rolling Launch per-map enable mask in the validated runtime "
            "configuration record"
        ),
        "units": "raw bit mask",
        "scale_expr": "x",
        "to_byte": "x",
        "scale_conf": "code",
        "note": (
            "Bits 0 through 4 enable Maps 1 through 5. The runtime rejects "
            "any set bit outside mask 0x1F and fails closed."
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


def _enable_mask_presentation():
    return {
        "name": "Rolling Launch Enable Mask (Raw)",
        "category": "Rolling Launch / Advanced",
        "order": 900000,
        "emit": True,
        "format": "0",
        "fine": 1,
        "coarse": 1,
        "static_axis_name": "Configuration",
        "static_axis": ["Enable mask"],
    }


def _enable_views(address):
    source = address_key(address)
    return [
        {
            "source": source,
            "name": f"Map {slot} - Rolling Launch Enable",
            "category": "Rolling Launch / Map Enable",
            "mask": f"{1 << (slot - 1):02X}",
            "units": "Enabled (0: Off | 1: On)",
            "expression": "x",
            "to_byte": "x",
            "format": "0",
            "fine": 1,
            "coarse": 1,
        }
        for slot in range(1, contract.SLOT_COUNT + 1)
    ]


def project_definition_model(maps, overrides, layout=None):
    """Add per-map Rolling Launch enable controls to a definition model."""
    layout = layout or load_layout()
    projected_maps = deepcopy(maps)
    projected_overrides = deepcopy(overrides)
    table_overrides = projected_overrides.get("table")
    if not isinstance(table_overrides, dict):
        raise ValueError("definition overrides must contain a table mapping")

    configuration_address = layout.configuration.start
    enable_mask_address = configuration_address + 4
    enable_key = address_key(enable_mask_address)
    if enable_key in projected_maps or enable_key in table_overrides:
        raise ValueError(
            f"Rolling Launch enable-mask address {enable_key} collides"
        )

    projected_maps[enable_key] = _enable_mask_model(enable_mask_address)
    table_overrides[enable_key] = _enable_mask_presentation()

    existing_views = _masked_view_entries(projected_overrides)
    projected_overrides["masked_view"] = (
        deepcopy(existing_views) + _enable_views(enable_mask_address)
    )

    projection = DefinitionProjection(
        maps=projected_maps,
        overrides=projected_overrides,
        configuration_address=address_key(configuration_address),
        enable_mask_address=enable_key,
        table_count=1,
        masked_view_count=contract.SLOT_COUNT,
    )
    validate_projection(projection, maps, overrides, layout)
    return projection


def validate_projection(projection, source_maps, source_overrides, layout=None):
    """Validate the synthetic address, five independent bits, and preservation."""
    layout = layout or load_layout()
    expected_configuration = address_key(layout.configuration.start)
    expected_enable = address_key(layout.configuration.start + 4)
    if projection.configuration_address != expected_configuration:
        raise ValueError("Rolling Launch configuration address differs")
    if projection.enable_mask_address != expected_enable:
        raise ValueError("Rolling Launch enable-mask address differs")
    if projection.table_count != 1:
        raise ValueError("Rolling Launch projection must contain one source table")
    if projection.masked_view_count != contract.SLOT_COUNT:
        raise ValueError("Rolling Launch projection must contain five map views")

    if projection.maps.get(expected_enable) != _enable_mask_model(
        layout.configuration.start + 4
    ):
        raise ValueError("Rolling Launch enable-mask model differs")
    if projection.overrides["table"].get(
        expected_enable
    ) != _enable_mask_presentation():
        raise ValueError("Rolling Launch enable-mask presentation differs")

    projected_views = [
        view
        for view in _masked_view_entries(projection.overrides)
        if str(view.get("source", "")).lower() == expected_enable
    ]
    expected_views = _enable_views(layout.configuration.start + 4)
    if projected_views != expected_views:
        raise ValueError("Rolling Launch per-map enable views differ")
    if {int(view["mask"], 16) for view in projected_views} != {
        1 << index for index in range(contract.SLOT_COUNT)
    }:
        raise ValueError("Rolling Launch map-enable masks overlap or differ")

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
