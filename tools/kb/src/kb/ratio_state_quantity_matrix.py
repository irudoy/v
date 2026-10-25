"""Raw primary-ratio inputs and complete signed state-filter phase continuity."""
from copy import deepcopy
from kb import test_contract
from kb import ratio_state_quantity_contract as contract

RAM_BASE = 0x01000000
RAM_SIZE = 65536
RAM_FIELDS = (
    ('word_1702', 0x1702, 2), ('word_10d6', 0x10D6, 2), ('word_1582', 0x1582, 2),
    ('word_1770', 0x1770, 2), ('word_18d2', 0x18D2, 2), ('word_1152', 0x1152, 2),
    ('long_1540', 0x1540, 4), ('long_14f8', 0x14F8, 4), ('word_177c', 0x177C, 2),
    ('prior_17e2', 0x17E2, 2), ('prior_16b2', 0x16B2, 2), ('prior_19a2', 0x19A2, 2),
    ('prior_145a', 0x145A, 2), ('prior_1792', 0x1792, 2), ('prior_14f4', 0x14F4, 2),
    ('prior_14f6', 0x14F6, 2), ('prior_1508', 0x1508, 2), ('prior_177e', 0x177E, 2),
    ('prior_9818', 0x9818, 4))
ROM_FIELDS = (('rom_920e', 0x920E, 2), ('rom_944e', 0x944E, 2),
    ('rom_95a0', 0x95A0, 2), ('rom_918e', 0x918E, 2),
    ('rom_928c', 0x928C, 2), ('rom_928e', 0x928E, 2))
BLOBS = (('ratio_curve', 0x15770, 16), ('centered_curve_axis', 0x15276, 16))
WIDTHS = {name: width * 8 for name, at, width in (*RAM_FIELDS, *ROM_FIELDS)}
ARRAYS = {name: (count, 16) for name, at, count in BLOBS}
ARRAYS.update(producer_context=(20, 32), consumer_context=(20, 32))


def initial_context(phase):
    return [*((0x18765430 + index * 0x01030507 + phase * 0x2030405) & 0xFFFFFFFF for index in range(15)),
        0x12344321 + phase, 0x13579BDF + phase, 0x2468ACE0 + phase, 0, 0xB6C70000 + phase]


DEFAULTS = {name: 0 for name in WIDTHS}
DEFAULTS.update({name: 0xA55AA55A if width == 4 else 0xA55A
    for name, at, width in RAM_FIELDS if name.startswith('prior_')})
DEFAULTS.update(word_1702=64, word_10d6=200, word_1582=200, word_1770=64, word_18d2=1,
    long_14f8=0x80000000, rom_944e=1, rom_928c=65535,
    ratio_curve=[1024] * 16, centered_curve_axis=[32768] * 8 + [8192 * i for i in range(8)],
    producer_context=initial_context(0), consumer_context=initial_context(1))


