"""Exact natural curve scale caller withdrawal paths, literal inputs and declared pointer aliases."""

import hashlib
import json
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.curve-scale-caller-withdrawal-paths.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
ENTRIES=(751464,)
UNIT={'assembly': 'tools/sh-elf-run/stock_jk08a_curve_scale_caller_withdrawal.s',
 'code': [{'start': 138172, 'end': 138454},
          {'start': 156964, 'end': 156998},
          {'start': 157504, 'end': 157550},
          {'start': 158084, 'end': 158144},
          {'start': 158840, 'end': 158990},
          {'start': 751464, 'end': 751594}],
 'pools': [{'address': 34115, 'size': 1, 'stock_hex': '00'},
           {'address': 138456, 'size': 4, 'stock_hex': 'ffff9818'},
           {'address': 138460, 'size': 4, 'stock_hex': '0000044e'},
           {'address': 157000, 'size': 4, 'stock_hex': '00026740'},
           {'address': 157004, 'size': 4, 'stock_hex': '00026984'},
           {'address': 158144, 'size': 4, 'stock_hex': '00026c78'},
           {'address': 751680, 'size': 2, 'stock_hex': '2710'},
           {'address': 751682, 'size': 2, 'stock_hex': '6c77'},
           {'address': 751684, 'size': 2, 'stock_hex': '7fff'},
           {'address': 751686, 'size': 2, 'stock_hex': '1388'},
           {'address': 751688, 'size': 2, 'stock_hex': '0410'},
           {'address': 751968, 'size': 4, 'stock_hex': '00014b0a'},
           {'address': 751972, 'size': 4, 'stock_hex': '00013ff4'},
           {'address': 751976, 'size': 4, 'stock_hex': '00026524'},
           {'address': 751980, 'size': 4, 'stock_hex': '00021bbc'},
           {'address': 751984, 'size': 4, 'stock_hex': 'ffff6c78'},
           {'address': 751988, 'size': 4, 'stock_hex': '00008543'},
           {'address': 751992, 'size': 4, 'stock_hex': 'ffff28f8'}],
 'aliases': [{'address': 138456, 'width': 4, 'original': 4294940696, 'alias': 16816152},
             {'address': 751992, 'width': 4, 'original': 4294912248, 'alias': 16787704}]}
CONTROLLED_CALIBRATION=[{'address': 34115, 'size': 1},
 {'address': 138456, 'size': 4},
 {'address': 138460, 'size': 4},
 {'address': 157000, 'size': 4},
 {'address': 157004, 'size': 4},
 {'address': 158144, 'size': 4},
 {'address': 751680, 'size': 2},
 {'address': 751682, 'size': 2},
 {'address': 751684, 'size': 2},
 {'address': 751686, 'size': 2},
 {'address': 751688, 'size': 2},
 {'address': 751968, 'size': 4},
 {'address': 751972, 'size': 4},
 {'address': 751976, 'size': 4},
 {'address': 751980, 'size': 4},
 {'address': 751984, 'size': 4},
 {'address': 751988, 'size': 4},
 {'address': 751992, 'size': 4},
 {'address': 84746, 'size': 66},
 {'address': 81908, 'size': 64}]
BOUND_SPANS=({'address': 138172, 'size': 282},
 {'address': 156964, 'size': 34},
 {'address': 157504, 'size': 46},
 {'address': 158084, 'size': 60},
 {'address': 158840, 'size': 150},
 {'address': 751464, 'size': 130},
 {'address': 34115, 'size': 1},
 {'address': 138456, 'size': 4},
 {'address': 138460, 'size': 4},
 {'address': 157000, 'size': 4},
 {'address': 157004, 'size': 4},
 {'address': 158144, 'size': 4},
 {'address': 751680, 'size': 2},
 {'address': 751682, 'size': 2},
 {'address': 751684, 'size': 2},
 {'address': 751686, 'size': 2},
 {'address': 751688, 'size': 2},
 {'address': 751968, 'size': 4},
 {'address': 751972, 'size': 4},
 {'address': 751976, 'size': 4},
 {'address': 751980, 'size': 4},
 {'address': 751984, 'size': 4},
 {'address': 751988, 'size': 4},
 {'address': 751992, 'size': 4},
 {'address': 84746, 'size': 66},
 {'address': 81908, 'size': 64})
