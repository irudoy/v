"""Complete raw signed-word difference,dual byte factors and capped partial products and exact prior source boundaries."""
import hashlib
import json
import pytest
from kb import repo,proof_adapter
from kb import ordinary_access_registry as registry
from kb import byte_factor_caller_withdrawal_contract as contract,byte_factor_caller_withdrawal_matrix as matrix
from kb import byte_factor_caller_withdrawal_semantics as scalar,byte_factor_caller_withdrawal_transfers as transfers
from kb import byte_factor_caller_withdrawal_capture_evidence as proof,scalar_ram_leaf_withdrawal_contract as withdrawal


def evaluate(entry,**changes):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=entry,**changes)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    return scalar.evaluate(entry,matrix.memory(case),matrix.calibrations(source,image,case),
        matrix.context(source,case),case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)


@pytest.mark.parametrize('prior,decrement',((0,0),(0,255),(1,1),(127,63),(128,64),(255,0),(255,1),(255,127),(255,128),(255,255)))
def test_in_place_override_keeps_full_raw_byte_preimage_and_zero_clamp(prior,decrement):
    value=evaluate(0x4BA48,byte_2478=2,byte_1657=prior,config_886d=decrement)
    assert value['mode']=='override' and value['ram'][0x1657]==max(prior-2*decrement,0)
    assert value['ram'][0x1658:0x165A]==bytes((0xA5,0x5A)) and not value['calls']
    assert value['known_registers'][0]==0x3CB and 'byte_1657' not in matrix.ENTRY_FIELDS[0x4BA48]
    assert [(row['site'],row['width_bytes']) for row in value['events'].values() if row['mode']=='write' and row['domain']=='ram']==[(0x4BB5E,1)]


@pytest.mark.parametrize('first,second,gain',((0,0,0),(0,32767,255),(0,32768,255),(65535,32768,255),
    (65535,65535,255),(65535,0,255),(1000,100,128),(1,0,1),(1,65535,254)))
def test_percentage_mode_keeps_unsigned_first_signed_second_low32_product_and_logical_shift14(first,second,gain):
    value=evaluate(0x4BA48,byte_2458=32,word_15fc=first,word_15fe=second,config_886b=gain)
    signed_second=second-65536 if second&32768 else second;difference=max(first-signed_second,0)
    raw=(((difference*gain)&0xFFFFFFFF)*100)&0xFFFFFFFF;shifted=raw>>14
    assert value['mode']=='percentage' and value['ram'][0x1657]==min(255,shifted)
    assert value['known_registers'][6]==(0xFFFFFFFF if shifted>255 else shifted)
    assert value['ram'][0x1658:0x165A]==bytes((0xA5,0x5A)) and not value['calls']
    assert 0x4BABE in value['path'] and 0x4BB5E not in value['path']


@pytest.mark.parametrize('first,second,a,b',((0,0,255,255),(0,32767,255,255),(0,32768,255,255),
    (65535,32768,255,255),(65535,65535,255,255),(65535,0,1,1),(1000,100,127,128),
    (1,0,255,255),(1,65535,254,255),(65535,32768,0,255),(65535,32768,255,0)))
def test_two_real_byte_factors_keep_distinct_low_high_products_high_term_cap_and_final_byte_cap(first,second,a,b):
    value=evaluate(0x4BA48,word_15fc=first,word_15fe=second,
        **{field:a if i<8 else b for i,field in enumerate(matrix.CURVE_FIELDS)})
    signed_second=second-65536 if second&32768 else second;difference=max(first-signed_second,0)
    scaled=(difference*100)&0xFFFFFFFF;product=a*b
    low=((scaled&65535)*product)&0xFFFFFFFF;high=((scaled>>16)*product)&0xFFFFFFFF
    combined=((low>>16)&65535)+min(high,65535);expected=min(255,combined>>5)
    assert value['mode']=='curves' and value['ram'][0x1657:0x165A]==bytes((expected,a,b))
    calls=[row for row in value['calls'] if row['site'] in (0x4BADE,0x4BB0C)]
    assert [(row['site'],row['target'],row['registers'][4],row['registers'][14]) for row in calls]==[
        (0x4BADE,0x26370,0x126A8,difference),(0x4BB0C,0x26370,0x126A0,difference)]
    assert value['sp']==0x02001000 and value['pr']==0x02100000 and value['known_registers'][0]==0x3CB
    high_branch=next(row for row in value['controls'] if row['site']==0x4BB40)
    assert high_branch['kind']==('taken' if high>65535 else 'fallthrough')


@pytest.mark.parametrize('first_word,second_word',((0,0),(1,31),(127,32),(128,33),(32767,255),
    (32768,256),(65535,287),(65535,288),(65535,65535)))
