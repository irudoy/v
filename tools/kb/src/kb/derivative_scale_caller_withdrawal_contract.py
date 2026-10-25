"""Exact natural derivative scale caller withdrawal paths, literal inputs and declared pointer aliases."""

import hashlib
import json
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.derivative-scale-caller-withdrawal-paths.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
ENTRIES=(751834, 752188)
UNIT={'assembly': 'tools/sh-elf-run/stock_jk08a_derivative_scale_caller_withdrawal.s',
 'code': [{'start': 138172, 'end': 138454},
          {'start': 138464, 'end': 138694},
          {'start': 156876, 'end': 156910},
          {'start': 156920, 'end': 156954},
          {'start': 157504, 'end': 157550},
          {'start': 158084, 'end': 158144},
          {'start': 158840, 'end': 158990},
          {'start': 751834, 'end': 751948},
          {'start': 752044, 'end': 752188},
          {'start': 752188, 'end': 752378},
          {'start': 752390, 'end': 752536}],
 'pools': [{'address': 34514, 'size': 1, 'stock_hex': '00'},
           {'address': 34515, 'size': 1, 'stock_hex': '00'},
           {'address': 34841, 'size': 1, 'stock_hex': '00'},
           {'address': 34866, 'size': 1, 'stock_hex': '00'},
           {'address': 35376, 'size': 1, 'stock_hex': '00'},
           {'address': 35380, 'size': 1, 'stock_hex': '00'},
           {'address': 35381, 'size': 1, 'stock_hex': '00'},
           {'address': 35382, 'size': 1, 'stock_hex': '00'},
           {'address': 37522, 'size': 2, 'stock_hex': '0000'},
           {'address': 138456, 'size': 4, 'stock_hex': 'ffff9818'},
           {'address': 138460, 'size': 4, 'stock_hex': '0000044e'},
           {'address': 138696, 'size': 4, 'stock_hex': 'ffff9818'},
           {'address': 138700, 'size': 4, 'stock_hex': '0000044e'},
           {'address': 156912, 'size': 4, 'stock_hex': '00026740'},
           {'address': 156916, 'size': 4, 'stock_hex': '00026984'},
           {'address': 156956, 'size': 4, 'stock_hex': '00026740'},
           {'address': 156960, 'size': 4, 'stock_hex': '00026984'},
           {'address': 158144, 'size': 4, 'stock_hex': '00026c78'},
           {'address': 751954, 'size': 2, 'stock_hex': '4e20'},
           {'address': 751956, 'size': 2, 'stock_hex': '763b'},
           {'address': 751958, 'size': 2, 'stock_hex': '7fff'},
           {'address': 751960, 'size': 2, 'stock_hex': '09c4'},
           {'address': 751980, 'size': 4, 'stock_hex': '00021bbc'},
           {'address': 752032, 'size': 4, 'stock_hex': 'ffff763c'},
           {'address': 752036, 'size': 4, 'stock_hex': '000086d2'},
           {'address': 752040, 'size': 4, 'stock_hex': '0001fffe'},
           {'address': 752378, 'size': 2, 'stock_hex': 'ff01'},
           {'address': 752380, 'size': 2, 'stock_hex': '06a0'},
           {'address': 752382, 'size': 2, 'stock_hex': '4e20'},
           {'address': 752384, 'size': 2, 'stock_hex': '763b'},
           {'address': 752386, 'size': 2, 'stock_hex': '7fff'},
           {'address': 752388, 'size': 2, 'stock_hex': '09c4'},
           {'address': 752624, 'size': 2, 'stock_hex': 'ff01'},
           {'address': 752626, 'size': 2, 'stock_hex': '09c4'},
           {'address': 752628, 'size': 2, 'stock_hex': '0930'},
           {'address': 752632, 'size': 4, 'stock_hex': '00009292'},
           {'address': 752636, 'size': 4, 'stock_hex': '00008819'},
           {'address': 752640, 'size': 4, 'stock_hex': '00021bbc'},
           {'address': 752644, 'size': 4, 'stock_hex': 'ffff0001'},
           {'address': 752648, 'size': 4, 'stock_hex': '00014cca'},
           {'address': 752652, 'size': 4, 'stock_hex': '00013b38'},
           {'address': 752656, 'size': 4, 'stock_hex': '000264f8'},
           {'address': 752660, 'size': 4, 'stock_hex': '00021ce0'},
           {'address': 752664, 'size': 4, 'stock_hex': 'ffff28f8'},
           {'address': 752668, 'size': 4, 'stock_hex': '00008a30'},
           {'address': 752672, 'size': 4, 'stock_hex': 'ffff763c'},
           {'address': 752676, 'size': 4, 'stock_hex': '00014e42'},
           {'address': 752680, 'size': 4, 'stock_hex': '00013bb8'},
           {'address': 752684, 'size': 4, 'stock_hex': '000264cc'},
           {'address': 752688, 'size': 4, 'stock_hex': '0001fffe'},
           {'address': 752692, 'size': 4, 'stock_hex': '00008832'},
           {'address': 752696, 'size': 4, 'stock_hex': '000151f2'},
           {'address': 752700, 'size': 4, 'stock_hex': '00013bf8'}],
 'aliases': [{'address': 138456, 'width': 4, 'original': 4294940696, 'alias': 16816152},
             {'address': 138696, 'width': 4, 'original': 4294940696, 'alias': 16816152},
             {'address': 752664, 'width': 4, 'original': 4294912248, 'alias': 16787704}]}
