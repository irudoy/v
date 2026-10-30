"""Bind target raw-threshold role homology to exact stock operands and owners.

Static checks preserve target execution, full arithmetic/ABI equivalence,
engineering scale and physical channel identity as unestablished claims.
"""

from copy import copy, deepcopy
from dataclasses import replace
import hashlib
import re

import pytest

from kb import compile, derive, repo, sh2
from kb.model import SymbolKey


THIS_TEST = 'tools/kb/tests/test_knock_target_homology.py'
OWNER_TEST = 'test_knock_target_homology_owner_contract'
ROM_TEST = 'test_knock_target_homology_exact_registered_rom_contract'
TABLE = 'knock_slice_threshold/tbl'
HOME = SymbolKey('7mfk', 'tbl', 0x1108e)
TARGET_AXIS = (32, 64, 96, 128, 160, 192, 224, 256,
               288, 320, 352, 384, 416, 464, 504, 544)
HOME_AXIS = tuple(range(32, 513, 32))
TARGET_TABLE_SHA = '5c241044326c80409a97eb5b5cc9cf9ed571b21730cc3ce54367abc6034d2544'
IMAGES = {
    'JK08A': ('7mfk', '23710-JK08A/1JK08A-20260726-stock.bin', 0x100000,
              'ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23', '1JK08A00000'),
    '1ND0A': ('1nd', '23710-1ND0A/11ND0A-20260715-stock.bin', 0x180000,
              '650d3d3d5f1fdefdb310820a990d6e1a49baa1e072e51ee0019c0b69fd6da978', '11ND0A00000'),
    '1ND3B': ('1nd', '23710-1ND3B/11ND3B-20260715-stock.bin', 0x180000,
              '0e428cff9e601db74b380ae2e05d3c4ec0ff31313eb7d70aa3badd49a232ec7e', '11ND3B00000'),
    '1ME3B': ('1me3b', '23710-1ME3B/11ME3B-20260825-stock.bin', 0x180000,
              'f905b78901b4ca96002a31c2fca8f1cd00dee57b02bea1921a341caa6db2a6f3', '11ME3B00000'),
}
CONTRACTS = {
    '7mfk': dict(table=0x1108e, axis=0x15340, mode=0x8b3d, mode_value=0x82,
                 code=(0x49ffc, 0x4a04a, 'e32b801d6090a980735d7fbc8767b3930b6ef69bcb0bdcd0e3187c661fed5225'),
                 pools=(0x4a1fc, 0x4a218, 'd2903e51955ccf1a9fbf6a3a6350c188eb868518005b750867d7be548c7a68ad'),
                 table_sha='9a02dafbc2c70c55005cd7dde3f169314d6f2516e1140f944dbbe7dd466bb7f6',
                 loads=((0x4a000, 6, 0x4a1fc, 0x8b3d),
                        (0x4a00a, 2, 0x4a200, 0xffff1ff4),
                        (0x4a014, 4, 0x4a204, 0x1108e),
                        (0x4a01a, 6, 0x4a208, 0xffff11d4),
                        (0x4a020, 5, 0x4a20c, 0x15340),
                        (0x4a02a, 2, 0x4a210, 0x264f8),
                        (0x4a030, 5, 0x4a214, 0xffff2144)),
                 call=0x4a02c, call_register=2, delay=0x667d, coordinate_load=0x4a024,
                 coordinate_base=6, output_store=0x4a03a, output_base=5,
                 caller_call=0x4a2ee),
    '1nd': dict(table=0x122c8, axis=0x16bc2, mode=0x8a2b, mode_value=0xba,
                code=(0x6e854, 0x6e8a0, '35767de52abdedb6d70f2391fda1026e60b897a482228a11d46eea9672dca2f6'),
                pools=(0x6ea8c, 0x6eaa8, '30770d929c7c9a28a62aa46878744bace087ec132a0882063712d7d96c9e4d7d'),
                table_sha=TARGET_TABLE_SHA,
                loads=((0x6e858, 6, 0x6ea8c, 0x8a2b),
                       (0x6e862, 6, 0x6ea90, 0xfffe8fdc),
                       (0x6e86c, 1, 0x6ea94, 0xfffe81cc),
                       (0x6e87e, 4, 0x6ea98, 0x122c8),
                       (0x6e884, 5, 0x6ea9c, 0x16bc2),
                       (0x6e888, 7, 0x6eaa0, 0x2893c),
                       (0x6e894, 2, 0x6eaa4, 0xfffe9138)),
                call=0x6e88c, call_register=7, delay=0x666d, coordinate_load=0x6e882,
                coordinate_base=1, output_store=0x6e89e, output_base=2,
                caller_call=0x6ed2a, caller=0x6ea18, cmp=0x6ed64,
                coordinate=0xfffe81ee, output=0xfffe9138),
    '1me3b': dict(table=0x11dfc, axis=0x16c46, mode=0x8a7c, mode_value=0xba,
                  code=(0x7275c, 0x727a8, 'f4c9d31b1a7b572d89318ab5bf4abdd71f965eda775a2e7ddb467fab42923dfa'),
                  pools=(0x72994, 0x729b0, '308a65fbefaddce6f556799e7470207a2745d0c2ceb0c814e81c7192bd38cee2'),
                  table_sha=TARGET_TABLE_SHA,
                  loads=((0x72760, 6, 0x72994, 0x8a7c),
                         (0x7276a, 6, 0x72998, 0xfffe8f98),
                         (0x72774, 1, 0x7299c, 0xfffe81b4),
                         (0x72786, 4, 0x729a0, 0x11dfc),
                         (0x7278c, 5, 0x729a4, 0x16c46),
                         (0x72790, 7, 0x729a8, 0x2af88),
                         (0x7279c, 2, 0x729ac, 0xfffe9100)),
                  call=0x72794, call_register=7, delay=0x666d, coordinate_load=0x7278a,
                  coordinate_base=1, output_store=0x727a6, output_base=2,
                  caller_call=0x72c32, caller=0x72920, cmp=0x72c6c,
                  coordinate=0xfffe81d6, output=0xfffe9100),
}
COMPARISONS = {
    '1nd': ((0x6ed4a, 8, 0x6ed98, 0xfffe91cc),
            (0x6ed52, 2, 0x6ed9c, 0xfffe9138),
            (0x6ed68, 0, 0x6eda4, 0xfffe94de),
            0x6ed50, 0x6ed58, 0x6ed5a, 0x6ed6e, 0x6eda8),
    '1me3b': ((0x72c52, 8, 0x72ca0, 0xfffe9194),
              (0x72c5a, 2, 0x72ca4, 0xfffe9100),
              (0x72c70, 0, 0x72cac, 0xfffe94af),
              0x72c58, 0x72c60, 0x72c62, 0x72c76, 0x72cb0),
}


