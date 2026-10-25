"""Complete raw native index1 inputs for the actual channel target builder."""
from copy import deepcopy
from kb import test_contract
from kb import channel_target_builder_contract as contract

RAM_BASE = 0x01000000
RAM_SIZE = 65536
RAM_FIELDS = (
    ('word_1340', 0x1340, 2), ('byte_24ce', 0x24CE, 1), ('byte_24d2', 0x24D2, 1),
    ('byte_41a5', 0x41A5, 1), ('byte_244f', 0x244F, 1), ('word_19b2', 0x19B2, 2),
    ('correction_570a', 0x570A, 2), ('word_2696', 0x2696, 2), ('byte_417e', 0x417E, 1),
    ('byte_11b3', 0x11B3, 1), ('record_6f', 0x5866, 1), ('record_121', 0x5A7C, 1),
    ('record_70', 0x5869, 1), ('record_122', 0x5A7F, 1), ('prior_28f8', 0x28F8, 2),
    ('prior_3508', 0x3508, 2), ('prior_28be', 0x28BE, 2),
    ('neighbor_28bc', 0x28BC, 2), ('neighbor_28c0', 0x28C0, 2))
WIDTHS = {name: width * 8 for name, address, width in RAM_FIELDS}
WIDTHS.update({row['name']: row['size'] * 8 for row in contract.DECLARED['control_blobs']})
ARRAYS = {'inverse_curve': (33, 16), 'inverse_axis': (32, 16), 'upper_curve': (9, 8), 'upper_axis': (8, 8)}
WORD_VALUES = (0, 1, 2, 3, 4, 5, 14, 15, 16, 19, 20, 21, 38, 39, 40, 127, 128, 255, 256,
               544, 545, 546, 1023, 1024, 16383, 16384, 32767, 32768, 65534, 65535)
DEFAULTS = dict(word_1340=0, byte_24ce=0, byte_24d2=0, byte_41a5=0, byte_244f=0,
                word_19b2=0, correction_570a=0, word_2696=0, byte_417e=32, byte_11b3=0,
                record_6f=0, record_121=0, record_70=0, record_122=0, prior_28f8=0xA55A,
                prior_3508=0x5AA5, prior_28be=0xCAFE, neighbor_28bc=0xBEEF, neighbor_28c0=0x1234,
                rom_9574=15, rom_9576=227, rom_9578=727, rom_8cb6=39, rom_8cb7=40, rom_92f2=545,
                inverse_curve=[2000 * index for index in range(33)],
                inverse_axis=[1000 * index for index in range(32)], upper_curve=[100] * 9,
                upper_axis=[32 * index for index in range(8)], pattern=0xA5,
                context=[0x18765430, 0x19795937, 0x1A7C5E3E, 0x1B7F6345, 0xAB123401,
                         0x1D856D53, 0x1E88725A, 0x1F8B7761, 0x208E7C68, 0x2191816F,
                         0x22948676, 0x23978B7D, 0x249A9084, 0x259D958B, 0x26A09A92,
                         0x12345721, 0x13579BDF, 0x2468ACE0, 0, 0xB6C70000])


def require_case(case):
    if (type(case) is not dict or set(case) != {*WIDTHS, *ARRAYS, 'context', 'pattern', 'index', 'kind'}
            or type(case['index']) is not int or case['index'] < 0 or type(case['kind']) is not str
            or type(case['pattern']) is not int or not 0 <= case['pattern'] <= 255
            or any(type(case[name]) is not int or not 0 <= case[name] < 1 << bits for name, bits in WIDTHS.items())):
        raise ValueError('the channel builder changes a complete typed raw scalar input')
    for name, (count, bits) in (*ARRAYS.items(), ('context', (20, 32))):
        values = case[name]
        if (type(values) is not list or len(values) != count
                or any(type(value) is not int or not 0 <= value < 1 << bits for value in values)):
            raise ValueError('the channel builder truncates a physical array or complete incoming context')
    if case['context'][4] & 255 != 1 or case['context'][18] & ~0x3F1:
        raise ValueError('the channel builder changes native index1 or the complete admitted I/M/Q/T input')


