"""Existing record-byte membership preserves native types, TEST and prior MAF facts."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import maf_record_contract as contract,maf_record_matrix as matrix
from kb import maf_record_capture_evidence as proof,maf_record_semantics as scalar
from kb import maf_access_contract as owning,maf_access_evidence as owning_proof,repo
from kb.test_stock_capture import tool
from kb import byte_surface_equations as state

RETAINED_REFERENCES={'bank-publication-imposing-auk-reader': '9d30fdab9d94e580eaebcb503652c62931698cc880b71617c7be62bd1be7137d',
 'caller-0003a904-ffff101c-reader': 'b8249ba4d33d69bade2175489afbf8fd5a160d5527a92a0efdf7531f4109379c',
 'caller-0003a904-ffff101e-reader': '18637528f14c1209c583b57c9486802a94625c86e06a57bcdf7afdcbdb775127',
 'caller-0003c3ac-ffff101c-writer': 'e9fbd890a6b261c5011607901c7e1ddf5de880b2a4fdb13f8ee02e8f37aec12f',
 'caller-0003c3ac-ffff101e-writer': 'a5df1f45497ea4ee1f1f3842f95187af9bba1dc0d331bec136e9542e97fa4a7e',
 'compensation-careful-penguin-writer': 'f2d8f24819b7f7ad798eaf0bd5fb07132603fd44c24a8c8dbb49c97dc10e86ed',
 'compensation-maf_b2-reader': '3427f02ef7da3a7246416b123ccdfbee3d77e90c927941742a159937bff6b064',
 'compensation-unselfish-okapi-reader': '700c7e53d59ce62efb6fec95728ebe6c04d968ac1e29b634a3cefd62fb1a711a',
 'contribution-imposing-auk-writer': '191268659bff7a917970e9f43aea07e829582077528996f5a5d5c43a2cb9261c',
 'contribution-maf_base_b2-writer': 'd09b20aae610b197a74985abc70a78508e0d96bbe95b51403971661c0c23593e',
 'contribution-maf_base_reference_b2-reader': '55d6b081e5fa491c2db591aa12409964da12d42a112ad223e45ea35e7b8e2856',
 'contribution-maf_correction_state_b2-reader': 'cad185533e240bbe68e67bb8ac57f7d4061fec01cb9837fc904f198ecd072f32',
 'contribution-maf_correction_state_b2-writer': '2e6d8a1c017a7f647f3c1941c824c31f5dd224813a07ece78ce3fd93bb19df63',
 'contribution-maf_delta_reference_b2-reader': '2231dbbde5752d1faa1cdec94a2b6d2b84280610e17b0edd358c5050b83cf8ec',
 'contribution-maf_fallback_latch_b2-reader': '0703ac3368fb8577187e7b2342a759c981b9fc4d43d6933e83db0e07b578b87a',
 'contribution-maf_fallback_latch_b2-writer': '654a2a8b734372d072ac400c005d677767f3417275ddbd487611305556a37076',
 'contribution-maf_fallback_reference_b2-reader': 'ec601866ae2d2f21ec1d87f9030d44ee08354a28f40bab5f682cd9c0626e640a',
 'contribution-maf_residual_magnitude_b2-reader': 'b64f50b7c756d9452f0aa35c59bd1c820dbffe96b9548eeae532f6b0d61c6c41',
 'contribution-maf_residual_magnitude_b2-writer': '845369dcb3575453cf01f2e12d08aeaf241eb241f4a8dc26c3abc2754ad2099e',
 'contribution-spiked-dalmatian-reader': 'c60f0e7f4620080c5c7389b3ea18610ed296d4051466fa26f8e37d5f3c2a8ec7',
 'curve-attribution-000141f4-reader': '599b11489311b804aa82a616896887255b17c8f7141f71e2d2c8a138362223b7',
 'curve-attribution-00014274-reader': '5bc447c4135148e441e5c4540c92633ae7f393501cbbc3bcb663045a32689163',
 'diagnostic-copy-camouflaged-cockle-writer': '22a889ef76d64666ecb80d30cd576db5ed8d3b393e0a65c5e3615f1dd070f5b1',
 'diagnostic-copy-hairy-dalmatian-reader': '3fb50e0407d16d21e7ef9e2f1fa4e03f9a2118fc2598a9747d38b46137fa1633',
 'filtered-write': '53e3ea4d9a4571d4b312f0810bbf7189e3fc4da9abc8a53b9cccb4f7896ec935',
 'scaling-hairy-dalmatian-reader': '892a5b75059b03daab63e1b7f8ff468f3fc6c28a8514182433cec4922694bc61',
 'scaling-maf_b2-writer': '1cebdce9320c536bbc1790cd137511459d924a761e4a91c12fb673995654c808',
 'scaling-satisfied-oarfish-reader': '7b39c6ba7c8a28b7d20e3b02274b2564da8eb46b10c9b7bbf1ba53e1210bdc72',
 'source-copy-read': '35b0cb8ab5d9005e2377a3bffeb37c5470b063f734fc44f2d2a6589f72394a25',
 'working-copy-write': '1b3a9e94b0b7de455984944be5ef1d053ce340be4bd94a8ecc9a944cf1e6dea5',
 'working-filter-read': 'eccf6f47d41c6f537de5ba052605e8b61c4e8f41e07098991cb73ec819213331'}


def test_joint_thirty_four_preserves_all_pinned_full_reference_items_and_record_metadata():
    rows=owning.descriptor(repo.ROOT)['reference'];by_id={row['id']:row for row in rows}
    assert len(rows)==34 and len({row['owner'] for row in rows})==21
    for identity,pin in RETAINED_REFERENCES.items():
        data=json.dumps(by_id[identity],sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
        assert hashlib.sha256(data).hexdigest()==pin
    selected=[row for row in rows if owning.record_member(row)]
    assert len(selected)==2 and {row['function'] for row in selected}=={0x25E20,0x3C3AC}
    for row in selected:
        assert (row['address'],row['member_offset'],row['record_size'],row['record_index'],row['width_bytes'])==(0xFFFF5A93,1,3,0x129,1)
        assert row['declared_width']==row['declared_signed']=='unset'
        assert row['sites']==[0x25E32]
        before=json.loads(row['original_native_json']);after=json.loads(row['proposed_native_json'])
        assert {key:value for key,value in before.items() if key!='link'}=={
            key:value for key,value in after.items() if key!='link'}
        assert len(before['symbol'][0]['evidence'])==11 and before['symbol']==after['symbol']
        assert row['original_ledger_json']==row['proposed_ledger_json']
        selected_targets={'diagnostic_record_byte1_bit7_predicate/fn','dual_bank_maf_diagnostic_coordinator/fn'}
        assert [link for link in before['link'] if link['to'] not in selected_targets]==[
            link for link in after['link'] if link['to'] not in selected_targets]
        assert len(before['link'])==len(after['link'])==5
    assert len({row['proposed_native_json'] for row in selected})==1
    assert set(owning_proof.COMPONENTS)=={'maf_copy_filter_paths','maf_extended_paths','maf_transfer_paths','maf_record_paths'}


@pytest.mark.parametrize('field,old,new',(('member_offset','1','0'),('record_size','3','1'),
    ('record_index','297','296'),('declared_width','"unset"','8'),('declared_signed','"unset"','false')))
def test_owning_contract_refuses_a_different_member_index_extent_or_semantic_type(tmp_path,field,old,new):
    path=tmp_path/owning.DESCRIPTOR;path.parent.mkdir(parents=True)
    text=(repo.ROOT/owning.DESCRIPTOR).read_text();start=text.index('id = "record0129-00025e20-member-reader"')
    end=text.find('\n[[reference]]',start)
    if end<0:end=len(text)
    block=text[start:end];changed=block.replace(field+' = '+old,field+' = '+new,1)
    assert changed!=block;path.write_text(text[:start]+changed+text[end:])
    with pytest.raises(ValueError):owning.descriptor(tmp_path)


def test_only_the_exact_base_literal_and_outside_return_change_in_the_fixture():
    image=repo.images()['JK08A'].path.read_bytes();source=contract.descriptor(repo.ROOT)
    fixture,aliases=contract.independent_fixture(source,image)
    assert aliases==[dict(address=0x25F10,original=0xFFFF5718,alias=0x01005718)]
    restored=bytearray(fixture);restored[0x25F10:0x25F14]=bytes.fromhex('ffff5718')
    restored[0x3C3DA:0x3C3E2]=image[0x3C3DA:0x3C3E2]
    assert bytes(restored)==image
    for row in contract.WINDOWS:assert fixture[row['start']:row['end']]==image[row['start']:row['end']]
    assert sum(row['size'] for row in contract.POOLS)==10
    assert fixture[0x3C3DA:0x3C3E2]==bytes.fromhex('57f6472a000b0009')


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_descriptor_refuses_producer_RPM_full_caller_geometry_or_hardware_admission(tmp_path,flag):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    path.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('argument,flags,status,caller,register,output,t',(
    (0x129,0,0x36,False,0,0x36,1),(0x129,0x7F,0x36,False,0,0x36,1),
    (0x129,0x80,0x36,False,1,0x36,0),(0xA5C30129,0xFF,0x36,False,1,0x36,0),
    (0xFFFFFFFF,0xFF,0x36,False,0,0x36,1),(0x129,0,0xFF,True,0,0x7F,1),
    (0x129,0x80,0,True,0,0x80,0),(0x129,0x80,0x7F,True,0,0xFF,0),
    (0x129,0x7F,0x80,True,0,0,1),(0x129,0xFF,0xA5,True,0,0xA5,0)))
def test_record_bit_and_summary_mask_have_independent_literal_boundaries(argument,flags,status,caller,register,output,t):
    value=scalar.scalar(argument,flags,status,caller)
    assert (value['register'],value['status'],value['exit_t'])==(register,output,t)


@pytest.mark.parametrize('argument,flags,status,caller',((0x128,0,0,False),(0xA5C30129,0,0,True),
    (0xFFFFFFFF,0,0,True),(True,0,0,False),(0x129,256,0,False),(0x129,0,-1,False)))
def test_scalar_refuses_an_unselected_index_or_input_width(argument,flags,status,caller):
    with pytest.raises(ValueError):scalar.scalar(argument,flags,status,caller)


@pytest.mark.parametrize('entry',(0x25E20,0x3C3C6))
def test_byte1_alternatives_hold_sibling_bytes_all_other_RAM_and_complete_context_fixed(entry):
    source=contract.descriptor(repo.ROOT)
    first=dict(index=0,entry=entry,argument=0x129,flags=0,status=0x36,variant=0,sr=0)
    second=dict(first,flags=0x80)
    assert matrix.context(source,first)==matrix.context(source,second)
    a,b=bytearray(matrix.memory(first)),bytearray(matrix.memory(second))
    assert a[0x5A93:0x5A96]==bytes.fromhex('3600a7') and b[0x5A93:0x5A96]==bytes.fromhex('3680a7')
    a[0x5A94]=b[0x5A94];assert a==b


def test_private_record_header_matches_existing_complete_observer_without_expected_outputs():
    image=repo.images()['JK08A'].path.read_bytes();source=contract.descriptor(repo.ROOT)
    declared=dict(source=source,cases=list(matrix.cases(source,image)))
    producer=tool(repo.ROOT,'maf_record_capture.py','_kb_maf_record_test_producer')
    assert producer.header(declared,image)==proof.header(declared,image)


@pytest.mark.parametrize('word,incoming,output',((0xCD7F,0xFF,0x7F),(0xCD7F,0x80,0),(0xCD7F,0x36,0x36),
    (0xCF80,0,0x80),(0xCF80,0x36,0xB6),(0xCF80,0xFF,0xFF)))
@pytest.mark.parametrize('offset',(0,3,255,0xFFFFFFFF))
@pytest.mark.parametrize('sr',(0,1,0x301))
def test_GBR_R0_byte_AND_OR_read_modify_write_preserves_registers_SR_and_frame(word,incoming,output,offset,sr):
    entry,sp,continuation,gbr=0x200,0x02000100,0x123456,0x01002400
    context=tuple([offset,*[0x17283900+index for index in range(1,15)],gbr,0x13579BDF,0x2468ACE0,sr,0xB6C70000])
    frame=bytes([0xA5])*192;memory=bytearray([0xA5])*65536;at=((gbr+offset)&0xFFFFFFFF)-0x01000000
    memory[at]=incoming;fixture=bytearray(1024)
    fixture[entry:entry+6]=word.to_bytes(2,'big')+bytes.fromhex('000b0009')
    result=state.execute(dict(id='jk08a-maf-record-readers',entry=[dict(start=entry,end=entry+6)]),
        bytes(fixture),context,bytes(memory),frame,sp,continuation,entry,sr)
    expected=bytearray(memory);expected[at]=output
    assert result['ram']==bytes(expected) and result['frame']==frame and result['registers']==context[:15]
    assert (result['pr'],result['sp'],result['sr'],result['gbr'],result['mach'],result['macl'])==(
        continuation,sp,sr,gbr,context[16],context[17])
    assert [(row['mode'],row['address'],row['width_bytes'],row['bytes']) for row in result['accesses']]==[
        ('read',0x01000000+at,1,bytes([incoming]).hex()),('write',0x01000000+at,1,bytes([output]).hex())]
    assert result['calls']==[] and result['code']=={entry:word.to_bytes(2,'big').hex(),entry+2:'000b',entry+4:'0009'}
