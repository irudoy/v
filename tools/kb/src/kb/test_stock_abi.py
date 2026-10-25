"""Literal observer ABI declarations and strict big-endian raw byte views."""

import re

from kb import test_contract

ONESHOT_FIELDS = (
    ('context', 'r', 0, 60), ('context', 'gbr', 60, 4),
    ('context', 'mach', 64, 4), ('context', 'macl', 68, 4),
    ('context', 'entry_sr', 72, 4),
    ('observation', 'exit', 0, 80), ('observation', 'sp', 80, 4),
    ('observation', 'continuation', 84, 4),
    ('observation', 'abi_before', 88, 48), ('observation', 'abi_after', 136, 48),
    ('observation', 'frame_before', 184, 192), ('observation', 'frame_after', 376, 192),
    ('observation', 'sr_before', 568, 4),
)


def oneshot(region, invocations, entries, spans):
    return dict(schema=1, region=region, observer_symbol='stock_invoke_oneshot',
        context_type='struct context', observation_type='struct observation',
        context_size=76, observation_size=572,
        fields=[dict(side=side, name=name, offset=offset, size=size)
                for side, name, offset, size in ONESHOT_FIELDS],
        spans=[dict(name=name, original=original, alias=alias, size=size)
               for name, original, alias, size in spans],
        selected=[dict(index=index, entry=entry) for index, entry in entries],
        invocations=invocations)


def raw(value, size):
    if (type(value) is not str or len(value) != size * 2
            or re.fullmatch('[0-9a-f]*', value) is None):
        raise ValueError('the stock TEST observation omits its exact big-endian raw bytes')
    return bytes.fromhex(value)


def words(data):
    if type(data) is not bytes or len(data) % 4:
        raise ValueError('the stock TEST ABI word view has an incomplete value')
    return tuple(int.from_bytes(data[at:at + 4], 'big') for at in range(0, len(data), 4))


def oneshot_observation(capture, spec):
    """Decode explicit raw packets; successful decoding grants no semantic fact."""
    if (type(capture) is not dict
            or set(capture) != {'spec', 'abi', 'terminal', 'observations', 'stdout_sha256', 'semantic_admission'}
            or capture['semantic_admission'] is not False
            or not test_contract.exact(capture['spec'], spec)):
        raise ValueError('the stock TEST capture has another observer or declared case scope')
    abi = {key: spec[key] for key in ('schema', 'region', 'context_size', 'observation_size', 'fields', 'spans')}
    if not test_contract.exact(capture['abi'], abi):
        raise ValueError('the stock TEST capture has another compiled C ABI')
    expected_terminal = dict(schema=1, region=spec['region'], invocations=spec['invocations'],
                             captured=len(spec['selected']))
    if (not test_contract.exact(capture['terminal'], expected_terminal)
            or type(capture['observations']) is not list
            or len(capture['observations']) != len(spec['selected'])):
        raise ValueError('the stock TEST capture lacks its complete original invocation count')
    result = []
    for selected, pair in zip(spec['selected'], capture['observations']):
        if type(pair) is not dict or set(pair) != {'before', 'after'}:
            raise ValueError('the stock TEST capture omits its paired actual observation')
        before, after = pair['before'], pair['after']
        if (type(before) is not dict or type(after) is not dict
                or set(before) != {'schema', 'region', 'index', 'entry', 'driver_context', 'driver_memory'}
                or set(after) != {'schema', 'region', 'index', 'entry', 'observation', 'driver_context_after', 'driver_memory'}):
            raise ValueError('the stock TEST raw pair changes its schema')
        identity = dict(schema=1, region=spec['region'], **selected)
        if not all(test_contract.exact({key: packet[key] for key in identity}, identity)
                   for packet in (before, after)):
            raise ValueError('the stock TEST raw pair names another case or entry')
        context = raw(before['driver_context'], 76)
        if raw(after['driver_context_after'], 76) != context:
            raise ValueError('the stock TEST observer mutates its declared const entry context')
        observation = raw(after['observation'], 572)
        memory = []
        for packet in (before, after):
            values = packet['driver_memory']
            if type(values) is not list or len(values) != len(spec['spans']):
                raise ValueError('the stock TEST raw pair omits its memory view')
            memory.append(tuple(raw(value, span['size']) for value, span in zip(values, spec['spans'])))
        result.append(dict(index=selected['index'], entry=selected['entry'],
            context=words(context), exit=words(observation[:80]),
            sp=int.from_bytes(observation[80:84], 'big'),
            continuation=int.from_bytes(observation[84:88], 'big'),
            abi_before=words(observation[88:136]), abi_after=words(observation[136:184]),
            frame_before=observation[184:376], frame_after=observation[376:568],
            sr_before=int.from_bytes(observation[568:572], 'big'),
            memory_before=memory[0], memory_after=memory[1]))
    return result
