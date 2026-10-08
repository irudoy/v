"""Bind closed-loop software claims to independent literals and stock bytes."""
import ast
import builtins
from collections import Counter
from dataclasses import asdict
from fractions import Fraction
from functools import cache
import hashlib
from math import floor
import re
import json

from kb import compile, repo
from kb.arithmetic import Grammar
from tools.kb.tests import test_injection_start_delay_chain as publication

TOOL_DIR = repo.ROOT / 'tools/sh-elf-run'
SPEC = 'defs/JK08A.closed-loop-publication.md'
PACKETS = ('stft', 'selection', 'learning')


@cache
def contracts():
    value = json.loads((TOOL_DIR / 'closed-loop-publication-contracts.json').read_text())
    assert value['hardware_ready'] is False
    assert set(value['regions']) == set(PACKETS)
    assert len(value['new_owners']) == 18
    assert set(value['steps']) == {'9', '10', '11', '12', '13'}
    return value


def owner_contract(packet, model=None):
    model = compile.cached(repo.ROOT) if model is None else model
    for ref in contracts()['required_owners'][packet]:
        expected = contracts()['owner_contracts'][ref]
        owner = publication.required_owner(model, ref, int(expected['address'], 16))
        symbol = owner.symbols['7mfk']
        publication.required_properties(model, owner.props, expected['props'])
        publication.required_properties(model, symbol.props, expected['symbol_props'])
        assert symbol.value('level') == expected['level']
        publication.required_evidence(model, symbol.evidence, expected['evidence'])
        for wanted in expected['links']:
            matches = [link for link in owner.links if
                (link.type, link.to.key, link.slot, link.offset) ==
                (wanted['type'], wanted['to'], wanted['slot'], wanted['offset'])]
            assert len(matches) == 1, (ref, wanted)
            [link] = matches
            assert link.stated >= set(wanted['layouts'])
            assert link.roles >= set(wanted['roles'])
            publication.required_properties(model, link.props, wanted['props'])
            publication.required_evidence(model, link.evidence, wanted['evidence'])
    chain = model.entities[('chain', 'closed_loop_fuel')]
    assert len(chain.steps) == 19
    for number in contracts()['packet_steps'][packet]:
        assert publication.normalized(model, chain.steps[number-1]) == contracts()['steps'][str(number)]
    assert contracts()['steps']['9']['sign'] == 'positive'
    assert all(contracts()['steps'][str(i)]['sign'] == 'none' for i in (10, 11, 12, 13))
    if packet == 'learning':
        owner = publication.required_owner(model, 'wisteria-tarantula/fn', 0x580e8)
        notes = publication.normalized(model, owner.props)['note']
        assert any(contracts()['formulas']['auxiliary'] in note for note in notes)


def region(packet):
    module = publication.stock_module()
    selected = [row for row in module.REGIONS if row.key == contracts()['regions'][packet]['key']]
    assert len(selected) == 1
    [row] = selected
    assert json.loads(json.dumps(asdict(row))) == contracts()['regions'][packet]
    assert module.REGION_OBSERVERS[row.key] == contracts()['observers'][packet]
    return row, module


def stock_bytes(packet, image):
    for at, raw in contracts()['slices'][packet]:
        data = bytes.fromhex(raw)
        assert image[at:at+len(data)] == data, f'{at:08x}'


