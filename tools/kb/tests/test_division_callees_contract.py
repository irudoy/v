"""Exact helper code, quotient limits, fault store and independent signed initialization."""

import pytest
from kb import repo,byte_surface_equations as state
from kb import division_callees_contract as contract,division_callees_semantics as numeric


def test_independent_division_fixture_preserves_all_stock_instructions_and_only_declared_fault_aliases():
    declared=contract.descriptor(repo.ROOT)
    image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(declared,image)
    restored=bytearray(fixture)
    assert {row['address'] for row in aliases}=={0x21CD8,0x21DC8}
    for row in aliases:
        assert row['original']==0xFFFF9818 and row['alias']==0x01009818
        restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert bytes(restored)==image
    for start,end in contract.SPANS:assert fixture[start:end]==image[start:end]


@pytest.mark.parametrize('fault',(*contract.FLAGS,'signed-entry','fault-code','fault-alias'))
def test_direct_helper_descriptor_refuses_caller_inference_or_changed_physical_contract(tmp_path,fault):
    original=(repo.ROOT/contract.DESCRIPTOR).read_text()
    if fault in contract.FLAGS:text=original.replace(fault+' = false',fault+' = true',1)
    elif fault=='signed-entry':text=original.replace('function_entries = [0x21bbc,0x21ce0]',
        'function_entries = [0x21ce0,0x21bbc]',1)
    elif fault=='fault-code':text=original.replace('stock_value = 0x0000044e','stock_value = 0x0000044f',1)
    else:text=original.replace('stock_value = 0xffff9818','stock_value = 0xffff981c',1)
    assert text!=original
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True);path.write_text(text)
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('kind,divisor,dividend,expected',(
    ('signed',2,0xFFFFFFFF,0),('signed',2,0xFFFFFFFD,0xFFFFFFFF),
    ('signed',0xFFFFFFFF,0x80000000,0x80000000),('signed',1,0x80000000,0x80000000),
    ('signed',0x80000000,0x80000000,1),('unsigned',1,0xFFFFFFFF,0xFFFFFFFF),
    ('unsigned',0x80000000,0xFFFFFFFF,1),('signed',0,0xFFFFFFFF,0),('unsigned',0,0xFFFFFFFF,0)))
def test_separate_quotient_equation_keeps_truncation_wrap_and_zero_contract(kind,divisor,dividend,expected):
    assert numeric.quotient(kind,divisor,dividend)==expected


@pytest.mark.parametrize('divisor',(0,1,0x80000000,0xFFFFFFFF))
def test_only_zero_divisor_changes_the_exact_fault_word(divisor):
    memory=bytes([0xA5])*65536
    expected=bytearray(memory)
    if divisor==0:expected[0x9818:0x981C]=bytes.fromhex('0000044e')
    assert numeric.memory_after(memory,divisor)==bytes(expected)


@pytest.mark.parametrize('divisor,dividend,expected',(
    (0,0,0),(0x80000000,0,0x201),(0,0x80000000,0x101),(0x80000000,0x80000000,0x300)))
def test_DIV0S_normative_sign_pairs_preserve_other_SR_bits(divisor,dividend,expected):
    registers=[0]*15;registers[0:2]=[divisor,dividend]
    context=(*registers,0x12344321,0x13579BDF,0x2468ACE0,0x3F1,0xA1B2C3D4)
    result=state.execute({'entry':[{'start':0,'end':2}]},bytes.fromhex('2107'),context,
        bytes(65536),bytes(192),0x02000000,2,0,0x3F1)
    assert result['sr']==0xF0|expected
    assert result['registers']==tuple(registers)
    assert result['ram']==bytes(65536) and result['frame']==bytes(192)


def test_documented_entry_fault_word_and_manual_identity_bind_to_executed_sources():
    text=(repo.ROOT/'defs/JK08A.division-callees.md').read_text()
    declared=contract.descriptor(repo.ROOT)
    for entry in declared['function_entries']:assert f'`{entry:08X}`' in text
    assert '`FFFF9818`' in text and '`0000044E`' in text
    assert state.ISA_REFERENCE_ID in text and state.ISA_REFERENCE in text


def test_call_argument_snapshot_follows_the_actual_STS_MACL_delay_slot():
    fixture=bytes.fromhex('440b011a00000000000b0009')
    registers=[0]*15;registers[1]=0x12345678;registers[4]=8
    context=(*registers,0x12344321,0x13579BDF,0x2468ACE0,0,0xA1B2C3D4)
    source={'entry':[{'start':0,'end':4},{'start':8,'end':12}]}
    result=state.execute(source,fixture,context,bytes(65536),bytes(192),0x02000000,4,0,0)
    call,=result['calls']
    assert call['registers'][1]==0x12345678
    assert call['entry']['registers'][1]==0x2468ACE0
    assert call['entry']['sp']==0x02000000 and call['entry']['pr']==4
