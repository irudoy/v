"""Complete paired byte curves,normalization and signed word publications and exact prior source boundaries."""
import hashlib
import json
import pytest
from kb import repo,proof_adapter
from kb import ordinary_access_registry as registry
from kb import paired_curve_normalization_withdrawal_contract as contract,paired_curve_normalization_withdrawal_matrix as matrix
from kb import paired_curve_normalization_withdrawal_semantics as scalar,paired_curve_normalization_withdrawal_transfers as transfers
from kb import paired_curve_normalization_withdrawal_capture_evidence as proof,scalar_ram_leaf_withdrawal_contract as withdrawal


def evaluate(entry,**changes):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=entry,**changes)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    return scalar.evaluate(entry,matrix.memory(case),matrix.calibrations(source,image,case),
        matrix.context(source,case),case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)


@pytest.mark.parametrize('entry,at,returned',((0x655B4,0x18D4,0x648),(0x65B08,0x18CE,0x642)))
@pytest.mark.parametrize('first,second,word',((0,0,1000),(0,255,1000),(255,0,32767),
    (255,0,32768),(128,128,65535),(255,255,1),(1,254,32768),(254,1,65535),(0,0,0)))
def test_two_exact_byte_coefficients_keep_variable_positive_divisor_signed_product_and_both_word_caps(entry,at,returned,first,second,word):
    changes=dict(matrix.curve_profile(0),curve_value_0=first,curve_value_15=second,word_18cc=word)
    value=evaluate(entry,**changes);signed=word-65536 if word&32768 else word
    numerator=signed*(256-second);divisor=256-first
    quotient=abs(numerator)//divisor*(-1 if numerator<0 else 1)
    expected=max(-32768,min(32767,quotient))&65535
    assert value['ram'][at:at+2]==expected.to_bytes(2,'big') and value['known_registers'][0]==returned
    curves=[row for row in value['lookups'] if row['kind']=='byte-curve']
    assert [(row['coordinate'],row['value']) for row in curves]==[(0,first),(255,second)]
    divider=next(row for row in value['calls'] if row['target']==0x21BBC)
    assert divider['divisor']==divisor and divider['dividend']==numerator&0xFFFFFFFF
    assert divider['long_path']==(abs(numerator)>=divisor*256)
    assert not divider['zero'] and not divider['large_divisor']


@pytest.mark.parametrize('word',(0,1,32767,32768,65535))
def test_equal_signed_word_alternate_path_copies_the_other_word_without_any_helper(word):
    value=evaluate(0x655B4,config_8710=32,word_11a0=100,word_119e=100,word_18ce=word)
    assert value['ram'][0x18D4:0x18D6]==word.to_bytes(2,'big') and value['calls']==[]
    assert value['known_registers'][0]==0x648 and value['sp']==0x02001000 and value['pr']==0x02100000


