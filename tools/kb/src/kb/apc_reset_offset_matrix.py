"""Typed inputs for the natural APC reset offset entry."""

RAM_BASE=0x01000000
RAM_SIZE=65536
ENTRY=0x4C1E4
PATTERNS=('stock','rising','falling','constant','high')


def curve(pattern):
    if pattern=='stock':return None
    if pattern=='rising':return tuple(index*30 for index in range(8))
    if pattern=='falling':return tuple(240-index*30 for index in range(8))
    if pattern=='constant':return (100,)*8
    if pattern=='high':return (255,)*8
    raise ValueError('the APC reset calibration input changes its declared pattern')


def cases(declared,image):
    result=[]
    def add(pattern='stock', gate=0, word=400, secondary=3, source=40, flag=0, ceiling=0):
        result.append(dict(index=len(result), entry=ENTRY, pattern=pattern, gate=gate, word=word,
            secondary=secondary, source=source, flag=flag, ceiling=ceiling, variant=len(result)%4,
            sr=(len(result)&1)|((len(result)&15)<<4)|((len(result)&3)<<8)))
    for pattern in ('rising','falling','constant','high','stock'):
        add(pattern, gate=0, word=200, secondary=4, source=80)
    add(gate=1, word=400, secondary=3, source=40)
    add(gate=1, word=2000, secondary=2, source=10)
    add(gate=0, word=0, secondary=0, source=20)
    add(gate=1, word=100, secondary=0, source=30)
    add(gate=0, source=230, ceiling=255, secondary=5)
    add(gate=0, source=40, flag=1, secondary=6)
    add(gate=1, word=80, secondary=1, source=255, pattern='constant')
    return tuple(result)


def context(declared, case):
    registers=[(0x1728394A+reg*0x110203+case['variant']*0x1000101)&0xFFFFFFFF for reg in range(15)]
    return (*registers, 0x12344321, 0x13579BDF, 0x2468ACE0, case['sr'], 0xB6C70000|case['source'])


def calibration_spans(declared):
    return ((0x1208E,8),(0x12096,8),(0x851F,7),(0x8291,1),(0x828A,1),(0x959A,2),(0x8B87,2))


def calibrations(declared, image, case):
    values=curve(case['pattern'])
    primary=image[0x1208E:0x12096] if values is None else bytes(values)
    config=bytearray(image[0x851F:0x8526])
    if case['ceiling']:config[3]=case['ceiling']&255
    return {0x1208E:primary, 0x12096:image[0x12096:0x1209E], 0x851F:bytes(config),
        0x8291:image[0x8291:0x8292], 0x828A:image[0x828A:0x828B], 0x959A:image[0x959A:0x959C],
        0x8B87:image[0x8B87:0x8B89]}


def memory(case):
    result=bytearray(RAM_SIZE)
    result[0x4184]=0x40 if case['gate'] else 0
    result[0x10CA:0x10CC]=case['word'].to_bytes(2,'big')
    result[0x1108]=case['secondary']&255
    result[0x11AE]=case['source']&255
    result[0x4251]=1 if case['flag'] else 0
    result[0x9818:0x981C]=bytes.fromhex('a5c3d2e1')
    return bytes(result)


def require_input(declared, image, case, observed):
    from kb import test_contract
    if (observed['entry']!=ENTRY or not test_contract.exact(observed['context'], context(declared, case))
            or observed['memory_before']!=(memory(case),)
            or not test_contract.exact(observed['calibration_before'], calibrations(declared, image, case))
            or not test_contract.exact(observed['calibration_after'], calibrations(declared, image, case))):
        raise ValueError('the APC reset original changes an explicit gate, word, curve or configuration byte')
