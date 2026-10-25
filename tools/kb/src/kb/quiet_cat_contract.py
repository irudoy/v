"""Exact natural quiet-cat closure; native relation admission is separate."""
import hashlib
from pathlib import Path
import tomllib
from kb import test_contract
DESCRIPTOR='defs/JK08A.quiet-cat.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
SPANS=((138172, 138454), (155968, 156016), (156788, 156822), (157504, 157550), (157552, 157638), (158020, 158080), (158840, 158990), (779050, 779128), (779134, 779360), (779476, 779708))
POOLS={779360: (2, 872), 779362: (2, 2144), 779364: (2, 840), 779366: (2, 2040), 779388: (4, 4294906508), 779392: (4, 34326), 779396: (4, 40986), 779400: (4, 41114), 779404: (4, 4294906382), 779408: (4, 41178), 779412: (4, 4294911610), 779416: (4, 77862), 779420: (4, 77894), 779424: (4, 41050), 779428: (4, 4294905962), 779432: (4, 4294906268), 779436: (4, 155968), 779440: (4, 138172), 779444: (4, 32768), 779448: (4, 4294906444), 779452: (4, 74730), 779456: (4, 74770), 779460: (4, 72675), 779464: (4, 156788), 779468: (4, 4294911088), 779472: (4, 36196), 779788: (2, 2096), 779790: (2, 2144), 779792: (2, 2034), 779794: (2, 2160), 780092: (4, 34735), 780096: (4, 34740), 780100: (4, 16777215), 780104: (4, 36196), 780108: (4, 34325), 156016: (4, 157552), 156020: (4, 158020), 156824: (4, 157504), 156828: (4, 158020), 138456: (4, 4294940696), 138460: (4, 1102), 158080: (4, 158840), 157640: (4, 157504)}
FUNCTIONS=(138172, 155968, 156788, 157504, 157552, 158020, 158840, 779050)
ALIASES={address:value for address,(width,value) in POOLS.items() if width==4 and value>=0xFFFF0000}
FLAGS=('automatic_resolution', 'datum_identity_inference', 'stock_function_stubs', 'native_relation_publication', 'native_geometry_publication', 'scale_admission', 'hardware_qualification', 'natural_caller_reachability')
ENTRY=0xBE32A
DIVISOR=100


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','assembly','scope','entry','pool','function_entries',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-quiet-cat'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or value['assembly']!='tools/sh-elf-run/stock_jk08a_quiet_cat.s'
            or any(value[key] is not False for key in FLAGS)
            or not test_contract.exact(value['function_entries'],list(FUNCTIONS))):
        raise ValueError('the quiet-cat descriptor changes its exact identity or conditional scope')
    wanted=[dict(key=f'code-{index}',start=start,end=end) for index,(start,end) in enumerate(SPANS)]
    if not test_contract.exact(value['entry'],wanted):
        raise ValueError('the quiet-cat descriptor changes an exact instruction span')
    wanted=[dict(address=address,width_bytes=width,stock_value=original,RAM_pointer_alias=address in ALIASES)
            for address,(width,original) in sorted(POOLS.items())]
    if not test_contract.exact(value['pool'],wanted):
        raise ValueError('the quiet-cat descriptor changes an exact pool or RAM pointer alias')
    return value


def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the quiet-cat source has another owned image')
    used=set()
    for start,end in SPANS:
        for pc in range(start,end,2):
            word=int.from_bytes(image[pc:pc+2],'big')
            if word>>12 in (9,13):
                width=4 if word>>12==13 else 2
                address=((pc&~3) if width==4 else pc)+4+(word&255)*width
                used.add((address,width))
    if used!={(address,width) for address,(width,value) in POOLS.items()}:
        raise ValueError('the quiet-cat exact pool inventory differs from its stock instructions')
    for address,(width,value) in POOLS.items():
        if int.from_bytes(image[address:address+width],'big')!=value:
            raise ValueError('the quiet-cat source changes a stock literal')
    if int.from_bytes(image[0x26480:0x26482],'big')!=0xE407:
        raise ValueError('the quiet-cat byte-curve origin changes')


def independent_fixture(declared,image):
    require_image(declared,image)
    fixture=bytearray(image)
    aliases=[]
    for address,original in sorted(ALIASES.items()):
        if any(start<=address<end for start,end in SPANS):
            raise ValueError('a quiet-cat alias changes a tested instruction')
        relocated=0x01000000+(original&65535)
        fixture[address:address+4]=relocated.to_bytes(4,'big')
        aliases.append(dict(address=address,original=original,alias=relocated))
    return bytes(fixture),aliases
