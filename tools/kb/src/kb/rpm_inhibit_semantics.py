"""Independent byte-preserving vehicle/main FSM equations over complete inputs."""


def vehicle(before,calibration):
    if type(before) is not bytes or len(before)!=65536:
        raise ValueError('the vehicle contributor equation requires complete RAM')
    memory=bytearray(before);state=before[0x24A6];control=before[0x24A7];speed=before[0x110E]
    delay=before[0x24F6];on=calibration[0x8DB7][0];off=calibration[0x8DC3][0]
    active=bool(state&1);newly_armed=False;cleared_by_gate=False
    if active:
        if control&32:
            state&=254;memory[0x24A6]=state;cleared_by_gate=True
        if speed<off:
            control&=127;memory[0x24A7]=control
            state=memory[0x24A6]&254;memory[0x24A6]=state
    elif speed>=on:
        if not control&128:
            newly_armed=True;delay=calibration[0x8CAF][0];memory[0x24F6]=delay
            control|=128;memory[0x24A7]=control
        if delay==0 and not control&32:
            state|=1;memory[0x24A6]=state
    else:
        control&=127;memory[0x24A7]=control
    return dict(memory=bytes(memory),state=state,control=control,speed=speed,delay=delay,on=on,off=off,
        entry_active=active,newly_armed=newly_armed,cleared_by_gate=cleared_by_gate,output=state&1)


def main(before,calibration):
    if type(before) is not bytes or len(before)!=65536:
        raise ValueError('the main RPM contributor equation requires complete RAM')
    memory=bytearray(before);flags=before[0x2497];delay=before[0x24F1]
    rpm=int.from_bytes(before[0x11BC:0x11BE],'big');config=calibration[0x8B38][0]
    conditioned=bool(config&128 and before[0x2499]&2 and before[0x2494]&32 and before[0x244F]&4)
    pair=2 if conditioned else int(bool(before[0x2468]&16))
    words=[int.from_bytes(calibration[0x934E][index:index+2],'big') for index in range(0,12,2)]
    on=words[pair if pair<2 else 4];off=words[pair+2 if pair<2 else 5]
    active=bool(flags&4);newly_armed=False;released=False
    if active:
        if rpm<off:
            flags&=249;memory[0x2497]=flags;released=True
    elif rpm>=on:
        if not flags&2:
            newly_armed=True;delay=calibration[0x8C69][0];memory[0x24F1]=delay
            flags|=2;memory[0x2497]=flags
        if delay==0:
            flags|=4;memory[0x2497]=flags
    else:
        flags&=253;memory[0x2497]=flags
    return dict(memory=bytes(memory),rpm=rpm,config=config,pair=pair,on=on,off=off,flags=flags,delay=delay,
        entry_active=active,newly_armed=newly_armed,released=released,output=int(bool(flags&4)))


def compose(before,calibration,prior):
    if type(prior) is not int or not 0<=prior<=0xFFFFFFFF:
        raise ValueError('the bounded caller equation requires its explicit full incoming R0')
    first=vehicle(before,calibration);second=main(first['memory'],calibration)
    return dict(memory=second['memory'],vehicle=first,main=second,
        output=(second['output'],prior|first['output']),prior=prior)


def summary(before,path,incoming_r0,incoming_r2,incoming_r14):
    if (type(before) is not bytes or len(before)!=65536 or path not in ('maf-summary','shared-status')
            or any(type(value) is not int or not 0<=value<=0xFFFFFFFF
                for value in (incoming_r0,incoming_r2,incoming_r14))):
        raise ValueError('the bounded summary equation requires complete RAM and explicit full R0/R2/R14')
    if path=='maf-summary':
        status=before[0x2448];rpm=before[0x11B2]
        output=int(bool(status&128) and rpm>=192);prior=incoming_r0
    else:
        status=before[0x418C];rpm=None
        output=int(bool(status&2));prior=incoming_r2
    return dict(path=path,memory=before,status=status,rpm=rpm,incoming_r0=incoming_r0,
        incoming_r2=incoming_r2,incoming_r14=incoming_r14,output=(output,incoming_r14|prior))


def composite(before,calibration,incoming_r0,incoming_r2,incoming_r14):
    from kb.apc_reset_offset_semantics import curve
    if (type(before) is not bytes or len(before)!=65536
            or any(type(value) is not int or not 0<=value<=0xFFFFFFFF
                for value in (incoming_r0,incoming_r2,incoming_r14))
            or len(calibration[0x9462])!=2 or len(calibration[0x12A32])!=8):
        raise ValueError('the bounded composite equation requires complete RAM, full incoming words and exact curve/hysteresis inputs')
    memory=bytearray(before)
    seed=int(bool(before[0x41EA]&128))
    low_coordinate=before[0x11B3]+(8 if before[0x2489]&1 else 0)
    low_active=low_coordinate>=72
    memory[0x2489]=(before[0x2489]&254)|int(low_active)
    low_output=bool(before[0x245D]&64 and before[0x2458]&32 and low_active)
    coordinate=4*min(before[0x110E],63)
    lookup=curve(calibration[0x12A32],coordinate)
    threshold=2*lookup['value']
    memory[0x17CA:0x17CC]=threshold.to_bytes(2,'big')
    rpm=int.from_bytes(before[0x11BC:0x11BE],'big')
    hysteresis=int.from_bytes(calibration[0x9462],'big')
    high_coordinate=rpm+(hysteresis if before[0x249F]&4 else 0)
    high_active=high_coordinate>=threshold
    memory[0x249F]=(before[0x249F]&251)|(4 if high_active else 0)
    high_output=bool((before[0x24CE]&4 or before[0x24D2]&1) and high_active)
    return dict(path='composite-status',memory=bytes(memory),seed=seed,low_coordinate=low_coordinate,
        low_active=low_active,low_output=low_output,coordinate=coordinate,curve=lookup,
        threshold=threshold,rpm=rpm,hysteresis=hysteresis,high_coordinate=high_coordinate,
        high_active=high_active,high_output=high_output,incoming_r0=incoming_r0,
        incoming_r2=incoming_r2,incoming_r14=incoming_r14,
        output=(int(bool(seed or low_output or high_output)),incoming_r14|incoming_r2))
