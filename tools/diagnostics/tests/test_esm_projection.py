"""ESM inventory and byte-comparison failures preserve existing projections."""
from pathlib import Path
from types import SimpleNamespace
import sys

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools' / 'diagnostics'))
import extract_esm


@pytest.fixture
def catalog():
    return {
        'documents': [{'id':'document'}],
        'discovery': [{'document_id':'document'}],
        'fragments': [{'id':'fragment','text':'retained text\n'}],
        'dtc_definitions': [
            {'id':'first','code':'P0001','ecu_id':'vehicle:ecm'},
            {'id':'second','code':'P0001','ecu_id':'vehicle:ecm'},
            {'id':'third','code':'P0002','ecu_id':'vehicle:bcm'},
        ],
        'diagnostic_parameters': [{'id':'parameter'}],
        'diagnostic_operations': [{'id':'operation'}],
        'can_signals': [{'id':'signal'}],
        'unparsed': [{'id':'gap'}],
    }


def pack_file(tmp_path, counts='expected_documents = 1\n'):
    path=tmp_path/'source_pack.toml'
    path.write_text('id = "fixture"\nvehicle_id = "vehicle"\n'+counts)
    return path


@pytest.mark.parametrize('key', tuple(extract_esm.EXPECTED_COUNTS))
def test_every_declared_inventory_mismatch_names_its_count(tmp_path, catalog, key):
    counts=''.join(f'{name} = {2 if name == key else 1}\n'
                   for name in extract_esm.EXPECTED_COUNTS)
    pack=extract_esm.load_pack(pack_file(tmp_path,counts))
    with pytest.raises(extract_esm.CatalogError) as error:
        extract_esm.validate_inventory(pack,catalog)
    assert f'{key}: extracted 1, expected 2' in str(error.value)


def test_ecm_inventory_counts_unique_codes_across_fragments(tmp_path,catalog):
    pack=extract_esm.load_pack(pack_file(tmp_path,
        ''.join(f'{key} = 1\n' for key in extract_esm.EXPECTED_COUNTS)))
    extract_esm.validate_inventory(pack,catalog)
    assert len(catalog['dtc_definitions'])==3


@pytest.mark.parametrize('value', ['-1','true','"1"'])
def test_invalid_inventory_counts_are_not_coerced(tmp_path,value):
    with pytest.raises(extract_esm.CatalogError,match='nonnegative integer'):
        extract_esm.load_pack(pack_file(tmp_path,f'expected_documents = {value}\n'))


def test_unknown_expected_key_cannot_silently_skip_a_check(tmp_path):
    with pytest.raises(extract_esm.CatalogError,match='expected_can_singals'):
        extract_esm.load_pack(pack_file(tmp_path,
            'expected_documents = 1\nexpected_can_singals = 106\n'))


@pytest.mark.parametrize('check_mode',[False,True])
def test_different_poppler_layout_cannot_publish_an_incomplete_inventory(tmp_path,monkeypatch,capsys,check_mode):
    source=tmp_path/'input';source.mkdir()
    (source/'ENGINE CONTROL SYSTEM.pdf').write_bytes(b'controlled PDF input')
    pack=pack_file(tmp_path,'expected_documents = 1\nexpected_can_signals = 106\n')
    output=tmp_path/'output';output.mkdir()
    (output/'can_signals.csv').write_bytes(b'original projection\n')
    before={p.name:p.read_bytes() for p in output.iterdir()}
    monkeypatch.setattr(extract_esm,'poppler_versions',lambda:{'pdftotext':'24.02.0','pdfinfo':'24.02.0'})
    monkeypatch.setattr(extract_esm,'pdf_pages',lambda path:['No structured section\nEC-1\n'])
    monkeypatch.setattr(extract_esm,'pdf_page_count',lambda path:1)
    args=['extract_esm.py',str(source),'--pack',str(pack),'--output',str(output)]
    if check_mode:args.append('--check')
    monkeypatch.setattr(sys,'argv',args)
    assert extract_esm.main()==1
    captured=capsys.readouterr()
    assert 'expected_can_signals: extracted 0, expected 106' in captured.err
    assert '24.02.0' in captured.out
    assert {p.name:p.read_bytes() for p in output.iterdir()}==before


