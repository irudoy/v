"""Complete raw counter-rate caller,ordered clamps and real auxiliary gate and exact prior source boundaries."""
import hashlib
import json
import pytest
from kb import repo,proof_adapter
from kb import ordinary_access_registry as registry
from kb import aux_rate_caller_withdrawal_contract as contract,aux_rate_caller_withdrawal_matrix as matrix
from kb import aux_rate_caller_withdrawal_semantics as scalar,aux_rate_caller_withdrawal_transfers as transfers
from kb import aux_rate_caller_withdrawal_capture_evidence as proof,scalar_ram_leaf_withdrawal_contract as withdrawal


def evaluate(entry,**changes):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=entry,**changes)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    return scalar.evaluate(entry,matrix.memory(case),matrix.calibrations(source,image,case),
        matrix.context(source,case),case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)


@pytest.mark.parametrize('counter,measured,previous',((0,1000,200),(1,1000,200),(100,1000,200),
    (65535,65535,200),(65535,65535,32768),(100,0,0),(100,124,0),(100,125,0),(100,249,32767),
    (100,250,32768),(100,65535,65535)))
def test_full_unsigned_word_product_and_sign_extended_counter_keep_ordered_upper_then_lower_clamps(counter,measured,previous):
    value=evaluate(0x68D58,word_235c=counter,word_201a=measured,word_2018=previous)
    signed=previous-65536 if previous&32768 else previous
    expected=0 if counter==0 else max(125,min(signed+counter*measured//4000,measured-125))
    assert int.from_bytes(value['ram'][0x201E:0x2020],'big')==expected
    dividers=[row for row in value['calls'] if row['target']==0x21CE0]
    assert len(dividers)==int(counter!=0)
    if dividers:
        assert dividers[0]['divisor']==4000 and dividers[0]['dividend']==counter*measured
        assert dividers[0]['return_registers'][0]==counter*measured//4000
        assert dividers[0]['long_path']==(counter*measured>=4000*256)


def test_negative_saved_word_keeps_both_full_local_dwords_and_the_actual_reload():
    value=evaluate(0x68D58,word_2018=32768,word_201a=250)
    rows=[next(row for row in value['events'].values() if row['site']==site) for site in (0x68D90,0x68D92,0x68DA6)]
    assert [(row['mode'],row['width_bytes'],row['bytes']) for row in rows]==[
        ('write',4,'ffff8000'),('write',4,'ffff8000'),('read',4,'ffff8000')]
    assert [row['address']-0x02001000 for row in rows]==[-16,-20,-20]


@pytest.mark.parametrize('initialized,gate,blocked',((0,0,0),(0,1,0),(0,1,64),(1,0,0),(1,1,0)))
def test_real_initialization_call_delay_publication_and_post_gate_clear_remain_distinct(initialized,gate,blocked):
    value=evaluate(0x68D58,byte_4251=initialized,word_34e4=20 if gate else 0,byte_4184=blocked)
    first=125 if initialized else 225;cleared=bool(gate and not blocked and not initialized)
    rows=[row for row in value['events'].values() if row['address']==0x0100201E and row['mode']=='write']
    assert [(row['site'],int(row['bytes'],16)) for row in rows]==[(0x68DCA,first)]+([(0x68DDA,0)] if cleared else [])
    assert int.from_bytes(value['ram'][0x201E:0x2020],'big')==(0 if cleared else first)
    assert int.from_bytes(value['ram'][0x235C:0x235E],'big')==(400 if initialized else 100)
    assert int.from_bytes(value['ram'][0x2018:0x201A],'big')==(0 if initialized else 200)
    assert value['sp']==0x02001000 and value['pr']==0x02100000


@pytest.mark.parametrize('first,second,returned,register',((0,0,0,0),(19,19,0,19),(20,0,1,20),
    (32768,0,1,0xFFFF8000),(65535,0,1,0xFFFFFFFF),(0,20,1,20),(0,32768,1,32768),(0,65535,1,65535)))
def test_real_auxiliary_gate_retains_distinct_promoted_word_values(first,second,returned,register):
    value=evaluate(0x68D58,word_34e4=first,word_34e6=second)
    gate=next(row for row in value['calls'] if row['target']==0x8C3FA)
    assert gate['return_registers'][0]==returned and gate['return_registers'][2]==register


@pytest.mark.parametrize('field,raw',(('byte_24c0',True),('byte_41a5',256),('word_2018',65536),
    ('dword_9818',1<<32),('raw_r6',1<<32),('initial_sr',2)))
def test_complete_raw_byte_word_dword_register_and_SR_inputs_refuse_narrowing(field,raw):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x68D58);case[field]=raw
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
    rows=[row for row in withdrawal.descriptor(repo.ROOT)['reference'] if row['component']=='aux_rate_caller_withdrawal_paths']
    identity,address,alias=root
    if form=='alias':
        if alias is None:pytest.skip('the selected ROM root has no RAM alias')
        address=alias
    width=1
    if form=='overlapping-interval':address-=1;width=2
    with pytest.raises(ValueError):transfers.require_no_selected_datum(dict(accesses=[dict(site=0x68DCA,
        address=address,width_bytes=width,domain=domain)]),rows)


@pytest.mark.parametrize('name',tuple(contract.REUSED_HELPER_FILES_SHA256))
def test_each_complete_previous_helper_source_is_exact(monkeypatch,name):
    read=__import__('pathlib').Path.read_bytes
    monkeypatch.setattr(__import__('pathlib').Path,'read_bytes',lambda path:read(path)+b'\n' if path==repo.ROOT/name else read(path))
    with pytest.raises(ValueError):contract.require_reused_helper_boundary(repo.ROOT)


def test_complete_fixture_retains_full_unsigned_divider_and_real_auxiliary_gate():
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(declared,image);restored=bytearray(fixture)
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert len(aliases)==8 and bytes(restored)==image
    assert contract.SPANS==((0x21CE0,0x21DC6),(0x68D58,0x68DE8),(0x8C3FA,0x8C446))
    assert contract.HELPER_ENTRIES==(0x21CE0,0x8C3FA) and contract.INPUT_BLOBS==[] and contract.CONFIGURATION==[]
    from kb.test_stock_capture import tool
    producer=tool(repo.ROOT,'aux_rate_caller_withdrawal_capture.py','_kb_auxiliary_rate_producer_source_contract')
    assert declared['adapter']['marker']==producer.MARKER=='VQ_SH_ELF_AUX_RATE_CALLER_WITHDRAWAL'
    proof_adapter.require_generated(repo.ROOT,contract.DESCRIPTOR)


def test_published_auxiliary_rate_joint_prior_and_registry_counts_bind_execution_sources():
    declared=withdrawal.descriptor(repo.ROOT);rows=[row for row in declared['reference'] if row['component']=='aux_rate_caller_withdrawal_paths']
    text=(repo.ROOT/'defs/JK08A.aux-rate-caller-withdrawal-paths.md').read_text();words=' '.join(text.split())
    assert len(rows)==1 and len(declared['reference'])==129 and len(declared['function'])==70
    assert len({row['owner'] for row in declared['reference']})==98
    assert [line for line in text.splitlines() if line.startswith('| `7mfk:')]==[
        '| `7mfk:'+f'{row["address"]:08x}'+'` | `7mfk:'+f'{row["function"]:08x}'+'` | `'+row['original_claim_sha256']+'` |' for row in rows]
    for phrase,actual,wanted in (('225 stock instructions',sum((last-first)//2 for first,last in contract.SPANS),225),
        ('450 code bytes',sum(last-first for first,last in contract.SPANS),450),('3 code spans',len(contract.SPANS),3),
        ('179 feasible instructions',len(transfers.FEASIBLE_SITES),179),('46 excluded helper instructions',len(transfers.INFEASIBLE_SITES),46),
        ('14 literal spans',len(contract.UNIT['pools']),14),('8 pointer aliases',len(contract.UNIT['aliases']),8),
        ('13 complete RAM fields',len(matrix.RAM_FIELDS),13),('14 complete calibration spans',len(contract.CONTROLLED_CALIBRATION),14),
        ('23 raw input fields',len(matrix.WIDTHS),23),('7 complete helper sources',len(contract.REUSED_HELPER_FILES_SHA256),7)):
        assert phrase in words and actual==wanted
    assert len(proof.REQUIRED_BRANCHES)==14 and '14 two-sided conditions' in words
    assert len(proof.FIXED_BRANCHES)==2 and '2 fixed conditions' in words
    owners={row['owner']:row for row in declared['reference']}
    datum_removed=sum(sum(len(marker.get('dependency',())) for marker in (json.loads(row['original_ledger_json']) or ()))-
        sum(len(marker.get('dependency',())) for marker in (json.loads(row['proposed_ledger_json']) or ())) for row in owners.values())
    function_removed=sum(sum(len(marker.get('dependency',())) for marker in json.loads(row['original_ledger_json']))-
        sum(len(marker.get('dependency',())) for marker in json.loads(row['proposed_ledger_json']))
        for row in declared['function'] if 'proposed_ledger_json' in row)
    assert datum_removed==113 and function_removed==8 and datum_removed+function_removed==121
    assert '121 matching ledger selectors' in words and '113 datum-end selectors and 8 function-end selectors' in words
    assert len(withdrawal.NATIVE_LINK_ROLES)==19 and len(withdrawal.ORIGINAL_LINK_TYPES)==10
    assert sum(json.loads(row['original_claim_json'])['type']=='reader' for row in declared['reference'])==119
    assert '119 readers and ten' in words
    from kb import scalar_ram_leaf_withdrawal_evidence as family
    assert len(family.COMPONENTS)==29 and 'Twenty-nine independent components' in words
    assert len({row['component'] for row in declared['reference'] if row['owner'].endswith('/ram')})==16
    for name in ('tools/kb/README.md','tools/kb/SPEC.md','tools/sh-elf-run/README.md','tools/kb/ordinary-access.md'):
        assert 'Fourteen native-RAM components' in ' '.join((repo.ROOT/name).read_text().split())
    assert withdrawal.digest(withdrawal.prior_reference_rows(declared,115))==withdrawal.PRIOR_THRESHOLD_WINDOW_READER_REFERENCE_SHA256
    assert withdrawal.digest(declared['function'][:59])==withdrawal.PRIOR_THRESHOLD_WINDOW_READER_FUNCTION_SHA256
    assert len(registry.FAMILIES)==13 and len(registry.captures())==47
    assert 'thirteen families and forty-seven capture bindings' in words
    assert proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)==26 and 'preceding twenty-six adapters' in words
    mappings=(withdrawal.PRIOR_FILES_SHA256,withdrawal.PRIOR_PRODUCT_FILES_SHA256,withdrawal.PRIOR_GATED_FILES_SHA256,withdrawal.PRIOR_RPM_RAM_FILES_SHA256,withdrawal.PRIOR_OVERFLOW_FILES_SHA256,withdrawal.PRIOR_WORD_FILES_SHA256,withdrawal.PRIOR_RPM_STATE_FILES_SHA256,withdrawal.PRIOR_INDEXED_WORD_FILES_SHA256,withdrawal.PRIOR_DIVISION_CALLER_FILES_SHA256,withdrawal.PRIOR_BYTE_CURVE_CALLER_FILES_SHA256,withdrawal.PRIOR_WORD_INTERP_CALLER_FILES_SHA256,withdrawal.PRIOR_SCALED_DIVISION_FILES_SHA256,withdrawal.PRIOR_CURVE_SCALE_CALLER_FILES_SHA256,withdrawal.PRIOR_DERIVATIVE_SCALE_CALLER_FILES_SHA256,withdrawal.PRIOR_GUARDED_QUOTIENT_CALLER_FILES_SHA256,withdrawal.PRIOR_MIXED_CURVE_CALLER_FILES_SHA256,withdrawal.PRIOR_TIMING_REMAINDER_CALLER_FILES_SHA256,withdrawal.PRIOR_STATE_RATIO_CALLER_FILES_SHA256,withdrawal.PRIOR_DFCO_STATE_CALLER_FILES_SHA256,withdrawal.PRIOR_PAIRED_INHIBIT_WRITER_FILES_SHA256,withdrawal.PRIOR_THRESHOLD_WINDOW_READER_FILES_SHA256,)
    files={name:sha for mapping in mappings for name,sha in mapping.items()}
    assert len(files)==189 and '189 prior domain sources' in words and '188 byte-identical sources' in words
    for name,sha in files.items():assert hashlib.sha256(withdrawal.prior_gated_source_bytes(repo.ROOT,name)).hexdigest()==sha
