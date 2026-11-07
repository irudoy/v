import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from patches import can_telemetry_profile
from tools.logs import can_telemetry
from tools.logs import can_telemetry_schema


def frames(profile, tick, *, context_tag=0, health_valid=True, identity=None,
           configuration=0):
    """Build one group; ``identity`` overrides the (ID, CRC) of tag 3 and
    ``configuration`` is the configuration byte of the dynamic page."""
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
    if profile_spec.dynamic is not None:
        dynamic = profile_spec.dynamic
        result[dynamic.page][dynamic.configuration_offset] = configuration
    for pad in manifest.padding:
        if pad.tag is None or pad.tag == context_tag:
            result[pad.page][pad.offset:pad.offset + pad.width] = bytes(pad.width)
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


def feed_timed(decoder, group, time):
    """Feed one group whose frames all arrive at ``time``."""
    snapshot = None
    for payload in group:
        result = decoder.feed(decoder.can_id, payload, time)
        if result is not None:
            snapshot = result
    return snapshot


TICK_SECONDS = 0.01024
# Host queueing delays each frame by a few milliseconds and never advances it.
QUEUE_DELAYS = (0.0, 0.004, 0.001, 0.007, 0.002)


def stream_times(count, pauses=None, stalls=()):
    """Recorded times of ticks 1..count with STOP pauses and host stalls.

    ``pauses`` maps the first tick after START to the stopped seconds; a stall
    (index, length) holds that many snapshots until the next one arrives and
    drains them as one burst.
    """
    pauses = pauses or {}
    ticks = list(range(1, count + 1))
    stopped = 0.0
    times = []
    for index, tick in enumerate(ticks):
        stopped += pauses.get(tick, 0.0)
        times.append(tick * TICK_SECONDS + stopped + QUEUE_DELAYS[index % 5])
    for index, length in stalls:
        for held in range(index, index + length):
            times[held] = times[index + length]
    return ticks, times


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
        for key in ("conversion", "candidate", "unit", "values", "bits"):
            field.pop(key, None)
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
            health[3] = profile["id"]
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
        self.assertIsNone(snapshot.profile_id)
        self.assertEqual(snapshot.fields["request_flow_raw"], 0x0304)
        self.assertEqual(snapshot.fields["final_timing_raw"], 5)
        self.assertEqual(snapshot.fields["injection_0_raw"], 0x1213)
        self.assertNotIn("injection_end_angle_raw", snapshot.fields)
        self.assertIn("torque_transition_state_raw", snapshot.fields)
        self.assertIn("transmission_reduction_state_raw", snapshot.fields)
        self.assertIn("throttle_request_bounded_raw", snapshot.fields)
        with self.assertRaises(can_telemetry.DecodeError):
            can_telemetry.engineering_values(snapshot, decoder.calibrations)
        self.assertEqual(decoder.completed_groups, 1)

    def test_context_pairs_and_in_band_health_verification(self):
        decoder = can_telemetry.Decoder("tuning", 0x6EF)
        temperature = feed_group(
            decoder, frames("tuning", 1, context_tag=0)
        )
        self.assertFalse(temperature.schema_verified)
        self.assertIsNone(temperature.profile_id)
        self.assertEqual(
            temperature.context_name,
            "temperatures_and_b2_trim_terms + launch_abort_voltage_and_trim_terms",
        )
        self.assertIn("ltft_learned_b1_raw", temperature.fields)
        self.assertIn("ltft_learned_b2_raw", temperature.fields)
        self.assertIn("ltft_adjustment_b2_raw", temperature.fields)
        self.assertIn("rolling_launch_abort_reason", temperature.fields)
        with self.assertRaises(can_telemetry.DecodeError):
            can_telemetry.engineering_values(temperature, decoder.calibrations)

        health = feed_group(
            decoder, frames("tuning", 2, context_tag=3)
        )
        self.assertTrue(health.schema_verified)
        self.assertEqual(health.fields["snapshot_overrun_count"], 4)
        verified_temperature = feed_group(
            decoder, frames("tuning", 3, context_tag=0)
        )
        self.assertTrue(verified_temperature.schema_verified)
        self.assertEqual(
            verified_temperature.profile_id, decoder.profile["id"]
        )
        self.assertEqual(verified_temperature.fields["request_flow_raw"], 0x0304)
        self.assertEqual(
            verified_temperature.context_name,
            "temperatures_and_b2_trim_terms + launch_abort_voltage_and_trim_terms",
        )
        self.assertIn("rolling_launch_abort_reason", verified_temperature.fields)
        physical = can_telemetry.engineering_values(
            verified_temperature, decoder.calibrations
        )
        self.assertEqual(
            physical["coolant"],
            verified_temperature.fields["coolant_raw"] - 50,
        )
        fixed_physical = can_telemetry.engineering_values(
            health, decoder.calibrations
        )
        self.assertEqual(
            fixed_physical["intake_cvtc_actual_b1"],
            health.fields["intake_cvtc_actual_b1_raw"] * 0.5 - 64,
        )
        self.assertAlmostEqual(
            fixed_physical["calculated_load"],
            health.fields["calculated_load_raw"] * 100 / 255,
        )
        self.assertAlmostEqual(
            fixed_physical["engine_torque_state"],
            health.fields["engine_torque_state_raw"],
        )
        self.assertAlmostEqual(
            physical["battery_voltage"],
            verified_temperature.fields["battery_voltage_raw"] * 0.08,
        )
        self.assertAlmostEqual(
            physical["ltft_learned_b1"],
            verified_temperature.fields["ltft_learned_b1_raw"] / 256 - 100,
        )
        self.assertAlmostEqual(
            physical["ltft_learned_b2"],
            verified_temperature.fields["ltft_learned_b2_raw"] / 256 - 100,
        )
        for name in ("transmission_reduction_state", "torque_transition_state"):
            self.assertEqual(fixed_physical[name], health.fields[name + "_raw"])
        self.assertNotIn("injection_end_angle_raw", health.fields)

        trims = feed_group(
            decoder, frames("tuning", 4, context_tag=1)
        )
        trim_physical = can_telemetry.engineering_values(
            trims, decoder.calibrations
        )
        self.assertAlmostEqual(
            trim_physical["stft_b1"],
            trims.fields["stft_b1_raw"] / 256 - 100,
        )
        self.assertEqual(
            trims.context_name,
            "short_fuel_trim_cvtc_duty"
            " + air_oil_temperature_and_af_state",
        )
        for bank in (1, 2):
            self.assertAlmostEqual(
                trim_physical[f"intake_cvtc_duty_b{bank}"],
                trims.fields[f"intake_cvtc_duty_b{bank}_raw"] * 39 / 100,
            )
            self.assertNotIn(f"intake_cvtc_duty_command_b{bank}_raw", trims.fields)
        self.assertAlmostEqual(
            trim_physical["injection_end_angle"],
            trims.fields["injection_end_angle_raw"] * 2 - 590,
        )

    def test_verification_ends_with_its_run(self):
        decoder = can_telemetry.Decoder("tuning")
        health = feed_group(decoder, frames("tuning", 0x281F, context_tag=3))
        self.assertEqual(health.profile_id, decoder.profile["id"])
        restarted = feed_group(decoder, frames("tuning", 1))
        self.assertEqual(restarted.run, 1)
        self.assertFalse(restarted.schema_verified)
        self.assertIsNone(restarted.profile_id)

    def test_another_profile_identity_is_rejected(self):
        decoder = can_telemetry.Decoder("tuning")
        feed_group(decoder, frames("tuning", 1, context_tag=3))
        self.assertTrue(decoder.schema_verified)
        profile_id, crc16 = decoder.profile["id"], decoder.profile["_crc16"]
        for identity in (
            (profile_id - 1, crc16),
            (profile_id, crc16 ^ 1),
            (profile_id + 1, crc16 ^ 0x8000),
        ):
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
                self.assertFalse(decoder.schema_verified)
        self.assertEqual(decoder.schema_mismatches, 3)

    def test_health_mismatch_is_rejected(self):
        decoder = can_telemetry.Decoder("tuning")
        result = feed_group(
            decoder,
            frames("tuning", 5, context_tag=3, health_valid=False),
        )
        self.assertIsNone(result)
        self.assertEqual(decoder.schema_mismatches, 1)
        self.assertEqual(decoder.completed_groups, 0)

    def test_reported_identity_survives_rejection_until_replaced(self):
        for offset in (2, 3, 5):
            with self.subTest(offset=offset):
                decoder = can_telemetry.Decoder("tuning")
                group = list(frames("tuning", 5, context_tag=3))
                health = bytearray(group[9])
                health[offset] ^= 1
                group[9] = bytes(health)
                reported = (health[2], health[3], int.from_bytes(health[4:6], "big"))
                self.assertIsNone(feed_group(decoder, group))
                self.assertEqual(decoder.reported_identity, reported)
                self.assertNotEqual(reported, decoder.expected_identity)

                waiting = feed_group(decoder, frames("tuning", 6))
                self.assertFalse(waiting.schema_verified)
                self.assertEqual(decoder.reported_identity, reported)
                matching = feed_group(decoder, frames("tuning", 7, context_tag=3))
                self.assertTrue(matching.schema_verified)
                self.assertEqual(decoder.reported_identity, decoder.expected_identity)

    def test_a_restart_clears_the_previous_identity_but_keeps_a_new_mismatch(self):
        decoder = can_telemetry.Decoder("tuning")
        feed_group(decoder, frames("tuning", 512, context_tag=3))
        restarted = feed_group(decoder, frames("tuning", 1))
        self.assertFalse(restarted.schema_verified)
        self.assertIsNone(decoder.reported_identity)

        # A mismatch can be the first complete group after another restart.
        feed_group(decoder, frames("tuning", 512, context_tag=3))
        feed_group(decoder, frames("tuning", 2, context_tag=3, health_valid=False))
        reported = decoder.reported_identity
        self.assertIsNotNone(reported)
        following = feed_group(decoder, frames("tuning", 3))
        self.assertFalse(following.schema_verified)
        self.assertEqual(decoder.reported_identity, reported)

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

    def test_tick_step_classifies_steps_by_tick_and_receive_time(self):
        step = can_telemetry.tick_step
        forward = can_telemetry.TickStep.FORWARD
        restart = can_telemetry.TickStep.RESTART
        stale = can_telemetry.TickStep.STALE
        cases = (
            # Without receive times only the opening window marks a restart.
            (0x2820, 0x0003, None, restart),
            (0x2820, 0x0300, None, stale),
            (0x9000, 0x0300, None, forward),
            (0x2820, 0x2820, None, stale),
            # A step back after a receive pause opens a new run.
            (0x2820, 0x0300, 1.0, restart),
            (0x2820, 0x281F, 0.6, restart),
            (0x2820, 0x281F, 0.5, stale),
            (0x2820, 0x2820, 60.0, stale),
            # A forward step longer than the receive time opens a new run.
            (0x9000, 0x0300, 1.0, restart),
            # (1.0 + 1.0) / 0.01024 + 1 = 196.3 ticks.
            (0x2820, 0x2820 + 197, 1.0, restart),
            (0x2820, 0x2820 + 196, 1.0, forward),
            (0xFFFF, 0x0000, 0.01, forward),
            (0x2820, 0x2821, 60.0, forward),
            # A pause longer than the step of a new run hides the restart.
            (0x0100, 0x0180, 5.0, forward),
            # A receive time that runs backwards or is not finite is unknown.
            (0x2820, 0x0300, -1.0, stale),
            (0x9000, 0x0300, float("nan"), forward),
        )
        for previous, tick16, elapsed, expected in cases:
            with self.subTest(previous=previous, tick16=tick16, elapsed=elapsed):
                self.assertIs(step(previous, tick16, elapsed), expected)
        self.assertIsNone(can_telemetry.receive_gap(None, 1.0))
        self.assertIsNone(can_telemetry.receive_gap(1.0, float("inf")))
        self.assertEqual(can_telemetry.receive_gap(1.0, 1.5), 0.5)

    def test_a_restart_past_the_opening_window_opens_a_new_run(self):
        for before in (0x2820, 0x9000):
            with self.subTest(before=hex(before)):
                decoder = can_telemetry.Decoder("tuning")
                feed_timed(decoder, frames("tuning", before - 1, context_tag=3), 9.99)
                self.assertTrue(decoder.schema_verified)
                feed_timed(decoder, frames("tuning", before), 10.0)
                restarted = feed_timed(decoder, frames("tuning", 0x0300), 11.0)
                self.assertIsNotNone(restarted)
                self.assertEqual(restarted.run, 1)
                self.assertEqual(restarted.unwrapped_tick, 0x0300)
                self.assertFalse(restarted.schema_verified)
                self.assertEqual(decoder.producer_restarts, 1)
                following = feed_timed(
                    decoder, frames("tuning", 0x0301, context_tag=3), 11.01
                )
                self.assertEqual(following.run, 1)
                self.assertEqual(following.unwrapped_tick, 0x0301)
                self.assertTrue(following.schema_verified)

    def test_a_repeated_or_reordered_group_within_the_pause_is_rejected(self):
        decoder = can_telemetry.Decoder("tuning")
        feed_timed(decoder, frames("tuning", 0x2820), 10.0)
        feed_timed(decoder, frames("tuning", 0x2821), 10.01)
        self.assertIsNone(feed_timed(decoder, frames("tuning", 0x2821), 10.02))
        self.assertIsNone(feed_timed(decoder, frames("tuning", 0x2820), 10.03))
        self.assertEqual(decoder.producer_restarts, 0)
        self.assertGreaterEqual(decoder.malformed_frames, 2)
        following = feed_timed(decoder, frames("tuning", 0x2822), 10.04)
        self.assertEqual((following.run, following.unwrapped_tick), (0, 0x2822))

    def test_wrap_pause_and_drained_stall_stay_in_one_run(self):
        decoder = can_telemetry.Decoder("tuning")
        feed_timed(decoder, frames("tuning", 0xFFFF), 10.0)
        wrapped = feed_timed(decoder, frames("tuning", 0x0000), 10.01)
        self.assertEqual(wrapped.unwrapped_tick, 0x10000)
        # STOP holds the tick for a minute.
        resumed = feed_timed(decoder, frames("tuning", 0x0001), 70.0)
        self.assertEqual(resumed.unwrapped_tick, 0x10001)
        # A host stall drains 64 groups with one receive time.
        for tick in range(0x0002, 0x0042):
            drained = feed_timed(decoder, frames("tuning", tick), 70.7)
            self.assertIsNotNone(drained)
        self.assertEqual(drained.unwrapped_tick, 0x10041)
        self.assertEqual(drained.run, 0)
        self.assertEqual(decoder.producer_restarts, 0)

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


