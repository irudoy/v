#!/usr/bin/env python3
"""Executable reference model for the JK08A map selector contract.

This module does not patch a ROM. It defines the state transitions and the
fail-closed calibration selection and limiter-shadow transaction that an SH-2E
implementation must match.
"""

from dataclasses import dataclass
from enum import IntEnum

from patches.map_switching_layout import load_layout


RELEASED = 0x20
CANCEL = 0x02
SET_COAST = 0x08
RESUME_ACCEL = 0x10
INVALID_ZERO = 0x00

LAYOUT = load_layout()
FAMILIES = LAYOUT.family_by_key
SLOT_COUNT = LAYOUT.slot_count
TIMEOUT_TICKS = 100

STOCK_OVER_RUN_HOLD_BASE = FAMILIES[
    "over_run_fuel_hold"
].canonical_address
OVER_RUN_HOLD_BASES = FAMILIES[
    "over_run_fuel_hold"
].all_slot_addresses
STOCK_OVER_RUN_HOLD_BYTES = bytes.fromhex(
    "78 78 78 78 78 70 6c 68 64 60 58 50 48 48 48 48"
)
STOCK_OVER_RUN_CUT_BASE = FAMILIES[
    "over_run_fuel_cut"
].canonical_address
OVER_RUN_CUT_BASES = FAMILIES[
    "over_run_fuel_cut"
].all_slot_addresses
STOCK_OVER_RUN_CUT_BYTES = bytes.fromhex(
    "78 78 78 78 78 70 58 54 50 4c 48 38 2a 2a 2a 38"
)
STOCK_OVER_RUN_RESTORE_BASE = FAMILIES[
    "over_run_fuel_restore"
].canonical_address
OVER_RUN_RESTORE_BASES = FAMILIES[
    "over_run_fuel_restore"
].all_slot_addresses
STOCK_OVER_RUN_RESTORE_BYTES = bytes.fromhex(
    "50 50 50 50 50 48 44 40 3c 38 38 30 24 24 24 30"
)
STOCK_OVER_RUN_INTERMEDIATE_RESTORE_BASE = FAMILIES[
    "over_run_fuel_intermediate_restore"
].canonical_address
OVER_RUN_INTERMEDIATE_RESTORE_BASES = FAMILIES[
    "over_run_fuel_intermediate_restore"
].all_slot_addresses
STOCK_OVER_RUN_INTERMEDIATE_RESTORE_BYTES = bytes.fromhex(
    "6c 6c 6c 6c 6c 64 60 5c 58 54 4c 30 24 24 24 30"
)

STOCK_IGNITION_MAIN_BASE = FAMILIES[
    "ignition_timing_trim_main"
].canonical_address
IGNITION_MAIN_BASES = FAMILIES[
    "ignition_timing_trim_main"
].all_slot_addresses
STOCK_IGNITION_HIGH_DET_BASE = FAMILIES[
    "ignition_timing_trim_high_det"
].canonical_address
IGNITION_HIGH_DET_BASES = FAMILIES[
    "ignition_timing_trim_high_det"
].all_slot_addresses
STOCK_FUEL_TARGETS_BASE = FAMILIES["fuel_targets"].canonical_address
FUEL_TARGETS_BASES = FAMILIES["fuel_targets"].all_slot_addresses
STOCK_FUEL_COMPENSATION_BASE = FAMILIES[
    "fuel_compensation_main"
].canonical_address
FUEL_COMPENSATION_BASES = FAMILIES[
    "fuel_compensation_main"
].all_slot_addresses
STOCK_REV_FUEL_CUT_BASE = FAMILIES[
    "rev_limit_fuel_cut"
].canonical_address
REV_FUEL_CUT_BASES = FAMILIES[
    "rev_limit_fuel_cut"
].all_slot_addresses
STOCK_REV_THROTTLE_CUT_BASE = FAMILIES[
    "rev_limit_throttle_cut"
].canonical_address
REV_THROTTLE_CUT_BASES = FAMILIES[
    "rev_limit_throttle_cut"
].all_slot_addresses

ADAPTER_FAMILY_BASES = {
    family.canonical_address: family.all_slot_addresses
    for family in LAYOUT.families
    if family.access_kind == "adapter"
}
SELECTOR_DIAGNOSTIC_BIT = 0x80
FEEDBACK_STATUS_MASK = LAYOUT.feedback.status_mask
FEEDBACK_LAMP_ON_VALUE = LAYOUT.feedback.lamp_on_value
FEEDBACK_LAMP_OFF_VALUE = LAYOUT.feedback.lamp_off_value


