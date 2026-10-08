"""Independent lookup arithmetic and complete bounded angle publication state."""
MASK = 0xffffffff
RAM = 0x01000000
ENTRY = 0x56bd0
SCALAR_CAL = (('mode_a', 0x8b34), ('mode_b', 0x8b42), ('inhibit', 0x870b),
              ('warm_limit', 0x8770), ('reload_a', 0x876f), ('reload_b', 0x876e),
              ('override', 0x8729), ('threshold_a', 0x8e03), ('threshold_b', 0x8e06),
              ('threshold_sub', 0x8d2c), ('bias_cap', 0x8bdb), ('cold_limit', 0x8cec),
              ('rpm_limit', 0x88bb), ('alternate_flag', 0x86f9))
WORD_CAL = (('bias_period', 0x9504), ('window_low', 0x9038), ('window_high', 0x9036),
            ('alternate_word', 0x90fa))
TABLE_CAL = (('counter_curve', 0x12136, 8), ('base_curve', 0x12302, 8),
             ('conditional_curve', 0x1230a, 8), ('transient_curve', 0x12c12, 9),
             ('coolant_axis', 0x11bb3, 8))
BYTE_RAM = (('coolant', 0x106e), ('previous_coolant', 0x106f), ('warm_input', 0x1071),
            ('rpm_check', 0x11b2), ('rpm', 0x11b3), ('source_flag', 0x4184),
            ('warm_flag', 0x41d0), ('selector_flag', 0x2484), ('gate_flag', 0x244f),
            ('delay_a', 0x24df), ('delay_b', 0x2593), ('delay_flag', 0x2468),
            ('prefix_flag', 0x24d0), ('window_flag', 0x24a0), ('counter', 0x54ee),
            ('counter_value', 0x14df), ('bias_flag', 0x4205), ('fault', 0x5a98),
            ('transient', 0x340b), ('bias', 0x340c))
WORD_RAM = (('window_input', 0x269e), ('alternate_input', 0x1002),
            ('alternate_ram', 0x5584), ('bias_progress', 0x340e), ('angle', 0x192e))

def signed(value, bits):
    return value if value < 1 << (bits-1) else value-(1 << bits)

class State:
    def __init__(self, incoming, macl, sr):
        self.r = incoming.copy()
        self.macl = macl
        self.sr = sr
        self.frame = {}

    def put(self, at, size, value):
        assert 0 <= at <= 192-size and size in (1, 2, 4)
        for offset, byte in enumerate((value & ((1 << (8*size))-1)).to_bytes(size, 'big')):
            self.frame[at+offset] = byte

    def t(self, value):
        self.sr = (self.sr & ~1) | int(bool(value))

    def linear(self, left, right, fraction, stack):
        assert 0 <= left <= 255 and 0 <= right <= 255 and 0 <= fraction < 65536
        delta = abs(right-left)*fraction//65536
        self.r[1] = self.macl
        self.r[3] = fraction
        self.t(right >= left)
        if right >= left:
            self.r[0], self.r[2] = left+delta, delta
        else:
            self.put(stack-4, 4, left)
            self.r[0] = self.r[2] = left-delta
        return self.r[0]

    def implicit(self, table, base, x, stack):
        self.r[0], self.r[5] = 224, x
        self.t(x >= 224)
        if x >= 224:
            self.r[0] = signed(table[7], 8)
            return table[7]
        index, fraction = divmod(x, 32)
        fraction *= 2048
        self.r[4], self.r[5], self.r[6] = base+index, index, 0x26740
        return self.linear(table[index], table[index+1], fraction, stack)

    def explicit(self, table, axis, x, stack, return_pc):
        self.put(stack-4, 4, return_pc)
        self.put(stack-8, 4, 0x12c12)
        self.r[0], self.r[3], self.r[4], self.r[5], self.r[7] = 0x11bb3, 7, 7, x, 0x26944
        assert all(a < b for a, b in zip(axis, axis[1:]))
        index = max((i for i, value in enumerate(axis) if value <= x), default=0)
        fraction = 0
        if axis[index] < x and index < 7:
            fraction = (x-axis[index])*65536//(axis[index+1]-axis[index])
            self.put(stack-12, 4, 0x26482)
            self.put(stack-16, 4, 0x26c78)
            self.r[2] = 0x26c78
            self.sr &= ~0x301
            self.sr |= (1-(fraction&1)) << 8
        self.r[4], self.r[5], self.r[6] = index, fraction, 0x26740
        return self.linear(table[index], table[index+1], fraction, stack)

    def divide(self, numerator, divisor, stack):
        assert 0 <= numerator <= 65535 and 1 <= divisor <= 65535
        quotient = numerator//divisor
        self.put(stack-4, 4, self.r[2])
        if quotient >= 256:
            self.put(stack-8, 4, self.r[3])
        self.sr = (self.sr & ~0x301) | ((1-(quotient&1)) << 8)
        self.r[0] = quotient
        return quotient

