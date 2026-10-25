"""Exact reused natural MAF units and explicitly declared pointer relocations."""

import hashlib
from pathlib import Path
import tomllib

from kb import test_contract

DESCRIPTOR = 'defs/JK08A.maf-extended.toml'
IMAGE_SHA256 = 'ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
UNITS = [{'id': 'jk08a-maf-compensation', 'assembly': 'tools/sh-elf-run/stock_jk08a_maf_compensation.s', 'code': [{'start': 241290, 'end': 241474}, {'start': 138464, 'end': 138694}], 'pools': [{'address': 38278, 'size': 2}, {'address': 38284, 'size': 2}, {'address': 138696, 'size': 8}, {'address': 241912, 'size': 20}], 'aliases': [{'address': 138696, 'original': 4294940696, 'alias': 16816152}, {'address': 241912, 'original': 4294916456, 'alias': 16791912}, {'address': 241916, 'original': 4294905880, 'alias': 16781336}, {'address': 241920, 'original': 4294909468, 'alias': 16784924}]}, {'id': 'jk08a-maf-contribution', 'assembly': 'tools/sh-elf-run/stock_jk08a_maf_contribution.s', 'code': [{'start': 241474, 'end': 241816}, {'start': 241818, 'end': 241904}, {'start': 241964, 'end': 242212}, {'start': 140538, 'end': 140552}], 'pools': [{'address': 33462, 'size': 3}, {'address': 33469, 'size': 1}, {'address': 35523, 'size': 1}, {'address': 241816, 'size': 2}, {'address': 241904, 'size': 2}, {'address': 241932, 'size': 32}, {'address': 242556, 'size': 16}], 'aliases': [{'address': 241932, 'original': 4294909420, 'alias': 16784876}, {'address': 241936, 'original': 4294911048, 'alias': 16786504}, {'address': 241940, 'original': 4294911156, 'alias': 16786612}, {'address': 241944, 'original': 4294919111, 'alias': 16794567}, {'address': 241948, 'original': 4294911072, 'alias': 16786528}]}, {'id': 'jk08a-maf-scaling', 'assembly': 'tools/sh-elf-run/stock_jk08a_maf_scaling.s', 'code': [{'start': 236190, 'end': 236270}, {'start': 246792, 'end': 246876}, {'start': 422280, 'end': 422342}, {'start': 422360, 'end': 422402}], 'pools': [{'address': 34808, 'size': 2}, {'address': 37566, 'size': 2}, {'address': 236508, 'size': 2}, {'address': 236716, 'size': 20}, {'address': 246900, 'size': 2}, {'address': 246924, 'size': 16}, {'address': 422342, 'size': 18}, {'address': 422506, 'size': 6}], 'aliases': [{'address': 236716, 'original': 4294909536, 'alias': 16784992}, {'address': 236720, 'original': 4294909236, 'alias': 16784692}, {'address': 236732, 'original': 4294906132, 'alias': 16781588}, {'address': 246928, 'original': 4294909236, 'alias': 16784692}, {'address': 246936, 'original': 4294905880, 'alias': 16781336}, {'address': 422344, 'original': 4294918732, 'alias': 16794188}, {'address': 422348, 'original': 4294919512, 'alias': 16794968}, {'address': 422508, 'original': 4294919512, 'alias': 16794968}]}, {'id': 'jk08a-maf-bank-publication', 'assembly': 'tools/sh-elf-run/stock_jk08a_maf_bank_publication.s', 'code': [{'start': 242212, 'end': 242258}], 'pools': [{'address': 242572, 'size': 16}], 'aliases': [{'address': 242572, 'original': 4294909468, 'alias': 16784924}, {'address': 242576, 'original': 4294909420, 'alias': 16784876}, {'address': 242580, 'original': 4294910768, 'alias': 16786224}, {'address': 242584, 'original': 4294905928, 'alias': 16781384}]}, {'id': 'jk08a-maf-diagnostic-copy', 'assembly': 'tools/sh-elf-run/stock_jk08a_maf_diagnostic_copy.s', 'code': [{'start': 246876, 'end': 246896}], 'pools': [{'address': 246902, 'size': 2}, {'address': 246928, 'size': 4}, {'address': 246940, 'size': 4}], 'aliases': [{'address': 246928, 'original': 4294909236, 'alias': 16784692}, {'address': 246940, 'original': 4294906508, 'alias': 16781964}]}, {'id': 'jk08a-maf-callers', 'assembly': 'tools/sh-elf-run/stock_jk08a_maf_callers.s', 'code': [{'start': 239898, 'end': 239906}, {'start': 246710, 'end': 246718}], 'pools': [], 'aliases': []}]
ENTRIES = (241290, 241474, 246792, 242212, 246876, 239898, 246710, 236190)
FUNCTIONS = (138464, 140536, 241290, 241474, 246792, 422280, 422360, 242212, 246876, 239876, 246700, 236190)
CALL_TARGETS = (138464, 140538, 422280, 422360, 241290, 246792)
SPANS = tuple(sorted((row['start'],row['end']) for unit in UNITS for row in unit['code']))
ALIASES = {row['address']:row['original'] for unit in UNITS for row in unit['aliases']}
FLAGS = ('automatic_resolution','datum_identity_inference','native_relation_publication',
         'native_geometry_publication','scale_admission','units_admission','natural_caller_reachability','hardware_qualification')
