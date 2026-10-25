"""Exact natural independent-leopard closure; native relation admission is separate."""
import hashlib
from pathlib import Path
import tomllib
from kb import test_contract
DESCRIPTOR='defs/JK08A.independent-leopard.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
SPANS=((138464, 138694), (156504, 156522), (157504, 157550), (158332, 158394), (371796, 371906), (372040, 372138))
POOLS={138696: (4, 4294940696), 138700: (4, 1102), 156522: (2, 192), 156524: (4, 158332), 158396: (4, 157504), 372012: (4, 4294912140), 372016: (4, 4294918312), 372020: (4, 4294918308), 372024: (4, 4294918176), 372028: (4, 4294915369), 372032: (4, 75046), 372036: (4, 156504), 372552: (4, 75042), 372556: (4, 156504), 372560: (4, 4294918300), 372564: (4, 138464)}
FUNCTIONS=(138464, 156504, 157504, 371796)
ALIASES={address:value for address,(width,value) in POOLS.items() if width==4 and value>=0xFFFF0000}
FLAGS=('automatic_resolution', 'datum_identity_inference', 'stock_function_stubs', 'native_relation_publication', 'native_geometry_publication', 'scale_admission', 'hardware_qualification', 'natural_caller_reachability')
ENTRY=0x5AC54


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','assembly','scope','entry','pool','function_entries',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-independent-leopard'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or value['assembly']!='tools/sh-elf-run/stock_jk08a_independent_leopard.s'
            or any(value[key] is not False for key in FLAGS)
            or not test_contract.exact(value['function_entries'],list(FUNCTIONS))):
        raise ValueError('the independent-leopard descriptor changes its exact identity or conditional scope')
    wanted=[dict(key=f'code-{index}',start=start,end=end) for index,(start,end) in enumerate(SPANS)]
    if not test_contract.exact(value['entry'],wanted):
        raise ValueError('the independent-leopard descriptor changes an exact instruction span')
    wanted=[dict(address=address,width_bytes=width,stock_value=original,RAM_pointer_alias=address in ALIASES)
            for address,(width,original) in sorted(POOLS.items())]
    if not test_contract.exact(value['pool'],wanted):
        raise ValueError('the independent-leopard descriptor changes an exact pool or RAM pointer alias')
    return value


def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the independent-leopard source has another owned image')
    used=set()
    for start,end in SPANS:
        for pc in range(start,end,2):
            word=int.from_bytes(image[pc:pc+2],'big')
            if word>>12 in (9,13):
                width=4 if word>>12==13 else 2
                address=((pc&~3) if width==4 else pc)+4+(word&255)*width
                used.add((address,width))
    if used!={(address,width) for address,(width,value) in POOLS.items()}:
        raise ValueError('the independent-leopard exact pool inventory differs from its stock instructions')
    for address,(width,value) in POOLS.items():
        if int.from_bytes(image[address:address+width],'big')!=value:
            raise ValueError('the independent-leopard source changes a stock literal')
    if int.from_bytes(image[0x26358:0x2635A],'big')!=0x9007 or int.from_bytes(image[0x26368:0x2636A],'big')!=0x8443:
        raise ValueError('the independent-leopard byte-lookup threshold or saturated read changes')


def independent_fixture(declared,image):
    require_image(declared,image)
    fixture=bytearray(image)
    aliases=[]
    for address,original in sorted(ALIASES.items()):
        if any(start<=address<end for start,end in SPANS):
            raise ValueError('an independent-leopard alias changes a tested instruction')
        relocated=0x01000000+(original&65535)
        fixture[address:address+4]=relocated.to_bytes(4,'big')
        aliases.append(dict(address=address,original=original,alias=relocated))
    return bytes(fixture),aliases
