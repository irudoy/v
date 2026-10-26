import sys
import threading
import types
import unittest
from unittest import mock

from tools.can_dashboard import app
from tools.can_dashboard import model, presentation, sources


class PcanReconnectTest(unittest.TestCase):
    def exercise_reconnect(self, *, cancel_waiting, stop_through_app=False):
        old_stop, new_stop = threading.Event(), threading.Event()
        old_connected, new_decision = threading.Event(), threading.Event()
        shutdown_entered, release_shutdown = threading.Event(), threading.Event()
        actions, new_events = [], []

        class FakeBus:
            def __init__(self, name, stop):
                self.name, self.stop = name, stop

            def recv(self, timeout):
                self.stop.wait(timeout)
                return None

            def shutdown(self):
                actions.append(("shutdown", self.name))
                if self.name == "old":
                    shutdown_entered.set()
                    if not release_shutdown.wait(2):
                        raise RuntimeError("test did not release shutdown")
                actions.append(("released", self.name))

        def open_bus(**_options):
            name = threading.current_thread().name
            actions.append(("open", name))
            if name == "new" and not cancel_waiting:
                new_stop.set()
            return FakeBus(name, old_stop if name == "old" else new_stop)

        def reset(_channel):
            actions.append(("reset", threading.current_thread().name))

        def emit_old(event):
            if isinstance(event, sources.SourceStatus) and event.state == "connected":
                old_connected.set()

        def emit_new(event):
            new_events.append(event)
            if isinstance(event, sources.SourceStatus) and event.state in {"connecting", "connected"}:
                new_decision.set()

        config = sources.PcanConfiguration(reset_channel=True)
        old = threading.Thread(target=sources.run_pcan, args=(config, old_stop, emit_old), name="old")
        new = threading.Thread(target=sources.run_pcan, args=(config, new_stop, emit_new), name="new")
        fake_can = types.SimpleNamespace(
            Bus=open_bus, BusState=types.SimpleNamespace(PASSIVE="passive", ACTIVE="active"),
        )
        with mock.patch.dict(sys.modules, {"can": fake_can}), \
                mock.patch.object(sources, "_reset_pcan_channel", side_effect=reset):
            try:
                old.start()
                self.assertTrue(old_connected.wait(1))
                old_stop.set()
                self.assertTrue(shutdown_entered.wait(1))
                if stop_through_app:
                    dashboard = object.__new__(app.DashboardApp)
                    dashboard.stop_recording = mock.Mock()
                    dashboard._sync_replay_bar = mock.Mock()
                    dashboard._set_stream_command = mock.Mock()
                    dashboard._set_source_status = mock.Mock()
                    dashboard.events = app.queue.Queue()
                    dashboard.source_generation = 1
                    dashboard.source_state = "connected"
                    dashboard.stop_event = old_stop
                    dashboard.worker = old
                    dashboard.stop_source()
                    self.assertTrue(old.is_alive())
                new.start()
                self.assertTrue(new_decision.wait(1))
                self.assertNotIn(("open", "new"), actions)
                self.assertNotIn(("reset", "new"), actions)
                if cancel_waiting:
                    new_stop.set()
                    new.join(timeout=1)
                    self.assertFalse(new.is_alive())
                    self.assertEqual(new_events[-1].state, "stopped")
                release_shutdown.set()
                old.join(timeout=1)
                new.join(timeout=1)
                self.assertFalse(old.is_alive())
                self.assertFalse(new.is_alive())
            finally:
                old_stop.set()
                new_stop.set()
                release_shutdown.set()
                old.join(timeout=1)
                if new.ident is not None:
                    new.join(timeout=1)
        if cancel_waiting:
            self.assertNotIn(("open", "new"), actions)
        else:
            last_old_reset = max(index for index, action in enumerate(actions) if action == ("reset", "old"))
            self.assertLess(actions.index(("released", "old")), last_old_reset)
            self.assertLess(last_old_reset, actions.index(("reset", "new")))
            self.assertLess(last_old_reset, actions.index(("open", "new")))

    def test_reconnect_waits_for_old_shutdown_and_channel_release(self):
        self.exercise_reconnect(cancel_waiting=False, stop_through_app=True)

    def test_cancelled_waiting_source_never_opens_or_resets_the_channel(self):
        self.exercise_reconnect(cancel_waiting=True)

    def test_source_cancelled_before_start_does_not_touch_the_channel(self):
        stopped = threading.Event()
        stopped.set()
        fake_can = types.SimpleNamespace(
            Bus=mock.Mock(), BusState=types.SimpleNamespace(PASSIVE="passive", ACTIVE="active"),
        )
        events = []
        with mock.patch.dict(sys.modules, {"can": fake_can}), \
                mock.patch.object(sources, "_reset_pcan_channel") as reset:
            sources.run_pcan(sources.PcanConfiguration(reset_channel=True), stopped, events.append)
        fake_can.Bus.assert_not_called()
        reset.assert_not_called()
        self.assertEqual(events[-1].state, "stopped")

    def test_connected_status_error_still_closes_bus_and_allows_retry(self):
        stop = threading.Event()
        shutdown = mock.Mock()
        bus = types.SimpleNamespace(shutdown=shutdown)

        def emit(event):
            if event.state == "connected":
                raise ValueError("status consumer failed")

        def retry_open(**_options):
            stop.set()
            return bus

        fake_can = types.SimpleNamespace(
            Bus=mock.Mock(return_value=bus),
            BusState=types.SimpleNamespace(PASSIVE="passive", ACTIVE="active"),
        )
        with mock.patch.dict(sys.modules, {"can": fake_can}):
            with self.assertRaisesRegex(ValueError, "status consumer failed"):
                sources.run_pcan(sources.PcanConfiguration(), stop, emit)
            shutdown.assert_called_once_with()
            fake_can.Bus.side_effect = retry_open
            sources.run_pcan(sources.PcanConfiguration(), stop, lambda _event: None)
        self.assertEqual(shutdown.call_count, 2)


