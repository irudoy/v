"""Owning calculation admission requires the exact complete shared original."""

from importlib import import_module
import hashlib
import json

from kb import copy_evidence, ignition_literal_evidence, test_contract
from kb import calculation_dependency_contract as contract
from kb.diagnostic_rom_evidence import dependency_state


def native_rows(model):
    rows = contract.rows(model.root)
    for row in rows:
        symbol = model.symbols.get(contract.symbol_key(row))
        target = model.symbols.get(contract.target(row))
        expected_target = json.loads(row['proposed_claim_json'])['to']
        if (symbol is None or symbol.meaning is None or symbol.meaning.key != row['owner']
                or target is None or target.meaning is None or target.meaning.key != expected_target):
            raise ValueError('a calculation disposition changes its exact owning symbol or target')
        old_target = json.loads(row['original_claim_json'])['to']
        links = [link for link in model.links if link.owner is symbol.meaning and
                 (link.type == 'reader' and link.to.key == old_target
                  or link.type == 'depends' and link.to.key == expected_target
                  or any(contract.registered(value) for value in link.evidence))]
        if len(links) != 1 or not (contract.original(row, links[0]) or contract.dependency(row, links[0])):
            raise ValueError('a calculation needs its one complete original or qualified replacement claim')
        ledger = 'original_ledger_json' if contract.original(row, links[0]) else 'proposed_ledger_json'
        if not test_contract.exact(contract.native_ledger(model, row['owner']), json.loads(row[ledger])):
            raise ValueError('a calculation changes an original ledger field, selector or evidence position')
        if row['family'] == 'counter-threshold':
            from kb import counter_threshold_factor_evidence
            counter_threshold_factor_evidence.native_row(model)
        if row['family']=='closed-loop-feedback':
            width=None if row['declared_width']=='unset' else row['declared_width']
            signed=None if row['declared_signed']=='unset' else row['declared_signed']
            if not test_contract.exact((symbol.value('width'),symbol.value('signed')),(width,signed)):
                raise ValueError('a feedback argument changes its retained native semantic type')
        if row['family'] == 'closed-loop-sample' and (symbol.value('width') is not None
                or symbol.value('signed') is not None):
            raise ValueError('the coordinate sample argument changes an unset native semantic type')
        if row['family']=='cvtc-gain' and (symbol.value('width') is not None or symbol.value('signed') is not None
                or not test_contract.exact(contract.plain(symbol.evidence),json.loads(row['original_symbol_evidence_json']))):
            raise ValueError('the CVTC result changes an unset native type or original L0/TEST position')
    return rows


