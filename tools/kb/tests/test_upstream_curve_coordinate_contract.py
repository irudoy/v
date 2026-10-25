"""Descriptor-bound published facts and complete raw source/consumer inputs."""
from copy import deepcopy
import hashlib
import re
import pytest
from kb import repo
from kb import upstream_curve_coordinate_contract as contract,upstream_curve_coordinate_matrix as matrix
from kb import upstream_curve_coordinate_transfers as transfers


def case():return dict(deepcopy(matrix.DEFAULTS),index=0,kind='controlled-upstream-coordinate-entry')


def test_published_counts_read_the_executed_descriptor():
    source=contract.descriptor(repo.ROOT);text=(repo.ROOT/'defs/JK08A.upstream-curve-coordinate.md').read_text()
    actual=(sum((r['end']-r['start'])//2 for r in source['unit']['code']),len(source['entries']),
        len(source['unit']['code']),len(source['unit']['pools']),len(source['unit']['aliases']),len(source['controlled_calibration']))
    pattern=r'binds (\d+) stock instructions in\s*(\d+) actual entry path and (\d+) spans, (\d+) literal pools, (\d+) four-byte RAM pointer\s*aliases and (\d+) calibration spans'
    assert tuple(map(int,re.search(pattern,text).groups()))==actual==(586,1,9,30,3,39)
    root=sum((r['end']-r['start'])//2 for r in source['unit']['code'] if 0xB7A3C<=r['start']<0xB7B98)
    assert int(re.search(r'entry has (\d+) instructions',text)[1])==root==168
    assert int(re.search(r'(\d+) stock entry paths',text)[1])==len(source['stock_entry_paths'])==8
    assert int(re.search(r'(\d+) raw input blobs',text)[1])==len(source['input_blobs'])==4
    assert int(re.search(r'containing (\d+) input bytes',text)[1])==sum(r['size'] for r in source['input_blobs'])==100
    assert int(re.search(r'(\d+) raw ROM controls',text)[1])==len(source['control_blobs'])==5
    assert int(re.search(r'containing (\d+) control bytes',text)[1])==sum(r['size'] for r in source['control_blobs'])==5
    for phrase,key,wanted in (('byte context','context_bytes',80),('byte observer','observation_bytes',572),('byte frame','frame_bytes',192)):
        assert int(re.search(r'(\d+)-'+phrase,text)[1])==source[key]==wanted
    assert int(re.search(r'(\d+) independent context',text)[1])==source['independent_context_fields']==20
    assert int(re.search(r'All (\d+) RAM bytes',text)[1])==source['complete_initial_final_RAM_bytes']==65536
    assert int(re.search(r'allocates (\d+) stack bytes',text)[1])==source['outer_stack_bytes']==32
    assert int(re.search(r'(\d+) feasible instructions',text)[1])==len(transfers.FEASIBLE_SITES)==485
    assert int(re.search(r'(\d+) infeasible\s*instructions',text)[1])==len(transfers.INFEASIBLE_SITES)==101
    assert transfers.EXACT_SITES==transfers.FEASIBLE_SITES|transfers.INFEASIBLE_SITES


def test_actual_source_return_consumer_delay_output_and_constants_read_the_descriptor():
    source=contract.descriptor(repo.ROOT);inputs={r['name']:r for r in source['input_blobs']}
    assert [(inputs[n]['address'],inputs[n]['size']) for n in ('source_curve','source_axis','output_curve','output_axis')]==[
        (0x14E42,18),(0x13BB8,16),(0x151F2,34),(0x13BF8,32)]
    assert source['actual_source_call']['site']==0xB7AAC and source['actual_source_call']['target']==0x264CC
    assert source['actual_source_return']==dict(site=0xB7AB0,source_register=0,target_register=2)
    assert source['actual_source_extension']==dict(site=0xB7ACA,source_register=2,target_register=6,width_bits=16)
    assert source['actual_consumer_call']==dict(site=0xB7B14,delay_slot=0xB7B16,target=0x264F8,base=0x151F2,axis=0x13BF8,coordinate_register=6)
    assert source['actual_final_output']==dict(address=0xFFFF3228,width_bytes=4,site=0xB7B84,register=2)
    assert source['complete_incoming_argument']['full_word_read_site']==0xB7A58
    assert source['complete_incoming_argument']['lowbyte_SP_delta']==3
    assert source['full_GBR_ROM_rebase']==dict(address=0x8A30,site=0xB7A4C,restore_site=0xB7B88)
    assert source['primitive_has_no_fixed_ROM14E42_read'] is True
    aliases={r['address'] for r in source['unit']['aliases']}
    assert {r['address'] for r in source['signed_numeric_pool_constants']}=={0xB7C04,0xB7C20}
    assert aliases.isdisjoint((0xB7C04,0xB7C20))


def test_fixture_retains_instructions_and_only_actual_RAM_pointer_aliases():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes();fixture,aliases=contract.independent_fixture(source,image)
    assert {i for i,(a,z) in enumerate(zip(image,fixture)) if a!=z}<={i for r in aliases for i in range(r['address'],r['address']+4)}
    for r in source['unit']['code']:assert fixture[r['start']:r['end']]==image[r['start']:r['end']]
    for r in source['signed_numeric_pool_constants']:assert fixture[r['address']:r['address']+4].hex()==r['stock_hex']
    changed=bytearray(image);changed[contract.ENTRY]^=1
    with pytest.raises(ValueError):contract.independent_fixture(source,bytes(changed))


@pytest.mark.parametrize('fault',('wide-control','wide-source','wide-output','wide-prior','bool-control','short-context','short-source','short-axis','bad-SR','supplied-R6'))
def test_raw_inputs_refuse_narrowing_missing_guards_and_supplied_coordinates(fault):
    value=case()
    if fault=='wide-control':value['rom_8832']=256
    elif fault=='wide-source':value['source_curve'][0]=65536
    elif fault=='wide-output':value['output_curve'][-1]=65536
    elif fault=='wide-prior':value['prior_3228']=0x100000000
    elif fault=='bool-control':value['rom_8a30']=True
    elif fault=='short-context':value['context'].pop()
    elif fault=='short-source':value['source_curve'].pop()
    elif fault=='short-axis':value['output_axis'].pop()
    elif fault=='bad-SR':value['context'][18]=2
    else:value['supplied_R6']=1
    with pytest.raises(ValueError):matrix.require_case(value)


def test_complete_input_domains_and_full_existing_same_primary_originals():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes();rows=matrix.cases(source,image)
    assert rows and all(set(r)=={*matrix.WIDTHS,*matrix.ARRAYS,'index','kind'} for r in rows)
    assert {r['context'][19]&255 for r in rows}==set(range(256))
    assert {r['context'][5]&255 for r in rows}==set(range(256))
    for name in ('rom_8a34','rom_8a35','rom_8a36'):assert {r[name] for r in rows}==set(range(256))
    raw=matrix.header(dict(source=source,cases=[case()]),image).decode()
    assert 'struct context context' in raw and '\\n' not in raw and '\n' in raw
    assert 'supplied_R6' not in raw and 'expected_3228' not in raw
    assert source['full_existing_same_primary_originals']==['word_interp_caller_withdrawal_paths','division_callees_paths']
    for name,wanted in source['reused_source_sha256'].items():assert hashlib.sha256((repo.ROOT/name).read_bytes()).hexdigest()==wanted