def test_full_unsigned_word_coordinates_reach_raw_curves_with_both_signed_endpoint_promotions(first_word,second_word):
    first=(255,192,128,64,0,64,128,255);second=tuple(reversed(first))
    value=evaluate(0x4BA48,word_1024=first_word,word_11bc=second_word,
        **{field:raw for field,raw in zip(matrix.CURVE_FIELDS,(*first,*second))})
    def expected(data,coordinate):
        if coordinate>=224:return data[7]
        index,remainder=divmod(coordinate,32);a,b=data[index:index+2];amount=abs(b-a)*remainder//32
        return a+amount if b>=a else a-amount
    coordinates=(min(255,first_word>>7),min(255,max(0,second_word-32)))
    wanted=(expected(second,coordinates[0]),expected(first,coordinates[1]))
    assert value['ram'][0x1659]==wanted[0] and value['ram'][0x1658]==wanted[1]
    for site,coordinate,raw in zip((0x4BADE,0x4BB0C),coordinates,wanted):
        call=next(row for row in value['calls'] if row['site']==site)
        assert call['registers'][5]==coordinate
        promoted=(raw|0xFFFFFF00) if coordinate>=224 and raw>=128 else raw
        assert call['return_registers'][0]==promoted


@pytest.mark.parametrize('field,raw',(('byte_2478',True),('byte_1657',256),('word_15fc',65536),
    ('word_15fe',65536),('word_1024',65536),('word_11bc',65536),('curve_value_0',256),('curve_value_15',256),
    ('config_886b',256),('config_886d',256),('raw_r7',1<<32),('initial_sr',2)))
def test_complete_raw_signed_unsigned_word_byte_curve_register_and_SR_inputs_refuse_narrowing(field,raw):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x4BA48);case[field]=raw
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
    rows=[row for row in withdrawal.descriptor(repo.ROOT)['reference'] if row['component']=='byte_factor_caller_withdrawal_paths']
    identity,address,alias=root
    if form=='alias':
        if alias is None:pytest.skip('the selected ROM root has no RAM alias')
        address=alias
    width=1
    if form=='overlapping-interval':address-=1;width=2
    with pytest.raises(ValueError):transfers.require_no_selected_datum(dict(accesses=[dict(site=0x4BB5E,
        address=address,width_bytes=width,domain=domain)]),rows)


@pytest.mark.parametrize('name',tuple(contract.REUSED_HELPER_FILES_SHA256))
def test_each_complete_previous_helper_source_is_exact(monkeypatch,name):
    read=__import__('pathlib').Path.read_bytes
    monkeypatch.setattr(__import__('pathlib').Path,'read_bytes',lambda path:read(path)+b'\n' if path==repo.ROOT/name else read(path))
    with pytest.raises(ValueError):contract.require_reused_helper_boundary(repo.ROOT)


def test_complete_caller_and_byte_helper_sources_keep_five_exact_aliases_and_full26A60_parent():
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(declared,image);restored=bytearray(fixture)
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert len(aliases)==5 and bytes(restored)==image
    assert contract.HELPER_ENTRIES==(0x26370,0x26A60,0x26740) and (0x26A60,0x26ABA) in contract.SPANS
    assert len(contract.CONFIGURATION)==18 and contract.INPUT_BLOBS==[dict(name='curve_value_bytes',address=0x126A0,size=16)]
    from kb.test_stock_capture import tool
    producer=tool(repo.ROOT,'byte_factor_caller_withdrawal_capture.py','_kb_byte_factor_caller_source_contract')
    assert declared['adapter']['marker']==producer.MARKER=='VQ_SH_ELF_BYTE_FACTOR_CALLER_WITHDRAWAL'
    proof_adapter.require_generated(repo.ROOT,contract.DESCRIPTOR)


