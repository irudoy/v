from dataclasses import replace
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from patches import can_telemetry
from patches import can_telemetry_assembly
from patches import can_telemetry_compose
from patches import can_telemetry_layout
from patches import can_telemetry_profile
from patches import jk08a_runtime_reservations
from tools.logs import can_telemetry_schema


# The profile CRC covers byte placement alone, so the profile ID is the only
# wire-level statement of which quantity each slot carries. One digest of the
# slot-to-field assignment is pinned per profile ID.
SLOT_ASSIGNMENT_SHA256 = {
    4: "3e03c72b5d80187d2335f3ea42996aab9b48c3e0e09c4fc11fe7a6b6405e11fd",
    5: "aee00366d786afd544790945cddd28ca26ddda9f092e60ab2a4221b628391681",
    6: "2110176f4c4c6be218b8e3356ba6f69185082a6e234a9699aa6297f2375d5f19",
    7: "99f46715917a3e0d3d8c4dd666b6fc5848764f36377fb5898161e181ffd43228",
}


def _assignment_digest(assignment):
    return hashlib.sha256(
        json.dumps(assignment, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


class CanTelemetryContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = can_telemetry_profile.load_manifest()
        cls.layout = can_telemetry_layout.load_layout()
        cls.blobs = can_telemetry_assembly.load_payloads(cls.layout)

    def test_rom_configuration_guard_follows_the_manifest_identity(self):
        base = can_telemetry_assembly._manifest_identity
        drifts = (
            ("crc16", 0x6475),
            ("profile_id", 6),
            ("page_count", 12),
            ("version", 3),
        )
        for field, value in drifts:
            with self.subTest(field=field):
                def drifted(manifest, _field=field, _value=value):
                    identity = base(manifest)
                    identity[_field] = _value
                    return identity

                can_telemetry_assembly._manifest_identity = drifted
                try:
                    with self.assertRaises(ValueError):
                        can_telemetry_assembly.validate_assembly_sources(
                            self.layout
                        )
                finally:
                    can_telemetry_assembly._manifest_identity = base
        self.assertEqual(
            base(self.manifest),
            {
                "magic": can_telemetry.CONFIG_MAGIC,
                "version": can_telemetry.CONFIG_VERSION,
                "can_id_max": can_telemetry.MAX_DATA_CAN_ID,
                "profile_id": 7,
                "page_count": 11,
                "crc16": 0x6474,
            },
        )

    def test_generated_profile_identity_and_complete_tables(self):
        self.assertEqual(
            tuple(
                (item.name, item.profile_id, item.page_count, item.crc16)
                for item in self.manifest.profiles
            ),
            (
                ("tuning", 7, 11, 0x6474),
            ),
        )
        self.assertEqual(len(self.manifest.fields), 40)
        self.assertEqual(len(self.manifest.page_sources), 63)
        self.assertEqual(len(self.manifest.contexts), 10)
        names = {item.name for item in self.manifest.fields}
        context_names = {
            field.name
            for context in self.manifest.contexts
            for field in context.fields
        }
        self.assertTrue({
            "normalized_load_raw",
            "rolling_launch_phase",
            "intake_cvtc_target_raw",
            "exhaust_cvtc_target_raw",
            "throttle_request_bounded_raw",
            "engine_torque_state_raw",
        } <= names)
        self.assertTrue({
            "active_map_index",
            "rolling_launch_abort_reason",
            "battery_voltage_raw",
            "front_af_sensor_b1_word_raw",
            "secondary_tps_b2_raw",
        } <= context_names)
        self.assertFalse({
            "front_oxygen_sensor_b1_raw",
            "front_oxygen_sensor_b2_raw",
            "timing_state_2023_raw",
            "atmospheric_pressure_raw",
        } & (names | context_names))
        self.assertEqual(
            can_telemetry_profile.render_tables(self.manifest),
            can_telemetry_profile.DEFAULT_TABLES.read_text(encoding="utf-8"),
        )
        self.assertEqual(
            can_telemetry_profile.render_schema(self.manifest),
            can_telemetry_profile.DEFAULT_SCHEMA.read_text(encoding="utf-8"),
        )
        host_schema = json.loads(
            can_telemetry_profile.DEFAULT_SCHEMA.read_text(encoding="utf-8")
        )
        self.assertNotIn("rom", host_schema)
        self.assertNotIn("mailbox", host_schema["frame"])
        self.assertEqual(host_schema["frame"]["default_can_id"], "0x6F0")
        self.assertEqual(
            host_schema["control"],
            {
                "can_id": "data_can_id + 1",
                "commands": {
                    "start": "54454C320201B632",
                    "stop": "54454C320200A613",
                },
                "dlc": 8,
                "format": "standard_11_bit_classical_can",
                "maximum_data_can_id": "0x7FE",
            },
        )
        host_fields = list(host_schema["profiles"][0]["fields"])
        for context in host_schema["profiles"][0]["contexts"]:
            host_fields.extend(context["fields"])
        self.assertTrue(host_fields)
        self.assertTrue(all("source" not in field for field in host_fields))

    def test_profile_crc_covers_the_wire_layout_alone(self):
        document = json.loads(
            can_telemetry_profile.DEFAULT_SCHEMA.read_text(encoding="utf-8")
        )
        version = document["protocol_version"]
        profile = document["profiles"][0]
        expected = self.manifest.profiles[0].crc16
        self.assertEqual(
            can_telemetry_schema.profile_crc16(profile, version), expected
        )

        relabelled = copy.deepcopy(profile)
        relabelled["name"] = "relabelled"
        for field in relabelled["fields"]:
            field["name"] += "_renamed"
            field["scale"] = "restated"
        for context in relabelled["contexts"]:
            context["name"] += "_renamed"
            for field in context["fields"]:
                field["name"] += "_renamed"
                field["scale"] = "restated"
        relabelled["fields"].reverse()
        self.assertEqual(
            can_telemetry_schema.profile_crc16(relabelled, version), expected
        )

        def mutated(change):
            candidate = copy.deepcopy(profile)
            change(candidate)
            return can_telemetry_schema.profile_crc16(candidate, version)

        wide = next(
            index for index, field in enumerate(profile["fields"])
            if field["width"] == 2
        )
        mutations = {
            "id": lambda item: item.update(id=item["id"] + 1),
            "page_count": lambda item: item.update(
                page_count=item["page_count"] - 1
            ),
            "width": lambda item: item["fields"][wide].update(width=1),
            "offset": lambda item: item["fields"][wide].update(
                offset=item["fields"][wide]["offset"] + 1
            ),
            "signed": lambda item: item["fields"][wide].update(
                signed=not item["fields"][wide]["signed"]
            ),
            "context_width": lambda item: item["contexts"][0]["fields"][
                0
            ].update(width=item["contexts"][0]["fields"][0]["width"] + 1),
            "context_order": lambda item: item["contexts"].reverse(),
        }
        for name, change in mutations.items():
            with self.subTest(mutation=name):
                self.assertNotEqual(mutated(change), expected)
        self.assertNotEqual(
            can_telemetry_schema.profile_crc16(profile, version + 1), expected
        )

    def test_slot_assignment_is_pinned_to_the_profile_id(self):
        for profile in self.manifest.profiles:
            assignment = {
                "fields": sorted(
                    [field.page, field.offset, field.name]
                    for field in self.manifest.fields
                    if profile.name in field.profiles
                ),
                "contexts": [
                    [
                        context.page,
                        context.tag,
                        [field.name for field in context.fields],
                    ]
                    for context in self.manifest.contexts
                ],
            }
            self.assertEqual(
                _assignment_digest(assignment),
                SLOT_ASSIGNMENT_SHA256.get(profile.profile_id),
                f"the slot assignment of profile ID {profile.profile_id} "
                "differs from the pinned one. The profile CRC covers byte "
                "placement alone, so a slot that carries a different "
                "quantity requires a new profile ID with its own digest; "
                "only a rename of the same quantity replaces the digest "
                "under the same ID.",
            )

    def test_retired_profiles_keep_their_pinned_slot_assignment(self):
        retired = self.manifest.retired_profiles
        self.assertEqual([item["id"] for item in retired], [5, 6])
        for item in retired:
            with self.subTest(profile_id=item["id"]):
                assignment = {
                    "fields": sorted(
                        [field["page"], field["offset"], field["name"]]
                        for field in item["fields"]
                    ),
                    "contexts": [
                        [
                            context["page"],
                            context["tag"],
                            [field["name"] for field in context["fields"]],
                        ]
                        for context in item["contexts"]
                    ],
                }
                self.assertEqual(
                    _assignment_digest(assignment),
                    SLOT_ASSIGNMENT_SHA256[item["id"]],
                )
        schema = json.loads(
            can_telemetry_profile.DEFAULT_SCHEMA.read_text(encoding="utf-8")
        )
        self.assertEqual(schema["retired_profiles"], list(retired))

    def test_retired_profiles_reject_reused_ids_and_foreign_framing(self):
        source = json.loads(
            can_telemetry_profile.DEFAULT_RETIRED.read_text(encoding="utf-8")
        )
        tracked = source["retired_profiles"]
        retired = {row["id"]: row for row in tracked}[6]

        def load(rows):
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "retired.json"
                path.write_text(
                    json.dumps({"retired_profiles": rows}), encoding="utf-8"
                )
                manifest = can_telemetry_profile.load_manifest(retired=path)
                return can_telemetry_profile.render_schema(manifest)

        self.assertIn('"retired_profiles"', load(tracked))
        reused = (
            [dict(retired, id=7)],
            [dict(retired, id=8)],
            [retired, retired],
            [dict(retired, name="missing")],
        )
        for rows in reused:
            with self.subTest(ids=[row["id"] for row in rows]):
                with self.assertRaises(ValueError):
                    load(rows)
        foreign = {
            "page_count": dict(retired, page_count=12),
            "crc16": dict(retired, crc16_ccitt_false="0xF14F"),
            "contexts": dict(retired, contexts=retired["contexts"][:-1]),
        }
        for change, row in foreign.items():
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    load([row])

    def test_configuration_round_trip_and_mailbox_encoding(self):
        cases = (
            can_telemetry.default_configuration(),
            can_telemetry.Configuration(True, 0x001, "tuning", 255),
            can_telemetry.Configuration(True, 0x6EF, "tuning", 5),
            can_telemetry.Configuration(True, 0x7FE, "tuning", 1),
        )
        for configuration in cases:
            with self.subTest(configuration=configuration):
                encoded = configuration.to_bytes(self.manifest)
                self.assertEqual(len(encoded), can_telemetry.CONFIG_SIZE)
                self.assertEqual(
                    can_telemetry.Configuration.from_bytes(
                        encoded, self.manifest
                    ),
                    configuration,
                )
                record = configuration.mailbox_record()
                self.assertEqual(len(record), 4)
                self.assertEqual(record[:2], bytes((0x04, 0x08)))
                self.assertEqual(
                    int.from_bytes(record[2:], "big"),
                    configuration.can_id << 5,
                )
                self.assertEqual(
                    configuration.control_can_id,
                    configuration.can_id + 1,
                )

    def test_the_specification_publishes_the_default_configuration(self):
        published = " ".join(
            (Path(__file__).resolve().parents[1] / "can-telemetry.md")
            .read_text(encoding="utf-8")
            .split()
        )
        encoded = can_telemetry.default_configuration().to_bytes(self.manifest)
        self.assertIn(
            "The default disabled bytes are `"
            + " ".join(f"{byte:02X}" for byte in encoded)
            + "`.",
            published,
        )

    def test_configuration_rejects_corruption_and_invalid_ranges(self):
        encoded = bytearray(can_telemetry.default_configuration().to_bytes())
        for index in (0, 2, 4, 5, 6, 7, 10, 12, 15):
            with self.subTest(index=index):
                damaged = bytearray(encoded)
                damaged[index] ^= 1
                with self.assertRaises(ValueError):
                    can_telemetry.Configuration.from_bytes(damaged)
        invalid = (
            can_telemetry.Configuration(True, 0, "tuning", 1),
            can_telemetry.Configuration(True, 0x7FF, "tuning", 1),
            can_telemetry.Configuration(True, 0x800, "tuning", 1),
            can_telemetry.Configuration(True, 0x6F0, "missing", 1),
            can_telemetry.Configuration(True, 0x6F0, "tuning", 0),
            can_telemetry.Configuration(1, 0x6F0, "tuning", 1),
        )
        for configuration in invalid:
            with self.subTest(configuration=configuration):
                self.assertFalse(configuration.is_valid())
                with self.assertRaises(ValueError):
                    configuration.to_bytes()

    def test_layout_has_active_and_future_budgets(self):
        self.assertEqual(
            (self.layout.owned_rom.start, self.layout.owned_rom.end),
            (0xD4280, 0xD6000),
        )
        self.assertEqual(self.layout.reserved_rom.size, 0x1000)
        self.assertEqual(self.layout.ram.active.size, 0x100)
        self.assertEqual(self.layout.ram.future.size, 0x100)
        self.assertEqual(self.layout.assembled_instruction_count, 720)
        self.assertEqual(self.layout.assembled_data_bytes, 770)

    def test_static_assembly_and_default_composition_are_locked(self):
        parsed = can_telemetry_assembly.validate_assembly_sources(
            self.layout
        )
        audit = can_telemetry_assembly.validate_instruction_semantics(
            self.layout, parsed, self.blobs
        )
        self.assertEqual(audit.instructions, 720)
        composition = can_telemetry_compose.compose(
            layout=self.layout, blobs=self.blobs
        )
        self.assertEqual(
            composition.sha256,
            self.layout.expected_composition_sha256,
        )
        self.assertEqual(composition.instruction_count, 720)
        self.assertEqual(composition.code_entry_count, 11)
        self.assertEqual(
            composition.data[
                self.layout.reserved_rom.start : self.layout.reserved_rom.end
            ],
            bytes([0xFF]) * self.layout.reserved_rom.size,
        )

    def test_layout_mutations_fail_closed(self):
        cases = (
            replace(
                self.layout,
                reserved_rom=replace(
                    self.layout.reserved_rom,
                    start=self.layout.reserved_rom.start + 1,
                ),
            ),
            replace(
                self.layout,
                mailbox_record_address=(
                    self.layout.mailbox_record_address + 4
                ),
            ),
            replace(
                self.layout,
                ram=replace(
                    self.layout.ram,
                    future=replace(
                        self.layout.ram.future,
                        end=self.layout.ram.future.end - 1,
                    ),
                ),
            ),
        )
        for item in cases:
            with self.subTest(item=item):
                with self.assertRaises(ValueError):
                    can_telemetry_layout.validate_structure(item)

    def test_shared_reservation_ledger_is_disjoint_and_erased(self):
        ledger = jk08a_runtime_reservations.load_ledger()
        self.assertEqual(
            {item.owner for item in ledger.future_rom},
            jk08a_runtime_reservations.OWNERS,
        )
        self.assertEqual(
            sum(item.span.size for item in ledger.future_rom), 8192
        )
        self.assertEqual(
            sum(item.span.size for item in ledger.future_ram), 768
        )


if __name__ == "__main__":
    unittest.main()
