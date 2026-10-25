"""Exact natural guarded quotient caller withdrawal paths, literal inputs and declared pointer aliases."""

import hashlib
import json
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.guarded-quotient-caller-withdrawal-paths.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
ENTRIES=(340654, 478056, 480006)
UNIT={'assembly': 'tools/sh-elf-run/stock_jk08a_guarded_quotient_caller_withdrawal.s',
 'code': [{'start': 138172, 'end': 138454},
          {'start': 340654, 'end': 340922},
          {'start': 340988, 'end': 341166},
          {'start': 478056, 'end': 478216},
          {'start': 480006, 'end': 480068},
          {'start': 480078, 'end': 480150}],
 'pools': [{'address': 37010, 'size': 2, 'stock_hex': '0148'},
           {'address': 37198, 'size': 2, 'stock_hex': '001b'},
           {'address': 37200, 'size': 2, 'stock_hex': '0037'},
           {'address': 37966, 'size': 2, 'stock_hex': '351e'},
           {'address': 138456, 'size': 4, 'stock_hex': 'ffff9818'},
           {'address': 138460, 'size': 4, 'stock_hex': '0000044e'},
           {'address': 340922, 'size': 2, 'stock_hex': '038e'},
           {'address': 340924, 'size': 2, 'stock_hex': '0342'},
           {'address': 340926, 'size': 2, 'stock_hex': '0372'},
           {'address': 340928, 'size': 2, 'stock_hex': '3fff'},
           {'address': 340960, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 340964, 'size': 4, 'stock_hex': 'ffff22f8'},
           {'address': 340968, 'size': 4, 'stock_hex': 'ffff2470'},
           {'address': 340972, 'size': 4, 'stock_hex': 'ffff22dc'},
           {'address': 340976, 'size': 4, 'stock_hex': '00009092'},
           {'address': 340980, 'size': 4, 'stock_hex': '7fffffff'},
           {'address': 340984, 'size': 4, 'stock_hex': '00021bbc'},
           {'address': 341166, 'size': 2, 'stock_hex': '0375'},
           {'address': 341168, 'size': 2, 'stock_hex': '0353'},
           {'address': 341170, 'size': 2, 'stock_hex': '03d4'},
           {'address': 341172, 'size': 2, 'stock_hex': '03f4'},
           {'address': 341174, 'size': 2, 'stock_hex': '06b1'},
           {'address': 341176, 'size': 2, 'stock_hex': '06f8'},
           {'address': 341178, 'size': 2, 'stock_hex': '0374'},
           {'address': 341180, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 341184, 'size': 4, 'stock_hex': 'ffff28f8'},
           {'address': 341188, 'size': 4, 'stock_hex': '00021bbc'},
           {'address': 341192, 'size': 4, 'stock_hex': '3fc00000'},
           {'address': 341196, 'size': 4, 'stock_hex': '003fffff'},
           {'address': 478288, 'size': 2, 'stock_hex': '056c'},
           {'address': 478500, 'size': 4, 'stock_hex': 'ffff23bc'},
           {'address': 478504, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 478516, 'size': 4, 'stock_hex': '00021bbc'},
           {'address': 478520, 'size': 4, 'stock_hex': 'ffff417e'},
           {'address': 478524, 'size': 4, 'stock_hex': 'ffff24ce'},
           {'address': 478528, 'size': 4, 'stock_hex': 'ffff120e'},
           {'address': 478532, 'size': 4, 'stock_hex': '0000914e'},
           {'address': 480074, 'size': 2, 'stock_hex': '0716'},
           {'address': 480076, 'size': 2, 'stock_hex': '0666'},
           {'address': 480286, 'size': 2, 'stock_hex': '7fff'},
           {'address': 480288, 'size': 2, 'stock_hex': '0748'},
           {'address': 480320, 'size': 4, 'stock_hex': 'ffff23bc'},
           {'address': 480324, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 480328, 'size': 4, 'stock_hex': '0000944e'},
           {'address': 480332, 'size': 4, 'stock_hex': '00021bbc'},
           {'address': 480336, 'size': 4, 'stock_hex': '01ffffff'}],
 'aliases': [{'address': 138456, 'width': 4, 'original': 4294940696, 'alias': 16816152},
             {'address': 340960, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 340964, 'width': 4, 'original': 4294910712, 'alias': 16786168},
             {'address': 340968, 'width': 4, 'original': 4294911088, 'alias': 16786544},
             {'address': 340972, 'width': 4, 'original': 4294910684, 'alias': 16786140},
             {'address': 341180, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 341184, 'width': 4, 'original': 4294912248, 'alias': 16787704},
             {'address': 478500, 'width': 4, 'original': 4294910908, 'alias': 16786364},
             {'address': 478504, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 478520, 'width': 4, 'original': 4294918526, 'alias': 16793982},
             {'address': 478524, 'width': 4, 'original': 4294911182, 'alias': 16786638},
             {'address': 478528, 'width': 4, 'original': 4294906382, 'alias': 16781838},
             {'address': 480320, 'width': 4, 'original': 4294910908, 'alias': 16786364},
             {'address': 480324, 'width': 4, 'original': 4294906508, 'alias': 16781964}]}