def require_case(case):
    if (type(case) is not dict or set(case) != {*WIDTHS, *ARRAYS, 'index', 'kind'}
            or type(case['index']) is not int or case['index'] < 0 or type(case['kind']) is not str
            or any(type(case[name]) is not int or not 0 <= case[name] < (1 << bits) for name, bits in WIDTHS.items())):
        raise ValueError('the ratio-state input changes its complete raw scalar shape or width')
    for name, (count, bits) in ARRAYS.items():
        values = case[name]
        if type(values) is not list or len(values) != count or any(type(v) is not int or not 0 <= v < (1 << bits) for v in values):
            raise ValueError('the ratio-state input changes a complete physical word blob or CPU context')
    if any(case[name][18] & ~0x3F1 for name in ('producer_context', 'consumer_context')):
        raise ValueError('the ratio-state context changes its admitted complete I/M/Q/T input')


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
    for index in range(16):
        for raw in (0, 1024):
            curve = [0] * 16
            curve[index] = raw
            add('ratio-word-held-other-causal-alternative', ratio_curve=curve,
                rom_920e=(32768 * index + 14) // 15)
    for gain in (0, 1, 2184, 2185, 32767, 32768, 32769, 65534, 65535):
        for curve in ([4095 * i for i in range(16)], [65535 - 4095 * i for i in range(16)], [65535] * 16):
            add('actual-ratio-curve-directed-and-signed-endpoint', ratio_curve=curve, rom_920e=gain)
    for source in (0, 1, 2, 7, 8, 20970, 20971, 20972, 32767, 32768, 65535):
        for first, second in ((0, 65535), (65535, 0), (1, 4), (4, 1), (32768, 65535), (65535, 65535)):
            add('unsigned-primary-numerator-and-wide-positive-divisor', word_1702=source,
                word_10d6=first, word_1582=second, rom_920e=65535)
    for raw in (0, 1, 63, 64, 65, 32767, 32768, 65534, 65535):
        for other in (0, 1, 64, 32767, 32768, 65535):
            add('actual-product-bit31-signed-shift-and-unsigned-cap', ratio_curve=[raw] * 16, word_1770=other)
    for divisor in (0, 1, 2, 255, 256, 32767, 32768, 65535):
        for factor in (0, 1, 32767, 32768, 32769, 65535):
            add('actual-signed-division-clamps-and-zero-error-write', ratio_curve=[65535] * 16,
                word_1770=65535, word_18d2=factor, rom_944e=divisor)
    for index in range(8):
        for coordinate in (max(0, index * 8192 - 1), index * 8192, min(65535, index * 8192 + 1)):
            for curve in ([8191 * i for i in range(8)], [65535 - 8191 * i for i in range(8)], [32768] * 8):
                add('actual-centered-directed-word-interpolation', centered_curve_axis=curve + [8192 * i for i in range(8)],
                    word_1152=coordinate)
        for raw in (0, 1, 32767, 32768, 65535):
            blob = list(DEFAULTS['centered_curve_axis'])
            blob[index] = raw
            add('complete-centered-map-raw-word', centered_curve_axis=blob, word_1152=index * 8192)
            blob = list(DEFAULTS['centered_curve_axis'])
            blob[index + 8] = raw
            add('complete-raw-axis-including-shared-guard-word', centered_curve_axis=blob, word_1152=65535)
    add('unsigned-centered-axis-numerator-bit31', centered_curve_axis=[32768] * 8 + [0] * 7 + [65535], word_1152=32768)
    add('complete-centered-search-below-first-knot', centered_curve_axis=[32768] * 8 + [1000 + 8192 * i for i in range(8)], word_1152=0)
    for field, at, width in RAM_FIELDS:
        values = ((0, 1, 255, 256, 257, 32766, 32767, 32768, 32769, 65534, 65535) if width == 2
            else (0, 1, 255, 256, 65535, 65536, 0x7FFFFFFF, 0x80000000, 0xFFFF0000, 0xFFFFFFFF))
        for raw in values:
            add('complete-raw-RAM-boundary-and-output-poison', **{field: raw})
    for field, at, width in ROM_FIELDS:
        for raw in (0, 1, 255, 256, 32767, 32768, 65534, 65535):
            add('complete-independent-ROM-word-boundary', **{field: raw})
    for previous in (0, 1, 0x7FFFFFFF, 0x80000000, 0xFFFF0000, 0xFFFFFFFF):
        for coordinate in (0, 1, 32767, 32768, 65535):
            for gain in (0, 1, 32768, 65535):
                add('first-accumulator-modulo-sign-delta-clamps-and-stuck-progress',
                    long_1540=previous, word_1152=coordinate, rom_95a0=gain)
        for gain in (0, 1, 32768, 65535):
            for feedback in (0, 1, 1000, 65535):
                add('second-accumulator-centered-feedback-and-zero-gain-progress',
                    long_14f8=previous, rom_918e=gain, rom_928e=feedback)
    for old in (0, 1, 32767, 32768, 65535):
        for curve in (0, 32767, 32768, 65535):
            for gain in (0, 1, 32768, 65535):
                add('actual-signed-final-lag-wrap-stuck-and-zero-floor', word_177c=old,
                    centered_curve_axis=[curve] * 8 + [8192 * i for i in range(8)], rom_928c=gain)
    for raw in (0, 1, 32767, 32768, 65535):
        add('zero-first-divisor-preserves-actual-error-continuity', rom_944e=0, prior_9818=raw,
            consumer_context=initial_context(1))
    return tuple(rows)


def context(source, case, phase):
    require_case(case)
    if type(phase) is not int or phase not in (0, 1):
        raise ValueError('the ratio-state input changes its fixed phase identity')
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
        raise ValueError('the ratio-state phase changes complete immutable raw input or calibration')
    if phase == 0:
        if previous is not None or observed['memory_before'] != (memory(case),):
            raise ValueError('the ratio-state producer changes its complete initial RAM')
    elif (previous is None or previous['phase'] != 0 or previous['pair'] != observed['pair']
            or previous['memory_after'] != observed['memory_before']
            or not test_contract.exact(previous['calibration_after'], observed['calibration_before'])
            or previous['bound_after'] != observed['bound_before']):
        raise ValueError('the ratio-state consumer resets or substitutes actual producer RAM or code/calibration')


def header(declared, image):
    source = declared['source']
    cal, bound = contract.CONTROLLED_CALIBRATION, contract.BOUND_SPANS
    lines = ['/* Raw paired inputs only; no primary ratio, filter state or expected output. */',
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
