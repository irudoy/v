import json
from pathlib import Path
import tempfile
import unittest

from patches import rolling_launch
from tools.can_dashboard import model
from tools.logs import can_telemetry
from tools.logs import can_telemetry_schema


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
    def test_model_and_demo_share_an_external_rom_neutral_schema(self):
        document = json.loads(
            can_telemetry.DEFAULT_SCHEMA.read_text(encoding="utf-8")
        )
        profile = document["profiles"][0]
        profile["name"] = "portable"
        profile["id"] = 7
        portable_crc = can_telemetry_schema.profile_crc16(
            profile, document["protocol_version"]
        )
        profile["crc16_ccitt_false"] = f"0x{portable_crc:04X}"
        with tempfile.TemporaryDirectory() as directory:
            schema_path = Path(directory) / "portable-schema.json"
            schema_path.write_text(
                json.dumps(document), encoding="utf-8"
            )
            generator = model.DemoGenerator(
                profile="portable", schema_path=schema_path
            )
            dashboard = model.DashboardModel(
                "portable", 0x6F0, 1, schema_path
            )
            for tick in range(1, 5):
                feed_group(
                    dashboard,
                    generator.group(tick),
                    tick * model.BASE_TICK_SECONDS,
                )

        self.assertTrue(dashboard.schema_verified)
        self.assertEqual(dashboard.decoder.profile["name"], "portable")

    def test_demo_groups_verify_schema_and_retain_contexts(self):
        generator = model.DemoGenerator()
        dashboard = model.DashboardModel("tuning", 0x6F0, 1)
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
        self.assertIn("engine_torque_state_nm", dashboard.engineering)
        self.assertIn("battery_voltage_v", dashboard.engineering)
        self.assertIn("exhaust_cvtc_actual_b1_deg_ca", dashboard.engineering)
        self.assertEqual(
            dashboard.value("knock_timing_state"),
            dashboard.raw["knock_timing_state_raw"] / 256,
        )
        self.assertEqual(dashboard.value("knock_surface_mode"), "HIGH OCTANE")
        self.assertEqual(dashboard.high_detonation_selected, 0)
        self.assertGreater(dashboard.value("stft_b1_percent"), -5)
        self.assertLess(dashboard.value("stft_b1_percent"), 5)
        self.assertIsNone(dashboard.value("rpm"))
        self.assertEqual(dashboard.missed_snapshots, 0)
        self.assertEqual(
            dashboard.value("intake_cvtc_target_deg_ca"),
            dashboard.raw["intake_cvtc_target_raw"] * 0.5 - 64,
        )
        self.assertEqual(
            dashboard.value("exhaust_cvtc_target_deg_ca"),
            dashboard.raw["exhaust_cvtc_target_raw"] * 0.5 - 64,
        )

    def test_secondary_throttle_sensors_display_volts(self):
        generator = model.DemoGenerator()
        dashboard = model.DashboardModel("tuning", 0x6F0, 1)
        for tick in range(1, 65):
            feed_group(
                dashboard,
                generator.group(tick),
                tick * model.BASE_TICK_SECONDS,
            )
            if "secondary_tps_b2_v" in dashboard.engineering:
                break

        for bank in (1, 2):
            with self.subTest(bank=bank):
                raw = dashboard.raw[f"secondary_tps_b{bank}_raw"]
                self.assertLess(raw, 1024)
                self.assertAlmostEqual(
                    dashboard.value(f"secondary_tps_b{bank}_v"), raw / 200
                )

    def test_converted_fields_display_engineering_units(self):
        dashboard = model.DashboardModel("tuning", 0x6F0, 1)
        values = {
            "tick16": 1,
            "schema_verified": 1,
            "apc_command_raw": 90,
            "throttle_request_bounded_raw": 2565,
            "throttle_target_shared_raw": 26845,
            "throttle_target_channel_0_raw": 2143,
            "throttle_target_channel_1_raw": 2149,
            "front_af_sensor_b1_word_raw": 440,
            "front_af_sensor_b2_word_raw": 1013,
            "af_adjustment_b1_raw": -2,
            "af_adjustment_b2_raw": 165,
            "fuel_inhibit_mask": 0x15,
            "knock_channel_mask_latched": 0x2B,
        }
        dashboard.process_record(model.SnapshotRecord(0.0, values), now=0.0)

        expected = {
            "apc_command_deg": 20,
            "torque_request_nm": 256.5,
            "throttle_area_request_cm2": 21.476,
            "throttle_target_b1_percent": 2143 * 34285 / 1114112,
            "throttle_target_b2_percent": 2149 * 34285 / 1114112,
            "af_sensor_b1_v": 2.2,
            "af_sensor_b2_v": 5.065,
            "af_adjustment_b1": -0.004,
            "af_adjustment_b2": 0.33,
        }
        for key, value in expected.items():
            with self.subTest(key=key):
                self.assertAlmostEqual(dashboard.value(key), value)
        self.assertEqual(dashboard.value("fuel_inhibit_cylinders"), "cyl 1 3 5")
        self.assertEqual(dashboard.value("knock_channels_latched"), "ch 1 2 4 6")
        self.assertEqual(dashboard.raw["af_adjustment_b1_raw"], -2)

    def test_masks_name_their_members(self):
        self.assertEqual(model.inhibited_cylinders(0), "none")
        self.assertEqual(model.inhibited_cylinders(0x3F), "all")
        self.assertEqual(model.inhibited_cylinders(0x15), "cyl 1 3 5")
        self.assertEqual(model.inhibited_cylinders(0x20), "cyl 6")
        self.assertEqual(model.knock_channels(0), "none")
        self.assertEqual(model.knock_channels(0x2B), "ch 1 2 4 6")

    def test_mask_names_follow_the_profile_declarations(self):
        _document, profiles = can_telemetry.load_schema(
            can_telemetry.DEFAULT_SCHEMA
        )
        scales = {
            field["name"]: field["scale"]
            for field in profiles["tuning"]["fields"]
        }
        self.assertIn(
            "bit k inhibits injector output k, cylinder k + 1",
            scales["fuel_inhibit_mask"],
        )
        self.assertIn(
            "bit c - 1 is knock channel c",
            scales["knock_channel_mask_latched"],
        )

    def test_demo_af_adjustments_stay_inside_their_bounds(self):
        generator = model.DemoGenerator()
        dashboard = model.DashboardModel("tuning", 0x6F0, 1)
        seen = set()
        for tick in range(1, 400):
            feed_group(
                dashboard,
                generator.group(tick, tick * 0.05),
                tick * model.BASE_TICK_SECONDS,
            )
            for bank in (1, 2):
                value = dashboard.engineering.get(f"af_adjustment_b{bank}")
                if value is not None:
                    self.assertLessEqual(abs(value), 1.0)
                    seen.add(value < 0)
        self.assertEqual(seen, {False, True})

    def test_hot_ignition_surface_selector_decodes_bit_6(self):
        generator = model.DemoGenerator()
        dashboard = model.DashboardModel("tuning", 0x6F0, 1)
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

    def test_idle_knock_margin_keeps_the_last_evaluated_value(self):
        generator = model.DemoGenerator()
        dashboard = model.DashboardModel("tuning", 0x6F0, 1)
        channel_5, channel_6 = model.KNOCK_MARGIN_FIELDS[4:6]

        def feed(tick, margin_5, margin_6):
            group = list(generator.group(tick))
            page = bytearray(group[10].data)
            self.assertEqual(page[1], 4)
            page[4:6] = margin_5.to_bytes(2, "big", signed=True)
            page[6:8] = margin_6.to_bytes(2, "big", signed=True)
            group[10] = model.FrameRecord(0x6F0, bytes(page))
            return feed_group(
                dashboard, group, tick * model.BASE_TICK_SECONDS
            )

        for tick in range(1, 5):
            feed_group(
                dashboard,
                generator.group(tick),
                tick * model.BASE_TICK_SECONDS,
            )
        self.assertIsNotNone(feed(5, model.KNOCK_MARGIN_IDLE, -250))
        evaluated_at = dashboard.updated_at[channel_6]
        self.assertEqual(dashboard.raw[channel_6], -250)
        self.assertNotIn(channel_5, dashboard.raw)
        for tick in range(6, 10):
            feed_group(
                dashboard,
                generator.group(tick),
                tick * model.BASE_TICK_SECONDS,
            )
        snapshot = feed(10, model.KNOCK_MARGIN_IDLE, model.KNOCK_MARGIN_IDLE)

        self.assertEqual(snapshot.fields[channel_6], model.KNOCK_MARGIN_IDLE)
        self.assertEqual(dashboard.raw[channel_6], -250)
        self.assertEqual(dashboard.updated_at[channel_6], evaluated_at)
        self.assertNotIn(channel_5, dashboard.raw)
        self.assertEqual(dashboard.missed_snapshots, 0)

    def test_dashboard_state_names_every_produced_ascd_state(self):
        dashboard = model.DashboardModel("tuning", 0x6F0, 1)
        expected = {
            0x02: "STOCK",
            0x42: "ASCD STATE 4",
            0x52: "ASCD STATE 5",
            0x62: "ASCD STATE 6",
            0x72: "ASCD STATE 7",
            0x12: "0x12",
        }
        for value, label in expected.items():
            with self.subTest(value=hex(value)):
                dashboard.process_frame(
                    model.FrameRecord(
                        model.DASHBOARD_STATE_ID,
                        bytes([0, 0, 0, 0, 0, value, 0, 0]),
                        1.0,
                    ),
                    now=1.0,
                )
                self.assertEqual(dashboard.dashboard_state_raw, value)
                self.assertEqual(dashboard.dashboard_state, label)

    def test_tick_loss_and_stock_context_are_visible(self):
        generator = model.DemoGenerator()
        dashboard = model.DashboardModel("tuning", 0x6F0, 1)
        feed_group(dashboard, generator.group(1), 1.0)
        feed_group(dashboard, generator.group(3), 1.02)
        self.assertEqual(dashboard.missed_snapshots, 1)

        for frame in generator.stock_context(10):
            dashboard.process_frame(frame, now=1.03)
        self.assertEqual(dashboard.gear, "D")
        self.assertIn(dashboard.tcm_gear, model.TCM_GEARS)
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

    def test_producer_restart_keeps_the_feed_and_is_not_counted_as_loss(self):
        generator = model.DemoGenerator()
        dashboard = model.DashboardModel("tuning", 0x6F0, 1)
        feed_group(dashboard, generator.group(900), 1.0)
        feed_group(dashboard, generator.group(901), 1.01)
        feed_group(dashboard, generator.group(1), 70.0)
        feed_group(dashboard, generator.group(2), 70.01)
        self.assertEqual(dashboard.missed_snapshots, 0)
        self.assertEqual(dashboard.unexpected_tick_steps, 0)
        self.assertEqual(dashboard.stats(now=70.02).producer_restarts, 1)
        self.assertEqual(dashboard.decoder.completed_groups, 4)

    def test_target_vehicle_selector_button_and_speed_codes(self):
        dashboard = model.DashboardModel("tuning", 0x6F0, 1)
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
        button[3] = 0x01
        dashboard.process_frame(
            model.FrameRecord(model.ASCD_BUTTON_ID, bytes(button)),
            now=1.15,
        )
        self.assertEqual(dashboard.ascd_button, "MAIN")

        speed = bytearray(8)
        speed[4:6] = (6854).to_bytes(2, "big")
        dashboard.process_frame(
            model.FrameRecord(model.VEHICLE_SPEED_ID, bytes(speed)),
            now=1.2,
        )
        self.assertEqual(dashboard.vehicle_speed_raw, 6854)
        self.assertEqual(dashboard.vehicle_speed_kmh, 68.54)

    def test_the_transmission_gear_is_the_low_nibble_of_frame_0x174(self):
        dashboard = model.DashboardModel("tuning", 0x6F0, 1)
        for code, gear in (
            (0x11, 1),
            (0x33, 3),
            (0x34, 4),
            (0x77, 7),
            (0xAA, None),
            (0x99, None),
            (0x00, None),
            (0x38, None),
        ):
            with self.subTest(code=code):
                data = bytearray(8)
                data[3] = code
                dashboard.process_frame(
                    model.FrameRecord(model.TCM_GEAR_ID, bytes(data)),
                    now=1.0,
                )
                self.assertEqual(dashboard.tcm_gear, gear)
        dashboard.process_frame(
            model.FrameRecord(model.TCM_GEAR_ID, bytes((0, 0, 0, 0x22))),
            now=1.1,
        )
        dashboard.process_frame(
            model.FrameRecord(model.TCM_GEAR_ID, bytes((0, 0, 0x55))),
            now=1.2,
        )
        self.assertEqual(dashboard.tcm_gear, 2)

    def test_status_bits_and_decoder_errors_are_exposed(self):
        generator = model.DemoGenerator()
        dashboard = model.DashboardModel("tuning", 0x6F0, 1)
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
        dashboard = model.DashboardModel("tuning", 0x6F0, 4)
        feed_group(dashboard, generator.group(4), 3.0)
        feed_group(dashboard, generator.group(8), 3.04)
        self.assertEqual(dashboard.missed_snapshots, 0)
        self.assertEqual(dashboard.unexpected_tick_steps, 0)

    def test_health_mismatch_disables_retained_engineering_values(self):
        generator = model.DemoGenerator()
        dashboard = model.DashboardModel("tuning", 0x6F0, 1)
        for tick in range(1, 5):
            feed_group(dashboard, generator.group(tick), 4.0 + tick * 0.01)
        self.assertTrue(dashboard.schema_verified)
        self.assertIsNotNone(dashboard.value("normalized_load_percent"))

        bad = list(generator.group(9))
        self.assertEqual(bad[9].data[1], 3)
        health = bytearray(bad[9].data)
        health[5] ^= 1
        bad[9] = model.FrameRecord(0x6F0, bytes(health))
        self.assertIsNone(feed_group(dashboard, bad, 4.1))
        self.assertFalse(dashboard.schema_verified)
        self.assertIsNone(dashboard.value("normalized_load_percent"))

    def test_the_telemetry_map_index_names_the_selected_map(self):
        dashboard = model.DashboardModel("tuning", 0x6F0, 1)
        for tick, (index, number) in enumerate(
            ((0, 1), (3, 4), (4, 5), (5, 1), (0xFF, 1)), start=1
        ):
            with self.subTest(index=index):
                values = {
                    "tick16": tick,
                    "schema_verified": 1,
                    "profile_id": 7,
                    "active_map_index": index,
                }
                dashboard.process_record(
                    model.SnapshotRecord(tick * 0.01, values), now=tick * 0.01
                )
                self.assertEqual(dashboard.profile_id, 7)
                self.assertEqual(dashboard.telemetry_map, number)
                self.assertEqual(dashboard.selected_map, number)
        dashboard.drive.map.number = 3
        dashboard.schema_verified = False
        self.assertIsNone(dashboard.telemetry_map)
        self.assertEqual(dashboard.selected_map, 3)

    def test_rolling_launch_codes_follow_the_runtime_enumerations(self):
        for names, enumeration in (
            (model.ROLLING_LAUNCH_PHASES, rolling_launch.Phase),
            (model.ROLLING_LAUNCH_ABORT_REASONS, rolling_launch.AbortReason),
        ):
            with self.subTest(enumeration=enumeration.__name__):
                self.assertEqual(
                    [member.value for member in enumeration],
                    list(range(len(enumeration))),
                )
                self.assertEqual(
                    names,
                    tuple(
                        member.name.replace("_", " ")
                        for member in enumeration
                    ),
                )
        values = model._dashboard_engineering_values(
            {"rolling_launch_phase": 2, "rolling_launch_abort_reason": 14}
        )
        self.assertEqual(values["rolling_launch_phase_name"], "COOLDOWN")
        self.assertEqual(values["rolling_launch_abort_name"], "TIMEOUT")
        values = model._dashboard_engineering_values(
            {"rolling_launch_phase": 3, "rolling_launch_abort_reason": 19}
        )
        self.assertEqual(values["rolling_launch_phase_name"], "0x03")
        self.assertEqual(values["rolling_launch_abort_name"], "0x13")


if __name__ == "__main__":
    unittest.main()
