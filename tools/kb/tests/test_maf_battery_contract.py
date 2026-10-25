"""Complete natural battery coefficient access preserves every retained MAF proof."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import maf_access_contract as owning,maf_extended_contract as contract
from kb import maf_extended_matrix as matrix,maf_extended_capture_evidence as proof,repo,test_contract
from kb.test_stock_capture import tool

RETAINED_REFERENCES = {'bank-publication-imposing-auk-reader': '9d30fdab9d94e580eaebcb503652c62931698cc880b71617c7be62bd1be7137d',
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
 'record0129-00025e20-member-reader': '68ace336a49804e5a26112876441f27c46927551c35598bc7e31a93d509984f6',
 'record0129-0003c3ac-member-reader': 'b735cc481d18e489c715cf77959b488fea9659b7cf61c81975a97353d4b22392',
 'scaling-hairy-dalmatian-reader': '892a5b75059b03daab63e1b7f8ff468f3fc6c28a8514182433cec4922694bc61',
 'scaling-maf_b2-writer': '1cebdce9320c536bbc1790cd137511459d924a761e4a91c12fb673995654c808',
 'scaling-satisfied-oarfish-reader': 'a95c98e8500a83af1ce7e1a138c20c6684ff0a11feafb1c54961c3a3f946a2c1',
 'source-copy-read': '35b0cb8ab5d9005e2377a3bffeb37c5470b063f734fc44f2d2a6589f72394a25',
 'working-copy-write': '1b3a9e94b0b7de455984944be5ef1d053ce340be4bd94a8ecc9a944cf1e6dea5',
 'working-filter-read': 'eccf6f47d41c6f537de5ba052605e8b61c4e8f41e07098991cb73ec819213331'}


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()


def test_joint_thirty_four_retains_all_thirty_three_full_references_with_only_the_exact_grouped_append():
    rows=owning.descriptor(repo.ROOT)['reference'];by_id={row['id']:row for row in rows}
    assert len(rows)==34 and len({row['owner'] for row in rows})==21
    added=by_id['battery-satisfied-oarfish-reader']
    assert added['original_claim_sha256']=='93cf03a0382ab39a6bfbc1e336c7044eafaf5c8911ed48b5d87b1bf77d0fa907'
    assert added['function']==0x39A9E and added['sites']==[0x6719A,0x671E0]
    assert added['component']=='maf_extended_paths' and added['direction']=='reader'
    assert (added['width_bytes'],added['declared_width'],added['declared_signed'])==(2,16,False)
    for identity,pin in RETAINED_REFERENCES.items():
        value=deepcopy(by_id[identity])
        if identity=='scaling-satisfied-oarfish-reader':
            original=json.loads(value['original_native_json']);after=json.loads(value['proposed_native_json'])
            old=next(link for link in original['link'] if link['type']=='reader' and link['to']=='battery_voltage_publish/fn')
            at=next(index for index,link in enumerate(after['link']) if link['type']=='reader' and link['to']=='battery_voltage_publish/fn')
            expected=deepcopy(old);expected.setdefault('evidence',[]).append(owning.item(added))
            assert test_contract.exact(after['link'][at],expected)
            after['link'][at]=deepcopy(old)
            value['proposed_native_json']=json.dumps(after,sort_keys=True,separators=(',',':'),ensure_ascii=True)
            value['proposed_native_sha256']=digest(after)
        assert digest(value)==pin
    shared=[row for row in rows if row['owner']=='satisfied-oarfish/ram']
    assert len(shared)==2
    assert len({row['original_native_json'] for row in shared})==len({row['proposed_native_json'] for row in shared})==1
    before=json.loads(added['original_native_json']);after=json.loads(added['proposed_native_json'])
    expected=deepcopy(before)
    for row in shared:
        old=json.loads(row['original_claim_json'])
        link=next(link for link in expected['link'] if (link['type'],link['to'])==(old['type'],old['to']))
        link.setdefault('evidence',[]).append(owning.item(row))
    assert expected==after and before['symbol']==after['symbol'] and before.get('ledger')==after.get('ledger')


def test_complete_battery_entry_uses_the_existing_assembly_with_only_three_additional_pointer_aliases():
    declared=contract.descriptor(repo.ROOT)
    unit=next(row for row in declared['unit'] if row['id']=='jk08a-maf-scaling')
    assert dict(start=0x39A9E,end=0x39AEE) in unit['code']
    assert 0x39A9E in contract.ENTRIES and 0x39A9E in contract.FUNCTIONS
    assert unit['assembly']=='tools/sh-elf-run/stock_jk08a_maf_scaling.s'
    assert {row['address']:row['size'] for row in unit['pools'] if row['address'] in (0x39BDC,0x39CAC)}=={0x39BDC:2,0x39CAC:20}
    expected={0x39CAC:0xFFFF1E60,0x39CB0:0xFFFF1D34,0x39CBC:0xFFFF1114}
    assert {row['address']:row['original'] for row in unit['aliases'] if row['address'] in expected}==expected
    image=repo.images()['JK08A'].path.read_bytes();fixture,aliases=contract.independent_fixture(declared,image)
    for at,original in expected.items():
        assert fixture[at:at+4]==(0x01000000+(original&65535)).to_bytes(4,'big')
    assert fixture[0x39A9E:0x39AEE]==image[0x39A9E:0x39AEE]
    assert not any(0x39A9E<=row['address']<0x39AEE for row in contract.BOUNDARIES)


def test_battery_coefficient_alternatives_change_only_that_word_in_complete_inputs():
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    rows=matrix.cases(declared,image)
    selected=list({row['coefficient']:row for row in rows if row['kind']=='battery'
        and row['mode']==8 and row['input']==508}.values())
    assert {row['coefficient'] for row in selected}>={0,0x8000,0xFFFF}
    first=selected[0]
    for other in selected[1:]:
        assert matrix.context(declared,first)==matrix.context(declared,other)
        assert matrix.calibrations(declared,image,first)==matrix.calibrations(declared,image,other)
        left,right=bytearray(matrix.memory(first)),bytearray(matrix.memory(other))
        assert left[0x4970:0x4972]!=right[0x4970:0x4972]
        left[0x4970:0x4972]=right[0x4970:0x4972]
        assert left==right


def test_raw_private_header_retains_the_existing_observer_layout_and_contains_only_inputs():
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    data=dict(source=declared,cases=list(matrix.cases(declared,image)))
    producer=tool(repo.ROOT,'maf_extended_capture.py','_kb_maf_battery_existing_producer')
    assert producer.header(data,image)==proof.header(data,image)
    assert matrix.FIELDS==('entry','argument','input','previous','correction','initialized','multiplier','bias',
        'mode','coefficient','reference','delta','magnitude','positive','enable','diagnostic','inhibit','latch',
        'fallback','weight','variant','sr')


def test_current_document_binds_the_executed_joint_count_natural_entries_and_battery_boundary():
    text=(repo.ROOT/'defs/JK08A.maf-extended.md').read_text()
    rows=owning.descriptor(repo.ROOT)['reference'];source=contract.descriptor(repo.ROOT)
    assert 'contains all 34 exact original claims' in text and len(rows)==34
    assert '22 accesses from six natural entries' in text
    assert sum(row['component']=='maf_extended_paths' for row in rows)==22+len(source['caller'])*2
    assert len(source['unit'])==6 and len(source['natural_entries'])-len(source['caller'])==6
    assert '21 complete owner documents' in text and len({row['owner'] for row in rows})==21
    for value in ('00039A9E','00039AEE','00039ABC','00039ACA','00039ACC','0006719A','000671E0','FFFF4970'):
        assert value in text
    assert 'no added observing return' in text and 'no raw-full-scale increment' in text
