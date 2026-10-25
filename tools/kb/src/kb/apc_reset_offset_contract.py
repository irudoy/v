"""Exact natural APC reset offset closure; native relation admission is separate."""
import hashlib
from pathlib import Path
import tomllib
from kb import test_contract
DESCRIPTOR='defs/JK08A.apc-reset-offset.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
SPANS=((138172, 138454), (138464, 138694), (156528, 156546), (157504, 157550), (158336, 158394), (311780, 312164), (312172, 312226))
POOLS={138456: (4, 4294940696), 138460: (4, 1102), 138696: (4, 4294940696), 138700: (4, 1102), 156546: (2, 224), 156548: (4, 158336), 158396: (4, 157504), 312164: (2, 1512), 312166: (2, 449), 312168: (2, 453), 312170: (2, 1513), 312298: (2, 1512), 312300: (4, 4294918532), 312304: (4, 34079), 312308: (4, 33425), 312312: (4, 4294906004), 312316: (4, 33418), 312320: (4, 4294906268), 312324: (4, 4294906508), 312328: (4, 38298), 312332: (4, 138464), 312336: (4, 35719), 312340: (4, 73870), 312344: (4, 156528), 312348: (4, 73878), 312352: (4, 81920), 312356: (4, 138172), 312360: (4, 4294910908), 312364: (4, 4294918732)}
FUNCTIONS=(138172, 138464, 156528, 157504, 311780)
ALIASES={address:value for address,(width,value) in POOLS.items() if width==4 and value>=0xFFFF0000}
FLAGS=('automatic_resolution', 'datum_identity_inference', 'stock_function_stubs', 'native_relation_publication', 'native_geometry_publication', 'scale_admission', 'hardware_qualification', 'natural_caller_reachability')
ENTRY=0x4C1E4
DIVISOR=0x14000


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','assembly','scope','entry','pool','function_entries',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-apc-reset-offset'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or value['assembly']!='tools/sh-elf-run/stock_jk08a_apc_reset_offset.s'
            or any(value[key] is not False for key in FLAGS)
            or not test_contract.exact(value['function_entries'],list(FUNCTIONS))):
        raise ValueError('the APC reset descriptor changes its exact identity or conditional scope')
    wanted=[dict(key=f'code-{index}',start=start,end=end) for index,(start,end) in enumerate(SPANS)]
    if not test_contract.exact(value['entry'],wanted):
        raise ValueError('the APC reset descriptor changes an exact instruction span')
    wanted=[dict(address=address,width_bytes=width,stock_value=original,RAM_pointer_alias=address in ALIASES)
            for address,(width,original) in sorted(POOLS.items())]
    if not test_contract.exact(value['pool'],wanted):
        raise ValueError('the APC reset descriptor changes an exact pool or RAM pointer alias')
    return value


def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the APC reset source has another owned image')
    used=set()
    for start,end in SPANS:
        for pc in range(start,end,2):
            word=int.from_bytes(image[pc:pc+2],'big')
            if word>>12 in (9,13):
                width=4 if word>>12==13 else 2
                address=((pc&~3) if width==4 else pc)+4+(word&255)*width
                used.add((address,width))
    if used!={(address,width) for address,(width,value) in POOLS.items()}:
        raise ValueError('the APC reset exact pool inventory differs from its stock instructions')
    for address,(width,value) in POOLS.items():
        if int.from_bytes(image[address:address+width],'big')!=value:
            raise ValueError('the APC reset source changes a stock literal')
    if int.from_bytes(image[0x26370:0x26372],'big')!=0x9007 or int.from_bytes(image[0x26380:0x26382],'big')!=0x8447:
        raise ValueError('the APC reset byte-curve threshold or saturated read changes')


def independent_fixture(declared,image):
    require_image(declared,image)
    fixture=bytearray(image)
    aliases=[]
    for address,original in sorted(ALIASES.items()):
        if any(start<=address<end for start,end in SPANS):
            raise ValueError('an APC reset alias changes a tested instruction')
        relocated=0x01000000+(original&65535)
        fixture[address:address+4]=relocated.to_bytes(4,'big')
        aliases.append(dict(address=address,original=original,alias=relocated))
    return bytes(fixture),aliases
