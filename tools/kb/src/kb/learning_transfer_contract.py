"""Exact reused learned-grid stock units; native admission remains separate."""

import hashlib
from pathlib import Path
import tomllib

from kb import test_contract

DESCRIPTOR='defs/JK08A.learning-transfers.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
UNITS = [{'id': 'jk08a-learning-selection',
  'assembly': 'tools/sh-elf-run/stock_jk08a_grid_selection.s',
  'code': [{'start': 358764, 'end': 359118},
           {'start': 359120, 'end': 359206},
           {'start': 360594, 'end': 360642},
           {'start': 360680, 'end': 360808},
           {'start': 155168, 'end': 155204}],
  'pools': [{'address': 33692, 'size': 2, 'stock': '6e5a', 'RAM_pointer_alias': False},
            {'address': 34842, 'size': 2, 'stock': '0404', 'RAM_pointer_alias': False},
            {'address': 35061, 'size': 1, 'stock': '00', 'RAM_pointer_alias': False},
            {'address': 35486, 'size': 2, 'stock': '5a6e', 'RAM_pointer_alias': False},
            {'address': 75154, 'size': 8, 'stock': '00151d2840587080', 'RAM_pointer_alias': False},
            {'address': 75484, 'size': 8, 'stock': '00141e2c44586c80', 'RAM_pointer_alias': False},
            {'address': 155408, 'size': 4, 'stock': 'ffff5718', 'RAM_pointer_alias': True},
            {'address': 359118, 'size': 2, 'stock': '0129', 'RAM_pointer_alias': False},
            {'address': 359296, 'size': 4, 'stock': 'ffff1024', 'RAM_pointer_alias': True},
            {'address': 359300, 'size': 4, 'stock': '00012592', 'RAM_pointer_alias': False},
            {'address': 359304, 'size': 4, 'stock': 'ffff130a', 'RAM_pointer_alias': True},
            {'address': 359308, 'size': 4, 'stock': '0000881b', 'RAM_pointer_alias': False},
            {'address': 359312, 'size': 4, 'stock': 'ffff119c', 'RAM_pointer_alias': True},
            {'address': 359316, 'size': 4, 'stock': '000126dc', 'RAM_pointer_alias': False},
            {'address': 359320, 'size': 4, 'stock': '0000881a', 'RAM_pointer_alias': False},
            {'address': 359324, 'size': 4, 'stock': 'ffff4b10', 'RAM_pointer_alias': True},
            {'address': 359328, 'size': 4, 'stock': 'ffff4b90', 'RAM_pointer_alias': True},
            {'address': 359332, 'size': 4, 'stock': '00008a9e', 'RAM_pointer_alias': False},
            {'address': 359336, 'size': 4, 'stock': '00008a9f', 'RAM_pointer_alias': False},
            {'address': 359340, 'size': 4, 'stock': 'ffff41a9', 'RAM_pointer_alias': True},
            {'address': 359344, 'size': 4, 'stock': '00025e20', 'RAM_pointer_alias': False},
            {'address': 359348, 'size': 4, 'stock': 'ffff45a0', 'RAM_pointer_alias': True},
            {'address': 359352, 'size': 4, 'stock': 'ffff49b0', 'RAM_pointer_alias': True},
            {'address': 359356, 'size': 4, 'stock': 'ffff49f0', 'RAM_pointer_alias': True},
            {'address': 359360, 'size': 4, 'stock': 'ffff2306', 'RAM_pointer_alias': True},
            {'address': 361284, 'size': 4, 'stock': '000088f5', 'RAM_pointer_alias': False},
            {'address': 361288, 'size': 4, 'stock': 'ffff134e', 'RAM_pointer_alias': True},
            {'address': 361292, 'size': 4, 'stock': '0000839c', 'RAM_pointer_alias': False},
            {'address': 361296, 'size': 4, 'stock': '0000839d', 'RAM_pointer_alias': False}]},
 {'id': 'jk08a-learning-learning',
  'assembly': 'tools/sh-elf-run/stock_jk08a_grid_learning.s',
  'code': [{'start': 359710, 'end': 359984},
           {'start': 360100, 'end': 360174},
           {'start': 360594, 'end': 360642},
           {'start': 360680, 'end': 360808},
           {'start': 140688, 'end': 140698}],
  'pools': [{'address': 33692, 'size': 2, 'stock': '6e5a', 'RAM_pointer_alias': False},
            {'address': 35061, 'size': 1, 'stock': '00', 'RAM_pointer_alias': False},
            {'address': 35485, 'size': 3, 'stock': '1a5a6e', 'RAM_pointer_alias': False},
            {'address': 76230, 'size': 4, 'stock': '1a1a1008', 'RAM_pointer_alias': False},
            {'address': 359984, 'size': 2, 'stock': '01cb', 'RAM_pointer_alias': False},
            {'address': 360040, 'size': 4, 'stock': 'ffff128c', 'RAM_pointer_alias': True},
            {'address': 360052, 'size': 4, 'stock': 'ffff134e', 'RAM_pointer_alias': True},
            {'address': 360056, 'size': 4, 'stock': 'ffff49b0', 'RAM_pointer_alias': True},
            {'address': 360060, 'size': 4, 'stock': 'ffff49f0', 'RAM_pointer_alias': True},
            {'address': 360064, 'size': 4, 'stock': 'ffff2c21', 'RAM_pointer_alias': True},
            {'address': 360068, 'size': 4, 'stock': '00022590', 'RAM_pointer_alias': False},
            {'address': 360072, 'size': 4, 'stock': '000129c6', 'RAM_pointer_alias': False},
            {'address': 360076, 'size': 4, 'stock': 'ffff130a', 'RAM_pointer_alias': True},
            {'address': 360080, 'size': 4, 'stock': '00008a9d', 'RAM_pointer_alias': False},
            {'address': 360084, 'size': 4, 'stock': 'ffff22dc', 'RAM_pointer_alias': True},
            {'address': 360088, 'size': 4, 'stock': 'ffff2306', 'RAM_pointer_alias': True},
            {'address': 360092, 'size': 4, 'stock': '00008a9f', 'RAM_pointer_alias': False},
            {'address': 360096, 'size': 4, 'stock': '00008a9e', 'RAM_pointer_alias': False},
            {'address': 360644, 'size': 4, 'stock': 'ffff4b90', 'RAM_pointer_alias': True},
            {'address': 360648, 'size': 4, 'stock': 'ffff49f0', 'RAM_pointer_alias': True},
            {'address': 360652, 'size': 4, 'stock': 'ffff4b10', 'RAM_pointer_alias': True},
            {'address': 360656, 'size': 4, 'stock': 'ffff49b0', 'RAM_pointer_alias': True},
            {'address': 360660, 'size': 4, 'stock': 'ffff130a', 'RAM_pointer_alias': True},
            {'address': 361284, 'size': 4, 'stock': '000088f5', 'RAM_pointer_alias': False},
            {'address': 361288, 'size': 4, 'stock': 'ffff134e', 'RAM_pointer_alias': True},
            {'address': 361292, 'size': 4, 'stock': '0000839c', 'RAM_pointer_alias': False},
            {'address': 361296, 'size': 4, 'stock': '0000839d', 'RAM_pointer_alias': False}]},
 {'id': 'jk08a-learning-publication',
  'assembly': 'tools/sh-elf-run/stock_jk08a_ltft_publication.s',
  'code': [{'start': 359206, 'end': 359290},
           {'start': 359380, 'end': 359476},
           {'start': 155168, 'end': 155204}],
  'pools': [{'address': 36442, 'size': 1, 'stock': '6e', 'RAM_pointer_alias': False},
            {'address': 36443, 'size': 1, 'stock': '5a', 'RAM_pointer_alias': False},
            {'address': 155408, 'size': 4, 'stock': 'ffff5718', 'RAM_pointer_alias': True},
            {'address': 359290, 'size': 2, 'stock': '0370', 'RAM_pointer_alias': False},
            {'address': 359292, 'size': 2, 'stock': '0372', 'RAM_pointer_alias': False},
            {'address': 359360, 'size': 4, 'stock': 'ffff2306', 'RAM_pointer_alias': True},
            {'address': 359364, 'size': 4, 'stock': 'ffff5648', 'RAM_pointer_alias': True},
            {'address': 359368, 'size': 4, 'stock': 'ffff22f8', 'RAM_pointer_alias': True},
            {'address': 359372, 'size': 4, 'stock': 'ffff128c', 'RAM_pointer_alias': True},
            {'address': 359376, 'size': 4, 'stock': '00008e5b', 'RAM_pointer_alias': False},
            {'address': 359706, 'size': 2, 'stock': '0129', 'RAM_pointer_alias': False},
            {'address': 359988, 'size': 4, 'stock': '00008e5a', 'RAM_pointer_alias': False},
            {'address': 359992, 'size': 4, 'stock': '00025e20', 'RAM_pointer_alias': False},
            {'address': 359996, 'size': 4, 'stock': 'ffff41a9', 'RAM_pointer_alias': True},
            {'address': 360000, 'size': 4, 'stock': 'ffff2470', 'RAM_pointer_alias': True},
            {'address': 360004, 'size': 4, 'stock': 'ffff2302', 'RAM_pointer_alias': True}]}]
