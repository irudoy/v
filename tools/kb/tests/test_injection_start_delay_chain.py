"""Bind complete injection start-delay publication to stock bytes and typed owners."""
import ast
import builtins
from collections import Counter
from dataclasses import replace
from fractions import Fraction
from functools import cache
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import sys
from types import SimpleNamespace

import pytest
from kb import compile, derive, repo, research, sh2, store
from kb.arithmetic import Grammar
from kb.model import SymbolKey

TOOL_DIR = repo.ROOT/'tools/sh-elf-run'
KEY = 'jk08a-injection-start-delay'
FN = 'transformed_pulse_maximum/fn'
FUNCTION = SymbolKey('7mfk','fn',0x521a8)
NEW = ('injection_start_delay_decrement/tbl',0x83ea)
HEADER = 'stock-jk08a-injection-start-delay-cases.h'
HARNESS = 'harness-stock-jk08a-injection-start-delay.c'
SPEC = 'defs/JK08A.injection.md'
FUTURE_PATH = 'tools/kb/tests/test_injection_start_delay_chain.py'
OWNER_KEY = 'test_injection_start_delay_chain_owner_contract'
STOCK_KEY = 'test_injection_start_delay_registered_stock_contract'
CODE_SPANS = ((0x521a8,0x52292),(0x21bbc,0x21cd6),(0x21e14,0x21f38))
POOLS = ((0x83ea,1),(0x52296,2),*((at,4) for at in range(0x52298,0x522c4,4)),
         (0x21cd8,4),(0x21cdc,4),(0x21f38,4),(0x21f3c,4))
