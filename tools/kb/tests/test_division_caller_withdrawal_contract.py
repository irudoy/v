"""Separate quotient/clamp, exact real-helper source and native shared-owner boundaries."""
import hashlib
import json
import pytest
from kb import repo,proof_adapter
from kb import ordinary_access_registry as registry
from kb import division_caller_withdrawal_contract as contract,division_caller_withdrawal_matrix as matrix
from kb import division_caller_withdrawal_semantics as scalar,division_caller_withdrawal_transfers as transfers
from kb import division_caller_withdrawal_capture_evidence as proof,scalar_ram_leaf_withdrawal_contract as withdrawal


def evaluate(entry,**changes):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=entry,**changes)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    return scalar.evaluate(entry,matrix.memory(case),matrix.calibrations(source,image,case),
        matrix.context(source,case),case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)


@pytest.mark.parametrize('argument,output',((0,0),(19,0),(20,1),(5099,254),(5100,255),(65535,255),(0x800003E8,50)))
def test_enabled_word_argument_uses_low16_signed_division_by20_and_byte_cap(argument,output):
    value=evaluate(0x3A254,raw_r4=argument)
    assert value['ram'][0x1020]==value['ram'][0x118E]==output
    assert value['known_registers'][0]==0x7A and value['calls'][0]['arguments']=={0:20,1:argument&65535}
    assert value['t']==((argument&65535)//20>255)


def test_disabled_word_caller_retains_complete_RAM_and_has_no_helper():
    value=evaluate(0x3A254,enable_mask=128)
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x3A254,enable_mask=128)
    assert value['ram']==matrix.memory(case) and value['calls']==[]
    assert value['known_registers'][0]==0xFFFFFF80 and value['t'] is True


@pytest.mark.parametrize('level,factor,output',((0,255,0),(1,255,255),(50,60,72),(255,0,50),(255,255,68)))
def test_unsigned_source_byte_divisor_factor_product_bias_and_cap(level,factor,output):
    value=evaluate(0x6E442,source_level=level,factor=factor)
    assert value['ram'][0x1F86]==output and value['known_registers'][0]==0x126
    if level:
        call=value['calls'][0]
        assert call['arguments']=={0:level*80,1:factor*1475} and call['macl']==factor*1475
    else:assert value['calls']==[]


@pytest.mark.parametrize('argument,first,second,output',((1,50,60,6),
    (0xFFFFFFFF,50,60,-6),(0x7FFFFFFF,1,1,200000),(0x80000000,1,1,-200000),
    (1,0,1,200000),(0xFFFFFFFF,1,0,-200000),(0,0,0,200000),
    (100000,255,255,186306)))
def test_signed_input_and_output_clamps_zero_product_bypass_and_truncation(argument,first,second,output):
    value=evaluate(0xB7C84,raw_r4=argument,factor_first=first,factor_second=second)
    assert scalar.signed(int.from_bytes(value['ram'][0x3400:0x3404],'big'))==output
    assert value['known_registers'][0]==0xB08
    if first*second:
        call=value['calls'][0]
        numerator=max(-107350,min(107350,scalar.signed(argument)))
        assert call['arguments']=={0:min(first*second,10735),1:(numerator*20000)&0xFFFFFFFF}
        assert call['macl']==(numerator*20000)&0xFFFFFFFF
    else:assert value['calls']==[]


@pytest.mark.parametrize('entry,changes,short_site,long_site',((0x3A254,dict(raw_r4=65535),0x21C04,0x21C6C),
    (0x6E442,dict(source_level=1,factor=255),0x21D08,0x21D66),
    (0xB7C84,dict(raw_r4=107350,factor_first=1,factor_second=1),0x21C04,0x21C6C)))
def test_long_helper_frame_preserves_independent_saved_words_and_post_delay_state(entry,changes,short_site,long_site):
    value=evaluate(entry,**changes);call=value['calls'][0]
    assert call['long_path'] is True and call['return_address']==call['site']+4
    assert call['sr']==0 and call['sp']==0x02001000-(4 if entry==0x3A254 else 8)
    assert len(call['registers'])==15 and call['registers'][0:2]==tuple(call['arguments'][i] for i in (0,1))
    assert any(mode=='write' and depth>=16 for mode,depth,register,raw in value['frame_accesses'].values())
    assert value['frame']!=bytes([0xA5])*192


@pytest.mark.parametrize('field,value',(('factor',256),('source_level',-1),('factor_first',True),
    ('raw_r4',1<<32),('previous_fault',1<<32),('initial_sr',2),('initial_sr',0x400)))
def test_inputs_refuse_narrowing_boolean_or_undeclared_SR_bits(field,value):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x3A254);case[field]=value
    with pytest.raises(ValueError):matrix.require_case(case)


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_source_refuses_identity_geometry_scale_units_caller_hardware_stub_or_publication(tmp_path,flag):
    p=tmp_path/contract.DESCRIPTOR;p.parent.mkdir(parents=True)
    p.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('name',tuple(contract.REUSED_DIVISION_FILES_SHA256))
def test_reused_full_direct_helper_input_fixture_equations_producer_and_consumer_bytes_remain_exact(monkeypatch,name):
    from pathlib import Path
    read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda p:read(p)+b'\n' if p==repo.ROOT/name else read(p))
    with pytest.raises(ValueError):contract.require_reused_division_boundary(repo.ROOT)


