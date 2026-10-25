"""Exact bounded physical contract; no diagnostic relation is published here."""
import hashlib
from pathlib import Path
import tomllib
from kb import test_contract
DESCRIPTOR='defs/JK08A.bfs-path.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
SPANS=((138464, 138694), (139072, 139310), (140538, 140570), (154084, 154130), (156552, 156570), (157504, 157550), (158340, 158394), (243548, 243896), (243900, 244108), (244184, 244514), (244516, 244674), (244716, 245108))
POOLS={138696: (4, 4294940696), 138700: (4, 1102), 139312: (4, 4294940696), 139316: (4, 1102), 154520: (4, 4294924056), 156570: (2, 240), 156572: (4, 158340), 158396: (4, 157504), 243896: (2, 1831), 243898: (2, 9163), 244108: (4, 4294909420), 244112: (4, 4294918533), 244116: (4, 35968), 244120: (4, 4294918867), 244124: (4, 4294911870), 244128: (4, 4294911072), 244132: (4, 4294906324), 244136: (4, 37508), 244140: (4, 35367), 244144: (4, 35067), 244148: (4, 468729), 244152: (4, 138464), 244156: (4, 139072), 244160: (4, 4294905970), 244164: (4, 156632), 244168: (4, 87600), 244172: (4, 4294906132), 244176: (4, 4294911148), 244180: (4, 4294905928), 244514: (2, 32767), 244676: (4, 33561), 244680: (4, 4294911148), 244684: (4, 33562), 244688: (4, 4294911048), 244692: (4, 4294918732), 244696: (4, 36242), 244700: (4, 154084), 244704: (4, 34394), 244708: (4, 140538), 244712: (4, 4294905928), 245220: (4, 4294906324), 245224: (4, 76958), 245228: (4, 156552), 245232: (4, 4294905892), 245236: (4, 4294905970), 245240: (4, 38734), 245244: (4, 4294925102), 245248: (4, 4294911148), 245252: (4, 4294923700), 245256: (4, 33551), 245260: (4, 140552), 245264: (4, 4294905928), 245268: (4, 38196), 245272: (4, 138464)}
FUNCTIONS=(243548, 138464, 139072, 140552, 154084, 156552, 157504, 158340)
ALIASES={address:value for address,(width,value) in POOLS.items() if width==4 and value>=0xFFFF0000}
FLAGS=('stock_function_stubs','native_relation_publication','scale_admission','all_modes',
       'hardware_qualification','natural_caller_reachability')

def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','assembly','scope','entry','pool','function_entries',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-bfs-path'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or value['assembly']!='tools/sh-elf-run/stock_jk08a_bfs_path.s'
            or any(value[key] is not False for key in FLAGS)
            or not test_contract.exact(value['function_entries'],list(FUNCTIONS))):
        raise ValueError('the bfs-path descriptor changes its exact identity or conditional scope')
    wanted=[dict(key=f'code-{index}',start=start,end=end) for index,(start,end) in enumerate(SPANS)]
    if not test_contract.exact(value['entry'],wanted):
        raise ValueError('the bfs-path descriptor changes an exact instruction span')
    wanted=[dict(address=address,width_bytes=width,stock_value=original,RAM_pointer_alias=address in ALIASES)
            for address,(width,original) in sorted(POOLS.items())]
    if not test_contract.exact(value['pool'],wanted):
        raise ValueError('the bfs-path descriptor changes an exact pool or RAM pointer alias')
    return value

def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the bfs-path source has another owned image')
    used=set()
    for start,end in SPANS:
        for pc in range(start,end,2):
            word=int.from_bytes(image[pc:pc+2],'big')
            if word>>12 in (9,13):
                width=4 if word>>12==13 else 2
                address=((pc&~3) if width==4 else pc)+4+(word&255)*width
                used.add((address,width))
    if used!={(address,width) for address,(width,value) in POOLS.items()}:
        raise ValueError('the bfs-path exact pool inventory differs from its stock instructions')
    for address,(width,value) in POOLS.items():
        if int.from_bytes(image[address:address+width],'big')!=value:
            raise ValueError('the bfs-path source changes a stock literal')

def independent_fixture(declared,image):
    require_image(declared,image)
    fixture=bytearray(image)
    aliases=[]
    for address,original in sorted(ALIASES.items()):
        if any(start<=address<end for start,end in SPANS):
            raise ValueError('an bfs-path alias changes a tested instruction')
        relocated=0x01000000+(original&65535)
        fixture[address:address+4]=relocated.to_bytes(4,'big')
        aliases.append(dict(address=address,original=original,alias=relocated))
    return bytes(fixture),aliases
