"""Separate scalar latch, saturation and byte-curve equations for three RPM phases."""

MASK=0xFFFFFFFF


def byte_curve(curve,coordinate):
    if coordinate>=240:
        byte=curve[15]
        return dict(value=byte,raw=byte if byte<128 else byte-256,index=15,fraction=0,upper=True)
    index,fraction=divmod(coordinate,16)
    left,right=curve[index:index+2]
    value=(left+(right-left)*fraction//16 if right>=left
        else left-(left-right)*fraction//16)
    return dict(value=value,raw=value,index=index,fraction=fraction,upper=False)


def stationary(before,calibration):
    memory=bytearray(before);flags=before[0x247F]
    active=before[0x110E]==0 and bool(before[0x244F]&4) and not before[0x2458]&32
    curve=None;accumulator=None
    if active:
        if not flags&8:
            memory[0x258A]=100;flags|=8
        elif before[0x258A]==0:
            difference=int.from_bytes(before[0x11BC:0x11BE],'big')-160
            quotient=difference//2 if difference>=0 else -((-difference)//2)
            coordinate=min(255,max(0,quotient))
            curve=dict(byte_curve(calibration[0x124D2],coordinate),coordinate=coordinate)
            accumulator=int.from_bytes(before[0x16A6:0x16A8],'big')+curve['value']-128
            memory[0x16A6:0x16A8]=min(65535,max(0,accumulator)).to_bytes(2,'big')
            memory[0x258A]=100
        ready=(int.from_bytes(memory[0x16A6:0x16A8],'big')>=int.from_bytes(calibration[0x911C],'big')
            and (before[0x1071]>=calibration[0x8D0E][0] or bool(before[0x245D]&64)))
        flags=(flags|16) if ready else (flags&239)
        if flags&32:
            if before[0x11AE]<calibration[0x85D9][1]:flags&=199
        elif flags&16 and before[0x11AE]>=calibration[0x85D9][0]:flags|=32
    else:
        memory[0x16A6:0x16A8]=bytes(2);flags&=199
    memory[0x247F]=flags
    return dict(memory=bytes(memory),output=int(bool(flags&32)),active=active,curve=curve,
        accumulator=accumulator,flags=flags)


def thermal(before,calibration):
    if before[0x4184]!=192 or before[0x571E]<40:
        raise ValueError('the thermal scalar proof lacks its explicit quiet diagnostic premise')
    memory=bytearray(before);flags=before[0x41F2]
    enabled=bool(calibration[0x186C9][0]&1)
    if enabled:
        memory[0x4397]=10;memory[0x4396]=50
        if flags&8 and not before[0x5720]&16:
            flags&=247;memory[0x4370]=10
        temperature=before[0x1071]+(10 if before[0x4209]&1 else 0)
        memory[0x4209]=(before[0x4209]|1) if temperature>=calibration[0x8D15][0] else (before[0x4209]&254)
        memory[0x4370]=10;flags&=239
        rpm=before[0x11B3]+(calibration[0x8957][0] if before[0x41EE]&8 else 0)
        memory[0x41EE]=(before[0x41EE]|8) if rpm>=calibration[0x88ED][0] else (before[0x41EE]&247)
        flags=(flags|32) if flags&8 and not before[0x2458]&32 and memory[0x41EE]&8 else (flags&223)
        memory[0x41F2]=flags
    return dict(memory=bytes(memory),output=int(bool(flags&32)),enabled=enabled,flags=flags,
        diagnostic_dispatch=False)


def sustained(before,calibration):
    memory=bytearray(before);flags=before[0x247C]
    threshold=min(65535,int.from_bytes(calibration[0x90E0],'big')*calibration[0x84DA][4])
    enabled=not calibration[0x8B3F][0]&128
    exposure=int.from_bytes(before[0x1932:0x1934],'big')
    if not enabled or exposure<threshold or before[0x11B3]<calibration[0x84DA][3]:flags&=127
    elif before[0x11B3]>=calibration[0x84DA][0]:flags|=128
    memory[0x247C]=flags
    return dict(memory=bytes(memory),output=int(bool(flags&128)),enabled=enabled,
        threshold=threshold,exposure=exposure,flags=flags)


def ceiling(before,calibration):
    memory=bytearray(before);flags=before[0x249C]
    enabled=not calibration[0x8B3F][0]&128;target=None
    if enabled:
        request=before[0x2714]
        valid=request not in (0,255) and not before[0x4189]&2 and not before[0x4250]&128
        target=max(request,calibration[0x89FC][1]) if valid else 255
        memory[0x2488]=(before[0x2488]|32) if valid else (before[0x2488]&223)
        memory[0x31F6]=target
        rpm=before[0x11AE]+(calibration[0x89FC][0] if flags&128 else 0)
        flags=(flags|128) if rpm>target else (flags&127)
    else:flags&=127
    memory[0x249C]=flags
    return dict(memory=bytes(memory),output=int(bool(flags&128)),enabled=enabled,target=target,flags=flags)


def evaluate(entry,before,calibration,context):
    if entry==0x4EDC6:
        first=stationary(before,calibration);second=thermal(first['memory'],calibration)
        return dict(entry=entry,memory=second['memory'],stationary=first,thermal=second,
            output=(second['output'],context[14]|context[0]|first['output']))
    if entry==0x4EDE4:
        value=sustained(before,calibration)
        return dict(entry=entry,memory=value['memory'],sustained=value,
            output=(value['output'],context[14]),r2=value['output'])
    if entry==0x4EE00:
        value=ceiling(before,calibration)
        return dict(entry=entry,memory=value['memory'],ceiling=value,
            output=(value['output'],context[14]|context[0]))
    raise ValueError('the remaining RPM scalar proof changes its bounded caller phase')