@pytest.mark.parametrize('root',transfers.NATIVE_ROOTS)
@pytest.mark.parametrize('form',('native','alias','overlapping-interval'))
@pytest.mark.parametrize('domain',('ram','rom','frame'))
def test_exact_selected_ROM_and_native_RAM_roots_refuse_every_physical_alias_interval(root,form,domain):
    rows=[r for r in withdrawal.descriptor(repo.ROOT)['reference'] if r['component']=='division_caller_withdrawal_paths']
    identity,native,alias=root;at=alias if form=='alias' and alias is not None else native;width=1
    if form=='overlapping-interval':at-=1;width=2
    with pytest.raises(ValueError):transfers.require_no_selected_datum(dict(accesses=[dict(site=0x3A258,address=at,width_bytes=width,domain=domain)]),rows)


def test_fixture_preserves_every_caller_and_real_helper_instruction_and_only_exact_aliases():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image);restored=bytearray(fixture)
    for a,b in contract.SPANS:assert fixture[a:b]==image[a:b]
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert len(aliases)==8 and bytes(restored)==image
    assert tuple((r['start'],r['end']) for r in source['entry'][:2])==transfers.HELPER_SPANS
    from kb.test_stock_capture import tool
    producer=tool(repo.ROOT,'division_caller_withdrawal_capture.py','_kb_division_caller_producer_source_contract')
    assert source['adapter']['marker']==producer.MARKER=='VQ_SH_ELF_DIVISION_CALLER_WITHDRAWAL'
    proof_adapter.require_generated(repo.ROOT,contract.DESCRIPTOR)


def test_published_source_helper_joint_role_and_preserved_counts_bind_current_execution_sources():
    declared=withdrawal.descriptor(repo.ROOT);rows=[r for r in declared['reference'] if r['component']=='division_caller_withdrawal_paths']
    text=(repo.ROOT/'defs/JK08A.division-caller-withdrawal-paths.md').read_text();words=' '.join(text.split())
    assert len(rows)==3 and len(declared['reference'])==134 and len(declared['function'])==74
    assert len({r['owner'] for r in declared['reference']})==100
    assert [line for line in text.splitlines() if line.startswith('| `7mfk:')]==[
        '| `7mfk:'+f'{r["address"]:08x}'+'` | `7mfk:'+f'{r["function"]:08x}'+'` | `'+r['original_claim_sha256']+'` |' for r in rows]
    for phrase,actual,wanted in (('375 stock instructions',sum((b-a)//2 for a,b in contract.SPANS),375),
        ('750 code bytes',sum(b-a for a,b in contract.SPANS),750),('5 code spans',len(contract.SPANS),5),
        ('119 caller instructions',len(transfers.CALLER_SITES),119),('256 real helper instructions',sum((b-a)//2 for a,b in transfers.HELPER_SPANS),256),
        ('29 literal/configuration spans',len(contract.UNIT['pools']),29),('8 pointer aliases',len(contract.UNIT['aliases']),8),
        ('3 configuration bytes',len(contract.CONFIGURATION),3),('11 two-sided caller conditions',len(proof.REQUIRED_BRANCHES),11)):
        assert phrase in words and actual==wanted
    owners={r['owner']:r for r in declared['reference']}
    removed=sum(sum(len(m.get('dependency',())) for m in (json.loads(r['original_ledger_json']) or ()))-
        sum(len(m.get('dependency',())) for m in (json.loads(r['proposed_ledger_json']) or ())) for r in owners.values())
    removed+=sum(sum(len(marker.get('dependency',())) for marker in json.loads(row['original_ledger_json']))-
        sum(len(marker.get('dependency',())) for marker in json.loads(row['proposed_ledger_json']))
        for row in declared['function'] if 'proposed_ledger_json' in row)
    assert removed==126 and '126 matching ledger selectors' in words
    assert len(withdrawal.NATIVE_LINK_ROLES)==19 and '5 exact indexed_by originals' in words
    assert withdrawal.ORIGINAL_LINK_TYPES=={'00052034-ffff120e-withdraw':'writer','0006e3d8-ffff1300-withdraw':'writer','0006e3d8-ffff1f86-withdraw':'writer'}
    assert all(json.loads(r['original_claim_json'])['type']=='reader' for r in rows)
    assert withdrawal.digest(withdrawal.prior_reference_rows(declared,41))==withdrawal.PRIOR_INDEXED_WORD_REFERENCE_SHA256
    assert withdrawal.digest(declared['function'][:31])==withdrawal.PRIOR_INDEXED_WORD_FUNCTION_SHA256
    assert len(registry.FAMILIES)==13 and len(registry.captures())==47
    assert 'thirteen families and forty-seven capture bindings' in words
    assert proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)==13 and 'preceding thirteen adapters' in words
    files={k:v for mapping in (withdrawal.PRIOR_FILES_SHA256,withdrawal.PRIOR_PRODUCT_FILES_SHA256,
        withdrawal.PRIOR_GATED_FILES_SHA256,withdrawal.PRIOR_RPM_RAM_FILES_SHA256,
        withdrawal.PRIOR_OVERFLOW_FILES_SHA256,withdrawal.PRIOR_WORD_FILES_SHA256,
        withdrawal.PRIOR_RPM_STATE_FILES_SHA256,withdrawal.PRIOR_INDEXED_WORD_FILES_SHA256) for k,v in mapping.items()}
    assert len(files)==72 and '72 prior domain sources' in words and '71 byte-identical sources' in words
    for name,sha in files.items():assert hashlib.sha256(withdrawal.prior_gated_source_bytes(repo.ROOT,name)).hexdigest()==sha
