from pathlib import Path
import tomllib
import unittest

from tools.logs import tcm_shift_audit as audit


ROOT = Path(__file__).resolve().parents[3]
HARDWARE_RESULTS = ROOT / "patches" / "hardware-results.toml"
LAYOUT = ROOT / "patches" / "map-switching-layout.toml"
KEY = "transmission_interface.vehicle_2026_09_22"
SCALAR_HOOK = "rev_throttle_scalar_base"


def _lookup(registry, dotted):
    node = registry
    for part in dotted.split("."):
        node = node[part]
    return node


# The TRC captures of the record carry telemetry frames that the current
# profile does not verify, so the audit does not replay them; these tests bind
# the recorded figures to the published text and the ledgers.
class TcmShiftRecordTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with HARDWARE_RESULTS.open("rb") as source:
            cls.registry = tomllib.load(source)
        cls.result = _lookup(cls.registry, KEY)
        cls.status = cls.result["term_status"]
        cls.session = _lookup(cls.registry, cls.result["session"])
        cls.captures = {
            row["capture_name"]: row for row in _lookup(cls.registry, cls.result["capture_registry"])
        }
        with LAYOUT.open("rb") as source:
            cls.hooks = {hook["key"]: hook for hook in tomllib.load(source)["hook"]}

    def total(self, key):
        return sum(self.result[key])

    def test_record_belongs_to_the_registered_drive(self):
        result = self.result
        self.assertTrue((ROOT / result["audit_tool"]).is_file())
        self.assertEqual(result["recorded_on"], self.session["recorded_on"])
        self.assertEqual(result["image_sha256"], self.session["image_sha256"])
        self.assertEqual(result["rom_sha256"], result["image_sha256"])
        self.assertEqual(self.session["capture_registry"], result["capture_registry"])
        self.assertEqual(len(result["captures"]), len(result["capture_sha256"]))
        for name, digest in zip(result["captures"], result["capture_sha256"]):
            self.assertTrue(name.endswith(".trc"), name)
            self.assertEqual(self.captures[name]["capture_sha256"], digest, name)
        for key in audit.PER_CAPTURE_KEYS:
            self.assertEqual(len(result[key]), len(result["captures"]), key)

    def test_code_facts_match_the_stock_rom(self):
        result = self.result
        code = audit.interface_code(audit.STOCK_ROM.read_bytes())
        self.assertTrue(result["code_matches_stock"])
        for key, value in code.items():
            self.assertEqual(result[key], value, key)
        self.assertAlmostEqual(
            result["code_hold_s"], result["code_hold_passes"] * audit.SCHEDULER_PASS_S, places=9
        )

    def test_scalar_source_is_the_map_switching_redirect(self):
        hook = self.hooks[SCALAR_HOOK]
        stock = audit.STOCK_ROM.read_bytes()
        opcode = audit._u16(stock, audit.SCALAR_LOAD)
        literal = ((audit.SCALAR_LOAD + 4) & ~3) + (opcode & 0xFF) * 4
        self.assertEqual(hook["address"], literal)
        self.assertEqual(hook["width"], 4)
        self.assertEqual(hook["stock"], audit._pc_literal(stock, audit.SCALAR_LOAD))
        self.assertEqual(self.result["scalar_source"], hook["replacement"])

    def test_counts_are_consistent(self):
        result = self.result
        for index, passes in enumerate(result["pass_count"]):
            self.assertEqual(
                passes,
                result["request_identity_passes"][index] + result["request_mismatch_passes"][index],
            )
            self.assertEqual(result["tcm_group_count"][index] - 1, result["counter_pair_count"][index])
            self.assertEqual(
                result["divergence_passes"][index],
                result["divergence_in_burst_passes"][index]
                + result["divergence_in_status_passes"][index]
                + result["divergence_other_passes"][index],
            )
            self.assertEqual(
                result["event_count"][index],
                result["upshift_count"][index] + result["downshift_count"][index],
            )
            self.assertLessEqual(result["binding_equal_passes"][index], result["binding_passes"][index])
            self.assertEqual(
                len(result["binding_unequal_s"][index]),
                result["binding_passes"][index] - result["binding_equal_passes"][index],
            )
        episodes = len(result["episode_shift"])
        for key in (f"episode_{name}" for name in audit.EPISODE_KEYS):
            self.assertEqual(len(result[key]), episodes, key)
        self.assertEqual(len(result["episode_capture_index"]), episodes)
        self.assertEqual(sum(result["episode_value_frames"]), self.total("status_value_3_frames"))
        self.assertEqual(result["status_downshift_count"], episodes)
        self.assertEqual(
            result["status_downshift_count"]
            + result["same_type_downshift_count"]
            + result["other_type_downshift_count"],
            self.total("downshift_count"),
        )
        self.assertEqual(
            sum(result["episode_request_mismatch_passes"]), self.total("request_mismatch_passes")
        )
        upshifts = len(result["burst_upshift_shift"])
        for key in (f"burst_upshift_{name}" for name in audit.BURST_UPSHIFT_KEYS):
            self.assertEqual(len(result[key]), upshifts, key)
        self.assertEqual(upshifts, self.total("burst_upshift_divergence_count"))
        self.assertEqual(
            self.total("burst_count"),
            self.total("burst_upshift_count") + self.total("burst_downshift_count"),
        )
        self.assertEqual(len(result["shift_code_shifts"]), len(result["shift_code_values"]))

    def test_term_status_follows_the_figures(self):
        result = self.result
        status = self.status
        self.assertEqual(status["status_counter"], "pass")
        self.assertEqual(result["counter_step_count"], result["counter_pair_count"])
        self.assertEqual(self.total("status_bit4_count"), 0)
        self.assertEqual(status["status_value_3"], "pass")
        self.assertEqual(result["status_values"], [0, audit.STATUS_EPISODE_VALUE])
        self.assertEqual(self.total("incomplete_event_count"), 0)
        self.assertEqual(status["word_b_bound"], "pass")
        self.assertEqual(self.total("word_b_other_outside_episodes"), 0)
        self.assertEqual(self.total("request_mismatch_outside_episodes"), 0)
        self.assertEqual(self.total("request_mismatch_without_status"), 0)
        self.assertLessEqual(max(result["request_mismatch_status_lag_max_s"]), result["code_hold_s"])
        self.assertEqual(result["limited_equals_request_passes"], result["pass_count"])
        self.assertEqual(status["shift_code_floor"], "partial")
        self.assertEqual(self.total("event_shift_code_constant_count"), self.total("event_count"))
        self.assertEqual(self.total("shift_code_changes_outside_events"), 0)
        floors = [
            (index, count) for index, count in enumerate(result["episode_floor_passes"]) if count
        ]
        self.assertTrue(floors)
        for index, count in floors:
            code = result["episode_shift_code"][index]
            capture = result["episode_capture_index"][index]
            self.assertEqual(count, result["code_floor_passes"][code])
            self.assertEqual(result["episode_floor_tick_span"][index], count)
            self.assertIn(result["episode_floor_start_s"][index][0],
                          result["binding_unequal_s"][capture])
        self.assertLess(len(floors), len(result["episode_shift"]))
        self.assertEqual(status["reduction_burst"], "partial")
        self.assertEqual(self.total("bursts_outside_events"), 0)
        self.assertEqual(self.total("divergence_other_passes"), 0)
        self.assertEqual(self.total("burst_downshift_divergence_passes"), 0)
        self.assertEqual(self.total("upshift_without_burst_divergence_passes"), 0)
        self.assertEqual(status["gear_signal"], "pass")
        self.assertEqual(result["phase_equal_frames"], result["phase_frames"])
        self.assertEqual(self.total("ratio_other_gear_frames"), 0)
        self.assertEqual(result["manual_equal_frames"], result["manual_frames"])
        self.assertEqual(result["phase_gears"], list(audit.RE5R05A_RATIOS))
        self.assertEqual(result["manual_positions"], sorted(audit.MANUAL_SELECTORS.values()))
        self.assertEqual(status["kickdown"], "not_run")
        self.assertLessEqual(result["drive_downshift_app1_max"], audit.CLOSED_PEDAL_APP1)
        self.assertEqual(status["blip"], "not_observed")
        self.assertEqual(self.total("request_mismatch_above_passes"), 0)
        self.assertEqual(self.total("fuel_inhibit_passes"), 0)
        self.assertEqual(self.result["hardware_status"], "partial")

    def test_episodes_and_captures_match_the_audit(self):
        result = self.result
        drive = [
            words
            for selector, words in zip(result["episode_selector"], result["episode_word_b_during"])
            if selector in audit.DRIVE_SELECTORS
        ]
        self.assertEqual(len(drive), 1)
        self.assertEqual(len(result["captures"]), 2)
        self.assertTrue(all(len(values) == 1 for values in result["shift_code_values"]))
        selectors = set(audit.DRIVE_SELECTORS) | set(audit.MANUAL_SELECTORS)
        self.assertLessEqual(set(result["episode_selector"]), selectors)


if __name__ == "__main__":
    unittest.main()
