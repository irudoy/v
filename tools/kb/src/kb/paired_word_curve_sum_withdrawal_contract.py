"""Exact natural paired word curve sum withdrawal paths, literal inputs and declared pointer aliases."""

import hashlib
import json
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.paired-word-curve-sum-withdrawal-paths.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
ENTRIES=(470076,)
UNIT={'assembly': 'tools/sh-elf-run/stock_jk08a_paired_word_curve_sum_withdrawal.s',
 'code': [{'start': 156964, 'end': 156998},
          {'start': 157504, 'end': 157550},
          {'start': 158084, 'end': 158144},
          {'start': 158840, 'end': 158990},
          {'start': 470076, 'end': 470260}],
 'pools': [{'address': 157000, 'size': 4, 'stock_hex': '00026740'},
           {'address': 157004, 'size': 4, 'stock_hex': '00026984'},
           {'address': 158144, 'size': 4, 'stock_hex': '00026c78'},
           {'address': 470260, 'size': 2, 'stock_hex': '05b2'},
           {'address': 470262, 'size': 2, 'stock_hex': '0726'},
           {'address': 470264, 'size': 2, 'stock_hex': '072a'},
           {'address': 470268, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 470272, 'size': 4, 'stock_hex': 'ffff24ce'},
           {'address': 470276, 'size': 4, 'stock_hex': 'ffff120e'},
           {'address': 470280, 'size': 4, 'stock_hex': 'ffff28f8'},
           {'address': 470284, 'size': 4, 'stock_hex': 'ffff2898'},
           {'address': 470288, 'size': 4, 'stock_hex': '00013202'},
           {'address': 470292, 'size': 4, 'stock_hex': '000155a0'},
           {'address': 470296, 'size': 4, 'stock_hex': '00026524'}],
 'aliases': [{'address': 470268, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 470272, 'width': 4, 'original': 4294911182, 'alias': 16786638},
             {'address': 470276, 'width': 4, 'original': 4294906382, 'alias': 16781838},
             {'address': 470280, 'width': 4, 'original': 4294912248, 'alias': 16787704},
             {'address': 470284, 'width': 4, 'original': 4294912152, 'alias': 16787608}]}
CONTROLLED_CALIBRATION=[{'address': 78338, 'size': 66},
 {'address': 87456, 'size': 64},
 {'address': 157000, 'size': 4},
 {'address': 157004, 'size': 4},
 {'address': 158144, 'size': 4},
 {'address': 470260, 'size': 2},
 {'address': 470262, 'size': 2},
 {'address': 470264, 'size': 2},
 {'address': 470268, 'size': 4},
 {'address': 470272, 'size': 4},
 {'address': 470276, 'size': 4},
 {'address': 470280, 'size': 4},
 {'address': 470284, 'size': 4},
 {'address': 470288, 'size': 4},
 {'address': 470292, 'size': 4},
 {'address': 470296, 'size': 4}]
BOUND_SPANS=({'address': 156964, 'size': 34},
 {'address': 157504, 'size': 46},
 {'address': 158084, 'size': 60},
 {'address': 158840, 'size': 150},
 {'address': 470076, 'size': 184},
 {'address': 78338, 'size': 66},
 {'address': 87456, 'size': 64},
 {'address': 157000, 'size': 4},
 {'address': 157004, 'size': 4},
 {'address': 158144, 'size': 4},
 {'address': 470260, 'size': 2},
 {'address': 470262, 'size': 2},
 {'address': 470264, 'size': 2},
 {'address': 470268, 'size': 4},
 {'address': 470272, 'size': 4},
 {'address': 470276, 'size': 4},
 {'address': 470280, 'size': 4},
 {'address': 470284, 'size': 4},
 {'address': 470288, 'size': 4},
 {'address': 470292, 'size': 4},
 {'address': 470296, 'size': 4})
FLAGS=('native_identity_admission',
 'native_geometry_inference',
 'scale_admission',
 'units_admission',
 'natural_caller_reachability',
 'hardware_qualification',
 'stock_function_stubs',
 'native_publication')
