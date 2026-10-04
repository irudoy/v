"""Bind the BFS rate, latch, timers, correction, blend, and sentinel query."""

import hashlib
import importlib.util
import sys

import pytest

from kb import compile, derive, repo, sh2
from kb.model import SymbolKey

SPANS = (
    (0x3bb24, 0x3bb86, '87c56f687a40efe966b9e716a7d3a27558a256fe19862fa0a999dabc407c4e91'),
    (0x3b908, 0x3b98c, '66435f5b1dc2954d1b87da995c731cc1f3697fdb386a9d522e3c91cb113c3501'),
    (0x3b9d8, 0x3bb22, '649c359a62398052ab0bf4b55b853ef74a36b49be9bb3ca0e9a64abb4332091f'),
    (0x224fa, 0x22508, '425d05c23b3b52262420a2b20dd9f3a5475c099e0ccb66737be91ebbbcc2c2c6'),
    (0x259e4, 0x25a12, 'b03a86ac38f4ee7ff4ca4dc2aeb6a05c88c226ffc1d1279f7adf1e259533a300'),
    (0x8319, 0x831b, 'c20cb1d72e69a3e05fa8382577e88b9ee19b270ebe3f79ab28b7ec76e989d506'),
    (0x865a, 0x865b, 'c19a797fa1fd590cd2e5b42d1cf5f246e29b91684e2f87404b81dc345c7a56a0'),
    (0x8d92, 0x8d93, '594e519ae499312b29433b7dd8a97ff068defcba9755b6d5d00e84c524d67b06'),
    (0x25b98, 0x25b9c, '4b9e90bd8b8a501f4cace831f15ee6c421b3a92edcad3f7990ae6ed6ee7fe2f2'),
    (0x3b9d0, 0x3b9d8, '58e09aca4038b6427055d607350dd27b740457700f9b716a68b76f71a4523d72'),
    (0x3bb22, 0x3bb24, 'fc5c2283015b212d975b85e56b2a75aac4b50bd5aba30cbe74f62857c380bd47'),
    (0x3bbc4, 0x3bbec, '2a274e12c352159314027e4471c361daf26c13bcb1833bee77d8b023148d354a'),
    (0x3b8c6, 0x3b8c8, '579b6cc24588e23a1b4dae7da39b218371b5a43ea3715a52b860db3a9c0c9979'),
    (0x3b8da, 0x3b908, 'e14247203e885b1fb1c6891d388f9f6c138d03fb5a6eaac746f5395fb4fb13bb'),
    (0x3b9a0, 0x3b9a4, '232431b0a9268e58e76a6627cabaf5bc422fc7fa256c2d0822881fa45140e41e'),
    (0x3b9cc, 0x3b9d0, '20cd895c4c1549090441989a67c192c8f146c0ce518df06934cea4991f5897e5'),
)


def verify_rate(data):
    for start, end, digest in SPANS:
        assert hashlib.sha256(data[start:end]).hexdigest() == digest, f'{start:08x}'

    def word(address, size=2):
        return int.from_bytes(data[address:address+size], 'big')

    assert [word(a) for a in (0x3b93e, 0x3b940, 0x3b942, 0x3b944, 0x3b946, 0x3b948)] == [
        0x4619, 0x4609, 0x4609, 0x4609, 0xa001, 0x4601]
    assert [word(a) for a in (0x3b976, 0x3b978, 0x3b97a, 0x3b97c, 0x3b97e)] == [
        0x4419, 0x4409, 0x4409, 0x4409, 0x4401]
    assert word(0x3b9a0, 4) == 0xffff2460
    assert word(0x3b9cc, 4) == 0xffff1114
    assert word(0x3b9d0, 4) + 5 == 0xffff24b1
    assert word(0x3b9d4, 4) + 0x1a == 0xffff1062
    assert word(0x3bbdc, 4) == 0x259e4
    assert word(0x3bbe4, 4) == 0x224fa
    assert word(0x25b98, 4) == 0xffff5718
    assert word(0x3ba68) == 0xe4ff
    assert word(0x3b8c6) & 0xff00 == 0xdc00
    assert sh2.decode(word(0x3b8ec), 0x3b8ec).access == sh2.Access(5, 5, 1, 'load')
    assert word(0x3b8f8) == 0x6e0c
    assert word(0x3b902) == 0x655d
    assert [word(a) for a in range(0x224fa, 0x22504, 2)] == [0x4021] * 5
    assert word(0x22504) == 0x000b and word(0x22506) == 0x4021
    assert [data[a] for a in (0x8319, 0x831a, 0x865a, 0x8d92)] == [202, 200, 160, 0x7a]


def test_bfs_rate_sum_difference_latch_timers_correction_blend_and_query_match_stock():
    verify_rate(derive.image_bytes(repo.layout('7mfk')))


