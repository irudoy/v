"""Raw paired coefficient inputs with actual lag/history and quantity continuity."""
from copy import deepcopy
from kb import test_contract
from kb import torque_correction_ratio_contract as contract

RAM_BASE = 0x01000000
RAM_SIZE = 65536
RAM_FIELDS = (
    ('word_11bc', 0x11BC, 2), ('byte_4181', 0x4181, 1), ('byte_1071', 0x1071, 1),
    ('byte_2772', 0x2772, 1), ('byte_11b3', 0x11B3, 1), ('word_199e', 0x199E, 2),
    ('word_19c6', 0x19C6, 2), ('word_2408', 0x2408, 2), ('word_2410', 0x2410, 2),
    ('byte_24a3', 0x24A3, 1), ('word_18d4', 0x18D4, 2), ('byte_16a3', 0x16A3, 1),
    ('word_19cc', 0x19CC, 2), ('word_34b8', 0x34B8, 2),
    ('prior_14e2', 0x14E2, 2), ('prior_14e4', 0x14E4, 2), ('prior_1608', 0x1608, 2),
    ('prior_19a0', 0x19A0, 2), ('prior_34d6', 0x34D6, 2),
    ('prior_186c', 0x186C, 1), ('prior_1864', 0x1864, 1),
    *((f'history_{index}', 0x19F6 + 2 * index, 2) for index in range(10)))
ROM_FIELDS = (('rom_8639', 0x8639, 1), ('rom_8e51', 0x8E51, 1),
    ('rom_8c61', 0x8C61, 1), ('rom_83c1', 0x83C1, 1), ('rom_8b38', 0x8B38, 1))
BLOBS = (('coefficient_curve', 0x14C1A, 9), ('coefficient_axis', 0x14ABA, 8),
    ('lag_curve', 0x14E52, 16))
WIDTHS = {name: width * 8 for name, at, width in (*RAM_FIELDS, *ROM_FIELDS)}
ARRAYS = {name: (count, 16) for name, at, count in BLOBS}
ARRAYS.update(producer_context=(20, 32), consumer_context=(20, 32))


def initial_context(phase):
    return [*((0x18765430 + index * 0x01030507 + phase * 0x2030405) & 0xFFFFFFFF for index in range(15)),
        0x12344321 + phase, 0x13579BDF + phase, 0x2468ACE0 + phase, 0, 0xB6C70000 + phase]


DEFAULTS = {name: 0 for name in WIDTHS}
DEFAULTS.update({name: 0xA5 if width == 1 else 0xA55A for name, at, width in RAM_FIELDS if name.startswith('prior_')})
DEFAULTS.update(word_199e=2048, word_19c6=2048, byte_24a3=8, word_18d4=2048,
    byte_4181=128, rom_8639=128, rom_8e51=128, rom_8c61=1,
    coefficient_curve=[256] * 9, coefficient_axis=[8192 * index for index in range(8)],
    lag_curve=[0] * 16, producer_context=initial_context(0), consumer_context=initial_context(1))
DEFAULTS.update({f'history_{index}': 2048 for index in range(10)})


def require_case(case):
    if (type(case) is not dict or set(case) != {*WIDTHS, *ARRAYS, 'index', 'kind'}
            or type(case['index']) is not int or case['index'] < 0 or type(case['kind']) is not str
            or any(type(case[name]) is not int or not 0 <= case[name] < (1 << bits) for name, bits in WIDTHS.items())):
        raise ValueError('the torque ratio input changes its complete raw scalar shape or width')
    for name, (count, bits) in ARRAYS.items():
        values = case[name]
        if type(values) is not list or len(values) != count or any(type(v) is not int or not 0 <= v < (1 << bits) for v in values):
            raise ValueError('the torque ratio input changes a complete raw array or CPU context')
    if any(case[name][18] & ~0x3F1 for name in ('producer_context', 'consumer_context')):
        raise ValueError('the torque ratio context changes its admitted complete I/M/Q/T input')


