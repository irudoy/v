"""Durable source publication and exact-file recovery for native KB writes.

The journal precedes every source mutation and stays until the enclosing
publication, including its graph synchronization, completes. Recovery restores
previous bytes only when every current file is one of the recorded states.
It does not accept a batch, relax a source gate, or roll back the derived graph.
"""

from contextlib import contextmanager
from contextvars import ContextVar
import base64
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import tempfile
import uuid

from kb import repo, vocab

PATH = repo.STATE / "publication.json"
_active = ContextVar("kb_source_publications", default={})


def pending(root=repo.ROOT):
    path = root / PATH
    return path.exists() or path.is_symlink()


def require_clean(root=repo.ROOT):
    if root.resolve() not in _active.get() and pending(root):
        raise repo.KbError(f"an incomplete KB publication is recorded in {PATH}; "
                           "run `uv run kb recover --status`, then `uv run kb recover`", code=6)


def _target(root, path):
    path = Path(path)
    owned = (len(path.parts) == 3 and path.parts[0] == "kb"
             and path.parts[1] in vocab.KINDS and path.suffix == ".toml")
    allowed = {Path("kb/names.csv"), repo.OWNER_CONFIG, repo.CONFIG, repo.HOMOLOGY,
               Path("rom-images/homology.csv")}
    interpolation = re.fullmatch(r"defs/registries/[A-Z0-9]+\.interp\.csv", path.as_posix()) is not None
    if path.is_absolute() or ".." in path.parts or not (owned or interpolation or path in allowed):
        raise repo.KbError(f"{path}: not a supported KB publication source", code=3)
    target = root / path
    _no_links(root, target)
    return target


def _no_links(root, target):
    current = root
    for part in target.relative_to(root).parts:
        current /= part
        if current.is_symlink():
            raise repo.KbError(f"{current.relative_to(root)}: a publication path is a symlink", code=3)


def _snapshot(target):
    try:
        metadata = target.lstat()
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(metadata.st_mode):
        raise repo.KbError(f"{target}: a publication source is not a regular file", code=3)
    return {"data": base64.b64encode(target.read_bytes()).decode("ascii"),
            "mode": stat.S_IMODE(metadata.st_mode)}


def _state(snapshot):
    if snapshot is None:
        return None
    data = base64.b64decode(snapshot["data"], validate=True)
    return {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data), "mode": snapshot["mode"]}


def _sync_directory(directory):
    descriptor = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _replace(target, data, mode):
    """One durable replacement; an interrupted publication retains its journal."""
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(dir=target.parent, prefix=f".{target.name}.")
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(data)
            os.fchmod(output.fileno(), mode)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, target)
        _sync_directory(target.parent)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _remove(target):
    if target.exists():
        target.unlink()
        _sync_directory(target.parent)


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate journal key {key!r}")
        result[key] = value
    return result


class Publication:
    def __init__(self, root, document=None):
        from kb import lock
        self.root = root.resolve()
        self.document = document or {"version": 2, "root": str(self.root),
                                     "id": uuid.uuid4().hex, "entries": {},
                                     "lock_timeout": lock.publication_timeout(self.root)}

    def save(self):
        target = self.root / PATH
        _no_links(self.root, target)
        _replace(target, (json.dumps(self.document, sort_keys=True) + "\n").encode(), 0o600)

    def register(self, changes):
        entries = self.document["entries"]
        for path, text in sorted(changes.items(), key=lambda item: str(item[0])):
            target = _target(self.root, path)
            key = target.relative_to(self.root).as_posix()
            current = _snapshot(target)
            if key not in entries:
                entries[key] = {"before": current, "states": [_state(current)]}
            elif _state(current) not in entries[key]["states"]:
                raise repo.KbError(f"{key}: changes outside the active publication; "
                                   "the recovery journal is retained", code=3)
            mode = current["mode"] if current is not None else 0o644
            after = None if text is None else {"data": base64.b64encode(text.encode("utf-8")).decode(),
                                                "mode": mode}
            state = _state(after)
            if state not in entries[key]["states"]:
                entries[key]["states"].append(state)
        self.save()

    def write(self, changes):
        for path, text in sorted(changes.items(), key=lambda item: str(item[0])):
            target = _target(self.root, path)
            entry = self.document["entries"][target.relative_to(self.root).as_posix()]
            current = _snapshot(target)
            if _state(current) not in entry["states"]:
                raise repo.KbError(f"{path}: changes outside the active publication; "
                                   "the recovery journal is retained", code=3)
            if text is None:
                _remove(target)
            else:
                _replace(target, text.encode("utf-8"), current["mode"] if current else 0o644)

    def conflicts(self):
        conflicts = []
        for path, entry in sorted(self.document["entries"].items()):
            try:
                current = _state(_snapshot(_target(self.root, path)))
                if current not in entry["states"]:
                    conflicts.append(f"{path}: current content or mode is outside the publication; "
                                     "preserve the edit separately, return this path to a recorded "
                                     "state and retry `uv run kb recover`; reapply the edit through "
                                     "a KB batch after recovery; do not delete the journal")
            except (OSError, repo.KbError) as error:
                conflicts.append(f"{path}: {error}")
        return conflicts

    def restore(self):
        conflicts = self.conflicts()
        if conflicts:
            raise repo.KbError("recovery refuses external changes; nothing is restored:\n"
                               + "\n".join(conflicts), code=3)
        for path, entry in sorted(self.document["entries"].items()):
            target = _target(self.root, path)
            current = _snapshot(target)
            if _state(current) not in entry["states"]:
                raise repo.KbError(f"{path}: changes during recovery; journal retained", code=3)
            before = entry["before"]
            if current == before:
                continue
            if before is None:
                _remove(target)
            else:
                _replace(target, base64.b64decode(before["data"], validate=True), before["mode"])
        self.finish()

    def finish(self):
        _remove(self.root / PATH)


