"""Qualified local execution of the registered 1ME3B image-scan witness."""

import hashlib
import json
from pathlib import Path
import platform
import sys

from kb import repo, test_contract
from kb.test_contract import SCHEMA, digest, encode, exact, json_text

PATH = 'patches/tests/test_rom_address_profiles.py'
KEY = 'test_1me3b_unreferenced_ignition_routine_is_bound_to_the_image'
NODEID = PATH + '::' + KEY
CONTRACT = test_contract.Contract('1me3b-image-scan', (test_contract.Case(NODEID, {}),))
MEANING = 'ignition_unreferenced_routine/const'
SYMBOL = ('1me3b', 'const', 0x791A4)
NOTE = ('Stock-image scan for region 000791a4..000797cb rejects aligned inbound '
        'pointer values in occupied bytes and direct PC-relative branches from '
        'outside the region to entry 000791a4.')
PROFILE = 'patches/rom-address-profiles.toml'
RECEIPT = Path('.kb/test-receipts/1me3b-image-scan.json')
PRODUCER_FILES = ('tools/kb/src/kb/test_evidence.py', 'tools/kb/src/kb/test_witness.py')
# Full-context mode requires a catalog covering every native TEST attachment.
REQUIRE_CONTEXTS = False
EXECUTION_INPUTS = (
    PATH, 'patches/tests/conftest.py', 'pyproject.toml', 'uv.lock',
    'patches/rom_address_profiles.py', PROFILE,
    'patches/map_switching_layout.py', 'patches/map-switching-layout.toml',
    'patches/rolling_launch_layout.py', 'patches/rolling-launch-layout.toml',
    'patches/can_telemetry_layout.py', 'patches/can-telemetry-layout.toml',
    'patches/can_telemetry_profile.py', 'patches/can-telemetry-profile.toml',
    'patches/can_telemetry.py', 'patches/rolling_launch.py',
    'patches/jk08a-runtime-reservations.toml',
    'tools/logs/can_telemetry.py', 'tools/logs/can_telemetry_schema.py',
    'tools/mapkit/rom.py', 'tools/rom_homology.py',
    'rom-images/roms.csv', 'rom-images/homology.toml',
)


def facts():
    return {'region_start': '000791a4', 'region_end_exclusive': '000797cc',
            'pointer_alignment_bytes': 2, 'pointer_scan': 'occupied bytes',
            'pointer_targets': 'whole region', 'direct_branch_targets': 'entry only',
            'entry': '000791a4', 'other_layout': '1nd', 'other_region': 'absent'}


def item():
    return {'kind': 'test', 'supports': 'identity', 'path': PATH, 'key': KEY, 'note': NOTE}


def model_digest(model):
    """Public compiled values plus exact input identity, without memory IDs."""
    from kb import convert
    required = ('layouts', 'spaces', 'functions', 'config', 'names', 'overlay')
    if any(not hasattr(model, name) for name in required) or model.overlay:
        raise ValueError('a complete native model without an overlay is required')
    return digest(encode({'facts': convert.dump(model),
                          **{name: getattr(model, name) for name in required}}))


