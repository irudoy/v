"""Independent wrapped accumulator, counter and byte-curve equations for native index1."""


def integer(memory, address, size):
    return int.from_bytes(memory[address:address + size], 'big')


def byte_curve(values, axis, coordinate):
    """Descending search and Q16 interpolation, including the physical ninth byte."""
    if type(values) is not bytes or len(values) != 9 or type(axis) is not bytes or len(axis) != 8:
        raise ValueError('the accumulator curve needs all eight axis bytes and nine physical values')
    index = 7
    while True:
        knot = axis[index]
        if coordinate == knot:
            fraction = 0
            break
        if coordinate > knot:
            fraction = 0 if index == 7 else ((coordinate - knot) << 16) // (axis[index + 1] - knot)
            break
        index -= 1
        if index < 0:
            index, fraction = 0, 0
            break
    first, last = values[index], values[index + 1]
    step = (abs(last - first) * fraction) >> 16
    result = first + step if last >= first else first - step
    return dict(index=index, fraction=fraction, first=first, last=last, value=result & 255)


def caller(memory, calibration, context):
    if type(memory) is not bytes or len(memory) != 65536:
        raise ValueError('the accumulator equations require complete raw RAM')
    if (type(context) not in (list, tuple) or len(context) != 20
            or any(type(v) is not int or not 0 <= v <= 0xFFFFFFFF for v in context)
            or context[4] & 255 != 1 or context[18] & ~0x3F1):
        raise ValueError('the accumulator equations require complete native index1 CPU and SR inputs')
    for address, size in ((0x829E, 1), (0x829F, 1), (0x82A0, 1), (0x82A1, 1),
                          (0x8A4C, 1), (0x8A4E, 1), (0x8D75, 1), (0x8F8A, 2),
                          (0x8F8C, 2), (0x9410, 2), (0x95B6, 2),
                          (0x11BC3, 8), (0x12D82, 9), (0x11BBB, 8), (0x12C4A, 9)):
        if type(calibration.get(address)) is not bytes or len(calibration[address]) != size:
            raise ValueError('the accumulator equations lose complete physical ROM controls or curve bytes')
    after = bytearray(memory)
    publications = []
    local_writes = []

    def get(address, size=1):
        return integer(after, address, size)

    def put(site, address, value, size=1):
        value &= (1 << (8 * size)) - 1
        after[address:address + size] = value.to_bytes(size, 'big')
        publications.append(dict(site=site, address=address, size=size, value=value))

    def rom(address):
        return int.from_bytes(calibration[address], 'big')

    threshold = rom(0x829E)
    first_condition = (get(0x3A1F) < rom(0x829F) and get(0x1075) < rom(0x82A0)
                       and get(0x101E, 2) >= rom(0x8F8A))
    if first_condition:
        put(0x3AA6C, 0x421A, get(0x421A) | 128)
        count = get(0x3969)
        if count >= threshold:
            local_writes.append(dict(offset=8, value=get(0x3977)))
            put(0x3AA86, 0x3977, get(0x3977) | 2)
        put(0x3AA9C, 0x3969, min(255, count + 1))
    else:
        put(0x3AAA6, 0x421A, get(0x421A) & 127)
        put(0x3AAAA, 0x3969, 0)
    second_condition = bool(get(0x3977) & 2) and get(0x101E, 2) < rom(0x8F8C) and get(0x1188) >= rom(0x82A1)
    if second_condition:
        put(0x3AAE0, 0x421A, get(0x421A) | 64)
        count = get(0x396B)
        if count >= threshold:
            local_writes.append(dict(offset=12, value=get(0x3978)))
            put(0x3AAFA, 0x3978, get(0x3978) | 2)
        put(0x3AB1E, 0x396B, min(255, count + 1))
    else:
        put(0x3AB16, 0x421A, get(0x421A) & 191)
        put(0x3AB1E, 0x396B, 0)
    if get(0x3978) & 2:
        if not get(0x398C) & 2:
            difference = (get(0x398B) - threshold) & 65535
            put(0x3AB54, 0x3989, difference)
            put(0x3AB5A, 0x398C, get(0x398C) | 2)
    else:
        put(0x3ABBA, 0x398B, min(255, get(0x398B) + 1))
    seed_product = None
    addition = None
    if not get(0x3997) & 2:
        difference = (rom(0x8A4E) - rom(0x8D75)) & 65535
        square_low_word = difference * difference & 65535
        seed_product = (5 * rom(0x8A4C) * square_low_word) & 0xFFFFFFFF
        put(0x3ABEE, 0x3980, seed_product, 4)
        put(0x3ABFA, 0x3997, get(0x3997) | 2)
    elif ((get(0x421A) & 128 or get(0x3977) & 2)
          and not get(0x421A) & 64 and not get(0x3978) & 2):
        difference = get(0x1188) - rom(0x8D75)
        addition = 5 * difference * difference
        put(0x3AC58, 0x3980, min(0xFFFFFFFF, get(0x3980, 4) + addition), 4)
    divisor = get(0x3989) + rom(0x8A4C)
    first_quotient = None if divisor == 0 else get(0x3980, 4) // divisor
    second_quotient = None if divisor == 0 else first_quotient // 1000
    mean = 255 if divisor == 0 else min(255, second_quotient)
    put(0x3ACB0, 0x397A, mean)
    mean_curve = byte_curve(calibration[0x12D82], calibration[0x11BC3], get(0x397A))
    put(0x3ACD0, 0x3996, mean_curve['value'])
    if not get(0x3992) & 2:
        if get(0x3978) & 2:
            latched = min(65535, get(0x3996) * (get(0x3989) + rom(0x8A4C)))
            put(0x3AD0E, 0x3990, latched, 2)
            put(0x3AD42, 0x3992, get(0x3992) | 2)
        elif get(0x398B) == 125 and get(0x3977) & 2:
            put(0x3AD38, 0x3990, 25600, 2)
            local_writes.append(dict(offset=16, value=get(0x3992)))
            put(0x3AD42, 0x3992, get(0x3992) | 2)
    factor_curve = None
    if get(0x3977) & 2:
        factor_curve = byte_curve(calibration[0x12C4A], calibration[0x11BBB], get(0x3990, 2) >> 8)
        put(0x3AD6E, 0x3994, factor_curve['value'])
    old = get(0x399C, 4)
    coefficient = rom(0x9410)
    decayed = None
    if not get(0x39A0) & 2:
        value = rom(0x95B6) << 16
        put(0x3AD8A, 0x399C, value, 4)
        put(0x3AD90, 0x39A0, get(0x39A0) | 2)
        branch = 'initialize'
    elif (not get(0x3977) & 2 and get(0x3A1F) >= rom(0x829F)) or get(0x439B) == 0:
        value = 0
        put(0x3AE74, 0x399C, value, 4)
        branch = 'zero'
    else:
        high_product = ((old >> 16) * coefficient) & 0xFFFFFFFF
        low_product = ((old & 65535) * coefficient) & 0xFFFFFFFF
        decayed = (high_product + (low_product >> 16)) & 0xFFFFFFFF
        if get(0x3992) & 2 and not get(0x39A1) & 2:
            factor = get(0x3994)
            high_product = ((decayed >> 8) * factor) & 0xFFFFFFFF
            low_product = ((decayed & 255) * factor) & 0xFFFFFFFF
            value = (high_product + (low_product >> 8)) & 0xFFFFFFFF
            put(0x3AE1A, 0x399C, value, 4)
            local_writes.append(dict(offset=20, value=get(0x39A1)))
            put(0x3AE24, 0x39A1, get(0x39A1) | 2)
            branch = 'decay-and-scale-once'
        else:
            value = decayed
            put(0x3AE74, 0x399C, value, 4)
            branch = 'decay'
    return dict(memory=bytes(after), publications=publications, local_writes=local_writes,
                first_condition=first_condition, second_condition=second_condition,
                seed_product=seed_product, addition=addition, divisor=divisor,
                first_quotient=first_quotient, second_quotient=second_quotient,
                mean=mean, mean_curve=mean_curve, factor_curve=factor_curve,
                old=old, coefficient=coefficient, decayed=decayed, value=value, branch=branch)
