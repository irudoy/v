"""Exact natural gated accumulator, native control window and complete source boundary."""
import hashlib
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.shifted-word-accumulator-withdrawal-paths.toml'
ENTRY=0xA5398
ENTRIES=FUNCTIONS=(ENTRY,)
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
DECLARED={'schema': 1,
 'id': 'jk08a-shifted-word-accumulator-withdrawal',
 'layout': '7mfk',
 'rom': 'JK08A',
 'image_sha256': 'ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23',
 'scope': 'Complete natural A5398 gated shifted-word accumulator; exact direct absence of both existing '
          'surface roots preserves derived input and diagnostic dependencies.',
 'entries': [676760],
 'observer': 'tools/sh-elf-run/stock_ignition_consumer_invoke.s',
 'context_bytes': 80,
 'frame_bytes': 192,
 'frame_prefix': 160,
 'unit': {'assembly': 'tools/sh-elf-run/stock_jk08a_shifted_word_accumulator_withdrawal.s',
          'code': [{'start': 676760, 'end': 676924}],
          'pools': [{'address': 677056, 'size': 2, 'stock_hex': '84c3'},
                    {'address': 677058, 'size': 2, 'stock_hex': '0a92'},
                    {'address': 677060, 'size': 2, 'stock_hex': '0a3c'},
                    {'address': 677072, 'size': 4, 'stock_hex': 'ffff28f8'},
                    {'address': 677112, 'size': 4, 'stock_hex': 'ffff244f'},
                    {'address': 677116, 'size': 4, 'stock_hex': '00008cba'},
                    {'address': 677120, 'size': 4, 'stock_hex': 'ffff102c'},
                    {'address': 677124, 'size': 4, 'stock_hex': '000083ec'},
                    {'address': 677128, 'size': 4, 'stock_hex': '00008a0d'},
                    {'address': 677132, 'size': 4, 'stock_hex': '00ffffff'}],
          'aliases': [{'address': 677072, 'width': 4, 'original': 4294912248, 'alias': 16787704},
                      {'address': 677112, 'width': 4, 'original': 4294911055, 'alias': 16786511},
                      {'address': 677120, 'width': 4, 'original': 4294905900, 'alias': 16781356}]},
 'native_control_bytes': {'addresses': [4294935747], 'window_start': 4294935552, 'window_size': 256},
 'controlled_calibration': [{'address': 33772, 'size': 1},
                            {'address': 35341, 'size': 1},
                            {'address': 36026, 'size': 1},
                            {'address': 677056, 'size': 2},
                            {'address': 677058, 'size': 2},
                            {'address': 677060, 'size': 2},
                            {'address': 677072, 'size': 4},
                            {'address': 677112, 'size': 4},
                            {'address': 677116, 'size': 4},
                            {'address': 677120, 'size': 4},
                            {'address': 677124, 'size': 4},
                            {'address': 677128, 'size': 4},
                            {'address': 677132, 'size': 4}],
 'bound_spans': [{'address': 676760, 'size': 164},
                 {'address': 33772, 'size': 1},
                 {'address': 35341, 'size': 1},
                 {'address': 36026, 'size': 1},
                 {'address': 677056, 'size': 2},
                 {'address': 677058, 'size': 2},
                 {'address': 677060, 'size': 2},
                 {'address': 677072, 'size': 4},
                 {'address': 677112, 'size': 4},
                 {'address': 677116, 'size': 4},
                 {'address': 677120, 'size': 4},
                 {'address': 677124, 'size': 4},
                 {'address': 677128, 'size': 4},
                 {'address': 677132, 'size': 4}],
 'configuration': [{'address': 33772, 'size': 1, 'field': 'factor'},
                   {'address': 35341, 'size': 1, 'field': 'shift'},
                   {'address': 36026, 'size': 1, 'field': 'threshold'}],
 'selected': [{'address': 43962,
               'owner': 'tuscan-porcupine/tbl',
               'original_claim_sha256': 'ce9e49e046ca8e2232523b5f62ded6df74bfaa2cb36c02e0ae227a33a08da481',
               'declared_width': 'unset',
               'declared_signed': 'unset',
               'extent_inference': False},
              {'address': 44026,
               'owner': 'soft-pronghorn/tbl',
               'original_claim_sha256': '796fc620c738208462ca3357504acb3021beeeb9d6396bc562ed31060594b78f',
               'declared_width': 'unset',
               'declared_signed': 'unset',
               'extent_inference': False}],
 'native_identity_admission': False,
 'native_geometry_inference': False,
 'scale_admission': False,
 'units_admission': False,
 'natural_caller_reachability': False,
 'natural_scheduling_inference': False,
 'hardware_qualification': False,
 'stock_function_stubs': False,
 'native_publication': False}
UNIT=DECLARED['unit']
SPANS=tuple((row['start'],row['end']) for row in UNIT['code'])
CONTROLLED_CALIBRATION=DECLARED['controlled_calibration']
BOUND_SPANS=DECLARED['bound_spans']
IMAGE_SHA256=DECLARED['image_sha256']


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if not test_contract.exact(value,DECLARED):
        raise ValueError('the shifted word accumulator changes its complete exact natural source or admission boundary')
    return dict(value,entry=[dict(start=a,end=b) for a,b in SPANS])


def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the shifted word accumulator changes its complete owned stock image')
    for row in UNIT['pools']:
        if image[row['address']:row['address']+row['size']].hex()!=row['stock_hex']:
            raise ValueError('the shifted word accumulator changes an exact stock pool')
    if not test_contract.exact(declared['unit'],UNIT):
        raise ValueError('the shifted word accumulator changes the instruction or literal reconstruction boundary')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image)
    for row in UNIT['aliases']:
        at=row['address']
        if image[at:at+4]!=row['original'].to_bytes(4,'big'):
            raise ValueError('the shifted word accumulator substitutes a native pointer alias')
        fixture[at:at+4]=row['alias'].to_bytes(4,'big')
    return bytes(fixture),[dict(row) for row in UNIT['aliases']]


def fixture_for_case(declared,image,case):
    from kb import shifted_word_accumulator_withdrawal_matrix as matrix
    matrix.require_case(case);fixture,aliases=independent_fixture(declared,image);fixture=bytearray(fixture)
    for row in DECLARED['configuration']:
        fixture[row['address']]=case[row['field']]
    return bytes(fixture),aliases
