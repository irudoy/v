"""Exact natural denominator closure; native relation admission is separate."""
import hashlib
from pathlib import Path
import tomllib
from kb import test_contract
DESCRIPTOR='defs/JK08A.timing-denominator.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
SPANS=((138172, 138454), (138464, 138694), (156328, 156376), (156876, 156910), (157224, 157272), (157372, 157406), (157504, 157550), (157768, 157856), (158084, 158144), (158456, 158502), (158504, 158592), (158596, 158656), (158840, 158990), (158992, 159142), (504520, 504750), (504820, 505054))
POOLS={138456: (4, 4294940696), 138460: (4, 1102), 138696: (4, 4294940696), 138700: (4, 1102), 156376: (4, 157768), 156380: (4, 158084), 156912: (4, 157504), 156916: (4, 158084), 157272: (4, 158504), 157276: (4, 158596), 157408: (4, 158456), 157412: (4, 158596), 157856: (4, 157504), 158144: (4, 158840), 158592: (4, 158456), 158656: (4, 158992), 504750: (2, 886), 504752: (2, 1030), 504754: (2, 1029), 504756: (2, 884), 504760: (4, 4294918436), 504764: (4, 33729), 504768: (4, 4294906268), 504772: (4, 51598), 504776: (4, 78968), 504780: (4, 79000), 504784: (4, 156328), 504788: (4, 4294912248), 504792: (4, 84730), 504796: (4, 156876), 504800: (4, 79032), 504804: (4, 4294906004), 504808: (4, 138464), 504812: (4, 138172), 504816: (4, 4294910908), 505054: (2, 2714), 505056: (2, 3290), 505058: (2, 3320), 505060: (2, 3286), 505062: (2, 3288), 505064: (2, 3296), 505066: (2, 3294), 505068: (4, 33729), 505072: (4, 4294906508), 505076: (4, 4294912248), 505080: (4, 4294918569), 505084: (4, 4294918436), 505088: (4, 4294906268), 505092: (4, 92488), 505096: (4, 100422), 505100: (4, 100454), 505104: (4, 157224), 505108: (4, 4294906004), 505112: (4, 101846), 505116: (4, 100486), 505120: (4, 157372), 505124: (4, 138464), 505128: (4, 138172)}
FUNCTIONS=(138172, 138464, 156328, 156876, 157224, 157372, 157504, 157768, 158084, 158456, 158504, 158596, 158840, 158992, 504520, 504820)
ALIASES={address:value for address,(width,value) in POOLS.items() if width==4 and value>=0xFFFF0000}
FLAGS=('automatic_resolution', 'datum_identity_inference', 'stock_function_stubs', 'native_relation_publication', 'native_geometry_publication', 'scale_admission', 'hardware_qualification', 'natural_caller_reachability')
AXES=((0x13478,16),(0x13498,16),(0x18846,16),(0x18866,16),(0x134B8,8),(0x18886,8))

def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','assembly','scope','entry','pool','function_entries',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-timing-denominator'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or value['assembly']!='tools/sh-elf-run/stock_jk08a_timing_denominator.s'
            or any(value[key] is not False for key in FLAGS)
            or not test_contract.exact(value['function_entries'],list(FUNCTIONS))):
        raise ValueError('the timing-denominator descriptor changes its exact identity or conditional scope')
    wanted=[dict(key=f'code-{index}',start=start,end=end) for index,(start,end) in enumerate(SPANS)]
    if not test_contract.exact(value['entry'],wanted):
        raise ValueError('the timing-denominator descriptor changes an exact instruction span')
    wanted=[dict(address=address,width_bytes=width,stock_value=original,RAM_pointer_alias=address in ALIASES)
            for address,(width,original) in sorted(POOLS.items())]
    if not test_contract.exact(value['pool'],wanted):
        raise ValueError('the timing-denominator descriptor changes an exact pool or RAM pointer alias')
    return value

def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the timing-denominator source has another owned image')
    used=set()
    for start,end in SPANS:
        for pc in range(start,end,2):
            word=int.from_bytes(image[pc:pc+2],'big')
            if word>>12 in (9,13):
                width=4 if word>>12==13 else 2
                address=((pc&~3) if width==4 else pc)+4+(word&255)*width
                used.add((address,width))
    if used!={(address,width) for address,(width,value) in POOLS.items()}:
        raise ValueError('the timing-denominator exact pool inventory differs from its stock instructions')
    for address,(width,value) in POOLS.items():
        if int.from_bytes(image[address:address+width],'big')!=value:
            raise ValueError('the timing-denominator source changes a stock literal')
    for address,count in AXES:
        axis=tuple(int.from_bytes(image[address+offset:address+offset+2],'big') for offset in range(0,count*2,2))
        if axis[0]!=0 or axis[-1]>=65535 or any(first>=second for first,second in zip(axis,axis[1:])):
            raise ValueError('the denominator axis branch premises change')

def independent_fixture(declared,image):
    require_image(declared,image)
    fixture=bytearray(image)
    aliases=[]
    for address,original in sorted(ALIASES.items()):
        if any(start<=address<end for start,end in SPANS):
            raise ValueError('a timing-denominator alias changes a tested instruction')
        relocated=0x01000000+(original&65535)
        fixture[address:address+4]=relocated.to_bytes(4,'big')
        aliases.append(dict(address=address,original=original,alias=relocated))
    return bytes(fixture),aliases
