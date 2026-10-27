"""The patch runner forwards bounded simulator waits to its owned container."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools/sh-elf-run"
TIMEOUT_ENV = "VQ_SH_ELF_STOCK_TIMEOUT_SECONDS"
INVALID = ("", "0", "119", "121", "239", "241", "-1", "+240", "240 ",
           "120.0", "nan", "inf", "٢٤٠")


def inputs_label(tool):
    return subprocess.run([sys.executable, str(tool / "image_inputs.py")], capture_output=True,
        text=True, check=True).stdout.strip()


def runner_environment(tmp_path, value):
    directory = tmp_path / "bin"
    directory.mkdir()
    calls = tmp_path / "docker-calls.jsonl"
    checkout = tmp_path / "checkout"
    tool = checkout / "tools/sh-elf-run"
    tool.mkdir(parents=True)
    for filename in ('run.sh', 'docker_lifecycle.py', 'gate_paths.py', 'image_inputs.py',
                     'Dockerfile', 'gnu16.3-sh-pc-observer.patch'):
        target = tool / filename
        target.write_bytes((TOOL / filename).read_bytes())
        target.chmod((TOOL / filename).stat().st_mode)
    fake = directory / "docker"
    fake.write_text(f"#!{sys.executable}\n" +
        "import json,os,sys\nfrom pathlib import Path\n" +
        "with open(os.environ['VQ_TIMEOUT_TEST_CALLS'],'a') as out:\n" +
        " out.write(json.dumps(dict(args=sys.argv[1:],context=os.environ.get('DOCKER_CONTEXT'),host=os.environ.get('DOCKER_HOST')))+'\\n')\n" +
        "args=sys.argv[1:]\nassert args[:2]==['--context','default']\nargs=args[2:]\n" +
        "if args[0]=='image': print(json.dumps(dict(id='sha256:'+'d'*64,config=dict(Labels=dict([os.environ['VQ_TIMEOUT_TEST_LABEL'].split('=',1)])))))\n" +
        "if args[0]=='run': Path(args[args.index('--cidfile')+1]).write_text('f'*64)\n")
    fake.chmod(0o755)
    environment = os.environ.copy()
    for name in (TIMEOUT_ENV, "VQ_SH_ELF_IMAGE", "VQ_SH_ELF_SKIP_BUILD"):
        environment.pop(name, None)
    environment.update(PATH=str(directory) + os.pathsep + environment["PATH"],
        VQ_TIMEOUT_TEST_CALLS=str(calls), VQ_TIMEOUT_TEST_LABEL=inputs_label(tool),
        DOCKER_CONTEXT="unrelated-context", DOCKER_HOST="unrelated-host")
    if value is not None:
        environment[TIMEOUT_ENV] = value
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
    assert commands[1] == ["build", "--tag", "vq-sh-elf-run:16.3", "--label", inputs_label(TOOL),
                           str(tool)]
    assert commands[3] == ['image', 'inspect', '--format',
                           '{"id":{{json .Id}},"config":{{json .Config}}}', 'vq-sh-elf-run:16.3']
    run = commands[4]
    assert run[:2] == ['run', '--rm']
    assert '--pull=never' in run
    assert run[-2:] == ['sha256:' + 'd' * 64, '--verbose']
    assert run[run.index('--env') + 1] == f"{TIMEOUT_ENV}={value or '120'}"
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
