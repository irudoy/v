"""Two positive curve readers preserve exact MAF owners and prior reference items."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import maf_transfer_contract as contract,maf_transfer_matrix as matrix
from kb import maf_transfer_capture_evidence as proof,maf_transfer_semantics as scalar
from kb import maf_access_contract as owning,maf_access_evidence as owning_proof,repo
from kb.test_stock_capture import tool

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
 'diagnostic-copy-camouflaged-cockle-writer': '22a889ef76d64666ecb80d30cd576db5ed8d3b393e0a65c5e3615f1dd070f5b1',
 'diagnostic-copy-hairy-dalmatian-reader': '3fb50e0407d16d21e7ef9e2f1fa4e03f9a2118fc2598a9747d38b46137fa1633',
 'filtered-write': '53e3ea4d9a4571d4b312f0810bbf7189e3fc4da9abc8a53b9cccb4f7896ec935',
 'scaling-hairy-dalmatian-reader': '892a5b75059b03daab63e1b7f8ff468f3fc6c28a8514182433cec4922694bc61',
 'scaling-maf_b2-writer': '1cebdce9320c536bbc1790cd137511459d924a761e4a91c12fb673995654c808',
 'scaling-satisfied-oarfish-reader': '7b39c6ba7c8a28b7d20e3b02274b2564da8eb46b10c9b7bbf1ba53e1210bdc72',
 'source-copy-read': '35b0cb8ab5d9005e2377a3bffeb37c5470b063f734fc44f2d2a6589f72394a25',
 'working-copy-write': '1b3a9e94b0b7de455984944be5ef1d053ce340be4bd94a8ecc9a944cf1e6dea5',
 'working-filter-read': 'eccf6f47d41c6f537de5ba052605e8b61c4e8f41e07098991cb73ec819213331'}


def test_joint_thirty_one_retains_every_previous_full_reference_item_and_six_table_layouts():
    rows=owning.descriptor(repo.ROOT)['reference'];by_id={row['id']:row for row in rows}
    assert len(rows)==34 and len({row['owner'] for row in rows})==21
    for identity,pin in RETAINED_REFERENCES.items():
        assert hashlib.sha256(json.dumps(by_id[identity],sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()==pin
    selected=[row for row in rows if owning.correction(row)]
    assert len(selected)==2
    assert {row['owner'] for row in selected}=={'ivory-gecko/tbl','wealthy-woodlouse/tbl'}
    for row in selected:
        before=json.loads(row['original_native_json']);after=json.loads(row['proposed_native_json'])
        assert row['function']==0x3A904 and row['sites']==[0x26AA0]
        assert row['declared_width']==row['declared_signed']=='unset'
        assert len(before['symbol'])==6 and before['symbol']==after['symbol']
        assert {key:value for key,value in before.items() if key!='link'}=={
            key:value for key,value in after.items() if key!='link'}
        assert json.loads(row['original_claim_json'])['to']=='wondrous-camel/fn'
        assert owning.base_claim(row)['to']=='dual_bank_maf_coordinator/fn'
        assert not any(link['type']=='reader' and link['to']=='wondrous-camel/fn' for link in after['link'])
        assert sum(link['type']=='reader' and link['to']=='dual_bank_maf_coordinator/fn' for link in after['link'])==1
        assert len(after['link'])==len(before['link'])-1
    assert set(owning_proof.COMPONENTS)=={'maf_copy_filter_paths','maf_extended_paths','maf_transfer_paths','maf_record_paths'}


def test_existing_assembly_origin_and_tested_instructions_are_preserved():
    image=repo.images()['JK08A'].path.read_bytes();source=contract.descriptor(repo.ROOT)
    fixture,aliases=contract.independent_fixture(source,image)
    assert aliases==[dict(address=0x3AB68,original=0xFFFF1048,alias=0x01001048)]
    assert (min(row['address'] for row in contract.POOLS)&~3)==0x86F8
    assert sum(row['size'] for row in contract.POOLS)==283
    restored=bytearray(fixture);restored[0x3AB68:0x3AB6C]=bytes.fromhex('ffff1048')
    restored[0x3A94C:0x3A954]=image[0x3A94C:0x3A954]
    assert bytes(restored)==image
    for row in contract.WINDOWS:assert fixture[row['start']:row['end']]==image[row['start']:row['end']]
    assert fixture[0x3A94C:0x3A954]==bytes.fromhex('57f6472a000b0009')


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_descriptor_refuses_full_caller_geometry_correction_or_universal_no_read_inference(tmp_path,flag):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    path.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('coordinate,expected',((0,1000),(128,1050),(255,1099),(256,1100),(0x3E80,7250),(0x3F00,7300),(65535,7300)))
def test_implicit_word_interpolation_and_upper_clamp_have_independent_literal_boundaries(coordinate,expected):
    curve=b''.join((1000+100*index).to_bytes(2,'big') for index in range(64))
    assert scalar.lookup(curve,coordinate)['word']==expected


@pytest.mark.parametrize('coordinate,expected',((0,65535),(1,65535),(0x3F00,0xFFFFFFFF),(65535,0xFFFFFFFF)))
def test_upper_word_load_sign_extension_is_separate_from_stored_word_width(coordinate,expected):
    value=scalar.lookup(bytes.fromhex('ffff')*64,coordinate)
    assert value['word']==65535 and value['register']==expected


@pytest.mark.parametrize('profile,other_profile,offset',((1,2,0),(3,4,128)))
def test_curve_root_alternatives_hold_every_other_byte_and_full_context_fixed(profile,other_profile,offset):
    image=repo.images()['JK08A'].path.read_bytes();source=contract.descriptor(repo.ROOT)
    first=dict(index=0,entry=0x3A922,adc1=0,adc2=0,profile=profile,variant=0,sr=0)
    second=dict(first,profile=other_profile)
    assert matrix.memory(first)==matrix.memory(second) and matrix.context(source,first)==matrix.context(source,second)
    a,b=matrix.calibrations(source,image,first),matrix.calibrations(source,image,second)
    left,right=bytearray(a[0x141F4]),bytearray(b[0x141F4])
    assert left[offset:offset+2]!=right[offset:offset+2];left[offset:offset+2]=right[offset:offset+2]
    a[0x141F4],b[0x141F4]=bytes(left),bytes(right);assert a==b


def test_private_curve_header_is_input_only_and_matches_the_existing_observer_ABI():
    image=repo.images()['JK08A'].path.read_bytes();source=contract.descriptor(repo.ROOT)
    declared=dict(source=source,cases=list(matrix.cases(source,image)))
    producer=tool(repo.ROOT,'maf_transfer_capture.py','_kb_maf_transfer_test_producer')
    assert producer.header(declared,image)==proof.header(declared,image)