CONTROLLED_CALIBRATION=[{'address': 34514, 'size': 1},
 {'address': 34515, 'size': 1},
 {'address': 34841, 'size': 1},
 {'address': 34866, 'size': 1},
 {'address': 35376, 'size': 7},
 {'address': 37522, 'size': 2},
 {'address': 80696, 'size': 32},
 {'address': 80824, 'size': 16},
 {'address': 80888, 'size': 32},
 {'address': 85194, 'size': 34},
 {'address': 85570, 'size': 18},
 {'address': 86514, 'size': 34},
 {'address': 138456, 'size': 4},
 {'address': 138460, 'size': 4},
 {'address': 138696, 'size': 4},
 {'address': 138700, 'size': 4},
 {'address': 156912, 'size': 4},
 {'address': 156916, 'size': 4},
 {'address': 156956, 'size': 4},
 {'address': 156960, 'size': 4},
 {'address': 158144, 'size': 4},
 {'address': 751954, 'size': 2},
 {'address': 751956, 'size': 2},
 {'address': 751958, 'size': 2},
 {'address': 751960, 'size': 2},
 {'address': 751980, 'size': 4},
 {'address': 752032, 'size': 4},
 {'address': 752036, 'size': 4},
 {'address': 752040, 'size': 4},
 {'address': 752378, 'size': 2},
 {'address': 752380, 'size': 2},
 {'address': 752382, 'size': 2},
 {'address': 752384, 'size': 2},
 {'address': 752386, 'size': 2},
 {'address': 752388, 'size': 2},
 {'address': 752624, 'size': 2},
 {'address': 752626, 'size': 2},
 {'address': 752628, 'size': 2},
 {'address': 752632, 'size': 4},
 {'address': 752636, 'size': 4},
 {'address': 752640, 'size': 4},
 {'address': 752644, 'size': 4},
 {'address': 752648, 'size': 4},
 {'address': 752652, 'size': 4},
 {'address': 752656, 'size': 4},
 {'address': 752660, 'size': 4},
 {'address': 752664, 'size': 4},
 {'address': 752668, 'size': 4},
 {'address': 752672, 'size': 4},
 {'address': 752676, 'size': 4},
 {'address': 752680, 'size': 4},
 {'address': 752684, 'size': 4},
 {'address': 752688, 'size': 4},
 {'address': 752692, 'size': 4},
 {'address': 752696, 'size': 4},
 {'address': 752700, 'size': 4}]
