import unittest

from patches import map_switching_cruise_free as cf


class CruiseFreeModelTest(unittest.TestCase):
    def test_config_round_trip_and_corruption_rejected(self):
        raw = cf.DEFAULT_CONFIG.to_bytes()
        self.assertEqual(len(raw), cf.CONFIG_SIZE)
        parsed = cf.CruiseFreeConfig.from_bytes(raw)
        self.assertEqual(parsed, cf.DEFAULT_CONFIG)

        for offset in (0, 4, 22, 24, 28, 31):
            bad = bytearray(raw)
            bad[offset] ^= 0x01
            self.assertIsNone(cf.CruiseFreeConfig.try_from_bytes(bytes(bad)))

    def test_stationary_contract_freshness_sentinel_and_gate_reset(self):
        cfg = cf.DEFAULT_CONFIG
        st = cf.StationaryState()
        self.assertFalse(st.observed)
        self.assertFalse(st.valid)

        # No frame yet, gates on: stays unobserved and invalid.
        st = cf.advance_stationary(
            st, port_ready=True, hcan1_ready=True, new_frame=False,
            raw_speed=0, config=cfg,
        )
        self.assertFalse(st.observed)
        self.assertFalse(st.valid)

        # First valid zero-speed frame sets observed and valid, age=0.
        st = cf.advance_stationary(
            st, port_ready=True, hcan1_ready=True, new_frame=True,
            raw_speed=0, config=cfg,
        )
        self.assertTrue(st.valid)
        self.assertEqual(st.age, 0)

        # Ages 1, 2, 3 remain valid (<= 30.72 ms).
        for expected_age in (1, 2, 3):
            st = cf.advance_stationary(
                st, port_ready=True, hcan1_ready=True, new_frame=False,
                raw_speed=0, config=cfg,
            )
            self.assertTrue(st.valid)
            self.assertEqual(st.age, expected_age)

        # Age 4 expires stationary while keeping observed.
        st = cf.advance_stationary(
            st, port_ready=True, hcan1_ready=True, new_frame=False,
            raw_speed=0, config=cfg,
        )
        self.assertTrue(st.observed)
        self.assertFalse(st.valid)
        self.assertEqual(st.age, 4)

        # Wire sentinel 0xFFFF clears stationary immediately.
        st = cf.advance_stationary(
            st, port_ready=True, hcan1_ready=True, new_frame=True,
            raw_speed=0xFFFF, config=cfg,
        )
        self.assertTrue(st.observed)
        self.assertFalse(st.valid)
        self.assertEqual(st.last_raw_speed, 0xFFFF)

        # Gate drop clears observed completely.
        st = cf.advance_stationary(
            st, port_ready=False, hcan1_ready=True, new_frame=False,
            raw_speed=0, config=cfg,
        )
        self.assertFalse(st.observed)
        self.assertFalse(st.valid)
        self.assertEqual(st.age, 0xFF)

    def test_cyclic_selector_full_wrap_and_preconditions(self):
        cfg = cf.CruiseFreeConfig(
            flags=cf.FLAG_ASCD_ENABLED | cf.FLAG_CRUISE_FREE_ENABLED | cf.FLAG_TACH_ALLOWED,
            feedback_mode=cf.FEEDBACK_MIL | cf.FEEDBACK_TACH,
            tach_hold_frames=40,
            debounce_ticks=2,
        )
        stationary = cf.StationaryState(
            flags=cf.STATIONARY_OBSERVED_BIT | cf.STATIONARY_VALID_BIT,
            age=1,
            last_raw_speed=0,
        )
        state = cf.CruiseFreeState()
        active = 0

        # Pressing pedal before releasing does NOT arm or commit.
        for _ in range(3):
            dec = cf.advance_cruise_free(
                state, active_index=active, stationary=stationary,
                port_ready=True, hcan1_ready=True, rpm_fine=0, rpm_coarse=0,
                brake_held=True, app1=850, app2=850, config=cfg,
            )
            state = dec.state
            self.assertIsNone(dec.commit_index)
            self.assertEqual(state.phase, cf.CruiseFreePhase.IDLE_WAIT_RELEASE)

        # Cycle through all 5 slots: 0 -> 1 -> 2 -> 3 -> 4 -> 0.
        for expected_next in (1, 2, 3, 4, 0):
            # 2 released ticks arm/re-arm.
            for _ in range(2):
                dec = cf.advance_cruise_free(
                    state, active_index=active, stationary=stationary,
                    port_ready=True, hcan1_ready=True, rpm_fine=0, rpm_coarse=0,
                    brake_held=True, app1=150, app2=150, config=cfg,
                )
                state = dec.state
                self.assertIsNone(dec.commit_index)
            self.assertEqual(state.phase, cf.CruiseFreePhase.ARMED_RELEASED)

            # Deadband spike resets debounce but keeps ARMED_RELEASED.
            dec = cf.advance_cruise_free(
                state, active_index=active, stationary=stationary,
                port_ready=True, hcan1_ready=True, rpm_fine=0, rpm_coarse=0,
                brake_held=True, app1=750, app2=750, config=cfg,
            )
            state = dec.state
            self.assertEqual(state.debounce, 1)
            dec = cf.advance_cruise_free(
                state, active_index=active, stationary=stationary,
                port_ready=True, hcan1_ready=True, rpm_fine=0, rpm_coarse=0,
                brake_held=True, app1=450, app2=450, config=cfg,
            )
            state = dec.state
            self.assertEqual(state.debounce, 0)
            self.assertEqual(state.phase, cf.CruiseFreePhase.ARMED_RELEASED)

            # Two consecutive pressed ticks commit cyclic next slot.
            dec1 = cf.advance_cruise_free(
                state, active_index=active, stationary=stationary,
                port_ready=True, hcan1_ready=True, rpm_fine=0, rpm_coarse=0,
                brake_held=True, app1=820, app2=815, config=cfg,
            )
            self.assertIsNone(dec1.commit_index)
            dec2 = cf.advance_cruise_free(
                dec1.state, active_index=active, stationary=stationary,
                port_ready=True, hcan1_ready=True, rpm_fine=0, rpm_coarse=0,
                brake_held=True, app1=830, app2=825, config=cfg,
            )
            self.assertEqual(dec2.commit_index, expected_next)
            state = dec2.state
            active = expected_next
            self.assertEqual(state.phase, cf.CruiseFreePhase.PRESSED_LATCHED)
            self.assertEqual(state.tach_slot, expected_next + 1)
            self.assertEqual(state.tach_ticks, 40)

            wire, state = cf.tach_wire_word(
                state, stationary=stationary, rpm_fine=0, rpm_coarse=0, config=cfg,
            )
            self.assertEqual(wire, (expected_next + 1) * 0x1F40)

        # Cranking (RPM != 0) immediately cancels tach override.
        wire, state = cf.tach_wire_word(
            state, stationary=stationary, rpm_fine=10, rpm_coarse=0, config=cfg,
        )
        self.assertIsNone(wire)
        self.assertEqual(state.tach_ticks, 0)
        self.assertEqual(state.tach_slot, 0)

    def test_precondition_blocks_record_reasons(self):
        cfg = cf.DEFAULT_CONFIG
        stationary = cf.StationaryState(
            flags=cf.STATIONARY_OBSERVED_BIT | cf.STATIONARY_VALID_BIT,
            age=0,
            last_raw_speed=0,
        )
        armed = cf.CruiseFreeState(phase=cf.CruiseFreePhase.ARMED_RELEASED)

        # Engine running
        dec = cf.advance_cruise_free(
            armed, active_index=0, stationary=stationary,
            port_ready=True, hcan1_ready=True, rpm_fine=1, rpm_coarse=0,
            brake_held=True, app1=800, app2=800, config=cfg,
        )
        self.assertEqual(dec.state.last_reason, cf.BlockReason.ENGINE_RUNNING)
        self.assertEqual(dec.state.phase, cf.CruiseFreePhase.IDLE_WAIT_RELEASE)

        # Dual APP disagreement > 60
        dec = cf.advance_cruise_free(
            armed, active_index=0, stationary=stationary,
            port_ready=True, hcan1_ready=True, rpm_fine=0, rpm_coarse=0,
            brake_held=True, app1=800, app2=700, config=cfg,
        )
        self.assertEqual(dec.state.last_reason, cf.BlockReason.PEDAL_IMPLAUSIBLE)


if __name__ == "__main__":
    unittest.main()
