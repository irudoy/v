"""One actual TEST cohort with independently reconstructed semantic facts.

Adapters are explicit repository code. Each adapter supplies physical or
semantic checks in addition to pytest success; owning metadata, declaration
existence and successful reports alone cannot produce a qualified record.
"""

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

from kb import test_cohort, test_contract, test_origins, test_primary

SCHEMA = 1
HEX = re.compile(r'[0-9a-f]{64}')


def manifest(root, paths):
    """Read declared current inputs; a directory or missing source refuses."""
    root = Path(root).resolve()
    result = {}
    for path in paths:
        if type(path) is not str:
            raise ValueError('a TEST semantic input requires an exact repository path')
        relative = PurePosixPath(path)
        if (relative.is_absolute() or '..' in relative.parts or str(relative) != path
                or not relative.parts):
            raise ValueError('a TEST semantic input escapes its repository source boundary')
        physical = (root / path).resolve()
        if not physical.is_relative_to(root):
            raise ValueError('a TEST semantic input escapes through a source link')
        result[path] = hashlib.sha256(physical.read_bytes()).hexdigest()
    if not result:
        raise ValueError('a TEST semantic adapter has no consumed input sources')
    return {path: result[path] for path in sorted(result)}


@dataclass(frozen=True)
class Adapter:
    key: str
    inputs: tuple[str, ...]
    evaluate: object

    def packet(self, root):
        if (type(self.key) is not str or not self.key or self.key == 'metadata'
                or type(self.inputs) is not tuple or len(set(self.inputs)) != len(self.inputs)
                or not callable(self.evaluate)):
            raise ValueError('TEST qualification requires an explicit independent semantic adapter')
        module = getattr(self.evaluate, '__module__', None)
        function = getattr(self.evaluate, '__qualname__', None)
        if (type(module) is not str or type(function) is not str
                or '<' in function or not module.startswith('kb.')):
            raise ValueError('a TEST semantic adapter requires a named repository implementation')
        from inspect import getsourcefile
        source = getsourcefile(self.evaluate)
        if source is None:
            raise ValueError('the TEST semantic adapter implementation has no current source')
        try:
            path = Path(source).resolve().relative_to(Path(root).resolve()).as_posix()
        except ValueError as error:
            raise ValueError('the TEST semantic adapter implementation is outside its checkout') from error
        if path not in self.inputs:
            raise ValueError('the TEST semantic adapter omits its own executable source')
        return dict(key=self.key, implementation=dict(module=module, function=function),
                    inputs=manifest(root, self.inputs))


@dataclass(frozen=True)
class Preparation:
    native_model: str
    producer_inputs_text: str
    environment_text: str
    contexts_text: str
    adapters_text: str
    registry_text: str
    raw_declarations_text: str


