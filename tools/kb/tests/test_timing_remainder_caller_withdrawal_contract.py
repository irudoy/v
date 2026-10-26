"""Complete timing history, raw quotient/remainder carriers and exact prior source boundaries."""
import hashlib
import json
import pytest
from kb import repo,proof_adapter
from kb import ordinary_access_registry as registry
from kb import timing_remainder_caller_withdrawal_contract as contract,timing_remainder_caller_withdrawal_matrix as matrix
from kb import timing_remainder_caller_withdrawal_semantics as scalar,timing_remainder_caller_withdrawal_transfers as transfers
from kb import timing_remainder_caller_withdrawal_capture_evidence as proof,scalar_ram_leaf_withdrawal_contract as withdrawal


def evaluate(entry,**changes):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=entry,**changes)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    return scalar.evaluate(entry,matrix.memory(case),matrix.calibrations(source,image,case),
        matrix.context(source,case),case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)


@pytest.mark.parametrize('word,angle,lead,full_return',((0,1,0,0),(60,1,1,1),(59,29,0,0),(65535,7,68,1092)))
def test_zero_maxima_keep_two_actual120_calls_and_separate_full_quotient_and_clamped_remainder(word,angle,lead,full_return):
    value=evaluate(0x521A8,word_241c=0,word_192e=word,**{field:0 for field in matrix.MAXIMUM_FIELDS})
    assert value['output']==(angle,lead) and value['known_registers'][0]==full_return
    assert value['ram'][0x23BF]==angle and value['ram'][0x23F0]==lead
    calls=[row for row in value['calls'] if row['site'] in (0x52246,0x52250)]
    assert [(row['target'],row['registers'][:2]) for row in calls]==[(0x21BBC,(120,word*2)),(0x21E14,(120,word*2))]
    assert value['ram'][0x9818:0x981C]==matrix.DEFAULTS['previous_fault'].to_bytes(4,'big')


def test_offset_floor_keeps_zero_numerator_calls_without_a_divisor_fault():
    value=evaluate(0x521A8,word_241c=0,word_192e=59,byte_24c9=32,remainder_offset=119,
        **{field:0 for field in matrix.MAXIMUM_FIELDS})
    assert value['output']==(1,0) and [row['registers'][:2] for row in value['calls']]==[(120,0),(120,0)]
    assert value['ram'][0x9818:0x981C]==matrix.DEFAULTS['previous_fault'].to_bytes(4,'big')
    saved=[row for row in value['events'].values() if row['site'] in (0x5222A,0x52240,0x5224C)]
    assert [row['bytes'] for row in saved]==['00000076','00000000','00000000']


def test_lead_override_changes_only_the_saved_quotient_and_its_real_publication():
    value=evaluate(0x521A8,word_241c=0,word_192e=65535,byte_4251=1,
        **{field:0 for field in matrix.MAXIMUM_FIELDS})
    assert value['output']==(7,3) and value['known_registers'][0]==3
    writes=[row for row in value['events'].values() if row['site'] in (0x5224E,0x52280)]
    assert writes[0]['bytes']=='00000444' and writes[1]['bytes']=='00000003'


@pytest.mark.parametrize('history,byte,output',((0,0,0),(127,0,127),(128,0,127),
    (0x7FFFFFFF,1,128),(0x80000000,255,127)))
def test_full_raw_history_sum_wraps_before_signed_byte_clamping(history,byte,output):
    value=evaluate(0x4D99C,history_word=history,byte_25fc=1,byte_2356=byte,
        **{field:0 for field in matrix.CURVE_FIELDS})
    assert value['output']==output and value['ram'][0x12D6]==output
    assert value['known_registers'][0]==0x4A
    assert value['ram'][0x1FF8:0x1FFC]==history.to_bytes(4,'big')
    assert value['ram'][0x2000:0x2002]==bytes(2) and value['ram'][0x1FF6:0x1FF8]==bytes(2)


@pytest.mark.parametrize('history,word',((0,1),(0x7FFFFFFF,0xFFFFFFFE),(0x80000000,1)))
def test_history_compare_uses_raw_signed32_but_step_uses_the_real_signed_low_word(history,word):
    value=evaluate(0x4D99C,history_word=history,byte_25fc=0,byte_229d=30)
    assert value['ram'][0x1FF8:0x1FFC]==word.to_bytes(4,'big')
    assert value['ram'][0x25FC]==matrix.DEFAULTS['counter_reload']


