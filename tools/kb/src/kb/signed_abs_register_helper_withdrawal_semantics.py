"""Independent full raw32 signed-magnitude helper and complete leaf state."""

MASK=0xFFFFFFFF
ENTRY=0x22590


def evaluate(entry,memory,calibration,context,sr_before,frame_before,sp,continuation):
    if (type(entry) is not int or entry!=ENTRY or type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(value) is not int or not 0<=value<=MASK for value in context)
            or type(sr_before) is not int or sr_before&0x3F1!=context[18]
            or type(sp) is not int or sp&3 or type(continuation) is not int
            or calibration!={ENTRY:bytes.fromhex('44158900644b000b6043')}):
        raise ValueError('the signed-magnitude helper lacks complete raw32 CPU, RAM, frame, SR or immutable code observations')
    incoming=context[4]
    signed=incoming if incoming<0x80000000 else incoming-0x100000000
    positive=signed>0
    magnitude=(signed if positive else -signed)&MASK
    registers=list(context[:15]);registers[0]=registers[4]=magnitude
    sr=(sr_before&~1)|int(positive)
    path=(0x22590,0x22592,*(() if positive else (0x22594,)),0x22596,0x22598)
    branches=[dict(site=0x22592,target=0x22596 if positive else 0x22594,
        kind='taken' if positive else 'fallthrough',delay=False),
        dict(site=0x22596,target=continuation,kind='return',delay=True)]
    return dict(entry=entry,registers=tuple(registers),sr=sr,gbr=context[15],mach=context[16],
        macl=context[17],pr=continuation,sp=sp,frame=frame_before,ram=memory,path=path,branches=branches,
        tags=dict(incoming=incoming,signed=signed,positive=positive,zero=(incoming==0),
            minimum_word=(incoming==0x80000000),magnitude=magnitude),
        exit=(sr,continuation,context[17],context[16],context[15],*reversed(registers)))
