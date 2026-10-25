"""Complete raw uint8-index inputs and held-other word alternatives."""
from copy import deepcopy
from kb import test_contract
from kb import channel_target_reader_contract as contract

RAM_BASE = 0x01000000
RAM_SIZE = 65536
WORD_VALUES = (0, 1, 127, 128, 255, 256, 3582, 3583, 3584, 3585, 32767, 32768, 65534, 65535)
DEFAULT_CONTEXT = [*((0x18765430 + i * 0x01030507) & 0xFFFFFFFF for i in range(15)),
                   0x12344321, 0x13579BDF, 0x2468ACE0, 0, 0xB6C70000]
DEFAULT_CONTEXT[4] = 1
DEFAULTS = dict(context=DEFAULT_CONTEXT, pattern=0xA5,
                input_words=[(0x1357 + i * 257) & 65535 for i in range(256)],
                prior_words=[(0xA55A + i * 17) & 65535 for i in range(256)])


def require_case(case):
    if (type(case) is not dict or set(case) != {'index', 'kind', 'context', 'pattern', 'input_words', 'prior_words'}
            or type(case['index']) is not int or case['index'] < 0 or type(case['kind']) is not str
            or type(case['pattern']) is not int or not 0 <= case['pattern'] <= 255):
        raise ValueError('the indexed reader changes an exact raw input shape')
    for name, count, limit in (('context', 20, 0x100000000), ('input_words', 256, 65536), ('prior_words', 256, 65536)):
        values = case[name]
        if type(values) is not list or len(values) != count or any(type(v) is not int or not 0 <= v < limit for v in values):
            raise ValueError('the indexed reader truncates a complete raw context or word array')
    if case['context'][18] & ~0x3F1:
        raise ValueError('the indexed reader changes the admitted complete I/M/Q/T input')


def cases(source, image):
    rows = []

    def add(kind, context=None, channel=None, selected=None, owner=None, prior=None, pattern=None):
        value = deepcopy(DEFAULTS)
        if context is not None:
            value['context'] = list(context)
        if channel is not None:
            value['context'][4] = channel
        index = value['context'][4] & 255
        if selected is not None:
            value['input_words'][index] = selected
        if owner is not None:
            value['input_words'][1] = owner
        if prior is not None:
            value['prior_words'][index] = prior
        if pattern is not None:
            value['pattern'] = pattern
        value.update(index=len(rows), kind=kind)
        rows.append(value)

    add('complete-natural-indexed-reader')
    for index in range(256):
        for word in (3583, 3584):
            add('complete-uint8-index-and-both-saturation-outcomes', channel=index, selected=word)
    for index in (0, 1, 255):
        for word in WORD_VALUES:
            add('raw-word-sign-and-saturation-boundaries-at-owner-and-domain-ends', channel=index, selected=word)
    for index in (0, 1, 2, 127, 128, 255):
        for high in (*(1 << bit for bit in range(8, 32)), 0xFFFFFF00):
            for word in (3583, 3584):
                add('upper24-index-alias-and-real-saturation-branch', channel=high | index, selected=word)
    for register in range(20):
        values = (0, 1, 0x7FFF, 0x8000, 0xFFFF, 0x10000, 0x80000000, 0xFFFFFFFF)
        if register == 18:
            values = (0, 1, 0xF0, 0x100, 0x200, 0x301, 0x3F1)
        for raw in values:
            context = list(DEFAULT_CONTEXT)
            context[register] = raw
            add('independent-complete-context-field', context=context)
    for qm in (0, 0x100, 0x200, 0x300):
        for interrupt in range(0, 256, 16):
            for t in (0, 1):
                context = list(DEFAULT_CONTEXT)
                context[18] = qm | interrupt | t
                add('complete-QM-interrupt-T-context', context=context)
    for raw in WORD_VALUES:
        add('held-other-owning-word-alternative', channel=1, owner=raw)
        for index in (0, 2, 255):
            add('held-other-unselected-owner-control', channel=index, owner=raw)
        for index in (0, 1, 2, 255):
            add('independent-prior-destination-word', channel=index, prior=raw)
    for pattern in (0, 1, 0x5A, 0x80, 0xFF):
        for index in (0, 1, 2, 255):
            add('complete-other-RAM-pattern', channel=index, pattern=pattern)
    return tuple(rows)


def context(source, case):
    require_case(case)
    return tuple(case['context'])


def memory(case):
    require_case(case)
    out = bytearray([case['pattern']]) * RAM_SIZE
    for start, name in ((0x28BC, 'input_words'), (0x387A, 'prior_words')):
        for index, word in enumerate(case[name]):
            at = start + 2 * index
            out[at:at+2] = word.to_bytes(2, 'big')
    return bytes(out)


def calibrations(source, image, case):
    require_case(case)
    fixture, _ = contract.fixture_for_case(source, image, case)
    return {row['address']: fixture[row['address']:row['address']+row['size']] for row in contract.CONTROLLED_CALIBRATION}


def require_input(source, image, case, observed):
    wanted = calibrations(source, image, case)
    if (observed['entry'] != contract.ENTRY or not test_contract.exact(observed['context'], context(source, case))
            or observed['memory_before'] != (memory(case),)
            or not test_contract.exact(observed['calibration_before'], wanted)
            or not test_contract.exact(observed['calibration_after'], wanted)):
        raise ValueError('the indexed reader changes a complete immutable raw input or calibration')


def header(declared, image):
    source = declared['source']
    cal, bound = contract.CONTROLLED_CALIBRATION, contract.BOUND_SPANS
    lines = ['/* Complete raw inputs for one full indexed stock leaf. */',
             f'#define CHANNEL_CALIBRATION_SIZE {sum(r["size"] for r in cal)}U',
             f'#define CHANNEL_BOUND_SIZE {sum(r["size"] for r in bound)}U',
             'static const struct span channel_calibration[] = {' + ','.join('{%dU,%dU}' % (r['address'], r['size']) for r in cal) + '};',
             'static const struct span channel_bound[] = {' + ','.join('{%dU,%dU}' % (r['address'], r['size']) for r in bound) + '};',
             'struct path_case { uint16_t input_words[256],prior_words[256];struct context context;uint8_t pattern,calibration[CHANNEL_CALIBRATION_SIZE]; };',
             'static const struct path_case channel_cases[] = {']
    for case in declared['cases']:
        raw = context(source, case)
        ctx = '{{' + ','.join(f'0x{v:x}U' for v in raw[:15]) + '},' + ','.join(f'0x{v:x}U' for v in raw[15:]) + '}'
        mapping = calibrations(source, image, case)
        blob = b''.join(mapping[row['address']] for row in cal)
        words = ['{' + ','.join(f'0x{v:04x}U' for v in case[name]) + '}' for name in ('input_words', 'prior_words')]
        lines.append('{' + ','.join((*words, ctx, f'0x{case["pattern"]:02x}U',
                                     '{' + ','.join(f'0x{v:02x}U' for v in blob) + '}')) + '},')
    return '\n'.join((*lines, '};', '')).encode()
