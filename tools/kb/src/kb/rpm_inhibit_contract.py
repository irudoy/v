"""Exact bounded contributor, MAF-summary and shared-status instruction units."""

import hashlib
from pathlib import Path
import tomllib

from kb import test_contract

DESCRIPTOR='defs/JK08A.rpm-inhibit.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
ENTRY=0x4EDBE
PARENT=0x4ED88
FUNCTIONS = (322952, 323996, 324226, 325430, 326304, 329678, 154084, 156528, 157504)
INCOMING_GBR=0x01009F34
UNITS = [{'id': 'jk08a-rpm-inhibit-callers',
  'assembly': 'tools/sh-elf-run/stock_jk08a_rpm_inhibit_callers.s',
  'code': [{'start': 323006, 'end': 323014},
           {'start': 323026, 'end': 323030},
           {'start': 323050, 'end': 323056},
           {'start': 323064, 'end': 323068}],
  'pools': [{'address': 323468, 'size': 4}],
  'aliases': []},
 {'id': 'jk08a-rpm-inhibit-vehicle',
  'assembly': 'tools/sh-elf-run/stock_jk08a_vehicle_speed_fuel_cut.s',
  'code': [{'start': 323996, 'end': 324056}, {'start': 324160, 'end': 324226}],
  'pools': [{'address': 324092, 'size': 4},
            {'address': 324132, 'size': 4},
            {'address': 324156, 'size': 4},
            {'address': 324692, 'size': 12},
            {'address': 36279, 'size': 1},
            {'address': 36291, 'size': 1},
            {'address': 36015, 'size': 1}],
  'aliases': [{'address': 324092, 'original': 4294911088},
              {'address': 324132, 'original': 4294906004},
              {'address': 324692, 'original': 4294906004}]},
 {'id': 'jk08a-rpm-inhibit-main',
  'assembly': 'tools/sh-elf-run/stock_jk08a_main_rpm_fuel_cut.s',
  'code': [{'start': 324226, 'end': 324388}],
  'pools': [{'address': 324704, 'size': 20},
            {'address': 35640, 'size': 1},
            {'address': 35945, 'size': 1},
            {'address': 37710, 'size': 12}],
  'aliases': [{'address': 324704, 'original': 4294911052}, {'address': 324716, 'original': 4294906268}]},
 {'id': 'jk08a-rpm-summary-leaves',
  'assembly': 'tools/sh-elf-run/stock_jk08a_rpm_summary_leaves.s',
  'code': [{'start': 325430, 'end': 325464}, {'start': 326304, 'end': 326316}],
  'pools': [{'address': 325904, 'size': 8}, {'address': 326556, 'size': 4}],
  'aliases': [{'address': 325904, 'original': 4294911048},
              {'address': 325908, 'original': 4294906268},
              {'address': 326556, 'original': 4294918536}]},
 {'id': 'jk08a-composite-rpm-inhibit',
  'assembly': 'tools/sh-elf-run/stock_jk08a_composite_rpm_inhibit.s',
  'code': [{'start': 329678, 'end': 329770}, {'start': 329782, 'end': 329958}],
  'pools': [{'address': 329778, 'size': 2},
            {'address': 329780, 'size': 2},
            {'address': 329958, 'size': 2},
            {'address': 329964, 'size': 4},
            {'address': 329980, 'size': 4},
            {'address': 329984, 'size': 4},
            {'address': 329988, 'size': 4},
            {'address': 329992, 'size': 4},
            {'address': 329996, 'size': 4},
            {'address': 330000, 'size': 4},
            {'address': 330004, 'size': 4},
            {'address': 330008, 'size': 4},
            {'address': 330012, 'size': 4}],
  'aliases': [{'address': 329964, 'original': 4294906004},
              {'address': 329980, 'original': 4294911064},
              {'address': 329984, 'original': 4294918569},
              {'address': 329992, 'original': 4294905900},
              {'address': 329996, 'original': 4294906268},
              {'address': 330008, 'original': 4294906508}]},
 {'id': 'jk08a-diagnostic-fault-sentinel',
  'assembly': 'tools/sh-elf-run/stock_jk08a_diagnostic_fault_sentinel.s',
  'code': [{'start': 154084, 'end': 154130}],
  'pools': [{'address': 154520, 'size': 4}],
  'aliases': [{'address': 154520, 'original': 4294924056}]},
 {'id': 'jk08a-composite-byte-curve',
  'assembly': 'tools/sh-elf-run/stock_jk08a_implicit_byte_curve.s',
  'code': [{'start': 156528, 'end': 156546},
           {'start': 157504, 'end': 157550},
           {'start': 158336, 'end': 158394}],
  'pools': [{'address': 156546, 'size': 2}, {'address': 156548, 'size': 4}, {'address': 158396, 'size': 4}],
  'aliases': []}]
