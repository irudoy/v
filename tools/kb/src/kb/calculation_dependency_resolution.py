"""Batch-only exact transition of registered conditional calculation claims."""

from copy import deepcopy
import json
from pathlib import Path
import re

from kb import calculation_dependency_contract as contract
from kb import calculation_dependency_evidence as proof
from kb import test_contract
from kb.model import SymbolKey
from kb.repo import KbError


def operation_shape(op):
    return (type(op) is dict and set(op) == {'cmd', 'id', 'claim_sha256'}
            and op['cmd'] == 'reconcile-calculation-dependency'
            and any(op['id'] == family + ':' + key and op['claim_sha256'] == original
                    for family, key, owner, address, original, proposed in contract.IDENTITIES))


def via_reference(value, model):
    match = re.fullmatch(r"SymbolKey\(layout='7mfk', kind='fn', address=([0-9]+)\)", value)
    if match is None:
        raise ValueError('the calculation disposition has an undeclared via reference')
    key = SymbolKey('7mfk', 'fn', int(match[1]))
    if key not in model.symbols:
        raise ValueError('the calculation disposition via function has no current native symbol')
    return key.location


def prepare(change, op):
    from kb import reconciliation
    if not operation_shape(op):
        raise KbError('reconcile-calculation-dependency needs one exact registered original claim', code=3)
    rows = proof.native_rows(change.model)
    row = next(row for row in rows if row['operation_id'] == op['id'])
    if row['operation_id'] in change.calculation_resolutions:
        raise KbError('reconcile-calculation-dependency repeats an original claim', code=3)
    symbol = change.model.symbols[contract.symbol_key(row)]
    links = [link for link in change.model.links if contract.original(row, link)]
    if len(links) != 1:
        raise KbError('reconcile-calculation-dependency needs its complete unchanged original reader', code=3)
    questions = [item for item in reconciliation.differences(change.model)
                 if item['kind'] == 'access' and item['subject'] == symbol.key.key
                 and item['claim_sha256'] == row['original_claim_sha256']]
    if len(questions) != 1:
        raise KbError('reconcile-calculation-dependency names no exact current raw access question', code=3)
    question = questions[0]
    reviews = [item for item in change.model.config.get('reconciliation', {}).get('review', ())
               if isinstance(item, dict) and reconciliation.difference_key(item) == reconciliation.difference_key(question)]
    if (len(reviews) != 1 or set(reviews[0]) != set(question) | {'state', 'reason'}
            or reviews[0].get('state') != 'unresolved' or type(reviews[0].get('reason')) is not str
            or not reviews[0]['reason'].strip()
            or any(not test_contract.exact(reviews[0].get(key), value) for key, value in question.items())):
        raise KbError('reconcile-calculation-dependency needs its complete exact retained unresolved review', code=3)
    try:
        proof.require_current(change.model, family=row['family'])
    except (OSError, ValueError, TypeError, KeyError, AttributeError, ImportError, RecursionError) as error:
        raise KbError(f'reconcile-calculation-dependency lacks its exact qualified original: {error}', code=3) from None
    path, document = change.document(symbol.meaning)
    old, new = json.loads(row['original_claim_json']), json.loads(row['proposed_claim_json'])
    if path != Path(old['sources'][0]) or not (change.root / path).is_file():
        raise KbError('reconcile-calculation-dependency needs its existing exact owned native file', code=3)
    if not test_contract.exact(document.get('ledger'), json.loads(row['original_ledger_json'])):
        raise KbError('reconcile-calculation-dependency needs its complete exact original ledger', code=3)
    target = change.model.symbols[contract.target(row, proposed=False)].meaning
    candidates = [(index, entry) for index, entry in enumerate(document.get('link', ()))
                  if change._same_link(entry, {'type': 'reader'}, target)]
    if len(candidates) != 1:
        raise KbError('reconcile-calculation-dependency needs one exact original document relation', code=3)
    index, entry = candidates[0]
    replacement = deepcopy(entry)
    replacement.update(type='depends', to=new['to'], role=row['role'], note=new['props']['note'],
                       via=[via_reference(value, change.model) for value in new['props']['via']])
    if row['family'] in ('closed-loop-sample','closed-loop-feedback'):
        replacement.update(relies='structure', supports='identity')
    evidence = contract.item(row)
    evidence['to'] = evidence['to'].location
    replacement['evidence'] = [evidence]
    document['link'][index] = replacement
    document['ledger'] = json.loads(row['proposed_ledger_json'])
    change.calculation_resolutions[row['operation_id']] = row['original_claim_sha256']
    if len(change.calculation_resolutions) == 1:
        def complete(result):
            try:
                require_transition(change.model, result, change.calculation_resolutions)
            except (OSError, ValueError, TypeError, KeyError, AttributeError, ImportError, RecursionError) as error:
                return f'the calculation transition is incomplete or unqualified: {error}'
            return None
        change.expected.append(complete)
    change.lines.append(f'reconcile calculation {row["operation_id"]}: {row["original_claim_sha256"]}; exact conditional execution')


def require_transition(before, after, resolutions):
    from kb import test_origins, copy_evidence, injection_copy_evidence, coherent_copy_evidence, sid22_evidence
    rows = contract.rows(before.root)
    if not test_contract.exact(resolutions, {row['operation_id']: row['original_claim_sha256'] for row in rows}):
        raise ValueError('the calculation transition requires every exact registered original claim')
    proof.native_rows(before)
    proof.native_rows(after)
    for row in rows:
        if (sum(contract.original(row, link) for link in before.links) != 1
                or sum(contract.dependency(row, link) for link in after.links) != 1
                or any(contract.original(row, link) for link in after.links)):
            raise ValueError('the calculation transition substitutes or retains an original relation')
    old = {key: origin.packet() for key, origin in test_origins.index(before).items()}
    new = {key: origin.packet() for key, origin in test_origins.index(after).items()}
    if not test_contract.exact(old, new):
        raise ValueError('the calculation transition changes an original TEST context or attachment')
    for module in (copy_evidence, injection_copy_evidence, coherent_copy_evidence, sid22_evidence):
        if module.scope_digest(before) != module.scope_digest(after):
            raise ValueError('the calculation transition changes an existing physical proof namespace')
    proof.require_current(after)
    return rows


def retires(before, after, claim, resolutions):
    if contract.digest(contract.plain(claim)) not in resolutions.values():
        return False
    try:
        rows = require_transition(before, after, resolutions)
        return any(test_contract.exact(contract.plain(claim), json.loads(row['original_claim_json'])) for row in rows)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, ImportError, RecursionError):
        return False


def publication_expected(before, after, resolutions, before_view, after_view):
    rows = require_transition(before, after, resolutions)
    expected = deepcopy(before_view)
    ledger = {row['owner']: json.loads(row['proposed_ledger_json']) for row in rows}
    expected['ordered']['native_ledgers'] = [(kind, name, ledger.get(f'{name}/{kind}', items), source)
                                            for kind, name, items, source in expected['ordered']['native_ledgers']]
    for row in rows:
        old, new = json.loads(row['original_claim_json']), json.loads(row['proposed_claim_json'])
        old_key = row['owner'], 'reader', old['to'], None, None
        new_key = row['owner'], 'depends', new['to'], None, None
        for section in (expected['facts']['links'], expected['origins']['links']):
            if old_key not in section or new_key in section:
                raise ValueError('the calculation transition changes its exact relation namespace')
            del section[old_key]
        expected['facts']['links'][new_key] = after_view['facts']['links'][new_key]
        expected['origins']['links'][new_key] = after_view['origins']['links'][new_key]
    return expected
