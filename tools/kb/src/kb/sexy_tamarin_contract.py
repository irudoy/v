"""Exact natural sexy-tamarin closure; native relation admission is separate."""
import hashlib
from pathlib import Path
import tomllib
from kb import test_contract
DESCRIPTOR='defs/JK08A.sexy-tamarin.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
SPANS=((138172, 138454), (140536, 140552), (156272, 156320), (156788, 156822), (156920, 156954), (157504, 157550), (157768, 157856), (158020, 158080), (158084, 158144), (158840, 158990), (789904, 790082), (790094, 790202), (790272, 790568), (790582, 790866))
POOLS={790208: (4, 4294906508), 790212: (4, 4294906382), 790216: (4, 4294906444), 790220: (4, 75058), 790228: (4, 4294906268), 790232: (4, 77870), 790236: (4, 156788), 790086: (2, 874), 790240: (4, 138172), 790244: (4, 32768), 790088: (2, 2156), 790090: (2, 2112), 790248: (4, 36193), 790202: (2, 2104), 790256: (4, 34737), 790260: (4, 16777215), 790928: (4, 4294906268), 790932: (4, 74746), 790936: (4, 72683), 790568: (2, 842), 790940: (4, 138172), 790570: (2, 2046), 790944: (4, 36193), 790572: (2, 2156), 790574: (2, 2104), 790948: (4, 16777215), 790576: (2, 2176), 790952: (4, 4286578688), 790956: (4, 33596), 790960: (4, 36313), 790964: (4, 8388607), 790578: (2, 2052), 790972: (4, 4294906508), 790580: (2, 572), 790980: (4, 88848), 790984: (4, 84426), 790988: (4, 156920), 790922: (2, 2060), 791012: (4, 62478), 790996: (4, 84362), 791000: (4, 4294910756), 791004: (4, 84394), 791008: (4, 156272), 790924: (2, 2042), 791016: (4, 34714), 791020: (4, 140536), 790992: (4, 62350), 790976: (4, 88784), 790968: (4, 268435455), 790264: (4, 74738), 790268: (4, 72683), 790252: (4, 34736), 790092: (2, 2104), 790224: (4, 75050), 138456: (4, 4294940696), 138460: (4, 1102), 156324: (4, 158084), 156320: (4, 157768), 156828: (4, 158020), 156824: (4, 157504), 156960: (4, 158084), 156956: (4, 157504), 157856: (4, 157504), 158080: (4, 158840), 158144: (4, 158840)}
FUNCTIONS=(138172, 140536, 156272, 156788, 156920, 157504, 157768, 158020, 158084, 158840, 789904)
ALIASES={address:value for address,(width,value) in POOLS.items() if width==4 and value>=0xFFFF0000}
FLAGS=('automatic_resolution', 'datum_identity_inference', 'stock_function_stubs', 'native_relation_publication', 'native_geometry_publication', 'scale_admission', 'hardware_qualification', 'natural_caller_reachability')
ENTRY=0xC0D90
DIVISOR=100


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','assembly','scope','entry','pool','function_entries',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-sexy-tamarin'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or value['assembly']!='tools/sh-elf-run/stock_jk08a_sexy_tamarin.s'
            or any(value[key] is not False for key in FLAGS)
            or not test_contract.exact(value['function_entries'],list(FUNCTIONS))):
        raise ValueError('the sexy-tamarin descriptor changes its exact identity or conditional scope')
    wanted=[dict(key=f'code-{index}',start=start,end=end) for index,(start,end) in enumerate(SPANS)]
    if not test_contract.exact(value['entry'],wanted):
        raise ValueError('the sexy-tamarin descriptor changes an exact instruction span')
    wanted=[dict(address=address,width_bytes=width,stock_value=original,RAM_pointer_alias=address in ALIASES)
            for address,(width,original) in sorted(POOLS.items())]
    if not test_contract.exact(value['pool'],wanted):
        raise ValueError('the sexy-tamarin descriptor changes an exact pool or RAM pointer alias')
    return value


def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the sexy-tamarin source has another owned image')
    used=set()
    for start,end in SPANS:
        for pc in range(start,end,2):
            word=int.from_bytes(image[pc:pc+2],'big')
            if word>>12 in (9,13):
                width=4 if word>>12==13 else 2
                address=((pc&~3) if width==4 else pc)+4+(word&255)*width
                used.add((address,width))
    if used!={(address,width) for address,(width,value) in POOLS.items()}:
        raise ValueError('the sexy-tamarin exact pool inventory differs from its stock instructions')
    for address,(width,value) in POOLS.items():
        if int.from_bytes(image[address:address+width],'big')!=value:
            raise ValueError('the sexy-tamarin source changes a stock literal')
    if int.from_bytes(image[0x26480:0x26482],'big')!=0xE407 or int.from_bytes(image[0x26504:0x26506],'big')!=0xE41E:
        raise ValueError('the sexy-tamarin curve origin changes')


def independent_fixture(declared,image):
    require_image(declared,image)
    fixture=bytearray(image)
    aliases=[]
    for address,original in sorted(ALIASES.items()):
        if any(start<=address<end for start,end in SPANS):
            raise ValueError('a sexy-tamarin alias changes a tested instruction')
        relocated=0x01000000+(original&65535)
        fixture[address:address+4]=relocated.to_bytes(4,'big')
        aliases.append(dict(address=address,original=original,alias=relocated))
    return bytes(fixture),aliases
