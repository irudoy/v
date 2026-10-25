"""Exact natural scalar RAM gated paths, literal inputs and declared pointer aliases."""

import hashlib
import json
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.scalar-ram-gated.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
ENTRIES=(250972, 279624, 478216, 489466, 591848)
UNIT={'assembly': 'tools/sh-elf-run/stock_jk08a_scalar_ram_gated.s',
 'code': [{'start': 250972, 'end': 251048},
          {'start': 279624, 'end': 279738},
          {'start': 478216, 'end': 478280},
          {'start': 478292, 'end': 478338},
          {'start': 489466, 'end': 489594},
          {'start': 591848, 'end': 592004}],
 'pools': [{'address': 33729, 'size': 1, 'stock_hex': '2c'},
           {'address': 35269, 'size': 1, 'stock_hex': '19'},
           {'address': 36081, 'size': 1, 'stock_hex': '01'},
           {'address': 36082, 'size': 1, 'stock_hex': '00'},
           {'address': 36378, 'size': 1, 'stock_hex': '00'},
           {'address': 251120, 'size': 2, 'stock_hex': '057a'},
           {'address': 251122, 'size': 2, 'stock_hex': '0588'},
           {'address': 251128, 'size': 4, 'stock_hex': 'ffff39c4'},
           {'address': 251136, 'size': 4, 'stock_hex': 'ffff277e'},
           {'address': 251172, 'size': 4, 'stock_hex': 'ffff417f'},
           {'address': 279738, 'size': 2, 'stock_hex': '06cc'},
           {'address': 279740, 'size': 2, 'stock_hex': '05b0'},
           {'address': 279744, 'size': 4, 'stock_hex': 'ffff24ce'},
           {'address': 279748, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 279752, 'size': 4, 'stock_hex': 'ffff1068'},
           {'address': 279756, 'size': 4, 'stock_hex': '00008cf1'},
           {'address': 478286, 'size': 2, 'stock_hex': '065c'},
           {'address': 478290, 'size': 2, 'stock_hex': '065a'},
           {'address': 478492, 'size': 2, 'stock_hex': '065c'},
           {'address': 478494, 'size': 2, 'stock_hex': '065a'},
           {'address': 478496, 'size': 2, 'stock_hex': '0668'},
           {'address': 478500, 'size': 4, 'stock_hex': 'ffff23bc'},
           {'address': 478504, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 478520, 'size': 4, 'stock_hex': 'ffff417e'},
           {'address': 478536, 'size': 4, 'stock_hex': 'ffff2470'},
           {'address': 478540, 'size': 4, 'stock_hex': 'ffff245c'},
           {'address': 489596, 'size': 2, 'stock_hex': '0b90'},
           {'address': 489598, 'size': 2, 'stock_hex': '0b94'},
           {'address': 489600, 'size': 2, 'stock_hex': '0b8e'},
           {'address': 489602, 'size': 2, 'stock_hex': '0b92'},
           {'address': 489604, 'size': 2, 'stock_hex': '0ba8'},
           {'address': 489606, 'size': 2, 'stock_hex': '0bd0'},
           {'address': 489608, 'size': 2, 'stock_hex': '0ba4'},
           {'address': 489610, 'size': 2, 'stock_hex': '0b88'},
           {'address': 489612, 'size': 2, 'stock_hex': '0b8c'},
           {'address': 489614, 'size': 2, 'stock_hex': '0b86'},
           {'address': 489616, 'size': 2, 'stock_hex': '0b8a'},
           {'address': 489744, 'size': 4, 'stock_hex': 'ffff28f8'},
           {'address': 489748, 'size': 4, 'stock_hex': '000083c1'},
           {'address': 489752, 'size': 4, 'stock_hex': '000089c5'},
           {'address': 489756, 'size': 4, 'stock_hex': 'ffff41a5'},
           {'address': 489760, 'size': 4, 'stock_hex': 'ffff4124'},
           {'address': 592170, 'size': 2, 'stock_hex': '0820'},
           {'address': 592172, 'size': 2, 'stock_hex': '022c'},
           {'address': 592174, 'size': 2, 'stock_hex': '06a4'},
           {'address': 592176, 'size': 2, 'stock_hex': '0264'},
           {'address': 592476, 'size': 4, 'stock_hex': 'ffff2324'},
           {'address': 592480, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 592484, 'size': 4, 'stock_hex': 'ffff24f9'},
           {'address': 592488, 'size': 4, 'stock_hex': '00008e1a'}],
 'aliases': [{'address': 251128, 'width': 4, 'original': 4294916548, 'alias': 16792004},
             {'address': 251136, 'width': 4, 'original': 4294911870, 'alias': 16787326},
             {'address': 251172, 'width': 4, 'original': 4294918527, 'alias': 16793983},
             {'address': 279744, 'width': 4, 'original': 4294911182, 'alias': 16786638},
             {'address': 279748, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 279752, 'width': 4, 'original': 4294905960, 'alias': 16781416},
             {'address': 478500, 'width': 4, 'original': 4294910908, 'alias': 16786364},
             {'address': 478504, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 478520, 'width': 4, 'original': 4294918526, 'alias': 16793982},
             {'address': 478536, 'width': 4, 'original': 4294911088, 'alias': 16786544},
             {'address': 478540, 'width': 4, 'original': 4294911068, 'alias': 16786524},
             {'address': 489744, 'width': 4, 'original': 4294912248, 'alias': 16787704},
             {'address': 489756, 'width': 4, 'original': 4294918565, 'alias': 16794021},
             {'address': 489760, 'width': 4, 'original': 4294918436, 'alias': 16793892},
             {'address': 592476, 'width': 4, 'original': 4294910756, 'alias': 16786212},
             {'address': 592480, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 592484, 'width': 4, 'original': 4294911225, 'alias': 16786681}]}
