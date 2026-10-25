"""Exact bounded parent call and complete natural coordinate conditioner."""

import hashlib
from pathlib import Path
import tomllib

from kb import test_contract

DESCRIPTOR='defs/JK08A.closed-loop-coordinate.toml'
ASSEMBLY='tools/sh-elf-run/stock_jk08a_closed_loop_conversion.s'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
ENTRY=0x3EE5C
WINDOWS=({'start':0x3EE5C,'end':0x3EE7E},
    {'start':0x21BBC,'end':0x21CD6},{'start':0x264A0,'end':0x264C2},
    {'start':0x26740,'end':0x2676E},{'start':0x26944,'end':0x26980},
    {'start':0x26C78,'end':0x26D0E},{'start':0x3EF74,'end':0x3EFFE},
    {'start':0x3F068,'end':0x3F176})
FUNCTIONS=(0x3EDB4,0x3EF74,0x21BBC,0x264A0,0x26740,0x26944,0x26C78)
LITERALS=({'address':0x8978,'size':1,'value':0xA0},
    {'address':0x21CD8,'size':4,'value':0xFFFF9818},
    {'address':0x21CDC,'size':4,'value':0x44E},
    {'address':0x264C4,'size':4,'value':0x26740},
    {'address':0x264C8,'size':4,'value':0x26944},
    {'address':0x26980,'size':4,'value':0x26C78},
    {'address':0x3F002,'size':2,'value':0x8560},
    {'address':0x3F004,'size':2,'value':0x696},
    {'address':0x3F006,'size':2,'value':0x7FFF},
    {'address':0x3F028,'size':4,'value':0xFFFF28F8},
    {'address':0x3F034,'size':4,'value':0xFFFF1094},
    {'address':0x3F038,'size':4,'value':0x148FA},
    {'address':0x3F03C,'size':4,'value':0xFFFF4514},
    {'address':0x3F040,'size':4,'value':0x15D20},
    {'address':0x3F058,'size':4,'value':0x12292},
    {'address':0x3F05C,'size':4,'value':0x11B47},
    {'address':0x3F060,'size':4,'value':0x264A0},
    {'address':0x3F064,'size':4,'value':0x8F98},
    {'address':0x3F176,'size':2,'value':0x696},
    {'address':0x3F178,'size':2,'value':0x7FFF},
    {'address':0x3F17C,'size':4,'value':0x21BBC},
    {'address':0x3F180,'size':4,'value':0xFF00},
    {'address':0x3F184,'size':4,'value':0x95C6},
    {'address':0x3F188,'size':4,'value':0x9384})
CALIBRATIONS=({'address':0x8F98,'size':2},{'address':0x9384,'size':4},
    {'address':0x95C6,'size':2},{'address':0x11B47,'size':17},{'address':0x12292,'size':17})
ALIASES={0x21CD8:0xFFFF9818,0x3F028:0xFFFF28F8,0x3F034:0xFFFF1094,0x3F03C:0xFFFF4514}
NATIVE_STORAGE={'start':0xFFFF8560,'size':20,'logical_offset':0x8560,
    'observed_start':0xFFFF8500,'observed_size':256}
INCOMING={'gbr':0x01008544,'first_word':0x01008554,'second_word_register':0,
    'output_pointer':0x01008558,'coefficient_pointer':0x0100855F}
BOUNDARY={'address':0x3EE7E,'bytes':'57f6472a000b0009',
    'source':'tools/sh-elf-run/publication_inhibit_snapshot_return.s',
    'return_register':7,'stack_return_offset':24,'stock_coordinator_body_admitted':False}
FLAGS=('automatic_resolution','native_geometry_inference','scale_admission','units_admission',
    'natural_caller_reachability','hardware_qualification','source_producer_admission',
    'full_conversion_admission','helper_parameter_reader_admission')


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','assembly','image_sha256','scope','window','literal',
                    'calibration','native_storage','incoming','entry_point','boundary',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-closed-loop-coordinate'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['assembly']!=ASSEMBLY
            or value['image_sha256']!=IMAGE_SHA256 or any(value[key] is not False for key in FLAGS)
            or not test_contract.exact(value['window'],list(WINDOWS))
            or not test_contract.exact(value['literal'],list(LITERALS))
            or not test_contract.exact(value['calibration'],list(CALIBRATIONS))
            or not test_contract.exact(value['native_storage'],NATIVE_STORAGE)
            or not test_contract.exact(value['incoming'],INCOMING)
            or not test_contract.exact(value['entry_point'],ENTRY)
            or not test_contract.exact(value['boundary'],BOUNDARY)):
        raise ValueError('the coordinate call changes its exact stock scope, native storage or entry premises')
    return dict(value,entry=list(WINDOWS))


def pools():
    return tuple(sorted((*LITERALS,*CALIBRATIONS),key=lambda row:row['address']))


def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the coordinate call changes its owned stock image')
    for row in LITERALS:
        if image[row['address']:row['address']+row['size']]!=row['value'].to_bytes(row['size'],'big'):
            raise ValueError('the coordinate call changes an exact stock pointer, native GBR word or literal')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for at,original in ALIASES.items():
        alias=0x01000000+(original&65535)
        fixture[at:at+4]=alias.to_bytes(4,'big');aliases.append(dict(address=at,original=original,alias=alias))
    at=BOUNDARY['address'];data=bytes.fromhex(BOUNDARY['bytes'])
    if any(row['start']<at+len(data) and at<row['end'] for row in WINDOWS) or any(
            row['address']<at+len(data) and at<row['address']+row['size'] for row in pools()):
        raise ValueError('the coordinate observing return overlaps tested stock code or data')
    fixture[at:at+len(data)]=data
    for row in WINDOWS:
        if fixture[row['start']:row['end']]!=image[row['start']:row['end']]:
            raise ValueError('the coordinate fixture changes a tested stock instruction')
    return bytes(fixture),aliases