class Phase(IntEnum):
    IDLE = 0
    SET_HELD = 1
    CANCEL_HELD = 2


class FeedbackPhase(IntEnum):
    IDLE = 0
    ON = 1
    OFF = 2


@dataclass(frozen=True)
class SelectorState:
    active_index: int = 0
    phase: int = Phase.IDLE
    selection_count: int = 0
    elapsed_ticks: int = 0


@dataclass(frozen=True)
class SelectorDecision:
    """One selector step before a requested map is published."""

    state: SelectorState
    commit_index: int | None = None


@dataclass(frozen=True)
class PreparedCalibration:
    """Complete data prepared for one atomic calibration commit."""

    active_index: int
    fuel_cut_shadow: bytes
    throttle_shadow: bytes
    throttle_runtime_scalar: int


@dataclass(frozen=True)
class CalibrationRuntime:
    """Observable calibration state after an indivisible commit."""

    active_index: int
    fuel_cut_shadow: bytes
    throttle_shadow: bytes
    throttle_runtime_scalar: int


@dataclass(frozen=True)
class FeedbackState:
    """CRUISE-lamp pulse state advanced by CAN 0x551 serializations."""

    pulses_remaining: int = 0
    phase: int = FeedbackPhase.IDLE
    phase_ticks: int = 0


def reset_transient(active_index=0):
    """Return an idle state while retaining a validated active map."""
    if not 0 <= active_index < SLOT_COUNT:
        active_index = 0
    return SelectorState(active_index=active_index)


def _validate_state(state):
    active_index = state.active_index
    if not 0 <= active_index < SLOT_COUNT:
        return reset_transient(0), False
    try:
        phase = Phase(state.phase)
    except ValueError:
        return reset_transient(active_index), False
    if not 0 <= state.selection_count <= SLOT_COUNT:
        return reset_transient(active_index), False
    if not 0 <= state.elapsed_ticks < TIMEOUT_TICKS:
        return reset_transient(active_index), False
    if phase == Phase.IDLE:
        if state.selection_count != 0 or state.elapsed_ticks != 0:
            return reset_transient(active_index), False
    elif state.elapsed_ticks == 0:
        return reset_transient(active_index), False
    return (
        SelectorState(
            active_index=active_index,
            phase=phase,
            selection_count=state.selection_count,
            elapsed_ticks=state.elapsed_ticks,
        ),
        True,
    )


def advance_selector_decision(
    state,
    previous_code,
    current_code,
    *,
    ascd_enabled=False,
):
    """Evaluate one selector invocation without publishing a new map index.

    The caller supplies the stock debounced previous/current ASCD one-hot pair.
    An armed gesture is accepted only while ASCD is off. Timeout expiration,
    corrupt state, unexpected transitions, and count overflow retain the
    validated active map and reset the transient state. A valid release returns
    a commit request while the returned state still contains the old index.
    """
    state, valid = _validate_state(state)
    if not valid:
        return SelectorDecision(state)
    if ascd_enabled:
        return SelectorDecision(reset_transient(state.active_index))

    if state.phase == Phase.IDLE:
        if previous_code == RELEASED and current_code == SET_COAST:
            return SelectorDecision(
                SelectorState(
                    active_index=state.active_index,
                    phase=Phase.SET_HELD,
                    selection_count=0,
                    elapsed_ticks=1,
                )
            )
        return SelectorDecision(state)

    elapsed_ticks = state.elapsed_ticks + 1
    if elapsed_ticks >= TIMEOUT_TICKS:
        return SelectorDecision(reset_transient(state.active_index))

    if state.phase == Phase.SET_HELD:
        if previous_code == SET_COAST and current_code == SET_COAST:
            return SelectorDecision(
                SelectorState(
                    state.active_index,
                    Phase.SET_HELD,
                    state.selection_count,
                    elapsed_ticks,
                )
            )
        if previous_code == SET_COAST and current_code == CANCEL:
            return SelectorDecision(
                SelectorState(
                    state.active_index,
                    Phase.CANCEL_HELD,
                    state.selection_count,
                    elapsed_ticks,
                )
            )
        if previous_code == SET_COAST and current_code == RELEASED:
            if 1 <= state.selection_count <= SLOT_COUNT:
                return SelectorDecision(
                    reset_transient(state.active_index),
                    state.selection_count - 1,
                )
            return SelectorDecision(reset_transient(state.active_index))
        return SelectorDecision(reset_transient(state.active_index))

    if previous_code == CANCEL and current_code == CANCEL:
        return SelectorDecision(
            SelectorState(
                state.active_index,
                Phase.CANCEL_HELD,
                state.selection_count,
                elapsed_ticks,
            )
        )
    if previous_code == CANCEL and current_code == SET_COAST:
        selection_count = state.selection_count + 1
        if selection_count > SLOT_COUNT:
            return SelectorDecision(reset_transient(state.active_index))
        return SelectorDecision(
            SelectorState(
                state.active_index,
                Phase.SET_HELD,
                selection_count,
                elapsed_ticks,
            )
        )
    return SelectorDecision(reset_transient(state.active_index))


