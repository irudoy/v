"""Explicit existing-path input premises for the connected MAF group."""

RAM_BASE = 0x01000000
RAM_SIZE = 65536
KINDS = ('compensation', 'contribution', 'scaling', 'bank-publication', 'diagnostic-copy',
         'compensation-caller','scaling-caller','battery')
ENTRIES = (0x3AE8A, 0x3AF42, 0x3C408, 0x3B224, 0x3C45C,0x3A91A,0x3C3B6,0x39A9E)
FIELDS = ('entry', 'argument', 'input', 'previous', 'correction', 'initialized', 'multiplier', 'bias',
          'mode', 'coefficient', 'reference', 'delta', 'magnitude', 'positive', 'enable',
          'diagnostic', 'inhibit', 'latch', 'fallback', 'weight', 'variant', 'sr')
CALIBRATIONS = ((0x82B6, 3), (0x82BD, 1), (0x87F8, 2), (0x8AC3, 1), (0x92BE, 2), (0x9586, 2), (0x958C, 2))


def cases(declared, image):
    result = []

    def add(kind, bank, **changes):
        seed = KINDS.index(kind) + bank
        row = dict(index=len(result), kind=kind, entry=ENTRIES[KINDS.index(kind)], argument=bank,
            input=1000, previous=168, correction=0, initialized=1, multiplier=335, bias=80,
            mode=0, coefficient=0x8000, reference=0, delta=0, magnitude=0, positive=1,
            enable=1, diagnostic=0, inhibit=0, latch=0, fallback=1193046, weight=128,
            variant=seed % 4, sr=(seed & 1) | ((seed & 15) << 4) | ((seed & 3) << 8))
        if kind == 'compensation':
            row['correction'] = 0x00180000
        row.update(changes)
        result.append(row)

    for bank in (0, 1):
        for input in (0, 1, 0x8000, 65535):
            add('compensation', bank, input=input, initialized=0)
            add('compensation', bank, input=input)
        for previous in (0, 65454, 65455, 65456, 65535):
            add('compensation', bank, previous=previous)
        for correction in (0, 0xFFFF, 0x10000, 0x10001, 0x80000000, 0xFFFFFFFF):
            add('compensation', bank, previous=0, correction=correction)
        add('compensation', bank, previous=0, bias=0)
        add('compensation', bank, input=65535, previous=0, bias=0)
        add('compensation', bank, argument=0xF00DCA00 | bank)

        for input in (0, 1, 1000, 65535):
            add('contribution', bank, input=input)
        for reference in (1000, 65535):
            add('contribution', bank, reference=reference)
        for delta in (0, 1, 1000, 65535):
            add('contribution', bank, reference=1000, delta=delta)
        for correction in (0, 64, 0xFFC0, 0x7FFF, 0x8000):
            add('contribution', bank, input=100, reference=100, correction=correction)
        for magnitude in (0, 1, 65535):
            for positive in (0, 1):
                add('contribution', bank, magnitude=magnitude, positive=positive)
        for fallback in (0, 1, 65535, 0xFFFFFFFF):
            add('contribution', bank, enable=0, input=65535, fallback=fallback)
        add('contribution', bank, latch=1)
        add('contribution', bank, latch=255)
        add('contribution', bank, diagnostic=0x80)
        add('contribution', bank, inhibit=8)
        add('contribution', bank, diagnostic=0x80, latch=255)
        add('contribution', bank, argument=0xF00DCA00 | bank)

        for coefficient in (0, 0x78FF, 0x7900, 0x7FFF, 0x8000, 0x8001, 0x8700, 0x8701, 0xFFFF):
            add('scaling', bank, input=1023, coefficient=coefficient)
        for input in (0, 1, 1022, 1023, 0x7FFF, 0x8000, 0x8001, 65535):
            add('scaling', bank, mode=8, coefficient=0xFFFF, input=input)
        add('scaling', bank, mode=8, coefficient=0, input=1023)
        add('scaling', bank, mode=8, coefficient=1, input=1023)
        add('scaling', bank, argument=0xF00DCA00 | bank)

        for input in (0, 1, 0x7FFFFFFF, 0x80000000, 0xFFFFFFFF):
            add('bank-publication', bank, input=input)
        for input,correction,reference in ((0,0xFFFF,0),(0,0x8000,65535),
                (0x7FFFFFFF,1,0),(0x80000000,0xFFFF,0),(0xFFFFFFFF,1,0),
                (0xFFFFFFFF,0x8000,65535)):
            add('bank-publication', bank, input=input, correction=correction, reference=reference)
        add('bank-publication', bank, argument=0xF00DCA00 | bank)
        for input in (0, 1, 0x7FFF, 0x8000, 0xFFFF):
            add('diagnostic-copy', bank, input=input)
        add('diagnostic-copy', bank, argument=0xF00DCA00 | bank)
    for first,second in ((0,1000),(1,1000),(1000,0),(1000,1),(0x7FFF,0x8000),(0xFFFF,0xFFFF)):
        add('compensation-caller',0,input=first,previous=second,initialized=0,reference=0)
        add('scaling-caller',0,input=first,previous=second,mode=8,coefficient=0x8000)
    for initialized,reference,bias,correction in ((1,0,0,0),(2,1000,80,0xFFFFFFFF),
            (3,1000,80,0x00180000),(3,65535,80,0xFFFFFFFF)):
        add('compensation-caller',0,input=1000,previous=2000,initialized=initialized,
            reference=reference,bias=bias,correction=correction)
    for coefficient in (0,0x78FF,0x7900,0x8700,0x8701,0xFFFF):
        add('scaling-caller',0,input=1023,previous=0x8000,mode=0,coefficient=coefficient)
    for mode in (0,8,0xF7,0xFF):
        for coefficient in (0,1,0x78FF,0x7900,0x7901,0x7FFF,0x8000,0x8001,0x86FF,0x8700,0x8701,0xFFFF):
            add('battery',0,input=1023,mode=mode,coefficient=coefficient)
    for input in (0,1,3,4,507,508,511,512,515,516,1019,1020,1023,1024,1027,2047,32767,32768,65535):
        add('battery',0,input=input,mode=8,coefficient=0xFFFF)
        add('battery',0,input=input,mode=0,coefficient=0x8000)
    for coefficient in (0,1,0x7900,0x8000,0x8700,0xFFFF):
        add('battery',0,input=508,mode=8,coefficient=coefficient)
    for sample in (170,171,172):add('battery',0,input=sample*4,mode=8,coefficient=0xC000)
    for variant in range(4):
        for sr in (0,1,0x100,0x101,0x200,0x201,0x300,0x301):
            add('battery',0,input=1024,mode=8,coefficient=0xFFFF,variant=variant,sr=sr)
    return tuple(result)


