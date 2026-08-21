from pathlib import Path
import tempfile
import unittest

from patches import apply_map_switching as patcher
from patches import jk08a_checksums as checksums
from patches import map_switching_compose as composer
from patches import map_switching_layout as layout_model
from tools.mapkit import rom as romkit


ROOT = Path(__file__).resolve().parents[2]
STOCK = (
    ROOT
    / "rom-images"
    / "23710-JK08A"
    / "1JK08A-20260726-stock.bin"
)


class ApplyMapSwitchingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layout = layout_model.load_layout()
        cls.stock = STOCK.read_bytes()
        tuned = bytearray(cls.stock)
        tuned[0x8725] = 0x00
        tuned[0x942C : 0x942E] = b"\xff\xff"
        tuned[0x09A1A] ^= 0x11
        tuned[0x09B1A] ^= 0x22
        tuned[0x0A29A] ^= 0x33
        tuned[0x0B33A] ^= 0x44
        tuned[0x126E4] ^= 0x77
        tuned[0x12718] ^= 0x55
        tuned[0x12818] ^= 0x66
        tuned[0x1298C] ^= 0x88
        cls.tuned = checksums.recalculate(tuned)
        cls.blobs = patcher.load_payloads(cls.layout)
        cls.result = patcher.patch_image(
            cls.tuned,
            layout=cls.layout,
            blobs=cls.blobs,
            source_name="synthetic tuned JK08A",
        )

    def test_tracked_payload_bundle_matches_every_manifest_lock(self):
        self.assertEqual(
            set(self.blobs), set(self.layout.assembly_unit_by_key)
        )
        for unit in self.layout.assembly_units:
            with self.subTest(unit=unit.key):
                self.assertEqual(len(self.blobs[unit.key]), unit.span.size)
                self.assertEqual(
                    layout_model.validate_assembled_blob(
                        unit, self.blobs[unit.key]
                    ),
                    self.blobs[unit.key],
                )

    def test_patcher_accepts_calibration_changes_and_recalculates_checksums(self):
        self.assertTrue(checksums.verify(self.tuned).valid)
        self.assertTrue(checksums.verify(self.result.data).valid)
        self.assertNotEqual(
            self.result.source_sha256, self.result.output_sha256
        )
        self.assertGreater(self.result.final_changed_bytes, 0)
        self.assertGreater(self.result.checksum_changed_bytes, 0)

    def test_input_calibration_and_configuration_are_preserved(self):
        permitted = {
            offset
            for region in composer.composition_write_ranges(self.layout)
            for offset in range(region.start, region.end)
        }
        permitted.update(checksums.checksum_byte_offsets())
        changed_outside = {
            offset
            for offset, (source, output) in enumerate(
                zip(self.tuned, self.result.data)
            )
            if source != output and offset not in permitted
        }
        self.assertEqual(changed_outside, set())
        for offset in (
            0x8725,
            0x942C,
            0x942D,
            0x09A1A,
            0x09B1A,
            0x0A29A,
            0x0B33A,
            0x126E4,
            0x12718,
            0x12818,
            0x1298C,
            0x12196,
            0x1219E,
        ):
            with self.subTest(offset=offset):
                self.assertEqual(
                    self.result.data[offset], self.tuned[offset]
                )

    def test_maps_two_through_five_start_as_input_map_one(self):
        for family in self.layout.families:
            source = self.tuned[
                family.canonical_address :
                family.canonical_address + family.byte_length
            ]
            for slot, address in enumerate(family.copies, 2):
                with self.subTest(family=family.key, slot=slot):
                    self.assertEqual(
                        self.result.data[
                            address : address + family.byte_length
                        ],
                        source,
                    )

    def test_runtime_hooks_and_feedback_configuration_are_installed(self):
        for hook in self.layout.hooks:
            with self.subTest(hook=hook.key):
                actual = int.from_bytes(
                    self.result.data[
                        hook.address : hook.address + hook.width
                    ],
                    self.layout.byte_order,
                )
                self.assertEqual(actual, hook.replacement)
        start = self.layout.feedback.phase_counts_address
        self.assertEqual(self.result.data[start : start + 2], b"\x1e\x1e")

    def test_invalid_input_checksum_is_rejected(self):
        corrupt = bytearray(self.tuned)
        corrupt[0x8725] ^= 0x01
        with self.assertRaisesRegex(patcher.PatchError, "checksum mismatch"):
            patcher.patch_image(
                corrupt, self.layout, self.blobs, "bad checksum"
            )

    def test_changed_read_only_anchor_is_rejected(self):
        corrupt = bytearray(self.tuned)
        corrupt[0x29CC] ^= 0x01
        corrupt = checksums.recalculate(corrupt)
        with self.assertRaisesRegex(
            patcher.PatchError, "startup_clear_start_stock"
        ):
            patcher.patch_image(
                corrupt, self.layout, self.blobs, "changed anchor"
            )

    def test_changed_protected_upper_rom_is_rejected(self):
        corrupt = bytearray(self.tuned)
        corrupt[0x30000] ^= 0x01
        corrupt = checksums.recalculate(corrupt)
        with self.assertRaisesRegex(
            patcher.PatchError, "protected upper ROM differs"
        ):
            patcher.patch_image(
                corrupt, self.layout, self.blobs, "changed code"
            )

    def test_changed_vector_prefix_is_rejected(self):
        corrupt = bytearray(self.tuned)
        corrupt[0x100] ^= 0x01
        self.assertTrue(checksums.verify(corrupt).valid)
        with self.assertRaisesRegex(
            patcher.PatchError, "protected ROM differs"
        ):
            patcher.patch_image(
                corrupt, self.layout, self.blobs, "changed vector prefix"
            )

    def test_occupied_allocation_and_already_patched_rom_are_rejected(self):
        occupied = bytearray(self.tuned)
        occupied[self.layout.claimed_rom.start] = 0x00
        occupied = checksums.recalculate(occupied)
        with self.assertRaisesRegex(
            patcher.PatchError, "claimed ROM is not erased"
        ):
            patcher.patch_image(
                occupied, self.layout, self.blobs, "occupied allocation"
            )
        with self.assertRaisesRegex(
            patcher.PatchError, "claimed ROM is not erased"
        ):
            patcher.patch_image(
                self.result.data,
                self.layout,
                self.blobs,
                "already patched",
            )

    def test_changed_calibration_identity_is_rejected(self):
        corrupt = bytearray(self.tuned)
        corrupt[layout_model.COMPATIBLE_IDENTITY_START] ^= 0x01
        corrupt = checksums.recalculate(corrupt)
        with self.assertRaisesRegex(
            patcher.PatchError, "calibration identity"
        ):
            patcher.patch_image(
                corrupt, self.layout, self.blobs, "wrong identity"
            )

    def test_output_and_md5_sidecar_are_idempotent_and_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "image-map-switching.bin"
            self.assertTrue(
                patcher.write_output(output, self.result.data)
            )
            self.assertFalse(
                patcher.write_output(output, self.result.data)
            )
            self.assertTrue(
                patcher.write_md5_sidecar(output, self.result.data)
            )
            self.assertFalse(
                patcher.write_md5_sidecar(output, self.result.data)
            )
            output.write_bytes(b"different")
            with self.assertRaisesRegex(
                patcher.PatchError, "existing output differs"
            ):
                patcher.write_output(output, self.result.data)

    def test_default_output_path_is_adjacent_and_non_destructive(self):
        source = Path("/tmp/example.bin")
        self.assertEqual(
            patcher.default_output_path(source),
            Path("/tmp/example-map-switching.bin"),
        )

    def test_compatible_layout_accepts_the_tuned_lower_partition(self):
        image = romkit.Image("JK08A", "synthetic", self.tuned)
        self.assertIs(
            layout_model.validate_compatible_image(self.layout, image),
            image,
        )


if __name__ == "__main__":
    unittest.main()
