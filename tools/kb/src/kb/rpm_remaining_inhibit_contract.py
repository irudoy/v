"""Exact separate RPM caller fixtures and fixed quiet diagnostic consumer premise."""

import hashlib
import json
from pathlib import Path
import tomllib

from kb import test_contract
from kb.rpm_inhibit_contract import INCOMING_GBR

DESCRIPTOR='defs/JK08A.rpm-remaining-inhibit.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
ADAPTER_SHA256='487c6f21afa9ad6ecb58c5d574d3c5664b77c372cf9b5c520a64608fbd538268'
PARENT=0x4ED88
ENTRIES=(0x4EDC6,0x4EDE4,0x4EE00)
FUNCTIONS=(PARENT,0x4F324,0x4F494,0x4F958,0x50A60,0x26388,0x26740)
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
UNIT = {'assembly': 'tools/sh-elf-run/stock_jk08a_rpm_remaining_inhibit.s',
 'code': [{'start': 156552, 'end': 156570},
          {'start': 157504, 'end': 157550},
          {'start': 158340, 'end': 158394},
          {'start': 323014, 'end': 323022},
          {'start': 323044, 'end': 323050},
          {'start': 323072, 'end': 323078},
          {'start': 324388, 'end': 324472},
          {'start': 324474, 'end': 324688},
          {'start': 324756, 'end': 325218},
          {'start': 325976, 'end': 326084},
          {'start': 330336, 'end': 330502}],
 'pools': [{'address': 156570, 'size': 2, 'stock_hex': '00f0'},
           {'address': 156572, 'size': 4, 'stock_hex': '00026a84'},
           {'address': 158396, 'size': 4, 'stock_hex': '00026740'},
           {'address': 323476, 'size': 4, 'stock_hex': '00050a60'},
           {'address': 324472, 'size': 2, 'stock_hex': 'ff60'},
           {'address': 324688, 'size': 2, 'stock_hex': '041a'},
           {'address': 324692, 'size': 4, 'stock_hex': 'ffff1094'},
           {'address': 324704, 'size': 4, 'stock_hex': 'ffff244c'},
           {'address': 324716, 'size': 4, 'stock_hex': 'ffff119c'},
           {'address': 324724, 'size': 4, 'stock_hex': 'ffff256a'},
           {'address': 324728, 'size': 4, 'stock_hex': '000124d2'},
           {'address': 324732, 'size': 4, 'stock_hex': '00026388'},
           {'address': 324736, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 324740, 'size': 4, 'stock_hex': '0000911c'},
           {'address': 324744, 'size': 4, 'stock_hex': 'ffff1068'},
           {'address': 324748, 'size': 4, 'stock_hex': '00008d0e'},
           {'address': 324752, 'size': 4, 'stock_hex': '000085d9'},
           {'address': 325308, 'size': 4, 'stock_hex': 'ffff4184'},
           {'address': 325312, 'size': 4, 'stock_hex': '000186c8'},
           {'address': 325316, 'size': 4, 'stock_hex': 'ffff1094'},
           {'address': 325320, 'size': 4, 'stock_hex': 'ffff42d3'},
           {'address': 325324, 'size': 4, 'stock_hex': 'ffff5718'},
           {'address': 325328, 'size': 4, 'stock_hex': 'ffff1068'},
           {'address': 325332, 'size': 4, 'stock_hex': '00008d15'},
           {'address': 325336, 'size': 4, 'stock_hex': '0007d8b8'},
           {'address': 325340, 'size': 4, 'stock_hex': 'ffff119c'},
           {'address': 325344, 'size': 4, 'stock_hex': '00008957'},
           {'address': 325348, 'size': 4, 'stock_hex': '000088ed'},
           {'address': 325352, 'size': 4, 'stock_hex': 'ffff2458'},
           {'address': 326300, 'size': 2, 'stock_hex': '06a6'},
           {'address': 326512, 'size': 4, 'stock_hex': 'ffff2470'},
           {'address': 326516, 'size': 4, 'stock_hex': '00008b3f'},
           {'address': 326520, 'size': 4, 'stock_hex': '000090e0'},
           {'address': 326524, 'size': 4, 'stock_hex': '000084da'},
           {'address': 326528, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 326532, 'size': 4, 'stock_hex': 'ffff119c'},
           {'address': 330502, 'size': 2, 'stock_hex': '08fe'},
           {'address': 330516, 'size': 4, 'stock_hex': 'ffff119c'},
           {'address': 330528, 'size': 4, 'stock_hex': 'ffff28f8'},
           {'address': 330532, 'size': 4, 'stock_hex': 'ffff2470'},
           {'address': 330536, 'size': 4, 'stock_hex': '00008b3f'},
           {'address': 330540, 'size': 4, 'stock_hex': 'ffff267a'},
           {'address': 330544, 'size': 4, 'stock_hex': 'ffff4188'},
           {'address': 330548, 'size': 4, 'stock_hex': 'ffff424c'},
           {'address': 330552, 'size': 4, 'stock_hex': '000089fc'},
           {'address': 34265, 'size': 2, 'stock_hex': '241e'},
           {'address': 37148, 'size': 2, 'stock_hex': '017d'},
           {'address': 36110, 'size': 1, 'stock_hex': '00'},
           {'address': 74962, 'size': 16, 'stock_hex': '80818181828282828485a9ffffffffff'},
           {'address': 100041, 'size': 1, 'stock_hex': '01'},
           {'address': 36117, 'size': 1, 'stock_hex': 'be'},
           {'address': 35159, 'size': 1, 'stock_hex': '08'},
           {'address': 35053, 'size': 1, 'stock_hex': '4c'},
           {'address': 35647, 'size': 1, 'stock_hex': '18'},
           {'address': 37088, 'size': 2, 'stock_hex': '07d0'},
           {'address': 34010, 'size': 5, 'stock_hex': '48745c3c0c'},
           {'address': 35324, 'size': 2, 'stock_hex': '0624'}],
 'aliases': [{'address': 324692, 'width': 4, 'original': 4294906004, 'alias': 16781460},
             {'address': 324704, 'width': 4, 'original': 4294911052, 'alias': 16786508},
             {'address': 324716, 'width': 4, 'original': 4294906268, 'alias': 16781724},
             {'address': 324724, 'width': 4, 'original': 4294911338, 'alias': 16786794},
             {'address': 324736, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 324744, 'width': 4, 'original': 4294905960, 'alias': 16781416},
             {'address': 325308, 'width': 4, 'original': 4294918532, 'alias': 16793988},
             {'address': 325316, 'width': 4, 'original': 4294906004, 'alias': 16781460},
             {'address': 325320, 'width': 4, 'original': 4294918867, 'alias': 16794323},
             {'address': 325324, 'width': 4, 'original': 4294924056, 'alias': 16799512},
             {'address': 325328, 'width': 4, 'original': 4294905960, 'alias': 16781416},
             {'address': 325340, 'width': 4, 'original': 4294906268, 'alias': 16781724},
             {'address': 325352, 'width': 4, 'original': 4294911064, 'alias': 16786520},
             {'address': 326512, 'width': 4, 'original': 4294911088, 'alias': 16786544},
             {'address': 326528, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 326532, 'width': 4, 'original': 4294906268, 'alias': 16781724},
             {'address': 330516, 'width': 4, 'original': 4294906268, 'alias': 16781724},
             {'address': 330528, 'width': 4, 'original': 4294912248, 'alias': 16787704},
             {'address': 330532, 'width': 4, 'original': 4294911088, 'alias': 16786544},
             {'address': 330540, 'width': 4, 'original': 4294911610, 'alias': 16787066},
             {'address': 330544, 'width': 4, 'original': 4294918536, 'alias': 16793992},
             {'address': 330548, 'width': 4, 'original': 4294918732, 'alias': 16794188}]}
