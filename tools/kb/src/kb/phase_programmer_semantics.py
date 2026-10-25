"""Separate offset multiply, real helper arguments and exact physical transfers."""

from kb import phase_split_semantics as split,test_contract


def scalar(period,remainder):
    if type(period) is not int or type(remainder) is not int or not 0<=period<=65535 or not 0<=remainder<=255:
        raise ValueError('the phase programmer needs explicit unsigned word and byte inputs')
    product=period*remainder
    return dict(argument=product,**split.scalar(product))


def evaluate(case,observed,result):
    expected=scalar(case['period'],case['remainder']);memory=bytearray(observed['memory_before'][0])
    memory[0x16C2:0x16C4]=expected['quotient'].to_bytes(2,'big');memory[0x166C]=expected['remainder']
    registers=result['registers']
    scratch=tuple(registers[index] for index in (0,2,3,4,5,6,7,13))+(result['sr']&1,result['macl'])
    wanted=(0x06AF,expected['quotient'],6554,expected['remaining'],0x010016C2,
        expected['ten'],observed['continuation'],0x0100128C,expected['exit_t'],expected['argument'])
    if observed['memory_after']!=(bytes(memory),) or not test_contract.exact(scratch,wanted):
        raise ValueError('the phase programmer differs from separate low32 scalar, scratch, MACL or complete RAM equations')
    if len(result['calls'])!=1:
        raise ValueError('the phase programmer needs its one actual reciprocal helper call')
    call=result['calls'][0];entry=call['entry']
    if (tuple(call[key] for key in ('site','target','return_address','sp'))!=(0x2B6F4,0x28E7C,0x2B6F8,observed['sp'])
            or tuple(entry['registers'][index] for index in (4,5,6))!=(expected['argument'],0x010016C2,0x0100166C)
            or (entry['sp'],entry['pr'],entry['macl'])!=(observed['sp'],0x2B6F8,expected['argument'])):
        raise ValueError('the phase programmer changes the real helper target, delay-slot arguments, SP, PR or MACL')
    wanted_accesses=[
        (0x2B6D4,'read',0x2B874,4,'01001ff4'),
        (0x2B6D6,'read',0x2B760,2,'02c8'),
        (0x2B6D8,'read',0x2B864,4,'0100128c'),
        (0x2B6DA,'read',0x010022BC,2,case['period'].to_bytes(2,'big').hex()),
        (0x2B6DC,'read',0x2B75E,2,'06af'),
        (0x2B6E0,'read',0x0100193B,1,bytes([case['remainder']]).hex()),
        (0x2B6E4,'read',0x2B762,2,'0436'),
        (0x2B6F2,'read',0x2B86C,4,'00028e7c'),
        (0x28E7E,'read',0x28EA0,2,'199a'),
        (0x28E94,'write',0x010016C2,2,expected['quotient'].to_bytes(2,'big').hex()),
        (0x28E98,'write',0x0100166C,1,bytes([expected['remainder']]).hex())]
    actual=[tuple(row[key] for key in ('site','mode','address','width_bytes','bytes'))
        for row in result['accesses'] if row['domain'] in ('ram','rom')]
    if not test_contract.exact(actual,wanted_accesses):
        raise ValueError('the phase programmer changes an exact physical input, literal or unconditional delay-slot output')
    returns=[(row['site'],row['target']) for row in result['branches'] if row['kind']=='return']
    if returns!=[(0x28E9A,0x2B6F8),(0x2B6FC,observed['continuation'])]:
        raise ValueError('the phase programmer changes its natural child return or separate observing return')
    return dict(index=case['index'],output=(expected['quotient'],expected['remainder']),
        accesses=actual,exact_phase_programmer=True,count_guard_admission=False,
        natural_caller_reachability=False,hardware_qualification=False)
