"""Retained RPM originals and separate bounded summary equations."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import repo,rpm_inhibit_contract as contract,rpm_inhibit_matrix as matrix
from kb import rpm_inhibit_semantics as numeric,rpm_inhibit_access_contract as owning

RETAINED_FOUR = {'0004ed88-0000934e-reader': '06b1d9e50500580d019435146dc58d13824574719cddab2a5cf8e8a917387195',
 '0004ed88-ffff2494-reader': '0150d72cc1dc88e37f50f7917005107d3687865e5915da010672d475ff0884aa',
 '0004ed88-ffff2497-reader': '4b938150413dbd5dbdd576f74733e8e93b1a0ef5ab6122fd22454f69dc4d1033',
 '0004ed88-ffff24a6-reader': 'e894c1c5dab812be8fe932644ccc845a630eab883b5fb73162460a0521fee362'}


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()


def test_all_four_original_full_references_remain_exact_in_the_joint_group():
    rows=owning.descriptor(repo.ROOT)['reference']
    assert len(rows)==14 and {row['id']:digest(row) for row in rows[:4]}==RETAINED_FOUR
    assert {row['address'] for row in rows[4:6]}=={0xFFFF2448,0xFFFF418C}
    for row in rows[4:6]:
        before,after=(json.loads(row[key]) for key in ('original_native_json','proposed_native_json'))
        expected=deepcopy(before)
        link=next(link for link in expected['link'] if link['type']=='reader' and link['to']=='fuel_output_inhibit_coordinator/fn')
        link.setdefault('evidence',[]).append(owning.item(row))
        assert after==expected and before['symbol']==after['symbol'] and before['ledger']==after['ledger']
        assert row['declared_width']==row['declared_signed']=='unset'


@pytest.mark.parametrize('flags,rpm,output',((0,192,0),(127,255,0),(128,0,0),(128,191,0),
    (128,192,1),(128,255,1),(255,191,0),(255,192,1)))
def test_independent_MAF_snapshot_and_unsigned_RPM_boundaries(flags,rpm,output):
    case=dict(index=0,kind='maf-summary',entry=matrix.ENTRIES['maf-summary'],**matrix.DEFAULTS)
    case.update(summary_flags=flags,summary_rpm=rpm,prior=0x80000000,prior2=1,prior14=0x40000000)
    before=matrix.memory(case)
    result=numeric.summary(before,case['kind'],case['prior'],case['prior2'],case['prior14'])
    assert result['memory']==before and result['output']==(output,0xC0000000)


@pytest.mark.parametrize('status,output',((0,0),(1,0),(2,1),(3,1),(128,0),(253,0),(254,1),(255,1)))
def test_independent_shared_bit_and_R2_delay_keep_the_full_incoming_words(status,output):
    case=dict(index=0,kind='shared-status',entry=matrix.ENTRIES['shared-status'],**matrix.DEFAULTS)
    case.update(shared_status=status,prior=0x80000000,prior2=1,prior14=0x40000000)
    before=matrix.memory(case)
    result=numeric.summary(before,case['kind'],case['prior'],case['prior2'],case['prior14'])
    assert result['memory']==before and result['output']==(output,0x40000001)
    assert result['output'][1]!=(case['prior14']|case['prior'])


@pytest.mark.parametrize('kind,field,address',(('maf-summary','summary_flags',0x2448),
    ('shared-status','shared_status',0x418C)))
def test_each_new_positive_input_preserves_every_other_RAM_context_and_calibration(kind,field,address):
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    first=dict(index=0,kind=kind,entry=matrix.ENTRIES[kind],**matrix.DEFAULTS)
    second=dict(first);second[field]=128 if kind=='maf-summary' else 2
    left,right=bytearray(matrix.memory(first)),bytearray(matrix.memory(second))
    assert matrix.context(source,first)==matrix.context(source,second)
    assert matrix.calibrations(source,image,first)==matrix.calibrations(source,image,second)
    assert left[address]!=right[address];left[address]=right[address];assert left==right


def test_contributors_keep_their_original_complete_RAM_and_context_seeding_rules():
    source=contract.descriptor(repo.ROOT)
    first=dict(index=0,kind='contributors',entry=contract.ENTRY,**matrix.DEFAULTS)
    second=dict(first,summary_flags=255,shared_status=255,summary_rpm=0,prior2=0xFFFFFFFF,prior14=0xFFFFFFFF)
    assert matrix.memory(first)==matrix.memory(second) and matrix.context(source,first)==matrix.context(source,second)
    raw=matrix.memory(first)
    assert (raw[0x2448],raw[0x418C],raw[0x11B2])==(0xA5,0xA5,0xA5)


def test_the_shared_status_descriptor_grants_no_stock_reachability():
    assert contract.descriptor(repo.ROOT)['stock_shared_status_reachability'] is False
