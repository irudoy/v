"""Independent existing history transfer and complete pedal high-state equations."""

CONTROL_SIZES = ((33778, 1), (34572, 1), (34573, 1), (34961, 1), (34962, 1), (34963, 1), (34964, 1), (34992, 1), (34993, 1), (34994, 1), (34996, 1), (35236, 1), (35237, 1), (35647, 1), (35818, 1), (35819, 1), (35821, 1), (35956, 1), (35957, 1), (36037, 1), (36038, 1), (36247, 1), (36248, 1), (36249, 1), (36250, 1), (36251, 1), (36277, 1), (36828, 2), (36830, 2), (38198, 2))


def integer(memory,address,size):
    return int.from_bytes(memory[address:address+size],'big')


def snapshot(memory):
    """Numerical expectation for the exact registered history and following block."""
    if type(memory) is not bytes or len(memory)!=65536:
        raise ValueError('the pedal snapshot equations require complete raw RAM')
    out=bytearray(memory)
    for source,destination,size in ((0x2668,0x266C,2),(0x266A,0x2668,2),(0x2672,0x266E,4)):
        out[destination:destination+size]=out[source:source+size]
    out[0x267A:0x277E]=out[0x277E:0x2882]
    return bytes(out)


def uniform_word_curve(table,coordinate):
    if type(table) is not bytes or len(table)!=16 or type(coordinate) is not int or not 0<=coordinate<=65535:
        raise ValueError('the pedal threshold curve requires all eight physical words and its actual coordinate')
    if coordinate>=57344:
        value=integer(table,14,2)
        return dict(index=7,fraction=0,value=value,returned=value if value<32768 else value-65536)
    index=coordinate>>13;fraction=(coordinate&8191)<<3
    first,last=integer(table,2*index,2),integer(table,2*index+2,2)
    step=(abs(last-first)*fraction)>>16
    value=first+step if last>=first else first-step
    return dict(index=index,fraction=fraction,value=value,returned=value)


