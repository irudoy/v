#!/usr/bin/env python3
"""Run the fast tests of the subsystems that the changed paths touch.

The changed paths are those that differ from `origin/master` in the commits of
HEAD, in the index and the worktree, and the untracked paths that `.gitignore`
does not exclude. `tools/test-map.toml` maps them to test directories and the
pin-tracer contract. A path that no subsystem matches selects the complete
fast tier, `make test`. The selection is printed before it runs.
"""

import argparse
import re
import shlex
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "tools" / "test-map.toml"
BASE = "origin/master"


class MapError(Exception):
    """The test map is malformed."""


@dataclass(frozen=True)
class Subsystem:
    name: str
    paths: tuple[str, ...]
    pytest: tuple[str, ...]
    js: bool

    def matches(self, path):
        return any(glob_pattern(pattern).fullmatch(path) for pattern in self.paths)


@dataclass(frozen=True)
class Selection:
    pytest: tuple[str, ...]
    js: bool
    unmapped: tuple[str, ...]


def glob_pattern(pattern):
    """Compile a path glob: `*` and `?` stay within a segment, `**` spans segments."""
    parts = []
    index = 0
    while index < len(pattern):
        if pattern.startswith("**/", index):
            parts.append("(?:.*/)?")
            index += 3
        elif pattern.startswith("**", index):
            parts.append(".*")
            index += 2
        elif pattern[index] == "*":
            parts.append("[^/]*")
            index += 1
        elif pattern[index] == "?":
            parts.append("[^/]")
            index += 1
        else:
            parts.append(re.escape(pattern[index]))
            index += 1
    return re.compile("".join(parts))


def load_map(path=MAP):
    with path.open("rb") as source:
        entries = tomllib.load(source).get("subsystem", [])
    subsystems = []
    names = set()
    for entry in entries:
        name = entry.get("name")
        if not isinstance(name, str) or not name or name in names:
            raise MapError(f"{path}: subsystem name {name!r} is missing or repeated")
        names.add(name)
        paths = entry.get("paths", [])
        pytest = entry.get("pytest", [])
        js = entry.get("js", False)
        if not paths or not all(isinstance(item, str) and item for item in paths):
            raise MapError(f"{path}: subsystem {name!r} needs path patterns")
        if not all(isinstance(item, str) and item for item in pytest):
            raise MapError(f"{path}: subsystem {name!r} names an invalid test directory")
        if not isinstance(js, bool) or not (pytest or js):
            raise MapError(f"{path}: subsystem {name!r} selects no tests")
        unknown = set(entry) - {"name", "paths", "pytest", "js"}
        if unknown:
            raise MapError(f"{path}: subsystem {name!r} has unknown keys {sorted(unknown)}")
        subsystems.append(Subsystem(name, tuple(paths), tuple(pytest), js))
    if not subsystems:
        raise MapError(f"{path}: no subsystem is declared")
    return tuple(subsystems)


def select(paths, subsystems):
    pytest = set()
    js = False
    unmapped = []
    for path in paths:
        matched = [subsystem for subsystem in subsystems if subsystem.matches(path)]
        if not matched:
            unmapped.append(path)
        for subsystem in matched:
            pytest.update(subsystem.pytest)
            js = js or subsystem.js
    return Selection(tuple(sorted(pytest)), js, tuple(unmapped))


def _git(root, *arguments):
    result = subprocess.run(
        ["git", *arguments], cwd=root, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise MapError(f"git {' '.join(arguments)} failed: {result.stderr.strip()}")
    return result.stdout.splitlines()


def changed_paths(base=BASE, root=ROOT):
    _git(root, "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}")
    paths = set(_git(root, "diff", "--name-only", f"{base}...HEAD"))
    paths.update(_git(root, "diff", "--name-only", "HEAD"))
    paths.update(_git(root, "ls-files", "--others", "--exclude-standard"))
    return tuple(sorted(path for path in paths if path))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default=BASE, help="commit the changes are measured against")
    parser.add_argument("--pytest", default="uv run pytest", help="pytest command")
    parser.add_argument("--npm", default="npm", help="npm command")
    parser.add_argument("--make", default="make", help="make command for the fallback")
    parser.add_argument("--dry-run", action="store_true", help="print the selection only")
    args = parser.parse_args(argv)
    try:
        paths = changed_paths(args.base)
        selection = select(paths, load_map())
    except (OSError, MapError, tomllib.TOMLDecodeError) as error:
        print(f"test-changed: {error}", file=sys.stderr)
        return 2
    print(f"test-changed: {len(paths)} paths differ from {args.base}")
    if not paths:
        return 0
    if selection.unmapped:
        for path in selection.unmapped:
            print(f"test-changed: unmapped path {path}")
        print("test-changed: running make test")
        if args.dry_run:
            return 0
        return subprocess.call([*shlex.split(args.make), "test"], cwd=ROOT)
    for directory in selection.pytest:
        print(f"test-changed: pytest {directory}")
    if selection.js:
        print("test-changed: pin-tracer contract")
    if args.dry_run:
        return 0
    status = 0
    if selection.pytest:
        status = subprocess.call(
            [*shlex.split(args.pytest), "-q", "-m", "not slow", *selection.pytest], cwd=ROOT
        )
    if selection.js:
        status = subprocess.call(
            [*shlex.split(args.npm), "--prefix", "tools/pin-tracer", "test"], cwd=ROOT
        ) or status
    return status


if __name__ == "__main__":
    raise SystemExit(main())
