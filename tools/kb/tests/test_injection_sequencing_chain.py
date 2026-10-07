"""Bind bounded injection scheduler operands to exact stock instructions."""
import ast
import builtins
from collections import Counter
import copy
from dataclasses import replace
from functools import cache
import hashlib
import math
import re
from types import SimpleNamespace

import pytest

from kb import compile, repo, sh2
from kb.arithmetic import Grammar
from tools.kb.tests import test_injection_start_delay_chain as publication

TOOL_DIR = repo.ROOT / 'tools/sh-elf-run'
PATH = 'tools/kb/tests/test_injection_sequencing_chain.py'
FORMULA = 'M = uint16(ffff22bc)*uint8(ffff193b); to = floor(uint32(6554*M)/65536)'
NEW = 'injection_offset_reciprocal_residue/ram'
CALLER = 'pumpkin-peacock/fn'
SPLIT = 'split_u8_by_ten/fn'
NORMALIZER = 'apc_command_phase_normalizer/fn'
SEQ = 'amigurumi-dormouse/fn'
CONTINUATION = 0xc0def00d
SECTIONS = {
    'pending': 'Bounded injection pending-mask selection',
    'reciprocal': 'Bounded injection reciprocal splitter',
    'tooth': 'Bounded injection argument splitting and phase normalization',
    'offset': 'Bounded injection offset multiplication',
}
OWNERS = (
    ('acrid-bonobo/ram', 0xffff20b4, 8, 'pending'),
    ('lurking-swine/ram', 0xffff221e, 8, 'pending'),
    ('uber-deer/ram', 0xffff2228, 8, 'pending'),
    ('huge-lori/ram', 0xffff13b8, 16, 'tooth'),
    ('economic-collie/ram', 0xffff193b, 8, 'tooth'),
    ('apc_mode/ram', 0xffff24c9, 8, 'tooth'),
    ('tunneling-doberman/ram', 0xffff13b2, 8, 'tooth'),
    ('spry-koel/ram', 0xffff22bc, 16, 'offset'),
    ('amphibian-panda/ram', 0xffff16c2, 16, 'offset'),
    (NEW, 0xffff166c, 8, 'offset'),
)
# Filled from the byte-locked original ROM and independently executed sources.
SLICES = {'pending': ((347398, b'\x02\x8c\x90_\x0e$'), (347100, b'\x90\x1d\xe2\x00\xe5\x06\x0e$\x90"\x02\xecf,v\x016S\x8b\x00\xe6\x00\xc4\xc0e\x0c6P\x89\x01\xa0\x87\x00\t\xde\x0cx\x07\x90\x13\x0eT\xa0~`S'), (347150, b'\xd3\x08\xe2\x00\x90\x02\x03$\xa0y\x00\t'), (140949, b'\x02\x04\x08\x10 \x01'), (347162, b'\x024'), (347180, b'\x02*'), (347184, b'\xff\xff\x1f\xf4'), (347594, b'\x024')), 'reciprocal': ((167548, b"O\x12\x93\x0fgc\x03G\x02\x1aB)f#F\x086,F\x00&h\x8d\x01%!4h'@\x00\x0bO\x16"), (167584, b'\x19\x9a')), 'tooth': ((177760, b'\xd6\x81\x84a\xc8@\x8d\x12dL\xe6xbC\xe0\x004c\x8f\x08\xc1\x96r\x88B\x11\x8d\x01f#\xe6\x00\xe0\x01bc\xc1\x96\xddw\x90i\xa0 \r$\xe2K\xdet\x05\x12B\x08f\xe35,\x92`\xd3sC\x0b6,\xc5\x96 \x08\x8d\tf\x03v\xfffm\xddm`c\xc1\x96\x90S\x02\xdcr\n\r$\xe2K\x04\x12B\x084,\x92K>,\xd3iC\x0be\xe3'), (167368, b"\xd2\x95gS\x90g\x05,bA`\\\x88\x04\x8f\rb-\xe5\x062S\x8b\x02\xe5\x0f2W\x8b2`#\x88\x05\x89>\x88\x04\x896\xa0B\x00\t\x88\t\x8b\x0f`#\x88\t\x8b\x06r\xffb-$!bpr\n' bAb-\xe5\n2S\x89*\xa00\x00\t\xe5\x0f2S\x8b\x05\xe5\x182W\x89\x02r\xfc\xa0\x13b-`#\x88\x0e\x8b\x02r\xfc\xa0\x1cb-\x88\r\x8b\x02r\xfd\xa0\x11b-\xe5\x032S\x8b\x06\xe5\x0c2W\x89\x03r\xfeb-\x00\x0b$!`#\x88\x02\x89\x07\x88\x01\x8b\x0cr\xffb-$!bp\xa0\x05r\nr\xfeb-$!bpr\x14\x00\x0b' \x00\x0b\x00\tO\x12\x93\x0fgc\x03G\x02\x1aB)f#F\x086,F\x00&h\x8d\x01%!4h'@\x00\x0bO\x16"), (167582, b'\x01&\x19\x9a'), (167968, b'\xff\xff\x12\x8c'), (178014, b'\x06\xaf'), (178276, b'\xff\xff\x12\x8c\xff\xff$\xc8\x00\x02\x8e|\x00\x02\x8d\xc8')), 'offset': ((177876, b'\xd2g\x90C\xddb\x06-\x90?fm\x02\xdce,\x92=\x05ge\xd35,r\xaaf\xd3\x04\x1a\xd3^C\x0b6,'), (167548, b"O\x12\x93\x0fgc\x03G\x02\x1aB)f#F\x086,F\x00&h\x8d\x01%!4h'@\x00\x0bO\x16"), (167584, b'\x19\x9a'), (178014, b'\x06\xaf\x02\xc8\x046'), (178276, b'\xff\xff\x12\x8c'), (178284, b'\x00\x02\x8e|'), (178292, b'\xff\xff\x1f\xf4'))}
EXECUTION_SOURCES = {'stock_jk08a_injection_pending.s': '384be94007ccb386cc09157d46f42b744bfc4148da225267379c198835669a0d', 'injection-pending-cases.h': '6a327a81dba202f5ffe7180c91279f46608c139009c8b17ce9aa1dcf9692fd68', 'harness-stock-jk08a-injection-pending.c': 'c0a7376fd33b19d86b9a7ef4d23428364f857d9aca55345003ca9444fbb84dc1', 'stock_jk08a_injection_reciprocal.s': '94d68b0c59e6137345791866a837f282b1ccbb36d3240568c83491fabe635e4c', 'injection-reciprocal-cases.h': 'a257f178bae70b2dbed05bc5c30e93bc3c123836ebe7195100807ec94f9bcadd', 'harness-stock-jk08a-injection-reciprocal.c': 'c785d0a238116e75862a1ac3dd38cece8e2b953ac91b8478dbb35bdb31863bb6', 'stock_jk08a_injection_tooth.s': 'ec2296c9e8bbb8f3788a1f7e5c2a8ccaa60e8aa468103dad1698b5edd0868b1c', 'injection-tooth-cases.h': 'f2047af2d2723c90ba8bc4d4c4bd978bc7b62f9ddf60103de2f89188dfd73a99', 'harness-stock-jk08a-injection-tooth.c': 'fb87f1f5bb7fc31a16d5dce30c4467b2e9c1ddcbf6e3ed90a3ea19a01cf2ede5', 'stock_jk08a_injection_offset.s': 'eecb0c0549d0497eb9175d55a2195cd3eb62527d2f586840b11b5f58db9e4fef', 'injection-offset-cases.h': 'bf2cfdd9692f89727c1a2568b3daccd889ce83774732da6e67bda4ae80828c95', 'harness-stock-jk08a-injection-offset.c': '28ffad7063aa90550f59e484d02517480cc8e5c16cb9aa8fed3dcf2d360f99f3', 'stock_injection_start_delay_invoke.s': '0e60c06fb860bfccde3e166f1d45e4059994026ccd89db9313a5b6d0757d44db'}

