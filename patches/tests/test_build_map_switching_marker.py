from pathlib import Path
import unittest

from patches import build_map_switching_marker as marker
from patches import jk08a_checksums as checksums
from patches import map_switching_layout as layout_model


ROOT = Path(__file__).resolve().parents[2]
STOCK = (
    ROOT
    / "rom-images"
    / "23710-JK08A"
    / "1JK08A-20260726-stock.bin"
)


class BuildMapSwitchingMarkerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layout = layout_model.load_layout()
        tuned = bytearray(STOCK.read_bytes())
        tuned[0x8725] ^= 0x01
        tuned[0x09A1A] ^= 0x11
        tuned[0x0B33A] ^= 0x22
        cls.tuned = checksums.recalculate(tuned)
        cls.tuned_sha256 = marker.sha256(cls.tuned)
        cls.result = marker.build_image(
            cls.tuned,
            layout=cls.layout,
            source_name="synthetic working base",
            expected_source_sha256=cls.tuned_sha256,
        )

    def test_complete_marker_line_is_zero_filled(self):
        self.assertEqual(
            self.tuned[marker.MARKER_START : marker.MARKER_END],
            b"\xff" * 128,
        )
        self.assertEqual(
            self.result.data[marker.MARKER_START : marker.MARKER_END],
            b"\x00" * 128,
        )
        self.assertEqual(self.result.marker_changed_bytes, 128)

    def test_only_marker_and_checksum_fields_change(self):
        permitted = set(range(marker.MARKER_START, marker.MARKER_END))
        permitted.update(checksums.checksum_byte_offsets())
        changed = {
            offset
            for offset, (before, after) in enumerate(
                zip(self.tuned, self.result.data)
            )
            if before != after
        }
        self.assertEqual(changed - permitted, set())
        self.assertEqual(self.result.permitted_write_bytes, 148)
        self.assertEqual(self.result.changed_bytes, len(changed))

    def test_output_checksums_are_valid(self):
        self.assertTrue(checksums.verify(self.tuned).valid)
        self.assertTrue(checksums.verify(self.result.data).valid)
        self.assertNotEqual(
            self.result.source_sha256, self.result.output_sha256
        )
        self.assertGreater(self.result.checksum_changed_bytes, 0)

    def test_all_runtime_hooks_remain_stock(self):
        for hook in self.layout.hooks:
            with self.subTest(hook=hook.key):
                source_value = int.from_bytes(
                    self.tuned[
                        hook.address : hook.address + hook.width
                    ],
                    self.layout.byte_order,
                )
                output_value = int.from_bytes(
                    self.result.data[
                        hook.address : hook.address + hook.width
                    ],
                    self.layout.byte_order,
                )
                self.assertEqual(source_value, hook.stock)
                self.assertEqual(output_value, hook.stock)

    def test_wrong_source_hash_is_rejected(self):
        with self.assertRaisesRegex(marker.MarkerError, "source sha256"):
            marker.build_image(
                self.tuned,
                layout=self.layout,
                source_name="wrong source",
                expected_source_sha256="0" * 64,
            )

    def test_invalid_source_checksum_is_rejected(self):
        corrupt = bytearray(self.tuned)
        corrupt[0x8725] ^= 0x01
        with self.assertRaisesRegex(marker.MarkerError, "checksum mismatch"):
            marker.build_image(
                corrupt,
                layout=self.layout,
                source_name="bad checksum",
                expected_source_sha256=marker.sha256(corrupt),
            )

    def test_occupied_marker_line_is_rejected(self):
        occupied = bytearray(self.tuned)
        occupied[marker.MARKER_START] = 0x00
        occupied = checksums.recalculate(occupied)
        with self.assertRaisesRegex(marker.MarkerError, "not erased"):
            marker.build_image(
                occupied,
                layout=self.layout,
                source_name="occupied marker",
                expected_source_sha256=marker.sha256(occupied),
            )

    def test_default_output_path_is_adjacent_and_specific(self):
        source = Path("/tmp/example.bin")
        self.assertEqual(
            marker.default_output_path(source),
            Path("/tmp/example-marker-only-d2280.bin"),
        )


if __name__ == "__main__":
    unittest.main()
