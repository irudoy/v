from bisect import bisect_right
import contextlib
from dataclasses import replace
import io
import json
from pathlib import Path
import tempfile
import unittest

from tools.can_dashboard import model
from tools.can_dashboard.tests.test_selected_map import feedback_frames
from tools.logs import can_telemetry, telemetry_acceptance as audit
from tools.logs.tests.test_telemetry_acceptance import write_capture


def scenario(wanted=2, *, pulses=None, actual_map=None, lose_index=False,
             lose_feedback=False, unexpected_change=False, configuration=None,
             only_group_zero=False, steady_on=False):
    """Modify the existing wire demo with a request and its independent outcomes."""
    _document, profiles = can_telemetry.load_schema()
    layout = profiles["tuning"]["_layout"]
    button_events = [(1.0, 0x20), (1.2, 0x08)]
    for tap in range(wanted):
        button_events.extend(((1.4 + tap * 0.25, 0x02), (1.5 + tap * 0.25, 0x08)))
    released = 1.6 + (wanted - 1) * 0.25
    button_events.append((released, 0x20))
    button_times = [time for time, _code in button_events]
    feedback = feedback_frames(released, wanted if pulses is None else pulses, until=4)
    feedback_times = [time for time, _code in feedback]
    target = wanted if actual_map is None else actual_map

    def mutate(tick, frames):
        time = frames[0].timestamp
        button = button_events[bisect_right(button_times, time) - 1][1]
        feedback_position = bisect_right(feedback_times, time) - 1
        display = feedback[feedback_position][1] if feedback_position >= 0 else 0x02
        if steady_on and time > released + 0.09:
            display = 0x42
        index = 0 if time < released + 0.02 else target - 1
        if unexpected_change and time > 6:
            index = 3
        result = []
        for frame in frames:
            data = bytearray(frame.data)
            if frame.arbitration_id == 0x239:
                data[3] = button
            elif frame.arbitration_id == 0x551:
                if lose_feedback and released < time < released + 1:
                    continue
                data[5] = display
            elif frame.arbitration_id == 0x6F0:
                page = data[0] & 15
                if lose_index and page in (9, 10) and data[1] == 2:
                    continue
                placed = layout.contexts.get((page, data[1])) if page in (9, 10) else None
                if placed:
                    for field, offset in placed[1]:
                        if field["name"] == "active_map_index":
                            data[offset] = index
                if configuration is not None and time > 1.4 and page == layout.dynamic.page:
                    data[1:layout.dynamic.configuration_offset] = bytes(layout.dynamic.configuration_offset - 1)
                    group = 0 if only_group_zero else tick % 2
                    data[layout.dynamic.configuration_offset] = configuration | group << 7
            result.append(replace(frame, data=bytes(data)))
        return result
    return mutate


class MapSelectionAuditTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)

    def capture(self, name="sample", ticks=range(1, 701), **options):
        return write_capture(self.root / name, ticks=ticks, mutate=scenario(**options))

    def audit(self, files, **options):
        trc, mlg, baseline = files
        return audit.audit_capture(trc, mlg, bitrate=500000, baseline=baseline,
                                   cadence_tolerance_ms=0.001,
                                   can_capture_evidence="Synthetic fixture captures CAN notifications", **options)

    def test_each_map_requires_both_pulses_and_the_verified_index(self):
        for wanted in range(1, 6):
            with self.subTest(wanted=wanted):
                result = self.audit(self.capture(str(wanted), wanted=wanted), expected_maps=[wanted])
                section = result["map_selection"]
                self.assertEqual(section["status"], "PASS", section)
                self.assertEqual(section["covered_maps"], [wanted])
                row = section["gestures"][0]
                self.assertEqual(row["after_indices"], [wanted - 1])
                self.assertEqual(row["feedback"]["pulses"], wanted)
                self.assertEqual(result["status"], "PASS")

    def test_mismatched_feedback_is_a_failure(self):
        section = self.audit(self.capture(wanted=3, pulses=2))["map_selection"]
        self.assertEqual(section["status"], "FAIL")
        self.assertEqual(section["gestures"][0]["outcome"], "FEEDBACK_MISMATCH")

    def test_actual_index_disagrees_despite_correct_pulses(self):
        section = self.audit(self.capture(wanted=3, actual_map=2))["map_selection"]
        self.assertEqual(section["status"], "FAIL")
        self.assertEqual(section["gestures"][0]["outcome"], "INDEX_MISMATCH")

    def test_no_confirmation_distinguishes_no_acceptance_from_missing_feedback(self):
        for name, actual, outcome in (("unchanged", 1, "NOT_ACCEPTED"),
                                       ("changed", 2, "FEEDBACK_MISSING")):
            with self.subTest(name=name):
                section = self.audit(self.capture(name, pulses=0, actual_map=actual))["map_selection"]
                self.assertEqual(section["gestures"][0]["outcome"], outcome)
                self.assertEqual(section["status"], "FAIL")

    def test_inferred_dashboard_map_does_not_replace_the_published_index(self):
        section = self.audit(self.capture(lose_index=True))["map_selection"]
        self.assertEqual(section["fresh_index_samples"], 0)
        self.assertEqual(section["status"], "INCOMPLETE")

    def test_missing_feedback_samples_and_cut_feedback_remain_incomplete(self):
        section = self.audit(self.capture(lose_feedback=True))["map_selection"]
        self.assertEqual(section["status"], "INCOMPLETE")
        section = self.audit(self.capture("tail", ticks=range(1, 111)))["map_selection"]
        self.assertEqual(section["status"], "INCOMPLETE")

    def test_steady_shared_display_state_is_not_counted_as_feedback(self):
        section = self.audit(self.capture(steady_on=True))["map_selection"]
        self.assertEqual(section["status"], "INCOMPLETE")
        self.assertEqual(section["gestures"][0]["feedback"]["status"], "uncountable")

    def test_invalid_index_is_not_folded_to_map_one(self):
        section = self.audit(self.capture(actual_map=7))["map_selection"]
        self.assertEqual(section["status"], "FAIL")
        self.assertEqual(section["gestures"][0]["outcome"], "INVALID_INDEX")

    def test_unrequested_index_change_and_missing_planned_map_are_visible(self):
        section = self.audit(self.capture(unexpected_change=True))["map_selection"]
        self.assertEqual(section["status"], "INCOMPLETE")
        self.assertEqual(len(section["unmatched_index_changes"]), 1)
        section = self.audit(self.capture("planned"), expected_maps=[1, 2])["map_selection"]
        self.assertEqual(section["missing_expected_maps"], [1])
        self.assertEqual(section["status"], "INCOMPLETE")

    def test_dynamic_coverage_counts_the_configuration_byte_and_both_groups(self):
        result = self.audit(self.capture(configuration=4), expected_configurations=[0, 4])
        section = result["dynamic_configurations"]
        self.assertEqual(section["status"], "PASS", section)
        config = next(row for row in section["configurations"] if row["configuration_id"] == 4)
        self.assertEqual([group["group"] for group in config["groups"]], [0, 1])
        self.assertTrue(all(group["snapshots"] > 0 for group in config["groups"]))
        self.assertEqual(result["status"], "PASS")

    def test_missing_dynamic_group_and_unobserved_planned_configuration_are_incomplete(self):
        files = self.capture(configuration=4, only_group_zero=True)
        section = self.audit(files, expected_configurations=[0, 4, 6])["dynamic_configurations"]
        self.assertEqual(section["status"], "INCOMPLETE")
        self.assertIn([4, 1], section["missing_groups"])
        self.assertIn([6, 0], section["missing_groups"])

    def test_cli_reports_the_map_table_and_complete_coverage(self):
        trc, mlg, baseline = self.capture()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = audit.main([str(trc), str(mlg), "--json", "--bitrate", "500000",
                               "--baseline", str(baseline), "--cadence-tolerance-ms", "0.001",
                               "--can-capture-evidence", "Synthetic capture", "--expect-map", "2"])
        self.assertEqual(code, 0)
        result = json.loads(output.getvalue())
        self.assertIn("CONFIRMED", audit.format_report(result))
