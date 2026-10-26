"""Exact exposure, byte-promotion, transition priority and native-source contracts."""

import hashlib
import json
import pytest
from kb import repo,proof_adapter
from kb import ordinary_access_registry as registry
from kb import rpm_state_withdrawal_contract as contract,rpm_state_withdrawal_matrix as matrix
from kb import rpm_state_withdrawal_semantics as scalar,rpm_state_withdrawal_transfers as transfers
from kb import rpm_state_withdrawal_capture_evidence as proof,scalar_ram_leaf_withdrawal_contract as withdrawal


def evaluate(entry,**changes):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=entry,**changes)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    return scalar.evaluate(entry,matrix.memory(case),matrix.calibrations(source,image,case),
        matrix.context(source,case),case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)


@pytest.mark.parametrize('exposure,changes,expected,t',((500,{},512,False),
    (1199,{},1200,True),(1,dict(boundary_state=5),0,True),(0,dict(boundary_state=5),0,False),
    (500,dict(reset_flags=4),0,False),(500,dict(limit_flags=64),0,True),
    (2000,dict(limit_flags=64),2000,False),(500,dict(mode_flags=1),0,True),
    (65535,dict(exposure_base=65535,exposure_step=255),65535,True)))
def test_exposure_product_cap_reset_decrement_floor_and_retention(exposure,changes,expected,t):
    value=evaluate(0x4F7E0,exposure=exposure,**changes)
    assert int.from_bytes(value['ram'][0x1932:0x1934],'big')==expected
    assert bool(value['sr']&1)==t and value['path'][-2:]==(0x4F902,0x4F904)


def test_disabled_exposure_keeps_the_complete_signed_mask_and_other_incoming_registers():
    value=evaluate(0x4F7E0,disable_mask=128,raw_r2=0x12345678)
    assert value['registers'][0]==0xFFFFFF80 and value['registers'][2]==0x12345678
    assert value['registers'][6]==0x8B3F and int.from_bytes(value['ram'][0x1932:0x1934],'big')==500
    assert value['sr']&1==0 and value['tags']['physical_writes']=={}


@pytest.mark.parametrize('state,threshold,expected',((128,127,499),(127,128,512)))
def test_boundary_byte_operands_keep_signed_promotion_before_unsigned32_comparison(state,threshold,expected):
    value=evaluate(0x4F7E0,boundary_state=state,boundary_threshold=threshold)
    assert int.from_bytes(value['ram'][0x1932:0x1934],'big')==expected


@pytest.mark.parametrize('changes,clock,latch,result',(({},6,128,1),
    (dict(reset_flags=4,transition_latch=128),255,0,0),
    (dict(edge_flags=4),0,128,1),(dict(transition_clock=255),255,0,0),
    (dict(transition_latch=128,rpm=80),255,0,0),
    (dict(transition_latch=128,restore_count=0),255,0,0),
    (dict(transition_flags=64),6,0,0),(dict(mode_flags=1),6,0,0),
    (dict(disable_mask=128,transition_latch=255),5,127,0)))
def test_transition_clock_priority_restore_entry_and_disable(changes,clock,latch,result):
    value=evaluate(0x4F9C4,**changes)
    assert (value['ram'][0x1690],value['ram'][0x2497],value['registers'][0])==(clock,latch,result)
    assert bool(value['sr']&1)==(not bool(latch&128))
    assert value['path'][-2:]==(0x4FA98,0x4FA9A)


@pytest.mark.parametrize('rpm,threshold,latch',((128,127,128),(127,128,0)))
def test_transition_entry_retains_actual_sign_extended_unsigned32_byte_comparison(rpm,threshold,latch):
    value=evaluate(0x4F9C4,rpm=rpm,entry_rpm=threshold)
    assert value['ram'][0x2497]==latch


def test_restore_retains_the_distinct_first_increment_and_following_clock_reset():
    value=evaluate(0x4F9C4,transition_latch=128,rpm=80)
    assert value['tags']['physical_writes']=={0x4FA10:b'\x06',0x4FA34:b'\x00',0x4FA3E:b'\xff'}
    assert value['tags']['physical_reads'][0x4FA8E]==b'\x00'
    assert value['ram'][0x1690]==255


def test_complete_disjoint_fixture_excludes_the_embedded_data_word_and_preserves_native_instructions():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image);restored=bytearray(fixture)
    assert len(contract.SPANS)==3 and not any(a<=0x4F8D4<b for a,b in contract.SPANS)
    assert any(r['address']==0x4F8D4 and r['size']==2 for r in contract.UNIT['pools'])
    for a,b in contract.SPANS:assert fixture[a:b]==image[a:b]
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert len(aliases)==13 and bytes(restored)==image
    text=(repo.ROOT/contract.UNIT['assembly']).read_text()
    assert 'L_0004f8d4:' not in text and 'P_0004f8d4:' in text
    assert 'shll 2 ' not in text and 'shlr 2 ' not in text


def test_producer_and_input_only_adapter_have_one_exact_terminal_marker():
    from kb.test_stock_capture import tool
    producer=tool(repo.ROOT,'rpm_state_withdrawal_capture.py','_kb_rpm_state_producer_source_contract')
    source=contract.descriptor(repo.ROOT)
    assert source['adapter']['marker']==producer.MARKER=='VQ_SH_ELF_RPM_STATE_WITHDRAWAL'
    assert source['adapter']['region']==producer.REGION and source['adapter']['prefix']==producer.PREFIX
    proof_adapter.require_generated(repo.ROOT,contract.DESCRIPTOR)


