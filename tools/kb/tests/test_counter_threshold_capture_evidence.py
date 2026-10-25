"""Exact original capture and native ownership govern the AAFA factor scale."""

import copy
import hashlib
import json

import pytest

from kb import compile, copy_evidence, repo, test_evidence
from kb import counter_threshold_capture_evidence as proof
from kb import counter_threshold_factor_contract as factor
from kb import counter_threshold_factor_evidence as joint
from kb.model import SymbolKey


@pytest.fixture(scope='module')
def original():
    try:
        record = json.loads(copy_evidence._read(repo.ROOT, copy_evidence.RECEIPT))
        packet = record['candidate']['witness']['counter_threshold_paths']
    except (FileNotFoundError, KeyError):
        if test_evidence.REQUIRE_CONTEXTS:
            pytest.fail('the common B acceptance requires its complete original counter-threshold capture')
        pytest.skip('the complete original counter-threshold capture is unavailable')
    model = compile.build(repo.ROOT)
    result = proof.require_primary(model, record)
    assert result['bounded_ratio_factor_lineage'] is True and result['scale_admission'] is False
    admitted = joint.require_primary(model, record)
    assert admitted['owned_factor_scale_admission'] is True
    assert admitted['owned_fields'] == factor.FIELDS
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
    row = packet['observations'][0]
    raw = bytearray.fromhex(row[field])
    raw[0] ^= 1
    row[field] = raw.hex()
    lines = packet['stdout'].splitlines(keepends=True)
    position = next(index for index, line in enumerate(lines) if line.startswith(proof.PREFIX))
    lines[position] = proof.PREFIX + json.dumps(row, separators=(',', ':')) + '\n'
    packet['stdout'] = ''.join(lines)
    packet['stdout_sha256'] = hashlib.sha256(packet['stdout'].encode()).hexdigest()
    refuse(original, packet)


def test_missing_raw_component_cannot_preserve_owned_factor_scale(original):
    record = copy.deepcopy(original[1])
    record['candidate']['witness'].pop('counter_threshold_paths')
    with pytest.raises((ValueError, KeyError)):
        joint.require_primary(original[0], record)


@pytest.mark.parametrize('claim', ('identity', 'structure', 'contract'))
def test_factor_cannot_supply_other_claims_or_another_owner(original, claim):
    model = original[0]
    row = factor.descriptor(repo.ROOT)['reference'][0]
    with pytest.raises(ValueError):
        joint.owning_row(factor.item(row), model.symbols[factor.SYMBOL], model, claim)
    with pytest.raises(ValueError):
        joint.owning_row(factor.item(row), model.symbols[SymbolKey('7mfk', 'fn', 0x21BBC)], model, 'scale')
