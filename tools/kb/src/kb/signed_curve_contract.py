"""Exact natural signed-curve closure; native relation admission is separate."""
import hashlib
from pathlib import Path
import tomllib
from kb import test_contract
DESCRIPTOR='defs/JK08A.signed-curve.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
SPANS=((138172, 138454), (157416, 157450), (158456, 158502), (158596, 158656), (158992, 159142), (503968, 504214), (504230, 504460))
POOLS={138456: (4, 4294940696), 138460: (4, 1102), 157452: (4, 158456), 157456: (4, 158596), 158656: (4, 158992), 504214: (2, 3314), 504216: (2, 2708), 504218: (2, 2710), 504220: (2, 2718), 504222: (2, 800), 504224: (2, 3342), 504226: (2, 3344), 504228: (2, 3346), 504460: (2, 800), 504462: (2, 3342), 504464: (2, 3344), 504466: (2, 3346), 504468: (2, 3286), 504472: (4, 4294912248), 504476: (4, 4294918569), 504480: (4, 4294906004), 504484: (4, 101894), 504488: (4, 101926), 504492: (4, 157416), 504496: (4, 101862), 504500: (4, 4294918732), 504504: (4, 138172), 504508: (4, 33729), 504512: (4, 4294911088), 504516: (4, 4294911610)}
FUNCTIONS=(138172, 157416, 158456, 158596, 158992, 503968, 504230)
ALIASES={address:value for address,(width,value) in POOLS.items() if width==4 and value>=0xFFFF0000}
FLAGS=('automatic_resolution', 'datum_identity_inference', 'stock_function_stubs', 'native_relation_publication', 'native_geometry_publication', 'scale_admission', 'hardware_qualification', 'natural_caller_reachability')
ENTRY=0x7B0A0

def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','assembly','scope','entry','pool','function_entries',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-signed-curve'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or value['assembly']!='tools/sh-elf-run/stock_jk08a_signed_curve.s'
            or any(value[key] is not False for key in FLAGS)
            or not test_contract.exact(value['function_entries'],list(FUNCTIONS))):
        raise ValueError('the signed-curve descriptor changes its exact identity or conditional scope')
    wanted=[dict(key=f'code-{index}',start=start,end=end) for index,(start,end) in enumerate(SPANS)]
    if not test_contract.exact(value['entry'],wanted):
        raise ValueError('the signed-curve descriptor changes an exact instruction span')
    wanted=[dict(address=address,width_bytes=width,stock_value=original,RAM_pointer_alias=address in ALIASES)
            for address,(width,original) in sorted(POOLS.items())]
    if not test_contract.exact(value['pool'],wanted):
        raise ValueError('the signed-curve descriptor changes an exact pool or RAM pointer alias')
    return value

def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the signed-curve source has another owned image')
    used=set()
    for start,end in SPANS:
        for pc in range(start,end,2):
            word=int.from_bytes(image[pc:pc+2],'big')
            if word>>12 in (9,13):
                width=4 if word>>12==13 else 2
                address=((pc&~3) if width==4 else pc)+4+(word&255)*width
                used.add((address,width))
    if used!={(address,width) for address,(width,value) in POOLS.items()}:
        raise ValueError('the signed-curve exact pool inventory differs from its stock instructions')
    for address,(width,value) in POOLS.items():
        if int.from_bytes(image[address:address+width],'big')!=value:
            raise ValueError('the signed-curve source changes a stock literal')
    axis=tuple(int.from_bytes(image[0x18E26+offset:0x18E28+offset],'big') for offset in range(0,32,2))
    if axis[0]!=0 or axis[-1]>=65535 or any(first>=second for first,second in zip(axis,axis[1:])):
        raise ValueError('the signed-curve axis branch premises change')

def independent_fixture(declared,image):
    require_image(declared,image)
    fixture=bytearray(image)
    aliases=[]
    for address,original in sorted(ALIASES.items()):
        if any(start<=address<end for start,end in SPANS):
            raise ValueError('a signed-curve alias changes a tested instruction')
        relocated=0x01000000+(original&65535)
        fixture[address:address+4]=relocated.to_bytes(4,'big')
        aliases.append(dict(address=address,original=original,alias=relocated))
    return bytes(fixture),aliases
