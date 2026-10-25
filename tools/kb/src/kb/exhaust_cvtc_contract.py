"""Exact natural bank2 CVTC state/duty bytes and explicit scalar input premises."""

import hashlib
import json
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.exhaust-cvtc-accesses.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
ENTRIES=(0xC1DEC,0xC2040)
FUNCTIONS=(*ENTRIES,0x21CE0,0x21F40,0x26474,0x26740,0x26944,0x26C78)
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
UNIT = {'assembly': 'tools/sh-elf-run/stock_jk08a_exhaust_cvtc_transition.s',
 'code': [{'start': 138464, 'end': 138694},
          {'start': 139072, 'end': 139310},
          {'start': 156788, 'end': 156822},
          {'start': 157504, 'end': 157550},
          {'start': 158020, 'end': 158080},
          {'start': 158840, 'end': 158990},
          {'start': 794092, 'end': 794360},
          {'start': 794366, 'end': 794628},
          {'start': 794688, 'end': 794962}],
 'pools': [{'address': 34325, 'size': 1, 'stock_hex': 'ab'},
           {'address': 36321, 'size': 1, 'stock_hex': '0a'},
           {'address': 37394, 'size': 4, 'stock_hex': '22a222a2'},
           {'address': 73818, 'size': 9, 'stock_hex': '6666666a717b808014'},
           {'address': 75856, 'size': 8, 'stock_hex': '325a646e788287aa'},
           {'address': 138696, 'size': 8, 'stock_hex': 'ffff98180000044e'},
           {'address': 139312, 'size': 8, 'stock_hex': 'ffff98180000044e'},
           {'address': 156824, 'size': 8, 'stock_hex': '0002674000026944'},
           {'address': 158080, 'size': 4, 'stock_hex': '00026c78'},
           {'address': 794360, 'size': 2, 'stock_hex': '0890'},
           {'address': 794362, 'size': 2, 'stock_hex': '0820'},
           {'address': 794364, 'size': 2, 'stock_hex': '01ae'},
           {'address': 794628, 'size': 2, 'stock_hex': '088c'},
           {'address': 794630, 'size': 2, 'stock_hex': '0271'},
           {'address': 794632, 'size': 2, 'stock_hex': '01ae'},
           {'address': 794634, 'size': 2, 'stock_hex': '07fa'},
           {'address': 794636, 'size': 2, 'stock_hex': '0804'},
           {'address': 794638, 'size': 2, 'stock_hex': '0818'},
           {'address': 794640, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 794644, 'size': 4, 'stock_hex': 'ffff2470'},
           {'address': 794648, 'size': 4, 'stock_hex': 'ffff120e'},
           {'address': 794652, 'size': 4, 'stock_hex': 'ffff267a'},
           {'address': 794656, 'size': 4, 'stock_hex': '0001205a'},
           {'address': 794660, 'size': 4, 'stock_hex': '00012850'},
           {'address': 794664, 'size': 4, 'stock_hex': '00026474'},
           {'address': 794668, 'size': 4, 'stock_hex': '00008615'},
           {'address': 794672, 'size': 4, 'stock_hex': '00009212'},
           {'address': 794676, 'size': 4, 'stock_hex': '00021ce0'},
           {'address': 794680, 'size': 4, 'stock_hex': '00021f40'},
           {'address': 794684, 'size': 4, 'stock_hex': 'ffff0000'},
           {'address': 795048, 'size': 2, 'stock_hex': '0818'},
           {'address': 795050, 'size': 2, 'stock_hex': '09e4'},
           {'address': 795052, 'size': 2, 'stock_hex': '0820'},
           {'address': 795054, 'size': 2, 'stock_hex': '0890'},
           {'address': 795272, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 795276, 'size': 4, 'stock_hex': '00021ce0'},
           {'address': 795280, 'size': 4, 'stock_hex': 'ffff1094'},
           {'address': 795284, 'size': 4, 'stock_hex': 'ffff124c'},
           {'address': 795288, 'size': 4, 'stock_hex': 'ffff120e'},
           {'address': 795292, 'size': 4, 'stock_hex': '00008de1'}],
 'aliases': [{'address': 138696, 'width': 4, 'original': 4294940696, 'alias': 16816152},
             {'address': 139312, 'width': 4, 'original': 4294940696, 'alias': 16816152},
             {'address': 794640, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 794644, 'width': 4, 'original': 4294911088, 'alias': 16786544},
             {'address': 794648, 'width': 4, 'original': 4294906382, 'alias': 16781838},
             {'address': 794652, 'width': 4, 'original': 4294911610, 'alias': 16787066},
             {'address': 795272, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 795280, 'width': 4, 'original': 4294906004, 'alias': 16781460},
             {'address': 795284, 'width': 4, 'original': 4294906444, 'alias': 16781900},
             {'address': 795288, 'width': 4, 'original': 4294906382, 'alias': 16781838}]}
