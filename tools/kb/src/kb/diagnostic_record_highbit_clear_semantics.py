"""Independent complete CPU and indexed byte-clear equations for natural 0008C348."""
MASK=0xFFFFFFFF
RAM_BASE=0x01000000
ENTRY=0x8C348
SENTINEL=MASK
ACTIVE_PATH=tuple(range(ENTRY,0x8C362,2))
SENTINEL_PATH=tuple(range(ENTRY,0x8C350,2))+(0x8C362,0x8C364)


def signed_byte(raw):return raw if raw<128 else raw-256


def evaluate(entry,memory,calibration,context,sr_before,frame_before,sp,continuation):
    if (type(entry) is not int or entry!=ENTRY or type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(raw) is not int or not 0<=raw<=MASK for raw in context)
            or type(sr_before) is not int or sr_before&0x3F1!=context[18]
            or type(sp) is not int or sp&3 or type(continuation) is not int):
        raise ValueError('the high-bit clear equations require complete raw CPU,frame,RAM inputs')
    rows=[raw[0x8C45C-start:0x8C460-start] for start,raw in calibration.items()
        if start<=0x8C45C and 0x8C460<=start+len(raw)]
    if len(rows)!=1 or rows[0]!=b'\x01\x00\x57\x18':
        raise ValueError('the high-bit clear equations replace the exact native pointer relocation')
    base=RAM_BASE+0x5718;index=context[4];inert=index==SENTINEL
    triple=(3*index)&MASK;member=None if inert else (base+triple+1)&MASK
    if member is not None and not RAM_BASE<=member<RAM_BASE+len(memory):
        raise ValueError('the high-bit clear raw index leaves the complete declared ordinary-memory premise')
    ram=bytearray(memory);incoming=None if inert else memory[member-RAM_BASE]
    published=None if inert else incoming&0x7F
    if not inert:ram[member-RAM_BASE]=published
    path=SENTINEL_PATH if inert else ACTIVE_PATH
    updates={0x8C348:{1:base},0x8C34A:{0:index},0x8C34C:{},0x8C34E:{},
        0x8C350:{6:base},0x8C352:{2:index},0x8C354:{2:(2*index)&MASK},
        0x8C356:{2:triple},0x8C358:{6:(base+triple)&MASK},
        0x8C35A:{0:0 if inert else signed_byte(incoming)&MASK},
        0x8C35C:{0:0 if inert else published},0x8C35E:{},0x8C360:{},0x8C362:{},0x8C364:{}}
    cpu=list(context[:15])+[sp];states={};current_sr=sr_before
    for site in path:
        for register,raw in updates[site].items():cpu[register]=raw
        if site==0x8C34C:current_sr=(current_sr&~1)|int(inert)
        elif site==0x8C354:current_sr=(current_sr&~1)|(index>>31)
        states[site]=dict(registers=tuple(cpu),gbr=context[15],mach=context[16],macl=context[17],sr=current_sr,pr=continuation)
    operands=[dict(site=0x8C348,mode='read',address=0x8C45C,width_bytes=4,register=1,domain='rom',bytes=rows[0].hex())]
    if not inert:
        operands.extend((dict(site=0x8C35A,mode='read',address=member,width_bytes=1,register=0,domain='ram',bytes=bytes([incoming]).hex()),
            dict(site=0x8C360,mode='write',address=member,width_bytes=1,register=0,domain='ram',bytes=bytes([published]).hex())))
    branches=[dict(site=0x8C34E,kind='taken' if inert else 'fallthrough',target=0x8C362 if inert else 0x8C350,delay=False),
        dict(site=0x8C362 if inert else 0x8C35E,kind='return',target=continuation,delay=True)]
    return dict(entry=entry,index=index,inert=inert,member=member,incoming=incoming,published=published,
        registers=tuple(cpu[:15]),sr=current_sr,gbr=context[15],mach=context[16],macl=context[17],pr=continuation,sp=sp,
        frame=frame_before,ram=bytes(ram),path=path,states=states,operands=operands,calls=[],branches=branches,
        exit=(current_sr,continuation,context[17],context[16],context[15],*reversed(cpu[:15])))