@pytest.mark.parametrize('address', [a for start, end, _ in SPANS for a in range(start, end)])
def test_changed_rate_selector_cache_load_timer_signed_helper_query_or_publication_fails(address):
    data = bytearray(derive.image_bytes(repo.layout('7mfk')))
    data[address] ^= 1
    with pytest.raises(AssertionError):
        verify_rate(data)


def test_bfs_rate_owners_conditions_and_arithmetic_keep_exact_raw_scope():
    model = compile.cached(repo.ROOT)
    step = model.entities[('chain', 'airflow_load')].steps[23]
    assert step['effect'] == 'filters' and step['sign'] == 'none'
    assert [ref.address for ref in step['via']] == [0x3b75c]
    assert 'ffff1062' in step['note'] and 'ffff1dee' in step['note']
    assert '>>15' in step['note'] or '/32768' in step['note']
    working = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff1dee))
    assert {(link.to.key, link.slot) for link in working.links if link.type == 'selector'} >= {
        ('bfs_state_flags/ram', 'bit4')}
    assert {link.to.key for link in working.links if link.type == 'input'} >= {
        'tall-quoll/ram', 'fanatic-marten/ram', 'bfs_rate_coefficient/ram', 'flashy-elk/ram'}
    blend = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff1dec))
    assert 'magenta-anaconda/ram' not in {
        link.to.key for link in blend.links if link.type == 'input'}
    assert {(link.to.key, link.slot) for link in blend.links if link.type == 'selector'} >= {
        ('bfs_mode_flags/tbl', 'bit4'), ('burrowing-platypus/ram', 'bit0'),
        ('busy-bird/ram', 'bit2'), ('bfs_state_flags/ram', 'bit7')}
    correction = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff1060))
    assert {(link.to.key, link.slot) for link in correction.links if link.type == 'selector'} >= {
        ('burrowing-platypus/ram', 'bit0'), ('busy-bird/ram', 'bit2'),
        ('bfs_state_flags/ram', 'bit7')}
    third = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff1e4c))
    assert {(link.to.key, link.slot) for link in third.links if link.type == 'selector'} >= {
        ('bfs_mode_flags/tbl', 'bit3'),
        ('diagnostic_record_byte2_fault_predicate/fn', None)}
    for address, width, signed in (
            (0xffff115c, 16, False), (0xffff1f30, 16, False), (0xffff1e06, 16, False),
            (0xffff1e04, 16, False), (0xffff1ee1, 8, False), (0xffff4250, 8, False),
            (0xffff24bd, 8, False), (0xffff1e20, 8, False), (0xffff1e47, 8, False),
            (0xffff1e4c, 8, False), (0xffff244e, 8, False), (0xffff1060, 16, True)):
        symbol = model.symbols[SymbolKey('7mfk', 'ram', address)]
        assert symbol.value('width') == width and symbol.value('signed') is signed
    mode = model.symbols[SymbolKey('7mfk', 'tbl', 0x8d92)]
    assert mode.props['images'] == ['JK08A']
    for name in ('bfs_rate_coefficient/ram', 'bfs_blend_weight/ram',
                 'bfs_rate_timer_first/ram', 'bfs_rate_timer_second/ram',
                 'bfs_rate_timer_third/ram', 'bfs_rate_timer_monitor/ram',
                 'bfs_alpha_latch_set/tbl', 'bfs_alpha_latch_clear/tbl',
                 'bfs_correction_gain/tbl'):
        owner = next(item for item in model.meanings if item.key == name)
        assert owner.props['block'] == 'airflow_load/block'
        assert owner.symbols['7mfk'].value('level') == 'code'


def test_bfs_rate_published_counts_and_simulator_scope_bind_the_executed_region():
    path = repo.ROOT / 'tools/sh-elf-run/verify_stock_code.py'
    spec = importlib.util.spec_from_file_location('bfs_rate_count_verifier', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    region = next(item for item in module.REGIONS if item.key == 'jk08a-bfs-rate')
    instructions = sum((end-start)//2 for start, end in region.code_spans)
    bound = sum(end-start for start, end in region.code_spans) + sum(size for _, size in region.pools)
    section = (repo.ROOT / 'tools/sh-elf-run/README.md').read_text().split('## BFS rate state', 1)[1].split('\n## ', 1)[0]
    section = ' '.join(section.split())
    assert (instructions, bound) == (310, 678)
    assert f'{instructions} instructions' in section and f'{bound} bound bytes' in section
    assert f'{region.cases} cases' in section
    static_bytes = sum(end-start for start, end, _ in SPANS)
    assert static_bytes == 734 and f'{static_bytes} bytes' in section
    fixture = module.build_fixture(region, module.stock_image(region.rom))
    for start, end in region.code_spans:
        assert fixture[start:end] == module.stock_image(region.rom)[start:end]
    assert region.return_address_offset == 24 and region.return_register == 1
    assert module.return_stub(region) == bytes.fromhex('51f6412a000b0009')
    assert 0x25b98 in region.ram_literals