def cases(source, image):
    rows = []

    def add(kind, **changes):
        value = deepcopy(DEFAULTS)
        value.update(changes)
        value.update(index=len(rows), kind=kind)
        rows.append(value)

    add('complete-natural-native-index1-builder')
    for raw in (39, 100):
        add('held-other-actual-base-byte-and-final-word', rom_8cb6=raw)
    for register in range(20):
        values = (0, 1, 0x7FFF, 0x8000, 0xFFFF, 0x10000, 0x80000000, 0xFFFFFFFF)
        if register == 4:
            values = (1, 0x101, 0xFFFF01, 0x7FFFFF01, 0x80000001, 0xFFFFFF01)
        elif register == 18:
            values = (0, 1, 0xF0, 0x100, 0x200, 0x301, 0x3F1)
        for raw in values:
            incoming = list(DEFAULTS['context'])
            incoming[register] = raw
            add('independent-complete-context-field', context=incoming)
    for qm in (0, 0x100, 0x200, 0x300):
        for interrupt in range(0, 256, 16):
            for t in (0, 1):
                incoming = list(DEFAULTS['context'])
                incoming[18] = qm | interrupt | t
                add('complete-QM-interrupt-T-context', context=incoming)
    for name, address, width in RAM_FIELDS:
        changes = {}
        if name in ('byte_244f', 'word_19b2', 'correction_570a'):
            changes.update(byte_41a5=4, byte_244f=32)
        if name == 'word_2696':
            changes['byte_24ce'] = 4
        if name == 'byte_11b3':
            changes['byte_417e'] = 0
        for raw in (range(256) if width == 1 else WORD_VALUES):
            add('independent-actual-RAM-word-or-byte', **{**changes, name: raw})
    for row in contract.DECLARED['control_blobs']:
        active = {}
        if row['name'] == 'rom_9576':
            active['byte_417e'] = 0
        elif row['name'] == 'rom_8cb7':
            active.update(byte_41a5=4, byte_244f=0)
        elif row['name'] == 'rom_92f2':
            active['record_70'] = 128
        for raw in (range(256) if row['size'] == 1 else WORD_VALUES):
            add('independent-complete-raw-ROM-control', **{**active, row['name']: raw})
    for lower, upper in ((0, 65535), (1, 0), (227, 0), (1000, 1),
                          (16383, 65535), (16384, 0), (32768, 65535), (65535, 1)):
        add('independent-dynamic-minimum-maximum-and-wrapped-publication', byte_417e=0,
            rom_9576=lower, rom_9578=upper)
    for first, second, enabled, normal in ((0, 0, 0, 0), (4, 0, 0, 0), (0, 1, 0, 0),
                                           (4, 1, 4, 32), (0, 0, 4, 0), (0, 0, 4, 32)):
        add('all-natural-request-branch-precedence', byte_24ce=first, byte_24d2=second,
            byte_41a5=enabled, byte_244f=normal, word_2696=16384)
    for coordinate in (0, 1, 2, 1999, 2000, 2001, 30999, 31000, 31001, 61999, 62000, 62001, 65534, 65535):
        add('actual-first-floor-coordinate-boundary', word_1340=coordinate, byte_24ce=4)
    for request in (0, 1, 2, 32767, 32768, 65534, 65535):
        for correction in (0, 1, 32767, 32768, 65535):
            add('actual-signed-correction-and-floor-coordinate', byte_41a5=4, byte_244f=32,
                word_19b2=request, correction_570a=correction, rom_9574=0, rom_9578=16383)
    for cell in range(32):
        for raw in (0, 1024):
            table = list(DEFAULTS['inverse_curve'])
            table[cell] = raw
            add('held-other-one-inverse-active-word', inverse_curve=table, word_1340=2000 * cell,
                byte_24ce=4, rom_9574=0, rom_9578=16383)
            add('actual-second-inverse-active-word', inverse_curve=table, byte_41a5=4, byte_244f=32,
                word_19b2=2000 * cell, rom_9574=0, rom_9578=16383)
    for cell in range(31):
        for descending in (False, True):
            table = [(65535 - 1800 * index if descending else 1800 * index) for index in range(33)]
            add('actual-directed-inverse-interior-fraction', inverse_curve=table, byte_24ce=4,
                word_1340=2000 * cell + 1000, rom_9574=0, rom_9578=16383)
    for cell in range(32):
        for raw in (0, 1, 32767, 65535):
            axis = list(DEFAULTS['inverse_axis'])
            axis[cell] = raw
            add('independent-raw-inverse-axis-knot', inverse_axis=axis, byte_24ce=4, word_1340=24002)
    for axis in ([0] * 32, [65535] * 32, list(reversed(DEFAULTS['inverse_axis'])),
                 [0] * 31 + [65535], [65535, 0] * 16):
        add('raw-duplicate-descending-or-nonmonotonic-word-axis', inverse_axis=axis,
            byte_41a5=4, byte_244f=32, word_19b2=65535, correction_570a=1)
    for raw in (0, 1, 32767, 32768, 65535):
        table = list(DEFAULTS['inverse_curve'])
        table[32] = raw
        add('actual-zero-fraction-physical-inverse-neighbor', inverse_curve=table, word_1340=65535)
    for cell in range(8):
        for raw in (0, 1, 127, 128, 254, 255):
            table = list(DEFAULTS['upper_curve'])
            table[cell] = raw
            add('actual-upper-curve-cell-and-byte-coordinate', upper_curve=table, byte_417e=0,
                byte_11b3=32 * cell, rom_9576=0, rom_9578=65535, rom_8cb6=255)
    for cell in range(7):
        for table in ([16 * index for index in range(9)], [255 - 16 * index for index in range(9)], [100] * 9):
            add('actual-directed-byte-curve-interior-fraction', upper_curve=table, byte_417e=0,
                byte_11b3=32 * cell + 16, rom_9576=0, rom_9578=65535)
    for cell in range(8):
        for raw in (0, 1, 127, 128, 255):
            axis = list(DEFAULTS['upper_axis'])
            axis[cell] = raw
            add('independent-complete-byte-axis-knot', upper_axis=axis, byte_417e=0, byte_11b3=97)
    for axis in ([0] * 8, [255] * 8, list(reversed(DEFAULTS['upper_axis'])), [255, 0] * 4):
        add('raw-duplicate-descending-or-nonmonotonic-byte-axis', upper_axis=axis, byte_417e=0, byte_11b3=129)
    for raw in (0, 1, 127, 128, 255):
        table = list(DEFAULTS['upper_curve'])
        table[8] = raw
        add('actual-zero-fraction-physical-byte-neighbor', upper_curve=table, byte_417e=0, byte_11b3=255)
    for lower, upper in ((0, 0), (0, 1), (1, 0), (15, 39), (156, 39), (157, 39),
                          (65535, 0), (65535, 16383), (0, 16384), (65535, 65535)):
        for mode in (0, 32):
            add('actual-ordered-unrelated-limits-and-lowword-wrap', rom_9574=lower,
                rom_9576=upper, rom_9578=upper, byte_417e=mode)
    for first, second, third, fourth in ((0, 0, 0, 0), (128, 0, 0, 0), (0, 128, 0, 0),
                                        (128, 128, 0, 0), (0, 0, 128, 0), (0, 0, 0, 128),
                                        (0, 0, 128, 128), (128, 128, 128, 128)):
        for base in (0, 1, 4, 5, 6, 39, 100, 255):
            for hard in (0, 1, 135, 136, 137, 545, 65535):
                add('real-fixed-record-short-circuit-and-both-caps', record_6f=first, record_121=second,
                    record_70=third, record_122=fourth, rom_8cb6=base, rom_92f2=hard)
    for pattern in (0, 1, 0x5A, 0x80, 0xFF):
        add('complete-other-RAM-and-neighbor-preservation', pattern=pattern)
    return tuple(rows)


