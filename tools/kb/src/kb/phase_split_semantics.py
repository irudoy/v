"""Independent low32 multiplication and exact natural splitter transfers."""

from kb import test_contract


def scalar(argument):
    if type(argument) is not int or not 0<=argument<=0xFFFFFFFF:
        raise ValueError('the splitter needs its explicit complete unsigned R4 input')
    product=(argument*6554)&0xFFFFFFFF;quotient=product//65536;ten=quotient*10
    remaining=(argument-ten)&0xFFFFFFFF
    return dict(product=product,quotient=quotient,ten=ten,remaining=remaining,remainder=remaining&255,exit_t=int(ten==0))


def evaluate(case,observed,result):
    expected=scalar(case['argument']);word=case['word']&65535;byte=case['byte']&65535
    before=observed['memory_before'][0];memory=bytearray(before)
    memory[word:word+2]=expected['quotient'].to_bytes(2,'big');memory[byte]=expected['remainder']
    registers=result['registers']
    scratch=(registers[2],registers[3],registers[4],registers[5],registers[6],registers[7],result['sr']&1,result['macl'])
    wanted_scratch=(expected['quotient'],6554,expected['remaining'],0x01000000+word,
        expected['ten'],0x01000000+byte,expected['exit_t'],observed['context'][17])
    if observed['memory_after']!=(bytes(memory),) or result['calls'] or scratch!=wanted_scratch:
        raise ValueError('the splitter differs from separate low32 integer, scratch, MACL and full RAM equations')
    wanted=[(0x28E7E,'read',0x28EA0,2,'199a'),
        (0x28E94,'write',0x01000000+word,2,expected['quotient'].to_bytes(2,'big').hex()),
        (0x28E98,'write',0x01000000+byte,1,bytes([expected['remainder']]).hex())]
    actual=[(row['site'],row['mode'],row['address'],row['width_bytes'],row['bytes'])
        for row in result['accesses'] if row['domain']=='ram' or row['site']==0x28E7E]
    if not test_contract.exact(actual,wanted):
        raise ValueError('the splitter changes its exact literal, pointer, width, direction or BT/S delay-slot store')
    return dict(index=case['index'],pair=case['pair'],count=expected['quotient'],remainder=expected['remainder'],
        output=(expected['quotient'],expected['remainder']),accesses=actual,exact_phase_normalization=True,
        native_geometry_inference=False,natural_caller_reachability=False,hardware_qualification=False)
