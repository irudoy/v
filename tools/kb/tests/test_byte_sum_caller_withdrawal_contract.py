"""Complete clipped byte curve,independent minimum and separate saturating word sums and exact prior source boundaries."""
import hashlib
import json
import pytest
from kb import repo,proof_adapter
from kb import ordinary_access_registry as registry
from kb import byte_sum_caller_withdrawal_contract as contract,byte_sum_caller_withdrawal_matrix as matrix
from kb import byte_sum_caller_withdrawal_semantics as scalar,byte_sum_caller_withdrawal_transfers as transfers
from kb import byte_sum_caller_withdrawal_capture_evidence as proof,scalar_ram_leaf_withdrawal_contract as withdrawal


def evaluate(entry,**changes):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=entry,**changes)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    return scalar.evaluate(entry,matrix.memory(case),matrix.calibrations(source,image,case),
        matrix.context(source,case),case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)


@pytest.mark.parametrize('raw,coordinate',((0,0),(39,0),(40,0),(41,4),(47,28),(48,32),(95,220),(96,224),(103,252),(104,255),(255,255)))
def test_complete_unsigned_byte_coordinate_keeps_lower40_scale4_upper255_and_endpoint_boundaries(raw,coordinate):
    value=evaluate(0x464DE,byte_22e4=raw)
    call=next(row for row in value['calls'] if row['site']==0x4654A)
    assert (call['target'],call['registers'][4],call['registers'][5])==(0x26370,0x128D8,coordinate)
    assert (0x26380 in value['path'])==(coordinate>=224)
    assert value['sp']==0x02001000 and value['pr']==0x02100000 and value['known_registers'][0]==0x4BC


@pytest.mark.parametrize('curve,a,b,c,word,last',((0,255,255,255,0,255),(255,255,255,255,65535,255),
    (127,128,255,129,32768,255),(128,127,128,255,65000,254),(1,0,0,0,65535,1),
    (0,0,1,0,65535,0),(255,255,0,0,65280,255),(255,255,0,0,65279,255)))
def test_minimum_does_not_change_the_separate_unclipped_three_byte_sum_and_both_word_caps(curve,a,b,c,word,last):
    value=evaluate(0x464DE,byte_1742=a,byte_1741=b,byte_174f=c,word_174c=word,byte_1740=last,
        **{field:curve for field in matrix.CURVE_FIELDS})
    first=b+c+a;second=min(65535,word+b+min(a,curve));third=min(65535,second+last)
    assert value['ram'][0x1716]==curve
    assert int.from_bytes(value['ram'][0x173C:0x173E],'big')==first
    assert int.from_bytes(value['ram'][0x173E:0x1740],'big')==second
    assert int.from_bytes(value['ram'][0x1748:0x174A],'big')==third
    assert value['known_registers'][7]==b+min(a,curve)
    assert value['known_registers'][2]==second+last and value['known_registers'][6]==third
    stores=[event for event in value['events'].values() if event['domain']=='ram' and event['mode']=='write']
    assert [(event['site'],event['width_bytes']) for event in stores]==[(0x46552,1),(0x46570,2),(0x46590,2),(0x465A6,2)]


@pytest.mark.parametrize('raw',(40,41,47,48,63,64,95,96,103,104,255))
def test_raw_eight_cells_keep_signed_endpoint_return_before_unsigned_minimum_and_word_sums(raw):
    data=(255,192,128,64,0,64,128,255);coordinate=max(0,min(255,(raw-40)*4))
    value=evaluate(0x464DE,byte_22e4=raw,**{field:cell for field,cell in zip(matrix.CURVE_FIELDS,data)})
    if coordinate>=224:expected=data[7]
    else:
        index,remainder=divmod(coordinate,32);a,b=data[index:index+2];amount=abs(b-a)*remainder//32
        expected=a+amount if b>=a else a-amount
    call=next(row for row in value['calls'] if row['site']==0x4654A)
    promoted=(expected|0xFFFFFF00) if coordinate>=224 and expected>=128 else expected
    assert call['return_registers'][0]==promoted and value['ram'][0x1716]==expected


@pytest.mark.parametrize('field,raw',(('byte_22e4',True),('byte_1742',256),('byte_174f',256),('byte_1740',256),
    ('word_174c',65536),('word_173e',65536),('word_1748',65536),('curve_value_0',256),('curve_value_7',256),
    ('raw_r7',1<<32),('initial_sr',2)))
def test_complete_raw_coordinate_byte_word_curve_register_and_SR_widths_cannot_be_narrowed(field,raw):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x464DE);case[field]=raw
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
    rows=[row for row in withdrawal.descriptor(repo.ROOT)['reference'] if row['component']=='byte_sum_caller_withdrawal_paths']
    identity,address,alias=root
    if form=='alias':
        if alias is None:pytest.skip('the selected ROM root has no RAM alias')
        address=alias
    width=1
    if form=='overlapping-interval':address-=1;width=2
    with pytest.raises(ValueError):transfers.require_no_selected_datum(dict(accesses=[dict(site=0x465A6,
        address=address,width_bytes=width,domain=domain)]),rows)


