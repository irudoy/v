"""Family publication with synthetic images and controlled census/model gates.

The homology renderer and its post-publication byte check are real. Controlled
L0, census and model results isolate the publication lifecycle from stock-code
interpretation and the graph server.
"""

import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
from types import SimpleNamespace

import pytest

from kb import compile, family, graph, l0, lock, names, project, publication, repo, write
from kb.repo import KbError
from tools import rom_homology


REPORT = Path('rom-images/homology.csv')
METADATA = dict(kind='distinct-code', mcu='SH7058', flash_size=0x9000,
                software_ids=['FIXTURE'])
CENSUS = family.census


def _sources(root):
    directory = root / 'rom-images'
    directory.mkdir()
    catalog = 'path,rom,sha256,note\n'
    for label in ('OLD', 'NEW'):
        data = bytearray(b'\xff' * 0x9000)
        for offset, marker, address in rom_homology.IDENTITY_BLOCKS[:1]:
            data[offset:offset + len(marker)] = marker
            data[address:address + 11] = b'FIXTURE\x00\x00\x00\x00'
        data[0x8204:0x820f] = ('1' + label + '00000').encode().ljust(11, b'\x00')
        data[0x8300:0x8400] = bytes(range(256))
        path = Path('23710-PROBE') / f'1{label}-20260101-stock.bin'
        (directory / path).parent.mkdir(exist_ok=True)
        (directory / path).write_bytes(data)
        catalog += f'{path},{label},{hashlib.sha256(data).hexdigest()},Controlled fixture\n'
    (directory / 'roms.csv').write_text(catalog)
    text = '''schema_version = 1
# Retain the intake note.
[analysis]
code_start = 0x8200
window_size = 64
source_stride = 64
target_stride = 1
page_size = 512
min_distinct_bytes = 2
max_dominant_fraction = 0.95

[family.existing]
kind = "distinct-code"
members = ["OLD"]
canonical = "OLD"
mcu = "SH7058"
flash_size = 0x9000
software_ids = ["FIXTURE"]
same_address_inheritance = false
layouts = { old = "OLD" }
evidence = "Controlled image identity."
'''
    (root / repo.HOMOLOGY).write_bytes(text.replace('\n', '\r\n').encode())
    (root / repo.HOMOLOGY).chmod(0o640)
    (root / REPORT).write_bytes(b'previous,report\r\nOLD,retained\r\n')
    (root / REPORT).chmod(0o600)
    (root / names.PATH).parent.mkdir()
    (root / names.PATH).write_text(names.render([]))


def _case(root, operation):
    return SimpleNamespace(root=root, operation=operation,
                           family_id='onboarded' if operation == 'new' else 'existing')


def _configure(root, monkeypatch):
    state = SimpleNamespace(model=object(), layouts=[], synchronized=False)
    monkeypatch.setattr(lock, 'timeout_of', lambda root: 5)
    monkeypatch.setattr(family, 'census', lambda *args: 'Controlled census gate result.')

    def check_layout(layout, held):
        assert held == root
        state.layouts.append(layout.id)
        return []

    def build(held, overlay):
        assert held == root and set(overlay) == {repo.HOMOLOGY}
        assert 'NEW' in overlay[repo.HOMOLOGY]
        return state.model

    def synchronize(held, full, log, model):
        assert held == root and model is state.model
        assert publication.pending(root)
        assert (root / REPORT).read_bytes() == rom_homology.build_report(
            root / repo.CATALOG, root / repo.HOMOLOGY).encode()
        state.synchronized = True

    monkeypatch.setattr(l0, 'check_layout', check_layout)
    monkeypatch.setattr(compile, 'build', build)
    monkeypatch.setattr(write, '_issues', lambda model: {})
    monkeypatch.setattr(graph, 'sync_held', synchronize)
    return state


@pytest.fixture(params=['new', 'add'])
def sources(tmp_path, monkeypatch, request):
    _sources(tmp_path)
    case = _case(tmp_path, request.param)
    case.state = _configure(tmp_path, monkeypatch)
    return case


def snapshot(root):
    result = {}
    for relative in (repo.HOMOLOGY, REPORT, names.PATH):
        path = root / relative
        result[relative] = (path.read_bytes(), path.stat().st_mode & 0o7777) if path.exists() else None
    return result


