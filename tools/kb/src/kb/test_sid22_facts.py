"""Exact reader TEST relations jointly bound to the complete SID22 execution.

Pointer-slot observations establish bounded byte reads of the retained native
members. Direct symbol identity, physical scale, scheduling and hardware
behavior require their separate semantic evidence.
"""

from dataclasses import asdict

from kb import sid22_evidence as proof
from kb import test_cases, test_contract, test_execution, test_registry
from kb.model import SymbolKey

ADAPTER = 'independent-sid22-pointer-reads'
FACT = 'sid22-bounded-pointer-read'


def profile(model, origins):
    contract = proof.descriptor(model.root)
    members = {member.meaning: member for member in contract.members}
    bindings, selectors = [], set()
    for origin in origins.values():
        if (origin.kind != 'link' or origin.owner not in members
                or origin.explicit_support not in (None, 'identity')):
            continue
        identity = origin.packet()['locator'][1]
        if identity['type'] != 'reader' or identity['to'] != proof.FUNCTION_MEANING:
            continue
        member = members[origin.owner]
        key = SymbolKey('7mfk', 'ram', member.address).key
        selector = origin.path + '::' + origin.selector
        cases = tuple(case.nodeid for case in test_cases.cases(selector))
        selectors.add(selector)
        bindings.append(test_registry.Binding(origin.key, origin.context_digest,
            origin.path, origin.selector, key, test_registry.Claim(key, 'identity'),
            'identity', FACT, cases, origin.locator_text))
    if not bindings:
        raise ValueError('the SID22 TEST profile has no exact retained native reader contexts')
    return test_registry.Profile('sid22-pointer-reads',
        test_cases.contract('sid22-pointer-reads', tuple(sorted(selectors))),
        tuple(bindings), ADAPTER, (FACT,), (proof.REGION,))


def adapter(root):
    paths = set(proof.EXECUTION_FILES)
    paths.update(('tools/kb/src/kb/test_sid22_facts.py', 'tools/kb/src/kb/sid22_evidence.py',
                  'tools/kb/src/kb/sid22_matrix.py', 'tools/kb/src/kb/sid22_witness.py'))
    return test_execution.Adapter(ADAPTER, tuple(sorted(paths)), evaluate)


def evaluate(model, registered, contexts, primary):
    if (registered.adapter != ADAPTER or registered.facts != (FACT,)
            or registered.gnu_regions != (proof.REGION,) or primary is None
            or len(contexts) != len(registered.bindings)):
        raise ValueError('the SID22 TEST adapter supports another execution or fact scope')
    contract = proof.descriptor(model.root)
    members = {SymbolKey('7mfk', 'ram', member.address).key: member
               for member in contract.members}
    symbols = {symbol.key.key: symbol for symbol in model.symbols.values()}
    supported = []
    for binding, request in zip(registered.bindings, contexts):
        if (binding.symbol not in members or binding.fact != FACT or binding.support != 'identity'
                or binding.claim.name != 'identity' or binding.claim.subject != binding.symbol
                or not test_contract.exact(binding.packet(), request['binding'])):
            raise ValueError('the SID22 TEST observation supplies another storage member or property')
        member = members[binding.symbol]
        symbol = symbols.get(binding.symbol)
        if proof._member(model, symbol, contract) != member:
            raise ValueError('the SID22 TEST observation changes its exact native member')
        relation = proof._link(model, symbol, member, contract)
        origin = request['origin']
        identity = dict(owner=relation.owner.key, type='reader', to=relation.to.key,
                        slot=relation.slot, offset=relation.offset)
        if (origin['kind'] != 'link'
                or not test_contract.exact(origin['locator'][:3], ['link', identity, 'evidence'])):
            raise ValueError('the SID22 TEST observation changes its exact reader or pointer-slot context')
        selected = [asdict(row) for row in contract.bindings if row.member == member.meaning]
        if not selected:
            raise ValueError('the SID22 TEST observation has no actual executed source binding')
        supported.append(dict(origin=binding.origin_key, symbol=binding.symbol,
            claim=binding.claim.packet(), member=asdict(member), source_bindings=selected,
            declared_width=symbol.value('width'), declared_signed=symbol.value('signed')))
    original = primary.sid22_packet()['candidate']
    scope = proof.scope_digest(model)
    if scope != original['scope']:
        raise ValueError('the SID22 TEST facts differ from their independently qualified native scope')
    return {FACT: dict(scope=scope, supported=supported,
                       scope_kind='bounded-diagnostic-pointer-byte-read',
                       scale=False, producer_semantics=False, scheduling=False,
                       declared_width_inference=False, hardware_qualification=False)}