def cases(source, image):
    rows = []
    def add(kind, **updates):
        case = deepcopy(DEFAULTS)
        case.update(updates)
        case.update(index=len(rows), kind=kind)
        rows.append(case)
    add('complete-actual-two-phase-default')
    for phase in ('producer', 'consumer'):
        for register in range(20):
            values = ((0, 1, 0x7FFF, 0x8000, 0xFFFF, 0x10000, 0x80000000, 0xFFFFFFFF)
                if register != 18 else (0, 1, 0xF0, 0x100, 0x200, 0x301, 0x3F1))
            for raw in values:
                context = initial_context(0 if phase == 'producer' else 1)
                context[register] = raw
                add('complete-independent-phase-context', **{phase + '_context': context})
        for qm in (0, 0x100, 0x200, 0x300):
            for interrupt in range(0, 256, 16):
                for t in (0, 1):
                    context = initial_context(0 if phase == 'producer' else 1)
                    context[18] = qm | interrupt | t
                    add('complete-phase-QM-interrupt-T', **{phase + '_context': context})
    for index in range(8):
        for raw in (0, 512):
            curve = list(DEFAULTS['coefficient_curve'])
            curve[index] = raw
            add('coefficient-word-held-other-causal-alternative', coefficient_curve=curve, word_11bc=index * 8192)
    for raw in (0, 1, 32767, 32768, 65534, 65535):
        curve = list(DEFAULTS['coefficient_curve'])
        curve[8] = raw
        add('physical-last-neighbor-at-zero-fraction', coefficient_curve=curve, word_11bc=65535)
    for index in range(8):
        for coordinate in (max(0, index * 8192 - 1), index * 8192, min(65535, index * 8192 + 1)):
            for curve in ([8191 * i for i in range(9)], [65535 - 8191 * i for i in range(9)], [32768] * 9):
                add('actual-directed-word-interpolation', coefficient_curve=curve, word_11bc=coordinate)
        for raw in (0, 1, 32767, 32768, 65535):
            axis = list(DEFAULTS['coefficient_axis'])
            axis[index] = raw
            add('complete-raw-axis-word', coefficient_axis=axis)
    add('unsigned-axis-numerator-bit31', coefficient_axis=[0] * 7 + [65535], word_11bc=32768)
    for index in range(16):
        for raw in (0, 32768, 65535):
            curve = [0] * 16
            curve[index] = raw
            add('complete-lag-table-word', lag_curve=curve, byte_11b3=index * 16)
    for raw in range(256):
        for field in ('byte_4181', 'byte_1071', 'byte_2772', 'byte_11b3', 'byte_24a3',
                'byte_16a3', 'rom_8639', 'rom_8e51', 'rom_8c61', 'rom_83c1', 'rom_8b38'):
            updates = {field: raw}
            if field in ('rom_8639', 'byte_2772'):
                updates.update(byte_4181=0, byte_1071=32)
                if field == 'rom_8639':
                    updates['byte_2772'] = 224
            if field == 'byte_16a3':
                updates.update(rom_8b38=2, rom_83c1=32, word_18d4=32767)
            if field == 'rom_8c61':
                updates.update({f'history_{i}': 1024 * (i + 1) for i in range(10)})
            if field == 'byte_11b3':
                updates['lag_curve'] = [4095 * i for i in range(16)]
            add('complete-actual-byte-domain', **updates)
    for field, at, width in RAM_FIELDS:
        if width == 2:
            for raw in (0, 1, 255, 256, 257, 32766, 32767, 32768, 32769, 65534, 65535):
                add('signed-word-boundary-and-publication-poison', **{field: raw})
    for previous in (0, 1, 32767, 32768, 65535):
        for target in (0, 1, 32767, 32768, 65535):
            for weight in (0, 1, 32768, 65535):
                add('signed-lag-floor-and-stuck-progress', word_199e=previous, word_19c6=target, lag_curve=[weight] * 16)
    for source in (0, 1, 255, 256, 32766, 32767, 32768, 65535):
        for divisor in (0, 1, 2, 255, 256, 257, 32767, 32768, 65535):
            for offset in (0, 65535):
                updates = dict(word_19cc=source, word_34b8=source, word_199e=divisor,
                    word_19c6=divisor, word_2408=offset, rom_83c1=32, word_18d4=divisor,
                    coefficient_curve=[0] * 9, **{f'history_{i}': divisor for i in range(10)})
                add('actual-signed-ratio-clamp-sentinel-and-zero-divisor', **updates)
    for source in (0, 1, 32767, 32768, 65535):
        add('independent-first-ratio-sentinel', word_19cc=32767, word_34b8=source)
        add('independent-second-ratio-sentinel', word_34b8=32767, word_19cc=source)
    for divisor in (0, 1, 32767, 32768, 65535):
        for count in (0, 1, 5, 6, 7, 127, 128, 255):
            add('actual-factor-signed-truncation-and-word-wrap', word_18d4=divisor, byte_16a3=count,
                rom_83c1=32, rom_8b38=2)
    for curve in ([0] * 9, [1] * 9, [32767] * 9, [32768] * 9, [65535] * 9):
        for source in (0, 1, 127, 128, 129, 255):
            add('actual-positive-negative-product-and-zero-clamp', coefficient_curve=curve, byte_1071=source)
    return tuple(rows)

