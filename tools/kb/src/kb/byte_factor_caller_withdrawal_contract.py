"""Exact natural byte factor caller withdrawal paths, literal inputs and declared pointer aliases."""

import hashlib
import json
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.byte-factor-caller-withdrawal-paths.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
ENTRIES=(309832,)
UNIT={'assembly': 'tools/sh-elf-run/stock_jk08a_byte_factor_caller_withdrawal.s',
 'code': [{'start': 156528, 'end': 156546},
          {'start': 157504, 'end': 157550},
          {'start': 158304, 'end': 158394},
          {'start': 309832, 'end': 309858},
          {'start': 309860, 'end': 310122}],
 'pools': [{'address': 34923, 'size': 1, 'stock_hex': '00'},
           {'address': 34925, 'size': 1, 'stock_hex': '00'},
           {'address': 156546, 'size': 2, 'stock_hex': '00e0'},
           {'address': 156548, 'size': 4, 'stock_hex': '00026a80'},
           {'address': 158396, 'size': 4, 'stock_hex': '00026740'},
           {'address': 309858, 'size': 2, 'stock_hex': '03cb'},
           {'address': 310178, 'size': 2, 'stock_hex': '0370'},
           {'address': 310180, 'size': 2, 'stock_hex': '0372'},
           {'address': 310182, 'size': 2, 'stock_hex': '03cb'},
           {'address': 310184, 'size': 2, 'stock_hex': '03cd'},
           {'address': 310186, 'size': 2, 'stock_hex': '03cc'},
           {'address': 310340, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 310344, 'size': 4, 'stock_hex': 'ffff1024'},
           {'address': 310352, 'size': 4, 'stock_hex': '00026370'},
           {'address': 310356, 'size': 4, 'stock_hex': 'ffff119c'},
           {'address': 310372, 'size': 4, 'stock_hex': 'ffff2470'},
           {'address': 310380, 'size': 4, 'stock_hex': '0000886b'},
           {'address': 310384, 'size': 4, 'stock_hex': 'ffff2458'},
           {'address': 310388, 'size': 4, 'stock_hex': '000126a0'}],
 'aliases': [{'address': 310340, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 310344, 'width': 4, 'original': 4294905892, 'alias': 16781348},
             {'address': 310356, 'width': 4, 'original': 4294906268, 'alias': 16781724},
             {'address': 310372, 'width': 4, 'original': 4294911088, 'alias': 16786544},
             {'address': 310384, 'width': 4, 'original': 4294911064, 'alias': 16786520}]}
CONTROLLED_CALIBRATION=[{'address': 34923, 'size': 1},
 {'address': 34925, 'size': 1},
 {'address': 75424, 'size': 16},
 {'address': 156546, 'size': 2},
 {'address': 156548, 'size': 4},
 {'address': 158396, 'size': 4},
 {'address': 309858, 'size': 2},
 {'address': 310178, 'size': 2},
 {'address': 310180, 'size': 2},
 {'address': 310182, 'size': 2},
 {'address': 310184, 'size': 2},
 {'address': 310186, 'size': 2},
 {'address': 310340, 'size': 4},
 {'address': 310344, 'size': 4},
 {'address': 310352, 'size': 4},
 {'address': 310356, 'size': 4},
 {'address': 310372, 'size': 4},
 {'address': 310380, 'size': 4},
 {'address': 310384, 'size': 4},
 {'address': 310388, 'size': 4}]
BOUND_SPANS=({'address': 156528, 'size': 18},
 {'address': 157504, 'size': 46},
 {'address': 158304, 'size': 90},
 {'address': 309832, 'size': 26},
 {'address': 309860, 'size': 262},
 {'address': 34923, 'size': 1},
 {'address': 34925, 'size': 1},
 {'address': 75424, 'size': 16},
 {'address': 156546, 'size': 2},
 {'address': 156548, 'size': 4},
 {'address': 158396, 'size': 4},
 {'address': 309858, 'size': 2},
 {'address': 310178, 'size': 2},
 {'address': 310180, 'size': 2},
 {'address': 310182, 'size': 2},
 {'address': 310184, 'size': 2},
 {'address': 310186, 'size': 2},
 {'address': 310340, 'size': 4},
 {'address': 310344, 'size': 4},
 {'address': 310352, 'size': 4},
 {'address': 310356, 'size': 4},
 {'address': 310372, 'size': 4},
 {'address': 310380, 'size': 4},
 {'address': 310384, 'size': 4},
 {'address': 310388, 'size': 4})
FLAGS=('native_identity_admission',
 'native_geometry_inference',
 'scale_admission',
 'units_admission',
 'natural_caller_reachability',
 'hardware_qualification',
 'stock_function_stubs',
 'native_publication')
