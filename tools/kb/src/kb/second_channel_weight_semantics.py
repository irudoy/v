"""Independent word lookups, weight publication and complete second-channel output equations."""

RAM_BASE = 0x01000000
MASK = 0xFFFFFFFF


def signed(value, bits=32):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def evaluate(memory, calibration, frame_before):
    if (type(memory) is not bytes or len(memory) != 65536
            or type(frame_before) is not bytes or len(frame_before) != 192):
        raise ValueError('the second-channel equations require complete incoming RAM and frame')
    after = bytearray(memory)
    operands, calls, tails, lookups = [], [], [], []

    def rom(address, width):
        spans = [(at, raw) for at, raw in calibration.items()
                 if at <= address and address + width <= at + len(raw)]
        if len(spans) != 1:
            raise ValueError('the second-channel equations lose one exact physical ROM span')
        at, raw = spans[0]
        if type(raw) is not bytes:
            raise ValueError('the second-channel equations replace immutable calibration')
        return raw[address-at:address-at+width]

    def read(site, address, width, register, domain='ram'):
        raw = bytes(after[address:address+width]) if domain == 'ram' else rom(address, width)
        operands.append(dict(site=site, mode='read',
            address=RAM_BASE+address if domain == 'ram' else address,
            width_bytes=width, register=register, domain=domain, bytes=raw.hex()))
        return int.from_bytes(raw, 'big')

    def write(site, address, width, value, register):
        raw = (value & ((1 << (width*8))-1)).to_bytes(width, 'big')
        after[address:address+width] = raw
        operands.append(dict(site=site, mode='write', address=RAM_BASE+address,
            width_bytes=width, register=register, domain='ram', bytes=raw.hex()))

    def call(site, target, arguments, sp_delta, returned=None):
        row = dict(site=site, target=target, return_address=site+4,
                   arguments=arguments, sp_delta=sp_delta)
        if returned is not None:
            row['returned'] = returned
        calls.append(row)
        return row

    def axis(site, base, coordinate, count, sp_delta):
        search = call(site, 0x26B84, {0:base, 4:2*(count-1), 5:coordinate}, sp_delta)
        scanned = []
        fraction, bracket, index = 0, False, 0
        for index in range(count-1, -1, -1):
            knot = read(0x26B86, base+index*2, 2, 1, 'rom')
            scanned.append(index)
            if coordinate == knot or coordinate > knot and index == count-1:
                break
            if coordinate > knot:
                lower = read(0x26B9C, base+index*2, 2, 1, 'rom')
                upper = read(0x26B9E, base+(index+1)*2, 2, 0, 'rom')
                divisor, dividend = upper-lower, (coordinate-knot)*65536
                if divisor <= 0 or not lower < coordinate < upper:
                    raise ValueError('the rightmost word bracket loses its positive actual divisor')
                fraction, bracket = dividend//divisor, True
                call(0x26BAA, 0x26D10, {0:divisor, 1:dividend}, sp_delta-4,
                     {0:fraction})
                break
        search['returned'] = {4:index*2, 5:fraction}
        value = dict(base=base, coordinate=coordinate, count=count, index=index,
                     fraction=fraction, scanned=tuple(scanned), bracket=bracket)
        lookups.append(dict(kind='axis', **value))
        return value

    def linear(first, second, fraction):
        change = abs(second-first)*fraction//65536
        return first+change if second >= first else first-change

    def interpolation(site, first, second, fraction, sp_delta):
        value = linear(first, second, fraction)
        call(site, 0x26AF8, {0:first, 2:second, 3:fraction}, sp_delta, {0:value})
        return value

    def curve(site, base, coordinate):
        parent = call(site, 0x266E8, {4:base, 5:0x18F76, 6:coordinate}, -40)
        position = axis(0x266F2, 0x18F76, coordinate, 16, -48)
        index, fraction = position['index'], position['fraction']
        second = read(0x266FA, base+index*2+2, 2, 0, 'rom')
        first = read(0x26700, base+index*2, 2, 1, 'rom')
        value = linear(first, second, fraction)
        parent['returned'] = {0:value}
        tails.append((0x26706, 0x26AF8))
        lookups.append(dict(kind='word-curve', base=base, coordinate=coordinate,
            index=index, fraction=fraction, first=first, second=second, value=value))
        return value

    alternate = bool(read(0x7A81C, 0x249F, 1, 0) & 2)
    coordinate = read(0x7A826 if alternate else 0x7A83C, 0x2698, 2, 0)
    first_curve = curve(0x7A82E if alternate else 0x7A844,
                        0x19090 if alternate else 0x18CF6, coordinate)
    second_coordinate = read(0x7A84C, 0x2698, 2, 0)
    second_curve = curve(0x7A850, 0x190B0 if alternate else 0x18D16, second_coordinate)
    substitute = bool(read(0x7A858, 0x83C1, 1, 0, 'rom') & 128)
    inner_raw = inner_argument = outer_coordinate = surface_return = None
    if substitute:
        weight_return = signed(read(0x7A864, 0x1630C, 2, 5, 'rom'), 16) & MASK
    else:
        inner_raw = read(0x7A86C, 0x2C71, 1, 2) << 8
        inner_argument = int.from_bytes(frame_before[120:122]+inner_raw.to_bytes(2, 'big'), 'big')
        outer_coordinate = read(0x7A87C, 0x10BC, 2, 10)
        parent = call(0x7A882, 0x265F0,
                      {4:0x16F48, 5:0x18A96, 6:0x18A86, 7:outer_coordinate}, -40)
        outer = axis(0x265FC, 0x18A96, outer_coordinate, 8, -48)
        inner = axis(0x2660A, 0x18A86, inner_raw, 8, -56)
        tails.append((0x2661C, 0x26B28))
        row, column = outer['index'], inner['index']
        rf, cf = outer['fraction'], inner['fraction']
        address = 0x16F48+row*16+column*2
        next_row = address+16
        if cf:
            first = read(0x26B44, address, 2, 1, 'rom')
            second = read(0x26B46, address+2, 2, 0, 'rom')
            upper = interpolation(0x26B4A, first, second, cf, -48)
            if rf:
                first = read(0x26B54, next_row, 2, 1, 'rom')
                second = read(0x26B56, next_row+2, 2, 0, 'rom')
                lower = interpolation(0x26B5A, first, second, cf, -52)
                surface_return = interpolation(0x26B62, upper, lower, rf, -48)
            else:
                surface_return = upper
        else:
            first = read(0x26B6E, address, 2, 0, 'rom')
            if rf:
                second = read(0x26B70, next_row, 2, 2, 'rom')
                surface_return = interpolation(0x26B76, first, second, rf, -48)
            else:
                surface_return = signed(first, 16) & MASK
        parent['returned'] = {0:surface_return}
        weight_return = surface_return
        lookups.append(dict(kind='word-surface', row=row, column=column,
            row_fraction=rf, column_fraction=cf, return_register=surface_return,
            value=surface_return & 65535))
    weight = weight_return & 65535
    write(0x7A88C, 0x35F4, 2, weight_return, 5)
    complement = (32768-weight) & MASK
    first_product = (complement*first_curve) & MASK
    second_product = (weight*second_curve) & MASK
    sum_taken = second_product > 0x7FFFFFFF or signed(second_product) > signed((-first_product) & MASK)
    summed = (first_product+second_product) & MASK
    shifted = summed >> 15 if sum_taken else 0
    blended = min(65535, shifted)
    write(0x7A8C8, 0x35CA, 2, blended, 2)
    third_coordinate = read(0x7A8CA, 0x2698, 2, 0)
    common_curve = curve(0x7A8CC, 0x18D36, third_coordinate)
    write(0x7A8D6, 0x35FC, 2, common_curve, 2)
    multiply_common = bool(read(0x7A8D8, 0x245E, 1, 0) & 64)
    if multiply_common:
        actual_blended = read(0x7A8E2, 0x35CA, 2, 6)
        selected = ((common_curve*actual_blended) & MASK) >> 15
    else:
        selected = read(0x7A8F8, 0x35CA, 2, 6)
    factor = read(0x7A902, 0x31E2, 2, 2)
    quotient = MASK//factor if factor else 0
    call(0x7A906, 0x21CE0, {0:factor, 1:MASK}, -40, {0:quotient})
    if not factor:
        write(0x21D6E, 0x9818, 4, 0x44E, 2)
    overflow = selected > quotient
    scaled_product = None
    if overflow:
        scaled = 800
    else:
        factor_again = read(0x7A922, 0x31E2, 2, 6)
        scaled_product = (selected*factor_again) & MASK
        scaled = min(800, scaled_product >> 15)
    last_coordinate = read(0x7A93E, 0x2698, 2, 0)
    coordinate_override = last_coordinate >= 800
    chosen = last_coordinate if coordinate_override else scaled
    limit = read(0x7A94C, 0x3024, 2, 6)
    limited = min(limit, chosen)
    override = bool(read(0x7A95C, 0x4214, 1, 0) & 64)
    output = read(0x7A964, 0x35EA, 2, 2) if override else limited
    product = output*727
    write(0x7A972, 0x35CC, 2, output, 5)
    final = product//800
    call(0x7A976, 0x21CE0, {0:800, 1:product}, -40, {0:final})
    write(0x7A980, 0x1248, 2, final, 2)
    if any(row['mode'] == 'read' and row['address'] == RAM_BASE+0x35F4 for row in operands):
        raise ValueError('the second-channel equations invent a read of overwritten prior35F4')
    return dict(memory=bytes(after), operands=operands, calls=calls, tails=tails, lookups=lookups,
        alternate=alternate, substitute=substitute, coordinate=coordinate,
        first_curve=first_curve, second_curve=second_curve, common_curve=common_curve,
        inner_raw=inner_raw, inner_argument=inner_argument, outer_coordinate=outer_coordinate,
        surface_return=surface_return, weight_return=weight_return, weight=weight,
        complement=complement, first_product=first_product, second_product=second_product,
        sum_taken=sum_taken, summed=summed, shifted=shifted, blended=blended,
        multiply_common=multiply_common, selected=selected, factor=factor, quotient=quotient,
        overflow=overflow, scaled_product=scaled_product, scaled=scaled,
        coordinate_override=coordinate_override, chosen=chosen, limit=limit, limited=limited,
        override=override, output=output, product=product, value=final)
