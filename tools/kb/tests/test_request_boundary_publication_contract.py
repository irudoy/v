"""Complete source binding, raw widths and exact fixture-preservation refusals."""
from copy import deepcopy
from pathlib import Path
import hashlib
import re
import pytest
from kb import repo
from kb import request_boundary_publication_contract as contract,request_boundary_publication_matrix as matrix

def case():return dict(deepcopy(matrix.DEFAULTS),index=0,kind='complete-source-contract')

@pytest.fixture
def owned():return repo.images(repo.ROOT)['JK08A'].path.read_bytes()

def test_documented_counts_and_complete_natural_entry_read_the_executed_descriptor():
    source=contract.descriptor(repo.ROOT)
    assert source['entries']==[0x79DD8]
    assert sum((row['end']-row['start'])//2 for row in source['unit']['code'])==1132
    assert len(source['unit']['code'])==17 and len(contract.FUNCTIONS)==14
    assert len(source['unit']['pools'])==81 and len(source['unit']['aliases'])==21
    assert len(source['controlled_calibration'])==94
    assert dict(start=0x26A60,end=0x26ABA) in source['unit']['code']
    assert source['observer']=='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
    assert (source['context_bytes'],source['frame_bytes'],source['frame_prefix'])==(80,192,160)
    assert source['actual_writer']==dict(owner_entry=0x79DD8,actual_entry=0x79030,
        native_address=0xFFFF19C6,width_bytes=2,sites=[0x791A8,0x791B2])
    text=(Path(repo.ROOT)/'defs/JK08A.request-boundary-publication.md').read_text()
    count=re.search(r'binds (\d+) stock instructions, (\d+) instruction bytes,\s+(\d+) contiguous spans, and (\d+) complete source bodies',text)
    assert count is not None and tuple(map(int,count.groups()))==(1132,2264,17,14)
    count=re.search(r'binds (\d+) literal pools, (\d+) four-byte RAM pointer\s+aliases, and (\d+) calibration spans',text)
    assert count is not None and tuple(map(int,count.groups()))==(81,21,94)

def test_fixture_changes_only_declared_four_byte_RAM_pools_and_preserves_all_code(owned):
    source=contract.descriptor(repo.ROOT);fixture,aliases=contract.independent_fixture(source,owned)
    changed={index for index,(a,b) in enumerate(zip(owned,fixture)) if a!=b}
    allowed={at for row in aliases for at in range(row['address'],row['address']+4)}
    assert changed<=allowed
    for row in source['unit']['code']:assert fixture[row['start']:row['end']]==owned[row['start']:row['end']]
    for row in aliases:
        assert row['width']==4 and row['original']>=0xFFFF0000
        assert int.from_bytes(fixture[row['address']:row['address']+4],'big')==0x01000000+(row['original']&65535)
    broken=bytearray(owned);broken[0x79DE2]^=1
    with pytest.raises(ValueError):contract.independent_fixture(source,bytes(broken))

@pytest.mark.parametrize('fault',('bool-word','short-context','bad-SR','bad-array-byte','output-field','wrong-width'))
def test_input_contract_refuses_lost_raw_widths_context_and_supplied_results(fault):
    value=case()
    if fault=='bool-word':value['word_2438']=True
    elif fault=='short-context':value['context'].pop()
    elif fault=='bad-SR':value['context'][18]=2
    elif fault=='bad-array-byte':value['curve_12e1a'][15]=256
    elif fault=='output-field':value['expected_19c6']=128
    else:value['word_3480']=65536
    with pytest.raises(ValueError):matrix.require_case(value)

def test_private_header_has_complete_context_and_inputs_without_supplied_arithmetic(owned):
    source=contract.descriptor(repo.ROOT);value=case()
    text=matrix.header(dict(source=source,cases=[value]),owned).decode()
    assert 'struct context context' in text and 'uint32_t ram[48]' in text
    assert 'expected' not in text and 'quotient' not in text and 'signed_value' not in text
    assert matrix.memory(value)[0x19C6:0x19C8]==bytes.fromhex('a55a')

def test_complete_existing_original_sources_and_numeric_helpers_retain_exact_bindings():
    source=contract.descriptor(repo.ROOT)
    for name,wanted in source['reused_source_sha256'].items():
        assert hashlib.sha256((Path(repo.ROOT)/name).read_bytes()).hexdigest()==wanted
    for stem in ('division_callees','adorable_llama','counter_threshold','register_only_helpers'):
        assert any(name.endswith(stem+'_capture_evidence.py') for name in source['reused_source_sha256'])
    assert 'tools/kb/src/kb/arrogant_catfish_semantics.py' in source['reused_source_sha256']
    assert 'tools/kb/src/kb/byte_surface_semantics.py' in source['reused_source_sha256']