def context(source, case):
    require_case(case)
    return tuple(case['context'])


def memory(case):
    require_case(case)
    out = bytearray([case['pattern']]) * RAM_SIZE
    for name, address, width in RAM_FIELDS:
        out[address:address + width] = case[name].to_bytes(width, 'big')
    return bytes(out)


def input_calibrations(case):
    require_case(case)
    out = {}
    for row in contract.DECLARED['input_blobs']:
        name = row['name']
        width = ARRAYS[name][1] // 8
        out[row['address']] = b''.join(value.to_bytes(width, 'big') for value in case[name])
    for row in contract.DECLARED['control_blobs']:
        out[row['address']] = case[row['name']].to_bytes(row['size'], 'big')
    return out


def calibrations(source, image, case):
    fixture, _ = contract.fixture_for_case(source, image, case)
    return {row['address']: fixture[row['address']:row['address'] + row['size']]
            for row in contract.CONTROLLED_CALIBRATION}


def require_input(source, image, case, observed):
    wanted = calibrations(source, image, case)
    if (observed['entry'] != contract.ENTRY or not test_contract.exact(observed['context'], context(source, case))
            or observed['memory_before'] != (memory(case),)
            or not test_contract.exact(observed['calibration_before'], wanted)
            or not test_contract.exact(observed['calibration_after'], wanted)):
        raise ValueError('the channel builder changes a complete immutable input or physical calibration')


