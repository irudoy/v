"""Exact product wrap, signed shift, reciprocal fault, blend and native source boundaries."""
import hashlib
import json
import pytest
from kb import repo,proof_adapter
from kb import ordinary_access_registry as registry
from kb import scaled_division_caller_withdrawal_contract as contract,scaled_division_caller_withdrawal_matrix as matrix
from kb import scaled_division_caller_withdrawal_semantics as scalar,scaled_division_caller_withdrawal_transfers as transfers
from kb import scaled_division_caller_withdrawal_capture_evidence as proof,scalar_ram_leaf_withdrawal_contract as withdrawal


def evaluate(entry,**changes):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=entry,**changes)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    return scalar.evaluate(entry,matrix.memory(case),matrix.calibrations(source,image,case),
        matrix.context(source,case),case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)


@pytest.mark.parametrize('first,second,product,result,t',((1,63,63,0,True),
    (32768,32768,0x40000000,0x01000000,False),(65535,65535,0xFFFE0001,0xFFFFF800,False)))
def test_unsigned_word_product_is_reinterpreted_as_signed32_before_six_arithmetic_shifts(first,second,product,result,t):
    assert scalar.product_shift(first,second)==dict(product=product,value=result,t=t)


@pytest.mark.parametrize('source,gain,step,result,fault',((0,16,0,256,True),(5462,1,1,65535,False),
    (32768,16,96,938,False)))
def test_reciprocal_zero_fault_and_unsigned_output_cap_remain_distinct(source,gain,step,result,fault):
    value=evaluate(0x4E59C,reciprocal_source=source,reciprocal_gain=gain)
    assert value['ram'][0x12C2:0x12C4]==step.to_bytes(2,'big')
    assert value['ram'][0x16C0:0x16C2]==result.to_bytes(2,'big')
    assert value['ram'][0x9818:0x981C]==(0x44E if fault else matrix.DEFAULTS['previous_fault']).to_bytes(4,'big')
    assert value['calls'][0]['registers'][:2]==(step,65536)
    assert value['calls'][0]['gbr']==0x0100128C and value['gbr']!=value['calls'][0]['gbr']


@pytest.mark.parametrize('changes,output,calls',(({},73,3),({'first_gain':65535},65535,3),
    ({'first_source':32767,'first_factor':64,'first_gain':32767,'first_divisor':1},32767,2),
    ({'first_source':32767,'first_factor':64,'first_gain':32768,'first_divisor':1},32768,3)))
def test_repeated_signed_division_and_both_saturation_edges_preserve_real_call_count(changes,output,calls):
    value=evaluate(0x74B04,**changes)
    assert value['ram'][0x18E8:0x18EA]==output.to_bytes(2,'big') and len(value['calls'])==calls
    assert value['calls'][0]['target']==0x224FA and all(row['target']==0x21BBC for row in value['calls'][1:])


@pytest.mark.parametrize('current,history,weight,raw',((1,0,1,0xFFFF0000),(-1,0,1,0x0001FFFF),
    (-32768,32767,32768,0x8000FFFF),(73,0xC000,0,73),(73,0xC000,65535,0xFFFFC000)))
def test_signed_blend_retains_both_halves_of_SWAP_W_and_special_weight_paths(current,history,weight,raw):
    assert scalar.blend(current,history,weight)==raw


def test_blend_caller_keeps_full_raw_swap_result_distinct_from_word_publication():
    value=evaluate(0x74478)
    assert value['known_registers'][4]==0x8000E024
    assert value['ram'][0x1CF8:0x1CFA]==bytes.fromhex('0049')
    assert value['ram'][0x1D00:0x1D02]==bytes.fromhex('e024')
    bypass=evaluate(0x74478,flag_first=128)
    assert bypass['ram'][0x1D00:0x1D02]==bytes.fromhex('0049')
    assert not any(row['site'] in (0x74508,0x74514) for row in bypass['events'].values())


@pytest.mark.parametrize('field,value',(('first_source',65536),('second_gain',-1),('first_divisor',True),
    ('second_divisor',65536),('reciprocal_gain',256),('blend_weight',65536),('raw_r4',1<<32),('initial_sr',2)))
def test_input_refuses_width_boolean_or_SR_changes(field,value):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x74B04);case[field]=value
    with pytest.raises(ValueError):matrix.require_case(case)


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_source_refuses_identity_geometry_scale_units_caller_hardware_stub_or_publication(tmp_path,flag):
    p=tmp_path/contract.DESCRIPTOR;p.parent.mkdir(parents=True)
    p.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('name',tuple(contract.REUSED_HELPER_FILES_SHA256))
def test_complete_division_and_register_only_helper_sources_are_byte_exact(monkeypatch,name):
    from pathlib import Path
    read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda p:read(p)+b'\n' if p==repo.ROOT/name else read(p))
    with pytest.raises(ValueError):contract.require_reused_helper_boundary(repo.ROOT)


@pytest.mark.parametrize('root',transfers.NATIVE_ROOTS)
@pytest.mark.parametrize('width,offset',((1,0),(2,-1),(4,-3)))
@pytest.mark.parametrize('domain',('ram','rom','frame'))
def test_selected_ROM_roots_require_physical_interval_absence(root,width,offset,domain):
    rows=[r for r in withdrawal.descriptor(repo.ROOT)['reference'] if r['component']=='scaled_division_caller_withdrawal_paths']
    identity,native,alias=root
    with pytest.raises(ValueError):transfers.require_no_selected_datum(dict(accesses=[dict(site=0x74B2C,
        address=native+offset,width_bytes=width,domain=domain)]),rows)


