"""Separate full-R4 indexed byte OR and exact complete leaf-state equations."""
MASK=0xFFFFFFFF
RAM_BASE=0x01000000
INDICES=(0,1,0x47,0x123,0x128,0x129,0x156)
PATH=tuple(range(0x8C968,0x8C984,2))


def signed_byte(raw):return raw if raw<128 else raw-256


def evaluate(entry,memory,calibration,context,sr_before,frame_before,sp,continuation):
    if (type(entry) is not int or entry!=0x8C968 or type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(raw) is not int or not 0<=raw<=MASK for raw in context)
            or context[4] not in INDICES or type(sr_before) is not int or sr_before&0x3F1!=context[18]
            or type(sp) is not int or sp&3 or type(continuation) is not int):
        raise ValueError('the bit4 equations require exact bounded index, complete CPU, frame and RAM inputs')
    def pool(address,width):
        rows=[raw[address-start:address-start+width] for start,raw in calibration.items()
            if start<=address and address+width<=start+len(raw)]
        if len(rows)!=1:raise ValueError('the bit4 equations omit a unique complete PC operand')
        return int.from_bytes(rows[0],'big')
    base,flag_base,flag_offset=pool(0x8C98C,4),pool(0x8C998,4),pool(0x8C988,2)
    if (base,flag_base,flag_offset)!=(RAM_BASE+0x5718,RAM_BASE+0x4558,0xB34):
        raise ValueError('the bit4 equations replace an exact aliased native PC operand')
    index=context[4];triple=(3*index)&MASK;member=(base+triple+2)&MASK
    offset=member-RAM_BASE;incoming=memory[offset];published=incoming|0x10
    ram=bytearray(memory);ram[offset]=published;ram[0x508C]=1
    registers=list(context[:15]);registers[0]=flag_offset;registers[1]=base;registers[2]=1;registers[6]=flag_base
    sr=(sr_before&~1)|(index>>31)
    operands=[dict(site=site,mode=mode,address=address,width_bytes=width,register=register,domain=domain,bytes=raw.hex())
        for site,mode,address,width,register,domain,raw in (
            (0x8C968,'read',0x8C98C,4,1,'rom',base.to_bytes(4,'big')),
            (0x8C974,'read',member,1,0,'ram',bytes([incoming])),
            (0x8C97A,'write',member,1,0,'ram',bytes([published])),
            (0x8C97C,'read',0x8C998,4,6,'rom',flag_base.to_bytes(4,'big')),
            (0x8C97E,'read',0x8C988,2,0,'rom',flag_offset.to_bytes(2,'big')),
            (0x8C982,'write',RAM_BASE+0x508C,1,2,'ram',b'\x01'))]
    # Closed scalar carrier equations are independent of instruction decoding.
    updates={0x8C968:{1:base},0x8C96A:{6:base},0x8C96C:{2:index},0x8C96E:{2:(2*index)&MASK},
        0x8C970:{2:triple},0x8C972:{6:(base+triple)&MASK},0x8C974:{0:signed_byte(incoming)&MASK},
        0x8C976:{2:1},0x8C978:{0:(signed_byte(incoming)|0x10)&MASK},0x8C97A:{},
        0x8C97C:{6:flag_base},0x8C97E:{0:flag_offset},0x8C980:{},0x8C982:{}}
    cpu=list(context[:15])+[sp];states={};current_sr=sr_before
    for site in PATH:
        for register,raw in updates[site].items():cpu[register]=raw
        if site==0x8C96E:current_sr=sr
        states[site]=dict(registers=tuple(cpu),gbr=context[15],mach=context[16],macl=context[17],sr=current_sr,pr=continuation)
    return dict(entry=entry,index=index,member=member,incoming=incoming,published=published,
        registers=tuple(registers),sr=sr,gbr=context[15],mach=context[16],macl=context[17],pr=continuation,sp=sp,
        frame=frame_before,ram=bytes(ram),path=PATH,states=states,operands=operands,calls=[],
        branches=[dict(site=0x8C980,kind='return',target=continuation,delay=True)],
        exit=(sr,continuation,context[17],context[16],context[15],*reversed(registers)))