CONTROLLED_CALIBRATION = [{'address': 34265, 'size': 2},
 {'address': 37148, 'size': 2},
 {'address': 36110, 'size': 1},
 {'address': 74962, 'size': 16},
 {'address': 100041, 'size': 1},
 {'address': 36117, 'size': 1},
 {'address': 35159, 'size': 1},
 {'address': 35053, 'size': 1},
 {'address': 35647, 'size': 1},
 {'address': 37088, 'size': 2},
 {'address': 34010, 'size': 5},
 {'address': 35324, 'size': 2}]
BOUNDARIES = [{'address': 323022,
  'bytes': '57f6472a000b0009',
  'source': 'tools/sh-elf-run/publication_inhibit_snapshot_return.s',
  'return_register': 7,
  'stack_return_offset': 24,
  'stock_coordinator_body_admitted': False},
 {'address': 323050,
  'bytes': '57f6472a000b0009',
  'source': 'tools/sh-elf-run/publication_inhibit_snapshot_return.s',
  'return_register': 7,
  'stack_return_offset': 24,
  'stock_coordinator_body_admitted': False},
 {'address': 323078,
  'bytes': '57f6472a000b0009',
  'source': 'tools/sh-elf-run/publication_inhibit_snapshot_return.s',
  'return_register': 7,
  'stack_return_offset': 24,
  'stock_coordinator_body_admitted': False}]
