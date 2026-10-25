"""Exact bounded bank-mask decoding from the existing adjustment assembly."""

import hashlib
from pathlib import Path
import tomllib

from kb import test_contract

DESCRIPTOR='defs/JK08A.closed-loop-admission.toml'
ASSEMBLY='tools/sh-elf-run/stock_jk08a_closed_loop_adjustment.s'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
WINDOWS=({'parent':0xA0EE8,'start':0xA0F04,'end':0xA0F7E},
    {'parent':0xA0EE8,'start':0xA0FFE,'end':0xA101C},
    {'parent':0xA0EE8,'start':0xA102C,'end':0xA1036})
ENTRIES=(0xA0F04,0xA0FFE)
POOLS=({'address':0x8E78,'size':1,'value':0},
    {'address':0xA101E,'size':2,'value':0x368},
    {'address':0xA1020,'size':2,'value':0x366},
    {'address':0xA1022,'size':2,'value':0x35F},
    {'address':0xA102A,'size':2,'value':0x35C},
    {'address':0xA114C,'size':4,'value':0xFFFF4558})
ALIASES={0xA114C:0xFFFF4558}
DECODERS=({'input':0xFFFF48C0,'offset':0x2C,'pool_site':0xA0F08,'pool':0xA101E,
        'read_site':0xA0F0E,'one_site':0xA0F26,'zero_site':0xA0F28,'test_site':0xA0F20,'loop_site':0xA0F30},
    {'input':0xFFFF48BE,'offset':0x2E,'pool_site':0xA0F32,'pool':0xA1020,
        'read_site':0xA0F36,'one_site':0xA0F4C,'zero_site':0xA0F4E,'test_site':0xA0F46,'loop_site':0xA0F56},
    {'input':0xFFFF48B7,'offset':0x30,'pool_site':0xA0F58,'pool':0xA1022,
        'read_site':0xA0F5C,'one_site':0xA0F72,'zero_site':0xA0F74,'test_site':0xA0F6C,'loop_site':0xA0F7C},
    {'input':0xFFFF48B4,'offset':0x39,'pool_site':0xA1002,'pool':0xA102A,
        'read_site':0xA1004,'one_site':0xA101A,'zero_site':0xA102C,'test_site':0xA1014,'loop_site':0xA1034})
INCOMING={'gbr':0x0100977C,'second_window':{'r8':1,'r9':0,'r10':2}}
RETURN_SOURCE='tools/sh-elf-run/publication_inhibit_snapshot_return.s'
BOUNDARIES=tuple({'address':at,'bytes':'57f6472a000b0009','source':RETURN_SOURCE,
    'return_register':7,'stack_return_offset':24,'stock_coordinator_body_admitted':False}
    for at in (0xA0F7E,0xA1036))
FLAGS=('automatic_resolution','native_geometry_inference','scale_admission','units_admission',
    'natural_caller_reachability','hardware_qualification','integrator_update_admission',
    'source_producer_admission','hardware_permission_admission')


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','assembly','image_sha256','scope','window','pool',
                    'decoder','incoming','entry_points','boundary',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-closed-loop-admission'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['assembly']!=ASSEMBLY
            or value['image_sha256']!=IMAGE_SHA256 or any(value[key] is not False for key in FLAGS)
            or not test_contract.exact(value['window'],list(WINDOWS))
            or not test_contract.exact(value['pool'],list(POOLS))
            or not test_contract.exact(value['decoder'],list(DECODERS))
            or not test_contract.exact(value['incoming'],INCOMING)
            or not test_contract.exact(value['entry_points'],list(ENTRIES))
            or not test_contract.exact(value['boundary'],list(BOUNDARIES))):
        raise ValueError('the admission decoder changes its exact stock windows, inputs or stores')
    return dict(value,entry=[dict(start=row['start'],end=row['end']) for row in WINDOWS])


def selected(case):
    return DECODERS[:3] if case['entry']==ENTRIES[0] else DECODERS[3:]


def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the admission decoder changes its owned stock image')
    for row in POOLS:
        if image[row['address']:row['address']+row['size']]!=row['value'].to_bytes(row['size'],'big'):
            raise ValueError('the admission decoder changes its exact displacement, base or origin anchor')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for at,original in ALIASES.items():
        alias=0x01000000+(original&65535)
        fixture[at:at+4]=alias.to_bytes(4,'big');aliases.append(dict(address=at,original=original,alias=alias))
    for boundary in BOUNDARIES:
        at=boundary['address'];data=bytes.fromhex(boundary['bytes'])
        if any(row['start']<at+len(data) and at<row['end'] for row in WINDOWS) or any(
                row['address']<at+len(data) and at<row['address']+row['size'] for row in POOLS):
            raise ValueError('an admission observing return overlaps tested stock code or literals')
        fixture[at:at+len(data)]=data
    for row in WINDOWS:
        if fixture[row['start']:row['end']]!=image[row['start']:row['end']]:
            raise ValueError('the admission fixture changes a tested stock instruction')
    return bytes(fixture),aliases