class DynamicPageTest(unittest.TestCase):
    """The configuration byte selects the placement of the dynamic page."""

    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads(can_telemetry.DEFAULT_SCHEMA.read_text(encoding="utf-8"))
        cls.frames = json.loads(
            can_telemetry.DEFAULT_CONFIGURATION_FRAMES.read_text(encoding="utf-8")
        )
        cls.profile = can_telemetry.load_schema()[1]["tuning"]
        cls.page = cls.profile["dynamic"]["page"]

    def decode(self, selector, data):
        decoder = can_telemetry.Decoder("tuning")
        group = [bytearray(page) for page in frames("tuning", 1, configuration=selector)]
        group[self.page][1:7] = data
        return decoder, feed_group(decoder, group)

    def test_the_default_configuration_carries_the_fixed_fields(self):
        decoder, snapshot = self.decode(0, bytes((1, 2, 3, 4, 5, 6)))
        self.assertEqual(snapshot.fields["telemetry_page_configuration"], 0)
        self.assertEqual(snapshot.fields["exhaust_cvtc_actual_b1_raw"], 6)
        self.assertEqual(snapshot.fields["torque_transition_state_raw"], 0x0405)
        self.assertNotIn("rolling_launch_speed_error_raw", snapshot.fields)
        self.assertEqual(decoder.unknown_configurations, 0)

    def test_a_configuration_places_its_slots_in_order(self):
        data = (-25).to_bytes(2, "big", signed=True) + (523).to_bytes(2, "big") + bytes((7, 40))
        decoder, snapshot = self.decode(1, data)
        self.assertEqual(snapshot.fields["rolling_launch_speed_error_raw"], -25)
        self.assertEqual(snapshot.fields["rolling_launch_torque_fraction_raw"], 523)
        self.assertEqual(snapshot.fields["rolling_launch_cut_counter"], 7)
        self.assertEqual(snapshot.fields["ignition_dwell_angle_raw"], 40)
        self.assertNotIn("exhaust_cvtc_actual_b1_raw", snapshot.fields)
        self.assertNotIn("torque_transition_state_raw", snapshot.fields)
        self.assertEqual(decoder.unknown_configurations, 0)

    def test_group_one_of_a_two_group_configuration_is_zero_padded(self):
        data = (-32).to_bytes(2, "big", signed=True) + bytes((3, 9, 0, 0))
        decoder, snapshot = self.decode(0x82, data)
        self.assertEqual(snapshot.fields["rolling_launch_integrator_raw"], -32)
        self.assertEqual(snapshot.fields["speed_frame_receive_age_raw"], 3)
        self.assertEqual(snapshot.fields["rolling_launch_cut_counter"], 9)
        self.assertNotIn("rolling_launch_speed_error_raw", snapshot.fields)
        self.assertEqual(decoder.unknown_configurations, 0)

    def test_an_undefined_layout_leaves_the_page_undecoded(self):
        cases = {
            "unknown ID": (7, bytes(6)),
            "group of a one-group configuration": (0x81, bytes(6)),
            "group 1 of the default": (0x80, bytes(6)),
            "bytes after the slots": (0x82, bytes((0, 1, 2, 3, 0, 1))),
        }
        for name, (selector, data) in cases.items():
            with self.subTest(name=name):
                decoder, snapshot = self.decode(selector, data)
                self.assertIsNotNone(snapshot)
                self.assertEqual(decoder.unknown_configurations, 1)
                self.assertEqual(snapshot.fields["telemetry_page_configuration"], selector)
                self.assertFalse(
                    can_telemetry.dynamic_field_names(self.profile) & snapshot.fields.keys()
                )

    def test_invalid_configurations_are_refused(self):
        def mutate(change):
            raw = json.loads(json.dumps(self.raw))
            change(raw["profiles"][0])
            return raw

        def widen(profile):
            profile["configurations"][0]["groups"][0].append(
                "rolling_launch_integrator_raw"
            )

        def repeat_field(profile):
            profile["dynamic_fields"][0]["name"] = "coolant_raw"

        def place(profile):
            profile["dynamic_fields"][0]["offset"] = 1

        def no_dynamic(profile):
            del profile["dynamic"]
            profile["crc16_ccitt_false"] = "0x%04X" % can_telemetry_schema.profile_crc16(
                profile, self.raw["protocol_version"]
            )

        cases = {
            "group wider than the data bytes": widen,
            "ID 0": lambda profile: profile["configurations"][0].update(id=0),
            "ID 128": lambda profile: profile["configurations"][0].update(id=128),
            "repeated ID": lambda profile: profile["configurations"][1].update(id=1),
            "three groups": lambda profile: profile["configurations"][1]["groups"].append(
                ["rolling_launch_cut_counter"]
            ),
            "unknown slot": lambda profile: profile["configurations"][0]["groups"][0].append("x"),
            "slot named like a field": repeat_field,
            "slot with a placement": place,
            "configurations without a dynamic page": no_dynamic,
        }
        for name, change in cases.items():
            with self.subTest(name=name):
                with self.assertRaises(can_telemetry.DecodeError):
                    can_telemetry.parse_schema(mutate(change))

    def test_slot_fields_join_the_profile_fields_and_calibrations(self):
        names = [field["name"] for field in can_telemetry.profile_fields(self.profile)]
        self.assertEqual(len(names), len(set(names)))
        self.assertIn("rolling_launch_speed_error_raw", names)
        calibration = can_telemetry.calibrations(self.profile)["rolling_launch_integrator_raw"]
        self.assertAlmostEqual(calibration.apply(-32), -0.2)
        self.assertEqual(
            can_telemetry.configuration_labels(self.profile)[0], "Default"
        )

    def test_configuration_commands_follow_the_schema_groups(self):
        can_id, commands = can_telemetry_schema.configuration_commands(
            self.frames, self.profile, 0x6F0, 4
        )
        self.assertEqual(can_id, 0x6F1)
        self.assertEqual(
            [command for command, _payload in commands],
            ["page-set"] * 6 + ["page-commit"],
        )
        descriptors = [payload[2] for _command, payload in commands[:-1]]
        self.assertEqual(descriptors, [0x04, 0x11, 0x21, 0x82, 0x92, 0xA2])
        self.assertEqual(commands[-1][1][:6], bytes((0xC2, 4, 2, 3, 3, 0)))
        for command, payload in commands:
            self.assertEqual(payload[1], 4)
            if command == "page-set":
                self.assertEqual(payload[3], 0xFF)
            self.assertEqual(
                int.from_bytes(payload[6:], "big"),
                can_telemetry_schema.crc16_ccitt_false(payload[:6]),
            )
        _can_id, (default,) = can_telemetry_schema.configuration_commands(
            self.frames, self.profile, 0x6F0, 0
        )
        self.assertEqual(default, ("page-default", bytes.fromhex("C00000000000B020")))

    def test_configuration_commands_refuse_frames_that_differ(self):
        def tampered(change):
            frames = json.loads(json.dumps(self.frames))
            change(frames)
            return frames

        def swap(frames):
            row = frames["configurations"][0]
            row["frames"][0], row["frames"][1] = row["frames"][1], row["frames"][0]

        def corrupt(frames):
            row = frames["configurations"][0]
            row["frames"][0] = row["frames"][0][:-1] + ("1" if row["frames"][0][-1] == "0" else "0")

        cases = {
            "swapped slots": (tampered(swap), 3),
            "corrupt CRC": (tampered(corrupt), 3),
            "dropped commit": (
                tampered(lambda frames: frames["configurations"][0]["frames"].pop()), 3
            ),
            "other profile": (tampered(lambda frames: frames.update(profile="x")), 0),
            "undefined ID": (self.frames, 9),
            "historical ID": (self.frames, 1),
        }
        for name, (frames, configuration_id) in cases.items():
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    can_telemetry_schema.configuration_commands(
                        frames, self.profile, 0x6F0, configuration_id
                    )
        with self.assertRaises(ValueError):
            can_telemetry_schema.configuration_commands(
                self.frames, self.profile, 0x7FF, 3
            )


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


