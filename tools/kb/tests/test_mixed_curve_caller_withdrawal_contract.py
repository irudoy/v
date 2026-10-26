"""Exact mixed curve callers, unsigned lookup operands and complete retained sources."""
import hashlib
import json
import pytest
from kb import repo,proof_adapter
from kb import ordinary_access_registry as registry
from kb import mixed_curve_caller_withdrawal_contract as contract,mixed_curve_caller_withdrawal_matrix as matrix
from kb import mixed_curve_caller_withdrawal_semantics as scalar,mixed_curve_caller_withdrawal_transfers as transfers
from kb import mixed_curve_caller_withdrawal_capture_evidence as proof,scalar_ram_leaf_withdrawal_contract as withdrawal


def evaluate(entry,**changes):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=entry,**changes)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    return scalar.evaluate(entry,matrix.memory(case),matrix.calibrations(source,image,case),
        matrix.context(source,case),case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)


def test_zero_implicit_curve_keeps_unsigned_old_byte_and_full_wrapped_delta():
    value=evaluate(0x3B498,word_1e60=0,word_114e=0,word_120e=0,byte_1170=255,
        **{field:0 for field in matrix.IMPLICIT_FIELDS})
    assert value['ram'][0x1E62:0x1E64]==bytes(2) and value['ram'][0x1170]==0
    assert value['known_registers'][0]==0xFFFFFF01 and value['ram'][0x1138:0x113A]==bytes.fromhex('ff01')
    assert value['lookups'][0]['base']==0x15042 and value['lookups'][0]['coordinate']==0


@pytest.mark.parametrize('coordinate,base,helper_coordinate',((0,0x15042,0),(15359,0x15042,61436),
    (15360,0x15022,0),(65535,0x15022,50175)))
def test_actual_implicit_base_literals_keep_their_separate_coordinate_domains(coordinate,base,helper_coordinate):
    value=evaluate(0x3B498,word_1e60=512,word_114e=coordinate,word_120e=0)
    call=next(row for row in value['calls'] if row['site']==0x3B500)
    assert call['registers'][4:6]==(base,helper_coordinate)
    assert not any(site in (0x26402,0x26404) for site in value['path'])


def test_each_separate_admission_flag_can_enable_the_signed_word_computation():
    disabled=evaluate(0x41DB6,byte_2465=0,byte_2468=0)
    assert disabled['output']==128 and disabled['known_registers'][0]==0xFFFFFF80 and disabled['calls']==[]
    for first,second in ((64,0),(0,4)):
        value=evaluate(0x41DB6,byte_2465=first,byte_2468=second)
        assert [row['target'] for row in value['calls']]==[0x21BBC]


@pytest.mark.parametrize('word,output',((0,255),(32767,255),(32768,0),(65535,0)))
def test_zero_denominator_uses_the_caller_sentinel_without_a_divider_fault_store(word,output):
    value=evaluate(0x41DB6,word_1752=0,byte_1765=0,byte_1763=0,byte_1f62=0,word_2266=word)
    assert value['calls']==[] and value['output']==output and value['ram'][0x2315]==output
    assert value['ram'][0x9818:0x981C]==matrix.DEFAULTS['previous_fault'].to_bytes(4,'big')


@pytest.mark.parametrize('word,output',((0,128),(1,255),(65535,0),(32768,0)))
def test_real_signed_word_numerator_and_one_divisor_keep_byte_caps(word,output):
    value=evaluate(0x41DB6,word_1752=1,byte_1765=0,byte_1763=0,byte_1f62=0,word_2266=word)
    call=next(row for row in value['calls'] if row['site']==0x41E0C)
    assert call['registers'][0]==1 and call['registers'][1]==((word if word<32768 else word-65536)*128)&0xFFFFFFFF
    assert value['output']==output and value['ram'][0x2315]==output


def test_alternate_timing_mode_preserves_the_unwritten_lookup_publications():
    value=evaluate(0x4BDC2,byte_2458=32,byte_23c5=0,byte_1a7d=64,byte_23ee=0)
    assert value['output']==0 and value['calls']==[]
    for at in (0x134C,0x1348,0x134A):
        assert value['ram'][at]==next(matrix.DEFAULTS[name] for name,address,width in matrix.RAM_FIELDS if address==at)


