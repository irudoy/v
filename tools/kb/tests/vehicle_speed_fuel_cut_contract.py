"""Bind bounded vehicle state arithmetic to exact stock bytes and native owners."""
from dataclasses import asdict
from functools import cache
import hashlib, json, re
from kb import compile, repo
from kb.arithmetic import Grammar
from tools.kb.tests import test_injection_start_delay_chain as publication
from tools.kb.tests import vehicle_speed_fuel_cut_equations as equations

TOOL = repo.ROOT/'tools/sh-elf-run'
SPEC = 'defs/JK08A.vehicle-speed-fuel-cut.md'
KEY = 'jk08a-vehicle-speed-fuel-cut'

@cache
def contracts():
    value = json.loads((TOOL/'vehicle-speed-fuel-cut-contracts.json').read_text())
    assert value['changed_steps'] == [18] and value['hardware_ready'] is False
    return value

def owner_contract(model=None):
    model = compile.cached(repo.ROOT) if model is None else model
    for ref,wanted in contracts()['owner_contracts'].items():
        owner = publication.required_owner(model,ref,int(wanted['address'],16))
        symbol = owner.symbols['7mfk']
        publication.required_properties(model,owner.props,wanted['props'])
        publication.required_properties(model,symbol.props,wanted['symbol_props'])
        assert symbol.value('level') == wanted['level']
        publication.required_evidence(model,symbol.evidence,wanted['evidence'])
        for expected in wanted['links']:
            links = [link for link in owner.links if (link.type,link.to.key,link.slot,link.offset) ==
                (expected['type'],expected['to'],expected['slot'],expected['offset'])]
            assert len(links) == 1
            [link] = links
            assert link.stated >= set(expected['layouts']) and link.roles >= set(expected['roles'])
            publication.required_properties(model,link.props,expected['props'])
            publication.required_evidence(model,link.evidence,expected['evidence'])
    chain = model.entities[('chain','fuel_cut')]
    assert len(chain.steps) == 25
    for number,wanted in contracts()['steps'].items():
        assert publication.normalized(model,chain.steps[int(number)-1]) == wanted
        assert wanted['sign'] == 'none' and Grammar(repo.config()).validate(wanted['note']) is None
    for number,wanted in contracts()['held_steps'].items():
        assert publication.normalized(model,chain.steps[int(number)-1]) == wanted

def registered_stock_contract(image):
    stock = publication.stock_module()
    [region] = [row for row in stock.REGIONS if row.key == KEY]
    assert json.loads(json.dumps(asdict(region))) == contracts()['region']
    assert stock.REGION_OBSERVERS[KEY] == contracts()['observer']
    assert hashlib.sha256(stock.build_fixture(region,image)).hexdigest() == contracts()['fixture_sha256']
    assert region.boundary is False and dict(region.constants)['EARLY_ONLY'] == 0
    assert region.cases == len(equations.model.matrix())
    assert region.ram_literals == (0x4f1fc,0x4f224,0x4f454)
    assert region.ram_word_literals == region.register_word_literals == ()
    for path,digest in contracts()['sources_sha256'].items():
        assert hashlib.sha256((repo.ROOT/path).read_bytes()).hexdigest() == digest,path

def earlier_region_contract():
    stock = publication.stock_module()
    earlier = [row for row in stock.REGIONS if row.key != KEY]
    assert len(earlier) == 80
    assert json.loads(json.dumps([asdict(row) for row in earlier])) == contracts()['held_regions']
    assert {key:value for key,value in stock.REGION_OBSERVERS.items() if key != KEY} == contracts()['held_observers']
    for row in earlier:
        assert hashlib.sha256(stock.build_fixture(row,stock.stock_image(row.rom))).hexdigest() == contracts()['held_fixtures'][row.key]

def literal_contract():
    assert equations.model.header(equations.model.matrix()) == (TOOL/'vehicle-fuel-cut-cases.h').read_text()

def equation_contract(model=None,formula=None):
    model = compile.cached(repo.ROOT) if model is None else model
    actual = model.entities[('chain','fuel_cut')].steps[17]['note']
    assert actual == contracts()['formula'] == equations.FORMULA
    assert equations.verify(actual if formula is None else formula) == len(equations.model.matrix())

def publication_contract():
    stock = publication.stock_module()
    [region] = [row for row in stock.REGIONS if row.key == KEY]
    code = sum(end-start for start,end in region.code_spans)
    counts = (code//2,code+sum(size for _,size in region.pools),region.cases)
    assert counts == tuple(contracts()['counts']) == (63,153,12544)
    for path in (SPEC,'tools/sh-elf-run/README.md'):
        text = re.sub(r'\s+',' ',(repo.ROOT/path).read_text().split('## Vehicle-speed fuel-cut state',1)[1])
        assert f'The bounded entry 0004f19c binds {counts[0]} stock instructions and {counts[1]} bytes' in text
        assert f'The literal matrix has {counts[2]} independent contexts' in text
        for phrase in ('Hardware readiness is NO','does not decrement','already armed','SR/MQT','64 KiB','00008caf','12544'):
            assert phrase in text,phrase

def bound_byte_contract(image):
    stock = publication.stock_module()
    [region] = [row for row in stock.REGIONS if row.key == KEY]
    addresses = [address for start,end in region.code_spans for address in range(start,end)]
    addresses += [address for start,size in region.pools for address in range(start,start+size)]
    assert len(addresses) == len(set(addresses)) == 153
    for address in addresses:
        changed = bytearray(image);changed[address] ^= 1
        try:
            fixture = stock.build_fixture(region,bytes(changed))
        except (stock.VerificationError,stock.base_verifier.VerificationError):
            continue
        assert hashlib.sha256(fixture).hexdigest() != contracts()['fixture_sha256'],hex(address)
