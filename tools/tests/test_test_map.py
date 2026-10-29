"""The test map of `make test-changed` reaches every test directory, covers the
imports of every test, and selects tests from the changed paths."""

import ast
import subprocess
import sys
import tomllib
from collections import defaultdict
from pathlib import Path

import pytest

from tools import changed_tests

ROOT = Path(__file__).resolve().parents[2]
JS_TESTS = "tools/pin-tracer/tests"
SUBSYSTEMS = changed_tests.load_map()


def _tracked(*patterns):
    return subprocess.run(
        ["git", "ls-files", *patterns], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.split()


def _testpaths():
    with (ROOT / "pyproject.toml").open("rb") as source:
        return set(tomllib.load(source)["tool"]["pytest"]["ini_options"]["testpaths"])


def _test_directory(path):
    return path.split("/tests/")[0] + "/tests"


PYTHON = set(_tracked("patches/*.py", "tools/*.py"))
BY_STEM = defaultdict(list)
for _path in PYTHON:
    BY_STEM[Path(_path).stem].append(_path)


def _module_file(dotted):
    parts = dotted.split(".")
    base = "/".join(["tools", "kb", "src", *parts] if parts[0] == "kb" else parts)
    for candidate in (f"{base}.py", f"{base}/__init__.py"):
        if candidate in PYTHON:
            return candidate
    return None


def _imports(path):
    """Tracked modules that a file imports or names by its repository path."""
    tree = ast.parse((ROOT / path).read_text(encoding="utf-8"))
    found = set()
    for node in ast.walk(tree):
        names = []
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if node.level:
                package = Path(path).parents[node.level - 1]
                module = ".".join([*package.parts, *([module] if module else [])])
            names = [module, *(f"{module}.{alias.name}" for alias in node.names)]
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value in PYTHON:
            found.add(node.value)
        for name in names:
            target = _module_file(name)
            if target is None and name and "." not in name and name not in sys.stdlib_module_names:
                # A bare name resolves beside the importer or in a sys.path tool directory.
                beside = str(Path(path).parent / f"{name}.py")
                if beside in PYTHON:
                    target = beside
                elif len(BY_STEM.get(name, ())) == 1:
                    (target,) = BY_STEM[name]
            if target:
                found.add(target)
                parent = Path(target).parent
                while parent.parts:
                    if (init := str(parent / "__init__.py")) in PYTHON:
                        found.add(init)
                    parent = parent.parent
    found.discard(path)
    return found


def _closure(paths, graph):
    seen = set(paths)
    stack = list(paths)
    while stack:
        for other in graph.get(stack.pop(), ()):
            if other not in seen:
                seen.add(other)
                stack.append(other)
    return seen


def test_every_test_directory_is_reachable():
    directories = {_test_directory(path) for path in _tracked("patches", "tools") if "/tests/" in path}
    assert directories == _testpaths() | {JS_TESTS}
    assert {directory for subsystem in SUBSYSTEMS for directory in subsystem.pytest} == _testpaths()
    for directory in _testpaths():
        files = [path for path in _tracked(f"{directory}/*") if path.endswith(".py")]
        selection = changed_tests.select(files, SUBSYSTEMS)
        assert not selection.unmapped, directory
        assert directory in selection.pytest
    pin_tracer = changed_tests.select(_tracked(f"{JS_TESTS}/*"), SUBSYSTEMS)
    assert pin_tracer.js and not pin_tracer.unmapped


def test_every_mapped_module_selects_the_tests_that_import_it():
    graph = {}
    for path in PYTHON:
        graph[path] = _imports(path)
    missing = []
    for test in sorted(path for path in PYTHON if "/tests/" in path):
        directory = _test_directory(test)
        roots = {test} | {
            str(parent / "conftest.py")
            for parent in Path(test).parents
            if str(parent / "conftest.py") in PYTHON
        }
        for module in sorted(_closure(roots, graph) - {test}):
            selection = changed_tests.select([module], SUBSYSTEMS)
            if not selection.unmapped and directory not in selection.pytest:
                missing.append(f"{module} -> {directory} (via {test})")
    assert not missing, "\n".join(missing)


def test_one_subsystem_selects_only_its_tests():
    selection = changed_tests.select(
        ["tools/vendor/build_catalog.py", "tools/tests/test_vendor_catalog.py"], SUBSYSTEMS
    )
    assert selection == changed_tests.Selection(("tools/tests",), False, ())
    tests_only = changed_tests.select(["tools/memgraph/tests/test_example.py"], SUBSYSTEMS)
    assert tests_only == changed_tests.Selection(("tools/memgraph/tests",), False, ())
    pin_tracer = changed_tests.select(["tools/pin-tracer/index.html"], SUBSYSTEMS)
    assert pin_tracer == changed_tests.Selection((), True, ())


def test_runtime_data_selects_the_complete_fast_contract():
    paths = (
        "kb/fn/juicy-panther.toml",
        "kb/fn/rousing-rhino.toml",
        "kb/ram/fuel_learning_permit_a.toml",
        "kb/feature/can_telemetry.toml",
        "kb/tbl/precise-nuthatch.toml",
        "tools/kb/owners.toml",
        "defs/JK08A.architecture.toml",
        "patches/jk78c-runtime-correspondence.csv",
        "patches/1nd-runtime-correspondence.csv",
        "patches/rom-address-profiles.toml",
        "patches/runtime-target-payloads.toml",
        "rom-images/support-matrix.md",
    )
    for path in paths:
        selection = changed_tests.select([path], SUBSYSTEMS)
        assert not selection.unmapped, path
        assert set(selection.pytest) == _testpaths(), path
        assert selection.js, path


def test_patterns_keep_single_star_within_a_segment():
    assert changed_tests.glob_pattern("tools/kb/src/**/*.py").fullmatch("tools/kb/src/kb/adapters/files.py")
    assert changed_tests.glob_pattern("tools/kb/src/**/*.py").fullmatch("tools/kb/src/top.py")
    assert not changed_tests.glob_pattern("tools/mapkit/*.py").fullmatch("tools/mapkit/tests/test_rom.py")
    assert changed_tests.glob_pattern("patches/tests/**").fullmatch("patches/tests/fixtures/a.bin")


def test_malformed_map_is_refused(tmp_path):
    path = tmp_path / "map.toml"
    path.write_text('[[subsystem]]\nname = "a"\npaths = ["a/*.py"]\n', encoding="utf-8")
    with pytest.raises(changed_tests.MapError, match="selects no tests"):
        changed_tests.load_map(path)
    path.write_text(
        '[[subsystem]]\nname = "a"\npaths = ["a/*"]\npytest = ["a"]\n'
        '[[subsystem]]\nname = "a"\npaths = ["b/*"]\npytest = ["b"]\n',
        encoding="utf-8",
    )
    with pytest.raises(changed_tests.MapError, match="missing or repeated"):
        changed_tests.load_map(path)


class _Calls:
    def __init__(self, capsys):
        self.capsys = capsys
        self.runs = []

    def __call__(self, command, cwd):
        self.runs.append((command, self.capsys.readouterr().out))
        return 0


def test_unmapped_path_is_named_and_falls_back_to_make_test(monkeypatch, capsys):
    monkeypatch.setattr(
        changed_tests, "changed_paths", lambda base: ("pyproject.toml", "tools/diagnostics/catalog.py")
    )
    calls = _Calls(capsys)
    monkeypatch.setattr(changed_tests.subprocess, "call", calls)
    assert changed_tests.main([]) == 0
    ((command, printed),) = calls.runs
    assert command == ["make", "test"]
    assert "test-changed: unmapped path pyproject.toml\n" in printed
    assert "unmapped path tools/diagnostics/catalog.py" not in printed
    assert printed.endswith("test-changed: running make test\n")


def test_selected_directories_are_printed_before_they_run(monkeypatch, capsys):
    monkeypatch.setattr(
        changed_tests, "changed_paths", lambda base: ("tools/vendor/build_catalog.py", "tools/pin-tracer/model.js")
    )
    calls = _Calls(capsys)
    monkeypatch.setattr(changed_tests.subprocess, "call", calls)
    assert changed_tests.main(["--pytest", "uv run pytest"]) == 0
    (pytest_command, printed), (npm_command, _) = calls.runs
    assert pytest_command == ["uv", "run", "pytest", "-q", "-m", "not slow", "tools/tests"]
    assert npm_command == ["npm", "--prefix", "tools/pin-tracer", "test"]
    assert "test-changed: pytest tools/tests\n" in printed
    assert "test-changed: pin-tracer contract\n" in printed


def _repository(path):
    def git(*arguments):
        subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid",
             "-c", "commit.gpgsign=false", *arguments],
            cwd=path, check=True, capture_output=True,
        )

    git("init", "-q")
    (path / ".gitignore").write_text("*.log\n", encoding="utf-8")
    (path / "base.txt").write_text("base\n", encoding="utf-8")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    git("update-ref", "refs/remotes/origin/master", "HEAD")
    return git


def test_changed_paths_join_commits_index_worktree_and_untracked(tmp_path):
    git = _repository(tmp_path)
    (tmp_path / "committed.txt").write_text("c\n", encoding="utf-8")
    git("add", "committed.txt")
    git("commit", "-q", "-m", "next")
    (tmp_path / "base.txt").write_text("edited\n", encoding="utf-8")
    (tmp_path / "staged.txt").write_text("s\n", encoding="utf-8")
    git("add", "staged.txt")
    (tmp_path / "untracked.txt").write_text("u\n", encoding="utf-8")
    (tmp_path / "ignored.log").write_text("i\n", encoding="utf-8")
    assert changed_tests.changed_paths(root=tmp_path) == (
        "base.txt", "committed.txt", "staged.txt", "untracked.txt",
    )


def test_missing_base_is_refused(tmp_path):
    _repository(tmp_path)
    with pytest.raises(changed_tests.MapError, match="rev-parse"):
        changed_tests.changed_paths(base="refs/remotes/origin/absent", root=tmp_path)
