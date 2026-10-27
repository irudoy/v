from pathlib import Path
import tomllib
import unittest

import pytest

from tools.logs import ltft_publication_audit as audit
from tools.mapkit import rom as romkit


ROOT = Path(__file__).resolve().parents[3]
HARDWARE_RESULTS = ROOT / "patches" / "hardware-results.toml"
FUEL = ROOT / "defs" / "JK08A.fuel.md"
TELEMETRY = ROOT / "defs" / "JK08A.tuning-telemetry.md"
PROFILE = ROOT / "patches" / "can-telemetry-profile.toml"
LOGS = ROOT / "tmp" / "logs-09-22"
IMAGE = ROOT / "tmp" / "1JK08A-tune-v3-1.bin"
RAM_WINDOW = 0xFFFF128C
KEY = "can_telemetry.ltft_learning_2026_09_22"
SESSION = "schema2_profile5_drive_2026_09_22"
CAPTURES = "schema2_profile5_captures_2026_09_22"
TERM_VALUES = {"pass", "fail", "untested", "not_streamed", "not_observed", "unresolved"}
SUMMED = (
    "record_count",
    "unverified_record_count",
    "snapshot_count",
    "learned_b1_sample_count",
    "learned_b1_neutral_count",
    "learned_b1_upper_bound_count",
    "learned_b1_lower_bound_count",
    "adjustment_b1_sample_count",
    "adjustment_b1_neutral_count",
    "published_b1_sample_count",
    "published_b1_neutral_count",
    "published_b1_upper_bound_count",
    "published_b2_sample_count",
    "published_b2_neutral_count",
    "published_b2_upper_bound_count",
    "relation_bracketed_count",
    "relation_exact_count",
    "relation_nonneutral_exact_count",
    "relation_forced_neutral_count",
    "relation_other_count",
    "relation_transition_count",
    "relation_transition_bracket_count",
    "relation_unbracketed_count",
    "learned_pair_count",
    "learned_change_count",
    "in_visit_change_count",
    "in_visit_update_count",
    "in_visit_over_bound_count",
    "row_0_update_count",
    "update_stft_sign_agreement_count",
    "update_stft_neutral_count",
    "gear_p_learned_pair_count",
    "gear_p_learned_change_count",
)
PER_CAPTURE = {
    "capture_learned_change_count": "learned_change_count",
    "capture_in_visit_update_count": "in_visit_update_count",
    "capture_update_bound": "update_bound",
}
CRUISE = (
    "longest_gear_d_seconds",
    "speed_band_seconds",
    "speed_band_interval_count",
    "speed_band_longest_seconds",
    "gear_d_full_fuel_inhibit_interval_count",
    "warm_closed_loop_seconds",
    "relation_nonneutral_exact_count",
    "learned_change_count",
    "in_visit_update_count",
    "update_stft_sign_agreement_count",
    "final_gear_p_seconds",
    "final_gear_p_stft_b1_median_raw",
    "gear_p_learned_pair_count",
    "gear_p_learned_change_count",
)
COLD = {
    "cold_warm_elapsed_seconds": "warm_elapsed_seconds",
    "cold_warm_capture_seconds": "warm_capture_seconds",
    "cold_warm_gear_d_seconds": "warm_gear_d_seconds",
    "cold_warm_closed_loop_seconds": "warm_closed_loop_seconds",
    "cold_warm_fueled_above_maf_gate_count": "warm_fueled_above_maf_gate_count",
    "cold_learned_pair_count": "learned_pair_count",
    "cold_learned_change_count": "learned_change_count",
}
# The replayed selector cell and the MAF summary gate take engine-speed
# coordinate 0xFFFF11F4, which the recorded profile published. The converted
# recordings take engine speed from stock frame 0x180, which can trail that
# coordinate, so the figures these enter remain the record.
RECORD_ONLY = {
    "in_visit_change_count",
    "in_visit_update_count",
    "in_visit_over_bound_count",
    "row_0_update_count",
    "update_stft_sign_agreement_count",
    "update_stft_neutral_count",
    "capture_in_visit_update_count",
    "cruise_in_visit_update_count",
    "cruise_update_stft_sign_agreement_count",
    "cold_warm_fueled_above_maf_gate_count",
}


def _u16(data, address):
    return int.from_bytes(data[address : address + 2], "big")


def _u32(data, address):
    return int.from_bytes(data[address : address + 4], "big")


