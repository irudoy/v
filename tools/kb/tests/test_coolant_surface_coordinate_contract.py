"""Descriptor-bound counts, complete physical spans and strict raw input domains."""
from copy import deepcopy
import hashlib
import re
import pytest
from kb import repo
from kb import coolant_surface_coordinate_contract as contract,coolant_surface_coordinate_matrix as matrix


def case():return dict(deepcopy(matrix.DEFAULTS),index=0,kind='controlled-coolant-coordinate-entry')


def test_published_counts_read_the_executed_descriptor():
    source=contract.descriptor(repo.ROOT);text=(repo.ROOT/'defs/JK08A.coolant-surface-coordinate.md').read_text()
    actual=(sum((r['end']-r['start'])//2 for r in source['unit']['code']),len(source['entries']),
        len(source['unit']['code']),len(source['unit']['pools']),len(source['unit']['aliases']),
        len(source['controlled_calibration']))
    pattern=r'binds (\d+) stock instructions in\s*(\d+) actual entry path and (\d+) spans, (\d+) literal pools, (\d+) four-byte RAM pointer\s*aliases and (\d+) calibration spans'
    assert tuple(map(int,re.search(pattern,text).groups()))==actual==(209,1,7,14,2,16)
    root=sum((r['end']-r['start'])//2 for r in source['unit']['code'] if r['start']==0x52576)
    assert int(re.search(r'entry has (\d+) instructions',text)[1])==root==49
    assert int(re.search(r'(\d+) stock entry paths',text)[1])==len(source['stock_entry_paths'])==7
    assert int(re.search(r'(\d+) raw input blobs',text)[1])==len(source['input_blobs'])==2
    assert int(re.search(r'containing (\d+) input bytes',text)[1])==sum(r['size'] for r in source['input_blobs'])==80
    for phrase,key,wanted in (('byte context','context_bytes',80),('byte observer','observation_bytes',572),(r'byte\s*frame','frame_bytes',192)):
        assert int(re.search(r'(\d+)-'+phrase,text)[1])==source[key]==wanted
    assert int(re.search(r'(\d+) independent context',text)[1])==source['independent_context_fields']==20
    assert int(re.search(r'All (\d+) RAM bytes',text)[1])==source['complete_initial_final_RAM_bytes']==65536
    assert int(re.search(r'allocates (\d+) stack bytes',text)[1])==source['outer_stack_bytes']==16


def test_published_surface_word_and_coordinate_facts_read_the_descriptor():
    source=contract.descriptor(repo.ROOT);text=(repo.ROOT/'defs/JK08A.coolant-surface-coordinate.md').read_text()
    inputs={r['name']:r for r in source['input_blobs']}
    rows,columns=map(int,re.search(r'(\d+)x(\d+) byte surface',text).groups())
    assert rows*columns==inputs['surface']['size']==int(re.search(r'(\d+) physical bytes',text)[1])==64
    assert int(re.search(r'(\d+) physical words',text)[1])*2==inputs['word_curve']['size']==16
    assert int(re.search(r'coordinate multiplication (\d+)',text)[1])==source['actual_word_input']['multiplier']==32
    assert int(re.search(r'cap (\d+)',text)[1])==source['actual_word_input']['maximum']==65535
    threshold,=[r for r in source['unit']['pools'] if r['address']==0x263F0]
    assert int(re.search(r'endpoint threshold is (\d+)',text)[1])==int(threshold['stock_hex'],16)==57344
    assert source['actual_RAM_input']['read_site']==0x52582
    assert source['actual_RAM_input']['unsigned_extension_site']==0x52586
    assert source['actual_second_input']['unsigned_delay_site']==0x5258E
    assert source['actual_helper_calls']==[dict(site=0x5258C,delay_slot=0x5258E,target=0x26040)]
    assert source['actual_final_output']==dict(address=0xFFFF1652,width_bytes=2,site=0x525CC,register=2)
    assert source['wrapper_has_no_physical_read_of_RAM106F'] is True


def test_fixture_retains_all_stock_instructions_and_only_declared_pointer_aliases():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image)
    assert {i for i,(a,z) in enumerate(zip(image,fixture)) if a!=z}<={i for r in aliases for i in range(r['address'],r['address']+4)}
    for r in source['unit']['code']:assert fixture[r['start']:r['end']]==image[r['start']:r['end']]
    changed=bytearray(image);changed[0x52576]^=1
    with pytest.raises(ValueError):contract.independent_fixture(source,bytes(changed))


@pytest.mark.parametrize('fault',('wide-byte','wide-word','bool-coordinate','short-context','short-surface','short-curve','bad-SR','supplied-R5'))
def test_raw_input_refuses_narrowed_or_supplied_live_results(fault):
    value=case()
    if fault=='wide-byte':value['coolant_snapshot']=256
    elif fault=='wide-word':value['word_curve'][0]=65536
    elif fault=='bool-coordinate':value['inner_snapshot']=True
    elif fault=='short-context':value['context'].pop()
    elif fault=='short-surface':value['surface'].pop()
    elif fault=='short-curve':value['word_curve'].pop()
    elif fault=='bad-SR':value['context'][18]=2
    else:value['supplied_R5']=1
    with pytest.raises(ValueError):matrix.require_case(value)


def test_input_source_retains_full_raw_coordinates_and_same_primary_originals():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes();rows=matrix.cases(source,image)
    assert rows and all(set(r)=={*matrix.WIDTHS,*matrix.ARRAYS,'index','kind'} for r in rows)
    for name in ('coolant_snapshot','inner_snapshot'):assert {r[name] for r in rows}==set(range(256))
    assert any(r['word_1222']==65535 and r['word_curve']==[65535]*8 for r in rows)
    raw=matrix.header(dict(source=source,cases=[case()]),image).decode()
    assert 'struct context context' in raw and '\\n' not in raw and '\n' in raw
    assert 'supplied_R5' not in raw and 'expected_1652' not in raw
    assert source['full_existing_same_primary_originals']==['byte_surface_paths','word_interp_caller_withdrawal_paths']
    for name,wanted in source['reused_source_sha256'].items():assert hashlib.sha256((repo.ROOT/name).read_bytes()).hexdigest()==wanted
