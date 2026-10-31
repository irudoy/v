"""Classify the runtime layers of an image built from a registered stock image.

An image carries no runtime, the current builder runtime, or a registered
historical Rolling Launch endpoint under an optional current or registered
historical CAN telemetry layer. Each signature names the ROMs it describes, and
classification considers only the signatures of the selected ROM. Partial,
unknown, or mixed layers are rejected with a named reason.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import struct

from patches import can_telemetry
from patches import can_telemetry_history
from patches import jk08a_checksums as canonical_checksums
from patches import map_switching_compose
from patches import rolling_launch
from patches import rom_checksums
from patches import runtime_targets


class EndpointError(ValueError):
    """Raised when an image holds a partial or unknown runtime state."""


def sha256(data):
    return hashlib.sha256(bytes(data)).hexdigest()


@dataclass(frozen=True)
class RollingEndpointSignature:
    key: str
    roms: tuple[str, ...]
    configuration_schema_version: int
    unit_sha256: tuple[tuple[str, str], ...]
    hook_values: tuple[tuple[str, int], ...]
    carries_current_telemetry: bool = False


PRE_FEEDBACK_ROLLING_HOOK_VALUES = (
    ("displaced_periodic_task", 0x000D3860),
    ("selector_arbitration", 0x000D3880),
    ("startup_state_clear", 0x000D38A0),
    ("primary_ignition_command", 0x000D3EA0),
    ("feedback_arbitration", 0x000D35E0),
)
CURRENT_ROLLING_HOOK_VALUES = (
    ("displaced_periodic_task", 0x000D3860),
    ("selector_arbitration", 0x000D3880),
    ("startup_state_clear", 0x000D38A0),
    ("primary_ignition_command", 0x000D3EA0),
    ("feedback_arbitration", 0x000D41E0),
)
ERASED_FEEDBACK_ARBITER_SHA256 = (
    "0052516839b94ee314a4e3b398c8036de3790d672194987a394ee60323848539"
)


# Exact code fingerprints of registered historical Rolling Launch endpoints.
# Each signature names the ROMs whose layout it describes. Configuration bytes
# remain calibration-specific and are validated against the record contract.
HISTORICAL_ROLLING_ENDPOINTS = (
    RollingEndpointSignature(
        key="schema-1-bandless",
        roms=runtime_targets.EXACT_ROMS,
        configuration_schema_version=1,
        unit_sha256=(
            (
                "wrappers",
                "7e650ae06bbfdd33f9da9b99488de8202de64160440bced19719a07c74881e45",
            ),
            (
                "engine",
                "599c859dffe2f2b88eefa0c2add63ceecf3232a08625b1acc2481bd9c4658673",
            ),
            (
                "ignition_adapter",
                "542aab5999c39903c6614daa4b44ca41a77fe37273ee57dc2c4390e53844311d",
            ),
            (
                "ignition_controller",
                "e9175db65a9789096ca9cb5524d3abc2107df03e3c9ba3af1aca628f9c5d3bd2",
            ),
            (
                "threshold_helper",
                "0052516839b94ee314a4e3b398c8036de3790d672194987a394ee60323848539",
            ),
            ("feedback_arbiter", ERASED_FEEDBACK_ARBITER_SHA256),
        ),
        hook_values=PRE_FEEDBACK_ROLLING_HOOK_VALUES,
    ),
    RollingEndpointSignature(
        key="schema-2-speed-required",
        roms=runtime_targets.EXACT_ROMS,
        configuration_schema_version=2,
        unit_sha256=(
            (
                "wrappers",
                "7e650ae06bbfdd33f9da9b99488de8202de64160440bced19719a07c74881e45",
            ),
            (
                "engine",
                "6fbe61494983b09c45565b02409f1d768c1633cbe3c088d6e378d10c0ed9d3c6",
            ),
            (
                "ignition_adapter",
                "82452974b158d34cc8d7c69b990f327428ff01f92e047c6a15cb2f9251e90952",
            ),
            (
                "ignition_controller",
                "465b6e90325fa6aecffa94eeffa40b9c7b65f5095ed4bf768e52ee55f1407e3c",
            ),
            (
                "threshold_helper",
                "0052516839b94ee314a4e3b398c8036de3790d672194987a394ee60323848539",
            ),
            ("feedback_arbiter", ERASED_FEEDBACK_ARBITER_SHA256),
        ),
        hook_values=PRE_FEEDBACK_ROLLING_HOOK_VALUES,
    ),
    RollingEndpointSignature(
        key="schema-2-zero-speed",
        roms=runtime_targets.EXACT_ROMS,
        configuration_schema_version=2,
        unit_sha256=(
            (
                "wrappers",
                "7e650ae06bbfdd33f9da9b99488de8202de64160440bced19719a07c74881e45",
            ),
            (
                "engine",
                "e7e940b866526ea9feeab044f072fdee1ce157de600dd61482fbbe2905203661",
            ),
            (
                "ignition_adapter",
                "82452974b158d34cc8d7c69b990f327428ff01f92e047c6a15cb2f9251e90952",
            ),
            (
                "ignition_controller",
                "465b6e90325fa6aecffa94eeffa40b9c7b65f5095ed4bf768e52ee55f1407e3c",
            ),
            (
                "threshold_helper",
                "0052516839b94ee314a4e3b398c8036de3790d672194987a394ee60323848539",
            ),
            ("feedback_arbiter", ERASED_FEEDBACK_ARBITER_SHA256),
        ),
        hook_values=PRE_FEEDBACK_ROLLING_HOOK_VALUES,
    ),
    RollingEndpointSignature(
        key="schema-3-pre-feedback-indicators",
        roms=runtime_targets.EXACT_ROMS,
        configuration_schema_version=3,
        unit_sha256=(
            (
                "wrappers",
                "7e650ae06bbfdd33f9da9b99488de8202de64160440bced19719a07c74881e45",
            ),
            (
                "engine",
                "6420e4f75b36a1ac86691f2d16952c235862db62b57d297a51b8efc0f3379729",
            ),
            (
                "ignition_adapter",
                "ed76618204bb4f3838f806e090d45882409ad1fb0aa9462ae91d531806d9ca7b",
            ),
            (
                "ignition_controller",
                "ebb3cbeb3464ac3f53c6e8738a9b4f1fe729965fa7e24bccc0a5d790038b57f7",
            ),
            (
                "threshold_helper",
                "c1ab086bc1930c841e96be4cae34126af95e44821a03c2c177c33761a6336af7",
            ),
            ("feedback_arbiter", ERASED_FEEDBACK_ARBITER_SHA256),
        ),
        hook_values=PRE_FEEDBACK_ROLLING_HOOK_VALUES,
    ),
    # The arbiter of this endpoint emits ASCD state 6 for a failed held attempt
    # and state 7 for ACTIVE. It pairs that arbiter with the guarded ignition
    # controller and the schema-3 hooks. The CAN telemetry layer is compatible
    # with this complete registered lower endpoint.
    RollingEndpointSignature(
        key="schema-3-state-6-7-indicators",
        roms=runtime_targets.EXACT_ROMS,
        configuration_schema_version=3,
        unit_sha256=(
            (
                "wrappers",
                "7e650ae06bbfdd33f9da9b99488de8202de64160440bced19719a07c74881e45",
            ),
            (
                "engine",
                "6420e4f75b36a1ac86691f2d16952c235862db62b57d297a51b8efc0f3379729",
            ),
            (
                "ignition_adapter",
                "ed76618204bb4f3838f806e090d45882409ad1fb0aa9462ae91d531806d9ca7b",
            ),
            (
                "ignition_controller",
                "ebb3cbeb3464ac3f53c6e8738a9b4f1fe729965fa7e24bccc0a5d790038b57f7",
            ),
            (
                "threshold_helper",
                "c1ab086bc1930c841e96be4cae34126af95e44821a03c2c177c33761a6336af7",
            ),
            (
                "feedback_arbiter",
                "0ec18b26a0ef6556bcb5f6056a2a9b988f8c895f65ec6b2b3665352ce73fb4dc",
            ),
        ),
        hook_values=CURRENT_ROLLING_HOOK_VALUES,
        carries_current_telemetry=True,
    ),
    RollingEndpointSignature(
        key="schema-3-guarded-controller",
        roms=runtime_targets.EXACT_ROMS,
        configuration_schema_version=3,
        unit_sha256=(
            ("wrappers", "7e650ae06bbfdd33f9da9b99488de8202de64160440bced19719a07c74881e45"),
            ("engine", "6420e4f75b36a1ac86691f2d16952c235862db62b57d297a51b8efc0f3379729"),
            ("ignition_adapter", "ed76618204bb4f3838f806e090d45882409ad1fb0aa9462ae91d531806d9ca7b"),
            ("ignition_controller", "ebb3cbeb3464ac3f53c6e8738a9b4f1fe729965fa7e24bccc0a5d790038b57f7"),
            ("threshold_helper", "c1ab086bc1930c841e96be4cae34126af95e44821a03c2c177c33761a6336af7"),
            ("feedback_arbiter", "1e1a884eee649ec5cfea48af0c2129c8290628401d11118253c5265e965b0da6"),
        ),
        hook_values=CURRENT_ROLLING_HOOK_VALUES,
        carries_current_telemetry=True,
    ),
)
TELEMETRY_LOWER_ROLLING_STATES = frozenset(
    {"current"}
    | {
        endpoint.key
        for endpoint in HISTORICAL_ROLLING_ENDPOINTS
        if endpoint.carries_current_telemetry
    }
)

HISTORICAL_FEEDBACK_FRAME_COUNTS = ((10, 10), (15, 15))
# Exact JK08A engine fingerprints that emit ASCD state 6 during the ON phase:
# the partial 0x9F mask and the full 0x8F mask, each with 10/10, 15/15, and
# 30/30 phase counts.
HISTORICAL_FEEDBACK_ENGINE_SHA256 = frozenset(
    {
        "925a7ebc321e965bfed0fdfdc7e06287b6b794b0525226c4bd9a11187bc1f66f",
        "22c9c42f228cd827610a7e5ef848942e219e0461cbd2c9ba362ca8817130435f",
        "22c69075abb5f0c48207eb3c14a8c538f0fc17cf14f79951d55799186fc1a448",
        "0e0501f3d91e18a17c6a9bf7c4ebd187809c094fbf701f9d2864fd4792f9b32e",
        "017a1c01d0f2fba835a93714d1ce9e20a07e5ff709fc41ed997bf92e7124a13a",
        "d64600dd5be497cf49df077956e2ac86159b0366ecc485b33c5633e146b4e66a",
    }
)


def read_integer(data, address, width, byte_order="big"):
    return int.from_bytes(data[address : address + width], byte_order)


def _expected_pointer_table(layout, family):
    return b"".join(
        address.to_bytes(4, layout.byte_order)
        for address in family.all_slot_addresses
    )


def historical_configuration_fields(configuration, schema_version):
    """Return the named settings of a valid schema 1 or 2 Rolling Launch
    record, which the current profile schema cannot express."""
    if schema_version not in (1, 2) or not historical_configuration_is_valid(
        configuration, schema_version
    ):
        raise EndpointError(
            f"no valid schema {schema_version} Rolling Launch record"
        )
    values = struct.unpack(">H8B6H5sBHH", bytes(configuration))
    return {
        "mode": rolling_launch.Mode(values[2]).name.lower(),
        "enable_mask": values[3],
        "coolant_min": values[5],
        "coolant_max": values[6],
        "min_speed": values[7],
        ("speed_padding" if schema_version == 1 else "retard_ramp_native"): (
            values[8]
        ),
        "min_rpm_native": values[9],
        "min_pedal": values[10],
        "rpm_offset_native": values[11],
        "hysteresis_native": values[12],
        "run_timeout_ticks": values[13],
        "rearm_ticks": values[14],
        "target_commands": tuple(values[15]),
    }


def historical_configuration_is_valid(configuration, schema_version):
    if schema_version == rolling_launch.CONFIG_SCHEMA_VERSION:
        try:
            return rolling_launch.Calibration.from_bytes(
                configuration
            ).is_valid()
        except (TypeError, ValueError):
            return False
    if schema_version not in (1, 2):
        raise EndpointError(
            "internal historical Rolling Launch schema is unsupported"
        )
    try:
        values = struct.unpack(">H8B6H5sBHH", bytes(configuration))
        rolling_launch.Mode(values[2])
        options = rolling_launch.Option(values[4])
    except (TypeError, ValueError, struct.error):
        return False
    common = all((
        values[0] == rolling_launch.CONFIG_MAGIC,
        values[1] == schema_version,
        0 <= values[3] <= 0x1F,
        options == rolling_launch.Option.NONE,
        0 <= values[5] <= values[6] <= 0xFF,
        0 < values[9] <= 0xFFFF,
        0 <= values[10] <= 0xFFFF,
        0 < values[11] <= 0xFFFF,
        0 < values[12] < values[9],
        0 < values[13] <= 0x7FFF,
        0 < values[14] <= 0x7FFF,
        len(values[15]) == rolling_launch.SLOT_COUNT,
        all(110 <= value <= 117 for value in values[15]),
        values[16] == 0,
        values[17] == rolling_launch.CONFIG_MAGIC_INVERSE,
        values[18] == rolling_launch.CONFIG_END_MARKER,
    ))
    if schema_version == 1:
        return common and 0 < values[7] <= 0xFF and values[8] == 0
    return all((
        common,
        0 <= values[7] <= 0xFF,
        0 < values[8] <= 0xFF,
        values[12] < values[8] <= values[11],
    ))


def _endpoint_binding(endpoint, layout):
    """Return the hash and hook maps of a signature of the layout's ROM.

    A signature names unique units and hooks with lowercase SHA-256 text, and
    its units, hooks, and hook values describe the layout of every ROM that it
    names.
    """
    expected_hashes = dict(endpoint.unit_sha256)
    expected_hooks = dict(endpoint.hook_values)
    if (
        len(expected_hashes) != len(endpoint.unit_sha256)
        or len(expected_hooks) != len(endpoint.hook_values)
        or any(
            len(digest) != 64
            or any(
                character not in "0123456789abcdef"
                for character in digest
            )
            for digest in expected_hashes.values()
        )
    ):
        raise EndpointError(
            f"internal historical Rolling Launch endpoint "
            f"{endpoint.key!r} is invalid"
        )
    if (
        set(expected_hashes) != set(layout.assembly_unit_by_key)
        or set(expected_hooks) != set(layout.hook_by_key)
        or any(
            expected_hooks[hook.key] not in (hook.stock, hook.replacement)
            for hook in layout.hooks
        )
    ):
        raise EndpointError(
            f"internal historical Rolling Launch endpoint "
            f"{endpoint.key!r} does not describe the selected layout"
        )
    return expected_hashes, expected_hooks


def require_coherent_rolling_endpoint(
    source, layout, payloads, context, rom
):
    """Accept only an absent, current, or registered historical endpoint of
    the ROM."""
    expected_units = set(layout.assembly_unit_by_key)
    if set(payloads) != expected_units:
        raise EndpointError(
            "internal Rolling Launch payload set differs from the layout"
        )

    unit_bytes = {
        unit.key: source[unit.span.start : unit.span.end]
        for unit in layout.assembly_units
    }
    hook_values = {
        hook.key: read_integer(
            source, hook.address, hook.width, layout.byte_order
        )
        for hook in layout.hooks
    }
    did_values = {
        item.did: read_integer(
            source, item.pointer_address, 4, layout.byte_order
        )
        for item in layout.diagnostics
    }
    configuration = source[
        layout.configuration.start : layout.configuration.end
    ]

    claimed_erased = all(
        source[span.start : span.end] == bytes([0xFF]) * span.size
        for span in layout.claimed_rom_ranges
    )
    hooks_stock = all(
        hook_values[hook.key] == hook.stock for hook in layout.hooks
    )
    dids_stock = all(
        did_values[item.did] == item.stock for item in layout.diagnostics
    )
    if claimed_erased and hooks_stock and dids_stock:
        return "absent"

    hooks_current = all(
        hook_values[hook.key] == hook.replacement for hook in layout.hooks
    )
    dids_current = all(
        did_values[item.did] == item.target for item in layout.diagnostics
    )
    if hooks_current and dids_current:
        current_units = all(
            unit_bytes[unit.key] == payloads[unit.key]
            for unit in layout.assembly_units
        )
        try:
            current_configuration = rolling_launch.Calibration.from_bytes(
                configuration
            ).is_valid()
        except (TypeError, ValueError):
            current_configuration = False
        if current_units and current_configuration:
            return "current"

    if dids_current:
        actual_hashes = {
            key: sha256(value) for key, value in unit_bytes.items()
        }
        for endpoint in historical_endpoints(rom):
            expected_hashes, expected_hooks = _endpoint_binding(
                endpoint, layout
            )
            if (
                actual_hashes == expected_hashes
                and hook_values == expected_hooks
                and historical_configuration_is_valid(
                    configuration, endpoint.configuration_schema_version
                )
            ):
                return endpoint.key

    raise EndpointError(
        f"{context}: partial or unknown Rolling Launch state"
    )


def require_coherent_telemetry_endpoint(
    source, layout, payloads, context, launch_layout=None, rom=None
):
    """Accept an absent, current, or exactly registered historical endpoint."""
    expected_units = set(layout.assembly_unit_by_key)
    if set(payloads) != expected_units:
        raise EndpointError(
            "internal CAN telemetry payload set differs from the layout"
        )

    erased_units = all(
        source[unit.span.start : unit.span.end]
        == bytes([0xFF]) * unit.span.size
        for unit in layout.assembly_units
    )
    current_units = all(
        source[unit.span.start : unit.span.end] == payloads[unit.key]
        for unit in layout.assembly_units
    )
    configuration = source[
        layout.configuration.start : layout.configuration.end
    ]
    configuration_erased = (
        configuration == bytes([0xFF]) * layout.configuration.size
    )
    reserve_erased = (
        source[layout.reserved_rom.start : layout.reserved_rom.end]
        == bytes([0xFF]) * layout.reserved_rom.size
    )
    hook_values = {
        hook.key: read_integer(
            source, hook.address, hook.width, layout.byte_order
        )
        for hook in layout.hooks
    }
    lower_hook_values = {}
    if launch_layout is not None:
        lower_hook_values = {
            hook.address: hook.stock for hook in launch_layout.hooks
        }
    hooks_stock = all(
        hook_values[hook.key]
        in ({hook.stock} | (
            {lower_hook_values[hook.address]}
            if hook.address in lower_hook_values
            else set()
        ))
        for hook in layout.hooks
    )
    hooks_current = all(
        hook_values[hook.key] == hook.replacement for hook in layout.hooks
    )
    record_start = layout.mailbox_record_address
    mailbox_record = source[record_start : record_start + 4]
    stock_mailbox_record = layout.mailbox_record_stock.to_bytes(
        4, layout.byte_order
    )
    if all((
        erased_units,
        configuration_erased,
        reserve_erased,
        hooks_stock,
        mailbox_record == stock_mailbox_record,
    )):
        return "absent"

    try:
        model = can_telemetry.Configuration.from_bytes(configuration)
        configuration_current = model.to_bytes() == configuration
    except (TypeError, ValueError):
        model = None
        configuration_current = False
    if all((
        current_units,
        configuration_current,
        reserve_erased,
        hooks_current,
        model is not None and mailbox_record == model.mailbox_record(),
    )):
        return "current"

    if reserve_erased and hooks_current:
        for endpoint in can_telemetry_history.endpoints():
            if (rom or layout.rom) not in endpoint.roms or not endpoint.matches(source, layout):
                continue
            try:
                model = endpoint.configuration(configuration)
            except (TypeError, ValueError):
                continue
            if mailbox_record == model.mailbox_record():
                return endpoint.key

    raise EndpointError(f"{context}: partial or unknown CAN telemetry state")


def strip_telemetry_endpoint(
    source, layout, state, checksum_layout=None
):
    """Restore the exact lower-layer bytes used by endpoint validation."""
    if state == "absent":
        return bytes(source)
    if state != "current" and can_telemetry_history.endpoint(state) is None:
        raise EndpointError(f"unsupported CAN telemetry endpoint {state!r}")
    data = bytearray(source)
    for unit in layout.assembly_units:
        data[unit.span.start : unit.span.end] = (
            bytes([0xFF]) * unit.span.size
        )
    data[layout.configuration.start : layout.configuration.end] = (
        bytes([0xFF]) * layout.configuration.size
    )
    for hook in layout.hooks:
        data[hook.address : hook.address + hook.width] = hook.stock.to_bytes(
            hook.width, layout.byte_order
        )
    start = layout.mailbox_record_address
    data[start : start + 4] = layout.mailbox_record_stock.to_bytes(
        4, layout.byte_order
    )
    checksum_layout = checksum_layout or canonical_checksums.LAYOUT
    return bytes(rom_checksums.recalculate(data, checksum_layout))


def require_complete_map_endpoint(
    source,
    map_layout,
    launch_layout,
    map_payloads,
    launch_payloads,
    context,
    rom,
):
    """Accept one current map endpoint with an optional Rolling Launch layer."""
    for unit in map_layout.assembly_units:
        expected = map_switching_compose.endpoint_unit_bytes(
            map_layout, map_payloads, unit
        )
        actual = source[unit.span.start : unit.span.end]
        if actual != expected and unit.key == "cruise_feedback_engine":
            offset = (
                map_layout.feedback.phase_counts_address - unit.span.start
            )
            historical = []
            for on_frames, off_frames in HISTORICAL_FEEDBACK_FRAME_COUNTS:
                candidate = bytearray(expected)
                candidate[offset : offset + 2] = bytes(
                    (on_frames, off_frames)
                )
                historical.append(bytes(candidate))
            if (
                actual in historical
                or sha256(actual) in HISTORICAL_FEEDBACK_ENGINE_SHA256
            ):
                continue
        if actual != expected:
            raise EndpointError(
                f"{context}: partial or unknown patch state; "
                f"map unit {unit.key} differs"
            )

    rolling_hook_values = (
        {}
        if launch_layout is None
        else {
            hook.address: hook.replacement for hook in launch_layout.hooks
        }
    )
    for hook in map_layout.hooks:
        actual = read_integer(
            source, hook.address, hook.width, map_layout.byte_order
        )
        allowed = {hook.replacement}
        if hook.address in rolling_hook_values:
            allowed.add(rolling_hook_values[hook.address])
        if actual not in allowed:
            raise EndpointError(
                f"{context}: partial or unknown patch state; "
                f"map hook {hook.key} is {actual:#x}"
            )

    for family in map_layout.families:
        start = family.pointer_table
        expected = _expected_pointer_table(map_layout, family)
        actual = source[start : start + len(expected)]
        if actual != expected:
            raise EndpointError(
                f"{context}: partial or unknown patch state; "
                f"pointer table {family.key} differs"
            )

    if launch_layout is None:
        if launch_payloads:
            raise EndpointError(
                "disabled Rolling Launch has unexpected payloads"
            )
        return "current"
    return require_coherent_rolling_endpoint(
        source, launch_layout, launch_payloads, context, rom
    )


@dataclass(frozen=True)
class Classification:
    """The runtime layers of an image: each state is "absent", "current", or
    the key of a registered historical Rolling Launch endpoint."""

    telemetry: str
    rolling: str


def historical_endpoints(rom):
    """Return the registered historical Rolling Launch endpoints of a ROM."""
    return tuple(
        endpoint for endpoint in HISTORICAL_ROLLING_ENDPOINTS
        if rom in endpoint.roms
    )


def classify_runtime(source, target, context):
    """Classify the complete runtime of an image that differs from its stock
    image inside the builder write sets."""
    telemetry_state = require_coherent_telemetry_endpoint(
        source,
        target.telemetry_layout,
        target.telemetry_payloads,
        context,
        target.rolling_layout,
        rom=target.rom,
    )
    lower_source = strip_telemetry_endpoint(
        source, target.telemetry_layout, telemetry_state, target.checksum_layout
    )
    rolling_state = require_complete_map_endpoint(
        lower_source,
        target.map_layout,
        target.rolling_layout,
        target.map_payloads,
        target.rolling_payloads,
        context,
        target.rom,
    )
    if (
        telemetry_state != "absent"
        and rolling_state not in TELEMETRY_LOWER_ROLLING_STATES
    ):
        raise EndpointError(
            f"{context}: CAN telemetry is not layered "
            "over the current lower runtime endpoint"
        )
    if target.rolling_layout is None:
        # The map endpoint is the complete lower runtime of a target
        # without a Rolling Launch layer.
        rolling_state = "absent"
    return Classification(telemetry=telemetry_state, rolling=rolling_state)