def evidence(scope):
    return [{'kind': 'test', 'path': PATH, 'key': 'test_injection_sequencing_owner_contract'},
            {'kind': 'test', 'path': PATH, 'key': 'test_injection_sequencing_registered_stock_contract'},
            {'kind': 'spec', 'path': publication.SPEC, 'key': SECTIONS[scope]}]

def declared_regions():
    Region = publication.stock_module().Region
    common = {'rom': 'JK08A'}
    return {
        'pending': Region(**common, key='jk08a-injection-pending',
            source='stock_jk08a_injection_pending.s', harness='harness-stock-jk08a-injection-pending.c',
            start=0x54d06, end=0x54d0c, callees=((0x54bdc, 0x54c0a), (0x54c0e, 0x54c1a)),
            pools=((0x22695, 6), (0x54c1a, 2), (0x54c2c, 2), (0x54c30, 4), (0x54dca, 2)),
            ram_literals=(0x54c30,), cases=9216,
            symbols=(('SLOT', 'acrid-bonobo/ram'), ('CURSOR', 'lurking-swine/ram'), ('PENDING', 'uber-deer/ram')),
            constants=(('ZERO_ENTRY', 0x54bdc), ('NEGATIVE_ENTRY', 0x54c0e), ('EARLY_ONLY', 0))),
        'reciprocal': Region(**common, key='jk08a-injection-reciprocal',
            source='stock_jk08a_injection_reciprocal.s', harness='harness-stock-jk08a-injection-reciprocal.c',
            start=0x28e7c, end=0x28e9e, boundary=False,
            pools=((0x28ea0, 2),), ram_literals=(), cases=12826,
            symbols=(('OUTPUT', 'amphibian-panda/ram'), ('REMAINDER', 'economic-collie/ram')),
            constants=(('EARLY_ONLY', 0),)),
        'tooth': Region(**common, key='jk08a-injection-tooth',
            source='stock_jk08a_injection_tooth.s', harness='harness-stock-jk08a-injection-tooth.c',
            start=0x2b660, end=0x2b6ce, callees=((0x28dc8, 0x28e9e),),
            pools=((0x28e9e, 4), (0x29020, 4), (0x2b75e, 2), (0x2b864, 16)),
            ram_literals=(0x29020, 0x2b864, 0x2b868), cases=12668,
            return_address_offset=24, return_register=11,
            symbols=(('COUNT', 'huge-lori/ram'), ('REMAINDER', 'economic-collie/ram'),
                     ('MODE', 'apc_mode/ram'), ('POSITION', 'tunneling-doberman/ram')),
            constants=(('DIRECT_ENTRY', 0x2b676), ('NORMALIZER_ENTRY', 0x28dc8), ('EARLY_ONLY', 0))),
        'offset': Region(**common, key='jk08a-injection-offset',
            source='stock_jk08a_injection_offset.s', harness='harness-stock-jk08a-injection-offset.c',
            start=0x2b6d4, end=0x2b6f8, callees=((0x28e7c, 0x28e9e),),
            pools=((0x28ea0, 2), (0x2b75e, 6), (0x2b864, 4), (0x2b86c, 4), (0x2b874, 4)),
            ram_literals=(0x2b864, 0x2b874), cases=14118,
            return_address_offset=24, return_register=11,
            symbols=(('PERIOD', 'spry-koel/ram'), ('REMAINDER', 'economic-collie/ram'),
                     ('OUTPUT', 'amphibian-panda/ram'), ('SCRATCH', NEW)),
            constants=(('EARLY_ONLY', 0),)),
    }