@pytest.mark.parametrize('biased,gain,unsigned_word,signed_word,output',((16384,0,0,0,0),
    (16384,0,65535,32767,32767),(0,255,65535,32767,32768)))
def test_raw_unsigned_signed_product_and_weight_bypass_keep_both_word_clamps(biased,gain,unsigned_word,signed_word,output):
    value=evaluate(0x659AE,word_18e4=biased,gain_byte=gain,word_2408=unsigned_word,
        word_18ca=signed_word,byte_15eb=0)
    assert value['output']==output and value['ram'][0x18CC:0x18CE]==output.to_bytes(2,'big')
    assert [row['target'] for row in value['calls']]==[0x224F8]


@pytest.mark.parametrize('field,value',(('byte_1765',True),('byte_106f',256),('word_2266',65536),
    ('implicit_word_29',65536),('surface_word_63',65536),('previous_fault',1<<32),('raw_r6',1<<32),('initial_sr',2)))
def test_inputs_refuse_boolean_narrowing_width_or_SR_changes(field,value):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x3B498);case[field]=value
    with pytest.raises(ValueError):matrix.require_case(case)


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_source_refuses_identity_geometry_scale_units_caller_hardware_stub_or_publication(tmp_path,flag):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    path.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('name',tuple(contract.REUSED_HELPER_FILES_SHA256))
def test_every_complete_timing_implicit_register_and_divider_source_remains_exact(monkeypatch,name):
    from pathlib import Path
    read=Path.read_bytes
    monkeypatch.setattr(Path,'read_bytes',lambda path:read(path)+b'\n' if path==repo.ROOT/name else read(path))
    with pytest.raises(ValueError):contract.require_reused_helper_boundary(repo.ROOT)


@pytest.mark.parametrize('root',transfers.NATIVE_ROOTS)
@pytest.mark.parametrize('form',('native','overlapping-interval'))
@pytest.mark.parametrize('domain',('ram','rom','frame'))
def test_each_selected_original_ROM_root_requires_physical_interval_absence(root,form,domain):
    rows=[r for r in withdrawal.descriptor(repo.ROOT)['reference'] if r['component']=='mixed_curve_caller_withdrawal_paths']
    identity,address,alias=root;assert alias is None
    if form=='overlapping-interval':address-=1;width=2
    else:width=1
    with pytest.raises(ValueError):transfers.require_no_selected_datum(dict(accesses=[dict(site=0x4BE92,
        address=address,width_bytes=width,domain=domain)]),rows)


def test_fixture_keeps_all_natural_code_exact_and_only_twenty_two_declared_pointer_aliases():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image);restored=bytearray(fixture)
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert len(aliases)==22 and bytes(restored)==image and len(contract.HELPER_ENTRIES)==13
    assert fixture[0x1503E:0x15042]==image[0x1503E:0x15042]
    assert not any(row['address']<0x15042 and 0x1503E<row['address']+row['size'] for row in contract.CONTROLLED_CALIBRATION)
    implicit=[row for row in contract.INPUT_BLOBS if row['name'].startswith('implicit_')]
    assert [(row['address'],row['size']) for row in implicit]==[(0x15022,28),(0x15042,32)]
    from kb.test_stock_capture import tool
    producer=tool(repo.ROOT,'mixed_curve_caller_withdrawal_capture.py','_kb_mixed_curve_producer_source_contract')
    assert source['adapter']['marker']==producer.MARKER=='VQ_SH_ELF_MIXED_CURVE_CALLER_WITHDRAWAL'
    proof_adapter.require_generated(repo.ROOT,contract.DESCRIPTOR)