def _word(data, address, size=2):
    assert 0 <= address <= len(data)-size
    return int.from_bytes(data[address:address+size], 'big')


def _movl(data, pc, register, pool, operand):
    opcode = _word(data, pc)
    assert opcode >> 12 == 0xd and (opcode >> 8) & 15 == register
    assert ((pc+4) & ~3) + 4*(opcode & 255) == pool
    assert sh2.decode(opcode, pc).value == ('pool', pool, 4)
    assert _word(data, pool, 4) == operand


def _image_identity(data, rom):
    _, _, size, digest, calibration_id = IMAGES[rom]
    assert len(data) == size and hashlib.sha256(data).hexdigest() == digest
    assert data[0x8204:0x820f] == calibration_id.encode('ascii')


@pytest.fixture(scope='module')
def stock_images():
    catalog = repo.images()
    assert set(repo.layout('1nd').images) == {'1ND0A', '1ND3B'}
    assert repo.layout('1me3b').images == ('1ME3B',)
    images = {}
    for rom, (layout_id, path, _, digest, _) in IMAGES.items():
        layout = repo.layout(layout_id)
        assert rom in layout.images
        assert catalog[rom].path == repo.ROOT / 'rom-images' / path
        assert catalog[rom].sha256 == digest
        images[rom] = derive.image_bytes(replace(layout, image=rom))
        _image_identity(images[rom], rom)
    return images


