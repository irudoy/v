"""Bind the natural entry saves and byte operation to the original prologue."""
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
from tools.kb.tests import test_injection_sequencing_chain as operands
from tools.kb.tests import test_injection_start_delay_chain as publication

TOOL_DIR = repo.ROOT/'tools/sh-elf-run'
PATH = 'tools/kb/tests/test_injection_prologue_chain.py'
SECTION = 'Bounded injection programmer entry frame and byte flag'
PROG = 'pumpkin-peacock/fn'
CONTROL = 'provocative-anteater/ram'
SLICES = ((177738, b'/\xd6/\xe6O"O\x12O\x13\xd0\x83@\x1e\x96\x80``\xcb\x80&\x00'), (178012, b'\x84\xec'), (178276, b'\xff\xff\x12\x8c'))
EXECUTION_SOURCES = {'stock_jk08a_injection_prologue.s': '59b9f2b372f6a7621134d44d79bf15ba76a638227016fa1b614cc2dcc3347d17', 'harness-stock-jk08a-injection-prologue.c': '54cad2c68e80f63e692bcea7b28cc340b42fa08f8a31020fffc96543d7b55433', 'injection-prologue-cases.h': '94e2885329454055c61d22991a76c29b7f13b7f5a5e716c66dbc5e995d59535c', 'stock_injection_prologue_invoke.s': '736d62527412855d7c75a8bda9fbab60138652f5de01a89b6fb05e56a2153a8e', 'stock_invoke.s': '24686f13ca6d9176a80872ef2594f0ed0b812c367b9e0c6e355b86277a6fcde7', 'stock_injection_start_delay_invoke.s': '0e60c06fb860bfccde3e166f1d45e4059994026ccd89db9313a5b6d0757d44db'}
OBSERVER = {'RETURN': 'L_injection_prologue_stock_return:\n    add #124,r15\n    add #20,r15\n    mov.l r0,@r15\n    mov r15,r0\n    add #-124,r0\n    add #-20,r0\n    add #-4,r15\n    mov.l r0,@r15\n    add #-120,r15\n    mov #124,r0\n    mov.l @(r0,r15),r0\n', 'OLD_SP': '    mov r15,r0\n    add #-32,r0\n    mov.l r0,@r2\n', 'ACTUAL_SP': '    mov r15,r0\n    add #88,r0\n    mov.l @r0,r0\n    mov.l r0,@r2\n'}

def evidence():
    return [{'kind':'test','path':PATH,'key':'test_injection_prologue_owner_contract'},
            {'kind':'test','path':PATH,'key':'test_injection_prologue_registered_stock_contract'},
            {'kind':'spec','path':publication.SPEC,'key':SECTION}]

def declared_region():
    return publication.stock_module().Region(key='jk08a-injection-prologue',rom='JK08A',
        source='stock_jk08a_injection_prologue.s',harness='harness-stock-jk08a-injection-prologue.c',
        start=0x2b64a,end=0x2b660,pools=((0x2b75c,2),(0x2b864,4)),
        ram_literals=(0x2b864,),ram_word_literals=((0x2b75c,0xffff84ec,0x7f00,1),),
        cases=1036,symbols=(('CONTROL',CONTROL),),
        constants=(('EARLY_ONLY',0),('WORD_ALIAS',0x7f00)))

def region_contract(module):
    expected = declared_region()
    matches = [region for region in module.REGIONS if region.key == expected.key]
    assert len(matches) == 1
    [region] = matches
    assert region == expected and type(region.cases) is int
    return region

def stock_contract(data):
    assert sum(len(span) for _,span in SLICES) == 28
    for address,span in SLICES:
        assert data[address:address+len(span)] == span, f'{address:08x}'
    region = declared_region()
    for address in range(region.start,region.end,2):
        instruction = sh2.decode(int.from_bytes(data[address:address+2],'big'),address)
        assert instruction.flow not in ('branch','call','return')
    assert int.from_bytes(data[0x2b75c:0x2b75e],'big') | 0xffff0000 == 0xffff84ec

@cache
def literals():
    text = (TOOL_DIR/'injection-prologue-cases.h').read_text()
    [body] = re.findall(r'prologue_cases\[\] = \{(.*?)\n\};',text,re.S)
    body = re.sub(r'(0x[0-9a-f]+|\d+)U\b',r'\1',body)
    rows = ast.literal_eval('['+body.replace('{','[').replace('}',']')+']')
    assert re.findall(r'^#define PROLOGUE_CASE_COUNT (\d+)U$',text,re.M) == ['1036']
    assert len(rows) == declared_region().cases
    assert all(len(row) == 5 and len(row[3]) == len(row[4]) == 15 for row in rows)
    return rows

