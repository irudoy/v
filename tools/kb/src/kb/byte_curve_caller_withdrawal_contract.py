"""Exact natural byte curve caller withdrawal paths, literal inputs and declared pointer aliases."""

import hashlib
import json
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.byte-curve-caller-withdrawal-paths.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
ENTRIES=(181660, 451544)
UNIT={'assembly': 'tools/sh-elf-run/stock_jk08a_byte_curve_caller_withdrawal.s',
 'code': [{'start': 138172, 'end': 138454},
          {'start': 156528, 'end': 156546},
          {'start': 157504, 'end': 157550},
          {'start': 158336, 'end': 158364},
          {'start': 158378, 'end': 158394},
          {'start': 181660, 'end': 181696},
          {'start': 451544, 'end': 451650}],
 'pools': [{'address': 138456, 'size': 4, 'stock_hex': 'ffff9818'},
           {'address': 138460, 'size': 4, 'stock_hex': '0000044e'},
           {'address': 156546, 'size': 2, 'stock_hex': '00e0'},
           {'address': 156548, 'size': 4, 'stock_hex': '00026a80'},
           {'address': 158396, 'size': 4, 'stock_hex': '00026740'},
           {'address': 182236, 'size': 4, 'stock_hex': 'ffff1072'},
           {'address': 182268, 'size': 4, 'stock_hex': 'ffff1e50'},
           {'address': 182272, 'size': 4, 'stock_hex': '00012332'},
           {'address': 182276, 'size': 4, 'stock_hex': '00026370'},
           {'address': 451804, 'size': 2, 'stock_hex': '0425'},
           {'address': 451808, 'size': 2, 'stock_hex': '0422'},
           {'address': 451810, 'size': 2, 'stock_hex': '04da'},
           {'address': 452036, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 452044, 'size': 4, 'stock_hex': 'ffff244f'},
           {'address': 452048, 'size': 4, 'stock_hex': 'ffff106a'},
           {'address': 452052, 'size': 4, 'stock_hex': '0001296c'},
           {'address': 452056, 'size': 4, 'stock_hex': '00026370'},
           {'address': 452060, 'size': 4, 'stock_hex': '00021bbc'}],
 'aliases': [{'address': 138456, 'width': 4, 'original': 4294940696, 'alias': 16816152},
             {'address': 182236, 'width': 4, 'original': 4294905970, 'alias': 16781426},
             {'address': 182268, 'width': 4, 'original': 4294909520, 'alias': 16784976},
             {'address': 452036, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 452044, 'width': 4, 'original': 4294911055, 'alias': 16786511},
             {'address': 452048, 'width': 4, 'original': 4294905962, 'alias': 16781418}]}
CONTROLLED_CALIBRATION=[{'address': 138456, 'size': 4},
 {'address': 138460, 'size': 4},
 {'address': 156546, 'size': 2},
 {'address': 156548, 'size': 4},
 {'address': 158396, 'size': 4},
 {'address': 182236, 'size': 4},
 {'address': 182268, 'size': 4},
 {'address': 182272, 'size': 4},
 {'address': 182276, 'size': 4},
 {'address': 451804, 'size': 2},
 {'address': 451808, 'size': 2},
 {'address': 451810, 'size': 2},
 {'address': 452036, 'size': 4},
 {'address': 452044, 'size': 4},
 {'address': 452048, 'size': 4},
 {'address': 452052, 'size': 4},
 {'address': 452056, 'size': 4},
 {'address': 452060, 'size': 4},
 {'address': 74546, 'size': 8},
 {'address': 76140, 'size': 8}]
BOUND_SPANS=({'address': 138172, 'size': 282},
 {'address': 156528, 'size': 18},
 {'address': 157504, 'size': 46},
 {'address': 158336, 'size': 28},
 {'address': 158378, 'size': 16},
 {'address': 181660, 'size': 36},
 {'address': 451544, 'size': 106},
 {'address': 138456, 'size': 4},
 {'address': 138460, 'size': 4},
 {'address': 156546, 'size': 2},
 {'address': 156548, 'size': 4},
 {'address': 158396, 'size': 4},
 {'address': 182236, 'size': 4},
 {'address': 182268, 'size': 4},
 {'address': 182272, 'size': 4},
 {'address': 182276, 'size': 4},
 {'address': 451804, 'size': 2},
 {'address': 451808, 'size': 2},
 {'address': 451810, 'size': 2},
 {'address': 452036, 'size': 4},
 {'address': 452044, 'size': 4},
 {'address': 452048, 'size': 4},
 {'address': 452052, 'size': 4},
 {'address': 452056, 'size': 4},
 {'address': 452060, 'size': 4},
 {'address': 74546, 'size': 8},
 {'address': 76140, 'size': 8})
FLAGS=('native_identity_admission',
 'native_geometry_inference',
 'scale_admission',
 'units_admission',
 'natural_caller_reachability',
 'hardware_qualification',
 'stock_function_stubs',
 'native_publication')