BOUND_SPANS=({'address': 138172, 'size': 282},
 {'address': 138464, 'size': 230},
 {'address': 156876, 'size': 34},
 {'address': 156920, 'size': 34},
 {'address': 157504, 'size': 46},
 {'address': 158084, 'size': 60},
 {'address': 158840, 'size': 150},
 {'address': 751834, 'size': 114},
 {'address': 752044, 'size': 144},
 {'address': 752188, 'size': 190},
 {'address': 752390, 'size': 146},
 {'address': 34514, 'size': 1},
 {'address': 34515, 'size': 1},
 {'address': 34841, 'size': 1},
 {'address': 34866, 'size': 1},
 {'address': 35376, 'size': 7},
 {'address': 37522, 'size': 2},
 {'address': 80696, 'size': 32},
 {'address': 80824, 'size': 16},
 {'address': 80888, 'size': 32},
 {'address': 85194, 'size': 34},
 {'address': 85570, 'size': 18},
 {'address': 86514, 'size': 34},
 {'address': 138456, 'size': 4},
 {'address': 138460, 'size': 4},
 {'address': 138696, 'size': 4},
 {'address': 138700, 'size': 4},
 {'address': 156912, 'size': 4},
 {'address': 156916, 'size': 4},
 {'address': 156956, 'size': 4},
 {'address': 156960, 'size': 4},
 {'address': 158144, 'size': 4},
 {'address': 751954, 'size': 2},
 {'address': 751956, 'size': 2},
 {'address': 751958, 'size': 2},
 {'address': 751960, 'size': 2},
 {'address': 751980, 'size': 4},
 {'address': 752032, 'size': 4},
 {'address': 752036, 'size': 4},
 {'address': 752040, 'size': 4},
 {'address': 752378, 'size': 2},
 {'address': 752380, 'size': 2},
 {'address': 752382, 'size': 2},
 {'address': 752384, 'size': 2},
 {'address': 752386, 'size': 2},
 {'address': 752388, 'size': 2},
 {'address': 752624, 'size': 2},
 {'address': 752626, 'size': 2},
 {'address': 752628, 'size': 2},
 {'address': 752632, 'size': 4},
 {'address': 752636, 'size': 4},
 {'address': 752640, 'size': 4},
 {'address': 752644, 'size': 4},
 {'address': 752648, 'size': 4},
 {'address': 752652, 'size': 4},
 {'address': 752656, 'size': 4},
 {'address': 752660, 'size': 4},
 {'address': 752664, 'size': 4},
 {'address': 752668, 'size': 4},
 {'address': 752672, 'size': 4},
 {'address': 752676, 'size': 4},
 {'address': 752680, 'size': 4},
 {'address': 752684, 'size': 4},
 {'address': 752688, 'size': 4},
 {'address': 752692, 'size': 4},
 {'address': 752696, 'size': 4},
 {'address': 752700, 'size': 4})
FLAGS=('native_identity_admission',
 'native_geometry_inference',
 'scale_admission',
 'units_admission',
 'natural_caller_reachability',
 'hardware_qualification',
 'stock_function_stubs',
 'native_publication')