def region_contract(module, scope):
    expected = declared_regions()[scope]
    matches = [region for region in module.REGIONS if region.key == expected.key]
    assert len(matches) == 1, 'The mandatory bounded injection Region is absent or duplicated'
    [region] = matches
    assert region == expected and type(region.cases) is int
    return region

def stock_contract(data, scope):
    for address, expected in SLICES[scope]:
        assert data[address:address + len(expected)] == expected, f'{address:08x}'
    region = declared_regions()[scope]
    word = lambda at: int.from_bytes(data[at:at+2], 'big')
    for start, end in region.code_spans:
        for address in range(start, end, 2):
            instruction = sh2.decode(word(address), address)
            if instruction.flow == 'branch':
                assert instruction.target == region.end or any(lo <= instruction.target < hi
                    for lo, hi in region.code_spans)
    if scope in ('reciprocal', 'tooth', 'offset'):
        assert word(0x28e7c) == 0x4f12 and word(0x28e92) == 0x8d01
        assert word(0x28e94) == 0x2521 and word(0x28e9a) == 0x000b
        assert word(0x28e9c) == 0x4f16 and word(0x28ea0) == 6554
    if scope == 'tooth':
        assert word(0x2b666) == 0x8d12 and word(0x2b668) == 0x644c
        assert word(0x2b67a) == 0x8d01 and word(0x2b67e) == 0xe600
        assert int.from_bytes(data[0x2b86c:0x2b870], 'big') == 0x28e7c
        assert int.from_bytes(data[0x2b870:0x2b874], 'big') == 0x28dc8
    if scope == 'offset':
        base = int.from_bytes(data[0x2b864:0x2b868], 'big')
        destination = base + word(0x2b762)
        assert destination == 0xffff16c2 and destination-0x56 == 0xffff166c
        assert word(0x2b6e6) == 0x0567 and word(0x2b6f4) == 0x430b
        assert word(0x2b6f6) == 0x362c
    if scope == 'pending':
        assert data[0x22695:0x2269b] == bytes((2,4,8,16,32,1))

