#!/usr/bin/env python3
"""Audit JK08A long-term fuel-trim publication and learning in dashboard MLGs.

Telemetry profile 5 carries the published LTFT words 0xFFFF2302/0xFFFF2304 in
context tag 2 and the bank 1 learned cell 0xFFFF2306 and adjustment term
0xFFFF5648 in context tag 0. An MLG retains every context value between its
refreshes and stores no tag, so the audit derives the refresh phase from the
tick residue on which the tag-2 front A/F word 0xFFFF2780 changes. A recording
whose changes fall on more than one residue is refused.

At each tag-2 refresh the audit brackets published B1 with the tag-0 refreshes
two snapshots before and three snapshots after it. When both brackets hold the
same learned and adjustment words, FUN 00057B26 publishes
clamp(learned + adjustment - 0x6400) unless one of its neutralizing conditions
holds, so exact matches, forced neutral words, and other values are counted
separately. A neutralizing condition is visible only where the predicted word
differs from neutral, so exact matches with a non-neutral prediction are counted
as well. The audit clamps unconditionally; FUN 00057B26 skips the clamp while
bit b of 0xFFFF230E is set or while uint16[0xFFFF15FC] <= int16[0xFFFF15FE],
which changes the word only when the sum leaves the clamp range and then counts
as another value.

Learning is counted as a change of the learned word between tag-0 refreshes
five snapshots apart. The audit replays the FUN 0005796C cell selector from
the captured Base Fuel Schedule word and the RPM/12.5 word, whose right shift
by two equals the selector's engine-speed byte, and counts the changes inside
one replayed cell visit. A single FUN 00057D1E update cannot exceed the
largest captured STFT deviation times the largest gain divided by 256, so a
larger in-visit change marks a cell switch that the replay does not reproduce.
Near idle the Base Fuel Schedule word lies inside the column hysteresis band of
row 0, where the selected column depends on history that precedes the
recording.

The warm window starts at the first tag-0 refresh whose coolant word reaches
the ROM8[0x8CFD] learning threshold. FUN 0004F736 makes the fuel-inhibit
coordinator publish the full mask while MAF diagnostic summary snapshot bit
0xFFFF2448.bit7 is set and 0xFFFF11B2 >= 0xC0, so every fueled snapshot whose
RPM/12.5 word reaches 0xC0 is a snapshot in which that bit is clear. Runtime
record 0x129 behind that bit also resets the learned grid in FUN 0005796C and
neutralizes the publication in FUN 00057B26.
"""

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

from tools.logs import mlg_relation_audit, mlg_retime  # noqa: E402
from tools.mapkit import rom as romkit  # noqa: E402


NEUTRAL = 0x6400
TICK_SECONDS = 0.01024
TAG_COUNT = 5
LEARNED_TAG = 0
STFT_TAG = 1
PUBLISHED_TAG = 2
AF_ADJUSTMENT_B2_TAG = 3
PHASE_SOURCE = "front_af_sensor_b1_word_raw"
BRACKET_BEFORE = 2
BRACKET_AFTER = 3
STABLE_VISIT = 5
GEAR_D = 0x20
GEAR_P = 0x08
FULL_FUEL_INHIBIT_MASK = 0x3F
CLOSED_LOOP_WINDOW = 98
MAF_SUMMARY_RPM_RAW = 0xC0
PUBLICATION_LOW_ADDRESS = 0x8E5B
PUBLICATION_HIGH_ADDRESS = 0x8E5A
CELL_LOW_ADDRESS = 0x8A9E
CELL_HIGH_ADDRESS = 0x8A9F
COOLANT_THRESHOLD_ADDRESS = 0x8CFD
GAIN_TABLE_ADDRESS = 0x129C6
GAIN_TABLE_POINTS = 3
FIRST_VISIT_GAIN_ADDRESS = 0x8A9D
BFS_AXIS_ADDRESS = 0x12592
RPM_AXIS_ADDRESS = 0x126DC
AXIS_POINTS = 8
BFS_HYSTERESIS_ADDRESS = 0x881B
RPM_HYSTERESIS_ADDRESS = 0x881A
COLUMNS = (
    "date",
    "elapsed",
    "rpm_raw",
    "bfs_raw",
    "vehicle_speed_kmh",
    "gear_raw",
    "coolant_raw",
    "fuel_inhibit_mask",
    "stft_b1_raw",
    "stft_b2_raw",
    "ltft_b1_raw",
    "ltft_b2_raw",
    "ltft_learned_b1_raw",
    "ltft_adjustment_b1_raw",
    "af_adjustment_b1_raw",
    "af_adjustment_b2_raw",
    PHASE_SOURCE,
)
FLOAT_COLUMNS = ("date", "elapsed", "vehicle_speed_kmh")


