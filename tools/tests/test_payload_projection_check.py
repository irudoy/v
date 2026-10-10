"""Read-only manifest gates retain independent GNU reconstruction and locks."""

from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

TOOL_DIR = Path(__file__).resolve().parents[1] / 'sh-elf-run'
sys.path.insert(0, str(TOOL_DIR))
import generate_runtime_targets as generator

CONTENT = '# payload fixture\nschema_version = 1\n[units]\nentry = "0009000b"\n'


@pytest.fixture(params=['runtime', 'telemetry'])
def manifest(request, tmp_path, monkeypatch):
    path = tmp_path / 'payloads.toml'
    calls = []
    if request.param == 'telemetry':
        monkeypatch.setattr(generator.can_telemetry_assembly, 'DEFAULT_PAYLOADS', path)
        monkeypatch.setattr(generator, 'build_telemetry', lambda: calls.append('telemetry') or CONTENT)
        monkeypatch.setattr(generator, 'build_locks', lambda rom: pytest.fail('wrong payload family'))
        flags = ['--telemetry']
    else:
        monkeypatch.setattr(generator.runtime_targets, 'DEFAULT_PAYLOADS', path)
        monkeypatch.setattr(generator.runtime_targets, 'RELOCATED_ROMS', ('FIRST', 'SECOND'))
        monkeypatch.setattr(generator, 'build_locks', lambda rom: calls.append(rom) or rom)
        monkeypatch.setattr(generator, 'render', lambda locks: CONTENT if locks == ['FIRST', 'SECOND'] else '')
        monkeypatch.setattr(generator, 'build_telemetry', lambda: pytest.fail('wrong payload family'))
        flags = []
    return path, flags, calls


def test_exact_manifest_passes_without_writing(manifest, capsys):
    path, flags, calls = manifest
    path.write_bytes(CONTENT.encode())
    before = path.stat().st_mtime_ns
    assert generator.main(flags + ['--check']) == 0
    assert path.read_bytes() == CONTENT.encode()
    assert path.stat().st_mtime_ns == before
    assert calls == (['telemetry'] if flags else ['FIRST', 'SECOND'])
    assert 'status=PASS' in capsys.readouterr().out


@pytest.mark.parametrize('content', [
    CONTENT.replace('0009000b', '000b0009').encode(),
    CONTENT.replace('\n', '\r\n').encode(),
    CONTENT.replace('\n', '\r').encode(),
    CONTENT.encode() + b'\n',
    CONTENT.encode()[:-1],
    b'\xff' + CONTENT.encode(),
])
def test_different_bytes_fail_without_replacement(manifest, content, capsys):
    path, flags, _ = manifest
    path.write_bytes(content)
    before = path.stat().st_mtime_ns
    with pytest.raises(SystemExit) as error:
        generator.main(flags + ['--check'])
    assert error.value.code == 2
    assert path.read_bytes() == content
    assert path.stat().st_mtime_ns == before
    captured = capsys.readouterr()
    assert 'status=PASS' not in captured.out
    assert 'generated payloads differ' in captured.err


def test_missing_manifest_is_refused_without_creation(manifest, capsys):
    path, flags, _ = manifest
    with pytest.raises(SystemExit) as error:
        generator.main(flags + ['--check'])
    assert error.value.code == 2
    assert not path.exists()
    assert 'status=PASS' not in capsys.readouterr().out


def test_explicit_output_is_compared_instead_of_default(manifest, tmp_path):
    default, flags, _ = manifest
    default.write_bytes(b'unrelated\n')
    output = tmp_path / 'explicit.toml'
    output.write_bytes(CONTENT.encode())
    assert generator.main(flags + ['--output', str(output), '--check']) == 0
    assert default.read_bytes() == b'unrelated\n'


def test_generation_writes_the_same_bytes(manifest):
    path, flags, _ = manifest
    assert generator.main(flags) == 0
    assert path.read_bytes() == CONTENT.encode()
    assert generator.main(flags + ['--check']) == 0