def test_published_byte_factor_joint_prior_and_registry_counts_bind_execution_sources():
    declared=withdrawal.descriptor(repo.ROOT);rows=[row for row in declared['reference'] if row['component']=='byte_factor_caller_withdrawal_paths']
    text=(repo.ROOT/'defs/JK08A.byte-factor-caller-withdrawal-paths.md').read_text();words=' '.join(text.split())
    assert len(rows)==1 and len(declared['reference'])==135 and len(declared['function'])==75
    assert len({row['owner'] for row in declared['reference']})==100
    assert [line for line in text.splitlines() if line.startswith('| `7mfk:')]==[
        '| `7mfk:'+f'{row["address"]:08x}'+'` | `7mfk:'+f'{row["function"]:08x}'+'` | `'+row['original_claim_sha256']+'` |' for row in rows]
    for phrase,actual,wanted in (('221 stock instructions',sum((last-first)//2 for first,last in contract.SPANS),221),
        ('442 code bytes',sum(last-first for first,last in contract.SPANS),442),('5 code spans',len(contract.SPANS),5),
        ('198 feasible instructions',len(transfers.FEASIBLE_SITES),198),('23 excluded instructions',len(transfers.INFEASIBLE_SITES),23),
        ('19 literal spans',len(contract.UNIT['pools']),19),('5 pointer aliases',len(contract.UNIT['aliases']),5),
        ('9 complete RAM fields',len(matrix.RAM_FIELDS),9),('18 scalar configuration fields',len(contract.CONFIGURATION),18),
        ('20 complete calibration spans',len(contract.CONTROLLED_CALIBRATION),20),('37 raw input fields',len(matrix.WIDTHS),37),
        ('8 complete helper sources',len(contract.REUSED_HELPER_FILES_SHA256),8)):
        assert phrase in words and actual==wanted
    assert len(proof.REQUIRED_BRANCHES)==12 and '12 two-sided conditions' in words
    assert len(proof.FIXED_BRANCHES)==1 and '1 fixed condition' in words
    owners={row['owner']:row for row in declared['reference']}
    datum_removed=sum(sum(len(marker.get('dependency',())) for marker in (json.loads(row['original_ledger_json']) or ()))-
        sum(len(marker.get('dependency',())) for marker in (json.loads(row['proposed_ledger_json']) or ())) for row in owners.values())
    function_removed=sum(sum(len(marker.get('dependency',())) for marker in json.loads(row['original_ledger_json']))-
        sum(len(marker.get('dependency',())) for marker in json.loads(row['proposed_ledger_json']))
        for row in declared['function'] if 'proposed_ledger_json' in row)
    assert datum_removed==119 and function_removed==8 and datum_removed+function_removed==127
    assert len(withdrawal.FUNCTION_POSTIMAGE_IDENTITIES)==5 and len(withdrawal.FUNCTION_POSTIMAGE_CLAIMS)==8
    assert 'five transitions and eight exact function-end selectors' in words
    assert '126 matching ledger selectors' in words and '118 datum-end selectors and 8 function-end selectors' in words
    assert len(withdrawal.NATIVE_LINK_ROLES)==19 and len(withdrawal.ORIGINAL_LINK_TYPES)==11
    assert sum(json.loads(row['original_claim_json'])['type']=='reader' for row in declared['reference'])==123
    assert '123 readers and eleven' in words
    from kb import scalar_ram_leaf_withdrawal_evidence as family
    assert len(family.COMPONENTS)==34 and 'Thirty-four independent components' in words
    assert len({row['component'] for row in declared['reference'] if row['owner'].endswith('/ram')})==16
    assert withdrawal.digest(withdrawal.uptight_RAM3348_prior_current_rows(declared,121))==withdrawal.PRIOR_STATE_SURFACE_CALLER_REFERENCE_SHA256
    assert withdrawal.digest(declared['function'][:64])==withdrawal.PRIOR_STATE_SURFACE_CALLER_FUNCTION_SHA256
    assert len(registry.FAMILIES)==13 and len(registry.captures())==47
    assert 'thirteen families and forty-seven capture bindings' in words
    assert proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)==30 and 'preceding thirty adapters' in words
    files={name:sha for mapping in (withdrawal.PRIOR_FILES_SHA256,withdrawal.PRIOR_PRODUCT_FILES_SHA256,withdrawal.PRIOR_GATED_FILES_SHA256,withdrawal.PRIOR_RPM_RAM_FILES_SHA256,withdrawal.PRIOR_OVERFLOW_FILES_SHA256,withdrawal.PRIOR_WORD_FILES_SHA256,withdrawal.PRIOR_RPM_STATE_FILES_SHA256,withdrawal.PRIOR_INDEXED_WORD_FILES_SHA256,withdrawal.PRIOR_DIVISION_CALLER_FILES_SHA256,withdrawal.PRIOR_BYTE_CURVE_CALLER_FILES_SHA256,withdrawal.PRIOR_WORD_INTERP_CALLER_FILES_SHA256,withdrawal.PRIOR_SCALED_DIVISION_FILES_SHA256,withdrawal.PRIOR_CURVE_SCALE_CALLER_FILES_SHA256,withdrawal.PRIOR_DERIVATIVE_SCALE_CALLER_FILES_SHA256,withdrawal.PRIOR_GUARDED_QUOTIENT_CALLER_FILES_SHA256,withdrawal.PRIOR_MIXED_CURVE_CALLER_FILES_SHA256,withdrawal.PRIOR_TIMING_REMAINDER_CALLER_FILES_SHA256,withdrawal.PRIOR_STATE_RATIO_CALLER_FILES_SHA256,withdrawal.PRIOR_DFCO_STATE_CALLER_FILES_SHA256,withdrawal.PRIOR_PAIRED_INHIBIT_WRITER_FILES_SHA256,withdrawal.PRIOR_THRESHOLD_WINDOW_READER_FILES_SHA256,withdrawal.PRIOR_AUX_RATE_CALLER_FILES_SHA256,withdrawal.PRIOR_PAIRED_CURVE_NORMALIZATION_FILES_SHA256,withdrawal.PRIOR_BYTE_RATIO_PRODUCER_FILES_SHA256,withdrawal.PRIOR_STATE_SURFACE_CALLER_FILES_SHA256,) for name,sha in mapping.items()}
    assert len(files)==225 and '225 prior domain sources' in words and '224 byte-identical sources' in words
    for name,sha in files.items():assert hashlib.sha256(withdrawal.prior_gated_source_bytes(repo.ROOT,name)).hexdigest()==sha
