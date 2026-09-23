import json
from pathlib import Path
import tempfile
import unittest

from patches import can_telemetry_profile
from tools.logs import can_telemetry
from tools.logs import can_telemetry_schema


def frames(profile, tick, *, context_tag=0, health_valid=True, identity=None):
    """Build one group; ``identity`` overrides the (ID, CRC) of tag 3."""
    manifest = can_telemetry_profile.load_manifest()
    profile_spec = manifest.profile_by_name[profile]
    profile_id, crc16 = identity or (profile_spec.profile_id, profile_spec.crc16)
    result = []
    for page in range(profile_spec.page_count):
        payload = bytearray(8)
        payload[0] = ((tick & 0x0F) << 4) | page
        payload[1:] = bytes(
            ((page * 7 + index + 1) & 0xFF) for index in range(7)
        )
        result.append(payload)
    result[0][1:3] = tick.to_bytes(2, "big")
    for page in manifest.context_pages:
        result[page][1] = context_tag
    if context_tag == 3:
        result[9][2] = manifest.protocol_version
        result[9][3] = profile_id
        result[9][4:6] = crc16.to_bytes(2, "big")
        result[9][6] = 4
        result[9][7] = 2
        if not health_valid:
            result[9][5] ^= 1
    return tuple(bytes(item) for item in result)


def feed_group(decoder, group):
    snapshot = None
    for payload in group:
        result = decoder.feed(decoder.can_id, payload)
        if result is not None:
            snapshot = result
    return snapshot


