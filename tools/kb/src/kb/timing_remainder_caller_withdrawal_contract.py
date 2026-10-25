"""Exact natural timing remainder caller withdrawal paths, literal inputs and declared pointer aliases."""

import hashlib
import json
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.timing-remainder-caller-withdrawal-paths.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
ENTRIES=(317852, 336296)
UNIT={'assembly': 'tools/sh-elf-run/stock_jk08a_timing_remainder_caller_withdrawal.s',
 'code': [{'start': 138172, 'end': 138454},
          {'start': 138464, 'end': 138694},
          {'start': 138772, 'end': 139064},
          {'start': 156876, 'end': 156910},
          {'start': 157504, 'end': 157550},
          {'start': 158084, 'end': 158144},
          {'start': 158840, 'end': 158990},
          {'start': 317852, 'end': 318116},
          {'start': 318120, 'end': 318364},
          {'start': 336296, 'end': 336530}],
 'pools': [{'address': 33424, 'size': 1, 'stock_hex': '00'},
           {'address': 33770, 'size': 1, 'stock_hex': '1e'},
           {'address': 34576, 'size': 1, 'stock_hex': '7c'},
           {'address': 35388, 'size': 1, 'stock_hex': '64'},
           {'address': 35389, 'size': 1, 'stock_hex': '64'},
           {'address': 138456, 'size': 4, 'stock_hex': 'ffff9818'},
           {'address': 138460, 'size': 4, 'stock_hex': '0000044e'},
           {'address': 138696, 'size': 4, 'stock_hex': 'ffff9818'},
           {'address': 138700, 'size': 4, 'stock_hex': '0000044e'},
           {'address': 139064, 'size': 4, 'stock_hex': 'ffff9818'},
           {'address': 139068, 'size': 4, 'stock_hex': '0000044e'},
           {'address': 156912, 'size': 4, 'stock_hex': '00026740'},
           {'address': 156916, 'size': 4, 'stock_hex': '00026984'},
           {'address': 158144, 'size': 4, 'stock_hex': '00026c78'},
           {'address': 318116, 'size': 2, 'stock_hex': '02a9'},
           {'address': 318118, 'size': 2, 'stock_hex': '0278'},
           {'address': 318364, 'size': 2, 'stock_hex': '0278'},
           {'address': 318366, 'size': 2, 'stock_hex': '02a9'},
           {'address': 318368, 'size': 4, 'stock_hex': 'ffff1ff4'},
           {'address': 318372, 'size': 4, 'stock_hex': '00008710'},
           {'address': 318376, 'size': 4, 'stock_hex': 'ffff24c0'},
           {'address': 318380, 'size': 4, 'stock_hex': 'ffff11d4'},
           {'address': 318384, 'size': 4, 'stock_hex': 'ffff22f8'},
           {'address': 318388, 'size': 4, 'stock_hex': 'ffff23bc'},
           {'address': 318392, 'size': 4, 'stock_hex': '00008290'},
           {'address': 318396, 'size': 4, 'stock_hex': 'ffff2330'},
           {'address': 318400, 'size': 4, 'stock_hex': 'ffff25fb'},
           {'address': 318404, 'size': 4, 'stock_hex': '000147da'},
           {'address': 318408, 'size': 4, 'stock_hex': '00013c48'},
           {'address': 318412, 'size': 4, 'stock_hex': '000264cc'},
           {'address': 318416, 'size': 4, 'stock_hex': 'ffff2459'},
           {'address': 318420, 'size': 4, 'stock_hex': '00008a3c'},
           {'address': 318424, 'size': 4, 'stock_hex': '00008a3d'},
           {'address': 318428, 'size': 4, 'stock_hex': '00021ce0'},
           {'address': 318432, 'size': 4, 'stock_hex': 'ffff40cc'},
           {'address': 318436, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 336534, 'size': 2, 'stock_hex': '06a2'},
           {'address': 336536, 'size': 4, 'stock_hex': 'ffff23bc'},
           {'address': 336540, 'size': 4, 'stock_hex': 'ffff4184'},
           {'address': 336544, 'size': 4, 'stock_hex': 'ffff1094'},
           {'address': 336548, 'size': 4, 'stock_hex': 'ffff119c'},
           {'address': 336552, 'size': 4, 'stock_hex': '0000c49b'},
           {'address': 336556, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 336560, 'size': 4, 'stock_hex': 'ffff24c8'},
           {'address': 336564, 'size': 4, 'stock_hex': '000083ea'},
           {'address': 336568, 'size': 4, 'stock_hex': '00021bbc'},
           {'address': 336572, 'size': 4, 'stock_hex': '00021e14'},
           {'address': 336576, 'size': 4, 'stock_hex': 'ffff424c'}],
 'aliases': [{'address': 138456, 'width': 4, 'original': 4294940696, 'alias': 16816152},
             {'address': 138696, 'width': 4, 'original': 4294940696, 'alias': 16816152},
             {'address': 139064, 'width': 4, 'original': 4294940696, 'alias': 16816152},
             {'address': 318368, 'width': 4, 'original': 4294909940, 'alias': 16785396},
             {'address': 318376, 'width': 4, 'original': 4294911168, 'alias': 16786624},
             {'address': 318380, 'width': 4, 'original': 4294906324, 'alias': 16781780},
             {'address': 318384, 'width': 4, 'original': 4294910712, 'alias': 16786168},
             {'address': 318388, 'width': 4, 'original': 4294910908, 'alias': 16786364},
             {'address': 318396, 'width': 4, 'original': 4294910768, 'alias': 16786224},
             {'address': 318400, 'width': 4, 'original': 4294911483, 'alias': 16786939},
             {'address': 318416, 'width': 4, 'original': 4294911065, 'alias': 16786521},
             {'address': 318432, 'width': 4, 'original': 4294918348, 'alias': 16793804},
             {'address': 318436, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 336536, 'width': 4, 'original': 4294910908, 'alias': 16786364},
             {'address': 336540, 'width': 4, 'original': 4294918532, 'alias': 16793988},
             {'address': 336544, 'width': 4, 'original': 4294906004, 'alias': 16781460},
             {'address': 336548, 'width': 4, 'original': 4294906268, 'alias': 16781724},
             {'address': 336556, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 336560, 'width': 4, 'original': 4294911176, 'alias': 16786632},
             {'address': 336576, 'width': 4, 'original': 4294918732, 'alias': 16794188}]}
