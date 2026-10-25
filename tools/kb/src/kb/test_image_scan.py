"""Independent reconstruction of the exact registered 1ME3B scan scope.

The scan covers aligned occupied-image pointers into the region and direct
PC-relative branches to its entry. Interior control flow, computed entries,
private literal consumers and hardware reachability require separate proof.
"""

import hashlib
from pathlib import Path

from kb import repo, test_contract, test_evidence, test_execution, test_origins, test_registry
from kb.model import SymbolKey

ADAPTER = 'independent-1me3b-image-scan'
FACT = '1me3b-image-scan'


def profile(model, origins):
    symbol = model.symbols.get(SymbolKey(*test_evidence.SYMBOL))
    test_evidence.public_packet(model, symbol, test_evidence.item())
    matches = [origin for origin in origins.values()
               if origin.kind == 'symbol' and origin.owner == symbol.key.key
               and origin.path == test_evidence.PATH and origin.selector == test_evidence.KEY]
    if len(matches) != 1:
        raise ValueError('the image scan requires its unique direct native TEST attachment')
    origin = test_origins.rebind(model, matches[0])
    bindings = tuple(test_registry.Binding(origin.key, origin.context_digest,
        origin.path, origin.selector, symbol.key.key,
        test_registry.Claim(subject, 'identity'), 'identity', FACT,
        (test_evidence.NODEID,), origin.locator_text)
        for subject in (symbol.key.key, symbol.meaning.key))
    return test_registry.Profile('1me3b-image-scan', test_evidence.CONTRACT,
                                 bindings, ADAPTER, (FACT,))


def adapter(root):
    root = Path(root).resolve()
    paths = set(test_evidence.EXECUTION_INPUTS)
    paths.add('tools/kb/src/kb/test_image_scan.py')
    paths.update(image.path.relative_to(root).as_posix() for image in repo.images(root).values())
    return test_execution.Adapter(ADAPTER, tuple(sorted(paths)), evaluate)


def evaluate(model, registered, contexts, primary):
    if (registered.adapter != ADAPTER or registered.facts != (FACT,) or registered.gnu_regions
            or not test_contract.exact(registered.contract.packet(), test_evidence.CONTRACT.packet())
            or len(contexts) != len(registered.bindings)):
        raise ValueError('the image-scan adapter supports another fact or execution scope')
    symbol = model.symbols.get(SymbolKey(*test_evidence.SYMBOL))
    public = test_evidence.public_packet(model, symbol, test_evidence.item())
    for binding, request in zip(registered.bindings, contexts):
        origin = request['origin']
        if (binding.fact != FACT or binding.support != 'identity'
                or binding.symbol != symbol.key.key or binding.claim.name != 'identity'
                or binding.claim.subject not in (symbol.key.key, symbol.meaning.key)
                or not test_contract.exact(binding.packet(), request['binding'])
                or origin['kind'] != 'symbol' or origin['owner'] != symbol.key.key
                or origin['path'] != test_evidence.PATH or origin['selector'] != test_evidence.KEY):
            raise ValueError('the image scan cannot supply another owner, scale or claim')
    from patches import rom_address_profiles
    profiles = rom_address_profiles.load_registry()
    selected = profiles['1ME3B']
    routine = selected.ignition_unreferenced_routine
    if ((routine.start, routine.end) != (0x791a4, 0x797cc)
            or profiles['1ND0A'].ignition_unreferenced_routine is not None):
        raise ValueError('the image scan has another region or layout comparison')
    root = Path(model.root).resolve()
    image = repo.images(root)['1ME3B']
    data = image.path.read_bytes()
    if hashlib.sha256(data).hexdigest() != image.sha256:
        raise ValueError('the image scan stock bytes differ from their catalog identity')
    limit = selected.free_rom.start
    if not 0 <= routine.start < routine.end <= limit <= len(data):
        raise ValueError('the image scan has incomplete occupied stock-image bounds')
    pointers = []
    for site in range(0, limit - 3, 2):
        target = int.from_bytes(data[site:site + 4], 'big')
        if routine.start <= target < routine.end:
            pointers.append((site, target))
    if pointers:
        raise ValueError('the occupied stock image has an aligned pointer into the registered region')
    branches = []
    for site in range(0, limit - 1, 2):
        if routine.start <= site < routine.end:
            continue
        word = int.from_bytes(data[site:site + 2], 'big')
        if word >> 12 in (0xa, 0xb):
            displacement = word & 0xfff
            displacement -= 0x1000 if displacement & 0x800 else 0
        elif word >> 8 in (0x89, 0x8b, 0x8d, 0x8f):
            displacement = word & 0xff
            displacement -= 0x100 if displacement & 0x80 else 0
        else:
            continue
        if site + 4 + 2 * displacement == routine.start:
            branches.append((site, word))
    if branches:
        raise ValueError('a direct stock branch enters the registered region entry')
    return {FACT: dict(public=public, facts=test_evidence.facts(),
        image=dict(path=image.path.relative_to(root).as_posix(), sha256=hashlib.sha256(data).hexdigest()),
        occupied_end_exclusive=limit, pointer_stride_bytes=2,
        region_bytes=data[routine.start:routine.end].hex(),
        inbound_aligned_pointers=pointers, inbound_direct_entry_branches=branches,
        interior_control_flow=False, computed_entries=False,
        private_literal_consumers=False, hardware_qualification=False)}