@dataclass(frozen=True)
class Calibration:
    image_sha256: str
    publication_low: int
    publication_high: int
    cell_low: int
    cell_high: int
    coolant_threshold_raw: int
    gains: tuple[int, ...]
    first_visit_gain: int
    bfs_axis: tuple[int, ...]
    rpm_axis: tuple[int, ...]
    bfs_hysteresis: int
    rpm_hysteresis: int


@dataclass(frozen=True)
class Snapshots:
    path: Path
    sha256: str
    record_count: int
    unverified_record_count: int
    bridge_record_count: int
    ticks: tuple[int, ...]
    columns: dict[str, list]

    def __len__(self) -> int:
        return len(self.ticks)


def load_calibration(rom: str = "JK08A", image: Path | None = None) -> Calibration:
    """Read the audit constants from the calibration image.

    Without an explicit image the hash-verified registered ROM is used.
    """
    data = romkit.load(rom).data if image is None else Path(image).read_bytes()
    return Calibration(
        image_sha256=hashlib.sha256(data).hexdigest(),
        publication_low=data[PUBLICATION_LOW_ADDRESS] << 8,
        publication_high=data[PUBLICATION_HIGH_ADDRESS] << 8,
        cell_low=data[CELL_LOW_ADDRESS] << 8,
        cell_high=data[CELL_HIGH_ADDRESS] << 8,
        coolant_threshold_raw=data[COOLANT_THRESHOLD_ADDRESS],
        gains=tuple(data[GAIN_TABLE_ADDRESS : GAIN_TABLE_ADDRESS + GAIN_TABLE_POINTS]),
        first_visit_gain=data[FIRST_VISIT_GAIN_ADDRESS],
        bfs_axis=tuple(data[BFS_AXIS_ADDRESS : BFS_AXIS_ADDRESS + AXIS_POINTS]),
        rpm_axis=tuple(data[RPM_AXIS_ADDRESS : RPM_AXIS_ADDRESS + AXIS_POINTS]),
        bfs_hysteresis=data[BFS_HYSTERESIS_ADDRESS],
        rpm_hysteresis=data[RPM_HYSTERESIS_ADDRESS] >> 2,
    )


def _value(value):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    return int(round(value))


def read_snapshots(path: Path) -> Snapshots:
    """Return the verified snapshots of one MLG with unwrapped ticks."""
    recording = mlg_relation_audit.read_recording(Path(path))
    columns = recording.columns
    rows = []
    unverified = 0
    for index, tick in enumerate(columns["tick16"]):
        if _value(tick) is None or _value(columns["schema_verified"][index]) != 1:
            unverified += 1
            continue
        rows.append(index)
    ticks = mlg_retime.unwrap_ticks(int(columns["tick16"][index]) for index in rows)
    kept = []
    kept_ticks = []
    bridges = 0
    for index, tick in zip(rows, ticks):
        if kept_ticks and tick == kept_ticks[-1]:
            bridges += 1
            continue
        kept.append(index)
        kept_ticks.append(tick)
    selected = {}
    for name in COLUMNS:
        source = columns[name]
        if name in FLOAT_COLUMNS:
            selected[name] = [
                None if math.isnan(source[index]) else float(source[index])
                for index in kept
            ]
        else:
            selected[name] = [_value(source[index]) for index in kept]
    return Snapshots(
        Path(path),
        recording.sha256,
        recording.record_count,
        unverified,
        bridges,
        tuple(kept_ticks),
        selected,
    )


