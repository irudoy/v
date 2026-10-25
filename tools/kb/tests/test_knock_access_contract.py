"""Separate knock fixture declarations and independent scalar boundaries."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import copy_evidence,copy_witness,ignition_literal_evidence,repo,test_contract
from kb import knock_access_unit_contract as units,knock_access_matrix as matrix
from kb import knock_access_contract as owning,knock_access_semantics as numeric


def test_four_stock_units_keep_adjacent_returns_in_separate_fixtures():
    image=repo.images()['JK08A'].path.read_bytes();fixtures=[]
    for kind in matrix.KINDS:
        declared=units.selection(repo.ROOT,kind);unit=declared['unit'][0]
        fixture,aliases=units.independent_fixture(declared,image);fixtures.append(fixture)
        for row in unit['code']:assert fixture[row['start']:row['end']]==image[row['start']:row['end']]
        assert len(aliases)==len(unit['aliases'])
        assert bool(unit['boundary'])==(kind!='threshold')
        for row in unit['boundary']:
            assert fixture[row['address']:row['address']+8].hex()=='57f6472a000b0009'
            assert not any(code['start']<=row['address']<code['end'] for code in unit['code'])
    assert len({hashlib.sha256(value).hexdigest() for value in fixtures})==4
    with pytest.raises(ValueError):units.independent_fixture(units.descriptor(repo.ROOT),image)


def test_a_return_inside_tested_knock_instructions_is_refused():
    image=repo.images()['JK08A'].path.read_bytes();declared=units.selection(repo.ROOT,'metric')
    declared['unit'][0]['boundary'][0]['address']=0x49D88
    with pytest.raises(ValueError):units.independent_fixture(declared,image)


@pytest.mark.parametrize('kind',matrix.KINDS)
def test_old_expected_columns_cannot_supply_new_raw_inputs(tmp_path,kind):
    source=matrix.INPUT_SOURCES[matrix.KINDS.index(kind)]
    original=(repo.ROOT/source).read_text();before=matrix.inputs(repo.ROOT,kind)
    text=original
    arrays={'normalization':'normalization_cases','metric':'metric_cases','threshold':'accessor_cases','comparison':'comparison_cases'}
    # Every literal row is changed only beyond the explicit input columns.
    rows=matrix.source_prefix(original,arrays[kind]);changed=[]
    inputs={'normalization':9,'metric':8,'threshold':4,'comparison':8}[kind]
    for row in rows:
        value=deepcopy(row)
        for index in range(inputs,len(value)):value[index]=0 if type(value[index]) is int else [0]*len(value[index])
        changed.append('{'+','.join(json.dumps(item).replace('[','{').replace(']','}') for item in value)+'},')
    at=text.index(arrays[kind]+'[]');start=text.index('{',at)+1
    text=text[:start]+'\n'+'\n'.join(changed)+'\n};\n'
    path=tmp_path/source;path.parent.mkdir(parents=True);path.write_text(text)
    assert test_contract.exact(matrix.inputs(tmp_path,kind),before)


def test_every_raw_and_owning_descriptor_and_arithmetic_source_is_bound_by_both_primary_paths():
    paths=(units.DESCRIPTOR,owning.DESCRIPTOR,*numeric.ARITHMETIC_SOURCES)
    producer=copy_witness.provenance(repo.ROOT);consumer=ignition_literal_evidence.execution_inputs(repo.ROOT)
    for path in paths:
        digest=hashlib.sha256((repo.ROOT/path).read_bytes()).hexdigest()
        assert path in copy_evidence.EXECUTION_FILES
        assert producer[path]==consumer[path]==digest


def test_eight_claims_preserve_seven_grouped_owners_and_existing_types():
    rows=owning.descriptor(repo.ROOT)['reference']
    assert len(rows)==8 and len({row['owner'] for row in rows})==7
    expected={'amorphous-bird/tbl':(None,None),'laughing-caterpillar/axis':(None,None),
        'knock_metric_sum/ram':(32,True),'knock_metric_base/ram':(32,False),
        'knock_signed_metric_base/ram':(32,True),'knock_threshold_base/ram':(16,False),
        'knock_normalized_cache/ram':(16,False)}
    for row in rows:assert (owning.native_type(row,'width'),owning.native_type(row,'signed'))==expected[row['owner']]
    table=[row for row in rows if row['owner']=='amorphous-bird/tbl']
    assert len(table)==2 and table[0]['proposed_native_json']==table[1]['proposed_native_json']
    assert {tuple(row['sites']) for row in table}=={(0x26510,)}
    assert not hasattr(owning,'RECEIPT')


def stock_scalar_input():
    memory=bytearray(65536);memory[0x11DE]=1;memory[0x2143]=6
    calibrations={0x8B3D:b'\x82',0x8618:b'\0',0x8870:b'\x03',
        0x86A7:b'\x80',0x8694:b'\x80',0x86AC:b'\x80'}
    return memory,calibrations


def test_scalar_metric_word_differences_signed_sum_and_biased_outputs_have_literal_boundaries():
    memory,cal=stock_scalar_input();numeric.put(memory,0x20C2,2,1)
    result=numeric.metric(bytes(memory),cal,0)
    assert (result['total'],result['scaled'],result['biased'])==(1,1,0x80000001)
    numeric.put(memory,0x20C2,2,0);numeric.put(memory,0x2178,2,1);cal[0x8870]=b'\x08'
    result=numeric.metric(bytes(memory),cal,0)
    assert (result['total'],result['scaled'],result['biased'])==(0xFFFFFFFF,0xFFFFFFFF,0x7FFFFFFF)
    cal.update({at:b'\xff' for at in (0x86A7,0x8694,0x86AC)})
    for total,scaled,biased in ((0x80000000,0x80000000,0),(0x7FFFFFFF,0x7FFFFFFF,0xFFFFFFFF)):
        numeric.put(memory,0x2274,4,total);result=numeric.metric(bytes(memory),cal,2)
        assert (result['scaled'],result['biased'])==(scaled,biased)


def test_scalar_axis_and_table_alternatives_and_strict_comparison_use_literal_boundaries():
    memory,cal=stock_scalar_input();numeric.put(memory,0x11F4,2,33)
    cal[0x15340]=b''.join((32*(index+1)).to_bytes(2,'big') for index in range(16))
    table=bytearray(194);numeric.put(table,0,2,1000);numeric.put(table,2,2,2000);cal[0x1108E]=bytes(table)
    assert numeric.lookup(bytes(memory),cal)['threshold']==1031
    axis=bytearray(cal[0x15340]);numeric.put(axis,0,2,34);cal[0x15340]=bytes(axis)
    assert numeric.lookup(bytes(memory),cal)['threshold']==1000
    numeric.put(memory,0x11F4,2,32)
    for metric,exceeded in ((0x800003E7,False),(0x800003E8,False),(0x800003E9,True)):
        numeric.put(memory,0x21D8,4,metric)
        assert numeric.lookup(bytes(memory),cal,True)['exceeded'] is exceeded
