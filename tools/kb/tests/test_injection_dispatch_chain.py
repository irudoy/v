"""Bind pre-call injection argument preparation to complete executable inputs."""
import ast
import copy
from dataclasses import replace
from functools import cache
import hashlib
import re
from types import SimpleNamespace

import pytest

from kb import compile, repo, sh2
from tools.kb.tests import test_injection_start_delay_chain as publication
from tools.kb.tests import test_injection_sequencing_chain as operands

TOOL_DIR = repo.ROOT/'tools/sh-elf-run'
PATH = 'tools/kb/tests/test_injection_dispatch_chain.py'
SECTION = 'Bounded injection pre-call argument preparation'
SEQ = 'amigurumi-dormouse/fn'
LEAD = 'bizarre-axolotl/ram'
FLAG = 'shaggy-nyala/ram'
OWNERS = ((LEAD,0xffff221d),(FLAG,0xffff4251))
SLICES = ((347404, b'\xd3_\x90^\xd6b\x03\x94\x84e\xc8\x01\x89\x02\xd2a\xa0\x02\xe44T\xf2\xd2_'), (347598, b'\x02)'), (347788, b'\xff\xff\x1f\xf4'), (347804, b'\xff\xffBL\x00\x02\xb6J'))
EXECUTION_SOURCES = {'stock_jk08a_injection_dispatch.s': '0f6db66bb28fb9b69056990cbf4a0d89b7e847d10941f347f0359b986147d5a3', 'harness-stock-jk08a-injection-dispatch.c': 'fc59d2cbabcbfbeb5db83c79dfb2817684b04c67049517790e204a1bfe1f181d', 'injection-dispatch-cases.h': 'a321e51996e0caf35899a89fc81ae4208f866c8e8136cc0eb965da919885c811', 'stock_injection_dispatch_invoke.s': 'afe5c4e8ac1e73ef82994be9de3306cebe9abf01d12a0600dec79e0d5162c36c', 'stock_invoke.s': '3dc406d51859502a6a987023cdae830968444b66c4ec2eba8b93bc28c47bd4fd', 'stock_injection_start_delay_invoke.s': '0e60c06fb860bfccde3e166f1d45e4059994026ccd89db9313a5b6d0757d44db'}

def evidence():
    return [{'kind':'test','path':PATH,'key':'test_injection_dispatch_owner_contract'},
            {'kind':'test','path':PATH,'key':'test_injection_dispatch_registered_stock_contract'},
            {'kind':'spec','path':publication.SPEC,'key':SECTION}]

def declared_region():
    return publication.stock_module().Region(key='jk08a-injection-dispatch',rom='JK08A',
        source='stock_jk08a_injection_dispatch.s',harness='harness-stock-jk08a-injection-dispatch.c',
        start=0x54d0c,end=0x54d24,return_address_offset=24,return_register=11,
        pools=((0x54dce,2),(0x54e8c,4),(0x54e9c,8)),ram_literals=(0x54e8c,0x54e9c),cases=9292,
        symbols=(('LEAD',LEAD),('FLAG',FLAG)),constants=(('EARLY_ONLY',0),))

def region_contract(module):
    expected = declared_region()
    matches = [region for region in module.REGIONS if region.key == expected.key]
    assert len(matches) == 1
    [region] = matches
    assert region == expected and type(region.cases) is int
    return region

def stock_contract(data):
    assert sum(len(span) for _,span in SLICES) == 38
    for address,span in SLICES:
        assert data[address:address+len(span)] == span, f'{address:08x}'
    region = declared_region()
    for address in range(region.start,region.end,2):
        instruction = sh2.decode(int.from_bytes(data[address:address+2],'big'),address)
        if instruction.flow == 'branch':
            assert instruction.target == region.end or region.start <= instruction.target < region.end
    assert int.from_bytes(data[0x54ea0:0x54ea4],'big') == 0x2b64a
    assert int.from_bytes(data[0x54d1e:0x54d20],'big') == 0xe434

@cache
def literals():
    text = (TOOL_DIR/'injection-dispatch-cases.h').read_text()
    [body] = re.findall(r'dispatch_cases\[\] = \{(.*?)\n\};',text,re.S)
    body = re.sub(r'(0x[0-9a-f]+|\d+)U\b',r'\1',body)
    rows = ast.literal_eval('['+body.replace('{','[').replace('}',']')+']')
    assert re.findall(r'^#define DISPATCH_CASE_COUNT (\d+)U$',text,re.M) == ['9292']
    assert len(rows) == declared_region().cases
    assert all(len(row) == 11 and len(row[9]) == len(row[10]) == 15 for row in rows)
    return rows

