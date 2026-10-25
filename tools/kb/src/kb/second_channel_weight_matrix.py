"""Raw word curves, surface, axes and complete input state for the second-channel entry."""
from copy import deepcopy
from kb import test_contract
from kb import second_channel_weight_contract as contract

RAM_BASE = 0x01000000
RAM_SIZE = 65536
RAM_FIELDS = (
    ('byte_249f', 0x249F, 1), ('word_2698', 0x2698, 2),
    ('byte_2c71', 0x2C71, 1), ('word_10bc', 0x10BC, 2),
    ('byte_245e', 0x245E, 1), ('word_31e2', 0x31E2, 2),
    ('word_3024', 0x3024, 2), ('byte_4214', 0x4214, 1), ('word_35ea', 0x35EA, 2),
    ('prior_35f4', 0x35F4, 2), ('prior_35ca', 0x35CA, 2),
    ('prior_35fc', 0x35FC, 2), ('prior_35cc', 0x35CC, 2),
    ('prior_1248', 0x1248, 2), ('prior_9818', 0x9818, 4))
WIDTHS = {name:width*8 for name, at, width in RAM_FIELDS}
WIDTHS.update({row['name']:row['size']*8 for row in contract.DECLARED['control_blobs']})
WIDTHS['pattern'] = 8
ARRAYS = {'context':(20,32), 'ordinary_curves':(49,16), 'alternate_curves':(33,16),
          'curve_axis':(16,16), 'weight_surface':(64,16), 'weight_axes':(16,16)}
BYTE_VALUES = (0,1,2,31,32,33,63,64,65,127,128,129,254,255)
WORD_VALUES = (0,1,2,255,256,257,799,800,801,1024,4095,4096,4097,
               8191,8192,8193,16383,16384,32767,32768,32769,61440,65534,65535)
LONG_VALUES = (0,1,65535,65536,0x7FFFFFFF,0x80000000,0xFFFFFFFF)
DEFAULT_CONTEXT = [*((0x18765430+i*0x01030507)&0xFFFFFFFF for i in range(15)),
                   0x12344321,0x13579BDF,0x2468ACE0,0,0xB6C70000]
DEFAULTS = {name:0 for name in WIDTHS}
DEFAULTS.update(context=DEFAULT_CONTEXT,
    ordinary_curves=[0]*16+[32768]*32+[0], alternate_curves=[0]*16+[32768]*16+[0],
    curve_axis=[i*4096 for i in range(16)], weight_surface=[0]*64,
    weight_axes=[i*8192 for i in range(8)]*2,
    pattern=0xA5, word_31e2=32768, word_3024=65535, rom_1630c=32768,
    prior_35f4=0xA5B6, prior_35ca=0xB6C7, prior_35fc=0xC7D8,
    prior_35cc=0xD8E9, prior_1248=0xE9FA, prior_9818=0xDEADBEEF)


def require_case(case):
    if (type(case) is not dict or set(case) != {*WIDTHS,*ARRAYS,'index','kind'}
            or type(case['index']) is not int or case['index'] < 0
            or type(case['kind']) is not str
            or any(type(case[name]) is not int or not 0 <= case[name] < (1 << bits)
                   for name,bits in WIDTHS.items())):
        raise ValueError('the second-channel input changes a raw scalar or supplies a live result')
    for name,(count,bits) in ARRAYS.items():
        values = case[name]
        if (type(values) is not list or len(values) != count
                or any(type(v) is not int or not 0 <= v < (1 << bits) for v in values)):
            raise ValueError('the second-channel input truncates a complete CPU, physical curve, surface or axis')
    if case['context'][18] & ~0x3F1:
        raise ValueError('the second-channel input changes admitted I/M/Q/T controls')


