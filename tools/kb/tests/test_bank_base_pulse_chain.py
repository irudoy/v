"""Bind the complete bank base-pulse publication to unsigned machine arithmetic."""

from collections import Counter
from dataclasses import replace
import hashlib
import importlib.util
from math import floor
import re
import sys

import pytest

from kb import compile, derive, repo, sh2
from kb.arithmetic import Grammar
from kb.model import SymbolKey


KEY = 'jk08a-bank-base-pulse'
SOURCE = 'stock_jk08a_bank_base_pulse.s'
HARNESS = 'harness-stock-jk08a-bank-base-pulse.c'
HEADER = 'stock-jk08a-bank-base-pulse-cases.h'
SPEC = 'defs/JK08A.fuel.md'
SECTION = 'Bounded bank base-pulse builder'
THIS_TEST = 'tools/kb/tests/test_bank_base_pulse_chain.py'
OWNER_TEST = 'test_bank_base_pulse_chain_owner_contract'
STOCK_TEST = 'test_bank_base_pulse_registered_stock_contract'
FUNCTION = SymbolKey('7mfk', 'fn', 0x4ead4)
FN = 'bank_base_pulse_builder/fn'
FORMULA = (
    'B = uint8(x); S = RAM16[ffff22dc+2*B]; L = RAM16[ffff2302+2*B]; '
    'E = RAM16[ffff2a24+2*B]; I = RAM16[ffff18c0+2*B]; A = RAM16[ffff2436]; '
    'O = RAM16[ffff2310+2*B]; F = (ROM8[0000893d]>>1)&1; '
    'J = (ROM8[00008940]>>4)&1; C = (1-J)*RAM16[ffff22e6]+J*RAM16[ffff22e8]; '
    'G = max(F,1-min(1,max(0,C-16384))); '
    'T = max(0,S+G*L+E-25600*(1+G)); P = uint32(I*T); '
    'V = A+floor(P/65536); Z = min(1,I); '
    'R = (1-Z)*V+Z*floor(uint32(256*V+O-32768)/256); to = min(65535,R)'
)
CODE_SPANS = ((0x4ead4, 0x4eba2),)
POOLS = ((0x893d, 1), (0x8940, 1), (0x4ebe2, 2), (0x4ebe4, 2),
         (0x4ec00, 4), (0x4ec04, 4), (0x4ec08, 4), (0x4ec18, 4), (0x4ec1c, 4))
