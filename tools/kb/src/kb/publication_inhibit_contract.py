"""Exact bounded physical contract; no diagnostic relation is published here."""
import hashlib
from pathlib import Path
import tomllib
from kb import test_contract
DESCRIPTOR='defs/JK08A.publication-inhibit-path.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
SPANS=((134940, 134970), (140632, 140688), (155168, 155204), (155214, 155336), (156504, 156522), (157504, 157550), (158304, 158394), (254426, 254596), (254608, 254850))
POOLS={135460: (4, 4294905956), 135464: (4, 4294905960), 135468: (4, 4294905958), 135472: (4, 4294905962), 135476: (4, 4294905970), 155408: (4, 4294924056), 156522: (2, 192), 156524: (4, 158332), 158396: (4, 157504), 254906: (2, 1250), 254908: (2, 33987), 254916: (4, 4294906324), 254924: (4, 4294906132), 254928: (4, 4294909520), 254932: (4, 155214), 254936: (4, 4294911156), 254940: (4, 33955), 254944: (4, 4294911065), 254948: (4, 73774), 254952: (4, 156504), 254956: (4, 4294911338), 254960: (4, 4294911057), 254964: (4, 4294905970), 254968: (4, 4294918685), 254972: (4, 4294916548), 254976: (4, 4294911870)}
FUNCTIONS=(134654, 140632, 155168, 155214, 156504, 157504, 158304, 254426)
TABLE={'table': 73774, 'elements': 4, 'element_bytes': 1, 'axis_step': 64, 'RPM': 4294906186, 'cache': 4294911354, 'upstream': 4294905970, 'snapshot': 4294905962, 'mode': 4294911065, 'mode_mask': 32, 'brake': 4294911057, 'brake_mask': 128}
CONTROL={'addresses': [4294935747], 'window_start': 4294935552, 'window_size': 256}
BOUNDARY={'address': 134970, 'bytes': '57f6472a000b0009', 'source': 'tools/sh-elf-run/publication_inhibit_snapshot_return.s', 'return_register': 7, 'stack_return_offset': 24, 'stock_scheduler_body_admitted': False}
ALIASES={address:value for address,(width,value) in POOLS.items() if width==4 and value>=0xFFFF0000}
FLAGS=('stock_function_stubs', 'native_relation_publication', 'native_geometry_publication', 'scale_admission', 'all_modes', 'hardware_qualification', 'natural_caller_reachability')

def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','assembly','scope','entry','pool','function_entries','sequence','table','native_control_bytes','snapshot_return',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-publication-inhibit-path'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or value['assembly']!='tools/sh-elf-run/stock_jk08a_publication_inhibit.s'
            or any(value[key] is not False for key in FLAGS)
            or not test_contract.exact(value['function_entries'],list(FUNCTIONS))):
        raise ValueError('the publication-inhibit descriptor changes its exact identity or conditional scope')
    wanted=[dict(key=f'code-{index}',start=start,end=end) for index,(start,end) in enumerate(SPANS)]
    if not test_contract.exact(value['entry'],wanted):
        raise ValueError('the publication-inhibit descriptor changes an exact instruction span')
    wanted=[dict(address=address,width_bytes=width,stock_value=original,RAM_pointer_alias=address in ALIASES)
            for address,(width,original) in sorted(POOLS.items())]
    if not test_contract.exact(value['pool'],wanted):
        raise ValueError('the publication-inhibit descriptor changes an exact pool or RAM pointer alias')
    for key,expected in (('table',TABLE),('native_control_bytes',CONTROL),('snapshot_return',BOUNDARY)):
        if not test_contract.exact(value[key],expected):
            raise ValueError('the publication-inhibit exact table, native controls or observing return differ')
    if not test_contract.exact(value['sequence'],[0x3E1DA,0x3E1DA,0x20F1C]):
        raise ValueError('the publication-inhibit sequence differs')
    return value

def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the publication-inhibit source has another owned image')
    used=set()
    for start,end in SPANS:
        for pc in range(start,end,2):
            word=int.from_bytes(image[pc:pc+2],'big')
            if word>>12 in (9,13):
                width=4 if word>>12==13 else 2
                address=((pc&~3) if width==4 else pc)+4+(word&255)*width
                used.add((address,width))
    if used!={(address,width) for address,(width,value) in POOLS.items()}:
        raise ValueError('the publication-inhibit exact pool inventory differs from its stock instructions')
    for address,(width,value) in POOLS.items():
        if int.from_bytes(image[address:address+width],'big')!=value:
            raise ValueError('the publication-inhibit source changes a stock literal')

def independent_fixture(declared,image):
    require_image(declared,image)
    fixture=bytearray(image)
    aliases=[]
    for address,original in sorted(ALIASES.items()):
        if any(start<=address<end for start,end in SPANS):
            raise ValueError('an publication-inhibit alias changes a tested instruction')
        relocated=0x01000000+(original&65535)
        fixture[address:address+4]=relocated.to_bytes(4,'big')
        aliases.append(dict(address=address,original=original,alias=relocated))
    at=BOUNDARY['address'];data=bytes.fromhex(BOUNDARY['bytes'])
    if any(start<at+len(data) and at<end for start,end in SPANS) or any(
            address<at+len(data) and at<address+width for address,(width,value) in POOLS.items()):
        raise ValueError('the publication snapshot return overlaps tested stock words or pools')
    original=image[at:at+len(data)]
    fixture[at:at+len(data)]=data
    return bytes(fixture),aliases,[dict(address=at,end=at+len(data),stock=original.hex(),
        bytes=data.hex(),source=BOUNDARY['source'],stock_scheduler_body_admitted=False)]