@cache
def literals(scope):
    text = (TOOL_DIR / f'injection-{scope}-cases.h').read_text()
    [body] = re.findall(scope + r'_cases\[\] = \{(.*?)\n\};', text, re.S)
    body = re.sub(r'(0x[0-9a-f]+|\d+)U\b', r'\1', body)
    rows = ast.literal_eval('[' + body.replace('{', '[').replace('}', ']') + ']')
    count = declared_regions()[scope].cases
    assert re.findall(r'^#define ' + scope.upper() + r'_CASE_COUNT (\d+)U$', text, re.M) == [str(count)]
    assert len(rows) == count and all(len(row[-1]) == len(row[-2]) == 15 for row in rows)
    return rows

def seed(variant):
    return [((0x81234567+i*0x1020305) if variant else (0x1728394a+i*0x110203)) & 0xffffffff
            for i in range(15)]

def reciprocal(value):
    quotient = ((6554*value) & 0xffffffff) >> 16
    return quotient, (value-10*quotient) & 0xffffffff

def normalized(count, remainder, position):
    original = count
    signed = remainder if remainder <128 else remainder-256
    change = lambda c, add: (c, (remainder+add)&255, (signed+add)&0xffffffff)
    if position == 4:
        scratch = 6 if count <6 else 15
        if 6 <= count <= 15: return count-2,remainder,4,count-2,scratch,0
        if count == 5:
            c,r,r2 = change(3,20)
            return c,r,5,r2,scratch,1
        if count == 4:
            c,r,r2 = change(3,10)
            return c,r,4,r2,scratch,1
        return count,remainder,count,count,scratch,0
    if position == 9:
        if count == 9: count,remainder = 8,(remainder+10)&255
        if count >=10:
            c,r,r2 = change(count-2,20)
            return c,r,original,r2,10,1
        return count,remainder,original,count,10,0
    if 15 <= count <=24: return count-4,remainder,position,count-4,24,0
    if count in (13,14):
        c,r,r2 = change(10,10*(count-12))
        return c,r,count,r2,15,1
    if 3 <= count <=12: return count-2,remainder,count,count-2,12,0
    if count in (1,2):
        c,r,r2 = change(0,10*count)
        return c,r,count,r2,3,1
    assert count == 0 or count >24
    return count,remainder,count,count,3 if count==0 else 12,0

