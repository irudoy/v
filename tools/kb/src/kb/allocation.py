"""Bound automatic collection to the boundaries of synchronous allocation."""

from functools import wraps
import gc
from threading import RLock

_LOCK = RLock()


def allocation_phase(function):
    """Run one independent phase with automatic GC paused, then restore its caller."""
    @wraps(function)
    def call(*args, **kwargs):
        with _LOCK:
            collecting = gc.isenabled()
            gc.disable()
            try:
                return function(*args, **kwargs)
            finally:
                (gc.enable if collecting else gc.disable)()
    return call
