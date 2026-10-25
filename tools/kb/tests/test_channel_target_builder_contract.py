"""Exact executed descriptor counts, native low-byte premise and raw-input refusals."""
from copy import deepcopy
import hashlib
import re
import pytest
from kb import repo
from kb import channel_target_builder_contract as contract, channel_target_builder_matrix as matrix


def case():
    return dict(deepcopy(matrix.DEFAULTS), index=0, kind='complete-source-contract')


def test_published_counts_and_physical_inputs_read_the_executed_descriptor():
    source = contract.descriptor(repo.ROOT)
    actual = (sum((row['end'] - row['start']) // 2 for row in source['unit']['code']),
              len(contract.FUNCTIONS), len(source['unit']['code']), len(source['unit']['pools']),
              len(source['unit']['aliases']), len(source['controlled_calibration']))
    text = (repo.ROOT / 'defs/JK08A.channel-target-builder.md').read_text()
    match = re.search(r'binds (\d+) stock instructions in\s*(\d+) actual entry paths and (\d+) spans, '
                      r'(\d+) literal pools, (\d+) four-byte RAM pointer\s*aliases and (\d+) calibration spans', text)
    assert match is not None and tuple(map(int, match.groups())) == actual == (457, 8, 9, 31, 11, 41)
    assert source['entries'] == [0x6F48C]
    assert source['entry_premises'] == dict(register4_low_byte=1, register4_upper24_independent=True,
        other19_context_fields_independent=True, physical_channel_to_bank_identity_admission=False)
    assert source['actual_output'] == dict(site=0x6F668, address=0xFFFF28BE, width_bytes=2)
    assert [(row['name'], row['address'], row['size']) for row in source['input_blobs']] == [
        ('inverse_curve', 0x155A0, 66), ('inverse_axis', 0x13202, 64),
        ('upper_curve', 0x12DAA, 9), ('upper_axis', 0x12D9A, 8)]
    assert source['actual_ROM_GBR'] == dict(value=0x9574, word_addresses=[0x9574, 0x9576, 0x9578], relocated=False)
    assert len(source['caller_scoped_infeasible_sites']) == 8
    assert (source['context_bytes'], source['frame_bytes'], source['frame_prefix']) == (80, 192, 160)
    assert source['full_existing_channel_target_reader_original_required_same_primary'] is True
    assert source['finite_shared_native_owner_companion_required'] is True


def test_fixture_keeps_all_instruction_bytes_and_only_relocates_exact_full_RAM_pointers():
    source = contract.descriptor(repo.ROOT)
    image = repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    fixture, aliases = contract.independent_fixture(source, image)
    assert {index for index, (first, second) in enumerate(zip(image, fixture)) if first != second} <= {
        address for row in aliases for address in range(row['address'], row['address'] + 4)}
    assert not any(row['original'] == 0x9574 for row in aliases)
    for row in source['unit']['code']:
        assert fixture[row['start']:row['end']] == image[row['start']:row['end']]
    changed = bytearray(image)
    changed[0x6F48C] ^= 1
    with pytest.raises(ValueError):
        contract.independent_fixture(source, bytes(changed))


@pytest.mark.parametrize('fault', ('bool-word', 'wide-byte', 'short-axis', 'short-neighbor', 'short-context',
    'other-index', 'bool-index', 'bad-SR', 'supplied-output'))
def test_complete_raw_inputs_refuse_partial_or_semantic_substitutions(fault):
    value = case()
    if fault == 'bool-word':
        value['word_19b2'] = True
    elif fault == 'wide-byte':
        value['rom_8cb6'] = 256
    elif fault == 'short-axis':
        value['inverse_axis'].pop()
    elif fault == 'short-neighbor':
        value['upper_curve'].pop()
    elif fault == 'short-context':
        value['context'].pop()
    elif fault == 'other-index':
        value['context'][4] = 0x12345600
    elif fault == 'bool-index':
        value['context'][4] = True
    elif fault == 'bad-SR':
        value['context'][18] = 2
    else:
        value['expected_target'] = 156
    with pytest.raises(ValueError):
        matrix.require_case(value)


def test_upper24_bits_remain_independent_and_private_header_remains_input_only():
    value = case()
    for raw in (1, 0x80000001, 0xFFFFFF01):
        value['context'][4] = raw
        matrix.require_case(value)
    source = contract.descriptor(repo.ROOT)
    image = repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    header = matrix.header(dict(source=source, cases=[value]), image).decode()
    assert 'struct context context' in header and 'uint8_t pattern' in header
    assert 'builder_calibration_blobs' in header
    assert all(word not in header for word in ('expected_target', 'computed_request', 'supplied_result'))
    for path, wanted in source['reused_source_sha256'].items():
        assert hashlib.sha256((repo.ROOT / path).read_bytes()).hexdigest() == wanted
    assert source['stock_function_stubs'] is source['native_identity_admission'] is False
