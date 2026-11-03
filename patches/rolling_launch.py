#!/usr/bin/env python3
"""Reference contract for the exact JK08A Rolling Launch runtime.

The model is intentionally independent from the SH-2E implementation. It
defines fail-closed calibration validation, gate ordering, the vehicle-speed
capture, the windowed torque-fraction controller, the latched RPM ceiling
request and its merge into the stock cylinder mask, cooldown/rearm
behavior, the per-map ignition trim with its cut compensation, and the
spark-handler cut actuator with its misfire-monitor latch.
It never reads or writes a ROM image.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import IntEnum, IntFlag
import struct


CONFIG_MAGIC = 0x524C
CONFIG_MAGIC_INVERSE = CONFIG_MAGIC ^ 0xFFFF
CONFIG_END_MARKER = 0xA55A
CONFIG_SCHEMA_VERSION = 5
# The record holds a 40-byte head, five 6-byte map slots, and an end marker.
CONFIG_HEAD_FORMAT = ">H6B4HhBB3H2B3H2B2H"
SLOT_FORMAT = ">hBBH"
SLOT_COUNT = 5
SLOT_OFFSET = 0x28
CONFIG_FORMAT = CONFIG_HEAD_FORMAT + SLOT_FORMAT[1:] * SLOT_COUNT + "H"
CONFIG_SIZE = struct.calcsize(CONFIG_FORMAT)
# The schema 4 record is the head alone with the integral gain at +0x16.
LEGACY_SCHEMA_VERSION = 4
LEGACY_CONFIG_SIZE = struct.calcsize(CONFIG_HEAD_FORMAT)
# The largest ignition trim: the end of the stock torque-efficiency axis.
TRIM_MAX = 40
# The engine owns the first 28 bytes of the state record, which end with the
# RPM ceiling latch word and a reserved word. The spark-handler wrapper alone
# writes the 16 actuator bytes that follow.
ENGINE_STATE_SIZE = 28
STATE_SIZE = 44

# The torque fraction u and its integrator are expressed in thousandths.
U_ONE = 1000
# The integrator holds sixteenths of one u count.
INTEGRATOR_SHIFT = 4
# The stock receive age saturates at 255, so a larger limit never expires.
SPEED_FRAME_AGE_LIMIT_MAX = 254

BUTTON_RELEASED = 0x20
BUTTON_CANCEL = 0x02
BUTTON_SET = 0x08
MAIN_PRESSED_MASK = 0x80
FUEL_CUT_ACTIVE_MASK = 0x04
FUEL_CUT_CYLINDER_MASK = 0x3F
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
    FUEL_CUT = 1 << 13
    HOLD = 1 << 14
    CEILING = 1 << 15


ACTIVE_OUTPUT_FLAGS = Flag.ACTIVE | Flag.FUEL_CUT | Flag.HOLD | Flag.CEILING


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


class LimiterAction(IntEnum):
    NONE = 0
    RESTORE_MAP_1 = 1


def _clamp(value, low, high):
    return min(high, max(low, value))


@dataclass(frozen=True)
class Slot:
    """Per-map hold settings.

    max_trim is the ignition trim z in APC command degrees, floor_command the
    latest command that the trim may reach, and trim_efficiency the torque
    efficiency e(z) of the trim in thousandths, from the stock table F of the
    map: e = (256 - F(z)) * 1000 // 256. A zero trim requires e = 1000.
    """

    integral_gain: int = 0
    max_trim: int = 0
    floor_command: int = 0
    trim_efficiency: int = 1000

    def is_valid(self):
        return all((
            0 <= self.integral_gain <= 0x7FFF,
            0 <= self.max_trim <= TRIM_MAX,
            0 <= self.floor_command <= 0xFF,
            0 < self.trim_efficiency <= U_ONE,
            self.max_trim != 0 or self.trim_efficiency == U_ONE,
        ))


def trim_efficiency(table_value):
    """Return e in thousandths for a stock F value of 0..255."""
    if not 0 <= table_value <= 0xFF:
        raise ValueError("F value lies outside one byte")
    return (256 - table_value) * U_ONE // 256


@dataclass(frozen=True)
class Calibration:
    mode: Mode = Mode.OBSERVE
    enable_mask: int = 0
    options: Option = Option.NONE
    coolant_min: int = 0
    coolant_max: int = 0xFF
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
    rpm_ceiling_offset_native: int = 80
    run_timeout_ticks: int = 781
    rearm_ticks: int = 98
    speed_frame_age_limit: int = 10
    rpm_ceiling_hysteresis_native: int = 8
    magic: int = CONFIG_MAGIC
    schema_version: int = CONFIG_SCHEMA_VERSION
    magic_inverse: int = CONFIG_MAGIC_INVERSE
    end_marker: int = CONFIG_END_MARKER
    slots: tuple[Slot, ...] = (Slot(),) * SLOT_COUNT
    slot_end_marker: int = CONFIG_END_MARKER

    def slot(self, index):
        return self.slots[index]

    def is_valid(self):
        try:
            Mode(self.mode)
            options = Option(self.options)
        except ValueError:
            return False
        return all((
            self.magic == CONFIG_MAGIC,
            self.schema_version == CONFIG_SCHEMA_VERSION,
            0 <= self.enable_mask <= 0x1F,
            options == Option.NONE,
            0 <= self.coolant_min <= self.coolant_max <= 0xFF,
            0 <= self.min_speed <= 0xFFFF,
            0 <= self.max_speed <= 0xFFFF,
            self.min_speed == 0
            or self.max_speed == 0
            or self.min_speed <= self.max_speed,
            0 < self.min_rpm_native <= 0xFFFF,
            0 <= self.min_pedal <= 0xFFFF,
            0 < self.abort_above <= 0xFF,
            0 < self.abort_below <= 0xFF,
            -self.abort_above < self.target_speed_offset < self.abort_below,
            0 < self.window_width <= 0xFF,
            0 <= self.window_top <= 0xFF,
            0 < self.u_rate_limit <= U_ONE,
            self.reserved == 0,
            0 <= self.integrator_limit <= U_ONE,
            0 < self.rpm_ceiling_offset_native <= 0xFFFF,
            0 < self.run_timeout_ticks <= 0x7FFF,
            0 < self.rearm_ticks <= 0x7FFF,
            0 < self.speed_frame_age_limit <= SPEED_FRAME_AGE_LIMIT_MAX,
            0 < self.rpm_ceiling_hysteresis_native <= 0xFF,
            self.rpm_ceiling_hysteresis_native
            <= self.rpm_ceiling_offset_native,
            self.magic_inverse == CONFIG_MAGIC_INVERSE,
            self.end_marker == CONFIG_END_MARKER,
            len(self.slots) == SLOT_COUNT,
            all(
                isinstance(slot, Slot) and slot.is_valid()
                for slot in self.slots
            ),
            self.slot_end_marker == CONFIG_END_MARKER,
        ))

    def enabled_for(self, index):
        return 0 <= index < SLOT_COUNT and bool(
            self.enable_mask & (1 << index)
        )

    def to_bytes(self):
        data = struct.pack(
            CONFIG_FORMAT,
            self.magic,
            self.schema_version,
            int(self.mode),
            self.enable_mask,
            int(self.options),
            self.coolant_min,
            self.coolant_max,
            self.min_speed,
            self.max_speed,
            self.min_rpm_native,
            self.min_pedal,
            self.target_speed_offset,
            self.window_width,
            self.window_top,
            self.u_rate_limit,
            self.reserved,
            self.integrator_limit,
            self.abort_above,
            self.abort_below,
            self.rpm_ceiling_offset_native,
            self.run_timeout_ticks,
            self.rearm_ticks,
            self.speed_frame_age_limit,
            self.rpm_ceiling_hysteresis_native,
            self.magic_inverse,
            self.end_marker,
            *(
                value
                for slot in self.slots
                for value in (
                    slot.integral_gain,
                    slot.max_trim,
                    slot.floor_command,
                    slot.trim_efficiency,
                )
            ),
            self.slot_end_marker,
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
        values = struct.unpack(CONFIG_FORMAT, data)
        slots = tuple(
            Slot(*values[26 + 4 * index : 30 + 4 * index])
            for index in range(SLOT_COUNT)
        )
        return cls(
            magic=values[0],
            schema_version=values[1],
            mode=values[2],
            enable_mask=values[3],
            options=values[4],
            coolant_min=values[5],
            coolant_max=values[6],
            min_speed=values[7],
            max_speed=values[8],
            min_rpm_native=values[9],
            min_pedal=values[10],
            target_speed_offset=values[11],
            window_width=values[12],
            window_top=values[13],
            u_rate_limit=values[14],
            reserved=values[15],
            integrator_limit=values[16],
            abort_above=values[17],
            abort_below=values[18],
            rpm_ceiling_offset_native=values[19],
            run_timeout_ticks=values[20],
            rearm_ticks=values[21],
            speed_frame_age_limit=values[22],
            rpm_ceiling_hysteresis_native=values[23],
            magic_inverse=values[24],
            end_marker=values[25],
            slots=slots,
            slot_end_marker=values[-1],
        )

    @classmethod
    def from_legacy_bytes(cls, data):
        """Return the schema 5 equivalent of a valid schema 4 record.

        Every slot takes the single integral gain of the record and no trim.
        """
        if len(data) != LEGACY_CONFIG_SIZE:
            raise ValueError(
                f"schema 4 configuration is {len(data)} bytes, expected "
                f"{LEGACY_CONFIG_SIZE}"
            )
        values = struct.unpack(CONFIG_HEAD_FORMAT, data)
        if values[1] != LEGACY_SCHEMA_VERSION:
            raise ValueError("configuration is not schema 4")
        slot = Slot(integral_gain=values[15])
        head = bytearray(data)
        head[2] = CONFIG_SCHEMA_VERSION
        head[0x16:0x18] = bytes(2)
        calibration = cls.from_bytes(
            bytes(head)
            + bytes(SLOT_COUNT * struct.calcsize(SLOT_FORMAT))
            + CONFIG_END_MARKER.to_bytes(2, "big")
        )
        calibration = replace(calibration, slots=(slot,) * SLOT_COUNT)
        if not calibration.is_valid():
            raise ValueError("schema 4 configuration is invalid")
        return calibration


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
    target_speed: int = 0
    torque_fraction: int = 0
    speed_error: int = 0
    integrator: int = 0
    fuel_cut_request: int = 0
    torque_command: int = 0
    ceiling_latch: int = 0
    cut_fraction: int = 0


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


def evaluate_gates(inputs, calibration, target_speed=None):
    """Return all satisfied gate flags and the first failure by priority.

    IDLE passes ``target_speed=None`` and checks the activation speed range.
    ACTIVE passes the captured target and checks the speed-error window.
    """
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
        not inputs.ascd_status & MAIN_PRESSED_MASK,
        Flag.MAIN_RELEASED,
        AbortReason.MAIN_PRESSED,
    )
    gate(
        inputs.button == BUTTON_CANCEL,
        Flag.BUTTON_HELD,
        AbortReason.BUTTON_INVALID,
    )
    gate(
        valid and inputs.speed_frame_age <= calibration.speed_frame_age_limit,
        Flag.SPEED_FRAME_OK,
        AbortReason.SPEED_FRAME_STALE,
    )
    if target_speed is None:
        low_ok = valid and (
            calibration.min_speed == 0 or inputs.speed >= calibration.min_speed
        )
        high_ok = valid and (
            calibration.max_speed == 0 or inputs.speed <= calibration.max_speed
        )
        gate(low_ok, Flag(0), AbortReason.SPEED_LOW)
        gate(high_ok, Flag(0), AbortReason.SPEED_HIGH)
    else:
        error = inputs.speed - target_speed
        high_ok = valid and error <= calibration.abort_above
        low_ok = valid and error >= -calibration.abort_below
        gate(high_ok, Flag(0), AbortReason.SPEED_ABOVE_WINDOW)
        gate(low_ok, Flag(0), AbortReason.SPEED_BELOW_WINDOW)
    if low_ok and high_ok:
        flags |= Flag.SPEED_OK
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


def proportional_fraction(error, calibration):
    """Return u_p = clamp((W_top - e) / W, 0, 1) in thousandths."""
    numerator = calibration.window_top - error
    if numerator <= 0:
        return 0
    if numerator >= calibration.window_width:
        return U_ONE
    return numerator * U_ONE // calibration.window_width


def update_integrator(integrator, proportional, error, calibration, gain):
    """Advance the integrator unless the step deepens a saturated sum.

    The integrator falls while the speed is above target and rises while it
    is below, at the integral gain of the map slot. The result is always
    bounded by the configured limit.
    """
    step = -(gain * error)
    total = proportional + (integrator >> INTEGRATOR_SHIFT)
    if (total <= 0 and step < 0) or (total >= U_ONE and step > 0):
        step = 0
    bound = calibration.integrator_limit << INTEGRATOR_SHIFT
    return _clamp(integrator + step, -bound, bound)


def rpm_ceiling(state, calibration):
    """Return the cut and restore sums of the RPM ceiling latch.

    The cut sum is the captured RPM plus the ceiling offset; the restore sum
    lies the hysteresis below it. Both are exact integers, as in the 32-bit
    runtime sums, so a high captured RPM never wraps below either threshold.
    """
    cut = state.captured_rpm_native + calibration.rpm_ceiling_offset_native
    return cut, cut - calibration.rpm_ceiling_hysteresis_native


def ceiling_latch(state, rpm_native, calibration):
    """Return the next latch: set above the cut sum, held above the
    restore sum while set, and released at or below it."""
    cut, restore = rpm_ceiling(state, calibration)
    if rpm_native > cut:
        return 1
    if state.ceiling_latch and rpm_native > restore:
        return 1
    return 0


def cut_fraction(torque_fraction, efficiency):
    """Return c = 1000 - min(1000, 1000 * u / e), the share of events that
    the spark-cut actuator withholds so that the fired events, each at the
    trim efficiency e, deliver the torque fraction u."""
    if efficiency == U_ONE:
        return U_ONE - torque_fraction
    return U_ONE - min(U_ONE, U_ONE * torque_fraction // efficiency)


def ignition_command(state, stock_command, calibration, apc_fallback):
    """Return the APC command of the primary ignition consumer.

    During an ACTIVE hold of a map slot with a trim, the command retards by
    the trim and never past the floor command: max(stock, min(stock + z,
    floor)). The adapter never advances the stock command and passes it
    through outside an ACTIVE hold and during the P0335 APC fallback.
    """
    stock_command &= 0xFF
    if (
        state.phase != Phase.ACTIVE
        or state.active_mode_snapshot != Mode.HOLD
        or apc_fallback
        or not 0 <= state.active_index_snapshot < SLOT_COUNT
    ):
        return stock_command
    slot = calibration.slot(state.active_index_snapshot)
    return max(
        stock_command,
        min(stock_command + slot.max_trim, slot.floor_command),
    )


def _publish_active(state, flags, inputs, calibration):
    """Run the controller, publish the ACTIVE flags, the cut fraction, and
    the ceiling request."""
    error = inputs.speed - state.target_speed
    proportional = proportional_fraction(error, calibration)
    slot = calibration.slot(state.active_index_snapshot)
    integrator = update_integrator(
        state.integrator, proportional, error, calibration,
        slot.integral_gain,
    )
    command = _clamp(
        proportional + (integrator >> INTEGRATOR_SHIFT), 0, U_ONE
    )
    rate = calibration.u_rate_limit
    fraction = _clamp(
        command, state.torque_fraction - rate, state.torque_fraction + rate
    )
    result = flags | Flag.ACTIVE
    request = 0
    latch = 0
    if state.active_mode_snapshot == Mode.HOLD:
        result |= Flag.HOLD
        latch = ceiling_latch(state, inputs.rpm_native, calibration)
        if latch:
            request = FUEL_CUT_CYLINDER_MASK
            result |= Flag.CEILING | Flag.FUEL_CUT
    if inputs.fuel_cut_status & FUEL_CUT_ACTIVE_MASK:
        result |= Flag.FUEL_CUT
    return replace(
        state,
        flags=result,
        speed_error=error,
        integrator=integrator,
        torque_command=command,
        torque_fraction=fraction,
        fuel_cut_request=request,
        ceiling_latch=latch,
        cut_fraction=cut_fraction(fraction, slot.trim_efficiency),
    )


def apply_fuel_cut_request(stock_mask, request):
    """Return the cylinder mask that the fuel-cut wrapper leaves published.

    A request of 0x0001..0x003F is ORed into the stock coordinator result.
    Zero and any request with a bit outside the six cylinder bits leave the
    stock result unchanged.
    """
    if not 0 <= stock_mask <= 0xFF:
        raise ValueError("stock cylinder mask must fit in uint8")
    if not 0 <= request <= 0xFFFF:
        raise ValueError("fuel-cut request must fit in uint16")
    if request == 0 or request & ~FUEL_CUT_CYLINDER_MASK:
        return stock_mask
    return stock_mask | request


def apply_dashboard_feedback(
    state,
    serialized_status,
    *,
    map_feedback_active=False,
):
    """Apply the Rolling Launch ASCD field after map feedback.

    A nonzero map-feedback state has strict priority. Normal IDLE and corrupt
    Rolling Launch phases preserve the serializer result. A failed activation
    attempt is visible only while CANCEL remains held.
    """
    if not 0 <= serialized_status <= 0xFF:
        raise ValueError("serialized ASCD status must fit in one byte")
    if map_feedback_active:
        return serialized_status
    try:
        phase = Phase(state.phase)
    except ValueError:
        return serialized_status

    if phase == Phase.ACTIVE:
        value = ASCD_FEEDBACK_CRUISE_SET
    elif phase == Phase.COOLDOWN:
        value = ASCD_FEEDBACK_OFF
    elif (
        state.abort_reason != AbortReason.NONE
        and state.flags & Flag.BUTTON_HELD
    ):
        value = ASCD_FEEDBACK_CRUISE
    else:
        return serialized_status
    return (serialized_status & ~ASCD_FEEDBACK_MASK) | value


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
        state.target_speed,
        state.torque_fraction,
        state.fuel_cut_request,
        state.torque_command,
        state.cut_fraction,
    )):
        return False
    if not all(-0x8000 <= value <= 0x7FFF for value in (
        state.speed_error,
        state.integrator,
    )):
        return False
    if phase == Phase.IDLE:
        return (
            mode == Mode.OBSERVE
            and state.run_ticks == 0
            and state.rearm_ticks == 0
        )
    if phase == Phase.ACTIVE:
        return (
            state.rearm_ticks == 0
            and state.torque_fraction <= U_ONE
            and state.ceiling_latch in (0, 1)
        )
    # COOLDOWN never counts beyond the largest valid rearm period.
    return state.rearm_ticks <= 0x7FFF


def _abort_active(state, flags, reason):
    return StepResult(replace(
        state,
        phase=Phase.COOLDOWN,
        abort_reason=reason,
        flags=flags & ~ACTIVE_OUTPUT_FLAGS,
        rearm_ticks=0,
        fuel_cut_request=0,
        ceiling_latch=0,
    ))


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

    state = replace(state, fuel_cut_request=0)
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

    if phase == Phase.IDLE:
        flags, reason = evaluate_gates(inputs, calibration)
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
        target = _clamp(
            inputs.speed + calibration.target_speed_offset, 0, 0xFFFF
        )
        active = replace(
            idle,
            phase=Phase.ACTIVE,
            abort_reason=AbortReason.NONE,
            active_index_snapshot=inputs.active_index,
            active_mode_snapshot=Mode(calibration.mode),
            captured_rpm_native=inputs.rpm_native,
            target_speed=target,
            torque_fraction=U_ONE,
            integrator=0,
            ceiling_latch=0,
            cut_fraction=0,
        )
        return StepResult(_publish_active(active, flags, inputs, calibration))

    flags, reason = evaluate_gates(inputs, calibration, state.target_speed)
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
        run_ticks=run_ticks,
    )
    return StepResult(_publish_active(active, flags, inputs, calibration))


# The spark-handler actuator selects cuts with one accumulator per event
# cylinder 1..6 (0xFFFF13C9). The veto at the match of cylinder c withholds
# the dwell of its successor ROM8[0x22680 + c], a bijection, so the balance
# per event cylinder is the balance per cut cylinder. The accumulators count
# sixths of a thousandth: each eligible event adds six times the cut
# fraction of the trim unit, which is 1000 - u without a trim, and a sum
# of 6000 is one cut. The offsets 1000 * k + 250 follow the firing order with
# k = (0, 2, 4, 1, 3, 5). Since the six offsets differ by exact sixths, the
# total over whole engine cycles equals that of one accumulator, and every
# cylinder is cut within one event of the others over six cycles.
SPARK_CYLINDER_COUNT = 6
SPARK_CUT_ONE = 6 * U_ONE
SPARK_CYLINDER_OFFSETS = (250, 2250, 4250, 1250, 3250, 5250)
# Above this dwell angle the successor can be armed before the spark.
SPARK_DWELL_LIMIT_DEGREES = 110
SPARK_VETO_BIT = 0x80
MISFIRE_MARKER = 0x01
# The stock writer at 0x00082FC8 stores this calibration byte into the misfire
# latch, so a calibration that equals the marker would let the release clear a
# stock blanking request.
MISFIRE_CALIBRATION_ADDRESS = 0x00008C2E
# The latch is released after at least thirteen events past the last cut,
# which is the carried-over veto of the first event that sees the state leave
# ACTIVE.
MISFIRE_RELEASE_EVENTS = 14
QUIET_EVENTS_MAX = 0xFF


@dataclass(frozen=True)
class SparkEvent:
    """Stock state that the wrapper reads at one GR11A match."""

    spark_armed: bool = True
    synchronized: bool = True
    apc_fallback: bool = False
    dwell_degrees: int = 60
    cylinder: int = 1
    veto_byte: int = 0
    misfire_latch: int = 0


@dataclass(frozen=True)
class SparkCutState:
    """Actuator bytes of the state record."""

    quiet_events: int = 0
    cut_count: int = 0
    accumulators: tuple[int, ...] = (0,) * SPARK_CYLINDER_COUNT


@dataclass(frozen=True)
class SparkResult:
    state: SparkCutState
    veto_byte: int
    misfire_latch: int

    @property
    def vetoed(self):
        return bool(self.veto_byte & SPARK_VETO_BIT)


def spark_event(runtime, cut, event):
    """Return the actuator state, veto byte and misfire latch after one match.

    A match without the armed spark bit is a timeout-forced match and changes
    nothing. A spark resets the quiet-event count while ACTIVE and counts it
    up otherwise. Outside an ACTIVE hold, and for a cut fraction above 1000,
    the accumulators return to their offsets. An ineligible event leaves every
    accumulator unchanged; an out-of-range accumulator of an eligible event
    resets them all.
    """
    if not event.spark_armed:
        return SparkResult(cut, event.veto_byte, event.misfire_latch)
    active = runtime.phase == Phase.ACTIVE
    hold = active and runtime.active_mode_snapshot == Mode.HOLD
    quiet = 0 if active else min(cut.quiet_events + 1, QUIET_EVENTS_MAX)
    latch = event.misfire_latch
    if hold and latch == 0:
        latch = MISFIRE_MARKER
    elif (
        runtime.phase == Phase.IDLE
        and latch == MISFIRE_MARKER
        and quiet >= MISFIRE_RELEASE_EVENTS
    ):
        latch = 0
    cut = replace(cut, quiet_events=quiet)
    reset = replace(cut, accumulators=SPARK_CYLINDER_OFFSETS)
    if not hold or runtime.cut_fraction > U_ONE:
        return SparkResult(reset, event.veto_byte, latch)
    if (
        not event.synchronized
        or event.apc_fallback
        or event.dwell_degrees > SPARK_DWELL_LIMIT_DEGREES
        or not 1 <= event.cylinder <= SPARK_CYLINDER_COUNT
    ):
        return SparkResult(cut, event.veto_byte, latch)
    index = event.cylinder - 1
    if cut.accumulators[index] >= SPARK_CUT_ONE:
        return SparkResult(reset, event.veto_byte, latch)
    accumulator = cut.accumulators[index] + 6 * runtime.cut_fraction
    veto_byte = event.veto_byte
    cut_count = cut.cut_count
    if accumulator >= SPARK_CUT_ONE:
        accumulator -= SPARK_CUT_ONE
        veto_byte |= SPARK_VETO_BIT
        cut_count = (cut_count + 1) & 0xFF
    accumulators = list(cut.accumulators)
    accumulators[index] = accumulator
    return SparkResult(
        replace(cut, cut_count=cut_count, accumulators=tuple(accumulators)),
        veto_byte,
        latch,
    )
