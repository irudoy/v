"""Complete raw threshold-window caller,real division and local frame lineage and exact prior source boundaries."""
import hashlib
import json
import pytest
from kb import repo,proof_adapter
from kb import ordinary_access_registry as registry
from kb import threshold_window_reader_withdrawal_contract as contract,threshold_window_reader_withdrawal_matrix as matrix
from kb import threshold_window_reader_withdrawal_semantics as scalar,threshold_window_reader_withdrawal_transfers as transfers
from kb import threshold_window_reader_withdrawal_capture_evidence as proof,scalar_ram_leaf_withdrawal_contract as withdrawal


def evaluate(entry,**changes):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=entry,**changes)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    return scalar.evaluate(entry,matrix.memory(case),matrix.calibrations(source,image,case),
        matrix.context(source,case),case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)


@pytest.mark.parametrize('coordinate,measured,inside',((0,0,True),(0,29,True),(0,30,False),
    (29,0,True),(30,0,True),(31,0,False),(100,69,False),(100,70,True),(100,129,True),(100,130,False),
    (225,194,False),(225,195,True),(225,254,True),(225,255,False),(285,255,False),(65535,65535,False)))
def test_raw_low_word_coordinate_retains_lower_zero_clip_upper255_clip_and_exclusive_upper_bound(coordinate,measured,inside):
    value=evaluate(0x847DC,raw_r4=0xA5C30000|coordinate,word_11bc=measured)
    assert value['known_registers'][0]==int(inside)
    assert value['known_registers'][13]==matrix.context(contract.descriptor(repo.ROOT),
        dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x847DC,raw_r4=0xA5C30000|coordinate,word_11bc=measured))[13]


@pytest.mark.parametrize('source,measured,inside',((0,0,False),(100,79,False),(100,80,True),
    (100,119,True),(100,120,False),(214,170,False),(214,171,True),(214,255,True),(255,203,False),(255,204,True),(255,255,True)))
def test_two_real_signed_divisions_retain_distinct_byte_numerators_floor_thresholds_and_short_long_paths(source,measured,inside):
    value=evaluate(0x847DC,raw_r5=0xB6D40000|source,byte_413e=measured)
    assert value['known_registers'][0]==int(inside)
    calls=value['calls'];assert calls and calls[0]['divisor']==10 and calls[0]['dividend']==source*8
    assert calls[0]['return_registers'][0]==source*8//10
    if len(calls)==2:
        assert calls[1]['divisor']==10 and calls[1]['dividend']==source*12
        assert calls[1]['return_registers'][0]==source*12//10
        assert calls[1]['long_path']==(source*12>=2560)
    assert all(call['quotient_sign_flag'] is False for call in calls)


@pytest.mark.parametrize('incoming,held',((0,0),(0,110),(109,109),(109,110),(110,109),(110,110),(128,255),(255,128)))
def test_110_split_uses_unsigned_bytes_and_preserves_raw_saved_R12(incoming,held):
    value=evaluate(0x847DC,raw_r6=0xC7E50000|incoming,byte_3fa4=held)
    assert value['known_registers'][0]==int((incoming>=110)==(held>=110))
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x847DC,raw_r6=0xC7E50000|incoming,byte_3fa4=held)
    assert value['known_registers'][12]==matrix.context(contract.descriptor(repo.ROOT),case)[12]
    assert value['ram']==matrix.memory(case)


@pytest.mark.parametrize('field,raw',(('byte_4251',0),('byte_41d2',0),('byte_41d2',1),('byte_41d2',2)))
def test_all_three_required_flag_bits_keep_their_real_early_return(field,raw):
    value=evaluate(0x847DC,**{field:raw})
    assert value['known_registers'][0]==0 and value['calls']==[]


def test_local_byte_two_dwords_and_each_real_helper_frame_are_separately_retained():
    value=evaluate(0x847DC,raw_r5=0xB6D400D6,byte_413e=255)
    sites=(0x847F0,0x84836,0x84838,0x84844,0x84850,0x84852,0x84862)
    rows=[next(row for row in value['events'].values() if row['site']==site) for site in sites]
    assert [(row['mode'],row['width_bytes'],row['bytes']) for row in rows]==[
        ('write',1,'d6'),('read',1,'d6'),('write',4,'000000ff'),('read',4,'000000ff'),
        ('read',1,'d6'),('write',4,'000000ff'),('read',4,'000000ff')]
    assert [row['address']-0x02001000 for row in rows]==[-25,-25,-20,-20,-25,-24,-24]
    assert [call['sp'] for call in value['calls']]==[0x02001000-28]*2
    assert value['sp']==0x02001000 and value['pr']==0x02100000


