"""Exact source and fixture boundary of the native byte-surface closure.

Descriptor validation and fixture construction grant no execution, geometry
publication, access identity or diagnostic dependency on their own.
"""

import hashlib
from pathlib import Path
import tomllib

from kb import test_contract

DESCRIPTOR = 'defs/JK08A.byte-surface-paths.toml'
IMAGE_SHA256 = 'ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
ENTRIES = {
    'caller':(0xBFDC0,0xBFE80),'wrapper4':(0x26084,0x260B4),
    'wrapper8':(0x26140,0x26170),'wrapper16':(0x261B8,0x261E8),
    'axis':(0x26944,0x26980),'surface':(0x26770,0x267C6),
    'linear':(0x26740,0x2676E),'divider':(0x26C78,0x26D0E),
}
SURFACES = ((0xB2FA,8,0x12EC2,0x12EA2,0xFFFF1C5F),
            (0xB33A,16,0x12F2E,0x12F0E,0xFFFF1C5D),
            (0xAB4A,4,0x12F96,0x12F8E,0xFFFF1C5D))
ALIASES = {0xBFFF8:0xFFFF128C,0xC0004:0xFFFF2464,
           0xC000C:0xFFFF102C,0xC0010:0xFFFF119C}
SELECTION = dict(coordinate_source=0xFFFF11AE,load_source=0xFFFF102C,
    force_mode_source=0xFFFF2468,force_mode_mask=8,ROM_configuration=0x8615,
    ROM_configuration_mask=1,ROM_offset_pool=0xC0008,ROM_offset_value=0xFFFF5773,
    ROM_GBR=0x12EA2,correction_source=0xFFFF2466,correction_mask=64)


def descriptor(root):
    declared=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    keys={'schema','id','scope','layout','rom','image_sha256','assembly','stock_function_stubs',
          'native_geometry_changed','ROM_to_DID_dependency_inference','natural_caller_reachability',
          'hardware_qualification','entry','pool','surface','selection'}
    if (set(declared)!=keys or type(declared['schema']) is not int or declared['schema']!=1
            or declared['id']!='jk08a-byte-surface-paths' or declared['layout']!='7mfk'
            or declared['rom']!='JK08A' or declared['image_sha256']!=IMAGE_SHA256
            or declared['assembly']!='tools/sh-elf-run/stock_jk08a_byte_surface_paths.s'
            or any(declared[key] is not False for key in ('stock_function_stubs','native_geometry_changed',
                'ROM_to_DID_dependency_inference','natural_caller_reachability','hardware_qualification'))):
        raise ValueError('the byte-surface descriptor changes its exact image or bounded admission scope')
    entries={row['key']:(row['start'],row['end']) for row in declared['entry']}
    if len(entries)!=len(declared['entry']) or not test_contract.exact(entries,ENTRIES):
        raise ValueError('the byte-surface descriptor changes an exact natural entry or callee span')
    surfaces=tuple((row['table'],row['rows'],row['row_axis'],row['col_axis'],row['caller_output'])
                   for row in declared['surface'])
    if (not test_contract.exact(surfaces,SURFACES)
            or any(type(row['cols']) is not int or row['cols']!=row['rows']
                   or type(row['element_bytes']) is not int or row['element_bytes']!=1
                   for row in declared['surface'])):
        raise ValueError('the byte-surface descriptor changes its conditional wrapper geometry or publication')
    if not test_contract.exact(declared['selection'],SELECTION):
        raise ValueError('the byte-surface descriptor changes coordinate, configuration or correction inputs')
    addresses=set()
    aliases={}
    for row in declared['pool']:
        if (set(row)!={'address','width_bytes','stock_value','RAM_pointer_alias'}
                or type(row['address']) is not int or row['address'] in addresses
                or type(row['width_bytes']) is not int or row['width_bytes'] not in (2,4)
                or type(row['stock_value']) is not int or not 0<=row['stock_value']<(1 << (8*row['width_bytes']))
                or type(row['RAM_pointer_alias']) is not bool):
            raise ValueError('the byte-surface descriptor repeats or changes a typed stock pool')
        addresses.add(row['address'])
        if row['RAM_pointer_alias']:
            if row['width_bytes']!=4:
                raise ValueError('the byte-surface RAM alias changes its pointer width')
            aliases[row['address']]=row['stock_value']
    if not test_contract.exact(aliases,ALIASES):
        raise ValueError('the byte-surface descriptor changes an exact native RAM pointer alias')
    offsets=[row for row in declared['pool'] if row['address']==0xC0008]
    if offsets!=[dict(address=0xC0008,width_bytes=4,stock_value=0xFFFF5773,RAM_pointer_alias=False)]:
        raise ValueError('the byte-surface descriptor aliases the wrapping ROM offset as a RAM pointer')
    return declared


def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the byte-surface source has another complete owned stock image')
    pools=set()
    for row in declared['entry']:
        for pc in range(row['start'],row['end'],2):
            word=int.from_bytes(image[pc:pc+2],'big')
            if word >> 12 in (9,13):
                width=4 if word >> 12==13 else 2
                address=((pc&~3) if width==4 else pc)+4+(word&255)*width
                pools.add((address,width))
    stated={(row['address'],row['width_bytes']) for row in declared['pool']}
    if pools!=stated:
        raise ValueError('the byte-surface descriptor omits or adds an actual PC-relative pool')
    for row in declared['pool']:
        start,width=row['address'],row['width_bytes']
        if int.from_bytes(image[start:start+width],'big')!=row['stock_value']:
            raise ValueError('the byte-surface descriptor changes an exact stock literal')


def independent_fixture(declared,image):
    """Reconstruct declared aliases while preserving the wrapping ROM offset."""
    require_image(declared,image)
    fixture=bytearray(image)
    aliases=[]
    for address,original in sorted(ALIASES.items()):
        if any(row['start']<=address<row['end'] for row in declared['entry']):
            raise ValueError('the byte-surface RAM alias changes tested executable instructions')
        relocated=0x01000000+(original&65535)
        fixture[address:address+4]=relocated.to_bytes(4,'big')
        aliases.append(dict(address=address,original=original,alias=relocated))
    if fixture[0xC0008:0xC000C]!=image[0xC0008:0xC000C]:
        raise ValueError('the byte-surface fixture changes its wrapping ROM offset')
    return bytes(fixture),aliases
