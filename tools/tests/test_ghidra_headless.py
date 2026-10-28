"""Installation selection and process behavior of the headless entry point."""

import os
from pathlib import Path
import shutil
import subprocess

import pytest

from kb import repo

WRAPPER = repo.ROOT / "tools/ghidra/headless-analyze.sh"
BASH = shutil.which("bash")


def executable(path, source):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/bin/sh\n" + source)
    path.chmod(0o755)
    return path


@pytest.fixture
def installation(tmp_path):
    ghidra = tmp_path / "Ghidra tools" / "libexec"
    java = tmp_path / "JDK tools" / "libexec/openjdk.jdk/Contents/Home"
    properties = ghidra / "Ghidra/application.properties"
    properties.parent.mkdir(parents=True)
    properties.write_text(f"application.version={repo.ghidra_version()}\n")
    executable(ghidra / "support/analyzeHeadless",
               'printf "%s\\n" "$JAVA_HOME" "$@"\n'
               'exit "${GHIDRA_TEST_EXIT:-0}"\n')
    executable(java / "bin/java", "exit 0\n")
    binaries = tmp_path / "bin"
    binaries.mkdir()
    (binaries / "sed").symlink_to(shutil.which("sed"))
    env = {k: v for k, v in os.environ.items() if k not in {"GHIDRA_HOME", "JAVA_HOME"}}
    env["PATH"] = str(binaries)
    return ghidra, java, env


def run(env, *arguments):
    return subprocess.run([BASH, str(WRAPPER), *arguments], env=env,
                          capture_output=True, text=True, timeout=10)


def brew(installation):
    ghidra, java, env = installation
    log = Path(env["PATH"]) / "brew-calls"
    env.update(GHIDRA_TEST_BREW_LOG=str(log),
               GHIDRA_TEST_GHIDRA_PREFIX=str(ghidra.parent),
               GHIDRA_TEST_JAVA_PREFIX=str(java.parents[3]))
    executable(Path(env["PATH"]) / "brew",
               'printf "%s\\n" "$*" >> "$GHIDRA_TEST_BREW_LOG"\n'
               'case "$*" in\n'
               '  "--prefix ghidra") printf "%s\\n" "$GHIDRA_TEST_GHIDRA_PREFIX" ;;\n'
               '  "--prefix openjdk@21") printf "%s\\n" "$GHIDRA_TEST_JAVA_PREFIX" ;;\n'
               '  *) exit 99 ;;\n'
               'esac\n')
    return log


def test_explicit_installations_preserve_paths_and_arguments_without_homebrew(installation):
    ghidra, java, env = installation
    env.update(GHIDRA_HOME=str(ghidra), JAVA_HOME=str(java))
    arguments = ["project directory", "project", "-readOnly", "-postScript", "a b.java", ""]
    result = run(env, *arguments)
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [str(java), *arguments]


def test_headless_exit_status_reaches_the_caller(installation):
    ghidra, java, env = installation
    env.update(GHIDRA_HOME=str(ghidra), JAVA_HOME=str(java), GHIDRA_TEST_EXIT="23")
    assert run(env).returncode == 23


def test_unset_paths_select_both_homebrew_installations(installation):
    _, java, env = installation
    log = brew(installation)
    result = run(env, "project")
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [str(java), "project"]
    assert log.read_text().splitlines() == ["--prefix ghidra", "--prefix openjdk@21"]


@pytest.mark.parametrize("provided, expected_call", [
    ("GHIDRA_HOME", "--prefix openjdk@21"),
    ("JAVA_HOME", "--prefix ghidra"),
])
def test_only_the_unset_path_uses_homebrew(installation, provided, expected_call):
    ghidra, java, env = installation
    log = brew(installation)
    env[provided] = str(ghidra if provided == "GHIDRA_HOME" else java)
    result = run(env, "project")
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [str(java), "project"]
    assert log.read_text().splitlines() == [expected_call]


@pytest.mark.parametrize("invalid", ["properties", "launcher", "version"])
def test_invalid_explicit_ghidra_is_rejected_without_homebrew(installation, invalid):
    ghidra, java, env = installation
    env.update(GHIDRA_HOME=str(ghidra), JAVA_HOME=str(java))
    properties = ghidra / "Ghidra/application.properties"
    if invalid == "version":
        properties.write_text("application.version=0.0\n")
    else:
        (properties if invalid == "properties" else ghidra / "support/analyzeHeadless").unlink()
    result = run(env)
    assert result.returncode != 0
    assert result.stdout == ""
    expected = "required" if invalid == "version" else "GHIDRA_HOME"
    assert expected in result.stderr
    assert "Homebrew" not in result.stderr


def test_invalid_explicit_jdk_is_rejected_without_homebrew(installation):
    ghidra, java, env = installation
    env.update(GHIDRA_HOME=str(ghidra), JAVA_HOME=str(java))
    (java / "bin/java").unlink()
    result = run(env)
    assert result.returncode != 0
    assert result.stdout == ""
    assert "JAVA_HOME" in result.stderr
    assert "Homebrew" not in result.stderr


@pytest.mark.parametrize("provided", ["GHIDRA_HOME", "JAVA_HOME"])
def test_missing_homebrew_requests_explicit_paths(installation, provided):
    ghidra, java, env = installation
    env[provided] = str(ghidra if provided == "GHIDRA_HOME" else java)
    result = run(env)
    assert result.returncode != 0
    assert result.stdout == ""
    assert "set GHIDRA_HOME and JAVA_HOME explicitly" in result.stderr
