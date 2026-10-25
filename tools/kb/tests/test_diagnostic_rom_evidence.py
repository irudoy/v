"""Joint admission and namespace refusals against the complete actual original."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,sid22_evidence,test_evidence,width_view_matrix
from kb import diagnostic_rom_contract as contract,diagnostic_rom_evidence as proof
from kb.model import Link,SymbolKey


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        sid=json.loads(copy_evidence._read(repo.ROOT,sid22_evidence.RECEIPT))
        for key,consumer in proof.COMPONENTS:record['candidate']['witness'][key]
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:
            pytest.fail('the common B acceptance requires its complete original diagnostic dependency components')
        pytest.skip('the original complete diagnostic dependency components are unavailable')
    model=compile.build(repo.ROOT)
    admitted=proof.require_primary(model,record,sid)
    return model,record,sid,admitted


def test_dependency_requires_the_same_full_original_and_grants_only_its_conditional_scope(original):
    result=original[3]
    assert set(result['components'])=={key for key,consumer in proof.COMPONENTS}
    assert {row['selected'] for row in result['exhaust_bridge']}=={0,1}
    for selected in (0,1):
        assert len({row['output'] for row in result['exhaust_bridge'] if row['selected']==selected})>=2
    for name in ('physical_reader_inference','universal_no_ROM_read','scale_admission',
                 'all_modes','natural_scheduling_inference','hardware_qualification'):
        assert result[name] is False
    assert not hasattr(proof,'RECEIPT')


@pytest.mark.parametrize('field',('process_path','process_sha256','native_model','terminal'))
def test_sid22_and_ROM_paths_cannot_combine_different_original_processes(original,field):
    model,record,sid,_=original
    changed=dict(sid)
    changed[field]='different-original' if field!='terminal' else {**sid[field],'actual_exit_code':1}
    with pytest.raises(ValueError):
        proof.require_sid22(model,contract.descriptor(model.root),changed,record)


def representation(model,row,dependency):
    claim=json.loads(row['proposed_claim_json'] if dependency else row['original_claim_json'])
    meanings={meaning.key:meaning for meaning in model.meanings}
    return Link(meanings[claim['owner']],claim['type'],meanings[claim['to']],claim['slot'],claim['offset'],
        deepcopy(claim['props']),[contract.item(row)] if dependency else [],
        set(claim['stated']),set(claim['sources']),set(claim['roles']))


@pytest.mark.parametrize('row_index',range(4))
def test_sid22_scope_normalizes_only_the_exact_before_and_after_representations(original,row_index):
    model=original[0]
    row=contract.descriptor(model.root)['reference'][row_index]
    position=next(index for index,link in enumerate(model.links)
        if contract.original(row,link) or contract.dependency(row,link))
    held=model.links[position]
    baseline=sid22_evidence.scope_digest(model)
    try:
        for dependency in (False,True):
            model.links[position]=representation(model,row,dependency)
            assert sid22_evidence.scope_digest(model)==baseline
            for field in ('props','stated','sources','evidence'):
                changed=representation(model,row,dependency)
                if field=='props':changed.props['unexpected']='different'
                elif field=='stated':changed.stated.add('1nd')
                elif field=='sources':changed.sources.add('unrelated-native.toml')
                else:changed.evidence.append({'kind':'arithmetic','value':'1=1'})
                model.links[position]=changed
                assert sid22_evidence.scope_digest(model)!=baseline
    finally:
        model.links[position]=held


def encode(memory):
    rows=[]
    start=0
    while start<len(memory):
        end=start+1
        while end<len(memory) and memory[end]==memory[start]:end+=1
        rows.append(f'{end-start}:{memory[start]:02x}')
        start=end
    return ','.join(rows)


@pytest.mark.parametrize('offset',(0x1234,0x1C5F,0x1C5D,0x248B,0x2327))
def test_a_consistent_exhaust_stream_cannot_reset_any_part_of_the_shared_RAM(original,offset):
    witness=original[1]['candidate']['witness']
    surface=witness['byte_surface_paths']
    held=witness['exhaust_target_paths']
    packet=dict(held)
    position=next(index for index,case in enumerate(held['declaration']['cases']) if case['bridge']==1)
    row=dict(held['observations'][position])
    memory=bytearray(width_view_matrix.decode_rle(row['ram_before']))
    memory[offset]^=1
    row['ram_before']=encode(memory)
    packet['observations']=list(held['observations'])
    packet['observations'][position]=row
    lines=held['stdout'].splitlines()
    stream_positions=[index for index,line in enumerate(lines) if line.startswith(proof.exhaust.PREFIX)]
    lines[stream_positions[position]]=proof.exhaust.PREFIX+json.dumps(row)
    packet['stdout']='\n'.join(lines)+'\n'
    packet['stdout_sha256']=hashlib.sha256(packet['stdout'].encode()).hexdigest()
    with pytest.raises(ValueError,match='RAM'):
        proof.require_exhaust_bridge(surface,packet)


@pytest.mark.parametrize('field',('kind','mode','selected','cold','main','bridge'))
def test_bridge_endpoint_selection_cannot_be_relabelled(original,field):
    witness=original[1]['candidate']['witness']
    packet=dict(witness['exhaust_target_paths'])
    declared=deepcopy(packet['declaration'])
    packet['declaration']=declared
    row=next(case for case in declared['cases'] if case['bridge']==1)
    row[field]='hysteresis' if field=='kind' else row[field]^1
    with pytest.raises(ValueError):
        proof.require_exhaust_bridge(witness['byte_surface_paths'],packet)


def test_cached_joint_admission_cannot_keep_a_changed_native_source_origin(original):
    model=original[0]
    proof.require_current(model)
    row=contract.descriptor(model.root)['reference'][0]
    symbol=model.symbols[SymbolKey('7mfk','ram',row['RAM_address'])]
    sources=symbol.sources
    try:
        symbol.sources={*sources,'different-native-source.toml'}
        with pytest.raises(ValueError):proof.require_current(model)
    finally:
        symbol.sources=sources
