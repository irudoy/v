"""Exact complete natural endpoint-normalizer and selected whole-datum absence source."""
import hashlib
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.endpoint-normalizer-writer-withdrawal-paths.toml'
ENTRY=0x7AF78
ENTRIES=(ENTRY,)
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
DECLARED={'schema': 1,
 'id': 'jk08a-endpoint-normalizer-writer-withdrawal',
 'layout': '7mfk',
 'rom': 'JK08A',
 'image_sha256': 'ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23',
 'scope': 'Complete natural endpoint normalizer and every actual helper; exact whole-datum41FB absence '
          'preserves the full coordinator and all transitive dependencies.',
 'entries': [503672],
 'observer': 'tools/sh-elf-run/stock_ignition_consumer_invoke.s',
 'context_bytes': 80,
 'frame_bytes': 192,
 'frame_prefix': 160,
 'unit': {'assembly': 'tools/sh-elf-run/stock_jk08a_endpoint_normalizer_writer_withdrawal.s',
          'code': [{'start': 138172, 'end': 138454},
                   {'start': 156920, 'end': 156954},
                   {'start': 157504, 'end': 157550},
                   {'start': 158084, 'end': 158144},
                   {'start': 158840, 'end': 158990},
                   {'start': 503672, 'end': 503892}],
          'pools': [{'address': 138456, 'size': 4, 'stock_hex': 'ffff9818'},
                    {'address': 138460, 'size': 4, 'stock_hex': '0000044e'},
                    {'address': 156956, 'size': 4, 'stock_hex': '00026740'},
                    {'address': 156960, 'size': 4, 'stock_hex': '00026984'},
                    {'address': 158144, 'size': 4, 'stock_hex': '00026c78'},
                    {'address': 503892, 'size': 2, 'stock_hex': '0a94'},
                    {'address': 503894, 'size': 2, 'stock_hex': '0a96'},
                    {'address': 503896, 'size': 2, 'stock_hex': '0a9e'},
                    {'address': 503898, 'size': 2, 'stock_hex': '0320'},
                    {'address': 503900, 'size': 2, 'stock_hex': '0b80'},
                    {'address': 503902, 'size': 2, 'stock_hex': '0b82'},
                    {'address': 503904, 'size': 2, 'stock_hex': '0b84'},
                    {'address': 503908, 'size': 4, 'stock_hex': 'ffff28f8'},
                    {'address': 503940, 'size': 4, 'stock_hex': 'ffff1114'},
                    {'address': 503944, 'size': 4, 'stock_hex': '000154e0'},
                    {'address': 503948, 'size': 4, 'stock_hex': '00014baa'},
                    {'address': 503952, 'size': 4, 'stock_hex': '000264f8'},
                    {'address': 503956, 'size': 4, 'stock_hex': '000154c0'},
                    {'address': 503960, 'size': 4, 'stock_hex': '00008000'},
                    {'address': 503964, 'size': 4, 'stock_hex': '00021bbc'}],
          'aliases': [{'address': 138456, 'width': 4, 'original': 4294940696, 'alias': 16816152},
                      {'address': 503908, 'width': 4, 'original': 4294912248, 'alias': 16787704},
                      {'address': 503940, 'width': 4, 'original': 4294906132, 'alias': 16781588}]},
 'controlled_calibration': [{'address': 84906, 'size': 32},
                            {'address': 87232, 'size': 32},
                            {'address': 87264, 'size': 32},
                            {'address': 87296, 'size': 2},
                            {'address': 138456, 'size': 4},
                            {'address': 138460, 'size': 4},
                            {'address': 156956, 'size': 4},
                            {'address': 156960, 'size': 4},
                            {'address': 158144, 'size': 4},
                            {'address': 503892, 'size': 2},
                            {'address': 503894, 'size': 2},
                            {'address': 503896, 'size': 2},
                            {'address': 503898, 'size': 2},
                            {'address': 503900, 'size': 2},
                            {'address': 503902, 'size': 2},
                            {'address': 503904, 'size': 2},
                            {'address': 503908, 'size': 4},
                            {'address': 503940, 'size': 4},
                            {'address': 503944, 'size': 4},
                            {'address': 503948, 'size': 4},
                            {'address': 503952, 'size': 4},
                            {'address': 503956, 'size': 4},
                            {'address': 503960, 'size': 4},
                            {'address': 503964, 'size': 4}],
 'bound_spans': [{'address': 138172, 'size': 282},
                 {'address': 156920, 'size': 34},
                 {'address': 157504, 'size': 46},
                 {'address': 158084, 'size': 60},
                 {'address': 158840, 'size': 150},
                 {'address': 503672, 'size': 220},
                 {'address': 84906, 'size': 32},
                 {'address': 87232, 'size': 32},
                 {'address': 87264, 'size': 32},
                 {'address': 87296, 'size': 2},
                 {'address': 138456, 'size': 4},
                 {'address': 138460, 'size': 4},
                 {'address': 156956, 'size': 4},
                 {'address': 156960, 'size': 4},
                 {'address': 158144, 'size': 4},
                 {'address': 503892, 'size': 2},
                 {'address': 503894, 'size': 2},
                 {'address': 503896, 'size': 2},
                 {'address': 503898, 'size': 2},
                 {'address': 503900, 'size': 2},
                 {'address': 503902, 'size': 2},
                 {'address': 503904, 'size': 2},
                 {'address': 503908, 'size': 4},
                 {'address': 503940, 'size': 4},
                 {'address': 503944, 'size': 4},
                 {'address': 503948, 'size': 4},
                 {'address': 503952, 'size': 4},
                 {'address': 503956, 'size': 4},
                 {'address': 503960, 'size': 4},
                 {'address': 503964, 'size': 4}],
 'input_blobs': [{'name': 'upper', 'address': 87232, 'size': 32},
                 {'name': 'lower', 'address': 87264, 'size': 32},
                 {'name': 'axis', 'address': 84906, 'size': 32}],
 'control_blobs': [{'name': 'lower_guard', 'address': 87296, 'size': 2, 'stock_hex': '0000'}],
 'selected': {'original_claim_sha256': '00a6bea0c6225c361de23d2c59fae3eefd394cf866ab46b88e02e93c40ff8c1c',
              'owner': 'fluffy-salamander/ram',
              'function': 'aromatic-coua/fn',
              'address': 4294918651,
              'width_bytes': 1,
              'semantic_width': 'unset',
              'semantic_signed': 'unset',
              'whole_datum_absence_required': True,
              'existing_family': 'scalar-ram-leaf-withdrawal',
              'native_identity_admission': False},
 'actual_outputs': [{'address': 4294915192, 'width_bytes': 2},
                    {'address': 4294915194, 'width_bytes': 2},
                    {'address': 4294915196, 'width_bytes': 2}],
 'full_existing_same_primary_originals': ['request_limit_normalization_paths', 'timing_denominator'],
 'reused_source_sha256': {'defs/JK08A.timing-denominator.toml': '407f42035990e98f84b513394d3fe0c8728e5742bb776d98e13f8adf9ee93e33',
                          'tools/sh-elf-run/stock_jk08a_timing_denominator.s': '616bc7c9a1f0b269183cc2ac096ba46626966830285c017dbdeb2eeffb1b1e1c',
                          'tools/sh-elf-run/stock_ignition_consumer_invoke.s': 'f0803224463944e2ecef86b1694e8802b01a5146a3fe706db39a4a1be9512809',
                          'tools/kb/src/kb/byte_surface_equations.py': 'b7a72d1ce7dde1bd247db201c9458d7666c368c6eac903443a7b9e45077ee286',
                          'tools/kb/src/kb/packed_transfer_evidence.py': '7aa7f7e57a5b1a2db170e0b7003bf52bf42e96160fdfd92a7655764227bc866c',
                          'tools/kb/src/kb/test_stock_abi.py': 'e0fbc5f20b99e736449ba68afd5879915b432088922493bbcfc5da0bf318240c',
                          'tools/kb/src/kb/width_view_matrix.py': '087e0f9e3db4874db26841f3cf4c89ce38bc7a9df152e916b8313110e8142869',
                          'tools/kb/src/kb/timing_denominator_contract.py': '7b58c1255b8851db8f53f5c8f45a4c56000db4fc6717d902a0724dabf0e19ef3',
                          'tools/kb/src/kb/timing_denominator_matrix.py': '9c0c1a00db24333f996a86dced884c3b1755773334bd34efcfe932068ef59c9e',
                          'tools/kb/src/kb/timing_denominator_semantics.py': 'b8401b6bc3e6bd8e6a230c9b40e696afa31d3581801be7570e8a0f56ae8d9516',
                          'tools/kb/src/kb/timing_denominator_capture_evidence.py': '7ea0b371eaa05063d144bc3a8f386b7e64915917ec3b4848b56d2ebef5cfbfe6',
                          'defs/JK08A.request-limit-normalization-paths.toml': 'cf79e62d0dd7c20d438e92db2ebc2a919f2ca4a1952a37d6b626917d34029705',
                          'defs/JK08A.request-limit-normalization-claims.toml': '3a87c42814920464779c2387f92339de7b1ada1b24909bd4142dd5e2183a6385',
                          'defs/JK08A.request-limit-normalization.md': 'b7ebd97998cd13efe723c88da8a01df2c2ae17dbc38c22c4ab439ba4e1cad33a',
                          'tools/sh-elf-run/stock_jk08a_request_limit_normalization.s': 'ef4a4fcd00d6bb4d3507bc75ad37e92a61b5c1cf816e94f7a7677471d830ac21',
                          'tools/sh-elf-run/harness-request-limit-normalization-paths.c': '129bd92c510bcfa54e6b6acf7f2ec4a0d0ea1402a1aaac0fe8c3449ae6502c0c',
                          'tools/sh-elf-run/request_limit_normalization_capture.py': 'aa66cb7150cb45df8fc2549359e7ade399862a7ae90310b689b76304822dff0f',
                          'tools/kb/src/kb/request_limit_normalization_contract.py': '3c3724ceada6cc8cb08ff2f7b2d537e3b2811ee9672cdb281a37bab3f1aec0bd',
                          'tools/kb/src/kb/request_limit_normalization_matrix.py': 'ce595f44f24b4903e2bb3559ed105b145435cb8985496ae951d98674abf14b39',
                          'tools/kb/src/kb/request_limit_normalization_semantics.py': '653c39cd6c60bebe00e9687cbd35f9ff8eceb44a83abfe1866a4c374347c7337',
                          'tools/kb/src/kb/request_limit_normalization_transfers.py': 'ad324b2d11959849889a4180ca463f87d499becb5298ba25b3af13fd2df56ccc',
                          'tools/kb/src/kb/request_limit_normalization_capture_evidence.py': '4e26a80b3d78955152430cc890849d8000cc63be69606e0677a004aa42e2a921',
                          'tools/kb/src/kb/request_limit_normalization_access_contract.py': 'b38e3788e25d84664f6ed20f6a8674c6e7f430ee6bb217ebe80e657d1e0f6db1',
                          'tools/kb/src/kb/request_limit_normalization_access_evidence.py': 'd01813dc682b9f230f9b8b34e5503cb5f8e524dc52a7aad9ba5d4f599aa368de',
                          'tools/kb/src/kb/request_limit_normalization_access_resolution.py': '103a0858dc422c04e1f7e282543d793fe6557ec33a1395b793fd49910901fc20',
                          'tools/kb/tests/test_request_limit_normalization_contract.py': 'e1fd53f849021b0b92f58bcb0373ceb3e91a866cb694f8d6946d739c19877100',
                          'tools/kb/tests/test_request_limit_normalization_capture_evidence.py': '648121034198544ff1de26cb1484918df74695a57f55176ffde706af0cb5b7ec',
                          'tools/kb/tests/test_request_limit_normalization_access.py': '098db513e0ec36993e6209f5f46901c099e7540ceda38dfbf859028dc4aa7aca'},
 'native_identity_admission': False,
 'native_geometry_inference': False,
 'scale_admission': False,
 'units_admission': False,
 'natural_caller_reachability': False,
 'natural_scheduling_inference': False,
 'hardware_qualification': False,
 'stock_function_stubs': False,
 'native_publication': False}
