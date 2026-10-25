"""Independent scalar transition, curve, split-product, duty and decay equations."""

MASK=0xFFFFFFFF
RAM_BASE=0x01000000


def signed(value):
    return value-(1<<32) if value&(1<<31) else value


def curve_value(curve,axis,coordinate):
    if (type(curve) is not bytes or len(curve)!=9 or type(axis) is not bytes or len(axis)!=8
            or any(left>=right for left,right in zip(axis,axis[1:]))
            or type(coordinate) is not int or not 0<=coordinate<=255):
        raise ValueError('the CVTC curve lacks its exact nine bytes and strictly increasing eight-byte axis')
    visited=[];index=7;fraction=0;division=None
    while index>=0:
        visited.append(index)
        if coordinate==axis[index] or coordinate>axis[index] and index==7:break
        if coordinate>axis[index]:
            dividend=(coordinate-axis[index])*65536;divisor=axis[index+1]-axis[index]
            fraction=dividend//divisor;division=(dividend,divisor)
            break
        index-=1
    index=max(0,index);left,right=curve[index:index+2]
    value=(left+((right-left)*fraction)//65536 if right>=left
        else left-((left-right)*fraction)//65536)
    return dict(value=value,index=index,fraction=fraction,left=left,right=right,
        coordinate=coordinate,visited=tuple(visited),division=division)


def evaluate(entry,before,calibration,context):
    if (entry not in (0xC1DEC,0xC2040) or type(before) is not bytes or len(before)!=65536
            or type(context) is not tuple or len(context)!=20 or context[4]&255!=1
            or before[0x1108]==0):
        raise ValueError('the CVTC equations require complete RAM and the exact bank2/nonzero-input premises')
    memory=bytearray(before);events=[];mode_writes=[];quotients=[]
    def ram(site,at,width=1):
        value=int.from_bytes(memory[at:at+width],'big')
        events.append((site,'read',RAM_BASE+at,width,value));return value
    def rom(site,at,width=1):
        owners=[first for first,data in calibration.items() if first<=at and at+width<=first+len(data)]
        if len(owners)!=1:raise ValueError('the CVTC scalar operand lacks one exact calibration span')
        first=owners[0];value=int.from_bytes(calibration[first][at-first:at-first+width],'big')
        events.append((site,'read',at,width,value));return value
    def store(site,at,width,value):
        value&=(1<<(8*width))-1;memory[at:at+width]=value.to_bytes(width,'big')
        events.append((site,'write',RAM_BASE+at,width,value))
    def mode_store(site,value):
        store(site,0x1B1D,1,value);mode_writes.append((site,value))
    value=dict(entry=entry,bank=1,curve=None,quotients=quotients,mode_writes=mode_writes)
    if entry==0xC1DEC:
        mode=ram(0xC1E06,0x1B1D)
        if mode==0:
            flags=ram(0xC1E12,0x248B)
            if flags&5==5 and ram(0xC1E1E,0x1246)&2:
                mode=1;mode_store(0xC1E32,mode)
        if mode==1:
            flags=ram(0xC1E40,0x248B)
            if not flags&1:
                mode=0;mode_store(0xC1E66,mode)
            elif not ram(0xC1E52,0x1246)&2:
                mode=2;mode_store(0xC1E66,mode)
        if mode==2:
            current=ram(0xC1E78,0x1AAE,2);flags=ram(0xC1E82,0x248B)
            if current==0 or not flags&1:mode_store(0xC1E92,0)
            if flags&5==5 and ram(0xC1EA0,0x1246)&2:mode_store(0xC1EB4,1)
        mode=ram(0xC1EBC,0x1B1D);payload=0
        if mode:
            coordinate=ram(0xC1ECE,0x2772)
            curve=curve_value(calibration[0x1205A],calibration[0x12850],coordinate);value['curve']=curve
            for index in curve['visited']:rom(0x26946,0x12850+index)
            if curve['division'] is not None:
                rom(0x2695C,0x12850+curve['index']);rom(0x2695E,0x12850+curve['index']+1)
            rom(0x26486,0x1205A+curve['index']+1);rom(0x2648C,0x1205A+curve['index'])
            gain=curve['value'];store(0xC1EE2,0x143A,1,gain)
            configuration=rom(0xC1EE6,0x8615);value.update(gain=gain,configuration=configuration)
            if configuration&8:
                coefficient=rom(0xC1EFE,0x9214,2);error=ram(0xC1F0C,0x1B1A,2)
                product=(coefficient*error)&MASK
                high=2*(product>>16)*gain
                first=high//625;remainder=high%625
                ram(0xC1F32,0x143A)
                low=(2*(product&65535)*gain+(remainder<<16))&MASK
                second=low//625
                quotients.extend(((0xC1F24,high,625,first),(0xC1F56,low,625,second)))
                payload=min(0x04000000,((first<<16)+second)&MASK)
                value.update(product=product,high=high,remainder=remainder,low=low,
                    raw_payload=payload,remainder_call=(0xC1F46,high,625,remainder))
            else:
                term_a=ram(0xC1F78,0x1A88,2);term_b=ram(0xC1F7E,0x1A9A,2)
                accumulator=ram(0xC1F92,0x1A94,4)
                raw=(((term_a+term_b-65536)<<16)+accumulator-0x08000000)&MASK
                payload=raw
                if signed(raw)>0:
                    high=(signed((raw>>16)<<16)>>16)*gain
                    payload=(((high>>7)<<16)+(((raw&65535)*gain+((high&127)<<16))>>7))&MASK
                    payload=min(0x04000000,payload)
                value.update(raw_payload=raw,scaled_payload=payload)
        payload=max(0,min(0x04000000,signed(payload)))
        store(0xC1FF4,0x1AA8,4,payload)
        value.update(mode=mode,output=payload,output_address=0x1AA8,output_width=4)
    else:
        payload=ram(0xC205E,0x1AA8,4);battery=ram(0xC2074,0x1108)
        first_dividend=(payload>>16)*150;second_dividend=((payload>>8)&255)*150
        first=first_dividend//battery;second=second_dividend//battery
        quotients.extend(((0xC2078,first_dividend,battery,first),(0xC208A,second_dividend,battery,second)))
        preliminary=min(1024,first+((second+128)>>8))&65535
        store(0xC20AE,0x1C72,2,preliminary)
        current_mask=ram(0xC20B2,0x1284);copied=False
        if current_mask&2 and not ram(0xC20C2,0x1246)&2:
            current=ram(0xC20D2,0x1AAE,2);store(0xC20DA,0x1AB6,2,current);copied=True
        mode=ram(0xC20E4,0x1B1D);output=preliminary
        if mode==0:output=0
        elif mode!=1 and not ram(0xC20F8,0x1246)&2:
            current=ram(0xC2108,0x1AAE,2);lag=ram(0xC2114,0x1AB6,2);decay=rom(0xC2118,0x8DE1)
            output=max(0,current-((lag*decay)>>8));value.update(current=current,lag=lag,decay=decay)
        value['precap_output']=output;output=min(1024,output)
        store(0xC213E,0x1AAE,2,output)
        value.update(mode=mode,preliminary=preliminary,copied=copied,battery=battery,payload=payload,
            output=output,output_address=0x1AAE,output_width=2)
    return dict(value,memory=bytes(memory),physical=tuple(events))