def case(index, defaults, **changes):
    row = dict(defaults)
    row.update(changes)
    for name, _, size in TABLE_CAL:
        row[name] = tuple(row[name])
        assert len(row[name]) == size and all(0 <= value <= 255 for value in row[name])
    for name, _ in (*SCALAR_CAL, *BYTE_RAM):
        assert 0 <= row[name] <= 255
    for name, _ in (*WORD_CAL, *WORD_RAM):
        assert 0 <= row[name] <= 65535
    row['entry_sr'] = changes.get('entry_sr', (index&1)|((index&30)<<3)|((index&96)<<3))
    row['variant'] = index&1
    incoming = [(0x17395b7d ^ i*0x1020304 ^ index*0x101) & MASK for i in range(15)]
    state = State(incoming, 0x9274b6d8 if index&1 else 0x2468ace0, row['entry_sr'])
    r = state.r
    memory = {name: row[name] for name, _ in (*BYTE_RAM, *WORD_RAM)}
    for i in range(4):
        state.put(156-4*i, 4, incoming[11+i])
    state.put(136, 4, state.macl)
    state.put(132, 4, 0x01004567 if index&1 else 0x01003579)
    # Main PR at offset 140 is the independent observer continuation.
    state.put(116, 4, incoming[12]); state.put(112, 4, incoming[13])
    state.put(108, 4, incoming[14]); state.put(104, 4, 0x56be8)
    state.put(100, 4, RAM+0x244c)
    r[7], r[2] = RAM+0x106a, 0x8cec
    r[12], r[13], r[14] = signed(row['coolant'], 8), signed(row['cold_limit'], 8), signed(row['window_flag'], 8)
    if row['coolant'] <= row['cold_limit']:
        memory['prefix_flag'] |= 2
    r[5], r[6], r[2] = 0x88bb, signed(row['rpm_check'], 8), signed(row['rpm_limit'], 8)
    if row['rpm_check'] >= row['rpm_limit']:
        memory['prefix_flag'] |= 16
    r[0], r[2], r[5], r[6] = 0x24, RAM+0x267a, row['window_input'], row['window_low']
    in_window = row['window_low'] <= row['window_input'] < row['window_high'] and bool(row['source_flag']&64)
    if row['window_input'] >= row['window_low']:
        r[6], r[2] = 0x9036, row['window_high']
        if row['window_input'] < row['window_high']:
            r[6] = RAM+0x4184
    memory['window_flag'] = (row['window_flag']|64) if in_window else row['window_flag']&191
    r[0] = signed(memory['window_flag'], 8)
    state.t(not in_window)
    if not in_window:
        if memory['prefix_flag']&4:
            memory['counter'] = min(255, row['counter']+1)
        r[7], r[4], r[2] = RAM+0x106a, 0x12136, 0x26370
        value = state.implicit(row['counter_curve'], 0x12136, row['previous_coolant'], 100)
        r[2], r[6], r[0], r[5] = value, RAM+0x128c, 0xf96, row['counter']
        memory['counter_value'] = value
        r[2], r[6], r[5] = value, signed(memory['counter'], 8), memory['counter']
        state.t(memory['counter'] >= value)
        if memory['counter'] >= value:
            r[6], r[0] = RAM+0x4184, signed(row['source_flag'], 8)
            state.t(not row['source_flag']&64)
            if row['source_flag']&64:
                memory['prefix_flag'] |= 128
                r[0] = 0x60
    r[12], r[13], r[14] = incoming[12:15]
    r[6], r[0] = 0x8b34, signed(row['mode_a'], 8)
    alternate = not row['mode_a']&1 and bool(row['mode_a']&16) and bool(row['mode_b']&65)
    if not row['mode_a']&1:
        state.t(not row['mode_a']&16)
        if row['mode_a']&16:
            r[2], r[0] = 0x8b42, signed(row['mode_b'], 8)
            state.t(not row['mode_b']&65)
    else:
        state.t(False)
    if alternate:
        if not row['mode_b']&1:
            r[6], r[2] = RAM+0x1000, row['alternate_input']//4
            state.t((row['alternate_input']>>1)&1)
        else:
            state.t(not row['alternate_flag']&2)
            r[6] = 0x90fa if row['alternate_flag']&2 else RAM+0x4558
            r[2] = signed(row['alternate_word'] if row['alternate_flag']&2 else row['alternate_ram'], 16)
        memory['angle'] = r[2]&65535
        r[0], r[5] = 0x6a2, RAM+0x128c
        row['path'] = 1
    else:
        r[6], r[0] = 0x870b, signed(row['inhibit'], 8)
        state.t(not row['inhibit']&1)
        row['path'] = 2 if row['inhibit']&1 else 3
        if not row['inhibit']&1:
            r[11], r[12] = RAM+0x106a, RAM+0x41a9
            warm = row['warm_input']+(5 if row['warm_flag']&2 else 0) >= row['warm_limit']
            memory['warm_flag'] = (row['warm_flag']|2) if warm else row['warm_flag']&253
            state.put(120, 1, row['source_flag']&64)
            if row['source_flag']&64 or not row['gate_flag']&32:
                memory['delay_a'] = row['reload_a']
            memory['selector_flag'] = ((row['selector_flag']|16) if not memory['delay_a'] and not row['source_flag']&64
                                       else row['selector_flag']&239)
            if row['delay_flag']&8:
                if not row['delay_b']:
                    memory['selector_flag'] |= 32
            else:
                memory['delay_b'] = row['reload_b']
                memory['selector_flag'] &= 223
            r[13], r[14] = row['warm_input']+(5 if row['warm_flag']&2 else 0), signed(row['selector_flag'], 8)
            if warm and memory['selector_flag']&48 == 48:
                r[2], r[4] = 0x26370, 0x1230a
                r[6] = signed(row['rpm'], 8)
                angle_input = state.implicit(row['conditional_curve'], 0x1230a, row['rpm'], 120)
                row['path'] = 4
            elif memory['prefix_flag']&2 and not memory['prefix_flag']&16:
                r[6] = 0x8729
                angle_input = row['override']
                row['path'] = 5
            else:
                r[2] = 0x26474
                transient = state.explicit(row['transient_curve'], row['coolant_axis'], row['coolant'], 120, 0x56cdc)
                memory['transient'] = transient
                r[2] = transient
                r[4] = row['threshold_a']
                r[5] = min(row['threshold_a'], row['threshold_b'])-row['threshold_sub']
                r[3], r[7] = 0x8d2c, row['warm_input']
                reached = row['warm_input'] >= r[5] or row['warm_input']-row['coolant'] >= transient
                if row['warm_input'] < r[5]:
                    r[5], r[6], r[7] = transient, row['warm_input']-row['coolant'], row['coolant']
                if reached:
                    memory['bias_flag'] |= 1
                    r[6] = signed(memory['bias_flag'], 8)
                if not transient or row['fault']&96:
                    if transient:
                        r[1], r[7], r[4] = RAM+0x5718, 894, 298
                        r[5] = 1
                    r[3], r[2], r[0] = RAM+0x28f8, 0, 0xb14
                    memory['bias'] = 0
                else:
                    r[1], r[7], r[4] = RAM+0x5718, 894, 298
                    r[2] = row['bias_cap']
                    state.macl = row['bias_cap']*400
                    cap = min(65535, state.macl)
                    state.put(128, 4, cap)
                    r[5], r[6] = cap, 65535
                    if not memory['bias_flag']&1:
                        memory['bias_progress'] = 0
                        r[3], r[6] = RAM+0x28f8, 0
                    elif not row['bias_period']:
                        r[2], r[3], r[6] = 0x9504, RAM+0x28f8, cap
                        memory['bias_progress'] = cap
                    else:
                        r[2] = 0x9504
                        state.put(124, 4, 0x21ce0)
                        quotient = state.divide(cap, row['bias_period'], 120)
                        r[2] = quotient
                        r[1], r[3] = RAM+0x28f8, RAM+0x28f8
                        r[6] = min(cap, row['bias_progress']+quotient)
                        memory['bias_progress'] = r[6]
                    r[4] = 0x21ce0
                    state.put(124, 4, r[4])
                    r[5] = cap-r[6]
                    bias = state.divide(r[5], 400, 120)
                    r[2], r[1], r[0] = bias, RAM+0x28f8, 0xb14
                    memory['bias'] = bias&255
                r[2], r[4] = 0x26370, 0x12302
                r[6] = signed(row['rpm'], 8)
                base = state.implicit(row['base_curve'], 0x12302, row['rpm'], 120)
                r[3], r[5] = RAM+0x28f8, signed(memory['bias'], 8)
                angle_input = base+memory['bias']
                row['path'] = 6
            angle_value = 2*min(angle_input, 209)
            memory['angle'] = angle_value
            r[0], r[2], r[5], r[6] = 0x6a2, RAM+0x128c, 210, angle_value
            state.t(False)
    for i in range(11, 15):
        r[i] = incoming[i]
    assert row['entry_sr']&~0x3f1 == 0
    row['expected_sr'] = state.sr
    row['incoming'], row['expected'] = incoming, [value&MASK for value in r]
    row['output'] = memory
    row['frame'] = state.frame
    return row

