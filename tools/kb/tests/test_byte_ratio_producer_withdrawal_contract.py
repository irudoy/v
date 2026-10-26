"""Complete variable ratio producer,real signed shift and final byte and exact prior source boundaries."""
import hashlib
import json
import pytest
from kb import repo,proof_adapter
from kb import ordinary_access_registry as registry
from kb import byte_ratio_producer_withdrawal_contract as contract,byte_ratio_producer_withdrawal_matrix as matrix
from kb import byte_ratio_producer_withdrawal_semantics as scalar,byte_ratio_producer_withdrawal_transfers as transfers
from kb import byte_ratio_producer_withdrawal_capture_evidence as proof,scalar_ram_leaf_withdrawal_contract as withdrawal


def evaluate(entry,**changes):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=entry,**changes)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    return scalar.evaluate(entry,matrix.memory(case),matrix.calibrations(source,image,case),
        matrix.context(source,case),case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)


@pytest.mark.parametrize('byte,word,numerator,gain,offset,publication',(
    (1,256,1,1,6,1024),(0,256,1,1,0,1),(0,256,1,1,1,1),(255,65535,65535,255,255,65535),
    (1,16,8738,1,0,1024),(1,15,8192,1,0,1024),(1,1,65535,255,0,32768),
    (1,256,0,0,0,0),(1,256,0,0,1,65535)))
def test_full_unsigned_product_divisor_ratio65536_split_and_real_final_byte_rules(byte,word,numerator,gain,offset,publication):
    value=evaluate(0x4AE6C,byte_17b8=byte,word_14dc=word,word_1630=numerator,
        config_884d=gain,config_8b6c=offset,word_11bc=publication)
    divisor=byte*word;first=65535 if divisor==0 else gain*120*numerator//divisor
    ratio=first+offset*5//2
    if ratio<65536:quotient=(((ratio*publication)&0xFFFFFFFF)>>10)*3//5
    else:
        product=(publication*65535)&0xFFFFFFFF;signed=product-2**32 if product&0x80000000 else product
        shifted=signed>>10;quotient=(abs(shifted*3)//5*(-1 if shifted<0 else 1))&0xFFFFFFFF
    expected=127 if quotient>141 else (quotient-14)&255
    assert value['ram'][0x23F1]==expected and value['known_registers'][0]==53
    assert any(row['target']==0x22508 for row in value['calls'])==(ratio>=65536)
    if divisor:
        first_call=value['calls'][0]
        assert first_call['target']==0x21CE0 and first_call['divisor']==divisor and first_call['dividend']==gain*120*numerator
        assert first_call['large_divisor']==(divisor>65535)
    assert value['sp']==0x02001000 and value['pr']==0x02100000


@pytest.mark.parametrize('word',(0,1,2,3,4,6,7,32767,32768,32769,65528,65534,65535))
def test_real22508_keeps_signed_shift10_and_preserved_R1_without_a_narrowed_word_product(word):
    value=evaluate(0x4AE6C,byte_17b8=0,config_8b6c=1,word_11bc=word)
    shift=next(row for row in value['calls'] if row['target']==0x22508)
    product=(word*65535)&0xFFFFFFFF;signed=product-2**32 if product&0x80000000 else product
    assert shift['registers'][0]==product and shift['return_registers'][0]==(signed>>10)&0xFFFFFFFF
    assert shift['return_registers'][1]==shift['registers'][1]
    divider=next(row for row in value['calls'] if row['target']==0x21BBC)
    assert divider['divisor']==5 and divider['dividend']==((signed>>10)*3)&0xFFFFFFFF
    assert value['opaque_frame_sites']==()


def test_post_division_R1_stays_numerically_unknown_but_its_two_real_saved_frame_operands_are_explicit():
    value=evaluate(0x4AE6C,byte_17b8=1,word_14dc=15,word_1630=8192,config_884d=1,config_8b6c=0)
    assert value['opaque_frame_sites']==(0x22508,0x22518)
    rows=[row for row in value['events'].values() if row['bytes'] is None]
    assert [(row['site'],row['mode'],row['address'],row['width_bytes'],row['register']) for row in rows]==[
        (0x22508,'write',0x02001000-12,4,1),(0x22518,'read',0x02001000-12,4,1)]
    shift=next(row for row in value['calls'] if row['target']==0x22508)
    assert shift['registers'][1] is None and shift['return_registers'][1] is None
    overwrite=next(row for row in value['events'].values() if row['site']==0x21BBC)
    assert overwrite['address']==0x02001000-12 and overwrite['bytes']=='00000400'


def test_zero_final_quotient_keeps_the_actual_subtract14_byte_underflow():
    value=evaluate(0x4AE6C,word_1630=0,word_11bc=0,config_8b6c=0)
    assert value['ram'][0x23F1]==242 and value['known_registers'][6]==0xFFFFFFF2
    assert value['known_registers'][0]==53


@pytest.mark.parametrize('field,raw',(('byte_17b8',True),('byte_17b8',256),('word_14dc',65536),
    ('word_11bc',65536),('config_884d',256),('config_8b6c',256),('dword_9818',1<<32),('raw_r6',1<<32),('initial_sr',2)))
def test_all_raw_byte_word_dword_register_configuration_and_SR_inputs_refuse_narrowing(field,raw):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x4AE6C);case[field]=raw
    with pytest.raises(ValueError):matrix.require_case(case)


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_source_refuses_identity_geometry_scale_units_caller_hardware_stub_or_publication(tmp_path,flag):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    path.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('root',transfers.NATIVE_ROOTS)
@pytest.mark.parametrize('form',('native','alias','overlapping-interval'))
@pytest.mark.parametrize('domain',('ram','rom','frame'))
def test_selected_ROM_native_RAM_and_alias_roots_require_exact_physical_interval_absence(root,form,domain):
    rows=[row for row in withdrawal.descriptor(repo.ROOT)['reference'] if row['component']=='byte_ratio_producer_withdrawal_paths']
    identity,address,alias=root
    if form=='alias':
        if alias is None:pytest.skip('the selected ROM root has no RAM alias')
        address=alias
    width=1
    if form=='overlapping-interval':address-=1;width=2
    with pytest.raises(ValueError):transfers.require_no_selected_datum(dict(accesses=[dict(site=0x4AF36,
        address=address,width_bytes=width,domain=domain)]),rows)