class PcanFrameSelectionTest(unittest.TestCase):
    def receive(self, records, *, can_id=model.DEFAULT_CAN_ID, listen_only=False):
        stop = threading.Event()
        events = []

        class SoftwareFilteredBus:
            def __init__(self, **options):
                self.filters = options["can_filters"]
                self.records = iter(records)

            def recv(self, timeout):
                for record in self.records:
                    if self.filters is None or any(
                        row["extended"] == record.is_extended_id
                        and (row["can_id"] ^ record.arbitration_id) & row["can_mask"] == 0
                        for row in self.filters
                    ):
                        return record
                stop.set()
                return None

            def shutdown(self):
                pass

        fake_can = types.SimpleNamespace(
            Bus=SoftwareFilteredBus,
            BusState=types.SimpleNamespace(PASSIVE="passive", ACTIVE="active"),
        )
        with mock.patch.dict(sys.modules, {"can": fake_can}):
            sources.run_pcan(
                sources.PcanConfiguration(can_id=can_id, listen_only=listen_only), stop, events.append,
            )
        return [event for event in events if isinstance(event, model.FrameRecord)]

    def test_live_errors_reach_the_model_and_visible_health_counter(self):
        generator = model.DemoGenerator()
        records = [
            model.FrameRecord(0, b"", 0.0, is_error_frame=True),
            *generator.group(1, 0.0),
            model.FrameRecord(0x1FFFFFFF, b"", 0.1, is_extended_id=True, is_error_frame=True),
        ]
        dashboard = object.__new__(app.DashboardApp)
        dashboard.model = model.DashboardModel("tuning", model.DEFAULT_CAN_ID, 1)
        for record in self.receive(records):
            dashboard.model.process_frame(record)
        self.assertEqual(dashboard.model.stats().error_frames, 2)
        self.assertEqual(dashboard.model.stats().completed_groups, 1)

        dashboard.palette = app.DARK
        dashboard.source_state = "connected"
        dashboard.source_drops = 0
        dashboard.status_dot_color = None
        dashboard.status_dot = types.SimpleNamespace(configure=mock.Mock())
        dashboard.status_field = types.SimpleNamespace(set_foreground=mock.Mock())
        for name in ("status_var", "schema_var", "rate_var", "loss_var"):
            setattr(dashboard, name, types.SimpleNamespace(set=mock.Mock()))
        dashboard._sync_source_button = mock.Mock()
        dashboard._refresh_panels = mock.Mock()
        dashboard._refresh_timers = mock.Mock()
        dashboard._refresh_replay = mock.Mock()
        dashboard.last_ui_group = 0
        dashboard.hero_cards = {}
        dashboard.active_tab = 0
        dashboard.health_vars = {
            key: types.SimpleNamespace(set=mock.Mock()) for key, _title, _sample in app.HEALTH_FIELDS
        }
        dashboard._refresh(app.time.monotonic())
        dashboard.health_vars["errors"].set.assert_called_once_with("errors=2")

    def test_needed_standard_data_arrive_and_unrelated_data_stay_excluded(self):
        for can_id in (model.DEFAULT_CAN_ID, 0x6E0):
            for listen_only in (False, True):
                with self.subTest(can_id=can_id, listen_only=listen_only):
                    generator = model.DemoGenerator(can_id)
                    expected = [*generator.group(1, 0.0), *generator.stock_context(1, 0.0)]
                    unrelated = model.FrameRecord(0x123, bytes(8), 0.0)
                    extended = model.FrameRecord(can_id, bytes(8), 0.0, is_extended_id=True)
                    records = self.receive(
                        [unrelated, *expected, extended], can_id=can_id, listen_only=listen_only,
                    )
                    self.assertEqual(
                        [(frame.arbitration_id, frame.data) for frame in records],
                        [(frame.arbitration_id, frame.data) for frame in expected],
                    )
                    delivered = {frame.arbitration_id for frame in records}
                    self.assertTrue({can_id, *model.OBSERVED_IDS} <= delivered)


