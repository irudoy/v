"""Exact complete diagnostic-record composite gate and explicit ordinary-memory premises."""
import hashlib
import json
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.diagnostic-record-composite-gate-paths.toml'
DECLARED = {'schema': 1,
 'id': 'jk08a-diagnostic-record-composite-gate',
 'layout': '7mfk',
 'rom': 'JK08A',
 'image_sha256': 'ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23',
 'scope': 'Complete 00025A12 short-circuit indexed diagnostic-record reader and full 000259E4 predicate, '
          'including two actual sentinel calls, exact delayed arguments, complete CPU/SR/frame/RAM and '
          'natural returns.',
 'entries': [154130],
 'observer': 'tools/sh-elf-run/stock_ignition_consumer_invoke.s',
 'context_bytes': 80,
 'frame_bytes': 192,
 'frame_prefix': 160,
 'unit': {'assembly': 'tools/sh-elf-run/stock_jk08a_diagnostic_record_composite_gate.s',
          'code': [{'start': 154084, 'end': 154130}, {'start': 154130, 'end': 154252}],
          'pools': [{'address': 154520, 'size': 4, 'stock_hex': 'ffff5718'}],
          'aliases': [{'address': 154520, 'width': 4, 'original': 4294924056, 'alias': 16799512}]},
 'controlled_calibration': [{'address': 154520, 'size': 4}],
 'bound_spans': [{'address': 154084, 'size': 46},
                 {'address': 154130, 'size': 122},
                 {'address': 154520, 'size': 4}],
 'configuration': [],
 'index_premise': [20, 71, 72, 73, 74, 75, 76, 138, 139, 140],
 'adapter': {'schema': 1,
             'profile': 'ordinary-80-572',
             'symbol': 'diagnostic_record_composite_gate',
             'region': 'jk08a-diagnostic-record-composite-gate-paths',
             'prefix': 'kb-diagnostic-record-composite-gate-observation ',
             'marker': 'VQ_SH_ELF_DIAGNOSTIC_RECORD_COMPOSITE_GATE',
             'header': 'diagnostic-record-composite-gate-cases.h',
             'driver': 'tools/sh-elf-run/harness-diagnostic-record-composite-gate-paths.c',
             'refusals': 'tools/kb/tests/test_diagnostic_record_composite_gate_adapter_generated.py',
             'fields': [{'name': 'raw_r0', 'bits': 32},
                        {'name': 'raw_r1', 'bits': 32},
                        {'name': 'raw_r2', 'bits': 32},
                        {'name': 'raw_r3', 'bits': 32},
                        {'name': 'raw_r4', 'bits': 32},
                        {'name': 'raw_r5', 'bits': 32},
                        {'name': 'raw_r6', 'bits': 32},
                        {'name': 'raw_r7', 'bits': 32},
                        {'name': 'record_014_0', 'bits': 8},
                        {'name': 'record_014_1', 'bits': 8},
                        {'name': 'record_014_2', 'bits': 8},
                        {'name': 'record_047_0', 'bits': 8},
                        {'name': 'record_047_1', 'bits': 8},
                        {'name': 'record_047_2', 'bits': 8},
                        {'name': 'record_048_0', 'bits': 8},
                        {'name': 'record_048_1', 'bits': 8},
                        {'name': 'record_048_2', 'bits': 8},
                        {'name': 'record_049_0', 'bits': 8},
                        {'name': 'record_049_1', 'bits': 8},
                        {'name': 'record_049_2', 'bits': 8},
                        {'name': 'record_04a_0', 'bits': 8},
                        {'name': 'record_04a_1', 'bits': 8},
                        {'name': 'record_04a_2', 'bits': 8},
                        {'name': 'record_04b_0', 'bits': 8},
                        {'name': 'record_04b_1', 'bits': 8},
                        {'name': 'record_04b_2', 'bits': 8},
                        {'name': 'record_04c_0', 'bits': 8},
                        {'name': 'record_04c_1', 'bits': 8},
                        {'name': 'record_04c_2', 'bits': 8},
                        {'name': 'record_08a_0', 'bits': 8},
                        {'name': 'record_08a_1', 'bits': 8},
                        {'name': 'record_08a_2', 'bits': 8},
                        {'name': 'record_08b_0', 'bits': 8},
                        {'name': 'record_08b_1', 'bits': 8},
                        {'name': 'record_08b_2', 'bits': 8},
                        {'name': 'record_08c_0', 'bits': 8},
                        {'name': 'record_08c_1', 'bits': 8},
                        {'name': 'record_08c_2', 'bits': 8},
                        {'name': 'variant', 'bits': 8},
                        {'name': 'initial_sr', 'bits': 10}],
             'entries': [154130],
             'kind': {'field': 'entry', 'values': [154130]},
             'memory': [{'offset': 22356, 'width': 1, 'field': 'record_014_0'},
                        {'offset': 22357, 'width': 1, 'field': 'record_014_1'},
                        {'offset': 22358, 'width': 1, 'field': 'record_014_2'},
                        {'offset': 22509, 'width': 1, 'field': 'record_047_0'},
                        {'offset': 22510, 'width': 1, 'field': 'record_047_1'},
                        {'offset': 22511, 'width': 1, 'field': 'record_047_2'},
                        {'offset': 22512, 'width': 1, 'field': 'record_048_0'},
                        {'offset': 22513, 'width': 1, 'field': 'record_048_1'},
                        {'offset': 22514, 'width': 1, 'field': 'record_048_2'},
                        {'offset': 22515, 'width': 1, 'field': 'record_049_0'},
                        {'offset': 22516, 'width': 1, 'field': 'record_049_1'},
                        {'offset': 22517, 'width': 1, 'field': 'record_049_2'},
                        {'offset': 22518, 'width': 1, 'field': 'record_04a_0'},
                        {'offset': 22519, 'width': 1, 'field': 'record_04a_1'},
                        {'offset': 22520, 'width': 1, 'field': 'record_04a_2'},
                        {'offset': 22521, 'width': 1, 'field': 'record_04b_0'},
                        {'offset': 22522, 'width': 1, 'field': 'record_04b_1'},
                        {'offset': 22523, 'width': 1, 'field': 'record_04b_2'},
                        {'offset': 22524, 'width': 1, 'field': 'record_04c_0'},
                        {'offset': 22525, 'width': 1, 'field': 'record_04c_1'},
                        {'offset': 22526, 'width': 1, 'field': 'record_04c_2'},
                        {'offset': 22710, 'width': 1, 'field': 'record_08a_0'},
                        {'offset': 22711, 'width': 1, 'field': 'record_08a_1'},
                        {'offset': 22712, 'width': 1, 'field': 'record_08a_2'},
                        {'offset': 22713, 'width': 1, 'field': 'record_08b_0'},
                        {'offset': 22714, 'width': 1, 'field': 'record_08b_1'},
                        {'offset': 22715, 'width': 1, 'field': 'record_08b_2'},
                        {'offset': 22716, 'width': 1, 'field': 'record_08c_0'},
                        {'offset': 22717, 'width': 1, 'field': 'record_08c_1'},
                        {'offset': 22718, 'width': 1, 'field': 'record_08c_2'}],
             'calibration': [{'address': 154520, 'size': 4}],
             'calibration_input': False,
             'bound': [{'address': 154084, 'size': 46},
                       {'address': 154130, 'size': 122},
                       {'address': 154520, 'size': 4}],
             'dependencies': ['defs/JK08A.diagnostic-record-composite-gate-paths.toml',
                              'defs/JK08A.diagnostic-record-bit4-claims.toml',
                              'defs/JK08A.diagnostic-record-composite-gate.md',
                              'tools/sh-elf-run/stock_jk08a_diagnostic_record_composite_gate.s',
                              'tools/sh-elf-run/stock_ignition_consumer_invoke.s',
                              'tools/sh-elf-run/diagnostic_record_composite_gate_capture.py',
                              'tools/kb/src/kb/diagnostic_record_composite_gate_contract.py',
                              'tools/kb/src/kb/diagnostic_record_composite_gate_matrix.py',
                              'tools/kb/src/kb/diagnostic_record_composite_gate_semantics.py',
                              'tools/kb/src/kb/diagnostic_record_composite_gate_transfers.py',
                              'tools/kb/src/kb/diagnostic_record_composite_gate_capture_evidence.py',
                              'tools/kb/src/kb/diagnostic_record_composite_gate_access_contract.py',
                              'tools/kb/src/kb/diagnostic_record_composite_gate_access_evidence.py',
                              'tools/kb/src/kb/diagnostic_record_composite_gate_access_resolution.py',
                              'tools/kb/tests/test_diagnostic_record_composite_gate_contract.py',
                              'tools/kb/tests/test_diagnostic_record_composite_gate_capture_evidence.py',
                              'tools/kb/tests/test_diagnostic_record_composite_gate_access.py',
                              'tools/kb/src/kb/byte_surface_equations.py',
                              'tools/kb/src/kb/packed_transfer_evidence.py',
                              'tools/kb/src/kb/test_stock_capture.py',
                              'tools/kb/src/kb/ignition_literal_evidence.py',
                              'tools/kb/src/kb/test_contract.py',
                              'tools/kb/tests/test_diagnostic_record_composite_gate_access.py']},
 'native_identity_admission': False,
 'native_geometry_inference': False,
 'scale_admission': False,
 'units_admission': False,
 'natural_caller_reachability': False,
 'natural_scheduling_inference': False,
 'hardware_qualification': False,
 'stock_function_stubs': False,
 'native_publication': False}

