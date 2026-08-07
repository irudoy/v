"""Definition projection for the JK08A Rolling Launch configuration.

The runtime stores its tuner-facing activation thresholds, RPM hold values,
bounded-retard ramp width, pedal requirement, and one enable bit per map in a
validated 32-byte record. This module projects those fields into the common
JK08A RomRaider and TunerPro models. It does not write definitions or ROM
images.
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
    coolant_min_address: str
    min_speed_address: str
    retard_ramp_address: str
    min_rpm_address: str
    pedal_requirement_address: str
    rpm_offset_address: str
    hysteresis_address: str
    table_count: int
    masked_view_count: int
    switch_count: int
    bitwise_switch_count: int
    enable_bit_count: int

    @property
    def editor_view_count(self):
        return (
            self.table_count
            + self.switch_count
            + self.bitwise_switch_count
        )


def address_key(address):
    return f"{address:08x}"


def load_layout():
    return rolling_launch_layout.load_layout()


def _override_entries(overrides, key):
    entries = overrides.get(key, [])
    if isinstance(entries, dict):
        entries = [entries]
    if not isinstance(entries, list):
        raise ValueError(f"{key} must be a table or an array of tables")
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


def _pedal_requirement_switch(address):
    return {
        "name": "Rolling Launch Require Accelerator Pedal",
        "category": "Rolling Launch / Activation",
        "storageaddress": f"0x{address:X}",
        "storagetype": "uint8",
        "sizey": "2",
        "endian": "big",
        "userlevel": "5",
        "description": (
            "Exact JK08A. Enabled writes min_pedal=1 and requires a nonzero "
            "normalized accelerator-pedal signal for activation. Disabled "
            "writes min_pedal=0, which makes the pedal gate unconditional. "
            "The signal is not presented as a calibrated pedal percentage."
        ),
        "state": [
            {"name": "Enabled", "data": "00 01"},
            {"name": "Disabled", "data": "00 00"},
        ],
    }


def _scalar_model(
    address,
    *,
    storagetype,
    semantics,
    units,
    scale_expr,
    to_byte,
    scale_conf,
    note,
):
    return {
        "addr": address_key(address),
        "family": "direct-scalar",
        "dims": 1,
        "width": 1,
        "height": None,
        "storagetype": storagetype,
        "confidence": "code",
        "role": "table",
        "semantics": semantics,
        "units": units,
        "scale_expr": scale_expr,
        "to_byte": to_byte,
        "scale_conf": scale_conf,
        "note": note,
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


def _scalar_presentation(
    name,
    category,
    order,
    axis_label,
    *,
    fmt="0.0",
    fine=None,
    coarse=None,
):
    return {
        "name": name,
        "category": category,
        "order": order,
        "emit": True,
        "format": fmt,
        "fine": fine,
        "coarse": coarse,
        "static_axis_name": "Configuration",
        "static_axis": [axis_label],
    }


def _configuration_tables(configuration_address):
    coolant_min = configuration_address + 0x06
    min_speed = configuration_address + 0x08
    retard_ramp = configuration_address + 0x09
    min_rpm = configuration_address + 0x0A
    rpm_offset = configuration_address + 0x0E
    hysteresis = configuration_address + 0x10
    return (
        (
            coolant_min,
            _scalar_model(
                coolant_min,
                storagetype="uint8",
                semantics=(
                    "Minimum normalized engine-coolant temperature required "
                    "for Rolling Launch activation"
                ),
                units="deg C",
                scale_expr="x*0.625-40",
                to_byte="(x+40)/0.625",
                scale_conf="code",
                note=(
                    "The runtime compares the normalized coolant index at "
                    "0xFFFF1077 against this inclusive minimum. The index "
                    "maps 0, 16, ..., 240 to -40, -30, ..., 110 deg C; "
                    "255 is the saturated hot endpoint."
                ),
            ),
            _scalar_presentation(
                "Rolling Launch Minimum Coolant Temperature",
                "Rolling Launch / Activation",
                900010,
                "Minimum coolant temperature",
                fine=0.625,
                coarse=10,
            ),
        ),
        (
            min_speed,
            _scalar_model(
                min_speed,
                storagetype="uint8",
                semantics=(
                    "Minimum coarse vehicle speed required for Rolling "
                    "Launch activation"
                ),
                units="km/h",
                scale_expr="x*2",
                to_byte="x/2",
                scale_conf="candidate",
                note=(
                    "The exact firmware chain produces the byte at "
                    "0xFFFF110E. Its approximately 2 km/h per count physical "
                    "scale depends on homologous observed CAN 0x280 data; "
                    "zero-speed semantics are exact."
                ),
            ),
            _scalar_presentation(
                "Rolling Launch Minimum Vehicle Speed",
                "Rolling Launch / Activation",
                900020,
                "Minimum vehicle speed",
                fine=2,
                coarse=10,
            ),
        ),
        (
            retard_ramp,
            _scalar_model(
                retard_ramp,
                storagetype="uint8",
                semantics=(
                    "Rolling Launch ignition-retard ramp width below the "
                    "captured fuel-cut threshold"
                ),
                units="RPM",
                scale_expr="x*12.5",
                to_byte="x/12.5",
                scale_conf="code",
                note=(
                    "Mode 2 keeps the stock ignition command at or below "
                    "max(captured_rpm, Cut - retard_ramp), blends linearly "
                    "toward the per-map late-command cap inside the band, "
                    "and applies the cap at Cut. The validated record "
                    "requires hysteresis < retard_ramp <= rpm_offset."
                ),
            ),
            _scalar_presentation(
                "Rolling Launch Retard Ramp Width",
                "Rolling Launch / Ignition Retard",
                900035,
                "Retard ramp width",
                fine=12.5,
                coarse=100,
            ),
        ),
        (
            min_rpm,
            _scalar_model(
                min_rpm,
                storagetype="uint16",
                semantics=(
                    "Minimum engine speed required for Rolling Launch "
                    "activation"
                ),
                units="RPM",
                scale_expr="x*12.5",
                to_byte="x/12.5",
                scale_conf="code",
                note=(
                    "The runtime compares the native RPM/12.5 word at "
                    "0xFFFF11BC against this inclusive minimum."
                ),
            ),
            _scalar_presentation(
                "Rolling Launch Minimum Engine Speed",
                "Rolling Launch / Activation",
                900030,
                "Minimum engine speed",
                fine=12.5,
                coarse=100,
            ),
        ),
        (
            rpm_offset,
            _scalar_model(
                rpm_offset,
                storagetype="uint16",
                semantics=(
                    "Rolling Launch fuel-cut threshold offset above captured "
                    "activation RPM"
                ),
                units="RPM",
                scale_expr="x*12.5",
                to_byte="x/12.5",
                scale_conf="code",
                note=(
                    "The runtime computes Cut = saturate_u16(captured_rpm + "
                    "rpm_offset). The value must be nonzero."
                ),
            ),
            _scalar_presentation(
                "Rolling Launch RPM Offset",
                "Rolling Launch / RPM Hold",
                900040,
                "RPM offset",
                fine=12.5,
                coarse=100,
            ),
        ),
        (
            hysteresis,
            _scalar_model(
                hysteresis,
                storagetype="uint16",
                semantics=(
                    "Rolling Launch fuel-cut restore hysteresis in the "
                    "validated runtime configuration record"
                ),
                units="RPM",
                scale_expr="x*12.5",
                to_byte="x/12.5",
                scale_conf="code",
                note=(
                    "The runtime computes Restore = Cut - hysteresis, accepts "
                    "only 0 < hysteresis_native < min_rpm_native and "
                    "hysteresis_native < retard_ramp_native, and rejects the "
                    "entire configuration otherwise. The default value is 8 "
                    "native counts, or 100 RPM."
                ),
            ),
            _scalar_presentation(
                "Rolling Launch RPM Hysteresis",
                "Rolling Launch / RPM Hold",
                900050,
                "Hysteresis",
                fine=12.5,
                coarse=100,
            ),
        ),
    )


def project_definition_model(maps, overrides, layout=None):
    """Add validated Rolling Launch controls to a definition model."""
    layout = layout or load_layout()
    projected_maps = deepcopy(maps)
    projected_overrides = deepcopy(overrides)
    table_overrides = projected_overrides.get("table")
    if not isinstance(table_overrides, dict):
        raise ValueError("definition overrides must contain a table mapping")

    configuration_address = layout.configuration.start
    enable_mask_address = configuration_address + 0x04
    pedal_requirement_address = configuration_address + 0x0C
    tables = _configuration_tables(configuration_address)

    for address in (enable_mask_address, pedal_requirement_address):
        key = address_key(address)
        if key in projected_maps or key in table_overrides:
            raise ValueError(
                f"Rolling Launch control address {key} collides"
            )

    for address, model, presentation in tables:
        key = address_key(address)
        if key in projected_maps or key in table_overrides:
            raise ValueError(
                f"Rolling Launch calibration address {key} collides"
            )
        projected_maps[key] = model
        table_overrides[key] = presentation

    bitwise_switches = _override_entries(
        projected_overrides, "bitwise_switch"
    )
    if any(
        int(str(entry.get("storageaddress", "-1")), 0)
        == enable_mask_address
        for entry in bitwise_switches
    ):
        raise ValueError(
            "Rolling Launch enable-switch address "
            f"{address_key(enable_mask_address)} collides"
        )
    projected_overrides["bitwise_switch"] = (
        deepcopy(bitwise_switches) + [_enable_switch(enable_mask_address)]
    )

    switches = _override_entries(projected_overrides, "switch")
    if any(
        int(str(entry.get("storageaddress", "-1")), 0)
        == pedal_requirement_address
        for entry in switches
    ):
        raise ValueError(
            "Rolling Launch pedal-switch address "
            f"{address_key(pedal_requirement_address)} collides"
        )
    projected_overrides["switch"] = (
        deepcopy(switches)
        + [_pedal_requirement_switch(pedal_requirement_address)]
    )

    projection = DefinitionProjection(
        maps=projected_maps,
        overrides=projected_overrides,
        configuration_address=address_key(configuration_address),
        enable_mask_address=address_key(enable_mask_address),
        coolant_min_address=address_key(configuration_address + 0x06),
        min_speed_address=address_key(configuration_address + 0x08),
        retard_ramp_address=address_key(configuration_address + 0x09),
        min_rpm_address=address_key(configuration_address + 0x0A),
        pedal_requirement_address=address_key(pedal_requirement_address),
        rpm_offset_address=address_key(configuration_address + 0x0E),
        hysteresis_address=address_key(configuration_address + 0x10),
        table_count=len(tables),
        masked_view_count=0,
        switch_count=1,
        bitwise_switch_count=1,
        enable_bit_count=contract.SLOT_COUNT,
    )
    validate_projection(projection, maps, overrides, layout)
    return projection


def validate_projection(projection, source_maps, source_overrides, layout=None):
    """Validate controls, independent enable bits, and source preservation."""
    layout = layout or load_layout()
    configuration_address = layout.configuration.start
    expected_addresses = {
        "configuration_address": configuration_address,
        "enable_mask_address": configuration_address + 0x04,
        "coolant_min_address": configuration_address + 0x06,
        "min_speed_address": configuration_address + 0x08,
        "retard_ramp_address": configuration_address + 0x09,
        "min_rpm_address": configuration_address + 0x0A,
        "pedal_requirement_address": configuration_address + 0x0C,
        "rpm_offset_address": configuration_address + 0x0E,
        "hysteresis_address": configuration_address + 0x10,
    }
    for field, address in expected_addresses.items():
        if getattr(projection, field) != address_key(address):
            raise ValueError(f"Rolling Launch {field} differs")
    if projection.table_count != 6:
        raise ValueError(
            "Rolling Launch projection must contain six calibration tables"
        )
    if projection.masked_view_count != 0:
        raise ValueError("Rolling Launch projection must not contain masked views")
    if projection.switch_count != 1:
        raise ValueError(
            "Rolling Launch projection must contain one pedal switch"
        )
    if projection.bitwise_switch_count != 1:
        raise ValueError(
            "Rolling Launch projection must contain one bitwise switch"
        )
    if projection.enable_bit_count != contract.SLOT_COUNT:
        raise ValueError("Rolling Launch bitwise switch must contain five bits")
    if projection.enable_mask_address in projection.maps:
        raise ValueError("Rolling Launch raw enable-mask table is visible")
    if projection.pedal_requirement_address in projection.maps:
        raise ValueError("Rolling Launch raw pedal threshold table is visible")

    for address, model, presentation in _configuration_tables(
        configuration_address
    ):
        key = address_key(address)
        if projection.maps.get(key) != model:
            raise ValueError(
                f"Rolling Launch calibration model {key} differs"
            )
        if projection.overrides["table"].get(key) != presentation:
            raise ValueError(
                f"Rolling Launch calibration presentation {key} differs"
            )

    projected_bitwise = [
        entry
        for entry in _override_entries(
            projection.overrides, "bitwise_switch"
        )
        if int(str(entry.get("storageaddress", "-1")), 0)
        == configuration_address + 0x04
    ]
    if projected_bitwise != [_enable_switch(configuration_address + 0x04)]:
        raise ValueError("Rolling Launch per-map bitwise switch differs")
    positions = [bit["position"] for bit in projected_bitwise[0]["bit"]]
    if positions != list(range(contract.SLOT_COUNT)):
        raise ValueError("Rolling Launch enable-bit positions differ")

    projected_pedal = [
        entry
        for entry in _override_entries(projection.overrides, "switch")
        if int(str(entry.get("storageaddress", "-1")), 0)
        == configuration_address + 0x0C
    ]
    if projected_pedal != [
        _pedal_requirement_switch(configuration_address + 0x0C)
    ]:
        raise ValueError("Rolling Launch pedal switch differs")

    for address, model in source_maps.items():
        if projection.maps.get(address) != model:
            raise ValueError(
                f"source map {address} changed during Rolling Launch projection"
            )
    for address, presentation in source_overrides.get("table", {}).items():
        if projection.overrides["table"].get(address) != presentation:
            raise ValueError(
                "source presentation "
                f"{address} changed during Rolling Launch projection"
            )
    return projection
