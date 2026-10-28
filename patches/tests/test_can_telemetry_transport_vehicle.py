from pathlib import Path
import json
import tomllib
import unittest

from tools.logs import peak_trc_audit


ROOT = Path(__file__).resolve().parents[2]
HARDWARE_RESULTS = ROOT / "patches" / "hardware-results.toml"
SCHEMA = ROOT / "patches" / "can-telemetry-schema.json"
TELEMETRY = ROOT / "patches" / "can-telemetry.md"
SESSION_KEY = "can_telemetry.schema2_profile5_drive_2026_09_22"
KEY = "can_telemetry.schema2_transport_2026_09_22"
PREVIOUS_SESSION_KEY = "can_telemetry.schema2_profile5_drive_2026_09_21"
# The capture runs once per 204800 peripheral clocks at the measured 20 MHz.
SNAPSHOT_RATE_HZ = 20_000_000 / 204_800
CONTROL_TERMS = (
    "stop_start_control",
    "invalid_control_rejection",
    "override_priority",
    "mailbox_31_after_recovery",
)


def _normalized(path):
    return " ".join(path.read_text(encoding="utf-8").split())


def _entry(registry, dotted):
    section, name = dotted.split(".")
    return registry[section][name]


def _recorded_profile_ids(node):
    """The profile IDs that the records of a registry node carry."""
    if isinstance(node, dict):
        found = {node["profile_id"]} if "profile_id" in node else set()
        for value in node.values():
            found |= _recorded_profile_ids(value)
        return found
    if isinstance(node, list):
        return set().union(*map(_recorded_profile_ids, node))
    return set()


def _percent_range(low, high):
    return f"`{low:.3f}%..{high:.3f}%`"


class CanTelemetryTransportVehicleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with HARDWARE_RESULTS.open("rb") as source:
            cls.registry = tomllib.load(source)
        cls.session = _entry(cls.registry, SESSION_KEY)
        cls.result = _entry(cls.registry, KEY)
        cls.captures = _entry(cls.registry, cls.session["capture_registry"])
        cls.by_name = {row["capture_name"]: row for row in cls.captures}
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        (cls.current_profile_id,) = (
            row["id"] for row in schema["profiles"] if row["name"] == "tuning"
        )
        cls.published = _normalized(TELEMETRY)

    def test_session_carries_the_tuning_profile_of_the_same_image(self):
        session = self.session
        previous = _entry(self.registry, PREVIOUS_SESSION_KEY)
        self.assertEqual(session["image_sha256"], previous["image_sha256"])
        self.assertEqual(session["profile_id"], previous["profile_id"])
        self.assertEqual(session["profile_crc16"], previous["profile_crc16"])
        self.assertEqual(len(self.by_name), len(self.captures))
        self.assertEqual(
            session["record_count_total"],
            sum(row["record_count"] for row in self.captures),
        )
        self.assertLess(session["identity_record_count"], session["record_count_total"])
        traces = [row for row in self.captures if row["capture_name"].endswith(".trc")]
        for row in traces:
            self.assertIn("converted_mlg_sha256", row)
        self.assertEqual(session["trc_error_count"], 0)
        self.assertEqual(session["trc_warning_count"], 0)
        self.assertEqual(session["snapshot_overrun_count_max"], 0)
        self.assertEqual(session["tx_abort_count_max"], 0)
        self.assertIn(
            f"The road session of {session['recorded_on']} in registry entry "
            f"`{SESSION_KEY}` carried the same profile",
            self.published,
        )

    def test_transport_captures_are_the_session_traces(self):
        result = self.result
        self.assertEqual(result["session"], SESSION_KEY)
        self.assertEqual(result["recorded_on"], self.session["recorded_on"])
        self.assertEqual(result["image_sha256"], self.session["image_sha256"])
        self.assertTrue((ROOT / result["audit_tool"]).is_file())
        traces = [
            row["capture_name"] for row in self.captures
            if row["capture_name"].endswith(".trc")
        ]
        self.assertEqual([row["capture_name"] for row in result["captures"]], traces)
        pages = result["page_count"]
        for row in result["captures"]:
            with self.subTest(capture=row["capture_name"]):
                session_row = self.by_name[row["capture_name"]]
                self.assertEqual(row["complete_group_count"], session_row["record_count"])
                self.assertLess(row["truncated_final_group_page_count"], pages)
                self.assertEqual(
                    row["telemetry_frame_count"],
                    row["complete_group_count"] * pages
                    + row["truncated_final_group_page_count"],
                )
                self.assertEqual(row["tick_step_values"], [1])
                for name in (
                    "tx_count",
                    "rtr_count",
                    "warning_record_count",
                    "error_record_count",
                    "extended_id_count",
                ):
                    self.assertEqual(row[name], 0)
                self.assertEqual(
                    row["standard_id_count"], result["stock_identifier_count"] + 1
                )
        self.assertEqual(self.session["trc_error_count"], 0)

    def test_planning_bounds_follow_the_frame_length_and_page_count(self):
        result = self.result
        frame = peak_trc_audit.Frame(
            number=1, offset_ms=0.0, direction="Rx",
            can_id=result["candidate_id"], data=bytes(8),
        )
        frames_per_second = result["page_count"] * SNAPSHOT_RATE_HZ
        theory = [
            round(100 * frames_per_second * bits / result["nominal_bitrate"], 3)
            for bits in peak_trc_audit.frame_bit_bounds(frame)
        ]
        self.assertEqual(theory, result["stream_theoretical_load_percent"])
        passive = {row["capture_name"] for row in self.registry["passive_can"]["captures"]}
        self.assertIn(result["planning_baseline_capture"], passive)
        self.assertLessEqual(set(result["period_baseline_captures"]), passive)
        for baseline, planned in (
            ("planning_baseline_average_bus_load_percent", "planning_average_bus_load_percent"),
            ("planning_baseline_peak_100ms_bus_load_percent", "planning_peak_100ms_bus_load_percent"),
        ):
            self.assertEqual(
                [round(a + b, 3) for a, b in zip(result[baseline], theory)],
                result[planned],
            )
        for text in (
            f"add {_percent_range(*theory)} theoretical load",
            f"was {_percent_range(*result['planning_baseline_average_bus_load_percent'])}",
            f"planning average of {_percent_range(*result['planning_average_bus_load_percent'])}",
            f"stream is {_percent_range(*result['planning_peak_100ms_bus_load_percent'])}",
        ):
            self.assertIn(text, self.published)

    def test_measured_load_stays_inside_the_planning_bounds(self):
        result = self.result
        rows = result["captures"]
        average = [
            min(row["average_bus_load_percent"][0] for row in rows),
            max(row["average_bus_load_percent"][1] for row in rows),
        ]
        peak = [
            min(row["peak_100ms_bus_load_percent"][0] for row in rows),
            max(row["peak_100ms_bus_load_percent"][1] for row in rows),
        ]
        self.assertLessEqual(average[1], result["planning_average_bus_load_percent"][1])
        self.assertLessEqual(peak[1], result["planning_peak_100ms_bus_load_percent"][1])
        for row in rows:
            for name in (
                "average_bus_load_percent",
                "peak_100ms_bus_load_percent",
                "peak_1000ms_bus_load_percent",
            ):
                low, high = row[name]
                self.assertLess(low, high)
            self.assertLessEqual(
                row["average_bus_load_percent"][1], row["peak_1000ms_bus_load_percent"][1]
            )
            self.assertLessEqual(
                row["peak_1000ms_bus_load_percent"][1], row["peak_100ms_bus_load_percent"][1]
            )
        span = sum(row["observed_span_ms"] for row in rows) / 1000
        self.assertEqual(result["term_status"]["whole_bus_load"], "pass")
        for text in (
            f"three moving TRC captures of the {result['recorded_on']} road session, "
            f"{span:.1f} s in total",
            f"the whole-bus average lies within {_percent_range(*average)}",
            f"the highest 100 ms window within {_percent_range(*peak)}",
            "the captures contain no error, warning, or remote frame.",
        ):
            self.assertIn(text, self.published)

    def test_stock_cadence_and_group_timing_are_published(self):
        result = self.result
        rows = result["captures"]
        self.assertEqual(len(result["startup_only_identifiers"]), 5)
        self.assertEqual(result["dashboard_state_median_period_ms"], 102.4)
        self.assertLessEqual(
            max(result["dashboard_state_p99_period_ms"]),
            result["dashboard_state_baseline_p99_period_ms_max"],
        )
        self.assertLessEqual(
            max(result["dashboard_state_maximum_period_ms"]),
            result["dashboard_state_baseline_maximum_period_ms_max"],
        )
        self.assertEqual(len(result["dashboard_state_p99_period_ms"]), len(rows))
        self.assertEqual(len(result["dashboard_state_maximum_period_ms"]), len(rows))
        self.assertEqual(result["term_status"]["stock_frame_cadence"], "pass")
        self.assertEqual(result["term_status"]["group_continuity"], "pass")
        medians = [row["page_0_to_10_median_ms"] for row in rows]
        longest = max(row["page_0_to_10_max_ms"] for row in rows)
        for row in rows:
            self.assertLessEqual(row["page_0_to_10_median_ms"], row["page_0_to_10_p99_ms"])
            self.assertLessEqual(row["page_0_to_10_p99_ms"], row["page_0_to_10_max_ms"])
            self.assertLess(row["page_0_to_10_max_ms"], 1000 / SNAPSHOT_RATE_HZ)
            self.assertLess(row["group_rate_hz"], SNAPSHOT_RATE_HZ)
        for text in (
            f"Each of the {result['stock_identifier_count']} stock identifiers of the "
            "stationary baselines keeps its median period within "
            f"{result['median_period_max_deviation_ms']} ms",
            f"`0x{result['dashboard_state_can_id']:03X}` at "
            f"`{result['dashboard_state_median_period_ms']} ms`",
            f"longest interval within {result['maximum_period_max_increase_ms']} ms "
            "of the baseline maximum",
            f"page 10 follows page 0 after {min(medians)}..{max(medians)} ms in the "
            f"median and at most {longest} ms",
        ):
            self.assertIn(text, self.published)

    def test_control_terms_stay_untested(self):
        status = self.result["term_status"]
        for term in CONTROL_TERMS:
            self.assertEqual(status[term], "untested")
        self.assertEqual(status["bus_error_records"], "pass")
        self.assertIn("no frame was transmitted", self.result["evidence_boundary"])
        # PCAN-View stores no trace of its error-frame setting in the TRC file.
        self.assertEqual(self.result["error_frame_recording"], "enabled")
        self.assertIn(
            "error-frame recording was enabled for all three captures by operator report",
            self.result["evidence_boundary"],
        )
        self.assertEqual(len(self.result["captures"]), 3)
        for row in self.result["captures"]:
            self.assertEqual(row["error_record_count"], 0)
            self.assertEqual(row["warning_record_count"], 0)
        self.assertIn(
            "With PCAN-View error-frame recording enabled, the captures contain no "
            "error, warning, or remote frame.",
            self.published,
        )
        self.assertIn(
            "On the vehicle they remain untested: registry entry "
            f"`{KEY}` records that no capture carries a control frame.",
            self.published,
        )
        self.assertIn(
            f"The TRC captures of registry entry `{KEY}` measure the last criterion "
            f"for profile {self.session['profile_id']} on the target vehicle; "
            "the current profile has no target-vehicle capture.",
            self.published,
        )
        self.assertNotIn(
            self.current_profile_id, _recorded_profile_ids(self.registry)
        )


if __name__ == "__main__":
    unittest.main()
