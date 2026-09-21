"""Bounded log file of the telemetry dashboard.

The file records what an operator cannot see after the fact: the start of a
run, the state of the telemetry source, failures of the recording and of the
live value feed, and every exception that would otherwise reach a stream the
platform discards. The Windows launcher starts the application through
`pythonw.exe`, which has no console, so an unhandled exception leaves no
other trace.

The file never records telemetry values, so it grows with events and not with
the length of a run, and rotation bounds it: `MAX_BYTES` per file and
`BACKUP_COUNT` older files beside it.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys
import threading

from tools.can_dashboard import PRODUCT_SLUG
from tools.can_dashboard import settings as dashboard_settings


FILE_NAME = f"{PRODUCT_SLUG}.log"
LOGGER_NAME = PRODUCT_SLUG
MAX_BYTES = 512 * 1024
BACKUP_COUNT = 2
FORMAT = "%(asctime)s %(levelname)s %(message)s"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def logger():
    """Return the dashboard logger, silent until a file is configured."""
    log = logging.getLogger(LOGGER_NAME)
    log.propagate = False
    if not log.handlers:
        log.addHandler(logging.NullHandler())
    log.setLevel(logging.INFO)
    return log


def default_path(product_name, product_slug, *, platform=None, environ=None):
    """Return the per-user log file, beside the settings file."""
    return dashboard_settings.default_path(
        product_name,
        product_slug,
        platform=platform,
        environ=environ,
    ).with_name(FILE_NAME)


def configure(path, *, max_bytes=MAX_BYTES, backup_count=BACKUP_COUNT):
    """Send the dashboard log to a rotating file at path.

    A file that cannot be opened leaves the logger silent instead of ending
    the run, because the log is a diagnostic and not a function of the
    dashboard.
    """
    log = logger()
    for handler in tuple(log.handlers):
        log.removeHandler(handler)
        handler.close()
    path = Path(path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        handler = RotatingFileHandler(
            path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
    except OSError:
        log.addHandler(logging.NullHandler())
        return log
    handler.setFormatter(logging.Formatter(FORMAT, TIME_FORMAT))
    log.addHandler(handler)
    return log


def install_hooks(log, root=None):
    """Write unhandled exceptions of the process and of Tk to the log."""

    def on_exception(kind, value, traceback):
        log.error("unhandled exception", exc_info=(kind, value, traceback))

    sys.excepthook = on_exception

    def on_thread_exception(args):
        if args.exc_type is SystemExit:
            return
        log.error(
            "unhandled exception in thread %s",
            args.thread.name if args.thread is not None else "unknown",
            exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
        )

    threading.excepthook = on_thread_exception
    if root is not None:
        root.report_callback_exception = on_exception