def test_published_mixed_joint_prior_and_registry_counts_bind_execution_sources():
    declared=withdrawal.descriptor(repo.ROOT);rows=[r for r in declared['reference'] if r['component']=='mixed_curve_caller_withdrawal_paths']
    text=(repo.ROOT/'defs/JK08A.mixed-curve-caller-withdrawal-paths.md').read_text();words=' '.join(text.split())
    assert len(rows)==8 and len(declared['reference'])==127 and len(declared['function'])==68
    assert len({r['owner'] for r in declared['reference']})==97
    assert [line for line in text.splitlines() if line.startswith('| `7mfk:')]==[
        '| `7mfk:'+f'{r["address"]:08x}'+'` | `7mfk:'+f'{r["function"]:08x}'+'` | `'+r['original_claim_sha256']+'` |' for r in rows]
    for phrase,actual,wanted in (('964 stock instructions',sum((b-a)//2 for a,b in contract.SPANS),964),
        ('1928 code bytes',sum(b-a for a,b in contract.SPANS),1928),('17 code spans',len(contract.SPANS),17),
        ('876 feasible instructions',len(transfers.FEASIBLE_SITES),876),('70 literal spans',len(contract.UNIT['pools']),70),
        ('22 pointer aliases',len(contract.UNIT['aliases']),22),('43 complete RAM fields',len(matrix.RAM_FIELDS),43),
        ('114 scalar configuration fields',len(contract.CONFIGURATION),114),('79 complete calibration spans',len(contract.CONTROLLED_CALIBRATION),79),
        ('175 raw input fields',len(matrix.WIDTHS),175),('33 reused helper sources',len(contract.REUSED_HELPER_FILES_SHA256),33),
        ('44 two-sided conditions',len(proof.REQUIRED_BRANCHES),44),('7 fixed branch premises',len(proof.FIXED_BRANCHES),7)):
        assert phrase in words and actual==wanted
    owners={r['owner']:r for r in declared['reference']}
    removed=sum(sum(len(m.get('dependency',())) for m in (json.loads(r['original_ledger_json']) or ()))-
        sum(len(m.get('dependency',())) for m in (json.loads(r['proposed_ledger_json']) or ())) for r in owners.values())
    removed+=sum(sum(len(marker.get('dependency',())) for marker in json.loads(row['original_ledger_json']))-
        sum(len(marker.get('dependency',())) for marker in json.loads(row['proposed_ledger_json']))
        for row in declared['function'] if 'proposed_ledger_json' in row)
    assert removed==119 and '119 matching ledger selectors' in words
    assert len(withdrawal.NATIVE_LINK_ROLES)==19 and len(withdrawal.ORIGINAL_LINK_TYPES)==10
    assert withdrawal.digest(withdrawal.prior_reference_rows(declared,79))==withdrawal.PRIOR_GUARDED_QUOTIENT_CALLER_REFERENCE_SHA256
    assert withdrawal.digest(declared['function'][:47])==withdrawal.PRIOR_GUARDED_QUOTIENT_CALLER_FUNCTION_SHA256
    assert len(registry.FAMILIES)==13 and len(registry.captures())==47
    assert 'thirteen families and forty-seven capture bindings' in words
    assert proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)==20 and 'preceding twenty adapters' in words
    files={k:v for mapping in (withdrawal.PRIOR_FILES_SHA256,withdrawal.PRIOR_PRODUCT_FILES_SHA256,
        withdrawal.PRIOR_GATED_FILES_SHA256,withdrawal.PRIOR_RPM_RAM_FILES_SHA256,
        withdrawal.PRIOR_OVERFLOW_FILES_SHA256,withdrawal.PRIOR_WORD_FILES_SHA256,
        withdrawal.PRIOR_RPM_STATE_FILES_SHA256,withdrawal.PRIOR_INDEXED_WORD_FILES_SHA256,
        withdrawal.PRIOR_DIVISION_CALLER_FILES_SHA256,withdrawal.PRIOR_BYTE_CURVE_CALLER_FILES_SHA256,
        withdrawal.PRIOR_WORD_INTERP_CALLER_FILES_SHA256,withdrawal.PRIOR_SCALED_DIVISION_FILES_SHA256,
        withdrawal.PRIOR_CURVE_SCALE_CALLER_FILES_SHA256,withdrawal.PRIOR_DERIVATIVE_SCALE_CALLER_FILES_SHA256,
        withdrawal.PRIOR_GUARDED_QUOTIENT_CALLER_FILES_SHA256) for k,v in mapping.items()}
    assert len(files)==135 and '135 prior domain sources' in words and '134 byte-identical sources' in words
    for name,sha in files.items():assert hashlib.sha256(withdrawal.prior_gated_source_bytes(repo.ROOT,name)).hexdigest()==sha
