"""Exact byte interpolation, endpoint promotion, real helper and native writer boundaries."""
import hashlib
import json
import pytest
from kb import repo,proof_adapter
from kb import ordinary_access_registry as registry
from kb import byte_curve_caller_withdrawal_contract as contract,byte_curve_caller_withdrawal_matrix as matrix
from kb import byte_curve_caller_withdrawal_semantics as scalar,byte_curve_caller_withdrawal_transfers as transfers
from kb import byte_curve_caller_withdrawal_capture_evidence as proof,scalar_ram_leaf_withdrawal_contract as withdrawal


def evaluate(entry,**changes):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=entry,**changes)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    return scalar.evaluate(entry,matrix.memory(case),matrix.calibrations(source,image,case),
        matrix.context(source,case),case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)


@pytest.mark.parametrize('raw,coordinate,expected',((bytes(range(0,256,32)),31,31),
    (bytes((255,223,191,159,127,95,63,31)),31,224),
    (bytes((3,0,0,0,0,0,0,0)),1,3),(bytes((0,3,0,0,0,0,0,0)),1,0),
    (bytes([127])*8,223,127),(bytes([255])*8,224,255),(bytes([255])*8,255,255)))
def test_positive_distance_floor_and_constant_upper_endpoint_are_separate(raw,coordinate,expected):
    value=scalar.lookup(raw,coordinate)
    assert value['value']==expected
    if coordinate>=224:assert value['endpoint'] is True and value['raw_result']==scalar.signed(expected,8)&0xFFFFFFFF
    else:assert value['endpoint'] is False and value['raw_result']==expected


def test_first_caller_retains_signed_endpoint_return_before_explicit_unsigned_word_publication():
    value=evaluate(0x2C59C,coordinate_first=224,curve_first_7=255)
    assert value['calls'][0]['return_registers'][0]==0xFFFFFFFF
    assert value['ram'][0x1F24]==255 and value['ram'][0x1E54:0x1E56]==bytes.fromhex('ff00')
    assert value['known_registers'][0]==0xFF00 and value['gbr']!=value['calls'][0]['gbr']
    assert value['calls'][0]['gbr']==0x01001E50


def test_second_direct_caller_retains_complete_signed_endpoint_register_and_lowbyte_store():
    value=evaluate(0x6E3D8,mode=2,coordinate_second=224,curve_second_7=255)
    assert value['known_registers'][2]==0xFFFFFFFF and value['ram'][0x1766]==255
    assert value['known_registers'][0]==0x4DA and value['division_active'] is False
    assert len(value['calls'])==1 and value['calls'][0]['target']==0x26370


@pytest.mark.parametrize('coordinate,gain,denominator,output,long_path',((1,255,1,255,False),
    (128,64,32,255,True),(64,64,32,128,False),(255,255,1,255,True),(0,255,1,0,False)))
def test_scaled_unsigned_byte_product_uses_real_signed_division_and_explicit_byte_cap(coordinate,gain,denominator,output,long_path):
    value=evaluate(0x6E3D8,mode=0,coordinate_second=coordinate,gain=gain,denominator=denominator)
    assert value['ram'][0x1766]==output and value['division_active'] is True
    assert len(value['calls'])==2 and value['calls'][1]['target']==0x21BBC
    call=value['calls'][1]
    assert call['long_path'] is long_path and call['registers'][0]==denominator
    assert call['registers'][1]==value['curves'][0]['value']*gain==call['macl']
    assert value['known_registers'][6]==call['macl']//denominator


def test_zero_denominator_gate_skips_both_helpers_and_preserves_all_other_RAM():
    value=evaluate(0x6E3D8,mode=0,denominator=0)
    assert value['calls']==[] and value['curves']==[] and value['ram'][0x1766]==255
    assert value['known_registers'][2]==0xFFFFFFFF and value['t'] is True
    assert value['ram'][0x9818:0x981C]==matrix.DEFAULTS['previous_fault'].to_bytes(4,'big')
    assert value['ram'][0x1300:0x1302]==bytes.fromhex('a5a5') and value['ram'][0x1F86]==0xA5


