"""Exact bounded physical contract; no diagnostic relation is published here."""
import hashlib
from pathlib import Path
import tomllib
from kb import test_contract
DESCRIPTOR='defs/JK08A.exhaust-target-path.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
SPANS=((154064, 154084), (786056, 786422), (786536, 786636), (786638, 786918), (786922, 787046), (787108, 787440), (787442, 787688), (787740, 788078), (788088, 788314), (788364, 788614), (788622, 788934), (788996, 789178), (789182, 789584), (789598, 789680), (789716, 789810))
POOLS={786424: (4, 4294906508), 786428: (4, 4294910756), 786448: (4, 4294906268), 786476: (4, 4294911080), 786480: (4, 34529), 786484: (4, 36406), 786488: (4, 154064), 786492: (4, 4294906004), 786496: (4, 34536), 786500: (4, 36334), 786504: (4, 4294911610), 786508: (4, 36392), 786512: (4, 4294906382), 786516: (4, 36374), 786520: (4, 36028), 786524: (4, 4294911338), 786528: (4, 34325), 786532: (4, 35636), 786636: (2, 2515), 786918: (2, 2513), 786920: (2, 2515), 787046: (2, 1736), 787048: (4, 35650), 787052: (4, 4294906004), 787056: (4, 4294905856), 787060: (4, 34078), 787064: (4, 36142), 787068: (4, 36141), 787072: (4, 4294905962), 787076: (4, 4294906508), 787080: (4, 138172), 787084: (4, 4294911055), 787088: (4, 36406), 787092: (4, 4294911182), 787096: (4, 36324), 787100: (4, 36382), 787104: (4, 36393), 787440: (2, 572), 787688: (2, 572), 787690: (2, 1801), 787692: (2, 2564), 787694: (2, 1146), 787696: (4, 4294906382), 787700: (4, 36028), 787704: (4, 4294911225), 787708: (4, 4294906444), 787712: (4, 4294910756), 787716: (4, 34001), 787720: (4, 4294906508), 787724: (4, 33991), 787728: (4, 33546), 787732: (4, 4294906268), 787736: (4, 34035), 788078: (2, 2564), 788080: (2, 2546), 788082: (2, 2125), 788084: (2, 1733), 788086: (2, 1734), 788314: (2, 1734), 788316: (2, 1735), 788318: (2, 1733), 788320: (2, 2125), 788324: (4, 36406), 788328: (4, 36299), 788332: (4, 4294906508), 788336: (4, 4294910756), 788340: (4, 4294906444), 788344: (4, 4294911080), 788348: (4, 4294911182), 788352: (4, 34548), 788356: (4, 36326), 788360: (4, 4294906382), 788614: (2, 1733), 788616: (2, 1734), 788618: (2, 1735), 788620: (2, 2546), 788934: (2, 2546), 788936: (2, 1734), 788938: (2, 1735), 788940: (2, 2536), 788944: (4, 4294906508), 788948: (4, 36028), 788952: (4, 36299), 788956: (4, 34548), 788960: (4, 36406), 788964: (4, 36373), 788968: (4, 4294906268), 788972: (4, 36372), 788976: (4, 4294906382), 788980: (4, 4294906444), 788984: (4, 4294910756), 788988: (4, 4294910762), 788992: (4, 4294911338), 789178: (2, 2546), 789180: (2, 494), 789584: (2, 494), 789586: (2, 2546), 789588: (2, 744), 789590: (2, 736), 789592: (2, 748), 789594: (2, 740), 789596: (2, 2547), 789680: (2, 2562), 789684: (4, 4294911182), 789688: (4, 4294925107), 789692: (4, 4294906508), 789696: (4, 4294906444), 789700: (4, 36434), 789704: (4, 4294919512), 789708: (4, 157052), 789712: (4, 157124), 790082: (2, 2536), 790204: (4, 4294910756), 790208: (4, 4294906508)}
FUNCTIONS=(0xBFE88,0x259D0)
ALIASES={address:value for address,(width,value) in POOLS.items() if width==4 and value>=0xFFFF0000}
FLAGS=('stock_function_stubs','native_relation_publication','scale_admission','all_modes',
       'hardware_qualification','natural_caller_reachability')

def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','assembly','scope','entry','pool','function_entries',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-exhaust-target-path'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or value['assembly']!='tools/sh-elf-run/stock_jk08a_exhaust_target.s'
            or any(value[key] is not False for key in FLAGS)
            or not test_contract.exact(value['function_entries'],list(FUNCTIONS))):
        raise ValueError('the exhaust-target descriptor changes its exact identity or conditional scope')
    wanted=[dict(key=f'code-{index}',start=start,end=end) for index,(start,end) in enumerate(SPANS)]
    if not test_contract.exact(value['entry'],wanted):
        raise ValueError('the exhaust-target descriptor changes an exact instruction span')
    wanted=[dict(address=address,width_bytes=width,stock_value=original,RAM_pointer_alias=address in ALIASES)
            for address,(width,original) in sorted(POOLS.items())]
    if not test_contract.exact(value['pool'],wanted):
        raise ValueError('the exhaust-target descriptor changes an exact pool or RAM pointer alias')
    return value

def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the exhaust-target source has another owned image')
    used=set()
    for start,end in SPANS:
        for pc in range(start,end,2):
            word=int.from_bytes(image[pc:pc+2],'big')
            if word>>12 in (9,13):
                width=4 if word>>12==13 else 2
                address=((pc&~3) if width==4 else pc)+4+(word&255)*width
                used.add((address,width))
    if used!={(address,width) for address,(width,value) in POOLS.items()}:
        raise ValueError('the exhaust-target exact pool inventory differs from its stock instructions')
    for address,(width,value) in POOLS.items():
        if int.from_bytes(image[address:address+width],'big')!=value:
            raise ValueError('the exhaust-target source changes a stock literal')

def independent_fixture(declared,image):
    require_image(declared,image)
    fixture=bytearray(image)
    aliases=[]
    for address,original in sorted(ALIASES.items()):
        if any(start<=address<end for start,end in SPANS):
            raise ValueError('an exhaust-target alias changes a tested instruction')
        relocated=0x01000000+(original&65535)
        fixture[address:address+4]=relocated.to_bytes(4,'big')
        aliases.append(dict(address=address,original=original,alias=relocated))
    return bytes(fixture),aliases