def vector_contract(scope, row):
    incoming, expected = row[-2:]
    if scope == 'pending':
        entry,cursor,slot,variant,t,next_cursor,mask,exit_t = row[:-2]
        assert entry in (0x54d06,0x54bdc,0x54c0e) and 0 <= cursor <=255 and 0 <= slot <=255
        actual = seed(variant)
        actual[7],actual[8],actual[14] = entry,0x22695 if entry==0x54d06 else 0x2268e,0x01001ff4
        if entry==0x54d06: actual[0] = slot
        if entry==0x54bdc: actual[6] = 0
        if entry==0x54c0e: actual[6] = 0xffffffff
        final = actual.copy()
        c,m,result_t = cursor,0,t
        if entry==0x54d06:
            assert slot <6
            m = (2,4,8,16,32,1)[slot]
            final[0],final[2] = 0x234,m
        elif entry==0x54bdc:
            next_slot = cursor+1 if cursor<5 else 0
            result_t = int(slot==next_slot)
            signed = lambda v: (v if v<128 else v-256)&0xffffffff
            final[0],final[2],final[5],final[6] = signed(slot),signed(cursor),slot,next_slot
            if result_t:
                c,m = slot,(2,4,8,16,32,1)[slot]
                final[0],final[2],final[8] = 0x234,m,0x22695
        else: final[0],final[2],final[3] = 0x234,0,0x01001ff4
        assert (next_cursor,mask,exit_t)==(c,m,result_t)
    elif scope == 'reciprocal':
        value,variant,t,quotient,remainder,exit_t = row[:-2]
        assert 0 <= value <=0xffffffff
        q,residue = reciprocal(value)
        assert (quotient,remainder,exit_t)==(q,residue&255,int(q==0))
        actual = seed(variant)
        actual[4:8] = value,0x010016c2,0x0100193b,0x28e7c
        final = actual.copy()
        final[2],final[3],final[4],final[6],final[7] = q,6554,residue,10*q,0x0100193b
    elif scope == 'offset':
        period,remainder,variant,t,product,quotient,scratch,exit_t = row[:-2]
        assert 0 <= period <=65535 and 0 <= remainder <=255
        q,residue = reciprocal(period*remainder)
        assert (product,quotient,scratch,exit_t)==(period*remainder,q,residue&255,int(q==0))
        actual = seed(variant)
        actual[7] = 0x2b6d4
        final = actual.copy()
        final[0],final[2],final[3],final[4] = 0x6af,q,6554,residue
        final[5],final[6],final[7],final[11],final[13] = 0x010016c2,10*q,0x0100166c,CONTINUATION,0x0100128c
    else:
        assert scope=='tooth'
        entry,argument,flags,position,variant,t,count,remainder,exit_t,normal,old_count,old_remainder = row[:-2]
        assert entry in (0x2b660,0x2b676,0x28dc8)
        assert 0 <= argument <=0xffffffff and 0 <= flags <=255 and 0 <= position <=255
        actual = seed(variant)
        actual[4],actual[7] = argument,entry
        if entry==0x2b676: actual[2] = argument
        if entry==0x28dc8: actual[4],actual[5] = 0x010013b8,0x0100193b
        final = actual.copy()
        if entry!=0x28dc8: final[11] = CONTINUATION
        is_normal = int(entry==0x2b660 and not flags&64)
        assert normal==is_normal
        if entry==0x28dc8:
            c,r,r0,r2,r5,result_t = normalized(old_count,old_remainder,position)
            final[0],final[2],final[5],final[7] = r0,r2,r5,0x0100193b
        elif entry==0x2b676:
            difference = (argument-120)&0xffffffff
            result_t = int(difference<0x80000000)
            c,r = 1,difference if result_t else 0
            final[0],final[2],final[6],final[13] = 0x6af,r,r,0x0100128c
        elif flags&64:
            a = argument&255
            c = int(a>=120)
            r = a-120 if c else a
            result_t = c
            final[0],final[2],final[4],final[6],final[13] = 0x6af,r,a,r if c else 120,0x0100128c
        else:
            a = argument&255
            q,rem = divmod(a,10)
            initial = max(0,q-1)
            rem += 10 if q else 0
            c,r,r0,r2,r5,result_t = normalized(initial,rem,position)
            final[0],final[2],final[3],final[4],final[5] = r0,r2,0x28dc8,0x010013b8,r5
            final[6],final[7],final[14] = initial,0x0100193b,0x0100193b
            if q: final[13] = 0x0100128c
        assert (count,remainder,exit_t)==(c,r&255,result_t)
    assert variant in (0,1) and t in (0,1)
    assert incoming==actual and expected==final

@cache
def program(formula=FORMULA):
    assert Grammar(repo.config()).validate(formula) is None
    source = re.sub(r'\bffff[0-9a-f]{4}\b', lambda m: 'memory[0x'+m[0]+']', formula)
    return builtins.compile(source, '<bounded reciprocal offset arithmetic>', 'exec')

def evaluate(period, remainder, formula=FORMULA):
    values = {'memory': {0xffff22bc: period, 0xffff193b: remainder},
              'uint8': lambda v: v&255, 'uint16': lambda v: v&65535,
              'uint32': lambda v: v&0xffffffff, 'floor': math.floor}
    exec(program(formula), {'__builtins__': {}}, values)
    return values['to']

def chain_contract(model):
    chain = model.entities[('chain','injection_phase')]
    assert len(chain.steps)==22
    assert publication.normalized(model,chain.steps[18])=={
        'from': 'spry-koel/ram', 'to': 'amphibian-panda/ram', 'effect': 'scales',
        'sign': 'none', 'via': [CALLER,SPLIT], 'note': FORMULA,
        'specs': ['defs/JK08A.fuel.md',publication.SPEC]}
    assert Grammar(repo.config()).validate(chain.steps[18]['note']) is None

def owner(model, ref):
    matches = [meaning for meaning in model.meanings if meaning.key==ref]
    assert len(matches)==1, 'Mandatory meaning is absent or ambiguous: '+ref
    return matches[0]

def clone_owner(meaning):
    changed = copy.copy(meaning)
    changed.symbols = {layout:copy.copy(symbol) for layout,symbol in meaning.symbols.items()}
    for symbol in changed.symbols.values():
        symbol.props = copy.deepcopy(symbol.props)
        symbol.meaning = changed
    changed.links = [copy.copy(link) for link in meaning.links]
    for link in changed.links:
        link.props = copy.deepcopy(link.props)
        link.evidence = copy.deepcopy(link.evidence)
        link.owner = changed
    return changed

