"""Exact-child lifecycle contracts with controlled Docker state and client loss."""

from copy import deepcopy
import importlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def lifecycle(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'tools/sh-elf-run'))
    return importlib.import_module('docker_lifecycle')


def row(root, *, identity='a' * 64, labels=None, status='running', running=True, restart='no'):
    return dict(id=identity, labels=labels or {}, status=status, running=running, restart=restart,
        mounts=[dict(Type='bind', Source=str(root), Destination='/workspace')])


class ControlledDocker:
    def __init__(self, module, root):
        self.module, self.root = module, root
        self.rows, self.commands = [], []
        self.reads = 0
        self.fail_read = None
        self.build_code = self.run_code = 0
        self.cid = 'c' * 64
        self.write_cid = True
        self.retained = None

    def inventory(self):
        self.reads += 1
        if self.fail_read == self.reads or self.fail_read == 'all':
            raise self.module.DockerStateUnknown('controlled unknown daemon state')
        return deepcopy(self.rows)

    def image_identity(self, image):
        return 'sha256:' + 'd' * 64

    def run(self, arguments):
        self.commands.append(arguments)
        if arguments[0] == 'build':
            return self.build_code
        assert arguments[0] == 'run'
        labels = dict(arguments[i + 1].split('=', 1)
                      for i, value in enumerate(arguments) if value == '--label')
        if self.write_cid:
            Path(arguments[arguments.index('--cidfile') + 1]).write_text(self.cid)
        if self.retained is not None:
            self.rows.append(row(self.root, identity='d' * 64 if self.retained == 'wrong-id'
                else 'c' * 64, labels=labels, status=self.retained,
                running=self.retained == 'running'))
        return self.run_code


def attempts(gate):
    return [json.loads(path.read_text()) for path in gate.directory.glob('*.json')
            if path.name != 'owner.json']


def test_normal_completion_binds_unique_identity_and_keeps_primary_arguments(lifecycle, tmp_path):
    docker = ControlledDocker(lifecycle, tmp_path)
    gate = lifecycle.Lifecycle(tmp_path, docker)
    assert gate.execute('controlled-image', 240, ['--can-copy-witness', '--sid22-witness']) == 0
    assert docker.reads == 3
    build, run = docker.commands
    assert build == ['build', '--tag', 'controlled-image', str(tmp_path / 'tools/sh-elf-run')]
    owner = gate.owner()
    assert run[:2] == ['run', '--rm']
    assert '--pull=never' in run
    assert run[run.index('--name') + 1] == 'vq-sh-elf-run-' + owner
    assert run[-3:] == ['sha256:' + 'd' * 64, '--can-copy-witness', '--sid22-witness']
    assert 'VQ_SH_ELF_STOCK_TIMEOUT_SECONDS=240' in run
    assert f'type=bind,src={tmp_path},dst=/workspace,readonly' in run
    saved, = attempts(gate)
    assert saved['status'] == 'succeeded' and saved['client_exit_code'] == 0
    assert saved['container_id'] == 'c' * 64
    assert saved['image'] == 'controlled-image' and saved['image_id'] == 'sha256:' + 'd' * 64
    assert saved['current_container_state'] == 'absent'
    assert saved['owner'] == owner
    assert saved['retained_stopped_containers'] == []


def test_linked_results_have_one_read_only_mount_without_changing_checkout_identity(lifecycle, tmp_path):
    root = tmp_path / 'checkout'
    root.mkdir()
    external = tmp_path / 'data/local-results'
    external.mkdir(parents=True)
    (root / 'tmp').mkdir()
    (root / 'tmp/local-results').symlink_to(external, target_is_directory=True)
    docker = ControlledDocker(lifecycle, root)
    gate = lifecycle.Lifecycle(root, docker)
    assert gate.execute('controlled-image', 120, [], skip_build=True) == 0
    run, = docker.commands
    mounts = [run[i + 1] for i, value in enumerate(run) if value == '--mount']
    assert mounts == [f'type=bind,src={root},dst=/workspace,readonly',
                      f'type=bind,src={external},dst={external},readonly']
    saved, = attempts(gate)
    assert saved['repository'] == str(root) and saved['checkout'] == gate.checkout
    assert (external / 'sh-elf-run/owner.json').is_file()


