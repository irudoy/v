"""Bind fuel-cut consumer equations to unchanged executed Regions and native owners."""
from dataclasses import asdict
from functools import cache
import hashlib,json,re

from kb import compile,repo
from kb.arithmetic import Grammar
from tools.kb.tests import test_injection_start_delay_chain as publication
from tools.kb.tests import test_connected_injection_chain as connected
from tools.kb.tests import fuel_cut_consumer_equations as equations

TOOL=repo.ROOT/'tools/sh-elf-run'
SPEC='defs/JK08A.fuel-cut-consumer.md'

@cache
def contracts():
    value=json.loads((TOOL/'fuel-cut-consumer-contracts.json').read_text())
    assert value['changed_steps']==[23,24,25] and value['hardware_ready'] is False
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
            links=[item for item in owner.links if (item.type,item.to.key,item.slot,item.offset)==
                (wanted['type'],wanted['to'],wanted['slot'],wanted['offset'])]
            assert len(links)==1
            [link]=links
            assert link.stated>=set(wanted['layouts']) and link.roles>=set(wanted['roles'])
            publication.required_properties(model,link.props,wanted['props'])
            publication.required_evidence(model,link.evidence,wanted['evidence'])
    chain=model.entities[('chain','fuel_cut')]
    assert len(chain.steps)==25
    publication.required_properties(model,chain.props,contracts()['chain_props'])
    for number,wanted in contracts()['steps'].items():
        assert publication.normalized(model,chain.steps[int(number)-1])==wanted
        assert wanted['sign']=='none' and Grammar(repo.config()).validate(wanted['note']) is None
    for number,wanted in contracts()['held_steps'].items():
        assert publication.normalized(model,chain.steps[int(number)-1])==wanted

def registered_stock_contract(image):
    module=publication.stock_module()
    connected.stock_contract(image)
    regions={row.key:row for row in module.REGIONS}
    for key,wanted in contracts()['regions'].items():
        row=regions[key]
        assert json.loads(json.dumps(asdict(row)))==wanted
        assert module.REGION_OBSERVERS[key]==contracts()['observers'][key]
        assert hashlib.sha256(module.build_fixture(row,image)).hexdigest()==contracts()['fixtures'][key]
        assert row.boundary is False and dict(row.constants)['EARLY_ONLY']==0
        connected.harness_contract(row,(TOOL/row.harness).read_text())
    for path,digest in contracts()['sources_sha256'].items():
        assert hashlib.sha256((repo.ROOT/path).read_bytes()).hexdigest()==digest,path

def all_regions_contract():
    module=publication.stock_module()
    assert json.loads(json.dumps([asdict(row) for row in module.REGIONS]))==contracts()['held_regions']
    assert module.REGION_OBSERVERS==contracts()['held_observers']
    for row in module.REGIONS:
        assert hashlib.sha256(module.build_fixture(row,module.stock_image(row.rom))).hexdigest()==contracts()['held_fixtures'][row.key]

def literal_contract():
    for name,model in (('oneshot',equations.oneshot),('event-isr',equations.event)):
        assert model.header(model.matrix())==(TOOL/(name+'-cases.h')).read_text()

def equation_contract(model=None,formulas=None):
    model=compile.cached(repo.ROOT) if model is None else model
    chain=model.entities[('chain','fuel_cut')]
    actual={str(number):chain.steps[number-1]['note'] for number in (23,24,25)}
    assert actual==contracts()['formulas']==equations.FORMULAS
    formulas=actual if formulas is None else formulas
    assert equations.verify_counter(formulas['23'],'23')==48072
    assert equations.verify_counter(formulas['25'],'25')==48072
    assert equations.verify_event(formulas['24'])==contracts()['event_paths']

def publication_contract():
    rows=contracts()['regions'].values()
    counts=(len(contracts()['regions']),sum((end-start)//2 for row in rows for start,end in [(row['start'],row['end']),*row['callees']]),
        sum(row['end']-row['start']+sum(end-start for start,end in row['callees'])+sum(size for _,size in row['pools']) for row in rows),
        sum(row['cases'] for row in rows))
    assert counts==tuple(contracts()['counts'])
    for path in (SPEC,'tools/sh-elf-run/README.md'):
        text=re.sub(r'\s+',' ',(repo.ROOT/path).read_text().split('## Fuel-cut consumer and event history',1)[1])
        assert f'Two existing mandatory Regions bind {counts[1]} instructions, {counts[2]} bound bytes and {counts[3]} literal cases' in text
        for phrase in ('Hardware readiness is NO','whole mask','uint16','SPC/SSR','1936','R4','R5','0..5','producer'):
            assert phrase in text,phrase
    text=(repo.ROOT/'defs/JK08A.fuel.md').read_text()
    assert 'if mask & (uint8[0xFFFF22E0] | uint8[0xFFFF1935]):' in text
    assert 'set every bit of mask in uint8[0xFFFF1935]' in text
    assert 'if bit i of 0xFFFF22E0 or of history 0xFFFF1935:' not in text
