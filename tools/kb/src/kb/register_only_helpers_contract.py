"""Complete natural register-only helper bytes and observation boundary."""

import hashlib
import json
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.register-only-helpers.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
ENTRIES=(140536, 140538, 140572, 154064, 157504, 330316)
FUNCTIONS=ENTRIES
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
UNIT={'assembly': 'tools/sh-elf-run/stock_jk08a_register_only_helpers.s',
 'code': [{'start': 140536, 'end': 140538},
          {'start': 140538, 'end': 140552},
          {'start': 140572, 'end': 140592},
          {'start': 154064, 'end': 154084},
          {'start': 157504, 'end': 157550},
          {'start': 330316, 'end': 330326}],
 'pools': [],
 'aliases': []}
OBSERVED_SPANS=[{'address': 140536, 'size': 16}]
BOUND_SPANS=({'address': 140536, 'size': 2},
 {'address': 140538, 'size': 14},
 {'address': 140572, 'size': 20},
 {'address': 154064, 'size': 20},
 {'address': 157504, 'size': 46},
 {'address': 330316, 'size': 10})
FLAGS=('native_identity_admission',
 'native_geometry_inference',
 'scale_admission',
 'units_admission',
 'natural_caller_reachability',
 'hardware_qualification',
 'stock_function_stubs',
 'native_publication')
ADAPTER_SHA256='0a90478b215504e26add49dab32c6a7cb66f02eb199c087fa1130d2ffd939613'
SPANS=tuple((row['start'],row['end']) for row in UNIT['code'])


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','entries','observer',
            'context_bytes','frame_bytes','frame_prefix','unit','readonly_observation','adapter',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-register-only-helpers'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or not test_contract.exact((value['entries'],value['observer'],value['context_bytes'],
                value['frame_bytes'],value['frame_prefix']),(list(ENTRIES),OBSERVER,80,192,160))
            or any(value[name] is not False for name in FLAGS)
            or not test_contract.exact(value['unit'],UNIT)
            or not test_contract.exact(value['readonly_observation'],OBSERVED_SPANS)
            or hashlib.sha256(json.dumps(value['adapter'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=ADAPTER_SHA256):
        raise ValueError('the register-only source changes an exact natural helper entry, byte or observation premise')
    return dict(value,entry=[dict(start=first,end=last) for first,last in SPANS])


def require_image(declared,image):
    if (type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256
            or not test_contract.exact(declared['unit'],UNIT)):
        raise ValueError('the register-only source changes its complete owned image or tested unit')


def independent_fixture(declared,image):
    require_image(declared,image)
    return image,[]


def fixture_for_case(declared,image,case):
    from kb import register_only_helpers_matrix as matrix
    matrix.require_case(case)
    return independent_fixture(declared,image)
