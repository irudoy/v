"""Exact indexed physical words, signed subtraction, SR restoration and native writer boundary."""

import hashlib
import json
import pytest
from kb import repo,proof_adapter
from kb import ordinary_access_registry as registry
from kb import indexed_word_update_contract as contract,indexed_word_update_matrix as matrix
from kb import indexed_word_update_semantics as scalar,indexed_word_update_transfers as transfers
from kb import indexed_word_update_capture_evidence as proof,scalar_ram_leaf_withdrawal_contract as withdrawal


def evaluate(**changes):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x52034,**changes)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    return scalar.evaluate(0x52034,matrix.memory(case),matrix.calibrations(source,image,case),
        matrix.context(source,case),case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)


@pytest.mark.parametrize('previous,delta,full,stored,t',((2000,1000,1000,1000,True),
    (0,1000,0,0,False),(1000,1000,0,0,True),(65535,65535,65536,0,True),
    (0,65535,1,1,True),(65535,32768,98303,32767,True),(0,32767,0,0,False)))
def test_unsigned_counter_minus_signed_delta_has_zero_floor_and_low16_store(previous,delta,full,stored,t):
    value=evaluate(counter_word_000=previous,state_word_000=delta)
    assert value['registers'][6]==full and int.from_bytes(value['ram'][0x2348:0x234A],'big')==stored
    assert value['registers'][4]==(previous-scalar.signed(delta,16))&0xFFFFFFFF
    assert bool(value['sr']&1)==t and value['path'][-2:]==(0x520E8,0x520EA)


@pytest.mark.parametrize('sample,factor,blocked',((639,5,True),(640,5,False),(32767,255,False),
    (32768,0,True),(65535,0,True),(0,0,False)))
def test_threshold_is_signed_word_against_unsigned_byte_times128(sample,factor,blocked):
    value=evaluate(state_word_076=sample,threshold_factor=factor,update_mask=255)
    assert value['tags']['blocked'] is blocked
    assert value['ram'][0x1220]==(254 if blocked else 255)


def test_disabled_path_retains_raw_incoming_index_and_exact_delay_slot_mask():
    value=evaluate(enable_mask=0,raw_r4=0x812345FF,raw_r5=0x81234581)
    assert value['registers'][4]==129 and value['registers'][7]==0x812345FF
    assert value['registers'][5]==0x81234581 and value['registers'][6]==0x8D92
    assert value['tags']['physical_writes']=={} and value['sr']&1==1


def test_held_path_sets_status_without_entering_counter_or_interrupt_update():
    value=evaluate(update_mask=128,hold_mask=1)
    assert value['ram'][0x1220]==129 and value['tags']['held'] is True
    assert value['tags']['counter_changed'] is False and value['tags']['interrupted_sr'] is None
    assert value['frame'][148:152]==bytes([0xA5])*4 and value['registers'][6]==0x0100128C
    assert value['sr']&1==0


@pytest.mark.parametrize('sr',tuple(qm|interrupt|t for qm in (0,0x100,0x200,0x300)
    for interrupt in range(0,256,16) for t in (0,1)))
@pytest.mark.parametrize('changes',({},dict(hold_mask=1),dict(enable_mask=0),dict(fuel_mask=1)))
def test_complete_QM_interrupt_and_T_contexts_retain_exact_final_and_temporary_SR(sr,changes):
    value=evaluate(initial_sr=sr,**changes)
    assert value['sr']&~1==sr&~1
    if value['tags']['counter_changed']:
        assert value['tags']['interrupted_sr']==((sr&~0xF1)|0xF1)
        assert value['registers'][0]==sr&0xF0 and value['registers'][2]==value['sr']
    else:assert value['tags']['interrupted_sr'] is None


def test_frame_equations_retain_old_pointer_read_before_replacement_and_saved_status():
    value=evaluate(update_mask=128)
    events=value['tags']['frame_accesses']
    assert events[0x520A2]==('write',12,6,bytes.fromhex('01002330'))
    assert events[0x520BE]==('read',12,5,bytes.fromhex('01002330'))
    assert events[0x520CA]==('write',12,5,bytes.fromhex('01002348'))
    assert value['frame'][148:156]==bytes.fromhex('01002348ffffff80')


