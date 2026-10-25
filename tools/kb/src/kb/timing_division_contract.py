"""Exact timing compositor closure; native relation admission is separate."""
import hashlib
from pathlib import Path
import tomllib
from kb import test_contract
DESCRIPTOR='defs/JK08A.timing-division.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
SPANS=((138464, 138694), (156272, 156320), (156788, 156822), (157504, 157550), (157768, 157856), (158020, 158080), (158084, 158144), (158840, 158990), (310722, 311026))
POOLS={138696: (4, 4294940696), 138700: (4, 1102), 156320: (4, 157768), 156324: (4, 158084), 156824: (4, 157504), 156828: (4, 158020), 157856: (4, 157504), 158080: (4, 158840), 158144: (4, 158840), 311026: (2, 862), 311028: (2, 2033), 311030: (2, 1652), 311032: (2, 1444), 311048: (4, 4294906508), 311076: (4, 4294911064), 311080: (4, 4294910908), 311084: (4, 4294912152), 311088: (4, 4294918569), 311092: (4, 36882), 311096: (4, 4294905960), 311100: (4, 73474), 311104: (4, 73450), 311108: (4, 156788), 311112: (4, 4294905892), 311116: (4, 4294906004), 311120: (4, 50446), 311124: (4, 83482), 311128: (4, 83530), 311132: (4, 156272), 311136: (4, 500000), 311140: (4, 138464), 311144: (4, 4294911182)}
FUNCTIONS=(138464, 156272, 156788, 157504, 157768, 158020, 158084, 158840, 310722)
ALIASES={address:value for address,(width,value) in POOLS.items() if width==4 and value>=0xFFFF0000}
FLAGS=('automatic_resolution', 'datum_identity_inference', 'stock_function_stubs', 'native_relation_publication', 'native_geometry_publication', 'scale_admission', 'hardware_qualification', 'natural_caller_reachability')

def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','assembly','scope','entry','pool','function_entries',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-timing-division'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or value['assembly']!='tools/sh-elf-run/stock_jk08a_timing_division.s'
            or any(value[key] is not False for key in FLAGS)
            or not test_contract.exact(value['function_entries'],list(FUNCTIONS))):
        raise ValueError('the timing-division descriptor changes its exact identity or conditional scope')
    wanted=[dict(key=f'code-{index}',start=start,end=end) for index,(start,end) in enumerate(SPANS)]
    if not test_contract.exact(value['entry'],wanted):
        raise ValueError('the timing-division descriptor changes an exact instruction span')
    wanted=[dict(address=address,width_bytes=width,stock_value=original,RAM_pointer_alias=address in ALIASES)
            for address,(width,original) in sorted(POOLS.items())]
    if not test_contract.exact(value['pool'],wanted):
        raise ValueError('the timing-division descriptor changes an exact pool or RAM pointer alias')
    return value

def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the timing-division source has another owned image')
    used=set()
    for start,end in SPANS:
        for pc in range(start,end,2):
            word=int.from_bytes(image[pc:pc+2],'big')
            if word>>12 in (9,13):
                width=4 if word>>12==13 else 2
                address=((pc&~3) if width==4 else pc)+4+(word&255)*width
                used.add((address,width))
    if used!={(address,width) for address,(width,value) in POOLS.items()}:
        raise ValueError('the timing-division exact pool inventory differs from its stock instructions')
    for address,(width,value) in POOLS.items():
        if int.from_bytes(image[address:address+width],'big')!=value:
            raise ValueError('the timing-division source changes a stock literal')
    for address in (0x1461A,0x1464A):
        axis=tuple(int.from_bytes(image[address+offset:address+offset+2],'big') for offset in range(0,16,2))
        if axis[0]!=0 or axis[-1]>=65535 or any(first>=second for first,second in zip(axis,axis[1:])):
            raise ValueError('the timing word-axis branch premises change')
    axis=image[0x11EEA:0x11EF2]
    if not 0<axis[0]<axis[-1]<255 or any(first>=second for first,second in zip(axis,axis[1:])):
        raise ValueError('the timing byte-axis branch premises change')

def independent_fixture(declared,image):
    require_image(declared,image)
    fixture=bytearray(image)
    aliases=[]
    for address,original in sorted(ALIASES.items()):
        if any(start<=address<end for start,end in SPANS):
            raise ValueError('a timing-division alias changes a tested instruction')
        relocated=0x01000000+(original&65535)
        fixture[address:address+4]=relocated.to_bytes(4,'big')
        aliases.append(dict(address=address,original=original,alias=relocated))
    return bytes(fixture),aliases