def matrix(defaults):
    rows = []
    def add(**changes):
        rows.append(case(len(rows), defaults, **changes))
    active = dict(inhibit=0, cold_limit=0, coolant=65, rpm_limit=255, rpm_check=0,
                  warm_input=60, transient_curve=(30, 25, 20, 15, 10, 5, 1, 1, 0),
                  bias_cap=15, bias_period=17, bias_progress=0, bias_flag=0,
                  source_flag=0, warm_flag=0, selector_flag=0, gate_flag=0,
                  delay_flag=0, prefix_flag=0, threshold_a=200, threshold_b=180)
    add()
    for changes in (dict(inhibit=1), dict(mode_a=16,mode_b=64,alternate_input=65535),
                    dict(mode_a=16,mode_b=1,alternate_flag=2,alternate_word=65535),
                    dict(mode_a=16,mode_b=1,alternate_flag=0,alternate_ram=32768),
                    dict(warm_input=255,gate_flag=32,delay_a=0,delay_flag=8,delay_b=0),
                    dict(prefix_flag=2), dict(fault=32), dict(fault=64),
                    dict(bias_flag=1), dict(bias_flag=1,bias_period=0),
                    dict(bias_flag=1,bias_period=1,bias_cap=255),
                    dict(bias_flag=0,bias_period=400,bias_cap=255),
                    dict(coolant=61,bias_flag=1,bias_period=65535),
                    dict(source_flag=64,window_input=10,window_low=0,window_high=20),
                    dict(base_curve=(255,0,255,0,255,0,255,0),rpm=31)):
        add(**(active|changes))
    assert len(rows) == 16
    for rpm in range(256):
        for kind in range(4):
            changes = active|dict(rpm=rpm)
            if kind == 1:
                changes.update(warm_input=255,gate_flag=32,delay_a=0,delay_flag=8,delay_b=0)
            elif kind == 2:
                changes.update(base_curve=(0,255,0,255,0,255,0,255),bias_flag=1)
            elif kind == 3:
                changes.update(base_curve=(255,0,255,0,255,0,255,0),bias_flag=1)
            add(**changes)
    for coolant in range(256):
        for kind in range(3):
            changes = active|dict(coolant=coolant,previous_coolant=coolant,cold_limit=127,
                                  rpm_check=coolant,rpm_limit=128,window_input=100)
            if kind == 1:
                changes.update(transient_curve=(0,255,0,255,0,255,0,255,17),bias_flag=1)
            elif kind == 2:
                changes.update(transient_curve=(255,0,255,0,255,0,255,0,29),bias_flag=1)
            add(**changes)
    for flags in range(256):
        for kind in range(4):
            changes = active|dict(source_flag=flags,warm_flag=flags,selector_flag=flags,
                                  prefix_flag=flags,window_flag=flags,gate_flag=flags,
                                  delay_flag=flags,delay_a=kind,delay_b=kind,bias_flag=flags,
                                  fault=flags if kind&1 else 0)
            add(**changes)
    for cap in (0,1,2,163,164,165,254,255):
        for period in (0,1,2,255,256,257,400,65535):
            for progress in (0,1,32767,32768,65534,65535):
                add(**(active|dict(bias_cap=cap,bias_period=period,bias_progress=progress,bias_flag=1)))
    for value in (0,1,3,4,32767,32768,65534,65535):
        for mode_a in (0,1,16,17,255):
            for mode_b in (0,1,64,65,255):
                add(**(active|dict(mode_a=mode_a,mode_b=mode_b,alternate_input=value,
                                  alternate_word=value,alternate_ram=value,alternate_flag=value&255)))
    for counter in (0,1,9,10,19,20,254,255):
        for value in (0,1,19,20,127,128,254,255):
            for enabled in (0,64):
                add(**(active|dict(counter=counter,source_flag=enabled,prefix_flag=4,
                                  previous_coolant=value,window_input=value,window_low=100,window_high=200)))
    for sr in range(128):
        entry = (sr&1)|((sr&30)<<3)|((sr&96)<<3)
        for kind in range(4):
            add(**(active|dict(entry_sr=entry,bias_flag=kind&1,bias_period=(1,17,400,65535)[kind],
                              coolant=61 if kind&2 else 65,rpm=255 if kind&1 else 127)))
    return rows

