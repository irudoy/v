"""Exact caller ownership, native storage and independent coordinate boundaries."""

from copy import deepcopy
import json

import pytest

from kb import byte_surface_equations as state
from kb import closed_loop_coordinate_contract as contract,closed_loop_coordinate_matrix as matrix
from kb import closed_loop_coordinate_semantics as scalar,closed_loop_coordinate_capture_evidence as proof
from kb import closed_loop_coordinate_access_contract as owning,repo
from kb.test_stock_capture import tool


def test_six_original_caller_claims_preserve_complete_owners_unset_types_and_every_other_relation():
    rows=[row for row in owning.descriptor(repo.ROOT)['reference'] if row['component']=='closed_loop_coordinate_paths']
    assert len(rows)==len({row['owner'] for row in rows})==6
    assert {row['function'] for row in rows}=={0x3EDB4}
    assert {row['address'] for row in rows}=={0x8F98,0x9384,0x9386,0x95C6,0x12292,0xFFFF2F8E}
    assert {row['direction'] for row in rows}=={'reader','writer'}
    for row in rows:
        assert row['declared_width']==row['declared_signed']=='unset'
        assert owning.native_type(row,'width') is owning.native_type(row,'signed') is None
        before=json.loads(row['original_native_json']);after=json.loads(row['proposed_native_json'])
        expected=deepcopy(before);old=json.loads(row['original_claim_json'])
        links=[link for link in expected['link'] if (link['type'],link['to'])==(old['type'],old['to'])]
        assert len(links)==1;links[0].setdefault('evidence',[]).append(owning.item(row))
        assert expected==after and before['symbol']==after['symbol']
        assert row['original_ledger_json']==row['proposed_ledger_json']
        assert len(before.get('link',[]))==len(after.get('link',[]))
    assert not {'closed_loop_speed_gate/ram','placid-jackrabbit/ram'}&{row['owner'] for row in rows}


def test_existing_assembly_changes_only_four_pointers_and_outside_return_and_preserves_native_GBR_word():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image);restored=bytearray(fixture)
    assert {row['address'] for row in aliases}=={0x21CD8,0x3F028,0x3F034,0x3F03C}
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    at=contract.BOUNDARY['address'];assert fixture[at:at+8]==bytes.fromhex('57f6472a000b0009')
    restored[at:at+8]=image[at:at+8];assert bytes(restored)==image
    assert fixture[0x3F002:0x3F004]==image[0x3F002:0x3F004]==bytes.fromhex('8560')
    for row in contract.WINDOWS:assert fixture[row['start']:row['end']]==image[row['start']:row['end']]
    assert contract.NATIVE_STORAGE==dict(start=0xFFFF8560,size=20,logical_offset=0x8560,
        observed_start=0xFFFF8500,observed_size=256)


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_descriptor_refuses_geometry_full_conversion_parameter_reader_or_hardware_admission(tmp_path,flag):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    path.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('width,offset,accepted',((1,0,True),(1,19,True),(1,20,False),(1,-1,False),
    (2,0,True),(2,18,True),(2,20,False),(4,0,True),(4,16,True),(4,20,False),(4,-4,False)))
def test_native_engine_allows_only_exact_twenty_bytes_with_unchanged_complete_state(width,offset,accepted):
    entry,sp,continuation=0x200,0x02000100,0x123456
    context=tuple([0x12345678,*range(1,15),0xFFFF8560+offset,0x13579BDF,0x2468ACE0,0x301,0xB6C70000])
    fixture=bytearray(1024);word={1:0xC000,2:0xC100,4:0xC200}[width]
    fixture[entry:entry+6]=word.to_bytes(2,'big')+bytes.fromhex('000b0009')
    source=dict(id='jk08a-closed-loop-coordinate',native_storage=dict(contract.NATIVE_STORAGE),
        entry=[dict(start=entry,end=entry+6)])
    memory=bytes([0xA5])*65536;frame=bytes([0x3C])*192
    if not accepted:
        with pytest.raises(ValueError):state.execute(source,bytes(fixture),context,memory,frame,sp,continuation,entry,0x301)
        return
    result=state.execute(source,bytes(fixture),context,memory,frame,sp,continuation,entry,0x301)
    expected=bytearray(memory);raw=(context[0]&((1<<(width*8))-1)).to_bytes(width,'big')
    expected[0x8560+offset:0x8560+offset+width]=raw
    assert result['ram']==bytes(expected) and result['frame']==frame and result['registers']==context[:15]
    assert (result['gbr'],result['mach'],result['macl'],result['sr'],result['sp'],result['pr'])==(
        context[15],context[16],context[17],0x301,sp,continuation)
    assert [(row['domain'],row['mode'],row['address'],row['width_bytes'],row['bytes']) for row in result['accesses']]==[
        ('coordinate-workspace','write',0xFFFF8560+offset,width,raw.hex())]


