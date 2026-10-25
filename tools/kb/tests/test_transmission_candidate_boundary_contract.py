"""Executed paired scope, declared phase identities and complete raw input refusals."""
from copy import deepcopy
import ast,hashlib,re
import pytest
from kb import repo
from kb import transmission_candidate_boundary_contract as contract
from kb import transmission_candidate_boundary_matrix as matrix

def case():
    return dict(deepcopy(matrix.DEFAULTS),index=0,kind='controlled-pair')

def test_published_counts_and_current_phase_identity_read_the_executed_descriptor():
    source=contract.descriptor(repo.ROOT);text=(repo.ROOT/'defs/JK08A.transmission-candidate-boundary.md').read_text()
    actual=(sum((r['end']-r['start'])//2 for r in source['unit']['code']),len(source['entries']),
        len(source['unit']['code']),len(source['unit']['pools']),len(source['unit']['aliases']),len(source['controlled_calibration']))
    found=re.search(r'binds (\d+) stock instructions in (\d+) actual entry paths and (\d+) spans,\s*'
        r'(\d+) literal pools, (\d+) four-byte RAM pointer aliases and (\d+) calibration spans',text)
    assert found is not None and tuple(map(int,found.groups()))==actual==(294,2,3,38,9,41)
    assert source['entries']==[0x777FA,0x79030] and contract.PHASES==('completion','boundary')
    assert tuple(row['id'] for row in source['phases'])==contract.PHASES
    assert int(re.search(r'completion has (\d+) instructions',text)[1])==64
    assert int(re.search(r'boundary has (\d+) instructions',text)[1])==230
    assert int(re.search(r'(\d+)-byte context',text)[1])==source['context_bytes']==80
    assert int(re.search(r'(\d+)-byte observer',text)[1])==source['observation_bytes']==572
    assert int(re.search(r'(\d+)-byte frame',text)[1])==source['frame_bytes']==192
    assert int(re.search(r'(\d+) independent context',text)[1])==source['independent_context_fields_per_phase']==20
    assert int(re.search(r'complete (\d+)-byte RAM',text)[1])==source['complete_RAM_handoff_bytes']==65536
    assert int(re.search(r'All (\d+) actual completion',text)[1])==len(source['actual_handoff'])+2==4
    driver=(repo.ROOT/'tools/sh-elf-run/harness-transmission-candidate-boundary-paths.c').read_text()
    assert 'names[2]={"completion","boundary"}' in driver and 'entries[2]={0x777FAU,0x79030U}' in driver
    parser=(repo.ROOT/'tools/kb/src/kb/transmission_candidate_boundary_capture_evidence.py').read_text()
    assert 'phase_id=contract.PHASES[phase]' in parser
    assert "('producer','consumer')" not in parser
    tree=ast.parse((repo.ROOT/'tools/kb/src/kb/transmission_candidate_boundary_contract.py').read_text())
    assert sum(isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='LITERAL_OPERANDS' for t in n.targets) for n in tree.body)==1

def test_exact_fixture_preserves_both_complete_entries_and_only_relocates_declared_pointer_words():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image)
    assert {i for i,(a,z) in enumerate(zip(image,fixture)) if a!=z}<={i for r in aliases for i in range(r['address'],r['address']+4)}
    for row in source['unit']['code']:assert fixture[row['start']:row['end']]==image[row['start']:row['end']]
    changed=bytearray(image);changed[0x777FA]^=1
    with pytest.raises(ValueError):contract.independent_fixture(source,bytes(changed))

@pytest.mark.parametrize('fault',('wide-source','bool-mode','short-first-context','short-second-context','bad-SR','supplied-bound'))
def test_raw_pair_refuses_lost_width_or_supplied_intermediate_results(fault):
    value=case()
    if fault=='wide-source':value['word_4162']=65536
    elif fault=='bool-mode':value['rom_83c1']=True
    elif fault=='short-first-context':value['completion_context'].pop()
    elif fault=='short-second-context':value['boundary_context'].pop()
    elif fault=='bad-SR':value['boundary_context'][18]=2
    else:value['supplied_3480']=1000
    with pytest.raises(ValueError):matrix.require_case(value)

def test_input_generation_keeps_both_independent_context_keys_and_current_header():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    rows=matrix.cases(source,image)
    assert rows and all(set(row)=={*matrix.WIDTHS,*matrix.ARRAYS,'index','kind'} for row in rows)
    assert any(row['word_2438']==0x8000 for row in rows)
    raw=matrix.header(dict(source=source,cases=[case()]),image).decode()
    assert 'struct context contexts[2]' in raw and '\\n' not in raw and '\n' in raw
    assert all(name not in raw for name in ('supplied_3480','expected_19c6','intermediate_result'))
    assert source['reseed_between_phases'] is False
    assert source['full_existing_same_primary_originals']==['request_boundary_publication_paths']
    for name,wanted in source['reused_source_sha256'].items():assert hashlib.sha256((repo.ROOT/name).read_bytes()).hexdigest()==wanted
