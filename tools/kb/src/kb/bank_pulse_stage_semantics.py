"""Existing precursor and channel equations over full explicit observed inputs."""

from kb import bank_pulse_stage_matrix as matrix

PRECURSOR_NUMERIC='tools/sh-elf-run/stock_precursor_model.py'
CHANNEL_ARITHMETIC_SOURCE='tools/kb/tests/test_channel_pulse_chain.py'


def data(calibrations,address,width):
    for start,raw in calibrations.items():
        if start<=address and address+width<=start+len(raw):
            return raw[address-start:address-start+width]
    raise ValueError('a bank-pulse stage lacks an exact observed calibration input')


def word(memory,address):return int.from_bytes(memory[address:address+2],'big')


def put_word(memory,address,value):memory[address:address+2]=(value&65535).to_bytes(2,'big')


def precursor(before,calibrations,numeric):
    values={key:before[at] for key,at in matrix.BYTE_INPUTS}
    values.update({key:word(before,at) for key,at in matrix.WORD_INPUTS})
    values['cap_numerator']=int.from_bytes(data(calibrations,0x96E0,4),'big')
    values['pulse_floor']=int.from_bytes(data(calibrations,0x94E8,2),'big')
    expected=numeric.arithmetic(values)
    memory=bytearray(before)
    if values['cap_flags']&1:put_word(memory,0x196A,expected['selected_bfs'])
    put_word(memory,0x18C0,expected['bank0_output']);put_word(memory,0x18C2,expected['bank1_output'])
    put_word(memory,0x1876,expected['common_output']);memory[0x24A1]=expected['updated_flags']
    return dict(expected,inputs=values,memory=bytes(memory),output=expected['bank1_output'])


def signed_word(value):return value-65536 if value&32768 else value


def channel(before,calibrations,index):
    if type(index) is not int or index not in range(6):
        raise ValueError('a channel scalar input leaves its declared natural domain')
    inhibited=bool(before[0x22E0]&(1<<index));opening=word(before,0x2436)
    selected=word(before,0x191C+(index&1)*2)
    additive=signed_word(word(before,0x1396+index*2));subtractive=signed_word(word(before,0x1466+index*2))
    flag=data(calibrations,0x8D92,1)[0]
    value=selected+additive-(subtractive if flag&8 else 0)
    positive=value>0
    multiplier=data(calibrations,0x129C0+index,1)[0]
    product=(max(0,value)*multiplier)&0xFFFFFFFF
    compensated=opening if inhibited else min(65535,product//128)
    a,c,b,d=(int.from_bytes(data(calibrations,at,2),'big') for at in (0x91DA,0x91DC,0x91DE,0x91E0))
    lower=min(65535,((a*compensated+100*b)&0xFFFFFFFF)//16384)
    upper=min(65535,((c*compensated+100*d)&0xFFFFFFFF)//16384)
    transformed=compensated if inhibited else max(compensated,lower,upper)
    memory=bytearray(before);put_word(memory,0x23C8+index*2,compensated);put_word(memory,0x23D4+index*2,transformed)
    return dict(memory=bytes(memory),index=index,inhibited=inhibited,opening=opening,selected=selected,
        additive=additive,subtractive=subtractive,flag=flag,value=value,positive=positive,multiplier=multiplier,
        product=product,compensated=compensated,lower=lower,upper=upper,transformed=transformed,output=compensated)
