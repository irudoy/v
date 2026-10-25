"""Exact natural clamp latch caller withdrawal paths, literal inputs and declared pointer aliases."""

import hashlib
import json
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.clamp-latch-caller-withdrawal-paths.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
ENTRIES=(234262,)
UNIT={'assembly': 'tools/sh-elf-run/stock_jk08a_clamp_latch_caller_withdrawal.s',
 'code': [{'start': 140688, 'end': 140698}, {'start': 234262, 'end': 234488}],
 'pools': [{'address': 34450, 'size': 1, 'stock_hex': '00'},
           {'address': 34451, 'size': 1, 'stock_hex': 'ff'},
           {'address': 35710, 'size': 1, 'stock_hex': '64'},
           {'address': 234580, 'size': 4, 'stock_hex': 'ffff1e60'},
           {'address': 234584, 'size': 4, 'stock_hex': 'ffff1114'},
           {'address': 234588, 'size': 4, 'stock_hex': 'ffff55bc'},
           {'address': 234608, 'size': 4, 'stock_hex': 'ffff2459'},
           {'address': 234612, 'size': 4, 'stock_hex': '00008b7e'},
           {'address': 234616, 'size': 4, 'stock_hex': 'ffff256a'},
           {'address': 234620, 'size': 4, 'stock_hex': 'ffff4185'},
           {'address': 234624, 'size': 4, 'stock_hex': 'ffff2451'},
           {'address': 234628, 'size': 4, 'stock_hex': 'ffff2449'},
           {'address': 234632, 'size': 4, 'stock_hex': 'ffff424c'},
           {'address': 234636, 'size': 4, 'stock_hex': 'ffff11d4'},
           {'address': 234640, 'size': 4, 'stock_hex': 'ffff22dc'},
           {'address': 234644, 'size': 4, 'stock_hex': '00022590'},
           {'address': 234648, 'size': 4, 'stock_hex': 'ffff1048'},
           {'address': 234652, 'size': 4, 'stock_hex': '00008692'},
           {'address': 234656, 'size': 4, 'stock_hex': 'ffff421c'},
           {'address': 234660, 'size': 4, 'stock_hex': 'ffff1026'}],
 'aliases': [{'address': 234580, 'width': 4, 'original': 4294909536, 'alias': 16784992},
             {'address': 234584, 'width': 4, 'original': 4294906132, 'alias': 16781588},
             {'address': 234588, 'width': 4, 'original': 4294923708, 'alias': 16799164},
             {'address': 234608, 'width': 4, 'original': 4294911065, 'alias': 16786521},
             {'address': 234616, 'width': 4, 'original': 4294911338, 'alias': 16786794},
             {'address': 234620, 'width': 4, 'original': 4294918533, 'alias': 16793989},
             {'address': 234624, 'width': 4, 'original': 4294911057, 'alias': 16786513},
             {'address': 234628, 'width': 4, 'original': 4294911049, 'alias': 16786505},
             {'address': 234632, 'width': 4, 'original': 4294918732, 'alias': 16794188},
             {'address': 234636, 'width': 4, 'original': 4294906324, 'alias': 16781780},
             {'address': 234640, 'width': 4, 'original': 4294910684, 'alias': 16786140},
             {'address': 234648, 'width': 4, 'original': 4294905928, 'alias': 16781384},
             {'address': 234656, 'width': 4, 'original': 4294918684, 'alias': 16794140},
             {'address': 234660, 'width': 4, 'original': 4294905894, 'alias': 16781350}]}
CONTROLLED_CALIBRATION=[{'address': 34450, 'size': 1},
 {'address': 34451, 'size': 1},
 {'address': 35710, 'size': 1},
 {'address': 234580, 'size': 4},
 {'address': 234584, 'size': 4},
 {'address': 234588, 'size': 4},
 {'address': 234608, 'size': 4},
 {'address': 234612, 'size': 4},
 {'address': 234616, 'size': 4},
 {'address': 234620, 'size': 4},
 {'address': 234624, 'size': 4},
 {'address': 234628, 'size': 4},
 {'address': 234632, 'size': 4},
 {'address': 234636, 'size': 4},
 {'address': 234640, 'size': 4},
 {'address': 234644, 'size': 4},
 {'address': 234648, 'size': 4},
 {'address': 234652, 'size': 4},
 {'address': 234656, 'size': 4},
 {'address': 234660, 'size': 4}]
