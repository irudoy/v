"""End a pytest run whose fast test blocks, with the stack of every thread.

Each test without the ``slow`` marker arms the faulthandler watchdog for
``fast_test_timeout`` seconds. When a test exceeds it, the watchdog thread
writes the traceback of every Python thread, which names the test file and
function, to the original standard error and ends the process with status 1.
The watchdog is a C thread and does not need the GIL, so it also fires while
the test waits in a system call, such as on a blocked child process.

The ``slow`` integration checks of the full tier keep no limit. The process
has one faulthandler watchdog, which the pytest faulthandler plugin arms when
``faulthandler_timeout`` is set; that setting therefore excludes this one.
"""

import faulthandler
import os
import sys

import pytest

TIMEOUT = pytest.StashKey[float]()
STDERR = pytest.StashKey[int]()


def pytest_addoption(parser):
    parser.addini(
        "fast_test_timeout",
        "seconds after which a test without the slow marker dumps every thread "
        "stack and ends the run with status 1; 0 disables the limit",
        default="0",
    )


def pytest_configure(config):
    timeout = float(config.getini("fast_test_timeout") or 0)
    if timeout < 0:
        raise pytest.UsageError("fast_test_timeout must not be negative")
    if timeout and float(config.getini("faulthandler_timeout") or 0):
        raise pytest.UsageError(
            "fast_test_timeout and faulthandler_timeout both arm the one "
            "faulthandler watchdog of the process; set one of them to 0"
        )
    config.stash[TIMEOUT] = timeout
    if timeout:
        # Output capture replaces descriptor 2 during a test, and the watchdog
        # ends the process without restoring it, so it writes to a copy.
        config.stash[STDERR] = os.dup(sys.__stderr__.fileno())


def pytest_unconfigure(config):
    if STDERR in config.stash:
        os.close(config.stash[STDERR])
        del config.stash[STDERR]


@pytest.hookimpl(wrapper=True)
def pytest_runtest_protocol(item):
    timeout = item.config.stash.get(TIMEOUT, 0)
    if not timeout or item.get_closest_marker("slow") is not None:
        return (yield)
    faulthandler.dump_traceback_later(
        timeout, file=item.config.stash[STDERR], exit=True
    )
    try:
        return (yield)
    finally:
        faulthandler.cancel_dump_traceback_later()
