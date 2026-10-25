"""Conditional array paths retain exact inputs, element effects and native facts."""

import json

import pytest

from kb import counter_array_contract as contract,counter_array_matrix as matrix
from kb import counter_array_capture_evidence as proof,counter_access_contract as owning,repo


def test_exact_three_stock_windows_keep_code_and_only_declared_pointers_and_returns():
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(declared,image);restored=bytearray(fixture)
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    for row in contract.RETURNS:restored[row['address']:row['address']+4]=image[row['address']:row['address']+4]
    assert bytes(restored)==image and len(declared['window'])==3 and len(declared['array'])==5
    assert [(row['count'],row['width_bytes']) for row in declared['array']]==[(138,1),(10,2),(195,1),(244,1),(7,1)]
    for row in contract.WINDOWS:assert fixture[row['start']:row['end']]==image[row['start']:row['end']]


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_source_never_admits_cadence_entry_width_units_or_hardware(tmp_path,flag):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    path.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_native_nine_writers_keep_unset_width_signedness_and_complete_documents():
    rows=owning.descriptor(repo.ROOT)['reference']
    assert len(rows)==9 and len({row['owner'] for row in rows})==9
    for index,row in enumerate(rows):
        assert row['function']==(0x2040C if index<8 else 0x208F8)
        assert row['direction']=='writer' and row['width_bytes']==1
        assert (row['declared_width'],row['declared_signed'])==('unset','unset')
        before,after=json.loads(row['original_native_json']),json.loads(row['proposed_native_json'])
        assert before.get('ledger')==after.get('ledger') and before['symbol']==after['symbol']


@pytest.mark.parametrize('index',range(3))
@pytest.mark.parametrize('value',matrix.SEEDS)
def test_array_equations_saturate_each_byte_word_and_preserve_all_other_ram(index,value):
    window=contract.WINDOWS[index];before=value.to_bytes(2,'big')*32768
    after,accesses,branches,steps,arrays=proof.array_equation(window,before)
    assert steps<16384
    wanted=bytearray(before)
    for array in contract.ARRAYS:
        if array['entry']!=window['start']:continue
        width=array['width_bytes'];first=array['first']&65535
        for number in range(array['count']):
            address=first+number*width;incoming=int.from_bytes(before[address:address+width],'big')
            wanted[address:address+width]=max(0,incoming-1).to_bytes(width,'big')
    assert after==bytes(wanted)
    assert len(arrays)==(3 if index==0 else 1)
    assert all(row[3] in (1,2) for row in accesses)
    assert branches


def test_zero_has_one_read_without_store_and_one_has_repeat_read_and_store():
    window=contract.WINDOWS[0]
    _,zero,_,_,_=proof.array_equation(window,bytes(65536))
    _,one,_,_,_=proof.array_equation(window,b'\x01\x01'*32768)
    assert all(row[1]=='read' for row in zero)
    array=contract.ARRAYS[0];address=matrix.RAM_BASE+(array['first']&65535)
    assert [row[:4] for row in one[:3]]==[(array['read'],'read',address,1),
        (array['repeat_read'],'read',address,1),(array['store'],'write',address,1)]
    assert one[0][4]==one[1][4]=='01' and one[2][4]=='00'


def test_shared_driver_keeps_byte_seeds_and_separates_stream_and_word_pattern_inputs():
    from kb import ram_initialization_contract,ram_initialization_matrix,ram_initialization_capture_evidence
    init=ram_initialization_contract.descriptor(repo.ROOT)
    arrays=contract.descriptor(repo.ROOT)
    init_case=ram_initialization_matrix.cases(init,b'')[0];array_case=matrix.cases(arrays,b'')[1]
    assert ram_initialization_matrix.memory(init_case)==bytes([init_case['seed']])*65536
    expected=bytearray([1])*65536
    expected[0x2604:0x2618]=b'\x00\x01'*10
    assert matrix.memory(array_case)==bytes(expected)
    init_declared=dict(source=init,cases=list(ram_initialization_matrix.cases(init,b'')))
    array_declared=dict(source=arrays,cases=list(matrix.cases(arrays,b'')))
    first=ram_initialization_capture_evidence.header(init_declared,b'').decode()
    second=proof.header(array_declared,b'').decode()
    assert '#define RAM_INITIALIZATION_WORD_SEED 0' in first
    assert '#define RAM_INITIALIZATION_WORD_SEED 1' in second
    assert ram_initialization_capture_evidence.PREFIX in first and proof.PREFIX in second
    assert proof.PREFIX not in first and ram_initialization_capture_evidence.PREFIX not in second
    from kb.test_stock_capture import tool
    init_producer=tool(repo.ROOT,'ram_initialization_capture.py','_kb_init_shared_header_source')
    array_producer=tool(repo.ROOT,'counter_array_capture.py','_kb_counter_shared_header_source')
    assert init_producer.header(init_declared,b'')==first.encode()
    assert array_producer.header(array_declared,b'')==second.encode()


def test_documented_claim_counts_follow_the_executed_native_descriptor():
    rows=owning.descriptor(repo.ROOT)['reference'];text=(repo.ROOT/'defs/JK08A.counter-arrays.md').read_text()
    assert len(rows)==len({row['owner'] for row in rows})==9
    assert 'nine original writer' in text and 'nine complete native' in text
    for row in contract.ARRAYS:
        if row['width_bytes']==2:
            assert row['count']==10 and 'ten words' in text
        else:assert f'{row["count"]} bytes' in text