def advance_selector(
    state,
    previous_code,
    current_code,
    *,
    ascd_enabled=False,
):
    """Advance one complete selector invocation as an atomic state model."""
    decision = advance_selector_decision(
        state,
        previous_code,
        current_code,
        ascd_enabled=ascd_enabled,
    )
    if decision.commit_index is None:
        return decision.state
    return reset_transient(decision.commit_index)


def select_calibration_base(requested_base, active_index):
    """Select any adapter-backed family and pass every other base unchanged."""
    bases = ADAPTER_FAMILY_BASES.get(requested_base)
    if bases is None:
        return requested_base
    if not 0 <= active_index < SLOT_COUNT:
        active_index = 0
    return bases[active_index]


def _rom_bytes(rom):
    return rom.data if hasattr(rom, "data") else bytes(rom)


def _read_exact(data, address, size, label):
    value = data[address : address + size]
    if len(value) != size:
        raise ValueError(
            f"{label}: [{address:#x}, {address + size:#x}) exceeds ROM"
        )
    return value


def normalized_index(active_index):
    """Resolve every invalid index to map 1."""
    return active_index if 0 <= active_index < SLOT_COUNT else 0


def prepare_calibration_commit(rom, active_index):
    """Build complete limiter shadows before publishing the active index.

    The fuel-cut shadow preserves the two stock alternate words after its 2x2
    switchable table. The throttle shadow preserves its complete 28-byte stock
    cluster and replaces only the selected scalar at offset 8.
    """
    data = _rom_bytes(rom)
    active_index = normalized_index(active_index)
    fuel_cut = FAMILIES["rev_limit_fuel_cut"]
    throttle = FAMILIES["rev_limit_throttle_cut"]

    fuel_container = bytearray(
        _read_exact(
            data,
            fuel_cut.stock_container_start,
            fuel_cut.stock_container_size,
            fuel_cut.key,
        )
    )
    fuel_selected = _read_exact(
        data,
        fuel_cut.slot_address(active_index),
        fuel_cut.byte_length,
        f"{fuel_cut.key}.map_{active_index + 1}",
    )
    fuel_start = fuel_cut.selected_offset
    fuel_container[
        fuel_start : fuel_start + fuel_cut.byte_length
    ] = fuel_selected

    throttle_container = bytearray(
        _read_exact(
            data,
            throttle.stock_container_start,
            throttle.stock_container_size,
            throttle.key,
        )
    )
    throttle_selected = _read_exact(
        data,
        throttle.slot_address(active_index),
        throttle.byte_length,
        f"{throttle.key}.map_{active_index + 1}",
    )
    throttle_start = throttle.selected_offset
    throttle_container[
        throttle_start : throttle_start + throttle.byte_length
    ] = throttle_selected
    runtime_scalar = int.from_bytes(
        throttle_selected, LAYOUT.byte_order
    )

    return PreparedCalibration(
        active_index=active_index,
        fuel_cut_shadow=bytes(fuel_container),
        throttle_shadow=bytes(throttle_container),
        throttle_runtime_scalar=runtime_scalar,
    )