CONFIGURATION=[{'address': 85194, 'field': 'curve_first_00', 'size': 2},
 {'address': 85196, 'field': 'curve_first_01', 'size': 2},
 {'address': 85198, 'field': 'curve_first_02', 'size': 2},
 {'address': 85200, 'field': 'curve_first_03', 'size': 2},
 {'address': 85202, 'field': 'curve_first_04', 'size': 2},
 {'address': 85204, 'field': 'curve_first_05', 'size': 2},
 {'address': 85206, 'field': 'curve_first_06', 'size': 2},
 {'address': 85208, 'field': 'curve_first_07', 'size': 2},
 {'address': 85210, 'field': 'curve_first_08', 'size': 2},
 {'address': 85212, 'field': 'curve_first_09', 'size': 2},
 {'address': 85214, 'field': 'curve_first_10', 'size': 2},
 {'address': 85216, 'field': 'curve_first_11', 'size': 2},
 {'address': 85218, 'field': 'curve_first_12', 'size': 2},
 {'address': 85220, 'field': 'curve_first_13', 'size': 2},
 {'address': 85222, 'field': 'curve_first_14', 'size': 2},
 {'address': 85224, 'field': 'curve_first_15', 'size': 2},
 {'address': 85226, 'field': 'curve_first_16', 'size': 2},
 {'address': 85570, 'field': 'curve_middle_00', 'size': 2},
 {'address': 85572, 'field': 'curve_middle_01', 'size': 2},
 {'address': 85574, 'field': 'curve_middle_02', 'size': 2},
 {'address': 85576, 'field': 'curve_middle_03', 'size': 2},
 {'address': 85578, 'field': 'curve_middle_04', 'size': 2},
 {'address': 85580, 'field': 'curve_middle_05', 'size': 2},
 {'address': 85582, 'field': 'curve_middle_06', 'size': 2},
 {'address': 85584, 'field': 'curve_middle_07', 'size': 2},
 {'address': 85586, 'field': 'curve_middle_08', 'size': 2},
 {'address': 86514, 'field': 'curve_last_00', 'size': 2},
 {'address': 86516, 'field': 'curve_last_01', 'size': 2},
 {'address': 86518, 'field': 'curve_last_02', 'size': 2},
 {'address': 86520, 'field': 'curve_last_03', 'size': 2},
 {'address': 86522, 'field': 'curve_last_04', 'size': 2},
 {'address': 86524, 'field': 'curve_last_05', 'size': 2},
 {'address': 86526, 'field': 'curve_last_06', 'size': 2},
 {'address': 86528, 'field': 'curve_last_07', 'size': 2},
 {'address': 86530, 'field': 'curve_last_08', 'size': 2},
 {'address': 86532, 'field': 'curve_last_09', 'size': 2},
 {'address': 86534, 'field': 'curve_last_10', 'size': 2},
 {'address': 86536, 'field': 'curve_last_11', 'size': 2},
 {'address': 86538, 'field': 'curve_last_12', 'size': 2},
 {'address': 86540, 'field': 'curve_last_13', 'size': 2},
 {'address': 86542, 'field': 'curve_last_14', 'size': 2},
 {'address': 86544, 'field': 'curve_last_15', 'size': 2},
 {'address': 86546, 'field': 'curve_last_16', 'size': 2},
 {'address': 37522, 'field': 'threshold_word', 'size': 2},
 {'address': 34514, 'field': 'ratio_gain_first', 'size': 1},
 {'address': 34515, 'field': 'ratio_gain_second', 'size': 1},
 {'address': 34841, 'field': 'negative_gain_first', 'size': 1},
 {'address': 34866, 'field': 'negative_gain_second', 'size': 1},
 {'address': 35376, 'field': 'ratio_gain_middle', 'size': 1},
 {'address': 35380, 'field': 'selector_gain_last', 'size': 1},
 {'address': 35381, 'field': 'selector_gain_second', 'size': 1},
 {'address': 35382, 'field': 'selector_gain_third', 'size': 1}]
INPUT_BLOBS=[{'name': 'curve_first', 'address': 85194, 'size': 34},
 {'name': 'curve_middle', 'address': 85570, 'size': 18},
 {'name': 'curve_last', 'address': 86514, 'size': 34},
 {'name': 'axis_first', 'address': 80696, 'size': 32},
 {'name': 'axis_middle', 'address': 80824, 'size': 16},
 {'name': 'axis_last', 'address': 80888, 'size': 32},
 {'name': 'selector_block', 'address': 35376, 'size': 7}]
