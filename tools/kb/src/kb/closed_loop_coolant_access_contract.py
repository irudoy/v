"""Exact existing whole-coolant stock closure, ordinary aliases and observer ABI."""

import hashlib
import json
from pathlib import Path
import tomllib

from kb import test_contract

DESCRIPTOR='defs/JK08A.closed-loop-coolant-accesses.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
ENTRY=0x5525A
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
FUNCTIONS=(0x5525A,0x26370,0x26A80,0x26740,0x22590)
UNIT = {'assembly': 'tools/sh-elf-run/stock_jk08a_coolant_conditional.s',
 'code': [{'start': 348762, 'end': 348916},
          {'start': 348928, 'end': 348988},
          {'start': 349060, 'end': 349358},
          {'start': 156528, 'end': 156546},
          {'start': 158336, 'end': 158394},
          {'start': 157504, 'end': 157550},
          {'start': 140688, 'end': 140698}],
 'pools': [{'address': 34539, 'size': 1, 'stock_hex': '03'},
           {'address': 34725, 'size': 3, 'stock_hex': '909696'},
           {'address': 37008, 'size': 2, 'stock_hex': '0005'},
           {'address': 37530, 'size': 2, 'stock_hex': '1e77'},
           {'address': 39178, 'size': 16, 'stock_hex': '00000080000000800000808000808080'},
           {'address': 72471, 'size': 4, 'stock_hex': '18485068'},
           {'address': 72475, 'size': 4, 'stock_hex': '40465266'},
           {'address': 74786, 'size': 8, 'stock_hex': '00000004070a0d10'},
           {'address': 156546, 'size': 2, 'stock_hex': '00e0'},
           {'address': 156548, 'size': 4, 'stock_hex': '00026a80'},
           {'address': 158396, 'size': 4, 'stock_hex': '00026740'},
           {'address': 348988, 'size': 2, 'stock_hex': 'ff40'},
           {'address': 349008, 'size': 4, 'stock_hex': 'ffff119c'},
           {'address': 349040, 'size': 4, 'stock_hex': 'ffff2458'},
           {'address': 349044, 'size': 4, 'stock_hex': '000087a5'},
           {'address': 349048, 'size': 4, 'stock_hex': 'ffff1094'},
           {'address': 349052, 'size': 4, 'stock_hex': '000086eb'},
           {'address': 349056, 'size': 4, 'stock_hex': 'ffff1068'},
           {'address': 349424, 'size': 2, 'stock_hex': '0351'},
           {'address': 349426, 'size': 2, 'stock_hex': '0350'},
           {'address': 349428, 'size': 2, 'stock_hex': '034e'},
           {'address': 349632, 'size': 4, 'stock_hex': '00012422'},
           {'address': 349636, 'size': 4, 'stock_hex': '00026370'},
           {'address': 349640, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 349644, 'size': 4, 'stock_hex': 'ffff102c'},
           {'address': 349648, 'size': 4, 'stock_hex': '00011b1b'},
           {'address': 349652, 'size': 4, 'stock_hex': '00011b17'},
           {'address': 349656, 'size': 4, 'stock_hex': '0000990a'},
           {'address': 349660, 'size': 4, 'stock_hex': '00022590'},
           {'address': 349664, 'size': 4, 'stock_hex': '00009090'},
           {'address': 349668, 'size': 4, 'stock_hex': '0000929a'},
           {'address': 349672, 'size': 4, 'stock_hex': 'ffff22dc'}],
 'aliases': [{'address': 349008, 'width': 4, 'original': 4294906268, 'alias': 16781724},
             {'address': 349040, 'width': 4, 'original': 4294911064, 'alias': 16786520},
             {'address': 349048, 'width': 4, 'original': 4294906004, 'alias': 16781460},
             {'address': 349056, 'width': 4, 'original': 4294905960, 'alias': 16781416},
             {'address': 349640, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 349644, 'width': 4, 'original': 4294905900, 'alias': 16781356},
             {'address': 349672, 'width': 4, 'original': 4294910684, 'alias': 16786140}]}
