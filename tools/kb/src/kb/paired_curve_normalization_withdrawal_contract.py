"""Exact natural paired curve normalization caller withdrawal paths, literal inputs and declared pointer aliases."""

import hashlib
import json
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.paired-curve-normalization-withdrawal-paths.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
ENTRIES=(415156, 416520)
UNIT={'assembly': 'tools/sh-elf-run/stock_jk08a_paired_curve_normalization_withdrawal.s',
 'code': [{'start': 138172, 'end': 138454},
          {'start': 156832, 'end': 156866},
          {'start': 157504, 'end': 157550},
          {'start': 158020, 'end': 158080},
          {'start': 158840, 'end': 158990},
          {'start': 415156, 'end': 415490},
          {'start': 416520, 'end': 416806}],
 'pools': [{'address': 34576, 'size': 1, 'stock_hex': '7c'},
           {'address': 138456, 'size': 4, 'stock_hex': 'ffff9818'},
           {'address': 138460, 'size': 4, 'stock_hex': '0000044e'},
           {'address': 156868, 'size': 4, 'stock_hex': '00026740'},
           {'address': 156872, 'size': 4, 'stock_hex': '00026944'},
           {'address': 158080, 'size': 4, 'stock_hex': '00026c78'},
           {'address': 415490, 'size': 2, 'stock_hex': '035e'},
           {'address': 415492, 'size': 2, 'stock_hex': '0640'},
           {'address': 415494, 'size': 2, 'stock_hex': '0642'},
           {'address': 415496, 'size': 2, 'stock_hex': '7fff'},
           {'address': 415498, 'size': 2, 'stock_hex': '0648'},
           {'address': 415788, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 415792, 'size': 4, 'stock_hex': '00008710'},
           {'address': 415796, 'size': 4, 'stock_hex': 'ffff23bc'},
           {'address': 415800, 'size': 4, 'stock_hex': '00011d24'},
           {'address': 415804, 'size': 4, 'stock_hex': '0001199e'},
           {'address': 415808, 'size': 4, 'stock_hex': '000264a0'},
           {'address': 415812, 'size': 4, 'stock_hex': 'ffff119c'},
           {'address': 415816, 'size': 4, 'stock_hex': '00021bbc'},
           {'address': 415820, 'size': 4, 'stock_hex': 'ffff4124'},
           {'address': 416886, 'size': 2, 'stock_hex': '035e'},
           {'address': 416888, 'size': 2, 'stock_hex': '0640'},
           {'address': 416890, 'size': 2, 'stock_hex': '7fff'},
           {'address': 416892, 'size': 2, 'stock_hex': '0642'},
           {'address': 417140, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 417144, 'size': 4, 'stock_hex': '00008710'},
           {'address': 417148, 'size': 4, 'stock_hex': 'ffff23bc'},
           {'address': 417152, 'size': 4, 'stock_hex': '00011d24'},
           {'address': 417156, 'size': 4, 'stock_hex': '0001199e'},
           {'address': 417160, 'size': 4, 'stock_hex': '000264a0'},
           {'address': 417164, 'size': 4, 'stock_hex': 'ffff119c'},
           {'address': 417168, 'size': 4, 'stock_hex': '00021bbc'}],
 'aliases': [{'address': 138456, 'width': 4, 'original': 4294940696, 'alias': 16816152},
             {'address': 415788, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 415796, 'width': 4, 'original': 4294910908, 'alias': 16786364},
             {'address': 415812, 'width': 4, 'original': 4294906268, 'alias': 16781724},
             {'address': 415820, 'width': 4, 'original': 4294918436, 'alias': 16793892},
             {'address': 417140, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 417148, 'width': 4, 'original': 4294910908, 'alias': 16786364},
             {'address': 417164, 'width': 4, 'original': 4294906268, 'alias': 16781724}]}
