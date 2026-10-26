"""Complete three-mode state caller,raw surfaces,local word carrier and implicit curve and exact prior source boundaries."""
import hashlib
import json
import pytest
from kb import repo,proof_adapter
from kb import ordinary_access_registry as registry
from kb import state_surface_caller_withdrawal_contract as contract,state_surface_caller_withdrawal_matrix as matrix
from kb import state_surface_caller_withdrawal_semantics as scalar,state_surface_caller_withdrawal_transfers as transfers
from kb import state_surface_caller_withdrawal_capture_evidence as proof,scalar_ram_leaf_withdrawal_contract as withdrawal


def evaluate(entry,**changes):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=entry,**changes)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    return scalar.evaluate(entry,matrix.memory(case),matrix.calibrations(source,image,case),
        matrix.context(source,case),case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)


@pytest.mark.parametrize('config,flags,next_flags,first,second',(
    (0,64,0,0,255),(0,65,32,255,0),(0,0,32,1,0),(0,1,0,3,4),(0,0,0,1,2),
    (16,255,255,0,255),(16,255,255,255,0),(16,255,255,128,128),
    (16,0,0,127,128),(16,0,0,128,127)))
def test_complete_configured_state_comparisons_and_flag_precedence(config,flags,next_flags,first,second):
    value=evaluate(0x647E8,config_8b3f=config,byte_244f=flags,byte_2450=next_flags,
        byte_1082=first,byte_1083=second)
    expected=('surface' if second<first else 'split' if second>first else 'bypass') if config&16 else (
        'surface' if flags&64 else 'split' if next_flags&32 else 'implicit' if flags&1 else 'bypass')
    assert value['mode']==expected and value['sp']==0x02001000 and value['pr']==0x02100000
    if expected=='bypass':
        for at,width,raw in ((0x13DC,2,0xA5C3),(0x13DE,2,0xC3A5),(0x1861,1,0xA5),(0x1873,1,0x5A)):
            assert int.from_bytes(value['ram'][at:at+width],'big')==raw
        assert not [event for event in value['events'].values() if event['domain']=='ram' and event['mode']=='write']


@pytest.mark.parametrize('first,second,selected,cell,gain',((0,0,0,0,0),(1,0,127,255,255),
    (2,1,128,128,127),(4,3,255,17,129),(255,255,224,254,255)))
def test_complete_packed_selection_and_constant_four_row_surface(first,second,selected,cell,gain):
    settings=dict(byte_1082=first,byte_1083=second,byte_3373=gain,
        **{field:cell for field in matrix.SURFACE_FIELDS},
        **{field:selected for field in matrix.SELECTION_FIELDS})
    value=evaluate(0x647E8,**settings)
    assert value['mode']=='surface' and value['ram'][0x1861]==selected and value['ram'][0x1873]==gain
    assert int.from_bytes(value['ram'][0x13DE:0x13E0],'big')==65535
    assert int.from_bytes(value['ram'][0x13DC:0x13DE],'big')==cell*gain
    selection=next(row for row in value['events'].values() if row['site']==0x64862)
    assert selection['address']==0xB60A+4*(max(1,min(4,first))-1)+min(3,second)
    stored=next(row for row in value['events'].values() if row['site']==0x6486C)
    carrier=next(row for row in value['events'].values() if row['site']==0x2609A)
    assert stored['bytes']==f'{selected:02x}' and carrier['bytes']=='a5a5a5'+stored['bytes']


def test_two_dimensional_half_fraction_keeps_three_real_blend_calls_and_exact_order():
    values=[0]*16;values[0],values[1],values[4],values[5]=0,64,128,192
    value=evaluate(0x647E8,byte_11ae=32,byte_3373=1,
        **{field:32 for field in matrix.SELECTION_FIELDS},
        **{field:raw for field,raw in zip(matrix.SURFACE_FIELDS,values)})
    assert int.from_bytes(value['ram'][0x13DC:0x13DE],'big')==96
    blend=[row for row in value['calls'] if row['site'] in (0x26790,0x267A0,0x267A8)]
    assert [(row['site'],row['target'],row['registers'][3]) for row in blend]==[
        (0x26790,0x26740,32768),(0x267A0,0x26740,32768),(0x267A8,0x26740,32768)]
    assert [row['return_registers'][0] for row in blend]==[32,160,96]


