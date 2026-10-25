"""Raw paired inputs preserve the complete actual shared-weight handoff."""
from copy import deepcopy
from kb import test_contract
from kb import blend_weight_quantity_contract as contract

RAM_BASE = 0x01000000
RAM_SIZE = 65536
RAM_FIELDS = (
    ('word_10d2', 0x10D2, 2), ('word_1210', 0x1210, 2), ('word_1248', 0x1248, 2),
    ('word_1a78', 0x1A78, 2), ('word_10b2', 0x10B2, 2),
    ('word_124e', 0x124E, 2), ('word_1250', 0x1250, 2),
    ('word_1286', 0x1286, 2), ('word_1288', 0x1288, 2),
    ('byte_417e', 0x417E, 1), ('byte_4180', 0x4180, 1),
    ('byte_4205', 0x4205, 1), ('byte_4214', 0x4214, 1),
    ('byte_244f', 0x244F, 1), ('byte_245e', 0x245E, 1),
    ('byte_41bd', 0x41BD, 1), ('byte_245d', 0x245D, 1),
    ('byte_26b0', 0x26B0, 1), ('byte_26e0', 0x26E0, 1),
    ('prior_190e', 0x190E, 2), ('prior_133a', 0x133A, 2), ('prior_133c', 0x133C, 2),
    ('prior_1212', 0x1212, 2), ('prior_1328', 0x1328, 2), ('prior_1330', 0x1330, 2),
    ('prior_1332', 0x1332, 2), ('prior_1cba', 0x1CBA, 2), ('prior_1cbc', 0x1CBC, 2),
    ('prior_124a', 0x124A, 2), ('prior_1cb2', 0x1CB2, 2), ('prior_1cb4', 0x1CB4, 2),
    ('prior_1cb6', 0x1CB6, 2))
ROM_FIELDS = (
    ('rom_89fb', 0x89FB, 1), ('rom_89fa', 0x89FA, 1), ('rom_8b3f', 0x8B3F, 1),
    ('rom_95d2', 0x95D2, 2), ('rom_8775', 0x8775, 1), ('rom_840f', 0x840F, 1),
    ('rom_9020', 0x9020, 2), ('rom_9022', 0x9022, 2), ('rom_16338', 0x16338, 2),
    ('rom_15f69', 0x15F69, 1), ('rom_15f55', 0x15F55, 1),
    ('rom_15f9a', 0x15F9A, 2), ('rom_15f9c', 0x15F9C, 2))
BLOBS = (
    ('producer_a', 0x1050E, 256), ('producer_b', 0x1070E, 256),
    ('consumer_a', 0x17CC8, 256), ('consumer_b', 0x17EC8, 256),
    ('producer_axis_x', 0x131E2, 16), ('producer_axis_y', 0x15F20, 16),
    ('consumer_axis_x', 0x18746, 16), ('consumer_axis_y', 0x19340, 16),
    ('weight_axis', 0x14C7A, 16), ('weight_curve', 0x1488A, 17))
WIDTHS = {name: width * 8 for name, at, width in (*RAM_FIELDS, *ROM_FIELDS)}
ARRAYS = {name: (count, 16) for name, at, count in BLOBS}
ARRAYS.update(producer_context=(20, 32), consumer_context=(20, 32))


def initial_context(phase):
    return [*((0x18765430 + i * 0x01030507 + phase * 0x2030405) & 0xFFFFFFFF for i in range(15)),
        0x12344321 + phase, 0x13579BDF + phase, 0x2468ACE0 + phase, 0, 0xB6C70000 + phase]


DEFAULTS = {name: 0 for name in WIDTHS}
DEFAULTS.update({name: 0xA55A for name, at, width in RAM_FIELDS if name.startswith('prior_')})
DEFAULTS.update(word_10d2=0x5000, word_1210=0x5000, word_1248=0x5000,
    word_1a78=0x5000, word_10b2=100, rom_89fb=0x20, rom_89fa=0x40, rom_8b3f=0x18,
    producer_a=[0] * 256, producer_b=[0] * 256,
    consumer_a=[0] * 256, consumer_b=[65535] * 256, weight_curve=[32768] * 17,
    producer_context=initial_context(0), consumer_context=initial_context(1))
DEFAULTS.update({name: [4096 * index for index in range(16)]
    for name in ('producer_axis_x', 'producer_axis_y', 'consumer_axis_x', 'consumer_axis_y', 'weight_axis')})


def require_case(case):
    if (type(case) is not dict or set(case) != {*WIDTHS, *ARRAYS, 'index', 'kind'}
            or type(case['index']) is not int or case['index'] < 0 or type(case['kind']) is not str
            or any(type(case[name]) is not int or not 0 <= case[name] < (1 << bits)
                for name, bits in WIDTHS.items())):
        raise ValueError('the shared-weight input changes its complete raw scalar shape or width')
    for name, (count, bits) in ARRAYS.items():
        values = case[name]
        if type(values) is not list or len(values) != count or any(type(v) is not int or not 0 <= v < (1 << bits) for v in values):
            raise ValueError('the shared-weight input changes a complete raw blob or independent CPU context')
    if any(case[name][18] & ~0x3F1 for name in ('producer_context', 'consumer_context')):
        raise ValueError('the shared-weight context changes the admitted complete I/M/Q/T input')


