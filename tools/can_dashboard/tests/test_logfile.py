import logging
from pathlib import Path
import sys
import tempfile
import threading
import unittest

from tools.can_dashboard import logfile


def files(log):
    """Return the file handlers of a logger, ignoring handlers of the runner."""
    return [
        handler
        for handler in log.handlers
        if isinstance(handler, logging.FileHandler)
    ]


class DefaultPathTest(unittest.TestCase):
    def test_macos_keeps_the_log_beside_the_settings_file(self):
        path = logfile.default_path(
            "VQ CAN Telemetry",
            "vq-can-telemetry",
            platform="darwin",
            environ={"HOME": "/Users/operator"},
        )
        self.assertEqual(
            path,
            Path(
                "/Users/operator/Library/Application Support/"
                "VQ CAN Telemetry/vq-can-telemetry.log"
            ),
        )

    def test_windows_keeps_the_log_beside_the_settings_file(self):
        path = logfile.default_path(
            "VQ CAN Telemetry",
            "vq-can-telemetry",
            platform="win32",
            environ={"HOME": "/home/operator", "APPDATA": "/profile/Roaming"},
        )
        self.assertEqual(
            path,
            Path("/profile/Roaming/VQ CAN Telemetry/vq-can-telemetry.log"),
        )


class LogFileTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "logs" / logfile.FILE_NAME
        self.addCleanup(self.close)
        hooks = (sys.excepthook, threading.excepthook)
        self.addCleanup(self.restore, hooks)

    def close(self):
        log = logfile.logger()
        for handler in tuple(log.handlers):
            log.removeHandler(handler)
            handler.close()
        log.addHandler(logging.NullHandler())

    def restore(self, hooks):
        sys.excepthook, threading.excepthook = hooks

    def test_a_silent_logger_writes_nothing_before_a_file_is_configured(self):
        log = logfile.logger()
        self.assertEqual(files(log), [])
        log.info("dropped")
        self.assertFalse(self.path.exists())

    def test_the_configured_file_records_the_line_and_its_level(self):
        log = logfile.configure(self.path)
        log.info("start %s", "8.2.2")
        log.error("source error: no device")
        text = self.path.read_text(encoding="utf-8")
        self.assertIn("INFO start 8.2.2", text)
        self.assertIn("ERROR source error: no device", text)

    def test_rotation_bounds_the_log_to_the_file_and_its_backups(self):
        log = logfile.configure(self.path, max_bytes=1024, backup_count=2)
        for index in range(400):
            log.info("event %04d with enough text to fill the file", index)
        written = sorted(self.path.parent.iterdir())
        self.assertEqual(
            [entry.name for entry in written],
            [
                logfile.FILE_NAME,
                logfile.FILE_NAME + ".1",
                logfile.FILE_NAME + ".2",
            ],
        )
        total = sum(entry.stat().st_size for entry in written)
        self.assertLess(total, 3 * 1024 + 1024)

    def test_a_file_that_cannot_be_opened_leaves_the_logger_silent(self):
        blocked = Path(self.directory.name) / "blocked"
        blocked.write_text("not a directory\n", encoding="utf-8")
        log = logfile.configure(blocked / "sub" / logfile.FILE_NAME)
        self.assertEqual(files(log), [])
        log.error("dropped")

    def test_an_unhandled_exception_of_the_process_reaches_the_file(self):
        log = logfile.configure(self.path)
        logfile.install_hooks(log)
        try:
            raise ValueError("torn frame")
        except ValueError:
            sys.excepthook(*sys.exc_info())
        text = self.path.read_text(encoding="utf-8")
        self.assertIn("unhandled exception", text)
        self.assertIn("ValueError: torn frame", text)

    def test_an_unhandled_exception_of_a_thread_reaches_the_file(self):
        log = logfile.configure(self.path)
        logfile.install_hooks(log)

        def fail():
            raise RuntimeError("reader stopped")

        thread = threading.Thread(target=fail, name="source")
        thread.start()
        thread.join()
        text = self.path.read_text(encoding="utf-8")
        self.assertIn("unhandled exception in thread source", text)
        self.assertIn("RuntimeError: reader stopped", text)

    def test_a_tk_callback_exception_reaches_the_file(self):
        log = logfile.configure(self.path)

        class Root:
            pass

        root = Root()
        logfile.install_hooks(log, root)
        try:
            raise KeyError("panel")
        except KeyError:
            root.report_callback_exception(*sys.exc_info())
        self.assertIn("KeyError: 'panel'", self.path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