def publish_calibration_commit(previous, prepared):
    """Publish prepared shadows and the active index as one model transition.

    The SH-2E implementation must write both RAM shadows and
    ``0xFFFF1796`` while interrupts are masked, then store ``active_index`` as
    the final operation before restoring SR. This immutable model deliberately
    exposes no partially updated state.
    """
    if not isinstance(previous, CalibrationRuntime):
        raise TypeError("previous must be CalibrationRuntime")
    if not isinstance(prepared, PreparedCalibration):
        raise TypeError("prepared must be PreparedCalibration")
    if normalized_index(prepared.active_index) != prepared.active_index:
        raise ValueError("prepared active index is invalid")
    if len(prepared.fuel_cut_shadow) != LAYOUT.ram.fuel_cut_shadow.size:
        raise ValueError("prepared fuel-cut shadow has the wrong size")
    if len(prepared.throttle_shadow) != LAYOUT.ram.throttle_shadow.size:
        raise ValueError("prepared throttle shadow has the wrong size")
    throttle = FAMILIES["rev_limit_throttle_cut"]
    scalar_bytes = prepared.throttle_shadow[
        throttle.selected_offset :
        throttle.selected_offset + throttle.byte_length
    ]
    if (
        not 0 <= prepared.throttle_runtime_scalar <= 0xFFFF
        or int.from_bytes(scalar_bytes, LAYOUT.byte_order)
        != prepared.throttle_runtime_scalar
    ):
        raise ValueError(
            "prepared throttle runtime scalar differs from the shadow"
        )
    return CalibrationRuntime(
        active_index=prepared.active_index,
        fuel_cut_shadow=prepared.fuel_cut_shadow,
        throttle_shadow=prepared.throttle_shadow,
        throttle_runtime_scalar=prepared.throttle_runtime_scalar,
    )


def initialize_calibration_runtime(rom, active_index=0):
    """Initialize all direct-access shadows with fail-closed index handling."""
    prepared = prepare_calibration_commit(rom, active_index)
    seed = CalibrationRuntime(
        active_index=0,
        fuel_cut_shadow=bytes(len(prepared.fuel_cut_shadow)),
        throttle_shadow=bytes(len(prepared.throttle_shadow)),
        throttle_runtime_scalar=0,
    )
    return publish_calibration_commit(seed, prepared)


def advance_calibration_system(
    state,
    runtime,
    rom,
    previous_code,
    current_code,
    *,
    ascd_enabled=False,
):
    """Advance selector and runtime with shadow preparation before publication.

    Returns ``(selector_state, calibration_runtime, committed)``. Divergent
    selector/runtime indices are treated as corrupt state and fail closed to
    map 1 without accepting the current input transition.
    """
    if (
        not isinstance(runtime, CalibrationRuntime)
        or state.active_index != runtime.active_index
        or normalized_index(runtime.active_index) != runtime.active_index
    ):
        fallback = initialize_calibration_runtime(rom, 0)
        return SelectorState(), fallback, False

    decision = advance_selector_decision(
        state,
        previous_code,
        current_code,
        ascd_enabled=ascd_enabled,
    )
    if decision.commit_index is None:
        return decision.state, runtime, False

    prepared = prepare_calibration_commit(rom, decision.commit_index)
    runtime = publish_calibration_commit(runtime, prepared)
    return reset_transient(runtime.active_index), runtime, True


def mirror_active_index(status_byte, active_index):
    """Mirror non-default selection in bit 7 while preserving stock bits."""
    value = status_byte & ~SELECTOR_DIAGNOSTIC_BIT
    if 0 < active_index < SLOT_COUNT:
        value |= SELECTOR_DIAGNOSTIC_BIT
    return value


def visual_confirmation_count(active_index):
    """Return the CRUISE-lamp pulse count, with corrupt state shown as map 1."""
    if not 0 <= active_index < SLOT_COUNT:
        active_index = 0
    return active_index + 1


def queue_visual_feedback(active_index):
    """Queue one through five pulses after a completed calibration commit."""
    return FeedbackState(
        pulses_remaining=visual_confirmation_count(active_index),
        phase=FeedbackPhase.ON,
        phase_ticks=0,
    )


def _validate_feedback_state(state):
    if not isinstance(state, FeedbackState):
        return FeedbackState(), False
    try:
        phase = FeedbackPhase(state.phase)
    except ValueError:
        return FeedbackState(), False
    if phase == FeedbackPhase.IDLE:
        if state.pulses_remaining != 0 or state.phase_ticks != 0:
            return FeedbackState(), False
    elif (
        not 1 <= state.pulses_remaining <= SLOT_COUNT
        or not 0 <= state.phase_ticks <= 0xFF
    ):
        return FeedbackState(), False
    return FeedbackState(
        pulses_remaining=state.pulses_remaining,
        phase=phase,
        phase_ticks=state.phase_ticks,
    ), True


def feedback_active(state):
    """Return true only for a structurally valid active feedback sequence."""
    state, valid = _validate_feedback_state(state)
    return valid and state.phase != FeedbackPhase.IDLE


def _override_feedback_status(stock_status_byte, value):
    if not 0 <= stock_status_byte <= 0xFF:
        raise ValueError("stock CAN status byte must fit in one byte")
    return (
        stock_status_byte & (~FEEDBACK_STATUS_MASK & 0xFF)
    ) | value


