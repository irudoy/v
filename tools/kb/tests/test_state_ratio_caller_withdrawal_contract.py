"""Complete state ratio, signed divisors, byte candidate carriers and exact prior source boundaries."""
import hashlib
import json
import pytest
from kb import repo,proof_adapter
from kb import ordinary_access_registry as registry
from kb import state_ratio_caller_withdrawal_contract as contract,state_ratio_caller_withdrawal_matrix as matrix
from kb import state_ratio_caller_withdrawal_semantics as scalar,state_ratio_caller_withdrawal_transfers as transfers
from kb import state_ratio_caller_withdrawal_capture_evidence as proof,scalar_ram_leaf_withdrawal_contract as withdrawal


def evaluate(entry,**changes):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=entry,**changes)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    return scalar.evaluate(entry,matrix.memory(case),matrix.calibrations(source,image,case),
        matrix.context(source,case),case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)


@pytest.mark.parametrize('divisor,bias,word',((0,0,0),(65535,0,65535),(65535,32767,0),(65535,65535,0),(1,0,65535)))
def test_signed_word_division_keeps_zero_bypass_negative_normalization_wrap_and_caps(divisor,bias,word):
    value=evaluate(0x64CB2,word_240e=divisor,config_8ea6=bias)
    assert value['ram'][0x1866:0x1868]==word.to_bytes(2,'big')
    assert value['ram'][0x9818:0x981C]==matrix.DEFAULTS['dword_9818'].to_bytes(4,'big')
    if divisor==0:assert value['calls']==[]
    else:
        call=next(row for row in value['calls'] if row['site']==0x64D54)
        assert call['target']==0x21BBC and call['registers'][0]==(divisor|0xFFFF0000 if divisor&32768 else divisor)
        if divisor==65535:assert {0x21BCC,0x21BCE}<=set(value['path'])


def test_zero_numerator_with_negative_divisor_retains_the_real_XOR_sign_flag():
    value=evaluate(0x64CB2,word_240e=65535,config_8ea6=65535)
    call=value['calls'][0]
    assert call['registers'][:2]==(0xFFFFFFFF,0) and call['quotient_sign_flag'] is True
    assert call['return_registers'][0]==0 and call['return_sr']&1==1


def test_signed_byte_endpoint_updates_counters_without_replacing_the_saved_candidate():
    value=evaluate(0xBDC66,byte_24a7=2,byte_106f=224,curve_second_7=255)
    assert value['lookups'][0]['raw_result']==0xFFFFFFFF
    assert (value['ram'][0x2326],value['ram'][0x1A1E],value['ram'][0x25EE])==(41,255,255)
    assert value['known_registers'][0]==41
    candidate=[row for row in value['events'].values() if row['site'] in (0xBDE40,0xBDEC6)]
    assert candidate[0]['address']==candidate[1]['address'] and candidate[0]['bytes']==candidate[1]['bytes']=='00000029'


def test_counter_hold_and_signed_final_offset_keep_distinct_local_candidate_paths():
    held=evaluate(0xBDC66,byte_24a7=2,byte_25ee=1)
    assert held['ram'][0x2326]==40 and not any(row['target']==0x26370 for row in held['calls'])
    lowered=evaluate(0xBDC66,byte_24a7=2,byte_1704=128,byte_41fa=1)
    assert lowered['ram'][0x2326]==0 and lowered['ram'][0x1A1E]!=matrix.DEFAULTS['byte_1a1e']


def test_transition_uses_unsigned_byte_endpoints_and_a_signed_real_difference():
    value=evaluate(0xBDC66,byte_1c5c=0,byte_1c5e=255,byte_1071=100)
    call=next(row for row in value['calls'] if row['site']==0xBDDCA)
    assert call['registers'][:2]==(180,(-20400)&0xFFFFFFFF)
    assert value['ram'][0x1BEE]==value['ram'][0x2326]==142
    reversed_value=evaluate(0xBDC66,config_8d2d=20,config_8d2e=200,byte_1071=100)
    assert reversed_value['ram'][0x2326]==matrix.DEFAULTS['byte_1c5e']
    assert reversed_value['calls']==[]


def test_special_mode_without_its_status_flag_retains_the_complete_RAM_preimage():
    value=evaluate(0xBDC66,config_8b34=16,config_8b42=2,byte_10e4=0)
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0xBDC66,config_8b34=16,config_8b42=2,byte_10e4=0)
    assert value['ram']==matrix.memory(case) and value['calls']==[]


