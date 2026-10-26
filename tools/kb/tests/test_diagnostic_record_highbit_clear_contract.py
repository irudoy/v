"""Exact full-width address, byte-clear, CPU/SR and inert-sentinel source contracts."""
from copy import deepcopy
import pytest
from kb import repo
from kb import diagnostic_record_highbit_clear_contract as contract
from kb import diagnostic_record_highbit_clear_matrix as matrix
from kb import diagnostic_record_highbit_clear_semantics as semantics


def controlled(index=0,raw=0,**changes):
    case=dict(matrix.DEFAULTS,entry=contract.ENTRY,index=0,kind='controlled',raw_r4=index)
    field=matrix.selected_field(index)
    if field is not None:case[field]=raw
    case.update(changes);source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    context=matrix.context(source,case)
    value=semantics.evaluate(contract.ENTRY,matrix.memory(case),matrix.calibrations(source,image,case),
        context,case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)
    return case,context,value


@pytest.mark.parametrize('index',tuple(i for i in contract.INDICES if i!=0xFFFFFFFF))
@pytest.mark.parametrize('raw',(0,1,63,127,128,129,254,255))
def test_exact_indexed_clear_preserves_low_bits_full_R4_and_complete_other_RAM(index,raw):
    case,context,value=controlled(index,raw);offset=(0x5719+3*index)&0xFFFFFFFF
    wanted=bytearray(matrix.memory(case));wanted[offset]=raw&0x7F
    assert value['ram']==bytes(wanted) and value['member']==matrix.RAM_BASE+offset
    assert value['published']==raw&0x7F and value['registers'][0]==raw&0x7F
    assert value['states'][0x8C35A]['registers'][0]==(raw if raw<128 else raw|0xFFFFFF00)
    assert value['states'][0x8C354]['registers'][2]==(index*2)&0xFFFFFFFF
    assert value['states'][0x8C356]['registers'][2]==(index*3)&0xFFFFFFFF
    assert value['states'][0x8C358]['registers'][6]==(matrix.RAM_BASE+0x5718+3*index)&0xFFFFFFFF
    assert value['registers'][4]==index and value['registers'][1]==matrix.RAM_BASE+0x5718
    assert value['path']==semantics.ACTIVE_PATH and value['calls']==[]
    assert value['frame']==bytes([0xA5])*192


@pytest.mark.parametrize('sr',(0,1,0xF0,0xF1,0x100,0x200,0x300,0x3F1))
@pytest.mark.parametrize('index',(0,0xAAAAAAAB,0xFFFFFFFF))
def test_real_CMP_SHLL_T_and_both_natural_RTS_paths_preserve_other_complete_state(sr,index):
    case,context,value=controlled(index,0xFF,initial_sr=sr)
    wanted_T=1 if index==0xFFFFFFFF else index>>31
    assert value['sr']==(sr&~1)|wanted_T
    assert value['states'][0x8C34C]['sr']==(sr&~1)|int(index==0xFFFFFFFF)
    assert (value['sp'],value['pr'],value['gbr'],value['mach'],value['macl'])==(0x02001000,0x02100000,*context[15:18])
    if index==0xFFFFFFFF:
        assert value['ram']==matrix.memory(case) and value['registers'][0]==0xFFFFFFFF
        assert value['registers'][2]==context[2] and value['registers'][6]==context[6]
        assert value['path']==semantics.SENTINEL_PATH and len(value['operands'])==1
        assert value['operands'][0]['domain']=='rom'
    else:
        assert value['operands'][-1]['site']==0x8C360 and value['operands'][-1]['bytes']=='7f'
    assert value['branches'][0]==dict(site=0x8C34E,kind='taken' if index==0xFFFFFFFF else 'fallthrough',
        target=0x8C362 if index==0xFFFFFFFF else 0x8C350,delay=False)


def test_full_raw_modular_inputs_are_not_replaced_by_low16_or_an_invented_API_bound():
    _,_,first=controlled(0xAAAAAAAB,255);_,_,second=controlled(0x55555555,255)
    assert first['member']==matrix.RAM_BASE+0x571A and second['member']==matrix.RAM_BASE+0x5718
    for raw in (True,-1,0x100000000,0x10000,0x80000000):
        case=dict(matrix.DEFAULTS,entry=contract.ENTRY,index=0,kind='controlled',raw_r4=raw)
        with pytest.raises(ValueError):matrix.require_case(case)


