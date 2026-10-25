"""Exact owning bounded closed-loop coordinate accesses from the complete original primary."""

import hashlib
import json

from kb import copy_evidence, test_contract
from kb import closed_loop_coordinate_access_contract as contract
from kb import closed_loop_coordinate_capture_evidence as capture_consumer
from kb import closed_loop_feedback_capture_evidence as feedback_consumer
from kb import closed_loop_coolant_capture_evidence as coolant_consumer
from kb.diagnostic_rom_contract import native_ledger
from kb.diagnostic_rom_evidence import dependency_state

COMPONENTS = {'closed_loop_coordinate_paths': capture_consumer,'closed_loop_feedback_paths':feedback_consumer,'closed_loop_coolant_paths':coolant_consumer}


def native_rows(model):
    rows = contract.descriptor(model.root)['reference']
    for row in rows:
        symbol = model.symbols.get(contract.symbol_key(row))
        if (symbol is None or symbol.meaning is None or symbol.meaning.key != row['owner']
                or not test_contract.exact(symbol.value('width'), contract.native_type(row,'width'))
                or not test_contract.exact(symbol.value('signed'), contract.native_type(row,'signed'))):
            raise ValueError('the bounded closed-loop coordinate proof changes its exact owning semantic width or signedness')
        links = [link for link in model.links if contract.original(row, link) or contract.qualified(row, link)]
        if len(links) != 1:
            raise ValueError('the bounded closed-loop coordinate proof needs one complete original or exact owning evidence append')
        ledger = json.loads(row['original_ledger_json'])
        if ledger is None:
            if any(f'{name}/{kind}' == row['owner'] for kind, name, _, _ in model.stash.get('ledger_rows', ())):
                raise ValueError('the bounded closed-loop coordinate proof introduces a native ledger')
        elif not test_contract.exact(native_ledger(model, row['owner']), ledger):
            raise ValueError('the bounded closed-loop coordinate proof changes a retained native ledger')
        if not test_contract.exact(contract.plain(symbol.evidence), json.loads(row['original_symbol_evidence_json'])):
            raise ValueError('the bounded closed-loop coordinate proof changes a retained ledger, symbol evidence or TEST position')
    return rows


def require_primary(model, record=None):
    rows = native_rows(model)
    if record is None:
        record = json.loads(copy_evidence._read(model.root, copy_evidence.RECEIPT))
    components = {key: consumer.require_primary(model, record) for key, consumer in COMPONENTS.items()}
    if (components['closed_loop_coordinate_paths']['exact_coordinate_accesses'] is not True
            or components['closed_loop_feedback_paths']['exact_feedback_arguments'] is not True
            or components['closed_loop_feedback_paths']['exact_feedback_stores'] is not True
            or components['closed_loop_feedback_paths']['exact_transition_counter_accesses'] is not True
            or components['closed_loop_coolant_paths']['exact_coolant_accesses'] is not True
            or components['closed_loop_coolant_paths']['exact_selected_coefficient'] is not True
            or components['closed_loop_coolant_paths']['exact_signed_offset'] is not True
            or {row['component'] for row in rows}!=set(components)):
        raise ValueError('the bounded closed-loop coordinate claim lacks independent complete stock scalar admission')
    for path in (contract.DESCRIPTOR, 'tools/kb/src/kb/closed_loop_coordinate_access_contract.py',
                 'tools/kb/src/kb/closed_loop_coordinate_access_evidence.py', 'tools/kb/src/kb/closed_loop_coordinate_access_resolution.py'):
        if record['candidate']['producer_inputs'].get(path) != hashlib.sha256(copy_evidence._read(model.root, path)).hexdigest():
            raise ValueError('the bounded closed-loop coordinate owning admission source differs from its original complete input snapshot')
    return dict(scope='exact-bounded-closed-loop-coordinate', components=components,
        original_process_sha256=record['process_sha256'], native_model=record['native_model'],
        original_claims={row['id']: row['original_claim_sha256'] for row in rows},
        units_admission=False, scale_admission=False, natural_scheduling_inference=False, hardware_qualification=False)


def require_current(model):
    before = dependency_state(model)
    result = require_primary(model)
    if dependency_state(model) != before:
        raise ValueError('the bounded closed-loop coordinate native, physical or original state changes during admission')
    return result


def owning_row(evidence, symbol, model, claim):
    if (model is None or symbol is None or model.symbols.get(symbol.key) is not symbol or symbol.meaning is None):
        raise ValueError('the bounded closed-loop coordinate proof needs its exact owning model and symbol')
    if claim != 'identity' and (getattr(claim, 'name', None) != 'identity' or getattr(claim, 'subject', None)
            not in (symbol.key.key, symbol.meaning.key, symbol.meaning.name)):
        raise ValueError('the bounded closed-loop coordinate proof supports its owning identity only')
    rows = [row for row in native_rows(model) if contract.symbol_key(row) == symbol.key
            and test_contract.exact(evidence, contract.item(row))]
    if len(rows) != 1:
        raise ValueError('the bounded closed-loop coordinate proof changes its exact original claim or owning attachment')
    row = rows[0]
    attached = [(link, value) for link in model.links for value in link.evidence if test_contract.exact(value, evidence)]
    if (len(attached) != 1 or attached[0][0].owner is not symbol.meaning or not contract.qualified(row, attached[0][0])
            or any(contract.registered(value) for value in symbol.evidence)):
        raise ValueError('the bounded closed-loop coordinate proof needs its unique complete qualified owning relation')
    return row


def failure(evidence, symbol=None, model=None, claim=None):
    if not contract.registered(evidence):
        return None
    try:
        owning_row(evidence, symbol, model, claim)
        require_current(model)
        return None
    except (OSError, ValueError, TypeError, KeyError, AttributeError, ImportError, IndexError, RecursionError):
        return 'missing or invalid exact owning bounded closed-loop coordinate execution context'


def accepted(model, symbol, function, claim):
    try:
        if not any(contract.registered(entry) for entry in claim['evidence']):
            return None
        row = next(row for row in native_rows(model) if symbol.key == contract.symbol_key(row)
                   and test_contract.exact(contract.plain(claim), json.loads(row['proposed_claim_json'])))
        if (function.key.layout != '7mfk' or function.key.address != row['function']
                or function.meaning.key != claim['to'] or failure(contract.item(row), symbol, model, 'identity') is not None):
            return None
        return dict(proof=contract.PREFIX + row['id'], callsite=f'7mfk:{row["sites"][0]:08x}',
                    scope='bounded-closed-loop-coordinate', support='identity')
    except (OSError, ValueError, TypeError, KeyError, AttributeError, ImportError, IndexError, StopIteration):
        return None


def link_failure(model, link):
    if not contract.looks_like_access(link):
        return None
    entries = [value for value in link.evidence if contract.registered(value)]
    if len(entries) != 1:
        return 'the bounded closed-loop coordinate relation lacks its one exact qualified owning proof'
    return failure(entries[0], link.owner.symbols.get('7mfk'), model, 'identity')


def identity_only(symbol):
    return symbol is not None and symbol.meaning is not None and any(
        link.owner is symbol.meaning and contract.looks_like_access(link) for link in symbol.meaning.links)