CONTROLLED_CALIBRATION=[{'address': 33424, 'size': 1},
 {'address': 33770, 'size': 1},
 {'address': 34576, 'size': 1},
 {'address': 35388, 'size': 1},
 {'address': 35389, 'size': 1},
 {'address': 80968, 'size': 16},
 {'address': 83930, 'size': 18},
 {'address': 138456, 'size': 4},
 {'address': 138460, 'size': 4},
 {'address': 138696, 'size': 4},
 {'address': 138700, 'size': 4},
 {'address': 139064, 'size': 4},
 {'address': 139068, 'size': 4},
 {'address': 156912, 'size': 4},
 {'address': 156916, 'size': 4},
 {'address': 158144, 'size': 4},
 {'address': 318116, 'size': 2},
 {'address': 318118, 'size': 2},
 {'address': 318364, 'size': 2},
 {'address': 318366, 'size': 2},
 {'address': 318368, 'size': 4},
 {'address': 318372, 'size': 4},
 {'address': 318376, 'size': 4},
 {'address': 318380, 'size': 4},
 {'address': 318384, 'size': 4},
 {'address': 318388, 'size': 4},
 {'address': 318392, 'size': 4},
 {'address': 318396, 'size': 4},
 {'address': 318400, 'size': 4},
 {'address': 318404, 'size': 4},
 {'address': 318408, 'size': 4},
 {'address': 318412, 'size': 4},
 {'address': 318416, 'size': 4},
 {'address': 318420, 'size': 4},
 {'address': 318424, 'size': 4},
 {'address': 318428, 'size': 4},
 {'address': 318432, 'size': 4},
 {'address': 318436, 'size': 4},
 {'address': 336534, 'size': 2},
 {'address': 336536, 'size': 4},
 {'address': 336540, 'size': 4},
 {'address': 336544, 'size': 4},
 {'address': 336548, 'size': 4},
 {'address': 336552, 'size': 4},
 {'address': 336556, 'size': 4},
 {'address': 336560, 'size': 4},
 {'address': 336564, 'size': 4},
 {'address': 336568, 'size': 4},
 {'address': 336572, 'size': 4},
 {'address': 336576, 'size': 4}]
