"""The lock that serializes syncs and writes in a working tree
(tools/kb/SPEC.md, section 9.6)."""

from contextlib import contextmanager
import fcntl
import os
import sys
import time

from kb import repo

PATH = repo.STATE / "lock"
POLL = 0.2


def timeout_of(root=repo.ROOT):
    return repo.config(root)["lock"]["timeout"]


@contextmanager
def held(root=repo.ROOT, timeout=None, log=sys.stderr):
    """Hold `.kb/lock`; a waiting process prints the holder and gives up with
    exit code 7 after the timeout of tools/kb/config.toml."""
    if timeout is None:
        timeout = timeout_of(root)
    path = root / PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", encoding="utf-8") as handle:
        deadline = time.monotonic() + timeout
        holder = None
        while True:
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if holder is None:
                    handle.seek(0)
                    holder = handle.read().strip() or "another process"
                    print(f"kb: waiting for {PATH}, held by {holder}", file=log)
                if time.monotonic() >= deadline:
                    raise repo.KbError(
                        f"{PATH} is held by {holder}; gave up after {timeout} s", code=7
                    ) from None
                time.sleep(POLL)
        handle.seek(0)
        handle.truncate()
        handle.write(f"pid {os.getpid()}: {' '.join(sys.argv)}\n")
        handle.flush()
        try:
            yield
        finally:
            handle.seek(0)
            handle.truncate()
            handle.flush()
            fcntl.flock(handle, fcntl.LOCK_UN)
