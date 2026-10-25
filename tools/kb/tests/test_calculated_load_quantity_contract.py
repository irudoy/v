"""Complete stock source, raw paired inputs and fixture-preservation refusals."""
from copy import deepcopy
from pathlib import Path
import hashlib
import pytest
from kb import repo,test_contract
from kb import calculated_load_quantity_contract as contract,calculated_load_quantity_matrix as matrix

def case():return dict(deepcopy(matrix.DEFAULTS),index=0,kind='controlled-source-contract')

@pytest.fixture
def owned():return repo.images(repo.ROOT)['JK08A'].path.read_bytes()

def test_published_counts_and_both_complete_stock_phase_entries_read_the_executed_descriptor():
    declared=contract.descriptor(repo.ROOT)
    assert declared['entries']==[0xB997C,0x8083C]
    assert declared['phases']==[dict(id='producer',entry=0xB997C),dict(id='consumer',entry=0x8083C)]
    assert sum((row['end']-row['start'])//2 for row in declared['unit']['code'])==436
    assert len(declared['unit']['code'])==11 and len(declared['unit']['pools'])==27
    assert len(declared['unit']['aliases'])==9 and len(declared['controlled_calibration'])==30
    assert dict(start=0x26A60,end=0x26ABA) in declared['unit']['code']
    assert declared['observer']=='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
    assert (declared['context_bytes'],declared['frame_bytes'],declared['frame_prefix'])==(80,192,160)

def test_fixture_changes_only_exact_four_byte_pointer_aliases_before_raw_calibration(owned):
    source=contract.descriptor(repo.ROOT);fixture,aliases=contract.independent_fixture(source,owned)
    changed={i for i,(a,b) in enumerate(zip(owned,fixture)) if a!=b}
    allowed={at for row in aliases for at in range(row['address'],row['address']+4)}
    assert changed<=allowed
    for row in source['unit']['code']:assert fixture[row['start']:row['end']]==owned[row['start']:row['end']]
    for row in aliases:
        assert row['width']==4 and row['original']>=0xFFFF0000
        assert int.from_bytes(fixture[row['address']:row['address']+4],'big')==0x01000000+(row['original']&65535)
    wrong=bytearray(owned);wrong[0x8083C]^=1
    with pytest.raises(ValueError):contract.independent_fixture(source,bytes(wrong))

@pytest.mark.parametrize('fault',('bool-word','short-context','bad-SR','bad-curve-byte','synthetic-K','wrong-width'))
def test_raw_input_refuses_lost_width_context_or_an_output_like_handoff_field(fault):
    value=case()
    if fault=='bool-word':value['word_4524']=True
    elif fault=='short-context':value['consumer_context'].pop()
    elif fault=='bad-SR':value['producer_context'][18]=2
    elif fault=='bad-curve-byte':value['curve'][16]=256
    elif fault=='synthetic-K':value['handoff_K']=128
    else:value['word_1024']=65536
    with pytest.raises(ValueError):matrix.require_case(value)

def test_header_contains_two_immutable_contexts_and_raw_inputs_without_supplied_results(owned):
    source=contract.descriptor(repo.ROOT);value=case();declared=dict(source=source,cases=[value])
    raw=matrix.header(declared,owned).decode()
    assert 'struct context contexts[2]' in raw
    body='\n'.join(raw.splitlines()[1:])
    assert 'expected' not in body and 'handoff_K' not in body and 'quotient' not in body
    assert matrix.memory(value)[0x329F]==value['prior_329f']
    assert matrix.context(source,value,0)!=matrix.context(source,value,1)

def test_every_reused_complete_original_source_is_pinned_without_a_helper_summary():
    source=contract.descriptor(repo.ROOT)
    for name,wanted in source['reused_source_sha256'].items():assert hashlib.sha256((Path(repo.ROOT)/name).read_bytes()).hexdigest()==wanted
    for stem in ('division_callees','mixed_curve_caller_withdrawal','paired_curve_normalization_withdrawal'):
        assert any(name.endswith(stem+'_capture_evidence.py') for name in source['reused_source_sha256'])