@pytest.mark.parametrize('name',tuple(contract.REUSED_HELPER_FILES_SHA256))
def test_each_complete_previous_helper_source_is_exact(monkeypatch,name):
    read=__import__('pathlib').Path.read_bytes
    monkeypatch.setattr(__import__('pathlib').Path,'read_bytes',lambda path:read(path)+b'\n' if path==repo.ROOT/name else read(path))
    with pytest.raises(ValueError):contract.require_reused_helper_boundary(repo.ROOT)


def test_complete_caller_real_curve_helpers_and_full26A60_parent_keep_two_exact_aliases():
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(declared,image);restored=bytearray(fixture)
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert len(aliases)==2 and bytes(restored)==image
    assert contract.HELPER_ENTRIES==(0x26370,0x26A60,0x26740) and (0x26A60,0x26ABA) in contract.SPANS
    assert len(contract.CONFIGURATION)==8 and contract.INPUT_BLOBS==[dict(name='curve_value_bytes',address=0x128D8,size=8)]
    from kb.test_stock_capture import tool
    producer=tool(repo.ROOT,'byte_sum_caller_withdrawal_capture.py','_kb_byte_sum_caller_source_contract')
    assert declared['adapter']['marker']==producer.MARKER=='VQ_SH_ELF_BYTE_SUM_CALLER_WITHDRAWAL'
    proof_adapter.require_generated(repo.ROOT,contract.DESCRIPTOR)