def refresh_phase(snapshots: Snapshots) -> dict[int, int]:
    """Map each context tag to the tick residue on which it refreshes."""
    residues = Counter()
    words = snapshots.columns[PHASE_SOURCE]
    ticks = snapshots.ticks
    for index in range(1, len(snapshots)):
        previous, current = words[index - 1], words[index]
        if previous is not None and current is not None and previous != current:
            residues[ticks[index] % TAG_COUNT] += 1
    if len(residues) != 1:
        raise ValueError(
            f"{snapshots.path.name}: the tag-{PUBLISHED_TAG} word changes on "
            f"tick residues {dict(sorted(residues.items()))}"
        )
    (published,) = residues
    return {
        tag: (published + tag - PUBLISHED_TAG) % TAG_COUNT for tag in range(TAG_COUNT)
    }


def refreshes(snapshots: Snapshots, phase: dict[int, int], tag: int) -> list[int]:
    return [
        index
        for index, tick in enumerate(snapshots.ticks)
        if tick % TAG_COUNT == phase[tag]
    ]


def published_value(calibration: Calibration, learned: int, adjustment: int) -> int:
    raw = learned + adjustment - NEUTRAL
    return min(max(raw, calibration.publication_low), calibration.publication_high)


def publication_relation(
    snapshots: Snapshots, phase: dict[int, int], calibration: Calibration
) -> Counter:
    columns = snapshots.columns
    position = {tick: index for index, tick in enumerate(snapshots.ticks)}
    published = columns["ltft_b1_raw"]
    learned = columns["ltft_learned_b1_raw"]
    adjustment = columns["ltft_adjustment_b1_raw"]
    result = Counter()
    for index in refreshes(snapshots, phase, PUBLISHED_TAG):
        word = published[index]
        if word is None:
            continue
        tick = snapshots.ticks[index]
        before = position.get(tick - BRACKET_BEFORE)
        after = position.get(tick + BRACKET_AFTER)
        pairs = [
            (learned[i], adjustment[i]) for i in (before, after) if i is not None
        ]
        if len(pairs) != 2 or any(None in pair for pair in pairs):
            result["unbracketed"] += 1
            continue
        if pairs[0] == pairs[1]:
            result["bracketed"] += 1
            expected = published_value(calibration, *pairs[0])
            if word == expected:
                result["exact"] += 1
                result["nonneutral_exact"] += expected != NEUTRAL
            elif word == NEUTRAL:
                result["forced_neutral"] += 1
            else:
                result["other"] += 1
        else:
            result["transition"] += 1
            candidates = {published_value(calibration, *pair) for pair in pairs}
            result["transition_bracket"] += word in candidates
    return result


def select_cell(
    calibration: Calibration, bfs: int, rpm_byte: int, prior: int | None
) -> int:
    """Return the packed FUN 0005796C index row * 8 + column."""
    bfs_axis = calibration.bfs_axis
    rpm_axis = calibration.rpm_axis
    column = 0
    while column < AXIS_POINTS - 1 and bfs >= bfs_axis[column + 1] << 8:
        column += 1
    if prior is not None and column != prior & 7:
        prior_column = prior & 7
        if prior_column < column:
            if bfs < (bfs_axis[prior_column + 1] + calibration.bfs_hysteresis) << 8:
                column -= 1
        elif (bfs_axis[prior_column] - calibration.bfs_hysteresis) << 8 < bfs:
            column += 1
    row = 0
    while row < AXIS_POINTS - 1 and rpm_byte >= rpm_axis[row + 1]:
        row += 1
    if prior is not None and row != prior >> 3:
        prior_row = prior >> 3
        if prior_row < row:
            if rpm_byte < rpm_axis[prior_row + 1] + calibration.rpm_hysteresis:
                row -= 1
        elif rpm_axis[prior_row] - calibration.rpm_hysteresis < rpm_byte:
            row += 1
    return row * 8 + column