RAM_LITERALS = (0x4ec00, 0x4ec04, 0x4ec08)
SPANS = (
    (0x4ead4, 0x4eba2, 'cb10fc1d73193f47f1bbd8e31da96a145b20fdeaee5f26e2f608ca7dfc28c9c5'),
    (0x893d, 0x893e, '4ae81572f06e1b88fd5ced7a1a000945432e83e1551e6f721ee9c00b8cc33260'),
    (0x8940, 0x8941, '4bf5122f344554c53bde2ebb8cd2b7e3d1600ad631c385a5d7cce23c7785459a'),
    (0x4ebe2, 0x4ebe4, '7c780e8d1180b5c258bdc08506855bca08c111a40cb4b38313b153a712504948'),
    (0x4ebe4, 0x4ebe6, 'b54d7f43052bd9abe02ed4947f9c2c22cf2de16b1e20b5539b891dbfaea26571'),
    (0x4ec00, 0x4ec04, 'ec8b3d982688af3847d88f663cfe6eac173f3edd5f43b1d739baec8531c51f67'),
    (0x4ec04, 0x4ec08, '4f7e96f2f3d19407e474f2d34b2db605ff768abffb7f78d34e14dae07a06b8b1'),
    (0x4ec08, 0x4ec0c, 'fe13ff4ca9550784a11feef52d84223ffe77c4f9590e2681ea033aae144c3181'),
    (0x4ec18, 0x4ec1c, 'd87cf055b980ec229606186c4f0c5606397561cb7afef0f8bbcaf35df9e5b47c'),
    (0x4ec1c, 0x4ec20, 'e279a9c7501ed95961fdd703f9bdd6141f1930ea8e901555dfb6dd91f026b4d0'),
)
OWNERS = (
    ('stft_b1/ram', 0xffff22dc), ('stft_b2/ram', 0xffff22de),
    ('ltft_b1/ram', 0xffff2302), ('ltft_b2/ram', 0xffff2304),
    ('astonishing-hoatzin/ram', 0xffff2a24), ('illustrious-peccary/ram', 0xffff2a26),
    ('dainty-oriole/ram', 0xffff18c0), ('famous-grouse/ram', 0xffff18c2),
    ('portable-kingfisher/ram', 0xffff2436), ('provocative-cat/ram', 0xffff2310),
    ('axiomatic-squirrel/ram', 0xffff2312), ('dazzling-sawfly/ram', 0xffff22e6),
    ('af_state_factor/ram', 0xffff22e8), ('enlightened-mastodon/ram', 0xffff191c),
    ('able-cougar/ram', 0xffff191e), ('bipedal-tortoise/ram', 0xffff28f8),
    ('outstanding-marmot/ram', 0xffff128c),
)
SYMBOLS = {
    'STFT': 'stft_b1/ram', 'LTFT': 'ltft_b1/ram',
    'EXTRA': 'astonishing-hoatzin/ram', 'PRECURSOR': 'dainty-oriole/ram',
    'ADDITIVE': 'portable-kingfisher/ram', 'OFFSET': 'provocative-cat/ram',
    'CONTROL0': 'dazzling-sawfly/ram', 'CONTROL1': 'af_state_factor/ram',
    'OUTPUT': 'enlightened-mastodon/ram', 'LTFT_CONFIG': 'bank_base_ltft_config/tbl',
    'CONTROL_CONFIG': 'bank_base_control_config/tbl',
}
READER_ROLES = (
    ('stft_b1/ram', 'b=0: S=RAM16[ffff22dc].'),
    ('stft_b2/ram', 'b=1: S=RAM16[ffff22dc+2].'),
    ('ltft_b1/ram', 'b=0: L=RAM16[ffff2302], only when ROM893d.bit1 is set or selected control<=16384.'),
    ('ltft_b2/ram', 'b=1: L=RAM16[ffff2302+2], only when ROM893d.bit1 is set or selected control<=16384.'),
    ('astonishing-hoatzin/ram', 'b=0: E=RAM16[ffff2a24].'),
    ('illustrious-peccary/ram', 'b=1: E=RAM16[ffff2a24+2].'),
    ('dainty-oriole/ram', 'b=0: I=RAM16[ffff18c0]. I=0 bypasses the offset correction completely.'),
    ('famous-grouse/ram', 'b=1: I=RAM16[ffff18c0+2]. I=0 bypasses the offset correction completely.'),
    ('portable-kingfisher/ram', 'Common A=RAM16[ffff2436] adds after the low32 product high-word extraction.'),
    ('provocative-cat/ram', 'b=0 and I!=0: O=RAM16[ffff2310], interpreted only through unsigned uint32(256*V+O-32768). I=0 does not read O.'),
    ('axiomatic-squirrel/ram', 'b=1 and I!=0: O=RAM16[ffff2310+2], interpreted only through unsigned uint32(256*V+O-32768). I=0 does not read O.'),
    ('dazzling-sawfly/ram', 'Only when ROM893d.bit1 is clear and ROM8940.bit4 is clear: selected C=RAM16[ffff22e6]. C<=16384 includes LTFT; C>16384 omits it.'),
    ('af_state_factor/ram', 'Only when ROM893d.bit1 is clear and ROM8940.bit4 is set: selected C=RAM16[ffff22e8]. C<=16384 includes LTFT; C>16384 omits it.'),
)
READER_SCOPE = (
    ' MOV.W/EXTU.W supplies an unsigned16 bounded-consumer context. Both banks, '
    'complete uint16 word boundaries and independent sibling words are executed; '
    'producer signedness, units, acquisition and physical meaning are unchanged.'
)
INPUT_SCOPE = (
    ' This is one view of the same complete output publication, with explicit '
    'full-word arithmetic and wrap. A sign-positive physical domain is not inferred.'
)
LTFT_SELECTOR = (
    'Bit1 set includes L; clear includes L only when the separately selected C<=16384. '
    'LTFT flag does not change bank selection. Complete machine inputs admit '
    'nonmonotone output across low32 product and offset-wrap boundaries.'
)
CONTROL_SELECTOR = (
    'When LTFT flag bit1 is clear, bit4 clear selects unsigned C at ffff22e6 and set '
    'selects ffff22e8. The strict omit condition is C>16384, so equality includes L. '
    'If LTFT flag bit1 is set neither control candidate nor this scalar is read.'
)
CONTROL_THRESHOLD = (
    'With ROM893d.bit1 clear, this candidate controls LTFT inclusion only when '
    'selected by ROM8940.bit4. Unsigned C<=16384 includes L, strictly greater '
    'omits it. The other candidate is independent and preserved.'
)
CAL_READERS = {
    'bank_base_ltft_config/tbl': (
        'The bounded reader loads this raw ROM byte at 0004eaf4 and tests bit1. '
        'Set includes L regardless of control; clear delegates inclusion to the '
        'separately selected unsigned control word. Other readers and unrelated '
        'bits have no inferred role. Generic storage does not prescribe a stock '
        'byte or a physical mode.'),
    'bank_base_control_config/tbl': (
        'Only with LTFT flag bit1 clear, the bounded reader loads this byte '
        'through ROM pointer 893d+3 at 0004eb0c and tests bit4. Clear selects '
        'ffff22e6; set selects ffff22e8. Generic storage does not prescribe '
        'a stock byte, other consumer semantics or a physical mode.'),
}