CONTROLLED_CALIBRATION=[{'address': 34576, 'size': 1},
 {'address': 72094, 'size': 16},
 {'address': 72996, 'size': 17},
 {'address': 138456, 'size': 4},
 {'address': 138460, 'size': 4},
 {'address': 156868, 'size': 4},
 {'address': 156872, 'size': 4},
 {'address': 158080, 'size': 4},
 {'address': 415490, 'size': 2},
 {'address': 415492, 'size': 2},
 {'address': 415494, 'size': 2},
 {'address': 415496, 'size': 2},
 {'address': 415498, 'size': 2},
 {'address': 415788, 'size': 4},
 {'address': 415792, 'size': 4},
 {'address': 415796, 'size': 4},
 {'address': 415800, 'size': 4},
 {'address': 415804, 'size': 4},
 {'address': 415808, 'size': 4},
 {'address': 415812, 'size': 4},
 {'address': 415816, 'size': 4},
 {'address': 415820, 'size': 4},
 {'address': 416886, 'size': 2},
 {'address': 416888, 'size': 2},
 {'address': 416890, 'size': 2},
 {'address': 416892, 'size': 2},
 {'address': 417140, 'size': 4},
 {'address': 417144, 'size': 4},
 {'address': 417148, 'size': 4},
 {'address': 417152, 'size': 4},
 {'address': 417156, 'size': 4},
 {'address': 417160, 'size': 4},
 {'address': 417164, 'size': 4},
 {'address': 417168, 'size': 4}]
BOUND_SPANS=({'address': 138172, 'size': 282},
 {'address': 156832, 'size': 34},
 {'address': 157504, 'size': 46},
 {'address': 158020, 'size': 60},
 {'address': 158840, 'size': 150},
 {'address': 415156, 'size': 334},
 {'address': 416520, 'size': 286},
 {'address': 34576, 'size': 1},
 {'address': 72094, 'size': 16},
 {'address': 72996, 'size': 17},
 {'address': 138456, 'size': 4},
 {'address': 138460, 'size': 4},
 {'address': 156868, 'size': 4},
 {'address': 156872, 'size': 4},
 {'address': 158080, 'size': 4},
 {'address': 415490, 'size': 2},
 {'address': 415492, 'size': 2},
 {'address': 415494, 'size': 2},
 {'address': 415496, 'size': 2},
 {'address': 415498, 'size': 2},
 {'address': 415788, 'size': 4},
 {'address': 415792, 'size': 4},
 {'address': 415796, 'size': 4},
 {'address': 415800, 'size': 4},
 {'address': 415804, 'size': 4},
 {'address': 415808, 'size': 4},
 {'address': 415812, 'size': 4},
 {'address': 415816, 'size': 4},
 {'address': 415820, 'size': 4},
 {'address': 416886, 'size': 2},
 {'address': 416888, 'size': 2},
 {'address': 416890, 'size': 2},
 {'address': 416892, 'size': 2},
 {'address': 417140, 'size': 4},
 {'address': 417144, 'size': 4},
 {'address': 417148, 'size': 4},
 {'address': 417152, 'size': 4},
 {'address': 417156, 'size': 4},
 {'address': 417160, 'size': 4},
 {'address': 417164, 'size': 4},
 {'address': 417168, 'size': 4})
FLAGS=('native_identity_admission',
 'native_geometry_inference',
 'scale_admission',
 'units_admission',
 'natural_caller_reachability',
 'hardware_qualification',
 'stock_function_stubs',
 'native_publication')
CONFIGURATION=[{'address': 34576, 'field': 'config_8710', 'size': 1},
 {'address': 72094, 'field': 'curve_axis_0', 'size': 1},
 {'address': 72095, 'field': 'curve_axis_1', 'size': 1},
 {'address': 72096, 'field': 'curve_axis_2', 'size': 1},
 {'address': 72097, 'field': 'curve_axis_3', 'size': 1},
 {'address': 72098, 'field': 'curve_axis_4', 'size': 1},
 {'address': 72099, 'field': 'curve_axis_5', 'size': 1},
 {'address': 72100, 'field': 'curve_axis_6', 'size': 1},
 {'address': 72101, 'field': 'curve_axis_7', 'size': 1},
 {'address': 72102, 'field': 'curve_axis_8', 'size': 1},
 {'address': 72103, 'field': 'curve_axis_9', 'size': 1},
 {'address': 72104, 'field': 'curve_axis_10', 'size': 1},
 {'address': 72105, 'field': 'curve_axis_11', 'size': 1},
 {'address': 72106, 'field': 'curve_axis_12', 'size': 1},
 {'address': 72107, 'field': 'curve_axis_13', 'size': 1},
 {'address': 72108, 'field': 'curve_axis_14', 'size': 1},
 {'address': 72109, 'field': 'curve_axis_15', 'size': 1},
 {'address': 72996, 'field': 'curve_value_0', 'size': 1},
 {'address': 72997, 'field': 'curve_value_1', 'size': 1},
 {'address': 72998, 'field': 'curve_value_2', 'size': 1},
 {'address': 72999, 'field': 'curve_value_3', 'size': 1},
 {'address': 73000, 'field': 'curve_value_4', 'size': 1},
 {'address': 73001, 'field': 'curve_value_5', 'size': 1},
 {'address': 73002, 'field': 'curve_value_6', 'size': 1},
 {'address': 73003, 'field': 'curve_value_7', 'size': 1},
 {'address': 73004, 'field': 'curve_value_8', 'size': 1},
 {'address': 73005, 'field': 'curve_value_9', 'size': 1},
 {'address': 73006, 'field': 'curve_value_10', 'size': 1},
 {'address': 73007, 'field': 'curve_value_11', 'size': 1},
 {'address': 73008, 'field': 'curve_value_12', 'size': 1},
 {'address': 73009, 'field': 'curve_value_13', 'size': 1},
 {'address': 73010, 'field': 'curve_value_14', 'size': 1},
 {'address': 73011, 'field': 'curve_value_15', 'size': 1},
 {'address': 73012, 'field': 'curve_value_16', 'size': 1}]
