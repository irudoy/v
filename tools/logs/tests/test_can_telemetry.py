import unittest

from patches import can_telemetry_profile
from tools.logs import can_telemetry


def frames(profile, tick, *, context_tag=0, health_valid=True):
    manifest = can_telemetry_profile.load_manifest()
    profile_spec = manifest.profile_by_name[profile]
    result = []
    for page in range(profile_spec.page_count):
        payload = bytearray(8)
        payload[0] = ((tick & 0x1F) << 3) | page
        payload[1:] = bytes(
            ((page * 7 + index + 1) & 0xFF) for index in range(7)
        )
        result.append(payload)
    result[0][1:3] = tick.to_bytes(2, "big")
    if profile == "wide54":
        result[7][1] = context_tag
        if context_tag == 3:
            result[7][2] = manifest.protocol_version
            result[7][3] = profile_spec.profile_id
            result[7][4:6] = profile_spec.crc16.to_bytes(2, "big")
            result[7][6] = 4
            result[7][7] = 2
            if not health_valid:
                result[7][5] ^= 1
    return tuple(bytes(item) for item in result)


def feed_group(decoder, group):
    snapshot = None
    for payload in group:
        result = decoder.feed(decoder.can_id, payload)
        if result is not None:
            snapshot = result
    return snapshot


class CanTelemetryDecoderTest(unittest.TestCase):
    def test_core_group_decodes_raw_and_engineering_values(self):
        decoder = can_telemetry.Decoder("core32", 0x6F0)
        snapshot = feed_group(decoder, frames("core32", 0x1234))
        self.assertIsNotNone(snapshot)
        self.assertEqual(snapshot.tick16, 0x1234)
        self.assertEqual(snapshot.sequence, 0x14)
        self.assertTrue(snapshot.schema_verified)
        self.assertEqual(snapshot.fields["rpm_raw"], 0x0304)
        self.assertEqual(snapshot.fields["final_timing_raw"], 5)
        self.assertEqual(snapshot.fields["injection_0_raw"], 0x1213)
        physical = can_telemetry.engineering_values(snapshot)
        self.assertEqual(physical["rpm"], 0x0304 * 12.5)
        self.assertEqual(
            physical["injection_0_ms"], 0x1213 / 100
        )
        self.assertEqual(decoder.completed_groups, 1)

    def test_wide_contexts_and_in_band_health_verification(self):
        decoder = can_telemetry.Decoder("wide54", 0x6EF)
        temperature = feed_group(
            decoder, frames("wide54", 1, context_tag=0)
        )
        self.assertFalse(temperature.schema_verified)
        self.assertEqual(temperature.context_name, "temperatures_af")
        with self.assertRaises(can_telemetry.DecodeError):
            can_telemetry.engineering_values(temperature)

        health = feed_group(
            decoder, frames("wide54", 2, context_tag=3)
        )
        self.assertTrue(health.schema_verified)
        self.assertEqual(health.fields["snapshot_overrun_count"], 4)
        verified_temperature = feed_group(
            decoder, frames("wide54", 3, context_tag=0)
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

    def test_health_mismatch_is_rejected(self):
        decoder = can_telemetry.Decoder("wide54")
        result = feed_group(
            decoder,
            frames("wide54", 5, context_tag=3, health_valid=False),
        )
        self.assertIsNone(result)
        self.assertEqual(decoder.schema_mismatches, 1)
        self.assertEqual(decoder.completed_groups, 0)

    def test_loss_duplicate_reorder_and_preemption_are_visible(self):
        decoder = can_telemetry.Decoder("core32")
        first = frames("core32", 10)
        decoder.feed(decoder.can_id, first[0])
        decoder.feed(decoder.can_id, first[1])
        second = frames("core32", 11)
        snapshot = feed_group(decoder, second)
        self.assertEqual(snapshot.tick16, 11)
        self.assertEqual(decoder.incomplete_groups, 1)

        third = frames("core32", 12)
        decoder.feed(decoder.can_id, third[0])
        decoder.feed(decoder.can_id, third[2])
        self.assertGreaterEqual(decoder.malformed_frames, 1)
        self.assertGreaterEqual(decoder.incomplete_groups, 2)

        fourth = frames("core32", 13)
        decoder.feed(decoder.can_id, fourth[0])
        decoder.feed(decoder.can_id, fourth[1])
        decoder.feed(decoder.can_id, fourth[1])
        self.assertGreaterEqual(decoder.malformed_frames, 2)

    def test_tick_wrap_unwrap_and_stale_group_rejection(self):
        decoder = can_telemetry.Decoder("core32")
        before = feed_group(decoder, frames("core32", 0xFFFF))
        after = feed_group(decoder, frames("core32", 0x0000))
        self.assertEqual(before.unwrapped_tick, 0xFFFF)
        self.assertEqual(after.unwrapped_tick, 0x10000)
        duplicate = feed_group(decoder, frames("core32", 0x0000))
        self.assertIsNone(duplicate)
        self.assertGreaterEqual(decoder.malformed_frames, 1)

    def test_wrong_id_bad_length_bad_header_and_unknown_context_are_rejected(self):
        decoder = can_telemetry.Decoder("wide54", 0x6F0)
        self.assertIsNone(decoder.feed(0x6EF, bytes(8)))
        self.assertIsNone(decoder.feed(0x6F0, bytes(7)))
        bad_header = bytearray(frames("wide54", 1)[0])
        bad_header[0] ^= 0x08
        self.assertIsNone(decoder.feed(0x6F0, bad_header))
        unknown = frames("wide54", 2, context_tag=0x7F)
        self.assertIsNone(feed_group(decoder, unknown))
        self.assertGreaterEqual(decoder.malformed_frames, 3)

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
