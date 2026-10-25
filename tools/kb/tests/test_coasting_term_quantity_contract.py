"""Executed paired scope, exact phase names and raw curve/context refusal sources."""
from copy import deepcopy
import ast,hashlib,re
import pytest
from kb import repo
from kb import coasting_term_quantity_contract as contract
from kb import coasting_term_quantity_matrix as matrix

def case():return dict(deepcopy(matrix.DEFAULTS),index=0,kind='controlled-coasting-pair')

def test_published_counts_and_current_phase_identity_read_the_executed_descriptor():
    source=contract.descriptor(repo.ROOT);text=(repo.ROOT/'defs/JK08A.coasting-term-quantity.md').read_text()
    actual=(sum((r['end']-r['start'])//2 for r in source['unit']['code']),len(source['entries']),
        len(source['unit']['code']),len(source['unit']['pools']),len(source['unit']['aliases']),len(source['controlled_calibration']))
    found=re.search(r'binds (\d+) stock instructions in (\d+) actual entry paths and (\d+) spans,\s*'
        r'(\d+) literal pools, (\d+) four-byte RAM pointer aliases and (\d+) calibration spans',text)
    assert found is not None and tuple(map(int,found.groups()))==actual==(467,2,9,33,12,47)
    assert source['entries']==[0x2C626,0x47120] and contract.PHASES==('producer','consumer')
    assert tuple(row['id'] for row in source['phases'])==contract.PHASES
    producer=sum((r['end']-r['start'])//2 for r in source['unit']['code'] if r['start']==0x2C626)
    consumer=sum((r['end']-r['start'])//2 for r in source['unit']['code'] if 0x47120<=r['start']<0x47364)
    assert int(re.search(r'producer has (\d+) instructions',text)[1])==producer==15
    assert int(re.search(r'consumer has (\d+) instructions',text)[1])==consumer==287
    assert int(re.search(r'includes (\d+) stock entry paths',text)[1])==len(source['stock_entry_paths'])==8
    for phrase,key,wanted in (('byte context','context_bytes',80),('byte observer','observation_bytes',572),('byte frame','frame_bytes',192)):
        assert int(re.search(r'(\d+)-'+phrase,text)[1])==source[key]==wanted
    assert int(re.search(r'(\d+) independent context',text)[1])==source['independent_context_fields_per_phase']==20
    assert int(re.search(r'complete (\d+)-byte RAM',text)[1])==source['complete_RAM_handoff_bytes']==65536
    driver=(repo.ROOT/'tools/sh-elf-run/harness-coasting-term-quantity-paths.c').read_text()
    assert 'names[2]={"producer","consumer"}' in driver and 'entries[2]={0x2C626U,0x47120U}' in driver
    parser=(repo.ROOT/'tools/kb/src/kb/coasting_term_quantity_capture_evidence.py').read_text()
    assert 'phase_id=contract.PHASES[phase]' in parser
    tree=ast.parse((repo.ROOT/'tools/kb/src/kb/coasting_term_quantity_contract.py').read_text())
    assert sum(isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='LITERAL_OPERANDS' for t in n.targets) for n in tree.body)==1

def test_exact_fixture_preserves_full_entries_and_only_declared_pointer_aliases():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image)
    assert {i for i,(a,z) in enumerate(zip(image,fixture)) if a!=z}<={i for r in aliases for i in range(r['address'],r['address']+4)}
    for row in source['unit']['code']:assert fixture[row['start']:row['end']]==image[row['start']:row['end']]
    changed=bytearray(image);changed[0x2C626]^=1
    with pytest.raises(ValueError):contract.independent_fixture(source,bytes(changed))

@pytest.mark.parametrize('fault',('wide-cell','bool-mode','short-producer','short-consumer','short-curve','bad-SR','supplied-word'))
def test_raw_pair_refuses_lost_width_or_supplied_intermediate_results(fault):
    value=case()
    if fault=='wide-cell':value['source_curve'][0]=256
    elif fault=='bool-mode':value['rom_870c']=True
    elif fault=='short-producer':value['producer_context'].pop()
    elif fault=='short-consumer':value['consumer_context'].pop()
    elif fault=='short-curve':value['coasting_curve'].pop()
    elif fault=='bad-SR':value['consumer_context'][18]=2
    else:value['supplied_1230']=1000
    with pytest.raises(ValueError):matrix.require_case(value)

def test_input_generation_preserves_independent_raw_contexts_curves_and_original():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    rows=matrix.cases(source,image)
    assert rows and all(set(row)=={*matrix.WIDTHS,*matrix.ARRAYS,'index','kind'} for row in rows)
    assert any(row['word_1748']==0x8000 for row in rows)
    raw=matrix.header(dict(source=source,cases=[case()]),image).decode()
    assert 'struct context contexts[2]' in raw and '\\n' not in raw and '\n' in raw
    assert all(name not in raw for name in ('supplied_1230','expected_13ea','intermediate_result'))
    assert source['reseed_between_phases'] is False
    assert source['full_existing_same_primary_originals']==['byte_factor_caller_withdrawal_paths']
    for name,wanted in source['reused_source_sha256'].items():assert hashlib.sha256((repo.ROOT/name).read_bytes()).hexdigest()==wanted
