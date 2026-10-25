"""Complete raw endpoint-normalizer inputs and unchanged selected status-byte preimages."""
from copy import deepcopy
from kb import test_contract
from kb import endpoint_normalizer_writer_withdrawal_contract as contract

RAM_BASE = 0x01000000
RAM_SIZE = 65536
RAM_FIELDS = (('word_113c', 0x113C, 2), ('word_338c', 0x338C, 2),
    ('word_338e', 0x338E, 2), ('word_3396', 0x3396, 2),
    ('prior_3478', 0x3478, 2), ('prior_347a', 0x347A, 2), ('prior_347c', 0x347C, 2),
    ('byte_41fb', 0x41FB, 1))
WIDTHS = {name: width * 8 for name, at, width in RAM_FIELDS}
WIDTHS.update(lower_guard=16)
ARRAYS = dict(upper=16, lower=16, axis=16)
WORD_VALUES = (0, 1, 799, 800, 801, 999, 1000, 1001, 32767, 32768, 53499, 53500, 53501, 65534, 65535)
DEFAULTS = dict(word_113c=1000, word_338c=48768, word_338e=48768, word_3396=48768,
    prior_3478=0xA55A, prior_347a=0x5AA5, prior_347c=0xCAFE,
    byte_41fb=0xA5, lower_guard=0, pattern=0xA5,
    upper=[32000] * 16, lower=[0] * 16, axis=[1000 + 3500 * i for i in range(16)],
    context=[*((0x18765430 + i * 0x01030507) & 0xFFFFFFFF for i in range(15)),
        0x12344321, 0x13579BDF, 0x2468ACE0, 0, 0xB6C70000])


def require_case(case):
    if (type(case) is not dict or set(case) != {*WIDTHS, *ARRAYS, 'context', 'pattern', 'index', 'kind'}
            or type(case['index']) is not int or case['index'] < 0 or type(case['kind']) is not str
            or type(case['pattern']) is not int or not 0 <= case['pattern'] <= 255
            or any(type(case[name]) is not int or not 0 <= case[name] < (1 << bits) for name, bits in WIDTHS.items())):
        raise ValueError('the endpoint-normalizer input changes a complete typed raw scalar or status byte')
    for name, count in (*ARRAYS.items(), ('context', 20)):
        values = case[name]
        limit = 0x100000000 if name == 'context' else 65536
        if type(values) is not list or len(values) != count or any(type(v) is not int or not 0 <= v < limit for v in values):
            raise ValueError('the endpoint-normalizer input truncates a complete word blob or incoming CPU context')
    if case['context'][18] & ~0x3F1:
        raise ValueError('the endpoint-normalizer input changes its admitted full I/M/Q/T controls')


def cases(source, image):
    rows = []
    def add(kind, **updates):
        value = deepcopy(DEFAULTS)
        value.update(updates)
        value.update(index=len(rows), kind=kind)
        rows.append(value)
    add('complete-natural-endpoint-normalizer')
    add('stock-zero-endpoints-real-three-word-fallback', upper=[0] * 16, lower=[0] * 16)
    for register in range(20):
        values = (0, 1, 0x7FFF, 0x8000, 0xFFFF, 0x10000, 0x80000000, 0xFFFFFFFF) if register != 18 else (0, 1, 0xF0, 0x100, 0x200, 0x301, 0x3F1)
        for raw in values:
            context = list(DEFAULTS['context'])
            context[register] = raw
            add('complete-independent-CPU-input', context=context)
    for qm in (0, 0x100, 0x200, 0x300):
        for interrupt in range(0, 256, 16):
            for t in (0, 1):
                context = list(DEFAULTS['context'])
                context[18] = qm | interrupt | t
                add('complete-QM-interrupt-T-input', context=context)
    for raw in range(256):
        add('entire-selected-status-byte-preimage-preserved', byte_41fb=raw)
    for pattern in (0, 1, 0x55, 0xA5, 0xFF):
        add('complete-unrelated-RAM-pattern', pattern=pattern)
    for field, at, width in RAM_FIELDS:
        if width == 2:
            for raw in WORD_VALUES:
                add('complete-signed-word-coordinate-and-output-poison-boundary', **{field: raw})
    for index in range(16):
        coordinate = DEFAULTS['axis'][index]
        for table, values in (('upper', (16000, 32000)), ('lower', (0, 8000))):
            for raw in values:
                curve = list(DEFAULTS[table])
                curve[index] = raw
                add('held-other-active-endpoint-word', **{table: curve}, word_113c=coordinate)
        for delta in (-1, 0, 1):
            for upper, lower in (([4095 * i for i in range(16)], [1000] * 16),
                    ([65535 - 4095 * i for i in range(16)], [0] * 16)):
                add('complete-directed-interpolation-and-reverse-search', upper=upper, lower=lower,
                    word_113c=max(0, min(65535, coordinate + delta)))
        for raw in (0, 1, 32767, 32768, 65535):
            axis = list(DEFAULTS['axis'])
            axis[index] = raw
            add('complete-independent-raw-axis-word', axis=axis)
    for raw in (0, 1, 32767, 32768, 65535):
        add('physical-lower-neighbor-at-zero-fraction', lower_guard=raw, word_113c=65535)
    add('unsigned-axis-numerator-bit31', axis=[0] * 15 + [65535], word_113c=32768)
    add('actual-search-below-first-knot', word_113c=0)
    for lower, upper in ((0, 0), (65535, 0), (0, 1), (1000, 1001), (0, 32000), (0, 65535), (65534, 65535)):
        for raw in WORD_VALUES:
            add('zero-positive-span-signed-base-clamp-and-real-division', lower=[lower] * 16,
                upper=[upper] * 16, word_338c=raw, word_338e=raw, word_3396=raw)
    for field in ('word_338c', 'word_338e', 'word_3396'):
        for raw in (32768, 0):
            add('held-other-actual-signed-input-publication', **{field: raw})
    return tuple(rows)