def test_descending_curve_frame_value_precedes_later_divider_save_at_the_same_depth():
    value=evaluate(0x6E3D8,mode=0,coordinate_second=31,gain=64,denominator=32,
        curve_second_0=255,curve_second_1=223)
    frames=value['frame_accesses']
    assert frames[0x26744]==('write',12,0,bytes.fromhex('000000ff'))
    assert frames[0x26752]==('read',12,2,bytes.fromhex('000000ff'))
    assert frames[0x21BBC]==('write',12,2,bytes.fromhex('00000040'))
    assert value['frame'][148:152]==bytes.fromhex('00000040')


@pytest.mark.parametrize('field,value',(('coordinate_first',256),('coordinate_second',-1),
    ('curve_first_0',True),('curve_second_7',256),('raw_r4',1<<32),('initial_sr',2),('initial_sr',0x400)))
def test_input_refuses_curve_coordinate_context_narrowing_or_boolean_values(field,value):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x2C59C);case[field]=value
    with pytest.raises(ValueError):matrix.require_case(case)


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_source_refuses_identity_geometry_scale_units_caller_hardware_stub_or_publication(tmp_path,flag):
    p=tmp_path/contract.DESCRIPTOR;p.parent.mkdir(parents=True)
    p.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('name',tuple(contract.REUSED_HELPER_FILES_SHA256))
def test_existing_real_division_and_interpolation_sources_remain_complete_and_byte_exact(monkeypatch,name):
    from pathlib import Path
    read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda p:read(p)+b'\n' if p==repo.ROOT/name else read(p))
    with pytest.raises(ValueError):contract.require_reused_helper_boundary(repo.ROOT)


@pytest.mark.parametrize('root',transfers.NATIVE_ROOTS)
@pytest.mark.parametrize('form',('native','alias','overlapping-interval'))
@pytest.mark.parametrize('domain',('ram','rom','frame'))
def test_every_exact_native_RAM_root_and_alias_requires_physical_interval_absence(root,form,domain):
    rows=[r for r in withdrawal.descriptor(repo.ROOT)['reference'] if r['component']=='byte_curve_caller_withdrawal_paths']
    identity,native,alias=root;at=alias if form=='alias' else native;width=1
    if form=='overlapping-interval':at-=1;width=2
    with pytest.raises(ValueError):transfers.require_no_selected_datum(dict(accesses=[dict(site=0x2C5A8,address=at,width_bytes=width,domain=domain)]),rows)


def test_fixture_retains_all_caller_and_actual_interior_helper_bytes_with_exact_aliases():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image);restored=bytearray(fixture)
    for a,b in contract.SPANS:assert fixture[a:b]==image[a:b]
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert len(aliases)==6 and bytes(restored)==image
    assert any(a==0x26A80 for a,b in contract.SPANS)
    assert not any(a<=0x26A60<b or a<=0x26A9C<b for a,b in contract.SPANS)
    assert proof.FIXED_BRANCHES=={0x26A9A:'taken'}
    from kb.test_stock_capture import tool
    producer=tool(repo.ROOT,'byte_curve_caller_withdrawal_capture.py','_kb_byte_curve_caller_producer_source_contract')
    assert source['adapter']['marker']==producer.MARKER=='VQ_SH_ELF_BYTE_CURVE_CALLER_WITHDRAWAL'
    proof_adapter.require_generated(repo.ROOT,contract.DESCRIPTOR)


