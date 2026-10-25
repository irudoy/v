"""Independent B variation and all normalization bypasses retain exact scope."""

import pytest
from kb import compile, repo
from kb import adorable_llama_argument_contract as arguments
from kb import adorable_llama_contract as contract
from kb import adorable_llama_matrix as matrix
from kb import adorable_llama_semantics as numeric
from kb.model import SymbolKey


def test_exact_alias_and_SP28_return_restore_the_stock_image():
    declared = contract.descriptor(repo.ROOT)
    image = repo.images()['JK08A'].path.read_bytes()
    fixture, aliases, boundaries = contract.independent_fixture(declared, image)
    assert aliases == [dict(address=0x416B4, original=0xFFFF2458, alias=0x01002458)]
    assert boundaries[0]['address'] == 0x416F8 and boundaries[0]['bytes'] == '57f7472a000b0009'
    assert contract.BOUNDARY['stack_return_offset'] == 28
    restored = bytearray(fixture)
    for row in aliases:
        restored[row['address']:row['address'] + 4] = row['original'].to_bytes(4, 'big')
    for row in boundaries:
        restored[row['address']:row['end']] = bytes.fromhex(row['stock'])
    assert bytes(restored) == image


@pytest.mark.parametrize('flag', contract.FLAGS)
def test_descriptor_refuses_implicit_admission(tmp_path, flag):
    path = tmp_path / contract.DESCRIPTOR
    path.parent.mkdir(parents=True)
    path.write_text((repo.ROOT / contract.DESCRIPTOR).read_text().replace(flag + ' = false', flag + ' = true', 1))
    with pytest.raises(ValueError):
        contract.descriptor(tmp_path)


def test_only_B_changes_both_actual_operands_and_unsaturated_output():
    image = repo.images()['JK08A'].path.read_bytes()
    declared = contract.descriptor(repo.ROOT)

    def one(pattern):
        case = dict(index=0, kind='window', entry=matrix.ENTRY, pattern=pattern,
                    coordinate=64, flags=0x42, variant=0, sr=0)
        calibration = matrix.calibrations(declared, image, case)
        return calibration, numeric.caller(calibration, matrix.memory(case), case['coordinate'])

    first_calibration, first = one('ratio-first')
    second_calibration, second = one('ratio-second')
    assert first_calibration[0x12798] == second_calibration[0x12798]
    assert (first['dividend'], first['divisor'], first['output']) == (1024, 8, 128)
    assert (second['dividend'], second['divisor'], second['output']) == (512, 10, 51)
    assert first['fault'] == second['fault'] == bytes.fromhex('a5c3d2e1')
    assert one('maximum')[1]['opened'] is False and one('maximum')[1]['output'] == 0
    assert one('anchor-equal')[1]['divided'] is False and one('anchor-equal')[1]['output'] == 255
    assert one('anchor-above')[1]['divided'] is False and one('anchor-above')[1]['output'] == 255
    assert one('tiny-divisor')[1]['divisor'] == 1 and one('tiny-divisor')[1]['quotient'] == 65280


def test_exact_disposition_matches_the_retained_signed_reader():
    model = compile.build(repo.ROOT)
    row = arguments.descriptor(repo.ROOT)['reference'][0]
    symbol = model.symbols[SymbolKey('7mfk', 'tbl', row['address'])]
    link = next(item for item in model.links if item.owner is symbol.meaning
                and item.type == 'reader' and item.to.key == arguments.TARGET)
    assert arguments.original(row, link)
    assert row['owner'] == 'adorable-llama/tbl' and row['wrapper'] == 0x26388


def test_document_binds_the_actual_delay_and_stack_temporary_boundary():
    text = (repo.ROOT / 'defs/JK08A.adorable-llama.md').read_text()
    for at in (0x413CC, 0x4161C, 0x12798, 0x127D8, 0x4168A, 0x4168C, 0x416F6, 0x416F8):
        assert f'{at:08X}' in text
    assert 'SP+24' in text and 'SP+28' in text
