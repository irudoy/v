"""Complete raw endpoint inputs and separate held-other surface-word alternatives."""
from copy import deepcopy
from kb import test_contract
from kb import conditional_endpoint_blend_contract as contract

RAM_BASE = 0x01000000
RAM_SIZE = 65536
RAM_FIELDS = (('word_10d2', 0x10D2, 2), ('word_10e2', 0x10E2, 2), ('word_1210', 0x1210, 2),
              ('prior_18e6', 0x18E6, 2), ('prior_18ec', 0x18EC, 2), ('prior_18ee', 0x18EE, 2),
              ('word_2420', 0x2420, 2), ('byte_245c', 0x245C, 1), ('byte_4255', 0x4255, 1))
WIDTHS = {name: width * 8 for name, at, width in RAM_FIELDS}
WIDTHS['weight_step'] = 16
WIDTHS['gate_8b3f'] = 8
WIDTHS['gate_89fa'] = 8
ARRAYS = dict(surface_a=256, surface_b=256, axis_x=16, axis_y=16)
WORD_VALUES = (0, 1, 999, 1000, 1001, 32767, 32768, 53499, 53500, 53501, 65534, 65535)
DEFAULTS = dict(
    word_10d2=1000, word_10e2=53500, word_1210=1000,
    prior_18e6=0xCAFE, prior_18ec=0xA55A, prior_18ee=0x5AA5,
    word_2420=32768, byte_245c=0, byte_4255=0, weight_step=300, gate_8b3f=0x18, gate_89fa=0x60, pattern=0xA5,
    surface_a=[0x6000 + row * 257 + column * 113 for row in range(16) for column in range(16)],
    surface_b=[0xA000 - row * 123 - column * 97 for row in range(16) for column in range(16)],
    axis_x=[1000 + index * 3500 for index in range(16)],
    axis_y=[1000 + index * 3500 for index in range(16)],
    context=[*((0x18765430 + i * 0x01030507) & 0xFFFFFFFF for i in range(15)),
             0x12344321, 0x13579BDF, 0x2468ACE0, 0, 0xB6C70000],
)


def require_case(case):
    if (type(case) is not dict or set(case) != {*WIDTHS, *ARRAYS, 'context', 'pattern', 'index', 'kind'}
            or type(case['index']) is not int or case['index'] < 0 or type(case['kind']) is not str
            or type(case['pattern']) is not int or not 0 <= case['pattern'] <= 255
            or any(type(case[name]) is not int or not 0 <= case[name] < (1 << bits) for name, bits in WIDTHS.items())):
        raise ValueError('the conditional endpoint blend changes a complete typed raw scalar input')
    for name, count in (*ARRAYS.items(), ('context', 20)):
        values = case[name]
        limit = 0x100000000 if name == 'context' else 65536
        if type(values) is not list or len(values) != count or any(type(value) is not int or not 0 <= value < limit for value in values):
            raise ValueError('the conditional endpoint blend truncates a complete word array or incoming context')
    if case['context'][18] & ~0x3F1:
        raise ValueError('the conditional endpoint blend changes the admitted complete I/M/Q/T input')


