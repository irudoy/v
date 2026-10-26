"""Complete DFCO state, indexed bytes, raw frame carriers and exact prior source boundaries."""
import hashlib
import json
import pytest
from kb import repo,proof_adapter
from kb import ordinary_access_registry as registry
from kb import dfco_state_caller_withdrawal_contract as contract,dfco_state_caller_withdrawal_matrix as matrix
from kb import dfco_state_caller_withdrawal_semantics as scalar,dfco_state_caller_withdrawal_transfers as transfers
from kb import dfco_state_caller_withdrawal_capture_evidence as proof,scalar_ram_leaf_withdrawal_contract as withdrawal


def evaluate(entry,**changes):
    defaults=matrix.RESTORE_DEFAULTS if entry==0x50018 else matrix.DEFAULTS
    case=dict(defaults,index=0,kind='controlled',entry=entry,**changes)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    return scalar.evaluate(entry,matrix.memory(case),matrix.calibrations(source,image,case),
        matrix.context(source,case),case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)


@pytest.mark.parametrize('mask,next_mask',((1,2),(2,4),(4,8),(8,16),(16,32),(32,1),(0,0),(3,0),(128,0),(255,0)))
def test_real_rotation_retains_valid_one_hot_and_invalid_mask_domains(mask,next_mask):
    value=evaluate(0x503E0,raw_r4=0,raw_r5=0,byte_14c1=0,byte_193a=255,byte_1936=mask,byte_1937=1,
        **{field:0 for field in matrix.STATE_FIELDS})
    assert value['rotations']==1 and value['known_registers'][0]==next_mask
    assert [(row['site'],row['target'],row['registers'][4]) for row in value['calls']]==[(0x50642,0x50766,mask)]
    assert value['calls'][0]['return_registers'][0]==next_mask


def test_raw_count255_keeps_six_real_calls_and_the_unmodified_counter_byte():
    value=evaluate(0x503E0,raw_r4=0,raw_r5=0,byte_14c1=0,byte_193a=255,byte_1936=1,byte_1937=255,
        **{field:0 for field in matrix.STATE_FIELDS})
    assert value['rotations']==6 and value['known_registers'][0]==63 and value['ram'][0x1937]==255
    assert [row['registers'][4] for row in value['calls']]==[1,2,4,8,16,32]
    assert [row['registers'][13] for row in value['calls']]==[1,2,3,4,5,6]


@pytest.mark.parametrize('state',(0,1,2,3,4,5,127,128,255))
@pytest.mark.parametrize('byte',(0,1,127,128,255))
def test_every_admitted_state_index_uses_the_complete_raw_byte_table_without_a_four_state_cap(state,byte):
    value=evaluate(0x503E0,raw_r4=0,raw_r5=0,byte_14c1=state,byte_193a=255,byte_1937=0,
        byte_2571=1,byte_2572=1,byte_2573=1,**{matrix.STATE_FIELDS[state]:byte})
    read=next(row for row in value['events'].values() if row['site']==0x50658)
    assert (read['address'],read['width_bytes'],read['bytes'])==(0x2371C+state,1,f'{byte:02x}')
    assert value['known_registers'][0]==byte and value['ram'][0x14C1]==state and value['rotations']==0


def test_full_R6_carrier_preserves_word_dword_and_byte_frame_operations():
    value=evaluate(0x503E0,raw_r4=1,raw_r5=0,raw_r6=0x12340078,byte_14c1=0,byte_2571=0,byte_2572=0)
    rows=[next(row for row in value['events'].values() if row['site']==site) for site in (0x503F4,0x50406,0x50490,0x504AC)]
    assert [(row['mode'],row['width_bytes'],row['bytes']) for row in rows]==[
        ('write',2,'0078'),('write',4,'12340078'),('read',1,'00'),('read',1,'78')]
    assert value['ram'][0x2571]==0 and value['ram'][0x2572]==120 and value['ram'][0x14C1]==2


