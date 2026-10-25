"""Exact timing compositor closure; native relation admission is separate."""
import hashlib
from pathlib import Path
import tomllib
from kb import test_contract
DESCRIPTOR='defs/JK08A.timing-tail.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
SPANS=((138464, 138694), (156788, 156822), (156876, 156910), (157504, 157550), (158020, 158080), (158084, 158144), (158840, 158990), (308210, 308360), (308380, 308388))
POOLS={138696: (4, 4294940696), 138700: (4, 1102), 156824: (4, 157504), 156828: (4, 158020), 156912: (4, 157504), 156916: (4, 158084), 158080: (4, 158840), 158144: (4, 158840), 308376: (2, 58186), 308378: (2, 1652), 308500: (4, 4294912152), 308504: (4, 36880), 308508: (4, 73466), 308512: (4, 73450), 308516: (4, 156788), 308520: (4, 4294906004), 308524: (4, 83914), 308528: (4, 83466), 308532: (4, 156876), 308536: (4, 500000), 308540: (4, 138464)}
FUNCTIONS=(138464, 156788, 156876, 157504, 158020, 158084, 158840, 307164)
BOUNDARY={'address': 308388, 'bytes': '57f6472a000b0009', 'source': 'tools/sh-elf-run/timing_tail_return.s', 'return_register': 7, 'stack_return_offset': 24, 'parent_reachability_admitted': False}
ALIASES={address:value for address,(width,value) in POOLS.items() if width==4 and value>=0xFFFF0000}
FLAGS=('automatic_resolution', 'datum_identity_inference', 'stock_function_stubs', 'native_relation_publication', 'native_geometry_publication', 'scale_admission', 'hardware_qualification', 'natural_caller_reachability')

def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','assembly','scope','entry','pool','function_entries','window_entry','observing_return',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-timing-tail'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or value['assembly']!='tools/sh-elf-run/stock_jk08a_timing_tail.s'
            or any(value[key] is not False for key in FLAGS)
            or not test_contract.exact(value['function_entries'],list(FUNCTIONS))):
        raise ValueError('the timing-tail descriptor changes its exact identity or conditional scope')
    wanted=[dict(key=f'code-{index}',start=start,end=end) for index,(start,end) in enumerate(SPANS)]
    if not test_contract.exact(value['entry'],wanted):
        raise ValueError('the timing-tail descriptor changes an exact instruction span')
    wanted=[dict(address=address,width_bytes=width,stock_value=original,RAM_pointer_alias=address in ALIASES)
            for address,(width,original) in sorted(POOLS.items())]
    if not test_contract.exact(value['pool'],wanted):
        raise ValueError('the timing-tail descriptor changes an exact pool or RAM pointer alias')
    if not test_contract.exact(value['window_entry'],0x4B3F2) or not test_contract.exact(value['observing_return'],BOUNDARY):
        raise ValueError('the timing-tail entry premise or observing return differs')
    return value

def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the timing-tail source has another owned image')
    used=set()
    for start,end in SPANS:
        for pc in range(start,end,2):
            word=int.from_bytes(image[pc:pc+2],'big')
            if word>>12 in (9,13):
                width=4 if word>>12==13 else 2
                address=((pc&~3) if width==4 else pc)+4+(word&255)*width
                used.add((address,width))
    if used!={(address,width) for address,(width,value) in POOLS.items()}:
        raise ValueError('the timing-tail exact pool inventory differs from its stock instructions')
    for address,(width,value) in POOLS.items():
        if int.from_bytes(image[address:address+width],'big')!=value:
            raise ValueError('the timing-tail source changes a stock literal')
    axis=tuple(int.from_bytes(image[0x1460A+offset:0x1460C+offset],'big') for offset in range(0,16,2))
    if not 0<axis[0]<axis[-1]<65535 or any(a>=b for a,b in zip(axis,axis[1:])):
        raise ValueError('the timing-tail word-axis branch premises differ')
    axis=image[0x11EEA:0x11EF2]
    if not 0<axis[0]<axis[-1]<255 or any(a>=b for a,b in zip(axis,axis[1:])):
        raise ValueError('the timing-tail byte-axis branch premises differ')
    if int.from_bytes(image[0x9010:0x9012],'big')!=7350:
        raise ValueError('the timing-tail threshold and coefficient-offset premises differ')


def independent_fixture(declared,image):
    require_image(declared,image)
    fixture=bytearray(image)
    aliases=[]
    for address,original in sorted(ALIASES.items()):
        if any(start<=address<end for start,end in SPANS):
            raise ValueError('a timing-tail alias changes a tested instruction')
        relocated=0x01000000+(original&65535)
        fixture[address:address+4]=relocated.to_bytes(4,'big')
        aliases.append(dict(address=address,original=original,alias=relocated))
    at=BOUNDARY['address'];data=bytes.fromhex(BOUNDARY['bytes'])
    if any(first<at+len(data) and at<last for first,last in SPANS) or any(
            address<at+len(data) and at<address+width for address,(width,value) in POOLS.items()):
        raise ValueError('the timing-tail observing return overlaps a tested stock word or pool')
    original=image[at:at+len(data)];fixture[at:at+len(data)]=data
    return bytes(fixture),aliases,[dict(address=at,end=at+len(data),stock=original.hex(),bytes=data.hex(),
        source=BOUNDARY['source'],parent_reachability_admitted=False)]
