"""Raw complete caller inputs for the engine-speed byte and its actual curve handoffs."""
from copy import deepcopy
from kb import test_contract
from kb import engine_speed_curve_input_contract as contract

RAM_BASE = 0x01000000
RAM_SIZE = 65536
RAM_FIELDS = (
    ('byte_1071',0x1071,1),('byte_41de',0x41DE,1),('byte_2458',0x2458,1),
    ('byte_2590',0x2590,1),('word_2318',0x2318,2),('speed_snapshot',0x11B2,1),
    ('byte_244f',0x244F,1),('byte_22ff',0x22FF,1),('byte_4184',0x4184,1),
    ('byte_42bc',0x42BC,1),('byte_22e1',0x22E1,1),('byte_4251',0x4251,1),
    ('byte_106e',0x106E,1),('clock_15f8',0x15F8,4),('byte_106f',0x106F,1),
    ('prior_1841',0x1841,1),('prior_1842',0x1842,1),('byte_1239',0x1239,1),
    ('byte_248d',0x248D,1),('byte_1277',0x1277,1),('prior_1513',0x1513,1),
    ('byte_23c5',0x23C5,1),('byte_1a7d',0x1A7D,1),('prior_1511',0x1511,1),
    ('byte_2404',0x2404,1),('prior_1512',0x1512,1),('byte_24a7',0x24A7,1),
    ('byte_2442',0x2442,1),('byte_11ae',0x11AE,1),('byte_2443',0x2443,1),
    ('prior_1515',0x1515,1),('prior_1516',0x1516,1),('prior_1514',0x1514,1),
    ('word_28b8',0x28B8,2),('word_28ba',0x28BA,2),('prior_1900',0x1900,2),
    ('byte_41ab',0x41AB,1),('word_10ca',0x10CA,2),('prior_134b',0x134B,1),
    ('prior_1347',0x1347,1),('prior_1349',0x1349,1),('prior_12db',0x12DB,1),
    ('prior_12d5',0x12D5,1),('prior_23ee',0x23EE,1),('prior_9818',0x9818,4))
WIDTHS = {name:width*8 for name,at,width in RAM_FIELDS}
WIDTHS.update({r['name']:r['size']*8 for r in contract.DECLARED['control_blobs']})
WIDTHS['pattern'] = 8
ARRAYS = {'context':(20,32),'speed_curves':(24,8),'correction_curves':(32,8),
    'correction_surface':(64,8),'surface_outer_axis':(8,8),'surface_inner_axis':(8,8),
    'explicit_byte_curve':(9,8),'explicit_byte_axis':(8,8),
    'explicit_word_curve':(9,16),'explicit_word_axis':(8,16)}
BYTE_VALUES = (0,1,2,3,4,7,8,15,16,17,31,32,33,63,64,65,127,128,129,223,224,225,254,255)
WORD_VALUES = (0,1,2,255,256,257,7349,7350,7351,8191,8192,8193,
               16383,16384,32767,32768,57344,65534,65535)
LONG_VALUES = (0,1,65535,65536,0x7FFFFFFF,0x80000000,0xFFFFFFFF)
DEFAULT_CONTEXT = [*((0x18765430+i*0x01030507)&0xFFFFFFFF for i in range(15)),
                   0x12344321,0x13579BDF,0x2468ACE0,0,0xB6C70000]
DEFAULTS = {name:0 for name in WIDTHS}
DEFAULTS.update(context=DEFAULT_CONTEXT,pattern=0xA5,
    speed_curves=[128+i for i in range(8)]*3,correction_curves=[0]*32,
    correction_surface=[128]*64,surface_outer_axis=[i*32 for i in range(8)],
    surface_inner_axis=[i*32 for i in range(8)],explicit_byte_curve=[0]*9,
    explicit_byte_axis=[i*32 for i in range(8)],explicit_word_curve=[0]*9,
    explicit_word_axis=[i*8192 for i in range(8)],
    rom_86a2=128,rom_86a3=0,rom_86a4=255,rom_870b=0,
    rom_8789=0,rom_878a=0,rom_8c3b=0,rom_8cd1=255,rom_9010=7350,
    rom_9276=0,rom_9278=100,rom_927a=0,rom_927c=100,
    byte_2590=1,prior_1841=17,prior_1842=23,prior_1513=77,
    prior_1511=91,prior_1512=101,prior_1514=111,prior_1515=121,prior_1516=131,
    prior_1900=0xA5B6,prior_134b=141,prior_1347=151,prior_1349=161,
    prior_12db=171,prior_12d5=181,prior_23ee=191,prior_9818=0xDEADBEEF)
