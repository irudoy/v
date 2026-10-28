"""Capability checks before importing modules that require Tkinter."""

import unittest


def require_tk():
    try:
        import tkinter
    except ImportError as error:
        raise unittest.SkipTest(f"Tkinter is unavailable: {error}") from error
    return tkinter


def application_for_tests():
    """Skip only the tests that actually use the Tk-dependent application."""
    try:
        require_tk()
    except unittest.SkipTest as error:
        return _UnavailableApplication(str(error))
    from tools.can_dashboard import app
    return app


class _UnavailableApplication:
    def __init__(self, reason):
        self.reason = reason

    def __getattr__(self, name):
        raise unittest.SkipTest(self.reason)


def event_supported(widget, sequence):
    tk = require_tk()
    try:
        widget.event_generate(sequence, delta=0)
    except tk.TclError as error:
        if "bad event type or keysym" in str(error):
            return False
        raise
    return True