def scope_digest(model, symbol):
    """Current identity facts and geometry; unrelated writer facts are independent.

    The producer and finalizer bind the complete native snapshot separately.
    An effective overlay may change other owned documents and review records;
    it cannot substitute the test, profile, ROM, L0 or execution configuration.
    """
    from kb import convert
    required = ('layouts', 'spaces', 'functions', 'config', 'names', 'overlay')
    if any(not hasattr(model, name) for name in required):
        raise ValueError('a complete compiled model is required')
    for path in model.overlay:
        path = Path(path)
        if path.is_absolute() or '..' in path.parts or (
                (not path.parts or path.parts[0] != 'kb') and path != repo.OWNER_CONFIG):
            raise ValueError('the overlay changes an execution input')
    meaning = symbol.meaning
    value = lambda data: convert._value(model, data)
    symbols = {key: {'key': member.key, 'name': member.name, 'generated': member.generated,
                     'former': member.former, 'props': value(member.props),
                     'evidence': value(member.evidence), 'sources': member.sources,
                     'implicit': member.implicit}
               for key, member in meaning.symbols.items()}
    links = {(link.owner.key, link.type, link.to.key, link.slot, link.offset):
             (value(link.props), value(link.evidence), link.stated, link.roles, link.sources)
             for link in model.links if link.owner is meaning or link.to is meaning}
    # These tables contain knowledge ownership and reviews, not execution settings.
    settings = {key: data for key, data in model.config.items()
                if key not in ('names', 'reconciliation', 'source_bindings')}
    return digest(encode({
        'meaning': {'key': meaning.key, 'kind': meaning.kind, 'semantic': meaning.semantic,
                    'props': value(meaning.props), 'tables': value(meaning.tables),
                    'names': meaning.other_names, 'sources': meaning.sources,
                    'tier': meaning.tier, 'name_sources': meaning.name_sources,
                    'groups': value(meaning.groups),
                    'statuses': {layout: (status.state, value(status.props),
                                         value(status.evidence), status.sources)
                                 for layout, status in meaning.statuses.items()}},
        'symbols': symbols, 'links': links, 'settings': settings,
        'files': {key: src for key, (subject, src) in model.files.items()
                  if subject is meaning or any(subject is member
                                               for member in meaning.symbols.values())},
        **{name: getattr(model, name) for name in ('layouts', 'spaces', 'functions')},
    }))


def inputs(root):
    """Execution closure and exact identity owner, independent of other KB facts.

    Stock-profile validation consumes the profile/layout/telemetry manifests,
    family/catalog declarations and catalog image bytes. Compiler code also
    binds interpretation of the current typed scope; whole-model source inputs
    belong to producer provenance, not the image-scan freshness boundary.
    """
    from kb import store
    paths = set(EXECUTION_INPUTS)
    paths.update(p.relative_to(root).as_posix()
                 for p in (root / 'tools/kb/src/kb').rglob('*.py'))
    paths.add(store.path_of('const', MEANING.split('/')[0]).as_posix())
    paths.update(image.path.relative_to(root).as_posix() for image in repo.images(root).values())
    return {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in sorted(paths)}


def producer_inputs(root):
    """Complete compiler provenance, independently finalized for the native run."""
    from kb import compatibility, fingerprint
    paths = set(fingerprint.inputs(root))
    paths.update(PRODUCER_FILES)
    paths.update((PATH, 'tools/rom_homology.py', 'pyproject.toml', 'uv.lock'))
    paths.update(p.relative_to(root).as_posix() for p in (root / 'patches').rglob('*')
                 if p.is_file() and p.suffix in ('.py', '.toml'))
    result = {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in sorted(paths)}
    result['@reference-commit'] = compatibility.reference_commit(root)
    return result


def runtime():
    from importlib.metadata import version
    return {'python': sys.version, 'implementation': platform.python_implementation(),
            'pytest': version('pytest'), 'python_optimize': sys.flags.optimize}


def public_packet(model, symbol, evidence):
    if model is None or symbol is None or getattr(model, 'root', None) is None:
        raise ValueError('complete model and symbol context is required')
    if model.symbols.get(symbol.key) is not symbol:
        raise ValueError('the symbol does not belong to this model')
    if (symbol.layout, symbol.kind, symbol.address) != SYMBOL:
        raise ValueError('the registered witness supports another symbol')
    if symbol.meaning is None or symbol.meaning.key != MEANING:
        raise ValueError('the registered witness supports another meaning')
    if not exact(evidence, item()) or not any(exact(evidence, entry) for entry in symbol.evidence):
        raise ValueError('the registered witness supports another role or fact scope')
    return {'meaning': MEANING, 'symbol': list(SYMBOL), 'support': 'identity',
            'evidence': dict(evidence), 'facts': facts()}


def context(model, symbol, evidence):
    root = Path(model.root).resolve()
    return {'root': str(root), 'public': public_packet(model, symbol, evidence),
            'model': scope_digest(model, symbol), 'inputs': inputs(root), 'runtime': runtime()}


