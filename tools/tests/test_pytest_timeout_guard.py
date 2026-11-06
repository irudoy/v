"""A blocked fast test ends the pytest run with its stack; slow checks keep no limit."""

import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]

BLOCKED = '''
import subprocess
import sys


def test_waits_on_a_blocked_child():
    subprocess.run(
        [sys.executable, "-c", "import time; time.sleep(20)"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
'''

BOUNDED = '''
import time

import pytest


def test_returns_within_the_limit():
    pass


@pytest.mark.slow
def test_slow_check_has_no_limit():
    time.sleep(3)
'''


def run(tmp_path, source, *options):
    (tmp_path / "pytest.ini").write_text(
        "[pytest]\nmarkers =\n    slow: integration checks\n", encoding="utf-8"
    )
    (tmp_path / "test_probe.py").write_text(source, encoding="utf-8")
    env = dict(os.environ, PYTHONPATH=str(ROOT))
    env.pop("PYTEST_ADDOPTS", None)
    started = time.monotonic()
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
         "-p", "tools.pytest_timeout_guard", *options, "test_probe.py"],
        cwd=tmp_path, env=env, capture_output=True, text=True, timeout=60,
    )
    return result, time.monotonic() - started


def test_a_blocked_fast_test_prints_its_stack_and_ends_the_run(tmp_path):
    result, elapsed = run(tmp_path, BLOCKED, "-o", "fast_test_timeout=1")
    assert result.returncode == 1
    assert elapsed < 15
    assert "Timeout (0:00:01)!" in result.stderr
    assert "test_probe.py" in result.stderr
    assert "in test_waits_on_a_blocked_child" in result.stderr


def test_a_slow_check_and_a_prompt_test_pass_under_the_limit(tmp_path):
    result, _elapsed = run(tmp_path, BOUNDED, "-o", "fast_test_timeout=1")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "2 passed" in result.stdout
    assert "Timeout" not in result.stderr


def test_the_limit_refuses_the_faulthandler_timeout(tmp_path):
    result, _elapsed = run(
        tmp_path, BOUNDED,
        "-o", "fast_test_timeout=1", "-o", "faulthandler_timeout=5",
    )
    assert result.returncode == 4
    assert "both arm the one faulthandler watchdog" in result.stderr
