"""Exact leaf boundary, independent arithmetic and input-only transport refusals."""
from copy import deepcopy
import re
import pytest
from kb import repo
from kb import shifted_word_accumulator_withdrawal_contract as contract
from kb import shifted_word_accumulator_withdrawal_matrix as matrix
from kb import shifted_word_accumulator_withdrawal_semantics as semantics


def case(**changes):
    return dict(matrix.DEFAULTS,**changes,entry=contract.ENTRY,kind='controlled-source',index=0)


def test_published_counts_read_the_complete_executed_source_boundary():
    source=contract.descriptor(repo.ROOT)
    actual=(sum((r['end']-r['start'])//2 for r in source['unit']['code']),len(source['unit']['code']),
        len(source['unit']['pools']),len(source['unit']['aliases']),len(source['configuration']))
    text=(repo.ROOT/'defs/JK08A.shifted-word-accumulator-withdrawal-paths.md').read_text()
    found=re.search(r'binds (\d+) stock\s+instructions in one natural function span, (\d+) literal pools, three four-byte\s+RAM pointer aliases and three scalar calibration inputs',text)
    assert found is not None and tuple(map(int,found.groups()))==(actual[0],actual[2])
    assert actual==(82,1,10,3,3) and source['entries']==[0xA5398]
    assert source['native_control_bytes']==dict(addresses=[0xFFFF84C3],window_start=0xFFFF8400,window_size=256)
    assert source['unit']['pools'][0]==dict(address=0xA54C0,size=2,stock_hex='84c3')
    assert (source['context_bytes'],source['frame_bytes'],source['frame_prefix'])==(80,192,160)


@pytest.mark.parametrize('fault',('entry','bool-gate','wide-byte','wide-word','bad-SR','supplied-result'))
def test_input_contract_refuses_lost_width_changed_entry_or_supplied_results(fault):
    value=case()
    if fault=='entry':value['entry']+=2
    elif fault=='bool-gate':value['native_gate']=True
    elif fault=='wide-byte':value['shift']=256
    elif fault=='wide-word':value['prior']=65536
    elif fault=='bad-SR':value['initial_sr']=2
    else:value['expected_word']=1000
    with pytest.raises(ValueError):matrix.require_case(value)


@pytest.mark.parametrize('field',('entries','native_control_bytes','unit','selected','native_identity_admission'))
def test_complete_descriptor_rejects_changed_natural_physical_or_native_scope(monkeypatch,field):
    value=deepcopy(contract.DECLARED);value[field]=False
    monkeypatch.setattr(contract.tomllib,'loads',lambda text:value)
    with pytest.raises(ValueError):contract.descriptor(repo.ROOT)


def test_independent_equations_bind_strict_gate_shift_cap_and_final_word_boundaries():
    equation=semantics.accumulation
    assert equation(0,64,200,32768,1000,128,8,17)['updated']==0
    assert equation(32,0,200,32768,1000,128,8,17)['updated']==1000
    assert equation(32,64,17,32768,1000,128,8,17)['updated']==1000
    assert equation(32,64,200,32768,1000,128,0,17)['updated']==1045
    assert equation(32,64,200,32768,1000,128,8,17)['updated']==1255
    zero=equation(32,64,200,0,1000,128,255,17)
    assert zero['count']==255 and zero['shifted']==0 and zero['updated']==1000
    saturated=equation(32,64,255,65535,65535,255,8,0)
    assert saturated['scale']==65279 and saturated['final_saturated'] and saturated['updated']==65535


def test_fixture_changes_only_declared_full_pointer_pools_and_header_has_only_complete_inputs():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image)
    changed={i for i,(a,b) in enumerate(zip(image,fixture)) if a!=b}
    assert changed<={at for row in aliases for at in range(row['address'],row['address']+4)}
    for start,end in contract.SPANS:assert fixture[start:end]==image[start:end]
    assert fixture[0xA54C0:0xA54C2]==image[0xA54C0:0xA54C2]
    raw=matrix.header(dict(source=source,cases=[case()]),image).decode()
    assert 'struct context context' in raw and 'uint32_t ram[5]' in raw
    assert all(name not in raw for name in ('expected','computed','terminal','result'))