BOUND_SPANS=({'address': 140688, 'size': 10},
 {'address': 234262, 'size': 226},
 {'address': 34450, 'size': 1},
 {'address': 34451, 'size': 1},
 {'address': 35710, 'size': 1},
 {'address': 234580, 'size': 4},
 {'address': 234584, 'size': 4},
 {'address': 234588, 'size': 4},
 {'address': 234608, 'size': 4},
 {'address': 234612, 'size': 4},
 {'address': 234616, 'size': 4},
 {'address': 234620, 'size': 4},
 {'address': 234624, 'size': 4},
 {'address': 234628, 'size': 4},
 {'address': 234632, 'size': 4},
 {'address': 234636, 'size': 4},
 {'address': 234640, 'size': 4},
 {'address': 234644, 'size': 4},
 {'address': 234648, 'size': 4},
 {'address': 234652, 'size': 4},
 {'address': 234656, 'size': 4},
 {'address': 234660, 'size': 4})
FLAGS=('native_identity_admission',
 'native_geometry_inference',
 'scale_admission',
 'units_admission',
 'natural_caller_reachability',
 'hardware_qualification',
 'stock_function_stubs',
 'native_publication')
CONFIGURATION=[{'address': 34450, 'field': 'config_8692', 'size': 1},
 {'address': 34451, 'field': 'config_8693', 'size': 1},
 {'address': 35710, 'field': 'config_8b7e', 'size': 1}]
INPUT_BLOBS=[]
ADAPTER_SHA256='667b236fd1a9d163450397db9669545db40124a7ec29f02c427ff2ba1d9e6b33'
HELPER_ENTRIES=(140688,)
REUSED_HELPER_FILES_SHA256={}
FUNCTIONS=(*ENTRIES,*HELPER_ENTRIES)
SPANS=tuple((row['start'],row['end']) for row in UNIT['code'])


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','entries','observer',
            'context_bytes','frame_bytes','frame_prefix','unit','controlled_calibration','configuration','input_blobs','adapter',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-clamp-latch-caller-withdrawal'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or not test_contract.exact((value['entries'],value['observer'],value['context_bytes'],value['frame_bytes'],
                value['frame_prefix']),(list(ENTRIES),OBSERVER,80,192,160))
            or any(value[name] is not False for name in FLAGS)
            or not test_contract.exact(value['unit'],UNIT)
            or not test_contract.exact(value['controlled_calibration'],CONTROLLED_CALIBRATION)
            or not test_contract.exact(value['configuration'],CONFIGURATION)
            or not test_contract.exact(value['input_blobs'],INPUT_BLOBS)
            or hashlib.sha256(json.dumps(value['adapter'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=ADAPTER_SHA256):
        raise ValueError('the clamp latch caller withdrawal paths change an exact natural entry, code/pool byte, alias or complete observer premise')
    require_reused_helper_boundary(root)
    return dict(value,entry=[dict(start=first,end=last) for first,last in SPANS])


def require_image(declared,image):
    if (type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256
            or not test_contract.exact(declared['unit'],UNIT)):
        raise ValueError('the clamp latch caller withdrawal paths change the complete owned stock image or exact unit')
    for row in UNIT['pools']:
        if image[row['address']:row['address']+row['size']].hex()!=row['stock_hex']:
            raise ValueError('the clamp latch caller withdrawal paths change a pinned exact stock pool or configuration byte')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for row in UNIT['aliases']:
        at=row['address']
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('the clamp latch caller withdrawal paths relocate a different original native pointer')
        fixture[at:at+4]=row['alias'].to_bytes(4,'big');aliases.append(dict(row))
    return bytes(fixture),aliases


def fixture_for_case(declared,image,case):
    from kb import clamp_latch_caller_withdrawal_matrix as matrix
    matrix.require_case(case);fixture,aliases=independent_fixture(declared,image);fixture=bytearray(fixture)
    for row in CONFIGURATION:
        at,size=row['address'],row['size'];fixture[at:at+size]=case[row['field']].to_bytes(size,'big')
    return bytes(fixture),aliases


def require_reused_helper_boundary(root):
    for name,wanted in REUSED_HELPER_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=wanted:
            raise ValueError('the clamp latch caller changes a complete reused signed/unsigned division,byte-curve and standard implicit-byte source boundary')