def replay_cells(snapshots: Snapshots, calibration: Calibration) -> list[int | None]:
    cells = []
    prior = None
    for index in range(len(snapshots)):
        bfs = snapshots.columns["bfs_raw"][index]
        rpm = snapshots.columns["rpm_raw"][index]
        contiguous = index == 0 or snapshots.ticks[index] - snapshots.ticks[index - 1] == 1
        if not contiguous:
            prior = None
        if bfs is None or rpm is None:
            cells.append(None)
            prior = None
            continue
        prior = select_cell(calibration, bfs, min(255, rpm >> 2), prior)
        cells.append(prior)
    return cells


def update_bound(snapshots: Snapshots, calibration: Calibration) -> int:
    deviations = [
        abs(value - NEUTRAL)
        for value in snapshots.columns["stft_b1_raw"]
        if value is not None
    ]
    gain = max(*calibration.gains, calibration.first_visit_gain)
    return (max(deviations, default=0) * gain) >> 8


def learning_changes(
    snapshots: Snapshots, phase: dict[int, int], calibration: Calibration
) -> dict:
    columns = snapshots.columns
    ticks = snapshots.ticks
    learned = columns["ltft_learned_b1_raw"]
    stft = columns["stft_b1_raw"]
    gear = columns["gear_raw"]
    samples = [i for i in refreshes(snapshots, phase, LEARNED_TAG) if learned[i] is not None]
    pairs = changes = park_pairs = park_changes = 0
    for first, second in zip(samples, samples[1:]):
        if ticks[second] - ticks[first] == TAG_COUNT:
            pairs += 1
            changes += learned[first] != learned[second]
            if gear[first] == GEAR_P and gear[second] == GEAR_P:
                park_pairs += 1
                park_changes += learned[first] != learned[second]
    cells = replay_cells(snapshots, calibration)
    stable = []
    visit_start = 0
    for index in range(len(snapshots)):
        if index and (
            cells[index] != cells[index - 1] or ticks[index] - ticks[index - 1] != 1
        ):
            visit_start = index
        if (
            ticks[index] % TAG_COUNT == phase[LEARNED_TAG]
            and learned[index] is not None
            and cells[index] is not None
            and index - visit_start + 1 >= STABLE_VISIT
        ):
            stable.append(index)
    bound = update_bound(snapshots, calibration)
    in_visit = updates = row0 = agree = neutral_stft = 0
    for first, second in zip(stable, stable[1:]):
        if (
            cells[first] != cells[second]
            or ticks[second] - ticks[first] != TAG_COUNT
            or learned[first] == learned[second]
        ):
            continue
        in_visit += 1
        step = learned[second] - learned[first]
        if abs(step) > bound:
            continue
        updates += 1
        row0 += cells[second] < 8
        if stft[second] is None or stft[second] == NEUTRAL:
            neutral_stft += 1
        else:
            agree += (step > 0) == (stft[second] > NEUTRAL)
    return {
        "learned_pair_count": pairs,
        "learned_change_count": changes,
        "gear_p_learned_pair_count": park_pairs,
        "gear_p_learned_change_count": park_changes,
        "update_bound": bound,
        "in_visit_change_count": in_visit,
        "in_visit_update_count": updates,
        "in_visit_over_bound_count": in_visit - updates,
        "row_0_update_count": row0,
        "update_stft_sign_agreement_count": agree,
        "update_stft_neutral_count": neutral_stft,
    }