def vector_contract(row):
    flag,word,lead,old,variant,t,selected,stored,exit_t,incoming,expected = row
    assert type(flag) is int and 0 <= flag < 256 and type(old) is int and 0 <= old < 256
    assert type(word) is int and 0 <= word <= 0xffffffff
    assert type(lead) is int and 0 <= lead <= 0xffffffff and variant in (0,1) and t in (0,1)
    chosen = word
    if flag % 2: chosen = 13 << 2
    assert (selected,stored,exit_t) == (chosen,lead % 256,int(flag % 2 == 0))
    initial = operands.seed(variant)
    initial[4], initial[7], initial[9] = word,0x54d0c,lead
    final = initial.copy()
    final[0] = flag if flag < 128 else (flag-256) % (1 << 32)
    final[2], final[3], final[4], final[6], final[11] = 0x2b64a,0x01001ff4,chosen,0x0100424c,0xfedcba98
    assert incoming == initial and expected == final

def owner_contract(model):
    for ref,address in OWNERS:
        symbol = publication.required_owner(model,ref,address).symbols['7mfk']
        assert symbol.value('width') == 8 and symbol.value('signed') is False
        publication.required_evidence(model,symbol.evidence,evidence())
    publication.required_evidence(model,publication.required_owner(model,SEQ,0x54a44).symbols['7mfk'].evidence,evidence())
    matches = [link for link in operands.owner(model,FLAG).links if link.type == 'reader' and link.to.key == SEQ]
    assert len(matches) == 1
    [reader] = matches
    assert reader.slot is None and reader.offset is None and reader.stated == {'7mfk'}
    assert publication.normalized(model,reader.props['via']) == [SEQ]
    assert reader.props['relies'] == 'structure' and reader.props['supports'] == 'identity'
    publication.required_evidence(model,reader.evidence,evidence())

def proxy(model,changed):
    def meaning_of(key):
        return changed if key == changed.symbols['7mfk'].key else model.meaning_of(key)
    return SimpleNamespace(meanings=[changed if item.key == changed.key else item for item in model.meanings],
                           entities=model.entities,meaning_of=meaning_of)

def invocation_contract(text):
    insertion = '    mov.l @(16,r3),r0\n    mov.l r0,@(8,r15)\n'
    assert text.count(insertion) == 1
    normalized = text.replace(insertion,'',1).replace('injection_dispatch','injection_start_delay')
    assert normalized == (TOOL_DIR/'stock_injection_start_delay_invoke.s').read_text()

