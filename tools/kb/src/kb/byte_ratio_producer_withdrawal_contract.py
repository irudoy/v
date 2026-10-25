"""Exact natural byte ratio producer withdrawal paths, literal inputs and declared pointer aliases."""

import hashlib
import json
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.byte-ratio-producer-withdrawal-paths.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
ENTRIES=(306796,)
UNIT={'assembly': 'tools/sh-elf-run/stock_jk08a_byte_ratio_producer_withdrawal.s',
 'code': [{'start': 138172, 'end': 138454},
          {'start': 138464, 'end': 138694},
          {'start': 140552, 'end': 140570},
          {'start': 306796, 'end': 306860},
          {'start': 306884, 'end': 307000}],
 'pools': [{'address': 34893, 'size': 1, 'stock_hex': '80'},
           {'address': 35692, 'size': 1, 'stock_hex': '0e'},
           {'address': 138456, 'size': 4, 'stock_hex': 'ffff9818'},
           {'address': 138460, 'size': 4, 'stock_hex': '0000044e'},
           {'address': 138696, 'size': 4, 'stock_hex': 'ffff9818'},
           {'address': 138700, 'size': 4, 'stock_hex': '0000044e'},
           {'address': 306878, 'size': 2, 'stock_hex': '0250'},
           {'address': 306880, 'size': 2, 'stock_hex': '052c'},
           {'address': 306882, 'size': 2, 'stock_hex': '03a4'},
           {'address': 307092, 'size': 4, 'stock_hex': 'ffff119c'},
           {'address': 307116, 'size': 4, 'stock_hex': '00021ce0'},
           {'address': 307128, 'size': 4, 'stock_hex': '00021bbc'},
           {'address': 307140, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 307144, 'size': 4, 'stock_hex': '0000884d'},
           {'address': 307148, 'size': 4, 'stock_hex': '00008b6c'},
           {'address': 307152, 'size': 4, 'stock_hex': '00022508'},
           {'address': 307156, 'size': 4, 'stock_hex': 'ffff23bc'}],
 'aliases': [{'address': 138456, 'width': 4, 'original': 4294940696, 'alias': 16816152},
             {'address': 138696, 'width': 4, 'original': 4294940696, 'alias': 16816152},
             {'address': 307092, 'width': 4, 'original': 4294906268, 'alias': 16781724},
             {'address': 307140, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 307156, 'width': 4, 'original': 4294910908, 'alias': 16786364}]}
CONTROLLED_CALIBRATION=[{'address': 34893, 'size': 1},
 {'address': 35692, 'size': 1},
 {'address': 138456, 'size': 4},
 {'address': 138460, 'size': 4},
 {'address': 138696, 'size': 4},
 {'address': 138700, 'size': 4},
 {'address': 306878, 'size': 2},
 {'address': 306880, 'size': 2},
 {'address': 306882, 'size': 2},
 {'address': 307092, 'size': 4},
 {'address': 307116, 'size': 4},
 {'address': 307128, 'size': 4},
 {'address': 307140, 'size': 4},
 {'address': 307144, 'size': 4},
 {'address': 307148, 'size': 4},
 {'address': 307152, 'size': 4},
 {'address': 307156, 'size': 4}]
BOUND_SPANS=({'address': 138172, 'size': 282},
 {'address': 138464, 'size': 230},
 {'address': 140552, 'size': 18},
 {'address': 306796, 'size': 64},
 {'address': 306884, 'size': 116},
 {'address': 34893, 'size': 1},
 {'address': 35692, 'size': 1},
 {'address': 138456, 'size': 4},
 {'address': 138460, 'size': 4},
 {'address': 138696, 'size': 4},
 {'address': 138700, 'size': 4},
 {'address': 306878, 'size': 2},
 {'address': 306880, 'size': 2},
 {'address': 306882, 'size': 2},
 {'address': 307092, 'size': 4},
 {'address': 307116, 'size': 4},
 {'address': 307128, 'size': 4},
 {'address': 307140, 'size': 4},
 {'address': 307144, 'size': 4},
 {'address': 307148, 'size': 4},
 {'address': 307152, 'size': 4},
 {'address': 307156, 'size': 4})
FLAGS=('native_identity_admission',
 'native_geometry_inference',
 'scale_admission',
 'units_admission',
 'natural_caller_reachability',
 'hardware_qualification',
 'stock_function_stubs',
 'native_publication')
CONFIGURATION=[{'address': 34893, 'field': 'config_884d', 'size': 1}, {'address': 35692, 'field': 'config_8b6c', 'size': 1}]
INPUT_BLOBS=[]
ADAPTER_SHA256='f4f04816d42cefd30cb0a490ab689071da0dcd71f8f2780619be27baa5b91950'
HELPER_ENTRIES=(138172, 138464, 140552)
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
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-byte-ratio-producer-withdrawal'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or not test_contract.exact((value['entries'],value['observer'],value['context_bytes'],value['frame_bytes'],
                value['frame_prefix']),(list(ENTRIES),OBSERVER,80,192,160))
            or any(value[name] is not False for name in FLAGS)
            or not test_contract.exact(value['unit'],UNIT)
            or not test_contract.exact(value['controlled_calibration'],CONTROLLED_CALIBRATION)
            or not test_contract.exact(value['configuration'],CONFIGURATION)
            or not test_contract.exact(value['input_blobs'],INPUT_BLOBS)
            or hashlib.sha256(json.dumps(value['adapter'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=ADAPTER_SHA256):
        raise ValueError('the byte ratio producer withdrawal paths change an exact natural entry, code/pool byte, alias or complete observer premise')
    require_reused_helper_boundary(root)
    return dict(value,entry=[dict(start=first,end=last) for first,last in SPANS])


def require_image(declared,image):
    if (type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256
            or not test_contract.exact(declared['unit'],UNIT)):
        raise ValueError('the byte ratio producer withdrawal paths change the complete owned stock image or exact unit')
    for row in UNIT['pools']:
        if image[row['address']:row['address']+row['size']].hex()!=row['stock_hex']:
            raise ValueError('the byte ratio producer withdrawal paths change a pinned exact stock pool or configuration byte')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for row in UNIT['aliases']:
        at=row['address']
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('the byte ratio producer withdrawal paths relocate a different original native pointer')
        fixture[at:at+4]=row['alias'].to_bytes(4,'big');aliases.append(dict(row))
    return bytes(fixture),aliases


def fixture_for_case(declared,image,case):
    from kb import byte_ratio_producer_withdrawal_matrix as matrix
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
            raise ValueError('the byte ratio producer changes a complete reused direct signed/unsigned-divider source boundary')