HELD_LINK_EXPECTATIONS = ((('stft_b1/ram', 'reader', 'bank_base_pulse_builder/fn', None),
  {'reverse_relies': 'structure', 'reverse_supports': 'identity'},
  ('indexed_by',)),
 (('ltft_b1/ram', 'reader', 'bank_base_pulse_builder/fn', None),
  {'reverse_relies': 'structure', 'reverse_supports': 'identity'},
  ('indexed_by',)),
 (('astonishing-hoatzin/ram', 'reader', 'bank_base_pulse_builder/fn', None),
  {'relies': 'structure',
   'supports': 'identity',
   'reverse_relies': 'structure',
   'reverse_supports': 'identity'},
  ('indexed_by',)),
 (('illustrious-peccary/ram', 'reader', 'bank_base_pulse_builder/fn', None),
  {'relies': 'structure',
   'supports': 'identity',
   'reverse_relies': 'structure',
   'reverse_supports': 'identity'},
  ('indexed_by',)),
 (('dainty-oriole/ram', 'reader', 'bank_base_pulse_builder/fn', None),
  {'relies': 'structure',
   'supports': 'identity',
   'reverse_relies': 'structure',
   'reverse_supports': 'identity'},
  ('indexed_by',)),
 (('famous-grouse/ram', 'reader', 'bank_base_pulse_builder/fn', None),
  {'relies': 'structure', 'supports': 'identity'},
  ()),
 (('portable-kingfisher/ram', 'reader', 'bank_base_pulse_builder/fn', None),
  {'relies': 'structure',
   'supports': 'identity',
   'reverse_relies': 'structure',
   'reverse_supports': 'identity'},
  ('indexed_by',)),
 (('provocative-cat/ram', 'reader', 'bank_base_pulse_builder/fn', None),
  {'relies': 'structure',
   'supports': 'identity',
   'reverse_relies': 'structure',
   'reverse_supports': 'identity'},
  ('indexed_by',)),
 (('axiomatic-squirrel/ram', 'reader', 'bank_base_pulse_builder/fn', None),
  {'relies': 'structure', 'supports': 'identity'},
  ()),
 (('dazzling-sawfly/ram', 'reader', 'bank_base_pulse_builder/fn', None),
  {'relies': 'structure',
   'supports': 'identity',
   'reverse_relies': 'structure',
   'reverse_supports': 'identity'},
  ('indexed_by',)),
 (('af_state_factor/ram', 'reader', 'bank_base_pulse_builder/fn', None),
  {'relies': 'structure', 'supports': 'identity'},
  ()),
 (('enlightened-mastodon/ram', 'input', 'stft_b1/ram', None),
  {'relies': 'structure', 'supports': 'identity'},
  ()),
 (('enlightened-mastodon/ram', 'input', 'ltft_b1/ram', None),
  {'relies': 'structure', 'supports': 'identity'},
  ()),
 (('enlightened-mastodon/ram', 'input', 'astonishing-hoatzin/ram', None),
  {'relies': 'structure', 'supports': 'identity'},
  ()),
 (('enlightened-mastodon/ram', 'input', 'dainty-oriole/ram', None),
  {'relies': 'structure', 'supports': 'identity'},
  ()),
 (('enlightened-mastodon/ram', 'input', 'provocative-cat/ram', None),
  {'relies': 'structure', 'supports': 'identity'},
  ()),
 (('enlightened-mastodon/ram', 'input', 'portable-kingfisher/ram', None),
  {'relies': 'structure', 'supports': 'identity'},
  ()),
 (('enlightened-mastodon/ram', 'writer', 'bank_base_pulse_builder/fn', None),
  {'relies': 'structure',
   'supports': 'identity',
   'reverse_relies': 'structure',
   'reverse_supports': 'identity'},
  ()),
 (('able-cougar/ram', 'input', 'stft_b2/ram', None), {'relies': 'structure', 'supports': 'identity'}, ()),
 (('able-cougar/ram', 'input', 'ltft_b2/ram', None), {'relies': 'structure', 'supports': 'identity'}, ()),
 (('able-cougar/ram', 'input', 'illustrious-peccary/ram', None),
  {'relies': 'structure', 'supports': 'identity'},
  ()),
 (('able-cougar/ram', 'input', 'famous-grouse/ram', None),
  {'relies': 'structure', 'supports': 'identity'},
  ()),
 (('able-cougar/ram', 'input', 'axiomatic-squirrel/ram', None),
  {'relies': 'structure', 'supports': 'identity'},
  ()),
 (('able-cougar/ram', 'input', 'portable-kingfisher/ram', None),
  {'relies': 'structure', 'supports': 'identity'},
  ()),
 (('able-cougar/ram', 'writer', 'bank_base_pulse_builder/fn', None),
  {'relies': 'structure',
   'supports': 'identity',
   'reverse_relies': 'structure',
   'reverse_supports': 'identity'},
  ()))


def _verifier():
    name = 'bank_base_pulse_stock_verifier'
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            name, repo.ROOT / 'tools/sh-elf-run/verify_stock_code.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


def _region():
    [region] = [item for item in _verifier().REGIONS if item.key == KEY]
    return region


def _check_region(region):
    assert region.rom == 'JK08A' and (region.source, region.harness) == (SOURCE, HARNESS)
    assert region.code_spans == CODE_SPANS and region.pools == POOLS
    assert region.ram_literals == RAM_LITERALS and region.boundary is False
    assert not region.callees and region.return_address_offset is None and region.base_load is None
    assert not region.bits and not region.constants and region.cases == 6184
    assert tuple(region.symbols) == tuple(SYMBOLS.items())


def _text(value):
    return ' '.join(value.split()) if isinstance(value, str) else ' '.join(value)


def _link(owner, kind, target, slot=None):
    [link] = [item for item in owner.links if item.type == kind
              and item.to.key == target and item.slot == slot]
    return link


def _proof(link):
    assert link.stated == {'7mfk'} and link.props['via'] == [FUNCTION]
    assert (link.props['relies'], link.props['supports']) == ('structure', 'identity')
    assert {(THIS_TEST, OWNER_TEST), (THIS_TEST, STOCK_TEST)} <= {
        (item.get('path'), item.get('key')) for item in link.evidence
        if item['kind'] == 'test'}
    assert (SPEC, SECTION) in {(item.get('path'), item.get('key'))
                             for item in link.evidence if item['kind'] == 'spec'}
    key = (link.owner.key, link.type, link.to.key, link.slot)
    for expected, props, roles in HELD_LINK_EXPECTATIONS:
        if key == expected:
            _check_held_props(link, props, roles)


def _check_held_props(link, props, roles):
    assert all(link.props.get(key) == value for key, value in props.items())
    assert set(roles) <= link.roles


