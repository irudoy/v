import copy
import unittest

from tools.can_dashboard import descriptions, presentation
from tools.logs import can_telemetry


def tuning_profile():
    _document, profiles = can_telemetry.load_schema(
        can_telemetry.DEFAULT_SCHEMA
    )
    return copy.deepcopy(profiles["tuning"])


def field_of(profile, name):
    return next(
        field
        for field in can_telemetry.profile_fields(profile)
        if field["name"] == name
    )


def panel_rows(layout):
    return {
        title: metrics
        for _tab, panels in layout.tabs
        for title, metrics in panels
    }


class PresentationTest(unittest.TestCase):
    def test_every_panel_field_takes_its_place_in_order(self):
        profile = tuning_profile()
        rows = panel_rows(presentation.build(profile))
        placed = 0
        for field in can_telemetry.profile_fields(profile):
            dashboard = field["dashboard"]
            if "panel" not in dashboard:
                continue
            placed += 1
            key = can_telemetry.engineering_key(field["name"])
            with self.subTest(field=field["name"]):
                labels = {
                    metric.key: metric.label
                    for metric in rows[dashboard["panel"]]
                }
                self.assertEqual(
                    labels[key],
                    dashboard.get("panel_label", dashboard["label"]),
                )
        self.assertGreater(placed, 50)
        context = [
            metric.key for metric in rows["Temperatures and context"]
        ]
        # Code metrics stand at their orders among the fields of a panel.
        self.assertLess(
            context.index("oil_temperature_did_source"),
            context.index("stock_rpm"),
        )
        self.assertLess(
            context.index("selected_map"),
            context.index("rolling_launch_phase"),
        )
        self.assertLess(
            context.index("rolling_launch_abort_reason"),
            context.index("ascd_button"),
        )

    def test_a_metric_shows_the_display_unit_and_digits_of_its_field(self):
        profile = tuning_profile()
        rows = panel_rows(presentation.build(profile))
        metrics = {
            metric.key: metric
            for panel in rows.values()
            for metric in panel
        }
        self.assertEqual(metrics["alpha_n_flow"].unit, "%*")
        self.assertEqual(metrics["iat"].unit, "degC")
        self.assertEqual(metrics["knock_margin_min_ch1"].unit, "cnt")
        self.assertEqual(metrics["profile_crc16"].unit, "")
        self.assertTrue(metrics["profile_crc16"].hexadecimal)
        self.assertEqual(
            metrics["bfs"].digits,
            field_of(profile, "bfs_raw")["dashboard"]["digits"],
        )

    def test_hero_cards_show_the_field_label_in_capitals(self):
        hero = {
            metric.key: metric
            for metric in presentation.build(tuning_profile()).hero
        }
        self.assertEqual(hero["coolant"].label, "COOLANT")
        self.assertEqual(hero["coolant"].unit, "degC")
        self.assertEqual(hero["rpm"].label, "ENGINE SPEED")

    def test_the_default_hero_row_leaves_the_optional_cards_out(self):
        layout = presentation.build(tuning_profile())
        self.assertEqual(
            layout.default_hero,
            (
                "rpm",
                "vehicle_speed_kmh",
                "calculated_load",
                "final_timing",
                "maf_total",
                "injection_average_ms",
                "coolant",
            ),
        )
        self.assertEqual(
            presentation.default().default_hero, layout.default_hero
        )

    def test_a_field_describes_itself_and_a_code_metric_in_code(self):
        profile = tuning_profile()
        layout = presentation.build(profile)
        self.assertEqual(
            layout.describe("coolant"),
            field_of(profile, "coolant_raw")["dashboard"]["description"],
        )
        self.assertEqual(
            layout.describe("selected_map"),
            descriptions.describe("selected_map"),
        )
        self.assertTrue(layout.describe("selected_map"))
        self.assertEqual(layout.describe("unknown"), "")

    def test_a_field_without_a_presentation_stays_out(self):
        profile = tuning_profile()
        del field_of(profile, "coolant_raw")["dashboard"]
        del field_of(profile, "iat_raw")["dashboard"]
        layout = presentation.build(profile)
        self.assertNotIn("coolant", [metric.key for metric in layout.hero])
        self.assertNotIn(
            "iat",
            [
                metric.key
                for metric in panel_rows(layout)["Temperatures and context"]
            ],
        )
        self.assertEqual(layout.describe("coolant"), "")

    def test_a_panel_that_no_tab_shows_is_refused(self):
        profile = tuning_profile()
        field_of(profile, "iat_raw")["dashboard"]["panel"] = "Elsewhere"
        with self.assertRaisesRegex(ValueError, "no tab shows panel"):
            presentation.build(profile)

    def test_two_metrics_at_one_order_are_refused(self):
        profile = tuning_profile()
        # Order 40 of the context panel holds the stock engine speed.
        field_of(profile, "iat_raw")["dashboard"]["order"] = 40
        with self.assertRaisesRegex(ValueError, "repeats an order"):
            presentation.build(profile)


if __name__ == "__main__":
    unittest.main()
