"""Exact existing two-curve lookup slice and its real stock helper closure."""

import hashlib
from pathlib import Path
import tomllib

from kb import test_contract

DESCRIPTOR='defs/JK08A.maf-transfer.toml'
ASSEMBLY='tools/sh-elf-run/stock_jk08a_maf_transfer.s'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
WINDOWS=({'parent':0x3A904,'start':0x3A922,'end':0x3A94C},
    {'parent':0x26410,'start':0x26410,'end':0x26424},
    {'parent':0x26A74,'start':0x26A74,'end':0x26ABA},
    {'parent':0x26740,'start':0x26740,'end':0x2676E})
POOLS=({'address':0x86F9,'size':1},{'address':0x141F4,'size':256}, {'address':0x26424,'size':2},
    {'address':0x26428,'size':4},{'address':0x26ABC,'size':4},{'address':0x3AB60,'size':16})
LITERALS={0x86F9:'dc',0x26424:'3f00',0x26428:'00026a74',0x26ABC:'00026740',
    0x3AB60:'0001427400026410ffff1048000141f4'}
ALIASES={0x3AB68:0xFFFF1048}
BOUNDARY={'address':0x3A94C,'bytes':'57f6472a000b0009',
    'source':'tools/sh-elf-run/publication_inhibit_snapshot_return.s',
    'return_register':7,'stack_return_offset':24,'stock_coordinator_body_admitted':False}
CURVES=({'address':0x141F4,'size':128,'owner':'ivory-gecko/tbl','channel':1},
    {'address':0x14274,'size':128,'owner':'wealthy-woodlouse/tbl','channel':0})
FLAGS=('automatic_resolution','native_geometry_inference','scale_admission','units_admission',
    'natural_caller_reachability','hardware_qualification','correction_publisher_admission','universal_no_read_claim')


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','assembly','image_sha256','scope','window','pool','curve','boundary',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-maf-transfer'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['assembly']!=ASSEMBLY
            or value['image_sha256']!=IMAGE_SHA256 or any(value[key] is not False for key in FLAGS)
            or not test_contract.exact(value['window'],list(WINDOWS))
            or not test_contract.exact(value['pool'],list(POOLS))
            or not test_contract.exact(value['curve'],list(CURVES))
            or not test_contract.exact(value['boundary'],BOUNDARY)):
        raise ValueError('the MAF curve slice changes its exact stock closure or bounded admission')
    return dict(value,entry=[dict(start=row['start'],end=row['end']) for row in WINDOWS])


def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the MAF curve slice changes its owned stock image')
    for at,value in LITERALS.items():
        data=bytes.fromhex(value)
        if image[at:at+len(data)]!=data:raise ValueError('the MAF curve slice changes an exact pointer or clamp literal')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for at,original in ALIASES.items():
        alias=0x01000000+(original&65535)
        fixture[at:at+4]=alias.to_bytes(4,'big');aliases.append(dict(address=at,original=original,alias=alias))
    at=BOUNDARY['address'];data=bytes.fromhex(BOUNDARY['bytes'])
    if any(row['start']<at+len(data) and at<row['end'] for row in WINDOWS) or any(
            row['address']<at+len(data) and at<row['address']+row['size'] for row in POOLS):
        raise ValueError('the MAF observing return overlaps tested instructions or data')
    fixture[at:at+len(data)]=data
    for row in WINDOWS:
        if fixture[row['start']:row['end']]!=image[row['start']:row['end']]:
            raise ValueError('the MAF curve fixture changes a tested instruction')
    return bytes(fixture),aliases
