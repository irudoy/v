"""Complete raw EVAP inputs under the exact native output-pointer premise."""
from copy import deepcopy
from kb import test_contract
from kb import evap_result_word_contract as contract

RAM_BASE = 0x01000000
RAM_SIZE = 65536
RAM_FIELDS = (('word_272a', 0x272A, 2), ('byte_41e5', 0x41E5, 1),
    ('byte_10fa', 0x10FA, 1), ('byte_10f9', 0x10F9, 1), ('word_2c92', 0x2C92, 2),
    ('prior_3062', 0x3062, 2), ('prior_2f8d', 0x2F8D, 1), ('prior_2f94', 0x2F94, 1),
    ('prior_3240', 0x3240, 2), ('prior_3018', 0x3018, 2), ('prior_301c', 0x301C, 2))
ROM_FIELDS = (('rom_893e', 0x893E, 1), ('rom_893f', 0x893F, 1),
    ('rom_85c1', 0x85C1, 1), ('rom_94cc', 0x94CC, 2), ('rom_8813', 0x8813, 1))
BLOBS = (('coefficient_a_default', 0x12282, 16, 1), ('coefficient_a_active', 0x122B2, 16, 1),
    ('coefficient_b_cluster', 0x1259A, 25, 1), ('coefficient_b_axis', 0x12A5A, 8, 1),
    ('transform_curve', 0x152D6, 17, 2), ('transform_axis', 0x13C18, 16, 2))
WIDTHS = {name: width * 8 for name, at, width in (*RAM_FIELDS, *ROM_FIELDS)}
ARRAYS = {name: (count, width * 8) for name, at, count, width in BLOBS}


def initial_context():
    result = [*((0x18765430 + index * 0x01030507) & 0xFFFFFFFF for index in range(15)),
        0x12344321, 0x13579BDF, 0x2468ACE0, 0, 0xB6C70000]
    result[4], result[5], result[6] = 0x98760001, 0x76540000, 0x0100301C
    return result


DEFAULTS = {name: 0 for name in WIDTHS}
DEFAULTS.update({name: 0xA5 if width == 1 else 0xA55A for name, at, width in RAM_FIELDS if name.startswith('prior_')})
DEFAULTS.update(word_272a=0, word_2c92=0, rom_893e=0x40, rom_893f=0xC0,
    rom_85c1=0x55, rom_94cc=0x3C00, rom_8813=0x9F, pattern=0xA5,
    coefficient_a_default=[128] * 16, coefficient_a_active=[128] * 16,
    coefficient_b_cluster=[128] * 25, coefficient_b_axis=[32 * index for index in range(8)],
    transform_curve=[1024] * 17, transform_axis=[4096 * index for index in range(16)], context=initial_context())


def require_case(case):
    if (type(case) is not dict or set(case) != {*WIDTHS, *ARRAYS, 'context', 'pattern', 'index', 'kind'}
            or type(case['index']) is not int or case['index'] < 0 or type(case['kind']) is not str
            or type(case['pattern']) is not int or not 0 <= case['pattern'] <= 255
            or any(type(case[name]) is not int or not 0 <= case[name] < (1 << bits) for name, bits in WIDTHS.items())):
        raise ValueError('the EVAP input changes a complete raw scalar width or identity')
    for name, (count, bits) in (*ARRAYS.items(), ('context', (20, 32))):
        values = case[name]
        if type(values) is not list or len(values) != count or any(type(v) is not int or not 0 <= v < (1 << bits) for v in values):
            raise ValueError('the EVAP input changes a complete mixed-width array or independent CPU context')
    if (case['context'][18] & ~0x3F1
            or case['context'][6] != contract.DECLARED['exact_entry_premise']['simulator_address']):
        raise ValueError('the EVAP input changes its exact native output-pointer alias or complete I/M/Q/T premise')