INPUT_BLOBS=[{'name': 'curve_axis_bytes', 'address': 72094, 'size': 16},
 {'name': 'curve_value_bytes', 'address': 72996, 'size': 17}]
ADAPTER_SHA256='43f1502c2e036745fde2341232c24937f0bc0a0e99c8a830676c54f606aa8f78'
HELPER_ENTRIES=(138172, 156832, 157504, 158020, 158840)
REUSED_HELPER_FILES_SHA256={'defs/JK08A.division-callees.toml': '7f9946b15693c37f864e3c47751737ab341e453a062280732017a29c658f9ab6',
 'tools/sh-elf-run/stock_jk08a_division_callees.s': 'a46dacba966f536c37c85cdfec520fb35b1292e3638fbb1faa52593f537fa76e',
 'tools/kb/src/kb/division_callees_contract.py': '958ca6f804d7e32c5b1eebc3b6542d612b04dd24f59a964cc51c3d9046f70891',
 'tools/kb/src/kb/division_callees_matrix.py': '571166545e61d9a15eee52925eb84decc96411de28461c09e7d62152585b3780',
 'tools/kb/src/kb/division_callees_semantics.py': 'a87ea86eb0e9243c1dcb6b6424cbf3a29c8e37aa843014ec926bdefbf19d7beb',
 'tools/kb/src/kb/division_callees_capture_evidence.py': '0ee672c6c73a734cf9e01705ed594dddc69e2d22c9e47544fef8231b267e95c6',
 'tools/sh-elf-run/division_callees_capture.py': '270fffde03f81f1609de6f7314ad7882ed61a146c83aba178773cf07060877ae',
 'defs/JK08A.byte-curve-caller-withdrawal-paths.toml': 'eef3bb053ec07819d675547b5667b0a188cbc0343643f318db8100ffe15e65c7',
 'tools/sh-elf-run/stock_jk08a_byte_curve_caller_withdrawal.s': '2042cd93ebd162de58c83323ba6477a37d5110a211b6d7755425dc33d6bd3c21',
 'tools/kb/src/kb/byte_curve_caller_withdrawal_contract.py': 'aaaee28de43a668abbaf7ab4d1d0288eeedfbd7c19436dc78103dbb62d52c5dc',
 'tools/kb/src/kb/byte_curve_caller_withdrawal_matrix.py': '3afd1bda60c112551d18e8fecb2197982f99550e94d97d0c63b7feec58a5e035',
 'tools/kb/src/kb/byte_curve_caller_withdrawal_semantics.py': 'c334890fab9b66321bd6643a49020116babe6911b8dbc433dde9ff63b7cea56b',
 'tools/kb/src/kb/byte_curve_caller_withdrawal_transfers.py': '45176f0d29df994a923a215650f4e5f752fee320a74dad5e38f7f3f9dae377a6',
 'tools/kb/src/kb/byte_curve_caller_withdrawal_capture_evidence.py': '56ac55bef74315fc665cc1bb1ecb9e316e1e5738f96615fc15b440f2088aa49d',
 'tools/sh-elf-run/byte_curve_caller_withdrawal_capture.py': 'c3005baae784087eb3602f4bb2264a10131b8b978ba920c742d47103bfa3d931',
 'tools/sh-elf-run/harness-byte-curve-caller-withdrawal-paths.c': '51506e0f10f538727cbc453289ebc977bc9f1995f649c1d93bae8a16069940e4',
 'tools/kb/tests/test_byte_curve_caller_withdrawal_adapter_generated.py': '8e3a8a4cc92d9996e880b86c2303afab29e035136ffb0cfa66404fb9f0b12c65',
 'defs/JK08A.mixed-curve-caller-withdrawal-paths.toml': '981b0db82094bd12e0d7693689d3b92dd76cf7a3014aa1de4b2046ffa01966d8',
 'tools/sh-elf-run/stock_jk08a_mixed_curve_caller_withdrawal.s': '396119d014a46cef95f4dee9dd0d1e2212138deefa6fc71d1fed66dbf5940a92',
 'tools/kb/src/kb/mixed_curve_caller_withdrawal_contract.py': '92da7ea75343a44fe132ec4dee276df7e6e8f010a6aa25d3c741b279c229bd82',
 'tools/kb/src/kb/mixed_curve_caller_withdrawal_matrix.py': 'f864ed45f70c63be6ad420c5dcdd8471bb56c38e17eb6215d8741780d827e19d',
 'tools/kb/src/kb/mixed_curve_caller_withdrawal_semantics.py': 'b124ded8e0c8144f6612f6df9e706e68a7e784cae12d87215a5f730acef7bdca',
 'tools/kb/src/kb/mixed_curve_caller_withdrawal_transfers.py': '03f7b96e668588ec61d9615bbd19229d43f19b7d145e4f0e5a610b580c1884cf',
 'tools/sh-elf-run/mixed_curve_caller_withdrawal_capture.py': '09af5cf9834060f992ae8d47aaeaa005e7536143d8109c18614977b3b5a13b73',
 'tools/sh-elf-run/harness-mixed-curve-caller-withdrawal-paths.c': '48d6e0c618e0d26328133d69d66fed9a69fe9294301754f4474c983c7adc9e19',
 'tools/kb/tests/test_mixed_curve_caller_withdrawal_adapter_generated.py': '6b6ddc6999d8502e5adcffc604127114adcd92d7302bb4f5b75e9bf575c4e4c7'}