def registered(evidence, symbol=None):
    """The selected key and symbol cannot escape qualification by substitution."""
    return (evidence.get('key') == KEY or
            (symbol is not None and
             (symbol.layout, symbol.kind, symbol.address) == SYMBOL))


def identity_only(symbol):
    return (symbol is not None and (symbol.layout, symbol.kind, symbol.address) == SYMBOL
            and any(entry.get('kind') == 'test' and entry.get('key') == KEY
                    for entry in symbol.evidence))


def requires_origin(evidence, symbol=None):
    return REQUIRE_CONTEXTS or registered(evidence, symbol)


def receipt_path(root):
    return Path(root) / RECEIPT


def dependencies(root, *, receipt=None):
    """A missing receipt, original process or stream remains a live dependency."""
    paths = {str(RECEIPT)}
    try:
        record = json.loads(test_contract._read(root, RECEIPT) if receipt is None else receipt)
        named = [record['process_path'], *(record['terminal'][name] for name in ('stdout', 'stderr'))]
        if any(type(path) is not str or '..' in Path(path).parts for path in named):
            raise ValueError('invalid TEST output path')
        paths.update(named)
        if 'semantic_schema' in record:
            for declared in record['candidate']['primary_records'].values():
                path = declared['path']
                if type(path) is not str or '..' in Path(path).parts:
                    raise ValueError('invalid TEST primary preparation path')
                paths.add(path)
                try:
                    primary = json.loads(test_contract._read(root, path))
                    original = (primary['process_path'], *(primary['terminal'][name]
                                                         for name in ('stdout', 'stderr')))
                    if any(type(name) is not str or '..' in Path(name).parts for name in original):
                        raise ValueError('invalid TEST primary terminal path')
                    paths.update(original)
                except (OSError, ValueError, TypeError, KeyError):
                    pass
    except (OSError, ValueError, TypeError, KeyError):
        pass
    return paths


def witness_failure(witness, expected_context):
    """Validate the actual image/profile observations independently of case scope."""
    if (not exact(witness['facts'], facts())
            or witness['profile_origin'] != expected_context['inputs'][PROFILE]):
        return 'TEST execution has wrong facts or unknown profile preparation origin'
    if digest(witness['profiles']) != witness['profiles_digest']:
        return 'TEST execution profile values are inconsistent'
    for image in [*witness['images'].values(), *witness['fixture_image_reads']]:
        if expected_context['inputs'].get(image['path']) != image['sha256']:
            return 'TEST execution image bytes lack exact input binding'
    if '1ME3B' not in witness['images'] or not witness['fixture_image_reads']:
        return 'TEST execution lacks its stock image'
    return None


def failure(evidence, symbol=None, model=None, claim=None, *, record=None, origin=None):
    """None only for a qualified receipt or an unregistered legacy witness."""
    if not registered(evidence, symbol):
        if REQUIRE_CONTEXTS or (type(record) is dict and 'semantic_schema' in record):
            return profile_failure(evidence, symbol, model, claim, record=record, origin=origin)
        return None
    try:
        if origin is not None:
            from kb import test_origins
            owning = test_origins.current(model, origin, evidence)
            if owning.kind != 'symbol' or symbol is None or owning.owner != symbol.key.key:
                return 'the registered image-scan TEST requires its direct owning symbol attachment'
        public_packet(model, symbol, evidence)
        if claim != 'identity':
            from kb import checks
            meaning_claim = (claim is not None and claim.symbol is None
                             and symbol.meaning.home_symbol is symbol
                             and claim.subject in (MEANING, checks._subject(symbol.meaning)))
            symbol_claim = (claim is not None and claim.symbol is symbol
                            and claim.subject in (MEANING, symbol.key.key,
                                                  checks._subject(symbol.meaning)))
            if claim is None or claim.name != 'identity' or not (meaning_claim or symbol_claim):
                return 'the registered TEST requires its exact identity-claim context'
        if record is None:
            record = json.loads(test_contract._read(model.root, RECEIPT))
        if 'semantic_schema' in record:
            return profile_failure(evidence, symbol, model, claim, record=record, origin=origin)
        candidate = record['candidate']
        if type(record['schema']) is not int or record['schema'] != SCHEMA:
            return 'incompatible TEST execution receipt'
        refused = CONTRACT.failure(candidate)
        if refused:
            return refused
        native = record['native_model']
        if (type(native) is not str or len(native) != 64
                or any(char not in '0123456789abcdef' for char in native)
                or candidate['native_model'] != native):
            return 'TEST execution native snapshot lacks independent finalization'
        if digest(encode(candidate['producer_inputs'])) != record['native_inputs']:
            return 'TEST execution source provenance lacks independent finalization'
        if not exact(candidate['context'], context(model, symbol, evidence)):
            return 'TEST execution inputs or model context are stale'
        witness = candidate['witness']
        refused = witness_failure(witness, candidate['context'])
        if refused:
            return refused
        return test_contract.terminal_failure(record, model.root, CONTRACT)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, RecursionError, ImportError):
        return 'missing or invalid qualified TEST execution context'