FUNCTIONS=(138172, 156920, 157504, 158084, 158840, 503672)
LITERAL_OPERANDS={138352: (138456, 4, 1),
 138354: (138460, 4, 2),
 156928: (156960, 4, 7),
 156948: (156956, 4, 6),
 158118: (158144, 4, 2),
 503688: (503940, 4, 13),
 503692: (503944, 4, 4),
 503696: (503948, 4, 14),
 503698: (503952, 4, 2),
 503702: (503908, 4, 10),
 503716: (503956, 4, 4),
 503718: (503952, 4, 2),
 503720: (503960, 4, 14),
 503728: (503892, 2, 0),
 503746: (503894, 2, 0),
 503762: (503896, 2, 0),
 503794: (503898, 2, 13),
 503798: (503964, 4, 6),
 503816: (503900, 2, 0),
 503818: (503964, 4, 6),
 503838: (503902, 2, 0),
 503840: (503964, 4, 6),
 503860: (503898, 2, 2),
 503862: (503900, 2, 0),
 503866: (503902, 2, 0),
 503870: (503904, 2, 0)}
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
    from kb import endpoint_normalizer_writer_withdrawal_matrix as matrix
    matrix.require_case(case);out,aliases=independent_fixture(source,image);out=bytearray(out)
    for at,raw in matrix.input_calibrations(case).items():out[at:at+len(raw)]=raw
    return bytes(out),aliases
