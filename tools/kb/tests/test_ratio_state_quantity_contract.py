"""Full stock composition, published facts and immutable raw-input refusals."""
from copy import deepcopy
from pathlib import Path
import hashlib
import re
import pytest
from kb import repo
from kb import ratio_state_quantity_contract as contract, ratio_state_quantity_matrix as matrix


def case():
    return dict(deepcopy(matrix.DEFAULTS), index=0, kind='controlled-source-contract')


@pytest.fixture
def owned():
    return repo.images(repo.ROOT)['JK08A'].path.read_bytes()


def test_published_counts_and_phase_identities_read_the_executed_descriptor():
    declared = contract.descriptor(repo.ROOT)
    assert declared['entries'] == [0x75174, 0x7654C]
    assert declared['phases'] == [dict(id='producer', entry=0x75174), dict(id='consumer', entry=0x7654C)]
    actual = (sum((r['end'] - r['start']) // 2 for r in declared['unit']['code']),
        len(contract.FUNCTIONS), len(declared['unit']['code']), len(declared['unit']['pools']),
        len(declared['unit']['aliases']), len(declared['controlled_calibration']))
    text = (repo.ROOT / 'defs/JK08A.ratio-state-quantity.md').read_text()
    found = re.search(r'binds (\d+) stock instructions in (\d+) actual entry paths and (\d+) spans,\s*'
        r'(\d+) literal pools, (\d+) four-byte RAM pointer aliases and (\d+) calibration spans', text)
    assert found is not None and tuple(map(int, found.groups())) == actual
    assert actual == (777, 11, 12, 45, 6, 53)
    curve, = [r for r in declared['input_blobs'] if r['name'] == 'ratio_curve']
    assert (curve['address'], curve['size']) == (0x15770, 32)
    assert {0x21BBC, 0x21CE0, 0x224FA, 0x263F4, 0x264CC, 0x26740, 0x26984, 0x26A60, 0x26C78, 0x75174, 0x7654C} == set(contract.FUNCTIONS)
    assert (declared['context_bytes'], declared['frame_bytes'], declared['frame_prefix']) == (80, 192, 160)


def test_fixture_preserves_every_instruction_and_only_relocates_exact_full_pointers(owned):
    source = contract.descriptor(repo.ROOT)
    fixture, aliases = contract.independent_fixture(source, owned)
    changed = {i for i, (a, b) in enumerate(zip(owned, fixture)) if a != b}
    allowed = {at for row in aliases for at in range(row['address'], row['address'] + 4)}
    assert changed <= allowed
    for row in source['unit']['code']:
        assert fixture[row['start']:row['end']] == owned[row['start']:row['end']]
    for row in aliases:
        assert row['width'] == 4 and row['original'] >= 0xFFFF0000
        assert int.from_bytes(fixture[row['address']:row['address'] + 4], 'big') == matrix.RAM_BASE + (row['original'] & 65535)
    wrong = bytearray(owned)
    wrong[0x7654C] ^= 1
    with pytest.raises(ValueError):
        contract.independent_fixture(source, bytes(wrong))


@pytest.mark.parametrize('fault', ('bool-word', 'short-context', 'bad-SR', 'bad-guard', 'supplied-weight', 'wrong-width'))
def test_raw_input_refuses_lost_width_context_or_a_supplied_handoff(fault):
    value = case()
    if fault == 'bool-word':
        value['word_1702'] = True
    elif fault == 'short-context':
        value['consumer_context'].pop()
    elif fault == 'bad-SR':
        value['producer_context'][18] = 2
    elif fault == 'bad-guard':
        value['ratio_curve'][15] = 65536
    elif fault == 'supplied-weight':
        value['handoff_quantity'] = 32768
    else:
        value['word_177c'] = 65536
    with pytest.raises(ValueError):
        matrix.require_case(value)


def test_header_has_two_complete_input_contexts_without_supplied_results(owned):
    source = contract.descriptor(repo.ROOT)
    value = case()
    raw = matrix.header(dict(source=source, cases=[value]), owned).decode()
    assert 'struct context contexts[2]' in raw
    body = '\n'.join(raw.splitlines()[1:])
    assert all(word not in body for word in ('expected', 'handoff_quantity', 'quotient', 'computed_blend'))
    assert matrix.memory(value)[0x19A2:0x19A4] == value['prior_19a2'].to_bytes(2, 'big')
    assert matrix.context(source, value, 0) != matrix.context(source, value, 1)


def test_reused_full_originals_remain_pinned_and_all_stock_controls_are_checked(owned):
    source = contract.descriptor(repo.ROOT)
    for name, wanted in source['reused_source_sha256'].items():
        assert hashlib.sha256((Path(repo.ROOT) / name).read_bytes()).hexdigest() == wanted
    assert any(name.endswith('timing_denominator_capture_evidence.py') for name in source['reused_source_sha256'])
    assert any(name.endswith('register_only_helpers_capture_evidence.py') for name in source['reused_source_sha256'])
    assert source['stock_function_stubs'] is False and source['scale_admission'] is False
    for row in source['control_blobs']:
        assert owned[row['address']:row['address'] + row['size']].hex() == row['stock_hex']


def test_centered_neighbor_and_first_axis_word_have_one_complete_physical_owner():
    source = contract.descriptor(repo.ROOT)
    blob, = [r for r in source['input_blobs'] if r['name'] == 'centered_curve_axis']
    assert (blob['address'], blob['size']) == (0x15276, 32)
    assert source['physical_overlap']['guard_word_address'] == source['physical_overlap']['axis_address'] == 0x15286
    assert source['physical_overlap']['guard_is_same_physical_word_as_first_axis_knot'] is True
    calibration = matrix.input_calibrations(case())
    assert 0x15286 not in calibration and len(calibration[0x15276]) == 32