ALIASES = (0x21cd8,0x21f38,0x52298,0x5229c,0x522a0,0x522a4,0x522ac,0x522b0,0x522c0)
FORMULA = 'F = (uint8(ffff4184)>>6)&1; R = F*uint16(ffff10ca)+(1-F)*uint16(ffff11bc); K = floor(uint32(16*R*50331)/65536); P = uint16(ffff241c); P = max(P,uint16(RAM16[0xffff23d4])); P = max(P,uint16(RAM16[0xffff23d6])); P = max(P,uint16(RAM16[0xffff23d8])); P = max(P,uint16(RAM16[0xffff23da])); P = max(P,uint16(RAM16[0xffff23dc])); P = max(P,uint16(RAM16[0xffff23de])); p = min(255,floor(K*P/65536)); E = uint16(ffff192e); D0 = max(0,2*E-4*p); W = (uint8(ffff24c9)>>5)&1; D = max(0,D0-W*ROM8[0x000083ea]); q = floor(D/120); C = uint8(ffff4251)&1; to = (1-C)*uint8(q)+3*C'
ANGLE_FORMULA = 'F = (uint8(ffff4184)>>6)&1; R = F*uint16(ffff10ca)+(1-F)*uint16(ffff11bc); K = floor(uint32(16*R*50331)/65536); P = uint16(ffff241c); P = max(P,uint16(RAM16[0xffff23d4])); P = max(P,uint16(RAM16[0xffff23d6])); P = max(P,uint16(RAM16[0xffff23d8])); P = max(P,uint16(RAM16[0xffff23da])); P = max(P,uint16(RAM16[0xffff23dc])); P = max(P,uint16(RAM16[0xffff23de])); p = min(255,floor(K*P/65536)); E = uint16(ffff192e); D0 = max(0,2*E-4*p); W = (uint8(ffff24c9)>>5)&1; D = max(0,D0-W*ROM8[0x000083ea]); r = D%120; to = floor(min(116,max(4,r))/4)'
OWNER_DEFINES = {'PRIMARY_SPEED': ('rpm/ram', 4294906300), 'ALTERNATE_SPEED': ('rare-sawfly/ram', 4294906058), 'PULSES': ('handsome-spaniel/ram', 4294910932), 'FLOOR': ('devout-swift/ram', 4294911004), 'END': ('injection_end_angle/ram', 4294908206), 'SPEED_SELECTOR': ('futuristic-chinchilla/ram', 4294918532), 'DELAY_CONTROL': ('apc_mode/ram', 4294911177), 'LEAD_OVERRIDE': ('shaggy-nyala/ram', 4294918737), 'ANGLE_OUTPUT': ('righteous-scorpion/ram', 4294910911), 'LEAD_OUTPUT': ('flat-coyote/ram', 4294910960), 'DELAY_CONFIG': ('injection_start_delay_decrement/tbl', 33770)}
EXISTING = (('amorphous-ape/ram', 4294910908), ('apc_mode/ram', 4294911177), ('devout-swift/ram', 4294911004), ('expert-lion/ram', 4294918732), ('flat-coyote/ram', 4294910960), ('futuristic-chinchilla/ram', 4294918532), ('handsome-spaniel/ram', 4294910932), ('injection_end_angle/ram', 4294908206), ('offbeat-mantis/ram', 4294906268), ('outstanding-marmot/ram', 4294906508), ('pompous-firefly/fn', 138172), ('rare-sawfly/ram', 4294906058), ('righteous-scorpion/ram', 4294910911), ('rpm/ram', 4294906300), ('sage-tapir/fn', 138772), ('shaggy-nyala/ram', 4294918737), ('transformed_pulse_maximum/fn', 336296))
SELECTOR_NOTES = {'bit6': 'For this bounded entry, bit6 set selects unsigned16 word ffff10ca; bit6 clear selects unsigned16 word ffff11bc. Other bits and producers retain their independent evidence.', 'bit5': 'For this bounded entry, bit5 set applies max(0,D0-ROM8[000083ea]) with an unsigned uint8 decrement; bit5 clear retains D0.', 'bit0': 'For this bounded entry, bit0 set publishes ffff23f0=3; bit0 clear publishes uint8(floor(D/120)).'}
SPANS = ((336296, 336530, b'/\xe6O"O\x12O\x13\xd09@\x1e\x7f\xf8\xd69``\xc8@\x89\x03\xd28\xe06\xa0\x03\x06-\xd27\xe0 \x06-fm\xd26F\x08F\x08\x02g\x04\x12\x07\x1at\x18\xee\x00G)\xe5\x06bAb->#\x89\x00n#E\x10\x8f\xf8t\x02\xc50f\r>c\x89\x00nc\x0ew\xe4\xffdL\x02\x1aB)2F\x89\x00d#\xd2\'dL\x90A\x05-bCB\x00e]5#\x89\x01\xa0\x03\xe5\x00E\x00D\x085H\xd6!/R\x84a\xc8 \x89\x07\xd6 b`b,5(E\x11\x89\x00\xe5\x00/R\xd2\x1d\xe0xB\x0baS\xd2\x1ca\xf2\x1f\x01B\x0b\xe0x\xe2\x040#\x8d\x01e\x03\xe5\x04\xe2t5\'\x8b\x00\xe5tE\x11\x8d\x01bSr\x03B!\xd5\x13B!`#\xc0\x03\x84U\xc8\x01\x89\x01\xe6\x03\x1faP\xf1\xc04\x7f\x08O\x17O\x16O&\x00\x0bn\xf6'), (138172, 138454, b'/& \x08\x89V/6!\x07\x03)@\x15\x89\x01p\xff`\x07A\x15\x89\x01q\xffa\x17b\r0 \x8bN\x00\x19@\x180\x16\x8b\x101\x041\x041\x041\x041\x041\x041\x041\x04A$`\x1cC%\x8b\x01`\x07p\x01c\xf6\x00\x0bb\xf6/Fd\x1d@\x18A)1\x041\x041\x041\x041\x041\x041\x041\x041\x041\x041\x041\x041\x041\x041\x041\x04b\x1d!*2.B(1L1\x041\x041\x041\x041\x041\x041\x041\x041\x041\x041\x041\x041\x041\x041\x041\x04A$`\x1d0,C%\x8b\x01`\x07p\x01d\xf6c\xf6\x00\x0bb\xf6\xd1\x19\xd2\x1a!"\xe0\x00\x00\x0bb\xf6\x00\x19b\x1dB(A)B$1\x04B$1\x04B$1\x04B$1\x04B$1\x04B$1\x04B$1\x04B$1\x04B$1\x04B$1\x04B$1\x04B$1\x04B$1\x04B$1\x04B$1\x04B$1\x04B$`#C%\x8b\x01`\x07p\x01c\xf6\x00\x0bb\xf6'), (138772, 139064, b'/& \x08\x89Z/6c\x13C$\x03)@\x15\x89\x01p\xff`\x07A\x15\x89\x01q\xffa\x17b\r0 \x8bQ\x00\x19@\x180\x16\x8b\x131\x041\x041\x041\x041\x041\x041\x041\x04b\x13\x89\x002\x0cB\x19`#C%\x8b\x01`\x07p\x01c\xf6\x00\x0bb\xf6/Fd\x1d@\x18A)1\x041\x041\x041\x041\x041\x041\x041\x041\x041\x041\x041\x041\x041\x041\x041\x04b\x1d!*1L1\x041\x041\x041\x041\x041\x041\x041\x041\x041\x041\x041\x041\x041\x041\x041\x04b\x13\x89\x002\x0c`#@)C%\x8b\x01`\x07p\x01d\xf6c\xf6\x00\x0bb\xf6\xd1\x19\xd2\x1a!"\xe0\x00\x00\x0bb\xf6\x00\x19b\x1dB(A)B$1\x04B$1\x04B$1\x04B$1\x04B$1\x04B$1\x04B$1\x04B$1\x04B$1\x04B$1\x04B$1\x04B$1\x04B$1\x04B$1\x04B$1\x04B$1\x04\x89\x001\x0c`\x13C%\x8b\x01`\x07p\x01c\xf6\x00\x0bb\xf6'), (33770, 33771, b'\x1e'), (336534, 336536, b'\x06\xa2'), (336536, 336540, b'\xff\xff#\xbc'), (336540, 336544, b'\xff\xffA\x84'), (336544, 336548, b'\xff\xff\x10\x94'), (336548, 336552, b'\xff\xff\x11\x9c'), (336552, 336556, b'\x00\x00\xc4\x9b'), (336556, 336560, b'\xff\xff\x12\x8c'), (336560, 336564, b'\xff\xff$\xc8'), (336564, 336568, b'\x00\x00\x83\xea'), (336568, 336572, b'\x00\x02\x1b\xbc'), (336572, 336576, b'\x00\x02\x1e\x14'), (336576, 336580, b'\xff\xffBL'), (138456, 138460, b'\xff\xff\x98\x18'), (138460, 138464, b'\x00\x00\x04N'), (139064, 139068, b'\xff\xff\x98\x18'), (139068, 139072, b'\x00\x00\x04N'))
OWNER_CONTRACTS = json.loads('{"amorphous-ape/ram":{"links":[],"props":{},"symbol":{"address":"ffff23bc","evidence":[],"props":{}}},"apc_mode/ram":{"links":[{"evidence":[{"at":"7mfk:0005222c","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"note":"This bounded consumer reads the raw 7mfk value at its independently owned address; conditions are stated by the function selectors. The input is preserved per case, and producer or hardware-mode reachability is not inferred.","relies":"structure","supports":"identity","to":"transformed_pulse_maximum/fn","type":"reader","via":["transformed_pulse_maximum/fn"]}],"props":{},"symbol":{"address":"ffff24c9","evidence":[{"at":"7mfk:0005222c","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"props":{"signed":false,"width":8}}},"devout-swift/ram":{"links":[{"evidence":[{"at":"7mfk:000521f2","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"reverse_relies":"structure","reverse_supports":"identity","role":"indexed_by","to":"transformed_pulse_maximum/fn","type":"reader"},{"evidence":[{"at":"7mfk:000521f2","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"note":"The exact stock pool and natural consumer bind this address plus the stated byte offset. This is an address-base relation only, without a numeric base-value input, producer, full structure extent or physical claim.","offset":96,"relies":"structure","supports":"identity","to":"amorphous-ape/ram","type":"base","via":["transformed_pulse_maximum/fn"]}],"props":{},"symbol":{"address":"ffff241c","evidence":[{"at":"7mfk:000521f2","kind":"l0","supports":"identity"},{"at":"7mfk:000521f2","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"props":{"signed":false,"width":16}}},"expert-lion/ram":{"links":[],"props":{},"symbol":{"address":"ffff424c","evidence":[],"props":{}}},"flat-coyote/ram":{"links":[{"evidence":[{"at":"7mfk:00052284","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"relies":"structure","reverse_relies":"structure","reverse_supports":"identity","supports":"identity","to":"transformed_pulse_maximum/fn","type":"writer"},{"evidence":[{"at":"7mfk:00052234","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"note":"For this bounded entry, bit5 set applies max(0,D0-ROM8[000083ea]) with an unsigned uint8 decrement; bit5 clear retains D0.","relies":"structure","supports":"identity","to":"injection_start_delay_decrement/tbl","type":"threshold","via":["transformed_pulse_maximum/fn"]},{"evidence":[{"at":"7mfk:000521e2","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"note":"The consumer reads six unsigned16 words at ffff23d4+2*i for i=0..5. P is their maximum and the independently read floor. The common bounded publisher computes both result bytes from live arithmetic; no scheduler readback or upstream transform is executed.","relies":"structure","supports":"identity","to":"handsome-spaniel/ram","type":"input","via":["transformed_pulse_maximum/fn"]},{"evidence":[{"at":"7mfk:000521f2","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"note":"Unsigned16 floor ffff241c participates in P=max(floor,six unsigned pulse words). Its producer, physical scale and scheduler snapshot remain separate facts.","relies":"structure","supports":"identity","to":"devout-swift/ram","type":"input","via":["transformed_pulse_maximum/fn"]},{"evidence":[{"at":"7mfk:00052212","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"note":"Unsigned16 E supplies D0=max(0,2*E-4*p). Full-word quotient-byte wrap prevents a universal monotone sign. Stored lead and angle are separate from the widened helper registers.","relies":"structure","supports":"identity","to":"injection_end_angle/ram","type":"input","via":["transformed_pulse_maximum/fn"]},{"evidence":[{"at":"7mfk:000521ca","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"note":"When speed-selector bit6 is clear, unsigned16 ffff11bc supplies R. K=floor(uint32(16*R*50331)/65536) retains the low32 product wrap. Other selector bits are irrelevant to this numerical choice.","relies":"structure","supports":"identity","to":"rpm/ram","type":"input","via":["transformed_pulse_maximum/fn"]},{"evidence":[{"at":"7mfk:000521c4","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"note":"When speed-selector bit6 is set, unsigned16 ffff10ca supplies R, independently of the unused primary word. K=floor(uint32(16*R*50331)/65536) retains the low32 product wrap.","relies":"structure","supports":"identity","to":"rare-sawfly/ram","type":"input","via":["transformed_pulse_maximum/fn"]},{"evidence":[{"at":"7mfk:00052284","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"note":"The exact stock pool and natural consumer bind this address plus the stated byte offset. This is an address-base relation only, without a numeric base-value input, producer, full structure extent or physical claim.","offset":52,"relies":"structure","supports":"identity","to":"amorphous-ape/ram","type":"base","via":["transformed_pulse_maximum/fn"]}],"props":{},"symbol":{"address":"ffff23f0","evidence":[{"at":"7mfk:00052284","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"props":{"signed":false,"width":8}}},"futuristic-chinchilla/ram":{"links":[{"evidence":[{"at":"7mfk:000521b8","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"note":"This bounded consumer reads the raw 7mfk value at its independently owned address; conditions are stated by the function selectors. The input is preserved per case, and producer or hardware-mode reachability is not inferred.","relies":"structure","supports":"identity","to":"transformed_pulse_maximum/fn","type":"reader","via":["transformed_pulse_maximum/fn"]}],"props":{},"symbol":{"address":"ffff4184","evidence":[{"at":"7mfk:000521b8","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"props":{"signed":false,"width":8}}},"handsome-spaniel/ram":{"links":[{"evidence":[{"at":"7mfk:000521e2","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"relies":"structure","reverse_relies":"structure","reverse_supports":"identity","role":"indexed_by","supports":"identity","to":"transformed_pulse_maximum/fn","type":"reader"},{"evidence":[{"at":"7mfk:000521e2","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"note":"The exact stock pool and natural consumer bind this address plus the stated byte offset. This is an address-base relation only, without a numeric base-value input, producer, full structure extent or physical claim.","offset":24,"relies":"structure","supports":"identity","to":"amorphous-ape/ram","type":"base","via":["transformed_pulse_maximum/fn"]}],"props":{},"symbol":{"address":"ffff23d4","evidence":[{"at":"7mfk:000521e2","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"props":{"signed":false,"width":16}}},"injection_end_angle/ram":{"links":[{"evidence":[{"at":"7mfk:00052212","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"relies":"structure","reverse_relies":"structure","reverse_supports":"identity","role":"indexed_by","supports":"identity","to":"transformed_pulse_maximum/fn","type":"reader"},{"evidence":[{"at":"7mfk:00052212","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"note":"The exact stock pool and natural consumer bind this address plus the stated byte offset. This is an address-base relation only, without a numeric base-value input, producer, full structure extent or physical claim.","offset":1698,"relies":"structure","supports":"identity","to":"outstanding-marmot/ram","type":"base","via":["transformed_pulse_maximum/fn"]}],"props":{},"symbol":{"address":"ffff192e","evidence":[{"at":"7mfk:00052212","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"props":{"signed":false,"width":16}}},"injection_start_delay_decrement/tbl":{"links":[{"evidence":[{"at":"7mfk:00052234","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"note":"For this bounded entry, bit5 set applies max(0,D0-ROM8[000083ea]) with an unsigned uint8 decrement; bit5 clear retains D0.","relies":"structure","supports":"identity","to":"transformed_pulse_maximum/fn","type":"reader","via":["transformed_pulse_maximum/fn"]}],"props":{"block":"injection_timing/block","summary":"7mfk unsigned scalar byte supplying the conditional decrement of the bounded injection start-delay consumer."},"symbol":{"address":"000083ea","evidence":[{"at":"7mfk:00052234","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"props":{"cols":1,"level":"code","note":"MOV.B 00052234 and EXTU.B 00052236 supply an unsigned decrement only when incoming snapshot byte ffff24c9.bit5 is set. The natural consumer clamps its subtraction at zero. Stock value, artificial calibration contexts, other readers and physical purpose are distinct evidence scopes.","rows":1,"signed":false,"storage":"uint8","width":8}}},"offbeat-mantis/ram":{"links":[],"props":{},"symbol":{"address":"ffff119c","evidence":[],"props":{}}},"outstanding-marmot/ram":{"links":[],"props":{},"symbol":{"address":"ffff128c","evidence":[],"props":{}}},"pompous-firefly/fn":{"links":[],"props":{},"symbol":{"address":"00021bbc","evidence":[{"at":"7mfk:00021bbc","kind":"l0","supports":"identity"},{"at":"7mfk:00021bbc","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"props":{}}},"rare-sawfly/ram":{"links":[{"evidence":[{"at":"7mfk:000521c4","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"reverse_relies":"structure","reverse_supports":"identity","role":"indexed_by","to":"transformed_pulse_maximum/fn","type":"reader"}],"props":{},"symbol":{"address":"ffff10ca","evidence":[{"at":"7mfk:000521c4","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"props":{"signed":false,"width":16}}},"righteous-scorpion/ram":{"links":[{"evidence":[{"at":"7mfk:00052276","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"relies":"structure","reverse_relies":"structure","reverse_supports":"identity","supports":"identity","to":"transformed_pulse_maximum/fn","type":"writer"},{"evidence":[{"at":"7mfk:000521e2","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"note":"The consumer reads six unsigned16 words at ffff23d4+2*i for i=0..5. P is their maximum and the independently read floor. The common bounded publisher computes both result bytes from live arithmetic; no scheduler readback or upstream transform is executed.","relies":"structure","supports":"identity","to":"handsome-spaniel/ram","type":"input","via":["transformed_pulse_maximum/fn"]},{"evidence":[{"at":"7mfk:000521f2","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"note":"Unsigned16 floor ffff241c participates in P=max(floor,six unsigned pulse words). Its producer, physical scale and scheduler snapshot remain separate facts.","relies":"structure","supports":"identity","to":"devout-swift/ram","type":"input","via":["transformed_pulse_maximum/fn"]},{"evidence":[{"at":"7mfk:00052212","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"note":"Unsigned16 E supplies D0=max(0,2*E-4*p). The bounded publisher stores floor(min(116,max(4,D%120))/4) in unsigned byte ffff23bf. Remainder periodicity prevents a universal monotone sign; the stored angle is independent of the quotient-byte override. Producer, physical units and scheduler reachability retain their separate evidence.","relies":"structure","supports":"identity","to":"injection_end_angle/ram","type":"input","via":["transformed_pulse_maximum/fn"]},{"evidence":[{"at":"7mfk:000521ca","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"note":"When speed-selector bit6 is clear, unsigned16 ffff11bc supplies R. K=floor(uint32(16*R*50331)/65536) retains the low32 product wrap. Other selector bits are irrelevant to this numerical choice.","relies":"structure","supports":"identity","to":"rpm/ram","type":"input","via":["transformed_pulse_maximum/fn"]},{"evidence":[{"at":"7mfk:000521c4","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"note":"When speed-selector bit6 is set, unsigned16 ffff10ca supplies R, independently of the unused primary word. K=floor(uint32(16*R*50331)/65536) retains the low32 product wrap.","relies":"structure","supports":"identity","to":"rare-sawfly/ram","type":"input","via":["transformed_pulse_maximum/fn"]},{"evidence":[{"at":"7mfk:00052276","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"note":"The exact stock pool and natural consumer bind this address plus the stated byte offset. This is an address-base relation only, without a numeric base-value input, producer, full structure extent or physical claim.","offset":3,"relies":"structure","supports":"identity","to":"amorphous-ape/ram","type":"base","via":["transformed_pulse_maximum/fn"]}],"props":{},"symbol":{"address":"ffff23bf","evidence":[{"at":"7mfk:00052276","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"props":{"signed":false,"width":8}}},"rpm/ram":{"links":[{"evidence":[{"at":"7mfk:000521ca","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"reverse_relies":"structure","reverse_supports":"identity","role":"indexed_by","to":"transformed_pulse_maximum/fn","type":"reader"},{"evidence":[{"at":"7mfk:000521ca","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"note":"The exact stock pool and natural consumer bind this address plus the stated byte offset. This is an address-base relation only, without a numeric base-value input, producer, full structure extent or physical claim.","offset":32,"relies":"structure","supports":"identity","to":"offbeat-mantis/ram","type":"base","via":["transformed_pulse_maximum/fn"]}],"props":{},"symbol":{"address":"ffff11bc","evidence":[{"at":"7mfk:000521ca","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"props":{"signed":false,"width":16}}},"sage-tapir/fn":{"links":[],"props":{},"symbol":{"address":"00021e14","evidence":[{"at":"7mfk:00021e14","kind":"l0","supports":"identity"},{"at":"7mfk:00021e14","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"props":{}}},"shaggy-nyala/ram":{"links":[{"evidence":[{"at":"7mfk:00052278","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"note":"This bounded consumer reads the raw 7mfk value at its independently owned address; conditions are stated by the function selectors. The input is preserved per case, and producer or hardware-mode reachability is not inferred.","relies":"structure","supports":"identity","to":"transformed_pulse_maximum/fn","type":"reader","via":["transformed_pulse_maximum/fn"]},{"evidence":[{"at":"7mfk:00052278","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"note":"The exact stock pool and natural consumer bind this address plus the stated byte offset. This is an address-base relation only, without a numeric base-value input, producer, full structure extent or physical claim.","offset":5,"relies":"structure","supports":"identity","to":"expert-lion/ram","type":"base","via":["transformed_pulse_maximum/fn"]}],"props":{},"symbol":{"address":"ffff4251","evidence":[{"at":"7mfk:00052278","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"props":{"signed":false,"width":8}}},"transformed_pulse_maximum/fn":{"links":[{"evidence":[{"at":"7mfk:000521ba","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"note":"For this bounded entry, bit6 set selects unsigned16 word ffff10ca; bit6 clear selects unsigned16 word ffff11bc. Other bits and producers retain their independent evidence.","relies":"structure","slot":"bit6","supports":"identity","to":"futuristic-chinchilla/ram","type":"selector","via":["transformed_pulse_maximum/fn"]},{"evidence":[{"at":"7mfk:0005222e","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"note":"For this bounded entry, bit5 set applies max(0,D0-ROM8[000083ea]) with an unsigned uint8 decrement; bit5 clear retains D0.","relies":"structure","slot":"bit5","supports":"identity","to":"apc_mode/ram","type":"selector","via":["transformed_pulse_maximum/fn"]},{"evidence":[{"at":"7mfk:0005227a","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"note":"For this bounded entry, bit0 set publishes ffff23f0=3; bit0 clear publishes uint8(floor(D/120)).","relies":"structure","slot":"bit0","supports":"identity","to":"shaggy-nyala/ram","type":"selector","via":["transformed_pulse_maximum/fn"]},{"evidence":[{"at":"7mfk:00052246","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"note":"The natural caller executes the real quotient helper with nonnegative D in 0..131070 and fixed divisor120. Zero numerator, short and long positive branches, calls and natural returns execute. Negative numerator, zero/negative/wide divisor and result-sign correction semantics are identity-only in this caller domain; broad signed helper contracts retain their separate evidence.","relies":"structure","role":"consumer","supports":"identity","to":"pompous-firefly/fn","type":"depends","via":["transformed_pulse_maximum/fn","pompous-firefly/fn"]},{"evidence":[{"at":"7mfk:00052250","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"layouts":["7mfk"],"note":"The natural caller executes the real remainder helper with nonnegative D in 0..131070 and fixed divisor120. Zero numerator, short and long positive branches, calls and natural returns execute. Negative numerator, zero/negative/wide divisor and result-sign correction semantics are identity-only in this caller domain; broad signed helper contracts retain their separate evidence.","relies":"structure","role":"consumer","supports":"identity","to":"sage-tapir/fn","type":"depends","via":["transformed_pulse_maximum/fn","sage-tapir/fn"]}],"props":{"summary":"Complete 7mfk bounded injection start-delay publisher with natural quotient and remainder calls. Five unsigned-word input identities supply the two speed alternatives, six-word maximum, floor and end word. The selected-speed product retains uint32 wrap, the pulse fraction clamps at 255, and nonnegative delay optionally subtracts an unsigned ROM byte. Divisor 120 produces a remainder clamped to 4..116 and a quotient published through uint8 unless a raw control bit forces 3. All full-word input and control-byte domains are explicit consumer contexts. Upstream units, acquisition, scheduling and hardware reachability retain their separate evidence."},"symbol":{"address":"000521a8","evidence":[{"at":"7mfk:000521a8","kind":"l0"},{"key":"test_injection_start_delay_chain_owner_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"test_injection_start_delay_registered_stock_contract","kind":"test","path":"tools/kb/tests/test_injection_start_delay_chain.py"},{"key":"Bounded injection start-delay publication","kind":"spec","path":"defs/JK08A.injection.md"}],"props":{}}}}')
REQUIRED_STEPS = json.loads('{"10":{"effect":"subtracts","from":"handsome-spaniel/ram","note":"F = (uint8(ffff4184)>>6)&1; R = F*uint16(ffff10ca)+(1-F)*uint16(ffff11bc); K = floor(uint32(16*R*50331)/65536); P = uint16(ffff241c); P = max(P,uint16(RAM16[0xffff23d4])); P = max(P,uint16(RAM16[0xffff23d6])); P = max(P,uint16(RAM16[0xffff23d8])); P = max(P,uint16(RAM16[0xffff23da])); P = max(P,uint16(RAM16[0xffff23dc])); P = max(P,uint16(RAM16[0xffff23de])); p = min(255,floor(K*P/65536)); E = uint16(ffff192e); D0 = max(0,2*E-4*p); W = (uint8(ffff24c9)>>5)&1; D = max(0,D0-W*ROM8[0x000083ea]); q = floor(D/120); C = uint8(ffff4251)&1; to = (1-C)*uint8(q)+3*C","sign":"none","to":"flat-coyote/ram","via":["transformed_pulse_maximum/fn"]},"11":{"effect":"scales","from":"rpm/ram","note":"F = (uint8(ffff4184)>>6)&1; R = F*uint16(ffff10ca)+(1-F)*uint16(ffff11bc); K = floor(uint32(16*R*50331)/65536); P = uint16(ffff241c); P = max(P,uint16(RAM16[0xffff23d4])); P = max(P,uint16(RAM16[0xffff23d6])); P = max(P,uint16(RAM16[0xffff23d8])); P = max(P,uint16(RAM16[0xffff23da])); P = max(P,uint16(RAM16[0xffff23dc])); P = max(P,uint16(RAM16[0xffff23de])); p = min(255,floor(K*P/65536)); E = uint16(ffff192e); D0 = max(0,2*E-4*p); W = (uint8(ffff24c9)>>5)&1; D = max(0,D0-W*ROM8[0x000083ea]); q = floor(D/120); C = uint8(ffff4251)&1; to = (1-C)*uint8(q)+3*C","sign":"none","to":"flat-coyote/ram","via":["transformed_pulse_maximum/fn"]},"8":{"effect":"converts","from":"injection_end_angle/ram","note":"F = (uint8(ffff4184)>>6)&1; R = F*uint16(ffff10ca)+(1-F)*uint16(ffff11bc); K = floor(uint32(16*R*50331)/65536); P = uint16(ffff241c); P = max(P,uint16(RAM16[0xffff23d4])); P = max(P,uint16(RAM16[0xffff23d6])); P = max(P,uint16(RAM16[0xffff23d8])); P = max(P,uint16(RAM16[0xffff23da])); P = max(P,uint16(RAM16[0xffff23dc])); P = max(P,uint16(RAM16[0xffff23de])); p = min(255,floor(K*P/65536)); E = uint16(ffff192e); D0 = max(0,2*E-4*p); W = (uint8(ffff24c9)>>5)&1; D = max(0,D0-W*ROM8[0x000083ea]); q = floor(D/120); C = uint8(ffff4251)&1; to = (1-C)*uint8(q)+3*C","sign":"none","to":"flat-coyote/ram","via":["transformed_pulse_maximum/fn"]},"9":{"effect":"converts","from":"injection_end_angle/ram","note":"F = (uint8(ffff4184)>>6)&1; R = F*uint16(ffff10ca)+(1-F)*uint16(ffff11bc); K = floor(uint32(16*R*50331)/65536); P = uint16(ffff241c); P = max(P,uint16(RAM16[0xffff23d4])); P = max(P,uint16(RAM16[0xffff23d6])); P = max(P,uint16(RAM16[0xffff23d8])); P = max(P,uint16(RAM16[0xffff23da])); P = max(P,uint16(RAM16[0xffff23dc])); P = max(P,uint16(RAM16[0xffff23de])); p = min(255,floor(K*P/65536)); E = uint16(ffff192e); D0 = max(0,2*E-4*p); W = (uint8(ffff24c9)>>5)&1; D = max(0,D0-W*ROM8[0x000083ea]); r = D%120; to = floor(min(116,max(4,r))/4)","sign":"none","to":"righteous-scorpion/ram","via":["transformed_pulse_maximum/fn"]}}')
EXECUTION_SOURCES = {'stock_jk08a_injection_start_delay.s': 'f887ab01761ec298155ed8dd400a42ba25a71c14e0912548583af85ebaf60d80', 'harness-stock-jk08a-injection-start-delay.c': 'f7b47c4be99baf27dd10537415456a317261431ec722770c2dd0f41be8fdb46d', 'stock-jk08a-injection-start-delay-cases.h': '5edc27dd9c30c204ccaeedcf9ca5003355d5ce5aa858977ff476657bc12560a1', 'stock_injection_start_delay_invoke.s': '0e60c06fb860bfccde3e166f1d45e4059994026ccd89db9313a5b6d0757d44db'}

