"""Independent conditional word-curve and diagnostic-chain integer equations.

These equations do not grant execution, native geometry, relation, physical
scale or hardware admission. Actual complete observations remain mandatory.
"""


def signed_byte(value):
    if type(value) is not int or not 0<=value<=255:
        raise ValueError('an ignition diagnostic byte input has another width')
    return value-256 if value&128 else value


def words(raw,size):
    if type(raw) is not bytes or len(raw)!=size or size%2:
        raise ValueError('the ignition word curve lacks exact original big-endian operands')
    return tuple(int.from_bytes(raw[index:index+2],'big') for index in range(0,size,2))


def word_curve(table_with_neighbor,axis,coordinate):
    """The final neighbor is read by264CC but has zero weight at the endpoint."""
    table=words(table_with_neighbor,18)
    knots=words(axis,16)
    if (type(coordinate) is not int or not 0<=coordinate<=65535
            or any(first>=second for first,second in zip(knots,knots[1:]))):
        raise ValueError('the ignition curve changes its bounded word coordinate or strict stock axis')
    if coordinate<=knots[0]:index,fraction=0,0
    elif coordinate>=knots[-1]:index,fraction=7,0
    else:
        index=max(index for index in range(7) if knots[index]<=coordinate)
        fraction=((coordinate-knots[index])*65536)//(knots[index+1]-knots[index])
    first,second=table[index:index+2]
    delta=(abs(second-first)*fraction)//65536
    value=first+delta if second>=first else first-delta
    return dict(index=index,byte_offset=index*2,fraction=fraction,value=value,
                operand_offsets=(index*2,index*2+2),semantic_table_bytes=16,
                physical_read_extent_bytes=18,neighbor_contribution=fraction!=0)


def event_correction(amplitude,coefficient,base=0):
    if (type(amplitude) is not int or not 0<=amplitude<=65535
            or type(coefficient) is not int or not 0<=coefficient<=255
            or type(base) is not int or not -128<=base<=127):
        raise ValueError('the conditional ignition event path changes an operand width')
    scaled=min(amplitude*coefficient//100,65535)
    output=max(-128,min(127,base-scaled))
    return dict(amplitude=amplitude,scaled=scaled,correction=output)


def normal_coordinate(correction,lower,upper,command_base):
    """Only the explicit direct-limit mode; no timer, rate-hold or auxiliary mode."""
    if (any(type(value) is not int for value in (correction,lower,upper,command_base))
            or not -128<=correction<=127 or not -128<=lower<=upper<=127
            or not 0<=command_base<=255):
        raise ValueError('the conditional final-coordinate path changes a signed byte or stock limit')
    limited=max(lower,min(upper,correction))
    lower_floor=-max(129-command_base,0)
    return max(lower_floor,min(command_base-40,limited))


def command(coordinate,command_base,override=False):
    if (type(coordinate) is not int or not -128<=coordinate<=127
            or type(command_base) is not int or not 0<=command_base<=255
            or type(override) is not bool):
        raise ValueError('the conditional command path changes its signed input, base or explicit override')
    return (command_base-(20 if override else coordinate))&255