def test_missing_results_disk_refuses_before_mkdir_or_docker(lifecycle, tmp_path):
    missing = tmp_path.parent / (tmp_path.name + '-unmounted')
    (tmp_path / 'tmp').mkdir()
    (tmp_path / 'tmp/local-results').symlink_to(missing, target_is_directory=True)
    docker = ControlledDocker(lifecycle, tmp_path)
    with pytest.raises(lifecycle.LifecycleError, match='unavailable'):
        lifecycle.Lifecycle(tmp_path, docker)
    assert not missing.exists() and docker.commands == []


@pytest.mark.parametrize('code', [1, 137])
def test_original_client_failure_is_never_recorded_as_success(lifecycle, tmp_path, code):
    docker = ControlledDocker(lifecycle, tmp_path)
    docker.run_code = code
    gate = lifecycle.Lifecycle(tmp_path, docker)
    assert gate.execute('controlled-image', 120, [], skip_build=True) == code
    saved, = attempts(gate)
    assert saved['status'] == 'failed' and saved['client_exit_code'] == code


def test_build_failure_never_starts_a_container(lifecycle, tmp_path):
    docker = ControlledDocker(lifecycle, tmp_path)
    docker.build_code = 7
    gate = lifecycle.Lifecycle(tmp_path, docker)
    assert gate.execute('controlled-image', 120, []) == 7
    assert [command[0] for command in docker.commands] == ['build']
    assert attempts(gate)[0]['status'] == 'build-failed'


@pytest.mark.parametrize('status,running,kind', [
    ('running', True, 'live'), ('paused', True, 'live'),
    ('created', False, 'unknown'), ('removing', False, 'unknown'),
])
def test_previous_live_and_unknown_children_refuse_before_build(
        lifecycle, tmp_path, status, running, kind):
    docker = ControlledDocker(lifecycle, tmp_path)
    docker.rows = [row(tmp_path, status=status, running=running)]
    gate = lifecycle.Lifecycle(tmp_path, docker)
    with pytest.raises(lifecycle.LifecycleError) as error:
        gate.execute('controlled-image', 120, [])
    assert error.value.kind == kind and 'a' * 64 in str(error.value)
    assert docker.commands == []
    assert attempts(gate) == []


@pytest.mark.parametrize('read', [1, 2, 3])
def test_unknown_daemon_state_cannot_start_or_qualify_a_repeat(lifecycle, tmp_path, read):
    docker = ControlledDocker(lifecycle, tmp_path)
    docker.fail_read = read
    gate = lifecycle.Lifecycle(tmp_path, docker)
    with pytest.raises(lifecycle.DockerStateUnknown):
        gate.execute('controlled-image', 120, [])
    if read == 1:
        assert docker.commands == []
    else:
        saved, = attempts(gate)
        assert saved['status'] == 'unresolved' and saved['refusal_kind'] == 'unknown'
        if read == 2:
            assert not any(command[0] == 'run' for command in docker.commands)


def test_survivor_after_zero_client_exit_blocks_the_next_attempt(lifecycle, tmp_path):
    docker = ControlledDocker(lifecycle, tmp_path)
    docker.retained = 'running'
    gate = lifecycle.Lifecycle(tmp_path, docker)
    with pytest.raises(lifecycle.SurvivingGate):
        gate.execute('controlled-image', 120, [], skip_build=True)
    saved, = attempts(gate)
    assert saved['status'] == 'unresolved' and saved['refusal_kind'] == 'live'
    assert saved['client_exit_code'] == 0
    before = deepcopy(docker.commands)
    with pytest.raises(lifecycle.SurvivingGate):
        lifecycle.Lifecycle(tmp_path, docker).execute('controlled-image', 120, [])
    assert docker.commands == before