def verify_bank_base_stock(data):
    for start, end, digest in SPANS:
        assert hashlib.sha256(data[start:end]).hexdigest() == digest, f'{start:08x}'
    word = lambda at, size=2: int.from_bytes(data[at:at+size], 'big')
    assert [word(at, 4) for at in (0x4ec00, 0x4ec04, 0x4ec08, 0x4ec18, 0x4ec1c)] == [
        0xffff28f8, 0xffff128c, 0xffff22dc, 0x893d, 0xffff3800]
    assert (word(0x4ebe2), word(0x4ebe4), word(0x893d, 1), word(0x8940, 1)) == (
        0x634, 0x690, 0x51, 1)
    addresses = dict(OWNERS)
    assert word(0x4ec00, 4)+0x12c == addresses['astonishing-hoatzin/ram']
    assert word(0x4ec04, 4)+word(0x4ebe2) == addresses['dainty-oriole/ram']
    assert word(0x4ec04, 4)+word(0x4ebe4) == addresses['enlightened-mastodon/ram']
    assert word(0x4ec08, 4)+0x26 == addresses['ltft_b1/ram']
    assert word(0x4ec08, 4)+0x34 == addresses['provocative-cat/ram']
    assert word(0x4ec08, 4)+0x15a == addresses['portable-kingfisher/ram']
    assert [word(at) for at in (0x4ead4, 0x4ead6, 0x4eb9c, 0x4eb9e, 0x4eba0)] == [
        0x4f12, 0x4f13, 0x4f17, 0x000b, 0x4f16]
    assert [word(at) for at in (0x4eadc, 0x4eaf6, 0x4eb0e, 0x4eb64,
                               0x4eb6a, 0x4eb6c, 0x4eb88, 0x4eb8e, 0x4eb9a)] == [
        0x614c, 0xc802, 0xc810, 0x0647, 0x021a, 0x4229, 0x4519, 0x3526, 0x0725]
    for at in range(0x4ead4, 0x4eba2, 2):
        insn = sh2.decode(word(at), at)
        assert insn.flow != 'call'
        if insn.target is not None and insn.flow in ('branch', 'jump'):
            assert 0x4ead4 <= insn.target < 0x4eba2


def _rows(header):
    [body] = re.findall(r'bank_base_cases\[\]\s*=\s*\{(.*?)\n\};', header, re.S)
    result = []
    for line in body.splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r'\s*\{(0x[0-9a-f]+U),\{([^{}]+)\},([^{}]+)\},', line)
        assert match is not None, 'Every expectation is an explicit independent literal tuple'
        integer = lambda value: int(value.strip().rstrip('U'), 0)
        raw = integer(match[1])
        registers = [integer(item) for item in match[2].split(',')]
        values = [integer(item) for item in match[3].split(',')]
        assert len(registers) == len(values) == 15
        names = ('s', 'l', 'e', 'precursor', 'additive', 'offset', 'c0', 'c1',
                 'output', 'f1', 'f2', 'initial_t', 'variant', 'expected_t', 'group')
        result.append(dict(zip(names, values), raw_r4=raw, expected=registers))
    return result


def _evaluate_formula(row):
    bank = row['raw_r4'] & 255
    ram = {0xffff2436: row['additive'], 0xffff22e6: row['c0'], 0xffff22e8: row['c1']}
    for address, name in ((0xffff22dc, 's'), (0xffff2302, 'l'), (0xffff2a24, 'e'),
                          (0xffff18c0, 'precursor'), (0xffff2310, 'offset')):
        ram[address+2*bank] = row[name]
    env = dict(x=row['raw_r4'], RAM16=ram, ROM8={0x893d: row['f1'], 0x8940: row['f2']},
               uint8=lambda value: int(value) & 255,
               uint32=lambda value: int(value) & 0xffffffff, min=min, max=max, floor=floor)
    assert Grammar(repo.config()).validate(FORMULA) is None
    for assignment in FORMULA.split(';'):
        target, expression = assignment.split('=', 1)
        expression = re.sub(r'\b([0-9a-f]{8})\b', r'0x\1', expression.strip())
        env[target.strip()] = eval(expression, {'__builtins__': {}}, env)
    return env


def _check_rows(literals):
    assert len(literals) == 6184
    for row in literals:
        env = _evaluate_formula(row)
        assert env['B'] in (0, 1) and env['to'] == row['output']
        assert all(0 <= row[name] <= 65535 for name in (
            's', 'l', 'e', 'precursor', 'additive', 'offset', 'c0', 'c1', 'output'))
        assert all(0 <= row[name] <= 255 for name in ('f1', 'f2'))
        expected = [(0x28765430+n*0x01030507+row['variant']*0x00102040) & 0xffffffff
                    for n in range(15)]
        expected[0] = expected[1] = 2*env['B']
        expected[2] = env['to']
        expected[4] = env['T']
        expected[5] = env['R']
        expected[6] = 0x690
        expected[7] = 0x0100191c
        assert row['expected'] == expected
        assert row['expected_t'] == int(env['R'] > 65535)
        assert row['initial_t'] in (0, 1)
        if row['precursor'] == 0:
            assert env['to'] == row['additive'] and row['expected_t'] == 0
    assert Counter(row['raw_r4'] & 255 for row in literals) == {0: 3092, 1: 3092}
    assert Counter(row['initial_t'] for row in literals) == {0: 3092, 1: 3092}
    assert {row['raw_r4'] & 0xffffff00 for row in literals} == {
        0, 0x80000000, 0xa5c30000, 0xffffff00}
    assert {row['expected'][5] for row in literals if row['group'] == 7} >= {65535, 65536, 65537}
    assert {row['f1'] for row in literals if row['group'] == 2} == set(range(256))
    assert {row['f2'] for row in literals if row['group'] == 3} == set(range(256))


def _section(path, title):
    text = (repo.ROOT / path).read_text()
    assert text.count('## '+title+'\n') == 1
    return ' '.join(text.split('## '+title+'\n', 1)[1].split('\n## ', 1)[0].split())