def registered_stock_contract(packet, image):
    row, module = region(packet)
    stock_bytes(packet, image)
    for name, digest in contracts()['sources_sha256'][packet].items():
        assert hashlib.sha256((TOOL_DIR/name).read_bytes()).hexdigest() == digest, name
    assert hashlib.sha256(module.build_fixture(row, image)).hexdigest() == contracts()['fixtures'][packet]
    expected = contracts()['counts'][packet]
    assert sum((end-start)//2 for start, end in row.code_spans) == expected['instructions']
    assert sum(end-start for start, end in row.code_spans) + sum(size for _, size in row.pools) == expected['bound_bytes']
    assert row.cases == len(literals(packet)) == expected['cases']
    assert not row.boundary and not row.register_word_literals
    assert (row.return_address_offset, row.return_register) == (None, 5)
    assert len(row.ram_literals) == {'stft': 2, 'selection': 12, 'learning': 14}[packet]
    assert len(row.ram_word_literals) == (2 if packet == 'stft' else 0)


def previous_regions_contract():
    module = publication.stock_module()
    held = contracts()['previous_regions']
    assert len(held) == 73 and len(module.REGIONS) == 76
    assert json.loads(json.dumps([asdict(row) for row in module.REGIONS[:73]])) == held
    for key, name in contracts()['previous_observers'].items():
        assert module.REGION_OBSERVERS[key] == name
    images = {rom: module.stock_image(rom) for rom in {row.rom for row in module.REGIONS[:73]}}
    for row in module.REGIONS[:73]:
        assert hashlib.sha256(module.build_fixture(row, images[row.rom])).hexdigest() == contracts()['previous_fixtures'][row.key]


def all_bound_mutations_fail(packet, image):
    for at, raw in contracts()['slices'][packet]:
        for offset in range(len(bytes.fromhex(raw))):
            changed = bytearray(image)
            changed[at+offset] ^= 1
            try:
                stock_bytes(packet, changed)
            except AssertionError:
                pass
            else:
                raise AssertionError(f'{packet} accepts changed byte {at+offset:08x}')


@cache
def array(packet, name):
    text = (TOOL_DIR/contracts()['headers'][packet]).read_text()
    [body] = re.findall(name+r'\[\]\s*=\s*\{(.*?)\n\};', text, re.S)
    assert re.fullmatch(r'[\s{},0-9a-fxU]+', body)
    body = re.sub(r'(0x[0-9a-f]+|\d+)U\b', r'\1', body)
    return ast.literal_eval('['+body.replace('{', '[').replace('}', ']')+']')


def literals(packet):
    return array(packet, 'samples')


def publication_contract(packet):
    row, _ = region(packet)
    expected = contracts()['counts'][packet]
    for path in (SPEC, 'tools/sh-elf-run/README.md'):
        section = (repo.ROOT/path).read_text().split('## '+contracts()['sections'][packet], 1)[1].split('\n## ', 1)[0]
        [counts] = re.findall(r'One mandatory Region binds (\d+) instructions, (\d+) bound bytes and (\d+) literal\s+cases', section)
        assert tuple(map(int, counts)) == (expected['instructions'], expected['bound_bytes'], row.cases)
        prose = re.sub(r'\s+', ' ', section)
        assert 'physical units' in prose and 'cadence' in prose
    text = (repo.ROOT/SPEC).read_text()
    assert 'Hardware readiness is NO' in text
    assert '10621 normal' in text and '219 reset' in text and '10658 calls' in text
    assert '9340 enabled' in text and '516 disabled' in text
    assert '3179 conditional' in text and '1054 decay' in text and '2421 auxiliary' in text


def signed_word(word):
    return word | 0xffff0000 if word & 32768 else word


def signed32(value):
    return value - (1 << 32) if value & (1 << 31) else value


def clipped_index(value, axis, old, hysteresis, scale):
    raw = 0
    for threshold in axis[1:]:
        if value < scale*threshold:
            break
        raw += 1
    selected = raw
    if raw > old and value < scale*(axis[old+1]+hysteresis):
        selected -= 1
    if raw < old and value > scale*(axis[old]-hysteresis):
        selected += 1
    return selected, raw


def literal_contract(packet, rows=None):
    rows = literals(packet) if rows is None else rows
    counts = Counter()
    domains = {name: set() for name in ('mode', 'forced', 'packed', 'speed', 'coefficient', 'counter', 'permit_a', 'permit_b', 'index')}
    for row in rows:
        if packet == 'stft':
            assert len(row) == 7
            mode, forced, t, working, output, changed, exit_t = row
            assert mode in range(256) and forced in range(256) and t in (0, 1)
            assert len(working) == 2 and all(value in range(65536) for value in working)
            is_forced = bool(mode & 2)
            value = 256*min(125, max(75, forced))
            assert output == ([value, value] if is_forced else working)
            expected = ([value, 0x010022dc, 75*256 if forced < 75 else 125*256, value]
                        if is_forced else [signed_word(working[1]), signed_word(working[0]), 0x010040ac, 0x010022dc])
            assert changed == expected
            assert exit_t == (int(forced > 125) if is_forced else 1)
            counts['forced' if is_forced else 'normal'] += 1
            domains['mode'].add(mode)
            domains['forced'].add(forced)
        elif packet == 'selection':
            assert len(row) == 19
            bank_register, load, speed, packed, cell, flag, diagnostic, t, profile, lo, hi, li, si, index, output, reset, called, r3_speed_base, packed_output = row
            bank = bank_register & 255
            assert bank in (0, 1) and t in (0, 1) and profile in range(4)
            assert load in range(65536) and cell in range(65536)
            assert all(value in range(256) for value in (speed, packed, flag, diagnostic, lo, hi))
            a, s, lh, sh = array(packet, 'calibrations')[profile]
            expected_li, _ = clipped_index(load, a, packed & 7, lh, 256)
            expected_si, speed_raw = clipped_index(speed, s, (packed >> 3) & 7, sh//4, 1)
            assert [li, si, index, packed_output] == [expected_li, expected_si, 8*expected_si+expected_li, 8*expected_si+expected_li]
            expected_reset = int(not (lo*256 <= cell <= hi*256) or bool(flag & 1) or bool(diagnostic & 128))
            assert reset == expected_reset
            assert output == (25600 if expected_reset else cell)
            assert called == int(lo*256 <= cell <= hi*256 and not flag & 1)
            assert r3_speed_base == int(speed_raw != ((packed >> 3) & 7))
            counts['reset' if reset else 'normal'] += 1
            counts['predicate_called'] += called
            domains['packed'].add(packed)
            domains['speed'].add(speed)
        else:
            assert packet == 'learning' and len(row) == 22
            bank_register, word, stft, previous, index, counter, permit_a, permit_b, t, profile, coefficient_override, decay_override, enabled, region_index, coefficient, raw_delta, output, auxiliary, frame_threshold, changed_mask, exit_t, gpr = row
            bank = bank_register & 255
            assert bank in (0, 1) and index in range(64) and t in (0, 1)
            assert all(value in range(65536) for value in (word, stft, previous))
            assert all(value in range(256) for value in (counter, permit_a, permit_b))
            assert coefficient_override in range(257) and decay_override in range(257)
            thresholds, coefficients, initial, decay, lo, hi, aux_lo, aux_hi = array(packet, 'calibrations')[profile]
            if coefficient_override < 256:
                coefficients = [coefficient_override]*4
            if decay_override < 256:
                decay = decay_override
            expected_region = 0
            for threshold in thresholds:
                if abs(word-25600) <= 256*threshold:
                    break
                expected_region += 1
            expected_coefficient = initial if counter == 0 else coefficients[expected_region]
            numerator = (word-25600)*expected_coefficient
            delta = (1 if numerator >= 0 else -1)*(abs(numerator)//256)
            zero_force = stft != 25600 and delta == 0
            if zero_force:
                delta += 1 if word >= 25600 else -1
            expected_enabled = int(bool(permit_a & (1 << bank)) and bool(permit_b & (1 << bank)))
            assert [enabled, region_index, coefficient, signed32(raw_delta), output] == [
                expected_enabled, expected_region, expected_coefficient, delta, max(256*lo, min(256*hi, previous+delta))]
            incremented = (counter+1) & 255
            decay_applied = incremented+decay > 255
            aux_value = max(0, incremented-decay) if decay_applied else incremented
            outside = not (256*aux_lo <= word < 256*aux_hi)
            assert auxiliary == (0 if outside else aux_value)
            assert frame_threshold == thresholds[min(expected_region, 2)]*256
            if enabled:
                signed_lower = aux_lo | 0xffffff00 if aux_lo & 128 else aux_lo
                expected_gpr = [index if outside else 2*bank, index,
                    word if word >= 256*aux_hi else signed_lower, 255,
                    incremented-decay if decay_applied and incremented >= decay else incremented,
                    0 if outside else 256*aux_lo,
                    256*aux_hi if word >= 256*aux_hi else word, decay]
                assert gpr == expected_gpr and changed_mask == 255
                assert exit_t == (1 if word >= 256*aux_hi else int(word >= 256*aux_lo))
            else:
                first = not permit_a & (1 << bank)
                assert gpr == [0x1cc if first else 0x1cb, 0, permit_a if first else permit_b, 0, 0, 0x0100128c, bank+1, 0]
                assert changed_mask == 0x65 and exit_t == 1
            counts['enabled' if enabled else 'skipped'] += 1
            counts['zero_force'] += int(enabled and zero_force)
            counts['decay_applied'] += int(enabled and decay_applied)
            counts['auxiliary_cleared'] += int(enabled and outside)
            for name, value in (('coefficient', coefficient_override), ('counter', counter), ('permit_a', permit_a), ('permit_b', permit_b), ('index', index)):
                domains[name].add(value)
    if packet == 'stft':
        assert len(rows) == 6160 and counts == {'normal': 2308, 'forced': 3852}
        assert domains['mode'] == domains['forced'] == set(range(256))
    elif packet == 'selection':
        assert len(rows) == 10840 and counts == {'normal': 10621, 'reset': 219, 'predicate_called': 10658}
        assert domains['packed'] == domains['speed'] == set(range(256))
        assert {23039: 25600, 23040: 23040}.items() <= {
            row[4]: row[14] for row in rows if row[9:11] == [90, 110] and row[5:7] == [0, 0]}.items()
    else:
        assert len(rows) == 9856
        assert counts == {'enabled': 9340, 'skipped': 516, 'zero_force': 3179, 'decay_applied': 1054, 'auxiliary_cleared': 2421}
        assert set(range(256)) <= domains['coefficient']
        assert domains['counter'] == domains['permit_a'] == domains['permit_b'] == set(range(256))
        assert domains['index'] == set(range(64))
    return dict(counts)


@cache
def statements(note):
    assert Grammar(repo.config()).validate(note) is None
    class ExactDivision(ast.NodeTransformer):
        def visit_BinOp(self, node):
            node = self.generic_visit(node)
            if isinstance(node.op, ast.Div):
                return ast.copy_location(ast.Call(ast.Name('Fraction', ast.Load()), [node.left, node.right], []), node)
            return node
    result = []
    for statement in note.split(';'):
        target, expression = statement.split('=', 1)
        tree = ast.parse(re.sub(r'\bfrom\b', 'source', expression.strip()), mode='eval')
        tree = ast.fix_missing_locations(ExactDivision().visit(tree))
        result.append((target.strip(), builtins.compile(tree, '<closed-loop arithmetic>', 'eval')))
    return result


def evaluate(note, **values):
    env = dict(RAM8={}, RAM16={}, ROM8={}, source=0, x=0, Fraction=Fraction,
               uint8=lambda x: int(x) & 255, uint16=lambda x: int(x) & 65535,
               min=min, max=max, abs=abs, trunc0=int, floor=floor)
    env.update(values)
    for target, expression in statements(note):
        env[target] = eval(expression, {'__builtins__': {}}, env)
    return env


def formula_contract(packet):
    formula = contracts()['formulas'][packet]
    for row in literals(packet):
        if packet == 'stft':
            mode, forced, _, working, output, _, _ = row
            for bank in range(2):
                env = evaluate(formula, source=working[bank], RAM8={0xffff99c4: mode, 0xffff9925: forced})
                assert env['to'] == output[bank]
        elif packet == 'selection':
            bank_register, load, speed, packed, cell, flag, diagnostic, _, profile, lo, hi, li, si, index, output, reset, *_ = row
            bank = bank_register & 255
            a, s, lh, sh = array(packet, 'calibrations')[profile]
            rom = {0x12592+i: value for i, value in enumerate(a)}
            rom.update({0x126dc+i: value for i, value in enumerate(s)})
            rom.update({0x881b: lh, 0x881a: sh, 0x8a9e: lo, 0x8a9f: hi})
            env = evaluate(formula, x=bank_register, ROM8=rom,
                RAM8={0xffff11ae: speed, 0xffff130a+bank: packed, 0xffff41b5: flag, 0xffff5a94: diagnostic},
                RAM16={0xffff1024: load, 0xffff4b90-128*bank+2*index: cell})
            assert [env[key] for key in ('I', 'J', 'Z', 'to')] == [li, si, reset, output]
        else:
            bank_register, word, stft, previous, index, counter, permit_a, permit_b, _, profile, coefficient_override, decay_override, enabled, region_index, coefficient, raw_delta, output, auxiliary, *_ = row
            bank = bank_register & 255
            thresholds, coefficients, initial, decay, lo, hi, aux_lo, aux_hi = array(packet, 'calibrations')[profile]
            if coefficient_override < 256:
                coefficients = [coefficient_override]*4
            if decay_override < 256:
                decay = decay_override
            rom = {0x129c6+i: value for i, value in enumerate(coefficients)}
            rom.update({0x8a9d: initial, 0x88f5: decay, 0x8a9e: lo, 0x8a9f: hi, 0x839d: aux_lo, 0x839c: aux_hi})
            ram8 = {0xffff130a+bank: index, 0xffff49f0-64*bank+index: counter, 0xffff1458: permit_a, 0xffff1457: permit_b}
            ram8.update({0xffff2c21+i: value for i, value in enumerate(thresholds)})
            old = (23600 if bank else 23100)+17*index
            ram16 = {0xffff134e+2*bank: word, 0xffff2306+2*bank: previous, 0xffff4b90-128*bank+2*index: old}
            env = evaluate(formula, x=bank_register, source=stft, ROM8=rom, RAM8=ram8, RAM16=ram16)
            assert [env[key] for key in ('R', 'K', 'delta', 'G', 'to')] == [region_index, coefficient, signed32(raw_delta), enabled, output if enabled else old]
            env = evaluate(contracts()['formulas']['auxiliary'], x=bank_register, source=counter, ROM8=rom, RAM16=ram16)
            assert env['to'] == auxiliary
