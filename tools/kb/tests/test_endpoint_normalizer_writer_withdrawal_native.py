"""One exact writer/selector correction retains the complete shared native images."""
from copy import deepcopy
import json
import pytest
from kb import repo, scalar_ram_leaf_withdrawal_contract as owning
from kb import request_limit_normalization_access_contract as positive
from kb import endpoint_normalizer_writer_withdrawal_contract as contract


def selected():
    rows = [r for r in owning.descriptor(repo.ROOT)['reference']
        if r['component'] == 'endpoint_normalizer_writer_withdrawal_paths']
    assert len(rows) == 1
    return rows[0]


def test_exact_writer_and_owner_end_selector_are_the_only_native_changes():
    row = selected()
    assert row['original_claim_sha256'] == contract.DECLARED['selected']['original_claim_sha256']
    original = json.loads(row['original_claim_json'])
    assert (original['owner'], original['type'], original['to']) == ('fluffy-salamander/ram', 'writer', 'aromatic-coua/fn')
    assert original['props'] == dict(layouts=['7mfk'], relies='level', supports='identity')
    before = json.loads(row['original_native_json'])
    after = json.loads(row['proposed_native_json'])
    expected = deepcopy(before)
    links = [r for r in expected['link'] if (r['type'], r['to']) == ('writer', 'aromatic-coua/fn')]
    assert len(links) == 1
    expected['link'].remove(links[0])
    removed = []
    for ledger in expected['ledger']:
        retained = []
        for item in ledger.get('dependency', []):
            if (item.get('type'), item.get('to'), item.get('end')) == ('writer', 'aromatic-coua/fn', 'owner'):
                assert item['role'] == 'writes' and item['relies'] == 'level'
                removed.append(item)
            else:
                retained.append(item)
        if retained:
            ledger['dependency'] = retained
        elif 'dependency' in ledger:
            ledger.pop('dependency')
    assert len(removed) == 1 and after == expected
    assert after['unit'] == before['unit'] == 'bitfield'
    assert after['summary'] == before['summary'] and after['note'] == before['note']
    assert after['symbol'] == before['symbol']
    symbol, = [r for r in after['symbol'] if r['layout'] == '7mfk']
    assert symbol['address'] == 'ffff41fb' and 'width' not in symbol and 'signed' not in symbol
    assert any((r['type'], r['to']) == ('writer', 'malachite-ferret/fn') for r in after['link'])
    assert any((r['type'], r['to']) == ('writer', 'power_balance_mask_update/fn') for r in after['link'])


def test_complete_function_matches_the_full_existing_positive_package_and_retains_all_outputs():
    source = owning.descriptor(repo.ROOT)
    function, = [r for r in source['function'] if r['function'] == contract.ENTRY]
    prior, = [r for r in positive.descriptor(repo.ROOT)['retained_functions'] if r['address'] == contract.ENTRY]
    before = owning.function_native_document(function, 'original')
    after = owning.function_native_document(function, 'proposed')
    assert before == after == json.loads(prior['native_json'])
    assert not any(item.get('to') == 'fluffy-salamander/ram' for ledger in before['ledger'] for item in ledger.get('dependency', []))
    outputs = {item['to'] for ledger in before['ledger'] for item in ledger.get('dependency', []) if item.get('role') == 'writes'}
    assert outputs == {'onyx-axolotl/ram', 'origami-curassow/ram', 'real-orca/ram'}


@pytest.mark.parametrize('fault', ('summary', 'unrelated-writer', 'semantic-width', 'selector-evidence'))
def test_coherent_native_descriptor_refuses_partial_or_broadened_owner_changes(monkeypatch, fault):
    document = deepcopy(owning.descriptor(repo.ROOT))
    row, = [r for r in document['reference'] if r['component'] == 'endpoint_normalizer_writer_withdrawal_paths']
    value = json.loads(row['proposed_native_json'])
    if fault == 'summary':
        value['summary'] = 'partial status-byte summary'
    elif fault == 'unrelated-writer':
        value['link'] = [r for r in value['link'] if r.get('to') != 'malachite-ferret/fn']
    elif fault == 'semantic-width':
        next(r for r in value['symbol'] if r['layout'] == '7mfk')['width'] = 8
    else:
        value['ledger'][0]['identity'].pop()
    row['proposed_native_json'] = json.dumps(value)
    monkeypatch.setattr(owning.tomllib, 'loads', lambda text: document)
    with pytest.raises(ValueError):
        owning.descriptor(repo.ROOT)
