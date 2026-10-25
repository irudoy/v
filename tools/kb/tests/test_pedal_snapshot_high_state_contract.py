"""Executed source counts, exact existing-prefix fixture and typed paired inputs."""
from copy import deepcopy
import re
import pytest
from kb import repo
from kb import pedal_snapshot_high_state_contract as contract,pedal_snapshot_high_state_matrix as matrix
from kb import pedal_snapshot_high_state_semantics as numeric


def case(**changes):
    image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    value=dict(deepcopy(matrix.DEFAULTS),threshold_curve=image[0x1473A:0x1474A],index=0,kind='paired-refusal')
    value.update(changes);return value


def test_published_counts_read_the_executed_paired_descriptor():
    source=contract.descriptor(repo.ROOT);text=(repo.ROOT/'defs/JK08A.pedal-snapshot-high-state.md').read_text()
    counts=re.search(r'(\d+) stock instructions in\s*(\d+) stock entry paths and (\d+) code spans, '
        r'(\d+) literal pools, (\d+) four-byte RAM aliases\s*and (\d+) calibration spans',text)
    units=(source['unit'],source['snapshot'])
    actual=(sum((r['end']-r['start'])//2 for unit in units for r in unit['code']),len(source['stock_entry_paths']),
        sum(len(unit['code']) for unit in units),sum(len(unit['pools']) for unit in units),
        len(source['aliases']),len(source['controlled_calibration']))
    assert counts is not None and tuple(map(int,counts.groups()))==actual==(613,7,9,58,21,89)
    assert int(re.search(r'root uses (\d+) stack bytes',text)[1])==source['root_stack_bytes']==28
    assert int(re.search(r'Its (\d+) raw\s*ROM controls',text)[1])==len(source['control_blobs'])==30
    assert int(re.search(r'(\d+)-byte uniform curve',text)[1])==source['input_blobs'][0]['size']==16
    assert source['snapshot']['entry']==0x20FA4 and source['snapshot']['end']==0x20FD0
    assert source['snapshot']['entry_context']=={'r11':0x22558}
    assert [0xFFFF2672,0xFFFF266E,4] in source['snapshot']['history']
    assert source['complete_RAM_handoff_bytes']==65536 and source['reseed_between_phases'] is False
    assert (source['snapshot']['context_bytes'],source['snapshot']['observation_bytes'],source['snapshot']['frame_bytes'])==(76,380,96)
    assert (source['context_bytes'],source['observation_bytes'],source['frame_bytes'])==(80,572,192)
    assert source['complete_existing_coherent_original_required_same_primary'] is True

    boundary_count=int(re.search(r'and (\d+) observing-boundary instructions',text)[1])
    assert boundary_count==len(bytes.fromhex(source['snapshot']['boundary']['bytes']))//2==4
    legacy=re.search(r'(\d+)-byte context, (\d+)-byte observer, (\d+)-byte\s*frame',text)
    ordinary=re.search(r'existing (\d+)-byte context,\s*(\d+)-byte observer and (\d+)-byte frame',text)
    assert tuple(map(int,legacy.groups()))==tuple(source['snapshot'][k] for k in ('context_bytes','observation_bytes','frame_bytes'))
    assert tuple(map(int,ordinary.groups()))==tuple(source[k] for k in ('context_bytes','observation_bytes','frame_bytes'))
    assert int(re.search(r'All (\d+) comparator context fields',text)[1])==source['context_bytes']//4==20
    assert int(re.search(r'complete (\d+)-byte RAM',text)[1])==source['complete_RAM_handoff_bytes']
    assert int(re.search(r'the (\d+)-byte block transfer',text)[1])==source['snapshot']['length_bytes']
    assert f"{source['snapshot']['entry']:08X}..{source['snapshot']['end']:08X}" in text
    assert f"{source['snapshot']['helper']:08X}" in text and f"{source['entries'][0]:08X}" in text


def test_fixture_retains_stock_code_and_only_exact_existing_boundary_and_full_aliases():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image)
    permitted={at for row in aliases for at in range(row['address'],row['address']+4)}|set(range(0x20FD0,0x20FD8))
    assert {i for i,(a,b) in enumerate(zip(image,fixture)) if a!=b}<=permitted
    for unit in (source['unit'],source['snapshot']):
        for row in unit['code']:assert fixture[row['start']:row['end']]==image[row['start']:row['end']]
    assert fixture[0x20FD0:0x20FD8]==bytes.fromhex('57f6472a000b0009')
    damaged=bytearray(image);damaged[0x47A56]^=1
    with pytest.raises(ValueError):contract.independent_fixture(source,bytes(damaged))


@pytest.mark.parametrize('fault',('bool-word','wide-word','wide-byte','short-block','short-curve',
    'snapshot-variant','snapshot-T','short-context','bad-SR','supplied-output'))
def test_paired_inputs_refuse_partial_state_and_supplied_results(fault):
    value=case()
    if fault=='bool-word':value['word_2672']=True
    elif fault=='wide-word':value['word_2672']=65536
    elif fault=='wide-byte':value['byte_11ae']=256
    elif fault=='short-block':value['snapshot_block']=bytes(259)
    elif fault=='short-curve':value['threshold_curve']=bytes(14)
    elif fault=='snapshot-variant':value['snapshot_variant']=2
    elif fault=='snapshot-T':value['snapshot_t']=2
    elif fault=='short-context':value['context'].pop()
    elif fault=='bad-SR':value['context'][18]=2
    else:value['expected_high']=True
    with pytest.raises(ValueError):matrix.require_case(value)


def test_header_contains_both_complete_input_contexts_and_no_expected_output():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    header=matrix.header(dict(source=source,cases=[case()]),image).decode()
    assert len(header.splitlines())>10
    assert 'struct snapshot_context snapshot' in header and 'struct context comparator' in header
    assert 'uint8_t block[260]' in header and 'pedal_calibration_blobs' in header
    assert all(name not in header for name in ('expected_high','computed_word','supplied_result'))
    assert matrix.snapshot_context(case())[11]==0x22558
    for register in range(20):
        value=case();value['context'][register]=0xFFFFFFFF if register!=18 else 0x3F1
        matrix.require_case(value)


def test_history_and_both_physical_pedal_comparison_modes_keep_exact_words():
    for raw,high in ((0,False),(609,False),(610,True),(65535,True)):
        value=case(word_2672=raw,word_2674=0xBEEF);before=matrix.memory(value);middle=numeric.snapshot(before)
        assert middle[0x266E:0x2672]==raw.to_bytes(2,'big')+bytes.fromhex('beef')
        result=numeric.caller(middle,matrix.input_calibrations(value),matrix.context({},value))
        assert result['pedal_high'] is high and bool(result['memory'][0x246A]&128) is high
    for raw,high in ((0,False),(65535,True)):
        value=case(word_2672=raw,rom_870c=128,byte_110e=0)
        result=numeric.caller(numeric.snapshot(matrix.memory(value)),matrix.input_calibrations(value),matrix.context({},value))
        assert bool(result['memory'][0x24B4]&64) is high


def test_uniform_curve_preserves_signed_cap_return_and_integer_interiors():
    table=b''.join(value.to_bytes(2,'big') for value in (0,8192,16384,24576,32768,40960,49152,32768))
    assert numeric.uniform_word_curve(table,4096)==dict(index=0,fraction=32768,value=4096,returned=4096)
    assert numeric.uniform_word_curve(table,65535)==dict(index=7,fraction=0,value=32768,returned=-32768)
