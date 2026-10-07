"""Bind the stored-count decision and saved-frame return to exact stock bytes."""
import ast
import copy
from dataclasses import replace
from functools import cache
import hashlib
import re
from types import SimpleNamespace

import pytest

from kb import compile, repo, sh2
from tools.kb.tests import test_injection_dispatch_chain as dispatch
from tools.kb.tests import test_injection_start_delay_chain as publication
from tools.kb.tests import test_injection_sequencing_chain as operands

TOOL_DIR = repo.ROOT/'tools/sh-elf-run'
PATH = 'tools/kb/tests/test_injection_count_chain.py'
SECTION = 'Bounded injection count decision and saved-frame return'
PROG = 'pumpkin-peacock/fn'
COUNT = 'huge-lori/ram'
SLICES = ((177870, b'\xc5\x96 \x08\x8b:\xd2g\x90C\xddb\x06-\x90?fm\x02\xdce,\x92=\x05ge\xd35,r\xaaf\xd3\x04\x1a\xd3^C\x0b6,'), (167548, b"O\x12\x93\x0fgc\x03G\x02\x1aB)f#F\x086,F\x00&h\x8d\x01%!4h'@\x00\x0bO\x16"), (177994, b'O\x17O\x16O&n\xf6\x00\x0bm\xf6'), (167584, b'\x19\x9a'), (178014, b'\x06\xaf\x02\xc8\x046'), (178276, b'\xff\xff\x12\x8c'), (178284, b'\x00\x02\x8e|'), (178292, b'\xff\xff\x1f\xf4'))
EXECUTION_SOURCES = {'stock_jk08a_injection_count.s': '5e429c385d3a2356e79856624b58aa2d8893f522b5c113870c22b7478c4aaf6e', 'harness-stock-jk08a-injection-count.c': '7b4a348bf68c7c39178a2f6604671692041da9d4c6172f237b66180cd563ddfb', 'injection-count-cases.h': '805396ba4cb72b3ce1b096b8f101f6738602e6707aabb7fcb2991f978be8fd5f', 'stock_injection_count_invoke.s': '176d8bf6c981583e3d894708d6ecb9b013de6f959175aca40a9624c9aced705f', 'stock_invoke.s': '24686f13ca6d9176a80872ef2594f0ed0b812c367b9e0c6e355b86277a6fcde7', 'stock_injection_start_delay_invoke.s': '0e60c06fb860bfccde3e166f1d45e4059994026ccd89db9313a5b6d0757d44db'}
OBSERVER = {'SETUP': '    mov r3,r2\n    add #76,r2\n    mov.l @r2+,r0\n    mov.l r0,@r15\n    mov.l @r2+,r0\n    mov.l r0,@(4,r15)\n    mov.l L_injection_count_nonzero_pointer,r0\n    mov.l r0,@(8,r15)\n    mov.l @r2+,r0\n    mov.l r0,@(12,r15)\n    mov.l @r2,r0\n    mov.l r0,@(16,r15)\n    mov r6,r2\n    add #124,r2\n    add #124,r2\n    add #124,r2\n    add #8,r2\n    mov.l L_injection_count_nonzero_pointer,r0\n    mov.l r0,@r2\n', 'RETURNS': 'L_injection_count_nonzero_return:\n    add #104,r15\n    mov.l r0,@r15\n    mov r15,r0\n    add #-104,r0\n    add #-4,r15\n    mov.l r0,@r15\n    add #-120,r15\n    mov #124,r0\n    mov.l @(r0,r15),r0\n    bra L_injection_count_capture\n    nop\nL_injection_count_stock_return:\n    add #124,r15\n    mov.l r0,@r15\n    mov r15,r0\n    add #-124,r0\n    add #-4,r15\n    mov.l r0,@r15\n    add #-120,r15\n    mov #124,r0\n    mov.l @(r0,r15),r0\nL_injection_count_capture:\n', 'OLD_SP': '    mov r15,r0\n    add #-32,r0\n    mov.l r0,@r2\n', 'ACTUAL_SP': '    mov r15,r0\n    add #88,r0\n    mov.l @r0,r0\n    mov.l r0,@r2\n', 'POINTER': 'L_injection_count_nonzero_pointer: .long L_injection_count_nonzero_return\n'}

def evidence():
    return [{'kind':'test','path':PATH,'key':'test_injection_count_owner_contract'},
            {'kind':'test','path':PATH,'key':'test_injection_count_registered_stock_contract'},
            {'kind':'spec','path':publication.SPEC,'key':SECTION}]