def test_reconstruction_failure_cannot_publish_or_replace_output(manifest, monkeypatch, capsys):
    path, flags, _ = manifest
    path.write_bytes(b'previous\n')

    def fail(*args):
        raise generator.verify_map_switching.VerificationError('GNU assembly failure')

    monkeypatch.setattr(generator, 'build_telemetry' if flags else 'build_locks', fail)
    with pytest.raises(generator.verify_map_switching.VerificationError, match='GNU assembly failure'):
        generator.main(flags + ['--check'])
    assert path.read_bytes() == b'previous\n'
    assert 'status=PASS' not in capsys.readouterr().out


@pytest.mark.parametrize('projected', [False, True])
def test_each_unit_uses_the_primary_fill_aware_assembler(projected, tmp_path, monkeypatch):
    units = (SimpleNamespace(key='first'), SimpleNamespace(key='second'))
    source_texts = {'first': 'relocated first', 'second': 'relocated second'} if projected else {}
    layout = SimpleNamespace(assembly_units=units, source_text_by_unit=source_texts)
    parsed = {'first': object(), 'second': object()}
    calls = []

    def assemble(unit, instructions, directory, *, source_text):
        calls.append((unit.key, instructions, directory, source_text))
        return b'first' if unit.key == 'first' else b'second'

    monkeypatch.setattr(generator.verify_map_switching, 'assemble_unit', assemble)
    assert generator._assemble(layout, parsed, tmp_path, canonical=not projected) == {'first': b'first', 'second': b'second'}
    assert calls == [('first', parsed['first'], tmp_path, source_texts.get('first')),
                     ('second', parsed['second'], tmp_path, source_texts.get('second'))]


def test_relocated_unit_cannot_fall_back_to_canonical_source(tmp_path, monkeypatch):
    layout = SimpleNamespace(assembly_units=(SimpleNamespace(key='missing'),),
                             source_text_by_unit={})
    monkeypatch.setattr(generator.verify_map_switching, 'assemble_unit',
                        lambda *args, **kwargs: pytest.fail('missing projected source reaches GNU'))
    with pytest.raises(KeyError, match='missing'):
        generator._assemble(layout, {'missing': object()}, tmp_path)


@pytest.mark.parametrize('refuse', [None, 'structure', 'source', 'assembly', 'instructions', 'composition', 'render'])
def test_telemetry_locks_precede_manifest_publication(refuse, monkeypatch):
    layout = object()
    parsed = object()
    blobs = object()
    calls = []
    build_directory = []

    def step(name, value):
        calls.append(name)
        if name == refuse:
            raise ValueError(f'{name} lock fails')
        return value

    monkeypatch.setattr(generator.can_telemetry_layout, 'load_layout', lambda: layout)
    monkeypatch.setattr(generator.can_telemetry_layout, 'validate_structure',
                        lambda actual: step('structure', None) if actual is layout else pytest.fail())
    monkeypatch.setattr(generator.can_telemetry_assembly, 'validate_assembly_sources',
                        lambda actual: step('source', parsed) if actual is layout else pytest.fail())

    def assemble(actual, instructions, directory, *, canonical):
        assert actual is layout and instructions is parsed
        assert canonical is True
        assert directory.is_dir()
        build_directory.append(directory)
        return step('assembly', blobs)

    monkeypatch.setattr(generator, '_assemble', assemble)
    monkeypatch.setattr(generator.can_telemetry_assembly, 'validate_instruction_semantics',
                        lambda actual, instructions, data: step('instructions', None)
                        if (actual is layout and instructions is parsed and data is blobs) else pytest.fail())
    monkeypatch.setattr(generator.can_telemetry_compose, 'compose',
                        lambda **values: step('composition', None)
                        if values == dict(layout=layout, blobs=blobs) else pytest.fail())
    monkeypatch.setattr(generator.can_telemetry_assembly, 'render_payloads',
                        lambda actual, data: step('render', CONTENT)
                        if actual is layout and data is blobs else pytest.fail())
    stages = ['structure', 'source', 'assembly', 'instructions', 'composition', 'render']
    if refuse:
        with pytest.raises(ValueError, match=f'{refuse} lock fails'):
            generator.build_telemetry()
        assert calls == stages[:stages.index(refuse) + 1]
    else:
        assert generator.build_telemetry() == CONTENT
        assert calls == stages
    assert all(not directory.exists() for directory in build_directory)
