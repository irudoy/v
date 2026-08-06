from pathlib import Path
import tempfile
import unittest

from patches import apply_map_switching as runtime
from patches import build_map_switching_limiter as limiter_gate
from patches import build_map_switching_limiter_overlays as limiter_overlays
from patches import build_map_switching_lookup_overlays as lookup_overlays
from patches import build_map_switching_full_dfco_overlays as overlays
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


class BuildMapSwitchingFullDfcoOverlaysTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layout = layout_model.load_layout()
        cls.payloads = runtime.load_payloads(cls.layout)

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
        limiter_results = limiter_overlays.build_overlays(
            selector_result.data,
            layout=cls.layout,
            source_name="synthetic selector-init readback",
            expected_source_sha256=limiter_gate.sha256(
                selector_result.data
            ),
            expected_output_sha256=None,
        )
        lookup_results = lookup_overlays.build_overlays(
            limiter_results[-1].data,
            layout=cls.layout,
            payloads=cls.payloads,
            source_name="synthetic limiter Overlay 05",
            expected_source_sha256=limiter_results[-1].output_sha256,
            expected_output_sha256=None,
        )
        cls.source = lookup_results[-1].data
        cls.source_sha256 = limiter_gate.sha256(cls.source)
        cls.results = overlays.build_overlays(
            cls.source,
            layout=cls.layout,
            payloads=cls.payloads,
            source_name="synthetic lookup Overlay 14",
            expected_source_sha256=cls.source_sha256,
            expected_output_sha256=None,
        )

    def test_chain_has_six_ordered_stages(self):
        self.assertEqual(len(self.results), 6)
        self.assertEqual(
            tuple(result.spec.sequence for result in self.results),
            (15, 16, 17, 18, 19, 20),
        )

    def test_hardware_hash_contract_has_one_entry_per_stage(self):
        self.assertEqual(
            len(overlays.EXPECTED_OUTPUT_SHA256),
            len(overlays.OVERLAY_SPECS),
        )
        self.assertEqual(len(overlays.HISTORICAL_OUTPUT_SHA256), 5)
        self.assertEqual(len(set(overlays.EXPECTED_OUTPUT_SHA256)), 6)
        for digest in (
            *overlays.EXPECTED_OUTPUT_SHA256,
            *overlays.HISTORICAL_OUTPUT_SHA256,
        ):
            self.assertEqual(len(digest), 64)
            int(digest, 16)

    def test_every_stage_is_a_complete_checksum_valid_rom(self):
        for result in self.results:
            with self.subTest(stage=result.spec.sequence):
                self.assertEqual(len(result.data), limiter_gate.ROM_SIZE)
                verification = checksums.verify(result.data)
                self.assertTrue(verification.valid)
                self.assertEqual(
                    verification.stored, verification.calculated
                )

    def test_hash_chain_uses_previous_planned_image(self):
        self.assertEqual(
            self.results[0].source_sha256, self.source_sha256
        )
        for previous, current in zip(self.results, self.results[1:]):
            self.assertEqual(current.source_sha256, previous.output_sha256)

    def test_stage_15_installs_only_inactive_full_dfco_component(self):
        stage = self.results[0]
        self.assertFalse(stage.spec.functional_selection_allowed)
        self._assert_unit_state(stage.data, stage.spec)
        self._assert_hook_state(stage.data, stage.spec)
        overlays._require_full_dfco_storage(
            self.layout, self.source, stage.data, "test stage 15"
        )

    def test_stages_16_and_17_activate_one_shared_dfco_hook_each(self):
        for stage in self.results[1:3]:
            with self.subTest(stage=stage.spec.sequence):
                self.assertFalse(stage.spec.functional_selection_allowed)
                self._assert_unit_state(
                    stage.data, stage.spec
                )
                self._assert_hook_state(stage.data, stage.spec)

    def test_stage_18_is_selector_boot_only_gate(self):
        stage = self.results[3]
        self.assertFalse(stage.spec.functional_selection_allowed)
        self._assert_unit_state(stage.data, stage.spec)
        self._assert_hook_state(stage.data, stage.spec)
        for key in overlays.FEEDBACK_UNIT_KEYS:
            unit = self.layout.assembly_unit_by_key[key]
            self.assertEqual(
                stage.data[unit.span.start : unit.span.end],
                self.source[unit.span.start : unit.span.end],
            )

    def test_stage_19_retains_hardware_tested_feedback_timing(self):
        stage = self.results[4]
        self.assertTrue(stage.spec.functional_selection_allowed)
        self._assert_unit_state(stage.data, stage.spec)
        self._assert_hook_state(stage.data, stage.spec)
        start = self.layout.feedback.phase_counts_address
        self.assertEqual(
            stage.data[start : start + 2], b"\x0a\x0a"
        )

    def test_stage_20_is_complete_runtime_endpoint(self):
        stage = self.results[5]
        self.assertTrue(stage.spec.functional_selection_allowed)
        self._assert_unit_state(stage.data, stage.spec)
        self._assert_hook_state(stage.data, stage.spec)
        self.assertEqual(
            stage.data,
            overlays._build_final_endpoint(
                self.layout, self.source, self.payloads
            ),
        )

    def test_stage_20_matches_direct_patch_except_pcmflash_line(self):
        direct = runtime.patch_image(
            STOCK.read_bytes(),
            layout=self.layout,
            blobs=self.payloads,
            source_name=str(STOCK),
        ).data
        stage = self.results[5].data
        differences = {
            offset
            for offset, (left, right) in enumerate(zip(direct, stage))
            if left != right
        }
        expected = set(
            range(
                limiter_gate.RESET_SELECTOR_LINE_START,
                limiter_gate.RESET_SELECTOR_LINE_END,
            )
        )
        self.assertEqual(differences, expected)
        self.assertEqual(
            direct[
                limiter_gate.RESET_SELECTOR_LINE_START :
                limiter_gate.RESET_SELECTOR_LINE_END
            ],
            bytes([0xEE]) * 128,
        )
        self.assertEqual(
            stage[
                limiter_gate.RESET_SELECTOR_LINE_START :
                limiter_gate.RESET_SELECTOR_LINE_END
            ],
            bytes(128),
        )

    def test_storage_is_valid_across_all_stages(self):
        for result in self.results:
            with self.subTest(stage=result.spec.sequence):
                overlays._require_storage(
                    self.layout,
                    self.source,
                    result.data,
                    f"test stage {result.spec.sequence}",
                    require_full_dfco=True,
                    require_idle_ignition=result.spec.sequence >= 20,
                )

    def test_each_stage_changes_only_its_component_and_checksums(self):
        checksum_offsets = set(checksums.checksum_byte_offsets())
        previous = self.source
        for result in self.results:
            component = overlays._component_offsets(
                self.layout, result.spec
            )
            changed = {
                offset
                for offset, (before, after) in enumerate(
                    zip(previous, result.data)
                )
                if before != after
            }
            with self.subTest(stage=result.spec.sequence):
                self.assertEqual(
                    changed - component - checksum_offsets, set()
                )
                self.assertEqual(
                    result.component_changed_bytes,
                    len(changed & component),
                )
                self.assertEqual(
                    result.checksum_changed_bytes,
                    len(changed & checksum_offsets),
                )
                self.assertEqual(
                    result.permitted_write_bytes,
                    len(component | checksum_offsets),
                )
            previous = result.data
        self.assertEqual(
            tuple(result.permitted_write_bytes for result in self.results),
            (284, 24, 24, 384, 408, 194),
        )

    def test_wrong_source_is_rejected(self):
        with self.assertRaisesRegex(
            overlays.FullDfcoOverlayError, "source sha256"
        ):
            overlays.build_overlays(
                self.source,
                layout=self.layout,
                payloads=self.payloads,
                source_name="wrong source",
                expected_source_sha256="0" * 64,
                expected_output_sha256=None,
            )

    def test_missing_source_unit_is_rejected(self):
        corrupted = bytearray(self.source)
        unit = self.layout.assembly_unit_by_key["lookup_adapters"]
        corrupted[unit.span.start] ^= 0x01
        corrupted = checksums.recalculate(corrupted)
        with self.assertRaisesRegex(
            overlays.FullDfcoOverlayError,
            "assembly unit lookup_adapters differs",
        ):
            overlays.build_overlays(
                corrupted,
                layout=self.layout,
                payloads=self.payloads,
                source_name="corrupt source unit",
                expected_source_sha256=None,
                expected_output_sha256=None,
            )

    def test_wrong_expected_hash_count_is_rejected(self):
        with self.assertRaisesRegex(
            overlays.FullDfcoOverlayError,
            "SHA-256 count differs",
        ):
            overlays.build_overlays(
                self.source,
                layout=self.layout,
                payloads=self.payloads,
                source_name="wrong hash count",
                expected_source_sha256=self.source_sha256,
                expected_output_sha256=("0" * 64,),
            )

    def test_default_paths_continue_global_stage_numbers(self):
        source = Path(
            "/tmp/example-14-fuel-comp-startup-hook-2cf1c_readback.bin"
        )
        prefix = overlays.default_output_prefix(source)
        self.assertEqual(
            prefix, Path("/tmp/example-map-switching-safe-v5")
        )
        self.assertEqual(
            tuple(path.name for path in overlays.output_paths(prefix)),
            (
                "example-map-switching-safe-v5-15-full-dfco-payload-map1.bin",
                "example-map-switching-safe-v5-16-dfco-hold-entry-hook-4fdd0.bin",
                "example-map-switching-safe-v5-17-dfco-full-intermediate-restore-hook-50258.bin",
                "example-map-switching-safe-v5-18-selector-host-boot-only-no-map-gesture.bin",
                "example-map-switching-safe-v5-19-can-feedback-full-runtime.bin",
                "example-map-switching-safe-v5-20-idle-ignition-feedback-15x15.bin",
            ),
        )

    def test_writer_creates_exact_images_sidecars_and_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            prefix = Path(directory) / "chain"
            paths, manifest, created = overlays.write_overlays(
                prefix, self.results
            )
            self.assertEqual(created, 13)
            for result, path in zip(self.results, paths):
                self.assertEqual(path.read_bytes(), result.data)
                self.assertEqual(
                    path.with_name(f"{path.name}.md5").read_text(
                        encoding="ascii"
                    ),
                    f"{result.output_md5} *{path.name}\n",
                )
            self.assertEqual(
                manifest.read_text(encoding="ascii"),
                overlays._manifest_content(self.results, paths),
            )
            _, _, repeated_created = overlays.write_overlays(
                prefix, self.results
            )
            self.assertEqual(repeated_created, 0)

    def test_writer_preflights_different_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            prefix = Path(directory) / "chain"
            first = overlays.output_paths(prefix)[0]
            first.write_bytes(b"different")
            with self.assertRaisesRegex(
                overlays.FullDfcoOverlayError,
                "existing output differs",
            ):
                overlays.write_overlays(prefix, self.results)
            self.assertFalse(overlays.output_paths(prefix)[1].exists())

    def _assert_unit_state(self, image, spec):
        active_keys = set(spec.active_unit_keys)
        for unit in self.layout.assembly_units:
            if unit.key not in active_keys:
                expected = bytes([unit.fill]) * unit.span.size
            elif spec.default_feedback_counts:
                expected = overlays.composer.endpoint_unit_bytes(
                    self.layout, self.payloads, unit
                )
            else:
                expected = self.payloads[unit.key]
            self.assertEqual(
                image[unit.span.start : unit.span.end], expected
            )

    def _assert_hook_state(self, image, spec):
        active_keys = set(spec.active_hook_keys)
        for hook in self.layout.hooks:
            actual = int.from_bytes(
                image[hook.address : hook.address + hook.width],
                self.layout.byte_order,
            )
            if hook.key not in active_keys:
                expected = hook.stock
            elif (
                hook.key in overlays.FULL_DFCO_HOOK_KEYS
                and hook.key not in spec.full_dfco_hook_keys
            ):
                expected = lookup_overlays.LEGACY_OVERRUN_ADAPTER_ENTRY
            else:
                expected = hook.replacement
            self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
