"""Exact complete diagnostic-record high-bit clearer and explicit ordinary-memory premises."""
import hashlib
import json
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.diagnostic-record-highbit-clear-paths.toml'
DECLARED = {'schema': 1,
 'id': 'jk08a-diagnostic-record-highbit-clear',
 'layout': '7mfk',
 'rom': 'JK08A',
 'image_sha256': 'ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23',
 'scope': 'Complete natural 0008C348, full raw R4 arithmetic, inert -1 sentinel and actual indexed byte '
          'AND7F publication in its RTS delay slot. Explicit observations do not infer an API index '
          'bound, array extent or natural caller reachability.',
 'entries': [574280],
 'observer': 'tools/sh-elf-run/stock_ignition_consumer_invoke.s',
 'context_bytes': 80,
 'frame_bytes': 192,
 'frame_prefix': 160,
 'unit': {'assembly': 'tools/sh-elf-run/stock_jk08a_diagnostic_record_highbit_clear.s',
          'code': [{'start': 574280, 'end': 574310}],
          'pools': [{'address': 574556, 'size': 4, 'stock_hex': 'ffff5718'}],
          'aliases': [{'address': 574556, 'width': 4, 'original': 4294924056, 'alias': 16799512}]},
 'controlled_calibration': [{'address': 574556, 'size': 4}],
 'bound_spans': [{'address': 574280, 'size': 30}, {'address': 574556, 'size': 4}],
 'configuration': [],
 'explicit_raw_R4_inputs': [0, 1, 71, 210, 211, 291, 342, 2863311531, 1431655765, 4294967295],
 'adapter': {'schema': 1,
             'profile': 'ordinary-80-572',
             'symbol': 'diagnostic_record_highbit_clear',
             'region': 'jk08a-diagnostic-record-highbit-clear-paths',
             'prefix': 'kb-diagnostic-record-highbit-clear-observation ',
             'marker': 'VQ_SH_ELF_DIAGNOSTIC_RECORD_HIGHBIT_CLEAR',
             'header': 'diagnostic-record-highbit-clear-cases.h',
             'driver': 'tools/sh-elf-run/harness-diagnostic-record-highbit-clear-paths.c',
             'refusals': 'tools/kb/tests/test_diagnostic_record_highbit_clear_adapter_generated.py',
             'fields': [{'name': 'raw_r0', 'bits': 32},
                        {'name': 'raw_r1', 'bits': 32},
                        {'name': 'raw_r2', 'bits': 32},
                        {'name': 'raw_r3', 'bits': 32},
                        {'name': 'raw_r4', 'bits': 32},
                        {'name': 'raw_r5', 'bits': 32},
                        {'name': 'raw_r6', 'bits': 32},
                        {'name': 'raw_r7', 'bits': 32},
                        {'name': 'record_000_0', 'bits': 8},
                        {'name': 'record_000_1', 'bits': 8},
                        {'name': 'record_000_2', 'bits': 8},
                        {'name': 'record_001_0', 'bits': 8},
                        {'name': 'record_001_1', 'bits': 8},
                        {'name': 'record_001_2', 'bits': 8},
                        {'name': 'record_047_0', 'bits': 8},
                        {'name': 'record_047_1', 'bits': 8},
                        {'name': 'record_047_2', 'bits': 8},
                        {'name': 'record_0d2_0', 'bits': 8},
                        {'name': 'record_0d2_1', 'bits': 8},
                        {'name': 'record_0d2_2', 'bits': 8},
                        {'name': 'record_0d3_0', 'bits': 8},
                        {'name': 'record_0d3_1', 'bits': 8},
                        {'name': 'record_0d3_2', 'bits': 8},
                        {'name': 'record_123_0', 'bits': 8},
                        {'name': 'record_123_1', 'bits': 8},
                        {'name': 'record_123_2', 'bits': 8},
                        {'name': 'record_156_0', 'bits': 8},
                        {'name': 'record_156_1', 'bits': 8},
                        {'name': 'record_156_2', 'bits': 8},
                        {'name': 'variant', 'bits': 8},
                        {'name': 'initial_sr', 'bits': 10}],
             'entries': [574280],
             'kind': {'field': 'entry', 'values': [574280]},
             'memory': [{'offset': 22296, 'width': 1, 'field': 'record_000_0'},
                        {'offset': 22297, 'width': 1, 'field': 'record_000_1'},
                        {'offset': 22298, 'width': 1, 'field': 'record_000_2'},
                        {'offset': 22299, 'width': 1, 'field': 'record_001_0'},
                        {'offset': 22300, 'width': 1, 'field': 'record_001_1'},
                        {'offset': 22301, 'width': 1, 'field': 'record_001_2'},
                        {'offset': 22509, 'width': 1, 'field': 'record_047_0'},
                        {'offset': 22510, 'width': 1, 'field': 'record_047_1'},
                        {'offset': 22511, 'width': 1, 'field': 'record_047_2'},
                        {'offset': 22926, 'width': 1, 'field': 'record_0d2_0'},
                        {'offset': 22927, 'width': 1, 'field': 'record_0d2_1'},
                        {'offset': 22928, 'width': 1, 'field': 'record_0d2_2'},
                        {'offset': 22929, 'width': 1, 'field': 'record_0d3_0'},
                        {'offset': 22930, 'width': 1, 'field': 'record_0d3_1'},
                        {'offset': 22931, 'width': 1, 'field': 'record_0d3_2'},
                        {'offset': 23169, 'width': 1, 'field': 'record_123_0'},
                        {'offset': 23170, 'width': 1, 'field': 'record_123_1'},
                        {'offset': 23171, 'width': 1, 'field': 'record_123_2'},
                        {'offset': 23322, 'width': 1, 'field': 'record_156_0'},
                        {'offset': 23323, 'width': 1, 'field': 'record_156_1'},
                        {'offset': 23324, 'width': 1, 'field': 'record_156_2'}],
             'calibration': [{'address': 574556, 'size': 4}],
             'calibration_input': False,
             'bound': [{'address': 574280, 'size': 30}, {'address': 574556, 'size': 4}],
             'dependencies': ['defs/JK08A.diagnostic-record-highbit-clear-paths.toml',
                              'defs/JK08A.diagnostic-record-highbit-clear.md',
                              'defs/JK08A.diagnostic-record-bit4-claims.toml',
                              'tools/sh-elf-run/stock_jk08a_diagnostic_record_highbit_clear.s',
                              'tools/sh-elf-run/stock_ignition_consumer_invoke.s',
                              'tools/sh-elf-run/diagnostic_record_highbit_clear_capture.py',
                              'tools/kb/src/kb/diagnostic_record_highbit_clear_contract.py',
                              'tools/kb/src/kb/diagnostic_record_highbit_clear_matrix.py',
                              'tools/kb/src/kb/diagnostic_record_highbit_clear_semantics.py',
                              'tools/kb/src/kb/diagnostic_record_highbit_clear_transfers.py',
                              'tools/kb/src/kb/diagnostic_record_highbit_clear_capture_evidence.py',
                              'tools/kb/tests/test_diagnostic_record_highbit_clear_contract.py',
                              'tools/kb/tests/test_diagnostic_record_highbit_clear_capture_evidence.py',
                              'tools/kb/tests/test_diagnostic_record_highbit_clear_access.py',
                              'tools/kb/src/kb/diagnostic_record_bit4_access_contract.py',
                              'tools/kb/src/kb/diagnostic_record_bit4_access_evidence.py',
                              'tools/kb/src/kb/diagnostic_record_bit4_access_resolution.py',
                              'tools/kb/src/kb/byte_surface_equations.py',
                              'tools/kb/src/kb/packed_transfer_evidence.py',
                              'tools/kb/src/kb/test_stock_capture.py',
                              'tools/kb/src/kb/ignition_literal_evidence.py',
                              'tools/kb/src/kb/test_contract.py']},
 'native_identity_admission': False,
 'native_geometry_inference': False,
 'scale_admission': False,
 'units_admission': False,
 'natural_caller_reachability': False,
 'natural_scheduling_inference': False,
 'hardware_qualification': False,
 'stock_function_stubs': False,
 'native_publication': False}

