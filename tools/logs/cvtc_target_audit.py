#!/usr/bin/env python3
"""Replay JK08A intake- or exhaust-CVTC target maps against a tuning TRC or MLG."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import math
from pathlib import Path
import statistics
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.can_dashboard.model import DashboardModel, FrameRecord
from tools.logs import can_telemetry, mlg_relation_audit, peak_trc_audit
from tools.logs.load_axis_audit import (
    internal_load_raw,
    interpolate_implicit_u16,
)
from tools.mapkit import rom as romkit


INTERNAL_LOAD_SCALER_ADDRESS = 0x9534
CVTC_MAIN_MAP_ADDRESS = 0xB43A
CVTC_MAIN_RPM_AXIS_ADDRESS = 0x12F3E
CVTC_MAIN_LOAD_AXIS_ADDRESS = 0x12F1E
CVTC_MAIN_SIZE = 16
CVTC_COLD_MAP_ADDRESS = 0xB53A
CVTC_COLD_RPM_AXIS_ADDRESS = 0x12ECA
CVTC_COLD_LOAD_AXIS_ADDRESS = 0x12EAA
CVTC_COLD_SIZE = 8
CVTC_CORRECTION_MAP_ADDRESS = 0xAB5A
CVTC_CORRECTION_RPM_AXIS_ADDRESS = 0x12F9A
CVTC_CORRECTION_LOAD_AXIS_ADDRESS = 0x12F92
CVTC_CORRECTION_SIZE = 4
CVTC_CORRECTION_STATE_MASK = 0x40
CVTC_WARM_THRESHOLD_ADDRESS = 0x8D2D
CVTC_COLD_THRESHOLD_ADDRESS = 0x8D2E

EXHAUST_CVTC_MAIN_MAP_ADDRESS = 0xB33A
EXHAUST_CVTC_MAIN_RPM_AXIS_ADDRESS = 0x12F2E
EXHAUST_CVTC_MAIN_LOAD_AXIS_ADDRESS = 0x12F0E
EXHAUST_CVTC_COLD_MAP_ADDRESS = 0xB2FA
EXHAUST_CVTC_COLD_RPM_AXIS_ADDRESS = 0x12EC2
EXHAUST_CVTC_COLD_LOAD_AXIS_ADDRESS = 0x12EA2
EXHAUST_CVTC_CORRECTION_MAP_ADDRESS = 0xAB4A
EXHAUST_CVTC_CORRECTION_RPM_AXIS_ADDRESS = 0x12F96
EXHAUST_CVTC_CORRECTION_LOAD_AXIS_ADDRESS = 0x12F8E

# FUN_000BDB66 forms byte 0xFFFF1553 from engine-speed table 0x122EA and
# coolant-index weight 0x122F2. FUN_000BDC66 conditions it in place of the
# coolant-selected intake byte while 0xFFFF24A7 bit 1 is set.
INTAKE_ALTERNATE_TABLE_ADDRESS = 0x122EA
INTAKE_ALTERNATE_AXIS_ADDRESS = 0x12F66
INTAKE_ALTERNATE_POINTS = 8
INTAKE_ALTERNATE_WEIGHT_ADDRESS = 0x122F2
INTAKE_ALTERNATE_WEIGHT_POINTS = 16
INTAKE_ALTERNATE_WEIGHT_STEP = 16

COOLANT_BANDS = ("cold", "blend", "warm")
CVTC_INPUT_FIELDS = (
    "bfs_raw",
    "rpm_raw",
    "coolant_raw",
    "knock_surface_state",
    "intake_cvtc_target_raw",
    "exhaust_cvtc_target_raw",
    "intake_cvtc_actual_b1_raw",
    "intake_cvtc_actual_b2_raw",
)
MLG_SIGNATURE = b"MLVLG\x00"
# A hold-last bridge record of the dashboard recorder rewrites only these
# channels and repeats every other channel of the preceding record.
MLG_BRIDGE_TIME_SOURCES = ("date", "elapsed")


@dataclass(frozen=True)
class ExplicitU8Map:
    address: int
    row_axis: tuple[int, ...]
    column_axis: tuple[int, ...]
    table: tuple[tuple[int, ...], ...]


@dataclass(frozen=True)
class IntakeAlternateSource:
    speed_axis: tuple[int, ...]
    speed_table: tuple[int, ...]
    coolant_weight: tuple[int, ...]


@dataclass(frozen=True)
class CvtcCalibration:
    image_source: Path
    image_sha256: str
    load_scaler: int
    main: ExplicitU8Map
    cold: ExplicitU8Map
    correction: ExplicitU8Map
    cold_threshold: int
    warm_threshold: int
    target: str
    conditioned_reference: str
    alternate_source: IntakeAlternateSource | None = None


@dataclass(frozen=True)
class CvtcSample:
    timestamp: float
    run: int
    tick: int
    bfs_raw: int
    rpm_raw: int
    coolant_raw: int
    coolant_age_ms: float
    knock_surface_state: int
    reference_a_raw: int
    reference_b_raw: int
    intake_actual_b1_raw: int
    intake_actual_b2_raw: int


@dataclass(frozen=True)
class ReplayPoint:
    load_raw: int
    rpm50_raw: int
    cold_raw: int
    main_base_raw: int
    correction_raw: int
    main_selected_raw: int
    coolant_selected_raw: int
    coolant_band: str
    correction_active: bool
    alternate_source_raw: int | None = None


@dataclass(frozen=True)
class ErrorSummary:
    comparisons: int
    exact: int
    within_one: int
    within_two: int
    mean_signed: float
    mean_absolute: float
    median_absolute: float
    p95_absolute: int
    maximum_absolute: int
    common_signed_errors: tuple[tuple[int, int], ...]


@dataclass(frozen=True)
class StableActiveSummary:
    unchanged_source_cycles: int
    errors: ErrorSummary


@dataclass(frozen=True)
class AlignmentSummary:
    source_lag: int
    comparisons: int
    selected_to_reference_a: ErrorSummary
    selected_to_reference_b: ErrorSummary
    selected_to_intake_actual_b1: ErrorSummary
    selected_to_intake_actual_b2: ErrorSummary
    without_conditioned_neutralization: ErrorSummary | None
    active_to_active: ErrorSummary | None
    conditioned_neutralization_count: int
    conditioned_neutralization_runs: int
    stable_active: tuple[StableActiveSummary, ...]
    correction_active_count: int
    coolant_band_counts: tuple[tuple[str, int], ...]
    selected_raw_range: tuple[int, int]
    alternate_source_to_reference: ErrorSummary | None = None
    alternate_source_active_to_active: ErrorSummary | None = None
    cold_dependent_active_to_active: ErrorSummary | None = None


@dataclass(frozen=True)
class TraceCvtcAudit:
    source: Path
    source_sha256: str
    source_format: str
    target: str
    calibration_image_source: Path
    calibration_image_sha256: str
    source_frames: int | None
    source_records: int | None
    bridge_records: int | None
    complete_snapshots: int
    analyzed_snapshots: int
    coolant_bands: tuple[str, ...]
    load_scaler: int
    cold_threshold: int
    warm_threshold: int
    coolant_raw_range: tuple[int, int]
    coolant_age_max_ms: float | None
    reference_a_raw_range: tuple[int, int]
    reference_b_raw_range: tuple[int, int]
    intake_actual_b1_raw_range: tuple[int, int]
    intake_actual_b2_raw_range: tuple[int, int]
    alignments: tuple[AlignmentSummary, ...]


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_map(image, address, size, row_axis_address, column_axis_address):
    return ExplicitU8Map(
        address=address,
        row_axis=tuple(image.values(row_axis_address, size, "uint8")),
        column_axis=tuple(image.values(column_axis_address, size, "uint8")),
        table=tuple(
            tuple(row)
            for row in image.table(address, size, size, "uint8")
        ),
    )


def load_calibration(
    rom: str = "JK08A",
    calibration_image: Path | None = None,
    target: str = "intake",
) -> CvtcCalibration:
    if calibration_image is None:
        image = romkit.load(rom)
        image_source = Path(image.path)
    else:
        image_source = Path(calibration_image).resolve()
        data = image_source.read_bytes()
        image = romkit.Image(image_source.name, str(image_source), data)
    if target == "intake":
        main = (
            CVTC_MAIN_MAP_ADDRESS,
            CVTC_MAIN_SIZE,
            CVTC_MAIN_RPM_AXIS_ADDRESS,
            CVTC_MAIN_LOAD_AXIS_ADDRESS,
        )
        cold = (
            CVTC_COLD_MAP_ADDRESS,
            CVTC_COLD_SIZE,
            CVTC_COLD_RPM_AXIS_ADDRESS,
            CVTC_COLD_LOAD_AXIS_ADDRESS,
        )
        correction = (
            CVTC_CORRECTION_MAP_ADDRESS,
            CVTC_CORRECTION_SIZE,
            CVTC_CORRECTION_RPM_AXIS_ADDRESS,
            CVTC_CORRECTION_LOAD_AXIS_ADDRESS,
        )
        conditioned_reference = "reference_a_raw"
        alternate_source = IntakeAlternateSource(
            speed_axis=tuple(
                image.values(
                    INTAKE_ALTERNATE_AXIS_ADDRESS,
                    INTAKE_ALTERNATE_POINTS,
                    "uint8",
                )
            ),
            speed_table=tuple(
                image.values(
                    INTAKE_ALTERNATE_TABLE_ADDRESS,
                    INTAKE_ALTERNATE_POINTS,
                    "uint8",
                )
            ),
            coolant_weight=tuple(
                image.values(
                    INTAKE_ALTERNATE_WEIGHT_ADDRESS,
                    INTAKE_ALTERNATE_WEIGHT_POINTS,
                    "uint8",
                )
            ),
        )
    elif target == "exhaust":
        main = (
            EXHAUST_CVTC_MAIN_MAP_ADDRESS,
            CVTC_MAIN_SIZE,
            EXHAUST_CVTC_MAIN_RPM_AXIS_ADDRESS,
            EXHAUST_CVTC_MAIN_LOAD_AXIS_ADDRESS,
        )
        cold = (
            EXHAUST_CVTC_COLD_MAP_ADDRESS,
            CVTC_COLD_SIZE,
            EXHAUST_CVTC_COLD_RPM_AXIS_ADDRESS,
            EXHAUST_CVTC_COLD_LOAD_AXIS_ADDRESS,
        )
        correction = (
            EXHAUST_CVTC_CORRECTION_MAP_ADDRESS,
            CVTC_CORRECTION_SIZE,
            EXHAUST_CVTC_CORRECTION_RPM_AXIS_ADDRESS,
            EXHAUST_CVTC_CORRECTION_LOAD_AXIS_ADDRESS,
        )
        conditioned_reference = "reference_b_raw"
        alternate_source = None
    else:
        raise ValueError(f"unknown CVTC target {target!r}")

    return CvtcCalibration(
        image_source=image_source,
        image_sha256=hashlib.sha256(image.data).hexdigest(),
        load_scaler=image.values(
            INTERNAL_LOAD_SCALER_ADDRESS, 1, "uint16"
        )[0],
        main=_load_map(image, *main),
        cold=_load_map(image, *cold),
        correction=_load_map(image, *correction),
        cold_threshold=image.values(
            CVTC_COLD_THRESHOLD_ADDRESS, 1, "uint8"
        )[0],
        warm_threshold=image.values(
            CVTC_WARM_THRESHOLD_ADDRESS, 1, "uint8"
        )[0],
        target=target,
        conditioned_reference=conditioned_reference,
        alternate_source=alternate_source,
    )


def _require_u8(value: int, name: str) -> None:
    if type(value) is not int or not 0 <= value <= 0xFF:
        raise ValueError(f"{name} must be an unsigned 8-bit integer")


def _linear_u8(first: int, second: int, fraction: int) -> int:
    _require_u8(first, "first")
    _require_u8(second, "second")
    if type(fraction) is not int or not 0 <= fraction <= 0xFFFF:
        raise ValueError("fraction must be a Q0.16 unsigned integer")
    if second < first:
        return first - ((first - second) * fraction >> 16)
    return first + ((second - first) * fraction >> 16)


def explicit_axis_position(axis: tuple[int, ...], key: int) -> tuple[int, int]:
    """Return the stock byte-axis lower index and Q0.16 fraction."""
    _require_u8(key, "key")
    if len(axis) < 2 or len(axis) > 256:
        raise ValueError("axis must contain 2..256 points")
    if any(type(value) is not int or not 0 <= value <= 0xFF for value in axis):
        raise ValueError("axis points must be unsigned 8-bit integers")
    if any(first > second for first, second in zip(axis, axis[1:])):
        raise ValueError("axis points must be nondecreasing")

    if key <= axis[0]:
        return 0, 0
    if key >= axis[-1]:
        return len(axis) - 1, 0
    for index in range(len(axis) - 2, -1, -1):
        lower = axis[index]
        if key == lower:
            return index, 0
        if key > lower:
            delta = axis[index + 1] - lower
            if delta == 0:
                return index, 0
            return index, ((key - lower) << 16) // delta
    return 0, 0


def interpolate_explicit_u8(
    calibration: ExplicitU8Map,
    row_key: int,
    column_key: int,
) -> int:
    """Reproduce wrappers 0x26084/0x26140/0x261B8 and finisher 0x26770."""
    rows = len(calibration.row_axis)
    columns = len(calibration.column_axis)
    if len(calibration.table) != rows or any(
        len(row) != columns for row in calibration.table
    ):
        raise ValueError("map geometry differs from its axes")
    row_index, row_fraction = explicit_axis_position(
        calibration.row_axis, row_key
    )
    column_index, column_fraction = explicit_axis_position(
        calibration.column_axis, column_key
    )
    first = calibration.table[row_index][column_index]
    if column_fraction:
        first = _linear_u8(
            first,
            calibration.table[row_index][column_index + 1],
            column_fraction,
        )
    if not row_fraction:
        return first
    second = calibration.table[row_index + 1][column_index]
    if column_fraction:
        second = _linear_u8(
            second,
            calibration.table[row_index + 1][column_index + 1],
            column_fraction,
        )
    return _linear_u8(first, second, row_fraction)


def conditional_main_target(
    main_raw: int,
    correction_raw: int,
    knock_surface_state: int,
) -> int:
    _require_u8(main_raw, "main_raw")
    _require_u8(correction_raw, "correction_raw")
    _require_u8(knock_surface_state, "knock_surface_state")
    if not knock_surface_state & CVTC_CORRECTION_STATE_MASK:
        return main_raw
    return min(0xFF, max(0, main_raw - correction_raw + 0x80))


def _trunc_div(dividend: int, divisor: int) -> int:
    if divisor == 0:
        return 0
    quotient = abs(dividend) // abs(divisor)
    return -quotient if (dividend < 0) != (divisor < 0) else quotient


def coolant_selected_target(
    cold_raw: int,
    main_raw: int,
    coolant_raw: int,
    cold_threshold: int,
    warm_threshold: int,
) -> tuple[int, str]:
    """Reproduce the exact cold/main selector at 0xBDD80..0xBDE04."""
    for value, name in (
        (cold_raw, "cold_raw"),
        (main_raw, "main_raw"),
        (coolant_raw, "coolant_raw"),
        (cold_threshold, "cold_threshold"),
        (warm_threshold, "warm_threshold"),
    ):
        _require_u8(value, name)
    if cold_threshold >= warm_threshold:
        raise ValueError("cold threshold must be below warm threshold")
    if coolant_raw <= cold_threshold:
        return cold_raw, "cold"
    if coolant_raw > warm_threshold:
        return main_raw, "warm"
    span = warm_threshold - cold_threshold
    delta = _trunc_div(
        (coolant_raw - cold_threshold) * (main_raw - cold_raw),
        span,
    )
    return min(0xFF, max(0, cold_raw + delta)), "blend"


def coolant_index(coolant_raw: int) -> int:
    """Reproduce FUN_00039634, the producer of coolant index 0xFFFF1077."""
    _require_u8(coolant_raw, "coolant_raw")
    if coolant_raw < 10:
        return 0
    if coolant_raw >= 170:
        return 0xFF
    return 240 * (coolant_raw - 10) // 150


def intake_alternate_target(
    source: IntakeAlternateSource,
    rpm50_raw: int,
    coolant_raw: int,
) -> int:
    """Reproduce byte 0xFFFF1553 of FUN_000BDB66.

    The engine-speed lookup is centered on 0x80, weighted by the Q0.7
    coolant-index lookup, divided by 128 toward zero, recentered, and
    saturated to a byte.
    """
    if len(source.speed_table) != len(source.speed_axis):
        raise ValueError("alternate table geometry differs from its axis")
    index, fraction = explicit_axis_position(source.speed_axis, rpm50_raw)
    speed_raw = source.speed_table[index]
    if fraction:
        speed_raw = _linear_u8(
            speed_raw, source.speed_table[index + 1], fraction
        )
    weight = interpolate_implicit_u16(
        source.coolant_weight,
        coolant_index(coolant_raw),
        INTAKE_ALTERNATE_WEIGHT_STEP,
    )
    value = 0x80 + _trunc_div((speed_raw - 0x80) * weight, 0x80)
    return min(0xFF, max(0, value))


def replay_point(calibration: CvtcCalibration, sample: CvtcSample) -> ReplayPoint:
    load_raw = internal_load_raw(sample.bfs_raw, calibration.load_scaler)
    rpm50_raw = min(0xFF, sample.rpm_raw >> 2)
    cold_raw = interpolate_explicit_u8(
        calibration.cold, rpm50_raw, load_raw
    )
    main_base_raw = interpolate_explicit_u8(
        calibration.main, rpm50_raw, load_raw
    )
    correction_raw = interpolate_explicit_u8(
        calibration.correction, rpm50_raw, load_raw
    )
    main_selected_raw = conditional_main_target(
        main_base_raw, correction_raw, sample.knock_surface_state
    )
    selected_raw, coolant_band = coolant_selected_target(
        cold_raw,
        main_selected_raw,
        sample.coolant_raw,
        calibration.cold_threshold,
        calibration.warm_threshold,
    )
    return ReplayPoint(
        load_raw=load_raw,
        rpm50_raw=rpm50_raw,
        cold_raw=cold_raw,
        main_base_raw=main_base_raw,
        correction_raw=correction_raw,
        main_selected_raw=main_selected_raw,
        coolant_selected_raw=selected_raw,
        coolant_band=coolant_band,
        correction_active=bool(
            sample.knock_surface_state & CVTC_CORRECTION_STATE_MASK
        ),
        alternate_source_raw=(
            None
            if calibration.alternate_source is None
            else intake_alternate_target(
                calibration.alternate_source, rpm50_raw, sample.coolant_raw
            )
        ),
    )


def _percentile_nearest_rank(values: list[int], percentile: float) -> int:
    if not values:
        raise ValueError("at least one value is required")
    index = max(0, math.ceil(percentile * len(values)) - 1)
    return sorted(values)[index]


def _error_summary(errors: list[int]) -> ErrorSummary:
    if not errors:
        raise ValueError("at least one comparison is required")
    absolute = [abs(error) for error in errors]
    return ErrorSummary(
        comparisons=len(errors),
        exact=sum(error == 0 for error in errors),
        within_one=sum(value <= 1 for value in absolute),
        within_two=sum(value <= 2 for value in absolute),
        mean_signed=statistics.fmean(errors),
        mean_absolute=statistics.fmean(absolute),
        median_absolute=statistics.median(absolute),
        p95_absolute=_percentile_nearest_rank(absolute, 0.95),
        maximum_absolute=max(absolute),
        common_signed_errors=tuple(Counter(errors).most_common(5)),
    )


def _optional_error_summary(errors: list[int]) -> ErrorSummary | None:
    return _error_summary(errors) if errors else None


def _trace_samples(trace, profile: str, can_id: int, tick_divisor: int):
    model = DashboardModel(profile, can_id, tick_divisor)
    samples = []
    for frame in trace.frames:
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
        if not all(name in model.raw for name in CVTC_INPUT_FIELDS):
            continue
        coolant_updated = model.updated_at["coolant_raw"]
        samples.append(
            CvtcSample(
                timestamp=timestamp,
                run=snapshot.run,
                tick=snapshot.unwrapped_tick,
                bfs_raw=model.raw["bfs_raw"],
                rpm_raw=model.raw["rpm_raw"],
                coolant_raw=model.raw["coolant_raw"],
                coolant_age_ms=(timestamp - coolant_updated) * 1000,
                knock_surface_state=model.raw["knock_surface_state"],
                reference_a_raw=model.raw["intake_cvtc_target_raw"],
                reference_b_raw=model.raw["exhaust_cvtc_target_raw"],
                intake_actual_b1_raw=model.raw["intake_cvtc_actual_b1_raw"],
                intake_actual_b2_raw=model.raw["intake_cvtc_actual_b2_raw"],
            )
        )
    return model, samples


def is_mlg(path: Path) -> bool:
    """Report whether a capture starts with the MLVLG signature."""
    with Path(path).open("rb") as source:
        return source.read(len(MLG_SIGNATURE)) == MLG_SIGNATURE


def _raw_limits(profile: str) -> dict[str, tuple[int, int]]:
    """Return the wire range of every fixed and context field of a profile."""
    _document, profiles = can_telemetry.load_schema(can_telemetry.DEFAULT_SCHEMA)
    try:
        selected = profiles[profile]
    except KeyError as error:
        raise ValueError(f"unknown telemetry profile {profile!r}") from error
    fields = list(selected["fields"])
    for context in selected.get("contexts", ()):
        fields.extend(context["fields"])
    limits = {}
    for field in fields:
        bits = 8 * field["width"]
        if field["signed"]:
            limits[field["name"]] = (-(1 << (bits - 1)), (1 << (bits - 1)) - 1)
        else:
            limits[field["name"]] = (0, (1 << bits) - 1)
    return limits


def _same_record_value(first: float, second: float) -> bool:
    return first == second or (math.isnan(first) and math.isnan(second))


def _recording_samples(recording, profile: str):
    """Recover the verified snapshots of one dashboard MLG recording.

    The recorder stores every telemetry field as its raw wire integer in F32,
    which is exact for the 8- and 16-bit fields of the replay, and stores an
    absent field as NaN. It writes one event record per completed snapshot and,
    across a gap, hold-last bridge records that repeat every channel except
    Date and Elapsed. The decoder never accepts two consecutive groups with
    the same tick, so a record that repeats the preceding tick is a bridge
    record, and the decoder's own tick rule rebuilds run and unwrapped tick
    from the event records.
    """
    columns = recording.columns
    required = ("elapsed", "schema_verified", "tick16", *CVTC_INPUT_FIELDS)
    missing = [name for name in required if name not in columns]
    if missing:
        raise ValueError(f"{recording.path}: MLG lacks {', '.join(missing)}")
    limits = _raw_limits(profile)
    repeated = [
        name for name in columns if name not in MLG_BRIDGE_TIME_SOURCES
    ]

    def raw(name: str, index: int) -> int:
        value = columns[name][index]
        low, high = limits[name]
        if not (
            math.isfinite(value) and value.is_integer() and low <= value <= high
        ):
            raise ValueError(
                f"{recording.path}: record {index} carries {name}={value!r}, "
                f"which is not a raw {profile} wire value"
            )
        return int(value)

    samples = []
    event_records = 0
    bridge_records = 0
    last_tick16 = None
    run = 0
    tick = 0
    for index in range(recording.record_count):
        tick16 = raw("tick16", index)
        if tick16 == last_tick16:
            if not all(
                _same_record_value(columns[name][index], columns[name][index - 1])
                for name in repeated
            ):
                raise ValueError(
                    f"{recording.path}: record {index} repeats tick {tick16} "
                    "but not the preceding channel values"
                )
            bridge_records += 1
            continue
        if last_tick16 is None:
            tick = tick16
        else:
            delta = (tick16 - last_tick16) & 0xFFFF
            if delta < 0x8000:
                tick += delta
            elif can_telemetry.is_producer_restart(last_tick16, tick16):
                run += 1
                tick = tick16
            else:
                raise ValueError(
                    f"{recording.path}: record {index} steps tick "
                    f"{last_tick16} to {tick16}, which the decoder rejects"
                )
        last_tick16 = tick16
        event_records += 1
        if columns["schema_verified"][index] != 1.0:
            continue
        if any(math.isnan(columns[name][index]) for name in CVTC_INPUT_FIELDS):
            continue
        values = {name: raw(name, index) for name in CVTC_INPUT_FIELDS}
        samples.append(
            CvtcSample(
                timestamp=columns["elapsed"][index],
                run=run,
                tick=tick,
                bfs_raw=values["bfs_raw"],
                rpm_raw=values["rpm_raw"],
                coolant_raw=values["coolant_raw"],
                coolant_age_ms=math.nan,
                knock_surface_state=values["knock_surface_state"],
                reference_a_raw=values["intake_cvtc_target_raw"],
                reference_b_raw=values["exhaust_cvtc_target_raw"],
                intake_actual_b1_raw=values["intake_cvtc_actual_b1_raw"],
                intake_actual_b2_raw=values["intake_cvtc_actual_b2_raw"],
            )
        )
    return event_records, bridge_records, samples


def _alignment_summary(
    samples: list[CvtcSample],
    points_by_source: list[ReplayPoint],
    source_lag: int,
    tick_divisor: int,
    stable_cycles: tuple[int, ...],
    conditioned_reference: str = "reference_a_raw",
    coolant_bands: tuple[str, ...] = COOLANT_BANDS,
) -> AlignmentSummary:
    if source_lag < 0:
        raise ValueError("source lag must be nonnegative")
    errors_a = []
    errors_b = []
    errors_actual_b1 = []
    errors_actual_b2 = []
    rows = []
    for target_index in range(source_lag, len(samples)):
        source_index = target_index - source_lag
        source = samples[source_index]
        target = samples[target_index]
        if (
            target.run != source.run
            or target.tick - source.tick != source_lag * tick_divisor
        ):
            continue
        point = points_by_source[source_index]
        if point.coolant_band not in coolant_bands:
            continue
        predicted = point.coolant_selected_raw
        errors_a.append(predicted - target.reference_a_raw)
        errors_b.append(predicted - target.reference_b_raw)
        errors_actual_b1.append(predicted - target.intake_actual_b1_raw)
        errors_actual_b2.append(predicted - target.intake_actual_b2_raw)
        rows.append((source_index, target_index, point, target))
    if not rows:
        raise ValueError(
            f"no contiguous samples for source lag {source_lag} in coolant "
            f"bands {','.join(coolant_bands)}"
        )

    if conditioned_reference not in ("reference_a_raw", "reference_b_raw"):
        raise ValueError("conditioned reference must be reference A or B")

    neutralized_rows = [
        (target_index, target.run, target.tick)
        for _, target_index, point, target in rows
        if point.coolant_selected_raw != 0x80
        and getattr(target, conditioned_reference) == 0x80
    ]
    neutralized_runs = 0
    previous_index = None
    previous_run = None
    previous_tick = None
    for target_index, run, tick in neutralized_rows:
        if (
            previous_index is None
            or target_index != previous_index + 1
            or run != previous_run
            or tick != previous_tick + tick_divisor
        ):
            neutralized_runs += 1
        previous_index = target_index
        previous_run = run
        previous_tick = tick

    without_neutralization = [
        point.coolant_selected_raw - getattr(target, conditioned_reference)
        for _, _, point, target in rows
        if not (
            point.coolant_selected_raw != 0x80
            and getattr(target, conditioned_reference) == 0x80
        )
    ]
    active_to_active = [
        point.coolant_selected_raw - getattr(target, conditioned_reference)
        for _, _, point, target in rows
        if point.coolant_selected_raw != 0x80
        and getattr(target, conditioned_reference) != 0x80
    ]
    # The cold surface determines a prediction exactly where the
    # coolant-selected byte differs from the main-surface byte.
    cold_dependent_active_to_active = [
        point.coolant_selected_raw - getattr(target, conditioned_reference)
        for _, _, point, target in rows
        if point.coolant_selected_raw != 0x80
        and getattr(target, conditioned_reference) != 0x80
        and point.coolant_selected_raw != point.main_selected_raw
    ]
    alternate_source_errors = [
        point.alternate_source_raw - getattr(target, conditioned_reference)
        for _, _, point, target in rows
        if point.alternate_source_raw is not None
    ]
    alternate_active_to_active = [
        point.alternate_source_raw - getattr(target, conditioned_reference)
        for _, _, point, target in rows
        if point.alternate_source_raw is not None
        and point.alternate_source_raw != 0x80
        and getattr(target, conditioned_reference) != 0x80
    ]
    stable = []
    for cycles in stable_cycles:
        if type(cycles) is not int or cycles < 1:
            raise ValueError("stable cycles must be positive integers")
        errors = []
        for source_index, _, point, target in rows:
            if source_index < cycles:
                continue
            first = source_index - cycles
            if (
                samples[source_index].run != samples[first].run
                or samples[source_index].tick - samples[first].tick
                != cycles * tick_divisor
            ):
                continue
            selected = point.coolant_selected_raw
            reference = getattr(target, conditioned_reference)
            if selected == 0x80 or reference == 0x80:
                continue
            if any(
                candidate.coolant_selected_raw != selected
                for candidate in points_by_source[first : source_index + 1]
            ):
                continue
            errors.append(selected - reference)
        if errors:
            stable.append(StableActiveSummary(cycles, _error_summary(errors)))

    points = [point for _, _, point, _ in rows]
    return AlignmentSummary(
        source_lag=source_lag,
        comparisons=len(points),
        selected_to_reference_a=_error_summary(errors_a),
        selected_to_reference_b=_error_summary(errors_b),
        selected_to_intake_actual_b1=_error_summary(errors_actual_b1),
        selected_to_intake_actual_b2=_error_summary(errors_actual_b2),
        without_conditioned_neutralization=_optional_error_summary(
            without_neutralization
        ),
        active_to_active=_optional_error_summary(active_to_active),
        conditioned_neutralization_count=len(neutralized_rows),
        conditioned_neutralization_runs=neutralized_runs,
        stable_active=tuple(stable),
        correction_active_count=sum(point.correction_active for point in points),
        coolant_band_counts=tuple(
            sorted(Counter(point.coolant_band for point in points).items())
        ),
        selected_raw_range=(
            min(point.coolant_selected_raw for point in points),
            max(point.coolant_selected_raw for point in points),
        ),
        alternate_source_to_reference=_optional_error_summary(
            alternate_source_errors
        ),
        alternate_source_active_to_active=_optional_error_summary(
            alternate_active_to_active
        ),
        cold_dependent_active_to_active=_optional_error_summary(
            cold_dependent_active_to_active
        ),
    )


def audit_trace(
    source: Path,
    *,
    rom: str = "JK08A",
    calibration_image: Path | None = None,
    profile: str = "tuning",
    can_id: int = 0x6F0,
    tick_divisor: int = 1,
    source_lags: tuple[int, ...] = (0, 1, 2),
    stable_cycles: tuple[int, ...] = (1, 4, 8, 16),
    target: str = "intake",
    coolant_bands: tuple[str, ...] = COOLANT_BANDS,
) -> TraceCvtcAudit:
    """Audit a PEAK TRC capture or a dashboard MLG recording.

    Both inputs yield the same verified snapshot sequence. An MLG carries no
    CAN frames and no context tag, so its report omits the frame count and the
    age of retained context values; ``can_id`` applies only to a TRC.
    """
    source = Path(source)
    source_sha256 = _sha256_file(source)
    if not coolant_bands or any(band not in COOLANT_BANDS for band in coolant_bands):
        raise ValueError(f"coolant bands must be drawn from {','.join(COOLANT_BANDS)}")
    if is_mlg(source):
        recording = mlg_relation_audit.read_recording(source)
        if recording.sha256 != source_sha256:
            raise ValueError(f"{source}: capture changed while it was being parsed")
        complete_snapshots, bridge_records, samples = _recording_samples(
            recording, profile
        )
        source_format = "mlg"
        source_frames = None
        source_records = recording.record_count
    else:
        trace = peak_trc_audit.load_trace(source)
        if _sha256_file(source) != source_sha256:
            raise ValueError(f"{source}: capture changed while it was being parsed")
        model, samples = _trace_samples(trace, profile, can_id, tick_divisor)
        complete_snapshots = model.decoder.completed_groups
        source_format = "trc"
        source_frames = len(trace.frames)
        source_records = None
        bridge_records = None
    calibration = load_calibration(rom, calibration_image, target)
    if len(samples) < 3:
        raise ValueError(f"{source}: fewer than three verified CVTC snapshots")
    if not source_lags or any(type(lag) is not int or lag < 0 for lag in source_lags):
        raise ValueError("source lags must be nonnegative integers")
    points_by_source = [replay_point(calibration, sample) for sample in samples]
    alignments = tuple(
        _alignment_summary(
            samples,
            points_by_source,
            lag,
            tick_divisor,
            stable_cycles,
            calibration.conditioned_reference,
            coolant_bands,
        )
        for lag in source_lags
    )
    return TraceCvtcAudit(
        source=source,
        source_sha256=source_sha256,
        source_format=source_format,
        target=calibration.target,
        calibration_image_source=calibration.image_source,
        calibration_image_sha256=calibration.image_sha256,
        source_frames=source_frames,
        source_records=source_records,
        bridge_records=bridge_records,
        complete_snapshots=complete_snapshots,
        analyzed_snapshots=len(samples),
        coolant_bands=tuple(coolant_bands),
        load_scaler=calibration.load_scaler,
        cold_threshold=calibration.cold_threshold,
        warm_threshold=calibration.warm_threshold,
        coolant_raw_range=(
            min(sample.coolant_raw for sample in samples),
            max(sample.coolant_raw for sample in samples),
        ),
        coolant_age_max_ms=(
            None
            if source_format == "mlg"
            else max(sample.coolant_age_ms for sample in samples)
        ),
        reference_a_raw_range=(
            min(sample.reference_a_raw for sample in samples),
            max(sample.reference_a_raw for sample in samples),
        ),
        reference_b_raw_range=(
            min(sample.reference_b_raw for sample in samples),
            max(sample.reference_b_raw for sample in samples),
        ),
        intake_actual_b1_raw_range=(
            min(sample.intake_actual_b1_raw for sample in samples),
            max(sample.intake_actual_b1_raw for sample in samples),
        ),
        intake_actual_b2_raw_range=(
            min(sample.intake_actual_b2_raw for sample in samples),
            max(sample.intake_actual_b2_raw for sample in samples),
        ),
        alignments=alignments,
    )


def _format_errors(label: str, summary: ErrorSummary | None) -> str:
    if summary is None:
        return f"    {label}: n=0"
    exact = 100 * summary.exact / summary.comparisons
    within_one = 100 * summary.within_one / summary.comparisons
    within_two = 100 * summary.within_two / summary.comparisons
    common = ",".join(
        f"{error:+d}:{count}" for error, count in summary.common_signed_errors
    )
    return (
        f"    {label}: exact={summary.exact}/{summary.comparisons} "
        f"({exact:.3f}%), within1={summary.within_one} ({within_one:.3f}%), "
        f"within2={summary.within_two} ({within_two:.3f}%), "
        f"mean={summary.mean_signed:.6f}, MAE={summary.mean_absolute:.6f}, "
        f"median_abs={summary.median_absolute:g}, p95_abs={summary.p95_absolute}, "
        f"max_abs={summary.maximum_absolute}, common={common}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument(
        "--calibration-image",
        type=Path,
        help="exact full ROM image whose CVTC calibration should be replayed",
    )
    parser.add_argument(
        "--can-id", type=lambda value: int(value, 0), default=0x6F0
    )
    parser.add_argument("--tick-divisor", type=int, default=1)
    parser.add_argument(
        "--target",
        choices=("intake", "exhaust"),
        default="intake",
        help="CVTC target family to replay",
    )
    parser.add_argument(
        "--source-lags",
        type=lambda value: tuple(int(item, 0) for item in value.split(",")),
        default=(0, 1, 2),
        help="comma-separated snapshot lags used as map inputs",
    )
    parser.add_argument(
        "--stable-cycles",
        type=lambda value: tuple(int(item, 0) for item in value.split(",")),
        default=(1, 4, 8, 16),
        help="comma-separated unchanged-map-input windows for active comparisons",
    )
    parser.add_argument(
        "--coolant-bands",
        type=lambda value: tuple(value.split(",")),
        default=COOLANT_BANDS,
        help=(
            "comma-separated coolant bands (cold, blend, warm) of the replayed "
            "source snapshot that enter the comparisons"
        ),
    )
    args = parser.parse_args(argv)
    if not 1 <= args.can_id <= 0x7FF:
        parser.error("CAN ID must be in 0x001..0x7FF")
    if not 1 <= args.tick_divisor <= 0xFF:
        parser.error("tick divisor must be in 1..255")

    try:
        for source in args.inputs:
            result = audit_trace(
                source,
                rom="JK08A",
                calibration_image=args.calibration_image,
                profile="tuning",
                can_id=args.can_id,
                tick_divisor=args.tick_divisor,
                source_lags=args.source_lags,
                stable_cycles=args.stable_cycles,
                target=args.target,
                coolant_bands=args.coolant_bands,
            )
            print(result.source)
            print(f"  target={result.target}")
            print(f"  capture_sha256={result.source_sha256}")
            print(
                f"  calibration={result.calibration_image_source}, "
                f"sha256={result.calibration_image_sha256}"
            )
            if result.source_format == "mlg":
                source_counts = (
                    f"records={result.source_records}, "
                    f"bridge={result.bridge_records}"
                )
                context_age = "n/a"
            else:
                source_counts = f"frames={result.source_frames}"
                context_age = f"{result.coolant_age_max_ms:.3f}ms"
            print(
                f"  {source_counts}, "
                f"complete={result.complete_snapshots}, "
                f"analyzed={result.analyzed_snapshots}"
            )
            print(
                f"  load_scaler=0x{result.load_scaler:04X}, "
                f"coolant_thresholds={result.cold_threshold}.."
                f"{result.warm_threshold}, coolant_raw="
                f"{result.coolant_raw_range[0]}..{result.coolant_raw_range[1]}, "
                f"retained_context_max_age={context_age}"
            )
            if result.coolant_bands != COOLANT_BANDS:
                print(f"  compared_coolant_bands={','.join(result.coolant_bands)}")
            print(
                "  captured_ranges: "
                f"reference_a={result.reference_a_raw_range[0]}.."
                f"{result.reference_a_raw_range[1]}, "
                f"reference_b={result.reference_b_raw_range[0]}.."
                f"{result.reference_b_raw_range[1]}, "
                f"intake_actual_b1={result.intake_actual_b1_raw_range[0]}.."
                f"{result.intake_actual_b1_raw_range[1]}, "
                f"intake_actual_b2={result.intake_actual_b2_raw_range[0]}.."
                f"{result.intake_actual_b2_raw_range[1]}"
            )
            for alignment in result.alignments:
                bands = ",".join(
                    f"{name}:{count}"
                    for name, count in alignment.coolant_band_counts
                )
                print(
                    f"  source_lag={alignment.source_lag}: "
                    f"n={alignment.comparisons}, selected_raw="
                    f"{alignment.selected_raw_range[0]}.."
                    f"{alignment.selected_raw_range[1]}, "
                    f"correction_active={alignment.correction_active_count}, "
                    f"coolant_bands={bands}"
                )
                print(
                    _format_errors(
                        "selected_to_reference_a",
                        alignment.selected_to_reference_a,
                    )
                )
                print(
                    _format_errors(
                        "selected_to_reference_b",
                        alignment.selected_to_reference_b,
                    )
                )
                print(
                    _format_errors(
                        "selected_to_intake_actual_b1",
                        alignment.selected_to_intake_actual_b1,
                    )
                )
                print(
                    _format_errors(
                        "selected_to_intake_actual_b2",
                        alignment.selected_to_intake_actual_b2,
                    )
                )
                if alignment.alternate_source_to_reference is not None:
                    print(
                        _format_errors(
                            "alternate_ffff1553_to_reference_a",
                            alignment.alternate_source_to_reference,
                        )
                    )
                    print(
                        _format_errors(
                            "alternate_ffff1553_active_to_active",
                            alignment.alternate_source_active_to_active,
                        )
                    )
                print(
                    "    conditioned_neutralization: "
                    f"samples={alignment.conditioned_neutralization_count}, "
                    f"runs={alignment.conditioned_neutralization_runs}"
                )
                print(
                    _format_errors(
                        "without_conditioned_neutralization",
                        alignment.without_conditioned_neutralization,
                    )
                )
                print(
                    _format_errors(
                        "active_to_active",
                        alignment.active_to_active,
                    )
                )
                print(
                    _format_errors(
                        "cold_dependent_active_to_active",
                        alignment.cold_dependent_active_to_active,
                    )
                )
                for stable in alignment.stable_active:
                    print(
                        _format_errors(
                            "active_unchanged_"
                            f"{stable.unchanged_source_cycles}_cycles",
                            stable.errors,
                        )
                    )
    except (OSError, ValueError, peak_trc_audit.TraceError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