@pytest.mark.parametrize('byte',(0,127,128,255))
def test_curve_bypass_keeps_signed_MOV_B_and_the_unwritten_word2000_preimage(byte):
    value=evaluate(0x4D99C,byte_24cc=2,byte_2378=byte)
    assert value['output']==byte and value['ram'][0x12D6]==byte and value['calls']==[]
    assert value['ram'][0x2000:0x2002]==matrix.DEFAULTS['word_2000'].to_bytes(2,'big')
    assert any(row['site']==0x4DB7E and row['kind']=='taken' for row in value['controls'])
    assert 0x4DB82 not in value['path']


@pytest.mark.parametrize('field,value',(('byte_24c5',True),('counter_reload',256),('word_192e',65536),
    ('curve_word_08',65536),('history_word',1<<32),('previous_fault',1<<32),('raw_r6',1<<32),('initial_sr',2)))
def test_inputs_refuse_boolean_narrowing_width_or_SR_changes(field,value):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x4D99C);case[field]=value
    with pytest.raises(ValueError):matrix.require_case(case)


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_source_refuses_identity_geometry_scale_units_caller_hardware_stub_or_publication(tmp_path,flag):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    path.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('name',tuple(contract.REUSED_HELPER_FILES_SHA256))
def test_all_complete_prior_helpers_and_standard_remainder_sources_remain_exact(monkeypatch,name):
    from pathlib import Path
    read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda path:read(path)+b'\n' if path==repo.ROOT/name else read(path))
    with pytest.raises(ValueError):contract.require_reused_helper_boundary(repo.ROOT)


@pytest.mark.parametrize('root',transfers.NATIVE_ROOTS)
@pytest.mark.parametrize('form',('native','alias','overlapping-interval'))
@pytest.mark.parametrize('domain',('ram','rom','frame'))
def test_selected_ROM_native_RAM_and_alias_roots_require_exact_physical_interval_absence(root,form,domain):
    rows=[row for row in withdrawal.descriptor(repo.ROOT)['reference'] if row['component']=='timing_remainder_caller_withdrawal_paths']
    identity,address,alias=root
    if form=='alias':
        if alias is None:pytest.skip('the selected ROM root has no RAM alias')
        address=alias
    width=1
    if form=='overlapping-interval':address-=1;width=2
    with pytest.raises(ValueError):transfers.require_no_selected_datum(dict(accesses=[dict(site=0x4DA90,
        address=address,width_bytes=width,domain=domain)]),rows)


def test_fixture_keeps_one_literal_hole_full_real_remainder_and_exact_eight_knot_geometry():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image);restored=bytearray(fixture)
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert len(aliases)==20 and bytes(restored)==image and len(contract.HELPER_ENTRIES)==7
    assert (0x21E14,0x21F38) in contract.SPANS
    assert fixture[0x4DAA4:0x4DAA8]==image[0x4DAA4:0x4DAA8]
    assert not any(max(0x4DAA4,first)<min(0x4DAA8,last) for first,last in contract.SPANS)
    assert contract.INPUT_BLOBS==[dict(name='curve_words',address=0x147DA,size=18),dict(name='axis_words',address=0x13C48,size=16)]
    assert 'mov #0xe,r4' in (repo.ROOT/contract.UNIT['assembly']).read_text()
    from kb.test_stock_capture import tool
    producer=tool(repo.ROOT,'timing_remainder_caller_withdrawal_capture.py','_kb_timing_remainder_producer_source_contract')
    assert source['adapter']['marker']==producer.MARKER=='VQ_SH_ELF_TIMING_REMAINDER_CALLER_WITHDRAWAL'
    proof_adapter.require_generated(repo.ROOT,contract.DESCRIPTOR)