CONTROLLED_CALIBRATION = [{'address': 34325, 'size': 1},
 {'address': 36321, 'size': 1},
 {'address': 37394, 'size': 4},
 {'address': 73818, 'size': 9},
 {'address': 75856, 'size': 8},
 {'address': 138696, 'size': 8},
 {'address': 139312, 'size': 8},
 {'address': 156824, 'size': 8},
 {'address': 158080, 'size': 4},
 {'address': 794360, 'size': 2},
 {'address': 794362, 'size': 2},
 {'address': 794364, 'size': 2},
 {'address': 794628, 'size': 2},
 {'address': 794630, 'size': 2},
 {'address': 794632, 'size': 2},
 {'address': 794634, 'size': 2},
 {'address': 794636, 'size': 2},
 {'address': 794638, 'size': 2},
 {'address': 794640, 'size': 4},
 {'address': 794644, 'size': 4},
 {'address': 794648, 'size': 4},
 {'address': 794652, 'size': 4},
 {'address': 794656, 'size': 4},
 {'address': 794660, 'size': 4},
 {'address': 794664, 'size': 4},
 {'address': 794668, 'size': 4},
 {'address': 794672, 'size': 4},
 {'address': 794676, 'size': 4},
 {'address': 794680, 'size': 4},
 {'address': 794684, 'size': 4},
 {'address': 795048, 'size': 2},
 {'address': 795050, 'size': 2},
 {'address': 795052, 'size': 2},
 {'address': 795054, 'size': 2},
 {'address': 795272, 'size': 4},
 {'address': 795276, 'size': 4},
 {'address': 795280, 'size': 4},
 {'address': 795284, 'size': 4},
 {'address': 795288, 'size': 4},
 {'address': 795292, 'size': 4}]
BOUND_SPANS = ({'address': 138464, 'size': 230},
 {'address': 139072, 'size': 238},
 {'address': 156788, 'size': 34},
 {'address': 157504, 'size': 46},
 {'address': 158020, 'size': 60},
 {'address': 158840, 'size': 150},
 {'address': 794092, 'size': 268},
 {'address': 794366, 'size': 262},
 {'address': 794688, 'size': 274},
 {'address': 34325, 'size': 1},
 {'address': 36321, 'size': 1},
 {'address': 37394, 'size': 4},
 {'address': 73818, 'size': 9},
 {'address': 75856, 'size': 8},
 {'address': 138696, 'size': 8},
 {'address': 139312, 'size': 8},
 {'address': 156824, 'size': 8},
 {'address': 158080, 'size': 4},
 {'address': 794360, 'size': 2},
 {'address': 794362, 'size': 2},
 {'address': 794364, 'size': 2},
 {'address': 794628, 'size': 2},
 {'address': 794630, 'size': 2},
 {'address': 794632, 'size': 2},
 {'address': 794634, 'size': 2},
 {'address': 794636, 'size': 2},
 {'address': 794638, 'size': 2},
 {'address': 794640, 'size': 4},
 {'address': 794644, 'size': 4},
 {'address': 794648, 'size': 4},
 {'address': 794652, 'size': 4},
 {'address': 794656, 'size': 4},
 {'address': 794660, 'size': 4},
 {'address': 794664, 'size': 4},
 {'address': 794668, 'size': 4},
 {'address': 794672, 'size': 4},
 {'address': 794676, 'size': 4},
 {'address': 794680, 'size': 4},
 {'address': 794684, 'size': 4},
 {'address': 795048, 'size': 2},
 {'address': 795050, 'size': 2},
 {'address': 795052, 'size': 2},
 {'address': 795054, 'size': 2},
 {'address': 795272, 'size': 4},
 {'address': 795276, 'size': 4},
 {'address': 795280, 'size': 4},
 {'address': 795284, 'size': 4},
 {'address': 795288, 'size': 4},
 {'address': 795292, 'size': 4})
