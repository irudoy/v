"""Independent ordered same-member OR08/OR40 and complete diagnostic writer CPU equations."""
MASK=0xFFFFFFFF
RAM_BASE=0x01000000
INDICES=(0,1,0x47,0x123,0x128,0x129,0x156)
PATH=tuple(range(0x8C942,0x8C968,2))


def signed_byte(raw):return raw if raw<128 else raw-256


def evaluate(entry,memory,calibration,context,sr_before,frame_before,sp,continuation):
    if (type(entry) is not int or entry!=0x8C942 or type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(raw) is not int or not 0<=raw<=MASK for raw in context)
            or context[4] not in INDICES or type(sr_before) is not int or sr_before&0x3F1!=context[18]
            or type(sp) is not int or sp&3 or type(continuation) is not int):
        raise ValueError('the bits3/6 equations require exact bounded index and complete CPU,frame,RAM inputs')
    def pool(address,width):
        rows=[raw[address-start:address-start+width] for start,raw in calibration.items()
            if start<=address and address+width<=start+len(raw)]
        if len(rows)!=1:raise ValueError('the bits3/6 equations omit a unique complete PC operand')
        return int.from_bytes(rows[0],'big')
    base,flag_base,flag_offset=pool(0x8C98C,4),pool(0x8C998,4),pool(0x8C986,2)
    if (base,flag_base,flag_offset)!=(RAM_BASE+0x5718,RAM_BASE+0x4558,0xB27):
        raise ValueError('the bits3/6 equations replace an exact aliased native PC operand')
    index=context[4];triple=(3*index)&MASK;member=(base+triple+2)&MASK
    incoming=memory[member-RAM_BASE];first=incoming|8;published=first|0x40
    ram=bytearray(memory);ram[member-RAM_BASE]=published;ram[0x507F]=1
    registers=list(context[:15]);registers[0]=flag_offset;registers[1]=base;registers[2]=1
    registers[5]=triple;registers[6]=flag_base;sr=(sr_before&~1)|(index>>31)
    operands=[dict(site=site,mode=mode,address=address,width_bytes=width,register=register,domain=domain,bytes=raw.hex())
        for site,mode,address,width,register,domain,raw in (
            (0x8C942,'read',0x8C98C,4,1,'rom',base.to_bytes(4,'big')),
            (0x8C94E,'read',member,1,0,'ram',bytes([incoming])),
            (0x8C954,'write',member,1,0,'ram',bytes([first])),
            (0x8C95A,'read',member,1,0,'ram',bytes([first])),
            (0x8C95E,'write',member,1,0,'ram',bytes([published])),
            (0x8C960,'read',0x8C998,4,6,'rom',flag_base.to_bytes(4,'big')),
            (0x8C962,'read',0x8C986,2,0,'rom',flag_offset.to_bytes(2,'big')),
            (0x8C966,'write',RAM_BASE+0x507F,1,2,'ram',b'\x01'))]
    updates={0x8C942:{1:base},0x8C944:{5:index},0x8C946:{5:(2*index)&MASK},0x8C948:{6:base},
        0x8C94A:{5:triple},0x8C94C:{6:(base+triple)&MASK},0x8C94E:{0:signed_byte(incoming)&MASK},
        0x8C950:{2:1},0x8C952:{0:(signed_byte(incoming)|8)&MASK},0x8C954:{},0x8C956:{6:base},
        0x8C958:{6:(base+triple)&MASK},0x8C95A:{0:signed_byte(first)&MASK},
        0x8C95C:{0:(signed_byte(first)|0x40)&MASK},0x8C95E:{},0x8C960:{6:flag_base},
        0x8C962:{0:flag_offset},0x8C964:{},0x8C966:{}}
    cpu=list(context[:15])+[sp];states={};current_sr=sr_before
    for site in PATH:
        for register,raw in updates[site].items():cpu[register]=raw
        if site==0x8C946:current_sr=sr
        states[site]=dict(registers=tuple(cpu),gbr=context[15],mach=context[16],macl=context[17],sr=current_sr,pr=continuation)
    return dict(entry=entry,index=index,member=member,incoming=incoming,first=first,published=published,
        registers=tuple(registers),sr=sr,gbr=context[15],mach=context[16],macl=context[17],pr=continuation,sp=sp,
        frame=frame_before,ram=bytes(ram),path=PATH,states=states,operands=operands,calls=[],
        branches=[dict(site=0x8C964,kind='return',target=continuation,delay=True)],
        exit=(sr,continuation,context[17],context[16],context[15],*reversed(registers)))
