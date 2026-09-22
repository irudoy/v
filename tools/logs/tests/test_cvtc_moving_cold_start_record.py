import csv
from fractions import Fraction
import hashlib
from pathlib import Path
import re
import tomllib
import unittest

from tools.logs import cvtc_intake_state_audit as state_audit
from tools.logs import cvtc_target_audit, mlg_relation_audit


ROOT = Path(__file__).resolve().parents[3]
HARDWARE_RESULTS = ROOT / "patches" / "hardware-results.toml"
PROFILE = ROOT / "patches" / "can-telemetry-profile.toml"
CVTC = ROOT / "defs" / "JK08A.cvtc.md"
FUNCS = ROOT / "defs" / "JK08A.funcs.csv"
STOCK_ROM = ROOT / "rom-images" / "23710-JK08A" / "1JK08A-20260726-stock.bin"
LOGS = ROOT / "tmp" / "logs-09-22"
IMAGE = ROOT / "tmp" / "1JK08A-tune-v3-1.bin"
KEY = "can_telemetry.cvtc_cold_start_2026_09_22"
STATIONARY_KEY = "can_telemetry.cvtc_cold_start_2026_09_21"
SESSION = "schema2_profile5_drive_2026_09_22"
CAPTURES = "schema2_profile5_captures_2026_09_22"
# FUN_000BD170 through FUN_000BDF5C occupy 0xBD170..0xBE121; the next
# function starts at 0xBE122, and their last literal ends at 0xBE217.
CODE_START = 0xBD170
CODE_END = 0xBE122
CODE_SPAN_END = 0xBE218
CLASS_LABELS = {
    "start_unresolved": "before the first rise, decided by the start terms",
    "neutral_target_0x80": "operating bit clear, target `0x80`",
    "neutral_target_active": "operating bit clear, target active",
    "idle_exact": "idle source, exact",
    "idle_rise": "idle source, on a rise",
    "idle_other": "idle source, other",
    "map_exact_active": "map path, exact and active",
    "map_exact_0x80": "map path, exact at `0x80`",
    "map_within_3": "map path, within 3",
    "map_target_0x80": "map path, target `0x80`",
    "map_other": "map path, other",
}
DISCRIMINATION_FIELDS = ("selected", "neutral", "alternate", "main", "other")
TRACE_ROWS = (
    ("intake", "cold", "coolant-selected map",
     "intake_cold_direct_exact_count", "cold_comparison_count"),
    ("intake", "cold", "coolant-selected map, active",
     "intake_cold_active_exact_count", "intake_cold_active_comparison_count"),
    ("intake", "cold", "coolant-selected map, cold-dependent",
     "intake_cold_cold_dependent_exact_count",
     "intake_cold_cold_dependent_comparison_count"),
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


def _lookup(registry, dotted):
    node = registry
    for part in dotted.split("."):
        node = node[part]
    return node


def _field(name):
    with PROFILE.open("rb") as source:
        profile = tomllib.load(source)
    (field,) = [row for row in profile["field"] if row["name"] == name]
    return field


def _counts(errors):
    return (0, 0, 0) if errors is None else (
        errors.comparisons, errors.exact, errors.within_one
    )


def _trace_values(source):
    """Return the record keys that cvtc_target_audit.py reproduces."""
    values = {}
    corrections = 0
    for target in ("intake", "exhaust"):
        for band in cvtc_target_audit.COOLANT_BANDS:
            output = cvtc_target_audit.audit_trace(
                source,
                calibration_image=IMAGE,
                target=target,
                coolant_bands=(band,),
                source_lags=(1,),
            )
            (alignment,) = output.alignments
            corrections += alignment.correction_active_count
            stable = {
                item.unchanged_source_cycles: item.errors
                for item in alignment.stable_active
            }
            direct = (
                alignment.selected_to_reference_a
                if target == "intake"
                else alignment.selected_to_reference_b
            )
            prefix = f"{target}_{band}"
            if target == "intake":
                values[f"{band}_comparison_count"] = alignment.comparisons
                values["coolant_raw_range"] = list(output.coolant_raw_range)
                values["coolant_thresholds"] = [
                    output.cold_threshold,
                    output.warm_threshold,
                ]
                values["record_count"] = output.source_records
                values["bridge_record_count"] = output.bridge_records
                values["analyzed_snapshot_count"] = output.analyzed_snapshots
            values[f"{prefix}_direct_exact_count"] = _counts(direct)[1]
            values[f"{prefix}_neutralization_sample_count"] = (
                alignment.conditioned_neutralization_count
            )
            pairs = {
                "without_neutralization": alignment.without_conditioned_neutralization,
                "active": alignment.active_to_active,
                "cold_dependent": alignment.cold_dependent_active_to_active,
                "alternate_active": alignment.alternate_source_active_to_active,
                "stable_active_16": stable.get(16),
            }
            for name, errors in pairs.items():
                comparisons, exact, within_one = _counts(errors)
                values[f"{prefix}_{name}_comparison_count"] = comparisons
                values[f"{prefix}_{name}_exact_count"] = exact
                values[f"{prefix}_{name}_within_one_count"] = within_one
            alternate = alignment.alternate_source_to_reference
            if alternate is not None:
                values[f"{prefix}_alternate_exact_count"] = alternate.exact
                values[f"{prefix}_alternate_within_two_count"] = alternate.within_two
    values["correction_active_count"] = corrections
    return values


class CvtcMovingColdStartRecordTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with HARDWARE_RESULTS.open("rb") as source:
            cls.registry = tomllib.load(source)
        section, name = KEY.split(".")
        cls.result = cls.registry[section][name]
        cls.stationary = _lookup(cls.registry, STATIONARY_KEY)
        cls.session = cls.registry[section][SESSION]
        cls.captures = {
            row["capture_name"]: row for row in cls.registry[section][CAPTURES]
        }
        cls.published = " ".join(CVTC.read_text(encoding="utf-8").split())

    def classes(self, key="cold_state_class_counts"):
        return dict(zip(self.result["state_class_names"], self.result[key]))

    def test_record_belongs_to_the_registered_drive(self):
        result = self.result
        self.assertTrue((ROOT / result["tool"]).is_file())
        self.assertTrue((ROOT / result["state_tool"]).is_file())
        self.assertEqual(self.session["capture_registry"], f"can_telemetry.{CAPTURES}")
        self.assertEqual(result["recorded_on"], self.session["recorded_on"])
        self.assertEqual(result["image_sha256"], self.session["image_sha256"])
        self.assertEqual(result["image_sha256"], self.stationary["image_sha256"])
        capture = self.captures[result["capture_name"]]
        self.assertEqual(result["capture_sha256"], capture["capture_sha256"])
        self.assertEqual(result["record_count"], capture["record_count"])
        self.assertEqual(result["bridge_record_count"], 0)
        self.assertEqual(result["analyzed_snapshot_count"], result["record_count"])
        self.assertEqual(result["map_slot"], 1)
        self.assertEqual(result["source_lag"], self.stationary["source_lag"])

    def test_bands_follow_the_coolant_thresholds(self):
        result = self.result
        self.assertEqual(result["coolant_thresholds"], self.stationary["coolant_thresholds"])
        cold_threshold, warm_threshold = result["coolant_thresholds"]
        low, high = result["coolant_raw_range"]
        self.assertEqual(result["cold_band_coolant_raw"], [low, cold_threshold])
        self.assertEqual(
            result["blend_band_coolant_raw"], [cold_threshold + 1, warm_threshold]
        )
        self.assertEqual(result["warm_band_coolant_raw"], [warm_threshold + 1, high])
        spans = [
            result[f"{band}_band_elapsed_seconds"]
            for band in cvtc_target_audit.COOLANT_BANDS
        ]
        self.assertEqual(spans[0][0], 0.0)
        for (start, end), (next_start, _next_end) in zip(spans, spans[1:]):
            self.assertLessEqual(start, end)
            self.assertLess(end, next_start)
        self.assertLess(spans[-1][1], self.captures[result["capture_name"]]["span_seconds"])
        compared = sum(
            result[f"{band}_comparison_count"]
            for band in cvtc_target_audit.COOLANT_BANDS
        )
        self.assertLessEqual(
            compared, result["analyzed_snapshot_count"] - result["source_lag"]
        )
        self.assertGreater(result["cold_band_vehicle_speed_kmh_max"], 0.0)
        self.assertEqual(result["correction_active_count"], 0)
        # The cold band lies inside the coolant range that keeps the latch.
        self.assertGreaterEqual(low, state_audit.LATCH_CLEAR_COOLANT)
        self.assertLess(cold_threshold, state_audit.LATCH_SET_COOLANT)

    def test_counts_are_consistent(self):
        result = self.result
        for _target, _band, _check, exact, comparisons in TRACE_ROWS:
            if comparisons in result:
                with self.subTest(exact=exact):
                    self.assertLessEqual(result[exact], result[comparisons])
        self.assertLessEqual(
            result["intake_cold_cold_dependent_comparison_count"],
            result["intake_cold_active_comparison_count"],
        )
        self.assertLessEqual(
            result["intake_blend_cold_dependent_comparison_count"],
            result["intake_blend_active_comparison_count"],
        )
        self.assertLessEqual(
            result["intake_blend_cold_dependent_exact_count"],
            result["intake_blend_cold_dependent_within_one_count"],
        )
        self.assertLessEqual(
            result["intake_cold_alternate_exact_count"],
            result["intake_cold_alternate_within_two_count"],
        )
        self.assertEqual(
            result["exhaust_cold_exact_count"], result["cold_comparison_count"]
        )
        self.assertEqual(result["exhaust_blend_active_comparison_count"], 0)
        self.assertEqual(
            result["exhaust_blend_neutralization_sample_count"]
            + result["exhaust_blend_without_neutralization_exact_count"],
            result["blend_comparison_count"],
        )

    def test_state_replay_is_consistent(self):
        result = self.result
        self.assertEqual(result["state_class_names"], list(state_audit.CLASSES))
        self.assertEqual(list(CLASS_LABELS), list(state_audit.CLASSES))
        for key in (
            "cold_state_class_counts",
            "cold_state_class_counts_latch_clear",
            "blend_state_class_counts",
            "warm_state_class_counts",
        ):
            band = key.split("_", 1)[0]
            with self.subTest(key=key):
                self.assertEqual(
                    sum(result[key]), result[f"{band}_comparison_count"]
                )
        self.assertTrue(result["blend_and_warm_state_latch_independent"])
        self.assertEqual(result["state_latch_initial"], "set")
        latched = self.classes()
        clear = self.classes("cold_state_class_counts_latch_clear")
        # The unobservable start terms and the idle-source path do not depend
        # on the latch; without it the cold band has no map path.
        for name in ("start_unresolved", "idle_exact", "idle_rise", "idle_other"):
            self.assertEqual(latched[name], clear[name])
        self.assertEqual({clear[name] for name in clear if name.startswith("map_")}, {0})
        self.assertEqual(
            result["cold_state_predicted_neutral_count"],
            latched["neutral_target_0x80"] + latched["neutral_target_active"],
        )
        self.assertEqual(
            result["cold_state_predicted_neutral_target_0x80_count"],
            latched["neutral_target_0x80"],
        )
        self.assertLessEqual(
            result["cold_state_neutralization_predicted_count"],
            result["intake_cold_neutralization_sample_count"],
        )
        self.assertEqual(
            result["cold_state_map_active_exact_count"], latched["map_exact_active"]
        )
        self.assertLessEqual(
            result["cold_state_map_cold_dependent_comparison_count"],
            result["cold_state_map_active_comparison_count"],
        )
        self.assertLessEqual(
            result["cold_state_map_cold_dependent_exact_count"],
            result["cold_state_map_cold_dependent_comparison_count"],
        )
        self.assertEqual(result["cold_state_map_cold_dependent_main_exact_count"], 0)
        self.assertEqual(
            len(result["cold_state_neutral_idle_blocker_names"]),
            len(result["cold_state_neutral_idle_blocker_counts"]),
        )
        self.assertLessEqual(
            sum(result["cold_state_neutral_idle_blocker_counts"]),
            result["cold_state_predicted_neutral_count"],
        )
        differ = dict(
            zip(result["state_class_names"], result["cold_differ_from_both_class_counts"])
        )
        self.assertEqual(sum(differ.values()), result["cold_differ_from_both_count"])
        for name, count in differ.items():
            self.assertLessEqual(count, latched[name])
        self.assertEqual(differ["idle_exact"], 0)
        self.assertEqual(differ["map_exact_active"] + differ["map_exact_0x80"], 0)

        middle = result["state_rearm_sweep_snapshots"].index(
            result["state_rearm_snapshots"]
        )
        self.assertEqual(middle, 1)
        self.assertEqual(
            result["cold_state_idle_other_by_rearm"][middle], latched["idle_other"]
        )
        self.assertEqual(
            result["cold_state_neutral_target_active_by_rearm"][middle],
            latched["neutral_target_active"],
        )
        self.assertEqual(
            result["state_app1_sweep"][0], result["state_app1_released_max"]
        )
        for key, value in (
            ("cold_state_map_target_0x80_by_app1", latched["map_target_0x80"]),
            (
                "cold_state_neutral_target_active_by_app1",
                latched["neutral_target_active"],
            ),
            (
                "cold_state_map_cold_dependent_comparison_by_app1",
                result["cold_state_map_cold_dependent_comparison_count"],
            ),
            (
                "cold_state_map_cold_dependent_exact_by_app1",
                result["cold_state_map_cold_dependent_exact_count"],
            ),
        ):
            with self.subTest(key=key):
                self.assertEqual(len(result[key]), len(result["state_app1_sweep"]))
                self.assertEqual(result[key][0], value)

        for band in ("cold", "blend"):
            counts = [
                result[f"{band}_discriminating_{field}_count"]
                for field in DISCRIMINATION_FIELDS
            ]
            comparisons = result[f"{band}_discriminating_comparison_count"]
            with self.subTest(band=band):
                self.assertEqual(sum(counts), comparisons)
                self.assertLessEqual(comparisons, result[f"{band}_comparison_count"])
        selected = result["cold_discriminating_selected_count"]
        for field in ("moving", "pedal_applied", "off_cell"):
            self.assertLessEqual(
                result[f"cold_discriminating_selected_{field}_count"], selected
            )
        self.assertEqual(result["cold_discriminating_main_count"], 0)

    def test_published_figures_match_the_registry(self):
        result = self.result
        text = self.published
        self.assertIn(f"`{KEY}`", text)
        self.assertIn(f"`{result['capture_name']}`", text)
        self.assertIn(f"`{result['capture_sha256']}`", text)
        self.assertIn(
            f"holds {result['record_count']:,} records, all of them snapshots", text
        )
        rpm = _field("rpm_raw")
        scale = re.fullmatch(r"raw \* ([0-9.]+) RPM", rpm["scale"])
        first_rpm = Fraction(scale.group(1)) * result["first_record_rpm_raw"]
        self.assertEqual(first_rpm.denominator, 1)
        self.assertIn(
            f"its first snapshot carries {int(first_rpm):,} RPM "
            f"(`0x{rpm['source']:08X}` = {result['first_record_rpm_raw']})",
            text,
        )
        low, high = result["coolant_raw_range"]
        self.assertIn(f"Coolant rises from raw {low} to {high}", text)
        self.assertIn(
            f"Its bytes `0x{CODE_START:X}..0x{CODE_SPAN_END - 1:X}`, which hold "
            "`FUN 000BD170` through `FUN 000BDF5C` and every literal these "
            "functions load, equal stock",
            text,
        )
        self.assertIn(
            f"stock bytes 0x{CODE_START:X}..0x{CODE_SPAN_END - 1:X}, which hold "
            "FUN 000BD170 through FUN 000BDF5C and every literal these functions "
            "load",
            result["calibration_basis"],
        )
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

        counts = dict(result)
        counts["exhaust_blend_without_neutralization_comparison_count"] = (
            result["blend_comparison_count"]
            - result["exhaust_blend_neutralization_sample_count"]
        )
        for target, band, check, exact, comparisons in TRACE_ROWS:
            row = (
                f"| {target} | {band} | {check} | "
                f"{counts[exact]:,} / {counts[comparisons]:,} |"
            )
            with self.subTest(row=row):
                self.assertIn(row, text)

        for band in ("cold", "blend"):
            row = (
                f"| `{result['capture_name']}` | {band} | "
                f"{result[f'{band}_discriminating_comparison_count']:,} | "
                + " | ".join(
                    f"{result[f'{band}_discriminating_{field}_count']:,}"
                    for field in DISCRIMINATION_FIELDS
                )
                + " |"
            )
            with self.subTest(row=row):
                self.assertIn(row, text)
        self.assertIn(
            f"Of the {result['cold_discriminating_selected_count']:,} cold-band "
            f"targets of `{result['capture_name']}` that carry the "
            "coolant-selected byte, "
            f"{result['cold_discriminating_selected_moving_count']:,} are moving, "
            f"{result['cold_discriminating_selected_pedal_applied_count']:,} have "
            f"APP1 raw above {result['state_app1_released_max']}, and "
            f"{result['cold_discriminating_selected_off_cell_count']:,} carry a "
            "byte that no cell of `0xB53A` holds",
            text,
        )

    def test_published_state_replay_matches_the_registry(self):
        result = self.result
        text = self.published
        latched = self.classes()
        clear = self.classes("cold_state_class_counts_latch_clear")
        self.assertIn(
            "The replay takes `CLSD THL POS` as APP1 raw at most "
            f"{result['state_app1_released_max']}",
            text,
        )
        self.assertIn(
            f"uses a re-arm wait of {result['state_rearm_snapshots']} snapshots",
            text,
        )
        for name, label in CLASS_LABELS.items():
            row = f"| {label} | {latched[name]:,} | {clear[name]:,} |"
            with self.subTest(row=row):
                self.assertIn(row, text)
        self.assertIn(
            "With the latch clear the replay puts "
            f"{clear['neutral_target_active']:,} cold-band comparisons whose "
            "target is active on the neutral path, against "
            f"{latched['neutral_target_active']:,} with the latch set.",
            text,
        )
        cold_low, cold_high = result["cold_band_coolant_raw"]
        self.assertIn(
            f"The cold band holds raw coolant {cold_low}..{cold_high}, inside the "
            "range in which `FUN 000BD20A` leaves the latch unchanged, so the "
            "latch was set when the recording started.",
            text,
        )
        self.assertIn(
            f"inside the {state_audit.LATCH_CLEAR_COOLANT}.."
            f"{state_audit.LATCH_SET_COOLANT - 1} range in which FUN 000BD20A "
            "leaves the latch unchanged",
            result["state_latch_basis"],
        )
        self.assertIn(
            "With the latch set, "
            f"{result['cold_state_map_cold_dependent_exact_count']:,} of the "
            f"{result['cold_state_map_cold_dependent_comparison_count']:,} "
            "cold-dependent cold-band comparisons on the map path are exact, and "
            "none equals the main-surface byte.",
            text,
        )
        differ = dict(
            zip(result["state_class_names"], result["cold_differ_from_both_class_counts"])
        )
        neutral = differ["neutral_target_0x80"] + differ["neutral_target_active"]
        self.assertEqual(
            neutral
            + differ["idle_rise"]
            + differ["start_unresolved"]
            + differ["map_within_3"]
            + differ["map_target_0x80"]
            + differ["idle_other"],
            result["cold_differ_from_both_count"],
        )
        self.assertEqual(differ["idle_other"], 1)
        self.assertIn(
            f"Of the {result['cold_differ_from_both_count']:,} cold-band "
            "comparisons that differ from both replayed bytes, the replay places "
            f"{neutral:,} on the neutral path and {differ['idle_rise']:,} on a "
            f"rise; {differ['start_unresolved']:,} precede the first rise, "
            f"{differ['map_within_3']:,} lie within 3 counts of the "
            f"coolant-selected byte, {differ['map_target_0x80']:,} carry `0x80` on "
            f"the map path, and {differ['idle_other']:,} lies on the idle-source "
            "path outside a rise.",
            text,
        )
        rearm = result["state_rearm_sweep_snapshots"]
        idle_other = result["cold_state_idle_other_by_rearm"]
        active = result["cold_state_neutral_target_active_by_rearm"]
        self.assertEqual(idle_other[1], idle_other[2])
        self.assertIn(
            f"With a re-arm wait of {rearm[0]} snapshots, {idle_other[0]} "
            "idle-source targets outside a rise differ from the replayed byte, "
            f"against {idle_other[1]} at {rearm[1]} and {rearm[2]}; at "
            f"{rearm[2]}, {active[2]} neutral-path targets are active.",
            text,
        )
        app1 = result["state_app1_sweep"]
        map_0x80 = result["cold_state_map_target_0x80_by_app1"]
        neutral_active = result["cold_state_neutral_target_active_by_app1"]
        self.assertIn(
            f"As the APP1 bound rises from {app1[0]} to {app1[1]}, the map-path "
            f"targets at `0x80` fall from {map_0x80[0]:,} to {map_0x80[1]:,} and "
            f"the neutral-path active targets rise from {neutral_active[0]:,} to "
            f"{neutral_active[1]:,}.",
            text,
        )
        self.assertIn(
            "The blend and warm bands are identical for both latch states.", text
        )
        cold_and_blend = (
            result["cold_comparison_count"] + result["blend_comparison_count"]
        )
        self.assertIn(
            f"stays `0x80` in all {cold_and_blend:,} cold- and blend-band "
            f"comparisons, {result['exhaust_blend_neutralization_sample_count']:,} "
            "of them against a blend value other than `0x80`",
            text,
        )

    def test_record_prose_matches_the_counts(self):
        result = self.result
        latched = self.classes()
        differ = dict(
            zip(result["state_class_names"], result["cold_differ_from_both_class_counts"])
        )
        neutral = differ["neutral_target_0x80"] + differ["neutral_target_active"]
        for phrase in (
            f"{result['cold_discriminating_selected_count']:,} cold-band "
            "comparisons whose coolant-selected byte differs from 0x80, the "
            "main-surface byte, and the replayed 0xFFFF1553 byte carry that byte, "
            f"{result['cold_discriminating_selected_off_cell_count']:,} of them a "
            "byte that no cell of the surface holds, and none carries the "
            "main-surface byte",
            f"puts {result['cold_state_map_cold_dependent_comparison_count']:,} "
            "cold-dependent comparisons on the map path, "
            f"{result['cold_state_map_cold_dependent_exact_count']:,} of them exact "
            "and none equal to the main-surface byte, predicts neutral 0x80 for "
            f"{result['cold_state_predicted_neutral_count']:,} comparisons, "
            f"{result['cold_state_predicted_neutral_target_0x80_count']:,} of them "
            f"at 0x80, and places {neutral:,} of the "
            f"{result['cold_differ_from_both_count']:,} cold-band comparisons that "
            "differ from both replayed bytes on the neutral path and "
            f"{differ['idle_rise']:,} on a rise",
            "the blend band reproduces the intake blend in "
            f"{result['intake_blend_cold_dependent_exact_count']:,} of "
            f"{result['intake_blend_cold_dependent_comparison_count']:,} "
            "cold-dependent comparisons",
        ):
            with self.subTest(phrase=phrase[:40]):
                self.assertIn(phrase, result["result"])
        boundary = result["evidence_boundary"]
        map_0x80 = result["cold_state_map_target_0x80_by_app1"]
        neutral_active = result["cold_state_neutral_target_active_by_app1"]
        for phrase in (
            "the replay takes CLSD THL POS as APP1 raw at most "
            f"{result['state_app1_released_max']}",
            f"uses a re-arm wait of {result['state_rearm_snapshots']} snapshots",
            f"the {latched['start_unresolved']:,} comparisons before the first "
            "rise depend on the start delay",
            f"{latched['map_within_3']:,} map-path comparisons lie within 3 counts "
            "of the selected byte",
            f"the {map_0x80[0]:,} map-path comparisons at 0x80 fall to "
            f"{map_0x80[1]:,} as the APP1 bound rises to "
            f"{result['state_app1_sweep'][1]} while the neutral-path comparisons "
            f"with an active target rise from {neutral_active[0]:,} to "
            f"{neutral_active[1]:,}",
        ):
            with self.subTest(phrase=phrase[:40]):
                self.assertIn(phrase, boundary)
        self.assertIn(
            f"with the latch clear the replay puts "
            f"{self.classes('cold_state_class_counts_latch_clear')['neutral_target_active']:,} "
            "cold-band comparisons whose target is active on the neutral path, "
            f"against {latched['neutral_target_active']:,} with the latch set",
            result["state_latch_basis"],
        )

    def test_code_span_holds_the_functions_and_their_literals(self):
        rom = STOCK_ROM.read_bytes()
        with FUNCS.open(encoding="utf-8", newline="") as source:
            functions = {row["addr"]: row for row in csv.DictReader(source)}
        self.assertEqual(
            sorted(
                name
                for name in functions
                if CODE_START <= int(name, 16) < CODE_END
            ),
            [
                "000bd170",
                "000bd20a",
                "000bd9f0",
                "000bda64",
                "000bdb66",
                "000bdc66",
                "000bdf5c",
            ],
        )
        # FUN_000BD170 calls the function that follows the span's code.
        self.assertIn(f"trace:{CODE_END:08x}@", functions["000bd170"]["evidence"])
        # rts of FUN_000BDF5C and its delay slot precede the next function.
        self.assertEqual(int.from_bytes(rom[0xBE116:0xBE118], "big"), 0x000B)
        literal_end = 0
        for address in range(CODE_START, CODE_END, 2):
            opcode = int.from_bytes(rom[address : address + 2], "big")
            if opcode >> 12 == 0xD:
                literal = ((address + 4) & ~3) + (opcode & 0xFF) * 4 + 4
            elif opcode >> 12 == 0x9:
                literal = address + 4 + (opcode & 0xFF) * 2 + 2
            else:
                continue
            literal_end = max(literal_end, literal)
        self.assertEqual(literal_end, CODE_SPAN_END)

    @unittest.skipUnless(IMAGE.is_file(), "the tested image is local and untracked")
    def test_image_carries_the_stock_code_and_calibration(self):
        result = self.result
        image = IMAGE.read_bytes()
        rom = STOCK_ROM.read_bytes()
        self.assertEqual(hashlib.sha256(image).hexdigest(), result["image_sha256"])
        self.assertEqual(
            image[CODE_START:CODE_SPAN_END], rom[CODE_START:CODE_SPAN_END]
        )
        tested = state_audit.load_state_calibration(calibration_image=IMAGE)
        stock = state_audit.load_state_calibration()
        for field in tested.__dataclass_fields__:
            if field != "image_sha256":
                with self.subTest(field=field):
                    self.assertEqual(getattr(tested, field), getattr(stock, field))
        for address in (0x12EFE, 0x12F06):
            self.assertEqual(image[address : address + 8], rom[address : address + 8])
        for target in ("intake", "exhaust"):
            tested_surfaces = cvtc_target_audit.load_calibration(
                calibration_image=IMAGE, target=target
            )
            stock_surfaces = cvtc_target_audit.load_calibration(target=target)
            with self.subTest(target=target):
                self.assertEqual(tested_surfaces.cold, stock_surfaces.cold)
                if target == "intake":
                    self.assertEqual(
                        tested_surfaces.alternate_source,
                        stock_surfaces.alternate_source,
                    )
                    self.assertEqual(
                        {value for row in tested_surfaces.cold.table for value in row},
                        {128, 148},
                    )

    @unittest.skipUnless(
        LOGS.is_dir() and IMAGE.is_file(), "road captures are local and untracked"
    )
    def test_audits_reproduce_the_record(self):
        result = self.result
        source = LOGS / result["capture_name"]
        if not source.is_file():
            self.skipTest(f"missing capture: {source.name}")
        recording = mlg_relation_audit.read_recording(source)
        self.assertEqual(recording.sha256, result["capture_sha256"])
        self.assertEqual(set(recording.columns["ascd_button_raw"]), {0x20})
        self.assertEqual(
            recording.columns["rpm_raw"][0], result["first_record_rpm_raw"]
        )

        values = _trace_values(source)
        for key, value in values.items():
            if key in result:
                with self.subTest(key=key):
                    self.assertEqual(result[key], value)
        reproduced = set(values) & set(result)
        self.assertGreaterEqual(len(reproduced), 38)

        output = state_audit.audit_recording(
            source,
            calibration_image=IMAGE,
            app1_released_max=result["state_app1_released_max"],
            rearm_snapshots=result["state_rearm_snapshots"],
        )
        self.assertEqual(output.calibration_image_sha256, result["image_sha256"])
        self.assertEqual(output.records, result["record_count"])
        self.assertEqual(output.first_rpm_raw, result["first_record_rpm_raw"])
        self.assertEqual(
            output.calibration.rise_period, result["state_rise_period_snapshots"]
        )
        for span in output.bands:
            with self.subTest(band=span.band):
                self.assertEqual(span.comparisons, result[f"{span.band}_comparison_count"])
                self.assertEqual(
                    [round(value, 3) for value in span.elapsed_range],
                    result[f"{span.band}_band_elapsed_seconds"],
                )
                self.assertEqual(
                    list(span.coolant_raw_range), result[f"{span.band}_band_coolant_raw"]
                )
                self.assertEqual(
                    round(span.vehicle_speed_kmh_max, 2),
                    result[f"{span.band}_band_vehicle_speed_kmh_max"],
                )
        for item in output.discrimination:
            if item.band == "warm":
                self.assertEqual(item.comparisons, 0)
                continue
            fields = ("comparison", *DISCRIMINATION_FIELDS)
            if item.band == "cold":
                fields += ("selected_moving", "selected_pedal_applied", "selected_off_cell")
            for field in fields:
                attribute = "comparisons" if field == "comparison" else field
                with self.subTest(band=item.band, field=field):
                    self.assertEqual(
                        getattr(item, attribute),
                        result[f"{item.band}_discriminating_{field}_count"],
                    )
        replays = {replay.latch_initial: replay for replay in output.replays}
        self.assertEqual(set(replays), set(state_audit.LATCH_STATES))
        partitions = {
            latch: {partition.band: partition for partition in replay.partitions}
            for latch, replay in replays.items()
        }
        for latch, key in (
            ("set", "cold_state_class_counts"),
            ("clear", "cold_state_class_counts_latch_clear"),
        ):
            with self.subTest(latch=latch):
                self.assertEqual(
                    [count for _name, count in partitions[latch]["cold"].classes],
                    result[key],
                )
        for band in ("blend", "warm"):
            with self.subTest(band=band):
                self.assertEqual(partitions["set"][band], partitions["clear"][band])
                self.assertEqual(
                    [count for _name, count in partitions["set"][band].classes],
                    result[f"{band}_state_class_counts"],
                )
        cold = partitions["set"]["cold"]
        self.assertEqual(cold.predicted_neutral, result["cold_state_predicted_neutral_count"])
        self.assertEqual(
            cold.predicted_neutral_target_0x80,
            result["cold_state_predicted_neutral_target_0x80_count"],
        )
        self.assertEqual(
            cold.audit_neutralization, result["intake_cold_neutralization_sample_count"]
        )
        self.assertEqual(
            cold.audit_neutralization_predicted,
            result["cold_state_neutralization_predicted_count"],
        )
        self.assertEqual(cold.map_active, result["cold_state_map_active_comparison_count"])
        self.assertEqual(cold.map_active_exact, result["cold_state_map_active_exact_count"])
        self.assertEqual(
            cold.map_cold_dependent, result["cold_state_map_cold_dependent_comparison_count"]
        )
        self.assertEqual(
            cold.map_cold_dependent_exact,
            result["cold_state_map_cold_dependent_exact_count"],
        )
        self.assertEqual(
            cold.map_cold_dependent_main_exact,
            result["cold_state_map_cold_dependent_main_exact_count"],
        )
        self.assertEqual(
            [name for name, _count in cold.neutral_idle_blockers],
            result["cold_state_neutral_idle_blocker_names"],
        )
        self.assertEqual(
            [count for _name, count in cold.neutral_idle_blockers],
            result["cold_state_neutral_idle_blocker_counts"],
        )
        differ = dict(cold.differ_from_both)
        self.assertEqual(
            [differ.get(name, 0) for name in state_audit.CLASSES],
            result["cold_differ_from_both_class_counts"],
        )

        def cold_classes(**options):
            (replay,) = state_audit.audit_recording(
                source,
                calibration_image=IMAGE,
                latch_initial=("set",),
                coolant_bands=("cold",),
                **options,
            ).replays
            (partition,) = replay.partitions
            return partition, dict(partition.classes)

        # The base wait and APP1 bound reproduce the full replay above.
        for index, rearm in enumerate(result["state_rearm_sweep_snapshots"]):
            if rearm == result["state_rearm_snapshots"]:
                continue
            _partition, classes = cold_classes(
                app1_released_max=result["state_app1_released_max"],
                rearm_snapshots=rearm,
            )
            with self.subTest(rearm=rearm):
                self.assertEqual(
                    classes["idle_other"],
                    result["cold_state_idle_other_by_rearm"][index],
                )
                self.assertEqual(
                    classes["neutral_target_active"],
                    result["cold_state_neutral_target_active_by_rearm"][index],
                )
        for index, app1 in enumerate(result["state_app1_sweep"]):
            if app1 == result["state_app1_released_max"]:
                continue
            partition, classes = cold_classes(
                app1_released_max=app1,
                rearm_snapshots=result["state_rearm_snapshots"],
            )
            with self.subTest(app1=app1):
                self.assertEqual(
                    classes["map_target_0x80"],
                    result["cold_state_map_target_0x80_by_app1"][index],
                )
                self.assertEqual(
                    classes["neutral_target_active"],
                    result["cold_state_neutral_target_active_by_app1"][index],
                )
                self.assertEqual(
                    partition.map_cold_dependent,
                    result["cold_state_map_cold_dependent_comparison_by_app1"][index],
                )
                self.assertEqual(
                    partition.map_cold_dependent_exact,
                    result["cold_state_map_cold_dependent_exact_by_app1"][index],
                )


if __name__ == "__main__":
    unittest.main()