def verify_stock(data):
    for start, end, expected in SPANS:
        assert data[start:end] == expected, f'{start:08x}'
    word = lambda address, size=2: int.from_bytes(data[address:address + size], 'big')
    assert [(word(at, 4)) for at in ALIASES] == [
        0xffff9818, 0xffff9818, 0xffff23bc, 0xffff4184, 0xffff1094,
        0xffff119c, 0xffff128c, 0xffff24c8, 0xffff424c]
    assert word(0x52296) == 0x6a2 and word(0x522a8, 4) == 50331
    assert [word(at, 4) for at in (0x522b4, 0x522b8, 0x522bc)] == [0x83ea, 0x21bbc, 0x21e14]
    assert word(0x83ea, 1) == 30
    owners = dict(EXISTING)
    assert word(0x52298, 4) + 0x18 == owners['handsome-spaniel/ram']
    assert word(0x52298, 4) + 0x60 == owners['devout-swift/ram']
    assert word(0x52298, 4) + 3 == owners['righteous-scorpion/ram']
    assert word(0x52298, 4) + 0x34 == owners['flat-coyote/ram']
    assert word(0x522a0, 4) + 0x36 == owners['rare-sawfly/ram']
    assert word(0x522a4, 4) + 0x20 == owners['rpm/ram']
    assert word(0x522ac, 4) + word(0x52296) == owners['injection_end_angle/ram']
    assert word(0x522b0, 4) + 1 == owners['apc_mode/ram']
    assert word(0x522c0, 4) + 5 == owners['shaggy-nyala/ram']
    assert [word(at) for at in (0x521a8, 0x521aa, 0x521ac, 0x521ae)] == [0x2fe6, 0x4f22, 0x4f12, 0x4f13]
    assert [word(at) for at in (0x521ee, 0x521f0, 0x52246, 0x52248, 0x52250, 0x52252)] == [
        0x8ff8, 0x7402, 0x420b, 0x6153, 0x420b, 0xe078]
    assert [word(at) for at in (0x52276, 0x52284, 0x52288, 0x5228a, 0x5228c, 0x5228e, 0x52290)] == [
        0xc003, 0xc034, 0x4f17, 0x4f16, 0x4f26, 0x000b, 0x6ef6]
    assert sh2.decode(word(0x521ee), 0x521ee).target == 0x521e2
    for start, end in CODE_SPANS:
        for at in range(start, end, 2):
            insn = sh2.decode(word(at), at)
            if insn.target is not None and insn.flow in ('branch', 'jump'):
                assert any(s <= insn.target < e for s, e in CODE_SPANS)