@pytest.mark.parametrize('index',(0,75,76,179,180,255))
def test_all_logical_word_views_share_one_authoritative_physical_union(index):
    assert matrix.state_field('delta',index)==f'state_word_{index:03d}'
    assert matrix.state_field('threshold',index)==f'state_word_{76+index:03d}'
    case=dict(matrix.DEFAULTS,index=0,entry=0x52034,kind='controlled')
    field=matrix.state_field('threshold',index);case[field]=0x8123;memory=matrix.memory(case)
    assert memory[0x142E+2*index:0x1430+2*index]==bytes.fromhex('8123')
    if index<180:assert field==matrix.state_field('delta',index+76)
    assert len({at+offset for n,at,width in matrix.RAM_FIELDS for offset in range(width)})==sum(w for n,a,w in matrix.RAM_FIELDS)


def test_fixture_preserves_all_natural_instructions_and_only_declared_pointer_aliases():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image);restored=bytearray(fixture)
    for a,b in contract.SPANS:assert fixture[a:b]==image[a:b]
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert len(aliases)==4 and bytes(restored)==image
    assert transfers.FIXED_BRANCHES=={} and transfers.INFEASIBLE_INSTRUCTIONS==()
    text=(repo.ROOT/contract.UNIT['assembly']).read_text()
    assert 'L_000520e8:' in text and 'L_000520ea:' in text and 'shll 2 ' not in text


def test_producer_and_input_only_adapter_retain_exact_terminal_marker():
    from kb.test_stock_capture import tool
    producer=tool(repo.ROOT,'indexed_word_update_capture.py','_kb_indexed_word_producer_source_contract')
    source=contract.descriptor(repo.ROOT)
    assert source['adapter']['marker']==producer.MARKER=='VQ_SH_ELF_INDEXED_WORD_UPDATE'
    assert source['adapter']['region']==producer.REGION and source['adapter']['prefix']==producer.PREFIX
    proof_adapter.require_generated(repo.ROOT,contract.DESCRIPTOR)


@pytest.mark.parametrize('root',transfers.NATIVE_RAM_ROOTS)
@pytest.mark.parametrize('form',('native','alias','overlapping-interval'))
@pytest.mark.parametrize('domain',('ram','rom','frame'))
def test_selected_native_writer_root_and_alias_absence_is_independent_of_domain_labels(root,form,domain):
    rows=[r for r in withdrawal.descriptor(repo.ROOT)['reference'] if r['component']=='indexed_word_update_paths']
    original,native,alias=root;at=native if form=='native' else alias;width=1
    if form=='overlapping-interval':at-=1;width=2
    with pytest.raises(ValueError):transfers.require_no_selected_datum(dict(accesses=[dict(site=0x52082,address=at,width_bytes=width,domain=domain)]),rows)


@pytest.mark.parametrize('field,value',(('state_word_000',65536),('counter_word_255',-1),('hold_mask',True),
    ('threshold_factor',256),('raw_r4',1<<32),('initial_sr',2),('initial_sr',0x400)))
def test_inputs_refuse_boolean_narrowing_or_undeclared_SR_bits(field,value):
    case=dict(matrix.DEFAULTS,index=0,entry=0x52034,kind='controlled');case[field]=value
    with pytest.raises(ValueError):matrix.require_case(case)


