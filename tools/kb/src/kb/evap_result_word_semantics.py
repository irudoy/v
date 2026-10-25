"""Independent EVAP interpolation, wide normalization and result-word equations."""

MASK = 0xFFFFFFFF
POINTER_ALIAS = 0x0100301C


def word(memory, at):
    return int.from_bytes(memory[at:at + 2], 'big')


def words(raw, count):
    if type(raw) is not bytes or len(raw) != 2 * count:
        raise ValueError('the EVAP equation truncates a complete physical word array')
    return tuple(word(raw, 2 * index) for index in range(count))


def position(axis, coordinate):
    if type(coordinate) is not int or not 0 <= coordinate <= 65535 or len(axis) not in (8, 16):
        raise ValueError('the EVAP equation changes an actual axis or raw coordinate domain')
    for index in range(len(axis) - 1, -1, -1):
        if coordinate == axis[index]:
            return index, 0
        if coordinate > axis[index]:
            if index == len(axis) - 1:
                return index, 0
            if not axis[index] < coordinate < axis[index + 1]:
                raise ValueError('the EVAP axis loses its actual positive neighboring divisor')
            return index, (coordinate - axis[index]) * 65536 // (axis[index + 1] - axis[index])
    return 0, 0


def linear(first, second, fraction):
    if second >= first:
        return first + (second - first) * fraction // 65536
    return first - (first - second) * fraction // 65536


def byte_curve(raw, coordinate):
    if type(raw) is not bytes or len(raw) != 16 or not 0 <= coordinate <= 255:
        raise ValueError('the EVAP fixed byte curve loses a physical cell or coordinate')
    if coordinate >= 240:
        returned = raw[15] if raw[15] < 128 else raw[15] | 0xFFFFFF00
        return dict(index=15, fraction=0, value=raw[15], returned=returned,
            physical_cells=(15,), endpoint=True)
    index, remainder = divmod(coordinate, 16)
    fraction = remainder * 4096
    value = linear(raw[index], raw[index + 1], fraction)
    return dict(index=index, fraction=fraction, value=value, returned=value,
        physical_cells=(index, index + 1), endpoint=False)


def indexed_byte_curve(raw, axis, coordinate):
    if type(raw) is not bytes or len(raw) != 9 or type(axis) is not bytes or len(axis) != 8:
        raise ValueError('the EVAP indexed byte curve loses a complete axis or guard cell')
    index, fraction = position(tuple(axis), coordinate)
    value = linear(raw[index], raw[index + 1], fraction)
    return dict(index=index, fraction=fraction, value=value,
        first=raw[index], second=raw[index + 1], physical_cells=(index, index + 1))


def word_curve(raw, axis, coordinate):
    table = words(raw, 17)
    index, fraction = position(words(axis, 16), coordinate)
    return dict(index=index, fraction=fraction, value=linear(table[index], table[index + 1], fraction),
        first=table[index], second=table[index + 1], physical_cells=(index, index + 1))


def caller(memory, calibration, context):
    if (type(memory) is not bytes or len(memory) != 65536 or type(context) is not tuple or len(context) != 20
            or any(type(value) is not int or not 0 <= value <= MASK for value in context)
            or context[6] != POINTER_ALIAS):
        raise ValueError('the EVAP equation requires complete RAM/CPU and its exact native output-pointer alias')
    out = bytearray(memory)
    def store(at, value):
        out[at:at + 2] = (value & 65535).to_bytes(2, 'big')
    parameter, comparison = context[4] & 65535, context[5] & 65535
    baseline_rom = bool(calibration[0x893E][0] & 64)
    baseline = word(calibration[0x94CC], 0) if baseline_rom else word(memory, 0x272A)
    store(0x3062, baseline)
    active = bool(calibration[0x893F][0] & 16 and memory[0x41E5] & 4)
    table_a = 0x122B2 if active else 0x12282
    first = byte_curve(calibration[table_a], memory[0x10FA])
    out[0x2F8D] = first['value']
    threshold = calibration[0x85C1][0] if active else None
    table_b = (0x125A2 if memory[0x10F9] >= threshold else 0x1259A) if active else 0x125AA
    offset = table_b - 0x1259A
    coordinate_b = word(memory, 0x272A) // 256
    second = indexed_byte_curve(calibration[0x1259A][offset:offset + 9], calibration[0x12A5A], coordinate_b)
    out[0x2F94] = second['value']
    transform = word_curve(calibration[0x152D6], calibration[0x13C18], word(memory, 0x2C92))
    store(0x3240, transform['value'])
    difference = transform['value'] - comparison
    gain = product = low_product = scaled = high = quotient_high = remainder_high = low_dividend = quotient_low = None
    product_capped = quotient_capped = False
    if difference <= 0:
        normalized = 0
        branch = 'nonpositive-difference'
    elif parameter == 0:
        normalized = 65535
        branch = 'zero-parameter'
    else:
        gain = calibration[0x8813][0]
        product = baseline * gain * difference
        # The independently defined result uses the full mathematical product.
        # The split values bind the real stock quotient/remainder call operands.
        normalized = min(65535, product // (32 * parameter))
        low_product = baseline * gain * (difference & 255)
        scaled = product // 256
        product_capped = scaled > 0x1FFFC000
        if product_capped:
            branch = 'wide-product-cap'
        else:
            high = product // 65536
            quotient_high = high // parameter
            quotient_capped = quotient_high > 31
            if quotient_capped:
                branch = 'high-quotient-cap'
            else:
                remainder_high = high % parameter
                low_dividend = remainder_high * 65536 + product % 65536
                quotient_low = low_dividend // parameter
                branch = 'normalized-positive'
    store(0x3018, normalized)
    multiplied = normalized * first['value'] * second['value']
    result = min(65535, multiplied // 16384)
    store(0x301C, result)
    return dict(parameter=parameter, comparison=comparison, pointer=context[6], baseline_rom=baseline_rom,
        baseline=baseline, active=active, table_a=table_a, coefficient_a=first, threshold=threshold,
        table_b=table_b, coefficient_b=second, coordinate_b=coordinate_b, transform=transform,
        difference=difference, gain=gain, product=product, low_product=low_product, scaled=scaled,
        high=high, quotient_high=quotient_high, remainder_high=remainder_high, low_dividend=low_dividend,
        quotient_low=quotient_low, product_capped=product_capped, quotient_capped=quotient_capped,
        branch=branch, normalized=normalized, multiplied=multiplied, result=result, memory=bytes(out))