ENTRY=0x8C348
ENTRIES=(ENTRY,)
FUNCTIONS=ENTRIES
SPANS=((ENTRY,0x8C366),)
UNIT=DECLARED['unit']
ASSEMBLY=UNIT['assembly']
OBSERVER=DECLARED['observer']
CONTROLLED_CALIBRATION=DECLARED['controlled_calibration']
BOUND_SPANS=DECLARED['bound_spans']
CONFIGURATION=[]
INDICES=tuple(DECLARED['explicit_raw_R4_inputs'])
IMAGE_SHA256=DECLARED['image_sha256']
FLAGS=tuple(key for key,value in DECLARED.items() if value is False)

def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if not test_contract.exact(value,DECLARED):
        raise ValueError('the high-bit clearer changes its exact image, complete function, pools, index premises or input-only observer')
    return dict(value,entry=[dict(start=first,end=last) for first,last in SPANS])

def require_image(declared,image):
    if (type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256
            or not test_contract.exact(declared['unit'],UNIT)):
        raise ValueError('the high-bit clearer changes its complete owned image or declared natural unit')
    if image[ENTRY:0x8C366].hex()!='d144604388ff8908661362434200324c362c8461c97f000b8061000b0009':
        raise ValueError('the high-bit clearer changes an exact complete stock instruction')
    for row in UNIT['pools']:
        if image[row['address']:row['address']+row['size']].hex()!=row['stock_hex']:
            raise ValueError('the high-bit clearer changes an exact stock PC operand')

def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for row in UNIT['aliases']:
        at=row['address']
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('the high-bit clearer aliases a different native pointer')
        fixture[at:at+4]=row['alias'].to_bytes(4,'big');aliases.append(dict(row))
    return bytes(fixture),aliases

def fixture_for_case(declared,image,case):
    from kb import diagnostic_record_highbit_clear_matrix as matrix
    matrix.require_case(case)
    return independent_fixture(declared,image)
