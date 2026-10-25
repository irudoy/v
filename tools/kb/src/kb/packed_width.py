"""Exact width-question resolution by a qualified packed-transfer contract.

A resolution accepts only the declared byte/container compatibility. It does
not change semantic width, ground symbol identity, or qualify another access.
The original unresolved question remains reproducible without its live proof.
"""

import json

from kb import copy_evidence, ignition_literal_evidence, packed_transfer_capture_evidence
from kb import packed_transfer_evidence as contract, test_contract


def require(model, symbol, claim, *, record=None):
    if model is None or symbol is None or model.symbols.get(symbol.key) is not symbol:
        raise ValueError('the packed width contract requires its actual complete native symbol')
    declared = contract.descriptor(model.root)
    fields = [row for row in declared['field'] if row['symbol'] == symbol.key.key]
    if len(fields) != 1:
        raise ValueError('the packed width contract does not register this exact field')
    field = fields[0]
    if record is None:
        record = json.loads(copy_evidence._read(model.root, copy_evidence.RECEIPT))
    packets = record['candidate']['witness'].get('packed_transfers')
    if type(packets) is not dict or set(packets) != set(contract.LAYOUTS):
        raise ValueError('the packed width contract lacks its exact complete original layout set')
    contract.bind_field(model, field)
    observed = sorted((row['function'], row['site'], row['mode'], row['width_bytes'])
                      for row in field['observed'])
    expected = dict(symbol=symbol.key.key, width=field['declared_bits'], observed=observed)
    if not test_contract.exact(claim, expected):
        raise ValueError('the packed width contract receives another retained wider-access question')
    original, current = ignition_literal_evidence.require_original(model, record)
    layout = field['layout']
    packet = packets[layout]
    physical = packed_transfer_capture_evidence.require_witness(
        model, layout, packet, record['candidate']['producer_inputs'])
    if original.count(packet['marker']) != 1:
        raise ValueError('the packed width contract lacks its exact original region success marker')
    support = physical['fields'].get(symbol.key.key)
    if not support or any(row['declared_field_bits'] != field['declared_bits']
                          or row['semantic_width_inference'] is not False
                          or row['publication_width_inference'] is not False for row in support):
        raise ValueError('the packed width result changes its bounded byte/container compatibility')
    if ignition_literal_evidence.execution_inputs(model.root) != current:
        raise ValueError('the packed width execution inputs change during resolution')
    return dict(symbol=symbol.key.key, original_claim_sha256=field['original_claim_sha256'],
        source_l0=field['original_l0'], descriptor=contract.DESCRIPTOR,
        descriptor_sha256=packet['declaration']['descriptor_sha256'],
        original_process_sha256=record['process_sha256'], region=physical['region'],
        fixture_sha256=physical['fixture_sha256'], elf_sha256=physical['elf_sha256'],
        observations=len(support), scope='exact-wide-transfer-byte-field-compatibility',
        declared_bits=field['declared_bits'], semantic_width_inference=False,
        publication_width_inference=False, identity_grounding=False,
        access_grounding=False, hardware_qualification=False)


def accepted(model, symbol, claim):
    """A missing, stale, failing or unrelated proof accepts no width question."""
    try:
        return require(model, symbol, claim)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, ImportError, IndexError, RecursionError):
        return None
