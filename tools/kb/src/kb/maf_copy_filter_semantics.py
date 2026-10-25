"""Unsigned copy and first-order filtering with an independent anti-stall step."""


def output(kind, argument, before, coefficient):
    if (kind not in ('copy', 'filter') or type(argument) is not int or not 0 <= argument <= 0xFFFFFFFF
            or argument & 255 not in (0, 1) or type(before) is not bytes or len(before) != 65536
            or type(coefficient) is not int or not 0 <= coefficient <= 255):
        raise ValueError('the MAF equation changes its exact kind, bank, memory or coefficient domain')
    offset = (argument & 255) * 2
    source = (0x1054 if kind == 'copy' else 0x1058) + offset
    destination = (0x1058 if kind == 'copy' else 0x1DF0) + offset
    value = int.from_bytes(before[source:source + 2], 'big')
    previous = int.from_bytes(before[destination:destination + 2], 'big')
    weighted = kind == 'filter' and bool(before[0x2461] & 0x20)
    result, step = value, 0
    if weighted:
        result = ((coefficient * value + (256 - coefficient) * previous) >> 8) & 65535
        if result != value and result == previous:
            step = 1 if previous < value else -1
            result = (result + step) & 65535
    memory = bytearray(before)
    memory[destination:destination + 2] = result.to_bytes(2, 'big')
    return dict(source=source, destination=destination, input=value, previous=previous, weighted=weighted,
                output=result, step=step, memory=bytes(memory), bank_offset=offset)
