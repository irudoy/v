"""Bind primary quarter-BFS selection, bounded split multiplication, and Q7 publication."""

import hashlib
import re

import pytest

from kb import compile, derive, repo, sh2
from kb.model import SymbolKey


SPANS = (
    (0x21ce0, 0x21dc6, 'e77ecbefb7c84f7f75e93b1e704bb8b0fad41a5c1c9b63214097a0da3cd166df'),
    (0x21f40, 0x2202e, '2ed1116dc2b8e51a6e4a4c4cf0682b41d7ccd81ae42ab7a197beb3b2b9fd78b9'),
    (0x3b7c6, 0x3b8b8, 'ade06cce609925e1c3648768ca33f4cccc2a0115ea0be820b5b71933d6161c5c'),
    (0x3b8da, 0x3b908, 'e14247203e885b1fb1c6891d388f9f6c138d03fb5a6eaac746f5395fb4fb13bb'),
    (0x88fb, 0x88fc, '084fed08b978af4d7d196a7446a86b58009e636b611db16211b65a9aadff29c5'),
    (0x8a27, 0x8a28, '62c66a7a5dd70c3146618063c344e531e6d4b59e379808443ce962b3abd63c5a'),
    (0x9284, 0x9286, 'e9a3919b0a99cfad0dfb2e5797ebef91b8bf86b8e669a46adba618e11c236eaa'),
    (0x21dc8, 0x21dd0, 'eb7fb46dde2694e213d4f0999632d1b7f61dce5d56c3d71f2e5ca125e3c9f565'),
    (0x22030, 0x22038, 'eb7fb46dde2694e213d4f0999632d1b7f61dce5d56c3d71f2e5ca125e3c9f565'),
    (0x3b8b8, 0x3b8bc, 'eba7becf8e7c0d77aae9f01b15efa2731455043211f626f836ad3651057a3ea0'),
    (0x3b98c, 0x3b990, '1f90d4097fc8764f4d05298ef31b0c6baf272cf19e8af38b17dfcfae8776b238'),
    (0x3b9a0, 0x3b9c0, 'de7d12161a36b77e476d6d50b3f31563948cc05132e16e516204d2fd4bccef3e'),
    (0x3b9cc, 0x3b9d8, '7ea244625d34929f52790e56f56e94c646a9efc7ce71cc3c2a8361b9397b29d9'),
    (0x3b770, 0x3b7c6, '82b4e40a15aa33ee94c09362df9a1b137b034762df19206844ebf3e1e4f9c034'),
    (0x3b990, 0x3b9a0, '2e06c850a7b1bd342b00a42b0d8deabda65c9c159fc3ac09bde066edd76785bc'),
)


def verify_base(data):
    for start, end, expected in SPANS:
        assert hashlib.sha256(data[start:end]).hexdigest() == expected, f'{start:08x}'

    def word(address, size=2):
        return int.from_bytes(data[address:address+size], 'big')

    def instruction(address):
        return sh2.decode(word(address), address)

    assert instruction(0x3b770).value == ('pool',0x3b98c,4)
    assert word(0x3b98c,4) == 0xffff1dec
    assert word(0x3b7b8) == 0xc940 and word(0x3b7be) == 0x6403
    assert instruction(0x3b7ce).access == sh2.Access(12,1,1,'load')
    assert word(0x3b7d0) == 0xc820
    assert instruction(0x3b7d4).access == sh2.Access(7,8,2,'load')
    assert instruction(0x3b7e2).access == sh2.Access(7,20,2,'load')
    assert word(0x3b9a4,4)+8 == 0xffff11dc
    assert word(0x3b9a4,4)+20 == 0xffff11e8
    assert instruction(0x3b802).access == sh2.Access('gbr',0x4c,4,'load')
    assert word(0x3b804) == 0x4015 and instruction(0x3b806).target == 0x3b80e
    assert word(0x3b9a8,4) == 0x9284 and word(0x9284) == 26806
    assert instruction(0x3b814).access == sh2.Access(5,0,2,'load')
    assert word(0x3b9ac,4) == 0x8a27 and data[0x8a27] == 109
    assert instruction(0x3b824).access == sh2.Access(4,0,1,'load')
    assert word(0x3b9b0,4) == 0x88fb and data[0x88fb] == 3
    for address in (0x3b872,0x3b888,0x3b894):
        assert instruction(address).flow == 'call' and instruction(address).delayed
    assert word(0x3b9b8,4) == 0x21ce0 and word(0x3b9bc,4) == 0x21f40
    assert word(0x3b9b4,4) == 0x726f9 and word(0x3b8b8) == 0x727
    assert word(0x3b8ba) == 9163 and (0x726f9*9163)>>16 == 65535
    assert instruction(0x3b8b6).access == sh2.Access('gbr',0x54,4,'store')
    assert instruction(0x3b8e0).access == sh2.Access(8,0,1,'load',indexed=True)
    assert word(0x3b9cc,4)+0x4c == 0xffff1160
    assert instruction(0x3b906).access == sh2.Access(10,0x1a,2,'store')
    assert word(0x3b9d4,4)+0x1a == 0xffff1062
    assert word(0x21dc8,4) == word(0x22030,4) == 0xffff9818
    assert word(0x21dcc,4) == word(0x22034,4) == 0x44e


