"""Lower-knot selection and the owned ratio scale have separate admission."""

import json
import pytest

from kb import compile, repo
from kb import counter_threshold_contract as contract
from kb import counter_threshold_factor_contract as factor
from kb import counter_threshold_matrix as matrix
from kb import counter_threshold_semantics as numeric


def test_fixture_preserves_stock_words_and_only_declared_RAM_literals_and_return():
    declared = contract.descriptor(repo.ROOT)
    image = repo.images()['JK08A'].path.read_bytes()
    fixture, aliases, boundaries = contract.independent_fixture(declared, image)
    restored = bytearray(fixture)
    assert [row['address'] for row in aliases] == [0x797F8, 0x797FC]
    assert [row['address'] for row in boundaries] == [0x7974A]
    for row in aliases:
        restored[row['address']:row['address'] + 4] = row['original'].to_bytes(4, 'big')
    for row in boundaries:
        restored[row['address']:row['end']] = bytes.fromhex(row['stock'])
    assert bytes(restored) == image
    for first, last in contract.SPANS:
        assert fixture[first:last] == image[first:last]


@pytest.mark.parametrize('flag', contract.FLAGS)
def test_raw_descriptor_refuses_implicit_admission(tmp_path, flag):
    text = (repo.ROOT / contract.DESCRIPTOR).read_text()
    path = tmp_path / contract.DESCRIPTOR
    path.parent.mkdir(parents=True)
    path.write_text(text.replace(flag + ' = false', flag + ' = true', 1))
    with pytest.raises(ValueError):
        contract.descriptor(tmp_path)


def test_grid_uses_lower_knots_without_value_interpolation():
    axis = bytes([0, 64, 128, 192])
    table = bytes(range(16))
    assert numeric.cell(table, axis, axis, 63, 127) == dict(value=1, row=0, column=1, reads=(1,))
    assert numeric.cell(table, axis, axis, 64, 128) == dict(value=6, row=1, column=2, reads=(6,))
    assert numeric.cell(table, axis, axis, 255, 255) == dict(value=15, row=3, column=3, reads=(15,))


def test_ratio_multiplies_before_division_and_saturates_only_the_counter():
    declared = contract.descriptor(repo.ROOT)
    image = repo.images()['JK08A'].path.read_bytes()
    case = dict(index=0, kind='window', entry=matrix.ENTRY, pattern='nine', axis='strict',
                row=44, word=92, elapsed=7, counter=65535, variant=0, sr=0)
    result = numeric.caller(matrix.calibrations(declared, image, case), matrix.memory(case))
    assert result['dividend'] == 63 and result['quotient'] == result['threshold'] == 6
    assert result['counter'] == 65535 and result['active'] == 1
    assert result['fault'] == bytes.fromhex('a5c3d2e1')


def test_factor_retains_exact_existing_scale_and_withdraws_only_original_reader_selector():
    model = compile.build(repo.ROOT)
    row = factor.descriptor(repo.ROOT)['reference'][0]
    symbol = model.symbols[factor.SYMBOL]
    link = next(item for item in model.links if item.owner is symbol.meaning
                and item.type == 'reader' and item.to.key == factor.TARGET)
    assert factor.original(row, link)
    assert {key: symbol.value(key) for key in factor.FIELDS} == factor.FIELDS
    old, new = json.loads(row['original_claim_json']), json.loads(row['proposed_claim_json'])
    assert old['props']['supports'] == new['props']['supports'] == 'scale'
    assert new['roles'] == ['arithmetic-factor']
    before, after = json.loads(row['original_ledger_json']), json.loads(row['proposed_ledger_json'])
    assert before[0]['scale'] == after[0]['scale'] == [3, 4, 5, 6, 7, 8]
    assert len(before[0]['dependency']) == len(after[0]['dependency']) + 1


@pytest.mark.parametrize('old,new', (('ratio', 'seconds'), ('x/10', 'x/100'), ('x*10', 'x*100'), ('code', 'manual')))
def test_factor_descriptor_refuses_scale_donation_or_reinterpretation(tmp_path, old, new):
    path = tmp_path / factor.DESCRIPTOR
    path.parent.mkdir(parents=True)
    text = (repo.ROOT / factor.DESCRIPTOR).read_text()
    path.write_text(text.replace(old, new))
    with pytest.raises(ValueError):
        factor.descriptor(tmp_path)
