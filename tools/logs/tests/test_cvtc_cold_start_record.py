from pathlib import Path
import re
import tomllib
import unittest

from tools.logs import cvtc_intake_state_audit as state_audit
from tools.logs import cvtc_target_audit


ROOT = Path(__file__).resolve().parents[3]
HARDWARE_RESULTS = ROOT / "patches" / "hardware-results.toml"
CVTC = ROOT / "defs" / "JK08A.cvtc.md"
STOCK_ROM = ROOT / "rom-images" / "23710-JK08A" / "1JK08A-20260726-stock.bin"
LOGS = ROOT / "tmp" / "logs-09-21"
IMAGE = ROOT / "tmp" / "1JK08A-tune-v3-1.bin"
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

    def test_state_replay_places_the_cold_band(self):
        result = self.result
        text = self.published
        self.assertTrue((ROOT / result["state_tool"]).is_file())
        self.assertEqual(result["state_class_names"], list(state_audit.CLASSES))
        classes = dict(
            zip(result["state_class_names"], result["cold_state_class_counts"])
        )
        named = ("neutral_target_0x80", "idle_exact", "idle_rise", "idle_other")
        self.assertEqual(
            sum(classes[name] for name in named), result["cold_comparison_count"]
        )
        self.assertEqual(sum(classes.values()), result["cold_comparison_count"])
        self.assertTrue(result["cold_state_latch_independent"])
        # A neutral target differs from the replayed byte only while that byte
        # is active, and each such target lists the failing idle-source terms.
        self.assertEqual(result["cold_state_neutral_idle_blocker_names"], ["rpm"])
        (blocked,) = result["cold_state_neutral_idle_blocker_counts"]
        differ = (
            result["cold_comparison_count"]
            - result["intake_cold_alternate_exact_count"]
        )
        self.assertEqual(
            differ, blocked + classes["idle_rise"] + classes["idle_other"]
        )
        self.assertIn(
            f"divides the cold band into {classes['neutral_target_0x80']:,} "
            f"neutral `0x80` targets, {classes['idle_exact']:,} exact idle-source "
            f"targets, {classes['idle_rise']:,} targets on a rise, and "
            f"{classes['idle_other']:,} other idle-source targets for either latch "
            f"state, so the {differ:,} cold-band comparisons that differ from the "
            f"replayed byte are {blocked:,} neutral targets while the engine-speed "
            f"term of the idle source fails, {classes['idle_rise']:,} on a rise, "
            f"and {classes['idle_other']:,} on the idle-source path outside a "
            "rise.",
            text,
        )
        self.assertIn(
            f"places the {differ:,} cold-band comparisons that differ from that "
            f"byte for either latch state: {blocked:,} carry neutral 0x80 while "
            "the engine-speed term of the idle source fails, "
            f"{classes['idle_rise']:,} lie on a rise, and "
            f"{classes['idle_other']:,} lie on the idle-source path outside a "
            "rise",
            result["result"],
        )
        self.assertIn(
            "the state replay takes CLSD THL POS as APP1 raw at most "
            f"{result['state_app1_released_max']}",
            result["evidence_boundary"],
        )
        self.assertIn(
            f"and {classes['idle_other']:,} cold-band comparisons on the "
            "predicted idle-source path outside a rise differ from the replayed "
            "byte",
            result["evidence_boundary"],
        )

        fields = ("selected", "neutral", "alternate", "main", "other")
        counts = {
            field: result[f"cold_discriminating_{field}_count"] for field in fields
        }
        comparisons = result["cold_discriminating_comparison_count"]
        self.assertEqual(sum(counts.values()), comparisons)
        self.assertLessEqual(comparisons, result["cold_comparison_count"])
        self.assertEqual(result["cold_discriminating_selected_moving_count"], 0)
        row = (
            f"| `{result['capture_name']}` | cold | {comparisons:,} | "
            + " | ".join(f"{counts[field]:,}" for field in fields)
            + " |"
        )
        self.assertIn(row, text)

    @unittest.skipUnless(
        LOGS.is_dir() and IMAGE.is_file(), "road captures are local and untracked"
    )
    def test_state_audit_reproduces_the_cold_band(self):
        result = self.result
        source = LOGS / result["capture_name"]
        if not source.is_file():
            self.skipTest(f"missing capture: {source.name}")
        output = state_audit.audit_recording(
            source,
            calibration_image=IMAGE,
            app1_released_max=result["state_app1_released_max"],
            rearm_snapshots=result["state_rearm_snapshots"],
            coolant_bands=("cold",),
        )
        self.assertEqual(output.source_sha256, result["capture_sha256"])
        self.assertEqual(output.calibration_image_sha256, result["image_sha256"])
        self.assertEqual(output.records, result["record_count"])
        (band,) = output.bands
        self.assertEqual(band.comparisons, result["cold_comparison_count"])
        self.assertEqual(
            list(band.coolant_raw_range), result["cold_band_coolant_raw"]
        )
        self.assertEqual(
            [replay.latch_initial for replay in output.replays],
            list(state_audit.LATCH_STATES),
        )
        for replay in output.replays:
            (partition,) = replay.partitions
            with self.subTest(latch=replay.latch_initial):
                self.assertEqual(
                    [count for _name, count in partition.classes],
                    result["cold_state_class_counts"],
                )
                self.assertEqual(
                    [name for name, _count in partition.neutral_idle_blockers],
                    result["cold_state_neutral_idle_blocker_names"],
                )
                self.assertEqual(
                    [count for _name, count in partition.neutral_idle_blockers],
                    result["cold_state_neutral_idle_blocker_counts"],
                )
                (blocked,) = result["cold_state_neutral_idle_blocker_counts"]
                classes = dict(partition.classes)
                self.assertEqual(
                    dict(partition.differ_from_alternate),
                    {
                        "neutral_target_0x80": blocked,
                        "idle_rise": classes["idle_rise"],
                        "idle_other": classes["idle_other"],
                    },
                )
        (discrimination,) = output.discrimination
        for field in (
            "comparison",
            "selected",
            "selected_moving",
            "neutral",
            "alternate",
            "main",
            "other",
        ):
            attribute = "comparisons" if field == "comparison" else field
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(discrimination, attribute),
                    result[f"cold_discriminating_{field}_count"],
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
    """Return the target of the BT, BF, BT/S, or BF/S at address."""
    opcode = _u16(data, address)
    assert opcode >> 8 in (0x89, 0x8B, 0x8D, 0x8F), hex(opcode)
    displacement = opcode & 0xFF
    if displacement & 0x80:
        displacement -= 0x100
    return address + 4 + displacement * 2


