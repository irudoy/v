"""Absence of physical datum access authorizes only exact registered withdrawals."""

import hashlib
import json
from pathlib import Path

from kb import copy_evidence,store,test_contract
from kb import register_only_withdrawal_contract as contract
from kb import register_only_helpers_capture_evidence as capture_consumer
from kb.diagnostic_rom_contract import native_ledger
from kb.diagnostic_rom_evidence import dependency_state

COMPONENTS={'register_only_helper_paths':capture_consumer}


def native_rows(model,phase=None):
    rows=contract.descriptor(model.root)['reference'];phases=set();seen=set()
    for row in rows:
        symbol=model.symbols.get(contract.symbol_key(row))
        if (symbol is None or symbol.meaning is None or symbol.meaning.key!=row['owner']
                or not test_contract.exact((symbol.value('width'),symbol.value('signed')),
                    (contract.native_type(row,'width'),contract.native_type(row,'signed')))
                or not test_contract.exact(contract.plain(symbol.evidence),json.loads(row['original_symbol_evidence_json']))):
            raise ValueError('the register-only withdrawal changes a retained exact symbol, type or original evidence position')
        if row['owner'] in seen:continue
        seen.add(row['owner'])
        # Use the normal owned-document loader, including the normal writer overlay.
        document=store.load(model.root,Path(row['source']),model.overlay)
        matches=[name for name in ('original','proposed')
            if test_contract.exact(document,json.loads(row[name+'_native_json']))]
        if len(matches)!=1:raise ValueError('the register-only withdrawal changes its complete native preimage or postimage')
        current=matches[0];phases.add(current)
        if not test_contract.exact(native_ledger(model,row['owner']),json.loads(row[
                'original_ledger_json' if current=='original' else 'proposed_ledger_json'])):
            raise ValueError('the register-only withdrawal changes a retained native ledger identity or selector position')
    if len(seen)!=11 or len(phases)!=1 or phase is not None and phases!={phase}:
        raise ValueError('the register-only withdrawal requires one complete exact twelve-claim phase')
    current=next(iter(phases))
    for row in rows:
        old=json.loads(row['original_claim_json'])
        related=[link for link in model.links if (link.owner.key,link.type,link.to.key,link.slot,link.offset)
            ==(row['owner'],old['type'],old['to'],old['slot'],old['offset'])]
        if (current=='original' and (len(related)!=1 or not contract.original(row,related[0]))
                or current=='proposed' and related):
            raise ValueError('the register-only withdrawal changes an exact before-present/after-absent relation')
    return rows


def require_primary(model,record=None):
    rows=native_rows(model)
    if record is None:record=json.loads(copy_evidence._read(model.root,copy_evidence.RECEIPT))
    components={key:consumer.require_primary(model,record) for key,consumer in COMPONENTS.items()}
    result=components['register_only_helper_paths']
    if (result.get('exact_register_only_paths') is not True or result.get('no_datum_access') is not True
            or result.get('native_identity_admission') is not False
            or {row['component'] for row in rows}!=set(components)):
        raise ValueError('the register-only withdrawal lacks complete independent natural-path and no-datum-access admission')
    for path in (contract.DESCRIPTOR,'tools/kb/src/kb/register_only_withdrawal_contract.py',
            'tools/kb/src/kb/register_only_withdrawal_evidence.py','tools/kb/src/kb/register_only_withdrawal_resolution.py'):
        if record['candidate']['producer_inputs'].get(path)!=hashlib.sha256(copy_evidence._read(model.root,path)).hexdigest():
            raise ValueError('the register-only withdrawal source differs from its complete original input snapshot')
    return dict(scope='exact-register-only-withdrawal',components=components,
        original_process_sha256=record['process_sha256'],native_model=record['native_model'],
        original_claims={row['id']:row['original_claim_sha256'] for row in rows},
        replacement_relation=False,native_identity_admission=False,scale_admission=False,
        units_admission=False,natural_caller_reachability=False,hardware_qualification=False)


def require_current(model):
    before=dependency_state(model);result=require_primary(model)
    if dependency_state(model)!=before:raise ValueError('the register-only withdrawal input or original changes during admission')
    return result


def failure(evidence,symbol=None,model=None,claim=None):
    return 'a register-only withdrawal grants no owning evidence or supported fact' if contract.registered(evidence) else None


def accepted(model,symbol,function,claim):return None


def link_failure(model,link):
    return 'the exact register-only physical reader is unsupported and requires its complete withdrawal' if contract.looks_like_access(link) else None


def identity_only(symbol):return False
