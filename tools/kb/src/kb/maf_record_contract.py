"""Exact byte1 reader of existing runtime record0129 and bounded summary call."""

import hashlib
import json
from pathlib import Path
import tomllib

from kb import test_contract

DESCRIPTOR='defs/JK08A.maf-record-readers.toml'
ASSEMBLY='tools/sh-elf-run/stock_jk08a_maf_record_readers.s'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
WINDOWS=({'parent':0x25E20,'start':0x25E20,'end':0x25E44},
    {'parent':0x3C3AC,'start':0x3C3C6,'end':0x3C3DA})
POOLS=({'address':0x25F10,'size':4,'value':0xFFFF5718},
    {'address':0x3C470,'size':2,'value':0x129},{'address':0x3C47C,'size':4,'value':0x25E20})
ALIASES={0x25F10:0xFFFF5718}
RECORD={'owner':'tourmaline-jackal/ram','base':0xFFFF5A93,'size':3,
    'index':0x129,'member_offset':1,'member_bytes':1,'mask':0x80,'status':0xFFFF2449}
BOUNDARY={'address':0x3C3DA,'bytes':'57f6472a000b0009',
    'source':'tools/sh-elf-run/publication_inhibit_snapshot_return.s',
    'return_register':7,'stack_return_offset':24,'stock_coordinator_body_admitted':False}
ADAPTER_SHA256='f7094a21a86bf293388a23cdee3bebaf581cca4e98f599af154468fabef36ed7'
FLAGS=('automatic_resolution','native_geometry_inference','scale_admission','units_admission',
    'natural_caller_reachability','hardware_qualification','record_producer_admission','RPM_contributor_admission')


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','assembly','image_sha256','scope','window','pool','record','boundary','adapter',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-maf-record-readers'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['assembly']!=ASSEMBLY
            or value['image_sha256']!=IMAGE_SHA256 or any(value[key] is not False for key in FLAGS)
            or not test_contract.exact(value['window'],list(WINDOWS))
            or not test_contract.exact(value['pool'],list(POOLS))
            or not test_contract.exact(value['record'],RECORD)
            or not test_contract.exact(value['boundary'],BOUNDARY)
            or hashlib.sha256(json.dumps(value['adapter'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=ADAPTER_SHA256):
        raise ValueError('the MAF record readers change their exact existing record member or stock scope')
    return dict(value,entry=[dict(start=row['start'],end=row['end']) for row in WINDOWS])


def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the MAF record readers change their owned stock image')
    for row in POOLS:
        if image[row['address']:row['address']+row['size']]!=row['value'].to_bytes(row['size'],'big'):
            raise ValueError('a MAF record reader changes its exact base, index or real helper literal')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for at,original in ALIASES.items():
        alias=0x01000000+(original&65535)
        fixture[at:at+4]=alias.to_bytes(4,'big');aliases.append(dict(address=at,original=original,alias=alias))
    at=BOUNDARY['address'];data=bytes.fromhex(BOUNDARY['bytes'])
    if any(row['start']<at+len(data) and at<row['end'] for row in WINDOWS) or any(
            row['address']<at+len(data) and at<row['address']+row['size'] for row in POOLS):
        raise ValueError('the record observing return overlaps tested code or literals')
    fixture[at:at+len(data)]=data
    for row in WINDOWS:
        if fixture[row['start']:row['end']]!=image[row['start']:row['end']]:
            raise ValueError('the record fixture changes a tested stock instruction')
    return bytes(fixture),aliases