class Engine:
    """Shared admission mechanics; no adapter or profile is discovered implicitly."""

    def __init__(self, registry, adapters, *, raw_declarations=()):
        if type(adapters) is not tuple or not adapters:
            raise ValueError('TEST qualification requires an explicit semantic adapter catalog')
        self.registry = registry
        self.cohort = test_cohort.Cohort(registry)
        self.adapters = {}
        for adapter in adapters:
            if type(adapter) is not Adapter or adapter.key in self.adapters:
                raise ValueError('TEST qualification repeats or replaces a semantic adapter')
            self.adapters[adapter.key] = adapter
        needed = {profile['adapter'] for profile in registry.packets()}
        if needed != self.adapters.keys():
            raise ValueError('TEST qualification has missing or unrelated semantic adapters')
        if type(raw_declarations) is not tuple or any(type(packet) is not dict for packet in raw_declarations):
            raise ValueError('TEST qualification requires an explicit immutable raw-capture declaration order')
        self.raw_declarations_text = test_contract.json_text(list(raw_declarations))
        regions = [packet.get('region') for packet in raw_declarations]
        if any(type(region) is not str or not region for region in regions) or len(set(regions)) != len(regions):
            raise ValueError('the TEST raw-capture catalog repeats or omits a region identity')
        requested = {region for packet in registry.packets() for region in packet['GNU_regions']}
        if not set(regions) <= requested:
            raise ValueError('the TEST raw-capture catalog contains an unrelated execution region')

    def contexts(self, model):
        return {packet['key']: self.contexts_for(model, self.registry.profile(packet['key']))
                for packet in self.registry.packets()}

    def require_coverage(self, model):
        """Every native attachment needs a registration, including relation-only items."""
        origins = test_origins.index(model)
        registered = {binding['origin'] for profile in self.registry.packets()
                      for binding in profile['bindings']}
        if registered != origins.keys():
            missing = sorted(origins.keys() - registered)
            unrelated = sorted(registered - origins.keys())
            raise ValueError(f'TEST semantic catalog coverage differs: missing={missing}, unrelated={unrelated}')
        self.contexts(model)

    def inputs(self, root):
        return {key: adapter.packet(root) for key, adapter in sorted(self.adapters.items())}

    def require_raw_catalog(self, primary):
        declarations = json.loads(self.raw_declarations_text)
        if primary is not None and type(primary) is not test_primary.Primary:
            raise ValueError('the TEST raw catalog requires the original shared primary record')
        if primary is None:
            if declarations:
                raise ValueError('the TEST raw-capture catalog lacks its original shared GNU process')
            return
        actual = primary.raw_regions(required=False)
        if tuple(actual) != tuple(packet['region'] for packet in declarations):
            raise ValueError('the TEST raw original omits, adds or reorders a declared stock region')
        for expected in declarations:
            if not test_contract.exact(actual[expected['region']]['capture']['spec'], expected):
                raise ValueError('the TEST raw original changes its explicit ABI, entries or case selections')

    def environment(self, root):
        """Bind the shared collector, assertion runtime and actual pytest sources."""
        root = Path(root).resolve()
        paths = {'pyproject.toml', 'uv.lock'}
        paths.update(path.relative_to(root).as_posix()
                     for path in (root / 'tools/kb/src/kb').rglob('*.py'))
        for case in self.cohort.contract.cases:
            path = PurePosixPath(case.nodeid.split('::', 1)[0])
            if path.suffix != '.py' or path.is_absolute() or '..' in path.parts:
                raise ValueError('the TEST cohort has an invalid repository source path')
            paths.add(path.as_posix())
            for parent in path.parents:
                conftest = parent / 'conftest.py'
                if (root / conftest).is_file():
                    paths.add(conftest.as_posix())
        from kb import test_evidence
        return dict(inputs=manifest(root, paths), runtime=test_evidence.runtime())

    def require_model(self, model):
        """A consumer overlay may change owned facts, never execution settings."""
        from kb import repo
        required = ('root', 'layouts', 'spaces', 'functions', 'config', 'names', 'overlay')
        if any(not hasattr(model, name) for name in required):
            raise ValueError('qualified TEST semantics require a complete current native model')
        for path in model.overlay:
            path = Path(path)
            if path.is_absolute() or '..' in path.parts or (
                    (not path.parts or path.parts[0] != 'kb') and path != repo.OWNER_CONFIG):
                raise ValueError('the TEST consumer overlay changes an execution input')

    def reconstruct(self, model, primary):
        """Execute independent fact equations against declared original observations.

        This is called by the producer and independently by the finalizer. The
        finalizer receives the original GNU record, never a stored pass result.
        """
        self.require_model(model)
        root = Path(model.root).resolve()
        gnu_regions = {region for packet in self.registry.packets() for region in packet['GNU_regions']}
        if primary is not None and type(primary) is not test_primary.Primary:
            raise ValueError('a TEST adapter requires the original shared GNU record')
        if gnu_regions and primary is None:
            raise ValueError('the TEST semantic profiles lack their original GNU execution')
        self.require_raw_catalog(primary)
        gnu = primary.require(model) if primary is not None else None
        if gnu_regions and not gnu_regions <= primary.available_regions():
            raise ValueError('the TEST semantic profiles omit a declared original GNU region')
        contexts = self.contexts(model)
        before = self.inputs(root)
        result = {}
        for packet in self.registry.packets():
            profile = self.registry.profile(packet['key'])
            adapter = self.adapters[profile.adapter]
            proof = adapter.evaluate(model, profile, contexts[profile.key], primary)
            if type(proof) is not dict or set(proof) != set(profile.facts):
                raise ValueError('the TEST semantic adapter omits or broadens its declared fact set')
            if any(type(value) is not dict or not value for value in proof.values()):
                raise ValueError('the TEST semantic adapter supplies no independent fact observations')
            # Immutable transport rejects opaque objects, non-finite numbers,
            # custom equality and later mutations by the adapter.
            proof = json.loads(test_contract.json_text(test_contract.encode(proof)))
            result[profile.key] = dict(
                profile_digest=test_contract.digest(profile.packet()),
                contexts=contexts[profile.key], adapter=before[adapter.key],
                GNU=gnu if profile.gnu_regions else None, proof=proof)
        if self.inputs(root) != before or not test_contract.exact(self.contexts(model), contexts):
            raise ValueError('TEST semantic inputs or native owning contexts change during reconstruction')
        return result

    def begin(self, model, *, native_model, producer_inputs):
        """Snapshot execution obligations before pytest collection and fixture setup."""
        self.require_model(model)
        self.require_coverage(model)
        if type(native_model) is not str or HEX.fullmatch(native_model) is None or model.overlay:
            raise ValueError('the TEST producer requires a complete native source snapshot')
        text = test_contract.json_text
        return Preparation(native_model, text(producer_inputs), text(self.environment(model.root)),
            text(self.contexts(model)), text(self.inputs(model.root)), text(self.registry.packets()),
            self.raw_declarations_text)

    def candidate(self, capture, exitstatus, model, primary, *, preparation):
        if capture.contract.packet() != self.cohort.contract.packet():
            raise ValueError('the TEST producer captured another execution contract')
        if type(preparation) is not Preparation:
            raise ValueError('the TEST producer lacks its pre-collection source and context preparation')
        self.require_coverage(model)
        environment = json.loads(preparation.environment_text)
        text = test_contract.json_text
        if (text(self.environment(model.root)) != preparation.environment_text
                or text(self.contexts(model)) != preparation.contexts_text
                or text(self.inputs(model.root)) != preparation.adapters_text
                or text(self.registry.packets()) != preparation.registry_text
                or self.raw_declarations_text != preparation.raw_declarations_text):
            raise ValueError('TEST sources or owning contexts change after pre-collection preparation')
        witnesses = self.reconstruct(model, primary)
        if not test_contract.exact(self.environment(model.root), environment):
            raise ValueError('the TEST collector sources or assertion runtime change during observation')
        return capture.candidate(exitstatus, complete=True, semantic_schema=SCHEMA,
            native_model=preparation.native_model,
            producer_inputs=json.loads(preparation.producer_inputs_text),
            profile_registry=self.registry.packets(), witnesses=witnesses,
            execution_environment=environment,
            raw_catalog=json.loads(preparation.raw_declarations_text))

    def prepare(self, record, model, primary):
        """Validate an unpublished record against an independent native snapshot."""
        from kb import test_evidence
        native_model = test_evidence.model_digest(model)
        producer_inputs = test_evidence.producer_inputs(model.root)
        self.require_coverage(model)
        self.cohort.require_terminal(record, model.root)
        candidate = record['candidate']
        if (not test_contract.exact(candidate.get('semantic_schema'), SCHEMA)
                or not test_contract.exact(candidate.get('profile_registry'), self.registry.packets())
                or not test_contract.exact(candidate.get('raw_catalog'), json.loads(self.raw_declarations_text))
                or not test_contract.exact(candidate.get('producer_inputs'), producer_inputs)
                or not test_contract.exact(candidate.get('execution_environment'), self.environment(model.root))
                or type(native_model) is not str or HEX.fullmatch(native_model) is None
                or candidate.get('native_model') != native_model):
            raise ValueError('the TEST producer scope or native inputs lack independent finalization')
        expected = self.reconstruct(model, primary)
        if not test_contract.exact(candidate.get('witnesses'), expected):
            raise ValueError('the TEST semantic witness disagrees with independent reconstruction')
        if test_evidence.NODEID in {case.nodeid for case in self.cohort.contract.cases}:
            self.require_image_scan(candidate, model)
        views = {packet['key']: self.cohort.view(candidate, packet['key'])
                 for packet in self.registry.packets()}
        return {**record, 'schema': test_contract.SCHEMA, 'semantic_schema': SCHEMA, 'native_model': native_model,
                'native_inputs': test_contract.digest(test_contract.encode(producer_inputs)),
                'profile_views': views}

    def failure(self, evidence, symbol, model, claim, origin, *, record, primary):
        """Consumer admission is scoped to one exact current registered claimant."""
        try:
            self.require_model(model)
            request = self.registry.request(model, symbol, evidence, claim, origin)
            profile = self.registry.profile(request.profile)
            candidate = record['candidate']
            if (not test_contract.exact(record['schema'], test_contract.SCHEMA)
                    or not test_contract.exact(record['semantic_schema'], SCHEMA)
                    or not test_contract.exact(candidate['semantic_schema'], SCHEMA)
                    or type(record['native_model']) is not str
                    or HEX.fullmatch(record['native_model']) is None
                    or record['native_model'] != candidate['native_model']
                    or not test_contract.exact(candidate['raw_catalog'], json.loads(self.raw_declarations_text))
                    or not test_contract.exact(candidate['execution_environment'], self.environment(model.root))
                    or record['native_inputs'] != test_contract.digest(
                        test_contract.encode(candidate['producer_inputs']))):
                return 'TEST semantic provenance lacks independent native finalization'
            self.require_raw_catalog(primary)
            self.cohort.require_terminal(record, model.root)
            self.cohort.require_view(candidate, profile.key, record['profile_views'][profile.key])
            original = [packet for packet in candidate['profile_registry'] if packet['key'] == profile.key]
            if not test_contract.exact(original, [profile.packet()]):
                return 'the qualified TEST profile has other native claim or owning-context bindings'
            from kb import test_evidence
            if any(binding.path == test_evidence.PATH and binding.selector == test_evidence.KEY
                   for binding in profile.bindings):
                self.require_image_scan(candidate, model)
            contexts = self.contexts_for(model, profile)
            adapter = self.adapters[profile.adapter]
            before = adapter.packet(model.root)
            gnu = None
            if profile.gnu_regions:
                if type(primary) is not test_primary.Primary:
                    return 'the qualified TEST lacks its original shared GNU record'
                gnu = primary.require(model)
                if not set(profile.gnu_regions) <= primary.available_regions():
                    return 'the qualified TEST lacks its declared original GNU regions'
            proof = adapter.evaluate(model, profile, contexts, primary)
            if (type(proof) is not dict or set(proof) != set(profile.facts)
                    or any(type(value) is not dict or not value for value in proof.values())):
                return 'the TEST semantic adapter omits its independently supported facts'
            expected = dict(profile_digest=test_contract.digest(profile.packet()), contexts=contexts,
                adapter=before, GNU=gnu,
                proof=json.loads(test_contract.json_text(test_contract.encode(proof))))
            if (not test_contract.exact(candidate['witnesses'][profile.key], expected)
                    or adapter.packet(model.root) != before
                    or not test_contract.exact(self.contexts_for(model, profile), contexts)):
                return 'the TEST semantic facts, source inputs or owning contexts are stale'
            return None
        except (OSError, ValueError, TypeError, KeyError, AttributeError, IndexError,
                RecursionError, ImportError):
            return 'missing or invalid qualified TEST semantic context'

    def contexts_for(self, model, profile):
        """Resolve only this profile; unrelated native owners do not supply its facts."""
        result = []
        from kb.model import SymbolKey
        for binding in profile.bindings:
            match = test_origins.SYMBOL_KEY.fullmatch(binding.symbol)
            symbol = model.symbols.get(SymbolKey(match[1], match[3], int(match[2], 16)))
            origin = test_origins.capture(model, json.loads(binding.locator_text))
            result.append(self.registry.obligation(model, symbol, binding, origin).packet())
        return result

    def require_image_scan(self, candidate, model):
        """Retain the actual registered image/profile observation in the common run."""
        from kb import test_evidence
        from kb.model import SymbolKey
        observed = candidate['image_scan']
        symbol = model.symbols[SymbolKey(*test_evidence.SYMBOL)]
        current = test_evidence.context(model, symbol, test_evidence.item())
        if (type(observed) is not dict or set(observed) != {'context', 'witness'}
                or not test_contract.exact(observed['context'], current)):
            raise ValueError('the common TEST run substitutes the registered image-scan context')
        refused = test_evidence.witness_failure(observed['witness'], current)
        if refused:
            raise ValueError(refused)
