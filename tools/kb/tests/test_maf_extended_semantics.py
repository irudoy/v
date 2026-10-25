"""Literal existing stock vectors bind independent MAF equations and neighbors."""

import pytest

from kb import maf_extended_semantics as numeric


def set_word(memory, address, value):
    memory[address:address + 2] = (value & 65535).to_bytes(2, 'big')


def set_long(memory, address, value):
    memory[address:address + 4] = (value & 0xFFFFFFFF).to_bytes(4, 'big')


@pytest.mark.parametrize('previous,input,correction,expected',
    ((0, 200, 0x00180000, 100), (168, 200, 0x00180000, 168),
     (0, 1000, 0xFFFFFFFF, 54249), (0, 0, 0x00180000, 65436)))
def test_compensation_existing_literal_vectors(previous, input, correction, expected):
    memory = bytearray([0xA5]) * 65536
    memory[0x3976] = 2
    set_word(memory, 0x101E, input)
    set_word(memory, 0x1E4A, previous)
    set_long(memory, 0x399C, correction)
    result = numeric.compensation(1, bytes(memory), 335, 80)
    assert result['output'] == expected
    assert result['memory'][0x1E48:0x1E4A] == memory[0x1E48:0x1E4A]
    assert result['memory'][0x399C:0x39A0] == memory[0x399C:0x39A0]


@pytest.mark.parametrize('mode,coefficient,sample,coefficient_after,output',
    ((0, 0, 1023, 0x8000, 1024), (0, 0x7900, 1023, 0x7900, 968),
     (0, 0x8700, 1023, 0x8700, 1079), (8, 0, 1023, 0, 1),
     (8, 0xFFFF, 0xFFFF, 0xFFFF, 65535)))
def test_scaling_existing_guard_and_word_vectors(mode, coefficient, sample, coefficient_after, output):
    memory = bytearray([0xA5]) * 65536
    memory[0x4252] = mode
    set_word(memory, 0x4970, coefficient)
    set_word(memory, 0x1D64, sample)
    result = numeric.scaling(1, bytes(memory), bytes.fromhex('8779'), 0x8000)
    assert (result['coefficient'], result['output']) == (coefficient_after, output)
    assert result['memory'][0x101C:0x101E] == memory[0x101C:0x101E]


@pytest.mark.parametrize('mode,coefficient,raw,after,sample,scaled,output',(
    (0,0,1023,0x8000,255,255,255),(0,0x7900,1023,0x7900,255,241,241),
    (0,0x8700,1023,0x8700,255,268,255),(0,0x78FF,508,0x8000,127,127,127),
    (0,0x7900,508,0x7900,127,120,120),(0,0x8700,508,0x8700,127,133,133),
    (0,0x8701,508,0x8000,127,127,127),(8,0,1023,0,255,0,0),
    (8,0xFFFF,65535,0xFFFF,255,509,255),(8,0xFFFF,1024,0xFFFF,0,0,0),
    (8,0xFFFF,512,0xFFFF,128,255,255),(8,0xFFFF,516,0xFFFF,129,257,255),
    (8,0xC000,680,0xC000,170,255,255),(8,0xC000,684,0xC000,171,256,255),
    (8,0xC000,688,0xC000,172,258,255)))
def test_battery_has_independent_guard_byte_wrap_and_cap_boundaries_without_full_scale_increment(
        mode,coefficient,raw,after,sample,scaled,output):
    memory=bytearray([0xA5])*65536;memory[0x4252]=mode
    set_word(memory,0x4970,coefficient);set_word(memory,0x1D6E,raw)
    result=numeric.battery(bytes(memory),bytes.fromhex('8779'),0x8000)
    assert (result['coefficient'],result['sample'],result['scaled'],result['output'])==(after,sample,scaled,output)
    expected=bytearray(memory);set_word(expected,0x1FC4,raw);expected[0x1FC6]=sample
    set_word(expected,0x4970,after);expected[0x1188]=output
    assert result['memory']==bytes(expected)
    assert result['memory'][0x1D6E:0x1D70]==memory[0x1D6E:0x1D70]


@pytest.mark.parametrize('active,input,reference,fallback,output,base,correction',
    ((True, 1000, 0, 1193046, 5782, 5625, 131),
     (True, 1000, 1000, 1193046, 1027, 1000, 23),
     (False, 1000, 0, 1193046, 597023, 65535, 0),
     (False, 65535, 0, 0, 32767, 32767, 0),
     (False, 65535, 0, 1, 32768, 32768, 0)))
