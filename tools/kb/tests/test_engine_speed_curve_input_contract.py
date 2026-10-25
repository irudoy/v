"""Complete caller scope, raw input widths and descriptor-bound published facts."""
from copy import deepcopy
import hashlib
import re
import pytest
from kb import repo
from kb import engine_speed_curve_input_contract as contract,engine_speed_curve_input_matrix as matrix


def case():
    return dict(deepcopy(matrix.DEFAULTS),index=0,kind='controlled-speed-coordinate-entry')


def test_published_counts_read_the_executed_descriptor():
    source=contract.descriptor(repo.ROOT)
    text=(repo.ROOT/'defs/JK08A.engine-speed-curve-input.md').read_text()
    actual=(sum((r['end']-r['start'])//2 for r in source['unit']['code']),len(source['entries']),
        len(source['unit']['code']),len(source['unit']['pools']),len(source['unit']['aliases']),
        len(source['controlled_calibration']))
    match=re.search(r'binds (\d+) stock instructions in (\d+) actual entry path and (\d+) spans,\s*'
        r'(\d+) literal pools, (\d+) four-byte RAM pointer aliases and (\d+) calibration spans',text)
    assert match is not None and tuple(map(int,match.groups()))==actual==(1153,1,18,86,21,108)
    root=sum((r['end']-r['start'])//2 for r in source['unit']['code'] if 0x4AFDC<=r['start']<0x4B55E)
    assert int(re.search(r'entry has (\d+) instructions',text)[1])==root==584
    assert int(re.search(r'(\d+) stock entry paths',text)[1])==len(source['stock_entry_paths'])==13
    assert int(re.search(r'(\d+) raw ROM controls',text)[1])==len(source['control_blobs'])==13
    assert int(re.search(r'containing (\d+) bytes',text)[1])==sum(r['size'] for r in source['control_blobs'])==18
    assert int(re.search(r'(\d+) raw input blobs',text)[1])==len(source['input_blobs'])==9
    assert int(re.search(r'containing (\d+) input bytes',text)[1])==sum(r['size'] for r in source['input_blobs'])==187
    for phrase,key,wanted in (('byte context','context_bytes',80),('byte observer','observation_bytes',572),
                              ('byte frame','frame_bytes',192)):
        assert int(re.search(r'(\d+)-'+phrase,text)[1])==source[key]==wanted
    assert int(re.search(r'(\d+) independent context',text)[1])==source['independent_context_fields']==20
    assert int(re.search(r'All (\d+) RAM bytes',text)[1])==source['complete_initial_final_RAM_bytes']==65536
    assert int(re.search(r'allocates (\d+) stack bytes',text)[1])==source['outer_stack_bytes']==44


def test_published_carrier_surface_and_SR_facts_read_the_descriptor():
    source=contract.descriptor(repo.ROOT)
    text=(repo.ROOT/'defs/JK08A.engine-speed-curve-input.md').read_text()
    rows,columns=map(int,re.search(r'(\d+)x(\d+) byte surface',text).groups())
    inputs={r['name']:r for r in source['input_blobs']}
    assert rows==inputs['surface_outer_axis']['size']==8
    assert columns==inputs['surface_inner_axis']['size']==8
    assert rows*columns==inputs['correction_surface']['size']==64
    carrier=source['complete_inner_argument']
    assert carrier['original_frame_high24_offset']==116 and carrier['root_call_SP_delta']==-44
    assert carrier['read_SP_delta']==-60 and carrier['high24_from_original_frame_required'] is True
    assert source['SR_transfer']['architectural_mask']==int(re.search(r'architectural mask\s*(0x[0-9A-F]+)',text)[1],16)
    assert source['SR_transfer']['admitted_changed_bits']==int(re.search(r'guard(0x[0-9A-F]+)',text)[1],16)
    assert source['wrapper_has_no_physical_read_of_RAM11B2'] is True
    assert [(r['site'],r['delay_slot'],r['target']) for r in source['actual_helper_calls']]==[
        (0x4B058,0x4B05A,0x26370),(0x4B08E,0x4B090,0x26370),(0x4B0B8,0x4B0BA,0x26370)]


def test_fixture_retains_all_stock_instructions_and_only_declared_pointer_aliases():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image)
    assert {i for i,(a,z) in enumerate(zip(image,fixture)) if a!=z}<={
        i for row in aliases for i in range(row['address'],row['address']+4)}
    for row in source['unit']['code']:
        assert fixture[row['start']:row['end']]==image[row['start']:row['end']]
    changed=bytearray(image);changed[0x4AFDC]^=1
    with pytest.raises(ValueError):contract.independent_fixture(source,bytes(changed))


@pytest.mark.parametrize('fault',('wide-byte','wide-word','wide-long','bool-mode','short-context',
    'short-surface','short-axis','short-curve','bad-SR','supplied-R5'))
def test_raw_input_refuses_width_loss_and_supplied_live_registers(fault):
    value=case()
    if fault=='wide-byte':value['speed_snapshot']=256
    elif fault=='wide-word':value['explicit_word_curve'][0]=65536
    elif fault=='wide-long':value['clock_15f8']=0x100000000
    elif fault=='bool-mode':value['rom_870b']=True
    elif fault=='short-context':value['context'].pop()
    elif fault=='short-surface':value['correction_surface'].pop()
    elif fault=='short-axis':value['surface_inner_axis'].pop()
    elif fault=='short-curve':value['speed_curves'].pop()
    elif fault=='bad-SR':value['context'][18]=2
    else:value['supplied_R5']=1
    with pytest.raises(ValueError):matrix.require_case(value)


def test_input_source_retains_complete_raw_domains_and_same_primary_originals():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    rows=matrix.cases(source,image)
    assert rows and all(set(r)=={*matrix.WIDTHS,*matrix.ARRAYS,'index','kind'} for r in rows)
    assert {r['speed_snapshot'] for r in rows}==set(range(256))
    assert any(r['clock_15f8']==0x80000000 for r in rows)
    assert any(r['word_2318']==16384 and r['rom_870b']==1 for r in rows)
    assert any(r['byte_1071']==255 and r['byte_41de']&32 for r in rows)
    raw=matrix.header(dict(source=source,cases=[case()]),image).decode()
    assert 'struct context context' in raw and '\\n' not in raw and '\n' in raw
    assert 'supplied_R5' not in raw and 'expected_1511' not in raw
    assert source['full_existing_same_primary_originals']==['byte_factor_caller_withdrawal_paths',
        'mixed_curve_caller_withdrawal_paths','word_interp_caller_withdrawal_paths','byte_surface_paths','division_callees_paths']
    for name,wanted in source['reused_source_sha256'].items():
        assert hashlib.sha256((repo.ROOT/name).read_bytes()).hexdigest()==wanted
