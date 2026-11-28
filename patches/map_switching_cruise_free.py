#!/usr/bin/env python3
"""Executable reference model for EcuTek-style and cruise-free Map Switching.

Defines the 32-byte ROM configuration record (``MSCF`` v2), the stationary
vehicle-speed predicate over CAN 0x284, the three non-overlapping map
selection modes:

1. Stationary cruise menu (speed == 0, ASCD enabled):
   Hold CANCEL for ``cancel_hold_ticks`` (default 20 = 1.024 s) with the
   accelerator released -> enter menu showing the current map on the tachometer
   (1000..5000 RPM) and 1 MIL flash. RES/ACCEL (+1) and COAST/SET (-1) cycle
   through Maps 1..5 with wrap-around and reset the inactivity timer. A fresh
   CANCEL edge, the inactivity timeout (default 586 ticks = 30.00 s), or
   vehicle motion commits the selected map with 1 MIL flash and restores live
   RPM. Pressing the accelerator (or ASCD MAIN) aborts immediately without
   commit so Rolling Launch retains unconditional priority.
2. Moving cruise direct gesture (speed > 0, ASCD enabled):
   SET + 1..5 CANCEL taps -> release SET commits the map with N MIL flashes.
   Never overrides CRUISE/SET or tachometer frames.
3. Stationary RPM == 0 brake+APP stateful selector (cruise-free):
   Brake held + debounced full accelerator press (>75%) enters selection mode
   showing the current map on the tachometer + 1 MIL flash without incrementing.
   Each subsequent release (<25%) -> full press (>75%) cycles 1..5 -> 1 on the
   tachometer. Releasing the brake commits the selected map with 1 MIL flash
   and restores live RPM (0).

The SH-2E assembly units in ``patches/map-switching-cruise-free.s``,
``patches/map-switching-cruise-free-feedback.s``, and
``patches/map-switching-cruise-free-menu.s`` must match this model on every
boundary and fail-closed path.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import IntEnum
import struct


CONFIG_MAGIC = b"MSCF"
CONFIG_MAGIC_WORD = int.from_bytes(CONFIG_MAGIC, "big")
CONFIG_VERSION = 2
CONFIG_SENTINEL = 0xA55A5AA5
CONFIG_SIZE = 32
# Exact 32-byte big-endian layout (MSCF v2):
#   +0x00: 4s  magic ("MSCF")
#   +0x04: B   version (2)
#   +0x05: B   flags (bit0=ascd, bit1=cruise_free, bit2=tach_allowed, bit3=mil_enabled)
#   +0x06: B   cancel_hold_ticks (20 -> 1.024 s at 51.2 ms selector tick)
#   +0x07: B   age_limit_ticks (3 -> 30.72 ms at 10.24 ms HCAN1 RX tick)
#   +0x08: H   app_min_valid (60)
#   +0x0A: H   app1_max_valid (964)
#   +0x0C: H   app2_max_valid (1000)
#   +0x0E: H   app_diff_max (60)
#   +0x10: H   app_release_max (260)
#   +0x12: H   app_press_min (700)
#   +0x14: H   menu_timeout_ticks (586 -> 30.0032 s at 51.2 ms selector tick)
#   +0x16: B   debounce_ticks (2)
#   +0x17: B   reserved1 (0)
#   +0x18: I   reserved2 (0)
#   +0x1C: I   sentinel (0xA55A5AA5)
CONFIG_FORMAT = struct.Struct(">4sBBBBHHHHHHHBBII")
assert CONFIG_FORMAT.size == CONFIG_SIZE

FLAG_ASCD_ENABLED = 0x01
FLAG_CRUISE_FREE_ENABLED = 0x02
FLAG_TACH_ALLOWED = 0x04
FLAG_MIL_ENABLED = 0x08
VALID_FLAGS_MASK = (
    FLAG_ASCD_ENABLED
    | FLAG_CRUISE_FREE_ENABLED
    | FLAG_TACH_ALLOWED
    | FLAG_MIL_ENABLED
)

MIL_MASK = 0x20
TACH_WIRE_PER_SLOT = 0x1F40  # 8000 wire counts = 1000 RPM at wire / 8 RPM
SLOT_COUNT = 5

STATIONARY_OBSERVED_BIT = 0x01
STATIONARY_VALID_BIT = 0x02

BUTTON_INVALID = 0x00
BUTTON_CANCEL = 0x02
BUTTON_SET = 0x08
BUTTON_RES = 0x10
BUTTON_RELEASED = 0x20


class CruiseFreePhase(IntEnum):
    IDLE_WAIT_RELEASE = 0
    ARMED_ENTER = 1
    ACTIVE_PRESSED = 2
    ACTIVE_RELEASED = 3


class MenuPhase(IntEnum):
    IDLE = 0
    HOLDING_CANCEL = 1
    ACTIVE = 2


class TachMode(IntEnum):
    OFF = 0
    STATIONARY_MENU = 1
    BRAKE_APP_RPM0 = 2


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
    flags: int = VALID_FLAGS_MASK
    cancel_hold_ticks: int = 20
    age_limit_ticks: int = 3
    app_min_valid: int = 60
    app1_max_valid: int = 964
    app2_max_valid: int = 1000
    app_diff_max: int = 60
    app_release_max: int = 260
    app_press_min: int = 700
    menu_timeout_ticks: int = 586
    debounce_ticks: int = 2

    def validate(self):
        if self.flags & ~VALID_FLAGS_MASK:
            raise ValueError(f"unsupported cruise-free flags {self.flags:#x}")
        if not 1 <= self.cancel_hold_ticks <= 255:
            raise ValueError("cancel_hold_ticks must lie in 1..255")
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
        if not 1 <= self.menu_timeout_ticks <= 0xFFFF:
            raise ValueError("menu_timeout_ticks must lie in 1..65535")
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
            self.cancel_hold_ticks,
            self.age_limit_ticks,
            self.app_min_valid,
            self.app1_max_valid,
            self.app2_max_valid,
            self.app_diff_max,
            self.app_release_max,
            self.app_press_min,
            self.menu_timeout_ticks,
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
            cancel_hold_ticks,
            age_limit_ticks,
            app_min_valid,
            app1_max_valid,
            app2_max_valid,
            app_diff_max,
            app_release_max,
            app_press_min,
            menu_timeout_ticks,
            debounce_ticks,
            reserved1,
            reserved2,
            sentinel,
        ) = CONFIG_FORMAT.unpack(data)
        if magic != CONFIG_MAGIC:
            raise ValueError(f"bad cruise-free magic {magic!r}")
        if version != CONFIG_VERSION:
            raise ValueError(f"unsupported cruise-free version {version}")
        if reserved1 != 0 or reserved2 != 0:
            raise ValueError("nonzero reserved cruise-free config field")
        if sentinel != CONFIG_SENTINEL:
            raise ValueError(f"bad cruise-free sentinel {sentinel:#x}")
        cfg = cls(
            flags=flags,
            cancel_hold_ticks=cancel_hold_ticks,
            age_limit_ticks=age_limit_ticks,
            app_min_valid=app_min_valid,
            app1_max_valid=app1_max_valid,
            app2_max_valid=app2_max_valid,
            app_diff_max=app_diff_max,
            app_release_max=app_release_max,
            app_press_min=app_press_min,
            menu_timeout_ticks=menu_timeout_ticks,
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
    tach_mode: int = TachMode.OFF
    tach_slot: int = 0
    last_reason: int = BlockReason.NONE
    active_source: int = 0
    menu_phase: int = MenuPhase.IDLE
    menu_slot: int = 0
    menu_timer: int = 0
    selected_slot: int = 0


@dataclass(frozen=True)
class CruiseFreeDecision:
    state: CruiseFreeState
    commit_index: int | None = None
    mil_pulses: int = 0
    stationary: StationaryState = StationaryState()


@dataclass(frozen=True)
class MenuDecision:
    state: CruiseFreeState
    route: int  # 0 = moving ASCD, 1 = menu owned tick, 2 = stationary idle
    commit_index: int | None = None
    mil_pulses: int = 0


def _clear_cf_transient(
    state: CruiseFreeState, *, clear_tach_if_mode2: bool = True
) -> CruiseFreeState:
    tach_mode = state.tach_mode
    tach_slot = state.tach_slot
    if clear_tach_if_mode2 and tach_mode == TachMode.BRAKE_APP_RPM0:
        tach_mode = TachMode.OFF
        tach_slot = 0
    return replace(
        state,
        phase=CruiseFreePhase.IDLE_WAIT_RELEASE,
        debounce=0,
        selected_slot=0,
        tach_mode=tach_mode,
        tach_slot=tach_slot,
    )


def _clear_menu_transient(
    state: CruiseFreeState, *, clear_tach: bool = True
) -> CruiseFreeState:
    tach_mode = TachMode.OFF if clear_tach else state.tach_mode
    tach_slot = 0 if clear_tach else state.tach_slot
    return replace(
        state,
        menu_phase=MenuPhase.IDLE,
        menu_slot=0,
        menu_timer=0,
        tach_mode=tach_mode,
        tach_slot=tach_slot,
    )


def _wipe_invalid_state(
    state: CruiseFreeState, *, last_reason: BlockReason | None = None
) -> CruiseFreeState:
    return CruiseFreeState(
        phase=CruiseFreePhase.IDLE_WAIT_RELEASE,
        debounce=0,
        tach_mode=TachMode.OFF,
        tach_slot=0,
        last_reason=(
            int(last_reason) if last_reason is not None else state.last_reason
        ),
        active_source=state.active_source,
        menu_phase=MenuPhase.IDLE,
        menu_slot=0,
        menu_timer=0,
        selected_slot=0,
    )


@dataclass(frozen=True)
class CruiseFreeRuntime:
    """Unified CF RAM bank holding stationary, brake+APP, menu, and tach state."""

    stationary: StationaryState = StationaryState()
    selector: CruiseFreeState = CruiseFreeState()

    def _wipe_invalid_config(
        self, *, last_reason: BlockReason | None = None
    ) -> CruiseFreeRuntime:
        return CruiseFreeRuntime(
            stationary=StationaryState(),
            selector=_wipe_invalid_state(self.selector, last_reason=last_reason),
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

    def step_menu(
        self,
        *,
        active_index: int,
        current_code: int,
        previous_code: int,
        feedback_active: bool,
        port_ready: bool,
        hcan1_ready: bool,
        app1: int,
        app2: int,
        config: CruiseFreeConfig | None,
    ) -> tuple[CruiseFreeRuntime, MenuDecision]:
        if not _config_valid(config):
            wiped = self._wipe_invalid_config()
            return wiped, MenuDecision(state=wiped.selector, route=0)
        assert config is not None
        dec = advance_stationary_menu(
            self.selector,
            active_index=active_index,
            current_code=current_code,
            previous_code=previous_code,
            feedback_active=feedback_active,
            stationary=self.stationary,
            port_ready=port_ready,
            hcan1_ready=hcan1_ready,
            app1=app1,
            app2=app2,
            config=config,
        )
        return (
            CruiseFreeRuntime(stationary=self.stationary, selector=dec.state),
            dec,
        )

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
        app1: int = 151,
        app2: int = 151,
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
            app1=app1,
            app2=app2,
            config=config,
        )
        return wire, CruiseFreeRuntime(stationary=self.stationary, selector=next_sel)


def advance_stationary_menu(
    state: CruiseFreeState,
    *,
    active_index: int,
    current_code: int,
    previous_code: int,
    feedback_active: bool,
    stationary: StationaryState,
    port_ready: bool,
    hcan1_ready: bool,
    app1: int,
    app2: int,
    config: CruiseFreeConfig,
) -> MenuDecision:
    """Evaluate one 51.2 ms tick of the stationary cruise menu (Mode 1)."""
    cur = active_index if 0 <= active_index < SLOT_COUNT else 0
    stat_live = _stationary_live(
        stationary,
        port_ready=port_ready,
        hcan1_ready=hcan1_ready,
        config=config,
    )
    accel_pressed = app1 > config.app_release_max or app2 > config.app_release_max

    if state.menu_phase not in (MenuPhase.IDLE, MenuPhase.HOLDING_CANCEL, MenuPhase.ACTIVE):
        state = _clear_menu_transient(
            state, clear_tach=(state.tach_mode == TachMode.STATIONARY_MENU)
        )

    phase = MenuPhase(state.menu_phase)

    if phase == MenuPhase.IDLE:
        if not stat_live:
            return MenuDecision(state=state, route=0)
        if (
            feedback_active
            or accel_pressed
            or state.phase >= CruiseFreePhase.ACTIVE_PRESSED
            or current_code != BUTTON_CANCEL
        ):
            return MenuDecision(state=state, route=2)
        if config.cancel_hold_ticks <= 1:
            slot = cur + 1
            tach_on = bool(config.flags & FLAG_TACH_ALLOWED)
            entered = replace(
                state,
                menu_phase=MenuPhase.ACTIVE,
                menu_slot=slot,
                menu_timer=0,
                tach_mode=TachMode.STATIONARY_MENU if tach_on else TachMode.OFF,
                tach_slot=slot if tach_on else 0,
            )
            return MenuDecision(state=entered, route=1, mil_pulses=1)
        holding = replace(
            state,
            menu_phase=MenuPhase.HOLDING_CANCEL,
            menu_slot=0,
            menu_timer=1,
        )
        return MenuDecision(state=holding, route=1)

    if phase == MenuPhase.HOLDING_CANCEL:
        if accel_pressed:
            return MenuDecision(
                state=_clear_menu_transient(state, clear_tach=False),
                route=1,
            )
        if not stat_live:
            return MenuDecision(
                state=_clear_menu_transient(state, clear_tach=False),
                route=0,
            )
        if feedback_active or current_code != BUTTON_CANCEL:
            return MenuDecision(
                state=_clear_menu_transient(state, clear_tach=False),
                route=2,
            )
        timer = (state.menu_timer + 1) & 0xFFFF
        if timer >= config.cancel_hold_ticks:
            slot = cur + 1
            tach_on = bool(config.flags & FLAG_TACH_ALLOWED)
            entered = replace(
                state,
                menu_phase=MenuPhase.ACTIVE,
                menu_slot=slot,
                menu_timer=0,
                tach_mode=TachMode.STATIONARY_MENU if tach_on else TachMode.OFF,
                tach_slot=slot if tach_on else 0,
            )
            return MenuDecision(state=entered, route=1, mil_pulses=1)
        return MenuDecision(state=replace(state, menu_timer=timer), route=1)

    # MenuPhase.ACTIVE
    slot = state.menu_slot
    if not 1 <= slot <= SLOT_COUNT:
        return MenuDecision(
            state=_clear_menu_transient(state, clear_tach=True),
            route=1,
        )
    if accel_pressed:
        return MenuDecision(
            state=_clear_menu_transient(state, clear_tach=True),
            route=1,
        )
    if not stat_live:
        committed = replace(
            _clear_menu_transient(state, clear_tach=True),
            active_source=3,
        )
        return MenuDecision(
            state=committed, route=1, commit_index=slot - 1, mil_pulses=1
        )
    if current_code == BUTTON_INVALID:
        return MenuDecision(
            state=_clear_menu_transient(state, clear_tach=True),
            route=1,
        )
    if current_code != previous_code:
        if current_code == BUTTON_CANCEL:
            committed = replace(
                _clear_menu_transient(state, clear_tach=True),
                active_source=3,
            )
            return MenuDecision(
                state=committed, route=1, commit_index=slot - 1, mil_pulses=1
            )
        if current_code == BUTTON_RES:
            next_slot = 1 if slot >= SLOT_COUNT else slot + 1
            tach_on = bool(config.flags & FLAG_TACH_ALLOWED)
            updated = replace(
                state,
                menu_slot=next_slot,
                menu_timer=0,
                tach_mode=TachMode.STATIONARY_MENU if tach_on else TachMode.OFF,
                tach_slot=next_slot if tach_on else 0,
            )
            return MenuDecision(state=updated, route=1)
        if current_code == BUTTON_SET:
            next_slot = SLOT_COUNT if slot <= 1 else slot - 1
            tach_on = bool(config.flags & FLAG_TACH_ALLOWED)
            updated = replace(
                state,
                menu_slot=next_slot,
                menu_timer=0,
                tach_mode=TachMode.STATIONARY_MENU if tach_on else TachMode.OFF,
                tach_slot=next_slot if tach_on else 0,
            )
            return MenuDecision(state=updated, route=1)

    timer = (state.menu_timer + 1) & 0xFFFF
    if timer >= config.menu_timeout_ticks:
        committed = replace(
            _clear_menu_transient(state, clear_tach=True),
            active_source=3,
        )
        return MenuDecision(
            state=committed, route=1, commit_index=slot - 1, mil_pulses=1
        )
    tach_on = bool(config.flags & FLAG_TACH_ALLOWED)
    return MenuDecision(
        state=replace(
            state,
            menu_timer=timer,
            tach_mode=TachMode.STATIONARY_MENU if tach_on else TachMode.OFF,
            tach_slot=slot if tach_on else 0,
        ),
        route=1,
    )


def _reset_cf(
    state: CruiseFreeState,
    reason: BlockReason,
    stationary: StationaryState,
) -> CruiseFreeDecision:
    return CruiseFreeDecision(
        state=replace(
            _clear_cf_transient(state, clear_tach_if_mode2=True),
            last_reason=int(reason),
        ),
        commit_index=None,
        stationary=stationary,
    )


def _reset_cf_invalid_cfg(
    state: CruiseFreeState, reason: BlockReason
) -> CruiseFreeDecision:
    return CruiseFreeDecision(
        state=_wipe_invalid_state(state, last_reason=reason),
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
    """Evaluate one Mode 3 stateful RPM==0 brake+APP selector step."""
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
        if (
            state.phase in (CruiseFreePhase.ACTIVE_PRESSED, CruiseFreePhase.ACTIVE_RELEASED)
            and 1 <= state.selected_slot <= SLOT_COUNT
        ):
            committed = replace(
                _clear_cf_transient(state, clear_tach_if_mode2=True),
                last_reason=BlockReason.NONE,
                active_source=2,
            )
            return CruiseFreeDecision(
                state=committed,
                commit_index=state.selected_slot - 1,
                mil_pulses=1,
                stationary=stationary,
            )
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
        return CruiseFreeDecision(
            state=replace(
                _clear_cf_transient(state, clear_tach_if_mode2=True),
                last_reason=BlockReason.NONE,
            ),
            stationary=stationary,
        )

    is_released = (
        app1 <= config.app_release_max and app2 <= config.app_release_max
    )
    is_pressed = (
        app1 >= config.app_press_min and app2 >= config.app_press_min
    )

    if phase in (CruiseFreePhase.ACTIVE_PRESSED, CruiseFreePhase.ACTIVE_RELEASED):
        if not 1 <= state.selected_slot <= SLOT_COUNT:
            return CruiseFreeDecision(
                state=replace(
                    _clear_cf_transient(state, clear_tach_if_mode2=True),
                    last_reason=BlockReason.NONE,
                ),
                stationary=stationary,
            )

    # Phases 0 (IDLE_WAIT_RELEASE) and 2 (ACTIVE_PRESSED) wait for release (<25%).
    if phase in (CruiseFreePhase.IDLE_WAIT_RELEASE, CruiseFreePhase.ACTIVE_PRESSED):
        if is_released:
            deb = state.debounce + 1
            if deb >= config.debounce_ticks:
                next_phase = (
                    CruiseFreePhase.ARMED_ENTER
                    if phase == CruiseFreePhase.IDLE_WAIT_RELEASE
                    else CruiseFreePhase.ACTIVE_RELEASED
                )
                return CruiseFreeDecision(
                    state=replace(
                        state,
                        phase=next_phase,
                        debounce=0,
                        last_reason=BlockReason.NONE,
                    ),
                    stationary=stationary,
                )
            return CruiseFreeDecision(
                state=replace(state, debounce=deb, last_reason=BlockReason.NONE),
                stationary=stationary,
            )
        return CruiseFreeDecision(
            state=replace(state, debounce=0, last_reason=BlockReason.NONE),
            stationary=stationary,
        )

    # Phases 1 (ARMED_ENTER) and 3 (ACTIVE_RELEASED) wait for press (>75%).
    if is_pressed:
        deb = state.debounce + 1
        if deb >= config.debounce_ticks:
            tach_on = bool(config.flags & FLAG_TACH_ALLOWED)
            if phase == CruiseFreePhase.ARMED_ENTER:
                cur = active_index if 0 <= active_index < SLOT_COUNT else 0
                slot = cur + 1
                return CruiseFreeDecision(
                    state=replace(
                        state,
                        phase=CruiseFreePhase.ACTIVE_PRESSED,
                        debounce=0,
                        selected_slot=slot,
                        tach_mode=TachMode.BRAKE_APP_RPM0 if tach_on else TachMode.OFF,
                        tach_slot=slot if tach_on else 0,
                        last_reason=BlockReason.NONE,
                    ),
                    mil_pulses=1,
                    stationary=stationary,
                )
            next_slot = 1 if state.selected_slot >= SLOT_COUNT else state.selected_slot + 1
            return CruiseFreeDecision(
                state=replace(
                    state,
                    phase=CruiseFreePhase.ACTIVE_PRESSED,
                    debounce=0,
                    selected_slot=next_slot,
                    tach_mode=TachMode.BRAKE_APP_RPM0 if tach_on else TachMode.OFF,
                    tach_slot=next_slot if tach_on else 0,
                    last_reason=BlockReason.NONE,
                ),
                stationary=stationary,
            )
        return CruiseFreeDecision(
            state=replace(state, debounce=deb, last_reason=BlockReason.NONE),
            stationary=stationary,
        )
    return CruiseFreeDecision(
        state=replace(state, debounce=0, last_reason=BlockReason.NONE),
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
    app1: int = 151,
    app2: int = 151,
    config: CruiseFreeConfig | None,
) -> tuple[int | None, CruiseFreeState]:
    """Compute optional stationary tachometer wire value (wire / 8 RPM).

    Returns ``(None, new_state)`` when stock 0x180/0x1F9 bytes must remain
    untouched, or ``(slot * 0x1F40, state)`` while the mode interlock holds.
    """
    if not _config_valid(config):
        return None, _wipe_invalid_state(state)
    assert config is not None

    clear_tach = replace(state, tach_mode=TachMode.OFF, tach_slot=0)
    if (
        not (config.flags & FLAG_TACH_ALLOWED)
        or state.tach_mode == TachMode.OFF
        or not 1 <= state.tach_slot <= SLOT_COUNT
    ):
        return None, clear_tach

    stat_live = _stationary_live(
        stationary,
        port_ready=port_ready,
        hcan1_ready=hcan1_ready,
        config=config,
    )
    if state.tach_mode == TachMode.STATIONARY_MENU:
        if app1 > config.app_release_max or app2 > config.app_release_max:
            return None, _clear_menu_transient(state, clear_tach=True)
        if not stat_live:
            # Clear tach immediately so live RPM returns <=10.24 ms; keep
            # menu_phase/menu_slot intact so selector_host commits on next tick.
            return None, clear_tach
        return state.tach_slot * TACH_WIRE_PER_SLOT, state

    if state.tach_mode == TachMode.BRAKE_APP_RPM0:
        if rpm_fine != 0 or rpm_coarse != 0 or not stat_live:
            return None, clear_tach
        return state.tach_slot * TACH_WIRE_PER_SLOT, state

    return None, clear_tach
