"""Exact natural RPM RAM withdrawal paths, literal inputs and declared pointer aliases."""

import hashlib
import json
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.rpm-ram-withdrawal-paths.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
ENTRIES=(325430, 325976, 328586)
UNIT={'assembly': 'tools/sh-elf-run/stock_jk08a_rpm_ram_withdrawal.s',
 'code': [{'start': 325430, 'end': 325464},
          {'start': 325976, 'end': 326084},
          {'start': 328586, 'end': 328672}],
 'pools': [{'address': 34010, 'size': 1, 'stock_hex': '48'},
           {'address': 34013, 'size': 1, 'stock_hex': '3c'},
           {'address': 34014, 'size': 1, 'stock_hex': '0c'},
           {'address': 34572, 'size': 1, 'stock_hex': '44'},
           {'address': 35392, 'size': 1, 'stock_hex': '04'},
           {'address': 35647, 'size': 1, 'stock_hex': '18'},
           {'address': 35904, 'size': 1, 'stock_hex': '00'},
           {'address': 35905, 'size': 1, 'stock_hex': '00'},
           {'address': 35915, 'size': 1, 'stock_hex': '00'},
           {'address': 35916, 'size': 1, 'stock_hex': '00'},
           {'address': 35917, 'size': 1, 'stock_hex': '00'},
           {'address': 37088, 'size': 2, 'stock_hex': '07d0'},
           {'address': 325904, 'size': 4, 'stock_hex': 'ffff2448'},
           {'address': 325908, 'size': 4, 'stock_hex': 'ffff119c'},
           {'address': 326300, 'size': 2, 'stock_hex': '06a6'},
           {'address': 326512, 'size': 4, 'stock_hex': 'ffff2470'},
           {'address': 326516, 'size': 4, 'stock_hex': '00008b3f'},
           {'address': 326520, 'size': 4, 'stock_hex': '000090e0'},
           {'address': 326524, 'size': 4, 'stock_hex': '000084da'},
           {'address': 326528, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 326532, 'size': 4, 'stock_hex': 'ffff119c'},
           {'address': 328800, 'size': 4, 'stock_hex': '00008c40'},
           {'address': 328804, 'size': 4, 'stock_hex': 'ffff424c'},
           {'address': 328808, 'size': 4, 'stock_hex': 'ffff2458'},
           {'address': 328812, 'size': 4, 'stock_hex': 'ffff106a'},
           {'address': 328816, 'size': 4, 'stock_hex': '00008a40'},
           {'address': 328820, 'size': 4, 'stock_hex': '0000870c'}],
 'aliases': [{'address': 325904, 'width': 4, 'original': 4294911048, 'alias': 16786504},
             {'address': 325908, 'width': 4, 'original': 4294906268, 'alias': 16781724},
             {'address': 326512, 'width': 4, 'original': 4294911088, 'alias': 16786544},
             {'address': 326528, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 326532, 'width': 4, 'original': 4294906268, 'alias': 16781724},
             {'address': 328804, 'width': 4, 'original': 4294918732, 'alias': 16794188},
             {'address': 328808, 'width': 4, 'original': 4294911064, 'alias': 16786520},
             {'address': 328812, 'width': 4, 'original': 4294905962, 'alias': 16781418}]}
CONTROLLED_CALIBRATION=[{'address': 34010, 'size': 1},
 {'address': 34013, 'size': 1},
 {'address': 34014, 'size': 1},
 {'address': 34572, 'size': 1},
 {'address': 35392, 'size': 1},
 {'address': 35647, 'size': 1},
 {'address': 35904, 'size': 1},
 {'address': 35905, 'size': 1},
 {'address': 35915, 'size': 1},
 {'address': 35916, 'size': 1},
 {'address': 35917, 'size': 1},
 {'address': 37088, 'size': 2},
 {'address': 325904, 'size': 4},
 {'address': 325908, 'size': 4},
 {'address': 326300, 'size': 2},
 {'address': 326512, 'size': 4},
 {'address': 326516, 'size': 4},
 {'address': 326520, 'size': 4},
 {'address': 326524, 'size': 4},
 {'address': 326528, 'size': 4},
 {'address': 326532, 'size': 4},
 {'address': 328800, 'size': 4},
 {'address': 328804, 'size': 4},
 {'address': 328808, 'size': 4},
 {'address': 328812, 'size': 4},
 {'address': 328816, 'size': 4},
 {'address': 328820, 'size': 4}]
