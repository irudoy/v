"""Pytest candidate for the registered image-scan case; terminal exit is external."""

import hashlib
from functools import wraps
from pathlib import Path
import sys
import tomllib

import pytest

from kb import compile, lock, repo, test_contract, test_evidence as evidence
from kb.model import SymbolKey


class _ReadTap:
    def __init__(self, source, reads):
        self.source, self.reads = source, reads

    def read(self, *args, **kwargs):
        data = self.source.read(*args, **kwargs)
        self.reads.append(data)
        return data

    def __getattr__(self, name):
        return getattr(self.source, name)


class State:
    def __init__(self, config):
        self.config = config
        self.root = repo.ROOT.resolve()
        self.output = Path(config.getoption('--kb-test-candidate'))
        if self.output.exists():
            raise ValueError('a TEST candidate output already exists')
        self.capture = test_contract.Capture(evidence.CONTRACT, {
            'mode': config.getoption('assertmode'), 'python_optimize': sys.flags.optimize})
        self.witness = None
        self.profile_origins = []
        self.preparations = {}
        self.image_reads = []
        self.original_load = tomllib.load
        self.lease = lock.held(self.root)
        self.lease.__enter__()
        self.patch = pytest.MonkeyPatch()

        def load(source, *args, **kwargs):
            path = getattr(source, 'name', None)
            if path is None or Path(path).resolve() != self.root / evidence.PROFILE:
                return self.original_load(source, *args, **kwargs)
            reads = []
            result = self.original_load(_ReadTap(source, reads), *args, **kwargs)
            if len(reads) != 1 or type(reads[0]) is not bytes:
                raise ValueError('profile parsing lacks one exact binary origin')
            self.profile_origins.append(hashlib.sha256(reads[0]).hexdigest())
            return result

        self.patch.setattr(tomllib, 'load', load)
        from patches import rom_address_profiles
        if rom_address_profiles.load_registry.cache_info().currsize:
            self.close()
            raise ValueError('profile preparation already exists without a captured origin')
        original_registry = rom_address_profiles.load_registry

        @wraps(original_registry)
        def registry(*args, **kwargs):
            before = len(self.profile_origins)
            result = original_registry(*args, **kwargs)
            if len(self.profile_origins) > before:
                origins = set(self.profile_origins[before:])
                if len(origins) != 1:
                    raise ValueError('profile preparation has mixed binary origins')
                self.preparations[id(result)] = (next(iter(origins)),
                                                 evidence.digest(evidence.encode(result)))
            return result

        for name in ('cache_info', 'cache_clear', 'cache_parameters'):
            if hasattr(original_registry, name):
                setattr(registry, name, getattr(original_registry, name))
        self.patch.setattr(rom_address_profiles, 'load_registry', registry)
        from tools import rom_homology
        original_images = rom_homology.load_images

        @wraps(original_images)
        def images(*args, **kwargs):
            result = original_images(*args, **kwargs)
            self.image_reads.extend(self.image_packets(result).values())
            return result

        self.patch.setattr(rom_homology, 'load_images', images)
        model = compile.build(self.root)
        symbol = model.symbols[SymbolKey(*evidence.SYMBOL)]
        self.model, self.symbol = model, symbol
        self.native_model = evidence.model_digest(model)
        self.producer_inputs = evidence.producer_inputs(self.root)
        self.context = evidence.context(model, symbol, evidence.item())
        self.profile_engine = None
        self.profile_primary = None
        self.profile_preparation = None
        self.profile_references = None

    def bind_profiles(self, engine, primary, references):
        """Use the same real collector for an explicit complete semantic cohort."""
        from kb import test_execution
        if (type(engine) is not test_execution.Engine or self.profile_engine is not None
                or self.capture.collected or self.capture.reports or self.witness is not None):
            raise ValueError('the TEST profile cohort must bind once before collection and observation')
        if evidence.NODEID not in {case.nodeid for case in engine.cohort.contract.cases}:
            raise ValueError('the shared TEST cohort omits the registered image-scan case')
        from kb import test_primary
        prepared = test_primary.load(self.root, references)
        if not test_contract.exact(prepared, primary):
            raise ValueError('the common TEST run substitutes its original primary preparation')
        self.profile_preparation = engine.begin(self.model, native_model=self.native_model,
                                               producer_inputs=self.producer_inputs)
        self.capture = test_contract.Capture(engine.cohort.contract, self.capture.assertions)
        self.profile_engine, self.profile_primary = engine, primary
        self.profile_references = test_contract.json_text(references)

    def image_packets(self, images):
        return {name: {'path': image.path.resolve().relative_to(self.root).as_posix(),
                       'sha256': hashlib.sha256(image.data).hexdigest()}
                for name, image in images.items()}

    def observe(self, profiles, images, facts):
        if self.witness is not None:
            raise ValueError('the registered TEST witness is emitted more than once')
        if not test_contract.exact(facts, evidence.facts()):
            raise ValueError('the TEST witness names other supported facts')
        origin = self.context['inputs'][evidence.PROFILE]
        if not self.profile_origins or set(self.profile_origins) != {origin}:
            raise ValueError('the actual profile preparation origin is unknown or stale')
        routine = profiles['1ME3B'].ignition_unreferenced_routine
        if (routine.start, routine.end) != (0x791A4, 0x797CC):
            raise ValueError('the TEST witness supports another region')
        if profiles['1ND0A'].ignition_unreferenced_routine is not None:
            raise ValueError('the TEST witness supports another layout comparison')
        packet = evidence.encode(profiles)
        profile_digest = evidence.digest(packet)
        if self.preparations.get(id(profiles)) != (origin, profile_digest):
            raise ValueError('the consumed profile values differ from their captured preparation')
        image_packets = self.image_packets(images)
        for image in [*self.image_reads, *image_packets.values()]:
            if self.context['inputs'].get(image['path']) != image['sha256']:
                raise ValueError('actual consumed image bytes disagree with the input manifest')
        self.witness = {'facts': facts, 'profile_origin': origin,
                        'profiles': packet, 'profiles_digest': profile_digest,
                        'images': image_packets, 'fixture_image_reads': self.image_reads}

    def finish(self, exitstatus):
        stable = (test_contract.exact(evidence.context(self.model, self.symbol, evidence.item()), self.context)
                  and evidence.model_digest(self.model) == self.native_model
                  and evidence.producer_inputs(self.root) == self.producer_inputs)
        if self.profile_engine is None:
            candidate = self.capture.candidate(exitstatus,
                         complete=self.witness is not None and stable,
                         context=self.context, native_model=self.native_model,
                         producer_inputs=self.producer_inputs, witness=self.witness)
        else:
            if not stable or self.witness is None:
                raise ValueError('the shared TEST cohort lacks stable native inputs or its actual image-scan witness')
            candidate = self.profile_engine.candidate(self.capture, exitstatus, self.model,
                self.profile_primary, preparation=self.profile_preparation)
            candidate['image_scan'] = dict(context=self.context, witness=self.witness)
            import json
            from kb import test_primary
            references = json.loads(self.profile_references)
            if not test_contract.exact(test_primary.load(self.root, references), self.profile_primary):
                raise ValueError('the TEST original primary preparation changes during execution')
            candidate['primary_records'] = references
        evidence.publish(self.output, candidate)
        print('\n' + test_contract.MARKER + evidence.digest(candidate))

    def close(self):
        self.patch.undo()
        if self.lease is not None:
            self.lease.__exit__(None, None, None)
            self.lease = None


