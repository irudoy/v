"""Callback recovery and smoke failures without a display or CAN device."""

import contextlib
import io
import subprocess
import sys
import threading
import types
import unittest
from unittest import mock

from tools.can_dashboard.tests.tk_support import require_tk

require_tk()

from tools.can_dashboard import app


class CallbackTimerTest(unittest.TestCase):
    def dashboard(self):
        dashboard = object.__new__(app.DashboardApp)
        dashboard.closed = False
        dashboard.events = app.queue.Queue()
        dashboard.source_generation = 1
        dashboard.feed = None
        dashboard.recorder = None
        dashboard.model = types.SimpleNamespace(process_frame=mock.Mock())
        dashboard.error_var = types.SimpleNamespace(set=mock.Mock())
        dashboard.root = types.SimpleNamespace(
            after=mock.Mock(), report_callback_exception=mock.Mock(),
        )
        return dashboard

    def test_event_error_is_visible_and_the_next_tick_processes_more_events(self):
        dashboard = self.dashboard()
        error = ValueError("invalid event")
        dashboard.model.process_frame.side_effect = [error, None]
        for index in range(2):
            dashboard.events.put(app.SourceEnvelope(1, app.FrameRecord(0x6F0, bytes(8), index)))

        dashboard._poll()

        dashboard.root.after.assert_called_once_with(app.POLL_INTERVAL_MS, dashboard._poll)
        self.assertIn("invalid event", dashboard.error_var.set.call_args.args[0])
        self.assertIs(dashboard.root.report_callback_exception.call_args.args[1], error)
        dashboard.root.after.call_args.args[1]()
        self.assertEqual(dashboard.model.process_frame.call_count, 2)
        self.assertTrue(dashboard.events.empty())

    def test_render_error_is_visible_and_the_next_tick_paints(self):
        dashboard = self.dashboard()
        error = RuntimeError("panel paint failed")
        dashboard._refresh = mock.Mock(side_effect=[error, None])

        dashboard._refresh_tick()

        dashboard.root.after.assert_called_once_with(app.REFRESH_INTERVAL_MS, dashboard._refresh_tick)
        self.assertIn("panel paint failed", dashboard.error_var.set.call_args.args[0])
        self.assertIs(dashboard.root.report_callback_exception.call_args.args[1], error)
        dashboard.root.after.call_args.args[1]()
        self.assertEqual(dashboard._refresh.call_count, 2)

    def test_closed_window_does_not_schedule_another_tick(self):
        for method in ("_poll", "_refresh_tick"):
            with self.subTest(method=method):
                dashboard = self.dashboard()
                dashboard.closed = True
                dashboard._refresh = mock.Mock()
                getattr(dashboard, method)()
                dashboard.root.after.assert_not_called()
                dashboard._refresh.assert_not_called()

    def test_a_close_during_painting_prevents_rescheduling(self):
        dashboard = self.dashboard()
        dashboard._refresh = lambda _now: setattr(dashboard, "closed", True)
        dashboard._refresh_tick()
        dashboard.root.after.assert_not_called()


class SmokeFailureTest(unittest.TestCase):
    def setUp(self):
        hooks = (sys.excepthook, threading.excepthook)
        self.addCleanup(self.restore_hooks, hooks)

    @staticmethod
    def restore_hooks(hooks):
        sys.excepthook, threading.excepthook = hooks

    def run_smoke(self, *, callback_error=False, worker_error=False, groups=1):
        root = types.SimpleNamespace(withdraw=mock.Mock(), after=mock.Mock(), quit=mock.Mock())

        def mainloop():
            if callback_error:
                try:
                    raise RuntimeError("smoke callback failed")
                except RuntimeError:
                    root.report_callback_exception(*sys.exc_info())
            if worker_error:
                def fail():
                    raise RuntimeError("smoke worker failed")

                worker = threading.Thread(target=fail)
                worker.start()
                worker.join()

        root.mainloop = mainloop
        dashboard = types.SimpleNamespace(
            model=types.SimpleNamespace(stats=lambda _now: types.SimpleNamespace(completed_groups=groups)),
            close=mock.Mock(),
        )
        stderr = io.StringIO()
        with mock.patch.object(app.tk, "Tk", return_value=root), \
                mock.patch.object(app, "DashboardApp", return_value=dashboard), \
                mock.patch.object(app, "LOG", mock.Mock()), contextlib.redirect_stderr(stderr):
            try:
                result = app.main(["--smoke-test"])
            finally:
                dashboard.close.assert_called_once_with()
        return result

    def test_callback_error_fails_smoke_even_after_complete_groups(self):
        with self.assertRaisesRegex(SystemExit, "smoke.*exception|smoke.*error"):
            self.run_smoke(callback_error=True)

    def test_worker_error_fails_smoke_even_after_complete_groups(self):
        with self.assertRaisesRegex(SystemExit, "smoke.*exception"):
            self.run_smoke(worker_error=True)

    def test_successful_smoke_still_requires_completed_groups(self):
        self.assertEqual(self.run_smoke(), 0)
        with self.assertRaisesRegex(SystemExit, "no complete groups"):
            self.run_smoke(groups=0)

    def test_startup_exception_reaches_stderr_without_a_log_file(self):
        code = """
from types import SimpleNamespace
from tools.can_dashboard import app
app.tk.Tk = SimpleNamespace
def fail(*args):
    raise RuntimeError('startup construction failed')
app.DashboardApp = fail
app.main(['--no-log-file', '--no-auto-connect'])
"""
        result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("RuntimeError: startup construction failed", result.stderr)


if __name__ == "__main__":
    unittest.main()
