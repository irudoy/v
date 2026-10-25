"""Exact natural scaled division caller withdrawal paths, literal inputs and declared pointer aliases."""

import hashlib
import json
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.scaled-division-caller-withdrawal-paths.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
ENTRIES=(320924, 476280, 477956)
UNIT={'assembly': 'tools/sh-elf-run/stock_jk08a_scaled_division_caller_withdrawal.s',
 'code': [{'start': 138172, 'end': 138454},
          {'start': 140538, 'end': 140552},
          {'start': 320924, 'end': 321028},
          {'start': 476280, 'end': 476460},
          {'start': 477956, 'end': 478056}],
 'pools': [{'address': 37966, 'size': 2, 'stock_hex': '351e'},
           {'address': 90902, 'size': 2, 'stock_hex': '351e'},
           {'address': 138456, 'size': 4, 'stock_hex': 'ffff9818'},
           {'address': 138460, 'size': 4, 'stock_hex': '0000044e'},
           {'address': 321028, 'size': 2, 'stock_hex': '03c6'},
           {'address': 321030, 'size': 2, 'stock_hex': '0352'},
           {'address': 321032, 'size': 2, 'stock_hex': '0434'},
           {'address': 321036, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 321040, 'size': 4, 'stock_hex': '00021bbc'},
           {'address': 476460, 'size': 2, 'stock_hex': '0a42'},
           {'address': 476462, 'size': 2, 'stock_hex': '0a8a'},
           {'address': 476464, 'size': 2, 'stock_hex': '0a8e'},
           {'address': 476466, 'size': 2, 'stock_hex': '7fff'},
           {'address': 476468, 'size': 2, 'stock_hex': '0a6c'},
           {'address': 476470, 'size': 2, 'stock_hex': '0a74'},
           {'address': 476472, 'size': 2, 'stock_hex': '0a6a'},
           {'address': 476476, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 476480, 'size': 4, 'stock_hex': '000224fa'},
           {'address': 476484, 'size': 4, 'stock_hex': '00016316'},
           {'address': 476488, 'size': 4, 'stock_hex': '00021bbc'},
           {'address': 476492, 'size': 4, 'stock_hex': 'ffff245c'},
           {'address': 476496, 'size': 4, 'stock_hex': 'ffff417e'},
           {'address': 476500, 'size': 4, 'stock_hex': 'ffff2470'},
           {'address': 476504, 'size': 4, 'stock_hex': 'ffff23bc'},
           {'address': 478280, 'size': 2, 'stock_hex': '0716'},
           {'address': 478282, 'size': 2, 'stock_hex': '072e'},
           {'address': 478284, 'size': 2, 'stock_hex': '7fff'},
           {'address': 478286, 'size': 2, 'stock_hex': '065c'},
           {'address': 478500, 'size': 4, 'stock_hex': 'ffff23bc'},
           {'address': 478504, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 478508, 'size': 4, 'stock_hex': '0000944e'},
           {'address': 478512, 'size': 4, 'stock_hex': '000224fa'},
           {'address': 478516, 'size': 4, 'stock_hex': '00021bbc'}],
 'aliases': [{'address': 138456, 'width': 4, 'original': 4294940696, 'alias': 16816152},
             {'address': 321036, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 476476, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 476492, 'width': 4, 'original': 4294911068, 'alias': 16786524},
             {'address': 476496, 'width': 4, 'original': 4294918526, 'alias': 16793982},
             {'address': 476500, 'width': 4, 'original': 4294911088, 'alias': 16786544},
             {'address': 476504, 'width': 4, 'original': 4294910908, 'alias': 16786364},
             {'address': 478500, 'width': 4, 'original': 4294910908, 'alias': 16786364},
             {'address': 478504, 'width': 4, 'original': 4294906508, 'alias': 16781964}]}
