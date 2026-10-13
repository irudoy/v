"""Pytest candidate for the registered image-scan case; terminal exit is external."""

import hashlib
from functools import wraps
from pathlib import Path
import tomllib
import uuid

import pytest

from kb import compile, lock, repo, test_evidence as evidence
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
        self.collected, self.reports, self.parameters = [], [], None
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
        self.context = evidence.context(model, symbol, evidence.item())

    def image_packets(self, images):
        return {name: {'path': image.path.resolve().relative_to(self.root).as_posix(),
                       'sha256': hashlib.sha256(image.data).hexdigest()}
                for name, image in images.items()}

    def observe(self, profiles, images, facts):
        if self.witness is not None:
            raise ValueError('the registered TEST witness is emitted more than once')
        if facts != evidence.facts():
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
        stable = evidence.context(self.model, self.symbol, evidence.item()) == self.context
        complete = (exitstatus == 0 and self.collected == [evidence.NODEID]
                    and self.parameters == evidence.encode({}) and self.witness is not None
                    and self.reports == [['setup', 'passed', False], ['call', 'passed', False],
                                        ['teardown', 'passed', False]]
                    and stable)
        candidate = {'schema': evidence.SCHEMA, 'run_id': str(uuid.uuid4()),
                     'nodeid': evidence.NODEID, 'collected': self.collected,
                     'parameters': self.parameters, 'reports': self.reports,
                     'context': self.context, 'witness': self.witness,
                     'complete': complete, 'exitstatus': int(exitstatus)}
        evidence.publish(self.output, candidate)
        print('kb-test-candidate sha256=' + evidence.digest(candidate))

    def close(self):
        self.patch.undo()
        if self.lease is not None:
            self.lease.__exit__(None, None, None)
            self.lease = None


def pytest_addoption(parser):
    parser.addoption('--kb-test-candidate', default=None)


def pytest_configure(config):
    if config.getoption('--kb-test-candidate'):
        config._kb_test_witness = State(config)


def pytest_collection_finish(session):
    state = getattr(session.config, '_kb_test_witness', None)
    if state is not None:
        state.collected = [item.nodeid for item in session.items]
        for item in session.items:
            if item.nodeid == evidence.NODEID:
                callspec = getattr(item, 'callspec', None)
                state.parameters = evidence.encode(callspec.params if callspec else {})


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    result = yield
    report = result.get_result()
    state = getattr(item.config, '_kb_test_witness', None)
    if state is not None and item.nodeid == evidence.NODEID:
        state.reports.append([report.when, report.outcome, hasattr(report, 'wasxfail')])


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
