from dataclasses import replace
import unittest

from patches import map_switching_cruise_free as cf


STATIONARY = cf.StationaryState(
    flags=cf.STATIONARY_OBSERVED_BIT | cf.STATIONARY_VALID_BIT,
    age=0,
    last_raw_speed=0,
)
MOVING = cf.StationaryState(
    flags=cf.STATIONARY_OBSERVED_BIT,
    age=0,
    last_raw_speed=1,
)


def menu_step(state, **overrides):
    inputs = dict(
        active_index=0,
        current_code=cf.BUTTON_CANCEL,
        previous_code=cf.BUTTON_CANCEL,
        feedback_active=False,
        stationary=STATIONARY,
        port_ready=True,
        hcan1_ready=True,
        app1=151,
        app2=151,
        config=cf.DEFAULT_CONFIG,
    )
    inputs.update(overrides)
    return cf.advance_stationary_menu(state, **inputs)


def brake_app_step(state, *, app=151, **overrides):
    inputs = dict(
        active_index=0,
        stationary=STATIONARY,
        port_ready=True,
        hcan1_ready=True,
        rpm_fine=0,
        rpm_coarse=0,
        brake_held=True,
        app1=app,
        app2=app,
        config=cf.DEFAULT_CONFIG,
    )
    inputs.update(overrides)
    return cf.advance_cruise_free(state, **inputs)


def tach_step(state, **overrides):
    inputs = dict(
        stationary=STATIONARY,
        port_ready=True,
        hcan1_ready=True,
        rpm_fine=0,
        rpm_coarse=0,
        config=cf.DEFAULT_CONFIG,
    )
    inputs.update(overrides)
    return cf.tach_wire_word(state, **inputs)


