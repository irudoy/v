"""Independent complete natural endpoint normalization and actual three-word publication."""

def unsigned_word(memory, at):
    return int.from_bytes(memory[at:at+2], 'big')

def words(raw, count):
    if type(raw) is not bytes or len(raw) != 2 * count:
        raise ValueError('the normalization equations require a complete raw word array')
    return tuple(unsigned_word(raw, 2 * index) for index in range(count))

def position(axis, coordinate):
    if len(axis) != 16 or type(coordinate) is not int or not 0 <= coordinate <= 65535:
        raise ValueError('the normalization axis lacks its complete raw word coordinate')
    for index in range(15, -1, -1):
        lower = axis[index]
        if coordinate == lower:
            return index, 0
        if coordinate > lower:
            if index == 15:
                return index, 0
            upper = axis[index+1]
            if not lower < coordinate < upper:
                raise ValueError('the normalization axis loses its actual positive neighboring divisor')
            return index, ((coordinate - lower) * 65536) // (upper - lower)
    return 0, 0

def directed_word(first, second, fraction):
    if not all(type(value) is int and 0 <= value <= 65535 for value in (first, second, fraction)):
        raise ValueError('the normalization interpolation loses an actual unsigned word or fraction')
    if second >= first:
        return first + ((second - first) * fraction) // 65536
    return first - ((first - second) * fraction) // 65536

def curve(raw,axis,coordinate,guard):
    table=words(raw,16);index,fraction=position(words(axis,16),coordinate)
    first=table[index];second=table[index+1] if index<15 else guard
    value=directed_word(first,second,fraction)
    return dict(value=value,index=index,fraction=fraction,first=first,second=second,cells=[index,index+1])

def caller(memory,calibration):
    if type(memory) is not bytes or len(memory)!=65536:raise ValueError('the normalization lacks complete raw RAM')
    coordinate=unsigned_word(memory,0x113C)
    lower=curve(calibration[0x154E0],calibration[0x14BAA],coordinate,unsigned_word(calibration[0x15500],0))
    upper=curve(calibration[0x154C0],calibration[0x14BAA],coordinate,unsigned_word(calibration[0x154E0],0))
    L,U=lower['value'],upper['value'];span=max(0,U-L)
    raw_inputs=[unsigned_word(memory,at) for at in (0x338C,0x338E,0x3396)]
    signed_inputs=[word if word<32768 else word-65536 for word in raw_inputs]
    bases=[max(0,word+32768-L) for word in signed_inputs]
    normalized=[min(800,base*800//span) for base in bases] if span else [800,800,800]
    after=bytearray(memory)
    for at,value in zip((0x3478,0x347A,0x347C),normalized):after[at:at+2]=value.to_bytes(2,'big')
    return dict(coordinate=coordinate,lower=lower,upper=upper,lower_value=L,upper_value=U,span=span,
        raw_inputs=raw_inputs,signed_inputs=signed_inputs,bases=bases,normalized=normalized,
        value=tuple(normalized),memory=bytes(after))
