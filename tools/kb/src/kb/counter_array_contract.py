"""Exact bounded stock counter arrays; no cadence or interrupt-entry inference."""

import hashlib
from pathlib import Path
import tomllib

from kb import test_contract

DESCRIPTOR='defs/JK08A.counter-arrays.toml'
ASSEMBLY='tools/sh-elf-run/stock_jk08a_counter_arrays.s'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
WINDOWS=(dict(parent=0x2040C,start=0x205A6,end=0x2061A,gbr=0x12344321,prefix_steps=22),
         dict(parent=0x2040C,start=0x206A2,end=0x206CA,gbr=0x12344321,prefix_steps=8),
         dict(parent=0x208F8,start=0x2093E,end=0x20962,gbr=0x12344321,prefix_steps=6))
ARRAYS=(dict(entry=0x205A6,pointer=0x20660,first=0xFFFF256A,count=138,width_bytes=1,
             read=0x205B6,repeat_read=0x205BC,store=0x205C2,initial_branch=0x205B2,zero_branch=0x205BA,loop_branch=0x205CC),
        dict(entry=0x205A6,pointer=0x20664,first=0xFFFF2604,count=10,width_bytes=2,
             read=0x205DA,repeat_read=0x205E0,store=0x205E6,initial_branch=0x205D6,zero_branch=0x205DE,loop_branch=0x205F0),
        dict(entry=0x205A6,pointer=0x20668,first=0xFFFF43C7,count=195,width_bytes=1,
             read=0x20602,repeat_read=0x20608,store=0x2060E,initial_branch=0x205FE,zero_branch=0x20606,loop_branch=0x20618),
        dict(entry=0x206A2,pointer=0x208E0,first=0xFFFF42D3,count=244,width_bytes=1,
             read=0x206B2,repeat_read=0x206B8,store=0x206BE,initial_branch=0x206AE,zero_branch=0x206B6,loop_branch=0x206C8),
        dict(entry=0x2093E,pointer=0x20B44,first=0xFFFF25FB,count=7,width_bytes=1,
             read=0x2094A,repeat_read=0x20950,store=0x20956,initial_branch=0x20946,zero_branch=0x2094E,loop_branch=0x20960))
POOLS={0x20660:0xFFFF256A,0x20664:0xFFFF2604,0x20668:0xFFFF43C7,0x208E0:0xFFFF42D3,
    0x20B44:0xFFFF25FB}
ALIASES=POOLS
RETURNS=tuple(dict(address=row['end'],bytes='000b0009') for row in WINDOWS)
FLAGS=('ISR_entry_reachability','periodic_cadence_inference','native_geometry_inference',
       'automatic_resolution','scale_admission','units_admission','hardware_qualification')


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','assembly','image_sha256','scope','window','array','pool','boundary',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-counter-arrays'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['assembly']!=ASSEMBLY
            or value['image_sha256']!=IMAGE_SHA256 or any(value[key] is not False for key in FLAGS)
            or not test_contract.exact(value['window'],list(WINDOWS))
            or not test_contract.exact(value['array'],list(ARRAYS))
            or not test_contract.exact(value['pool'],[dict(address=at,value=value) for at,value in POOLS.items()])
            or not test_contract.exact(value['boundary'],list(RETURNS))):
        raise ValueError('the counter-array source changes an exact stock window, array or admission boundary')
    return dict(value,entry=[dict(start=row['start'],end=row['end']+4) for row in WINDOWS])


def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the counter-array source changes its complete owned stock image')
    for at,value in POOLS.items():
        if image[at:at+4]!=value.to_bytes(4,'big'):
            raise ValueError('the counter-array source changes an exact native array pointer')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for at,original in POOLS.items():
        alias=0x01000000+(original&65535);fixture[at:at+4]=alias.to_bytes(4,'big')
        aliases.append(dict(address=at,original=original,alias=alias))
    for row in RETURNS:fixture[row['address']:row['address']+4]=bytes.fromhex(row['bytes'])
    for row in WINDOWS:
        if fixture[row['start']:row['end']]!=image[row['start']:row['end']]:
            raise ValueError('the counter-array fixture changes tested stock instructions')
    return bytes(fixture),aliases
