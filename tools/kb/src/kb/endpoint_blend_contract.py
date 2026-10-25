"""Exact complete stock endpoint and blend composition under ordinary observation."""
import hashlib
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR = 'defs/JK08A.endpoint-blend-paths.toml'
ENTRY = 0x740E2
ENTRIES = (ENTRY,)
OBSERVER = 'tools/sh-elf-run/stock_ignition_consumer_invoke.s'
DECLARED = {'schema': 1,
 'id': 'jk08a-endpoint-blend',
 'layout': '7mfk',
 'rom': 'JK08A',
 'image_sha256': 'ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23',
 'scope': 'Complete natural signed endpoint surfaces, actual saturating weight and all final blended word '
          'choices.',
 'entries': [475362],
 'observer': 'tools/sh-elf-run/stock_ignition_consumer_invoke.s',
 'context_bytes': 80,
 'frame_bytes': 192,
 'frame_prefix': 160,
 'unit': {'assembly': 'tools/sh-elf-run/stock_jk08a_endpoint_blend.s',
          'code': [{'start': 157224, 'end': 157272},
                   {'start': 158456, 'end': 158502},
                   {'start': 158504, 'end': 158592},
                   {'start': 158596, 'end': 158656},
                   {'start': 158992, 'end': 159142},
                   {'start': 475176, 'end': 475310},
                   {'start': 475310, 'end': 475362},
                   {'start': 475362, 'end': 475448}],
          'pools': [{'address': 157272, 'size': 4, 'stock_hex': '00026b28'},
                    {'address': 157276, 'size': 4, 'stock_hex': '00026b84'},
                    {'address': 158592, 'size': 4, 'stock_hex': '00026af8'},
                    {'address': 158656, 'size': 4, 'stock_hex': '00026d10'},
                    {'address': 475448, 'size': 2, 'stock_hex': '0a70'},
                    {'address': 475450, 'size': 2, 'stock_hex': '0a72'},
                    {'address': 475452, 'size': 2, 'stock_hex': '0a80'},
                    {'address': 475454, 'size': 2, 'stock_hex': '0a6a'},
                    {'address': 475456, 'size': 4, 'stock_hex': 'ffff1094'},
                    {'address': 475460, 'size': 4, 'stock_hex': 'ffff424c'},
                    {'address': 475464, 'size': 4, 'stock_hex': '000171c8'},
                    {'address': 475468, 'size': 4, 'stock_hex': '00018916'},
                    {'address': 475472, 'size': 4, 'stock_hex': '00018936'},
                    {'address': 475476, 'size': 4, 'stock_hex': '00026628'},
                    {'address': 475480, 'size': 4, 'stock_hex': 'ffff128c'},
                    {'address': 475484, 'size': 4, 'stock_hex': '00016fc8'},
                    {'address': 475488, 'size': 4, 'stock_hex': 'ffff245c'},
                    {'address': 475492, 'size': 4, 'stock_hex': '000162dc'}],
          'aliases': [{'address': 475456, 'width': 4, 'original': 4294906004, 'alias': 16781460},
                      {'address': 475460, 'width': 4, 'original': 4294918732, 'alias': 16794188},
                      {'address': 475480, 'width': 4, 'original': 4294906508, 'alias': 16781964},
                      {'address': 475488, 'width': 4, 'original': 4294911068, 'alias': 16786524}]},
 'controlled_calibration': [{'address': 90844, 'size': 2},
                            {'address': 94152, 'size': 512},
                            {'address': 94664, 'size': 512},
                            {'address': 100630, 'size': 32},
                            {'address': 100662, 'size': 32},
                            {'address': 157272, 'size': 4},
                            {'address': 157276, 'size': 4},
                            {'address': 158592, 'size': 4},
                            {'address': 158656, 'size': 4},
                            {'address': 475448, 'size': 2},
                            {'address': 475450, 'size': 2},
                            {'address': 475452, 'size': 2},
                            {'address': 475454, 'size': 2},
                            {'address': 475456, 'size': 4},
                            {'address': 475460, 'size': 4},
                            {'address': 475464, 'size': 4},
                            {'address': 475468, 'size': 4},
                            {'address': 475472, 'size': 4},
                            {'address': 475476, 'size': 4},
                            {'address': 475480, 'size': 4},
                            {'address': 475484, 'size': 4},
                            {'address': 475488, 'size': 4},
                            {'address': 475492, 'size': 4}],
 'bound_spans': [{'address': 157224, 'size': 48},
                 {'address': 158456, 'size': 46},
                 {'address': 158504, 'size': 88},
                 {'address': 158596, 'size': 60},
                 {'address': 158992, 'size': 150},
                 {'address': 475176, 'size': 134},
                 {'address': 475310, 'size': 52},
                 {'address': 475362, 'size': 86},
                 {'address': 90844, 'size': 2},
                 {'address': 94152, 'size': 512},
                 {'address': 94664, 'size': 512},
                 {'address': 100630, 'size': 32},
                 {'address': 100662, 'size': 32},
                 {'address': 157272, 'size': 4},
                 {'address': 157276, 'size': 4},
                 {'address': 158592, 'size': 4},
                 {'address': 158656, 'size': 4},
                 {'address': 475448, 'size': 2},
                 {'address': 475450, 'size': 2},
                 {'address': 475452, 'size': 2},
                 {'address': 475454, 'size': 2},
                 {'address': 475456, 'size': 4},
                 {'address': 475460, 'size': 4},
                 {'address': 475464, 'size': 4},
                 {'address': 475468, 'size': 4},
                 {'address': 475472, 'size': 4},
                 {'address': 475476, 'size': 4},
                 {'address': 475480, 'size': 4},
                 {'address': 475484, 'size': 4},
                 {'address': 475488, 'size': 4},
                 {'address': 475492, 'size': 4}],
 'input_blobs': [{'name': 'surface_a', 'address': 94664, 'size': 512},
                 {'name': 'surface_b', 'address': 94152, 'size': 512},
                 {'name': 'axis_x', 'address': 100630, 'size': 32},
                 {'name': 'axis_y', 'address': 100662, 'size': 32}],
 'control_blobs': [{'name': 'weight_step', 'address': 90844, 'size': 2, 'stock_hex': '012c'}],
 'actual_endpoints': [{'table': 94664, 'call': 475250, 'output': 4294909180, 'store': 475266},
                      {'table': 94152, 'call': 475276, 'output': 4294909182, 'store': 475288}],
 'actual_weight': {'entry': 475310,
                   'input': 4294909196,
                   'control': 4294911068,
                   'bit': 2,
                   'step': 90844,
                   'store_delay': 475360},
 'actual_blend': {'entry': 475362,
                  'output': 4294909174,
                  'store': 475438,
                  'maximum_weight_selects_B_exactly': True},
 'reused_source_sha256': {'defs/JK08A.timing-denominator.toml': '407f42035990e98f84b513394d3fe0c8728e5742bb776d98e13f8adf9ee93e33',
                          'tools/sh-elf-run/stock_jk08a_timing_denominator.s': '616bc7c9a1f0b269183cc2ac096ba46626966830285c017dbdeb2eeffb1b1e1c',
                          'tools/sh-elf-run/stock_ignition_consumer_invoke.s': 'f0803224463944e2ecef86b1694e8802b01a5146a3fe706db39a4a1be9512809',
                          'tools/kb/src/kb/byte_surface_equations.py': '2c686f6ef380bf88a1635742b4cf6b25f3998b49a83e1f014baa698c3f5548cf',
                          'tools/kb/src/kb/packed_transfer_evidence.py': '7aa7f7e57a5b1a2db170e0b7003bf52bf42e96160fdfd92a7655764227bc866c',
                          'tools/kb/src/kb/test_stock_abi.py': 'e0fbc5f20b99e736449ba68afd5879915b432088922493bbcfc5da0bf318240c',
                          'tools/kb/src/kb/width_view_matrix.py': '087e0f9e3db4874db26841f3cf4c89ce38bc7a9df152e916b8313110e8142869',
                          'tools/kb/src/kb/timing_denominator_contract.py': '7b58c1255b8851db8f53f5c8f45a4c56000db4fc6717d902a0724dabf0e19ef3',
                          'tools/kb/src/kb/timing_denominator_matrix.py': '9c0c1a00db24333f996a86dced884c3b1755773334bd34efcfe932068ef59c9e',
                          'tools/kb/src/kb/timing_denominator_semantics.py': 'b8401b6bc3e6bd8e6a230c9b40e696afa31d3581801be7570e8a0f56ae8d9516',
                          'tools/kb/src/kb/timing_denominator_capture_evidence.py': '7ea0b371eaa05063d144bc3a8f386b7e64915917ec3b4848b56d2ebef5cfbfe6'},
 'native_identity_admission': False,
 'native_geometry_inference': False,
 'scale_admission': False,
 'units_admission': False,
 'natural_caller_reachability': False,
 'natural_scheduling_inference': False,
 'hardware_qualification': False,
 'stock_function_stubs': False,
 'native_publication': False}
