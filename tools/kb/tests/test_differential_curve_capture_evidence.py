"""Original raw state, physical inputs and bounded terminals govern admission."""

import copy
import hashlib
import json

import pytest

from kb import compile, copy_evidence, repo, test_evidence
from kb import differential_curve_capture_evidence as proof


@pytest.fixture(scope='module')
def original():
    try:
        record = json.loads(copy_evidence._read(repo.ROOT, copy_evidence.RECEIPT))
        packet = record['candidate']['witness']['differential_curve_paths']
    except (FileNotFoundError, KeyError):
        if test_evidence.REQUIRE_CONTEXTS:
            pytest.fail('the common B acceptance requires its complete original differential-curve capture')
        pytest.skip('the complete original differential-curve capture is unavailable')
    model = compile.build(repo.ROOT)
    result = proof.require_primary(model, record)
    assert result['bounded_argument_lineage'] is True
    return model, record, packet


def refuse(original, packet):
    with pytest.raises(ValueError):
        proof.require_witness(original[0], packet, original[1]['candidate']['producer_inputs'])


@pytest.mark.parametrize('field', ('declaration', 'consumed', 'reconstruction', 'aliases',
                                  'boundaries', 'observations', 'simulator', 'toolchain', 'stub_reconstruction'))
def test_missing_physical_or_terminal_input_refuses(original, field):
    packet = dict(original[2])
    packet.pop(field)
    refuse(original, packet)


@pytest.mark.parametrize('returncode,limit', ((1, 1200), (0, 0), (0, 1201)))
def test_failed_or_changed_original_terminal_refuses(original, returncode, limit):
    packet = copy.deepcopy(original[2])
    packet['simulator'].update(returncode=returncode, timeout_seconds=limit)
    refuse(original, packet)


@pytest.mark.parametrize('field', ('context', 'observation', 'calibration_before', 'calibration_after'))
def test_changed_actual_state_refuses_even_with_consistent_stream_hash(original, field):
    packet = copy.deepcopy(original[2])
    actual = packet['observations']
    row = actual[0]
    raw = bytearray.fromhex(row[field])
    raw[0] ^= 1
    row[field] = raw.hex()
    lines = packet['stdout'].splitlines(keepends=True)
    position = next(index for index, line in enumerate(lines) if line.startswith(proof.PREFIX))
    lines[position] = proof.PREFIX + json.dumps(row, separators=(',', ':')) + '\n'
    packet['stdout'] = ''.join(lines)
    packet['stdout_sha256'] = hashlib.sha256(packet['stdout'].encode()).hexdigest()
    refuse(original, packet)


def test_missing_common_original_component_refuses(original):
    record = copy.deepcopy(original[1])
    record['candidate']['witness'].pop('differential_curve_paths')
    with pytest.raises(ValueError):
        proof.require_primary(original[0], record)