ADAPTER_SHA256='8e2ea8805a2eb2330282a70cc451adbe9a06a8c960cceb7404fc8b0890b935f7'
HELPER_ENTRIES=(138172, 138464, 156876, 156920, 157504, 158084, 158840)
REUSED_HELPER_FILES_SHA256={'defs/JK08A.timing-denominator.toml': '407f42035990e98f84b513394d3fe0c8728e5742bb776d98e13f8adf9ee93e33',
 'tools/sh-elf-run/stock_jk08a_timing_denominator.s': '616bc7c9a1f0b269183cc2ac096ba46626966830285c017dbdeb2eeffb1b1e1c',
 'tools/kb/src/kb/timing_denominator_contract.py': '7b58c1255b8851db8f53f5c8f45a4c56000db4fc6717d902a0724dabf0e19ef3',
 'tools/kb/src/kb/timing_denominator_matrix.py': '9c0c1a00db24333f996a86dced884c3b1755773334bd34efcfe932068ef59c9e',
 'tools/kb/src/kb/timing_denominator_semantics.py': 'b8401b6bc3e6bd8e6a230c9b40e696afa31d3581801be7570e8a0f56ae8d9516',
 'tools/kb/src/kb/timing_denominator_capture_evidence.py': '7ea0b371eaa05063d144bc3a8f386b7e64915917ec3b4848b56d2ebef5cfbfe6',
 'tools/sh-elf-run/timing_denominator_capture.py': '678a1640087cef960f81eeb142ad232922525708859fcf03fa3b1b8d0b5e14dd',
 'defs/JK08A.normalization.toml': 'b9d174009947b7413854d65e027b91133206c5d8251b027ac13940baa44239ed',
 'tools/sh-elf-run/stock_jk08a_normalization.s': '473bed7d7f1e793529bc10e75a881782ebd9bfe7a3f37c9b530880bb0a48464b',
 'tools/kb/src/kb/normalization_contract.py': '2f9c40d7adbd2030ed8df8c8ceb8e4c0210f300dbe06f86ae48e920b8fee8551',
 'tools/kb/src/kb/normalization_argument_contract.py': 'b83a8f6371f5f2fc60d777db04c6f60b3435dbbf72021e67c5f8627d106d2a9e',
 'tools/kb/src/kb/normalization_matrix.py': 'ce0039e26866053704fe910951e6275466ea13036af412794f8cb797855c9a90',
 'tools/kb/src/kb/normalization_semantics.py': '4c17af559b354c1f3575fe2ca344eee6438ef857d1f35d0eac49ae5ff76be3e5',
 'tools/kb/src/kb/normalization_capture_evidence.py': '105e33b7ae6837f0334187ff765c952d25444de7c00dc037520589f3b4ef92ca',
 'tools/sh-elf-run/normalization_capture.py': '28394ebf2cdd24548f7fcd49c1ba0e678c98732b333136ded311ac3c44083ec1',
 'defs/JK08A.division-callees.toml': '7f9946b15693c37f864e3c47751737ab341e453a062280732017a29c658f9ab6',
 'tools/sh-elf-run/stock_jk08a_division_callees.s': 'a46dacba966f536c37c85cdfec520fb35b1292e3638fbb1faa52593f537fa76e',
 'tools/kb/src/kb/division_callees_contract.py': '958ca6f804d7e32c5b1eebc3b6542d612b04dd24f59a964cc51c3d9046f70891',
 'tools/kb/src/kb/division_callees_matrix.py': '571166545e61d9a15eee52925eb84decc96411de28461c09e7d62152585b3780',
 'tools/kb/src/kb/division_callees_semantics.py': 'a87ea86eb0e9243c1dcb6b6424cbf3a29c8e37aa843014ec926bdefbf19d7beb',
 'tools/kb/src/kb/division_callees_capture_evidence.py': '0ee672c6c73a734cf9e01705ed594dddc69e2d22c9e47544fef8231b267e95c6',
 'tools/sh-elf-run/division_callees_capture.py': '270fffde03f81f1609de6f7314ad7882ed61a146c83aba178773cf07060877ae',
 'defs/JK08A.viridian-armadillo.toml': '2ee5ce5d548db45c20de60e8abe7d913a5b58deee47fe9628547b40cf6d0fa59',
 'defs/JK08A.viridian-armadillo-argument.toml': 'cce7c9238fd389a33763301a69cc0c82985d65e6423fc9d0cb4e749f51beadc2',
 'tools/sh-elf-run/stock_jk08a_viridian_armadillo.s': 'ab18baa48a36d075b2cac7a21d1d0eb18a316027debb3fe38bfae17a41895e09',
 'tools/kb/src/kb/viridian_armadillo_contract.py': 'de2a1fa1a153922ae351198b94e056eb8e2ea61ae002be274e1544d4071c1add',
 'tools/kb/src/kb/viridian_armadillo_argument_contract.py': '14ffa51ea86974987e032ebc644558fc3a1317b2e6f35cf4b69836b2a671c8ac',
 'tools/kb/src/kb/viridian_armadillo_matrix.py': '05be7cab5e4ccc3f2d7c4ebe62809eb68f6a969e2857ca1cf1a0a4202e2f2c68',
 'tools/kb/src/kb/viridian_armadillo_semantics.py': '6b1c04403c3dd8e9f4a46d6c1d009d2670e30d0d4c1ff52c02fe984350536788',
 'tools/kb/src/kb/viridian_armadillo_capture_evidence.py': '248215da74e8328b206f180452d29427a4da0502997d84fbe429df50be6c7bea',
 'tools/sh-elf-run/viridian_armadillo_capture.py': 'c946bac1f378562a7f46c3362321413c8661af64affe1d581b31107617548698'}