class CruiseFreeModelTest(unittest.TestCase):
    def test_mscf_v2_default_record(self):
        self.assertEqual(
            (
                cf.FLAG_ASCD_ENABLED,
                cf.FLAG_CRUISE_FREE_ENABLED,
                cf.FLAG_TACH_ALLOWED,
                cf.FLAG_MIL_ENABLED,
            ),
            (0x01, 0x02, 0x04, 0x08),
        )
        raw = bytes.fromhex(
            "4d534346 02 0f 14 03 003c 03c4 03e8 003c 0104 02bc 024a 02 "
            "00 00000000 a55a5aa5"
        )
        self.assertEqual(len(raw), 32)
        self.assertEqual(cf.DEFAULT_CONFIG_BYTES, raw)
        self.assertEqual(cf.DEFAULT_CONFIG.to_bytes(), raw)
        parsed = cf.CruiseFreeConfig.from_bytes(raw)
        self.assertEqual(parsed, cf.DEFAULT_CONFIG)
        self.assertEqual(parsed.flags, 0x0F)
        self.assertEqual(parsed.cancel_hold_ticks, 20)
        self.assertEqual(parsed.menu_timeout_ticks, 586)
        self.assertEqual(parsed.debounce_ticks, 2)

    def test_mscf_v2_rejects_invalid_records(self):
        raw = cf.DEFAULT_CONFIG_BYTES
        invalid_fields = (
            (0x00, b"BAD!"),
            (0x04, b"\x01"),
            (0x05, b"\x1f"),
            (0x05, b"\x8f"),
            (0x06, b"\x00"),
            (0x07, b"\x00"),
            (0x07, b"\xff"),
            (0x14, b"\x00\x00"),
            (0x16, b"\x00"),
            (0x17, b"\x01"),
            (0x18, b"\x00\x00\x00\x01"),
            (0x1C, b"\x00\x00\x00\x00"),
        )
        for offset, field in invalid_fields:
            with self.subTest(offset=offset, field=field):
                bad = raw[:offset] + field + raw[offset + len(field):]
                with self.assertRaises(ValueError):
                    cf.CruiseFreeConfig.from_bytes(bad)
                self.assertIsNone(cf.CruiseFreeConfig.try_from_bytes(bad))
        for bad in (raw[:-1], raw + b"\x00"):
            self.assertIsNone(cf.CruiseFreeConfig.try_from_bytes(bad))

    def test_mscf_v2_app_order_and_unsigned_boundaries(self):
        for overrides in (
            {"app_min_valid": 261},
            {"app_release_max": 700},
            {"app_press_min": 965},
            {"app1_max_valid": 1000, "app2_max_valid": 699},
        ):
            with self.subTest(**overrides):
                bad = replace(cf.DEFAULT_CONFIG, **overrides)
                self.assertFalse(bad.is_valid())
                with self.assertRaises(ValueError):
                    bad.to_bytes()

        config = cf.CruiseFreeConfig(
            flags=0,
            cancel_hold_ticks=255,
            age_limit_ticks=254,
            app_min_valid=0x8000,
            app1_max_valid=0xFFFE,
            app2_max_valid=0xFFFF,
            app_diff_max=0xFFFF,
            app_release_max=0x8000,
            app_press_min=0x8001,
            menu_timeout_ticks=0xFFFF,
            debounce_ticks=1,
        )
        self.assertEqual(cf.CruiseFreeConfig.from_bytes(config.to_bytes()), config)

    def test_stationary_requires_fresh_zero_speed_and_ready_receiver(self):
        runtime = cf.CruiseFreeRuntime()

        def receive(runtime, *, raw_speed=0, new_frame=True, **overrides):
            inputs = dict(port_ready=True, hcan1_ready=True, config=cf.DEFAULT_CONFIG)
            inputs.update(overrides)
            return runtime.step_stationary(
                raw_speed=raw_speed, new_frame=new_frame, **inputs
            )

        self.assertEqual(receive(runtime, new_frame=False), runtime)
        runtime = receive(runtime)
        self.assertEqual(runtime.stationary, STATIONARY)

        for age in range(1, 5):
            runtime = receive(runtime, new_frame=False)
            self.assertEqual(runtime.stationary.age, age)
            self.assertTrue(runtime.stationary.observed)
            self.assertEqual(runtime.stationary.valid, age <= 3)

        for raw_speed in (1, 0xFFFF):
            with self.subTest(raw_speed=raw_speed):
                runtime = receive(receive(runtime), raw_speed=raw_speed)
                self.assertTrue(runtime.stationary.observed)
                self.assertFalse(runtime.stationary.valid)
                self.assertEqual(runtime.stationary.last_raw_speed, raw_speed)
                self.assertEqual(runtime.stationary.age, 0)

        runtime = receive(runtime)
        for overrides in ({"port_ready": False}, {"hcan1_ready": False}):
            with self.subTest(**overrides):
                reset = receive(runtime, **overrides)
                self.assertEqual(reset.stationary, cf.StationaryState())
                self.assertFalse(receive(reset, new_frame=False).stationary.valid)
                self.assertTrue(receive(reset).stationary.valid)

    def test_stationary_age_boundary_with_unsigned_limits(self):
        active = cf.CruiseFreeState(
            phase=cf.CruiseFreePhase.ACTIVE_PRESSED,
            selected_slot=2,
            tach_mode=cf.TachMode.BRAKE_APP_RPM0,
            tach_slot=2,
        )
        for limit in (1, 3, 0x7F, 0x80, 0xFE):
            config = replace(cf.DEFAULT_CONFIG, age_limit_ticks=limit)
            self.assertEqual(config.to_bytes()[0x07], limit)
            for age in (limit - 1, limit, limit + 1):
                with self.subTest(limit=limit, age=age):
                    stationary = replace(STATIONARY, age=age)
                    decision = brake_app_step(
                        active, brake_held=False, stationary=stationary, config=config
                    )
                    wire, _ = tach_step(active, stationary=stationary, config=config)
                    if age <= limit:
                        self.assertEqual(decision.commit_index, 1)
                        self.assertEqual(wire, 2 * 0x1F40)
                    else:
                        self.assertIsNone(decision.commit_index)
                        self.assertEqual(
                            decision.state.last_reason, cf.BlockReason.NOT_STATIONARY
                        )
                        self.assertIsNone(wire)

    def test_stationary_menu_cancel_hold_opens_at_active_map(self):
        state = cf.CruiseFreeState()
        for ticks in range(1, 20):
            decision = menu_step(state, active_index=3)
            state = decision.state
            self.assertEqual(decision.route, 1)
            self.assertIsNone(decision.commit_index)
            self.assertEqual(decision.mil_pulses, 0)
            self.assertEqual(state.menu_phase, cf.MenuPhase.HOLDING_CANCEL)
            self.assertEqual(state.menu_timer, ticks)
            self.assertEqual(state.tach_mode, cf.TachMode.OFF)

        entered = menu_step(state, active_index=3)
        self.assertEqual(entered.route, 1)
        self.assertIsNone(entered.commit_index)
        self.assertEqual(entered.mil_pulses, 1)
        self.assertEqual(
            entered.state,
            cf.CruiseFreeState(
                menu_phase=cf.MenuPhase.ACTIVE,
                menu_slot=4,
                tach_mode=cf.TachMode.STATIONARY_MENU,
                tach_slot=4,
            ),
        )
        held = menu_step(entered.state)
        self.assertIsNone(held.commit_index)
        self.assertEqual(held.mil_pulses, 0)
        self.assertEqual(held.state.menu_slot, 4)

    def test_stationary_menu_entry_arbitration_and_interrupted_hold(self):
        idle = cf.CruiseFreeState()
        for overrides, route in (
            ({"stationary": MOVING}, 0),
            ({"feedback_active": True}, 2),
            ({"app1": 261}, 2),
            ({"current_code": cf.BUTTON_RES}, 2),
        ):
            with self.subTest(**overrides):
                decision = menu_step(idle, **overrides)
                self.assertEqual(decision.route, route)
                self.assertEqual(decision.state, idle)
                self.assertIsNone(decision.commit_index)

        brake_active = replace(
            idle, phase=cf.CruiseFreePhase.ACTIVE_RELEASED, selected_slot=2
        )
        self.assertEqual(menu_step(brake_active).route, 2)
        self.assertEqual(menu_step(brake_active).state, brake_active)

        holding = menu_step(idle).state
        for overrides, route in (
            ({"current_code": cf.BUTTON_RELEASED}, 2),
            ({"stationary": MOVING}, 0),
            ({"app2": 261}, 1),
        ):
            with self.subTest(**overrides):
                decision = menu_step(holding, **overrides)
                self.assertEqual(decision.route, route)
                self.assertEqual(decision.state, idle)
                self.assertIsNone(decision.commit_index)
                self.assertEqual(decision.mil_pulses, 0)

    def test_stationary_menu_res_and_set_wrap_on_edges(self):
        active = cf.CruiseFreeState(
            menu_phase=cf.MenuPhase.ACTIVE,
            tach_mode=cf.TachMode.STATIONARY_MENU,
            menu_timer=585,
        )
        for button, start, expected_slots in (
            (cf.BUTTON_RES, 5, (1, 2, 3, 4, 5)),
            (cf.BUTTON_SET, 1, (5, 4, 3, 2, 1)),
        ):
            state = replace(active, menu_slot=start, tach_slot=start)
            for slot in expected_slots:
                with self.subTest(button=button, slot=slot):
                    edge = menu_step(
                        state, current_code=button, previous_code=cf.BUTTON_RELEASED
                    )
                    self.assertIsNone(edge.commit_index)
                    self.assertEqual(edge.mil_pulses, 0)
                    self.assertEqual(edge.state.menu_slot, slot)
                    self.assertEqual(edge.state.tach_slot, slot)
                    self.assertEqual(edge.state.menu_timer, 0)
                    held = menu_step(edge.state, current_code=button, previous_code=button)
                    self.assertIsNone(held.commit_index)
                    self.assertEqual(held.state.menu_slot, slot)
                    self.assertEqual(held.state.menu_timer, 1)
                    state = menu_step(
                        held.state, current_code=cf.BUTTON_RELEASED, previous_code=button
                    ).state

    def test_stationary_menu_commits_on_fresh_cancel_timeout_or_motion(self):
        active = cf.CruiseFreeState(
            menu_phase=cf.MenuPhase.ACTIVE,
            menu_slot=4,
            menu_timer=584,
            tach_mode=cf.TachMode.STATIONARY_MENU,
            tach_slot=4,
        )
        waiting = menu_step(active)
        self.assertIsNone(waiting.commit_index)
        self.assertEqual(waiting.state.menu_timer, 585)
        for state, overrides in (
            (active, {"previous_code": cf.BUTTON_RELEASED}),
            (waiting.state, {}),
            (active, {"stationary": MOVING}),
        ):
            with self.subTest(state=state, **overrides):
                decision = menu_step(state, **overrides)
                self.assertEqual(decision.route, 1)
                self.assertEqual(decision.commit_index, 3)
                self.assertEqual(decision.mil_pulses, 1)
                self.assertEqual(decision.state, cf.CruiseFreeState(active_source=3))

    def test_stationary_menu_accelerator_abort_takes_priority_over_commit(self):
        active = cf.CruiseFreeState(
            menu_phase=cf.MenuPhase.ACTIVE,
            menu_slot=5,
            menu_timer=585,
            tach_mode=cf.TachMode.STATIONARY_MENU,
            tach_slot=5,
        )
        for overrides in (
            {"app1": 261, "previous_code": cf.BUTTON_RELEASED},
            {"app2": 261},
            {"app1": 261, "stationary": MOVING},
            {"current_code": cf.BUTTON_INVALID},
        ):
            with self.subTest(**overrides):
                decision = menu_step(active, **overrides)
                self.assertEqual(decision.route, 1)
                self.assertIsNone(decision.commit_index)
                self.assertEqual(decision.mil_pulses, 0)
                self.assertEqual(decision.state, cf.CruiseFreeState())

    def test_brake_app_first_press_previews_active_map_and_cycles_without_commit(self):
        state = cf.CruiseFreeState()
        for _ in range(3):
            blocked = brake_app_step(state, app=700, active_index=2)
            self.assertEqual(blocked.state, state)
            self.assertIsNone(blocked.commit_index)
            self.assertEqual(blocked.mil_pulses, 0)

        release = brake_app_step(state, app=260)
        self.assertEqual(release.state.phase, cf.CruiseFreePhase.IDLE_WAIT_RELEASE)
        self.assertEqual(release.state.debounce, 1)
        armed = brake_app_step(release.state, app=260)
        self.assertEqual(armed.state.phase, cf.CruiseFreePhase.ARMED_ENTER)
        partial = brake_app_step(armed.state, app=700, active_index=2)
        self.assertEqual(partial.state.phase, cf.CruiseFreePhase.ARMED_ENTER)
        self.assertEqual(partial.state.debounce, 1)
        reset = brake_app_step(partial.state, app=450, active_index=2)
        self.assertEqual(reset.state, armed.state)

        partial = brake_app_step(reset.state, app=700, active_index=2)
        entered = brake_app_step(partial.state, app=700, active_index=2)
        self.assertIsNone(entered.commit_index)
        self.assertEqual(entered.mil_pulses, 1)
        self.assertEqual(entered.state.phase, cf.CruiseFreePhase.ACTIVE_PRESSED)
        self.assertEqual(entered.state.selected_slot, 3)
        self.assertEqual(entered.state.tach_mode, cf.TachMode.BRAKE_APP_RPM0)
        self.assertEqual(entered.state.tach_slot, 3)

        state = entered.state
        for slot in (4, 5, 1, 2):
            with self.subTest(slot=slot):
                held = brake_app_step(state, app=700, active_index=2)
                self.assertEqual(held.state, state)
                self.assertIsNone(held.commit_index)
                self.assertEqual(held.mil_pulses, 0)

                release = brake_app_step(state, app=260, active_index=2)
                self.assertEqual(release.state.phase, cf.CruiseFreePhase.ACTIVE_PRESSED)
                ready = brake_app_step(release.state, app=260, active_index=2)
                self.assertEqual(ready.state.phase, cf.CruiseFreePhase.ACTIVE_RELEASED)
                self.assertEqual(ready.state.selected_slot, state.selected_slot)
                partial = brake_app_step(ready.state, app=700, active_index=2)
                self.assertEqual(partial.state.selected_slot, state.selected_slot)
                advanced = brake_app_step(partial.state, app=700, active_index=2)
                self.assertIsNone(advanced.commit_index)
                self.assertEqual(advanced.mil_pulses, 0)
                state = advanced.state
                self.assertEqual(state.phase, cf.CruiseFreePhase.ACTIVE_PRESSED)
                self.assertEqual(state.selected_slot, slot)
                self.assertEqual(state.tach_slot, slot)
                self.assertEqual(tach_step(state, app1=700, app2=700), (slot * 0x1F40, state))

        committed = brake_app_step(state, app=700, brake_held=False, active_index=2)
        self.assertEqual(committed.commit_index, 1)
        self.assertEqual(committed.mil_pulses, 1)
        self.assertEqual(committed.state, cf.CruiseFreeState(active_source=2))
        self.assertEqual(tach_step(committed.state), (None, committed.state))

    def test_brake_app_commit_from_released_phase_and_vetoes(self):
        active = cf.CruiseFreeState(
            phase=cf.CruiseFreePhase.ACTIVE_RELEASED,
            selected_slot=5,
            tach_mode=cf.TachMode.BRAKE_APP_RPM0,
            tach_slot=5,
        )
        committed = brake_app_step(active, brake_held=False)
        self.assertEqual(committed.commit_index, 4)
        self.assertEqual(committed.mil_pulses, 1)
        self.assertEqual(committed.state, cf.CruiseFreeState(active_source=2))

        for overrides, reason in (
            ({"rpm_fine": 1, "brake_held": False}, cf.BlockReason.ENGINE_RUNNING),
            ({"rpm_coarse": 1}, cf.BlockReason.ENGINE_RUNNING),
            ({"stationary": MOVING, "brake_held": False}, cf.BlockReason.NOT_STATIONARY),
            ({"app1": 761, "app2": 700}, cf.BlockReason.PEDAL_IMPLAUSIBLE),
            ({"app1": 965, "app2": 965}, cf.BlockReason.PEDAL_IMPLAUSIBLE),
            ({"app1": 964, "app2": 1001}, cf.BlockReason.PEDAL_IMPLAUSIBLE),
            ({"app1": 59, "app2": 60}, cf.BlockReason.PEDAL_IMPLAUSIBLE),
            (
                {"config": replace(cf.DEFAULT_CONFIG, flags=cf.FLAG_ASCD_ENABLED)},
                cf.BlockReason.CONFIG_DISABLED_OR_INVALID,
            ),
        ):
            with self.subTest(**overrides):
                decision = brake_app_step(active, **overrides)
                self.assertIsNone(decision.commit_index)
                self.assertEqual(decision.mil_pulses, 0)
                self.assertEqual(decision.state, cf.CruiseFreeState(last_reason=reason))

        idle_release = brake_app_step(cf.CruiseFreeState(), brake_held=False)
        self.assertIsNone(idle_release.commit_index)
        self.assertEqual(idle_release.state.last_reason, cf.BlockReason.BRAKE_RELEASED)

    def test_tach_stationary_menu_allows_running_rpm_and_clears_only_tach_on_motion(self):
        active = cf.CruiseFreeState(
            menu_phase=cf.MenuPhase.ACTIVE,
            menu_slot=5,
            menu_timer=3,
            tach_mode=cf.TachMode.STATIONARY_MENU,
            tach_slot=5,
        )
        self.assertEqual(
            tach_step(active, rpm_fine=2300, rpm_coarse=58, app1=260, app2=260),
            (5 * 0x1F40, active),
        )
        wire, moving = tach_step(active, stationary=MOVING, rpm_fine=2300, rpm_coarse=58)
        self.assertIsNone(wire)
        self.assertEqual(moving, replace(active, tach_mode=cf.TachMode.OFF, tach_slot=0))
        committed = menu_step(moving, stationary=MOVING)
        self.assertEqual(committed.commit_index, 4)
        self.assertEqual(committed.mil_pulses, 1)

        for overrides in ({"app1": 261}, {"app2": 261, "stationary": MOVING}):
            with self.subTest(**overrides):
                self.assertEqual(tach_step(active, **overrides), (None, cf.CruiseFreeState()))

    def test_tach_brake_app_requires_both_rpm_values_zero_and_live_stationary(self):
        active = cf.CruiseFreeState(
            phase=cf.CruiseFreePhase.ACTIVE_PRESSED,
            selected_slot=4,
            tach_mode=cf.TachMode.BRAKE_APP_RPM0,
            tach_slot=4,
        )
        self.assertEqual(tach_step(active), (4 * 0x1F40, active))
        cleared = replace(active, tach_mode=cf.TachMode.OFF, tach_slot=0)
        for overrides in (
            {"rpm_fine": 1},
            {"rpm_coarse": 0x0100},
            {"stationary": MOVING},
            {"stationary": replace(STATIONARY, last_raw_speed=0xFFFF)},
            {"stationary": replace(STATIONARY, age=4)},
            {"stationary": replace(STATIONARY, flags=cf.STATIONARY_OBSERVED_BIT)},
            {"stationary": replace(STATIONARY, flags=cf.STATIONARY_VALID_BIT)},
            {"port_ready": False},
            {"hcan1_ready": False},
        ):
            with self.subTest(**overrides):
                self.assertEqual(tach_step(active, **overrides), (None, cleared))

    def test_tach_flag_is_independent_and_invalid_tach_state_preserves_selection(self):
        no_tach = replace(
            cf.DEFAULT_CONFIG, flags=cf.DEFAULT_CONFIG.flags & ~cf.FLAG_TACH_ALLOWED
        )
        menu_config = replace(no_tach, cancel_hold_ticks=1)
        menu = menu_step(cf.CruiseFreeState(), active_index=4, config=menu_config)
        self.assertEqual(menu.mil_pulses, 1)
        self.assertEqual(menu.state.menu_slot, 5)
        self.assertEqual(menu.state.tach_mode, cf.TachMode.OFF)
        self.assertEqual(menu.state.tach_slot, 0)
        brake = brake_app_step(
            cf.CruiseFreeState(phase=cf.CruiseFreePhase.ARMED_ENTER, debounce=1),
            active_index=4, app=700, config=no_tach,
        )
        self.assertEqual(brake.mil_pulses, 1)
        self.assertEqual(brake.state.selected_slot, 5)
        self.assertEqual(brake.state.tach_mode, cf.TachMode.OFF)
        self.assertEqual(brake.state.tach_slot, 0)

        active = replace(menu.state, tach_mode=cf.TachMode.STATIONARY_MENU, tach_slot=5)
        self.assertEqual(tach_step(active, config=no_tach), (None, menu.state))
        for invalid in (
            replace(active, tach_mode=cf.TachMode.OFF),
            replace(active, tach_mode=3),
            replace(active, tach_slot=0),
            replace(active, tach_slot=6),
        ):
            with self.subTest(invalid=invalid):
                self.assertEqual(tach_step(invalid), (None, menu.state))

    def test_invalid_mscf_wipes_stationary_and_transient_state_across_handlers(self):
        seeded = cf.CruiseFreeRuntime(
            stationary=STATIONARY,
            selector=cf.CruiseFreeState(
                phase=cf.CruiseFreePhase.ACTIVE_RELEASED,
                debounce=1,
                selected_slot=3,
                tach_mode=cf.TachMode.STATIONARY_MENU,
                tach_slot=2,
                menu_phase=cf.MenuPhase.ACTIVE,
                menu_slot=2,
                menu_timer=4,
                active_source=2,
            ),
        )
        gates = dict(port_ready=True, hcan1_ready=True)
        for bad in (None, replace(cf.DEFAULT_CONFIG, age_limit_ticks=0xFF)):
            with self.subTest(config=bad):
                rx = seeded.step_stationary(
                    new_frame=True, raw_speed=0, config=bad, **gates
                )
                menu, menu_decision = seeded.step_menu(
                    active_index=0, current_code=cf.BUTTON_CANCEL,
                    previous_code=cf.BUTTON_RELEASED, feedback_active=False,
                    app1=151, app2=151, config=bad, **gates,
                )
                selector, commit = seeded.step_selector(
                    active_index=0, rpm_fine=500, rpm_coarse=10,
                    brake_held=True, app1=800, app2=800, config=bad, **gates,
                )
                wire, tx = seeded.step_tach_wire(
                    rpm_fine=0, rpm_coarse=0, config=bad, **gates
                )
                self.assertIsNone(menu_decision.commit_index)
                self.assertIsNone(commit)
                self.assertIsNone(wire)
                cleared = cf.CruiseFreeRuntime(selector=cf.CruiseFreeState(active_source=2))
                self.assertEqual((rx, menu, tx), (cleared, cleared, cleared))
                self.assertEqual(
                    selector,
                    replace(
                        cleared,
                        selector=replace(
                            cleared.selector,
                            last_reason=cf.BlockReason.CONFIG_DISABLED_OR_INVALID,
                        ),
                    ),
                )
                restored = cleared.step_stationary(
                    new_frame=False, raw_speed=0, config=cf.DEFAULT_CONFIG, **gates
                )
                self.assertFalse(restored.stationary.valid)
                recovered = restored.step_stationary(
                    new_frame=True, raw_speed=0, config=cf.DEFAULT_CONFIG, **gates
                )
                self.assertTrue(recovered.stationary.valid)


if __name__ == "__main__":
    unittest.main()
