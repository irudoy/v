"""Exact natural scalar RAM word paths, literal inputs and declared pointer aliases."""

import hashlib
import json
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.scalar-ram-word-paths.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
ENTRIES=(451728, 484224, 831946)
UNIT={'assembly': 'tools/sh-elf-run/stock_jk08a_scalar_ram_word.s',
 'code': [{'start': 451728, 'end': 451784},
          {'start': 484224, 'end': 484278},
          {'start': 831946, 'end': 831992}],
 'pools': [{'address': 37030, 'size': 2, 'stock_hex': '03e8'},
           {'address': 37032, 'size': 2, 'stock_hex': '03e8'},
           {'address': 37832, 'size': 2, 'stock_hex': '0000'},
           {'address': 451810, 'size': 2, 'stock_hex': '04da'},
           {'address': 451816, 'size': 2, 'stock_hex': '04e2'},
           {'address': 452036, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 452076, 'size': 4, 'stock_hex': '000093c8'},
           {'address': 452080, 'size': 4, 'stock_hex': '00346dc5'},
           {'address': 484424, 'size': 2, 'stock_hex': '03ac'},
           {'address': 484426, 'size': 2, 'stock_hex': '0c26'},
           {'address': 484436, 'size': 4, 'stock_hex': 'ffff39c4'},
           {'address': 484464, 'size': 4, 'stock_hex': 'ffff28f8'},
           {'address': 484468, 'size': 4, 'stock_hex': '000090a6'},
           {'address': 831994, 'size': 2, 'stock_hex': '01a2'},
           {'address': 832012, 'size': 4, 'stock_hex': 'ffff36d8'},
           {'address': 832032, 'size': 4, 'stock_hex': 'ffff2898'}],
 'aliases': [{'address': 452036, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 484436, 'width': 4, 'original': 4294916548, 'alias': 16792004},
             {'address': 484464, 'width': 4, 'original': 4294912248, 'alias': 16787704},
             {'address': 832012, 'width': 4, 'original': 4294915800, 'alias': 16791256},
             {'address': 832032, 'width': 4, 'original': 4294912152, 'alias': 16787608}]}
CONTROLLED_CALIBRATION=[{'address': 37030, 'size': 2},
 {'address': 37032, 'size': 2},
 {'address': 37832, 'size': 2},
 {'address': 451810, 'size': 2},
 {'address': 451816, 'size': 2},
 {'address': 452036, 'size': 4},
 {'address': 452076, 'size': 4},
 {'address': 452080, 'size': 4},
 {'address': 484424, 'size': 2},
 {'address': 484426, 'size': 2},
 {'address': 484436, 'size': 4},
 {'address': 484464, 'size': 4},
 {'address': 484468, 'size': 4},
 {'address': 831994, 'size': 2},
 {'address': 832012, 'size': 4},
 {'address': 832032, 'size': 4}]
BOUND_SPANS=({'address': 451728, 'size': 56},
 {'address': 484224, 'size': 54},
 {'address': 831946, 'size': 46},
 {'address': 37030, 'size': 2},
 {'address': 37032, 'size': 2},
 {'address': 37832, 'size': 2},
 {'address': 451810, 'size': 2},
 {'address': 451816, 'size': 2},
 {'address': 452036, 'size': 4},
 {'address': 452076, 'size': 4},
 {'address': 452080, 'size': 4},
 {'address': 484424, 'size': 2},
 {'address': 484426, 'size': 2},
 {'address': 484436, 'size': 4},
 {'address': 484464, 'size': 4},
 {'address': 484468, 'size': 4},
 {'address': 831994, 'size': 2},
 {'address': 832012, 'size': 4},
 {'address': 832032, 'size': 4})
FLAGS=('native_identity_admission',
 'native_geometry_inference',
 'scale_admission',
 'units_admission',
 'natural_caller_reachability',
 'hardware_qualification',
 'stock_function_stubs',
 'native_publication')
CONFIGURATION=[{'address': 37832, 'field': 'factor', 'size': 2},
 {'address': 451816, 'field': 'scale', 'size': 2},
 {'address': 452080, 'field': 'cap', 'size': 4},
 {'address': 37030, 'field': 'fall_rate', 'size': 2},
 {'address': 37032, 'field': 'rise_rate', 'size': 2}]
ADAPTER_SHA256='c2beae27fa54286da65cbb191c0c212b710924ea514885cd72de1b10353422fe'
FUNCTIONS=ENTRIES
SPANS=tuple((row['start'],row['end']) for row in UNIT['code'])


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','entries','observer',
            'context_bytes','frame_bytes','frame_prefix','unit','controlled_calibration','configuration','adapter',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-scalar-ram-word'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or not test_contract.exact((value['entries'],value['observer'],value['context_bytes'],value['frame_bytes'],
                value['frame_prefix']),(list(ENTRIES),OBSERVER,80,192,160))
            or any(value[name] is not False for name in FLAGS)
            or not test_contract.exact(value['unit'],UNIT)
            or not test_contract.exact(value['controlled_calibration'],CONTROLLED_CALIBRATION)
            or not test_contract.exact(value['configuration'],CONFIGURATION)
            or hashlib.sha256(json.dumps(value['adapter'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=ADAPTER_SHA256):
        raise ValueError('the scalar RAM word paths change an exact natural entry, code/pool byte, alias or complete observer premise')
    return dict(value,entry=[dict(start=first,end=last) for first,last in SPANS])


def require_image(declared,image):
    if (type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256
            or not test_contract.exact(declared['unit'],UNIT)):
        raise ValueError('the scalar RAM word paths change the complete owned stock image or exact unit')
    for row in UNIT['pools']:
        if image[row['address']:row['address']+row['size']].hex()!=row['stock_hex']:
            raise ValueError('the scalar RAM word paths change a pinned exact stock pool or configuration byte')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for row in UNIT['aliases']:
        at=row['address']
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('the scalar RAM word paths relocate a different original native pointer')
        fixture[at:at+4]=row['alias'].to_bytes(4,'big');aliases.append(dict(row))
    return bytes(fixture),aliases


def fixture_for_case(declared,image,case):
    from kb import scalar_ram_word_matrix as matrix
    matrix.require_case(case);fixture,aliases=independent_fixture(declared,image);fixture=bytearray(fixture)
    for row in CONFIGURATION:
        at,size=row['address'],row['size'];fixture[at:at+size]=case[row['field']].to_bytes(size,'big')
    return bytes(fixture),aliases