def test_published_caller_interior_curve_joint_and_prior_counts_bind_execution_sources():
    declared=withdrawal.descriptor(repo.ROOT);rows=[r for r in declared['reference'] if r['component']=='byte_curve_caller_withdrawal_paths']
    text=(repo.ROOT/'defs/JK08A.byte-curve-caller-withdrawal-paths.md').read_text();words=' '.join(text.split())
    assert len(rows)==5 and len(declared['reference'])==127 and len(declared['function'])==68
    assert len({r['owner'] for r in declared['reference']})==97
    assert [line for line in text.splitlines() if line.startswith('| `7mfk:')]==[
        '| `7mfk:'+f'{r["address"]:08x}'+'` | `7mfk:'+f'{r["function"]:08x}'+'` | `'+r['original_claim_sha256']+'` |' for r in rows]
    for phrase,actual,wanted in (('266 stock instructions',sum((b-a)//2 for a,b in contract.SPANS),266),
        ('532 code bytes',sum(b-a for a,b in contract.SPANS),532),('7 code spans',len(contract.SPANS),7),
        ('125 caller/byte-helper instructions',len(transfers.EXACT_SITES),125),
        ('18 literal spans',len(contract.UNIT['pools']),18),('6 pointer aliases',len(contract.UNIT['aliases']),6),
        ('16 typed curve-cell bytes',len(contract.CONFIGURATION),16),('20 complete calibration spans',len(contract.CONTROLLED_CALIBRATION),20),
        ('5 two-sided conditional sites',len(proof.REQUIRED_BRANCHES),5),('1 fixed byte-mode condition',len(proof.FIXED_BRANCHES),1)):
        assert phrase in words and actual==wanted
    owners={r['owner']:r for r in declared['reference']}
    removed=sum(sum(len(m.get('dependency',())) for m in (json.loads(r['original_ledger_json']) or ()))-
        sum(len(m.get('dependency',())) for m in (json.loads(r['proposed_ledger_json']) or ())) for r in owners.values())
    removed+=sum(sum(len(marker.get('dependency',())) for marker in json.loads(row['original_ledger_json']))-
        sum(len(marker.get('dependency',())) for marker in json.loads(row['proposed_ledger_json']))
        for row in declared['function'] if 'proposed_ledger_json' in row)
    assert removed==119 and '119 matching ledger selectors' in words
    assert len(withdrawal.NATIVE_LINK_ROLES)==19
    assert withdrawal.ORIGINAL_LINK_TYPES=={'00052034-ffff120e-withdraw':'writer',
        '0006e3d8-ffff1300-withdraw':'writer','0006e3d8-ffff1f86-withdraw':'writer'}
    assert sum(json.loads(r['original_claim_json'])['type']=='writer' for r in rows)==2
    assert withdrawal.digest(withdrawal.prior_reference_rows(declared,44))==withdrawal.PRIOR_DIVISION_CALLER_REFERENCE_SHA256
    assert withdrawal.digest(declared['function'][:34])==withdrawal.PRIOR_DIVISION_CALLER_FUNCTION_SHA256
    assert len(registry.FAMILIES)==13 and len(registry.captures())==47
    assert 'thirteen families and forty-seven capture bindings' in words
    assert proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)==14 and 'preceding fourteen adapters' in words
    files={k:v for mapping in (withdrawal.PRIOR_FILES_SHA256,withdrawal.PRIOR_PRODUCT_FILES_SHA256,
        withdrawal.PRIOR_GATED_FILES_SHA256,withdrawal.PRIOR_RPM_RAM_FILES_SHA256,
        withdrawal.PRIOR_OVERFLOW_FILES_SHA256,withdrawal.PRIOR_WORD_FILES_SHA256,
        withdrawal.PRIOR_RPM_STATE_FILES_SHA256,withdrawal.PRIOR_INDEXED_WORD_FILES_SHA256,
        withdrawal.PRIOR_DIVISION_CALLER_FILES_SHA256) for k,v in mapping.items()}
    assert len(files)==81 and '81 prior domain sources' in words and '80 byte-identical sources' in words
    for name,sha in files.items():assert hashlib.sha256(withdrawal.prior_gated_source_bytes(repo.ROOT,name)).hexdigest()==sha