CONTROLLED_CALIBRATION=[{'address': 37010, 'size': 2},
 {'address': 37198, 'size': 2},
 {'address': 37200, 'size': 2},
 {'address': 37966, 'size': 2},
 {'address': 138456, 'size': 4},
 {'address': 138460, 'size': 4},
 {'address': 340922, 'size': 2},
 {'address': 340924, 'size': 2},
 {'address': 340926, 'size': 2},
 {'address': 340928, 'size': 2},
 {'address': 340960, 'size': 4},
 {'address': 340964, 'size': 4},
 {'address': 340968, 'size': 4},
 {'address': 340972, 'size': 4},
 {'address': 340976, 'size': 4},
 {'address': 340980, 'size': 4},
 {'address': 340984, 'size': 4},
 {'address': 341166, 'size': 2},
 {'address': 341168, 'size': 2},
 {'address': 341170, 'size': 2},
 {'address': 341172, 'size': 2},
 {'address': 341174, 'size': 2},
 {'address': 341176, 'size': 2},
 {'address': 341178, 'size': 2},
 {'address': 341180, 'size': 4},
 {'address': 341184, 'size': 4},
 {'address': 341188, 'size': 4},
 {'address': 341192, 'size': 4},
 {'address': 341196, 'size': 4},
 {'address': 478288, 'size': 2},
 {'address': 478500, 'size': 4},
 {'address': 478504, 'size': 4},
 {'address': 478516, 'size': 4},
 {'address': 478520, 'size': 4},
 {'address': 478524, 'size': 4},
 {'address': 478528, 'size': 4},
 {'address': 478532, 'size': 4},
 {'address': 480074, 'size': 2},
 {'address': 480076, 'size': 2},
 {'address': 480286, 'size': 2},
 {'address': 480288, 'size': 2},
 {'address': 480320, 'size': 4},
 {'address': 480324, 'size': 4},
 {'address': 480328, 'size': 4},
 {'address': 480332, 'size': 4},
 {'address': 480336, 'size': 4}]
BOUND_SPANS=({'address': 138172, 'size': 282},
 {'address': 340654, 'size': 268},
 {'address': 340988, 'size': 178},
 {'address': 478056, 'size': 160},
 {'address': 480006, 'size': 62},
 {'address': 480078, 'size': 72},
 {'address': 37010, 'size': 2},
 {'address': 37198, 'size': 2},
 {'address': 37200, 'size': 2},
 {'address': 37966, 'size': 2},
 {'address': 138456, 'size': 4},
 {'address': 138460, 'size': 4},
 {'address': 340922, 'size': 2},
 {'address': 340924, 'size': 2},
 {'address': 340926, 'size': 2},
 {'address': 340928, 'size': 2},
 {'address': 340960, 'size': 4},
 {'address': 340964, 'size': 4},
 {'address': 340968, 'size': 4},
 {'address': 340972, 'size': 4},
 {'address': 340976, 'size': 4},
 {'address': 340980, 'size': 4},
 {'address': 340984, 'size': 4},
 {'address': 341166, 'size': 2},
 {'address': 341168, 'size': 2},
 {'address': 341170, 'size': 2},
 {'address': 341172, 'size': 2},
 {'address': 341174, 'size': 2},
 {'address': 341176, 'size': 2},
 {'address': 341178, 'size': 2},
 {'address': 341180, 'size': 4},
 {'address': 341184, 'size': 4},
 {'address': 341188, 'size': 4},
 {'address': 341192, 'size': 4},
 {'address': 341196, 'size': 4},
 {'address': 478288, 'size': 2},
 {'address': 478500, 'size': 4},
 {'address': 478504, 'size': 4},
 {'address': 478516, 'size': 4},
 {'address': 478520, 'size': 4},
 {'address': 478524, 'size': 4},
 {'address': 478528, 'size': 4},
 {'address': 478532, 'size': 4},
 {'address': 480074, 'size': 2},
 {'address': 480076, 'size': 2},
 {'address': 480286, 'size': 2},
 {'address': 480288, 'size': 2},
 {'address': 480320, 'size': 4},
 {'address': 480324, 'size': 4},
 {'address': 480328, 'size': 4},
 {'address': 480332, 'size': 4},
 {'address': 480336, 'size': 4})