def test_published_byte_sum_joint_prior_and_registry_counts_bind_execution_sources():
    declared=withdrawal.descriptor(repo.ROOT);rows=[row for row in declared['reference'] if row['component']=='byte_sum_caller_withdrawal_paths']
    text=(repo.ROOT/'defs/JK08A.byte-sum-caller-withdrawal-paths.md').read_text();words=' '.join(text.split())
    assert len(rows)==1 and len(declared['reference'])==125 and len(declared['function'])==67
    assert len({row['owner'] for row in declared['reference']})==95
    assert [line for line in text.splitlines() if line.startswith('| `7mfk:')]==[
        '| `7mfk:'+f'{row["address"]:08x}'+'` | `7mfk:'+f'{row["function"]:08x}'+'` | `'+row['original_claim_sha256']+'` |' for row in rows]
    for phrase,actual,wanted in (('153 stock instructions',sum((last-first)//2 for first,last in contract.SPANS),153),
        ('306 code bytes',sum(last-first for first,last in contract.SPANS),306),('5 code spans',len(contract.SPANS),5),
        ('130 feasible instructions',len(transfers.FEASIBLE_SITES),130),('23 excluded instructions',len(transfers.INFEASIBLE_SITES),23),
        ('16 literal spans',len(contract.UNIT['pools']),16),('2 pointer aliases',len(contract.UNIT['aliases']),2),
        ('10 complete RAM fields',len(matrix.RAM_FIELDS),10),('8 scalar configuration fields',len(contract.CONFIGURATION),8),
        ('17 complete calibration spans',len(contract.CONTROLLED_CALIBRATION),17),('28 raw input fields',len(matrix.WIDTHS),28),
        ('8 complete helper sources',len(contract.REUSED_HELPER_FILES_SHA256),8)):
        assert phrase in words and actual==wanted
    assert len(proof.REQUIRED_BRANCHES)==7 and '7 two-sided conditions' in words
    assert len(proof.FIXED_BRANCHES)==1 and '1 fixed condition' in words
    owners={row['owner']:row for row in declared['reference']}
    datum_removed=sum(sum(len(marker.get('dependency',())) for marker in (json.loads(row['original_ledger_json']) or ()))-
        sum(len(marker.get('dependency',())) for marker in (json.loads(row['proposed_ledger_json']) or ())) for row in owners.values())
    function_removed=sum(sum(len(marker.get('dependency',())) for marker in json.loads(row['original_ledger_json']))-
        sum(len(marker.get('dependency',())) for marker in json.loads(row['proposed_ledger_json']))
        for row in declared['function'] if 'proposed_ledger_json' in row)
    assert datum_removed==109 and function_removed==8 and datum_removed+function_removed==117
    assert len(withdrawal.FUNCTION_POSTIMAGE_IDENTITIES)==5 and len(withdrawal.FUNCTION_POSTIMAGE_CLAIMS)==8
    assert 'five transitions and eight exact function-end selectors' in words
    assert '117 matching ledger selectors' in words and '109 datum-end selectors and 8 function-end selectors' in words
    assert len(withdrawal.NATIVE_LINK_ROLES)==19 and len(withdrawal.ORIGINAL_LINK_TYPES)==10
    assert sum(json.loads(row['original_claim_json'])['type']=='reader' for row in declared['reference'])==115
    assert '115 readers and ten' in words
    from kb import scalar_ram_leaf_withdrawal_evidence as family
    assert len(family.COMPONENTS)==27 and 'Twenty-seven independent components' in words
    shared=(repo.ROOT/'tools/kb/ordinary-access.md').read_text()
    shared=' '.join(shared.split('The `scalar-ram-leaf-withdrawal` registration',1)[1].split('The complete byte-ratio producer',1)[0].split())
    assert len(family.COMPONENTS)==27 and 'Twenty-seven independent components' in shared
    assert f"{len(declared['reference'])} exact original access relations" in shared
    assert f"{len({row['owner'] for row in declared['reference']})} full datum owners" in shared
    assert f"{len(declared['function'])} complete functions" in shared
    assert f'{datum_removed+function_removed} matching ledger selectors' in shared
    assert f'{datum_removed} datum-end and {function_removed} function-end removals' in shared
    assert len(withdrawal.FUNCTION_POSTIMAGE_IDENTITIES)==5 and 'Five complete function transitions' in shared
    assert len(withdrawal.FUNCTION_POSTIMAGE_CLAIMS)==8 and 'eight exact function-end selectors' in shared
    assert sum(json.loads(row['original_claim_json'])['type']=='reader' for row in declared['reference'])==115 and '115 readers' in shared
    assert len(withdrawal.ORIGINAL_LINK_TYPES)==10 and 'ten individually pinned writers' in shared
    assert len(withdrawal.NATIVE_LINK_ROLES)==19 and 'nineteen exact indexed_by originals' in shared
    assert len({row['component'] for row in declared['reference'] if row['owner'].endswith('/ram')})==16
    assert withdrawal.digest(withdrawal.uptight_RAM3348_prior_current_rows(declared,122))==withdrawal.PRIOR_BYTE_FACTOR_CALLER_REFERENCE_SHA256
    assert withdrawal.digest(declared['function'][:65])==withdrawal.PRIOR_BYTE_FACTOR_CALLER_FUNCTION_SHA256
    assert len(registry.FAMILIES)==13 and len(registry.captures())==47
    assert 'thirteen families and forty-seven capture bindings' in words
    assert proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)==31 and 'preceding thirty-one adapters' in words
    files={name:sha for mapping in (withdrawal.PRIOR_FILES_SHA256,withdrawal.PRIOR_PRODUCT_FILES_SHA256,withdrawal.PRIOR_GATED_FILES_SHA256,withdrawal.PRIOR_RPM_RAM_FILES_SHA256,withdrawal.PRIOR_OVERFLOW_FILES_SHA256,withdrawal.PRIOR_WORD_FILES_SHA256,withdrawal.PRIOR_RPM_STATE_FILES_SHA256,withdrawal.PRIOR_INDEXED_WORD_FILES_SHA256,withdrawal.PRIOR_DIVISION_CALLER_FILES_SHA256,withdrawal.PRIOR_BYTE_CURVE_CALLER_FILES_SHA256,withdrawal.PRIOR_WORD_INTERP_CALLER_FILES_SHA256,withdrawal.PRIOR_SCALED_DIVISION_FILES_SHA256,withdrawal.PRIOR_CURVE_SCALE_CALLER_FILES_SHA256,withdrawal.PRIOR_DERIVATIVE_SCALE_CALLER_FILES_SHA256,withdrawal.PRIOR_GUARDED_QUOTIENT_CALLER_FILES_SHA256,withdrawal.PRIOR_MIXED_CURVE_CALLER_FILES_SHA256,withdrawal.PRIOR_TIMING_REMAINDER_CALLER_FILES_SHA256,withdrawal.PRIOR_STATE_RATIO_CALLER_FILES_SHA256,withdrawal.PRIOR_DFCO_STATE_CALLER_FILES_SHA256,withdrawal.PRIOR_PAIRED_INHIBIT_WRITER_FILES_SHA256,withdrawal.PRIOR_THRESHOLD_WINDOW_READER_FILES_SHA256,withdrawal.PRIOR_AUX_RATE_CALLER_FILES_SHA256,withdrawal.PRIOR_PAIRED_CURVE_NORMALIZATION_FILES_SHA256,withdrawal.PRIOR_BYTE_RATIO_PRODUCER_FILES_SHA256,withdrawal.PRIOR_STATE_SURFACE_CALLER_FILES_SHA256,withdrawal.PRIOR_BYTE_FACTOR_CALLER_FILES_SHA256,) for name,sha in mapping.items()}
    assert len(files)==234 and '234 prior domain sources' in words and '233 byte-identical sources' in words
    for name,sha in files.items():assert hashlib.sha256(withdrawal.prior_gated_source_bytes(repo.ROOT,name)).hexdigest()==sha
