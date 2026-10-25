"""Exact natural viridian-armadillo closure; native relation admission is separate."""
import hashlib
from pathlib import Path
import tomllib
from kb import test_contract
DESCRIPTOR='defs/JK08A.viridian-armadillo.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
SPANS=((138172, 138454), (138464, 138694), (156876, 156910), (156920, 156954), (157504, 157550), (158084, 158144), (158840, 158990), (752188, 752378), (752390, 752536))
POOLS={138456: (4, 4294940696), 138460: (4, 1102), 138696: (4, 4294940696), 138700: (4, 1102), 156912: (4, 157504), 156916: (4, 158084), 156956: (4, 157504), 156960: (4, 158084), 158144: (4, 158840), 752382: (2, 20000), 752384: (2, 30267), 752386: (2, 32767), 752388: (2, 2500), 752624: (2, 65281), 752626: (2, 2500), 752628: (2, 2352), 752640: (4, 138172), 752644: (4, 4294901761), 752656: (4, 156920), 752660: (4, 138464), 752664: (4, 4294912248), 752668: (4, 35376), 752672: (4, 4294932028), 752676: (4, 85570), 752680: (4, 80824), 752684: (4, 156876), 752688: (4, 131070), 752692: (4, 34866), 752696: (4, 86514), 752700: (4, 80888)}
FUNCTIONS=(138172, 138464, 156876, 156920, 157504, 158084, 158840, 752188)
ALIASES={752664: 0xFFFF28F8}
FLAGS=('automatic_resolution', 'datum_identity_inference', 'stock_function_stubs', 'native_relation_publication', 'native_geometry_publication', 'scale_admission', 'hardware_qualification', 'natural_caller_reachability')
ENTRY=0xB7A3C
SITE=0xB7AE8
CONSTANT_DIVISOR=0x4E20


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','assembly','scope','entry','pool','function_entries',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-viridian-armadillo'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or value['assembly']!='tools/sh-elf-run/stock_jk08a_viridian_armadillo.s'
            or any(value[key] is not False for key in FLAGS)
            or not test_contract.exact(value['function_entries'],list(FUNCTIONS))):
        raise ValueError('the viridian-armadillo descriptor changes its exact identity or conditional scope')
    wanted=[dict(key=f'code-{index}',start=start,end=end) for index,(start,end) in enumerate(SPANS)]
    if not test_contract.exact(value['entry'],wanted):
        raise ValueError('the viridian-armadillo descriptor changes an exact instruction span')
    wanted=[dict(address=address,width_bytes=width,stock_value=original,RAM_pointer_alias=address in ALIASES)
            for address,(width,original) in sorted(POOLS.items())]
    if not test_contract.exact(value['pool'],wanted):
        raise ValueError('the viridian-armadillo descriptor changes an exact pool or RAM pointer alias')
    return value


def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the viridian-armadillo source has another owned image')
    used=set()
    for start,end in SPANS:
        for pc in range(start,end,2):
            word=int.from_bytes(image[pc:pc+2],'big')
            if word>>12 in (9,13):
                width=4 if word>>12==13 else 2
                address=((pc&~3) if width==4 else pc)+4+(word&255)*width
                used.add((address,width))
    if used!={(address,width) for address,(width,value) in POOLS.items()}:
        raise ValueError('the viridian-armadillo exact pool inventory differs from its stock instructions')
    for address,(width,value) in POOLS.items():
        if int.from_bytes(image[address:address+width],'big')!=value:
            raise ValueError('the viridian-armadillo source changes a stock literal')
    if int.from_bytes(image[0x264D8:0x264DA],'big')!=0xE40E:
        raise ValueError('the viridian-armadillo eight-word curve origin changes')


def independent_fixture(declared,image):
    require_image(declared,image)
    fixture=bytearray(image)
    aliases=[]
    for address,original in sorted(ALIASES.items()):
        if any(start<=address<end for start,end in SPANS):
            raise ValueError('a viridian-armadillo alias changes a tested instruction')
        relocated=0x01000000+(original&65535)
        fixture[address:address+4]=relocated.to_bytes(4,'big')
        aliases.append(dict(address=address,original=original,alias=relocated))
    return bytes(fixture),aliases
