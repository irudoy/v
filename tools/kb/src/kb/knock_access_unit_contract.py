"""Exact stock knock units and separate simulator-only observation returns."""

import hashlib
from pathlib import Path
import tomllib

from kb import test_contract

DESCRIPTOR='defs/JK08A.knock-accesses.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
RETURN_SOURCE='tools/sh-elf-run/publication_inhibit_snapshot_return.s'
RETURN_BYTES='57f6472a000b0009'
FLAGS=('automatic_resolution','native_geometry_inference','scale_admission','units_admission',
       'natural_caller_reachability','hardware_qualification')
UNITS=({'id': 'normalization',
  'parent': 303672,
  'entry': 303722,
  'assembly': 'tools/sh-elf-run/stock_jk08a_knock_normalization.s',
  'code': [{'start': 303722, 'end': 303798},
           {'start': 304048, 'end': 304126},
           {'start': 304184, 'end': 304278},
           {'start': 304380, 'end': 304526},
           {'start': 138464, 'end': 138602}],
  'pools': [{'address': 304332, 'size': 4, 'stock_hex': 'ffff11d4'},
            {'address': 304336, 'size': 4, 'stock_hex': 'ffff1ff4'},
            {'address': 304340, 'size': 4, 'stock_hex': 'ffff20d2'},
            {'address': 304344, 'size': 4, 'stock_hex': 'ffff20c2'},
            {'address': 304372, 'size': 4, 'stock_hex': 'ffff2132'},
            {'address': 304376, 'size': 4, 'stock_hex': '00021ce0'},
            {'address': 304528, 'size': 4, 'stock_hex': 'ffff87e1'},
            {'address': 304532, 'size': 4, 'stock_hex': 'ffff20d2'},
            {'address': 304536, 'size': 4, 'stock_hex': 'ffff1ff4'},
            {'address': 304540, 'size': 4, 'stock_hex': 'ffff20c2'},
            {'address': 304544, 'size': 4, 'stock_hex': 'ffff2132'},
            {'address': 304548, 'size': 4, 'stock_hex': '00021ce0'},
            {'address': 304552, 'size': 4, 'stock_hex': 'ffff11d4'},
            {'address': 303692, 'size': 12, 'stock_hex': 'd29e6020c90820088d026b03'},
            {'address': 303708, 'size': 14, 'stock_hex': 'de9b84ea650c25588b01a0900009'},
            {'address': 304032, 'size': 16, 'stock_hex': 'e001de4b4018704f05ec6e5c2ee889ec'},
            {'address': 304328, 'size': 4, 'stock_hex': '00008b3d'},
            {'address': 35645, 'size': 1, 'stock_hex': '82'}],
  'aliases': [{'address': 304332, 'original': 4294906324},
              {'address': 304336, 'original': 4294909940},
              {'address': 304340, 'original': 4294910162},
              {'address': 304344, 'original': 4294910146},
              {'address': 304372, 'original': 4294910258},
              {'address': 304528, 'original': 4294936545},
              {'address': 304532, 'original': 4294910162},
              {'address': 304536, 'original': 4294909940},
              {'address': 304540, 'original': 4294910146},
              {'address': 304544, 'original': 4294910258},
              {'address': 304552, 'original': 4294906324}],
  'boundary': [{'address': 303798,
                'bytes': '57f6472a000b0009',
                'source': 'tools/sh-elf-run/publication_inhibit_snapshot_return.s'}]},
 {'id': 'metric',
  'parent': 303672,
  'entry': 303798,
  'assembly': 'tools/sh-elf-run/stock_jk08a_knock_metric.s',
  'code': [{'start': 303798, 'end': 303854},
           {'start': 304278, 'end': 304328},
           {'start': 302472, 'end': 302742},
           {'start': 302742, 'end': 303040},
           {'start': 139708, 'end': 139734},
           {'start': 139744, 'end': 139768}],
  'pools': [{'address': 303040,
             'size': 60,
             'stock_hex': '00008618000221bc0000887000008b3dffff1ff4ffff2274ffff2158ffff11d4000086a700008694000086ac7fffffffffff21f8ffff21d800008000'},
            {'address': 304328, 'size': 4, 'stock_hex': '00008b3d'},
            {'address': 304332, 'size': 4, 'stock_hex': 'ffff11d4'},
            {'address': 304336, 'size': 4, 'stock_hex': 'ffff1ff4'},
            {'address': 304344, 'size': 4, 'stock_hex': 'ffff20c2'},
            {'address': 304348, 'size': 4, 'stock_hex': 'ffff2178'},
            {'address': 304352, 'size': 4, 'stock_hex': 'ffff2158'},
            {'address': 139676,
             'size': 32,
             'stock_hex': '0e0c0a0806040200201e1c1a181614123432302e2c2a2826403e3c3a4856626c'},
            {'address': 139736, 'size': 8, 'stock_hex': '000221e60002219c'},
            {'address': 303692, 'size': 12, 'stock_hex': 'd29e6020c90820088d026b03'},
            {'address': 303766, 'size': 2, 'stock_hex': 'd690'},
            {'address': 303772, 'size': 2, 'stock_hex': '2f62'},
            {'address': 304090, 'size': 2, 'stock_hex': 'd63f'},
            {'address': 304096, 'size': 2, 'stock_hex': '2f62'},
            {'address': 34328, 'size': 1, 'stock_hex': '00'},
            {'address': 34928, 'size': 1, 'stock_hex': '03'},
            {'address': 35645, 'size': 1, 'stock_hex': '82'},
            {'address': 34471, 'size': 1, 'stock_hex': '80'},
            {'address': 34452, 'size': 1, 'stock_hex': '80'},
            {'address': 34476, 'size': 1, 'stock_hex': '80'}],
  'aliases': [{'address': 303056, 'original': 4294909940},
              {'address': 303060, 'original': 4294910580},
              {'address': 303064, 'original': 4294910296},
              {'address': 303068, 'original': 4294906324},
              {'address': 303088, 'original': 4294910456},
              {'address': 303092, 'original': 4294910424},
              {'address': 304332, 'original': 4294906324},
              {'address': 304336, 'original': 4294909940},
              {'address': 304344, 'original': 4294910146},
              {'address': 304348, 'original': 4294910328},
              {'address': 304352, 'original': 4294910296}],
  'boundary': [{'address': 303854,
                'bytes': '57f6472a000b0009',
                'source': 'tools/sh-elf-run/publication_inhibit_snapshot_return.s'}]},
 {'id': 'threshold',
  'parent': 303100,
  'entry': 303100,
  'assembly': 'tools/sh-elf-run/stock_jk08a_knock_threshold.s',
  'code': [{'start': 303100, 'end': 303178},
           {'start': 156920, 'end': 156954},
           {'start': 157504, 'end': 157550},
           {'start': 158084, 'end': 158144},
           {'start': 158840, 'end': 158990}],
  'pools': [{'address': 35645, 'size': 1, 'stock_hex': '82'},
            {'address': 69774,
             'size': 194,
             'stock_hex': 'ffff080809800a000a800be40e261066163119001c0020002c0036383d784600ffff04f1068d070008e109330b310d4a10ae12d41500198d23542b3332ae3c6effffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff04bb06f1078008da0a000cbd0f0a1300158019001fdc2e00364a3fa94ddaffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff04e1070008000abb0cb71000118015a61ac01e3b24732f00380042524f5a0000'},
            {'address': 86848,
             'size': 32,
             'stock_hex': '002000400060008000a000c000e00100012001400160018001a001c001e00200'},
            {'address': 156956, 'size': 8, 'stock_hex': '0002674000026984'},
            {'address': 158144, 'size': 4, 'stock_hex': '00026c78'},
            {'address': 303612,
             'size': 28,
             'stock_hex': '00008b3dffff1ff40001108effff11d400015340000264f8ffff2144'}],
  'aliases': [{'address': 303616, 'original': 4294909940},
              {'address': 303624, 'original': 4294906324},
              {'address': 303636, 'original': 4294910276}],
  'boundary': []},
 {'id': 'comparison',
  'parent': 303672,
  'entry': 303854,
  'assembly': 'tools/sh-elf-run/stock_jk08a_knock_comparison.s',
  'code': [{'start': 303854, 'end': 304006},
           {'start': 303100, 'end': 303178},
           {'start': 156920, 'end': 156954},
           {'start': 157504, 'end': 157550},
           {'start': 158084, 'end': 158144},
           {'start': 158840, 'end': 158990},
           {'start': 304126, 'end': 304184},
           {'start': 139708, 'end': 139734},
           {'start': 139744, 'end': 139768}],
  'pools': [{'address': 35645, 'size': 1, 'stock_hex': '82'},
            {'address': 69774,
             'size': 194,
             'stock_hex': 'ffff080809800a000a800be40e261066163119001c0020002c0036383d784600ffff04f1068d070008e109330b310d4a10ae12d41500198d23542b3332ae3c6effffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff04bb06f1078008da0a000cbd0f0a1300158019001fdc2e00364a3fa94ddaffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff04e1070008000abb0cb71000118015a61ac01e3b24732f00380042524f5a0000'},
            {'address': 86848,
             'size': 32,
             'stock_hex': '002000400060008000a000c000e00100012001400160018001a001c001e00200'},
            {'address': 139676,
             'size': 32,
             'stock_hex': '0e0c0a0806040200201e1c1a181614123432302e2c2a2826403e3c3a4856626c'},
            {'address': 139736, 'size': 8, 'stock_hex': '000221e60002219c'},
            {'address': 156956, 'size': 8, 'stock_hex': '0002674000026984'},
            {'address': 158144, 'size': 4, 'stock_hex': '00026c78'},
            {'address': 303612,
             'size': 28,
             'stock_hex': '00008b3dffff1ff40001108effff11d400015340000264f8ffff2144'},
            {'address': 304328, 'size': 12, 'stock_hex': '00008b3dffff11d4ffff1ff4'},
            {'address': 304356, 'size': 16, 'stock_hex': 'ffff21d8ffff2144ffff24c0000221bc'}],
  'aliases': [{'address': 303616, 'original': 4294909940},
              {'address': 303624, 'original': 4294906324},
              {'address': 303636, 'original': 4294910276},
              {'address': 304332, 'original': 4294906324},
              {'address': 304336, 'original': 4294909940},
              {'address': 304356, 'original': 4294910424},
              {'address': 304360, 'original': 4294910276},
              {'address': 304364, 'original': 4294911168}],
  'boundary': [{'address': 304006,
                'bytes': '57f6472a000b0009',
                'source': 'tools/sh-elf-run/publication_inhibit_snapshot_return.s'}]})