def _intervals(flags: list[bool], ticks: tuple[int, ...]) -> list[tuple[int, int]]:
    out = []
    start = None
    for index, flag in enumerate(flags):
        contiguous = index > 0 and ticks[index] - ticks[index - 1] == 1
        if flag and (start is None or not contiguous):
            if start is not None:
                out.append((start, index - 1))
            start = index
        elif not flag and start is not None:
            out.append((start, index - 1))
            start = None
    if start is not None:
        out.append((start, len(flags) - 1))
    return out


def _seconds(interval: tuple[int, int], ticks: tuple[int, ...]) -> float:
    first, last = interval
    return round((ticks[last] - ticks[first] + 1) * TICK_SECONDS, 3)


def warm_window(
    snapshots: Snapshots, phase: dict[int, int], calibration: Calibration
) -> dict:
    """Report the capture after coolant first reaches the learning threshold."""
    columns = snapshots.columns
    ticks = snapshots.ticks
    coolant = columns["coolant_raw"]
    warm = [
        index
        for index in refreshes(snapshots, phase, LEARNED_TAG)
        if coolant[index] is not None and coolant[index] >= calibration.coolant_threshold_raw
    ]
    if not warm:
        return {"warm_elapsed_seconds": None}
    first = warm[0]
    stft = columns["stft_b1_raw"]
    mask = columns["fuel_inhibit_mask"]
    closed_loop = 0
    changed_at = None
    for index in range(first, len(snapshots)):
        if index and stft[index] != stft[index - 1]:
            changed_at = ticks[index]
        closed_loop += (
            changed_at is not None
            and ticks[index] - changed_at <= CLOSED_LOOP_WINDOW
            and mask[index] == 0
        )
    in_d = sum(1 for index in range(first, len(snapshots)) if columns["gear_raw"][index] == GEAR_D)
    rpm = columns["rpm_raw"]
    fueled_above_gate = sum(
        1
        for index in range(first, len(snapshots))
        if rpm[index] is not None and rpm[index] >= MAF_SUMMARY_RPM_RAW and mask[index] == 0
    )
    return {
        "warm_elapsed_seconds": round(columns["elapsed"][first], 3),
        "warm_capture_seconds": _seconds((first, len(snapshots) - 1), ticks),
        "warm_gear_d_seconds": round(in_d * TICK_SECONDS, 3),
        "warm_closed_loop_seconds": round(closed_loop * TICK_SECONDS, 3),
        "warm_gear_p_seconds": round(
            sum(1 for index in range(first, len(snapshots)) if columns["gear_raw"][index] == GEAR_P)
            * TICK_SECONDS,
            3,
        ),
        "warm_fueled_above_maf_gate_count": fueled_above_gate,
    }


def drive_profile(snapshots: Snapshots, band: tuple[float, float]) -> dict:
    """Report the longest D interval, the speed band inside D, and the final P."""
    columns = snapshots.columns
    ticks = snapshots.ticks
    gear = columns["gear_raw"]
    speed = columns["vehicle_speed_kmh"]
    low, high = band
    d_runs = _intervals([value == GEAR_D for value in gear], ticks)
    p_runs = _intervals([value == GEAR_P for value in gear], ticks)
    band_runs = _intervals(
        [
            gear[index] == GEAR_D and speed[index] is not None and low <= speed[index] <= high
            for index in range(len(snapshots))
        ],
        ticks,
    )
    result = {
        "speed_band_kmh": [low, high],
        "longest_gear_d_seconds": max((_seconds(run, ticks) for run in d_runs), default=0.0),
        "speed_band_seconds": round(sum(_seconds(run, ticks) for run in band_runs), 3),
        "speed_band_interval_count": len(band_runs),
        "speed_band_longest_seconds": max(
            (_seconds(run, ticks) for run in band_runs), default=0.0
        ),
        "final_gear_p_seconds": 0.0,
        "final_gear_p_stft_b1_median_raw": None,
    }
    if p_runs and p_runs[-1][1] == len(snapshots) - 1:
        first, last = p_runs[-1]
        stft = [
            value
            for value in columns["stft_b1_raw"][first : last + 1]
            if value is not None
        ]
        result["final_gear_p_seconds"] = _seconds(p_runs[-1], ticks)
        result["final_gear_p_stft_b1_median_raw"] = statistics.median_low(stft) if stft else None
    full_mask = _intervals(
        [
            gear[index] == GEAR_D and columns["fuel_inhibit_mask"][index] == FULL_FUEL_INHIBIT_MASK
            for index in range(len(snapshots))
        ],
        ticks,
    )
    result["gear_d_full_fuel_inhibit_interval_count"] = len(full_mask)
    return result


