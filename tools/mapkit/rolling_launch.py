"""Definition projection for the exact-family Rolling Launch configuration.

The runtime stores its head controls and five map slots in a validated schema-5
record. This module projects the head and logical slot fields into paired
editor models backed by the canonical executable layout. The derived slot
efficiency stays hidden and is refreshed from F after editing. The signed
target-speed offset, coolant maximum, and run and rearm periods stay in the
build profile. This module does not write definitions or ROM images.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import struct

from patches import rolling_launch as contract
from patches import rolling_launch_layout


ENABLE_MASK_OFFSET = 0x04
PEDAL_REQUIREMENT_OFFSET = 0x0E


@dataclass(frozen=True)
class Control:
    key: str
    offset: int
    storagetype: str
    semantics: str
    units: str
    scale_expr: str
    to_byte: str
    note: str
    name: str
    category: str
    order: int
    axis_label: str
    fmt: str
    fine: float
    coarse: float


SPEED_NOTE = (
    "The runtime reads the vehicle-speed word 0xFFFF113C, km/h*10 by the "
    "firmware chain of CAN 0x284."
)
CONTROLS = (
    Control(
        "coolant_min", 0x06, "uint8",
        "Minimum normalized engine-coolant temperature required for Rolling "
        "Launch activation",
        "deg C", "x*0.625-40", "(x+40)/0.625",
        "The runtime compares the normalized coolant index at 0xFFFF1077 "
        "against this inclusive minimum. The index maps 0, 16, ..., 240 to "
        "-40, -30, ..., 110 deg C; 255 is the saturated hot endpoint.",
        "Rolling Launch Minimum Coolant Temperature",
        "Rolling Launch / Activation", 900010, "Minimum coolant temperature",
        "0.0", 0.625, 10,
    ),
    Control(
        "min_speed", 0x08, "uint16",
        "Minimum vehicle speed required for Rolling Launch activation; zero "
        "disables this bound",
        "km/h", "x/10", "x*10",
        SPEED_NOTE + " Activation requires the word at or above this "
        "inclusive bound.",
        "Rolling Launch Minimum Vehicle Speed",
        "Rolling Launch / Activation", 900020, "Minimum vehicle speed",
        "0.0", 0.1, 1,
    ),
    Control(
        "max_speed", 0x0A, "uint16",
        "Maximum vehicle speed allowed for Rolling Launch activation; zero "
        "disables this bound",
        "km/h", "x/10", "x*10",
        SPEED_NOTE + " Activation requires the word at or below this "
        "inclusive bound; two nonzero bounds must be ordered.",
        "Rolling Launch Maximum Vehicle Speed",
        "Rolling Launch / Activation", 900021, "Maximum vehicle speed",
        "0.0", 0.1, 1,
    ),
    Control(
        "min_rpm_native", 0x0C, "uint16",
        "Minimum engine speed required for Rolling Launch activation",
        "RPM", "x*12.5", "x/12.5",
        "The runtime compares the native RPM/12.5 word at 0xFFFF11BC against "
        "this inclusive minimum.",
        "Rolling Launch Minimum Engine Speed",
        "Rolling Launch / Activation", 900030, "Minimum engine speed",
        "0", 12.5, 100,
    ),
    Control(
        "speed_frame_age_limit", 0x22, "uint8",
        "Maximum receive age of the vehicle-speed frame for Rolling Launch",
        "ms", "x*10.24", "x/10.24",
        "The stock receive age 0xFFFF3B38 of CAN 0x284 advances once per "
        "10.24 ms pass without a processed frame and saturates at 255; a "
        "20 ms frame keeps it at 0..2 counts. Activation and every ACTIVE "
        "pass require the age at or below this limit; the value must lie in "
        "1..254 counts.",
        "Rolling Launch Speed Frame Age Limit",
        "Rolling Launch / Activation", 900040, "Speed frame age limit",
        "0.00", 10.24, 102.4,
    ),
    Control(
        "window_width", 0x12, "uint8",
        "Speed-error width over which the Rolling Launch torque fraction "
        "falls from full to zero",
        "km/h", "x/10", "x*10",
        "With e = speed - target, the proportional fraction is "
        "clamp((window_top - e) * 1000 / width, 0, 1000) thousandths. The "
        "width must be nonzero.",
        "Rolling Launch Speed Window Width",
        "Rolling Launch / Speed Hold", 900110, "Speed window width",
        "0.0", 0.1, 1,
    ),
    Control(
        "window_top", 0x13, "uint8",
        "Speed error at which the Rolling Launch proportional torque "
        "fraction reaches zero",
        "km/h", "x/10", "x*10",
        "The proportional fraction is full at e <= window_top - width and "
        "zero at e >= window_top.",
        "Rolling Launch Speed Window Top",
        "Rolling Launch / Speed Hold", 900111, "Speed window top",
        "0.0", 0.1, 1,
    ),
    Control(
        "u_rate_limit", 0x14, "uint16",
        "Largest change of the Rolling Launch torque fraction per scheduler "
        "pass",
        "%", "x/10", "x*10",
        "The torque fraction moves toward the controller command by at most "
        "this many thousandths per 10.24 ms pass; the value must lie in "
        "1..1000.",
        "Rolling Launch Torque Fraction Rate Limit",
        "Rolling Launch / Speed Hold", 900120, "Rate limit per pass",
        "0.0", 0.1, 1,
    ),
    Control(
        "integrator_limit", 0x18, "uint16",
        "Magnitude limit of the Rolling Launch speed integrator",
        "%", "x/10", "x*10",
        "The integrator contribution stays within plus or minus this many "
        "thousandths of the torque fraction; the value must not exceed 1000.",
        "Rolling Launch Integrator Limit",
        "Rolling Launch / Speed Hold", 900131, "Integrator limit",
        "0.0", 0.1, 1,
    ),
    Control(
        "abort_above", 0x1A, "uint8",
        "Speed error above the target that ends a Rolling Launch run",
        "km/h", "x/10", "x*10",
        "An ACTIVE pass with e above this nonzero bound aborts with "
        "SPEED_ABOVE_WINDOW.",
        "Rolling Launch Abort Above Target",
        "Rolling Launch / Speed Hold", 900140, "Abort above target",
        "0.0", 0.1, 1,
    ),
    Control(
        "abort_below", 0x1B, "uint8",
        "Speed error below the target that ends a Rolling Launch run",
        "km/h", "x/10", "x*10",
        "An ACTIVE pass with e below the negative of this nonzero bound "
        "aborts with SPEED_BELOW_WINDOW.",
        "Rolling Launch Abort Below Target",
        "Rolling Launch / Speed Hold", 900141, "Abort below target",
        "0.0", 0.1, 1,
    ),
    Control(
        "rpm_ceiling_offset_native", 0x1C, "uint16",
        "Rolling Launch RPM ceiling above the captured activation RPM",
        "RPM", "x*12.5", "x/12.5",
        "Hold mode latches the all-cylinder fuel-cut request when RPM "
        "exceeds the captured RPM plus this nonzero offset.",
        "Rolling Launch RPM Ceiling Offset",
        "Rolling Launch / RPM Ceiling", 900210, "RPM ceiling offset",
        "0", 12.5, 100,
    ),
    Control(
        "rpm_ceiling_hysteresis_native", 0x23, "uint8",
        "Rolling Launch RPM ceiling hysteresis below the cut threshold",
        "RPM", "x*12.5", "x/12.5",
        "A latched ceiling request holds while RPM exceeds the cut threshold "
        "minus this hysteresis and releases at or below it. The value must "
        "be nonzero and must not exceed the ceiling offset.",
        "Rolling Launch RPM Ceiling Hysteresis",
        "Rolling Launch / RPM Ceiling", 900211, "RPM ceiling hysteresis",
        "0", 12.5, 100,
    ),
)

TRIM_REFRESH_TOOL = "patches/refresh_rolling_launch.py"


def _slot_controls():
    controls = []
    for index in range(contract.SLOT_COUNT):
        offset = contract.SLOT_OFFSET + index * struct.calcsize(contract.SLOT_FORMAT)
        category = f"Rolling Launch / Map {index + 1}"
        fields = (
            ("integral_gain", 0, "uint16", "Integral Gain", "raw", "x", "x",
             "Integral gain Ki, 0..32767. Each active pass adds -Ki * speed "
             "error to the Q4 integrator before its limit and anti-windup gates."),
            ("max_trim", 2, "uint8", "Maximum Trim", "deg", "x", "x",
             "Maximum retard trim, 0..40 degrees. After editing this value or "
             "the F table, refresh the hidden efficiency with " + TRIM_REFRESH_TOOL +
             " as documented in patches/rolling-launch.md. The command uses F "
             "of the edited image; preflash rejects an inconsistent efficiency."),
            ("floor_command", 3, "uint8", "Timing Floor", "deg ATDC", "x-110", "x+110",
             "Latest ignition command of the trim. Timing is 110 - command "
             "degrees BTDC, so the editor shows command - 110 degrees ATDC. "
             "Negative ATDC values are before TDC. Ignored when trim is zero."),
        )
        for order, (key, relative, storage, label, units, expr, inverse, note) in enumerate(fields):
            controls.append(Control(
                f"map_{index + 1}_{key}", offset + relative, storage,
                f"Map {index + 1} Rolling Launch {label.lower()}", units, expr, inverse,
                note, f"Rolling Launch Map {index + 1} {label}", category,
                900300 + index * 10 + order, label, "0", 1, 5,
            ))
    return tuple(controls)


SLOT_CONTROLS = _slot_controls()
ALL_CONTROLS = CONTROLS + SLOT_CONTROLS


@dataclass(frozen=True)
class DefinitionProjection:
    maps: dict
    overrides: dict
    configuration_address: str
    enable_mask_address: str
    pedal_requirement_address: str
    control_addresses: tuple[tuple[str, str], ...]
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

    def address(self, key):
        return dict(self.control_addresses)[key]


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


def _enable_switch(address, rom="JK08A"):
    return {
        "name": "Rolling Launch Enable by Map",
        "category": "Rolling Launch / Map Enable",
        "storageaddress": f"0x{address:X}",
        "storagetype": "uint8",
        "endian": "big",
        "userlevel": "5",
        "description": (
            f"Exact {rom}. Each checkbox independently enables Rolling Launch "
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


def _pedal_requirement_switch(address, rom="JK08A"):
    return {
        "name": "Rolling Launch Require Accelerator Pedal",
        "category": "Rolling Launch / Activation",
        "storageaddress": f"0x{address:X}",
        "storagetype": "uint8",
        "sizey": "2",
        "endian": "big",
        "userlevel": "5",
        "description": (
            f"Exact {rom}. Enabled writes min_pedal=1 and requires a nonzero "
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
    return tuple(
        (
            configuration_address + control.offset,
            _scalar_model(
                configuration_address + control.offset,
                storagetype=control.storagetype,
                semantics=control.semantics,
                units=control.units,
                scale_expr=control.scale_expr,
                to_byte=control.to_byte,
                scale_conf="code",
                note=control.note,
            ),
            _scalar_presentation(
                control.name,
                control.category,
                control.order,
                control.axis_label,
                fmt=control.fmt,
                fine=control.fine,
                coarse=control.coarse,
            ),
        )
        for control in ALL_CONTROLS
    )


def project_definition_model(maps, overrides, layout=None, target_rom=None):
    """Add validated Rolling Launch controls to a definition model."""
    layout = layout or load_layout()
    target_rom = target_rom or layout.rom
    projected_maps = deepcopy(maps)
    projected_overrides = deepcopy(overrides)
    table_overrides = projected_overrides.get("table")
    if not isinstance(table_overrides, dict):
        raise ValueError("definition overrides must contain a table mapping")

    configuration_address = layout.configuration.start
    enable_mask_address = configuration_address + ENABLE_MASK_OFFSET
    pedal_requirement_address = (
        configuration_address + PEDAL_REQUIREMENT_OFFSET
    )
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
        deepcopy(bitwise_switches)
        + [_enable_switch(enable_mask_address, target_rom)]
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
        + [_pedal_requirement_switch(pedal_requirement_address, target_rom)]
    )

    projection = DefinitionProjection(
        maps=projected_maps,
        overrides=projected_overrides,
        configuration_address=address_key(configuration_address),
        enable_mask_address=address_key(enable_mask_address),
        pedal_requirement_address=address_key(pedal_requirement_address),
        control_addresses=tuple(
            (control.key, address_key(configuration_address + control.offset))
            for control in ALL_CONTROLS
        ),
        table_count=len(tables),
        masked_view_count=0,
        switch_count=1,
        bitwise_switch_count=1,
        enable_bit_count=contract.SLOT_COUNT,
    )
    validate_projection(
        projection,
        maps,
        overrides,
        layout,
        target_rom=target_rom,
    )
    return projection


def validate_projection(
    projection,
    source_maps,
    source_overrides,
    layout=None,
    target_rom=None,
):
    """Validate controls, independent enable bits, and source preservation."""
    layout = layout or load_layout()
    target_rom = target_rom or layout.rom
    configuration_address = layout.configuration.start
    enable_mask_address = configuration_address + ENABLE_MASK_OFFSET
    pedal_requirement_address = (
        configuration_address + PEDAL_REQUIREMENT_OFFSET
    )
    expected_addresses = {
        "configuration_address": configuration_address,
        "enable_mask_address": enable_mask_address,
        "pedal_requirement_address": pedal_requirement_address,
    }
    for field, address in expected_addresses.items():
        if getattr(projection, field) != address_key(address):
            raise ValueError(f"Rolling Launch {field} differs")
    if projection.control_addresses != tuple(
        (control.key, address_key(configuration_address + control.offset))
        for control in ALL_CONTROLS
    ):
        raise ValueError("Rolling Launch control addresses differ")
    if projection.table_count != len(ALL_CONTROLS):
        raise ValueError(
            "Rolling Launch projection must contain one table per control"
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
        == enable_mask_address
    ]
    if projected_bitwise != [_enable_switch(enable_mask_address, target_rom)]:
        raise ValueError("Rolling Launch per-map bitwise switch differs")
    positions = [bit["position"] for bit in projected_bitwise[0]["bit"]]
    if positions != list(range(contract.SLOT_COUNT)):
        raise ValueError("Rolling Launch enable-bit positions differ")

    projected_pedal = [
        entry
        for entry in _override_entries(projection.overrides, "switch")
        if int(str(entry.get("storageaddress", "-1")), 0)
        == pedal_requirement_address
    ]
    if projected_pedal != [
        _pedal_requirement_switch(pedal_requirement_address, target_rom)
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
