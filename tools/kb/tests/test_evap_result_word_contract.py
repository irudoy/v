"""Exact bounded pointer, complete source identities and raw input refusal controls."""
from copy import deepcopy
import re
import pytest
from kb import repo
from kb import evap_result_word_contract as contract, evap_result_word_matrix as matrix


def case(**updates):
    result = dict(deepcopy(matrix.DEFAULTS), index=0, kind='source-refusal-control')
    result.update(updates)
    return result


def test_published_counts_bind_the_executed_descriptor_and_actual_pointer_premise():
    source = contract.descriptor(repo.ROOT)
    actual = (sum((r['end'] - r['start']) // 2 for r in source['unit']['code']), len(contract.FUNCTIONS),
        len(source['unit']['code']), len(source['unit']['pools']), len(source['unit']['aliases']), len(source['controlled_calibration']))
    text = (repo.ROOT / 'defs/JK08A.evap-result-word.md').read_text()
    match = re.search(r'binds (\d+) stock instructions in (\d+) actual entry paths and (\d+) spans,\s*'
        r'(\d+) literal pools, (\d+) four-byte RAM pointer aliases and (\d+) calibration spans', text)
    assert match is not None and tuple(map(int, match.groups())) == actual == (672, 11, 13, 44, 6, 55)
    premise = source['exact_entry_premise']
    assert (premise['pointer_register'], premise['native_address'], premise['simulator_address']) == (6, 0xFFFF301C, 0x0100301C)
    assert (premise['natural_caller'], premise['call_site'], premise['delay_site']) == (0xB29B8, 0xB2C88, 0xB2C8A)
    assert premise['whole_natural_caller_body_execution'] is False
    assert source['native_identity_admission'] is source['scale_admission'] is source['hardware_qualification'] is False


@pytest.mark.parametrize('fault', ('pointer', 'native-pointer', 'bool-word', 'short-array', 'bad-SR', 'computed-input'))
def test_raw_input_refuses_pointer_substitution_lost_width_or_supplied_result(fault):
    value = case()
    if fault == 'pointer':
        value['context'][6] ^= 2
    elif fault == 'native-pointer':
        value['context'][6] = 0xFFFF301C
    elif fault == 'bool-word':
        value['word_272a'] = True
    elif fault == 'short-array':
        value['coefficient_b_cluster'].pop()
    elif fault == 'bad-SR':
        value['context'][18] = 2
    else:
        value['computed_301c'] = 65535
    with pytest.raises(ValueError):
        matrix.require_case(value)


def test_fixture_preserves_all_instruction_bytes_and_only_relocates_declared_pool_pointers():
    image = repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    source = contract.descriptor(repo.ROOT)
    fixture, aliases = contract.independent_fixture(source, image)
    changed = {at for at, (a, b) in enumerate(zip(image, fixture)) if a != b}
    allowed = {at for row in aliases for at in range(row['address'], row['address'] + 4)}
    assert changed <= allowed
    for row in source['unit']['code']:
        assert fixture[row['start']:row['end']] == image[row['start']:row['end']]
    raw = matrix.header(dict(source=source, cases=[case()]), image).decode()
    assert 'calibration_index' in raw and 'evap_calibration_inputs' in raw
    assert all(word not in '\n'.join(raw.splitlines()[1:]) for word in ('expected', 'computed_301c', 'quotient'))
