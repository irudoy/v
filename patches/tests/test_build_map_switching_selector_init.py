from pathlib import Path
import unittest

from patches import build_map_switching_selector_init as selector_init
from patches import build_map_switching_trampoline as trampoline
from patches import jk08a_checksums as checksums
from patches import map_switching_layout as layout_model


ROOT = Path(__file__).resolve().parents[2]
STOCK = (
    ROOT
    / "rom-images"
    / "23710-JK08A"
    / "1JK08A-20260726-stock.bin"
)


class BuildMapSwitchingSelectorInitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layout = layout_model.load_layout()
        marker_source = bytearray(STOCK.read_bytes())
        marker_source[
            trampoline.RESET_SELECTOR_LINE_START :
            trampoline.RESET_SELECTOR_LINE_END
        ] = bytes(128)
        marker_source[
            trampoline.MARKER_LINE_START : trampoline.MARKER_LINE_END
        ] = bytes(128)
        marker_source = checksums.recalculate(marker_source)
        trampoline_result = trampoline.build_image(
            marker_source,
            layout=cls.layout,
            source_name="synthetic marker readback",
            expected_source_sha256=trampoline.sha256(marker_source),
        )
        cls.source = trampoline_result.data
        cls.source_sha256 = selector_init.sha256(cls.source)
        cls.result = selector_init.build_image(
            cls.source,
            layout=cls.layout,
            source_name="synthetic trampoline readback",
            expected_source_sha256=cls.source_sha256,
        )

    def test_source_contract_is_exact_and_minimal(self):
        parsed = selector_init._require_selector_init_contract()
        self.assertEqual(parsed.instruction_count, 10)
        self.assertEqual(parsed.data_bytes, 8)
        self.assertEqual(
            selector_init.SELECTOR_INIT_BLOB.hex(),
            "4f22d105e0002100d002400b00094f26000b0009"
            "0002c648ffff5d00",
        )
        self.assertEqual(
            selector_init.sha256(selector_init.SELECTOR_INIT_BLOB),
            selector_init.SELECTOR_INIT_SHA256,
        )

    def test_source_is_exact_trampoline_gate(self):
        self.assertEqual(
            self.source[
                trampoline.TRAMPOLINE_START : trampoline.TRAMPOLINE_END
            ],
            trampoline.TRAMPOLINE_BLOB,
        )
        self.assertEqual(
            self.source[
                trampoline.TRAMPOLINE_END : selector_init.MARKER_LINE_END
            ],
            bytes(
                selector_init.MARKER_LINE_END - trampoline.TRAMPOLINE_END
            ),
        )

    def test_only_selector_init_and_checksum_fields_change(self):
        permitted = set(
            range(
                selector_init.SELECTOR_INIT_START,
                selector_init.SELECTOR_INIT_END,
            )
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
        self.assertEqual(self.result.permitted_write_bytes, len(permitted))
        self.assertEqual(self.result.changed_bytes, len(changed))

    def test_selector_init_and_surrounding_bytes_are_exact(self):
        self.assertEqual(
            self.result.data[
                selector_init.SELECTOR_INIT_START :
                selector_init.SELECTOR_INIT_END
            ],
            selector_init.SELECTOR_INIT_BLOB,
        )
        self.assertEqual(
            self.result.data[
                selector_init.MARKER_LINE_START :
                selector_init.SELECTOR_INIT_START
            ],
            bytes(
                selector_init.SELECTOR_INIT_START
                - selector_init.MARKER_LINE_START
            ),
        )
        self.assertEqual(
            self.result.data[
                selector_init.SELECTOR_INIT_END :
                selector_init.MARKER_LINE_END
            ],
            bytes(
                selector_init.MARKER_LINE_END
                - selector_init.SELECTOR_INIT_END
            ),
        )

    def test_startup_hook_stays_replaced_and_other_hooks_stay_stock(self):
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
                    else hook.stock
                )
                self.assertEqual(actual, expected)

    def test_output_checksums_are_valid(self):
        self.assertTrue(checksums.verify(self.source).valid)
        self.assertTrue(checksums.verify(self.result.data).valid)
        self.assertNotEqual(
            self.result.source_sha256, self.result.output_sha256
        )
        self.assertGreater(self.result.checksum_changed_bytes, 0)

    def test_wrong_source_hash_is_rejected(self):
        with self.assertRaisesRegex(
            selector_init.SelectorInitError, "source sha256"
        ):
            selector_init.build_image(
                self.source,
                layout=self.layout,
                source_name="wrong source",
                expected_source_sha256="0" * 64,
            )

    def test_invalid_source_checksum_is_rejected(self):
        corrupt = bytearray(self.source)
        corrupt[0x8725] ^= 0x01
        with self.assertRaisesRegex(
            selector_init.SelectorInitError, "checksum mismatch"
        ):
            selector_init.build_image(
                corrupt,
                layout=self.layout,
                source_name="bad checksum",
                expected_source_sha256=selector_init.sha256(corrupt),
            )

    def test_different_source_trampoline_is_rejected(self):
        corrupt = bytearray(self.source)
        corrupt[trampoline.TRAMPOLINE_START] ^= 0x01
        corrupt = checksums.recalculate(corrupt)
        with self.assertRaisesRegex(
            selector_init.SelectorInitError,
            "source trampoline payload differs",
        ):
            selector_init.build_image(
                corrupt,
                layout=self.layout,
                source_name="different trampoline",
                expected_source_sha256=selector_init.sha256(corrupt),
            )

    def test_nonzero_reset_selector_line_is_rejected(self):
        corrupt = bytearray(self.source)
        corrupt[selector_init.RESET_SELECTOR_LINE_START] = 0xEE
        with self.assertRaisesRegex(
            selector_init.SelectorInitError,
            "reset-selector line is not all zero",
        ):
            selector_init.build_image(
                corrupt,
                layout=self.layout,
                source_name="different selector line",
                expected_source_sha256=selector_init.sha256(corrupt),
            )

    def test_nonstock_runtime_hook_is_rejected(self):
        hook = next(
            hook
            for hook in self.layout.hooks
            if hook.key != "startup_initializer"
        )
        corrupt = bytearray(self.source)
        corrupt[hook.address] ^= 0x01
        corrupt = checksums.recalculate(corrupt)
        with self.assertRaisesRegex(
            selector_init.SelectorInitError, hook.key
        ):
            selector_init.build_image(
                corrupt,
                layout=self.layout,
                source_name="changed runtime hook",
                expected_source_sha256=selector_init.sha256(corrupt),
            )

    def test_stock_startup_hook_is_rejected(self):
        startup = next(
            hook
            for hook in self.layout.hooks
            if hook.key == "startup_initializer"
        )
        corrupt = bytearray(self.source)
        corrupt[startup.address : startup.address + startup.width] = (
            startup.stock.to_bytes(startup.width, self.layout.byte_order)
        )
        corrupt = checksums.recalculate(corrupt)
        with self.assertRaisesRegex(
            selector_init.SelectorInitError, "startup_initializer"
        ):
            selector_init.build_image(
                corrupt,
                layout=self.layout,
                source_name="stock startup hook",
                expected_source_sha256=selector_init.sha256(corrupt),
            )

    def test_default_output_path_is_adjacent_and_specific(self):
        source = Path("/tmp/example.bin")
        self.assertEqual(
            selector_init.default_output_path(source),
            Path("/tmp/example-startup-selector-init-d22a0.bin"),
        )


if __name__ == "__main__":
    unittest.main()