def schema_document():
    return json.loads(can_telemetry.DEFAULT_SCHEMA.read_text(encoding="utf-8"))


def load_document(document):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "schema.json"
        path.write_text(json.dumps(document), encoding="utf-8")
        return can_telemetry.load_schema(path)


def field_of(document, name):
    for field in can_telemetry.profile_fields(document["profiles"][0]):
        if field["name"] == name:
            return field
    raise KeyError(name)


class HistoricalSchemaTest(unittest.TestCase):
    """A decoder of a later profile reads the recordings of a frozen one."""

    FROZEN = (2, 9, 24047)

    @staticmethod
    def later_schema(directory, profile_id=10):
        """The current schema under another profile ID and its CRC."""
        raw = json.loads(can_telemetry.DEFAULT_SCHEMA.read_text(encoding="utf-8"))
        profile = raw["profiles"][0]
        profile["id"] = profile_id
        crc16 = can_telemetry_schema.profile_crc16(profile, raw["protocol_version"])
        profile["crc16_ccitt_false"] = f"0x{crc16:04X}"
        path = Path(directory) / "schema.json"
        path.write_text(json.dumps(raw), encoding="utf-8")
        return path, crc16

    def test_the_history_registry_binds_the_frozen_schemas(self):
        from patches import can_telemetry_history

        named = {
            endpoint.key: endpoint.host_schema
            for endpoint in can_telemetry_history.endpoints()
            if endpoint.host_schema is not None
        }
        self.assertEqual(named, {"schema2-profile9": "can-telemetry-schema-profile9.json"})
        self.assertEqual(
            {path.name for path in can_telemetry.HISTORICAL_SCHEMAS}, set(named.values())
        )
        for path in can_telemetry.HISTORICAL_SCHEMAS:
            self.assertEqual(path.parent, can_telemetry_history.REGISTRY.parent)

    def test_a_later_profile_decodes_a_frozen_profile_stream(self):
        with tempfile.TemporaryDirectory() as directory:
            later, crc16 = self.later_schema(directory)
            decoder = can_telemetry.Decoder("tuning", schema_path=later)
            strict = can_telemetry.Decoder(
                "tuning", schema_path=later, historical_schemas=()
            )
        self.assertEqual(decoder.expected_identity, (2, 10, crc16))
        self.assertEqual(decoder.accepted_identities, {(2, 10, crc16), self.FROZEN})
        frozen = frames("tuning", 1, context_tag=3, identity=self.FROZEN[1:], configuration=1)
        snapshot = feed_group(decoder, frozen)
        self.assertTrue(snapshot.schema_verified)
        self.assertEqual(snapshot.profile_id, 9)
        self.assertIn("rolling_launch_speed_error_raw", snapshot.fields)
        # Profile 9 defines no schema 6 configuration.
        snapshot = feed_group(decoder, frames("tuning", 2, configuration=3))
        self.assertEqual(decoder.unknown_configurations, 1)
        self.assertNotIn("rolling_launch_law_output_raw", snapshot.fields)
        self.assertIsNone(feed_group(strict, frozen))
        self.assertEqual(strict.schema_mismatches, 1)
        foreign = frames("tuning", 3, context_tag=3, identity=(11, 0x1234))
        self.assertIsNone(feed_group(decoder, foreign))
        self.assertEqual(decoder.schema_mismatches, 1)

    def test_a_later_profile_stream_takes_the_later_layout(self):
        with tempfile.TemporaryDirectory() as directory:
            later, crc16 = self.later_schema(directory)
            decoder = can_telemetry.Decoder("tuning", schema_path=later)
        feed_group(decoder, frames("tuning", 1, context_tag=3, identity=self.FROZEN[1:]))
        group = frames("tuning", 2, context_tag=3, identity=(10, crc16), configuration=3)
        snapshot = feed_group(decoder, group)
        self.assertEqual(snapshot.profile_id, 10)
        self.assertIn("rolling_launch_law_output_raw", snapshot.fields)
        self.assertEqual(decoder.unknown_configurations, 0)

    def test_the_frozen_profile_fields_are_fields_of_the_current_profile(self):
        """The host presents a frozen profile through the current one."""
        current = {
            field["name"]: field
            for field in can_telemetry.profile_fields(can_telemetry.load_schema()[1]["tuning"])
        }
        for path in can_telemetry.HISTORICAL_SCHEMAS:
            profile = can_telemetry.load_schema(path)[1]["tuning"]
            for field in can_telemetry.profile_fields(profile):
                with self.subTest(schema=path.name, field=field["name"]):
                    other = current[field["name"]]
                    for key in ("width", "signed", "conversion", "unit", "candidate"):
                        self.assertEqual(field.get(key), other.get(key))
                    for key in ("values", "bits"):
                        self.assertLessEqual(
                            {json.dumps(item, sort_keys=True) for item in field.get(key, ())},
                            {json.dumps(item, sort_keys=True) for item in other.get(key, ())},
                        )


