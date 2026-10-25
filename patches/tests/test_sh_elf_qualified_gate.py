"""Real child capture and gate orchestration with controlled semantic adapters."""

import hashlib
import importlib
import json
from pathlib import Path
import shlex
import os
import signal
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def gate(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'tools/sh-elf-run'))
    return importlib.import_module('qualified_gate')


@pytest.mark.parametrize('mode', ['passed', 'failed', 'timeout'])
def test_original_child_terminal_and_both_streams_are_exact(gate, tmp_path, mode):
    program = ("import os,sys,time; os.write(1,b'x'*200000); os.write(2,b'y'*200000); "
               + ("time.sleep(30)" if mode == 'timeout' else
                  "sys.exit(7)" if mode == 'failed' else "sys.exit(0)"))
    paths = gate.process_record.run(tmp_path, tmp_path / 'job', mode,
        [sys.executable, '-c', program], 1 if mode == 'timeout' else 10, live=False)
    record = json.loads(paths[0].read_bytes())
    assert record['stdout_sha256'] == hashlib.sha256(paths[1].read_bytes()).hexdigest()
    assert record['stderr_sha256'] == hashlib.sha256(paths[2].read_bytes()).hexdigest()
    assert paths[1].read_bytes() == b'x' * 200000
    assert paths[2].read_bytes() == b'y' * 200000
    if mode == 'passed':
        gate.process_record.require_success(record)
    else:
        with pytest.raises(ValueError):
            gate.process_record.require_success(record)
        assert record['timed_out'] is (mode == 'timeout')


def test_unstarted_child_has_no_fabricated_process_terminal(gate, tmp_path):
    with pytest.raises(FileNotFoundError):
        gate.process_record.run(tmp_path, tmp_path / 'job', 'missing',
                                ['missing-vq-controlled-executable'], 5, live=False)
    assert not (tmp_path / 'job/missing-process.json').exists()
    error = json.loads((tmp_path / 'job/missing-start-error.json').read_bytes())
    assert error['child_started'] is False


def test_term_interrupt_preserves_failed_original_and_reaps_its_owned_child(gate, tmp_path):
    import selectors
    script = tmp_path / 'capture.py'
    script.write_text('import sys,json\nfrom pathlib import Path\n'
        + f'sys.path.insert(0,{str(ROOT / "tools/sh-elf-run")!r})\n'
        + 'import process_record\n'
        + f'root=Path({str(tmp_path)!r})\n'
        + 'paths=process_record.run(root,root/"job","controlled",'
        + '[sys.executable,"-c","import time; print(\\\"READY\\\",flush=True); time.sleep(30)"],20)\n'
        + 'process_record.require_success(json.loads(paths[0].read_bytes()))\n')
    process = subprocess.Popen([sys.executable, str(script)], text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    try:
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ)
            assert selector.select(timeout=5)
            assert process.stdout.readline().strip() == 'READY'
        process.send_signal(signal.SIGTERM)
        process.communicate(timeout=10)
    finally:
        started = tmp_path / 'job/controlled-started.json'
        if started.exists():
            identity = json.loads(started.read_bytes())['pgid']
            try: os.killpg(identity, signal.SIGKILL)
            except ProcessLookupError: pass
        if process.poll() is None:
            process.kill()
            process.communicate(timeout=5)
    assert process.returncode != 0
    record = json.loads((tmp_path / 'job/controlled-process.json').read_bytes())
    assert record['interrupted'] is True and record['timed_out'] is False
    assert record['actual_exit_code'] == -signal.SIGKILL
    with pytest.raises(ProcessLookupError):
        os.kill(identity, 0)
    with pytest.raises(ValueError):
        gate.process_record.require_success(record)


