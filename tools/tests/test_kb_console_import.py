"""Installed console acceptance for primary exact-image preparation imports."""

import subprocess

import pytest

from kb import ghidra_preparation, l0, repo
from tools.ghidra import preparation


@pytest.mark.parametrize("arguments, expected", [
    (["--help"], "Knowledge model and entry point"),
    (["code", "--help"], "usage: kb code"),
    (["move", "--help"], "usage: kb move"),
])
def test_original_uv_console_imports_without_repository_pythonpath(arguments, expected):
    result = subprocess.run(["uv", "run", "kb", *arguments], cwd=repo.ROOT,
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    assert expected in result.stdout
    assert "ModuleNotFoundError" not in result.stderr


def test_primary_tools_and_installed_console_share_one_preparation_api():
    assert l0.preparation is ghidra_preparation
    for name in ("Plan", "Seed", "Fragment", "plan", "verify_stage", "verify_receipt",
                 "check_exports", "inputs", "promote_directory"):
        assert getattr(preparation, name) is getattr(ghidra_preparation, name)
    assert "tools/kb/src/kb/ghidra_preparation.py" in ghidra_preparation.BUILDERS
