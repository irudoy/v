"""Separate implicit-word interpolation and real two-channel physical transfers."""

from kb import test_contract


def lookup(curve,coordinate):
    if type(curve) is not bytes or len(curve)!=128 or type(coordinate) is not int or not 0<=coordinate<=65535:
        raise ValueError('the MAF lookup needs its exact byte extent and word coordinate')
    words=[int.from_bytes(curve[index:index+2],'big') for index in range(0,128,2)]
    if coordinate>=0x3F00:
        value=words[-1];raw=(value if value<0x8000 else value-65536)&0xFFFFFFFF
        return dict(word=value,register=raw,index=63,fraction=0,clamped=True,return_site=0x26420)
    index,fraction=coordinate//256,(coordinate%256)*256
    left,right=words[index:index+2]
    delta=abs(right-left)*fraction//65536
    value=left+delta if right>=left else left-delta
    return dict(word=value,register=value,index=index,fraction=fraction,clamped=False,
        return_site=0x2676A if right>=left else 0x26758)


def evaluate(case,observed,result):
    calibration=observed['calibration_before'];curves=calibration[0x141F4]
    coordinates=((case['adc1']*16)&65535,(case['adc2']*16)&65535)
    outputs=(lookup(curves[128:],coordinates[0]),lookup(curves[:128],coordinates[1]))
    memory=bytearray(observed['memory_before'][0]);memory[0x1054:0x1056]=outputs[0]['word'].to_bytes(2,'big')
    if observed['memory_after']!=(bytes(memory),) or result['registers'][0]!=outputs[1]['register']:
        raise ValueError('the MAF curve slice differs from independent word, register-extension or complete RAM equations')
    if len(result['calls'])!=2:raise ValueError('the MAF curve slice needs both actual wrapper calls')
    for call,site,at,coordinate in zip(result['calls'],(0x3A930,0x3A946),(0x14274,0x141F4),coordinates):
        entry=call['entry']
        if (tuple(call[key] for key in ('site','target','return_address','sp'))!=(site,0x26410,site+4,observed['sp'])
                or tuple(entry['registers'][index] for index in (4,5))!=(at,coordinate)
                or (entry['sp'],entry['pr'])!=(observed['sp'],site+4)):
            raise ValueError('the MAF curve slice changes a real wrapper target or post-delay ADC/table argument')
    wanted=[]
    def read(site,address,width,data):wanted.append((site,'read',address,width,data.hex()))
    def helper(at,value):
        read(0x26410,0x26424,2,bytes.fromhex('3f00'))
        if value['clamped']:
            address=at+126;offset=address-0x141F4
            read(0x26422,address,2,curves[offset:offset+2])
        else:
            read(0x26418,0x26428,4,bytes.fromhex('00026a74'))
            address=at+value['index']*2;offset=address-0x141F4
            read(0x26AA0,address,2,curves[offset:offset+2]);read(0x26AA2,address+2,2,curves[offset+2:offset+4])
            read(0x26AB4,0x26ABC,4,bytes.fromhex('00026740'))
    read(0x3A924,0x3AB60,4,bytes.fromhex('00014274'))
    read(0x3A926,0x01001E48,2,case['adc1'].to_bytes(2,'big'))
    read(0x3A928,0x3AB64,4,bytes.fromhex('00026410'));helper(0x14274,outputs[0])
    read(0x3A934,0x3AB68,4,bytes.fromhex('01001048'))
    read(0x3A936,0x3AB6C,4,bytes.fromhex('000141f4'))
    wanted.append((0x3A938,'write',0x01001054,2,outputs[0]['word'].to_bytes(2,'big').hex()))
    read(0x3A93C,0x01001E4A,2,case['adc2'].to_bytes(2,'big'))
    read(0x3A93E,0x3AB64,4,bytes.fromhex('00026410'));helper(0x141F4,outputs[1])
    read(0x3A94A,0x3AB68,4,bytes.fromhex('01001048'))
    actual=[tuple(row[key] for key in ('site','mode','address','width_bytes','bytes'))
        for row in result['accesses'] if row['domain'] in ('ram','rom')]
    if not test_contract.exact(actual,wanted):
        raise ValueError('the MAF curve slice changes an exact root/cell, input, pointer, width, value or transfer order')
    if (result['macl'],result['mach'],result['gbr'])!=tuple(observed['context'][index] for index in (17,16,15)):
        raise ValueError('the MAF curve helpers change a retained special register')
    returns=[(row['site'],row['target']) for row in result['branches'] if row['kind']=='return']
    if returns!=[(outputs[0]['return_site'],0x3A934),(outputs[1]['return_site'],0x3A94A),
            (0x3A950,observed['continuation'])]:
        raise ValueError('the MAF curve slice changes a natural helper return or its separate observing return')
    return dict(index=case['index'],output=(outputs[0]['word'],outputs[1]['word']),accesses=actual,
        exact_MAF_curve_reads=True,native_geometry_inference=False,natural_caller_reachability=False,
        universal_no_read_claim=False,hardware_qualification=False)
