"""Exact natural actuator mask access paths, literal inputs and declared pointer aliases."""

import hashlib
import json
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.actuator-mask-access-paths.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
ENTRIES=(330092,)
UNIT={'assembly': 'tools/sh-elf-run/stock_jk08a_actuator_mask_access.s',
 'code': [{'start': 155168, 'end': 155204},
          {'start': 330092, 'end': 330144},
          {'start': 330144, 'end': 330218},
          {'start': 330218, 'end': 330246}],
 'pools': [{'address': 155408, 'size': 4, 'stock_hex': 'ffff5718'},
           {'address': 330328, 'size': 2, 'stock_hex': '0123'},
           {'address': 330516, 'size': 4, 'stock_hex': 'ffff119c'},
           {'address': 330520, 'size': 4, 'stock_hex': '00025e20'},
           {'address': 330524, 'size': 4, 'stock_hex': 'ffff1094'}],
 'aliases': [{'address': 155408, 'width': 4, 'original': 4294924056, 'alias': 16799512},
             {'address': 330516, 'width': 4, 'original': 4294906268, 'alias': 16781724},
             {'address': 330524, 'width': 4, 'original': 4294906004, 'alias': 16781460}]}
CONTROLLED_CALIBRATION=[{'address': 155408, 'size': 4},
 {'address': 330328, 'size': 2},
 {'address': 330516, 'size': 4},
 {'address': 330520, 'size': 4},
 {'address': 330524, 'size': 4}]
BOUND_SPANS=({'address': 155168, 'size': 36},
 {'address': 330092, 'size': 52},
 {'address': 330144, 'size': 74},
 {'address': 330218, 'size': 28},
 {'address': 155408, 'size': 4},
 {'address': 330328, 'size': 2},
 {'address': 330516, 'size': 4},
 {'address': 330520, 'size': 4},
 {'address': 330524, 'size': 4})
FLAGS=('native_identity_admission',
 'native_geometry_inference',
 'scale_admission',
 'units_admission',
 'natural_caller_reachability',
 'hardware_qualification',
 'stock_function_stubs',
 'native_publication')
CONFIGURATION=[]
INPUT_BLOBS=[]
ADAPTER_SHA256='5ef44133854bf737a8e6f7623db16293f7d1f8ca504559597af7ce96cfa45299'
HELPER_ENTRIES=(155168, 330144, 330218)
REUSED_HELPER_FILES_SHA256={'defs/JK08A.maf-record-readers.toml': '951d4a914418e91eb4885a9733537cdf03d56af10b8846f3e7602b3e58a6d1db',
 'tools/sh-elf-run/stock_jk08a_maf_record_readers.s': '3bd2b1a1d00d45003ae9fc833831684f3e63ad263ce498b9fd3511216e8ed55f',
 'tools/kb/src/kb/maf_record_contract.py': 'b5aa0ef83773d651be93f089f7e6e26b46dd99a67f897c22bb093d804d1ade92',
 'tools/kb/src/kb/maf_record_matrix.py': '21c10a48c9f121a40c9f592ed99f13af88e8de705aeb8d84992810a71099503b',
 'tools/kb/src/kb/maf_record_semantics.py': 'b26ce790d01dc9123fbc8451e40fad6c81db682304bc52ae83de55e363898b11',
 'tools/kb/src/kb/maf_record_capture_evidence.py': 'd8bc66d54e3a91a48b5a696791e041202db5b64724cc22c84c3e392f0f34f1cd',
 'tools/sh-elf-run/maf_record_capture.py': 'bc2decb03c1c18fa03c19c5f9dee1985fbe0a7298810b1532db82febb6ff68db',
 'tools/sh-elf-run/harness-maf-record.c': '7a3a73f5f27b5912321adb25f7106bd5372a47e92e0390b25d515fafa4d2d1f0',
 'defs/JK08A.paired-inhibit-writer-withdrawal-paths.toml': 'f37e081ed11c77ec4022fce89be2eb1d3f690d6f8aab79e1f366a430d8ed2b49',
 'tools/sh-elf-run/stock_jk08a_paired_inhibit_writer_withdrawal.s': '53044d90056325b33154ec297377c17e4537809b8920812935e3a21a83328869',
 'tools/kb/src/kb/paired_inhibit_writer_withdrawal_contract.py': 'c5b1f72c0c10a1f2516418459b4bc1fa186e1eb7ef4dc34b49fa347bdf734af1',
 'tools/kb/src/kb/paired_inhibit_writer_withdrawal_matrix.py': 'ce82ffe2b16a9e901ab949acdcb570d9b68684bc225720fdca4431fdc54ceb88',
 'tools/kb/src/kb/paired_inhibit_writer_withdrawal_semantics.py': '64786a40cc6a314ee77330035f3b3560e0cc8c269b599855c49ef56913215aeb',
 'tools/kb/src/kb/paired_inhibit_writer_withdrawal_transfers.py': '263af512962490156926efb461bfc4d8f6556f2410a5c7af1f638446a2a11ad6',
 'tools/sh-elf-run/paired_inhibit_writer_withdrawal_capture.py': '13c6a8443db26aa6a31b32fdeba816e88a9e5ec4dc0d2cb3d828ff39fd935a32',
 'tools/sh-elf-run/harness-paired-inhibit-writer-withdrawal-paths.c': '252af6204971e188e1ab28236312a723f04c5c2eabf6ade2aaef08a66de8219e',
 'tools/kb/tests/test_paired_inhibit_writer_withdrawal_adapter_generated.py': '152455e3b9245ccc87025c889fb1d28f2508de4de3a3a7693ac0d51872e192e0',
 'tools/kb/src/kb/paired_inhibit_writer_withdrawal_capture_evidence.py': '6fb556f5f5b0f67bc0d67bace35632c3385da757eee39d5f61a2e8814fd433de'}
