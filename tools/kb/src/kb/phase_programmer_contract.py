"""Exact post-guard injection offset window and real reciprocal helper."""

import hashlib
from pathlib import Path
import tomllib

from kb import test_contract

DESCRIPTOR='defs/JK08A.phase-programmer.toml'
ASSEMBLY='tools/sh-elf-run/stock_jk08a_injection_offset.s'
LEGACY_INPUTS='tools/sh-elf-run/injection-offset-cases.h'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
WINDOWS=({'parent':0x2B64A,'start':0x2B6D4,'end':0x2B6F8},
         {'parent':0x28E7C,'start':0x28E7C,'end':0x28E9E})
POOLS=({'address':0x28EA0,'size':2,'value':6554},
       {'address':0x2B75E,'size':6,'value':0x06AF02C80436},
       {'address':0x2B864,'size':4,'value':0xFFFF128C},
       {'address':0x2B86C,'size':4,'value':0x28E7C},
       {'address':0x2B874,'size':4,'value':0xFFFF1FF4})
ALIASES={0x2B864:0xFFFF128C,0x2B874:0xFFFF1FF4}
BOUNDARY={'address':0x2B6F8,'bytes':'57f6472a000b0009',
    'source':'tools/sh-elf-run/publication_inhibit_snapshot_return.s',
    'return_register':7,'stack_return_offset':24,'stock_programmer_body_admitted':False}
FLAGS=('automatic_resolution','native_geometry_inference','scale_admission','units_admission',
       'natural_caller_reachability','hardware_qualification','count_guard_admission','peripheral_admission')


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','assembly','image_sha256','scope','window','pool','boundary',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-phase-programmer'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['assembly']!=ASSEMBLY
            or value['image_sha256']!=IMAGE_SHA256 or any(value[key] is not False for key in FLAGS)
            or not test_contract.exact(value['window'],list(WINDOWS))
            or not test_contract.exact(value['pool'],list(POOLS))
            or not test_contract.exact(value['boundary'],BOUNDARY)):
        raise ValueError('the phase programmer changes its exact post-guard stock window or admission boundary')
    return dict(value,entry=[dict(start=row['start'],end=row['end']) for row in WINDOWS])


def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the phase programmer changes its owned stock image')
    for row in POOLS:
        if image[row['address']:row['address']+row['size']]!=row['value'].to_bytes(row['size'],'big'):
            raise ValueError('the phase programmer changes an exact pointer, offset or multiplier literal')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for at,original in ALIASES.items():
        alias=0x01000000+(original&65535)
        fixture[at:at+4]=alias.to_bytes(4,'big');aliases.append(dict(address=at,original=original,alias=alias))
    at=BOUNDARY['address'];data=bytes.fromhex(BOUNDARY['bytes'])
    if any(row['start']<at+len(data) and at<row['end'] for row in WINDOWS) or any(
            row['address']<at+len(data) and at<row['address']+row['size'] for row in POOLS):
        raise ValueError('the phase programmer observing return overlaps tested instructions or pools')
    fixture[at:at+len(data)]=data
    for row in WINDOWS:
        if fixture[row['start']:row['end']]!=image[row['start']:row['end']]:
            raise ValueError('the phase programmer fixture changes a tested instruction')
    return bytes(fixture),aliases