def _bra_target(data, address):
    """Return the target of the BRA at address."""
    opcode = _u16(data, address)
    assert opcode >> 12 == 0xA, hex(opcode)
    displacement = opcode & 0xFFF
    if displacement & 0x800:
        displacement -= 0x1000
    return address + 4 + displacement * 2


def _signed8(value):
    return value - 0x100 if value & 0x80 else value


def _record_calls(data, start, end):
    """Return the r4 argument of each JSR @r6 in [start, end).

    The argument comes from MOV #imm,r4 or MOV.W @(disp,PC),r4 up to five
    instructions before the call or in its delay slot, which may also hold
    EXTU.B r4,r4, SHLL2 r4, or an instruction that leaves r4 unchanged.
    """
    records = []
    for address in range(start, end, 2):
        if _u16(data, address) != 0x460B:
            continue
        slot = _u16(data, address + 2)
        if slot >> 8 == 0xE4:
            records.append(_signed8(slot & 0xFF))
            continue
        for back in range(address - 2, address - 12, -2):
            word = _u16(data, back)
            if word >> 8 == 0xE4:
                value = _signed8(word & 0xFF)
                break
            if word >> 8 == 0x94:
                value = _u16(data, back + 4 + (word & 0xFF) * 2)
                break
        else:
            raise AssertionError(f"no r4 load before 0x{address:X}")
        if slot == 0x644C:
            value &= 0xFF
        elif slot == 0x4408:
            value <<= 2
        else:
            # nop or mov.l r6,@(4,r15)
            assert slot in (0x0009, 0x1F61), hex(slot)
        records.append(value)
    return records


def _section(text, heading):
    """Return the Markdown section under heading up to the next heading."""
    start = text.index(f"\n{heading}\n")
    end = text.find("\n#", start + len(heading) + 2)
    return text[start:end]


