#!/usr/bin/env python3
"""Executable reference model for cruise-free Map Switching on JK08A.

Defines the 32-byte ROM configuration record (``MSCF`` v1), the stationary
vehicle-speed predicate over CAN 0x284, the brake-held cyclic dual-APP
selector state machine (Maps 1 -> 2 -> 3 -> 4 -> 5 -> 1), and multi-channel
cluster confirmation (CRUISE/SET, MIL 0x551[3].5, and stationary tachometer
0x180/0x1F9).

The SH-2E assembly units in ``patches/map-switching-cruise-free.s`` and
``patches/map-switching-cruise-free-feedback.s`` must match this model on
every boundary and fail-closed path.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
import struct


CONFIG_MAGIC = b"MSCF"
CONFIG_MAGIC_WORD = int.from_bytes(CONFIG_MAGIC, "big")
CONFIG_VERSION = 1
CONFIG_SENTINEL = 0xA55A5AA5
CONFIG_SIZE = 32
# Exact 32-byte big-endian layout:
#   +0x00: 4s  magic ("MSCF")
#   +0x04: B   version (1)
#   +0x05: B   flags (bit0=ascd, bit1=cruise_free, bit2=tach_allowed)
#   +0x06: B   feedback_mode (bit0=cruise, bit1=mil, bit2=tach)
#   +0x07: B   age_limit_ticks (3 -> 30.72 ms)
#   +0x08: H   app_min_valid (60)
#   +0x0A: H   app1_max_valid (964)
#   +0x0C: H   app2_max_valid (1000)
#   +0x0E: H   app_diff_max (60)
#   +0x10: H   app_release_max (260)
#   +0x12: H   app_press_min (700)
#   +0x14: B   tach_hold_frames (40)
#   +0x15: B   debounce_ticks (2)
#   +0x16: H   reserved (0)
#   +0x18: I   reserved2 (0)
#   +0x1C: I   sentinel (0xA55A5AA5)
CONFIG_FORMAT = struct.Struct(">4sBBBBHHHHHHBBHII")
assert CONFIG_FORMAT.size == CONFIG_SIZE

FLAG_ASCD_ENABLED = 0x01
FLAG_CRUISE_FREE_ENABLED = 0x02
FLAG_TACH_ALLOWED = 0x04
VALID_FLAGS_MASK = FLAG_ASCD_ENABLED | FLAG_CRUISE_FREE_ENABLED | FLAG_TACH_ALLOWED

FEEDBACK_CRUISE = 0x01
FEEDBACK_MIL = 0x02
FEEDBACK_TACH = 0x04
VALID_FEEDBACK_MASK = FEEDBACK_CRUISE | FEEDBACK_MIL | FEEDBACK_TACH

FEEDBACK_MODE_NAMES = {
    "off": 0x00,
    "cruise": FEEDBACK_CRUISE,
    "mil": FEEDBACK_MIL,
    "both": FEEDBACK_CRUISE | FEEDBACK_MIL,
    "tach": FEEDBACK_TACH,
    "cruise_tach": FEEDBACK_CRUISE | FEEDBACK_TACH,
    "mil_tach": FEEDBACK_MIL | FEEDBACK_TACH,
    "all": FEEDBACK_CRUISE | FEEDBACK_MIL | FEEDBACK_TACH,
}

MIL_MASK = 0x20
TACH_WIRE_PER_SLOT = 0x1F40  # 8000 wire counts = 1000 RPM at wire / 8 RPM
SLOT_COUNT = 5

STATIONARY_OBSERVED_BIT = 0x01
STATIONARY_VALID_BIT = 0x02


class CruiseFreePhase(IntEnum):
    IDLE_WAIT_RELEASE = 0
    ARMED_RELEASED = 1
    PRESSED_LATCHED = 2


class BlockReason(IntEnum):
    NONE = 0
    CONFIG_DISABLED_OR_INVALID = 1
    ENGINE_RUNNING = 2
    NOT_STATIONARY = 3
    BRAKE_RELEASED = 4
    PEDAL_IMPLAUSIBLE = 5
    ARBITRATION_BLOCKED = 6


@dataclass(frozen=True)
class CruiseFreeConfig:
    flags: int = FLAG_ASCD_ENABLED | FLAG_CRUISE_FREE_ENABLED
    feedback_mode: int = FEEDBACK_CRUISE
    age_limit_ticks: int = 3
    app_min_valid: int = 60
    app1_max_valid: int = 964
    app2_max_valid: int = 1000
    app_diff_max: int = 60
    app_release_max: int = 260
    app_press_min: int = 700
    tach_hold_frames: int = 40
    debounce_ticks: int = 2

    def validate(self):
        if self.flags & ~VALID_FLAGS_MASK:
            raise ValueError(f"unsupported cruise-free flags {self.flags:#x}")
        if self.feedback_mode & ~VALID_FEEDBACK_MASK:
            raise ValueError(
                f"unsupported feedback_mode {self.feedback_mode:#x}"
            )
        if not 1 <= self.age_limit_ticks <= 254:
            raise ValueError("age_limit_ticks must lie in 1..254")
        if not 0 <= self.app_min_valid <= self.app1_max_valid <= 0xFFFF:
            raise ValueError("invalid app1 valid range")
        if not 0 <= self.app_min_valid <= self.app2_max_valid <= 0xFFFF:
            raise ValueError("invalid app2 valid range")
        if not 0 <= self.app_diff_max <= 0xFFFF:
            raise ValueError("invalid app_diff_max")
        if not (
            self.app_min_valid
            <= self.app_release_max
            < self.app_press_min
            <= min(self.app1_max_valid, self.app2_max_valid)
        ):
            raise ValueError(
                "app_release_max < app_press_min must lie within valid APP bounds"
            )
        if not 0 <= self.tach_hold_frames <= 255:
            raise ValueError("tach_hold_frames must lie in 0..255")
        if not 1 <= self.debounce_ticks <= 255:
            raise ValueError("debounce_ticks must lie in 1..255")

    def is_valid(self) -> bool:
        try:
            self.validate()
        except ValueError:
            return False
        return True

    def to_bytes(self) -> bytes:
        self.validate()
        return CONFIG_FORMAT.pack(
            CONFIG_MAGIC,
            CONFIG_VERSION,
            self.flags,
            self.feedback_mode,
            self.age_limit_ticks,
            self.app_min_valid,
            self.app1_max_valid,
            self.app2_max_valid,
            self.app_diff_max,
            self.app_release_max,
            self.app_press_min,
            self.tach_hold_frames,
            self.debounce_ticks,
            0,
            0,
            CONFIG_SENTINEL,
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> CruiseFreeConfig:
        if len(data) != CONFIG_SIZE:
            raise ValueError(
                f"cruise-free configuration must be {CONFIG_SIZE} bytes"
            )
        (
            magic,
            version,
            flags,
            feedback_mode,
            age_limit_ticks,
            app_min_valid,
            app1_max_valid,
            app2_max_valid,
            app_diff_max,
            app_release_max,
            app_press_min,
            tach_hold_frames,
            debounce_ticks,
            reserved,
            reserved2,
            sentinel,
        ) = CONFIG_FORMAT.unpack(data)
        if magic != CONFIG_MAGIC:
            raise ValueError(f"bad cruise-free magic {magic!r}")
        if version != CONFIG_VERSION:
            raise ValueError(f"unsupported cruise-free version {version}")
        if reserved != 0 or reserved2 != 0:
            raise ValueError("nonzero reserved cruise-free config field")
        if sentinel != CONFIG_SENTINEL:
            raise ValueError(f"bad cruise-free sentinel {sentinel:#x}")
        cfg = cls(
            flags=flags,
            feedback_mode=feedback_mode,
            age_limit_ticks=age_limit_ticks,
            app_min_valid=app_min_valid,
            app1_max_valid=app1_max_valid,
            app2_max_valid=app2_max_valid,
            app_diff_max=app_diff_max,
            app_release_max=app_release_max,
            app_press_min=app_press_min,
            tach_hold_frames=tach_hold_frames,
            debounce_ticks=debounce_ticks,
        )
        cfg.validate()
        return cfg

    @classmethod
    def try_from_bytes(cls, data: bytes) -> CruiseFreeConfig | None:
        try:
            return cls.from_bytes(data)
        except ValueError:
            return None


DEFAULT_CONFIG = CruiseFreeConfig()
DEFAULT_CONFIG_BYTES = DEFAULT_CONFIG.to_bytes()


@dataclass(frozen=True)
class StationaryState:
    flags: int = 0
    age: int = 0xFF
    last_raw_speed: int = 0xFFFF

    @property
    def observed(self) -> bool:
        return bool(self.flags & STATIONARY_OBSERVED_BIT)

    @property
    def valid(self) -> bool:
        return (self.flags & (STATIONARY_OBSERVED_BIT | STATIONARY_VALID_BIT)) == (
            STATIONARY_OBSERVED_BIT | STATIONARY_VALID_BIT
        )


def _config_valid(config: CruiseFreeConfig | None) -> bool:
    return config is not None and config.is_valid()


def _stationary_live(
    stationary: StationaryState,
    *,
    port_ready: bool,
    hcan1_ready: bool,
    config: CruiseFreeConfig,
) -> bool:
    return (
        port_ready
        and hcan1_ready
        and stationary.valid
        and stationary.last_raw_speed == 0
        and stationary.age <= config.age_limit_ticks
    )


def advance_stationary(
    state: StationaryState,
    *,
    port_ready: bool,
    hcan1_ready: bool,
    new_frame: bool,
    raw_speed: int,
    config: CruiseFreeConfig | None,
) -> StationaryState:
    """Update stationary contract state once per 10.24 ms HCAN1 RX dispatch."""
    if not _config_valid(config) or not (port_ready and hcan1_ready):
        return StationaryState(flags=0, age=0xFF, last_raw_speed=0xFFFF)

    assert config is not None
    if new_frame:
        raw = raw_speed & 0xFFFF
        if raw == 0:
            return StationaryState(
                flags=STATIONARY_OBSERVED_BIT | STATIONARY_VALID_BIT,
                age=0,
                last_raw_speed=0,
            )
        return StationaryState(
            flags=STATIONARY_OBSERVED_BIT,
            age=0,
            last_raw_speed=raw,
        )

    age = min(0xFF, state.age + 1)
    observed = bool(state.flags & STATIONARY_OBSERVED_BIT)
    if (
        observed
        and state.last_raw_speed == 0
        and age <= config.age_limit_ticks
    ):
        return StationaryState(
            flags=STATIONARY_OBSERVED_BIT | STATIONARY_VALID_BIT,
            age=age,
            last_raw_speed=0,
        )
    return StationaryState(
        flags=STATIONARY_OBSERVED_BIT if observed else 0,
        age=age,
        last_raw_speed=state.last_raw_speed,
    )


@dataclass(frozen=True)
class CruiseFreeState:
    phase: int = CruiseFreePhase.IDLE_WAIT_RELEASE
    debounce: int = 0
    tach_ticks: int = 0
    tach_slot: int = 0
    last_reason: int = BlockReason.NONE
    active_source: int = 0


@dataclass(frozen=True)
class CruiseFreeDecision:
    state: CruiseFreeState
    commit_index: int | None = None
    stationary: StationaryState = StationaryState()


@dataclass(frozen=True)
class CruiseFreeRuntime:
    """Unified 16-byte CF RAM bank holding stationary and selector/tach state.

    Matches the shared SH-2E validator contract where any invalid MSCF record
    wipes CF[0..7] (stationary observation, gesture phase/debounce, and tach
    countdown/slot) regardless of which entry runs first.
    """

    stationary: StationaryState = StationaryState()
    selector: CruiseFreeState = CruiseFreeState()

    def _wipe_invalid_config(
        self, *, last_reason: BlockReason | None = None
    ) -> CruiseFreeRuntime:
        return CruiseFreeRuntime(
            stationary=StationaryState(),
            selector=CruiseFreeState(
                phase=CruiseFreePhase.IDLE_WAIT_RELEASE,
                debounce=0,
                tach_ticks=0,
                tach_slot=0,
                last_reason=(
                    int(last_reason)
                    if last_reason is not None
                    else self.selector.last_reason
                ),
                active_source=self.selector.active_source,
            ),
        )

    def step_stationary(
        self,
        *,
        port_ready: bool,
        hcan1_ready: bool,
        new_frame: bool,
        raw_speed: int,
        config: CruiseFreeConfig | None,
    ) -> CruiseFreeRuntime:
        if not _config_valid(config):
            return self._wipe_invalid_config()
        next_stat = advance_stationary(
            self.stationary,
            port_ready=port_ready,
            hcan1_ready=hcan1_ready,
            new_frame=new_frame,
            raw_speed=raw_speed,
            config=config,
        )
        return CruiseFreeRuntime(stationary=next_stat, selector=self.selector)

    def step_selector(
        self,
        *,
        active_index: int,
        port_ready: bool,
        hcan1_ready: bool,
        rpm_fine: int,
        rpm_coarse: int,
        brake_held: bool,
        app1: int,
        app2: int,
        config: CruiseFreeConfig | None,
    ) -> tuple[CruiseFreeRuntime, int | None]:
        dec = advance_cruise_free(
            self.selector,
            active_index=active_index,
            stationary=self.stationary,
            port_ready=port_ready,
            hcan1_ready=hcan1_ready,
            rpm_fine=rpm_fine,
            rpm_coarse=rpm_coarse,
            brake_held=brake_held,
            app1=app1,
            app2=app2,
            config=config,
        )
        return (
            CruiseFreeRuntime(stationary=dec.stationary, selector=dec.state),
            dec.commit_index,
        )

    def step_tach_wire(
        self,
        *,
        port_ready: bool,
        hcan1_ready: bool,
        rpm_fine: int,
        rpm_coarse: int,
        config: CruiseFreeConfig | None,
    ) -> tuple[int | None, CruiseFreeRuntime]:
        if not _config_valid(config):
            return None, self._wipe_invalid_config()
        wire, next_sel = tach_wire_word(
            self.selector,
            stationary=self.stationary,
            port_ready=port_ready,
            hcan1_ready=hcan1_ready,
            rpm_fine=rpm_fine,
            rpm_coarse=rpm_coarse,
            config=config,
        )
        return wire, CruiseFreeRuntime(stationary=self.stationary, selector=next_sel)

    def step_tach_countdown(
        self,
        *,
        port_ready: bool,
        hcan1_ready: bool,
        rpm_fine: int,
        rpm_coarse: int,
        config: CruiseFreeConfig | None,
    ) -> CruiseFreeRuntime:
        if not _config_valid(config):
            return self._wipe_invalid_config()
        next_sel = tick_tach_countdown(
            self.selector,
            stationary=self.stationary,
            port_ready=port_ready,
            hcan1_ready=hcan1_ready,
            rpm_fine=rpm_fine,
            rpm_coarse=rpm_coarse,
            config=config,
        )
        return CruiseFreeRuntime(stationary=self.stationary, selector=next_sel)


def _reset_cf(
    state: CruiseFreeState,
    reason: BlockReason,
    stationary: StationaryState,
) -> CruiseFreeDecision:
    return CruiseFreeDecision(
        state=CruiseFreeState(
            phase=CruiseFreePhase.IDLE_WAIT_RELEASE,
            debounce=0,
            tach_ticks=state.tach_ticks,
            tach_slot=state.tach_slot,
            last_reason=int(reason),
            active_source=state.active_source,
        ),
        commit_index=None,
        stationary=stationary,
    )


def _reset_cf_invalid_cfg(
    state: CruiseFreeState, reason: BlockReason
) -> CruiseFreeDecision:
    return CruiseFreeDecision(
        state=CruiseFreeState(
            phase=CruiseFreePhase.IDLE_WAIT_RELEASE,
            debounce=0,
            tach_ticks=0,
            tach_slot=0,
            last_reason=int(reason),
            active_source=state.active_source,
        ),
        commit_index=None,
        stationary=StationaryState(),
    )


def advance_cruise_free(
    state: CruiseFreeState,
    *,
    active_index: int,
    stationary: StationaryState,
    port_ready: bool,
    hcan1_ready: bool,
    rpm_fine: int,
    rpm_coarse: int,
    brake_held: bool,
    app1: int,
    app2: int,
    config: CruiseFreeConfig | None,
) -> CruiseFreeDecision:
    """Evaluate one cruise-free cyclic selector step."""
    if not _config_valid(config):
        return _reset_cf_invalid_cfg(state, BlockReason.CONFIG_DISABLED_OR_INVALID)
    assert config is not None
    if not (config.flags & FLAG_CRUISE_FREE_ENABLED):
        return _reset_cf(state, BlockReason.CONFIG_DISABLED_OR_INVALID, stationary)

    if rpm_fine != 0 or rpm_coarse != 0:
        return _reset_cf(state, BlockReason.ENGINE_RUNNING, stationary)

    if not _stationary_live(
        stationary,
        port_ready=port_ready,
        hcan1_ready=hcan1_ready,
        config=config,
    ):
        return _reset_cf(state, BlockReason.NOT_STATIONARY, stationary)

    if not brake_held:
        return _reset_cf(state, BlockReason.BRAKE_RELEASED, stationary)

    if not (
        config.app_min_valid <= app1 <= config.app1_max_valid
        and config.app_min_valid <= app2 <= config.app2_max_valid
        and abs(app1 - app2) <= config.app_diff_max
    ):
        return _reset_cf(state, BlockReason.PEDAL_IMPLAUSIBLE, stationary)

    try:
        phase = CruiseFreePhase(state.phase)
    except ValueError:
        phase = CruiseFreePhase.IDLE_WAIT_RELEASE
        state = CruiseFreeState(
            phase=phase,
            debounce=0,
            tach_ticks=state.tach_ticks,
            tach_slot=state.tach_slot,
            last_reason=state.last_reason,
            active_source=state.active_source,
        )

    is_released = (
        app1 <= config.app_release_max and app2 <= config.app_release_max
    )
    is_pressed = (
        app1 >= config.app_press_min and app2 >= config.app_press_min
    )

    if phase == CruiseFreePhase.IDLE_WAIT_RELEASE:
        if is_released:
            deb = state.debounce + 1
            if deb >= config.debounce_ticks:
                return CruiseFreeDecision(
                    state=CruiseFreeState(
                        phase=CruiseFreePhase.ARMED_RELEASED,
                        debounce=0,
                        tach_ticks=state.tach_ticks,
                        tach_slot=state.tach_slot,
                        last_reason=BlockReason.NONE,
                        active_source=state.active_source,
                    ),
                    stationary=stationary,
                )
            return CruiseFreeDecision(
                state=CruiseFreeState(
                    phase=CruiseFreePhase.IDLE_WAIT_RELEASE,
                    debounce=deb,
                    tach_ticks=state.tach_ticks,
                    tach_slot=state.tach_slot,
                    last_reason=BlockReason.NONE,
                    active_source=state.active_source,
                ),
                stationary=stationary,
            )
        return CruiseFreeDecision(
            state=CruiseFreeState(
                phase=CruiseFreePhase.IDLE_WAIT_RELEASE,
                debounce=0,
                tach_ticks=state.tach_ticks,
                tach_slot=state.tach_slot,
                last_reason=BlockReason.NONE,
                active_source=state.active_source,
            ),
            stationary=stationary,
        )

    if phase == CruiseFreePhase.ARMED_RELEASED:
        if is_pressed:
            deb = state.debounce + 1
            if deb >= config.debounce_ticks:
                cur = active_index if 0 <= active_index < SLOT_COUNT else 0
                next_idx = (cur + 1) % SLOT_COUNT
                next_slot = next_idx + 1
                tach_ticks = state.tach_ticks
                tach_slot = state.tach_slot
                if (
                    (config.flags & FLAG_TACH_ALLOWED)
                    and (config.feedback_mode & FEEDBACK_TACH)
                    and config.tach_hold_frames > 0
                ):
                    tach_ticks = config.tach_hold_frames
                    tach_slot = next_slot
                return CruiseFreeDecision(
                    state=CruiseFreeState(
                        phase=CruiseFreePhase.PRESSED_LATCHED,
                        debounce=0,
                        tach_ticks=tach_ticks,
                        tach_slot=tach_slot,
                        last_reason=BlockReason.NONE,
                        active_source=2,
                    ),
                    commit_index=next_idx,
                    stationary=stationary,
                )
            return CruiseFreeDecision(
                state=CruiseFreeState(
                    phase=CruiseFreePhase.ARMED_RELEASED,
                    debounce=deb,
                    tach_ticks=state.tach_ticks,
                    tach_slot=state.tach_slot,
                    last_reason=BlockReason.NONE,
                    active_source=state.active_source,
                ),
                stationary=stationary,
            )
        return CruiseFreeDecision(
            state=CruiseFreeState(
                phase=CruiseFreePhase.ARMED_RELEASED,
                debounce=0,
                tach_ticks=state.tach_ticks,
                tach_slot=state.tach_slot,
                last_reason=BlockReason.NONE,
                active_source=state.active_source,
            ),
            stationary=stationary,
        )

    # PRESSED_LATCHED: require clean release before arming next tap.
    if is_released:
        deb = state.debounce + 1
        if deb >= config.debounce_ticks:
            return CruiseFreeDecision(
                state=CruiseFreeState(
                    phase=CruiseFreePhase.ARMED_RELEASED,
                    debounce=0,
                    tach_ticks=state.tach_ticks,
                    tach_slot=state.tach_slot,
                    last_reason=BlockReason.NONE,
                    active_source=state.active_source,
                ),
                stationary=stationary,
            )
        return CruiseFreeDecision(
            state=CruiseFreeState(
                phase=CruiseFreePhase.PRESSED_LATCHED,
                debounce=deb,
                tach_ticks=state.tach_ticks,
                tach_slot=state.tach_slot,
                last_reason=BlockReason.NONE,
                active_source=state.active_source,
            ),
            stationary=stationary,
        )
    return CruiseFreeDecision(
        state=CruiseFreeState(
            phase=CruiseFreePhase.PRESSED_LATCHED,
            debounce=0,
            tach_ticks=state.tach_ticks,
            tach_slot=state.tach_slot,
            last_reason=BlockReason.NONE,
            active_source=state.active_source,
        ),
        stationary=stationary,
    )


def tach_wire_word(
    state: CruiseFreeState,
    *,
    stationary: StationaryState,
    port_ready: bool,
    hcan1_ready: bool,
    rpm_fine: int,
    rpm_coarse: int,
    config: CruiseFreeConfig | None,
) -> tuple[int | None, CruiseFreeState]:
    """Compute optional stationary tachometer wire value (wire / 8 RPM).

    Returns ``(None, new_state)`` when stock 0x180/0x1F9 bytes must remain
    untouched, or ``(slot * 0x1F40, state)`` while the hard interlock holds.
    """
    if not _config_valid(config):
        cleared = CruiseFreeState(
            phase=CruiseFreePhase.IDLE_WAIT_RELEASE,
            debounce=0,
            tach_ticks=0,
            tach_slot=0,
            last_reason=state.last_reason,
            active_source=state.active_source,
        )
        return None, cleared
    assert config is not None
    if (
        not (config.flags & FLAG_TACH_ALLOWED)
        or not (config.feedback_mode & FEEDBACK_TACH)
        or state.tach_ticks == 0
        or not 1 <= state.tach_slot <= SLOT_COUNT
        or rpm_fine != 0
        or rpm_coarse != 0
        or not _stationary_live(
            stationary,
            port_ready=port_ready,
            hcan1_ready=hcan1_ready,
            config=config,
        )
    ):
        cleared = CruiseFreeState(
            phase=state.phase,
            debounce=state.debounce,
            tach_ticks=0,
            tach_slot=0,
            last_reason=state.last_reason,
            active_source=state.active_source,
        )
        return None, cleared

    return state.tach_slot * TACH_WIRE_PER_SLOT, state


def tick_tach_countdown(
    state: CruiseFreeState,
    *,
    stationary: StationaryState,
    port_ready: bool,
    hcan1_ready: bool,
    rpm_fine: int,
    rpm_coarse: int,
    config: CruiseFreeConfig | None,
) -> CruiseFreeState:
    """Decrement tach hold counter once per CAN 0x551 tick."""
    wire, checked = tach_wire_word(
        state,
        stationary=stationary,
        port_ready=port_ready,
        hcan1_ready=hcan1_ready,
        rpm_fine=rpm_fine,
        rpm_coarse=rpm_coarse,
        config=config,
    )
    if wire is None:
        return checked
    remaining = state.tach_ticks - 1
    return CruiseFreeState(
        phase=state.phase,
        debounce=state.debounce,
        tach_ticks=remaining,
        tach_slot=state.tach_slot if remaining > 0 else 0,
        last_reason=state.last_reason,
        active_source=state.active_source,
    )
