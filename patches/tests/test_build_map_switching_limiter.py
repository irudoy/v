from itertools import chain
from pathlib import Path
import unittest

from patches import build_map_switching_limiter as limiter_gate
from patches import build_map_switching_selector_init as selector_init
from patches import build_map_switching_trampoline as trampoline
from patches import jk08a_checksums as checksums
from patches import map_switching_assembly as assembly
from patches import map_switching_layout as layout_model


ROOT = Path(__file__).resolve().parents[2]
STOCK = (
    ROOT
    / "rom-images"
    / "23710-JK08A"
    / "1JK08A-20260726-stock.bin"
)


class BuildMapSwitchingLimiterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layout = layout_model.load_layout()
        marker_source = bytearray(STOCK.read_bytes())
        marker_source[
            limiter_gate.RESET_SELECTOR_LINE_START :
            limiter_gate.RESET_SELECTOR_LINE_END
        ] = bytes(128)
        marker_source[
            limiter_gate.MARKER_LINE_START :
            limiter_gate.MARKER_LINE_END
        ] = bytes(128)
        marker_source = checksums.recalculate(marker_source)
        trampoline_result = trampoline.build_image(
            marker_source,
            layout=cls.layout,
            source_name="synthetic marker readback",
            expected_source_sha256=trampoline.sha256(marker_source),
        )
        selector_result = selector_init.build_image(
            trampoline_result.data,
            layout=cls.layout,
            source_name="synthetic trampoline readback",
            expected_source_sha256=selector_init.sha256(
                trampoline_result.data
            ),
        )
        cls.source = selector_result.data
        cls.source_sha256 = limiter_gate.sha256(cls.source)
        cls.payloads = limiter_gate.load_gate_payloads(cls.layout)
        cls.result = limiter_gate.build_image(
            cls.source,
            layout=cls.layout,
            payloads=cls.payloads,
            source_name="synthetic selector-init readback",
            expected_source_sha256=cls.source_sha256,
        )

    def test_payload_contract_is_exact(self):
        startup = self.payloads["startup_wrapper"]
        limiter = self.payloads["limiter_commit"]
        self.assertEqual(len(startup), 0x60)
        self.assertEqual(len(limiter), 0x100)
        self.assertEqual(
            limiter_gate.sha256(startup),
            limiter_gate.STARTUP_WRAPPER_SHA256,
        )
        self.assertEqual(
            limiter_gate.sha256(limiter),
            limiter_gate.LIMITER_COMMIT_SHA256,
        )
        parsed = assembly.validate_assembly_sources(self.layout)
        self.assertEqual(parsed["startup_wrapper"].instruction_count, 14)
        self.assertEqual(parsed["startup_wrapper"].data_bytes, 12)
        self.assertEqual(parsed["limiter_commit"].instruction_count, 56)
        self.assertEqual(parsed["limiter_commit"].data_bytes, 36)

    def test_source_is_exact_selector_init_stage(self):
        self.assertEqual(
            self.source[
                limiter_gate.STARTUP_WRAPPER_START :
                selector_init.SELECTOR_INIT_END
            ],
            selector_init.SELECTOR_INIT_BLOB,
        )
        self.assertEqual(
            self.source[
                selector_init.SELECTOR_INIT_END :
                limiter_gate.MARKER_LINE_END
            ],
            bytes(
                limiter_gate.MARKER_LINE_END
                - selector_init.SELECTOR_INIT_END
            ),
        )

    def test_only_declared_gate_and_checksum_bytes_change(self):
        permitted = set(
            range(
                limiter_gate.STARTUP_WRAPPER_START,
                limiter_gate.STARTUP_WRAPPER_END,
            )
        )
        permitted.update(
            range(
                limiter_gate.LIMITER_COMMIT_START,
                limiter_gate.LIMITER_COMMIT_END,
            )
        )
        for family in limiter_gate._limiter_families(self.layout):
            permitted.update(
                chain.from_iterable(
                    range(address, address + family.byte_length)
                    for address in family.copies
                )
            )
            permitted.update(
                range(
                    family.pointer_table,
                    family.pointer_table + self.layout.pointer_table_size,
                )
            )
        for hook in self.layout.hooks:
            if hook.key in limiter_gate.LIMITER_HOOK_KEYS:
                permitted.update(
                    range(hook.address, hook.address + hook.width)
                )
        permitted.update(checksums.checksum_byte_offsets())
        changed = {
            offset
            for offset, (before, after) in enumerate(
                zip(self.source, self.result.data)
            )
            if before != after
        }
        self.assertEqual(changed - permitted, set())
        self.assertEqual(len(permitted), 464)
        self.assertEqual(self.result.permitted_write_bytes, len(permitted))
        self.assertEqual(self.result.changed_bytes, len(changed))

    def test_startup_and_limiter_payloads_are_exact(self):
        self.assertEqual(
            self.result.data[
                limiter_gate.STARTUP_WRAPPER_START :
                limiter_gate.STARTUP_WRAPPER_END
            ],
            self.payloads["startup_wrapper"],
        )
        self.assertEqual(
            self.result.data[
                limiter_gate.LIMITER_COMMIT_START :
                limiter_gate.LIMITER_COMMIT_END
            ],
            self.payloads["limiter_commit"],
        )
        self.assertGreater(self.result.startup_wrapper_changed_bytes, 0)
        self.assertGreater(self.result.limiter_commit_changed_bytes, 0)

    def test_limiter_slots_are_map_1_and_pointer_tables_are_exact(self):
        for family in limiter_gate._limiter_families(self.layout):
            map_1 = self.source[
                family.canonical_address :
                family.canonical_address + family.byte_length
            ]
            for address in family.copies:
                with self.subTest(family=family.key, address=address):
                    self.assertEqual(
                        self.result.data[
                            address : address + family.byte_length
                        ],
                        map_1,
                    )
            expected_pointers = b"".join(
                address.to_bytes(4, self.layout.byte_order)
                for address in family.all_slot_addresses
            )
            start = family.pointer_table
            self.assertEqual(
                self.result.data[
                    start : start + self.layout.pointer_table_size
                ],
                expected_pointers,
            )

    def test_non_limiter_storage_remains_absent(self):
        for family in self.layout.families:
            if family.key in limiter_gate.LIMITER_FAMILY_KEYS:
                continue
            for address in family.copies:
                with self.subTest(family=family.key, address=address):
                    self.assertEqual(
                        self.result.data[
                            address : address + family.byte_length
                        ],
                        self.source[
                            address : address + family.byte_length
                        ],
                    )
            start = family.pointer_table
            self.assertEqual(
                self.result.data[
                    start : start + self.layout.pointer_table_size
                ],
                self.source[
                    start : start + self.layout.pointer_table_size
                ],
            )

    def test_selector_lookup_and_feedback_code_remain_absent(self):
        for key in (
            "selector_host",
            "adapter_select_helper",
            "lookup_adapters",
            "cruise_feedback_wrapper",
            "cruise_feedback_engine",
        ):
            unit = self.layout.assembly_unit_by_key[key]
            with self.subTest(unit=key):
                self.assertEqual(
                    self.result.data[unit.span.start : unit.span.end],
                    self.source[unit.span.start : unit.span.end],
                )

    def test_only_startup_and_direct_limiter_hooks_are_replaced(self):
        for hook in self.layout.hooks:
            with self.subTest(hook=hook.key):
                actual = int.from_bytes(
                    self.result.data[
                        hook.address : hook.address + hook.width
                    ],
                    self.layout.byte_order,
                )
                expected = (
                    hook.replacement
                    if hook.key == "startup_initializer"
                    or hook.key in limiter_gate.LIMITER_HOOK_KEYS
                    else hook.stock
                )
                self.assertEqual(actual, expected)
        self.assertEqual(self.result.hook_changed_bytes, 12)

    def test_output_checksums_are_valid(self):
        self.assertTrue(checksums.verify(self.source).valid)
        verification = checksums.verify(self.result.data)
        self.assertTrue(verification.valid)
        self.assertEqual(verification.stored, verification.calculated)
        self.assertNotEqual(
            self.result.source_sha256, self.result.output_sha256
        )
        self.assertGreater(self.result.checksum_changed_bytes, 0)

    def test_wrong_source_hash_is_rejected(self):
        with self.assertRaisesRegex(
            limiter_gate.LimiterGateError, "source sha256"
        ):
            limiter_gate.build_image(
                self.source,
                layout=self.layout,
                payloads=self.payloads,
                source_name="wrong source",
                expected_source_sha256="0" * 64,
            )

    def test_invalid_source_checksum_is_rejected(self):
        corrupt = bytearray(self.source)
        corrupt[0x8725] ^= 0x01
        with self.assertRaisesRegex(
            limiter_gate.LimiterGateError, "checksum mismatch"
        ):
            limiter_gate.build_image(
                corrupt,
                layout=self.layout,
                payloads=self.payloads,
                source_name="bad checksum",
                expected_source_sha256=limiter_gate.sha256(corrupt),
            )

    def test_different_selector_init_payload_is_rejected(self):
        corrupt = bytearray(self.source)
        corrupt[limiter_gate.STARTUP_WRAPPER_START] ^= 0x01
        corrupt = checksums.recalculate(corrupt)
        with self.assertRaisesRegex(
            limiter_gate.LimiterGateError,
            "source staged runtime differs",
        ):
            limiter_gate.build_image(
                corrupt,
                layout=self.layout,
                payloads=self.payloads,
                source_name="different selector init",
                expected_source_sha256=limiter_gate.sha256(corrupt),
            )

    def test_occupied_future_runtime_region_is_rejected(self):
        corrupt = bytearray(self.source)
        corrupt[0x000D2400] = 0x00
        corrupt = checksums.recalculate(corrupt)
        with self.assertRaisesRegex(
            limiter_gate.LimiterGateError,
            "source staged runtime differs at 0xd2400",
        ):
            limiter_gate.build_image(
                corrupt,
                layout=self.layout,
                payloads=self.payloads,
                source_name="occupied runtime",
                expected_source_sha256=limiter_gate.sha256(corrupt),
            )

    def test_nonstock_runtime_hook_is_rejected(self):
        hook = next(
            hook
            for hook in self.layout.hooks
            if hook.key not in {"startup_initializer"}
        )
        corrupt = bytearray(self.source)
        corrupt[hook.address] ^= 0x01
        corrupt = checksums.recalculate(corrupt)
        with self.assertRaisesRegex(
            limiter_gate.LimiterGateError, hook.key
        ):
            limiter_gate.build_image(
                corrupt,
                layout=self.layout,
                payloads=self.payloads,
                source_name="changed runtime hook",
                expected_source_sha256=limiter_gate.sha256(corrupt),
            )

    def test_nonzero_reset_selector_line_is_rejected(self):
        corrupt = bytearray(self.source)
        corrupt[limiter_gate.RESET_SELECTOR_LINE_START] = 0xEE
        corrupt = checksums.recalculate(corrupt)
        with self.assertRaisesRegex(
            limiter_gate.LimiterGateError,
            "reset-selector line is not all zero",
        ):
            limiter_gate.build_image(
                corrupt,
                layout=self.layout,
                payloads=self.payloads,
                source_name="different reset selector line",
                expected_source_sha256=limiter_gate.sha256(corrupt),
            )

    def test_invalid_payload_set_is_rejected(self):
        with self.assertRaisesRegex(
            limiter_gate.LimiterGateError,
            "payload set differs",
        ):
            limiter_gate.build_image(
                self.source,
                layout=self.layout,
                payloads={"startup_wrapper": self.payloads["startup_wrapper"]},
                source_name="missing payload",
                expected_source_sha256=self.source_sha256,
            )

    def test_default_output_path_is_adjacent_and_specific(self):
        source = Path("/tmp/example.bin")
        self.assertEqual(
            limiter_gate.default_output_path(source),
            Path("/tmp/example-startup-limiter-map1-d3660.bin"),
        )


if __name__ == "__main__":
    unittest.main()