class ScaleTermsTest(unittest.TestCase):
    """A scale string states what a host needs of its field."""

    def test_arithmetic_gives_the_affine_conversion_and_the_unit(self):
        cases = (
            ("raw / 256 - 100 percent", 1 / 256, -100, "percent", False),
            ("raw * 0.5 - 64 degCA", 0.5, -64, "degCA", False),
            ("raw * 100 / 255 percent", 100 / 255, 0, "percent", False),
            ("raw - 50 degC", 1, -50, "degC", False),
            ("candidate raw * 0.1 Nm", 0.1, 0, "Nm", True),
            ("110 - raw degBTDC", -1, 110, "degBTDC", False),
            ("raw degBTDC", 1, 0, "degBTDC", False),
            ("raw / 16384 ratio", 2**-14, 0, "ratio", False),
            ("raw * 2 - 590 degCA", 2, -590, "degCA", False),
            ("100 - raw / 2 percent", -0.5, 100, "percent", False),
            ("raw * 34285 / 1114112 percent", 34285 / 1114112, 0, "percent", False),
            ("raw + 1; any other value selects Map 1", 1, 1, None, False),
            ("candidate raw * 0.002 ratio", 0.002, 0, "ratio", True),
        )
        for scale, factor, offset, unit, candidate in cases:
            with self.subTest(scale=scale):
                terms = can_telemetry_schema.scale_terms(scale)
                self.assertAlmostEqual(terms["conversion"]["factor"], factor)
                self.assertAlmostEqual(terms["conversion"]["offset"], offset)
                self.assertEqual(terms.get("unit"), unit)
                self.assertIs(terms["candidate"], candidate)

    def test_named_scales_give_their_values_and_bits(self):
        self.assertEqual(
            can_telemetry_schema.scale_terms(
                "enumeration: 1 ACTIVE, 0 IDLE, 2 COOLDOWN"
            ),
            {
                "values": [
                    {"value": 0, "name": "IDLE"},
                    {"value": 1, "name": "ACTIVE"},
                    {"value": 2, "name": "COOLDOWN"},
                ]
            },
        )
        self.assertEqual(
            can_telemetry_schema.scale_terms("bits: 6 HIGH_DETONATION"),
            {"bits": [{"bit": 6, "name": "HIGH_DETONATION"}]},
        )

    def test_a_packed_scale_gives_its_field_and_bits(self):
        self.assertEqual(
            can_telemetry_schema.scale_terms(
                "field 0 through 9 raw / 10 percent; bits: 15 READY, 14 SPEED"
            ),
            {
                "field": {
                    "low": 0,
                    "high": 9,
                    "conversion": {"factor": 0.1, "offset": 0.0},
                    "candidate": False,
                    "unit": "percent",
                },
                "bits": [{"bit": 14, "name": "SPEED"}, {"bit": 15, "name": "READY"}],
            },
        )
        self.assertEqual(
            can_telemetry_schema.scale_terms(
                "field 0 through 1 enumeration: 0 NONE, 2 SPEED; bits: 7 READY"
            ),
            {
                "field": {
                    "low": 0,
                    "high": 1,
                    "values": [{"value": 0, "name": "NONE"}, {"value": 2, "name": "SPEED"}],
                },
                "bits": [{"bit": 7, "name": "READY"}],
            },
        )

    def test_a_packed_scale_keeps_its_value_apart_from_its_bits(self):
        for scale in (
            "field 0 through 5 bit mask; bits: 6 READY",
            "field 0 through 5 raw deg; bits: 5 READY",
            "field 2 through 1 raw deg; bits: 7 READY",
            "field 0 through 5 raw deg; bits: 32 READY",
            "field 0 through 1 enumeration: 0 NONE, 4 FAR; bits: 7 READY",
        ):
            with self.subTest(scale=scale), self.assertRaises(ValueError):
                can_telemetry_schema.scale_terms(scale)

    def test_a_description_without_raw_states_nothing(self):
        for scale in (
            "bit mask",
            "base scheduler ticks",
            "CRC-16/CCITT-FALSE",
            "Q14 factor",
            "signed internal request coordinate",
        ):
            with self.subTest(scale=scale):
                self.assertEqual(can_telemetry_schema.scale_terms(scale), {})

    def test_arithmetic_that_does_not_parse_is_refused(self):
        for scale in (
            "raw target coordinate",
            "raw * raw V",
            "raw / raw V",
            "raw / 0 V",
            "raw - raw V",
            "raw + V",
            "raw 2 V",
            "raw + 1 map number",
            "enumeration: the latest, 0 NONE",
            "bits: 0 CYLINDER_1, 0 CYLINDER_2",
            "enumeration: 0 NONE, 1 NONE",
        ):
            with self.subTest(scale=scale), self.assertRaises(ValueError):
                can_telemetry_schema.scale_terms(scale)