def test_resolved_survivor_allows_only_a_fresh_attempt_and_preserves_the_failure(lifecycle, tmp_path):
    docker = ControlledDocker(lifecycle, tmp_path)
    docker.retained = 'running'
    gate = lifecycle.Lifecycle(tmp_path, docker)
    with pytest.raises(lifecycle.SurvivingGate):
        gate.execute('controlled-image', 120, [], skip_build=True)
    old_path, = [path for path in gate.directory.glob('*.json') if path.name != 'owner.json']
    old_bytes = old_path.read_bytes()
    docker.rows = []
    docker.retained = None
    docker.cid = 'b' * 64
    assert gate.execute('controlled-image', 120, [], skip_build=True) == 0
    assert old_path.read_bytes() == old_bytes
    successful, = [saved for saved in attempts(gate) if saved['status'] == 'succeeded']
    assert successful['container_id'] == 'b' * 64
    assert sum(command[0] == 'run' for command in docker.commands) == 2


def test_child_appearing_during_build_refuses_container_creation(lifecycle, tmp_path, monkeypatch):
    docker = ControlledDocker(lifecycle, tmp_path)
    original = docker.run

    def build(arguments):
        code = original(arguments)
        if arguments[0] == 'build':
            docker.rows = [row(tmp_path)]
        return code

    monkeypatch.setattr(docker, 'run', build)
    gate = lifecycle.Lifecycle(tmp_path, docker)
    with pytest.raises(lifecycle.SurvivingGate):
        gate.execute('controlled-image', 120, [])
    assert [command[0] for command in docker.commands] == ['build']
    assert attempts(gate)[0]['refusal_kind'] == 'live'


@pytest.mark.parametrize('fault', ['missing', 'invalid', 'wrong-id'])
def test_zero_exit_requires_an_exact_primary_identity(lifecycle, tmp_path, fault):
    docker = ControlledDocker(lifecycle, tmp_path)
    if fault == 'missing': docker.write_cid = False
    elif fault == 'invalid': docker.cid = 'not-a-container'
    else: docker.retained = 'wrong-id'
    gate = lifecycle.Lifecycle(tmp_path, docker)
    with pytest.raises(lifecycle.LifecycleError):
        gate.execute('controlled-image', 120, [], skip_build=True)
    assert attempts(gate)[0]['status'] == 'unresolved'


def test_stopped_child_is_distinct_from_a_live_or_restartable_child(lifecycle, tmp_path):
    docker = ControlledDocker(lifecycle, tmp_path)
    docker.retained = 'exited'
    gate = lifecycle.Lifecycle(tmp_path, docker)
    assert gate.execute('controlled-image', 120, [], skip_build=True) == 0
    assert attempts(gate)[0]['retained_stopped_containers'] == ['c' * 64]
    assert attempts(gate)[0]['current_container_state'] == 'stopped'
    docker.rows[0]['restart'] = 'always'
    with pytest.raises(lifecycle.DockerStateUnknown):
        gate.execute('controlled-image', 120, [])


def test_other_checkout_is_untouched_and_erased_owner_does_not_hide_a_child(lifecycle, tmp_path):
    docker = ControlledDocker(lifecycle, tmp_path)
    docker.rows = [row(tmp_path / 'other-checkout')]
    gate = lifecycle.Lifecycle(tmp_path, docker)
    assert gate.execute('controlled-image', 120, [], skip_build=True) == 0
    old_owner = gate.owner()
    (gate.directory / 'owner.json').unlink()
    docker.rows = [row(tmp_path, labels={lifecycle.OWNER_LABEL: old_owner})]
    previous = deepcopy(docker.commands)
    with pytest.raises(lifecycle.SurvivingGate):
        gate.execute('controlled-image', 120, [])
    assert docker.commands == previous


@pytest.mark.parametrize('content', ['not-json', '{"schema":true,"owner":"bad"}', '{}'])
def test_corrupt_owner_is_not_replaced_to_avoid_the_guard(lifecycle, tmp_path, content):
    docker = ControlledDocker(lifecycle, tmp_path)
    gate = lifecycle.Lifecycle(tmp_path, docker)
    gate.directory.mkdir(parents=True)
    path = gate.directory / 'owner.json'
    path.write_text(content)
    with pytest.raises(lifecycle.LifecycleError, match='saved container owner'):
        gate.execute('controlled-image', 120, [])
    assert path.read_text() == content and docker.commands == []