def pytest_addoption(parser):
    parser.addoption('--kb-test-candidate', default=None)
    from kb import test_primary
    parser.addoption(test_primary.COPY_OPTION, default=None)
    parser.addoption(test_primary.SID22_OPTION, default=None)


def pytest_configure(config):
    from kb import test_primary
    copy_path = config.getoption(test_primary.COPY_OPTION)
    sid_path = config.getoption(test_primary.SID22_OPTION)
    if bool(copy_path) != bool(sid_path) or ((copy_path or sid_path) and not config.getoption('--kb-test-candidate')):
        raise ValueError('common TEST primary references require both preparations and the actual candidate')
    if config.getoption('--kb-test-candidate'):
        config._kb_test_witness = State(config)
        if copy_path:
            from kb import test_catalog
            state = config._kb_test_witness
            references = test_primary.references(state.root, copy_path, sid_path)
            primary = test_primary.load(state.root, references)
            primary.require(state.model)
            state.bind_profiles(test_catalog.build(state.model), primary, references)


def pytest_collection_finish(session):
    state = getattr(session.config, '_kb_test_witness', None)
    if state is not None:
        state.capture.collect([(item.nodeid, getattr(item, 'callspec', None).params
                                if hasattr(item, 'callspec') else {})
                               for item in session.items])


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    result = yield
    report = result.get_result()
    state = getattr(item.config, '_kb_test_witness', None)
    if state is not None:
        state.capture.report(item.nodeid, report.when, report.outcome, hasattr(report, 'wasxfail'))


@pytest.fixture
def execution_witness(request):
    state = getattr(request.config, '_kb_test_witness', None)
    if state is None:
        return lambda profiles, images, facts: None
    if request.node.nodeid != evidence.NODEID:
        raise ValueError('the execution witness belongs to another collected case')
    return state.observe


def pytest_sessionfinish(session, exitstatus):
    state = getattr(session.config, '_kb_test_witness', None)
    if state is not None:
        state.finish(exitstatus)


def pytest_unconfigure(config):
    state = getattr(config, '_kb_test_witness', None)
    if state is not None:
        state.close()