KINDS=tuple(unit['id'] for unit in UNITS)
FUNCTIONS=(0x4A238,0x49D88,0x49E96,0x49FFC,0x26984,0x264F8,0x26740,0x26C78,0x221BC,0x221E0,0x21CE0)


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','unit',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-knock-accesses'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or any(value[key] is not False for key in FLAGS) or not test_contract.exact(value['unit'],list(UNITS))):
        raise ValueError('the knock source changes its exact existing units, entry premises or separate boundaries')
    return value


def selection(root,kind):
    source=descriptor(root)
    units=[unit for unit in source['unit'] if unit['id']==kind]
    if len(units)!=1:raise ValueError('the knock capture needs one exact existing software stage')
    unit=units[0]
    entries=[dict(row) for row in unit['code']]
    entries.extend(dict(start=row['address'],end=row['address']+len(bytes.fromhex(row['bytes'])))
                   for row in unit['boundary'])
    return dict(source,unit=units,entry=entries,boundary=list(unit['boundary']))


def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the knock source changes its owned stock image')
    for unit in declared['unit']:
        for row in unit['pools']:
            if image[row['address']:row['address']+row['size']]!=bytes.fromhex(row['stock_hex']):
                raise ValueError('a knock stage changes a declared literal or calibration byte')


def independent_fixture(declared,image):
    require_image(declared,image)
    if len(declared['unit'])!=1:
        raise ValueError('adjacent knock stages require separate image fixtures')
    unit=declared['unit'][0];fixture=bytearray(image);aliases=[]
    for row in unit['aliases']:
        at,original=row['address'],row['original'];alias=0x01000000+(original&65535)
        fixture[at:at+4]=alias.to_bytes(4,'big');aliases.append(dict(address=at,original=original,alias=alias))
    for row in unit['boundary']:
        at=row['address'];data=bytes.fromhex(row['bytes'])
        if (row['source']!=RETURN_SOURCE or row['bytes']!=RETURN_BYTES
                or any(code['start']<at+len(data) and at<code['end'] for code in unit['code'])):
            raise ValueError('a knock observation return changes a tested stock instruction')
        fixture[at:at+len(data)]=data
    for row in unit['code']:
        if fixture[row['start']:row['end']]!=image[row['start']:row['end']]:
            raise ValueError('a knock fixture changes tested instruction bytes')
    return bytes(fixture),aliases
