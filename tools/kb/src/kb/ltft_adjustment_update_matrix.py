"""Complete raw native index1 trim inputs and held-other word alternatives."""
from copy import deepcopy
from kb import test_contract
from kb import ltft_adjustment_update_contract as contract

RAM_BASE = 0x01000000
RAM_SIZE = 65536
RAM_FIELDS = (
    ('word_564a', 0x564A, 2), ('word_2304', 0x2304, 2), ('byte_22e1', 0x22E1, 1),
    ('byte_230e', 0x230E, 1), ('byte_4498', 0x4498, 1), ('byte_3e30', 0x3E30, 1),
    ('word_1308', 0x1308, 2), ('word_2308', 0x2308, 2), ('byte_3ea4', 0x3EA4, 1),
    ('byte_2461', 0x2461, 1), ('byte_3082', 0x3082, 1), ('word_29e4', 0x29E4, 2),
    ('record_129', 0x5A94, 1), ('byte_41b5', 0x41B5, 1), ('byte_12fe', 0x12FE, 1),
    ('neighbor_2302', 0x2302, 2), ('neighbor_2306', 0x2306, 2),
    ('neighbor_5648', 0x5648, 2), ('neighbor_564c', 0x564C, 2))
WIDTHS = {name: width * 8 for name, address, width in RAM_FIELDS}
WIDTHS.update({row['name']: row['size'] * 8 for row in contract.DECLARED['control_blobs']})
WORD_VALUES = (0, 1, 2, 7, 15, 16, 127, 128, 255, 256, 652, 653, 7199, 7200, 7201, 7499, 7500,
               7501, 21759, 21760, 21761, 23039, 23040, 23041, 25599, 25600, 25601,
               28159, 28160, 28161, 32767, 32768, 33023, 33024, 33025, 65279, 65280, 65534, 65535)
DEFAULTS = dict(word_564a=30000, word_2304=25600, byte_22e1=2, byte_230e=2, byte_4498=0, byte_3e30=2,
                word_1308=25600, word_2308=25600, byte_3ea4=0, byte_2461=8, byte_3082=2, word_29e4=7500,
                record_129=0, byte_41b5=0, byte_12fe=0xA5, neighbor_2302=0x1234, neighbor_2306=0x5678,
                neighbor_5648=0xBEEF, neighbor_564c=0xCAFE, rom_878b=7, rom_878c=16, rom_878f=110,
                rom_8790=90, rom_86be=129, rom_86bf=85, rom_8fa6=7500, rom_8fa8=7200, pattern=0xA5,
                context=[0x18765430, 0x19795937, 0x1A7C5E3E, 0x1B7F6345, 0xAB123401,
                         0x1D856D53, 0x1E88725A, 0x1F8B7761, 0x208E7C68, 0x2191816F,
                         0x22948676, 0x23978B7D, 0x249A9084, 0x259D958B, 0x26A09A92,
                         0x12345721, 0x13579BDF, 0x2468ACE0, 0, 0xB6C70000])


def require_case(case):
    if (type(case) is not dict or set(case) != {*WIDTHS, 'context', 'pattern', 'index', 'kind'}
            or type(case['index']) is not int or case['index'] < 0 or type(case['kind']) is not str
            or type(case['pattern']) is not int or not 0 <= case['pattern'] <= 255
            or any(type(case[name]) is not int or not 0 <= case[name] < 1 << bits for name, bits in WIDTHS.items())):
        raise ValueError('the trim updater changes a complete typed raw scalar input')
    if (type(case['context']) is not list or len(case['context']) != 20
            or any(type(value) is not int or not 0 <= value <= 0xFFFFFFFF for value in case['context'])
            or case['context'][4] & 255 != 1 or case['context'][18] & ~0x3F1):
        raise ValueError('the trim updater changes native index1 or complete incoming CPU/I/M/Q/T')