FUNCTIONS = (157224, 158456, 158504, 158596, 158992, 475176, 475310, 475362)
LITERAL_OPERANDS = {157234: (157276, 4, 7),
 157266: (157272, 4, 7),
 158526: (158592, 4, 7),
 158630: (158656, 4, 2),
 475192: (475456, 4, 0),
 475198: (475460, 4, 6),
 475234: (475464, 4, 4),
 475238: (475468, 4, 10),
 475242: (475472, 4, 11),
 475244: (475476, 4, 12),
 475248: (475480, 4, 9),
 475256: (475448, 2, 0),
 475260: (475484, 4, 4),
 475282: (475450, 2, 0),
 475310: (475488, 4, 6),
 475312: (475480, 4, 4),
 475316: (475492, 4, 5),
 475320: (475452, 2, 0),
 475356: (475452, 2, 0),
 475374: (475480, 4, 7),
 475376: (475452, 2, 0),
 475386: (475448, 2, 0),
 475400: (475450, 2, 0),
 475406: (475448, 2, 0),
 475416: (475450, 2, 0),
 475436: (475454, 2, 0)}
IMAGE_SHA256 = DECLARED['image_sha256']
UNIT = DECLARED['unit']
CONTROLLED_CALIBRATION = DECLARED['controlled_calibration']
BOUND_SPANS = DECLARED['bound_spans']
SPANS = tuple((row['start'], row['end']) for row in UNIT['code'])

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def descriptor(root):
    value = tomllib.loads((Path(root) / DESCRIPTOR).read_text())
    if not test_contract.exact(value, DECLARED):
        raise ValueError('the endpoint blend changes a full natural entry, source, operand or observer premise')
    for name, wanted in value['reused_source_sha256'].items():
        if sha((Path(root) / name).read_bytes()) != wanted:
            raise ValueError('the endpoint blend changes a complete reused source dependency')
    return dict(value, entry=[dict(start=a, end=b) for a, b in SPANS])

def require_image(source, image):
    if type(image) is not bytes or sha(image) != IMAGE_SHA256 or not test_contract.exact(source['unit'], UNIT):
        raise ValueError('the endpoint blend changes its complete owned image or exact reconstructed unit')
    for row in (*UNIT['pools'], *DECLARED['control_blobs']):
        at, size = row['address'], row['size']
        if image[at:at+size].hex() != row['stock_hex']:
            raise ValueError('the endpoint blend changes an exact stock pointer, literal or weight step')

def independent_fixture(source, image):
    require_image(source, image)
    out = bytearray(image)
    for row in UNIT['aliases']:
        at = row['address']
        if int.from_bytes(image[at:at+4], 'big') != row['original']:
            raise ValueError('the endpoint blend relocates another native pointer')
        out[at:at+4] = row['alias'].to_bytes(4, 'big')
    return bytes(out), [dict(row) for row in UNIT['aliases']]

def fixture_for_case(source, image, case):
    from kb import endpoint_blend_matrix as matrix
    matrix.require_case(case)
    out, aliases = independent_fixture(source, image)
    out = bytearray(out)
    for at, raw in matrix.input_calibrations(case).items():
        out[at:at+len(raw)] = raw
    return bytes(out), aliases
