import contextlib
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from patches import apply_map_switching as patcher
from patches import apply_can_telemetry
from patches import apply_rolling_launch
from patches import jk08a_checksums as checksums
from patches import map_switching_compose as composer
from patches import rolling_launch
from patches import rolling_launch_compose
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
        self.assertEqual(self.result.data[start : start + 2], b"\x14\x14")

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

    def test_each_cli_refuses_foreign_md5_before_publishing_a_rom(self):
        rolling_result = apply_rolling_launch.patch_image(
            self.result.data,
            calibration=rolling_launch.Calibration(),
            efficiency=rolling_launch_compose.efficiency_table(self.result.data),
            expected_source_sha256=patcher.sha256(self.result.data),
        )
        telemetry_result = apply_can_telemetry.patch_image(rolling_result.data)
        for module, source, result in (
            (patcher, self.tuned, self.result),
            (apply_can_telemetry, rolling_result.data, telemetry_result),
        ):
            with self.subTest(module=module.__name__), tempfile.TemporaryDirectory() as directory:
                input_path = Path(directory) / "input.bin"
                input_path.write_bytes(source)
                output = Path(directory) / "image.bin"
                sidecar = Path(f"{output}.md5")
                sidecar.write_bytes(b"foreign MD5")
                error = io.StringIO()
                with (mock.patch.object(module, "patch_image", return_value=result),
                      contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(error)):
                    with self.assertRaises(SystemExit) as stopped:
                        module.main([str(input_path), "--output", str(output)])
                self.assertEqual(stopped.exception.code, 2)
                self.assertIn("artifact differs", error.getvalue())
                self.assertEqual(set(Path(directory).iterdir()), {input_path, sidecar})
                self.assertEqual(sidecar.read_bytes(), b"foreign MD5")

    def test_compatible_layout_accepts_the_tuned_lower_partition(self):
        image = romkit.Image("JK08A", "synthetic", self.tuned)
        self.assertIs(
            layout_model.validate_compatible_image(self.layout, image),
            image,
        )


class ArtifactPublicationTest(unittest.TestCase):
    image = b"complete ROM bytes"

    def test_md5_is_complete_before_the_rom_is_published(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "image.bin"
            sidecar = Path(f"{output}.md5")
            link = os.link

            def publish(source, destination):
                self.assertFalse(output.exists())
                if destination == output:
                    self.assertEqual(
                        sidecar.read_text(encoding="ascii"),
                        f"{patcher.md5(self.image)} *image.bin\n",
                    )
                    self.assertEqual(source.read_bytes(), self.image)
                link(source, destination)

            with mock.patch.object(patcher.os, "link", side_effect=publish):
                self.assertTrue(patcher.write_output_with_md5(output, self.image))
            self.assertEqual(output.read_bytes(), self.image)
            self.assertFalse(patcher.write_output_with_md5(output, self.image))

    def test_staging_failure_or_truncation_publishes_nothing_and_allows_retry(self):
        for truncate in (False, True):
            with self.subTest(truncate=truncate), tempfile.TemporaryDirectory() as directory:
                output = Path(directory) / "image.bin"
                fsync = os.fsync
                calls = 0

                def sync(fd):
                    nonlocal calls
                    calls += 1
                    if calls == 2:
                        if not truncate:
                            raise OSError("injected staging failure")
                        os.ftruncate(fd, 1)
                    fsync(fd)

                with mock.patch.object(patcher.os, "fsync", side_effect=sync):
                    with self.assertRaises((OSError, patcher.PatchError)):
                        patcher.write_output_with_md5(output, self.image)
                self.assertEqual(list(Path(directory).iterdir()), [])
                self.assertTrue(patcher.write_output_with_md5(output, self.image))

    def test_publication_failure_preserves_existing_sidecar_and_allows_retry(self):
        for existing in (False, True):
            with self.subTest(existing=existing), tempfile.TemporaryDirectory() as directory:
                output = Path(directory) / "image.bin"
                sidecar = Path(f"{output}.md5")
                if existing:
                    patcher.write_md5_sidecar(output, self.image)
                link = os.link

                def publish(source, destination):
                    if destination == output:
                        raise OSError("injected publication failure")
                    link(source, destination)

                with mock.patch.object(patcher.os, "link", side_effect=publish):
                    with self.assertRaisesRegex(OSError, "publication failure"):
                        patcher.write_output_with_md5(output, self.image)
                self.assertEqual(
                    list(Path(directory).iterdir()), [sidecar] if existing else []
                )
                self.assertTrue(patcher.write_output_with_md5(output, self.image))

    def test_foreign_sidecar_prevents_rom_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "image.bin"
            sidecar = Path(f"{output}.md5")
            sidecar.write_bytes(b"foreign sidecar")
            with self.assertRaisesRegex(patcher.PatchError, "artifact differs"):
                patcher.write_output_with_md5(output, self.image)
            self.assertEqual(list(Path(directory).iterdir()), [sidecar])
            self.assertEqual(sidecar.read_bytes(), b"foreign sidecar")

    def test_concurrent_foreign_rom_is_not_overwritten_or_removed(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "image.bin"
            link = os.link

            def publish(source, destination):
                if destination == output:
                    output.write_bytes(b"foreign ROM")
                link(source, destination)

            with mock.patch.object(patcher.os, "link", side_effect=publish):
                with self.assertRaisesRegex(patcher.PatchError, "artifact differs"):
                    patcher.write_output_with_md5(output, self.image)
            self.assertEqual(list(Path(directory).iterdir()), [output])
            self.assertEqual(output.read_bytes(), b"foreign ROM")

    def test_cleanup_preserves_replaced_or_modified_sidecar(self):
        for replace in (False, True):
            with self.subTest(replace=replace), tempfile.TemporaryDirectory() as directory:
                output = Path(directory) / "image.bin"
                sidecar = Path(f"{output}.md5")
                link = os.link

                def publish(source, destination):
                    if destination == output:
                        content = sidecar.read_bytes() if replace else b"foreign data"
                        if replace:
                            sidecar.unlink()
                        sidecar.write_bytes(content)
                        raise OSError("injected publication failure")
                    link(source, destination)

                with mock.patch.object(patcher.os, "link", side_effect=publish):
                    with self.assertRaises(OSError):
                        patcher.write_output_with_md5(output, self.image)
                self.assertEqual(list(Path(directory).iterdir()), [sidecar])
                if not replace:
                    self.assertEqual(sidecar.read_bytes(), b"foreign data")

    def test_default_outputs_reject_stock_collection_and_symlink_alias(self):
        with tempfile.TemporaryDirectory() as directory:
            alias = Path(directory) / "stock"
            alias.symlink_to(STOCK.parent, target_is_directory=True)
            for module in (patcher, apply_can_telemetry):
                for source in (STOCK, alias / STOCK.name):
                    with self.subTest(module=module.__name__, source=source):
                        with self.assertRaisesRegex(patcher.PatchError, "explicit --output"):
                            module.default_output_path(source)


if __name__ == "__main__":
    unittest.main()