CONFIGURATION=[{'address': 78338, 'field': 'curve_word_00', 'size': 2},
 {'address': 78340, 'field': 'curve_word_01', 'size': 2},
 {'address': 78342, 'field': 'curve_word_02', 'size': 2},
 {'address': 78344, 'field': 'curve_word_03', 'size': 2},
 {'address': 78346, 'field': 'curve_word_04', 'size': 2},
 {'address': 78348, 'field': 'curve_word_05', 'size': 2},
 {'address': 78350, 'field': 'curve_word_06', 'size': 2},
 {'address': 78352, 'field': 'curve_word_07', 'size': 2},
 {'address': 78354, 'field': 'curve_word_08', 'size': 2},
 {'address': 78356, 'field': 'curve_word_09', 'size': 2},
 {'address': 78358, 'field': 'curve_word_10', 'size': 2},
 {'address': 78360, 'field': 'curve_word_11', 'size': 2},
 {'address': 78362, 'field': 'curve_word_12', 'size': 2},
 {'address': 78364, 'field': 'curve_word_13', 'size': 2},
 {'address': 78366, 'field': 'curve_word_14', 'size': 2},
 {'address': 78368, 'field': 'curve_word_15', 'size': 2},
 {'address': 78370, 'field': 'curve_word_16', 'size': 2},
 {'address': 78372, 'field': 'curve_word_17', 'size': 2},
 {'address': 78374, 'field': 'curve_word_18', 'size': 2},
 {'address': 78376, 'field': 'curve_word_19', 'size': 2},
 {'address': 78378, 'field': 'curve_word_20', 'size': 2},
 {'address': 78380, 'field': 'curve_word_21', 'size': 2},
 {'address': 78382, 'field': 'curve_word_22', 'size': 2},
 {'address': 78384, 'field': 'curve_word_23', 'size': 2},
 {'address': 78386, 'field': 'curve_word_24', 'size': 2},
 {'address': 78388, 'field': 'curve_word_25', 'size': 2},
 {'address': 78390, 'field': 'curve_word_26', 'size': 2},
 {'address': 78392, 'field': 'curve_word_27', 'size': 2},
 {'address': 78394, 'field': 'curve_word_28', 'size': 2},
 {'address': 78396, 'field': 'curve_word_29', 'size': 2},
 {'address': 78398, 'field': 'curve_word_30', 'size': 2},
 {'address': 78400, 'field': 'curve_word_31', 'size': 2},
 {'address': 78402, 'field': 'curve_word_32', 'size': 2},
 {'address': 87456, 'field': 'axis_word_00', 'size': 2},
 {'address': 87458, 'field': 'axis_word_01', 'size': 2},
 {'address': 87460, 'field': 'axis_word_02', 'size': 2},
 {'address': 87462, 'field': 'axis_word_03', 'size': 2},
 {'address': 87464, 'field': 'axis_word_04', 'size': 2},
 {'address': 87466, 'field': 'axis_word_05', 'size': 2},
 {'address': 87468, 'field': 'axis_word_06', 'size': 2},
 {'address': 87470, 'field': 'axis_word_07', 'size': 2},
 {'address': 87472, 'field': 'axis_word_08', 'size': 2},
 {'address': 87474, 'field': 'axis_word_09', 'size': 2},
 {'address': 87476, 'field': 'axis_word_10', 'size': 2},
 {'address': 87478, 'field': 'axis_word_11', 'size': 2},
 {'address': 87480, 'field': 'axis_word_12', 'size': 2},
 {'address': 87482, 'field': 'axis_word_13', 'size': 2},
 {'address': 87484, 'field': 'axis_word_14', 'size': 2},
 {'address': 87486, 'field': 'axis_word_15', 'size': 2},
 {'address': 87488, 'field': 'axis_word_16', 'size': 2},
 {'address': 87490, 'field': 'axis_word_17', 'size': 2},
 {'address': 87492, 'field': 'axis_word_18', 'size': 2},
 {'address': 87494, 'field': 'axis_word_19', 'size': 2},
 {'address': 87496, 'field': 'axis_word_20', 'size': 2},
 {'address': 87498, 'field': 'axis_word_21', 'size': 2},
 {'address': 87500, 'field': 'axis_word_22', 'size': 2},
 {'address': 87502, 'field': 'axis_word_23', 'size': 2},
 {'address': 87504, 'field': 'axis_word_24', 'size': 2},
 {'address': 87506, 'field': 'axis_word_25', 'size': 2},
 {'address': 87508, 'field': 'axis_word_26', 'size': 2},
 {'address': 87510, 'field': 'axis_word_27', 'size': 2},
 {'address': 87512, 'field': 'axis_word_28', 'size': 2},
 {'address': 87514, 'field': 'axis_word_29', 'size': 2},
 {'address': 87516, 'field': 'axis_word_30', 'size': 2},
 {'address': 87518, 'field': 'axis_word_31', 'size': 2}]