@pytest.mark.parametrize('field,raw',(('byte_4251',True),('byte_413e',256),('word_11bc',65536),
    ('dword_9818',1<<32),('raw_r5',1<<32),('initial_sr',2)))
def test_complete_raw_bytes_words_registers_and_SR_refuse_narrowing_or_bool(field,raw):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x847DC);case[field]=raw
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
    rows=[row for row in withdrawal.descriptor(repo.ROOT)['reference'] if row['component']=='threshold_window_reader_withdrawal_paths']
    identity,address,alias=root
    if form=='alias':
        if alias is None:pytest.skip('the selected ROM root has no RAM alias')
        address=alias
    width=1
    if form=='overlapping-interval':address-=1;width=2
    with pytest.raises(ValueError):transfers.require_no_selected_datum(dict(accesses=[dict(site=0x8480C,
        address=address,width_bytes=width,domain=domain)]),rows)


@pytest.mark.parametrize('name',tuple(contract.REUSED_HELPER_FILES_SHA256))
def test_each_complete_previous_helper_source_is_exact(monkeypatch,name):
    read=__import__('pathlib').Path.read_bytes
    monkeypatch.setattr(__import__('pathlib').Path,'read_bytes',lambda path:read(path)+b'\n' if path==repo.ROOT/name else read(path))
    with pytest.raises(ValueError):contract.require_reused_helper_boundary(repo.ROOT)


def test_complete_fixture_retains_real_signed_helper_and_only_five_explicit_pointer_aliases():
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(declared,image);restored=bytearray(fixture)
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert len(aliases)==5 and bytes(restored)==image
    assert contract.SPANS==((0x21BBC,0x21CD6),(0x847DC,0x8489E))
    assert contract.HELPER_ENTRIES==(0x21BBC,) and contract.INPUT_BLOBS==[] and contract.CONFIGURATION==[]
    from kb.test_stock_capture import tool
    producer=tool(repo.ROOT,'threshold_window_reader_withdrawal_capture.py','_kb_threshold_window_producer_source_contract')
    assert declared['adapter']['marker']==producer.MARKER=='VQ_SH_ELF_THRESHOLD_WINDOW_READER_WITHDRAWAL'
    proof_adapter.require_generated(repo.ROOT,contract.DESCRIPTOR)


