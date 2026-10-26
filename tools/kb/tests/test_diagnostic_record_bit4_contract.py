"""Complete bit4 byte equations, signed carriers, natural delay store and bounded inputs."""
from copy import deepcopy
import pytest
from kb import repo
from kb import diagnostic_record_bit4_contract as contract, diagnostic_record_bit4_matrix as matrix
from kb import diagnostic_record_bit4_semantics as semantics


def controlled(index=0,raw=0,**changes):
    case=dict(matrix.DEFAULTS,entry=contract.ENTRY,index=0,kind='controlled')
    case.update(raw_r4=index,**{f'record_{index:03x}_2':raw});case.update(changes)
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    context=matrix.context(declared,case)
    value=semantics.evaluate(contract.ENTRY,matrix.memory(case),matrix.calibrations(declared,image,case),
        context,case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)
    return case,context,value


@pytest.mark.parametrize('index',contract.INDICES)
@pytest.mark.parametrize('raw',(0,1,15,16,17,31,63,127,128,129,239,240,254,255))
def test_exact_indexed_byte_operation_keeps_every_unmasked_bit_and_complete_signed_carrier(index,raw):
    case,context,value=controlled(index,raw)
    wanted=bytearray(matrix.memory(case));wanted[0x571A+3*index]=raw|16;wanted[0x508C]=1
    assert value['ram']==bytes(wanted) and value['member']==matrix.RAM_BASE+0x571A+3*index
    assert value['published']==raw|16
    assert value['states'][0x8C974]['registers'][0]==(raw if raw<128 else raw|0xFFFFFF00)
    assert value['states'][0x8C978]['registers'][0]==((raw|16) if raw<128 else (raw|16)|0xFFFFFF00)
    assert value['states'][0x8C970]['registers'][2]==index*3
    assert value['states'][0x8C972]['registers'][6]==matrix.RAM_BASE+0x5718+index*3
    assert value['registers'][4]==index and value['registers'][0]==0xB34
    assert value['registers'][1]==matrix.RAM_BASE+0x5718 and value['registers'][2]==1
    assert value['registers'][6]==matrix.RAM_BASE+0x4558
    assert value['path']==tuple(range(0x8C968,0x8C984,2)) and value['calls']==[]


@pytest.mark.parametrize('sr',(0,1,0xF0,0xF1,0x100,0x200,0x300,0x3F1))
def test_full_actual_SR_controls_are_preserved_except_real_SHLL_T_and_delay_store_is_unconditional(sr):
    case,context,value=controlled(0x129,0x80,initial_sr=sr,prior_508c=255)
    assert value['sr']==sr&~1
    assert value['states'][0x8C96C]['sr']==sr and value['states'][0x8C96E]['sr']==sr&~1
    assert value['branches']==[dict(site=0x8C980,kind='return',target=0x02100000,delay=True)]
    assert value['operands'][-1]==dict(site=0x8C982,mode='write',address=matrix.RAM_BASE+0x508C,
        width_bytes=1,register=2,domain='ram',bytes='01')
    assert value['frame']==bytes([0xA5])*192
    assert (value['sp'],value['pr'],value['gbr'],value['mach'],value['macl'])==(0x02001000,0x02100000,*context[15:18])


@pytest.mark.parametrize('raw',(True,-1,0x157,0x10000,0x80000000,0xFFFFFFFF))
def test_explicit_full_R4_execution_premise_does_not_truncate_or_infer_unobserved_indices(raw):
    case=dict(matrix.DEFAULTS,entry=contract.ENTRY,index=0,kind='controlled');case['raw_r4']=raw
    with pytest.raises(ValueError):matrix.require_case(case)


@pytest.mark.parametrize('fault',('image','code','pool','alias','index','native','scope'))
def test_exact_source_declaration_refuses_changed_image_function_pool_alias_or_premise(tmp_path,fault):
    import tomllib
    text=(repo.ROOT/contract.DESCRIPTOR).read_text()
    value=tomllib.loads(text)
    if fault=='image':value['image_sha256']='0'*64
    elif fault=='code':value['unit']['code'][0]['end']-=2
    elif fault=='pool':value['unit']['pools'][0]['stock_hex']='0000'
    elif fault=='alias':value['unit']['aliases'][0]['alias']+=1
    elif fault=='index':value['index_premise'].append(0x157)
    elif fault=='scope':value['scope']='partial leaf'
    else:value['native_identity_admission']=True
    from unittest.mock import patch
    with patch.object(contract.tomllib,'loads',return_value=value):
        with pytest.raises(ValueError):contract.descriptor(repo.ROOT)


def test_owned_fixture_preserves_every_instruction_and_changes_only_two_pointer_literals():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image)
    assert fixture[0x8C968:0x8C984]==image[0x8C968:0x8C984]
    allowed={at for row in aliases for at in range(row['address'],row['address']+row['width'])}
    assert {at for at,(old,new) in enumerate(zip(image,fixture)) if old!=new}<=allowed
    assert len(aliases)==2 and fixture[0x8C988:0x8C98A]==bytes.fromhex('0b34')


def test_input_catalog_retains_every_full_byte_preimage_for_each_exact_physical_index():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    cases=matrix.cases(source,image)
    assert contract.INDICES==(0,1,0x47,0x123,0x128,0x129,0x156)
    for index in contract.INDICES:
        rows=[case for case in cases if case['kind']=='every-selected-byte-preimage' and case['raw_r4']==index]
        assert {case[f'record_{index:03x}_2'] for case in rows}==set(range(256))
        for case in rows:
            matrix.require_case(case)
            assert matrix.context(source,case)[4]==index
            assert matrix.memory(case)[0x571A+3*index]==case[f'record_{index:03x}_2']
    assert {case['initial_sr'] for case in cases if case['kind']=='complete-QM-interrupt-T-context'}=={
        qm|interrupt|t for qm in (0,0x100,0x200,0x300) for interrupt in range(0,256,16) for t in (0,1)}


def test_specification_publishes_exact_instruction_delay_and_existing_native_claim_boundaries():
    words=' '.join((repo.ROOT/'defs/JK08A.diagnostic-record-bit4.md').read_text().split())
    for phrase in ('3655c66e3ef972ce95f95db39da784ed70f454d346be7a51411fffaeb1fa00b5',
        'Two simulator-only pointer literal relocations','FFFF508C','00000B34',
        'input echo','changed write-set alone','both ledger ends','TEST origins and positions'):
        assert phrase in words
    assert len(contract.UNIT['aliases'])==2
    assert contract.SPANS==((0x8C968,0x8C984),)
    assert {(r['address'],r['size']) for r in contract.UNIT['pools']}=={(0x8C988,2),(0x8C98C,4),(0x8C998,4)}


def test_registered_positive_writer_publication_reads_the_execution_registries():
    import tomllib
    from kb import ordinary_access_registry as registry,proof_adapter
    text=' '.join((repo.ROOT/'defs/JK08A.diagnostic-record-bit4.md').read_text().split())
    outputs=set()
    for path in proof_adapter.DESCRIPTORS:
        adapter=tomllib.loads((repo.ROOT/path).read_text())['adapter']
        outputs.update((adapter['driver'],adapter['refusals']))
    assert len(registry.FAMILIES)==40 and len(registry.captures())==83
    assert f'{len(registry.FAMILIES)} families and {len(registry.captures())} captures' in text
    assert len(proof_adapter.DESCRIPTORS)==38 and len(outputs)==76
    assert f'{len(proof_adapter.DESCRIPTORS)} descriptors and {len(outputs)} generated outputs' in text