ENTRY=0x25A12
ENTRIES=(ENTRY,)
FUNCTIONS=(ENTRY,0x259E4)
SPANS=((0x259E4,0x25A12),(ENTRY,0x25A8C))
UNIT=DECLARED['unit']
ASSEMBLY=UNIT['assembly']
OBSERVER=DECLARED['observer']
CONTROLLED_CALIBRATION=DECLARED['controlled_calibration']
BOUND_SPANS=DECLARED['bound_spans']
CONFIGURATION=[]
INDICES=tuple(DECLARED['index_premise'])
IMAGE_SHA256=DECLARED['image_sha256']
FLAGS=tuple(key for key,value in DECLARED.items() if value is False)

def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if not test_contract.exact(value,DECLARED):
        raise ValueError('the composite gate changes its exact image, complete function, pools, index premises or input-only observer')
    return dict(value,entry=[dict(start=first,end=last) for first,last in SPANS])

def require_image(declared,image):
    if (type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256
            or not test_contract.exact(declared['unit'],UNIT)):
        raise ValueError('the composite gate changes its complete owned image or declared natural unit')
    for first,last,expected in STOCK_CODE:
        if image[first:last].hex()!=expected:
            raise ValueError('the composite gate changes an exact complete natural caller or helper instruction')
    for row in UNIT['pools']:
        if image[row['address']:row['address']+row['size']].hex()!=row['stock_hex']:
            raise ValueError('the composite gate changes an exact stock PC operand')

def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for row in UNIT['aliases']:
        at=row['address']
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('the composite gate aliases a different native pointer')
        fixture[at:at+4]=row['alias'].to_bytes(4,'big');aliases.append(dict(row))
    return bytes(fixture),aliases

def fixture_for_case(declared,image,case):
    from kb import diagnostic_record_composite_gate_matrix as matrix
    matrix.require_case(case)
    return independent_fixture(declared,image)

STOCK_CODE = ((154084,
  154130,
  'd16c604f88ff890f670347006213370c327c8422c8408f08e5016213327c8422c8208b02a001e500e500000b6053'),
 (154130,
  154252,
  '4f22bfe6e4ff20088b33bfe2e4ff20088b2fbfdee41420088b2bbfdae44720088b27bfd6e44820088b23bfd2e44920088b1fbfcee44a20088b1bbfcae44b20088b17bfc6e44c20088b13e38a643cbfc0000920088b0de38b643cbfba000920088b07e38c643cbfb4000920088b01a001e200e2014f26000b6023'))
