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
from patches import can_telemetry_configurations
from patches import can_telemetry_layout
from patches import can_telemetry_profile
from patches import jk08a_runtime_reservations
from patches import map_switching_assembly
from tools.logs import can_telemetry_schema


# The profile CRC covers byte placement alone, so the profile ID is the only
# wire-level statement of which quantity each slot carries. One digest of the
# slot-to-field assignment is pinned per profile ID.
SLOT_ASSIGNMENT_SHA256 = {
    4: "3e03c72b5d80187d2335f3ea42996aab9b48c3e0e09c4fc11fe7a6b6405e11fd",
    5: "aee00366d786afd544790945cddd28ca26ddda9f092e60ab2a4221b628391681",
    6: "2110176f4c4c6be218b8e3356ba6f69185082a6e234a9699aa6297f2375d5f19",
    7: "99f46715917a3e0d3d8c4dd666b6fc5848764f36377fb5898161e181ffd43228",
    8: "7b2efd638d3fc25e8859d7b381e9d21f3608fb62aaae4c270fd2ea6b2eabd6e2",
    9: "af383f1b8d7bd30f207b2ef81cafd9884a18d60f4726a800121f2c05da0d4df4",
}


def _assignment_digest(assignment):
    return hashlib.sha256(
        json.dumps(assignment, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


def _generated_identity():
    """The integer symbols of the generated identity header, read as the
    source dialect reads them, and its configuration record."""
    header = can_telemetry_profile.DEFAULT_IDENTITY
    symbols = map_switching_assembly._header_symbols(header.name, header, 0)
    (record,) = (
        match["value"]
        for line in header.read_text(encoding="utf-8").splitlines()
        if (match := map_switching_assembly.DEFINE_RE.fullmatch(line))
        and match["name"] == "TELEMETRY_CONFIGURATION"
    )
    return symbols, bytes(
        int(value, 16) for value in record.strip("{ }").split(",")
    )


class CanTelemetryContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = can_telemetry_profile.load_manifest()
        cls.layout = can_telemetry_layout.load_layout()
        cls.blobs = can_telemetry_assembly.load_payloads(cls.layout)
        symbols, cls.configuration_record = _generated_identity()
        cls.profile_id = symbols["TELEMETRY_PROFILE_ID"]
        cls.page_count = symbols["TELEMETRY_PAGE_COUNT"]
        cls.crc16 = symbols["TELEMETRY_PROFILE_CRC"]

    def test_rom_configuration_guard_follows_the_manifest_identity(self):
        base = can_telemetry_assembly._manifest_identity
        drifts = (
            ("crc16", self.crc16 ^ 1),
            ("profile_id", self.profile_id + 1),
            ("page_count", self.page_count + 1),
            ("version", can_telemetry.CONFIG_VERSION + 1),
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
                "profile_id": self.profile_id,
                "page_count": self.page_count,
                "crc16": self.crc16,
            },
        )

    def test_rom_configuration_guard_takes_the_generated_identity(self):
        # A guard that spells a number of the identity instead of its symbol
        # fails, although the number equals the generated one.
        profile_id = f"0x{self.profile_id:X}"
        page_count = f"0x{self.page_count:X}"
        for unit_key, statement, spelled in (
            (
                "capture",
                "cmp/eq TELEMETRY_PROFILE_ID,r0",
                f"cmp/eq {profile_id},r0",
            ),
            ("capture", "mov #TELEMETRY_PAGE_COUNT,r6", f"mov #{page_count},r6"),
            (
                "control",
                "cmp/eq TELEMETRY_PAGE_COUNT,r0",
                f"cmp/eq {page_count},r0",
            ),
            (
                "control",
                ".word TELEMETRY_PROFILE_CRC",
                f".word 0x{self.crc16:04X}",
            ),
        ):
            with self.subTest(unit=unit_key, statement=statement):
                unit = self.layout.assembly_unit_by_key[unit_key]
                source = (
                    can_telemetry_layout.DEFAULT_MANIFEST.parent / unit.source
                ).read_text(encoding="utf-8")
                self.assertEqual(source.count(statement + "\n"), 1)
                drifted = replace(
                    self.layout,
                    source_texts=tuple(sorted({
                        **{
                            item.key: (
                                can_telemetry_layout.DEFAULT_MANIFEST.parent
                                / item.source
                            ).read_text(encoding="utf-8")
                            for item in self.layout.assembly_units
                        },
                        unit_key: source.replace(statement, spelled),
                    }.items())),
                )
                with self.assertRaisesRegex(ValueError, "generated"):
                    can_telemetry_assembly.validate_assembly_sources(drifted)

    def test_generated_profile_identity_and_complete_tables(self):
        self.assertEqual(
            tuple(
                (item.name, item.profile_id, item.page_count, item.crc16)
                for item in self.manifest.profiles
            ),
            (
                ("tuning", self.profile_id, self.page_count, self.crc16),
            ),
        )
        # The locked assembly of the generated table holds one long word per
        # fixed page byte and per context byte of the manifest.
        self.assertEqual(
            4 * (
                len(self.manifest.page_sources)
                + sum(
                    len(context.byte_sources)
                    for context in self.manifest.contexts
                )
            ),
            self.layout.assembly_unit_by_key["tables"].data_bytes,
        )
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
            can_telemetry_profile.render_schema(
                self.manifest, can_telemetry_configurations.load_catalog()
            ),
            can_telemetry_profile.DEFAULT_SCHEMA.read_text(encoding="utf-8"),
        )
        self.assertEqual(
            can_telemetry_profile.render_identity(self.manifest),
            can_telemetry_profile.DEFAULT_IDENTITY.read_text(encoding="utf-8"),
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

    def test_the_specification_slot_tables_follow_the_manifest(self):
        text = can_telemetry_profile.DEFAULT_SPECIFICATION.read_text(
            encoding="utf-8"
        )
        self.assertEqual(
            can_telemetry_profile.specification_text(self.manifest, text), text
        )
        rows = can_telemetry_profile.render_specification(
            self.manifest
        ).splitlines()
        fields = list(self.manifest.fields)
        for context in self.manifest.contexts:
            fields.extend(context.fields)
        for field in fields:
            with self.subTest(field=field.name):
                (row,) = [row for row in rows if f"| `{field.name}` |" in row]
                self.assertIn(f"`0x{field.source:08X}` |", row)

    def test_a_stale_slot_row_fails_the_specification_check(self):
        text = can_telemetry_profile.DEFAULT_SPECIFICATION.read_text(
            encoding="utf-8"
        )
        begin = f"<!-- {can_telemetry_profile.SPECIFICATION_SECTION}:begin -->"
        end = f"<!-- {can_telemetry_profile.SPECIFICATION_SECTION}:end -->"
        head, rest = text.split(begin)
        section, tail = rest.split(end)
        field = self.manifest.fields[1]
        source = f"`0x{field.source:08X}`"
        self.assertEqual(section.count(source), 1)
        removed = (
            "| 4 | 10 | `knock_margin_channels_4_to_6` | 2..3 | "
            "`removed_raw` | s16 | ECU RAM `0xFFFF1000` | raw count |\n"
        )
        drifts = {
            "edited source": section.replace(
                source, f"`0x{field.source + 2:08X}`"
            ),
            "removed field": section + removed,
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / can_telemetry_profile.DEFAULT_SPECIFICATION.name
            for name, drifted in drifts.items():
                with self.subTest(drift=name):
                    path.write_text(head + begin + drifted + end + tail,
                                    encoding="utf-8")
                    with self.assertRaisesRegex(
                        ValueError,
                        "regenerate them with "
                        + can_telemetry_profile.GENERATE_COMMAND,
                    ):
                        can_telemetry_profile.generate(
                            specification=path, check=True
                        )
                    can_telemetry_profile.generate(specification=path)
                    self.assertEqual(path.read_text(encoding="utf-8"), text)
            path.write_text(head + drifts["edited source"] + tail,
                            encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "no markers"):
                can_telemetry_profile.generate(specification=path, check=True)

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

    def test_the_generated_header_holds_the_default_configuration(self):
        # TELEMETRY_CONFIGURATION is the enabled record; the default disabled
        # configuration differs from it in enable byte 3 alone.
        record = bytearray(self.configuration_record)
        self.assertEqual(record[3], 1)
        record[3] = 0
        self.assertEqual(
            can_telemetry.default_configuration().to_bytes(self.manifest),
            bytes(record),
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
        self.assertEqual(self.layout.ram.active.size, 0x190)
        self.assertEqual(self.layout.ram.future.size, 0x70)
        self.assertEqual(self.layout.assembled_instruction_count, 1068)
        self.assertEqual(self.layout.assembled_data_bytes, 812)

    def test_static_assembly_and_default_composition_are_locked(self):
        parsed = can_telemetry_assembly.validate_assembly_sources(
            self.layout
        )
        audit = can_telemetry_assembly.validate_instruction_semantics(
            self.layout, parsed, self.blobs
        )
        self.assertEqual(audit.instructions, 1068)
        composition = can_telemetry_compose.compose(
            layout=self.layout, blobs=self.blobs
        )
        self.assertEqual(
            composition.sha256,
            self.layout.expected_composition_sha256,
        )
        self.assertEqual(composition.instruction_count, 1068)
        self.assertEqual(composition.code_entry_count, 13)
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
            sum(item.span.size for item in ledger.future_rom), 6160
        )
        self.assertEqual(
            sum(item.span.size for item in ledger.future_ram), 592
        )


class RuntimeStateSpanTest(unittest.TestCase):
    ROWS = (
        ("map_switching", 0xFFFF5D00, 0xFFFF5D3C),
        ("rolling_launch", 0xFFFF5D40, 0xFFFF5D6C),
        ("rolling_launch", 0xFFFF6100, 0xFFFF6120),
        ("can_telemetry", 0xFFFF5E00, 0xFFFF5F90),
    )

    @staticmethod
    def ledger(directory, rows):
        path = Path(directory) / "reservations.toml"
        path.write_text(
            "".join(
                f'[[active_ram]]\nowner = "{owner}"\n'
                f"start = 0x{start:08X}\nend = 0x{end:08X}\n\n"
                for owner, start, end in rows
            ),
            encoding="utf-8",
        )
        return path

    def test_a_runtime_may_own_several_state_spans(self):
        with tempfile.TemporaryDirectory() as directory:
            spans = can_telemetry_profile._runtime_state_spans(
                self.ledger(directory, self.ROWS)
            )
            self.assertEqual(spans, tuple(
                (start, end) for owner, start, end in self.ROWS
                if owner in can_telemetry_profile.RUNTIME_STATE_OWNERS
            ))
            for owner in can_telemetry_profile.RUNTIME_STATE_OWNERS:
                with self.subTest(missing=owner):
                    path = self.ledger(
                        directory, [row for row in self.ROWS if row[0] != owner]
                    )
                    with self.assertRaisesRegex(
                        ValueError, f"no active runtime state span of {owner}"
                    ):
                        can_telemetry_profile._runtime_state_spans(path)

    def test_a_state_field_reads_the_rolling_launch_extension(self):
        spans = can_telemetry_profile._runtime_state_spans()
        self.assertIn((0xFFFF6100, 0xFFFF6120), spans)
        raw = {
            "name": "extension_probe", "width": 2, "source": 0xFFFF6116,
            "kind": "runtime_state", "signed": False, "scale": "raw count",
        }
        field = can_telemetry_profile._parse_field(
            raw, context="probe", page_field=False, runtime_spans=spans
        )
        self.assertEqual(field.source, 0xFFFF6116)
        with self.assertRaisesRegex(ValueError, "outside the active runtime RAM"):
            can_telemetry_profile._parse_field(
                {**raw, "source": 0xFFFF611F}, context="probe",
                page_field=False, runtime_spans=spans,
            )


if __name__ == "__main__":
    unittest.main()