CONFIGURATION=[{'address': 74546, 'field': 'curve_first_0', 'size': 1},
 {'address': 74547, 'field': 'curve_first_1', 'size': 1},
 {'address': 74548, 'field': 'curve_first_2', 'size': 1},
 {'address': 74549, 'field': 'curve_first_3', 'size': 1},
 {'address': 74550, 'field': 'curve_first_4', 'size': 1},
 {'address': 74551, 'field': 'curve_first_5', 'size': 1},
 {'address': 74552, 'field': 'curve_first_6', 'size': 1},
 {'address': 74553, 'field': 'curve_first_7', 'size': 1},
 {'address': 76140, 'field': 'curve_second_0', 'size': 1},
 {'address': 76141, 'field': 'curve_second_1', 'size': 1},
 {'address': 76142, 'field': 'curve_second_2', 'size': 1},
 {'address': 76143, 'field': 'curve_second_3', 'size': 1},
 {'address': 76144, 'field': 'curve_second_4', 'size': 1},
 {'address': 76145, 'field': 'curve_second_5', 'size': 1},
 {'address': 76146, 'field': 'curve_second_6', 'size': 1},
 {'address': 76147, 'field': 'curve_second_7', 'size': 1}]
ADAPTER_SHA256='a3a40af81c6380518ab29b66135c614cdc239befab261308155b5c29f9bec07c'
HELPER_ENTRIES=(156528, 158304, 157504, 138172)
REUSED_HELPER_FILES_SHA256={'defs/JK08A.division-callees.toml': '7f9946b15693c37f864e3c47751737ab341e453a062280732017a29c658f9ab6',
 'tools/sh-elf-run/stock_jk08a_division_callees.s': 'a46dacba966f536c37c85cdfec520fb35b1292e3638fbb1faa52593f537fa76e',
 'tools/kb/src/kb/division_callees_contract.py': '958ca6f804d7e32c5b1eebc3b6542d612b04dd24f59a964cc51c3d9046f70891',
 'tools/kb/src/kb/division_callees_matrix.py': '571166545e61d9a15eee52925eb84decc96411de28461c09e7d62152585b3780',
 'tools/kb/src/kb/division_callees_semantics.py': 'a87ea86eb0e9243c1dcb6b6424cbf3a29c8e37aa843014ec926bdefbf19d7beb',
 'tools/kb/src/kb/division_callees_capture_evidence.py': '0ee672c6c73a734cf9e01705ed594dddc69e2d22c9e47544fef8231b267e95c6',
 'tools/sh-elf-run/division_callees_capture.py': '270fffde03f81f1609de6f7314ad7882ed61a146c83aba178773cf07060877ae',
 'defs/JK08A.rugged-gerbil.toml': '43d8bf88e97976d8ea5d28f8c67e8f974ca69c08a50c1ce713a848308c7350e3',
 'tools/sh-elf-run/stock_jk08a_rugged_gerbil.s': 'b39a1086f3a2b62f5b1aa07048c0aa782cc295ee2f29bd05d4df70970e6c91e9',
 'tools/kb/src/kb/rugged_gerbil_contract.py': 'c265922d3f1433ac5462022d659481245a43b07b8df1537dec82c907e97cb9dd'}
FUNCTIONS=(*ENTRIES,*HELPER_ENTRIES)
SPANS=tuple((row['start'],row['end']) for row in UNIT['code'])


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','entries','observer',
            'context_bytes','frame_bytes','frame_prefix','unit','controlled_calibration','configuration','adapter',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-byte-curve-caller-withdrawal'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or not test_contract.exact((value['entries'],value['observer'],value['context_bytes'],value['frame_bytes'],
                value['frame_prefix']),(list(ENTRIES),OBSERVER,80,192,160))
            or any(value[name] is not False for name in FLAGS)
            or not test_contract.exact(value['unit'],UNIT)
            or not test_contract.exact(value['controlled_calibration'],CONTROLLED_CALIBRATION)
            or not test_contract.exact(value['configuration'],CONFIGURATION)
            or hashlib.sha256(json.dumps(value['adapter'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=ADAPTER_SHA256):
        raise ValueError('the byte curve caller withdrawal paths change an exact natural entry, code/pool byte, alias or complete observer premise')
    require_reused_helper_boundary(root)
    return dict(value,entry=[dict(start=first,end=last) for first,last in SPANS])


def require_image(declared,image):
    if (type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256
            or not test_contract.exact(declared['unit'],UNIT)):
        raise ValueError('the byte curve caller withdrawal paths change the complete owned stock image or exact unit')
    for row in UNIT['pools']:
        if image[row['address']:row['address']+row['size']].hex()!=row['stock_hex']:
            raise ValueError('the byte curve caller withdrawal paths change a pinned exact stock pool or configuration byte')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for row in UNIT['aliases']:
        at=row['address']
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('the byte curve caller withdrawal paths relocate a different original native pointer')
        fixture[at:at+4]=row['alias'].to_bytes(4,'big');aliases.append(dict(row))
    return bytes(fixture),aliases


def fixture_for_case(declared,image,case):
    from kb import byte_curve_caller_withdrawal_matrix as matrix
    matrix.require_case(case);fixture,aliases=independent_fixture(declared,image);fixture=bytearray(fixture)
    for row in CONFIGURATION:
        at,size=row['address'],row['size'];fixture[at:at+size]=case[row['field']].to_bytes(size,'big')
    return bytes(fixture),aliases


def require_reused_helper_boundary(root):
    for name,wanted in REUSED_HELPER_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=wanted:
            raise ValueError('the division caller changes the complete reused direct-helper source boundary')
