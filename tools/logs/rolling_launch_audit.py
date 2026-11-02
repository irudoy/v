#!/usr/bin/env python3
"""Audit the Rolling Launch hold of a JK08A tuning MLG or TRC capture.

The reader returns the verified snapshots of a capture. Each snapshot carries
the stock button and dashboard frames, vehicle speed, coolant, the
fuel-inhibit, timing, APC, pedal, BFS, knock-surface, and exhaust-CVTC
telemetry sources, and the Rolling Launch phase and abort reason. The
integrator, speed error, torque fraction, and cut counter are slots of the
launch-law configurations of the dynamic page: a snapshot carries the slots
that the configuration and group of its configuration byte name, and the
others read None.

The hold audit replays the speed controller of `patches/rolling_launch.py`
with the calibration of the flashed image through every ACTIVE run. The
speed error of a snapshot lies inside the abort window. The model integrator
follows the published errors from zero at the entry tick, or from a published
integrator; the model fraction follows from the previous fraction through the
rate limit. A snapshot without the speed error leaves the integrator unknown,
and one without the fraction widens the previous fraction by the rate limit.
Under the one-group configuration every snapshot carries the error, the
fraction, and the cut counter, so every fraction equals its model step. Under
the two-group configuration a snapshot of group 0 follows a published
integrator and a snapshot whose fraction is unknown, so its fraction lies in
the model range of the two-tick step. In hold mode the cut counter of a run
lies within the cuts that the delivered fractions owe the spark events of its
engine speed.

Engine speed is the coordinate `0xFFFF11F4` in counts of 12.5 RPM, which is a
shift of the word that stock frame 0x180 carries. The frame is sampled at
another instant of the cycle, so every RPM bound spans the frames recorded
with the snapshot and with the next one, widened by `STOCK_RPM_MARGIN` counts.

A TRC adds frame times: the first and last page of every snapshot group and
the context frames of 0x239 and 0x551.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
import hashlib
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import rolling_launch
from patches.rolling_launch_layout import load_layout
from tools.can_dashboard.model import (
    ASCD_BUTTON_ID,
    DASHBOARD_STATE_ID,
    DashboardModel,
    FrameRecord,
)
from tools.logs import can_telemetry
from tools.logs import mlg_relation_audit
from tools.logs import mlg_retime
from tools.logs import peak_trc_audit

# The coordinate of a snapshot lies between the stock frames recorded with it
# and with the next snapshot apart from the update jitter that registry entry
# can_telemetry.stock_speed_bracket_2026_09_22 bounds; the margin exceeds it.
STOCK_RPM_MARGIN = 8
TELEMETRY_SOURCES = (
    "fuel_inhibit_mask",
    "final_timing_raw",
    "apc_command_raw",
    "app1_raw",
    "bfs_raw",
    "knock_surface_state",
    "exhaust_cvtc_target_raw",
)
CONTEXT_SOURCES = (
    "ascd_button_raw",
    "dashboard_state_raw",
    "vehicle_speed_kmh",
    "coolant_raw",
)
# The Rolling Launch fields of the hold audit and their sample attributes.
# The phase and the abort reason are fixed and context fields; the others are
# slots of the dynamic page.
HOLD_SOURCES = {
    "rolling_launch_phase": "phase",
    "rolling_launch_abort_reason": "abort_reason",
    "rolling_launch_integrator_raw": "integrator",
    "rolling_launch_speed_error_raw": "speed_error",
    "rolling_launch_torque_fraction_raw": "torque_fraction",
    "rolling_launch_cut_counter": "cut_counter",
}
# Spark events per tick and native RPM count: three events per revolution,
# 12.5 RPM per count, and 10.24 ms per tick.
EVENTS_PER_COUNT_TICK = 3 * 12.5 / 60 * 0.01024
# The six accumulators start a run at offsets that sum to 2.75 cuts, and each
# truncates less than one cut, so a run that owes E cuts makes more than
# E - 3.25 and at most E + 2.75. One event of phase uncertainty at each end of
# the run widens both sides by one cut.
_OFFSET_CUTS = (
    sum(rolling_launch.SPARK_CYLINDER_OFFSETS) / rolling_launch.SPARK_CUT_ONE
)
CUTS_BELOW = _OFFSET_CUTS - rolling_launch.SPARK_CYLINDER_COUNT - 1
CUTS_ABOVE = _OFFSET_CUTS + 1
# Every tag of the rotating context pages is refreshed within this many
# snapshots, so the abort reason of the snapshot this far after the abort
# tick was captured after it.
CONTEXT_REFRESH_SNAPSHOTS = 5


@dataclass(frozen=True)
class Sample:
    tick: int
    button: int | None
    dashboard: int | None
    speed_kmh: float | None
    coolant_raw: int | None
    rpm_raw: int
    rpm_low: int
    rpm_high: int
    fuel_inhibit_mask: int
    final_timing_raw: int
    apc_command_raw: int
    app1_raw: int
    bfs_raw: int
    knock_surface_state: int
    exhaust_cvtc_target_raw: int
    phase: int | None = None
    abort_reason: int | None = None
    integrator: int | None = None
    speed_error: int | None = None
    torque_fraction: int | None = None
    cut_counter: int | None = None
    # The configuration byte of the dynamic page.
    configuration: int | None = None


@dataclass(frozen=True)
class DynamicPage:
    """The fields that the configuration byte of a snapshot makes current.

    A field outside the dynamic page is current in every snapshot. A slot
    field is current only when the configuration and group of the byte name
    it, because the dashboard holds the last value of a slot that the
    snapshot does not carry.
    """

    field: str | None
    dynamic: frozenset
    groups: dict

    @classmethod
    def of(cls, profile):
        return cls(
            can_telemetry.configuration_field(profile),
            can_telemetry.dynamic_field_names(profile),
            {
                row["id"] | index << 7: frozenset(names)
                for row in profile.get("configurations", ())
                for index, names in enumerate(row["groups"])
            },
        )

    def carries(self, selector, name):
        return name not in self.dynamic or name in self.groups.get(selector, ())


@dataclass(frozen=True)
class TraceTiming:
    """Frame times of a TRC in milliseconds from the trace start.

    The page times align with the verified snapshots; the context frames hold
    byte 3 of every 0x239 frame and byte 5 of every 0x551 frame.
    """

    first_page_ms: tuple[float, ...]
    last_page_ms: tuple[float, ...]
    button_frames: tuple[tuple[float, int], ...]
    dashboard_frames: tuple[tuple[float, int], ...]


@dataclass(frozen=True)
class Capture:
    path: Path
    sha256: str
    samples: tuple[Sample, ...]
    timing: TraceTiming | None = None


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _optional_int(value) -> int | None:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    return int(value)


def _optional_float(value) -> float | None:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    return float(value)


def _sample(tick: int, value, rpm_raw: int, page: DynamicPage) -> Sample:
    selector = None if page.field is None else _optional_int(value(page.field))
    return Sample(
        tick=tick,
        button=_optional_int(value("ascd_button_raw")),
        dashboard=_optional_int(value("dashboard_state_raw")),
        speed_kmh=_optional_float(value("vehicle_speed_kmh")),
        coolant_raw=_optional_int(value("coolant_raw")),
        rpm_raw=rpm_raw,
        rpm_low=rpm_raw,
        rpm_high=rpm_raw,
        **{name: int(value(name)) for name in TELEMETRY_SOURCES},
        **{
            attribute: (
                _optional_int(value(name)) if page.carries(selector, name) else None
            )
            for name, attribute in HOLD_SOURCES.items()
        },
        configuration=selector,
    )


def stock_speed_pairs(samples) -> list[tuple[int, int]]:
    """Return the lower and upper word of the stock frames around each snapshot.

    The stock frame recorded with a snapshot precedes its group, and the frame
    recorded with the next snapshot follows it. A snapshot without a next one
    keeps its own frame.
    """
    pairs = []
    for index, sample in enumerate(samples):
        words = [sample.rpm_raw]
        if index + 1 < len(samples) and samples[index + 1].tick == sample.tick + 1:
            words.append(samples[index + 1].rpm_raw)
        pairs.append((min(words), max(words)))
    return pairs


def _stock_speed_bounds(samples: list[Sample]) -> list[Sample]:
    """Widen each stock-frame word to the words its snapshot can carry."""
    return [
        replace(
            sample,
            rpm_low=max(0, low - STOCK_RPM_MARGIN),
            rpm_high=high + STOCK_RPM_MARGIN,
        )
        for sample, (low, high) in zip(samples, stock_speed_pairs(samples))
    ]


def read_mlg(path: Path) -> Capture:
    """Read the verified snapshots of one dashboard MLVLG recording."""
    recording_ = mlg_relation_audit.read_recording(path)
    columns = recording_.columns
    required = ("tick16", "schema_verified", *TELEMETRY_SOURCES, *CONTEXT_SOURCES)
    missing = [name for name in required if name not in columns]
    rpm = mlg_relation_audit.engine_speed_counts(recording_)
    if rpm is None:
        missing.append("engine speed")
    if missing:
        raise ValueError(f"{path}: missing channels {', '.join(missing)}")
    ticks = mlg_retime.unwrap_ticks(columns["tick16"])
    page = DynamicPage.of(can_telemetry.load_schema()[1]["tuning"])
    samples = []
    previous = None
    for index, tick in enumerate(ticks):
        # A bridge record repeats the preceding snapshot, tick included.
        if tick == previous or columns["schema_verified"][index] != 1:
            continue
        previous = tick
        if rpm[index] is None:
            continue
        samples.append(
            _sample(
                tick,
                lambda name: columns[name][index] if name in columns else None,
                rpm[index],
                page,
            )
        )
    return Capture(
        Path(path), recording_.sha256, tuple(_stock_speed_bounds(samples))
    )


def read_trc(
    path: Path,
    *,
    profile: str = "tuning",
    can_id: int = 0x6F0,
    tick_divisor: int = 1,
) -> Capture:
    """Replay a PEAK TRC through the dashboard model into verified snapshots."""
    path = Path(path)
    digest = _sha256_file(path)
    trace = peak_trc_audit.load_trace(path)
    model = DashboardModel(profile, can_id, tick_divisor)
    page = DynamicPage.of(model.decoder.profile)
    samples = []
    first_pages = []
    last_pages = []
    buttons = []
    dashboard = []
    group_start = None
    run = None
    for frame in trace.frames:
        timestamp = frame.offset_ms / 1000.0
        standard = not frame.extended and not frame.remote
        if standard and frame.can_id == can_id and len(frame.data) == 8:
            # The low nibble of byte 0 is the page index of a group.
            if not frame.data[0] & 0x0F:
                group_start = frame.offset_ms
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
        if standard and frame.can_id == ASCD_BUTTON_ID and len(frame.data) >= 4:
            buttons.append((frame.offset_ms, model.ascd_button_raw))
        elif (
            standard and frame.can_id == DASHBOARD_STATE_ID and len(frame.data) >= 6
        ):
            dashboard.append((frame.offset_ms, model.dashboard_state_raw))
        if snapshot is None or not model.schema_verified:
            continue
        if any(name not in model.raw for name in TELEMETRY_SOURCES):
            continue
        rpm_raw = model.engine_speed_counts
        if rpm_raw is None:
            continue
        if run is None:
            run = snapshot.run
        elif snapshot.run != run:
            raise ValueError(f"{path}: the capture spans more than one producer run")

        def value(name):
            if name in model.raw:
                return model.raw[name]
            return getattr(model, name, None)

        samples.append(_sample(snapshot.unwrapped_tick, value, rpm_raw, page))
        first_pages.append(group_start)
        last_pages.append(frame.offset_ms)
    timing = TraceTiming(
        tuple(first_pages), tuple(last_pages), tuple(buttons), tuple(dashboard)
    )
    return Capture(path, digest, tuple(_stock_speed_bounds(samples)), timing)


def read_capture(path: Path, **options) -> Capture:
    if Path(path).suffix.lower() == ".trc":
        return read_trc(path, **options)
    return read_mlg(path)



@dataclass(frozen=True)
class HoldRun:
    """One ACTIVE run of contiguous snapshots and its audit results.

    `law_ticks` counts the snapshots whose torque fraction was checked
    against the model step.
    `target_speed` is the range of the stock-frame speed minus the published
    error in km/h*10, which stays narrow while the speed word follows the
    frame. `cuts` and `owed` are None outside hold mode, for a run without
    the snapshots before and after it, and when a fraction of the run or a
    cut counter of those snapshots is unknown.
    """

    start_tick: int
    end_tick: int
    abort_reason: int | None
    law_ticks: int
    failures: tuple[tuple[int, str], ...]
    target_speed: tuple[float, float] | None
    ceiling_ticks: int
    cuts: int | None
    owed: tuple[float, float] | None

    @property
    def cuts_inside(self) -> bool | None:
        if self.cuts is None or self.owed is None:
            return None
        return self.owed[0] < self.cuts <= self.owed[1]


def read_calibration(image: Path) -> rolling_launch.Calibration:
    """Read the Rolling Launch configuration record of a flashed image."""
    span = load_layout().configuration
    data = Path(image).read_bytes()
    if len(data) < span.end:
        raise ValueError(f"{image}: image ends before the configuration record")
    calibration = rolling_launch.Calibration.from_bytes(data[span.start : span.end])
    if not calibration.is_valid():
        raise ValueError(f"{image}: the Rolling Launch configuration is invalid")
    return calibration


def _predecessor(samples, index):
    if index and samples[index - 1].tick == samples[index].tick - 1:
        return samples[index - 1]
    return None


def _replay(samples, start, end, calibration):
    """Replay the controller through one ACTIVE run.

    Return the failures, the count of checked fractions, and the bounds of
    the torque fraction at every snapshot of the run, None where unknown.
    """
    unit = rolling_launch.U_ONE
    rate = calibration.u_rate_limit
    previous = _predecessor(samples, start)
    integrator = fraction = None
    if previous is not None and previous.phase == rolling_launch.Phase.IDLE:
        integrator, fraction = 0, (unit, unit)
    failures = []
    law_ticks = 0
    bounds = []
    for sample in samples[start : end + 1]:
        error = sample.speed_error
        command = None
        if error is None:
            integrator = None
        else:
            if not -calibration.abort_below <= error <= calibration.abort_above:
                failures.append(
                    (sample.tick, "speed error outside the abort window")
                )
            if integrator is not None:
                proportional = rolling_launch.proportional_fraction(
                    error, calibration
                )
                integrator = rolling_launch.update_integrator(
                    integrator, proportional, error, calibration
                )
                command = min(
                    max(
                        proportional
                        + (integrator >> rolling_launch.INTEGRATOR_SHIFT),
                        0,
                    ),
                    unit,
                )
        if fraction is not None:
            low, high = fraction
            if command is None:
                fraction = max(0, low - rate), min(unit, high + rate)
            else:
                fraction = (
                    min(max(command, low - rate), low + rate),
                    min(max(command, high - rate), high + rate),
                )
        if sample.integrator is not None:
            if integrator is not None and sample.integrator != integrator:
                failures.append(
                    (sample.tick,
                     f"integrator {sample.integrator}, model {integrator}")
                )
            integrator = sample.integrator
        published = sample.torque_fraction
        if published is not None:
            if command is not None and fraction is not None:
                law_ticks += 1
                low, high = fraction
                if not low <= published <= high:
                    model = low if low == high else f"{low}..{high}"
                    failures.append(
                        (sample.tick,
                         f"torque fraction {published}, model {model}")
                    )
            fraction = published, published
        bounds.append(fraction)
    return failures, law_ticks, bounds


def _abort_reason(samples, end):
    """The abort reason of the snapshot that the context refresh makes
    fresh after the run, or None when the capture lacks it."""
    tick = samples[end].tick + CONTEXT_REFRESH_SNAPSHOTS
    for sample in samples[end + 1 : end + 1 + CONTEXT_REFRESH_SNAPSHOTS]:
        if sample.phase != rolling_launch.Phase.COOLDOWN:
            return None
        if sample.tick == tick:
            return sample.abort_reason
    return None


def _owed_cuts(samples, start, end, bounds):
    """The bounds of the cuts owed from the IDLE snapshot before the run
    through the snapshot after it, or None without both of them or with a
    fraction of the run unknown."""
    before = _predecessor(samples, start)
    after = end + 1 < len(samples) and samples[end + 1].tick == samples[end].tick + 1
    if before is None or not after or None in bounds:
        return None
    unit = rolling_launch.U_ONE
    low = high = 0.0
    for index in range(start, end + 2):
        sample = samples[index]
        fractions = []
        if index <= end:
            fractions.append(bounds[index - start])
        if index > start:
            fractions.append(bounds[index - start - 1])
        # Before the update of the entry tick the phase is IDLE, and after the
        # update of the tick that ends the run it is COOLDOWN; both cut nothing.
        if index in (start, end + 1):
            fractions.append((unit, unit))
        low += sample.rpm_low * EVENTS_PER_COUNT_TICK * min(
            unit - fraction for _low, fraction in fractions
        )
        high += sample.rpm_high * EVENTS_PER_COUNT_TICK * max(
            unit - fraction for fraction, _high in fractions
        )
    return max(0.0, low / unit + CUTS_BELOW), high / unit + CUTS_ABOVE


def audit_hold(samples, calibration) -> tuple[HoldRun, ...]:
    """Audit every ACTIVE run of the verified snapshots.

    The replay steps the controller once per snapshot, so a capture whose
    snapshots do not step by one tick, which a tick divisor above 1
    produces, is refused.
    """
    samples = list(samples)
    if not any(sample.phase is not None for sample in samples):
        raise ValueError("the capture carries no Rolling Launch phase")
    step = math.gcd(
        *(after.tick - before.tick for before, after in zip(samples, samples[1:]))
    )
    if step > 1:
        raise ValueError(
            f"the snapshots step by {step} ticks; the hold audit needs one"
            " snapshot per tick"
        )
    active = rolling_launch.Phase.ACTIVE
    runs = []
    index = 0
    while index < len(samples):
        if samples[index].phase != active:
            index += 1
            continue
        start = index
        while (
            index + 1 < len(samples)
            and samples[index + 1].phase == active
            and samples[index + 1].tick == samples[index].tick + 1
        ):
            index += 1
        runs.append(_run(samples, start, index, calibration))
        index += 1
    return tuple(runs)


def _run(samples, start, end, calibration):
    run = samples[start : end + 1]
    for sample in run:
        if sample.speed_error is None and sample.integrator is None:
            raise ValueError(
                f"tick {sample.tick}: the capture lacks the Rolling Launch"
                " hold fields"
            )
    failures, law_ticks, bounds = _replay(samples, start, end, calibration)
    targets = [
        sample.speed_kmh * 10 - sample.speed_error
        for sample in run
        if sample.speed_kmh is not None and sample.speed_error is not None
    ]
    cuts = owed = None
    if calibration.mode == rolling_launch.Mode.HOLD:
        owed = _owed_cuts(samples, start, end, bounds)
        if owed is not None:
            counters = [
                sample.cut_counter for sample in samples[start - 1 : end + 2]
            ]
            if None in counters:
                owed = None
            else:
                cuts = sum(
                    (after - before) & 0xFF
                    for before, after in zip(counters, counters[1:])
                )
    return HoldRun(
        start_tick=samples[start].tick,
        end_tick=samples[end].tick,
        abort_reason=_abort_reason(samples, end),
        law_ticks=law_ticks,
        failures=tuple(failures),
        target_speed=(min(targets), max(targets)) if targets else None,
        ceiling_ticks=sum(
            sample.fuel_inhibit_mask & rolling_launch.FUEL_CUT_CYLINDER_MASK
            == rolling_launch.FUEL_CUT_CYLINDER_MASK
            for sample in run
        ),
        cuts=cuts,
        owed=owed,
    )


def _reason_name(reason):
    if reason is None:
        return "unknown"
    try:
        return rolling_launch.AbortReason(reason).name
    except ValueError:
        return str(reason)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--image", type=Path, required=True,
        help="flashed image whose Rolling Launch configuration ran",
    )
    parser.add_argument("captures", type=Path, nargs="+")
    args = parser.parse_args(argv)
    calibration = read_calibration(args.image)
    failed = False
    for path in args.captures:
        capture = read_capture(path)
        runs = audit_hold(capture.samples, calibration)
        print(f"{capture.path.name} sha256={capture.sha256} runs={len(runs)}")
        # A capture without a run, or a run without a checked fraction,
        # checks nothing and cannot pass.
        failed |= not runs
        for run in runs:
            target = (
                "none" if run.target_speed is None
                else f"{run.target_speed[0]:.0f}..{run.target_speed[1]:.0f}"
            )
            cuts = "n/a"
            if run.cuts is not None:
                low, high = run.owed
                cuts = f"{run.cuts} owed ({low:.2f}, {high:.2f}]"
            print(
                f"  ticks {run.start_tick}..{run.end_tick}"
                f" abort={_reason_name(run.abort_reason)}"
                f" law_ticks={run.law_ticks}"
                f" failed_ticks={len({tick for tick, _ in run.failures})}"
                f" target={target}"
                f" ceiling_ticks={run.ceiling_ticks} cuts={cuts}"
            )
            for tick, failure in run.failures:
                print(f"    tick {tick}: {failure}")
            failed |= (
                bool(run.failures)
                or run.cuts_inside is False
                or not run.law_ticks
            )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
