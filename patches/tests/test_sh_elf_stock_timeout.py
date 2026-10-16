"""Declared stock limits preserve compilation and complete Region execution."""
from dataclasses import replace
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools/sh-elf-run"
SPEC = importlib.util.spec_from_file_location("stock_timeout_verifier", TOOL / "verify_stock_code.py")
stock = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = stock
SPEC.loader.exec_module(stock)
INVALID = ("", "0", "119", "121", "239", "241", "-1", "+240", "240 ",
           "120.0", "nan", "inf", "٢٤٠")


def test_stock_timeout_defaults_to_120(monkeypatch):
    monkeypatch.delenv(stock.STOCK_TIMEOUT_ENV, raising=False)
    assert stock.stock_execution_timeout() == 120


@pytest.mark.parametrize("value", ("120", "240"))
def test_stock_timeout_accepts_only_declared_limits(monkeypatch, value):
    monkeypatch.setenv(stock.STOCK_TIMEOUT_ENV, value)
    assert stock.stock_execution_timeout() == int(value)


@pytest.mark.parametrize("value", INVALID)
def test_stock_timeout_refuses_invalid_values_before_tools(monkeypatch, tmp_path, value):
    monkeypatch.setenv(stock.STOCK_TIMEOUT_ENV, value)
    calls = []
    monkeypatch.setattr(stock.base_verifier, "run_command", lambda *args, **kwargs: calls.append(args))
    with pytest.raises(stock.VerificationError, match="must be 120 or 240"):
        stock.run_region(SimpleNamespace(key="timeout-contract"), None, tmp_path)
    assert calls == []
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("value", ("120", "240"))
def test_stock_timeout_changes_only_simulator_wait(monkeypatch, tmp_path, value):
    monkeypatch.setenv(stock.STOCK_TIMEOUT_ENV, value)
    region = replace(stock.REGIONS[0], key="timeout-contract")
    marker = f"VQ_SH_ELF_STOCK_CODE status=PASS region={region.key} cases={region.cases}"
    calls = []

    def command(args, **options):
        calls.append((args, options))
        return SimpleNamespace(stdout=marker + "\n")

    monkeypatch.setattr(stock.base_verifier, "run_command", command)
    monkeypatch.setattr(stock, "stock_image", lambda rom: b"stock-image")
    monkeypatch.setattr(stock, "require_reconstruction", lambda *args: 33)
    monkeypatch.setattr(stock, "build_fixture", lambda *args: b"exact-fixture")
    monkeypatch.setattr(stock, "harness_defines", lambda *args: {})
    monkeypatch.setattr(stock, "require_separate_storage", lambda *args: None)
    invoke = tmp_path / "invoke.o"
    assert stock.run_region(region, invoke, tmp_path) == 33
    compiler = next((args, options) for args, options in calls if args[0] == stock.base_verifier.GCC)
    simulation = calls[-1]
    assert compiler[1] == {"timeout": 120}
    assert simulation[1] == {"timeout": int(value)}
    assert simulation[0] == [stock.base_verifier.RUN, "--memory-region=0x1000000,64k",
                             tmp_path / "timeout-contract-harness.elf"]
    assert (tmp_path / "timeout-contract.sim-fixture").read_bytes() == b"exact-fixture"
    assert invoke in compiler[0]


def runner_environment(tmp_path, value):
    directory = tmp_path / "bin"
    directory.mkdir()
    calls = tmp_path / "docker-calls.jsonl"
    checkout = tmp_path / "checkout"
    tool = checkout / "tools/sh-elf-run"
    tool.mkdir(parents=True)
    for filename in ('run.sh', 'docker_lifecycle.py'):
        target = tool / filename
        target.write_bytes((TOOL / filename).read_bytes())
        target.chmod((TOOL / filename).stat().st_mode)
    fake = directory / "docker"
    fake.write_text(f"#!{sys.executable}\n" +
        "import json,os,sys\nfrom pathlib import Path\n" +
        "with open(os.environ['VQ_TIMEOUT_TEST_CALLS'],'a') as out:\n" +
        " out.write(json.dumps(dict(args=sys.argv[1:],context=os.environ.get('DOCKER_CONTEXT'),host=os.environ.get('DOCKER_HOST')))+'\\n')\n" +
        "args=sys.argv[1:]\nassert args[:2]==['--context','default']\nargs=args[2:]\n" +
        "if args[0]=='image': print(json.dumps('sha256:'+'d'*64))\n" +
        "if args[0]=='run': Path(args[args.index('--cidfile')+1]).write_text('f'*64)\n")
    fake.chmod(0o755)
    environment = os.environ.copy()
    for name in (stock.STOCK_TIMEOUT_ENV, "VQ_SH_ELF_IMAGE", "VQ_SH_ELF_SKIP_BUILD"):
        environment.pop(name, None)
    environment.update(PATH=str(directory) + os.pathsep + environment["PATH"],
        VQ_TIMEOUT_TEST_CALLS=str(calls), DOCKER_CONTEXT="unrelated-context", DOCKER_HOST="unrelated-host")
    if value is not None:
        environment[stock.STOCK_TIMEOUT_ENV] = value
    return environment, calls, checkout, tool


@pytest.mark.parametrize("value", (None, "120", "240"))
def test_runner_forwards_declared_limit_to_same_readonly_container(tmp_path, value):
    environment, calls_path, checkout, tool = runner_environment(tmp_path, value)
    result = subprocess.run([str(tool / "run.sh"), "--verbose"], env=environment,
        capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    calls = [json.loads(line) for line in calls_path.read_text().splitlines()]
    commands = [row['args'][2:] for row in calls]
    assert [args[0] for args in commands] == ['container', 'build', 'container', 'image', 'run', 'container']
    assert commands[1] == ["build", "--tag", "vq-sh-elf-run:16.3", str(tool)]
    assert commands[3] == ['image', 'inspect', '--format', '{{json .Id}}', 'vq-sh-elf-run:16.3']
    run = commands[4]
    assert run[:2] == ['run', '--rm']
    assert '--pull=never' in run
    assert run[-2:] == ['sha256:' + 'd' * 64, '--verbose']
    assert run[run.index('--env') + 1] == f"{stock.STOCK_TIMEOUT_ENV}={value or '120'}"
    assert run[run.index('--mount') + 1] == f"type=bind,src={checkout},dst=/workspace,readonly"
    assert Path(run[run.index('--cidfile') + 1]).read_text() == 'f' * 64
    assert all(row['args'][:2] == ['--context', 'default'] for row in calls)
    assert all(row["context"] == "default" and row["host"] is None for row in calls)


@pytest.mark.parametrize("value", INVALID)
def test_runner_refuses_invalid_limits_without_docker(tmp_path, value):
    environment, calls_path, checkout, tool = runner_environment(tmp_path, value)
    result = subprocess.run([str(tool / "run.sh")], env=environment,
        capture_output=True, text=True, timeout=30)
    assert result.returncode == 2
    assert "must be 120 or 240" in result.stderr
    assert not calls_path.exists()


def test_stock_timeout_published_defaults_match_executed_values():
    text = (TOOL / "README.md").read_text()
    expected = (f"`{stock.STOCK_TIMEOUT_ENV}` declares the stock simulator's execution\n"
        f"limit: `{stock.DEFAULT_STOCK_TIMEOUT}` seconds by default, or an explicit `{stock.EXTENDED_STOCK_TIMEOUT}`.")
    assert expected in text
    assert stock.DEFAULT_STOCK_TIMEOUT == 120 and stock.EXTENDED_STOCK_TIMEOUT == 240
