"""Exact complete stock endpoint and blend composition under ordinary observation."""
import hashlib
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR = 'defs/JK08A.conditional-endpoint-blend-paths.toml'
ENTRY = 0x76108
ENTRIES = (ENTRY,)
OBSERVER = 'tools/sh-elf-run/stock_ignition_consumer_invoke.s'
DECLARED = {'schema': 1,
 'id': 'jk08a-conditional-endpoint-blend',
 'layout': '7mfk',
 'rom': 'JK08A',
 'image_sha256': 'ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23',
 'scope': 'Complete ROM-gated natural signed endpoint surfaces, actual saturating weight and all final '
          'blended word choices.',
 'entries': [483592],
 'observer': 'tools/sh-elf-run/stock_ignition_consumer_invoke.s',
 'context_bytes': 80,
 'frame_bytes': 192,
 'frame_prefix': 160,
 'unit': {'assembly': 'tools/sh-elf-run/stock_jk08a_conditional_endpoint_blend.s',
          'code': [{'start': 156328, 'end': 156376},
                   {'start': 157504, 'end': 157550},
                   {'start': 157768, 'end': 157856},
                   {'start': 158084, 'end': 158144},
                   {'start': 158840, 'end': 158990},
                   {'start': 483404, 'end': 483538},
                   {'start': 483538, 'end': 483592},
                   {'start': 483592, 'end': 483698}],
          'pools': [{'address': 156376, 'size': 4, 'stock_hex': '00026848'},
                    {'address': 156380, 'size': 4, 'stock_hex': '00026984'},
                    {'address': 157856, 'size': 4, 'stock_hex': '00026740'},
                    {'address': 158144, 'size': 4, 'stock_hex': '00026c78'},
                    {'address': 483698, 'size': 2, 'stock_hex': '0660'},
                    {'address': 483700, 'size': 2, 'stock_hex': '0662'},
                    {'address': 483702, 'size': 2, 'stock_hex': '065a'},
                    {'address': 483704, 'size': 4, 'stock_hex': 'ffff1094'},
                    {'address': 483708, 'size': 4, 'stock_hex': 'ffff424c'},
                    {'address': 483712, 'size': 4, 'stock_hex': '0000de8e'},
                    {'address': 483716, 'size': 4, 'stock_hex': '00013d14'},
                    {'address': 483720, 'size': 4, 'stock_hex': '00013d34'},
                    {'address': 483724, 'size': 4, 'stock_hex': '000262a8'},
                    {'address': 483728, 'size': 4, 'stock_hex': 'ffff128c'},
                    {'address': 483732, 'size': 4, 'stock_hex': '0000e08e'},
                    {'address': 483736, 'size': 4, 'stock_hex': 'ffff23bc'},
                    {'address': 483740, 'size': 4, 'stock_hex': '000090a0'},
                    {'address': 483744, 'size': 4, 'stock_hex': '00008b3f'},
                    {'address': 483748, 'size': 4, 'stock_hex': '000089fa'}],
          'aliases': [{'address': 483704, 'width': 4, 'original': 4294906004, 'alias': 16781460},
                      {'address': 483708, 'width': 4, 'original': 4294918732, 'alias': 16794188},
                      {'address': 483728, 'width': 4, 'original': 4294906508, 'alias': 16781964},
                      {'address': 483736, 'width': 4, 'original': 4294910908, 'alias': 16786364}]},
 'controlled_calibration': [{'address': 35322, 'size': 1},
                            {'address': 35647, 'size': 1},
                            {'address': 37024, 'size': 2},
                            {'address': 56974, 'size': 512},
                            {'address': 57486, 'size': 512},
                            {'address': 81172, 'size': 32},
                            {'address': 81204, 'size': 32},
                            {'address': 156376, 'size': 4},
                            {'address': 156380, 'size': 4},
                            {'address': 157856, 'size': 4},
                            {'address': 158144, 'size': 4},
                            {'address': 483698, 'size': 2},
                            {'address': 483700, 'size': 2},
                            {'address': 483702, 'size': 2},
                            {'address': 483704, 'size': 4},
                            {'address': 483708, 'size': 4},
                            {'address': 483712, 'size': 4},
                            {'address': 483716, 'size': 4},
                            {'address': 483720, 'size': 4},
                            {'address': 483724, 'size': 4},
                            {'address': 483728, 'size': 4},
                            {'address': 483732, 'size': 4},
                            {'address': 483736, 'size': 4},
                            {'address': 483740, 'size': 4},
                            {'address': 483744, 'size': 4},
                            {'address': 483748, 'size': 4}],
 'bound_spans': [{'address': 156328, 'size': 48},
                 {'address': 157504, 'size': 46},
                 {'address': 157768, 'size': 88},
                 {'address': 158084, 'size': 60},
                 {'address': 158840, 'size': 150},
                 {'address': 483404, 'size': 134},
                 {'address': 483538, 'size': 54},
                 {'address': 483592, 'size': 106},
                 {'address': 35322, 'size': 1},
                 {'address': 35647, 'size': 1},
                 {'address': 37024, 'size': 2},
                 {'address': 56974, 'size': 512},
                 {'address': 57486, 'size': 512},
                 {'address': 81172, 'size': 32},
                 {'address': 81204, 'size': 32},
                 {'address': 156376, 'size': 4},
                 {'address': 156380, 'size': 4},
                 {'address': 157856, 'size': 4},
                 {'address': 158144, 'size': 4},
                 {'address': 483698, 'size': 2},
                 {'address': 483700, 'size': 2},
                 {'address': 483702, 'size': 2},
                 {'address': 483704, 'size': 4},
                 {'address': 483708, 'size': 4},
                 {'address': 483712, 'size': 4},
                 {'address': 483716, 'size': 4},
                 {'address': 483720, 'size': 4},
                 {'address': 483724, 'size': 4},
                 {'address': 483728, 'size': 4},
                 {'address': 483732, 'size': 4},
                 {'address': 483736, 'size': 4},
                 {'address': 483740, 'size': 4},
                 {'address': 483744, 'size': 4},
                 {'address': 483748, 'size': 4}],
 'input_blobs': [{'name': 'surface_a', 'address': 56974, 'size': 512},
                 {'name': 'surface_b', 'address': 57486, 'size': 512},
                 {'name': 'axis_x', 'address': 81172, 'size': 32},
                 {'name': 'axis_y', 'address': 81204, 'size': 32}],
 'control_blobs': [{'name': 'weight_step', 'address': 37024, 'size': 2, 'stock_hex': '012c'},
                   {'name': 'gate_8b3f', 'address': 35647, 'size': 1, 'stock_hex': '18'},
                   {'name': 'gate_89fa', 'address': 35322, 'size': 1, 'stock_hex': '40'}],
 'actual_endpoints': [{'table': 56974, 'call': 483478, 'output': 4294908140, 'store': 483494},
                      {'table': 57486, 'call': 483504, 'output': 4294908142, 'store': 483516}],
 'actual_weight': {'entry': 483538,
                   'input': 4294911008,
                   'control': 4294911068,
                   'bit': 2,
                   'step': 37024,
                   'store': 483586,
                   'GBR_restore_delay': 483590},
 'actual_blend': {'entry': 483592,
                  'output': 4294908134,
                  'store': 483688,
                  'maximum_weight_selects_B_exactly': True,
                  'MACL_restored': True},
 'actual_entry_gates': [{'site': 483598, 'address': 35647, 'mask': 128, 'required_clear': True},
                        {'site': 483606, 'address': 35322, 'mask': 32, 'required_set': True}],
 'reused_source_sha256': {'defs/JK08A.timing-denominator.toml': '407f42035990e98f84b513394d3fe0c8728e5742bb776d98e13f8adf9ee93e33',
                          'tools/sh-elf-run/stock_jk08a_timing_denominator.s': '616bc7c9a1f0b269183cc2ac096ba46626966830285c017dbdeb2eeffb1b1e1c',
                          'tools/sh-elf-run/stock_ignition_consumer_invoke.s': 'f0803224463944e2ecef86b1694e8802b01a5146a3fe706db39a4a1be9512809',
                          'tools/kb/src/kb/byte_surface_equations.py': '0056b8869cfcf79f91210ae9cbac4a8b03c0326731adcc8efe9e49a278a1378e',
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
FUNCTIONS = (156328, 157504, 157768, 158084, 158840, 483404, 483538, 483592)
LITERAL_OPERANDS = {156338: (156380, 4, 7),
 156370: (156376, 4, 7),
 157790: (157856, 4, 7),
 158118: (158144, 4, 2),
 483420: (483704, 4, 0),
 483426: (483708, 4, 6),
 483462: (483712, 4, 4),
 483466: (483716, 4, 10),
 483470: (483720, 4, 11),
 483472: (483724, 4, 12),
 483476: (483728, 4, 9),
 483484: (483698, 2, 0),
 483488: (483732, 4, 4),
 483510: (483700, 2, 0),
 483540: (483736, 4, 0),
 483546: (483740, 4, 5),
 483596: (483744, 4, 6),
 483604: (483748, 4, 6),
 483620: (483736, 4, 2),
 483632: (483728, 4, 4),
 483634: (483698, 2, 0),
 483648: (483728, 4, 4),
 483650: (483700, 2, 0),
 483656: (483728, 4, 4),
 483660: (483698, 2, 0),
 483668: (483700, 2, 0),
 483686: (483702, 2, 0)}
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
    from kb import conditional_endpoint_blend_matrix as matrix
    matrix.require_case(case)
    out, aliases = independent_fixture(source, image)
    out = bytearray(out)
    for at, raw in matrix.input_calibrations(case).items():
        out[at:at+len(raw)] = raw
    return bytes(out), aliases