@pytest.mark.parametrize('write_cid', [False, True])
def test_killed_coordinator_has_no_terminal_and_the_primary_refuses_a_repeat(
        gate, tmp_path, write_cid):
    import selectors
    root = tmp_path
    tool = root / 'tools/sh-elf-run'
    tool.mkdir(parents=True)
    producer = root / 'primary.py'
    producer.write_text('import sys,signal\nfrom pathlib import Path\n'
        + f'sys.path.insert(0,{str(ROOT / "tools/sh-elf-run")!r})\n'
        + 'from docker_lifecycle import Lifecycle\n'
        + 'class Controlled:\n'
        + ' def inventory(self): return []\n'
        + ' def image_identity(self,image): return "sha256:"+"d"*64\n'
        + ' def run(self,args):\n'
        + '  assert args[0]=="run"\n'
        + ('  Path(args[args.index("--cidfile")+1]).write_text("c"*64)\n' if write_cid else '')
        + '  print("READY",flush=True)\n'
        + '  signal.pause()\n'
        + f'Lifecycle(Path({str(root)!r}),Controlled()).execute("controlled-image",120,[],skip_build=True)\n')
    runner = tool / 'run.sh'
    runner.write_text('#!/bin/sh\nexec ' + shlex.quote(sys.executable) + ' '
                      + shlex.quote(str(producer)) + '\n')
    runner.chmod(0o755)
    client = root / 'coordinator.py'
    client.write_text('import sys\nfrom pathlib import Path\n'
        + f'sys.path.insert(0,{str(ROOT / "tools/sh-elf-run")!r})\n'
        + 'import qualified_gate as gate\n'
        + 'gate.source_inputs=lambda root: {"controlled":"unchanged"}\n'
        + f'gate.run(Path({str(root)!r}))\n')
    process = subprocess.Popen([sys.executable, str(client)], text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    owned_groups = []
    try:
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ)
            assert selector.select(timeout=5), 'the original primary did not start'
            assert process.stdout.readline().strip() == 'READY'
        first, = (root / 'tmp/local-results/sh-elf-run').glob('qualification-*')
        started = json.loads((first / 'GNU-started.json').read_bytes())
        owned_groups.append(started['pgid'])
        process.kill()
        process.communicate(timeout=5)
        assert process.returncode == -signal.SIGKILL
        assert not (first / 'GNU-process.json').exists()
        # Its isolated original remains live. The actual lifecycle lock rejects
        # the next shared gate before another container/client can execute.
        repeated = subprocess.run([sys.executable, str(client)], text=True,
                                  capture_output=True, timeout=10)
        assert repeated.returncode != 0 and 'another host gate owns' in repeated.stderr
        assert 'READY' not in repeated.stdout
        jobs = list((root / 'tmp/local-results/sh-elf-run').glob('qualification-*'))
        second, = [job for job in jobs if job != first]
        assert json.loads((second / 'state.json').read_bytes())['status'] == 'failed'
        assert not list(root.rglob('TEST-candidate.json'))
        assert all(not (root / name).exists() for name in gate.RECEIPTS)
    finally:
        # The coordinator may fail before READY while its isolated child lives.
        for started_path in (root / 'tmp/local-results/sh-elf-run').glob('qualification-*/GNU-started.json'):
            if not started_path.with_name('GNU-process.json').exists():
                owned_groups.append(json.loads(started_path.read_bytes())['pgid'])
        for group in owned_groups:
            try: os.killpg(group, signal.SIGKILL)
            except ProcessLookupError: pass
        if process.poll() is None:
            process.kill()
            process.communicate(timeout=5)


