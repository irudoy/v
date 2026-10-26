"""Exact complete stock indexed word reader under the existing ordinary observer."""
import hashlib
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR = 'defs/JK08A.channel-target-reader-paths.toml'
ENTRY = 0xCB1CA
ENTRIES = (ENTRY,)
FUNCTIONS = ENTRIES
OBSERVER = 'tools/sh-elf-run/stock_ignition_consumer_invoke.s'
DECLARED = {'schema': 1,
 'id': 'jk08a-channel-target-reader',
 'layout': '7mfk',
 'rom': 'JK08A',
 'image_sha256': 'ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23',
 'scope': 'Complete uint8-indexed stock word reader and actual saturated regulator-domain publication.',
 'entries': [831946],
 'observer': 'tools/sh-elf-run/stock_ignition_consumer_invoke.s',
 'context_bytes': 80,
 'frame_bytes': 192,
 'frame_prefix': 160,
 'unit': {'assembly': 'tools/sh-elf-run/stock_jk08a_channel_target_reader.s',
          'code': [{'start': 831946, 'end': 831992}],
          'pools': [{'address': 831994, 'size': 2, 'stock_hex': '01a2'},
                    {'address': 832012, 'size': 4, 'stock_hex': 'ffff36d8'},
                    {'address': 832032, 'size': 4, 'stock_hex': 'ffff2898'}],
          'aliases': [{'address': 832012, 'width': 4, 'original': 4294915800, 'alias': 16791256},
                      {'address': 832032, 'width': 4, 'original': 4294912152, 'alias': 16787608}]},
 'controlled_calibration': [{'address': 831994, 'size': 2},
                            {'address': 832012, 'size': 4},
                            {'address': 832032, 'size': 4}],
 'bound_spans': [{'address': 831946, 'size': 46},
                 {'address': 831994, 'size': 2},
                 {'address': 832012, 'size': 4},
                 {'address': 832032, 'size': 4}],
 'physical_read': {'site': 831956,
                   'native_base': 4294912188,
                   'relocated_base': 16787644,
                   'index_bits': 8,
                   'stride': 2,
                   'width_bytes': 2,
                   'register': 6},
 'physical_store': {'site': 831990,
                    'native_base': 4294916218,
                    'relocated_base': 16791674,
                    'index_bits': 8,
                    'stride': 2,
                    'width_bytes': 2,
                    'register': 6,
                    'real_return_delay': True},
 'reused_source_sha256': {'tools/sh-elf-run/stock_jk08a_scalar_ram_word.s': '7c64e2966ab6d8467fd75b36b841d3d77d7d21dbda3d45d39719a068656bacf5',
                          'tools/sh-elf-run/stock_ignition_consumer_invoke.s': 'f0803224463944e2ecef86b1694e8802b01a5146a3fe706db39a4a1be9512809',
                          'tools/kb/src/kb/byte_surface_equations.py': 'c3f54829d9364bd8063d4bedb58d810f673dc21e50ae295edcbaa6818a382012',
                          'tools/kb/src/kb/packed_transfer_evidence.py': '7aa7f7e57a5b1a2db170e0b7003bf52bf42e96160fdfd92a7655764227bc866c',
                          'tools/kb/src/kb/test_stock_abi.py': 'e0fbc5f20b99e736449ba68afd5879915b432088922493bbcfc5da0bf318240c',
                          'tools/kb/src/kb/width_view_matrix.py': '087e0f9e3db4874db26841f3cf4c89ce38bc7a9df152e916b8313110e8142869'},
 'native_identity_admission': False,
 'native_geometry_inference': False,
 'scale_admission': False,
 'units_admission': False,
 'natural_caller_reachability': False,
 'natural_scheduling_inference': False,
 'hardware_qualification': False,
 'stock_function_stubs': False,
 'native_publication': False}
LITERAL_OPERANDS = {831946: (832032, 4, 2), 831980: (832012, 4, 2), 831984: (831994, 2, 3)}
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
        raise ValueError('the indexed reader changes an exact complete entry, source, operand or observer premise')
    for name, wanted in value['reused_source_sha256'].items():
        if sha((Path(root) / name).read_bytes()) != wanted:
            raise ValueError('the indexed reader changes a complete reused source boundary')
    return dict(value, entry=[dict(start=a, end=b) for a, b in SPANS])

def require_image(source, image):
    if type(image) is not bytes or sha(image) != IMAGE_SHA256 or not test_contract.exact(source['unit'], UNIT):
        raise ValueError('the indexed reader changes its complete owned image or reconstructed source unit')
    for row in UNIT['pools']:
        at, size = row['address'], row['size']
        if image[at:at+size].hex() != row['stock_hex']:
            raise ValueError('the indexed reader changes an exact stock pointer or signed16 literal')

def independent_fixture(source, image):
    require_image(source, image)
    out = bytearray(image)
    for row in UNIT['aliases']:
        at = row['address']
        if int.from_bytes(image[at:at+4], 'big') != row['original']:
            raise ValueError('the indexed reader relocates another native pointer')
        out[at:at+4] = row['alias'].to_bytes(4, 'big')
    return bytes(out), [dict(row) for row in UNIT['aliases']]

def fixture_for_case(source, image, case):
    from kb import channel_target_reader_matrix as matrix
    matrix.require_case(case)
    return independent_fixture(source, image)
