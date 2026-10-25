"""Full stock composition, published facts and immutable raw-input refusals."""
from copy import deepcopy
from pathlib import Path
import hashlib
import re
import pytest
from kb import repo
from kb import torque_correction_ratio_contract as contract, torque_correction_ratio_matrix as matrix


def case():
    return dict(deepcopy(matrix.DEFAULTS), index=0, kind='controlled-source-contract')


@pytest.fixture
def owned():
    return repo.images(repo.ROOT)['JK08A'].path.read_bytes()


def test_published_counts_and_phase_identities_read_the_executed_descriptor():
    declared = contract.descriptor(repo.ROOT)
    assert declared['entries'] == [0x658A4, 0x64A1C]
    assert declared['phases'] == [dict(id='producer', entry=0x658A4), dict(id='consumer', entry=0x64A1C)]
    actual = (sum((r['end'] - r['start']) // 2 for r in declared['unit']['code']),
        len(contract.FUNCTIONS), len(declared['unit']['code']), len(declared['unit']['pools']),
        len(declared['unit']['aliases']), len(declared['controlled_calibration']))
    text = (repo.ROOT / 'defs/JK08A.torque-correction-ratio.md').read_text()
    found = re.search(r'binds (\d+) stock instructions in (\d+) actual entry paths and (\d+) spans,\s*'
        r'(\d+) literal pools, (\d+) four-byte RAM pointer aliases and (\d+) calibration spans', text)
    assert found is not None and tuple(map(int, found.groups())) == actual
    assert actual == (690, 9, 10, 46, 12, 54)
    curve, = [r for r in declared['input_blobs'] if r['name'] == 'coefficient_curve']
    assert (curve['address'], curve['size']) == (0x14C1A, 18)
    assert {0x21BBC, 0x263F4, 0x264CC, 0x26740, 0x26984, 0x26A60, 0x26C78, 0x658A4, 0x64A1C} == set(contract.FUNCTIONS)
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
    wrong[0x64A1C] ^= 1
    with pytest.raises(ValueError):
        contract.independent_fixture(source, bytes(wrong))


@pytest.mark.parametrize('fault', ('bool-word', 'short-context', 'bad-SR', 'bad-guard', 'supplied-weight', 'wrong-width'))
def test_raw_input_refuses_lost_width_context_or_a_supplied_handoff(fault):
    value = case()
    if fault == 'bool-word':
        value['word_11bc'] = True
    elif fault == 'short-context':
        value['consumer_context'].pop()
    elif fault == 'bad-SR':
        value['producer_context'][18] = 2
    elif fault == 'bad-guard':
        value['coefficient_curve'][8] = 65536
    elif fault == 'supplied-weight':
        value['handoff_correction'] = 32768
    else:
        value['word_199e'] = 65536
    with pytest.raises(ValueError):
        matrix.require_case(value)


def test_header_has_two_complete_input_contexts_without_supplied_results(owned):
    source = contract.descriptor(repo.ROOT)
    value = case()
    raw = matrix.header(dict(source=source, cases=[value]), owned).decode()
    assert 'struct context contexts[2]' in raw
    body = '\n'.join(raw.splitlines()[1:])
    assert all(word not in body for word in ('expected', 'handoff_correction', 'quotient', 'computed_blend'))
    assert matrix.memory(value)[0x14E2:0x1910] == value['prior_14e2'].to_bytes(2, 'big')
    assert matrix.context(source, value, 0) != matrix.context(source, value, 1)


def test_reused_full_originals_remain_pinned_and_all_stock_controls_are_checked(owned):
    source = contract.descriptor(repo.ROOT)
    for name, wanted in source['reused_source_sha256'].items():
        assert hashlib.sha256((Path(repo.ROOT) / name).read_bytes()).hexdigest() == wanted
    assert any(name.endswith('timing_denominator_capture_evidence.py') for name in source['reused_source_sha256'])
    assert source['stock_function_stubs'] is False and source['scale_admission'] is False
    for row in source['control_blobs']:
        assert owned[row['address']:row['address'] + row['size']].hex() == row['stock_hex']
