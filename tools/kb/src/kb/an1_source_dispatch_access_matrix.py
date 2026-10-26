"""Complete typed two-lane source, phase, calibration and ordinary/native RAM inputs."""
from kb import test_contract
from kb import an1_source_dispatch_access_contract as contract
RAM_BASE=0x01000000
RAM_SIZE=65536
RAM_FIELDS=(('ram_1d58', 7512, 2),
 ('ram_1d5a', 7514, 2),
 ('ram_2830', 10288, 2),
 ('ram_2832', 10290, 2),
 ('ram_2834', 10292, 2),
 ('ram_1076', 4214, 1),
 ('ram_1079', 4217, 1),
 ('ram_1174', 4468, 1),
 ('ram_1175', 4469, 1),
 ('ram_1176', 4470, 1),
 ('ram_1188', 4488, 1),
 ('ram_118e', 4494, 1),
 ('ram_1eda', 7898, 1),
 ('ram_1edb', 7899, 1),
 ('ram_1f85', 8069, 1),
 ('ram_2836', 10294, 1),
 ('ram_2837', 10295, 1),
 ('ram_2838', 10296, 1),
 ('ram_2839', 10297, 1),
 ('ram_283a', 10298, 1),
 ('ram_283c', 10300, 1),
 ('ram_283d', 10301, 1),
 ('ram_3d52', 15698, 1),
 ('ram_3d62', 15714, 1),
 ('ram_3f3e', 16190, 1),
 ('ram_3f3f', 16191, 1),
 ('ram_3f40', 16192, 1),
 ('ram_3f41', 16193, 1),
 ('ram_3f42', 16194, 1),
 ('ram_3f43', 16195, 1),
 ('ram_3f44', 16196, 1),
 ('ram_3f45', 16197, 1),
 ('ram_3f46', 16198, 1),
 ('ram_3f47', 16199, 1),
 ('ram_3f48', 16200, 1),
 ('ram_3f49', 16201, 1),
 ('ram_3f4a', 16202, 1),
 ('ram_3f4b', 16203, 1),
 ('ram_3f4c', 16204, 1),
 ('ram_3f4d', 16205, 1),
 ('ram_417f', 16767, 1),
 ('ram_4185', 16773, 1),
 ('ram_4187', 16775, 1),
 ('ram_4226', 16934, 1),
 ('ram_422e', 16942, 1),
 ('ram_4237', 16951, 1),
 ('ram_4238', 16952, 1),
 ('ram_423a', 16954, 1),
 ('ram_42c6', 17094, 1),
 ('ram_42c7', 17095, 1),
 ('ram_454c', 17740, 1),
 ('ram_5610', 22032, 1),
 ('ram_5611', 22033, 1),
 ('ram_5612', 22034, 1),
 ('ram_84c3', 33987, 1))
REGISTERS=tuple(f'raw_r{i}' for i in range(8))
WIDTHS={name:width*8 for name,at,width in RAM_FIELDS}
WIDTHS.update({name:32 for name in REGISTERS})
WIDTHS.update({row['field']:8 for row in contract.DECLARED['configuration']})
WIDTHS.update(variant=8,initial_sr=10)
DEFAULTS={name:0 for name in WIDTHS}
DEFAULTS.update({'cal_083ee': 10,
 'cal_08424': 5,
 'cal_08b34': 129,
 'cal_08b42': 224,
 'cal_08b5b': 0,
 'cal_08b5c': 15,
 'cal_08c5d': 2,
 'cal_08c5e': 2,
 'cal_08cce': 12,
 'cal_08cef': 90,
 'cal_08d26': 150,
 'cal_08d27': 120,
 'cal_08dc8': 16,
 'cal_12dea': 255,
 'cal_12deb': 241,
 'cal_12dec': 200,
 'cal_12ded': 174,
 'cal_12dee': 160,
 'cal_12def': 149,
 'cal_12df0': 141,
 'cal_12df1': 134,
 'cal_12df2': 128,
 'cal_12df3': 122,
 'cal_12df4': 118,
 'cal_12df5': 113,
 'cal_12df6': 109,
 'cal_12df7': 105,
 'cal_12df8': 101,
 'cal_12df9': 97,
 'cal_12dfa': 93,
 'cal_12dfb': 90,
 'cal_12dfc': 86,
 'cal_12dfd': 82,
 'cal_12dfe': 78,
 'cal_12dff': 74,
 'cal_12e00': 70,
 'cal_12e01': 66,
 'cal_12e02': 61,
 'cal_12e03': 57,
 'cal_12e04': 51,
 'cal_12e05': 45,
 'cal_12e06': 38,
 'cal_12e07': 27,
 'cal_12e08': 8,
 'cal_12e09': 0})
