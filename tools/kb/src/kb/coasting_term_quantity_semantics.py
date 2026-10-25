"""Independent directed byte interpolation, exact operand order and coasting publications."""
RAM_BASE=0x01000000
MASK=0xFFFFFFFF
PREDICATES=(-1,-1,20,71,72,73,74,75,76,138,139,140)
PREDICATE_CALLS=(0x25E50,0x25E58,0x25E60,0x25E68,0x25E70,0x25E78,
    0x25E80,0x25E88,0x25E90,0x25E9C,0x25EA8,0x25EB4)

def signed(raw,bits):return raw-(1<<bits) if raw&(1<<(bits-1)) else raw
def byte_register(raw):return signed(raw,8)&MASK

def evaluate(phase,memory,calibration):
    if type(phase) is not int or phase not in (0,1) or type(memory) is not bytes or len(memory)!=65536:
        raise ValueError('the coasting equations require an exact phase and complete actual incoming RAM')
    after=bytearray(memory);operands=[];calls=[];tails=[];curves=[];predicate_results=[]
    def rom(address,width=1):
        spans=[(at,raw) for at,raw in calibration.items() if at<=address and address+width<=at+len(raw)]
        if len(spans)!=1:raise ValueError('the coasting equations lose a complete authoritative ROM operand')
        at,raw=spans[0]
        if type(raw) is not bytes:raise ValueError('the coasting equations replace immutable calibration bytes')
        return raw[address-at:address-at+width]
    def read(site,address,width,register,domain='ram'):
        raw=bytes(after[address:address+width]) if domain=='ram' else rom(address,width)
        operands.append(dict(site=site,mode='read',address=RAM_BASE+address if domain=='ram' else address,
            width_bytes=width,register=register,domain=domain,bytes=raw.hex()))
        return int.from_bytes(raw,'big')
    def write(site,address,width,value,register):
        raw=(value&((1<<(8*width))-1)).to_bytes(width,'big');after[address:address+width]=raw
        operands.append(dict(site=site,mode='write',address=RAM_BASE+address,width_bytes=width,
            register=register,domain='ram',bytes=raw.hex()))
    def call(site,target,arguments,sp_delta):
        row=dict(site=site,target=target,return_address=site+4,arguments=arguments,sp_delta=sp_delta)
        calls.append(row);return row
    def curve(site,entry,base,coordinate,sp_delta):
        count,shift=(8,5) if entry==0x26370 else (16,4)
        row=call(site,entry,{4:base,5:coordinate},sp_delta)
        index=min(coordinate>>shift,count-1)
        if index==count-1:
            value=read(entry+16,base+index,1,0,'rom');returned=byte_register(value);fraction=0
        else:
            fraction=(coordinate&((1<<shift)-1))<<(16-shift)
            first=read(0x26AAC,base+index,1,1,'rom')
            second=read(0x26AAE,base+index+1,1,0,'rom')
            magnitude=abs(second-first)*fraction//65536
            value=first+magnitude if second>=first else first-magnitude;returned=value
            tails.extend(((entry+10,0x26A80 if count==8 else 0x26A84),(0x26AB6,0x26740)))
        row['returned']={0:returned}
        curves.append(dict(entry=entry,base=base,coordinate=coordinate,index=index,fraction=fraction,value=value))
        return value
    def predicate(site,index,sp_delta):
        row=call(site,0x25E20,{4:index&MASK},sp_delta)
        active=0 if index==-1 else int(bool(read(0x25E32,0x5719+index*3,1,0)&128))
        row['returned']={0:active};predicate_results.append((site,index,active));return active
    if phase==0:
        coordinate=read(0x2C62C,0x1077,1,0)
        value=curve(0x2C630,0x26370,0x122E2,coordinate,-4)
        write(0x2C63C,0x1230,2,value,6);write(0x2C642,0x126E,2,value,6)
        return dict(phase=phase,memory=bytes(after),operands=operands,calls=calls,tails=tails,curves=curves,
            value=value,coordinate=coordinate,handoff={0x1230:value,0x126E:value})
    value=signed(read(0x47132,0x13EA,2,13),16)
    speed=None;source_word=None;quantity=None;target=None;decaying=False;growing=False
    def admit():
        if not read(0x47134,0x2458,1,0)&32:return False
        if read(0x4713E,0x244F,1,0)&4:return False
        speed_input=read(0x4714E,0x110E,1,6)
        floor=read(0x47150,0x86FD,1,2,'rom')
        if byte_register(speed_input)<byte_register(floor):return False
        if read(0x4715C,0x4197,1,0)&64:return False
        row=call(0x47168,0x25E4E,{},-48);active=0
        for site,index in zip(PREDICATE_CALLS,PREDICATES):
            if predicate(site,index,-52):active=1;break
        row['returned']={0:active}
        if active:return False
        if predicate(0x47176,-1,-48):raise ValueError('the actual minus-one diagnostic predicate cannot be active')
        limit_input=read(0x47184,0x106A,1,0)
        limit=read(0x4718E,0x8763,1,0,'rom')
        read(0x47192,0x2473,1,0)
        if limit_input>=limit:return False
        corrected=bool(read(0x471A2,0x870C,1,0,'rom')&128)
        if corrected and not read(0x471AC,0x2466,1,0)&128:return False
        return True
    admitted=admit()
    if not admitted:
        flags=read(0x4734C,0x2473,1,None);write(0x4734C,0x2473,1,flags&251,None)
        flags=read(0x47350,0x24A0,1,None);write(0x47350,0x24A0,1,flags&254,None)
        value=0
    else:
        corrected=bool(rom(0x870C)[0]&128)
        correction_flags=read(0x471BC,0x2458,1,0) if corrected else 0
        if corrected and correction_flags&128:
            raw_speed=read(0x471C8,0x110E,1,2)
            correction=signed(read(0x471CA,0x8252,1,6,'rom'),8)
            speed=max(0,min(255,signed((raw_speed-correction)&65535,16)))
        else:speed=read(0x471EE,0x110E,1,2)
        write(0x471F2,0x1A7A,1,speed,2)
        active=bool(after[0x2473]&4)
        if not active:
            pending=read(0x47204,0x24A0,1,0)&1
            if not pending:
                first=read(0x47210,0x11B2,1,5)
                second=read(0x47212,0x22E4,1,0)
                threshold=read(0x4721A,0x8762,1,0,'rom')
                if first>second+threshold:
                    actual_speed=read(0x47228,0x1A7A,1,4)
                    floor=read(0x4722A,0x8766,1,0,'rom')
                    if byte_register(actual_speed)>=byte_register(floor):
                        lower=read(0x47234,0x8765,1,0,'rom')
                        temperature=read(0x47238,0x1071,1,0)
                        if lower<=temperature:
                            upper=read(0x47242,0x8764,1,0,'rom')
                            if temperature<=upper:
                                flags=after[0x2473]|4
                                write(0x47252,0x2473,1,flags,0);active=True
        if active:
            additive=read(0x4726A,0x1748,2,5)
            source_word=read(0x4726E,0x1230,2,4)
            summed=signed(source_word,16)+additive
            if summed>=0:quantity=signed(read(0x47282,0x1230,2,7),16)+additive
            else:quantity=0
            actual_speed=read(0x4728E,0x1A7A,1,4);coordinate=min(255,actual_speed*4)
            cap=curve(0x472A6,0x26388,0x11FF6,coordinate,-48)
            if cap<=quantity:cap=curve(0x472BA,0x26388,0x11FF6,coordinate,-48)
            target=128*min(quantity,cap)
            first=read(0x472D4,0x11B2,1,2);second=read(0x472D6,0x22E4,1,0)
            threshold=read(0x472D8,0x8760,1,6,'rom')
            maintain=first>second+threshold
            if maintain:maintain=not bool(read(0x472E6,0x2465,1,0)&64)
            if maintain:
                actual_speed=read(0x472F0,0x1A7A,1,2)
                floor=read(0x472F2,0x8761,1,0,'rom')
                maintain=byte_register(actual_speed)>=byte_register(floor)
            if maintain:
                step=read(0x472FE,0x84D9,1,0,'rom')
                prior=read(0x47304,0x13EA,2,6)
                value=min(prior+step,target);growing=True
            else:
                flags=read(0x47318,0x2473,1,None);write(0x47318,0x2473,1,flags&251,None)
                flags=read(0x4731C,0x24A0,1,None);write(0x4731C,0x24A0,1,flags|1,None)
        flags=read(0x4731E,0x24A0,1,0)
        if flags&1:
            prior=read(0x4732A,0x13EA,2,7)
            step=read(0x4732C,0x84D8,1,5,'rom')
            value=max(0,prior-step);decaying=True
            if value==0:write(0x47348,0x24A0,1,flags&254,0)
    write(0x47356,0x13EA,2,value,13)
    return dict(phase=phase,memory=bytes(after),operands=operands,calls=calls,tails=tails,curves=curves,
        predicates=predicate_results,value=value&65535,publication_register_value=value&MASK,admitted=admitted,speed=speed,source_word=source_word,
        quantity=quantity,target=target,growing=growing,decaying=decaying)
