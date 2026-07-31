from dataclasses import replace
from pathlib import Path
import unittest

from patches import map_switching_layout as layout_model
from patches import map_switching_assembly


ROOT = Path(__file__).resolve().parents[2]


class MapSwitchingLayoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layout = layout_model.load_layout()
        cls.image = layout_model.validate_image(cls.layout)

    def test_manifest_targets_exact_jk08a_and_complete_pilot(self):
        self.assertEqual(self.layout.rom, "JK08A")
        self.assertEqual(self.layout.slot_count, 5)
        self.assertEqual(len(self.layout.families), 8)
        self.assertEqual(
            self.layout.source_sha256,
            "ab60f18793fb121e4f55f626246117a6c"
            "69d9a900c0307ab1f4fc5f6ac718b23",
        )

    def test_claimed_rom_is_inside_the_audited_erased_region(self):
        self.assertTrue(
            self.layout.free_rom.contains(self.layout.claimed_rom)
        )
        claimed = self.image.data[
            self.layout.claimed_rom.start : self.layout.claimed_rom.end
        ]
        self.assertEqual(claimed, bytes([0xFF]) * len(claimed))

    def test_reserved_rom_ranges_are_non_overlapping(self):
        ranges = sorted(
            self.layout.reserved_rom_ranges(),
            key=lambda item: (item.start, item.end),
        )
        for left, right in zip(ranges, ranges[1:]):
            with self.subTest(left=left.key, right=right.key):
                self.assertLessEqual(left.end, right.start)

    def test_every_hook_literal_matches_the_exact_stock_rom(self):
        for hook in self.layout.hooks:
            with self.subTest(hook=hook.key):
                actual = int.from_bytes(
                    self.image.data[
                        hook.address : hook.address + hook.width
                    ],
                    self.layout.byte_order,
                )
                self.assertEqual(actual, hook.stock)

    def test_feedback_contract_matches_exact_can_551_serializer(self):
        feedback = self.layout.feedback
        self.assertEqual(feedback.can_channel, 1)
        self.assertEqual(feedback.mailbox_index, 3)
        self.assertEqual(feedback.frame_id, 0x551)
        self.assertEqual(feedback.dlc, 8)
        self.assertEqual(
            self.image.data[
                feedback.config_record_address :
                feedback.config_record_address + 4
            ],
            bytes.fromhex("03 08 aa 20"),
        )
        self.assertEqual(feedback.serializer, 0x000C5372)
        self.assertEqual(feedback.dispatch_literal, 0x000C3FA4)
        self.assertEqual(feedback.payload_start, 0xFFFF3AD5)
        self.assertEqual(feedback.status_byte_index, 5)
        self.assertEqual(feedback.status_byte_address, 0xFFFF3ADA)
        self.assertEqual(feedback.status_mask, 0x03)
        self.assertEqual(feedback.lamp_on_value, 0x02)
        self.assertEqual(feedback.phase_counts_address, 0x000D3848)
        self.assertEqual(feedback.default_on_frames, 10)
        self.assertEqual(feedback.default_off_frames, 10)

    def test_all_slot_copies_and_pointer_tables_share_one_manifest(self):
        materialized = layout_model.materialize_calibration_copies(
            self.layout, self.image
        )
        for family in self.layout.families:
            source = materialized[
                family.canonical_address :
                family.canonical_address + family.byte_length
            ]
            with self.subTest(family=family.key):
                self.assertEqual(len(family.all_slot_addresses), 5)
                for address in family.all_slot_addresses:
                    self.assertEqual(
                        materialized[address : address + family.byte_length],
                        source,
                    )
                pointers = tuple(
                    int.from_bytes(
                        materialized[address : address + 4],
                        self.layout.byte_order,
                    )
                    for address in range(
                        family.pointer_table,
                        family.pointer_table
                        + self.layout.pointer_table_size,
                        4,
                    )
                )
                self.assertEqual(pointers, family.all_slot_addresses)

    def test_implemented_assembly_sources_match_layout_and_adapter_abi(self):
        parsed = map_switching_assembly.validate_assembly_sources(
            self.layout
        )
        self.assertEqual(
            set(parsed),
            {
                "selector_host",
                "adapter_select_helper",
                "lookup_adapters",
                "startup_wrapper",
                "limiter_commit",
                "cruise_feedback_wrapper",
                "cruise_feedback_engine",
            },
        )
        self.assertEqual(
            self.layout.assembled_region_keys,
            {
                "selector_host",
                "adapter_select_helper",
                "overrun_adapter",
                "ignition_adapter",
                "fuel_compensation_adapter",
                "fuel_targets_adapter",
                "startup_wrapper",
                "limiter_commit",
                "cruise_feedback_wrapper",
                "cruise_feedback_engine",
            },
        )
        self.assertEqual(
            sum(
                unit.instruction_count
                for unit in self.layout.assembly_units
            ),
            386,
        )
        self.assertEqual(
            self.layout.unassembled_region_keys,
            set(),
        )

    def test_assembly_blob_lock_rejects_wrong_length_and_hash(self):
        unit = self.layout.assembly_unit_by_key[
            "adapter_select_helper"
        ]
        with self.assertRaisesRegex(ValueError, "blob has"):
            layout_model.validate_assembled_blob(unit, b"")
        with self.assertRaisesRegex(ValueError, "blob SHA-256"):
            layout_model.validate_assembled_blob(
                unit, bytes([unit.fill]) * unit.span.size
            )

    def test_materialization_changes_only_copy_and_pointer_storage(self):
        materialized = layout_model.materialize_calibration_copies(
            self.layout, self.image
        )
        permitted = set()
        for family in self.layout.families:
            for address in family.copies:
                permitted.update(
                    range(address, address + family.byte_length)
                )
            permitted.update(
                range(
                    family.pointer_table,
                    family.pointer_table + self.layout.pointer_table_size,
                )
            )
        changed = {
            index
            for index, (stock, projected) in enumerate(
                zip(self.image.data, materialized)
            )
            if stock != projected
        }
        self.assertTrue(changed)
        self.assertLessEqual(changed, permitted)

    def test_direct_limiters_preserve_complete_stock_containers(self):
        fuel_cut = self.layout.family_by_key["rev_limit_fuel_cut"]
        throttle = self.layout.family_by_key["rev_limit_throttle_cut"]
        self.assertEqual(
            self.image.data[
                fuel_cut.stock_container_start :
                fuel_cut.stock_container_start + fuel_cut.stock_container_size
            ],
            bytes.fromhex("02 64 02 54 02 54 01 70 00 00 00 00"),
        )
        self.assertEqual(
            self.image.data[
                throttle.stock_container_start :
                throttle.stock_container_start
                + throttle.stock_container_size
            ],
            bytes.fromhex(
                "00 4c 00 c8 05 dc 07 d0 25 80 ff ff 00 00 00 10 "
                "ff ff 00 00 00 05 00 1e 00 32 00 b6"
            ),
        )

    def test_structural_validator_rejects_an_overlapping_copy(self):
        family = self.layout.families[1]
        corrupted = replace(
            family,
            copies=(
                self.layout.families[0].copies[0],
                *family.copies[1:],
            ),
        )
        layout = replace(
            self.layout,
            families=(self.layout.families[0], corrupted)
            + self.layout.families[2:],
        )
        with self.assertRaisesRegex(ValueError, "ROM allocations overlap"):
            layout_model.validate_structure(layout)

    def test_structural_validator_rejects_an_undeclared_hook_target(self):
        corrupted = replace(
            self.layout.hooks[0], replacement=0x00123456
        )
        layout = replace(
            self.layout,
            hooks=(corrupted,) + self.layout.hooks[1:],
        )
        with self.assertRaisesRegex(
            ValueError, "neither a code entry nor reserved RAM"
        ):
            layout_model.validate_structure(layout)

    def test_structural_validator_rejects_misaligned_feedback_status(self):
        layout = replace(
            self.layout,
            feedback=replace(
                self.layout.feedback,
                status_byte_address=0xFFFF3ADB,
            ),
        )
        with self.assertRaisesRegex(
            ValueError, "differs from its payload byte index"
        ):
            layout_model.validate_structure(layout)


if __name__ == "__main__":
    unittest.main()