@pytest.mark.parametrize('fault',('image','code','pool','alias','indices','native','scope'))
def test_exact_unit_refuses_changed_bytes_aliases_input_observations_or_admission(monkeypatch,fault):
    value=deepcopy(contract.DECLARED)
    if fault=='image':value['image_sha256']='0'*64
    elif fault=='code':value['unit']['code'][0]['end']-=2
    elif fault=='pool':value['unit']['pools'][0]['stock_hex']='00000000'
    elif fault=='alias':value['unit']['aliases'][0]['alias']+=1
    elif fault=='indices':value['explicit_raw_R4_inputs'].pop()
    elif fault=='scope':value['scope']='universal bounded-index proof'
    else:value['native_identity_admission']=True
    monkeypatch.setattr(contract.tomllib,'loads',lambda text:value)
    with pytest.raises(ValueError):contract.descriptor(repo.ROOT)


def test_fixture_preserves_every_instruction_and_changes_only_one_pointer_literal():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image)
    assert fixture[contract.ENTRY:0x8C366]==image[contract.ENTRY:0x8C366]
    assert len(aliases)==1 and aliases[0]['address']==0x8C45C
    allowed=set(range(0x8C45C,0x8C460))
    assert {at for at,(old,new) in enumerate(zip(image,fixture)) if old!=new}<=allowed


def test_complete_input_catalog_retains_sentinel_all_preimages_and_full_high_R4():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes();cases=matrix.cases(source,image)
    assert 0xFFFFFFFF in contract.INDICES and 0xAAAAAAAB in contract.INDICES and 0x55555555 in contract.INDICES
    for index in contract.INDICES:
        rows=[case for case in cases if case['raw_r4']==index]
        assert rows
        if index==0xFFFFFFFF:continue
        field=matrix.selected_field(index)
        assert {case[field] for case in rows}==set(range(256))
        for case in rows:assert matrix.context(source,case)[4]==index


def test_specification_counts_and_original_read_the_executed_source_boundary():
    from kb import diagnostic_record_bit4_access_contract as owning
    source=contract.descriptor(repo.ROOT)
    words=' '.join((repo.ROOT/'defs/JK08A.diagnostic-record-highbit-clear.md').read_text().split())
    instructions=sum((row['end']-row['start'])//2 for row in source['unit']['code'])
    assert f'{instructions}-instruction body' in words and instructions==15
    assert len(source['unit']['pools'])==len(source['unit']['aliases'])==1
    selected,=[r for r in owning.descriptor(repo.ROOT)['reference'] if r['component']=='diagnostic_record_highbit_clear_paths']
    assert selected['original_claim_sha256'] in words
    assert selected['function']==contract.ENTRY and selected['sites']==[0x8C360]
    assert 'changed write-set alone' in words and 'TEST origins and positions' in words



def test_registered_family_and_adapter_publications_read_the_current_execution_declarations():
    import json,tomllib
    from kb import ordinary_access_registry as registry,proof_adapter
    from kb import diagnostic_record_bit4_access_contract as owning
    family=next(row for row in registry.FAMILIES if row.mode=='diagnostic-record-bit4-access')
    declared=owning.descriptor(repo.ROOT);rows=declared['reference']
    assert len(rows)==4 and len(declared['retained_functions'])==5 and len(family.captures)==4
    assert sum(json.loads(row['original_claim_json'])['type']=='writer' for row in rows)==3
    assert sum(json.loads(row['original_claim_json'])['type']=='reader' for row in rows)==1
    outputs=set();preceding=set()
    position=proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)
    for index,path in enumerate(proof_adapter.DESCRIPTORS):
        adapter=tomllib.loads((repo.ROOT/path).read_text())['adapter'];outputs.update((adapter['driver'],adapter['refusals']))
        if index<position:preceding.update((adapter['driver'],adapter['refusals']))
    assert len(registry.FAMILIES)==42 and len(registry.captures())==88
    assert len(proof_adapter.DESCRIPTORS)==41 and len(outputs)==82 and len(preceding)==78
    paths=('defs/JK08A.diagnostic-record-highbit-clear.md','defs/JK08A.diagnostic-record-bit4.md',
        'defs/JK08A.diagnostic-record-bits3-6.md','defs/JK08A.diagnostic-record-composite-gate.md',
        'defs/JK08A.map-bias-division-caller-withdrawal-paths.md','defs/JK08A.an1-source-dispatch-access-paths.md')
    for path in paths:
        text=' '.join((repo.ROOT/path).read_text().split())
        assert f'{len(registry.FAMILIES)} families and {len(registry.captures())} captures' in text
        assert f'{len(proof_adapter.DESCRIPTORS)} descriptors and {len(outputs)} generated outputs' in text
    for path in ('tools/sh-elf-run/README.md','tools/kb/ordinary-access.md'):
        text=' '.join((repo.ROOT/path).read_text().split())
        assert f'{len(registry.FAMILIES)} families and {len(registry.captures())} captures' in text
    text=' '.join((repo.ROOT/paths[0]).read_text().split())
    assert f'{len(preceding)} preceding generated outputs' in text
    assert 'four exact positive originals: three writers and one indexed reader' in text
    assert 'five complete unchanged function snapshots' in text