@pytest.mark.parametrize('field,value',(('byte_246a',True),('config_8616',256),('word_240e',65536),
    ('curve_first_7',256),('dword_9818',1<<32),('raw_r6',1<<32),('initial_sr',2)))
def test_inputs_refuse_boolean_narrowing_width_or_SR_changes(field,value):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x64CB2);case[field]=value
    with pytest.raises(ValueError):matrix.require_case(case)


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_source_refuses_identity_geometry_scale_units_caller_hardware_stub_or_publication(tmp_path,flag):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    path.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('name',tuple(contract.REUSED_HELPER_FILES_SHA256))
def test_all_complete_prior_helpers_and_standard_implicit_byte_sources_remain_exact(monkeypatch,name):
    from pathlib import Path
    read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda path:read(path)+b'\n' if path==repo.ROOT/name else read(path))
    with pytest.raises(ValueError):contract.require_reused_helper_boundary(repo.ROOT)


@pytest.mark.parametrize('root',transfers.NATIVE_ROOTS)
@pytest.mark.parametrize('form',('native','alias','overlapping-interval'))
@pytest.mark.parametrize('domain',('ram','rom','frame'))
def test_selected_ROM_native_RAM_and_alias_roots_require_exact_physical_interval_absence(root,form,domain):
    rows=[row for row in withdrawal.descriptor(repo.ROOT)['reference'] if row['component']=='state_ratio_caller_withdrawal_paths']
    identity,address,alias=root
    if form=='alias':
        if alias is None:pytest.skip('the selected ROM root has no RAM alias')
        address=alias
    width=1
    if form=='overlapping-interval':address-=1;width=2
    with pytest.raises(ValueError):transfers.require_no_selected_datum(dict(accesses=[dict(site=0xBDE8C,
        address=address,width_bytes=width,domain=domain)]),rows)


def test_fixture_keeps_three_literal_holes_exact_byte_path_and_two_distinct_curves():
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(declared,image);restored=bytearray(fixture)
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert len(aliases)==30 and bytes(restored)==image
    for first,last in ((0x64DC4,0x64E00),(0x64ED4,0x64EE2),(0xBDCFA,0xBDD80)):
        assert fixture[first:last]==image[first:last]
        assert not any(max(first,start)<min(last,end) for start,end in contract.SPANS)
    assert (0x26A80,0x26A9C) in contract.SPANS and (0x26AAA,0x26ABA) in contract.SPANS
    assert not any(first<=0x26A60<last for first,last in contract.SPANS)
    assert contract.INPUT_BLOBS==[]
    assert [(row['address'],row['size']) for row in contract.CONFIGURATION if row['field'].startswith('curve_')]==[(at,1) for at in range(0x12EFE,0x12F0E)]
    from kb.test_stock_capture import tool
    producer=tool(repo.ROOT,'state_ratio_caller_withdrawal_capture.py','_kb_state_ratio_producer_source_contract')
    assert declared['adapter']['marker']==producer.MARKER=='VQ_SH_ELF_STATE_RATIO_CALLER_WITHDRAWAL'
    proof_adapter.require_generated(repo.ROOT,contract.DESCRIPTOR)