class HostContractTest(unittest.TestCase):
    """The schema carries the conversion and presentation of each field."""

    def test_calibrations_follow_the_scales_under_engineering_keys(self):
        calibrations = can_telemetry.Decoder("tuning").calibrations
        self.assertEqual(
            calibrations["coolant_raw"],
            can_telemetry.Calibration("coolant", 1.0, -50.0),
        )
        self.assertEqual(
            calibrations["apc_command_raw"],
            can_telemetry.Calibration("apc_command", -1.0, 110.0),
        )
        self.assertEqual(
            calibrations["active_map_index"],
            can_telemetry.Calibration("active_map_index", 1.0, 1.0),
        )
        self.assertAlmostEqual(
            calibrations["calculated_load_raw"].factor, 100 / 255
        )
        for name in (
            "knock_margin_min_ch1_raw",
            "rolling_launch_phase",
            "fuel_inhibit_mask",
            "profile_crc16",
        ):
            self.assertNotIn(name, calibrations)
        for name, calibration in calibrations.items():
            self.assertEqual(
                calibration.target, can_telemetry.engineering_key(name)
            )

    def test_display_units_spell_the_scale_unit_and_mark_candidates(self):
        document = schema_document()
        for name, unit in {
            "stft_b1_raw": "%",
            "af_state_factor_raw": "",
            "af_adjustment_b1_raw": "*",
            "engine_torque_state_raw": "cnt",
            "coolant_raw": "degC",
            "knock_margin_min_ch1_raw": "cnt",
            "fuel_inhibit_mask": "",
        }.items():
            with self.subTest(name=name):
                self.assertEqual(
                    can_telemetry.display_unit(field_of(document, name)), unit
                )

    def test_a_field_without_a_presentation_loads(self):
        document = schema_document()
        del field_of(document, "tick16")["dashboard"]
        _raw, profiles = load_document(document)
        self.assertIn("tuning", profiles)

    def test_keys_that_differ_from_the_scale_are_refused(self):
        def factor(field):
            field["conversion"]["factor"] = 0.02

        def unit(field):
            del field["unit"]

        def values(field):
            field["values"][0]["name"] = "WAITING"

        def conversion(field):
            field["conversion"] = {"factor": 1.0, "offset": 0.0}

        for name, change in (
            ("maf_total_raw", factor),
            ("coolant_raw", unit),
            ("rolling_launch_phase", values),
            ("telemetry_status", conversion),
        ):
            document = schema_document()
            change(field_of(document, name))
            with self.subTest(name=name), self.assertRaisesRegex(
                can_telemetry.DecodeError, "differs from the conversion"
            ):
                load_document(document)

    def test_an_invalid_presentation_is_refused(self):
        def unit(document):
            field_of(document, "coolant_raw")["dashboard"]["unit"] = "C"

        def label(document):
            field_of(document, "iat_raw")["dashboard"]["label"] = "Coolant"

        def feed_key(document):
            field_of(document, "iat_raw")["dashboard"]["feed"]["key"] = (
                "coolant_c"
            )

        def feed_range(document):
            field_of(document, "coolant_raw")["dashboard"]["feed"][
                "minimum"
            ] = 200

        def order(document):
            field_of(document, "coolant_raw")["dashboard"]["order"] = 10

        def unknown(document):
            field_of(document, "coolant_raw")["dashboard"]["color"] = "red"

        def digits(document):
            del field_of(document, "coolant_raw")["dashboard"]["digits"]

        def raw_feed(document):
            feed = dict(field_of(document, "coolant_raw")["dashboard"]["feed"])
            feed.update(key="knock_count", name="VQ Knock Count")
            field_of(document, "knock_count_latched")["dashboard"]["feed"] = (
                feed
            )

        for change, message in (
            (unit, "states a unit that the scale states"),
            (label, "repeats the presentation label"),
            (feed_key, "repeats the presentation key"),
            (feed_range, "invalid feed channel"),
            (order, "invalid presentation"),
            (unknown, "presentation keys"),
            (digits, "invalid presentation"),
            (raw_feed, "publishes a field without a conversion"),
        ):
            document = schema_document()
            change(document)
            with self.subTest(change=change.__name__), self.assertRaisesRegex(
                can_telemetry.DecodeError, message
            ):
                load_document(document)

    def test_the_decoder_nests_engineering_values_by_engineering_key(self):
        lines = []
        for tick, tag in ((1, 3), (2, 0), (3, 2)):
            for payload in frames("tuning", tick, context_tag=tag):
                lines.append(f"(0.{tick:06d}) can0 6F0#{payload.hex().upper()}")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "capture.log"
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(
                io.StringIO()
            ):
                self.assertEqual(can_telemetry.main([str(path)]), 0)
        rows = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual(len(rows), 3)
        for row in rows:
            self.assertTrue(row["schema_verified"])
            self.assertNotIn("coolant", row)
            self.assertEqual(
                row["engineering"]["maf_total"], row["maf_total_raw"] / 100
            )
        self.assertEqual(
            rows[1]["engineering"]["coolant"], rows[1]["coolant_raw"] - 50
        )
        self.assertEqual(
            rows[2]["engineering"]["active_map_index"],
            rows[2]["active_map_index"] + 1,
        )


