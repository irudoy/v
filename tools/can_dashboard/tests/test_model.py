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

    def test_demo_defaults_a_field_without_a_curve_of_its_own(self):
        document = json.loads(
            can_telemetry.DEFAULT_SCHEMA.read_text(encoding="utf-8")
        )
        profile = document["profiles"][0]
        renamed = {
            "coolant_raw": "spare_coolant_raw",
            "knock_count_latched": "spare_count",
        }
        for field in can_telemetry.profile_fields(profile):
            field["name"] = renamed.get(field["name"], field["name"])
        crc = can_telemetry_schema.profile_crc16(
            profile, document["protocol_version"]
        )
        profile["crc16_ccitt_false"] = f"0x{crc:04X}"
        coolant = []
        with tempfile.TemporaryDirectory() as directory:
            schema_path = Path(directory) / "spare-schema.json"
            schema_path.write_text(json.dumps(document), encoding="utf-8")
            generator = model.DemoGenerator(schema_path=schema_path)
            dashboard = model.DashboardModel(
                "tuning", 0x6F0, 1, schema_path
            )
            for tick in range(1, 200):
                elapsed = tick * 0.05
                feed_group(
                    dashboard, generator.group(tick, elapsed), elapsed
                )
                if "spare_coolant" in dashboard.engineering:
                    coolant.append(dashboard.value("spare_coolant"))

        # The coolant feed channel spans -40 to 140 degC; the count has no
        # feed channel and reads zero.
        self.assertTrue(dashboard.schema_verified)
        self.assertGreater(len(set(coolant)), 1)
        self.assertTrue(all(-40 <= value <= 140 for value in coolant))
        self.assertEqual(dashboard.raw["spare_count"], 0)

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
        self.assertEqual(dashboard.value("coolant"), 90)
        self.assertEqual(dashboard.value("iat"), 32)
        self.assertIn("stft_b1", dashboard.engineering)
        self.assertIn("ltft_b1", dashboard.engineering)
        self.assertIn("intake_cvtc_actual_b1", dashboard.engineering)
        self.assertIn("intake_cvtc_target", dashboard.engineering)
        self.assertIn("exhaust_cvtc_target", dashboard.engineering)
        self.assertIn("calculated_load", dashboard.engineering)
        self.assertIn("app1", dashboard.engineering)
        self.assertIn("tps_b1", dashboard.engineering)
        self.assertIn("oil_temperature_did_source", dashboard.engineering)
        self.assertIn("engine_torque_state", dashboard.engineering)
        self.assertIn("battery_voltage", dashboard.engineering)
        self.assertIn("exhaust_cvtc_actual_b1", dashboard.engineering)
        self.assertEqual(
            dashboard.value("knock_timing_state"),
            dashboard.raw["knock_timing_state_raw"] / 256,
        )
        self.assertEqual(dashboard.value("knock_surface_state"), "HIGH OCTANE")
        self.assertEqual(dashboard.high_detonation_selected, 0)
        self.assertGreater(dashboard.value("stft_b1"), -5)
        self.assertLess(dashboard.value("stft_b1"), 5)
        self.assertIsNone(dashboard.value("rpm"))
        self.assertEqual(dashboard.missed_snapshots, 0)
        self.assertEqual(
            dashboard.value("intake_cvtc_target"),
            dashboard.raw["intake_cvtc_target_raw"] * 0.5 - 64,
        )
        self.assertEqual(
            dashboard.value("exhaust_cvtc_target"),
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
            if "secondary_tps_b2" in dashboard.engineering:
                break

        for bank in (1, 2):
            with self.subTest(bank=bank):
                raw = dashboard.raw[f"secondary_tps_b{bank}_raw"]
                self.assertLess(raw, 1024)
                self.assertAlmostEqual(
                    dashboard.value(f"secondary_tps_b{bank}"), raw / 200
                )

    def test_converted_fields_preserve_counts_and_engineering_units(self):
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
            "apc_command": 20,
            "throttle_request_bounded": 2565,
            "throttle_target_shared": 26845,
            "throttle_target_channel_0": 2143 * 34285 / 1114112,
            "throttle_target_channel_1": 2149 * 34285 / 1114112,
            "front_af_sensor_b1_word": 2.2,
            "front_af_sensor_b2_word": 5.065,
            "af_adjustment_b1": -0.004,
            "af_adjustment_b2": 0.33,
        }
        for key, value in expected.items():
            with self.subTest(key=key):
                self.assertAlmostEqual(dashboard.value(key), value)
        self.assertEqual(dashboard.value("fuel_inhibit_mask"), "cyl 1 3 5")
        self.assertEqual(
            dashboard.value("knock_channel_mask_latched"), "ch 1 2 4 6"
        )
        self.assertEqual(dashboard.raw["af_adjustment_b1_raw"], -2)

    def test_masks_name_their_members(self):
        self.assertEqual(model.inhibited_cylinders(0), "none")
        self.assertEqual(model.inhibited_cylinders(0x3F), "all")
        self.assertEqual(model.inhibited_cylinders(0x15), "cyl 1 3 5")
        self.assertEqual(model.inhibited_cylinders(0x20), "cyl 6")
        self.assertEqual(model.knock_channels(0), "none")
        self.assertEqual(model.knock_channels(0x2B), "ch 1 2 4 6")

    def test_a_field_displays_its_conversion_or_its_named_codes(self):
        def field(**terms):
            return {"name": "example", "width": 1, "signed": False, **terms}

        calibration = can_telemetry.Calibration("example", 0.5, -64)
        self.assertEqual(model.field_display(field(), calibration)(160), 16)
        values = model.field_display(
            field(
                values=[
                    {"value": 0, "name": "IDLE"},
                    {"value": 1, "name": "BUTTON_HELD"},
                ]
            )
        )
        self.assertEqual(values(1), "BUTTON HELD")
        self.assertEqual(values(7), "0x07")
        bits = model.field_display(
            field(
                bits=[
                    {"bit": 0, "name": "LEFT"},
                    {"bit": 6, "name": "HIGH_DETONATION"},
                ]
            )
        )
        self.assertEqual(bits(0x41), "LEFT, HIGH DETONATION")
        self.assertEqual(bits(0x02), "none")
        efficiency = model.field_display(
            field(
                width=2,
                dashboard={"digits": 1},
                **can_telemetry_schema.scale_terms(
                    "field 0 through 9 raw / 10 percent; bits: 14 SPEED, 15 ACTUATION_READY"
                ),
            )
        )
        self.assertEqual(efficiency(750 | 3 << 14), "75.0 %, SPEED, ACTUATION READY")
        self.assertEqual(efficiency(1000), "100.0 %")
        status = model.field_display(
            field(
                **can_telemetry_schema.scale_terms(
                    "field 0 through 1 enumeration: 0 NONE, 1 RPM, 2 SPEED; "
                    "bits: 2 VALUE_VALID, 7 ACTUATION_READY"
                )
            )
        )
        self.assertEqual(status(0x86), "SPEED, VALUE VALID, ACTUATION READY")
        self.assertEqual(status(0x03), "0x03")
        self.assertIsNone(model.field_display(field()))
        # A mask the dashboard names in code keeps its code display.
        self.assertIs(
            model.field_display(field(name="fuel_inhibit_mask")),
            model.inhibited_cylinders,
        )

    def test_a_field_without_a_display_shows_its_raw_value(self):
        dashboard = model.DashboardModel("tuning", 0x6F0, 1)
        values = {
            "tick16": 1,
            "schema_verified": 1,
            "knock_margin_min_ch1_raw": -250,
            "knock_count_latched": 3,
        }
        dashboard.process_record(model.SnapshotRecord(0.0, values), now=0.0)
        self.assertEqual(dashboard.value("knock_margin_min_ch1"), -250)
        self.assertEqual(dashboard.value("knock_count_latched"), 3)
        self.assertNotIn("knock_margin_min_ch1", dashboard.engineering)
        self.assertIsNone(dashboard.value("unknown", None))

    def test_mask_names_follow_the_profile_declarations(self):
        _document, profiles = can_telemetry.load_schema(
            can_telemetry.DEFAULT_SCHEMA
        )
        scales = {
            field["name"]: field["scale"]
            for field in profiles["tuning"]["fields"]
        }
        prefix = "bits: "
        self.assertTrue(scales["fuel_inhibit_mask"].startswith(prefix))
        for entry in scales["fuel_inhibit_mask"][len(prefix):].split(", "):
            bit, name = entry.split(" ")
            with self.subTest(bit=bit):
                self.assertEqual(
                    model.inhibited_cylinders(1 << int(bit)),
                    "cyl " + name.removeprefix("CYLINDER_"),
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
            dashboard.value("knock_surface_state"),
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

    def test_a_restart_past_the_opening_window_opens_a_run_live_and_recorded(self):
        generator = model.DemoGenerator()
        live = model.DashboardModel("tuning", 0x6F0, 1)
        feed_group(live, generator.group(0x2820, 10.0), 10.0)
        feed_group(live, generator.group(0x0300, 11.0), 11.0)
        feed_group(live, generator.group(0x0301, 11.01), 11.01)
        self.assertEqual(live.stats(now=11.02).producer_restarts, 1)
        self.assertEqual(live.decoder.completed_groups, 3)
        self.assertEqual(live.unexpected_tick_steps, 0)

        recorded = model.DashboardModel("tuning", 0x6F0, 1)
        for timestamp, tick in ((10.0, 0x2820), (11.0, 0x0300), (11.01, 0x0300)):
            recorded.process_record(
                model.SnapshotRecord(timestamp, {"tick16": tick}), now=timestamp
            )
        self.assertEqual(recorded.stats(now=11.02).producer_restarts, 1)

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
        feed_group(dashboard, generator.group(4), 1.0)
        group = list(generator.group(5))
        page = bytearray(group[7].data)
        page[7] = 0x09
        group[7] = model.FrameRecord(0x6F0, bytes(page))
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

    def test_rate_windows_stay_bounded_without_stats_requests(self):
        generator = model.DemoGenerator()
        dashboard = model.DashboardModel("tuning", 0x6F0, 1)
        group_seconds = model.BASE_TICK_SECONDS
        for tick in range(1, 1001):
            feed_group(dashboard, generator.group(tick), tick * group_seconds)
        now = 1000 * group_seconds
        window = model.RATE_WINDOW_SECONDS
        self.assertTrue(all(
            now - value <= window for value in dashboard._snapshot_times
        ))
        self.assertTrue(all(
            now - value <= window + 0.01
            for value in dashboard._telemetry_frame_times
        ))
        stats = dashboard.stats(now)
        self.assertAlmostEqual(stats.snapshot_hz, 1 / group_seconds, places=6)

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
        self.assertIsNotNone(dashboard.value("normalized_load"))

        bad = list(generator.group(9))
        self.assertEqual(bad[9].data[1], 3)
        health = bytearray(bad[9].data)
        health[5] ^= 1
        bad[9] = model.FrameRecord(0x6F0, bytes(health))
        self.assertIsNone(feed_group(dashboard, bad, 4.1))
        self.assertFalse(dashboard.schema_verified)
        self.assertIsNone(dashboard.value("normalized_load"))

    def test_unverified_fields_stay_hidden_and_do_not_cross_verification(self):
        generator = model.DemoGenerator()
        dashboard = model.DashboardModel("tuning", 0x6F0, 1)
        for frame in generator.stock_context(1):
            dashboard.process_frame(frame, now=0.0)
        stock_rpm = dashboard.stock_rpm
        feed_group(dashboard, generator.group(1), 0.01)
        self.assertIn("coolant_raw", dashboard.raw)
        for key in (*dashboard._displays, *dashboard._raw_keys):
            with self.subTest(key=key):
                self.assertIsNone(dashboard.value(key))
        self.assertEqual(dashboard.telemetry_status_flags, {})
        self.assertEqual(dashboard.stock_rpm, stock_rpm)

        feed_group(dashboard, generator.group(4), 0.04)
        self.assertTrue(dashboard.schema_verified)
        self.assertIsNotNone(dashboard.value("normalized_load"))
        self.assertIsNone(dashboard.value("coolant"))
        feed_group(dashboard, generator.group(6), 0.06)
        self.assertIsNotNone(dashboard.value("coolant"))

        bad = list(generator.group(9))
        health = bytearray(bad[9].data)
        health[3] ^= 1
        bad[9] = model.FrameRecord(0x6F0, bytes(health))
        self.assertIsNone(feed_group(dashboard, bad, 0.09))
        self.assertEqual(dashboard.raw, {})
        self.assertEqual(dashboard.engineering, {})
        self.assertEqual(dashboard.updated_at, {})
        feed_group(dashboard, generator.group(11), 0.11)
        self.assertIn("coolant_raw", dashboard.raw)
        self.assertIsNone(dashboard.value("coolant"))
        self.assertIsNone(dashboard.value("rolling_launch_phase"))
        self.assertEqual(dashboard.stock_rpm, stock_rpm)

        feed_group(dashboard, generator.group(14), 0.14)
        self.assertTrue(dashboard.schema_verified)
        self.assertIsNotNone(dashboard.value("normalized_load"))
        self.assertIsNone(dashboard.value("coolant"))
        feed_group(dashboard, generator.group(16), 0.16)
        self.assertIsNotNone(dashboard.value("coolant"))

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

    def test_a_configuration_change_drops_the_values_of_the_previous_one(self):
        generator = model.DemoGenerator()
        dashboard = model.DashboardModel("tuning", 0x6F0, 1)
        page = dashboard.decoder.profile["dynamic"]["page"]

        def feed(tick, selector, data):
            group = list(generator.group(tick))
            payload = bytearray(group[page].data)
            payload[1:7] = data
            payload[7] = selector
            group[page] = model.FrameRecord(0x6F0, bytes(payload))
            return feed_group(
                dashboard, group, tick * model.BASE_TICK_SECONDS
            )

        for tick in range(1, 11):
            feed_group(
                dashboard,
                generator.group(tick),
                tick * model.BASE_TICK_SECONDS,
            )
        self.assertTrue(dashboard.schema_verified)
        self.assertIn("exhaust_cvtc_actual_b1_raw", dashboard.raw)
        self.assertEqual(dashboard.page_configuration_label, "Default")
        feed(11, 2, bytes((0, 25, 1, 0x0B, 7, 40)))
        self.assertNotIn("exhaust_cvtc_actual_b1_raw", dashboard.raw)
        self.assertNotIn("exhaust_cvtc_actual_b1", dashboard.engineering)
        self.assertEqual(dashboard.raw["rolling_launch_speed_error_raw"], 25)
        self.assertAlmostEqual(dashboard.value("rolling_launch_speed_error"), 2.5)
        feed(12, 0x82, bytes((0, 16, 3, 7, 0, 0)))
        # The groups of one configuration keep the values of each other.
        self.assertEqual(dashboard.raw["rolling_launch_speed_error_raw"], 25)
        self.assertEqual(dashboard.raw["rolling_launch_integrator_raw"], 16)
        feed(13, 1, bytes((0, 30, 1, 0x0B, 8, 40)))
        self.assertNotIn("rolling_launch_integrator_raw", dashboard.raw)
        self.assertNotIn("speed_frame_receive_age", dashboard.engineering)
        self.assertEqual(dashboard.page_configuration_id, 1)
        self.assertEqual(dashboard.page_configuration_label, "Rolling Launch law")

    def test_rolling_launch_codes_follow_the_runtime_enumerations(self):
        _document, profiles = can_telemetry.load_schema(
            can_telemetry.DEFAULT_SCHEMA
        )
        fields = {
            field["name"]: field
            for field in can_telemetry.profile_fields(profiles["tuning"])
        }
        for name, enumeration in (
            ("rolling_launch_phase", rolling_launch.Phase),
            ("rolling_launch_abort_reason", rolling_launch.AbortReason),
        ):
            with self.subTest(enumeration=enumeration.__name__):
                self.assertEqual(
                    fields[name]["values"],
                    [
                        {"value": member.value, "name": member.name}
                        for member in enumeration
                    ],
                )
        dashboard = model.DashboardModel("tuning", 0x6F0, 1)
        for tick, (phase, reason, phase_name, reason_name) in enumerate(
            ((2, 14, "COOLDOWN", "TIMEOUT"), (3, 26, "0x03", "0x1A")),
            start=1,
        ):
            with self.subTest(phase=phase, reason=reason):
                values = {
                    "tick16": tick,
                    "schema_verified": 1,
                    "rolling_launch_phase": phase,
                    "rolling_launch_abort_reason": reason,
                }
                dashboard.process_record(
                    model.SnapshotRecord(tick * 0.01, values), now=tick * 0.01
                )
                self.assertEqual(
                    dashboard.value("rolling_launch_phase"), phase_name
                )
                self.assertEqual(
                    dashboard.value("rolling_launch_abort_reason"), reason_name
                )

    def test_telemetry_autostart_bits_and_demo_control(self):
        generator = model.DemoGenerator()
        dashboard = model.DashboardModel("tuning", 0x6F0, 1)
        # Feed ticks 1..5 so schema identity verifies; initial demo state is OFF (saved).
        for tick in range(1, 6):
            feed_group(dashboard, generator.group(tick, tick * 0.01), tick * 0.01)
        self.assertTrue(dashboard.schema_verified)
        self.assertEqual(dashboard.telemetry_autostart_enabled, False)
        self.assertEqual(dashboard.telemetry_autostart_saved, True)
        self.assertEqual(dashboard.telemetry_autostart_state, "off")
        self.assertFalse(any(dashboard.telemetry_status_flags.values()))

        # Demo control toggles autostart ON and updates telemetry_status bits 4..5.
        self.assertTrue(generator.control(bytes.fromhex("54454C3202039670")))
        feed_group(dashboard, generator.group(6, 0.06), 0.06)
        self.assertEqual(dashboard.telemetry_autostart_enabled, True)
        self.assertEqual(dashboard.telemetry_autostart_saved, True)
        self.assertEqual(dashboard.telemetry_autostart_state, "on")
        self.assertFalse(any(dashboard.telemetry_status_flags.values()))

        # Fault bits 0..3 remain independent of persistent autostart bits 4..5.
        dashboard.process_record(
            model.SnapshotRecord(0.07, {"tick16": 7, "schema_verified": 1, "telemetry_status": 0x15}),
            now=0.07,
        )
        self.assertEqual(dashboard.telemetry_autostart_enabled, True)
        self.assertEqual(dashboard.telemetry_autostart_saved, False)
        self.assertEqual(dashboard.telemetry_autostart_state, "on (saving)")
        self.assertEqual(
            dashboard.telemetry_status_flags,
            {
                "overrun_latched": True,
                "abort_latched": False,
                "event_overflow": True,
                "preempted": False,
            },
        )

        self.assertTrue(generator.control(bytes.fromhex("54454C3202028651")))
        feed_group(dashboard, generator.group(8, 0.08), 0.08)
        self.assertEqual(dashboard.telemetry_autostart_enabled, False)
        self.assertEqual(dashboard.telemetry_autostart_saved, True)
        self.assertEqual(dashboard.telemetry_autostart_state, "off")


if __name__ == "__main__":
    unittest.main()