CONFIGURATION=[{'address': 34923, 'field': 'config_886b', 'size': 1},
 {'address': 34925, 'field': 'config_886d', 'size': 1},
 {'address': 75424, 'field': 'curve_value_0', 'size': 1},
 {'address': 75425, 'field': 'curve_value_1', 'size': 1},
 {'address': 75426, 'field': 'curve_value_2', 'size': 1},
 {'address': 75427, 'field': 'curve_value_3', 'size': 1},
 {'address': 75428, 'field': 'curve_value_4', 'size': 1},
 {'address': 75429, 'field': 'curve_value_5', 'size': 1},
 {'address': 75430, 'field': 'curve_value_6', 'size': 1},
 {'address': 75431, 'field': 'curve_value_7', 'size': 1},
 {'address': 75432, 'field': 'curve_value_8', 'size': 1},
 {'address': 75433, 'field': 'curve_value_9', 'size': 1},
 {'address': 75434, 'field': 'curve_value_10', 'size': 1},
 {'address': 75435, 'field': 'curve_value_11', 'size': 1},
 {'address': 75436, 'field': 'curve_value_12', 'size': 1},
 {'address': 75437, 'field': 'curve_value_13', 'size': 1},
 {'address': 75438, 'field': 'curve_value_14', 'size': 1},
 {'address': 75439, 'field': 'curve_value_15', 'size': 1}]
INPUT_BLOBS=[{'name': 'curve_value_bytes', 'address': 75424, 'size': 16}]
ADAPTER_SHA256='d42e79fcfe20c0f26854c89e8d50149be3d1adc60b0ed5a66799c6fb03ea9871'
HELPER_ENTRIES=(156528, 158304, 157504)
REUSED_HELPER_FILES_SHA256={'defs/JK08A.byte-curve-caller-withdrawal-paths.toml': 'eef3bb053ec07819d675547b5667b0a188cbc0343643f318db8100ffe15e65c7',
 'tools/sh-elf-run/stock_jk08a_byte_curve_caller_withdrawal.s': '2042cd93ebd162de58c83323ba6477a37d5110a211b6d7755425dc33d6bd3c21',
 'tools/kb/src/kb/byte_curve_caller_withdrawal_contract.py': 'aaaee28de43a668abbaf7ab4d1d0288eeedfbd7c19436dc78103dbb62d52c5dc',
 'tools/kb/src/kb/byte_curve_caller_withdrawal_matrix.py': '3afd1bda60c112551d18e8fecb2197982f99550e94d97d0c63b7feec58a5e035',
 'tools/kb/src/kb/byte_curve_caller_withdrawal_semantics.py': 'c334890fab9b66321bd6643a49020116babe6911b8dbc433dde9ff63b7cea56b',
 'tools/kb/src/kb/byte_curve_caller_withdrawal_transfers.py': '45176f0d29df994a923a215650f4e5f752fee320a74dad5e38f7f3f9dae377a6',
 'tools/kb/src/kb/byte_curve_caller_withdrawal_capture_evidence.py': '56ac55bef74315fc665cc1bb1ecb9e316e1e5738f96615fc15b440f2088aa49d',
 'tools/sh-elf-run/byte_curve_caller_withdrawal_capture.py': 'c3005baae784087eb3602f4bb2264a10131b8b978ba920c742d47103bfa3d931'}
FUNCTIONS=(*ENTRIES,*HELPER_ENTRIES)
SPANS=tuple((row['start'],row['end']) for row in UNIT['code'])


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','entries','observer',
            'context_bytes','frame_bytes','frame_prefix','unit','controlled_calibration','configuration','input_blobs','adapter',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-byte-factor-caller-withdrawal'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or not test_contract.exact((value['entries'],value['observer'],value['context_bytes'],value['frame_bytes'],
                value['frame_prefix']),(list(ENTRIES),OBSERVER,80,192,160))
            or any(value[name] is not False for name in FLAGS)
            or not test_contract.exact(value['unit'],UNIT)
            or not test_contract.exact(value['controlled_calibration'],CONTROLLED_CALIBRATION)
            or not test_contract.exact(value['configuration'],CONFIGURATION)
            or not test_contract.exact(value['input_blobs'],INPUT_BLOBS)
            or hashlib.sha256(json.dumps(value['adapter'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=ADAPTER_SHA256):
        raise ValueError('the byte factor caller withdrawal paths change an exact natural entry, code/pool byte, alias or complete observer premise')
    require_reused_helper_boundary(root)
    return dict(value,entry=[dict(start=first,end=last) for first,last in SPANS])


def require_image(declared,image):
    if (type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256
            or not test_contract.exact(declared['unit'],UNIT)):
        raise ValueError('the byte factor caller withdrawal paths change the complete owned stock image or exact unit')
    for row in UNIT['pools']:
        if image[row['address']:row['address']+row['size']].hex()!=row['stock_hex']:
            raise ValueError('the byte factor caller withdrawal paths change a pinned exact stock pool or configuration byte')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for row in UNIT['aliases']:
        at=row['address']
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('the byte factor caller withdrawal paths relocate a different original native pointer')
        fixture[at:at+4]=row['alias'].to_bytes(4,'big');aliases.append(dict(row))
    return bytes(fixture),aliases


def fixture_for_case(declared,image,case):
    from kb import byte_factor_caller_withdrawal_matrix as matrix
    matrix.require_case(case);fixture,aliases=independent_fixture(declared,image);fixture=bytearray(fixture)
    for row in CONFIGURATION:
        at,size=row['address'],row['size'];fixture[at:at+size]=case[row['field']].to_bytes(size,'big')
    return bytes(fixture),aliases


def require_reused_helper_boundary(root):
    for name,wanted in REUSED_HELPER_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=wanted:
            raise ValueError('the byte factor caller changes a complete reused signed/unsigned division,byte-curve and standard implicit-byte source boundary')
