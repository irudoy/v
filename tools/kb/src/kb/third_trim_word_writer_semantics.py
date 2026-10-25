"""Independent full third-trim writer arithmetic and exact raw channel/shared-bank effects."""
RAM_BASE=0x01000000
MASK=0xFFFFFFFF

def signed(value,bits=32):return value-(1<<bits) if value&(1<<(bits-1)) else value

def evaluate(memory,calibration,context):
    if (type(memory) is not bytes or len(memory)!=65536 or type(context) is not tuple or len(context)!=20
            or any(type(v) is not int or not 0<=v<=MASK for v in context)):
        raise ValueError('the third-trim equations need complete exact incoming RAM and CPU context')
    after=bytearray(memory);operands=[]
    channel=context[4]&255;mask=channel+1;word_address=0x2A24+channel*2;accumulator_address=0x3310+channel*4
    def rom(address,width):
        spans=[(at,raw) for at,raw in calibration.items() if at<=address and address+width<=at+len(raw)]
        if len(spans)!=1:raise ValueError('the third-trim equation loses one physical ROM span')
        at,raw=spans[0]
        if type(raw) is not bytes:raise ValueError('the third-trim equation replaces immutable calibration')
        return raw[address-at:address-at+width]
    def read(site,address,width,register,domain='ram'):
        raw=bytes(after[address:address+width]) if domain=='ram' else rom(address,width)
        operands.append(dict(site=site,mode='read',address=RAM_BASE+address if domain=='ram' else address,
            width_bytes=width,register=register,domain=domain,bytes=raw.hex()))
        return int.from_bytes(raw,'big')
    def write(site,address,width,value,register):
        raw=(value&((1<<(width*8))-1)).to_bytes(width,'big');after[address:address+width]=raw
        operands.append(dict(site=site,mode='write',address=RAM_BASE+address,width_bytes=width,
            register=register,domain='ram',bytes=raw.hex()))
    shared=bool(read(0x5B548,0x8B2A,1,0,'rom')&4)
    correction=False;ramp=False;accumulator=None;accumulator_before=None;clear=False
    if not shared:
        flags=read(0x5B55A,0x328A,1,2)
        if flags&mask:
            flags=read(0x5B564,0x328B,1,2)
            if flags&mask:correction=True
            else:correction=bool(read(0x5B56E,0x328E,1,2)&mask)
    else:
        flags=read(0x5B582,0x328A,1,0)
        if flags&1 and flags&2:
            flags=read(0x5B58E,0x328B,1,0)
            if flags&1 and flags&2:correction=True
            else:
                flags=read(0x5B59A,0x328E,1,0)
                correction=bool(flags&1 and flags&2)
    if correction:
        first_mask=read(0x5B5AA,0x28E4,1,6)
        old=read(0x5B5AE,word_address,2,2)
        second_mask=read(0x5B5BC,0x28B4,1,6)
        if first_mask&mask:
            if not second_mask&mask:
                step=read(0x5B600,0x8998,1,5,'rom')*16;tentative=old+step
            else:
                step=read(0x5B60C,0x86F7,1,4,'rom');tentative=max(0,old-step)
        else:
            if second_mask&mask:
                step=read(0x5B622,0x8997,1,6,'rom')*16;tentative=max(0,old-step)
            else:
                step=read(0x5B638,0x86F6,1,6,'rom');tentative=old+step
        upper=read(0x5B642,0x82E5,1,6,'rom')*256
        lower=read(0x5B656,0x82E4,1,5,'rom')*256
        produced=max(lower,min(tentative,upper))
    else:
        flags=read(0x5B670,0x328C,1,2)
        ramp=bool(flags&mask)
        if not ramp:ramp=bool(read(0x5B67A,0x3288,1,2)&mask)
        if not ramp:produced=0x6400
        else:
            accumulator_before=read(0x5B690,accumulator_address,4,14)
            old=signed(accumulator_before);step=read(0x5B696,0x86F5,1,4,'rom')
            if old<0x6400:
                produced=min(0x6400,old+step)
                write(0x5B6B8,accumulator_address,4,produced,7)
            else:
                produced=max(0x6400,old-step)
                write(0x5B6D4,accumulator_address,4,produced,7)
            accumulator=produced&MASK;clear=produced==0x6400
            if clear:
                flags=read(0x5B6DC,0x328C,1,6);write(0x5B6E0,0x328C,1,flags&~mask,6)
                flags=read(0x5B6E4,0x3288,1,6);write(0x5B6E8,0x3288,1,flags&~mask,6)
    full=produced&MASK;word=full&65535
    write(0x5B6F0,word_address,2,full,2)
    if shared:write(0x5B6F4,0x2A26,2,full,0)
    return dict(memory=bytes(after),operands=operands,calls=[],tails=[],channel=channel,mask=mask,
        indexed_address=word_address,accumulator_address=accumulator_address,shared=shared,correction=correction,
        ramp=ramp,clear=clear,accumulator_before=accumulator_before,accumulator=accumulator,
        full_word_register=full,word=word,value=int.from_bytes(after[0x2A24:0x2A26],'big'),
        sibling_value=int.from_bytes(after[0x2A26:0x2A28],'big'))
