"""Exact existing stock copy/filter assembly, aliases and natural returns."""

import hashlib
from pathlib import Path
import tomllib

from kb import test_contract

DESCRIPTOR = 'defs/JK08A.maf-copy-filter.toml'
IMAGE_SHA256 = 'ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
SPANS = ((0x3A982, 0x3A9AA), (0x3A9AA, 0x3AA12))
FUNCTIONS = (0x3A982, 0x3A9AA)
POOLS = {0x870A: (1, 26), 0x3AB68: (4, 0xFFFF1048), 0x3AB70: (4, 0xFFFF1DEC),
         0x3AB74: (4, 0xFFFF2460), 0x3AB78: (4, 0x870A)}
ALIASES = {0x3AB68: 0xFFFF1048, 0x3AB70: 0xFFFF1DEC, 0x3AB74: 0xFFFF2460}
FLAGS = ('automatic_resolution', 'datum_identity_inference', 'stock_function_stubs',
         'native_relation_publication', 'native_geometry_publication', 'scale_admission',
         'hardware_qualification', 'natural_caller_reachability')


def descriptor(root):
    value = tomllib.loads((Path(root) / DESCRIPTOR).read_text())
    if (set(value) != {'schema', 'id', 'layout', 'rom', 'image_sha256', 'assembly', 'scope',
                      'entry', 'pool', 'function_entries', *FLAGS}
            or not test_contract.exact(value['schema'], 1) or value['id'] != 'jk08a-maf-copy-filter'
            or value['layout'] != '7mfk' or value['rom'] != 'JK08A' or value['image_sha256'] != IMAGE_SHA256
            or value['assembly'] != 'tools/sh-elf-run/stock_jk08a_maf_filter.s'
            or any(value[key] is not False for key in FLAGS)
            or not test_contract.exact(value['function_entries'], list(FUNCTIONS))):
        raise ValueError('the MAF copy/filter source changes its exact identity or admission boundary')
    if not test_contract.exact(value['entry'], [dict(key=f'code-{index}', start=start, end=end)
                                               for index, (start, end) in enumerate(SPANS)]):
        raise ValueError('the MAF copy/filter source changes a complete natural instruction span')
    if not test_contract.exact(value['pool'], [dict(address=address, width_bytes=width, stock_value=original,
            RAM_pointer_alias=address in ALIASES) for address, (width, original) in sorted(POOLS.items())]):
        raise ValueError('the MAF copy/filter source changes a literal, coefficient or exact RAM alias')
    return value


def require_image(declared, image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest() != IMAGE_SHA256:
        raise ValueError('the MAF copy/filter original changes its owned stock image')
    used = set()
    for start, end in SPANS:
        for pc in range(start, end, 2):
            word = int.from_bytes(image[pc:pc + 2], 'big')
            if word >> 12 in (9, 13):
                width = 4 if word >> 12 == 13 else 2
                address = ((pc & ~3) if width == 4 else pc) + 4 + (word & 255) * width
                used.add((address, width))
    if used != {(address, width) for address, (width, _) in POOLS.items() if address != 0x870A}:
        raise ValueError('the MAF copy/filter source changes its complete PC-relative literal inventory')
    for address, (width, value) in POOLS.items():
        if int.from_bytes(image[address:address + width], 'big') != value:
            raise ValueError('the MAF copy/filter source changes a stock literal or coefficient byte')


def independent_fixture(declared, image):
    require_image(declared, image)
    fixture, aliases = bytearray(image), []
    for address, original in sorted(ALIASES.items()):
        if any(start <= address < end for start, end in SPANS):
            raise ValueError('a MAF RAM alias changes a tested stock instruction')
        alias = 0x01000000 + (original & 65535)
        fixture[address:address + 4] = alias.to_bytes(4, 'big')
        aliases.append(dict(address=address, original=original, alias=alias))
    return bytes(fixture), aliases