class ReplayOptionTest(unittest.TestCase):
    def test_invalid_replay_speed_is_rejected_before_the_window_opens(self):
        for speed in ("0", "-1", "nan", "inf"):
            with self.subTest(speed=speed), mock.patch.object(
                app.tk, "Tk"
            ) as window:
                with self.assertRaises(SystemExit) as caught:
                    app.main(["--replay-speed", speed, "--no-log-file"])
                self.assertEqual(
                    str(caught.exception),
                    "replay speed must be positive",
                )
                window.assert_not_called()

    def test_replay_loop_is_a_command_line_option(self):
        self.assertFalse(app.build_parser().parse_args([]).replay_loop)
        self.assertTrue(
            app.build_parser().parse_args(["--replay-loop"]).replay_loop
        )


class PcanSourceTest(unittest.TestCase):
    def test_active_connection_sends_queued_stream_control(self):
        sent = []
        events = []
        requests = sources.queue.Queue()
        requests.put(sources.ControlRequest(
            "start",
            0x6F1,
            bytes.fromhex("54454C320201B632"),
        ))

        class FakeMessage:
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)

        bus = types.SimpleNamespace(
            send=lambda message, timeout: sent.append((message, timeout))
        )
        can_module = types.SimpleNamespace(Message=FakeMessage)

        sources._send_control_requests(
            bus,
            can_module,
            sources.PcanConfiguration(listen_only=False),
            requests,
            events.append,
        )

        self.assertTrue(requests.empty())
        self.assertEqual(len(sent), 1)
        self.assertEqual(sent[0][0].arbitration_id, 0x6F1)
        self.assertEqual(
            sent[0][0].data,
            bytes.fromhex("54454C320201B632"),
        )
        self.assertEqual(sent[0][1], 0.1)
        self.assertEqual(events[0].state, "sent")

    def test_listen_only_connection_rejects_stream_control(self):
        events = []
        requests = sources.queue.Queue()
        requests.put(sources.ControlRequest("stop", 0x6F1, bytes(8)))
        bus = types.SimpleNamespace(send=mock.Mock())

        sources._send_control_requests(
            bus,
            types.SimpleNamespace(Message=mock.Mock()),
            sources.PcanConfiguration(listen_only=True),
            requests,
            events.append,
        )

        bus.send.assert_not_called()
        self.assertTrue(requests.empty())
        self.assertEqual(events[0].state, "error")
        self.assertIn("active/ACK", events[0].detail)

    def test_reset_wraps_bus_lifecycle_when_enabled(self):
        actions = []

        class FakeBus:
            def shutdown(self):
                actions.append(("shutdown",))

        def open_bus(**kwargs):
            actions.append(("open", kwargs))
            stop_event.set()
            return FakeBus()

        fake_can = types.SimpleNamespace(
            Bus=open_bus,
            BusState=types.SimpleNamespace(PASSIVE="passive", ACTIVE="active"),
        )
        stop_event = threading.Event()
        events = []

        def reset(channel):
            actions.append(("reset", channel))

        with mock.patch.dict(sys.modules, {"can": fake_can}), mock.patch.object(
            sources,
            "_reset_pcan_channel",
            side_effect=reset,
        ):
            sources.run_pcan(
                sources.PcanConfiguration(reset_channel=True),
                stop_event,
                events.append,
            )

        self.assertEqual(
            [action[0] for action in actions],
            ["reset", "open", "shutdown", "reset"],
        )
        self.assertEqual(actions[0][1], "PCAN_USBBUS1")
        self.assertEqual(actions[1][1]["state"], "active")
        self.assertEqual(events[0].state, "connected")
        self.assertEqual(
            events[-1],
            sources.SourceStatus("stopped", "PCAN channel closed"),
        )

    def test_listen_only_configuration_opens_the_passive_state(self):
        states = []

        class FakeBus:
            def shutdown(self):
                pass

        def open_bus(**kwargs):
            states.append(kwargs["state"])
            stop_event.set()
            return FakeBus()

        fake_can = types.SimpleNamespace(
            Bus=open_bus,
            BusState=types.SimpleNamespace(PASSIVE="passive", ACTIVE="active"),
        )
        stop_event = threading.Event()
        events = []

        with mock.patch.dict(sys.modules, {"can": fake_can}):
            sources.run_pcan(
                sources.PcanConfiguration(listen_only=True),
                stop_event,
                events.append,
            )

        self.assertEqual(states, ["passive"])
        self.assertEqual(events[0].state, "connected")
        self.assertIn("listen-only", events[0].detail)

    def test_reset_releases_channel_after_bus_initialization_failure(self):
        actions = []

        def open_bus(**_kwargs):
            actions.append(("open",))
            raise RuntimeError("open failed")

        fake_can = types.SimpleNamespace(
            Bus=open_bus,
            BusState=types.SimpleNamespace(PASSIVE="passive", ACTIVE="active"),
        )
        events = []

        def reset(channel):
            actions.append(("reset", channel))

        with mock.patch.dict(sys.modules, {"can": fake_can}), mock.patch.object(
            sources,
            "_reset_pcan_channel",
            side_effect=reset,
        ):
            sources.run_pcan(
                sources.PcanConfiguration(reset_channel=True),
                threading.Event(),
                events.append,
            )

        self.assertEqual(
            actions,
            [
                ("reset", "PCAN_USBBUS1"),
                ("open",),
                ("reset", "PCAN_USBBUS1"),
            ],
        )
        self.assertEqual(events[0].state, "error")
        self.assertIn("open failed", events[0].detail)

    def test_receive_error_remains_terminal_status(self):
        class FakeBus:
            def recv(self, timeout):
                self.timeout = timeout
                raise RuntimeError("receive failed")

            def shutdown(self):
                pass

        fake_can = types.SimpleNamespace(
            Bus=lambda **_kwargs: FakeBus(),
            BusState=types.SimpleNamespace(PASSIVE="passive", ACTIVE="active"),
        )
        events = []
        with mock.patch.dict(sys.modules, {"can": fake_can}):
            sources.run_pcan(
                sources.PcanConfiguration(),
                threading.Event(),
                events.append,
            )

        self.assertEqual([event.state for event in events], ["connected", "error"])
        self.assertIn("receive failed", events[-1].detail)

    def test_shutdown_error_is_reported(self):
        class FakeBus:
            def __init__(self):
                stop_event.set()

            def shutdown(self):
                raise RuntimeError("shutdown failed")

        fake_can = types.SimpleNamespace(
            Bus=lambda **_kwargs: FakeBus(),
            BusState=types.SimpleNamespace(PASSIVE="passive", ACTIVE="active"),
        )
        stop_event = threading.Event()
        events = []
        with mock.patch.dict(sys.modules, {"can": fake_can}):
            sources.run_pcan(
                sources.PcanConfiguration(),
                stop_event,
                events.append,
            )

        self.assertEqual([event.state for event in events], ["connected", "error"])
        self.assertIn("shutdown failed", events[-1].detail)

    def test_driver_check_loads_library_without_touching_channel(self):
        actions = []

        class FakePCANBasic:
            def __init__(self):
                actions.append("loaded")

            def Uninitialize(self, _channel):
                actions.append("uninitialized")

        modules = {
            name: types.ModuleType(name)
            for name in (
                "can",
                "can.interfaces",
                "can.interfaces.pcan",
                "can.interfaces.pcan.basic",
            )
        }
        modules["can.interfaces.pcan.basic"].PCANBasic = FakePCANBasic
        with mock.patch.dict(sys.modules, modules):
            sources._check_pcan_driver()

        self.assertEqual(actions, ["loaded"])

    def test_macos_parser_defaults_to_channel_reset(self):
        with mock.patch.object(app.sys, "platform", "darwin"):
            args = app.build_parser().parse_args([])
        self.assertTrue(args.reset_channel)

        args = app.build_parser().parse_args(["--no-reset-channel"])
        self.assertFalse(args.reset_channel)

        args = app.build_parser().parse_args(["--smoke-test"])
        self.assertTrue(args.smoke_test)

        args = app.build_parser().parse_args(["--pcan-driver-check"])
        self.assertTrue(args.pcan_driver_check)

    def test_active_ack_state_is_the_default(self):
        self.assertFalse(sources.PcanConfiguration().listen_only)
        self.assertFalse(app.build_parser().parse_args([]).listen_only)
        self.assertTrue(
            app.build_parser().parse_args(["--listen-only"]).listen_only
        )
        with self.assertRaises(SystemExit), mock.patch.object(
            app.sys, "stderr"
        ):
            app.build_parser().parse_args(["--active"])


