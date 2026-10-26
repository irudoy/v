"""Exact natural closure, independent two-lane equations and input-only transport."""
from copy import deepcopy
import re
import pytest
from kb import repo
from kb import an1_source_dispatch_access_contract as contract
from kb import an1_source_dispatch_access_matrix as matrix
from kb import an1_source_dispatch_access_semantics as numeric


def case(**changes):
    return dict(matrix.DEFAULTS,**changes,entry=contract.ENTRY,kind='controlled-source',index=0)


def test_published_closure_counts_and_native_premises_read_the_executed_declaration():
    source=contract.descriptor(repo.ROOT)
    text=(repo.ROOT/'defs/JK08A.an1-source-dispatch-access-paths.md').read_text()
    found=re.search(r'binds (\d+) complete function\s+bodies and (\d+) literal pools',text)
    assert found is not None and tuple(map(int,found.groups()))==(len(source['unit']['code']),len(source['unit']['pools']))==(22,63)
    assert source['entries']==[0x3D832] and 0x26A60 in contract.FUNCTIONS and 0x26A80 not in contract.FUNCTIONS
    assert source['native_control_bytes']==dict(addresses=[0xFFFF84C3],window_start=0xFFFF8400,window_size=256)
    assert source['selected']['physical_table_bytes']==32 and source['selected']['native_geometry_inference'] is False
    assert (source['context_bytes'],source['frame_bytes'],source['frame_prefix'])==(80,192,160)


@pytest.mark.parametrize('fault',('entry','bool-byte','wide-byte','wide-word','bad-SR','supplied-result'))
def test_complete_inputs_reject_lost_width_changed_scope_and_supplied_outputs(fault):
    value=case()
    if fault=='entry':value['entry']+=2
    elif fault=='bool-byte':value['ram_84c3']=True
    elif fault=='wide-byte':value['cal_12dea']=256
    elif fault=='wide-word':value['ram_1d58']=65536
    elif fault=='bad-SR':value['initial_sr']=2
    else:value['expected_PID']=100
    with pytest.raises(ValueError):matrix.require_case(value)


def test_independent_curve_uses_exact_byte_neighbors_fraction_and_endpoint():
    ascending=bytes(range(0,256,8));descending=bytes(reversed(ascending))
    assert numeric.curve(ascending,4)==dict(index=0,fraction=32768,value=4,endpoint=False)
    assert numeric.curve(descending,4)==dict(index=0,fraction=32768,value=244,endpoint=False)
    assert numeric.curve(ascending,248)==numeric.curve(ascending,255)==dict(index=31,fraction=0,value=248,endpoint=True)


def test_independent_full_sequence_preserves_actual_filter_minimum_and_PID_order():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    value=case(cal_08b34=0,cal_08b42=0,cal_08cef=255,cal_08cce=255,cal_08b5b=0)
    result=numeric.sequence(matrix.memory(value),matrix.calibrations(source,image,value));ram=result['ram']
    assert int.from_bytes(ram[0x2832:0x2834],'big')==512
    assert int.from_bytes(ram[0x2834:0x2836],'big')==544
    assert tuple(ram[at] for at in (0x3F3E,0x3F44))==(3,3)
    assert result['temperature_codes']==(128,136) and result['PID']==(118,126)
    assert result['publication']==ram[0x3F41]==118 and result['running_minimum']==(128,136)
    assert tuple(ram[at] for at in (0x1174,0x1175,0x1176))==(188,188,201)
    assert next(i for i,r in enumerate(result['writes']) if r['site']==0x3D8C6)>max(
        i for i,r in enumerate(result['writes']) if r['site'] in (0x3D4DA,0x3D4E6))


@pytest.mark.parametrize('field',('entries','native_control_bytes','unit','selected','native_identity_admission'))
def test_exact_descriptor_rejects_changed_body_native_window_or_admission(monkeypatch,field):
    value=deepcopy(contract.DECLARED);value[field]=False
    monkeypatch.setattr(contract.tomllib,'loads',lambda text:value)
    with pytest.raises(ValueError):contract.descriptor(repo.ROOT)


def test_fixture_relocates_only_declared_full_pointer_pools_and_header_contains_no_oracle():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image)
    changed={i for i,(a,b) in enumerate(zip(image,fixture)) if a!=b}
    assert changed<={i for row in aliases for i in range(row['address'],row['address']+4)}
    for start,end in contract.SPANS:assert fixture[start:end]==image[start:end]
    raw=matrix.header(dict(source=source,cases=[case()]),image).decode()
    assert 'struct context context' in raw and all(word not in raw for word in ('expected','computed','terminal','result'))