CONTROLLED_CALIBRATION=[{'address': 37966, 'size': 2},
 {'address': 90902, 'size': 2},
 {'address': 138456, 'size': 4},
 {'address': 138460, 'size': 4},
 {'address': 321028, 'size': 2},
 {'address': 321030, 'size': 2},
 {'address': 321032, 'size': 2},
 {'address': 321036, 'size': 4},
 {'address': 321040, 'size': 4},
 {'address': 476460, 'size': 2},
 {'address': 476462, 'size': 2},
 {'address': 476464, 'size': 2},
 {'address': 476466, 'size': 2},
 {'address': 476468, 'size': 2},
 {'address': 476470, 'size': 2},
 {'address': 476472, 'size': 2},
 {'address': 476476, 'size': 4},
 {'address': 476480, 'size': 4},
 {'address': 476484, 'size': 4},
 {'address': 476488, 'size': 4},
 {'address': 476492, 'size': 4},
 {'address': 476496, 'size': 4},
 {'address': 476500, 'size': 4},
 {'address': 476504, 'size': 4},
 {'address': 478280, 'size': 2},
 {'address': 478282, 'size': 2},
 {'address': 478284, 'size': 2},
 {'address': 478286, 'size': 2},
 {'address': 478500, 'size': 4},
 {'address': 478504, 'size': 4},
 {'address': 478508, 'size': 4},
 {'address': 478512, 'size': 4},
 {'address': 478516, 'size': 4}]
BOUND_SPANS=({'address': 138172, 'size': 282},
 {'address': 140538, 'size': 14},
 {'address': 320924, 'size': 104},
 {'address': 476280, 'size': 180},
 {'address': 477956, 'size': 100},
 {'address': 37966, 'size': 2},
 {'address': 90902, 'size': 2},
 {'address': 138456, 'size': 4},
 {'address': 138460, 'size': 4},
 {'address': 321028, 'size': 2},
 {'address': 321030, 'size': 2},
 {'address': 321032, 'size': 2},
 {'address': 321036, 'size': 4},
 {'address': 321040, 'size': 4},
 {'address': 476460, 'size': 2},
 {'address': 476462, 'size': 2},
 {'address': 476464, 'size': 2},
 {'address': 476466, 'size': 2},
 {'address': 476468, 'size': 2},
 {'address': 476470, 'size': 2},
 {'address': 476472, 'size': 2},
 {'address': 476476, 'size': 4},
 {'address': 476480, 'size': 4},
 {'address': 476484, 'size': 4},
 {'address': 476488, 'size': 4},
 {'address': 476492, 'size': 4},
 {'address': 476496, 'size': 4},
 {'address': 476500, 'size': 4},
 {'address': 476504, 'size': 4},
 {'address': 478280, 'size': 2},
 {'address': 478282, 'size': 2},
 {'address': 478284, 'size': 2},
 {'address': 478286, 'size': 2},
 {'address': 478500, 'size': 4},
 {'address': 478504, 'size': 4},
 {'address': 478508, 'size': 4},
 {'address': 478512, 'size': 4},
 {'address': 478516, 'size': 4})
FLAGS=('native_identity_admission',
 'native_geometry_inference',
 'scale_admission',
 'units_admission',
 'natural_caller_reachability',
 'hardware_qualification',
 'stock_function_stubs',
 'native_publication')
CONFIGURATION=[{'address': 37966, 'field': 'first_divisor', 'size': 2},
 {'address': 90902, 'field': 'second_divisor', 'size': 2}]