def test_published_state_ratio_joint_prior_and_registry_counts_bind_execution_sources():
    declared=withdrawal.descriptor(repo.ROOT);rows=[row for row in declared['reference'] if row['component']=='state_ratio_caller_withdrawal_paths']
    text=(repo.ROOT/'defs/JK08A.state-ratio-caller-withdrawal-paths.md').read_text();words=' '.join(text.split())
    assert len(rows)==8 and len(declared['reference'])==127 and len(declared['function'])==68
    assert len({row['owner'] for row in declared['reference']})==97
    assert [line for line in text.splitlines() if line.startswith('| `7mfk:')]==[
        '| `7mfk:'+f'{row["address"]:08x}'+'` | `7mfk:'+f'{row["function"]:08x}'+'` | `'+row['original_claim_sha256']+'` |' for row in rows]
    for phrase,actual,wanted in (('927 stock instructions',sum((last-first)//2 for first,last in contract.SPANS),927),
        ('1854 code bytes',sum(last-first for first,last in contract.SPANS),1854),('11 code spans',len(contract.SPANS),11),
        ('828 feasible instructions',len(transfers.FEASIBLE_SITES),828),('91 literal spans',len(contract.UNIT['pools']),91),
        ('30 pointer aliases',len(contract.UNIT['aliases']),30),('45 complete RAM fields',len(matrix.RAM_FIELDS),45),
        ('30 configuration fields',len(contract.CONFIGURATION),30),('107 complete calibration spans',len(contract.CONTROLLED_CALIBRATION),107),
        ('85 raw input fields',len(matrix.WIDTHS),85),('19 reused helper sources',len(contract.REUSED_HELPER_FILES_SHA256),19)):
        assert phrase in words and actual==wanted
    assert f'{len(proof.REQUIRED_BRANCHES)} two-sided conditions' in words and f'{len(proof.FIXED_BRANCHES)} fixed branch premises' in words
    owners={row['owner']:row for row in declared['reference']}
    removed=sum(sum(len(marker.get('dependency',())) for marker in (json.loads(row['original_ledger_json']) or ()))-
        sum(len(marker.get('dependency',())) for marker in (json.loads(row['proposed_ledger_json']) or ())) for row in owners.values())
    removed+=sum(sum(len(marker.get('dependency',())) for marker in json.loads(row['original_ledger_json']))-
        sum(len(marker.get('dependency',())) for marker in json.loads(row['proposed_ledger_json']))
        for row in declared['function'] if 'proposed_ledger_json' in row)
    assert removed==119 and '119 matching ledger selectors' in words
    assert len(withdrawal.NATIVE_LINK_ROLES)==19 and len(withdrawal.ORIGINAL_LINK_TYPES)==10
    assert sum(json.loads(row['original_claim_json'])['type']=='reader' for row in declared['reference'])==115
    assert '117 readers and ten' in words
    from kb import scalar_ram_leaf_withdrawal_evidence as family
    assert len(family.COMPONENTS)==27 and 'Twenty-seven independent components' in words
    assert len({row['component'] for row in declared['reference'] if row['owner'].endswith('/ram')})==16
    assert withdrawal.digest(withdrawal.prior_reference_rows(declared,92))==withdrawal.PRIOR_TIMING_REMAINDER_CALLER_REFERENCE_SHA256
    assert withdrawal.digest(declared['function'][:53])==withdrawal.PRIOR_TIMING_REMAINDER_CALLER_FUNCTION_SHA256
    assert len(registry.FAMILIES)==13 and len(registry.captures())==47
    assert 'thirteen families and forty-seven capture bindings' in words
    assert proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)==22 and 'preceding twenty-two adapters' in words
    mappings=(withdrawal.PRIOR_FILES_SHA256,withdrawal.PRIOR_PRODUCT_FILES_SHA256,withdrawal.PRIOR_GATED_FILES_SHA256,
        withdrawal.PRIOR_RPM_RAM_FILES_SHA256,withdrawal.PRIOR_OVERFLOW_FILES_SHA256,withdrawal.PRIOR_WORD_FILES_SHA256,
        withdrawal.PRIOR_RPM_STATE_FILES_SHA256,withdrawal.PRIOR_INDEXED_WORD_FILES_SHA256,
        withdrawal.PRIOR_DIVISION_CALLER_FILES_SHA256,withdrawal.PRIOR_BYTE_CURVE_CALLER_FILES_SHA256,
        withdrawal.PRIOR_WORD_INTERP_CALLER_FILES_SHA256,withdrawal.PRIOR_SCALED_DIVISION_FILES_SHA256,
        withdrawal.PRIOR_CURVE_SCALE_CALLER_FILES_SHA256,withdrawal.PRIOR_DERIVATIVE_SCALE_CALLER_FILES_SHA256,
        withdrawal.PRIOR_GUARDED_QUOTIENT_CALLER_FILES_SHA256,withdrawal.PRIOR_MIXED_CURVE_CALLER_FILES_SHA256,
        withdrawal.PRIOR_TIMING_REMAINDER_CALLER_FILES_SHA256)
    files={name:sha for mapping in mappings for name,sha in mapping.items()}
    assert len(files)==153 and '153 prior domain sources' in words and '152 byte-identical sources' in words
    for name,sha in files.items():assert hashlib.sha256(withdrawal.prior_gated_source_bytes(repo.ROOT,name)).hexdigest()==sha