def test_fixture_retains_complete_natural_callers_real_shift_divider_and_exact_aliases():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image);restored=bytearray(fixture)
    for a,b in contract.SPANS:assert fixture[a:b]==image[a:b]
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert len(aliases)==9 and bytes(restored)==image
    assert set(contract.HELPER_ENTRIES)=={0x21BBC,0x224FA}
    from kb.test_stock_capture import tool
    producer=tool(repo.ROOT,'scaled_division_caller_withdrawal_capture.py','_kb_scaled_division_caller_producer_source_contract')
    assert source['adapter']['marker']==producer.MARKER=='VQ_SH_ELF_SCALED_DIVISION_CALLER_WITHDRAWAL'
    proof_adapter.require_generated(repo.ROOT,contract.DESCRIPTOR)


def test_published_scaling_caller_joint_prior_and_registry_counts_bind_execution_sources():
    declared=withdrawal.descriptor(repo.ROOT);rows=[r for r in declared['reference'] if r['component']=='scaled_division_caller_withdrawal_paths']
    text=(repo.ROOT/'defs/JK08A.scaled-division-caller-withdrawal-paths.md').read_text();words=' '.join(text.split())
    assert len(rows)==3 and len(declared['reference'])==136 and len(declared['function'])==76
    assert len({r['owner'] for r in declared['reference']})==101
    assert [line for line in text.splitlines() if line.startswith('| `7mfk:')]==[
        '| `7mfk:'+f'{r["address"]:08x}'+'` | `7mfk:'+f'{r["function"]:08x}'+'` | `'+r['original_claim_sha256']+'` |' for r in rows]
    for phrase,actual,wanted in (('340 stock instructions',sum((b-a)//2 for a,b in contract.SPANS),340),
        ('680 code bytes',sum(b-a for a,b in contract.SPANS),680),('5 code spans',len(contract.SPANS),5),
        ('191 feasible caller instructions',len(transfers.FEASIBLE_CALLER_SITES),191),
        ('33 literal spans',len(contract.UNIT['pools']),33),('9 pointer aliases',len(contract.UNIT['aliases']),9),
        ('2 controlled word divisors',len(contract.CONFIGURATION),2),('33 complete calibration spans',len(contract.CONTROLLED_CALIBRATION),33),
        ('8 two-sided caller conditions',len(proof.REQUIRED_BRANCHES),8),('1 fixed reciprocal cap',len(proof.FIXED_BRANCHES),1)):
        assert phrase in words and actual==wanted
    owners={r['owner']:r for r in declared['reference']}
    removed=sum(sum(len(m.get('dependency',())) for m in (json.loads(r['original_ledger_json']) or ()))-
        sum(len(m.get('dependency',())) for m in (json.loads(r['proposed_ledger_json']) or ())) for r in owners.values())
    removed+=sum(sum(len(marker.get('dependency',())) for marker in json.loads(row['original_ledger_json']))-
        sum(len(marker.get('dependency',())) for marker in json.loads(row['proposed_ledger_json']))
        for row in declared['function'] if 'proposed_ledger_json' in row)
    assert removed==128 and '126 matching ledger selectors' in words
    assert len(withdrawal.NATIVE_LINK_ROLES)==19 and len(withdrawal.ORIGINAL_LINK_TYPES)==11
    assert all(json.loads(r['original_claim_json'])['type']=='reader' and json.loads(r['original_claim_json'])['roles']==[] for r in rows)
    assert withdrawal.digest(withdrawal.prior_reference_rows(declared,54))==withdrawal.PRIOR_WORD_INTERP_CALLER_REFERENCE_SHA256
    assert withdrawal.digest(declared['function'][:38])==withdrawal.PRIOR_WORD_INTERP_CALLER_FUNCTION_SHA256
    assert len(registry.FAMILIES)==42 and len(registry.captures())==88
    assert '42 families and 88 capture bindings' in words
    assert proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)==16 and 'preceding sixteen adapters' in words
    files={k:v for mapping in (withdrawal.PRIOR_FILES_SHA256,withdrawal.PRIOR_PRODUCT_FILES_SHA256,
        withdrawal.PRIOR_GATED_FILES_SHA256,withdrawal.PRIOR_RPM_RAM_FILES_SHA256,
        withdrawal.PRIOR_OVERFLOW_FILES_SHA256,withdrawal.PRIOR_WORD_FILES_SHA256,
        withdrawal.PRIOR_RPM_STATE_FILES_SHA256,withdrawal.PRIOR_INDEXED_WORD_FILES_SHA256,
        withdrawal.PRIOR_DIVISION_CALLER_FILES_SHA256,withdrawal.PRIOR_BYTE_CURVE_CALLER_FILES_SHA256,
        withdrawal.PRIOR_WORD_INTERP_CALLER_FILES_SHA256) for k,v in mapping.items()}
    assert len(files)==99 and '99 prior domain sources' in words and '98 byte-identical sources' in words
    for name,sha in files.items():assert hashlib.sha256(withdrawal.prior_gated_source_bytes(repo.ROOT,name)).hexdigest()==sha