CALIBRATIONS = ({'address': 35640, 'size': 1},
 {'address': 35945, 'size': 1},
 {'address': 36015, 'size': 1},
 {'address': 36279, 'size': 1},
 {'address': 36291, 'size': 1},
 {'address': 37710, 'size': 12},
 {'address': 37986, 'size': 2},
 {'address': 76338, 'size': 8})
BOUNDARY={'address': 323014, 'bytes': '57f6472a000b0009', 'source': 'tools/sh-elf-run/publication_inhibit_snapshot_return.s', 'return_register': 7, 'stack_return_offset': 24, 'full_coordinator_admitted': False}
FLAGS = ('automatic_resolution',
 'native_geometry_inference',
 'scale_admission',
 'units_admission',
 'natural_caller_reachability',
 'hardware_qualification',
 'full_coordinator_admission',
 'stock_conditioned_pair_reachability',
 'physical_units_admission',
 'stock_shared_status_reachability',
 'stock_composite_seed_reachability')
SPANS=tuple((row['start'],row['end']) for unit in UNITS for row in unit['code'])
ALIASES={row['address']:row['original'] for unit in UNITS for row in unit['aliases']}
EXTRA_BOUNDARIES = ({'address': 323030,
  'bytes': '57f6472a000b0009',
  'source': 'tools/sh-elf-run/publication_inhibit_snapshot_return.s',
  'return_register': 7,
  'stack_return_offset': 24,
  'full_coordinator_admitted': False},
 {'address': 323068,
  'bytes': '57f6472a000b0009',
  'source': 'tools/sh-elf-run/publication_inhibit_snapshot_return.s',
  'return_register': 7,
  'stack_return_offset': 24,
  'full_coordinator_admitted': False},
 {'address': 323056,
  'bytes': '57f6472a000b0009',
  'source': 'tools/sh-elf-run/publication_inhibit_snapshot_return.s',
  'return_register': 7,
  'stack_return_offset': 24,
  'full_coordinator_admitted': False})
BOUNDARIES=(BOUNDARY,*EXTRA_BOUNDARIES)


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','entry_point','incoming_gbr',
            'normalized_functions','boundary','extra_boundaries','unit','calibration',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-rpm-inhibit'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or any(value[key] is not False for key in FLAGS)
            or not test_contract.exact((value['entry_point'],value['incoming_gbr']),(ENTRY,INCOMING_GBR))
            or not test_contract.exact(value['normalized_functions'],list(FUNCTIONS))
            or not test_contract.exact(value['boundary'],BOUNDARY)
            or not test_contract.exact(value['extra_boundaries'],list(EXTRA_BOUNDARIES))
            or not test_contract.exact(value['unit'],UNITS)
            or not test_contract.exact(value['calibration'],list(CALIBRATIONS))):
        raise ValueError('the bounded RPM contributors change an exact stock source, entry premise or scope')
    return dict(value,entry=[dict(start=start,end=end) for start,end in SPANS]+
        [dict(start=row['address'],end=row['address']+8) for row in BOUNDARIES])


def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the bounded RPM contributors change their owned stock image')
    for unit in UNITS:
        for span in unit['code']:
            for pc in range(span['start'],span['end'],2):
                word=int.from_bytes(image[pc:pc+2],'big')
                if word>>12 in (9,13):
                    width=4 if word>>12==13 else 2
                    at=((pc&~3) if width==4 else pc)+4+(word&255)*width
                    if not any(row['address']<=at and at+width<=row['address']+row['size'] for row in unit['pools']):
                        raise ValueError('a bounded RPM contributor reads an undeclared PC-relative pool')
        for row in unit['aliases']:
            if int.from_bytes(image[row['address']:row['address']+4],'big')!=row['original']:
                raise ValueError('a bounded RPM contributor changes an exact stock RAM pointer')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for at,original in sorted(ALIASES.items()):
        if any(start<at+4 and at<end for start,end in SPANS):
            raise ValueError('a bounded RPM alias changes tested stock instructions')
        alias=0x01000000+(original&65535);fixture[at:at+4]=alias.to_bytes(4,'big')
        aliases.append(dict(address=at,original=original,alias=alias))
    for boundary in BOUNDARIES:
        at=boundary['address'];data=bytes.fromhex(boundary['bytes'])
        if any(start<at+len(data) and at<end for start,end in SPANS) or any(
                row['address']<at+len(data) and at<row['address']+row['size'] for unit in UNITS for row in unit['pools']):
            raise ValueError('the bounded RPM observing return overlaps tested stock bytes or data')
        fixture[at:at+len(data)]=data
    return bytes(fixture),aliases