class StreamPauseTest(unittest.TestCase):
    def pauses(self, ticks, times):
        return can_telemetry.stream_pauses(ticks, times, TICK_SECONDS)

    def test_a_running_stream_has_no_pause(self):
        self.assertEqual(set(self.pauses(*stream_times(600))), {0.0})

    def test_a_stop_pause_keeps_its_recorded_time(self):
        pauses = self.pauses(*stream_times(600, pauses={301: 5.0}))
        self.assertAlmostEqual(pauses[300], 5.0, places=9)
        self.assertEqual(sum(1 for pause in pauses if pause), 1)

    def test_a_drained_host_stall_is_not_a_pause(self):
        ticks, times = stream_times(600, stalls=((300, 30),))
        self.assertGreater(times[300] - times[299], can_telemetry.STREAM_GAP_SECONDS)
        self.assertEqual(set(self.pauses(ticks, times)), {0.0})

    def test_a_stall_after_start_keeps_the_pause_time(self):
        ticks, times = stream_times(600, pauses={301: 5.0}, stalls=((300, 30),))
        pauses = self.pauses(ticks, times)
        self.assertAlmostEqual(pauses[300], 5.0, places=9)
        self.assertEqual(sum(1 for pause in pauses if pause), 1)

    def test_pauses_and_stalls_are_told_apart_in_one_stream(self):
        ticks, times = stream_times(
            1200, pauses={301: 2.0, 901: 0.5}, stalls=((600, 40), (1000, 15))
        )
        pauses = self.pauses(ticks, times)
        self.assertEqual(
            [index for index, pause in enumerate(pauses) if pause], [300, 900]
        )
        self.assertAlmostEqual(pauses[300], 2.0, places=9)
        self.assertAlmostEqual(pauses[900], 0.5, places=9)


if __name__ == "__main__":
    unittest.main()
