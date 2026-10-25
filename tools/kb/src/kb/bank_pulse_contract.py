"""Exact natural bank base-pulse code, literal pools and three RAM aliases."""

import hashlib
from pathlib import Path
import tomllib

from kb import test_contract

DESCRIPTOR='defs/JK08A.bank-pulse-transfers.toml'
ASSEMBLY='tools/sh-elf-run/stock_jk08a_bank_base_pulse.s'
ARITHMETIC_SOURCE='tools/kb/tests/test_bank_base_pulse_chain.py'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
WINDOWS=({'parent':0x4EAD4,'start':0x4EAD4,'end':0x4EBA2},)
POOLS=tuple(dict(address=at,size=size,value=value) for at,size,value in (
    (0x893D,1,0x51),(0x8940,1,1),(0x4EBE2,2,0x634),(0x4EBE4,2,0x690),
    (0x4EC00,4,0xFFFF28F8),(0x4EC04,4,0xFFFF128C),(0x4EC08,4,0xFFFF22DC),
    (0x4EC18,4,0x893D),(0x4EC1C,4,0xFFFF3800)))
ALIASES={0x4EC00:0xFFFF28F8,0x4EC04:0xFFFF128C,0x4EC08:0xFFFF22DC}
RETURNS=()
FLAGS=('automatic_resolution','native_geometry_inference','scale_admission','units_admission',
       'natural_caller_reachability','hardware_qualification')


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','assembly','image_sha256','scope','window','pool',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-bank-pulse-transfers'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['assembly']!=ASSEMBLY
            or value['image_sha256']!=IMAGE_SHA256 or any(value[key] is not False for key in FLAGS)
            or not test_contract.exact(value['window'],list(WINDOWS))
            or not test_contract.exact(value['pool'],list(POOLS))):
        raise ValueError('the bank pulse changes its exact stock bytes, literals or admission boundary')
    return dict(value,entry=[dict(start=row['start'],end=row['end']) for row in WINDOWS])


def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the bank pulse changes its owned stock image')
    for row in POOLS:
        if image[row['address']:row['address']+row['size']]!=row['value'].to_bytes(row['size'],'big'):
            raise ValueError('the bank pulse changes an exact offset, flag or pointer literal')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for at,original in ALIASES.items():
        alias=0x01000000+(original&65535)
        fixture[at:at+4]=alias.to_bytes(4,'big')
        aliases.append(dict(address=at,original=original,alias=alias))
    for row in WINDOWS:
        if fixture[row['start']:row['end']]!=image[row['start']:row['end']]:
            raise ValueError('the bank-pulse fixture changes a tested stock instruction')
    return bytes(fixture),aliases
