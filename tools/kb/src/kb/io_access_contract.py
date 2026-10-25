"""Exact bounded software transfers and declared flat native I/O storage."""

import hashlib
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.io-accesses.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
SPANS=((8256, 8282), (683464, 683492), (683678, 683696), (798692, 798744), (798760, 798842))
POOLS={8600: (2, 62496), 684060: (4, 146116), 799134: (2, 55584), 799136: (2, 32752), 799156: (4, 38746)}
FUNCTIONS=(8256, 683460, 798654)
WINDOWS=(('capture', 8256, 8256), ('monitor-prefix', 683464, 683460), ('monitor-read', 683678, 683460), ('mailbox', 798692, 798654))
NATIVE_IO=((4294957312, 1024), (4294964224, 256), (4294964992, 256))
BOUNDARIES=({'address': 8282, 'bytes': '7f0c4f266ef6000b0009', 'source': 'tools/sh-elf-run/io_capture_return.s', 'stack_recovery_bytes': 20, 'kind': 'saved-parent-PR', 'parent_reachability_admitted': False}, {'address': 683496, 'bytes': '7f0857f6472a000b0009', 'source': 'tools/sh-elf-run/io_monitor_return.s', 'stack_recovery_bytes': 8, 'kind': 'observer-slot24', 'parent_reachability_admitted': False}, {'address': 683696, 'bytes': '57f6472a000b0009', 'source': 'tools/sh-elf-run/io_access_return.s', 'stack_recovery_bytes': 0, 'kind': 'observer-slot24', 'parent_reachability_admitted': False}, {'address': 798842, 'bytes': '57f6472a000b0009', 'source': 'tools/sh-elf-run/io_access_return.s', 'stack_recovery_bytes': 0, 'kind': 'observer-slot24', 'parent_reachability_admitted': False})
FLAGS=('automatic_resolution','datum_identity_inference','stock_function_stubs','native_relation_publication',
       'native_geometry_publication','scale_admission','hardware_qualification','natural_caller_reachability',
       'peripheral_side_effects_admission')


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','assembly','scope','entry','pool',
                    'function_entries','window','native_io','observing_return',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-io-accesses'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or value['assembly']!='tools/sh-elf-run/stock_jk08a_io_accesses.s'
            or any(value[key] is not False for key in FLAGS)
            or not test_contract.exact(value['function_entries'],list(FUNCTIONS))):
        raise ValueError('the I/O source changes its exact bounded identity or admission scope')
    if not test_contract.exact(value['entry'],[dict(key=f'code-{i}',start=a,end=b) for i,(a,b) in enumerate(SPANS)]):
        raise ValueError('the I/O source changes an exact stock instruction span')
    if not test_contract.exact(value['pool'],[dict(address=at,width_bytes=width,stock_value=original,RAM_pointer_alias=False)
            for at,(width,original) in sorted(POOLS.items())]):
        raise ValueError('the I/O source changes a literal or introduces an alias')
    if (not test_contract.exact(value['window'],[dict(key=key,entry=entry,parent=parent) for key,entry,parent in WINDOWS])
            or not test_contract.exact(value['native_io'],[dict(start=at,size=size) for at,size in NATIVE_IO])
            or not test_contract.exact(value['observing_return'],list(BOUNDARIES))):
        raise ValueError('the I/O source changes its entry, native storage or observing boundary')
    return value


def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the I/O original changes its owned stock image')
    used=set()
    for start,end in SPANS:
        for pc in range(start,end,2):
            word=int.from_bytes(image[pc:pc+2],'big')
            if word>>12 in (9,13):
                width=4 if word>>12==13 else 2
                at=((pc&~3) if width==4 else pc)+4+(word&255)*width
                used.add((at,width))
    if used!={(at,width) for at,(width,value) in POOLS.items()} or any(
            int.from_bytes(image[at:at+width],'big')!=value for at,(width,value) in POOLS.items()):
        raise ValueError('the I/O original changes its complete exact stock literal inventory')
    if image[0x97BE:0x97C2]!=bytes.fromhex('05000000'):
        raise ValueError('the I/O original changes the stock mailbox26 configuration')
    for selector,mask in ((0,0x0800),(6,0x0004)):
        at=0x23AC4+selector*56
        if (image[at:at+4]!=bytes.fromhex('fffff754')
                or int.from_bytes(image[at+4:at+6],'big')!=mask):
            raise ValueError('the I/O original changes a selected native word pointer or bit mask')


def independent_fixture(declared,image):
    require_image(declared,image)
    fixture=bytearray(image);boundaries=[]
    for row in BOUNDARIES:
        at=row['address'];data=bytes.fromhex(row['bytes'])
        if any(first<at+len(data) and at<last for first,last in SPANS) or any(
                pool<at+len(data) and at<pool+width for pool,(width,value) in POOLS.items()):
            raise ValueError('an I/O observing return overlaps a tested stock word or literal')
        boundaries.append(dict(address=at,end=at+len(data),stock=image[at:at+len(data)].hex(),
            bytes=row['bytes'],source=row['source'],parent_reachability_admitted=False))
        fixture[at:at+len(data)]=data
    return bytes(fixture),[],boundaries
