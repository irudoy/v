"""Complete raw native index1 MAF state and independent scalar/curve alternatives."""
from copy import deepcopy
from kb import test_contract
from kb import maf_accumulator_update_contract as contract

RAM_BASE = 0x01000000
RAM_SIZE = 65536
RAM_FIELDS = (
    ('counter_first', 0x3969, 1), ('counter_second', 0x396B, 1),
    ('phase_first', 0x3977, 1), ('phase_second', 0x3978, 1), ('mean', 0x397A, 1),
    ('sum', 0x3980, 4), ('latched_count', 0x3989, 1), ('call_count', 0x398B, 1),
    ('count_latched', 0x398C, 1), ('latched_word', 0x3990, 2), ('word_latched', 0x3992, 1),
    ('factor', 0x3994, 1), ('mean_curve', 0x3996, 1), ('seeded', 0x3997, 1),
    ('accumulator', 0x399C, 4), ('initialized', 0x39A0, 1), ('scaled', 0x39A1, 1),
    ('threshold_sample', 0x3A1F, 1), ('maf_word', 0x101E, 2), ('throttle', 0x1075, 1),
    ('battery', 0x1188, 1), ('status', 0x421A, 1), ('enabled', 0x439B, 1),
    ('neighbor_accumulator', 0x3998, 4), ('neighbor_sum', 0x397C, 4),
    ('neighbor_maf', 0x101C, 2), ('neighbor_sample', 0x3A1E, 1), ('neighbor_enabled', 0x439A, 1))
WIDTHS = {name: size * 8 for name, address, size in RAM_FIELDS}
WIDTHS.update({row['name']: row['size'] * 8 for row in contract.DECLARED['control_blobs']})
BLOBS = {row['name']: row['size'] for row in contract.DECLARED['input_blobs']}
DEFAULTS = dict(counter_first=0, counter_second=0, phase_first=2, phase_second=0, mean=0,
                sum=0x12345678, latched_count=12, call_count=124, count_latched=0,
                latched_word=25600, word_latched=2, factor=128, mean_curve=0, seeded=2,
                accumulator=0xFEDCBA98, initialized=2, scaled=2, threshold_sample=0,
                maf_word=700, throttle=0, battery=100, status=0, enabled=1,
                neighbor_accumulator=0x89ABCDEF, neighbor_sum=0xA1B2C3D4, neighbor_maf=0x1357,
                neighbor_sample=0x79, neighbor_enabled=0xBD, pattern=0xA5,
                context=[0x18765430,0x19795937,0x1A7C5E3E,0x1B7F6345,0xAB123401,
                         0x1D856D53,0x1E88725A,0x1F8B7761,0x208E7C68,0x2191816F,
                         0x22948676,0x23978B7D,0x249A9084,0x259D958B,0x26A09A92,
                         0x12345721,0x13579BDF,0x2468ACE0,0,0xB6C70000])
DEFAULTS.update({row['name']: int(row['stock_hex'], 16) for row in contract.DECLARED['control_blobs']})
WORD_VALUES = (0,1,127,128,255,256,599,600,601,699,700,701,32767,32768,65534,65535)
LONG_VALUES = (0,1,255,256,999,1000,1001,65535,65536,0x7FFFFFFF,0x80000000,0xFFFFFFFE,0xFFFFFFFF)


def require_case(case):
    if (type(case) is not dict or set(case) != {*WIDTHS,*BLOBS,'context','pattern','index','kind'}
            or type(case['index']) is not int or case['index'] < 0 or type(case['kind']) is not str
            or type(case['pattern']) is not int or not 0 <= case['pattern'] <= 255
            or any(type(case[name]) is not int or not 0 <= case[name] < 1 << bits for name,bits in WIDTHS.items())
            or any(type(case[name]) is not bytes or len(case[name]) != size for name,size in BLOBS.items())):
        raise ValueError('the accumulator changes complete raw scalar or physical curve inputs')
    if (type(case['context']) is not list or len(case['context']) != 20
            or any(type(v) is not int or not 0 <= v <= 0xFFFFFFFF for v in case['context'])
            or case['context'][4] & 255 != 1 or case['context'][18] & ~0x3F1):
        raise ValueError('the accumulator changes native index1 or complete incoming CPU/I/M/Q/T')


