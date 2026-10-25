"""Exact physical boundary of the conditional ignition diagnostic chain.

The descriptor alone admits no execution or native publication.
"""
import hashlib
from pathlib import Path
import tomllib
from kb import test_contract
DESCRIPTOR='defs/JK08A.ignition-diagnostic-path.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
SPANS=((138464, 138694), (156876, 156910), (157504, 157550), (158084, 158144), (158840, 158990), (317852, 318116), (318120, 318364), (318440, 318770), (318774, 318924), (319008, 319062), (319064, 319356), (319362, 319462), (319524, 319616), (574458, 574534))
POOLS={138696: (4, 4294940696), 138700: (4, 1102), 156912: (4, 157504), 156916: (4, 158084), 158144: (4, 158840), 318116: (2, 681), 318118: (2, 632), 318364: (2, 632), 318366: (2, 681), 318368: (4, 4294909940), 318372: (4, 34576), 318376: (4, 4294911168), 318380: (4, 4294906324), 318384: (4, 4294910712), 318388: (4, 4294910908), 318392: (4, 33424), 318396: (4, 4294910768), 318400: (4, 4294911483), 318404: (4, 83930), 318408: (4, 80968), 318412: (4, 156876), 318416: (4, 4294911065), 318420: (4, 35388), 318424: (4, 35389), 318428: (4, 138464), 318432: (4, 4294918348), 318436: (4, 4294906508), 318770: (2, 39364), 318772: (2, 39204), 318924: (4, 33310), 318928: (4, 4294906268), 318932: (4, 4294925105), 318936: (4, 34967), 318940: (4, 34966), 318944: (4, 4294905928), 318948: (4, 34664), 318952: (4, 34663), 318956: (4, 4294905970), 318960: (4, 33749), 318964: (4, 4294906324), 318968: (4, 4294923852), 318972: (4, 4294906508), 318976: (4, 4294911168), 318980: (4, 4294918532), 318984: (4, 4294911176), 318988: (4, 4294911338), 318992: (4, 34668), 318996: (4, 34667), 319000: (4, 34669), 319004: (4, 35407), 319062: (2, 2340), 319356: (2, 2340), 319358: (2, 1243), 319360: (2, 2326), 319464: (4, 35636), 319468: (4, 4294923816), 319472: (4, 4294906132), 319476: (4, 34391), 319480: (4, 4294906324), 319484: (4, 139708), 319488: (4, 4294910768), 319492: (4, 4294905862), 319496: (4, 138172), 319500: (4, 4294909940), 319504: (4, 574458), 319508: (4, 4294911057), 319512: (4, 4294911176), 319516: (4, 33749), 319520: (4, 35989), 319872: (4, 33749), 319876: (4, 4294906324), 319880: (4, 4294911176), 319884: (4, 33770), 319888: (4, 34378), 319892: (4, 4294918732), 319896: (4, 174226), 574538: (2, 3052), 574540: (2, 3054), 574564: (4, 4294912248), 574568: (4, 4294918532), 574572: (4, 4294911055)}
SEQUENCE=(0x4D99C,0x4DBE8,0x4DF82)
HELPERS=(0x264CC,0x26984,0x26740,0x26C78,0x21CE0,0x8C3FA)
ALIASES={address:value for address,(width,value) in POOLS.items() if width==4 and value>=0xFFFF0000}
FLAGS=('native_relation_publication','native_geometry_publication','scale_admission','all_modes',
       'hardware_qualification','natural_caller_reachability')
CURVE=dict(table=0x147DA,axis=0x13C48,wrapper=0x264CC,element_bytes=2,
    last_axis_byte_offset=14,semantic_table_bytes=16,physical_read_extent_bytes=18,
    source=0xFFFF237E,result=0xFFFF2000)
