import contextlib
import io
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
        self.assertIn("injection_end_angle_raw", snapshot.fields)
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
            "temperatures_af + launch_abort_voltage_and_trim_terms",
        )
        self.assertIn("ltft_learned_b1_raw", temperature.fields)
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
            "temperatures_af + launch_abort_voltage_and_trim_terms",
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
            " + exhaust_cvtc_duty_and_intake_duty_command",
        )
        for bank in (1, 2):
            self.assertAlmostEqual(
                trim_physical[f"intake_cvtc_duty_b{bank}"],
                trims.fields[f"intake_cvtc_duty_b{bank}_raw"] * 39 / 100,
            )
            self.assertAlmostEqual(
                trim_physical[f"intake_cvtc_duty_command_b{bank}"],
                trims.fields[f"intake_cvtc_duty_command_b{bank}_raw"]
                * 39
                / 100,
            )
        self.assertAlmostEqual(
            fixed_physical["injection_end_angle"],
            health.fields["injection_end_angle_raw"] * 2 - 590,
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
