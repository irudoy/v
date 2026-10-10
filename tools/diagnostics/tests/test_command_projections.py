"""Complete byte checks through the public and ROM diagnostic writers."""

import hashlib
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools' / 'diagnostics'))

from catalog import CatalogError
from check_projection import check
import extract_rom_dtc
import import_370z_logger
import import_ecudocs
import import_nissan_datatable
import import_obd2tools

MODULES = (extract_rom_dtc, import_370z_logger, import_ecudocs,
           import_nissan_datatable, import_obd2tools)


@pytest.fixture(params=MODULES, ids=lambda module: module.__name__)
def projection(request, tmp_path):
    module = request.param
    output = tmp_path / 'output'
    output.mkdir()
    if module is extract_rom_dtc:
        data = []
        writer = lambda directory, rows: module.write(directory / 'descriptors.csv', rows)
    else:
        data = {key: [] for key in ('documents', 'fragments', 'diagnostic_parameters',
                                   'diagnostic_requests', 'diagnostic_operations',
                                   'can_frames', 'can_signals', 'can_bindings',
                                   'request_parameters')}
        data['documents'] = [{'id': 'fixture-doc', 'filename': 'fixture.txt'}]
        data['fragments'] = [{'id': 'fixture-fragment', 'text': 'source fixture\n'}]
        writer = module.write
    writer(output, data)
    (output / 'source_pack.toml').write_text('id = "fixture"\n')
    return module, output, data, writer


def snapshot(output):
    return {p.name: p.read_bytes() for p in output.iterdir() if p.is_file()}


def test_exact_output_set_passes_without_changing_files(projection):
    _, output, data, writer = projection
    before = snapshot(output)
    check(output, data, writer)
    assert snapshot(output) == before
    assert len(list(output.iterdir())) == len(before)


@pytest.mark.parametrize('drift', ['changed', 'missing', 'crlf'])
def test_every_output_drift_is_rejected_and_preserved(projection, drift, subtests):
    _, output, data, writer = projection
    originals = snapshot(output)
    for name, content in originals.items():
        if name == 'source_pack.toml':
            continue
        with subtests.test(file=name, drift=drift):
            path = output / name
            if drift == 'missing':
                path.unlink()
            elif drift == 'crlf':
                changed = content.replace(b'\n', b'\r\n')
                if changed == content:
                    changed += b'\r\n'
                assert changed != content
                path.write_bytes(changed)
            else:
                path.write_bytes(content + b'drift\n')
            before = snapshot(output)
            with pytest.raises(CatalogError, match='missing' if drift == 'missing' else 'differs'):
                check(output, data, writer)
            assert snapshot(output) == before
            path.write_bytes(content)


def test_unexpected_csv_is_rejected_without_deletion(projection):
    _, output, data, writer = projection
    (output / 'extra.csv').write_bytes(b'extra\n')
    before = snapshot(output)
    with pytest.raises(CatalogError, match='unexpected projection file'):
        check(output, data, writer)
    assert snapshot(output) == before


def test_writer_failure_preserves_existing_files(projection):
    _, output, data, _ = projection
    before = snapshot(output)

    def fail(directory, rows):
        (directory / 'partial.csv').write_bytes(b'partial\n')
        raise CatalogError('writer failure')

    with pytest.raises(CatalogError, match='writer failure'):
        check(output, data, fail)
    assert snapshot(output) == before


def test_each_check_cli_rejects_drift_with_nonzero_status(projection, monkeypatch, capsys):
    module, output, data, _ = projection
    (output / 'fragments.jsonl').write_bytes(b'stale\n')
    before = snapshot(output)
    args = SimpleNamespace(source_root=output, source_path=None, layouts=output,
                           output=output / 'descriptors.csv' if module is extract_rom_dtc else output,
                           check=True)
    monkeypatch.setattr(module, 'parser', lambda: SimpleNamespace(parse_args=lambda: args))
    monkeypatch.setattr(module, 'build', lambda *args: data)
    assert module.main() == 1
    assert 'differs from its rendering' in capsys.readouterr().err
    assert snapshot(output) == before


def pin(tmp_path, **changes):
    data = b'identity-check fixture'
    source = tmp_path / 'NissanDatatable.pdf'
    source.write_bytes(data)
    values = dict(filename=source.name, source_url='https://example.com/source.pdf',
                  sha256=hashlib.sha256(data).hexdigest(), pages=7)
    values.update(changes)
    manifest = tmp_path / 'source.toml'
    text = '\n'.join(f'{key} = {value!r}'.replace('True', 'true').replace('False', 'false')
                     for key, value in values.items())
    manifest.write_text(text + '\n')
    return source, manifest


def test_source_pin_selects_and_hashes_the_declared_file(tmp_path):
    source, manifest = pin(tmp_path)
    assert import_nissan_datatable.source_pdf(manifest=manifest) == source.resolve()
    assert import_nissan_datatable.source_pdf(source, manifest=manifest) == source.resolve()


@pytest.mark.parametrize('changes,reason', [
    ({'sha256': '0' * 64}, 'sha256 differs'),
    ({'sha256': 'invalid'}, 'invalid sha256'),
    ({'filename': '../NissanDatatable.pdf'}, 'filename must name one PDF'),
    ({'pages': 8}, 'page contract'),
    ({'pages': True}, 'page contract'),
    ({'source_url': 'http://example.com/source.pdf'}, 'must be HTTPS'),
    ({'unexpected': 'value'}, 'invalid source pin keys'),
])
def test_invalid_source_pin_is_refused(tmp_path, changes, reason):
    _, manifest = pin(tmp_path, **changes)
    with pytest.raises(CatalogError, match=reason):
        import_nissan_datatable.source_pdf(manifest=manifest)


def test_missing_or_renamed_source_is_refused(tmp_path):
    source, manifest = pin(tmp_path)
    renamed = tmp_path / 'different.pdf'
    renamed.write_bytes(source.read_bytes())
    with pytest.raises(CatalogError, match='filename differs'):
        import_nissan_datatable.source_pdf(renamed, manifest=manifest)
    source.unlink()
    with pytest.raises(FileNotFoundError):
        import_nissan_datatable.source_pdf(manifest=manifest)
