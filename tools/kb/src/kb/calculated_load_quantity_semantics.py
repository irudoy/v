"""Separate integer quantity equations and entry-scoped physical operand order."""
from kb.paired_curve_normalization_withdrawal_semantics import position,linear
from kb.division_callees_semantics import quotient

RAM_BASE=0x01000000
MASK=0xFFFFFFFF
PHYSICAL_REGISTERS={0xB9982:0,0x26946:1,0x2695C:1,0x2695E:0,0x264B2:0,0x264B8:1,
    0xB999A:2,0x80844:0,0x259F6:0,0x25A02:0,0x808CC:6,0x26404:0,
    0x26AA0:1,0x26AA2:0,0x808DE:2,0x21D6E:2,0x808EA:0,0x808F4:7,0x80926:6}

def evaluate(phase,memory,calibration):
    if type(phase) is not int or phase not in (0,1) or type(memory) is not bytes or len(memory)!=65536:
        raise ValueError('the quantity equation requires an exact phase and complete actual incoming RAM')
    out=bytearray(memory);operands=[];calls=[];tails=[]
    def event(site,mode,address,width,raw):
        if type(raw) is not bytes or len(raw)!=width:raise ValueError('the quantity equation truncates a physical operand')
        operands.append(dict(site=site,mode=mode,address=address,width_bytes=width,register=PHYSICAL_REGISTERS[site],
            domain='ram' if RAM_BASE<=address<RAM_BASE+65536 else 'rom',bytes=raw.hex()))
        return int.from_bytes(raw,'big')
    def ram(site,offset,width):return event(site,'read',RAM_BASE+offset,width,memory[offset:offset+width])
    def rom(site,address,width):
        matches=[(at,raw) for at,raw in calibration.items() if at<=address and address+width<=at+len(raw)]
        if len(matches)!=1:raise ValueError('the quantity equation loses an authoritative complete ROM operand')
        at,raw=matches[0];return event(site,'read',address,width,raw[address-at:address-at+width])
    def store(site,offset,width,value):
        raw=value.to_bytes(width,'big');event(site,'write',RAM_BASE+offset,width,raw);out[offset:offset+width]=raw
    def call(site,target,arguments,sp_delta,returned=None):
        row=dict(site=site,target=target,return_address=site+4,arguments=arguments,sp_delta=sp_delta)
        if returned is not None:row['returned']=returned
        calls.append(row);return row
    if phase==0:
        sample=ram(0xB9982,0x4524,2);coordinate=sample>>8
        parent=call(0xB998C,0x264A0,{4:0x129D2,5:0x11B7B,6:coordinate},-4)
        axis=next(raw for at,raw in calibration.items() if at==0x11B7B)
        pos=position(tuple(axis),coordinate)
        nested=call(0x264AA,0x26944,{0:0x11B7B,4:15,5:coordinate,6:coordinate},-12)
        for index in pos['scanned']:rom(0x26946,0x11B7B+index,1)
        if pos['bracket']:
            first=rom(0x2695C,0x11B7B+pos['index'],1)
            second=rom(0x2695E,0x11B7B+pos['index']+1,1)
            call(0x2696A,0x26C78,{0:second-first,1:(coordinate-first)<<16},-16,{0:pos['fraction']})
        nested['returned']={4:pos['index'],5:pos['fraction']}
        second=rom(0x264B2,0x129D2+pos['index']+1,1)
        first=rom(0x264B8,0x129D2+pos['index'],1)
        value=linear(first,second,pos['fraction'])['value']
        parent['returned']={0:value};tails.append((0x264BE,0x26740))
        store(0xB999A,0x329F,1,value)
        return dict(phase=phase,memory=bytes(out),operands=operands,calls=calls,tails=tails,
            value=value,position=pos,coordinate=coordinate,source_byte_addresses=(0x129D2+pos['index'],0x129D2+pos['index']+1))
    predicates=[];first_divisor=None;first_quotient=None;second_division=None;K=None
    mode=ram(0x80844,0x244F,1)
    def predicate(site,index):
        row=call(site,0x259E4,{4:index},-8)
        if index==MASK:value=0
        else:
            raw=ram(0x259F6,0x5718+3*index+2,1)
            if raw&64:value=1
            else:value=int(bool(ram(0x25A02,0x5718+3*index+2,1)&32))
        row['returned']={0:value};predicates.append((site,index,value));return value
    calculate=False
    if not mode&32:
        if predicate(0x8084C,188):value=255
        else:value=255 if predicate(0x80854,9) else 0
    elif predicate(0x808AE,187):value=0
    elif predicate(0x808B6,8):value=0
    else:
        if predicate(0x808BE,MASK):raise ValueError('the actual minus-one predicate cannot take the consumer bypass branch')
        calculate=True;coordinate=ram(0x808CC,0x11B3,1)<<8
        curve_call=call(0x808D4,0x263F4,{4:0x1491A,5:coordinate},-8)
        if coordinate>=0xF000:
            first_divisor=rom(0x26404,0x14938,2)
            curve_return=first_divisor if first_divisor<0x8000 else (first_divisor|0xFFFF0000)
        else:
            index=coordinate>>12;fraction=(coordinate&4095)<<4
            first=rom(0x26AA0,0x1491A+index*2,2);second=rom(0x26AA2,0x1491C+index*2,2)
            first_divisor=linear(first,second,fraction)['value'];curve_return=first_divisor
            tails.extend(((0x263FE,0x26A64),(0x26AA6,0x26AB4),(0x26AB6,0x26740)))
        curve_call['returned']={0:curve_return}
        dividend=ram(0x808DE,0x1024,2)<<8
        first_quotient=quotient('unsigned',first_divisor,dividend)
        call(0x808E2,0x21CE0,{0:first_divisor,1:dividend},-8,{0:first_quotient})
        if first_divisor==0:store(0x21D6E,0x9818,4,0x44E)
        control=rom(0x808EA,0x870E,1)
        value=first_quotient
        if control&16:
            K=ram(0x808F4,0x329F,1)
            if not K:value=255
            else:
                numerator=(first_quotient<<7)&MASK;value=quotient('unsigned',K,numerator)
                second_division=dict(divisor=K,dividend=numerator,quotient=value)
                call(0x80906,0x21CE0,{0:K,1:numerator},-8,{0:value})
    value=min(value,255);store(0x80926,0x413E,1,value)
    return dict(phase=phase,memory=bytes(out),operands=operands,calls=calls,tails=tails,
        value=value,calculate=calculate,predicates=predicates,first_divisor=first_divisor,
        first_quotient=first_quotient,K=K,second_division=second_division)
