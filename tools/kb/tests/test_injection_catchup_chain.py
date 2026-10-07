"""Bind the bounded injection catch-up loop to complete literal observations."""
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

TOOL_DIR=repo.ROOT/'tools/sh-elf-run'
PATH='tools/kb/tests/test_injection_catchup_chain.py'
SECTION='Bounded injection positive-delta mask accumulation'
SEQ='amigurumi-dormouse/fn'
CURSOR='lurking-swine/ram'
OWNERS=((CURSOR,0xffff221e),('curvy-hyena/ram',0xffff20b5),
        ('quantum-tiger/ram',0xffff1935),('injection_catchup_mask_a/ram',0xffff157e),
        ('injection_catchup_mask_b/ram',0xffff16fe))
NEW=('injection_catchup_mask_a/ram','injection_catchup_mask_b/ram')
SLICES=((347220, b"jl\xeb\x00J\x15\x1f\xb3f\xb3\x8f3\x1f\xb4\xd3\x8a\x90\xab\xd2\x8a\x0c<\xc4\xc1/\x92\xe9\x06g\x03\x90\xa5\r,\x90\xa4\x0e,\x90\xa3\x04,\xd3\x83|\x01\x90\x9c\x03\xc4l\xcc<\x93\x8b\x02\xd3\x7f\xec\x00\x03\xc4b\x83r\x07l\xcc`\xc3\x05,{\x01b\\;\xa3&+bg\x1fd'k-k$)\x8f\xe6.k\xd2w\x90\x86\x1f\xb3\x02D\x90\x82i\xf2\x02\xe4\x90~\x02\xd4`s\xc0\xc1"), (140949, b'\x02\x04\x08\x10 \x01'), (347582, b'\x02*\x02\xf2\x04r\x06\xa9'), (347788, b'\xff\xff\x1f\xf4\xff\xff\x12\x8c'))
EXECUTION_SOURCES={'stock_jk08a_injection_catchup.s': 'e22a590f0a105d5538461f3d72eaa4effe6b6e715b3f752aeb3464cbde05807a', 'injection-catchup-cases.h': '47abc4248d5370def7122724702cfda8d76e6af2fdd2e67cfc5e4db85b04e22f', 'harness-stock-jk08a-injection-catchup.c': '7020aab382fb9336804ba98523622ffdf65d2246f16cbbc853bc25c7e13ba431', 'stock_injection_start_delay_invoke.s': '0e60c06fb860bfccde3e166f1d45e4059994026ccd89db9313a5b6d0757d44db'}

def evidence():
    return [{'kind':'test','path':PATH,'key':'test_injection_catchup_owner_contract'},
            {'kind':'test','path':PATH,'key':'test_injection_catchup_registered_stock_contract'},
            {'kind':'spec','path':publication.SPEC,'key':SECTION}]

def declared_region():
    return publication.stock_module().Region(key='jk08a-injection-catchup',rom='JK08A',
        source='stock_jk08a_injection_catchup.s',harness='harness-stock-jk08a-injection-catchup.c',
        start=0x54c54,end=0x54cc8,pools=((0x22695,6),(0x54dbe,8),(0x54e8c,8)),
        ram_literals=(0x54e8c,0x54e90),cases=11340,
        symbols=(('CURSOR',CURSOR),('QUEUE','curvy-hyena/ram'),('CLEAR','quantum-tiger/ram'),
                 ('MASK_A',NEW[0]),('MASK_B',NEW[1])),constants=(('EARLY_ONLY',0),))

def region_contract(module):
    expected=declared_region()
    matches=[region for region in module.REGIONS if region.key==expected.key]
    assert len(matches)==1, 'The mandatory bounded catch-up Region is absent or duplicated'
    [region]=matches
    assert region==expected and type(region.cases) is int
    return region

def stock_contract(data):
    for address,expected in SLICES:
        assert data[address:address+len(expected)]==expected,f'{address:08x}'
    region=declared_region()
    for address in range(region.start,region.end,2):
        instruction=sh2.decode(int.from_bytes(data[address:address+2],'big'),address)
        if instruction.flow=='branch':
            assert instruction.target==region.end or region.start<=instruction.target<region.end
    assert data[0x22695:0x2269b]==bytes((2,4,8,16,32,1))
    word=lambda at:int.from_bytes(data[at:at+2],'big')
    assert word(0x54c5e)==0x8f33 and word(0x54c60)==0x1fb4
    assert word(0x54cae)==0x8fe6 and word(0x54cb0)==0x2e6b
    base=int.from_bytes(data[0x54e90:0x54e94],'big')
    assert [base+word(at) for at in (0x54dc0,0x54dc2,0x54dc4)]==[0xffff157e,0xffff16fe,0xffff1935]

