"""Shared structural refusal sources; domain consumers retain semantic tests."""

from copy import deepcopy
import json

import pytest

from kb import proof_adapter, proof_transport


def require_descriptor_refusals(adapter):
    faults = []
    value = deepcopy(adapter);value['profile'] = 'partial-registers';faults.append(value)
    value = deepcopy(adapter);value['fields'][0]['name'] = 'expected_output';faults.append(value)
    value = deepcopy(adapter);value['fields'][0]['bits'] = 0;faults.append(value)
    value = deepcopy(adapter);value['fields'][0]['bits'] = True;faults.append(value)
    value = deepcopy(adapter);value['memory'].append(deepcopy(value['memory'][0]));faults.append(value)
    value = deepcopy(adapter);value['memory'][0]['offset'] = 65536;faults.append(value)
    value = deepcopy(adapter);value['calibration'][0]['size'] = 0;faults.append(value)
    value = deepcopy(adapter);value['dependencies'].append('../outside.py');faults.append(value)
    value = deepcopy(adapter);value['entries'].append(value['entries'][0]);faults.append(value)
    value = deepcopy(adapter);value['entries'][0] = True;faults.append(value)
    value = deepcopy(adapter);value['driver'] = '/tmp/driver.c';faults.append(value)
    value = deepcopy(adapter);value['terminal'] = {};faults.append(value)
    for value in faults:
        with pytest.raises(ValueError):
            proof_adapter.validate(value)


def _synthetic(adapter):
    case = dict(entry=adapter['entries'][0])
    if adapter['kind']['field'] == 'kind':
        case['kind'] = adapter['kind']['values'][0]
    declared = dict(cases=[case], calibration_spans=
        [[row['address'], row['size']] for row in adapter['calibration']])
    row = dict(schema=1, index=0, kind=0, entry=case['entry'],
        context=bytes(80).hex(), context_after=bytes(80).hex(), observation=bytes(572).hex(),
        ram_before='65536:a5', ram_after='65536:a5',
        calibration_before=bytes(sum(item['size'] for item in adapter['calibration'])).hex(),
        calibration_after=bytes(sum(item['size'] for item in adapter['calibration'])).hex())
    if adapter['bound']:
        declared['bound_spans'] = [[item['address'], item['size']] for item in adapter['bound']]
        row.update(bound_before=bytes(sum(item['size'] for item in adapter['bound'])).hex(),
            bound_after=bytes(sum(item['size'] for item in adapter['bound'])).hex())
    return declared, row


def _packet(adapter, row):
    marker = f'{adapter["marker"]} status=PASS region={adapter["region"]} cases=1'
    return dict(stdout=adapter['prefix']+json.dumps(row)+'\n'+marker+'\n',
        observations=[row], marker=marker)


def require_transport_refusals(adapter):
    declared, row = _synthetic(adapter)
    # A structural decode supplies no domain admission, even for a complete packet.
    proof_transport.decode(_packet(adapter, row), declared, adapter)
    for key in row:
        value = deepcopy(row);value.pop(key)
        with pytest.raises(ValueError):
            proof_transport.decode(_packet(adapter, value), declared, adapter)
    for key, replacement in (('schema', True), ('index', True), ('kind', True),
            ('entry', adapter['entries'][0]+2), ('context', '00'),
            ('context_after', '01'*80), ('observation', '00'*571),
            ('ram_before', '65535:a5'), ('ram_after', '65535:a5'),
            ('calibration_before', '00'), ('calibration_after', '00')):
        value = deepcopy(row);value[key] = replacement
        with pytest.raises(ValueError):
            proof_transport.decode(_packet(adapter, value), declared, adapter)
    value = deepcopy(row);value['expected_output'] = 0
    with pytest.raises(ValueError):
        proof_transport.decode(_packet(adapter, value), declared, adapter)
    packet = _packet(adapter, row)
    packet['stdout'] = packet['stdout'].replace('{', '{"schema":1,', 1)
    with pytest.raises(ValueError):
        proof_transport.decode(packet, declared, adapter)
    packet = _packet(adapter, row);packet['observations'] = []
    with pytest.raises(ValueError):
        proof_transport.decode(packet, declared, adapter)
    packet = _packet(adapter, row);packet['stdout'] += packet['marker']+'\n'
    with pytest.raises(ValueError):
        proof_transport.decode(packet, declared, adapter)
