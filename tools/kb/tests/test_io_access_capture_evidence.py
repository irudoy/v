"""Actual native banks, descriptors and complete state govern I/O admission."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile, copy_evidence, repo, test_evidence
from kb import io_access_capture_evidence as proof


@pytest.fixture(scope='module')
def original():
    try:
        record = json.loads(copy_evidence._read(repo.ROOT, copy_evidence.RECEIPT))
        packet = record['candidate']['witness']['io_access_paths']
    except (FileNotFoundError, KeyError):
        if test_evidence.REQUIRE_CONTEXTS:
            pytest.fail('the common B acceptance requires its complete original I/O-access capture')
        pytest.skip('the complete original I/O-access capture is unavailable')
    model = compile.build(repo.ROOT)
    result = proof.require_primary(model, record)
    assert result['bounded_physical_IO_access'] is True
    return model, record, packet


def refuse(original, packet):
    with pytest.raises(ValueError):
        proof.require_witness(original[0], packet, original[1]['candidate']['producer_inputs'])


def replace_observation(packet, index, field):
    row = packet['observations'][index]
    if field.startswith('ram_'):
        from kb import width_view_matrix
        data = bytearray(width_view_matrix.decode_rle(row[field]))
        data[0x1234] ^= 1
        parts, start = [], 0
        while start < len(data):
            end = start + 1
            while end < len(data) and data[end] == data[start]:
                end += 1
            parts.append(f'{end - start}:{data[start]:02x}')
            start = end
        row[field] = ','.join(parts)
    else:
        data = bytearray.fromhex(row[field])
        data[0] ^= 1
        row[field] = data.hex()
    lines = packet['stdout'].splitlines(keepends=True)
    positions = [number for number, line in enumerate(lines) if line.startswith(proof.PREFIX)]
    lines[positions[index]] = proof.PREFIX + json.dumps(row, separators=(',', ':')) + '\n'
    packet['stdout'] = ''.join(lines)
    packet['stdout_sha256'] = hashlib.sha256(packet['stdout'].encode()).hexdigest()


@pytest.mark.parametrize('field', ('declaration', 'consumed', 'reconstruction', 'aliases', 'boundaries',
                                  'observations', 'simulator', 'toolchain', 'stub_reconstruction'))
def test_missing_physical_or_terminal_input_refuses(original, field):
    packet = dict(original[2])
    packet.pop(field)
    refuse(original, packet)


@pytest.mark.parametrize('returncode,limit', ((1, 1200), (0, 0), (0, 1201)))
def test_failed_or_changed_original_terminal_refuses(original, returncode, limit):
    packet = deepcopy(original[2])
    packet['simulator'].update(returncode=returncode, timeout_seconds=limit)
    refuse(original, packet)


@pytest.mark.parametrize('field', ('context', 'context_after', 'observation', 'calibration_before',
    'calibration_after', 'native_io_before', 'native_io_after', 'ram_before', 'ram_after'))
def test_changed_complete_state_refuses_even_with_consistent_stream_hash(original, field):
    packet = deepcopy(original[2])
    replace_observation(packet, 0, field)
    refuse(original, packet)


@pytest.mark.parametrize('field', ('context', 'calibration_before', 'native_io_before', 'ram_before'))
def test_monitor_read_cannot_reset_or_substitute_the_actual_prefix_result(original, field):
    packet = deepcopy(original[2])
    index = next(index for index, case in enumerate(packet['declaration']['cases']) if case['kind'] == 'monitor-read')
    replace_observation(packet, index, field)
    refuse(original, packet)


@pytest.mark.parametrize('index', (1, 2, 3, 4))
def test_each_declared_simulator_memory_domain_is_required(original, index):
    packet = deepcopy(original[2])
    packet['simulator']['command'][index] = '--memory-region=0xffff0000,64k'
    refuse(original, packet)


def test_missing_complete_primary_component_refuses(original):
    record = deepcopy(original[1])
    record['candidate']['witness'].pop('io_access_paths')
    with pytest.raises(ValueError):
        proof.require_primary(original[0], record)