DIAGNOSTIC_PREMISE = {'status_address': 16772,
 'status_value': 192,
 'diagnostic_count_address': 22302,
 'diagnostic_count_minimum': 40,
 'excluded_target': 514232,
 'dispatch_admitted': False,
 'function_stub': False,
 'universal_no_call': False}
FLAGS = ('stock_function_stubs',
 'semantic_admission',
 'automatic_resolution',
 'native_geometry_inference',
 'scale_admission',
 'units_admission',
 'natural_caller_reachability',
 'hardware_qualification',
 'diagnostic_producer_admission',
 'whole_coordinator_admission')

SPANS=tuple((row['start'],row['end']) for row in UNIT['code'])
BOUND_SPANS=tuple([dict(address=first,size=last-first) for first,last in SPANS]+
    [dict(address=row['address'],size=row['size']) for row in UNIT['pools']]+
    [dict(address=row['address'],size=len(bytes.fromhex(row['bytes']))) for row in BOUNDARIES])


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','entries','observer',
            'context_bytes','frame_bytes','frame_prefix','incoming_gbr','entry','unit',
            'controlled_calibration','boundary','diagnostic_premise','adapter',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-rpm-remaining-inhibit'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or not test_contract.exact((value['entries'],value['observer'],value['context_bytes'],
                value['frame_bytes'],value['frame_prefix'],value['incoming_gbr']),
                (list(ENTRIES),OBSERVER,80,192,160,INCOMING_GBR))
            or any(value[name] is not False for name in FLAGS)
            or not test_contract.exact(value['entry'],UNIT['code'])
            or not test_contract.exact(value['unit'],UNIT)
            or not test_contract.exact(value['controlled_calibration'],CONTROLLED_CALIBRATION)
            or not test_contract.exact(value['boundary'],BOUNDARIES)
            or not test_contract.exact(value['diagnostic_premise'],DIAGNOSTIC_PREMISE)
            or hashlib.sha256(json.dumps(value['adapter'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=ADAPTER_SHA256):
        raise ValueError('the remaining RPM source changes exact stock bytes, aliases, caller phases or quiet diagnostic premises')
    return dict(value,entry=[*value['entry'],*(dict(start=row['address'],
        end=row['address']+len(bytes.fromhex(row['bytes']))) for row in BOUNDARIES)])


def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the remaining RPM source changes the complete owned stock image')
    if not test_contract.exact(declared['unit'],UNIT):
        raise ValueError('the remaining RPM source changes its complete stock unit')
    for row in UNIT['pools']:
        at,size=row['address'],row['size']
        if image[at:at+size].hex()!=row['stock_hex']:
            raise ValueError('the remaining RPM source changes an original literal or controlled stock calibration')


def independent_fixture(declared,image):
    require_image(declared,image);result=bytearray(image)
    for row in UNIT['aliases']:
        at=row['address'];result[at:at+4]=row['alias'].to_bytes(4,'big')
    for row in BOUNDARIES:
        at=row['address'];data=bytes.fromhex(row['bytes'])
        if any(first<at+len(data) and at<last for first,last in SPANS) or any(
                pool['address']<at+len(data) and at<pool['address']+pool['size'] for pool in UNIT['pools']):
            raise ValueError('a remaining RPM outside return overlaps tested stock code or data')
        result[at:at+len(data)]=data
    for first,last in SPANS:
        if bytes(result[first:last])!=image[first:last]:
            raise ValueError('the remaining RPM fixture modifies a tested stock instruction')
    return bytes(result),[dict(row) for row in UNIT['aliases']]


def fixture_for_case(declared,image,case):
    from kb import rpm_remaining_inhibit_matrix as matrix
    fixture,aliases=independent_fixture(declared,image);result=bytearray(fixture)
    for at,data in matrix.calibrations(declared,image,case).items():
        if (any(first<at+len(data) and at<last for first,last in SPANS)
                or any(row['address']<at+len(data) and at<row['address']+row['width'] for row in UNIT['aliases'])
                or any(row['address']<at+len(data) and at<row['address']+len(bytes.fromhex(row['bytes'])) for row in BOUNDARIES)):
            raise ValueError('a remaining RPM controlled input overlaps tested instructions, aliases or observing returns')
        result[at:at+len(data)]=data
    return bytes(result),aliases
