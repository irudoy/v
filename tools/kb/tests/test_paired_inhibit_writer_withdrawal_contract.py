"""Complete paired flag writers, raw byte comparisons, ordered RMW operands and exact prior source boundaries."""
import hashlib
import json
import pytest
from kb import repo,proof_adapter
from kb import ordinary_access_registry as registry
from kb import paired_inhibit_writer_withdrawal_contract as contract,paired_inhibit_writer_withdrawal_matrix as matrix
from kb import paired_inhibit_writer_withdrawal_semantics as scalar,paired_inhibit_writer_withdrawal_transfers as transfers
from kb import paired_inhibit_writer_withdrawal_capture_evidence as proof,scalar_ram_leaf_withdrawal_contract as withdrawal


def evaluate(entry,**changes):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=entry,**changes)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    return scalar.evaluate(entry,matrix.memory(case),matrix.calibrations(source,image,case),
        matrix.context(source,case),case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)


@pytest.mark.parametrize('entry',(0x7C8FA,0x7C9A8))
@pytest.mark.parametrize('raw',(0,1,4,63,64,127,128,255))
def test_every_physical_OR_AND_byte_keeps_both_preimage_and_masked_publication(entry,raw):
    value=evaluate(entry,**{field:raw for field in (*matrix.OR_FIELDS,*matrix.AND_FIELDS)})
    events=[event for rows in value['events'].values() for event in rows if event['site'] in transfers.RMW_SITES]
    assert len(events)==28
    for index in range(0,len(events),2):
        before,after=events[index:index+2]
        assert before['mode']=='read' and after['mode']=='write'
        assert before['site']==after['site'] and before['address']==after['address']
        assert before['width_bytes']==after['width_bytes']==1 and before['register'] is after['register'] is None
        assert before['bytes']==f'{raw:02x}'
        field=f"byte_{before['address']&65535:04x}"
        wanted=raw|4 if field in matrix.OR_FIELDS else raw&0xBF
        assert after['bytes']==f'{wanted:02x}' and value['ram'][before['address']&65535]==wanted


@pytest.mark.parametrize('entry',(0x7C8FA,0x7C9A8))
@pytest.mark.parametrize('flag',(0,1,15,31,32,33,42,63,64,127,128,129,255))
def test_real_helper_retains_raw_blocker_gate_low_nibble_and_natural_return(entry,flag):
    value=evaluate(entry,byte_5b33=flag)
    called=bool(flag&32) and not bool(flag&128)
    assert len(value['calls'])==int(called)
    assert value['ram'][0x5B33]==(flag&15 if called else flag)
    if called:
        call=value['calls'][0]
        assert call['target']==0x7D84C and call['return_site']==0x7D852
        assert call['return_registers'][0]==flag&15
        assert any(row['site']==0x7D854 and row['mode']=='write' for rows in value['events'].values() for row in rows)
    assert value['gbr']==matrix.context(contract.descriptor(repo.ROOT),dict(matrix.DEFAULTS,index=0,kind='controlled',entry=entry))[15]
    assert value['pr']==0x02100000 and value['sp']==0x02001000


@pytest.mark.parametrize('coordinate,threshold,blocked',((0,0,True),(1,4,False),(4,4,True),
    (127,128,False),(128,127,True),(128,255,False),(255,128,True),(255,255,True)))
def test_MOVB_sign_extension_precedes_raw_unsigned_threshold_comparison(coordinate,threshold,blocked):
    value=evaluate(0x7C9A8,byte_3118=coordinate,config_885d=threshold)
    branch=next(row for row in value['controls'] if row['site']==0x7C9CE)
    assert branch['kind']==('taken' if blocked else 'fallthrough')
    assert value['known_registers'][0]==(0x820 if blocked else 10)
    assert len(value['calls'])==int(not blocked)


def test_real_writes_stay_with_their_exact_first_or_second_entry():
    first=evaluate(0x7C8FA);second=evaluate(0x7C9A8)
    for value,cleared,retained in ((first,(0x4AC6,0x4A45,0x4A70,0x48C2),(0x4AC8,0x4A47,0x4A74,0x48C4)),
        (second,(0x4AC8,0x4A47,0x4A74,0x48C4),(0x4AC6,0x4A45,0x4A70,0x48C2))):
        assert all(value['ram'][address]==0 for address in cleared)
        assert all(value['ram'][address]!=0 for address in retained)
    assert first['ram'][0x4A70:0x4A72]==second['ram'][0x4A74:0x4A76]==bytes(2)