FUNCTIONS=(*ENTRIES,*HELPER_ENTRIES)
SPANS=tuple((row['start'],row['end']) for row in UNIT['code'])


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','entries','observer',
            'context_bytes','frame_bytes','frame_prefix','unit','controlled_calibration','configuration','input_blobs','adapter',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-actuator-mask-access'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or not test_contract.exact((value['entries'],value['observer'],value['context_bytes'],value['frame_bytes'],
                value['frame_prefix']),(list(ENTRIES),OBSERVER,80,192,160))
            or any(value[name] is not False for name in FLAGS)
            or not test_contract.exact(value['unit'],UNIT)
            or not test_contract.exact(value['controlled_calibration'],CONTROLLED_CALIBRATION)
            or not test_contract.exact(value['configuration'],CONFIGURATION)
            or not test_contract.exact(value['input_blobs'],INPUT_BLOBS)
            or hashlib.sha256(json.dumps(value['adapter'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=ADAPTER_SHA256):
        raise ValueError('the actuator mask access paths change an exact natural entry, code/pool byte, alias or complete observer premise')
    require_reused_helper_boundary(root)
    return dict(value,entry=[dict(start=first,end=last) for first,last in SPANS])


def require_image(declared,image):
    if (type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256
            or not test_contract.exact(declared['unit'],UNIT)):
        raise ValueError('the actuator mask access paths change the complete owned stock image or exact unit')
    for row in UNIT['pools']:
        if image[row['address']:row['address']+row['size']].hex()!=row['stock_hex']:
            raise ValueError('the actuator mask access paths change a pinned exact stock pool or configuration byte')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for row in UNIT['aliases']:
        at=row['address']
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('the actuator mask access paths relocate a different original native pointer')
        fixture[at:at+4]=row['alias'].to_bytes(4,'big');aliases.append(dict(row))
    return bytes(fixture),aliases


def fixture_for_case(declared,image,case):
    from kb import actuator_mask_access_matrix as matrix
    matrix.require_case(case);fixture,aliases=independent_fixture(declared,image);fixture=bytearray(fixture)
    for row in CONFIGURATION:
        at,size=row['address'],row['size'];fixture[at:at+size]=case[row['field']].to_bytes(size,'big')
    return bytes(fixture),aliases


def require_reused_helper_boundary(root):
    for name,wanted in REUSED_HELPER_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=wanted:
            raise ValueError('the actuator mask access changes a complete reused diagnostic-record and paired writer source boundaries')
