"""Exact natural threshold window reader caller withdrawal paths, literal inputs and declared pointer aliases."""

import hashlib
import json
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.threshold-window-reader-withdrawal-paths.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
ENTRIES=(542684,)
UNIT={'assembly': 'tools/sh-elf-run/stock_jk08a_threshold_window_reader_withdrawal.s',
 'code': [{'start': 138172, 'end': 138454}, {'start': 542684, 'end': 542878}],
 'pools': [{'address': 138456, 'size': 4, 'stock_hex': 'ffff9818'},
           {'address': 138460, 'size': 4, 'stock_hex': '0000044e'},
           {'address': 542878, 'size': 2, 'stock_hex': '05e0'},
           {'address': 543200, 'size': 4, 'stock_hex': 'ffff4124'},
           {'address': 543204, 'size': 4, 'stock_hex': 'ffff424c'},
           {'address': 543208, 'size': 4, 'stock_hex': 'ffff119c'},
           {'address': 543212, 'size': 4, 'stock_hex': '00021bbc'},
           {'address': 543216, 'size': 4, 'stock_hex': 'ffff39c4'}],
 'aliases': [{'address': 138456, 'width': 4, 'original': 4294940696, 'alias': 16816152},
             {'address': 543200, 'width': 4, 'original': 4294918436, 'alias': 16793892},
             {'address': 543204, 'width': 4, 'original': 4294918732, 'alias': 16794188},
             {'address': 543208, 'width': 4, 'original': 4294906268, 'alias': 16781724},
             {'address': 543216, 'width': 4, 'original': 4294916548, 'alias': 16792004}]}
CONTROLLED_CALIBRATION=[{'address': 138456, 'size': 4},
 {'address': 138460, 'size': 4},
 {'address': 542878, 'size': 2},
 {'address': 543200, 'size': 4},
 {'address': 543204, 'size': 4},
 {'address': 543208, 'size': 4},
 {'address': 543212, 'size': 4},
 {'address': 543216, 'size': 4}]
BOUND_SPANS=({'address': 138172, 'size': 282},
 {'address': 542684, 'size': 194},
 {'address': 138456, 'size': 4},
 {'address': 138460, 'size': 4},
 {'address': 542878, 'size': 2},
 {'address': 543200, 'size': 4},
 {'address': 543204, 'size': 4},
 {'address': 543208, 'size': 4},
 {'address': 543212, 'size': 4},
 {'address': 543216, 'size': 4})
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
ADAPTER_SHA256='4300627ddffb41c989a6208c15d7b651aa3d20c5107cda7a27ae2d3853d6d4fa'
HELPER_ENTRIES=(138172,)
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
 'tools/sh-elf-run/stock_jk08a_implicit_byte_curve.s': 'e88b06e655a2fb1454632474fb189e602b48e983374b0c21a43302d6ae044399',
 'tools/sh-elf-run/stock_implicit_byte_curve_harness.c': '5ed963a79e7cf3311476d426f4c0bdf55332a344646c1f477a53fcb3f9597ad6'}
FUNCTIONS=(*ENTRIES,*HELPER_ENTRIES)
SPANS=tuple((row['start'],row['end']) for row in UNIT['code'])


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','entries','observer',
            'context_bytes','frame_bytes','frame_prefix','unit','controlled_calibration','configuration','input_blobs','adapter',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-threshold-window-reader-withdrawal'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or not test_contract.exact((value['entries'],value['observer'],value['context_bytes'],value['frame_bytes'],
                value['frame_prefix']),(list(ENTRIES),OBSERVER,80,192,160))
            or any(value[name] is not False for name in FLAGS)
            or not test_contract.exact(value['unit'],UNIT)
            or not test_contract.exact(value['controlled_calibration'],CONTROLLED_CALIBRATION)
            or not test_contract.exact(value['configuration'],CONFIGURATION)
            or not test_contract.exact(value['input_blobs'],INPUT_BLOBS)
            or hashlib.sha256(json.dumps(value['adapter'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=ADAPTER_SHA256):
        raise ValueError('the threshold window reader caller withdrawal paths change an exact natural entry, code/pool byte, alias or complete observer premise')
    require_reused_helper_boundary(root)
    return dict(value,entry=[dict(start=first,end=last) for first,last in SPANS])


def require_image(declared,image):
    if (type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256
            or not test_contract.exact(declared['unit'],UNIT)):
        raise ValueError('the threshold window reader caller withdrawal paths change the complete owned stock image or exact unit')
    for row in UNIT['pools']:
        if image[row['address']:row['address']+row['size']].hex()!=row['stock_hex']:
            raise ValueError('the threshold window reader caller withdrawal paths change a pinned exact stock pool or configuration byte')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for row in UNIT['aliases']:
        at=row['address']
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('the threshold window reader caller withdrawal paths relocate a different original native pointer')
        fixture[at:at+4]=row['alias'].to_bytes(4,'big');aliases.append(dict(row))
    return bytes(fixture),aliases


def fixture_for_case(declared,image,case):
    from kb import threshold_window_reader_withdrawal_matrix as matrix
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
            raise ValueError('the threshold window reader caller changes a complete reused signed/unsigned division,byte-curve and standard implicit-byte source boundary')