@pytest.mark.parametrize('field,value',(('byte_41c5',True),('byte_3118',256),('config_885d',256),
    ('word_4a70',65536),('raw_r6',1<<32),('initial_sr',2)))
def test_raw_flags_RMW_word_outputs_registers_and_SR_refuse_narrowing(field,value):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x7C8FA);case[field]=value
    with pytest.raises(ValueError):matrix.require_case(case)


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_source_refuses_identity_geometry_scale_units_caller_hardware_stub_or_publication(tmp_path,flag):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    path.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('scope',transfers.NATIVE_FUNCTION_SCOPES)
@pytest.mark.parametrize('form',('native','alias','overlapping-interval'))
@pytest.mark.parametrize('domain',('ram','rom','frame'))
def test_selected_root_interval_absence_uses_exact_function_native_and_alias_scope(scope,form,domain):
    rows=[row for row in withdrawal.descriptor(repo.ROOT)['reference'] if row['component']=='paired_inhibit_writer_withdrawal_paths']
    identity,entry,native,alias=scope;address=alias if form=='alias' else native;width=1
    if form=='overlapping-interval':address-=1;width=2
    result=dict(trace=[dict(site=entry)],accesses=[dict(site=entry,address=address,width_bytes=width,domain=domain)])
    with pytest.raises(ValueError):transfers.require_no_selected_datum(result,rows,entry)


def test_other_entry_real_stores_remain_admitted_but_an_unscoped_global_absence_does_not():
    rows=[row for row in withdrawal.descriptor(repo.ROOT)['reference'] if row['component']=='paired_inhibit_writer_withdrawal_paths']
    result=dict(trace=[dict(site=0x7C8FA)],accesses=[dict(site=site,address=address,width_bytes=width)
        for site,address,width in ((0x7C96C,0x01004AC6,1),(0x7C970,0x01004A45,1),(0x7C974,0x01004A70,2))])
    transfers.require_no_selected_datum(result,rows,0x7C8FA)
    with pytest.raises(ValueError):transfers.require_no_selected_datum(result,rows,0x7C9A8)


def test_fixture_keeps_both_complete_callers_and_the_real_delay_slot_helper():
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(declared,image);restored=bytearray(fixture)
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert len(aliases)==6 and bytes(restored)==image
    assert contract.SPANS==((0x7C8FA,0x7C9A8),(0x7C9A8,0x7CA58),(0x7D84C,0x7D856))
    assert contract.HELPER_ENTRIES==(0x7D84C,) and contract.INPUT_BLOBS==[]
    from kb.test_stock_capture import tool
    producer=tool(repo.ROOT,'paired_inhibit_writer_withdrawal_capture.py','_kb_paired_flag_producer_source_contract')
    assert declared['adapter']['marker']==producer.MARKER=='VQ_SH_ELF_PAIRED_INHIBIT_WRITER_WITHDRAWAL'
    proof_adapter.require_generated(repo.ROOT,contract.DESCRIPTOR)


