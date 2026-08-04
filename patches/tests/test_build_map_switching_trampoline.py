from pathlib import Path
import unittest

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


class BuildMapSwitchingTrampolineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layout = layout_model.load_layout()
        source = bytearray(STOCK.read_bytes())
        source[
            trampoline.RESET_SELECTOR_LINE_START :
            trampoline.RESET_SELECTOR_LINE_END
        ] = bytes(128)
        source[
            trampoline.MARKER_LINE_START : trampoline.MARKER_LINE_END
        ] = bytes(128)
        cls.source = checksums.recalculate(source)
        cls.source_sha256 = trampoline.sha256(cls.source)
        cls.result = trampoline.build_image(
            cls.source,
            layout=cls.layout,
            source_name="synthetic hardware readback",
            expected_source_sha256=cls.source_sha256,
        )

    def test_source_contract_is_exact_and_minimal(self):
        parsed = trampoline._require_trampoline_contract()
        self.assertEqual(parsed.instruction_count, 3)
        self.assertEqual(parsed.data_bytes, 4)
        self.assertEqual(
            trampoline.TRAMPOLINE_BLOB.hex(),
            "d001402b000900000002c648",
        )
        self.assertEqual(
            trampoline.sha256(trampoline.TRAMPOLINE_BLOB),
            trampoline.TRAMPOLINE_SHA256,
        )

    def test_complete_marker_line_starts_zero_filled(self):
        self.assertEqual(
            self.source[
                trampoline.MARKER_LINE_START : trampoline.MARKER_LINE_END
            ],
            bytes(128),
        )

    def test_only_hook_trampoline_and_checksum_fields_change(self):
        startup = next(
            hook
            for hook in self.layout.hooks
            if hook.key == "startup_initializer"
        )
        permitted = set(
            range(startup.address, startup.address + startup.width)
        )
        permitted.update(
            range(trampoline.TRAMPOLINE_START, trampoline.TRAMPOLINE_END)
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

    def test_trampoline_and_surrounding_marker_bytes_are_exact(self):
        self.assertEqual(
            self.result.data[
                trampoline.TRAMPOLINE_START : trampoline.TRAMPOLINE_END
            ],
            trampoline.TRAMPOLINE_BLOB,
        )
        self.assertEqual(
            self.result.data[
                trampoline.MARKER_LINE_START : trampoline.TRAMPOLINE_START
            ],
            bytes(
                trampoline.TRAMPOLINE_START
                - trampoline.MARKER_LINE_START
            ),
        )
        self.assertEqual(
            self.result.data[
                trampoline.TRAMPOLINE_END : trampoline.MARKER_LINE_END
            ],
            bytes(
                trampoline.MARKER_LINE_END - trampoline.TRAMPOLINE_END
            ),
        )

    def test_only_startup_hook_is_replaced(self):
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
            trampoline.TrampolineError, "source sha256"
        ):
            trampoline.build_image(
                self.source,
                layout=self.layout,
                source_name="wrong source",
                expected_source_sha256="0" * 64,
            )

    def test_invalid_source_checksum_is_rejected(self):
        corrupt = bytearray(self.source)
        corrupt[0x8725] ^= 0x01
        with self.assertRaisesRegex(
            trampoline.TrampolineError, "checksum mismatch"
        ):
            trampoline.build_image(
                corrupt,
                layout=self.layout,
                source_name="bad checksum",
                expected_source_sha256=trampoline.sha256(corrupt),
            )

    def test_nonzero_marker_line_is_rejected(self):
        corrupt = bytearray(self.source)
        corrupt[trampoline.MARKER_LINE_START] = 0x01
        corrupt = checksums.recalculate(corrupt)
        with self.assertRaisesRegex(
            trampoline.TrampolineError, "marker line is not all zero"
        ):
            trampoline.build_image(
                corrupt,
                layout=self.layout,
                source_name="occupied marker line",
                expected_source_sha256=trampoline.sha256(corrupt),
            )

    def test_nonzero_reset_selector_line_is_rejected(self):
        corrupt = bytearray(self.source)
        corrupt[trampoline.RESET_SELECTOR_LINE_START] = 0xEE
        with self.assertRaisesRegex(
            trampoline.TrampolineError,
            "reset-selector line is not all zero",
        ):
            trampoline.build_image(
                corrupt,
                layout=self.layout,
                source_name="different selector line",
                expected_source_sha256=trampoline.sha256(corrupt),
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
            trampoline.TrampolineError, hook.key
        ):
            trampoline.build_image(
                corrupt,
                layout=self.layout,
                source_name="changed runtime hook",
                expected_source_sha256=trampoline.sha256(corrupt),
            )

    def test_default_output_path_is_adjacent_and_specific(self):
        source = Path("/tmp/example.bin")
        self.assertEqual(
            trampoline.default_output_path(source),
            Path("/tmp/example-startup-trampoline-d22a0.bin"),
        )


if __name__ == "__main__":
    unittest.main()
