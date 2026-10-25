"""Normal writer width retirement is exact, explicit and proof dependent."""

from copy import copy
import json
import tomllib
from unittest.mock import patch

import pytest

from kb import compile, copy_evidence, packed_width, reconciliation, repo, test_evidence, write
from kb.repo import KbError


@pytest.fixture(scope='module')
def qualified_source():
    try:
        record = json.loads(copy_evidence._read(repo.ROOT, copy_evidence.RECEIPT))
        record['candidate']['witness']['packed_transfers']
    except (FileNotFoundError, KeyError):
        if test_evidence.REQUIRE_CONTEXTS:
            pytest.fail('the width writer contract requires its original common packed-transfer proof')
        pytest.skip('the original packed-transfer proof is unavailable')
    model = compile.build(repo.ROOT)
    declared = packed_width.contract.descriptor(repo.ROOT)
    field = declared['field'][0]
    symbol = next(value for value in model.symbols.values() if value.key.key == field['symbol'])
    claim = dict(symbol=symbol.key.key, width=field['declared_bits'],
        observed=sorted((row['function'], row['site'], row['mode'], row['width_bytes']) for row in field['observed']))
    packed_width.require(model, symbol, claim, record=record)
    raw = [row for row in reconciliation.differences(model, width_proofs=False) if row['kind'] == 'width']
    review = next(row for row in raw if row['subject'] == symbol.key.key)
    return model, field, review, raw


def pending(source):
    model, field, review, raw = source
    result = copy(model)
    result.config = {**model.config, 'reconciliation':{
        **model.config.get('reconciliation', {}),
        'enabled':True,
        'review':[{**row, 'state':'unresolved', 'reason':row['detail']} for row in raw],
    }}
    return result


def operation(source):
    _, field, review, _ = source
    return dict(cmd='reconcile-width', ref=field['meaning'], layout=field['layout'],
                claim_sha256=review['claim_sha256'])


def test_only_the_explicit_exact_review_retires_with_its_real_original_proof(qualified_source):
    subject = pending(qualified_source)
    held = list(subject.config['reconciliation']['review'])
    change = write.Change(subject, write.model_resolver(subject), repo.ROOT)
    change.run(operation(qualified_source))
    text = reconciliation.rebase(subject, subject, {}, width_resolutions=change.width_resolutions)
    assert text is not None
    after = tomllib.loads(text)['reconciliation']['review']
    wanted = qualified_source[2]
    assert after == [row for row in held if reconciliation.difference_key(row) != reconciliation.difference_key(wanted)]
    assert subject.config['reconciliation']['review'] == held
    assert change.documents == {} and change.removed == set()
    assert next(value for value in subject.symbols.values() if value.key.key == wanted['subject']).value('width') == 8


def test_current_proof_does_not_remove_an_unrequested_review(qualified_source):
    subject = pending(qualified_source)
    assert reconciliation.rebase(subject, subject, {}) is None


@pytest.mark.parametrize('fault', ('claim', 'layout', 'reason', 'l0', 'duplicate', 'proof'))
def test_writer_preserves_reviews_when_an_exact_precondition_fails(qualified_source, fault):
    subject = pending(qualified_source)
    op = operation(qualified_source)
    wanted = qualified_source[2]
    reviews = subject.config['reconciliation']['review']
    index = next(index for index, row in enumerate(reviews)
                 if reconciliation.difference_key(row) == reconciliation.difference_key(wanted))
    if fault == 'claim':
        op['claim_sha256'] = '0' * 64
    elif fault == 'layout':
        op['layout'] = '1nd'
    elif fault == 'reason':
        reviews[index] = {**reviews[index], 'reason':' '}
    elif fault == 'l0':
        reviews[index] = {**reviews[index], 'l0':'0' * 16}
    elif fault == 'duplicate':
        reviews.append(dict(reviews[index]))
    held = list(reviews)
    change = write.Change(subject, write.model_resolver(subject), repo.ROOT)
    if fault == 'proof':
        with patch.object(packed_width, 'require', side_effect=ValueError('missing or stale original')):
            with pytest.raises(KbError):
                change.run(op)
    else:
        with pytest.raises(KbError):
            change.run(op)
    assert subject.config['reconciliation']['review'] == held
    assert change.width_resolutions == {} and change.documents == {}


def test_proof_loss_before_rebase_preserves_the_review_and_refuses_the_expectation(qualified_source):
    subject = pending(qualified_source)
    held = list(subject.config['reconciliation']['review'])
    change = write.Change(subject, write.model_resolver(subject), repo.ROOT)
    change.run(operation(qualified_source))
    with patch.object(packed_width, 'accepted', return_value=None):
        text = reconciliation.rebase(subject, subject, {}, width_resolutions=change.width_resolutions)
    assert text is None
    assert change.expected[0](subject)
    assert subject.config['reconciliation']['review'] == held
