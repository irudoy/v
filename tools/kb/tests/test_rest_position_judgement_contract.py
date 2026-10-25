"""Exact complete bank1 root, source counts and immutable raw-input refusals."""
from copy import deepcopy
import hashlib
import re
import pytest
from kb import repo
from kb import rest_position_judgement_contract as contract, rest_position_judgement_matrix as matrix


def case():
    return dict(deepcopy(matrix.DEFAULTS), index=0, kind='controlled-source-contract')


def test_published_counts_and_native_index_premise_read_the_executed_descriptor():
    source = contract.descriptor(repo.ROOT)
    assert source['entries'] == [0x90256] and contract.FUNCTIONS == (0x90256,)
    actual = (sum((r['end'] - r['start']) // 2 for r in source['unit']['code']),
        len(contract.FUNCTIONS), len(source['unit']['code']), len(source['unit']['pools']),
        len(source['unit']['aliases']), len(source['controlled_calibration']))
    text = (repo.ROOT / 'defs/JK08A.rest-position-judgement.md').read_text()
    match = re.search(r'binds (\d+) stock instructions in (\d+) actual entry paths? and (\d+) spans,\s*'
        r'(\d+) literal pools, (\d+) four-byte RAM pointer aliases and (\d+) calibration spans', text)
    assert match is not None and tuple(map(int, match.groups())) == actual == (273, 1, 3, 26, 7, 34)
    assert source['entry_premises']['register4'] == 1
    assert source['entry_premises']['other19_context_fields_independent'] is True
    assert source['selected_actual_byte'] == dict(address=0xFFFF16BB, width_bytes=1,
        read_sites=[0x9030C, 0x903AA], source_base=0xFFFF16BA, actual_index=1)
    assert (source['context_bytes'], source['frame_bytes'], source['frame_prefix']) == (80, 192, 160)


def test_fixture_preserves_all_instructions_and_only_relocates_exact_full_pointer_words():
    source = contract.descriptor(repo.ROOT)
    image = repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    fixture, aliases = contract.independent_fixture(source, image)
    assert {i for i, (a, b) in enumerate(zip(image, fixture)) if a != b} <= {
        at for r in aliases for at in range(r['address'], r['address'] + 4)}
    for r in source['unit']['code']:
        assert fixture[r['start']:r['end']] == image[r['start']:r['end']]
    wrong = bytearray(image)
    wrong[0x90256] ^= 1
    with pytest.raises(ValueError):
        contract.independent_fixture(source, bytes(wrong))


@pytest.mark.parametrize('fault', ('bool-byte', 'wide-byte', 'short-context', 'other-bank', 'wide-bank', 'bool-bank', 'bad-SR', 'supplied-output'))
def test_input_refuses_changed_full_bank_word_or_partial_raw_state(fault):
    value = case()
    if fault == 'bool-byte':
        value['byte_16bb'] = True
    elif fault == 'wide-byte':
        value['rom_855d'] = 256
    elif fault == 'short-context':
        value['context'].pop()
    elif fault in ('other-bank', 'wide-bank', 'bool-bank'):
        value['context'][4] = {'other-bank': 0, 'wide-bank': 0x10001, 'bool-bank': True}[fault]
    elif fault == 'bad-SR':
        value['context'][18] = 2
    else:
        value['expected_fault'] = 2
    with pytest.raises(ValueError):
        matrix.require_case(value)


def test_private_header_keeps_the_existing_complete_input_only_transport():
    source = contract.descriptor(repo.ROOT)
    image = repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    header = matrix.header(dict(source=source, cases=[case()]), image).decode()
    assert 'struct context context' in header and 'uint8_t pattern' in header
    assert all(value not in header for value in ('expected_fault', 'computed_flag', 'supplied_result'))
    for path, wanted in source['reused_source_sha256'].items():
        assert hashlib.sha256((repo.ROOT / path).read_bytes()).hexdigest() == wanted
    assert source['stock_function_stubs'] is source['native_identity_admission'] is False
