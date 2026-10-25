"""Exact natural APC normalizer/splitter bytes and explicit native pointer pairs."""

import hashlib
from pathlib import Path
import tomllib

from kb import test_contract

DESCRIPTOR='defs/JK08A.phase-normalization.toml'
ASSEMBLY='tools/sh-elf-run/stock_jk08a_injection_tooth.s'
NUMERIC='tools/sh-elf-run/stock_injection_programmer_model.py'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
WINDOWS=({'parent':0x28DC8,'start':0x28DC8,'end':0x28E7C},
         {'parent':0x28E7C,'start':0x28E7C,'end':0x28E9E})
PAIRS=({'word':0xFFFF13B8,'byte':0xFFFF193B,'word_owner':'huge-lori/ram','byte_owner':'economic-collie/ram'},
       {'word':0xFFFF1558,'byte':0xFFFF155A,'word_owner':'vivacious-petrel/ram','byte_owner':'peridot-pony/ram'})
POOLS=({ 'address':0x28E9E,'size':2,'value':0x0126},
       { 'address':0x29020,'size':4,'value':0xFFFF128C},
       { 'address':0x28EA0,'size':2,'value':6554})
ALIASES={0x29020:0xFFFF128C}
RETURNS=()
FLAGS=('automatic_resolution','native_geometry_inference','scale_admission','units_admission',
       'natural_caller_reachability','hardware_qualification')


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','assembly','image_sha256','scope','window','pair','pool',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-phase-normalization'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['assembly']!=ASSEMBLY
            or value['image_sha256']!=IMAGE_SHA256 or any(value[key] is not False for key in FLAGS)
            or not test_contract.exact(value['window'],list(WINDOWS))
            or not test_contract.exact(value['pair'],list(PAIRS))
            or not test_contract.exact(value['pool'],list(POOLS))):
        raise ValueError('the phase normalizer changes its exact stock bytes, pointer premises or admission boundary')
    return dict(value,entry=[dict(start=row['start'],end=row['end']) for row in WINDOWS])


def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the phase normalizer changes its owned stock image')
    for row in POOLS:
        if image[row['address']:row['address']+row['size']]!=row['value'].to_bytes(row['size'],'big'):
            raise ValueError('the phase normalizer changes its exact position offset or base literal')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for at,original in ALIASES.items():
        alias=0x01000000+(original&65535)
        fixture[at:at+4]=alias.to_bytes(4,'big')
        aliases.append(dict(address=at,original=original,alias=alias))
    for row in WINDOWS:
        if fixture[row['start']:row['end']]!=image[row['start']:row['end']]:
            raise ValueError('the phase normalizer fixture changes a tested stock instruction')
    return bytes(fixture),aliases
