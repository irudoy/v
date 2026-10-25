"""Exact unsigned axis, authoritative word union and unchanged complete native boundaries."""
import hashlib
import json
import pytest
from kb import repo,proof_adapter
from kb import ordinary_access_registry as registry
from kb import word_interp_caller_withdrawal_contract as contract,word_interp_caller_withdrawal_matrix as matrix
from kb import word_interp_caller_withdrawal_semantics as scalar,word_interp_caller_withdrawal_transfers as transfers
from kb import word_interp_caller_withdrawal_capture_evidence as proof,scalar_ram_leaf_withdrawal_contract as withdrawal


def evaluate(entry,**changes):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=entry,**changes)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    return scalar.evaluate(entry,matrix.memory(case),matrix.calibrations(source,image,case),
        matrix.context(source,case),case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)


@pytest.mark.parametrize('knots,coordinate,index,fraction',(
    (tuple(range(0,160,10)),15,1,32768),
    ((0,0,*range(10,150,10)),15,2,32768),
    ((0,100,50,*range(200,1500,100)),75,2,10922),
    ((65535,)*16,0,0,0),((65535,)*32,65535,31,0)))
def test_backward_axis_uses_unsigned_rightmost_selection_without_monotonicity(knots,coordinate,index,fraction):
    value=scalar.position(knots,coordinate)
    assert (value['index'],value['fraction'])==(index,fraction)
    if value['bracket']:
        assert value['denominator']>0 and value['numerator']//value['denominator']==fraction


@pytest.mark.parametrize('first,second,fraction,wanted',((65535,0,1,65535),
    (0,65535,65535,65534),(65535,0,65535,1),(0x8000,0x7FFF,32768,0x8000)))
def test_CMP_HS_interpolation_retains_unsigned_values_and_positive_distance_floor(first,second,fraction,wanted):
    assert scalar.linear(first,second,fraction)['value']==wanted


def test_surface_zero_fraction_preserves_signed_word_return_until_caller_unsigned_multiply():
    value=evaluate(0xB7B98,raw_r4=0,raw_r6=0,surface_style=4,surface_seed=65535,raw_r7=17)
    top=value['calls'][0]
    assert top['return_registers'][0]==0xFFFFFFFF
    assert value['output']==65535*17 and value['ram'][0x2D04:0x2D08]==(65535*17).to_bytes(4,'big')
    assert value['registers'][0]==0x40C and value['macl']==matrix.context(None,dict(matrix.DEFAULTS,
        index=0,kind='controlled',entry=0xB7B98,raw_r4=0,raw_r6=0,surface_style=4,surface_seed=65535,raw_r7=17))[17]


def test_low_branch_clamp_is_fixed_and_high_logical_shift_has_both_clamp_outcomes():
    low=evaluate(0x72F1E,source_value=65535,curve_low_axis_style=5,curve_low_axis_seed=65535)
    assert 0x72F38 in low['path'] and 0x72F3A not in low['path']
    high=evaluate(0x72F1E,source_value=0x100000)
    edge=evaluate(0x72F1E,source_value=0xFFFFF)
    assert 0x72F5A in high['path'] and 0x72F5A not in edge['path']
    assert next(r for r in high['calls'] if r['site']==0x72F62)['registers'][6]==65535


def test_two_curve_views_have_one_authoritative_shared_neighbor_and_controlled_threshold():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x72F1E,
        curve_word_032=0xCAFE,curve_word_064=0xBEEF,curve_low_axis_style=5,curve_low_axis_seed=0x1234)
    fixture,_=contract.fixture_for_case(source,image,case)
    assert fixture[0x18F96+64:0x18F96+66]==fixture[0x18FD6:0x18FD8]==bytes.fromhex('cafe')
    assert fixture[0x18FD6+64:0x18FD6+66]==bytes.fromhex('beef')
    assert fixture[0x18EC4:0x18EC6]==fixture[0x18E86+62:0x18E86+64]==bytes.fromhex('1234')
    assert len(contract.CONFIGURATION)==len({r['address'] for r in contract.CONFIGURATION})==65
    assert [r for r in contract.INPUT_BLOBS if r['name']=='curve_words']==[dict(name='curve_words',address=0x18F96,size=130)]
    assert not any(r['address']<=0x18EC4<r['address']+r['size'] for r in contract.UNIT['pools'])
    assert matrix.CURVE_FIELDS[64] not in matrix.ENTRY_FIELDS[0x72F1E]


@pytest.mark.parametrize('field,value',(('source_value',1<<32),('previous_curve',-1),
    ('curve_word_032',True),('curve_word_064',65536),('raw_r4',1<<32),
    ('surface_style',7),('curve_low_axis_seed',65536),('initial_sr',2),('initial_sr',0x400)))
def test_input_refuses_width_boolean_style_or_SR_changes(field,value):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x72F1E);case[field]=value
    with pytest.raises(ValueError):matrix.require_case(case)


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_source_refuses_identity_geometry_scale_units_caller_hardware_stub_or_publication(tmp_path,flag):
    p=tmp_path/contract.DESCRIPTOR;p.parent.mkdir(parents=True)
    p.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('name',tuple(contract.REUSED_HELPER_FILES_SHA256))
def test_complete_existing_timing_helper_sources_are_byte_exact(monkeypatch,name):
    from pathlib import Path
    read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda p:read(p)+b'\n' if p==repo.ROOT/name else read(p))
    with pytest.raises(ValueError):contract.require_reused_helper_boundary(repo.ROOT)


