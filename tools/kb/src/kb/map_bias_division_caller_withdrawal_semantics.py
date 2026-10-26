"""Independent natural caller equations with the exact constant second-axis input."""

MASK=0xFFFFFFFF
RAM_BASE=0x01000000


def signed16(value):return value if value<0x8000 else value-0x10000


def byte_axis(values,coordinate):
    """The actual rightmost byte-axis scan uses byte knots shifted by four."""
    if type(values) is not bytes or len(values)!=16 or type(coordinate) is not int or not 0<=coordinate<=0xFFFF:
        raise ValueError('the map-bias caller changes its complete byte axis or unsigned-word coordinate')
    index=15;reads=[]
    while True:
        knot=values[index]<<4;reads.append(index)
        if coordinate==knot:return dict(index=index,fraction=0,reads=tuple(reads),division=None)
        if knot<=coordinate:
            if index==15:return dict(index=index,fraction=0,reads=tuple(reads),division=None)
            upper=values[index+1]<<4;denominator=upper-knot
            if not knot<coordinate<upper or denominator<=0:
                raise ValueError('the actual byte-axis scan loses its selected positive local bracket')
            numerator=(coordinate-knot)<<16
            return dict(index=index,fraction=numerator//denominator,reads=tuple(reads),
                division=dict(numerator=numerator,denominator=denominator))
        index-=1
        if index<0:return dict(index=0,fraction=0,reads=tuple(reads),division=None)


def interpolate(low,high,fraction):
    if not 0<=low<=0xFFFF or not 0<=high<=0xFFFF or not 0<=fraction<=0xFFFF:
        raise ValueError('the map-bias caller changes a word endpoint or actual fractional width')
    if high>=low:return low+(((high-low)*fraction&MASK)>>16)
    return low-(((low-high)*fraction&MASK)>>16)


def lookup(map_words,axis_bytes,axis_words,coordinate):
    if type(map_words) is not bytes or len(map_words)!=512 or type(axis_words) is not bytes or len(axis_words)!=32:
        raise ValueError('the map-bias caller lacks its complete physical map and second axis')
    selected=byte_axis(axis_bytes,coordinate)
    # The caller stores FFFF as the actual fifth word. Every possible final
    # unsigned-word knot is <= FFFF, so the word-axis entry retains offset30
    # and fraction0 without searching another knot or dividing.
    last_word=int.from_bytes(axis_words[30:32],'big')
    offset=selected['index']*32+30
    low=int.from_bytes(map_words[offset:offset+2],'big')
    upper=None
    if selected['fraction']:
        if selected['index']>=15:raise ValueError('an endpoint cannot supply an undeclared following row')
        upper=int.from_bytes(map_words[offset+32:offset+34],'big')
        value=interpolate(low,upper,selected['fraction']);raw_return=value
    else:value=low;raw_return=signed16(low)&MASK
    return dict(axis=selected,second_axis_offset=30,second_axis_fraction=0,
        second_axis_last_word=last_word,second_axis_equal=(last_word==0xFFFF),
        offset=offset,low=low,high=upper,value=value,raw_return=raw_return)


def sequence(memory,calibrations):
    if type(memory) is not bytes or len(memory)!=65536 or type(calibrations) is not dict:
        raise ValueError('the map-bias caller requires complete raw ordinary memory and calibration bytes')
    ram=bytearray(memory);writes=[]
    def word(at):return int.from_bytes(ram[at:at+2],'big')
    def write(site,at,value,register):
        raw=(value&0xFFFF).to_bytes(2,'big');ram[at:at+2]=raw
        writes.append(dict(site=site,address=RAM_BASE+at,width_bytes=2,register=register,bytes=raw.hex()))
    same_mode=ram[0x1880]==ram[0x18B4]
    prior=word(0x1878);other=word(0x188C)
    first=abs(prior-other) if same_mode else min(0xFFFF,prior+other)
    write(0x70316,0x142A,first,0)
    query=word(0x1702)
    table=lookup(calibrations[0xE98E],calibrations[0x11D0C],calibrations[0x14114],query)
    centered=table['value']-0x8000;positive=max(10,centered)
    write(0x70348,0x19C4,positive,2)
    denominator=positive-5
    if not 5<=denominator<=32762:
        raise ValueError('the complete caller loses its independently positive bounded divisor')
    source=signed16(word(0x243A));magnitude=abs(source)
    numerator=magnitude<<16;quotient=numerator//denominator;published=min(0xFFFF,quotient)
    write(0x7037A,0x1878,published,2)
    return dict(ram=bytes(ram),writes=writes,same_mode=same_mode,prior=prior,other=other,
        first_term=first,query=query,lookup=table,centered=centered,positive_term=positive,
        denominator=denominator,signed_source=source,magnitude=magnitude,numerator=numerator,
        quotient=quotient,published=published,final_cap=(quotient>0xFFFF))


def evaluate(entry,memory,calibrations,context,sr_before,frame_before,sp,continuation):
    if (type(entry) is not int or entry!=0x702C6 or type(context) is not tuple or len(context)!=20
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(sp) is not int or sp&3 or type(continuation) is not int):
        raise ValueError('the map-bias caller lacks its exact complete entry,context,frame or continuation')
    value=sequence(memory,calibrations);frame=bytearray(frame_before)
    def word32(offset,raw):frame[160+offset:164+offset]=(raw&MASK).to_bytes(4,'big')
    for offset,raw in ((-4,context[12]),(-8,context[13]),(-12,context[14]),
            (-16,continuation),(-20,context[15])):word32(offset,raw)
    frame[138:140]=bytes.fromhex('ffff')
    fraction=value['lookup']['axis']['fraction'];index=value['lookup']['axis']['index']
    word32(-40,index)
    decreasing=(value['lookup']['high'] is not None and value['lookup']['high']<value['lookup']['low'])
    word32(-36,value['lookup']['low'] if decreasing else fraction)
    long_division=(value['denominator']<<8)<=value['numerator']
    word32(-32,fraction if long_division else 0x7032C)
    word32(-28,value['denominator'])
    known={0:0x5EC,2:value['published'],4:value['magnitude'],5:0xFFFF,6:0x21CE0,7:0x26740}
    known.update({index:context[index] for index in range(8,15)})
    return dict(value,frame=bytes(frame),known_registers=known,gbr=context[15],mach=context[16],
        macl=context[17],sp=sp,pr=continuation,long_division=long_division,
        sr=(sr_before&~0x301)|int(value['final_cap']),sr_mask=MASK^0x100)