def run(case, *, dry_run=False, report='defs/OLD-NEW.census-correspondence.csv'):
    return family.apply(case.operation, case.family_id, 'NEW', 'new', report,
                        METADATA if case.operation == 'new' else None,
                        root=case.root, dry_run=dry_run, log=lambda text: None)


def test_family_success_publishes_a_checked_report_through_sync(sources):
    assert 'source and stock gates pass' in run(sources)
    assert sources.state.synchronized and 'new' in sources.state.layouts
    assert not publication.pending(sources.root)
    assert '# Retain the intake note.' in (sources.root / repo.HOMOLOGY).read_text()
    assert (sources.root / REPORT).stat().st_mode & 0o7777 == 0o600


def test_family_dry_run_reviews_both_files_without_publication(sources):
    before = snapshot(sources.root)
    difference = run(sources, dry_run=True)
    assert 'b/rom-images/homology.toml' in difference
    assert 'b/rom-images/homology.csv' in difference
    assert snapshot(sources.root) == before
    assert not sources.state.synchronized and not publication.pending(sources.root)


@pytest.mark.parametrize('missing_report', [False, True])
def test_failed_sync_restores_both_files_and_nested_names(sources, monkeypatch, missing_report):
    if missing_report:
        (sources.root / REPORT).unlink()
    before = snapshot(sources.root)

    def failed(*args):
        assert publication.pending(sources.root)
        names.write([names.Row('new', 'ram', 0x100, 'fixture-otter', ())], sources.root)
        raise KbError('controlled synchronization refusal', code=3)

    monkeypatch.setattr(graph, 'sync_held', failed)
    with pytest.raises(KbError, match='synchronization refusal'):
        run(sources)
    status = publication.recover(sources.root, status=True)
    assert set(status['paths']) == {path.as_posix() for path in before}
    assert publication.recover(sources.root, dry_run=True) == status
    publication.recover(sources.root)
    assert snapshot(sources.root) == before


def test_post_publication_report_refusal_retains_recovery(sources, monkeypatch):
    before = snapshot(sources.root)
    checking = rom_homology.check_report

    def refused(path, rendered):
        assert publication.pending(sources.root)
        checking(path, rendered + 'controlled mismatched report\n')

    monkeypatch.setattr(rom_homology, 'check_report', refused)
    with pytest.raises(KbError, match='report is stale') as caught:
        run(sources)
    assert caught.value.code == 3 and not sources.state.synchronized
    message = str(caught.value)
    assert 'publication journal retained' in message
    assert 'uv run kb recover --status' in message
    assert 'regenerate' not in message
    publication.recover(sources.root)
    assert snapshot(sources.root) == before


def test_standalone_report_check_retains_its_regeneration_advice(sources, monkeypatch, capsys):
    monkeypatch.setattr(rom_homology, 'build_report', lambda: 'expected report\n')
    assert rom_homology.main(['--check', '--output', str(sources.root / REPORT)]) == 2
    assert 'regenerate with tools/rom_homology.py' in capsys.readouterr().err
    assert not publication.pending(sources.root)


def test_manual_report_edit_prevents_any_family_restoration(sources, monkeypatch):
    before = snapshot(sources.root)
    monkeypatch.setattr(graph, 'sync_held', lambda *args: (_ for _ in ()).throw(KbError('sync refusal')))
    with pytest.raises(KbError):
        run(sources)
    produced = (sources.root / REPORT).read_bytes()
    (sources.root / REPORT).write_bytes(b'manual report edit\n')
    held = snapshot(sources.root)
    with pytest.raises(KbError, match='nothing is restored'):
        publication.recover(sources.root)
    assert snapshot(sources.root) == held and publication.pending(sources.root)
    (sources.root / REPORT).write_bytes(produced)
    publication.recover(sources.root)
    assert snapshot(sources.root) == before


@pytest.mark.parametrize('gate', ['census', 'image', 'family', 'identity', 'relationships',
                                  'analysis', 'l0', 'model'])
