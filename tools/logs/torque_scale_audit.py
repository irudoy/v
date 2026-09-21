#!/usr/bin/env python3
"""Bound the physical scale of the JK08A engine-torque domain with road runs.

Telemetry field `engine_torque_state_raw` carries gross engine-torque state
0xFFFF18CC. The net torque that frame 0x180 reports subtracts base term
0xFFFF2408, which the audit replays from the calibration image, and a small
remainder that the TRC captures measure against the 0x180 actual-torque word.
During full-pedal runs the audit derives the flywheel torque that the
longitudinal dynamics of the car require and reports its ratio to the net
word under the candidate scale, the range of that ratio over a box of vehicle
constants, and the road grade that each candidate scale would require.

Gear and converter state come from kinematics. A converter-clutch-locked
cruise in the top gear gives the engine speed per CAN km/h, and the RE5R05A
ratios scale it to the other gears. A point belongs to the gear whose turbine
speed divided by the engine speed lies inside the coupling range, where the
converter transmits torque without multiplication.

The output is one `key = value` line per figure in TOML syntax.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, fields, replace
import hashlib
import itertools
import math
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.can_dashboard.model import BASE_TICK_SECONDS, DashboardModel, FrameRecord
from tools.logs import can_telemetry
from tools.logs import mlg_relation_audit
from tools.logs import peak_trc_audit
from tools.mapkit import rom as romkit

# RE5R05A gear ratios, 2007 Infiniti G35 Sedan service manual, section TM,
# Service Data and Specifications.
RE5R05A_RATIOS = {1: 3.842, 2: 2.353, 3: 1.529, 4: 1.000, 5: 0.839}
LOCKED_GEAR = 5
SELECTOR_NEUTRAL = 0x18
# Frame 0x421 byte 0 codes of the manual positions (defs/JK08A.can.md).
MANUAL_SELECTOR_GEAR = {0x80: 1, 0x88: 2, 0x90: 3, 0x98: 4, 0xA0: 5}
G = 9.80665
RPM_PER_COUNT = 12.5
TICK_MODULUS = 0x10000

BASE_TABLE_ADDRESS = 0x154A0
BASE_AXIS_ADDRESS = 0x14ABA
BASE_POINTS = 8
BFS_TERM_NUMERATOR_ADDRESS = 0x92AC
BFS_SCALER_ADDRESS = 0x9534
CAN_TORQUE_DIVISOR = 5
CAN_TORQUE_ZERO = 800
CAN_TORQUE_INVALID = 4095
ACTUAL_TORQUE_ID = 0x180

CANDIDATE_SCALE_NM = 0.1
CANDIDATE_SCALES_NM = (0.0625, 0.08, 0.1, 0.125)

FULL_PEDAL_APP1 = 900
MIN_SEGMENT_SECONDS = 1.5
POINT_STEP_SECONDS = 0.1
FIT_HALF_SECONDS = 0.2
COUPLING_RANGE = (0.90, 1.0)
MIN_POINT_RPM = 2500.0
MIN_TIMING_RAW = 15
SHIFT_DROP_RPM_PER_S = -1500.0
SHIFT_FIT_HALF_SECONDS = 0.05
SHIFT_GUARD_SECONDS = (0.5, 0.7)
REMAINDER_MIN_APP1 = 600
REMAINDER_MIN_TIMING_RAW = 20
LOCKED_MIN_SPEED_KMH = 60.0
LOCKED_WINDOW_SECONDS = 1.0
LOCKED_RATIO_TOLERANCE = 0.005
COAST_MIN_SPEED_KMH = 40.0
COAST_MAX_APP1 = 200
COAST_MIN_SECONDS = 5.0
COAST_WINDOW_SECONDS = 1.0
RPM_BANDS = tuple(range(2500, 7500, 500))


@dataclass(frozen=True)
class Vehicle:
    """Vehicle constants of the force balance; none of them is measured here."""

    mass_kg: float = 1700.0
    rotating_mass_kg: float = 50.0
    efficiency: float = 0.89
    engine_inertia: float = 0.18
    turbine_inertia: float = 0.06
    speed_scale: float = 1.0
    rolling_n: float = 180.0
    aero_n_per_m2s2: float = 0.37


NOMINAL = Vehicle()
VEHICLE_BOX = {
    "mass_kg": (1650.0, 1750.0),
    "rotating_mass_kg": (40.0, 60.0),
    "efficiency": (0.85, 0.93),
    "engine_inertia": (0.12, 0.25),
    "turbine_inertia": (0.03, 0.10),
    "speed_scale": (0.965, 1.035),
    "rolling_n": (150.0, 220.0),
    "aero_n_per_m2s2": (0.33, 0.41),
}


@dataclass(frozen=True)
class Sample:
    seconds: float
    run: int
    speed_kmh: float | None
    stock_rpm: float | None
    rpm_raw: int
    app1_raw: int
    timing_raw: int
    torque_raw: int
    bfs_raw: int
    selector: int | None
    actual_word: int | None
    fuel_inhibit_mask: int = 0


@dataclass(frozen=True)
class Capture:
    path: Path
    sha256: str
    samples: tuple[Sample, ...]


@dataclass(frozen=True)
class BaseTerm:
    """Replay of base term 0xFFFF2408 from the calibration image."""

    axis: tuple[int, ...]
    table: tuple[int, ...]
    bfs_numerator: int
    bfs_scaler: int

    @classmethod
    def from_image(cls, path: Path) -> "BaseTerm":
        path = Path(path)
        image = romkit.Image(path.name, str(path), path.read_bytes())
        return cls(
            axis=tuple(image.values(BASE_AXIS_ADDRESS, BASE_POINTS, "uint16")),
            table=tuple(image.values(BASE_TABLE_ADDRESS, BASE_POINTS, "uint16")),
            bfs_numerator=image.values(BFS_TERM_NUMERATOR_ADDRESS, 1, "uint16")[0],
            bfs_scaler=image.values(BFS_SCALER_ADDRESS, 1, "uint16")[0],
        )

    def lookup(self, rpm_raw: int) -> int:
        """Descending-search u16 interpolation with a Q0.16 fraction."""
        axis, table = self.axis, self.table
        if rpm_raw <= axis[0]:
            return table[0]
        if rpm_raw >= axis[-1]:
            return table[-1]
        for index in range(len(axis) - 2, -1, -1):
            low = axis[index]
            if rpm_raw == low:
                return table[index]
            if rpm_raw > low:
                fraction = ((rpm_raw - low) << 16) // (axis[index + 1] - low)
                a, b = table[index], table[index + 1]
                if b < a:
                    return a - ((a - b) * fraction >> 16)
                return a + ((b - a) * fraction >> 16)
        return table[0]

    def value(self, rpm_raw: int, bfs_raw: int) -> int:
        bfs_term = min(0xFFFF, bfs_raw * self.bfs_numerator // self.bfs_scaler)
        return max(0, min(0xFFFF, self.lookup(rpm_raw) - bfs_term))


@dataclass(frozen=True)
class Point:
    capture: str
    segment: int
    seconds: float
    speed_mps: float
    accel: float
    rpm: float
    engine_accel: float
    gear: int
    speed_ratio: float
    gross: float
    base: float
    net: float
    actual_word_torque: float | None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _optional(value, kind):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    return kind(value)


def new_tick_records(ticks):
    """Yield (index, run, unwrapped tick) for each record with a new tick.

    A bridge record repeats the preceding tick. A producer restart opens a new
    run whose tick count starts again.
    """
    run = 0
    offset = 0
    previous = None
    for index, value in enumerate(ticks):
        tick = int(value)
        if previous is not None:
            if tick == previous:
                continue
            if can_telemetry.is_producer_restart(previous, tick):
                run += 1
                offset = 0
            elif tick < previous:
                offset += TICK_MODULUS
        previous = tick
        yield index, run, offset + tick


def read_mlg(path: Path) -> Capture:
    recording_ = mlg_relation_audit.read_recording(path)
    columns = recording_.columns
    required = (
        "tick16", "schema_verified", "rpm_raw", "app1_raw", "final_timing_raw",
        "engine_torque_state_raw", "bfs_raw", "vehicle_speed_kmh", "stock_rpm",
        "gear_raw", "fuel_inhibit_mask",
    )
    missing = [name for name in required if name not in columns]
    if missing:
        raise ValueError(f"{path}: missing channels {', '.join(missing)}")
    samples = []
    for index, run, tick in new_tick_records(columns["tick16"]):
        if columns["schema_verified"][index] != 1:
            continue
        samples.append(
            Sample(
                seconds=tick * BASE_TICK_SECONDS,
                run=run,
                speed_kmh=_optional(columns["vehicle_speed_kmh"][index], float),
                stock_rpm=_optional(columns["stock_rpm"][index], float),
                rpm_raw=int(columns["rpm_raw"][index]),
                app1_raw=int(columns["app1_raw"][index]),
                timing_raw=int(columns["final_timing_raw"][index]),
                torque_raw=int(columns["engine_torque_state_raw"][index]),
                bfs_raw=int(columns["bfs_raw"][index]),
                selector=_optional(columns["gear_raw"][index], int),
                actual_word=None,
                fuel_inhibit_mask=int(columns["fuel_inhibit_mask"][index]),
            )
        )
    return Capture(Path(path), recording_.sha256, tuple(samples))


def actual_torque_word(data: bytes) -> int:
    """0x180 byte 2 and the high nibble of byte 3."""
    return data[2] << 4 | data[3] >> 4


def read_trc(path: Path, *, profile="tuning", can_id=0x6F0, tick_divisor=1) -> Capture:
    """Replay a PEAK TRC into snapshots with the latest 0x180 actual-torque word."""
    path = Path(path)
    trace = peak_trc_audit.load_trace(path)
    model = DashboardModel(profile, can_id, tick_divisor)
    names = ("rpm_raw", "app1_raw", "final_timing_raw", "engine_torque_state_raw", "bfs_raw",
             "fuel_inhibit_mask")
    samples = []
    word = None
    for frame in trace.frames:
        if frame.can_id == ACTUAL_TORQUE_ID and not frame.remote and len(frame.data) >= 4:
            word = actual_torque_word(bytes(frame.data))
        timestamp = frame.offset_ms / 1000.0
        snapshot = model.process_frame(
            FrameRecord(
                arbitration_id=frame.can_id,
                data=frame.data,
                timestamp=timestamp,
                received_monotonic=timestamp,
                is_extended_id=frame.extended,
                is_remote_frame=frame.remote,
            ),
            now=timestamp,
        )
        if snapshot is None or not model.schema_verified:
            continue
        if any(name not in model.raw for name in names):
            continue
        samples.append(
            Sample(
                seconds=snapshot.unwrapped_tick * BASE_TICK_SECONDS,
                run=snapshot.run,
                speed_kmh=model.vehicle_speed_kmh,
                stock_rpm=model.stock_rpm,
                rpm_raw=int(model.raw["rpm_raw"]),
                app1_raw=int(model.raw["app1_raw"]),
                timing_raw=int(model.raw["final_timing_raw"]),
                torque_raw=int(model.raw["engine_torque_state_raw"]),
                bfs_raw=int(model.raw["bfs_raw"]),
                selector=model.gear_raw,
                actual_word=word,
                fuel_inhibit_mask=int(model.raw["fuel_inhibit_mask"]),
            )
        )
    return Capture(path, sha256_file(path), tuple(samples))


def read_capture(path: Path) -> Capture:
    if Path(path).suffix.lower() == ".trc":
        return read_trc(path)
    return read_mlg(path)


def line_fit(ts, xs, center, half, minimum=5):
    """Least-squares line over |t - center| <= half: (value at center, slope)."""
    pairs = [(t, x) for t, x in zip(ts, xs) if abs(t - center) <= half]
    if len(pairs) < minimum:
        return None
    mean_t = sum(t for t, _ in pairs) / len(pairs)
    mean_x = sum(x for _, x in pairs) / len(pairs)
    sxx = sum((t - mean_t) ** 2 for t, _ in pairs)
    if sxx == 0:
        return None
    slope = sum((t - mean_t) * (x - mean_x) for t, x in pairs) / sxx
    return mean_x + slope * (center - mean_t), slope


def gear_speed_ratios(locked_rpm_per_kmh, ratios=RE5R05A_RATIOS, locked_gear=LOCKED_GEAR):
    """Engine RPM per CAN km/h of a coupled turbine in every gear."""
    return {
        gear: locked_rpm_per_kmh * ratio / ratios[locked_gear]
        for gear, ratio in ratios.items()
    }


def engine_rad_per_metre(rpm_per_kmh: float) -> float:
    return rpm_per_kmh * 3.6 * 2 * math.pi / 60


def classify_gear(speed_kmh, rpm, rpm_per_kmh, coupling=COUPLING_RANGE):
    """Return (gear, turbine/engine speed ratio) inside the coupling range, or None."""
    if speed_kmh is None or rpm <= 0:
        return None
    for gear, ratio in rpm_per_kmh.items():
        speed_ratio = ratio * speed_kmh / rpm
        if coupling[0] <= speed_ratio <= coupling[1]:
            return gear, speed_ratio
    return None


def runs(flags):
    """Maximal half-open index runs where the flag is set."""
    result = []
    start = None
    for index, flag in enumerate(flags):
        if flag and start is None:
            start = index
        elif not flag and start is not None:
            result.append((start, index))
            start = None
    if start is not None:
        result.append((start, len(flags)))
    return result


def run_samples(capture: Capture):
    by_run = {}
    for sample in capture.samples:
        by_run.setdefault(sample.run, []).append(sample)
    return [by_run[run] for run in sorted(by_run)]


def full_pedal_segments(samples, app1_min=FULL_PEDAL_APP1, min_seconds=MIN_SEGMENT_SECONDS):
    """(start, end) seconds of full-pedal intervals of one producer run."""
    result = []
    for start, stop in runs([s.app1_raw >= app1_min for s in samples]):
        first, last = samples[start].seconds, samples[stop - 1].seconds
        if last - first >= min_seconds:
            result.append((first, last))
    return result


def locked_ratio(samples, *, min_speed=LOCKED_MIN_SPEED_KMH, window=LOCKED_WINDOW_SECONDS,
                 tolerance=LOCKED_RATIO_TOLERANCE):
    """Median stock RPM per CAN km/h over steady converter-locked windows.

    A window qualifies when every sample carries speed and stock RPM, the speed
    stays at or above min_speed, and every sample ratio lies within the
    relative tolerance of the window median.
    """
    usable = [s for s in samples if s.speed_kmh and s.stock_rpm]
    if not usable:
        return None
    ratios = []
    start = usable[0].seconds
    block = []
    for sample in usable:
        if sample.seconds - start >= window:
            ratios.append(block)
            block = []
            start = sample.seconds
        block.append(sample)
    ratios.append(block)
    medians = []
    for block in ratios:
        if len(block) < 10 or any(s.speed_kmh < min_speed for s in block):
            continue
        values = [s.stock_rpm / s.speed_kmh for s in block]
        centre = statistics.median(values)
        if all(abs(v / centre - 1) <= tolerance for v in values):
            medians.append(centre)
    if not medians:
        return None
    return {
        "window_count": len(medians),
        "median": statistics.median(medians),
        "stdev": statistics.pstdev(medians),
        "minimum": min(medians),
        "maximum": max(medians),
    }


def _rpm(sample: Sample) -> float:
    return sample.stock_rpm if sample.stock_rpm else sample.rpm_raw * RPM_PER_COUNT


def shift_instants(samples, start, end):
    """Centres of 0.05 s fits whose engine speed falls faster than the shift threshold."""
    ts = [s.seconds for s in samples if start - 0.1 <= s.seconds <= end + 0.1]
    rs = [_rpm(s) for s in samples if start - 0.1 <= s.seconds <= end + 0.1]
    result = []
    centre = start + SHIFT_FIT_HALF_SECONDS
    while centre <= end - SHIFT_FIT_HALF_SECONDS:
        fit = line_fit(ts, rs, centre, SHIFT_FIT_HALF_SECONDS)
        if fit and fit[1] < SHIFT_DROP_RPM_PER_S:
            result.append(centre)
        centre += 0.02
    return result


def segment_points(capture_name, segment_index, samples, start, end, rpm_per_kmh,
                   base_term: BaseTerm, remainder: float, *, step=POINT_STEP_SECONDS,
                   half=FIT_HALF_SECONDS, coupling=COUPLING_RANGE):
    """Smoothed kinematic points of one full-pedal segment outside gear changes."""
    inside = [s for s in samples if start <= s.seconds <= end]
    speed = [(s.seconds, s.speed_kmh / 3.6) for s in inside if s.speed_kmh is not None]
    speed_t = [t for t, _ in speed]
    speed_v = [v for _, v in speed]
    rpm_t = [s.seconds for s in inside]
    rpm_v = [_rpm(s) for s in inside]
    shifts = shift_instants(samples, start, end)
    before, after = SHIFT_GUARD_SECONDS
    points = []
    centre = start + half
    while centre <= end - half + 1e-9:
        window = [s for s in inside if abs(s.seconds - centre) <= half]
        speed_fit = line_fit(speed_t, speed_v, centre, half)
        rpm_fit = line_fit(rpm_t, rpm_v, centre, half)
        near_shift = any(f - before <= centre <= f + after for f in shifts)
        if (window and speed_fit and rpm_fit and not near_shift
                and min(s.timing_raw for s in window) >= MIN_TIMING_RAW
                and not any(s.fuel_inhibit_mask for s in window)
                and rpm_fit[0] >= MIN_POINT_RPM):
            state = classify_gear(speed_fit[0] * 3.6, rpm_fit[0], rpm_per_kmh, coupling)
            manual = {MANUAL_SELECTOR_GEAR.get(s.selector) for s in window}
            if state is not None and len(manual) == 1 and manual != {None}:
                # A manual position holds its gear: a coupled lower-gear match
                # is a converter multiplying in the held gear.
                if state[0] != next(iter(manual)):
                    state = None
            elif state is not None and len(manual) > 1:
                state = None
            if state is not None:
                gross = statistics.fmean(s.torque_raw for s in window)
                base = statistics.fmean(base_term.value(s.rpm_raw, s.bfs_raw) for s in window)
                words = [s.actual_word for s in window]
                actual = None
                if all(w is not None and w != CAN_TORQUE_INVALID for w in words):
                    actual = statistics.fmean(word_torque(w) for w in words)
                points.append(
                    Point(
                        capture=capture_name,
                        segment=segment_index,
                        seconds=centre,
                        speed_mps=speed_fit[0],
                        accel=speed_fit[1],
                        rpm=rpm_fit[0],
                        engine_accel=rpm_fit[1] * 2 * math.pi / 60,
                        gear=state[0],
                        speed_ratio=state[1],
                        gross=gross,
                        base=base,
                        net=gross - base - remainder,
                        actual_word_torque=actual,
                    )
                )
        centre += step
    return points


def word_torque(word: int) -> float:
    """Midpoint of the raw net-torque interval that a 0x180 word encodes."""
    counts = word - CAN_TORQUE_ZERO
    if counts > 0:
        return counts * CAN_TORQUE_DIVISOR + (CAN_TORQUE_DIVISOR - 1) / 2
    if counts < 0:
        return counts * CAN_TORQUE_DIVISOR - (CAN_TORQUE_DIVISOR - 1) / 2
    return 0.0


def remainder_pairs(samples, base_term: BaseTerm):
    """gross - base - 0x180 net for pedal-open samples outside torque reduction."""
    result = []
    for sample in samples:
        word = sample.actual_word
        if word is None or word == CAN_TORQUE_INVALID:
            continue
        if sample.app1_raw < REMAINDER_MIN_APP1 or sample.timing_raw < REMAINDER_MIN_TIMING_RAW:
            continue
        if sample.fuel_inhibit_mask:
            continue
        base = base_term.value(sample.rpm_raw, sample.bfs_raw)
        result.append((sample.rpm_raw * RPM_PER_COUNT, sample.torque_raw - base - word_torque(word)))
    return result


def flywheel_torque(point: Point, vehicle: Vehicle, rpm_per_kmh, grade=0.0) -> float:
    """Flywheel torque (Nm) that the force balance of one point requires.

    grade is the sine of the road angle, positive uphill. speed_scale is CAN
    speed divided by true speed.
    """
    k = vehicle.speed_scale
    rad_can = engine_rad_per_metre(rpm_per_kmh[point.gear])
    rad_true = rad_can * k
    speed = point.speed_mps / k
    accel = point.accel / k
    force = (
        (vehicle.mass_kg + vehicle.rotating_mass_kg) * accel
        + vehicle.rolling_n
        + vehicle.aero_n_per_m2s2 * speed * speed
        + vehicle.mass_kg * G * grade
    )
    turbine_accel = rad_can * point.accel
    return (
        force / (rad_true * vehicle.efficiency)
        + vehicle.engine_inertia * point.engine_accel
        + vehicle.turbine_inertia * turbine_accel
    )


def implied_grade(point: Point, vehicle: Vehicle, rpm_per_kmh, scale: float, word="net") -> float:
    """Road grade (sine) that makes the force balance hold for a candidate scale."""
    torque = scale * getattr(point, word)
    k = vehicle.speed_scale
    rad_true = engine_rad_per_metre(rpm_per_kmh[point.gear]) * k
    at_zero = flywheel_torque(point, vehicle, rpm_per_kmh, 0.0)
    return (torque - at_zero) * rad_true * vehicle.efficiency / (vehicle.mass_kg * G)


def coast_grades(samples, vehicle: Vehicle = NOMINAL):
    """Grade (sine) of each 1 s window of neutral coasting at nominal road load."""
    flags = [
        s.selector == SELECTOR_NEUTRAL and s.speed_kmh is not None
        and s.speed_kmh >= COAST_MIN_SPEED_KMH and s.app1_raw <= COAST_MAX_APP1
        for s in samples
    ]
    result = []
    for start, stop in runs(flags):
        block = samples[start:stop]
        if block[-1].seconds - block[0].seconds < COAST_MIN_SECONDS:
            continue
        ts = [s.seconds for s in block]
        vs = [s.speed_kmh / 3.6 for s in block]
        centre = ts[0] + COAST_WINDOW_SECONDS / 2
        while centre <= ts[-1] - COAST_WINDOW_SECONDS / 2:
            fit = line_fit(ts, vs, centre, COAST_WINDOW_SECONDS / 2)
            if fit:
                speed, accel = fit
                load = vehicle.rolling_n + vehicle.aero_n_per_m2s2 * speed * speed
                grade = -((vehicle.mass_kg + vehicle.rotating_mass_kg) * accel + load) / (vehicle.mass_kg * G)
                result.append((centre, speed * 3.6, accel, grade))
            centre += COAST_WINDOW_SECONDS
    return result


def box_corners(box=VEHICLE_BOX, nominal=NOMINAL):
    names = list(box)
    for values in itertools.product(*(box[name] for name in names)):
        yield replace(nominal, **dict(zip(names, values)))


def segment_medians(points, value):
    by_segment = {}
    for point in points:
        by_segment.setdefault((point.capture, point.segment), []).append(value(point))
    return {key: statistics.median(values) for key, values in by_segment.items()}


def ratio_summary(points, vehicle, rpm_per_kmh, scale=CANDIDATE_SCALE_NM, word="net"):
    """Median over segments of the segment-median flywheel/candidate torque ratio."""
    medians = segment_medians(
        points,
        lambda p: flywheel_torque(p, vehicle, rpm_per_kmh) / (scale * getattr(p, word)),
    )
    return statistics.median(medians.values()), medians


def sensitivity(points, rpm_per_kmh, box=VEHICLE_BOX, nominal=NOMINAL):
    """Ratio summary with one constant at each end of its box range."""
    return {
        name: tuple(
            ratio_summary(points, replace(nominal, **{name: value}), rpm_per_kmh)[0]
            for value in ends
        )
        for name, ends in box.items()
    }


def candidate_grades(points, rpm_per_kmh, scale, word="net"):
    grades = segment_medians(points, lambda p: implied_grade(p, NOMINAL, rpm_per_kmh, scale, word))
    corner_medians = []
    for vehicle in box_corners():
        medians = segment_medians(points, lambda p: implied_grade(p, vehicle, rpm_per_kmh, scale, word))
        corner_medians.append(statistics.median(medians.values()))
    return {
        "segment_grade_nominal": grades,
        "median_grade_nominal": statistics.median(grades.values()),
        "median_grade_box": (min(corner_medians), max(corner_medians)),
    }


def consistent_scale(first, second, vehicle, rpm_per_kmh, word="net"):
    """Scale at which two point sets imply the same mean road grade.

    The implied grade of a point is linear in the scale, so equal means give
    one scale. Two gears of one run share a stretch of road a few hundred
    metres long, which removes the grade from the comparison.
    """

    def coefficients(points):
        slope = statistics.fmean(
            getattr(p, word) * engine_rad_per_metre(rpm_per_kmh[p.gear])
            * vehicle.speed_scale * vehicle.efficiency / (vehicle.mass_kg * G)
            for p in points
        )
        offset = statistics.fmean(implied_grade(p, vehicle, rpm_per_kmh, 0.0, word) for p in points)
        return slope, offset

    slope_a, offset_a = coefficients(first)
    slope_b, offset_b = coefficients(second)
    return (offset_b - offset_a) / (slope_a - slope_b)


def gear_pair_scales(points, rpm_per_kmh, minimum=5):
    """Grade-free scale of each pair of adjacent gears inside one segment."""
    result = []
    for key in sorted({(p.capture, p.segment) for p in points}, key=lambda k: k[1]):
        chosen = [p for p in points if (p.capture, p.segment) == key]
        gears = sorted({p.gear for p in chosen})
        for low, high in zip(gears, gears[1:]):
            first = [p for p in chosen if p.gear == low]
            second = [p for p in chosen if p.gear == high]
            if len(first) < minimum or len(second) < minimum:
                continue
            corners = [consistent_scale(first, second, v, rpm_per_kmh) for v in box_corners()]
            result.append({
                "capture": key[0], "segment": key[1], "gears": (low, high),
                "points": (len(first), len(second)),
                "scale_nominal": consistent_scale(first, second, NOMINAL, rpm_per_kmh),
                "scale_box": (min(corners), max(corners)),
            })
    return result


def audit(image: Path, cruise: Path, captures: list[Path], remainder_captures: list[Path]):
    base_term = BaseTerm.from_image(image)
    cruise_capture = read_capture(cruise)
    locked = locked_ratio(cruise_capture.samples)
    rpm_per_kmh = gear_speed_ratios(locked["median"])
    pairs = []
    loaded = {}
    for path in remainder_captures:
        loaded[path] = read_capture(path)
        pairs.extend(remainder_pairs(loaded[path].samples, base_term))
    remainder = statistics.median(value for _, value in pairs)
    points = []
    segments = []
    coasts = []
    for path in captures:
        capture = loaded.get(path) or read_capture(path)
        for samples in run_samples(capture):
            coasts.extend(coast_grades(samples))
            for start, end in full_pedal_segments(samples):
                index = len(segments)
                found = segment_points(path.name, index, samples, start, end, rpm_per_kmh,
                                       base_term, remainder)
                origin = capture.samples[0].seconds if capture.samples[0].run == samples[0].run else samples[0].seconds
                segments.append({"capture": path.name, "sha256": capture.sha256,
                                 "start": start - origin, "end": end - origin,
                                 "points": len(found),
                                 "gears": sorted({p.gear for p in found})})
                points.extend(found)
    nominal, per_segment = ratio_summary(points, NOMINAL, rpm_per_kmh)
    corners = [ratio_summary(points, vehicle, rpm_per_kmh)[0] for vehicle in box_corners()]
    gross_nominal, _ = ratio_summary(points, NOMINAL, rpm_per_kmh, word="gross")
    bands = {}
    for gear in sorted({p.gear for p in points}):
        for low in RPM_BANDS:
            chosen = [p for p in points if p.gear == gear and low <= p.rpm < low + 500]
            if len(chosen) < 5:
                continue
            _, medians = ratio_summary(chosen, NOMINAL, rpm_per_kmh)
            bands[(gear, low)] = (len(chosen), len(medians), statistics.median(medians.values()))
    candidates = {scale: candidate_grades(points, rpm_per_kmh, scale) for scale in CANDIDATE_SCALES_NM}
    gross_candidate = candidate_grades(points, rpm_per_kmh, CANDIDATE_SCALE_NM, "gross")
    word_points = [p for p in points if p.actual_word_torque is not None]
    word_gap = [p.net - p.actual_word_torque for p in word_points]
    coast_values = [g for *_, g in coasts]
    return {
        "locked": locked,
        "rpm_per_kmh": rpm_per_kmh,
        "remainder_pairs": len(pairs),
        "remainder": remainder,
        "segments": segments,
        "points": points,
        "ratio_nominal": nominal,
        "ratio_per_segment": per_segment,
        "ratio_box": (min(corners), max(corners)),
        "ratio_gross_nominal": gross_nominal,
        "bands": bands,
        "candidates": candidates,
        "gross_candidate": gross_candidate,
        "sensitivity": sensitivity(points, rpm_per_kmh),
        "gear_pairs": gear_pair_scales(points, rpm_per_kmh),
        "word_point_count": len(word_points),
        "word_gap_median": statistics.median(word_gap) if word_gap else None,
        "coast_windows": len(coasts),
        "coast_grade_range": (min(coast_values), max(coast_values)) if coasts else None,
        "coast_grade_median": statistics.median(coast_values) if coasts else None,
    }


def _toml(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return f'"{value}"'
    if isinstance(value, dict):
        return "{ " + ", ".join(f"{key} = {_toml(item)}" for key, item in value.items()) + " }"
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(_toml(item) for item in value) + "]"
    return repr(value)


def result_lines(result):
    """Figures of one audit as `key = value` lines in TOML syntax."""
    locked = result["locked"]
    segments = result["segments"]
    keys = [(s["capture"], index) for index, s in enumerate(segments)]
    ratios = result["ratio_per_segment"]
    candidates = result["candidates"]
    gross = result["gross_candidate"]
    pairs = result["gear_pairs"]
    figures = {
        "locked_window_count": locked["window_count"],
        "locked_rpm_per_kmh": round(locked["median"], 3),
        "gear_rpm_per_kmh": [round(value, 3) for value in result["rpm_per_kmh"].values()],
        "remainder_sample_count": result["remainder_pairs"],
        "net_remainder_raw": round(result["remainder"], 1),
        "segment_capture_name": [s["capture"] for s in segments],
        "segment_start_seconds": [round(s["start"], 2) for s in segments],
        "segment_end_seconds": [round(s["end"], 2) for s in segments],
        "segment_point_count": [s["points"] for s in segments],
        "segment_gears": [s["gears"] for s in segments],
        "point_count": len(result["points"]),
        "ratio_nominal": round(result["ratio_nominal"], 3),
        "ratio_box": [round(value, 3) for value in result["ratio_box"]],
        "ratio_by_segment": [round(ratios[key], 3) for key in keys if key in ratios],
        "gross_ratio_nominal": round(result["ratio_gross_nominal"], 3),
        "band_gear": [gear for gear, _ in sorted(result["bands"])],
        "band_rpm_low": [low for _, low in sorted(result["bands"])],
        "band_point_count": [result["bands"][key][0] for key in sorted(result["bands"])],
        "band_ratio": [round(result["bands"][key][2], 3) for key in sorted(result["bands"])],
        "candidate_scales_nm_per_raw": list(CANDIDATE_SCALES_NM),
        "candidate_median_grade_percent": [
            round(100 * candidates[scale]["median_grade_nominal"], 2) for scale in CANDIDATE_SCALES_NM
        ],
        "candidate_median_grade_percent_box": [
            [round(100 * value, 2) for value in candidates[scale]["median_grade_box"]]
            for scale in CANDIDATE_SCALES_NM
        ],
        "candidate_segment_grade_percent": [
            [round(100 * candidates[scale]["segment_grade_nominal"][key], 2)
             for key in keys if key in candidates[scale]["segment_grade_nominal"]]
            for scale in CANDIDATE_SCALES_NM
        ],
        "gross_median_grade_percent": round(100 * gross["median_grade_nominal"], 2),
        "gross_median_grade_percent_box": [round(100 * value, 2) for value in gross["median_grade_box"]],
        "gear_pair_segment": [row["segment"] for row in pairs],
        "gear_pair_gears": [list(row["gears"]) for row in pairs],
        "gear_pair_point_count": [list(row["points"]) for row in pairs],
        "gear_pair_scale_nominal": [round(row["scale_nominal"], 4) for row in pairs],
        "gear_pair_scale_box": [[round(value, 4) for value in row["scale_box"]] for row in pairs],
        "sensitivity_ratio": {
            name: [round(value, 3) for value in ends] for name, ends in result["sensitivity"].items()
        },
        "word_point_count": result["word_point_count"],
        "coast_window_count": result["coast_windows"],
    }
    if result["word_gap_median"] is not None:
        figures["word_gap_median_raw"] = round(result["word_gap_median"], 1)
    if result["coast_grade_range"]:
        figures["coast_grade_percent_range"] = [round(100 * value, 2) for value in result["coast_grade_range"]]
        figures["coast_grade_percent_median"] = round(100 * result["coast_grade_median"], 2)
    return [f"{key} = {_toml(value)}" for key, value in figures.items()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("captures", nargs="+", type=Path)
    parser.add_argument("--calibration-image", type=Path, required=True)
    parser.add_argument("--cruise", type=Path, required=True,
                        help="converter-locked top-gear cruise capture")
    parser.add_argument("--remainder", type=Path, action="append", default=[],
                        help="TRC capture with 0x180 frames for the net remainder")
    args = parser.parse_args(argv)
    result = audit(args.calibration_image, args.cruise, args.captures, args.remainder)
    for line in result_lines(result):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
