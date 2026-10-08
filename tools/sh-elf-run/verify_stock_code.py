#!/usr/bin/env python3
"""Execute stock instruction regions whose behavior the entity files state.

A region is a run of stock instructions of one image at their original
addresses: a whole function, or a block inside one. The verifier links the
GNU reconstruction of the region and of the pool words it loads at the same
addresses and requires byte identity with the image. It then builds a
simulator-only fixture from the image: the pool words that hold high-RAM
addresses point into simulator test RAM. A block returns through a boundary
outside the tested instructions: RTS/NOP normally, or a stack-held PR restore
followed by RTS/NOP after a stock call replaces PR. A whole function returns
through its own RTS. The harness seeds the RAM and
calibration inputs, calls the region with the registers that it reads on
entry, and checks every store and the return value against the symbols and
the named bits of the entity files, which the verifier passes to it with the
region constants.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
import hashlib
from pathlib import Path
import sys
import tempfile

TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parents[1]
# The firmware gate runs outside the project environment, where the `kb`
# package is importable only from its source tree.
for _path in (TOOL_DIR, ROOT / "tools" / "kb" / "src", ROOT):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

import verify_map_switching as base_verifier
from elf_storage_layout import ELFStorageError, require_separate_storage

from kb import targets as kb_targets


RETURN_STUB = bytes.fromhex("000b0009")


@dataclass(frozen=True)
class Region:
    key: str
    rom: str
    source: str
    harness: str
    start: int
    # The first address after the region.
    end: int
    # The pool spans that the region loads, as (address, size).
    pools: tuple[tuple[int, int], ...]
    # Pool words that hold high-RAM addresses.
    ram_literals: tuple[int, ...]
    cases: int
    # A region without a stock return uses the RTS/NOP pair that the fixture
    # places at `end`; another region returns through its own instructions.
    boundary: bool = True
    # The stack offset of a simulator return continuation for a block whose
    # stock calls replace PR. The boundary restores PR outside all tested
    # instructions; None uses the ordinary RTS/NOP boundary.
    return_address_offset: int | None = None
    # Scratch register used only by the simulator boundary to restore PR.
    # R0 keeps the stock result; a block can also retain its cached R5.
    return_register: int = 5
    # The stock MOV.L @(disp,PC),R12 that loads the base register before a
    # block that reads it on entry.
    base_load: int | None = None
    # Harness definitions of the address of a meaning on the layout, as
    # (definition, meaning).
    symbols: tuple[tuple[str, str], ...] = ()
    # Harness definitions of the mask of a named bit, as (definition,
    # meaning, bit).
    bits: tuple[tuple[str, str, str], ...] = ()
    # Harness definitions of the addresses inside the region that no entity
    # file names, as (definition, value).
    constants: tuple[tuple[str, int], ...] = ()
    # Additional stock instruction spans executed by this region, including
    # callees or a selection path separated by pool data, at stock addresses.
    callees: tuple[tuple[int, int], ...] = ()
    # Explicit (pool, high-RAM address, positive word alias, byte extent).
    # MOV.W sign-extension requires a separate low-memory alias domain.
    ram_word_literals: tuple[tuple[int, int, int, int], ...] = ()
    # Explicit pool, I/O address, positive alias, and declared register extent.
    register_word_literals: tuple[tuple[int, int, int, int], ...] = ()

    @property
    def code_spans(self):
        return ((self.start, self.end), *self.callees)


FUEL_CUT_SYMBOLS = (
    ("FUEL_INHIBIT", "fuel_inhibit/ram"),
    ("ENGINE_SPEED", "rpm/ram"),
    ("FUEL_CUT_TABLE", "rev_limit_fuel_cut/tbl"),
)
FUEL_CUT_BITS = (
    ("ARMED_MASK", "fuel_inhibit/ram", "armed"),
    ("ACTIVE_MASK", "fuel_inhibit/ram", "active"),
)

REGIONS = (
    Region(key='jk08a-base-accumulator', rom='JK08A', source='stock_jk08a_base_accumulator.s', harness='harness-stock-jk08a-base-accumulator.c', start=349358, end=349424, pools=((349428, 4), (349640, 4), (349676, 4)), ram_literals=(349640, 349676), cases=132684, boundary=False, return_address_offset=None, return_register=5, base_load=None, symbols=(('TERM', 'adept-bumblebee/ram'), ('CONDITIONAL', 'beneficial-ringtail/ram'), ('COOLANT', 'competent-pillbug/ram'), ('OUTPUT', 'happy-curassow/ram')), bits=(), constants=(('EARLY_ONLY', 0),), callees=(), ram_word_literals=(), register_word_literals=()),
    Region(key='jk08a-transient-coefficient', rom='JK08A', source='stock_jk08a_transient_coefficient.s', harness='harness-stock-jk08a-transient-coefficient.c', start=338110, end=338166, pools=((74102, 8), (156546, 2), (156548, 4), (158396, 4), (338172, 2), (338176, 2), (338276, 4), (338304, 4), (338308, 4), (338312, 4)), ram_literals=(338276, 338304), cases=7440, boundary=False, return_address_offset=None, return_register=5, base_load=None, symbols=(('TERM', 'urban-degu/ram'), ('NORMALIZED', 'normalized_load/ram'), ('OUTPUT', 'attractive-donkey/ram')), bits=(), constants=(('EARLY_ONLY', 0),), callees=((156528, 156546), (158336, 158394), (157504, 157550)), ram_word_literals=(), register_word_literals=()),
    Region(key='jk08a-transient-additive', rom='JK08A', source='stock_jk08a_transient_additive.s', harness='harness-stock-jk08a-transient-additive.c', start=338178, end=338270, pools=((35648, 1), (338270, 10), (338300, 4), (338316, 8)), ram_literals=(338276, 338300, 338320), cases=87052, boundary=False, return_address_offset=None, return_register=5, base_load=None, symbols=(('TERM', 'urban-degu/ram'), ('COEFFICIENT', 'attractive-donkey/ram'), ('FLAGS', 'auspicious-jacamar/ram'), ('OUTPUT', 'enigmatic-mouse/ram')), bits=(), constants=(('EARLY_ONLY', 0),), callees=(), ram_word_literals=(), register_word_literals=()),
    Region(key='jk08a-coolant-conditional', rom='JK08A', source='stock_jk08a_coolant_conditional.s', harness='harness-stock-jk08a-coolant-conditional.c', start=348762, end=348916, pools=((34539, 1), (34725, 3), (37008, 2), (37530, 2), (39178, 16), (72471, 4), (72475, 4), (74786, 8), (156546, 2), (156548, 4), (158396, 4), (348988, 2), (349008, 4), (349040, 4), (349044, 4), (349048, 4), (349052, 4), (349056, 4), (349424, 2), (349426, 2), (349428, 2), (349632, 4), (349636, 4), (349640, 4), (349644, 4), (349648, 4), (349652, 4), (349656, 4), (349660, 4), (349664, 4), (349668, 4), (349672, 4)), ram_literals=(349008, 349040, 349048, 349056, 349640, 349644, 349672), cases=14261, boundary=False, return_address_offset=None, return_register=5, base_load=None, symbols=(('OUTPUT', 'competent-pillbug/ram'),), bits=(), constants=(('EARLY_ONLY', 0),), callees=((348928, 348988), (349060, 349358), (156528, 156546), (158336, 158394), (157504, 157550), (140688, 140698)), ram_word_literals=(), register_word_literals=()),
    Region(key='jk08a-transient-pair-1', rom='JK08A', source='stock_jk08a_transient_pair.s', harness='harness-stock-jk08a-transient-pair.c', start=336956, end=336964, pools=((35648, 1), (74102, 8), (156546, 6), (158396, 4), (338172, 2), (338176, 2), (338270, 10), (338300, 24)), ram_literals=(338276, 338300, 338304, 338320), cases=44640, boundary=True, return_address_offset=24, return_register=11, base_load=None, symbols=(('TERM', 'urban-degu/ram'), ('NORMALIZED', 'normalized_load/ram'), ('OUTPUT', 'enigmatic-mouse/ram')), bits=(), constants=(('EARLY_ONLY', 0),), callees=((338110, 338166), (338178, 338270), (156528, 156546), (158336, 158394), (157504, 157550)), ram_word_literals=(), register_word_literals=()),
    Region(key='jk08a-transient-pair-2', rom='JK08A', source='stock_jk08a_transient_pair.s', harness='harness-stock-jk08a-transient-pair.c', start=337054, end=337062, pools=((35648, 1), (74102, 8), (156546, 6), (158396, 4), (338172, 2), (338176, 2), (338270, 10), (338300, 24)), ram_literals=(338276, 338300, 338304, 338320), cases=44640, boundary=True, return_address_offset=24, return_register=11, base_load=None, symbols=(('TERM', 'urban-degu/ram'), ('NORMALIZED', 'normalized_load/ram'), ('OUTPUT', 'enigmatic-mouse/ram')), bits=(), constants=(('EARLY_ONLY', 0),), callees=((338110, 338166), (338178, 338270), (156528, 156546), (158336, 158394), (157504, 157550)), ram_word_literals=(), register_word_literals=()),
    Region(key='jk08a-fuel-multiplier', rom='JK08A', source='stock_jk08a_fuel_multiplier.s', harness='harness-stock-jk08a-fuel-multiplier.c', start=349932, end=350028, pools=((33678, 1), (33805, 6), (34022, 2), (35741, 1), (350288, 2), (350290, 2), (350296, 4), (350332, 4), (350336, 4), (350340, 4), (350344, 4), (350348, 4), (350352, 4), (350356, 4), (350706, 2), (350940, 4), (350944, 4), (350948, 4)), ram_literals=(350296, 350332, 350336, 350344, 350948), cases=77328, boundary=False, return_address_offset=None, return_register=5, base_load=None, symbols=(('OUTPUT', 'dazzling-sawfly/ram'), ('SNAPSHOT', 'vigorous-chihuahua/ram')), bits=(), constants=(('EARLY_ONLY', 0), ('WORD_ALIAS', 31232)), callees=((350030, 350288), (350360, 350538)), ram_word_literals=((350290, 4294935747, 31232, 1),), register_word_literals=()),
    Region(key='jk08a-pulse-precursor', rom='JK08A', source='stock_jk08a_pulse_precursor.s', harness='harness-stock-jk08a-pulse-precursor.c', start=321908, end=322250, pools=((38120, 2), (38624, 4), (138696, 4), (138700, 4), (322250, 2), (322252, 2), (322254, 2), (322256, 2), (322258, 2), (322536, 4), (322540, 4), (322544, 4), (322548, 4), (322552, 4), (322556, 4), (322560, 4), (322564, 4), (322568, 4), (322572, 4), (322576, 4), (322580, 4)), ram_literals=(138696, 322536, 322540, 322544, 322548, 322560, 322564, 322568, 322572), cases=78272, boundary=False, return_address_offset=None, return_register=5, base_load=None, symbols=(('OUTPUT', 'shapeless-worm/ram'), ('BANKS', 'dainty-oriole/ram')), bits=(), constants=(('EARLY_ONLY', 0), ('SELECTED_BFS', 4294908266)), callees=((138464, 138694), (157052, 157124)), ram_word_literals=(), register_word_literals=()),
    Region(key='jk08a-common-gain', rom='JK08A', source='stock_jk08a_common_gain.s', harness='harness-stock-jk08a-common-gain.c', start=341656, end=341988, pools=((33732, 3), (35326, 1), (35559, 1), (35665, 1), (37682, 2), (37830, 2), (76258, 16), (76274, 16), (138696, 4), (138700, 4), (155408, 4), (156570, 2), (156572, 4), (158396, 4), (341988, 2), (341990, 2), (341992, 2), (341994, 2), (341996, 2), (342160, 2), (342162, 2), (342164, 2), (342166, 2), (342168, 2), (342170, 2), (342172, 2), (342176, 4), (342180, 4), (342184, 4), (342188, 4), (342192, 4), (342196, 4), (342200, 4), (342204, 4), (342208, 4), (342212, 4), (342216, 4), (342220, 4), (342224, 4), (342228, 4), (342232, 4), (342236, 4), (342240, 4), (342244, 4), (342248, 4), (342252, 4), (342256, 4), (342260, 4), (342264, 4)), ram_literals=(138696, 155408, 342176, 342188, 342204, 342212, 342228, 342232, 342244, 342252), cases=68855, boundary=False, return_address_offset=None, return_register=5, base_load=None, symbols=(('OUTPUT', 'versatile-bobcat/ram'), ('FACTOR', 'asparagus-toucan/ram')), bits=(), constants=(('EARLY_ONLY', 0),), callees=((341998, 342160), (155168, 155204), (140536, 140552), (156552, 156570), (158340, 158394), (157504, 157550), (138464, 138694)), ram_word_literals=(), register_word_literals=()),
    Region(key='jk08a-enrichment-prefix', rom='JK08A', source='stock_jk08a_enrichment_prefix.s', harness='harness-stock-jk08a-enrichment-prefix.c', start=350712, end=350802, pools=((35739, 1), (35743, 1), (43434, 64), (72391, 8), (72896, 8), (72920, 8), (74062, 16), (75090, 9), (156076, 4), (156080, 4), (156084, 4), (156570, 2), (156572, 4), (156824, 4), (156828, 4), (157640, 4), (158080, 4), (158216, 4), (158396, 4), (350708, 2), (350710, 2), (350936, 2), (350948, 4), (350952, 4), (350956, 4), (350960, 4), (350964, 4), (350968, 4), (350972, 4), (350976, 4), (350980, 4), (350984, 4), (350988, 4), (350992, 4), (350996, 4), (351000, 4), (351004, 4), (351008, 4), (351012, 4), (351016, 4)), ram_literals=(350948, 350952, 350964, 350968, 350972, 351016), cases=70800, boundary=True, return_address_offset=20, return_register=11, base_load=None, symbols=(('OUTPUT', 'inquisitive-crow/ram'), ('PREFIX_ENTRY', 'large-tamarin/fn')), bits=(), constants=(('EARLY_ONLY', 0),), callees=((350538, 350706), (156552, 156570), (158340, 158394), (157504, 157550), (156024, 156074), (158148, 158214), (158020, 158080), (158840, 158990), (157552, 157638), (156788, 156822), (140536, 140552)), ram_word_literals=(), register_word_literals=()),
    Region(key='jk08a-enrichment-terminal', rom='JK08A', source='stock_jk08a_enrichment_terminal.s', harness='harness-stock-jk08a-enrichment-terminal.c', start=353288, end=353546, pools=((33947, 2), (34538, 1), (34547, 1), (34774, 1), (34777, 1), (35739, 2), (35743, 1), (35823, 1), (36742, 2), (37532, 2), (38124, 2), (73438, 8), (156546, 2), (156548, 4), (158396, 4), (353046, 2), (353244, 2), (353248, 4), (353252, 4), (353264, 4), (353268, 4), (353272, 4), (353276, 4), (353280, 4), (353284, 4), (353562, 2), (353806, 2), (353808, 4), (353812, 4), (353816, 4), (353820, 4), (353824, 4), (353828, 4), (353832, 4), (353836, 4), (353840, 4), (353844, 4), (353848, 4), (353852, 4), (353856, 4), (353860, 4), (353864, 4), (353868, 4), (353872, 4), (353876, 4), (353880, 4), (353884, 4), (353888, 4), (353892, 4), (353896, 4), (354048, 4), (354052, 4), (354056, 4), (354060, 4)), ram_literals=(353248, 353252, 353264, 353812, 353816, 353820, 353828, 353832, 353840, 353844, 353848, 353860, 353864, 353872, 353892, 354056), cases=70112, boundary=True, return_address_offset=24, return_register=11, base_load=None, symbols=(('OUTPUT', 'af_state_factor/ram'),), bits=(), constants=(('EARLY_ONLY', 0), ('TERMINAL_ENTRY', 352994), ('WORD_ALIAS', 31232)), callees=((352994, 353044), (353056, 353244), (353564, 353806), (353900, 354048), (156528, 156546), (158336, 158394), (157504, 157550)), ram_word_literals=((353046, 4294935747, 31232, 1), (353806, 4294935747, 31232, 1)), register_word_literals=()),
    Region(key='jk08a-opening-word', rom='JK08A', source='stock_jk08a_opening_word.s', harness='harness-stock-jk08a-opening-word.c', start=356288, end=356364, pools=((34038, 1), (35998, 1), (356364, 20)), ram_literals=(356364, 356380), cases=12556, boundary=False, return_address_offset=None, return_register=5, base_load=None, symbols=(('BATTERY', 'private-groundhog/ram'), ('OPENING', 'portable-kingfisher/ram')), bits=(), constants=(('EARLY_ONLY', 0),), callees=((140536, 140552),), ram_word_literals=(), register_word_literals=()),
    Region(key='jk08a-pulse-selector', rom='JK08A', source='stock_jk08a_pulse_selector.s', harness='harness-stock-jk08a-pulse-selector.c', start=347454, end=347582, pools=((34295, 1), (36242, 1), (38120, 2), (139676, 32), (139736, 8), (347596, 2), (347784, 2), (347788, 4), (347796, 4), (347812, 20), (357020, 6), (357204, 28)), ram_literals=(347788, 347812, 347816, 347820, 357204, 357208, 357216, 357220, 357228), cases=7302, boundary=False, return_address_offset=None, return_register=5, base_load=None, symbols=(('OUTPUT', 'portable-gecko/ram'), ('SNAPSHOT', 'berserk-terrier/ram')), bits=(), constants=(('EARLY_ONLY', 0),), callees=((347600, 347784), (356800, 356986), (139708, 139734), (139744, 139768)), ram_word_literals=(), register_word_literals=()),
    Region(key='jk08a-full-programmer', rom='JK08A', source='stock_jk08a_full_programmer.s', harness='harness-stock-jk08a-full-programmer.c', start=177738, end=178006, pools=((167582, 4), (167968, 4), (178010, 14), (178276, 20)), ram_literals=(167968, 178276, 178280, 178292), cases=18696, boundary=False, return_address_offset=None, return_register=5, base_load=None, symbols=(('CONTROL', 'provocative-anteater/ram'), ('COUNT', 'huge-lori/ram'), ('REMAINDER', 'economic-collie/ram'), ('MODE', 'apc_mode/ram'), ('POSITION', 'tunneling-doberman/ram'), ('PERIOD', 'spry-koel/ram'), ('OUTPUT', 'amphibian-panda/ram'), ('SCRATCH', 'injection_offset_reciprocal_residue/ram'), ('COUNTER_REGISTER', 'pompous-impala/reg'), ('COMPARE_REGISTER', 'injection_scheduler_compare_word/reg'), ('STATUS_REGISTER', 'injection_scheduler_status_word/reg'), ('CONTROL_REGISTER', 'injection_scheduler_control_word/reg')), bits=(), constants=(('EARLY_ONLY', 0), ('WORD_ALIAS', 32512), ('REGISTER_ALIAS', 32256)), callees=((167368, 167582),), ram_word_literals=((178012, 4294935788, 32512, 1),), register_word_literals=((178020, 4294964288, 32256, 36),)),
    Region(key='jk08a-oneshot', rom='JK08A', source='stock_jk08a_oneshot.s', harness='harness-stock-jk08a-oneshot.c', start=180540, end=180788, pools=((180788, 2), (180792, 28)), ram_literals=(180800, 180804, 180808, 180812, 180816), cases=8012, boundary=False, return_address_offset=None, return_register=5, base_load=None, symbols=(('COUNTER_REGISTER', 'glossy-tarantula/reg'), ('START_REGISTER', 'imported-panther/reg'), ('OPENING', 'flashy-jerboa/ram'), ('INHIBIT', 'fuel_inhibit_mask/ram'), ('HISTORY', 'quantum-tiger/ram'), ('ENABLE', 'futuristic-chinchilla/ram'), ('DIAGNOSTIC', 'shaggy-nyala/ram')), bits=(), constants=(('EARLY_ONLY', 0), ('REGISTER_ALIAS', 32000)), callees=(), ram_word_literals=(), register_word_literals=((180788, 4294964800, 32000, 40),)),
    Region(key='jk08a-rpm-phase-word', rom='JK08A', source='stock_jk08a_rpm_phase_word.s', harness='harness-stock-jk08a-rpm-phase.c', start=230662, end=230686, pools=((34627, 1), (230824, 4), (230836, 8)), ram_literals=(230824, 230836), cases=65536, boundary=True, return_address_offset=None, return_register=11, base_load=None, symbols=(('INPUT_WORD', 'classic-caracal/ram'), ('WORK_WORD', 'vigorous-horse/ram'), ('WORK_BYTE', 'liberal-falcon/ram'), ('SNAPSHOT_BYTE', 'daffodil-gibbon/ram')), bits=(), constants=(('EARLY_ONLY', 0), ('VIEW_KIND', 0)), callees=(), ram_word_literals=(), register_word_literals=()),
    Region(key='jk08a-rpm-phase-byte', rom='JK08A', source='stock_jk08a_rpm_phase_byte.s', harness='harness-stock-jk08a-rpm-phase.c', start=230604, end=230630, pools=((230824, 4),), ram_literals=(230824,), cases=65536, boundary=False, return_address_offset=None, return_register=11, base_load=None, symbols=(('INPUT_WORD', 'classic-caracal/ram'), ('WORK_WORD', 'vigorous-horse/ram'), ('WORK_BYTE', 'liberal-falcon/ram'), ('SNAPSHOT_BYTE', 'daffodil-gibbon/ram')), bits=(), constants=(('EARLY_ONLY', 0), ('VIEW_KIND', 1)), callees=(), ram_word_literals=(), register_word_literals=()),
    Region(key='jk08a-rpm-phase-copy', rom='JK08A', source='stock_jk08a_rpm_phase_copy.s', harness='harness-stock-jk08a-rpm-phase.c', start=135008, end=135024, pools=((135508, 12), (139536, 4), (139664, 4)), ram_literals=(135508, 135512, 135516), cases=2048, boundary=True, return_address_offset=24, return_register=11, base_load=None, symbols=(('INPUT_WORD', 'classic-caracal/ram'), ('WORK_WORD', 'vigorous-horse/ram'), ('WORK_BYTE', 'liberal-falcon/ram'), ('SNAPSHOT_BYTE', 'daffodil-gibbon/ram')), bits=(), constants=(('EARLY_ONLY', 0), ('VIEW_KIND', 2)), callees=((139512, 139524), (139550, 139608)), ram_word_literals=(), register_word_literals=()),
    Region(key='jk08a-event-isr', rom='JK08A', source='stock_jk08a_event_isr.s', harness='harness-stock-jk08a-event-isr.c', start=179776, end=180090, pools=((34295, 1), (36242, 1), (38120, 2), (139676, 32), (139736, 8), (180090, 34), (180412, 20), (180788, 2), (180792, 28), (347596, 2), (347784, 2), (347788, 4), (347796, 4), (347812, 20), (357020, 6), (357204, 28)), ram_literals=(180412, 180420, 180424, 180800, 180804, 180808, 180812, 180816, 347788, 347812, 347816, 347820, 357204, 357208, 357216, 357220, 357228), cases=7254, boundary=False, return_address_offset=None, return_register=5, base_load=None, symbols=(('TIMER_REGISTER', 'pompous-impala/reg'), ('STATUS_REGISTER', 'injection_scheduler_status_word/reg'), ('CONTROL_REGISTER', 'injection_scheduler_control_word/reg'), ('COUNTER_REGISTER', 'glossy-tarantula/reg'), ('START_REGISTER', 'imported-panther/reg')), bits=(), constants=(('EARLY_ONLY', 0), ('TIMER_ALIAS', 32256), ('PULSE_ALIAS', 32000), ('CONTROL_ALIAS', 32512), ('EVENT_ALIAS', 31744)), callees=((347454, 347582), (347600, 347784), (356800, 356986), (139708, 139734), (139744, 139768), (180540, 180788)), ram_word_literals=((180092, 4294935788, 32512, 1), (180096, 4294935828, 31744, 1)), register_word_literals=((180090, 4294964288, 32256, 36), (180788, 4294964800, 32000, 40))),
    Region(key='jk08a-end-angle', rom='JK08A', source='stock_jk08a_end_angle.s', harness='harness-stock-jk08a-end-angle.c', start=355280, end=355608, pools=((34553, 1), (34571, 1), (34601, 1), (34670, 1), (34671, 1), (34672, 1), (35003, 1), (35636, 1), (35650, 1), (35803, 1), (36076, 1), (36140, 1), (36355, 1), (36358, 1), (36918, 2), (36920, 2), (37114, 2), (38148, 2), (72627, 8), (74038, 8), (74498, 8), (74506, 8), (76818, 9), (138696, 4), (138700, 4), (154520, 4), (156546, 2), (156548, 4), (156824, 4), (156828, 4), (158080, 4), (158396, 4), (355608, 2), (355770, 2), (355772, 2), (355774, 2), (355776, 4), (355780, 4), (355784, 4), (355788, 4), (355792, 4), (355796, 4), (355800, 4), (355804, 4), (355808, 4), (355812, 4), (355816, 4), (355820, 4), (355824, 4), (355828, 4), (355832, 4), (355836, 4), (355840, 4), (355844, 4), (355848, 4), (355852, 4), (355856, 4), (355860, 4), (355864, 4), (355868, 4), (355872, 4), (356202, 2), (356204, 2), (356206, 2), (356208, 2), (356210, 2), (356212, 4), (356216, 4), (356220, 4), (356224, 4), (356228, 4), (356232, 4), (356236, 4), (356240, 4), (356244, 4), (356248, 4), (356252, 4), (356256, 4), (356260, 4), (356264, 4), (356268, 4), (356272, 4), (356276, 4), (356280, 4), (356284, 4)), ram_literals=(138696, 154520, 355776, 355792, 355796, 355804, 355812, 355820, 355848, 356212, 356216, 356228, 356236, 356248, 356252, 356256, 356272, 356280), cases=4056, boundary=False, return_address_offset=None, return_register=5, base_load=None, symbols=(), bits=(), constants=(('EARLY_ONLY', 0),), callees=((355610, 355770), (355876, 355952), (355952, 356006), (356006, 356202), (154084, 154130), (156528, 156546), (156788, 156822), (157504, 157550), (158336, 158394), (158020, 158080), (158840, 158990), (138464, 138694)), ram_word_literals=(), register_word_literals=()),
    Region(key='jk08a-full-dispatch', rom='JK08A', source='stock_jk08a_full_dispatch.s', harness='harness-stock-jk08a-full-dispatch.c', start=346692, end=346962, pools=((34295, 1), (36242, 1), (38120, 2), (139676, 32), (139736, 4), (139740, 4), (140942, 269), (167582, 2), (167584, 2), (167968, 4), (178010, 2), (178012, 2), (178014, 2), (178016, 2), (178018, 2), (178020, 2), (178022, 2), (178276, 4), (178280, 4), (178284, 4), (178288, 4), (178292, 4), (180788, 2), (180792, 2), (180794, 2), (180796, 2), (180798, 2), (180800, 4), (180804, 4), (180808, 4), (180812, 4), (180816, 4), (346962, 2), (346964, 2), (346966, 2), (346968, 2), (346970, 2), (346972, 2), (347162, 2), (347164, 2), (347166, 2), (347168, 2), (347170, 2), (347172, 2), (347174, 2), (347176, 2), (347178, 2), (347180, 2), (347184, 4), (347188, 4), (347192, 4), (347196, 4), (347200, 4), (347204, 4), (347208, 4), (347212, 4), (347216, 4), (347582, 2), (347584, 2), (347586, 2), (347588, 2), (347590, 2), (347592, 2), (347594, 2), (347596, 2), (347598, 2), (347784, 2), (347788, 4), (347792, 4), (347796, 4), (347800, 4), (347804, 4), (347808, 4), (347812, 4), (347816, 4), (347820, 4), (347824, 4), (347828, 4), (357020, 2), (357022, 2), (357024, 2), (357204, 4), (357208, 4), (357212, 4), (357216, 4), (357220, 4), (357224, 4), (357228, 4)), ram_literals=(167968, 178276, 178280, 178292, 180800, 180804, 180808, 180812, 180816, 347184, 347188, 347192, 347200, 347204, 347208, 347788, 347792, 347804, 347812, 347816, 347820, 357204, 357208, 357216, 357220, 357228), cases=3864, boundary=False, return_address_offset=None, return_register=5, base_load=None, symbols=(('TIMER_REGISTER', 'pompous-impala/reg'), ('STATUS_REGISTER', 'injection_scheduler_status_word/reg'), ('CONTROL_REGISTER', 'injection_scheduler_control_word/reg'), ('COUNTER_REGISTER', 'glossy-tarantula/reg'), ('START_REGISTER', 'imported-panther/reg')), bits=(), constants=(('EARLY_ONLY', 0), ('TIMER_ALIAS', 32256), ('PULSE_ALIAS', 32000), ('CONTROL_ALIAS', 32512), ('EVENT_ALIAS', 31488)), callees=((346974, 347162), (347220, 347454), (347454, 347582), (347600, 347784), (356800, 356986), (139708, 139734), (139744, 139768), (180540, 180788), (177738, 178006), (167368, 167582)), ram_word_literals=((346962, 4294935824, 31488, 5), (346970, 4294935788, 32512, 1), (178012, 4294935788, 32512, 1)), register_word_literals=((347176, 4294964288, 32256, 36), (180788, 4294964800, 32000, 40), (178020, 4294964288, 32256, 36))),
    Region(key='jk08a-channel-pulse', rom='JK08A', source='stock_jk08a_channel_pulse.s', harness='harness-stock-jk08a-channel-pulse.c', start=322466, end=322530, pools=((36242, 1), (37338, 8), (76224, 6), (322568, 4), (322592, 4), (322912, 8), (322928, 20), (374916, 4)), ram_literals=(322568, 322592, 322928), cases=14132, boundary=False, return_address_offset=None, return_register=5, base_load=None, symbols=(('INHIBIT', 'fuel_inhibit_mask/ram'), ('COMPENSATED', 'injection_0/ram'), ('TRANSFORMED', 'handsome-spaniel/ram'), ('OPENING', 'portable-kingfisher/ram'), ('ADDITIVE', 'berserk-ocelot/ram'), ('SUBTRACTIVE', 'apricot-raven/ram'), ('MULTIPLIER', 'over_run_channel_multiplier/tbl')), bits=(), constants=(('EARLY_ONLY', 0),), callees=((322596, 322732), (374764, 374916), (140536, 140552)), ram_word_literals=()),
    Region(key='jk08a-injection-prologue', rom='JK08A', source='stock_jk08a_injection_prologue.s', harness='harness-stock-jk08a-injection-prologue.c', start=177738, end=177760, pools=((178012, 2), (178276, 4)), ram_literals=(178276,), cases=1036, boundary=True, return_address_offset=None, return_register=5, base_load=None, symbols=(('CONTROL', 'provocative-anteater/ram'),), bits=(), constants=(('EARLY_ONLY', 0), ('WORD_ALIAS', 32512)), callees=(), ram_word_literals=((178012, 4294935788, 32512, 1),)),
    Region(key='jk08a-injection-count', rom='JK08A', source='stock_jk08a_injection_count.s', harness='harness-stock-jk08a-injection-count.c', start=177870, end=177912, pools=((167584, 2), (178014, 6), (178276, 4), (178284, 4), (178292, 4)), ram_literals=(178276, 178292), cases=10252, boundary=True, return_address_offset=24, return_register=11, base_load=None, symbols=(('COUNT', 'huge-lori/ram'), ('PERIOD', 'spry-koel/ram'), ('REMAINDER', 'economic-collie/ram'), ('OUTPUT', 'amphibian-panda/ram'), ('SCRATCH', 'injection_offset_reciprocal_residue/ram')), bits=(), constants=(('EARLY_ONLY', 0),), callees=((167548, 167582), (177994, 178006))),
    Region(key='jk08a-injection-dispatch', rom='JK08A', source='stock_jk08a_injection_dispatch.s', harness='harness-stock-jk08a-injection-dispatch.c', start=347404, end=347428, pools=((347598, 2), (347788, 4), (347804, 8)), ram_literals=(347788, 347804), cases=9292, boundary=True, return_address_offset=24, return_register=11, base_load=None, symbols=(('LEAD', 'bizarre-axolotl/ram'), ('FLAG', 'shaggy-nyala/ram')), bits=(), constants=(('EARLY_ONLY', 0),), callees=()),
    Region(key='jk08a-injection-catchup', rom='JK08A', source='stock_jk08a_injection_catchup.s', harness='harness-stock-jk08a-injection-catchup.c', start=347220, end=347336, pools=((140949, 6), (347582, 8), (347788, 8)), ram_literals=(347788, 347792), cases=11340, boundary=True, return_address_offset=None, return_register=5, base_load=None, symbols=(('CURSOR', 'lurking-swine/ram'), ('QUEUE', 'curvy-hyena/ram'), ('CLEAR', 'quantum-tiger/ram'), ('MASK_A', 'injection_catchup_mask_a/ram'), ('MASK_B', 'injection_catchup_mask_b/ram')), bits=(), constants=(('EARLY_ONLY', 0),), callees=()),
    Region(key='jk08a-injection-pending', rom='JK08A', source='stock_jk08a_injection_pending.s', harness='harness-stock-jk08a-injection-pending.c', start=347398, end=347404, pools=((140949, 6), (347162, 2), (347180, 2), (347184, 4), (347594, 2)), ram_literals=(347184,), cases=9216, boundary=True, return_address_offset=None, return_register=5, base_load=None, symbols=(('SLOT', 'acrid-bonobo/ram'), ('CURSOR', 'lurking-swine/ram'), ('PENDING', 'uber-deer/ram')), bits=(), constants=(('ZERO_ENTRY', 347100), ('NEGATIVE_ENTRY', 347150), ('EARLY_ONLY', 0)), callees=((347100, 347146), (347150, 347162))),
    Region(key='jk08a-injection-reciprocal', rom='JK08A', source='stock_jk08a_injection_reciprocal.s', harness='harness-stock-jk08a-injection-reciprocal.c', start=167548, end=167582, pools=((167584, 2),), ram_literals=(), cases=12826, boundary=False, return_address_offset=None, return_register=5, base_load=None, symbols=(('OUTPUT', 'amphibian-panda/ram'), ('REMAINDER', 'economic-collie/ram')), bits=(), constants=(('EARLY_ONLY', 0),), callees=()),
    Region(key='jk08a-injection-tooth', rom='JK08A', source='stock_jk08a_injection_tooth.s', harness='harness-stock-jk08a-injection-tooth.c', start=177760, end=177870, pools=((167582, 4), (167968, 4), (178014, 2), (178276, 16)), ram_literals=(167968, 178276, 178280), cases=12668, boundary=True, return_address_offset=24, return_register=11, base_load=None, symbols=(('COUNT', 'huge-lori/ram'), ('REMAINDER', 'economic-collie/ram'), ('MODE', 'apc_mode/ram'), ('POSITION', 'tunneling-doberman/ram')), bits=(), constants=(('DIRECT_ENTRY', 177782), ('NORMALIZER_ENTRY', 167368), ('EARLY_ONLY', 0)), callees=((167368, 167582),)),
    Region(key='jk08a-injection-offset', rom='JK08A', source='stock_jk08a_injection_offset.s', harness='harness-stock-jk08a-injection-offset.c', start=177876, end=177912, pools=((167584, 2), (178014, 6), (178276, 4), (178284, 4), (178292, 4)), ram_literals=(178276, 178292), cases=14118, boundary=True, return_address_offset=24, return_register=11, base_load=None, symbols=(('PERIOD', 'spry-koel/ram'), ('REMAINDER', 'economic-collie/ram'), ('OUTPUT', 'amphibian-panda/ram'), ('SCRATCH', 'injection_offset_reciprocal_residue/ram')), bits=(), constants=(('EARLY_ONLY', 0),), callees=((167548, 167582),)),
    Region(
        key="jk08a-injection-slot", rom="JK08A",
        source="stock_jk08a_injection_slot.s",
        harness="harness-stock-jk08a-injection-slot.c",
        start=0x00054A64, end=0x00054AC8,
        pools=((0x0002268E, 20), (0x00054B52, 4), (0x00054C30, 28)),
        ram_literals=(0x00054C38, 0x00054C40, 0x00054C44, 0x00054C48),
        cases=8508,
        symbols=(("CYLINDER", "knock_channel_primary/ram"),
                 ("LEAD", "fabulous-koel/ram"), ("MODE", "flawless-silkworm/ram"),
                 ("COUNTER", "arcane-chinchilla/ram"), ("HISTORY", "lime-caracara/ram"),
                 ("SLOT", "acrid-bonobo/ram")),
        constants=(("EARLY_ONLY", 0),),
    ),
    Region(
        key="jk08a-injection-snapshot", rom="JK08A",
        source="stock_jk08a_injection_snapshot.s",
        harness="harness-stock-jk08a-injection-snapshot.c",
        start=0x00021314, end=0x0002131C,
        pools=((0x000213A0, 8),), ram_literals=(0x000213A0, 0x000213A4),
        cases=1700, return_address_offset=24, return_register=7,
        symbols=(("LEAD_SOURCE", "flat-coyote/ram"),
                 ("ANGLE_SOURCE", "righteous-scorpion/ram"),
                 ("LEAD_SNAPSHOT", "fabulous-koel/ram"),
                 ("ANGLE_SNAPSHOT", "nippy-caribou/ram")),
        constants=(("EARLY_ONLY", 0),), callees=((0x00022558, 0x00022590),),
    ),
    Region(
        key="jk08a-injection-start-delay", rom="JK08A",
        source="stock_jk08a_injection_start_delay.s",
        harness="harness-stock-jk08a-injection-start-delay.c",
        start=0x000521A8, end=0x00052292, boundary=False,
        pools=((0x000083EA, 1), (0x00052296, 2),
               (0x00052298, 4), (0x0005229C, 4), (0x000522A0, 4),
               (0x000522A4, 4), (0x000522A8, 4), (0x000522AC, 4),
               (0x000522B0, 4), (0x000522B4, 4), (0x000522B8, 4),
               (0x000522BC, 4), (0x000522C0, 4),
               (0x00021CD8, 4), (0x00021CDC, 4),
               (0x00021F38, 4), (0x00021F3C, 4)),
        ram_literals=(0x00021CD8, 0x00021F38, 0x00052298,
                      0x0005229C, 0x000522A0, 0x000522A4,
                      0x000522AC, 0x000522B0, 0x000522C0),
        cases=6855,
        symbols=(('PRIMARY_SPEED', 'rpm/ram'), ('ALTERNATE_SPEED', 'rare-sawfly/ram'), ('PULSES', 'handsome-spaniel/ram'), ('FLOOR', 'devout-swift/ram'), ('END', 'injection_end_angle/ram'), ('SPEED_SELECTOR', 'futuristic-chinchilla/ram'), ('DELAY_CONTROL', 'apc_mode/ram'), ('LEAD_OVERRIDE', 'shaggy-nyala/ram'), ('ANGLE_OUTPUT', 'righteous-scorpion/ram'), ('LEAD_OUTPUT', 'flat-coyote/ram'), ('DELAY_CONFIG', 'injection_start_delay_decrement/tbl')),
        callees=((0x00021BBC, 0x00021CD6), (0x00021E14, 0x00021F38)),
    ),
    Region(
        key="jk08a-ltft-publication", rom="JK08A",
        source="stock_jk08a_ltft_publication.s",
        harness="harness-stock-jk08a-ltft-publication.c",
        start=0x00057B26, end=0x00057B7A, boundary=False,
        callees=((0x00057BD4, 0x00057C34), (0x00025E20, 0x00025E44)),
        pools=((0x00008E5A, 1), (0x00008E5B, 1), (0x00025F10, 4),
               (0x00057B7A, 2), (0x00057B7C, 2),
               (0x00057BC0, 4), (0x00057BC4, 4), (0x00057BC8, 4),
               (0x00057BCC, 4), (0x00057BD0, 4), (0x00057D1A, 2),
               (0x00057E34, 4), (0x00057E38, 4), (0x00057E3C, 4),
               (0x00057E40, 4), (0x00057E44, 4)),
        ram_literals=(0x00025F10, 0x00057BC0, 0x00057BC4, 0x00057BC8,
                      0x00057BCC, 0x00057E3C, 0x00057E40, 0x00057E44),
        cases=12028,
        symbols=(("SELECTED", "ltft_learned_b1/ram"),
                 ("ADJUSTMENT", "ltft_adjustment_b1/ram"),
                 ("OUTPUT", "ltft_b1/ram"), ("MASK", "logical-swan/ram"),
                 ("COMPARE_U", "gay-bloodhound/ram"),
                 ("COMPARE_V", "ltft_limit_comparison_word/ram"),
                 ("DIAGNOSTIC_RECORD", "tourmaline-jackal/ram"),
                 ("CONTROL_F", "ltft_publication_neutral_control/ram"),
                 ("CONTROL_G", "origami-iguana/ram"),
                 ("CONTROL_H", "onyx-jerboa/ram"),
                 ("CONTROL_K", "jovial-buzzard/ram"),
                 ("LOWER", "ltft_publication_lower_bound/tbl"),
                 ("UPPER", "ltft_publication_upper_bound/tbl")),
        constants=(("DIAGNOSTIC_BYTE1_OFFSET", 1),),
    ),
    Region(
        key="jk08a-knock-reference-learning", rom="JK08A",
        source="stock_jk08a_knock_reference_learning.s",
        harness="harness-stock-jk08a-knock-reference-learning.c",
        start=0x0004A118, end=0x0004A1FC, boundary=False,
        pools=((0x0000884B, 1), (0x00008B3D, 1), (0x00009282, 2),
               (0x00025F10, 4), (0x0004A1FC, 4), (0x0004A200, 4),
               (0x0004A208, 4), (0x0004A224, 4), (0x0004A228, 4),
               (0x0004A22C, 4), (0x0004A230, 4), (0x0004A234, 4)),
        ram_literals=(0x00025F10, 0x0004A200, 0x0004A208,
                      0x0004A22C, 0x0004A234),
        cases=7336,
        symbols=(("REFERENCES", "gigantic-goshawk/ram"),
                 ("SAMPLES", "knock_reference_samples/ram"),
                 ("PRIMARY", "knock_channel_primary/ram"),
                 ("ALTERNATE", "knock_channel_alternate/ram"),
                 ("DIAGNOSTICS", "hallowed-malkoha/ram"),
                 ("SELECTOR", "knock_selector_config/tbl"),
                 ("WEIGHT", "knock_reference_weight/tbl"),
                 ("RESET_WORD", "knock_reference_reset/tbl")),
        constants=(("PREDICATE_ENTRY", 0x00025E20),),
        callees=((0x00025E20, 0x00025E44),),
    ),
    Region(
        key="jk08a-bank-base-pulse", rom="JK08A",
        source="stock_jk08a_bank_base_pulse.s",
        harness="harness-stock-jk08a-bank-base-pulse.c",
        start=0x0004EAD4, end=0x0004EBA2,
        pools=((0x0000893D, 1), (0x00008940, 1),
               (0x0004EBE2, 2), (0x0004EBE4, 2),
               (0x0004EC00, 4), (0x0004EC04, 4), (0x0004EC08, 4),
               (0x0004EC18, 4), (0x0004EC1C, 4)),
        ram_literals=(0x0004EC00, 0x0004EC04, 0x0004EC08),
        cases=6184, boundary=False,
        symbols=(("STFT", "stft_b1/ram"), ("LTFT", "ltft_b1/ram"),
                 ("EXTRA", "astonishing-hoatzin/ram"),
                 ("PRECURSOR", "dainty-oriole/ram"),
                 ("ADDITIVE", "portable-kingfisher/ram"),
                 ("OFFSET", "provocative-cat/ram"),
                 ("CONTROL0", "dazzling-sawfly/ram"),
                 ("CONTROL1", "af_state_factor/ram"),
                 ("OUTPUT", "enlightened-mastodon/ram"),
                 ("LTFT_CONFIG", "bank_base_ltft_config/tbl"),
                 ("CONTROL_CONFIG", "bank_base_control_config/tbl")),
    ),
    Region(
        key="jk08a-knock-state-selection", rom="JK08A",
        source="stock_jk08a_knock_state_selection.s",
        harness="harness-stock-jk08a-knock-state-selection.c",
        start=0x00049614, end=0x0004964A,
        pools=((0x00009078, 2), (0x000493FC, 4),
               (0x000495DA, 2), (0x000495E8, 2), (0x000495F6, 2),
               (0x000495FA, 10), (0x00049610, 4),
               (0x0004965C, 4), (0x00049678, 4), (0x000496AC, 4),
               (0x000496B4, 4), (0x000496C0, 4), (0x000496C4, 4),
               (0x000499AE, 2), (0x00049B28, 4), (0x00049B2C, 4),
               (0x00049B38, 4), (0x00049B3C, 4)),
        ram_literals=(0x0004965C, 0x00049678, 0x000496AC,
                      0x00049B28, 0x00049B2C, 0x00049B38),
        cases=11615,
        symbols=(("SOURCE_STATE", "thick-dalmatian/ram"),
                 ("TARGET_STATE", "curious-mustang/ram"),
                 ("NEGATIVE_BOUND", "knock_state_negative_bound/ram"),
                 ("GATE69", "masked-inchworm/ram"),
                 ("GATE67", "glorious-spider/ram"),
                 ("WORD_OUTPUT", "knock_timing_state/ram"),
                 ("BYTE_OUTPUT", "steady-lionfish/ram"),
                 ("SLEW_STEP", "knock_state_slew_step/tbl")),
        constants=(("POST_LOOKUP_ENTRY", 0x00049614),
                   ("ALTERNATIVE_ENTRY", 0x000499B8)),
        callees=((0x000499B8, 0x00049A0E),),
    ),
    Region(
        key="jk08a-knock-event-publication", rom="JK08A",
        source="stock_jk08a_knock_event_publication.s",
        harness="harness-stock-jk08a-knock-event-publication.c",
        start=0x0004DB86, end=0x0004DB8E,
        pools=((0x0004D9A8, 4), (0x0004D9C2, 2), (0x0004DA7C, 2),
               (0x0004DBA0, 4), (0x0004DBAC, 4), (0x0004DBBC, 4),
               (0x0004DBE4, 4)),
        ram_literals=(0x0004DBA0, 0x0004DBAC, 0x0004DBBC, 0x0004DBE4),
        cases=8754,
        symbols=(("RETARD", "eccentric-badger/ram"),
                 ("SNAPSHOT", "liberal-gorilla/ram"),
                 ("CORRECTION", "lumpy-kudu/ram"),
                 ("SCALED_RAM", "artichoke-capuchin/ram"),
                 ("LONG_SUM", "venomous-oyster/ram"),
                 ("BYTE_OUTPUT", "viridian-koel/ram")),
        constants=(("PUBLICATION_ENTRY", 0x0004DB48),),
        callees=((0x0004DB48, 0x0004DB74),),
    ),
    Region(
        key="jk08a-knock-event-retard", rom="JK08A",
        source="stock_jk08a_knock_event_retard.s",
        harness="harness-stock-jk08a-knock-event-retard.c",
        start=0x0004D9AC, end=0x0004DA2A,
        pools=((0x00008710, 1), (0x0004DBA4, 4), (0x0004DBA8, 4),
               (0x0004DBAC, 4), (0x0004DBB0, 4), (0x0004DBB4, 4)),
        ram_literals=(0x0004DBA8, 0x0004DBAC, 0x0004DBB0, 0x0004DBB4),
        cases=7408,
        symbols=(("FIRST", "eccentric-badger/ram"),
                 ("SECOND", "wooden-aardwolf/ram"),
                 ("KNOCK_BYTE", "steady-lionfish/ram"),
                 ("REQUEST_A", "hopeful-hedgehog/ram"),
                 ("REQUEST_B", "aquamarine-leopard/ram"),
                 ("SOURCE_WORD", "athletic-coucal/ram"),
                 ("FLAG5", "utopian-grebe/ram"),
                 ("FLAGB", "muscular-malamute/ram"),
                 ("MODE", "event_retard_config/tbl")),
    ),
    Region(
        key="jk08a-knock-integration", rom="JK08A",
        source="stock_jk08a_knock_integration.s",
        harness="harness-stock-jk08a-knock-integration.c",
        start=0x0004956A, end=0x00049582,
        pools=((0x00008EAA, 2), (0x00008EAE, 2), (0x00049668, 4),
               (0x00049678, 4), (0x0004968C, 4), (0x00049690, 4),
               (0x00049694, 4), (0x00049698, 4), (0x00049938, 4),
               (0x0004995C, 4)),
        ram_literals=(0x00049668, 0x00049678, 0x0004968C, 0x00049690,
                      0x00049938), cases=4035,
        symbols=(("STATE", "thick-dalmatian/ram"),
                 ("OUTPUT", "curious-mustang/ram"),
                 ("COUNT", "knock_count/ram")),
        constants=(("QUIET_ENTRY", 0x00049544), ("EVENT_ENTRY", 0x00049900)),
        callees=((0x00049544, 0x00049568), (0x00049900, 0x00049912)),
    ),
    Region(
        key="jk08a-knock-timing-byte", rom="JK08A",
        source="stock_jk08a_knock_timing_byte.s",
        harness="harness-stock-jk08a-knock-timing-byte.c",
        start=0x000496CC, end=0x000496DA,
        pools=((0x000495DA, 2), (0x000496AC, 4), (0x000496C8, 4),
               (0x000499AE, 2), (0x00049B38, 4)),
        ram_literals=(0x000496C8,), cases=65650,
        symbols=(("WORD_STATE", "knock_timing_state/ram"),
                 ("BYTE_STATE", "steady-lionfish/ram")),
        constants=(("CONVERSION_ENTRY", 0x0004964A),),
        callees=((0x0004964A, 0x0004965C),),
    ),
    Region(
        key="jk08a-knock-comparison", rom="JK08A",
        source="stock_jk08a_knock_comparison.s",
        harness="harness-stock-jk08a-knock-comparison.c",
        start=0x0004A2EE, end=0x0004A386,
        pools=((0x00008B3D, 1), (0x0001108E, 194), (0x00015340, 32),
               (0x0002219C, 32), (0x000221D8, 8), (0x0002651C, 8),
               (0x000269C0, 4), (0x0004A1FC, 28), (0x0004A4C8, 12),
               (0x0004A4E4, 16)),
        ram_literals=(0x0004A200, 0x0004A208, 0x0004A214, 0x0004A4CC,
                      0x0004A4D0, 0x0004A4E4, 0x0004A4E8, 0x0004A4EC),
        cases=1100, return_address_offset=16, return_register=1,
        symbols=(("TABLE", "amorphous-bird/tbl"),
                 ("AXIS", "laughing-caterpillar/axis"),
                 ("MODE", "knock_selector_config/tbl"),
                 ("PRIMARY", "knock_channel_primary/ram"),
                 ("ALTERNATE", "knock_channel_alternate/ram"),
                 ("SPEED", "authentic-wasp/ram"),
                 ("THRESHOLDS", "knock_threshold_base/ram"),
                 ("METRICS", "knock_metric_base/ram"),
                 ("COUNT", "knock_count/ram"),
                 ("STATUS", "military-flamingo/ram"),
                 ("BITMAP", "knock_mask/ram")),
        constants=(("SHIFT_ENTRY", 0x000221BC), ("JUMP_TABLE", 0x0002219C)),
        callees=((0x00049FFC, 0x0004A04A), (0x000264F8, 0x0002651A),
                 (0x00026740, 0x0002676E), (0x00026984, 0x000269C0),
                 (0x00026C78, 0x00026D0E), (0x0004A3FE, 0x0004A438),
                 (0x000221BC, 0x000221D6), (0x000221E0, 0x000221F8)),
    ),
    Region(
        key="jk08a-knock-threshold",
        rom="JK08A",
        source="stock_jk08a_knock_threshold.s",
        harness="harness-stock-jk08a-knock-threshold.c",
        start=0x00049FFC,
        end=0x0004A04A,
        pools=((0x00008B3D, 1), (0x0001108E, 194), (0x00015340, 32),
               (0x0002651C, 8), (0x000269C0, 4), (0x0004A1FC, 28)),
        ram_literals=(0x0004A200, 0x0004A208, 0x0004A214),
        cases=829,
        boundary=False,
        symbols=(("TABLE", "amorphous-bird/tbl"),
                 ("AXIS", "laughing-caterpillar/axis"),
                 ("MODE", "knock_selector_config/tbl"),
                 ("PRIMARY", "knock_channel_primary/ram"),
                 ("ALTERNATE", "knock_channel_alternate/ram"),
                 ("SPEED", "authentic-wasp/ram"),
                 ("THRESHOLDS", "knock_threshold_base/ram")),
        constants=(("WRAPPER_ENTRY", 0x000264F8), ("LINEAR_ENTRY", 0x00026740),
                   ("AXIS_ENTRY", 0x00026984), ("DIVIDER_ENTRY", 0x00026C78)),
        callees=((0x000264F8, 0x0002651A), (0x00026740, 0x0002676E),
                 (0x00026984, 0x000269C0), (0x00026C78, 0x00026D0E)),
    ),
    Region(
        key="jk08a-bfs-rate",
        rom="JK08A",
        source="stock_jk08a_bfs_rate.s",
        harness="harness-stock-jk08a-bfs-rate.c",
        start=0x0003BB24,
        end=0x0003BB86,
        pools=((0x00008319, 2), (0x0000865A, 1), (0x00008D92, 1),
               (0x00025B98, 4), (0x0003B9D0, 8), (0x0003BB22, 2),
               (0x0003BBC4, 40)),
        ram_literals=(0x00025B98, 0x0003B9D0, 0x0003B9D4, 0x0003BBC8,
                      0x0003BBD0, 0x0003BBD4, 0x0003BBE8),
        cases=461,
        return_address_offset=24,
        return_register=1,
        symbols=(("Q7_SOURCE", "tall-quoll/ram"),
                 ("SELECTED_SOURCE", "fanatic-marten/ram"),
                 ("COEFFICIENT", "bfs_rate_coefficient/ram"),
                 ("REFERENCE", "flashy-elk/ram"),
                 ("WORKING", "elite-dormouse/ram"),
                 ("BLENDED", "wise-squirrel/ram"),
                 ("CORRECTION", "magenta-anaconda/ram"),
                 ("FLAGS", "bfs_state_flags/ram"),
                 ("ALPHA", "alpha_n_flow/ram"),
                 ("ENABLE", "burrowing-platypus/ram"),
                 ("DIAGNOSTIC", "busy-bird/ram"),
                 ("WEIGHT", "bfs_blend_weight/ram"),
                 ("BLEND_PRIOR", "nifty-otter/ram"),
                 ("TIMER_FIRST", "bfs_rate_timer_first/ram"),
                 ("TIMER_SECOND", "bfs_rate_timer_second/ram"),
                 ("TIMER_THIRD", "bfs_rate_timer_third/ram"),
                 ("SOURCE_FIRST", "slick-bullfinch/ram"),
                 ("SOURCE_SECOND", "macho-weasel/ram"),
                 ("MONITOR", "bfs_rate_timer_monitor/ram"),
                 ("MODE", "bfs_mode_flags/tbl"),
                 ("CORRECTION_GAIN", "bfs_correction_gain/tbl"),
                 ("LATCH_SET", "bfs_alpha_latch_set/tbl"),
                 ("LATCH_CLEAR", "bfs_alpha_latch_clear/tbl"),
                 ("QUERY_RECORDS", "hallowed-malkoha/ram"),
                 ("QUERY_ENTRY", "diagnostic_record_byte2_fault_predicate/fn")),
        constants=(("PRIMARY_ENTRY", 0x0003B908), ("CORRECTION_ENTRY", 0x0003BAB8),
                   ("BLEND_ENTRY", 0x0003BB3C), ("POST_QUERY_ENTRY", 0x0003BA6A),
                   ("PRIMARY_BASE", 0xFFFF1114), ("MODE_BASE", 0xFFFF2460)),
        callees=((0x0003B908, 0x0003B98C), (0x0003B9D8, 0x0003BB22),
                 (0x000224FA, 0x00022508), (0x000259E4, 0x00025A12)),
    ),
    Region(
        key="jk08a-fuel-compensation",
        rom="JK08A",
        source="stock_jk08a_fuel_compensation.s",
        harness="stock_fuel_compensation_harness.c",
        start=0x0003C284,
        end=0x0003C29E,
        pools=((0x0000851A,1),(0x000086F9,1),(0x00008B34,1),(0x00008B42,1),
               (0x0000A29A,256),(0x00011CF0,16),(0x00011D4C,16),(0x00026224,12),
               (0x000267C8,4),(0x00026980,4),(0x00026A08,4),
               (0x0003C26C,24),(0x0003C37C,20)),
        ram_literals=(0x0003C27C,0x0003C280,0x0003C38C),
        cases=3494,
        return_address_offset=4,
        symbols=(("RPM_SOURCE","authentic-wasp/ram"),("COL_SOURCE","alpha_n_flow/ram"),
                 ("OUTPUT","majestic-jackrabbit/ram"),
                 ("FIRST_SOURCE","fuel_compensation_bypass_first/ram"),
                 ("SECOND_SOURCE","fuel_compensation_bypass_second/ram"),
                 ("MODE_A","fuel_compensation_mode_a/tbl"),
                 ("MODE_B","fuel_compensation_mode_b/tbl"),
                 ("SOURCE_MODE","fuel_compensation_source_mode/tbl"),
                 ("BYPASS_SCALAR","fuel_compensation_bypass_scalar/tbl"),
                 ("TABLE","fuel_compensation_main/tbl"),
                 ("ROW_AXIS","fascinating-hog/axis"),("COL_AXIS","mellow-turtle/axis")),
        constants=(("SELECTOR_ENTRY",0x0003C1C0),("PRIMARY_BASE",0xFFFF1114),
                   ("WRAPPER_ENTRY",0x000261F0),("DIVIDER_ENTRY",0x00026C78)),
        callees=((0x000261F0,0x00026222),(0x00026740,0x0002676E),
                 (0x00026770,0x000267C6),(0x00026944,0x00026980),
                 (0x000269C4,0x00026A06),(0x00026C78,0x00026D0E),
                 (0x0003C1C0,0x0003C236)),
    ),
    Region(
        key="jk08a-bfs-limit",
        rom="JK08A",
        source="stock_jk08a_bfs_limit.s",
        harness="stock_bfs_limit_harness.c",
        start=0x0003BC78,
        end=0x0003BC80,
        pools=((0x0000974E, 12), (0x00012C9E, 16), (0x0002639A, 6),
               (0x00026ABC, 4), (0x0003BBD0, 4), (0x0003BDE4, 32)),
        ram_literals=(0x0003BBD0, 0x0003BDE4, 0x0003BDF0, 0x0003BDF4,
                      0x0003BDFC, 0x0003BE00),
        cases=969,
        return_address_offset=0,
        symbols=(("WORKING", "elite-dormouse/ram"), ("BLENDED", "wise-squirrel/ram"),
                 ("CORRECTION", "magenta-anaconda/ram"), ("FLAGS", "slick-bullfinch/ram"),
                 ("SPEED_BYTE", "angelic-shark/ram"), ("RPM_BYTE", "liberal-falcon/ram"),
                 ("THROTTLE_BYTE", "absolute_throttle/ram"), ("OUTPUT", "bfs/ram"),
                 ("CAP_BYTE", "bfs_upper_limit_raw/ram"),
                 ("LIMIT_TABLE", "lilac-magpie/tbl"), ("ALTERNATE_TABLE", "almond-orca/tbl")),
        constants=(("SELECTOR_ENTRY", 0x0003BB86), ("PRIMARY_BASE", 0xFFFF1DEC),
                   ("WRAPPER_ENTRY", 0x00026388),
                   ("BODY_ENTRY", 0x00026A84)),
        callees=((0x00026388, 0x0002639A), (0x00026740, 0x0002676E),
                 (0x00026A84, 0x00026ABA), (0x0003BB86, 0x0003BBC2),
                 (0x0003BBEC, 0x0003BC78)),
    ),
    Region(
        key="jk08a-bfs-base",
        rom="JK08A",
        source="stock_jk08a_bfs_base.s",
        harness="stock_bfs_base_harness.c",
        start=0x0003B8DA,
        end=0x0003B908,
        pools=((0x000088FB, 1), (0x00008A27, 1), (0x00009284, 2),
               (0x00021DC8, 8), (0x00022030, 8), (0x0003B8B8, 4),
               (0x0003B98C, 4), (0x0003B9A0, 32), (0x0003B9CC, 12)),
        ram_literals=(0x00021DC8, 0x00022030, 0x0003B9A0, 0x0003B9A4,
                      0x0003B9CC, 0x0003B9D0, 0x0003B9D4),
        cases=126,
        return_address_offset=24,
        symbols=(("AGGREGATE", "polar-viper/ram"), ("PRIMARY_SPEED", "vigorous-horse/ram"),
                 ("ALTERNATE_SPEED", "bfs_alternate_speed/ram"),
                 ("CONTROL_BYTE", "bfs_state_flags/ram"),
                 ("SPEED_FLAGS", "satisfied-bulldog/ram"),
                 ("QUARTER_BFS", "voracious-oarfish/ram"),
                 ("COMPENSATION", "majestic-jackrabbit/ram"),
                 ("COMPENSATED_BFS", "tall-quoll/ram"),
                 ("K_ADDRESS", "active-caracal/tbl"), ("FACTOR_ADDRESS", "spectral-corgi/tbl")),
        constants=(("PRIMARY_ENTRY", 0x0003B7C6), ("PRIMARY_BASE", 0xFFFF1DEC),
                   ("E_ADDRESS", 0x000088FB), ("DIVIDER_ENTRY", 0x00021CE0),
                   ("REMAINDER_ENTRY", 0x00021F40), ("FAULT_ADDRESS", 0xFFFF9818)),
        callees=((0x0003B7C6, 0x0003B8B8), (0x00021CE0, 0x00021DC6),
                 (0x00021F40, 0x0002202E)),
    ),
    Region(
        key="jk08a-maf-contribution",
        rom="JK08A",
        source="stock_jk08a_maf_contribution.s",
        harness="stock_maf_contribution_harness.c",
        start=0x0003AF42,
        end=0x0003B098,
        pools=((0x000082B6, 3), (0x000082BD, 1), (0x00008AC3, 1),
               (0x0003B098, 2), (0x0003B0F0, 2), (0x0003B10C, 32), (0x0003B37C, 16)),
        ram_literals=(0x0003B10C, 0x0003B110, 0x0003B114, 0x0003B118, 0x0003B11C),
        cases=260,
        boundary=False,
        symbols=(("MAF_INPUT_B1", "vegan-polecat/ram"),
                 ("MAF_INPUT_B2", "spiked-dalmatian/ram"),
                 ("MAF_OUTPUT_B1", "jasper-walrus/ram"),
                 ("MAF_OUTPUT_B2", "imposing-auk/ram"),
                 ("ENABLE_FLAGS", "burrowing-platypus/ram"),
                 ("DIAGNOSTIC_FLAGS", "slick-bullfinch/ram"),
                 ("INHIBIT_FLAGS", "splendid-cheetah/ram"),
                 ("BASE_B1", "maf_base_b1/ram"), ("BASE_B2", "maf_base_b2/ram"),
                 ("REFERENCE_B1", "maf_base_reference_b1/ram"),
                 ("REFERENCE_B2", "maf_base_reference_b2/ram"),
                 ("FALLBACK_B1", "maf_fallback_reference_b1/ram"),
                 ("FALLBACK_B2", "maf_fallback_reference_b2/ram"),
                 ("DELTA_B1", "maf_delta_reference_b1/ram"),
                 ("DELTA_B2", "maf_delta_reference_b2/ram"),
                 ("CORRECTION_B1", "maf_correction_state_b1/ram"),
                 ("CORRECTION_B2", "maf_correction_state_b2/ram"),
                 ("MAGNITUDE_B1", "maf_residual_magnitude_b1/ram"),
                 ("MAGNITUDE_B2", "maf_residual_magnitude_b2/ram"),
                 ("SIGN_FLAGS", "maf_residual_signs/ram"),
                 ("LATCH_B1", "maf_fallback_latch_b1/ram"),
                 ("LATCH_B2", "maf_fallback_latch_b2/ram")),
        constants=(("TAIL_ENTRY", 0x0003B042), ("CONTRIBUTION_BASE", 0xFFFF1DEC),
                   ("COEFFICIENT_ADDRESS", 0x000082B6), ("FALLBACK_WEIGHT_ADDRESS", 0x00008AC3)),
        callees=((0x0003B09A, 0x0003B0F0), (0x0003B12C, 0x0003B224),
                 (0x000224FA, 0x00022508)),
    ),
    Region(
        key="jk08a-load-snapshot",
        rom="JK08A",
        source="stock_jk08a_load_snapshot.s",
        harness="stock_load_snapshot_harness.c",
        start=0x00020F04,
        end=0x00020F1C,
        pools=((0x0002110C, 24), (0x00022110, 4), (0x00022174, 4)),
        ram_literals=(0x0002110C, 0x00021110, 0x00021114, 0x00021118, 0x00021120),
        cases=11,
        return_address_offset=0,
        symbols=(("BFS_NEWEST", "bfs/ram"), ("BFS_CURRENT", "kickass-mole/ram"),
                 ("BFS_PREVIOUS", "micro-chicken/ram"),
                 ("LIVE_LOAD", "benign-cassowary/ram"),
                 ("SNAPSHOT_LOAD", "normalized_load/ram")),
        constants=(("COPY_SIZE", 28),),
        callees=((0x00022104, 0x00022110), (0x0002213A, 0x00022158)),
    ),
    Region(
        key="jk08a-load-normalization",
        rom="JK08A",
        source="stock_jk08a_load_normalization.s",
        harness="stock_load_normalization_harness.c",
        start=0x0003BD1C,
        end=0x0003BD5C,
        pools=((0x00009534, 2), (0x00021DC8, 8),
               (0x0003BDF0, 4), (0x0003BE10, 12)),
        ram_literals=(0x00021DC8, 0x0003BDF0, 0x0003BE10),
        cases=44,
        return_address_offset=0,
        symbols=(("BFS_INPUT", "bfs/ram"), ("LIVE_LOAD", "benign-cassowary/ram"),
                 ("REFERENCE_ADDRESS", "precise-nuthatch/tbl")),
        constants=(("DIVIDER_ENTRY", 0x00021CE0), ("FAULT_ADDRESS", 0xFFFF9818)),
        callees=((0x00021CE0, 0x00021DC6),),
    ),
    Region(
        key="jk08a-maf-aggregate",
        rom="JK08A",
        source="stock_jk08a_maf_aggregate.s",
        harness="stock_maf_aggregate_harness.c",
        start=0x0003B252,
        end=0x0003B27E,
        pools=((0x0003B390, 8),),
        ram_literals=(0x0003B390, 0x0003B394),
        cases=32,
        boundary=False,
        symbols=(("MAF_BANK1", "jasper-walrus/ram"),
                 ("MAF_BANK2", "imposing-auk/ram"),
                 ("MAF_CORRECTION", "mindful-goose/ram"),
                 ("MAF_AUXILIARY", "wondrous-sparrow/ram"),
                 ("MAF_AGGREGATE", "polar-viper/ram")),
    ),
    Region(
        key="jk08a-maf-filter",
        rom="JK08A",
        source="stock_jk08a_maf_filter.s",
        harness="stock_maf_filter_harness.c",
        start=0x0003A982,
        end=0x0003A9AA,
        pools=((0x0000870A, 1), (0x0003AB68, 4), (0x0003AB70, 12)),
        ram_literals=(0x0003AB68, 0x0003AB70, 0x0003AB74),
        cases=110,
        boundary=False,
        symbols=(("MAF_SOURCE_B1", "vague-pony/ram"),
                 ("MAF_SOURCE_B2", "opalescent-pronghorn/ram"),
                 ("MAF_WORKING_B1", "precious-adder/ram"),
                 ("MAF_WORKING_B2", "dancing-hippo/ram"),
                 ("MAF_FILTERED_B1", "vegan-polecat/ram"),
                 ("MAF_FILTERED_B2", "spiked-dalmatian/ram"),
                 ("MODE_FLAGS", "satisfied-bulldog/ram"),
                 ("FILTER_ENTRY", "sandy-chameleon/fn")),
        constants=(("COPY_CAP_ENTRY", 0x0003A996), ("ANTI_STALL_ENTRY", 0x0003A9EC),
                   ("COEFFICIENT_ADDRESS", 0x0000870A), ("FILTER_BASE", 0xFFFF1DEC)),
        callees=((0x0003A9AA, 0x0003AA12),),
    ),
    Region(
        key="jk08a-maf-transfer",
        rom="JK08A",
        source="stock_jk08a_maf_transfer.s",
        harness="stock_maf_transfer_harness.c",
        start=0x0003A922,
        end=0x0003A950,
        pools=((0x000086F9, 1), (0x00008782, 1), (0x00008B3F, 1),
               (0x000141F4, 256), (0x00026424, 2), (0x00026428, 4),
               (0x00026ABC, 4), (0x0003AB60, 16), (0x0003B374, 2),
               (0x0003B3AC, 16), (0x0003B3E8, 12)),
        ram_literals=(0x0003AB68, 0x0003B3AC, 0x0003B3EC, 0x0003B3F0),
        cases=82,
        return_address_offset=0,
        symbols=(("MAF_INPUT_B1", "ginger-stingray/ram"),
                 ("MAF_INPUT_B2", "careful-penguin/ram"),
                 ("MAF_OUTPUT_B1", "vague-pony/ram"),
                 ("MAF_OUTPUT_B2", "opalescent-pronghorn/ram"),
                 ("MAF_TABLE_B1", "wealthy-woodlouse/tbl"),
                 ("MAF_TABLE_B2", "ivory-gecko/tbl"),
                 ("CURVE_ENTRY", "xanthic-kagu/fn")),
        constants=(("BODY_ENTRY", 0x00026A74), ("INPUT_BASE", 0xFFFF1E1C),
                   ("CORRECTION_OUTPUT", 0xFFFF1E2A)),
        callees=((0x00026410, 0x00026424), (0x00026740, 0x0002676E),
                 (0x00026A74, 0x00026ABA), (0x0003B320, 0x0003B374),
                 (0x0003B376, 0x0003B37C), (0x0003B3BC, 0x0003B3E6)),
    ),
    Region(
        key="jk08a-maf-compensation",
        rom="JK08A",
        source="stock_jk08a_maf_compensation.s",
        harness="stock_maf_compensation_harness.c",
        start=0x0003AE8A,
        end=0x0003AF42,
        pools=((0x00009586, 2), (0x0000958C, 2), (0x00021DC8, 8), (0x0003B0F8, 20)),
        ram_literals=(0x00021DC8, 0x0003B0F8, 0x0003B0FC, 0x0003B100),
        cases=90,
        boundary=False,
        symbols=(("MAF_INPUT_B1", "maf_b1/ram"), ("MAF_INPUT_B2", "maf_b2/ram"),
                 ("MAF_OUTPUT_B1", "ginger-stingray/ram"),
                 ("MAF_OUTPUT_B2", "careful-penguin/ram"),
                 ("CORRECTION_B1", "annoying-foxhound/ram"),
                 ("CORRECTION_B2", "unselfish-okapi/ram"),
                 ("INIT_FLAGS", "shapeless-bandicoot/ram"),
                 ("DIVIDER_ENTRY", "unsigned_divide/fn")),
        constants=(("ZERO_DEN_ENTRY", 0x0003AEF2), ("MULTIPLIER_ADDRESS", 0x00009586),
                   ("BIAS_ADDRESS", 0x0000958C), ("FAULT_ADDRESS", 0xFFFF9818)),
        callees=((0x00021CE0, 0x00021DC6),),
    ),
    Region(
        key="jk08a-battery-scaling",
        rom="JK08A",
        source="stock_jk08a_maf_scaling.s",
        harness="stock_battery_scaling_harness.c",
        start=0x00039A9E,
        end=0x00039AEE,
        pools=((0x000087F8, 2), (0x000092BE, 2), (0x00039BDC, 2),
               (0x00039CAC, 20), (0x000671C6, 18), (0x0006726A, 6)),
        ram_literals=(0x00039CAC, 0x00039CB0, 0x00039CBC, 0x000671C8,
                      0x000671CC, 0x0006726C),
        cases=32,
        boundary=False,
        symbols=(("BATTERY_SAMPLE", "eager-alligator/ram"),
                 ("BATTERY_COPY", "crouching-mole/ram"),
                 ("BATTERY_BYTE", "amaranth-swine/ram"),
                 ("BATTERY_OUTPUT", "battery_voltage/ram"),
                 ("COEFFICIENT", "satisfied-oarfish/ram"),
                 ("MODE_FLAGS", "shrewd-manul/ram")),
        callees=((0x00067188, 0x000671C6), (0x000671D8, 0x00067202)),
    ),
    Region(
        key="jk08a-maf-scaling",
        rom="JK08A",
        source="stock_jk08a_maf_scaling.s",
        harness="stock_maf_scaling_harness.c",
        start=0x0003C408,
        end=0x0003C45C,
        pools=((0x000087F8, 2), (0x000092BE, 2), (0x0003C474, 2),
               (0x0003C48C, 16), (0x000671C6, 18), (0x0006726A, 6)),
        ram_literals=(0x0003C490, 0x0003C498, 0x000671C8, 0x000671CC, 0x0006726C),
        cases=107,
        boundary=False,
        symbols=(("MAF_SAMPLE_B1", "enthusiastic-pillbug/ram"),
                 ("MAF_SAMPLE_B2", "hairy-dalmatian/ram"),
                 ("MAF_OUTPUT_B1", "maf_b1/ram"), ("MAF_OUTPUT_B2", "maf_b2/ram"),
                 ("COEFFICIENT", "satisfied-oarfish/ram"),
                 ("MODE_FLAGS", "shrewd-manul/ram")),
        constants=(("GUARD_ENTRY", 0x00067188), ("SCALE_ENTRY", 0x000671D8),
                   ("CAP_ENTRY", 0x0003C444), ("BOUNDS_ADDRESS", 0x000087F8),
                   ("DEFAULT_ADDRESS", 0x000092BE)),
        callees=((0x00067188, 0x000671C6), (0x000671D8, 0x00067202)),
    ),
    Region(
        key="jk08a-maf-adc",
        rom="JK08A",
        source="stock_jk08a_maf_adc.s",
        harness="stock_maf_adc_harness.c",
        start=0x000280B6,
        end=0x000280D8,
        pools=((0x000283E8, 4),),
        ram_literals=(0x000283E8,),
        cases=12,
        boundary=False,
        symbols=(("ADDR4", "real-sawfish/reg"), ("ADDR15", "zircon-stallion/reg"),
                 ("MAF_SAMPLE_B1", "enthusiastic-pillbug/ram"),
                 ("MAF_SAMPLE_B2", "hairy-dalmatian/ram")),
        constants=(("ADC_BASE", 0xFFFFF800),),
    ),
    Region(
        key="jk08a-direct-byte-axis",
        rom="JK08A",
        source="stock_jk08a_direct_byte_axis.s",
        harness="stock_direct_byte_axis_harness.c",
        start=0x00026944,
        end=0x00026980,
        pools=((0x00026980, 4),),
        ram_literals=(),
        cases=29,
        boundary=False,
        symbols=(("CVTC_RPM_AXIS", "scrupulous-ladybug/axis"),
                 ("CVTC_LOAD_AXIS", "witty-bobcat/axis")),
        constants=(("LAST_OFFSET", 15), ("AXIS_BYTES", 16), ("DIVIDER_ENTRY", 0x00026C78)),
        callees=((0x00026C78, 0x00026D0E),),
    ),
    Region(
        key="jk08a-implicit-byte-curve",
        rom="JK08A",
        source="stock_jk08a_implicit_byte_curve.s",
        harness="stock_implicit_byte_curve_harness.c",
        start=0x00026370,
        end=0x00026382,
        pools=((0x00026382, 2), (0x00026384, 4), (0x00026ABC, 4)),
        ram_literals=(),
        cases=40,
        boundary=False,
        symbols=(("INJECTION_TABLE", "tangible-gharial/tbl"),
                 ("COLD_TIMING_TABLE", "cold_idle_ignition_timing/tbl")),
        constants=(("BODY_ENTRY", 0x00026A80),),
        callees=((0x00026740, 0x0002676E), (0x00026A80, 0x00026ABA)),
    ),
    Region(
        key="jk08a-byte-axis",
        rom="JK08A",
        source="stock_jk08a_byte_axis.s",
        harness="stock_byte_axis_harness.c",
        start=0x000269C4,
        end=0x00026A06,
        pools=((0x00026A08, 4),),
        ram_literals=(),
        cases=38,
        boundary=False,
        symbols=(("FUEL_AXIS", "fascinating-hog/axis"),
                 ("IGNITION_AXIS", "able-butterfly/axis")),
        constants=(("LAST_OFFSET", 15), ("AXIS_BYTES", 16), ("DIVIDER_ENTRY", 0x00026C78)),
        callees=((0x00026C78, 0x00026D0E),),
    ),
    Region(
        key="jk08a-word-axis",
        rom="JK08A",
        source="stock_jk08a_word_axis.s",
        harness="stock_word_axis_harness.c",
        start=0x00026984,
        end=0x000269C0,
        pools=((0x000269C0, 4),),
        ram_literals=(),
        cases=22,
        boundary=False,
        symbols=(("TORQUE_AXIS", "functional-jackrabbit/axis"),),
        constants=(("LAST_OFFSET", 30), ("AXIS_BYTES", 32), ("DIVIDER_ENTRY", 0x00026C78)),
        callees=((0x00026C78, 0x00026D0E),),
    ),
    Region(
        key="jk08a-crank-capture",
        rom="JK08A",
        source="stock_jk08a_crank_capture.s",
        harness="stock_crank_capture_harness.c",
        start=0x00028F16,
        end=0x00028F4E,
        pools=((0x0002900C, 10), (0x0002903C, 4)),
        ram_literals=(0x0002903C,),
        cases=16,
        symbols=(
            ("OSBR1", "atu1_osbr1/reg"),
            ("CRANK_CAPTURE", "soft-seagull/ram"),
            ("RAW_PERIOD", "pistachio-porcupine/ram"),
            ("CAPTURE_FLAGS", "crank_capture_state/ram"),
        ),
        bits=(("INIT_MASK", "crank_capture_state/ram", "initialized"),),
        constants=(("CRANK_BASE", 0xFFFF128C), ("CORE_BASE", 0xFFFF1FF4),
                   ("MMIO_BASE", 0xFFFFF440), ("REFERENCE_PERIOD", 0xFFFF2294)),
    ),
    Region(
        key="jk08a-tooth-normalization",
        rom="JK08A",
        source="stock_jk08a_tooth_normalization.s",
        harness="stock_tooth_normalization_harness.c",
        start=0x0002915C,
        end=0x00029168,
        pools=((0x0002914A, 0x12), (0x0002920E, 6)),
        ram_literals=(),
        cases=20,
        symbols=(
            ("TOOTH_COUNTER", "tunneling-doberman/ram"),
            ("RAW_PERIOD", "pistachio-porcupine/ram"),
            ("NORMALIZED_PERIOD", "spry-koel/ram"),
        ),
        bits=(("SYNC_MASK", "engine_sync_flags/ram", "synchronized"),),
        constants=(("NORMALIZATION_ENTRY", 0x0002911C), ("REFERENCE_PERIOD", 0xFFFF2296),
                   ("CRANK_BASE", 0xFFFF128C), ("CORE_BASE", 0xFFFF1FF4)),
        # The selection path enters before its pool words and branches to
        # the ordinary copy or to the return boundary after both paths.
        callees=((0x0002911C, 0x0002914A),),
    ),
    Region(
        key="jk08a-tooth-fallback",
        rom="JK08A",
        source="stock_jk08a_tooth_fallback.s",
        harness="stock_tooth_fallback_harness.c",
        start=0x0002B800,
        end=0x0002B820,
        pools=((0x00021DC8, 8), (0x0002B85E, 6), (0x0002B878, 12)),
        ram_literals=(0x00021DC8, 0x0002B878, 0x0002B880),
        cases=13,
        return_address_offset=8,
        symbols=(
            ("EVENT_INTERVAL", "imported-kudu/ram"),
            ("RAW_PERIOD", "pistachio-porcupine/ram"),
            ("NORMALIZED_PERIOD", "spry-koel/ram"),
            ("CAM_INTERVAL", "berserk-woodlouse/ram"),
        ),
        constants=(("CORE_BASE", 0xFFFF1FF4),),
        callees=((0x00021CE0, 0x00021DC6),),
    ),
    Region(
        key="jk08a-event-interval",
        rom="JK08A",
        source="stock_jk08a_event_interval.s",
        harness="stock_event_interval_harness.c",
        start=0x00028AFA,
        end=0x00028B42,
        pools=((0x00028B42, 4), (0x00028B48, 0x14)),
        ram_literals=(0x00028B48, 0x00028B4C, 0x00028B50,
                      0x00028B54, 0x00028B58),
        cases=18,
        boundary=False,
        symbols=(
            ("MODE_FLAGS", "apc_mode/ram"),
            ("CURRENT_CAPTURE", "classy-bull/ram"),
            ("PREVIOUS_CAPTURE", "busy-horse/ram"),
            ("EVENT_INTERVAL", "imported-kudu/ram"),
            ("PUBLISHED_FLAGS", "eggplant-curassow/ram"),
            ("HOLDOFF", "event_interval_holdoff/ram"),
        ),
    ),
    Region(
        key="jk08a-rpm-median",
        rom="JK08A",
        source="stock_jk08a_rpm_median.s",
        harness="stock_rpm_median_harness.c",
        start=0x0003DF2C,
        end=0x0003DFC6,
        pools=((0x00021CD8, 8), (0x0003E018, 8), (0x0003E148, 0x1C)),
        ram_literals=(0x00021CD8, 0x0003E148, 0x0003E14C,
                      0x0003E158, 0x0003E15C, 0x0003E160),
        cases=35,
        boundary=False,
        symbols=(
            ("MODE_FLAGS", "apc_mode/ram"),
            ("TOOTH_PERIOD", "spry-koel/ram"),
            ("MEDIAN_OUTPUT", "statuesque-husky/ram"),
            ("LIVE_SPEED", "angelic-shark/ram"),
            ("HISTORY_NEWEST", "meek-iguana/ram"),
            ("DIVIDER_ENTRY", "pompous-firefly/fn"),
        ),
        constants=(("FAULT_POINTER", 0x00021CD8), ("FAULT_VALUE", 0x00021CDC),
                   ("HISTORY_PREVIOUS", 0xFFFF3E35), ("HISTORY_OLDER", 0xFFFF3E36)),
        callees=((0x00021BBC, 0x00021CD6),),
    ),
    Region(
        key="jk08a-rpm-division",
        rom="JK08A",
        source="stock_jk08a_rpm_division.s",
        harness="stock_rpm_division_harness.c",
        start=0x00038272,
        end=0x0003829E,
        pools=((0x00021DC8, 8), (0x00038370, 0x14)),
        ram_literals=(0x00021DC8, 0x00038370, 0x00038374, 0x00038380),
        cases=20,
        boundary=False,
        symbols=(
            ("MODE_FLAGS", "nice-silkworm/ram"),
            ("EVENT_INTERVAL", "imported-kudu/ram"),
            ("ENGINE_SPEED", "classic-caracal/ram"),
            ("DIVIDER_ENTRY", "unsigned_divide/fn"),
        ),
        constants=(("FAULT_POINTER", 0x00021DC8), ("FAULT_VALUE", 0x00021DCC)),
        callees=((0x00021CE0, 0x00021DC6),),
    ),
    Region(
        key="jk08a-rpm-drop-arithmetic",
        rom="JK08A",
        source="stock_jk08a_rpm_drop.s",
        harness="stock_rpm_drop_harness.c",
        start=0x0003E1FE,
        end=0x0003E26C,
        pools=((0x0003E3CC, 4), (0x0003E3DC, 4)),
        ram_literals=(0x0003E3CC,),
        cases=14,
        symbols=(
            ("DROP_WORD", "satisfied-macaque/ram"),
            ("CURRENT_SPEED", "sophisticated-magpie/ram"),
            ("HISTORY_SPEED", "cinnamon-crayfish/ram"),
            ("PREVIOUS_DROP", "teal-curassow/ram"),
        ),
        constants=(("DROP_COEFFICIENT", 0x000084A4),),
    ),
    Region(
        key="jk78c-ascd-main",
        rom="JK78C",
        source="stock_jk78c_ascd_main.s",
        harness="stock_ascd_main_harness.c",
        start=0x000FCBB0,
        end=0x000FCBEE,
        pools=((0x000FCD60, 0x10),),
        ram_literals=(0x000FCD60, 0x000FCD6C),
        cases=8,
        base_load=0x000FC9CA,
        symbols=(
            ("ASCD_FLAGS", "ascd_state/ram"),
            ("BUTTON_STATE", "button_state/ram"),
        ),
        bits=(("ASCD_MAIN_MASK", "ascd_state/ram", "main"),),
    ),
    # The main RPM fuel-cut state machines of the two relocated 8MFK layouts:
    # the delay counter, the pair selector, the configuration byte, and the
    # delay byte have no symbols on them.
    Region(
        key="jk00c-rpm-fuel-cut",
        rom="JK00C",
        source="stock_jk00c_rpm_fuel_cut.s",
        harness="stock_rpm_fuel_cut_harness.c",
        start=0x00050BF8,
        end=0x00050C9A,
        pools=((0x00050D68, 4), (0x00050D88, 0x10)),
        ram_literals=(0x00050D68, 0x00050D88),
        cases=14,
        boundary=False,
        symbols=FUEL_CUT_SYMBOLS,
        bits=FUEL_CUT_BITS,
        constants=(
            ("DELAY_COUNTER", 0xFFFF2579),
            ("PAIR_SELECTOR", 0xFFFF24EC),
            ("CUT_CONFIG", 0x00008B6B),
            ("CUT_DELAY", 0x00008C97),
        ),
    ),
    Region(
        key="jk00d-rpm-fuel-cut",
        rom="JK00D",
        source="stock_jk00d_rpm_fuel_cut.s",
        harness="stock_rpm_fuel_cut_harness.c",
        start=0x00050BF4,
        end=0x00050C96,
        pools=((0x00050D64, 4), (0x00050D84, 0x10)),
        ram_literals=(0x00050D64, 0x00050D84),
        cases=14,
        boundary=False,
        symbols=FUEL_CUT_SYMBOLS,
        bits=FUEL_CUT_BITS,
        constants=(
            ("DELAY_COUNTER", 0xFFFF2581),
            ("PAIR_SELECTOR", 0xFFFF24F4),
            ("CUT_CONFIG", 0x00008B6C),
            ("CUT_DELAY", 0x00008C99),
        ),
    ),
    Region(
        key='jk08a-knock-metric', rom="JK08A",
        source='stock_jk08a_knock_metric.s',
        harness='harness-stock-jk08a-knock-metric.c',
        start=0x0004a2b6, end=0x0004a2ee,
        pools=((0x00049fc0, 60), (0x0004a4c8, 4), (0x0004a4cc, 4), (0x0004a4d0, 4), (0x0004a4d8, 4), (0x0004a4dc, 4), (0x0004a4e0, 4), (0x0002219c, 32), (0x000221d8, 8), (0x0004a24c, 12), (0x0004a296, 2), (0x0004a29c, 2), (0x0004a3da, 2), (0x0004a3e0, 2), (0x00008618, 1), (0x00008870, 1), (0x00008b3d, 1), (0x000086a7, 1), (0x00008694, 1), (0x000086ac, 1)),
        ram_literals=(0x00049fd0, 0x00049fd4, 0x00049fd8, 0x00049fdc, 0x00049ff0, 0x00049ff4, 0x0004a4cc, 0x0004a4d0, 0x0004a4d8, 0x0004a4dc, 0x0004a4e0),
        cases=9404, return_address_offset=24, return_register=1,
        constants=(("TOP_THREE_ENTRY", 0x00049d88), ("SCALER_ENTRY", 0x00049e96)),
        callees=((0x0004a496, 0x0004a4c8), (0x00049d88, 0x00049e96), (0x00049e96, 0x00049fc0), (0x000221bc, 0x000221d6), (0x000221e0, 0x000221f8)),
    ),
    Region(
        key='jk08a-knock-normalization', rom="JK08A",
        source='stock_jk08a_knock_normalization.s',
        harness='harness-stock-jk08a-knock-normalization.c',
        start=0x0004a26a, end=0x0004a2b6,
        pools=((0x0004a4cc, 4), (0x0004a4d0, 4), (0x0004a4d4, 4), (0x0004a4d8, 4), (0x0004a4f4, 4), (0x0004a4f8, 4), (0x0004a590, 4), (0x0004a594, 4), (0x0004a598, 4), (0x0004a59c, 4), (0x0004a5a0, 4), (0x0004a5a4, 4), (0x0004a5a8, 4), (0x0004a24c, 12), (0x0004a25c, 14), (0x0004a3a0, 16), (0x0004a4c8, 4), (0x00008b3d, 1)),
        ram_literals=(0x0004a4cc, 0x0004a4d0, 0x0004a4d4, 0x0004a4d8, 0x0004a4f4, 0x0004a590, 0x0004a594, 0x0004a598, 0x0004a59c, 0x0004a5a0, 0x0004a5a8),
        cases=6563, return_address_offset=24, return_register=1,
        constants=(("ALTERNATE_ENTRY", 0x0004a3b0),),
        callees=((0x0004a3b0, 0x0004a3fe), (0x0004a438, 0x0004a496), (0x0004a4fc, 0x0004a58e), (0x00021ce0, 0x00021d6a)),
    ),
    Region(
        key='jk08a-stft-publication', rom='JK08A',
        source='stock_jk08a_stft_publication.s', harness='harness-stock-jk08a-stft-publication.c',
        start=0x5ca08, end=0x5ca5e,
        pools=((0x5ca5e, 0x2), (0x5ca6c, 0x2), (0x5ca84, 0x4), (0x5ca88, 0x4)),
        ram_literals=(0x5ca84, 0x5ca88),
        cases=6160, boundary=False, constants=(('MODE_ALIAS', 0x7f40), ('FORCE_ALIAS', 0x7f50), ('EARLY_ONLY', 0)),
        ram_word_literals=((0x5ca5e, 0xffff99c4, 0x7f40, 1), (0x5ca6c, 0xffff9924, 0x7f50, 2)),
    ),
    Region(
        key='jk08a-grid-selection', rom='JK08A',
        source='stock_jk08a_grid_selection.s', harness='harness-stock-jk08a-grid-selection.c',
        start=0x5796c, end=0x57ace,
        pools=((0x839c, 0x2), (0x881a, 0x2), (0x88f5, 0x1), (0x8a9e, 0x2), (0x12592, 0x8), (0x126dc, 0x8), (0x25f10, 0x4), (0x57ace, 0x2), (0x57b80, 0x4), (0x57b84, 0x4), (0x57b88, 0x4), (0x57b8c, 0x4), (0x57b90, 0x4), (0x57b94, 0x4), (0x57b98, 0x4), (0x57b9c, 0x4), (0x57ba0, 0x4), (0x57ba4, 0x4), (0x57ba8, 0x4), (0x57bac, 0x4), (0x57bb0, 0x4), (0x57bb4, 0x4), (0x57bb8, 0x4), (0x57bbc, 0x4), (0x57bc0, 0x4), (0x58344, 0x4), (0x58348, 0x4), (0x5834c, 0x4), (0x58350, 0x4)),
        ram_literals=(0x25f10, 0x57b80, 0x57b88, 0x57b90, 0x57b9c, 0x57ba0, 0x57bac, 0x57bb4, 0x57bb8, 0x57bbc, 0x57bc0, 0x58348),
        cases=10840, boundary=False, constants=(('EARLY_ONLY', 0),),
        callees=((0x57ad0, 0x57b26), (0x58092, 0x580c2), (0x580e8, 0x58168), (0x25e20, 0x25e44)),
    ),
    Region(
        key='jk08a-grid-learning', rom='JK08A',
        source='stock_jk08a_grid_learning.s', harness='harness-stock-jk08a-grid-learning.c',
        start=0x57d1e, end=0x57e30,
        pools=((0x839c, 0x2), (0x88f5, 0x1), (0x8a9d, 0x3), (0x129c6, 0x4), (0x57e30, 0x2), (0x57e68, 0x4), (0x57e74, 0x4), (0x57e78, 0x4), (0x57e7c, 0x4), (0x57e80, 0x4), (0x57e84, 0x4), (0x57e88, 0x4), (0x57e8c, 0x4), (0x57e90, 0x4), (0x57e94, 0x4), (0x57e98, 0x4), (0x57e9c, 0x4), (0x57ea0, 0x4), (0x580c4, 0x4), (0x580c8, 0x4), (0x580cc, 0x4), (0x580d0, 0x4), (0x580d4, 0x4), (0x58344, 0x4), (0x58348, 0x4), (0x5834c, 0x4), (0x58350, 0x4)),
        ram_literals=(0x57e68, 0x57e74, 0x57e78, 0x57e7c, 0x57e80, 0x57e8c, 0x57e94, 0x57e98, 0x580c4, 0x580c8, 0x580cc, 0x580d0, 0x580d4, 0x58348),
        cases=9856, boundary=False, constants=(('EARLY_ONLY', 0),),
        callees=((0x57ea4, 0x57eee), (0x58092, 0x580c2), (0x580e8, 0x58168), (0x22590, 0x2259a)),
    ),
)


class VerificationError(RuntimeError):
    """Raised when a stock-code executable contract fails."""


def stock_image(rom):
    """The bytes of the stock image of a ROM after its digest check."""
    with (ROOT / "rom-images" / "roms.csv").open(encoding="utf-8") as handle:
        rows = [row for row in csv.DictReader(handle) if row["rom"] == rom]
    if len(rows) != 1:
        raise VerificationError(f"{rom}: {len(rows)} rows in rom-images/roms.csv")
    data = (ROOT / "rom-images" / rows[0]["path"]).read_bytes()
    if hashlib.sha256(data).hexdigest() != rows[0]["sha256"]:
        raise VerificationError(f"{rom}: stock image digest differs")
    return data


def _word(data, address, size=4):
    return int.from_bytes(data[address : address + size], "big")


def base_register(region, image):
    """The value that the stock MOV.L at `base_load` gives R12."""
    word = _word(image, region.base_load, 2)
    if word & 0xFF00 != 0xDC00:
        raise VerificationError(
            f"{region.key}: {region.base_load:#010x} holds {word:04x}, "
            "no MOV.L @(disp,PC),R12"
        )
    pool = (region.base_load & ~3) + 4 + (word & 0xFF) * 4
    return _word(image, pool)


def require_reconstruction(region, image, build_dir):
    """Link on the four-byte boundary at or before the first code or pool and require
    the image bytes of the region and of its pool words. A two-byte-aligned
    entry has two padding bytes before its reconstruction, outside the region.
    This preserves the alignment of PC-relative longword loads."""
    starts = [start for start, _ in region.code_spans]
    starts.extend(address for address, _ in region.pools)
    origin = min(starts) & ~3
    stem = build_dir / region.key
    base_verifier.run_command([
        base_verifier.AS, "--big", "--isa=sh2e",
        "-o", stem.with_suffix(".o"), TOOL_DIR / region.source,
    ])
    base_verifier.run_command([
        base_verifier.LD, "-EB", f"-Ttext={origin:#x}",
        f"--entry={region.start:#x}",
        "-o", stem.with_suffix(".elf"), stem.with_suffix(".o"),
    ])
    base_verifier.run_command([
        base_verifier.OBJCOPY, "-O", "binary",
        stem.with_suffix(".elf"), stem.with_suffix(".raw"),
    ])
    raw = stem.with_suffix(".raw").read_bytes()
    spans = (
        *region.code_spans,
        *((address, address + size) for address, size in region.pools),
    )
    for start, end in spans:
        actual = raw[start - origin : end - origin]
        if actual != image[start:end]:
            raise VerificationError(
                f"{region.key}: the reconstruction of {start:#010x}.."
                f"{end:#010x} differs from the {region.rom} image"
            )
    return sum((end - start) // 2 for start, end in region.code_spans)


def return_stub(region):
    """The simulator boundary, with an optional stack-held return address."""
    offset = region.return_address_offset
    if offset is None:
        return RETURN_STUB
    if type(offset) is not int or not 0 <= offset <= 60 or offset % 4:
        raise VerificationError(f"{region.key}: return address offset is a multiple of four in 0..60")
    register = region.return_register
    if type(register) is not int or not 1 <= register <= 14:
        raise VerificationError(f"{region.key}: return register is an integer in 1..14")
    # MOV.L @(offset,R15),Rn; LDS Rn,PR; RTS; NOP. R0 remains the result.
    return b''.join(word.to_bytes(2, 'big')
                    for word in (0x50F0 | (register << 8) | (offset // 4),
                                 0x402A | (register << 8), 0x000B, 0x0009))


def ram_word_aliases(region,image):
    """Checked (pool, RAM address, simulator address, byte extent) bindings."""
    rows=region.ram_word_literals
    if not isinstance(rows,tuple):
        raise VerificationError(f"{region.key}: RAM word bindings are a tuple")
    if not rows:
        return ()
    layout=kb_targets.repo.layout(kb_targets.layout_of(region.rom,root=ROOT),root=ROOT)
    ram_start,ram_end=(int(value,16) for value in kb_targets.repo.config(ROOT)['mcu'][layout.mcu]['ram'])
    checked=[]
    code=list(region.code_spans)
    if region.boundary:
        code.append((region.end,region.end+len(return_stub(region))))
    pools=[(start,start+size) for start,size in region.pools]
    overlaps=lambda start,end,spans:any(start<right and left<end for left,right in spans)
    for row in rows:
        if (not isinstance(row,tuple) or len(row)!=4
            or any(type(value) is not int for value in row)):
            raise VerificationError(f"{region.key}: a RAM word binding has four integers")
        pool,original,alias,size=row
        if pool<0 or pool%2 or pool+2>len(image) or not any(left<=pool and pool+2<=right for left,right in pools):
            raise VerificationError(f"{region.key}: RAM word {pool:#010x} leaves its declared pool")
        if overlaps(pool,pool+2,code):
            raise VerificationError(f"{region.key}: RAM word {pool:#010x} overlaps stock code or return boundary")
        value=int.from_bytes(image[pool:pool+2],'big')
        target=value|0xffff0000 if value&0x8000 else value
        if target!=original or not 0xffff8000<=original<0x100000000 or not ram_start<=original<ram_end:
            raise VerificationError(f"{region.key}: RAM word {pool:#010x} does not bind its sign-extended high-RAM address")
        if size<=0 or original+size>ram_end or alias<0 or alias+size>0x8000 or alias+size>len(image):
            raise VerificationError(f"{region.key}: RAM word alias leaves the positive signed-word window")
        if overlaps(alias,alias+size,code+pools):
            raise VerificationError(f"{region.key}: RAM word alias overlaps stock code, pool or return boundary")
        if any(pool<other_pool+2 and other_pool<pool+2
               for other_pool,other_original,other_alias,other_size in checked):
            raise VerificationError(f"{region.key}: RAM word pool bindings overlap or repeat")
        if any((alias<other_alias+other_size and other_alias<alias+size
                or original<other_original+other_size and other_original<original+size)
               and (original,alias,size)!=(other_original,other_alias,other_size)
               for other_pool,other_original,other_alias,other_size in checked):
            raise VerificationError(f"{region.key}: RAM word windows overlap or conflict")
        if any(pool<address+4 and address<pool+2
               or _word(image,address)==original for address in region.ram_literals):
            raise VerificationError(f"{region.key}: RAM word binding conflicts with a long RAM literal")
        checked.append(row)
    return tuple(checked)


def register_word_aliases(region, image):
    """Checked pool bindings to declared 16-bit I/O register storage."""
    rows = region.register_word_literals
    if not isinstance(rows, tuple):
        raise VerificationError(f"{region.key}: register word bindings are a tuple")
    if not rows:
        return ()
    layout_id = kb_targets.layout_of(region.rom, root=ROOT)
    layout = kb_targets.repo.layout(layout_id, root=ROOT)
    io_start, io_end = (int(value, 16) for value in
                        kb_targets.repo.config(ROOT)['mcu'][layout.mcu]['io'])
    code = list(region.code_spans)
    if region.boundary:
        code.append((region.end, region.end + len(return_stub(region))))
    pools = [(start, start + size) for start, size in region.pools]
    overlaps = lambda start, end, spans: any(start < right and left < end for left, right in spans)
    ram_words = ram_word_aliases(region, image)
    checked = []
    for row in rows:
        if (not isinstance(row, tuple) or len(row) != 4
                or any(type(value) is not int for value in row)):
            raise VerificationError(f"{region.key}: a register word binding has four integers")
        pool, original, alias, size = row
        if (pool < 0 or pool % 2 or pool + 2 > len(image)
                or not any(left <= pool and pool + 2 <= right for left, right in pools)):
            raise VerificationError(f"{region.key}: register word leaves its declared pool")
        if overlaps(pool, pool + 2, code):
            raise VerificationError(f"{region.key}: register word overlaps stock code or return boundary")
        value = int.from_bytes(image[pool:pool + 2], 'big')
        target = value | 0xffff0000 if value & 0x8000 else value
        if (target != original or not 0xffff8000 <= original < 0x100000000
                or not io_start <= original < io_end or original % 2):
            raise VerificationError(f"{region.key}: register word does not bind its sign-extended I/O address")
        if (size <= 0 or size % 2 or original + size > io_end or alias < 0 or alias % 2
                or alias + size > 0x8000 or alias + size > len(image)):
            raise VerificationError(f"{region.key}: register word alias leaves its aligned positive window")
        if overlaps(alias, alias + size, code + pools):
            raise VerificationError(f"{region.key}: register word alias overlaps stock code, pool or return boundary")
        members = []
        for _, ref in region.symbols:
            if not ref.endswith('/reg'):
                continue
            try:
                symbol = kb_targets.symbol(ref, layout_id, root=ROOT)
                address = int(symbol['address'], 16)
                if not original <= address < original + size:
                    continue
                name, _, kind = ref.rpartition('/')
                document = kb_targets._document(kind, name, ROOT, None)
                width = symbol.get('width', document.get('width'))
            except (kb_targets.repo.KbError, KeyError, TypeError, ValueError) as error:
                raise VerificationError(f"{region.key}: register word has no valid declared owner") from error
            if type(width) is not int or width != 16 or address % 2 or address + 2 > original + size:
                raise VerificationError(f"{region.key}: register window requires aligned 16-bit owners")
            members.append(address)
        if (not members or original not in members or len(set(members)) != len(members)
                or max(members) + 2 != original + size):
            raise VerificationError(f"{region.key}: register window lacks distinct endpoint owners")
        for other_pool, other_original, other_alias, other_size in checked:
            if pool < other_pool + 2 and other_pool < pool + 2:
                raise VerificationError(f"{region.key}: register word pools overlap or repeat")
            coherent = (original, alias, size) == (other_original, other_alias, other_size)
            if not coherent and (alias < other_alias + other_size and other_alias < alias + size
                                 or original < other_original + other_size and other_original < original + size):
                raise VerificationError(f"{region.key}: register word windows conflict")
        if any(pool < other_pool + 2 and other_pool < pool + 2
               or alias < other_alias + other_size and other_alias < alias + size
               for other_pool, _, other_alias, other_size in ram_words):
            raise VerificationError(f"{region.key}: register word conflicts with a RAM word binding")
        if any(pool < address + 4 and address < pool + 2
               or original <= _word(image, address) < original + size
               for address in region.ram_literals):
            raise VerificationError(f"{region.key}: register word conflicts with a long RAM literal")
        checked.append(row)
    return tuple(checked)


def build_fixture(region, image):
    """The simulator-only fixture of a region; the region bytes stay stock."""
    fixture = bytearray(image)
    for address in region.ram_literals:
        if not any(start <= address <= start + size - 4
                   for start, size in region.pools):
            raise VerificationError(
                f"{region.key}: {address:#010x} lies outside the pools"
            )
        value = _word(fixture, address)
        fixture[address : address + 4] = base_verifier.alias_high_ram(
            value
        ).to_bytes(4, "big")
    for address,original,alias,size in ram_word_aliases(region,image):
        fixture[address:address+2] = alias.to_bytes(2,"big")
    for address, original, alias, size in register_word_aliases(region, image):
        fixture[address:address + 2] = alias.to_bytes(2, "big")
    if region.boundary:
        boundary = return_stub(region)
        end = region.end + len(boundary)
        if end > len(fixture) or any(region.end < address + size and address < end
                                     for address, size in region.pools):
            raise VerificationError(f"{region.key}: return boundary overlaps a pool or leaves the image")
        fixture[region.end : end] = boundary
    elif region.return_address_offset is not None:
        raise VerificationError(f"{region.key}: a natural stock return takes no boundary return address")
    for start, end in region.code_spans:
        if fixture[start:end] != image[start:end]:
            raise VerificationError(f"{region.key}: the fixture alters the region")
    return bytes(fixture)


def harness_defines(region, image):
    """The entry of a region, the symbols and named bits of the entity files
    on its layout, its constants, and the stock base register value, as
    harness definitions."""
    layout = kb_targets.layout_of(region.rom, root=ROOT)
    defines = {"REGION_ENTRY": region.start}
    defines.update(
        (name, kb_targets.address(ref, layout, root=ROOT))
        for name, ref in region.symbols
    )
    defines.update(
        (name, 1 << kb_targets.bit(ref, layout, bit, root=ROOT))
        for name, ref, bit in region.bits
    )
    defines.update(region.constants)
    if region.base_load is not None:
        defines["REGION_R12"] = base_register(region, image)
    return defines


REGION_OBSERVERS = {'jk08a-full-programmer': 'stock_injection_scheduler_invoke.s', 'jk08a-oneshot': 'stock_oneshot_invoke.s', 'jk08a-rpm-phase-word': 'stock_oneshot_invoke.s', 'jk08a-rpm-phase-byte': 'stock_oneshot_invoke.s', 'jk08a-rpm-phase-copy': 'stock_oneshot_invoke.s', 'jk08a-event-isr': 'stock_injector_event_invoke.s', 'jk08a-end-angle': 'stock_oneshot_invoke.s', 'jk08a-full-dispatch': 'stock_oneshot_invoke.s', 'jk08a-base-accumulator': 'stock_oneshot_invoke.s', 'jk08a-transient-coefficient': 'stock_oneshot_invoke.s', 'jk08a-transient-additive': 'stock_oneshot_invoke.s', 'jk08a-coolant-conditional': 'stock_oneshot_invoke.s', 'jk08a-transient-pair-1': 'stock_oneshot_invoke.s', 'jk08a-transient-pair-2': 'stock_oneshot_invoke.s', 'jk08a-fuel-multiplier': 'stock_oneshot_invoke.s', 'jk08a-pulse-precursor': 'stock_oneshot_invoke.s', 'jk08a-common-gain': 'stock_oneshot_invoke.s', 'jk08a-enrichment-prefix': 'stock_enrichment_prefix_invoke.s', 'jk08a-enrichment-terminal': 'stock_enrichment_terminal_invoke.s'}


REGION_OBSERVERS.update({
    'jk08a-knock-metric': 'invoke-knock-metric.s',
    'jk08a-knock-normalization': 'invoke-knock-normalization.s',
    'jk08a-stft-publication': 'invoke-stft-publication.s',
    'jk08a-grid-selection': 'invoke-grid-selection.s',
    'jk08a-grid-learning': 'invoke-grid-learning.s',
})


def run_region(region, invoke, build_dir):
    observer = REGION_OBSERVERS.get(region.key)
    if observer is not None:
        invoke = build_dir / f"{region.key}-invoke.o"
        base_verifier.run_command([
            base_verifier.AS, "--big", "--isa=sh2e", "-I", TOOL_DIR,
            "-o", invoke, TOOL_DIR / observer,
        ])
    image = stock_image(region.rom)
    instructions = require_reconstruction(region, image, build_dir)
    fixture = build_fixture(region, image)
    fixture_path = build_dir / f"{region.key}.sim-fixture"
    rom_object = build_dir / f"{region.key}-rom.o"
    fixture_path.write_bytes(fixture)
    base_verifier.run_command([
        base_verifier.OBJCOPY, "-I", "binary", "-O", "elf32-sh", "-B", "sh",
        "--rename-section", ".data=.rom,alloc,load,code,data,contents",
        fixture_path, rom_object,
    ])
    output = build_dir / f"{region.key}-harness.elf"
    text_base = max(base_verifier.DRIVER_TEXT_BASE, len(fixture) + 0x10000)
    defines = harness_defines(region, image)
    base_verifier.run_command(
        [
            base_verifier.GCC, "-m2e", "-mb", "-std=c11", "-O2",
            "-Wall", "-Wextra", "-Werror",
            f'-DREGION_KEY="{region.key}"',
            *(f"-D{name}={value:#x}U" for name, value in defines.items()),
            f"-Wl,-Ttext-segment={text_base:#x}",
            "-Wl,--section-start=.rom=0",
            "-o", output,
            TOOL_DIR / region.harness, invoke, rom_object,
        ],
        timeout=120,
    )
    try:
        require_separate_storage(output, ((base_verifier.TEST_RAM_BASE, 65536),))
    except (ELFStorageError, OSError) as error:
        raise VerificationError(f"{region.key}: ELF storage separation: {error}") from error
    result = base_verifier.run_command(
        [
            base_verifier.RUN,
            f"--memory-region={base_verifier.TEST_RAM_BASE:#x},64k",
            output,
        ],
        timeout=120,
    )
    marker = (
        f"VQ_SH_ELF_STOCK_CODE status=PASS region={region.key} "
        f"cases={region.cases}"
    )
    if marker not in result.stdout.splitlines():
        raise VerificationError(
            f"{region.key}: zero exit without the exact PASS marker"
            + (f"\n{result.stdout.rstrip()}" if result.stdout else "")
        )
    return instructions


def verify(verbose=False):
    with tempfile.TemporaryDirectory(prefix="vq-sh-elf-stock-") as directory:
        build_dir = Path(directory)
        invoke = build_dir / "stock-invoke.o"
        base_verifier.run_command([
            base_verifier.AS, "--big", "--isa=sh2e", "-I", TOOL_DIR,
            "-o", invoke, TOOL_DIR / "stock_invoke.s",
        ])
        instructions = 0
        for region in REGIONS:
            count = run_region(region, invoke, build_dir)
            instructions += count
            if verbose:
                print(
                    f"STOCK_CODE region={region.key} rom={region.rom} "
                    f"start={region.start:#010x} instructions={count} "
                    f"cases={region.cases}"
                )
    result = {
        "regions": len(REGIONS),
        "instructions": instructions,
        "dynamic_cases": sum(region.cases for region in REGIONS),
    }
    print(
        f"VQ_SH_ELF_STOCK_CODE status=PASS regions={result['regions']} "
        f"instructions={instructions} cases={result['dynamic_cases']}"
    )
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)
    try:
        verify(verbose=args.verbose)
    except (OSError, ValueError, VerificationError,
            base_verifier.VerificationError) as error:
        print(f"VQ_SH_ELF_STOCK_CODE status=FAIL error={error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
