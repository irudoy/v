"""Complete natural standalone signed-magnitude helper bytes and observation boundary."""

import hashlib
import json
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR = 'defs/JK08A.signed-abs-register-helper-withdrawal-paths.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
ENTRIES = (140688,)
FUNCTIONS=ENTRIES
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
UNIT = {'assembly': 'tools/sh-elf-run/stock_jk08a_signed_abs_register_helper_withdrawal.s',
 'code': [{'start': 140688, 'end': 140698}],
 'pools': [],
 'aliases': []}
OBSERVED_SPANS = [{'address': 140688, 'size': 10}]
BOUND_SPANS = ({'address': 140688, 'size': 10},)
FLAGS=('native_identity_admission',
 'native_geometry_inference',
 'scale_admission',
 'units_admission',
 'natural_caller_reachability',
 'hardware_qualification',
 'stock_function_stubs',
 'native_publication')
ADAPTER_SHA256 = '19b75975dadd9c3f5d5b271398485205c339fac13ab313c16d2f31d68133a130'
SPANS=tuple((row['start'],row['end']) for row in UNIT['code'])


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','entries','observer',
            'context_bytes','frame_bytes','frame_prefix','unit','readonly_observation','adapter',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-signed-abs-register-helper-withdrawal'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or not test_contract.exact((value['entries'],value['observer'],value['context_bytes'],
                value['frame_bytes'],value['frame_prefix']),(list(ENTRIES),OBSERVER,80,192,160))
            or any(value[name] is not False for name in FLAGS)
            or not test_contract.exact(value['unit'],UNIT)
            or not test_contract.exact(value['readonly_observation'],OBSERVED_SPANS)
            or hashlib.sha256(json.dumps(value['adapter'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=ADAPTER_SHA256):
        raise ValueError('the standalone signed-magnitude source changes an exact natural helper entry, byte or observation premise')
    return dict(value,entry=[dict(start=first,end=last) for first,last in SPANS])


def require_image(declared,image):
    if type(image) is not bytes or image[0x22590:0x2259A].hex()!='44158900644b000b6043':
        raise ValueError('the standalone helper changes an exact CMP/PL, BT, NEG, RTS or delay-slot MOV word')
    if (type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256
            or not test_contract.exact(declared['unit'],UNIT)):
        raise ValueError('the standalone signed-magnitude source changes its complete owned image or tested unit')


def independent_fixture(declared,image):
    require_image(declared,image)
    return image,[]


def fixture_for_case(declared,image,case):
    from kb import signed_abs_register_helper_withdrawal_matrix as matrix
    matrix.require_case(case)
    return independent_fixture(declared,image)

READONLY_OBSERVATION=OBSERVED_SPANS
CONFIGURATION=[]
