"""Bind exact whole-feedback bytes, independent equations and native owners."""
import ast
from collections import Counter
from dataclasses import asdict
from functools import cache
import hashlib,json,re

from kb import compile,repo
from tools.kb.tests import test_injection_start_delay_chain as publication
from tools.kb.tests.closed_loop_publication_contract import evaluate
from tools.kb.tests.closed_loop_feedback_model import Memory,byte_curve
from tools.kb.tests.closed_loop_feedback_frame import expectations,semantic_trace
from tools.kb.tests.closed_loop_feedback_terminal import expectations as cpu_expectations
from tools.kb.tests.closed_loop_feedback_selection import selected_source,source_equation

TOOL=repo.ROOT/'tools/sh-elf-run'
SPEC='defs/JK08A.closed-loop-feedback.md'
HEADER='stock-jk08a-closed-loop-feedback-cases.h'

@cache
def contracts():
    value=json.loads((TOOL/'closed-loop-feedback-contracts.json').read_text())
    assert value['hardware_ready'] is False and value['changed_steps']==[8]
    return value

def owner_contract(model=None):
    model=compile.cached(repo.ROOT) if model is None else model
    for ref,expected in contracts()['owner_contracts'].items():
        owner=publication.required_owner(model,ref,int(expected['address'],16))
        symbol=owner.symbols['7mfk']
        publication.required_properties(model,owner.props,expected['props'])
        publication.required_properties(model,symbol.props,expected['symbol_props'])
        assert symbol.value('level')==expected['level']
        publication.required_evidence(model,symbol.evidence,expected['evidence'])
        for wanted in expected['links']:
            matches=[link for link in owner.links if (link.type,link.to.key,link.slot,link.offset)==
                (wanted['type'],wanted['to'],wanted['slot'],wanted['offset'])]
            assert len(matches)==1
            [link]=matches
            assert link.stated>=set(wanted['layouts']) and link.roles>=set(wanted['roles'])
            publication.required_properties(model,link.props,wanted['props'])
            publication.required_evidence(model,link.evidence,wanted['evidence'])
    chain=model.entities[('chain','closed_loop_fuel')]
    assert len(chain.steps)==19
    assert publication.normalized(model,chain.steps[7])==contracts()['step']
    assert chain.steps[7]['sign']=='none'
    for number,wanted in contracts()['held_steps'].items():
        assert publication.normalized(model,chain.steps[int(number)-1])==wanted

def region():
    module=publication.stock_module()
    matches=[row for row in module.REGIONS if row.key=='jk08a-closed-loop-feedback']
    assert len(matches)==1
    [row]=matches
    assert json.loads(json.dumps(asdict(row)))==contracts()['region']
    assert module.REGION_OBSERVERS[row.key]==contracts()['observer']
    return row,module

def stock_bytes(image):
    for at,raw in contracts()['slices']:
        data=bytes.fromhex(raw)
        assert image[at:at+len(data)]==data,f'{at:08x}'