def _count(values, predicate) -> int:
    return sum(1 for value in values if value is not None and predicate(value))


def audit(
    path: Path, calibration: Calibration, band: tuple[float, float] = (80.0, 100.0)
) -> dict:
    snapshots = read_snapshots(path)
    phase = refresh_phase(snapshots)
    columns = snapshots.columns
    result = {
        "capture_name": snapshots.path.name,
        "capture_sha256": snapshots.sha256,
        "calibration_image_sha256": calibration.image_sha256,
        "record_count": snapshots.record_count,
        "unverified_record_count": snapshots.unverified_record_count,
        "bridge_record_count": snapshots.bridge_record_count,
        "snapshot_count": len(snapshots),
        "learned_tag_residue": phase[LEARNED_TAG],
    }
    samples = {
        "learned_b1": (LEARNED_TAG, "ltft_learned_b1_raw"),
        "adjustment_b1": (LEARNED_TAG, "ltft_adjustment_b1_raw"),
        "published_b1": (PUBLISHED_TAG, "ltft_b1_raw"),
        "published_b2": (PUBLISHED_TAG, "ltft_b2_raw"),
    }
    for name, (tag, column) in samples.items():
        values = [columns[column][index] for index in refreshes(snapshots, phase, tag)]
        if name.startswith("published"):
            low, high = calibration.publication_low, calibration.publication_high
        else:
            low, high = calibration.cell_low, calibration.cell_high
        result[f"{name}_sample_count"] = _count(values, lambda value: True)
        result[f"{name}_neutral_count"] = _count(values, lambda value: value == NEUTRAL)
        result[f"{name}_upper_bound_count"] = _count(values, lambda value: value == high)
        result[f"{name}_lower_bound_count"] = _count(values, lambda value: value == low)
    for bank, tag in ((1, PUBLISHED_TAG), (2, AF_ADJUSTMENT_B2_TAG)):
        column = f"af_adjustment_b{bank}_raw"
        values = [columns[column][index] for index in refreshes(snapshots, phase, tag)]
        result[f"af_adjustment_b{bank}_nonzero_count"] = _count(values, lambda value: value != 0)
    relation = publication_relation(snapshots, phase, calibration)
    for key in (
        "bracketed",
        "exact",
        "nonneutral_exact",
        "forced_neutral",
        "other",
        "transition",
        "transition_bracket",
        "unbracketed",
    ):
        result[f"relation_{key}_count"] = relation[key]
    result.update(learning_changes(snapshots, phase, calibration))
    result.update(warm_window(snapshots, phase, calibration))
    result.update(drive_profile(snapshots, band))
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="+", type=Path)
    parser.add_argument("--rom", default="JK08A")
    parser.add_argument("--calibration-image", type=Path)
    parser.add_argument("--speed-band", type=float, nargs=2, default=(80.0, 100.0))
    args = parser.parse_args(argv)
    calibration = load_calibration(args.rom, args.calibration_image)
    for index, log in enumerate(args.logs):
        if index:
            print()
        for key, value in audit(log, calibration, tuple(args.speed_band)).items():
            if value is not None:
                print(f"{key} = {mlg_relation_audit.format_value(value)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