SPEED_MODES = (
    ('first',dict(rom_870b=1,word_2318=0)),
    ('second',dict(rom_870b=0,byte_2458=32,byte_1071=255,byte_41de=0,byte_2590=1)),
    ('third',dict(rom_870b=0)),
    ('substitute',dict(rom_870b=0,byte_2458=128,byte_22ff=3)))


def require_case(case):
    if (type(case) is not dict or set(case) != {*WIDTHS,*ARRAYS,'index','kind'}
            or type(case['index']) is not int or case['index'] < 0 or type(case['kind']) is not str
            or any(type(case[name]) is not int or not 0 <= case[name] < (1 << bits)
                   for name,bits in WIDTHS.items())):
        raise ValueError('the speed-coordinate input changes a raw scalar or supplies a live result')
    for name,(count,bits) in ARRAYS.items():
        values = case[name]
        if (type(values) is not list or len(values) != count
                or any(type(v) is not int or not 0 <= v < (1 << bits) for v in values)):
            raise ValueError('the speed-coordinate input truncates a complete CPU, curve, surface or axis')
    if case['context'][18] & ~0x3F1:
        raise ValueError('the speed-coordinate input changes admitted I/M/Q/T controls')


def cases(source,image):
    rows = []

    def add(kind,**changes):
        value = deepcopy(DEFAULTS)
        value.update(changes)
        value.update(index=len(rows),kind=kind)
        rows.append(value)

    add('complete-natural-speed-coordinate-caller')
    stock = {r['name']:int.from_bytes(image[r['address']:r['address']+r['size']],'big')
             for r in source['control_blobs']}
    for r in source['input_blobs']:
        width = ARRAYS[r['name']][1]//8
        stock[r['name']] = [int.from_bytes(image[i:i+width],'big')
                           for i in range(r['address'],r['address']+r['size'],width)]
    add('complete-owned-stock-calibration',**stock)
    for register in range(20):
        values = LONG_VALUES if register != 18 else (0,1,0xF0,0x100,0x200,0x301,0x3F1)
        for raw in values:
            context = list(DEFAULT_CONTEXT)
            context[register] = raw
            add('independent-complete-CPU-context-field',context=context)
    for qm in (0,0x100,0x200,0x300):
        for interrupt in range(0,256,16):
            for t in (0,1):
                context = list(DEFAULT_CONTEXT)
                context[18] = qm|interrupt|t
                add('complete-QM-interrupt-T-context',context=context)
    for mode,changes in SPEED_MODES:
        for speed in range(256) if mode != 'substitute' else BYTE_VALUES:
            add('actual-speed-handoff-'+mode,**dict(changes,speed_snapshot=speed))
    for field,at,width in RAM_FIELDS:
        for raw in BYTE_VALUES if width == 1 else WORD_VALUES if width == 2 else LONG_VALUES:
            add('independent-raw-RAM-input-and-prior-publication',**{field:raw})
    for r in source['control_blobs']:
        for raw in BYTE_VALUES if r['size'] == 1 else WORD_VALUES:
            add('independent-raw-ROM-control',**{r['name']:raw})
    for index in range(24):
        mode,changes = SPEED_MODES[(2,1,0)[index//8]]
        for raw in (0,1,127,128,129,255):
            curve = list(DEFAULTS['speed_curves'])
            curve[index] = raw
            add('independent-physical-speed-curve-byte',
                **dict(changes,speed_snapshot=(index%8)*32,speed_curves=curve))
    for curve in ([0,255]*12,[255,0]*12,[0]*24,[255]*24):
        for speed in BYTE_VALUES:
            for mode,changes in SPEED_MODES[:3]:
                add('directed-implicit-speed-interpolation-and-endpoint-promotion',
                    **dict(changes,speed_snapshot=speed,speed_curves=list(curve)))
    for index in range(32):
        for raw in (0,1,127,128,255):
            curve = list(DEFAULTS['correction_curves'])
            curve[index] = raw
            hot = index//8 != 0
            changes = dict(byte_244f=4 if hot else 0,byte_106f=(index%8)*32,
                           correction_curves=curve)
            if index//8 == 2:changes['byte_22e1']=3
            if index//8 == 3:changes.update(byte_4251=0,byte_42bc=1,byte_4184=0)
            add('independent-physical-correction-curve-byte',**changes)
    for curve in ([0,255]*16,[255,0]*16):
        for coordinate in BYTE_VALUES:
            for changes in (dict(byte_244f=0),dict(byte_244f=4,byte_22e1=3),
                            dict(byte_244f=4,byte_4251=0,byte_42bc=1,byte_4184=0)):
                add('directed-implicit-correction-products-and-signed-endpoints',
                    **dict(changes,byte_106f=coordinate,correction_curves=list(curve)))
    for hot in (False,True):
        for lower,upper in ((0,0),(1,0),(0,1),(0,65535),(32767,32768),(32768,32767),(65534,65535)):
            values = {0,1,0x7FFFFFFF,0x80000000,0xFFFFFFFF,lower,upper,
                      max(0,lower-1),min(0xFFFFFFFF,lower+1),max(0,upper-1),min(0xFFFFFFFF,upper+1)}
            for current in sorted(values):
                for factor in (0,128,255):
                    changes = dict(byte_244f=4 if hot else 0,rom_8cd1=0,clock_15f8=current,
                        correction_curves=[255]*32)
                    changes.update({'rom_927a':lower,'rom_927c':upper,'rom_878a':factor} if hot else
                                   {'rom_9276':lower,'rom_9278':upper,'rom_8789':factor})
                    add('actual-positive-divisor-clock-term-or-bypass',**changes)
    for latch,first,second in ((0,0,0),(0,1,0),(0,1,1),(16,0,0),(16,1,0),(16,255,255)):
        for prior in (0,127,128,255):
            add('full-critical-latch-and-saved-term',byte_248d=latch,byte_1239=first,
                byte_1277=second,prior_1513=prior)
    for origin,subtraction,base,speed in ((127,255,0,0),(128,0,255,224),
                                         (0,0,0,0),(127,0,0,127)):
        add('signed-critical-clamp-boundary',byte_2404=origin,byte_23c5=subtraction,
            byte_1a7d=base,speed_snapshot=speed,correction_curves=[255]*32)
    for index in range(64):
        for raw in (0,1,127,128,255):
            surface = [128]*64
            surface[index] = raw
            add('independent-physical-surface-cell-and-two-real-calls',byte_24a7=2,
                byte_11ae=(index//8)*32,byte_2442=(index%8)*32,byte_2443=(index%8)*32,
                correction_surface=surface)
    byte_axes = ([i*32 for i in range(8)],[0]*8,[255]*8,[255-i*32 for i in range(8)],
                 [0,255,0,128,127,1,254,255],[0,1,1,128,128,254,255,255])
    for name,field in (('surface_outer_axis','byte_11ae'),('surface_inner_axis','byte_2442'),
                       ('explicit_byte_axis','byte_106f')):
        for axis in byte_axes:
            values = {0,1,31,32,33,127,128,223,224,255}
            for knot in axis:values.update((max(0,knot-1),knot,min(255,knot+1)))
            for coordinate in sorted(values):
                add('rightmost-byte-axis-without-monotonicity-premise',
                    **{name:list(axis),field:coordinate,'byte_24a7':2,'byte_11ae':coordinate if field=='byte_11ae' else 1,
                       'byte_41ab':64,'word_28b8':65535,'word_28ba':65535,
                       'correction_surface':[(i*7)&255 for i in range(64)]})
    for outer,inner in ((0,0),(1,0),(0,1),(1,1),(31,31),(32,32),(33,33),(255,255)):
        for descending in (False,True):
            add('all-four-actual-surface-kernel-paths',byte_24a7=2,byte_11ae=outer,
                byte_2442=inner,byte_2443=255-inner,
                correction_surface=[255-(i*3) if descending else i*3 for i in range(64)])
    word_axes = ([i*8192 for i in range(8)],[0]*8,[65535]*8,[65535-i*8192 for i in range(8)],
        [0,65535,0,32768,32767,1,65534,65535],[0,1,1,128,128,32768,65535,65535])
    for axis in word_axes:
        values = {*WORD_VALUES}
        for knot in axis:values.update((max(0,knot-1),knot,min(65535,knot+1)))
        for coordinate in sorted(values):
            add('rightmost-word-axis-and-actual-additive-input',byte_41ab=64,
                word_28b8=65535,word_28ba=65535,word_10ca=coordinate,
                explicit_word_axis=list(axis),explicit_word_curve=[65535-i*7000 for i in range(9)],
                explicit_byte_curve=[255]*9)
    for index in range(9):
        for raw in (0,1,127,128,255):
            curve = [0]*9
            curve[index] = raw
            add('independent-explicit-byte-curve-or-physical-guard',byte_41ab=64,
                word_28b8=65535,word_28ba=65535,byte_106f=min(index,7)*32,
                explicit_byte_curve=curve,explicit_word_curve=[255]*9)
        for raw in (0,1,255,256,32768,65535):
            curve = [0]*9
            curve[index] = raw
            add('independent-explicit-word-curve-or-physical-guard',byte_41ab=64,
                word_28b8=65535,word_28ba=65535,word_10ca=min(index,7)*8192,
                explicit_word_curve=curve,explicit_byte_curve=[255]*9)
    for threshold in WORD_VALUES:
        for minimum in sorted({max(0,threshold-1),threshold,min(65535,threshold+1),65535}):
            add('unsigned-minimum-factor-threshold-and-wide-product',rom_9010=threshold,
                byte_41ab=64,word_28b8=minimum,word_28ba=65535,
                explicit_byte_curve=[255]*9,explicit_word_curve=[65535]*9)
            add('opposite-minimum-word-and-factor-floor',rom_9010=threshold,
                byte_41ab=64,word_28ba=minimum,word_28b8=65535)
    for pattern in (0,1,0x5A,0x80,0xFF):
        add('complete-unmodified-RAM-pattern',pattern=pattern)
    return tuple(rows)


def context(source,case):
    require_case(case)
    return tuple(case['context'])


def memory(case):
    require_case(case)
    out = bytearray([case['pattern']])*RAM_SIZE
    for name,at,width in RAM_FIELDS:
        out[at:at+width] = case[name].to_bytes(width,'big')
    return bytes(out)


def input_calibrations(case):
    require_case(case)
    mapping = {r['address']:case[r['name']].to_bytes(r['size'],'big')
               for r in contract.DECLARED['control_blobs']}
    for r in contract.DECLARED['input_blobs']:
        width = ARRAYS[r['name']][1]//8
        mapping[r['address']] = b''.join(v.to_bytes(width,'big') for v in case[r['name']])
    return mapping


def calibrations(source,image,case):
    fixture,_ = contract.fixture_for_case(source,image,case)
    return {r['address']:fixture[r['address']:r['address']+r['size']]
            for r in contract.CONTROLLED_CALIBRATION}


def require_input(source,image,case,observed):
    wanted = calibrations(source,image,case)
    if (observed['entry'] != contract.ENTRY
            or not test_contract.exact(observed['context'],context(source,case))
            or observed['memory_before'] != (memory(case),)
            or not test_contract.exact(observed['calibration_before'],wanted)
            or not test_contract.exact(observed['calibration_after'],wanted)):
        raise ValueError('the speed-coordinate entry changes complete immutable inputs or calibration')


def header(declared,image):
    source=declared['source'];cal,bound=contract.CONTROLLED_CALIBRATION,contract.BOUND_SPANS
    lines=['/* Complete raw inputs only; no supplied live candidate or expected output. */',
        f'#define ENGINE_SPEED_CALIBRATION_SIZE {sum(r["size"] for r in cal)}U',
        f'#define ENGINE_SPEED_BOUND_SIZE {sum(r["size"] for r in bound)}U',
        'static const struct span engine_speed_calibration[] = {'+','.join('{%dU,%dU}'%(r['address'],r['size']) for r in cal)+'};',
        'static const struct span engine_speed_bound[] = {'+','.join('{%dU,%dU}'%(r['address'],r['size']) for r in bound)+'};',
        'struct path_case { '+''.join('uint32_t '+name+';' for name,at,width in RAM_FIELDS)+
        'struct context context;uint8_t pattern,calibration[ENGINE_SPEED_CALIBRATION_SIZE]; };',
        'static const struct path_case engine_speed_cases[] = {']
    for case in declared['cases']:
        raw=context(source,case)
        ctx='{{'+','.join(f'0x{v:x}U' for v in raw[:15])+'},'+','.join(f'0x{v:x}U' for v in raw[15:])+'}'
        mapping=calibrations(source,image,case);blob=b''.join(mapping[row['address']] for row in cal)
        lines.append('{'+','.join(f'0x{case[name]:x}U' for name,at,width in RAM_FIELDS)+','+ctx+
            f',0x{case["pattern"]:02x}U,'+'{'+','.join(f'0x{v:02x}U' for v in blob)+'}},')
    return '\n'.join((*lines,'};','')).encode()
