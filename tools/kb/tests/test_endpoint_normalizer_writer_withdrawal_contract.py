"""Complete natural root, immutable transport and physical endpoint geometry refusals."""
from copy import deepcopy
import hashlib
import re
import pytest
from kb import repo
from kb import endpoint_normalizer_writer_withdrawal_contract as contract
from kb import endpoint_normalizer_writer_withdrawal_matrix as matrix


def case():
    return dict(deepcopy(matrix.DEFAULTS), index=0, kind='controlled-source-contract')


def test_published_counts_and_natural_root_read_the_executed_descriptor():
    source = contract.descriptor(repo.ROOT)
    assert source['entries'] == [0x7AF78]
    actual = (sum((r['end'] - r['start']) // 2 for r in source['unit']['code']),
        len(contract.FUNCTIONS), len(source['unit']['code']), len(source['unit']['pools']),
        len(source['unit']['aliases']), len(source['controlled_calibration']))
    text = (repo.ROOT / 'defs/JK08A.endpoint-normalizer-writer-withdrawal-paths.md').read_text()
    found = re.search(r'binds (\d+) stock instructions in (\d+) actual entry paths and (\d+) spans,\s*'
        r'(\d+) literal pools, (\d+) four-byte RAM pointer aliases and (\d+) calibration spans', text)
    assert found is not None and tuple(map(int, found.groups())) == actual == (396, 6, 6, 20, 3, 24)
    assert set(contract.FUNCTIONS) == {0x7AF78, 0x264F8, 0x26984, 0x26C78, 0x26740, 0x21BBC}
    assert 0x7AE80 not in {r['start'] for r in source['unit']['code']}
    assert (source['context_bytes'], source['frame_bytes'], source['frame_prefix']) == (80, 192, 160)
    assert [(r['name'], r['address'], r['size']) for r in source['input_blobs']] == [
        ('upper', 0x154C0, 32), ('lower', 0x154E0, 32), ('axis', 0x14BAA, 32)]
    assert [(r['address'], r['size']) for r in source['control_blobs']] == [(0x15500, 2)]
    assert source['selected']['whole_datum_absence_required'] is True
    assert source['selected']['existing_family'] == 'scalar-ram-leaf-withdrawal'


def test_fixture_retains_all_instructions_and_only_aliases_exact_full_pointer_words():
    source = contract.descriptor(repo.ROOT)
    image = repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    fixture, aliases = contract.independent_fixture(source, image)
    changed = {i for i, (a, b) in enumerate(zip(image, fixture)) if a != b}
    assert changed <= {i for row in aliases for i in range(row['address'], row['address'] + 4)}
    for row in source['unit']['code']:
        assert fixture[row['start']:row['end']] == image[row['start']:row['end']]
    wrong = bytearray(image)
    wrong[0x7AF78] ^= 1
    with pytest.raises(ValueError):
        contract.independent_fixture(source, bytes(wrong))


@pytest.mark.parametrize('fault', ('bool-status', 'wide-word', 'short-context', 'bad-SR', 'short-axis', 'wide-guard', 'supplied-output'))
def test_raw_input_refuses_lost_width_context_or_supplied_results(fault):
    value = case()
    if fault == 'bool-status':
        value['byte_41fb'] = True
    elif fault == 'wide-word':
        value['word_338c'] = 65536
    elif fault == 'short-context':
        value['context'].pop()
    elif fault == 'bad-SR':
        value['context'][18] = 2
    elif fault == 'short-axis':
        value['axis'].pop()
    elif fault == 'wide-guard':
        value['lower_guard'] = 65536
    else:
        value['expected_3478'] = 800
    with pytest.raises(ValueError):
        matrix.require_case(value)


def test_header_and_pinned_complete_previous_originals_preserve_existing_transport():
    source = contract.descriptor(repo.ROOT)
    image = repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    raw = matrix.header(dict(source=source, cases=[case()]), image).decode()
    assert 'struct context context' in raw and 'uint8_t pattern' in raw
    assert all(key not in raw for key in ('expected_3478', 'computed_output', 'handoff', 'supplied_result'))
    for name, wanted in source['reused_source_sha256'].items():
        assert hashlib.sha256((repo.ROOT / name).read_bytes()).hexdigest() == wanted
    assert source['full_existing_same_primary_originals'] == ['request_limit_normalization_paths', 'timing_denominator']
    assert source['native_identity_admission'] is source['stock_function_stubs'] is False
