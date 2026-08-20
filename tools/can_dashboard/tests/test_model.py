import unittest

from tools.can_dashboard import model


def feed_group(dashboard, group, base_time):
    snapshot = None
    for index, frame in enumerate(group):
        result = dashboard.process_frame(
            frame,
            now=base_time + index * 0.00025,
        )
        if result is not None:
            snapshot = result
    return snapshot


class DashboardModelTest(unittest.TestCase):
    def test_demo_groups_verify_schema_and_retain_contexts(self):
        generator = model.DemoGenerator()
        dashboard = model.DashboardModel("wide54", 0x6F0, 1)
        for tick in range(1, 9):
            timestamp = tick * model.BASE_TICK_SECONDS
            snapshot = feed_group(
                dashboard,
                generator.group(tick, timestamp),
                timestamp,
            )
            self.assertIsNotNone(snapshot)

        self.assertTrue(dashboard.schema_verified)
        self.assertEqual(dashboard.decoder.completed_groups, 8)
        self.assertEqual(dashboard.value("coolant_deg_c"), 90)
        self.assertEqual(dashboard.value("iat_deg_c"), 32)
        self.assertIn("stft_b1_percent", dashboard.engineering)
        self.assertIn("ltft_b1_percent", dashboard.engineering)
        self.assertIn("intake_cvtc_actual_b1_deg_ca", dashboard.engineering)
        self.assertIn("intake_cvtc_target_deg_ca", dashboard.engineering)
        self.assertIn("exhaust_cvtc_target_deg_ca", dashboard.engineering)
        self.assertIn("calculated_load_percent", dashboard.engineering)
        self.assertIn("app1_v", dashboard.engineering)
        self.assertIn("tps_b1_v", dashboard.engineering)
        self.assertIn("oil_temperature_deg_c", dashboard.engineering)
        self.assertEqual(
            dashboard.value("knock_timing_state"),
            dashboard.raw["knock_timing_state_raw"] / 256,
        )
        self.assertEqual(dashboard.value("knock_surface_mode"), "HIGH OCTANE")
        self.assertEqual(dashboard.high_detonation_selected, 0)
        self.assertGreater(dashboard.value("stft_b1_percent"), -5)
        self.assertLess(dashboard.value("stft_b1_percent"), 5)
        self.assertGreater(dashboard.value("rpm"), 800)
        self.assertLess(dashboard.value("rpm"), 4_100)
        self.assertEqual(dashboard.missed_snapshots, 0)
        self.assertEqual(
            dashboard.value("intake_cvtc_target_deg_ca"),
            dashboard.raw["intake_cvtc_target_b1_raw"] * 0.5 - 64,
        )
        self.assertEqual(
            dashboard.value("exhaust_cvtc_target_deg_ca"),
            dashboard.raw["intake_cvtc_target_b2_raw"] * 0.5 - 64,
        )

    def test_hot_ignition_surface_selector_decodes_bit_6(self):
        generator = model.DemoGenerator()
        dashboard = model.DashboardModel("wide54", 0x6F0, 1)
        for tick in range(1, 5):
            feed_group(dashboard, generator.group(tick), tick * 0.01)

        group = list(generator.group(5))
        page = bytearray(group[4].data)
        page[5] = 0x40
        group[4] = model.FrameRecord(0x6F0, bytes(page))
        feed_group(dashboard, group, 0.05)

        self.assertEqual(
            dashboard.value("knock_surface_mode"),
            "HIGH DETONATION",
        )
        self.assertEqual(dashboard.high_detonation_selected, 1)

    def test_tick_loss_and_stock_context_are_visible(self):
        generator = model.DemoGenerator()
        dashboard = model.DashboardModel("wide54", 0x6F0, 1)
        feed_group(dashboard, generator.group(1), 1.0)
        feed_group(dashboard, generator.group(3), 1.02)
        self.assertEqual(dashboard.missed_snapshots, 1)

        for frame in generator.stock_context(10):
            dashboard.process_frame(frame, now=1.03)
        self.assertEqual(dashboard.gear, "D")
        self.assertEqual(dashboard.ascd_button, "RELEASE")
        self.assertIn(dashboard.dashboard_state, {"STOCK", "ASCD STATE 7"})
        self.assertIsNotNone(dashboard.stock_rpm)
        self.assertIsNotNone(dashboard.vehicle_speed_kmh)
        self.assertIsNone(dashboard.gps_lat)
        self.assertIsNone(dashboard.gps_lon)
        self.assertEqual(
            dashboard.gps_status,
            "not observed on primary CAN",
        )

    def test_target_vehicle_selector_button_and_speed_codes(self):
        dashboard = model.DashboardModel("wide54", 0x6F0, 1)
        for code, label in model.PRND_CODES.items():
            dashboard.process_frame(
                model.FrameRecord(model.PRND_ID, bytes((code, 0))),
                now=1.0,
            )
            self.assertEqual(dashboard.gear, label)

        button = bytearray(5)
        button[3] = 0x10
        dashboard.process_frame(
            model.FrameRecord(model.ASCD_BUTTON_ID, bytes(button)),
            now=1.1,
        )
        self.assertEqual(dashboard.ascd_button, "RES")

        speed = bytearray(8)
        speed[4:6] = (6854).to_bytes(2, "big")
        dashboard.process_frame(
            model.FrameRecord(model.VEHICLE_SPEED_ID, bytes(speed)),
            now=1.2,
        )
        self.assertEqual(dashboard.vehicle_speed_raw, 6854)
        self.assertEqual(dashboard.vehicle_speed_kmh, 68.54)

    def test_status_bits_and_decoder_errors_are_exposed(self):
        generator = model.DemoGenerator()
        dashboard = model.DashboardModel("wide54", 0x6F0, 1)
        group = list(generator.group(1))
        page = bytearray(group[3].data)
        page[7] = 0x09
        group[3] = model.FrameRecord(0x6F0, bytes(page))
        feed_group(dashboard, group, 2.0)
        self.assertTrue(dashboard.telemetry_status_flags["overrun_latched"])
        self.assertTrue(dashboard.telemetry_status_flags["preempted"])

        dashboard.process_frame(model.FrameRecord(0x6F0, bytes(7)), now=2.1)
        dashboard.process_frame(
            model.FrameRecord(0, bytes(), is_error_frame=True),
            now=2.2,
        )
        stats = dashboard.stats(2.2)
        self.assertGreaterEqual(stats.malformed_frames, 1)
        self.assertEqual(stats.error_frames, 1)

    def test_divisor_changes_expected_tick_step(self):
        generator = model.DemoGenerator()
        dashboard = model.DashboardModel("wide54", 0x6F0, 4)
        feed_group(dashboard, generator.group(4), 3.0)
        feed_group(dashboard, generator.group(8), 3.04)
        self.assertEqual(dashboard.missed_snapshots, 0)
        self.assertEqual(dashboard.unexpected_tick_steps, 0)

    def test_health_mismatch_disables_retained_engineering_values(self):
        generator = model.DemoGenerator()
        dashboard = model.DashboardModel("wide54", 0x6F0, 1)
        for tick in range(1, 5):
            feed_group(dashboard, generator.group(tick), 4.0 + tick * 0.01)
        self.assertTrue(dashboard.schema_verified)
        self.assertIsNotNone(dashboard.value("rpm"))

        bad = list(generator.group(8))
        health = bytearray(bad[7].data)
        health[5] ^= 1
        bad[7] = model.FrameRecord(0x6F0, bytes(health))
        self.assertIsNone(feed_group(dashboard, bad, 4.1))
        self.assertFalse(dashboard.schema_verified)
        self.assertIsNone(dashboard.value("rpm"))


if __name__ == "__main__":
    unittest.main()
