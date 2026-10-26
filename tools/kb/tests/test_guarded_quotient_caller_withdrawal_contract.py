"""Exact guarded state arithmetic, signed quotient carriers and complete source boundaries."""
import hashlib
import json
import pytest
from kb import repo,proof_adapter
from kb import ordinary_access_registry as registry
from kb import guarded_quotient_caller_withdrawal_contract as contract,guarded_quotient_caller_withdrawal_matrix as matrix
from kb import guarded_quotient_caller_withdrawal_semantics as scalar,guarded_quotient_caller_withdrawal_transfers as transfers
from kb import guarded_quotient_caller_withdrawal_capture_evidence as proof,scalar_ram_leaf_withdrawal_contract as withdrawal


def evaluate(entry,**changes):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=entry,**changes)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    return scalar.evaluate(entry,matrix.memory(case),matrix.calibrations(source,image,case),
        matrix.context(source,case),case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)


@pytest.mark.parametrize('changes,output',(({},64),
    (dict(word_18f2=65535,word_19a2=1,word_23fc=1,word_944e=1),65472),
    (dict(word_18f2=32767,word_19a2=1,word_23fc=1,word_944e=65535),32767),
    (dict(word_18f2=32768,word_19a2=1,word_23fc=1,word_944e=65535),32768)))
def test_two_stage_signed_scaler_preserves_raw_sign_wide_caps_and_final_word(changes,output):
    value=evaluate(0x75306,**changes)
    assert value['output']==output and value['ram'][0x19D4:0x19D6]==output.to_bytes(2,'big')
    assert [row['site'] for row in value['calls']]==[0x75330,0x7536C]
    assert value['path'][-2:]==(0x75392,0x75394)


@pytest.mark.parametrize('field',('word_19a2','word_23fc'))
def test_scaler_zero_gates_bypass_both_real_calls_without_fault_publication(field):
    value=evaluate(0x75306,**{field:0})
    assert value['output']==0 and value['calls']==[]
    assert value['ram'][0x9818:0x981C]==matrix.DEFAULTS['previous_fault'].to_bytes(4,'big')


@pytest.mark.parametrize('changes,output',(({},32767),(dict(byte_24d2=0),75),
    (dict(byte_24d2=0,word_17f8=200),0),(dict(word_1210=0),125),
    (dict(word_1210=65535),65535),(dict(word_1210=65534,word_914e=0,word_9150=65535),65533)))
def test_window_keeps_unsigned_thresholds_and_real_signed32_fraction_wrap(changes,output):
    value=evaluate(0x74B68,**changes)
    assert value['output']==output and value['ram'][0x2422:0x2424]==output.to_bytes(2,'big')
    if changes.get('word_1210')==65534:
        assert value['known_registers'][0]==0xFFFFFFFD
        assert value['calls'][0]['registers'][:2]==(65535,(65534*65535)&0xFFFFFFFF)


@pytest.mark.parametrize('field,flag',(('byte_417e',8),('byte_249b',1),('byte_245f',128)))
def test_each_window_gate_has_its_own_zero_publication(field,flag):
    value=evaluate(0x74B68,**{field:flag})
    assert value['output']==0 and value['calls']==[]


@pytest.mark.parametrize('changes,output',(({},6),
    (dict(byte_161a=0,word_1426=1000,word_15ce=50000,word_15fe=0),3051),
    (dict(byte_161a=0,word_1426=65535,word_15ce=65535,word_15fe=32767),327675)))
def test_guarded_main_path_keeps_multiply_before_or_after_extract_and_saved_sum(changes,output):
    value=evaluate(0x532AE,**changes)
    assert value['output']==value['known_registers'][0]==output
    call=next(row for row in value['calls'] if row['site']==0x5335A)
    assert call['registers'][1]==0x7FFFFFFF
    saved=[row for row in value['events'].values() if row['site'] in (0x5335C,0x5335E)]
    assert len(saved)==2 and saved[0]['bytes']==saved[1]['bytes']