def verify_target_rom_role(data, layout):
    """Static operand/width/shape contract; no guest execution or host model."""
    contract = CONTRACTS[layout]
    for start, end, digest in (contract['code'], contract['pools']):
        assert hashlib.sha256(data[start:end]).hexdigest() == digest
    for load in contract['loads']:
        _movl(data, *load)
    assert data[contract['mode']] == contract['mode_value']
    knots = tuple(_word(data, contract['axis']+2*i) for i in range(16))
    assert knots == (HOME_AXIS if layout == '7mfk' else TARGET_AXIS)
    table = contract['table']
    assert hashlib.sha256(data[table:table+192]).hexdigest() == contract['table_sha']
    assert _word(data, table+192) == 0
    start, end, _ = contract['code']
    calls = [pc for pc in range(start, end, 2)
             if sh2.decode(_word(data, pc), pc).flow == 'call']
    assert calls == [contract['call']]
    assert _word(data, contract['call']) == 0x400b | contract['call_register'] << 8
    assert _word(data, contract['call']+2) == contract['delay']
    assert sh2.decode(_word(data, contract['coordinate_load']), contract['coordinate_load']).access == (
        sh2.Access(contract['coordinate_base'], 0, 2, 'load', True))
    assert sh2.decode(_word(data, contract['output_store']), contract['output_store']).access == (
        sh2.Access(contract['output_base'], 0, 2, 'store', True))
    caller_pc = contract['caller_call']
    caller_call = sh2.decode(_word(data, caller_pc), caller_pc)
    assert caller_call.flow == 'call' and caller_call.delayed and caller_call.target == start
    assert _word(data, caller_pc+2) == 0x0009
    if layout in COMPARISONS:
        metric_pool, threshold_pool, status_pool, metric_pc, threshold_pc, bias_pc, clear_pc, set_pc = COMPARISONS[layout]
        for load in (metric_pool, threshold_pool, status_pool):
            _movl(data, *load)
        assert sh2.decode(_word(data, metric_pc), metric_pc).access == sh2.Access(8, 0, 4, 'load', True)
        assert sh2.decode(_word(data, threshold_pc), threshold_pc).access == sh2.Access(2, 0, 2, 'load', True)
        assert [_word(data, pc) for pc in range(bias_pc, bias_pc+12, 2)] == [
            0xe780, 0x4718, 0x699d, 0x4728, 0x397c, 0x3596]
        assert _word(data, clear_pc) == 0xcdef and _word(data, set_pc) == 0xcf10
    if layout == '1me3b':
        # Bind the documented implementation difference without asserting a
        # rounding theorem, executed target result or full FPU-state contract.
        assert hashlib.sha256(data[0x2af88:0x2b0d2]).hexdigest() == (
            '9eb0acccad16f1473290b843f9d24bd82f2587623ae87cbe5955331060a59490')
        assert _word(data, 0x2b088) == 0xf103  # FDIV FR0,FR1
        assert _word(data, 0x2b0a8) == _word(data, 0x2b0be) == 0xf13d  # FTRC FR1,FPUL
        assert _word(data, 0x2b0ce) == 0x000b and _word(data, 0x2b0d0) == 0x6041


def test_knock_target_homology_exact_registered_rom_contract(stock_images):
    for rom, data in stock_images.items():
        _image_identity(data, rom)
        verify_target_rom_role(data, IMAGES[rom][0])
    assert stock_images['1ND0A'][0x122c8:0x12388] == stock_images['1ND3B'][0x122c8:0x12388]
    assert stock_images['1ND0A'][0x122c8:0x12388] == stock_images['1ME3B'][0x11dfc:0x11ebc]
    assert TARGET_AXIS[:13] == HOME_AXIS[:13] and TARGET_AXIS[13:] != HOME_AXIS[13:]


def _owner_contract(symbol, layout):
    contract = CONTRACTS[layout]
    assert symbol.key == SymbolKey(layout, 'tbl', contract['table'])
    assert symbol.meaning.key == TABLE
    assert (symbol.value('access'), symbol.value('storage'), symbol.value('cols'), symbol.value('rows')) == (
        'direct-row-major', 'uint16', 16, 6)
    [item] = [e for e in symbol.evidence if e['kind'] == 'l0' and e.get('supports') == 'homology']
    table_load = contract['loads'][3]
    assert item['at'] == f'{layout}:{table_load[0]:08x}'
    assert item['to'] == '7mfk:0001108e'
    note = ' '.join(item['note'].split())
    for address in (contract['table'], table_load[0], table_load[2], contract['code'][0],
                    contract['axis'], contract['coordinate'], contract['output'], contract['caller'], contract['cmp']):
        assert f'{address:08x}' in note
    for phrase in ('32*(c-1)', '2*(c-1)', 'unsigned word axis', 'raw word', 'ordinal 0 of 1',
                   'uint32 metric', '0x80000000 + uint16(threshold)', 'strict CMP/HI',
                   'raw threshold-role homology', '7mfk:0001108e', '464,504,544'):
        assert phrase in note
    assert 'torque' not in note.lower()
    assert not re.search(r'\bequivalent\b', note.lower())
    assert note.endswith('Target execution, full arithmetic and ABI equivalence, engineering scale and physical channel identity remain unestablished.')
    if layout == '1nd':
        assert all(rom in note for rom in ('1ND0A', '1ND3B'))
        assert '448,480,512' in note
    else:
        assert '1ME3B' in note and 'FLOAT/FMUL/FDIV/FTRC' in note
        assert 'sign-extended zero-fraction return' in note
    assert {(THIS_TEST, OWNER_TEST), (THIS_TEST, ROM_TEST)} <= {
        (e.get('path'), e.get('key')) for e in symbol.evidence if e['kind'] == 'test'}


def test_knock_target_homology_owner_contract():
    model = compile.cached(repo.ROOT)
    owner = model.meaning_of(HOME)
    assert owner.key == TABLE
    assert owner.symbols['7mfk'].key == HOME
    for layout in ('1nd', '1me3b'):
        _owner_contract(owner.symbols[layout], layout)


