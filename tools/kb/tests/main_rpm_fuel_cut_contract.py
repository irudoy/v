"""Bind RPM state arithmetic to exact stock bytes and preserved native owners."""
from dataclasses import asdict
from functools import cache
import hashlib
import json
import re

from kb import compile, repo
from kb.arithmetic import Grammar
from tools.kb.tests import test_injection_start_delay_chain as publication
from tools.kb.tests import main_rpm_fuel_cut_equations as equations

TOOL = repo.ROOT / 'tools/sh-elf-run'
SPEC = 'defs/JK08A.main-rpm-fuel-cut.md'
KEY = 'jk08a-main-rpm-fuel-cut'


@cache
def contracts():
    value = json.loads((TOOL/'main-rpm-fuel-cut-contracts.json').read_text())
    assert value['changed_steps'] == [11,12] and value['hardware_ready'] is False
    return value


def owner_contract(model=None):
    model = compile.cached(repo.ROOT) if model is None else model
    for ref, expected in contracts()['owner_contracts'].items():
        owner = publication.required_owner(model,ref,int(expected['address'],16))
        symbol = owner.symbols['7mfk']
        publication.required_properties(model,owner.props,expected['props'])
        publication.required_properties(model,symbol.props,expected['symbol_props'])
        assert symbol.value('level') == expected['level']
        publication.required_evidence(model,symbol.evidence,expected['evidence'])
        for wanted in expected['links']:
            links = [item for item in owner.links if (item.type,item.to.key,item.slot,item.offset) ==
                (wanted['type'],wanted['to'],wanted['slot'],wanted['offset'])]
            assert len(links) == 1
            [link] = links
            assert link.stated >= set(wanted['layouts']) and link.roles >= set(wanted['roles'])
            publication.required_properties(model,link.props,wanted['props'])
            publication.required_evidence(model,link.evidence,wanted['evidence'])
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
    assert region.ram_literals == (0x4f460,0x4f46c)
    for path,digest in contracts()['sources_sha256'].items():
        assert hashlib.sha256((repo.ROOT/path).read_bytes()).hexdigest() == digest,path


def earlier_region_contract():
    stock = publication.stock_module()
    earlier = [row for row in stock.REGIONS if row.key not in (KEY,'jk08a-vehicle-speed-fuel-cut')]
    assert json.loads(json.dumps([asdict(row) for row in earlier])) == contracts()['held_regions']
    assert {key:value for key,value in stock.REGION_OBSERVERS.items() if key not in (KEY,'jk08a-vehicle-speed-fuel-cut')} == contracts()['held_observers']
    for row in earlier:
        assert hashlib.sha256(stock.build_fixture(row,stock.stock_image(row.rom))).hexdigest() == contracts()['held_fixtures'][row.key]


def literal_contract():
    assert equations.model.header(equations.model.matrix()) == (TOOL/'main-rpm-fuel-cut-cases.h').read_text()


def equation_contract(model=None,formulas=None):
    model = compile.cached(repo.ROOT) if model is None else model
    chain = model.entities[('chain','fuel_cut')]
    actual = {str(number):chain.steps[number-1]['note'] for number in (11,12)}
    assert actual == contracts()['formulas'] == equations.FORMULAS
    formulas = actual if formulas is None else formulas
    for number in ('11','12'):
        assert equations.verify(formulas[number],number) == len(equations.model.matrix())


def publication_contract():
    stock = publication.stock_module()
    [region] = [row for row in stock.REGIONS if row.key == KEY]
    instructions = (region.end-region.start)//2
    bound = region.end-region.start+sum(size for _,size in region.pools)
    counts = (instructions,bound,region.cases)
    assert counts == tuple(contracts()['counts'])
    assert len(equations.model.matrix()) == region.cases
    for path in (SPEC,'tools/sh-elf-run/README.md'):
        text = re.sub(r'\s+',' ',(repo.ROOT/path).read_text().split('## Main RPM fuel-cut state',1)[1])
        assert f'The bounded entry 0004f282 binds {counts[0]} stock instructions and {counts[1]} bytes' in text
        assert f'The literal matrix has {counts[2]} independent contexts' in text
        for phrase in ('Hardware readiness is NO','does not decrement','already armed','SR/MQT','64 KiB','identity-only'):
            assert phrase in text,phrase
