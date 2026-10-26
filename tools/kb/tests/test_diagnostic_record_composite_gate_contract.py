"""Independent nested predicate, exact sentinel calls and composite short-circuit contracts."""
from copy import deepcopy
import pytest
from kb import repo
from kb import diagnostic_record_composite_gate_contract as contract,diagnostic_record_composite_gate_matrix as matrix
from kb import diagnostic_record_composite_gate_semantics as semantics


def controlled(changes=None,**context_changes):
    case=dict(matrix.DEFAULTS,entry=contract.ENTRY,index=0,kind='controlled');case.update(context_changes)
    for index,raw in (changes or {}).items():case[f'record_{index:03x}_2']=raw
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    context=matrix.context(source,case)
    value=semantics.evaluate(contract.ENTRY,matrix.memory(case),matrix.calibrations(source,image,case),
        context,case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)
    return case,context,value


@pytest.mark.parametrize('index',contract.INDICES)
@pytest.mark.parametrize('raw',(0,1,31,32,63,64,95,96,127,128,255))
def test_each_selected_member_returns_boolean_mask_result_with_all_other_records_quiet(index,raw):
    case,context,value=controlled({index:raw});active=bool(raw&0x60)
    assert value['output']==int(active) and value['exit'][-1]==int(active)
    assert value['active_index']==(index if active else None)
    expected=2+contract.INDICES.index(index)+1 if active else 12
    assert len(value['calls'])==len(value['predicates'])==expected
    assert [row['argument'] for row in value['predicates'][:2]]==[0xFFFFFFFF,0xFFFFFFFF]
    assert all(row['sentinel'] is True and row['reads']==[] and row['output']==0 for row in value['predicates'][:2])
    assert value['ram']==matrix.memory(case)
    assert value['sr']==(case['initial_sr']&~1)|int(not active)
    if active:
        selected=value['predicates'][-1]
        assert selected['argument']==index and selected['reads'][0]==(0x259F6,matrix.RAM_BASE+0x571A+3*index,raw)
        assert len(selected['reads'])==(1 if raw&64 else 2)


@pytest.mark.parametrize('first',range(10))
def test_first_active_record_terminates_before_every_later_record_or_helper_argument(first):
    changes={index:64 for index in contract.INDICES[first:]}
    case,context,value=controlled(changes)
    assert value['active_index']==contract.INDICES[first]
    assert [row['argument'] for row in value['predicates']]==[0xFFFFFFFF,0xFFFFFFFF,*contract.INDICES[:first+1]]
    observed_members={event['address'] for event in value['operands'] if event['domain']=='ram'}
    assert observed_members=={matrix.RAM_BASE+0x571A+3*index for index in contract.INDICES[:first+1]}


@pytest.mark.parametrize('sr',(0,1,0xF0,0xF1,0x100,0x200,0x300,0x3F1))
def test_full_caller_PR_frame_SR_and_natural_return_are_independent_of_initial_T(sr):
    case,context,value=controlled(initial_sr=sr)
    assert value['output']==0 and value['sr']==(sr&~1)|1
    assert value['frame'][156:160]==bytes.fromhex('02100000')
    assert value['frame'][:156]==bytes([0xA5])*156 and value['frame'][160:]==bytes([0xA5])*32
    assert (value['sp'],value['pr'],value['gbr'],value['mach'],value['macl'])==(0x02001000,0x02100000,*context[15:18])
    assert value['steps'][-2]['site']==0x25A88 and value['steps'][-1]['site']==0x25A8A
    assert value['steps'][-1]['delay_slot'] is True and value['steps'][-1]['next']==0x02100000
    assert value['registers'][4]==0x8C and value['registers'][3]==0xFFFFFF8C and value['registers'][7]==3*0x8C
    assert all(value['registers'][i]==context[i] for i in range(8,15))


def test_real_first_call_distinguishes_complete_pre_delay_R4_and_exact_sentinel_entry():
    case,context,value=controlled(raw_r4=0xA5C31234)
    call=value['calls'][0]
    assert call['registers'][4]==0xA5C31234 and call['entry']['registers'][4]==0xFFFFFFFF
    assert (call['site'],call['target'],call['return_address'],call['sp'])==(0x25A14,0x259E4,0x25A18,0x02000FFC)
    assert call['entry']['pr']==0x25A18 and call['entry']['sp']==0x02000FFC
    for call,predicate in zip(value['calls'],value['predicates']):assert call['entry']['registers'][4]==predicate['argument']


def test_full_raw_inputs_cover_every_member_byte_and_independent_activation_combination():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes();cases=matrix.cases(source,image)
    for index in contract.INDICES:
        assert {case[f'record_{index:03x}_2'] for case in cases if case['kind']=='every-selected-byte-preimage'}==set(range(256))
    active={tuple(bool(case[f'record_{index:03x}_2']&96) for index in contract.INDICES)
        for case in cases if case['kind']=='every-independent-record-activation-combination'}
    assert len(active)==1<<len(contract.INDICES)
    assert contract.INDICES==(0x14,0x47,0x48,0x49,0x4A,0x4B,0x4C,0x8A,0x8B,0x8C)


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_fixture_grants_no_owning_geometry_scale_hardware_schedule_stub_or_publication(monkeypatch,flag):
    value=deepcopy(contract.DECLARED);value[flag]=True
    monkeypatch.setattr(contract.tomllib,'loads',lambda text:value)
    with pytest.raises(ValueError):contract.descriptor(repo.ROOT)


def test_exact_complete_caller_helper_and_one_pointer_alias_preserve_every_instruction():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image)
    assert contract.SPANS==((0x259E4,0x25A12),(0x25A12,0x25A8C))
    assert contract.FUNCTIONS==(0x25A12,0x259E4) and len(aliases)==1
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]
    allowed=set(range(0x25B98,0x25B9C))
    assert {at for at,(a,b) in enumerate(zip(image,fixture)) if a!=b}<=allowed


def test_diagnostic_family_publication_binds_current_native_and_execution_sources():
    import json,tomllib
    from kb import ordinary_access_registry as registry,proof_adapter
    family=next(row for row in registry.FAMILIES if row.mode=='diagnostic-record-bit4-access')
    declared=family.contract.descriptor(repo.ROOT);rows=declared['reference']
    text=' '.join((repo.ROOT/'defs/JK08A.diagnostic-record-composite-gate.md').read_text().split())
    assert len(rows)==3 and len(declared['retained_functions'])==4 and len(family.captures)==3
    assert sum(json.loads(row['original_claim_json'])['type']=='writer' for row in rows)==2
    assert sum(json.loads(row['original_claim_json'])['type']=='reader' for row in rows)==1
    assert len({row['proposed_native_sha256'] for row in rows})==1
    outputs=set();prior=set()
    for index,path in enumerate(proof_adapter.DESCRIPTORS):
        adapter=tomllib.loads((repo.ROOT/path).read_text())['adapter']
        outputs.update((adapter['driver'],adapter['refusals']))
        if index<36:prior.update((adapter['driver'],adapter['refusals']))
    assert len(registry.FAMILIES)==42 and len(registry.captures())==86
    assert f'{len(registry.FAMILIES)} families and {len(registry.captures())} captures' in text
    assert len(proof_adapter.DESCRIPTORS)==39 and len(outputs)==78 and len(prior)==72
    assert f'{len(proof_adapter.DESCRIPTORS)} descriptors and {len(outputs)} generated outputs' in text
    assert f'{len(prior)} preceding outputs' in text
