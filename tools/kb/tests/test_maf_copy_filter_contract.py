"""Natural word transfers preserve sibling state and distinct bank arguments."""

import pytest

from kb import maf_copy_filter_contract as contract, maf_copy_filter_matrix as matrix
from kb import maf_copy_filter_semantics as numeric, repo


def test_existing_fixture_has_only_three_declared_ram_pool_relocations():
    declared = contract.descriptor(repo.ROOT)
    image = repo.images()['JK08A'].path.read_bytes()
    fixture, aliases = contract.independent_fixture(declared, image)
    restored = bytearray(fixture)
    assert [row['address'] for row in aliases] == [0x3AB68, 0x3AB70, 0x3AB74]
    for row in aliases:
        restored[row['address']:row['address'] + 4] = row['original'].to_bytes(4, 'big')
    assert bytes(restored) == image
    for start, end in contract.SPANS:
        assert fixture[start:end] == image[start:end]


@pytest.mark.parametrize('flag', contract.FLAGS)
def test_descriptor_refuses_implicit_admission(tmp_path, flag):
    path = tmp_path / contract.DESCRIPTOR
    path.parent.mkdir(parents=True)
    path.write_text((repo.ROOT / contract.DESCRIPTOR).read_text().replace(flag + ' = false', flag + ' = true', 1))
    with pytest.raises(ValueError):
        contract.descriptor(tmp_path)


@pytest.mark.parametrize('argument', (1, 0xF00DCA01))
def test_unsigned_copy_and_delay_slot_output_use_bank_one_and_preserve_sibling(argument):
    case = dict(kind='copy', argument=argument, input=65535, previous=0x1234, flags=0)
    before = matrix.memory(case)
    result = numeric.output('copy', argument, before, 26)
    assert (result['source'], result['destination'], result['output']) == (0x1056, 0x105A, 65535)
    assert result['memory'][0x1058:0x105A] == before[0x1058:0x105A]
    assert result['memory'][0x105A:0x105C] == bytes.fromhex('ffff')


@pytest.mark.parametrize('input,previous,coefficient,expected,step',
                         ((1000, 0, 26, 101, 0), (0, 1000, 26, 898, 0),
                          (101, 100, 0, 101, 1), (100, 101, 0, 100, -1)))
def test_separate_filter_equations_bind_real_coefficient_and_anti_stall(input, previous, coefficient, expected, step):
    before = matrix.memory(dict(kind='filter', argument=1, input=input, previous=previous, flags=0x20))
    result = numeric.output('filter', 1, before, coefficient)
    assert result['source'] == 0x105A and result['destination'] == 0x1DF2
    assert (result['output'], result['step']) == (expected, step)
    assert result['memory'][0x1DF0:0x1DF2] == before[0x1DF0:0x1DF2]


def test_document_binds_actual_sites_and_the_existing_observer_abi():
    text = (repo.ROOT / 'defs/JK08A.maf-copy-filter.md').read_text()
    for address in (0x3A982, 0x3A98E, 0x3A9A8, 0x3A9AA, 0x3A9BE, 0x3AA08, 0x3AA0A,
                    0xFFFF1056, 0xFFFF105A, 0xFFFF1DF2):
        assert f'`{address:08X}`' in text