def test_published_paired_writer_joint_prior_and_registry_counts_bind_execution_sources():
    declared=withdrawal.descriptor(repo.ROOT);rows=[row for row in declared['reference'] if row['component']=='paired_inhibit_writer_withdrawal_paths']
    text=(repo.ROOT/'defs/JK08A.paired-inhibit-writer-withdrawal-paths.md').read_text();words=' '.join(text.split())
    assert len(rows)==5 and len(declared['reference'])==123 and len(declared['function'])==66
    assert len({row['owner'] for row in declared['reference']})==94
    assert [line for line in text.splitlines() if line.startswith('| `7mfk:')]==[
        '| `7mfk:'+f'{row["address"]:08x}'+'` | `7mfk:'+f'{row["function"]:08x}'+'` | `'+row['original_claim_sha256']+'` |' for row in rows]
    for phrase,actual,wanted in (('180 stock instructions',sum((last-first)//2 for first,last in contract.SPANS),180),
        ('360 code bytes',sum(last-first for first,last in contract.SPANS),360),('3 code spans',len(contract.SPANS),3),
        ('180 feasible instructions',len(transfers.FEASIBLE_SITES),180),('17 literal spans',len(contract.UNIT['pools']),17),
        ('6 pointer aliases',len(contract.UNIT['aliases']),6),('33 complete RAM fields',len(matrix.RAM_FIELDS),33),
        ('1 configuration field',len(contract.CONFIGURATION),1),('17 complete calibration spans',len(contract.CONTROLLED_CALIBRATION),17),
        ('44 raw input fields',len(matrix.WIDTHS),44),('28 physical RMW sites',len(transfers.RMW_SITES),28)):
        assert phrase in words and actual==wanted
    assert f'{len(proof.REQUIRED_BRANCHES)} two-sided conditions' in words and proof.FIXED_BRANCHES=={}
    assert transfers.FEASIBLE_SITES==transfers.EXACT_SITES
    owners={row['owner']:row for row in declared['reference']}
    datum_removed=sum(sum(len(marker.get('dependency',())) for marker in (json.loads(row['original_ledger_json']) or ()))-
        sum(len(marker.get('dependency',())) for marker in (json.loads(row['proposed_ledger_json']) or ())) for row in owners.values())
    function_removed=sum(sum(len(marker.get('dependency',())) for marker in json.loads(row['original_ledger_json']))-
        sum(len(marker.get('dependency',())) for marker in json.loads(row['proposed_ledger_json']))
        for row in declared['function'] if 'proposed_ledger_json' in row)
    assert datum_removed==108 and function_removed==7 and datum_removed+function_removed==115
    assert '115 matching ledger selectors' in words and '108 datum-end selectors and 7 function-end selectors' in words
    assert len(withdrawal.NATIVE_LINK_ROLES)==18 and len(withdrawal.ORIGINAL_LINK_TYPES)==10
    assert sum(json.loads(row['original_claim_json'])['type']=='reader' for row in declared['reference'])==113
    assert '113 readers and ten' in words
    from kb import scalar_ram_leaf_withdrawal_evidence as family
    assert len(family.COMPONENTS)==27 and 'Twenty-seven independent components' in words
    assert len({row['component'] for row in declared['reference'] if row['owner'].endswith('/ram')})==16
    for name in ('tools/kb/README.md','tools/kb/SPEC.md','tools/sh-elf-run/README.md','tools/kb/ordinary-access.md'):
        assert 'Fourteen native-RAM components' in ' '.join((repo.ROOT/name).read_text().split())
    assert withdrawal.digest(withdrawal.prior_reference_rows(declared,107))==withdrawal.PRIOR_DFCO_STATE_CALLER_REFERENCE_SHA256
    assert withdrawal.digest(declared['function'][:56])==withdrawal.PRIOR_DFCO_STATE_CALLER_FUNCTION_SHA256
    assert len(registry.FAMILIES)==13 and len(registry.captures())==47
    assert 'thirteen families and forty-seven capture bindings' in words
    assert proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)==24 and 'preceding twenty-four adapters' in words
    mappings=(withdrawal.PRIOR_FILES_SHA256,withdrawal.PRIOR_PRODUCT_FILES_SHA256,withdrawal.PRIOR_GATED_FILES_SHA256,withdrawal.PRIOR_RPM_RAM_FILES_SHA256,withdrawal.PRIOR_OVERFLOW_FILES_SHA256,withdrawal.PRIOR_WORD_FILES_SHA256,withdrawal.PRIOR_RPM_STATE_FILES_SHA256,withdrawal.PRIOR_INDEXED_WORD_FILES_SHA256,withdrawal.PRIOR_DIVISION_CALLER_FILES_SHA256,withdrawal.PRIOR_BYTE_CURVE_CALLER_FILES_SHA256,withdrawal.PRIOR_WORD_INTERP_CALLER_FILES_SHA256,withdrawal.PRIOR_SCALED_DIVISION_FILES_SHA256,withdrawal.PRIOR_CURVE_SCALE_CALLER_FILES_SHA256,withdrawal.PRIOR_DERIVATIVE_SCALE_CALLER_FILES_SHA256,withdrawal.PRIOR_GUARDED_QUOTIENT_CALLER_FILES_SHA256,withdrawal.PRIOR_MIXED_CURVE_CALLER_FILES_SHA256,withdrawal.PRIOR_TIMING_REMAINDER_CALLER_FILES_SHA256,withdrawal.PRIOR_STATE_RATIO_CALLER_FILES_SHA256,withdrawal.PRIOR_DFCO_STATE_CALLER_FILES_SHA256,)
    files={name:sha for mapping in mappings for name,sha in mapping.items()}
    assert len(files)==171 and '171 prior domain sources' in words and '170 byte-identical sources' in words
    for name,sha in files.items():assert hashlib.sha256(withdrawal.prior_gated_source_bytes(repo.ROOT,name)).hexdigest()==sha