def cases(source, image):
    rows = []

    def add(kind, **changes):
        value = deepcopy(DEFAULTS)
        value.update(changes)
        value.update(index=len(rows), kind=kind)
        rows.append(value)

    add('complete-weight-publication-and-output-entry')
    stock = {row['name']:int.from_bytes(image[row['address']:row['address']+row['size']], 'big')
             for row in source['control_blobs']}
    for row in source['input_blobs']:
        at, size = row['address'], row['size']
        stock[row['name']] = [int.from_bytes(image[i:i+2], 'big') for i in range(at,at+size,2)]
    add('complete-owned-stock-calibration', **stock)
    for register in range(20):
        values = LONG_VALUES if register != 18 else (0,1,0xF0,0x100,0x200,0x301,0x3F1)
        for raw in values:
            context = list(DEFAULT_CONTEXT)
            context[register] = raw
            add('independent-complete-CPU-context-field', context=context)
    for qm in (0,0x100,0x200,0x300):
        for interrupt in range(0,256,16):
            for t in (0,1):
                context = list(DEFAULT_CONTEXT)
                context[18] = qm | interrupt | t
                add('complete-QM-interrupt-T-context', context=context)
    for field, at, width in RAM_FIELDS:
        for raw in BYTE_VALUES if width == 1 else WORD_VALUES if width == 2 else LONG_VALUES:
            add('independent-raw-RAM-input-and-prior-publication', **{field:raw})
    for index in range(64):
        for raw in (0,1,1024,32767,32768,32769,65535):
            surface = [0]*64
            surface[index] = raw
            add('held-other-physical-weight-cell-and-actual-output', weight_surface=surface,
                word_10bc=(index//8)*8192, byte_2c71=(index%8)*32)
    for raw in WORD_VALUES:
        add('held-other-raw-substitute-weight-and-actual-output', rom_83c1=128, rom_1630c=raw)
    for name, count, alternate in (('ordinary_curves',49,False), ('alternate_curves',33,True)):
        for index in range(count):
            for raw in (0,1,32767,32768,65535):
                curve = list(DEFAULTS[name])
                curve[index] = raw
                add('independent-physical-curve-word-and-overlapping-neighbor',
                    **{name:curve, 'byte_249f':2 if alternate else 0,
                       'word_2698':min(index%16,15)*4096, 'rom_83c1':128})
    for guard in WORD_VALUES:
        ordinary = list(DEFAULTS['ordinary_curves'])
        ordinary[48] = guard
        add('last-common-curve-zero-weight-physical-guard', ordinary_curves=ordinary,
            word_2698=61440)
        alternate = list(DEFAULTS['alternate_curves'])
        alternate[32] = guard
        add('last-alternate-curve-zero-weight-physical-guard', alternate_curves=alternate,
            byte_249f=2, word_2698=61440)
    patterns = ([i*8192 for i in range(8)], [0]*8, [65535]*8,
        [65535-i*8192 for i in range(8)], [0,65535,0,32768,32767,1,65534,65535],
        [0,1,1,128,128,32768,65535,65535])
    for offset in (0,8):
        for pattern in patterns:
            axes = list(DEFAULTS['weight_axes'])
            axes[offset:offset+8] = pattern
            coordinates = range(256) if offset == 0 else sorted({*WORD_VALUES,
                *(v for knot in pattern for v in (max(0,knot-1),knot,min(65535,knot+1)))})
            for coordinate in coordinates:
                for descending in (False,True):
                    add('rightmost-weight-axis-without-monotonicity-premise', weight_axes=axes,
                        weight_surface=[65535-i*1000 if descending else i*1000 for i in range(64)],
                        **{'byte_2c71':coordinate} if offset == 0 else {'word_10bc':coordinate})
        for index in range(8):
            for raw in WORD_VALUES:
                axes = list(DEFAULTS['weight_axes'])
                axes[offset+index] = raw
                add('independent-weight-axis-word', weight_axes=axes,
                    byte_2c71=1, word_10bc=1)
    curve_patterns = ([i*4096 for i in range(16)], [0]*16, [65535]*16,
        [65535-i*4096 for i in range(16)], [0,65535,0,32768,32767,1,65534,65535]*2,
        [0,1,1,128,128,32768,65535,65535]*2)
    for axis in curve_patterns:
        coordinates = sorted({*WORD_VALUES,
            *(v for knot in axis for v in (max(0,knot-1),knot,min(65535,knot+1)))})
        for coordinate in coordinates:
            for alternate in (0,2):
                add('rightmost-sixteen-word-curve-and-directed-interpolation', curve_axis=list(axis),
                    ordinary_curves=[(i*1231)&65535 for i in range(49)],
                    alternate_curves=[65535-i*1777 for i in range(33)],
                    word_2698=coordinate, byte_249f=alternate)
    for outer, inner in ((0,0),(1,0),(0,1),(1,1),(8191,31),(8192,32),(8193,33),(65535,255)):
        for descending in (False,True):
            add('four-actual-bilinear-fraction-paths', word_10bc=outer, byte_2c71=inner,
                weight_surface=[65535-i*1000 if descending else i*1000 for i in range(64)])
    for first, second in ((0,0),(0,32768),(65535,65535),(65535,0),(32768,65535),(65535,32768)):
        for weight in (0,1,16384,32767,32768,32769,65534,65535):
            for common in (0,32768,65535):
                for multiply in (0,64):
                    add('guarded-wrapped-products-wide-R14-and-unsigned-cap', rom_83c1=128,
                        rom_1630c=weight, byte_245e=multiply,
                        ordinary_curves=[first]*16+[second]*16+[common]*16+[0])
    for factor in WORD_VALUES:
        for raw in (0,1,799,800,801,32768,65535):
            add('actual-zero-or-narrow-divider-and-final-output', word_31e2=factor,
                byte_4214=64, word_35ea=raw)
        add('actual-wide-R14-overflow-guard', word_31e2=factor, rom_83c1=128,
            rom_1630c=32768, byte_245e=64, ordinary_curves=[65535]*48+[0])
    for prior in WORD_VALUES:
        add('independent-prior35F4-on-surface-path', prior_35f4=prior)
        add('independent-prior35F4-on-substitute-path', prior_35f4=prior, rom_83c1=128)
    for flag in BYTE_VALUES:
        for field in ('byte_249f','byte_245e','byte_4214','rom_83c1'):
            add('raw-bit-selection-with-unrelated-bits-retained', **{field:flag})
    for pattern in (0,1,0x5A,0x80,0xFF):
        add('complete-unmodified-RAM-pattern', pattern=pattern)
    return tuple(rows)


def context(source, case):
    require_case(case)
    return tuple(case['context'])


def memory(case):
    require_case(case)
    out = bytearray([case['pattern']])*RAM_SIZE
    for name, at, width in RAM_FIELDS:
        out[at:at+width] = case[name].to_bytes(width, 'big')
    return bytes(out)


def input_calibrations(case):
    require_case(case)
    mapping = {row['address']:case[row['name']].to_bytes(row['size'], 'big')
               for row in contract.DECLARED['control_blobs']}
    for row in contract.DECLARED['input_blobs']:
        mapping[row['address']] = b''.join(v.to_bytes(2, 'big') for v in case[row['name']])
    return mapping


def calibrations(source, image, case):
    fixture, _ = contract.fixture_for_case(source, image, case)
    return {row['address']:fixture[row['address']:row['address']+row['size']]
            for row in contract.CONTROLLED_CALIBRATION}


def require_input(source, image, case, observed):
    wanted = calibrations(source, image, case)
    if (observed['entry'] != contract.ENTRY
            or not test_contract.exact(observed['context'], context(source,case))
            or observed['memory_before'] != (memory(case),)
            or not test_contract.exact(observed['calibration_before'], wanted)
            or not test_contract.exact(observed['calibration_after'], wanted)):
        raise ValueError('the second-channel entry changes a complete immutable raw input or calibration')


def header(declared,image):
    source=declared['source'];cal,bound=contract.CONTROLLED_CALIBRATION,contract.BOUND_SPANS
    lines=['/* Complete raw inputs only; no supplied live candidate or expected output. */',
        f'#define WEIGHT_CALIBRATION_SIZE {sum(r["size"] for r in cal)}U',
        f'#define WEIGHT_BOUND_SIZE {sum(r["size"] for r in bound)}U',
        'static const struct span weight_calibration[] = {'+','.join('{%dU,%dU}'%(r['address'],r['size']) for r in cal)+'};',
        'static const struct span weight_bound[] = {'+','.join('{%dU,%dU}'%(r['address'],r['size']) for r in bound)+'};',
        'struct path_case { '+''.join('uint32_t '+name+';' for name,at,width in RAM_FIELDS)+
        'struct context context;uint8_t pattern,calibration[WEIGHT_CALIBRATION_SIZE]; };',
        'static const struct path_case weight_cases[] = {']
    for case in declared['cases']:
        raw=context(source,case)
        ctx='{{'+','.join(f'0x{v:x}U' for v in raw[:15])+'},'+','.join(f'0x{v:x}U' for v in raw[15:])+'}'
        mapping=calibrations(source,image,case);blob=b''.join(mapping[row['address']] for row in cal)
        lines.append('{'+','.join(f'0x{case[name]:x}U' for name,at,width in RAM_FIELDS)+','+ctx+
            f',0x{case["pattern"]:02x}U,'+'{'+','.join(f'0x{v:02x}U' for v in blob)+'}},')
    return '\n'.join((*lines,'};','')).encode()