def require_primary(model, record=None, *, family=None):
    rows = native_rows(model)
    selected = rows if family is None else [row for row in rows if row['family'] == family]
    if not selected:
        raise ValueError('the calculation proof names no exact registered family')
    if record is None:
        record = json.loads(copy_evidence._read(model.root, copy_evidence.RECEIPT))
    original, current = ignition_literal_evidence.require_original(model, record)
    results, owned_scales = {}, {}
    for row in selected:
        key = row['component']
        if key not in results:
            if row['family'] == 'counter-threshold':
                from kb import counter_threshold_factor_evidence
                admitted = counter_threshold_factor_evidence.require_primary(model, record)
                owned_scales[row['owner']] = admitted
                result = admitted['component']
            else:
                consumer = import_module('kb.' + row['consumer'])
                packet = record['candidate']['witness'][key]
                result = consumer.require_witness(model, packet, record['candidate']['producer_inputs'])
            packet = record['candidate']['witness'][key]
            if original.count(packet['marker']) != 1 or result['image_sha256'] != contract.IMAGE_SHA256:
                raise ValueError('the calculation combines another image or incomplete original component')
            if row['family']=='closed-loop-feedback' and result.get('exact_feedback_arguments') is not True:
                raise ValueError('the feedback arguments lack their independent actual post-delay and fixed-other proof')
            if row['family'] == 'closed-loop-sample' and result.get('exact_sample_argument') is not True:
                raise ValueError('the coordinate sample argument lacks its independent fixed-other output proof')
            if row['family']=='cvtc-gain' and result.get('exact_cvtc_gain_output') is not True:
                raise ValueError('the CVTC result lacks its distinct real returned-byte/store and fixed-other output proof')
            results[key] = result
        if record['candidate']['producer_inputs'].get(row['descriptor']) != hashlib.sha256(
                copy_evidence._read(model.root, row['descriptor'])).hexdigest():
            raise ValueError('a calculation disposition differs from the complete original input snapshot')
    for path in ('tools/kb/src/kb/calculation_dependency_contract.py',
                 'tools/kb/src/kb/calculation_dependency_evidence.py',
                 'tools/kb/src/kb/calculation_dependency_resolution.py'):
        if record['candidate']['producer_inputs'].get(path) != hashlib.sha256(
                copy_evidence._read(model.root, path)).hexdigest():
            raise ValueError('the calculation native admission differs from its original executable inputs')
    if ignition_literal_evidence.execution_inputs(model.root) != current:
        raise ValueError('the calculation inputs change during independent original consumption')
    return dict(scope='exact-conditional-calculation', components=results, owned_scales=owned_scales,
        original_process_sha256=record['process_sha256'], native_model=record['native_model'],
        original_claims={row['operation_id']: row['original_claim_sha256'] for row in selected},
        physical_reader_inference=False, general_scale_admission=False,
        natural_scheduling_inference=False, hardware_qualification=False)


def owning_row(evidence, symbol, model, claim='identity'):
    if (model is None or symbol is None or model.symbols.get(symbol.key) is not symbol
            or symbol.meaning is None):
        raise ValueError('the calculation proof needs its exact current owning model and symbol')
    rows = [row for row in native_rows(model) if contract.symbol_key(row) == symbol.key
            and row['owner'] == symbol.meaning.key and test_contract.exact(evidence, contract.item(row))]
    if len(rows) != 1:
        raise ValueError('the calculation proof changes its complete family, original identity or owning item')
    row = rows[0]
    name = 'scale' if row['family'] == 'counter-threshold' else 'identity'
    if claim != name and (getattr(claim, 'name', None) != name or getattr(claim, 'subject', None)
            not in (symbol.key.key, symbol.meaning.key, symbol.meaning.name)):
        raise ValueError('the calculation proof cannot supply another owning claim or donate a level')
    attached = [(link, value) for link in model.links if link.owner is symbol.meaning
                for value in link.evidence if contract.registered(value)]
    if (len(attached) != 1 or not contract.dependency(row, attached[0][0])
            or not test_contract.exact(attached[0][1], evidence)
            or any(contract.registered(value) for value in symbol.evidence)):
        raise ValueError('the calculation proof lacks its unique complete qualified owning dependency')
    return row


def require_current(model, *, family=None):
    before = dependency_state(model)
    result = require_primary(model, family=family)
    if dependency_state(model) != before:
        raise ValueError('the calculation native/physical/original state changes during admission')
    return result


def failure(evidence, symbol=None, model=None, claim=None):
    if not contract.registered(evidence):
        return None
    try:
        row = owning_row(evidence, symbol, model, claim)
        require_current(model, family=row['family'])
        return None
    except (OSError, ValueError, TypeError, KeyError, AttributeError, ImportError, IndexError, RecursionError):
        return 'missing or invalid exact owning calculation execution context'


def link_failure(model, link):
    if not contract.looks_like_dependency(link):
        return None
    entries = [value for value in link.evidence if contract.registered(value)]
    if len(entries) != 1:
        return 'the calculation dependency lacks its one exact qualified owning proof'
    return failure(entries[0], link.owner.symbols.get('7mfk'), model, entries[0].get('supports'))


def identity_only(symbol):
    return symbol is not None and symbol.layout == '7mfk' and symbol.meaning is not None and any(
        link.owner is symbol.meaning and contract.looks_like_dependency(link)
        and link.owner.key != 'natural-hedgehog/tbl' for link in symbol.meaning.links)