def cases(source, image):
    rows = []
    def add(kind, **updates):
        case = deepcopy(DEFAULTS)
        case.update(updates)
        case.update(index=len(rows), kind=kind)
        rows.append(case)
    add('complete-two-phase-default')
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
    for index in range(16):
        for raw in (0, 32768):
            curve = list(DEFAULTS['weight_curve'])
            curve[index] = raw
            add('exact-weight-word-causal-alternative', weight_curve=curve, word_1a78=index * 4096)
    for raw in (0, 1, 32767, 32768, 65534, 65535):
        curve = list(DEFAULTS['weight_curve'])
        curve[16] = raw
        add('physical-neighbor-at-zero-weight', weight_curve=curve, word_1a78=65535)
        add('whole-constant-weight', weight_curve=[raw] * 17)
    for field in ('word_10d2', 'word_1210', 'word_1248', 'word_1a78'):
        for raw in (0, 1, 4095, 4096, 4097, 32767, 32768, 32769, 61439, 61440, 61441, 65535):
            add('raw-coordinate-and-clamp-boundaries', **{field: raw,
                'producer_a': [257 * i for i in range(256)],
                'producer_b': [65535 - 257 * i for i in range(256)],
                'consumer_a': [65535 - 257 * i for i in range(256)],
                'consumer_b': [257 * i for i in range(256)],
                'weight_curve': [4095 * i for i in range(17)]})
    for phase in ('producer', 'consumer'):
        x_field = 'word_1210' if phase == 'producer' else 'word_1248'
        for name in (phase + '_a', phase + '_b'):
            for index in range(256):
                table = [0] * 256
                table[index] = 65535
                add('complete-surface-cell-input', **{name: table,
                    x_field: (index // 16) * 4096, 'word_10d2': (index % 16) * 4096})
        for x in (1, 2048, 4095, 4096, 32767, 32768, 61439, 61440):
            for y in (1, 2048, 4095, 4096, 32767, 32768, 61439, 61440):
                add('two-axis-directed-interpolation', **{x_field: x, 'word_10d2': y,
                    phase + '_a': [257 * i for i in range(256)],
                    phase + '_b': [65535 - 257 * i for i in range(256)]})
    for name in ('producer_axis_x', 'producer_axis_y', 'consumer_axis_x', 'consumer_axis_y', 'weight_axis'):
        for index in range(16):
            for raw in (0, 1, 32767, 32768, 65535):
                axis = list(DEFAULTS[name])
                axis[index] = raw
                add('complete-raw-word-axis', **{name: axis})
        wide = [0] * 15 + [65535]
        add('unsigned-axis-numerator-bit31', **{name: wide, 'word_10d2': 32768,
            'word_1210': 32768, 'word_1248': 32768, 'word_1a78': 32768})
    active = dict(rom_89fb=0x68, rom_95d2=65535, rom_16338=65535,
        rom_8775=255, rom_15f69=255, rom_9020=65535, rom_15f9a=65535,
        byte_4180=8, byte_4205=4, byte_4214=4,
        consumer_a=[1000] * 256, consumer_b=[3000] * 256)
    for raw in range(256):
        for name in ('rom_89fb', 'rom_89fa', 'rom_8b3f', 'rom_8775', 'rom_840f', 'rom_15f69', 'rom_15f55'):
            updates = dict(active)
            updates[name] = raw
            add('complete-real-ROM-control-byte', **updates)
        for name, at, width in RAM_FIELDS:
            if width == 1:
                updates = dict(active)
                updates[name] = raw
                add('complete-real-RAM-flag-byte', **updates)
    for name, at, width in RAM_FIELDS:
        if width == 2:
            for raw in (0, 1, 99, 100, 101, 32767, 32768, 65534, 65535):
                updates = dict(active)
                updates[name] = raw
                add('complete-raw-word-and-publication-poison', **updates)
    for name in ('rom_95d2', 'rom_16338', 'rom_9020', 'rom_15f9a'):
        for threshold in (0, 1, 32767, 32768, 65535):
            for raw in (0, 1, 32767, 32768, 65535):
                updates = dict(active)
                updates.update({name: threshold, 'word_10d2': raw, 'byte_4205': 0, 'byte_4214': 0})
                add('actual-sign-extended-unsigned-threshold', **updates)
    for a in (0, 1, 4, 0xFF):
        for b in (0, 1, 4, 0xFF):
            updates = dict(active)
            updates.update(byte_4205=a, byte_4214=b, byte_4180=0)
            add('complete-shared-latch-reconciliation', **updates)
    for low, high in ((0, 1), (1, 0), (0, 0), (65534, 65535), (65535, 65534)):
        for raw in (0, 999, 1000, 2000, 2001, 65535):
            for threshold in (0, raw, min(65535, raw + 1)):
                updates = dict(active)
                updates.update(rom_89fb=0x28, word_124e=low, word_1250=high, word_1286=low,
                    word_1288=high, word_1210=raw, word_1248=raw, rom_9022=threshold,
                    rom_15f9c=threshold, producer_a=[1000] * 256, producer_b=[3000] * 256)
                add('actual-latch-comparison-and-final-selector', **updates)
    return tuple(rows)


def context(source, case, phase):
    require_case(case)
    if type(phase) is not int or phase not in (0, 1):
        raise ValueError('the shared-weight input changes its fixed phase identity')
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
        raise ValueError('the shared-weight phase changes complete immutable raw input or calibration')
    if phase == 0:
        if previous is not None or observed['memory_before'] != (memory(case),):
            raise ValueError('the shared-weight producer changes its complete initial RAM')
    elif (previous is None or previous['phase'] != 0 or previous['pair'] != observed['pair']
            or previous['memory_after'] != observed['memory_before']
            or not test_contract.exact(previous['calibration_after'], observed['calibration_before'])
            or previous['bound_after'] != observed['bound_before']):
        raise ValueError('the shared-weight consumer resets or substitutes actual producer RAM or code/calibration')


def header(declared, image):
    source = declared['source']
    cal, bound = contract.CONTROLLED_CALIBRATION, contract.BOUND_SPANS
    lines = ['/* Raw paired inputs only; no coefficient, blend or expected output. */',
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
