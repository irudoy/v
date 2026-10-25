"""Independent word interpolation, shared coefficient, conditioning and latch equations."""

MASK = 0xFFFFFFFF


def unsigned_word(memory, at):
    return int.from_bytes(memory[at:at + 2], 'big')


def words(raw, count):
    if type(raw) is not bytes or len(raw) != 2 * count:
        raise ValueError('the shared-weight equations require a complete raw word array')
    return tuple(unsigned_word(raw, 2 * index) for index in range(count))


def position(axis, coordinate):
    if len(axis) != 16 or type(coordinate) is not int or not 0 <= coordinate <= 65535:
        raise ValueError('the shared-weight axis lacks its complete raw word coordinate')
    for index in range(15, -1, -1):
        lower = axis[index]
        if coordinate == lower:
            return index, 0
        if coordinate > lower:
            if index == 15:
                return index, 0
            upper = axis[index + 1]
            if not lower < coordinate < upper:
                raise ValueError('the shared-weight axis loses its actual positive neighboring divisor')
            return index, ((coordinate - lower) * 65536) // (upper - lower)
    return 0, 0


def directed_word(first, second, fraction):
    if not all(type(value) is int and 0 <= value <= 65535 for value in (first, second, fraction)):
        raise ValueError('the shared-weight interpolation loses an unsigned word or fraction')
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
        first = directed_word(first, table[selected + 1], fraction_y)
    if fraction_x:
        selected_next = selected + 16
        cells.append(selected_next)
        second = table[selected_next]
        if fraction_y:
            cells.append(selected_next + 1)
            second = directed_word(second, table[selected_next + 1], fraction_y)
        result = directed_word(first, second, fraction_x)
    else:
        result = first
    returned = result if fraction_x or fraction_y or result < 32768 else result - 65536
    return dict(value=result, returned=returned, row=row, column=column,
        fraction_x=fraction_x, fraction_y=fraction_y, cells=cells)


def curve(raw, axis, coordinate):
    table = words(raw, 17)
    index, fraction = position(words(axis, 16), coordinate)
    value = directed_word(table[index], table[index + 1], fraction)
    return dict(value=value, index=index, fraction=fraction, first=table[index],
        second=table[index + 1], physical_cells=[index, index + 1])


def sign_extended_word(raw):
    return raw if raw < 32768 else raw | 0xFFFF0000