DEFAULTS.update(ram_1d58=512,ram_1d5a=544,ram_2832=512,ram_2834=544,ram_3f3e=0,ram_3f44=0,
    ram_1076=100,ram_1079=130,ram_1188=128,ram_118e=20,ram_1eda=1,ram_1edb=1,
    ram_3f4c=255,ram_3f4d=255,ram_4185=0,ram_4187=64,ram_4226=128,ram_422e=8,
    ram_4237=0,ram_4238=0,ram_423a=1,ram_42c6=0,ram_42c7=0,ram_84c3=32,ram_3d52=10,
    ram_5610=128,ram_5611=136,ram_5612=128,variant=7)
DEFAULTS.update({f'ram_{at:04x}':128 for at in range(0x3F45,0x3F4C)})
DEFAULTS.update({f'cal_{0x12DEA+i:05x}':i*8 for i in range(32)})
DEFAULTS.update({name:value for name,value in zip(REGISTERS,
    (0x12345678,0x87654321,0x80000000,0x7FFFFFFF,0xFFFFFFFF,1,0x10000,0xFFFF))})
BYTE_VALUES=(0,1,2,3,7,8,10,31,32,63,64,99,100,127,128,169,170,191,254,255)
WORD_VALUES=(0,1,2,3,4,7,8,31,32,511,512,991,992,1023,1024,32767,32768,65534,65535)


def require_case(case):
    if (type(case) is not dict or set(case)!={*WIDTHS,'entry','kind','index'}
            or type(case['entry']) is not int or case['entry']!=contract.ENTRY
            or type(case['kind']) is not str or type(case['index']) is not int or case['index']<0
            or any(type(case[name]) is not int or not 0<=case[name]<(1<<bits) for name,bits in WIDTHS.items())
            or case['initial_sr']&~0x3F1):
        raise ValueError('the AN1 input changes a complete raw byte,word,calibration,CPU or SR width')


def cases(declared,image):
    rows=[]
    def add(kind,**changes):rows.append(dict(DEFAULTS,**changes,entry=contract.ENTRY,kind=kind,index=len(rows)))
    for name,at,width in RAM_FIELDS:
        for value in WORD_VALUES if width==2 else BYTE_VALUES:add('independent-complete-source-boundary',**{name:value})
    for raw in range(256):add('complete-native-control-byte',ram_84c3=raw)
    for phase in (0,1,2,3,255):
        for initialized in (0,1,2,3,255):
            for raw,prior in ((0,65535),(65535,0),(4,3),(3,4),(512,512)):
                add('two-phase-first-update-filter-and-stall-boundary',ram_3f3e=phase,ram_3f44=initialized,
                    ram_1d58=raw,ram_1d5a=raw,ram_2832=prior,ram_2834=prior)
    for name in ('cal_08b34','cal_08b42'):
        for raw in range(256):add('complete-configuration-gates',**{name:raw})
    for first in (0,2,16,18,255):
        for second in (0,1,32,33,255):
            add('coupled-constant-or-curve-configuration',cal_08b34=first,cal_08b42=second)
    for start in (0,64,255):
        for battery in (0,99,100,127,128,255):
            add('coupled-start-signal-battery-freshness',ram_4185=start,ram_1188=battery)
    for flags in (0,8,16,24,255):
        for speed in (0,15,16,20,255):
            for counter in (0,9,10,254,255):
                add('coupled-speed-counter-latch-boundary',ram_422e=flags,ram_118e=speed,ram_3d52=counter)
    for offset in (0,1,128,255):
        for prior in (0,255):
            add('coupled-small-difference-conditioning',cal_08cef=255,cal_08cce=255,
                cal_08b5b=offset,ram_3f4c=prior)
    for row in contract.DECLARED['configuration']:
        if 0x12DEA<=row['address']<0x12E0A:continue
        for value in BYTE_VALUES:add('scalar-calibration-boundary',**{row['field']:value})
    for lane in (0,1):
        for coordinate in range(256):
            add('complete-raw-curve-coordinate',**{f'ram_{0x1D58+2*lane:04x}':coordinate*4})
    for index in range(32):
        for value in (20,200):
            add('fixed-other-selected-cell-publication',ram_1d58=index*32,
                **{f'cal_{0x12DEA+index:05x}':value})
    for curve in (bytes(32),bytes([255])*32,bytes(range(0,256,8)),bytes(reversed(range(0,256,8)))):
        for coordinate in (0,1,7,8,15,127,128,247,248,255):
            changes={f'cal_{0x12DEA+i:05x}':v for i,v in enumerate(curve)}
            add('complete-ascending-descending-flat-or-endpoint-path',**dict(changes,ram_1d58=coordinate*4,ram_1d5a=coordinate*4))
    for field in REGISTERS:
        for value in (0,1,0x7FFF,0x8000,0xFFFF,0x10000,0x80000000,0xFFFFFFFF):
            add('complete-raw-register-width',**{field:value})
    for qm in (0,0x100,0x200,0x300):
        for interrupt in range(0,256,16):
            for t in (0,1):add('complete-QM-interrupt-T-state',initial_sr=qm|interrupt|t)
    for variant in (0,1,255):add('complete-preserved-context',variant=variant)
    return tuple(rows)