def context(source, case):
    require_case(case)
    return tuple(case['context'])

def memory(case):
    require_case(case)
    out = bytearray([case['pattern']]) * RAM_SIZE
    for name, at, width in RAM_FIELDS:
        out[at:at+width] = case[name].to_bytes(width, 'big')
    return bytes(out)

def input_calibrations(case):
    require_case(case)
    out={row['address']:b''.join(word.to_bytes(2,'big') for word in case[row['name']]) for row in contract.DECLARED['input_blobs']}
    out[0x15500]=case['lower_guard'].to_bytes(2,'big')
    return out

def calibrations(source, image, case):
    fixture, _ = contract.fixture_for_case(source, image, case)
    return {row['address']: fixture[row['address']:row['address']+row['size']] for row in contract.CONTROLLED_CALIBRATION}

def require_input(source, image, case, observed):
    wanted = calibrations(source, image, case)
    if (observed['entry'] != contract.ENTRY or not test_contract.exact(observed['context'], context(source, case))
            or observed['memory_before'] != (memory(case),)
            or not test_contract.exact(observed['calibration_before'], wanted)
            or not test_contract.exact(observed['calibration_after'], wanted)):
        raise ValueError('the endpoint normalizer changes a complete immutable input or controlled calibration')

def header(declared, image):
    source, cal, bound = declared['source'], contract.CONTROLLED_CALIBRATION, contract.BOUND_SPANS
    lines = ['/* Complete raw inputs for the full natural endpoint normalizer and boundary caller. */',
             f'#define ENDPOINT_CALIBRATION_SIZE {sum(row["size"] for row in cal)}U',
             f'#define ENDPOINT_BOUND_SIZE {sum(row["size"] for row in bound)}U',
             'static const struct span endpoint_calibration[] = {' + ','.join('{%dU,%dU}' % (row['address'], row['size']) for row in cal) + '};',
             'static const struct span endpoint_bound[] = {' + ','.join('{%dU,%dU}' % (row['address'], row['size']) for row in bound) + '};',
             'static const struct span endpoint_ram_fields[] = {' + ','.join('{%dU,%dU}' % (at, width) for name, at, width in RAM_FIELDS) + '};',
             f'struct path_case {{ uint32_t ram[{len(RAM_FIELDS)}];struct context context;uint8_t pattern,calibration[ENDPOINT_CALIBRATION_SIZE]; }};',
             'static const struct path_case endpoint_cases[] = {']
    for case in declared['cases']:
        raw = context(source, case)
        ctx = '{{' + ','.join(f'0x{value:x}U' for value in raw[:15]) + '},' + ','.join(f'0x{value:x}U' for value in raw[15:]) + '}'
        mapping = calibrations(source, image, case)
        blob = b''.join(mapping[row['address']] for row in cal)
        lines.append('{{' + ','.join(f'0x{case[name]:x}U' for name, at, width in RAM_FIELDS) + '},' + ctx +
                     f',0x{case["pattern"]:02x}U,{{' + ','.join(f'0x{value:02x}U' for value in blob) + '}},')
    return '\n'.join((*lines, '};', '')).encode()