ENTRIES = (358764, 359710, 360680, 359206)
FUNCTIONS = (358764, 359710, 360594, 360680, 155168, 140688, 359206)
FLAGS = ('automatic_resolution', 'native_geometry_inference', 'scale_admission', 'units_admission', 'natural_caller_reachability', 'hardware_qualification')
SPANS=tuple(sorted({(row['start'],row['end']) for unit in UNITS for row in unit['code']}))
ALIASES={row['address']:int(row['stock'],16) for unit in UNITS for row in unit['pools'] if row['RAM_pointer_alias']}


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','natural_entries','normalized_functions','unit',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-learning-transfers'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or any(value[flag] is not False for flag in FLAGS)
            or not test_contract.exact(value['natural_entries'],list(ENTRIES))
            or not test_contract.exact(value['normalized_functions'],list(FUNCTIONS))
            or not test_contract.exact(value['unit'],UNITS)):
        raise ValueError('the learned-grid source changes an exact stock unit, entry or admission boundary')
    return dict(value,entry=[dict(start=start,end=end) for start,end in SPANS])


def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the learned-grid source changes its owned stock image')
    for unit in UNITS:
        for row in unit['pools']:
            if image[row['address']:row['address']+row['size']]!=bytes.fromhex(row['stock']):
                raise ValueError('the learned-grid source changes an exact stock literal or calibration')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for at,original in sorted(ALIASES.items()):
        if any(start<at+4 and at<end for start,end in SPANS):
            raise ValueError('a learned-grid RAM alias changes tested stock instructions')
        alias=0x01000000+(original&65535);fixture[at:at+4]=alias.to_bytes(4,'big')
        aliases.append(dict(address=at,original=original,alias=alias))
    return bytes(fixture),aliases
