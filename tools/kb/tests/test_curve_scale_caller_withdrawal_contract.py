"""Exact raw dividend/curve separation, negative constant and complete native boundaries."""
import hashlib
import json
import pytest
from kb import repo,proof_adapter
from kb import ordinary_access_registry as registry
from kb import curve_scale_caller_withdrawal_contract as contract,curve_scale_caller_withdrawal_matrix as matrix
from kb import curve_scale_caller_withdrawal_semantics as scalar,curve_scale_caller_withdrawal_transfers as transfers
from kb import curve_scale_caller_withdrawal_capture_evidence as proof,scalar_ram_leaf_withdrawal_contract as withdrawal


def evaluate(**changes):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0xB7768,**changes)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    return scalar.evaluate(0xB7768,matrix.memory(case),matrix.calibrations(source,image,case),
        matrix.context(source,case),case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)


@pytest.mark.parametrize('dividend,bias,candidate,output',((0,0,0,2500),
    (10000,0,1,2500),(0xFFFFD8F0,0,-1,2499),(0,0xABCD0001,-100,2450),
    (0x7FFFFFFF,0,214748,16383),(0x80000000,0,-214748,0),
    ((-60000000)&0xFFFFFFFF,0,-6000,0)))
def test_raw_signed_quotient_byte_bias_saturation_and_each_product_shift(dividend,bias,candidate,output):
    value=evaluate(raw_r5=dividend,raw_r6=bias,gain=128,**{name:256 for name in matrix.CURVE_FIELDS})
    assert value['candidate']==candidate and value['output']==output
    assert value['ram'][0x2D08:0x2D0C]==output.to_bytes(4,'big')
    call=next(row for row in value['calls'] if row['site']==0xB7788)
    assert call['registers'][:2]==(10000,dividend)


def test_curve_changes_publication_without_replacing_the_original_signed_argument():
    first=evaluate(raw_r5=50000000,raw_r6=0,gain=128,**{name:256 for name in matrix.CURVE_FIELDS})
    second=evaluate(raw_r5=50000000,raw_r6=0,gain=128,**{name:512 for name in matrix.CURVE_FIELDS})
    assert (first['curve_value'],second['curve_value'])==(256,512)
    assert first['signed_quotient']==second['signed_quotient']==5000
    assert (first['output'],second['output'])==(5000,10000)
    assert first['ram'][0x9818:0x981C]==second['ram'][0x9818:0x981C]==matrix.DEFAULTS['previous_fault'].to_bytes(4,'big')


def test_real_axis_uses32_unsigned_words_and_positive_distance_interpolation():
    value=scalar.position(tuple(i*1000 for i in range(32)),1500)
    assert (value['index'],value['fraction'])==(1,32768)
    assert scalar.linear(1000,2000,value['fraction'])['value']==1500
    assert scalar.linear(65535,0,1)['value']==65535


@pytest.mark.parametrize('field,value',(('curve_word_00',True),('curve_word_32',65536),
    ('gain',256),('raw_r5',1<<32),('axis_style',7),('axis_seed',65536),('initial_sr',2)))
def test_input_refuses_boolean_narrowing_axis_style_or_SR_changes(field,value):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0xB7768);case[field]=value
    with pytest.raises(ValueError):matrix.require_case(case)


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_source_refuses_identity_geometry_scale_units_caller_hardware_stub_or_publication(tmp_path,flag):
    p=tmp_path/contract.DESCRIPTOR;p.parent.mkdir(parents=True)
    p.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('name',tuple(contract.REUSED_HELPER_FILES_SHA256))
def test_complete_uptight_duck_and_division_sources_are_byte_exact(monkeypatch,name):
    from pathlib import Path
    read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda p:read(p)+b'\n' if p==repo.ROOT/name else read(p))
    with pytest.raises(ValueError):contract.require_reused_helper_boundary(repo.ROOT)


@pytest.mark.parametrize('root',transfers.NATIVE_ROOTS)
@pytest.mark.parametrize('form',('native','alias','overlapping-interval'))
@pytest.mark.parametrize('domain',('ram','rom','frame'))
def test_selected_ROM_native_RAM_and_alias_intervals_require_physical_absence(root,form,domain):
    rows=[r for r in withdrawal.descriptor(repo.ROOT)['reference'] if r['component']=='curve_scale_caller_withdrawal_paths' and r['function'] in contract.ENTRIES]
    identity,native,alias=root
    if form=='alias' and alias is None:pytest.skip('the selected ROM root has no RAM alias')
    at=alias if form=='alias' else native;width=1
    if form=='overlapping-interval':at-=1;width=2
    with pytest.raises(ValueError):transfers.require_no_selected_datum(dict(accesses=[dict(site=0xB77C6,
        address=at,width_bytes=width,domain=domain)]),rows)