def owner_contract(model):
    for ref,address,width,scope in OWNERS:
        meaning = publication.required_owner(model,ref,address)
        symbol = meaning.symbols['7mfk']
        assert symbol.value('width')==width and symbol.value('signed') is False
        publication.required_evidence(model,symbol.evidence,evidence(scope))
    for ref,address,scope in ((SEQ,0x54a44,'pending'),(CALLER,0x2b64a,'tooth'),
                               (SPLIT,0x28e7c,'reciprocal'),(NORMALIZER,0x28dc8,'tooth')):
        symbol = publication.required_owner(model,ref,address).symbols['7mfk']
        publication.required_evidence(model,symbol.evidence,evidence(scope))
    links = []
    for operand in ('acrid-bonobo/ram','lurking-swine/ram'):
        links.append(('uber-deer/ram','input',operand,'pending',[SEQ],None))
    for output in ('amphibian-panda/ram',NEW):
        links.append((output,'writer',CALLER,'offset',[CALLER,SPLIT],None))
        for operand in ('spry-koel/ram','economic-collie/ram'):
            links.append((output,'input',operand,'offset',[CALLER,SPLIT],None))
    for output in ('huge-lori/ram','economic-collie/ram'):
        links.append((output,'writer',CALLER,'tooth',[CALLER,SPLIT],None))
        links.append((output,'writer',NORMALIZER,'tooth',[CALLER,NORMALIZER],None))
    links.append((CALLER,'selector','apc_mode/ram','tooth',[CALLER],'bit6'))
    for ref,kind,to,scope,via,slot in links:
        meaning = owner(model,ref)
        matches = [link for link in meaning.links if link.type==kind and link.to.key==to and link.slot==slot]
        assert len(matches)==1
        [link] = matches
        assert link.offset is None and link.stated=={'7mfk'}
        assert publication.normalized(model,link.props['via'])==via
        assert link.props['relies']=='structure' and link.props['supports']=='identity'
        assert 'separate evidence' in link.props['note']
        publication.required_evidence(model,link.evidence,evidence(scope))
    splitter = owner(model,SPLIT)
    assert 'floor(uint32(6554*M)/65536)' in splitter.props['summary']
    assert 'M in 0..255' in splitter.props['summary']
    output = owner(model,'amphibian-panda/ram')
    assert 'no saturating cap' in output.props['summary']
    residue = owner(model,NEW)
    assert 'not restricted' in residue.props['summary'] and '0..9' in residue.props['summary']
    chain_contract(model)

