import contextlib
from dataclasses import replace
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
import warnings

from patches import can_telemetry_history
from tools.can_dashboard import excerpt, model, recording, raw_log
from tools.logs import can_telemetry, telemetry_acceptance as audit
from tools.logs import trc_to_mlg
from tools.logs.tests import test_can_telemetry


EPOCH = trc_to_mlg.trace_start_epoch(
    SimpleNamespace(start_time="46333.5"), "Asia/Vladivostok"
)
HEADER = raw_log.header(EPOCH)


def write_capture(root, *, ticks=range(1, 31), mutate=None, schema_path=None,
                  pause_after=None, time_scale=1.0, mlg_mutate=None, epoch=EPOCH):
    """Use the wire demo and the production recorder on one shared clock."""
    root.mkdir(parents=True, exist_ok=True)
    endpoint = can_telemetry_history.endpoint(audit.TARGET_ENDPOINT)
    schema = schema_path or (
        can_telemetry_history.REGISTRY.parent / endpoint.host_schema
    )
    generator = model.DemoGenerator(schema_path=schema)
    dashboard = model.DashboardModel(schema_path=schema_path or can_telemetry.DEFAULT_SCHEMA)
    trc, mlg, baseline = (root / name for name in ("drive.trc", "drive.mlg", "baseline.trc"))
    rows, stock_rows = [HEADER], [HEADER]
    frames = []
    for index, tick in enumerate(ticks):
        time = 1 + index * model.BASE_TICK_SECONDS * time_scale
        if pause_after is not None and index >= pause_after:
            time += 2
        group = [*generator.stock_context(tick, time), *generator.group(tick, time)]
        if mutate:
            group = mutate(tick, group)
        for offset, frame in enumerate(group):
            frame = replace(frame, timestamp=time + offset * 0.00005,
                            received_monotonic=time + offset * 0.00005)
            frames.append(frame)
            rows.append(raw_log.row(len(frames), frame.timestamp, frame))
            if frame.arbitration_id != model.DEFAULT_CAN_ID:
                stock_rows.append(raw_log.row(len(stock_rows), frame.timestamp, frame))
    trc.write_text("".join(rows), encoding="ascii")
    baseline.write_text("".join(stock_rows), encoding="ascii")
    writer = recording.TelemetryMlgRecorder(
        mlg, "tuning", epoch, schema_path=schema_path or can_telemetry.DEFAULT_SCHEMA
    )
    for frame in frames:
        snapshot = dashboard.process_frame(frame, now=frame.timestamp)
        if snapshot is not None:
            if mlg_mutate is not None:
                mlg_mutate(dashboard)
            writer.append(dashboard, frame.timestamp)
    writer.close()
    return trc, mlg, baseline


class TelemetryAcceptanceTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)

    def capture(self, name="sample", **kwargs):
        return write_capture(self.root / name, **kwargs)

    def qualified(self, files):
        trc, mlg, baseline = files
        return audit.audit_capture(trc, mlg, bitrate=500000, baseline=baseline,
                                   cadence_tolerance_ms=0.001,
                                   can_capture_evidence="Synthetic fixture captures CAN notifications")

    def test_registered_identity_and_paired_capture(self):
        report = self.qualified(self.capture())
        self.assertEqual(report["transport_status"], "PASS")
        self.assertEqual(report["status"], "INCOMPLETE")
        self.assertEqual(report["target"]["identity"], [2, 9, 0x5DEF])
        self.assertEqual(report["groups"]["completed"], 30)
        self.assertEqual(set(report["groups"]["page_frames"]), set(range(11)))
        self.assertEqual(report["pairing"]["matched_snapshots"], 30)
        self.assertGreater(report["can"]["load"]["average_max_percent"], 0)

    def test_known_other_identity_does_not_pass_as_schema_verified(self):
        schema, _crc = test_can_telemetry.HistoricalSchemaTest.later_schema(self.root)
        trc, mlg, baseline = self.capture(schema_path=schema)
        report = audit.audit_capture(trc, mlg, schema_path=schema,
                                     bitrate=500000, baseline=baseline, cadence_tolerance_ms=0.001)
        self.assertGreater(report["groups"]["verified"], 0)
        self.assertEqual(report["identity"]["status"], "FAIL")
        self.assertEqual(report["status"], "FAIL")

    def test_unknown_identity_is_reported_even_when_decoder_rejects_health(self):
        def mutate(_tick, frames):
            result = []
            for frame in frames:
                data = bytearray(frame.data)
                if frame.arbitration_id == 0x6F0 and data[0] & 15 == 9 and data[1] == 3:
                    data[4:6] = bytes(2)
                result.append(replace(frame, data=bytes(data)))
            return result
        report = self.qualified(self.capture(mutate=mutate))
        self.assertEqual(report["identity"]["observed"][0]["identity"], [2, 9, 0])
        self.assertGreater(report["groups"]["schema_mismatches"], 0)
        self.assertEqual(report["status"], "FAIL")

    def test_missing_and_reordered_pages_fail(self):
        def drop(tick, frames):
            return frames if tick != 10 else [f for f in frames if not (
                f.arbitration_id == 0x6F0 and f.data[0] & 15 == 5
            )]
        def reorder(tick, frames):
            if tick == 10:
                frames[-2], frames[-3] = frames[-3], frames[-2]
            return frames
        for name, mutate in (("drop", drop), ("reorder", reorder)):
            with self.subTest(name=name):
                report = self.qualified(self.capture(name, mutate=mutate))
                self.assertEqual(report["groups"]["status"], "FAIL")
                self.assertGreater(report["groups"]["malformed_frames"], 0)

    def test_lost_whole_group_is_not_hidden_by_mlg_filtering(self):
        report = self.qualified(self.capture(ticks=[t for t in range(1, 31) if t != 10]))
        self.assertEqual(report["pairing"]["status"], "PASS")
        self.assertEqual(report["groups"]["missed_snapshots"], 1)
        self.assertEqual(report["groups"]["status"], "FAIL")

    def test_tick_wrap_is_continuous_and_restart_is_not(self):
        wrapped = self.qualified(self.capture("wrap", ticks=range(65520, 65550)))
        self.assertEqual(wrapped["groups"]["status"], "PASS")
        restarted = self.qualified(self.capture("restart", ticks=[*range(300, 315), *range(1, 16)]))
        self.assertEqual(restarted["groups"]["producer_restarts"], 1)
        self.assertEqual(restarted["groups"]["status"], "FAIL")
        event = restarted["groups"]["restart_examples"][0]
        self.assertEqual(event["last_tick"], 314)
        self.assertEqual(event["new_tick"], 1)
        self.assertGreater(event["elapsed"], 1)

    def test_counter_increment_and_wrap_are_reported(self):
        def mutate(tick, frames):
            return [replace(f, data=f.data[:6] + bytes((255 if tick < 15 else 0, 0)))
                    if f.arbitration_id == 0x6F0 and f.data[0] & 15 == 9 and f.data[1] == 3
                    else f for f in frames]
        report = self.qualified(self.capture(mutate=mutate))
        row = next(row for row in report["health_counters"]["observations"]
                   if row["name"] == "snapshot_overrun_count")
        self.assertEqual(row["increments"], 1)
        self.assertEqual(report["health_counters"]["status"], "FAIL")

    def test_warning_and_error_records_fail_the_can_section(self):
        trc, mlg, baseline = self.capture()
        lines = trc.read_text().splitlines()
        last_number = int(lines[-1].split(")")[0])
        with trc.open("a") as stream:
            stream.write(f"{last_number + 1}) 2000.0 Warng FFFFFFFF 4 00 00 00 04 BUSLIGHT\n")
            stream.write(f"{last_number + 2}) 2001.0 Error 0008 4 00 19 08 08\n")
        report = self.qualified((trc, mlg, baseline))
        self.assertEqual(report["can"]["warning_count"], 1)
        self.assertEqual(report["can"]["error_count"], 1)
        self.assertEqual(report["can"]["status"], "FAIL")

    def test_wrong_pair_and_shifted_elapsed_fail(self):
        trc, _mlg, baseline = self.capture()
        _, other_mlg, _ = self.capture("other", ticks=range(40, 70))
        report = self.qualified((trc, other_mlg, baseline))
        self.assertEqual(report["pairing"]["status"], "FAIL")
        self.assertGreater(report["pairing"]["value_mismatches"], 0)
        shifted = self.capture("shifted", time_scale=1.1)
        report = self.qualified((trc, shifted[1], baseline))
        self.assertGreater(report["pairing"]["snapshots_without_mlg"], 0)

    def test_recording_bridges_are_not_extra_snapshots(self):
        report = self.qualified(self.capture(pause_after=15))
        self.assertEqual(report["pairing"]["status"], "PASS")
        self.assertGreater(report["pairing"]["bridge_records"], 0)
        self.assertEqual(len(report["groups"]["pauses"]), 1)
        self.assertEqual(report["groups"]["status"], "FAIL")

    def test_same_ticks_and_times_do_not_hide_different_payloads(self):
        def mutate(dashboard):
            dashboard.raw["app1_raw"] = dashboard.raw["app1_raw"] + 1
        report = self.qualified(self.capture(mlg_mutate=mutate))
        self.assertEqual(report["pairing"]["time_matches"], 30)
        self.assertEqual(report["pairing"]["matched_snapshots"], 0)
        self.assertGreater(report["pairing"]["value_mismatches"], 0)
        self.assertEqual(report["pairing"]["status"], "FAIL")

    def test_wrong_absolute_start_time_fails_despite_matching_elapsed(self):
        report = self.qualified(self.capture(epoch=EPOCH + 1))
        self.assertEqual(report["pairing"]["time_matches"], 30)
        self.assertEqual(report["pairing"]["date_mismatches"], 30)
        self.assertEqual(report["pairing"]["status"], "FAIL")

    def test_nonzero_initial_counter_is_not_a_pass(self):
        def mutate(_tick, frames):
            return [replace(f, data=f.data[:6] + bytes((1, 0)))
                    if f.arbitration_id == 0x6F0 and f.data[0] & 15 == 9 and f.data[1] == 3
                    else f for f in frames]
        report = self.qualified(self.capture(mutate=mutate))
        self.assertEqual(report["health_counters"]["status"], "INCOMPLETE")

    def test_synchronization_prefix_and_group_tail_are_separate_boundaries(self):
        def mutate(tick, frames):
            return [f for f in frames if not (f.arbitration_id == 0x6F0 and (
                tick == 1 and f.data[0] & 15 < 5 or tick == 30 and f.data[0] & 15 > 8
            ))]
        report = self.qualified(self.capture(mutate=mutate))
        self.assertEqual(report["groups"]["status"], "PASS")
        self.assertEqual(report["groups"]["synchronization_prefix_frames"], 6)
        self.assertEqual(report["groups"]["incomplete_tail_pages"], 9)

    def test_cut_trc_tail_is_incomplete_not_clean_acceptance(self):
        files = self.capture()
        with files[0].open("a") as stream:
            stream.write("999) 4000.0 Rx 0160 8 01 0")
        with warnings.catch_warnings(record=True):
            report = self.qualified(files)
        self.assertEqual(report["recording"]["status"], "INCOMPLETE")
        self.assertIsNotNone(report["recording"]["excluded_trc_tail"])

    def test_no_health_context_is_incomplete(self):
        report = self.qualified(self.capture(ticks=range(1, 4)))
        self.assertEqual(report["identity"]["status"], "INCOMPLETE")
        self.assertEqual(report["health_counters"]["status"], "INCOMPLETE")

    def test_stock_periods_are_reported_without_inventing_a_reference(self):
        trc, mlg, _ = self.capture()
        report = audit.audit_capture(trc, mlg, bitrate=500000)
        self.assertEqual(report["cadence"]["status"], "NOT_ASSESSED")
        self.assertEqual(report["status"], "INCOMPLETE")
        self.assertTrue(report["stock_frames"])

    def test_cadence_drift_fails_an_explicit_tolerance(self):
        _trc, _mlg, baseline = self.capture()
        trc, mlg, _ = self.capture("slower", time_scale=1.1)
        report = self.qualified((trc, mlg, baseline))
        self.assertEqual(report["cadence"]["status"], "FAIL")

    def test_missing_baseline_id_fails_and_faulty_baseline_is_incomplete(self):
        _trc, _mlg, baseline = self.capture()
        def without_lamps(_tick, frames):
            return [frame for frame in frames if frame.arbitration_id != 0x551]
        trc, mlg, _ = self.capture("without_lamps", mutate=without_lamps)
        report = self.qualified((trc, mlg, baseline))
        self.assertEqual(report["cadence"]["status"], "FAIL")
        missing = next(row for row in report["cadence"]["identifiers"] if row["can_id"] == 0x551)
        self.assertEqual(missing["status"], "FAIL")
        lines = baseline.read_text().splitlines()
        number = int(lines[-1].split(")")[0]) + 1
        with baseline.open("a") as stream:
            stream.write(f"{number}) 2000.0 Warng FFFFFFFF 4 00 00 00 04 BUSLIGHT\n")
        report = self.qualified((trc, mlg, baseline))
        self.assertEqual(report["cadence"]["status"], "INCOMPLETE")

    def test_identical_baseline_and_invalid_tolerance_are_rejected(self):
        trc, mlg, baseline = self.capture()
        for options in ({"baseline": trc}, {"baseline": baseline, "cadence_tolerance_ms": -1},
                        {"cadence_tolerance_ms": 1}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                audit.audit_capture(trc, mlg, **options)

    def test_cli_json_and_exit_status(self):
        trc, mlg, baseline = self.capture()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = audit.main([str(trc), str(mlg), "--json", "--bitrate", "500000",
                                 "--baseline", str(baseline), "--cadence-tolerance-ms", "0.001",
                                 "--can-capture-evidence", "Synthetic fixture captures CAN notifications"])
        self.assertEqual(status, 2)
        report = json.loads(output.getvalue())
        self.assertEqual(report["transport_status"], "PASS")
        self.assertIn("0x5DEF", audit.format_report(report))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(audit.main([str(trc), str(mlg)]), 2)
            self.assertEqual(audit.main([str(trc), str(mlg) + ".missing", "--json"]), 2)
            _, wrong_mlg, _ = self.capture("wrong", ticks=range(40, 70))
            self.assertEqual(audit.main([str(trc), str(wrong_mlg), "--json"]), 1)

    def test_zero_notifications_without_capture_evidence_are_unassessed(self):
        trc, mlg, baseline = self.capture()
        result = audit.audit_capture(trc, mlg, bitrate=500000, baseline=baseline,
                                    cadence_tolerance_ms=0.001)
        self.assertEqual(result["can"]["error_count"], 0)
        self.assertEqual(result["can"]["status"], "NOT_ASSESSED")
        self.assertEqual(result["status"], "INCOMPLETE")

    def test_unix_anchor_avoids_timezone_interpretation(self):
        files = self.capture()
        source = files[0]
        result = audit.audit_capture(source, files[1], timezone="Invalid/Timezone")
        self.assertEqual(result["pairing"]["status"], "PASS")
        self.assertEqual(result["pairing"]["absolute_clock_source"], "Unix start seconds")

    def test_paired_excerpt_reacquires_rotating_context_and_keeps_unix_clock(self):
        trc, mlg, _baseline = self.capture()
        out = self.root / "excerpt"
        # Open inside tick 13's raw group, after its first pages.
        with contextlib.redirect_stdout(io.StringIO()):
            status = excerpt.main([str(mlg), str(trc), "1.1232", "1.29", "-o", str(out)])
        self.assertEqual(status, 0)
        result = audit.audit_capture(next(out.glob("*.trc")), next(out.glob("*.mlg")),
                                    timezone="Invalid/Timezone")
        self.assertEqual(result["pairing"]["status"], "PASS")
        self.assertEqual(result["pairing"]["synchronization_prefix_records"], 1)
        self.assertGreater(result["pairing"]["bootstrap_records"], 0)
        self.assertGreater(result["pairing"]["matched_snapshots"], 0)
        self.assertEqual(result["pairing"]["absolute_clock_source"], "Unix start seconds")

    def test_historical_pcan_clock_mismatch_is_a_coverage_limitation(self):
        files = self.capture(epoch=EPOCH + 1)
        source = files[0]
        source.write_text(source.read_text().replace(
            ";$FILEVERSION=1.1\n", ";$FILEVERSION=1.1\n; Generated by PCAN-View v5.3\n"
        ))
        result = self.qualified(files)
        self.assertEqual(result["pairing"]["status"], "NOT_ASSESSED")
        self.assertEqual(result["pairing"]["unshifted_comparison_status"], "FAIL")
        self.assertEqual(result["status"], "INCOMPLETE")

    def test_single_stock_frame_fails_when_the_baseline_defines_a_period(self):
        baseline = [{"can_id": 0x551, "median_period_ms": 100,
                     "p99_period_ms": 100, "maximum_period_ms": 100}]
        observed = [{"can_id": 0x551, "median_period_ms": None}]
        result = audit._cadence(observed, baseline, 1)
        self.assertEqual(result["status"], "FAIL")

    def test_a_new_id_without_a_baseline_period_is_unassessed(self):
        observed = [{"can_id": 0x551, "median_period_ms": None}]
        result = audit._cadence(observed, [], 1)
        self.assertEqual(result["status"], "NOT_ASSESSED")

    def test_pcan_view_pairing_is_unassessed_even_when_all_samples_match(self):
        for name, generator in (("hyphen", "PCAN-View v5.3"), ("space", "PCAN View")):
            with self.subTest(generator=generator):
                files = self.capture(name)
                source = files[0]
                source.write_text(source.read_text().replace(
                    ";$FILEVERSION=1.1\n", f";$FILEVERSION=1.1\n; Generated by {generator}\n"
                ))
                result = self.qualified(files)
                self.assertEqual(result["pairing"]["unshifted_comparison_status"], "PASS")
                self.assertEqual(result["pairing"]["status"], "NOT_ASSESSED")
                self.assertNotIn("10.1.1", result["pairing"]["clock_limitation"])

    def test_explicit_pcan_source_does_not_depend_on_generator_metadata(self):
        trc, mlg, _baseline = self.capture()
        result = audit.audit_capture(trc, mlg, trc_source="pcan-view")
        self.assertEqual(result["pairing"]["trc_generator"], None)
        self.assertEqual(result["pairing"]["trc_source"], "pcan-view")
        self.assertEqual(result["pairing"]["status"], "NOT_ASSESSED")
        self.assertEqual(result["pairing"]["unshifted_comparison_status"], "PASS")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = audit.main([str(trc), str(mlg), "--trc-source", "pcan-view", "--json"])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(output.getvalue())["pairing"]["trc_source"], "pcan-view")

    def test_a_trace_without_generator_or_shared_unix_anchor_is_unassessed(self):
        trc, mlg, _baseline = self.capture()
        trc.write_text("".join(line for line in trc.read_text().splitlines(keepends=True)
                               if not line.startswith("; Unix start seconds:")))
        result = audit.audit_capture(trc, mlg)
        self.assertEqual(result["pairing"]["trc_source"], "independent-or-unknown")
        self.assertEqual(result["pairing"]["status"], "NOT_ASSESSED")
