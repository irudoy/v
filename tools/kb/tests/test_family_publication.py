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

from kb import cli, compile, family, graph, l0, lock, names, project, publication, repo, write
from kb.adapters import interp
from kb.repo import KbError
from tools import census_homology, rom_homology


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


def run(case, *, dry_run=False, report='defs/registries/OLD-NEW.census-correspondence.csv'):
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


def test_first_layout_exports_from_a_draft_and_publishes_with_its_bindings(
    tmp_path, monkeypatch, capsys
):
    _sources(tmp_path)
    checked_layout = l0.check_layout
    state = _configure(tmp_path, monkeypatch)
    monkeypatch.setattr(l0, 'check_layout', checked_layout)
    monkeypatch.setattr(family, 'census', CENSUS)
    catalog = repo.images(tmp_path)
    (tmp_path / repo.CONFIG).parent.mkdir(parents=True)
    (tmp_path / repo.CONFIG).write_text(
        '[l0]\nscripts = []\n[l0.census.new]\ninterp = "defs/registries/NEW.interp.csv"\n')
    (tmp_path / repo.GHIDRA_PIN).parent.mkdir(parents=True)
    (tmp_path / repo.GHIDRA_PIN).write_text('GHIDRA_VERSION=12.1.4\n')
    registry = tmp_path / 'defs/registries/NEW.interp.csv'
    registry.parent.mkdir(parents=True)
    batch = tmp_path / 'new-bindings.toml'
    batch.write_text('[[op]]\ncmd = "bind"\nmeaning = "fixture/fn"\n'
                     'symbol = "new:00000008"\n')
    (tmp_path / 'defs/registries/OLD-NEW.census-correspondence.csv').write_text(
        ','.join(census_homology.LEDGER_FIELDS) + '\n'
        'map,00008300,8x1:uint8:step16,homolog,00008300,8x1:uint8:step16,aligned-reference,yes,\n')
    original = snapshot(tmp_path)
    parser = cli.build_parser()
    args = ['family', 'new', 'onboarded', '--image', 'NEW', '--layout', 'new',
            '--mcu', 'SH7058', '--flash-size', '0x9000', '--software-id', 'FIXTURE']
    assert cli.command_family(parser.parse_args(args + ['--draft']), tmp_path) == 0
    draft = tmp_path / 'proposal.toml'
    draft.write_text(capsys.readouterr().out)
    stale = tmp_path / 'stale.toml'
    stale.write_text(draft.read_text().replace('code_start = 0x8200', 'code_start = 0x8202'))
    with pytest.raises(KbError, match='draft must add one family to the current registry'):
        family.draft_layout('new', stale, tmp_path)
    assert 'new' not in repo.layouts(tmp_path)
    assert snapshot(tmp_path) == original

    stage = tmp_path / 'stage'
    stage.mkdir()
    (stage / 'program.txt').write_text('NEW.bin\n')
    (stage / 'program.sha256').write_text(catalog['NEW'].sha256 + '\n')
    for filename, columns in l0.CORE.items():
        content = ','.join(name for name, _ in columns) + '\n'
        if filename == 'funcs.csv':
            content += '00000008,2,false,false\n'
        (stage / filename).write_text(content)
    (stage / l0.Census.file('8')).write_text(
        ','.join(name for name, _ in l0.ACCESSORS) + '\n'
        '00000008,00000008,,00000008,00000008,orig,,,,00008300,,,,pool,none,none,none,agree,\n')
    plan = tmp_path / 'proposed.interp.csv'
    text = ','.join(interp.FIELDS) + '\nimplicit,00000008,00000008,8,,16,uint8,,\n'
    plan.write_text(text)
    assert l0.export('new', from_stage=stage, family_draft=draft, interp_draft=plan, root=tmp_path)
    assert snapshot(tmp_path) == original and not registry.exists()

    def bind(ops, model, resolve, root, *, strict):
        assert strict and ops == write.read_batch(batch) and model is state.model and root == tmp_path
        return None, {}, model

    monkeypatch.setattr(write, 'model_resolver', lambda model: None)
    monkeypatch.setattr(write, 'plan', bind)
    monkeypatch.setattr(interp, 'owners', lambda model: {'defs/registries/NEW.interp.csv': 'new'})
    generated = {'defs/registries/NEW.interp.csv': text.replace('00000008', '0000000a')}
    monkeypatch.setattr(interp, 'render_registries', lambda model: generated)
    publish = args + ['--census', 'defs/registries/OLD-NEW.census-correspondence.csv', '--batch', str(batch)]
    with pytest.raises(KbError, match='family L0 gate fails: .*differs from'):
        cli.command_family(parser.parse_args(publish + ['--dry-run']), tmp_path)
    assert snapshot(tmp_path) == original and not registry.exists()
    generated['defs/registries/NEW.interp.csv'] = text
    assert cli.command_family(parser.parse_args(publish + ['--dry-run']), tmp_path) == 0
    assert 'b/defs/registries/NEW.interp.csv' in capsys.readouterr().out
    assert snapshot(tmp_path) == original and not registry.exists()

    def failed_sync(*args):
        assert registry.read_text() == text and 'new' in repo.layouts(tmp_path)
        raise KbError('controlled initial binding synchronization refusal')

    with monkeypatch.context() as failing:
        failing.setattr(graph, 'sync_held', failed_sync)
        with pytest.raises(KbError, match='initial binding synchronization refusal'):
            cli.command_family(parser.parse_args(publish), tmp_path)
    assert str(registry.relative_to(tmp_path)) in publication.recover(tmp_path, status=True)['paths']
    publication.recover(tmp_path)
    assert snapshot(tmp_path) == original and not registry.exists()

    assert cli.command_family(parser.parse_args(publish), tmp_path) == 0
    assert state.synchronized and registry.read_text() == text
    assert l0.check_all(tmp_path, only=['new']) == [] and not publication.pending(tmp_path)


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
                       '--census', 'defs/registries/OLD-NEW.census-correspondence.csv']):
        refused = subprocess.run([sys.executable, '-m', 'kb.cli', *arguments], cwd=sources.root,
                                 env=environment, capture_output=True, text=True, timeout=20)
        assert refused.returncode == 6 and 'kb recover' in refused.stderr
    restored = subprocess.run([sys.executable, '-m', 'kb.cli', 'recover', '--json'], cwd=sources.root,
                              env=environment, capture_output=True, text=True, timeout=20)
    assert restored.returncode == 0, restored.stderr
    assert json.loads(restored.stdout)['id']
    assert snapshot(sources.root) == before and not publication.pending(sources.root)
