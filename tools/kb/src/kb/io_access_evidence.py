"""Owning I/O software proof from one complete original primary."""

import hashlib
import json

from kb import copy_evidence, test_contract
from kb import io_access_capture_evidence as raw
from kb import io_access_claim_contract as contract
from kb.diagnostic_rom_contract import native_ledger
from kb.diagnostic_rom_evidence import dependency_state


def native_rows(model):
    rows = contract.descriptor(model.root)['reference']
    for row in rows:
        symbol = model.symbols.get(contract.symbol_key(row))
        if symbol is None or symbol.meaning is None or symbol.meaning.key != row['owner']:
            raise ValueError('the I/O proof changes its exact current register owner')
        original = [link for link in model.links if contract.original(row, link)]
        qualified = [link for link in model.links if contract.qualified(row, link)]
        before = json.loads(row['original_symbol_evidence_json'])
        after = json.loads(row['proposed_symbol_evidence_json'])
        if row['disposition'] == 'relocate-site-evidence':
            if not ((len(original) == 1 and not qualified and test_contract.exact(contract.plain(symbol.evidence), before))
                    or (not original and not qualified and test_contract.exact(contract.plain(symbol.evidence), after))):
                raise ValueError('the captured-word attribution needs its exact old reader or exact owning site evidence')
        elif (len(original) + len(qualified) != 1
              or not test_contract.exact(contract.plain(symbol.evidence), before)):
            raise ValueError('an I/O proof needs its complete original or exact qualified link and original symbol evidence')
        expected = json.loads(row['original_ledger_json'])
        if expected is None:
            ledgers = [value for kind, name, value, source in model.stash.get('ledger_rows', ())
                       if f'{name}/{kind}' == row['owner']]
            if ledgers:
                raise ValueError('the captured-word attribution introduces a ledger')
        elif not test_contract.exact(native_ledger(model, row['owner']), expected):
            raise ValueError('the I/O proof changes a retained ledger or diagnostic-binding position')
    return rows


def require_primary(model, record=None):
    rows = native_rows(model)
    if record is None:
        record = json.loads(copy_evidence._read(model.root, copy_evidence.RECEIPT))
    result = raw.require_primary(model, record)
    if result['bounded_physical_IO_access'] is not True or result['peripheral_side_effects_admission'] is not False:
        raise ValueError('the I/O claim lacks its exact bounded flat-storage execution')
    for path in (contract.DESCRIPTOR, 'tools/kb/src/kb/io_access_claim_contract.py',
                 'tools/kb/src/kb/io_access_evidence.py', 'tools/kb/src/kb/io_access_resolution.py'):
        if record['candidate']['producer_inputs'].get(path) != hashlib.sha256(
                copy_evidence._read(model.root, path)).hexdigest():
            raise ValueError('the I/O claim differs from its actual original native-admission source snapshot')
    return dict(scope='exact-bounded-software-IO', component=result,
        original_process_sha256=record['process_sha256'], native_model=record['native_model'],
        original_claims={row['id']: row['original_claim_sha256'] for row in rows},
        universal_no_read_claim=False, native_function_publication=False, physical_units_inference=False,
        scale_admission=False, natural_scheduling_inference=False,
        peripheral_side_effects_admission=False, hardware_qualification=False)


def require_current(model):
    before = dependency_state(model)
    result = require_primary(model)
    if dependency_state(model) != before:
        raise ValueError('the I/O native/physical/original state changes during admission')
    return result


def owning_row(evidence, symbol, model, claim='identity'):
    if (model is None or symbol is None or model.symbols.get(symbol.key) is not symbol
            or symbol.meaning is None):
        raise ValueError('the I/O proof requires its actual current owning model and symbol')
    if claim != 'identity' and (getattr(claim, 'name', None) != 'identity'
            or getattr(claim, 'subject', None) not in (symbol.key.key, symbol.meaning.key, symbol.meaning.name)):
        raise ValueError('the I/O software proof supports its owning identity only')
    rows = [row for row in native_rows(model) if symbol.key == contract.symbol_key(row)
            and symbol.meaning.key == row['owner'] and test_contract.exact(evidence, contract.item(row))]
    if len(rows) != 1:
        raise ValueError('the I/O proof changes its complete owning scope or exact original claim')
    row = rows[0]
    attached = [(link, item) for link in model.links if link.owner is symbol.meaning
                for item in link.evidence if contract.registered(item)]
    own = [item for item in symbol.evidence if contract.registered(item)]
    if row['disposition'] == 'relocate-site-evidence':
        if attached or len(own) != 1 or not test_contract.exact(own[0], evidence):
            raise ValueError('the captured word needs its unique owning symbol-evidence append')
    elif (own or len(attached) != 1 or not contract.qualified(row, attached[0][0])
          or not test_contract.exact(attached[0][1], evidence)):
        raise ValueError('the I/O transfer needs its unique complete qualified owning relation')
    return row


def failure(evidence, symbol=None, model=None, claim=None):
    if not contract.registered(evidence):
        return None
    try:
        owning_row(evidence, symbol, model, claim)
        require_current(model)
        return None
    except (OSError, ValueError, TypeError, KeyError, AttributeError, ImportError, IndexError, RecursionError):
        return 'missing or invalid exact owning I/O software execution context'


def accepted(model, symbol, function, claim):
    try:
        row = next(row for row in native_rows(model) if row['disposition'] == 'append-link-proof'
                   and symbol.key == contract.symbol_key(row))
        if not test_contract.exact(contract.plain(claim), json.loads(row['proposed_claim_json'])):
            return None
        if (claim['to'] != function.meaning.key or failure(contract.item(row), symbol, model, 'identity') is not None):
            return None
        return dict(proof=PREFIX + row['id'], callsite=f'7mfk:{row["site"]:08x}',
                    scope='bounded-software-IO', support='identity')
    except (OSError, ValueError, TypeError, KeyError, AttributeError, ImportError, IndexError, StopIteration):
        return None


def link_failure(model, link):
    if not contract.looks_like_access(link):
        return None
    entries = [item for item in link.evidence if contract.registered(item)]
    if len(entries) != 1:
        return 'the I/O relation lacks its one exact qualified owning proof'
    return failure(entries[0], link.owner.symbols.get('7mfk'), model, 'identity')


def identity_only(symbol):
    return (symbol is not None and symbol.layout == '7mfk' and symbol.meaning is not None
            and (any(contract.registered(item) for item in symbol.evidence)
                 or any(link.owner is symbol.meaning and contract.looks_like_access(link)
                        for link in symbol.meaning.links)))


PREFIX = contract.PREFIX