def test_zero_is_a_valid_declared_count(tmp_path,catalog):
    catalog['can_signals']=[]
    pack=extract_esm.load_pack(pack_file(tmp_path,
        'expected_documents = 1\nexpected_can_signals = 0\n'))
    extract_esm.validate_inventory(pack,catalog)


FILES=('documents.csv','discovery.csv','fragments.jsonl','dtc_definitions.csv',
       'diagnostic_parameters.csv','diagnostic_operations.csv','can_signals.csv','unparsed.csv')


@pytest.mark.parametrize('name',FILES)
@pytest.mark.parametrize('drift',['changed','missing'])
def test_check_detects_each_output_drift_without_replacing_files(tmp_path,catalog,name,drift):
    extract_esm.write(tmp_path,catalog)
    path=tmp_path/name
    if drift=='changed':path.write_bytes(path.read_bytes()+b'\n')
    else:path.unlink()
    before={p.name:p.read_bytes() for p in tmp_path.iterdir()}
    with pytest.raises(extract_esm.CatalogError) as error:
        extract_esm.check(tmp_path,catalog)
    assert str(path) in str(error.value)
    assert {p.name:p.read_bytes() for p in tmp_path.iterdir()}==before


def test_check_refuses_extra_csv_but_retains_source_pack_and_reports(tmp_path,catalog):
    extract_esm.write(tmp_path,catalog)
    (tmp_path/'source_pack.toml').write_text('id = "retained"\n')
    extract_esm.check(tmp_path,catalog)
    (tmp_path/'extra.csv').write_text('unexpected\n')
    before={p.name:p.read_bytes() for p in tmp_path.iterdir()}
    with pytest.raises(extract_esm.CatalogError,match='extra.csv: unexpected projection'):
        extract_esm.check(tmp_path,catalog)
    assert {p.name:p.read_bytes() for p in tmp_path.iterdir()}==before


def test_byte_check_refuses_a_line_ending_change(tmp_path,catalog):
    extract_esm.write(tmp_path,catalog)
    path=tmp_path/'can_signals.csv'
    path.write_bytes(path.read_bytes().replace(b'\n',b'\r\n'))
    with pytest.raises(extract_esm.CatalogError,match='can_signals.csv: differs'):
        extract_esm.check(tmp_path,catalog)


@pytest.mark.parametrize('explicit_output',[False,True])
def test_cli_check_selects_the_output_and_detects_drift(tmp_path,catalog,monkeypatch,capsys,explicit_output):
    pack=pack_file(tmp_path)
    output=tmp_path/'explicit' if explicit_output else tmp_path
    extract_esm.write(output,catalog)
    monkeypatch.setattr(extract_esm,'poppler_versions',lambda:{'pdftotext':'26.09.0','pdfinfo':'26.09.0'})
    monkeypatch.setattr(extract_esm,'build',lambda source,pack:catalog)
    args=['extract_esm.py',str(tmp_path),'--pack',str(pack),'--check']
    if explicit_output:args.extend(['--output',str(output)])
    monkeypatch.setattr(sys,'argv',args)
    assert extract_esm.main()==0
    before=(output/'fragments.jsonl').read_bytes()+b'\n'
    (output/'fragments.jsonl').write_bytes(before)
    assert extract_esm.main()==1
    assert 'fragments.jsonl: differs from extraction' in capsys.readouterr().err
    assert (output/'fragments.jsonl').read_bytes()==before


@pytest.mark.parametrize('stream',['stdout','stderr'])
def test_installed_pdf_tool_versions_are_observed_on_either_stream(monkeypatch,stream):
    calls=[]
    def run(command,**kwargs):
        calls.append(command)
        result={'stdout':'','stderr':''}
        result[stream]=f'{command[0]} version 24.02.0\n'
        return SimpleNamespace(**result)
    monkeypatch.setattr(extract_esm.subprocess,'run',run)
    assert extract_esm.poppler_versions()=={'pdftotext':'24.02.0','pdfinfo':'24.02.0'}
    assert calls==[['pdftotext','-v'],['pdfinfo','-v']]


def test_missing_pdf_tool_names_the_prerequisite(monkeypatch):
    def missing(*args,**kwargs):raise FileNotFoundError('not installed')
    monkeypatch.setattr(extract_esm.subprocess,'run',missing)
    with pytest.raises(extract_esm.CatalogError,match='pdftotext; install Poppler'):
        extract_esm.poppler_versions()