def context(declared,case):
    require_case(case)
    registers=[(0x28765430+i*0x01030507+case['variant']*0x00102040)&0xFFFFFFFF for i in range(15)]
    registers[:8]=[case[name] for name in REGISTERS]
    return (*registers,(0x456789AB+case['variant'])&0xFFFFFFFF,(0x13579BDF+case['variant'])&0xFFFFFFFF,
        (0x2468ACE0+case['variant'])&0xFFFFFFFF,case['initial_sr'],0xB6C70000)


def memory(case):
    require_case(case);raw=bytearray([0xA5])*RAM_SIZE
    for name,at,width in RAM_FIELDS:raw[at:at+width]=case[name].to_bytes(width,'big')
    return bytes(raw)


def calibrations(declared,image,case):
    fixture,_=contract.fixture_for_case(declared,image,case)
    return {row['address']:fixture[row['address']:row['address']+row['size']] for row in contract.CONTROLLED_CALIBRATION}


def require_input(declared,image,case,observed):
    raw=memory(case);cal=calibrations(declared,image,case)
    if (not test_contract.exact(observed['entry'],contract.ENTRY)
            or not test_contract.exact(observed['context'],context(declared,case)) or observed['memory_before']!=(raw,)
            or not test_contract.exact(observed['calibration_before'],cal)
            or not test_contract.exact(observed['calibration_after'],cal)
            or observed['native_before']!=raw[0x8400:0x8500] or observed['native_after']!=observed['native_before']):
        raise ValueError('the AN1 original changes complete explicit raw inputs or ordinary/native/calibration coherence')

def header(declared,image):
    lines=['/* Complete typed invocation inputs. */',
        '#define AN1_DISPATCH_CALIBRATION_SIZE '+str(sum(row['size'] for row in contract.CONTROLLED_CALIBRATION))+'U',
        '#define AN1_DISPATCH_BOUND_SIZE '+str(sum(row['size'] for row in contract.BOUND_SPANS))+'U']
    for name,spans in (('ram_fields',[dict(address=at,size=width) for field,at,width in RAM_FIELDS]),
            ('calibration',contract.CONTROLLED_CALIBRATION),('bound',contract.BOUND_SPANS)):
        lines.append('static const struct span an1_dispatch_'+name+'[] = {'+
            ','.join('{'+f'0x{row["address"]:x}U,{row["size"]}U'+'}' for row in spans)+'};')
    lines.extend(('struct path_case { uint8_t pattern; uint32_t ram[55]; struct context context;',
        '    uint8_t calibration[AN1_DISPATCH_CALIBRATION_SIZE]; };',
        'static const struct path_case an1_dispatch_cases[] = {'))
    for case in declared['cases']:
        require_case(case);registers=context(declared['source'],case)
        cal=calibrations(declared['source'],image,case)
        raw=b''.join(cal[row['address']] for row in contract.CONTROLLED_CALIBRATION)
        ram=','.join(f'0x{case[field]:x}U' for field,at,width in RAM_FIELDS)
        core=','.join(f'0x{value:x}U' for value in registers[:15]);tail=','.join(f'0x{value:x}U' for value in registers[15:])
        lines.append('    {0xa5U,{'+ram+'},{{'+core+'},'+tail+'},{'+','.join(f'0x{value:02x}U' for value in raw)+'}},')
    return '\n'.join((*lines,'};','')).encode()