FUNCTIONS=(*ENTRIES,*HELPER_ENTRIES)
SPANS=tuple((row['start'],row['end']) for row in UNIT['code'])


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','entries','observer',
            'context_bytes','frame_bytes','frame_prefix','unit','controlled_calibration','configuration','input_blobs','adapter',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-derivative-scale-caller-withdrawal'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or not test_contract.exact((value['entries'],value['observer'],value['context_bytes'],value['frame_bytes'],
                value['frame_prefix']),(list(ENTRIES),OBSERVER,80,192,160))
            or any(value[name] is not False for name in FLAGS)
            or not test_contract.exact(value['unit'],UNIT)
            or not test_contract.exact(value['controlled_calibration'],CONTROLLED_CALIBRATION)
            or not test_contract.exact(value['configuration'],CONFIGURATION)
            or not test_contract.exact(value['input_blobs'],INPUT_BLOBS)
            or hashlib.sha256(json.dumps(value['adapter'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=ADAPTER_SHA256):
        raise ValueError('the derivative scale caller withdrawal paths change an exact natural entry, code/pool byte, alias or complete observer premise')
    require_reused_helper_boundary(root)
    return dict(value,entry=[dict(start=first,end=last) for first,last in SPANS])


def require_image(declared,image):
    if (type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256
            or not test_contract.exact(declared['unit'],UNIT)):
        raise ValueError('the derivative scale caller withdrawal paths change the complete owned stock image or exact unit')
    for row in UNIT['pools']:
        if image[row['address']:row['address']+row['size']].hex()!=row['stock_hex']:
            raise ValueError('the derivative scale caller withdrawal paths change a pinned exact stock pool or configuration byte')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for row in UNIT['aliases']:
        at=row['address']
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('the derivative scale caller withdrawal paths relocate a different original native pointer')
        fixture[at:at+4]=row['alias'].to_bytes(4,'big');aliases.append(dict(row))
    return bytes(fixture),aliases


def fixture_for_case(declared,image,case):
    from kb import derivative_scale_caller_withdrawal_matrix as matrix
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
            raise ValueError('the derivative scale caller changes a complete reused timing/normalization/division/viridian source boundary')