FLAGS=('native_identity_admission',
 'native_geometry_inference',
 'scale_admission',
 'units_admission',
 'natural_caller_reachability',
 'hardware_qualification',
 'stock_function_stubs',
 'native_publication')
CONFIGURATION=[{'address': 84746, 'field': 'curve_word_00', 'size': 2},
 {'address': 84748, 'field': 'curve_word_01', 'size': 2},
 {'address': 84750, 'field': 'curve_word_02', 'size': 2},
 {'address': 84752, 'field': 'curve_word_03', 'size': 2},
 {'address': 84754, 'field': 'curve_word_04', 'size': 2},
 {'address': 84756, 'field': 'curve_word_05', 'size': 2},
 {'address': 84758, 'field': 'curve_word_06', 'size': 2},
 {'address': 84760, 'field': 'curve_word_07', 'size': 2},
 {'address': 84762, 'field': 'curve_word_08', 'size': 2},
 {'address': 84764, 'field': 'curve_word_09', 'size': 2},
 {'address': 84766, 'field': 'curve_word_10', 'size': 2},
 {'address': 84768, 'field': 'curve_word_11', 'size': 2},
 {'address': 84770, 'field': 'curve_word_12', 'size': 2},
 {'address': 84772, 'field': 'curve_word_13', 'size': 2},
 {'address': 84774, 'field': 'curve_word_14', 'size': 2},
 {'address': 84776, 'field': 'curve_word_15', 'size': 2},
 {'address': 84778, 'field': 'curve_word_16', 'size': 2},
 {'address': 84780, 'field': 'curve_word_17', 'size': 2},
 {'address': 84782, 'field': 'curve_word_18', 'size': 2},
 {'address': 84784, 'field': 'curve_word_19', 'size': 2},
 {'address': 84786, 'field': 'curve_word_20', 'size': 2},
 {'address': 84788, 'field': 'curve_word_21', 'size': 2},
 {'address': 84790, 'field': 'curve_word_22', 'size': 2},
 {'address': 84792, 'field': 'curve_word_23', 'size': 2},
 {'address': 84794, 'field': 'curve_word_24', 'size': 2},
 {'address': 84796, 'field': 'curve_word_25', 'size': 2},
 {'address': 84798, 'field': 'curve_word_26', 'size': 2},
 {'address': 84800, 'field': 'curve_word_27', 'size': 2},
 {'address': 84802, 'field': 'curve_word_28', 'size': 2},
 {'address': 84804, 'field': 'curve_word_29', 'size': 2},
 {'address': 84806, 'field': 'curve_word_30', 'size': 2},
 {'address': 84808, 'field': 'curve_word_31', 'size': 2},
 {'address': 84810, 'field': 'curve_word_32', 'size': 2},
 {'address': 34115, 'field': 'gain', 'size': 1}]