def cases(source, image):
    rows = []

    def add(kind, **changes):
        value = deepcopy(DEFAULTS)
        value.update(changes)
        value.update(index=len(rows), kind=kind)
        rows.append(value)

    add('complete-natural-native-index1-updater')
    for name, values in (('word_2304', (0, 65535)), ('word_2308', (0, 32768)), ('word_564a', (25000, 30000))):
        for raw in values:
            add('held-other-exact-physical-word-and-actual-output', **{name: raw})
    for register in range(20):
        values = (0, 1, 0x7FFF, 0x8000, 0xFFFF, 0x10000, 0x80000000, 0xFFFFFFFF)
        if register == 4:
            values = (1, 0x101, 0xFFFF01, 0x7FFFFF01, 0x80000001, 0xFFFFFF01)
        elif register == 18:
            values = (0, 1, 0xF0, 0x100, 0x200, 0x301, 0x3F1)
        for raw in values:
            incoming = list(DEFAULTS['context']); incoming[register] = raw
            add('independent-complete-context-field', context=incoming)
    for qm in (0, 0x100, 0x200, 0x300):
        for interrupt in range(0, 256, 16):
            for t in (0, 1):
                incoming = list(DEFAULTS['context']); incoming[18] = qm | interrupt | t
                add('complete-QM-interrupt-T-context', context=incoming)
    for name, address, width in RAM_FIELDS:
        active = {}
        if name == 'byte_3ea4':
            active['byte_3e30'] = 0
        elif name == 'byte_2461':
            active.update(byte_3e30=0, byte_3ea4=2)
        elif name == 'byte_3082':
            active['byte_22e1'] = 0
        elif name == 'word_29e4':
            active.update(byte_22e1=0, byte_3082=2, byte_3e30=2)
        for raw in (range(256) if width == 1 else WORD_VALUES):
            add('independent-actual-RAM-word-or-byte', **{**active, name: raw})
    for row in contract.DECLARED['control_blobs']:
        active = {}
        if row['name'] in ('rom_878c', 'rom_8fa6', 'rom_8fa8'):
            active.update(byte_22e1=0, byte_3082=2, byte_3e30=2, word_29e4=0)
        if row['name'] == 'rom_8fa6':
            active.update(rom_8fa8=0, word_29e4=65535)
        for raw in (range(256) if row['size'] == 1 else WORD_VALUES):
            add('independent-actual-raw-ROM-control', **{**active, row['name']: raw})
    for first in (0, 2):
        for second in (0, 2):
            for timer in (0, 1, 255):
                for status in (0, 2):
                    add('complete-permission-timer-and-active-status-precedence', byte_22e1=first,
                        byte_230e=second, byte_4498=timer, byte_3e30=status)
    for error in (0, 1, 23039, 23040, 23041, 25599, 25600, 25601, 28159, 28160, 28161, 32767, 32768, 65535):
        for old in (0, 1, 652, 21759, 21760, 25599, 25600, 25601, 33024, 65534, 65535):
            for factor in (0, 7, 255):
                add('actual-error-equality-word-wrap-and-neutral-crossing', word_1308=error,
                    word_2308=25600, word_564a=old, rom_878b=factor)
    for old in (25593, 25607):
        for active in (0, 2):
            add('exact-neutral-crossing-equality-with-real-step7', word_564a=old, byte_3e30=active,
                word_2304=25600, rom_878b=7)
    for diagnostic in (0, 1, 25599, 25600, 25601, 65535):
        for factor in (0, 1, 99, 100, 101, 254, 255):
            add('actual-positive-fixed-divisor-short-and-long-quotient', word_2304=diagnostic, rom_878b=factor)
    for upper, lower in ((0, 0), (0, 255), (255, 0), (100, 100), (110, 90), (90, 110), (255, 255)):
        for error in (0, 23040, 25600, 28160, 65535):
            add('independent-unordered-error-controls', rom_878f=upper, rom_8790=lower, word_1308=error)
    for upper, lower in ((0, 0), (0, 255), (255, 0), (100, 100), (129, 85), (85, 129), (255, 255)):
        for old in (0, 25599, 25600, 25601, 65535):
            for neutral in (0, 128):
                add('ordered-raw-adjustment-bounds-and-later-neutralization', rom_86be=upper,
                    rom_86bf=lower, word_564a=old, record_129=neutral)
    for old in (0, 1, 25599, 25600, 25601, 65535):
        for status in (0, 2):
            for permit in (0, 8):
                add('quiet-hold-or-real-return-to-neutral', byte_3e30=0, byte_3ea4=status,
                    byte_2461=permit, word_564a=old)
    for sample in (0, 7199, 7200, 7201, 7499, 7500, 7501, 65535):
        for old in (0, 1, 21760, 25600, 65280, 65535):
            for step in (0, 1, 16, 255):
                add('real-disabled-temperature-step-and-lowword-wrap', byte_22e1=0,
                    word_29e4=sample, word_564a=old, rom_878c=step)
    for upper, lower in ((0, 65535), (65535, 0), (7200, 7500), (7500, 7200), (7500, 7500)):
        for sample in (0, 7200, 7500, 65535):
            add('independent-temperature-threshold-order-and-equality', byte_22e1=0,
                rom_8fa8=upper, rom_8fa6=lower, word_29e4=sample)
    for record in (0, 127, 128, 255):
        for control in (0, 1, 254, 255):
            add('actual-record-bit7-and-control-bit0-short-circuit', record_129=record, byte_41b5=control)
    for pattern in (0, 1, 0x5A, 0x80, 0xFF):
        add('complete-other-RAM-and-sibling-preservation', pattern=pattern)
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
    return {row['address']: case[row['name']].to_bytes(row['size'], 'big')
            for row in contract.DECLARED['control_blobs']}


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
        raise ValueError('the trim updater changes complete immutable inputs or physical ROM controls')


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
    lines = ['/* Complete raw inputs for the natural native index1 learned-trim adjustment updater. */',
             f'#define TRIM_CALIBRATION_SIZE {sum(row["size"] for row in calibration)}U',
             f'#define TRIM_BOUND_SIZE {sum(row["size"] for row in bound)}U',
             'static const struct span trim_calibration[] = {' + ','.join(
                 '{%dU,%dU}' % (row['address'], row['size']) for row in calibration) + '};',
             'static const struct span trim_bound[] = {' + ','.join(
                 '{%dU,%dU}' % (row['address'], row['size']) for row in bound) + '};',
             'static const struct span trim_ram_fields[] = {' + ','.join(
                 '{%dU,%dU}' % (address, width) for name, address, width in RAM_FIELDS) + '};',
             'static const uint8_t trim_calibration_blobs[][TRIM_CALIBRATION_SIZE] = {']
    lines.extend('{' + ','.join(f'0x{value:02x}U' for value in blob) + '},' for blob in blobs)
    lines.extend(('};', f'struct path_case {{ uint32_t ram[{len(RAM_FIELDS)}];struct context context;'
                  'uint8_t pattern;uint32_t calibration_index; };',
                  'static const struct path_case trim_cases[] = {', *rows, '};', ''))
    return '\n'.join(lines).encode()
