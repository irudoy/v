"""Exact complete timer writer, native85 control window and unchanged ordinary observer ABI."""
import hashlib
from pathlib import Path
import tomllib
from kb import test_contract
DESCRIPTOR='defs/JK08A.indexed-timer-refresh-writer-paths.toml'
DECLARED = {'schema': 1,
 'id': 'jk08a-indexed-timer-refresh-writer',
 'layout': '7mfk',
 'rom': 'JK08A',
 'image_sha256': 'ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23',
 'scope': 'Complete 9018C indexed timer-refresh writer, full zero/nonzero enable paths, exact native850C '
          'read/write and850D read, complete separate ordinary/native snapshots, SR interrupt masking, frame '
          'and natural return.',
 'entries': [590220],
 'observer': 'tools/sh-elf-run/stock_ignition_consumer_invoke.s',
 'context_bytes': 80,
 'frame_bytes': 192,
 'frame_prefix': 160,
 'unit': {'assembly': 'tools/sh-elf-run/stock_jk08a_indexed_timer_refresh_writer.s',
          'code': [{'start': 590220, 'end': 590416}],
          'pools': [{'address': 590416, 'size': 2, 'stock_hex': '0c89'},
                    {'address': 590418, 'size': 2, 'stock_hex': 'ff0f'},
                    {'address': 590420, 'size': 2, 'stock_hex': '850c'},
                    {'address': 590840, 'size': 4, 'stock_hex': 'ffff42d3'},
                    {'address': 590844, 'size': 4, 'stock_hex': '00008e23'},
                    {'address': 590848, 'size': 4, 'stock_hex': 'ffff4124'},
                    {'address': 590852, 'size': 4, 'stock_hex': 'ffff28f8'}],
          'aliases': [{'address': 590840, 'width': 4, 'original': 4294918867, 'alias': 16794323},
                      {'address': 590848, 'width': 4, 'original': 4294918436, 'alias': 16793892},
                      {'address': 590852, 'width': 4, 'original': 4294912248, 'alias': 16787704}]},
 'native_control_bytes': {'addresses': [4294935820, 4294935821],
                          'window_start': 4294935808,
                          'window_size': 256},
 'controlled_calibration': [{'address': 36387, 'size': 1},
                            {'address': 590416, 'size': 2},
                            {'address': 590418, 'size': 2},
                            {'address': 590420, 'size': 2},
                            {'address': 590840, 'size': 4},
                            {'address': 590844, 'size': 4},
                            {'address': 590848, 'size': 4},
                            {'address': 590852, 'size': 4}],
 'bound_spans': [{'address': 590220, 'size': 196},
                 {'address': 36387, 'size': 1},
                 {'address': 590416, 'size': 2},
                 {'address': 590418, 'size': 2},
                 {'address': 590420, 'size': 2},
                 {'address': 590840, 'size': 4},
                 {'address': 590844, 'size': 4},
                 {'address': 590848, 'size': 4},
                 {'address': 590852, 'size': 4}],
 'configuration': [{'address': 36387, 'size': 1, 'field': 'reload'}],
 'software_index_premise': {'first': 0, 'last': 255, 'additional': [4294967295]},
 'exact_owner_index': 6,
 'exact_owner_address': 4294919102,
 'native_identity_admission': False,
 'native_geometry_inference': False,
 'scale_admission': False,
 'units_admission': False,
 'natural_caller_reachability': False,
 'natural_scheduling_inference': False,
 'hardware_qualification': False,
 'stock_function_stubs': False,
 'native_publication': False}

ENTRY=0x9018C
ENTRIES=FUNCTIONS=(ENTRY,)
SPANS=((ENTRY,0x90250),)
UNIT=DECLARED['unit']
OBSERVER=DECLARED['observer']
CONTROLLED_CALIBRATION=DECLARED['controlled_calibration']
BOUND_SPANS=DECLARED['bound_spans']
CONFIGURATION=DECLARED['configuration']
IMAGE_SHA256=DECLARED['image_sha256']
CONTROL=DECLARED['native_control_bytes']
FLAGS=tuple(key for key,value in DECLARED.items() if value is False)
INDICES=(*range(256),0xFFFFFFFF)
STOCK_CODE_HEX='2fe64f13d09b401e7ffcd19b6743905974016e73021c662c26488f4b7e012558893ac455650c25488b1ec454620c22488b1a000240094009c90f6203000293422039cbf0400e25eb6053953dc0556050cb8025006023c90f4008400802022239220b420ea004000925eb6053952cc0558451600c40094009c90320488911d27be6e5666c6073326c062c26688b169019021c22eba0120124c45562e72f022029c055d272e6e5d572666c326c60736650a0040264c45562e72029c0557f044f17000b6ef6'

def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if not test_contract.exact(value,DECLARED):
        raise ValueError('the timer writer changes its exact whole image, native window, full function, type premise or complete ABI')
    return dict(value,entry=[dict(start=first,end=last) for first,last in SPANS])

def require_image(source,image):
    if (type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256
            or not test_contract.exact(source['unit'],UNIT) or image[ENTRY:0x90250].hex()!=STOCK_CODE_HEX):
        raise ValueError('the timer writer changes its complete owned image or full stock instruction bytes')
    for row in UNIT['pools']:
        if image[row['address']:row['address']+row['size']].hex()!=row['stock_hex']:
            raise ValueError('the timer writer changes an exact stock PC literal or native850C displacement')

def independent_fixture(source,image):
    require_image(source,image);fixture=bytearray(image);aliases=[]
    for row in UNIT['aliases']:
        at=row['address']
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('the timer writer relocates another exact native base')
        fixture[at:at+4]=row['alias'].to_bytes(4,'big');aliases.append(dict(row))
    return bytes(fixture),aliases

def fixture_for_case(source,image,case):
    from kb import indexed_timer_refresh_writer_matrix as matrix
    matrix.require_case(case);fixture,aliases=independent_fixture(source,image);fixture=bytearray(fixture)
    fixture[0x8E23]=case['reload']
    return bytes(fixture),aliases