def header(rows):
    scalars = ('entry_sr','variant','expected_sr','path') + tuple(name for name,_ in (*SCALAR_CAL,*WORD_CAL,*BYTE_RAM,*WORD_RAM))
    outputs = tuple(name for name,_ in (*BYTE_RAM,*WORD_RAM))
    literal = lambda value: f'0x{value&MASK:x}U'
    lines = []
    max_frame = max(len(row['frame']) for row in rows)
    assert max_frame <= 128
    for row in rows:
        fields = [literal(row[name]) for name in scalars]
        fields += [literal(row['output'][name]) for name in outputs]
        fields += ['{'+','.join(map(literal,row[name]))+'}' for name,_,_ in TABLE_CAL]
        fields += ['{'+','.join(map(literal,row[name]))+'}' for name in ('incoming','expected')]
        fields += [str(len(row['frame']))+'U', '{'+','.join('{'+str(at)+'U,'+literal(value)+'}' for at,value in sorted(row['frame'].items()))+'}']
        lines.append('{'+','.join(fields)+'},')
    return ('/* Independent complete raw angle state and explicit stack writes. */\n'
            '#ifndef END_ANGLE_CASES_H\n#define END_ANGLE_CASES_H\n#include <stdint.h>\n'
            'struct end_angle_case {\n    uint32_t '+','.join(scalars)+';\n'
            '    uint32_t '+','.join('out_'+name for name in outputs)+';\n' +
            ''.join(f'    uint32_t {name}[{size}];\n' for name,_,size in TABLE_CAL) +
            '    uint32_t incoming[15],expected[15],frame_count;\n'
            f'    struct {{ uint32_t at,value; }} frame[{max_frame}];\n' +
            '};\nstatic const struct end_angle_case end_angle_cases[]={\n'+'\n'.join(lines)+
            '\n};\n#define END_ANGLE_CASE_COUNT '+str(len(rows))+'U\n'
            '#define END_ANGLE_EARLY_COUNT 16U\n#endif\n')