def context(source, case, phase):
    require_case(case)
    if type(phase) is not int or phase not in (0, 1):
        raise ValueError('the torque ratio input changes its fixed phase identity')
    return tuple(case[('producer', 'consumer')[phase] + '_context'])


def memory(case):
    require_case(case)
    out = bytearray([0xA5]) * RAM_SIZE
    for name, at, width in RAM_FIELDS:
        out[at:at + width] = case[name].to_bytes(width, 'big')
    return bytes(out)


def input_calibrations(case):
    require_case(case)
    out = {at: case[name].to_bytes(width, 'big') for name, at, width in ROM_FIELDS}
    out.update({at: b''.join(raw.to_bytes(2, 'big') for raw in case[name]) for name, at, count in BLOBS})
    return out


def calibrations(source, image, case):
    fixture, _ = contract.fixture_for_case(source, image, case)
    return {row['address']: fixture[row['address']:row['address'] + row['size']]
        for row in contract.CONTROLLED_CALIBRATION}


def require_input(source, image, case, observed, phase, previous=None):
    wanted = calibrations(source, image, case)
    if (observed['phase'] != phase or observed['entry'] != contract.ENTRIES[phase]
            or not test_contract.exact(observed['context'], context(source, case, phase))
            or not test_contract.exact(observed['calibration_before'], wanted)
            or not test_contract.exact(observed['calibration_after'], wanted)):
        raise ValueError('the torque ratio phase changes complete immutable raw input or calibration')
    if phase == 0:
        if previous is not None or observed['memory_before'] != (memory(case),):
            raise ValueError('the torque ratio producer changes its complete initial RAM')
    elif (previous is None or previous['phase'] != 0 or previous['pair'] != observed['pair']
            or previous['memory_after'] != observed['memory_before']
            or not test_contract.exact(previous['calibration_after'], observed['calibration_before'])
            or previous['bound_after'] != observed['bound_before']):
        raise ValueError('the torque ratio consumer resets or substitutes actual producer RAM or code/calibration')


def header(declared, image):
    source = declared['source']
    cal, bound = contract.CONTROLLED_CALIBRATION, contract.BOUND_SPANS
    lines = ['/* Raw paired inputs only; no correction, ratio or expected output. */',
        f'#define QUANTITY_CALIBRATION_SIZE {sum(r["size"] for r in cal)}U',
        f'#define QUANTITY_BOUND_SIZE {sum(r["size"] for r in bound)}U',
        'static const struct span quantity_calibration[] = {' + ','.join('{%dU,%dU}' % (r['address'], r['size']) for r in cal) + '};',
        'static const struct span quantity_bound[] = {' + ','.join('{%dU,%dU}' % (r['address'], r['size']) for r in bound) + '};',
        'struct path_case { ' + ''.join('uint32_t ' + name + ';' for name, at, width in RAM_FIELDS) +
        'struct context contexts[2];uint32_t calibration_index; };']
    calibration_inputs, calibration_indices, cases = [], {}, []
    for case in declared['cases']:
        require_case(case)
        contexts = []
        for phase in (0, 1):
            raw = context(source, case, phase)
            contexts.append('{{' + ','.join(f'0x{v:x}U' for v in raw[:15]) + '},' + ','.join(f'0x{v:x}U' for v in raw[15:]) + '}')
        mapping = calibrations(source, image, case)
        blob = b''.join(mapping[r['address']] for r in cal)
        if blob not in calibration_indices:
            calibration_indices[blob] = len(calibration_inputs)
            calibration_inputs.append(blob)
        cases.append('{' + ','.join(f'0x{case[name]:x}U' for name, at, width in RAM_FIELDS) + ',{' +
            ','.join(contexts) + '},' + str(calibration_indices[blob]) + 'U},')
    lines.append('static const uint8_t quantity_calibration_inputs[][QUANTITY_CALIBRATION_SIZE] = {')
    lines.extend('{' + ','.join(f'0x{raw:02x}U' for raw in blob) + '},' for blob in calibration_inputs)
    lines.extend(('};', 'static const struct path_case quantity_cases[] = {', *cases, '};', ''))
    return '\n'.join(lines).encode()
