"""Packed-width physical refusals consume the actual original common primary."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile, copy_evidence, packed_transfer_capture_evidence as proof, repo, test_evidence


@pytest.fixture(scope='module')
def original():
    try:
        record = json.loads(copy_evidence._read(repo.ROOT, copy_evidence.RECEIPT))
        packets = record['candidate']['witness']['packed_transfers']
    except (FileNotFoundError, KeyError):
        if test_evidence.REQUIRE_CONTEXTS:
            pytest.fail('the common B acceptance requires its original complete packed-transfer record')
        pytest.skip('the original packed-transfer primary record is not available')
    model = compile.build(repo.ROOT)
    accepted = proof.require_primary(model, record)
    assert set(accepted['packed_transfers']) == {'1me3b', '1nd', 'jk78c'}
    return model, record, packets


def refuse(original, packet):
    model, record, _ = original
    with pytest.raises(ValueError):
        proof.require_witness(model, '1me3b', packet, record['candidate']['producer_inputs'])


@pytest.mark.parametrize('field', ('consumed', 'reconstruction', 'aliases', 'boundaries', 'image_sha256',
    'fixture_sha256', 'elf_sha256', 'observer_object_sha256', 'simulator', 'declaration', 'observations'))
def test_actual_packed_physical_binding_cannot_be_omitted(original, field):
    packet = dict(original[2]['1me3b'])
    packet.pop(field)
    refuse(original, packet)


@pytest.mark.parametrize('fault', ('layout', 'width', 'native-claim', 'dropped-site', 'dropped-callee',
                                  'alias', 'boundary', 'source', 'failed-simulator', 'self-admission'))
def test_actual_packed_physical_binding_cannot_be_substituted(original, fault):
    packet = dict(original[2]['1me3b'])
    if fault in ('layout', 'width', 'native-claim', 'dropped-site', 'dropped-callee'):
        declared = deepcopy(packet['declaration'])
        packet['declaration'] = declared
        if fault == 'layout':
            declared['layout'] = '1nd'
        elif fault == 'width':
            declared['fields'][0]['declared_bits'] = 32
        elif fault == 'native-claim':
            declared['fields'][0]['original_claim_sha256'] = '0' * 64
        elif fault == 'dropped-site':
            declared['fields'][0]['observed'].pop()
        else:
            next(row for row in declared['windows'] if row['natural_copy_callee_required']).pop('copy_callee')
    elif fault == 'alias':
        packet['aliases'] = [{**row, 'alias': row['alias'] + 1} for row in packet['aliases']]
    elif fault == 'boundary':
        packet['boundaries'] = [{**row, 'bytes': '57f6442a000b0009'} for row in packet['boundaries']]
    elif fault == 'source':
        packet['consumed'] = {**packet['consumed'], proof.OBSERVER: '000b0009'}
    elif fault == 'failed-simulator':
        packet['simulator'] = {**packet['simulator'], 'returncode': 4}
    else:
        packet['semantic_admission'] = True
    refuse(original, packet)


@pytest.mark.parametrize('field,offset', (
    ('context', 43), ('context_after', 43), ('observation', 0), ('observation', 51),
    ('observation', 83), ('observation', 183), ('observation', 375), ('observation', 567),
    ('ram_before', 0x81B5), ('ram_after', 0x817D), ('ram_after', 0x1234),
))
def test_consistent_packed_raw_stream_cannot_replace_full_state_equations(original, field, offset):
    held = original[2]['1me3b']
    packet = dict(held)
    row = dict(held['observations'][0])
    raw = bytearray.fromhex(row[field])
    raw[offset] ^= 1
    row[field] = raw.hex()
    packet['observations'] = [row, *held['observations'][1:]]
    lines = held['stdout'].splitlines()
    first = next(index for index, line in enumerate(lines) if line.startswith(proof.PREFIX))
    lines[first] = proof.PREFIX + json.dumps(row)
    packet['stdout'] = '\n'.join(lines) + '\n'
    packet['stdout_sha256'] = hashlib.sha256(packet['stdout'].encode()).hexdigest()
    refuse(original, packet)


@pytest.mark.parametrize('fault', ('missing-layout', 'duplicate-layout', 'wrong-original', 'failed-terminal'))
def test_packed_capture_requires_the_same_complete_original_primary(original, fault):
    model, held, packets = original
    record = {**held, 'candidate': dict(held['candidate']), 'terminal': dict(held['terminal'])}
    if fault in ('missing-layout', 'duplicate-layout'):
        altered = dict(packets)
        if fault == 'missing-layout':
            altered.pop('1nd')
        else:
            altered['1nd3b'] = altered['1nd']
        record['candidate']['witness'] = {**record['candidate']['witness'], 'packed_transfers': altered}
    elif fault == 'wrong-original':
        record['process_sha256'] = '0' * 64
    else:
        record['terminal']['actual_exit_code'] = 1
    with pytest.raises(ValueError):
        proof.require_primary(model, record)
