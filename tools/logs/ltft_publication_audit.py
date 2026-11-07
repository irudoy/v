#!/usr/bin/env python3
"""Audit JK08A long-term fuel-trim publication and learning in dashboard MLGs.

The tuning telemetry profile carries the published LTFT words
0xFFFF2302/0xFFFF2304 in context tag 2 and learned cells 0xFFFF2306/0xFFFF2308
and adjustment terms 0xFFFF5648/0xFFFF564A in context tag 0. Earlier profiles
carry only the bank 1 summands. An MLG retains every context
value between its refreshes and stores no tag, so the audit derives the
refresh phase from the tick residue on which the tag-2 front A/F word
0xFFFF2780 changes. A recording whose changes fall on more than one residue is
refused.

At each tag-2 refresh the audit brackets each published bank with the tag-0 refreshes
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
one replayed cell visit. The RPM/12.5 word comes from the stock engine-speed
frame, which carries the word it is a shift of. A single FUN 00057D1E update cannot exceed the
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

Profile 8 carries the permit bytes 0xFFFF1458 and 0xFFFF1457 and the
neutralization byte 0xFFFF41B5 on page 3 of every snapshot. Profile 9 makes
page 3 dynamic: only its default configuration 0 carries the three bytes, and
a snapshot of another configuration leaves them unobserved. The audit treats
a missing byte as unknown, never as a clear bit: a missing byte ends a permit
interval, and the figures that look for a set or a clear bit inside a window
count a window without the byte separately. FUN 00057C78 sets the tick
flag on one coordinator pass when revolution counter 0xFFFF25FA reaches zero
and reloads it with the immediate at 0x57CA0; FUN 000208F8 decrements the
counter once per crank revolution. FUN 00058740 sets bit b of 0xFFFF1457 only
on tick passes and holds bit b of 0xFFFF1458 while its eligibility counter
exceeds one and the stability bounds hold. A permit interval therefore
expects one 0xFFFF1457 pulse per tick, counted from the stock engine-speed
word; fewer pulses mean that snapshots miss the one-pass pulse. Bit b of
0xFFFF1458 requires coolant at ROM8[0x8CFD] or above and af_adjustment
0xFFFF45A0+2b inside the bounds ROM16[0x8ECC] < value <= ROM16[0x8ECE]. A
decrease of the latched af_adjustment copy fails the composite gate for one
pass, which clears the eligibility counter and bit b of 0xFFFF1458. The
updater FUN 00057D1E requires bit b of both bytes, so an in-visit update
expects bit b of 0xFFFF1458 between its two tag-0 samples. A pulse of
0xFFFF41B5.bit0 refills the learned grid with 0x6400 in FUN 0005796C.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from functools import cached_property
import hashlib
import itertools
import math
from pathlib import Path
import statistics
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.logs import can_telemetry, mlg_relation_audit, mlg_retime  # noqa: E402
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
TICK_RELOAD_ADDRESS = 0x57CA0
MOV_IMMEDIATE_R0 = 0xE0
AF_ADJUSTMENT_LOW_ADDRESS = 0x8ECC
AF_ADJUSTMENT_HIGH_ADDRESS = 0x8ECE
RPM_RAW_SCALE = 12.5
STABILITY_PERMIT = "fuel_learning_permit_a_raw"
COMPOSITE_PERMIT = "fuel_learning_permit_b_raw"
NEUTRAL_CONTROL = "ltft_publication_neutral_control_raw"
AF_ADJUSTMENT_TAGS = {1: PUBLISHED_TAG, 2: AF_ADJUSTMENT_B2_TAG}
COLUMNS = (
    "date",
    "elapsed",
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
    "ltft_learned_b2_raw",
    "ltft_adjustment_b2_raw",
    "fuel_learning_permit_a_raw",
    "fuel_learning_permit_b_raw",
    "ltft_publication_neutral_control_raw",
    "af_adjustment_b1_raw",
    "af_adjustment_b2_raw",
    PHASE_SOURCE,
)
FLOAT_COLUMNS = ("date", "elapsed", "vehicle_speed_kmh")
OPTIONAL_COLUMNS = ("ltft_learned_b2_raw", "ltft_adjustment_b2_raw",
                    "fuel_learning_permit_a_raw", "fuel_learning_permit_b_raw",
                    "ltft_publication_neutral_control_raw")


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
    tick_revolutions: int
    af_adjustment_low: int
    af_adjustment_high: int


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

    @cached_property
    def pauses(self) -> tuple[float, ...]:
        """Recorded stream pause time that precedes each snapshot."""
        return tuple(
            can_telemetry.stream_pauses(
                self.ticks, self.columns["elapsed"], TICK_SECONDS
            )
        )

    @cached_property
    def segments(self) -> tuple[int, ...]:
        """Stream segment of each snapshot; a stream pause starts a new one."""
        return tuple(itertools.accumulate(int(pause > 0) for pause in self.pauses))

    @cached_property
    def pause_offsets(self) -> tuple[float, ...]:
        """Recorded pause time that the held tick does not count."""
        return tuple(itertools.accumulate(self.pauses))

    def contiguous(self, index: int) -> bool:
        """Whether a snapshot directly follows the previous one in one stream."""
        return (
            index > 0
            and self.ticks[index] - self.ticks[index - 1] == 1
            and self.segments[index] == self.segments[index - 1]
        )

    def seconds(self, first: int, last: int) -> float:
        """Elapsed time from snapshot first through the tick of snapshot last."""
        return round(
            (self.ticks[last] - self.ticks[first] + 1) * TICK_SECONDS
            + self.pause_offsets[last]
            - self.pause_offsets[first],
            3,
        )


def load_calibration(rom: str = "JK08A", image: Path | None = None) -> Calibration:
    """Read the audit constants from the calibration image.

    Without an explicit image the hash-verified registered ROM is used.
    """
    data = romkit.load(rom).data if image is None else Path(image).read_bytes()
    if data[TICK_RELOAD_ADDRESS] != MOV_IMMEDIATE_R0:
        raise ValueError(f"no mov #imm,r0 tick reload at {TICK_RELOAD_ADDRESS:#x}")
    af_low, af_high = struct.unpack_from(">hh", data, AF_ADJUSTMENT_LOW_ADDRESS)
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
        tick_revolutions=data[TICK_RELOAD_ADDRESS + 1],
        af_adjustment_low=af_low,
        af_adjustment_high=af_high,
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
    elapsed = columns.get("elapsed")
    ticks = mlg_retime.unwrap_ticks(
        (int(columns["tick16"][index]) for index in rows),
        None if elapsed is None else [elapsed[index] for index in rows],
    )
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
        source = (columns.get(name, [None] * recording.record_count)
                  if name in OPTIONAL_COLUMNS else columns[name])
        if name in FLOAT_COLUMNS:
            selected[name] = [
                None if source[index] is None or math.isnan(source[index]) else float(source[index])
                for index in kept
            ]
        else:
            selected[name] = [_value(source[index]) for index in kept]
    rpm = mlg_relation_audit.engine_speed_counts(recording)
    if rpm is None:
        raise ValueError(f"{Path(path).name}: the MLG carries no engine speed")
    selected["rpm_raw"] = [rpm[index] for index in kept]
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
    snapshots: Snapshots, phase: dict[int, int], calibration: Calibration, bank: int = 1
) -> Counter:
    columns = snapshots.columns
    position = {tick: index for index, tick in enumerate(snapshots.ticks)}
    published = columns[f"ltft_b{bank}_raw"]
    learned = columns[f"ltft_learned_b{bank}_raw"]
    adjustment = columns[f"ltft_adjustment_b{bank}_raw"]
    result = Counter()
    for index in refreshes(snapshots, phase, PUBLISHED_TAG):
        word = published[index]
        if word is None:
            continue
        tick = snapshots.ticks[index]
        before = position.get(tick - BRACKET_BEFORE)
        after = position.get(tick + BRACKET_AFTER)
        pairs = [
            (learned[i], adjustment[i])
            for i in (before, after)
            if i is not None and snapshots.segments[i] == snapshots.segments[index]
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
        if not snapshots.contiguous(index):
            prior = None
        if bfs is None or rpm is None:
            cells.append(None)
            prior = None
            continue
        prior = select_cell(calibration, bfs, min(255, rpm >> 2), prior)
        cells.append(prior)
    return cells


def update_bound(snapshots: Snapshots, calibration: Calibration, bank: int = 1) -> int:
    deviations = [
        abs(value - NEUTRAL)
        for value in snapshots.columns[f"stft_b{bank}_raw"]
        if value is not None
    ]
    gain = max(*calibration.gains, calibration.first_visit_gain)
    return (max(deviations, default=0) * gain) >> 8


def visit_changes(
    snapshots: Snapshots, phase: dict[int, int], cells: list[int | None], bank: int
) -> list[tuple[int, int]]:
    """Return the tag-0 sample pairs of one replayed cell visit whose word changes."""
    ticks = snapshots.ticks
    segments = snapshots.segments
    learned = snapshots.columns[f"ltft_learned_b{bank}_raw"]
    stable = []
    visit_start = 0
    for index in range(len(snapshots)):
        if index and (cells[index] != cells[index - 1] or not snapshots.contiguous(index)):
            visit_start = index
        if (
            ticks[index] % TAG_COUNT == phase[LEARNED_TAG]
            and learned[index] is not None
            and cells[index] is not None
            and index - visit_start + 1 >= STABLE_VISIT
        ):
            stable.append(index)
    return [
        (first, second)
        for first, second in zip(stable, stable[1:])
        if cells[first] == cells[second]
        and ticks[second] - ticks[first] == TAG_COUNT
        and segments[second] == segments[first]
        and learned[first] != learned[second]
    ]


def learning_changes(
    snapshots: Snapshots, phase: dict[int, int], calibration: Calibration, bank: int = 1
) -> dict:
    columns = snapshots.columns
    ticks = snapshots.ticks
    segments = snapshots.segments
    learned = columns[f"ltft_learned_b{bank}_raw"]
    stft = columns[f"stft_b{bank}_raw"]
    gear = columns["gear_raw"]
    samples = [i for i in refreshes(snapshots, phase, LEARNED_TAG) if learned[i] is not None]
    pairs = changes = park_pairs = park_changes = 0
    for first, second in zip(samples, samples[1:]):
        if ticks[second] - ticks[first] == TAG_COUNT and segments[second] == segments[first]:
            pairs += 1
            changes += learned[first] != learned[second]
            if gear[first] == GEAR_P and gear[second] == GEAR_P:
                park_pairs += 1
                park_changes += learned[first] != learned[second]
    cells = replay_cells(snapshots, calibration)
    bound = update_bound(snapshots, calibration, bank)
    in_visit = updates = row0 = agree = neutral_stft = 0
    for first, second in visit_changes(snapshots, phase, cells, bank):
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


def _intervals(flags: list[bool], snapshots: Snapshots) -> list[tuple[int, int]]:
    out = []
    start = None
    for index, flag in enumerate(flags):
        contiguous = snapshots.contiguous(index)
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


def _seconds(interval: tuple[int, int], snapshots: Snapshots) -> float:
    return snapshots.seconds(*interval)


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
        if index and snapshots.segments[index] != snapshots.segments[index - 1]:
            # Closed loop is unknown after a pause until STFT moves again.
            changed_at = None
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
        "warm_capture_seconds": _seconds((first, len(snapshots) - 1), snapshots),
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
    gear = columns["gear_raw"]
    speed = columns["vehicle_speed_kmh"]
    low, high = band
    d_runs = _intervals([value == GEAR_D for value in gear], snapshots)
    p_runs = _intervals([value == GEAR_P for value in gear], snapshots)
    band_runs = _intervals(
        [
            gear[index] == GEAR_D and speed[index] is not None and low <= speed[index] <= high
            for index in range(len(snapshots))
        ],
        snapshots,
    )
    result = {
        "speed_band_kmh": [low, high],
        "longest_gear_d_seconds": max((_seconds(run, snapshots) for run in d_runs), default=0.0),
        "speed_band_seconds": round(sum(_seconds(run, snapshots) for run in band_runs), 3),
        "speed_band_interval_count": len(band_runs),
        "speed_band_longest_seconds": max(
            (_seconds(run, snapshots) for run in band_runs), default=0.0
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
        result["final_gear_p_seconds"] = _seconds(p_runs[-1], snapshots)
        result["final_gear_p_stft_b1_median_raw"] = statistics.median_low(stft) if stft else None
    full_mask = _intervals(
        [
            gear[index] == GEAR_D and columns["fuel_inhibit_mask"][index] == FULL_FUEL_INHIBIT_MASK
            for index in range(len(snapshots))
        ],
        snapshots,
    )
    result["gear_d_full_fuel_inhibit_interval_count"] = len(full_mask)
    return result


def _count(values, predicate) -> int:
    return sum(1 for value in values if value is not None and predicate(value))


def learning_controls(snapshots: Snapshots) -> dict:
    """Count observed control bits without assigning physical gate causes."""
    columns = snapshots.columns
    a = columns["fuel_learning_permit_a_raw"]
    b = columns["fuel_learning_permit_b_raw"]
    neutral = columns["ltft_publication_neutral_control_raw"]
    paired = [(first, second) for first, second in zip(a, b)
              if first is not None and second is not None]
    result = {"learning_permits_available": bool(paired),
              "learning_permit_sample_count": len(paired),
              "neutral_control_sample_count": _count(neutral, lambda value: True),
              "neutral_control_bit0_set_count": _count(neutral, lambda value: bool(value & 1))}
    for bank in (1, 2):
        mask = 1 << (bank - 1)
        result[f"permit_a_b{bank}_set_count"] = _count(a, lambda value: bool(value & mask))
        result[f"permit_b_b{bank}_set_count"] = _count(b, lambda value: bool(value & mask))
        result[f"both_permits_b{bank}_set_count"] = sum(
            bool(first & mask and second & mask) for first, second in paired)
    return result


def _since(snapshots: Snapshots, first: int, last: int) -> float:
    """Elapsed time from the tick of snapshot first to the tick of snapshot last."""
    return round(
        (snapshots.ticks[last] - snapshots.ticks[first]) * TICK_SECONDS
        + snapshots.pause_offsets[last]
        - snapshots.pause_offsets[first],
        3,
    )


def _bits(values: list, mask: int) -> list[bool | None]:
    """Bit of each snapshot; None where the snapshot does not carry the byte."""
    return [None if value is None else bool(value & mask) for value in values]


def _rising(flags: list[bool | None], snapshots: Snapshots) -> list[int]:
    return [
        index
        for index, flag in enumerate(flags)
        if flag and (not snapshots.contiguous(index) or flags[index - 1] is not True)
    ]


def _seen(flags: list[bool | None], indices) -> set:
    """The bit states that a window of snapshots observes; None marks a gap."""
    return {flags[index] for index in indices}


def permit_behavior(
    snapshots: Snapshots, phase: dict[int, int], calibration: Calibration
) -> dict:
    """Relate the permit bits of each bank to ticks, gates, and learned updates."""
    columns = snapshots.columns
    stability = columns[STABILITY_PERMIT]
    composite = columns[COMPOSITE_PERMIT]
    if all(value is None for value in stability) or all(value is None for value in composite):
        return {}
    count = len(snapshots)
    ticks = snapshots.ticks
    segments = snapshots.segments
    rpm = columns["rpm_raw"]
    speed = columns["vehicle_speed_kmh"]
    coolant = columns["coolant_raw"]
    threshold = calibration.coolant_threshold_raw
    warm = next(
        (
            index
            for index in refreshes(snapshots, phase, LEARNED_TAG)
            if coolant[index] is not None and coolant[index] >= threshold
        ),
        None,
    )
    cells = replay_cells(snapshots, calibration)
    observed = [
        first is not None and second is not None for first, second in zip(stability, composite)
    ]
    result = {"permit_unobserved_snapshot_count": observed.count(False)}
    for bank in (1, 2):
        held = _bits(stability, 1 << (bank - 1))
        pulse = _bits(composite, 1 << (bank - 1))
        on = [flag is True for flag in held]
        runs = _intervals(on, snapshots)
        prefix = f"stability_permit_b{bank}_"
        result[prefix + "interval_count"] = len(runs)
        result[prefix + "seconds"] = round(sum(_seconds(run, snapshots) for run in runs), 3)
        result[prefix + "longest_seconds"] = max(
            (_seconds(run, snapshots) for run in runs), default=0.0
        )
        result[prefix + "standstill_seconds"] = round(
            TICK_SECONDS * sum(on[i] and speed[i] == 0 for i in range(count)), 3
        )
        result[prefix + "moving_seconds"] = round(
            TICK_SECONDS
            * sum(on[i] and speed[i] is not None and speed[i] > 0 for i in range(count)),
            3,
        )
        revolutions = sum(
            rpm[i] * RPM_RAW_SCALE / 60 * TICK_SECONDS
            for i in range(count)
            if on[i] and rpm[i] is not None
        )
        result[prefix + "expected_tick_count"] = round(
            revolutions / calibration.tick_revolutions, 1
        )
        edges = _rising(pulse, snapshots)
        result[f"composite_permit_b{bank}_pulse_count"] = len(edges)
        result[f"composite_permit_b{bank}_pulse_with_stability_count"] = sum(
            on[index] for index in edges
        )
        first = None if warm is None else next(
            (index for index in range(warm, count) if on[index]), None
        )
        result[prefix + "first_warm_seconds"] = (
            None if first is None else _since(snapshots, warm, first)
        )
        # Unobserved snapshots before the first permit make its time an upper bound.
        result[prefix + "first_warm_unobserved_count"] = (
            None if first is None else held[warm:first].count(None)
        )
        result[prefix + "below_coolant_threshold_count"] = sum(
            on[i] and coolant[i] is not None and coolant[i] < threshold for i in range(count)
        )
        af = columns[f"af_adjustment_b{bank}_raw"]
        result[prefix + "af_adjustment_out_of_bounds_count"] = sum(
            on[i]
            and af[i] is not None
            and not calibration.af_adjustment_low < af[i] <= calibration.af_adjustment_high
            for i in range(count)
        )
        samples = [
            index
            for index in refreshes(snapshots, phase, AF_ADJUSTMENT_TAGS[bank])
            if af[index] is not None
        ]
        drops = Counter()
        for before, after in zip(samples, samples[1:]):
            if (
                ticks[after] - ticks[before] != TAG_COUNT
                or segments[after] != segments[before]
                or af[after] >= af[before]
                or not on[before]
            ):
                continue
            # The latch follows within three coordinator passes; the context
            # sample can lag the change by one tag period.
            window = [
                i
                for i in range(before + 1, min(count, after + TAG_COUNT + 1))
                if segments[i] == segments[before]
            ]
            seen = _seen(held, window)
            drops["with_clear" if False in seen else
                  "unobserved" if None in seen else "held"] += 1
        result[f"af_adjustment_b{bank}_drop_with_stability_count"] = sum(drops.values())
        result[f"af_adjustment_b{bank}_drop_with_clear_count"] = drops["with_clear"]
        result[f"af_adjustment_b{bank}_drop_unobserved_count"] = drops["unobserved"]
        learned = columns[f"ltft_learned_b{bank}_raw"]
        bound = update_bound(snapshots, calibration, bank)
        updates = Counter()
        for before, after in visit_changes(snapshots, phase, cells, bank):
            if abs(learned[after] - learned[before]) > bound:
                continue
            window = range(before + 1, after + 1)
            stable = _seen(held, window)
            pulsed = _seen(pulse, window)
            if True in stable:
                updates["with_stability"] += 1
            elif None in stable:
                updates["unobserved"] += 1
            updates["with_pulse"] += True in pulsed
        result[f"in_visit_update_b{bank}_with_stability_count"] = updates["with_stability"]
        result[f"in_visit_update_b{bank}_with_pulse_count"] = updates["with_pulse"]
        result[f"in_visit_update_b{bank}_unobserved_count"] = updates["unobserved"]
    neutral = _bits(columns[NEUTRAL_CONTROL], 1)
    edges = _rising(neutral, snapshots)
    learned_refreshes = refreshes(snapshots, phase, LEARNED_TAG)
    refilled = 0
    for edge in edges:
        following = next((index for index in learned_refreshes if index > edge), None)
        if following is None or segments[following] != segments[edge]:
            continue
        words = [columns[f"ltft_learned_b{bank}_raw"][following] for bank in (1, 2)]
        refilled += all(word in (None, NEUTRAL) for word in words)
    result["neutral_control_pulse_count"] = len(edges)
    result["neutral_control_pulse_learned_neutral_count"] = refilled
    return result


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
        "learned_b2": (LEARNED_TAG, "ltft_learned_b2_raw"),
        "adjustment_b2": (LEARNED_TAG, "ltft_adjustment_b2_raw"),
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
    for bank in (1, 2):
        available = all(
            any(value is not None for value in columns[f"ltft_{term}_b{bank}_raw"])
            for term in ("learned", "adjustment")
        )
        result[f"summands_b{bank}_available"] = available
        if not available:
            continue
        relation = publication_relation(snapshots, phase, calibration, bank)
        # Retain the bank 1 output keys used by historical capture reports.
        prefix = "" if bank == 1 else "b2_"
        for key in (
            "bracketed", "exact", "nonneutral_exact", "forced_neutral", "other",
            "transition", "transition_bracket", "unbracketed",
        ):
            result[f"{prefix}relation_{key}_count"] = relation[key]
        result.update({prefix + key: value for key, value in
                       learning_changes(snapshots, phase, calibration, bank).items()})
    result.update(learning_controls(snapshots))
    result.update(permit_behavior(snapshots, phase, calibration))
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
