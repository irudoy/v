#!/usr/bin/env python3
"""Replay the JK08A intake-CVTC operating and idle-source bits against an MLG.

FUN_000BD20A writes intake operating bit 0xFFFF246B bit 6 at 0xBD9D6 and
idle-source bit 0xFFFF24A7 bit 1 at 0xBD994, 0xBD9C0, or 0xBD9C6 on every
call. While bit 6 is clear, FUN_000BDC66 stores neutral 0x80 to 0xFFFF2326
through 0xBDCF6 unless active test IOLID 0x19 runs; while it is set, the
function conditions the coolant-selected map byte, and while bit 1 is also set
it conditions replayed byte 0xFFFF1553 instead and raises the target one count
per rise countdown period.

The audit rebuilds both bits for each verified snapshot of a dashboard MLG
recording from its telemetry and dashboard channels and partitions the intake
comparisons of cvtc_target_audit.py by the predicted path. The pedal idle
position, the vehicle-speed byte, the start terms, the fault and inhibit
terms, the re-arm decrementer, and coolant latch 0xFFFF5B2C bit 6 are not in
the recording: the closed-throttle term uses an APP1 bound, the speed byte
uses the 0x280 speed of the dashboard, the unobservable terms are taken as
passing, the re-arm delay is an argument in snapshots, and the latch is
replayed from each initial state.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import math
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.logs import cvtc_target_audit, mlg_relation_audit
from tools.mapkit import rom as romkit


# Idle-source terms of FUN_000BD20A; each flag adds its offset while set.
IDLE_RPM_HOLD_ADDRESS = 0x8715  # ffff11b2 >= 112 holds the term
IDLE_RPM_SET_OFFSET_ADDRESS = 0x8716  # the clear term needs 112 + 8
IDLE_BFS_MIN_ADDRESS = 0x921E  # uint16, ffff1024 >= 0x1400
IDLE_COOLANT_MIN_ADDRESS = 0x871C  # coolant > 55, +3 while set
IDLE_COOLANT_MAX_ADDRESS = 0x871B  # coolant <= 100, -3 while set
IDLE_OIL_MIN_ADDRESS = 0x871A  # oil > 55, +3 while set
IDLE_OIL_MAX_ADDRESS = 0x8719  # oil <= 255, -3 while set
IDLE_OIL_OPTION_ADDRESS = 0x8616  # bit 0 set: the oil term applies
IDLE_IAT_OPTION_ADDRESS = 0x870F  # bit 0 set: the IAT term applies
IDLE_IAT_MAX_ADDRESS = 0x8717  # IAT < 100, -3 while set
IDLE_IAT_MIN_ADDRESS = 0x8718  # IAT >= 55, +3 while set
IDLE_SPEED_BYTE_MAX_ADDRESS = 0x871D  # ffff110e <= 2
IDLE_REARM_RELOAD_ADDRESS = 0x8713  # ffff2527 reload on a failing pass
IDLE_TEMPERATURE_OFFSET = 3
BATTERY_MIN_EXCLUSIVE_ADDRESS = 0x8E0A  # ffff1108 > 125
BATTERY_MAX_ADDRESS = 0x8E07  # ffff1108 <= 200

# Operating terms of FUN_000BD20A after the electrical enable sets r10.
CLOSED_THROTTLE_OPTION_ADDRESS = 0x8940  # bit 1 clear: CLSD THL POS clears r10
COOLANT_CEILING_ADDRESS = 0x8E00  # ffff24a9 bit 6: coolant <= 170, -3 while set
COOLANT_LATCHED_MIN_ADDRESS = 0x8E06  # ffff24a9 bit 0: coolant > 70, +3 while set
COOLANT_UNLATCHED_MIN_ADDRESS = 0x8E03  # ffff24a9 bit 3: coolant > 106, +3 while set
ENGINE_SPEED_MIN_ADDRESS = 0x8DE9  # ffff24a8 bit 4: ffff11b2 >= 72, +16 while set
ENGINE_SPEED_OFFSET = 16
# 0xFFFF5B2C bit 6 selects the coolant flag; immediates at 0xBD2B6 and 0xBD2C8.
LATCH_SET_COOLANT = 125
LATCH_CLEAR_COOLANT = 65

# FUN_000BDB66 and FUN_000BDC66 reload rise countdown 0xFFFF25EE from 0x12EFE
# while ROM8[0x8616] bit 0 is set and from 0x12F06 otherwise.
RISE_OPTION_ADDRESS = 0x8616
RISE_RELOAD_ADDRESS = 0x12EFE
RISE_RELOAD_ALTERNATE_ADDRESS = 0x12F06
RISE_RELOAD_POINTS = 8
RISE_MIN_STEPS = 3

SPEED_BYTE_DIVISOR = 20  # FUN_0003A254: km/h*10 word ffff115e / 20
STATE_FIELDS = (
    "app1_raw",
    "vehicle_speed_kmh",
    "oil_temperature_did_source_raw",
    "iat_raw",
    "battery_voltage_raw",
)
LATCH_STATES = ("set", "clear")
CLASSES = (
    "start_unresolved",
    "neutral_target_0x80",
    "neutral_target_active",
    "idle_exact",
    "idle_rise",
    "idle_other",
    "map_exact_active",
    "map_exact_0x80",
    "map_within_3",
    "map_target_0x80",
    "map_other",
)


@dataclass(frozen=True)
class StateCalibration:
    image_sha256: str
    idle_rpm_hold: int
    idle_rpm_set_offset: int
    idle_bfs_min: int
    idle_coolant_min: int
    idle_coolant_max: int
    idle_oil_min: int
    idle_oil_max: int
    idle_oil_enabled: bool
    idle_iat_enabled: bool
    idle_iat_min: int
    idle_iat_max: int
    idle_speed_byte_max: int
    idle_rearm_reload: int
    battery_min_exclusive: int
    battery_max: int
    closed_throttle_clears_operating: bool
    coolant_ceiling: int
    coolant_latched_min: int
    coolant_unlatched_min: int
    engine_speed_min: int
    rise_period: int


@dataclass(frozen=True)
class StateInput:
    run: int
    tick: int
    rpm_raw: int
    bfs_raw: int
    coolant_raw: int
    oil_raw: int
    iat_raw: int
    battery_raw: int
    app1_raw: int
    vehicle_speed_kmh: float


@dataclass(frozen=True)
class IntakeState:
    idle_bit: bool
    operating_bit: bool
    latch: bool
    failing_idle_terms: tuple[str, ...]
    failing_operating_terms: tuple[str, ...]


@dataclass(frozen=True)
class BandSpan:
    """Extent of the comparisons of one coolant band by their source snapshot."""

    band: str
    comparisons: int
    elapsed_range: tuple[float, float] | None
    coolant_raw_range: tuple[int, int] | None
    vehicle_speed_kmh_max: float | None


@dataclass(frozen=True)
class BandPartition:
    band: str
    comparisons: int
    classes: tuple[tuple[str, int], ...]
    predicted_neutral: int
    predicted_neutral_target_0x80: int
    map_active: int
    map_active_exact: int
    map_active_target_0x80: int
    map_cold_dependent: int
    map_cold_dependent_exact: int
    map_cold_dependent_main_exact: int
    map_cold_dependent_alternate_exact: int
    audit_neutralization: int
    audit_neutralization_predicted: int
    neutral_idle_blockers: tuple[tuple[str, int], ...]
    differ_from_alternate: tuple[tuple[str, int], ...]
    differ_from_both: tuple[tuple[str, int], ...]


@dataclass(frozen=True)
class Discrimination:
    band: str
    comparisons: int
    selected: int
    selected_moving: int
    selected_pedal_applied: int
    selected_off_cell: int
    neutral: int
    alternate: int
    main: int
    other: int


@dataclass(frozen=True)
class LatchReplay:
    latch_initial: str
    first_idle_activation: int | None
    partitions: tuple[BandPartition, ...]


@dataclass(frozen=True)
class IntakeStateAudit:
    source: Path
    source_sha256: str
    calibration_image_source: Path
    calibration_image_sha256: str
    records: int
    bridge_records: int
    analyzed_snapshots: int
    runs: int
    first_rpm_raw: int
    app1_released_max: int
    rearm_snapshots: int
    calibration: StateCalibration
    bands: tuple[BandSpan, ...]
    discrimination: tuple[Discrimination, ...]
    replays: tuple[LatchReplay, ...]


def load_state_calibration(
    rom: str = "JK08A", calibration_image: Path | None = None
) -> StateCalibration:
    if calibration_image is None:
        image = romkit.load(rom)
    else:
        source = Path(calibration_image).resolve()
        image = romkit.Image(source.name, str(source), source.read_bytes())

    def u8(address: int) -> int:
        return image.values(address, 1, "uint8")[0]

    reload_address = (
        RISE_RELOAD_ADDRESS
        if u8(RISE_OPTION_ADDRESS) & 1
        else RISE_RELOAD_ALTERNATE_ADDRESS
    )
    reload_cells = set(image.values(reload_address, RISE_RELOAD_POINTS, "uint8"))
    if len(reload_cells) != 1 or 0 in reload_cells:
        raise ValueError(
            f"rise reload table 0x{reload_address:X} is not one nonzero value; "
            "the rise rule needs a constant countdown period"
        )
    return StateCalibration(
        image_sha256=hashlib.sha256(image.data).hexdigest(),
        idle_rpm_hold=u8(IDLE_RPM_HOLD_ADDRESS),
        idle_rpm_set_offset=u8(IDLE_RPM_SET_OFFSET_ADDRESS),
        idle_bfs_min=image.values(IDLE_BFS_MIN_ADDRESS, 1, "uint16")[0],
        idle_coolant_min=u8(IDLE_COOLANT_MIN_ADDRESS),
        idle_coolant_max=u8(IDLE_COOLANT_MAX_ADDRESS),
        idle_oil_min=u8(IDLE_OIL_MIN_ADDRESS),
        idle_oil_max=u8(IDLE_OIL_MAX_ADDRESS),
        idle_oil_enabled=bool(u8(IDLE_OIL_OPTION_ADDRESS) & 1),
        idle_iat_enabled=bool(u8(IDLE_IAT_OPTION_ADDRESS) & 1),
        idle_iat_min=u8(IDLE_IAT_MIN_ADDRESS),
        idle_iat_max=u8(IDLE_IAT_MAX_ADDRESS),
        idle_speed_byte_max=u8(IDLE_SPEED_BYTE_MAX_ADDRESS),
        idle_rearm_reload=u8(IDLE_REARM_RELOAD_ADDRESS),
        battery_min_exclusive=u8(BATTERY_MIN_EXCLUSIVE_ADDRESS),
        battery_max=u8(BATTERY_MAX_ADDRESS),
        closed_throttle_clears_operating=(
            u8(CLOSED_THROTTLE_OPTION_ADDRESS) & 2
        ) == 0,
        coolant_ceiling=u8(COOLANT_CEILING_ADDRESS),
        coolant_latched_min=u8(COOLANT_LATCHED_MIN_ADDRESS),
        coolant_unlatched_min=u8(COOLANT_UNLATCHED_MIN_ADDRESS),
        engine_speed_min=u8(ENGINE_SPEED_MIN_ADDRESS),
        rise_period=reload_cells.pop(),
    )


def speed_byte(vehicle_speed_kmh: float) -> int:
    """Return the coarse speed byte of a km/h value, as ffff115e / 20."""
    return min(0xFF, math.floor(vehicle_speed_kmh * 10) // SPEED_BYTE_DIVISOR)


def replay_states(
    inputs: list[StateInput],
    calibration: StateCalibration,
    *,
    app1_released_max: int,
    rearm_snapshots: int,
    latch_initial: bool,
) -> list[IntakeState]:
    """Replay 0xFFFF24A7 bit 1 and 0xFFFF246B bit 6 once per snapshot.

    Hysteresis flags start clear, and a producer restart clears them and the
    earlier-activation flag 0xFFFF248F bit 4. The latch keeps its state across
    a restart. After an earlier activation, bit 1 stays clear for
    rearm_snapshots ticks after the last failing pass.
    """
    cal = calibration
    states = []
    latch = latch_initial
    previous = None
    for sample in inputs:
        if previous is None or sample.run != previous.run:
            idle_rpm = idle_cool_low = idle_cool_high = False
            idle_oil_low = idle_oil_high = False
            idle_iat_low = idle_iat_high = False
            coolant_ceiling = coolant_latched = coolant_unlatched = False
            engine_speed = False
            activated = False
            last_failure = None
        previous = sample
        rpm = min(0xFF, sample.rpm_raw)
        coolant = sample.coolant_raw
        offset = IDLE_TEMPERATURE_OFFSET

        # Prologue flags: ffff24a9 bits 3, 6, and 0, ffff24a8 bit 4, latch.
        coolant_unlatched = (
            coolant + (offset if coolant_unlatched else 0)
            > cal.coolant_unlatched_min
        )
        coolant_ceiling = (
            coolant - (offset if coolant_ceiling else 0) <= cal.coolant_ceiling
        )
        engine_speed = (
            rpm + (ENGINE_SPEED_OFFSET if engine_speed else 0)
            >= cal.engine_speed_min
        )
        coolant_latched = (
            coolant + (offset if coolant_latched else 0)
            > cal.coolant_latched_min
        )
        if coolant >= LATCH_SET_COOLANT:
            latch = True
        if coolant < LATCH_CLEAR_COOLANT:
            latch = False

        # Idle-source terms.
        idle_rpm = rpm >= cal.idle_rpm_hold + (0 if idle_rpm else cal.idle_rpm_set_offset)
        idle_cool_low = (
            coolant + (offset if idle_cool_low else 0) > cal.idle_coolant_min
        )
        idle_cool_high = (
            coolant - (offset if idle_cool_high else 0) <= cal.idle_coolant_max
        )
        idle_oil_low = (
            sample.oil_raw + (offset if idle_oil_low else 0) > cal.idle_oil_min
        )
        idle_oil_high = (
            sample.oil_raw - (offset if idle_oil_high else 0) <= cal.idle_oil_max
        )
        idle_iat_low = (
            sample.iat_raw + (offset if idle_iat_low else 0) >= cal.idle_iat_min
        )
        idle_iat_high = (
            sample.iat_raw - (offset if idle_iat_high else 0) < cal.idle_iat_max
        )
        closed_throttle = sample.app1_raw <= app1_released_max
        battery = (
            cal.battery_min_exclusive < sample.battery_raw <= cal.battery_max
        )
        idle_terms = {
            "battery": battery,
            "rpm": idle_rpm,
            "bfs": sample.bfs_raw >= cal.idle_bfs_min,
            "coolant": idle_cool_low and idle_cool_high,
            "oil": not cal.idle_oil_enabled or (idle_oil_low and idle_oil_high),
            "iat": not cal.idle_iat_enabled or (idle_iat_low and idle_iat_high),
            "closed_throttle": closed_throttle,
            "speed": speed_byte(sample.vehicle_speed_kmh)
            <= cal.idle_speed_byte_max,
        }
        failing_idle = tuple(name for name, value in idle_terms.items() if not value)
        if failing_idle:
            idle_bit = False
            last_failure = sample.tick
        elif (
            activated
            and last_failure is not None
            and sample.tick - last_failure <= rearm_snapshots
        ):
            idle_bit = False
            failing_idle = ("rearm_wait",)
        else:
            # The set path stores 0 to 0xFFFF2527 at 0xBD9CA.
            idle_bit = True
            activated = True
            last_failure = None

        operating_terms = {
            "battery": battery,
            "pedal_applied": not (
                closed_throttle and cal.closed_throttle_clears_operating
            ),
            "coolant_ceiling": coolant_ceiling,
            "coolant_latched" if latch else "coolant_unlatched": (
                coolant_latched if latch else coolant_unlatched
            ),
            "engine_speed": engine_speed,
        }
        failing_operating = tuple(
            name for name, value in operating_terms.items() if not value
        )
        states.append(
            IntakeState(
                idle_bit=idle_bit,
                operating_bit=idle_bit or not failing_operating,
                latch=latch,
                failing_idle_terms=failing_idle,
                failing_operating_terms=failing_operating,
            )
        )
    return states


def rise_indices(samples, rise_period: int) -> set[int]:
    """Return the snapshots of every rise of one count per countdown period.

    A rise holds at least RISE_MIN_STEPS one-count steps of the target spaced
    exactly rise_period ticks apart; it covers its steps and the countdown
    period before the first step.
    """
    steps = [
        index
        for index in range(1, len(samples))
        if samples[index].run == samples[index - 1].run
        and samples[index].tick - samples[index - 1].tick == 1
        and samples[index].reference_a_raw == samples[index - 1].reference_a_raw + 1
    ]
    rises = []
    for index in steps:
        if (
            rises
            and samples[index].run == samples[rises[-1][-1]].run
            and samples[index].tick - samples[rises[-1][-1]].tick == rise_period
        ):
            rises[-1].append(index)
        else:
            rises.append([index])
    covered = set()
    for rise in rises:
        if len(rise) < RISE_MIN_STEPS:
            continue
        first_tick = samples[rise[0]].tick - rise_period
        for index in range(rise[0], -1, -1):
            if (
                samples[index].run != samples[rise[0]].run
                or samples[index].tick < first_tick
            ):
                break
            covered.add(index)
        covered.update(range(rise[0], rise[-1] + 1))
    return covered


def comparison_indices(samples, bands, points) -> list[int]:
    return [
        index
        for index in range(1, len(samples))
        if samples[index].run == samples[index - 1].run
        and samples[index].tick - samples[index - 1].tick == 1
        and points[index - 1].coolant_band in bands
    ]


def start_unresolved(samples, states, rises) -> set[int]:
    """Return the leading comparisons that the unobservable start terms decide.

    When the first snapshots of the first run already pass every observable
    idle-source term while the target stays 0x80 until the first rise, the
    start delay of FUN_000BD20A (0xFFFF19AA, 0xFFFF2528) is not in the
    recording, and those comparisons are left unresolved.
    """
    if not rises:
        return set()
    first_rise = min(rises)
    unresolved = set()
    for index in range(1, first_rise):
        if (
            samples[index].run != samples[0].run
            or not states[index - 1].idle_bit
            or samples[index].reference_a_raw != 0x80
        ):
            return set()
        unresolved.add(index)
    return unresolved


def classify(index, samples, points, states, rises, unresolved) -> str:
    target = samples[index].reference_a_raw
    point = points[index - 1]
    state = states[index - 1]
    selected = point.coolant_selected_raw
    if index in unresolved:
        return "start_unresolved"
    if not state.operating_bit:
        return "neutral_target_0x80" if target == 0x80 else "neutral_target_active"
    if state.idle_bit:
        if target == point.alternate_source_raw:
            return "idle_exact"
        return "idle_rise" if index in rises else "idle_other"
    if target == selected:
        return "map_exact_active" if selected != 0x80 else "map_exact_0x80"
    if target == 0x80:
        return "map_target_0x80"
    if abs(target - selected) <= 3:
        return "map_within_3"
    return "map_other"


def _partition(band, rows, samples, points, states, rises, unresolved):
    classes = Counter()
    differ_alternate = Counter()
    differ = Counter()
    blockers = Counter()
    map_active = []
    for index in rows:
        name = classify(index, samples, points, states, rises, unresolved)
        classes[name] += 1
        target = samples[index].reference_a_raw
        point = points[index - 1]
        if target != point.alternate_source_raw:
            differ_alternate[name] += 1
            if target != point.coolant_selected_raw:
                differ[name] += 1
        state = states[index - 1]
        if name.startswith("neutral_") and point.alternate_source_raw != 0x80:
            blockers["+".join(state.failing_idle_terms)] += 1
        if (
            index not in unresolved
            and state.operating_bit
            and not state.idle_bit
            and point.coolant_selected_raw != 0x80
        ):
            map_active.append(index)
    predicted_neutral = [
        index
        for index in rows
        if index not in unresolved and not states[index - 1].operating_bit
    ]
    cold_dependent = [
        index
        for index in map_active
        if points[index - 1].coolant_selected_raw
        != points[index - 1].main_selected_raw
    ]
    neutralized = [
        index
        for index in rows
        if points[index - 1].coolant_selected_raw != 0x80
        and samples[index].reference_a_raw == 0x80
    ]

    def equal(indices, attribute):
        return sum(
            samples[index].reference_a_raw == getattr(points[index - 1], attribute)
            for index in indices
        )

    return BandPartition(
        band=band,
        comparisons=len(rows),
        classes=tuple((name, classes[name]) for name in CLASSES),
        predicted_neutral=len(predicted_neutral),
        predicted_neutral_target_0x80=sum(
            samples[index].reference_a_raw == 0x80 for index in predicted_neutral
        ),
        map_active=len(map_active),
        map_active_exact=equal(map_active, "coolant_selected_raw"),
        map_active_target_0x80=sum(
            samples[index].reference_a_raw == 0x80 for index in map_active
        ),
        map_cold_dependent=len(cold_dependent),
        map_cold_dependent_exact=equal(cold_dependent, "coolant_selected_raw"),
        map_cold_dependent_main_exact=equal(cold_dependent, "main_selected_raw"),
        map_cold_dependent_alternate_exact=equal(
            cold_dependent, "alternate_source_raw"
        ),
        audit_neutralization=len(neutralized),
        audit_neutralization_predicted=sum(
            index not in unresolved and not states[index - 1].operating_bit
            for index in neutralized
        ),
        neutral_idle_blockers=tuple(blockers.most_common()),
        differ_from_alternate=tuple(
            (name, differ_alternate[name])
            for name in CLASSES
            if differ_alternate[name]
        ),
        differ_from_both=tuple(
            (name, differ[name]) for name in CLASSES if differ[name]
        ),
    )


def _band_span(band, rows, samples, inputs) -> BandSpan:
    sources = [index - 1 for index in rows]
    if not sources:
        return BandSpan(band, 0, None, None, None)
    return BandSpan(
        band=band,
        comparisons=len(rows),
        elapsed_range=(
            min(samples[index].timestamp for index in sources),
            max(samples[index].timestamp for index in sources),
        ),
        coolant_raw_range=(
            min(samples[index].coolant_raw for index in sources),
            max(samples[index].coolant_raw for index in sources),
        ),
        vehicle_speed_kmh_max=max(
            inputs[index].vehicle_speed_kmh for index in sources
        ),
    )


def _discrimination(band, rows, samples, points, inputs, app1_released_max, cells):
    """Count comparisons whose coolant-selected byte is unlike every other path.

    The selected byte differs from 0x80, from the main-surface byte, and from
    replayed 0xFFFF1553, so a target equal to it follows the cold path of the
    band without any reconstructed bit. An equal target whose byte is no cell
    value of the cold surface also follows its interpolation.
    """
    counts = Counter()
    for index in rows:
        point = points[index - 1]
        selected = point.coolant_selected_raw
        if selected in (0x80, point.main_selected_raw, point.alternate_source_raw):
            continue
        target = samples[index].reference_a_raw
        if target == selected:
            counts["selected"] += 1
            source = inputs[index - 1]
            counts["selected_moving"] += source.vehicle_speed_kmh > 0
            counts["selected_pedal_applied"] += source.app1_raw > app1_released_max
            counts["selected_off_cell"] += selected not in cells
        elif target == 0x80:
            counts["neutral"] += 1
        elif target == point.alternate_source_raw:
            counts["alternate"] += 1
        elif target == point.main_selected_raw:
            counts["main"] += 1
        else:
            counts["other"] += 1
        counts["comparisons"] += 1
    return Discrimination(
        band=band,
        comparisons=counts["comparisons"],
        selected=counts["selected"],
        selected_moving=counts["selected_moving"],
        selected_pedal_applied=counts["selected_pedal_applied"],
        selected_off_cell=counts["selected_off_cell"],
        neutral=counts["neutral"],
        alternate=counts["alternate"],
        main=counts["main"],
        other=counts["other"],
    )


def _state_inputs(recording, samples) -> list[StateInput]:
    columns = recording.columns
    missing = mlg_relation_audit.missing_channels(recording, STATE_FIELDS)
    if missing:
        raise ValueError(f"{recording.path}: MLG lacks {', '.join(missing)}")
    inputs = []
    for sample in samples:
        index = sample.record_index
        values = {name: columns[name][index] for name in STATE_FIELDS}
        for name, value in values.items():
            if not math.isfinite(value) or (
                name != "vehicle_speed_kmh" and not value.is_integer()
            ):
                raise ValueError(
                    f"{recording.path}: record {index} carries {name}={value!r}"
                )
        inputs.append(
            StateInput(
                run=sample.run,
                tick=sample.tick,
                rpm_raw=sample.rpm_raw,
                bfs_raw=sample.bfs_raw,
                coolant_raw=sample.coolant_raw,
                oil_raw=int(values["oil_temperature_did_source_raw"]),
                iat_raw=int(values["iat_raw"]),
                battery_raw=int(values["battery_voltage_raw"]),
                app1_raw=int(values["app1_raw"]),
                vehicle_speed_kmh=values["vehicle_speed_kmh"],
            )
        )
    return inputs


def audit_recording(
    source: Path,
    *,
    rom: str = "JK08A",
    calibration_image: Path | None = None,
    app1_released_max: int = 153,
    rearm_snapshots: int = 988,
    latch_initial: tuple[str, ...] = LATCH_STATES,
    coolant_bands: tuple[str, ...] = cvtc_target_audit.COOLANT_BANDS,
) -> IntakeStateAudit:
    source = Path(source)
    if not cvtc_target_audit.is_mlg(source):
        raise ValueError(f"{source}: the state replay needs a dashboard MLG")
    if any(band not in cvtc_target_audit.COOLANT_BANDS for band in coolant_bands):
        raise ValueError(
            "coolant bands must be drawn from "
            f"{','.join(cvtc_target_audit.COOLANT_BANDS)}"
        )
    if any(state not in LATCH_STATES for state in latch_initial):
        raise ValueError(f"latch states must be drawn from {','.join(LATCH_STATES)}")
    if rearm_snapshots < 0:
        raise ValueError("the re-arm delay must be nonnegative")
    source_sha256 = cvtc_target_audit._sha256_file(source)
    recording = mlg_relation_audit.read_recording(source)
    if recording.sha256 != source_sha256:
        raise ValueError(f"{source}: capture changed while it was being parsed")
    _events, bridge_records, samples = cvtc_target_audit._recording_samples(
        recording, "tuning"
    )
    if len(samples) < 3:
        raise ValueError(f"{source}: fewer than three verified CVTC snapshots")
    replay = cvtc_target_audit.load_calibration(rom, calibration_image, "intake")
    calibration = load_state_calibration(rom, calibration_image)
    points = [cvtc_target_audit.replay_point(replay, sample) for sample in samples]
    inputs = _state_inputs(recording, samples)
    rises = rise_indices(samples, calibration.rise_period)
    rows_by_band = {
        band: comparison_indices(samples, (band,), points) for band in coolant_bands
    }
    bands = tuple(
        _band_span(band, rows, samples, inputs) for band, rows in rows_by_band.items()
    )
    cells = frozenset(value for row in replay.cold.table for value in row)
    discrimination = tuple(
        _discrimination(band, rows, samples, points, inputs, app1_released_max, cells)
        for band, rows in rows_by_band.items()
    )
    replays = []
    for name in latch_initial:
        states = replay_states(
            inputs,
            calibration,
            app1_released_max=app1_released_max,
            rearm_snapshots=rearm_snapshots,
            latch_initial=name == "set",
        )
        unresolved = start_unresolved(samples, states, rises)
        replays.append(
            LatchReplay(
                latch_initial=name,
                first_idle_activation=next(
                    (index for index, state in enumerate(states) if state.idle_bit),
                    None,
                ),
                partitions=tuple(
                    _partition(band, rows, samples, points, states, rises, unresolved)
                    for band, rows in rows_by_band.items()
                ),
            )
        )
    return IntakeStateAudit(
        source=source,
        source_sha256=source_sha256,
        calibration_image_source=replay.image_source,
        calibration_image_sha256=replay.image_sha256,
        records=recording.record_count,
        bridge_records=bridge_records,
        analyzed_snapshots=len(samples),
        runs=len({sample.run for sample in samples}),
        first_rpm_raw=samples[0].rpm_raw,
        app1_released_max=app1_released_max,
        rearm_snapshots=rearm_snapshots,
        calibration=calibration,
        bands=bands,
        discrimination=discrimination,
        replays=tuple(replays),
    )


def _counts(pairs) -> str:
    return ", ".join(f"{name}={count}" for name, count in pairs)


def _tail(pairs) -> str:
    return f", {_counts(pairs)}" if pairs else ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument(
        "--calibration-image",
        type=Path,
        help="exact full ROM image whose constants and surfaces are replayed",
    )
    parser.add_argument(
        "--app1-released-max",
        type=int,
        default=153,
        help="largest APP1 raw value (V*200) taken as CLSD THL POS",
    )
    parser.add_argument(
        "--rearm-snapshots",
        type=int,
        default=988,
        help="re-arm wait of 0xFFFF2527 in snapshot ticks after a failing pass",
    )
    parser.add_argument(
        "--latch",
        choices=("set", "clear", "both"),
        default="both",
        help="initial state of coolant latch 0xFFFF5B2C bit 6",
    )
    parser.add_argument(
        "--coolant-bands",
        type=lambda value: tuple(value.split(",")),
        default=cvtc_target_audit.COOLANT_BANDS,
        help="comma-separated coolant bands of the source snapshot",
    )
    args = parser.parse_args(argv)
    latch = LATCH_STATES if args.latch == "both" else (args.latch,)
    try:
        for source in args.inputs:
            result = audit_recording(
                source,
                calibration_image=args.calibration_image,
                app1_released_max=args.app1_released_max,
                rearm_snapshots=args.rearm_snapshots,
                latch_initial=latch,
                coolant_bands=args.coolant_bands,
            )
            cal = result.calibration
            print(result.source)
            print(f"  capture_sha256={result.source_sha256}")
            print(
                f"  calibration={result.calibration_image_source}, "
                f"sha256={result.calibration_image_sha256}"
            )
            print(
                f"  records={result.records}, bridge={result.bridge_records}, "
                f"analyzed={result.analyzed_snapshots}, runs={result.runs}, "
                f"first_rpm_raw={result.first_rpm_raw}"
            )
            print(
                f"  idle_terms: rpm_hold={cal.idle_rpm_hold}, "
                f"rpm_set={cal.idle_rpm_hold + cal.idle_rpm_set_offset}, "
                f"bfs_min=0x{cal.idle_bfs_min:04X}, coolant="
                f"{cal.idle_coolant_min + 1}..{cal.idle_coolant_max}, "
                "oil="
                + (
                    f"{cal.idle_oil_min + 1}..{cal.idle_oil_max}"
                    if cal.idle_oil_enabled
                    else "off"
                )
                + ", iat="
                + (
                    f"{cal.idle_iat_min}..{cal.idle_iat_max - 1}"
                    if cal.idle_iat_enabled
                    else "off"
                )
                + f", speed_byte_max={cal.idle_speed_byte_max}, "
                f"battery={cal.battery_min_exclusive + 1}..{cal.battery_max}, "
                f"rearm_reload={cal.idle_rearm_reload}"
            )
            print(
                "  operating_terms: closed_throttle_clears="
                f"{'yes' if cal.closed_throttle_clears_operating else 'no'}, "
                f"coolant_ceiling={cal.coolant_ceiling}, "
                f"coolant_latched_min={cal.coolant_latched_min + 1}, "
                f"coolant_unlatched_min={cal.coolant_unlatched_min + 1}, "
                f"engine_speed_min={cal.engine_speed_min}, "
                f"latch_set>={LATCH_SET_COOLANT}, latch_clear<{LATCH_CLEAR_COOLANT}"
            )
            print(
                f"  proxies: app1_released_max={result.app1_released_max}, "
                "speed_byte=floor(10*vehicle_speed_kmh)//20, "
                f"rearm_snapshots={result.rearm_snapshots}, "
                f"rise_period={cal.rise_period}"
            )
            for span in result.bands:
                if span.elapsed_range is None:
                    print(f"  band={span.band}: n=0")
                    continue
                print(
                    f"  band={span.band}: n={span.comparisons}, "
                    f"elapsed={span.elapsed_range[0]:.3f}.."
                    f"{span.elapsed_range[1]:.3f} s, coolant_raw="
                    f"{span.coolant_raw_range[0]}..{span.coolant_raw_range[1]}, "
                    f"vehicle_speed_kmh_max={span.vehicle_speed_kmh_max!r}"
                )
            for item in result.discrimination:
                print(
                    f"  discriminating band={item.band}: n={item.comparisons}, "
                    f"selected={item.selected} (moving={item.selected_moving}, "
                    f"pedal_applied={item.selected_pedal_applied}, "
                    f"off_cell={item.selected_off_cell}), "
                    f"neutral={item.neutral}, ffff1553={item.alternate}, "
                    f"main={item.main}, other={item.other}"
                )
            for replay in result.replays:
                print(
                    f"  latch_initial={replay.latch_initial}: "
                    "first_idle_activation="
                    f"{'none' if replay.first_idle_activation is None else replay.first_idle_activation}"
                )
                for part in replay.partitions:
                    print(f"    band={part.band}: n={part.comparisons}")
                    print(f"      classes: {_counts(part.classes)}")
                    print(
                        f"      predicted_neutral={part.predicted_neutral}, "
                        f"target_0x80={part.predicted_neutral_target_0x80}"
                    )
                    print(
                        f"      map_active: n={part.map_active}, "
                        f"exact={part.map_active_exact}, "
                        f"target_0x80={part.map_active_target_0x80}"
                    )
                    print(
                        f"      map_cold_dependent: n={part.map_cold_dependent}, "
                        f"exact={part.map_cold_dependent_exact}, "
                        f"main_exact={part.map_cold_dependent_main_exact}, "
                        f"ffff1553_exact={part.map_cold_dependent_alternate_exact}"
                    )
                    print(
                        "      audit_neutralization: "
                        f"n={part.audit_neutralization}, "
                        f"predicted_neutral={part.audit_neutralization_predicted}"
                    )
                    print(
                        "      neutral_with_active_ffff1553_by_failing_idle_terms: "
                        f"n={sum(count for _name, count in part.neutral_idle_blockers)}"
                        + _tail(part.neutral_idle_blockers)
                    )
                    for label, pairs in (
                        ("differ_from_ffff1553", part.differ_from_alternate),
                        ("differ_from_both_replays", part.differ_from_both),
                    ):
                        print(
                            f"      {label}: "
                            f"n={sum(count for _name, count in pairs)}"
                            + _tail(pairs)
                        )
    except (OSError, ValueError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