@cache
def literals():
    text=(TOOL_DIR/'injection-catchup-cases.h').read_text()
    [body]=re.findall(r'catchup_cases\[\] = \{(.*?)\n\};',text,re.S)
    body=re.sub(r'(0x[0-9a-f]+|\d+)U\b',r'\1',body)
    rows=ast.literal_eval('['+body.replace('{','[').replace('}',']')+']')
    assert re.findall(r'^#define CATCHUP_CASE_COUNT (\d+)U$',text,re.M)==['11340']
    assert len(rows)==declared_region().cases
    assert all(len(row)==11 and len(row[7])==len(row[8])==4
               and len(row[9])==len(row[10])==15 for row in rows)
    return rows

def vector_contract(row):
    cursor,delta,variant,t,final_cursor,mask,exit_t,old,state,incoming,expected=row
    assert type(cursor) is int and 0<=cursor<=255 and type(delta) is int and 0<=delta<=0xffffffff
    assert variant in (0,1) and t in (0,1)
    assert all(type(value) is int and 0<=value<=255 for value in old)
    count=delta&255
    current=cursor
    accumulated=0
    table=(2,4,8,16,32,1)
    for _ in range(count):
        current=(current+1)&255
        if current>=6:current=0
        accumulated|=table[current]
    wanted=[old[0]|accumulated,old[1]|accumulated,old[2]|accumulated,old[3]&(~accumulated&255)]
    assert (final_cursor,mask,exit_t)==(current,accumulated,int(count!=0))
    assert state==wanted
    actual=operands.seed(variant)
    actual[6],actual[7],actual[8]=delta,0x54c54,0x2268e
    final=actual.copy()
    final[6],final[10],final[11]=0,count,0
    signed=lambda value:(value if value<128 else value-256)&0xffffffff
    if count:
        final[0]=signed(wanted[0])
        final[2],final[3]=0x0100128c,0x01001ff4
        final[4]=signed(old[3])&(~accumulated&0xffffffff)
        final[5],final[6]=table[current],accumulated
        final[7]=signed(old[0])|accumulated
        final[11],final[12]=count,current
        final[13]=signed(old[1])|accumulated
        final[14]=signed(old[2])|accumulated
    assert incoming==actual and expected==final

def owner_contract(model):
    for ref,address in OWNERS:
        symbol=publication.required_owner(model,ref,address).symbols['7mfk']
        assert symbol.value('width')==8 and symbol.value('signed') is False
        publication.required_evidence(model,symbol.evidence,evidence())
    symbol=publication.required_owner(model,SEQ,0x54a44).symbols['7mfk']
    publication.required_evidence(model,symbol.evidence,evidence())
    for ref in (*NEW,'curvy-hyena/ram','quantum-tiger/ram'):
        meaning=operands.owner(model,ref)
        kinds=('reader','writer','input') if ref in NEW else ('reader',)
        for kind in kinds:
            target=CURSOR if kind=='input' else SEQ
            matches=[link for link in meaning.links if link.type==kind and link.to.key==target]
            assert len(matches)==1
            [link]=matches
            assert link.slot is None and link.offset is None and link.stated=={'7mfk'}
            assert publication.normalized(model,link.props['via'])==[SEQ]
            assert link.props['relies']=='structure' and link.props['supports']=='identity'
            assert 'retain separate evidence' in link.props['note']
            publication.required_evidence(model,link.evidence,evidence())
    assert 'raw injection' in operands.owner(model,'curvy-hyena/ram').props['summary'].lower()

def proxy(model,changed):
    def meaning_of(key):
        if key==changed.symbols['7mfk'].key:return changed
        return model.meaning_of(key)
    return SimpleNamespace(meanings=[changed if item.key==changed.key else item for item in model.meanings],
                           entities=model.entities,meaning_of=meaning_of)

