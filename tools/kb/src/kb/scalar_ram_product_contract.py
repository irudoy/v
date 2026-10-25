"""Exact natural scalar RAM products, literal inputs and declared pointer aliases."""

import hashlib
import json
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.scalar-ram-products.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
ENTRIES=(337820, 338178, 345164, 676484)
UNIT={'assembly': 'tools/sh-elf-run/stock_jk08a_scalar_ram_products.s',
 'code': [{'start': 337820, 'end': 337928},
          {'start': 338178, 'end': 338270},
          {'start': 345164, 'end': 345266},
          {'start': 676484, 'end': 676580}],
 'pools': [{'address': 35648, 'size': 1, 'stock_hex': '00'},
           {'address': 35774, 'size': 1, 'stock_hex': '59'},
           {'address': 338166, 'size': 2, 'stock_hex': '03c4'},
           {'address': 338168, 'size': 2, 'stock_hex': '0352'},
           {'address': 338170, 'size': 2, 'stock_hex': '7fff'},
           {'address': 338172, 'size': 2, 'stock_hex': '07da'},
           {'address': 338270, 'size': 2, 'stock_hex': '027e'},
           {'address': 338272, 'size': 2, 'stock_hex': '07da'},
           {'address': 338274, 'size': 2, 'stock_hex': '7fff'},
           {'address': 338276, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 338280, 'size': 4, 'stock_hex': 'ffff4184'},
           {'address': 338300, 'size': 4, 'stock_hex': 'ffff245c'},
           {'address': 338316, 'size': 4, 'stock_hex': '00008b40'},
           {'address': 338320, 'size': 4, 'stock_hex': 'ffff22f8'},
           {'address': 345298, 'size': 2, 'stock_hex': '06c8'},
           {'address': 345300, 'size': 2, 'stock_hex': '06c9'},
           {'address': 345302, 'size': 2, 'stock_hex': '0ac6'},
           {'address': 345520, 'size': 4, 'stock_hex': 'ffff28f8'},
           {'address': 345548, 'size': 4, 'stock_hex': 'ffff1024'},
           {'address': 345556, 'size': 4, 'stock_hex': '00008bbe'},
           {'address': 345560, 'size': 4, 'stock_hex': 'ffff4124'},
           {'address': 676754, 'size': 2, 'stock_hex': '0a92'},
           {'address': 676756, 'size': 2, 'stock_hex': '06fa'},
           {'address': 677072, 'size': 4, 'stock_hex': 'ffff28f8'}],
 'aliases': [{'address': 338276, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 338280, 'width': 4, 'original': 4294918532, 'alias': 16793988},
             {'address': 338300, 'width': 4, 'original': 4294911068, 'alias': 16786524},
             {'address': 338320, 'width': 4, 'original': 4294910712, 'alias': 16786168},
             {'address': 345520, 'width': 4, 'original': 4294912248, 'alias': 16787704},
             {'address': 345548, 'width': 4, 'original': 4294905892, 'alias': 16781348},
             {'address': 345560, 'width': 4, 'original': 4294918436, 'alias': 16793892},
             {'address': 677072, 'width': 4, 'original': 4294912248, 'alias': 16787704}]}
CONTROLLED_CALIBRATION=[{'address': 35648, 'size': 1},
 {'address': 35774, 'size': 1},
 {'address': 338166, 'size': 2},
 {'address': 338168, 'size': 2},
 {'address': 338170, 'size': 2},
 {'address': 338172, 'size': 2},
 {'address': 338270, 'size': 2},
 {'address': 338272, 'size': 2},
 {'address': 338274, 'size': 2},
 {'address': 338276, 'size': 4},
 {'address': 338280, 'size': 4},
 {'address': 338300, 'size': 4},
 {'address': 338316, 'size': 4},
 {'address': 338320, 'size': 4},
 {'address': 345298, 'size': 2},
 {'address': 345300, 'size': 2},
 {'address': 345302, 'size': 2},
 {'address': 345520, 'size': 4},
 {'address': 345548, 'size': 4},
 {'address': 345556, 'size': 4},
 {'address': 345560, 'size': 4},
 {'address': 676754, 'size': 2},
 {'address': 676756, 'size': 2},
 {'address': 677072, 'size': 4}]
