from pathlib import Path
import tomllib
import unittest

from tools.logs import cvtc_target_audit


ROOT = Path(__file__).resolve().parents[3]
HARDWARE_RESULTS = ROOT / "patches" / "hardware-results.toml"
CVTC = ROOT / "defs" / "JK08A.cvtc.md"
STOCK_ROM = ROOT / "rom-images" / "23710-JK08A" / "1JK08A-20260726-stock.bin"
RAM_WINDOW = 0xFFFF128C
KEY = "can_telemetry.cvtc_cold_start_2026_09_21"
SESSION = "schema2_profile5_drive_2026_09_21"
CAPTURES = "schema2_profile5_captures"
NUMBER_WORDS = ("zero", "one", "two", "three", "four", "five", "six", "seven")


def _percent(exact, comparisons):
    return f"{100 * exact / comparisons:.3f} percent"


class CvtcColdStartRecordTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with HARDWARE_RESULTS.open("rb") as source:
            cls.registry = tomllib.load(source)
        section, name = KEY.split(".")
        cls.result = cls.registry[section][name]
        cls.session = cls.registry[section][SESSION]
        cls.captures = {
            row["capture_name"]: row for row in cls.registry[section][CAPTURES]
        }
        cls.published = " ".join(CVTC.read_text(encoding="utf-8").split())

    def test_record_belongs_to_the_registered_drive(self):
        result = self.result
        self.assertTrue((ROOT / result["tool"]).is_file())
        self.assertEqual(result["recorded_on"], self.session["recorded_on"])
        self.assertEqual(result["image_sha256"], self.session["image_sha256"])
        capture = self.captures[result["capture_name"]]
        self.assertEqual(result["capture_sha256"], capture["capture_sha256"])
        self.assertEqual(result["record_count"], capture["record_count"])
        self.assertEqual(
            result["analyzed_snapshot_count"] + result["bridge_record_count"],
            result["record_count"],
        )

    def test_equivalence_covers_every_registered_trc_capture(self):
        result = self.result
        trc = {name for name in self.captures if name.endswith(".trc")}
        self.assertEqual(set(result["mlg_equivalence_trc_captures"]), trc)
        for name in trc:
            self.assertIn("converted_mlg_sha256", self.captures[name])
        self.assertEqual(
            result["mlg_equivalence_record_count"],
            sum(self.captures[name]["record_count"] for name in trc),
        )
        self.assertLessEqual(
            result["mlg_equivalence_snapshot_count"]
            + result["mlg_equivalence_bridge_record_count"],
            result["mlg_equivalence_record_count"],
        )
        self.assertLessEqual(
            set(result["warm_trc_intake_captures"]), trc
        )
        self.assertIn(result["warm_trc_exhaust_map_1_capture"], trc)
        self.assertIn("map-1", result["warm_trc_exhaust_map_1_capture"])

    def test_bands_follow_the_coolant_thresholds(self):
        result = self.result
        cold_threshold, warm_threshold = result["coolant_thresholds"]
        low, high = result["coolant_raw_range"]
        self.assertEqual(result["cold_band_coolant_raw"][0], low)
        self.assertEqual(result["cold_band_coolant_raw"][1], cold_threshold)
        self.assertEqual(
            result["blend_band_coolant_raw"],
            [cold_threshold + 1, warm_threshold],
        )
        self.assertEqual(result["warm_band_coolant_raw"], [warm_threshold + 1, high])
        spans = [
            result[f"{band}_band_elapsed_seconds"]
            for band in cvtc_target_audit.COOLANT_BANDS
        ]
        for (start, end), (next_start, _next_end) in zip(spans, spans[1:]):
            self.assertLessEqual(start, end)
            self.assertLess(end, next_start)
        compared = sum(
            result[f"{band}_comparison_count"]
            for band in cvtc_target_audit.COOLANT_BANDS
        )
        self.assertLessEqual(
            compared, result["analyzed_snapshot_count"] - result["source_lag"]
        )
        self.assertEqual(result["cold_band_vehicle_speed_kmh_max"], 0.0)
        self.assertEqual(result["correction_active_count"], 0)

    def test_counts_are_consistent(self):
        result = self.result
        pairs = (
            ("intake_cold_direct_exact_count", "cold_comparison_count"),
            ("intake_cold_active_exact_count", "intake_cold_active_comparison_count"),
            ("intake_cold_alternate_exact_count", "cold_comparison_count"),
            (
                "intake_cold_alternate_active_exact_count",
                "intake_cold_alternate_active_comparison_count",
            ),
            (
                "intake_blend_without_neutralization_exact_count",
                "intake_blend_without_neutralization_comparison_count",
            ),
            ("intake_blend_active_exact_count", "intake_blend_active_comparison_count"),
            (
                "intake_blend_cold_dependent_exact_count",
                "intake_blend_cold_dependent_comparison_count",
            ),
            (
                "intake_blend_stable_active_16_exact_count",
                "intake_blend_stable_active_16_comparison_count",
            ),
            (
                "intake_warm_without_neutralization_exact_count",
                "intake_warm_without_neutralization_comparison_count",
            ),
            (
                "intake_warm_stable_active_16_exact_count",
                "intake_warm_stable_active_16_comparison_count",
            ),
            ("exhaust_cold_exact_count", "cold_comparison_count"),
            (
                "exhaust_warm_without_neutralization_exact_count",
                "exhaust_warm_without_neutralization_comparison_count",
            ),
            (
                "exhaust_warm_stable_active_16_exact_count",
                "exhaust_warm_stable_active_16_comparison_count",
            ),
        )
        for exact, comparisons in pairs:
            with self.subTest(exact=exact):
                self.assertLessEqual(result[exact], result[comparisons])
        self.assertLessEqual(
            result["intake_cold_alternate_exact_count"],
            result["intake_cold_alternate_within_two_count"],
        )
        self.assertLessEqual(
            result["intake_blend_cold_dependent_comparison_count"],
            result["intake_blend_active_comparison_count"],
        )
        self.assertLessEqual(
            result["intake_blend_cold_dependent_exact_count"],
            result["intake_blend_cold_dependent_within_one_count"],
        )
        # The exhaust target is 0x80 wherever the blend prediction is not.
        self.assertEqual(
            result["exhaust_cold_exact_count"], result["cold_comparison_count"]
        )
        self.assertEqual(result["exhaust_blend_active_comparison_count"], 0)
        self.assertEqual(
            result["exhaust_blend_neutralization_sample_count"]
            + result["exhaust_blend_without_neutralization_exact_count"],
            result["blend_comparison_count"],
        )
        self.assertEqual(
            len(result["warm_trc_intake_stable_active_16_exact_count"]),
            len(result["warm_trc_intake_captures"]),
        )
        self.assertEqual(
            len(result["warm_trc_intake_stable_active_16_comparison_count"]),
            len(result["warm_trc_intake_captures"]),
        )

    def test_published_figures_match_the_registry(self):
        result = self.result
        text = self.published
        self.assertIn(f"`{KEY}`", text)
        self.assertIn(f"`{result['capture_name']}`", text)
        self.assertIn(f"`{result['capture_sha256']}`", text)
        self.assertIn(f"`{result['image_sha256']}`", text)
        trc_count = NUMBER_WORDS[len(result["mlg_equivalence_trc_captures"])]
        self.assertIn(f"For each of the {trc_count} TRC captures", text)
        self.assertIn(
            f"{result['mlg_equivalence_snapshot_count']:,} snapshots from "
            f"{result['mlg_equivalence_record_count']:,} records, "
            f"{result['mlg_equivalence_bridge_record_count']:,} of which are "
            "bridge records",
            text,
        )
        self.assertEqual(result["bridge_record_count"], 0)
        self.assertIn(
            f"holds {result['record_count']:,} records, all of them snapshots",
            text,
        )
        low, high = result["coolant_raw_range"]
        self.assertIn(f"Coolant rises from raw {low} to {high}", text)
        self.assertIn(f"keeps Map {result['map_slot']}", text)
        for band in cvtc_target_audit.COOLANT_BANDS:
            start, end = result[f"{band}_band_elapsed_seconds"]
            coolant_low, coolant_high = result[f"{band}_band_coolant_raw"]
            speed = result[f"{band}_band_vehicle_speed_kmh_max"]
            row = (
                f"| {band} | {start:.3f}..{end:.3f} s | "
                f"{coolant_low}..{coolant_high} | "
                f"{result[f'{band}_comparison_count']:,} | {speed!r} km/h |"
            )
            with self.subTest(band=band):
                self.assertIn(row, text)

        rows = (
            ("intake", "cold", "coolant-selected map",
             "intake_cold_direct_exact_count", "cold_comparison_count"),
            ("intake", "cold", "coolant-selected map, active",
             "intake_cold_active_exact_count", "intake_cold_active_comparison_count"),
            ("intake", "cold", "replayed `0xFFFF1553`",
             "intake_cold_alternate_exact_count", "cold_comparison_count"),
            ("intake", "cold", "replayed `0xFFFF1553`, active",
             "intake_cold_alternate_active_exact_count",
             "intake_cold_alternate_active_comparison_count"),
            ("intake", "blend", "map without downstream neutralization",
             "intake_blend_without_neutralization_exact_count",
             "intake_blend_without_neutralization_comparison_count"),
            ("intake", "blend", "map, active",
             "intake_blend_active_exact_count", "intake_blend_active_comparison_count"),
            ("intake", "blend", "map, cold-dependent",
             "intake_blend_cold_dependent_exact_count",
             "intake_blend_cold_dependent_comparison_count"),
            ("intake", "blend", "map, unchanged 16-cycle active",
             "intake_blend_stable_active_16_exact_count",
             "intake_blend_stable_active_16_comparison_count"),
            ("intake", "warm", "map without downstream neutralization",
             "intake_warm_without_neutralization_exact_count",
             "intake_warm_without_neutralization_comparison_count"),
            ("intake", "warm", "map, unchanged 16-cycle active",
             "intake_warm_stable_active_16_exact_count",
             "intake_warm_stable_active_16_comparison_count"),
            ("exhaust", "cold", "map",
             "exhaust_cold_exact_count", "cold_comparison_count"),
            ("exhaust", "blend", "map without downstream neutralization",
             "exhaust_blend_without_neutralization_exact_count",
             "exhaust_blend_without_neutralization_comparison_count"),
            ("exhaust", "warm", "map without downstream neutralization",
             "exhaust_warm_without_neutralization_exact_count",
             "exhaust_warm_without_neutralization_comparison_count"),
            ("exhaust", "warm", "map, unchanged 16-cycle active",
             "exhaust_warm_stable_active_16_exact_count",
             "exhaust_warm_stable_active_16_comparison_count"),
        )
        counts = dict(result)
        # Downstream neutralization removes exactly the neutralized samples.
        counts["exhaust_blend_without_neutralization_comparison_count"] = (
            result["blend_comparison_count"]
            - result["exhaust_blend_neutralization_sample_count"]
        )
        for target, band, check, exact, comparisons in rows:
            row = (
                f"| {target} | {band} | {check} | "
                f"{counts[exact]:,} / {counts[comparisons]:,} |"
            )
            with self.subTest(row=row):
                self.assertIn(row, text)

        unassigned = (
            result["cold_comparison_count"]
            - result["intake_cold_alternate_exact_count"]
        )
        self.assertIn(f"so the {unassigned:,} cold-band comparisons", text)
        self.assertIn(
            f"{result['intake_blend_cold_dependent_exact_count']:,} of its "
            f"{result['intake_blend_cold_dependent_comparison_count']:,} "
            "cold-dependent comparisons are exact",
            text,
        )
        trc_shares = [
            100 * exact / comparisons
            for exact, comparisons in zip(
                result["warm_trc_intake_stable_active_16_exact_count"],
                result["warm_trc_intake_stable_active_16_comparison_count"],
            )
        ]
        warm_share = _percent(
            result["intake_warm_stable_active_16_exact_count"],
            result["intake_warm_stable_active_16_comparison_count"],
        )
        self.assertGreaterEqual(float(warm_share.split()[0]), min(trc_shares))
        self.assertLessEqual(float(warm_share.split()[0]), max(trc_shares))
        self.assertIn(
            f"agreement of {warm_share} lies within the {min(trc_shares):.3f} "
            f"to {max(trc_shares):.3f} percent of the "
            f"{NUMBER_WORDS[len(trc_shares)]} warm TRC captures",
            text,
        )
        exhaust_share = _percent(
            result["exhaust_warm_stable_active_16_exact_count"],
            result["exhaust_warm_stable_active_16_comparison_count"],
        )
        trc_exhaust_share = _percent(
            result["warm_trc_exhaust_stable_active_16_exact_count"],
            result["warm_trc_exhaust_stable_active_16_comparison_count"],
        )
        self.assertLess(
            float(exhaust_share.split()[0]), float(trc_exhaust_share.split()[0])
        )
        self.assertIn(
            f"exhaust figure of {exhaust_share} is below the "
            f"{trc_exhaust_share} of Map 1 capture "
            f"`{result['warm_trc_exhaust_map_1_capture']}`",
            text,
        )
        cold_and_blend = (
            result["cold_comparison_count"] + result["blend_comparison_count"]
        )
        self.assertIn(
            f"stays `0x80` in all {cold_and_blend:,} cold- and blend-band "
            f"comparisons, {result['exhaust_blend_neutralization_sample_count']:,} "
            "of them",
            text,
        )


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


