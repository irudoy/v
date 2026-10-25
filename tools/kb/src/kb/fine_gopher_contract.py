"""Exact natural fine-gopher closure; native relation admission is separate."""
import hashlib
from pathlib import Path
import tomllib
from kb import test_contract
DESCRIPTOR='defs/JK08A.fine-gopher.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
SPANS=((138464, 138694), (156876, 156910), (157504, 157550), (158084, 158144), (158840, 158990), (394796, 395096), (395100, 395338), (395412, 395658), (395660, 395792))
POOLS={138696: (4, 4294940696), 138700: (4, 1102), 156912: (4, 157504), 156916: (4, 158084), 158144: (4, 158840), 395096: (2, 35924), 395098: (2, 1020), 395338: (2, 1020), 395340: (2, 5019), 395342: (2, 39420), 395344: (4, 4294918533), 395348: (4, 4294906324), 395352: (4, 85826), 395356: (4, 80984), 395360: (4, 156876), 395364: (4, 4294918172), 395368: (4, 85842), 395372: (4, 4294910768), 395376: (4, 83258), 395380: (4, 80952), 395384: (4, 4294905894), 395388: (4, 4294910684), 395392: (4, 138464), 395396: (4, 131586), 395400: (4, 4194240), 395404: (4, 83274), 395408: (4, 36966), 395658: (2, 1071), 395828: (4, 4294905970), 395832: (4, 86018), 395836: (4, 80856), 395840: (4, 37864), 395844: (4, 4294912140), 395848: (4, 86034), 395852: (4, 80872), 395856: (4, 37868), 395860: (4, 4294918718)}
FUNCTIONS=(138464, 156876, 157504, 158084, 158840, 394796)
ALIASES={address:value for address,(width,value) in POOLS.items() if width==4 and value>=0xFFFF0000}
FLAGS=('automatic_resolution', 'datum_identity_inference', 'stock_function_stubs', 'native_relation_publication', 'native_geometry_publication', 'scale_admission', 'hardware_qualification', 'natural_caller_reachability')
ENTRY=0x6062C
GBR_WINDOW=dict(start=0xFFFF8C00, size=256, base=0xFFFF8C54)
BLOCK_WINDOW=dict(start=0xFFFF9900, size=512, base=0xFFFF99FC)
AXES=((0x13C58,0),(0x13C38,0),(0x13BD8,50),(0x13BE8,10))


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','assembly','scope','entry','pool','function_entries','gbr_window','block_window',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-fine-gopher'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or value['assembly']!='tools/sh-elf-run/stock_jk08a_fine_gopher.s'
            or any(value[key] is not False for key in FLAGS)
            or not test_contract.exact(value['function_entries'],list(FUNCTIONS))):
        raise ValueError('the fine-gopher descriptor changes its exact identity or conditional scope')
    wanted=[dict(key=f'code-{index}',start=start,end=end) for index,(start,end) in enumerate(SPANS)]
    if not test_contract.exact(value['entry'],wanted):
        raise ValueError('the fine-gopher descriptor changes an exact instruction span')
    wanted=[dict(address=address,width_bytes=width,stock_value=original,RAM_pointer_alias=address in ALIASES)
            for address,(width,original) in sorted(POOLS.items())]
    if not test_contract.exact(value['pool'],wanted):
        raise ValueError('the fine-gopher descriptor changes an exact pool or RAM pointer alias')
    for key,expected in (('gbr_window',GBR_WINDOW),('block_window',BLOCK_WINDOW)):
        if not test_contract.exact(value[key],expected):
            raise ValueError('the fine-gopher descriptor changes an absolute memory window')
    return value


def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the fine-gopher source has another owned image')
    used=set()
    for start,end in SPANS:
        for pc in range(start,end,2):
            word=int.from_bytes(image[pc:pc+2],'big')
            if word>>12 in (9,13):
                width=4 if word>>12==13 else 2
                address=((pc&~3) if width==4 else pc)+4+(word&255)*width
                used.add((address,width))
    if used!={(address,width) for address,(width,value) in POOLS.items()}:
        raise ValueError('the fine-gopher exact pool inventory differs from its stock instructions')
    for address,(width,value) in POOLS.items():
        if int.from_bytes(image[address:address+width],'big')!=value:
            raise ValueError('the fine-gopher source changes a stock literal')
    for address,first in AXES:
        knots=tuple(int.from_bytes(image[address+offset:address+offset+2],'big') for offset in range(0,16,2))
        if knots[0]!=first or knots[-1]>=65535 or any(left>=right for left,right in zip(knots,knots[1:])):
            raise ValueError('a fine-gopher axis branch premise changes')


def independent_fixture(declared,image):
    require_image(declared,image)
    fixture=bytearray(image)
    aliases=[]
    for address,original in sorted(ALIASES.items()):
        if any(start<=address<end for start,end in SPANS):
            raise ValueError('a fine-gopher alias changes a tested instruction')
        relocated=0x01000000+(original&65535)
        fixture[address:address+4]=relocated.to_bytes(4,'big')
        aliases.append(dict(address=address,original=original,alias=relocated))
    return bytes(fixture),aliases