BOUND_SPANS=({'address': 325430, 'size': 34},
 {'address': 325976, 'size': 108},
 {'address': 328586, 'size': 86},
 {'address': 34010, 'size': 1},
 {'address': 34013, 'size': 1},
 {'address': 34014, 'size': 1},
 {'address': 34572, 'size': 1},
 {'address': 35392, 'size': 1},
 {'address': 35647, 'size': 1},
 {'address': 35904, 'size': 1},
 {'address': 35905, 'size': 1},
 {'address': 35915, 'size': 1},
 {'address': 35916, 'size': 1},
 {'address': 35917, 'size': 1},
 {'address': 37088, 'size': 2},
 {'address': 325904, 'size': 4},
 {'address': 325908, 'size': 4},
 {'address': 326300, 'size': 2},
 {'address': 326512, 'size': 4},
 {'address': 326516, 'size': 4},
 {'address': 326520, 'size': 4},
 {'address': 326524, 'size': 4},
 {'address': 326528, 'size': 4},
 {'address': 326532, 'size': 4},
 {'address': 328800, 'size': 4},
 {'address': 328804, 'size': 4},
 {'address': 328808, 'size': 4},
 {'address': 328812, 'size': 4},
 {'address': 328816, 'size': 4},
 {'address': 328820, 'size': 4})
FLAGS=('native_identity_admission',
 'native_geometry_inference',
 'scale_admission',
 'units_admission',
 'natural_caller_reachability',
 'hardware_qualification',
 'stock_function_stubs',
 'native_publication')
CONFIGURATION=[{'address': 35647, 'field': 'disable_mask', 'size': 1},
 {'address': 37088, 'field': 'exposure_base', 'size': 2},
 {'address': 34010, 'field': 'sustained_cut', 'size': 1},
 {'address': 34013, 'field': 'sustained_restore', 'size': 1},
 {'address': 34014, 'field': 'exposure_factor', 'size': 1},
 {'address': 35392, 'field': 'delay_threshold', 'size': 1},
 {'address': 34572, 'field': 'delay_configuration', 'size': 1},
 {'address': 35904, 'field': 'delay_00', 'size': 1},
 {'address': 35905, 'field': 'delay_01', 'size': 1},
 {'address': 35915, 'field': 'delay_11', 'size': 1},
 {'address': 35916, 'field': 'delay_12', 'size': 1},
 {'address': 35917, 'field': 'delay_13', 'size': 1}]
ADAPTER_SHA256='6bd70794e51fc7344121c0390c574a19893b4a70e3e2bd817c5e1c37636371bd'
FUNCTIONS=ENTRIES
SPANS=tuple((row['start'],row['end']) for row in UNIT['code'])


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','entries','observer',
            'context_bytes','frame_bytes','frame_prefix','unit','controlled_calibration','configuration','adapter',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-rpm-ram-withdrawal'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or not test_contract.exact((value['entries'],value['observer'],value['context_bytes'],value['frame_bytes'],
                value['frame_prefix']),(list(ENTRIES),OBSERVER,80,192,160))
            or any(value[name] is not False for name in FLAGS)
            or not test_contract.exact(value['unit'],UNIT)
            or not test_contract.exact(value['controlled_calibration'],CONTROLLED_CALIBRATION)
            or not test_contract.exact(value['configuration'],CONFIGURATION)
            or hashlib.sha256(json.dumps(value['adapter'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=ADAPTER_SHA256):
        raise ValueError('the RPM RAM withdrawal paths change an exact natural entry, code/pool byte, alias or complete observer premise')
    return dict(value,entry=[dict(start=first,end=last) for first,last in SPANS])


def require_image(declared,image):
    if (type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256
            or not test_contract.exact(declared['unit'],UNIT)):
        raise ValueError('the RPM RAM withdrawal paths change the complete owned stock image or exact unit')
    for row in UNIT['pools']:
        if image[row['address']:row['address']+row['size']].hex()!=row['stock_hex']:
            raise ValueError('the RPM RAM withdrawal paths change a pinned exact stock pool or configuration byte')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for row in UNIT['aliases']:
        at=row['address']
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('the RPM RAM withdrawal paths relocate a different original native pointer')
        fixture[at:at+4]=row['alias'].to_bytes(4,'big');aliases.append(dict(row))
    return bytes(fixture),aliases


def fixture_for_case(declared,image,case):
    from kb import rpm_ram_withdrawal_matrix as matrix
    matrix.require_case(case);fixture,aliases=independent_fixture(declared,image);fixture=bytearray(fixture)
    for row in CONFIGURATION:
        at,size=row['address'],row['size'];fixture[at:at+size]=case[row['field']].to_bytes(size,'big')
    return bytes(fixture),aliases