BOUND_SPANS=({'address': 337820, 'size': 108},
 {'address': 338178, 'size': 92},
 {'address': 345164, 'size': 102},
 {'address': 676484, 'size': 96},
 {'address': 35648, 'size': 1},
 {'address': 35774, 'size': 1},
 {'address': 338166, 'size': 2},
 {'address': 338168, 'size': 2},
 {'address': 338170, 'size': 2},
 {'address': 338172, 'size': 2},
 {'address': 338270, 'size': 2},
 {'address': 338272, 'size': 2},
 {'address': 338274, 'size': 2},
 {'address': 338276, 'size': 4},
 {'address': 338280, 'size': 4},
 {'address': 338300, 'size': 4},
 {'address': 338316, 'size': 4},
 {'address': 338320, 'size': 4},
 {'address': 345298, 'size': 2},
 {'address': 345300, 'size': 2},
 {'address': 345302, 'size': 2},
 {'address': 345520, 'size': 4},
 {'address': 345548, 'size': 4},
 {'address': 345556, 'size': 4},
 {'address': 345560, 'size': 4},
 {'address': 676754, 'size': 2},
 {'address': 676756, 'size': 2},
 {'address': 677072, 'size': 4})
FLAGS=('native_identity_admission',
 'native_geometry_inference',
 'scale_admission',
 'units_admission',
 'natural_caller_reachability',
 'hardware_qualification',
 'stock_function_stubs',
 'native_publication')
CONFIGURATION=[{'address': 35774, 'field': 'product_factor'}, {'address': 35648, 'field': 'bypass_configuration'}]
ADAPTER_SHA256='e18e804067db38ba3790fcd219eba9d66718214d4594216f8dd8588cc9bc3047'
FUNCTIONS=ENTRIES
SPANS=tuple((row['start'],row['end']) for row in UNIT['code'])


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','entries','observer',
            'context_bytes','frame_bytes','frame_prefix','unit','controlled_calibration','configuration','adapter',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-scalar-ram-products'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or not test_contract.exact((value['entries'],value['observer'],value['context_bytes'],value['frame_bytes'],
                value['frame_prefix']),(list(ENTRIES),OBSERVER,80,192,160))
            or any(value[name] is not False for name in FLAGS)
            or not test_contract.exact(value['unit'],UNIT)
            or not test_contract.exact(value['controlled_calibration'],CONTROLLED_CALIBRATION)
            or not test_contract.exact(value['configuration'],CONFIGURATION)
            or hashlib.sha256(json.dumps(value['adapter'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=ADAPTER_SHA256):
        raise ValueError('the scalar RAM products change an exact natural entry, code/pool byte, alias or complete observer premise')
    return dict(value,entry=[dict(start=first,end=last) for first,last in SPANS])


def require_image(declared,image):
    if (type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256
            or not test_contract.exact(declared['unit'],UNIT)):
        raise ValueError('the scalar RAM products change the complete owned stock image or exact unit')
    for row in UNIT['pools']:
        if image[row['address']:row['address']+row['size']].hex()!=row['stock_hex']:
            raise ValueError('the scalar RAM products change a pinned exact stock pool or configuration byte')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for row in UNIT['aliases']:
        at=row['address']
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('the scalar RAM products relocate a different original native pointer')
        fixture[at:at+4]=row['alias'].to_bytes(4,'big');aliases.append(dict(row))
    return bytes(fixture),aliases


def fixture_for_case(declared,image,case):
    from kb import scalar_ram_product_matrix as matrix
    matrix.require_case(case);fixture,aliases=independent_fixture(declared,image);fixture=bytearray(fixture)
    for row in CONFIGURATION:fixture[row['address']]=case[row['field']]
    return bytes(fixture),aliases
