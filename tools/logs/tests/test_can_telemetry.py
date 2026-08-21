import unittest

from patches import can_telemetry_profile
from tools.logs import can_telemetry


def frames(profile, tick, *, context_tag=0, health_valid=True):
    manifest = can_telemetry_profile.load_manifest()
    profile_spec = manifest.profile_by_name[profile]
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
        result[9][3] = profile_spec.profile_id
        result[9][4:6] = profile_spec.crc16.to_bytes(2, "big")
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
    def test_group_decodes_raw_fields_before_health_verification(self):
        decoder = can_telemetry.Decoder("tuning", 0x6F0)
        snapshot = feed_group(
            decoder, frames("tuning", 0x1234, context_tag=0)
        )
        self.assertIsNotNone(snapshot)
        self.assertEqual(snapshot.tick16, 0x1234)
        self.assertEqual(snapshot.sequence, 0x04)
        self.assertFalse(snapshot.schema_verified)
        self.assertEqual(snapshot.fields["rpm_raw"], 0x0304)
        self.assertEqual(snapshot.fields["final_timing_raw"], 5)
        self.assertEqual(snapshot.fields["injection_0_raw"], 0x1213)
        self.assertIn("injection_timing_state_raw", snapshot.fields)
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
        self.assertEqual(
            temperature.context_name,
            "temperatures_af + intake_cvtc_duty_and_manifold_pressure",
        )
        self.assertIn("manifold_pressure_1116_raw", temperature.fields)
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
            physical["intake_cvtc_duty_b1_word_percent"],
            verified_temperature.fields["intake_cvtc_duty_b1_word_raw"]
            * 100
            / 1024,
        )

        trims = feed_group(
            decoder, frames("tuning", 4, context_tag=1)
        )
        trim_physical = can_telemetry.engineering_values(trims)
        self.assertAlmostEqual(
            trim_physical["stft_b1_percent"],
            trims.fields["stft_b1_raw"] / 256 - 100,
        )

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


if __name__ == "__main__":
    unittest.main()