@pytest.fixture(params=['native', 'external'])
def controlled(gate, tmp_path, monkeypatch, request):
    """Keep capture, ordered stage check, locking, archives and publication real."""
    root = tmp_path
    if request.param == 'external':
        external = tmp_path.parent / (tmp_path.name + '-data')
        external.mkdir()
        (root / 'tmp').mkdir()
        (root / 'tmp/local-results').symlink_to(external, target_is_directory=True)
    (root / 'tools/sh-elf-run').mkdir(parents=True)
    (root / 'tools/kb').mkdir()
    (root / 'tools/kb/config.toml').write_text('[lock]\ntimeout = 1\n')
    (root / 'input.txt').write_text('current')
    regions = gate.acceptance.registered()
    stages = [('pipeline', name) for name in gate.acceptance.PRIMARY_STAGES]
    stages += [('stock', region.key) for region in regions]
    state = {'fault': None, 'events': []}
    runtime = dict(schema=1, checkout=hashlib.sha256(str(root.resolve()).encode()).hexdigest(),
        owner='a' * 32, attempt='b' * 32, container_id='c' * 64,
        image='controlled-image', image_id='sha256:' + 'd' * 64,
        arguments=gate.PRIMARY[1:], client_exit_code=0,
        current_container_state='absent', status='succeeded')
    source = root / 'producer.py'
    source.write_text('''import json,sys
from pathlib import Path
sys.path.insert(0, REAL_TOOL_DIR)
from execution_report import stage
fault=Path('fault.txt').read_text()
stages=STAGES
if fault=='subset': stages=[('pipeline','feedback:sid22_pointer')]
if fault=='missing-stage': stages=stages[:-1]
for kind,name in stages:
    with stage(name,kind=kind): pass
print('VQ_SH_ELF_VERIFY status=PASS controlled=true')
runtime=RUNTIME
if fault=='runtime-image': runtime['image_id']='unknown'
if fault=='runtime-checkout': runtime['checkout']='unrelated'
if fault=='runtime-live': runtime['current_container_state']='running'
if fault=='runtime-arguments': runtime['arguments']=[]
if fault!='missing-runtime': print('VQ_SH_ELF_CONTAINER '+json.dumps(runtime))
if fault=='duplicate-runtime': print('VQ_SH_ELF_CONTAINER '+json.dumps(runtime))
if fault=='source-change': Path('input.txt').write_text('changed')
raise SystemExit(7 if fault=='GNU-failed' else 0)
'''.replace('REAL_TOOL_DIR', repr(str(ROOT / 'tools/sh-elf-run')))
       .replace('STAGES', repr(stages)).replace('RUNTIME', repr(runtime)))
    runner = root / 'tools/sh-elf-run/run.sh'
    runner.write_text('#!/bin/sh\nexec ' + shlex.quote(sys.executable) + ' '
                      + shlex.quote(str(source)) + '\n')
    runner.chmod(0o755)
    tested = root / 'test-producer.py'
    tested.write_text('''import json,sys
from pathlib import Path
candidate=next(arg.split('=',1)[1] for arg in sys.argv if arg.startswith('--kb-test-candidate='))
Path(candidate).write_text(json.dumps({'controlled':True}))
raise SystemExit(3 if Path('fault.txt').read_text()=='TEST-failed' else 0)
''')
    monkeypatch.setattr(gate, 'test_command', lambda candidate, **kwargs:
                        [sys.executable, str(tested), gate.test_evidence.NODEID,
                         '--kb-test-candidate=' + str(candidate)])
    monkeypatch.setattr(gate, 'source_inputs', lambda root: {'controlled': gate.sha(root / 'input.txt')})
    raw_run = gate.process_record.run
    monkeypatch.setattr(gate.process_record, 'run',
                        lambda *args, **kwargs: raw_run(*args, **kwargs, live=False))
    before = {}
    for name in gate.RECEIPTS:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(('previous ' + name).encode())
        before[name] = path.read_bytes()

    preparer = root / 'prepare-producer.py'
    preparer.write_text('''import hashlib,json,sys
from pathlib import Path
protocol,output=sys.argv[1],Path(sys.argv[2])
process,stdout,stderr=map(Path,sys.argv[3:6])
fault=Path('fault.txt').read_text()
if fault==protocol+'-refused': raise ValueError('controlled semantic refusal '+protocol)
if fault=='prepare-source-change' and protocol=='CAN': Path('input.txt').write_text('changed')
if fault=='concurrent-receipt' and protocol=='SID22': Path(EXTERNAL_RECEIPT).write_bytes(b'concurrent publication')
original=process.read_bytes()
terminal={**json.loads(original),'stdout':stdout.relative_to(Path.cwd()).as_posix(),
          'stderr':stderr.relative_to(Path.cwd()).as_posix()}
record=dict(controlled_semantic_adapter=protocol,native_model='a'*64,
            process_path=process.relative_to(Path.cwd()).as_posix(),
            process_sha256=hashlib.sha256(original).hexdigest(),terminal=terminal)
if protocol=='SID22':
    if fault=='prepared-original': record['process_sha256']='f'*64
    if fault=='prepared-native': record['native_model']='f'*64
    if fault=='prepared-process-change': process.write_bytes(original+b' ')
    if fault=='prepared-stream-change': stdout.write_text(stdout.read_text()+'changed')
if protocol=='TEST' and fault=='prepared-output-late-change':
    previous=output.parent/'CAN-prepared.json'
    previous.write_bytes(previous.read_bytes()+b' ')
output.write_text(json.dumps(record))
identity=hashlib.sha256(output.read_bytes()).hexdigest()
if fault=='prepared-hash': identity='f'*64
shown='CAN' if fault=='prepared-protocol' and protocol=='SID22' else protocol
line='kb-evidence-prepared protocol='+shown+' sha256='+identity
print(line)
if fault=='prepared-duplicate': print(line)
'''.replace('EXTERNAL_RECEIPT', repr(gate.RECEIPTS[1])))
    def prepare_command(label, paths, output, candidate):
        state['events'].append(('prepare', label))
        return [sys.executable, str(preparer), label, str(output), *map(str, paths)]
    monkeypatch.setattr(gate, 'prepare_command', prepare_command)
    publish = gate.copy_evidence.publish

    def publication(path, value):
        state['events'].append(('publish', str(path)))
        assert state['events'][:3] == [('prepare', label) for label in ('CAN', 'SID22', 'TEST')]
        publish(path, value)

    monkeypatch.setattr(gate.copy_evidence, 'publish', publication)
    return root, state, before


