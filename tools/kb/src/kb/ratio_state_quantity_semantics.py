"""Independent primary ratio, signed scaling and complete state-filter equations."""

MASK = 0xFFFFFFFF


def word(memory, at):
    return int.from_bytes(memory[at:at + 2], 'big')


def long(memory, at):
    return int.from_bytes(memory[at:at + 4], 'big')


def signed(value, bits=32):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def signed_word(value):
    return signed(value, 16)


def truncate(dividend, divisor):
    if not divisor:
        raise ValueError('the ratio-state equation requires its actual nonzero signed divisor')
    magnitude = abs(dividend) // abs(divisor)
    return -magnitude if (dividend < 0) != (divisor < 0) else magnitude


def bounded_signed_word(value):
    return max(-32768, min(32767, value))


def words(raw, count):
    if type(raw) is not bytes or len(raw) != 2 * count:
        raise ValueError('the ratio-state equation truncates a complete physical word array')
    return tuple(word(raw, 2 * index) for index in range(count))


def linear(first, second, fraction):
    if second >= first:
        return first + (second - first) * fraction // 65536
    return first - (first - second) * fraction // 65536


def ratio_curve(raw, coordinate):
    table = words(raw, 16)
    if coordinate >= 0xF000:
        return dict(index=15, fraction=0, value=table[15], returned=signed_word(table[15]) & MASK,
            physical_cells=(15,), endpoint=True)
    index, remainder = divmod(coordinate, 4096)
    fraction = remainder * 16
    value = linear(table[index], table[index + 1], fraction)
    return dict(index=index, fraction=fraction, value=value, returned=value,
        physical_cells=(index, index + 1), endpoint=False)


def centered_curve(raw, coordinate):
    values = words(raw, 16)
    curve, axis = values[:8], values[8:]
    index, fraction = 0, 0
    for knot in range(7, -1, -1):
        if coordinate == axis[knot] or coordinate > axis[knot] and knot == 7:
            index = knot
            break
        if coordinate > axis[knot]:
            if not axis[knot] < coordinate < axis[knot + 1]:
                raise ValueError('the centered curve loses its actual positive neighboring divisor')
            index = knot
            fraction = (coordinate - axis[knot]) * 65536 // (axis[knot + 1] - axis[knot])
            break
    # The ninth physical curve word is exactly the first axis word.
    physical_curve = (*curve, axis[0])
    value = linear(physical_curve[index], physical_curve[index + 1], fraction)
    return dict(index=index, fraction=fraction, value=value, first=physical_curve[index],
        second=physical_curve[index + 1], centered=value - 32768,
        initial_live_signed_offset=(signed_word(value) - 32768) & MASK,
        physical_cells=(index, index + 1))


def accumulator(previous, target, gain):
    updated = (previous - (previous // 65536) * gain + target * gain) & MASK
    incremented = previous < target * 65536 and updated == previous
    if incremented:
        updated = (updated + 1) & MASK
    return dict(previous=previous, target=target, gain=gain, updated=updated,
        incremented=incremented, raw_delta=(updated - previous) & MASK)


def caller(phase, memory, calibration):
    if type(phase) is not int or phase not in (0, 1) or type(memory) is not bytes or len(memory) != 65536:
        raise ValueError('the ratio-state equations require one exact phase and complete actual incoming RAM')
    out = bytearray(memory)
    def store(at, width, value):
        out[at:at + width] = (value & ((1 << (8 * width)) - 1)).to_bytes(width, 'big')
    def control(at):
        return word(calibration[at], 0)
    if phase == 0:
        coordinate_source = word(memory, 0x1702)
        minimum = min(word(memory, 0x10D6), word(memory, 0x1582)) if coordinate_source else None
        divisor = (25 * coordinate_source) // 8 if coordinate_source else None
        dividend = minimum * 61440 if minimum is not None else None
        quotient = dividend // divisor if divisor is not None else None
        primary = 65535 if quotient is None else min(65535, quotient)
        store(0x17E2, 2, primary)
        product = primary * control(0x920E)
        coordinate = min(65535, product // 32768)
        store(0x16B2, 2, coordinate)
        curve = ratio_curve(calibration[0x15770], coordinate)
        store(0x19A2, 2, curve['value'])
        return dict(phase=phase, coordinate_source=coordinate_source, minimum=minimum, divisor=divisor,
            dividend=dividend, quotient=quotient, primary=primary, product=product, coordinate=coordinate,
            curve=curve, quantity=curve['value'], memory=bytes(out))
    quantity, other = word(memory, 0x19A2), word(memory, 0x1770)
    product = quantity * other
    shifted_return = signed(product) // 64
    scaled_product = min(65535, product // 64)
    first_divisor = control(0x944E)
    first_dividend = signed_word(word(memory, 0x18D2)) * scaled_product
    if first_divisor:
        first_quotient = truncate(first_dividend, first_divisor)
    else:
        first_quotient = 0
        store(0x9818, 4, 0x44E)
    first = bounded_signed_word(first_quotient)
    store(0x145A, 2, first)
    coordinate = word(memory, 0x1152)
    curve = centered_curve(calibration[0x15276], coordinate)
    store(0x1792, 2, curve['centered'])
    one = accumulator(long(memory, 0x1540), coordinate, control(0x95A0))
    delta = signed(one['raw_delta']) // 256
    delta_bounded = bounded_signed_word(delta)
    delta_product = delta_bounded * 283
    delta_scaled = truncate(delta_product, 256)
    delta_final = bounded_signed_word(delta_scaled)
    offset_target = (delta_final - 32768) & 65535
    store(0x14F4, 2, offset_target)
    store(0x1540, 4, one['updated'])
    two = accumulator(long(memory, 0x14F8), offset_target, control(0x918E))
    store(0x14F8, 4, two['updated'])
    centered_state = two['updated'] // 65536 - 32768
    store(0x14F6, 2, centered_state)
    feedback_dividend = centered_state * control(0x928E)
    feedback_quotient = truncate(feedback_dividend, 1000)
    feedback = bounded_signed_word(feedback_quotient)
    store(0x1508, 2, feedback)
    error = first - curve['centered'] - feedback
    target = bounded_signed_word(error)
    store(0x177E, 2, target - 32768)
    previous = word(memory, 0x177C)
    lag_gain = control(0x928C)
    lag_product = (target * lag_gain + previous * (65536 - lag_gain)) & MASK
    lag_initial = signed_word(lag_product // 65536)
    lag = lag_initial
    stuck = lag != target and lag == previous
    if stuck:
        lag += 1 if target > previous else -1
    result = max(0, lag)
    store(0x177C, 2, result)
    return dict(phase=phase, quantity=quantity, other=other, product=product,
        shifted_return=shifted_return & MASK, scaled_product=scaled_product,
        first_divisor=first_divisor, first_dividend=first_dividend, first_quotient=first_quotient, first=first,
        coordinate=coordinate, curve=curve, accumulator_one=one, delta=delta, delta_bounded=delta_bounded,
        delta_product=delta_product, delta_scaled=delta_scaled, delta_final=delta_final, offset_target=offset_target,
        accumulator_two=two, centered_state=centered_state, feedback_dividend=feedback_dividend,
        feedback_quotient=feedback_quotient, feedback=feedback, error=error, target=target,
        previous=previous, lag_gain=lag_gain, lag_product=lag_product, lag_initial=lag_initial,
        lag=lag, stuck=stuck, result=result, memory=bytes(out))