def publication_contract(text, scope, model):
    region = region_contract(publication.stock_module(),scope)
    instructions = sum((end-start)//2 for start,end in region.code_spans)
    bound = 2*instructions+sum(size for _,size in region.pools)
    for pattern,value in ((r'\b(\d+) instructions\b',instructions),
                          (r'\b(\d+) bound bytes\b',bound),
                          (r'\b(\d+) literal cases\b',len(literals(scope)))):
        claims = re.findall(pattern,text)
        assert claims and all(int(claim)==value for claim in claims)
    for phrase in ('EARLY_ONLY=0','all fifteen GPRs','actual complete SR',
                   '76-byte','96 frame bytes','64k RAM','hardware'):
        assert phrase in text
    if scope=='offset':
        assert FORMULA in text and 'step 19' in text and 'sign `none`' in text
        assert 'ffff166c' in text and 'Q=3277' in text and 'byte 246' in text
        chain_contract(model)
    if scope=='pending':
        assert 'positive-delta catch-up' in text and 'earlier mode exits' in text
    if scope=='tooth':
        assert '32 direct clamp contexts' in text and '3376 direct normalizer contexts' in text
        assert 'source-argument dispatch' in text and 'A=uint8(R4)' in text
    if scope=='reciprocal':
        assert 'M in 0..255' in text and 'M=200000' in text and 'Q=20001' in text

@pytest.mark.parametrize('scope',tuple(SECTIONS))
def test_injection_sequencing_registered_stock_contract(scope):
    module = publication.stock_module()
    region = region_contract(module,scope)
    image = module.stock_image('JK08A')
    stock_contract(image,scope)
    fixture = module.build_fixture(region,image)
    for start,end in region.code_spans:
        assert fixture[start:end]==image[start:end]
    for address in region.ram_literals:
        assert int.from_bytes(fixture[address:address+4],'big')==0x01000000+(int.from_bytes(image[address:address+4],'big')&65535)
    definitions = module.harness_defines(region,image)
    model = compile.cached(repo.ROOT)
    for macro,ref in region.symbols:
        assert definitions[macro]==owner(model,ref).symbols['7mfk'].key.address
    assert definitions['EARLY_ONLY']==0

def test_injection_sequencing_owner_contract():
    owner_contract(compile.cached(repo.ROOT))

@pytest.mark.parametrize('ref,address,width,scope',OWNERS)
@pytest.mark.parametrize('field',('width','signed'))
def test_injection_sequencing_refuses_wrong_operand_width_and_sign(ref,address,width,scope,field):
    model = compile.cached(repo.ROOT)
    changed = clone_owner(owner(model,ref))
    changed.symbols['7mfk'].props[field] = 32 if field=='width' else True
    def meaning_of(key):
        if key==changed.symbols['7mfk'].key: return changed
        return model.meaning_of(key)
    proxy = SimpleNamespace(meanings=[changed if item.key==ref else item for item in model.meanings],
        entities=model.entities,meaning_of=meaning_of)
    with pytest.raises(AssertionError): owner_contract(proxy)

@pytest.mark.parametrize('kind',('missing','via','offset','layout','evidence'))
def test_injection_sequencing_refuses_unbound_indirect_residue_writer(kind):
    model = compile.cached(repo.ROOT)
    changed = clone_owner(owner(model,NEW))
    [writer] = [link for link in changed.links if link.type=='writer' and link.to.key==CALLER]
    if kind=='missing': changed.links.remove(writer)
    elif kind=='via': writer.props['via'] = []
    elif kind=='offset': writer.offset = 1
    elif kind=='layout': writer.stated = {'jk78c'}
    else: writer.evidence = []
    def meaning_of(key):
        if key==changed.symbols['7mfk'].key: return changed
        return model.meaning_of(key)
    proxy = SimpleNamespace(meanings=[changed if item.key==NEW else item for item in model.meanings],
        entities=model.entities,meaning_of=meaning_of)
    with pytest.raises(AssertionError): owner_contract(proxy)

@pytest.mark.parametrize('scope',tuple(SECTIONS))
def test_injection_sequencing_every_literal_binds_complete_scalar_and_register_results(scope):
    for row in literals(scope): vector_contract(scope,row)

@pytest.mark.parametrize('scope,address',[(scope,address+i) for scope,spans in SLICES.items()
    for address,data in spans for i in range(len(data))])
def test_injection_sequencing_rejects_every_changed_instruction_and_pool_byte(scope,address):
    image = bytearray(publication.stock_module().stock_image('JK08A'))
    image[address]^=1
    with pytest.raises(AssertionError): stock_contract(image,scope)

@pytest.mark.parametrize('scope',tuple(SECTIONS))
@pytest.mark.parametrize('kind',('missing','duplicate','cases','pool','alias','early','callee','end','boundary'))
def test_injection_sequencing_refuses_missing_or_weakened_region(scope,kind):
    module = publication.stock_module()
    regions = list(module.REGIONS)
    region = declared_regions()[scope]
    index = next(i for i,item in enumerate(regions) if item.key==region.key)
    if kind=='missing': del regions[index]
    elif kind=='duplicate': regions.append(region)
    else:
        change = {'cases':{'cases':region.cases-1},'pool':{'pools':()},
                  'alias':{'ram_literals':region.ram_literals+(0x28ea0,)},
                  'early':{'constants':region.constants[:-1]+(('EARLY_ONLY',1),)},
                  'callee':{'callees':region.callees+((0x54a44,0x54a46),)},
                  'end':{'end':region.end-2},'boundary':{'boundary':not region.boundary}}[kind]
        regions[index] = replace(region,**change)
    with pytest.raises(AssertionError): region_contract(SimpleNamespace(REGIONS=regions),scope)

@pytest.mark.parametrize('scope',tuple(SECTIONS))
@pytest.mark.parametrize('position',('output','sr','incoming','gpr'))
def test_injection_sequencing_refuses_changed_literal_observations(scope,position):
    row = copy.deepcopy(literals(scope)[0])
    if position=='gpr': row[-1][8]^=1
    elif position=='incoming': row[-2][9]^=1
    elif position=='sr': row[{'pending':7,'reciprocal':5,'tooth':8,'offset':7}[scope]]^=1
    else: row[{'pending':6,'reciprocal':3,'tooth':6,'offset':5}[scope]]^=1
    with pytest.raises(AssertionError): vector_contract(scope,row)

def test_injection_sequencing_offset_equation_matches_all_real_caller_literals():
    for row in literals('offset'): assert evaluate(row[0],row[1])==row[5]

@pytest.mark.parametrize('before,after',(('6554','6553'),('uint32(6554*M)','6554*M'),
    ('uint32(6554*M)','uint16(6554*M)'),('uint16(ffff22bc)','uint8(ffff22bc)'),
    ('*uint8(ffff193b)','+uint8(ffff193b)'),('65536','65535')))
def test_injection_sequencing_offset_equation_rejects_precision_wrap_width_and_operator_changes(before,after):
    formula = FORMULA.replace(before,after)
    assert any(evaluate(row[0],row[1],formula)!=row[5] for row in literals('offset'))

def test_injection_sequencing_reciprocal_has_executed_precision_and_wrap_witnesses():
    [precision] = [row for row in literals('reciprocal')[:12] if row[0]==200000]
    assert precision[3:5]==[20001,246] and precision[3]!=precision[0]//10
    rows = literals('offset')
    assert any(row[0:2]==[8192,4] and row[5]==3277 for row in rows[:12])
    assert any(row[5] < (row[0]*row[1])//10 for row in rows)
    by_remainder = {}
    for period,remainder,_,_,_,quotient,*_ in rows: by_remainder.setdefault(remainder,{})[period]=quotient
    assert any(any(a>b for (_,a),(_,b) in zip(ordered,ordered[1:]))
               for values in by_remainder.values() if len(ordered:=sorted(values.items()))>1)

def test_injection_sequencing_full_consumer_domains_and_direct_entries_are_present():
    pending = literals('pending')
    assert {row[1] for row in pending if row[0]==0x54bdc}==set(range(256))
    assert {row[2] for row in pending if row[0]==0x54c0e}==set(range(256))
    assert {row[0] for row in literals('reciprocal') if row[0]<256}==set(range(256))
    tooth = literals('tooth')
    assert Counter(row[0] for row in tooth)=={0x2b660:9260,0x2b676:32,0x28dc8:3376}
    for position in range(10):
        assert {row[1]&255 for row in tooth if row[0]==0x2b660 and not row[2]&64 and row[3]==position}==set(range(256))
    assert {row[2] for row in tooth if row[0]==0x2b660}==set(range(256))
    assert {row[3] for row in tooth}==set(range(256))
    assert {row[1] for row in literals('offset')}==set(range(256))

@pytest.mark.parametrize('path',(publication.SPEC,'tools/sh-elf-run/README.md'))
@pytest.mark.parametrize('scope',tuple(SECTIONS))
def test_injection_sequencing_published_counts_bind_to_executed_sources(path,scope):
    publication_contract(publication.section(path,SECTIONS[scope]),scope,compile.cached(repo.ROOT))

@pytest.mark.parametrize('scope',tuple(SECTIONS))
@pytest.mark.parametrize('phrase',('instructions','bound bytes','literal cases'))
def test_injection_sequencing_rejects_contradictory_appended_counts(scope,phrase):
    text = publication.section(publication.SPEC,SECTIONS[scope])+'\n999999 '+phrase+'\n'
    with pytest.raises(AssertionError): publication_contract(text,scope,compile.cached(repo.ROOT))

def test_injection_sequencing_sources_preserve_the_executed_fixtures_and_shared_invocation():
    for name,expected in EXECUTION_SOURCES.items():
        assert hashlib.sha256((TOOL_DIR/name).read_bytes()).hexdigest()==expected,name

@pytest.mark.parametrize('field,value',(('sign','positive'),('via',[CALLER]),
    ('via',[SPLIT,CALLER]),('specs',['defs/JK08A.fuel.md']),
    ('note','to = floor(uint16(ffff22bc)*uint8(ffff193b)/10)')))
def test_injection_sequencing_chain_refuses_positive_sign_approximation_and_missing_real_call(field,value):
    model = compile.cached(repo.ROOT)
    chain = copy.deepcopy(model.entities[('chain','injection_phase')])
    chain.steps[18][field] = value
    proxy = SimpleNamespace(entities={('chain','injection_phase'):chain},meaning_of=model.meaning_of)
    with pytest.raises(AssertionError): chain_contract(proxy)