STOCK_DATA = {0x82B6:'4d0cff',0x82BD:'2d',0x8AC3:'80',0x9586:'014f',0x958C:'0050',
              0x87F8:'8779',0x92BE:'8000',0x3C476:'07b2'}

CALLERS = ({'parent': 239876, 'entry': 239898, 'end': 239906, 'incoming': {'r12': 0, 'r13': 1, 'r14': 16784924}}, {'parent': 246700, 'entry': 246710, 'end': 246718, 'incoming': {}})
BOUNDARIES = ({'address': 239906, 'bytes': '57f6472a000b0009', 'source': 'tools/sh-elf-run/publication_inhibit_snapshot_return.s', 'return_register': 7, 'stack_return_offset': 24}, {'address': 246718, 'bytes': '57f6472a000b0009', 'source': 'tools/sh-elf-run/publication_inhibit_snapshot_return.s', 'return_register': 7, 'stack_return_offset': 24})


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','natural_entries','normalized_functions','call_targets','unit','caller','boundary',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-maf-extended'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or any(value[key] is not False for key in FLAGS)
            or not test_contract.exact(value['natural_entries'],list(ENTRIES))
            or not test_contract.exact(value['normalized_functions'],list(FUNCTIONS))
            or not test_contract.exact(value['call_targets'],list(CALL_TARGETS))
            or not test_contract.exact(value['caller'],list(CALLERS))
            or not test_contract.exact(value['boundary'],list(BOUNDARIES))
            or not test_contract.exact(value['unit'],UNITS)):
        raise ValueError('the extended MAF source changes an exact reused unit or its admission boundary')
    return dict(value,entry=[dict(start=start,end=end) for start,end in SPANS]+
                [dict(start=row['address'],end=row['address']+len(bytes.fromhex(row['bytes']))) for row in BOUNDARIES])


def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the extended MAF source changes its owned stock image')
    for at,text in STOCK_DATA.items():
        data=bytes.fromhex(text)
        if image[at:at+len(data)]!=data:
            raise ValueError('the extended MAF source changes a stock calibration byte or bound')
    for unit in UNITS:
        pools=unit['pools']
        for span in unit['code']:
            for pc in range(span['start'],span['end'],2):
                word=int.from_bytes(image[pc:pc+2],'big')
                if word>>12 in (9,13):
                    width=4 if word>>12==13 else 2
                    at=((pc&~3) if width==4 else pc)+4+(word&255)*width
                    if not any(row['address']<=at and at+width<=row['address']+row['size'] for row in pools):
                        raise ValueError('an extended MAF unit uses an undeclared PC-relative literal')
        for row in unit['aliases']:
            if (int.from_bytes(image[row['address']:row['address']+4],'big')!=row['original']
                    or row['alias']!=0x01000000+(row['original']&65535)):
                raise ValueError('an extended MAF unit changes its exact RAM pointer relocation')


def independent_fixture(declared,image):
    require_image(declared,image)
    fixture,aliases=bytearray(image),[]
    for at,original in sorted(ALIASES.items()):
        if any(start<at+4 and at<end for start,end in SPANS):
            raise ValueError('an extended MAF alias changes tested stock instructions')
        alias=0x01000000+(original&65535)
        fixture[at:at+4]=alias.to_bytes(4,'big')
        aliases.append(dict(address=at,original=original,alias=alias))
    for row in BOUNDARIES:
        at=row['address'];data=bytes.fromhex(row['bytes'])
        if any(start<at+len(data) and at<end for start,end in SPANS):
            raise ValueError('a MAF observing return changes tested stock instructions')
        fixture[at:at+len(data)]=data
    return bytes(fixture),aliases
