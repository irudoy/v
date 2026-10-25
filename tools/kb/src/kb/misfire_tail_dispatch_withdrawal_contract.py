"""Exact natural misfire tail dispatch withdrawal paths, literal inputs and declared pointer aliases."""

import hashlib
import json
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.misfire-tail-dispatch-withdrawal-paths.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
ENTRIES=(509076,)
UNIT={'assembly': 'tools/sh-elf-run/stock_jk08a_misfire_tail_dispatch_withdrawal.s',
 'code': [{'start': 509076, 'end': 509088},
          {'start': 509152, 'end': 509226},
          {'start': 553680, 'end': 553886}],
 'pools': [{'address': 33620, 'size': 1, 'stock_hex': '01'},
           {'address': 34390, 'size': 1, 'stock_hex': '01'},
           {'address': 35802, 'size': 1, 'stock_hex': '20'},
           {'address': 100046, 'size': 1, 'stock_hex': '80'},
           {'address': 509088, 'size': 4, 'stock_hex': '000872d0'},
           {'address': 509228, 'size': 4, 'stock_hex': 'ffff4094'},
           {'address': 509232, 'size': 4, 'stock_hex': 'ffff24c4'},
           {'address': 509236, 'size': 4, 'stock_hex': 'ffff119c'},
           {'address': 509240, 'size': 4, 'stock_hex': '00008bda'},
           {'address': 553886, 'size': 2, 'stock_hex': '03e8'},
           {'address': 553888, 'size': 4, 'stock_hex': 'ffff4094'},
           {'address': 553892, 'size': 4, 'stock_hex': '000186c8'},
           {'address': 553896, 'size': 4, 'stock_hex': '00008354'},
           {'address': 553900, 'size': 4, 'stock_hex': 'ffff4240'},
           {'address': 553904, 'size': 4, 'stock_hex': '00008656'},
           {'address': 553908, 'size': 4, 'stock_hex': 'ffff41a9'},
           {'address': 553912, 'size': 4, 'stock_hex': 'ffff36d8'},
           {'address': 553916, 'size': 4, 'stock_hex': 'ffff43c7'}],
 'aliases': [{'address': 509228, 'width': 4, 'original': 4294918292, 'alias': 16793748},
             {'address': 509232, 'width': 4, 'original': 4294911172, 'alias': 16786628},
             {'address': 509236, 'width': 4, 'original': 4294906268, 'alias': 16781724},
             {'address': 553888, 'width': 4, 'original': 4294918292, 'alias': 16793748},
             {'address': 553900, 'width': 4, 'original': 4294918720, 'alias': 16794176},
             {'address': 553908, 'width': 4, 'original': 4294918569, 'alias': 16794025},
             {'address': 553912, 'width': 4, 'original': 4294915800, 'alias': 16791256},
             {'address': 553916, 'width': 4, 'original': 4294919111, 'alias': 16794567}]}
CONTROLLED_CALIBRATION=[{'address': 33620, 'size': 1},
 {'address': 34390, 'size': 1},
 {'address': 35802, 'size': 1},
 {'address': 100046, 'size': 1},
 {'address': 509088, 'size': 4},
 {'address': 509228, 'size': 4},
 {'address': 509232, 'size': 4},
 {'address': 509236, 'size': 4},
 {'address': 509240, 'size': 4},
 {'address': 553886, 'size': 2},
 {'address': 553888, 'size': 4},
 {'address': 553892, 'size': 4},
 {'address': 553896, 'size': 4},
 {'address': 553900, 'size': 4},
 {'address': 553904, 'size': 4},
 {'address': 553908, 'size': 4},
 {'address': 553912, 'size': 4},
 {'address': 553916, 'size': 4}]