def test_host_lock_refuses_concurrent_gate_without_touching_docker(lifecycle, tmp_path):
    docker = ControlledDocker(lifecycle, tmp_path)
    gate = lifecycle.Lifecycle(tmp_path, docker)
    with gate.locked():
        with pytest.raises(lifecycle.LifecycleError, match='another host gate'):
            lifecycle.Lifecycle(tmp_path, docker).execute('controlled-image', 120, [])
    assert docker.commands == []


@pytest.mark.parametrize('signal_number', [signal.SIGTERM, signal.SIGKILL])
@pytest.mark.parametrize('write_cid', [False, True])
def test_real_client_loss_before_or_after_cid_never_permits_a_live_repeat(
        lifecycle, tmp_path, signal_number, write_cid):
    state = tmp_path / 'controlled-docker.json'
    script = tmp_path / 'client.py'
    script.write_text(f'''
import json,os,signal,sys
from pathlib import Path
sys.path.insert(0,{str(ROOT / 'tools/sh-elf-run')!r})
from docker_lifecycle import Lifecycle
root=Path({str(tmp_path)!r}); state=Path({str(state)!r})
class Controlled:
 def inventory(self): return json.loads(state.read_text()) if state.exists() else []
 def image_identity(self,image): return 'sha256:'+'d'*64
 def run(self,args):
  assert args[0]=='run'
  labels=dict(args[i+1].split('=',1) for i,v in enumerate(args) if v=='--label')
  state.write_text(json.dumps([dict(id='e'*64,labels=labels,mounts=[],running=True,status='running',restart='no')]))
  if {write_cid!r}: Path(args[args.index('--cidfile')+1]).write_text('e'*64)
  os.kill(os.getpid(),{int(signal_number)})
Lifecycle(root,Controlled()).execute('controlled-image',120,[],skip_build=True)
''')
    terminal = subprocess.run([sys.executable, str(script)], capture_output=True, timeout=10)
    assert terminal.returncode == -signal_number
    docker = ControlledDocker(lifecycle, tmp_path)
    docker.rows = json.loads(state.read_text())
    gate = lifecycle.Lifecycle(tmp_path, docker)
    saved, = attempts(gate)
    assert saved['status'] == 'container-starting'
    assert Path(saved['cidfile']).exists() is write_cid
    with pytest.raises(lifecycle.SurvivingGate, match='e' * 64):
        gate.execute('controlled-image', 120, [])
    assert docker.commands == []


def test_docker_inventory_uses_bounded_primary_context_and_projected_fields(
        lifecycle, tmp_path, monkeypatch):
    calls = []
    expected = row(tmp_path)

    def command(arguments, **kwargs):
        calls.append((arguments, kwargs))
        return subprocess.CompletedProcess(arguments, 0,
            'a' * 64 + '\n' if len(calls) == 1 else json.dumps(expected) + '\n', '')

    monkeypatch.setattr(lifecycle.subprocess, 'run', command)
    assert lifecycle.Docker(tmp_path).inventory() == [expected]
    assert all(arguments[:3] == ['docker', '--context', 'default']
               and options == dict(cwd=tmp_path, capture_output=True, text=True, timeout=15)
               for arguments, options in calls)
    assert calls[1][0][-1] == 'a' * 64
    assert '.Config.Env' not in lifecycle.INSPECT


@pytest.mark.parametrize('fault', ['list-id', 'duplicate', 'json', 'missing-id', 'running-type',
                                  'mount-type', 'mount-source', 'labels-type', 'command-failure'])