def test_inputs_refuse_an_independent_duplicate_for_an_aliased_threshold_word():
    case=dict(matrix.DEFAULTS,index=0,entry=0x52034,kind='controlled',threshold_word_000=123)
    with pytest.raises(ValueError):matrix.require_case(case)


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_source_refuses_identity_geometry_scale_units_caller_hardware_or_publication(tmp_path,flag):
    p=tmp_path/contract.DESCRIPTOR;p.parent.mkdir(parents=True)
    p.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_published_component_joint_writer_alias_and_prior_source_counts_bind_execution_sources():
    declared=withdrawal.descriptor(repo.ROOT);rows=[r for r in declared['reference'] if r['component']=='indexed_word_update_paths']
    text=(repo.ROOT/'defs/JK08A.indexed-word-update-paths.md').read_text();words=' '.join(text.split())
    assert len(rows)==1 and len(declared['reference'])==127 and len(declared['function'])==68
    assert len({r['owner'] for r in declared['reference']})==97
    assert [line for line in text.splitlines() if line.startswith('| `7mfk:')]==[
        '| `7mfk:'+f'{r["address"]:08x}'+'` | `7mfk:'+f'{r["function"]:08x}'+'` | `'+r['original_claim_sha256']+'` |' for r in rows]
    for phrase,actual,wanted in (('92 stock instructions',sum((b-a)//2 for a,b in contract.SPANS),92),
        ('184 code bytes',sum(b-a for a,b in contract.SPANS),184),('11 literal/configuration spans',len(contract.UNIT['pools']),11),
        ('4 pointer aliases',len(contract.UNIT['aliases']),4),('2 typed configuration bytes',len(contract.CONFIGURATION),2),
        ('6 two-sided conditional sites',len(proof.REQUIRED_BRANCHES),6)):
        assert phrase in words and actual==wanted
    state=[r for r in matrix.RAM_FIELDS if r[0].startswith('state_word_')]
    counters=[r for r in matrix.RAM_FIELDS if r[0].startswith('counter_word_')]
    assert len(state)==332 and len(counters)==256 and matrix.WORD_VIEWS=={'delta':(0,256),'threshold':(76,256)}
    assert '332 authoritative state words' in words and '256 independent counter words' in words
    assert '76-word offset' in words and '128 complete SR contexts' in words
    assert withdrawal.ORIGINAL_LINK_TYPES=={'00052034-ffff120e-withdraw':'writer','0006e3d8-ffff1300-withdraw':'writer','0006e3d8-ffff1f86-withdraw':'writer'}
    assert json.loads(rows[0]['original_claim_json'])['type']=='writer'
    assert all(json.loads(r['original_claim_json'])['type']=='reader' for r in declared['reference'][:40])
    assert withdrawal.digest(withdrawal.prior_reference_rows(declared,40))==withdrawal.PRIOR_RPM_STATE_REFERENCE_SHA256
    assert withdrawal.digest(declared['function'][:30])==withdrawal.PRIOR_RPM_STATE_FUNCTION_SHA256
    owners={r['owner']:r for r in declared['reference']}
    removed=sum(sum(len(m.get('dependency',())) for m in (json.loads(r['original_ledger_json']) or ()))-
        sum(len(m.get('dependency',())) for m in (json.loads(r['proposed_ledger_json']) or ())) for r in owners.values())
    removed+=sum(sum(len(marker.get('dependency',())) for marker in json.loads(row['original_ledger_json']))-
        sum(len(marker.get('dependency',())) for marker in json.loads(row['proposed_ledger_json']))
        for row in declared['function'] if 'proposed_ledger_json' in row)
    assert removed==119 and '119 matching ledger selectors' in words
    image=repo.images()['JK08A'].path.read_bytes()
    assert sum(image[at:at+2]==b'\x00\x0b' for a,b in contract.SPANS for at in range(a,b,2))==1
    assert '1 natural RTS site' in words
    assert len(registry.FAMILIES)==13 and len(registry.captures())==47
    assert 'thirteen families and forty-seven capture bindings' in words
    assert proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)==12 and 'preceding twelve adapters' in words
    files={k:v for mapping in (withdrawal.PRIOR_FILES_SHA256,withdrawal.PRIOR_PRODUCT_FILES_SHA256,
        withdrawal.PRIOR_GATED_FILES_SHA256,withdrawal.PRIOR_RPM_RAM_FILES_SHA256,
        withdrawal.PRIOR_OVERFLOW_FILES_SHA256,withdrawal.PRIOR_WORD_FILES_SHA256,
        withdrawal.PRIOR_RPM_STATE_FILES_SHA256) for k,v in mapping.items()}
    assert len(files)==63 and '63 prior domain sources' in words
    assert len(files)-sum(name==withdrawal.GATED_ASSEMBLY_SOURCE_REPAIR['path'] for name in files)==62
    assert '62 byte-identical sources' in words
    for name,sha in files.items():assert hashlib.sha256(withdrawal.prior_gated_source_bytes(repo.ROOT,name)).hexdigest()==sha
