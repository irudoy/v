"""Exact paired raw callers, literal holes, fifth argument and complete native boundaries."""
import hashlib
import json
import pytest
from kb import repo,proof_adapter
from kb import ordinary_access_registry as registry
from kb import derivative_scale_caller_withdrawal_contract as contract,derivative_scale_caller_withdrawal_matrix as matrix
from kb import derivative_scale_caller_withdrawal_semantics as scalar,derivative_scale_caller_withdrawal_transfers as transfers
from kb import derivative_scale_caller_withdrawal_capture_evidence as proof,scalar_ram_leaf_withdrawal_contract as withdrawal


def evaluate(entry,**changes):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=entry,**changes)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    context=matrix.context(source,case);frame=bytearray([0xA5])*192
    frame[160:164]=context[19].to_bytes(4,'big');frame[164:168]=context[7].to_bytes(4,'big')
    return scalar.evaluate(entry,matrix.memory(case),matrix.calibrations(source,image,case),
        context,case['initial_sr'],bytes(frame),0x02001000,0x02100000)


@pytest.mark.parametrize('entry,divisor_field,offset',((0xB78DA,'raw_r7',0x2F98),(0xB7A3C,'raw_r4',0x3228)))
def test_zero_word_divisor_is_an_explicit_caller_bypass_and_preserves_the_fault_word(entry,divisor_field,offset):
    value=evaluate(entry,**{divisor_field:0xABCD0000})
    assert value['output']==0 and value['ram'][offset:offset+4]==bytes(4)
    assert value['ram'][0x9818:0x981C]==matrix.DEFAULTS['previous_fault'].to_bytes(4,'big')
    assert all(call.get('divisor')!=0 for call in value['calls'])
    assert len([call for call in value['calls'] if call['target']==0x21BBC])==1


@pytest.mark.parametrize('entry',contract.ENTRIES)
def test_controlled_zero_curves_retain_distinct_250_and_2500_final_divisors(entry):
    changes={name:0 for fields in matrix.CURVE_FIELDS.values() for name in fields}
    changes.update(raw_r6=0,ratio_gain_first=1,ratio_gain_second=1,ratio_gain_middle=1,
        negative_gain_first=0,negative_gain_second=0,threshold_word=0)
    changes.update(dict(raw_r4=0,raw_r5=0,raw_r7=1000) if entry==0xB78DA else dict(raw_r4=1000,raw_r5=0,raw_r7=0))
    value=evaluate(entry,**changes)
    assert value['candidate']==0 and value['nonnegative'] is True and value['output']==5000
    unsigned=[call for call in value['calls'] if call['target']==0x21CE0]
    assert [call['divisor'] for call in unsigned]==[255,250 if entry==0xB78DA else 2500]
    assert unsigned[0]['dividend']==318750 and unsigned[1]['dividend']==1250000


@pytest.mark.parametrize('entry,site',((0xB78DA,0xB78F0),(0xB7A3C,0xB7A62)))
@pytest.mark.parametrize('dividend',(0,1,0x7FFFFFFF,0x80000000,0xFFFFFFFF))
def test_first_signed_call_keeps_the_original_complete_raw_dividend(entry,site,dividend):
    value=evaluate(entry,raw_r6=dividend)
    call=next(row for row in value['calls'] if row['site']==site)
    assert call['registers'][:2]==(20000,dividend)


@pytest.mark.parametrize('count',(8,16))
def test_real_axis_extent_uses_unsigned_knots_and_both_interpolation_directions(count):
    value=scalar.position(tuple(i*1000 for i in range(count)),1500)
    assert (value['index'],value['fraction'])==(1,32768)
    assert scalar.linear(1000,2000,value['fraction'])['value']==1500
    assert scalar.linear(2000,1000,value['fraction'])['value']==1500
    assert scalar.position((0,)*(count-1)+(65535,),65535)['index']==count-1