BOUND_SPANS=({'address': 509076, 'size': 12},
 {'address': 509152, 'size': 74},
 {'address': 553680, 'size': 206},
 {'address': 33620, 'size': 1},
 {'address': 34390, 'size': 1},
 {'address': 35802, 'size': 1},
 {'address': 100046, 'size': 1},
 {'address': 509088, 'size': 4},
 {'address': 509228, 'size': 4},
 {'address': 509232, 'size': 4},
 {'address': 509236, 'size': 4},
 {'address': 509240, 'size': 4},
 {'address': 553886, 'size': 2},
 {'address': 553888, 'size': 4},
 {'address': 553892, 'size': 4},
 {'address': 553896, 'size': 4},
 {'address': 553900, 'size': 4},
 {'address': 553904, 'size': 4},
 {'address': 553908, 'size': 4},
 {'address': 553912, 'size': 4},
 {'address': 553916, 'size': 4})
FLAGS=('native_identity_admission',
 'native_geometry_inference',
 'scale_admission',
 'units_admission',
 'natural_caller_reachability',
 'hardware_qualification',
 'stock_function_stubs',
 'native_publication')
CONFIGURATION=[{'address': 33620, 'field': 'config_8354', 'size': 1},
 {'address': 34390, 'field': 'config_8656', 'size': 1},
 {'address': 35802, 'field': 'config_8bda', 'size': 1},
 {'address': 100046, 'field': 'config_186ce', 'size': 1}]
INPUT_BLOBS=[]
ADAPTER_SHA256='1e90b2fe465bfac45383d389c9964cc06fee241ccb1edd4212a19d1ea922da76'
HELPER_ENTRIES=(509152, 553680)
REUSED_HELPER_FILES_SHA256={}
FUNCTIONS=(*ENTRIES,*HELPER_ENTRIES)
SPANS=tuple((row['start'],row['end']) for row in UNIT['code'])


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','entries','observer',
            'context_bytes','frame_bytes','frame_prefix','unit','controlled_calibration','configuration','input_blobs','adapter',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-misfire-tail-dispatch-withdrawal'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or not test_contract.exact((value['entries'],value['observer'],value['context_bytes'],value['frame_bytes'],
                value['frame_prefix']),(list(ENTRIES),OBSERVER,80,192,160))
            or any(value[name] is not False for name in FLAGS)
            or not test_contract.exact(value['unit'],UNIT)
            or not test_contract.exact(value['controlled_calibration'],CONTROLLED_CALIBRATION)
            or not test_contract.exact(value['configuration'],CONFIGURATION)
            or not test_contract.exact(value['input_blobs'],INPUT_BLOBS)
            or hashlib.sha256(json.dumps(value['adapter'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=ADAPTER_SHA256):
        raise ValueError('the misfire tail dispatch withdrawal paths change an exact natural entry, code/pool byte, alias or complete observer premise')
    require_reused_helper_boundary(root)
    return dict(value,entry=[dict(start=first,end=last) for first,last in SPANS])


def require_image(declared,image):
    if (type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256
            or not test_contract.exact(declared['unit'],UNIT)):
        raise ValueError('the misfire tail dispatch withdrawal paths change the complete owned stock image or exact unit')
    for row in UNIT['pools']:
        if image[row['address']:row['address']+row['size']].hex()!=row['stock_hex']:
            raise ValueError('the misfire tail dispatch withdrawal paths change a pinned exact stock pool or configuration byte')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for row in UNIT['aliases']:
        at=row['address']
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('the misfire tail dispatch withdrawal paths relocate a different original native pointer')
        fixture[at:at+4]=row['alias'].to_bytes(4,'big');aliases.append(dict(row))
    return bytes(fixture),aliases


def fixture_for_case(declared,image,case):
    from kb import misfire_tail_dispatch_withdrawal_matrix as matrix
    matrix.require_case(case);fixture,aliases=independent_fixture(declared,image);fixture=bytearray(fixture)
    for row in CONFIGURATION:
        at,size=row['address'],row['size'];fixture[at:at+size]=case[row['field']].to_bytes(size,'big')
    return bytes(fixture),aliases


def require_reused_helper_boundary(root):
    for name,wanted in REUSED_HELPER_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=wanted:
            raise ValueError('the misfire tail dispatch changes a complete declared reused source boundary')