@pytest.mark.parametrize('knots,coordinate,index,fraction',(
    ((200,20,150,220),100,1,80*65536//130),((0,200,10,250),100,2,90*65536//240),
    ((7,7,7,7),6,0,0),((7,7,7,7),7,3,0),((200,20,150,40),100,3,0)))
def test_backward_raw_byte_axis_has_no_global_monotonicity_premise(knots,coordinate,index,fraction):
    selected=scalar.position(knots,coordinate)
    assert (selected['index'],selected['fraction'])==(index,fraction)
    if selected['bracket']:
        assert knots[index]<coordinate<knots[index+1] and selected['denominator']>0


@pytest.mark.parametrize('state,lookup,gain,residual,last',((0,0,0,255,0),(1,255,255,255,255),
    (2,127,128,17,128),(4,128,129,255,127),(255,255,255,255,255)))
def test_split_mode_uses_unsigned_byte_products_floor256_and_nonnegative_residual(state,lookup,gain,residual,last):
    i=max(1,min(4,state))-1
    value=evaluate(0x647E8,byte_244f=0,byte_2450=32,byte_1083=state,byte_3373=gain,config_8799=last,
        **{matrix.SPLIT_FIELDS[i]:lookup,matrix.CURVE_FIELDS[12+i]:residual})
    first=lookup*gain//256
    assert value['mode']=='split' and value['ram'][0x1873]==first
    assert int.from_bytes(value['ram'][0x13DE:0x13E0],'big')==(gain-first)*residual
    assert int.from_bytes(value['ram'][0x13DC:0x13DE],'big')==last*gain
    assert value['ram'][0x1861]==0xA5 and not value['calls']
    assert not {0x6493E,0x64940,0x64942,0x64960}&set(value['path'])


@pytest.mark.parametrize('word,state,gain',((0,0,0),(1,1,255),(90,2,128),(91,3,129),
    (400,4,127),(728,128,255),(8192,255,254),(32768,1,255),(65535,4,255)))
def test_implicit_mode_keeps_full_unsigned_word_scaling_raw_eight_cells_and_endpoint_promotion(word,state,gain):
    data=(255,192,128,64,0,64,128,255);i=max(1,min(4,state))-1
    value=evaluate(0x647E8,byte_244f=1,byte_2450=0,byte_1083=state,byte_3373=gain,word_40c6=word,
        **{matrix.CURVE_FIELDS[j]:raw for j,raw in enumerate(data)},**{matrix.CURVE_FIELDS[8+i]:17})
    coordinate=max(0,min(255,((word*0x2D0E)>>15)-32))
    if coordinate>=224:expected=data[7]
    else:
        index,remainder=divmod(coordinate,32);first,second=data[index:index+2]
        amount=abs(second-first)*remainder//32;expected=first+amount if second>=first else first-amount
    assert value['mode']=='implicit' and value['ram'][0x1873]==0 and value['ram'][0x1861]==0xA5
    assert int.from_bytes(value['ram'][0x13DE:0x13E0],'big')==17*gain
    assert int.from_bytes(value['ram'][0x13DC:0x13DE],'big')==expected*gain
    call=next(row for row in value['calls'] if row['site']==0x649F0)
    assert call['target']==0x26370 and call['registers'][5]==coordinate
    assert (0x26380 in value['path'])==(coordinate>=224)


@pytest.mark.parametrize('field,raw',(('byte_1082',True),('byte_1083',256),('word_40c6',65536),
    ('word_13dc',65536),('surface_value_0',256),('row_axis_0',256),('curve_value_15',256),
    ('config_8b3f',256),('raw_r7',1<<32),('initial_sr',2)))
def test_complete_raw_state_axis_calibration_word_register_and_SR_widths_cannot_be_narrowed(field,raw):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x647E8);case[field]=raw
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
    rows=[row for row in withdrawal.descriptor(repo.ROOT)['reference'] if row['component']=='state_surface_caller_withdrawal_paths']
    identity,address,alias=root
    if form=='alias':
        if alias is None:pytest.skip('the selected ROM root has no RAM alias')
        address=alias
    width=1
    if form=='overlapping-interval':address-=1;width=2
    with pytest.raises(ValueError):transfers.require_no_selected_datum(dict(accesses=[dict(site=0x64A04,
        address=address,width_bytes=width,domain=domain)]),rows)