@pytest.mark.parametrize('root',transfers.NATIVE_ROOTS)
@pytest.mark.parametrize('form',('native','alias','overlapping-interval'))
@pytest.mark.parametrize('domain',('ram','rom','frame'))
def test_selected_ROM_and_native_RAM_roots_require_physical_interval_absence(root,form,domain):
    rows=[r for r in withdrawal.descriptor(repo.ROOT)['reference'] if r['component']=='word_interp_caller_withdrawal_paths']
    identity,native,alias=root
    if form=='alias' and alias is None:pytest.skip('the selected ROM root has no RAM alias')
    at=alias if form=='alias' else native;width=1
    if form=='overlapping-interval':at-=1;width=2
    with pytest.raises(ValueError):transfers.require_no_selected_datum(dict(accesses=[dict(site=0x72F2C,
        address=at,width_bytes=width,domain=domain)]),rows)


def test_fixture_retains_all_natural_caller_and_nine_actual_helper_instruction_bytes():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image);restored=bytearray(fixture)
    for a,b in contract.SPANS:assert fixture[a:b]==image[a:b]
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert len(aliases)==2 and bytes(restored)==image
    assert set(contract.HELPER_ENTRIES)=={0x262A8,0x26714,0x26740,0x26848,0x26984,0x26AF8,0x26B84,0x26C78,0x26D10}
    from kb.test_stock_capture import tool
    producer=tool(repo.ROOT,'word_interp_caller_withdrawal_capture.py','_kb_word_interp_caller_producer_source_contract')
    assert source['adapter']['marker']==producer.MARKER=='VQ_SH_ELF_WORD_INTERP_CALLER_WITHDRAWAL'
    proof_adapter.require_generated(repo.ROOT,contract.DESCRIPTOR)


def test_published_word_caller_joint_prior_and_registry_counts_bind_execution_sources():
    declared=withdrawal.descriptor(repo.ROOT);rows=[r for r in declared['reference'] if r['component']=='word_interp_caller_withdrawal_paths']
    text=(repo.ROOT/'defs/JK08A.word-interp-caller-withdrawal-paths.md').read_text();words=' '.join(text.split())
    assert len(rows)==5 and len(declared['reference'])==124 and len(declared['function'])==66
    assert len({r['owner'] for r in declared['reference']})==95
    assert [line for line in text.splitlines() if line.startswith('| `7mfk:')]==[
        '| `7mfk:'+f'{r["address"]:08x}'+'` | `7mfk:'+f'{r["function"]:08x}'+'` | `'+r['original_claim_sha256']+'` |' for r in rows]
    for phrase,actual,wanted in (('419 stock instructions',sum((b-a)//2 for a,b in contract.SPANS),419),
        ('838 code bytes',sum(b-a for a,b in contract.SPANS),838),('11 code spans',len(contract.SPANS),11),
        ('414 feasible instructions',len(transfers.FEASIBLE_SITES),414),
        ('21 literal spans',len(contract.UNIT['pools']),21),('2 pointer aliases',len(contract.UNIT['aliases']),2),
        ('65 physical curve words',len(contract.CONFIGURATION),65),('27 complete calibration spans',len(contract.CONTROLLED_CALIBRATION),27),
        ('16 two-sided conditional sites',len(proof.REQUIRED_BRANCHES),16),('3 fixed premises',len(proof.FIXED_BRANCHES),3)):
        assert phrase in words and actual==wanted
    owners={r['owner']:r for r in declared['reference']}
    removed=sum(sum(len(m.get('dependency',())) for m in (json.loads(r['original_ledger_json']) or ()))-
        sum(len(m.get('dependency',())) for m in (json.loads(r['proposed_ledger_json']) or ())) for r in owners.values())
    removed+=sum(sum(len(marker.get('dependency',())) for marker in json.loads(row['original_ledger_json']))-
        sum(len(marker.get('dependency',())) for marker in json.loads(row['proposed_ledger_json']))
        for row in declared['function'] if 'proposed_ledger_json' in row)
    assert removed==116 and '116 matching ledger selectors' in words
    assert len(withdrawal.NATIVE_LINK_ROLES)==18
    assert withdrawal.ORIGINAL_LINK_TYPES=={'00052034-ffff120e-withdraw':'writer',
        '0006e3d8-ffff1300-withdraw':'writer','0006e3d8-ffff1f86-withdraw':'writer'}
    assert all(json.loads(r['original_claim_json'])['type']=='reader' for r in rows)
    assert withdrawal.digest(withdrawal.prior_reference_rows(declared,49))==withdrawal.PRIOR_BYTE_CURVE_CALLER_REFERENCE_SHA256
    assert withdrawal.digest(declared['function'][:36])==withdrawal.PRIOR_BYTE_CURVE_CALLER_FUNCTION_SHA256
    assert len(registry.FAMILIES)==13 and len(registry.captures())==47
    assert 'thirteen families and forty-seven capture bindings' in words
    assert proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)==15 and 'preceding fifteen adapters' in words
    files={k:v for mapping in (withdrawal.PRIOR_FILES_SHA256,withdrawal.PRIOR_PRODUCT_FILES_SHA256,
        withdrawal.PRIOR_GATED_FILES_SHA256,withdrawal.PRIOR_RPM_RAM_FILES_SHA256,
        withdrawal.PRIOR_OVERFLOW_FILES_SHA256,withdrawal.PRIOR_WORD_FILES_SHA256,
        withdrawal.PRIOR_RPM_STATE_FILES_SHA256,withdrawal.PRIOR_INDEXED_WORD_FILES_SHA256,
        withdrawal.PRIOR_DIVISION_CALLER_FILES_SHA256,withdrawal.PRIOR_BYTE_CURVE_CALLER_FILES_SHA256) for k,v in mapping.items()}
    assert len(files)==90 and '90 prior domain sources' in words and '89 byte-identical sources' in words
    for name,sha in files.items():assert hashlib.sha256(withdrawal.prior_gated_source_bytes(repo.ROOT,name)).hexdigest()==sha