def declared_region():
    return publication.stock_module().Region(key='jk08a-injection-count',rom='JK08A',
        source='stock_jk08a_injection_count.s',harness='harness-stock-jk08a-injection-count.c',
        start=0x2b6ce,end=0x2b6f8,return_address_offset=24,return_register=11,
        callees=((0x28e7c,0x28e9e),(0x2b74a,0x2b756)),
        pools=((0x28ea0,2),(0x2b75e,6),(0x2b864,4),(0x2b86c,4),(0x2b874,4)),
        ram_literals=(0x2b864,0x2b874),cases=10252,
        symbols=(('COUNT',COUNT),('PERIOD','spry-koel/ram'),
                 ('REMAINDER','economic-collie/ram'),('OUTPUT','amphibian-panda/ram'),
                 ('SCRATCH','injection_offset_reciprocal_residue/ram')),
        constants=(('EARLY_ONLY',0),))

def region_contract(module):
    expected = declared_region()
    matches = [region for region in module.REGIONS if region.key == expected.key]
    assert len(matches) == 1
    [region] = matches
    assert region == expected and type(region.cases) is int
    return region

def stock_contract(data):
    assert sum(len(span) for _,span in SLICES) == 108
    for address,span in SLICES:
        assert data[address:address+len(span)] == span, f'{address:08x}'
    region = declared_region()
    allowed = {region.end, *(start for start,_ in region.callees)}
    for start,end in ((region.start,region.end),*region.callees):
        for address in range(start,end,2):
            instruction = sh2.decode(int.from_bytes(data[address:address+2],'big'),address)
            if instruction.flow == 'branch':
                assert instruction.target in allowed or start <= instruction.target < end
    assert int.from_bytes(data[0x2b86c:0x2b870],'big') == 0x28e7c

@cache
def literals():
    text = (TOOL_DIR/'injection-count-cases.h').read_text()
    [body] = re.findall(r'count_cases\[\] = \{(.*?)\n\};',text,re.S)
    body = re.sub(r'(0x[0-9a-f]+|\d+)U\b',r'\1',body)
    rows = ast.literal_eval('['+body.replace('{','[').replace('}',']')+']')
    assert re.findall(r'^#define COUNT_CASE_COUNT (\d+)U$',text,re.M) == ['10252']
    assert len(rows) == declared_region().cases
    assert all(len(row) == 12 and len(row[9]) == len(row[10]) == 15 and len(row[11]) == 4 for row in rows)
    return rows

def vector_contract(row):
    count,period,remainder,variant,t,product,quotient,scratch,exit_t,incoming,expected,restore = row
    assert all(type(n) is int and 0 <= n <= 65535 for n in (count,period))
    assert type(remainder) is int and 0 <= remainder < 256 and variant in (0,1) and t in (0,1)
    m = period*remainder
    q = ((m*6554) % (1 << 32))//65536
    residue = (m-10*q) % (1 << 32)
    initial = operands.seed(variant)
    initial[7] = 0x2b6ce
    saved = [0x01004567 if variant else 0x01003579,
             0xf2e4d6c8 if variant else 0x24681357,initial[8],initial[9]]
    final = initial.copy()
    if count:
        final[0] = count if count < 32768 else (count-65536) % (1 << 32)
        final[13],final[14] = saved[3],saved[2]
        observed_t = 0
    else:
        final[0],final[2],final[3] = 0x6af,q,6554
        final[4],final[5],final[6] = residue,0x010016c2,10*q
        final[7],final[11],final[13] = 0x0100166c,0xfedcba98,0x0100128c
        observed_t = int(q == 0)
    assert (product,quotient,scratch,exit_t) == (m,q,residue % 256,observed_t)
    assert incoming == initial and expected == final and restore == saved

def chain_contract(model):
    chain = model.entities[('chain','injection_phase')]
    assert len(chain.steps) == 22
    step = publication.normalized(model,chain.steps[17])
    for field,value in {'from':'nippy-caribou/ram','to':'amphibian-panda/ram',
                        'effect':'converts','sign':'none',
                        'via':['amigurumi-dormouse/fn',PROG],
                        'specs':[publication.SPEC]}.items():
        assert step[field] == value

def owner_contract(model):
    symbol = publication.required_owner(model,COUNT,0xffff13b8).symbols['7mfk']
    assert symbol.value('width') == 16 and symbol.value('signed') is False
    publication.required_evidence(model,symbol.evidence,evidence())
    publication.required_evidence(model,publication.required_owner(model,PROG,0x2b64a).symbols['7mfk'].evidence,evidence())
    matches = [link for link in operands.owner(model,COUNT).links if link.type == 'reader' and link.to.key == PROG]
    assert len(matches) == 1
    [reader] = matches
    assert reader.slot is None and reader.offset is None and reader.stated == {'7mfk'}
    assert publication.normalized(model,reader.props['via']) == [PROG]
    assert reader.props['relies'] == 'structure' and reader.props['supports'] == 'identity'
    publication.required_evidence(model,reader.evidence,evidence())
    chain_contract(model)