@pytest.mark.parametrize('coordinate,index',((0,0),(10,1),(255,2)))
def test_each_real_delay_byte_and_actual1939_publication_retains_its_independent_index(coordinate,index):
    value=evaluate(0x503E0,config_8b3f=0,byte_1517=coordinate)
    assert value['ram'][0x1939]==index
    assert value['ram'][0x193A]==matrix.DEFAULTS[f'delay_byte_{0x1269D+index:05x}']
    assert value['ram'][0x1938]==matrix.DEFAULTS[f'delay_byte_{0x1269A+index:05x}']
    assert any(row['site']==0x50574 and row['address']==0x01001939 and row['mode']=='write' for row in value['events'].values())


def test_expired_delay_copies_the_full_byte_before_the_separate_six_call_loop_bound():
    value=evaluate(0x503E0,raw_r4=0,raw_r5=0,byte_14c1=0,byte_193a=1,byte_1938=7,byte_1936=1)
    assert value['ram'][0x193A]==255 and value['ram'][0x1937]==7
    assert value['rotations']==6 and value['known_registers'][0]==63


@pytest.mark.parametrize('field,value',(('byte_14c1',True),('state_byte_255',256),('delay_byte_1269f',256),
    ('word_11b6',65536),('raw_r6',1<<32),('initial_sr',2)))
def test_raw_state_table_delay_word_register_and_SR_inputs_refuse_narrowing(field,value):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x503E0);case[field]=value
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
    rows=[row for row in withdrawal.descriptor(repo.ROOT)['reference'] if row['component']=='dfco_state_caller_withdrawal_paths'
        and row['function']==0x503E0 and row['id']!=transfers.READER1939_IDENTITY[0]]
    transfers.require_no_selected_datum(dict(accesses=[]),rows)
    identity,address,alias=root
    if form=='alias':
        if alias is None:pytest.skip('the selected ROM root has no RAM alias')
        address=alias
    width=1
    if form=='overlapping-interval':address-=1;width=2
    with pytest.raises(ValueError):transfers.require_no_selected_datum(dict(accesses=[dict(site=0x50574,
        address=address,width_bytes=width,domain=domain)]),rows)


def test_fixture_keeps_five_literal_holes_full_rotation_and_all_raw_indexed_bytes():
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(declared,image);restored=bytearray(fixture)
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert len(aliases)==30 and bytes(restored)==image
    for first,last in ((0x50400,0x50402),(0x50444,0x50484),(0x50552,0x50554),(0x5068C,0x50698),(0x506AE,0x506E8)):
        assert restored[first:last]==image[first:last]
        assert not any(max(first,start)<min(last,end) for start,end in contract.SPANS)
    assert (0x50766,0x5079C) in contract.SPANS and contract.STATE_HELPER_ENTRIES==(0x50766,)
    assert contract.STATE_INPUT_BLOBS==[dict(name='delay_bytes',address=0x1269A,size=6),dict(name='state_bytes',address=0x2371C,size=256)]
    assert len(matrix.STATE_FIELDS)==256 and len(matrix.DELAY_FIELDS)==6
    from kb.test_stock_capture import tool
    producer=tool(repo.ROOT,'dfco_state_caller_withdrawal_capture.py','_kb_DFCO_state_producer_source_contract')
    assert declared['adapter']['marker']==producer.MARKER=='VQ_SH_ELF_DFCO_STATE_CALLER_WITHDRAWAL'
    proof_adapter.require_generated(repo.ROOT,contract.DESCRIPTOR)