@pytest.mark.parametrize('name',tuple(contract.REUSED_HELPER_FILES_SHA256))
def test_each_complete_previous_helper_source_is_exact(monkeypatch,name):
    read=__import__('pathlib').Path.read_bytes
    monkeypatch.setattr(__import__('pathlib').Path,'read_bytes',lambda path:read(path)+b'\n' if path==repo.ROOT/name else read(path))
    with pytest.raises(ValueError):contract.require_reused_helper_boundary(repo.ROOT)


def test_fixture_keeps_full_caller_seven_real_helpers_and_complete26A60_parent_with_nine_exact_aliases():
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(declared,image);restored=bytearray(fixture)
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert len(aliases)==9 and bytes(restored)==image
    assert contract.HELPER_ENTRIES==(0x26084,0x26370,0x26944,0x26A60,0x26740,0x26770,0x26C78)
    assert (0x26A60,0x26ABA) in contract.SPANS
    assert len(contract.CONFIGURATION)==62 and len(contract.INPUT_BLOBS)==6
    from kb.test_stock_capture import tool
    producer=tool(repo.ROOT,'state_surface_caller_withdrawal_capture.py','_kb_state_surface_caller_source_contract')
    assert declared['adapter']['marker']==producer.MARKER=='VQ_SH_ELF_STATE_SURFACE_CALLER_WITHDRAWAL'
    proof_adapter.require_generated(repo.ROOT,contract.DESCRIPTOR)


