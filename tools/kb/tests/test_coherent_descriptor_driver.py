"""Strict descriptor and original stock-primitive contracts, without execution."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tomllib

import pytest
import kb
from kb import repo

BASE=Path(__file__).parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return module

@pytest.fixture(scope='module')
def prepared():
    changes=pytest.MonkeyPatch()
    changes.syspath_prepend(str(repo.ROOT/'tools/sh-elf-run'))
    from kb import coherent_copy_matrix as matrix, coherent_copy_members as pins, coherent_copy_evidence as proof
    tool=load('coherent_capture_contract',repo.ROOT/'tools/sh-elf-run/coherent_snapshot_copy.py')
    image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    descriptor=tomllib.loads((repo.ROOT/'defs/JK08A.coherent-copy.toml').read_text())
    header=(repo.ROOT/'tools/sh-elf-run/coherent-copy-cases.h').read_bytes()
    yield matrix,pins,proof,tool,image,descriptor,header
    changes.undo()

def test_descriptor_binds_original_native_owners_and_exact_stock_bytes(prepared):
    matrix,pins,proof,tool,image,descriptor,header=prepared
    assert proof.validate_descriptor(descriptor,image,header) is descriptor
    assert len(pins.MEMBERS)==84
    assert sum(len(row['member']) for row in descriptor['window'])==84
    assert descriptor['matrix']==dict(cases=17228,feedback_cases=109,windows=15,
        header='tools/sh-elf-run/coherent-copy-cases.h',header_sha256=hashlib.sha256(header).hexdigest())
    tool.validate_header(header.decode(),descriptor)

@pytest.mark.parametrize('path,value',[
    (('schema',),True),(('id',),'coherent-copy-v1:other'),(('parent',),'other/fn'),
    (('window',0,'entry'),0x20f06),(('window',2,'length_bytes'),132),
    (('window',2,'entry_context','r12'),128),(('window',2,'read_ahead_bytes'),0),
    (('window',2,'end'),0x20f5c),(('window',2,'pool',0,'value'),0xffff1083),
    (('window',2,'code',1,'start'),0x22040),
    (('window',2,'member',0,'transfer_width_bits'),8),
    (('window',2,'member',0,'witness_width_bits'),True),
    (('window',2,'member',0,'declared_width'),'32'),
    (('window',2,'member',0,'declared_signed'),'signed'),
    (('window',2,'member',0,'direction'),'reader'),
    (('window',2,'member',0,'offset_bytes'),0),
    (('window',2,'member',0,'claim_sha256'),'0'*64),
    (('simulation','stack_return_offset'),28),
    (('matrix','cases'),12971),
    (('window',11,'function'),0x20dfe),
    (('window',11,'parent'),'coherent_snapshot/fn'),
    (('window',11,'member',0,'transfer_width_bits'),16),
    (('window',11,'member',0,'witness_width_bits'),32),
    (('window',13,'entry_context','r4'),0x22104),
])
def test_descriptor_refuses_changed_fact_context_or_typed_value(prepared,path,value):
    _,_,proof,_,image,descriptor,header=prepared
    changed=copy.deepcopy(descriptor);parent=changed
    for part in path[:-1]:parent=parent[part]
    assert parent[path[-1]]!=value or type(parent[path[-1]]) is not type(value)
    parent[path[-1]]=value
    with pytest.raises(ValueError):proof.validate_descriptor(changed,image,header)

def test_descriptor_refuses_changed_stock_and_duplicate_members(prepared):
    _,_,proof,_,image,descriptor,header=prepared
    changed=bytearray(image);changed[0x220e0]^=1
    with pytest.raises(ValueError,match='stock image'):proof.validate_descriptor(descriptor,changed,header)
    value=copy.deepcopy(descriptor);value['window'][0]['member']*=2
    with pytest.raises(ValueError):proof.validate_descriptor(value,image,header)


def test_two_parent_domains_and_longword_word_fields_are_explicit(prepared):
    matrix,pins,proof,_,image,descriptor,_=prepared
    assert descriptor['parents']==[dict(function=0x209d8,meaning='black-kudu/fn'),
                                   dict(function=0x20dfe,meaning='coherent_snapshot/fn')]
    window=next(row for row in descriptor['window'] if row['call']==0x20bd0)
    assert {row['declared_width'] for row in window['member']}=={'16'}
    assert {row['declared_signed'] for row in window['member']}=={'unsigned'}
    assert {row['witness_width_bits'] for row in window['member']}=={16}
    assert {row['transfer_width_bits'] for row in window['member']}=={32}
    assert {row['offset_bytes'] for row in window['member']}=={0,2}
    pointer=next(pool for pool in window['pool'] if pool['address']==0x22170)
    assert pointer['value']==0x2213e
    assert image[0x22170:0x22174]==pointer['value'].to_bytes(4,'big')

@pytest.mark.parametrize('suffix',['\n#define EARLY_ONLY 1\n','\n/* unrelated bytes */\n'])
def test_consumed_header_requires_exact_complete_canonical_bytes(prepared,suffix):
    _,_,_,tool,_,descriptor,header=prepared
    with pytest.raises(ValueError,match='complete canonical bytes'):
        tool.validate_header(header.decode()+suffix,descriptor)

@pytest.mark.parametrize('index',range(15))
def test_real_stock_fixture_and_boundary_preserve_all_tested_instruction_bytes(prepared,index):
    matrix,_,proof,tool,image,descriptor,_=prepared
    import verify_stock_code as stock
    window=matrix.WINDOWS[index];row=descriptor['window'][index]
    region=tool.region(window,row)
    assert region.code_spans==proof.code_spans(window)
    assert region.cases==len(matrix.cases(window))
    assert region.end==window.call+4 and region.return_register==7
    assert stock.return_stub(region)==bytes.fromhex('57f6472a000b0009')
    actual=stock.build_fixture(region,image)
    expected=bytearray(image)
    for pool in row['pool']:
        address=pool['address'];expected[address:address+4]=matrix.alias(pool['value']).to_bytes(4,'big')
    expected[region.end:region.end+8]=bytes.fromhex('57f6472a000b0009')
    assert actual==expected
    for start,end in region.code_spans:assert actual[start:end]==image[start:end]
    assert len(row['pool'])*4<=32
    assert tool.region(window,row,early=True).cases==len(proof.early_indices(window))

def test_incomplete_and_duplicate_actual_capture_is_refused(prepared):
    matrix,_,_,tool,_,descriptor,_=prepared
    window=matrix.WINDOWS[0];row=descriptor['window'][0]
    with pytest.raises(ValueError,match='omits or duplicates'):
        tool.observe('',window,row,early=True)
    with pytest.raises(ValueError,match='duplicate coherent observation key'):
        tool.observe(tool.PREFIX+'{"index":0,"index":1}\n',window,row,early=True)