INPUT_BLOBS=[{'name': 'curve_words', 'address': 78338, 'size': 66}, {'name': 'axis_words', 'address': 87456, 'size': 64}]
ADAPTER_SHA256='f02e8cb00ebc78cb55885df3fcd52cc27cfc0221b1c9f24adbc7949a6b845ba7'
HELPER_ENTRIES=(156964, 158084, 157504, 158840)
REUSED_HELPER_FILES_SHA256={'defs/JK08A.curve-scale-caller-withdrawal-paths.toml': 'ecb266e69212318a2313236dcadedd1310337979200982f4f351a619f27cf6be',
 'tools/sh-elf-run/stock_jk08a_curve_scale_caller_withdrawal.s': 'badbff3005e24f06e5f77635be706ab5e444f23935ff66c3dbd181d74f547682',
 'tools/kb/src/kb/curve_scale_caller_withdrawal_contract.py': '62fc5e874b5b1660eb77b64bce2e7288c284f9247f06e69603dc5d213cdc54f4',
 'tools/kb/src/kb/curve_scale_caller_withdrawal_matrix.py': 'cdd4f3e45562c3fcc5dbd99399d4f1d31b96e9585ebf95096cefbe7a773ac965',
 'tools/kb/src/kb/curve_scale_caller_withdrawal_semantics.py': '5cec258c846ee2318f25793fd2638dd72be5ceb8afaa85c31a3aee8feac33df4',
 'tools/kb/src/kb/curve_scale_caller_withdrawal_transfers.py': '593afd82c89f3a4f63fa9583682d8331c173a5bbdb0ccb7657c79fc57b0e0b7b',
 'tools/kb/src/kb/curve_scale_caller_withdrawal_capture_evidence.py': '28f5e6774ddef33d5423de1127af3eec0cb068098be79f243df1868f2dcace56',
 'tools/sh-elf-run/curve_scale_caller_withdrawal_capture.py': '5c34f2824f3723e45121b81eee378cf6cf04b29ff25e34c69be8149c781f94bf'}
FUNCTIONS=(*ENTRIES,*HELPER_ENTRIES)
SPANS=tuple((row['start'],row['end']) for row in UNIT['code'])


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','entries','observer',
            'context_bytes','frame_bytes','frame_prefix','unit','controlled_calibration','configuration','input_blobs','adapter',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-paired-word-curve-sum-withdrawal'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or not test_contract.exact((value['entries'],value['observer'],value['context_bytes'],value['frame_bytes'],
                value['frame_prefix']),(list(ENTRIES),OBSERVER,80,192,160))
            or any(value[name] is not False for name in FLAGS)
            or not test_contract.exact(value['unit'],UNIT)
            or not test_contract.exact(value['controlled_calibration'],CONTROLLED_CALIBRATION)
            or not test_contract.exact(value['configuration'],CONFIGURATION)
            or not test_contract.exact(value['input_blobs'],INPUT_BLOBS)
            or hashlib.sha256(json.dumps(value['adapter'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=ADAPTER_SHA256):
        raise ValueError('the paired word curve sum withdrawal paths change an exact natural entry, code/pool byte, alias or complete observer premise')
    require_reused_helper_boundary(root)
    return dict(value,entry=[dict(start=first,end=last) for first,last in SPANS])


def require_image(declared,image):
    if (type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256
            or not test_contract.exact(declared['unit'],UNIT)):
        raise ValueError('the paired word curve sum withdrawal paths change the complete owned stock image or exact unit')
    for row in UNIT['pools']:
        if image[row['address']:row['address']+row['size']].hex()!=row['stock_hex']:
            raise ValueError('the paired word curve sum withdrawal paths change a pinned exact stock pool or configuration byte')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for row in UNIT['aliases']:
        at=row['address']
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('the paired word curve sum withdrawal paths relocate a different original native pointer')
        fixture[at:at+4]=row['alias'].to_bytes(4,'big');aliases.append(dict(row))
    return bytes(fixture),aliases


def fixture_for_case(declared,image,case):
    from kb import paired_word_curve_sum_withdrawal_matrix as matrix
    matrix.require_case(case);fixture,aliases=independent_fixture(declared,image);fixture=bytearray(fixture)
    for row in CONFIGURATION:
        at,size=row['address'],row['size'];fixture[at:at+size]=case[row['field']].to_bytes(size,'big')
    return bytes(fixture),aliases


def require_reused_helper_boundary(root):
    for name,wanted in REUSED_HELPER_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=wanted:
            raise ValueError('the paired word curve sum changes a complete unchanged word-curve/scale source boundary')
