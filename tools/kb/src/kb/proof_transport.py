"""Strict raw transport for the existing complete ordinary-state observer.

Decoding preserves complete bytes. It establishes neither an instruction result
nor a physical, numerical, causal, native or publication claim.
"""

import json

from kb import proof_adapter, test_contract, test_stock_abi, width_view_matrix

SOURCE = 'tools/kb/src/kb/proof_transport.py'


def _objects(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('the raw adapter transport repeats a JSON key')
        result[key] = value
    return result


def decode(packet, declared, adapter):
    proof_adapter.validate(adapter)
    if type(packet) is not dict or type(packet.get('stdout')) is not str:
        raise ValueError('the raw adapter transport lacks its original stdout')
    prefix = adapter['prefix']
    rows = [json.loads(line[len(prefix):], object_pairs_hook=_objects)
        for line in packet['stdout'].splitlines() if line.startswith(prefix)]
    cases = declared['cases']
    if type(cases) not in (list, tuple) or not cases or len(rows) != len(cases):
        raise ValueError('the raw adapter transport omits or repeats an actual invocation')
    calibration = [[row['address'], row['size']] for row in adapter['calibration']]
    if not test_contract.exact(declared['calibration_spans'], calibration):
        raise ValueError('the raw adapter transport changes its calibration span declaration')
    bound_size = sum(row['size'] for row in adapter['bound'])
    if adapter['bound'] and not test_contract.exact(declared['bound_spans'],
            [[row['address'], row['size']] for row in adapter['bound']]):
        raise ValueError('the raw adapter transport changes its bound instruction/data spans')
    keys = proof_adapter.TRANSPORT_FIELDS | ({'bound_before', 'bound_after'} if adapter['bound'] else set())
    parsed = []
    for index, (row, case) in enumerate(zip(rows, cases)):
        if type(row) is not dict or set(row) != keys:
            raise ValueError('the raw adapter transport changes its complete schema')
        expected = dict(schema=1, index=index, kind=proof_adapter._kind(adapter, case), entry=case['entry'])
        if (type(case['entry']) is not int or case['entry'] not in adapter['entries']
                or not test_contract.exact({key: row[key] for key in expected}, expected)):
            raise ValueError('the raw adapter transport changes the typed input role, entry or order')
        context = test_stock_abi.raw(row['context'], 80)
        if test_stock_abi.raw(row['context_after'], 80) != context:
            raise ValueError('the raw adapter transport changes its complete const incoming context')
        out = test_stock_abi.raw(row['observation'], 572)
        spans = {}
        for name in ('calibration_before', 'calibration_after'):
            raw = test_stock_abi.raw(row[name], sum(size for at, size in calibration))
            offset, spans[name] = 0, {}
            for at, size in calibration:
                spans[name][at] = raw[offset:offset+size]
                offset += size
        ram = {name: width_view_matrix.decode_rle(row[name]) for name in ('ram_before', 'ram_after')}
        if any(type(data) is not bytes or len(data) != 65536 for data in ram.values()):
            raise ValueError('the raw adapter transport omits complete ordinary RAM')
        value = dict(index=index, entry=case['entry'], context=test_stock_abi.words(context),
            exit=test_stock_abi.words(out[:80]), sp=int.from_bytes(out[80:84], 'big'),
            continuation=int.from_bytes(out[84:88], 'big'),
            abi_before=test_stock_abi.words(out[88:136]), abi_after=test_stock_abi.words(out[136:184]),
            frame_before=out[184:376], frame_after=out[376:568], sr_before=int.from_bytes(out[568:572], 'big'),
            memory_before=(ram['ram_before'],), memory_after=(ram['ram_after'],), **spans)
        if adapter['bound']:
            for name in ('bound_before', 'bound_after'):
                value[name] = test_stock_abi.raw(row[name], bound_size)
        parsed.append(value)
    if not test_contract.exact(packet.get('observations'), rows):
        raise ValueError('the raw adapter transport substitutes decoded rows for its actual stdout')
    marker = f'{adapter["marker"]} status=PASS region={adapter["region"]} cases={len(parsed)}'
    if packet.get('marker') != marker or packet['stdout'].splitlines().count(marker) != 1:
        raise ValueError('the raw adapter transport lacks its unique complete invocation marker')
    return parsed