FLAGS=('native_identity_admission',
 'native_geometry_inference',
 'scale_admission',
 'units_admission',
 'natural_caller_reachability',
 'hardware_qualification',
 'stock_function_stubs',
 'native_publication')
CONFIGURATION=[{'address': 37010, 'field': 'word_9092', 'size': 2},
 {'address': 37198, 'field': 'word_914e', 'size': 2},
 {'address': 37200, 'field': 'word_9150', 'size': 2},
 {'address': 37966, 'field': 'word_944e', 'size': 2}]
INPUT_BLOBS=[]
ADAPTER_SHA256='717293d24602603d38ed9dab7a7b1e7490f90247ecc5c507330f47f0dfe06cb2'
HELPER_ENTRIES=(138172,)
REUSED_HELPER_FILES_SHA256={'defs/JK08A.division-callees.toml': '7f9946b15693c37f864e3c47751737ab341e453a062280732017a29c658f9ab6',
 'tools/sh-elf-run/stock_jk08a_division_callees.s': 'a46dacba966f536c37c85cdfec520fb35b1292e3638fbb1faa52593f537fa76e',
 'tools/kb/src/kb/division_callees_contract.py': '958ca6f804d7e32c5b1eebc3b6542d612b04dd24f59a964cc51c3d9046f70891',
 'tools/kb/src/kb/division_callees_matrix.py': '571166545e61d9a15eee52925eb84decc96411de28461c09e7d62152585b3780',
 'tools/kb/src/kb/division_callees_semantics.py': 'a87ea86eb0e9243c1dcb6b6424cbf3a29c8e37aa843014ec926bdefbf19d7beb',
 'tools/kb/src/kb/division_callees_capture_evidence.py': '0ee672c6c73a734cf9e01705ed594dddc69e2d22c9e47544fef8231b267e95c6',
 'tools/sh-elf-run/division_callees_capture.py': '270fffde03f81f1609de6f7314ad7882ed61a146c83aba178773cf07060877ae'}
FUNCTIONS=(*ENTRIES,*HELPER_ENTRIES)
SPANS=tuple((row['start'],row['end']) for row in UNIT['code'])


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','entries','observer',
            'context_bytes','frame_bytes','frame_prefix','unit','controlled_calibration','configuration','input_blobs','adapter',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-guarded-quotient-caller-withdrawal'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or not test_contract.exact((value['entries'],value['observer'],value['context_bytes'],value['frame_bytes'],
                value['frame_prefix']),(list(ENTRIES),OBSERVER,80,192,160))
            or any(value[name] is not False for name in FLAGS)
            or not test_contract.exact(value['unit'],UNIT)
            or not test_contract.exact(value['controlled_calibration'],CONTROLLED_CALIBRATION)
            or not test_contract.exact(value['configuration'],CONFIGURATION)
            or not test_contract.exact(value['input_blobs'],INPUT_BLOBS)
            or hashlib.sha256(json.dumps(value['adapter'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=ADAPTER_SHA256):
        raise ValueError('the guarded quotient caller withdrawal paths change an exact natural entry, code/pool byte, alias or complete observer premise')
    require_reused_helper_boundary(root)
    return dict(value,entry=[dict(start=first,end=last) for first,last in SPANS])


def require_image(declared,image):
    if (type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256
            or not test_contract.exact(declared['unit'],UNIT)):
        raise ValueError('the guarded quotient caller withdrawal paths change the complete owned stock image or exact unit')
    for row in UNIT['pools']:
        if image[row['address']:row['address']+row['size']].hex()!=row['stock_hex']:
            raise ValueError('the guarded quotient caller withdrawal paths change a pinned exact stock pool or configuration byte')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for row in UNIT['aliases']:
        at=row['address']
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('the guarded quotient caller withdrawal paths relocate a different original native pointer')
        fixture[at:at+4]=row['alias'].to_bytes(4,'big');aliases.append(dict(row))
    return bytes(fixture),aliases


def fixture_for_case(declared,image,case):
    from kb import guarded_quotient_caller_withdrawal_matrix as matrix
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
            raise ValueError('the derivative scale caller changes a complete reused direct division source boundary')
