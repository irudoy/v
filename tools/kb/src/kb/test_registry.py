"""Explicit TEST origin, claimant and independent-fact registrations.

Registry requests describe obligations for an execution adapter. They are not
receipts and cannot establish CODE without independent proof and terminals.
"""

from dataclasses import dataclass
import json
from pathlib import PurePosixPath
import re

from kb import test_contract, test_origins

HEX = re.compile(r'[0-9a-f]{64}')
SUPPORTS = frozenset(('identity', 'scale', 'contract', 'role'))
CLAIMS = frozenset(('identity', 'scale', 'contract', 'bit', 'value', 'diagnostic'))
COMPATIBLE_SUPPORT = {'identity': frozenset(('identity',)),
                      'scale': frozenset(('scale',)),
                      'contract': frozenset(('contract',)),
                      'bit': frozenset(('role',)), 'value': frozenset(('role',)),
                      'diagnostic': frozenset(('identity', 'role'))}


def _text(value, label):
    if type(value) is not str or not value:
        raise ValueError(f'a TEST registration requires {label}')
    return value


def _hash(value, label):
    if type(value) is not str or HEX.fullmatch(value) is None:
        raise ValueError(f'a TEST registration requires an exact {label} digest')
    return value


def _source(value):
    _text(value, 'a source path')
    path = PurePosixPath(value)
    if path.is_absolute() or '..' in path.parts or str(path) != value or path.suffix != '.py':
        raise ValueError('a TEST registration requires a normalized repository Python path')
    return value


@dataclass(frozen=True)
class Claim:
    subject: str
    name: str

    def packet(self):
        _text(self.subject, 'an exact claimant')
        _text(self.name, 'an explicit claim name')
        if self.name not in CLAIMS:
            raise ValueError('a TEST registration requires an explicit claim name')
        return {'subject': self.subject, 'name': self.name}


@dataclass(frozen=True)
class Binding:
    origin_key: str
    context_digest: str
    path: str
    selector: str
    symbol: str
    claim: Claim
    support: str
    fact: str
    cases: tuple[str, ...]
    locator_text: str

    def packet(self):
        _hash(self.origin_key, 'owning-origin')
        _hash(self.context_digest, 'semantic-context')
        _source(self.path)
        _text(self.selector, 'a selector')
        _text(self.locator_text, 'an exact owning locator')
        locator = json.loads(self.locator_text)
        if (type(locator) is not list or len(locator) < 3
                or test_contract.digest(dict(locator=locator, path=self.path,
                                             selector=self.selector)) != self.origin_key):
            raise ValueError('the TEST owning locator differs from its attachment identity')
        _text(self.symbol, 'an exact symbol context')
        if test_origins.SYMBOL_KEY.fullmatch(self.symbol) is None:
            raise ValueError('a TEST registration requires a layout/address/kind symbol key')
        _text(self.fact, 'an independently checked fact key')
        if self.support not in SUPPORTS:
            raise ValueError('a TEST registration requires one explicit supported fact')
        claim = self.claim.packet()
        if self.support not in COMPATIBLE_SUPPORT[claim['name']]:
            raise ValueError('the TEST supported fact does not match its claimed property')
        if type(self.cases) is not tuple or not self.cases or len(set(self.cases)) != len(self.cases):
            raise ValueError('a TEST binding requires unique explicit observed cases')
        for nodeid in self.cases:
            _text(nodeid, 'a collected node ID')
            if (not nodeid.startswith(self.path + '::')
                    or nodeid.rsplit('::', 1)[-1].split('[', 1)[0] != self.selector):
                raise ValueError('the TEST binding uses another selector or source')
        return {'origin': self.origin_key, 'context': self.context_digest,
                'locator': locator,
                'path': self.path, 'selector': self.selector, 'symbol': self.symbol,
                'claim': claim, 'support': self.support,
                'fact': self.fact, 'cases': list(self.cases)}


@dataclass(frozen=True)
class Profile:
    key: str
    contract: test_contract.Contract
    bindings: tuple[Binding, ...]
    adapter: str
    facts: tuple[str, ...]
    gnu_regions: tuple[str, ...] = ()

    def packet(self):
        _text(self.key, 'a profile key')
        _text(self.adapter, 'an independent semantic adapter')
        if self.adapter == 'metadata' or not self.bindings:
            raise ValueError('TEST metadata consistency alone supplies no semantic admission')
        if type(self.bindings) is not tuple:
            raise ValueError('a TEST profile requires immutable binding order')
        if type(self.facts) is not tuple or not self.facts or len(set(self.facts)) != len(self.facts):
            raise ValueError('a TEST profile requires explicit independent fact keys')
        for fact in self.facts:
            _text(fact, 'an independent fact key')
        if type(self.contract) is not test_contract.Contract:
            raise ValueError('a TEST profile requires its registered execution contract')
        contract = self.contract.packet()
        nodeids = {case['nodeid'] for case in contract['cases']}
        bindings = [binding.packet() for binding in self.bindings]
        for binding in bindings:
            if binding['fact'] not in self.facts or not set(binding['cases']) <= nodeids:
                raise ValueError('a TEST binding has no registered fact or execution case')
        keys = [(row['origin'], row['claim']['subject'], row['claim']['name'], row['symbol'])
                for row in bindings]
        if len(set(keys)) != len(keys):
            raise ValueError('a TEST profile repeats an origin/claim/symbol binding')
        if type(self.gnu_regions) is not tuple or len(set(self.gnu_regions)) != len(self.gnu_regions):
            raise ValueError('a TEST profile requires unique explicit GNU region identities')
        for region in self.gnu_regions:
            _text(region, 'a GNU region identity')
        return {'key': self.key, 'contract': contract, 'adapter': self.adapter,
                'facts': list(self.facts), 'GNU_regions': list(self.gnu_regions),
                'bindings': bindings}


