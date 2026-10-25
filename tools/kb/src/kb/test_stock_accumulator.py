"""Independent state equations for selected actual base-accumulator entries.

These equations consume GNU raw observations, not the C matrix's expected
columns. Complete stock execution, source/fixture reconstruction, exact native
claim scope and the original pytest cohort remain separate admission duties.
"""

from pathlib import Path

from kb import test_cases, test_contract, test_execution, test_registry, test_stock_abi, test_stock_capture
from kb.model import SymbolKey

REGION = 'jk08a-base-accumulator'
ENTRY = 0x554ae
INVOCATIONS = 132684
MASK = 0xffffffff
INPUTS = (
    (0x00000000, 0, 0), (0x0000bffe, 0, 0), (0x0000bfff, 0, 0),
    (0x0000c000, 0, 0), (0x7fffbfff, 0, 0), (0x7fffc000, 0, 0),
    (0xffffbfff, 0, 0), (0xffffc000, 0, 0), (0xffffffff, 65535, 65535),
    (0x7fffbffe, 1, 0), (0x7fffbffe, 2, 0), (0x80000000, 65535, 65535),
)
ABI = (0x18283848, 0x19293949, 0x1a2a3a4a, 0x1b2b3b4b,
       0x1c2c3c4c, 0x1d2d3d4d, 0x1e2e3e4e, 0x12344321, 0x10203040, 0x50607080)
FACT = 'base-accumulator-bounded-entries'
FUNCTION = 'fuel_base_accumulator/fn'
MEMBERS = {
    0xffff15f8: ('adept-bumblebee/ram', 'reader', 32),
    0xffff230c: ('beneficial-ringtail/ram', 'reader', 16),
    0xffff15da: ('competent-pillbug/ram', 'reader', 16),
    0xffff231a: ('happy-curassow/ram', 'writer', 16),
}
ADAPTER = 'independent-base-accumulator'
TEST_PATH = 'tools/kb/tests/test_fuel_upstream_chain.py'
TEST_SELECTORS = ('test_fuel_upstream_owner_contract', 'test_fuel_upstream_stock_regions_contract')


def profile(model, origins):
    """Curated physical members select contexts; a test name supplies no fact."""
    allowed = {SymbolKey('7mfk', 'ram', address).key: owner
               for address, (owner, mode, width) in MEMBERS.items()}
    allowed[SymbolKey('7mfk', 'fn', ENTRY).key] = FUNCTION
    by_owner = {owner: key for key, owner in allowed.items()}
    bindings = []
    for origin in origins.values():
        if origin.path != TEST_PATH or origin.selector not in TEST_SELECTORS:
            continue
        if origin.kind == 'symbol' and origin.owner in allowed:
            symbol_key = origin.owner
            subjects = (symbol_key, allowed[symbol_key])
        elif origin.kind == 'link' and origin.owner in by_owner:
            locator = origin.packet()['locator']
            identity = locator[1]
            if identity['to'] != FUNCTION:
                continue
            symbol_key = by_owner[origin.owner]
            subjects = (symbol_key,)
        else:
            continue
        if origin.explicit_support not in (None, 'identity'):
            continue
        cases = tuple(case.nodeid for case in test_cases.cases(origin.path + '::' + origin.selector))
        for subject in subjects:
            bindings.append(test_registry.Binding(origin.key, origin.context_digest,
                origin.path, origin.selector, symbol_key,
                test_registry.Claim(subject, 'identity'), 'identity', FACT, cases, origin.locator_text))
    if not bindings:
        raise ValueError('the accumulator semantic profile has no exact native TEST contexts')
    contract = test_cases.contract('base-accumulator',
        tuple(TEST_PATH + '::' + selector for selector in TEST_SELECTORS))
    return test_registry.Profile('base-accumulator', contract, tuple(bindings), ADAPTER, (FACT,), (REGION,))