@pytest.mark.parametrize('field,value',(('curve_first_00',True),('curve_middle_08',65536),
    ('curve_last_16',65536),('threshold_word',65536),('ratio_gain_middle',256),
    ('stack_argument',1<<32),('raw_r6',1<<32),('axis_middle_style',7),('axis_last_seed',65536),('initial_sr',2)))
def test_input_refuses_boolean_width_axis_and_full_stack_carrier_changes(field,value):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0xB78DA);case[field]=value
    with pytest.raises(ValueError):matrix.require_case(case)


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_source_refuses_identity_geometry_scale_units_caller_hardware_stub_or_publication(tmp_path,flag):
    p=tmp_path/contract.DESCRIPTOR;p.parent.mkdir(parents=True)
    p.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('name',tuple(contract.REUSED_HELPER_FILES_SHA256))
def test_complete_timing_normalization_division_and_viridian_sources_are_byte_exact(monkeypatch,name):
    from pathlib import Path
    read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda p:read(p)+b'\n' if p==repo.ROOT/name else read(p))
    with pytest.raises(ValueError):contract.require_reused_helper_boundary(repo.ROOT)


@pytest.mark.parametrize('root',transfers.NATIVE_ROOTS)
@pytest.mark.parametrize('form',('native','alias','overlapping-interval'))
@pytest.mark.parametrize('domain',('ram','rom','frame'))
def test_every_exact_selected_root_and_alias_requires_physical_interval_absence(root,form,domain):
    rows=[r for r in withdrawal.descriptor(repo.ROOT)['reference'] if r['component']=='derivative_scale_caller_withdrawal_paths']
    identity,native,alias=root
    if form=='alias' and alias is None:pytest.skip('the selected ROM root has no RAM alias')
    at=alias if form=='alias' else native;width=1
    if form=='overlapping-interval':at-=1;width=2
    with pytest.raises(ValueError):transfers.require_no_selected_datum(dict(accesses=[dict(site=0xB7A2E,
        address=at,width_bytes=width,domain=domain)]),rows)


def test_fixture_preserves_literal_holes_seven_real_helpers_and_only_three_exact_pointer_aliases():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image);restored=bytearray(fixture)
    for a,b in contract.SPANS:assert fixture[a:b]==image[a:b]
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert {row['address'] for row in aliases}=={0x21CD8,0x21DC8,0xB7C18} and bytes(restored)==image
    for at,raw in ((0xB79A0,'ffff763c'),(0xB7C20,'ffff763c'),(0xB7C04,'ffff0001')):
        assert fixture[at:at+4]==image[at:at+4]==bytes.fromhex(raw)
    for first,last in ((0xB794C,0xB79AC),(0xB7AFA,0xB7B06)):
        assert fixture[first:last]==image[first:last]
        assert not any(max(first,a)<min(last,b) for a,b in contract.SPANS)
    assert set(contract.HELPER_ENTRIES)=={0x21BBC,0x21CE0,0x264CC,0x264F8,0x26740,0x26984,0x26C78}
    from kb.test_stock_capture import tool
    producer=tool(repo.ROOT,'derivative_scale_caller_withdrawal_capture.py','_kb_derivative_scale_caller_producer_source_contract')
    assert source['adapter']['marker']==producer.MARKER=='VQ_SH_ELF_DERIVATIVE_SCALE_CALLER_WITHDRAWAL'
    proof_adapter.require_generated(repo.ROOT,contract.DESCRIPTOR)


