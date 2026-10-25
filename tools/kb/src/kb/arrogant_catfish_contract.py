"""Exact natural arrogant-catfish closure; native relation admission is separate."""
import hashlib
from pathlib import Path
import tomllib
from kb import test_contract
DESCRIPTOR='defs/JK08A.arrogant-catfish.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
SPANS=((138172, 138454), (156552, 156570), (157504, 157550), (158304, 158394), (310254, 310334), (310420, 310712))
POOLS={138456: (4, 4294940696), 138460: (4, 1102), 156570: (2, 240), 156572: (4, 158340), 158396: (4, 157504), 310334: (2, 865), 310336: (2, 866), 310340: (4, 4294906508), 310356: (4, 4294906268), 310364: (4, 156552), 310404: (4, 4294911078), 310408: (4, 74810), 310412: (4, 74850), 310416: (4, 34762), 310712: (2, 865), 310714: (2, 866), 310716: (2, 864), 310718: (2, 863), 310720: (2, 862), 311036: (4, 4294906268), 311040: (4, 74826), 311044: (4, 156552), 311048: (4, 4294906508), 311052: (4, 74866), 311056: (4, 34762), 311060: (4, 73406), 311064: (4, 4294905928), 311068: (4, 138172), 311072: (4, 4294910684)}
FUNCTIONS=(138172, 156552, 157504, 158304, 310254)
ALIASES={310340: 4294906508, 310356: 4294906268, 310404: 4294911078, 311036: 4294906268, 311048: 4294906508, 311064: 4294905928, 311072: 4294910684}
FLAGS=('automatic_resolution', 'datum_identity_inference', 'stock_function_stubs', 'native_relation_publication', 'native_geometry_publication', 'scale_admission', 'hardware_qualification', 'natural_caller_reachability')
ENTRY=0x4BBEE
SITE=0x4BCEC


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','assembly','scope','entry','pool','function_entries',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-arrogant-catfish'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or value['assembly']!='tools/sh-elf-run/stock_jk08a_arrogant_catfish.s'
            or any(value[key] is not False for key in FLAGS)
            or not test_contract.exact(value['function_entries'],list(FUNCTIONS))):
        raise ValueError('the arrogant-catfish descriptor changes its exact identity or conditional scope')
    wanted=[dict(key=f'code-{index}',start=start,end=end) for index,(start,end) in enumerate(SPANS)]
    if not test_contract.exact(value['entry'],wanted):
        raise ValueError('the arrogant-catfish descriptor changes an exact instruction span')
    wanted=[dict(address=address,width_bytes=width,stock_value=original,RAM_pointer_alias=address in ALIASES)
            for address,(width,original) in sorted(POOLS.items())]
    if not test_contract.exact(value['pool'],wanted):
        raise ValueError('the arrogant-catfish descriptor changes an exact pool or RAM pointer alias')
    return value


def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the arrogant-catfish source has another owned image')
    used=set()
    for start,end in SPANS:
        for pc in range(start,end,2):
            word=int.from_bytes(image[pc:pc+2],'big')
            if word>>12 in (9,13):
                width=4 if word>>12==13 else 2
                address=((pc&~3) if width==4 else pc)+4+(word&255)*width
                used.add((address,width))
    if used!={(address,width) for address,(width,value) in POOLS.items()}:
        raise ValueError('the arrogant-catfish exact pool inventory differs from its stock instructions')
    for address,(width,value) in POOLS.items():
        if int.from_bytes(image[address:address+width],'big')!=value:
            raise ValueError('the arrogant-catfish source changes a stock literal')


def independent_fixture(declared,image):
    require_image(declared,image)
    fixture=bytearray(image)
    aliases=[]
    for address,original in sorted(ALIASES.items()):
        if any(start<=address<end for start,end in SPANS):
            raise ValueError('a arrogant-catfish alias changes a tested instruction')
        relocated=0x01000000+(original&65535)
        fixture[address:address+4]=relocated.to_bytes(4,'big')
        aliases.append(dict(address=address,original=original,alias=relocated))
    return bytes(fixture),aliases
