"""Complete raw index1 byte-judgement inputs without supplied comparisons or outputs."""
from copy import deepcopy
from kb import test_contract
from kb import rest_position_judgement_contract as contract

RAM_BASE = 0x01000000
RAM_SIZE = 65536
RAM_FIELDS = (('byte_2327', 0x2327, 1), ('byte_43c3', 0x43C3, 1), ('byte_24ab', 0x24AB, 1),
    ('byte_43c2', 0x43C2, 1), ('byte_24aa', 0x24AA, 1), ('byte_2458', 0x2458, 1),
    ('byte_42f7', 0x42F7, 1), ('byte_430b', 0x430B, 1), ('byte_3599', 0x3599, 1),
    ('byte_16bb', 0x16BB, 1), ('byte_43c1', 0x43C1, 1), ('byte_43b7', 0x43B7, 1),
    ('byte_358b', 0x358B, 1), ('byte_3582', 0x3582, 1), ('byte_43b5', 0x43B5, 1), ('byte_43af', 0x43AF, 1))
ROM_FIELDS = (('rom_855d', 0x855D, 1), ('rom_871f', 0x871F, 1),
    ('rom_8951', 0x8951, 1), ('rom_8952', 0x8952, 1), ('rom_8e25', 0x8E25, 1),
    ('rom_8e1c', 0x8E1C, 1), ('rom_8736', 0x8736, 1), ('rom_8737', 0x8737, 1))
WIDTHS = {name: 8 for name, at, width in (*RAM_FIELDS, *ROM_FIELDS)}
DEFAULTS = {name: 0 for name in WIDTHS}
DEFAULTS.update(byte_2327=128, byte_24ab=0x50, byte_24aa=0x58, byte_2458=0x20,
    rom_855d=10, rom_871f=10, rom_8951=34, rom_8952=34, rom_8736=34, rom_8737=34,
    rom_8e25=90, rom_8e1c=90, pattern=0xA5,
    context=[*((0x18765430 + i * 0x01030507) & 0xFFFFFFFF for i in range(15)),
        0x12344321, 0x13579BDF, 0x2468ACE0, 0, 0xB6C70000])
DEFAULTS['context'][4] = 1
DEFAULTS['context'][5] = 1


def require_case(case):
    if (type(case) is not dict or set(case) != {*WIDTHS, 'context', 'pattern', 'index', 'kind'}
            or type(case['index']) is not int or case['index'] < 0 or type(case['kind']) is not str
            or type(case['pattern']) is not int or not 0 <= case['pattern'] <= 255
            or any(type(case[name]) is not int or not 0 <= case[name] <= 255 for name in WIDTHS)):
        raise ValueError('the rest-position input changes its complete raw byte shape or width')
    context = case['context']
    if (type(context) is not list or len(context) != 20
            or any(type(v) is not int or not 0 <= v <= 0xFFFFFFFF for v in context)
            or context[4] != 1 or context[18] & ~0x3F1):
        raise ValueError('the rest-position input changes the full native bank1 word or complete I/M/Q/T context')


def cases(source, image):
    rows = []
    def add(kind, **updates):
        case = deepcopy(DEFAULTS)
        case.update(updates)
        case.update(index=len(rows), kind=kind)
        rows.append(case)
    add('complete-natural-native-bank1-judgement')
    for register in range(20):
        if register == 4:
            continue
        values = ((0, 1, 0x7FFF, 0x8000, 0xFFFF, 0x10000, 0x80000000, 0xFFFFFFFF)
            if register != 18 else (0, 1, 0xF0, 0x100, 0x200, 0x301, 0x3F1))
        for raw in values:
            context = list(DEFAULTS['context'])
            context[register] = raw
            add('complete-independent-other19-context-fields', context=context)
    for qm in (0, 0x100, 0x200, 0x300):
        for interrupt in range(0, 256, 16):
            for t in (0, 1):
                context = list(DEFAULTS['context'])
                context[18] = qm | interrupt | t
                add('complete-QM-interrupt-T-context', context=context)
    for field in WIDTHS:
        for raw in range(256):
            updates = {field: raw}
            if field == 'rom_855d':
                updates['byte_43c3'] = 1
            elif field == 'rom_871f':
                updates['byte_43c2'] = 1
            elif field in ('rom_8e25', 'rom_8e1c'):
                updates['byte_16bb'] = 128
            add('complete-independent-raw-RAM-or-ROM-byte', **updates)
    for pattern in (0, 1, 0x55, 0xA5, 0xFF):
        add('complete-unrelated-RAM-pattern', pattern=pattern)
    for raw in (0, 93, 94, 95, 127, 128, 161, 162, 163, 255):
        for first_high in (0, 1):
            for first_low in (0, 1):
                for second_high in (0, 1):
                    for second_low in (0, 1):
                        add('actual-both-window-equalities-and-four-independent-timer-gates', byte_16bb=raw,
                            byte_43c1=first_high, byte_43b7=first_low, byte_43b5=second_high, byte_43af=second_low)
    for first in (0, 1):
        for second in (0, 1):
            for initial in (0, 2, 0xFD, 0xFF):
                add('independent-counter-zero-and-complete-bitfield-retention', byte_42f7=first,
                    byte_430b=second, byte_3599=initial, byte_358b=initial, byte_3582=initial)
    for raw in (0, 128, 255):
        add('held-other-selected-byte-actual-fault-and-timer-publications', byte_16bb=raw)
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
    return {at: bytes([case[name]]) for name, at, width in ROM_FIELDS}


def calibrations(source, image, case):
    fixture, _ = contract.fixture_for_case(source, image, case)
    return {row['address']: fixture[row['address']:row['address']+row['size']] for row in contract.CONTROLLED_CALIBRATION}

def require_input(source, image, case, observed):
    wanted = calibrations(source, image, case)
    if (observed['entry'] != contract.ENTRY or not test_contract.exact(observed['context'], context(source, case))
            or observed['memory_before'] != (memory(case),)
            or not test_contract.exact(observed['calibration_before'], wanted)
            or not test_contract.exact(observed['calibration_after'], wanted)):
        raise ValueError('the rest-position judgement changes a complete immutable input or controlled calibration')

def header(declared, image):
    source, cal, bound = declared['source'], contract.CONTROLLED_CALIBRATION, contract.BOUND_SPANS
    lines = ['/* Complete raw inputs for the natural byte judgement at native index 1. */',
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