def caller(memory,calibration,context):
    if type(memory) is not bytes or len(memory)!=65536:
        raise ValueError('the pedal comparator equations require complete raw RAM')
    if (type(context) not in (list,tuple) or len(context)!=20
            or any(type(v) is not int or not 0<=v<=0xFFFFFFFF for v in context) or context[18]&~0x3F1):
        raise ValueError('the pedal comparator equations require all twenty raw CPU/SR inputs')
    for address,size in (*CONTROL_SIZES,(0x1473A,16)):
        if type(calibration.get(address)) is not bytes or len(calibration[address])!=size:
            raise ValueError('the pedal comparator equations lose complete physical controls or curve words')
    after=bytearray(memory);publications=[];locals=[]

    def get(address,size=1):return integer(after,address,size)
    def rom(address):return int.from_bytes(calibration[address],'big')
    def put(site,address,value,size=1):
        value&=(1<<(8*size))-1
        after[address:address+size]=value.to_bytes(size,'big')
        publications.append(dict(site=site,address=address,size=size,value=value))
    def bits(site,address,mask,enabled):
        put(site,address,(get(address)|mask) if enabled else (get(address)&~mask))

    curve_mode=bool(rom(0x870C)&128)
    curve=None;threshold=None;adjusted_sample=None
    previous_state=get(0x24B6)
    if curve_mode:
        coordinate=min(65535,get(0x110E)<<11)
        curve=uniform_word_curve(calibration[0x1473A],coordinate)
        put(0x47A9A,0x1A42,curve['value'],2)
        if not get(0x245E)&64:
            adjusted_sample=get(0x266E,2)+(51 if get(0x24B4)&64 else 0)
            threshold=get(0x1A42,2)
            high=adjusted_sample>=threshold
            bits(0x47AC6 if high else 0x47AC4,0x24B4,64,high)
        if get(0x24B4)&64:
            state_high=bool(get(0x24E8))
        else:
            put(0x47ADE,0x24E8,rom(0x8BEB));state_high=False
        put(0x47AE4,0x24B6,(previous_state|2) if state_high else (previous_state&~2))
    else:
        threshold=rom(0x8FDE) if get(0x246D)&128 else rom(0x8FDC)
        adjusted_sample=get(0x266E,2)
        high=adjusted_sample>=threshold
        bits(0x47BB2 if high else 0x47BAE,0x246A,128,high)
        if get(0x246A)&128:
            timer=get(0x24E8)
            if get(0x110E)<rom(0x8DB5):
                state_high=bool(timer)
            elif timer and previous_state&2:
                state_high=True
            else:
                put(0x47BE8,0x24E8,rom(0x8BEB));state_high=False
        else:
            put(0x47BE8,0x24E8,rom(0x8BEB));state_high=False
        put(0x47BEE,0x24B6,(previous_state|2) if state_high else (previous_state&~2))
    permitted=(get(0x24D7)==0 or bool(get(0x2470)&4)) and not get(0x424F)&8
    diagnostic=None
    if permitted:
        diagnostic=bool(get(0x5719)&128)
        permitted=not diagnostic or (curve_mode and bool(rom(0x8B3F)&128))
    if permitted and curve_mode:
        local=get(0x2470);locals.append(dict(site=0x47B10,mode='write',value=local))
        permitted=not rom(0x8B3F)&128 and bool(rom(0x870C)&128) and not get(0x245E)&64
    elif permitted:
        local=get(0x2470);locals.append(dict(site=0x47C10,mode='write',value=local))
    if permitted:
        state_high=bool(get(0x24B6)&2)
        if state_high:
            put(0x47C1C,0x24D7,rom(0x83F2))
            locals.append(dict(site=0x47C1E,mode='read',value=local))
            local|=4
        else:
            locals.append(dict(site=0x47C24,mode='read',value=local));local&=~4
        locals.append(dict(site=0x47C28,mode='write',value=local&255))
        put(0x47C2C,0x2470,local)
    else:
        bits(0x47C30,0x2470,4,False)
    initial_2471=get(0x2471)
    temperature=get(0x11AE)
    companion=None
    if not rom(0x870D)&4:
        if temperature<rom(0x8893):decision='clear'
        elif temperature>=rom(0x8892):decision='set'
        else:decision='hold'
    elif temperature>=rom(0x88B0):decision='set'
    else:
        companion=get(0x10EC)
        if companion>=rom(0x89A4) or companion<=rom(0x8D98):decision='set'
        elif temperature>=rom(0x88B2) and companion>=rom(0x8D97):decision='set'
        elif temperature>=rom(0x8892) and companion>=rom(0x89A5):decision='set'
        elif (temperature<rom(0x8893) and temperature>0 and companion<rom(0x8D99)
              and companion>rom(0x8D9B)):decision='clear'
        elif (temperature<rom(0x8894) and temperature>0 and companion<rom(0x8D9A)
              and companion>=rom(0x8D99)):decision='clear'
        else:decision='hold'
    if decision!='hold':bits(0x47CF6 if decision=='set' else 0x47CF2,0x246A,64,decision=='set')
    status_4184=bool(get(0x4184)&64)
    if status_4184:put(0x47D08,0x2559,rom(0x8BED))
    status_2471=(initial_2471|128) if status_4184 or get(0x2559) else (initial_2471&~128)
    put(0x47D1E,0x2471,status_2471)
    if get(0x2471)&64:
        if temperature>=rom(0x88B4):bits(0x47DB4,0x2471,64,False)
    elif temperature<rom(0x88B1):bits(0x47DB4,0x2471,64,True)
    bits(0x47DC8,0x2470,1,bool(get(0x2471)&192))
    throttle=get(0x1071)
    throttle_threshold=rom(0x8CC6) if get(0x2471)&32 else rom(0x8CC5)
    bits(0x47DF4 if throttle>=throttle_threshold else 0x47DF0,0x2471,32,throttle>=throttle_threshold)
    current_2470=get(0x2470)
    timer_reload=False;inhibit_written=None
    if not current_2470&2:
        if throttle<rom(0x8C74):timer_reload=True
        elif get(0x1024,2)<rom(0x9536) and temperature<rom(0x8891):timer_reload=True
        elif get(0x42B4)==0:
            bits(0x47E3A,0x2470,2,True);inhibit_written=True
    else:
        if throttle<rom(0x8C75) or (get(0x1024,2)<rom(0x9536) and temperature<rom(0x8891)):
            bits(0x47E64,0x2470,2,False);inhibit_written=False
        timer_reload=True
    if timer_reload:put(0x47E6E,0x42B4,rom(0x8BEA))
    current_2470=get(0x2470)
    final_high=bool(current_2470&4 or get(0x246A)&64 or current_2470&1 or get(0x2471)&56 or current_2470&2)
    bits(0x47EA2 if final_high else 0x47E9E,0x24C6,128,final_high)
    return dict(memory=bytes(after),publications=publications,locals=locals,curve_mode=curve_mode,curve=curve,
                adjusted_sample=adjusted_sample,threshold=threshold,diagnostic=diagnostic,
                request_permitted=permitted,temperature=temperature,companion=companion,
                temperature_decision=decision,status_4184=status_4184,timer_reload=timer_reload,
                inhibit_written=inhibit_written,final_high=final_high,pedal_high=bool(get(0x246A)&128))