@pytest.mark.parametrize('name',tuple(contract.REUSED_HELPER_FILES_SHA256))
def test_each_complete_previous_helper_source_is_exact(monkeypatch,name):
    read=__import__('pathlib').Path.read_bytes
    monkeypatch.setattr(__import__('pathlib').Path,'read_bytes',lambda path:read(path)+b'\n' if path==repo.ROOT/name else read(path))
    with pytest.raises(ValueError):contract.require_reused_helper_boundary(repo.ROOT)


def test_fixture_keeps_the_full_caller_and_all_three_actual_helpers_with_only_five_exact_pointer_aliases():
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(declared,image);restored=bytearray(fixture)
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert len(aliases)==5 and bytes(restored)==image
    assert contract.HELPER_ENTRIES==(0x21BBC,0x21CE0,0x22508)
    assert len(contract.CONFIGURATION)==2 and contract.INPUT_BLOBS==[]
    from kb.test_stock_capture import tool
    producer=tool(repo.ROOT,'byte_ratio_producer_withdrawal_capture.py','_kb_byte_ratio_producer_source_contract')
    assert declared['adapter']['marker']==producer.MARKER=='VQ_SH_ELF_BYTE_RATIO_PRODUCER_WITHDRAWAL'
    proof_adapter.require_generated(repo.ROOT,contract.DESCRIPTOR)