FUNCTIONS=(*ENTRIES,*HELPER_ENTRIES)
SPANS=tuple((row['start'],row['end']) for row in UNIT['code'])


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','entries','observer',
            'context_bytes','frame_bytes','frame_prefix','unit','controlled_calibration','configuration','input_blobs','adapter',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-paired-curve-normalization-withdrawal'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or not test_contract.exact((value['entries'],value['observer'],value['context_bytes'],value['frame_bytes'],
                value['frame_prefix']),(list(ENTRIES),OBSERVER,80,192,160))
            or any(value[name] is not False for name in FLAGS)
            or not test_contract.exact(value['unit'],UNIT)
            or not test_contract.exact(value['controlled_calibration'],CONTROLLED_CALIBRATION)
            or not test_contract.exact(value['configuration'],CONFIGURATION)
            or not test_contract.exact(value['input_blobs'],INPUT_BLOBS)
            or hashlib.sha256(json.dumps(value['adapter'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=ADAPTER_SHA256):
        raise ValueError('the paired curve normalization caller withdrawal paths change an exact natural entry, code/pool byte, alias or complete observer premise')
    require_reused_helper_boundary(root)
    return dict(value,entry=[dict(start=first,end=last) for first,last in SPANS])


def require_image(declared,image):
    if (type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256
            or not test_contract.exact(declared['unit'],UNIT)):
        raise ValueError('the paired curve normalization caller withdrawal paths change the complete owned stock image or exact unit')
    for row in UNIT['pools']:
        if image[row['address']:row['address']+row['size']].hex()!=row['stock_hex']:
            raise ValueError('the paired curve normalization caller withdrawal paths change a pinned exact stock pool or configuration byte')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for row in UNIT['aliases']:
        at=row['address']
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('the paired curve normalization caller withdrawal paths relocate a different original native pointer')
        fixture[at:at+4]=row['alias'].to_bytes(4,'big');aliases.append(dict(row))
    return bytes(fixture),aliases


def fixture_for_case(declared,image,case):
    from kb import paired_curve_normalization_withdrawal_matrix as matrix
    matrix.require_case(case);fixture,aliases=independent_fixture(declared,image);fixture=bytearray(fixture)
    for row in INPUT_BLOBS:
        if not row['name'].startswith('axis_'):continue
        at,size=row['address'],row['size']
        fixture[at:at+size]=matrix.input_blob(row,case,image)
    for row in CONFIGURATION:
        at,size=row['address'],row['size'];fixture[at:at+size]=case[row['field']].to_bytes(size,'big')
    return bytes(fixture),aliases


def require_reused_helper_boundary(root):
    for name,wanted in REUSED_HELPER_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=wanted:
            raise ValueError('the paired curve normalization caller changes a complete reused signed/unsigned division,byte-curve and standard implicit-byte source boundary')
