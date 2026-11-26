from dataclasses import replace
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
            with self.assertRaises(ValueError):
                cf.CruiseFreeConfig.from_bytes(bytes(bad))
            self.assertIsNone(cf.CruiseFreeConfig.try_from_bytes(bytes(bad)))

        # Unsupported high bits in flags (+5) and feedback_mode (+6).
        for offset in (5, 6):
            for bit in (0x08, 0x10, 0x80):
                bad = bytearray(raw)
                bad[offset] |= bit
                with self.assertRaises(ValueError):
                    cf.CruiseFreeConfig.from_bytes(bytes(bad))
                self.assertIsNone(cf.CruiseFreeConfig.try_from_bytes(bytes(bad)))

        # Zero debounce (+0x15) rejected.
        bad = bytearray(raw)
        bad[0x15] = 0
        with self.assertRaises(ValueError):
            cf.CruiseFreeConfig.from_bytes(bytes(bad))
        self.assertIsNone(cf.CruiseFreeConfig.try_from_bytes(bytes(bad)))

        # APP ordering boundaries: min <= release < press <= min(app1_max, app2_max).
        for kwargs in (
            {"app_min_valid": 261, "app_release_max": 260},
            {"app_release_max": 700, "app_press_min": 700},
            {"app_press_min": 965, "app1_max_valid": 964},
            {"app_press_min": 1001, "app2_max_valid": 1000},
        ):
            bad_cfg = replace(cf.DEFAULT_CONFIG, **kwargs)
            self.assertFalse(bad_cfg.is_valid())
            with self.assertRaises(ValueError):
                bad_cfg.validate()

        # Valid boundary equalities and unsigned 16-bit halfwords > 0x7FFF.
        hi_cfg = cf.CruiseFreeConfig(
            flags=0,
            feedback_mode=0,
            age_limit_ticks=0xFE,
            app_min_valid=0x8000,
            app1_max_valid=0xFFFE,
            app2_max_valid=0xFFFF,
            app_diff_max=0xFFFF,
            app_release_max=0x8000,
            app_press_min=0x8001,
            tach_hold_frames=0,
            debounce_ticks=1,
        )
        self.assertEqual(cf.CruiseFreeConfig.from_bytes(hi_cfg.to_bytes()), hi_cfg)

    def test_age_limit_unsigned_boundaries_in_decoder_selector_and_tach(self):
        raw = bytearray(cf.DEFAULT_CONFIG.to_bytes())
        for bad_age in (0x00, 0xFF):
            raw[7] = bad_age
            with self.assertRaises(ValueError):
                cf.CruiseFreeConfig.from_bytes(bytes(raw))
            self.assertIsNone(cf.CruiseFreeConfig.try_from_bytes(bytes(raw)))

        for limit in (0x01, 0x03, 0x7F, 0x80, 0xFE):
            cfg = cf.CruiseFreeConfig(
                flags=(
                    cf.FLAG_ASCD_ENABLED
                    | cf.FLAG_CRUISE_FREE_ENABLED
                    | cf.FLAG_TACH_ALLOWED
                ),
                feedback_mode=cf.FEEDBACK_CRUISE | cf.FEEDBACK_TACH,
                age_limit_ticks=limit,
                debounce_ticks=1,
            )
            encoded = cfg.to_bytes()
            self.assertEqual(encoded[7], limit)
            self.assertEqual(cf.CruiseFreeConfig.from_bytes(encoded), cfg)

            for age, expect_ok in ((limit - 1, True), (limit, True), (limit + 1, False)):
                st = cf.StationaryState(
                    flags=cf.STATIONARY_OBSERVED_BIT | cf.STATIONARY_VALID_BIT,
                    age=age,
                    last_raw_speed=0,
                )
                dec = cf.advance_cruise_free(
                    cf.CruiseFreeState(phase=cf.CruiseFreePhase.ARMED_RELEASED),
                    active_index=0,
                    stationary=st,
                    port_ready=True,
                    hcan1_ready=True,
                    rpm_fine=0,
                    rpm_coarse=0,
                    brake_held=True,
                    app1=800,
                    app2=800,
                    config=cfg,
                )
                if expect_ok:
                    self.assertEqual(dec.commit_index, 1)
                else:
                    self.assertIsNone(dec.commit_index)
                    self.assertEqual(
                        dec.state.last_reason, cf.BlockReason.NOT_STATIONARY
                    )

                armed_tach = cf.CruiseFreeState(tach_ticks=5, tach_slot=2)
                wire, next_st = cf.tach_wire_word(
                    armed_tach,
                    stationary=st,
                    port_ready=True,
                    hcan1_ready=True,
                    rpm_fine=0,
                    rpm_coarse=0,
                    config=cfg,
                )
                ticked = cf.tick_tach_countdown(
                    armed_tach,
                    stationary=st,
                    port_ready=True,
                    hcan1_ready=True,
                    rpm_fine=0,
                    rpm_coarse=0,
                    config=cfg,
                )
                if expect_ok:
                    self.assertEqual(wire, 2 * cf.TACH_WIRE_PER_SLOT)
                    self.assertEqual(next_st, armed_tach)
                    self.assertEqual(ticked.tach_ticks, 4)
                    self.assertEqual(ticked.tach_slot, 2)
                else:
                    self.assertIsNone(wire)
                    self.assertEqual((next_st.tach_ticks, next_st.tach_slot), (0, 0))
                    self.assertEqual((ticked.tach_ticks, ticked.tach_slot), (0, 0))

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
        self.assertEqual(st.age, 0xFF)

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

        # Gate drop clears observed completely, even with a fresh zero frame.
        for port_ready, hcan1_ready in ((False, True), (True, False)):
            seeded = cf.StationaryState(
                flags=cf.STATIONARY_OBSERVED_BIT | cf.STATIONARY_VALID_BIT,
                age=0,
                last_raw_speed=0,
            )
            st = cf.advance_stationary(
                seeded, port_ready=port_ready, hcan1_ready=hcan1_ready,
                new_frame=True, raw_speed=0, config=cfg,
            )
            self.assertEqual(st, cf.StationaryState())

        # Invalid or missing config resets observation before latching a frame.
        bad_cfg = replace(cf.DEFAULT_CONFIG, age_limit_ticks=0xFF)
        for bad in (None, bad_cfg):
            for new_frame in (False, True):
                seeded = cf.StationaryState(
                    flags=cf.STATIONARY_OBSERVED_BIT | cf.STATIONARY_VALID_BIT,
                    age=0,
                    last_raw_speed=0,
                )
                reset = cf.advance_stationary(
                    seeded, port_ready=True, hcan1_ready=True,
                    new_frame=new_frame, raw_speed=0, config=bad,
                )
                self.assertEqual(reset, cf.StationaryState())

        # After reset, restoring valid config does not re-validate without a fresh frame.
        st = cf.advance_stationary(
            cf.StationaryState(), port_ready=True, hcan1_ready=True,
            new_frame=False, raw_speed=0, config=cfg,
        )
        self.assertFalse(st.valid)
        st = cf.advance_stationary(
            st, port_ready=True, hcan1_ready=True,
            new_frame=True, raw_speed=0, config=cfg,
        )
        self.assertTrue(st.valid)

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
                state, stationary=stationary, port_ready=True, hcan1_ready=True,
                rpm_fine=0, rpm_coarse=0, config=cfg,
            )
            self.assertEqual(wire, (expected_next + 1) * 0x1F40)

        # Cranking (RPM != 0) immediately cancels tach override.
        wire, state = cf.tach_wire_word(
            state, stationary=stationary, port_ready=True, hcan1_ready=True,
            rpm_fine=10, rpm_coarse=0, config=cfg,
        )
        self.assertIsNone(wire)
        self.assertEqual(state.tach_ticks, 0)
        self.assertEqual(state.tach_slot, 0)

    def test_precondition_blocks_and_invalid_config_resets(self):
        cfg = cf.DEFAULT_CONFIG
        stationary = cf.StationaryState(
            flags=cf.STATIONARY_OBSERVED_BIT | cf.STATIONARY_VALID_BIT,
            age=0,
            last_raw_speed=0,
        )
        armed = cf.CruiseFreeState(
            phase=cf.CruiseFreePhase.ARMED_RELEASED,
            debounce=1,
            tach_ticks=12,
            tach_slot=3,
            active_source=2,
        )

        # Invalid config clears phase, debounce, and tach pair even if RPM != 0.
        for bad in (None, replace(cfg, age_limit_ticks=0)):
            dec = cf.advance_cruise_free(
                armed, active_index=0, stationary=stationary,
                port_ready=True, hcan1_ready=True, rpm_fine=500, rpm_coarse=10,
                brake_held=True, app1=800, app2=800, config=bad,
            )
            self.assertIsNone(dec.commit_index)
            self.assertEqual(dec.state.last_reason, cf.BlockReason.CONFIG_DISABLED_OR_INVALID)
            self.assertEqual(dec.state.phase, cf.CruiseFreePhase.IDLE_WAIT_RELEASE)
            self.assertEqual(dec.state.debounce, 0)
            self.assertEqual((dec.state.tach_ticks, dec.state.tach_slot), (0, 0))
            self.assertEqual(dec.state.active_source, 2)

        # Valid config with cruise_free disabled preserves tach pair.
        dis_cfg = replace(cfg, flags=cf.FLAG_ASCD_ENABLED)
        dec = cf.advance_cruise_free(
            armed, active_index=0, stationary=stationary,
            port_ready=True, hcan1_ready=True, rpm_fine=0, rpm_coarse=0,
            brake_held=True, app1=800, app2=800, config=dis_cfg,
        )
        self.assertEqual(dec.state.last_reason, cf.BlockReason.CONFIG_DISABLED_OR_INVALID)
        self.assertEqual((dec.state.tach_ticks, dec.state.tach_slot), (12, 3))

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

    def test_tach_live_veto_matrix_and_countdown_lifecycle(self):
        cfg = cf.CruiseFreeConfig(
            flags=cf.FLAG_ASCD_ENABLED | cf.FLAG_CRUISE_FREE_ENABLED | cf.FLAG_TACH_ALLOWED,
            feedback_mode=cf.FEEDBACK_CRUISE | cf.FEEDBACK_TACH,
            age_limit_ticks=3,
        )
        valid_st = cf.StationaryState(
            flags=cf.STATIONARY_OBSERVED_BIT | cf.STATIONARY_VALID_BIT,
            age=2,
            last_raw_speed=0,
        )
        armed = cf.CruiseFreeState(
            phase=cf.CruiseFreePhase.PRESSED_LATCHED,
            debounce=1,
            tach_ticks=5,
            tach_slot=4,
            last_reason=cf.BlockReason.BRAKE_RELEASED,
            active_source=2,
        )

        veto_cases = [
            {"port_ready": False},
            {"hcan1_ready": False},
            {"stationary": replace(valid_st, flags=cf.STATIONARY_OBSERVED_BIT)},
            {"stationary": replace(valid_st, flags=cf.STATIONARY_VALID_BIT)},
            {"stationary": replace(valid_st, last_raw_speed=1)},
            {"stationary": replace(valid_st, last_raw_speed=0xFFFF)},
            {"stationary": replace(valid_st, age=4)},
            {"rpm_fine": 1},
            {"rpm_coarse": 0x0100},
            {"config": replace(cfg, flags=cf.FLAG_ASCD_ENABLED | cf.FLAG_CRUISE_FREE_ENABLED)},
            {"config": replace(cfg, feedback_mode=cf.FEEDBACK_CRUISE)},
            {"state": replace(armed, tach_ticks=0)},
            {"state": replace(armed, tach_slot=0)},
            {"state": replace(armed, tach_slot=6)},
            {"state": replace(armed, tach_slot=0xFF)},
        ]
        for overrides in veto_cases:
            kwargs = {
                "stationary": valid_st,
                "port_ready": True,
                "hcan1_ready": True,
                "rpm_fine": 0,
                "rpm_coarse": 0,
                "config": cfg,
            }
            st_in = overrides.get("state", armed)
            for k, v in overrides.items():
                if k != "state":
                    kwargs[k] = v
            wire, out = cf.tach_wire_word(st_in, **kwargs)
            self.assertIsNone(wire)
            self.assertEqual((out.tach_ticks, out.tach_slot), (0, 0))
            self.assertEqual(out.phase, st_in.phase)
            self.assertEqual(out.active_source, st_in.active_source)
            ticked = cf.tick_tach_countdown(st_in, **kwargs)
            self.assertEqual((ticked.tach_ticks, ticked.tach_slot), (0, 0))

        # Invalid config clears gesture and tach even when tach_ticks == 0.
        for bad in (None, replace(cfg, age_limit_ticks=0xFF)):
            for ticks in (5, 0):
                st_in = replace(armed, tach_ticks=ticks)
                wire, out = cf.tach_wire_word(
                    st_in, stationary=valid_st, port_ready=True, hcan1_ready=True,
                    rpm_fine=0, rpm_coarse=0, config=bad,
                )
                self.assertIsNone(wire)
                self.assertEqual(
                    (out.phase, out.debounce, out.tach_ticks, out.tach_slot),
                    (cf.CruiseFreePhase.IDLE_WAIT_RELEASE, 0, 0, 0),
                )
                ticked = cf.tick_tach_countdown(
                    st_in, stationary=valid_st, port_ready=True, hcan1_ready=True,
                    rpm_fine=0, rpm_coarse=0, config=bad,
                )
                self.assertEqual(
                    (ticked.phase, ticked.debounce, ticked.tach_ticks, ticked.tach_slot),
                    (cf.CruiseFreePhase.IDLE_WAIT_RELEASE, 0, 0, 0),
                )

        # Countdown lifecycle 2 -> 1 -> 0; repeated TX does not decrement ticks.
        st_run = cf.CruiseFreeState(tach_ticks=2, tach_slot=3)
        wire, st_run = cf.tach_wire_word(
            st_run, stationary=valid_st, port_ready=True, hcan1_ready=True,
            rpm_fine=0, rpm_coarse=0, config=cfg,
        )
        self.assertEqual(wire, 3 * cf.TACH_WIRE_PER_SLOT)
        self.assertEqual(st_run.tach_ticks, 2)
        st_run = cf.tick_tach_countdown(
            st_run, stationary=valid_st, port_ready=True, hcan1_ready=True,
            rpm_fine=0, rpm_coarse=0, config=cfg,
        )
        self.assertEqual((st_run.tach_ticks, st_run.tach_slot), (1, 3))
        st_run = cf.tick_tach_countdown(
            st_run, stationary=valid_st, port_ready=True, hcan1_ready=True,
            rpm_fine=0, rpm_coarse=0, config=cfg,
        )
        self.assertEqual((st_run.tach_ticks, st_run.tach_slot), (0, 0))

    def test_runtime_invalid_config_wipes_both_stationary_and_selector_across_handlers(self):
        cfg = cf.CruiseFreeConfig(
            flags=cf.FLAG_ASCD_ENABLED | cf.FLAG_CRUISE_FREE_ENABLED | cf.FLAG_TACH_ALLOWED,
            feedback_mode=cf.FEEDBACK_CRUISE | cf.FEEDBACK_TACH,
            age_limit_ticks=3,
            debounce_ticks=1,
        )
        bad_cfg = replace(cfg, age_limit_ticks=0xFF)
        seeded = cf.CruiseFreeRuntime(
            stationary=cf.StationaryState(
                flags=cf.STATIONARY_OBSERVED_BIT | cf.STATIONARY_VALID_BIT,
                age=0,
                last_raw_speed=0,
            ),
            selector=cf.CruiseFreeState(
                phase=cf.CruiseFreePhase.ARMED_RELEASED,
                debounce=1,
                tach_ticks=10,
                tach_slot=3,
                active_source=2,
            ),
        )

        # Invalid MSCF in RX, selector, TX, or countdown wipes CF[0..7] completely;
        # restoring valid MSCF without a fresh CAN 0x284 zero frame must stay blocked.
        for handler in ("rx", "selector", "tx", "countdown"):
            if handler == "rx":
                after = seeded.step_stationary(
                    port_ready=True, hcan1_ready=True, new_frame=True,
                    raw_speed=0, config=bad_cfg,
                )
            elif handler == "selector":
                after, commit = seeded.step_selector(
                    active_index=0, port_ready=True, hcan1_ready=True,
                    rpm_fine=0, rpm_coarse=0, brake_held=True,
                    app1=800, app2=800, config=bad_cfg,
                )
                self.assertIsNone(commit)
                self.assertEqual(
                    after.selector.last_reason,
                    cf.BlockReason.CONFIG_DISABLED_OR_INVALID,
                )
            elif handler == "tx":
                wire, after = seeded.step_tach_wire(
                    port_ready=True, hcan1_ready=True, rpm_fine=0, rpm_coarse=0,
                    config=bad_cfg,
                )
                self.assertIsNone(wire)
            else:
                after = seeded.step_tach_countdown(
                    port_ready=True, hcan1_ready=True, rpm_fine=0, rpm_coarse=0,
                    config=bad_cfg,
                )

            self.assertEqual(after.stationary, cf.StationaryState())
            self.assertEqual(
                (
                    after.selector.phase,
                    after.selector.debounce,
                    after.selector.tach_ticks,
                    after.selector.tach_slot,
                    after.selector.active_source,
                ),
                (cf.CruiseFreePhase.IDLE_WAIT_RELEASE, 0, 0, 0, 2),
            )

            # Restored valid config without a new zero frame stays non-stationary.
            re_armed = cf.CruiseFreeRuntime(
                stationary=after.stationary,
                selector=replace(
                    after.selector,
                    phase=cf.CruiseFreePhase.ARMED_RELEASED,
                    tach_ticks=5,
                    tach_slot=2,
                ),
            )
            after_sel, commit = re_armed.step_selector(
                active_index=0, port_ready=True, hcan1_ready=True,
                rpm_fine=0, rpm_coarse=0, brake_held=True,
                app1=800, app2=800, config=cfg,
            )
            self.assertIsNone(commit)
            self.assertEqual(
                after_sel.selector.last_reason, cf.BlockReason.NOT_STATIONARY
            )
            wire, after_tx = re_armed.step_tach_wire(
                port_ready=True, hcan1_ready=True, rpm_fine=0, rpm_coarse=0,
                config=cfg,
            )
            self.assertIsNone(wire)
            self.assertEqual((after_tx.selector.tach_ticks, after_tx.selector.tach_slot), (0, 0))

            # Fresh zero-speed frame re-establishes stationary validity.
            recovered = after.step_stationary(
                port_ready=True, hcan1_ready=True, new_frame=True,
                raw_speed=0, config=cfg,
            )
            self.assertTrue(recovered.stationary.valid)


if __name__ == "__main__":
    unittest.main()