@pytest.mark.parametrize('root',transfers.NATIVE_RAM_ROOTS)
@pytest.mark.parametrize('form',('native','alias','overlapping-interval'))
@pytest.mark.parametrize('domain',('ram','rom','frame'))
def test_selected_native_RAM_and_alias_absence_does_not_depend_on_event_domain(root,form,domain):
    rows=[r for r in withdrawal.descriptor(repo.ROOT)['reference'] if r['component']=='rpm_state_withdrawal_paths']
    original,native,alias=root;at=native if form=='native' else alias;width=1
    if form=='overlapping-interval':at-=1;width=2
    with pytest.raises(ValueError):transfers.require_no_selected_datum(dict(accesses=[dict(site=0x4F822,address=at,width_bytes=width,domain=domain)]),rows)


@pytest.mark.parametrize('field,value',(('exposure',65536),('exposure_base',-1),('rpm',True),
    ('transition_clock',256),('disable_mask',256),('raw_r4',1<<32),('initial_sr',2)))
def test_input_refuses_narrowing_boolean_signed_or_changed_SR_domains(field,value):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x4F7E0);case[field]=value
    with pytest.raises(ValueError):matrix.require_case(case)


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_source_refuses_owning_identity_units_geometry_scale_caller_hardware_or_publication(tmp_path,flag):
    p=tmp_path/contract.DESCRIPTOR;p.parent.mkdir(parents=True)
    p.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_published_component_joint_role_and_prior_source_counts_bind_current_execution_files():
    declared=withdrawal.descriptor(repo.ROOT);rows=[r for r in declared['reference'] if r['component']=='rpm_state_withdrawal_paths']
    text=(repo.ROOT/'defs/JK08A.rpm-state-withdrawal-paths.md').read_text();words=' '.join(text.split())
    assert len(rows)==2 and len(declared['reference'])==134 and len(declared['function'])==74
    assert len({r['owner'] for r in declared['reference']})==100
    assert [line for line in text.splitlines() if line.startswith('| `7mfk:')]==[
        '| `7mfk:'+f'{r["address"]:08x}'+'` | `7mfk:'+f'{r["function"]:08x}'+'` | `'+r['original_claim_sha256']+'` |' for r in rows]
    for phrase,actual,wanted in (('254 stock instructions',sum((b-a)//2 for a,b in contract.SPANS),254),
        ('508 code bytes',sum(b-a for a,b in contract.SPANS),508),('3 disjoint code spans',len(contract.SPANS),3),
        ('35 literal/configuration spans',len(contract.UNIT['pools']),35),('13 pointer aliases',len(contract.UNIT['aliases']),13),
        ('13 typed configuration operands',len(contract.CONFIGURATION),13),('30 two-sided conditional sites',len(proof.REQUIRED_BRANCHES),30)):
        assert phrase in words and actual==wanted
    assert len(withdrawal.NATIVE_LINK_ROLES)==19 and all(json.loads(r['original_claim_json'])['roles']==['indexed_by'] for r in rows)
    assert withdrawal.digest(declared['function'][:28])==withdrawal.PRIOR_WORD_FUNCTION_SHA256
    for row in rows:
        assert not any(withdrawal.selector(row,row['owner'],item)
            for marker in (json.loads(row['original_ledger_json']) or ()) for item in marker.get('dependency',()))
    image=repo.images()['JK08A'].path.read_bytes()
    assert sum(image[at:at+2]==b'\x00\x0b' for a,b in contract.SPANS for at in range(a,b,2))==2
    assert '2 natural RTS sites' in words
    owners={r['owner']:r for r in declared['reference']}
    removed=sum(sum(len(m.get('dependency',())) for m in (json.loads(r['original_ledger_json']) or ()))-
        sum(len(m.get('dependency',())) for m in (json.loads(r['proposed_ledger_json']) or ())) for r in owners.values())
    removed+=sum(sum(len(marker.get('dependency',())) for marker in json.loads(row['original_ledger_json']))-
        sum(len(marker.get('dependency',())) for marker in json.loads(row['proposed_ledger_json']))
        for row in declared['function'] if 'proposed_ledger_json' in row)
    assert removed==126 and '126 matching ledger selectors' in words
    assert len(registry.FAMILIES)==13 and len(registry.captures())==47
    assert 'thirteen families and forty-seven capture bindings' in words
    assert proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)==11 and 'preceding eleven adapters' in words
    files={k:v for mapping in (withdrawal.PRIOR_FILES_SHA256,withdrawal.PRIOR_PRODUCT_FILES_SHA256,
        withdrawal.PRIOR_GATED_FILES_SHA256,withdrawal.PRIOR_RPM_RAM_FILES_SHA256,
        withdrawal.PRIOR_OVERFLOW_FILES_SHA256,withdrawal.PRIOR_WORD_FILES_SHA256) for k,v in mapping.items()}
    assert len(files)==54 and '54 prior domain sources' in words
    assert len(files)-sum(name==withdrawal.GATED_ASSEMBLY_SOURCE_REPAIR['path'] for name in files)==53
    assert '53 byte-identical sources' in words
    for name,sha in files.items():assert hashlib.sha256(withdrawal.prior_gated_source_bytes(repo.ROOT,name)).hexdigest()==sha
