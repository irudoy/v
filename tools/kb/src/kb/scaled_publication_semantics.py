"""Independent bounded scaled quotient and exact publication footprint."""


def caller(before, kind, value):
    if (type(before) is not bytes or len(before) != 65536 or kind not in ('signed', 'unsigned')
            or type(value) is not int or not 0 <= value <= 65535):
        raise ValueError('the scaled-publication equation needs an explicit word input and complete RAM')
    dividend = value * 727
    output = dividend // 800
    after = bytearray(before)
    address = 0x1210 if kind == 'signed' else 0x1248
    after[address:address + 2] = output.to_bytes(2, 'big')
    if kind == 'unsigned':
        after[0x35CC:0x35CE] = value.to_bytes(2, 'big')
    return dict(memory=bytes(after), dividend=dividend, divisor=800, output=output, address=address,
                site=0x7A784 if kind == 'signed' else 0x7A976,
                target=0x21BBC if kind == 'signed' else 0x21CE0,
                fault=bytes(after[0x9818:0x981C]))
