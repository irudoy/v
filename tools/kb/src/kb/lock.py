"""The lock that serializes syncs and writes in a working tree
(tools/kb/SPEC.md, section 9.6)."""

from contextlib import contextmanager
from contextvars import ContextVar
import fcntl
import json
import os
import shlex
import sys
import time
import uuid

from kb import repo

PATH = repo.STATE / "lock"
POLL = 0.2
_holders = ContextVar("kb_lock_holders", default={})


class _Holder:
    def __init__(self, handle):
        self.handle = handle
        self.state = dict(version=1, pid=os.getpid(), token=uuid.uuid4().hex,
                          command=list(sys.argv), operation=None, stage="", progress=0)
        self.publish()

    def publish(self):
        self.handle.seek(0)
        self.handle.truncate()
        self.handle.write(json.dumps(self.state) + "\n")
        self.handle.flush()

    def advance(self, operation, stage):
        self.state.update(operation=operation, stage=stage, progress=self.state["progress"] + 1)
        self.publish()


def _status(handle):
    handle.seek(0)
    text = ""
    try:
        text = handle.read().strip()
        state = json.loads(text)
    except (ValueError, TypeError):
        state = None
    if (not isinstance(state, dict) or type(state.get("version")) is not int
            or state["version"] != 1
            or type(state.get("pid")) is not int or state["pid"] <= 0
            or not isinstance(state.get("token"), str) or not state["token"]
            or not isinstance(state.get("command"), list)
            or not all(isinstance(item, str) for item in state["command"])
            or "operation" not in state or state["operation"] not in (None, "sync")
            or not isinstance(state.get("stage"), str)
            or state["operation"] == "sync" and not state["stage"]
            or type(state.get("progress")) is not int or state["progress"] < 0):
        return None, text if text.startswith("pid ") else "another process (no valid lock status)"
    description = f"pid {state['pid']}: {shlex.join(state['command'])}"
    if state["operation"] == "sync":
        description += f"; graph sync: {state['stage']}"
    return state, description


@contextmanager
def syncing(root=repo.ROOT, stage="compiling sources"):
    """Publish graph reload stages only for the lock owned by this context.

    Each call to the yielded function records actual progress, not a timer
    heartbeat. Callers without an owned lock retain a no-op callback.
    """
    holder = _holders.get().get(root.resolve())
    if holder is None:
        yield lambda stage: None
        return
    previous = holder.state["operation"], holder.state["stage"]
    holder.advance("sync", stage)
    try:
        yield lambda stage: holder.advance("sync", stage)
    finally:
        holder.advance(*previous)


def timeout_of(root=repo.ROOT):
    return repo.config(root)["lock"]["timeout"]


@contextmanager
def held(root=repo.ROOT, timeout=None, log=sys.stderr):
    """Hold `.kb/lock`; renew a wait on progress of the same graph sync.

    Ordinary contention and a sync without progress fail with code 7 after
    the configured timeout. Holder and stage changes are shown to waiters.
    """
    if timeout is None:
        timeout = timeout_of(root)
    path = root / PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", encoding="utf-8") as handle:
        deadline = time.monotonic() + timeout
        holder = None
        observed = None
        renewed = False
        while True:
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                state, description = _status(handle)
                now = time.monotonic()
                notice = holder is None
                if state is not None:
                    identity = state["pid"], state["token"]
                    if observed is None or observed[0] != identity:
                        notice = True
                        observed = identity, state["progress"]
                    elif state["progress"] > observed[1]:
                        observed = identity, state["progress"]
                        if state["operation"] == "sync":
                            deadline = now + timeout
                            renewed = True
                            notice = True
                if state is not None or holder is None or description.startswith("pid "):
                    holder = description
                if notice:
                    print(f"kb: waiting for {PATH}, held by {holder}", file=log, flush=True)
                if now >= deadline:
                    reason = (f"no new graph-sync progress for {timeout} s"
                              if renewed or state is not None and state["operation"] == "sync"
                              else f"gave up after {timeout} s")
                    raise repo.KbError(
                        f"{PATH} is held by {holder}; {reason}", code=7
                    ) from None
                time.sleep(POLL)
        state = _Holder(handle)
        token = _holders.set({**_holders.get(), root.resolve(): state})
        try:
            yield
        finally:
            _holders.reset(token)
            handle.seek(0)
            handle.truncate()
            handle.flush()
            fcntl.flock(handle, fcntl.LOCK_UN)