def test_published_DFCO_joint_prior_and_registry_counts_bind_execution_sources():
    declared=withdrawal.descriptor(repo.ROOT);rows=[row for row in declared['reference'] if row['component']=='dfco_state_caller_withdrawal_paths']
    text=(repo.ROOT/'defs/JK08A.dfco-state-caller-withdrawal-paths.md').read_text();words=' '.join(text.split())
    assert len(rows)==9 and len(declared['reference'])==126 and len(declared['function'])==68
    assert len({row['owner'] for row in declared['reference']})==96
    assert [line for line in text.splitlines() if line.startswith('| `7mfk:')]==[
        '| `7mfk:'+f'{row["address"]:08x}'+'` | `7mfk:'+f'{row["function"]:08x}'+'` | `'+row['original_claim_sha256']+'` |' for row in rows]
    for phrase,actual,wanted in (('409 stock instructions',sum((last-first)//2 for first,last in contract.STATE_SPANS),409),
        ('818 code bytes',sum(last-first for first,last in contract.STATE_SPANS),818),('7 code spans',len(contract.STATE_SPANS),7),
        ('409 feasible instructions',len(transfers.STATE_FEASIBLE_SITES),409),('42 literal spans',len(contract.STATE_UNIT['pools']),42),
        ('13 pointer aliases',len(contract.STATE_UNIT['aliases']),13),('25 complete RAM fields',len(matrix.STATE_RAM_FIELDS),25),
        ('271 configuration fields',len(contract.STATE_CONFIGURATION),271),('44 complete calibration spans',len(contract.STATE_CONTROLLED_CALIBRATION),44),
        ('306 raw input fields',len(matrix.STATE_WIDTHS),306)):
        assert phrase in words and actual==wanted
    assert f'{len(proof.STATE_REQUIRED_BRANCHES)} two-sided conditions' in words and proof.STATE_FIXED_BRANCHES=={}
    assert transfers.STATE_FEASIBLE_SITES==transfers.STATE_EXACT_SITES
    owners={row['owner']:row for row in declared['reference']}
    removed=sum(sum(len(marker.get('dependency',())) for marker in (json.loads(row['original_ledger_json']) or ()))-
        sum(len(marker.get('dependency',())) for marker in (json.loads(row['proposed_ledger_json']) or ())) for row in owners.values())
    removed+=sum(sum(len(marker.get('dependency',())) for marker in json.loads(row['original_ledger_json']))-
        sum(len(marker.get('dependency',())) for marker in json.loads(row['proposed_ledger_json']))
        for row in declared['function'] if 'proposed_ledger_json' in row)
    assert removed==118 and '118 matching ledger selectors' in words
    assert len(withdrawal.NATIVE_LINK_ROLES)==19 and len(withdrawal.ORIGINAL_LINK_TYPES)==10
    assert sum(json.loads(row['original_claim_json'])['type']=='reader' for row in declared['reference'])==115
    assert '116 readers and ten' in words
    from kb import scalar_ram_leaf_withdrawal_evidence as family
    assert len(family.COMPONENTS)==27 and 'Twenty-seven independent components' in words
    assert len({row['component'] for row in declared['reference'] if row['owner'].endswith('/ram')})==16
    for name in ('tools/kb/README.md','tools/kb/SPEC.md','tools/sh-elf-run/README.md','tools/kb/ordinary-access.md'):
        assert 'Fourteen native-RAM components' in ' '.join((repo.ROOT/name).read_text().split())
    assert withdrawal.digest(withdrawal.prior_reference_rows(declared,100))==withdrawal.PRIOR_STATE_RATIO_CALLER_REFERENCE_SHA256
    assert withdrawal.digest(declared['function'][:55])==withdrawal.PRIOR_STATE_RATIO_CALLER_FUNCTION_SHA256
    assert len(registry.FAMILIES)==13 and len(registry.captures())==47
    assert 'thirteen families and forty-seven capture bindings' in words
    assert proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)==23 and 'preceding twenty-three adapters' in words
    mappings=(withdrawal.PRIOR_FILES_SHA256,withdrawal.PRIOR_PRODUCT_FILES_SHA256,withdrawal.PRIOR_GATED_FILES_SHA256,
        withdrawal.PRIOR_RPM_RAM_FILES_SHA256,withdrawal.PRIOR_OVERFLOW_FILES_SHA256,withdrawal.PRIOR_WORD_FILES_SHA256,
        withdrawal.PRIOR_RPM_STATE_FILES_SHA256,withdrawal.PRIOR_INDEXED_WORD_FILES_SHA256,
        withdrawal.PRIOR_DIVISION_CALLER_FILES_SHA256,withdrawal.PRIOR_BYTE_CURVE_CALLER_FILES_SHA256,
        withdrawal.PRIOR_WORD_INTERP_CALLER_FILES_SHA256,withdrawal.PRIOR_SCALED_DIVISION_FILES_SHA256,
        withdrawal.PRIOR_CURVE_SCALE_CALLER_FILES_SHA256,withdrawal.PRIOR_DERIVATIVE_SCALE_CALLER_FILES_SHA256,
        withdrawal.PRIOR_GUARDED_QUOTIENT_CALLER_FILES_SHA256,withdrawal.PRIOR_MIXED_CURVE_CALLER_FILES_SHA256,
        withdrawal.PRIOR_TIMING_REMAINDER_CALLER_FILES_SHA256,withdrawal.PRIOR_STATE_RATIO_CALLER_FILES_SHA256)
    files={name:sha for mapping in mappings for name,sha in mapping.items()}
    assert len(files)==162 and '162 prior domain sources' in words and '161 byte-identical sources' in words
    for name,sha in files.items():assert hashlib.sha256(withdrawal.prior_gated_source_bytes(repo.ROOT,name)).hexdigest()==sha



def reader1939_row():
    row,=[row for row in withdrawal.descriptor(repo.ROOT)['reference'] if row['id']==transfers.READER1939_IDENTITY[0]]
    return row


def write1939(site=0x50574,raw=2):
    return dict(site=site,mode='write',address=matrix.RAM_BASE+0x1939,width_bytes=1,
        register=6 if site==0x50574 else 2,domain='ram',bytes=f'{raw:02x}')


@pytest.mark.parametrize('site,raw',((0x50574,0),(0x50574,1),(0x50574,2),(0x50594,10)))
def test_reader_direction_retains_each_exact_real_class_writer(site,raw):
    assert transfers.require1939_reader_with_retained_writes(dict(accesses=[write1939(site,raw)]),reader1939_row())==((site,raw),)
    assert transfers.require1939_reader_with_retained_writes(dict(accesses=[]),reader1939_row())==()


@pytest.mark.parametrize('address,width',((0xFFFF1939,1),(matrix.RAM_BASE+0x1939,1),
    (0xFFFF1938,2),(matrix.RAM_BASE+0x1938,2),(0xFFFF1938,4),(matrix.RAM_BASE+0x1938,4)))
def test_reader_direction_refuses_native_alias_and_overlapping_container_reads(address,width):
    event=write1939();event.update(mode='read',address=address,width_bytes=width)
    with pytest.raises(ValueError):transfers.require1939_reader_with_retained_writes(dict(accesses=[event]),reader1939_row())


@pytest.mark.parametrize('fault',('site','address','width_bytes','register','domain','bytes','forced-ten','duplicate','identity'))
def test_reader_direction_cannot_admit_a_missing_or_substituted_actual_writer(fault):
    event=write1939();row=reader1939_row();events=[event]
    if fault=='forced-ten':events=[write1939(0x50594,2)]
    elif fault=='duplicate':events.append(dict(event))
    elif fault=='identity':row=dict(row,original_claim_sha256='0'*64)
    elif fault=='site':event['site']=0x50576
    elif fault=='address':event['address']=0xFFFF1939
    elif fault=='width_bytes':event['width_bytes']=2
    elif fault=='register':event['register']=2
    elif fault=='domain':event['domain']='frame'
    else:event['bytes']='80'
    with pytest.raises(ValueError):transfers.require1939_reader_with_retained_writes(dict(accesses=events),row)



def test_directional_prior_domains_and_published_preservation_bind_current_sources():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    rows=[r for r in matrix.cases(source,image) if r['kind']=='unread1939-prior-and-retained-writes']
    groups={}
    for row in rows:groups.setdefault((row['byte_2468'],row['byte_11b3']),set()).add(row['byte_1939'])
    assert len(groups)==3 and all(values==set(range(256)) for values in groups.values())
    text=(repo.ROOT/'defs/JK08A.dfco-state-caller-withdrawal-paths.md').read_text()
    assert 'all 256 prior byte values' in text and 'prior 123 reference records and 66 function records' in text
    assert len(transfers.NATIVE_ROOTS)==7
    assert withdrawal.digest(withdrawal.descriptor(repo.ROOT)['reference'][:123])==withdrawal.PRIOR_READER_DIRECTION_REFERENCE_SHA256


def test_restore_source_closure_retains_complete_owned_pool_inventory_and_existing_profile():
    unit=contract.RESTORE_SOURCE_UNIT
    image=repo.images()['JK08A'].path.read_bytes()
    assert hashlib.sha256(image).hexdigest()==contract.IMAGE_SHA256
    used=set()
    for span in unit['code']:
        for pc in range(span['start'],span['end'],2):
            word=int.from_bytes(image[pc:pc+2],'big')
            if word>>12 in (9,13):
                width=4 if word>>12==13 else 2
                address=((pc&~3) if width==4 else pc)+4+(word&255)*width
                used.add((address,width))
    assert used=={(row['address'],row['size']) for row in unit['pools']}
    for row in unit['pools']:
        first,last=row['address'],row['address']+row['size']
        assert image[first:last].hex()==row['stock_hex']
        assert not any(first<span['end'] and span['start']<last for span in (*contract.UNIT['code'],*unit['code']))
    assert unit['assembly']==contract.UNIT['assembly']
    for row in unit['aliases']:
        assert row['width']==4 and row['original']>=0xFFFF0000
        assert row['alias']==0x01000000+(row['original']&65535)
        assert image[row['address']:row['address']+4]==row['original'].to_bytes(4,'big')
    assert contract.STATE_ENTRIES==(0x503E0,)
    assert contract.ENTRIES==(*contract.STATE_ENTRIES,contract.RESTORE_SOURCE_ENTRY)


def test_restore_source_publication_counts_follow_the_exact_source_unit():
    text=(repo.ROOT/'defs/JK08A.dfco-state-caller-withdrawal-paths.md').read_text()
    unit=contract.RESTORE_SOURCE_UNIT
    for phrase,actual,wanted in (
            ('485 restore source instructions',sum((row['end']-row['start'])//2 for row in unit['code']),485),
            ('970 restore code bytes',sum(row['end']-row['start'] for row in unit['code']),970),
            ('7 restore code spans',len(unit['code']),7),
            ('17 restore RAM pointer aliases',len(unit['aliases']),17)):
        assert phrase in text and actual==wanted
    assert contract.RESTORE_SOURCE_CALLS==((0x50042,0x25C36),(0x5005E,0x25C36),(0x500AC,0x26388),(0x500BC,0x26388))
    assert contract.RESTORE_SOURCE_PUBLICATIONS==((0x501AA,0xFFFF1778,1,4),(0x501AE,0xFFFF16AA,1,14))



def test_shared_restore_input_fields_preserve_the_complete_state_prefix_and_physical_bytes():
    declared=contract.descriptor(repo.ROOT)
    adapter=declared['adapter']
    assert {row['name']:row['bits'] for row in adapter['fields']}==matrix.WIDTHS
    assert [row['name'] for row in adapter['fields'][:len(matrix.STATE_WIDTHS)]]==[
        *matrix.REGISTERS,*(name for name,at,width in matrix.STATE_RAM_FIELDS),
        *(row['field'] for row in contract.STATE_CONFIGURATION),'variant','initial_sr']
    assert list(matrix.WIDTHS)[:len(matrix.STATE_WIDTHS)]==list(matrix.STATE_WIDTHS)
    assert {row['offset'] for row in adapter['memory']}=={at for name,at,width in matrix.RAM_FIELDS}
    added=[row for row in matrix.RAM_FIELDS if row not in matrix.STATE_RAM_FIELDS]
    assert all(matrix.DEFAULTS[name]==0xA5 for name,at,width in added)
    old_memory=bytearray([0xA5])*65536
    for name,at,width in matrix.STATE_RAM_FIELDS:old_memory[at:at+width]=matrix.STATE_DEFAULTS[name].to_bytes(width,'big')
    case=dict(matrix.DEFAULTS,entry=0x503E0,kind='controlled',index=0)
    assert matrix.memory(case)==bytes(old_memory)
    assert matrix.RESTORE_CURVE_FIELDS[0x12818][-1]=='restore_byte_12827'
    assert matrix.RESTORE_CURVE_FIELDS[0x1298C][-1]=='restore_byte_1299b'
    assert len(matrix.RESTORE_SPEED_FIELDS)==len(matrix.RESTORE_FLOOR_FIELDS)==4


def test_restore_prior_byte_and_coordinate_domains_hold_every_other_raw_input():
    image=repo.images()['JK08A'].path.read_bytes();source=contract.descriptor(repo.ROOT)
    rows=matrix.restore_cases(source,image)
    selected=[row for row in rows if row['kind']=='restore-unread16aa-prior-and-retained-writer']
    groups={}
    for row in selected:
        matrix.require_case(row)
        key=tuple((name,row[name]) for name in matrix.WIDTHS if name!='byte_16aa')
        groups.setdefault(key,[]).append(row['byte_16aa'])
    assert len(groups)==4 and all(values==list(range(256)) for values in groups.values())
    coordinate=[row for row in rows if row['kind']=='restore-complete-coordinate-and-curve-direction']
    assert len(coordinate)==3*256
    for first in range(0,len(coordinate),256):
        group=coordinate[first:first+256]
        assert [row['byte_106f'] for row in group]==list(range(256))
        assert all({key:value for key,value in row.items() if key not in ('index','byte_106f')}==
                   {key:value for key,value in group[0].items() if key not in ('index','byte_106f')} for row in group)


def test_shared_restore_input_counts_bind_the_current_descriptor_sources():
    source=contract.descriptor(repo.ROOT)
    words=' '.join((repo.ROOT/'defs/JK08A.dfco-state-caller-withdrawal-paths.md').read_text().split())
    for phrase,actual,wanted in (
            ('894 shared stock instructions',sum((last-first)//2 for first,last in contract.SPANS),894),
            ('81 shared literal spans',len(contract.UNIT['pools']),81),
            ('30 shared RAM pointer aliases',len(contract.UNIT['aliases']),30),
            ('39 shared RAM fields',len(matrix.RAM_FIELDS),39),
            ('322 shared configuration fields',len(contract.CONFIGURATION),322),
            ('98 shared calibration spans',len(contract.CONTROLLED_CALIBRATION),98),
            ('371 shared raw input fields',len(source['adapter']['fields']),371)):
        assert phrase in words and actual==wanted


@pytest.mark.parametrize('field,value',(('byte_16aa',256),('byte_5a95',True),('restore_byte_12827',256),
    ('restore_byte_1299b',-1),('restore_byte_11cb8',256),('restore_byte_1299f',False)))
def test_restore_physical_input_widths_refuse_partial_or_untyped_bytes(field,value):
    case=dict(matrix.RESTORE_DEFAULTS,entry=0x50018,kind='controlled',index=0);case[field]=value
    with pytest.raises(ValueError):matrix.require_case(case)


@pytest.mark.parametrize('field,sites',(('byte_5a95',(0x50042,)),('byte_5a98',(0x50042,0x5005E))))
def test_restore_each_diagnostic_fallback_retains_actual_publications_without_table_calls(field,sites):
    value=evaluate(0x50018,**{field:32})
    assert tuple(row['site'] for row in value['calls'])==sites and value['lookups']==[]
    assert (value['ram'][0x1778],value['ram'][0x16AA])==(64,64)
    actual=[row for row in value['events'].values() if row['site'] in (0x501AA,0x501AE)]
    assert [(row['site'],row['address'],row['width_bytes'],row['register'],row['bytes']) for row in actual]==[
        (0x501AA,0x01001778,1,4,'40'),(0x501AE,0x010016AA,1,14,'40')]


@pytest.mark.parametrize('offset,thresholds',((0,(72,88)),(128,(96,112))))
def test_restore_real_lookup_and_offset_paths_keep_two_independent_thresholds(offset,thresholds):
    value=evaluate(0x50018,byte_4250=offset)
    assert [(row['site'],row['target']) for row in value['calls']]==list(contract.RESTORE_SOURCE_CALLS)
    assert tuple(value['ram'][at] for at in (0x1778,0x16AA))==thresholds
    assert [(row['base'],row['index'],row['fraction']) for row in value['lookups']]==[
        (0x1298C,5,0),(0x12818,5,0)]
    assert value['gbr']==0x456789B2 and value['mach']==0x13579BE6 and value['macl']==0x2468ACE7
    assert value['sp']==0x02001000 and value['pr']==0x02100000


def test_restore_actual_delay_store_and_fixed_diagnostic_arguments_keep_complete_post_delay_context():
    value=evaluate(0x50018)
    first,second=value['calls'][:2]
    assert (first['registers'][0],first['registers'][4],first['registers'][7],first['registers'][12])==(
        0x260,0x129,0x0100128C,4)
    assert second['registers'][4]==0x12A
    assert [row['address'] for row in value['events'].values() if row['site']==0x25C48]==[0x01005A95,0x01005A98]
    delay=next(row for row in value['events'].values() if row['site']==0x50044)
    assert (delay['address'],delay['width_bytes'],delay['register'],delay['bytes'])==(0x010014EC,1,12,'04')
    assert all(row['gbr']==0x0100119C and row['return_gbr']==0x0100119C for row in value['calls'])


def test_restore_clipped_offsets_and_speed_floor_keep_actual_byte_width_without_semantic_type_inference():
    clipped=evaluate(0x50018,byte_4250=128,config_84e8=255)
    assert (clipped['ram'][0x1778],clipped['ram'][0x16AA])==(255,255)
    fallback=evaluate(0x50018,byte_4250=128,config_84e8=255,byte_5a95=32)
    assert (fallback['ram'][0x1778],fallback['ram'][0x16AA])==(64,64)
    floor=evaluate(0x50018,restore_byte_1299f=200)
    assert (floor['ram'][0x1778],floor['ram'][0x16AA])==(200,200)


@pytest.mark.parametrize('coordinate', (239,240,255))
def test_restore_real_byte_endpoint_retains_sign_extended_helper_return_before_caller_unsigned_publication(coordinate):
    cells={name:255 for name in matrix.RESTORE_CURVE_FIELDS[0x1298C]}
    cells.update({name:128 for name in matrix.RESTORE_CURVE_FIELDS[0x12818]})
    value=evaluate(0x50018,byte_106f=coordinate,**cells)
    assert (value['ram'][0x1778],value['ram'][0x16AA])==(255,128)
    calls=value['calls'][2:]
    assert [row['return_registers'][0] for row in calls]==([255,128] if coordinate<240 else [0xFFFFFFFF,0xFFFFFF80])
    assert [row['return_site'] for row in calls]==([0x2676A,0x2676A] if coordinate<240 else [0x26396,0x26396])


def test_restore_distinct_class_outputs_and_bypass_keep_local_word_and_flag_publications():
    assert evaluate(0x50018,byte_11b3=200)['output']==0
    one=evaluate(0x50018,byte_2458=0)
    assert one['output']==1 and one['ram'][0x249D]&128
    two_cells={name:120 for name in matrix.RESTORE_CURVE_FIELDS[0x1298C]}
    two_cells.update({name:60 for name in matrix.RESTORE_CURVE_FIELDS[0x12818]})
    assert evaluate(0x50018,byte_110e=0,byte_11b3=80,**two_cells)['output']==2
    assert evaluate(0x50018)['output']==3
    bypass=evaluate(0x50018,byte_2468=64)
    assert bypass['output']==0 and bypass['ram'][0x249D]&128
    assert all(row['site'] not in range(0x501BA,0x5036A,2) for row in bypass['events'].values())


def test_restore_source_feasibility_retains_full_functions_and_only_proved_unreachable_helper_modes():
    words=' '.join((repo.ROOT/'defs/JK08A.dfco-state-caller-withdrawal-paths.md').read_text().split())
    assert len(transfers.RESTORE_EXACT_SITES)==485 and len(transfers.RESTORE_FEASIBLE_SITES)==459
    assert len(transfers.INFEASIBLE_SITES)==26 and len(transfers.FEASIBLE_SITES)==868
    assert transfers.RESTORE_INFEASIBLE_SITES=={0x25C54,*range(0x26A60,0x26A84,2),*range(0x26A9C,0x26AAA,2)}
    for phrase in ('459 feasible restore instructions','26 fixed-mode helper instructions','868 feasible shared instructions'):
        assert phrase in words


def test_restore_reader_direction_keeps_every_actual_byte_value_and_requires_the_exact_writer():
    row=dict(zip(('id','original_claim_sha256','address','function'),transfers.READER16AA_IDENTITY))
    for value in range(256):
        event=dict(site=0x501AE,mode='write',address=0x010016AA,width_bytes=1,register=14,domain='ram',bytes=f'{value:02x}')
        assert transfers.require16aa_reader_with_retained_writer(dict(accesses=[event]),row)==((0x501AE,value),)


@pytest.mark.parametrize('form',('native-read','alias-read','overlap-word','overlap-dword','native-write',
    'wrong-site','wrong-register','wrong-width','wrong-domain','missing','duplicate','bool-width','noncanonical-byte'))
def test_restore_reader_direction_refuses_reads_overlapping_containers_and_changed_actual_writer(form):
    row=dict(zip(('id','original_claim_sha256','address','function'),transfers.READER16AA_IDENTITY))
    event=dict(site=0x501AE,mode='write',address=0x010016AA,width_bytes=1,register=14,domain='ram',bytes='80')
    if form=='native-read':event.update(mode='read',address=0xFFFF16AA)
    elif form=='alias-read':event['mode']='read'
    elif form=='overlap-word':event.update(mode='read',address=0x010016A9,width_bytes=2,bytes='0080')
    elif form=='overlap-dword':event.update(mode='read',address=0xFFFF16A8,width_bytes=4,bytes='00008000')
    elif form=='native-write':event['address']=0xFFFF16AA
    elif form=='wrong-site':event['site']+=2
    elif form=='wrong-register':event['register']=4
    elif form=='wrong-width':event['width_bytes']=2
    elif form=='wrong-domain':event['domain']='rom'
    elif form=='bool-width':event['width_bytes']=True
    elif form=='noncanonical-byte':event['bytes']='aF'
    events=[] if form=='missing' else [event,event] if form=='duplicate' else [event]
    with pytest.raises(ValueError):transfers.require16aa_reader_with_retained_writer(dict(accesses=events),row)