def publication_contract(text):
    region=region_contract(publication.stock_module())
    for pattern,value in ((r'\b(\d+) instructions\b',(region.end-region.start)//2),
                          (r'\b(\d+) bound bytes\b',region.end-region.start+sum(size for _,size in region.pools)),
                          (r'\b(\d+) literal cases\b',len(literals()))):
        claims=re.findall(pattern,text)
        assert claims and all(int(claim)==value for claim in claims)
    for phrase in ('EARLY_ONLY=0','all fifteen GPRs','actual complete SR','76-byte',
                   '96 frame bytes','64k RAM','hardware','00054cc8','SP+12','SP+16',
                   'N=uint8(R6)','ffff157e','ffff16fe','22 complete steps'):
        assert phrase in text

def test_injection_catchup_registered_stock_contract(jk08a_stock_bytes):
    module=publication.stock_module()
    region=region_contract(module)
    stock_contract(jk08a_stock_bytes)
    defines=module.harness_defines(region,jk08a_stock_bytes)
    assert {name:defines[name] for name in ('CURSOR','QUEUE','CLEAR','MASK_A','MASK_B')}=={
        'CURSOR':0xffff221e,'QUEUE':0xffff20b5,'CLEAR':0xffff1935,'MASK_A':0xffff157e,'MASK_B':0xffff16fe}
    assert defines['EARLY_ONLY']==0
    fixture=module.build_fixture(region,jk08a_stock_bytes)
    assert fixture[region.start:region.end]==jk08a_stock_bytes[region.start:region.end]
    assert fixture[region.end:region.end+4]==module.RETURN_STUB
    for address in region.ram_literals:
        original=int.from_bytes(jk08a_stock_bytes[address:address+4],'big')
        assert int.from_bytes(fixture[address:address+4],'big')==0x01000000+(original&65535)

def test_injection_catchup_owner_contract():
    owner_contract(compile.cached(repo.ROOT))

@pytest.mark.parametrize('ref,address',OWNERS)
@pytest.mark.parametrize('field',('width','signed'))
def test_injection_catchup_refuses_wrong_owner_width_and_sign(ref,address,field):
    model=compile.cached(repo.ROOT)
    changed=operands.clone_owner(operands.owner(model,ref))
    changed.symbols['7mfk'].props[field]=32 if field=='width' else True
    with pytest.raises(AssertionError):owner_contract(proxy(model,changed))

@pytest.mark.parametrize('ref',NEW)
@pytest.mark.parametrize('kind',('missing','via','offset','layout','evidence'))
def test_injection_catchup_refuses_unbound_new_writer(ref,kind):
    model=compile.cached(repo.ROOT)
    changed=operands.clone_owner(operands.owner(model,ref))
    [writer]=[link for link in changed.links if link.type=='writer' and link.to.key==SEQ]
    if kind=='missing':changed.links.remove(writer)
    elif kind=='via':writer.props['via']=[]
    elif kind=='offset':writer.offset=1
    elif kind=='layout':writer.stated={'jk78c'}
    else:writer.evidence=[]
    with pytest.raises(AssertionError):owner_contract(proxy(model,changed))

def test_injection_catchup_every_literal_binds_all_scalar_and_register_results():
    for row in literals():vector_contract(row)

@pytest.mark.parametrize('address',[address+i for address,data in SLICES for i in range(len(data))])
def test_injection_catchup_rejects_every_changed_instruction_and_pool_byte(jk08a_stock_bytes,address):
    changed=bytearray(jk08a_stock_bytes)
    changed[address]^=1
    with pytest.raises(AssertionError):stock_contract(changed)

@pytest.mark.parametrize('kind',('missing','duplicate','cases','boolean','boundary','ram','span','pools','symbols','early','return'))
def test_injection_catchup_refuses_absent_or_weakened_region(kind):
    region=declared_region()
    changes={'cases':{'cases':12},'boolean':{'cases':True},'boundary':{'boundary':False},
             'ram':{'ram_literals':()},'span':{'end':0x54cc6},'pools':{'pools':()},
             'symbols':{'symbols':()},'early':{'constants':(('EARLY_ONLY',1),)},
             'return':{'return_address_offset':24}}
    rows=[] if kind=='missing' else [region,region] if kind=='duplicate' else [replace(region,**changes[kind])]
    with pytest.raises(AssertionError):region_contract(SimpleNamespace(REGIONS=rows))

@pytest.mark.parametrize('register',range(15))
def test_injection_catchup_refuses_changed_literal_full_register(register):
    row=copy.deepcopy(literals()[0])
    row[-1][register]^=1
    with pytest.raises(AssertionError):vector_contract(row)

@pytest.mark.parametrize('field',('cursor','mask','t','state','incoming'))
def test_injection_catchup_refuses_changed_literal_observation(field):
    row=copy.deepcopy(literals()[0])
    if field in ('cursor','mask','t'):row[{'cursor':4,'mask':5,'t':6}[field]]^=1
    elif field=='state':row[8][2]^=1
    else:row[9][1]^=1
    with pytest.raises(AssertionError):vector_contract(row)

def test_injection_catchup_full_cursor_delta_and_old_mask_domains_are_present():
    rows=literals()
    assert {row[0] for row in rows}==set(range(256))
    assert {row[1]&255 for row in rows}==set(range(256))
    for cursor in range(6):assert {row[1]&255 for row in rows if row[0]==cursor}==set(range(256))
    for field in range(4):assert {row[7][field] for row in rows}==set(range(256))
    for row in rows:
        if (row[1]&255)>=6:assert row[5]==63
    assert {row[6] for row in rows}=={0,1}
    assert {row[3] for row in rows}=={0,1}
    assert any(row[1]>255 for row in rows)
    assert any(row[0]==255 and row[1]==1 and row[4]==0 and row[5]==2 for row in rows)

@pytest.mark.parametrize('path',(publication.SPEC,'tools/sh-elf-run/README.md'))
def test_injection_catchup_published_counts_bind_to_executed_inputs(path):
    publication_contract(publication.section(path,SECTION))

@pytest.mark.parametrize('claim',('59 instructions','139 bound bytes','11339 literal cases'))
def test_injection_catchup_refuses_contradictory_published_counts(claim):
    with pytest.raises(AssertionError):publication_contract(publication.section(publication.SPEC,SECTION)+'\n'+claim)

def test_injection_catchup_sources_hold_the_executed_fixtures_and_shared_invocation():
    for path,digest in EXECUTION_SOURCES.items():
        assert hashlib.sha256((TOOL_DIR/path).read_bytes()).hexdigest()==digest