def test_family_gates_still_refuse_before_source_publication(sources, monkeypatch, gate):
    if gate == 'census':
        monkeypatch.setattr(family, 'census', CENSUS)
    elif gate == 'image':
        image = next((sources.root / 'rom-images/23710-PROBE').glob('*NEW*'))
        image.write_bytes(b'wrong image bytes')
    elif gate in ('family', 'identity', 'relationships', 'analysis'):
        path = sources.root / repo.HOMOLOGY
        text = path.read_text()
        if gate == 'family':
            text = text.replace('flash_size = 0x9000', 'flash_size = 0x8000')
        elif gate == 'identity':
            text = text.replace('software_ids = ["FIXTURE"]', 'software_ids = ["MISSING"]')
        elif gate == 'analysis':
            text = text.replace('source_stride = 64', 'source_stride = 0')
        else:
            text += '\n[[relationship]]\nleft_family = "missing"\n'
        path.write_text(text)
    elif gate == 'l0':
        monkeypatch.setattr(l0, 'check_layout', lambda *args: [
            SimpleNamespace(path='l0/new/manifest.toml', message='controlled L0 refusal')])
    else:
        monkeypatch.setattr(write, '_issues', lambda model: {1: SimpleNamespace(
            check='canonical', subject='new', message='controlled model refusal')})
    before = snapshot(sources.root)
    with pytest.raises(KbError):
        run(sources)
    assert snapshot(sources.root) == before
    assert not publication.pending(sources.root) and not sources.state.synchronized


@pytest.mark.parametrize('phase', ['report', 'registry', 'check', 'sync'])
def test_process_termination_recovers_family_through_the_guarded_cli(sources, phase):
    before = snapshot(sources.root)
    package = sources.root / 'tools/kb/src/kb'
    shutil.copytree(Path(publication.__file__).parent, package, ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copyfile(repo.ROOT / 'tools/kb/hook.py', sources.root / 'tools/kb/hook.py')
    environment = {**os.environ, 'PYTHONPATH': os.pathsep.join((str(package.parent), str(repo.ROOT)))}
    environment.pop('KB_GUARD', None)
    program = '''
import os, signal, sys
from pathlib import Path
import pytest
from kb import graph, publication
from tools import rom_homology
from tools.kb.tests.test_family_publication import _case, _configure, run
root, operation, phase = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
def killed(*args):
    os.kill(os.getpid(), signal.SIGKILL)
with pytest.MonkeyPatch.context() as patch:
    _configure(root, patch)
    if phase in ('report', 'registry'):
        replacing = publication._replace
        def replace(target, data, mode):
            replacing(target, data, mode)
            expected = 'homology.csv' if phase == 'report' else 'homology.toml'
            if target.name == expected:
                killed()
        patch.setattr(publication, '_replace', replace)
    elif phase == 'check':
        checking = rom_homology.check_report
        def check(*args):
            checking(*args)
            killed()
        patch.setattr(rom_homology, 'check_report', check)
    else:
        patch.setattr(graph, 'sync_held', killed)
    run(_case(root, operation))
'''
    result = subprocess.run([sys.executable, '-c', program, str(sources.root), sources.operation, phase],
                            cwd=sources.root, env=environment, capture_output=True, text=True, timeout=20)
    assert result.returncode == -signal.SIGKILL, result.stderr
    assert publication.pending(sources.root)
    assert project.hook.Guard(repo.ROOT).decide('Bash', {'command': 'uv run kb recover'}) is None
    for arguments in (['brief', '--no-sync'], ['sync'],
                      ['family', 'add', 'existing', '--image', 'NEW', '--layout', 'new',
                       '--census', 'defs/OLD-NEW.census-correspondence.csv']):
        refused = subprocess.run([sys.executable, '-m', 'kb.cli', *arguments], cwd=sources.root,
                                 env=environment, capture_output=True, text=True, timeout=20)
        assert refused.returncode == 6 and 'kb recover' in refused.stderr
    restored = subprocess.run([sys.executable, '-m', 'kb.cli', 'recover', '--json'], cwd=sources.root,
                              env=environment, capture_output=True, text=True, timeout=20)
    assert restored.returncode == 0, restored.stderr
    assert json.loads(restored.stdout)['id']
    assert snapshot(sources.root) == before and not publication.pending(sources.root)
