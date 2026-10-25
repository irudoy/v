"""Independent integer equations for natural MAF processing and publication.

These equations consume complete declared RAM and calibration bytes. They
provide no execution, native identity, scale or hardware admission by themselves.
"""

from kb import division_callees_semantics as division

MASK = 0xFFFFFFFF


def bank_call_sequence(kind,before,calibrations):
    """Compose existing independent equations over both actual bank calls."""
    steps=[];memory=before
    for bank in (0,1):
        if kind=='compensation-caller':
            result=compensation(bank,memory,int.from_bytes(calibrations[0x9586],'big'),
                                int.from_bytes(calibrations[0x958C],'big'))
        elif kind=='scaling-caller':
            result=scaling(bank,memory,calibrations[0x87F8],int.from_bytes(calibrations[0x92BE],'big'))
        else:raise ValueError('the MAF bank sequence changes its exact existing callee family')
        steps.append(result);memory=result['memory']
    return dict(memory=memory,output=tuple(row['output'] for row in steps),steps=steps)


def signed(value, bits=32):
    value &= (1 << bits) - 1
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def trunc(value, divisor):
    return -(abs(value) // divisor) if value < 0 else value // divisor


def clamp(value, low, high):
    return min(high, max(low, value))


def word(memory, address):
    return int.from_bytes(memory[address:address + 2], 'big')


def long(memory, address):
    return int.from_bytes(memory[address:address + 4], 'big')


def put(memory, address, width, value):
    memory[address:address + width] = (value & ((1 << (width * 8)) - 1)).to_bytes(width, 'big')


def premises(argument, before):
    if (type(argument) is not int or not 0 <= argument <= MASK or argument & 255 not in (0, 1)
            or type(before) is not bytes or len(before) != 65536):
        raise ValueError('the MAF equations need an exact declared bank argument and complete RAM')
    return argument & 255, bytearray(before)


def compensation(argument, before, multiplier, bias):
    bank, memory = premises(argument, before)
    if any(type(value) is not int or not 0 <= value <= 65535 for value in (multiplier, bias)):
        raise ValueError('the compensation equation changes its two unsigned calibration words')
    bit, offset = bank + 1, bank * 2
    input = word(before, 0x101C + offset)
    previous = word(before, 0x1E48 + offset)
    initialized = bool(before[0x3976] & bit)
    denominator = min(65535, previous + bias)
    correction, numerator, quotient = None, None, None
    if not initialized:
        output = input
        memory[0x3976] |= bit
    elif denominator == 0:
        output = (input + 1) & 65535
    else:
        correction = long(before, 0x3998 + bank * 4)
        numerator = (multiplier * (correction >> 16)
                     + ((multiplier * (correction & 65535)) >> 16)) & MASK
        quotient = division.quotient('unsigned', denominator, numerator)
        output = (input - quotient) & 65535
    put(memory, 0x1E48 + offset, 2, output)
    return dict(memory=bytes(memory), bank=bank, input=input, previous=previous, initialized=initialized,
        denominator=denominator, correction=correction, numerator=numerator, quotient=quotient, output=output)


def scaling(argument, before, bounds, default):
    bank, memory = premises(argument, before)
    if (type(bounds) is not bytes or len(bounds) != 2 or type(default) is not int or not 0 <= default <= 65535):
        raise ValueError('the scaling equation changes its exact two bound bytes or default word')
    mode, incoming = before[0x4252], word(before, 0x4970)
    coefficient = incoming
    guarded = not bool(mode & 8)
    reset = guarded and not bounds[1] << 8 <= incoming <= bounds[0] << 8
    if reset:
        coefficient = default
        put(memory, 0x4970, 2, coefficient)
    sample = word(before, 0x1D62 + bank * 2)
    scaled = min(65535, (coefficient * sample) >> 15)
    output = (scaled + int(sample == 0x03FF)) & 65535
    put(memory, 0x101C + bank * 2, 2, output)
    return dict(memory=bytes(memory), bank=bank, mode=mode, incoming_coefficient=incoming,
        coefficient=coefficient, guarded=guarded, reset=reset, sample=sample, scaled=scaled, output=output)


def battery(before,bounds,default):
    if (type(before) is not bytes or len(before)!=65536 or type(bounds) is not bytes or len(bounds)!=2
            or type(default) is not int or not 0<=default<=65535):
        raise ValueError('the battery equations need complete RAM, exact unsigned guard bounds and default')
    memory=bytearray(before);raw=word(before,0x1D6E);sample=(raw>>2)&255
    mode=before[0x4252];incoming=word(before,0x4970);guarded=not bool(mode&8)
    reset=guarded and not bounds[1]*256<=incoming<=bounds[0]*256
    coefficient=default if reset else incoming
    if reset:put(memory,0x4970,2,coefficient)
    scaled=min(65535,coefficient*sample//32768);output=min(255,scaled)
    put(memory,0x1FC4,2,raw);memory[0x1FC6]=sample;memory[0x1188]=output
    return dict(memory=bytes(memory),raw=raw,sample=sample,mode=mode,guarded=guarded,
        reset=reset,incoming_coefficient=incoming,coefficient=coefficient,scaled=scaled,output=output)


def contribution(argument, before, coefficients, alpha, weight):
    bank, memory = premises(argument, before)
    if (type(coefficients) is not bytes or len(coefficients) != 3
            or any(type(value) is not int or not 0 <= value <= 255 for value in (alpha, weight))):
        raise ValueError('the contribution equation changes its exact byte coefficients')
    offset, long_offset, bit = bank * 2, bank * 4, bank + 1
    input = word(before, 0x1DF0 + offset)
    forced = bool(before[0x2449] & 0x80 or before[0x24B8] & 8)
    if forced:
        memory[0x43CA + bank] = 3
    active = bool(before[0x2462] & 1) and not forced and memory[0x43CA + bank] == 0
    if not active:
        reference = long(before, 0x1E10 + long_offset)
        left = (((256 - weight) * reference) & MASK) >> 4
        right = ((weight * input) & MASK) >> 4
        combined = ((left + right) & MASK) >> 4
        output, base = min(combined, 0xFFFFFF), min(combined, 65535)
        put(memory, 0x1DF8 + long_offset, 4, output)
        put(memory, 0x1E00 + offset, 2, base)
        return dict(memory=bytes(memory), bank=bank, active=False, forced=forced, input=input,
            fallback_reference=reference, output=output, base=base,
            correction=signed(word(before, 0x1E1C + offset), 16), magnitude=word(before, 0x1E30 + offset))
    reference = word(before, 0x1E08 + offset)
    delta = word(before, 0x1E18 + offset)
    previous_correction = signed(word(before, 0x1E1C + offset), 16)
    previous_magnitude = word(before, 0x1E30 + offset)
    candidate = reference + trunc(signed(alpha * (input - reference)), 8)
    base = clamp(candidate, 0, 65535)
    residual = previous_magnitude if before[0x1E34] & bit else -previous_magnitude
    residual = clamp(residual + candidate - base, -0xFFFFFF, 0xFFFFFF)
    correction = clamp(trunc(signed(coefficients[1] * (base - delta)), 512)
                       + trunc(signed(coefficients[2] * previous_correction), 256), -32768, 32767)
    factor = coefficients[0] if correction >= 0 else 64
    adjusted = base + (signed(correction * factor) >> 6)
    total = adjusted + residual
    output = 0 if adjusted < 0 else clamp(total, 0, 0xFFFFFF)
    remainder = total if adjusted < 0 or total < 0 else 0
    magnitude = min(abs(remainder), 65535)
    memory[0x1E34] = (memory[0x1E34] | bit) if remainder >= 0 else (memory[0x1E34] & ~bit)
    put(memory, 0x1E00 + offset, 2, base)
    put(memory, 0x1E1C + offset, 2, correction)
    put(memory, 0x1DF8 + long_offset, 4, output)
    put(memory, 0x1E30 + offset, 2, magnitude)
    return dict(memory=bytes(memory), bank=bank, active=True, forced=forced, input=input,
        reference=reference, delta=delta, candidate=candidate, base=base, residual=residual,
        previous_correction=previous_correction, correction=correction, adjusted=adjusted,
        total=total, output=output, remainder=remainder, magnitude=magnitude)


def bank_publication(argument, before):
    bank, memory = premises(argument, before)
    input = long(before, 0x1DF8 + bank * 4)
    correction = signed(word(before, 0x1E2A), 16)
    auxiliary = word(before, 0x2368)
    total = signed((input + correction + auxiliary) & MASK)
    output = max(total, 0)
    put(memory, 0x104C + bank * 4, 4, output)
    return dict(memory=bytes(memory), bank=bank, input=input, correction=correction,
                auxiliary=auxiliary, total=total, output=output)


def diagnostic_copy(argument, before):
    bank, memory = premises(argument, before)
    output = word(before, 0x1D62 + bank * 2)
    put(memory, 0x1A3E + bank * 2, 2, output)
    return dict(memory=bytes(memory), bank=bank, output=output)