ADAPTER_SHA256='037d46f34ff839d3b29a8939e31b0ec05743ab190b0d2922127f0ccc4abfcb29'
HELPER_ENTRIES=(138172, 140538)
REUSED_HELPER_FILES_SHA256={'defs/JK08A.division-callees.toml': '7f9946b15693c37f864e3c47751737ab341e453a062280732017a29c658f9ab6',
 'tools/sh-elf-run/stock_jk08a_division_callees.s': 'a46dacba966f536c37c85cdfec520fb35b1292e3638fbb1faa52593f537fa76e',
 'tools/kb/src/kb/division_callees_contract.py': '958ca6f804d7e32c5b1eebc3b6542d612b04dd24f59a964cc51c3d9046f70891',
 'tools/kb/src/kb/division_callees_matrix.py': '571166545e61d9a15eee52925eb84decc96411de28461c09e7d62152585b3780',
 'tools/kb/src/kb/division_callees_semantics.py': 'a87ea86eb0e9243c1dcb6b6424cbf3a29c8e37aa843014ec926bdefbf19d7beb',
 'tools/kb/src/kb/division_callees_capture_evidence.py': '0ee672c6c73a734cf9e01705ed594dddc69e2d22c9e47544fef8231b267e95c6',
 'tools/sh-elf-run/division_callees_capture.py': '270fffde03f81f1609de6f7314ad7882ed61a146c83aba178773cf07060877ae',
 'defs/JK08A.register-only-helpers.toml': 'b59fe2071800caa3023516b8a7299ccab86c05ad257848bfb0e7153bfc0e884d',
 'tools/sh-elf-run/stock_jk08a_register_only_helpers.s': 'f8810cb5b192a4a93d89e84adfc24269f73e5b6bb1e9eda63fb86e95270ed9af',
 'tools/kb/src/kb/register_only_helpers_contract.py': 'f129512b01c0c264da5c50bf33a5c0e3536580789e6b180d881f455c0c462f7a',
 'tools/kb/src/kb/register_only_helpers_matrix.py': '8f9c12c52ee33cac53bd682010d931c5a848e66a2dda0f8ef58a4862ba3b65c8',
 'tools/kb/src/kb/register_only_helpers_semantics.py': '41602f59c53f51aceededc7fa14f24b3ab31516ce7c4824ea05bbd1d51681151',
 'tools/kb/src/kb/register_only_helpers_capture_evidence.py': '9db69f66a507d43e9ab40d3f31c6c93fae830b1bb8a68360988248352b90fa2d',
 'tools/sh-elf-run/register_only_helpers_capture.py': '4ea4993f3d8a5d97bc2794359aba7658badf2c7b2c63c2ac0c3aee1ee9a5cf8e'}
FUNCTIONS=(*ENTRIES,*HELPER_ENTRIES)
SPANS=tuple((row['start'],row['end']) for row in UNIT['code'])


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','entries','observer',
            'context_bytes','frame_bytes','frame_prefix','unit','controlled_calibration','configuration','adapter',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-scaled-division-caller-withdrawal'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or not test_contract.exact((value['entries'],value['observer'],value['context_bytes'],value['frame_bytes'],
                value['frame_prefix']),(list(ENTRIES),OBSERVER,80,192,160))
            or any(value[name] is not False for name in FLAGS)
            or not test_contract.exact(value['unit'],UNIT)
            or not test_contract.exact(value['controlled_calibration'],CONTROLLED_CALIBRATION)
            or not test_contract.exact(value['configuration'],CONFIGURATION)
            or hashlib.sha256(json.dumps(value['adapter'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=ADAPTER_SHA256):
        raise ValueError('the scaled division caller withdrawal paths change an exact natural entry, code/pool byte, alias or complete observer premise')
    require_reused_helper_boundary(root)
    return dict(value,entry=[dict(start=first,end=last) for first,last in SPANS])


def require_image(declared,image):
    if (type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256
            or not test_contract.exact(declared['unit'],UNIT)):
        raise ValueError('the scaled division caller withdrawal paths change the complete owned stock image or exact unit')
    for row in UNIT['pools']:
        if image[row['address']:row['address']+row['size']].hex()!=row['stock_hex']:
            raise ValueError('the scaled division caller withdrawal paths change a pinned exact stock pool or configuration byte')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for row in UNIT['aliases']:
        at=row['address']
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('the scaled division caller withdrawal paths relocate a different original native pointer')
        fixture[at:at+4]=row['alias'].to_bytes(4,'big');aliases.append(dict(row))
    return bytes(fixture),aliases


def fixture_for_case(declared,image,case):
    from kb import scaled_division_caller_withdrawal_matrix as matrix
    matrix.require_case(case);fixture,aliases=independent_fixture(declared,image);fixture=bytearray(fixture)
    for row in CONFIGURATION:
        at,size=row['address'],row['size'];fixture[at:at+size]=case[row['field']].to_bytes(size,'big')
    return bytes(fixture),aliases


def require_reused_helper_boundary(root):
    for name,wanted in REUSED_HELPER_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=wanted:
            raise ValueError('the scaled division caller changes the complete reused division/register-only helper source boundary')