def _load(root):
    root = root.resolve()
    target = root / PATH
    _no_links(root, target)
    try:
        document = json.loads(target.read_text(encoding="utf-8"), object_pairs_hook=_unique)
        if (isinstance(document, dict) and type(document.get("version")) is int
                and document["version"] == 1
                and set(document) == {"version", "root", "id", "entries"}):
            document = {**document, "lock_timeout": 300}
        if (set(document) != {"version", "root", "id", "entries", "lock_timeout"}
                or type(document["version"]) is not int or document["version"] not in (1, 2)
                or document["root"] != str(root)
                or not isinstance(document["id"], str)
                or re.fullmatch(r"[0-9a-f]{32}", document["id"]) is None
                or type(document["lock_timeout"]) not in (int, float)
                or not math.isfinite(document["lock_timeout"]) or document["lock_timeout"] < 0
                or not isinstance(document["entries"], dict) or not document["entries"]):
            raise ValueError("invalid header")
        for path, entry in document["entries"].items():
            if str(Path(path)) != path:
                raise ValueError("noncanonical path")
            _target(root, path)
            if set(entry) != {"before", "states"} or not isinstance(entry["states"], list):
                raise ValueError("invalid entry")
            before = entry["before"]
            if before is not None and (set(before) != {"data", "mode"}
                    or not isinstance(before["data"], str)
                    or type(before["mode"]) is not int or not 0 <= before["mode"] <= 0o7777):
                raise ValueError("invalid previous state")
            for state in entry["states"]:
                if state is not None and (set(state) != {"sha256", "bytes", "mode"}
                        or not isinstance(state["sha256"], str)
                        or re.fullmatch(r"[0-9a-f]{64}", state["sha256"]) is None
                        or type(state["bytes"]) is not int or state["bytes"] < 0
                        or type(state["mode"]) is not int or not 0 <= state["mode"] <= 0o7777):
                    raise ValueError("invalid produced state")
            if _state(before) not in entry["states"]:
                raise ValueError("previous state is not admitted")
    except (ValueError, TypeError, KeyError, OSError, OverflowError) as error:
        raise repo.KbError(f"{PATH}: invalid recovery journal ({error}); retained", code=6) from None
    return Publication(root, document)


def wait_timeout(root=repo.ROOT):
    """Read the publisher's setting instead of a possibly partial config."""
    if not pending(root):
        return None
    try:
        return _load(root).document["lock_timeout"]
    except repo.KbError:
        # The live publisher may have removed its journal during this read.
        if pending(root):
            raise
        return None


@contextmanager
def transaction(root, changes):
    """Keep a source journal through the caller's complete publication.

    The caller owns the KB lock. Nested writes join the existing publication,
    so name enrollment during graph sync records its previous state too.
    """
    if not changes:
        yield None
        return
    root = root.resolve()
    held = _active.get().get(root)
    if held is not None:
        held.register(changes)
        yield held
        return
    require_clean(root)
    publication = Publication(root)
    token = None
    try:
        publication.register(changes)
        token = _active.set({**_active.get(), root: publication})
        yield publication
        publication.finish()
    except OSError as error:
        raise repo.KbError(f"KB publication failed ({error}); inspect {PATH} with "
                           "`uv run kb recover --status`", code=6) from error
    finally:
        if token is not None:
            _active.reset(token)


def recover(root=repo.ROOT, *, dry_run=False, status=False):
    """Inspect or restore the recorded previous files under the ordinary lock."""
    from kb import compile, lock
    with lock.held(root, recovery=True):
        if not pending(root):
            return {"id": None, "paths": [], "conflicts": []}
        publication = _load(root)
        result = {"id": publication.document["id"],
                  "paths": sorted(publication.document["entries"]),
                  "conflicts": publication.conflicts()}
        if not status:
            if result["conflicts"]:
                raise repo.KbError("recovery refuses external changes; nothing is restored:\n"
                                   + "\n".join(result["conflicts"]), code=3)
            if not dry_run:
                try:
                    publication.restore()
                except OSError as error:
                    state = ('journal retained' if pending(root) else
                             'previous files restored; inspect journal status')
                    raise repo.KbError(f"recovery failed ({error}); {state}", code=6) from error
                compile.cached.cache_clear()
        return result
