"""Exact natural word interpolation caller withdrawal paths, literal inputs and declared pointer aliases."""

import hashlib
import json
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.word-interp-caller-withdrawal-paths.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
ENTRIES=(470814, 752536)
UNIT={'assembly': 'tools/sh-elf-run/stock_jk08a_word_interp_caller_withdrawal.s',
 'code': [{'start': 156328, 'end': 156376},
          {'start': 157460, 'end': 157494},
          {'start': 157504, 'end': 157550},
          {'start': 157768, 'end': 157856},
          {'start': 158084, 'end': 158144},
          {'start': 158456, 'end': 158502},
          {'start': 158596, 'end': 158656},
          {'start': 158840, 'end': 158990},
          {'start': 158992, 'end': 159142},
          {'start': 470814, 'end': 470900},
          {'start': 752536, 'end': 752606}],
 'pools': [{'address': 156376, 'size': 4, 'stock_hex': '00026848'},
           {'address': 156380, 'size': 4, 'stock_hex': '00026984'},
           {'address': 157496, 'size': 4, 'stock_hex': '00026af8'},
           {'address': 157500, 'size': 4, 'stock_hex': '00026b84'},
           {'address': 157856, 'size': 4, 'stock_hex': '00026740'},
           {'address': 158144, 'size': 4, 'stock_hex': '00026c78'},
           {'address': 158656, 'size': 4, 'stock_hex': '00026d10'},
           {'address': 471042, 'size': 2, 'stock_hex': '0a7c'},
           {'address': 471044, 'size': 2, 'stock_hex': '0a86'},
           {'address': 471060, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 471072, 'size': 4, 'stock_hex': '00018e86'},
           {'address': 471076, 'size': 4, 'stock_hex': '00018fd6'},
           {'address': 471080, 'size': 4, 'stock_hex': '00026714'},
           {'address': 471084, 'size': 4, 'stock_hex': '00018f96'},
           {'address': 471088, 'size': 4, 'stock_hex': '00018e46'},
           {'address': 752630, 'size': 2, 'stock_hex': '040c'},
           {'address': 752664, 'size': 4, 'stock_hex': 'ffff28f8'},
           {'address': 752704, 'size': 4, 'stock_hex': '00013d74'},
           {'address': 752708, 'size': 4, 'stock_hex': '00013db4'},
           {'address': 752712, 'size': 4, 'stock_hex': '0000d40e'},
           {'address': 752716, 'size': 4, 'stock_hex': '000262a8'}],
 'aliases': [{'address': 471060, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 752664, 'width': 4, 'original': 4294912248, 'alias': 16787704}]}
CONTROLLED_CALIBRATION=[{'address': 54286, 'size': 512},
 {'address': 81268, 'size': 32},
 {'address': 81332, 'size': 32},
 {'address': 101958, 'size': 64},
 {'address': 102022, 'size': 64},
 {'address': 102294, 'size': 130},
 {'address': 156376, 'size': 4},
 {'address': 156380, 'size': 4},
 {'address': 157496, 'size': 4},
 {'address': 157500, 'size': 4},
 {'address': 157856, 'size': 4},
 {'address': 158144, 'size': 4},
 {'address': 158656, 'size': 4},
 {'address': 471042, 'size': 2},
 {'address': 471044, 'size': 2},
 {'address': 471060, 'size': 4},
 {'address': 471072, 'size': 4},
 {'address': 471076, 'size': 4},
 {'address': 471080, 'size': 4},
 {'address': 471084, 'size': 4},
 {'address': 471088, 'size': 4},
 {'address': 752630, 'size': 2},
 {'address': 752664, 'size': 4},
 {'address': 752704, 'size': 4},
 {'address': 752708, 'size': 4},
 {'address': 752712, 'size': 4},
 {'address': 752716, 'size': 4}]
BOUND_SPANS=({'address': 156328, 'size': 48},
 {'address': 157460, 'size': 34},
 {'address': 157504, 'size': 46},
 {'address': 157768, 'size': 88},
 {'address': 158084, 'size': 60},
 {'address': 158456, 'size': 46},
 {'address': 158596, 'size': 60},
 {'address': 158840, 'size': 150},
 {'address': 158992, 'size': 150},
 {'address': 470814, 'size': 86},
 {'address': 752536, 'size': 70},
 {'address': 54286, 'size': 512},
 {'address': 81268, 'size': 32},
 {'address': 81332, 'size': 32},
 {'address': 101958, 'size': 64},
 {'address': 102022, 'size': 64},
 {'address': 102294, 'size': 130},
 {'address': 156376, 'size': 4},
 {'address': 156380, 'size': 4},
 {'address': 157496, 'size': 4},
 {'address': 157500, 'size': 4},
 {'address': 157856, 'size': 4},
 {'address': 158144, 'size': 4},
 {'address': 158656, 'size': 4},
 {'address': 471042, 'size': 2},
 {'address': 471044, 'size': 2},
 {'address': 471060, 'size': 4},
 {'address': 471072, 'size': 4},
 {'address': 471076, 'size': 4},
 {'address': 471080, 'size': 4},
 {'address': 471084, 'size': 4},
 {'address': 471088, 'size': 4},
 {'address': 752630, 'size': 2},
 {'address': 752664, 'size': 4},
 {'address': 752704, 'size': 4},
 {'address': 752708, 'size': 4},
 {'address': 752712, 'size': 4},
 {'address': 752716, 'size': 4})