def adapter(root):
    root = Path(root).resolve()
    paths = ('tools/kb/src/kb/test_stock_accumulator.py',
             'tools/kb/src/kb/test_stock_abi.py', 'tools/kb/src/kb/test_stock_capture.py',
             'tools/sh-elf-run/native_test_capture.py', 'tools/sh-elf-run/native_test_capture.c',
             'tools/sh-elf-run/native-test-capture.h', 'tools/sh-elf-run/verify_stock_code.py',
             'tools/sh-elf-run/verify_map_switching.py', 'tools/sh-elf-run/elf_storage_layout.py',
             'tools/sh-elf-run/stock_oneshot_invoke.s',
             'tools/sh-elf-run/stock_jk08a_base_accumulator.s',
             'tools/sh-elf-run/harness-stock-jk08a-base-accumulator.c',
             'tools/sh-elf-run/base-accumulator-cases.h',
             'tools/sh-elf-run/fuel-upstream-contracts.json',
             TEST_PATH, 'rom-images/roms.csv', 'rom-images/homology.toml')
    return test_execution.Adapter(ADAPTER, tuple(sorted(paths)), evaluate)


def capture_spec():
    return test_stock_abi.oneshot(REGION, INVOCATIONS,
        tuple((index, ENTRY) for index in range(len(INPUTS))),
        (('ram', 0xffff0000, 0x01000000, 65536),))


def signed(value):
    return value if value < 0x80000000 else value - 0x100000000


def check_observations(capture):
    """Check full GPR/SR/frame/ABI/RAM observations for the declared entries."""
    observations = test_stock_abi.oneshot_observation(capture, capture_spec())
    cases = []
    outcomes = set()
    for observed, wanted in zip(observations, INPUTS):
        index = observed['index']
        context = observed['context']
        before, after = observed['memory_before'][0], observed['memory_after'][0]
        term = int.from_bytes(before[0x15f8:0x15fc], 'big')
        conditional = int.from_bytes(before[0x230c:0x230e], 'big')
        coolant = int.from_bytes(before[0x15da:0x15dc], 'big')
        if (term, conditional, coolant) != wanted:
            raise ValueError('the accumulator raw input differs from its declared physical case')
        variant = index & 1
        incoming = tuple(((0x1728394a + register * 0x110203) if variant == 0
                          else (0x81234567 + register * 0x1020305)) & MASK
                         for register in range(15))
        entry_sr = (index & 1) | (((index >> 1) & 15) << 4) | ((index & 3) << 8)
        special = ((0x01004567, 0xf1e2d3c4, 0x9274b6d8) if variant
                   else (0x01003579, 0x13579bdf, 0x2468ace0))
        if context != (*incoming, *special, entry_sr):
            raise ValueError('the accumulator raw entry registers or controlled flags changed')
        first = (term + 0x4000) & MASK
        total = (first + conditional + coolant) & MASK
        upper = signed(total) > 65535
        selected = 65535 if upper else total
        negative = signed(selected) < 0
        output = 0 if negative else selected
        expected = list(incoming)
        for register, value in ((0, output), (1, 0x0100128c), (2, output),
                                (4, conditional), (5, first if upper else total),
                                (6, 65535), (7, coolant)):
            expected[register] = value
        actual = tuple(observed['exit'][19 - register] for register in range(15))
        if actual != tuple(expected):
            raise ValueError('the accumulator actual complete GPR result disagrees with its independent equation')
        sr = observed['sr_before']
        if (sr & 0x3f1 != entry_sr
                or observed['exit'][0] != (sr & ~1) | int(not negative)
                or observed['exit'][2:5] != (context[17], context[16], context[15])):
            raise ValueError('the accumulator actual full SR, MACH, MACL or GBR changed')
        if (observed['abi_before'] != observed['abi_after']
                or observed['abi_before'][:10] != ABI
                or observed['sp'] != (observed['abi_before'][10] - 164) & MASK
                or observed['exit'][1] != observed['continuation']):
            raise ValueError('the accumulator actual natural continuation or caller ABI changed')
        frame = bytearray(observed['frame_before'])
        frame[156:160] = context[15].to_bytes(4, 'big')
        if observed['frame_after'] != bytes(frame):
            raise ValueError('the accumulator actual frame changes outside the stock GBR save')
        memory = bytearray(before)
        memory[0x231a:0x231c] = output.to_bytes(2, 'big')
        if after != bytes(memory):
            raise ValueError('the accumulator actual full RAM differs from its independent bounded write')
        outcomes.add((upper, negative))
        cases.append(dict(index=index, entry=ENTRY, term=term, conditional=conditional,
            coolant=coolant, sum_low32=total, upper_clamp=upper,
            lower_clamp=negative, output=output, physical_write=[0xffff231a, 16]))
    if outcomes != {(False, False), (True, False), (False, True)}:
        raise ValueError('the accumulator observations omit a declared signed clamp branch outcome')
    return dict(scope='selected-bounded-native-entries', cases=cases,
                scheduler_reachability=False, hardware_qualification=False)


