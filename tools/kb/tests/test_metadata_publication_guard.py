"""Metadata publication preserves all semantic values and original TEST positions."""

from copy import deepcopy
from types import SimpleNamespace

import pytest

from kb import copy_evidence, repo, write
from kb.repo import KbError


def meaning(key, kind):
    return SimpleNamespace(key=key, kind=kind, semantic=True, symbols={}, props={}, tables={},
        other_names=[], statuses={}, sources={'controlled-native.toml'},
        name_sources=('controlled-native.toml',), tier=0)


@pytest.fixture
def pair(tmp_path):
    owner = meaning(copy_evidence.MEMBERS['reader'][0], 'ram')
    function = meaning('coherent_snapshot/fn', 'fn')
    owner.props['width'] = 8
    owner.statuses['1me3b'] = SimpleNamespace(state='unresolved', props={'method':'controlled'},
        evidence=[{'kind':'test', 'path':'controlled-test.py', 'key':'test_status'}], sources={'controlled-native.toml'})
    original_test = {'kind':'test', 'path':'controlled-test.py', 'key':'test_identity', 'supports':'identity'}
    link = SimpleNamespace(owner=owner, to=function, type='reader', slot=None, offset=None,
        props={}, evidence=[original_test], stated=[], roles=[], sources={'controlled-native.toml'})
    before = SimpleNamespace(root=tmp_path, symbols={}, meanings=[owner,function], links=[link],
        entities={}, targets={}, layouts={}, spaces={}, functions={}, names=[],
        config={'reconciliation':{'enabled':True,'review':[]}})
    after = deepcopy(before)
    after.links[0].evidence.append(copy_evidence.item('reader'))
    path = tmp_path / repo.OWNER_CONFIG
    path.parent.mkdir(parents=True)
    path.write_text('controlled preimage')
    operation = dict(cmd='link', meaning=owner.key, type='reader', to=function.key,
                     evidence=[copy_evidence.item('reader')])
    return before, after, [operation], SimpleNamespace(width_resolutions={}), {repo.OWNER_CONFIG:'controlled metadata'}


def test_exact_proof_append_preserves_original_claim_values_and_test_positions(pair):
    write.require_metadata_only(*pair)
    assert pair[0].links[0].evidence == pair[1].links[0].evidence[:-1]


@pytest.mark.parametrize('fault', ('semantic-width', 'status-evidence', 'status-property', 'status-source',
                                  'status-order', 'nested-evidence-order', 'target',
                                  'configuration', 'source-origin', 'insert-before-test', 'remove-test', 'wrong-proof',
                                  'ledger-selector'))
def test_other_metadata_and_semantics_cannot_use_the_publication_phase(pair, fault):
    before, after, operations, change, texts = pair
    if fault == 'semantic-width':
        after.meanings[0].props['width'] = 32
    elif fault == 'status-evidence':
        after.meanings[0].statuses['1me3b'].evidence.append({'kind':'test','path':'other.py','key':'test_other'})
    elif fault == 'status-property':
        after.meanings[0].statuses['1me3b'].props['method'] = 'different'
    elif fault == 'status-source':
        after.meanings[0].statuses['1me3b'].sources = {'other-native.toml'}
    elif fault == 'status-order':
        second = {'kind':'test', 'path':'controlled-test.py', 'key':'test_second_status'}
        before.meanings[0].statuses['1me3b'].evidence.append(second)
        after.meanings[0].statuses['1me3b'].evidence.insert(0, second)
    elif fault == 'nested-evidence-order':
        items = [{'kind':'test','path':'controlled.py','key':key} for key in ('test_a','test_b')]
        before.meanings[0].tables['controlled'] = {'evidence':items}
        after.meanings[0].tables['controlled'] = {'evidence':items[::-1]}
    elif fault == 'target':
        after.targets['controlled'] = SimpleNamespace(status='supported', props={})
    elif fault == 'configuration':
        after.config['execution'] = {'selector':123}
    elif fault == 'source-origin':
        after.meanings[0].sources = {'different-native.toml'}
    elif fault == 'insert-before-test':
        after.links[0].evidence.reverse()
    elif fault == 'remove-test':
        after.links[0].evidence.pop(0)
    elif fault == 'ledger-selector':
        before.stash={'ledger_rows':[('ram','controlled',[{'registry':'vars','order':1,
            'dependency':[{'role':'consumer','to':'controlled/fn','type':'reader'}]}],'controlled-native.toml')]}
        after.stash=deepcopy(before.stash)
        after.stash['ledger_rows'][0][2][0]['dependency'][0]['to']='different/fn'
    else:
        after.links[0].evidence[-1] = {**after.links[0].evidence[-1], 'at':'7mfk:00021094'}
    with pytest.raises(KbError):
        write.require_metadata_only(before, after, operations, change, texts)


def test_review_removal_requires_its_explicit_exact_resolution_key(pair):
    before, after, operations, change, texts = pair
    review = {'kind':'width', 'subject':'controlled-field/ram', 'claim_sha256':'a' * 64}
    before.config['reconciliation']['review'] = [review]
    with pytest.raises(KbError, match='unrequested review'):
        write.require_metadata_only(before, after, operations, change, texts)
    change.width_resolutions[review['subject']] = review['claim_sha256']
    operations.append(dict(cmd='reconcile-width', ref='controlled-field/ram', layout='1me3b',
                           claim_sha256=review['claim_sha256']))
    write.require_metadata_only(before, after, operations, change, texts)


@pytest.mark.parametrize('operation', (
    {'cmd':'set', 'ref':'controlled-field/ram', 'keys':{'width':32}},
    {'cmd':'rename', 'meaning':'controlled-field/ram', 'name':'different'},
    {'cmd':'absent', 'meaning':'controlled-field/ram', 'layout':'1me3b'},
    {'cmd':'link', 'type':'target', 'evidence':[copy_evidence.item('reader')]},
    {'cmd':'link', 'type':'reader', 'keys':{'supports':'scale'}, 'evidence':[copy_evidence.item('reader')]},
    {'cmd':'link', 'type':'reader', 'evidence':[{'kind':'test','path':'controlled.py','key':'test_ordinary'}]},
))
def test_publication_batch_rejects_nonpublication_operations_before_execution(operation):
    with pytest.raises(KbError):
        write.require_publication_operations([operation])


@pytest.mark.parametrize('fault', ('create', 'remove', 'unowned'))
def test_metadata_publication_cannot_create_remove_or_write_other_files(pair, fault):
    before, after, operations, change, texts = pair
    if fault == 'create':
        (before.root / repo.OWNER_CONFIG).unlink()
    elif fault == 'remove':
        texts[repo.OWNER_CONFIG] = None
    else:
        from pathlib import Path
        texts[Path('unowned.txt')] = 'unrequested content'
    with pytest.raises(KbError):
        write.require_metadata_only(before, after, operations, change, texts)
