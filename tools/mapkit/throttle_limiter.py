"""Exact integer state model for the stock JK08A speed-request limiter.

The model mirrors ``rotational_speed_request_limiter`` at 0x0007584e. It
isolates the limiter state machine from the ROM interpolation helper that
produces the per-RPM baseline request. ``EmulateThrottleLimiter.java`` executes
the unmodified ROM instructions, including that lookup and the downstream
target projection; this module provides a fast, reviewable model for boundary
and state-transition tests.

All values are raw firmware coordinates. Physical RPM and requested-torque
scales remain candidate interpretations in the definition layer.
"""

from dataclasses import dataclass, replace


def _u8(data: bytes, address: int) -> int:
    return data[address]


def _u16(data: bytes, address: int) -> int:
    return int.from_bytes(data[address:address + 2], "big")


def _s16(value: int) -> int:
    value &= 0xFFFF
    return value - 0x10000 if value & 0x8000 else value


def _clamp_u16(value: int) -> int:
    return min(0xFFFF, max(0, value))


def _clamp_s16(value: int) -> int:
    return min(0x7FFF, max(-0x8000, value))


@dataclass(frozen=True)
class ThrottleLimiterCalibration:
    blend_gain: int
    normal_ramp_rate: int
    fast_ramp_rate: int
    final_rate: int
    base_threshold: int
    mode_cap: int
    threshold_down_rate: int
    alternate_threshold: int
    threshold_up_rate: int
    recovery_rate_target_above_phase: int
    recovery_rate_other: int
    auxiliary_duration: int
    coolant_set_threshold: int
    coolant_hysteresis: int
    ramp_mode_load: int
    ramp_transition: int
    auxiliary_requests: tuple[int, ...]

    @classmethod
    def from_rom(cls, data: bytes) -> "ThrottleLimiterCalibration":
        """Read every calibration consumed by the stock limiter function."""
        return cls(
            blend_gain=_u16(data, 0x9424),
            normal_ramp_rate=_u16(data, 0x9426),
            fast_ramp_rate=_u16(data, 0x9428),
            final_rate=_u16(data, 0x942A),
            base_threshold=_u16(data, 0x942C),
            mode_cap=_u16(data, 0x942E),
            threshold_down_rate=_u16(data, 0x9430),
            alternate_threshold=_u16(data, 0x9434),
            threshold_up_rate=_u16(data, 0x9436),
            recovery_rate_target_above_phase=_u16(data, 0x943A),
            recovery_rate_other=_u16(data, 0x943C),
            auxiliary_duration=_u16(data, 0x943E),
            coolant_set_threshold=_u8(data, 0x8A99),
            coolant_hysteresis=_u8(data, 0x8A9A),
            ramp_mode_load=_u8(data, 0x8A9B),
            ramp_transition=_s16(_u16(data, 0x8F2C)),
            auxiliary_requests=tuple(
                _u16(data, 0x14384 + index * 2) - 0x8000
                for index in range(5)
            ),
        )


@dataclass(frozen=True)
class ThrottleLimiterState:
    speed_filtered: int
    dynamic_threshold: int
    blended_threshold: int
    output: int
    ramp: int
    recovery: int
    speed_filter_initialized: bool = True
    coolant_latched: bool = False
    ramp_latched: bool = False
    ramp_mode: int = 0
    auxiliary_request: int = -0x8000
    auxiliary_duration: int = 0


@dataclass(frozen=True)
class ThrottleLimiterInput:
    speed_raw: int
    app_request: int
    baseline_request: int
    raw_coolant: int = 100
    dynamic_threshold_enabled: bool = False
    mode_cap_enabled: bool = False
    force_neutral: bool = False
    shared_request: int = 0
    current_gear_index: int = 0
    target_gear_index: int = 0
    gear_phase_index: int = 0


def decode_can_174_gear_indices(payload_byte_3: int) -> tuple[int, int]:
    """Decode the exact target/current gear fields consumed by the limiter.

    Both nibbles use one-based transmission values 1 through 7. The stock
    decoder publishes zero for zero and every value above 7.
    """
    value = payload_byte_3 & 0xFF

    def decode(nibble: int) -> int:
        return nibble - 1 if 1 <= nibble <= 7 else 0

    return decode(value >> 4), decode(value & 0x0F)


def decode_can_177_gear_phase_index(payload_byte_2: int) -> int:
    """Decode the secondary TCM gear-phase index consumed by the limiter."""
    return payload_byte_2 & 0x07


def transmission_transition_forces_neutral(
    *,
    transition_gate: bool,
    current_gear_index: int,
    target_gear_index: int,
    transition_inhibited: bool,
) -> bool:
    """Model the bit-1 producer in stock-path function 0x00077892."""
    return (
        transition_gate
        and (current_gear_index & 0xFF) != (target_gear_index & 0xFF)
        and not transition_inhibited
    )