BOUND_SPANS=({'address': 138172, 'size': 282},
 {'address': 138464, 'size': 230},
 {'address': 138772, 'size': 292},
 {'address': 156876, 'size': 34},
 {'address': 157504, 'size': 46},
 {'address': 158084, 'size': 60},
 {'address': 158840, 'size': 150},
 {'address': 317852, 'size': 264},
 {'address': 318120, 'size': 244},
 {'address': 336296, 'size': 234},
 {'address': 33424, 'size': 1},
 {'address': 33770, 'size': 1},
 {'address': 34576, 'size': 1},
 {'address': 35388, 'size': 1},
 {'address': 35389, 'size': 1},
 {'address': 80968, 'size': 16},
 {'address': 83930, 'size': 18},
 {'address': 138456, 'size': 4},
 {'address': 138460, 'size': 4},
 {'address': 138696, 'size': 4},
 {'address': 138700, 'size': 4},
 {'address': 139064, 'size': 4},
 {'address': 139068, 'size': 4},
 {'address': 156912, 'size': 4},
 {'address': 156916, 'size': 4},
 {'address': 158144, 'size': 4},
 {'address': 318116, 'size': 2},
 {'address': 318118, 'size': 2},
 {'address': 318364, 'size': 2},
 {'address': 318366, 'size': 2},
 {'address': 318368, 'size': 4},
 {'address': 318372, 'size': 4},
 {'address': 318376, 'size': 4},
 {'address': 318380, 'size': 4},
 {'address': 318384, 'size': 4},
 {'address': 318388, 'size': 4},
 {'address': 318392, 'size': 4},
 {'address': 318396, 'size': 4},
 {'address': 318400, 'size': 4},
 {'address': 318404, 'size': 4},
 {'address': 318408, 'size': 4},
 {'address': 318412, 'size': 4},
 {'address': 318416, 'size': 4},
 {'address': 318420, 'size': 4},
 {'address': 318424, 'size': 4},
 {'address': 318428, 'size': 4},
 {'address': 318432, 'size': 4},
 {'address': 318436, 'size': 4},
 {'address': 336534, 'size': 2},
 {'address': 336536, 'size': 4},
 {'address': 336540, 'size': 4},
 {'address': 336544, 'size': 4},
 {'address': 336548, 'size': 4},
 {'address': 336552, 'size': 4},
 {'address': 336556, 'size': 4},
 {'address': 336560, 'size': 4},
 {'address': 336564, 'size': 4},
 {'address': 336568, 'size': 4},
 {'address': 336572, 'size': 4},
 {'address': 336576, 'size': 4})
FLAGS=('native_identity_admission',
 'native_geometry_inference',
 'scale_admission',
 'units_admission',
 'natural_caller_reachability',
 'hardware_qualification',
 'stock_function_stubs',
 'native_publication')
