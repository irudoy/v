"""Exact fixture, published counts and complete raw-input refusal controls."""
from copy import deepcopy
from pathlib import Path
import re
import pytest
from kb import repo
from kb import request_limit_normalization_contract as contract, request_limit_normalization_matrix as matrix

def case():return dict(deepcopy(matrix.DEFAULTS),index=0,kind='complete-source-contract')

def test_published_counts_and_domain_read_the_executed_descriptor():
    source=contract.descriptor(repo.ROOT)
    text=(Path(repo.ROOT)/'defs/JK08A.request-limit-normalization.md').read_text()
    actual=(sum((r['end']-r['start'])//2 for r in source['unit']['code']),sum(r['end']-r['start'] for r in source['unit']['code']),len(source['unit']['code']))
    found=re.search(r'binds (\d+) stock instructions, (\d+) instruction bytes and (\d+) complete source bodies',text)
    assert found and tuple(map(int,found.groups()))==actual==(515,1030,7)
    found=re.search(r'binds (\d+) literal pools, (\d+) four-byte RAM aliases and (\d+) calibration spans',text)
    assert found and tuple(map(int,found.groups()))==(len(source['unit']['pools']),len(source['unit']['aliases']),len(source['controlled_calibration']))
    assert source['entries']==[0x7AE80] and (source['context_bytes'],source['frame_bytes'],source['frame_prefix'])==(80,192,160)
    found=re.search(r'The normalization cap is (\d+)',text)
    cap=int(next(r for r in source['unit']['pools'] if r['address']==0x7B05A)['stock_hex'],16)
    assert found and int(found[1])==source['actual_normalization']['cap']==cap==800
    controls={r['name']:r for r in source['control_blobs']}
    found=re.search(r'Stock ROM8\[83C1\]=0x([0-9a-fA-F]+)',text)
    assert found and int(found[1],16)==int(controls['mode_83c1']['stock_hex'],16)==0x2C
    found=re.search(r'bind (\d+) physical curve words',text)
    curve_bytes=sum(r['size'] for r in source['input_blobs'] if r['name'] in ('upper','lower'))+controls['lower_guard']['size']
    assert found and int(found[1])==curve_bytes//2==33

def test_complete_stock_fixture_changes_only_declared_four_byte_pointer_pools():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image)
    allowed={at for r in aliases for at in range(r['address'],r['address']+4)}
    assert {i for i,(a,b) in enumerate(zip(image,fixture)) if a!=b}<=allowed
    for r in source['unit']['code']:assert fixture[r['start']:r['end']]==image[r['start']:r['end']]
    changed=bytearray(image);changed[0x7AE96]^=1
    with pytest.raises(ValueError):contract.independent_fixture(source,bytes(changed))

@pytest.mark.parametrize('fault',('bool-word','wide-mode','bool-guard','short-curve','wide-axis','short-context','invalid-SR','supplied-result'))
def test_raw_input_contract_refuses_truncation_type_loss_or_expected_outputs(fault):
    value=case()
    if fault=='bool-word':value['word_338c']=True
    elif fault=='wide-mode':value['mode_83c1']=256
    elif fault=='bool-guard':value['lower_guard']=False
    elif fault=='short-curve':value['upper'].pop()
    elif fault=='wide-axis':value['axis'][15]=65536
    elif fault=='short-context':value['context'].pop()
    elif fault=='invalid-SR':value['context'][18]=2
    else:value['expected_normalized']=[800]*3
    with pytest.raises(ValueError):matrix.require_case(value)

def test_private_header_contains_complete_inputs_without_expected_outputs():
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    text=matrix.header(dict(source=source,cases=[case()]),image).decode()
    assert 'uint32_t ram[16]' in text and 'struct context context' in text
    assert not any(word in text for word in ('expected','normalized','quotient','final_word'))