CONTROLLED_CALIBRATION=[{'address': 33729, 'size': 1},
 {'address': 35269, 'size': 1},
 {'address': 36081, 'size': 1},
 {'address': 36082, 'size': 1},
 {'address': 36378, 'size': 1},
 {'address': 251120, 'size': 2},
 {'address': 251122, 'size': 2},
 {'address': 251128, 'size': 4},
 {'address': 251136, 'size': 4},
 {'address': 251172, 'size': 4},
 {'address': 279738, 'size': 2},
 {'address': 279740, 'size': 2},
 {'address': 279744, 'size': 4},
 {'address': 279748, 'size': 4},
 {'address': 279752, 'size': 4},
 {'address': 279756, 'size': 4},
 {'address': 478286, 'size': 2},
 {'address': 478290, 'size': 2},
 {'address': 478492, 'size': 2},
 {'address': 478494, 'size': 2},
 {'address': 478496, 'size': 2},
 {'address': 478500, 'size': 4},
 {'address': 478504, 'size': 4},
 {'address': 478520, 'size': 4},
 {'address': 478536, 'size': 4},
 {'address': 478540, 'size': 4},
 {'address': 489596, 'size': 2},
 {'address': 489598, 'size': 2},
 {'address': 489600, 'size': 2},
 {'address': 489602, 'size': 2},
 {'address': 489604, 'size': 2},
 {'address': 489606, 'size': 2},
 {'address': 489608, 'size': 2},
 {'address': 489610, 'size': 2},
 {'address': 489612, 'size': 2},
 {'address': 489614, 'size': 2},
 {'address': 489616, 'size': 2},
 {'address': 489744, 'size': 4},
 {'address': 489748, 'size': 4},
 {'address': 489752, 'size': 4},
 {'address': 489756, 'size': 4},
 {'address': 489760, 'size': 4},
 {'address': 592170, 'size': 2},
 {'address': 592172, 'size': 2},
 {'address': 592174, 'size': 2},
 {'address': 592176, 'size': 2},
 {'address': 592476, 'size': 4},
 {'address': 592480, 'size': 4},
 {'address': 592484, 'size': 4},
 {'address': 592488, 'size': 4}]