def test_published_timing_remainder_joint_prior_and_registry_counts_bind_execution_sources():
    declared=withdrawal.descriptor(repo.ROOT);rows=[row for row in declared['reference'] if row['component']=='timing_remainder_caller_withdrawal_paths']
    text=(repo.ROOT/'defs/JK08A.timing-remainder-caller-withdrawal-paths.md').read_text();words=' '.join(text.split())
    assert len(rows)==5 and len(declared['reference'])==134 and len(declared['function'])==74
    assert len({row['owner'] for row in declared['reference']})==100
    assert [line for line in text.splitlines() if line.startswith('| `7mfk:')]==[
        '| `7mfk:'+f'{row["address"]:08x}'+'` | `7mfk:'+f'{row["function"]:08x}'+'` | `'+row['original_claim_sha256']+'` |' for row in rows]
    for phrase,actual,wanted in (('918 stock instructions',sum((last-first)//2 for first,last in contract.SPANS),918),
        ('1836 code bytes',sum(last-first for first,last in contract.SPANS),1836),('10 code spans',len(contract.SPANS),10),
        ('753 feasible instructions',len(transfers.FEASIBLE_SITES),753),('48 literal spans',len(contract.UNIT['pools']),48),
        ('20 pointer aliases',len(contract.UNIT['aliases']),20),('39 complete RAM fields',len(matrix.RAM_FIELDS),39),
        ('14 scalar configuration fields',len(contract.CONFIGURATION),14),('50 complete calibration spans',len(contract.CONTROLLED_CALIBRATION),50),
        ('65 raw input fields',len(matrix.WIDTHS),65),('33 reused helper sources',len(contract.REUSED_HELPER_FILES_SHA256),33),
        ('47 two-sided conditions',len(proof.REQUIRED_BRANCHES),47),('15 fixed branch premises',len(proof.FIXED_BRANCHES),15)):
        assert phrase in words and actual==wanted
    owners={row['owner']:row for row in declared['reference']}
    removed=sum(sum(len(marker.get('dependency',())) for marker in (json.loads(row['original_ledger_json']) or ()))-
        sum(len(marker.get('dependency',())) for marker in (json.loads(row['proposed_ledger_json']) or ())) for row in owners.values())
    removed+=sum(sum(len(marker.get('dependency',())) for marker in json.loads(row['original_ledger_json']))-
        sum(len(marker.get('dependency',())) for marker in json.loads(row['proposed_ledger_json']))
        for row in declared['function'] if 'proposed_ledger_json' in row)
    assert removed==126 and '126 matching ledger selectors' in words
    assert len(withdrawal.NATIVE_LINK_ROLES)==19 and len(withdrawal.ORIGINAL_LINK_TYPES)==11
    assert sum(json.loads(row['original_claim_json'])['type']=='reader' for row in declared['reference'])==123
    assert '123 readers and eleven' in words
    from kb import scalar_ram_leaf_withdrawal_evidence as family
    assert len(family.COMPONENTS)==33 and 'Thirty-three independent components' in words
    native_components={row['component'] for row in declared['reference'] if row['owner'].endswith('/ram')}
    assert len(native_components)==14
    for name in ('tools/kb/README.md','tools/kb/SPEC.md','tools/sh-elf-run/README.md','tools/kb/ordinary-access.md'):
        assert 'Fourteen native-RAM components' in ' '.join((repo.ROOT/name).read_text().split())
    assert withdrawal.digest(withdrawal.prior_reference_rows(declared,87))==withdrawal.PRIOR_MIXED_CURVE_CALLER_REFERENCE_SHA256
    assert withdrawal.digest(declared['function'][:51])==withdrawal.PRIOR_MIXED_CURVE_CALLER_FUNCTION_SHA256
    assert len(registry.FAMILIES)==13 and len(registry.captures())==47
    assert 'thirteen families and forty-seven capture bindings' in words
    assert proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)==21 and 'preceding twenty-one adapters' in words
    files={name:sha for mapping in (withdrawal.PRIOR_FILES_SHA256,withdrawal.PRIOR_PRODUCT_FILES_SHA256,
        withdrawal.PRIOR_GATED_FILES_SHA256,withdrawal.PRIOR_RPM_RAM_FILES_SHA256,
        withdrawal.PRIOR_OVERFLOW_FILES_SHA256,withdrawal.PRIOR_WORD_FILES_SHA256,
        withdrawal.PRIOR_RPM_STATE_FILES_SHA256,withdrawal.PRIOR_INDEXED_WORD_FILES_SHA256,
        withdrawal.PRIOR_DIVISION_CALLER_FILES_SHA256,withdrawal.PRIOR_BYTE_CURVE_CALLER_FILES_SHA256,
        withdrawal.PRIOR_WORD_INTERP_CALLER_FILES_SHA256,withdrawal.PRIOR_SCALED_DIVISION_FILES_SHA256,
        withdrawal.PRIOR_CURVE_SCALE_CALLER_FILES_SHA256,withdrawal.PRIOR_DERIVATIVE_SCALE_CALLER_FILES_SHA256,
        withdrawal.PRIOR_GUARDED_QUOTIENT_CALLER_FILES_SHA256,withdrawal.PRIOR_MIXED_CURVE_CALLER_FILES_SHA256) for name,sha in mapping.items()}
    assert len(files)==144 and '144 prior domain sources' in words and '143 byte-identical sources' in words
    for name,sha in files.items():assert hashlib.sha256(withdrawal.prior_gated_source_bytes(repo.ROOT,name)).hexdigest()==sha
