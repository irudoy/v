"""Exact bounded byte-denominator closure; native relation admission is separate."""
import hashlib
from pathlib import Path
import tomllib
from kb import test_contract
DESCRIPTOR='defs/JK08A.messy-roadrunner.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
SPANS=((138172, 138454), (156788, 156822), (157504, 157550), (158020, 158080), (158840, 158990), (437880, 437948))
POOLS={138456: (4, 4294940696), 138460: (4, 1102), 156824: (4, 157504), 156828: (4, 158020), 158080: (4, 158840), 438114: (2, 32702), 438408: (4, 73530), 438412: (4, 72431), 438416: (4, 156788), 438420: (4, 32833)}
FUNCTIONS=(138172, 156788, 157504, 158020, 158840, 430964)
BOUNDARY={'address': 437948, 'bytes': '57f6472a000b0009', 'source': 'tools/sh-elf-run/messy_roadrunner_return.s', 'return_register': 7, 'stack_return_offset': 24, 'parent_reachability_admitted': False}
ALIASES={}
FLAGS=('automatic_resolution', 'datum_identity_inference', 'stock_function_stubs', 'native_relation_publication', 'native_geometry_publication', 'scale_admission', 'hardware_qualification', 'natural_caller_reachability')

def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','assembly','scope','entry','pool','function_entries','window_entry','observing_return',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-messy-roadrunner'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or value['assembly']!='tools/sh-elf-run/stock_jk08a_messy_roadrunner.s'
            or any(value[key] is not False for key in FLAGS)
            or not test_contract.exact(value['function_entries'],list(FUNCTIONS))):
        raise ValueError('the messy-roadrunner descriptor changes its exact identity or conditional scope')
    wanted=[dict(key=f'code-{index}',start=start,end=end) for index,(start,end) in enumerate(SPANS)]
    if not test_contract.exact(value['entry'],wanted):
        raise ValueError('the messy-roadrunner descriptor changes an exact instruction span')
    wanted=[dict(address=address,width_bytes=width,stock_value=original,RAM_pointer_alias=address in ALIASES)
            for address,(width,original) in sorted(POOLS.items())]
    if not test_contract.exact(value['pool'],wanted):
        raise ValueError('the messy-roadrunner descriptor changes an exact pool or RAM pointer alias')
    if not test_contract.exact(value['window_entry'],0x6AE78) or not test_contract.exact(value['observing_return'],BOUNDARY):
        raise ValueError('the messy-roadrunner entry premise or observing return differs')
    return value

def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the messy-roadrunner source has another owned image')
    used=set()
    for start,end in SPANS:
        for pc in range(start,end,2):
            word=int.from_bytes(image[pc:pc+2],'big')
            if word>>12 in (9,13):
                width=4 if word>>12==13 else 2
                address=((pc&~3) if width==4 else pc)+4+(word&255)*width
                used.add((address,width))
    if used!={(address,width) for address,(width,value) in POOLS.items()}:
        raise ValueError('the messy-roadrunner exact pool inventory differs from its stock instructions')
    for address,(width,value) in POOLS.items():
        if int.from_bytes(image[address:address+width],'big')!=value:
            raise ValueError('the messy-roadrunner source changes a stock literal')

def independent_fixture(declared,image):
    require_image(declared,image)
    fixture=bytearray(image)
    aliases=[]
    for address,original in sorted(ALIASES.items()):
        if any(start<=address<end for start,end in SPANS):
            raise ValueError('a messy-roadrunner alias changes a tested instruction')
        relocated=0x01000000+(original&65535)
        fixture[address:address+4]=relocated.to_bytes(4,'big')
        aliases.append(dict(address=address,original=original,alias=relocated))
    at=BOUNDARY['address'];data=bytes.fromhex(BOUNDARY['bytes'])
    if any(first<at+len(data) and at<last for first,last in SPANS) or any(
            address<at+len(data) and at<address+width for address,(width,value) in POOLS.items()):
        raise ValueError('the messy-roadrunner observing return overlaps a tested stock word or pool')
    original=image[at:at+len(data)];fixture[at:at+len(data)]=data
    return bytes(fixture),aliases,[dict(address=at,end=at+len(data),stock=original.hex(),bytes=data.hex(),
        source=BOUNDARY['source'],parent_reachability_admitted=False)]
