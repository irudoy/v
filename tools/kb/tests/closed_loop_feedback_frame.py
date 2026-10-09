"""Independent semantic frame stores of the complete feedback call.

Offsets refer to the observer window SP-320..SP+31. Incoming PR and the
incoming preserved registers have explicit driver bindings. No SH decoder,
instruction interpreter, or simulator output supplies expected bytes.
"""
from tools.kb.tests import closed_loop_feedback_model as model

u32 = lambda value: value & 0xffffffff
s16 = lambda value: value - 65536 if value & 32768 else value
s8 = lambda value: value - 256 if value & 128 else value


def semantic_trace(initial, rom):
    """Capture equation-level state at real helper boundaries."""
    names = ('transition', 'backup_state', 'active_state', 'neutral_ramp',
        'elapsed_state', 'late_ramp', 'combined_elapsed_ramp')
    originals = {name: getattr(model, name) for name in names}
    trace = {}
    def wrap(name, function):
        def record(memory, *args):
            before = bytes(memory.ram)
            value = function(memory, *args)
            assert name not in trace
            trace[name] = dict(before=before, after=bytes(memory.ram), args=args)
            return value
        return record
    try:
        for name, function in originals.items():
            setattr(model, name, wrap(name, function))
        result = model.evaluate(initial, rom)
    finally:
        for name, function in originals.items():
            setattr(model, name, function)
    assert set(trace) == set(names)
    return result, trace