def test_one_original_primary_precedes_all_validators_and_publication(gate, controlled):
    root, state, before = controlled
    (root / 'fault.txt').write_text('none')
    result = gate.run(root)
    assert result['status'] == 'passed'
    job = root / result['job']
    original = json.loads((job / 'GNU-process.json').read_bytes())
    assert original['command'] == gate.PRIMARY
    assert original['actual_exit_code'] == 0 and original['timed_out'] is False
    assert len(list(job.glob('GNU-process.json'))) == 1
    assert set(result['validations']) == {'CAN', 'SID22', 'TEST'}
    assert len(list(job.glob('validate-*-process.json'))) == 3
    assert len([event for event in state['events'] if event[0] == 'publish']) == 3
    for name, old in before.items():
        archive = job / 'prior-receipts' / Path(name).relative_to('.kb')
        assert archive.read_bytes() == old
        assert (root / name).read_bytes() != old


def test_registered_test_writes_standard_reports_in_its_original_job(gate, tmp_path):
    candidate = tmp_path / 'TEST-candidate.json'
    command = gate.test_command(candidate)
    assert '--junitxml=' + str(tmp_path / 'TEST.xml') in command
    assert '--basetemp=' + str(tmp_path / 'TEST-work') in command
    assert gate.test_evidence.NODEID in command


@pytest.mark.parametrize('fault', ['GNU-failed', 'TEST-failed', 'missing-stage', 'subset',
                                 'source-change', 'prepare-source-change', 'SID22-refused',
                                 'TEST-refused', 'missing-runtime', 'runtime-image',
                                 'runtime-checkout', 'runtime-live', 'runtime-arguments',
                                 'duplicate-runtime', 'prepared-hash', 'prepared-protocol',
                                 'prepared-duplicate', 'prepared-original', 'prepared-native',
                                 'prepared-process-change', 'prepared-stream-change',
                                 'prepared-output-late-change'])