@dataclass(frozen=True)
class Request:
    profile: str
    profile_digest: str
    adapter: str
    binding_text: str
    origin_text: str

    def packet(self):
        import json
        return {'profile': self.profile, 'profile_digest': self.profile_digest,
                'adapter': self.adapter, 'binding': json.loads(self.binding_text),
                'origin': json.loads(self.origin_text)}


def claimed(symbol, claim):
    if claim == 'identity':
        if symbol is None:
            raise ValueError('the TEST identity anchor requires its symbol context')
        return Claim(symbol.key.key, 'identity')
    if claim is None or type(getattr(claim, 'subject', None)) is not str:
        raise ValueError('TEST qualification requires an explicit claimed subject and fact')
    result = Claim(claim.subject, claim.name)
    result.packet()
    return result


class Registry:
    """Exact declarative registrations; adapters and executions stay external."""

    def __init__(self, profiles, *, case_order=None):
        self._profiles = {}
        self._packets = {}
        self._bindings = {}
        if case_order is not None and (
                type(case_order) is not tuple or any(type(nodeid) is not str for nodeid in case_order)
                or len(set(case_order)) != len(case_order)):
            raise ValueError('the common TEST cohort requires one explicit immutable case order')
        self._case_order = case_order
        for profile in profiles:
            packet = profile.packet()
            if profile.key in self._profiles:
                raise ValueError('duplicate TEST profile identity')
            self._profiles[profile.key] = profile
            self._packets[profile.key] = test_contract.json_text(packet)
            for binding in profile.bindings:
                key = (binding.origin_key, binding.claim.subject, binding.claim.name, binding.symbol)
                if key in self._bindings:
                    raise ValueError('ambiguous TEST origin/claim/symbol registration')
                self._bindings[key] = (profile.key, binding)

    def packets(self):
        import json
        return [json.loads(self._packets[key]) for key in sorted(self._packets)]

    def profile(self, key):
        profile = self._profiles[key]
        if test_contract.json_text(profile.packet()) != self._packets[key]:
            raise ValueError('the TEST profile changed after registration')
        return profile

    def request(self, model, symbol, evidence, claim, origin):
        origin = test_origins.current(model, origin, evidence)
        return self._request(model, symbol, claim, origin)

    def obligation(self, model, symbol, binding, origin):
        """Resolve a declared producer obligation from its exact current owner."""
        origin = test_origins.rebind(model, origin)
        request = self._request(model, symbol, binding.claim, origin)
        if test_contract.json_text(request.packet()['binding']) != test_contract.json_text(binding.packet()):
            raise ValueError('the TEST producer obligation differs from its registered binding')
        return request

    def _request(self, model, symbol, claim, origin):
        if symbol is None or model.symbols.get(symbol.key) is not symbol:
            raise ValueError('the TEST request requires its current native symbol context')
        target = claimed(symbol, claim)
        target.packet()
        key = (origin.key, target.subject, target.name, symbol.key.key)
        found = self._bindings.get(key)
        if found is None:
            raise ValueError('the TEST owning origin, symbol or supported claim is unregistered')
        profile_key, binding = found
        profile = self._profiles[profile_key]
        packet = profile.packet()
        if test_contract.json_text(packet) != self._packets[profile_key]:
            raise ValueError('the TEST profile or typed parameter expectations changed')
        if (origin.context_digest != binding.context_digest
                or origin.path != binding.path or origin.selector != binding.selector
                or origin.locator_text != test_contract.json_text(json.loads(binding.locator_text))):
            raise ValueError('the TEST binding has stale facts or another selector')
        if origin.explicit_support is not None and origin.explicit_support != binding.support:
            raise ValueError('the TEST binding supports another explicit native fact')
        return Request(profile_key, test_contract.digest(packet), profile.adapter,
                       test_contract.json_text(binding.packet()), test_contract.json_text(origin.packet()))

    def cohort(self, nodeids=None):
        """Prepare one explicit case union; collection is not executed here."""
        cases = {}
        for key in sorted(self._profiles):
            profile = self._profiles[key]
            if test_contract.json_text(profile.packet()) != self._packets[key]:
                raise ValueError('the TEST profile changed before cohort preparation')
            for case in profile.contract.cases:
                if case.nodeid in cases and not test_contract.exact(cases[case.nodeid].packet(), case.packet()):
                    raise ValueError('shared TEST cases have different typed parameters')
                cases[case.nodeid] = case
        expected = tuple(cases) if self._case_order is None else self._case_order
        if set(expected) != cases.keys():
            raise ValueError('the common TEST case order omits or adds a registered case')
        if nodeids is None:
            nodeids = expected
        if type(nodeids) is not tuple or nodeids != expected:
            raise ValueError('the common TEST cohort must name every registered case exactly once in its declared order')
        for profile in self._profiles.values():
            own = tuple(case.nodeid for case in profile.contract.cases)
            if tuple(nodeid for nodeid in nodeids if nodeid in own) != own:
                raise ValueError('shared TEST profiles require conflicting actual case order')
        return test_contract.Contract('native-claim-contexts', tuple(cases[nodeid] for nodeid in nodeids))