def test_contribution_existing_active_and_fallback_vectors(active, input, reference, fallback, output, base, correction):
    memory = bytearray([0xA5]) * 65536
    memory[0x2449] = memory[0x24B8] = memory[0x43CB] = 0
    memory[0x2462] = int(active)
    memory[0x1E34] = 2
    set_word(memory, 0x1DF2, input)
    set_word(memory, 0x1E0A, reference)
    set_word(memory, 0x1E1A, 0)
    set_word(memory, 0x1E1E, 0)
    set_word(memory, 0x1E32, 0)
    set_long(memory, 0x1E14, fallback)
    result = numeric.contribution(1, bytes(memory), bytes((77, 12, 255)), 45, 128)
    assert (result['output'], result['base'], result['correction']) == (output, base, correction)
    assert result['memory'][0x1DF8:0x1DFC] == memory[0x1DF8:0x1DFC]
    assert result['memory'][0x1E14:0x1E18] == memory[0x1E14:0x1E18]


@pytest.mark.parametrize('input,correction,auxiliary,output',
    ((0,0,0,0),(1,0,0,1),(0,0xFFFF,0,0),(0,0x8000,65535,32767),
     (0x7FFFFFFF,1,0,0),(0x80000000,0xFFFF,0,0x7FFFFFFF),
     (0xFFFFFFFF,1,0,0),(0xFFFFFFFF,0x8000,65535,32766)))
def test_bank_publication_uses_signed_word_and_modulo32_before_zero_clamp(input,correction,auxiliary,output):
    memory=bytearray([0xA5])*65536
    set_long(memory,0x1DFC,input)
    set_word(memory,0x1E2A,correction)
    set_word(memory,0x2368,auxiliary)
    result=numeric.bank_publication(1,bytes(memory))
    assert result['output']==output
    assert result['memory'][0x1050:0x1054]==output.to_bytes(4,'big')
    assert result['memory'][0x104C:0x1050]==memory[0x104C:0x1050]
    assert result['memory'][0x1DFC:0x1E00]==memory[0x1DFC:0x1E00]


@pytest.mark.parametrize('input',(0,1,0x7FFF,0x8000,0xFFFF))
def test_diagnostic_word_copy_keeps_all_bits_and_sibling_bank(input):
    memory=bytearray([0xA5])*65536
    set_word(memory,0x1D64,input)
    result=numeric.diagnostic_copy(0xF00DCA01,bytes(memory))
    assert result['output']==input
    assert result['memory'][0x1A40:0x1A42]==input.to_bytes(2,'big')
    assert result['memory'][0x1A3E:0x1A40]==memory[0x1A3E:0x1A40]
    assert result['memory'][0x1D64:0x1D66]==memory[0x1D64:0x1D66]


@pytest.mark.parametrize('initialized,bias,outputs',((0,80,(1000,2000)),(1,0,(1001,2000)),
    (2,0,(1000,2001)),(3,80,(1000,2000))))
def test_compensation_caller_retains_both_bank_inputs_and_ordered_initialization(initialized,bias,outputs):
    memory=bytearray([0xA5])*65536
    memory[0x3976]=0x80|initialized
    for bank,sample in enumerate((1000,2000)):
        set_word(memory,0x101C+bank*2,sample)
        set_word(memory,0x1E48+bank*2,0)
        set_long(memory,0x3998+bank*4,0)
    result=numeric.bank_call_sequence('compensation-caller',bytes(memory),
        {0x9586:bytes.fromhex('014f'),0x958C:bias.to_bytes(2,'big')})
    assert result['output']==outputs
    assert result['memory'][0x3976]==0x83
    assert result['steps'][0]['memory'][0x1E4A:0x1E4C]==bytes(2)
    assert result['steps'][1]['memory'][0x1E48:0x1E4A]==outputs[0].to_bytes(2,'big')
    assert result['memory'][0x101C:0x1020]==memory[0x101C:0x1020]


@pytest.mark.parametrize('mode,coefficient,reset',((0,0,True),(0,0x7900,False),
    (0,0x8700,False),(0,0x8701,True),(8,0,False)))
def test_scaling_caller_second_bank_consumes_the_first_banks_shared_coefficient_state(mode,coefficient,reset):
    memory=bytearray([0xA5])*65536
    memory[0x4252]=mode
    set_word(memory,0x4970,coefficient)
    set_word(memory,0x1D62,1023);set_word(memory,0x1D64,1)
    result=numeric.bank_call_sequence('scaling-caller',bytes(memory),
        {0x87F8:bytes.fromhex('8779'),0x92BE:bytes.fromhex('8000')})
    first,second=result['steps']
    assert first['reset'] is reset
    assert second['incoming_coefficient']==(0x8000 if reset else coefficient)
    assert second['reset'] is False
    assert second['memory'][0x101C:0x101E]==first['output'].to_bytes(2,'big')
    assert result['memory'][0x1D62:0x1D66]==memory[0x1D62:0x1D66]
    if reset:
        assert result['output']==(1024,1)