def cases(source, image):
    defaults = deepcopy(DEFAULTS)
    defaults.update({row['name']: image[row['address']:row['address']+row['size']]
                     for row in contract.DECLARED['input_blobs']})
    rows = []

    def add(kind, **changes):
        value = deepcopy(defaults); value.update(changes)
        value.update(index=len(rows),kind=kind); rows.append(value)

    add('complete-natural-native-index1-accumulator')
    for value in (0,0xFFFFFFFF):
        add('held-other-actual-uint32-accumulator', accumulator=value)
    for register in range(20):
        values = (0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x80000000,0xFFFFFFFF)
        if register == 4: values = (1,0x101,0xFFFF01,0x7FFFFF01,0x80000001,0xFFFFFF01)
        elif register == 18: values = (0,1,0xF0,0x100,0x200,0x301,0x3F1)
        for value in values:
            incoming = list(defaults['context']); incoming[register] = value
            add('independent-complete-context-field',context=incoming)
    for qm in (0,0x100,0x200,0x300):
        for interrupt in range(0,256,16):
            for t in (0,1):
                incoming = list(defaults['context']);incoming[18] = qm | interrupt | t
                add('complete-QM-interrupt-T-context',context=incoming)
    for name,address,size in RAM_FIELDS:
        active = {}
        if name == 'factor': active.update(phase_first=0,word_latched=2,scaled=0)
        if name == 'counter_second': active.update(maf_word=0)
        if name == 'latched_count': active.update(phase_second=0,count_latched=2)
        if name == 'call_count': active.update(word_latched=0)
        for value in (range(256) if size == 1 else WORD_VALUES if size == 2 else LONG_VALUES):
            add('independent-actual-raw-RAM-state',**{**active,name:value})
    for row in contract.DECLARED['control_blobs']:
        active = {}
        if row['name'] in ('rom_8a4e','rom_8d75'): active.update(seeded=0)
        if row['name'] == 'rom_95b6': active.update(initialized=0)
        for value in (range(256) if row['size'] == 1 else WORD_VALUES):
            add('independent-actual-raw-ROM-control',**{**active,row['name']:value})
    for first in (0,2):
        for second in (0,2):
            for latch in (0,2):
                for init in (0,2):
                    for scaled in (0,2):
                        for enabled in (0,1):
                            add('complete-phase-latch-init-scale-enable-precedence',phase_first=first,
                                phase_second=second,word_latched=latch,initialized=init,scaled=scaled,enabled=enabled)
    for count in (0,1,4,5,6,124,125,126,254,255):
        for threshold in (0,1,5,125,255):
            for phase in (0,2):
                add('counter-latch-underflow-wrap-and-saturation',call_count=count,
                    counter_first=count,counter_second=count,rom_829e=threshold,phase_second=phase,
                    word_latched=0,count_latched=0,maf_word=0)
    for total in LONG_VALUES:
        for count in (0,1,2,255):
            for seed_count in (0,1,255):
                add('unsigned-divisions-zero-bypass-and-short-long-quotients',sum=total,
                    latched_count=count,rom_8a4c=seed_count,count_latched=2,phase_first=0,status=0)
    for total in (0,0xFFFFFFFF-325126,0xFFFFFFFF-325125,0xFFFFFFFE,0xFFFFFFFF):
        for battery in (0,1,127,128,255):
            add('full-uint32-sum-saturation',sum=total,battery=battery,rom_8d75=255,
                phase_first=2,phase_second=0,maf_word=700)
    for coefficient in WORD_VALUES:
        for value in LONG_VALUES:
            for factor in (0,1,127,128,254,255):
                add('split16-decay-and-split8-scaling-with-full-wrap',accumulator=value,
                    rom_9410=coefficient,phase_first=0,word_latched=2,scaled=0,factor=factor)
    for coordinate in range(256):
        add('all-byte-curve-coordinates',phase_first=2,latched_word=coordinate << 8,word_latched=2)
    for name in ('mean_values','factor_values'):
        for index in range(9):
            for value in (0,255):
                table = bytearray(defaults[name]);table[index] = value
                active = dict(phase_first=2,scaled=0,word_latched=2)
                if name == 'factor_values':
                    active.update(latched_word=min(7,index)*0x2000,factor_axis=bytes(range(0,256,32)))
                else:
                    active.update(sum=min(7,index)*32*24000,latched_count=12,count_latched=2,
                        phase_second=2,word_latched=0,mean_axis=bytes(range(0,256,32)),
                        factor_axis=bytes(range(0,256,32)),factor_values=bytes((*range(0,256,32),0)))
                add('held-other-exact-physical-curve-value',**{**active,name:bytes(table)})
    for name in ('mean_axis','factor_axis'):
        for axis in (bytes(8),bytes([255]*8),bytes(range(0,256,32)),bytes(reversed(range(0,256,32))),bytes((0,0,1,1,127,128,255,255))):
            for coordinate in (0,1,127,128,254,255):
                add('physical-axis-order-equality-duplicates-and-boundaries',**{name:axis},
                    phase_first=2,scaled=0,word_latched=2,latched_word=coordinate << 8,
                    sum=coordinate*24000,latched_count=12)
    for row in rows: require_case(row)
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
    return {**{row['address']: case[row['name']].to_bytes(row['size'], 'big')
               for row in contract.DECLARED['control_blobs']},
            **{row['address']: case[row['name']] for row in contract.DECLARED['input_blobs']}}


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
        raise ValueError('the MAF accumulator changes complete immutable inputs or physical ROM controls')


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
    lines = ['/* Complete raw inputs for the natural native index1 MAF accumulator updater. */',
             f'#define MAF_ACCUMULATOR_CALIBRATION_SIZE {sum(row["size"] for row in calibration)}U',
             f'#define MAF_ACCUMULATOR_BOUND_SIZE {sum(row["size"] for row in bound)}U',
             'static const struct span maf_accumulator_calibration[] = {' + ','.join(
                 '{%dU,%dU}' % (row['address'], row['size']) for row in calibration) + '};',
             'static const struct span maf_accumulator_bound[] = {' + ','.join(
                 '{%dU,%dU}' % (row['address'], row['size']) for row in bound) + '};',
             'static const struct span maf_accumulator_ram_fields[] = {' + ','.join(
                 '{%dU,%dU}' % (address, width) for name, address, width in RAM_FIELDS) + '};',
             'static const uint8_t maf_accumulator_calibration_blobs[][MAF_ACCUMULATOR_CALIBRATION_SIZE] = {']
    lines.extend('{' + ','.join(f'0x{value:02x}U' for value in blob) + '},' for blob in blobs)
    lines.extend(('};', f'struct path_case {{ uint32_t ram[{len(RAM_FIELDS)}];struct context context;'
                  'uint8_t pattern;uint32_t calibration_index; };',
                  'static const struct path_case maf_accumulator_cases[] = {', *rows, '};', ''))
    return '\n'.join(lines).encode()
