"""Both complete surfaces and the full native function retain every unrelated field."""
from copy import deepcopy
import json
import pytest
from kb import repo
from kb import scalar_ram_leaf_withdrawal_contract as owning
from kb import shifted_word_accumulator_withdrawal_contract as contract


def selected():
    return [row for row in owning.descriptor(repo.ROOT)['reference'] if row['component']=='shifted_word_accumulator_withdrawal_paths']


def test_only_two_exact_direct_readers_and_their_owner_selectors_are_removed():
    rows=selected()
    assert len(rows)==2
    for row,wanted in zip(rows,contract.DECLARED['selected']):
        assert row['original_claim_sha256']==wanted['original_claim_sha256']
        claim=json.loads(row['original_claim_json'])
        assert (claim['owner'],claim['to'],claim['type'])==(wanted['owner'],'hungry-mushroom/fn','reader')
        before=json.loads(row['original_native_json']);after=json.loads(row['proposed_native_json']);expected=deepcopy(before)
        links=[r for r in expected['link'] if (r['type'],r['to'])==('reader','hungry-mushroom/fn')]
        assert len(links)==1;expected['link'].remove(links[0]);removed=[]
        for ledger in expected.get('ledger',[]):
            retained=[]
            for item in ledger.get('dependency',[]):
                if (item.get('type'),item.get('to'),item.get('end'))==('reader','hungry-mushroom/fn','owner'):
                    assert item['role']=='consumer' and item['relies']=='structure';removed.append(item)
                else:retained.append(item)
            if 'dependency' in ledger:
                if retained:ledger['dependency']=retained
                else:ledger.pop('dependency')
        assert len(removed)==1 and after==expected
        assert len(after['diagnostic'])==4 and after['unit']=='raw' and after['scale']=='x'
        assert after['symbol']==before['symbol'] and after['editor']==before['editor']
        assert after['summary']==before['summary'] and after['note']==before['note']
        assert any(r.get('to')=='vague-ringtail/fn' for r in after['link'])
        assert all(key not in after['symbol'][0] for key in ('width','signed','cols','rows','storage'))
        assert any(item.get('to')=='nebulous-porpoise/ram' for ledger in after['ledger'] for item in ledger.get('dependency',[]))


def test_complete_natural_function_preserves_every_native_property_and_TEST_position():
    source=owning.descriptor(repo.ROOT)
    function,=[r for r in source['function'] if r['function']==contract.ENTRY]
    before=owning.function_native_document(function,'original');after=owning.function_native_document(function,'proposed')
    assert before==after and function['owner']=='hungry-mushroom/fn'
    assert set(before)=={'symbol'} and before['symbol'][0]['address']=='000a5398'
    assert before['symbol'][0]['evidence']==[dict(kind='l0',supports='identity',at='7mfk:000a5398')]


@pytest.mark.parametrize('fault',('diagnostic','reader','reverse','geometry','TEST','ledger-order'))
def test_native_boundary_refuses_broadened_surface_or_selector_edits(monkeypatch,fault):
    value=deepcopy(owning.descriptor(repo.ROOT));row=next(r for r in value['reference'] if r['component']=='shifted_word_accumulator_withdrawal_paths')
    document=json.loads(row['proposed_native_json'])
    if fault=='diagnostic':document['diagnostic'].pop()
    elif fault=='reader':document['link'].pop(0)
    elif fault=='reverse':document['link'][-1].pop('reverse_relies')
    elif fault=='geometry':document['symbol'][0]['cols']=8
    elif fault=='TEST':document['symbol'][0]['evidence'].append(dict(kind='test',path='changed',key='changed'))
    else:document['ledger'][-1]['dependency'].reverse()
    row['proposed_native_json']=json.dumps(document)
    monkeypatch.setattr(owning.tomllib,'loads',lambda text:value)
    with pytest.raises(ValueError):owning.descriptor(repo.ROOT)