def expectations(initial, rom, index):
    result, trace = semantic_trace(initial, rom)
    memory = model.Memory(result, rom)
    old = model.Memory(initial, rom)
    frame = bytearray().join(((0xa3b4c5d6 + 17 * i) & 0xffffffff).to_bytes(4, 'big') for i in range(88))
    fixups = []
    def put(at, value, width=4):
        assert 0 <= at and at + width <= len(frame)
        frame[at:at + width] = (value & ((1 << (8 * width)) - 1)).to_bytes(width, 'big')
    def parent(offset, value, width=4):
        put(160 + offset, value, width)
    base = 0xffff88b0
    curve = memory.b(base + 0x97)
    step = memory.b(0x86f8)
    initialized = bool(old.b(base + 0x3c) & 0x20)
    active = [memory.l(base + 0xac + 4 * bank) for bank in range(2)]
    count_one = memory.w(base + 0x62)

    # Complete stock caller save block, including its natural continuation.
    for register in range(8, 15):
        put(316 - 4 * (register - 8), 0x28765430 + 0x01030507 * register + 0x12345 * index)
    put(284, 0x2468ace0 ^ index)
    put(280, 0x456789ab ^ index)
    fixups.append(dict(at=288, source='continuation'))

    # Final outer arguments retain the upper bytes of earlier partial stores.
    parent(0, 0x01000000 | (memory.w(0xffff11bc) & 0xff00) | memory.b(0xffff110e))
    parent(4, 0x6087)
    parent(8, (memory.w(0xffff11bc) & 0xff00) | memory.b(0xffff2f0a))
    parent(0xc, 0x6000 | step)
    for offset, value in ((0x10, 0x608f), (0x14, 0x6089), (0x18, 0x010040b0),
        (0x1c, 0x6072), (0x20, 0x60b5), (0x24, 0x6076), (0x28, 0x607a), (0x2c, 0x60b7)):
        parent(offset, value)
    parent(0x30, active[0])
    parent(0x34, active[1])
    if initialized:
        parent(0x68, 0x010040b0)
    for bank in range(2):
        for offset, value in ((0x38, memory.b(base + 0xe + bank)),
            (0x40, memory.b(0xffff89da + bank)), (0x48, memory.b(0xffff89dc + bank)),
            (0x4c, memory.b(base + 0xb7 + bank)), (0x54, memory.b(base + 0xb5 + bank)),
            (0x5c, memory.b(base + 0xb9 + bank)), (0x64, memory.b(base + 0xa8 + bank))):
            parent(offset + bank, value, 1)
        for offset, value in ((0x3c, memory.w(0xffff2a1e + 2 * bank)),
            (0x44, memory.w(0xffff1628 + 2 * bank)), (0x50, memory.w(base + 0x72 + 2 * bank)),
            (0x58, memory.w(base + 0x76 + 2 * bank)), (0x60, memory.w(0xffff2898 + 2 * bank))):
            parent(offset + 2 * bank, value, 2)
        parent(0x70 + 4 * bank, memory.w(base + 2 * bank), 2)
    parent(0x6c, memory.b(base + 0xb9), 1)

    # Last combined helper 0005dcfa: caller saves and all 20 argument bytes.
    r11 = 0x934 if initialized else memory.b(base + 0x91)
    r12 = u32(s16(memory.w(0x8f9a))) if initialized else active[0]
    r14 = 0x38f if initialized else count_one
    for at, value in ((156, r11), (152, r12), (148, 0x6098), (144, r14),
        (140, 0x5d15e), (136, 0x5ffc), (116, 0x60e8), (120, 0x60ec),
        (124, 0x60ee), (128, 0x608f), (132, 0x6089)):
        put(at, value)

    # Deep elapsed helper 0005df48 save block, before the later ramp overlays it.
    for at, value in ((112, 2), (108, 0x010040b0), (104, 0x9c), (100, 0x6098),
        (96, 0x01002898), (92, 0x01002bd6), (88, 0x6000 | step), (84, 0x5dd38), (80, 0x6050)):
        put(at, value)

    # Elapsed-state locals hold signs, raw counts, and conditional hold data.
    elapsed_before = model.Memory(trace['elapsed_state']['before'], rom)
    elapsed_after = model.Memory(trace['elapsed_state']['after'], rom)
    control, level, common, input_mask, inhibit_mask = trace['elapsed_state']['args']
    high_level = level >= memory.b(0x8db9)
    divided = []
    elapsed_counts = [elapsed_after.w(0xffff3132 + 2 * bank) for bank in range(2)]
    for bank in range(2):
        put(24 + 4 * bank, int(elapsed_before.read(0xffff2bd6 + 2 * bank, 2, signed=True) < 0))
        put(32 + 4 * bank, elapsed_counts[bank], 2)
        value = elapsed_before.w(0xffff2898 + 2 * bank)
        high = value >> 8
        hold = bool(control and high_level and (high >= memory.b(0x82f1) or high <= memory.b(0x82f0)))
        if control and high_level:
            put(24 + (0x10 if bank == 0 else 0x20), value, 2)
            put(24 + (0x14 if bank == 0 else 0x24), high)
            if high < memory.b(0x82f1):
                put(24 + (0x18 if bank == 0 else 0x28), high)
        if hold:
            put(24 + (0x1c if bank == 0 else 0x2c), elapsed_after.w(0xffff89ba + 2 * bank), 2)
        called = not (input_mask[bank] or common or elapsed_before.b(0xffff8908 + bank))
        divided.append(called)
        if called:
            put(24 + (0x30 if bank == 0 else 0x34), memory.b(0x8b7f))
    if any(divided):
        put(20, memory.b(0x8b7f))
        put(16, 0x608f)
        if any(called and elapsed_counts[bank] >= 2560 for bank, called in enumerate(divided)):
            put(12, elapsed_counts[0] if divided[0] else 0x6050)

    # Later ramp 0005ddc4 overlays the upper elapsed save block and two locals.
    for at, value in ((112, 0x010040b0), (108, 0x9c), (104, 0x6098), (100, 0x01002898),
        (96, 0x01002bd6), (92, step), (88, 0x5dd70), (84, 0x6050)):
        put(at, value)
    counts = [memory.w(0xffff40c0 + 2 * bank) for bank in range(2)]
    put(72, u32(s16(counts[1])))
    put(68, 0x608f)
    if any(count >= 2560 for count in counts):
        put(64, 0x21bbc)
    flags = [int(count // 10 >= memory.b(0x8876)) for count in counts]
    for bank in (1, 0):
        value = memory.w(0xffff40b0 + 2 * bank)
        if flags[bank] and step != 255 and value < 0x6400:
            put(76 if bank == 1 else 80, 0x6400)
    return dict(frame=list(frame), fixups=fixups, result=result,
        real_elapsed_divisions=divided, complete_frame_expected=True, accepted_points=0)