def _published(section, value, noun):
    labels = {'instructions': r'instructions?', 'bytes': r'bytes?',
              'cases': r'(?:cases?|times)'}
    pattern = (r'\b([0-9][0-9,]*)\s*(?:-\s*)?'
               r'(?:(?:stock|bound|literal|executed|registered)\s+)?'+labels[noun]+r'\b')
    found = []
    for match in re.finditer(pattern, section, re.I):
        if noun == 'bytes':
            # Separate frame, pointer and subpool sizes are not total envelope sizes.
            after = section[match.end():].lstrip()
            if re.match(r'(?:(?:observed|stack|local|natural|saved|save|MACL/GBR|GBR/MACL|'
                        r'exit|capture)\s+)*(?:frame|pool|longword|word|pointer|'
                        r'calibration|RAM|output|capture)\b', after, re.I):
                continue
        found.append(int(match[1].replace(',', '')))
    assert found and set(found) == {value}, f'Only {value} {noun} belongs to this contract'


def _remaining_publication(section, count):
    found = [int(value.replace(',', '')) for value in re.findall(
        r'\ball other\s+([0-9][0-9,]*)\s+notes remain intact\b', section, re.I)]
    assert found and set(found) == {count}


def _published_scoped_sizes(section, frame_bytes, pool_bytes, require_pools=False):
    frames = [int(value) for value in re.findall(
        r'\b([0-9]+)\s*(?:-\s*)?byte\s+(?:(?:observed|stack|local)\s+)?frame\b', section, re.I)]
    assert frames and set(frames) == {frame_bytes}
    pools = [int(value) for value in re.findall(
        r'\ball\s+([0-9]+)\s+bound\s+pool/calibration\s+bytes\b', section, re.I)]
    if require_pools or pools:
        assert pools and set(pools) == {pool_bytes}


def _harness_scoped_sizes():
    c = (repo.ROOT / 'tools/sh-elf-run' / HARNESS).read_text()
    [(before, after)] = re.findall(
        r'uint8_t frame_before\[([0-9]+)\],frame_after\[([0-9]+)\];', c)
    assert before == after
    [calibration] = re.findall(r'calibration_before\[([0-9]+)\];', c)
    pool_bytes = sum(size for _, size in _region().pools)
    assert int(calibration) == pool_bytes
    return int(before), pool_bytes


def test_bank_base_exact_stock_complete_natural_return():
    verify_bank_base_stock(derive.image_bytes(repo.layout('7mfk')))
    assert sum((end-start)//2 for start, end in CODE_SPANS) == 103
    assert sum(end-start for start, end, _ in SPANS) == 232


@pytest.mark.parametrize('address', [at for start, end, _ in SPANS for at in range(start, end)])
def test_bank_base_each_stock_byte_corruption_is_rejected(address):
    data = bytearray(derive.image_bytes(repo.layout('7mfk')))
    data[address] ^= 1
    with pytest.raises(AssertionError):
        verify_bank_base_stock(data)


def test_bank_base_all_tracked_literals_match_arithmetic_note_and_gprs():
    header = (repo.ROOT / 'tools/sh-elf-run' / HEADER).read_text()
    _check_rows(_rows(header))


@pytest.mark.parametrize('source', ('s', 'l', 'e', 'precursor', 'additive'))
def test_bank_base_nonmonotone_sign_has_exact_literal_witnesses(source):
    literals = _rows((repo.ROOT / 'tools/sh-elf-run' / HEADER).read_text())
    for bank in (0, 1):
        if source in ('s', 'l', 'e'):
            common = dict(s=65535, l=65535, e=65535, precursor=65535,
                          additive=32768, offset=32768, c0=16384, c1=65535, f1=0x51, f2=1)
            before, after, outputs = 32768, 65534, (65535, 47097)
        elif source == 'precursor':
            common = dict(s=65535, l=0, e=51203, precursor=65534,
                          additive=0, offset=32768, c0=16384, c1=16385, f1=0x51, f2=1)
            before, after, outputs = 65534, 65535, (65535, 0)
        else:
            common = dict(s=0, l=0, e=0, precursor=1,
                          additive=127, offset=0, c0=16384, c1=16385, f1=0x51, f2=1)
            before, after, outputs = 127, 128, (65535, 0)
        for value, output in zip((before, after), outputs):
            expected = {**common, source: value}
            matches = [row for row in literals if row['raw_r4'] & 255 == bank
                       and all(row[key] == item for key, item in expected.items())]
            assert matches and all(row['output'] == output for row in matches)
        assert before < after and outputs[0] > outputs[1]


@pytest.mark.parametrize('noun,value', [('instructions', 103), ('bytes', 232), ('cases', 6184)])
def test_bank_base_conflicting_publication_count_is_rejected(noun, value):
    section = f'{value} {noun}'
    _published(section, value, noun)
    with pytest.raises(AssertionError):
        _published(section+f'; {value+1} {noun}', value, noun)


@pytest.mark.parametrize('path,title', [(SPEC, SECTION),
                                      ('tools/sh-elf-run/README.md', 'Bank base-pulse builder')])
@pytest.mark.parametrize('noun,extra', [
    ('instructions', '104-instruction envelope'),
    ('bytes', '233-byte bound envelope'),
    ('cases', '6185-case literal matrix'),
    ('cases', 'execution repeats 6185 times'),
])
def test_bank_base_hyphenated_and_repeated_count_claims_are_rejected(path, title, noun, extra):
    section = _section(path, title)
    value = {'instructions': 103, 'bytes': 232, 'cases': 6184}[noun]
    _published(section, value, noun)
    with pytest.raises(AssertionError):
        _published(section+'; '+extra, value, noun)


def test_bank_base_frame_and_subpool_counts_are_separate_from_envelope():
    section = '232 bound bytes; 80-byte observed frame; 4-byte pointer; 26-byte calibration pool'
    _published(section, 232, 'bytes')


def test_bank_base_other_note_publication_count_is_derived_and_conflicts_are_rejected():
    model = compile.cached(repo.ROOT)
    total = sum(len(model.entities[('chain', name)].steps)
                for name in ('closed_loop_fuel', 'fuel_pulse'))
    views = {('closed_loop_fuel', number) for number in (16, 17, 18, 19)} | {
        ('fuel_pulse', number) for number in (17, 19)}
    count = total-len(views)
    section = _section(SPEC, SECTION)
    _remaining_publication(section, count)
    with pytest.raises(AssertionError):
        _remaining_publication(section+f'; all other {count+1} notes remain intact', count)


@pytest.mark.parametrize('path,title', [(SPEC, SECTION),
                                      ('tools/sh-elf-run/README.md', 'Bank base-pulse builder')])
@pytest.mark.parametrize('scope', ('frame', 'pools'))
def test_bank_base_conflicting_scoped_publication_size_is_rejected(path, title, scope):
    frame_bytes, pool_bytes = _harness_scoped_sizes()
    section = _section(path, title)
    _published_scoped_sizes(section, frame_bytes, pool_bytes, require_pools=path == SPEC)
    extra = (f'{frame_bytes+1}-byte frame' if scope == 'frame'
             else f'all {pool_bytes+1} bound pool/calibration bytes')
    with pytest.raises(AssertionError):
        _published_scoped_sizes(section+'; '+extra, frame_bytes, pool_bytes, require_pools=path == SPEC)


@pytest.mark.parametrize('mutation', ('role-remove', 'role-change', 'reverse-remove',
                                      'reverse-change', 'supports-change', 'relies-remove'))
def test_bank_base_held_role_and_evidence_levels_mutation_is_rejected(mutation):
    model = compile.cached(repo.ROOT)
    owner = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff2a24))
    link = _link(owner, 'reader', FN)
    [(_, props, roles)] = [item for item in HELD_LINK_EXPECTATIONS
                          if item[0] == (owner.key, 'reader', FN, None)]
    _check_held_props(link, props, roles)
    changed_props, changed_roles = dict(link.props), set(link.roles)
    if mutation == 'role-remove':
        changed_roles.remove('indexed_by')
    elif mutation == 'role-change':
        changed_roles = {'consumer'}
    elif mutation == 'reverse-remove':
        del changed_props['reverse_relies']
    elif mutation == 'reverse-change':
        changed_props['reverse_supports'] = 'structure'
    elif mutation == 'supports-change':
        changed_props['supports'] = 'structure'
    else:
        del changed_props['relies']
    with pytest.raises(AssertionError):
        _check_held_props(replace(link, props=changed_props, roles=changed_roles), props, roles)


