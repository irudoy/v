"""Raw capture refuses ABI, physical alias, invocation and packet substitutions."""

from dataclasses import replace
import importlib.util
import json
import sys
from types import SimpleNamespace

import pytest

from kb import repo, test_stock_accumulator


@pytest.fixture
def capture_module():
    name = '_kb_native_test_capture_contract'
    spec = importlib.util.spec_from_file_location(name,
        repo.ROOT / 'tools/sh-elf-run/native_test_capture.py')
    module = importlib.util.module_from_spec(spec)
    previous = sys.modules.get(name)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
        yield module
    finally:
        if previous is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous


def test_literal_capture_declaration_roundtrips_without_inferred_cases(capture_module):
    packet = test_stock_accumulator.capture_spec()
    spec = capture_module.Spec.from_packet(packet)
    assert spec.packet() == packet
    assert spec.invocations > len(spec.selected)
    assert spec.selected[0].entry == 0x554ae
    assert 'semantic_admission' not in packet


@pytest.mark.parametrize('fault', ['unknown', 'bool-size', 'float-count', 'duplicate-case', 'wrong-order'])
def test_capture_declaration_does_not_coerce_or_extend_its_schema(capture_module, fault):
    packet = test_stock_accumulator.capture_spec()
    if fault == 'unknown':
        packet['qualified'] = True
    elif fault == 'bool-size':
        packet['context_size'] = True
    elif fault == 'float-count':
        packet['invocations'] = float(packet['invocations'])
    elif fault == 'duplicate-case':
        packet['selected'].append(packet['selected'][0])
    else:
        packet['selected'].reverse()
    with pytest.raises(ValueError):
        capture_module.Spec.from_packet(packet)


def test_overlapping_aliases_cannot_name_other_physical_bytes(capture_module):
    spec = capture_module.Spec.from_packet(test_stock_accumulator.capture_spec())
    forged = capture_module.Span('different_owner', 0xfffe1000, 0x01001000, 4)
    with pytest.raises(ValueError, match='different physical bytes'):
        replace(spec, spans=(*spec.spans, forged)).packet()


def test_array_member_adjacency_requires_a_compiled_array_bound(capture_module):
    spec = capture_module.Spec.from_packet(test_stock_accumulator.capture_spec())
    field = capture_module.Field('context', 'r[15]', 60, 4)
    source = capture_module.appendix(replace(spec, fields=(field,))).decode()
    assert '15U < sizeof(((struct context *)0)->r)' in source
    assert 'native TEST field array bound' in source
    assert 'offsetof(struct context, r[15]) == 60U' in source


def test_capture_session_refuses_reserved_protocol_and_repeated_original(capture_module):
    spec = capture_module.Spec.from_packet(test_stock_accumulator.capture_spec())
    region = SimpleNamespace(key=spec.region, cases=spec.invocations, code_spans=((0x554ae, 0x554f0),))
    session = capture_module.Session((spec,))
    with pytest.raises(ValueError, match='existing primary witness'):
        session.bind((region,), {spec.region: 'stock_oneshot_invoke.s'}, {spec.region})
    session.bind((region,), {spec.region: 'stock_oneshot_invoke.s'}, set())
    assert session.select(region) is spec
    with pytest.raises(ValueError, match='one original stock invocation'):
        session.bind((region,), {spec.region: 'stock_oneshot_invoke.s'}, set())
    with pytest.raises(ValueError, match='omits or repeats'):
        session.finish()


def test_missing_packets_and_duplicate_json_keys_are_refused(capture_module):
    spec = capture_module.Spec.from_packet(test_stock_accumulator.capture_spec())
    with pytest.raises(ValueError, match='omits, duplicates or reorders'):
        capture_module.observe('', spec)
    packet = json.dumps(spec.abi_packet())
    packet = packet[:-1] + ', "schema":1}'
    with pytest.raises(ValueError, match='duplicate native TEST observation key'):
        capture_module.observe('vq-native-test-abi ' + packet, spec)
