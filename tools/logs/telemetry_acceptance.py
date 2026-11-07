#!/usr/bin/env python3
"""Report transport acceptance of a paired dashboard TRC and MLG recording."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import asdict, replace
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import can_telemetry_history
from tools.can_dashboard import recording
from tools.can_dashboard.model import BASE_TICK_SECONDS, DashboardModel, FrameRecord
from tools.logs import can_telemetry, mlg_relation_audit, peak_trc_audit, trc_to_mlg


TARGET_ENDPOINT = "schema2-profile9"
EXAMPLE_LIMIT = 8
COUNTERS = ("snapshot_overrun_count", "tx_abort_count")


def _sha256(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _f32(value):
    return struct.unpack(">f", struct.pack(">f", value))[0]


def _same_value(left, right):
    if right is None:
        right = math.nan
    return (math.isnan(left) and math.isnan(right)) or left == _f32(right)


def _time_matches(left, right):
    # The Elapsed channel is F32; the TRC stores the shared clock in ms.
    return abs(left - right) <= max(0.00002, abs(right) * 2**-23)


class Pairing:
    """Join MLG events to raw snapshots on the shared recording clock."""

    def __init__(self, path, start_epoch, schema_path):
        self.log = mlg_relation_audit.read_recording(path)
        self.columns = self.log.columns
        required = {"date", "elapsed", "tick16", "schema_verified",
                    "protocol_version", "profile_id", "profile_crc16"}
        missing = required - self.columns.keys()
        if missing:
            raise ValueError(f"MLG lacks required channels: {', '.join(sorted(missing))}")
        self.times = self.columns["elapsed"]
        if any(not math.isfinite(t) or t < 0 for t in self.times) or any(
            b < a for a, b in zip(self.times, self.times[1:])
        ):
            raise ValueError("MLG Elapsed must be finite, nonnegative and ordered")
        self.bindings = {
            b.source: b for b in recording.build_bindings("tuning", schema_path)
            if b.source in self.columns and b.source_kind != "synthetic"
        }
        self.start_epoch = start_epoch
        self.index = 0
        self.previous = None
        self.matched = self.time_matches = self.bridges = self.missing_mlg = self.missing_trc = 0
        self.value_mismatches = self.date_mismatches = 0
        self.examples = []

    def _example(self, **example):
        if len(self.examples) < EXAMPLE_LIMIT:
            self.examples.append(example)

    def _bridge(self, index):
        previous = self.previous
        return previous is not None and _time_matches(
            self.times[index], self.times[previous] + recording.MAX_GAP_SECONDS
        ) and all(
            _same_value(self.columns[name][index], self.columns[name][previous])
            for name in self.bindings
        ) and self._date_valid(index, self.times[index])

    def _date_valid(self, index, time):
        if self.start_epoch is None:
            return True
        date = self.columns["date"][index]
        tolerance = max(0.00002, abs(time) * 2**-23)
        # OLE text and F32 elapsed rounding can cross an integer-second edge.
        return math.isfinite(date) and (
            math.floor(self.start_epoch + time - tolerance) <= date
            <= math.floor(self.start_epoch + time + tolerance)
        )

    def snapshot(self, model, time):
        while self.index < self.log.record_count and (
            self.times[self.index] < time and not _time_matches(self.times[self.index], time)
        ):
            if self._bridge(self.index):
                self.bridges += 1
                self.previous = self.index
            else:
                self.missing_trc += 1
                self._example(kind="mlg_without_snapshot", elapsed=self.times[self.index])
            self.index += 1
        if self.index == self.log.record_count or not _time_matches(
            self.times[self.index], time
        ):
            self.missing_mlg += 1
            self._example(kind="snapshot_without_mlg", elapsed=time)
            return
        index = self.index
        self.time_matches += 1
        previous_errors = self.value_mismatches + self.date_mismatches
        for name, binding in self.bindings.items():
            expected = (
                getattr(model, name, None) if binding.source_kind == "attribute"
                else model.raw.get(name)
            )
            actual = self.columns[name][index]
            if not _same_value(actual, expected):
                self.value_mismatches += 1
                self._example(
                    kind="value_mismatch", elapsed=time, field=name,
                    actual=actual if math.isfinite(actual) else None,
                    expected=expected if expected is not None and math.isfinite(expected) else None,
                )
        if not self._date_valid(index, time):
            self.date_mismatches += 1
            self._example(kind="date_mismatch", elapsed=time)
        if previous_errors == self.value_mismatches + self.date_mismatches:
            self.matched += 1
        self.previous = index
        self.index += 1

    def result(self):
        self.missing_trc += self.log.record_count - self.index
        failed = any((self.missing_mlg, self.missing_trc,
                      self.value_mismatches, self.date_mismatches))
        return {
            "status": "FAIL" if failed else (
                "PASS" if self.matched and self.start_epoch is not None else "INCOMPLETE"
            ),
            "clock": "TRC offset / 1000 = MLG Elapsed; no fitted offset",
            "absolute_clock_available": self.start_epoch is not None,
            "records": self.log.record_count,
            "compared_channels": sorted(self.bindings),
            "matched_snapshots": self.matched,
            "time_matches": self.time_matches,
            "bridge_records": self.bridges,
            "snapshots_without_mlg": self.missing_mlg,
            "mlg_without_snapshot": self.missing_trc,
            "value_mismatches": self.value_mismatches,
            "date_mismatches": self.date_mismatches,
            "examples": self.examples,
        }


def _stock_periods(trace, can_id):
    frames = tuple(
        frame for frame in trace.frames
        if frame.direction == "Rx" and not frame.extended and not frame.remote
        and frame.can_id not in (can_id, can_id + 1)
    )
    if not frames:
        return []
    return [asdict(item) for item in peak_trc_audit.audit_trace(
        replace(trace, frames=frames, status_records=()), candidate_id=can_id
    ).identifiers]


def _cadence(periods, baseline, tolerance):
    if baseline is None:
        return {"status": "NOT_ASSESSED", "reason": "no baseline supplied"}
    reference = {row["can_id"]: row for row in baseline}
    observed = {row["can_id"]: row for row in periods}
    rows = []
    for can_id in sorted(reference.keys() | observed.keys()):
        left, right = reference.get(can_id), observed.get(can_id)
        row = {"can_id": can_id}
        if left is None or left["median_period_ms"] is None:
            row["status"] = "NOT_ASSESSED"
        elif right is None or right["median_period_ms"] is None:
            row["status"] = "NOT_ASSESSED"
        else:
            deltas = {
                name: right[name] - left[name] for name in (
                    "median_period_ms", "p99_period_ms", "maximum_period_ms"
                )
            }
            row["delta_ms"] = deltas
            row["status"] = "NOT_ASSESSED" if tolerance is None else (
                "PASS" if abs(deltas["median_period_ms"]) <= tolerance
                and deltas["p99_period_ms"] <= tolerance
                and deltas["maximum_period_ms"] <= tolerance else "FAIL"
            )
        rows.append(row)
    statuses = {row["status"] for row in rows}
    status = "FAIL" if "FAIL" in statuses else (
        "PASS" if statuses == {"PASS"} else "NOT_ASSESSED"
    )
    return {"status": status, "tolerance_ms": tolerance, "identifiers": rows}


def audit_capture(trc, mlg, *, bitrate=None, baseline=None, cadence_tolerance_ms=None,
                  can_id=0x6F0, tick_divisor=1, timezone="Asia/Vladivostok",
                  schema_path=can_telemetry.DEFAULT_SCHEMA):
    """Audit observed transport; hardware identity and lamps need operator evidence."""
    if cadence_tolerance_ms is not None and (
        not math.isfinite(cadence_tolerance_ms) or cadence_tolerance_ms < 0
        or baseline is None
    ):
        raise ValueError("cadence tolerance requires a baseline and must be finite and nonnegative")
    target = can_telemetry_history.endpoint(TARGET_ENDPOINT)
    if target is None:
        raise ValueError(f"unregistered target endpoint {TARGET_ENDPOINT}")
    expected = (target.protocol_version, target.profile_id, target.profile_crc16)
    trace = peak_trc_audit.load_trace(trc)
    bus = peak_trc_audit.audit_trace(trace, candidate_id=can_id, bitrate=bitrate)
    start_epoch = trc_to_mlg.trace_start_epoch(trace, timezone) if trace.start_time else None
    pair = Pairing(mlg, start_epoch, schema_path)
    model = DashboardModel("tuning", can_id, tick_divisor, schema_path)
    pages = Counter()
    identities = Counter()
    health = defaultdict(list)
    runs = defaultdict(lambda: ([], []))
    prefix = non_rx = verified = 0
    tick_steps = []
    seen_zero = False
    for frame in trace.frames:
        if frame.extended or frame.remote:
            continue
        if frame.can_id == can_id:
            if frame.direction != "Rx":
                non_rx += 1
                continue
            if len(frame.data) == 8:
                page = frame.data[0] & 0x0F
                pages[page] += 1
                if not seen_zero and page != 0:
                    prefix += 1
                seen_zero |= page == 0
        time = frame.offset_ms / 1000
        mismatches = model.decoder.schema_mismatches
        snapshot = model.process_frame(FrameRecord(
            arbitration_id=frame.can_id, data=frame.data, timestamp=time,
            received_monotonic=time,
        ), now=time)
        if model.decoder.schema_mismatches > mismatches:
            identities[model.decoder.reported_identity] += 1
        if snapshot is None:
            continue
        if "protocol_version" in snapshot.fields:
            identity = tuple(snapshot.fields[name] for name in (
                "protocol_version", "profile_id", "profile_crc16"
            ))
            identities[identity] += 1
            for name in COUNTERS:
                health[(snapshot.run, name)].append(snapshot.fields[name])
        verified += snapshot.schema_verified
        ticks, times = runs[snapshot.run]
        if ticks and snapshot.unwrapped_tick - ticks[-1] != tick_divisor:
            if len(tick_steps) < EXAMPLE_LIMIT:
                tick_steps.append({"run": snapshot.run, "from_tick": ticks[-1],
                                   "to_tick": snapshot.unwrapped_tick, "elapsed": time})
        ticks.append(snapshot.unwrapped_tick)
        times.append(time)
        pair.snapshot(model, time)
    decoder = model.decoder
    pauses = []
    for run, (ticks, times) in runs.items():
        pauses.extend(
            {"run": run, "elapsed": times[index], "seconds": duration}
            for index, duration in enumerate(can_telemetry.stream_pauses(
                ticks, times, BASE_TICK_SECONDS
            )) if duration
        )
    counter_rows = [
        {"run": run, "name": name, "samples": len(values), "first": values[0],
         "last": values[-1], "increments": sum(
             (b - a) & 0xFF for a, b in zip(values, values[1:])
         )} for (run, name), values in sorted(health.items())
    ]
    group_errors = {
        "incomplete_groups": decoder.incomplete_groups,
        "malformed_frames": decoder.malformed_frames,
        "schema_mismatches": decoder.schema_mismatches,
        "unknown_configurations": decoder.unknown_configurations,
        "producer_restarts": decoder.producer_restarts,
        "missed_snapshots": model.missed_snapshots,
        "unexpected_tick_steps": model.unexpected_tick_steps,
        "non_rx_telemetry": non_rx,
    }
    periods = _stock_periods(trace, can_id)
    baseline_trace = None
    if baseline is not None:
        if Path(baseline).resolve() == Path(trc).resolve() or _sha256(baseline) == _sha256(trc):
            raise ValueError("baseline must be a distinct recording")
        baseline_trace = peak_trc_audit.load_trace(baseline)
    cadence = _cadence(periods, None if baseline_trace is None else
                       _stock_periods(baseline_trace, can_id), cadence_tolerance_ms)
    if baseline_trace is not None:
        baseline_warnings = sum(row.kind == "Warng" for row in baseline_trace.status_records)
        baseline_errors = sum(row.kind == "Error" for row in baseline_trace.status_records)
        cadence["baseline"] = {"path": str(baseline), "sha256": _sha256(baseline),
                               "warning_count": baseline_warnings, "error_count": baseline_errors}
        if baseline_trace.incomplete_tail is not None or baseline_warnings or baseline_errors:
            cadence["status"] = "INCOMPLETE"
            cadence["reason"] = "baseline contains CAN notifications or an excluded cut tail"
    report = {
        "scope": "telemetry_transport",
        "target": {"endpoint": TARGET_ENDPOINT, "identity": list(expected),
                   "page_count": target.page_count},
        "inputs": {"trc": str(trc), "trc_sha256": _sha256(trc),
                   "mlg": str(mlg), "mlg_sha256": pair.log.sha256},
        "identity": {
            "status": "FAIL" if any(i != expected for i in identities) else (
                "PASS" if identities else "INCOMPLETE"
            ),
            "observed": [{"identity": list(i), "health_groups": count}
                         for i, count in sorted(identities.items())],
        },
        "groups": {
            "status": "FAIL" if any(group_errors.values()) or pauses else (
                "PASS" if decoder.completed_groups and set(pages) == set(range(target.page_count))
                else "INCOMPLETE"
            ),
            "completed": decoder.completed_groups, "verified": verified,
            "tick_divisor": tick_divisor, "page_frames": dict(sorted(pages.items())),
            **group_errors, "pauses": pauses,
            "tick_step_examples": tick_steps,
            "synchronization_prefix_frames": prefix,
            "incomplete_tail_pages": decoder.pending_page_count,
        },
        "health_counters": {
            "status": "FAIL" if any(row["increments"] for row in counter_rows) else (
                "PASS" if counter_rows and all(
                    row["samples"] >= 2 and row["first"] == 0 for row in counter_rows
                ) else "INCOMPLETE"
            ), "observations": counter_rows,
        },
        "pairing": pair.result(),
        "can": {"status": "FAIL" if bus.warning_count or bus.error_count else "PASS",
                "warning_count": bus.warning_count, "error_count": bus.error_count,
                "notifications": [
                    {"record": row.number, "elapsed": row.offset_ms / 1000,
                     "kind": row.kind, "code": row.code, "data": row.data.hex(),
                     "description": row.description}
                    for row in trace.status_records[:EXAMPLE_LIMIT]
                ],
                "load_status": "REPORTED" if bus.load is not None else "NOT_ASSESSED",
                "load": None if bus.load is None else asdict(bus.load)},
        "recording": {
            "status": "INCOMPLETE" if trace.incomplete_tail else "PASS",
            "excluded_trc_tail": None if trace.incomplete_tail is None else asdict(trace.incomplete_tail),
            "boundary": "Parsed files do not establish operator-confirmed clean shutdown.",
        },
        "stock_frames": periods, "cadence": cadence,
    }
    statuses = {report[name]["status"] for name in (
        "identity", "groups", "health_counters", "pairing", "can", "recording", "cadence"
    )}
    report["status"] = "FAIL" if "FAIL" in statuses else (
        "PASS" if statuses == {"PASS"} and bitrate is not None else "INCOMPLETE"
    )
    return report


def format_report(report):
    target = report["target"]["identity"]
    lines = [f"Transport acceptance: {report['status']}",
             f"Registered target: {target[0]}/{target[1]}/0x{target[2]:04X}"]
    for name in ("identity", "groups", "health_counters", "pairing", "can", "recording", "cadence"):
        lines.append(f"{name}: {json.dumps(report[name], allow_nan=False, sort_keys=True)}")
    lines.append("Stock RX periods (ms): ID count median p99 max")
    for row in report["stock_frames"]:
        values = " ".join("n/a" if row[name] is None else f"{row[name]:.4f}"
                          for name in ("median_period_ms", "p99_period_ms", "maximum_period_ms"))
        lines.append(f"0x{row['can_id']:03X} {row['count']} {values}")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trc", type=Path)
    parser.add_argument("mlg", type=Path)
    parser.add_argument("--bitrate", type=int, help="recorded CAN bitrate; TRC does not declare it")
    parser.add_argument("--baseline", type=Path, help="distinct stock-cadence reference TRC")
    parser.add_argument("--cadence-tolerance-ms", type=float,
                        help="absolute median drift and maximum p99/max increase against baseline")
    parser.add_argument("--can-id", type=lambda value: int(value, 0), default=0x6F0)
    parser.add_argument("--tick-divisor", type=int, default=1)
    parser.add_argument("--timezone", default="Asia/Vladivostok")
    parser.add_argument("--schema", type=Path, default=can_telemetry.DEFAULT_SCHEMA)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = audit_capture(args.trc, args.mlg, bitrate=args.bitrate,
                               baseline=args.baseline, cadence_tolerance_ms=args.cadence_tolerance_ms,
                               can_id=args.can_id, tick_divisor=args.tick_divisor, timezone=args.timezone,
                               schema_path=args.schema)
    except (ValueError, OSError) as error:
        print(json.dumps({"status": "ERROR", "error": str(error)}) if args.json else
              f"Transport acceptance: ERROR: {error}")
        return 2
    print(json.dumps(report, allow_nan=False, sort_keys=True) if args.json else format_report(report))
    return {"PASS": 0, "FAIL": 1, "INCOMPLETE": 2}[report["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