CONTROL=dict(addresses=[0xFFFF99C4,0xFFFF9926],window_start=0xFFFF9900,window_size=256)
DIAGNOSTIC=dict(source=0xFFFF2022,dids=[0x1107,0x1108,0x1109,0x110A,0x113C])
SCHEDULER=dict(address=0x2A892,bytes='e000000b0009',
    source='tools/sh-elf-run/ignition_diagnostic_scheduler_sink.s',return_register=0,return_value=0,
    stock_body_admitted=False,hardware_effects_admitted=False)


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','assembly','scope','entry','pool',
            'sequence','natural_helpers','unadmitted_calls','curve',
            'native_control_bytes','diagnostic','scheduler_boundary',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-ignition-diagnostic-path'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or value['assembly']!='tools/sh-elf-run/stock_jk08a_ignition_diagnostic.s'
            or any(value[key] is not False for key in FLAGS)
            or not test_contract.exact(value['sequence'],list(SEQUENCE))
            or not test_contract.exact(value['natural_helpers'],list(HELPERS))
            or not test_contract.exact(value['unadmitted_calls'],[0x221BC,0x21BBC,0x2A892])):
        raise ValueError('the ignition diagnostic preparation changes its exact source or admission boundary')
    expected=[dict(key=f'code-{index}',start=start,end=end) for index,(start,end) in enumerate(SPANS)]
    if not test_contract.exact(value['entry'],expected):raise ValueError('the ignition diagnostic instruction spans differ')
    expected=[dict(address=address,width_bytes=width,stock_value=original,RAM_pointer_alias=address in ALIASES)
              for address,(width,original) in sorted(POOLS.items())]
    if not test_contract.exact(value['pool'],expected):raise ValueError('the ignition diagnostic exact literal inventory differs')
    for key,expected in (('curve',CURVE),('native_control_bytes',CONTROL),('diagnostic',DIAGNOSTIC),
                         ('scheduler_boundary',SCHEDULER)):
        actual={name:item for name,item in value[key].items() if name!='scope'}
        if not test_contract.exact(actual,expected):raise ValueError('the ignition diagnostic conditional geometry, controls or aliases differ')
    return value


def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the ignition diagnostic source has another owned image')
    if image[0x8290]!=0 or image[0x8B34]&16 or image[0x8B42]&1:
        raise ValueError('the ignition diagnostic normal-mode equations lack their explicit stock configuration premises')
    used=set()
    for start,end in SPANS:
        for pc in range(start,end,2):
            word=int.from_bytes(image[pc:pc+2],'big')
            if word>>12 in (9,13):
                width=4 if word>>12==13 else 2
                address=((pc&~3) if width==4 else pc)+4+(word&255)*width
                used.add((address,width))
    if used!={(address,width) for address,(width,original) in POOLS.items()}:
        raise ValueError('the ignition diagnostic stock code changes its PC-relative pool set')
    for address,(width,original) in POOLS.items():
        if int.from_bytes(image[address:address+width],'big')!=original:
            raise ValueError('the ignition diagnostic source changes a stock literal')
    # Count and physical extent belong to the actual wrapper operands and word-axis stride.
    for address,word in ((0x264D8,0xE40E),(0x264DC,0x364C),(0x264DE,0x8561),
                         (0x264E4,0x6161),(0x269B4,0x74FE)):
        if int.from_bytes(image[address:address+2],'big')!=word:
            raise ValueError('the ignition diagnostic curve bound or physical neighbor access differs')
    if any(address in ALIASES for address in (0x4DD32,0x4DD34)):
        raise ValueError('a native16-bit absolute control address becomes a32-bit pointer alias')


def independent_fixture(declared,image):
    """Keep tested words exact and declare the synthetic post-store boundary."""
    require_image(declared,image)
    fixture=bytearray(image)
    aliases=[]
    for address,original in sorted(ALIASES.items()):
        if any(start<address+4 and address<end for start,end in SPANS):
            raise ValueError('an ignition diagnostic pointer alias changes a tested instruction')
        relocated=0x01000000+(original&65535)
        fixture[address:address+4]=relocated.to_bytes(4,'big')
        aliases.append(dict(address=address,original=original,alias=relocated))
    start=SCHEDULER['address'];data=bytes.fromhex(SCHEDULER['bytes']);end=start+len(data)
    if any(first<end and start<last for first,last in SPANS) or any(
            address<end and start<address+width for address,(width,value) in POOLS.items()):
        raise ValueError('the post-store scheduler sink overlaps a stock instruction or literal under test')
    original=image[start:end]
    fixture[start:end]=data
    boundary=dict(address=start,end=end,stock=original.hex(),bytes=data.hex(),
        source=SCHEDULER['source'],stock_body_admitted=False,hardware_effects_admitted=False)
    return bytes(fixture),aliases,[boundary]
