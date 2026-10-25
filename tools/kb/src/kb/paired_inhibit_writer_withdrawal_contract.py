"""Exact natural paired flag writer caller withdrawal paths, literal inputs and declared pointer aliases."""

import hashlib
import json
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.paired-inhibit-writer-withdrawal-paths.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
ENTRIES=(510202, 510376)
UNIT={'assembly': 'tools/sh-elf-run/stock_jk08a_paired_inhibit_writer_withdrawal.s',
 'code': [{'start': 510202, 'end': 510376},
          {'start': 510376, 'end': 510552},
          {'start': 514124, 'end': 514134}],
 'pools': [{'address': 34909, 'size': 1, 'stock_hex': '04'},
           {'address': 510552, 'size': 2, 'stock_hex': '056e'},
           {'address': 510554, 'size': 2, 'stock_hex': '04ed'},
           {'address': 510556, 'size': 2, 'stock_hex': '0518'},
           {'address': 510558, 'size': 2, 'stock_hex': '036a'},
           {'address': 510560, 'size': 2, 'stock_hex': '0820'},
           {'address': 510562, 'size': 2, 'stock_hex': '0570'},
           {'address': 510564, 'size': 2, 'stock_hex': '04ef'},
           {'address': 510566, 'size': 2, 'stock_hex': '051c'},
           {'address': 510568, 'size': 2, 'stock_hex': '036c'},
           {'address': 510684, 'size': 4, 'stock_hex': 'ffff4558'},
           {'address': 510688, 'size': 4, 'stock_hex': 'ffff5718'},
           {'address': 510692, 'size': 4, 'stock_hex': 'ffff41a9'},
           {'address': 510696, 'size': 4, 'stock_hex': 'ffff5b2a'},
           {'address': 510700, 'size': 4, 'stock_hex': 'ffff28f8'},
           {'address': 510704, 'size': 4, 'stock_hex': '0000885d'},
           {'address': 514208, 'size': 4, 'stock_hex': 'ffff5b33'}],
 'aliases': [{'address': 510684, 'width': 4, 'original': 4294919512, 'alias': 16794968},
             {'address': 510688, 'width': 4, 'original': 4294924056, 'alias': 16799512},
             {'address': 510692, 'width': 4, 'original': 4294918569, 'alias': 16794025},
             {'address': 510696, 'width': 4, 'original': 4294925098, 'alias': 16800554},
             {'address': 510700, 'width': 4, 'original': 4294912248, 'alias': 16787704},
             {'address': 514208, 'width': 4, 'original': 4294925107, 'alias': 16800563}]}
CONTROLLED_CALIBRATION=[{'address': 34909, 'size': 1},
 {'address': 510552, 'size': 2},
 {'address': 510554, 'size': 2},
 {'address': 510556, 'size': 2},
 {'address': 510558, 'size': 2},
 {'address': 510560, 'size': 2},
 {'address': 510562, 'size': 2},
 {'address': 510564, 'size': 2},
 {'address': 510566, 'size': 2},
 {'address': 510568, 'size': 2},
 {'address': 510684, 'size': 4},
 {'address': 510688, 'size': 4},
 {'address': 510692, 'size': 4},
 {'address': 510696, 'size': 4},
 {'address': 510700, 'size': 4},
 {'address': 510704, 'size': 4},
 {'address': 514208, 'size': 4}]
BOUND_SPANS=({'address': 510202, 'size': 174},
 {'address': 510376, 'size': 176},
 {'address': 514124, 'size': 10},
 {'address': 34909, 'size': 1},
 {'address': 510552, 'size': 2},
 {'address': 510554, 'size': 2},
 {'address': 510556, 'size': 2},
 {'address': 510558, 'size': 2},
 {'address': 510560, 'size': 2},
 {'address': 510562, 'size': 2},
 {'address': 510564, 'size': 2},
 {'address': 510566, 'size': 2},
 {'address': 510568, 'size': 2},
 {'address': 510684, 'size': 4},
 {'address': 510688, 'size': 4},
 {'address': 510692, 'size': 4},
 {'address': 510696, 'size': 4},
 {'address': 510700, 'size': 4},
 {'address': 510704, 'size': 4},
 {'address': 514208, 'size': 4})
FLAGS=('native_identity_admission',
 'native_geometry_inference',
 'scale_admission',
 'units_admission',
 'natural_caller_reachability',
 'hardware_qualification',
 'stock_function_stubs',
 'native_publication')
CONFIGURATION=[{'address': 34909, 'field': 'config_885d', 'size': 1}]
INPUT_BLOBS=[]
ADAPTER_SHA256='14cf501ebdf36324e23ca8a22a5a0197b6a91800b102f48a6ee8bde661341e6b'
HELPER_ENTRIES=(514124,)
REUSED_HELPER_FILES_SHA256={}
FUNCTIONS=(*ENTRIES,*HELPER_ENTRIES)
SPANS=tuple((row['start'],row['end']) for row in UNIT['code'])


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','entries','observer',
            'context_bytes','frame_bytes','frame_prefix','unit','controlled_calibration','configuration','input_blobs','adapter',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-paired-inhibit-writer-withdrawal'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or not test_contract.exact((value['entries'],value['observer'],value['context_bytes'],value['frame_bytes'],
                value['frame_prefix']),(list(ENTRIES),OBSERVER,80,192,160))
            or any(value[name] is not False for name in FLAGS)
            or not test_contract.exact(value['unit'],UNIT)
            or not test_contract.exact(value['controlled_calibration'],CONTROLLED_CALIBRATION)
            or not test_contract.exact(value['configuration'],CONFIGURATION)
            or not test_contract.exact(value['input_blobs'],INPUT_BLOBS)
            or hashlib.sha256(json.dumps(value['adapter'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=ADAPTER_SHA256):
        raise ValueError('the paired flag writer caller withdrawal paths change an exact natural entry, code/pool byte, alias or complete observer premise')
    require_reused_helper_boundary(root)
    return dict(value,entry=[dict(start=first,end=last) for first,last in SPANS])


def require_image(declared,image):
    if (type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256
            or not test_contract.exact(declared['unit'],UNIT)):
        raise ValueError('the paired flag writer caller withdrawal paths change the complete owned stock image or exact unit')
    for row in UNIT['pools']:
        if image[row['address']:row['address']+row['size']].hex()!=row['stock_hex']:
            raise ValueError('the paired flag writer caller withdrawal paths change a pinned exact stock pool or configuration byte')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for row in UNIT['aliases']:
        at=row['address']
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('the paired flag writer caller withdrawal paths relocate a different original native pointer')
        fixture[at:at+4]=row['alias'].to_bytes(4,'big');aliases.append(dict(row))
    return bytes(fixture),aliases


def fixture_for_case(declared,image,case):
    from kb import paired_inhibit_writer_withdrawal_matrix as matrix
    matrix.require_case(case);fixture,aliases=independent_fixture(declared,image);fixture=bytearray(fixture)
    for row in INPUT_BLOBS:
        if not row['name'].startswith('axis_'):continue
        at,size=row['address'],row['size']
        fixture[at:at+size]=matrix.input_blob(row,case,image)
    for row in CONFIGURATION:
        at,size=row['address'],row['size'];fixture[at:at+size]=case[row['field']].to_bytes(size,'big')
    return bytes(fixture),aliases


def require_reused_helper_boundary(root):
    for name,wanted in REUSED_HELPER_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=wanted:
            raise ValueError('the paired flag writer caller changes a complete reused signed/unsigned division,byte-curve and standard implicit-byte source boundary')