def test_guarded_zero_divisor_keeps_the_real_fault_word_and_complete_argument():
    value=evaluate(0x532AE,byte_161a=0,word_1426=0)
    call=next(row for row in value['calls'] if row['site']==0x5335A)
    assert call['registers'][:2]==(0,0x7FFFFFFF) and value['output']==0
    assert value['ram'][0x9818:0x981C]==bytes.fromhex('0000044e')


def test_existing_state_bit_bypasses_fallback_without_donating_unwritten_preimages():
    value=evaluate(0x532AE,byte_2485=16)
    assert value['output']==0 and value['calls']==[]
    assert value['ram'][0x1600]==matrix.DEFAULTS['byte_1600'] and value['ram'][0x2485]==16


@pytest.mark.parametrize('field,value',(('byte_1660',True),('byte_230e',256),('word_1426',65536),
    ('word_914e',65536),('word_944e',65536),('previous_fault',1<<32),('raw_r6',1<<32),('initial_sr',2)))
def test_inputs_refuse_boolean_narrowing_width_or_SR_changes(field,value):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x532AE);case[field]=value
    with pytest.raises(ValueError):matrix.require_case(case)


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_source_refuses_identity_geometry_scale_units_caller_hardware_stub_or_publication(tmp_path,flag):
    p=tmp_path/contract.DESCRIPTOR;p.parent.mkdir(parents=True)
    p.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('name',tuple(contract.REUSED_HELPER_FILES_SHA256))
def test_every_full_direct_division_source_remains_byte_exact(monkeypatch,name):
    from pathlib import Path
    read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda p:read(p)+b'\n' if p==repo.ROOT/name else read(p))
    with pytest.raises(ValueError):contract.require_reused_helper_boundary(repo.ROOT)


@pytest.mark.parametrize('root',transfers.NATIVE_ROOTS)
@pytest.mark.parametrize('form',('native','alias','overlapping-interval'))
@pytest.mark.parametrize('domain',('ram','rom','frame'))
def test_every_selected_ROM_native_RAM_and_alias_requires_physical_interval_absence(root,form,domain):
    rows=[r for r in withdrawal.descriptor(repo.ROOT)['reference'] if r['component']=='guarded_quotient_caller_withdrawal_paths']
    identity,native,alias=root
    if form=='alias' and alias is None:pytest.skip('the selected ROM root has no RAM alias')
    at=alias if form=='alias' else native;width=1
    if form=='overlapping-interval':at-=1;width=2
    with pytest.raises(ValueError):transfers.require_no_selected_datum(dict(accesses=[dict(site=0x5348E,
        address=at,width_bytes=width,domain=domain)]),rows)


def test_fixture_keeps_literal_holes_full_real_signed_helper_and_fourteen_exact_pointer_aliases():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image);restored=bytearray(fixture)
    for a,b in contract.SPANS:assert fixture[a:b]==image[a:b]
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert len(aliases)==14 and bytes(restored)==image and set(contract.HELPER_ENTRIES)=={0x21BBC}
    for first,last in ((0x533BA,0x533FC),(0x75344,0x7534E)):
        assert fixture[first:last]==image[first:last]
        assert not any(max(first,a)<min(last,b) for a,b in contract.SPANS)
    from kb.test_stock_capture import tool
    producer=tool(repo.ROOT,'guarded_quotient_caller_withdrawal_capture.py','_kb_guarded_quotient_producer_source_contract')
    assert source['adapter']['marker']==producer.MARKER=='VQ_SH_ELF_GUARDED_QUOTIENT_CALLER_WITHDRAWAL'
    proof_adapter.require_generated(repo.ROOT,contract.DESCRIPTOR)


