"""Exact twelve-relation withdrawals through the existing normal unlink writer."""

from copy import deepcopy
import json

from kb import test_contract
from kb import register_only_withdrawal_contract as contract,register_only_withdrawal_evidence as proof


def require_transition(before,after):
    from kb import test_origins,copy_evidence,injection_copy_evidence,coherent_copy_evidence,sid22_evidence
    rows=proof.native_rows(before,'original');proof.native_rows(after,'proposed')
    old={key:origin.packet() for key,origin in test_origins.index(before).items()}
    new={key:origin.packet() for key,origin in test_origins.index(after).items()}
    if not test_contract.exact(old,new):
        raise ValueError('the register-only withdrawal changes an original TEST attachment, position, type or complete context')
    for module in (copy_evidence,injection_copy_evidence,coherent_copy_evidence,sid22_evidence):
        if module.scope_digest(before)!=module.scope_digest(after):
            raise ValueError('the register-only withdrawal changes an existing physical proof scope')
    proof.require_current(after)
    return rows


def publication_expected(before,after,before_view):
    rows=require_transition(before,after);expected=deepcopy(before_view)
    for row in rows:
        old=json.loads(row['original_claim_json'])
        key=row['owner'],old['type'],old['to'],old['slot'],old['offset']
        for section in (expected['facts']['links'],expected['origins']['links']):
            if key not in section:raise ValueError('the register-only withdrawal omits an exact original publication key')
            del section[key]
    ledgers=[]
    for kind,name,markers,source in expected['ordered']['native_ledgers']:
        owner=f'{name}/{kind}'
        for marker in markers:
            if 'dependency' in marker:
                marker['dependency']=[item for item in marker['dependency']
                    if not any(contract.selector(row,owner,item) for row in rows)]
                if not marker['dependency']:del marker['dependency']
        ledgers.append((kind,name,markers,source))
    expected['ordered']['native_ledgers']=ledgers
    return expected


def retires(before,after,claim):
    if not any(test_contract.exact(contract.plain(claim),json.loads(row['original_claim_json']))
            for row in contract.descriptor(before.root)['reference']):return False
    try:
        require_transition(before,after)
        return True
    except (OSError,ValueError,TypeError,KeyError,AttributeError,ImportError,RecursionError):
        return False
