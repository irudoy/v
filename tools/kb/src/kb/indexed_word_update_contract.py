"""Exact natural indexed word update paths, literal inputs and declared pointer aliases."""

import hashlib
import json
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.indexed-word-update-paths.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
ENTRIES=(335924,)
UNIT={'assembly': 'tools/sh-elf-run/stock_jk08a_indexed_word_update.s',
 'code': [{'start': 335924, 'end': 336108}],
 'pools': [{'address': 34814, 'size': 1, 'stock_hex': '05'},
           {'address': 36242, 'size': 1, 'stock_hex': '7a'},
           {'address': 336168, 'size': 2, 'stock_hex': 'ff0f'},
           {'address': 336176, 'size': 2, 'stock_hex': '01a2'},
           {'address': 336178, 'size': 2, 'stock_hex': '0473'},
           {'address': 336240, 'size': 4, 'stock_hex': '00008d92'},
           {'address': 336244, 'size': 4, 'stock_hex': 'ffff120e'},
           {'address': 336248, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 336256, 'size': 4, 'stock_hex': '000087fe'},
           {'address': 336260, 'size': 4, 'stock_hex': 'ffff22dc'},
           {'address': 336264, 'size': 4, 'stock_hex': 'ffff2330'}],
 'aliases': [{'address': 336244, 'width': 4, 'original': 4294906382, 'alias': 16781838},
             {'address': 336248, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 336260, 'width': 4, 'original': 4294910684, 'alias': 16786140},
             {'address': 336264, 'width': 4, 'original': 4294910768, 'alias': 16786224}]}
CONTROLLED_CALIBRATION=[{'address': 34814, 'size': 1},
 {'address': 36242, 'size': 1},
 {'address': 336168, 'size': 2},
 {'address': 336176, 'size': 2},
 {'address': 336178, 'size': 2},
 {'address': 336240, 'size': 4},
 {'address': 336244, 'size': 4},
 {'address': 336248, 'size': 4},
 {'address': 336256, 'size': 4},
 {'address': 336260, 'size': 4},
 {'address': 336264, 'size': 4}]
BOUND_SPANS=({'address': 335924, 'size': 184},
 {'address': 34814, 'size': 1},
 {'address': 36242, 'size': 1},
 {'address': 336168, 'size': 2},
 {'address': 336176, 'size': 2},
 {'address': 336178, 'size': 2},
 {'address': 336240, 'size': 4},
 {'address': 336244, 'size': 4},
 {'address': 336248, 'size': 4},
 {'address': 336256, 'size': 4},
 {'address': 336260, 'size': 4},
 {'address': 336264, 'size': 4})
FLAGS=('native_identity_admission',
 'native_geometry_inference',
 'scale_admission',
 'units_admission',
 'natural_caller_reachability',
 'hardware_qualification',
 'stock_function_stubs',
 'native_publication')
CONFIGURATION=[{'address': 36242, 'field': 'enable_mask', 'size': 1},
 {'address': 34814, 'field': 'threshold_factor', 'size': 1}]
ADAPTER_SHA256='098c04cd8c9fcd2b7b7d13d4edd69796b2c0d26fc72f33a25c680fc173b75350'
FUNCTIONS=ENTRIES
SPANS=tuple((row['start'],row['end']) for row in UNIT['code'])


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','entries','observer',
            'context_bytes','frame_bytes','frame_prefix','unit','controlled_calibration','configuration','adapter',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-indexed-word-update'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or not test_contract.exact((value['entries'],value['observer'],value['context_bytes'],value['frame_bytes'],
                value['frame_prefix']),(list(ENTRIES),OBSERVER,80,192,160))
            or any(value[name] is not False for name in FLAGS)
            or not test_contract.exact(value['unit'],UNIT)
            or not test_contract.exact(value['controlled_calibration'],CONTROLLED_CALIBRATION)
            or not test_contract.exact(value['configuration'],CONFIGURATION)
            or hashlib.sha256(json.dumps(value['adapter'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=ADAPTER_SHA256):
        raise ValueError('the indexed word update paths change an exact natural entry, code/pool byte, alias or complete observer premise')
    return dict(value,entry=[dict(start=first,end=last) for first,last in SPANS])


def require_image(declared,image):
    if (type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256
            or not test_contract.exact(declared['unit'],UNIT)):
        raise ValueError('the indexed word update paths change the complete owned stock image or exact unit')
    for row in UNIT['pools']:
        if image[row['address']:row['address']+row['size']].hex()!=row['stock_hex']:
            raise ValueError('the indexed word update paths change a pinned exact stock pool or configuration byte')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for row in UNIT['aliases']:
        at=row['address']
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('the indexed word update paths relocate a different original native pointer')
        fixture[at:at+4]=row['alias'].to_bytes(4,'big');aliases.append(dict(row))
    return bytes(fixture),aliases


def fixture_for_case(declared,image,case):
    from kb import indexed_word_update_matrix as matrix
    matrix.require_case(case);fixture,aliases=independent_fixture(declared,image);fixture=bytearray(fixture)
    for row in CONFIGURATION:
        at,size=row['address'],row['size'];fixture[at:at+size]=case[row['field']].to_bytes(size,'big')
    return bytes(fixture),aliases