def evaluate(model, profile, contexts, primary):
    """Support only exact identity contexts of the four physical fields or entry."""
    if (profile.facts != (FACT,) or profile.gnu_regions != (REGION,)
            or primary is None or len(contexts) != len(profile.bindings)):
        raise ValueError('the accumulator adapter supports another fact or execution region')
    function = model.symbols.get(SymbolKey('7mfk', 'fn', ENTRY))
    if (function is None or function.meaning is None or function.meaning.key != FUNCTION
            or ENTRY not in model.functions.get('7mfk', ())):
        raise ValueError('the accumulator entry has another native function owner')
    supported = []
    for binding, request in zip(profile.bindings, contexts):
        if (binding.support != 'identity' or binding.claim.name != 'identity'
                or binding.fact != FACT or not test_contract.exact(request['binding'], binding.packet())):
            raise ValueError('the accumulator identity observation cannot supply scale, contract or another fact')
        origin = request['origin']
        if binding.symbol == function.key.key:
            symbol, owner, mode, width = function, FUNCTION, 'entry', None
            if origin['kind'] != 'symbol' or origin['owner'] != function.key.key:
                raise ValueError('the accumulator entry requires its direct owning TEST attachment')
        else:
            found = [(address, values) for address, values in MEMBERS.items()
                     if binding.symbol == SymbolKey('7mfk', 'ram', address).key]
            if len(found) != 1:
                raise ValueError('the accumulator observation supplies another physical symbol')
            address, (owner, mode, width) = found[0]
            symbol = model.symbols.get(SymbolKey('7mfk', 'ram', address))
            if symbol is None or symbol.meaning is None or symbol.meaning.key != owner:
                raise ValueError('the accumulator field has another native semantic owner')
            if origin['kind'] == 'symbol':
                if origin['owner'] != symbol.key.key:
                    raise ValueError('the accumulator field requires its exact owning symbol attachment')
            elif origin['kind'] == 'link':
                identity = dict(owner=owner, type=mode, to=FUNCTION, slot=None, offset=None)
                if not test_contract.exact(origin['locator'][:3], ['link', identity, 'evidence']):
                    raise ValueError('the accumulator observation supplies another relation, direction or offset')
            else:
                raise ValueError('the accumulator observation supplies no nested or unrelated semantic property')
        if binding.claim.subject not in (symbol.key.key, owner):
            raise ValueError('the accumulator observation supports another claimed subject')
        supported.append(dict(origin=binding.origin_key, symbol=symbol.key.key,
            claim=binding.claim.packet(), fact=FACT, mode=mode, physical_width_bits=width,
            declared_width=symbol.value('width'), declared_signed=symbol.value('signed')))
    physical = test_stock_capture.require(model, primary, REGION, capture_spec())
    equations = check_observations(primary.raw_regions()[REGION]['capture'])
    return {FACT: dict(physical=physical, equations=equations, supported=supported,
                       support='identity', physical_units=False, declared_width_inference=False)}