CONFIGURATION=[{'address': 83930, 'field': 'curve_word_00', 'size': 2},
 {'address': 83932, 'field': 'curve_word_01', 'size': 2},
 {'address': 83934, 'field': 'curve_word_02', 'size': 2},
 {'address': 83936, 'field': 'curve_word_03', 'size': 2},
 {'address': 83938, 'field': 'curve_word_04', 'size': 2},
 {'address': 83940, 'field': 'curve_word_05', 'size': 2},
 {'address': 83942, 'field': 'curve_word_06', 'size': 2},
 {'address': 83944, 'field': 'curve_word_07', 'size': 2},
 {'address': 83946, 'field': 'curve_word_08', 'size': 2},
 {'address': 34576, 'field': 'mode_flag', 'size': 1},
 {'address': 33424, 'field': 'counter_reload', 'size': 1},
 {'address': 33770, 'field': 'remainder_offset', 'size': 1},
 {'address': 35388, 'field': 'first_gain', 'size': 1},
 {'address': 35389, 'field': 'second_gain', 'size': 1}]
INPUT_BLOBS=[{'name': 'curve_words', 'address': 83930, 'size': 18}, {'name': 'axis_words', 'address': 80968, 'size': 16}]
ADAPTER_SHA256='c632b6bfddd5e2110b67b7f3a1cecd93eba437acacce98428da9499751681d19'
HELPER_ENTRIES=(138172, 138464, 138772, 156876, 157504, 158084, 158840)
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
 'tools/sh-elf-run/viridian_armadillo_capture.py': 'c946bac1f378562a7f46c3362321413c8661af64affe1d581b31107617548698',
 'tools/sh-elf-run/stock_jk08a_injection_start_delay.s': 'f887ab01761ec298155ed8dd400a42ba25a71c14e0912548583af85ebaf60d80',
 'tools/sh-elf-run/harness-stock-jk08a-injection-start-delay.c': 'f7b47c4be99baf27dd10537415456a317261431ec722770c2dd0f41be8fdb46d'}
FUNCTIONS=(*ENTRIES,*HELPER_ENTRIES)
SPANS=tuple((row['start'],row['end']) for row in UNIT['code'])


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','entries','observer',
            'context_bytes','frame_bytes','frame_prefix','unit','controlled_calibration','configuration','input_blobs','adapter',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-timing-remainder-caller-withdrawal'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or not test_contract.exact((value['entries'],value['observer'],value['context_bytes'],value['frame_bytes'],
                value['frame_prefix']),(list(ENTRIES),OBSERVER,80,192,160))
            or any(value[name] is not False for name in FLAGS)
            or not test_contract.exact(value['unit'],UNIT)
            or not test_contract.exact(value['controlled_calibration'],CONTROLLED_CALIBRATION)
            or not test_contract.exact(value['configuration'],CONFIGURATION)
            or not test_contract.exact(value['input_blobs'],INPUT_BLOBS)
            or hashlib.sha256(json.dumps(value['adapter'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=ADAPTER_SHA256):
        raise ValueError('the timing remainder caller withdrawal paths change an exact natural entry, code/pool byte, alias or complete observer premise')
    require_reused_helper_boundary(root)
    return dict(value,entry=[dict(start=first,end=last) for first,last in SPANS])


def require_image(declared,image):
    if (type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256
            or not test_contract.exact(declared['unit'],UNIT)):
        raise ValueError('the timing remainder caller withdrawal paths change the complete owned stock image or exact unit')
    for row in UNIT['pools']:
        if image[row['address']:row['address']+row['size']].hex()!=row['stock_hex']:
            raise ValueError('the timing remainder caller withdrawal paths change a pinned exact stock pool or configuration byte')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for row in UNIT['aliases']:
        at=row['address']
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('the timing remainder caller withdrawal paths relocate a different original native pointer')
        fixture[at:at+4]=row['alias'].to_bytes(4,'big');aliases.append(dict(row))
    return bytes(fixture),aliases


def fixture_for_case(declared,image,case):
    from kb import timing_remainder_caller_withdrawal_matrix as matrix
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
            raise ValueError('the timing remainder caller changes a complete reused timing/normalization/division/viridian/remainder source boundary')
