"""Integer quotient and fault-store equations independent of DIV1 state steps."""

MASK=0xFFFFFFFF


def quotient(kind,divisor,dividend):
    if (kind not in ('signed','unsigned') or any(type(value) is not int or not 0<=value<=MASK
            for value in (divisor,dividend))):
        raise ValueError('the division equation needs an explicit signedness and two32-bit operand words')
    if divisor==0:return 0
    if kind=='unsigned':return dividend//divisor
    signed=lambda value:value if value<0x80000000 else value-(1 << 32)
    denominator,numerator=signed(divisor),signed(dividend)
    magnitude=abs(numerator)//abs(denominator)
    return (-magnitude if (numerator<0)!=(denominator<0) else magnitude)&MASK


def memory_after(before,divisor):
    if (type(before) is not bytes or len(before)!=65536
            or type(divisor) is not int or not 0<=divisor<=MASK):
        raise ValueError('the division fault equation requires the complete actual RAM input')
    result=bytearray(before)
    if divisor==0:result[0x9818:0x981C]=(0x044E).to_bytes(4,'big')
    return bytes(result)
