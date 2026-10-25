"""Executed updater counts, physical inputs and complete native index1 raw-input refusals."""
from copy import deepcopy
import hashlib
import re
import pytest
from kb import repo
from kb import ltft_adjustment_update_contract as contract, ltft_adjustment_update_matrix as matrix


def case():
    return dict(deepcopy(matrix.DEFAULTS), index=0, kind='complete-source-contract')


def test_published_counts_and_controls_read_the_executed_descriptor():
    source = contract.descriptor(repo.ROOT)
    actual = (sum((row['end'] - row['start']) // 2 for row in source['unit']['code']),
              len(contract.FUNCTIONS), len(source['unit']['code']), len(source['unit']['pools']),
              len(source['unit']['aliases']), len(source['controlled_calibration']))
    text = (repo.ROOT / 'defs/JK08A.ltft-adjustment-update.md').read_text()
    match = re.search(r'binds (\d+) stock instructions in\s*(\d+) actual entry paths and (\d+) spans, '
                      r'(\d+) literal pools, (\d+) four-byte RAM pointer\s*aliases and (\d+) calibration spans', text)
    assert match is not None and tuple(map(int, match.groups())) == actual == (553, 3, 6, 34, 16, 42)
    assert source['entries'] == [0x58168] and contract.FUNCTIONS == (0x21BBC, 0x25E20, 0x58168)
    assert source['entry_premises'] == dict(register4_low_byte=1, register4_upper24_independent=True,
        other19_context_fields_independent=True, new_physical_bank_identity_admission=False)
    assert source['actual_selected_reads'] == [dict(site=0x5819C, address=0xFFFF2304, width_bytes=2),
                                              dict(site=0x5820A, address=0xFFFF2308, width_bytes=2)]
    assert source['actual_output'] == dict(site=0x5848E, address=0xFFFF564A, width_bytes=2)
    controls = re.search(r'(\d+) raw ROM controls', text)
    stack = re.search(r'root uses (\d+) stack bytes', ' '.join(text.split()))
    assert controls is not None and int(controls[1]) == len(source['control_blobs']) == 8
    assert stack is not None and int(stack[1]) == source['root_stack_bytes'] == 68
    assert source['actual_fixed_divisor'] == 25600
    assert source['actual_fixed_record'] == dict(site=0x58478, index=0x129, address=0xFFFF5A94)
    assert (source['context_bytes'], source['frame_bytes'], source['frame_prefix']) == (80, 192, 160)
    assert source['complete_existing_bank_pulse_and_learning_originals_required_same_primary'] is True


def test_fixture_keeps_complete_stock_instructions_and_only_declared_full_pointer_aliases():
    source = contract.descriptor(repo.ROOT)
    image = repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    fixture, aliases = contract.independent_fixture(source, image)
    assert {index for index, (first, second) in enumerate(zip(image, fixture)) if first != second} <= {
        address for row in aliases for address in range(row['address'], row['address'] + 4)}
    for row in source['unit']['code']:
        assert fixture[row['start']:row['end']] == image[row['start']:row['end']]
    changed = bytearray(image); changed[0x58168] ^= 1
    with pytest.raises(ValueError):
        contract.independent_fixture(source, bytes(changed))


@pytest.mark.parametrize('fault', ('bool-word', 'wide-word', 'wide-byte', 'short-context', 'other-index',
    'bool-index', 'bad-SR', 'supplied-output'))
def test_raw_inputs_refuse_partial_context_or_supplied_results(fault):
    value = case()
    if fault == 'bool-word':
        value['word_2308'] = True
    elif fault == 'wide-word':
        value['word_564a'] = 65536
    elif fault == 'wide-byte':
        value['rom_878b'] = 256
    elif fault == 'short-context':
        value['context'].pop()
    elif fault == 'other-index':
        value['context'][4] = 0x12345600
    elif fault == 'bool-index':
        value['context'][4] = True
    elif fault == 'bad-SR':
        value['context'][18] = 2
    else:
        value['expected_trim'] = 25600
    with pytest.raises(ValueError):
        matrix.require_case(value)


def test_upper24_bits_and_complete_input_only_header_keep_original_sources_bound():
    value = case()
    for raw in (1, 0x80000001, 0xFFFFFF01):
        value['context'][4] = raw
        matrix.require_case(value)
    source = contract.descriptor(repo.ROOT)
    image = repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    header = matrix.header(dict(source=source, cases=[value]), image).decode()
    assert 'struct context context' in header and 'uint8_t pattern' in header
    assert 'trim_calibration_blobs' in header
    assert all(word not in header for word in ('expected_trim', 'computed_adjustment', 'supplied_result'))
    for path, wanted in source['reused_source_sha256'].items():
        assert hashlib.sha256((repo.ROOT / path).read_bytes()).hexdigest() == wanted
    assert source['stock_function_stubs'] is source['native_identity_admission'] is False
