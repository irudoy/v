"""Bind signed BFS correction, byte interpolation, mode bypass, and publication."""

import hashlib

import pytest

from kb import compile, derive, repo, sh2
from tools.kb.tests.stock_corruption import byte_span_ids, byte_span_samples
from kb.model import SymbolKey


SPANS = (
    (0x26388, 0x2639a, 'bd2d19bd68628b952304bac3a270d93ba1472fffda43513acc2567e612a3ee2d'),
    (0x26740, 0x2676e, 'e5ebb39cde98cd32ad8cbf753572029a70a828ea592d112b2d4d5cef40cd2cb0'),
    (0x26a84, 0x26aba, '3f4b5d0003e44f4906306807e0f0a71a5e4b60589c210693dfdb07cadd676300'),
    (0x3bb86, 0x3bbc2, '9427ebfc5ea3747ffbb4703cc824a2529576b936ac6bb6ce30359cbf00f2a633'),
    (0x3bbec, 0x3bc80, '34ad1b4184dccaf27abdd4887c436caad17562abe435c5f14b74d4b291f67b2b'),
    (0x974e, 0x975a, 'bf38d583ed3d968eb29ed6ec954f18d7c5c6c5c94f07b871d203bdbda6063333'),
    (0x12c9e, 0x12cae, '971040adb5e332bb1722fb274cb26dbf5b6d402891d7fc0407ee90f18d7ae1de'),
    (0x2639a, 0x263a0, 'ba559afb3cddf9a7a43ee9e236ce20c17456e969a57c72a93ef7bf3f6d20fbfc'),
    (0x26abc, 0x26ac0, 'cfc4959a72f2784595ed1bfa65612a0fdc2966ab3dbd24318f13a22dfce67f8d'),
    (0x3bbd0, 0x3bbd4, 'fa8ecf96d6d5b535bdd6283fabba73ea930d1ba40489269a69f9315fb79c7c74'),
    (0x3bde4, 0x3be04, '1076627f55e605eca63960b7a423cb7be2e0b7dfe36547311c5dfe7f0b55d09a'),
    (0x3bb24, 0x3bb86, '87c56f687a40efe966b9e716a7d3a27558a256fe19862fa0a999dabc407c4e91'),
    (0x3ba5a, 0x3ba5c, '559a548aa93c6aa088d3a0b13cc493a17443d28e22410942a42fb9dc8755c077'),
    (0x3bbd8, 0x3bbdc, 'd54b557e5675e2987978bd8f7b153653999fb01d5bd6c4fd2f340cdc929c0ccd'),
    (0x3bbe8, 0x3bbec, 'f625a609f83a83b85985f13c75d420ecaa437394300d7587cdb1caf4bac7a090'),
    (0x8d92, 0x8d93, '594e519ae499312b29433b7dd8a97ff068defcba9755b6d5d00e84c524d67b06'),
)


def verify_limit(data):
    for start, end, expected in SPANS:
        assert hashlib.sha256(data[start:end]).hexdigest() == expected, f'{start:08x}'

    def word(address, size=2):
        return int.from_bytes(data[address:address + size], 'big')

    def instruction(address):
        return sh2.decode(word(address), address)

    assert word(0x2639a) == 240 and word(0x2639c, 4) == 0x26a84
    assert instruction(0x2638a).value == ('extu', 8, 5)
    assert instruction(0x26398).access == sh2.Access(4, 15, 1, 'load')
    assert [word(address) for address in range(0x26a84, 0x26a94, 2)] == [0x4501, 0x4325]*4
    assert word(0x26abc, 4) == 0x26740
    assert instruction(0x26aa0).access == sh2.Access(4, 0, 2, 'load')
    assert instruction(0x26aaa).dest == 4 and instruction(0x26aaa).value == ('add', 5)
    assert instruction(0x26aac).access == sh2.Access(4, 0, 1, 'load')
    assert word(0x3bbd0, 4)+1 == 0xffff2449
    assert instruction(0x3bb88).access == sh2.Access(6, 1, 1, 'load')
    assert word(0x3bb8a) == 0xc880 and instruction(0x3bb8c).target == 0x3bc16
    assert instruction(0x3bb92).access == sh2.Access('gbr', 2, 2, 'load')
    assert instruction(0x3bbb0).access == sh2.Access('gbr', 0, 2, 'load')
    assert word(0x3bb94) == word(0x3bbec) == 0x677f
    assert instruction(0x3bbfe).flow == 'call' and instruction(0x3bbfe).delayed
    assert instruction(0x3bc00).value == ('extu', 8, 6)
    assert word(0x3bde8, 4) == 0x12c9e and word(0x3bdec, 4) == 0x26388
    assert instruction(0x3bc04).access == sh2.Access('gbr', 0x5a, 1, 'store')
    assert word(0x3bc06) == 0x4218 and word(0x3bc08) == 0x3e26
    assert word(0x3bdf8, 4) == 0x974e
    assert instruction(0x3bc1c).access == sh2.Access(7, 0, 1, 'load', indexed=True)
    assert instruction(0x3bc44).access == sh2.Access(4, 3, 1, 'load')
    assert word(0x3bdf4, 4)+3 == 0xffff1075
    assert instruction(0x3bc7e).access == sh2.Access(9, 2, 2, 'store')
    assert word(0x3bdf0, 4)+2 == 0xffff1026
    assert word(0x3ba5a) == 0xdd5f and word(0x3bbd8, 4) == 0x8d92
    assert data[0x8d92] == 0x7a and word(0x3bb3e) == 0xc910
    assert word(0x3bbe8, 4)+0x18 == 0xffff1060
    assert word(0x3bb32) == 0x6763 and word(0x3bb36) == 0xe700


