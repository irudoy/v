"""Executed full-entry scope, immutable stock fixture and raw input refusal sources."""
from copy import deepcopy
import ast,hashlib,re
import pytest
from kb import repo
from kb import third_trim_word_writer_contract as contract,third_trim_word_writer_matrix as matrix

def case():return dict(deepcopy(matrix.DEFAULTS),index=0,kind='controlled-third-trim-entry')

def test_published_counts_read_the_executed_descriptor():
    source=contract.descriptor(repo.ROOT);text=(repo.ROOT/'defs/JK08A.third-trim-word-writer.md').read_text()
    actual=(sum((r['end']-r['start'])//2 for r in source['unit']['code']),len(source['entries']),
        len(source['unit']['code']),len(source['unit']['pools']),len(source['unit']['aliases']),len(source['controlled_calibration']))
    match=re.search(r'binds (\d+) stock instructions in (\d+) actual entry path and (\d+) spans,\s*'
        r'(\d+) literal pools, (\d+) four-byte RAM pointer aliases and (\d+) calibration spans',text)
    assert match is not None and tuple(map(int,match.groups()))==actual==(205,1,2,20,7,28)
    root=sum((r['end']-r['start'])//2 for r in source['unit']['code'] if 0x5B534<=r['start']<0x5B704)
    assert int(re.search(r'entry has (\d+) instructions',text)[1])==root==205
    assert int(re.search(r'(\d+) stock entry paths?',text)[1])==len(source['stock_entry_paths'])==1
    assert int(re.search(r'(\d+) raw ROM controls',text)[1])==len(source['control_blobs'])==8
    assert int(re.search(r'containing (\d+) bytes',text)[1])==sum(r['size'] for r in source['control_blobs'])==8
    for phrase,key,wanted in (('byte context','context_bytes',80),('byte observer','observation_bytes',572),('byte frame','frame_bytes',192)):
        assert int(re.search(r'(\d+)-'+phrase,text)[1])==source[key]==wanted
    assert int(re.search(r'(\d+) independent context',text)[1])==source['independent_context_fields']==20
    assert int(re.search(r'All (\d+) RAM bytes',text)[1])==source['complete_initial_final_RAM_bytes']==65536
    assert source['entries']==[contract.ENTRY]==[0x5B534]
    tree=ast.parse((repo.ROOT/'tools/kb/src/kb/third_trim_word_writer_contract.py').read_text())
    assert sum(isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='LITERAL_OPERANDS' for t in n.targets) for n in tree.body)==1

def test_fixture_preserves_full_stock_code_and_only_declared_pointer_aliases():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image)
    assert {i for i,(a,z) in enumerate(zip(image,fixture)) if a!=z}<={i for row in aliases for i in range(row['address'],row['address']+4)}
    for row in source['unit']['code']:assert fixture[row['start']:row['end']]==image[row['start']:row['end']]
    changed=bytearray(image);changed[0x5B534]^=1
    with pytest.raises(ValueError):contract.independent_fixture(source,bytes(changed))

@pytest.mark.parametrize('fault',('wide-byte','wide-word','wide-counter','bool-mode','short-context','short-words','short-counters','bad-SR','supplied-R2'))
def test_raw_inputs_refuse_width_loss_and_supplied_live_results(fault):
    value=case()
    if fault=='wide-byte':value['rom_82e4']=256
    elif fault=='wide-word':value['prior_words'][0]=65536
    elif fault=='wide-counter':value['accumulators'][0]=1<<32
    elif fault=='bool-mode':value['flags_328a']=True
    elif fault=='short-context':value['context'].pop()
    elif fault=='short-words':value['prior_words'].pop()
    elif fault=='short-counters':value['accumulators'].pop()
    elif fault=='bad-SR':value['context'][18]=2
    else:value['supplied_R2']=1
    with pytest.raises(ValueError):matrix.require_case(value)

def test_input_source_keeps_full_context_and_raw_array_extents():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    rows=matrix.cases(source,image)
    assert rows and all(set(r)=={*matrix.WIDTHS,*matrix.ARRAYS,'index','kind'} for r in rows)
    for row in rows:matrix.require_case(row)
    assert {r['context'][4]&255 for r in rows}==set(range(256))
    raw=matrix.header(dict(source=source,cases=[case()]),image).decode()
    assert 'struct context context' in raw and '\\n' not in raw and '\n' in raw
    assert 'prior_words[256]' in raw and 'accumulators[256]' in raw
    assert 'supplied_R2' not in raw and 'expected_word' not in raw
    assert source['full_existing_same_primary_originals']==[]
    assert source['native_width']==16 and source['native_signed']=='unset'
    for name,wanted in source['reused_source_sha256'].items():
        assert hashlib.sha256((repo.ROOT/name).read_bytes()).hexdigest()==wanted

def test_published_raw_counts_read_the_executed_descriptor():
    source=contract.descriptor(repo.ROOT);text=(repo.ROOT/'defs/JK08A.third-trim-word-writer.md').read_text()
    assert int(re.search(r'All (\d+) raw channel values',text)[1])==source['actual_indexed_writer']['raw_channels']==256
    counts=tuple(map(int,re.search(r'Inputs include (\d+) raw prior words and (\d+) raw32 accumulators',text).groups()))
    assert counts==tuple(r['count'] for r in source['raw_memory_inputs'])==(256,256)
    assert counts==(matrix.ARRAYS['prior_words'][0],matrix.ARRAYS['accumulators'][0])
    assert source['actual_indexed_writer']['identity_bank1_channel']==0
    assert source['actual_accumulator']['neutral']==0x6400
