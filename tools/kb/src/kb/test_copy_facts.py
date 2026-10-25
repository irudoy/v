"""Exact TEST identity contexts backed by the existing complete COPY matrices.

Successful pytest phases and the full independently validated COPY original
are joint requirements for exact reader/writer relation attachments. Direct
symbol TEST attachments need their own semantic adapter. Copy observations
infer neither declared field width nor scale, cadence or producer values.
"""

from kb import coherent_copy_evidence as coherent
from kb import copy_evidence as common, injection_copy_evidence as injection
from kb import test_cases, test_contract, test_execution, test_registry
from kb.model import SymbolKey

ADAPTER = 'independent-copy-placements'
FACTS = ('can-copy-byte-placement', 'injection-copy-byte-placement', 'coherent-copy-byte-placement')


def domains():
    members = {}
    for direction, (meaning, address) in common.MEMBERS.items():
        key=(SymbolKey('7mfk', 'ram', address).key, 'coherent_snapshot/fn', direction)
        members[key] = (FACTS[0], direction, meaning, None)
    for fact, rows in ((FACTS[1], injection.MEMBERS), (FACTS[2], coherent.MEMBERS)):
        for row in rows:
            address, direction, meaning = row[:3]
            parent=coherent.parent(row)[1] if fact==FACTS[2] else 'coherent_snapshot/fn'
            key = (SymbolKey('7mfk', 'ram', address).key, parent, direction)
            if key in members:
                raise ValueError('the TEST copy domains have an ambiguous physical member')
            members[key] = (fact, direction, meaning, row)
    return members


def regions():
    return (common.REGION, injection.REGION,
            *(f'jk08a-coherent-{window.call:08x}' for window in coherent.matrix.WINDOWS))


def profile(model, origins):
    members = domains()
    bindings, selectors = [], set()
    for origin in origins.values():
        if origin.explicit_support not in (None, 'identity'):
            continue
        if origin.kind == 'link':
            identity = origin.packet()['locator'][1]
            selected=[(key,value) for key,value in members.items() if value[2]==origin.owner
                      and key[1:]==(identity['to'],identity['type'])]
            if not selected:
                continue
            if len(selected)!=1:
                raise ValueError('the TEST copy context has more than one exact owning caller domain')
            domain,value=selected[0]
            key=domain[0]
            subjects = (key,)
        else:
            continue
        selector = origin.path + '::' + origin.selector
        cases = tuple(case.nodeid for case in test_cases.cases(selector))
        selectors.add(selector)
        for subject in subjects:
            bindings.append(test_registry.Binding(origin.key, origin.context_digest,
                origin.path, origin.selector, key, test_registry.Claim(subject, 'identity'),
                'identity', value[0], cases, origin.locator_text))
    if not bindings:
        raise ValueError('the TEST copy profile has no exact native identity contexts')
    return test_registry.Profile('copy-placements',
        test_cases.contract('copy-placements', tuple(sorted(selectors))),
        tuple(bindings), ADAPTER, FACTS, regions())


def adapter(root):
    paths = set(common.EXECUTION_FILES)
    paths.update(('tools/kb/src/kb/test_copy_facts.py',
                  'tools/kb/src/kb/coherent_copy_evidence.py',
                  'tools/kb/src/kb/coherent_copy_matrix.py',
                  'tools/kb/src/kb/coherent_copy_members.py',
                  'tools/kb/src/kb/injection_copy_evidence.py',
                  'tools/kb/src/kb/injection_copy_matrix.py'))
    return test_execution.Adapter(ADAPTER, tuple(sorted(paths)), evaluate)


def evaluate(model, registered, contexts, primary):
    if (registered.adapter != ADAPTER or registered.facts != FACTS
            or registered.gnu_regions != regions() or primary is None
            or len(contexts) != len(registered.bindings)):
        raise ValueError('the TEST copy adapter supports another execution or fact set')
    members = domains()
    symbols = {symbol.key.key: symbol for symbol in model.symbols.values()}
    supported = {fact: [] for fact in FACTS}
    for binding, request in zip(registered.bindings, contexts):
        origin=request['origin']
        if origin['kind']!='link':
            raise ValueError('the TEST copy supports only its exact reader/writer relation attachment')
        identity=origin['locator'][1]
        domain=(binding.symbol,identity['to'],identity['type'])
        if (domain not in members or binding.support != 'identity'
                or binding.claim.name != 'identity'
                or not test_contract.exact(binding.packet(), request['binding'])):
            raise ValueError('the TEST copy observation supplies another symbol or claimed property')
        fact, direction, meaning, selected_row = members[domain]
        if binding.fact != fact or binding.claim.subject not in (binding.symbol, meaning):
            raise ValueError('the TEST copy observation supplies another physical fact or claimant')
        symbol = symbols.get(binding.symbol)
        if symbol is None or symbol.meaning is None or symbol.meaning.key != meaning:
            raise ValueError('the TEST copy observation has another native semantic owner')
        if fact == FACTS[0]:
            if common._member(model, symbol) != direction:
                raise ValueError('the TEST CAN copy context has another physical direction')
            relation = common._link(model, symbol, direction)
            physical = common.item(direction)['value']
        elif fact == FACTS[1]:
            row = injection.member(model, symbol)
            relation = injection.link(model, symbol, row)
            physical = injection.member_item(row)['value']
        else:
            row = coherent.member(model, symbol, row=selected_row)
            relation = coherent.link(model, symbol, row)
            physical = coherent.member_item(row)['value']
        if origin['kind'] == 'link':
            identity = dict(owner=relation.owner.key, type=relation.type, to=relation.to.key,
                            slot=relation.slot, offset=relation.offset)
            if not test_contract.exact(origin['locator'][:3], ['link', identity, 'evidence']):
                raise ValueError('the TEST copy supplies another reader/writer relation or offset')
        else:
            raise ValueError('the TEST copy supports only its exact reader/writer relation attachment')
        supported[fact].append(dict(origin=binding.origin_key, symbol=binding.symbol,
            claim=binding.claim.packet(), direction=direction,
            physical=physical, declared_width=symbol.value('width'),
            declared_signed=symbol.value('signed')))
    candidate = primary.packet()['candidate']
    scopes = (common.scope_digest(model), injection.scope_digest(model), coherent.scope_digest(model))
    if not test_contract.exact(scopes, (candidate['scope'], candidate['snapshot_scope'], candidate['coherent_scope'])):
        raise ValueError('the TEST copy facts differ from the exact full primary native scopes')
    return {fact: dict(scope=scopes[index], supported=supported[fact],
                       support='identity', scope_kind='bounded-byte-placement',
                       scale=False, declared_width_inference=False, cadence=False)
            for index, fact in enumerate(FACTS)}