def test_primary_bfs_speed_selection_split_product_unsigned_divisions_and_q7_store_match_stock():
    verify_base(derive.image_bytes(repo.layout('7mfk')))


@pytest.mark.parametrize('address',[address for start,end,_ in SPANS for address in range(start,end)])
def test_changed_primary_bfs_input_mode_width_product_divider_cap_coefficient_or_store_fails(address):
    data=bytearray(derive.image_bytes(repo.layout('7mfk')))
    data[address]^=1
    with pytest.raises(AssertionError):
        verify_base(data)


def test_primary_bfs_keeps_signed_input_split_product_speed_selectors_and_coherent_q7_cache():
    model = compile.cached(repo.ROOT)
    chain = model.entities[('chain', 'airflow_load')]
    primary = ('N = max(64,uint16(ffff11e8)); '
               'p = floor(ROM8[0x00008a27]*ROM16[0x00009284]*uint32(ffff1e38)/256); '
               't = 256*uint32(floor(p/256))+(p&255); '
               'fixed = min(0x726f9,floor(t/(ROM8[0x000088fb]*N))); '
               'ffff1e40 = floor(fixed*9163/65536)')
    compensation = 'ffff1062 = min(65535,floor(uint32(ffff1e40*uint8(ffff1160))/128))'
    for index in (16, 17, 18, 19):
        assert chain.steps[index]['note'] == primary
        assert [ref.address for ref in chain.steps[index]['via']] == [0x3b75c]
    for index in (20, 22):
        assert chain.steps[index]['note'] == compensation
        assert [ref.address for ref in chain.steps[index]['via']] == [0x3b75c]
    for address, width in ((0xffff1e40, 32), (0xffff1062, 16), (0xffff1160, 8),
                           (0xffff11e8, 16), (0xffff11dc, 16), (0xffff24b1, 8)):
        symbol = model.symbols[SymbolKey('7mfk', 'ram', address)]
        assert symbol.value('width') == width and symbol.value('signed') is False
        assert symbol.value('level') == 'code'
    for address, name in ((0xffff11dc, 'bfs_alternate_speed'), (0xffff24b1, 'bfs_state_flags')):
        symbol = model.symbols[SymbolKey('7mfk', 'ram', address)]
        assert symbol.meaning.key == name + '/ram'
        assert symbol.meaning.props['block'] == 'airflow_load/block'
        assert 'outside' in symbol.meaning.props['summary']
    quarter = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff1e40))
    assert 'modulo 2^40' in quarter.props['summary']
    assert any('0x02017ffc' in note and 'Stock F=109' in note for note in quarter.props['note'])
    inputs = [link for link in quarter.links if link.type == 'input']
    assert {link.to.key for link in inputs} == {
        'nice-coucal/tbl', 'polar-viper/ram', 'vigorous-horse/ram',
        'bfs_alternate_speed/ram', 'statuesque-husky/ram',
    }
    selectors = [link for link in quarter.links if link.type == 'selector']
    assert {link.to.key: link.slot for link in selectors} == {
        'satisfied-bulldog/ram': 'bit5', 'small-sheep/ram': 'bit6',
    }
    for link in selectors:
        assert link.stated == {'7mfk'}
        assert [ref.address for ref in link.props['via']] == [0x3b75c]
        assert any(evidence.get('kind') == 'test' for evidence in link.evidence)
    aggregate = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff1e38))
    for address, storage in ((0x9284, 'uint16'), (0x8a27, 'uint8')):
        scalar = model.meaning_of(SymbolKey('7mfk', 'tbl', address))
        assert scalar.props['access'] == 'direct-scalar' and scalar.props['storage'] == storage
        assert not any(link.type == 'index' and link.to is aggregate for link in scalar.links)
        [lookup] = [link for link in quarter.links if link.type == 'lookup' and link.to is scalar]
        assert 'fixed address' in lookup.props['note'] and 'never indexes' in lookup.props['note']
    compensated = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff1062))
    assert {link.to.key for link in compensated.links if link.type == 'input'} == {
        'voracious-oarfish/ram', 'majestic-jackrabbit/ram',
    }
    assert any('coherent cache/RAM' in note for note in compensated.props['note'])
    producer = model.meaning_of(SymbolKey('7mfk', 'fn', 0x3b75c))
    thresholds = [link for link in producer.links if link.type == 'threshold'
                  and link.to in (quarter, compensated)]
    assert len(thresholds) == 2
    assert any('zero denominator' in link.props['note'] and 'low-40-bit' in link.props['note']
               for link in thresholds)
    assert any('low 32 bits' in link.props['note'] and '65535' in link.props['note']
               for link in thresholds)