def test_published_threshold_window_joint_prior_and_registry_counts_bind_execution_sources():
    declared=withdrawal.descriptor(repo.ROOT);rows=[row for row in declared['reference'] if row['component']=='threshold_window_reader_withdrawal_paths']
    text=(repo.ROOT/'defs/JK08A.threshold-window-reader-withdrawal-paths.md').read_text();words=' '.join(text.split())
    assert len(rows)==3 and len(declared['reference'])==124 and len(declared['function'])==66
    assert len({row['owner'] for row in declared['reference']})==95
    assert [line for line in text.splitlines() if line.startswith('| `7mfk:')]==[
        '| `7mfk:'+f'{row["address"]:08x}'+'` | `7mfk:'+f'{row["function"]:08x}'+'` | `'+row['original_claim_sha256']+'` |' for row in rows]
    for phrase,actual,wanted in (('238 stock instructions',sum((last-first)//2 for first,last in contract.SPANS),238),
        ('476 code bytes',sum(last-first for first,last in contract.SPANS),476),('2 code spans',len(contract.SPANS),2),
        ('181 feasible instructions',len(transfers.FEASIBLE_SITES),181),('57 excluded helper instructions',len(transfers.INFEASIBLE_SITES),57),
        ('8 literal spans',len(contract.UNIT['pools']),8),('5 pointer aliases',len(contract.UNIT['aliases']),5),
        ('6 complete RAM fields',len(matrix.RAM_FIELDS),6),('8 complete calibration spans',len(contract.CONTROLLED_CALIBRATION),8),
        ('16 raw input fields',len(matrix.WIDTHS),16),('19 complete helper sources',len(contract.REUSED_HELPER_FILES_SHA256),19)):
        assert phrase in words and actual==wanted
    assert len(proof.REQUIRED_BRANCHES)==15 and '15 two-sided conditions' in words
    assert len(proof.FIXED_BRANCHES)==5 and '5 fixed conditions' in words
    owners={row['owner']:row for row in declared['reference']}
    datum_removed=sum(sum(len(marker.get('dependency',())) for marker in (json.loads(row['original_ledger_json']) or ()))-
        sum(len(marker.get('dependency',())) for marker in (json.loads(row['proposed_ledger_json']) or ())) for row in owners.values())
    function_removed=sum(sum(len(marker.get('dependency',())) for marker in json.loads(row['original_ledger_json']))-
        sum(len(marker.get('dependency',())) for marker in json.loads(row['proposed_ledger_json']))
        for row in declared['function'] if 'proposed_ledger_json' in row)
    assert datum_removed==109 and function_removed==7 and datum_removed+function_removed==116
    assert '116 matching ledger selectors' in words and '109 datum-end selectors and 7 function-end selectors' in words
    assert len(withdrawal.NATIVE_LINK_ROLES)==18 and len(withdrawal.ORIGINAL_LINK_TYPES)==10
    assert sum(json.loads(row['original_claim_json'])['type']=='reader' for row in declared['reference'])==114
    assert '114 readers and ten' in words
    from kb import scalar_ram_leaf_withdrawal_evidence as family
    assert len(family.COMPONENTS)==27 and 'Twenty-seven independent components' in words
    assert len({row['component'] for row in declared['reference'] if row['owner'].endswith('/ram')})==16
    for name in ('tools/kb/README.md','tools/kb/SPEC.md','tools/sh-elf-run/README.md','tools/kb/ordinary-access.md'):
        assert 'Fourteen native-RAM components' in ' '.join((repo.ROOT/name).read_text().split())
    assert withdrawal.digest(withdrawal.prior_reference_rows(declared,112))==withdrawal.PRIOR_PAIRED_INHIBIT_WRITER_REFERENCE_SHA256
    assert withdrawal.digest(declared['function'][:58])==withdrawal.PRIOR_PAIRED_INHIBIT_WRITER_FUNCTION_SHA256
    assert len(registry.FAMILIES)==13 and len(registry.captures())==47
    assert 'thirteen families and forty-seven capture bindings' in words
    assert proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)==25 and 'preceding twenty-five adapters' in words
    mappings=(withdrawal.PRIOR_FILES_SHA256,withdrawal.PRIOR_PRODUCT_FILES_SHA256,withdrawal.PRIOR_GATED_FILES_SHA256,withdrawal.PRIOR_RPM_RAM_FILES_SHA256,withdrawal.PRIOR_OVERFLOW_FILES_SHA256,withdrawal.PRIOR_WORD_FILES_SHA256,withdrawal.PRIOR_RPM_STATE_FILES_SHA256,withdrawal.PRIOR_INDEXED_WORD_FILES_SHA256,withdrawal.PRIOR_DIVISION_CALLER_FILES_SHA256,withdrawal.PRIOR_BYTE_CURVE_CALLER_FILES_SHA256,withdrawal.PRIOR_WORD_INTERP_CALLER_FILES_SHA256,withdrawal.PRIOR_SCALED_DIVISION_FILES_SHA256,withdrawal.PRIOR_CURVE_SCALE_CALLER_FILES_SHA256,withdrawal.PRIOR_DERIVATIVE_SCALE_CALLER_FILES_SHA256,withdrawal.PRIOR_GUARDED_QUOTIENT_CALLER_FILES_SHA256,withdrawal.PRIOR_MIXED_CURVE_CALLER_FILES_SHA256,withdrawal.PRIOR_TIMING_REMAINDER_CALLER_FILES_SHA256,withdrawal.PRIOR_STATE_RATIO_CALLER_FILES_SHA256,withdrawal.PRIOR_DFCO_STATE_CALLER_FILES_SHA256,withdrawal.PRIOR_PAIRED_INHIBIT_WRITER_FILES_SHA256,)
    files={name:sha for mapping in mappings for name,sha in mapping.items()}
    assert len(files)==180 and '180 prior domain sources' in words and '179 byte-identical sources' in words
    for name,sha in files.items():assert hashlib.sha256(withdrawal.prior_gated_source_bytes(repo.ROOT,name)).hexdigest()==sha