def test_published_state_surface_joint_prior_and_registry_counts_bind_execution_sources():
    declared=withdrawal.descriptor(repo.ROOT);rows=[row for row in declared['reference'] if row['component']=='state_surface_caller_withdrawal_paths']
    text=(repo.ROOT/'defs/JK08A.state-surface-caller-withdrawal-paths.md').read_text();words=' '.join(text.split())
    assert len(rows)==2 and len(declared['reference'])==134 and len(declared['function'])==74
    assert len({row['owner'] for row in declared['reference']})==100
    assert [line for line in text.splitlines() if line.startswith('| `7mfk:')]==[
        '| `7mfk:'+f'{row["address"]:08x}'+'` | `7mfk:'+f'{row["function"]:08x}'+'` | `'+row['original_claim_sha256']+'` |' for row in rows]
    for phrase,actual,wanted in (('474 stock instructions',sum((last-first)//2 for first,last in contract.SPANS),474),
        ('948 code bytes',sum(last-first for first,last in contract.SPANS),948),('9 code spans',len(contract.SPANS),9),
        ('445 feasible instructions',len(transfers.FEASIBLE_SITES),445),('29 excluded instructions',len(transfers.INFEASIBLE_SITES),29),
        ('36 literal spans',len(contract.UNIT['pools']),36),('9 pointer aliases',len(contract.UNIT['aliases']),9),
        ('11 complete RAM fields',len(matrix.RAM_FIELDS),11),('62 scalar configuration fields',len(contract.CONFIGURATION),62),
        ('42 complete calibration spans',len(contract.CONTROLLED_CALIBRATION),42),('83 raw input fields',len(matrix.WIDTHS),83),
        ('16 complete helper sources',len(contract.REUSED_HELPER_FILES_SHA256),16)):
        assert phrase in words and actual==wanted
    assert len(proof.REQUIRED_BRANCHES)==28 and '28 two-sided conditions' in words
    assert len(proof.FIXED_BRANCHES)==4 and '4 fixed conditions' in words
    owners={row['owner']:row for row in declared['reference']}
    datum_removed=sum(sum(len(marker.get('dependency',())) for marker in (json.loads(row['original_ledger_json']) or ()))-
        sum(len(marker.get('dependency',())) for marker in (json.loads(row['proposed_ledger_json']) or ())) for row in owners.values())
    function_removed=sum(sum(len(marker.get('dependency',())) for marker in json.loads(row['original_ledger_json']))-
        sum(len(marker.get('dependency',())) for marker in json.loads(row['proposed_ledger_json']))
        for row in declared['function'] if 'proposed_ledger_json' in row)
    assert datum_removed==118 and function_removed==8 and datum_removed+function_removed==126
    assert '126 matching ledger selectors' in words and '118 datum-end selectors and 8 function-end selectors' in words
    assert len(withdrawal.NATIVE_LINK_ROLES)==19 and len(withdrawal.ORIGINAL_LINK_TYPES)==11
    assert sum(json.loads(row['original_claim_json'])['type']=='reader' for row in declared['reference'])==123
    assert '123 readers and eleven' in words
    from kb import scalar_ram_leaf_withdrawal_evidence as family
    assert len(family.COMPONENTS)==33 and 'Thirty-three independent components' in words
    assert len({row['component'] for row in declared['reference'] if row['owner'].endswith('/ram')})==16
    assert withdrawal.state_surface_prefix_digest(declared,119)==withdrawal.PRIOR_BYTE_RATIO_PRODUCER_REFERENCE_SHA256
    assert withdrawal.digest(declared['function'][:63])==withdrawal.PRIOR_BYTE_RATIO_PRODUCER_FUNCTION_SHA256
    assert len(registry.FAMILIES)==13 and len(registry.captures())==47
    assert 'thirteen families and forty-seven capture bindings' in words
    assert proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)==29 and 'preceding twenty-nine adapters' in words
    files={name:sha for mapping in (withdrawal.PRIOR_FILES_SHA256,withdrawal.PRIOR_PRODUCT_FILES_SHA256,withdrawal.PRIOR_GATED_FILES_SHA256,withdrawal.PRIOR_RPM_RAM_FILES_SHA256,withdrawal.PRIOR_OVERFLOW_FILES_SHA256,withdrawal.PRIOR_WORD_FILES_SHA256,withdrawal.PRIOR_RPM_STATE_FILES_SHA256,withdrawal.PRIOR_INDEXED_WORD_FILES_SHA256,withdrawal.PRIOR_DIVISION_CALLER_FILES_SHA256,withdrawal.PRIOR_BYTE_CURVE_CALLER_FILES_SHA256,withdrawal.PRIOR_WORD_INTERP_CALLER_FILES_SHA256,withdrawal.PRIOR_SCALED_DIVISION_FILES_SHA256,withdrawal.PRIOR_CURVE_SCALE_CALLER_FILES_SHA256,withdrawal.PRIOR_DERIVATIVE_SCALE_CALLER_FILES_SHA256,withdrawal.PRIOR_GUARDED_QUOTIENT_CALLER_FILES_SHA256,withdrawal.PRIOR_MIXED_CURVE_CALLER_FILES_SHA256,withdrawal.PRIOR_TIMING_REMAINDER_CALLER_FILES_SHA256,withdrawal.PRIOR_STATE_RATIO_CALLER_FILES_SHA256,withdrawal.PRIOR_DFCO_STATE_CALLER_FILES_SHA256,withdrawal.PRIOR_PAIRED_INHIBIT_WRITER_FILES_SHA256,withdrawal.PRIOR_THRESHOLD_WINDOW_READER_FILES_SHA256,withdrawal.PRIOR_AUX_RATE_CALLER_FILES_SHA256,withdrawal.PRIOR_PAIRED_CURVE_NORMALIZATION_FILES_SHA256,withdrawal.PRIOR_BYTE_RATIO_PRODUCER_FILES_SHA256,) for name,sha in mapping.items()}
    assert len(files)==216 and '216 prior domain sources' in words and '215 byte-identical sources' in words
    for name,sha in files.items():assert hashlib.sha256(withdrawal.prior_gated_source_bytes(repo.ROOT,name)).hexdigest()==sha