def advance_visual_feedback(
    state,
    stock_status_byte,
    *,
    on_ticks,
    off_ticks,
):
    """Advance feedback once per stock CAN 0x551 serializer invocation.

    Returns ``(next_state, outgoing_status_byte)``. The exact serializer runs
    first; active feedback replaces only its byte-5 low two-bit state. Phase
    durations are caller-supplied counts of frame serializations because their
    wall-clock period remains a bench measurement.
    """
    if not 1 <= on_ticks <= 0xFF or not 1 <= off_ticks <= 0xFF:
        raise ValueError("feedback phase lengths must be 1..255 ticks")
    state, valid = _validate_feedback_state(state)
    if not valid or state.phase == FeedbackPhase.IDLE:
        return FeedbackState(), stock_status_byte

    if state.phase == FeedbackPhase.ON:
        outgoing = _override_feedback_status(
            stock_status_byte,
            FEEDBACK_LAMP_ON_VALUE,
        )
        next_ticks = state.phase_ticks + 1
        if next_ticks >= on_ticks:
            state = FeedbackState(
                pulses_remaining=state.pulses_remaining,
                phase=FeedbackPhase.OFF,
                phase_ticks=0,
            )
        else:
            state = FeedbackState(
                pulses_remaining=state.pulses_remaining,
                phase=FeedbackPhase.ON,
                phase_ticks=next_ticks,
            )
        return state, outgoing

    outgoing = _override_feedback_status(
        stock_status_byte,
        FEEDBACK_LAMP_OFF_VALUE,
    )
    next_ticks = state.phase_ticks + 1
    if next_ticks < off_ticks:
        return FeedbackState(
            pulses_remaining=state.pulses_remaining,
            phase=FeedbackPhase.OFF,
            phase_ticks=next_ticks,
        ), outgoing

    pulses_remaining = state.pulses_remaining - 1
    if pulses_remaining == 0:
        return FeedbackState(), outgoing
    return FeedbackState(
        pulses_remaining=pulses_remaining,
        phase=FeedbackPhase.ON,
        phase_ticks=0,
    ), outgoing


def advance_configured_visual_feedback(
    state,
    stock_status_byte,
    *,
    on_ticks=None,
    off_ticks=None,
):
    """Advance feedback using manifest defaults or an explicit bench config.

    A zero/zero configuration remains the fail-closed disabled state: it clears
    the feedback queue and preserves the stock serializer result. A partially
    configured pair is invalid.
    """
    if on_ticks is None:
        on_ticks = LAYOUT.feedback.default_on_frames
    if off_ticks is None:
        off_ticks = LAYOUT.feedback.default_off_frames
    if on_ticks == 0 and off_ticks == 0:
        if not 0 <= stock_status_byte <= 0xFF:
            raise ValueError("stock CAN status byte must fit in one byte")
        return FeedbackState(), stock_status_byte
    if on_ticks == 0 or off_ticks == 0:
        raise ValueError(
            "feedback phase lengths must both be zero or both be nonzero"
        )
    return advance_visual_feedback(
        state,
        stock_status_byte,
        on_ticks=on_ticks,
        off_ticks=off_ticks,
    )


def advance_calibration_system_with_feedback(
    state,
    runtime,
    feedback,
    rom,
    previous_code,
    current_code,
    *,
    ascd_enabled=False,
):
    """Advance selection and queue visual feedback after atomic publication.

    A valid active feedback sequence blocks selector input. Corrupt feedback
    state is cleared without accepting the current switch transition.
    """
    feedback, feedback_valid = _validate_feedback_state(feedback)
    if (
        not isinstance(runtime, CalibrationRuntime)
        or normalized_index(runtime.active_index) != runtime.active_index
    ):
        fallback = initialize_calibration_runtime(rom, 0)
        return SelectorState(), fallback, FeedbackState(), False
    if not feedback_valid:
        return (
            reset_transient(runtime.active_index),
            runtime,
            FeedbackState(),
            False,
        )
    if feedback.phase != FeedbackPhase.IDLE:
        return (
            reset_transient(runtime.active_index),
            runtime,
            feedback,
            False,
        )

    state, runtime, committed = advance_calibration_system(
        state,
        runtime,
        rom,
        previous_code,
        current_code,
        ascd_enabled=ascd_enabled,
    )
    if committed:
        feedback = queue_visual_feedback(runtime.active_index)
    return state, runtime, feedback, committed