BOUND_SPANS=({'address': 250972, 'size': 76},
 {'address': 279624, 'size': 114},
 {'address': 478216, 'size': 64},
 {'address': 478292, 'size': 46},
 {'address': 489466, 'size': 128},
 {'address': 591848, 'size': 156},
 {'address': 33729, 'size': 1},
 {'address': 35269, 'size': 1},
 {'address': 36081, 'size': 1},
 {'address': 36082, 'size': 1},
 {'address': 36378, 'size': 1},
 {'address': 251120, 'size': 2},
 {'address': 251122, 'size': 2},
 {'address': 251128, 'size': 4},
 {'address': 251136, 'size': 4},
 {'address': 251172, 'size': 4},
 {'address': 279738, 'size': 2},
 {'address': 279740, 'size': 2},
 {'address': 279744, 'size': 4},
 {'address': 279748, 'size': 4},
 {'address': 279752, 'size': 4},
 {'address': 279756, 'size': 4},
 {'address': 478286, 'size': 2},
 {'address': 478290, 'size': 2},
 {'address': 478492, 'size': 2},
 {'address': 478494, 'size': 2},
 {'address': 478496, 'size': 2},
 {'address': 478500, 'size': 4},
 {'address': 478504, 'size': 4},
 {'address': 478520, 'size': 4},
 {'address': 478536, 'size': 4},
 {'address': 478540, 'size': 4},
 {'address': 489596, 'size': 2},
 {'address': 489598, 'size': 2},
 {'address': 489600, 'size': 2},
 {'address': 489602, 'size': 2},
 {'address': 489604, 'size': 2},
 {'address': 489606, 'size': 2},
 {'address': 489608, 'size': 2},
 {'address': 489610, 'size': 2},
 {'address': 489612, 'size': 2},
 {'address': 489614, 'size': 2},
 {'address': 489616, 'size': 2},
 {'address': 489744, 'size': 4},
 {'address': 489748, 'size': 4},
 {'address': 489752, 'size': 4},
 {'address': 489756, 'size': 4},
 {'address': 489760, 'size': 4},
 {'address': 592170, 'size': 2},
 {'address': 592172, 'size': 2},
 {'address': 592174, 'size': 2},
 {'address': 592176, 'size': 2},
 {'address': 592476, 'size': 4},
 {'address': 592480, 'size': 4},
 {'address': 592484, 'size': 4},
 {'address': 592488, 'size': 4})
FLAGS=('native_identity_admission',
 'native_geometry_inference',
 'scale_admission',
 'units_admission',
 'natural_caller_reachability',
 'hardware_qualification',
 'stock_function_stubs',
 'native_publication')
CONFIGURATION=[{'address': 36081, 'field': 'status_threshold_low'},
 {'address': 36082, 'field': 'status_threshold_high'},
 {'address': 33729, 'field': 'bound_configuration'},
 {'address': 35269, 'field': 'bound_external_configuration'},
 {'address': 36378, 'field': 'reset_configuration'}]
ADAPTER_SHA256='09754842cb8443fd34df7bb6f4d102d3a40b92b34f1a1787268e8964f127e0d0'
FUNCTIONS=ENTRIES
SPANS=tuple((row['start'],row['end']) for row in UNIT['code'])


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','entries','observer',
            'context_bytes','frame_bytes','frame_prefix','unit','controlled_calibration','configuration','adapter',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-scalar-ram-gated'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or not test_contract.exact((value['entries'],value['observer'],value['context_bytes'],value['frame_bytes'],
                value['frame_prefix']),(list(ENTRIES),OBSERVER,80,192,160))
            or any(value[name] is not False for name in FLAGS)
            or not test_contract.exact(value['unit'],UNIT)
            or not test_contract.exact(value['controlled_calibration'],CONTROLLED_CALIBRATION)
            or not test_contract.exact(value['configuration'],CONFIGURATION)
            or hashlib.sha256(json.dumps(value['adapter'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=ADAPTER_SHA256):
        raise ValueError('the scalar RAM gated paths change an exact natural entry, code/pool byte, alias or complete observer premise')
    return dict(value,entry=[dict(start=first,end=last) for first,last in SPANS])


def require_image(declared,image):
    if (type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256
            or not test_contract.exact(declared['unit'],UNIT)):
        raise ValueError('the scalar RAM gated paths change the complete owned stock image or exact unit')
    for row in UNIT['pools']:
        if image[row['address']:row['address']+row['size']].hex()!=row['stock_hex']:
            raise ValueError('the scalar RAM gated paths change a pinned exact stock pool or configuration byte')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for row in UNIT['aliases']:
        at=row['address']
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('the scalar RAM gated paths relocate a different original native pointer')
        fixture[at:at+4]=row['alias'].to_bytes(4,'big');aliases.append(dict(row))
    return bytes(fixture),aliases


def fixture_for_case(declared,image,case):
    from kb import scalar_ram_gated_matrix as matrix
    matrix.require_case(case);fixture,aliases=independent_fixture(declared,image);fixture=bytearray(fixture)
    for row in CONFIGURATION:fixture[row['address']]=case[row['field']]
    return bytes(fixture),aliases
