import csv
from pathlib import Path
import tomllib
import unittest

from tools.logs import tcm_shift_audit as audit


ROOT = Path(__file__).resolve().parents[3]
HARDWARE_RESULTS = ROOT / "patches" / "hardware-results.toml"
LAYOUT = ROOT / "patches" / "map-switching-layout.toml"
CAN = ROOT / "defs" / "JK08A.can.md"
THROTTLE_CONTROL = ROOT / "defs" / "JK08A.throttle-control.md"
LIMITERS = ROOT / "defs" / "JK08A.limiters.md"
SELECTOR = ROOT / "patches" / "map-switching-selector.md"
VARS = ROOT / "defs" / "JK08A.vars.csv"
FUNCS = ROOT / "defs" / "JK08A.funcs.csv"
FINDINGS = ROOT / "defs" / "JK08A.findings.csv"
README = ROOT / "tools" / "logs" / "README.md"
KEY = "transmission_interface.vehicle_2026_09_22"
SCALAR_HOOK = "rev_throttle_scalar_base"


def _lookup(registry, dotted):
    node = registry
    for part in dotted.split("."):
        node = node[part]
    return node


def _number(value):
    return f"{value:,}"


def _value(value):
    return f"{value:g}" if isinstance(value, float) else f"{value}"


def _range(values, scale=1):
    return f"{_value(min(values) * scale)}..{_value(max(values) * scale)}"


def _series(items):
    items = [f"{item}" for item in items]
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + ", and " + items[-1]


def _text(path):
    return " ".join(path.read_text(encoding="utf-8").split())