def header(declared, image):
    source, calibration, bound = declared['source'], contract.CONTROLLED_CALIBRATION, contract.BOUND_SPANS
    blobs = []
    indices = {}
    rows = []
    for case in declared['cases']:
        mapping = calibrations(source, image, case)
        blob = b''.join(mapping[row['address']] for row in calibration)
        if blob not in indices:
            indices[blob] = len(blobs)
            blobs.append(blob)
        incoming = context(source, case)
        raw_context = '{{' + ','.join(f'0x{value:x}U' for value in incoming[:15]) + '},' + ','.join(
            f'0x{value:x}U' for value in incoming[15:]) + '}'
        rows.append('{{' + ','.join(f'0x{case[name]:x}U' for name, address, width in RAM_FIELDS) + '},' +
                    raw_context + f',0x{case["pattern"]:02x}U,{indices[blob]}U}},')
    lines = ['/* Complete raw inputs for the natural native index1 channel target builder. */',
             f'#define BUILDER_CALIBRATION_SIZE {sum(row["size"] for row in calibration)}U',
             f'#define BUILDER_BOUND_SIZE {sum(row["size"] for row in bound)}U',
             'static const struct span builder_calibration[] = {' + ','.join(
                 '{%dU,%dU}' % (row['address'], row['size']) for row in calibration) + '};',
             'static const struct span builder_bound[] = {' + ','.join(
                 '{%dU,%dU}' % (row['address'], row['size']) for row in bound) + '};',
             'static const struct span builder_ram_fields[] = {' + ','.join(
                 '{%dU,%dU}' % (address, width) for name, address, width in RAM_FIELDS) + '};',
             'static const uint8_t builder_calibration_blobs[][BUILDER_CALIBRATION_SIZE] = {']
    lines.extend('{' + ','.join(f'0x{value:02x}U' for value in blob) + '},' for blob in blobs)
    lines.extend(('};', f'struct path_case {{ uint32_t ram[{len(RAM_FIELDS)}];struct context context;'
                  'uint8_t pattern;uint32_t calibration_index; };',
                  'static const struct path_case builder_cases[] = {', *rows, '};', ''))
    return '\n'.join(lines).encode()