def test_published_paired_joint_prior_and_registry_counts_bind_execution_sources():
    declared=withdrawal.descriptor(repo.ROOT);rows=[r for r in declared['reference'] if r['component']=='derivative_scale_caller_withdrawal_paths']
    text=(repo.ROOT/'defs/JK08A.derivative-scale-caller-withdrawal-paths.md').read_text();words=' '.join(text.split())
    assert len(rows)==11 and len(declared['reference'])==123 and len(declared['function'])==66
    assert len({r['owner'] for r in declared['reference']})==94
    assert [line for line in text.splitlines() if line.startswith('| `7mfk:')]==[
        '| `7mfk:'+f'{r["address"]:08x}'+'` | `7mfk:'+f'{r["function"]:08x}'+'` | `'+r['original_claim_sha256']+'` |' for r in rows]
    for phrase,actual,wanted in (('715 stock instructions',sum((b-a)//2 for a,b in contract.SPANS),715),
        ('1430 code bytes',sum(b-a for a,b in contract.SPANS),1430),('11 code spans',len(contract.SPANS),11),
        ('614 feasible instructions',len(transfers.FEASIBLE_SITES),614),
        ('53 literal spans',len(contract.UNIT['pools']),53),('3 pointer aliases',len(contract.UNIT['aliases']),3),
        ('43 physical curve words',sum(len(fields) for fields in matrix.CURVE_FIELDS.values()),43),
        ('40 axis words',sum(matrix.AXES.values()),40),('56 complete calibration spans',len(contract.CONTROLLED_CALIBRATION),56),
        ('72 raw input fields',len(matrix.WIDTHS),72),('31 reused helper sources',len(contract.REUSED_HELPER_FILES_SHA256),31),
        ('31 two-sided conditions',len(proof.REQUIRED_BRANCHES),31),('7 fixed branch premises',len(proof.FIXED_BRANCHES),7)):
        assert phrase in words and actual==wanted
    owners={r['owner']:r for r in declared['reference']}
    removed=sum(sum(len(m.get('dependency',())) for m in (json.loads(r['original_ledger_json']) or ()))-
        sum(len(m.get('dependency',())) for m in (json.loads(r['proposed_ledger_json']) or ())) for r in owners.values())
    removed+=sum(sum(len(marker.get('dependency',())) for marker in json.loads(row['original_ledger_json']))-
        sum(len(marker.get('dependency',())) for marker in json.loads(row['proposed_ledger_json']))
        for row in declared['function'] if 'proposed_ledger_json' in row)
    assert removed==115 and '115 matching ledger selectors' in words
    assert len(withdrawal.NATIVE_LINK_ROLES)==18 and len(withdrawal.ORIGINAL_LINK_TYPES)==10
    assert withdrawal.digest(withdrawal.prior_reference_rows(declared,60))==withdrawal.PRIOR_CURVE_SCALE_CALLER_REFERENCE_SHA256
    assert withdrawal.digest(declared['function'][:42])==withdrawal.PRIOR_CURVE_SCALE_CALLER_FUNCTION_SHA256
    assert len(registry.FAMILIES)==13 and len(registry.captures())==47
    assert 'thirteen families and forty-seven capture bindings' in words
    assert proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)==18 and 'preceding eighteen adapters' in words
    files={k:v for mapping in (withdrawal.PRIOR_FILES_SHA256,withdrawal.PRIOR_PRODUCT_FILES_SHA256,
        withdrawal.PRIOR_GATED_FILES_SHA256,withdrawal.PRIOR_RPM_RAM_FILES_SHA256,
        withdrawal.PRIOR_OVERFLOW_FILES_SHA256,withdrawal.PRIOR_WORD_FILES_SHA256,
        withdrawal.PRIOR_RPM_STATE_FILES_SHA256,withdrawal.PRIOR_INDEXED_WORD_FILES_SHA256,
        withdrawal.PRIOR_DIVISION_CALLER_FILES_SHA256,withdrawal.PRIOR_BYTE_CURVE_CALLER_FILES_SHA256,
        withdrawal.PRIOR_WORD_INTERP_CALLER_FILES_SHA256,withdrawal.PRIOR_SCALED_DIVISION_FILES_SHA256,
        withdrawal.PRIOR_CURVE_SCALE_CALLER_FILES_SHA256) for k,v in mapping.items()}
    assert len(files)==117 and '117 prior domain sources' in words and '116 byte-identical sources' in words
    for name,sha in files.items():assert hashlib.sha256(withdrawal.prior_gated_source_bytes(repo.ROOT,name)).hexdigest()==sha
