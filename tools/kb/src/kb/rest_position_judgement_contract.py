"""Exact complete bank-index1 rest-position judgement and immutable physical inputs."""
import hashlib
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.rest-position-judgement-paths.toml'
ENTRY=0x90256
ENTRIES=(ENTRY,)
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
DECLARED={'schema': 1,
 'id': 'jk08a-rest-position-judgement',
 'layout': '7mfk',
 'rom': 'JK08A',
 'image_sha256': 'ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23',
 'scope': 'Complete90256 judgement under the exact native bank-index1 raw invocation, real measured-byte '
          'operands, reset permits, counters, timers and fault publications.',
 'entries': [590422],
 'entry_premises': {'register4': 1,
                    'other19_context_fields_independent': True,
                    'full_raw_R5_zero_and_nonzero_admitted': True,
                    'native_bank_general_identity_admission': False},
 'observer': 'tools/sh-elf-run/stock_ignition_consumer_invoke.s',
 'context_bytes': 80,
 'frame_bytes': 192,
 'frame_prefix': 160,
 'unit': {'assembly': 'tools/sh-elf-run/stock_jk08a_rest_position_judgement.s',
          'code': [{'start': 590422, 'end': 590686},
                   {'start': 590694, 'end': 590834},
                   {'start': 590900, 'end': 591042}],
          'pools': [{'address': 590686, 'size': 2, 'stock_hex': '0ca1'},
                    {'address': 590688, 'size': 2, 'stock_hex': '042e'},
                    {'address': 590690, 'size': 2, 'stock_hex': '0c93'},
                    {'address': 590692, 'size': 2, 'stock_hex': '0c8a'},
                    {'address': 590834, 'size': 2, 'stock_hex': '0ca1'},
                    {'address': 590836, 'size': 2, 'stock_hex': '042e'},
                    {'address': 590838, 'size': 2, 'stock_hex': '0c93'},
                    {'address': 590840, 'size': 4, 'stock_hex': 'ffff42d3'},
                    {'address': 590852, 'size': 4, 'stock_hex': 'ffff28f8'},
                    {'address': 590856, 'size': 4, 'stock_hex': 'ffff2324'},
                    {'address': 590860, 'size': 4, 'stock_hex': 'ffff2470'},
                    {'address': 590864, 'size': 4, 'stock_hex': '0000855d'},
                    {'address': 590868, 'size': 4, 'stock_hex': 'ffff2458'},
                    {'address': 590872, 'size': 4, 'stock_hex': '0000871f'},
                    {'address': 590876, 'size': 4, 'stock_hex': '00008951'},
                    {'address': 590880, 'size': 4, 'stock_hex': 'ffff128c'},
                    {'address': 590884, 'size': 4, 'stock_hex': '00008952'},
                    {'address': 590888, 'size': 4, 'stock_hex': '00008e1c'},
                    {'address': 590892, 'size': 4, 'stock_hex': '00008736'},
                    {'address': 590896, 'size': 4, 'stock_hex': '00008737'},
                    {'address': 591268, 'size': 2, 'stock_hex': '0c8a'},
                    {'address': 591270, 'size': 2, 'stock_hex': '0ca1'},
                    {'address': 591584, 'size': 4, 'stock_hex': '00008e1c'},
                    {'address': 591588, 'size': 4, 'stock_hex': 'ffff28f8'},
                    {'address': 591592, 'size': 4, 'stock_hex': '0000871f'},
                    {'address': 591596, 'size': 4, 'stock_hex': '0000855d'}],
          'aliases': [{'address': 590840, 'width': 4, 'original': 4294918867, 'alias': 16794323},
                      {'address': 590852, 'width': 4, 'original': 4294912248, 'alias': 16787704},
                      {'address': 590856, 'width': 4, 'original': 4294910756, 'alias': 16786212},
                      {'address': 590860, 'width': 4, 'original': 4294911088, 'alias': 16786544},
                      {'address': 590868, 'width': 4, 'original': 4294911064, 'alias': 16786520},
                      {'address': 590880, 'width': 4, 'original': 4294906508, 'alias': 16781964},
                      {'address': 591588, 'width': 4, 'original': 4294912248, 'alias': 16787704}]},
 'controlled_calibration': [{'address': 34141, 'size': 1},
                            {'address': 34591, 'size': 1},
                            {'address': 34614, 'size': 1},
                            {'address': 34615, 'size': 1},
                            {'address': 35153, 'size': 1},
                            {'address': 35154, 'size': 1},
                            {'address': 36380, 'size': 1},
                            {'address': 36389, 'size': 1},
                            {'address': 590686, 'size': 2},
                            {'address': 590688, 'size': 2},
                            {'address': 590690, 'size': 2},
                            {'address': 590692, 'size': 2},
                            {'address': 590834, 'size': 2},
                            {'address': 590836, 'size': 2},
                            {'address': 590838, 'size': 2},
                            {'address': 590840, 'size': 4},
                            {'address': 590852, 'size': 4},
                            {'address': 590856, 'size': 4},
                            {'address': 590860, 'size': 4},
                            {'address': 590864, 'size': 4},
                            {'address': 590868, 'size': 4},
                            {'address': 590872, 'size': 4},
                            {'address': 590876, 'size': 4},
                            {'address': 590880, 'size': 4},
                            {'address': 590884, 'size': 4},
                            {'address': 590888, 'size': 4},
                            {'address': 590892, 'size': 4},
                            {'address': 590896, 'size': 4},
                            {'address': 591268, 'size': 2},
                            {'address': 591270, 'size': 2},
                            {'address': 591584, 'size': 4},
                            {'address': 591588, 'size': 4},
                            {'address': 591592, 'size': 4},
                            {'address': 591596, 'size': 4}],
 'bound_spans': [{'address': 590422, 'size': 264},
                 {'address': 590694, 'size': 140},
                 {'address': 590900, 'size': 142},
                 {'address': 34141, 'size': 1},
                 {'address': 34591, 'size': 1},
                 {'address': 34614, 'size': 1},
                 {'address': 34615, 'size': 1},
                 {'address': 35153, 'size': 1},
                 {'address': 35154, 'size': 1},
                 {'address': 36380, 'size': 1},
                 {'address': 36389, 'size': 1},
                 {'address': 590686, 'size': 2},
                 {'address': 590688, 'size': 2},
                 {'address': 590690, 'size': 2},
                 {'address': 590692, 'size': 2},
                 {'address': 590834, 'size': 2},
                 {'address': 590836, 'size': 2},
                 {'address': 590838, 'size': 2},
                 {'address': 590840, 'size': 4},
                 {'address': 590852, 'size': 4},
                 {'address': 590856, 'size': 4},
                 {'address': 590860, 'size': 4},
                 {'address': 590864, 'size': 4},
                 {'address': 590868, 'size': 4},
                 {'address': 590872, 'size': 4},
                 {'address': 590876, 'size': 4},
                 {'address': 590880, 'size': 4},
                 {'address': 590884, 'size': 4},
                 {'address': 590888, 'size': 4},
                 {'address': 590892, 'size': 4},
                 {'address': 590896, 'size': 4},
                 {'address': 591268, 'size': 2},
                 {'address': 591270, 'size': 2},
                 {'address': 591584, 'size': 4},
                 {'address': 591588, 'size': 4},
                 {'address': 591592, 'size': 4},
                 {'address': 591596, 'size': 4}],
 'input_blobs': [],
 'control_blobs': [{'name': 'rom_855d', 'address': 34141, 'size': 1, 'stock_hex': '0a'},
                   {'name': 'rom_871f', 'address': 34591, 'size': 1, 'stock_hex': '0a'},
                   {'name': 'rom_8736', 'address': 34614, 'size': 1, 'stock_hex': '22'},
                   {'name': 'rom_8737', 'address': 34615, 'size': 1, 'stock_hex': '22'},
                   {'name': 'rom_8951', 'address': 35153, 'size': 1, 'stock_hex': '22'},
                   {'name': 'rom_8952', 'address': 35154, 'size': 1, 'stock_hex': '22'},
                   {'name': 'rom_8e1c', 'address': 36380, 'size': 1, 'stock_hex': '5a'},
                   {'name': 'rom_8e25', 'address': 36389, 'size': 1, 'stock_hex': '5a'}],
 'selected_actual_byte': {'address': 4294907579,
                          'width_bytes': 1,
                          'read_sites': [590604, 590762],
                          'source_base': 4294907578,
                          'actual_index': 1},
 'raw_RAM_byte_fields': [8999,
                         17347,
                         9387,
                         17346,
                         9386,
                         9304,
                         17143,
                         17163,
                         13721,
                         5819,
                         17345,
                         17335,
                         13707,
                         13698,
                         17333,
                         17327],
 'actual_publication_bytes': [13721, 13707, 13698, 17143, 17163, 17345, 17335, 17333, 17327],
 'reused_source_sha256': {'tools/sh-elf-run/stock_ignition_consumer_invoke.s': 'f0803224463944e2ecef86b1694e8802b01a5146a3fe706db39a4a1be9512809',
                          'tools/kb/src/kb/byte_surface_equations.py': '2c686f6ef380bf88a1635742b4cf6b25f3998b49a83e1f014baa698c3f5548cf',
                          'tools/kb/src/kb/packed_transfer_evidence.py': '7aa7f7e57a5b1a2db170e0b7003bf52bf42e96160fdfd92a7655764227bc866c',
                          'tools/kb/src/kb/test_stock_abi.py': 'e0fbc5f20b99e736449ba68afd5879915b432088922493bbcfc5da0bf318240c',
                          'tools/kb/src/kb/width_view_matrix.py': '087e0f9e3db4874db26841f3cf4c89ce38bc7a9df152e916b8313110e8142869',
                          'tools/kb/src/kb/ignition_literal_evidence.py': '39d2499d39ec80b6036ad96374d2962d37c4ae899a4fd0015dd34e5d5245becb',
                          'tools/kb/src/kb/test_contract.py': '10f4a6162e989ce8e4a31e50b6d4f9ec6838e7efa9528727924434321c064b6a',
                          'tools/kb/src/kb/test_stock_capture.py': '12192a4b275957e7d5894ad767b0c437ee3ff153c1e3b0b741051d2b05d05ebe'},
 'native_identity_admission': False,
 'native_geometry_inference': False,
 'scale_admission': False,
 'units_admission': False,
 'natural_caller_reachability': False,
 'natural_scheduling_inference': False,
 'hardware_qualification': False,
 'stock_function_stubs': False,
 'native_publication': False}
