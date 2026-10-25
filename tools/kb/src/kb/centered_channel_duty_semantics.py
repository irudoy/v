"""Independent wrapped preconditioning, centered curves, indexed duty and physical operand order."""
from kb.division_callees_semantics import quotient
RAM_BASE=0x01000000
MASK=0xFFFFFFFF

def signed(raw,bits=32):return raw-(1<<bits) if raw&(1<<(bits-1)) else raw
def bounded(raw):return min(0xFFFFFF,max(0,signed(raw&MASK)))

def evaluate(phase,memory,calibration,context):
    if (type(phase) is not int or phase not in (0,1) or type(memory) is not bytes or len(memory)!=65536
            or type(context) is not tuple or len(context)!=20
            or any(type(v) is not int or not 0<=v<=MASK for v in context)):
        raise ValueError('the centered duty equations need complete exact independent phase inputs')
    after=bytearray(memory);operands=[];calls=[];tails=[];curves=[];divisions=[]
    def rom(address,width=1):
        spans=[(at,raw) for at,raw in calibration.items() if at<=address and address+width<=at+len(raw)]
        if len(spans)!=1:raise ValueError('the centered duty equations lose a complete authoritative physical ROM span')
        at,raw=spans[0]
        if type(raw) is not bytes:raise ValueError('the centered duty equations replace immutable calibration bytes')
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
    def divide(site,target,divisor,dividend,sp_delta):
        value=quotient('signed' if target==0x21BBC else 'unsigned',divisor,dividend)
        row=call(site,target,{0:divisor,1:dividend},sp_delta);row['returned']={0:value}
        if divisor==0:
            write(0x21C74 if target==0x21BBC else 0x21D6E,0x9818,4,0x44E,2)
        divisions.append(dict(site=site,target=target,divisor=divisor,dividend=dividend,quotient=value))
        return value
    def implicit(site,base,coordinate):
        row=call(site,0x26370,{4:base,5:coordinate},-24);index=min(coordinate//32,7)
        if index==7:
            value=read(0x26380,base+7,1,0,'rom');returned=signed(value,8)&MASK;fraction=0
        else:
            fraction=(coordinate%32)*2048
            first=read(0x26AAC,base+index,1,1,'rom');second=read(0x26AAE,base+index+1,1,0,'rom')
            delta=abs(second-first)*fraction//65536
            value=first+delta if second>=first else first-delta;returned=value
            tails.extend(((0x2637A,0x26A80),(0x26AB6,0x26740)))
        row['returned']={0:returned}
        curves.append(dict(kind='implicit',base=base,coordinate=coordinate,index=index,fraction=fraction,value=value,return_register_value=returned))
        return value
    def explicit(site,base,coordinate):
        outer=call(site,0x26474,{4:base,5:0x11BDB,6:coordinate},-24)
        inner=call(0x2647E,0x26944,{0:0x11BDB,4:7,5:coordinate},-32)
        index=0;fraction=0;bracket=False
        for current in range(7,-1,-1):
            knot=read(0x26946,0x11BDB+current,1,1,'rom')
            if coordinate==knot or coordinate>knot and current==7:index=current;break
            if coordinate>knot:
                index=current;bracket=True
                first=read(0x2695C,0x11BDB+current,1,1,'rom')
                second=read(0x2695E,0x11BDC+current,1,0,'rom')
                denominator=second-first;numerator=(coordinate-first)*65536
                if denominator<=0 or not first<coordinate<second:
                    raise ValueError('the rightmost eight-knot bracket loses its positive actual divisor')
                fraction=numerator//denominator
                nested=call(0x2696A,0x26C78,{0:denominator,1:numerator},-36);nested['returned']={0:fraction}
                break
        inner['returned']={4:index,5:fraction}
        second=read(0x26486,base+index+1,1,0,'rom')
        first=read(0x2648C,base+index,1,1,'rom')
        delta=abs(second-first)*fraction//65536;value=first+delta if second>=first else first-delta
        outer['returned']={0:value};tails.append((0x26492,0x26740))
        curves.append(dict(kind='explicit',base=base,coordinate=coordinate,index=index,fraction=fraction,
            value=value,return_register_value=value,bracket=bracket,physical_addresses=(base+index+1,base+index)))
        return value
    if phase==1:
        channel=context[4]&255;selection=read(0xBE828,0x28C2,1,6)
        handoff=None;mode='forced-off'
        if selection&(channel+1):
            value=255;mode='forced-maximum'
        else:
            enabled=bool(read(0xBE842,0x246B,1,0)&64)
            if not enabled:
                requested=bool(read(0xBE848,0x248B,1,0)&2)
                if requested:enabled=bool(read(0xBE852,0x41FA,1,0)&1)
            if not enabled:value=0
            else:
                override=bool(read(0xBE866,0x24A7,1,0)&1)
                if override:value=read(0xBE870,0x1A59,1,6);mode='override'
                else:
                    handoff=read(0xBE886,0x1A9C+channel*4,4,4)
                    speed=read(0xBE894,0x1108,1,2)
                    high=divide(0xBE89C,0x21CE0,speed,(handoff>>16)*150,-28)
                    speed_again=read(0xBE8B2,0x1108,1,6)
                    middle=divide(0xBE8B8,0x21CE0,speed_again,((handoff>>8)&255)*150,-28)
                    value=high+((middle+128)>>8);mode='calculated'
                value=min(value,255)
        write(0xBE8DC,0x2440+channel,1,value,6)
        return dict(phase=phase,memory=bytes(after),operands=operands,calls=calls,tails=tails,curves=curves,
            divisions=divisions,channel=channel,handoff=handoff,value=value,mode=mode,publication=0x2440+channel,
            publication_register_value=MASK if mode=='forced-maximum' else value)
    mode=read(0xBE5CA,0x8615,1,0,'rom');override=None
    if mode&128:
        sample=read(0xBE5D4,0x2326,1,0);lower=read(0xBE5D6,0x8830,1,2,'rom')
        if sample<=lower+128:
            override='lower';value=read(0xBE5EA,0x882F,1,2,'rom')
            write(0xBE5F0,0x1A59,1,value,2)
            flags=read(0xBE5F4,0x248E,1,0);write(0xBE5FC,0x248E,1,flags&191,2)
            flags=read(0xBE600,0x24A7,1,0);write(0xBE60A,0x24A7,1,flags|1,2)
        else:
            flags=read(0xBE61E,0x248E,1,2)
            upper=read(0xBE622,0x86B9,1,0,'rom')
            if sample>=upper+128:
                override='upper'
                if not flags&64:
                    value=read(0xBE63C,0x86B7,1,2,'rom');write(0xBE642,0x1A59,1,value,2)
                    counter=read(0xBE644,0x86BD,1,0,'rom')*2;write(0xBE64A,0x2608,2,counter,0)
                    write(0xBE652,0x248E,1,flags|64,4)
                counter=read(0xBE662,0x2608,2,0)
                if counter==0:
                    value=read(0xBE66C,0x86B8,1,0,'rom');write(0xBE672,0x1A59,1,value,2)
                flags=read(0xBE676,0x24A7,1,0);write(0xBE680,0x24A7,1,flags|1,2)
    family=None
    if override is None:
        flags=read(0xBE68A,0x248E,1,0)
        write(0xBE69A,0x248E,1,flags&191,2)
        flags=read(0xBE69E,0x24A7,1,0)
        coefficient=read(0xBE6A0,0x8DD8,1,5,'rom')
        write(0xBE6A8,0x24A7,1,flags&254,2)
        prior=read(0xBE6B0,0x1AFC,4,6)
        numerator=((prior-0x800000)<<7)&MASK
        quotient_first=divide(0xBE6BE,0x21BBC,coefficient,numerator,-24)
        value=bounded(quotient_first+0x800000)
        coefficient_again=read(0xBE6DE,0x8DD8,1,5,'rom')
        write(0xBE6E0,0x16E8,4,value,2)
        prior=read(0xBE6E6,0x1B00,4,6)
        numerator=((prior-0x800000)<<7)&MASK
        quotient_second=divide(0xBE6F4,0x21BBC,coefficient_again,numerator,-24)
        value=bounded(quotient_second+0x800000);write(0xBE714,0x16EC,4,value,2)
        family=read(0xBE716,0x8616,1,0,'rom')&1
        if family:
            coordinate=read(0xBE724,0x2772,1,7)
            value=explicit(0xBE72A,0x12E82,coordinate)
        else:
            coordinate=read(0xBE788,0x106F,1,0)
            value=implicit(0xBE78E,0x12E72,coordinate)
        write(0xBE798,0x1A7B,1,value,2)
        base=read(0xBE7A0,0x16E8,4,6)
        composite=bounded((value<<16)+base-0x800000)
        write(0xBE7B6,0x1A9C,4,composite,2)
        family_second=read(0xBE7B8,0x8616,1,0,'rom')&1
        if family_second!=family:raise ValueError('the centered pair changes its shared immutable8616 family byte')
        if family_second:
            coordinate=read(0xBE7C6,0x2772,1,7)
            value=explicit(0xBE7CC,0x12E8A,coordinate)
        else:
            coordinate=read(0xBE7D8,0x106F,1,0)
            value=implicit(0xBE7DE,0x12E7A,coordinate)
        write(0xBE7E8,0x1A7C,1,value,2)
        base=read(0xBE7EE,0x16EC,4,6)
        composite=bounded((value<<16)+base-0x800000);write(0xBE804,0x1AA0,4,composite,7)
    handoff={at:int.from_bytes(after[at:at+4],'big') for at in (0x1A9C,0x1AA0)}
    return dict(phase=phase,memory=bytes(after),operands=operands,calls=calls,tails=tails,curves=curves,
        divisions=divisions,override=override,family=family,handoff=handoff,composites_published=override is None)