def test_bfs_limit_signed_correction_byte_interpolation_diagnostic_bypass_and_word_store_match_stock():
    verify_limit(derive.image_bytes(repo.layout('7mfk')))


@pytest.mark.parametrize('address', byte_span_samples(SPANS), ids=byte_span_ids(SPANS))
def test_changed_bfs_limit_mode_signedness_curve_cell_fraction_cap_bypass_or_store_fails(address, jk08a_stock_bytes):
    data = bytearray(jk08a_stock_bytes)
    data[address] ^= 1
    with pytest.raises(AssertionError):
        verify_limit(data)


def test_bfs_limit_keeps_working_source_signed_cache_endpoint_and_diagnostic_grid_contracts():
    model = compile.cached(repo.ROOT)
    chain = model.entities[('chain', 'airflow_load')]
    formula = ('u = uint8(ffff11eb); i = min(14,floor(u/16)); f = min(16,u-16*i); '
               'a = ROM8[0x00012c9e+i]; b = ROM8[0x00012c9e+i+1]; '
               'c = a+floor(max(0,b-a)*f/16)-floor(max(0,a-b)*f/16); ffff1e46 = c; '
               'candidate = max(0,uint16(ffff1dec)+int16(ffff1060)); '
               'ffff1026 = min(candidate,c*256)')
    assert chain.steps[24]['note'] == formula
    assert [ref.address for ref in chain.steps[24]['via']] == [0x3b75c]
    for address, width, signed in ((0xffff1e46,8,False),(0xffff1dee,16,False),
                                   (0xffff1dec,16,False),(0xffff1060,16,True),
                                   (0xffff11eb,8,False),(0xffff2449,8,False)):
        symbol = model.symbols[SymbolKey('7mfk', 'ram', address)]
        assert symbol.value('width') == width and symbol.value('signed') is signed
    cap = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff1e46))
    assert model.symbols[SymbolKey('7mfk', 'ram', 0xffff1e46)].value('level') == 'code'
    assert cap.key == 'bfs_upper_limit_raw/ram'
    assert cap.props['block'] == 'airflow_load/block'
    assert 'preserves' in cap.props['summary']
    mode = model.symbols[SymbolKey('7mfk', 'tbl', 0x8d92)]
    assert mode.value('level') == 'code'
    assert mode.meaning.key == 'bfs_mode_flags/tbl'
    assert mode.value('images') == ['JK08A']
    assert mode.meaning.props['access'] == 'direct-scalar'
    assert mode.meaning.props['storage'] == 'uint8'
    assert any('JK00A' in note and '0x7e' in note for note in mode.meaning.props['note'])
    output = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff1026))
    assert {link.to.key for link in output.links if link.type == 'input'} == {
        'wise-squirrel/ram', 'elite-dormouse/ram', 'magenta-anaconda/ram',
    }
    selectors = [link for link in output.links if link.type == 'selector']
    assert {(link.to.key, link.slot) for link in selectors} == {
        ('slick-bullfinch/ram','bit7'), ('bfs_mode_flags/tbl','bit4'),
    }
    assert any('coherent correction cache/RAM' in link.props['note']
               for link in output.links if link.type == 'input')
    curve = model.meaning_of(SymbolKey('7mfk', 'tbl', 0x12c9e))
    assert '16-point unsigned byte' in curve.props['summary']
    assert 'Direction' in curve.props['summary']
    assert curve.props['scale_level'] == 'candidate'
    grid = model.meaning_of(SymbolKey('7mfk', 'tbl', 0x974e))
    assert {link.to.key for link in grid.links if link.type == 'index'} == {
        'angelic-shark/ram', 'absolute_throttle/ram',
    }
    throttle = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff1075))
    assert throttle.key == 'absolute_throttle/ram' and throttle.props['unit'] == 'percent'
    producer = model.meaning_of(SymbolKey('7mfk', 'fn', 0x3b75c))
    assert any(link.type == 'reader' and link.to is producer for link in throttle.links)
    thresholds = [link for link in producer.links if link.type == 'threshold'
                  and link.to in (curve,grid)]
    assert len(thresholds) == 2
    for link in (*selectors,*thresholds):
        assert link.stated == {'7mfk'}
        assert any(evidence.get('kind') == 'test' for evidence in link.evidence)