FUNCTIONS=(ENTRY,)
LITERAL_OPERANDS={590424: (590840, 4, 0),
 590440: (590856, 4, 6),
 590464: (590860, 4, 6),
 590478: (590864, 4, 4),
 590488: (590852, 4, 1),
 590494: (590686, 2, 0),
 590512: (590860, 4, 6),
 590530: (590868, 4, 6),
 590538: (590872, 4, 4),
 590548: (590852, 4, 1),
 590554: (590686, 2, 0),
 590578: (590852, 4, 1),
 590582: (590686, 2, 0),
 590590: (590876, 4, 3),
 590594: (590880, 4, 2),
 590600: (590688, 2, 6),
 590618: (590884, 4, 2),
 590648: (590690, 2, 0),
 590674: (590692, 2, 0),
 590696: (590888, 4, 1),
 590736: (590852, 4, 1),
 590740: (590834, 2, 0),
 590748: (590892, 4, 3),
 590752: (590880, 4, 2),
 590758: (590836, 2, 6),
 590776: (590896, 4, 6),
 590804: (590838, 2, 0),
 590900: (591268, 2, 0),
 590914: (591584, 4, 1),
 590944: (591588, 4, 1),
 590948: (591270, 2, 0),
 590954: (591592, 4, 4),
 590970: (591596, 4, 4),
 590982: (591584, 4, 1)}