def test_published_byte_ratio_joint_prior_and_registry_counts_bind_execution_sources():
    declared=withdrawal.descriptor(repo.ROOT);rows=[row for row in declared['reference'] if row['component']=='byte_ratio_producer_withdrawal_paths']
    text=(repo.ROOT/'defs/JK08A.byte-ratio-producer-withdrawal-paths.md').read_text();words=' '.join(text.split())
    assert len(rows)==1 and len(declared['reference'])==126 and len(declared['function'])==68
    assert len({row['owner'] for row in declared['reference']})==96
    assert [line for line in text.splitlines() if line.startswith('| `7mfk:')]==[
        '| `7mfk:'+f'{row["address"]:08x}'+'` | `7mfk:'+f'{row["function"]:08x}'+'` | `'+row['original_claim_sha256']+'` |' for row in rows]
    for phrase,actual,wanted in (('355 stock instructions',sum((last-first)//2 for first,last in contract.SPANS),355),
        ('710 code bytes',sum(last-first for first,last in contract.SPANS),710),('5 code spans',len(contract.SPANS),5),
        ('296 feasible instructions',len(transfers.FEASIBLE_SITES),296),('59 excluded instructions',len(transfers.INFEASIBLE_SITES),59),
        ('17 literal spans',len(contract.UNIT['pools']),17),('5 pointer aliases',len(contract.UNIT['aliases']),5),
        ('6 complete RAM fields',len(matrix.RAM_FIELDS),6),('2 scalar configuration fields',len(contract.CONFIGURATION),2),
        ('17 complete calibration spans',len(contract.CONTROLLED_CALIBRATION),17),('18 raw input fields',len(matrix.WIDTHS),18),
        ('7 complete helper sources',len(contract.REUSED_HELPER_FILES_SHA256),7)):
        assert phrase in words and actual==wanted
    assert len(proof.REQUIRED_BRANCHES)==9 and '9 two-sided conditions' in words
    assert len(proof.FIXED_BRANCHES)==4 and '4 fixed conditions' in words
    owners={row['owner']:row for row in declared['reference']}
    datum_removed=sum(sum(len(marker.get('dependency',())) for marker in (json.loads(row['original_ledger_json']) or ()))-
        sum(len(marker.get('dependency',())) for marker in (json.loads(row['proposed_ledger_json']) or ())) for row in owners.values())
    function_removed=sum(sum(len(marker.get('dependency',())) for marker in json.loads(row['original_ledger_json']))-
        sum(len(marker.get('dependency',())) for marker in json.loads(row['proposed_ledger_json']))
        for row in declared['function'] if 'proposed_ledger_json' in row)
    assert datum_removed==110 and function_removed==8 and datum_removed+function_removed==118
    assert '118 matching ledger selectors' in words and '110 datum-end selectors and 8 function-end selectors' in words
    assert len(withdrawal.NATIVE_LINK_ROLES)==19 and len(withdrawal.ORIGINAL_LINK_TYPES)==10
    assert sum(json.loads(row['original_claim_json'])['type']=='reader' for row in declared['reference'])==115
    assert '116 readers and ten' in words
    from kb import scalar_ram_leaf_withdrawal_evidence as family
    assert len(family.COMPONENTS)==27 and 'Twenty-seven independent components' in words
    assert len({row['component'] for row in declared['reference'] if row['owner'].endswith('/ram')})==16
    assert withdrawal.state_surface_prefix_digest(declared,118)==withdrawal.PRIOR_PAIRED_CURVE_NORMALIZATION_REFERENCE_SHA256
    assert withdrawal.digest(declared['function'][:62])==withdrawal.PRIOR_PAIRED_CURVE_NORMALIZATION_FUNCTION_SHA256
    assert len(registry.FAMILIES)==13 and len(registry.captures())==47
    assert 'thirteen families and forty-seven capture bindings' in words
    assert proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)==28 and 'preceding twenty-eight adapters' in words
    files={name:sha for mapping in (withdrawal.PRIOR_FILES_SHA256,withdrawal.PRIOR_PRODUCT_FILES_SHA256,withdrawal.PRIOR_GATED_FILES_SHA256,withdrawal.PRIOR_RPM_RAM_FILES_SHA256,withdrawal.PRIOR_OVERFLOW_FILES_SHA256,withdrawal.PRIOR_WORD_FILES_SHA256,withdrawal.PRIOR_RPM_STATE_FILES_SHA256,withdrawal.PRIOR_INDEXED_WORD_FILES_SHA256,withdrawal.PRIOR_DIVISION_CALLER_FILES_SHA256,withdrawal.PRIOR_BYTE_CURVE_CALLER_FILES_SHA256,withdrawal.PRIOR_WORD_INTERP_CALLER_FILES_SHA256,withdrawal.PRIOR_SCALED_DIVISION_FILES_SHA256,withdrawal.PRIOR_CURVE_SCALE_CALLER_FILES_SHA256,withdrawal.PRIOR_DERIVATIVE_SCALE_CALLER_FILES_SHA256,withdrawal.PRIOR_GUARDED_QUOTIENT_CALLER_FILES_SHA256,withdrawal.PRIOR_MIXED_CURVE_CALLER_FILES_SHA256,withdrawal.PRIOR_TIMING_REMAINDER_CALLER_FILES_SHA256,withdrawal.PRIOR_STATE_RATIO_CALLER_FILES_SHA256,withdrawal.PRIOR_DFCO_STATE_CALLER_FILES_SHA256,withdrawal.PRIOR_PAIRED_INHIBIT_WRITER_FILES_SHA256,withdrawal.PRIOR_THRESHOLD_WINDOW_READER_FILES_SHA256,withdrawal.PRIOR_AUX_RATE_CALLER_FILES_SHA256,withdrawal.PRIOR_PAIRED_CURVE_NORMALIZATION_FILES_SHA256,) for name,sha in mapping.items()}
    assert len(files)==207 and '207 prior domain sources' in words and '206 byte-identical sources' in words
    for name,sha in files.items():assert hashlib.sha256(withdrawal.prior_gated_source_bytes(repo.ROOT,name)).hexdigest()==sha
