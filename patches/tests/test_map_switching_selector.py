import importlib.util
from pathlib import Path
import unittest

from patches import map_switching_layout


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "patches" / "map_switching_selector.py"
SPEC = importlib.util.spec_from_file_location(
    "map_switching_selector", MODULE_PATH
)
selector = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(selector)


def step(state, previous_code, current_code, main_pressed=False):
    return selector.advance_selector(
        state,
        previous_code,
        current_code,
        main_pressed=main_pressed,
    )


def pulse(state):
    state = step(state, selector.SET_COAST, selector.CANCEL)
    return step(state, selector.CANCEL, selector.SET_COAST)


class MapSwitchingSelectorTest(unittest.TestCase):
    def setUp(self):
        self.state = selector.SelectorState()

    def arm(self, state=None):
        return step(
            state or self.state,
            selector.RELEASED,
            selector.SET_COAST,
        )

    def test_reference_model_defaults_to_map_1(self):
        self.assertEqual(self.state, selector.SelectorState())
        for base in (
            selector.STOCK_OVER_RUN_HOLD_BASE,
            selector.STOCK_OVER_RUN_CUT_BASE,
            selector.STOCK_OVER_RUN_RESTORE_BASE,
            selector.STOCK_OVER_RUN_INTERMEDIATE_RESTORE_BASE,
        ):
            with self.subTest(base=hex(base)):
                self.assertEqual(
                    selector.select_calibration_base(
                        base, self.state.active_index
                    ),
                    base,
                )

    def test_one_cancel_pulse_commits_map_1_on_release(self):
        state = pulse(self.arm())
        self.assertEqual(state.active_index, 0)
        self.assertEqual(state.selection_count, 1)
        state = step(state, selector.SET_COAST, selector.RELEASED)
        self.assertEqual(state, selector.SelectorState(active_index=0))

    def test_two_cancel_pulses_commit_map_2_only_on_release(self):
        state = pulse(pulse(self.arm()))
        self.assertEqual(state.active_index, 0)
        self.assertEqual(state.selection_count, 2)
        state = step(state, selector.SET_COAST, selector.RELEASED)
        self.assertEqual(state, selector.SelectorState(active_index=1))

    def test_five_cancel_pulses_commit_map_5(self):
        state = self.arm()
        for _ in range(5):
            state = pulse(state)
        self.assertEqual(state.active_index, 0)
        self.assertEqual(state.selection_count, 5)
        state = step(state, selector.SET_COAST, selector.RELEASED)
        self.assertEqual(state, selector.SelectorState(active_index=4))

    def test_release_without_a_pulse_aborts(self):
        state = self.arm(selector.SelectorState(active_index=1))
        state = step(state, selector.SET_COAST, selector.RELEASED)
        self.assertEqual(state, selector.SelectorState(active_index=1))

    def test_unexpected_transition_aborts_without_changing_map(self):
        state = self.arm(selector.SelectorState(active_index=1))
        state = step(state, selector.SET_COAST, selector.RESUME_ACCEL)
        self.assertEqual(state, selector.SelectorState(active_index=1))

    def test_zero_code_aborts_an_armed_gesture(self):
        state = self.arm(selector.SelectorState(active_index=1))
        state = step(state, selector.SET_COAST, selector.INVALID_ZERO)
        self.assertEqual(state, selector.SelectorState(active_index=1))

    def test_zero_to_set_does_not_arm(self):
        state = step(
            selector.SelectorState(active_index=1),
            selector.INVALID_ZERO,
            selector.SET_COAST,
        )
        self.assertEqual(state, selector.SelectorState(active_index=1))

    def test_main_press_aborts_an_armed_gesture(self):
        state = self.arm(selector.SelectorState(active_index=1))
        state = step(
            state,
            selector.SET_COAST,
            selector.SET_COAST,
            main_pressed=True,
        )
        self.assertEqual(state, selector.SelectorState(active_index=1))

    def test_stable_samples_do_not_increment_the_count(self):
        state = self.arm()
        state = step(state, selector.SET_COAST, selector.SET_COAST)
        state = step(state, selector.SET_COAST, selector.CANCEL)
        state = step(state, selector.CANCEL, selector.CANCEL)
        state = step(state, selector.CANCEL, selector.SET_COAST)
        self.assertEqual(state.selection_count, 1)

    def test_sixth_cancel_pulse_aborts_for_five_slots(self):
        state = self.arm(selector.SelectorState(active_index=1))
        for _ in range(5):
            state = pulse(state)
        state = pulse(state)
        self.assertEqual(state, selector.SelectorState(active_index=1))

    def test_timeout_aborts_before_a_commit(self):
        state = self.arm(selector.SelectorState(active_index=1))
        for _ in range(selector.TIMEOUT_TICKS - 2):
            state = step(state, selector.SET_COAST, selector.SET_COAST)
        self.assertNotEqual(state.phase, selector.Phase.IDLE)
        state = step(state, selector.SET_COAST, selector.SET_COAST)
        self.assertEqual(state, selector.SelectorState(active_index=1))

    def test_corrupt_state_falls_back_and_does_not_arm(self):
        state = selector.SelectorState(
            active_index=0xFF,
            phase=selector.Phase.SET_HELD,
            selection_count=1,
            elapsed_ticks=5,
        )
        state = step(state, selector.SET_COAST, selector.RELEASED)
        self.assertEqual(state, selector.SelectorState(active_index=0))

    def test_accessor_changes_only_the_selected_stock_base(self):
        self.assertEqual(
            selector.select_calibration_base(
                selector.STOCK_OVER_RUN_HOLD_BASE, 1
            ),
            selector.OVER_RUN_HOLD_BASES[1],
        )
        self.assertEqual(
            selector.select_calibration_base(
                selector.STOCK_OVER_RUN_CUT_BASE, 1
            ),
            selector.OVER_RUN_CUT_BASES[1],
        )
        self.assertEqual(
            selector.select_calibration_base(
                selector.STOCK_OVER_RUN_RESTORE_BASE, 1
            ),
            selector.OVER_RUN_RESTORE_BASES[1],
        )
        self.assertEqual(
            selector.select_calibration_base(
                selector.STOCK_OVER_RUN_INTERMEDIATE_RESTORE_BASE, 1
            ),
            selector.OVER_RUN_INTERMEDIATE_RESTORE_BASES[1],
        )

    def test_accessor_falls_back_to_map_1_for_invalid_index(self):
        for active_index in (-1, 5, 0xFF):
            with self.subTest(active_index=active_index):
                for base in (
                    selector.STOCK_OVER_RUN_HOLD_BASE,
                    selector.STOCK_OVER_RUN_CUT_BASE,
                    selector.STOCK_OVER_RUN_RESTORE_BASE,
                    selector.STOCK_OVER_RUN_INTERMEDIATE_RESTORE_BASE,
                ):
                    self.assertEqual(
                        selector.select_calibration_base(base, active_index),
                        base,
                    )

    def test_accessor_exposes_all_five_bases_for_all_dfco_tables(self):
        for stock_base, expected_bases in (
            (
                selector.STOCK_OVER_RUN_HOLD_BASE,
                selector.OVER_RUN_HOLD_BASES,
            ),
            (
                selector.STOCK_OVER_RUN_CUT_BASE,
                selector.OVER_RUN_CUT_BASES,
            ),
            (
                selector.STOCK_OVER_RUN_RESTORE_BASE,
                selector.OVER_RUN_RESTORE_BASES,
            ),
            (
                selector.STOCK_OVER_RUN_INTERMEDIATE_RESTORE_BASE,
                selector.OVER_RUN_INTERMEDIATE_RESTORE_BASES,
            ),
        ):
            with self.subTest(base=hex(stock_base)):
                actual = [
                    selector.select_calibration_base(
                        stock_base, active_index
                    )
                    for active_index in range(selector.SLOT_COUNT)
                ]
                self.assertEqual(actual, list(expected_bases))

    def test_accessor_exposes_all_ten_adapter_backed_families(self):
        adapter_families = [
            family
            for family in selector.LAYOUT.families
            if family.access_kind == "adapter"
        ]
        self.assertEqual(len(adapter_families), 10)
        for family in adapter_families:
            with self.subTest(family=family.key):
                self.assertEqual(
                    tuple(
                        selector.select_calibration_base(
                            family.canonical_address, active_index
                        )
                        for active_index in range(selector.SLOT_COUNT)
                    ),
                    family.all_slot_addresses,
                )

    def test_direct_limiter_bases_are_not_redirected_by_lookup_adapter(self):
        for family_key in (
            "rev_limit_fuel_cut",
            "rev_limit_throttle_cut",
        ):
            family = selector.FAMILIES[family_key]
            with self.subTest(family=family_key):
                self.assertEqual(
                    selector.select_calibration_base(
                        family.canonical_address, 3
                    ),
                    family.canonical_address,
                )

    def test_stock_overrun_calibration_bytes_match_the_exact_rom(self):
        rom = (
            ROOT
            / "rom-images"
            / "23710-JK08A"
            / "1JK08A-20260726-stock.bin"
        ).read_bytes()
        for base, expected in (
            (
                selector.STOCK_OVER_RUN_HOLD_BASE,
                selector.STOCK_OVER_RUN_HOLD_BYTES,
            ),
            (
                selector.STOCK_OVER_RUN_CUT_BASE,
                selector.STOCK_OVER_RUN_CUT_BYTES,
            ),
            (
                selector.STOCK_OVER_RUN_RESTORE_BASE,
                selector.STOCK_OVER_RUN_RESTORE_BYTES,
            ),
            (
                selector.STOCK_OVER_RUN_INTERMEDIATE_RESTORE_BASE,
                selector.STOCK_OVER_RUN_INTERMEDIATE_RESTORE_BYTES,
            ),
        ):
            with self.subTest(base=hex(base)):
                self.assertEqual(rom[base : base + len(expected)], expected)

    def test_diagnostic_mirror_preserves_stock_bits(self):
        self.assertEqual(selector.mirror_active_index(0x24, 0), 0x24)
        self.assertEqual(selector.mirror_active_index(0x24, 1), 0xA4)
        self.assertEqual(selector.mirror_active_index(0x24, 4), 0xA4)
        self.assertEqual(selector.mirror_active_index(0xA4, 0xFF), 0x24)

    def test_visual_confirmation_uses_one_to_five_pulses(self):
        self.assertEqual(
            [
                selector.visual_confirmation_count(active_index)
                for active_index in range(selector.SLOT_COUNT)
            ],
            [1, 2, 3, 4, 5],
        )
        self.assertEqual(selector.visual_confirmation_count(0xFF), 1)

    def test_visual_feedback_queue_uses_one_to_five_pulses(self):
        self.assertEqual(
            [
                selector.queue_visual_feedback(active_index)
                for active_index in range(selector.SLOT_COUNT)
            ],
            [
                selector.FeedbackState(
                    pulses_remaining=count,
                    phase=selector.FeedbackPhase.ON,
                )
                for count in range(1, 6)
            ],
        )
        self.assertEqual(
            selector.queue_visual_feedback(0xFF).pulses_remaining,
            1,
        )

    def test_visual_feedback_replaces_complete_ascd_state(self):
        state = selector.queue_visual_feedback(0)
        state, status = selector.advance_visual_feedback(
            state,
            0xFD,
            on_ticks=1,
            off_ticks=1,
        )
        self.assertEqual(status, 0xCD)
        self.assertEqual(state.phase, selector.FeedbackPhase.OFF)

        state, status = selector.advance_visual_feedback(
            state,
            0xFD,
            on_ticks=1,
            off_ticks=1,
        )
        self.assertEqual(status, 0x8D)
        self.assertEqual(state, selector.FeedbackState())

    def test_visual_feedback_counts_serializer_invocations(self):
        state = selector.queue_visual_feedback(1)
        outputs = []
        for _ in range(8):
            state, status = selector.advance_visual_feedback(
                state,
                0xA1,
                on_ticks=2,
                off_ticks=2,
            )
            outputs.append(status & selector.FEEDBACK_STATUS_MASK)
        self.assertEqual(
            outputs,
            [0x40, 0x40, 0, 0, 0x40, 0x40, 0, 0],
        )
        self.assertEqual(state, selector.FeedbackState())

    def test_idle_or_corrupt_visual_feedback_preserves_stock_status(self):
        for state in (
            selector.FeedbackState(),
            selector.FeedbackState(
                pulses_remaining=6,
                phase=selector.FeedbackPhase.ON,
            ),
            selector.FeedbackState(
                pulses_remaining=1,
                phase=99,
            ),
        ):
            with self.subTest(state=state):
                next_state, status = selector.advance_visual_feedback(
                    state,
                    0xB5,
                    on_ticks=1,
                    off_ticks=1,
                )
                self.assertEqual(next_state, selector.FeedbackState())
                self.assertEqual(status, 0xB5)

    def test_visual_feedback_rejects_invalid_phase_lengths(self):
        with self.assertRaisesRegex(ValueError, "phase lengths"):
            selector.advance_visual_feedback(
                selector.queue_visual_feedback(0),
                0,
                on_ticks=0,
                off_ticks=1,
            )

    def test_zero_feedback_config_is_fail_closed(self):
        state = selector.queue_visual_feedback(4)
        state, status = selector.advance_configured_visual_feedback(
            state, 0xB5, on_ticks=0, off_ticks=0
        )
        self.assertEqual(state, selector.FeedbackState())
        self.assertEqual(status, 0xB5)

    def test_locked_feedback_config_uses_pilot_10x10_counts(self):
        state = selector.queue_visual_feedback(4)
        state, status = selector.advance_configured_visual_feedback(
            state, 0xB5
        )
        self.assertEqual(status, 0xC5)
        self.assertEqual(
            state,
            selector.FeedbackState(
                pulses_remaining=5,
                phase=selector.FeedbackPhase.ON,
                phase_ticks=1,
            ),
        )

    def test_explicit_feedback_config_uses_frame_counts(self):
        state = selector.queue_visual_feedback(0)
        outputs = []
        for _ in range(4):
            state, status = selector.advance_configured_visual_feedback(
                state,
                0xB5,
                on_ticks=2,
                off_ticks=2,
            )
            outputs.append(status)
        self.assertEqual(outputs, [0xC5, 0xC5, 0x85, 0x85])
        self.assertEqual(state, selector.FeedbackState())


class CalibrationRuntimeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layout = map_switching_layout.load_layout()
        cls.image = map_switching_layout.validate_image(cls.layout)
        cls.materialized = map_switching_layout.materialize_calibration_copies(
            cls.layout, cls.image
        )

    def test_startup_runtime_uses_map_1_and_complete_stock_clusters(self):
        runtime = selector.initialize_calibration_runtime(
            self.materialized
        )
        fuel_cut = self.layout.family_by_key["rev_limit_fuel_cut"]
        throttle = self.layout.family_by_key["rev_limit_throttle_cut"]
        self.assertEqual(runtime.active_index, 0)
        self.assertEqual(
            runtime.fuel_cut_shadow,
            self.materialized[
                fuel_cut.stock_container_start :
                fuel_cut.stock_container_start
                + fuel_cut.stock_container_size
            ],
        )
        self.assertEqual(
            runtime.throttle_shadow,
            self.materialized[
                throttle.stock_container_start :
                throttle.stock_container_start
                + throttle.stock_container_size
            ],
        )
        self.assertEqual(runtime.throttle_runtime_scalar, 0x2580)

    def test_prepare_replaces_only_switchable_limiter_bytes(self):
        data = bytearray(self.materialized)
        fuel_cut = self.layout.family_by_key["rev_limit_fuel_cut"]
        throttle = self.layout.family_by_key["rev_limit_throttle_cut"]
        fuel_value = bytes.fromhex("01 02 03 04 05 06 07 08")
        throttle_value = bytes.fromhex("12 34")
        data[
            fuel_cut.copies[0] :
            fuel_cut.copies[0] + fuel_cut.byte_length
        ] = fuel_value
        data[
            throttle.copies[0] :
            throttle.copies[0] + throttle.byte_length
        ] = throttle_value

        prepared = selector.prepare_calibration_commit(data, 1)
        stock_fuel_suffix = self.image.data[
            fuel_cut.canonical_address + fuel_cut.byte_length :
            fuel_cut.stock_container_start + fuel_cut.stock_container_size
        ]
        stock_throttle = bytearray(
            self.image.data[
                throttle.stock_container_start :
                throttle.stock_container_start
                + throttle.stock_container_size
            ]
        )
        stock_throttle[8:10] = throttle_value
        self.assertEqual(
            prepared.fuel_cut_shadow,
            fuel_value + stock_fuel_suffix,
        )
        self.assertEqual(prepared.throttle_shadow, bytes(stock_throttle))
        self.assertEqual(prepared.throttle_runtime_scalar, 0x1234)

    def test_invalid_commit_index_falls_back_to_map_1(self):
        expected = selector.prepare_calibration_commit(
            self.materialized, 0
        )
        for active_index in (-1, 5, 0xFF):
            with self.subTest(active_index=active_index):
                self.assertEqual(
                    selector.prepare_calibration_commit(
                        self.materialized, active_index
                    ),
                    expected,
                )

    def test_publication_rejects_a_scalar_that_differs_from_shadow(self):
        runtime = selector.initialize_calibration_runtime(
            self.materialized
        )
        prepared = selector.prepare_calibration_commit(
            self.materialized, 1
        )
        corrupted = selector.PreparedCalibration(
            active_index=prepared.active_index,
            fuel_cut_shadow=prepared.fuel_cut_shadow,
            throttle_shadow=prepared.throttle_shadow,
            throttle_runtime_scalar=prepared.throttle_runtime_scalar ^ 1,
        )
        with self.assertRaisesRegex(ValueError, "differs from the shadow"):
            selector.publish_calibration_commit(runtime, corrupted)

    def test_selector_decision_keeps_old_index_until_publication(self):
        state = selector.SelectorState(active_index=0)
        state = selector.advance_selector(
            state, selector.RELEASED, selector.SET_COAST
        )
        state = pulse(pulse(state))
        decision = selector.advance_selector_decision(
            state, selector.SET_COAST, selector.RELEASED
        )
        self.assertEqual(decision.state.active_index, 0)
        self.assertEqual(decision.commit_index, 1)

    def test_system_commit_publishes_shadows_and_index_together(self):
        runtime = selector.initialize_calibration_runtime(
            self.materialized
        )
        state = selector.SelectorState()
        state, runtime, committed = selector.advance_calibration_system(
            state,
            runtime,
            self.materialized,
            selector.RELEASED,
            selector.SET_COAST,
        )
        self.assertFalse(committed)
        for _ in range(2):
            state, runtime, committed = selector.advance_calibration_system(
                state,
                runtime,
                self.materialized,
                selector.SET_COAST,
                selector.CANCEL,
            )
            self.assertFalse(committed)
            state, runtime, committed = selector.advance_calibration_system(
                state,
                runtime,
                self.materialized,
                selector.CANCEL,
                selector.SET_COAST,
            )
            self.assertFalse(committed)
        state, runtime, committed = selector.advance_calibration_system(
            state,
            runtime,
            self.materialized,
            selector.SET_COAST,
            selector.RELEASED,
        )
        self.assertTrue(committed)
        self.assertEqual(state.active_index, 1)
        self.assertEqual(runtime.active_index, 1)
        self.assertEqual(
            runtime,
            selector.publish_calibration_commit(
                selector.initialize_calibration_runtime(self.materialized),
                selector.prepare_calibration_commit(
                    self.materialized, 1
                ),
            ),
        )

    def test_divergent_runtime_state_fails_closed_without_input(self):
        runtime = selector.initialize_calibration_runtime(
            self.materialized, 1
        )
        state, runtime, committed = selector.advance_calibration_system(
            selector.SelectorState(active_index=0),
            runtime,
            self.materialized,
            selector.RELEASED,
            selector.SET_COAST,
        )
        self.assertFalse(committed)
        self.assertEqual(state, selector.SelectorState())
        self.assertEqual(runtime.active_index, 0)

    def test_system_queues_feedback_only_after_atomic_commit(self):
        runtime = selector.initialize_calibration_runtime(
            self.materialized
        )
        state = selector.SelectorState()
        feedback = selector.FeedbackState()
        state, runtime, feedback, committed = (
            selector.advance_calibration_system_with_feedback(
                state,
                runtime,
                feedback,
                self.materialized,
                selector.RELEASED,
                selector.SET_COAST,
            )
        )
        self.assertFalse(committed)
        for _ in range(3):
            state, runtime, feedback, committed = (
                selector.advance_calibration_system_with_feedback(
                    state,
                    runtime,
                    feedback,
                    self.materialized,
                    selector.SET_COAST,
                    selector.CANCEL,
                )
            )
            self.assertFalse(committed)
            state, runtime, feedback, committed = (
                selector.advance_calibration_system_with_feedback(
                    state,
                    runtime,
                    feedback,
                    self.materialized,
                    selector.CANCEL,
                    selector.SET_COAST,
                )
            )
            self.assertFalse(committed)
        state, runtime, feedback, committed = (
            selector.advance_calibration_system_with_feedback(
                state,
                runtime,
                feedback,
                self.materialized,
                selector.SET_COAST,
                selector.RELEASED,
            )
        )
        self.assertTrue(committed)
        self.assertEqual(runtime.active_index, 2)
        self.assertEqual(
            feedback,
            selector.FeedbackState(
                pulses_remaining=3,
                phase=selector.FeedbackPhase.ON,
            ),
        )

    def test_active_feedback_blocks_selector_input(self):
        runtime = selector.initialize_calibration_runtime(
            self.materialized, 1
        )
        state, runtime, feedback, committed = (
            selector.advance_calibration_system_with_feedback(
                selector.SelectorState(active_index=1),
                runtime,
                selector.queue_visual_feedback(1),
                self.materialized,
                selector.RELEASED,
                selector.SET_COAST,
            )
        )
        self.assertFalse(committed)
        self.assertEqual(
            state,
            selector.SelectorState(active_index=1),
        )
        self.assertTrue(selector.feedback_active(feedback))

    def test_invalid_runtime_index_clears_active_feedback(self):
        runtime = selector.CalibrationRuntime(
            active_index=0xFF,
            fuel_cut_shadow=b"",
            throttle_shadow=b"",
            throttle_runtime_scalar=0,
        )
        state, runtime, feedback, committed = (
            selector.advance_calibration_system_with_feedback(
                selector.SelectorState(),
                runtime,
                selector.queue_visual_feedback(4),
                self.materialized,
                selector.RELEASED,
                selector.SET_COAST,
            )
        )
        self.assertFalse(committed)
        self.assertEqual(state, selector.SelectorState())
        self.assertEqual(runtime.active_index, 0)
        self.assertEqual(feedback, selector.FeedbackState())


if __name__ == "__main__":
    unittest.main()