@pytest.mark.parametrize('mutation', ('duplicate', 'reorder', 'rom', 'count'))
def test_bank_base_registered_identity_mutation_is_rejected(mutation):
    region = _region()
    _check_region(region)
    changes = {
        'duplicate': {'symbols': (*region.symbols, region.symbols[0])},
        'reorder': {'symbols': tuple(reversed(region.symbols))},
        'rom': {'rom': 'JK00D'},
        'count': {'cases': region.cases+1},
    }
    with pytest.raises(AssertionError):
        _check_region(replace(region, **changes[mutation]))


def _ledger_claim(model, owner, registry, order, dependency):
    name, kind = owner.split('/')
    [markers] = [rows for marker_kind, owner_name, rows, _ in model.stash['ledger_rows']
                 if (marker_kind, owner_name) == (kind, name)]
    [row] = [item for item in markers if (item['registry'], item['order']) == (registry, order)]
    assert dependency in row.get('dependency', [])


def test_bank_base_held_ledger_claiming_ends_remain_selected():
    model = compile.cached(repo.ROOT)
    for owner, order in (('astonishing-hoatzin/ram', 908), ('illustrious-peccary/ram', 909),
                          ('dainty-oriole/ram', 548), ('famous-grouse/ram', 549),
                          ('portable-kingfisher/ram', 376), ('provocative-cat/ram', 561),
                          ('axiomatic-squirrel/ram', 562), ('dazzling-sawfly/ram', 156),
                          ('af_state_factor/ram', 551)):
        _ledger_claim(model, owner, 'vars', order, dict(
            role='consumer', to=FN, type='reader', end='owner',
            relies='structure', supports='identity'))
    for output, order, sources in (
            ('enlightened-mastodon/ram', 363, ('astonishing-hoatzin/ram', 'dainty-oriole/ram',
             'ltft_b1/ram', 'portable-kingfisher/ram', 'provocative-cat/ram', 'stft_b1/ram')),
            ('able-cougar/ram', 364, ('axiomatic-squirrel/ram', 'famous-grouse/ram',
             'illustrious-peccary/ram', 'ltft_b2/ram', 'portable-kingfisher/ram', 'stft_b2/ram'))):
        for source in sources:
            _ledger_claim(model, output, 'vars', order, dict(
                role='indexed_by', to=source, type='input', end='owner',
                relies='structure', supports='identity'))
        _ledger_claim(model, output, 'vars', order, dict(
            role='writes', to=FN, type='writer', end='owner',
            relies='structure', supports='identity'))
        _ledger_claim(model, FN, 'funcs', 366, dict(
            role='writes', to=output, type='writer', end='to',
            relies='structure', supports='identity'))
    for source in ('astonishing-hoatzin/ram', 'dainty-oriole/ram', 'dazzling-sawfly/ram',
                   'illustrious-peccary/ram', 'ltft_b1/ram', 'portable-kingfisher/ram',
                   'provocative-cat/ram', 'stft_b1/ram'):
        _ledger_claim(model, FN, 'funcs', 366, dict(
            role='indexed_by', to=source, type='reader', end='to', link_role='indexed_by',
            relies='structure', supports='identity'))


