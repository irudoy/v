"""Exact stock clear paths; no boot or reset reachability inference."""

import hashlib
from pathlib import Path
import tomllib

from kb import test_contract

DESCRIPTOR = 'defs/JK08A.ram-initialization.toml'
ASSEMBLY = 'tools/sh-elf-run/stock_jk08a_ram_initialization.s'
IMAGE_SHA256 = 'ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
WINDOWS = (
    dict(parent=0x27AC0,start=0x27AE4,end=0x27AFA,gbr=0x225F4,
         first=0xFFFF261C,limit=0xFFFF4512,store=0x27AF0,
         initial_branch=0x27AEC,loop_branch=0x27AF8,prefix_steps=6,loop_steps=5),
    dict(parent=0x27C50,start=0x27C6E,end=0x27C84,gbr=0x2260C,
         first=0xFFFF1000,limit=0xFFFF261A,store=0x27C7A,
         initial_branch=0x27C76,loop_branch=0x27C82,prefix_steps=6,loop_steps=5),
    dict(parent=0x2FC24,start=0x2FC8A,end=0x2FCA4,gbr=0x2260C,
         first=0xFFFF1000,limit=0xFFFF5CF2,store=0x2FC98,
         initial_branch=0x2FC94,loop_branch=0x2FCA0,prefix_steps=7,loop_steps=6),
    dict(parent=0x34B70,start=0x34BF4,end=0x34C10,gbr=0x12344321,
         first=0xFFFF1000,limit=0xFFFF5CF2,store=0x34C04,
         initial_branch=0x34BFC,loop_branch=0x34C0C,prefix_steps=7,loop_steps=7),
    dict(parent=0x26F30,start=0x26F30,end=0x26F4C,gbr=0x12344321,
         first=0xFFFF4514,limit=0xFFFF5CF2,store=0x26F3E,
         initial_branch=0x26F3A,loop_branch=0x26F46,prefix_steps=7,loop_steps=5,
         natural_return=0x26F48,range_pointer=0x22624),
)
POOLS = {0x22604:0xFFFF261C,0x22608:0xFFFF4512,0x22614:0xFFFF1000,
         0x22618:0xFFFF261A,0x22628:0xFFFF5CF2,0x34DA0:0x225F4,
         0x22624:0xFFFF4514,0x26F9C:0x22624}
ALIASES = {at:value for at,value in POOLS.items() if value >= 0xFFFF0000}
RETURNS = tuple(dict(address=row['end'],bytes='000b0009') for row in WINDOWS if 'natural_return' not in row)
FLAGS = ('boot_reachability','reset_reachability','native_geometry_inference',
         'automatic_resolution','scale_admission','units_admission','hardware_qualification')


def stores(window):
    return (window['limit']-window['first']+3)//4


def steps(window):
    return window['prefix_steps']+window['loop_steps']*stores(window)+2


def instruction_budget():
    """Stock loop count, exact loop body and two boundary-return instructions."""
    return max(map(steps,WINDOWS))


def oracle_budget(declared):
    if (declared.get('id')!='jk08a-ram-initialization'
            or not test_contract.exact(declared.get('window'),list(WINDOWS))
            or not test_contract.exact(declared.get('instruction_budget'),instruction_budget())):
        raise ValueError('the RAM initialization oracle changes its exact finite stock loop budget')
    return instruction_budget()


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','assembly','image_sha256','scope',
                    'window','pool','boundary','instruction_budget',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-ram-initialization'
            or value['layout']!='7mfk' or value['rom']!='JK08A'
            or value['assembly']!=ASSEMBLY or value['image_sha256']!=IMAGE_SHA256
            or not test_contract.exact(value['window'],list(WINDOWS))
            or not test_contract.exact(value['pool'],[dict(address=at,value=value) for at,value in POOLS.items()])
            or not test_contract.exact(value['boundary'],list(RETURNS))
            or not test_contract.exact(value['instruction_budget'],instruction_budget())
            or any(value[key] is not False for key in FLAGS)):
        raise ValueError('the RAM initialization source changes its exact windows, range descriptors or admission boundary')
    return dict(value,entry=[dict(start=row['start'],end=row['end']+(0 if 'natural_return' in row else 4)) for row in WINDOWS])


def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the RAM initialization source changes its complete owned stock image')
    for address,value in POOLS.items():
        if image[address:address+4]!=value.to_bytes(4,'big'):
            raise ValueError('the RAM initialization source changes an exact native range pointer')


def independent_fixture(declared,image):
    require_image(declared,image)
    fixture=bytearray(image);aliases=[]
    for address,original in ALIASES.items():
        alias=0x01000000+(original&65535)
        fixture[address:address+4]=alias.to_bytes(4,'big')
        aliases.append(dict(address=address,original=original,alias=alias))
    for row in RETURNS:
        fixture[row['address']:row['address']+4]=bytes.fromhex(row['bytes'])
    for row in WINDOWS:
        if fixture[row['start']:row['end']]!=image[row['start']:row['end']]:
            raise ValueError('the RAM initialization fixture changes tested stock instructions')
    return bytes(fixture),aliases
