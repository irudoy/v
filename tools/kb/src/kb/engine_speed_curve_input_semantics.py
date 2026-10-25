"""Independent complete timing-state equations and physical engine-speed coordinate handoff."""

RAM_BASE = 0x01000000
MASK = 0xFFFFFFFF


def signed(value, bits=32):
    return value-(1 << bits) if value & (1 << (bits-1)) else value


def evaluate(memory, calibration, frame_before):
    if (type(memory) is not bytes or len(memory) != 65536
            or type(frame_before) is not bytes or len(frame_before) != 192):
        raise ValueError('the speed-coordinate equations need complete incoming RAM and frame')
    after = bytearray(memory)
    operands, calls, tails, lookups = [], [], [], []

    def read(site, address, width, register, domain='ram'):
        if domain == 'ram':
            raw = bytes(after[address:address+width])
        else:
            spans = [(at,data) for at,data in calibration.items()
                     if at <= address and address+width <= at+len(data)]
            if len(spans) != 1:
                raise ValueError('the speed-coordinate equations lose an exact physical ROM span')
            at, data = spans[0]
            if type(data) is not bytes:
                raise ValueError('the speed-coordinate equations replace immutable calibration')
            raw = data[address-at:address-at+width]
        operands.append(dict(site=site, mode='read', address=RAM_BASE+address if domain == 'ram' else address,
            width_bytes=width, register=register, domain=domain, bytes=raw.hex()))
        return int.from_bytes(raw, 'big')

    def write(site, address, width, value, register):
        raw = (value & ((1 << (width*8))-1)).to_bytes(width, 'big')
        after[address:address+width] = raw
        operands.append(dict(site=site, mode='write', address=RAM_BASE+address, width_bytes=width,
                             register=register, domain='ram', bytes=raw.hex()))

    def call(site, target, arguments, sp_delta=-44, returned=None):
        row = dict(site=site, target=target, arguments=arguments, sp_delta=sp_delta, return_address=site+4)
        if returned is not None:
            row['returned'] = returned
        calls.append(row)
        return row

    def linear(first, second, fraction):
        change = abs(second-first)*fraction//65536
        return first+change if second >= first else first-change

    def interpolate(site, first, second, fraction, sp_delta):
        value = linear(first,second,fraction)
        call(site,0x26740,{0:first,2:second,3:fraction},sp_delta,{0:value})
        return value

    def implicit(site, base, coordinate):
        parent = call(site,0x26370,{4:base,5:coordinate})
        index = min(7,coordinate//32)
        fraction = (coordinate%32)*2048 if coordinate < 224 else 0
        if coordinate >= 224:
            first = read(0x26380,base+7,1,0,'rom')
            returned = signed(first,8) & MASK
            second = None
        else:
            first = read(0x26AAC,base+index,1,1,'rom')
            second = read(0x26AAE,base+index+1,1,0,'rom')
            returned = linear(first,second,fraction)
            tails.extend(((0x2637A,0x26A80),(0x26AB6,0x26740)))
        parent['returned'] = {0:returned}
        lookups.append(dict(kind='implicit-byte-curve',site=site,base=base,coordinate=coordinate,
            index=index,fraction=fraction,first=first,second=second,return_register=returned,value=returned&255))
        return returned

    def axis(site, base, coordinate, width, sp_delta):
        entry = 0x26984 if width == 2 else 0x26944
        parent = call(site,entry,{0:base,4:7*width,5:coordinate},sp_delta)
        index, fraction, bracket, scanned = 0, 0, False, []
        for index in range(7,-1,-1):
            knot = read(entry+2,base+index*width,width,1,'rom')
            scanned.append(index)
            if coordinate == knot or coordinate > knot and index == 7:
                break
            if coordinate > knot:
                lower = read(entry+24,base+index*width,width,1,'rom')
                upper = read(entry+26,base+(index+1)*width,width,0,'rom')
                divisor, dividend = upper-lower, (coordinate-knot)*65536
                if divisor <= 0 or not lower < coordinate < upper:
                    raise ValueError('the rightmost speed-coordinate axis loses its positive divisor')
                fraction, bracket = dividend//divisor, True
                call(entry+38,0x26C78,{0:divisor,1:dividend},sp_delta-4,{0:fraction})
                break
        parent['returned'] = {4:index*width,5:fraction}
        value = dict(base=base,coordinate=coordinate,width=width,index=index,fraction=fraction,
                     bracket=bracket,scanned=tuple(scanned))
        lookups.append(dict(kind='axis',**value))
        return value

    def explicit(site, base, axis_base, coordinate, width):
        entry = 0x264CC if width == 2 else 0x26474
        parent = call(site,entry,{4:base,5:axis_base,6:coordinate})
        position = axis(entry+10,axis_base,coordinate,width,-52)
        index, fraction = position['index'], position['fraction']
        second = read(entry+18,base+(index+1)*width,width,0,'rom')
        first = read(entry+24,base+index*width,width,1,'rom')
        returned = linear(first,second,fraction)
        parent['returned'] = {0:returned}
        tails.append((entry+30,0x26740))
        lookups.append(dict(kind='explicit-curve',site=site,base=base,axis=axis_base,width=width,
            coordinate=coordinate,index=index,fraction=fraction,first=first,second=second,value=returned))
        return returned

    def surface(site, outer_coordinate, inner_raw):
        argument = int.from_bytes(frame_before[116:119]+bytes([inner_raw]),'big')
        parent = call(site,0x26140,{4:0x9DBA,5:0x12EBA,6:0x12E92,7:outer_coordinate})
        outer = axis(0x2614C,0x12EBA,outer_coordinate,1,-52)
        inner = axis(0x2615A,0x12E92,inner_raw,1,-60)
        row, column = outer['index'], inner['index']
        rf, cf = outer['fraction'], inner['fraction']
        address, next_row = 0x9DBA+row*8+column, 0x9DBA+(row+1)*8+column
        tails.append((0x2616C,0x26770))
        if cf:
            first = read(0x2678A,address,1,1,'rom')
            second = read(0x2678C,address+1,1,0,'rom')
            upper = interpolate(0x26790,first,second,cf,-52)
            if rf:
                first = read(0x2679A,next_row,1,1,'rom')
                second = read(0x2679C,next_row+1,1,0,'rom')
                lower = interpolate(0x267A0,first,second,cf,-56)
                returned = interpolate(0x267A8,upper,lower,rf,-52)
            else:
                returned = upper
        else:
            first = read(0x267B4,address,1,0,'rom')
            if rf:
                second = read(0x267B6,next_row,1,2,'rom')
                returned = interpolate(0x267BC,first,second,rf,-52)
            else:
                returned = signed(first,8) & MASK
        parent['returned'] = {0:returned}
        lookups.append(dict(kind='byte-surface',site=site,row=row,column=column,row_fraction=rf,
            column_fraction=cf,inner_raw=inner_raw,inner_argument=argument,outer_coordinate=outer_coordinate,
            return_register=returned,value=returned&255))
        return returned

    def clock_term(hot, coolant, threshold):
        address = 0x1842 if hot else 0x1841
        result = 0
        if coolant >= threshold:
            upper = read(0x4B118 if hot else 0x4B26A,0x927C if hot else 0x9278,2,0,'rom')
            lower = read(0x4B11C if hot else 0x4B26C,0x927A if hot else 0x9276,2,0 if hot else 7,'rom')
            if upper > lower:
                current = signed(read(0x4B124 if hot else 0x4B276,0x15F8,4,0))
                if current > lower:
                    second = current if hot else signed(read(0x4B27C,0x15F8,4,0))
                    if second >= upper:
                        result = read(0x4B134 if hot else 0x4B286,0x878A if hot else 0x8789,1,2,'rom')
                        write(0x4B156 if hot else 0x4B2AC,address,1,result,2)
                        return result
                    if not hot:
                        current = signed(read(0x4B28C,0x15F8,4,0))
                    factor = read(0x4B13C if hot else 0x4B28E,0x878A if hot else 0x8789,1,4,'rom')
                    divisor, product = upper-lower, factor*(current-lower)
                    result = product//divisor
                    call(0x4B146 if hot else 0x4B29C,0x21BBC,{0:divisor,1:product},returned={0:result})
                    write(0x4B150 if hot else 0x4B2A6,address,1,result,6)
                    return result
        write(0x4B156 if hot else 0x4B2AC,address,1,0,2)
        return result

    temperature = read(0x4AFF8,0x1071,1,0)
    hysteresis = read(0x4AFFE,0x41DE,1,5)
    adjusted = temperature+(4 if hysteresis&32 else 0)
    threshold = read(0x4B00C,0x86A4,1,2,'rom')
    hysteresis_out = hysteresis|32 if adjusted >= threshold else hysteresis&0xDF
    write(0x4B01E,0x41DE,1,hysteresis_out,2)
    mode = read(0x4B020,0x2458,1,0)
    if not mode&32:
        timer = read(0x4B032,0x86A3,1,6,'rom')
        write(0x4B034,0x2590,1,timer,6)
    switch = read(0x4B038,0x870B,1,0,'rom')
    speed_coordinate = None
    speed_branch = None
    if switch&1 and read(0x4B044,0x2318,2,6) < 16384:
        speed_coordinate = read(0x4B054,0x11B2,1,2)
        speed_return = implicit(0x4B058,0x121A6,speed_coordinate)
        hot = bool(read(0x4B0C0,0x244F,1,0)&4)
        speed_branch = 'first'
    else:
        hot = bool(read(0x4B064,0x244F,1,0)&4)
        selected = False
        if not hot:
            state_flags = read(0x4B070,0x41DE,1,0)
            if state_flags&32 and mode&32:
                selected = bool(read(0x4B07E,0x2590,1,2))
        if selected:
            speed_coordinate = read(0x4B08A,0x11B2,1,2)
            speed_return = implicit(0x4B08E,0x1219E,speed_coordinate)
            hot = bool(read(0x4B0C0,0x244F,1,0)&4)
            speed_branch = 'second'
        else:
            selected_mode = read(0x4B09A,0x22FF,1,0)
            if selected_mode == 3 and mode&128:
                speed_return = signed(read(0x4B0AC,0x86A2,1,6,'rom'),8) & MASK
                speed_branch = 'substitute'
            else:
                speed_coordinate = read(0x4B0B4,0x11B2,1,2)
                speed_return = implicit(0x4B0B8,0x12196,speed_coordinate)
                hot = bool(read(0x4B0C0,0x244F,1,0)&4)
                speed_branch = 'third'
    speed_register = signed(speed_return&255,8)-128
    write(0x4B0D0,0x1511,1,speed_register,2)
    control = read(0x4B0D2,0x4184,1,0)
    if control&64:
        timer = read(0x4B0DE,0x8C3B,1,2,'rom')
        write(0x4B0E2,0x42BC,1,timer,2)
    else:
        flags = read(0x4B0E8,0x22E1,1,0)
        if flags&1 and flags&2:
            flags = read(0x4B0F8,0x4251,1,0)
            write(0x4B0FC,0x4251,1,flags|4,0)
    coolant = read(0x4B100,0x106E,1,0)
    coolant_limit = read(0x4B108,0x8CD1,1,2,'rom')
    correction = clock_term(hot,coolant,coolant_limit)
    if hot:
        coordinate = read(0x4B158,0x106F,1,0)
        base_return = implicit(0x4B15C,0x11F12,coordinate)
        flags = read(0x4B166,0x22E1,1,0)
        if flags&1 and flags&2:
            correction_path = 'hot-two-curves'
            coordinate = read(0x4B174,0x106F,1,0)
            extra = implicit(0x4B178,0x11F1A,coordinate)&255
            held_correction = read(0x4B188,0x1842,1,5)
            quantity = max(0,(base_return&255)-extra-held_correction)
        else:
            flags = read(0x4B1A2,0x4251,1,0)
            grow = False
            if not flags&4:
                timer = read(0x4B1AC,0x42BC,1,2)
                if timer:
                    grow = not bool(read(0x4B1B2,0x4184,1,0)&64)
            if grow:
                correction_path = 'hot-growth'
                coordinate = read(0x4B1B8,0x106F,1,0)
                extra = implicit(0x4B1BC,0x11F22,coordinate)&255
                quantity = min(255,(base_return&255)+extra)
            else:
                correction_path = 'hot-subtraction'
                held_correction = read(0x4B1E0,0x1842,1,2)
                quantity = max(0,(base_return&255)-held_correction)
    else:
        correction_path = 'cold-subtraction'
        coordinate = read(0x4B2AE,0x106F,1,0)
        base_return = implicit(0x4B2B2,0x11F0A,coordinate)
        held_correction = read(0x4B2BA,0x1841,1,2)
        quantity = max(0,(base_return&255)-held_correction)
    write(0x4B2D2,0x12DB,1,quantity,0)
    latch = read(0x4B2EE,0x248D,1,4)
    first_state = read(0x4B2F8,0x1239,1,6)
    use_prior = False
    if latch&16:
        if first_state:
            use_prior = True
        else:
            write(0x4B308,0x248D,1,latch&0xEF,4)
    elif first_state == 1:
        second_state = read(0x4B314,0x1277,1,6)
        if second_state == 0:
            write(0x4B320,0x248D,1,latch|16,4)
            use_prior = True
    if use_prior:
        critical = signed(read(0x4B326,0x1513,1,6),8)
    else:
        if not latch&16 or first_state:
            subtraction = read(0x4B334,0x23C5,1,0)
            base = read(0x4B33A,0x1A7D,1,7)
            first_term = signed(read(0x4B340,0x1511,1,12),8)
            origin = signed(read(0x4B348,0x2404,1,4),8)
            requested = origin-(first_term+quantity-subtraction)-base+64
            stored = max(-128,min(127,signed(requested&65535,16)))
            write(0x4B366,0x1513,1,stored,6)
        critical = 0
    write(0x4B36C,0x1512,1,critical,6)
    surfaces_enabled = bool(read(0x4B384,0x24A7,1,0)&2)
    surface_results = []
    if surfaces_enabled:
        inner = read(0x4B392,0x2442,1,0)
        outer = read(0x4B39A,0x11AE,1,2)
        returned = surface(0x4B3A2,outer,inner)
        surface_results.append(returned)
        write(0x4B3AC,0x1515,1,returned,2)
        inner = read(0x4B3B4,0x2443,1,0)
        outer = read(0x4B3BC,0x11AE,1,2)
        returned = surface(0x4B3C2,outer,inner)
        surface_results.append(returned)
        write(0x4B3CA,0x1516,1,returned,6)
        first = read(0x4B3D0,0x1515,1,2)
        centered = first+(returned&255)-256
        surface_term = ((centered+int(centered<0)) >> 1)-128
    else:
        surface_term = -128
    write(0x4B3F0,0x1514,1,surface_term,2)
    first_word = read(0x4B3F6,0x28B8,2,5)
    second_word = read(0x4B3FA,0x28BA,2,6)
    minimum = min(first_word,second_word)
    factor = max(0,minimum-7350)
    write(0x4B418,0x1900,2,factor,2)
    enabled = bool(read(0x4B41A,0x41AB,1,0)&64)
    addon = 0
    if enabled:
        threshold = read(0x4B424,0x9010,2,2,'rom')
        enabled = minimum >= threshold
    if enabled:
        coordinate = read(0x4B42C,0x106F,1,0)
        byte_value = explicit(0x4B434,0x11EFA,0x11EEA,coordinate,1)
        write(0x4B43A,0x134B,1,byte_value,0)
        coordinate = read(0x4B43E,0x10CA,2,7)
        word_value = explicit(0x4B446,0x147CA,0x1460A,coordinate,2)
        word_value = min(255,word_value)
        write(0x4B458,0x1347,1,word_value,0)
        actual_factor = read(0x4B45E,0x1900,2,2)
        actual_byte = read(0x4B460,0x134B,1,0)
        product = actual_factor*actual_byte*word_value
        call(0x4B470,0x21CE0,{0:500000,1:product},returned={0:product//500000})
        addon = min(255,product//500000)
        write(0x4B482,0x1349,1,addon,0)
    write(0x4B4A0,0x12D5,1,addon,0)
    actual_quantity = read(0x4B4A4,0x12DB,1,0)
    actual_surface = read(0x4B4AA,0x1514,1,2)
    actual_speed = signed(read(0x4B4B0,0x1511,1,7),8)
    actual_critical = signed(read(0x4B4B6,0x1512,1,6),8)
    composed = actual_speed+actual_quantity+actual_critical+actual_surface+addon-128
    final = max(-128,min(127,signed(composed&65535,16)))
    write(0x4B546,0x23EE,1,final,2)
    return dict(memory=bytes(after),operands=operands,calls=calls,tails=tails,lookups=lookups,
        speed_coordinate=speed_coordinate,speed_branch=speed_branch,speed_return=speed_return,
        speed_register=speed_register,speed_byte=(speed_return&255),hot=hot,correction=correction,
        quantity=quantity,base_return=base_return,correction_path=correction_path,
        use_prior_critical=use_prior,critical=critical,surfaces_enabled=surfaces_enabled,
        surface_results=surface_results,surface_term=surface_term,minimum=minimum,factor=factor,
        addon_enabled=enabled,addon=addon,composed=composed,signed_value=final,value=final&255)