def registered_stock_contract(image):
    row,module=region()
    stock_bytes(image)
    for name,digest in contracts()['sources_sha256'].items():
        assert hashlib.sha256((repo.ROOT/name).read_bytes()).hexdigest()==digest,name
    assert hashlib.sha256(module.build_fixture(row,image)).hexdigest()==contracts()['fixture_sha256']
    assert sum((end-at)//2 for at,end in row.code_spans)==3067
    assert sum(end-at for at,end in row.code_spans)+sum(size for at,size in row.pools)==63998
    assert row.cases==1829 and len(row.ram_literals)==43 and len(row.ram_word_literals)==17
    assert not row.boundary and not row.register_word_literals and not row.constants
    assert (row.return_address_offset,row.return_register)==(None,5)
    assert all(alias-original==0x5ffc-0xffff88b0 for _,original,alias,size in row.ram_word_literals)
    assert min(original for _,original,_,_ in row.ram_word_literals)==0xffff88b0
    assert max(original+size for _,original,_,size in row.ram_word_literals)==0xffff89de

def previous_regions_contract():
    module=publication.stock_module()
    assert len(module.REGIONS)>=81 and len(contracts()['previous_regions'])==78
    assert json.loads(json.dumps([asdict(row) for row in module.REGIONS[:78]]))==contracts()['previous_regions']
    for key,name in contracts()['previous_observers'].items(): assert module.REGION_OBSERVERS[key]==name
    images={rom:module.stock_image(rom) for rom in {row.rom for row in module.REGIONS[:78]}}
    for row in module.REGIONS[:78]:
        assert hashlib.sha256(module.build_fixture(row,images[row.rom])).hexdigest()==contracts()['previous_fixtures'][row.key]

def all_bound_mutations_fail(image):
    original=bytearray(image)
    for at,raw in contracts()['slices']:
        for offset in range(len(bytes.fromhex(raw))):
            original[at+offset]^=1
            try: stock_bytes(original)
            except AssertionError: pass
            else: raise AssertionError(f'feedback accepts changed byte {at+offset:08x}')
            finally: original[at+offset]^=1

def publication_contract():
    row,_=region()
    text=re.sub(r'\s+',' ',(repo.ROOT/SPEC).read_text())
    assert f'One mandatory Region binds 3067 instructions, 63998 bound bytes and {row.cases} literal cases' in text
    for phrase in ('Hardware readiness is NO','352-byte','308 bytes','Seventeen word pointers',
        'Forty-three declared long RAM pointers','3658 bank observations','full Cartesian product',
        'Physical units','event cadence','x=0','x=1','max(ROM16[00008fc4],min(ROM16[00008fc6],selected))'):
        assert phrase in text,phrase
    assert 'jk08a-closed-loop-feedback' in (repo.ROOT/'tools/sh-elf-run/README.md').read_text()

@cache
def array(name):
    text=(TOOL/HEADER).read_text()
    [body]=re.findall(r'\b'+name+r'\[\]\s*=\s*\{(.*?)\};',text,re.S)
    assert re.fullmatch(r'[\s{},0-9a-fxU]+',body)
    body=re.sub(r'(0x[0-9a-f]+|\d+)U\b',r'\1',body)
    return ast.literal_eval('['+body.replace('{','[').replace('}',']')+']')

def literals(): return array('memory_samples'),array('cpu_samples')

def initial_ram(index,row,inputs):
    zero,begin,count,_,_,workspace=row
    assert zero in (0,1) and len(workspace)==302 and begin>=0 and count>=0
    ram=bytearray(65536) if zero else bytearray((0x51+29*i+(i>>8)+index)&255 for i in range(65536))
    changes=inputs[begin:begin+count]
    assert len(changes)==count and len({at for at,_ in changes})==count
    assert changes==sorted(changes)
    for at,value in changes:
        assert 0<=at<65536 and value in range(256)
        ram[at]=value
    return ram

def literal_contract(rows=None,cpu_rows=None):
    memory,cpu=literals()
    rows=memory if rows is None else rows
    cpu_rows=cpu if cpu_rows is None else cpu_rows
    assert len(rows)==len(cpu_rows)==1829
    inputs,outputs=array('inputs'),array('outputs')
    module=publication.stock_module();image=module.stock_image('JK08A')
    outcomes=Counter()
    for index,(row,cpu_row) in enumerate(zip(rows,cpu_rows)):
        ram=initial_ram(index,row,inputs)
        observed=expectations(ram,image,index)
        result=observed['result']
        expected=bytearray(ram)
        changes=outputs[row[3]:row[3]+row[4]]
        assert len(changes)==row[4] and changes==sorted(changes)
        assert len({at for at,_ in changes})==len(changes)
        for at,value in changes:
            assert at not in range(0x88b0,0x89de) and value in range(256)
            expected[at]=value
        assert expected[:0x88b0]==result[:0x88b0] and expected[0x89de:]==result[0x89de:]
        assert expected[0x88b0:0x89de]==ram[0x88b0:0x89de]
        assert row[5]==list(result[0x88b0:0x89de])
        terminal=cpu_expectations(result)
        assert cpu_row==[[terminal['r'+str(i)] for i in range(8)],terminal['exit_q'],observed['frame']]
        assert observed['fixups']==[dict(at=288,source='continuation')]
        assert observed['frame'][162]==ram[0x11bc]
        for bank in range(2):
            selected=source_equation(ram,result,image,bank)
            assert selected['output']==Memory(result,image).w(0xffff40ac+2*bank)
            outcomes[selected_source(ram,result,image,bank)]+=1
    assert dict(outcomes)==contracts()['outcomes']

def formula_observation(formula,ram,result,trace,image,bank):
    old,new=Memory(ram,image),Memory(result,image)
    before=Memory(trace['transition']['before'],image)
    ram8={0xffff8964:new.b(0xffff8964),0xffff88cd:before.b(0xffff88cd),
        0xffff14c1:old.b(0xffff14c1),0xffff88ec:old.b(0xffff88ec)}
    ram16={at:old.w(at) for at in (0xffff11bc,0xffff22e8,0xffff15da,0xffff88b4,0xffff88b6)}
    ram16[0xffff8920]=new.w(0xffff8920)
    for b in range(2):
        for base in (0xffff88be,0xffff89da,0xffff89dc,0xffff8967,0xffff8965,0xffff8969):ram8[base+b]=new.b(base+b)
        ram8[0xffff88c0+b]=before.b(0xffff88c0+b)
        for base in (0xffff88b8,0xffff28b8,0xffff88b0):ram16[base+2*b]=old.w(base+2*b)
        for base in (0xffff8926,0xffff2898,0xffff8922,0xffff1628,0xffff2a1e):ram16[base+2*b]=new.w(base+2*b)
    def lookup(table,coordinate):
        assert table==0x23752
        return byte_curve(old,table,0x2374a,coordinate,8)
    env=evaluate(formula,source=old.w(0xffff29e2+2*bank),x=bank,RAM8=ram8,RAM16=ram16,
        ROM8={0x8822:old.b(0x8822)},ROM16={at:old.w(at) for at in (0x92ee,0x92f0,0x8fc4,0x8fc6)},lookup=lookup)
    assert env['T']==min(1,new.b(0xffff8958+bank))
    wanted=source_equation(ram,result,image,bank)
    assert (env['W'],env['to'])==(wanted['raw'],wanted['output'])
    assert env['to']==new.w(0xffff40ac+2*bank)

def formula_contract(model=None,formula=None):
    model=compile.cached(repo.ROOT) if model is None else model
    note=model.entities[('chain','closed_loop_fuel')].steps[7]['note']
    formula=note if formula is None else formula
    assert note==contracts()['formula']
    rows,_=literals();image=publication.stock_module().stock_image('JK08A');inputs=array('inputs')
    for index,row in enumerate(rows):
        ram=initial_ram(index,row,inputs);result,trace=semantic_trace(ram,image)
        for bank in range(2):formula_observation(formula,ram,result,trace,image,bank)