def _ledger(path):
    with path.open(newline="", encoding="utf-8") as source:
        return {row["addr"]: row for row in csv.DictReader(source)}


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
        cls.published = _text(CAN)
        cls.record_text = " ".join(cls.result["result"].split())
        with LAYOUT.open("rb") as source:
            cls.hooks = {hook["key"]: hook for hook in tomllib.load(source)["hook"]}
        cls.hold = f"{cls.result['code_hold_s'] * 1000:g} ms"
        cls.types = " and ".join(dict.fromkeys(cls.result["episode_shift"]))

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
        self.assertIn(f"map-switching word `{hook['replacement']:#010X}`".replace("0X", "0x"),
                      self.published)
        self.assertIn(f"`ROM16[{hook['stock']:#06X}]`".replace("0X", "0x"), self.published)

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
        for key in ("runbook_block", "q_tcm_01", "q_rl_05"):
            self.assertEqual(status[key], "partial", key)
        self.assertEqual(self.result["hardware_status"], "partial")

    def test_published_text_reads_the_record(self):
        result = self.result
        published = self.published
        drive = [
            words
            for selector, words in zip(result["episode_selector"], result["episode_word_b_during"])
            if selector in audit.DRIVE_SELECTORS
        ]
        self.assertEqual(len(drive), 1)
        first = 0
        floor_code = result["episode_shift_code"][first]
        upshifts = [
            (shift, values)
            for shift, values in zip(result["shift_code_shifts"], result["shift_code_values"])
            if shift[0] < shift[2]
        ]
        downshifts = [
            (shift, values)
            for shift, values in zip(result["shift_code_shifts"], result["shift_code_values"])
            if shift[0] > shift[2]
        ]
        codes = (
            f"The observed codes are {_series(values[0] for _, values in upshifts)} for upshifts "
            f"{upshifts[0][0]} through {upshifts[-1][0]}, "
            + _series(f"{values[0]} for {shift}" for shift, values in downshifts)
            + "."
        )
        phrases = [
            f"replays two Map 3 captures with {self.total('event_count')} shift events through "
            f"gears {_range(result['phase_gears'])} in D and in "
            f"M{min(result['manual_positions'])}..M{max(result['manual_positions'])}",
            f"The byte 4 counter advances by one modulo 16 in all "
            f"{_number(self.total('counter_step_count'))} consecutive TCM group pairs, and bit 4 "
            "stays clear.",
            f"The status field carries only {result['status_values'][0]} and "
            f"{result['status_values'][1]}. Value 3 fills {self.total('status_value_3_frames')} "
            f"frames of {len(result['episode_shift'])} episodes, all in {self.types} downshifts at "
            f"{_range(result['status_downshift_rpm_range'])} RPM, beginning "
            f"{_range(result['episode_start_delay_s'], 1000)} ms after the target change and "
            f"lasting {_range(result['episode_seconds'])} s. The "
            f"{result['same_type_downshift_count']} downshifts of the same types at "
            f"{_range(result['same_type_downshift_rpm_range'])} RPM and the "
            f"{result['other_type_downshift_count']} downshifts of other types carry none.",
            f"Word A stays {result['word_a_values'][0]}. Word B holds {result['word_b_default'][0]} "
            f"outside the episode windows; it reads {drive[0][0]} in the one D episode and restarts "
            f"at {_range(result['episode_word_b_restart'])} after each episode, with steps of "
            f"{_range([step for steps in result['episode_word_b_steps'] for step in steps])} for "
            f"{_range(result['episode_ramp_s'])} s.",
            f"The `0x180` request word equals the packed `0xFFFF19C6` in all but "
            f"{self.total('request_mismatch_passes')} of {_number(self.total('pass_count'))} "
            "passes. In those passes the packed `0xFFFF19C6` lies below the `0x180` request; they "
            f"form {self.total('request_mismatch_runs')} runs inside the episode windows and lie "
            f"at most {max(result['request_mismatch_status_lag_max_s']):g} s after the latest "
            f"value-3 frame, inside the {self.hold} hold.",
            f"`0xFFFF19C6` equals the unpacked word B in {self.total('binding_equal_passes')} of "
            f"the {self.total('binding_passes')} passes in which that word lies below the `0x180` "
            f"request. In the first episode, a {result['episode_shift'][first]} downshift at "
            f"{result['episode_rpm'][first]:g} RPM, `0xFFFF19C6` holds the code-{floor_code} "
            f"floor of {result['code_floor_values'][floor_code]} for "
            f"{result['episode_floor_passes'][first]} consecutive passes from "
            f"{result['episode_floor_start_s'][first][0]:g} s while the `0x180` request reads "
            f"{_range(result['episode_floor_request_range'][first])}.",
            f"The `0x160` limited word equals the `0x180` request in all "
            f"{_number(self.total('limited_equals_request_passes'))} passes.",
            f"The {self.total('burst_count')} bursts of `0x177` byte 4 lie inside shift events. "
            "The `0x180` actual-torque word falls below the `0x160` parallel word "
            f"{_range(result['burst_upshift_onset_lag_s'], 1000)} ms after the onset of each of "
            f"the {self.total('burst_upshift_count')} upshift bursts; the "
            f"{self.total('burst_downshift_count')} downshift bursts and the "
            f"{self.total('upshift_without_burst_count')} upshifts without a burst show no "
            f"divergence, and all {self.total('divergence_passes')} divergence passes lie in burst "
            "or episode windows.",
            f"The `0x177` byte 5 code stays constant through each of the "
            f"{self.total('event_count')} shift events and holds "
            f"`{audit.IDLE_SHIFT_CODE:#04x}` outside them. {codes}",
            f"all {_number(self.total('phase_frames'))} stable-gear TCM groups of gears "
            f"{_range(result['phase_gears'])}, where the `0x176` speed ratio matches the current "
            f"gear in {_number(self.total('ratio_matched_frames'))} of "
            f"{_number(self.total('ratio_frames'))} groups and another gear in none, and the "
            f"`0x421` manual position equals the target gear in all "
            f"{_number(self.total('manual_frames'))} manual frames.",
            f"The highest APP1 at the {result['drive_downshift_count']} downshifts in D is "
            f"{result['drive_downshift_app1_max']} raw, and the shared throttle target rises by at "
            f"most {max(result['closed_pedal_target_rise_max'])} raw in the "
            f"{self.total('closed_pedal_downshift_count')} closed-pedal downshifts.",
            f"`FUN_0002040C` decrements the hold byte with its "
            f"{audit.SCHEDULER_PASS_S * 1000:g} ms block, so the hold ends {self.hold} after the "
            "last bit-1 pass.",
            f"hold byte `0xFFFF4413` with `ROM8[0x8B07] = {result['code_hold_passes']}`",
        ]
        for phrase in phrases:
            self.assertIn(phrase, published)
        self.assertIn(f"`{KEY}`", published)
        self.assertIn(f"`{result['audit_tool']}`", published)
        self.assertEqual(len(result["captures"]), 2)
        self.assertTrue(all(len(values) == 1 for values in result["shift_code_values"]))
        selectors = set(audit.DRIVE_SELECTORS) | set(audit.MANUAL_SELECTORS)
        self.assertLessEqual(set(result["episode_selector"]), selectors)

    def test_record_result_reads_the_figures(self):
        result = self.result
        text = self.record_text
        for phrase in (
            f"in all {_number(self.total('counter_step_count'))} consecutive TCM group pairs",
            f"value 3 fills {self.total('status_value_3_frames')} frames of "
            f"{len(result['episode_shift'])} episodes, all in {self.types} downshifts at "
            f"{_range(result['status_downshift_rpm_range'])} RPM",
            f"in all but {self.total('request_mismatch_passes')} of "
            f"{_number(self.total('pass_count'))} passes, in which the packed 0xFFFF19C6 lies "
            "below the 0x180 request",
            f"they form {self.total('request_mismatch_runs')} runs inside the episode windows",
            f"at most {max(result['request_mismatch_status_lag_max_s']):g} s after the latest "
            f"value-3 frame, inside the {self.hold} hold",
            f"in {self.total('binding_equal_passes')} of the {self.total('binding_passes')} passes",
            f"for {result['episode_floor_passes'][0]} consecutive passes from "
            f"{result['episode_floor_start_s'][0][0]:g} s",
            f"all {self.total('divergence_passes')} divergence passes lie in burst or episode windows",
            f"each of the {self.total('event_count')} shift events",
            f"all {_number(self.total('phase_frames'))} stable-gear groups",
            f"in {_number(self.total('ratio_matched_frames'))} of "
            f"{_number(self.total('ratio_frames'))} groups",
            f"all {_number(self.total('manual_frames'))} manual 0x421 frames",
            f"the {result['drive_downshift_count']} downshifts in D is "
            f"{result['drive_downshift_app1_max']} raw",
        ):
            self.assertIn(phrase, text)

    def test_limiter_documents_state_the_hold_and_the_episodes(self):
        result = self.result
        episodes = f"{self.types} downshifts"
        for path, phrases in (
            (THROTTLE_CONTROL, (
                f"so bit 3 stays set for {self.hold} after the last bit-1 pass",
                f"carry that value in {episodes} at {_range(result['status_downshift_rpm_range'])} RPM",
                f"`FFFF19C6` lies below the pre-limiter request in "
                f"{self.total('request_mismatch_passes')} passes inside those episodes",
                f"for the {self.hold} hold after it, which the road captures show in {episodes}",
            )),
            (LIMITERS, (
                f"the {self.hold} hold after it",
                f"episodes in {episodes}",
            )),
            (SELECTOR, (
                f"for the {self.hold} hold after it",
                f"show such episodes in {episodes}",
            )),
        ):
            text = _text(path)
            for phrase in phrases:
                self.assertIn(phrase, text, path.name)

    def test_ledger_notes_state_the_hold_and_the_episodes(self):
        result = self.result
        vars_rows = _ledger(VARS)
        funcs_rows = _ledger(FUNCS)
        findings_rows = _ledger(FINDINGS)
        floor = (
            f"code-{result['episode_shift_code'][0]} floor of "
            f"{result['code_floor_values'][result['episode_shift_code'][0]]} for "
            f"{result['episode_floor_passes'][0]} passes"
        )
        episodes = f"{self.types} downshifts"
        for rows, addr, field, phrases in (
            (vars_rows, "ffff3a2e", "note", (
                f"value 3 appears in {len(result['episode_shift'])} episodes, all in {episodes} "
                f"at {_range(result['status_downshift_rpm_range'])} RPM",
            )),
            (vars_rows, "ffff4413", "semantics", (
                f"so it keeps bit 3 set for {result['code_hold_passes']} passes, {self.hold}",
            )),
            (vars_rows, "ffff4413", "note", (
                f"up to {max(result['request_mismatch_status_lag_max_s']):g} s after the last TCM "
                "status-3 frame",
            )),
            (vars_rows, "ffff41a6", "note", (f"stays set for {self.hold}",)),
            (vars_rows, "ffff4162", "note", (self.hold, episodes)),
            (vars_rows, "ffff3480", "note", (self.hold, episodes)),
            (vars_rows, "ffff3484", "note", (floor,)),
            (vars_rows, "ffff32ec", "note", (self.hold,)),
            (vars_rows, "ffff418f", "note", (episodes,)),
            (vars_rows, "ffff4252", "note", (episodes,)),
            (vars_rows, "ffff1064", "note", (
                f"all {_number(self.total('phase_frames'))} stable-gear TCM groups of gears "
                f"{min(result['phase_gears'])} through {max(result['phase_gears'])}",
            )),
            (funcs_rows, "00077892", "note", (self.hold, episodes, floor)),
            (funcs_rows, "000777fa", "note", (self.hold, episodes)),
            (findings_rows, "0000942c", "note", (self.hold, episodes)),
            (findings_rows, "000094b2", "note", (self.hold,)),
        ):
            for phrase in phrases:
                self.assertIn(phrase, rows[addr][field], f"{addr} {field}")

    def test_readme_states_the_tool_thresholds(self):
        readme = _text(README)
        self.assertIn("## JK08A transmission interface audit", README.read_text(encoding="utf-8"))
        drive = ", ".join(audit.DRIVE_SELECTORS.values())
        manual = sorted(audit.MANUAL_SELECTORS.values())
        for text in (
            *(f"tmp/logs-09-22/{name}" for name in self.result["captures"]),
            f"one `0x177` frame within {audit.TCM_GROUP_MS:g} ms",
            f"whose frames lie at most {audit.EPISODE_GAP_S:g} s apart",
            f"when {audit.RAMP_SETTLE_FRAMES} consecutive frames carry its default",
            f"runs from {audit.EPISODE_MARGIN_S[0]:g} s before the first value-3 frame to "
            f"{audit.EPISODE_MARGIN_S[1]:g} s after word B settles",
            f"ends at the first gap of more than {audit.BURST_ZERO_GAP} zero frame",
            f"runs from {audit.BURST_MARGIN_S[0]:g} s before its first to "
            f"{audit.BURST_MARGIN_S[1]:g} s after its last nonzero frame",
            f"come from the {audit.BURST_REFERENCE_S:g} s before it",
            f"to {audit.DIVERGENCE_TAIL_S:g} s after its shift window closes",
            f"when the last {audit.BINDING_FRAMES} TCM groups at most "
            f"{audit.BINDING_WINDOW_S:g} s before it",
            f"form one run while they lie at most {audit.BINDING_WINDOW_S:g} s apart",
            f"in {drive}, or M{manual[0]}..M{manual[-1]}",
            f"whose `0x177` byte 5 holds `{audit.IDLE_SHIFT_CODE:#04x}`",
            f"within {100 * audit.RATIO_TOLERANCE:g} percent of the inverse RE5R05A ratio",
            f"turbine speed {audit.RATIO_MIN_TURBINE} or more and output speed "
            f"{audit.RATIO_MIN_OUTPUT} or more raw",
            f"APP1 stays at {audit.CLOSED_PEDAL_APP1} raw or less",
        ):
            self.assertIn(text, readme)


if __name__ == "__main__":
    unittest.main()
