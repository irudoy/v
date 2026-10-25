"""Complete natural BFS-dependent state caller and retained quantity dependencies."""
import hashlib
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.bfs-state-caller-withdrawal-paths.toml'
ENTRY=0x3A750
ENTRIES=(ENTRY,)
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
DECLARED={'schema': 1,
 'id': 'jk08a-bfs-state-caller-withdrawal',
 'layout': '7mfk',
 'rom': 'JK08A',
 'image_sha256': 'ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23',
 'scope': 'Complete natural3A750 state caller and real byte-curve/predicate helpers; direct table15630 '
          'interval absence preserves independently stated BFS quantities and producer dependencies.',
 'entries': [239440],
 'observer': 'tools/sh-elf-run/stock_ignition_consumer_invoke.s',
 'context_bytes': 80,
 'observation_bytes': 572,
 'frame_bytes': 192,
 'frame_prefix': 160,
 'root_stack_bytes': 16,
 'unit': {'assembly': 'tools/sh-elf-run/stock_jk08a_bfs_state_caller_withdrawal.s',
          'code': [{'start': 155168, 'end': 155204},
                   {'start': 156528, 'end': 156546},
                   {'start': 157504, 'end': 157550},
                   {'start': 158304, 'end': 158394},
                   {'start': 239440, 'end': 239728},
                   {'start': 239730, 'end': 239822}],
          'pools': [{'address': 155408, 'size': 4, 'stock_hex': 'ffff5718'},
                    {'address': 156546, 'size': 2, 'stock_hex': '00e0'},
                    {'address': 156548, 'size': 4, 'stock_hex': '00026a80'},
                    {'address': 158396, 'size': 4, 'stock_hex': '00026740'},
                    {'address': 239728, 'size': 2, 'stock_hex': '0129'},
                    {'address': 239824, 'size': 4, 'stock_hex': 'ffff39c4'},
                    {'address': 239828, 'size': 4, 'stock_hex': 'ffff2458'},
                    {'address': 239832, 'size': 4, 'stock_hex': 'ffff1072'},
                    {'address': 239836, 'size': 4, 'stock_hex': '00012a3a'},
                    {'address': 239840, 'size': 4, 'stock_hex': '00026370'},
                    {'address': 239844, 'size': 4, 'stock_hex': 'ffff1e60'},
                    {'address': 239848, 'size': 4, 'stock_hex': 'ffff24f9'},
                    {'address': 239852, 'size': 4, 'stock_hex': 'ffff24b0'},
                    {'address': 239856, 'size': 4, 'stock_hex': '0000875c'},
                    {'address': 239860, 'size': 4, 'stock_hex': '00025e20'},
                    {'address': 239864, 'size': 4, 'stock_hex': '00008ad9'},
                    {'address': 239868, 'size': 4, 'stock_hex': 'ffff1024'},
                    {'address': 239872, 'size': 4, 'stock_hex': 'ffff1048'}],
          'aliases': [{'address': 155408, 'width': 4, 'original': 4294924056, 'alias': 16799512},
                      {'address': 239824, 'width': 4, 'original': 4294916548, 'alias': 16792004},
                      {'address': 239828, 'width': 4, 'original': 4294911064, 'alias': 16786520},
                      {'address': 239832, 'width': 4, 'original': 4294905970, 'alias': 16781426},
                      {'address': 239844, 'width': 4, 'original': 4294909536, 'alias': 16784992},
                      {'address': 239848, 'width': 4, 'original': 4294911225, 'alias': 16786681},
                      {'address': 239852, 'width': 4, 'original': 4294911152, 'alias': 16786608},
                      {'address': 239868, 'width': 4, 'original': 4294905892, 'alias': 16781348},
                      {'address': 239872, 'width': 4, 'original': 4294905928, 'alias': 16781384}]},
 'controlled_calibration': [{'address': 34652, 'size': 1},
                            {'address': 35545, 'size': 1},
                            {'address': 76346, 'size': 8},
                            {'address': 155408, 'size': 4},
                            {'address': 156546, 'size': 2},
                            {'address': 156548, 'size': 4},
                            {'address': 158396, 'size': 4},
                            {'address': 239728, 'size': 2},
                            {'address': 239824, 'size': 4},
                            {'address': 239828, 'size': 4},
                            {'address': 239832, 'size': 4},
                            {'address': 239836, 'size': 4},
                            {'address': 239840, 'size': 4},
                            {'address': 239844, 'size': 4},
                            {'address': 239848, 'size': 4},
                            {'address': 239852, 'size': 4},
                            {'address': 239856, 'size': 4},
                            {'address': 239860, 'size': 4},
                            {'address': 239864, 'size': 4},
                            {'address': 239868, 'size': 4},
                            {'address': 239872, 'size': 4}],
 'bound_spans': [{'address': 155168, 'size': 36},
                 {'address': 156528, 'size': 18},
                 {'address': 157504, 'size': 46},
                 {'address': 158304, 'size': 90},
                 {'address': 239440, 'size': 288},
                 {'address': 239730, 'size': 92},
                 {'address': 34652, 'size': 1},
                 {'address': 35545, 'size': 1},
                 {'address': 76346, 'size': 8},
                 {'address': 155408, 'size': 4},
                 {'address': 156546, 'size': 2},
                 {'address': 156548, 'size': 4},
                 {'address': 158396, 'size': 4},
                 {'address': 239728, 'size': 2},
                 {'address': 239824, 'size': 4},
                 {'address': 239828, 'size': 4},
                 {'address': 239832, 'size': 4},
                 {'address': 239836, 'size': 4},
                 {'address': 239840, 'size': 4},
                 {'address': 239844, 'size': 4},
                 {'address': 239848, 'size': 4},
                 {'address': 239852, 'size': 4},
                 {'address': 239856, 'size': 4},
                 {'address': 239860, 'size': 4},
                 {'address': 239864, 'size': 4},
                 {'address': 239868, 'size': 4},
                 {'address': 239872, 'size': 4},
                 {'address': 87600, 'size': 16}],
 'input_blobs': [{'name': 'implicit_curve', 'address': 76346, 'size': 8}],
 'control_blobs': [{'name': 'rom_875c', 'address': 34652, 'size': 1, 'stock_hex': '00'},
                   {'name': 'rom_8ad9', 'address': 35545, 'size': 1, 'stock_hex': '20'}],
 'selected': {'original_claim_sha256': '1230d77f4ca1f795e40de5ad2bc862d25cfe1480a08b583f103b3b50b57fa3d1',
              'owner': 'nice-coucal/tbl',
              'function': 'ultramarine-taipan/fn',
              'address': 87600,
              'physical_interval_bytes': 16,
              'semantic_width': 'unset',
              'semantic_signed': 'unset',
              'whole_interval_all_direction_overlap_absence_required': True,
              'existing_family': 'scalar-ram-leaf-withdrawal',
              'native_identity_admission': False},
 'actual_curve': {'address': 76346, 'active_bytes': 8, 'coordinate': 4294905975, 'publication': 4294909816},
 'preserved_quantity_reads': [4294905954, 4294905894],
 'preserved_function_dependency': 'tall-quoll/ram',
 'full_existing_same_primary_originals': ['byte_factor_caller_withdrawal_paths'],
 'reused_source_sha256': {'tools/sh-elf-run/stock_ignition_consumer_invoke.s': 'f0803224463944e2ecef86b1694e8802b01a5146a3fe706db39a4a1be9512809',
                          'tools/kb/src/kb/byte_surface_equations.py': '03ee71a837ede086fae867e10eda2eba5c549eb2ee05e329c23082d0ef0a28be',
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
 'native_publication': False,
 'stock_entry_paths': [155168, 156528, 157504, 158336, 239440]}
FUNCTIONS=(0x25E20,0x26370,0x26740,0x26A60,0x3A750)
LITERAL_OPERANDS={155168: (155408, 4, 1),
 156528: (156546, 2, 0),
 156536: (156548, 4, 6),
 158388: (158396, 4, 6),
 239444: (239824, 4, 0),
 239458: (239828, 4, 6),
 239466: (239832, 4, 7),
 239468: (239836, 4, 4),
 239472: (239840, 4, 2),
 239480: (239844, 4, 6),
 239484: (239848, 4, 5),
 239502: (239828, 4, 6),
 239510: (239848, 4, 5),
 239530: (239828, 4, 6),
 239548: (239832, 4, 7),
 239550: (239852, 4, 6),
 239564: (239856, 4, 6),
 239574: (239852, 4, 6),
 239582: (239852, 4, 6),
 239598: (239828, 4, 6),
 239612: (239852, 4, 6),
 239620: (239828, 4, 6),
 239628: (239860, 4, 2),
 239630: (239728, 2, 4),
 239640: (239864, 4, 2),
 239642: (239852, 4, 6),
 239658: (239868, 4, 3),
 239662: (239872, 4, 1),
 239696: (239872, 4, 3),
 239700: (239868, 4, 1),
 239730: (239868, 4, 3),
 239740: (239872, 4, 3),
 239768: (239828, 4, 6),
 239786: (239828, 4, 6),
 239788: (239828, 4, 5),
 239802: (239828, 4, 6),
 239804: (239828, 4, 5)}
IMAGE_SHA256=DECLARED['image_sha256']
UNIT=DECLARED['unit']
CONTROLLED_CALIBRATION=DECLARED['controlled_calibration']
BOUND_SPANS=DECLARED['bound_spans']
SPANS=tuple((row['start'],row['end']) for row in UNIT['code'])
CONFIGURATION=tuple(dict(address=row['address'],size=row['size'],field=row['name']) for row in DECLARED['control_blobs'])
INPUT_BLOBS=DECLARED['input_blobs']

def sha(raw):return hashlib.sha256(raw).hexdigest()

def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if not test_contract.exact(value,DECLARED):
        raise ValueError('the BFS state caller changes an exact complete natural path, table interval or retained dependency')
    for path,wanted in value['reused_source_sha256'].items():
        if sha((Path(root)/path).read_bytes())!=wanted:
            raise ValueError('the BFS state caller changes a complete reused source')
    return dict(value,entry=[dict(start=a,end=b) for a,b in SPANS])

def require_image(source,image):
    if type(image) is not bytes or sha(image)!=IMAGE_SHA256 or not test_contract.exact(source['unit'],UNIT):
        raise ValueError('the BFS state caller changes its exact owned image or full reconstructed unit')
    for row in (*UNIT['pools'],*DECLARED['control_blobs']):
        at,size=row['address'],row['size']
        if image[at:at+size].hex()!=row['stock_hex']:
            raise ValueError('the BFS state caller changes a stock literal or raw ROM control')

def independent_fixture(source,image):
    require_image(source,image);out=bytearray(image)
    for row in UNIT['aliases']:
        at=row['address']
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('the BFS state caller relocates another native pointer')
        out[at:at+4]=row['alias'].to_bytes(4,'big')
    return bytes(out),[dict(row) for row in UNIT['aliases']]

def fixture_for_case(source,image,case):
    from kb import bfs_state_caller_withdrawal_matrix as matrix
    matrix.require_case(case);out,aliases=independent_fixture(source,image);out=bytearray(out)
    for at,raw in matrix.input_calibrations(case).items():out[at:at+len(raw)]=raw
    return bytes(out),aliases
