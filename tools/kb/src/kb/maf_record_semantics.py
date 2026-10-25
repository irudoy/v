"""Separate record-byte predicate, exact member access and summary-bit equations."""

from kb import test_contract


def scalar(argument,flags,status,caller):
    if (type(argument) is not int or not 0<=argument<=0xFFFFFFFF
            or type(flags) is not int or not 0<=flags<=255
            or type(status) is not int or not 0<=status<=255 or type(caller) is not bool):
        raise ValueError('the record reader needs complete typed argument and byte inputs')
    index=argument&65535
    if index not in (0x129,0xFFFF) or caller and argument!=0x129:
        raise ValueError('the record reader changes its explicitly selected index premise')
    bit=0 if index==0xFFFF else (flags>>7)&1
    output=((status&0x7F)|(bit<<7)) if caller else status
    return dict(bit=bit,exit_t=1-bit,register=0 if caller else bit,status=output,sentinel=index==0xFFFF)


def evaluate(case,observed,result):
    caller=case['entry']==0x3C3C6;value=scalar(case['argument'],case['flags'],case['status'],caller)
    memory=bytearray(observed['memory_before'][0])
    if caller:memory[0x2449]=value['status']
    if (observed['memory_after']!=(bytes(memory),) or result['registers'][0]!=value['register']
            or result['registers'][2]!=value['bit'] or result['sr']&1!=value['exit_t']
            or (result['macl'],result['mach'],result['gbr'])!=tuple(observed['context'][index] for index in (17,16,15))):
        raise ValueError('the record reader differs from separate byte predicate, status, scratch or complete RAM equations')
    if caller:
        if len(result['calls'])!=1:raise ValueError('the record coordinator needs its one actual predicate call')
        call=result['calls'][0];entry=call['entry']
        if (tuple(call[key] for key in ('site','target','return_address','sp'))!=(0x3C3CA,0x25E20,0x3C3CE,observed['sp'])
                or entry['registers'][4]!=0x129 or (entry['sp'],entry['pr'],entry['gbr'])!=(observed['sp'],0x3C3CE,0x01002449)):
            raise ValueError('the record coordinator changes its real post-delay index, GBR or call frame')
    elif result['calls']:raise ValueError('the natural record predicate introduces a call')
    wanted=[]
    if caller:wanted.extend([(0x3C3C6,'read',0x3C47C,4,'00025e20'),(0x3C3C8,'read',0x3C470,2,'0129')])
    wanted.append((0x25E20,'read',0x25F10,4,'01005718'))
    if not value['sentinel']:wanted.append((0x25E32,'read',0x01005A94,1,bytes([case['flags']]).hex()))
    if caller:
        site=0x3C3D6 if value['bit'] else 0x3C3D8
        wanted.extend([(site,'read',0x01002449,1,bytes([case['status']]).hex()),
                       (site,'write',0x01002449,1,bytes([value['status']]).hex())])
    actual=[tuple(row[key] for key in ('site','mode','address','width_bytes','bytes'))
        for row in result['accesses'] if row['domain'] in ('ram','rom')]
    if not test_contract.exact(actual,wanted):
        raise ValueError('the record reader changes its exact byte1, pointer, width, value, conditional RMW or delay-slot transfer')
    returns=[(row['site'],row['target']) for row in result['branches'] if row['kind']=='return']
    expected=[(0x25E40,0x3C3CE),(0x3C3DE,observed['continuation'])] if caller else [(0x25E40,observed['continuation'])]
    if returns!=expected:raise ValueError('the record reader changes its natural predicate or separate observing return')
    return dict(index=case['index'],output=value['status'] if caller else value['register'],accesses=actual,
        exact_MAF_record_reads=True,native_geometry_inference=False,natural_caller_reachability=False,
        record_producer_admission=False,RPM_contributor_admission=False,hardware_qualification=False)