@pytest.mark.parametrize('fault',('id','start','size','logical_offset','observed_start','observed_size','frame'))
def test_native_window_requires_exact_descriptor_and_frame_disjointness(fault):
    entry,sp,continuation=0x200,0x02000100,0x123456
    source=dict(id='jk08a-closed-loop-coordinate',native_storage=dict(contract.NATIVE_STORAGE),
        entry=[dict(start=entry,end=entry+6)])
    if fault=='id':source['id']='unregistered-native-window'
    elif fault=='frame':sp=0xFFFF8570
    else:source['native_storage'][fault]+=1
    context=tuple([1,*range(1,15),0xFFFF8560,0,0,0,0])
    fixture=bytearray(1024);fixture[entry:entry+6]=bytes.fromhex('c000000b0009')
    with pytest.raises(ValueError):state.execute(source,bytes(fixture),context,bytes(65536),bytes(192),sp,continuation,entry,0)


@pytest.mark.parametrize('coefficient,x1,x2,h,output,register',(
    (64,1000,2000,880,(1120,3120),3120),(128,1000,2000,880,(1000,2000),2000),
    (0,1000,2000,880,(1000,2000),2000),(136,65534,0,880,(31719,52),52),
    (1,65535,0,880,(33647,0),0),(1,65535,40000,40000,(7231,40000),40000),
    (64,0,0xA5C3FFFF,880,(0,33647),33647)))
def test_separate_scalar_retains_first_saturation_zero_coefficient_wrap_and_full_R0(coefficient,x1,x2,h,output,register):
    case=dict(matrix.DEFAULTS,x1=x1,x2=x2,midpoint=h)
    calibration={0x11B47:bytes(range(0,256,17))+b'\0',0x12292:bytes([coefficient])*16+b'\0'}
    value=scalar.scalar(case,calibration)
    assert value['output']==output and value['register']==register
    assert value['admitted'] is (coefficient>0)


@pytest.mark.parametrize('left,right,expected',((64,192,124),(192,64,132)))
def test_byte_curve_has_separate_directional_rounding_and_actual_fraction(left,right,expected):
    calibration={0x11B47:bytes(range(0,256,17))+b'\0',
        0x12292:bytes([left,right,*([128]*14),0])}
    value=scalar.curve(calibration,8<<8)
    assert (value['index'],value['fraction'],value['coefficient'])==(0,30840,expected)


def test_legacy_reader_consumes_only_sixteen_input_columns(tmp_path):
    path=tmp_path/matrix.INPUT_SOURCE;path.parent.mkdir(parents=True)
    prefix=','.join(f'{value}U' for value in range(16))+','
    path.write_text('static const struct sample samples[]={\n'+
        ''.join('    {'+prefix+'different_expected_result,{not_an_input}},\n' for _ in range(4338))+'};\n')
    assert matrix.legacy_inputs(tmp_path)==(tuple(range(16)),)*4338


def test_private_coordinate_header_matches_the_existing_complete_observer_without_expected_outputs():
    image=repo.images()['JK08A'].path.read_bytes();source=contract.descriptor(repo.ROOT)
    declared=dict(source=source,cases=list(matrix.cases(source,image,root=repo.ROOT)))
    producer=tool(repo.ROOT,'closed_loop_coordinate_capture.py','_kb_closed_loop_coordinate_test_producer')
    assert producer.header(declared,image)==proof.header(declared,image)


def test_current_document_pins_native_bounds_input_columns_and_exact_owning_count():
    text=(repo.ROOT/'defs/JK08A.closed-loop-coordinate-accesses.md').read_text()
    assert 'contains six exact\noriginal caller-owned relations in six complete owner documents' in text
    rows=[row for row in owning.descriptor(repo.ROOT)['reference'] if row['component']=='closed_loop_coordinate_paths']
    assert len(rows)==len({row['owner'] for row in rows})==6
    assert 'Five real helpers execute' in text and len(contract.FUNCTIONS)-2==5
    assert 'exactly20 bytes atFFFF8560..FFFF8574' in text and contract.NATIVE_STORAGE['size']==20
    assert 'captures all256 bytes atFFFF8500' in text and contract.NATIVE_STORAGE['observed_size']==256
    assert 'first16 input\ncolumns of the existing4338 literal rows' in text
    assert len(matrix.legacy_inputs(repo.ROOT))==4338
    assert 'Four existing 32-bit pointer aliases' in text and len(contract.ALIASES)==4
    assert 'Source preparation does not qualify' in text
