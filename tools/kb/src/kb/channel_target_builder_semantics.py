"""Independent inverse lookup, ordered channel limits and fixed-record caps."""


def unsigned_word(memory, address):
    return int.from_bytes(memory[address:address + 2], 'big')


def words(raw, count):
    if type(raw) is not bytes or len(raw) != 2 * count:
        raise ValueError('the channel equations require every physical word of the raw array')
    return tuple(unsigned_word(raw, 2 * index) for index in range(count))


def position(axis, coordinate, maximum):
    if (type(coordinate) is not int or not 0 <= coordinate <= maximum
            or not axis or any(type(value) is not int or not 0 <= value <= maximum for value in axis)):
        raise ValueError('the channel axis loses its complete raw coordinate or knot values')
    for index in range(len(axis) - 1, -1, -1):
        lower = axis[index]
        if coordinate == lower:
            return index, 0
        if coordinate > lower:
            if index == len(axis) - 1:
                return index, 0
            upper = axis[index + 1]
            if not lower < coordinate < upper:
                raise ValueError('the channel axis loses its actual positive neighboring divisor')
            return index, ((coordinate - lower) * 65536) // (upper - lower)
    return 0, 0


def directed(first, second, fraction):
    if not all(type(value) is int and 0 <= value <= 65535 for value in (first, second, fraction)):
        raise ValueError('the channel interpolation loses an actual unsigned endpoint or fraction')
    if second >= first:
        return first + ((second - first) * fraction) // 65536
    return first - ((first - second) * fraction) // 65536


def inverse_curve(raw, axis, coordinate):
    table = words(raw, 33)
    index, fraction = position(words(axis, 32), coordinate, 65535)
    first, second = table[index:index + 2]
    return dict(value=directed(first, second, fraction), index=index, fraction=fraction,
                first=first, second=second, cells=[index, index + 1], coordinate=coordinate)


def upper_curve(raw, axis, coordinate):
    if type(raw) is not bytes or len(raw) != 9 or type(axis) is not bytes or len(axis) != 8:
        raise ValueError('the channel upper curve requires all eight knots and the physical ninth byte')
    index, fraction = position(tuple(axis), coordinate, 255)
    first, second = raw[index:index + 2]
    return dict(value=directed(first, second, fraction), index=index, fraction=fraction,
                first=first, second=second, cells=[index, index + 1], coordinate=coordinate)


def caller(memory, calibration, context):
    if type(memory) is not bytes or len(memory) != 65536:
        raise ValueError('the channel equations require complete raw RAM')
    if (type(context) not in (list, tuple) or len(context) != 20
            or any(type(value) is not int or not 0 <= value <= 0xFFFFFFFF for value in context)
            or context[4] & 255 != 1 or context[18] & ~0x3F1):
        raise ValueError('the channel equations require the complete native index1 context')
    for address, size in ((0x9574, 2), (0x9576, 2), (0x9578, 2), (0x8CB6, 1),
                          (0x8CB7, 1), (0x92F2, 2), (0x155A0, 66), (0x13202, 64),
                          (0x12DAA, 9), (0x12D9A, 8)):
        if type(calibration.get(address)) is not bytes or len(calibration[address]) != size:
            raise ValueError('the channel equations lose an exact complete physical calibration input')
    minimum = unsigned_word(calibration[0x9574], 0)
    dynamic_minimum = 4 * unsigned_word(calibration[0x9576], 0)
    raw_maximum = 4 * unsigned_word(calibration[0x9578], 0)
    base, offset = calibration[0x8CB6][0], calibration[0x8CB7][0]
    hard_limit = unsigned_word(calibration[0x92F2], 0)
    first_coordinate = unsigned_word(memory, 0x1340) // 2
    first_inverse = inverse_curve(calibration[0x155A0], calibration[0x13202], first_coordinate)
    scratch = first_inverse['value'] // 4
    mode = bool(memory[0x24CE] & 4 or memory[0x24D2] & 1)
    second_inverse = None
    normal_coordinate = None
    correction_raw = None
    correction_signed = None
    if mode:
        branch = 'scratch-plus-base'
        initial_request = min(65535, 4 * (unsigned_word(memory, 0x2696) + scratch))
    elif not memory[0x41A5] & 4:
        branch = 'fixed-byte-base'
        initial_request = 4 * base
    elif memory[0x244F] & 32:
        branch = 'corrected-shared-request'
        correction_raw = unsigned_word(memory, 0x570A)
        correction_signed = correction_raw if correction_raw < 32768 else correction_raw - 65536
        normal_coordinate = min(65535, max(0, unsigned_word(memory, 0x19B2) // 2 + correction_signed))
        second_inverse = inverse_curve(calibration[0x155A0], calibration[0x13202], normal_coordinate)
        initial_request = second_inverse['value']
    else:
        branch = 'base-plus-byte-offset'
        initial_request = min(65535, 4 * (unsigned_word(memory, 0x2696) + offset))
    upper_lookup = None
    upper_product = None
    if memory[0x417E] & 32:
        upper_raw = raw_maximum
    else:
        upper_lookup = upper_curve(calibration[0x12DAA], calibration[0x12D9A], memory[0x11B3])
        upper_product = 13 * upper_lookup['value']
        upper_raw = max(min(upper_product, raw_maximum), dynamic_minimum)
    upper_stored = upper_raw & 65535
    if initial_request > upper_stored:
        ordered = upper_stored
        ordered_branch = 'upper'
    elif minimum > initial_request:
        ordered = minimum
        ordered_branch = 'lower'
    else:
        ordered = initial_request
        ordered_branch = 'unchanged'
    soft_limit = max(0, 4 * base - 20)
    predicate_6f = bool(memory[0x5866] & 128)
    predicate_121 = None if predicate_6f else bool(memory[0x5A7C] & 128)
    first_active = bool(predicate_6f or predicate_121)
    soft_result = min(ordered, soft_limit) if first_active else ordered
    predicate_70 = bool(memory[0x5869] & 128)
    predicate_122 = None if predicate_70 else bool(memory[0x5A7F] & 128)
    second_active = bool(predicate_70 or predicate_122)
    final = min(soft_result, hard_limit) if second_active else soft_result
    after = bytearray(memory)
    for address, value in ((0x28F8, scratch), (0x3508, upper_stored), (0x28BE, final)):
        after[address:address + 2] = value.to_bytes(2, 'big')
    return dict(channel=1, first_coordinate=first_coordinate, first_inverse=first_inverse, scratch=scratch,
                mode=mode, branch=branch, normal_coordinate=normal_coordinate, second_inverse=second_inverse,
                correction_raw=correction_raw, correction_signed=correction_signed, initial_request=initial_request,
                upper_lookup=upper_lookup, upper_product=upper_product, raw_maximum=raw_maximum,
                dynamic_minimum=dynamic_minimum, upper_raw=upper_raw, upper_stored=upper_stored,
                minimum=minimum, ordered=ordered, ordered_branch=ordered_branch, soft_limit=soft_limit,
                predicate_6f=predicate_6f, predicate_121=predicate_121, first_active=first_active,
                soft_result=soft_result, predicate_70=predicate_70, predicate_122=predicate_122,
                second_active=second_active, hard_limit=hard_limit, value=final, memory=bytes(after))