@cache
def literals():
    header = (TOOL_DIR / HEADER).read_text()
    [body] = re.findall(r'injection_start_delay_cases\[\] = \{(.*?)\n\};', header, re.S)
    body = re.sub(r'(0x[0-9a-f]+|\d+)U\b', r'\1', body)
    rows = ast.literal_eval('[' + body.replace('{', '[').replace('}', ']') + ']')
    assert all(len(row) == 21 and [len(row[i]) for i in (0, 1, 4, 18)] == [2, 6, 3, 15] for row in rows)
    return rows


@cache
def arithmetic_program():
    assert Grammar(repo.config()).validate(FORMULA) is None
    text = re.sub(r'\bffff[0-9a-f]{4}\b', lambda m: f'memory[{int(m[0], 16)}]', FORMULA)
    tree = ast.parse(text)

    class ExactDivision(ast.NodeTransformer):
        def visit_BinOp(self, node):
            node = self.generic_visit(node)
            if isinstance(node.op, ast.Div):
                return ast.copy_location(ast.Call(ast.Name('Fraction', ast.Load()), [node.left, node.right], []), node)
            return node

    return builtins.compile(ast.fix_missing_locations(ExactDivision().visit(tree)), '<injection candidate arithmetic>', 'exec')


def evaluate(row):
    memory = {0xffff11bc: row[0][0], 0xffff10ca: row[0][1], 0xffff241c: row[2],
              0xffff192e: row[3], 0xffff4184: row[4][0], 0xffff24c9: row[4][1],
              0xffff4251: row[4][2], 0x83ea: row[5]}
    memory.update((0xffff23d4 + 2 * i, value) for i, value in enumerate(row[1]))
    env = dict(memory=memory, RAM16=memory, ROM8=memory, min=min, max=max, floor=math.floor,
               uint8=lambda n: n & 255, uint16=lambda n: n & 65535,
               uint32=lambda n: n & 0xffffffff, Fraction=Fraction)
    exec(arithmetic_program(), {'__builtins__': {}}, env)
    return env


