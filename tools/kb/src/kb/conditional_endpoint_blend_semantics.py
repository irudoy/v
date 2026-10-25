"""Independent raw word-axis, directed interpolation, weight and signed blend equations."""

RAM_BASE = 0x01000000


def unsigned_word(memory, at):
    return int.from_bytes(memory[at:at+2], 'big')


def words(raw, count):
    if type(raw) is not bytes or len(raw) != 2 * count:
        raise ValueError('the endpoint equations require a complete raw word array')
    return tuple(unsigned_word(raw, 2 * index) for index in range(count))


def position(axis, coordinate):
    if len(axis) != 16 or type(coordinate) is not int or not 0 <= coordinate <= 65535:
        raise ValueError('the endpoint axis lacks its complete raw word coordinate')
    for index in range(15, -1, -1):
        lower = axis[index]
        if coordinate == lower:
            return index, 0
        if coordinate > lower:
            if index == 15:
                return index, 0
            upper = axis[index+1]
            if not lower < coordinate < upper:
                raise ValueError('the endpoint axis loses its actual positive neighboring divisor')
            return index, ((coordinate - lower) * 65536) // (upper - lower)
    return 0, 0


def directed_word(first, second, fraction):
    if not all(type(value) is int and 0 <= value <= 65535 for value in (first, second, fraction)):
        raise ValueError('the endpoint interpolation loses an actual unsigned word or fraction')
    if second >= first:
        return first + ((second - first) * fraction) // 65536
    return first - ((first - second) * fraction) // 65536


def surface(raw, axis_x, axis_y, x, y):
    table = words(raw, 256)
    row, fraction_x = position(words(axis_x, 16), x)
    column, fraction_y = position(words(axis_y, 16), y)
    selected = row * 16 + column
    cells = [selected]
    first = table[selected]
    if fraction_y:
        cells.append(selected + 1)
        first = directed_word(first, table[selected+1], fraction_y)
    if fraction_x:
        selected_next = selected + 16
        cells.append(selected_next)
        second = table[selected_next]
        if fraction_y:
            cells.append(selected_next + 1)
            second = directed_word(second, table[selected_next+1], fraction_y)
        result = directed_word(first, second, fraction_x)
    else:
        result = first
    returned = result if fraction_x or fraction_y or result < 32768 else result - 65536
    return dict(value=result, returned=returned, row=row, column=column,
                fraction_x=fraction_x, fraction_y=fraction_y, cells=cells)


def caller(memory, calibration):
    if type(memory) is not bytes or len(memory) != 65536:
        raise ValueError('the conditional endpoint blend lacks complete raw RAM')
    first, second = calibration[0x8B3F][0], calibration[0x89FA][0]
    refusal = 'gate-a-refusal' if first & 0x80 else 'gate-b-refusal' if not second & 0x20 else None
    if refusal is not None:
        raw = unsigned_word(memory, 0x18E6)
        return dict(enabled=False, branch=refusal, gate_a=first, gate_b=second,
                    value=raw, output=raw if raw<32768 else raw-65536, memory=memory)
    x = unsigned_word(memory, 0x1210)
    primary_y, alternate_y = (unsigned_word(memory, at) for at in (0x10D2, 0x10E2))
    y = max(primary_y, alternate_y) if memory[0x4255] & 128 else primary_y
    axis_x, axis_y = calibration[0x13D14], calibration[0x13D34]
    endpoint_a = surface(calibration[0xDE8E], axis_x, axis_y, x, y)
    endpoint_b = surface(calibration[0xE08E], axis_x, axis_y, x, y)
    signed_a, signed_b = endpoint_a['value'] - 32768, endpoint_b['value'] - 32768
    register_a = endpoint_a['value'] if endpoint_a['value'] < 32768 else endpoint_a['value'] - 65536
    register_b = endpoint_b['value'] if endpoint_b['value'] < 32768 else endpoint_b['value'] - 65536
    prior, step = unsigned_word(memory, 0x2420), unsigned_word(calibration[0x90A0], 0)
    increasing = bool(memory[0x245C] & 4)
    weight = min(65535, prior + step) if increasing else max(0, prior - step)
    if weight == 0:
        output, branch = signed_a, 'endpoint-a'
    elif weight == 65535:
        output, branch = signed_b, 'endpoint-b'
    else:
        output = ((65536 - weight) * signed_a + weight * signed_b) // 65536
        branch = 'intermediate'
    out = bytearray(memory)
    for at, value in ((0x18EC, signed_a), (0x18EE, signed_b), (0x2420, weight), (0x18E6, output)):
        out[at:at+2] = (value & 65535).to_bytes(2, 'big')
    return dict(enabled=True, gate_a=first, gate_b=second, x=x, y=y, endpoint_a=endpoint_a, endpoint_b=endpoint_b,
                signed_a=signed_a, signed_b=signed_b, publication_register_a=(register_a-32768) & 0xFFFFFFFF,
                publication_register_b=(register_b-32768) & 0xFFFFFFFF, prior_weight=prior, step=step,
                increasing=increasing, weight=weight, output=output, value=output & 65535,
                branch=branch, memory=bytes(out))
