"""Executed full-entry scope, immutable stock fixture and raw input refusal sources."""
from copy import deepcopy
import ast,hashlib,re
import pytest
from kb import repo
from kb import timing_additive_candidate_contract as contract,timing_additive_candidate_matrix as matrix

def case():return dict(deepcopy(matrix.DEFAULTS),index=0,kind='controlled-timing-additive-entry')

def test_published_counts_read_the_executed_descriptor():
    source=contract.descriptor(repo.ROOT);text=(repo.ROOT/'defs/JK08A.timing-additive-candidate.md').read_text()
    actual=(sum((r['end']-r['start'])//2 for r in source['unit']['code']),len(source['entries']),
        len(source['unit']['code']),len(source['unit']['pools']),len(source['unit']['aliases']),len(source['controlled_calibration']))
    match=re.search(r'binds (\d+) stock instructions in (\d+) actual entry path and (\d+) spans,\s*'
        r'(\d+) literal pools, (\d+) four-byte RAM pointer aliases and (\d+) calibration spans',text)
    assert match is not None and tuple(map(int,match.groups()))==actual==(510,1,9,32,10,38)
    root=sum((r['end']-r['start'])//2 for r in source['unit']['code'] if 0x4BDC2<=r['start']<0x4BEF2)
    assert int(re.search(r'entry has (\d+) instructions',text)[1])==root==152
    assert int(re.search(r'(\d+) stock entry paths',text)[1])==len(source['stock_entry_paths'])==9
    assert int(re.search(r'(\d+) raw ROM controls?',text)[1])==len(source['control_blobs'])==1
    assert int(re.search(r'containing (\d+) bytes',text)[1])==sum(r['size'] for r in source['control_blobs'])==2
    for phrase,key,wanted in (('byte context','context_bytes',80),('byte observer','observation_bytes',572),('byte frame','frame_bytes',192)):
        assert int(re.search(r'(\d+)-'+phrase,text)[1])==source[key]==wanted
    assert int(re.search(r'(\d+) independent context',text)[1])==source['independent_context_fields']==20
    assert int(re.search(r'All (\d+) RAM bytes',text)[1])==source['complete_initial_final_RAM_bytes']==65536
    assert source['entries']==[contract.ENTRY]==[0x4BDC2]
    tree=ast.parse((repo.ROOT/'tools/kb/src/kb/timing_additive_candidate_contract.py').read_text())
    assert sum(isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='LITERAL_OPERANDS' for t in n.targets) for n in tree.body)==1

def test_fixture_preserves_full_stock_code_and_only_declared_pointer_aliases():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image)
    assert {i for i,(a,z) in enumerate(zip(image,fixture)) if a!=z}<={i for row in aliases for i in range(row['address'],row['address']+4)}
    for row in source['unit']['code']:assert fixture[row['start']:row['end']]==image[row['start']:row['end']]
    changed=bytearray(image);changed[0x4BDC2]^=1
    with pytest.raises(ValueError):contract.independent_fixture(source,bytes(changed))

@pytest.mark.parametrize('fault',('wide-byte','wide-word','bool-mode','short-context','short-surface','short-axis','short-curve','bad-SR','supplied-R6'))
def test_raw_inputs_refuse_width_loss_and_supplied_live_results(fault):
    value=case()
    if fault=='wide-byte':value['source_curve'][0]=256
    elif fault=='wide-word':value['source_surface'][0]=65536
    elif fault=='bool-mode':value['byte_2458']=True
    elif fault=='short-context':value['context'].pop()
    elif fault=='short-surface':value['source_surface'].pop()
    elif fault=='short-axis':value['source_inner_axis'].pop()
    elif fault=='short-curve':value['source_curve'].pop()
    elif fault=='bad-SR':value['context'][18]=2
    else:value['supplied_R6']=1
    with pytest.raises(ValueError):matrix.require_case(value)

def test_input_source_keeps_complete_context_and_both_required_originals():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    rows=matrix.cases(source,image);assert rows and all(set(r)=={*matrix.WIDTHS,*matrix.ARRAYS,'index','kind'} for r in rows)
    assert any(r['word_1024']==65535 and len(r['source_surface'])==64 and len(r['source_curve'])==9 for r in rows)
    raw=matrix.header(dict(source=source,cases=[case()]),image).decode()
    assert 'struct context context' in raw and '\\n' not in raw and '\n' in raw
    assert 'supplied_R6' not in raw and 'expected_1830' not in raw
    assert source['prior134A_memory_is_input'] is False
    assert source['full_existing_same_primary_originals']==['mixed_curve_caller_withdrawal_paths','division_callees_paths']
    for name,wanted in source['reused_source_sha256'].items():assert hashlib.sha256((repo.ROOT/name).read_bytes()).hexdigest()==wanted

def test_physical_local_carrier_and_wide_divisor_are_executed_descriptor_facts():
    source=contract.descriptor(repo.ROOT)
    assert source['complete_inner_argument']==dict(local_bytes=4,word_write_site=0x4BE48,word_offset=2,
        full_wrapper_read_site=0x26286,root_call_SP_delta=-24,read_SP_delta=-40,low16_unsigned_coordinate=True)
    assert source['actual_unsigned_divisor']==500000==0x7A120
    assert source['actual_product_max']==255*65535*255<2**32
    assert source['source_surface']==dict(rows=8,columns=8,width_bytes=2,physical_words=64)
    assert source['source_byte_curve']==dict(physical_bytes=9,active_bytes=8,zero_weight_ninth_byte_invariance=True)

def test_published_surface_and_curve_counts_bind_physical_input_extents():
    source=contract.descriptor(repo.ROOT);text=(repo.ROOT/'defs/JK08A.timing-additive-candidate.md').read_text()
    rows,columns=map(int,re.search(r'(\d+)x(\d+) uint16 surface',text).groups())
    assert (rows,columns)==(source['source_surface']['rows'],source['source_surface']['columns'])==(8,8)
    assert int(re.search(r'has (\d+) physical words',text)[1])==source['source_surface']['physical_words']==64
    assert int(re.search(r'Every one of (\d+) surface words',text)[1])==64
    assert 'eight active byte-curve cells' in text and source['source_byte_curve']['active_bytes']==8
    assert 'nine bytes at 00011F02' in text and source['source_byte_curve']['physical_bytes']==9