def publication_contract(text):
    region = region_contract(publication.stock_module())
    for pattern,value in ((r'\b(\d+) instructions\b',(region.end-region.start)//2),
                          (r'\b(\d+) bound bytes\b',region.end-region.start+sum(size for _,size in region.pools)),
                          (r'\b(\d+) literal cases\b',len(literals()))):
        claims = re.findall(pattern,text)
        assert claims and all(int(claim) == value for claim in claims)
    for phrase in ('EARLY_ONLY=0','all fifteen GPRs','actual complete SR','76-byte','96 frame bytes',
                   '64k RAM','hardware','00054d24','SP+8','52','before JSR','32-bit'):
        assert phrase in text

def test_injection_dispatch_registered_stock_contract(jk08a_stock_bytes):
    module = publication.stock_module()
    region = region_contract(module)
    stock_contract(jk08a_stock_bytes)
    defines = module.harness_defines(region,jk08a_stock_bytes)
    assert defines['LEAD'] == 0xffff221d and defines['FLAG'] == 0xffff4251 and defines['EARLY_ONLY'] == 0
    fixture = module.build_fixture(region,jk08a_stock_bytes)
    assert fixture[region.start:region.end] == jk08a_stock_bytes[region.start:region.end]
    assert fixture[region.end:region.end+8] == module.return_stub(region)
    for address in region.ram_literals:
        original = int.from_bytes(jk08a_stock_bytes[address:address+4],'big')
        assert int.from_bytes(fixture[address:address+4],'big') == 0x01000000+(original & 65535)

def test_injection_dispatch_owner_contract():
    owner_contract(compile.cached(repo.ROOT))

@pytest.mark.parametrize('ref,address',OWNERS)
@pytest.mark.parametrize('field',('width','signed'))
def test_injection_dispatch_refuses_wrong_storage_width_and_sign(ref,address,field):
    model = compile.cached(repo.ROOT)
    changed = operands.clone_owner(operands.owner(model,ref))
    changed.symbols['7mfk'].props[field] = 32 if field == 'width' else True
    with pytest.raises(AssertionError): owner_contract(proxy(model,changed))

@pytest.mark.parametrize('kind',('missing','via','offset','layout','evidence'))
def test_injection_dispatch_refuses_unbound_flag_reader(kind):
    model = compile.cached(repo.ROOT)
    changed = operands.clone_owner(operands.owner(model,FLAG))
    [reader] = [link for link in changed.links if link.type == 'reader' and link.to.key == SEQ]
    if kind == 'missing': changed.links.remove(reader)
    elif kind == 'via': reader.props['via'] = []
    elif kind == 'offset': reader.offset = 1
    elif kind == 'layout': reader.stated = {'jk78c'}
    else: reader.evidence = []
    with pytest.raises(AssertionError): owner_contract(proxy(model,changed))

def test_injection_dispatch_all_literals_bind_complete_registers_and_observations():
    for row in literals(): vector_contract(row)

@pytest.mark.parametrize('register',range(15))
def test_injection_dispatch_refuses_each_changed_exit_register(register):
    row = copy.deepcopy(literals()[0])
    row[10][register] ^= 1
    with pytest.raises(AssertionError): vector_contract(row)

@pytest.mark.parametrize('field',(6,7,8,9))
def test_injection_dispatch_refuses_each_changed_observation(field):
    row = copy.deepcopy(literals()[0])
    if field == 9: row[field][1] ^= 1
    else: row[field] ^= 1
    with pytest.raises(AssertionError): vector_contract(row)

@pytest.mark.parametrize('address',[address+i for address,span in SLICES for i in range(len(span))])
def test_injection_dispatch_rejects_every_changed_bound_byte(jk08a_stock_bytes,address):
    changed = bytearray(jk08a_stock_bytes)
    changed[address] ^= 1
    with pytest.raises(AssertionError): stock_contract(changed)

@pytest.mark.parametrize('kind',('missing','duplicate','cases','boolean','boundary','ram','span','pools','symbols','early','return'))
def test_injection_dispatch_refuses_incomplete_or_changed_region(kind):
    region = declared_region()
    changes = {'cases':{'cases':12},'boolean':{'cases':True},'boundary':{'boundary':False},
               'ram':{'ram_literals':()},'span':{'end':0x54d22},'pools':{'pools':()},
               'symbols':{'symbols':()},'early':{'constants':(('EARLY_ONLY',1),)},
               'return':{'return_address_offset':None}}
    rows = [] if kind == 'missing' else [region,region] if kind == 'duplicate' else [replace(region,**changes[kind])]
    with pytest.raises(AssertionError): region_contract(SimpleNamespace(REGIONS=rows))

def test_injection_dispatch_complete_byte_flags_snapshot_words_and_lead_domains():
    rows = literals()
    assert {row[0] for row in rows} == set(range(256))
    assert {row[3] for row in rows} == set(range(256))
    assert {row[2] & 255 for row in rows} == set(range(256))
    for flag in (0,1,128,255):
        assert {row[1] for row in rows if row[0] == flag and row[1] <= 1020 and row[1] % 4 == 0} == set(range(0,1021,4))
    assert {row[8] for row in rows} == {0,1} and {row[5] for row in rows} == {0,1}
    assert any(row[1] > 1020 and row[0] & 1 == 0 and row[6] == row[1] for row in rows)

@pytest.mark.parametrize('path',(publication.SPEC,'tools/sh-elf-run/README.md'))
def test_injection_dispatch_publication_binds_executed_counts(path):
    publication_contract(publication.section(path,SECTION))

@pytest.mark.parametrize('claim',('13 instructions','39 bound bytes','9291 literal cases'))
def test_injection_dispatch_rejects_conflicting_published_counts(claim):
    with pytest.raises(AssertionError): publication_contract(publication.section(publication.SPEC,SECTION)+'\n'+claim)

def test_injection_dispatch_execution_sources_and_complete_invocation_are_exact():
    assert len(EXECUTION_SOURCES) == 6
    for path,digest in EXECUTION_SOURCES.items():
        assert hashlib.sha256((TOOL_DIR/path).read_bytes()).hexdigest() == digest
    invocation_contract((TOOL_DIR/'stock_injection_dispatch_invoke.s').read_text())
    assert (TOOL_DIR/'stock_invoke.s').read_text().count('.include "stock_injection_dispatch_invoke.s"') == 1

@pytest.mark.parametrize('kind',('missing','offset','source','frame'))
def test_injection_dispatch_rejects_changed_preparation_or_observation(kind):
    text = (TOOL_DIR/'stock_injection_dispatch_invoke.s').read_text()
    before,after = {'missing':('    mov.l r0,@(8,r15)\n',''),
                    'offset':('    mov.l r0,@(8,r15)\n','    mov.l r0,@(12,r15)\n'),
                    'source':('    mov.l @(16,r3),r0\n','    mov.l @(20,r3),r0\n'),
                    'frame':('L_injection_dispatch_frame_before:\n','L_injection_dispatch_frame_before_changed:\n')}[kind]
    assert text.count(before) == 1
    with pytest.raises(AssertionError): invocation_contract(text.replace(before,after,1))
