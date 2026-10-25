"""Exact natural RPM state withdrawal paths, literal inputs and declared pointer aliases."""

import hashlib
import json
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.rpm-state-withdrawal-paths.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
ENTRIES=(325600, 326084)
UNIT={'assembly': 'tools/sh-elf-run/stock_jk08a_rpm_state_withdrawal.s',
 'code': [{'start': 325600, 'end': 325844},
          {'start': 325846, 'end': 325894},
          {'start': 326084, 'end': 326300}],
 'pools': [{'address': 33751, 'size': 1, 'stock_hex': '37'},
           {'address': 34007, 'size': 1, 'stock_hex': '04'},
           {'address': 34011, 'size': 1, 'stock_hex': '74'},
           {'address': 34012, 'size': 1, 'stock_hex': '5c'},
           {'address': 34014, 'size': 1, 'stock_hex': '0c'},
           {'address': 34983, 'size': 1, 'stock_hex': '3c'},
           {'address': 34984, 'size': 1, 'stock_hex': '55'},
           {'address': 34985, 'size': 1, 'stock_hex': '6c'},
           {'address': 34986, 'size': 1, 'stock_hex': '04'},
           {'address': 34989, 'size': 1, 'stock_hex': '96'},
           {'address': 34990, 'size': 1, 'stock_hex': '58'},
           {'address': 35647, 'size': 1, 'stock_hex': '18'},
           {'address': 37088, 'size': 2, 'stock_hex': '07d0'},
           {'address': 325844, 'size': 2, 'stock_hex': '06a6'},
           {'address': 325894, 'size': 2, 'stock_hex': '06a6'},
           {'address': 325908, 'size': 4, 'stock_hex': 'ffff119c'},
           {'address': 325912, 'size': 4, 'stock_hex': 'ffff41a9'},
           {'address': 325916, 'size': 4, 'stock_hex': '00008b3f'},
           {'address': 325932, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 325940, 'size': 4, 'stock_hex': 'ffff1094'},
           {'address': 325952, 'size': 4, 'stock_hex': '000090e0'},
           {'address': 325956, 'size': 4, 'stock_hex': '000084d7'},
           {'address': 325960, 'size': 4, 'stock_hex': 'ffff244c'},
           {'address': 325964, 'size': 4, 'stock_hex': 'ffff424c'},
           {'address': 325968, 'size': 4, 'stock_hex': '000083d7'},
           {'address': 325972, 'size': 4, 'stock_hex': 'ffff24ce'},
           {'address': 326302, 'size': 2, 'stock_hex': '0404'},
           {'address': 326516, 'size': 4, 'stock_hex': '00008b3f'},
           {'address': 326528, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 326532, 'size': 4, 'stock_hex': 'ffff119c'},
           {'address': 326536, 'size': 4, 'stock_hex': 'ffff244c'},
           {'address': 326540, 'size': 4, 'stock_hex': '000088a7'},
           {'address': 326544, 'size': 4, 'stock_hex': 'ffff41a9'},
           {'address': 326548, 'size': 4, 'stock_hex': 'ffff1068'},
           {'address': 326552, 'size': 4, 'stock_hex': 'ffff1094'}],
 'aliases': [{'address': 325908, 'width': 4, 'original': 4294906268, 'alias': 16781724},
             {'address': 325912, 'width': 4, 'original': 4294918569, 'alias': 16794025},
             {'address': 325932, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 325940, 'width': 4, 'original': 4294906004, 'alias': 16781460},
             {'address': 325960, 'width': 4, 'original': 4294911052, 'alias': 16786508},
             {'address': 325964, 'width': 4, 'original': 4294918732, 'alias': 16794188},
             {'address': 325972, 'width': 4, 'original': 4294911182, 'alias': 16786638},
             {'address': 326528, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 326532, 'width': 4, 'original': 4294906268, 'alias': 16781724},
             {'address': 326536, 'width': 4, 'original': 4294911052, 'alias': 16786508},
             {'address': 326544, 'width': 4, 'original': 4294918569, 'alias': 16794025},
             {'address': 326548, 'width': 4, 'original': 4294905960, 'alias': 16781416},
             {'address': 326552, 'width': 4, 'original': 4294906004, 'alias': 16781460}]}
CONTROLLED_CALIBRATION=[{'address': 33751, 'size': 1},
 {'address': 34007, 'size': 1},
 {'address': 34011, 'size': 1},
 {'address': 34012, 'size': 1},
 {'address': 34014, 'size': 1},
 {'address': 34983, 'size': 1},
 {'address': 34984, 'size': 1},
 {'address': 34985, 'size': 1},
 {'address': 34986, 'size': 1},
 {'address': 34989, 'size': 1},
 {'address': 34990, 'size': 1},
 {'address': 35647, 'size': 1},
 {'address': 37088, 'size': 2},
 {'address': 325844, 'size': 2},
 {'address': 325894, 'size': 2},
 {'address': 325908, 'size': 4},
 {'address': 325912, 'size': 4},
 {'address': 325916, 'size': 4},
 {'address': 325932, 'size': 4},
 {'address': 325940, 'size': 4},
 {'address': 325952, 'size': 4},
 {'address': 325956, 'size': 4},
 {'address': 325960, 'size': 4},
 {'address': 325964, 'size': 4},
 {'address': 325968, 'size': 4},
 {'address': 325972, 'size': 4},
 {'address': 326302, 'size': 2},
 {'address': 326516, 'size': 4},
 {'address': 326528, 'size': 4},
 {'address': 326532, 'size': 4},
 {'address': 326536, 'size': 4},
 {'address': 326540, 'size': 4},
 {'address': 326544, 'size': 4},
 {'address': 326548, 'size': 4},
 {'address': 326552, 'size': 4}]
