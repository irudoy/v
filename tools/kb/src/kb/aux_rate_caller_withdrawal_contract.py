"""Exact natural auxiliary rate caller withdrawal paths, literal inputs and declared pointer aliases."""

import hashlib
import json
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.aux-rate-caller-withdrawal-paths.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
ENTRIES=(429400,)
UNIT={'assembly': 'tools/sh-elf-run/stock_jk08a_aux_rate_caller_withdrawal.s',
 'code': [{'start': 138464, 'end': 138694},
          {'start': 429400, 'end': 429544},
          {'start': 574458, 'end': 574534}],
 'pools': [{'address': 138696, 'size': 4, 'stock_hex': 'ffff9818'},
           {'address': 138700, 'size': 4, 'stock_hex': '0000044e'},
           {'address': 429716, 'size': 2, 'stock_hex': '0fa0'},
           {'address': 429760, 'size': 4, 'stock_hex': 'ffff1ff4'},
           {'address': 429772, 'size': 4, 'stock_hex': 'ffff24c0'},
           {'address': 429792, 'size': 4, 'stock_hex': 'ffff424c'},
           {'address': 429796, 'size': 4, 'stock_hex': 'ffff2330'},
           {'address': 429800, 'size': 4, 'stock_hex': '00021ce0'},
           {'address': 429804, 'size': 4, 'stock_hex': '0008c3fa'},
           {'address': 574538, 'size': 2, 'stock_hex': '0bec'},
           {'address': 574540, 'size': 2, 'stock_hex': '0bee'},
           {'address': 574564, 'size': 4, 'stock_hex': 'ffff28f8'},
           {'address': 574568, 'size': 4, 'stock_hex': 'ffff4184'},
           {'address': 574572, 'size': 4, 'stock_hex': 'ffff244f'}],
 'aliases': [{'address': 138696, 'width': 4, 'original': 4294940696, 'alias': 16816152},
             {'address': 429760, 'width': 4, 'original': 4294909940, 'alias': 16785396},
             {'address': 429772, 'width': 4, 'original': 4294911168, 'alias': 16786624},
             {'address': 429792, 'width': 4, 'original': 4294918732, 'alias': 16794188},
             {'address': 429796, 'width': 4, 'original': 4294910768, 'alias': 16786224},
             {'address': 574564, 'width': 4, 'original': 4294912248, 'alias': 16787704},
             {'address': 574568, 'width': 4, 'original': 4294918532, 'alias': 16793988},
             {'address': 574572, 'width': 4, 'original': 4294911055, 'alias': 16786511}]}
CONTROLLED_CALIBRATION=[{'address': 138696, 'size': 4},
 {'address': 138700, 'size': 4},
 {'address': 429716, 'size': 2},
 {'address': 429760, 'size': 4},
 {'address': 429772, 'size': 4},
 {'address': 429792, 'size': 4},
 {'address': 429796, 'size': 4},
 {'address': 429800, 'size': 4},
 {'address': 429804, 'size': 4},
 {'address': 574538, 'size': 2},
 {'address': 574540, 'size': 2},
 {'address': 574564, 'size': 4},
 {'address': 574568, 'size': 4},
 {'address': 574572, 'size': 4}]
BOUND_SPANS=({'address': 138464, 'size': 230},
 {'address': 429400, 'size': 144},
 {'address': 574458, 'size': 76},
 {'address': 138696, 'size': 4},
 {'address': 138700, 'size': 4},
 {'address': 429716, 'size': 2},
 {'address': 429760, 'size': 4},
 {'address': 429772, 'size': 4},
 {'address': 429792, 'size': 4},
 {'address': 429796, 'size': 4},
 {'address': 429800, 'size': 4},
 {'address': 429804, 'size': 4},
 {'address': 574538, 'size': 2},
 {'address': 574540, 'size': 2},
 {'address': 574564, 'size': 4},
 {'address': 574568, 'size': 4},
 {'address': 574572, 'size': 4})
FLAGS=('native_identity_admission',
 'native_geometry_inference',
 'scale_admission',
 'units_admission',
 'natural_caller_reachability',
 'hardware_qualification',
 'stock_function_stubs',
 'native_publication')
CONFIGURATION=[]
INPUT_BLOBS=[]
ADAPTER_SHA256='fd3b7fab92efb71a3aa1935d783853a64c4f3f2537a54f41791e86eb5b553da0'
HELPER_ENTRIES=(138464, 574458)
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
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-aux-rate-caller-withdrawal'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or not test_contract.exact((value['entries'],value['observer'],value['context_bytes'],value['frame_bytes'],
                value['frame_prefix']),(list(ENTRIES),OBSERVER,80,192,160))
            or any(value[name] is not False for name in FLAGS)
            or not test_contract.exact(value['unit'],UNIT)
            or not test_contract.exact(value['controlled_calibration'],CONTROLLED_CALIBRATION)
            or not test_contract.exact(value['configuration'],CONFIGURATION)
            or not test_contract.exact(value['input_blobs'],INPUT_BLOBS)
            or hashlib.sha256(json.dumps(value['adapter'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=ADAPTER_SHA256):
        raise ValueError('the auxiliary rate caller withdrawal paths change an exact natural entry, code/pool byte, alias or complete observer premise')
    require_reused_helper_boundary(root)
    return dict(value,entry=[dict(start=first,end=last) for first,last in SPANS])


def require_image(declared,image):
    if (type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256
            or not test_contract.exact(declared['unit'],UNIT)):
        raise ValueError('the auxiliary rate caller withdrawal paths change the complete owned stock image or exact unit')
    for row in UNIT['pools']:
        if image[row['address']:row['address']+row['size']].hex()!=row['stock_hex']:
            raise ValueError('the auxiliary rate caller withdrawal paths change a pinned exact stock pool or configuration byte')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for row in UNIT['aliases']:
        at=row['address']
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('the auxiliary rate caller withdrawal paths relocate a different original native pointer')
        fixture[at:at+4]=row['alias'].to_bytes(4,'big');aliases.append(dict(row))
    return bytes(fixture),aliases


def fixture_for_case(declared,image,case):
    from kb import aux_rate_caller_withdrawal_matrix as matrix
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
            raise ValueError('the auxiliary rate caller changes a complete reused signed/unsigned division,byte-curve and standard implicit-byte source boundary')
