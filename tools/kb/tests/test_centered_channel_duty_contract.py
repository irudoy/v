"""Executed paired scope, exact phase names and raw curve/context refusal sources."""
from copy import deepcopy
import ast,hashlib,re
import pytest
from kb import repo
from kb import centered_channel_duty_contract as contract
from kb import centered_channel_duty_matrix as matrix

def case():return dict(deepcopy(matrix.DEFAULTS),index=0,kind='controlled-coasting-pair')

def test_published_counts_and_current_phase_identity_read_the_executed_descriptor():
    source=contract.descriptor(repo.ROOT);text=(repo.ROOT/'defs/JK08A.centered-channel-duty.md').read_text()
    actual=(sum((r['end']-r['start'])//2 for r in source['unit']['code']),len(source['entries']),
        len(source['unit']['code']),len(source['unit']['pools']),len(source['unit']['aliases']),len(source['controlled_calibration']))
    found=re.search(r'binds (\d+) stock instructions in (\d+) actual entry paths and (\d+) spans,\s*'
        r'(\d+) literal pools, (\d+) four-byte RAM pointer aliases and (\d+) calibration spans',text)
    assert found is not None and tuple(map(int,found.groups()))==actual==(816,2,12,53,14,65)
    assert source['entries']==[0xBE5BC,0xBE814] and contract.PHASES==('producer','consumer')
    assert tuple(row['id'] for row in source['phases'])==contract.PHASES
    producer=sum((r['end']-r['start'])//2 for r in source['unit']['code'] if 0xBE5BC<=r['start']<0xBE814)
    consumer=sum((r['end']-r['start'])//2 for r in source['unit']['code'] if r['start']==0xBE814)
    assert int(re.search(r'producer has (\d+) instructions',text)[1])==producer==254
    assert int(re.search(r'consumer has (\d+) instructions',text)[1])==consumer==107
    assert int(re.search(r'includes (\d+) stock entry paths',text)[1])==len(source['stock_entry_paths'])==10
    for phrase,key,wanted in (('byte context','context_bytes',80),('byte observer','observation_bytes',572),('byte frame','frame_bytes',192)):
        assert int(re.search(r'(\d+)-'+phrase,text)[1])==source[key]==wanted
    assert int(re.search(r'(\d+) independent context',text)[1])==source['independent_context_fields_per_phase']==20
    assert int(re.search(r'complete (\d+)-byte RAM',text)[1])==source['complete_RAM_handoff_bytes']==65536
    driver=(repo.ROOT/'tools/sh-elf-run/harness-centered-channel-duty-paths.c').read_text()
    assert 'names[2]={"producer","consumer"}' in driver and 'entries[2]={0xBE5BCU,0xBE814U}' in driver
    parser=(repo.ROOT/'tools/kb/src/kb/centered_channel_duty_capture_evidence.py').read_text()
    assert 'phase_id=contract.PHASES[phase]' in parser
    tree=ast.parse((repo.ROOT/'tools/kb/src/kb/centered_channel_duty_contract.py').read_text())
    assert sum(isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='LITERAL_OPERANDS' for t in n.targets) for n in tree.body)==1

def test_exact_fixture_preserves_full_entries_and_only_declared_pointer_aliases():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image)
    assert {i for i,(a,z) in enumerate(zip(image,fixture)) if a!=z}<={i for r in aliases for i in range(r['address'],r['address']+4)}
    for row in source['unit']['code']:assert fixture[row['start']:row['end']]==image[row['start']:row['end']]
    changed=bytearray(image);changed[0xBE5BC]^=1
    with pytest.raises(ValueError):contract.independent_fixture(source,bytes(changed))

@pytest.mark.parametrize('fault',('wide-cell','bool-mode','short-producer','short-consumer','short-curve','bad-SR','supplied-word'))
def test_raw_pair_refuses_lost_width_or_supplied_intermediate_results(fault):
    value=case()
    if fault=='wide-cell':value['implicit_curves'][0]=256
    elif fault=='bool-mode':value['rom_8616']=True
    elif fault=='short-producer':value['producer_context'].pop()
    elif fault=='short-consumer':value['consumer_context'].pop()
    elif fault=='short-curve':value['explicit_curves'].pop()
    elif fault=='bad-SR':value['consumer_context'][18]=2
    else:value['supplied_1a9c']=1000
    with pytest.raises(ValueError):matrix.require_case(value)

def test_input_generation_preserves_independent_raw_contexts_curves_and_original():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    rows=matrix.cases(source,image)
    assert rows and all(set(row)=={*matrix.WIDTHS,*matrix.ARRAYS,'index','kind'} for row in rows)
    assert any(row['word_1afc']==0x80000000 for row in rows)
    raw=matrix.header(dict(source=source,cases=[case()]),image).decode()
    assert 'struct context contexts[2]' in raw and '\\n' not in raw and '\n' in raw
    assert all(name not in raw for name in ('supplied_1a9c','expected_2441','intermediate_result'))
    assert source['reseed_between_phases'] is False
    assert source['full_existing_same_primary_originals']==['byte_factor_caller_withdrawal_paths','division_callees_paths']
    for name,wanted in source['reused_source_sha256'].items():assert hashlib.sha256((repo.ROOT/name).read_bytes()).hexdigest()==wanted

def test_shared_terminal_neighbor_and_native_writer_width_read_exact_sources():
    source=contract.descriptor(repo.ROOT)
    assert [(r['address'],r['active_cells'],r['physical_bytes']) for r in source['explicit_physical_curves']]==[(0x12E82,8,9),(0x12E8A,8,9)]
    assert [(r['address'],r['size']) for r in source['input_blobs']]==[(0x11BDB,8),(0x12E72,16),(0x12E82,17)]
    assert source['shared_explicit_neighbor']['address']==0x12E8A
    mode,=[r for r in source['control_blobs'] if r['address']==0x8616]
    assert int(mode['stock_hex'],16)==source['actual_source']['stock_mode_byte']==1
    assert source['actual_source']['stock_active_inference'] is False
    from kb import centered_channel_duty_access_contract as owning
    text=(repo.ROOT/'defs/JK08A.centered-channel-duty.md').read_text()
    assert all(r['original_claim_sha256'] in text for r in owning.DECLARED['reference'])
    assert len(owning.DECLARED['reference'])==2
    assert int(re.search(r'(\d+) raw ROM controls',text)[1])==len(source['control_blobs'])==9
    assert source['original_writer']['declared_width']==8