def check_vector(row):
    assert all(type(n) is int and 0 <= n <= 65535 for n in (*row[0], *row[1], row[2], row[3]))
    assert all(type(n) is int and 0 <= n <= 255 for n in (*row[4], row[5]))
    assert row[6] in (0, 1) and row[7] in (0, 1)
    env = evaluate(row)
    selected = row[0][int(bool(row[4][0] & 64))]
    coefficient = (selected * 805296) % (1 << 32) // 65536
    maximum = max([row[2]] + row[1])
    raw_pulse = coefficient * maximum // 65536
    pulse = min(255, raw_pulse)
    raw_delay = max(0, 2 * row[3] - 4 * pulse)
    delay = max(0, raw_delay - row[5]) if row[4][1] & 32 else raw_delay
    quotient, remainder = divmod(delay, 120)
    angle = min(116, max(4, remainder)) // 4
    lead_word = 3 if row[4][2] & 1 else quotient
    assert row[8:18] == [angle, lead_word & 255, coefficient, maximum, raw_pulse,
                         pulse, raw_delay, delay, quotient, remainder]
    assert [env[name] for name in ('K', 'P', 'p', 'D0', 'D', 'q', 'to')] == [
        coefficient, maximum, pulse, raw_delay, delay, quotient, lead_word & 255]
    is_long = delay >= 30720
    q_bit = 1 - quotient % 2
    vector = [((0x28765430 + i * 0x01030507) if row[7] == 0 else
               (0xa9876543 + i * 0x00130709)) % (1 << 32) for i in range(15)]
    vector[:3] = [lead_word, ((remainder - 120 * q_bit) * (1 << (16 if is_long else 8))
                            + quotient // 2 + (0 if is_long else 128)) % (1 << 32), angle]
    vector[4] = pulse if row[3] < 2 * pulse else 4 * pulse
    vector[5] = 0x0100424c
    vector[6] = 3 if row[4][2] & 1 else 0x83ea if row[4][1] & 32 else 0x010024c8
    vector[7] = coefficient
    assert row[18] == vector
    assert row[19] == 256 * q_bit + 1 - row[4][2] % 2
    assert row[20] == int(is_long)


def publication(text, counts):
    def exact_claims(pattern, expected):
        values = re.findall(pattern, text)
        assert values and set(map(int, values)) == set(expected)

    exact_claims(r'\b(\d+)\s+(?:stock\s+)?instructions\b', (counts[0],))
    exact_claims(r'\b(\d+)\s+(?:bound\s+)?bytes\b', (counts[1],))
    exact_claims(r'\b(\d+)\s+literal\s+cases\b', (counts[2],))
    for phrase in ('identity-only', 'uint32', 'uint8', 'SP-64..SP+31', 'MD/RB', 'physical'):
        assert phrase.lower() in text.lower()
    summary = matrix_counts(literals())
    for key, label in (('primary', 'primary'), ('alternate', 'alternate'),
                       ('short_helpers', 'short'), ('long_helpers', 'long'),
                       ('stock_delay_byte', 'stock'), ('artificial_delay_byte', 'artificial')):
        exact_claims(rf'(?<![\w.])(\d+)\s+{label}\b', (summary[key],))
    zero_cases = sum(row[15] == 0 for row in literals())
    exact_claims(r'\bzero-numerator\s+path\s+executes(?:\s+in)?\s+(\d+)\s+(?:cases|times)\b', (zero_cases,))
    cross = summary['groups']['independent control-bit cross product']
    cross_claims = re.findall(r'\bcontrol\s+cross-product\s+(?:has|contains)\s+(\d+)\s+(?:distinct\s+)?cases\b', text)
    cross_claims += re.findall(r'\b(\d+)-case\s+control/T/register\s+cross-product\b', text)
    assert cross_claims and set(map(int, cross_claims)) == {cross}
    exact_claims(r'\b(\d+)(?:-case\b|\s+(?:(?:distinct|literal)\s+)?(?:cases|times)\b)',
                 (counts[2], zero_cases, cross))
    instruction_counts = re.findall(r'\b(\d+)\s+instruction\s+bytes\b', text)
    data_counts = re.findall(r'\b(\d+)\s+(?:bound\s+)?data\s+bytes\b', text)
    assert instruction_counts and set(map(int, instruction_counts)) == {sum(e - s for s, e in CODE_SPANS)}
    assert data_counts and set(map(int, data_counts)) == {sum(size for _, size in POOLS)}


@cache
def stock_module():
    spec = importlib.util.spec_from_file_location('injection_preview_stock_verifier', repo.ROOT / 'tools/sh-elf-run/verify_stock_code.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def verify_fixture(fixture, stock):
    expected = bytearray(stock)
    for address in ALIASES:
        raw = int.from_bytes(stock[address:address + 4], 'big')
        expected[address:address + 4] = (0x01000000 + (raw & 65535)).to_bytes(4, 'big')
    complete_match = fixture == bytes(expected)
    assert complete_match, 'Full fixture byte equality failed'
    assert all(fixture[start:end] == expected for start, end, expected in SPANS[:3])


def normalized(model, value):
    if isinstance(value, SymbolKey):
        owner = model.meaning_of(value)
        assert owner is not None, f'Unowned proof symbol: {value}'
        return owner.key
    if isinstance(value, list):
        return [normalized(model, item) for item in value]
    if isinstance(value, dict):
        return {key: normalized(model, item) for key, item in value.items() if item is not None}
    return value


def preserved_normalized(model, value):
    """Bind an unchanged held step to its exact immutable unresolved source."""
    if not isinstance(value, dict) or 'research' not in value:
        return normalized(model, value)
    record = value['research']
    path, order = record['source_path'], record['order']
    source = research.historical_source(model.root, record['source_commit'], path)
    document = store.load(model.root, Path(path), model.overlay)
    current = document['step'][order - 1]
    assert current['research'] == record
    failure = research.validate(record, current, source, Grammar(model.config), path, order,
                                model=model, home=document.get('home', '7mfk'))
    assert failure is None, failure
    original = json.loads(record['original'])
    held = {key: item for key, item in value.items() if key != 'research'}
    held['note'] = original['note']
    return normalized(model, held)


def stored_value(value):
    if isinstance(value, list):
        return [stored_value(item) for item in value]
    if isinstance(value, dict):
        return {key: stored_value(item) for key, item in value.items()}
    if isinstance(value, str) and re.fullmatch(r'[\w-]+/(?:fn|ram|tbl|axis|reg|did|dtc)/[\w-]+', value):
        return '/'.join(value.split('/')[:2])
    return value


def verify_selector_notes(notes, threshold_note):
    assert set(notes) == set(SELECTOR_NOTES)
    normalize = lambda text: re.sub(r'\s+', ' ', text).strip()
    for slot, expected in SELECTOR_NOTES.items():
        assert type(notes[slot]) is str and normalize(notes[slot]) == expected
    assert type(threshold_note) is str and normalize(threshold_note) == SELECTOR_NOTES['bit5']


def verify_bounded_path(path):
    assert path == [FUNCTION]


@pytest.mark.parametrize('address', (0x52284, 0x52298, 0x522a8, 0x522b8, 0x21f3c))
def test_injection_fixture_refuses_instruction_alias_constant_and_helper_pointer_changes(address):
    data = derive.image_bytes(repo.layout('7mfk'))
    fixture = bytearray(stock_module().build_fixture(declared_region(), data))
    fixture[address] ^= 1
    with pytest.raises(AssertionError):
        verify_fixture(fixture, data)


@pytest.mark.parametrize('address', [at for s, e, _ in SPANS for at in range(s, e)])
def test_injection_every_bound_stock_byte_corruption_is_rejected(address):
    data = bytearray(derive.image_bytes(repo.layout('7mfk')))
    data[address] ^= 1
    with pytest.raises(AssertionError):
        verify_stock(data)


def test_injection_all_frozen_vectors_match_existing_grammar_and_independent_gprs_sr():
    for row in literals():
        check_vector(row)


@pytest.mark.parametrize('index', (8, 9, 18, 19, 20))
def test_injection_literal_contract_rejects_output_gpr_sr_and_frame_path_mutation(index):
    row = [list(v) if isinstance(v, list) else v for v in literals()[0]]
    if index == 18:
        row[index][6] ^= 1
    else:
        row[index] ^= 1
    with pytest.raises(AssertionError):
        check_vector(row)


def test_injection_matrix_covers_all_control_combinations_and_numeric_boundaries():
    rows = literals()
    summary = matrix_counts(rows)
    cross = Counter(tuple((*r[4], r[6], r[7])) for r in rows
                    if r[0] == [1000, 5334] and r[1] == [0] * 6 and r[2] == 0
                    and r[3] == 15360 and r[5] == 30)
    assert set(cross) == {(f, m, o, t, v) for f in (0, 64) for m in (0, 32)
                          for o in (0, 1) for t in (0, 1) for v in (0, 1)}
    assert set(cross.values()) == {1} and sum(cross.values()) == summary['groups']['independent control-bit cross product'] == 32
    for axis in range(3):
        assert {r[4][axis] for r in rows} == set(range(256))
    assert {r[5] for r in rows} == set(range(256))
    assert {r[17] for r in rows} == set(range(120))
    assert {254, 255, 256} <= {r[12] for r in rows}
    assert {0, 30719, 30720, 30721, 131070} <= {r[15] for r in rows}
    assert {255, 256, 257, 511, 512, 513, 1023, 1024, 1025, 1092} <= {r[16] for r in rows}
    assert {(r[6], r[7]) for r in rows} == {(0, 0), (0, 1), (1, 0), (1, 1)}
    assert {max(r[0][bool(r[4][0] & 64)] * 805296 // (1 << 32), 0) for r in rows} == set(range(13))
    assert sum(bool(r[4][0] & 64) for r in rows) == summary['alternate'] == 1409
    assert sum(not bool(r[4][0] & 64) for r in rows) == summary['primary'] == 5446
    assert sum(r[5] == 30 for r in rows) == summary['stock_delay_byte'] == 5610
    assert sum(r[5] != 30 for r in rows) == summary['artificial_delay_byte'] == 1245
    assert sum(r[20] for r in rows) == summary['long_helpers'] == 2409
    assert sum(not r[20] for r in rows) == summary['short_helpers'] == 4446
    assert {(r[2] > max(r[1])) - (r[2] < max(r[1])) for r in rows} == {-1, 0, 1}
    assert {(r[3] > 2 * r[13]) - (r[3] < 2 * r[13]) for r in rows} == {-1, 0, 1}


def test_injection_three_none_signs_have_full_word_wrap_witnesses():
    expected = {(5333, 65535, 418): 0, (5334, 65535, 418): 6,
                (0, 0, 15359): 255, (0, 0, 15360): 0,
                (1000, 0, 15360): 0, (1000, 6, 15360): 255}
    observed = {}
    for row in literals():
        if row[4] == [0, 0, 0] and row[2] == 0 and len(set(row[1])) == 1:
            key = (row[0][0], row[1][0], row[3])
            if key in expected:
                observed[key] = row[9]
    assert observed == expected


@pytest.mark.parametrize('extra_first', (False, True))
def test_injection_bounded_proof_refuses_an_extra_unexecuted_function(extra_first):
    verify_bounded_path([FUNCTION])
    extra = SymbolKey('7mfk', 'fn', 0x4a26a)
    path = [extra, FUNCTION] if extra_first else [FUNCTION, extra]
    with pytest.raises(AssertionError):
        verify_bounded_path(path)


@pytest.mark.parametrize('slot,old,new', (
    ('bit6', 'bit6 set selects unsigned16 word ffff10ca; bit6 clear selects unsigned16 word ffff11bc',
     'bit6 set selects unsigned16 word ffff11bc; bit6 clear selects unsigned16 word ffff10ca'),
    ('bit5', 'bit5 set applies', 'bit5 clear applies'),
    ('bit0', 'bit0 set publishes ffff23f0=3; bit0 clear publishes',
     'bit0 clear publishes ffff23f0=3; bit0 set publishes'),
    ('bit6', 'unsigned16', 'unsigned8'),
    ('bit5', 'max(0,', 'min(0,'),
    ('bit0', 'uint8(floor', 'uint16(floor'),
    ('threshold', 'bit5 set applies', 'bit5 clear applies'),
    ('bit5', 'bit5 clear retains D0', 'bit5 clear applies the decrement'),
))
def test_injection_selector_contract_refuses_reversed_conditions_and_widths(slot, old, new):
    notes = dict(SELECTOR_NOTES)
    threshold_note = SELECTOR_NOTES['bit5']
    verify_selector_notes(notes, threshold_note)
    if slot == 'threshold':
        assert old in threshold_note
        threshold_note = threshold_note.replace(old, new)
    else:
        assert old in notes[slot]
        notes[slot] = notes[slot].replace(old, new)
    with pytest.raises(AssertionError):
        verify_selector_notes(notes, threshold_note)


def declared_region():
    return stock_module().Region(key=KEY,rom='JK08A',
        source='stock_jk08a_injection_start_delay.s',harness=HARNESS,
        start=0x521a8,end=0x52292,pools=POOLS,ram_literals=ALIASES,
        cases=6855,boundary=False,symbols=tuple((macro,owner) for macro,(owner,_) in OWNER_DEFINES.items()),
        callees=CODE_SPANS[1:])


def required_region(module):
    matches = [region for region in module.REGIONS if region.key == KEY]
    assert len(matches) == 1, 'The canonical registered injection Region is mandatory'
    region = matches[0]
    assert isinstance(region.cases, int) and not isinstance(region.cases, bool)
    assert region == declared_region(), 'Every Region field belongs to the registered contract'
    return region


def actual_counts():
    region = required_region(stock_module())
    header = (TOOL_DIR / HEADER).read_text()
    [macro] = re.findall(r'^#define INJECTION_START_DELAY_CASE_COUNT (\d+)U$', header, re.M)
    assert len(literals()) == int(macro) == region.cases == 6855
    assert len(region.code_spans) == 3 and sum(end-start for start,end in region.code_spans) == 808
    return (sum((end-start)//2 for start,end in region.code_spans),
            sum(end-start for start,end in region.code_spans)+sum(size for _,size in region.pools), len(literals()))


def matrix_counts(rows):
    cross = [r for r in rows if r[0] == [1000,5334] and r[1] == [0]*6 and r[2] == 0
             and r[3] == 15360 and r[5] == 30]
    return dict(total=len(rows), primary=sum(not bool(r[4][0]&64) for r in rows),
                alternate=sum(bool(r[4][0]&64) for r in rows),
                short_helpers=sum(not r[20] for r in rows), long_helpers=sum(r[20] for r in rows),
                stock_delay_byte=sum(r[5] == 30 for r in rows), artificial_delay_byte=sum(r[5] != 30 for r in rows),
                groups={'independent control-bit cross product':len(cross)})


def required_owner(model, name, address):
    owner = model.meaning_of(SymbolKey('7mfk', name.split('/')[1], address))
    assert owner is not None and owner.key == name, f'Mandatory owner is absent: {name}'
    return owner


def required_evidence(model, actual, expected):
    canonical = lambda item: json.dumps(stored_value(normalized(model, item)), sort_keys=True)
    assert Counter(canonical(item) for item in actual) >= Counter(canonical(item) for item in expected)


def required_properties(model, actual, expected):
    normalized_actual = stored_value(normalized(model, actual))
    for key,value in expected.items():
        assert normalized_actual.get(key) == stored_value(value), key


def owner_document_contract(model, owner, document):
    """Require the bounded consumer contract while allowing independent reviews."""
    assert owner.key in OWNER_CONTRACTS
    required_properties(model, owner.props, document['props'])
    current = owner.symbols['7mfk']
    expected = document['symbol']
    assert current.key.address == int(expected['address'],16)
    symbol_properties = dict(expected['props'])
    required_note = symbol_properties.pop('note', None)
    required_properties(model,current.props,symbol_properties)
    if required_note is not None:
        notes = current.props.get('note', [])
        assert isinstance(notes, list) and required_note in notes
    required_evidence(model,current.evidence,expected['evidence'])
    identity = lambda item: (item['type'],item['to'],item.get('slot'),item.get('offset'))
    wanted_links = {identity(item):item for item in document['links']}
    assert len(wanted_links) == len(document['links'])
    actual_links = {(link.type,link.to.key,link.slot,link.offset):link for link in owner.links}
    assert len(actual_links) == len(owner.links) and set(actual_links) >= set(wanted_links)
    for key,wanted in wanted_links.items():
        current = actual_links[key]
        assert current.stated >= set(wanted.get('layouts',['7mfk']))
        if wanted.get('role'):
            assert wanted['role'] in current.roles
        props = {field:value for field,value in wanted.items()
                 if field not in ('type','to','slot','offset','role','evidence','layouts')}
        required_properties(model,current.props,props)
        required_evidence(model,current.evidence,wanted.get('evidence',[]))


def chain_document_contract(model):
    entity = model.entities[('chain','injection_phase')]
    assert len(entity.steps) == 22
    grammar = Grammar(repo.config())
    for index in (8,9,10,11):
        step = entity.steps[index]
        assert stored_value(normalized(model,step)) == REQUIRED_STEPS[str(index)]
        assert step['sign'] == 'none' and normalized(model,step['via']) == [FN]
        formula = ANGLE_FORMULA if index == 9 else FORMULA
        assert re.sub(r'\s+','',step['note']) == re.sub(r'\s+','',formula)
        assert grammar.validate(step['note']) is None


def test_injection_start_delay_chain_owner_contract():
    model = compile.cached(repo.ROOT)
    for name,document in OWNER_CONTRACTS.items():
        owner_document_contract(model,required_owner(model,name,int(document['symbol']['address'],16)),document)
    scalar = required_owner(model,NEW[0],NEW[1])
    assert scalar.props['block'] == 'injection_timing/block'
    assert scalar.symbols['7mfk'].value('signed') is False
    chain_document_contract(model)


def scalar_with_notes(model, notes):
    owner = required_owner(model,NEW[0],NEW[1])
    symbol = owner.symbols['7mfk']
    changed = SimpleNamespace(key=symbol.key, props={**symbol.props, 'note':notes}, evidence=symbol.evidence)
    return SimpleNamespace(key=owner.key, props=owner.props, links=owner.links, symbols={'7mfk':changed})


@pytest.mark.parametrize('notes', ([], ['Unsupported scalar meaning.'], 'Unsupported scalar meaning.'))
def test_injection_scalar_contract_refuses_missing_changed_and_malformed_notes(notes):
    model = compile.cached(repo.ROOT)
    owner_document_contract_value = OWNER_CONTRACTS[NEW[0]]
    with pytest.raises(AssertionError):
        owner_document_contract(model,scalar_with_notes(model,notes),owner_document_contract_value)


def test_injection_scalar_contract_preserves_its_note_during_independent_review():
    model = compile.cached(repo.ROOT)
    wanted = OWNER_CONTRACTS[NEW[0]]
    note = wanted['symbol']['props']['note']
    owner_document_contract(model,scalar_with_notes(model,[note,'Independent reader review.']),wanted)


def harness_contract(text):
    assert text.count(f'#include "{HEADER}"') == 1
    assert 'i<ARRAY_SIZE(injection_start_delay_cases)' in text
    assert 'completed!=INJECTION_START_DELAY_CASE_COUNT' in text and text.count('++completed;') == 1
    assert f'VQ_SH_ELF_STOCK_CODE status=PASS region={KEY} cases=%lu' in text
    for macro in OWNER_DEFINES:
        assert not re.search(rf'^#define\s+{macro}\b',text,re.M)
    for assertion in (
        'sizeof(struct context)==76U','offsetof(struct context,entry_t)==72U',
        'sizeof(struct observation)==380U','offsetof(struct observation,sp)==80U',
        'offsetof(struct observation,continuation)==84U','offsetof(struct observation,abi_before)==88U',
        'offsetof(struct observation,abi_after)==136U','offsetof(struct observation,frame_before)==184U',
        'offsetof(struct observation,frame_after)==280U','offsetof(struct observation,sr_before)==376U'):
        assert assertion in text
    for assertion in (
        'i!=(ANGLE_OUTPUT&0xffffU) && i!=(LEAD_OUTPUT&0xffffU)',
        'out.sr_before&~0x301U','memcmp(&c,&before,sizeof(c))',
        'memcmp(out.abi_before,out.abi_after,sizeof(out.abi_before))',
        'for(i=0;i<15U;++i)','for(i=0;i<96U;++i)','for(i=0;i<65536U;++i)',
        'if(t->long_path)frame_set(expected_frame,28,t->expected[4]);',
        'frame_set(expected_frame,36,0x21e14U);frame_set(expected_frame,32,c.r[3]);',
        'word(out.frame_before,88)!=out.continuation || word(out.frame_after,88)!=out.continuation'):
        assert assertion in text


def section(path,title):
    text = (repo.ROOT/path).read_text()
    heading = '## '+title
    assert text.count(heading) == 1
    return text.split(heading,1)[1].split('\n## ',1)[0]


def test_injection_start_delay_registered_stock_contract():
    module = stock_module()
    region = required_region(module)
    assert actual_counts() == (404,871,6855)
    assert tuple(region.symbols) == tuple((macro,owner) for macro,(owner,_) in OWNER_DEFINES.items())
    data = module.stock_image('JK08A')
    assert module.harness_defines(region,data) == {**{macro:address for macro,(_,address) in OWNER_DEFINES.items()},'REGION_ENTRY':0x521a8}
    verify_stock(data)
    verify_fixture(module.build_fixture(region,data),data)
    for name,digest in EXECUTION_SOURCES.items():
        assert hashlib.sha256((TOOL_DIR/name).read_bytes()).hexdigest() == digest
    shared = (TOOL_DIR/'stock_invoke.s').read_text()
    assert shared.count('.include "stock_injection_start_delay_invoke.s"') == 1
    driver = (TOOL_DIR/'stock_injection_start_delay_invoke.s').read_text()
    assert driver.count('.global _stock_invoke_injection_start_delay') == 1
    assert driver.count('.size _stock_invoke_injection_start_delay') == 1
    harness_contract((TOOL_DIR/HARNESS).read_text())
    publication(section(SPEC,'Bounded injection start-delay publication'),actual_counts())
    publication(section('tools/sh-elf-run/README.md','Injection start-delay publication'),actual_counts())
    for row in literals():
        check_vector(row)


@pytest.mark.parametrize('name,address', ((NEW[0],NEW[1]),(FN,0x521a8)))
def test_injection_missing_required_owner_is_rejected(name,address):
    with pytest.raises(AssertionError):
        required_owner(type('MissingModel',(),{'meaning_of':lambda self,key:None})(),name,address)


def test_injection_missing_required_region_is_rejected():
    with pytest.raises(AssertionError):
        required_region(type('MissingModule',(),{'REGIONS':[]})())


def test_injection_missing_tracked_header_is_rejected(monkeypatch):
    monkeypatch.setattr(sys.modules[__name__],'HEADER','missing-injection-cases.h')
    literals.cache_clear()
    with pytest.raises(FileNotFoundError):
        literals()
    literals.cache_clear()


@pytest.mark.parametrize('index,field,value', (
    (8,'sign','positive'),(10,'sign','negative'),(11,'sign','negative'),
    (8,'via',[SymbolKey('7mfk','fn',0x4a26a)]),
    (8,'via',[SymbolKey('7mfk','fn',0x21bbc)]),(10,'note','unsupported delay expression')))
def test_injection_bounded_chain_contract_rejects_mutation(index,field,value):
    model = compile.cached(repo.ROOT)
    before = model.entities[('chain','injection_phase')]
    changed = replace(before,steps=[dict(step) for step in before.steps])
    changed.steps[index][field] = value
    proxy = type('Model',(),{'entities':{('chain','injection_phase'):changed},'meaning_of':model.meaning_of})()
    with pytest.raises(AssertionError):
        chain_document_contract(proxy)


def test_injection_unrelated_chain_note_allows_independent_review():
    model = compile.cached(repo.ROOT)
    before = model.entities[('chain','injection_phase')]
    changed = replace(before,steps=[dict(step) for step in before.steps])
    changed.steps[7]['note'] = 'Independent angular input review'
    proxy = type('Model',(),{'entities':{('chain','injection_phase'):changed},'meaning_of':model.meaning_of})()
    chain_document_contract(proxy)


@pytest.mark.parametrize('owner', ('amorphous-ape/ram','offbeat-mantis/ram','outstanding-marmot/ram','expert-lion/ram'))
def test_injection_address_base_is_not_an_extra_numeric_input(owner):
    model = compile.cached(repo.ROOT)
    for result in ('flat-coyote/ram','righteous-scorpion/ram'):
        meaning = next(item for item in model.meanings if item.key == result)
        assert not any(link.type == 'input' and link.to.key == owner for link in meaning.links)


@pytest.mark.parametrize('needle,replacement', (
    ('uint32(16*R*50331)','16*R*50331'),('uint8(q)','uint16(q)'),
    ('F*uint16(ffff10ca)+(1-F)*uint16(ffff11bc)','F*uint16(ffff11bc)+(1-F)*uint16(ffff10ca)'),
    ('max(0,D0-W*ROM8[0x000083ea])','max(0,D0-(1-W)*ROM8[0x000083ea])')))
def test_injection_machine_formula_refuses_width_and_condition_mutations(needle,replacement):
    assert needle in FORMULA
    model = compile.cached(repo.ROOT)
    before = model.entities[('chain','injection_phase')]
    changed = replace(before,steps=[dict(step) for step in before.steps])
    changed.steps[8]['note'] = FORMULA.replace(needle,replacement)
    proxy = type('Model',(),{'entities':{('chain','injection_phase'):changed},'meaning_of':model.meaning_of})()
    with pytest.raises(AssertionError):
        chain_document_contract(proxy)