def profile_failure(evidence, symbol, model, claim, *, record=None, origin=None):
    """Use the complete explicit catalog; no unregistered TEST fallback."""
    try:
        from kb import test_catalog, test_primary
        if record is None:
            record = json.loads(test_contract._read(model.root, RECEIPT))
        primary = test_primary.load(model.root, record['candidate']['primary_records'])
        return test_catalog.prepared(model).failure(evidence, symbol, model, claim, origin,
                                                    record=record, primary=primary)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, IndexError,
            RecursionError, ImportError):
        return 'missing or invalid qualified TEST semantic context'


def publish(path, value):
    """Replace a local output atomically; leave successful records on refusal."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    staged = path.with_name(path.name + '.pending')
    staged.write_text(json_text(value) + '\n', encoding='utf-8')
    staged.replace(path)


def finalize(candidate_path, process_path, stdout_path, stderr_path, root=repo.ROOT):
    from kb import lock
    with lock.held(root):
        record = prepare(candidate_path, process_path, stdout_path, stderr_path, root)
        publish(receipt_path(root), record)
        return record


def prepare(candidate_path, process_path, stdout_path, stderr_path, root=repo.ROOT):
    """Validate a native candidate under the caller's source lock, without publication."""
    candidate = json.loads(Path(candidate_path).read_bytes())
    if 'semantic_schema' in candidate:
        from kb import compile, test_catalog, test_primary
        model = compile.build(root)
        engine = test_catalog.build(model)
        record = test_contract.bind_terminal(candidate, process_path, stdout_path, stderr_path,
                                             root, engine.cohort.contract, candidate_path)
        primary = test_primary.load(root, candidate['primary_records'])
        return engine.prepare(record, model, primary)
    refused = CONTRACT.failure(candidate)
    if refused:
        raise ValueError(refused)
    record = test_contract.bind_terminal(candidate, process_path, stdout_path, stderr_path,
                                         root, CONTRACT, candidate_path)
    from kb import compile
    from kb.model import SymbolKey
    model = compile.build(root)
    symbol = model.symbols[SymbolKey(*SYMBOL)]
    native = model_digest(model)
    if candidate.get('native_model') != native:
        raise ValueError('the producer native snapshot disagrees with independent finalization')
    original_inputs = producer_inputs(root)
    if candidate.get('producer_inputs') != original_inputs:
        raise ValueError('the producer source inputs disagree with independent finalization')
    record.update(schema=SCHEMA, native_model=native,
                  native_inputs=digest(encode(original_inputs)))
    # Validate before publication without replacing an earlier qualified pass.
    refused = failure(item(), symbol, model, 'identity', record=record)
    if refused:
        raise ValueError(refused)
    return record


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('candidate')
    parser.add_argument('--process', required=True)
    parser.add_argument('--stdout', required=True)
    parser.add_argument('--stderr', required=True)
    args = parser.parse_args(argv)
    finalize(args.candidate, args.process, args.stdout, args.stderr)
    print('qualified TEST execution receipt published')


if __name__ == '__main__':
    main()
