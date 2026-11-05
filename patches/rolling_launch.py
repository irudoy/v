#!/usr/bin/env python3
"""Independent schema 6 model of the spark-only Rolling Launch runtime.

The ignition implementation supplies event eligibility. This model selects
cuts without choosing a physical delivery point and never reads a ROM.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import IntEnum, IntFlag
import struct

CONFIG_MAGIC = 0x524C
CONFIG_MAGIC_INVERSE = 0xADB3
CONFIG_END_MARKER = 0xA55A
CONFIG_SCHEMA_VERSION = 6
CONFIG_HEAD_FORMAT = ">H6B4HhBB3H4B2H2B2H"
SLOT_FORMAT = ">h4B3H"
SLOT_COUNT = 5
SLOT_OFFSET = 0x28
SLOT_SIZE = 12
CONFIG_FORMAT = CONFIG_HEAD_FORMAT + SLOT_FORMAT[1:] * SLOT_COUNT + "H"
CONFIG_SIZE = struct.calcsize(CONFIG_FORMAT)
LEGACY_SCHEMA_VERSION = 4
LEGACY_CONFIG_SIZE = 40
PREVIOUS_SCHEMA_VERSION = 5
PREVIOUS_CONFIG_SIZE = 72
TRIM_MAX = 40
EFFICIENCY_TABLE_SIZE = 82
ENGINE_STATE_SIZE = 28
STATE_SIZE = 44
EXTENSION_SIZE = 32
U_ONE = 1000
INTEGRATOR_SHIFT = 4
SPEED_FRAME_AGE_LIMIT_MAX = 254
BUTTON_RELEASED = 0x20
BUTTON_CANCEL = 0x02
BUTTON_SET = 0x08
MAIN_PRESSED_MASK = 0x80
HCAN1_INITIALIZED_MASK = 0x01
PL4_READY_MASK = 0x80
ASCD_FEEDBACK_MASK = 0x70
ASCD_FEEDBACK_OFF = 0x00
ASCD_FEEDBACK_CRUISE = 0x50
ASCD_FEEDBACK_CRUISE_SET = 0x40


class Phase(IntEnum):
    IDLE = 0
    ACTIVE = 1
    COOLDOWN = 2


class Mode(IntEnum):
    OBSERVE = 0
    HOLD = 1


class RegulatorKind(IntEnum):
    NONE = 0
    RPM = 1
    SPEED = 2


class Option(IntFlag):
    NONE = 0


class Flag(IntFlag):
    CONFIG_VALID = 1 << 0
    MAP_ENABLED = 1 << 1
    SELECTOR_IDLE = 1 << 2
    FEEDBACK_IDLE = 1 << 3
    MAIN_RELEASED = 1 << 4
    BUTTON_HELD = 1 << 5
    SPEED_OK = 1 << 6
    RPM_OK = 1 << 7
    PEDAL_OK = 1 << 8
    COOLANT_OK = 1 << 9
    SPEED_FRAME_OK = 1 << 10
    TIMER_OK = 1 << 11
    ACTIVE = 1 << 12
    HOLD = 1 << 14


ACTIVE_OUTPUT_FLAGS = Flag.ACTIVE | Flag.HOLD
VALID_FLAGS = ((1 << 13) - 1) | int(Flag.HOLD)


class AbortReason(IntEnum):
    NONE = 0
    CONFIG_INVALID = 1
    MAP_INDEX_INVALID = 2
    MAP_DISABLED = 3
    SELECTOR_BUSY = 4
    FEEDBACK_BUSY = 5
    MAIN_PRESSED = 6
    BUTTON_RELEASED = 7
    BUTTON_INVALID = 8
    SPEED_LOW = 9
    RPM_LOW = 10
    PEDAL_LOW = 11
    COOLANT_OUTSIDE = 12
    SPEED_FRAME_STALE = 13
    TIMEOUT = 14
    MAP_REQUEST = 15
    STATE_CORRUPT = 16
    MAP_CHANGED = 17
    MODE_CHANGED = 18
    SPEED_HIGH = 19
    SPEED_ABOVE_WINDOW = 20
    SPEED_BELOW_WINDOW = 21
    SPEED_VALUE_INVALID = 22
    SPEED_SOURCE_NOT_READY = 23
    RPM_INPUT_INVALID = 24
    CANCEL_CAPTURE_INVALID = 25


class LimiterAction(IntEnum):
    NONE = 0
    RESTORE_MAP_1 = 1


def _clamp(value, low, high):
    return min(high, max(low, value))


def _integer(value, low, high):
    return isinstance(value, int) and not isinstance(value, bool) and low <= value <= high


@dataclass(frozen=True)
class Slot:
    integral_gain: int = 0
    max_trim_rpm: int = 0
    max_trim_speed: int = 0
    floor_command: int = 0
    reserved_05: int = 0
    launch_rpm_native: int = 161
    launch_speed_threshold: int = 1
    launch_soft_width_native: int = 0

    def is_valid(self, min_rpm_native=0):
        return all((
            _integer(self.integral_gain, 0, 32767),
            _integer(self.max_trim_rpm, 0, 40),
            _integer(self.max_trim_speed, 0, 40),
            _integer(self.floor_command, 0, 120),
            _integer(self.reserved_05, 0, 0),
            _integer(self.launch_rpm_native, min_rpm_native + 1, 32767),
            _integer(self.launch_speed_threshold, 1, 65535),
            _integer(self.launch_soft_width_native, 0, 32767),
        )) and self.launch_soft_width_native < self.launch_rpm_native - min_rpm_native


def trim_efficiency(value):
    if not _integer(value, 0, 255):
        raise ValueError("F value lies outside one byte")
    return (256 - value) * U_ONE // 256


@dataclass(frozen=True)
class EfficiencyTable:
    """Derived efficiency at every integer applied trim, separate from slots."""
    values: tuple[int, ...] = (U_ONE,) * 41

    def is_valid(self):
        return (isinstance(self.values, tuple) and len(self.values) == 41
                and self.values[0] == U_ONE
                and all(_integer(value, 1, 1000) for value in self.values))

    def at(self, applied_trim):
        if not self.is_valid() or not _integer(applied_trim, 0, 40):
            raise ValueError("invalid efficiency table or applied trim")
        return self.values[applied_trim]

    def to_bytes(self):
        if not self.is_valid():
            raise ValueError("invalid efficiency table")
        return struct.pack(">41H", *self.values)

    @classmethod
    def from_bytes(cls, data):
        if len(data) != EFFICIENCY_TABLE_SIZE:
            raise ValueError("efficiency table must contain 82 bytes")
        result = cls(struct.unpack(">41H", data))
        if not result.is_valid():
            raise ValueError("invalid efficiency table")
        return result

    @classmethod
    def from_curve(cls, axis, values):
        """Use floor interpolation on ascending and descending F segments."""
        if (len(axis) != 16 or len(values) != 16
                or any(not _integer(x, 0, 255) for x in (*axis, *values))
                or axis[0] != 0 or axis[-1] < 40
                or any(a >= b for a, b in zip(axis, axis[1:]))):
            raise ValueError("trim efficiency axis must increase from 0 through 40")
        result = [1000]
        for trim in range(1, 41):
            for i, (low, high) in enumerate(zip(axis, axis[1:])):
                if low <= trim <= high:
                    value = values[i] + (values[i+1]-values[i]) * (trim-low) // (high-low)
                    result.append(trim_efficiency(value))
                    break
        return cls(tuple(result))


@dataclass(frozen=True)
class Calibration:
    mode: Mode = Mode.OBSERVE
    enable_mask: int = 0
    options: Option = Option.NONE
    coolant_min: int = 0
    coolant_max: int = 255
    min_speed: int = 200
    max_speed: int = 1200
    min_rpm_native: int = 160
    min_pedal: int = 1
    target_speed_offset: int = 0
    window_width: int = 40
    window_top: int = 20
    u_rate_limit: int = 50
    reserved: int = 0
    integrator_limit: int = 500
    abort_above: int = 150
    abort_below: int = 100
    reserved_1c: int = 0
    reserved_1d: int = 0
    run_timeout_ticks: int = 781
    rearm_ticks: int = 98
    speed_frame_age_limit: int = 10
    reserved_23: int = 0
    magic: int = CONFIG_MAGIC
    schema_version: int = 6
    magic_inverse: int = CONFIG_MAGIC_INVERSE
    end_marker: int = CONFIG_END_MARKER
    slots: tuple[Slot, ...] = (Slot(),) * 5
    slot_end_marker: int = CONFIG_END_MARKER

    def slot(self, index):
        return self.slots[index]

    def is_valid(self):
        ranges = (
            (self.mode, 0, 1), (self.enable_mask, 0, 31), (self.options, 0, 0),
            (self.coolant_min, 0, 255), (self.coolant_max, 0, 255),
            (self.min_speed, 0, 65535), (self.max_speed, 0, 65535),
            (self.min_rpm_native, 1, 32766), (self.min_pedal, 0, 65535),
            (self.target_speed_offset, -32768, 32767),
            (self.window_width, 1, 255), (self.window_top, 0, 255),
            (self.u_rate_limit, 1, 1000), (self.reserved, 0, 0),
            (self.integrator_limit, 0, 1000), (self.abort_above, 1, 255),
            (self.abort_below, 1, 255), (self.reserved_1c, 0, 0),
            (self.reserved_1d, 0, 0), (self.run_timeout_ticks, 1, 32767),
            (self.rearm_ticks, 1, 32767), (self.speed_frame_age_limit, 1, 254),
            (self.reserved_23, 0, 0), (self.magic, CONFIG_MAGIC, CONFIG_MAGIC),
            (self.schema_version, 6, 6),
            (self.magic_inverse, CONFIG_MAGIC_INVERSE, CONFIG_MAGIC_INVERSE),
            (self.end_marker, CONFIG_END_MARKER, CONFIG_END_MARKER),
            (self.slot_end_marker, CONFIG_END_MARKER, CONFIG_END_MARKER),
        )
        if not all(_integer(value, low, high) for value, low, high in ranges):
            return False
        return (self.coolant_min <= self.coolant_max
                and (not self.min_speed or not self.max_speed or self.min_speed <= self.max_speed)
                and -self.abort_above < self.target_speed_offset < self.abort_below
                and isinstance(self.slots, tuple) and len(self.slots) == 5
                and all(isinstance(slot, Slot) and slot.is_valid(self.min_rpm_native)
                        for slot in self.slots))

    def enabled_for(self, index):
        return _integer(index, 0, 4) and bool(self.enable_mask & (1 << index))

    def to_bytes(self):
        return struct.pack(CONFIG_FORMAT,
            self.magic, self.schema_version, int(self.mode), self.enable_mask,
            int(self.options), self.coolant_min, self.coolant_max,
            self.min_speed, self.max_speed, self.min_rpm_native, self.min_pedal,
            self.target_speed_offset, self.window_width, self.window_top,
            self.u_rate_limit, self.reserved, self.integrator_limit,
            self.abort_above, self.abort_below, self.reserved_1c, self.reserved_1d,
            self.run_timeout_ticks, self.rearm_ticks, self.speed_frame_age_limit,
            self.reserved_23, self.magic_inverse, self.end_marker,
            *(value for slot in self.slots for value in (
                slot.integral_gain, slot.max_trim_rpm, slot.max_trim_speed,
                slot.floor_command, slot.reserved_05,
                slot.launch_rpm_native, slot.launch_speed_threshold,
                slot.launch_soft_width_native)), self.slot_end_marker)

    @classmethod
    def from_bytes(cls, data):
        if len(data) != CONFIG_SIZE:
            raise ValueError(f"configuration is {len(data)} bytes, expected {CONFIG_SIZE}")
        v = struct.unpack(CONFIG_FORMAT, data)
        names = ("magic", "schema_version", "mode", "enable_mask", "options",
                 "coolant_min", "coolant_max", "min_speed", "max_speed",
                 "min_rpm_native", "min_pedal", "target_speed_offset", "window_width",
                 "window_top", "u_rate_limit", "reserved", "integrator_limit",
                 "abort_above", "abort_below", "reserved_1c", "reserved_1d",
                 "run_timeout_ticks", "rearm_ticks", "speed_frame_age_limit",
                 "reserved_23", "magic_inverse", "end_marker")
        return cls(**dict(zip(names, v[:27])),
                   slots=tuple(Slot(*v[27+8*i:35+8*i]) for i in range(5)),
                   slot_end_marker=v[-1])


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
    speed_frame_age: int = 0
    hcan1_state: int = 0
    port_input_state: int = 0
    speed_wire_word: int = 0xFFFF
    rpm_native: int = 0
    pedal: int = 0
    coolant: int = 0


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
    target_speed: int = 0
    torque_fraction: int = 0
    speed_error: int = 0
    integrator: int = 0
    target_rpm_native: int = 0
    torque_command: int = 0
    rpm_error_native: int = 0
    cut_fraction: int = 0
    regulator_kind: RegulatorKind = RegulatorKind.NONE
    input_status: int = 0
    control_error: int = 0
    rpm_sample_native: int = 0
    speed_sample: int = 0
    stock_command: int = 0
    effective_command: int = 0
    applied_trim: int = 0
    actuation_ready: bool = False
    applied_efficiency: int = U_ONE
    accepted_button: int = 0
    speed_age: int = 0
    law_output: int = 0
    cancel_speed_capture: int = 0
    selected_target: int = 0
    active_max_trim: int = 0

    @property
    def wire_mode_trim(self):
        return (self.applied_trim
                | (int(self.regulator_kind == RegulatorKind.SPEED) << 6)
                | (int(self.actuation_ready) << 7))

    @property
    def wire_efficiency(self):
        return (self.applied_efficiency
                | (int(self.regulator_kind == RegulatorKind.SPEED) << 14)
                | (int(self.actuation_ready) << 15))

    @property
    def wire_status(self):
        return (int(self.regulator_kind) | ((self.input_status & 7) << 2)
                | (int(self.accepted_button == BUTTON_CANCEL) << 5)
                | (int(self.accepted_button == BUTTON_RELEASED) << 6)
                | (int(self.actuation_ready) << 7))


@dataclass(frozen=True)
class StepResult:
    state: RuntimeState
    limiter_action: LimiterAction = LimiterAction.NONE
    limiter_index: int = 0
    # The extension counters belong to the event model. A corrupt-state clear
    # resets those counters without overwriting the base actuator state.
    reset_event_instrumentation: bool = False


def speed_source_ready(inputs):
    return (_integer(inputs.hcan1_state, 0, 255)
            and _integer(inputs.port_input_state, 0, 255)
            and bool(inputs.hcan1_state & HCAN1_INITIALIZED_MASK)
            and bool(inputs.port_input_state & PL4_READY_MASK))


def speed_value_valid(inputs):
    # The decoded speed has no validity flag: the stock decoder maps the
    # invalid wire word FFFF to zero. A real zero remains admissible.
    return (_integer(inputs.speed_wire_word, 0, 0xFFFE)
            and _integer(inputs.speed, 0, 65535))


def _speed_usable(inputs, calibration):
    return (speed_value_valid(inputs) and speed_source_ready(inputs)
            and _integer(inputs.speed, 0, 65535)
            and _integer(inputs.speed_frame_age, 0, calibration.speed_frame_age_limit))


def _sample(state, inputs, calibration):
    valid = calibration.is_valid()
    speed_valid = speed_value_valid(inputs)
    ready = speed_source_ready(inputs)
    age_ok = valid and _integer(inputs.speed_frame_age, 0, calibration.speed_frame_age_limit)
    captured = bool(state.input_status & 16)
    capture = state.cancel_speed_capture
    if inputs.button != BUTTON_CANCEL:
        captured, capture = False, 0
    elif state.phase == Phase.IDLE and state.accepted_button != BUTTON_CANCEL:
        captured = valid and speed_valid and ready and age_ok
        capture = inputs.speed if captured else 0
    status = (int(speed_valid) | (int(age_ok) << 1) | (int(ready) << 2)
              | (int(_integer(inputs.rpm_native, 0, 32767)) << 3)
              | (int(captured) << 4))
    return replace(state, input_status=status, cancel_speed_capture=capture,
                   accepted_button=inputs.button, speed_age=inputs.speed_frame_age,
                   rpm_sample_native=inputs.rpm_native, speed_sample=inputs.speed)


def evaluate_gates(inputs, calibration, target_speed=None, *,
                   regulator_kind=RegulatorKind.SPEED, capture_valid=True):
    """Publish all satisfied gates and preserve the first failure by priority."""
    flags, reason = Flag(0), AbortReason.NONE

    def gate(condition, flag, failure):
        nonlocal flags, reason
        if condition:
            flags |= flag
        elif reason == AbortReason.NONE:
            reason = failure

    valid = calibration.is_valid()
    index_valid = _integer(inputs.active_index, 0, 4)
    gate(valid, Flag.CONFIG_VALID, AbortReason.CONFIG_INVALID)
    gate(index_valid, Flag(0), AbortReason.MAP_INDEX_INVALID)
    gate(valid and index_valid and calibration.enabled_for(inputs.active_index),
         Flag.MAP_ENABLED, AbortReason.MAP_DISABLED)
    gate(not any((inputs.selector_phase, inputs.selection_count, inputs.selector_elapsed)),
         Flag.SELECTOR_IDLE, AbortReason.SELECTOR_BUSY)
    gate(not any((inputs.feedback_pulses, inputs.feedback_phase, inputs.feedback_ticks,
                  inputs.feedback_reserved)), Flag.FEEDBACK_IDLE, AbortReason.FEEDBACK_BUSY)
    gate(not inputs.ascd_status & MAIN_PRESSED_MASK, Flag.MAIN_RELEASED, AbortReason.MAIN_PRESSED)
    gate(inputs.button == BUTTON_CANCEL, Flag.BUTTON_HELD, AbortReason.BUTTON_INVALID)
    gate(speed_source_ready(inputs), Flag(0), AbortReason.SPEED_SOURCE_NOT_READY)
    gate(speed_value_valid(inputs),
         Flag(0), AbortReason.SPEED_VALUE_INVALID)
    gate(valid and _integer(inputs.speed_frame_age, 0, calibration.speed_frame_age_limit),
         Flag(0), AbortReason.SPEED_FRAME_STALE)
    gate(capture_valid, Flag(0), AbortReason.CANCEL_CAPTURE_INVALID)
    if valid and _speed_usable(inputs, calibration):
        flags |= Flag.SPEED_FRAME_OK
    if regulator_kind == RegulatorKind.RPM:
        flags |= Flag.SPEED_OK
    else:
        low = valid and (not calibration.min_speed or inputs.speed >= calibration.min_speed)
        high = valid and (not calibration.max_speed or inputs.speed <= calibration.max_speed)
        if target_speed is None:
            gate(low, Flag(0), AbortReason.SPEED_LOW)
            gate(high, Flag(0), AbortReason.SPEED_HIGH)
        else:
            error = inputs.speed - target_speed
            high = valid and error <= calibration.abort_above
            low = valid and error >= -calibration.abort_below
            gate(high, Flag(0), AbortReason.SPEED_ABOVE_WINDOW)
            gate(low, Flag(0), AbortReason.SPEED_BELOW_WINDOW)
        if low and high:
            flags |= Flag.SPEED_OK
    gate(_integer(inputs.rpm_native, 0, 32767), Flag(0), AbortReason.RPM_INPUT_INVALID)
    gate(valid and _integer(inputs.rpm_native, calibration.min_rpm_native, 32767),
         Flag.RPM_OK, AbortReason.RPM_LOW)
    gate(valid and _integer(inputs.pedal, calibration.min_pedal, 65535),
         Flag.PEDAL_OK, AbortReason.PEDAL_LOW)
    gate(valid and _integer(inputs.coolant, calibration.coolant_min, calibration.coolant_max),
         Flag.COOLANT_OK, AbortReason.COOLANT_OUTSIDE)
    gate(valid, Flag.TIMER_OK, AbortReason.CONFIG_INVALID)
    return flags, reason


def proportional_fraction(error, calibration):
    return _clamp((calibration.window_top-error) * U_ONE // calibration.window_width, 0, U_ONE)


def update_integrator(integrator, proportional, error, calibration, gain):
    delta = -gain * error
    total = proportional + (integrator >> INTEGRATOR_SHIFT)
    if (total <= 0 and delta < 0) or (total >= U_ONE and delta > 0):
        delta = 0
    limit = calibration.integrator_limit << INTEGRATOR_SHIFT
    return _clamp(integrator + delta, -limit, limit)


def rpm_fraction(error, width):
    """Return firing permissions; zero width is a hard two-step boundary."""
    if not _integer(error, -32768, 32767) or not _integer(width, 0, 32767):
        raise ValueError("invalid RPM error or soft width")
    if error >= 0:
        return 0
    if width == 0 or error <= -width:
        return U_ONE
    return -error * U_ONE // width


def cut_fraction(torque_fraction, efficiency):
    if not _integer(torque_fraction, 0, U_ONE) or not _integer(efficiency, 1, U_ONE):
        raise ValueError("invalid torque fraction or efficiency")
    return U_ONE - min(U_ONE, U_ONE * torque_fraction // efficiency)


def actuation(kind, law_output, applied_trim, table, ready):
    """Calculate q without selecting or claiming physical delivery."""
    if not _integer(law_output, 0, U_ONE):
        raise ValueError("invalid controller output")
    efficiency = table.at(applied_trim)
    if not ready:
        return 0
    if kind == RegulatorKind.RPM:
        return U_ONE - law_output
    if kind == RegulatorKind.SPEED:
        return cut_fraction(law_output, efficiency)
    raise ValueError("invalid active regulator kind")


def ignition_command(state, stock_command, calibration, apc_fallback):
    stock_command &= 255
    if (state.phase != Phase.ACTIVE or state.active_mode_snapshot != Mode.HOLD
            or apc_fallback or not _integer(state.active_index_snapshot, 0, 4)):
        return stock_command
    slot = calibration.slot(state.active_index_snapshot)
    return max(stock_command, min(stock_command + state.active_max_trim, slot.floor_command))


def _publish_actuation(state, table):
    ready = (state.actuation_ready and state.phase == Phase.ACTIVE
             and state.active_mode_snapshot == Mode.HOLD)
    return replace(state, actuation_ready=ready, applied_efficiency=table.at(state.applied_trim),
                   cut_fraction=actuation(state.regulator_kind, state.law_output,
                                          state.applied_trim, table, ready))


def ignition_step(state, stock_command, calibration, table, *, apc_fallback=False):
    """Publish one effective command for both schedulers and diagnostics."""
    if (not _state_is_structurally_valid(state)
            or not (state.flags & Flag.CONFIG_VALID)):
        return replace(state, stock_command=stock_command & 255,
                       effective_command=stock_command & 255, applied_trim=0,
                       applied_efficiency=U_ONE, actuation_ready=False, cut_fraction=0)
    command = ignition_command(state, stock_command, calibration, apc_fallback)
    ready = (state.phase == Phase.ACTIVE and state.active_mode_snapshot == Mode.HOLD
             and not apc_fallback and _integer(state.active_index_snapshot, 0, 4))
    return _publish_actuation(replace(state, stock_command=stock_command & 255,
        effective_command=command, applied_trim=command-(stock_command & 255),
        actuation_ready=ready), table)


def _publish_active(state, flags, inputs, calibration, table):
    slot = calibration.slot(state.active_index_snapshot)
    if state.regulator_kind == RegulatorKind.RPM:
        error = inputs.rpm_native-state.target_rpm_native
        state = replace(state, rpm_error_native=error, control_error=error,
                        law_output=rpm_fraction(error, slot.launch_soft_width_native),
                        speed_error=0, integrator=0, torque_command=0, torque_fraction=0)
    else:
        error = inputs.speed-state.target_speed
        proportional = proportional_fraction(error, calibration)
        integral = update_integrator(state.integrator, proportional, error, calibration, slot.integral_gain)
        command = _clamp(proportional + (integral >> INTEGRATOR_SHIFT), 0, U_ONE)
        output = _clamp(command, state.torque_fraction-calibration.u_rate_limit,
                        state.torque_fraction+calibration.u_rate_limit)
        state = replace(state, speed_error=error, control_error=error, integrator=integral,
                        torque_command=command, torque_fraction=output, law_output=output)
    flags |= Flag.ACTIVE
    if state.active_mode_snapshot == Mode.HOLD:
        flags |= Flag.HOLD
    return _publish_actuation(replace(state, flags=flags), table)


def _state_is_structurally_valid(state):
    try:
        phase = Phase(state.phase)
        mode = Mode(state.active_mode_snapshot)
        kind = RegulatorKind(state.regulator_kind)
        AbortReason(state.abort_reason)
    except (TypeError, ValueError):
        return False
    words = (state.run_ticks, state.rearm_ticks, state.captured_rpm_native,
             state.target_speed, state.target_rpm_native, state.rpm_sample_native,
             state.speed_sample, state.cancel_speed_capture, state.selected_target)
    if (not _integer(state.active_index_snapshot, 0, 4)
            or not all(_integer(x, 0, 65535) for x in words)
            or not all(_integer(x, -32768, 32767) for x in (
                state.speed_error, state.rpm_error_native, state.integrator, state.control_error))
            or not all(_integer(x, 0, U_ONE) for x in (
                state.torque_fraction, state.torque_command, state.cut_fraction, state.law_output))
            or not _integer(state.applied_trim, 0, TRIM_MAX)
            or not _integer(state.active_max_trim, 0, TRIM_MAX)
            or not _integer(state.applied_efficiency, 1, U_ONE)
            or not all(_integer(x, 0, 255) for x in (
                state.stock_command, state.effective_command, state.accepted_button, state.speed_age))
            or not _integer(state.input_status, 0, 31)
            or not isinstance(state.actuation_ready, bool)
            or not _integer(state.flags, 0, 65535)
            or int(state.flags) & ~VALID_FLAGS):
        return False
    if state.effective_command-state.stock_command != state.applied_trim:
        return False
    if not state.actuation_ready and state.cut_fraction != 0:
        return False
    if phase == Phase.IDLE:
        return (mode == Mode.OBSERVE and kind == RegulatorKind.NONE
                and not state.run_ticks and not state.rearm_ticks
                and not state.actuation_ready and state.active_max_trim == 0)
    if phase == Phase.COOLDOWN:
        return state.rearm_ticks <= 32767 and not state.actuation_ready and state.cut_fraction == 0
    if kind == RegulatorKind.NONE or state.rearm_ticks or state.run_ticks > 32767:
        return False
    if mode != Mode.HOLD and state.actuation_ready:
        return False
    if state.actuation_ready:
        if state.applied_trim > state.active_max_trim:
            return False
        expected = (1000-state.law_output if kind == RegulatorKind.RPM
                    else cut_fraction(state.law_output, state.applied_efficiency))
        if state.cut_fraction != expected:
            return False
    if kind == RegulatorKind.RPM:
        return (1 <= state.target_rpm_native <= 32767
                and state.selected_target == state.target_rpm_native
                and not any((state.target_speed, state.torque_fraction, state.speed_error,
                             state.integrator, state.torque_command))
                and state.control_error == state.rpm_error_native)
    return (state.selected_target == state.target_speed
            and not any((state.target_rpm_native, state.rpm_error_native))
            and state.control_error == state.speed_error
            and state.law_output == state.torque_fraction)


def _abort_active(state, flags, reason):
    return StepResult(replace(state, phase=Phase.COOLDOWN, abort_reason=reason,
                              flags=flags & ~ACTIVE_OUTPUT_FLAGS, rearm_ticks=0,
                              actuation_ready=False, cut_fraction=0))


def engine_step(state, inputs, calibration, table):
    """Advance one tick, preserving the speed captured on an accepted CANCEL edge."""
    if not _state_is_structurally_valid(state):
        return StepResult(RuntimeState(phase=Phase.COOLDOWN, abort_reason=AbortReason.STATE_CORRUPT),
                          LimiterAction.RESTORE_MAP_1, 0, True)
    state = _sample(state, inputs, calibration)
    if state.phase == Phase.COOLDOWN:
        if not calibration.is_valid() or not table.is_valid():
            return StepResult(replace(state, abort_reason=AbortReason.CONFIG_INVALID,
                                      flags=Flag(0), rearm_ticks=0))
        if inputs.button != BUTTON_RELEASED:
            return StepResult(replace(state, rearm_ticks=0))
        ticks = state.rearm_ticks + 1
        if ticks < calibration.rearm_ticks:
            return StepResult(replace(state, rearm_ticks=ticks))
        return StepResult(replace(state, phase=Phase.IDLE, flags=Flag(0),
                                  active_mode_snapshot=Mode.OBSERVE,
                                  regulator_kind=RegulatorKind.NONE, active_max_trim=0,
                                  run_ticks=0, rearm_ticks=0))
    kind = state.regulator_kind
    target = state.target_speed
    if state.phase == Phase.IDLE:
        kind = RegulatorKind.NONE
        if calibration.is_valid() and _integer(inputs.active_index, 0, 4):
            slot = calibration.slot(inputs.active_index)
            kind = RegulatorKind.RPM if inputs.speed < slot.launch_speed_threshold else RegulatorKind.SPEED
        target = (_clamp(state.cancel_speed_capture + calibration.target_speed_offset, 0, 65535)
                  if calibration.is_valid() else 0)
    flags, reason = evaluate_gates(inputs, calibration,
                                  target if state.phase == Phase.ACTIVE and kind == RegulatorKind.SPEED else None,
                                  regulator_kind=kind, capture_valid=bool(state.input_status & 16))
    if not table.is_valid():
        flags &= ~Flag.CONFIG_VALID
        reason = AbortReason.CONFIG_INVALID
    if state.phase == Phase.IDLE:
        state = replace(state, flags=flags, abort_reason=reason)
        if reason == AbortReason.NONE and kind == RegulatorKind.SPEED:
            error = inputs.speed-target
            if error > calibration.abort_above:
                reason = AbortReason.SPEED_ABOVE_WINDOW
            elif error < -calibration.abort_below:
                reason = AbortReason.SPEED_BELOW_WINDOW
            if reason != AbortReason.NONE:
                state = replace(state, abort_reason=reason, flags=flags & ~Flag.SPEED_OK)
        if reason != AbortReason.NONE:
            return StepResult(state)
        rpm = calibration.slot(inputs.active_index).launch_rpm_native if kind == RegulatorKind.RPM else 0
        slot = calibration.slot(inputs.active_index)
        trim = slot.max_trim_rpm if kind == RegulatorKind.RPM else slot.max_trim_speed
        active = replace(state, phase=Phase.ACTIVE, active_index_snapshot=inputs.active_index,
                         active_mode_snapshot=Mode(calibration.mode), regulator_kind=kind,
                         captured_rpm_native=inputs.rpm_native,
                         target_speed=target if kind == RegulatorKind.SPEED else 0,
                         target_rpm_native=rpm, selected_target=rpm if kind == RegulatorKind.RPM else target,
                         torque_fraction=U_ONE if kind == RegulatorKind.SPEED else 0,
                         integrator=0, speed_error=0, rpm_error_native=0, torque_command=0,
                         run_ticks=0, rearm_ticks=0, actuation_ready=False, cut_fraction=0)
        active = replace(active, active_max_trim=trim)
        return StepResult(_publish_active(active, flags, inputs, calibration, table))
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
    ticks = state.run_ticks + 1
    if ticks >= calibration.run_timeout_ticks:
        return _abort_active(state, flags & ~Flag.TIMER_OK, AbortReason.TIMEOUT)
    return StepResult(_publish_active(replace(state, run_ticks=ticks, abort_reason=AbortReason.NONE),
                                      flags, inputs, calibration, table))


def step(state, inputs, calibration, table):
    """Public periodic-step alias; the derived table must be explicit."""
    return engine_step(state, inputs, calibration, table)


def apply_dashboard_feedback(state, serialized_status, *, map_feedback_active=False):
    if not _integer(serialized_status, 0, 255):
        raise ValueError("serialized ASCD status must fit in one byte")
    if map_feedback_active:
        return serialized_status
    if state.phase == Phase.ACTIVE:
        value = ASCD_FEEDBACK_CRUISE_SET
    elif state.phase == Phase.COOLDOWN:
        value = ASCD_FEEDBACK_OFF
    elif state.phase == Phase.IDLE and state.abort_reason != AbortReason.NONE and state.flags & Flag.BUTTON_HELD:
        value = ASCD_FEEDBACK_CRUISE
    else:
        return serialized_status
    return (serialized_status & ~ASCD_FEEDBACK_MASK) | value


SPARK_CYLINDER_COUNT = 6
SPARK_CUT_ONE = 6 * U_ONE
SPARK_CYLINDER_OFFSETS = (250, 2250, 4250, 1250, 3250, 5250)
MISFIRE_MARKER = 1
MISFIRE_CALIBRATION_ADDRESS = 0x00008C2E
MISFIRE_RELEASE_EVENTS = 14
QUIET_EVENTS_MAX = 255


@dataclass(frozen=True)
class SparkEvent:
    """Eligibility is an input, not a claim about the veto delivery point."""
    armed: bool = True
    eligible: bool = True
    cylinder: int = 1
    misfire_latch: int = 0


@dataclass(frozen=True)
class SparkCutState:
    quiet_events: int = 0
    cut_count: int = 0
    accumulators: tuple[int, ...] = (0,) * 6
    consumed_q_sum: int = 0
    eligible_event_counter: int = 0


@dataclass(frozen=True)
class SparkResult:
    state: SparkCutState
    cut_requested: bool
    misfire_latch: int


def spark_event(runtime, cut, event):
    """Select a cut and integrate the one q sample consumed by the event."""
    if not event.armed:
        return SparkResult(cut, False, event.misfire_latch)
    active = runtime.phase == Phase.ACTIVE
    hold = active and runtime.active_mode_snapshot == Mode.HOLD
    quiet = 0 if active else min(cut.quiet_events+1, QUIET_EVENTS_MAX)
    latch = event.misfire_latch
    if hold and latch == 0:
        latch = MISFIRE_MARKER
    elif runtime.phase == Phase.IDLE and latch == MISFIRE_MARKER and quiet >= MISFIRE_RELEASE_EVENTS:
        latch = 0
    cut = replace(cut, quiet_events=quiet)
    reset = replace(cut, accumulators=SPARK_CYLINDER_OFFSETS)
    if not hold or not _integer(runtime.cut_fraction, 0, U_ONE):
        return SparkResult(reset, False, latch)
    if not event.eligible or not _integer(event.cylinder, 1, 6):
        return SparkResult(cut, False, latch)
    index = event.cylinder-1
    if not _integer(cut.accumulators[index], 0, SPARK_CUT_ONE-1):
        return SparkResult(reset, False, latch)
    q = runtime.cut_fraction
    accumulator = cut.accumulators[index] + 6*q
    requested = accumulator >= SPARK_CUT_ONE
    if requested:
        accumulator -= SPARK_CUT_ONE
    accumulators = list(cut.accumulators)
    accumulators[index] = accumulator
    return SparkResult(replace(
        cut, cut_count=(cut.cut_count+requested) & 255, accumulators=tuple(accumulators),
        consumed_q_sum=(cut.consumed_q_sum+q) & 0xFFFFFFFF,
        eligible_event_counter=(cut.eligible_event_counter+1) & 65535), requested, latch)


# The two blocks are separate allocations. Offset maps are shared with host
# instrumentation without making the model depend on a particular ROM layout.
BASE_STATE_FIELDS = (
    ("phase", 0x00, "B"), ("abort_reason", 0x01, "B"), ("flags", 0x02, "H"),
    ("active_index_snapshot", 0x04, "B"), ("active_mode_snapshot", 0x05, "B"),
    ("run_ticks", 0x06, "H"), ("rearm_ticks", 0x08, "H"),
    ("captured_rpm_native", 0x0A, "H"), ("target_speed", 0x0C, "H"),
    ("torque_fraction", 0x0E, "H"), ("speed_error", 0x10, "h"),
    ("integrator", 0x12, "h"), ("target_rpm_native", 0x14, "H"),
    ("torque_command", 0x16, "H"), ("rpm_error_native", 0x18, "h"),
    ("cut_fraction", 0x1A, "H"),
    ("active_max_trim", 0x1E, "B"),
)
BASE_COUNTER_FIELDS = (
    ("quiet_events", 0x1C, "B"), ("cut_counter", 0x1D, "B"),
)
BASE_ACCUMULATOR_FIELDS = tuple(
    (f"accumulator_{index+1}", 0x20 + 2*index, "H")
    for index in range(SPARK_CYLINDER_COUNT)
)
BASE_RESERVED_FIELDS = (("reserved_1f", 0x1F, "B"),)
# Runtime-owned bytes beyond the contiguous engine prefix need an extra clear.
ENGINE_EXTRA_CLEAR_OFFSETS = tuple(
    offset for _name, offset, _fmt in BASE_STATE_FIELDS
    if offset >= ENGINE_STATE_SIZE
)
EXTENSION_FIELDS = (
    ("regulator_kind", 0x00, "B"), ("input_status", 0x01, "B"),
    ("control_error", 0x02, "h"), ("rpm_sample_native", 0x04, "H"),
    ("speed_sample", 0x06, "H"), ("stock_command", 0x08, "B"),
    ("effective_command", 0x09, "B"), ("applied_trim", 0x0A, "B"),
    ("actuation_ready", 0x0B, "B"), ("applied_efficiency", 0x0C, "H"),
    ("accepted_button", 0x14, "B"), ("speed_age", 0x15, "B"),
    ("law_output", 0x16, "H"), ("cancel_speed_capture", 0x1A, "H"),
    ("selected_target", 0x1C, "H"),
)
EXTENSION_VIEW_FIELDS = (
    ("wire_efficiency", 0x0E, "H"), ("consumed_q_sum", 0x10, "I"),
    ("eligible_event_counter", 0x18, "H"),
    ("wire_mode_trim", 0x1E, "B"), ("wire_status", 0x1F, "B"),
)
EXTENSION_EVENT_FIELD_NAMES = frozenset(("consumed_q_sum", "eligible_event_counter"))
STATE_FIELDS = {
    "base": (BASE_STATE_FIELDS + BASE_COUNTER_FIELDS
             + BASE_ACCUMULATOR_FIELDS + BASE_RESERVED_FIELDS),
    "extension": EXTENSION_FIELDS + EXTENSION_VIEW_FIELDS,
}


def _pack_fields(buffer, fields, values):
    for name, offset, fmt in fields:
        struct.pack_into(">"+fmt, buffer, offset, values[name])


def _unpack_fields(buffer, fields):
    return {name: struct.unpack_from(">"+fmt, buffer, offset)[0]
            for name, offset, fmt in fields}


def encode_state(runtime, spark):
    """Return the exact base and extension records, with no padding aliases."""
    if not _state_is_structurally_valid(runtime):
        raise ValueError("invalid runtime state")
    base, extension = bytearray(STATE_SIZE), bytearray(EXTENSION_SIZE)
    for fields, buffer in ((BASE_STATE_FIELDS, base), (EXTENSION_FIELDS, extension)):
        _pack_fields(buffer, fields, {name: getattr(runtime, name) for name, _offset, _fmt in fields})
    _pack_fields(base, BASE_COUNTER_FIELDS,
                 {"quiet_events": spark.quiet_events, "cut_counter": spark.cut_count})
    if len(spark.accumulators) != len(BASE_ACCUMULATOR_FIELDS):
        raise ValueError("actuator state must contain six accumulators")
    _pack_fields(base, BASE_ACCUMULATOR_FIELDS,
                 {name: value for (name, _offset, _fmt), value
                  in zip(BASE_ACCUMULATOR_FIELDS, spark.accumulators)})
    _pack_fields(base, BASE_RESERVED_FIELDS,
                 {name: 0 for name, _offset, _fmt in BASE_RESERVED_FIELDS})
    _pack_fields(extension, EXTENSION_VIEW_FIELDS,
                 {name: getattr(spark if name in EXTENSION_EVENT_FIELD_NAMES else runtime, name)
                  for name, _offset, _fmt in EXTENSION_VIEW_FIELDS})
    return bytes(base), bytes(extension)


def decode_state(base, extension):
    if len(base) != STATE_SIZE or len(extension) != EXTENSION_SIZE:
        raise ValueError("runtime records must contain 44 and 32 bytes")
    values = {}
    for fields, buffer in ((BASE_STATE_FIELDS, base), (EXTENSION_FIELDS, extension)):
        values.update(_unpack_fields(buffer, fields))
    if values["actuation_ready"] not in (0, 1):
        raise ValueError("invalid actuation-ready byte")
    values["actuation_ready"] = bool(values["actuation_ready"])
    runtime = RuntimeState(**values)
    counters = _unpack_fields(base, BASE_COUNTER_FIELDS)
    accumulator_values = _unpack_fields(base, BASE_ACCUMULATOR_FIELDS)
    reserved = _unpack_fields(base, BASE_RESERVED_FIELDS)
    views = _unpack_fields(extension, EXTENSION_VIEW_FIELDS)
    if (any(reserved.values()) or not _state_is_structurally_valid(runtime)
            or any(value != getattr(runtime, name) for name, value in views.items()
                   if name not in EXTENSION_EVENT_FIELD_NAMES)):
        raise ValueError("invalid runtime record or derived wire view")
    spark = SparkCutState(
        quiet_events=counters["quiet_events"], cut_count=counters["cut_counter"],
        accumulators=tuple(accumulator_values[name] for name, _offset, _fmt in BASE_ACCUMULATOR_FIELDS),
        consumed_q_sum=views["consumed_q_sum"],
        eligible_event_counter=views["eligible_event_counter"],
    )
    return runtime, spark