FLAGS=('native_identity_admission',
 'native_geometry_inference',
 'scale_admission',
 'units_admission',
 'natural_caller_reachability',
 'hardware_qualification',
 'stock_function_stubs',
 'native_publication')
CONFIGURATION=[{'address': 102294, 'field': 'curve_word_000', 'size': 2},
 {'address': 102296, 'field': 'curve_word_001', 'size': 2},
 {'address': 102298, 'field': 'curve_word_002', 'size': 2},
 {'address': 102300, 'field': 'curve_word_003', 'size': 2},
 {'address': 102302, 'field': 'curve_word_004', 'size': 2},
 {'address': 102304, 'field': 'curve_word_005', 'size': 2},
 {'address': 102306, 'field': 'curve_word_006', 'size': 2},
 {'address': 102308, 'field': 'curve_word_007', 'size': 2},
 {'address': 102310, 'field': 'curve_word_008', 'size': 2},
 {'address': 102312, 'field': 'curve_word_009', 'size': 2},
 {'address': 102314, 'field': 'curve_word_010', 'size': 2},
 {'address': 102316, 'field': 'curve_word_011', 'size': 2},
 {'address': 102318, 'field': 'curve_word_012', 'size': 2},
 {'address': 102320, 'field': 'curve_word_013', 'size': 2},
 {'address': 102322, 'field': 'curve_word_014', 'size': 2},
 {'address': 102324, 'field': 'curve_word_015', 'size': 2},
 {'address': 102326, 'field': 'curve_word_016', 'size': 2},
 {'address': 102328, 'field': 'curve_word_017', 'size': 2},
 {'address': 102330, 'field': 'curve_word_018', 'size': 2},
 {'address': 102332, 'field': 'curve_word_019', 'size': 2},
 {'address': 102334, 'field': 'curve_word_020', 'size': 2},
 {'address': 102336, 'field': 'curve_word_021', 'size': 2},
 {'address': 102338, 'field': 'curve_word_022', 'size': 2},
 {'address': 102340, 'field': 'curve_word_023', 'size': 2},
 {'address': 102342, 'field': 'curve_word_024', 'size': 2},
 {'address': 102344, 'field': 'curve_word_025', 'size': 2},
 {'address': 102346, 'field': 'curve_word_026', 'size': 2},
 {'address': 102348, 'field': 'curve_word_027', 'size': 2},
 {'address': 102350, 'field': 'curve_word_028', 'size': 2},
 {'address': 102352, 'field': 'curve_word_029', 'size': 2},
 {'address': 102354, 'field': 'curve_word_030', 'size': 2},
 {'address': 102356, 'field': 'curve_word_031', 'size': 2},
 {'address': 102358, 'field': 'curve_word_032', 'size': 2},
 {'address': 102360, 'field': 'curve_word_033', 'size': 2},
 {'address': 102362, 'field': 'curve_word_034', 'size': 2},
 {'address': 102364, 'field': 'curve_word_035', 'size': 2},
 {'address': 102366, 'field': 'curve_word_036', 'size': 2},
 {'address': 102368, 'field': 'curve_word_037', 'size': 2},
 {'address': 102370, 'field': 'curve_word_038', 'size': 2},
 {'address': 102372, 'field': 'curve_word_039', 'size': 2},
 {'address': 102374, 'field': 'curve_word_040', 'size': 2},
 {'address': 102376, 'field': 'curve_word_041', 'size': 2},
 {'address': 102378, 'field': 'curve_word_042', 'size': 2},
 {'address': 102380, 'field': 'curve_word_043', 'size': 2},
 {'address': 102382, 'field': 'curve_word_044', 'size': 2},
 {'address': 102384, 'field': 'curve_word_045', 'size': 2},
 {'address': 102386, 'field': 'curve_word_046', 'size': 2},
 {'address': 102388, 'field': 'curve_word_047', 'size': 2},
 {'address': 102390, 'field': 'curve_word_048', 'size': 2},
 {'address': 102392, 'field': 'curve_word_049', 'size': 2},
 {'address': 102394, 'field': 'curve_word_050', 'size': 2},
 {'address': 102396, 'field': 'curve_word_051', 'size': 2},
 {'address': 102398, 'field': 'curve_word_052', 'size': 2},
 {'address': 102400, 'field': 'curve_word_053', 'size': 2},
 {'address': 102402, 'field': 'curve_word_054', 'size': 2},
 {'address': 102404, 'field': 'curve_word_055', 'size': 2},
 {'address': 102406, 'field': 'curve_word_056', 'size': 2},
 {'address': 102408, 'field': 'curve_word_057', 'size': 2},
 {'address': 102410, 'field': 'curve_word_058', 'size': 2},
 {'address': 102412, 'field': 'curve_word_059', 'size': 2},
 {'address': 102414, 'field': 'curve_word_060', 'size': 2},
 {'address': 102416, 'field': 'curve_word_061', 'size': 2},
 {'address': 102418, 'field': 'curve_word_062', 'size': 2},
 {'address': 102420, 'field': 'curve_word_063', 'size': 2},
 {'address': 102422, 'field': 'curve_word_064', 'size': 2}]
