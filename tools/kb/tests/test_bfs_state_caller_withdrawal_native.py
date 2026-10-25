"""The shared table correction preserves complete quantities, producer links and TEST context."""
from copy import deepcopy
import json
import pytest
from kb import repo,scalar_ram_leaf_withdrawal_contract as owning
from kb import bfs_state_caller_withdrawal_contract as contract

def test_shared_owner_changes_only_the_two_exact_direct_readers_and_selectors():
    source=owning.descriptor(repo.ROOT)
    selected=[r for r in source['reference'] if r['component'] in ('bfs_state_caller_withdrawal_paths','clamp_latch_caller_withdrawal_paths')]
    assert len(selected)==2 and {r['owner'] for r in selected}=={'nice-coucal/tbl'}
    row,=[r for r in selected if r['component']=='bfs_state_caller_withdrawal_paths']
    assert row['original_claim_sha256']==contract.DECLARED['selected']['original_claim_sha256']
    claim=json.loads(row['original_claim_json'])
    assert (claim['owner'],claim['type'],claim['to'])==('nice-coucal/tbl','reader','ultramarine-taipan/fn')
    assert claim['props']==dict(layouts=['7mfk'],relies='structure',supports='identity')
    before=json.loads(row['original_native_json']);after=json.loads(row['proposed_native_json']);expected=deepcopy(before)
    for selected_row in selected:
        original=json.loads(selected_row['original_claim_json']);target=original['to']
        link,=[r for r in expected['link'] if (r['type'],r['to'])==('reader',target)]
        expected['link'].remove(link);removed=[]
        for ledger in expected['ledger']:
            held=[]
            for item in ledger.get('dependency',[]):
                if (item.get('type'),item.get('to'),item.get('end'))==('reader',target,'owner'):removed.append(item)
                else:held.append(item)
            ledger['dependency']=held
        assert len(removed)==1
    assert after==expected
    for name in ('summary','note','unit','scale','to_raw','scale_level','editor','symbol'):assert after[name]==before[name]
    for reader in ('base_fuel_schedule_producer/fn','startup_initializer/fn'):
        assert any((r['type'],r['to'])==('reader',reader) for r in after['link'])
    assert any(r['type']=='index' and r['to']=='coolant_index/ram' for r in after['link'])
    symbol,=[r for r in after['symbol'] if r['layout']=='7mfk']
    assert symbol['address']=='00015630' and 'width' not in symbol and 'signed' not in symbol

def test_full_function_and_actual_BFS_dependencies_remain_exact():
    source=owning.descriptor(repo.ROOT);row,=[r for r in source['function'] if r['function']==contract.ENTRY]
    before=owning.function_native_document(row,'original');after=owning.function_native_document(row,'proposed')
    assert before==after
    assert before['summary'].startswith('Accessor and state updater.')
    assert before['link']==[dict(type='depends',to='tall-quoll/ram',layouts=['7mfk'],relies='structure',supports='identity',role='consumer')]
    assert any(item.get('to')=='bfs/ram' and item.get('role')=='indexed_by' for ledger in before['ledger'] for item in ledger.get('dependency',[]))

@pytest.mark.parametrize('fault',('summary','producer','semantic-width','TEST-position'))
def test_coherent_native_source_refuses_changes_outside_the_exact_direct_reader_pairs(monkeypatch,fault):
    source=deepcopy(owning.descriptor(repo.ROOT))
    row,=[r for r in source['reference'] if r['component']=='bfs_state_caller_withdrawal_paths']
    value=json.loads(row['proposed_native_json'])
    if fault=='summary':value['summary']='partial source-table summary'
    elif fault=='producer':value['link']=[r for r in value['link'] if r.get('to')!='base_fuel_schedule_producer/fn']
    elif fault=='semantic-width':next(r for r in value['symbol'] if r['layout']=='7mfk')['width']=16
    else:value['ledger'][0]['identity'].pop()
    row['proposed_native_json']=json.dumps(value)
    monkeypatch.setattr(owning.tomllib,'loads',lambda text:source)
    with pytest.raises(ValueError):owning.descriptor(repo.ROOT)