def test_outer_output_or_partial_preparation_cannot_replace_prior_receipts(
        gate, controlled, fault):
    root, state, before = controlled
    state['fault'] = fault
    (root / 'fault.txt').write_text(fault)
    with pytest.raises(ValueError):
        gate.run(root)
    assert all((root / name).read_bytes() == old for name, old in before.items())
    assert not any(event[0] == 'publish' for event in state['events'])
    job, = (root / 'tmp/local-results/sh-elf-run').glob('qualification-*')
    assert json.loads((job / 'state.json').read_bytes())['status'] == 'failed'
    if fault == 'GNU-failed':
        original = json.loads((job / 'GNU-process.json').read_bytes())
        assert original['actual_exit_code'] == 7
        assert 'status=PASS' in (job / 'GNU.stdout').read_text()
        assert state['events'] == []


def test_another_qualification_cannot_start_a_parallel_original(gate, controlled):
    root, _, before = controlled
    with gate.serialized(root):
        with pytest.raises(ValueError, match='another qualification'):
            gate.run(root)
    assert not list((root / 'tmp/local-results/sh-elf-run').glob('qualification-*'))
    assert all((root / name).read_bytes() == old for name, old in before.items())


def test_a_parallel_receipt_publication_is_preserved(gate, controlled, monkeypatch):
    root, state, before = controlled
    (root / 'fault.txt').write_text('concurrent-receipt')
    external = gate.RECEIPTS[1]
    with pytest.raises(ValueError, match='another publication'):
        gate.run(root)
    assert (root / external).read_bytes() == b'concurrent publication'
    assert all((root / name).read_bytes() == old for name, old in before.items() if name != external)
    assert not any(event[0] == 'publish' for event in state['events'])


def test_preparation_failure_has_no_child_or_receipt_change(gate, controlled, monkeypatch):
    root, _, before = controlled
    def invalid(root):
        raise ValueError('controlled invalid source preparation')
    monkeypatch.setattr(gate, 'source_inputs', invalid)
    with pytest.raises(ValueError):
        gate.run(root)
    job, = (root / 'tmp/local-results/sh-elf-run').glob('qualification-*')
    assert json.loads((job / 'state.json').read_bytes())['status'] == 'failed'
    assert not (job / 'GNU-started.json').exists()
    assert all((root / name).read_bytes() == old for name, old in before.items())


def test_publication_io_failure_keeps_its_journal_and_cannot_report_a_pass(
        gate, controlled, monkeypatch):
    root, _, before = controlled
    (root / 'fault.txt').write_text('none')
    publish = gate.copy_evidence.publish
    def failed(path, value):
        if path == root / gate.RECEIPTS[1]:
            raise OSError('controlled publication I/O failure')
        publish(path, value)
    monkeypatch.setattr(gate.copy_evidence, 'publish', failed)
    with pytest.raises(OSError):
        gate.run(root)
    job, = (root / 'tmp/local-results/sh-elf-run').glob('qualification-*')
    result = json.loads((job / 'state.json').read_bytes())
    assert result['status'] == 'failed' and result['published_receipts'] == [gate.RECEIPTS[0]]
    for name, old in before.items():
        assert (job / 'prior-receipts' / Path(name).relative_to('.kb')).read_bytes() == old
    assert all((root / name).read_bytes() == before[name] for name in gate.RECEIPTS[1:])


def test_source_change_during_publication_prevents_a_completed_gate(
        gate, controlled, monkeypatch):
    root, _, _ = controlled
    (root / 'fault.txt').write_text('none')
    publish = gate.copy_evidence.publish
    def changed(path, value):
        publish(path, value)
        (root / 'input.txt').write_text('changed during publication')
    monkeypatch.setattr(gate.copy_evidence, 'publish', changed)
    with pytest.raises(ValueError, match='during publication'):
        gate.run(root)
    job, = (root / 'tmp/local-results/sh-elf-run').glob('qualification-*')
    assert json.loads((job / 'state.json').read_bytes())['status'] == 'failed'