def context(declared, case):
    registers = [(0x1728394A + index * 0x110203 + case['variant'] * 0x1000101) & 0xFFFFFFFF for index in range(15)]
    registers[4] = case['argument']
    if case['kind']=='compensation-caller':
        registers[12:15]=[0,1,RAM_BASE+0x1E1C]
    return (*registers, 0x12344321, 0x13579BDF, 0x2468ACE0, case['sr'], 0xB6C70000)


def calibration_spans(declared):
    return CALIBRATIONS


def calibrations(declared, image, case):
    result = {at: image[at:at + size] for at, size in CALIBRATIONS}
    if case['kind'] in ('compensation','compensation-caller'):
        result[0x9586] = case['multiplier'].to_bytes(2, 'big')
        result[0x958C] = case['bias'].to_bytes(2, 'big')
    elif case['kind'] == 'contribution':
        result[0x8AC3] = bytes([case['weight']])
    return result


def memory(case):
    from kb.maf_extended_semantics import put
    bank = case['argument'] & 255
    if bank not in (0, 1):
        raise ValueError('the extended MAF input leaves its explicit bank domain')
    result = bytearray([0xA5]) * RAM_SIZE
    for index in (0, 1):
        selected = index == bank
        comp = selected and case['kind'] == 'compensation'
        contribution = selected and case['kind'] == 'contribution'
        scale = selected and case['kind'] == 'scaling'
        publication = selected and case['kind'] == 'bank-publication'
        diagnostic_copy = selected and case['kind'] == 'diagnostic-copy'
        put(result, 0x101C + index * 2, 2, case['input'] if comp else 0x2A39)
        put(result, 0x1E48 + index * 2, 2, case['previous'] if comp else 0xBEEF)
        put(result, 0x3998 + index * 4, 4, case['correction'] if comp else 0x10203040)
        put(result, 0x1DF0 + index * 2, 2, case['input'] if contribution else 0x1234)
        put(result, 0x1DF8 + index * 4, 4, case['input'] if publication else 0xAABBCCDD)
        put(result, 0x1E00 + index * 2, 2, 0x2345)
        put(result, 0x1E08 + index * 2, 2, case['reference'] if contribution else 0x3456)
        put(result, 0x1E10 + index * 4, 4, case['fallback'] if contribution else 0x00123456)
        put(result, 0x1E18 + index * 2, 2, case['delta'] if contribution else 0x4567)
        put(result, 0x1E1C + index * 2, 2, case['correction'] if contribution else 0xFEDC)
        put(result, 0x1E30 + index * 2, 2, case['magnitude'] if contribution else 0x5678)
        result[0x43CA + index] = case['latch'] if contribution else 0x5A
        put(result, 0x1D62 + index * 2, 2, case['input'] if scale or diagnostic_copy else 0x0369)
        put(result, 0x104C + index * 4, 4, 0x12345678)
        put(result, 0x1A3E + index * 2, 2, 0xD2C3)
    put(result, 0x1E2A, 2, case['correction'] if case['kind']=='bank-publication' else 0x1357)
    put(result, 0x2368, 2, case['reference'] if case['kind']=='bank-publication' else 0x2468)
    result[0x3976] = 0x80 | (2 if bank == 0 else 1)
    if case['kind'] == 'compensation' and case['initialized']:
        result[0x3976] |= bank + 1
    if case['kind']=='compensation-caller':
        result[0x3976]=0x80|case['initialized']
        for index,value in enumerate((case['input'],case['previous'])):
            put(result,0x101C+index*2,2,value)
            put(result,0x1E48+index*2,2,case['reference'])
            put(result,0x3998+index*4,4,case['correction'])
    if case['kind']=='scaling-caller':
        for index,value in enumerate((case['input'],case['previous'])):
            put(result,0x1D62+index*2,2,value)
    if case['kind']=='battery':put(result,0x1D6E,2,case['input'])
    result[0x2449] = case['diagnostic'] if case['kind'] == 'contribution' else 0
    result[0x24B8] = case['inhibit'] if case['kind'] == 'contribution' else 0
    result[0x2462] = case['enable'] if case['kind'] == 'contribution' else 0
    result[0x1E34] = 0x40 | (2 if bank == 0 else 1)
    if case['kind'] == 'contribution' and case['positive']:
        result[0x1E34] |= bank + 1
    result[0x4252] = case['mode'] if case['kind'] in ('scaling','scaling-caller','battery') else 8
    put(result, 0x4970, 2, case['coefficient'] if case['kind'] in ('scaling','scaling-caller','battery') else 0x8000)
    result[0x9818:0x981C] = bytes.fromhex('a5c3d2e1')
    return bytes(result)


def require_input(declared, image, case, observed):
    from kb import test_contract
    if (observed['entry'] != case['entry'] or not test_contract.exact(observed['context'], context(declared, case))
            or observed['memory_before'] != (memory(case),)
            or not test_contract.exact(observed['calibration_before'], calibrations(declared, image, case))
            or not test_contract.exact(observed['calibration_after'], calibrations(declared, image, case))):
        raise ValueError('the extended MAF original changes a complete explicit word, mode, state or calibration input')