IMAGE_SHA256=DECLARED['image_sha256']
UNIT=DECLARED['unit']
CONTROLLED_CALIBRATION=DECLARED['controlled_calibration']
BOUND_SPANS=DECLARED['bound_spans']
SPANS=tuple((row['start'],row['end']) for row in UNIT['code'])

def sha(raw):return hashlib.sha256(raw).hexdigest()

def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if not test_contract.exact(value,DECLARED):
        raise ValueError('the quantity source changes an exact phase, stock instruction, operand or observation premise')
    for name,wanted in value['reused_source_sha256'].items():
        if sha((Path(root)/name).read_bytes())!=wanted:
            raise ValueError('the quantity source changes a complete reused original source')
    return dict(value,entry=[dict(start=a,end=b) for a,b in SPANS])

def require_image(source,image):
    if type(image) is not bytes or sha(image)!=IMAGE_SHA256 or not test_contract.exact(source['unit'],UNIT):
        raise ValueError('the quantity fixture changes its complete owned image or exact reconstructed unit')
    for row in (*UNIT['pools'], *DECLARED['control_blobs']):
        at,size=row['address'],row['size']
        if image[at:at+size].hex()!=row['stock_hex']:
            raise ValueError('the quantity fixture changes an exact stock literal or raw control byte')

def independent_fixture(source,image):
    require_image(source,image);out=bytearray(image)
    for row in UNIT['aliases']:
        at=row['address']
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('the quantity fixture relocates a different native pointer')
        out[at:at+4]=row['alias'].to_bytes(4,'big')
    return bytes(out),[dict(row) for row in UNIT['aliases']]

def fixture_for_case(source,image,case):
    from kb import rest_position_judgement_matrix as matrix
    matrix.require_case(case);out,aliases=independent_fixture(source,image);out=bytearray(out)
    for at,raw in matrix.input_calibrations(case).items():out[at:at+len(raw)]=raw
    return bytes(out),aliases
