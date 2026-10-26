"""Projection checks reject different bytes even when CSV text is equivalent."""

import csv
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import census_homology as census
import rom_homology as homology
from patches import can_telemetry_profile as profile
from tools.mapkit import dtc_projection as dtc
from kb import project


@pytest.fixture(params=['rom-report', 'census', 'profile', 'dtc', 'native-file', 'native-section'])
def projection(request, tmp_path, monkeypatch):
    path = tmp_path / 'output.csv'
    content = 'key,value\nfixture,1\n'
    if request.param == 'rom-report':
        monkeypatch.setattr(homology, 'build_report', lambda: content)
        check = lambda: homology.main(['--check', '--output', str(path)])
    elif request.param == 'census':
        content = census.render_ledger([])
        monkeypatch.setattr(census.rom_sources, 'l0_dir', lambda rom: tmp_path)
        monkeypatch.setattr(census.rom_homology, 'load_images',
                            lambda: {name: SimpleNamespace(data=b'fixture') for name in ('1ND0A', '1ME3B')})
        monkeypatch.setattr(census, 'read_entities', lambda *args: [])
        monkeypatch.setattr(census, 'reference_votes', lambda *args: {})
        monkeypatch.setattr(census, 'published_pairs', lambda *args: {})
        monkeypatch.setattr(census, 'build_ledger', lambda *args: [])
        monkeypatch.setattr(census, 'validate_ledger', lambda *args: {})
        monkeypatch.setattr(census, 'render_summary', lambda summary: 'fixture summary')
        check = lambda: census.main(['--check', '--output', str(path)])
    elif request.param == 'profile':
        manifest = object()
        monkeypatch.setattr(profile, 'load_manifest', lambda source: manifest)
        monkeypatch.setattr(profile, 'render_tables', lambda actual: content)
        monkeypatch.setattr(profile, 'render_schema', lambda actual: 'schema fixture\n')
        monkeypatch.setattr(profile, 'render_identity', lambda actual: 'identity fixture\n')
        schema, identity = tmp_path / 'schema.json', tmp_path / 'identity.h'
        schema.write_bytes(b'schema fixture\n')
        identity.write_bytes(b'identity fixture\n')

        def check():
            try:
                profile.generate(tables=path, schema=schema, identity=identity, check=True)
            except ValueError:
                return 1
            return 0
    elif request.param == 'dtc':
        monkeypatch.setattr(dtc, 'DEFS', tmp_path)
        rows = [{field: 'fixture' for field in dtc.FIELDS}]
        monkeypatch.setattr(dtc, 'INHERITED_ROMS', ())
        monkeypatch.setattr(dtc.romkit, 'load', lambda rom: SimpleNamespace(data=b'fixture'))
        monkeypatch.setattr(dtc, 'project', lambda rom, **kwargs: (rows, []))
        path = dtc.write_registry('TARGET', rows)
        content = path.read_text()

        def read(rom):
            if rom == dtc.SOURCE_ROM:
                return rows
            with path.open(newline='') as source:
                return list(csv.DictReader(source))

        monkeypatch.setattr(dtc, 'read_registry', read)
        check = lambda: dtc.main(['TARGET'])
    elif request.param == 'native-file':
        entry = {'path': path.name, 'generator': 'kb.project:fixture'}
        monkeypatch.setattr(project, 'renderings', lambda root, selected: {path.name: content})
        check = lambda: int(bool(project._compare(tmp_path, entry, [path.name])))
    else:
        path = tmp_path / 'document.md'
        begin, end = project.markers('fixture')
        expected = '\nfixture body\n'
        content = 'Manual prefix\n' + begin + expected + end + '\nManual suffix\n'
        entry = {'path': path.name + '#fixture'}
        check = lambda: int(project.current(tmp_path, entry) != expected)
    path.write_bytes(content.encode())
    return path, check


def test_canonical_bytes_pass_without_writing(projection):
    path, check = projection
    original = path.read_bytes()
    before = path.stat().st_mtime_ns
    assert check() == 0
    assert path.read_bytes() == original
    assert path.stat().st_mtime_ns == before


def test_crlf_difference_is_refused_and_preserved(projection):
    path, check = projection
    changed = path.read_bytes().replace(b'\n', b'\r\n')
    path.write_bytes(changed)
    before = path.stat().st_mtime_ns
    assert check() != 0
    assert path.read_bytes() == changed
    assert path.stat().st_mtime_ns == before


def test_dtc_check_mode_cannot_write():
    with pytest.raises(SystemExit) as error:
        dtc.main(['--check', '--write'])
    assert error.value.code == 2


@pytest.mark.parametrize('section', [False, True])
def test_native_writer_compares_exact_bytes_and_preserves_manual_sections(tmp_path, monkeypatch, section):
    path = tmp_path / 'fixture.txt'
    expected = '\ncanonical body\n'
    begin, end = project.markers('fixture')
    prefix, suffix = 'Manual prefix\r\n' + begin, end + '\r\nManual suffix\r\n'
    old = prefix + expected.replace('\n', '\r\n') + suffix if section else expected.replace('\n', '\r\n')
    path.write_bytes(old.encode())
    entry = {'path': path.name + ('#fixture' if section else ''), 'generator': 'kb.project:fixture'}
    monkeypatch.setattr(project, 'load', lambda root: [entry])
    monkeypatch.setattr(project, 'generator', lambda selected: lambda root: expected)
    before = path.stat().st_mtime_ns
    assert project.write(tmp_path, check=True) == [(entry['path'], True)]
    assert path.read_bytes() == old.encode()
    assert path.stat().st_mtime_ns == before
    assert project.write(tmp_path) == [(entry['path'], True)]
    assert path.read_bytes() == (prefix + expected + suffix if section else expected).encode()
    assert project.write(tmp_path, check=True) == [(entry['path'], False)]