def test_fixture_retains_all_real_helpers_and_only_two_exact_RAM_aliases():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image);restored=bytearray(fixture)
    for a,b in contract.SPANS:assert fixture[a:b]==image[a:b]
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert {row['address'] for row in aliases}=={0x21CD8,0xB7978} and bytes(restored)==image
    assert fixture[0xB7970:0xB7974]==image[0xB7970:0xB7974]==bytes.fromhex('ffff6c78')
    assert set(contract.HELPER_ENTRIES)=={0x21BBC,0x26524,0x26740,0x26984,0x26C78}
    from kb.test_stock_capture import tool
    producer=tool(repo.ROOT,'curve_scale_caller_withdrawal_capture.py','_kb_curve_scale_caller_producer_source_contract')
    assert source['adapter']['marker']==producer.MARKER=='VQ_SH_ELF_CURVE_SCALE_CALLER_WITHDRAWAL'
    proof_adapter.require_generated(repo.ROOT,contract.DESCRIPTOR)


def test_published_curve_scale_joint_prior_and_registry_counts_bind_execution_sources():
    declared=withdrawal.descriptor(repo.ROOT);rows=[r for r in declared['reference'] if r['component']=='curve_scale_caller_withdrawal_paths']
    text=(repo.ROOT/'defs/JK08A.curve-scale-caller-withdrawal-paths.md').read_text();words=' '.join(text.split())
    assert len(rows)==4 and len(declared['reference'])==129 and len(declared['function'])==70
    assert len({r['owner'] for r in declared['reference']})==98
    assert [line for line in text.splitlines() if line.startswith('| `7mfk:')]==[
        '| `7mfk:'+f'{r["address"]:08x}'+'` | `7mfk:'+f'{r["function"]:08x}'+'` | `'+r['original_claim_sha256']+'` |' for r in rows]
    for phrase,actual,wanted in (('351 stock instructions',sum((b-a)//2 for a,b in contract.SPANS),351),
        ('702 code bytes',sum(b-a for a,b in contract.SPANS),702),('6 code spans',len(contract.SPANS),6),
        ('296 feasible instructions',len(transfers.FEASIBLE_SITES),296),
        ('18 literal spans',len(contract.UNIT['pools']),18),('2 pointer aliases',len(contract.UNIT['aliases']),2),
        ('33 physical curve words',len(matrix.CURVE_FIELDS),33),('20 complete calibration spans',len(contract.CONTROLLED_CALIBRATION),20),
        ('12 two-sided conditions',len(proof.REQUIRED_BRANCHES),12),('4 fixed divisor premises',len(proof.FIXED_BRANCHES),4)):
        assert phrase in words and actual==wanted
    assert next(row['size'] for row in contract.INPUT_BLOBS if row['name']=='axis_words')==64
    owners={r['owner']:r for r in declared['reference']}
    removed=sum(sum(len(m.get('dependency',())) for m in (json.loads(r['original_ledger_json']) or ()))-
        sum(len(m.get('dependency',())) for m in (json.loads(r['proposed_ledger_json']) or ())) for r in owners.values())
    removed+=sum(sum(len(marker.get('dependency',())) for marker in json.loads(row['original_ledger_json']))-
        sum(len(marker.get('dependency',())) for marker in json.loads(row['proposed_ledger_json']))
        for row in declared['function'] if 'proposed_ledger_json' in row)
    assert removed==121 and '121 matching ledger selectors' in words
    assert len(withdrawal.NATIVE_LINK_ROLES)==19 and len(withdrawal.ORIGINAL_LINK_TYPES)==10
    assert all(withdrawal.native_type(r,'width') is None and withdrawal.native_type(r,'signed') is None for r in rows)
    assert withdrawal.digest(withdrawal.prior_reference_rows(declared,57))==withdrawal.PRIOR_SCALED_DIVISION_REFERENCE_SHA256
    assert withdrawal.digest(declared['function'][:41])==withdrawal.PRIOR_SCALED_DIVISION_FUNCTION_SHA256
    assert len(registry.FAMILIES)==13 and len(registry.captures())==47
    assert 'thirteen families and forty-seven capture bindings' in words
    assert proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)==17 and 'preceding seventeen adapters' in words
    files={k:v for mapping in (withdrawal.PRIOR_FILES_SHA256,withdrawal.PRIOR_PRODUCT_FILES_SHA256,
        withdrawal.PRIOR_GATED_FILES_SHA256,withdrawal.PRIOR_RPM_RAM_FILES_SHA256,
        withdrawal.PRIOR_OVERFLOW_FILES_SHA256,withdrawal.PRIOR_WORD_FILES_SHA256,
        withdrawal.PRIOR_RPM_STATE_FILES_SHA256,withdrawal.PRIOR_INDEXED_WORD_FILES_SHA256,
        withdrawal.PRIOR_DIVISION_CALLER_FILES_SHA256,withdrawal.PRIOR_BYTE_CURVE_CALLER_FILES_SHA256,
        withdrawal.PRIOR_WORD_INTERP_CALLER_FILES_SHA256,withdrawal.PRIOR_SCALED_DIVISION_FILES_SHA256) for k,v in mapping.items()}
    assert len(files)==108 and '108 prior domain sources' in words and '107 byte-identical sources' in words
    for name,sha in files.items():assert hashlib.sha256(withdrawal.prior_gated_source_bytes(repo.ROOT,name)).hexdigest()==sha
