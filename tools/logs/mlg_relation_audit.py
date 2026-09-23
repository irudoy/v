#!/usr/bin/env python3
"""Audit code-level field relations inside a dashboard MLG recording.

The dashboard recorder stores every custom-telemetry channel as its raw wire
value, so a recording can be replayed against the exact JK08A formulas that
connect those values: the live intake-VTC duty pair against its duty command
latch, cam-position bytes against
their common targets, the MAF transfer chain, the J1979 Calculated Load byte,
the Base Fuel Schedule producer, the compensated injection words, the code
chain from the schedule to the pulse words, and the final timing to APC
command identity. Every relation is evaluated in raw
software units; the audit does not prove any physical unit.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import math
from pathlib import Path
import statistics
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.can_dashboard import recording
from tools.can_dashboard.model import rpm_counts
from tools.logs import mlvlg
from tools.logs.load_axis_audit import (
    CALCULATED_LOAD_REFERENCE_ADDRESS,
    CALCULATED_LOAD_REFERENCE_POINTS,
    INTERNAL_LOAD_SCALER_ADDRESS,
    calculated_load_raw,
    interpolate_implicit_u16,
)
from tools.mapkit import rom as romkit

MAF_CURVE_B1_ADDRESS = 0x14274
MAF_CURVE_B2_ADDRESS = 0x141F4
MAF_CURVE_POINTS = 64
MAF_CURVE_STEP = 16
MAF_SUM_OFFSET_ADDRESS = 0x93CE
MAF_DID_FACTOR_ADDRESS = 0x83EC
BFS_F_ADDRESS = 0x8A27
BFS_K_ADDRESS = 0x9284
BFS_E_ADDRESS = 0x88FB
BFS_FIXED_LIMIT = 0x726F9
BFS_OUTPUT_FACTOR = 9163
BFS_SPEED_FLOOR = 64
PULSE_GAIN_LOAD_CURVE_ADDRESS = 0x129E2
PULSE_GAIN_SPEED_CURVE_ADDRESS = 0x129F2
PULSE_GAIN_CURVE_POINTS = 16
PULSE_GAIN_CURVE_STEP = 16
PULSE_GAIN_CURVE_LIMIT = 240
PULSE_GAIN_PRESSURE_ADDRESS = 0x93C6
PULSE_GAIN_PRESSURE_SLOPE_ADDRESS = 0x89FE
PULSE_GAIN_PRESSURE_DIVISOR = 0xCA99
PULSE_GAIN_RATIO_FLOOR_ADDRESS = 0x83C4
PULSE_GAIN_TEMPERATURE_FLOOR_ADDRESS = 0x83C5
PULSE_GAIN_TEMPERATURE_CEILING_ADDRESS = 0x83C6
PULSE_GAIN_TEMPERATURE_NUMERATOR = 0x12A00
PULSE_GAIN_TEMPERATURE_OFFSET = 0xDF
PULSE_GAIN_RAIL_ADDRESS = 0x8AE7
PULSE_GAIN_AFFINE_SLOPE = 5259
PULSE_GAIN_AFFINE_OFFSET = 0x128500
PULSE_GAIN_AFFINE_DIVISOR = 10000
PULSE_GAIN_SCALAR_ADDRESS = 0x9332
PULSE_PRECURSOR_FLOOR_ADDRESS = 0x94E8
PULSE_OPENING_SLOPE_ADDRESS = 0x84F6
PULSE_OPENING_BASE_ADDRESS = 0x8C9E
PULSE_OPENING_BATTERY_REFERENCE = 175
TRIM_NEUTRAL_SUM = 0xC800
STFT_NEUTRAL = 0x6400
AF_STATE_NEUTRAL = 0x4000
APC_COMMAND_BASE = 110
KNOCK_EVENT_STEP = -307
KNOCK_RECOVERY_STEP = 13

DUTY_TOLERANCE = 3
CVTC_TOLERANCE = 2


@dataclass(frozen=True)
class RelationCalibration:
    image_source: Path
    image_sha256: str
    maf_curve_b1: tuple[int, ...]
    maf_curve_b2: tuple[int, ...]
    maf_sum_offset: int
    maf_did_factor: int
    bfs_f: int
    bfs_k: int
    bfs_e: int
    load_scaler: int
    calculated_load_reference: tuple[int, ...]
    pulse_gain_load_curve: tuple[int, ...]
    pulse_gain_speed_curve: tuple[int, ...]
    pulse_gain_pressure: int
    pulse_gain_pressure_slope: int
    pulse_gain_ratio_floor: int
    pulse_gain_temperature_floor: int
    pulse_gain_temperature_ceiling: int
    pulse_gain_rail: int
    pulse_gain_scalar: int
    pulse_precursor_floor: int
    pulse_opening_slope: int
    pulse_opening_base: int


@dataclass(frozen=True)
class Recording:
    path: Path
    sha256: str
    fields: tuple[mlvlg.FieldSpec, ...]
    columns: dict[str, list[float]]
    record_count: int


def load_calibration(
    rom: str = "JK08A",
    calibration_image: Path | None = None,
) -> RelationCalibration:
    if calibration_image is None:
        image = romkit.load(rom)
        image_source = Path(image.path)
    else:
        image_source = Path(calibration_image).resolve()
        image = romkit.Image(
            image_source.name, str(image_source), image_source.read_bytes()
        )
    return RelationCalibration(
        image_source=image_source,
        image_sha256=hashlib.sha256(image.data).hexdigest(),
        maf_curve_b1=tuple(
            image.values(MAF_CURVE_B1_ADDRESS, MAF_CURVE_POINTS, "uint16")
        ),
        maf_curve_b2=tuple(
            image.values(MAF_CURVE_B2_ADDRESS, MAF_CURVE_POINTS, "uint16")
        ),
        maf_sum_offset=image.values(MAF_SUM_OFFSET_ADDRESS, 1, "uint16")[0],
        maf_did_factor=image.values(MAF_DID_FACTOR_ADDRESS, 1, "uint8")[0],
        bfs_f=image.values(BFS_F_ADDRESS, 1, "uint8")[0],
        bfs_k=image.values(BFS_K_ADDRESS, 1, "uint16")[0],
        bfs_e=image.values(BFS_E_ADDRESS, 1, "uint8")[0],
        load_scaler=image.values(INTERNAL_LOAD_SCALER_ADDRESS, 1, "uint16")[0],
        calculated_load_reference=tuple(
            image.values(
                CALCULATED_LOAD_REFERENCE_ADDRESS,
                CALCULATED_LOAD_REFERENCE_POINTS,
                "uint16",
            )
        ),
        pulse_gain_load_curve=tuple(
            image.values(
                PULSE_GAIN_LOAD_CURVE_ADDRESS, PULSE_GAIN_CURVE_POINTS, "uint8"
            )
        ),
        pulse_gain_speed_curve=tuple(
            image.values(
                PULSE_GAIN_SPEED_CURVE_ADDRESS, PULSE_GAIN_CURVE_POINTS, "uint8"
            )
        ),
        pulse_gain_pressure=image.values(
            PULSE_GAIN_PRESSURE_ADDRESS, 1, "uint16"
        )[0],
        pulse_gain_pressure_slope=image.values(
            PULSE_GAIN_PRESSURE_SLOPE_ADDRESS, 1, "uint8"
        )[0],
        pulse_gain_ratio_floor=image.values(
            PULSE_GAIN_RATIO_FLOOR_ADDRESS, 1, "uint8"
        )[0],
        pulse_gain_temperature_floor=image.values(
            PULSE_GAIN_TEMPERATURE_FLOOR_ADDRESS, 1, "uint8"
        )[0],
        pulse_gain_temperature_ceiling=image.values(
            PULSE_GAIN_TEMPERATURE_CEILING_ADDRESS, 1, "uint8"
        )[0],
        pulse_gain_rail=image.values(PULSE_GAIN_RAIL_ADDRESS, 1, "uint8")[0],
        pulse_gain_scalar=image.values(PULSE_GAIN_SCALAR_ADDRESS, 1, "uint16")[0],
        pulse_precursor_floor=image.values(
            PULSE_PRECURSOR_FLOOR_ADDRESS, 1, "uint16"
        )[0],
        pulse_opening_slope=image.values(
            PULSE_OPENING_SLOPE_ADDRESS, 1, "uint8"
        )[0],
        pulse_opening_base=image.values(PULSE_OPENING_BASE_ADDRESS, 1, "uint8")[0],
    )


def maf_total_raw(
    calibration: RelationCalibration, maf_b1_raw: int, maf_b2_raw: int
) -> tuple[int, int, int]:
    """Return transfer outputs A and B and the published total word."""
    output_a = interpolate_implicit_u16(
        calibration.maf_curve_b1, maf_b1_raw, MAF_CURVE_STEP
    )
    output_b = interpolate_implicit_u16(
        calibration.maf_curve_b2, maf_b2_raw, MAF_CURVE_STEP
    )
    aggregate = max(output_a + output_b - calibration.maf_sum_offset, 0)
    total = min(0xFFFF, calibration.maf_did_factor * aggregate // 256)
    return output_a, output_b, total


def bfs_reference_raw(
    calibration: RelationCalibration, aggregate: int, speed_count: int
) -> int:
    """Return the primary-branch producer word for aggregate Q and count N."""
    count = max(speed_count, BFS_SPEED_FLOOR)
    fixed = (calibration.bfs_f * calibration.bfs_k * aggregate // 256) // (
        calibration.bfs_e * count
    )
    fixed = min(fixed, BFS_FIXED_LIMIT)
    return fixed * BFS_OUTPUT_FACTOR // 65536


def common_pulse_gain_raw(
    calibration: RelationCalibration,
    bfs_raw: int,
    intake_temperature_raw: int,
    speed_byte: int,
) -> int:
    """Return common Q14 gain 0xFFFF165E of FUN_00053698.

    The stage is reproduced for the stock configuration in which the pressure
    slope byte is zero, so the pressure word equals its ROM reference.
    """
    if calibration.pulse_gain_pressure_slope:
        raise ValueError("a nonzero pressure slope needs unstreamed word 0xFFFF4524")
    pressure = calibration.pulse_gain_pressure
    ratio = (pressure << 8) // PULSE_GAIN_PRESSURE_DIVISOR
    ratio = min(max(ratio, calibration.pulse_gain_ratio_floor), 0x100)
    temperature = PULSE_GAIN_TEMPERATURE_NUMERATOR // (
        intake_temperature_raw + PULSE_GAIN_TEMPERATURE_OFFSET
    )
    temperature = min(
        max(temperature, calibration.pulse_gain_temperature_floor + 0x80),
        calibration.pulse_gain_temperature_ceiling + 0x80,
    )
    load = min(0xFF, ((bfs_raw * ratio >> 8) * temperature) >> 15)
    fraction = min(
        0xFF,
        interpolate_implicit_u16(
            calibration.pulse_gain_load_curve,
            min(load, PULSE_GAIN_CURVE_LIMIT),
            PULSE_GAIN_CURVE_STEP,
        )
        + interpolate_implicit_u16(
            calibration.pulse_gain_speed_curve,
            min(speed_byte, PULSE_GAIN_CURVE_LIMIT),
            PULSE_GAIN_CURVE_STEP,
        ),
    )
    difference = min(0xFFFF, pressure * (0x100 - fraction) >> 8)
    denominator = (calibration.pulse_gain_rail << 10) + difference
    quotient = (
        min(0xFF, (calibration.pulse_gain_rail << 18) // denominator)
        if denominator
        else 0
    )
    factor = min(
        0xFF,
        (quotient * PULSE_GAIN_AFFINE_SLOPE + PULSE_GAIN_AFFINE_OFFSET)
        // PULSE_GAIN_AFFINE_DIVISOR,
    )
    return factor * calibration.pulse_gain_scalar >> 8


def pulse_reference_raw(
    calibration: RelationCalibration,
    bfs_raw: int,
    gain_raw: int,
    stft_raw: int,
    ltft_raw: int,
    battery_raw: int,
) -> int:
    """Return the closed-loop pulse word for unity multipliers and no transient.

    The published multiplier is 0x4000, the bank multiplier and the third trim
    word are 0x6400, and signed transient word 0xFFFF2300 is zero.
    """
    scheduled = bfs_raw * AF_STATE_NEUTRAL >> 17
    precursor = min(0xFFFF, scheduled * gain_raw >> 14)
    precursor = max(precursor, calibration.pulse_precursor_floor)
    delta = max(0, stft_raw + ltft_raw + STFT_NEUTRAL - TRIM_NEUTRAL_SUM)
    opening = (
        (PULSE_OPENING_BATTERY_REFERENCE - battery_raw)
        * calibration.pulse_opening_slope
        >> 7
    ) + calibration.pulse_opening_base
    return min(0xFFFF, (precursor * delta >> 16) + max(0, opening))


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_by_channel_name() -> dict[str, str]:
    return {
        binding.spec.name: binding.source
        for binding in recording.build_bindings("tuning")
    }


def read_recording(path: Path) -> Recording:
    """Decode every data block of one MLVLG file into raw columns by source."""
    path = Path(path)
    mlvlg.validate_mlg(path)
    fields = mlvlg.read_fields(path)
    data = path.read_bytes()
    _signature, _version, _stamp, _info, data_begin, record_length, _count = (
        struct.unpack(">6sHIIIHH", data[:mlvlg.MLG_HEADER_SIZE])
    )
    record_struct = struct.Struct(
        ">" + "".join(mlvlg.FIELD_STRUCTS[field.field_type][1:] for field in fields)
    )
    columns: dict[str, list[float]] = {}
    source_names = _source_by_channel_name()
    sources = []
    for field in fields:
        source = source_names.get(field.name.replace("*", ""))
        sources.append(source)
        if source is not None:
            columns[source] = []
    offset = data_begin
    records = 0
    while offset < len(data):
        block_type = data[offset]
        if block_type == 0:
            payload = data[offset + 4 : offset + 4 + record_length]
            values = record_struct.unpack(payload)
            for source, value in zip(sources, values):
                if source is not None:
                    columns[source].append(value)
            records += 1
            offset += 4 + record_length + 1
        else:
            offset += 4 + mlvlg.MLG_MARKER_MESSAGE_SIZE
    return Recording(path, _sha256_file(path), fields, columns, records)


def _ints(recording_: Recording, source: str) -> list[int] | None:
    column = recording_.columns.get(source)
    if column is None:
        return None
    return [int(round(value)) for value in column]


def engine_speed_counts(recording_: Recording) -> list[int | None] | None:
    """Engine speed per record in the RPM/12.5 counts of FFFF11F4.

    The stock engine-speed channel carries the word the coordinate is a shift
    of. A record without that value, such as one written before the first
    stock engine-speed frame, holds no count.
    """

    stock = recording_.columns.get("stock_rpm")
    if stock is None:
        return None
    return [rpm_counts(value) for value in stock]


def steady_mask(columns: list[list[int]], hold: int) -> list[bool]:
    """Mark records whose listed inputs are unchanged over the previous hold records."""
    length = len(columns[0])
    mask = [False] * length
    for index in range(hold, length):
        mask[index] = all(
            column[index - back] == column[index]
            for column in columns
            for back in range(1, hold + 1)
        )
    return mask


def percentile_nearest_rank(values: list[int | float], percentile: float):
    ordered = sorted(values)
    rank = max(1, math.ceil(percentile / 100 * len(ordered)))
    return ordered[rank - 1]


def _share(count: int, total: int) -> float:
    return count / total if total else 0.0


def pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 2:
        return 0.0
    mean_x = statistics.fmean(xs)
    mean_y = statistics.fmean(ys)
    covariance = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    variance_x = sum((x - mean_x) ** 2 for x in xs)
    variance_y = sum((y - mean_y) ** 2 for y in ys)
    if variance_x == 0 or variance_y == 0:
        return 0.0
    return covariance / math.sqrt(variance_x * variance_y)


def linear_fit(xs: list[float], ys: list[float]) -> tuple[float, float]:
    mean_x = statistics.fmean(xs)
    mean_y = statistics.fmean(ys)
    variance = sum((x - mean_x) ** 2 for x in xs)
    if variance == 0:
        return 0.0, mean_y
    slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / variance
    return slope, mean_y - slope * mean_x


def audit_duty_pairs(recording_: Recording) -> dict:
    result = {}
    for bank in (1, 2):
        monitor = _ints(recording_, f"intake_cvtc_duty_b{bank}_raw")
        command = _ints(recording_, f"intake_cvtc_duty_command_b{bank}_raw")
        if monitor is None or command is None:
            continue
        pairs = [
            (m, c) for m, c in zip(monitor, command) if m > 0 and c > 0
        ]
        prefix = f"intake_duty_b{bank}"
        result[f"{prefix}_monitor_max_raw"] = max(monitor)
        result[f"{prefix}_command_max_raw"] = max(command)
        result[f"{prefix}_nonzero_pair_count"] = len(pairs)
        if not pairs:
            continue
        differences = [m - c for m, c in pairs]
        result[f"{prefix}_monitor_minus_command_mean"] = statistics.fmean(
            differences
        )
        result[f"{prefix}_equal_share"] = _share(
            sum(1 for value in differences if value == 0), len(differences)
        )
        result[f"{prefix}_within_three_share"] = _share(
            sum(1 for value in differences if abs(value) <= DUTY_TOLERANCE),
            len(differences),
        )
        result[f"{prefix}_correlation"] = pearson(
            [float(m) for m, _ in pairs], [float(c) for _, c in pairs]
        )
    return result


def audit_cvtc_tracking(recording_: Recording, target_hold: int) -> dict:
    result = {}
    for family in ("intake", "exhaust"):
        target = _ints(recording_, f"{family}_cvtc_target_raw")
        if target is None:
            continue
        steady = steady_mask([target], target_hold)
        for bank in (1, 2):
            actual = _ints(recording_, f"{family}_cvtc_actual_b{bank}_raw")
            if actual is None:
                continue
            errors = [
                a - t for a, t, keep in zip(actual, target, steady) if keep
            ]
            prefix = f"{family}_cvtc_b{bank}_steady_target"
            result[f"{prefix}_sample_count"] = len(errors)
            if not errors:
                continue
            result[f"{prefix}_within_two_share"] = _share(
                sum(1 for value in errors if abs(value) <= CVTC_TOLERANCE),
                len(errors),
            )
            result[f"{prefix}_error_p5"] = percentile_nearest_rank(errors, 5)
            result[f"{prefix}_error_p95"] = percentile_nearest_rank(errors, 95)
    return result


def audit_maf_chain(
    recording_: Recording, calibration: RelationCalibration, hold: int
) -> dict:
    maf_b1 = _ints(recording_, "maf_b1_raw")
    maf_b2 = _ints(recording_, "maf_b2_raw")
    total = _ints(recording_, "maf_total_raw")
    if maf_b1 is None or maf_b2 is None or total is None:
        return {}
    steady = steady_mask([maf_b1, maf_b2], hold)
    errors = []
    ratios = []
    for b1, b2, observed, keep in zip(maf_b1, maf_b2, total, steady):
        if not keep:
            continue
        output_a, output_b, predicted = maf_total_raw(calibration, b1, b2)
        errors.append(observed - predicted)
        if output_a + output_b:
            ratios.append(observed / (output_a + output_b))
    result = {"maf_chain_steady_sample_count": len(errors)}
    if errors:
        result["maf_chain_exact_share"] = _share(
            sum(1 for value in errors if value == 0), len(errors)
        )
        result["maf_chain_within_one_share"] = _share(
            sum(1 for value in errors if abs(value) <= 1), len(errors)
        )
        result["maf_total_over_transfer_sum_median"] = statistics.median(
            ratios
        )
    return result


def audit_calculated_load(
    recording_: Recording, calibration: RelationCalibration
) -> dict:
    bfs = _ints(recording_, "bfs_raw")
    rpm = engine_speed_counts(recording_)
    load = _ints(recording_, "calculated_load_raw")
    if bfs is None or rpm is None or load is None:
        return {}
    predicted = [
        None
        if r is None
        else calculated_load_raw(b, r, calibration.calculated_load_reference)
        for b, r in zip(bfs, rpm)
    ]
    result = {}
    for lag, label in ((0, "same_record"), (1, "prior_record")):
        errors = [
            load[index] - predicted[index - lag]
            for index in range(lag, len(load))
            if predicted[index - lag] is not None
        ]
        result[f"calculated_load_{label}_comparison_count"] = len(errors)
        if errors:
            result[f"calculated_load_{label}_exact_share"] = _share(
                sum(1 for value in errors if value == 0), len(errors)
            )
            result[f"calculated_load_{label}_within_one_share"] = _share(
                sum(1 for value in errors if abs(value) <= 1), len(errors)
            )
    return result


def audit_bfs_producer(
    recording_: Recording, calibration: RelationCalibration, hold: int
) -> dict:
    maf_b1 = _ints(recording_, "maf_b1_raw")
    maf_b2 = _ints(recording_, "maf_b2_raw")
    bfs = _ints(recording_, "bfs_raw")
    rpm = engine_speed_counts(recording_)
    if maf_b1 is None or maf_b2 is None or bfs is None or rpm is None:
        return {}
    steady = steady_mask([maf_b1, maf_b2, rpm], hold)
    ratios = []
    for b1, b2, observed, count, keep in zip(maf_b1, maf_b2, bfs, rpm, steady):
        if not keep or count is None:
            continue
        output_a, output_b, _total = maf_total_raw(calibration, b1, b2)
        reference = bfs_reference_raw(
            calibration, output_a + output_b, 2 * count
        )
        if reference:
            ratios.append(observed / reference)
    result = {"bfs_steady_sample_count": len(ratios)}
    if ratios:
        result["bfs_over_producer_reference_median"] = statistics.median(ratios)
        result["bfs_over_producer_reference_p5"] = percentile_nearest_rank(
            ratios, 5
        )
        result["bfs_over_producer_reference_p95"] = percentile_nearest_rank(
            ratios, 95
        )
    return result


def audit_injection_fit(recording_: Recording) -> dict:
    bfs = _ints(recording_, "bfs_raw")
    af_state = _ints(recording_, "af_state_factor_raw")
    mask = _ints(recording_, "fuel_inhibit_mask")
    if bfs is None or af_state is None or mask is None:
        return {}
    result = {}
    for bank, channel in ((1, 0), (2, 1)):
        stft = _ints(recording_, f"stft_b{bank}_raw")
        pulse = _ints(recording_, f"injection_{channel}_raw")
        if stft is None or pulse is None:
            continue
        xs = []
        ys = []
        for b, a, m, s, p in zip(bfs, af_state, mask, stft, pulse):
            if a != AF_STATE_NEUTRAL or m != 0 or p <= 0:
                continue
            xs.append(b * s / STFT_NEUTRAL / 2048 * 100)
            ys.append(float(p))
        prefix = f"injection_b{bank}_closed_loop"
        result[f"{prefix}_sample_count"] = len(xs)
        if len(xs) < 2:
            continue
        slope, intercept = linear_fit(xs, ys)
        result[f"{prefix}_slope"] = slope
        result[f"{prefix}_intercept_raw"] = intercept
        result[f"{prefix}_correlation"] = pearson(xs, ys)
    return result


def audit_injection_chain(
    recording_: Recording,
    calibration: RelationCalibration,
    hold: int,
    tolerance: float = 0.02,
) -> dict:
    """Replay the code chain from Base Fuel Schedule to both bank pulse words.

    A record qualifies when the schedule stays within the tolerance over the
    previous hold records, which keeps signed transient word 0xFFFF2300 and the
    rate-limited fuel multiplier out of the comparison.
    """
    if calibration.pulse_gain_pressure_slope:
        return {}
    names = (
        "bfs_raw",
        "af_state_factor_raw",
        "fuel_inhibit_mask",
        "iat_raw",
        "battery_voltage_raw",
    )
    columns = {name: _ints(recording_, name) for name in names}
    rpm = engine_speed_counts(recording_)
    if rpm is None or any(column is None for column in columns.values()):
        return {}
    bfs = columns["bfs_raw"]
    result = {}
    for bank, channel in ((1, 0), (2, 1)):
        stft = _ints(recording_, f"stft_b{bank}_raw")
        ltft = _ints(recording_, f"ltft_b{bank}_raw")
        pulse = _ints(recording_, f"injection_{channel}_raw")
        if stft is None or ltft is None or pulse is None:
            continue
        ratios = []
        gains = []
        within_two_percent = 0
        for index in range(hold, len(bfs)):
            if (
                columns["af_state_factor_raw"][index] != AF_STATE_NEUTRAL
                or columns["fuel_inhibit_mask"][index] != 0
                or pulse[index] <= 0
                or rpm[index] is None
            ):
                continue
            window = bfs[index - hold : index + 1]
            if max(window) - min(window) > tolerance * window[-1]:
                continue
            gain = common_pulse_gain_raw(
                calibration,
                bfs[index],
                columns["iat_raw"][index],
                min(0xFF, rpm[index] >> 1),
            )
            reference = pulse_reference_raw(
                calibration,
                bfs[index],
                gain,
                stft[index],
                ltft[index],
                columns["battery_voltage_raw"][index],
            )
            ratios.append(pulse[index] / reference)
            gains.append(gain / 16384)
            within_two_percent += abs(pulse[index] - reference) <= 0.02 * reference
        prefix = f"injection_b{bank}_chain"
        result[f"{prefix}_sample_count"] = len(ratios)
        if not ratios:
            continue
        result[f"{prefix}_over_reference_median"] = statistics.median(ratios)
        result[f"{prefix}_over_reference_p5"] = percentile_nearest_rank(ratios, 5)
        result[f"{prefix}_over_reference_p95"] = percentile_nearest_rank(ratios, 95)
        result[f"{prefix}_within_two_percent_share"] = _share(
            within_two_percent, len(ratios)
        )
        result[f"{prefix}_gain_median"] = statistics.median(gains)
        result[f"{prefix}_gain_range"] = [min(gains), max(gains)]
    return result


def audit_timing_command(recording_: Recording) -> dict:
    final = _ints(recording_, "final_timing_raw")
    command = _ints(recording_, "apc_command_raw")
    if final is None or command is None:
        return {}
    matches = sum(
        1 for f, c in zip(final, command) if (APC_COMMAND_BASE - f) & 0xFF == c
    )
    return {
        "final_timing_apc_pair_count": len(final),
        "final_timing_apc_identity_share": _share(matches, len(final)),
    }


def audit_states(recording_: Recording) -> dict:
    result = {}
    mask = _ints(recording_, "fuel_inhibit_mask")
    if mask is not None:
        counts = Counter(mask)
        result["fuel_inhibit_mask_values"] = sorted(counts)
        result["fuel_inhibit_full_mask_sample_count"] = counts.get(0x3F, 0)
    state = _ints(recording_, "knock_timing_state_raw")
    if state is not None:
        steps = Counter(
            state[index] - state[index - 1]
            for index in range(1, len(state))
            if state[index] != state[index - 1]
        )
        result["knock_state_min"] = min(state)
        result["knock_state_event_step_count"] = steps.get(KNOCK_EVENT_STEP, 0)
        result["knock_state_recovery_step_count"] = steps.get(
            KNOCK_RECOVERY_STEP, 0
        )
        result["knock_state_change_count"] = sum(steps.values())
    selected = _ints(recording_, "high_detonation_selected")
    if selected is not None:
        result["high_detonation_selected_count"] = sum(
            1 for value in selected if value
        )
    for bank in (1, 2):
        ltft = _ints(recording_, f"ltft_b{bank}_raw")
        if ltft is not None:
            result[f"ltft_b{bank}_values"] = sorted(set(ltft))
    for source, key in (
        ("coolant_raw", "coolant_raw_range"),
        ("iat_raw", "iat_raw_range"),
        ("battery_voltage_raw", "battery_raw_range"),
        ("injection_end_angle_raw", "injection_end_angle_raw_range"),
    ):
        column = _ints(recording_, source)
        if column:
            result[key] = [min(column), max(column)]
    return result


def audit_recording(
    recording_: Recording,
    calibration: RelationCalibration,
    *,
    hold: int = 6,
    target_hold: int = 100,
    schedule_hold: int = 50,
) -> dict:
    result = {
        "capture_name": recording_.path.name,
        "capture_sha256": recording_.sha256,
        "calibration_image_sha256": calibration.image_sha256,
        "record_count": recording_.record_count,
        "steady_input_hold_records": hold,
        "steady_target_hold_records": target_hold,
        "steady_schedule_hold_records": schedule_hold,
    }
    result.update(audit_duty_pairs(recording_))
    result.update(audit_cvtc_tracking(recording_, target_hold))
    result.update(audit_maf_chain(recording_, calibration, hold))
    result.update(audit_calculated_load(recording_, calibration))
    result.update(audit_bfs_producer(recording_, calibration, hold))
    result.update(audit_injection_fit(recording_))
    result.update(audit_injection_chain(recording_, calibration, schedule_hold))
    result.update(audit_timing_command(recording_))
    result.update(audit_states(recording_))
    return result


def format_value(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return f"{value:.6f}"
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(format_value(item) for item in value) + "]"
    return '"' + str(value).replace('"', '\\"') + '"'


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="+", type=Path)
    parser.add_argument("--rom", default="JK08A")
    parser.add_argument("--calibration-image", type=Path)
    parser.add_argument("--hold", type=int, default=6)
    parser.add_argument("--target-hold", type=int, default=100)
    parser.add_argument("--schedule-hold", type=int, default=50)
    args = parser.parse_args(argv)
    calibration = load_calibration(args.rom, args.calibration_image)
    for index, log in enumerate(args.logs):
        if index:
            print()
        result = audit_recording(
            read_recording(log),
            calibration,
            hold=args.hold,
            target_hold=args.target_hold,
            schedule_hold=args.schedule_hold,
        )
        for key, value in result.items():
            print(f"{key} = {format_value(value)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
