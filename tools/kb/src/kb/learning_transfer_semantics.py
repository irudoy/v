"""Existing learned-grid integer equations over complete explicit RAM and calibrations.

These scalar equations provide no execution, owning identity, units, cadence
or hardware admission. Raw producers contain no expected scalar outputs.
"""


def word(memory,address):
    return int.from_bytes(memory[address:address+2],'big')


def put_word(memory,address,value):
    memory[address:address+2]=(value&65535).to_bytes(2,'big')


def clipped_index(value,axis,old,hysteresis,scale):
    raw=0
    for threshold in axis[1:]:
        if value<scale*threshold:break
        raw+=1
    selected=raw
    if raw>old and value<scale*(axis[old+1]+hysteresis):selected-=1
    if raw<old and value>scale*(axis[old]-hysteresis):selected+=1
    return selected,raw


def auxiliary(before,bank,index,decay,lower,upper):
    if (type(before) is not bytes or len(before)!=65536 or type(bank) is not int or bank not in (0,1)
            or type(index) is not int or index not in (*range(64),255)
            or any(type(value) is not int or not 0<=value<=255 for value in (decay,lower,upper))):
        raise ValueError('the auxiliary equations need a complete declared bank, cell and byte calibration state')
    memory=bytearray(before);base=0x49B0 if bank else 0x49F0
    if index==255:
        memory[base:base+64]=bytes(64)
        return dict(memory=bytes(memory),reset=True,bank=bank,base=base,index=index)
    incoming=before[base+index];incremented=(incoming+1)&255
    decayed=incremented+decay>255
    retained=max(0,incremented-decay) if decayed else incremented
    input=word(before,0x134E+bank*2)
    outside=not lower*256<=input<upper*256
    output=0 if outside else retained;memory[base+index]=output
    return dict(memory=bytes(memory),reset=False,bank=bank,base=base,index=index,input=input,
        incoming=incoming,incremented=incremented,decayed=decayed,retained=retained,outside=outside,output=output)


def selection(before,bank,load_axis,speed_axis,load_hysteresis,speed_hysteresis,lower,upper):
    if (type(before) is not bytes or len(before)!=65536 or type(bank) is not int or bank not in (0,1)
            or len(load_axis)!=8 or len(speed_axis)!=8
            or any(type(value) is not int or not 0<=value<=255
                   for value in (*load_axis,*speed_axis,load_hysteresis,speed_hysteresis,lower,upper))):
        raise ValueError('the grid selector needs its exact bank, full RAM and byte axis/calibration inputs')
    load=word(before,0x1024);speed=before[0x11AE];packed=before[0x130A+bank]
    load_index,load_raw=clipped_index(load,load_axis,packed&7,load_hysteresis,256)
    speed_index,speed_raw=clipped_index(speed,speed_axis,(packed>>3)&7,speed_hysteresis//4,1)
    index=8*speed_index+load_index;grid=0x4B10 if bank else 0x4B90
    incoming=word(before,grid+index*2);flag=before[0x41B5];diagnostic=before[0x5A94]
    called=lower*256<=incoming<=upper*256 and not flag&1
    reset=not lower*256<=incoming<=upper*256 or bool(flag&1) or bool(diagnostic&128)
    memory=bytearray(before);output=25600 if reset else incoming
    if reset:
        memory[grid:grid+128]=bytes.fromhex('6400')*64
        auxiliary_base=0x49B0 if bank else 0x49F0
        memory[auxiliary_base:auxiliary_base+64]=bytes(64)
        put_word(memory,0x45A0+bank*2,0)
    put_word(memory,0x2306+bank*2,output);memory[0x130A+bank]=index
    return dict(memory=bytes(memory),bank=bank,load=load,speed=speed,packed=packed,
        load_index=load_index,load_raw=load_raw,speed_index=speed_index,speed_raw=speed_raw,
        index=index,grid=grid,incoming=incoming,output=output,reset=reset,predicate_called=called)


def learning(before,bank,thresholds,coefficients,initial,decay,lower,upper,aux_lower,aux_upper):
    if (type(before) is not bytes or len(before)!=65536 or type(bank) is not int or bank not in (0,1)
            or len(thresholds)!=3 or len(coefficients)!=4
            or any(type(value) is not int or not 0<=value<=255
                   for value in (*thresholds,*coefficients,initial,decay,lower,upper,aux_lower,aux_upper))):
        raise ValueError('the learning equations need complete declared bank, RAM and byte calibration inputs')
    index=before[0x130A+bank]
    if index>=64:raise ValueError('the learned-cell index leaves its declared bounded domain')
    enabled=bool(before[0x1458]&(1<<bank)) and bool(before[0x1457]&(1<<bank))
    if not enabled:return dict(memory=before,bank=bank,index=index,enabled=False)
    input=word(before,0x134E+bank*2);stft=word(before,0x22DC+bank*2)
    previous=word(before,0x2306+bank*2);base=0x49B0 if bank else 0x49F0
    counter=before[base+index];region=0
    for threshold in thresholds:
        if abs(input-25600)<=256*threshold:break
        region+=1
    coefficient=initial if counter==0 else coefficients[region]
    numerator=(input-25600)*coefficient
    delta=(1 if numerator>=0 else -1)*(abs(numerator)//256)
    minimum=stft!=25600 and delta==0
    if minimum:delta+=1 if input>=25600 else -1
    output=max(256*lower,min(256*upper,previous+delta))
    memory=bytearray(before);grid=0x4B10 if bank else 0x4B90
    put_word(memory,grid+index*2,output)
    aux=auxiliary(bytes(memory),bank,index,decay,aux_lower,aux_upper)
    return dict(memory=aux['memory'],bank=bank,index=index,enabled=True,input=input,stft=stft,
        previous=previous,region=region,coefficient=coefficient,numerator=numerator,delta=delta,
        minimum=minimum,output=output,grid=grid,auxiliary=aux)


def publication(before,bank,lower,upper):
    """The existing LTFT formula keeps unsigned wrap and one final word store."""
    if (type(before) is not bytes or len(before)!=65536 or type(bank) is not int or bank not in (0,1)
            or any(type(value) is not int or not 0<=value<=255 for value in (lower,upper))):
        raise ValueError('the LTFT equations need complete RAM and explicit bank/byte bounds')
    left=word(before,0x2306+bank*2);right=word(before,0x5648+bank*2)
    u=word(before,0x15FC);raw_v=word(before,0x15FE);v=raw_v-65536 if raw_v&32768 else raw_v
    mask=before[0x230E];raw=(left+right-25600)&0xFFFFFFFF
    active=not mask&(bank+1) and u>v
    limited=min(upper*256,max(lower*256,raw)) if active else raw
    diagnostic=before[0x5A94];f=before[0x41B5];g=before[0x41FA];h=before[0x248B];k=before[0x249C]
    neutral=bool(diagnostic&128 or f&1 or g&1 and h&2 or k&64 and h&1)
    output=25600 if neutral else limited&65535
    memory=bytearray(before);put_word(memory,0x2302+bank*2,output)
    return dict(memory=bytes(memory),bank=bank,left=left,right=right,u=u,v=v,mask=mask,
        raw=raw,active=active,limited=limited,diagnostic=diagnostic,f=f,g=g,h=h,k=k,
        neutral=neutral,output=output)
