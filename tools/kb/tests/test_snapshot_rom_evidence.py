"""Actual original cached snapshot dependency and exact COPY namespaces."""

from copy import deepcopy
import hashlib,json
import pytest
from kb import compile,copy_evidence,repo,test_evidence,width_view_matrix
from kb import injection_copy_evidence,coherent_copy_evidence,sid22_evidence
from kb import snapshot_rom_contract as contract,snapshot_rom_evidence as proof
from kb.model import Link


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['publication_inhibit_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires its complete snapshot-ROM original')
        pytest.skip('the original complete snapshot-ROM component is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    return model,record,packet,result


def test_snapshot_admission_requires_a_positive_table_cache_publication_copy_sequence(original):
    result=original[3]
    assert result['sequences'] and len({row['snapshot'] for row in result['sequences']})>=2
    assert all(row['source_bytes']==row['destination_bytes'] for row in result['sequences'])
    for key in ('physical_reader_inference','universal_no_ROM_read','scale_admission',
            'natural_scheduling_inference','hardware_qualification'):assert result[key] is False
    assert not hasattr(proof,'RECEIPT')


@pytest.mark.parametrize('module',(copy_evidence,injection_copy_evidence,coherent_copy_evidence,sid22_evidence))
def test_snapshot_exact_representations_preserve_each_existing_physical_namespace(original,module):
    model=original[0];row=contract.descriptor(model.root)['reference'][0]
    meanings={meaning.key:meaning for meaning in model.meanings}
    position=next(index for index,link in enumerate(model.links) if contract.original(row,link) or contract.dependency(row,link))
    held=model.links[position];baseline=module.scope_digest(model)
    try:
        for dependency in (False,True):
            claim=json.loads(row['proposed_claim_json'] if dependency else row['original_claim_json'])
            model.links[position]=Link(meanings[claim['owner']],claim['type'],meanings[claim['to']],
                claim['slot'],claim['offset'],deepcopy(claim['props']),[contract.item(row)] if dependency else [],
                set(claim['stated']),set(claim['sources']),set(claim['roles']))
            assert module.scope_digest(model)==baseline
    finally:model.links[position]=held


def encode(memory):
    rows=[];start=0
    while start<len(memory):
        end=start+1
        while end<len(memory) and memory[end]==memory[start]:end+=1
        rows.append(f'{end-start}:{memory[start]:02x}');start=end
    return ','.join(rows)


@pytest.mark.parametrize('stage,offset',((1,0x1234),(1,0x2459),(1,0x257A),(2,0x1234),(2,0x1072)))
def test_consistent_snapshot_stream_cannot_reset_or_substitute_any_intermediate_RAM(original,stage,offset):
    held=original[2];packet=dict(held)
    position=next(index for index,case in enumerate(held['declaration']['cases'])
        if case['stage']==stage and case['initial_mode']==0 and case['brake']==0 and case['fault']==1)
    row=dict(held['observations'][position]);memory=bytearray(width_view_matrix.decode_rle(row['ram_before']))
    memory[offset]^=1;row['ram_before']=encode(memory)
    packet['observations']=list(held['observations']);packet['observations'][position]=row
    lines=held['stdout'].splitlines();positions=[index for index,line in enumerate(lines) if line.startswith(proof.execution.PREFIX)]
    lines[positions[position]]=proof.execution.PREFIX+json.dumps(row)
    packet['stdout']='\n'.join(lines)+'\n';packet['stdout_sha256']=hashlib.sha256(packet['stdout'].encode()).hexdigest()
    with pytest.raises(ValueError):proof.positive_sequences(packet,original[3]['component'])


def test_snapshot_proof_cannot_replace_positive_alternatives_with_a_constant_result(original):
    packet=original[2];component=deepcopy(original[3]['component'])
    for row,case in zip(component['semantic_results'],packet['declaration']['cases']):
        row['conditional_positive_path']=(row['conditional_positive_path']
            and case['pattern']=='flat' and case['flat']==0)
    with pytest.raises(ValueError):proof.positive_sequences(packet,component)
