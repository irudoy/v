"""Independent coefficient, signed lag/history and ratio-byte equations."""


def word(memory, at):
    return int.from_bytes(memory[at:at + 2], 'big')


def signed_word(value):
    return value if value < 32768 else value - 65536


def truncate(dividend, divisor):
    if type(dividend) is not int or type(divisor) is not int or not divisor:
        raise ValueError('the torque ratio equation requires a nonzero exact signed divisor')
    magnitude = abs(dividend) // abs(divisor)
    return -magnitude if (dividend < 0) != (divisor < 0) else magnitude


def words(raw, count):
    if type(raw) is not bytes or len(raw) != 2 * count:
        raise ValueError('the torque ratio equation truncates a complete raw word array')
    return tuple(word(raw, 2 * index) for index in range(count))


def directed(first, second, fraction):
    if not all(type(value) is int and 0 <= value <= 65535 for value in (first, second, fraction)):
        raise ValueError('the torque ratio interpolation loses an unsigned word or fraction')
    if second >= first:
        return first + (second - first) * fraction // 65536
    return first - (first - second) * fraction // 65536


def position(axis, coordinate):
    if len(axis) != 8 or type(coordinate) is not int or not 0 <= coordinate <= 65535:
        raise ValueError('the correction axis requires its complete eight-word coordinate domain')
    for index in range(7, -1, -1):
        if coordinate == axis[index]:
            return index, 0
        if coordinate > axis[index]:
            if index == 7:
                return index, 0
            if not axis[index] < coordinate < axis[index + 1]:
                raise ValueError('the correction axis loses its actual positive neighboring divisor')
            return index, (coordinate - axis[index]) * 65536 // (axis[index + 1] - axis[index])
    return 0, 0


def coefficient(curve, axis, coordinate):
    values = words(curve, 9)
    index, fraction = position(words(axis, 8), coordinate)
    return dict(index=index, fraction=fraction, first=values[index], second=values[index + 1],
        value=directed(values[index], values[index + 1], fraction), physical_cells=(index, index + 1))


def lag_weight(curve, coordinate):
    values = words(curve, 16)
    if type(coordinate) is not int or not 0 <= coordinate <= 65535:
        raise ValueError('the lag-weight equation changes its complete raw coordinate')
    if coordinate >= 0xF000:
        return dict(value=values[15], index=15, fraction=0, endpoint=True, physical_cells=(15,))
    index, remainder = divmod(coordinate, 4096)
    fraction = remainder * 16
    return dict(value=directed(values[index], values[index + 1], fraction), index=index,
        fraction=fraction, endpoint=False, physical_cells=(index, index + 1))


def ratio(source, correction, offset_a, offset_b, divisor):
    if source == 0x7FFF:
        return dict(sentinel=True, sum=None, quotient=None, value=255, divisor=divisor)
    total = signed_word(source) + correction + offset_a + offset_b
    quotient = truncate(total * 256, divisor) if divisor else None
    value = max(0, min(255, quotient)) if divisor else (255 if total > 0 else 0)
    return dict(sentinel=False, sum=total, quotient=quotient, value=value, divisor=divisor)


def caller(phase, memory, calibration):
    if type(phase) is not int or phase not in (0, 1) or type(memory) is not bytes or len(memory) != 65536:
        raise ValueError('the torque ratio equations require one exact phase and complete incoming RAM')
    out = bytearray(memory)
    def store(at, value):
        out[at:at + 2] = (value & 65535).to_bytes(2, 'big')
    if phase == 0:
        coordinate = word(memory, 0x11BC)
        lookup = coefficient(calibration[0x14C1A], calibration[0x14ABA], coordinate)
        store(0x14E4, lookup['value'])
        selector = memory[0x4181]
        first = memory[0x1071]
        weight = None
        second = None
        if selector & 128:
            selected = first
        else:
            second, weight = memory[0x2772], calibration[0x8639][0]
            selected = (first * (256 - weight) + second * weight) // 256
        limit = calibration[0x8E51][0]
        product = lookup['value'] * (limit - selected)
        correction = max(0, product) // 256
        store(0x14E2, correction)
        return dict(phase=phase, coordinate=coordinate, lookup=lookup, selector=selector, first=first,
            second=second, weight=weight, selected=selected, limit=limit, product=product,
            correction=correction, memory=bytes(out))
    weight = lag_weight(calibration[0x14E52], memory[0x11B3] * 256)
    offset_a, offset_b = word(memory, 0x2408), word(memory, 0x2410)
    target = min(32767, signed_word(word(memory, 0x19C6)) + offset_a + offset_b)
    previous = signed_word(word(memory, 0x199E))
    lag_initial = (target * weight['value'] + previous * (65536 - weight['value'])) // 65536
    lag = lag_initial + int(lag_initial < target and lag_initial == previous)
    store(0x199E, lag)
    initialized = not memory[0x24A3] & 8
    if initialized:
        for index in range(10):
            store(0x19F6 + 2 * index, lag)
        out[0x24A3] |= 8
    history_before_shift = tuple(word(out, 0x19F6 + 2 * index) for index in range(10))
    delay = calibration[0x8C61][0]
    delayed = lag if delay == 0 else signed_word(history_before_shift[min(delay - 1, 9)])
    store(0x19A0, delayed)
    for index in range(9, 0, -1):
        store(0x19F6 + 2 * index, history_before_shift[index - 1])
    store(0x19F6, lag)
    selected_divisor = signed_word(word(memory, 0x18D4)) if calibration[0x83C1][0] & 32 else delayed
    factor_enabled = bool(calibration[0x8B38][0] & 2)
    count = memory[0x16A3] if factor_enabled else None
    factor_quotient = truncate(selected_divisor * (6 - count), 6) if factor_enabled else None
    stored_divisor = (factor_quotient if factor_enabled else selected_divisor) & 65535
    divisor = signed_word(stored_divisor)
    store(0x34D6, stored_divisor)
    correction = word(memory, 0x14E2)
    first_ratio = ratio(word(memory, 0x19CC), correction, offset_a, offset_b, divisor)
    second_ratio = ratio(word(memory, 0x34B8), correction, offset_a, offset_b, delayed)
    out[0x186C], out[0x1864] = first_ratio['value'], second_ratio['value']
    store(0x1608, weight['value'])
    return dict(phase=phase, weight=weight, target=target, previous=previous, lag_initial=lag_initial,
        lag=lag, initialized=initialized, history_before_shift=history_before_shift, delay=delay,
        delayed=delayed, selected_divisor=selected_divisor, factor_enabled=factor_enabled, count=count,
        factor_quotient=factor_quotient, divisor=divisor, stored_divisor=stored_divisor,
        correction=correction, offset_a=offset_a, offset_b=offset_b,
        first_ratio=first_ratio, second_ratio=second_ratio, memory=bytes(out))