def cases(source, image):
    rows = []

    def add(kind, **changes):
        value = deepcopy(DEFAULTS)
        value.update(changes)
        value.update(index=len(rows), kind=kind)
        rows.append(value)

    add('exact-stock-ROM-disabled-by-second-actual-gate', gate_8b3f=0x18, gate_89fa=0x40)
    add('complete-natural-endpoint-weight-and-blend')
    for field in ('gate_8b3f', 'gate_89fa'):
        for raw in range(256):
            add('independent-actual-ROM-control-byte-and-branch', **{field:raw})
    for first in (0, 0x18, 0x7F, 0x80, 0xFF):
        for second in (0, 0x1F, 0x20, 0x40, 0x60, 0xFF):
            add('ordered-first-and-second-real-ROM-gates', gate_8b3f=first, gate_89fa=second)
    for register in range(20):
        values = (0, 1, 0x7FFF, 0x8000, 0xFFFF, 0x10000, 0x80000000, 0xFFFFFFFF)
        if register == 18:
            values = (0, 1, 0xF0, 0x100, 0x200, 0x301, 0x3F1)
        for raw in values:
            context = list(DEFAULTS['context'])
            context[register] = raw
            add('independent-complete-context-field', context=context)
    for qm in (0, 0x100, 0x200, 0x300):
        for interrupt in range(0, 256, 16):
            for t in (0, 1):
                context = list(DEFAULTS['context'])
                context[18] = qm | interrupt | t
                add('complete-QM-interrupt-T-context', context=context)
    for name, at, width in RAM_FIELDS:
        for raw in (range(256) if width == 1 else WORD_VALUES):
            add('independent-physical-RAM-input-or-prior-output', **{name: raw})
    for primary, alternate in ((0, 0), (0, 1), (1, 0), (32767, 32768), (32768, 32767), (65535, 0), (0, 65535)):
        add('actual-enabled-maximum-selector-order-and-equality', byte_4255=128,
            word_10d2=primary, word_10e2=alternate)
    for field in ('surface_a', 'surface_b'):
        for cell in range(256):
            row, column = divmod(cell, 16)
            for raw in (0x7000, 0x9000):
                table = list(DEFAULTS[field])
                table[cell] = raw
                add('held-other-one-actual-surface-word', **{
                    field: table, 'word_1210': DEFAULTS['axis_x'][row],
                    'word_10d2': DEFAULTS['axis_y'][column], 'word_10e2': DEFAULTS['axis_y'][column],
                    'word_2420': 0 if field == 'surface_a' else 65535,
                    'byte_245c': 0 if field == 'surface_a' else 4,
                })
    for row in range(15):
        for column in range(15):
            add('actual-two-axis-interior-four-neighbor-path', word_1210=DEFAULTS['axis_x'][row]+1750,
                word_10d2=DEFAULTS['axis_y'][column]+1750, word_10e2=DEFAULTS['axis_y'][column]+1)
    for axis in ('axis_x', 'axis_y'):
        for index in range(16):
            for raw in (0, 1, 32767, 65535):
                values = list(DEFAULTS[axis])
                values[index] = raw
                add('complete-raw-axis-word-alternative', **{axis: values, 'word_1210': 12001, 'word_10d2': 19001})
    for field in ('surface_a', 'surface_b'):
        for cell in (0, 1, 15, 16, 255):
            row, column = divmod(cell, 16)
            for raw in (0, 1, 32767, 32768, 65535):
                values = list(DEFAULTS[field])
                values[cell] = raw
                add('actual-word-sign-boundary-and-return', **{
                    field: values, 'word_1210': DEFAULTS['axis_x'][row], 'word_10d2': DEFAULTS['axis_y'][column]})
    for direction in (0, 4):
        for step in (0, 1, 300, 65535):
            for prior in (0, 1, 299, 300, 301, 32767, 32768, 65234, 65235, 65236, 65534, 65535):
                add('real-weight-direction-saturation-and-exact-endpoint-choice', byte_245c=direction,
                    weight_step=step, word_2420=prior)
    for signed_a, signed_b in ((-32768, 32767), (32767, -32768), (-32768, -32768), (32767, 32767), (-1, 0), (0, -1)):
        for weight in (0, 1, 2, 32767, 32768, 65534, 65535):
            add('independent-signed-blend-and-maximum-exact-B-branch',
                surface_a=[signed_a+32768]*256, surface_b=[signed_b+32768]*256,
                weight_step=0, word_2420=weight)
    add('actual-equal-word-interpolation-with-positive-axis-fractions', surface_a=[32767]*256,
        surface_b=[32768]*256, word_1210=1001, word_10d2=1001)
    for pattern in (0, 1, 0x5A, 0x80, 0xFF):
        add('complete-other-RAM-pattern', pattern=pattern)
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
    mapping = {row['address']: b''.join(word.to_bytes(2, 'big') for word in case[row['name']])
               for row in contract.DECLARED['input_blobs']}
    mapping[0x90A0] = case['weight_step'].to_bytes(2, 'big')
    mapping[0x8B3F] = bytes([case['gate_8b3f']])
    mapping[0x89FA] = bytes([case['gate_89fa']])
    return mapping


def calibrations(source, image, case):
    fixture, _ = contract.fixture_for_case(source, image, case)
    return {row['address']: fixture[row['address']:row['address']+row['size']] for row in contract.CONTROLLED_CALIBRATION}


def require_input(source, image, case, observed):
    wanted = calibrations(source, image, case)
    if (observed['entry'] != contract.ENTRY or not test_contract.exact(observed['context'], context(source, case))
            or observed['memory_before'] != (memory(case),)
            or not test_contract.exact(observed['calibration_before'], wanted)
            or not test_contract.exact(observed['calibration_after'], wanted)):
        raise ValueError('the conditional endpoint blend changes a complete immutable input or controlled calibration')


def header(declared, image):
    source, cal, bound = declared['source'], contract.CONTROLLED_CALIBRATION, contract.BOUND_SPANS
    lines = ['/* Complete raw inputs for the full natural endpoint and blend caller. */',
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