class DashboardPresentationTest(unittest.TestCase):
    @staticmethod
    def control_dashboard(*, active):
        dashboard = app.DashboardApp.__new__(app.DashboardApp)
        dashboard.control_requests = sources.queue.Queue(maxsize=8)
        dashboard.worker = types.SimpleNamespace(is_alive=lambda: True)
        dashboard.pcan_active = active
        dashboard.model = types.SimpleNamespace(
            can_id=0x6F0,
            decoder=types.SimpleNamespace(
                schema=app.can_telemetry.load_schema()[0]
            ),
        )
        values = []
        dashboard.control_var = types.SimpleNamespace(set=values.append)
        return dashboard, values

    def test_stream_start_queues_schema_declared_control_frame(self):
        dashboard, values = self.control_dashboard(active=True)

        dashboard.send_stream_command("start")

        self.assertEqual(
            dashboard.control_requests.get_nowait(),
            sources.ControlRequest(
                "start",
                0x6F1,
                bytes.fromhex("54454C320201B632"),
            ),
        )
        self.assertEqual(values[-1], "Control: START queued")

    def test_stream_toggle_sends_the_pending_command(self):
        dashboard, _values = self.control_dashboard(active=True)
        dashboard.stream_command = "stop"
        dashboard.stream_button = types.SimpleNamespace(
            configure=lambda **options: None
        )

        dashboard.toggle_stream()

        self.assertEqual(
            dashboard.control_requests.get_nowait().command,
            "stop",
        )

    def test_the_window_is_painted_on_a_timer_of_its_own(self):
        """The queue drain must not carry the painting.

        A toolkit rounds a timer up to the step of its own event loop, so a
        painting driven from the drain lands on the first drain tick past the
        painting interval and runs at a fraction of the rate that interval
        names.
        """
        dashboard = app.DashboardApp.__new__(app.DashboardApp)
        dashboard.events = app.queue.Queue()
        dashboard.source_generation = 1
        dashboard.recorder = None
        dashboard.feed = None
        delays = []
        dashboard.root = types.SimpleNamespace(
            after=lambda delay, _call: delays.append(delay)
        )
        dashboard._refresh = mock.Mock()

        dashboard._poll()

        dashboard._refresh.assert_not_called()
        self.assertEqual(delays, [app.POLL_INTERVAL_MS])

    def test_the_painting_timer_paints_and_renews_itself(self):
        dashboard = app.DashboardApp.__new__(app.DashboardApp)
        calls = []
        dashboard.root = types.SimpleNamespace(
            after=lambda delay, call: calls.append((delay, call))
        )
        dashboard._refresh = mock.Mock()

        dashboard._refresh_tick()

        dashboard._refresh.assert_called_once()
        self.assertEqual(
            calls,
            [(app.REFRESH_INTERVAL_MS, dashboard._refresh_tick)],
        )

    def test_confirmed_stream_command_flips_the_button(self):
        dashboard = app.DashboardApp.__new__(app.DashboardApp)
        dashboard.events = app.queue.Queue()
        dashboard.source_generation = 3
        dashboard.stream_command = "start"
        shown = []
        lit = []

        def configure(**options):
            shown.append(options["icon"])
            lit.append(options["lit"])

        dashboard.stream_button = types.SimpleNamespace(configure=configure)
        dashboard.control_var = types.SimpleNamespace(set=lambda text: None)
        dashboard.root = types.SimpleNamespace(after=lambda *arguments: None)
        dashboard.events.put(app.SourceEnvelope(
            3,
            sources.ControlStatus(
                "sent",
                "telemetry START sent on 0x6F1",
                "start",
            ),
        ))

        dashboard._poll()

        self.assertEqual(dashboard.stream_command, "stop")
        self.assertEqual(shown, [app.STREAM_ICONS["stop"]])
        self.assertEqual(lit, [True])

    def test_source_toggle_connects_and_disconnects(self):
        dashboard = app.DashboardApp.__new__(app.DashboardApp)
        dashboard.worker = None
        dashboard.start_pcan = mock.Mock()
        dashboard.stop_source = mock.Mock()

        dashboard.toggle_source()
        dashboard.worker = types.SimpleNamespace(is_alive=lambda: True)
        dashboard.toggle_source()

        dashboard.start_pcan.assert_called_once_with()
        dashboard.stop_source.assert_called_once_with()

    def test_source_button_tracks_the_running_worker(self):
        dashboard = app.DashboardApp.__new__(app.DashboardApp)
        texts = []
        lit = []

        def configure(**options):
            texts.append(options["text"])
            lit.append(options["lit"])

        dashboard.source_button = types.SimpleNamespace(configure=configure)
        dashboard.source_button_active = False
        dashboard.worker = types.SimpleNamespace(is_alive=lambda: True)

        dashboard._sync_source_button()
        dashboard._sync_source_button()
        dashboard.worker = None
        dashboard._sync_source_button()

        self.assertEqual(texts, ["DISCONNECT", "CONNECT"])
        self.assertEqual(lit, [True, False])

    def test_stream_control_requires_active_connection(self):
        dashboard, values = self.control_dashboard(active=False)

        dashboard.send_stream_command("stop")

        self.assertTrue(dashboard.control_requests.empty())
        self.assertIn("ACK enabled", values[-1])

    def test_cvtc_target_labels_match_recovered_roles(self):
        metrics = {
            metric.key: metric.label
            for _tab, panels in presentation.default().tabs
            for _title, panel_metrics in panels
            for metric in panel_metrics
        }
        self.assertEqual(
            metrics["intake_cvtc_target"],
            "Intake CVTC target",
        )
        self.assertEqual(
            metrics["exhaust_cvtc_target"],
            "Exhaust CVTC target",
        )

    def test_default_recording_name_is_generic_and_has_no_extension(self):
        with mock.patch.object(
            app.time,
            "strftime",
            return_value="2026-08-20_01-21-52",
        ):
            name = app.DashboardApp._default_recording_name()

        self.assertEqual(
            name,
            f"2026-08-20_01-21-52_vq-can-telemetry-v{app.__version__}",
        )
        self.assertFalse(name.endswith(".mlg"))

    def test_standard_can_id_parser_rejects_invalid_ui_values(self):
        self.assertEqual(app._parse_standard_can_id("0x6f0"), 0x6F0)
        for value in ("", "invalid", "0", "0x7ff", "0x800"):
            with self.subTest(value=value), self.assertRaisesRegex(
                ValueError,
                "0x001..0x7FE",
            ):
                app._parse_standard_can_id(value)

    def test_invalid_reconnect_stops_existing_source_before_error(self):
        dashboard = app.DashboardApp.__new__(app.DashboardApp)
        dashboard.can_id_var = types.SimpleNamespace(get=lambda: "invalid")
        dashboard.stop_source = mock.Mock()
        dashboard._set_source_status = mock.Mock()

        dashboard.start_pcan()

        dashboard.stop_source.assert_called_once_with()
        dashboard._set_source_status.assert_called_once_with(
            "error",
            "data CAN ID must be in 0x001..0x7FE",
        )

    def test_recording_ignores_frames_received_before_start(self):
        clock = app.FrameClock(10.0)
        before = model.FrameRecord(
            0x6F0,
            bytes(8),
            received_monotonic=9.9,
        )
        after = model.FrameRecord(
            0x6F0,
            bytes(8),
            received_monotonic=10.25,
        )
        later = model.FrameRecord(
            0x6F0,
            bytes(8),
            received_monotonic=10.40,
        )
        self.assertIsNone(clock.elapsed(before, 11.0))
        self.assertAlmostEqual(clock.elapsed(after, 11.0), 0.25)
        self.assertAlmostEqual(clock.elapsed(later, 11.0), 0.40)

    def test_recording_separates_frames_dequeued_in_one_burst(self):
        clock = app.FrameClock(10.0)
        burst = [
            model.FrameRecord(
                0x6F0,
                bytes(8),
                timestamp=1787740137.000000,
                received_monotonic=10.5,
            ),
            model.FrameRecord(
                0x6F0,
                bytes(8),
                timestamp=1787740137.000216,
                received_monotonic=10.5,
            ),
            model.FrameRecord(
                0x6F0,
                bytes(8),
                timestamp=1787740137.015000,
                received_monotonic=10.5,
            ),
        ]
        elapsed = [clock.elapsed(frame, 11.0) for frame in burst]

        self.assertTrue(clock.source_clock)
        self.assertAlmostEqual(elapsed[0], 0.5)
        self.assertAlmostEqual(elapsed[1], 0.500216, places=6)
        self.assertAlmostEqual(elapsed[2], 0.515, places=6)
        ticks = [round(value * 100_000) for value in elapsed]
        self.assertEqual(len(set(ticks)), len(ticks))

    def test_recording_uses_the_host_clock_without_interface_time(self):
        clock = app.FrameClock(10.0)
        first = model.FrameRecord(0x6F0, bytes(8), received_monotonic=10.5)
        second = model.FrameRecord(0x6F0, bytes(8), received_monotonic=10.53)

        self.assertAlmostEqual(clock.elapsed(first, 11.0), 0.5)
        self.assertAlmostEqual(clock.elapsed(second, 11.0), 0.53)
        self.assertFalse(clock.source_clock)

    def test_recording_abandons_a_stepping_interface_clock(self):
        clock = app.FrameClock(10.0)
        first = model.FrameRecord(
            0x6F0,
            bytes(8),
            timestamp=0.0,
            received_monotonic=10.5,
        )
        stepped = model.FrameRecord(
            0x6F0,
            bytes(8),
            timestamp=1787740137.0,
            received_monotonic=10.515,
        )
        after = model.FrameRecord(
            0x6F0,
            bytes(8),
            timestamp=1787740137.015,
            received_monotonic=10.53,
        )

        self.assertAlmostEqual(clock.elapsed(first, 11.0), 0.5)
        self.assertAlmostEqual(clock.elapsed(stepped, 11.0), 0.515)
        self.assertFalse(clock.source_clock)
        self.assertAlmostEqual(clock.elapsed(after, 11.0), 0.53)

    def test_recording_elapsed_never_decreases(self):
        clock = app.FrameClock(10.0)
        frames = [
            model.FrameRecord(
                0x6F0,
                bytes(8),
                timestamp=100.0,
                received_monotonic=10.5,
            ),
            model.FrameRecord(
                0x6F0,
                bytes(8),
                timestamp=99.5,
                received_monotonic=10.52,
            ),
            model.FrameRecord(
                0x6F0,
                bytes(8),
                timestamp=99.6,
                received_monotonic=10.54,
            ),
        ]
        elapsed = [clock.elapsed(frame, 11.0) for frame in frames]

        self.assertEqual(elapsed, sorted(elapsed))
        self.assertFalse(clock.source_clock)
        self.assertAlmostEqual(elapsed[1], 0.52)
        self.assertAlmostEqual(elapsed[2], 0.54)

    def test_source_emitter_rejects_events_after_generation_change(self):
        dashboard = app.DashboardApp.__new__(app.DashboardApp)
        dashboard.events = app.queue.Queue(maxsize=4)
        dashboard.source_drops = 0
        dashboard.source_generation = 7
        emit = dashboard._source_emitter()
        status = sources.SourceStatus("connected", "test")
        emit(status)
        envelope = dashboard.events.get_nowait()
        self.assertEqual(envelope, app.SourceEnvelope(7, status))

        dashboard.source_generation = 8
        emit(sources.SourceStatus("stopped", "stale"))
        self.assertTrue(dashboard.events.empty())

    def test_source_emitter_preserves_terminal_status_when_queue_is_full(self):
        dashboard = app.DashboardApp.__new__(app.DashboardApp)
        dashboard.events = app.queue.Queue(maxsize=1)
        dashboard.source_drops = 0
        dashboard.source_generation = 2
        emit = dashboard._source_emitter()
        emit(model.FrameRecord(0x6F0, bytes(8)))
        status = sources.SourceStatus("error", "receive failed")
        emit(status)

        envelope = dashboard.events.get_nowait()
        self.assertEqual(envelope, app.SourceEnvelope(2, status))
        self.assertEqual(dashboard.source_drops, 1)

    def test_nonfinite_values_render_as_missing(self):
        metric = app.Metric("gps_lat", "GPS", "deg", 6)
        self.assertEqual(app.DashboardApp._format(metric, float("nan")), "--")
        self.assertEqual(app.DashboardApp._format(metric, float("inf")), "--")

    def test_cli_rejects_nonfinite_replay_speed_before_tk_initialization(self):
        for value in ("nan", "inf"):
            with self.subTest(value=value), self.assertRaisesRegex(
                SystemExit,
                "replay speed must be positive",
            ):
                app.main(["--replay-speed", value, "--no-auto-connect"])


if __name__ == "__main__":
    unittest.main()
