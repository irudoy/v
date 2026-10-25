"""Joint execution admission of only AAFA's owned dimensionless ratio factor."""

import hashlib
import json

from kb import copy_evidence, ignition_literal_evidence, test_contract
from kb import counter_threshold_capture_evidence as caller
from kb import counter_threshold_factor_contract as contract


def native_row(model):
    row = contract.descriptor(model.root)['reference'][0]
    symbol = model.symbols.get(contract.SYMBOL)
    target = model.symbols.get(contract.FUNCTION)
    if (symbol is None or symbol.meaning is None or symbol.meaning.key != contract.OWNER
            or target is None or target.meaning is None or target.meaning.key != contract.TARGET
            or not test_contract.exact({key: symbol.value(key) for key in contract.FIELDS}, contract.FIELDS)):
        raise ValueError('the factor requires its exact existing owning unit and code scale')
    links = [link for link in model.links if link.owner is symbol.meaning and
             (link.type == 'reader' and link.to.key == contract.TARGET or contract.looks_like_dependency(link))]
    if len(links) != 1 or not (contract.original(row, links[0]) or contract.dependency(row, links[0])):
        raise ValueError('the factor requires its one complete original or replacement owning claim')
    ledger = 'original_ledger_json' if contract.original(row, links[0]) else 'proposed_ledger_json'
    if not test_contract.exact(contract.native_ledger(model, contract.OWNER), json.loads(row[ledger])):
        raise ValueError('the factor changes an unrelated native ledger field or evidence position')
    return row


def require_primary(model, record=None):
    row = native_row(model)
    if record is None:
        record = json.loads(copy_evidence._read(model.root, copy_evidence.RECEIPT))
    original, current = ignition_literal_evidence.require_original(model, record)
    packet = record['candidate']['witness']['counter_threshold_paths']
    result = caller.require_witness(model, packet, record['candidate']['producer_inputs'])
    if (original.count(packet['marker']) != 1 or result['bounded_ratio_factor_lineage'] is not True
            or result['scale_admission'] is not False):
        raise ValueError('the factor lacks its actual original lower-knot selection and product/10 execution')
    for path in (contract.DESCRIPTOR, 'tools/kb/src/kb/counter_threshold_factor_contract.py',
                 'tools/kb/src/kb/counter_threshold_factor_evidence.py'):
        if record['candidate']['producer_inputs'].get(path) != hashlib.sha256(
                copy_evidence._read(model.root, path)).hexdigest():
            raise ValueError('the owning factor differs from its actual original source snapshot')
    if ignition_literal_evidence.execution_inputs(model.root) != current:
        raise ValueError('the owning factor source closure changes during independent admission')
    return dict(proof=contract.KEY, owner=contract.OWNER, symbol='7mfk:0000aafa',
        component=result, original_process_sha256=record['process_sha256'], native_model=record['native_model'],
        original_claim_sha256=row['original_claim_sha256'], owned_fields=dict(contract.FIELDS),
        owned_factor_scale_admission=True, physical_reader_inference=False,
        physical_time_units_inference=False, natural_scheduling_inference=False, hardware_qualification=False)


def owning_row(evidence, symbol, model, claim='scale'):
    if (model is None or symbol is None or model.symbols.get(symbol.key) is not symbol
            or symbol.key != contract.SYMBOL or symbol.meaning is None or symbol.meaning.key != contract.OWNER):
        raise ValueError('the factor supplies its exact owning AAFA scale only')
    if claim != 'scale' and (getattr(claim, 'name', None) != 'scale'
            or getattr(claim, 'subject', None) not in (symbol.key.key, symbol.meaning.key, symbol.meaning.name)):
        raise ValueError('the factor cannot supply another claim or donate its scale')
    row = native_row(model)
    if not test_contract.exact(evidence, contract.item(row)):
        raise ValueError('the factor changes its complete owning scale evidence')
    attached = [(link, value) for link in model.links if link.owner is symbol.meaning
                for value in link.evidence if contract.registered(value)]
    if (len(attached) != 1 or not contract.dependency(row, attached[0][0])
            or not test_contract.exact(attached[0][1], evidence)
            or any(contract.registered(value) for value in symbol.evidence)):
        raise ValueError('the factor has no unique complete owning dependency')
    return row