BOUND_SPANS=({'address': 325600, 'size': 244},
 {'address': 325846, 'size': 48},
 {'address': 326084, 'size': 216},
 {'address': 33751, 'size': 1},
 {'address': 34007, 'size': 1},
 {'address': 34011, 'size': 1},
 {'address': 34012, 'size': 1},
 {'address': 34014, 'size': 1},
 {'address': 34983, 'size': 1},
 {'address': 34984, 'size': 1},
 {'address': 34985, 'size': 1},
 {'address': 34986, 'size': 1},
 {'address': 34989, 'size': 1},
 {'address': 34990, 'size': 1},
 {'address': 35647, 'size': 1},
 {'address': 37088, 'size': 2},
 {'address': 325844, 'size': 2},
 {'address': 325894, 'size': 2},
 {'address': 325908, 'size': 4},
 {'address': 325912, 'size': 4},
 {'address': 325916, 'size': 4},
 {'address': 325932, 'size': 4},
 {'address': 325940, 'size': 4},
 {'address': 325952, 'size': 4},
 {'address': 325956, 'size': 4},
 {'address': 325960, 'size': 4},
 {'address': 325964, 'size': 4},
 {'address': 325968, 'size': 4},
 {'address': 325972, 'size': 4},
 {'address': 326302, 'size': 2},
 {'address': 326516, 'size': 4},
 {'address': 326528, 'size': 4},
 {'address': 326532, 'size': 4},
 {'address': 326536, 'size': 4},
 {'address': 326540, 'size': 4},
 {'address': 326544, 'size': 4},
 {'address': 326548, 'size': 4},
 {'address': 326552, 'size': 4})
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
 {'address': 34007, 'field': 'boundary_threshold', 'size': 1},
 {'address': 34011, 'field': 'upper_rpm', 'size': 1},
 {'address': 34012, 'field': 'lower_rpm', 'size': 1},
 {'address': 34014, 'field': 'exposure_step', 'size': 1},
 {'address': 33751, 'field': 'gate_configuration', 'size': 1},
 {'address': 34990, 'field': 'restore_rpm', 'size': 1},
 {'address': 34989, 'field': 'restore_count', 'size': 1},
 {'address': 34985, 'field': 'entry_rpm', 'size': 1},
 {'address': 34984, 'field': 'warm_threshold', 'size': 1},
 {'address': 34986, 'field': 'entry_boundary', 'size': 1},
 {'address': 34983, 'field': 'entry_count', 'size': 1}]
ADAPTER_SHA256='be1fe1b8b4886d84f9a9d20939b0e453fdcafe55b766adfdcd106af95720647f'
FUNCTIONS=ENTRIES
SPANS=tuple((row['start'],row['end']) for row in UNIT['code'])


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','entries','observer',
            'context_bytes','frame_bytes','frame_prefix','unit','controlled_calibration','configuration','adapter',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-rpm-state-withdrawal'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or not test_contract.exact((value['entries'],value['observer'],value['context_bytes'],value['frame_bytes'],
                value['frame_prefix']),(list(ENTRIES),OBSERVER,80,192,160))
            or any(value[name] is not False for name in FLAGS)
            or not test_contract.exact(value['unit'],UNIT)
            or not test_contract.exact(value['controlled_calibration'],CONTROLLED_CALIBRATION)
            or not test_contract.exact(value['configuration'],CONFIGURATION)
            or hashlib.sha256(json.dumps(value['adapter'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=ADAPTER_SHA256):
        raise ValueError('the RPM state withdrawal paths change an exact natural entry, code/pool byte, alias or complete observer premise')
    return dict(value,entry=[dict(start=first,end=last) for first,last in SPANS])


def require_image(declared,image):
    if (type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256
            or not test_contract.exact(declared['unit'],UNIT)):
        raise ValueError('the RPM state withdrawal paths change the complete owned stock image or exact unit')
    for row in UNIT['pools']:
        if image[row['address']:row['address']+row['size']].hex()!=row['stock_hex']:
            raise ValueError('the RPM state withdrawal paths change a pinned exact stock pool or configuration byte')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for row in UNIT['aliases']:
        at=row['address']
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('the RPM state withdrawal paths relocate a different original native pointer')
        fixture[at:at+4]=row['alias'].to_bytes(4,'big');aliases.append(dict(row))
    return bytes(fixture),aliases


def fixture_for_case(declared,image,case):
    from kb import rpm_state_withdrawal_matrix as matrix
    matrix.require_case(case);fixture,aliases=independent_fixture(declared,image);fixture=bytearray(fixture)
    for row in CONFIGURATION:
        at,size=row['address'],row['size'];fixture[at:at+size]=case[row['field']].to_bytes(size,'big')
    return bytes(fixture),aliases