INPUT_BLOBS=[{'name': 'curve_words', 'address': 84746, 'size': 66}, {'name': 'axis_words', 'address': 81908, 'size': 64}]
ADAPTER_SHA256='a7e301a27fdf65914e7abe617633f77d2eb3f431af3570357a03005695688a62'
HELPER_ENTRIES=(138172, 156964, 157504, 158084, 158840)
REUSED_HELPER_FILES_SHA256={'defs/JK08A.uptight-duck.toml': 'aa1e2ab8b182e8f3536351da35fefc085491d726c9170f7bd5922b3f00cae9f6',
 'tools/sh-elf-run/stock_jk08a_uptight_duck.s': '7db9700a0fbc5fe4e3149db1931144a311a0548447c0739411c1481bdddf5324',
 'tools/kb/src/kb/uptight_duck_contract.py': '5468c2b7fc1fa9b7b49adb085ae357f731878ddb18a8ec6a6bf5ea384e5ed978',
 'tools/kb/src/kb/uptight_duck_argument_contract.py': '7b1b7f1103458d429bf137556d76eb622ed7a4670eecf511bd295bce675450d3',
 'tools/kb/src/kb/uptight_duck_matrix.py': '239f81f03ebd9457db5099186c141131fb18226ed6ab388b55a8b3ba18801211',
 'tools/kb/src/kb/uptight_duck_semantics.py': '26cebb5947c68fc3bb3fd4a69d2db886f1218b625b0d7e6c2e80a54b345b9685',
 'tools/kb/src/kb/uptight_duck_capture_evidence.py': 'ab84befbc885c4a20cff80a580377b15276148377ca7d296859eeb7634e4b8bd',
 'tools/sh-elf-run/uptight_duck_capture.py': '28dabc2c59812d56e41c549122a9964dff1af0c6fa517f4ee262bb7de0596751',
 'defs/JK08A.division-callees.toml': '7f9946b15693c37f864e3c47751737ab341e453a062280732017a29c658f9ab6',
 'tools/sh-elf-run/stock_jk08a_division_callees.s': 'a46dacba966f536c37c85cdfec520fb35b1292e3638fbb1faa52593f537fa76e',
 'tools/kb/src/kb/division_callees_contract.py': '958ca6f804d7e32c5b1eebc3b6542d612b04dd24f59a964cc51c3d9046f70891',
 'tools/kb/src/kb/division_callees_matrix.py': '571166545e61d9a15eee52925eb84decc96411de28461c09e7d62152585b3780',
 'tools/kb/src/kb/division_callees_semantics.py': 'a87ea86eb0e9243c1dcb6b6424cbf3a29c8e37aa843014ec926bdefbf19d7beb',
 'tools/kb/src/kb/division_callees_capture_evidence.py': '0ee672c6c73a734cf9e01705ed594dddc69e2d22c9e47544fef8231b267e95c6',
 'tools/sh-elf-run/division_callees_capture.py': '270fffde03f81f1609de6f7314ad7882ed61a146c83aba178773cf07060877ae'}
FUNCTIONS=(*ENTRIES,*HELPER_ENTRIES)
SPANS=tuple((row['start'],row['end']) for row in UNIT['code'])


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','entries','observer',
            'context_bytes','frame_bytes','frame_prefix','unit','controlled_calibration','configuration','input_blobs','adapter',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-curve-scale-caller-withdrawal'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or not test_contract.exact((value['entries'],value['observer'],value['context_bytes'],value['frame_bytes'],
                value['frame_prefix']),(list(ENTRIES),OBSERVER,80,192,160))
            or any(value[name] is not False for name in FLAGS)
            or not test_contract.exact(value['unit'],UNIT)
            or not test_contract.exact(value['controlled_calibration'],CONTROLLED_CALIBRATION)
            or not test_contract.exact(value['configuration'],CONFIGURATION)
            or not test_contract.exact(value['input_blobs'],INPUT_BLOBS)
            or hashlib.sha256(json.dumps(value['adapter'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=ADAPTER_SHA256):
        raise ValueError('the curve scale caller withdrawal paths change an exact natural entry, code/pool byte, alias or complete observer premise')
    require_reused_helper_boundary(root)
    return dict(value,entry=[dict(start=first,end=last) for first,last in SPANS])


def require_image(declared,image):
    if (type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256
            or not test_contract.exact(declared['unit'],UNIT)):
        raise ValueError('the curve scale caller withdrawal paths change the complete owned stock image or exact unit')
    for row in UNIT['pools']:
        if image[row['address']:row['address']+row['size']].hex()!=row['stock_hex']:
            raise ValueError('the curve scale caller withdrawal paths change a pinned exact stock pool or configuration byte')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for row in UNIT['aliases']:
        at=row['address']
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('the curve scale caller withdrawal paths relocate a different original native pointer')
        fixture[at:at+4]=row['alias'].to_bytes(4,'big');aliases.append(dict(row))
    return bytes(fixture),aliases


def fixture_for_case(declared,image,case):
    from kb import curve_scale_caller_withdrawal_matrix as matrix
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
            raise ValueError('the curve scale caller changes the complete reused uptight-duck/division source boundary')