def _conditional_target(data, address):
    """Return the target of the BT or BF at address."""
    opcode = _u16(data, address)
    assert opcode >> 8 in (0x89, 0x8B), hex(opcode)
    displacement = opcode & 0xFF
    if displacement & 0x80:
        displacement -= 0x100
    return address + 4 + displacement * 2


class IntakeIdleSourceCodeTest(unittest.TestCase):
    """Bind the published 0xFFFF1553 code facts to the stock ROM."""

    @classmethod
    def setUpClass(cls):
        cls.rom = STOCK_ROM.read_bytes()
        cls.published = " ".join(CVTC.read_text(encoding="utf-8").split())

    def test_producer_reads_the_tables_the_audit_replays(self):
        rom = self.rom
        # FUN_000BDB66: r7 = 0xFFFF119C[0x12], r4 = table, r5 = axis.
        self.assertEqual(_mov_l_literal(rom, 0xBDB6E) + 0x12, 0xFFFF11AE)
        self.assertEqual(_u16(rom, 0xBDB70), 0xE012)
        self.assertEqual(_u16(rom, 0xBDB74), 0x076C)
        table = _mov_l_literal(rom, 0xBDB72)
        self.assertEqual(
            table, cvtc_target_audit.INTAKE_ALTERNATE_TABLE_ADDRESS
        )
        self.assertEqual(
            _mov_l_literal(rom, 0xBDB76),
            cvtc_target_audit.INTAKE_ALTERNATE_AXIS_ADDRESS,
        )
        # add #8,r14 in the delay slot selects the weight table.
        self.assertEqual(_u16(rom, 0xBDB82), 0x7E08)
        self.assertEqual(
            table + 8, cvtc_target_audit.INTAKE_ALTERNATE_WEIGHT_ADDRESS
        )
        # mov.b @(5,r7),r0 reads coolant index 0xFFFF106F.
        self.assertEqual(_mov_l_literal(rom, 0xBDB88) + 5, 0xFFFF106F)
        self.assertEqual(_u16(rom, 0xBDB8E), 0x8475)
        # mov.b r6,@(r0,r13) stores the result.
        self.assertEqual(_mov_l_literal(rom, 0xBDB7E), RAM_WINDOW)
        self.assertEqual(RAM_WINDOW + _mov_w_literal(rom, 0xBDBD6), 0xFFFF1553)
        self.assertEqual(_u16(rom, 0xBDBDA), 0x0D64)

    def test_conditioner_reads_the_byte_while_the_idle_bit_is_set(self):
        rom = self.rom
        # FUN_000BDC66: mov.b r2,@(r0,r13) stores the coolant-selected byte.
        self.assertEqual(_mov_l_literal(rom, 0xBDDF6), RAM_WINDOW)
        self.assertEqual(RAM_WINDOW + _mov_w_literal(rom, 0xBDE00), 0xFFFF1BEE)
        self.assertEqual(_u16(rom, 0xBDE04), 0x0D24)
        # mov #0x3f,r0; mov.b @(r0,r5),r0; tst #2,r0; bt past the byte.
        self.assertEqual(_mov_l_literal(rom, 0xBDE02) + 0x3F, 0xFFFF24A7)
        self.assertEqual(_u16(rom, 0xBDE06), 0xE03F)
        self.assertEqual(_u16(rom, 0xBDE08), 0x005C)
        self.assertEqual(_u16(rom, 0xBDE0A), 0xC802)
        self.assertEqual(_conditional_target(rom, 0xBDE0C), 0xBDE9C)
        # mov.b @(r0,r13),r5 loads 0xFFFF1553.
        self.assertEqual(RAM_WINDOW + _mov_w_literal(rom, 0xBDE14), 0xFFFF1553)
        self.assertEqual(_u16(rom, 0xBDE16), 0x05DC)
        for phrase in (
            "stored to `0xFFFF1BEE` at `0xBDE04`",
            "tests `0xFFFF24A7` bit 1 at `0xBDE0A`",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.published)

    def test_ramp_reload_tables_hold_five(self):
        rom = self.rom
        # Both functions test ROM8[0x8616] bit 0 before the reload lookups.
        for load, test in ((0xBDBE6, 0xBDBEE), (0xBDE42, 0xBDE46)):
            with self.subTest(load=hex(load)):
                self.assertEqual(_mov_l_literal(rom, load), 0x8616)
                self.assertEqual(_u16(rom, test), 0xC801)
        self.assertEqual(rom[0x8616], 0x01)
        self.assertEqual(_mov_l_literal(rom, 0xBDC14), 0x12EFE)
        self.assertEqual(_mov_l_literal(rom, 0xBDC1E) + 8, 0x12F06)
        self.assertEqual(_u16(rom, 0xBDC22), 0x7408)
        self.assertEqual(_mov_l_literal(rom, 0xBDE70), 0x12EFE)
        self.assertEqual(_mov_l_literal(rom, 0xBDE7A), 0x12F06)
        # FUN_00026370 is the eight-cell implicit byte lookup.
        for load in (0xBDC16, 0xBDC24, 0xBDE72, 0xBDE7E):
            with self.subTest(lookup=hex(load)):
                self.assertEqual(_mov_l_literal(rom, load), 0x26370)
        for address in (0x12EFE, 0x12F06):
            with self.subTest(table=hex(address)):
                self.assertEqual(set(rom[address : address + 8]), {5})
        self.assertIn("bit 0 is set (stock `0x01`)", self.published)
        self.assertIn(
            "Both stock tables hold 5 in each of their eight cells.",
            self.published,
        )

    def test_idle_bit_producer_requires_closed_throttle_and_low_speed(self):
        rom = self.rom
        # FUN_000BD20A: ldc r0,gbr with GBR = 0xFFFF244C.
        gbr = _mov_l_literal(rom, 0xBD21C)
        self.assertEqual(gbr, 0xFFFF244C)
        self.assertEqual(_u16(rom, 0xBD21E), 0x401E)
        self.assertEqual(gbr + 0x5B, 0xFFFF24A7)
        # or #2,r0 ... mov.b r0,@(0x5b,gbr) sets the bit.
        self.assertEqual(_u16(rom, 0xBD98A), 0xCB02)
        self.assertEqual(_u16(rom, 0xBD994), 0xC05B)
        # and #0xfd,r0 ... mov.b r0,@(0x5b,gbr) and and.b #0xfd,@(r0,gbr).
        self.assertEqual(_u16(rom, 0xBD9B4), 0xC9FD)
        self.assertEqual(_u16(rom, 0xBD9C0), 0xC05B)
        self.assertEqual(_u16(rom, 0xBD9C4), 0xE05B)
        self.assertEqual(_u16(rom, 0xBD9C6), 0xCDFD)
        # mov.b @(0xc,gbr),r0; tst #0x20,r0; bt to the clearing path.
        self.assertEqual(gbr + 0xC, 0xFFFF2458)
        self.assertEqual(_u16(rom, 0xBD932), 0xC40C)
        self.assertEqual(_u16(rom, 0xBD934), 0xC820)
        self.assertEqual(_conditional_target(rom, 0xBD936), 0xBD9C2)
        # mov.b @(r0,r2),r6; mov.b @(0xf,r3),r0; cmp/hi r0,r6; bt clears.
        self.assertEqual(_mov_l_literal(rom, 0xBD938) + 0x7A, 0xFFFF110E)
        self.assertEqual(_u16(rom, 0xBD93A), 0xE07A)
        self.assertEqual(_u16(rom, 0xBD93E), 0x062C)
        self.assertEqual(_mov_l_literal(rom, 0xBD93C) + 0xF, 0x871D)
        self.assertEqual(_u16(rom, 0xBD940), 0x843F)
        self.assertEqual(_u16(rom, 0xBD942), 0x3606)
        self.assertEqual(_conditional_target(rom, 0xBD944), 0xBD9C2)
        self.assertEqual(rom[0x871D], 2)
        for phrase in (
            "sets the bit at `0xBD994`",
            "`CLSD THL POS` copy `0xFFFF2458` bit 5",
            f"`0xFFFF110E` at most `ROM8[0x871D] = {rom[0x871D]}`",
            "clears it at `0xBD9C0` or `0xBD9C6`",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.published)

    def test_stock_tables_match_the_published_values(self):
        source = cvtc_target_audit.load_calibration(
            target="intake"
        ).alternate_source
        rpm = [50 * point for point in source.speed_axis]
        self.assertEqual(rpm, list(range(800, 2201, 200)))
        speed = dict(zip(rpm, source.speed_table))
        self.assertEqual({speed[value] for value in rpm if value <= 1200}, {128})
        self.assertEqual(speed[1400], 148)
        self.assertEqual(
            {speed[value] for value in rpm if 1600 <= value <= 2000}, {168}
        )
        self.assertEqual({speed[value] for value in rpm if value >= 2200}, {128})
        step = cvtc_target_audit.INTAKE_ALTERNATE_WEIGHT_STEP
        weight = dict(zip(range(0, 256, step), source.coolant_weight))
        self.assertEqual({weight[index] for index in (96, 112, 128)}, {128})
        self.assertEqual(
            {value for index, value in weight.items() if not 80 < index < 144},
            {0},
        )
        index = cvtc_target_audit.coolant_index
        self.assertEqual(
            [index(raw) for raw in (60, 70, 90, 100)], [80, 96, 128, 144]
        )
        for coolant in (*range(0, 61), *range(100, 256)):
            for rpm50 in range(256):
                self.assertEqual(
                    cvtc_target_audit.intake_alternate_target(
                        source, rpm50, coolant
                    ),
                    0x80,
                )
        exhaust = cvtc_target_audit.load_calibration(target="exhaust").cold
        self.assertEqual(
            exhaust.address, cvtc_target_audit.EXHAUST_CVTC_COLD_MAP_ADDRESS
        )
        self.assertEqual({value for row in exhaust.table for value in row}, {0x80})
        for phrase in (
            "Stock `S` is 128 up to 1200 RPM, 148 at 1400 RPM, 168 from 1600 "
            "to 2000 RPM, and 128 from 2200 RPM.",
            "Stock `W` is 128 from coolant index 96 to 128 (raw 70 to 90, 20 to "
            "40 degC) and 0 at index 80 and below and at index 144 and above, "
            "so the byte is neutral 128 at raw 60 and below and at raw 100 and "
            "above.",
            f"every cell of exhaust cold surface `0x{exhaust.address:X}` is "
            "`0x80`",
        ):
            with self.subTest(phrase=phrase[:40]):
                self.assertIn(phrase, self.published)


if __name__ == "__main__":
    unittest.main()
