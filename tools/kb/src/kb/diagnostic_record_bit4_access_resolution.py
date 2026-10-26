"""Joint exact indexed bit4 writer proof appends reuse the existing normal link writer."""

from copy import deepcopy
import json

from kb import diagnostic_record_bit4_access_contract as contract, diagnostic_record_bit4_access_evidence as proof
from kb import test_contract


def require_transition(before, after):
    from kb import test_origins, copy_evidence, injection_copy_evidence, coherent_copy_evidence, sid22_evidence
    rows = contract.descriptor(before.root)['reference']
    proof.native_rows(before)
    proof.native_rows(after)
    for row in rows:
        if (sum(contract.original(row, link) for link in before.links) != 1
                or sum(contract.qualified(row, link) for link in after.links) != 1
                or any(contract.original(row, link) for link in after.links)):
            raise ValueError('the indexed bit4 writer publication needs every exact original and owning evidence append')
    old = {key: origin.packet() for key, origin in test_origins.index(before).items()}
    new = {key: origin.packet() for key, origin in test_origins.index(after).items()}
    if not test_contract.exact(old, new):
        raise ValueError('the indexed bit4 writer publication changes an original TEST origin or evidence position')
    for module in (copy_evidence, injection_copy_evidence, coherent_copy_evidence, sid22_evidence):
        if module.scope_digest(before) != module.scope_digest(after):
            raise ValueError('the indexed bit4 writer publication changes an existing physical proof namespace')
    proof.require_current(after)
    return rows


def publication_expected(before, after, before_view):
    from kb import convert
    rows = require_transition(before, after)
    expected = deepcopy(before_view)
    for row in rows:
        old = json.loads(row['original_claim_json'])
        key = row['owner'], old['type'], old['to'], old['slot'], old['offset']
        props, evidence, stated, roles = expected['facts']['links'][key]
        expected['facts']['links'][key] = props, evidence | frozenset((convert._value(after, contract.item(row)),)), stated, roles
    return expected


def retires(before, after, claim):
    if not any(test_contract.exact(contract.plain(claim), json.loads(row['original_claim_json']))
               for row in contract.descriptor(before.root)['reference']):
        return False
    try:
        require_transition(before, after)
        return True
    except (OSError, ValueError, TypeError, KeyError, AttributeError, ImportError, RecursionError):
        return False
