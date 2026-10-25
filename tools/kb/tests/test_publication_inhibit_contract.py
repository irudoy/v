"""Conditional cached-gate inputs and exact independent source boundaries."""

import pytest

from kb import repo
from kb import publication_inhibit_contract as contract,publication_inhibit_matrix as matrix
from kb import publication_inhibit_semantics as numeric


@pytest.fixture(scope='module')
def sources():
    declared=contract.descriptor(repo.ROOT)
    image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases,boundaries=contract.independent_fixture(declared,image)
    return declared,image,fixture,aliases,boundaries


def test_fixture_retains_every_tested_stock_word_and_exact_natural_helper(sources):
    declared,image,fixture,aliases,boundaries=sources
    restored=bytearray(fixture)
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    for row in boundaries:restored[row['address']:row['end']]=bytes.fromhex(row['stock'])
    assert bytes(restored)==image
    for start,end in contract.SPANS:assert fixture[start:end]==image[start:end]
    assert {row['address'] for row in aliases}==set(contract.ALIASES)
    assert len(boundaries)==1 and boundaries[0]['address']==contract.BOUNDARY['address']
    assert boundaries[0]['bytes']=='57f6472a000b0009'
    assert boundaries[0]['stock_scheduler_body_admitted'] is False


@pytest.mark.parametrize('fault',(*contract.FLAGS,'sequence','table','native-window','return','pool'))
def test_descriptor_refuses_changed_boundaries_or_admission_scope(tmp_path,fault):
    original=(repo.ROOT/contract.DESCRIPTOR).read_text()
    if fault in contract.FLAGS:text=original.replace(fault+' = false',fault+' = true',1)
    elif fault=='sequence':text=original.replace('sequence = [0x3e1da,0x3e1da,0x20f1c]',
        'sequence = [0x3e1da,0x20f1c,0x3e1da]',1)
    elif fault=='table':text=original.replace('axis_step = 64','axis_step = 1',1)
    elif fault=='native-window':text=original.replace('window_start = 4294935552','window_start = 4294940928',1)
    elif fault=='return':text=original.replace('57f6472a000b0009','000b0009',1)
    else:text=original.replace('stock_value = 0x0001202e','stock_value = 0x0001202f',1)
    assert text!=original
    path=tmp_path/contract.DESCRIPTOR
    path.parent.mkdir(parents=True)
    path.write_text(text)
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_second_invocation_changes_only_the_explicit_mode_bit():
    prior=bytes((index*37+19)&255 for index in range(matrix.RAM_SIZE))
    expected=bytearray(prior)
    expected[0x2459]|=32
    assert matrix.before({'stage':1},prior)==bytes(expected)
    assert matrix.before({'stage':2},prior)==prior
    assert matrix.native_controls(prior)==prior[0x8400:0x8500]


@pytest.mark.parametrize('rpm,expected,offsets',(
    (0,0,[0,1]),(96,0,[0,1]),(128,0,[0,1]),(159,0,[0,1]),
    (160,1,[1,2]),(161,2,[1,2]),(287,253,[2,3]),(288,255,[3]),(65535,255,[3])))
def test_separate_lookup_equation_keeps_boolean_zero_and_nonzero_interpolation_boundaries(rpm,expected,offsets):
    result=numeric.lookup(bytes((0,1,128,255)),rpm)
    assert result['output']==expected and result['operand_offsets']==offsets


def test_descending_interpolation_keeps_the_stock_directed_rounding():
    assert numeric.lookup(bytes((255,128,1,0)),128)['output']==192


@pytest.mark.parametrize('cached',(0,1,128,200,255))
@pytest.mark.parametrize('mode',(0,32))
@pytest.mark.parametrize('brake',(0,128))
def test_cache_magnitude_has_only_the_declared_boolean_publication_effect(cached,mode,brake):
    expected=0xAB if mode and (cached==0 or brake) else 0
    assert numeric.publication(0xABCD,cached,mode,brake)==expected


def test_document_binds_the_executed_table_live_snapshot_and_native_control_addresses():
    text=(repo.ROOT/'defs/JK08A.publication-inhibit-path.md').read_text()
    declared=contract.descriptor(repo.ROOT)
    for name in ('table','upstream','snapshot'):
        assert f'`{declared["table"][name]:08X}`' in text
    assert '`FFFF84C3`' in text and 'only `FFFF2459.bit5`' in text