def invocation_contract(text):
    assert set(OBSERVER) == {'SETUP','RETURNS','OLD_SP','ACTUAL_SP','POINTER'}
    for key in ('SETUP','RETURNS','ACTUAL_SP','POINTER'):
        assert text.count(OBSERVER[key]) == 1
    normalized = text.replace(OBSERVER['SETUP'],'',1)
    normalized = normalized.replace(OBSERVER['RETURNS'],'L_injection_count_stock_return:\n',1)
    normalized = normalized.replace(OBSERVER['ACTUAL_SP'],OBSERVER['OLD_SP'],1)
    normalized = normalized.replace('\n'+OBSERVER['POINTER'],'',1)
    assert normalized.count('    add #-128,r15\n') == normalized.count('    add #96,r15\n') == 1
    normalized = normalized.replace('    add #-128,r15\n','    add #-120,r15\n',1)
    normalized = normalized.replace('    add #96,r15\n','    add #88,r15\n',1)
    normalized = normalized.replace('injection_count','injection_start_delay')
    assert normalized == (TOOL_DIR/'stock_injection_start_delay_invoke.s').read_text()

def publication_contract(text):
    region = region_contract(publication.stock_module())
    instructions = (region.end-region.start+sum(end-start for start,end in region.callees))//2
    bound = 2*instructions+sum(size for _,size in region.pools)
    for pattern,value in ((r'\b(\d+) instructions\b',instructions),
                          (r'\b(\d+) bound bytes\b',bound),
                          (r'\b(\d+) literal cases\b',len(literals()))):
        claims = re.findall(pattern,text)
        assert claims and all(int(claim) == value for claim in claims)
    for phrase in ('EARLY_ONLY=0','all fifteen GPRs','actual complete SR','92-byte','96 frame bytes',
                   '64k RAM','hardware','0002b6f8','before MMIO','SP+20','saved-frame','prologue'):
        assert phrase in text

def test_injection_count_registered_stock_contract(jk08a_stock_bytes):
    module = publication.stock_module()
    region = region_contract(module)
    stock_contract(jk08a_stock_bytes)
    defines = module.harness_defines(region,jk08a_stock_bytes)
    assert {name:defines[name] for name in ('COUNT','PERIOD','REMAINDER','OUTPUT','SCRATCH','EARLY_ONLY')} == {
        'COUNT':0xffff13b8,'PERIOD':0xffff22bc,'REMAINDER':0xffff193b,
        'OUTPUT':0xffff16c2,'SCRATCH':0xffff166c,'EARLY_ONLY':0}
    fixture = module.build_fixture(region,jk08a_stock_bytes)
    for start,end in ((region.start,region.end),*region.callees):
        assert fixture[start:end] == jk08a_stock_bytes[start:end]
    assert fixture[region.end:region.end+8] == module.return_stub(region)
    for address in region.ram_literals:
        original = int.from_bytes(jk08a_stock_bytes[address:address+4],'big')
        assert int.from_bytes(fixture[address:address+4],'big') == 0x01000000+(original & 65535)

def test_injection_count_owner_contract():
    owner_contract(compile.cached(repo.ROOT))

@pytest.mark.parametrize('field',('width','signed'))
def test_injection_count_refuses_wrong_storage_width_and_sign(field):
    model = compile.cached(repo.ROOT)
    changed = operands.clone_owner(operands.owner(model,COUNT))
    changed.symbols['7mfk'].props[field] = 32 if field == 'width' else True
    with pytest.raises(AssertionError): owner_contract(dispatch.proxy(model,changed))

@pytest.mark.parametrize('kind',('missing','via','offset','layout','evidence'))
def test_injection_count_refuses_unbound_count_reader(kind):
    model = compile.cached(repo.ROOT)
    changed = operands.clone_owner(operands.owner(model,COUNT))
    [reader] = [link for link in changed.links if link.type == 'reader' and link.to.key == PROG]
    if kind == 'missing': changed.links.remove(reader)
    elif kind == 'via': reader.props['via'] = []
    elif kind == 'offset': reader.offset = 1
    elif kind == 'layout': reader.stated = {'jk78c'}
    else: reader.evidence = []
    with pytest.raises(AssertionError): owner_contract(dispatch.proxy(model,changed))

@pytest.mark.parametrize('field',('from','to','effect','sign','via','specs'))
def test_injection_count_refuses_changed_bounded_chain_description(field):
    model = compile.cached(repo.ROOT)
    chain = model.entities[('chain','injection_phase')]
    steps = copy.deepcopy(chain.steps)
    steps[17][field] = [] if field in ('via','specs') else ''
    changed = replace(chain,steps=steps)
    proxy = SimpleNamespace(entities={**model.entities,('chain','injection_phase'):changed},meaning_of=model.meaning_of)
    with pytest.raises(AssertionError): chain_contract(proxy)