@pytest.mark.parametrize('failure', [None, 'verify-firmware', 'check'])
def test_real_make_orders_the_shared_gate_before_its_consumers(tmp_path, failure):
    log = tmp_path / 'steps.txt'
    recorder = tmp_path / 'make-step'
    recorder.write_text('#!' + sys.executable + '\nfrom pathlib import Path\nimport sys\n'
        + f'p=Path({str(log)!r})\n'
        + 'with p.open("a") as out: out.write(sys.argv[1]+"\\n")\n'
        + f'raise SystemExit(7 if sys.argv[1]=={failure!r} else 0)\n')
    recorder.chmod(0o755)
    completed = subprocess.run(['make', '--no-print-directory', 'verify',
        'MAKE=' + str(recorder)], cwd=ROOT, text=True, capture_output=True, timeout=10)
    expected = ['verify-firmware', 'check', 'test']
    assert log.read_text().splitlines() == (expected if failure is None else expected[:expected.index(failure)+1])
    assert (completed.returncode == 0) is (failure is None)


@pytest.mark.parametrize('fault', ('execution', 'undeclared', 'added', 'removed', 'namespace', 'untracked', 'delete'))
def test_metadata_source_transition_admits_only_exact_existing_writer_bytes(gate, fault):
    before = {'GNU':{'metadata.txt':'a' * 64, 'execution.txt':'b' * 64},
              'TEST':{'metadata.txt':'a' * 64}}
    text = 'registered proof appended\n'
    texts = {Path('metadata.txt'):text}
    after = {name:dict(values) for name,values in before.items()}
    identity = hashlib.sha256(text.encode()).hexdigest()
    for values in after.values():
        values['metadata.txt'] = identity
    if fault == 'execution':
        after['GNU']['execution.txt'] = 'c' * 64
    elif fault == 'undeclared':
        after['GNU']['metadata.txt'] = 'd' * 64
    elif fault == 'added':
        after['GNU']['new.txt'] = 'e' * 64
    elif fault == 'removed':
        after['GNU'].pop('execution.txt')
    elif fault == 'namespace':
        after['OTHER'] = {}
    elif fault == 'untracked':
        texts[Path('untracked.txt')] = 'not in the original manifest'
    else:
        texts[Path('metadata.txt')] = None
    with pytest.raises(ValueError):
        gate.metadata_source_transition(before, after, texts)


def test_metadata_source_transition_binds_every_original_namespace(gate):
    before = {'GNU':{'metadata.txt':'a' * 64, 'execution.txt':'b' * 64},
              'TEST':{'metadata.txt':'a' * 64}}
    text = 'registered proof appended\n'
    identity = hashlib.sha256(text.encode()).hexdigest()
    after = {'GNU':{'metadata.txt':identity, 'execution.txt':'b' * 64},
             'TEST':{'metadata.txt':identity}}
    assert gate.metadata_source_transition(before, after, {Path('metadata.txt'):text}) == after
    assert before['GNU']['metadata.txt'] == 'a' * 64


