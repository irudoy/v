"""Independent scalar and complete-register expectations for natural helper entries."""

MASK=0xFFFFFFFF


def signed(value):
    return value-(1<<32) if value&(1<<31) else value


def evaluate(entry,context,sr_before,frame_before,sp,continuation):
    if (type(context) is not tuple or len(context)!=20
            or any(type(value) is not int or not 0<=value<=MASK for value in context)
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(sr_before) is not int or sr_before&0x3F1!=context[18]
            or type(sp) is not int or sp&3 or type(continuation) is not int):
        raise ValueError('the register-only equations need complete exact input CPU, frame and SR state')
    registers=list(context[:15]);frame=bytearray(frame_before);sr=sr_before;physical=[]
    def t(value):
        nonlocal sr
        sr=(sr&~1)|int(value)
    def push_pop(push_site,pop_site,source,target):
        value=context[source];raw=value.to_bytes(4,'big');frame[156:160]=raw
        physical.extend((dict(site=push_site,mode='write',address=sp-4,width_bytes=4,register=source,domain='frame',bytes=raw.hex()),
            dict(site=pop_site,mode='read',address=sp-4,width_bytes=4,register=target,domain='frame',bytes=raw.hex())))
    if entry in (0x224F8,0x224FA):
        amount=7 if entry==0x224F8 else 6;registers[0]=(signed(context[0])>>amount)&MASK
        t((context[0]>>(amount-1))&1);returned=0x22504
    elif entry==0x2251C:
        registers[0]=(signed(context[0])>>11)&MASK;t((context[0]>>10)&1)
        push_pop(0x2251C,0x2252E,1,1);returned=0x2252C
    elif entry==0x259D0:
        registers[7]=context[7]&255
        registers[2]=(context[4]-(context[6] if registers[7] else 0))&MASK
        comparison=signed(registers[2])>signed(context[5]);t(comparison)
        registers[0]=int(not comparison);returned=0x259E0
    elif entry==0x26740:
        left,right,fraction=context[0],context[2],context[3]
        ascending=right>=left;t(ascending);difference=(right-left if ascending else left-right)&MASK
        product=(difference*fraction)&MASK;word=product>>16
        registers[1]=context[17]
        registers[0]=(left+word if ascending else left-word)&MASK
        registers[2]=word if ascending else registers[0]
        if not ascending:push_pop(0x26744,0x26752,0,2)
        returned=0x2676A if ascending else 0x26758
    elif entry==0x50A4C:
        registers[4]=context[4]|context[5]|context[6]
        registers[0]=registers[4]&63;returned=0x50A52
    else:
        raise ValueError('the register-only equations name an undeclared natural entry')
    branches=[]
    if entry==0x259D0:
        branches.append(dict(site=0x259D4,target=0x259DA if not registers[7] else 0x259D8,
            kind='taken' if not registers[7] else 'fallthrough',delay=True))
    elif entry==0x26740:
        branches.append(dict(site=0x26742,target=0x2675C if ascending else 0x26744,
            kind='taken' if ascending else 'fallthrough',delay=False))
    branches.append(dict(site=returned,target=continuation,kind='return',delay=True))
    if entry in (0x224F8,0x224FA):path=tuple(range(entry,0x22508,2))
    elif entry==0x2251C:path=tuple(range(entry,0x22530,2))
    elif entry==0x259D0:
        path=(*range(entry,0x259D8,2),*((0x259D8,) if registers[7] else ()),*range(0x259DA,0x259E4,2))
    elif entry==0x26740:
        path=(0x26740,0x26742,*range(0x2675C,0x2676E,2)) if ascending else tuple(range(entry,0x2675C,2))
    else:path=tuple(range(entry,0x50A56,2))
    return dict(registers=tuple(registers),sr=sr,gbr=context[15],mach=context[16],macl=context[17],
        pr=continuation,sp=sp,frame=bytes(frame),physical=physical,
        exit=(sr,continuation,context[17],context[16],context[15],*reversed(registers)),
        return_site=returned,return_target=continuation,output=registers[0],branches=branches,path=path)