class IntakeIdleSourceCodeTest(unittest.TestCase):
    """Bind the published 0xFFFF1553 code facts to the stock ROM."""

    @classmethod
    def setUpClass(cls):
        cls.rom = STOCK_ROM.read_bytes()
        cls.source = CVTC.read_text(encoding="utf-8")
        cls.published = " ".join(cls.source.split())

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
            f"ffff110e <= ROM8[0x871D] = {rom[0x871D]} vehicle-speed byte",
            f"the vehicle-speed byte at most {rom[0x871D]}.",
            "clears it at `0xBD9C0` or `0xBD9C6`",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.published)

    def test_idle_bit_terms_follow_the_published_order(self):
        rom = self.rom
        gbr = _mov_l_literal(rom, 0xBD21C)
        # Each failing term branches to 0xBD9C2, directly or through a BRA.
        # (address, opcode): mov.b @(disp,gbr),r0 or tst #imm,r0 pairs.
        for address, opcode in (
            (0xBD680, 0xC43F),  # ffff248b
            (0xBD682, 0xC802),  # bit 1 set
            (0xBD6B0, 0xC444),  # ffff2490
            (0xBD6B2, 0xC808),  # bit 3 set
            (0xBD6BE, 0xC810),  # bit 4 set
            (0xBD700, 0xC444),  # ffff2490
            (0xBD702, 0xC840),  # bit 6 set
            (0xBD70E, 0xC880),  # bit 7 set
            (0xBD8A0, 0xC443),  # ffff248f
            (0xBD8A2, 0xC801),  # bit 0 set
            (0xBD8AE, 0xC802),  # bit 1 set
            (0xBD90C, 0x8464),  # mov.b @(4,r6),r0: ffff4250
            (0xBD90E, 0xC880),  # bit 7 clear
            (0xBD912, 0xC410),  # ffff245c
            (0xBD914, 0xC810),  # bit 4 clear
            (0xBD92C, 0xC444),  # ffff2490
            (0xBD92E, 0xC820),  # bit 5 set
            (0xBD94C, 0xC801),  # ffff2f64 bit 0 clear
            (0xBD950, 0xC802),  # ffff2f64 bit 1 clear
            (0xBD95A, 0xC801),  # ffff14b8 bit 0 clear
            (0xBD95E, 0xC802),  # ffff14b8 bit 1 clear
            (0xBD962, 0xC443),  # ffff248f
            (0xBD96C, 0xC804),  # bit 2 set
        ):
            with self.subTest(address=hex(address)):
                self.assertEqual(_u16(rom, address), opcode)
        self.assertEqual(
            (gbr + 0x3F, gbr + 0x43, gbr + 0x44, gbr + 0x10),
            (0xFFFF248B, 0xFFFF248F, 0xFFFF2490, 0xFFFF245C),
        )
        self.assertEqual(_mov_l_literal(rom, 0xBD904) + 4, 0xFFFF4250)
        self.assertEqual(
            _mov_l_literal(rom, 0xBD946) + _mov_w_literal(rom, 0xBD948), 0xFFFF2F64
        )
        self.assertEqual(RAM_WINDOW + _mov_w_literal(rom, 0xBD956), 0xFFFF14B8)
        for branch in (0xBD910, 0xBD916, 0xBD930, 0xBD94E, 0xBD952, 0xBD95C,
                       0xBD960, 0xBD96E):
            with self.subTest(branch=hex(branch)):
                self.assertEqual(_conditional_target(rom, branch), 0xBD9C2)
        for escape in (0xBD686, 0xBD6B8, 0xBD6C2, 0xBD708, 0xBD712, 0xBD8A8,
                       0xBD8B2):
            with self.subTest(escape=hex(escape)):
                self.assertEqual(_bra_target(rom, escape), 0xBD9C2)
        # 0xFFFF41D1 bit 7, 0xFFFF41D0 bit 0, 0xFFFF41BE bit 6 clear.
        base = _mov_l_literal(rom, 0xBD68A)
        for load, test, mask, address in (
            (0xBD68C, 0xBD690, 0x80, 0xFFFF41D1),
            (0xBD698, 0xBD69C, 0x01, 0xFFFF41D0),
            (0xBD6A4, 0xBD6A8, 0x40, 0xFFFF41BE),
        ):
            with self.subTest(address=hex(address)):
                self.assertEqual(base + (_u16(rom, load) & 0xFF), address)
                self.assertEqual(_u16(rom, test), 0xC800 | mask)
                self.assertEqual(_bra_target(rom, test + 4), 0xBD9C2)

        # FUN_00025E20 is saved to @(4,r15) and called with each record.
        self.assertEqual(_mov_l_literal(rom, 0xBD6C8), 0x25E20)
        self.assertEqual(_u16(rom, 0xBD6D0), 0x1F61)
        self.assertEqual(_mov_l_literal(rom, 0xBD6C6), 0x8616)
        self.assertEqual(_u16(rom, 0xBD6CC), 0xC801)
        self.assertEqual(_conditional_target(rom, 0xBD6CE), 0xBD716)
        self.assertEqual(_mov_l_literal(rom, 0xBD85A) + 1, 0x870F)
        self.assertEqual(_u16(rom, 0xBD85C), 0x8431)
        self.assertEqual(_u16(rom, 0xBD85E), 0xC801)
        self.assertEqual(_conditional_target(rom, 0xBD860), 0xBD8B6)
        self.assertEqual(_bra_target(rom, 0xBD862), 0xBD890)
        self.assertEqual(_mov_l_literal(rom, 0xBD8B6), 0x870C)
        self.assertEqual(_u16(rom, 0xBD8BA), 0xC820)
        self.assertEqual(_conditional_target(rom, 0xBD8BC), 0xBD902)
        self.assertEqual(_mov_l_literal(rom, 0xBD918), 0x870E)
        self.assertEqual(_u16(rom, 0xBD91C), 0xC810)
        self.assertEqual(_conditional_target(rom, 0xBD91E), 0xBD92C)
        self.assertEqual(rom[0x8616] & 1, 1)
        self.assertEqual(rom[0x870F] & 1, 1)
        self.assertEqual((rom[0x870C], rom[0x870E]), (0x44, 0x28))
        self.assertEqual(rom[0x870C] & 0x20, 0)
        self.assertEqual(rom[0x870E] & 0x10, 0)
        oil_records = _record_calls(rom, 0xBD6C6, 0xBD716)
        records = _record_calls(rom, 0xBD716, 0xBD85A)
        iat_records = _record_calls(rom, 0xBD85A, 0xBD8B6)
        option_records = _record_calls(rom, 0xBD8B6, 0xBD902)
        self.assertEqual(oil_records, [0xDD, 0xDE, 0xE4])
        self.assertEqual(
            sorted(records),
            [*range(0x8D, 0x97), *range(0xFC, 0x100), 0x127, 0x128,
             *range(0x153, 0x157)],
        )
        self.assertEqual(iat_records, [0x12E])
        self.assertEqual(option_records, [-1] * 6)
        for phrase in (
            "`FUN 000BD20A` writes `0xFFFF24A7` bit 1 on every call through its "
            "single exit.",
            "ffff248b bit 1 electrical enable",
            "ffff2458 bit 5 CLSD THL POS",
            "The pass also requires `0xFFFF41D1` bit 7, `0xFFFF41D0` bit 0, "
            "`0xFFFF41BE` bit 6, `0xFFFF4250` bit 7, `0xFFFF245C` bit 4, and bits "
            "0 and 1 of `0xFFFF2F64` and `0xFFFF14B8` clear, and the stored-fault "
            "bit of `FUN 00025E20` clear for records `0x8D..0x96`, `0xFC..0xFF`, "
            "`0x127`, `0x128`, and `0x153..0x156`, for `0xDD`, `0xDE`, and `0xE4` "
            "under `ROM8[0x8616]` bit 0, and for `0x12E` under `ROM8[0x870F]` bit "
            "0.",
            "The terms under `ROM8[0x870C]` bit 5 and `ROM8[0x870E]` bit 4 are "
            "skipped with the stock bytes `0x44` and `0x28`.",
        ):
            with self.subTest(phrase=phrase[:40]):
                self.assertIn(phrase, self.published)

    def test_start_and_rearm_countdowns(self):
        rom = self.rom
        gbr = _mov_l_literal(rom, 0xBD21C)
        self.assertEqual(
            (gbr + 0xDB, gbr + 0xDC, gbr + 0x41),
            (0xFFFF2527, 0xFFFF2528, 0xFFFF248D),
        )
        # r8 = 0xFFFF4184; the start event loads the countdown.
        self.assertEqual(_mov_l_literal(rom, 0xBD2D6), 0xFFFF4184)
        self.assertEqual(_u16(rom, 0xBD5EC), 0x6080)
        self.assertEqual(_u16(rom, 0xBD5EE), 0xC840)
        self.assertEqual(_conditional_target(rom, 0xBD5F0), 0xBD604)
        self.assertEqual(_mov_l_literal(rom, 0xBD5F2) + 6, 0x8714)
        self.assertEqual(_u16(rom, 0xBD5F4), 0x8436)
        self.assertEqual(_u16(rom, 0xBD5F6), 0xC0DC)
        self.assertEqual(rom[0x8714], 30)
        # or #8 into 0xFFFF248F, then and.b #0xeb clears bits 2 and 4.
        self.assertEqual(_u16(rom, 0xBD5FA), 0xCB08)
        self.assertEqual(_u16(rom, 0xBD5FC), 0xC043)
        self.assertEqual(_u16(rom, 0xBD5FE), 0xE043)
        self.assertEqual(_bra_target(rom, 0xBD600), 0xBD680)
        self.assertEqual(_u16(rom, 0xBD602), 0xCDEB)
        # A nonzero start countdown or a clear 0xFFFF248F bit 3 clears the
        # engine-speed flag (bit 2) and the BFS flag (0xFFFF2490 bit 5).
        self.assertEqual(_u16(rom, 0xBD604), 0xC4DC)
        self.assertEqual(_u16(rom, 0xBD606), 0x2008)
        self.assertEqual(_conditional_target(rom, 0xBD608), 0xBD676)
        self.assertEqual(_u16(rom, 0xBD608) >> 8, 0x8B)
        self.assertEqual(_u16(rom, 0xBD60C), 0xC808)
        self.assertEqual(_conditional_target(rom, 0xBD60E), 0xBD676)
        self.assertEqual(_u16(rom, 0xBD60E) >> 8, 0x89)
        self.assertEqual(_u16(rom, 0xBD678), 0xC9FB)
        self.assertEqual(_u16(rom, 0xBD67A), 0xC043)
        self.assertEqual(_u16(rom, 0xBD67C), 0xE044)
        self.assertEqual(_u16(rom, 0xBD67E), 0xCDDF)
        # 0xFFFF248D bit 3, or 0xFFFF248F bit 4 with 0xFFFF2527 nonzero,
        # takes the waiting path to 0xBD9B0.
        self.assertEqual(_u16(rom, 0xBD970), 0xC441)
        self.assertEqual(_u16(rom, 0xBD972), 0xC808)
        self.assertEqual(_u16(rom, 0xBD974) >> 8, 0x8B)
        self.assertEqual(_conditional_target(rom, 0xBD974), 0xBD9B0)
        # @(40,r15) holds the 0xFFFF248F byte loaded at 0xBD962.
        self.assertEqual(_u16(rom, 0xBD966), 0xE028)
        self.assertEqual(_u16(rom, 0xBD968), 0x0F24)
        self.assertEqual(_u16(rom, 0xBD976), 0xE028)
        self.assertEqual(_u16(rom, 0xBD978), 0x00FC)
        self.assertEqual(_u16(rom, 0xBD97A), 0xC810)
        self.assertEqual(_conditional_target(rom, 0xBD97C), 0xBD984)
        self.assertEqual(_u16(rom, 0xBD97E), 0xC4DB)
        self.assertEqual(_u16(rom, 0xBD980), 0x2008)
        self.assertEqual(_u16(rom, 0xBD982) >> 8, 0x8B)
        self.assertEqual(_conditional_target(rom, 0xBD982), 0xBD9B0)
        # The waiting path clears the bit at 0xBD9C0 and skips the reload.
        self.assertEqual(_u16(rom, 0xBD9B4), 0xC9FD)
        self.assertEqual(_bra_target(rom, 0xBD9BE), 0xBD9CC)
        self.assertEqual(_u16(rom, 0xBD9C0), 0xC05B)
        # The set path sets 0xFFFF248F bit 4 and stores 0 to 0xFFFF2527.
        self.assertEqual(_u16(rom, 0xBD99A), 0xCB10)
        self.assertEqual(_u16(rom, 0xBD9A4), 0xC043)
        self.assertEqual(_bra_target(rom, 0xBD9A6), 0xBD9CA)
        self.assertEqual(_u16(rom, 0xBD9A8), 0xE000)
        # The failing path reloads 0xFFFF2527 from ROM8[0x8713].
        self.assertEqual(_mov_l_literal(rom, 0xBD9C2) + 5, 0x8713)
        self.assertEqual(_u16(rom, 0xBD9C8), 0x8435)
        self.assertEqual(_u16(rom, 0xBD9CA), 0xC0DB)
        self.assertEqual(rom[0x8713], 100)
        self.assertEqual(
            (rom[0x8715], rom[0x8716]),
            (
                state_audit.load_state_calibration().idle_rpm_hold,
                state_audit.load_state_calibration().idle_rpm_set_offset,
            ),
        )
        for phrase in (
            "`ROM8[0x8714] = 30` at `0xBD5F6`",
            "sets `0xFFFF248F` bit 3, and clears `0xFFFF248F` bits 2 and 4",
            "stay clear while `0xFFFF2528` is nonzero or `0xFFFF248F` bit 3 is "
            "clear",
            "Each pass through `0xBD9C2` reloads re-arm countdown `0xFFFF2527` "
            "from `ROM8[0x8713] = 100` at `0xBD9C8`, and the set path stores 0 to "
            "it at `0xBD9CA` and sets `0xFFFF248F` bit 4 at `0xBD9A4`.",
            "the bit stays clear at `0xBD9C0` without the reload while "
            "`0xFFFF248D` bit 3 is set or, once `0xFFFF248F` bit 4 is set, while "
            "`0xFFFF2527` is nonzero.",
        ):
            with self.subTest(phrase=phrase[:40]):
                self.assertIn(phrase, self.published)

    def test_operating_bit_stores_the_enable_register(self):
        rom = self.rom
        gbr = _mov_l_literal(rom, 0xBD21C)
        self.assertEqual((gbr + 0x1F, gbr + 0x3F), (0xFFFF246B, 0xFFFF248B))
        # mov #0,r10 and mov #1,r10.
        for address, opcode in (
            (0xBD224, 0xEA00),
            (0xBD41E, 0xEA01),
            (0xBD462, 0xEA00),
            (0xBD492, 0xEA00),
            (0xBD988, 0xEA01),
        ):
            with self.subTest(address=hex(address)):
                self.assertEqual(_u16(rom, address), opcode)
        # tst r10,r10; bt/s; and #0xfd; or #2; mov.b r0,@(0x3f,gbr).
        self.assertEqual(_u16(rom, 0xBD420), 0xC43F)
        self.assertEqual(_u16(rom, 0xBD422), 0x2AA8)
        self.assertEqual(_conditional_target(rom, 0xBD42C), 0xBD432)
        self.assertEqual(_u16(rom, 0xBD42E), 0xC9FD)
        self.assertEqual(_u16(rom, 0xBD430), 0xCB02)
        self.assertEqual(_u16(rom, 0xBD432), 0xC03F)
        # tst r10,r10; bt/s; and #0xbf; or #0x40; mov.b r0,@(0x1f,gbr).
        self.assertEqual(_u16(rom, 0xBD9CC), 0xC41F)
        self.assertEqual(_u16(rom, 0xBD9CE), 0x2AA8)
        self.assertEqual(_conditional_target(rom, 0xBD9D0), 0xBD9D6)
        self.assertEqual(_u16(rom, 0xBD9D2), 0xC9BF)
        self.assertEqual(_u16(rom, 0xBD9D4), 0xCB40)
        self.assertEqual(_u16(rom, 0xBD9D6), 0xC01F)
        self.assertEqual(_u16(rom, 0xBD9EC), 0x000B)

        # Terms of 0xBD41E; each failing term branches past it to 0xBD420.
        self.assertEqual(_mov_l_literal(rom, 0xBD3BA), RAM_WINDOW)
        self.assertEqual(RAM_WINDOW + _mov_w_literal(rom, 0xBD3BC), 0xFFFF19AA)
        self.assertEqual(RAM_WINDOW + _mov_w_literal(rom, 0xBD3C0), 0xFFFF17F0)
        self.assertEqual(_u16(rom, 0xBD3C8), 0x3657)  # cmp/gt r5,r6
        self.assertEqual(_mov_l_literal(rom, 0xBD3CC), 0x25E4E)
        self.assertEqual(_u16(rom, 0xBD3D2), 0x2008)
        self.assertEqual(_record_calls(rom, 0xBD3D6, 0xBD3EE), [0x14B, 0x14C])
        self.assertEqual(_mov_l_literal(rom, 0xBD3D6), 0x25E20)
        self.assertEqual(_mov_l_literal(rom, 0xBD3EE), 0x8E0A)
        self.assertEqual(_u16(rom, 0xBD3F0), 0xE074)
        self.assertEqual(_mov_l_literal(rom, 0xBD3F4) + 0x74, 0xFFFF1108)
        self.assertEqual(_u16(rom, 0xBD3FC), 0x3653)  # cmp/ge r5,r6
        self.assertEqual(_mov_l_literal(rom, 0xBD400), 0x8E07)
        self.assertEqual(_u16(rom, 0xBD406), 0x3527)  # cmp/gt r2,r5
        self.assertEqual((rom[0x8E0A], rom[0x8E07]), (125, 200))
        self.assertEqual(gbr + 3, 0xFFFF244F)
        self.assertEqual(_u16(rom, 0xBD40A), 0xC403)
        self.assertEqual(_u16(rom, 0xBD40C), 0xC820)
        self.assertEqual(
            _mov_l_literal(rom, 0xBD410) + _mov_w_literal(rom, 0xBD412), 0xFFFF3622
        )
        self.assertEqual(_u16(rom, 0xBD416), 0xC801)
        self.assertEqual(_u16(rom, 0xBD41A), 0xC802)
        for branch, opcode in (
            (0xBD3CA, 0x8B),  # bf: counter not above the threshold
            (0xBD3D4, 0x8B),  # bf: FUN_00025E4E nonzero
            (0xBD3E0, 0x8B),  # bf: record 0x14B
            (0xBD3EC, 0x8B),  # bf: record 0x14C
            (0xBD3FE, 0x89),  # bt: battery at most 125
            (0xBD408, 0x89),  # bt: battery above 200
            (0xBD40E, 0x89),  # bt: 0xFFFF244F bit 5 clear
            (0xBD418, 0x8B),  # bf: 0xFFFF3622 bit 0 set
            (0xBD41C, 0x8B),  # bf: 0xFFFF3622 bit 1 set
        ):
            with self.subTest(branch=hex(branch)):
                self.assertEqual(_u16(rom, branch) >> 8, opcode)
                self.assertEqual(_conditional_target(rom, branch), 0xBD420)

        # Terms of 0xBD462.
        self.assertEqual(_u16(rom, 0xBD434), 0xC40C)  # 0xFFFF2458
        self.assertEqual(_u16(rom, 0xBD436), 0xC820)
        self.assertEqual(_conditional_target(rom, 0xBD438), 0xBD442)
        self.assertEqual(_mov_l_literal(rom, 0xBD43A), 0x8940)
        self.assertEqual(_u16(rom, 0xBD43E), 0xC802)
        self.assertEqual(rom[0x8940], 0x01)
        self.assertEqual(_u16(rom, 0xBD442), 0xC441)  # 0xFFFF248D
        self.assertEqual(_u16(rom, 0xBD444), 0xC808)
        base = _mov_l_literal(rom, 0xBD448)
        for load, test, mask, address in (
            (0xBD44A, 0xBD44E, 0x80, 0xFFFF41D1),
            (0xBD452, 0xBD456, 0x01, 0xFFFF41D0),
            (0xBD45A, 0xBD45E, 0x40, 0xFFFF41BE),
        ):
            with self.subTest(address=hex(address)):
                self.assertEqual(base + (_u16(rom, load) & 0xFF), address)
                self.assertEqual(_u16(rom, test), 0xC800 | mask)
        for branch, opcode in (
            (0xBD440, 0x89),
            (0xBD446, 0x8B),
            (0xBD450, 0x8B),
            (0xBD458, 0x8B),
        ):
            with self.subTest(branch=hex(branch)):
                self.assertEqual(_u16(rom, branch) >> 8, opcode)
                self.assertEqual(_conditional_target(rom, branch), 0xBD462)
        self.assertEqual(_conditional_target(rom, 0xBD460), 0xBD464)

        # Terms of 0xBD492: 0xFFFF24A9 bit 6, the latch-selected floor, and
        # 0xFFFF24A8 bit 4.
        self.assertEqual((gbr + 0x5C, gbr + 0x5D), (0xFFFF24A8, 0xFFFF24A9))
        self.assertEqual(_u16(rom, 0xBD468), 0xC45D)
        self.assertEqual(_u16(rom, 0xBD46A), 0xC840)
        self.assertEqual(_conditional_target(rom, 0xBD46C), 0xBD492)
        self.assertEqual(_mov_l_literal(rom, 0xBD470) + 2, 0xFFFF5B2C)
        self.assertEqual(_u16(rom, 0xBD472), 0x8462)
        self.assertEqual(_u16(rom, 0xBD474), 0xC940)
        self.assertEqual(_conditional_target(rom, 0xBD478), 0xBD482)
        self.assertEqual(_u16(rom, 0xBD47E), 0xC801)
        self.assertEqual(_conditional_target(rom, 0xBD480), 0xBD492)
        self.assertEqual(_conditional_target(rom, 0xBD484), 0xBD48C)
        self.assertEqual(_u16(rom, 0xBD488), 0xC808)
        self.assertEqual(_conditional_target(rom, 0xBD48A), 0xBD492)
        self.assertEqual(_u16(rom, 0xBD48C), 0xC45C)
        self.assertEqual(_u16(rom, 0xBD48E), 0xC810)
        self.assertEqual(_conditional_target(rom, 0xBD490), 0xBD494)

        # Start counter: zeroed and its threshold loaded by the start event,
        # counted up to 255 while 0xFFFF84C3 bit 7 is set.
        self.assertEqual(_u16(rom, 0xBD2DA), 0xC840)
        self.assertEqual(_conditional_target(rom, 0xBD2DC), 0xBD39C)
        self.assertEqual(_u16(rom, 0xBD2E0), 0xE200)
        self.assertEqual(RAM_WINDOW + _mov_w_literal(rom, 0xBD2E2), 0xFFFF19AA)
        self.assertEqual(_u16(rom, 0xBD2E6), 0x0624)
        self.assertEqual(_mov_l_literal(rom, 0xBD2EA), 0x8616)
        self.assertEqual(_u16(rom, 0xBD2EE), 0xC801)
        self.assertEqual(_mov_l_literal(rom, 0xBD2F2) + 0xF8, 0xFFFF2772)
        self.assertEqual(_u16(rom, 0xBD2F4), 0xE0F8)
        self.assertEqual(_u16(rom, 0xBD2F6), 0x600C)
        self.assertEqual(_mov_l_literal(rom, 0xBD2F8), 0x12A8A)
        self.assertEqual(RAM_WINDOW + _mov_w_literal(rom, 0xBD308), 0xFFFF17F0)
        self.assertEqual(_u16(rom, 0xBD30A), 0x0324)
        self.assertEqual(set(rom[0x12A8A : 0x12A8A + 8]), {30})
        opcode = _u16(rom, 0xBD39C)
        self.assertEqual(opcode >> 8, 0x96)
        self.assertEqual(
            0xFFFF0000 | _u16(rom, 0xBD39C + 4 + (opcode & 0xFF) * 2), 0xFFFF84C3
        )
        self.assertEqual(_u16(rom, 0xBD3A0), 0xC880)
        self.assertEqual(_conditional_target(rom, 0xBD3A2), 0xBD3BA)
        self.assertEqual(_u16(rom, 0xBD3A6), 0xE5FF)
        self.assertEqual(RAM_WINDOW + _mov_w_literal(rom, 0xBD3A8), 0xFFFF19AA)
        self.assertEqual(_u16(rom, 0xBD3B6), 0x7601)
        self.assertEqual(_u16(rom, 0xBD3B8), 0x0364)
        for phrase in (
            "`FUN 000BD20A` stores register `r10` to `0xFFFF246B` bit 6 at "
            "`0xBD9D6`.",
            "It clears `r10` at `0xBD224` and sets it at `0xBD41E` only while "
            "start counter `0xFFFF19AA` exceeds `0xFFFF17F0`, `FUN 00025E4E` "
            "returns zero, the stored-fault bits of records `0x14B` and `0x14C` "
            "are clear, battery snapshot `0xFFFF1108` lies above "
            "`ROM8[0x8E0A] = 125` and at most `ROM8[0x8E07] = 200`, `0xFFFF244F` "
            "bit 5 is set, and `0xFFFF3622` bits 0 and 1 are clear.",
            "The start event zeroes `0xFFFF19AA` and loads `0xFFFF17F0` from "
            "`0x12A8A` by oil temperature `0xFFFF2772` while `ROM8[0x8616]` bit 0 "
            "is set, 30 in each stock cell; later calls count `0xFFFF19AA` up to "
            "255 while `0xFFFF84C3` bit 7 is set.",
            "`0xBD432` stores the result as intake electrical enable `0xFFFF248B` "
            "bit 1.",
            "`r10` returns to 0 at `0xBD462` when `CLSD THL POS` copy "
            "`0xFFFF2458` bit 5 is set while `ROM8[0x8940]` bit 1 is clear (stock "
            "`0x01`), or when `0xFFFF248D` bit 3, `0xFFFF41D1` bit 7, "
            "`0xFFFF41D0` bit 0, or `0xFFFF41BE` bit 6 is set.",
            "It returns to 0 at `0xBD492` unless coolant ceiling flag "
            "`0xFFFF24A9` bit 6, the coolant floor, and engine-speed flag "
            "`0xFFFF24A8` bit 4 are all set.",
            "The idle-source path sets `r10` again at `0xBD988`, so the operating "
            "bit is set whenever `0xFFFF24A7` bit 1 is.",
        ):
            with self.subTest(phrase=phrase[:40]):
                self.assertIn(phrase, self.published)

    def test_latch_selects_the_coolant_floor(self):
        rom = self.rom
        # 0xFFFF24A9 bit 0: raw coolant, plus 3 while set, above ROM8[0x8E06].
        self.assertEqual(_mov_l_literal(rom, 0xBD294) + 9, 0xFFFF1071)
        self.assertEqual(_u16(rom, 0xBD296), 0x8439)
        self.assertEqual(_u16(rom, 0xBD29A), 0xC45D)
        self.assertEqual(_u16(rom, 0xBD29C), 0xC801)
        self.assertEqual(_conditional_target(rom, 0xBD29E), 0xBD2A2)
        self.assertEqual(_u16(rom, 0xBD2A0), 0x7D03)
        self.assertEqual(_mov_l_literal(rom, 0xBD2A2), 0x8E06)
        self.assertEqual(_u16(rom, 0xBD2A8), 0x3D66)  # cmp/hi r6,r13
        self.assertEqual(_conditional_target(rom, 0xBD2AA), 0xBD2B2)
        self.assertEqual(_u16(rom, 0xBD2AC), 0xE05D)
        self.assertEqual(_u16(rom, 0xBD2B0), 0xCDFE)
        self.assertEqual(_u16(rom, 0xBD2B2), 0xCF01)
        self.assertEqual(rom[0x8E06], 70)
        # Latch 0xFFFF5B2C bit 6: set at 125 and above, cleared below 65.
        self.assertEqual(_mov_l_literal(rom, 0xBD2B4) + 9, 0xFFFF1071)
        self.assertEqual(_u16(rom, 0xBD2B8), 0x8439)
        self.assertEqual(_u16(rom, 0xBD2B6), 0xE500 | state_audit.LATCH_SET_COOLANT)
        self.assertEqual(_u16(rom, 0xBD2BC), 0x3253)  # cmp/ge r5,r2
        self.assertEqual(_u16(rom, 0xBD2BE) >> 8, 0x8B)
        self.assertEqual(_conditional_target(rom, 0xBD2BE), 0xBD2C8)
        self.assertEqual(_mov_l_literal(rom, 0xBD2C0) + 2, 0xFFFF5B2C)
        self.assertEqual(_u16(rom, 0xBD2C2), 0x8452)
        self.assertEqual(_u16(rom, 0xBD2C4), 0xCB40)
        self.assertEqual(_u16(rom, 0xBD2C6), 0x8052)
        self.assertEqual(
            _u16(rom, 0xBD2C8), 0xE600 | state_audit.LATCH_CLEAR_COOLANT
        )
        self.assertEqual(_u16(rom, 0xBD2CA), 0x3263)  # cmp/ge r6,r2
        self.assertEqual(_u16(rom, 0xBD2CC) >> 8, 0x89)
        self.assertEqual(_conditional_target(rom, 0xBD2CC), 0xBD2D6)
        self.assertEqual(_mov_l_literal(rom, 0xBD2CE) + 2, 0xFFFF5B2C)
        self.assertEqual(_u16(rom, 0xBD2D0), 0x8462)
        self.assertEqual(_u16(rom, 0xBD2D2), 0xC9BF)
        self.assertEqual(_u16(rom, 0xBD2D4), 0x8062)
        low, high = (
            state_audit.LATCH_CLEAR_COOLANT,
            state_audit.LATCH_SET_COOLANT - 1,
        )
        for phrase in (
            "`0xFFFF24A9` bit 0 as raw coolant above `ROM8[0x8E06] = 70`, adding "
            "3 while set.",
            "The floor is `0xFFFF24A9` bit 0 while latch `0xFFFF5B2C` bit 6 is set "
            "and `0xFFFF24A9` bit 3, raw coolant above 106, while it is clear.",
            "The function sets the latch at raw coolant `0xFFFF1071` of "
            f"{state_audit.LATCH_SET_COOLANT} and above (`0xBD2B6`..`0xBD2C6`) "
            f"and clears it below {state_audit.LATCH_CLEAR_COOLANT} "
            f"(`0xBD2C8`..`0xBD2D4`), so raw coolant from {low} to {high} leaves "
            "the latch unchanged.",
        ):
            with self.subTest(phrase=phrase[:40]):
                self.assertIn(phrase, self.published)
        self.assertEqual(rom[0x8E03], 106)

    def test_conditioner_neutralizes_without_the_operating_bit(self):
        rom = self.rom
        # FUN_000BDC66: mov.b @(3,r6),r0 with r6 = 0xFFFF2468; tst #0x40.
        self.assertEqual(_mov_l_literal(rom, 0xBDCDA) + 3, 0xFFFF246B)
        self.assertEqual(_u16(rom, 0xBDCDC), 0x8463)
        self.assertEqual(_u16(rom, 0xBDCDE), 0xC840)
        self.assertEqual(_u16(rom, 0xBDCE0) >> 8, 0x8B)
        self.assertEqual(_conditional_target(rom, 0xBDCE0), 0xBDD80)
        # 0xFFFF248B bit 1 clear takes the neutral path.
        self.assertEqual(_mov_l_literal(rom, 0xBDCE2) + 0x23, 0xFFFF248B)
        self.assertEqual(_u16(rom, 0xBDCE4), 0xE023)
        self.assertEqual(_u16(rom, 0xBDCE8), 0xC802)
        self.assertEqual(_u16(rom, 0xBDCEA) >> 8, 0x89)
        self.assertEqual(_conditional_target(rom, 0xBDCEA), 0xBDCF6)
        # IOLID 0x19 active-test bit 0xFFFF41FA bit 0 continues to the map.
        self.assertEqual(_mov_l_literal(rom, 0xBDCEC) + 0x51, 0xFFFF41FA)
        self.assertEqual(_u16(rom, 0xBDCEE), 0xE051)
        self.assertEqual(_u16(rom, 0xBDCF2), 0xC801)
        self.assertEqual(_u16(rom, 0xBDCF4) >> 8, 0x8B)
        self.assertEqual(_conditional_target(rom, 0xBDCF4), 0xBDD80)
        # bra 0xBDEC8 with mov #0x80,r0 in the delay slot; 0xBDECA stores it.
        self.assertEqual(_bra_target(rom, 0xBDCF6), 0xBDEC8)
        self.assertEqual(_u16(rom, 0xBDCF8), 0xE080)
        self.assertEqual(_mov_l_literal(rom, 0xBDEC8) + 2, 0xFFFF2326)
        self.assertEqual(_u16(rom, 0xBDECA), 0x8052)
        for phrase in (
            "`FUN 000BDC66` tests the operating bit at `0xBDCDE`.",
            "While it is clear, the function stores neutral `0x80` to "
            "`0xFFFF2326` through `0xBDCF6` and `0xBDECA` unless `0xFFFF248B` bit "
            "1 and IOLID `0x19` active-test bit `0xFFFF41FA` bit 0 are both set.",
        ):
            with self.subTest(phrase=phrase[:40]):
                self.assertIn(phrase, self.published)

    def test_published_rom_constants_match_the_stock_bytes(self):
        checked = 0
        for heading in (
            "### Intake idle source `0xFFFF1553`",
            "### Intake operating bit `0xFFFF246B` bit 6",
        ):
            section = " ".join(_section(self.source, heading).split())
            for width, address, value in re.findall(
                r"ROM(8|16)\[0x([0-9A-F]+)\] = (0x[0-9A-F]+|\d+)", section
            ):
                address = int(address, 16)
                size = int(width) // 8
                with self.subTest(address=hex(address)):
                    self.assertEqual(
                        int.from_bytes(self.rom[address : address + size], "big"),
                        int(value, 0),
                    )
                checked += 1
        self.assertGreaterEqual(checked, 15)

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
