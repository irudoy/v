"""Exact complete diagnostic-record bit4 writer and explicit ordinary-memory premises."""
import hashlib
import json
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.diagnostic-record-bit4-paths.toml'
DECLARED = {'schema': 1,
 'id': 'jk08a-diagnostic-record-bit4',
 'layout': '7mfk',
 'rom': 'JK08A',
 'image_sha256': 'ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23',
 'scope': 'Complete 0008C968 direct entry with explicit full-R4 indices; exact indexed third-byte OR 0x10 '
          'and natural RTS-delay FFFF508C byte publication. Existing array identity and native facts remain '
          'fixed.',
 'entries': [575848],
 'observer': 'tools/sh-elf-run/stock_ignition_consumer_invoke.s',
 'context_bytes': 80,
 'frame_bytes': 192,
 'frame_prefix': 160,
 'unit': {'assembly': 'tools/sh-elf-run/stock_jk08a_diagnostic_record_bit4.s',
          'code': [{'start': 575848, 'end': 575876}],
          'pools': [{'address': 575880, 'size': 2, 'stock_hex': '0b34'},
                    {'address': 575884, 'size': 4, 'stock_hex': 'ffff5718'},
                    {'address': 575896, 'size': 4, 'stock_hex': 'ffff4558'}],
          'aliases': [{'address': 575884, 'width': 4, 'original': 4294924056, 'alias': 16799512},
                      {'address': 575896, 'width': 4, 'original': 4294919512, 'alias': 16794968}]},
 'controlled_calibration': [{'address': 575880, 'size': 2},
                            {'address': 575884, 'size': 4},
                            {'address': 575896, 'size': 4}],
 'bound_spans': [{'address': 575848, 'size': 28},
                 {'address': 575880, 'size': 2},
                 {'address': 575884, 'size': 4},
                 {'address': 575896, 'size': 4}],
 'configuration': [],
 'index_premise': [0, 1, 71, 291, 296, 297, 342],
 'adapter': {'schema': 1,
             'profile': 'ordinary-80-572',
             'symbol': 'diagnostic_record_bit4',
             'region': 'jk08a-diagnostic-record-bit4-paths',
             'prefix': 'kb-diagnostic-record-bit4-observation ',
             'marker': 'VQ_SH_ELF_DIAGNOSTIC_RECORD_BIT4',
             'header': 'diagnostic-record-bit4-cases.h',
             'driver': 'tools/sh-elf-run/harness-diagnostic-record-bit4-paths.c',
             'refusals': 'tools/kb/tests/test_diagnostic_record_bit4_adapter_generated.py',
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
                        {'name': 'record_123_0', 'bits': 8},
                        {'name': 'record_123_1', 'bits': 8},
                        {'name': 'record_123_2', 'bits': 8},
                        {'name': 'record_128_0', 'bits': 8},
                        {'name': 'record_128_1', 'bits': 8},
                        {'name': 'record_128_2', 'bits': 8},
                        {'name': 'record_129_0', 'bits': 8},
                        {'name': 'record_129_1', 'bits': 8},
                        {'name': 'record_129_2', 'bits': 8},
                        {'name': 'record_156_0', 'bits': 8},
                        {'name': 'record_156_1', 'bits': 8},
                        {'name': 'record_156_2', 'bits': 8},
                        {'name': 'prior_508c', 'bits': 8},
                        {'name': 'variant', 'bits': 8},
                        {'name': 'initial_sr', 'bits': 10}],
             'entries': [575848],
             'kind': {'field': 'entry', 'values': [575848]},
             'memory': [{'offset': 22296, 'width': 1, 'field': 'record_000_0'},
                        {'offset': 22297, 'width': 1, 'field': 'record_000_1'},
                        {'offset': 22298, 'width': 1, 'field': 'record_000_2'},
                        {'offset': 22299, 'width': 1, 'field': 'record_001_0'},
                        {'offset': 22300, 'width': 1, 'field': 'record_001_1'},
                        {'offset': 22301, 'width': 1, 'field': 'record_001_2'},
                        {'offset': 22509, 'width': 1, 'field': 'record_047_0'},
                        {'offset': 22510, 'width': 1, 'field': 'record_047_1'},
                        {'offset': 22511, 'width': 1, 'field': 'record_047_2'},
                        {'offset': 23169, 'width': 1, 'field': 'record_123_0'},
                        {'offset': 23170, 'width': 1, 'field': 'record_123_1'},
                        {'offset': 23171, 'width': 1, 'field': 'record_123_2'},
                        {'offset': 23184, 'width': 1, 'field': 'record_128_0'},
                        {'offset': 23185, 'width': 1, 'field': 'record_128_1'},
                        {'offset': 23186, 'width': 1, 'field': 'record_128_2'},
                        {'offset': 23187, 'width': 1, 'field': 'record_129_0'},
                        {'offset': 23188, 'width': 1, 'field': 'record_129_1'},
                        {'offset': 23189, 'width': 1, 'field': 'record_129_2'},
                        {'offset': 23322, 'width': 1, 'field': 'record_156_0'},
                        {'offset': 23323, 'width': 1, 'field': 'record_156_1'},
                        {'offset': 23324, 'width': 1, 'field': 'record_156_2'},
                        {'offset': 20620, 'width': 1, 'field': 'prior_508c'}],
             'calibration': [{'address': 575880, 'size': 2},
                             {'address': 575884, 'size': 4},
                             {'address': 575896, 'size': 4}],
             'calibration_input': False,
             'bound': [{'address': 575848, 'size': 28},
                       {'address': 575880, 'size': 2},
                       {'address': 575884, 'size': 4},
                       {'address': 575896, 'size': 4}],
             'dependencies': ['defs/JK08A.diagnostic-record-bit4-paths.toml',
                              'defs/JK08A.diagnostic-record-bit4-claims.toml',
                              'defs/JK08A.diagnostic-record-bit4.md',
                              'tools/sh-elf-run/stock_jk08a_diagnostic_record_bit4.s',
                              'tools/sh-elf-run/stock_ignition_consumer_invoke.s',
                              'tools/sh-elf-run/diagnostic_record_bit4_capture.py',
                              'tools/kb/src/kb/diagnostic_record_bit4_contract.py',
                              'tools/kb/src/kb/diagnostic_record_bit4_matrix.py',
                              'tools/kb/src/kb/diagnostic_record_bit4_semantics.py',
                              'tools/kb/src/kb/diagnostic_record_bit4_transfers.py',
                              'tools/kb/src/kb/diagnostic_record_bit4_capture_evidence.py',
                              'tools/kb/src/kb/diagnostic_record_bit4_access_contract.py',
                              'tools/kb/src/kb/diagnostic_record_bit4_access_evidence.py',
                              'tools/kb/src/kb/diagnostic_record_bit4_access_resolution.py',
                              'tools/kb/tests/test_diagnostic_record_bit4_contract.py',
                              'tools/kb/tests/test_diagnostic_record_bit4_capture_evidence.py',
                              'tools/kb/tests/test_diagnostic_record_bit4_access.py',
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
ENTRY=0x8C968
ENTRIES=(ENTRY,)
FUNCTIONS=ENTRIES
SPANS=((ENTRY,0x8C984),)
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
        raise ValueError('the bit4 writer changes its exact image, complete function, pools, index premises or input-only observer')
    return dict(value,entry=[dict(start=first,end=last) for first,last in SPANS])

def require_image(declared,image):
    if (type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256
            or not test_contract.exact(declared['unit'],UNIT)):
        raise ValueError('the bit4 writer changes its complete owned image or declared natural unit')
    if image[ENTRY:0x8C984].hex()!='d108661362434200324c362c8462e201cb108062d6069003000b0624':
        raise ValueError('the bit4 writer changes an exact complete stock instruction')
    for row in UNIT['pools']:
        if image[row['address']:row['address']+row['size']].hex()!=row['stock_hex']:
            raise ValueError('the bit4 writer changes an exact stock PC operand')

def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for row in UNIT['aliases']:
        at=row['address']
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('the bit4 writer aliases a different native pointer')
        fixture[at:at+4]=row['alias'].to_bytes(4,'big');aliases.append(dict(row))
    return bytes(fixture),aliases

def fixture_for_case(declared,image,case):
    from kb import diagnostic_record_bit4_matrix as matrix
    matrix.require_case(case)
    return independent_fixture(declared,image)
