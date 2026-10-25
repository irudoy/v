"""Exact I/O native transition with existing symbol-evidence attachment."""

from copy import deepcopy
import json
from pathlib import Path

from kb import io_access_claim_contract as contract, io_access_evidence as proof, test_contract
from kb.repo import KbError


def operation_shape(op):
    return (type(op) is dict and set(op) == {'cmd', 'id', 'claim_sha256'} and op['cmd'] == 'reconcile-io-access'
            and any(op['id'] == row[0] and op['claim_sha256'] == row[8] for row in contract.IDENTITIES))


def prepare(change, op):
    from kb import reconciliation, write
    if not operation_shape(op):
        raise KbError('reconcile-io-access needs one exact registered original claim', code=3)
    row = next(row for row in proof.native_rows(change.model) if row['id'] == op['id'])
    if row['id'] in change.io_resolutions:
        raise KbError('reconcile-io-access repeats an original claim', code=3)
    symbol = change.model.symbols[contract.symbol_key(row)]
    if sum(contract.original(row, link) for link in change.model.links) != 1:
        raise KbError('reconcile-io-access needs its complete unchanged original relation', code=3)
    questions = [item for item in reconciliation.differences(change.model) if item['kind'] == 'access'
                 and item['subject'] == symbol.key.key and item['claim_sha256'] == row['original_claim_sha256']]
    if len(questions) != 1:
        raise KbError('reconcile-io-access names no exact current raw access question', code=3)
    question = questions[0]
    reviews = [item for item in change.model.config.get('reconciliation', {}).get('review', ())
               if isinstance(item, dict) and reconciliation.difference_key(item) == reconciliation.difference_key(question)]
    if (len(reviews) != 1 or set(reviews[0]) != set(question) | {'state', 'reason'}
            or reviews[0].get('state') != 'unresolved' or type(reviews[0].get('reason')) is not str
            or not reviews[0]['reason'].strip()
            or any(not test_contract.exact(reviews[0].get(key), value) for key, value in question.items())):
        raise KbError('reconcile-io-access needs its complete exact retained unresolved review', code=3)
    try:
        proof.require_current(change.model)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, ImportError, RecursionError) as error:
        raise KbError(f'reconcile-io-access lacks its exact qualified original: {error}', code=3) from None
    path, document = change.document(symbol.meaning)
    if (path != Path(row['source']) or not (change.root / path).is_file()
            or not test_contract.exact(document, json.loads(row['original_native_json']))):
        raise KbError('reconcile-io-access needs the complete exact existing native document', code=3)
    old = json.loads(row['original_claim_json'])
    indices = [index for index, link in enumerate(document.get('link', ()))
               if link['type'] == old['type'] and link['to'] == old['to']]
    if len(indices) != 1:
        raise KbError('reconcile-io-access needs its one exact original document relation', code=3)
    evidence = write.evidence_item(contract.item(row))
    if row['disposition'] == 'relocate-site-evidence':
        entry = next(entry for entry in document['symbol'] if entry['layout'] == '7mfk'
                     and int(entry['address'], 16) == row['address'])
        entry['evidence'] = [*entry.get('evidence', ()), evidence]
        del document['link'][indices[0]]
    else:
        entry = document['link'][indices[0]]
        entry['evidence'] = [*entry.get('evidence', ()), evidence]
    if not test_contract.exact(document, json.loads(row['proposed_native_json'])):
        raise KbError('reconcile-io-access changes another native field, ledger or evidence position', code=3)
    change.io_resolutions[row['id']] = row['original_claim_sha256']
    if len(change.io_resolutions) == 1:
        def complete(result):
            try:
                require_transition(change.model, result, change.io_resolutions)
            except (OSError, ValueError, TypeError, KeyError, AttributeError, ImportError, RecursionError) as error:
                return f'the I/O transition is incomplete or unqualified: {error}'
            return None
        change.expected.append(complete)
    change.lines.append(f'reconcile I/O {row["id"]}: {row["original_claim_sha256"]}; exact bounded execution')


def require_transition(before, after, resolutions):
    from kb import test_origins, copy_evidence, injection_copy_evidence, coherent_copy_evidence, sid22_evidence
    rows = contract.descriptor(before.root)['reference']
    if not test_contract.exact(resolutions, {row['id']: row['original_claim_sha256'] for row in rows}):
        raise ValueError('the I/O transition requires every exact registered original question')
    proof.native_rows(before)
    proof.native_rows(after)
    for row in rows:
        if sum(contract.original(row, link) for link in before.links) != 1:
            raise ValueError('the I/O transition lacks an exact unchanged original relation')
        symbol = after.symbols[contract.symbol_key(row)]
        if row['disposition'] == 'relocate-site-evidence':
            if (any(contract.original(row, link) for link in after.links)
                    or not test_contract.exact(contract.plain(symbol.evidence),
                                               json.loads(row['proposed_symbol_evidence_json']))):
                raise ValueError('the captured-word attribution changes its exact removal or owning evidence append')
        elif sum(contract.qualified(row, link) for link in after.links) != 1:
            raise ValueError('the I/O transition changes its exact owning link-proof append')
    old = {key: origin.packet() for key, origin in test_origins.index(before).items()}
    new = {key: origin.packet() for key, origin in test_origins.index(after).items()}
    if not test_contract.exact(old, new):
        raise ValueError('the I/O transition changes an original TEST context or evidence position')
    for module in (copy_evidence, injection_copy_evidence, coherent_copy_evidence, sid22_evidence):
        if module.scope_digest(before) != module.scope_digest(after):
            raise ValueError('the I/O transition changes an existing physical proof namespace')
    proof.require_current(after)
    return rows


def publication_expected(before, after, resolutions, before_view, after_view):
    from kb import convert
    rows = require_transition(before, after, resolutions)
    expected = deepcopy(before_view)
    for row in rows:
        old = json.loads(row['original_claim_json'])
        key = row['owner'], old['type'], old['to'], old['slot'], old['offset']
        if key not in expected['facts']['links']:
            raise ValueError('the I/O publication substitutes its original relation namespace')
        encoded = convert._value(after, contract.item(row))
        if row['disposition'] == 'relocate-site-evidence':
            del expected['facts']['links'][key]
            del expected['origins']['links'][key]
            symbol_key = contract.symbol_key(row)
            fact_key = symbol_key.location, symbol_key.kind
            fields = list(expected['facts']['symbols'][fact_key])
            fields[4] = fields[4] | frozenset((encoded,))
            expected['facts']['symbols'][fact_key] = tuple(fields)
            props, evidence, former = expected['ordered']['symbols'][symbol_key]
            expected['ordered']['symbols'][symbol_key] = props, [*evidence, contract.item(row)], former
        else:
            props, evidence, stated, roles = expected['facts']['links'][key]
            expected['facts']['links'][key] = props, evidence | frozenset((encoded,)), stated, roles
    return expected


def retires(before, after, claim, resolutions):
    if contract.digest(contract.plain(claim)) not in resolutions.values():
        return False
    try:
        rows = require_transition(before, after, resolutions)
        return any(test_contract.exact(contract.plain(claim), json.loads(row['original_claim_json'])) for row in rows)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, ImportError, RecursionError):
        return False
