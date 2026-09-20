from types import SimpleNamespace
import unittest

from tools.logs import ignition_surface_audit


def _button(offset_ms, code):
    return SimpleNamespace(
        extended=False,
        remote=False,
        can_id=ignition_surface_audit.ASCD_BUTTON_ID,
        data=bytes((0, 0, 0, code)),
        offset_ms=offset_ms,
    )


class IgnitionSurfaceFormulaTest(unittest.TestCase):
    def test_ignition_finisher_interpolates_low_seven_bits(self):
        calibration = ignition_surface_audit.ExplicitU8Map(
            address=0,
            row_axis=(0, 10),
            column_axis=(0, 10),
            table=((0xC0, 0x46), (0x42, 0x44)),
        )
        self.assertEqual(
            ignition_surface_audit.interpolate_ignition_u8(
                calibration, 5, 5
            ),
            0xC3,
        )
        self.assertEqual(
            ignition_surface_audit.interpolate_ignition_u8(
                calibration, 0, 0
            ),
            0xC0,
        )

    def test_ignition_finisher_takes_flag_from_lower_left_cell(self):
        calibration = ignition_surface_audit.ExplicitU8Map(
            address=0,
            row_axis=(0, 10),
            column_axis=(0, 10),
            table=((0x40, 0xC6), (0xC2, 0xC4)),
        )
        self.assertEqual(
            ignition_surface_audit.interpolate_ignition_u8(
                calibration, 5, 5
            ),
            0x43,
        )

    def test_selector_gestures_recover_one_based_commits(self):
        codes = (
            ignition_surface_audit.RELEASED,
            ignition_surface_audit.SET_COAST,
            ignition_surface_audit.CANCEL,
            ignition_surface_audit.SET_COAST,
            ignition_surface_audit.CANCEL,
            ignition_surface_audit.SET_COAST,
            ignition_surface_audit.RELEASED,
            ignition_surface_audit.SET_COAST,
            ignition_surface_audit.CANCEL,
            ignition_surface_audit.SET_COAST,
            ignition_surface_audit.CANCEL,
            ignition_surface_audit.SET_COAST,
            ignition_surface_audit.CANCEL,
            ignition_surface_audit.SET_COAST,
            ignition_surface_audit.RELEASED,
        )
        trace = SimpleNamespace(
            frames=[_button(index * 10, code) for index, code in enumerate(codes)]
        )
        commits = ignition_surface_audit.detect_map_commits(trace)
        self.assertEqual(
            commits,
            (
                ignition_surface_audit.MapCommit(0.06, 2),
                ignition_surface_audit.MapCommit(0.14, 3),
            ),
        )

    def test_incomplete_or_invalid_selector_gesture_does_not_commit(self):
        trace = SimpleNamespace(
            frames=[
                _button(0, ignition_surface_audit.RELEASED),
                _button(10, ignition_surface_audit.SET_COAST),
                _button(20, ignition_surface_audit.RELEASED),
                _button(30, ignition_surface_audit.SET_COAST),
                _button(40, ignition_surface_audit.CANCEL),
                _button(50, 0x10),
                _button(60, ignition_surface_audit.RELEASED),
            ]
        )
        self.assertEqual(ignition_surface_audit.detect_map_commits(trace), ())

    def test_state_dynamics_separates_quiet_recovery_and_events(self):
        def sample(tick, state, count, map_number=1):
            return ignition_surface_audit.IgnitionSample(
                timestamp=tick / 100,
                run=0,
                tick=tick,
                bfs_raw=0,
                rpm_raw=0,
                state_q8=state,
                surface_state=0,
                knock_count=count,
                knock_channel_mask=0,
                map_number=map_number,
            )

        samples = [
            sample(0, -307, 0),
            sample(1, -294, 0),
            sample(2, -281, 0, 2),
            sample(3, -588, 1, 2),
        ]
        quiet, event, recovery, response, commit = (
            ignition_surface_audit._state_dynamics(samples, 13, 307, 1)
        )
        self.assertEqual(quiet.common_values, ((13, 2),))
        self.assertEqual(event.common_values, ((-307, 1),))
        self.assertEqual(recovery.exact, 2)
        self.assertEqual(response.exact, 1)
        self.assertEqual(commit.common_values, ((13, 1),))

    def test_stock_calibration_binds_exact_constants(self):
        calibration = ignition_surface_audit.load_calibration()
        self.assertEqual(calibration.high_octane_by_slot[0].address, 0x9A1A)
        self.assertEqual(
            calibration.high_detonation_by_slot[0].address, 0x9B1A
        )
        self.assertEqual(calibration.recovery_step_q8, 13)
        self.assertEqual(calibration.event_step_q8, 307)
        self.assertEqual(calibration.forced_state_raw, -5)


if __name__ == "__main__":
    unittest.main()