@pytest.mark.parametrize('entry,at',((0x655B4,0x18D4),(0x65B08,0x18CE)))
@pytest.mark.parametrize('coefficient,word',((0,32767),(0,32768),(128,65535),(255,32767),(255,32768),(255,65535)))
def test_alternate_word_product_rounds_signed_division_by256_toward_zero(entry,at,coefficient,word):
    changes=dict(config_8710=32,word_119e=101,word_11a0=100,word_18cc=word,
        **{name:coefficient for name in matrix.VALUE_FIELDS})
    value=evaluate(entry,**changes);signed=word-65536 if word&32768 else word
    numerator=signed*(256-coefficient);expected=(abs(numerator)//256*(-1 if numerator<0 else 1))&65535
    assert value['ram'][at:at+2]==expected.to_bytes(2,'big')
    assert not any(row['target']==0x21BBC for row in value['calls'])
    assert len([row for row in value['lookups'] if row['kind']=='byte-curve'])==1


@pytest.mark.parametrize('first,subtract,coordinate',((127,128,255),(128,127,0),(255,0,0),(0,255,1),(127,0,127)))
def test_second_alternate_coordinate_keeps_both_signed_byte_promotions_before_EXTU_B(first,subtract,coordinate):
    value=evaluate(0x65B08,config_8710=32,byte_23f1=first,byte_11a2=subtract)
    curve=next(row for row in value['lookups'] if row['kind']=='byte-curve')
    assert curve['coordinate']==coordinate


@pytest.mark.parametrize('entry',contract.ENTRIES)
def test_physical_seventeenth_data_byte_is_bound_but_cannot_claim_numerical_influence_at_zero_fraction(entry):
    changes=matrix.curve_profile(0)
    first=evaluate(entry,**dict(changes,curve_value_16=0));second=evaluate(entry,**dict(changes,curve_value_16=255))
    assert first['ram']==second['ram'] and first['known_registers'][0]==second['known_registers'][0]
    reads=[row for row in second['events'].values() if row['site']==0x264B2 and row['address']==0x11D34]
    assert len(reads)==1 and reads[0]['bytes']=='ff' and reads[0]['width_bytes']==1
    assert 'curve_value_16' in matrix.WIDTHS and 'curve_value_16' not in matrix.ENTRY_FIELDS[entry]


@pytest.mark.parametrize('knots,coordinate,index,fraction',(
    ((240,*([0]*14),100),50,14,32768),((240,*([0]*14),100),240,15,0),
    ((240,*([0]*14),100),0,14,0),((*([255]*16),),0,0,0),
    ((*([0]*15),255),254,14,254*65536//255)))
def test_rightmost_axis_selection_admits_complete_unordered_raw_bytes_and_only_actual_positive_brackets(knots,coordinate,index,fraction):
    position=scalar.position(knots,coordinate)
    assert (position['index'],position['fraction'])==(index,fraction)
    if position['bracket']:assert position['denominator']>0 and 0<position['numerator']<position['denominator']*65536


@pytest.mark.parametrize('field,raw',(('byte_11c1',True),('byte_23f1',256),('word_18cc',65536),
    ('curve_axis_15',256),('curve_value_16',256),('dword_9818',1<<32),('raw_r6',1<<32),('initial_sr',2)))
def test_raw_byte_word_dword_register_axis_lookahead_and_SR_inputs_refuse_narrowing(field,raw):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x655B4);case[field]=raw
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
    rows=[row for row in withdrawal.descriptor(repo.ROOT)['reference'] if row['component']=='paired_curve_normalization_withdrawal_paths']
    identity,address,alias=root
    if form=='alias':
        if alias is None:pytest.skip('the selected ROM root has no RAM alias')
        address=alias
    width=1
    if form=='overlapping-interval':address-=1;width=2
    with pytest.raises(ValueError):transfers.require_no_selected_datum(dict(accesses=[dict(site=0x656F2,
        address=address,width_bytes=width,domain=domain)]),rows)


@pytest.mark.parametrize('name',tuple(contract.REUSED_HELPER_FILES_SHA256))
def test_each_complete_previous_helper_source_is_exact(monkeypatch,name):
    read=__import__('pathlib').Path.read_bytes
    monkeypatch.setattr(__import__('pathlib').Path,'read_bytes',lambda path:read(path)+b'\n' if path==repo.ROOT/name else read(path))
    with pytest.raises(ValueError):contract.require_reused_helper_boundary(repo.ROOT)


def test_complete_fixture_retains_both_full_callers_and_all_five_real_helpers_with_only_exact_aliases():
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(declared,image);restored=bytearray(fixture)
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert len(aliases)==8 and bytes(restored)==image
    assert contract.HELPER_ENTRIES==(0x21BBC,0x264A0,0x26740,0x26944,0x26C78)
    assert [(row['name'],row['address'],row['size']) for row in contract.INPUT_BLOBS]==[
        ('curve_axis_bytes',0x1199E,16),('curve_value_bytes',0x11D24,17)]
    from kb.test_stock_capture import tool
    producer=tool(repo.ROOT,'paired_curve_normalization_withdrawal_capture.py','_kb_paired_normalization_producer_source_contract')
    assert declared['adapter']['marker']==producer.MARKER=='VQ_SH_ELF_PAIRED_CURVE_NORMALIZATION_WITHDRAWAL'
    proof_adapter.require_generated(repo.ROOT,contract.DESCRIPTOR)


def test_published_paired_curve_joint_prior_and_registry_counts_bind_execution_sources():
    declared=withdrawal.descriptor(repo.ROOT);rows=[row for row in declared['reference'] if row['component']=='paired_curve_normalization_withdrawal_paths']
    text=(repo.ROOT/'defs/JK08A.paired-curve-normalization-withdrawal-paths.md').read_text();words=' '.join(text.split())
    assert len(rows)==2 and len(declared['reference'])==132 and len(declared['function'])==73
    assert len({row['owner'] for row in declared['reference']})==100
    assert [line for line in text.splitlines() if line.startswith('| `7mfk:')]==[
        '| `7mfk:'+f'{row["address"]:08x}'+'` | `7mfk:'+f'{row["function"]:08x}'+'` | `'+row['original_claim_sha256']+'` |' for row in rows]
    for phrase,actual,wanted in (('596 stock instructions',sum((last-first)//2 for first,last in contract.SPANS),596),
        ('1192 code bytes',sum(last-first for first,last in contract.SPANS),1192),('7 code spans',len(contract.SPANS),7),
        ('538 feasible instructions',len(transfers.FEASIBLE_SITES),538),('58 excluded instructions',len(transfers.INFEASIBLE_SITES),58),
        ('32 literal spans',len(contract.UNIT['pools']),32),('8 pointer aliases',len(contract.UNIT['aliases']),8),
        ('15 complete RAM fields',len(matrix.RAM_FIELDS),15),('34 scalar configuration fields',len(contract.CONFIGURATION),34),
        ('34 complete calibration spans',len(contract.CONTROLLED_CALIBRATION),34),('59 raw input fields',len(matrix.WIDTHS),59),
        ('26 complete helper sources',len(contract.REUSED_HELPER_FILES_SHA256),26)):
        assert phrase in words and actual==wanted
    assert len(proof.REQUIRED_BRANCHES)==28 and '28 two-sided conditions' in words
    assert len(proof.FIXED_BRANCHES)==7 and '7 fixed conditions' in words
    owners={row['owner']:row for row in declared['reference']}
    datum_removed=sum(sum(len(marker.get('dependency',())) for marker in (json.loads(row['original_ledger_json']) or ()))-
        sum(len(marker.get('dependency',())) for marker in (json.loads(row['proposed_ledger_json']) or ())) for row in owners.values())
    function_removed=sum(sum(len(marker.get('dependency',())) for marker in json.loads(row['original_ledger_json']))-
        sum(len(marker.get('dependency',())) for marker in json.loads(row['proposed_ledger_json']))
        for row in declared['function'] if 'proposed_ledger_json' in row)
    assert datum_removed==116 and function_removed==8 and datum_removed+function_removed==124
    assert '124 matching ledger selectors' in words and '116 datum-end selectors and 8 function-end selectors' in words
    assert len(withdrawal.NATIVE_LINK_ROLES)==19 and len(withdrawal.ORIGINAL_LINK_TYPES)==11
    assert sum(json.loads(row['original_claim_json'])['type']=='reader' for row in declared['reference'])==121
    assert '121 readers and eleven' in words
    from kb import scalar_ram_leaf_withdrawal_evidence as family
    assert len(family.COMPONENTS)==32 and 'Thirty-two independent components' in words
    assert len({row['component'] for row in declared['reference'] if row['owner'].endswith('/ram')})==16
    for name in ('tools/kb/README.md','tools/kb/SPEC.md','tools/sh-elf-run/README.md','tools/kb/ordinary-access.md'):
        assert 'Fourteen native-RAM components' in ' '.join((repo.ROOT/name).read_text().split())
    assert withdrawal.paired_curve_prefix_digest(declared,116)==withdrawal.PRIOR_AUX_RATE_CALLER_REFERENCE_SHA256
    assert withdrawal.digest(declared['function'][:60])==withdrawal.PRIOR_AUX_RATE_CALLER_FUNCTION_SHA256
    assert len(registry.FAMILIES)==13 and len(registry.captures())==47
    assert 'thirteen families and forty-seven capture bindings' in words
    assert proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)==27 and 'preceding twenty-seven adapters' in words
    mappings=(withdrawal.PRIOR_FILES_SHA256,withdrawal.PRIOR_PRODUCT_FILES_SHA256,withdrawal.PRIOR_GATED_FILES_SHA256,withdrawal.PRIOR_RPM_RAM_FILES_SHA256,withdrawal.PRIOR_OVERFLOW_FILES_SHA256,withdrawal.PRIOR_WORD_FILES_SHA256,withdrawal.PRIOR_RPM_STATE_FILES_SHA256,withdrawal.PRIOR_INDEXED_WORD_FILES_SHA256,withdrawal.PRIOR_DIVISION_CALLER_FILES_SHA256,withdrawal.PRIOR_BYTE_CURVE_CALLER_FILES_SHA256,withdrawal.PRIOR_WORD_INTERP_CALLER_FILES_SHA256,withdrawal.PRIOR_SCALED_DIVISION_FILES_SHA256,withdrawal.PRIOR_CURVE_SCALE_CALLER_FILES_SHA256,withdrawal.PRIOR_DERIVATIVE_SCALE_CALLER_FILES_SHA256,withdrawal.PRIOR_GUARDED_QUOTIENT_CALLER_FILES_SHA256,withdrawal.PRIOR_MIXED_CURVE_CALLER_FILES_SHA256,withdrawal.PRIOR_TIMING_REMAINDER_CALLER_FILES_SHA256,withdrawal.PRIOR_STATE_RATIO_CALLER_FILES_SHA256,withdrawal.PRIOR_DFCO_STATE_CALLER_FILES_SHA256,withdrawal.PRIOR_PAIRED_INHIBIT_WRITER_FILES_SHA256,withdrawal.PRIOR_THRESHOLD_WINDOW_READER_FILES_SHA256,withdrawal.PRIOR_AUX_RATE_CALLER_FILES_SHA256,)
    files={name:sha for mapping in mappings for name,sha in mapping.items()}
    assert len(files)==198 and '198 prior domain sources' in words and '197 byte-identical sources' in words
    for name,sha in files.items():assert hashlib.sha256(withdrawal.prior_gated_source_bytes(repo.ROOT,name)).hexdigest()==sha
