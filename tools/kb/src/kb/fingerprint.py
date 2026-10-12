"""The fingerprint of the compiler inputs (tools/kb/SPEC.md, section 9.4).

The fingerprint is the SHA-256 of the sorted (path, git blob hash) pairs of
every file input and the pinned reference checkout identity, followed by the
compiler and schema versions. It covers the
working tree: a modified input contributes the blob hash of its current
content. `.kb/cache/hashes.json` keeps the hash of each input with its size
and modification time, so a hash is recomputed only for a changed file.
"""

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import subprocess

import kb
from kb import compile, repo

CACHE = repo.STATE / "cache" / "hashes.json"
ABSENT = "absent"


def blob(data):
    """The git blob hash of file content."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def inputs(root=repo.ROOT):
    """Every input path of the compiler: the model inputs, the L0 of every
    layout, and the images of the catalog."""
    found = set(compile.inputs(root))
    from kb import compatibility
    found.update(compatibility.FRAMEWORK)
    for layout in repo.layouts(root):
        base = root / repo.L0 / layout
        found.update(path.relative_to(root).as_posix()
                     for path in base.iterdir() if path.is_file())
    for image in repo.images(root).values():
        found.add(image.path.relative_to(root).as_posix())
    return sorted(found)


class Hashes:
    """Blob hashes of working-tree files, cached by size and modification time."""

    def __init__(self, root=repo.ROOT):
        self.root = root
        self.path = root / CACHE
        try:
            self.entries = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self.entries = {}
        self.changed = False

    def of(self, path):
        full = self.root / path
        try:
            stat = full.stat()
        except FileNotFoundError:
            return ABSENT
        entry = self.entries.get(path)
        if entry and entry[0] == stat.st_size and entry[1] == stat.st_mtime_ns:
            return entry[2]
        digest = blob(full.read_bytes())
        self.entries[path] = [stat.st_size, stat.st_mtime_ns, digest]
        self.changed = True
        return digest

    def save(self):
        if not self.changed:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(self.entries, sort_keys=True), encoding="utf-8")
        temporary.replace(self.path)
        self.changed = False


def digest(pairs):
    """SHA-256 of (path, blob) pairs followed by the compiler and schema versions."""
    text = "".join(f"{path}\t{value}\n" for path, value in sorted(pairs))
    text += f"compiler\t{kb.__version__}\nschema\t{compile.SCHEMA}\n"
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Fingerprint:
    value: str
    blobs: dict

    def part(self, predicate):
        """The digest of the inputs whose path satisfies the predicate."""
        return digest((path, value) for path, value in self.blobs.items() if predicate(path))


def compute(root=repo.ROOT):
    from kb import compatibility
    hashes = Hashes(root)
    blobs = {path: hashes.of(path) for path in inputs(root)}
    blobs[compatibility.PIN] = compatibility.reference_commit(root)
    hashes.save()
    return Fingerprint(digest(blobs.items()), blobs)


def _git(root, *args):
    result = subprocess.run(["git", *args], cwd=root, capture_output=True)
    if result.returncode != 0:
        raise repo.KbError(f"git {' '.join(args)}: {result.stderr.decode().strip()}")
    return result.stdout


def head(root=repo.ROOT):
    """The commit of HEAD and {path: blob hash} of its tree."""
    commit = _git(root, "rev-parse", "HEAD").decode().strip()
    blobs = {}
    for entry in _git(root, "ls-tree", "-r", "-z", "--full-tree", "HEAD").split(b"\0"):
        if not entry:
            continue
        meta, _, path = entry.partition(b"\t")
        mode, kind, value = meta.decode().split()
        if kind == "blob":
            blobs[path.decode()] = value
        elif kind == "commit":
            from kb import compatibility
            relative = Path(path.decode())
            if relative == compatibility.REFERENCE:
                blobs[compatibility.PIN] = value
                source = compatibility.A2L.relative_to(relative).as_posix()
                command = ["git", "-C", str(root / relative), "ls-tree", "-z", value, "--", source]
                result = subprocess.run(command, capture_output=True)
                if result.returncode:
                    raise repo.KbError(f"pinned A2L object is unavailable: {result.stderr.decode().strip()}")
                for row in result.stdout.split(b"\0"):
                    if row:
                        metadata, _, nested = row.partition(b"\t")
                        _, nested_kind, digest = metadata.decode().split()
                        if nested_kind == "blob":
                            blobs[(relative / nested.decode()).as_posix()] = digest
    return commit, blobs


def dirty(fingerprint, blobs):
    """Input paths whose working-tree content differs from HEAD."""
    return sorted(path for path, value in fingerprint.blobs.items() if blobs.get(path, ABSENT) != value)