def vector_contract(row):
    flag,variant,t,incoming,expected = row
    assert type(flag) is int and 0 <= flag <= 255
    assert type(variant) is int and variant in (0,1) and type(t) is int and t in (0,1)
    initial = operands.seed(variant)
    initial[7] = 0x2b64a
    final = initial.copy()
    final[0] = ((flag if flag < 128 else flag-256) | 128) % (1 << 32)
    final[6] = 0x7f00
    assert incoming == initial and expected == final

def owner_contract(model):
    symbol = publication.required_owner(model,CONTROL,0xffff84ec).symbols['7mfk']
    assert symbol.value('width') == 8 and symbol.value('signed') is False
    publication.required_evidence(model,symbol.evidence,evidence())
    publication.required_evidence(model,publication.required_owner(model,PROG,0x2b64a).symbols['7mfk'].evidence,evidence())
    for kind in ('reader','writer'):
        matches = [link for link in operands.owner(model,CONTROL).links if link.type == kind and link.to.key == PROG]
        assert len(matches) == 1
        [relation] = matches
        assert relation.slot is None and relation.offset is None and relation.stated == {'7mfk'}
        assert publication.normalized(model,relation.props['via']) == [PROG]
        assert relation.props['relies'] == 'structure' and relation.props['supports'] == 'identity'
        publication.required_evidence(model,relation.evidence,evidence())

def invocation_contract(text):
    assert set(OBSERVER) == {'RETURN','OLD_SP','ACTUAL_SP'}
    assert text.count(OBSERVER['RETURN']) == text.count(OBSERVER['ACTUAL_SP']) == 1
    normalized = text.replace(OBSERVER['RETURN'],'L_injection_prologue_stock_return:\n',1)
    normalized = normalized.replace(OBSERVER['ACTUAL_SP'],OBSERVER['OLD_SP'],1)
    assert normalized.count('    add #-128,r15\n') == normalized.count('    add #96,r15\n') == 1
    normalized = normalized.replace('    add #-128,r15\n','    add #-120,r15\n',1)
    normalized = normalized.replace('    add #96,r15\n','    add #88,r15\n',1)
    normalized = normalized.replace('injection_prologue','injection_start_delay')
    assert normalized == (TOOL_DIR/'stock_injection_start_delay_invoke.s').read_text()

def publication_contract(text):
    region = region_contract(publication.stock_module())
    instructions = (region.end-region.start)//2
    bound = 2*instructions+sum(size for _,size in region.pools)
    for pattern,value in ((r'\b(\d+) instructions\b',instructions),
                          (r'\b(\d+) bound bytes\b',bound),
                          (r'\b(\d+) literal cases\b',len(literals()))):
        claims = re.findall(pattern,text)
        assert claims and all(int(claim) == value for claim in claims)
    for phrase in ('EARLY_ONLY=0','all fifteen GPRs','actual complete SR','76-byte','96 frame bytes',
                   '64k RAM','hardware','0002b660','SP-20','0002b75c','ffff84ec','0x7f00','five saved words'):
        assert phrase in text

def test_injection_prologue_registered_stock_contract(jk08a_stock_bytes):
    module = publication.stock_module()
    region = region_contract(module)
    stock_contract(jk08a_stock_bytes)
    assert module.harness_defines(region,jk08a_stock_bytes) == {
        'REGION_ENTRY':0x2b64a,'CONTROL':0xffff84ec,'EARLY_ONLY':0,'WORD_ALIAS':0x7f00}
    fixture = module.build_fixture(region,jk08a_stock_bytes)
    assert fixture[region.start:region.end] == jk08a_stock_bytes[region.start:region.end]
    assert fixture[region.end:region.end+4] == module.return_stub(region)
    expected = bytearray(jk08a_stock_bytes)
    expected[0x2b75c:0x2b75e] = bytes.fromhex('7f00')
    expected[0x2b864:0x2b868] = bytes.fromhex('0100128c')
    expected[region.end:region.end+4] = module.return_stub(region)
    assert fixture == expected

def test_injection_prologue_owner_contract():
    owner_contract(compile.cached(repo.ROOT))

@pytest.mark.parametrize('field',('width','signed'))
def test_injection_prologue_refuses_wrong_storage_width_and_sign(field):
    model = compile.cached(repo.ROOT)
    changed = operands.clone_owner(operands.owner(model,CONTROL))
    changed.symbols['7mfk'].props[field] = 16 if field == 'width' else True
    with pytest.raises(AssertionError): owner_contract(dispatch.proxy(model,changed))