def caller(phase, memory, calibration):
    if type(phase) is not int or phase not in (0, 1) or type(memory) is not bytes or len(memory) != 65536:
        raise ValueError('the shared-weight equations require one exact phase and complete incoming RAM')
    out = bytearray(memory)
    def word(at):
        return unsigned_word(out, at)
    def write_word(at, value):
        out[at:at + 2] = (value & 65535).to_bytes(2, 'big')
    def rom_word(at):
        return unsigned_word(calibration[at], 0)
    if phase == 0:
        surface_addresses = (0x1050E, 0x1070E)
        axis_addresses = (0x131E2, 0x15F20)
        source_address, endpoint_addresses = 0x1210, (0x133A, 0x133C)
        blend_address, rate_address, conditioned_address, final_address = 0x1212, 0x1328, 0x1330, 0x1332
        rate_limit, rate_gain, rate_offset = 0x95D2, 0x8775, 0x840F
        latch_address, latch_enter, latch_exit, compare_addresses = 0x4205, 0x9020, 0x9022, (0x124E, 0x1250)
    else:
        surface_addresses = (0x17CC8, 0x17EC8)
        axis_addresses = (0x18746, 0x19340)
        source_address, endpoint_addresses = 0x1248, (0x1CBA, 0x1CBC)
        blend_address, rate_address, conditioned_address, final_address = 0x124A, 0x1CB2, 0x1CB4, 0x1CB6
        rate_limit, rate_gain, rate_offset = 0x16338, 0x15F69, 0x15F55
        latch_address, latch_enter, latch_exit, compare_addresses = 0x4214, 0x15F9A, 0x15F9C, (0x1286, 0x1288)
    x, y = word(source_address), word(0x10D2)
    endpoint_a, endpoint_b = [surface(calibration[at], calibration[axis_addresses[0]],
        calibration[axis_addresses[1]], x, y) for at in surface_addresses]
    write_word(endpoint_addresses[0], endpoint_a['value'])
    write_word(endpoint_addresses[1], endpoint_b['value'])
    coordinate_refreshed = False
    weight_curve = None
    if phase == 0:
        coordinate_refreshed = bool(out[0x417E] & 8)
        if coordinate_refreshed:
            write_word(0x1A78, y)
        weight_coordinate = word(0x1A78)
        weight_curve = curve(calibration[0x1488A], calibration[0x14C7A], weight_coordinate)
        weight = weight_curve['value']
        write_word(0x190E, weight)
    else:
        weight_coordinate = None
        weight = word(0x190E)
    A, B = endpoint_a['value'], endpoint_b['value']
    blend = (A * (65536 - weight) + B * weight) // 65536
    write_word(blend_address, blend)
    mode = calibration[0x89FB][0]
    rate_enabled = bool(mode & 64)
    rate_branch = 'mode-clear'
    rate = None
    rate_quotient = None
    if rate_enabled:
        if sign_extended_word(y) > sign_extended_word(rom_word(rate_limit)):
            rate_branch = 'coordinate-limit'
        elif out[0x244F] & 128:
            rate_branch = 'diagnostic-gate'
        elif out[0x245E] & 64:
            rate_branch = 'state-gate'
        elif out[0x41BD] & 1:
            rate_branch = 'service-gate'
        elif out[0x245D] & 1:
            rate_branch = 'inhibit-gate'
        else:
            rate_branch = 'rate-add'
            rate_quotient = word(0x10B2) * calibration[rate_gain][0] // 100
        rate = (max(0, min(rate_quotient - calibration[rate_offset][0], x - blend))
            if rate_quotient is not None else 0)
        write_word(rate_address, rate)
        conditioned = min(65535, blend + rate)
    else:
        conditioned = blend
    write_word(conditioned_address, conditioned)
    latch_before = out[latch_address]
    latch = latch_before
    latch_branch = 'retained'
    if not latch & 4:
        if (out[0x4180] & 8 and not out[0x417E] & 8 and not out[0x245D] & 1
                and sign_extended_word(y) < sign_extended_word(rom_word(latch_enter))):
            latch |= 4
            out[latch_address] = latch
            latch_branch = 'set'
    else:
        low, high = (word(at) for at in compare_addresses)
        if (low < high and x >= blend
                or low > high and x <= blend and x <= rom_word(latch_exit)):
            latch &= 0xFB
            out[latch_address] = latch
            latch_branch = 'clear'
    reconciled = False
    reconcile_before = None
    if phase == 1:
        reconcile_before = out[0x4205], latch
        if bool(out[0x4205] & 4) != bool(latch & 4):
            reconciled = True
            out[0x4205] &= 0xFB
            latch &= 0xFB
            out[0x4214] = latch
    final_enabled = (out[0x26B0] not in (1, 4) and out[0x26E0] != 3
        and bool(mode & 8) and not calibration[0x89FA][0] & 1
        and not calibration[0x8B3F][0] & 128 and bool(latch & 4))
    final = conditioned if final_enabled else x
    write_word(final_address, final)
    return dict(phase=phase, x=x, y=y, surface_addresses=surface_addresses, axis_addresses=axis_addresses,
        source_address=source_address, endpoint_addresses=endpoint_addresses, endpoint_a=endpoint_a,
        endpoint_b=endpoint_b, coordinate_refreshed=coordinate_refreshed,
        weight_coordinate=weight_coordinate, weight_curve=weight_curve, weight=weight,
        blend=blend, blend_address=blend_address, mode=mode, rate_enabled=rate_enabled,
        rate_branch=rate_branch, rate_quotient=rate_quotient, rate=rate,
        rate_address=rate_address, conditioned=conditioned, conditioned_address=conditioned_address,
        latch_address=latch_address, latch_before=latch_before, latch_after=latch,
        latch_branch=latch_branch, reconcile_before=reconcile_before, reconciled=reconciled,
        final_enabled=final_enabled, final=final, final_address=final_address, memory=bytes(out))