def transmission_request_candidate_enabled(
    *,
    force_neutral: bool,
    retained_transition: int,
) -> bool:
    """Model the bit-3 selector written by stock-path function 0x00077892.

    This selector is evaluated before common completion function 0x000777fa
    can publish the secondary 0x942c-derived signed candidate.
    """
    return force_neutral or (retained_transition & 0xFF) != 0


def step_throttle_limiter(
    calibration: ThrottleLimiterCalibration,
    state: ThrottleLimiterState,
    inputs: ThrottleLimiterInput,
) -> ThrottleLimiterState:
    """Execute one stock-equivalent limiter update.

    Right shifts intentionally use Python's arithmetic floor behavior, matching
    SH-2E ``SHAR``. The blend uses the filter value from function entry while
    both ramp terms use the newly stored filter value. This one-sample split is
    observable during acceleration and must not be collapsed into one value.
    """
    if calibration.base_threshold == 0xFFFF:
        return replace(state, output=0x7FFF)

    speed_raw = inputs.speed_raw & 0xFFFF
    if state.speed_filter_initialized:
        blend_speed = state.speed_filtered & 0xFFFF
        speed_filtered = min(
            0xFFFF,
            speed_raw + (3 * blend_speed >> 2),
        )
    else:
        speed_filtered = min(0xFFFF, 4 * speed_raw)
        blend_speed = speed_filtered

    coolant_compare = (inputs.raw_coolant & 0xFF)
    if state.coolant_latched:
        coolant_compare += calibration.coolant_hysteresis
    coolant_latched = coolant_compare >= calibration.coolant_set_threshold

    desired_threshold = calibration.base_threshold
    if coolant_latched:
        desired_threshold = min(desired_threshold, calibration.alternate_threshold)

    dynamic_threshold = state.dynamic_threshold & 0xFFFF
    if desired_threshold < dynamic_threshold:
        if inputs.dynamic_threshold_enabled:
            candidate = dynamic_threshold - calibration.threshold_down_rate
            dynamic_threshold = max(candidate, calibration.alternate_threshold)
    elif desired_threshold > dynamic_threshold:
        if inputs.dynamic_threshold_enabled:
            dynamic_threshold = min(
                desired_threshold,
                dynamic_threshold + calibration.threshold_up_rate,
            )

    if inputs.mode_cap_enabled:
        dynamic_threshold = min(dynamic_threshold, calibration.mode_cap)

    blended_threshold = _clamp_u16(
        blend_speed
        + (calibration.blend_gain * (dynamic_threshold - blend_speed) >> 10)
    )
    request_delta = blended_threshold - speed_filtered

    entry_ramp = _s16(state.ramp)
    app_request = _s16(inputs.app_request)
    previous_output = _s16(state.output)
    ramp = entry_ramp
    ramp_latched = state.ramp_latched
    ramp_mode = state.ramp_mode & 0xFF

    if previous_output < app_request:
        if ramp <= calibration.ramp_transition:
            ramp_latched = True

        if ramp_mode != 0 and not ramp_latched:
            ramp += calibration.fast_ramp_rate * request_delta >> 7
            ramp = max(calibration.ramp_transition, ramp)
        else:
            ramp += calibration.normal_ramp_rate * request_delta >> 7

        ramp = min(0x7FFF, max(_s16(inputs.baseline_request), ramp))
        request_base = ramp
    else:
        if previous_output < 0x7FFF:
            ramp = app_request
        request_base = ramp
        ramp_mode = calibration.ramp_mode_load
        ramp_latched = False

    request = _clamp_s16(
        request_base + (calibration.final_rate * request_delta >> 7)
    )

    recovery = _s16(state.recovery)
    current_gear = inputs.current_gear_index & 0xFF
    target_gear = inputs.target_gear_index & 0xFF
    gear_phase = inputs.gear_phase_index & 0xFF
    if (
        request < recovery
        and request < app_request
        and target_gear > current_gear
    ):
        recovery = request
    else:
        recovery_rate = (
            calibration.recovery_rate_target_above_phase
            if target_gear > gear_phase
            else calibration.recovery_rate_other
        )
        recovery = min(0x7FFF, recovery + recovery_rate)

    if recovery < request:
        output = recovery
        ramp = entry_ramp
    else:
        output = request

    if inputs.force_neutral:
        output = 0x7FFF
        ramp = _s16(inputs.shared_request)

    if output < app_request and target_gear > current_gear:
        auxiliary_request = calibration.auxiliary_requests[min(target_gear, 4)]
        auxiliary_duration = calibration.auxiliary_duration
    else:
        auxiliary_request = -0x8000
        auxiliary_duration = 0

    return ThrottleLimiterState(
        speed_filtered=speed_filtered,
        dynamic_threshold=dynamic_threshold,
        blended_threshold=blended_threshold,
        output=output,
        ramp=ramp,
        recovery=recovery,
        speed_filter_initialized=True,
        coolant_latched=coolant_latched,
        ramp_latched=ramp_latched,
        ramp_mode=ramp_mode,
        auxiliary_request=auxiliary_request,
        auxiliary_duration=auxiliary_duration,
    )
