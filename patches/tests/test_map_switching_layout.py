from dataclasses import replace
from pathlib import Path
import unittest

from patches import apply_map_switching
from patches import map_switching_layout as layout_model
from patches import map_switching_assembly


ROOT = Path(__file__).resolve().parents[2]


class MapSwitchingLayoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layout = layout_model.load_layout()
        cls.image = layout_model.validate_image(cls.layout)

    def test_manifest_targets_exact_jk08a_and_complete_runtime(self):
        self.assertEqual(self.layout.schema_version, 2)
        self.assertEqual(self.layout.rom, "JK08A")
        self.assertEqual(self.layout.slot_count, 5)
        self.assertEqual(len(self.layout.families), 12)
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

    def test_fallback_zero_fill_literal_is_a_read_only_stock_anchor(self):
        anchor = next(
            item
            for item in self.layout.anchors
            if item.key == "startup_clear_start_stock"
        )
        self.assertEqual(anchor.address, 0x000029CC)
        self.assertEqual(anchor.width, 4)
        self.assertEqual(anchor.value, 0xFFFF7000)
        self.assertNotIn(
            anchor.address,
            {hook.address for hook in self.layout.hooks},
        )
        actual = int.from_bytes(
            self.image.data[
                anchor.address : anchor.address + anchor.width
            ],
            self.layout.byte_order,
        )
        self.assertEqual(actual, anchor.value)

    def test_read_only_anchor_rejects_partial_hook_overlap(self):
        anchor = self.layout.anchor_by_key["startup_clear_start_stock"]
        overlapping = replace(
            self.layout.hooks[0],
            address=anchor.address + 2,
        )
        layout = replace(
            self.layout,
            hooks=(overlapping,) + self.layout.hooks[1:],
        )
        with self.assertRaisesRegex(
            ValueError, "read-only anchor overlaps writable range"
        ):
            layout_model.validate_structure(layout)

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
        self.assertEqual(feedback.status_mask, 0x70)
        self.assertEqual(feedback.lamp_on_value, 0x60)
        self.assertEqual(feedback.phase_counts_address, 0x000D3848)
        self.assertEqual(feedback.payload_on_frames, 10)
        self.assertEqual(feedback.payload_off_frames, 10)
        self.assertEqual(feedback.default_on_frames, 30)
        self.assertEqual(feedback.default_off_frames, 30)

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
                "full_dfco_adapter",
                "startup_wrapper",
                "limiter_commit",
                "cruise_feedback_wrapper",
                "cruise_feedback_engine",
                "idle_ignition_adapter",
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
                "full_dfco_adapter",
                "startup_wrapper",
                "limiter_commit",
                "cruise_feedback_wrapper",
                "cruise_feedback_engine",
                "idle_ignition_adapter",
            },
        )
        self.assertEqual(
            sum(
                unit.instruction_count
                for unit in self.layout.assembly_units
            ),
            435,
        )
        self.assertEqual(
            self.layout.unassembled_region_keys,
            set(),
        )

    def test_assembly_rejects_instruction_outside_sh7058s_sh2e(self):
        parsed = map_switching_assembly.ParsedSource(
            Path("synthetic-sh2a-only.s"),
            {},
            (
                map_switching_assembly.SourceStatement(
                    1, 0xD2108, "instruction", "movli.l @r0,r1", 2
                ),
            ),
        )
        with self.assertRaisesRegex(
            ValueError, "outside the audited SH7058S SH-2E subset"
        ):
            map_switching_assembly._validate_sh7058s_instruction_subset(
                parsed
            )

    def test_adapter_rejects_pc_relative_load_in_bra_delay_slot(self):
        parsed = map_switching_assembly.ParsedSource(
            Path("synthetic-delay-slot.s"),
            {},
            (
                map_switching_assembly.SourceStatement(
                    1, 0xD2300, "instruction", "bra 0xD2270", 2
                ),
                map_switching_assembly.SourceStatement(
                    2,
                    0xD2302,
                    "instruction",
                    "mov.l @(stock_wrapper,pc),r3",
                    2,
                ),
            ),
        )
        with self.assertRaisesRegex(ValueError, "BRA delay slot is not NOP"):
            map_switching_assembly._validate_registers_and_control_flow(
                parsed, 0xD2270
            )

    def test_all_machine_control_flow_and_pc_relative_literals_are_audited(self):
        parsed = map_switching_assembly.validate_assembly_sources(
            self.layout
        )
        audit = map_switching_assembly.validate_instruction_semantics(
            self.layout,
            parsed,
            apply_map_switching.load_payloads(self.layout),
        )
        self.assertEqual(audit.instructions, 435)
        self.assertEqual(audit.delayed_transfers, 43)
        self.assertEqual(audit.pc_relative_references, 59)
        self.assertEqual(audit.direct_branches, 81)
        self.assertEqual(audit.indirect_transfers, 24)

    def test_global_delay_slot_gate_rejects_pc_relative_load_after_jsr(self):
        parsed = map_switching_assembly.ParsedSource(
            Path("synthetic-jsr-delay-slot.s"),
            {"literal": 0x1008},
            (
                map_switching_assembly.SourceStatement(
                    1, 0x1000, "instruction", "jsr @r0", 2
                ),
                map_switching_assembly.SourceStatement(
                    2,
                    0x1002,
                    "instruction",
                    "mov.l @(literal,pc),r1",
                    2,
                ),
                map_switching_assembly.SourceStatement(
                    3, 0x1008, "long", "0x12345678", 4
                ),
            ),
        )
        with self.assertRaisesRegex(ValueError, "JSR delay slot is not NOP"):
            map_switching_assembly.validate_source_blob(
                parsed, bytes(12), 0x1000
            )

    def test_binary_delay_slot_gate_rejects_non_nop_word(self):
        parsed = map_switching_assembly.ParsedSource(
            Path("synthetic-binary-delay-slot.s"),
            {},
            (
                map_switching_assembly.SourceStatement(
                    1, 0x1000, "instruction", "jsr @r0", 2
                ),
                map_switching_assembly.SourceStatement(
                    2, 0x1002, "instruction", "nop", 2
                ),
            ),
        )
        with self.assertRaisesRegex(
            ValueError, "binary JSR delay slot is not NOP"
        ):
            map_switching_assembly.validate_source_blob(
                parsed, bytes.fromhex("400b0008"), 0x1000
            )

    def test_pc_relative_gate_rejects_wrong_encoded_literal_target(self):
        parsed = map_switching_assembly.ParsedSource(
            Path("synthetic-pc-relative.s"),
            {"literal": 0x1008},
            (
                map_switching_assembly.SourceStatement(
                    1,
                    0x1000,
                    "instruction",
                    "mov.l @(literal,pc),r0",
                    2,
                ),
                map_switching_assembly.SourceStatement(
                    2, 0x1008, "long", "0x12345678", 4
                ),
            ),
        )
        with self.assertRaisesRegex(
            ValueError, "resolves to 0x1004, expected 0x1008"
        ):
            map_switching_assembly.validate_source_blob(
                parsed,
                bytes.fromhex("d000ffffffffffff12345678"),
                0x1000,
            )

    def test_startup_wrapper_forces_map_1_on_both_sides_of_initializer(self):
        parsed = map_switching_assembly.validate_assembly_sources(
            self.layout
        )["startup_wrapper"]
        texts = [
            statement.text.lower()
            for statement in parsed.statements
            if statement.kind == "instruction"
        ]
        jsr_indexes = [
            index for index, text in enumerate(texts) if text == "jsr @r0"
        ]
        preinitializer_zero = texts.index("mov #0x0,r0")
        commit_zero = texts.index("mov #0x0,r4")
        store_index = texts.index("mov.b r0,@r1")
        self.assertEqual(len(jsr_indexes), 2)
        self.assertLess(preinitializer_zero, store_index)
        self.assertLess(store_index, jsr_indexes[0])
        self.assertLess(jsr_indexes[0], commit_zero)
        self.assertLess(commit_zero, jsr_indexes[1])

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