@pytest.mark.parametrize('relation',('reader','writer'))
@pytest.mark.parametrize('kind',('missing','via','offset','layout','evidence'))
def test_injection_prologue_refuses_unbound_control_access(relation,kind):
    model = compile.cached(repo.ROOT)
    changed = operands.clone_owner(operands.owner(model,CONTROL))
    [link] = [link for link in changed.links if link.type == relation and link.to.key == PROG]
    if kind == 'missing': changed.links.remove(link)
    elif kind == 'via': link.props['via'] = []
    elif kind == 'offset': link.offset = 1
    elif kind == 'layout': link.stated = {'jk78c'}
    else: link.evidence = []
    with pytest.raises(AssertionError): owner_contract(dispatch.proxy(model,changed))

def test_injection_prologue_all_literals_bind_complete_registers():
    for row in literals(): vector_contract(row)
    assert len(literals()[12:]) == 1024
    assert {(row[0],row[1],row[2]) for row in literals()[12:]} == {
        (flag,variant,t) for flag in range(256) for variant in range(2) for t in range(2)}

@pytest.mark.parametrize('register',range(15))
@pytest.mark.parametrize('case',(0,3))
def test_injection_prologue_refuses_each_changed_exit_register(register,case):
    row = copy.deepcopy(literals()[case])
    row[4][register] ^= 1
    with pytest.raises(AssertionError): vector_contract(row)

@pytest.mark.parametrize('field',range(5))
def test_injection_prologue_refuses_changed_input_context(field):
    row = copy.deepcopy(literals()[0])
    if field >= 3: row[field][0] ^= 1
    else: row[field] = 256
    with pytest.raises(AssertionError): vector_contract(row)

@pytest.mark.parametrize('address',[address+i for address,span in SLICES for i in range(len(span))])
def test_injection_prologue_rejects_every_changed_bound_byte(jk08a_stock_bytes,address):
    changed = bytearray(jk08a_stock_bytes)
    changed[address] ^= 1
    with pytest.raises(AssertionError): stock_contract(changed)

@pytest.mark.parametrize('kind',('missing','duplicate','cases','boolean','boundary','ram','span','pools','symbols','early','word','return','callees'))
def test_injection_prologue_refuses_incomplete_or_changed_region(kind):
    region = declared_region()
    changes = {'cases':{'cases':12},'boolean':{'cases':True},'boundary':{'boundary':False},
               'ram':{'ram_literals':()},'span':{'end':0x2b65e},'pools':{'pools':()},
               'symbols':{'symbols':()},'early':{'constants':(('EARLY_ONLY',1),('WORD_ALIAS',0x7f00))},
               'word':{'ram_word_literals':()},'return':{'return_address_offset':0},'callees':{'callees':((0x2b660,0x2b662),)}}
    rows = [] if kind == 'missing' else [region,region] if kind == 'duplicate' else [replace(region,**changes[kind])]
    with pytest.raises(AssertionError): region_contract(SimpleNamespace(REGIONS=rows))

@pytest.mark.parametrize('path',(publication.SPEC,'tools/sh-elf-run/README.md'))
def test_injection_prologue_publication_binds_executed_counts(path):
    publication_contract(publication.section(path,SECTION))

@pytest.mark.parametrize('claim',('10 instructions','29 bound bytes','1035 literal cases'))
def test_injection_prologue_rejects_conflicting_published_counts(claim):
    with pytest.raises(AssertionError): publication_contract(publication.section(publication.SPEC,SECTION)+'\n'+claim)

def test_injection_prologue_execution_sources_and_complete_invocation_are_exact():
    assert len(EXECUTION_SOURCES) == 6
    for path,digest in EXECUTION_SOURCES.items():
        assert hashlib.sha256((TOOL_DIR/path).read_bytes()).hexdigest() == digest
    invocation_contract((TOOL_DIR/'stock_injection_prologue_invoke.s').read_text())
    assert (TOOL_DIR/'stock_invoke.s').read_text().count('.include "stock_injection_prologue_invoke.s"') == 1

@pytest.mark.parametrize('kind',('sp','compensation','restore','frame'))
def test_injection_prologue_rejects_changed_sp_observation(kind):
    text = (TOOL_DIR/'stock_injection_prologue_invoke.s').read_text()
    before,after = {'sp':('    add #-20,r0\n','    add #-16,r0\n'),
                    'compensation':('    add #20,r15\n','    add #16,r15\n'),
                    'restore':('    add #96,r15\n','    add #88,r15\n'),
                    'frame':('L_injection_prologue_frame_before:\n','L_injection_prologue_frame_before_changed:\n')}[kind]
    assert text.count(before) == 1
    with pytest.raises(AssertionError): invocation_contract(text.replace(before,after,1))