class CanTelemetryDecoderTest(unittest.TestCase):
    def test_schema_crc_rejects_a_changed_wire_contract(self):
        document = json.loads(
            can_telemetry.DEFAULT_SCHEMA.read_text(encoding="utf-8")
        )
        field = document["profiles"][0]["fields"][0]
        field["signed"] = not field["signed"]
        with tempfile.TemporaryDirectory() as directory:
            schema_path = Path(directory) / "changed-schema.json"
            schema_path.write_text(
                json.dumps(document), encoding="utf-8"
            )
            with self.assertRaisesRegex(
                can_telemetry.DecodeError,
                "CRC16 does not match",
            ):
                can_telemetry.Decoder("tuning", 0x6F0, schema_path)

    def test_schema_crc_accepts_restated_names_and_scales(self):
        document = json.loads(
            can_telemetry.DEFAULT_SCHEMA.read_text(encoding="utf-8")
        )
        field = document["profiles"][0]["fields"][-1]
        field["name"] = "restated_" + field["name"]
        field["scale"] = "restated"
        with tempfile.TemporaryDirectory() as directory:
            schema_path = Path(directory) / "restated-schema.json"
            schema_path.write_text(
                json.dumps(document), encoding="utf-8"
            )
            decoder = can_telemetry.Decoder("tuning", 0x6F0, schema_path)
        self.assertEqual(
            decoder.profile["_crc16"],
            can_telemetry.Decoder("tuning", 0x6F0).profile["_crc16"],
        )

    def test_external_schema_identity_does_not_require_a_rom_manifest(self):
        document = json.loads(
            can_telemetry.DEFAULT_SCHEMA.read_text(encoding="utf-8")
        )
        profile = document["profiles"][0]
        profile["name"] = "portable"
        profile["id"] = 7
        for retired in document["retired_profiles"]:
            retired["name"] = "portable"
        portable_crc = can_telemetry_schema.profile_crc16(
            profile, document["protocol_version"]
        )
        profile["crc16_ccitt_false"] = f"0x{portable_crc:04X}"
        with tempfile.TemporaryDirectory() as directory:
            schema_path = Path(directory) / "portable-schema.json"
            schema_path.write_text(
                json.dumps(document), encoding="utf-8"
            )
            decoder = can_telemetry.Decoder(
                "portable", 0x6F0, schema_path
            )

            group = list(frames("tuning", 3, context_tag=3))
            health = bytearray(group[9])
            health[3] = 7
            health[4:6] = portable_crc.to_bytes(2, "big")
            group[9] = bytes(health)
            snapshot = feed_group(decoder, group)

        self.assertIsNotNone(snapshot)
        self.assertTrue(snapshot.schema_verified)
        self.assertEqual(decoder.profile["name"], "portable")

    def test_group_decodes_raw_fields_before_health_verification(self):
        decoder = can_telemetry.Decoder("tuning", 0x6F0)
        snapshot = feed_group(
            decoder, frames("tuning", 0x1234, context_tag=0)
        )
        self.assertIsNotNone(snapshot)
        self.assertEqual(snapshot.tick16, 0x1234)
        self.assertEqual(snapshot.sequence, 0x04)
        self.assertFalse(snapshot.schema_verified)
        # Retired profiles place the engine-speed coordinate where the current
        # one places the request flow, so an unidentified group reads neither.
        self.assertNotIn("rpm_raw", snapshot.fields)
        self.assertNotIn("request_flow_raw", snapshot.fields)
        self.assertEqual(snapshot.fields["final_timing_raw"], 5)
        self.assertEqual(snapshot.fields["injection_0_raw"], 0x1213)
        self.assertIn("injection_end_angle_raw", snapshot.fields)
        self.assertIn("throttle_request_bounded_raw", snapshot.fields)
        with self.assertRaises(can_telemetry.DecodeError):
            can_telemetry.engineering_values(snapshot)
        self.assertEqual(decoder.completed_groups, 1)

    def test_context_pairs_and_in_band_health_verification(self):
        decoder = can_telemetry.Decoder("tuning", 0x6EF)
        temperature = feed_group(
            decoder, frames("tuning", 1, context_tag=0)
        )
        self.assertFalse(temperature.schema_verified)
        self.assertIsNone(temperature.profile_id)
        # Profile 5 names the page-10 context of tag 0 differently, so an
        # unidentified run reports no context name for the pair.
        self.assertIsNone(temperature.context_name)
        self.assertIn("ltft_learned_b1_raw", temperature.fields)
        self.assertNotIn("rolling_launch_abort_reason", temperature.fields)
        with self.assertRaises(can_telemetry.DecodeError):
            can_telemetry.engineering_values(temperature)

        health = feed_group(
            decoder, frames("tuning", 2, context_tag=3)
        )
        self.assertTrue(health.schema_verified)
        self.assertEqual(health.fields["snapshot_overrun_count"], 4)
        verified_temperature = feed_group(
            decoder, frames("tuning", 3, context_tag=0)
        )
        self.assertTrue(verified_temperature.schema_verified)
        self.assertEqual(verified_temperature.profile_id, 7)
        self.assertEqual(verified_temperature.fields["request_flow_raw"], 0x0304)
        self.assertEqual(
            verified_temperature.context_name,
            "temperatures_af + launch_abort_voltage_and_trim_terms",
        )
        self.assertIn("rolling_launch_abort_reason", verified_temperature.fields)
        physical = can_telemetry.engineering_values(verified_temperature)
        self.assertEqual(
            physical["coolant_deg_c"],
            verified_temperature.fields["coolant_raw"] - 50,
        )
        fixed_physical = can_telemetry.engineering_values(health)
        self.assertEqual(
            fixed_physical["intake_cvtc_actual_b1_deg_ca"],
            health.fields["intake_cvtc_actual_b1_raw"] * 0.5 - 64,
        )
        self.assertAlmostEqual(
            fixed_physical["calculated_load_percent"],
            health.fields["calculated_load_raw"] * 100 / 255,
        )
        self.assertAlmostEqual(
            fixed_physical["engine_torque_state_nm"],
            health.fields["engine_torque_state_raw"] * 0.1,
        )
        self.assertAlmostEqual(
            physical["battery_voltage_v"],
            verified_temperature.fields["battery_voltage_raw"] * 0.08,
        )
        self.assertAlmostEqual(
            physical["ltft_learned_b1_percent"],
            verified_temperature.fields["ltft_learned_b1_raw"] / 256 - 100,
        )

        trims = feed_group(
            decoder, frames("tuning", 4, context_tag=1)
        )
        trim_physical = can_telemetry.engineering_values(trims)
        self.assertAlmostEqual(
            trim_physical["stft_b1_percent"],
            trims.fields["stft_b1_raw"] / 256 - 100,
        )
        self.assertEqual(
            trims.context_name,
            "short_fuel_trim_cvtc_duty"
            " + exhaust_cvtc_duty_and_intake_duty_command",
        )
        for bank in (1, 2):
            self.assertAlmostEqual(
                trim_physical[f"intake_cvtc_duty_b{bank}_percent"],
                trims.fields[f"intake_cvtc_duty_b{bank}_raw"] * 39 / 100,
            )
            self.assertAlmostEqual(
                trim_physical[f"intake_cvtc_duty_command_b{bank}_percent"],
                trims.fields[f"intake_cvtc_duty_command_b{bank}_raw"]
                * 39
                / 100,
            )
        self.assertAlmostEqual(
            fixed_physical["injection_end_angle_deg"],
            health.fields["injection_end_angle_raw"] * 2 - 590,
        )

    def test_retired_profile_stream_decodes_with_its_own_layout(self):
        decoder = can_telemetry.Decoder("tuning")
        self.assertEqual(sorted(decoder.versions), [5, 6, 7])
        retired = decoder.versions[5]
        identity = (5, retired["_crc16"])
        self.assertEqual(identity, (5, 0xE144))

        unidentified = feed_group(decoder, frames("tuning", 1, identity=identity))
        self.assertFalse(unidentified.schema_verified)
        self.assertIsNone(unidentified.profile_id)
        for name in (
            "front_oxygen_sensor_b1_raw",
            "normalized_load_raw",
            "rolling_launch_phase",
            "rpm_raw",
        ):
            self.assertNotIn(name, unidentified.fields)
        self.assertIn("maf_total_raw", unidentified.fields)

        health = feed_group(
            decoder, frames("tuning", 2, context_tag=3, identity=identity)
        )
        self.assertTrue(health.schema_verified)
        self.assertEqual(health.profile_id, 5)
        self.assertEqual(decoder.active_profile["id"], 5)
        # Profile 5 carries the A/F adjustment B2 slot unsigned.
        self.assertIn("af_adjustment_b2_raw", health.fields)
        self.assertGreaterEqual(health.fields["af_adjustment_b2_raw"], 0)

        identified = feed_group(
            decoder, frames("tuning", 3, context_tag=0, identity=identity)
        )
        self.assertEqual(identified.profile_id, 5)
        self.assertEqual(
            identified.context_name,
            "temperatures_af + pressure_voltage_and_trim_terms",
        )
        self.assertEqual(
            identified.fields["front_oxygen_sensor_b1_raw"],
            frames("tuning", 3)[1][7],
        )
        self.assertIn("atmospheric_pressure_raw", identified.fields)
        self.assertEqual(identified.fields["rpm_raw"], 0x0304)
        self.assertNotIn("normalized_load_raw", identified.fields)
        self.assertNotIn("rolling_launch_abort_reason", identified.fields)
        physical = can_telemetry.engineering_values(identified)
        self.assertNotIn("normalized_load_percent", physical)
        self.assertEqual(
            physical["coolant_deg_c"], identified.fields["coolant_raw"] - 50
        )

        current = feed_group(decoder, frames("tuning", 4, context_tag=3))
        self.assertEqual(current.profile_id, 7)
        loaded = feed_group(decoder, frames("tuning", 5))
        self.assertEqual(loaded.fields["normalized_load_raw"], frames("tuning", 5)[1][7])
        self.assertAlmostEqual(
            can_telemetry.engineering_values(loaded)["normalized_load_percent"],
            loaded.fields["normalized_load_raw"] * 100 / 128,
        )
        self.assertNotIn("front_oxygen_sensor_b1_raw", loaded.fields)
        self.assertEqual(loaded.fields["request_flow_raw"], 0x0304)
        self.assertNotIn("rpm_raw", loaded.fields)

        previous = can_telemetry.Decoder("tuning")
        identity = (6, previous.versions[6]["_crc16"])
        self.assertEqual(identity, (6, 0xF14E))
        feed_group(previous, frames("tuning", 1, context_tag=3, identity=identity))
        speed = feed_group(previous, frames("tuning", 2, identity=identity))
        self.assertEqual(speed.profile_id, 6)
        self.assertEqual(speed.fields["rpm_raw"], 0x0304)
        self.assertNotIn("request_flow_raw", speed.fields)

    def test_identified_profile_ends_with_its_run(self):
        decoder = can_telemetry.Decoder("tuning")
        feed_group(
            decoder, frames("tuning", 0x281F, context_tag=3, identity=(5, 0xE144))
        )
        self.assertEqual(decoder.active_profile["id"], 5)
        restarted = feed_group(decoder, frames("tuning", 1))
        self.assertEqual(restarted.run, 1)
        self.assertIsNone(restarted.profile_id)
        self.assertIsNone(decoder.active_profile)
        self.assertNotIn("front_oxygen_sensor_b1_raw", restarted.fields)

    def test_unknown_or_mismatched_profile_identity_is_rejected(self):
        decoder = can_telemetry.Decoder("tuning")
        feed_group(decoder, frames("tuning", 1, context_tag=3))
        self.assertEqual(decoder.active_profile["id"], 7)
        for identity in ((4, 0xE144), (5, 0xF14E), (7, 0xF14E)):
            with self.subTest(identity=identity):
                result = feed_group(
                    decoder,
                    frames(
                        "tuning",
                        2 + decoder.completed_groups,
                        context_tag=3,
                        identity=identity,
                    ),
                )
                self.assertIsNone(result)
                self.assertIsNone(decoder.active_profile)
                self.assertFalse(decoder.schema_verified)
        self.assertEqual(decoder.schema_mismatches, 3)

    def test_schema_rejects_a_retired_profile_with_foreign_framing(self):
        document = json.loads(
            can_telemetry.DEFAULT_SCHEMA.read_text(encoding="utf-8")
        )
        (current_id,) = (
            row["id"] for row in document["profiles"] if row["name"] == "tuning"
        )
        self.assertEqual(
            [row["id"] for row in document["retired_profiles"]], [5, 6]
        )
        for retired in document["retired_profiles"]:
            changes = {
                "reused_id": dict(retired, id=current_id),
                "later_id": dict(retired, id=current_id + 1),
                "unknown_name": dict(retired, name="missing"),
                "health_moved": dict(
                    retired,
                    contexts=[
                        dict(row, tag=(row["tag"] + 1) % 5)
                        if row["page"] == 9
                        else row
                        for row in retired["contexts"]
                    ],
                ),
            }
            for change, row in changes.items():
                with self.subTest(retired=retired["id"], change=change):
                    # A consistent CRC leaves the framing rules to reject the row.
                    crc16 = can_telemetry_schema.profile_crc16(
                        row, document["protocol_version"]
                    )
                    row = dict(row, crc16_ccitt_false=f"0x{crc16:04X}")
                    damaged = dict(document, retired_profiles=[row])
                    with self.assertRaisesRegex(
                        can_telemetry.DecodeError, "retired_profile"
                    ):
                        can_telemetry.parse_schema(damaged)
            crc16 = can_telemetry_schema.profile_crc16(
                retired, document["protocol_version"]
            )
            self.assertEqual(retired["crc16_ccitt_false"], f"0x{crc16:04X}")

    def test_health_mismatch_is_rejected(self):
        decoder = can_telemetry.Decoder("tuning")
        result = feed_group(
            decoder,
            frames("tuning", 5, context_tag=3, health_valid=False),
        )
        self.assertIsNone(result)
        self.assertEqual(decoder.schema_mismatches, 1)
        self.assertEqual(decoder.completed_groups, 0)

    def test_loss_duplicate_reorder_and_preemption_are_visible(self):
        decoder = can_telemetry.Decoder("tuning")
        first = frames("tuning", 10)
        decoder.feed(decoder.can_id, first[0])
        decoder.feed(decoder.can_id, first[1])
        second = frames("tuning", 11)
        snapshot = feed_group(decoder, second)
        self.assertEqual(snapshot.tick16, 11)
        self.assertEqual(decoder.incomplete_groups, 1)

        third = frames("tuning", 12)
        decoder.feed(decoder.can_id, third[0])
        decoder.feed(decoder.can_id, third[2])
        self.assertGreaterEqual(decoder.malformed_frames, 1)
        self.assertGreaterEqual(decoder.incomplete_groups, 2)

        fourth = frames("tuning", 13)
        decoder.feed(decoder.can_id, fourth[0])
        decoder.feed(decoder.can_id, fourth[1])
        decoder.feed(decoder.can_id, fourth[1])
        self.assertGreaterEqual(decoder.malformed_frames, 2)

    def test_tick_wrap_unwrap_and_stale_group_rejection(self):
        decoder = can_telemetry.Decoder("tuning")
        before = feed_group(decoder, frames("tuning", 0xFFFF))
        after = feed_group(decoder, frames("tuning", 0x0000))
        self.assertEqual(before.unwrapped_tick, 0xFFFF)
        self.assertEqual(after.unwrapped_tick, 0x10000)
        duplicate = feed_group(decoder, frames("tuning", 0x0000))
        self.assertIsNone(duplicate)
        self.assertGreaterEqual(decoder.malformed_frames, 1)

    def test_producer_restart_opens_a_new_run(self):
        decoder = can_telemetry.Decoder("tuning")
        feed_group(decoder, frames("tuning", 0x281F, context_tag=3))
        self.assertTrue(decoder.schema_verified)
        before = feed_group(decoder, frames("tuning", 0x2820))
        self.assertEqual(before.run, 0)
        restarted = feed_group(decoder, frames("tuning", 1))
        self.assertIsNotNone(restarted)
        self.assertEqual(restarted.run, 1)
        self.assertEqual(restarted.tick16, 1)
        self.assertEqual(restarted.unwrapped_tick, 1)
        self.assertFalse(restarted.schema_verified)
        self.assertFalse(decoder.schema_verified)
        self.assertEqual(decoder.producer_restarts, 1)
        following = feed_group(decoder, frames("tuning", 2, context_tag=3))
        self.assertEqual(following.run, 1)
        self.assertEqual(following.unwrapped_tick, 2)
        self.assertTrue(following.schema_verified)
        self.assertEqual(decoder.producer_restarts, 1)

    def test_backwards_tick_outside_the_opening_window_is_rejected(self):
        decoder = can_telemetry.Decoder("tuning")
        feed_group(decoder, frames("tuning", 0x2820))
        stale = feed_group(decoder, frames("tuning", 0x2330))
        self.assertIsNone(stale)
        self.assertEqual(decoder.producer_restarts, 0)
        self.assertGreaterEqual(decoder.malformed_frames, 1)

    def test_wrap_into_the_opening_window_is_not_a_restart(self):
        decoder = can_telemetry.Decoder("tuning")
        feed_group(decoder, frames("tuning", 0xFFFE))
        wrapped = feed_group(decoder, frames("tuning", 0x0002))
        self.assertEqual(wrapped.run, 0)
        self.assertEqual(wrapped.unwrapped_tick, 0x10002)
        self.assertEqual(decoder.producer_restarts, 0)

    def test_wrong_id_bad_length_bad_header_and_unknown_context_are_rejected(self):
        decoder = can_telemetry.Decoder("tuning", 0x6F0)
        self.assertIsNone(decoder.feed(0x6EF, bytes(8)))
        self.assertIsNone(decoder.feed(0x6F0, bytes(7)))
        bad_header = bytearray(frames("tuning", 1)[0])
        bad_header[0] ^= 0x10
        self.assertIsNone(decoder.feed(0x6F0, bad_header))
        unknown = frames("tuning", 2, context_tag=0x7F)
        self.assertIsNone(feed_group(decoder, unknown))
        self.assertGreaterEqual(decoder.malformed_frames, 3)

    def test_initial_partial_group_waits_for_page_zero(self):
        decoder = can_telemetry.Decoder("tuning")
        group = frames("tuning", 7, context_tag=2)
        for payload in group[3:]:
            self.assertIsNone(decoder.feed(decoder.can_id, payload))
        self.assertEqual(decoder.malformed_frames, 0)
        self.assertIsNotNone(feed_group(
            decoder, frames("tuning", 8, context_tag=3)
        ))

    def test_mismatched_context_tags_are_rejected(self):
        decoder = can_telemetry.Decoder("tuning")
        group = list(frames("tuning", 9, context_tag=0))
        page = bytearray(group[10])
        page[1] = 1
        group[10] = bytes(page)
        self.assertIsNone(feed_group(decoder, group))
        self.assertEqual(decoder.malformed_frames, 1)

    def test_candump_parser_accepts_compact_frames(self):
        parsed = can_telemetry.parse_candump_line(
            "(12.500000) can0 6F0#A001020304050607"
        )
        self.assertEqual(
            parsed,
            (0x6F0, bytes.fromhex("A001020304050607"), 12.5),
        )
        self.assertIsNone(can_telemetry.parse_candump_line("can0 6F0 [8]"))


class CanTelemetryControlTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(
            can_telemetry.DEFAULT_SCHEMA.read_text(encoding="utf-8")
        )

    def test_exact_start_and_stop_frames(self):
        self.assertEqual(
            can_telemetry_schema.control_frame(
                self.schema, 0x6F0, "start"
            ),
            (0x6F1, bytes.fromhex("54454C320201B632")),
        )
        self.assertEqual(
            can_telemetry_schema.control_frame(
                self.schema, 0x6F0, "stop"
            ),
            (0x6F1, bytes.fromhex("54454C320200A613")),
        )

    def test_control_id_uses_the_standard_id_boundary(self):
        can_id, payload = can_telemetry_schema.control_frame(
            self.schema, 0x7FE, "start"
        )
        self.assertEqual(can_id, 0x7FF)
        self.assertEqual(
            can_telemetry_schema.crc16_ccitt_false(payload[:6]),
            int.from_bytes(payload[6:], "big"),
        )
        for data_can_id in (0, 0x7FF, 0x800):
            with self.subTest(data_can_id=data_can_id), self.assertRaises(
                ValueError
            ):
                can_telemetry_schema.control_frame(
                    self.schema, data_can_id, "start"
                )

    def test_unknown_or_corrupt_control_contract_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "undefined"):
            can_telemetry_schema.control_frame(
                self.schema, 0x6F0, "reset"
            )

        damaged = json.loads(json.dumps(self.schema))
        damaged["control"]["commands"]["start"] = "54454C320201B633"
        with self.assertRaisesRegex(ValueError, "invalid payload"):
            can_telemetry_schema.control_frame(
                damaged, 0x6F0, "start"
            )


if __name__ == "__main__":
    unittest.main()