FLAGS = ('stock_function_stubs',
 'semantic_admission',
 'automatic_resolution',
 'native_geometry_inference',
 'scale_admission',
 'units_admission',
 'natural_caller_reachability',
 'hardware_qualification')
PREMISE = {'bank_index': 1,
 'battery_minimum': 1,
 'axis_hex': '325a646e788287aa',
 'scheduling_admitted': False,
 'sensor_producer_admitted': False}
ADAPTER_SHA256 = 'fb6e0697dec50186a82c62c431b6672536a133dcbae04795348f5139e73a5dd8'
SPANS=tuple((row['start'],row['end']) for row in UNIT['code'])
BOUNDARIES=()


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','entries','observer',
            'context_bytes','frame_bytes','frame_prefix','unit','controlled_calibration','premise','adapter',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-exhaust-cvtc-transition'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or not test_contract.exact((value['entries'],value['observer'],value['context_bytes'],
                value['frame_bytes'],value['frame_prefix']),(list(ENTRIES),OBSERVER,80,192,160))
            or any(value[name] is not False for name in FLAGS)
            or not test_contract.exact(value['unit'],UNIT)
            or not test_contract.exact(value['controlled_calibration'],CONTROLLED_CALIBRATION)
            or not test_contract.exact(value['premise'],PREMISE)
            or hashlib.sha256(json.dumps(value['adapter'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=ADAPTER_SHA256):
        raise ValueError('the CVTC source changes exact stock bytes, bank2 premises or complete raw observation')
    return dict(value,entry=[dict(start=first,end=last) for first,last in SPANS])


def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the CVTC source changes the complete owned stock image')
    if not test_contract.exact(declared['unit'],UNIT):
        raise ValueError('the CVTC source changes a complete tested natural stock unit')
    for row in UNIT['pools']:
        at,size=row['address'],row['size']
        if image[at:at+size].hex()!=row['stock_hex']:
            raise ValueError('the CVTC source changes an original offset, literal or stock calibration')


def independent_fixture(declared,image):
    require_image(declared,image);result=bytearray(image)
    for row in UNIT['aliases']:
        at=row['address']
        if any(first<at+4 and at<last for first,last in SPANS):
            raise ValueError('a CVTC pointer relocation overlaps tested instructions')
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('a CVTC relocation changes its exact original pointer')
        result[at:at+4]=row['alias'].to_bytes(4,'big')
    for first,last in SPANS:
        if bytes(result[first:last])!=image[first:last]:
            raise ValueError('the CVTC fixture modifies a tested stock instruction')
    return bytes(result),[dict(row) for row in UNIT['aliases']]


def fixture_for_case(declared,image,case):
    from kb import exhaust_cvtc_matrix as matrix
    fixture,aliases=independent_fixture(declared,image);result=bytearray(fixture)
    spans={(row['address'],row['size']) for row in CONTROLLED_CALIBRATION}
    for at,data in matrix.calibrations(declared,image,case).items():
        if (at,len(data)) not in spans or any(first<at+len(data) and at<last for first,last in SPANS):
            raise ValueError('a CVTC input changes undeclared calibration or tested instructions')
        result[at:at+len(data)]=data
    return bytes(result),aliases