def cases(source, image):
    rows = []
    def add(kind, **updates):
        case = deepcopy(DEFAULTS)
        case.update(updates)
        case.update(index=len(rows), kind=kind)
        rows.append(case)
    add('complete-bounded-writer-default')
    for register in range(20):
        if register == 6:
            continue
        values = ((0, 1, 0x7FFF, 0x8000, 0xFFFF, 0x10000, 0x80000000, 0xFFFFFFFF)
            if register != 18 else (0, 1, 0xF0, 0x100, 0x200, 0x301, 0x3F1))
        for raw in values:
            context = initial_context()
            context[register] = raw
            add('complete-other-CPU-input', context=context)
    for qm in (0, 0x100, 0x200, 0x300):
        for interrupt in range(0, 256, 16):
            for t in (0, 1):
                context = initial_context()
                context[18] = qm | interrupt | t
                add('complete-QM-interrupt-T-input', context=context)
    for raw in (0, 128):
        curve = list(DEFAULTS['coefficient_a_default'])
        curve[0] = raw
        add('held-other-real-result-word-alternative', coefficient_a_default=curve)
    for raw in range(256):
        for field in ('rom_893e', 'rom_893f', 'rom_85c1', 'rom_8813', 'byte_41e5', 'byte_10fa', 'byte_10f9'):
            updates = {field: raw}
            if field in ('rom_85c1', 'byte_10f9'):
                updates.update(rom_893f=16, byte_41e5=4)
                if field == 'rom_85c1':
                    updates['byte_10f9'] = 127
            if field == 'byte_41e5':
                updates['rom_893f'] = 16
            if field == 'byte_10fa':
                updates.update(coefficient_a_default=[17 * i for i in range(16)],
                    coefficient_a_active=[255 - 17 * i for i in range(16)])
            add('complete-actual-byte-control-domain', **updates)
        for active in (False, True):
            add('complete-fixed-byte-curve-coordinate', byte_10fa=raw, rom_893f=16 if active else 0,
                byte_41e5=4, coefficient_a_default=[17 * i for i in range(16)],
                coefficient_a_active=[255 - 17 * i for i in range(16)])
    for active, operating_byte in ((False, 0), (True, 0), (True, 255)):
        for coordinate in range(256):
            add('complete-three-curve-byte-coordinate', rom_893f=16 if active else 0,
                byte_41e5=4, byte_10f9=operating_byte, rom_85c1=128,
                word_272a=coordinate * 256, coefficient_b_cluster=[(37 * i) & 255 for i in range(25)])
    for field, at, width in (*RAM_FIELDS, *ROM_FIELDS):
        if width == 2:
            for raw in (0, 1, 31, 32, 33, 255, 256, 257, 32767, 32768, 65534, 65535):
                add('raw-word-boundaries-and-poison', **{field: raw})
    for name, at, count, width in BLOBS:
        maximum = (1 << (8 * width)) - 1
        for index in range(count):
            for raw in (0, 1, maximum // 2, maximum):
                values = list(DEFAULTS[name])
                values[index] = raw
                updates = {name: values}
                if name == 'transform_curve':
                    updates['word_2c92'] = min(65535, index * 4096)
                add('complete-physical-calibration-cell', **updates)
    for coordinate in (0, 1, 4095, 4096, 4097, 32767, 32768, 61439, 61440, 65535):
        for curve in ([4095 * i for i in range(17)], [65535 - 4095 * i for i in range(17)], [32768] * 17):
            add('actual-word-interpolation-directions', word_2c92=coordinate, transform_curve=curve)
    add('unsigned-word-axis-numerator-bit31', word_2c92=32768, transform_axis=[0] * 15 + [65535])
    for parameter in (0, 1, 2, 31, 32, 33, 255, 256, 257, 32767, 32768, 65535):
        for comparison in (0, 1, 1023, 1024, 1025, 32767, 32768, 65535):
            for upper in (0, 0x12340000, 0x80000000, 0xFFFF0000):
                context = initial_context()
                context[4], context[5] = upper | parameter, (upper ^ 0x43210000) | comparison
                add('independent-low16-arguments-and-arbitrary-upper-bits', context=context)
    for baseline in (0, 1, 31, 32, 255, 256, 4095, 32767, 32768, 65535):
        for difference in (1, 31, 32, 255, 256, 1024, 32767, 65535):
            for gain in (0, 1, 128, 255):
                context = initial_context()
                context[4], context[5] = 1, 0
                add('wide-product-split-and-normalization-saturation', rom_94cc=baseline,
                    rom_8813=gain, transform_curve=[difference] * 17, context=context)
    for baseline in (0, 1, 257, 4095, 32767, 65535):
        for parameter in (1, 2, 31, 32, 255, 256, 257, 65535):
            context = initial_context()
            context[4] = parameter
            add('quotient-remainder-carry-and-normalized-floor', rom_94cc=baseline, context=context)
    for coefficient_a in (0, 1, 127, 128, 129, 255):
        for coefficient_b in (0, 1, 127, 128, 129, 255):
            add('final-product-floor-and-word-saturation', coefficient_a_default=[coefficient_a] * 16,
                coefficient_b_cluster=[coefficient_b] * 25)
    for pattern in (0, 1, 0x55, 0xAA, 0xFF):
        add('complete-unrelated-RAM-pattern', pattern=pattern)
    return tuple(rows)


def context(source, case):
    require_case(case)
    return tuple(case['context'])


def memory(case):
    require_case(case)
    out = bytearray([case['pattern']]) * RAM_SIZE
    for name, at, width in RAM_FIELDS:
        out[at:at + width] = case[name].to_bytes(width, 'big')
    return bytes(out)


def input_calibrations(case):
    require_case(case)
    values = {at: case[name].to_bytes(width, 'big') for name, at, width in ROM_FIELDS}
    values.update({at: b''.join(raw.to_bytes(width, 'big') for raw in case[name]) for name, at, count, width in BLOBS})
    return values


def calibrations(source, image, case):
    fixture, _ = contract.fixture_for_case(source, image, case)
    return {row['address']: fixture[row['address']:row['address'] + row['size']]
        for row in contract.CONTROLLED_CALIBRATION}


def require_input(source, image, case, observed):
    wanted = calibrations(source, image, case)
    if (observed['entry'] != contract.ENTRY or observed['memory_before'] != (memory(case),)
            or not test_contract.exact(observed['context'], context(source, case))
            or not test_contract.exact(observed['calibration_before'], wanted)
            or not test_contract.exact(observed['calibration_after'], wanted)):
        raise ValueError('the EVAP writer changes its exact pointer/context, complete RAM or immutable calibration')


def header(declared, image):
    source, cal, bound = declared['source'], contract.CONTROLLED_CALIBRATION, contract.BOUND_SPANS
    lines = ['/* Complete raw bounded writer inputs with no expected result. */',
        f'#define EVAP_CALIBRATION_SIZE {sum(r["size"] for r in cal)}U',
        f'#define EVAP_BOUND_SIZE {sum(r["size"] for r in bound)}U',
        'static const struct span evap_calibration[] = {' + ','.join('{%dU,%dU}' % (r['address'], r['size']) for r in cal) + '};',
        'static const struct span evap_bound[] = {' + ','.join('{%dU,%dU}' % (r['address'], r['size']) for r in bound) + '};',
        'static const struct span evap_ram_fields[] = {' + ','.join('{%dU,%dU}' % (at, width) for name, at, width in RAM_FIELDS) + '};',
        f'struct path_case {{ uint32_t ram[{len(RAM_FIELDS)}];struct context context;uint8_t pattern;uint32_t calibration_index; }};']
    blobs, indices, inputs = [], {}, []
    for case in declared['cases']:
        raw = context(source, case)
        ctx = '{{' + ','.join(f'0x{v:x}U' for v in raw[:15]) + '},' + ','.join(f'0x{v:x}U' for v in raw[15:]) + '}'
        mapping = calibrations(source, image, case)
        blob = b''.join(mapping[r['address']] for r in cal)
        if blob not in indices:
            indices[blob] = len(blobs)
            blobs.append(blob)
        inputs.append('{{' + ','.join(f'0x{case[name]:x}U' for name, at, width in RAM_FIELDS) + '},' + ctx +
            f',0x{case["pattern"]:02x}U,' + str(indices[blob]) + 'U},')
    lines.append('static const uint8_t evap_calibration_inputs[][EVAP_CALIBRATION_SIZE] = {')
    lines.extend('{' + ','.join(f'0x{v:02x}U' for v in blob) + '},' for blob in blobs)
    lines.extend(('};', 'static const struct path_case evap_cases[] = {', *inputs, '};', ''))
    return '\n'.join(lines).encode()