INPUT_BLOBS=[{'name': 'surface', 'address': 54286, 'size': 512},
 {'name': 'surface_row_axis', 'address': 81268, 'size': 32},
 {'name': 'surface_column_axis', 'address': 81332, 'size': 32},
 {'name': 'curve_high_axis', 'address': 101958, 'size': 64},
 {'name': 'curve_low_axis', 'address': 102022, 'size': 64},
 {'name': 'curve_words', 'address': 102294, 'size': 130}]
ADAPTER_SHA256='f7f8c902fd5f3c22c2a115b907af9cfb8382850c27d4a3d55080ecf9f476f2e1'
HELPER_ENTRIES=(156328, 157460, 157504, 157768, 158084, 158456, 158596, 158840, 158992)
REUSED_HELPER_FILES_SHA256={'defs/JK08A.timing-denominator.toml': '407f42035990e98f84b513394d3fe0c8728e5742bb776d98e13f8adf9ee93e33',
 'tools/sh-elf-run/stock_jk08a_timing_denominator.s': '616bc7c9a1f0b269183cc2ac096ba46626966830285c017dbdeb2eeffb1b1e1c',
 'tools/kb/src/kb/timing_denominator_contract.py': '7b58c1255b8851db8f53f5c8f45a4c56000db4fc6717d902a0724dabf0e19ef3',
 'tools/kb/src/kb/timing_denominator_matrix.py': '9c0c1a00db24333f996a86dced884c3b1755773334bd34efcfe932068ef59c9e',
 'tools/kb/src/kb/timing_denominator_semantics.py': 'b8401b6bc3e6bd8e6a230c9b40e696afa31d3581801be7570e8a0f56ae8d9516',
 'tools/kb/src/kb/timing_denominator_capture_evidence.py': '7ea0b371eaa05063d144bc3a8f386b7e64915917ec3b4848b56d2ebef5cfbfe6',
 'tools/sh-elf-run/timing_denominator_capture.py': '678a1640087cef960f81eeb142ad232922525708859fcf03fa3b1b8d0b5e14dd'}
FUNCTIONS=(*ENTRIES,*HELPER_ENTRIES)
SPANS=tuple((row['start'],row['end']) for row in UNIT['code'])


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','entries','observer',
            'context_bytes','frame_bytes','frame_prefix','unit','controlled_calibration','configuration','input_blobs','adapter',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-word-interp-caller-withdrawal'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or not test_contract.exact((value['entries'],value['observer'],value['context_bytes'],value['frame_bytes'],
                value['frame_prefix']),(list(ENTRIES),OBSERVER,80,192,160))
            or any(value[name] is not False for name in FLAGS)
            or not test_contract.exact(value['unit'],UNIT)
            or not test_contract.exact(value['controlled_calibration'],CONTROLLED_CALIBRATION)
            or not test_contract.exact(value['configuration'],CONFIGURATION)
            or not test_contract.exact(value['input_blobs'],INPUT_BLOBS)
            or hashlib.sha256(json.dumps(value['adapter'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=ADAPTER_SHA256):
        raise ValueError('the word interpolation caller withdrawal paths change an exact natural entry, code/pool byte, alias or complete observer premise')
    require_reused_helper_boundary(root)
    return dict(value,entry=[dict(start=first,end=last) for first,last in SPANS])


def require_image(declared,image):
    if (type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256
            or not test_contract.exact(declared['unit'],UNIT)):
        raise ValueError('the word interpolation caller withdrawal paths change the complete owned stock image or exact unit')
    for row in UNIT['pools']:
        if image[row['address']:row['address']+row['size']].hex()!=row['stock_hex']:
            raise ValueError('the word interpolation caller withdrawal paths change a pinned exact stock pool or configuration byte')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for row in UNIT['aliases']:
        at=row['address']
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('the word interpolation caller withdrawal paths relocate a different original native pointer')
        fixture[at:at+4]=row['alias'].to_bytes(4,'big');aliases.append(dict(row))
    return bytes(fixture),aliases


def fixture_for_case(declared,image,case):
    from kb import word_interp_caller_withdrawal_matrix as matrix
    matrix.require_case(case);fixture,aliases=independent_fixture(declared,image);fixture=bytearray(fixture)
    for row in INPUT_BLOBS:
        if row['name']=='curve_words':continue
        at,size=row['address'],row['size']
        fixture[at:at+size]=matrix.input_blob(row,case,image)
    for row in CONFIGURATION:
        at,size=row['address'],row['size'];fixture[at:at+size]=case[row['field']].to_bytes(size,'big')
    return bytes(fixture),aliases


def require_reused_helper_boundary(root):
    for name,wanted in REUSED_HELPER_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=wanted:
            raise ValueError('the word interpolation caller changes the complete reused timing-helper source boundary')