@pytest.mark.parametrize('rom,pc,replacement', (
    ('1ND0A', 0x6ea98, '000122e8'), ('1ND3B', 0x6ea98, '000122e8'),
    ('1ME3B', 0x729a0, '00011e1c'),
    ('1ND0A', 0x6ea9c, '00016bc4'), ('1ME3B', 0x729a4, '00016c48'),
    ('1ND0A', 0x6e87e, 'd57e'), ('1ME3B', 0x72786, 'd47d'),
    ('1ND0A', 0x6eaa0, '00028b84'), ('1ME3B', 0x729a8, '0002893c'),
    ('1ND0A', 0x6e880, '4200'), ('1ME3B', 0x72788, '4200'),
    ('1ND0A', 0x6e88c, '460b'), ('1ME3B', 0x72794, '460b'),
    ('1ND0A', 0x6e88e, '666f'), ('1ME3B', 0x72796, '666f'),
    ('1ND0A', 0x6e89e, '0214'), ('1ME3B', 0x727a6, '0214'),
    ('1ND0A', 0x8a2b, 'b2'), ('1ME3B', 0x8a7c, 'b2'),
    ('1ND0A', 0x16bdc, '01c0'), ('1ME3B', 0x16c60, '01c0'),
    ('1ND0A', 0x122ca, '0381'), ('1ME3B', 0x11dfe, '0381'),
    ('1ND0A', 0x6ed50, '058d'), ('1ME3B', 0x72c58, '058d'),
    ('1ND0A', 0x6ed58, '092c'), ('1ME3B', 0x72c60, '092c'),
    ('1ND0A', 0x6ed5e, '699f'), ('1ME3B', 0x72c66, '699f'),
    ('1ND0A', 0x6ed64, '3592'), ('1ME3B', 0x72c6c, '3597'),
    ('1ND0A', 0x6ed6e, 'cdbf'), ('1ME3B', 0x72cb0, 'cf40'),
    ('1ND0A', 0x6ed2a, '0009'), ('1ME3B', 0x72c32, '0009'),
    ('1ME3B', 0x2b088, 'f102'), ('1ME3B', 0x2b0a8, 'f12d'),
    ('1ME3B', 0x2b0d0, '6040'),
))
def test_knock_target_homology_refuses_operand_width_axis_and_role_mutations(stock_images, rom, pc, replacement):
    data = bytearray(stock_images[rom])
    replacement = bytes.fromhex(replacement)
    assert data[pc:pc+len(replacement)] != replacement
    data[pc:pc+len(replacement)] = replacement
    with pytest.raises(AssertionError):
        verify_target_rom_role(data, IMAGES[rom][0])


@pytest.mark.parametrize('rom', IMAGES)
def test_knock_target_homology_refuses_changed_complete_image_identity(stock_images, rom):
    data = bytearray(stock_images[rom])
    data[-1] ^= 1
    with pytest.raises(AssertionError):
        _image_identity(data, rom)


@pytest.mark.parametrize('layout,field,value', (
    ('1nd', 'at', '1nd:0006e884'), ('1me3b', 'at', '1me3b:0007278c'),
    ('1nd', 'to', '7mfk:0000a4aa'), ('1me3b', 'to', '7mfk:0000a4aa'),
    ('1nd', 'note', 'The accessor loads the second torque surface.'),
    ('1me3b', 'note', 'The target is equivalent to the executed JK08A lookup.'),
    ('1nd', 'note', 'The interpolation call is ordinal 8 of 11.'),
    ('1me3b', 'note', 'Target execution and physical channel identity are established.'),
))
def test_knock_target_homology_refuses_owner_binding_or_scope_mutations(layout, field, value):
    symbol = copy(compile.cached(repo.ROOT).meaning_of(HOME).symbols[layout])
    symbol.evidence = deepcopy(symbol.evidence)
    _owner_contract(symbol, layout)
    [item] = [e for e in symbol.evidence if e['kind'] == 'l0' and e.get('supports') == 'homology']
    item[field] = value
    with pytest.raises(AssertionError):
        _owner_contract(symbol, layout)


@pytest.mark.slow
@pytest.mark.parametrize('layout', ('1nd', '1me3b'))
def test_knock_target_homology_refuses_wrong_owner_table_address(layout):
    symbol = copy(compile.cached(repo.ROOT).meaning_of(HOME).symbols[layout])
    symbol.evidence = deepcopy(symbol.evidence)
    _owner_contract(symbol, layout)
    symbol.key = replace(symbol.key, address=symbol.address+32)
    with pytest.raises(AssertionError):
        _owner_contract(symbol, layout)