def test_bank_base_pulse_chain_owner_contract():
    model = compile.cached(repo.ROOT)
    owners = {name: model.meaning_of(SymbolKey('7mfk', 'ram', address))
              for name, address in OWNERS}
    assert all(owner.key == name for name, owner in owners.items())
    assert model.meaning_of(FUNCTION).key == FN
    for name, address in (('bank_base_ltft_config/tbl', 0x893d),
                          ('bank_base_control_config/tbl', 0x8940)):
        owner = model.meaning_of(SymbolKey('7mfk', 'tbl', address))
        symbol = owner.symbols['7mfk']
        assert owner.key == name
        assert (symbol.value('storage'), symbol.value('rows'), symbol.value('cols')) == ('uint8', 1, 1)
        assert symbol.value('block') == 'fuel_quantity/block'
        reader = _link(owner, 'reader', FN)
        _proof(reader)
        assert _text(reader.props['note']) == CAL_READERS[name]
    for name, address in OWNERS[:15]:
        symbol = owners[name].symbols['7mfk']
        assert symbol.address == address and symbol.value('width') == 16
        assert {(THIS_TEST, OWNER_TEST), (THIS_TEST, STOCK_TEST)} <= {
            (item.get('path'), item.get('key')) for item in symbol.evidence
            if item['kind'] == 'test'}
    roles = dict(READER_ROLES)
    for name, role in READER_ROLES:
        reader = _link(owners[name], 'reader', FN)
        _proof(reader)
        assert _text(reader.props['note']) == role+READER_SCOPE
    for bank, output, sources in (
            (0, 'enlightened-mastodon/ram', ('stft_b1/ram', 'ltft_b1/ram',
             'astonishing-hoatzin/ram', 'dainty-oriole/ram', 'provocative-cat/ram')),
            (1, 'able-cougar/ram', ('stft_b2/ram', 'ltft_b2/ram',
             'illustrious-peccary/ram', 'famous-grouse/ram', 'axiomatic-squirrel/ram'))):
        owner = owners[output]
        for source in (*sources, 'portable-kingfisher/ram'):
            link = _link(owner, 'input', source)
            _proof(link)
            assert _text(link.props['note']) == roles[source]+INPUT_SCOPE
        for target, bit, expected in (
                ('bank_base_ltft_config/tbl', 'bit1', LTFT_SELECTOR),
                ('bank_base_control_config/tbl', 'bit4', CONTROL_SELECTOR)):
            link = _link(owner, 'selector', target, bit)
            _proof(link)
            assert _text(link.props['note']) == expected
        for target in ('dazzling-sawfly/ram', 'af_state_factor/ram'):
            link = _link(owner, 'threshold', target)
            _proof(link)
            assert _text(link.props['note']) == CONTROL_THRESHOLD
        writer = _link(owner, 'writer', FN)
        _proof(writer)
        expected = (
            f'Incoming independent full R4 has uint8(x)={bank}; the complete arithmetic '
            'note applies once to the corresponding output at ffff191c+2*b. All six chain '
            'views describe this same publication, not sequential updates. I=0 bypasses '
            'offset correction; I!=0 uses low32 offset arithmetic after low32 product '
            'extraction. Natural return restores MACL/GBR and the exact eight-byte frame. '
            'All remaining RAM and all 26 pool/calibration bytes are preserved per case, '
            'without an upstream producer, scheduling or physical bank claim.')
        assert _text(writer.props['note']) == expected
    for second, first in (('stft_b2/ram', 'stft_b1/ram'), ('ltft_b2/ram', 'ltft_b1/ram'),
                           ('illustrious-peccary/ram', 'astonishing-hoatzin/ram'),
                           ('famous-grouse/ram', 'dainty-oriole/ram'),
                           ('axiomatic-squirrel/ram', 'provocative-cat/ram'),
                           ('able-cougar/ram', 'enlightened-mastodon/ram')):
        base = _link(owners[second], 'base', first)
        _proof(base)
        assert base.offset == 2 and owners[second].symbols['7mfk'].address == (
            owners[first].symbols['7mfk'].address+2)
    for name, count, views in (
            ('closed_loop_fuel', 19, ((16, 'stft_b1/ram', 'multiplies'),
             (17, 'ltft_b1/ram', 'multiplies'), (18, 'astonishing-hoatzin/ram', 'multiplies'),
             (19, 'dainty-oriole/ram', 'multiplies'))),
            ('fuel_pulse', 26, ((17, 'dainty-oriole/ram', 'multiplies'),
             (19, 'portable-kingfisher/ram', 'adds')))):
        chain = model.entities[('chain', name)]
        assert len(chain.steps) == count
        for number, source, effect in views:
            step = chain.steps[number-1]
            assert Grammar(repo.config()).validate(step['note']) is None
            assert re.sub(r'\s+', '', step['note']) == re.sub(r'\s+', '', FORMULA)
            assert (step['from'], step['to'], step['effect'], step['sign'], step['via']) == (
                owners[source].symbols['7mfk'].key, owners['enlightened-mastodon/ram'].symbols['7mfk'].key,
                effect, 'none', [FUNCTION])