def test_injection_count_all_literals_bind_complete_registers_and_saved_state():
    for row in literals(): vector_contract(row)

@pytest.mark.parametrize('register',range(15))
@pytest.mark.parametrize('case',(0,1))
def test_injection_count_refuses_each_changed_exit_register(register,case):
    row = copy.deepcopy(literals()[case])
    row[10][register] ^= 1
    with pytest.raises(AssertionError): vector_contract(row)

@pytest.mark.parametrize('field',range(5,12))
def test_injection_count_refuses_each_changed_observation(field):
    row = copy.deepcopy(literals()[0])
    if field >= 9: row[field][0] ^= 1
    else: row[field] ^= 1
    with pytest.raises(AssertionError): vector_contract(row)

@pytest.mark.parametrize('address',[address+i for address,span in SLICES for i in range(len(span))])
def test_injection_count_rejects_every_changed_bound_byte(jk08a_stock_bytes,address):
    changed = bytearray(jk08a_stock_bytes)
    changed[address] ^= 1
    with pytest.raises(AssertionError): stock_contract(changed)

@pytest.mark.parametrize('kind',('missing','duplicate','cases','boolean','boundary','ram','span','pools','symbols','early','return','callees'))
def test_injection_count_refuses_incomplete_or_changed_region(kind):
    region = declared_region()
    changes = {'cases':{'cases':12},'boolean':{'cases':True},'boundary':{'boundary':False},
               'ram':{'ram_literals':()},'span':{'end':0x2b6f6},'pools':{'pools':()},
               'symbols':{'symbols':()},'early':{'constants':(('EARLY_ONLY',1),)},
               'return':{'return_address_offset':None},'callees':{'callees':()}}
    rows = [] if kind == 'missing' else [region,region] if kind == 'duplicate' else [replace(region,**changes[kind])]
    with pytest.raises(AssertionError): region_contract(SimpleNamespace(REGIONS=rows))

def test_injection_count_complete_count_period_and_remainder_byte_domains():
    rows = literals()
    for high in (0,1,128,255):
        assert {row[0] & 255 for row in rows if row[0] >> 8 == high} == set(range(256))
        assert {row[1] & 255 for row in rows if row[1] >> 8 == high and row[0] == 0} == set(range(256))
    for low in (0,1,128,255):
        assert {row[0] >> 8 for row in rows if row[0] & 255 == low} == set(range(256))
    for period in (8192,65535):
        assert {row[2] for row in rows if row[0] == 0 and row[1] == period} == set(range(256))
    assert {row[8] for row in rows} == {0,1} and {row[4] for row in rows} == {0,1}
    assert any(row[0] >= 32768 for row in rows)

@pytest.mark.parametrize('path',(publication.SPEC,'tools/sh-elf-run/README.md'))
def test_injection_count_publication_binds_executed_counts(path):
    publication_contract(publication.section(path,SECTION))

@pytest.mark.parametrize('claim',('43 instructions','109 bound bytes','10251 literal cases'))
def test_injection_count_rejects_conflicting_published_counts(claim):
    with pytest.raises(AssertionError): publication_contract(publication.section(publication.SPEC,SECTION)+'\n'+claim)

def test_injection_count_execution_sources_and_complete_invocation_are_exact():
    assert len(EXECUTION_SOURCES) == 6
    for path,digest in EXECUTION_SOURCES.items():
        assert hashlib.sha256((TOOL_DIR/path).read_bytes()).hexdigest() == digest
    invocation_contract((TOOL_DIR/'stock_injection_count_invoke.s').read_text())
    assert (TOOL_DIR/'stock_invoke.s').read_text().count('.include "stock_injection_count_invoke.s"') == 1

@pytest.mark.parametrize('kind',('saved','pr','sp','zero','restore','frame'))
def test_injection_count_rejects_changed_staging_or_sp_observation(kind):
    text = (TOOL_DIR/'stock_injection_count_invoke.s').read_text()
    before,after = {'saved':('    mov.l r0,@(16,r15)\n','    mov.l r0,@(20,r15)\n'),
                    'pr':('L_injection_count_nonzero_pointer: .long L_injection_count_nonzero_return\n','L_injection_count_nonzero_pointer: .long 0\n'),
                    'sp':('    add #-104,r0\n','    add #-100,r0\n'),
                    'zero':('    add #-124,r0\n','    add #-120,r0\n'),
                    'restore':('    add #96,r15\n','    add #88,r15\n'),
                    'frame':('L_injection_count_frame_before:\n','L_injection_count_frame_before_changed:\n')}[kind]
    assert text.count(before) == 1
    with pytest.raises(AssertionError): invocation_contract(text.replace(before,after,1))