@pytest.fixture
def metadata_publication(gate, controlled, monkeypatch):
    from types import SimpleNamespace
    from kb import copy_evidence, write
    root, state, before = controlled
    monkeypatch.setattr(gate, 'NATIVE_PRIMARY', gate.PRIMARY)
    (root / 'execution.txt').write_text('fixed execution input')
    monkeypatch.setattr(gate, 'source_inputs', lambda directory:{
        'GNU':{'input.txt':gate.sha(directory / 'input.txt'),
               'execution.txt':gate.sha(directory / 'execution.txt')},
        'TEST':{'input.txt':gate.sha(directory / 'input.txt')}})
    batch = root / 'metadata-batch.toml'
    batch.write_text('[[op]]\ncmd = "reconcile-width"\nref = "controlled-field/ram"\n'
                     'layout = "1me3b"\nclaim_sha256 = "' + 'a' * 64 + '"\n')

    def normal_writer(ops, directory, *, log, metadata_only, archive_before):
        assert directory == root and metadata_only is True
        assert archive_before.name == 'native-preimages'
        assert state['events'] == [('prepare', name) for name in ('CAN','SID22','TEST')]
        assert {name:(root / name).read_bytes() for name in before} == before
        for name, protocol in zip(gate.RECEIPTS, ('CAN','SID22','TEST')):
            record = json.loads(copy_evidence.read_output(root, name))
            assert record['controlled_semantic_adapter'] == protocol
        state['events'].append(('native', 'metadata-only'))
        fault = (root / 'fault.txt').read_text()
        if fault == 'metadata-refused':
            raise ValueError('controlled normal writer refusal')
        text = 'controlled proof metadata\n'
        (root / 'input.txt').write_text(text)
        if fault == 'metadata-execution-change':
            (root / 'execution.txt').write_text('unrequested executable mutation')
        return SimpleNamespace(lines=['controlled exact width resolution']), {Path('input.txt'):text}

    monkeypatch.setattr(write, 'apply', normal_writer)
    return root, state, before, batch


def test_all_three_records_precede_normal_metadata_and_final_receipts(gate, metadata_publication):
    root, state, before, batch = metadata_publication
    (root / 'fault.txt').write_text('none')
    result = gate.run(root, native_profiles=True, native_publication_batch=batch)
    assert result['status'] == 'passed'
    assert state['events'][:4] == [('prepare', name) for name in ('CAN','SID22','TEST')] + [('native','metadata-only')]
    assert len([event for event in state['events'] if event[0] == 'publish']) == 3
    job = root / result['job']
    assert len(list(job.glob('GNU-process.json'))) == 1
    assert len(list(job.glob('TEST-process.json'))) == 1
    assert (job / 'native-publication-batch.toml').read_bytes() == batch.read_bytes()
    original = json.loads((job / 'source-inputs.json').read_bytes())
    current = json.loads((job / 'source-inputs-after-native-publication.json').read_bytes())
    assert original['GNU']['execution.txt'] == current['GNU']['execution.txt']
    assert original['GNU']['input.txt'] != current['GNU']['input.txt']
    publication = json.loads((job / 'native-publication.json').read_bytes())
    assert publication['metadata_only'] is True and set(publication['prepared_records']) == set(gate.RECEIPTS)
    assert copy_evidence_view_is_restored(gate, root)
    assert all((root / name).read_bytes() != old for name,old in before.items())


def copy_evidence_view_is_restored(gate, root):
    return gate.copy_evidence._PREPARED_PUBLICATION.get() is None


@pytest.mark.parametrize('fault', ('TEST-failed', 'TEST-refused', 'metadata-refused', 'metadata-execution-change'))
def test_incomplete_test_or_metadata_refusal_cannot_publish_receipts(gate, metadata_publication, fault):
    root, state, before, batch = metadata_publication
    (root / 'fault.txt').write_text(fault)
    with pytest.raises(ValueError):
        gate.run(root, native_profiles=True, native_publication_batch=batch)
    assert all((root / name).read_bytes() == old for name,old in before.items())
    assert not any(event[0] == 'publish' for event in state['events'])
    assert copy_evidence_view_is_restored(gate, root)
    if fault.startswith('TEST'):
        assert not any(event[0] == 'native' for event in state['events'])


def test_publication_batch_requires_native_mode_before_starting_a_child(gate, controlled):
    root, _, before = controlled
    with pytest.raises(ValueError, match='complete native TEST mode'):
        gate.run(root, native_publication_batch=root / 'unused.toml')
    assert not list((root / 'tmp/local-results/sh-elf-run').glob('qualification-*'))
    assert all((root / name).read_bytes() == old for name,old in before.items())
