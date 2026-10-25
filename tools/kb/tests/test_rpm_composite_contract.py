"""Retained exact RPM references and independent bounded composite equations."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import repo,rpm_inhibit_contract as contract,rpm_inhibit_matrix as matrix
from kb import rpm_inhibit_semantics as numeric,rpm_inhibit_access_contract as owning
from kb import rpm_inhibit_capture_evidence as proof

RETAINED_SIX = {'0004ed88-0000934e-reader': '06b1d9e50500580d019435146dc58d13824574719cddab2a5cf8e8a917387195',
 '0004ed88-ffff2494-reader': '0150d72cc1dc88e37f50f7917005107d3687865e5915da010672d475ff0884aa',
 '0004ed88-ffff2497-reader': '4b938150413dbd5dbdd576f74733e8e93b1a0ef5ab6122fd22454f69dc4d1033',
 '0004ed88-ffff24a6-reader': 'e894c1c5dab812be8fe932644ccc845a630eab883b5fb73162460a0521fee362',
 '0004ed88-ffff2448-reader': '15667a47cca8df1baf85b86eb0f882127406322f284d1902406292c73598c9d5',
 '0004ed88-ffff418c-reader': '34a50baac00ccdcb6fbfa443e96a466c7f40b6d4d846465db3d795febc025fa7'}


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()


def test_six_complete_original_reference_records_remain_exact_in_joint_fourteen():
    rows=owning.descriptor(repo.ROOT)['reference']
    assert len(rows)==14 and {row['id']:digest(row) for row in rows[:6]}==RETAINED_SIX
    assert {row['address'] for row in rows[6:9]}=={0xFFFF2489,0xFFFF249F,0xFFFF41EA}
    for row in rows[6:9]:
        before,after=(json.loads(row[key]) for key in ('original_native_json','proposed_native_json'))
        expected=deepcopy(before)
        link=next(link for link in expected['link'] if link['type']=='reader' and link['to']=='fuel_output_inhibit_coordinator/fn')
        link.setdefault('evidence',[]).append(owning.item(row))
        assert after==expected and before['symbol']==after['symbol'] and before['ledger']==after['ledger']
        assert row['declared_width']==row['declared_signed']=='unset'


def inputs(**changes):
    case=dict(index=0,kind='composite-status',entry=matrix.ENTRIES['composite-status'],**matrix.DEFAULTS)
    case.update(changes)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    return case,matrix.memory(case),matrix.calibrations(source,image,case)


@pytest.mark.parametrize('flags,rpm,active',((0,71,False),(0,72,True),(1,63,False),
    (1,64,True),(1,68,True),(255,255,True),(254,64,False)))
def test_low_latch_uses_unsigned_byte_plus_nonwrapping_eight_and_preserves_other_bits(flags,rpm,active):
    case,before,calibration=inputs(low_flags=flags,low_rpm=rpm,low_gate1=64,low_gate2=32)
    result=numeric.composite(before,calibration,0x80000000,1,0x40000000)
    assert result['low_coordinate']==rpm+(8 if flags&1 else 0)
    assert result['low_active'] is active
    assert result['memory'][0x2489]==(flags&254)|int(active)
    assert result['output']==(int(active),0x40000001)


@pytest.mark.parametrize('flags,rpm,hysteresis,active',((0,509,16,False),(0,510,16,True),
    (4,493,16,False),(4,494,16,True),(4,500,16,True),(255,65535,65535,True),(251,0,65535,False)))
def test_high_latch_uses_unsigned_word_and_nonwrapping_hysteresis_without_other_bit_changes(flags,rpm,hysteresis,active):
    _,before,calibration=inputs(high_flags=flags,rpm=rpm,hysteresis=hysteresis,high_gate1=4)
    result=numeric.composite(before,calibration,0,0,0)
    assert result['threshold']==510 and result['high_coordinate']==rpm+(hysteresis if flags&4 else 0)
    assert result['high_active'] is active
    assert result['memory'][0x249F]==(flags&251)|(4 if active else 0)
    assert result['output']==(int(active),0)


@pytest.mark.parametrize('table,speed,value',(((0,32,64,96,128,160,192,255),0,0),
    ((0,32,64,96,128,160,192,255),9,36),((255,192,160,128,96,64,32,0),9,188),
    ((128,)*8,9,128),((0,32,64,96,128,160,192,255),56,255),
    ((0,32,64,96,128,160,192,255),63,255),((0,32,64,96,128,160,192,255),255,255)))
def test_real_eight_byte_curve_coordinate_cap_fraction_and_word_threshold(table,speed,value):
    _,before,calibration=inputs(speed=speed,**{'c'+str(i):v for i,v in enumerate(table)})
    result=numeric.composite(before,calibration,0,0,0)
    assert result['coordinate']==4*min(speed,63) and result['curve']['value']==value
    assert result['threshold']==2*value
    assert result['memory'][0x17CA:0x17CC]==(2*value).to_bytes(2,'big')


@pytest.mark.parametrize('field,first,second,setup',(
    ('low_flags',0,1,dict(low_rpm=68,low_gate1=64,low_gate2=32)),
    ('high_flags',0,4,dict(rpm=500,high_gate1=4)),('seed_flags',0,128,{})))
def test_each_new_reader_has_a_fixed_other_positive_output_pair(field,first,second,setup):
    source=contract.descriptor(repo.ROOT);left,before,calibration=inputs(**setup,**{field:first})
    right,after,other=inputs(**setup,**{field:second})
    offset={'low_flags':0x2489,'high_flags':0x249F,'seed_flags':0x41EA}[field]
    stripped=bytearray(before);stripped[offset]=after[offset]
    assert bytes(stripped)==after and calibration==other and matrix.context(source,left)==matrix.context(source,right)
    assert numeric.composite(before,calibration,0,0,0)['output']==(0,0)
    assert numeric.composite(after,other,0,0,0)['output']==(1,0)


@pytest.mark.parametrize('bits',range(16))
@pytest.mark.parametrize('active',(False,True))
def test_status_gates_require_the_actual_latch_and_exact_low_AND_high_OR(bits,active):
    _,before,calibration=inputs(low_rpm=72 if active else 0,rpm=510 if active else 0,
        low_gate1=64 if bits&1 else 0,low_gate2=32 if bits&2 else 0,
        high_gate1=4 if bits&4 else 0,high_gate2=1 if bits&8 else 0)
    result=numeric.composite(before,calibration,0,0,0)
    assert result['output']==(int(active and (bits&3==3 or bits&12!=0)),0)
    restored=bytearray(result['memory'])
    for at,size in ((0x2489,1),(0x249F,1),(0x17CA,2)):restored[at:at+size]=before[at:at+size]
    assert bytes(restored)==before


@pytest.mark.parametrize('kind',('contributors','maf-summary','shared-status'))
def test_new_composite_inputs_preserve_the_previous_three_kinds_RAM_context_and_calibration(kind):
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    first=dict(index=0,kind=kind,entry=matrix.ENTRIES[kind],**matrix.DEFAULTS)
    second=dict(first,low_flags=255,high_flags=255,seed_flags=255,low_rpm=255,
        low_gate1=255,low_gate2=255,high_gate1=255,high_gate2=255,hysteresis=65535,
        **{'c'+str(index):index for index in range(8)})
    assert matrix.memory(first)==matrix.memory(second) and matrix.context(source,first)==matrix.context(source,second)
    assert matrix.calibrations(source,image,first)==matrix.calibrations(source,image,second)


def test_exact_composite_closure_preserves_stock_seed_and_word_entry_reachability_boundaries():
    source=contract.descriptor(repo.ROOT)
    assert source['stock_composite_seed_reachability'] is False
    assert proof.FIXED_BRANCHES=={0x259EA:'taken',0x507F6:'fallthrough',0x50800:'taken',0x26A9A:'taken'}
    assert proof.UNREACHABLE_BRANCHES==(0x5080E,0x5081E,0x50838,0x259FA,0x25A06)
    curve=source['unit'][-1]
    assert curve['assembly']=='tools/sh-elf-run/stock_jk08a_implicit_byte_curve.s'
    assert [(row['start'],row['end']) for row in curve['code']]==[(0x26370,0x26382),(0x26740,0x2676E),(0x26A80,0x26ABA)]


def test_shared_RPM_document_counts_read_the_current_executed_contract():
    count=len(owning.descriptor(repo.ROOT)['reference'])
    assert count==14 and len(proof.REQUIRED_BRANCHES)==33 and len(proof.FIXED_BRANCHES)==4
    snippets={
        'tools/kb/README.md':('The bounded RPM-inhibit source','Ordinary access families'),
        'tools/kb/SPEC.md':('Reserved `rpm-inhibit-access` evidence','Reserved `phase-normalization-access` evidence'),
        'tools/sh-elf-run/README.md':('`jk08a-rpm-inhibit-paths` binds','The ordinary access captures')}
    for path,(start,end) in snippets.items():
        text=(repo.ROOT/path).read_text().split(start,1)[1].split(end,1)[0]
        assert 'fourteen exact' in text.lower() or 'fourteen ordinary' in text.lower()
    text=(repo.ROOT/'tools/sh-elf-run/README.md').read_text().split('`jk08a-rpm-inhibit-paths` binds',1)[1].split('The ordinary access captures',1)[0]
    assert 'Fifteen pointer aliases' in text and len(contract.ALIASES)==15
    assert 'four separate outside' in text and len(contract.BOUNDARIES)==4
    assert 'and27 calibration bytes' in text and sum(row['size'] for row in contract.CALIBRATIONS)==27
    assert 'All33 conditional branch sites' in text and 'Four exact\none-sided sites' in text
