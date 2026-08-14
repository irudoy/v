from dataclasses import replace
import unittest

from patches import can_telemetry
from patches import can_telemetry_assembly
from patches import can_telemetry_compose
from patches import can_telemetry_layout
from patches import can_telemetry_profile
from patches import jk08a_runtime_reservations


class CanTelemetryContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = can_telemetry_profile.load_manifest()
        cls.layout = can_telemetry_layout.load_layout()
        cls.blobs = can_telemetry_assembly.load_payloads(cls.layout)

    def test_generated_profile_identity_and_complete_tables(self):
        self.assertEqual(
            tuple(
                (item.name, item.profile_id, item.page_count, item.crc16)
                for item in self.manifest.profiles
            ),
            (
                ("core32", 1, 5, 0x27FA),
                ("wide54", 2, 8, 0x238C),
            ),
        )
        self.assertEqual(len(self.manifest.fields), 32)
        self.assertEqual(len(self.manifest.page_sources), 49)
        self.assertEqual(len(self.manifest.contexts), 4)
        self.assertEqual(
            can_telemetry_profile.render_tables(self.manifest),
            can_telemetry_profile.DEFAULT_TABLES.read_text(encoding="utf-8"),
        )
        self.assertEqual(
            can_telemetry_profile.render_schema(self.manifest),
            can_telemetry_profile.DEFAULT_SCHEMA.read_text(encoding="utf-8"),
        )

    def test_configuration_round_trip_and_mailbox_encoding(self):
        cases = (
            can_telemetry.default_configuration(),
            can_telemetry.Configuration(True, 0x001, "core32", 255),
            can_telemetry.Configuration(True, 0x6EF, "wide54", 5),
            can_telemetry.Configuration(True, 0x7FF, "wide54", 1),
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
                if configuration.enabled:
                    self.assertEqual(record[:2], bytes((0x04, 0x08)))
                    self.assertEqual(
                        int.from_bytes(record[2:], "big"),
                        configuration.can_id << 5,
                    )
                else:
                    self.assertEqual(
                        record, can_telemetry.STOCK_MAILBOX_RECORD
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
            can_telemetry.Configuration(True, 0, "core32", 1),
            can_telemetry.Configuration(True, 0x800, "core32", 1),
            can_telemetry.Configuration(True, 0x6F0, "missing", 1),
            can_telemetry.Configuration(True, 0x6F0, "core32", 0),
            can_telemetry.Configuration(1, 0x6F0, "core32", 1),
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
        self.assertEqual(self.layout.reserved_rom.size, 0x11F0)
        self.assertEqual(self.layout.ram.active.size, 0x100)
        self.assertEqual(self.layout.ram.future.size, 0x100)
        self.assertEqual(self.layout.assembled_instruction_count, 470)
        self.assertEqual(self.layout.assembled_data_bytes, 442)

    def test_static_assembly_and_default_composition_are_locked(self):
        parsed = can_telemetry_assembly.validate_assembly_sources(
            self.layout
        )
        audit = can_telemetry_assembly.validate_instruction_semantics(
            self.layout, parsed, self.blobs
        )
        self.assertEqual(audit.instructions, 470)
        composition = can_telemetry_compose.compose(
            layout=self.layout, blobs=self.blobs
        )
        self.assertEqual(
            composition.sha256,
            self.layout.expected_composition_sha256,
        )
        self.assertEqual(composition.instruction_count, 470)
        self.assertEqual(composition.code_entry_count, 8)
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
            sum(item.span.size for item in ledger.future_rom), 8688
        )
        self.assertEqual(
            sum(item.span.size for item in ledger.future_ram), 768
        )


if __name__ == "__main__":
    unittest.main()