def test_incomplete_docker_inventory_is_unknown_and_cannot_be_assumed_empty(
        lifecycle, tmp_path, monkeypatch, fault):
    expected = row(tmp_path)
    if fault == 'missing-id': expected['id'] = 'b' * 64
    elif fault == 'running-type': expected['running'] = 1
    elif fault == 'mount-type': expected['mounts'] = [None]
    elif fault == 'mount-source': expected['mounts'][0]['Source'] = 1
    elif fault == 'labels-type': expected['labels'] = []
    calls = []

    def command(arguments, **kwargs):
        calls.append(arguments)
        if fault == 'command-failure':
            return subprocess.CompletedProcess(arguments, 1, '', 'controlled unavailable daemon')
        if len(calls) == 1:
            text = 'bad-id\n' if fault == 'list-id' else 'a' * 64 + '\n'
            if fault == 'duplicate': text += text
        else:
            text = 'not-json' if fault == 'json' else json.dumps(expected)
        return subprocess.CompletedProcess(arguments, 0, text, '')

    monkeypatch.setattr(lifecycle.subprocess, 'run', command)
    with pytest.raises(lifecycle.DockerStateUnknown):
        lifecycle.Docker(tmp_path).inventory()


def test_docker_query_timeout_is_unknown(lifecycle, tmp_path, monkeypatch):
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], kwargs['timeout'])

    monkeypatch.setattr(lifecycle.subprocess, 'run', timeout)
    with pytest.raises(lifecycle.DockerStateUnknown, match='timed out'):
        lifecycle.Docker(tmp_path).inventory()


@pytest.mark.parametrize('output', ['"sha256:' + 'd' * 64 + '"\n', 'unknown', 'null',
                                  '"sha256:short"', '[]'])
def test_image_identity_is_exact_or_unknown(lifecycle, tmp_path, monkeypatch, output):
    docker = lifecycle.Docker(tmp_path)
    calls = []
    monkeypatch.setattr(docker, 'capture', lambda args: calls.append(args) or output)
    if output.startswith('"sha256:') and len(output.strip()) == 73:
        assert docker.image_identity('selected-tag') == 'sha256:' + 'd' * 64
    else:
        with pytest.raises(lifecycle.DockerStateUnknown):
            docker.image_identity('selected-tag')
    assert calls == [['image', 'inspect', '--format', '{{json .Id}}', 'selected-tag']]


def test_unknown_image_cannot_start_a_container(lifecycle, tmp_path, monkeypatch):
    docker = ControlledDocker(lifecycle, tmp_path)
    def unknown(image):
        raise lifecycle.DockerStateUnknown('controlled unknown image')
    monkeypatch.setattr(docker, 'image_identity', unknown)
    with pytest.raises(lifecycle.DockerStateUnknown):
        lifecycle.Lifecycle(tmp_path, docker).execute('selected-tag', 120, [], skip_build=True)
    assert docker.commands == []


@pytest.mark.parametrize('skip_build', [False, True])
def test_primary_shell_preserves_arguments_timeout_and_default_context(tmp_path, skip_build):
    binary = tmp_path / 'bin'
    binary.mkdir()
    received = tmp_path / 'received.json'
    probe = tmp_path / 'python-boundary.py'
    probe.write_text('import json,os,sys\nfrom pathlib import Path\n'
        + f'Path({str(received)!r}).write_text(json.dumps(dict(arguments=sys.argv[1:],'
        + 'context=os.environ.get("DOCKER_CONTEXT"),host=os.environ.get("DOCKER_HOST"))))\n')
    executable = binary / 'python3'
    executable.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{probe}" "$@"\n')
    executable.chmod(0o755)
    environment = dict(os.environ, PATH=str(binary) + os.pathsep + os.environ['PATH'],
        DOCKER_CONTEXT='controlled-other-context', DOCKER_HOST='controlled-unused-host',
        VQ_SH_ELF_IMAGE='controlled-image', VQ_SH_ELF_STOCK_TIMEOUT_SECONDS='240',
        VQ_SH_ELF_SKIP_BUILD='1' if skip_build else '0')
    terminal = subprocess.run(['sh', str(ROOT / 'tools/sh-elf-run/run.sh'),
        '--can-copy-witness', '--sid22-witness'], env=environment,
        capture_output=True, text=True, timeout=10)
    assert terminal.returncode == 0
    actual = json.loads(received.read_text())
    expected = [str(ROOT / 'tools/sh-elf-run/docker_lifecycle.py'), '--image', 'controlled-image',
                '--stock-timeout', '240']
    if skip_build:
        expected.append('--skip-build')
    assert actual == dict(arguments=[*expected, '--', '--can-copy-witness', '--sid22-witness'],
                         context='default', host=None)
