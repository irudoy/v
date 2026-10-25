"""Executed full-entry scope, immutable stock fixture and raw input refusal sources."""
from copy import deepcopy
import ast,hashlib,re
import pytest
from kb import repo
from kb import event_timing_candidate_contract as contract,event_timing_candidate_matrix as matrix

def case():return dict(deepcopy(matrix.DEFAULTS),index=0,kind='controlled-event-timing-entry')

def test_published_counts_read_the_executed_descriptor():
    source=contract.descriptor(repo.ROOT);text=(repo.ROOT/'defs/JK08A.event-timing-candidate.md').read_text()
    actual=(sum((r['end']-r['start'])//2 for r in source['unit']['code']),len(source['entries']),
        len(source['unit']['code']),len(source['unit']['pools']),len(source['unit']['aliases']),len(source['controlled_calibration']))
    match=re.search(r'binds (\d+) stock instructions in (\d+) actual entry path and (\d+) spans,\s*'
        r'(\d+) literal pools, (\d+) four-byte RAM pointer aliases and (\d+) calibration spans',text)
    assert match is not None and tuple(map(int,match.groups()))==actual==(514,1,7,27,11,33)
    root=sum((r['end']-r['start'])//2 for r in source['unit']['code'] if 0x4D99C<=r['start']<0x4DB9C)
    assert int(re.search(r'entry has (\d+) instructions',text)[1])==root==254
    assert int(re.search(r'(\d+) stock entry paths',text)[1])==len(source['stock_entry_paths'])==6
    assert int(re.search(r'(\d+) raw ROM controls',text)[1])==len(source['control_blobs'])==4
    assert int(re.search(r'containing (\d+) bytes',text)[1])==sum(r['size'] for r in source['control_blobs'])==4
    for phrase,key,wanted in (('byte context','context_bytes',80),('byte observer','observation_bytes',572),('byte frame','frame_bytes',192)):
        assert int(re.search(r'(\d+)-'+phrase,text)[1])==source[key]==wanted
    assert int(re.search(r'(\d+) independent context',text)[1])==source['independent_context_fields']==20
    assert int(re.search(r'All (\d+) RAM bytes',text)[1])==source['complete_initial_final_RAM_bytes']==65536
    assert source['entries']==[contract.ENTRY]==[0x4D99C]
    tree=ast.parse((repo.ROOT/'tools/kb/src/kb/event_timing_candidate_contract.py').read_text())
    assert sum(isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='LITERAL_OPERANDS' for t in n.targets) for n in tree.body)==1

def test_fixture_preserves_full_stock_code_and_only_declared_pointer_aliases():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image)
    assert {i for i,(a,z) in enumerate(zip(image,fixture)) if a!=z}<={i for row in aliases for i in range(row['address'],row['address']+4)}
    for row in source['unit']['code']:assert fixture[row['start']:row['end']]==image[row['start']:row['end']]
    changed=bytearray(image);changed[0x4D99C]^=1
    with pytest.raises(ValueError):contract.independent_fixture(source,bytes(changed))

@pytest.mark.parametrize('fault',('wide-byte','wide-word','bool-mode','short-context','short-words','short-axis','bad-SR','supplied-R6'))
def test_raw_inputs_refuse_width_loss_and_supplied_live_results(fault):
    value=case()
    if fault=='wide-byte':value['rom_8290']=256
    elif fault=='wide-word':value['source_words'][0]=65536
    elif fault=='bool-mode':value['byte_24cc']=True
    elif fault=='short-context':value['context'].pop()
    elif fault=='short-words':value['source_words'].pop()
    elif fault=='short-axis':value['source_axis'].pop()
    elif fault=='bad-SR':value['context'][18]=2
    else:value['supplied_R6']=1
    with pytest.raises(ValueError):matrix.require_case(value)

def test_input_source_keeps_complete_context_and_both_required_originals():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    rows=matrix.cases(source,image);assert rows and all(set(r)=={*matrix.WIDTHS,*matrix.ARRAYS,'index','kind'} for r in rows)
    assert any(r['word_237e']==65535 and len(r['source_words'])==9 and len(r['source_axis'])==8 for r in rows)
    raw=matrix.header(dict(source=source,cases=[case()]),image).decode()
    assert 'struct context context' in raw and '\\n' not in raw and '\n' in raw
    assert 'supplied_R6' not in raw and 'expected_12d6' not in raw
    assert source['prior2000_memory_is_input'] is False
    assert source['full_existing_same_primary_originals']==['word_interp_caller_withdrawal_paths','division_callees_paths']
    for name,wanted in source['reused_source_sha256'].items():assert hashlib.sha256((repo.ROOT/name).read_bytes()).hexdigest()==wanted
