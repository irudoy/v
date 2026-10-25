"""Exact existing precursor/channel units and their simulator pointer premises."""

import hashlib
from pathlib import Path
import tomllib

from kb import test_contract

DESCRIPTOR='defs/JK08A.bank-pulse-stages.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
ENTRIES=(0x4E974,0x4EBA2)
FUNCTIONS=(0x4E974,0x4EBA2,0x21CE0,0x2657C,0x224F8,0x5B7EC)
FLAGS=('automatic_resolution','native_geometry_inference','scale_admission','units_admission',
       'natural_caller_reachability','hardware_qualification')
UNITS=({'id': 'jk08a-pulse-precursor', 'assembly': 'tools/sh-elf-run/stock_jk08a_pulse_precursor.s', 'code': [{'start': 321908, 'end': 322250}, {'start': 138464, 'end': 138694}, {'start': 157052, 'end': 157124}], 'pools': [{'address': 38120, 'size': 2, 'stock_hex': '00aa', 'value': 170, 'RAM_pointer_alias': False}, {'address': 38624, 'size': 4, 'stock_hex': '0012c000', 'value': 1228800, 'RAM_pointer_alias': False}, {'address': 138696, 'size': 4, 'stock_hex': 'ffff9818', 'value': 4294940696, 'RAM_pointer_alias': True}, {'address': 138700, 'size': 4, 'stock_hex': '0000044e', 'value': 1102, 'RAM_pointer_alias': False}, {'address': 322250, 'size': 2, 'stock_hex': '0bfe', 'value': 3070, 'RAM_pointer_alias': False}, {'address': 322252, 'size': 2, 'stock_hex': '06de', 'value': 1758, 'RAM_pointer_alias': False}, {'address': 322254, 'size': 2, 'stock_hex': '0634', 'value': 1588, 'RAM_pointer_alias': False}, {'address': 322256, 'size': 2, 'stock_hex': '03d2', 'value': 978, 'RAM_pointer_alias': False}, {'address': 322258, 'size': 2, 'stock_hex': '05ea', 'value': 1514, 'RAM_pointer_alias': False}, {'address': 322536, 'size': 4, 'stock_hex': 'ffff245c', 'value': 4294911068, 'RAM_pointer_alias': True}, {'address': 322540, 'size': 4, 'stock_hex': 'ffff120e', 'value': 4294906382, 'RAM_pointer_alias': True}, {'address': 322544, 'size': 4, 'stock_hex': 'ffff1024', 'value': 4294905892, 'RAM_pointer_alias': True}, {'address': 322548, 'size': 4, 'stock_hex': 'ffff119c', 'value': 4294906268, 'RAM_pointer_alias': True}, {'address': 322552, 'size': 4, 'stock_hex': '000096e0', 'value': 38624, 'RAM_pointer_alias': False}, {'address': 322556, 'size': 4, 'stock_hex': '00021ce0', 'value': 138464, 'RAM_pointer_alias': False}, {'address': 322560, 'size': 4, 'stock_hex': 'ffff28f8', 'value': 4294912248, 'RAM_pointer_alias': True}, {'address': 322564, 'size': 4, 'stock_hex': 'ffff128c', 'value': 4294906508, 'RAM_pointer_alias': True}, {'address': 322568, 'size': 4, 'stock_hex': 'ffff22dc', 'value': 4294910684, 'RAM_pointer_alias': True}, {'address': 322572, 'size': 4, 'stock_hex': 'ffff40b4', 'value': 4294918324, 'RAM_pointer_alias': True}, {'address': 322576, 'size': 4, 'stock_hex': '0002657c', 'value': 157052, 'RAM_pointer_alias': False}, {'address': 322580, 'size': 4, 'stock_hex': '000094e8', 'value': 38120, 'RAM_pointer_alias': False}]}, {'id': 'jk08a-channel-pulse', 'assembly': 'tools/sh-elf-run/stock_jk08a_channel_pulse.s', 'code': [{'start': 322466, 'end': 322530}, {'start': 322596, 'end': 322732}, {'start': 374764, 'end': 374916}, {'start': 140536, 'end': 140552}], 'pools': [{'address': 36242, 'size': 1, 'stock_hex': '7a', 'value': 122, 'RAM_pointer_alias': False}, {'address': 37338, 'size': 8, 'stock_hex': '35584000109a0000', 'value': 3843892650983424000, 'RAM_pointer_alias': False}, {'address': 76224, 'size': 6, 'stock_hex': '808080808080', 'value': 141289400074368, 'RAM_pointer_alias': False}, {'address': 322568, 'size': 4, 'stock_hex': 'ffff22dc', 'value': 4294910684, 'RAM_pointer_alias': True}, {'address': 322592, 'size': 4, 'stock_hex': 'ffff23bc', 'value': 4294910908, 'RAM_pointer_alias': True}, {'address': 322912, 'size': 8, 'stock_hex': '06920690010a01da', 'value': 473448126389813722, 'RAM_pointer_alias': False}, {'address': 322928, 'size': 20, 'stock_hex': 'ffff128c00008d92000129c0000224f80005b7ec', 'value': 1461480952246385399583435069153390400584129296364, 'RAM_pointer_alias': True}, {'address': 374916, 'size': 4, 'stock_hex': '000091da', 'value': 37338, 'RAM_pointer_alias': False}]})

SPANS=tuple(sorted({(row['start'],row['end']) for unit in UNITS for row in unit['code']}))
POOLS=tuple(dict(row) for at,row in sorted({row['address']:row for unit in UNITS for row in unit['pools']}.items()))
ALIASES={row['address']:int.from_bytes(bytes.fromhex(row['stock_hex'])[:4],'big')
         for row in POOLS if row['RAM_pointer_alias']}
RETURNS=()


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','unit',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-bank-pulse-stages'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or any(value[key] is not False for key in FLAGS) or not test_contract.exact(value['unit'],list(UNITS))):
        raise ValueError('the bank-pulse stages change their exact existing stock units or bounded admission')
    return dict(value,entry=[dict(start=start,end=end) for start,end in SPANS])


def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the bank-pulse stages change their owned stock image')
    for row in POOLS:
        if image[row['address']:row['address']+row['size']]!=bytes.fromhex(row['stock_hex']):
            raise ValueError('a bank-pulse stage changes a declared pointer, scalar or offset literal')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for at,original in ALIASES.items():
        alias=0x01000000+(original&65535)
        fixture[at:at+4]=alias.to_bytes(4,'big');aliases.append(dict(address=at,original=original,alias=alias))
    for start,end in SPANS:
        if fixture[start:end]!=image[start:end]:
            raise ValueError('the bank-pulse stage fixture changes a tested stock instruction')
    return bytes(fixture),aliases