def test_published_guarded_joint_prior_and_registry_counts_bind_execution_sources():
    declared=withdrawal.descriptor(repo.ROOT);rows=[r for r in declared['reference'] if r['component']=='guarded_quotient_caller_withdrawal_paths']
    text=(repo.ROOT/'defs/JK08A.guarded-quotient-caller-withdrawal-paths.md').read_text();words=' '.join(text.split())
    assert len(rows)==8 and len(declared['reference'])==134 and len(declared['function'])==74
    assert len({r['owner'] for r in declared['reference']})==100
    assert [line for line in text.splitlines() if line.startswith('| `7mfk:')]==[
        '| `7mfk:'+f'{r["address"]:08x}'+'` | `7mfk:'+f'{r["function"]:08x}'+'` | `'+r['original_claim_sha256']+'` |' for r in rows]
    for phrase,actual,wanted in (('511 stock instructions',sum((b-a)//2 for a,b in contract.SPANS),511),
        ('1022 code bytes',sum(b-a for a,b in contract.SPANS),1022),('6 code spans',len(contract.SPANS),6),
        ('505 feasible instructions',len(transfers.FEASIBLE_SITES),505),
        ('46 literal spans',len(contract.UNIT['pools']),46),('14 pointer aliases',len(contract.UNIT['aliases']),14),
        ('26 complete RAM fields',len(matrix.RAM_FIELDS),26),('4 scalar configuration words',len(contract.CONFIGURATION),4),
        ('46 complete calibration spans',len(contract.CONTROLLED_CALIBRATION),46),('40 raw input fields',len(matrix.WIDTHS),40),
        ('7 reused helper sources',len(contract.REUSED_HELPER_FILES_SHA256),7),('40 two-sided conditions',len(proof.REQUIRED_BRANCHES),40),
        ('3 fixed branch premises',len(proof.FIXED_BRANCHES),3)):
        assert phrase in words and actual==wanted
    owners={r['owner']:r for r in declared['reference']}
    removed=sum(sum(len(m.get('dependency',())) for m in (json.loads(r['original_ledger_json']) or ()))-
        sum(len(m.get('dependency',())) for m in (json.loads(r['proposed_ledger_json']) or ())) for r in owners.values())
    removed+=sum(sum(len(marker.get('dependency',())) for marker in json.loads(row['original_ledger_json']))-
        sum(len(marker.get('dependency',())) for marker in json.loads(row['proposed_ledger_json']))
        for row in declared['function'] if 'proposed_ledger_json' in row)
    assert removed==126 and '126 matching ledger selectors' in words
    assert len(withdrawal.NATIVE_LINK_ROLES)==19 and len(withdrawal.ORIGINAL_LINK_TYPES)==11
    assert withdrawal.digest(withdrawal.prior_reference_rows(declared,71))==withdrawal.PRIOR_DERIVATIVE_SCALE_CALLER_REFERENCE_SHA256
    assert withdrawal.digest(declared['function'][:44])==withdrawal.PRIOR_DERIVATIVE_SCALE_CALLER_FUNCTION_SHA256
    assert len(registry.FAMILIES)==13 and len(registry.captures())==47
    assert 'thirteen families and forty-seven capture bindings' in words
    assert proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)==19 and 'preceding nineteen adapters' in words
    files={k:v for mapping in (withdrawal.PRIOR_FILES_SHA256,withdrawal.PRIOR_PRODUCT_FILES_SHA256,
        withdrawal.PRIOR_GATED_FILES_SHA256,withdrawal.PRIOR_RPM_RAM_FILES_SHA256,
        withdrawal.PRIOR_OVERFLOW_FILES_SHA256,withdrawal.PRIOR_WORD_FILES_SHA256,
        withdrawal.PRIOR_RPM_STATE_FILES_SHA256,withdrawal.PRIOR_INDEXED_WORD_FILES_SHA256,
        withdrawal.PRIOR_DIVISION_CALLER_FILES_SHA256,withdrawal.PRIOR_BYTE_CURVE_CALLER_FILES_SHA256,
        withdrawal.PRIOR_WORD_INTERP_CALLER_FILES_SHA256,withdrawal.PRIOR_SCALED_DIVISION_FILES_SHA256,
        withdrawal.PRIOR_CURVE_SCALE_CALLER_FILES_SHA256,withdrawal.PRIOR_DERIVATIVE_SCALE_CALLER_FILES_SHA256) for k,v in mapping.items()}
    assert len(files)==126 and '126 prior domain sources' in words and '125 byte-identical sources' in words
    for name,sha in files.items():assert hashlib.sha256(withdrawal.prior_gated_source_bytes(repo.ROOT,name)).hexdigest()==sha