CONTROLLED_CALIBRATION = [{'address': 34725, 'size': 3},
 {'address': 34539, 'size': 1},
 {'address': 74786, 'size': 8},
 {'address': 72475, 'size': 4},
 {'address': 72471, 'size': 4},
 {'address': 39178, 'size': 16},
 {'address': 37008, 'size': 2},
 {'address': 37530, 'size': 2},
 {'address': 348988, 'size': 2}]
ADAPTER_SHA256='11a76ca2339be10dce72aa62243545d1bf8de8d83a2657aba438f523e706bd9d'
FLAGS = ('stock_function_stubs', 'semantic_admission', 'automatic_resolution', 'native_geometry_inference', 'scale_admission', 'units_admission', 'natural_caller_reachability', 'hardware_qualification')

SPANS=tuple((row['start'],row['end']) for row in UNIT['code'])
BOUND_SPANS=tuple([dict(address=first,size=last-first) for first,last in SPANS]+
    [dict(address=row['address'],size=row['size']) for row in UNIT['pools']])


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    keys={'schema','id','layout','rom','image_sha256','scope','entry_point','observer',
        'context_bytes','frame_bytes','frame_prefix','entry','controlled_calibration','unit','adapter',*FLAGS}
    if (set(value)!=keys or not test_contract.exact(value['schema'],1)
            or value['id']!='jk08a-closed-loop-coolant-accesses' or value['layout']!='7mfk'
            or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or not test_contract.exact((value['entry_point'],value['observer'],value['context_bytes'],
                value['frame_bytes'],value['frame_prefix']),(ENTRY,OBSERVER,80,192,160))
            or any(value[key] is not False for key in FLAGS)
            or not test_contract.exact(value['entry'],UNIT['code'])
            or not test_contract.exact(value['unit'],UNIT)
            or not test_contract.exact(value['controlled_calibration'],CONTROLLED_CALIBRATION)
            or hashlib.sha256(json.dumps(value['adapter'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=ADAPTER_SHA256):
        raise ValueError('the coolant source changes its exact stock closure, aliases, input or observer premise')
    return value


def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the coolant source changes its complete owned stock image')
    if not test_contract.exact(declared['unit'],UNIT):
        raise ValueError('the coolant source changes its complete exact stock unit')
    for row in UNIT['pools']:
        at,size=row['address'],row['size']
        if image[at:at+size].hex()!=row['stock_hex']:
            raise ValueError('the coolant source changes an exact original constant or pointer literal')


def independent_fixture(declared,image):
    require_image(declared,image);result=bytearray(image)
    for row in UNIT['aliases']:
        at=row['address']
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('the coolant source changes an original native pointer value')
        result[at:at+4]=row['alias'].to_bytes(4,'big')
    for first,last in SPANS:
        if bytes(result[first:last])!=image[first:last]:
            raise ValueError('the coolant fixture modifies a tested stock instruction')
    return bytes(result),[dict(row) for row in UNIT['aliases']]


def fixture_for_case(declared,image,case):
    from kb import closed_loop_coolant_matrix as matrix
    fixture,aliases=independent_fixture(declared,image);result=bytearray(fixture)
    calibration=matrix.calibrations(declared,image,case)
    if set(calibration)!={row['address'] for row in CONTROLLED_CALIBRATION}:
        raise ValueError('the coolant input changes its exact controlled calibration set')
    for row in CONTROLLED_CALIBRATION:
        at,size=row['address'],row['size'];raw=calibration[at]
        if type(raw) is not bytes or len(raw)!=size:
            raise ValueError('the coolant input changes a complete controlled calibration span')
        result[at:at+size]=raw
    for first,last in SPANS:
        if bytes(result[first:last])!=image[first:last]:
            raise ValueError('the coolant input changes a stock executable byte')
    return bytes(result),aliases