def _mov_l_literal(data, address):
    """Return the literal a PC-relative MOV.L at address loads."""
    opcode = _u16(data, address)
    assert opcode >> 12 == 0xD, hex(opcode)
    return _u32(data, ((address + 4) & ~3) + (opcode & 0xFF) * 4)


def _mov_w_literal(data, address):
    """Return the positive word a PC-relative MOV.W at address loads."""
    opcode = _u16(data, address)
    assert opcode >> 12 == 0x9, hex(opcode)
    word = _u16(data, address + 4 + (opcode & 0xFF) * 2)
    assert word < 0x8000, hex(word)
    return word


def _conditional_target(data, address, opcode_high):
    """Return the target of the BT (0x89) or BF (0x8B) at address."""
    opcode = _u16(data, address)
    assert opcode >> 8 == opcode_high, hex(opcode)
    displacement = opcode & 0xFF
    if displacement & 0x80:
        displacement -= 0x100
    return address + 4 + displacement * 2


class LtftLearningRecordTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with HARDWARE_RESULTS.open("rb") as source:
            cls.registry = tomllib.load(source)
        section, name = KEY.split(".")
        cls.result = cls.registry[section][name]
        cls.session = cls.registry[section][SESSION]
        cls.captures = [row["capture_name"] for row in cls.registry[section][CAPTURES]]
        cls.published = " ".join(FUEL.read_text(encoding="utf-8").split())

    def test_record_belongs_to_the_registered_drive(self):
        result = self.result
        self.assertTrue((ROOT / result["tool"]).is_file())
        self.assertEqual(result["recorded_on"], self.session["recorded_on"])
        self.assertEqual(result["image_sha256"], self.session["image_sha256"])
        self.assertEqual(result["session"], f"can_telemetry.{SESSION}")
        self.assertEqual(result["capture_registry"], f"can_telemetry.{CAPTURES}")
        self.assertEqual(result["record_count"], self.session["record_count_total"])
        self.assertEqual(result["snapshot_count"], self.session["identity_record_count"])
        self.assertEqual(
            result["unverified_record_count"],
            result["record_count"] - result["snapshot_count"],
        )
        for name in ("capture_learned_change_count", "capture_in_visit_update_count",
                     "capture_update_bound"):
            with self.subTest(name=name):
                self.assertEqual(len(result[name]), len(self.captures))
        self.assertEqual(sum(result["capture_learned_change_count"]),
                         result["learned_change_count"])
        self.assertEqual(sum(result["capture_in_visit_update_count"]),
                         result["in_visit_update_count"])
        cruise = self.captures.index(result["cruise_capture"])
        cold = self.captures.index(result["cold_capture"])
        self.assertEqual(result["capture_learned_change_count"][cruise],
                         result["cruise_learned_change_count"])
        self.assertEqual(result["capture_in_visit_update_count"][cruise],
                         result["cruise_in_visit_update_count"])
        self.assertEqual(result["capture_learned_change_count"][cold],
                         result["cold_learned_change_count"])

    def test_calibration_matches_the_rom_the_tool_reads(self):
        result = self.result
        calibration = audit.load_calibration()
        self.assertEqual(
            result["publication_clamp_percent"],
            [calibration.publication_low >> 8, calibration.publication_high >> 8],
        )
        self.assertEqual(
            result["cell_bounds_percent"],
            [calibration.cell_low >> 8, calibration.cell_high >> 8],
        )
        self.assertEqual(result["update_gains"], list(calibration.gains))
        self.assertEqual(result["first_visit_gain"], calibration.first_visit_gain)
        self.assertEqual(result["coolant_threshold_raw"], calibration.coolant_threshold_raw)
        self.assertEqual(result["maf_summary_rpm_gate_raw"], audit.MAF_SUMMARY_RPM_RAW)
        self.assertEqual(max(result["capture_update_bound"]),
                         (0x1900 * max(result["update_gains"])) >> 8)

    def test_counts_are_consistent(self):
        result = self.result
        self.assertEqual(result["relation_exact_count"], result["relation_bracketed_count"])
        self.assertEqual(result["relation_forced_neutral_count"], 0)
        self.assertEqual(result["relation_other_count"], 0)
        self.assertLessEqual(result["relation_nonneutral_exact_count"],
                             result["relation_exact_count"])
        self.assertLessEqual(result["relation_transition_bracket_count"],
                             result["relation_transition_count"])
        # Each tag-2 refresh lies inside exactly one pair of tag-0 refreshes.
        self.assertEqual(
            result["relation_bracketed_count"] + result["relation_transition_count"],
            result["learned_pair_count"],
        )
        # With a constant adjustment term a bracket differs only by the learned word.
        self.assertEqual(result["adjustment_b1_neutral_count"],
                         result["adjustment_b1_sample_count"])
        self.assertEqual(result["relation_transition_count"], result["learned_change_count"])
        self.assertEqual(
            result["in_visit_update_count"] + result["in_visit_over_bound_count"],
            result["in_visit_change_count"],
        )
        self.assertLessEqual(result["in_visit_change_count"], result["learned_change_count"])
        self.assertLessEqual(
            result["update_stft_sign_agreement_count"] + result["update_stft_neutral_count"],
            result["in_visit_update_count"],
        )
        self.assertLessEqual(result["row_0_update_count"], result["in_visit_update_count"])
        self.assertEqual(result["published_lower_bound_count"], [0, 0])
        self.assertLessEqual(result["cruise_gear_p_learned_pair_count"],
                             result["gear_p_learned_pair_count"])
        self.assertLessEqual(result["cruise_speed_band_longest_seconds"],
                             result["cruise_speed_band_seconds"])
        self.assertLessEqual(result["cruise_speed_band_seconds"],
                             result["cruise_longest_gear_d_seconds"])
        self.assertLessEqual(result["cold_warm_gear_d_seconds"],
                             result["cold_warm_capture_seconds"])
        self.assertLessEqual(result["cold_warm_closed_loop_seconds"],
                             result["cold_warm_capture_seconds"])

    def test_term_status_follows_the_figures(self):
        result = self.result
        status = result["term_status"]
        self.assertLessEqual(set(status.values()), TERM_VALUES)
        self.assertEqual(status["publication_relation"], "pass")
        self.assertGreater(result["relation_nonneutral_exact_count"], 0)
        self.assertEqual(status["bank_1_learning"], "pass")
        self.assertGreater(result["in_visit_update_count"], 0)
        self.assertEqual(status["adjustment_term"], "untested")
        self.assertEqual(status["neutralizing_conditions"], "untested")
        planned_low, _planned_high = result["planned_cruise_seconds"]
        self.assertEqual(status["planned_cruise_duration"], "fail")
        self.assertLess(result["cruise_speed_band_seconds"], planned_low)
        self.assertEqual(status["planned_idle_duration"], "pass")
        self.assertGreaterEqual(result["cruise_final_gear_p_seconds"],
                                result["planned_idle_seconds"])
        self.assertEqual(status["idle_learning"], "not_observed")
        self.assertEqual(result["gear_p_learned_change_count"], 0)
        self.assertEqual(result["cruise_gear_p_learned_change_count"], 0)
        self.assertEqual(status["warm_cold_start_learning"], "not_observed")
        self.assertEqual(result["cold_learned_change_count"], 0)
        self.assertGreater(result["cold_warm_capture_seconds"], 0)
        self.assertEqual(status["cruise_map_1"], "pass")
        self.assertEqual(result["cruise_map_slot"], 1)

    def test_published_figures_match_the_registry(self):
        result = self.result
        text = self.published
        non_neutral_updates = (
            result["in_visit_update_count"] - result["update_stft_neutral_count"]
        )
        for phrase in (
            f"`{KEY}`",
            f"`{result['tool']}`",
            f"all {result['relation_bracketed_count']:,} tag-2 refreshes whose "
            "bracketing tag-0 refreshes agree",
            f"{result['relation_nonneutral_exact_count']:,} of them with a "
            "non-neutral prediction",
            f"stays `0x6400` in all {result['adjustment_b1_sample_count']:,} samples",
            f"The learned word changes {result['learned_change_count']:,} times",
            f"Of the {result['in_visit_change_count']:,} changes inside one replayed "
            f"selector cell, {result['in_visit_update_count']:,} stay within the "
            f"single-update bound, and {result['update_stft_sign_agreement_count']:,} "
            f"of the {non_neutral_updates:,} with non-neutral STFT follow its sign",
            f"No learned change occurs in the {result['gear_p_learned_pair_count']:,} "
            f"tag-0 pairs in P or in the {result['cold_warm_capture_seconds']:.3f} s",
            f"zero in {result['cold_warm_fueled_above_maf_gate_count']:,} snapshots",
            f"the `0x{result['maf_summary_rpm_gate_raw']:X}` gate of `FUN 0004F736`",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    @pytest.mark.slow
    @unittest.skipUnless(LOGS.is_dir() and IMAGE.is_file(), "road captures are local and untracked")
    def test_audit_reproduces_the_record(self):
        result = self.result
        rows = self.registry["can_telemetry"][CAPTURES]
        # Each capture is audited through its MLG in the current profile layout.
        logs = [LOGS / (Path(row["capture_name"]).stem + ".mlg") for row in rows]
        missing = [path.name for path in logs if not path.is_file()]
        if missing:
            self.skipTest(f"missing captures: {', '.join(missing)}")
        calibration = audit.load_calibration(image=IMAGE)
        self.assertEqual(calibration.image_sha256, result["image_sha256"])
        outputs = {}
        for row, path in zip(rows, logs):
            output = audit.audit(path, calibration)
            self.assertEqual(
                output["capture_sha256"], row["converted_mlg_sha256"], row["capture_name"]
            )
            outputs[row["capture_name"]] = output
        for key in SUMMED:
            if key in RECORD_ONLY:
                continue
            with self.subTest(key=key):
                self.assertEqual(sum(output[key] for output in outputs.values()), result[key])
        self.assertEqual(
            [
                sum(output[f"published_b{bank}_lower_bound_count"] for output in outputs.values())
                for bank in (1, 2)
            ],
            result["published_lower_bound_count"],
        )
        for key, name in PER_CAPTURE.items():
            if key in RECORD_ONLY:
                continue
            with self.subTest(key=key):
                self.assertEqual([output[name] for output in outputs.values()], result[key])
        self.assertEqual(
            round(sum(output["warm_gear_p_seconds"] for output in outputs.values()), 3),
            result["warm_gear_p_seconds"],
        )
        cruise = outputs[result["cruise_capture"]]
        for name in CRUISE:
            if f"cruise_{name}" in RECORD_ONLY:
                continue
            with self.subTest(key=f"cruise_{name}"):
                self.assertEqual(cruise[name], result[f"cruise_{name}"])
        cold = outputs[result["cold_capture"]]
        for key, name in COLD.items():
            if key in RECORD_ONLY:
                continue
            with self.subTest(key=key):
                self.assertEqual(cold[name], result[key])


class LtftPublisherCodeTest(unittest.TestCase):
    """Bind the published FUN 00057B26 and FUN 0005796C facts to the stock ROM."""

    @classmethod
    def setUpClass(cls):
        cls.rom = romkit.load("JK08A").data
        cls.published = " ".join(FUEL.read_text(encoding="utf-8").split())

    def test_summands_and_limiting_gates(self):
        rom = self.rom
        self.assertEqual(_mov_l_literal(rom, 0x57B2E), 0xFFFF2306)
        self.assertEqual(_mov_l_literal(rom, 0x57B30), 0xFFFF5648)
        # mov #22,r0; mov.b @(r0,r2),r6 with r2 = 0xFFFF22F8.
        self.assertEqual(_u16(rom, 0x57B3C), 0xE016)
        self.assertEqual(_mov_l_literal(rom, 0x57B40) + 22, 0xFFFF230E)
        self.assertEqual(_u16(rom, 0x57B4C), 0x062C)
        # mov r4,r2; add #1,r2; tst r2,r6; bf skips limiting when the bit is set.
        self.assertEqual(_u16(rom, 0x57B4E), 0x6243)
        self.assertEqual(_u16(rom, 0x57B50), 0x7201)
        self.assertEqual(_u16(rom, 0x57B54), 0x2628)
        self.assertEqual(_conditional_target(rom, 0x57B56, 0x8B), 0x57BEA)
        # extu.w of 0xFFFF15FC, sign-extending load of 0xFFFF15FE, cmp/gt, bf.
        self.assertEqual(_mov_l_literal(rom, 0x57B58), RAM_WINDOW)
        self.assertEqual(RAM_WINDOW + _mov_w_literal(rom, 0x57B5A), 0xFFFF15FC)
        self.assertEqual(RAM_WINDOW + _mov_w_literal(rom, 0x57B5E), 0xFFFF15FE)
        self.assertEqual(_u16(rom, 0x57B60), 0x622D)
        self.assertEqual(_u16(rom, 0x57B62), 0x065D)
        self.assertEqual(_u16(rom, 0x57B64), 0x3267)
        self.assertEqual(_conditional_target(rom, 0x57B66, 0x8B), 0x57BEA)
        # Clamp bounds: cmp/hs against ROM8[0x8E5B] << 8, cmp/hi against 0x8E5A.
        self.assertEqual(_mov_l_literal(rom, 0x57B68), audit.PUBLICATION_LOW_ADDRESS)
        self.assertEqual(_u16(rom, 0x57B72), 0x3E22)
        self.assertEqual(_mov_l_literal(rom, 0x57BD6), audit.PUBLICATION_HIGH_ADDRESS)
        self.assertEqual(_u16(rom, 0x57BE0), 0x3526)
        for phrase in (
            "`uint16[0xFFFF15FC] <= int16[0xFFFF15FE]`",
            "`extu.w` at `0x57B60`",
            "`cmp/gt` at `0x57B64`",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.published)

    def test_neutralizing_conditions(self):
        rom = self.rom
        # FUN 00025E20(0x0129) != 0.
        self.assertEqual(_mov_l_literal(rom, 0x57BEA), 0x25E20)
        self.assertEqual(_mov_w_literal(rom, 0x57BEC), 0x0129)
        self.assertEqual(_u16(rom, 0x57BF2), 0x2008)
        self.assertEqual(_conditional_target(rom, 0x57BF4, 0x8B), 0x57C22)
        # uint8[0xFFFF41B5].bit0 set.
        self.assertEqual(_mov_l_literal(rom, 0x57BF6) + 12, 0xFFFF41B5)
        self.assertEqual(_u16(rom, 0x57BF8), 0x846C)
        self.assertEqual(_u16(rom, 0x57BFA), 0xC801)
        self.assertEqual(_conditional_target(rom, 0x57BFC, 0x8B), 0x57C22)
        # uint8[0xFFFF41FA].bit0 set: bt skips the condition while it is clear.
        self.assertEqual(_u16(rom, 0x57BFE), 0xE051)
        self.assertEqual(_u16(rom, 0x57C00), 0x006C)
        self.assertEqual(_mov_l_literal(rom, 0x57BF6) + 0x51, 0xFFFF41FA)
        self.assertEqual(_u16(rom, 0x57C02), 0xC801)
        self.assertEqual(_conditional_target(rom, 0x57C04, 0x89), 0x57C10)
        # ... and uint8[0xFFFF248B].bit1 set.
        self.assertEqual(_mov_l_literal(rom, 0x57C06) + 27, 0xFFFF248B)
        self.assertEqual(_u16(rom, 0x57C08), 0xE01B)
        self.assertEqual(_u16(rom, 0x57C0A), 0x006C)
        self.assertEqual(_u16(rom, 0x57C0C), 0xC802)
        self.assertEqual(_conditional_target(rom, 0x57C0E, 0x8B), 0x57C22)
        # uint8[0xFFFF249C].bit6 set and uint8[0xFFFF248B].bit0 set.
        self.assertEqual(_mov_l_literal(rom, 0x57C10) + 44, 0xFFFF249C)
        self.assertEqual(_u16(rom, 0x57C12), 0xE02C)
        self.assertEqual(_u16(rom, 0x57C14), 0x006C)
        self.assertEqual(_u16(rom, 0x57C16), 0xC840)
        self.assertEqual(_conditional_target(rom, 0x57C18, 0x89), 0x57C26)
        self.assertEqual(_u16(rom, 0x57C1A), 0xE01B)
        self.assertEqual(_u16(rom, 0x57C1C), 0x006C)
        self.assertEqual(_u16(rom, 0x57C1E), 0xC801)
        self.assertEqual(_conditional_target(rom, 0x57C20, 0x89), 0x57C26)
        # mov #100,r14; shll8 r14 forms 0x6400, stored to 0xFFFF2302 + 2*b.
        self.assertEqual(_u16(rom, 0x57C22), 0xEE64)
        self.assertEqual(_u16(rom, 0x57C24), 0x4E18)
        self.assertEqual(_mov_l_literal(rom, 0x57C26), 0xFFFF2302)
        self.assertEqual(_u16(rom, 0x57C2A), 0x02E5)
        for phrase in (
            "uint8[0xFFFF41FA].bit0 set and uint8[0xFFFF248B].bit1 set",
            "uint8[0xFFFF249C].bit6 set and uint8[0xFFFF248B].bit0 set",
            "`tst #1` at `0x57C02` and `bt 0x57C10`",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.published)

    def test_selector_resets_the_grid_on_the_shared_conditions(self):
        rom = self.rom
        # Selected cell outside ROM8[0x8A9E] << 8 .. ROM8[0x8A9F] << 8.
        self.assertEqual(_mov_l_literal(rom, 0x57A94), audit.CELL_LOW_ADDRESS)
        self.assertEqual(_conditional_target(rom, 0x57AA2, 0x8B), 0x57AC4)
        self.assertEqual(_mov_l_literal(rom, 0x57AA4), audit.CELL_HIGH_ADDRESS)
        self.assertEqual(_conditional_target(rom, 0x57AAE, 0x89), 0x57AC4)
        # uint8[0xFFFF41B5].bit0 set.
        self.assertEqual(_mov_l_literal(rom, 0x57AB0) + 12, 0xFFFF41B5)
        self.assertEqual(_u16(rom, 0x57AB2), 0x846C)
        self.assertEqual(_u16(rom, 0x57AB4), 0xC801)
        self.assertEqual(_conditional_target(rom, 0x57AB6, 0x8B), 0x57AC4)
        # FUN 00025E20(0x0129) != 0.
        self.assertEqual(_mov_l_literal(rom, 0x57AB8), 0x25E20)
        self.assertEqual(_mov_w_literal(rom, 0x57ABA), 0x0129)
        self.assertEqual(_conditional_target(rom, 0x57AC2, 0x89), 0x57AFE)
        # The reset path selects 0x6400 and refills the bank grid through 0x58092.
        self.assertEqual(_u16(rom, 0x57AC8), 0xE564)
        self.assertEqual(_u16(rom, 0x57AD2), 0x4518)
        self.assertEqual(_mov_l_literal(rom, 0x57ADC), 0xFFFF4B10)
        self.assertEqual(_mov_l_literal(rom, 0x57AEC), 0xFFFF4B90)
        self.assertEqual(_mov_l_literal(rom, 0x57B00), 0xFFFF2306)
        self.assertIn(
            "`FUN 0005796C` refills the bank grid with `0x6400` and selects "
            "`0x6400` while runtime record `0x129` or `0xFFFF41B5.bit0` is set",
            self.published,
        )



class LtftTelemetryCoverageTest(unittest.TestCase):
    """Bind the published long-term trim coverage to the telemetry profile."""

    @classmethod
    def setUpClass(cls):
        with PROFILE.open("rb") as source:
            profile = tomllib.load(source)
        cls.context_fields = {
            field["name"]: (context["tag"], field["source"])
            for context in profile["context"]
            for field in context["field"]
        }
        cls.sources = {field["source"] for field in profile["field"]} | {
            source for _, source in cls.context_fields.values()
        }
        cls.published = " ".join(TELEMETRY.read_text(encoding="utf-8").split())

    def _field(self, name, tag):
        field_tag, source = self.context_fields[name]
        self.assertEqual(field_tag, tag, name)
        return source

    def test_summand_coverage(self):
        published_b1 = self._field("ltft_b1_raw", audit.PUBLISHED_TAG)
        published_b2 = self._field("ltft_b2_raw", audit.PUBLISHED_TAG)
        learned_b1 = self._field("ltft_learned_b1_raw", audit.LEARNED_TAG)
        adjustment_b1 = self._field("ltft_adjustment_b1_raw", audit.LEARNED_TAG)
        self.assertEqual(learned_b1, 0xFFFF2306)
        self.assertEqual(adjustment_b1, 0xFFFF5648)
        stride = published_b2 - published_b1
        learned_b2 = learned_b1 + stride
        adjustment_b2 = adjustment_b1 + stride
        self.assertNotIn(learned_b2, self.sources)
        self.assertNotIn(adjustment_b2, self.sources)
        self.assertIn("ltft_learned_b1_raw", audit.COLUMNS)
        self.assertIn("ltft_adjustment_b1_raw", audit.COLUMNS)
        for phrase in (
            f"The long-term trim words `{published_b1:08X}` and `{published_b2:08X}` "
            f"in context tag {audit.PUBLISHED_TAG}",
            f"Context tag {audit.LEARNED_TAG} carries the bank 1 summands, learned "
            f"cell `{learned_b1:08X}` and adjustment term `{adjustment_b1:08X}`, and "
            "`tools/logs/ltft_publication_audit.py` compares each bank 1 word with them",
            f"The bank 2 summands `{learned_b2:08X}` and `{adjustment_b2:08X}` are "
            "not streamed",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.published)


if __name__ == "__main__":
    unittest.main()