def test_bank_base_source_frame_sr_and_preservation_contract():
    directory = repo.ROOT / 'tools/sh-elf-run'
    c = (directory / HARNESS).read_text()
    driver_path = directory / 'stock_bank_base_pulse_invoke.s'
    assert hashlib.sha256(driver_path.read_bytes()).hexdigest() == (
        '06626ef76ea05f7587420aa5fa98bff2dc9d3e9da8751397db429401639a1151')
    assert (directory / 'stock_invoke.s').read_text().count(
        '.include "stock_bank_base_pulse_invoke.s"') == 1
    driver = driver_path.read_text()
    [driver] = re.findall(r'_stock_invoke_bank_base_pulse:\n(.*?)\n\s*\.size\s+'
                          r'_stock_invoke_bank_base_pulse\s*,[^\n]+', driver, re.S)
    for phrase in (
            'uint32_t r[15],gbr,mach,macl,sr;', 'uint32_t exit[20],sp,continuation,abi_before[12],abi_after[12];',
            'uint8_t frame_before[80],frame_after[80];', 'uint32_t sr_before;',
            'out.sr_before&1U', '(out.sr_before&~1U)|test->expected_t',
            'frame_word(out.frame_after,40)!=context.gbr', 'frame_word(out.frame_after,44)!=context.macl',
            '(i<40U || i>=48U)', 'i<65536U', 'if(i>=first && i<first+2U)continue;',
            'memcmp(out.abi_before,out.abi_after', 'memcmp(&context,&before,sizeof(before))',
            'for(i=0;i<15U;++i)', 'reg(&out,i)!=test->expected[i]',
            'out.exit[2]!=context.macl || out.exit[3]!=context.mach || out.exit[4]!=context.gbr',
            'out.sp!=out.abi_before[10]-164U', 'out.exit[1]!=out.continuation',
            'get_word(address)!=test->output', 'calibration_before[26]',
            'frame_word(out.frame_before,72)!=out.continuation',
            'frame_word(out.frame_after,72)!=out.continuation'):
        assert phrase in c
    for phrase in (
            'stc sr,r0\n    mov #-2,r1\n    and r1,r0\n    or r2,r0\n    ldc r0,sr\n    stc sr,r0',
            'add #127,r1\n    add #127,r1\n    add #90,r1\n    mov.l r0,@r1',
            'add #-48,r1\n    mov #20,r0\nL_bank_base_pulse_frame_before:',
            'add #-80,r1\n    mov #20,r4\nL_bank_base_pulse_frame_after:',
            'jsr @r7\n    nop\nL_bank_base_pulse_stock_return:\n    add #112,r15',
            'add #-120,r15', 'mov #112,r0', 'add #4,r0\n    mov.l r4,@(r0,r15)',
            'add #72,r2\n    mov.l @r2,r2', 'mov.l L_bank_base_pulse_return_pointer,r0\n    mov.l r0,@(24,r15)'):
        assert phrase in driver


def test_bank_base_pulse_registered_stock_contract():
    module, region = _verifier(), _region()
    data = derive.image_bytes(repo.layout('7mfk'))
    verify_bank_base_stock(data)
    _check_region(region)
    defines = module.harness_defines(region, data)
    addresses = {**dict(OWNERS), 'bank_base_ltft_config/tbl': 0x893d,
                 'bank_base_control_config/tbl': 0x8940}
    assert all(defines[macro] == addresses[owner] for macro, owner in SYMBOLS.items())
    fixture = module.build_fixture(region, data)
    for start, end in CODE_SPANS:
        assert fixture[start:end] == data[start:end]
    for start, size in POOLS:
        expected = data[start:start+size]
        if start in RAM_LITERALS:
            expected = module.base_verifier.alias_high_ram(int.from_bytes(expected, 'big')).to_bytes(4, 'big')
        assert fixture[start:start+size] == expected
    assert fixture[0x4ec1c:0x4ec20] == bytes.fromhex('ffff3800')
    directory = repo.ROOT / 'tools/sh-elf-run'
    header, harness = ((directory / name).read_text() for name in (HEADER, HARNESS))
    [count] = re.findall(r'^#define BANK_BASE_PULSE_CASE_COUNT ([0-9]+)U$', header, re.M)
    assert int(count) == len(_rows(header)) == region.cases == 6184
    assert hashlib.sha256((directory / HEADER).read_bytes()).hexdigest() == (
        '16605c7b8c3dbf8581bb39c67bc2ac7c8c6390f231f35b3b556e60ad6553b37f')
    assert hashlib.sha256((directory / SOURCE).read_bytes()).hexdigest() == (
        '17882d8baaa037e1e1fd95659e0fcfccef4c8225dc1b0200737b4786750c051f')
    assert not any(re.search(r'^#define\s+'+macro+r'\b', harness, re.M) for macro in SYMBOLS)
    assert 'ARRAY_SIZE(bank_base_cases)' in harness and harness.count('++completed;') == 1
    assert 'completed!=BANK_BASE_PULSE_CASE_COUNT' in harness
    assert harness.count(
        f'VQ_SH_ELF_STOCK_CODE status=PASS region={region.key} cases=%lu\\n') == 1
    assert re.search(r'printf\([^;]+,\s*completed\s*\);', harness)
    instructions = sum((end-start)//2 for start, end in region.code_spans)
    bound = sum(end-start for start, end in region.code_spans)+sum(size for _, size in region.pools)
    assert (instructions, bound, region.cases) == (103, 232, 6184)
    for path, title in ((SPEC, SECTION), ('tools/sh-elf-run/README.md', 'Bank base-pulse builder')):
        section = _section(path, title)
        for value, noun in ((instructions, 'instructions'), (bound, 'bytes'), (region.cases, 'cases')):
            _published(section, value, noun)
        frame_bytes, pool_bytes = _harness_scoped_sizes()
        _published_scoped_sizes(section, frame_bytes, pool_bytes, require_pools=path == SPEC)
        assert re.search(r'\bfull\s+(?:incoming\s+)?R4\b', section, re.I)
        for phrase in ('unsigned16', 'low32', 'offset', 'bypass', 'nonT',
                       'SR', 'GBR', 'MACL', 'SP-48..SP+31', 'ABI'):
            assert phrase in section
