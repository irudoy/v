#!/usr/bin/env python3
"""Reference contract for the exact JK08A Rolling Launch runtime.

The model is intentionally independent from the SH-2E implementation. It
defines fail-closed calibration validation, gate ordering, state transitions,
the temporary fuel-cut overlay, cooldown/rearm behavior, and the retard-only
ignition command rule. It never reads or writes a ROM image.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import IntEnum, IntFlag
import struct


CONFIG_MAGIC = 0x524C
CONFIG_MAGIC_INVERSE = CONFIG_MAGIC ^ 0xFFFF
CONFIG_END_MARKER = 0xA55A
CONFIG_SCHEMA_VERSION = 3
CONFIG_SIZE = 32
SLOT_COUNT = 5

BUTTON_RELEASED = 0x20
BUTTON_CANCEL = 0x02
BUTTON_SET = 0x08
ASCD_ACTIVE_MASK = 0x80
FUEL_CUT_ACTIVE_MASK = 0x04


class Phase(IntEnum):
    IDLE = 0
    ACTIVE = 1
    COOLDOWN = 2


class Mode(IntEnum):
    OBSERVE = 0
    RPM_HOLD = 1
    RPM_HOLD_RETARD = 2


class Option(IntFlag):
    NONE = 0


class Flag(IntFlag):
    CONFIG_VALID = 1 << 0
    MAP_ENABLED = 1 << 1
    SELECTOR_IDLE = 1 << 2
    FEEDBACK_IDLE = 1 << 3
    ASCD_OFF = 1 << 4
    BUTTON_HELD = 1 << 5
    SPEED_OK = 1 << 6
    RPM_OK = 1 << 7
    PEDAL_OK = 1 << 8
    COOLANT_OK = 1 << 9
    TIMER_OK = 1 << 11
    ACTIVE = 1 << 12
    FUEL_CUT = 1 << 13
    FUEL_OVERLAY = 1 << 14
    IGNITION_RETARD = 1 << 15


class AbortReason(IntEnum):
    NONE = 0
    CONFIG_INVALID = 1
    MAP_INDEX_INVALID = 2
    MAP_DISABLED = 3
    SELECTOR_BUSY = 4
    FEEDBACK_BUSY = 5
    ASCD_ACTIVE = 6
    BUTTON_RELEASED = 7
    BUTTON_INVALID = 8
    SPEED_LOW = 9
    RPM_LOW = 10
    PEDAL_LOW = 11
    COOLANT_OUTSIDE = 12
    RESERVED_13 = 13
    TIMEOUT = 14
    MAP_REQUEST = 15
    STATE_CORRUPT = 16
    MAP_CHANGED = 17
    MODE_CHANGED = 18


class LimiterAction(IntEnum):
    NONE = 0
    APPLY_OVERLAY = 1
    RESTORE_SNAPSHOT = 2
    RESTORE_MAP_1 = 3


@dataclass(frozen=True)
class Calibration:
    mode: Mode = Mode.OBSERVE
    enable_mask: int = 0
    options: Option = Option.NONE
    coolant_min: int = 0
    coolant_max: int = 0xFF
    min_speed: int = 1
    retard_ramp_native: int = 16
    min_rpm_native: int = 160
    min_pedal: int = 1
    rpm_offset_native: int = 16
    min_hysteresis_native: int = 4
    max_hysteresis_native: int = 12
    run_timeout_ticks: int = 300
    rearm_ticks: int = 100
    target_commands: tuple[int, ...] = (115, 115, 115, 115, 115)
    hysteresis_ratio_tenths: int = 20
    magic: int = CONFIG_MAGIC
    schema_version: int = CONFIG_SCHEMA_VERSION
    magic_inverse: int = CONFIG_MAGIC_INVERSE
    end_marker: int = CONFIG_END_MARKER

    def is_valid(self):
        try:
            mode = Mode(self.mode)
            options = Option(self.options)
        except ValueError:
            return False
        return all((
            self.magic == CONFIG_MAGIC,
            self.schema_version == CONFIG_SCHEMA_VERSION,
            mode in Mode,
            0 <= self.enable_mask <= 0x1F,
            options == Option.NONE,
            0 <= self.coolant_min <= self.coolant_max <= 0xFF,
            0 <= self.min_speed <= 0xFF,
            0 < self.retard_ramp_native <= 0xFF,
            0 < self.min_rpm_native <= 0xFFFF,
            0 <= self.min_pedal <= 0xFFFF,
            0 < self.rpm_offset_native <= 0xFFFF,
            0 < self.min_hysteresis_native
            <= self.max_hysteresis_native <= 0xFF,
            self.max_hysteresis_native < self.rpm_offset_native,
            self.retard_ramp_native <= self.rpm_offset_native,
            0 < self.run_timeout_ticks <= 0x7FFF,
            0 < self.rearm_ticks <= 0x7FFF,
            len(self.target_commands) == SLOT_COUNT,
            all(110 <= value <= 117 for value in self.target_commands),
            0 < self.hysteresis_ratio_tenths <= 0xFF,
            self.magic_inverse == CONFIG_MAGIC_INVERSE,
            self.end_marker == CONFIG_END_MARKER,
        ))

    def enabled_for(self, index):
        return 0 <= index < SLOT_COUNT and bool(
            self.enable_mask & (1 << index)
        )

    def to_bytes(self):
        if len(self.target_commands) != SLOT_COUNT:
            raise ValueError("target command table must contain five bytes")
        data = struct.pack(
            ">H8B3H2B2H5sBHH",
            self.magic,
            self.schema_version,
            int(self.mode),
            self.enable_mask,
            int(self.options),
            self.coolant_min,
            self.coolant_max,
            self.min_speed,
            self.retard_ramp_native,
            self.min_rpm_native,
            self.min_pedal,
            self.rpm_offset_native,
            self.min_hysteresis_native,
            self.max_hysteresis_native,
            self.run_timeout_ticks,
            self.rearm_ticks,
            bytes(self.target_commands),
            self.hysteresis_ratio_tenths,
            self.magic_inverse,
            self.end_marker,
        )
        if len(data) != CONFIG_SIZE:
            raise AssertionError(f"configuration is {len(data)} bytes")
        return data

    @classmethod
    def from_bytes(cls, data):
        if len(data) != CONFIG_SIZE:
            raise ValueError(
                f"configuration is {len(data)} bytes, expected {CONFIG_SIZE}"
            )
        values = struct.unpack(">H8B3H2B2H5sBHH", data)
        return cls(
            magic=values[0],
            schema_version=values[1],
            mode=values[2],
            enable_mask=values[3],
            options=values[4],
            coolant_min=values[5],
            coolant_max=values[6],
            min_speed=values[7],
            retard_ramp_native=values[8],
            min_rpm_native=values[9],
            min_pedal=values[10],
            rpm_offset_native=values[11],
            min_hysteresis_native=values[12],
            max_hysteresis_native=values[13],
            run_timeout_ticks=values[14],
            rearm_ticks=values[15],
            target_commands=tuple(values[16]),
            hysteresis_ratio_tenths=values[17],
            magic_inverse=values[18],
            end_marker=values[19],
        )


@dataclass(frozen=True)
class Inputs:
    active_index: int = 0
    selector_phase: int = 0
    selection_count: int = 0
    selector_elapsed: int = 0
    feedback_pulses: int = 0
    feedback_phase: int = 0
    feedback_ticks: int = 0
    feedback_reserved: int = 0
    ascd_status: int = 0
    button: int = BUTTON_RELEASED
    speed: int = 0
    rpm_native: int = 0
    pedal: int = 0
    coolant: int = 0
    fuel_cut_status: int = 0


@dataclass(frozen=True)
class RuntimeState:
    phase: Phase = Phase.IDLE
    abort_reason: AbortReason = AbortReason.NONE
    flags: Flag = Flag(0)
    active_index_snapshot: int = 0
    active_mode_snapshot: Mode = Mode.OBSERVE
    run_ticks: int = 0
    rearm_ticks: int = 0
    captured_rpm_native: int = 0
    cut_rpm_native: int = 0
    restore_rpm_native: int = 0
    stock_ign_command: int = 0
    effective_ign_command: int = 0
    retard_band_start_native: int = 0


@dataclass(frozen=True)
class StepResult:
    state: RuntimeState
    limiter_action: LimiterAction = LimiterAction.NONE
    limiter_index: int = 0


def _selector_idle(inputs):
    return (
        inputs.selector_phase == 0
        and inputs.selection_count == 0
        and inputs.selector_elapsed == 0
    )


def _feedback_idle(inputs):
    return (
        inputs.feedback_pulses == 0
        and inputs.feedback_phase == 0
        and inputs.feedback_ticks == 0
        and inputs.feedback_reserved == 0
    )


def evaluate_gates(inputs, calibration):
    """Return all satisfied gate flags and the first failure by priority."""
    flags = Flag(0)
    reason = AbortReason.NONE

    def gate(condition, flag, failure):
        nonlocal flags, reason
        if condition:
            flags |= flag
        elif reason == AbortReason.NONE:
            reason = failure

    valid = calibration.is_valid()
    gate(valid, Flag.CONFIG_VALID, AbortReason.CONFIG_INVALID)
    index_valid = 0 <= inputs.active_index < SLOT_COUNT
    gate(index_valid, Flag(0), AbortReason.MAP_INDEX_INVALID)
    gate(
        valid and index_valid and calibration.enabled_for(inputs.active_index),
        Flag.MAP_ENABLED,
        AbortReason.MAP_DISABLED,
    )
    gate(_selector_idle(inputs), Flag.SELECTOR_IDLE, AbortReason.SELECTOR_BUSY)
    gate(_feedback_idle(inputs), Flag.FEEDBACK_IDLE, AbortReason.FEEDBACK_BUSY)
    gate(
        not inputs.ascd_status & ASCD_ACTIVE_MASK,
        Flag.ASCD_OFF,
        AbortReason.ASCD_ACTIVE,
    )
    gate(
        inputs.button == BUTTON_CANCEL,
        Flag.BUTTON_HELD,
        AbortReason.BUTTON_INVALID,
    )
    gate(
        valid
        and (
            calibration.min_speed == 0
            or inputs.speed >= calibration.min_speed
        ),
        Flag.SPEED_OK,
        AbortReason.SPEED_LOW,
    )
    gate(
        valid and inputs.rpm_native >= calibration.min_rpm_native,
        Flag.RPM_OK,
        AbortReason.RPM_LOW,
    )
    gate(
        valid and inputs.pedal >= calibration.min_pedal,
        Flag.PEDAL_OK,
        AbortReason.PEDAL_LOW,
    )
    gate(
        valid
        and calibration.coolant_min
        <= inputs.coolant
        <= calibration.coolant_max,
        Flag.COOLANT_OK,
        AbortReason.COOLANT_OUTSIDE,
    )
    gate(valid, Flag.TIMER_OK, AbortReason.CONFIG_INVALID)
    return flags, reason


def _active_flags(flags, state, inputs):
    result = flags | Flag.ACTIVE
    if state.active_mode_snapshot >= Mode.RPM_HOLD:
        result |= Flag.FUEL_OVERLAY
    if state.active_mode_snapshot >= Mode.RPM_HOLD_RETARD:
        result |= Flag.IGNITION_RETARD
    if inputs.fuel_cut_status & FUEL_CUT_ACTIVE_MASK:
        result |= Flag.FUEL_CUT
    return result


def _state_is_structurally_valid(state):
    try:
        phase = Phase(state.phase)
        mode = Mode(state.active_mode_snapshot)
    except ValueError:
        return False
    if not 0 <= state.active_index_snapshot < SLOT_COUNT:
        return False
    if not all(0 <= value <= 0xFFFF for value in (
        state.run_ticks,
        state.rearm_ticks,
        state.captured_rpm_native,
        state.cut_rpm_native,
        state.restore_rpm_native,
        state.retard_band_start_native,
    )):
        return False
    if not all(0 <= value <= 0xFF for value in (
        state.stock_ign_command,
        state.effective_ign_command,
    )):
        return False
    if phase == Phase.IDLE:
        return (
            mode == Mode.OBSERVE
            and state.run_ticks == 0
            and state.rearm_ticks == 0
        )
    if phase == Phase.ACTIVE:
        return state.rearm_ticks == 0
    return mode in Mode


def _abort_active(state, flags, reason):
    mode = Mode(state.active_mode_snapshot)
    action = (
        LimiterAction.RESTORE_SNAPSHOT
        if mode >= Mode.RPM_HOLD
        else LimiterAction.NONE
    )
    return StepResult(
        replace(
            state,
            phase=Phase.COOLDOWN,
            abort_reason=reason,
            flags=flags & ~(
                Flag.ACTIVE | Flag.FUEL_OVERLAY | Flag.IGNITION_RETARD
            ),
            rearm_ticks=0,
        ),
        action,
        state.active_index_snapshot,
    )


def step(state, inputs, calibration):
    """Advance one exact periodic scheduler tick."""
    if not _state_is_structurally_valid(state):
        recovered = RuntimeState(
            phase=Phase.COOLDOWN,
            abort_reason=AbortReason.STATE_CORRUPT,
            active_index_snapshot=0,
        )
        return StepResult(
            recovered, LimiterAction.RESTORE_MAP_1, 0
        )

    phase = Phase(state.phase)
    if phase == Phase.COOLDOWN:
        if not calibration.is_valid():
            return StepResult(replace(
                state,
                abort_reason=AbortReason.CONFIG_INVALID,
                flags=Flag(0),
                rearm_ticks=0,
            ))
        if inputs.button != BUTTON_RELEASED:
            return StepResult(replace(state, rearm_ticks=0))
        rearm = state.rearm_ticks + 1
        if rearm < calibration.rearm_ticks:
            return StepResult(replace(state, rearm_ticks=rearm))
        return StepResult(replace(
            state,
            phase=Phase.IDLE,
            flags=Flag(0),
            active_mode_snapshot=Mode.OBSERVE,
            run_ticks=0,
            rearm_ticks=0,
        ))

    flags, reason = evaluate_gates(inputs, calibration)
    if phase == Phase.IDLE:
        idle = replace(
            state,
            abort_reason=reason,
            flags=flags,
            active_mode_snapshot=Mode.OBSERVE,
            run_ticks=0,
            rearm_ticks=0,
        )
        if reason != AbortReason.NONE:
            return StepResult(idle)
        cut = min(0xFFFF, inputs.rpm_native + calibration.rpm_offset_native)
        proportional_hysteresis = (
            inputs.rpm_native * calibration.hysteresis_ratio_tenths + 500
        ) // 1000
        hysteresis = min(
            calibration.max_hysteresis_native,
            max(
                calibration.min_hysteresis_native,
                proportional_hysteresis,
            ),
        )
        restore = cut - hysteresis
        retard_ramp = min(
            calibration.rpm_offset_native,
            max(calibration.retard_ramp_native, 2 * hysteresis),
        )
        retard_band_start = max(inputs.rpm_native, cut - retard_ramp)
        active = replace(
            idle,
            phase=Phase.ACTIVE,
            abort_reason=AbortReason.NONE,
            active_index_snapshot=inputs.active_index,
            active_mode_snapshot=Mode(calibration.mode),
            captured_rpm_native=inputs.rpm_native,
            cut_rpm_native=cut,
            restore_rpm_native=restore,
            retard_band_start_native=retard_band_start,
        )
        active = replace(active, flags=_active_flags(flags, active, inputs))
        action = (
            LimiterAction.APPLY_OVERLAY
            if active.active_mode_snapshot >= Mode.RPM_HOLD
            else LimiterAction.NONE
        )
        return StepResult(active, action, inputs.active_index)

    if inputs.active_index != state.active_index_snapshot:
        return _abort_active(state, flags, AbortReason.MAP_CHANGED)
    if calibration.mode != state.active_mode_snapshot:
        return _abort_active(state, flags, AbortReason.MODE_CHANGED)
    if reason != AbortReason.NONE:
        if inputs.button == BUTTON_SET:
            reason = AbortReason.MAP_REQUEST
        elif inputs.button == BUTTON_RELEASED:
            reason = AbortReason.BUTTON_RELEASED
        return _abort_active(state, flags, reason)

    run_ticks = state.run_ticks + 1
    if run_ticks >= calibration.run_timeout_ticks:
        return _abort_active(
            state,
            flags & ~Flag.TIMER_OK,
            AbortReason.TIMEOUT,
        )
    active = replace(
        state,
        abort_reason=AbortReason.NONE,
        flags=_active_flags(flags, state, inputs),
        run_ticks=run_ticks,
    )
    return StepResult(active)


def apply_ignition_command(
    state, calibration, stock_command, rpm_native, apc_mode_snapshot=0
):
    """Apply the normal-mode band-limited retard rule."""
    if not 0 <= stock_command <= 0xFF:
        raise ValueError("stock ignition command must fit in uint8")
    if not 0 <= rpm_native <= 0xFFFF:
        raise ValueError("native RPM must fit in uint16")
    if not 0 <= apc_mode_snapshot <= 0xFF:
        raise ValueError("APC mode snapshot must fit in uint8")
    effective = stock_command
    if (
        (apc_mode_snapshot & 0x40) == 0
        and _state_is_structurally_valid(state)
        and state.phase == Phase.ACTIVE
        and state.active_mode_snapshot == Mode.RPM_HOLD_RETARD
        and calibration.is_valid()
        and Mode(calibration.mode) == Mode.RPM_HOLD_RETARD
        and calibration.enabled_for(state.active_index_snapshot)
    ):
        target = calibration.target_commands[state.active_index_snapshot]
        if stock_command < target:
            cut = state.cut_rpm_native
            start = state.retard_band_start_native
            if rpm_native >= cut and cut > start:
                effective = target
            elif start < rpm_native < cut:
                command_span = target - stock_command
                rpm_span = cut - start
                progress = rpm_native - start
                effective = stock_command + (
                    command_span * progress // rpm_span
                )
    return replace(
        state,
        stock_ign_command=stock_command,
        effective_ign_command=effective,
    ), effective
