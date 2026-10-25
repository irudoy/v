"""Independent physical and complete-state admission of C5 in the shared primary.

This module consumes the existing COPY record and its original full GNU
terminal. It publishes no separate receipt and establishes no reachability,
interpolation arithmetic, arbitrary-computed-consumer or hardware claim.
"""

from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import re
import tomllib

from kb import copy_evidence, ignition_literal_equations as equations, test_contract
from kb.test_stock_capture import tool

REGION = '1me3b-ignition-literal-consumers'
PREFIX = 'kb-ignition-literal-observation '
SOURCES = ('harness-ignition-consumers.c', 'stock_1me3b_ignition_consumers.s',
           'stock_ignition_consumer_invoke.s', 'ignition_consumer_callee.s')
HEADER = 'ignition-consumer-cases.h'
FAMILIES = ('ignition_surface_hot', 'ignition_surface_cold', 'ignition_surface_state_3',
            'ignition_surface_state_4', 'ignition_surface_state_5', 'ignition_surface_state_6_7')
BOUNDARY = bytes.fromhex('57f6472a000b0009')


def sha(value):
    return hashlib.sha256(value).hexdigest()


def require_hash(value):
    if type(value) is not str or re.fullmatch('[0-9a-f]{64}', value) is None:
        raise ValueError('the C5 packet lacks an exact original artifact identity')
    return value


def same(actual, expected, reason):
    if not test_contract.exact(actual, expected):
        raise ValueError(reason)


def execution_inputs(root):
    """Current physical execution sources, independent of publication metadata.

    The original prepare binds every raw native input. Reuse additionally
    binds current native runtime values through the exact declaration, full
    composition and prepared-fixture reconstruction below. A review inventory
    is not an instruction, ABI value or calibration input. No caller-provided
    exclusion list or alternate model digest participates in this boundary.
    """
    root = Path(root).resolve()
    paths = set(copy_evidence.EXECUTION_FILES) | {
        'rom-images/roms.csv', 'rom-images/homology.toml',
        'defs/rom-identities.toml', 'defs/rom-inheritance.toml',
    }
    for directory, suffixes in (
        (root / 'tools/sh-elf-run', {'.py', '.c', '.s', '.h', '.sh'}),
        (root / 'patches', {'.py', '.s', '.h', '.toml', '.json'}),
        (root / 'tools', {'.py'}),
    ):
        paths.update(path.relative_to(root).as_posix() for path in directory.rglob('*')
                     if path.is_file() and path.suffix in suffixes
                     and 'tests' not in path.relative_to(directory).parts)
    return {path:sha((root / path).read_bytes()) for path in sorted(paths)}


def require_execution_inputs(original, current):
    """Require each declared executable input in the complete original map."""
    if type(original) is not dict or type(current) is not dict:
        raise ValueError('the C5 original physical source provenance is absent')
    for path, identity in current.items():
        if original.get(path) != identity:
            raise ValueError('the C5 original executable source or physical input is stale')
    # A removed producer source cannot disappear from a glob silently.
    for path in original.keys() - current.keys():
        file = Path(path)
        if (file.parts and file.parts[0] in ('tools', 'patches')
                and (file.suffix in {'.py', '.c', '.s', '.h', '.sh'}
                     or file.parts[0] == 'patches' and file.suffix in {'.toml', '.json'})
                and 'tests' not in file.parts):
            raise ValueError('the C5 original executable source closure loses a consumed file')


def current_profile(model):
    """Render the supplied native model; a process-local cached profile is insufficient."""
    from kb.adapters import profiles
    from patches import rom_address_profiles
    document = tomllib.loads(profiles.render_registries(model)[profiles.PROFILES.as_posix()])
    return rom_address_profiles.parse_registry(document, 'current native profile projection')['1ME3B']


def declaration(model, target):
    """Rebind the bounded declaration to current native owners and stock bytes."""
    from patches import ignition_literal_consumers as contract, rom_address_profiles
    from kb import targets as kb_targets
    if target.rom != '1ME3B' or target.map_layout.variant != 'sh7059-1me3b':
        raise ValueError('the independent C5 consumer requires exact 1ME3B bindings')
    profile = current_profile(model)
    same(asdict(rom_address_profiles.profile_for_rom('1ME3B')), asdict(profile),
         'the C5 cached execution profile differs from the current native model')
    layout = target.map_layout
    adapter = layout.code_region_by_key['ignition_adapter'].entry
    state_adapter = layout.code_region_by_key['ignition_state_adapter'].entry
    contract.require_hooks(profile, adapter)
    contract.require_state_hooks(profile, state_adapter)
    image = bytes(target.stock_image.data)
    contract.require_consumers(image)
    paired = contract.paired_state_loads(image, contract.STATE_BASES, contract.STATE_LITERALS)
    families = []
    for key in FAMILIES:
        family = layout.family_by_key[key]
        families.append(dict(key=key, canonical=family.canonical_address,
                             pointers=family.pointer_table, slots=list(family.all_slot_addresses)))
    owners = {family['canonical']: index for index, family in enumerate(families)}
    if len(owners) != 6 or any(len(row['slots']) != 5 for row in families):
        raise ValueError('the C5 native binding lacks six distinct five-slot families')
    windows = []
    for row in sorted((*contract.CONSUMERS, *contract.STATE_REGION_CONSUMERS), key=lambda row: row.start):
        state = row.literal == 0x79404
        windows.append(dict(entry=row.start, load=row.load, call=row.call, end=row.end,
            literal=row.literal, table=row.table, axis6=0x13DC6 if state else 0x13716,
            axis5=0x13DCE if state else 0x13726, stock=0x293D8 if state else 0x29BA8,
            adapter=state_adapter if state else adapter, target_register=row.register,
            family=owners[row.table], overwrites_fifth=int(row.stack_store is not None),
            operands=asdict(row)))
    return dict(schema=1, kind=REGION, rom='1ME3B', windows=windows, families=families,
        native_execution=dict(profile=json.loads(json.dumps(asdict(profile))),
            canonical_symbols={feature:kb_targets.canonical_symbols(feature,
                root=model.root, overlay=model.overlay)
                for feature in ('runtime', 'map_switching', 'rolling_launch', 'can_telemetry')}),
        selector=layout.ram.selector.start, selectors=list(equations.SELECTORS),
        inputs=[list(row) for row in equations.INPUTS], paired_state_loads=[list(row) for row in paired],
        call_observation=dict(address=0x01010000, words=24), context_size=80, observation_size=572,
        boundary=dict(bytes=BOUNDARY.hex(), scratch_register=7, return_stack_offset=24),
        reachability_proven=False, computed_consumer_absence_proven=False, semantic_admission=False)


def header(declared):
    """Reconstruct the exact private C binding independently of the producer."""
    lines = ['/* Exact 1ME3B input bindings consumed by the C5 driver. */',
             f"#define C5_SELECTOR_ADDRESS 0x{declared['selector']:08x}U",
             'static const struct c5_family c5_families[] = {']
    for family in declared['families']:
        values = ','.join(f'0x{value:08x}U' for value in family['slots'])
        lines.append(f"    {{0x{family['canonical']:08x}U,0x{family['pointers']:08x}U,{{{values}}}}},")
    lines.extend(('};', 'static const struct c5_window c5_windows[] = {'))
    fields = ('entry', 'load', 'call', 'literal', 'table', 'axis6', 'axis5',
              'stock', 'adapter', 'target_register', 'family', 'overwrites_fifth')
    for window in declared['windows']:
        lines.append('    {' + ','.join(f'0x{window[key]:x}U' for key in fields) + '},')
    lines.extend(('};', ''))
    return '\n'.join(lines).encode()


def callee_stub(entry):
    """Encode the small observing stub independently of its GNU source.

    Registers and special state are pushed before scratch use; PC-relative
    operands and the loop displacement are fixed by this complete sequence.
    The GNU output must equal these bytes before fixture admission.
    """
    if entry not in (0x293D8, 0x29BA8):
        raise ValueError('the C5 callee observer replaces another stock entry')
    words = [0x2F06 | register << 4 for register in range(15)]
    words.extend((0x4F13, 0x4F02, 0x4F12, 0x4F22, 0x4F03,
                  0x61F3, 0xD215, 0xE014, 0x6316, 0x2232, 0x7204, 0x4010, 0x8BFA,
                  0x60F3, 0x7050, 0x2202, 0x7204, 0x6002, 0x2202, 0x7204,
                  0x6022, 0x7001, 0x2202, 0x7204, 0xD00D, 0x2202,
                  0x4F07, 0x4F26, 0x4F16, 0x4F06, 0x4F17))
    words.extend(0x60F6 | register << 8 for register in range(14, -1, -1))
    words.extend((0xD003, 0x000B, 0x0009))
    return (b''.join(word.to_bytes(2, 'big') for word in words)
            + (0x01010000).to_bytes(4, 'big') + entry.to_bytes(4, 'big')
            + (0xA1B2C3D4).to_bytes(4, 'big'))


def _objects(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('the actual C5 output repeats a JSON key')
        result[key] = value
    return result


def observations(stdout, declared):
    if type(stdout) is not str:
        raise ValueError('the C5 original stdout is absent')
    actual = [json.loads(line[len(PREFIX):], object_pairs_hook=_objects)
              for line in stdout.splitlines() if line.startswith(PREFIX)]
    count = len(declared['windows']) * len(equations.SELECTORS) * len(equations.INPUTS)
    marker = f"VQ_SH_ELF_IGNITION_LITERAL_CONSUMERS status=PASS cases={count} windows={len(declared['windows'])}"
    if stdout.splitlines().count(marker) != 1:
        raise ValueError('the C5 original lacks its unique complete invocation marker')
    return actual, marker


def require_witness(model, packet, producer_inputs):
    """Validate physical bindings and independent equations; terminal is separate."""
    required = {'schema', 'kind', 'declaration', 'semantic_admission', 'consumed',
                'stock_sha256', 'composition_sha256', 'baseline_fixture_sha256', 'fixture_sha256',
                'elf_sha256', 'observer_object_sha256', 'map_blobs', 'reconstruction', 'boundaries',
                'stubs', 'stdout', 'stderr', 'stdout_sha256', 'stderr_sha256', 'observations',
                'command', 'marker', 'simulator', 'toolchain'}
    if type(packet) is not dict or set(packet) != required:
        raise ValueError('the C5 original physical packet has another schema')
    same((packet['schema'], packet['kind'], packet['semantic_admission']), (1, REGION, False),
         'the C5 raw packet changes its exact scope or grants its own admission')
    root = Path(model.root).resolve()
    runtime = tool(root, 'verify_runtime_targets.py', '_kb_c5_runtime_verifier')
    if runtime.ROOT.resolve() != root:
        raise ValueError('the C5 runtime source belongs to another checkout')
    target = runtime.runtime_targets.load_runtime_target('1ME3B')
    declared = declaration(model, target)
    same(packet['declaration'], declared, 'the C5 declaration differs from current native owners or exact stock operands')
    consumed = packet['consumed']
    if type(consumed) is not dict or set(consumed) != {*SOURCES, HEADER}:
        raise ValueError('the C5 physical packet omits a private consumed source')
    for name in SOURCES:
        path = 'tools/sh-elf-run/' + name
        source = (root / path).read_bytes()
        if (consumed[name] != source.hex() or producer_inputs.get(path) != sha(source)):
            raise ValueError('the C5 physical packet consumes another executable source snapshot')
    if consumed[HEADER] != header(declared).hex():
        raise ValueError('the C5 private header changes its exact family, window or input bindings')
    for name in ('ignition_literal_capture.py', 'verify_runtime_targets.py'):
        path = 'tools/sh-elf-run/' + name
        if producer_inputs.get(path) != sha((root / path).read_bytes()):
            raise ValueError('the C5 physical packet has stale producer preparation sources')
    image = bytes(target.stock_image.data)
    if packet['stock_sha256'] != sha(image):
        raise ValueError('the C5 packet uses another stock image')
    maps = target.map_payloads
    same(packet['map_blobs'], {key: data.hex() for key, data in maps.items()},
         'the C5 capture changes the exact independently assembled target payloads')
    locks = runtime.runtime_targets.load_payload_locks()['1ME3B']
    _, _, composition = runtime._compose_and_lock(target, locks, maps,
        target.rolling_payloads if target.rolling_layout is not None else {}, target.telemetry_payloads)
    map_parsed = runtime.map_switching_assembly.validate_assembly_sources(target.map_layout)
    rolling_parsed = (runtime.rolling_launch_assembly.validate_assembly_sources(target.rolling_layout)
                      if target.rolling_layout is not None else None)
    can_parsed = runtime.can_telemetry_assembly.validate_assembly_sources(target.telemetry_layout)
    baseline = runtime._build_dynamic_fixture(target, composition, map_parsed, rolling_parsed, can_parsed)[0]
    if packet['composition_sha256'] != composition.sha256 or packet['baseline_fixture_sha256'] != sha(baseline):
        raise ValueError('the C5 packet replaces its complete composed runtime or baseline fixture')
    windows = declared['windows']
    spans = [(row['entry'], row['end']) for row in windows]
    pools = sorted({value for row in windows for value in (
        row['literal'], row['operands']['table_pool'], row['operands']['first_axis_pool'],
        row['operands']['second_axis_pool'])})
    reconstructed = dict(code=[dict(start=start, end=end, stock=image[start:end].hex(),
                                    reconstructed=image[start:end].hex()) for start, end in spans],
        pools=[dict(address=address, stock=image[address:address + 4].hex(),
                    reconstructed=image[address:address + 4].hex()) for address in pools])
    same(packet['reconstruction'], reconstructed, 'the C5 GNU reconstruction changes stock instructions or pool words')
    expected_boundaries = [dict(address=row['end'], bytes=BOUNDARY.hex()) for row in windows]
    expected_stubs = [dict(address=address, bytes=callee_stub(address).hex()) for address in (0x293D8, 0x29BA8)]
    same(packet['boundaries'], expected_boundaries, 'the C5 observation boundary changes its PR restoration or scratch register')
    same(packet['stubs'], expected_stubs, 'the C5 GNU callee observer differs from its independent instruction reconstruction')
    fixture = bytearray(baseline)
    for row in expected_boundaries + expected_stubs:
        start, data = row['address'], bytes.fromhex(row['bytes'])
        if (any(start < end and begin < start + len(data) for begin, end in spans)
                or any(start < address + 4 and address < start + len(data) for address in pools)):
            raise ValueError('the C5 simulator transform intersects stock bytes under test')
        fixture[start:start + len(data)] = data
    for start, end in spans:
        if fixture[start:end] != image[start:end]:
            raise ValueError('the C5 fixture changes a stock instruction under test')
    for row in windows:
        if fixture[row['literal']:row['literal'] + 4] != row['adapter'].to_bytes(4, 'big'):
            raise ValueError('the C5 fixture changes an actual composed lookup pointer')
    if packet['fixture_sha256'] != sha(fixture):
        raise ValueError('the C5 fixture changes an undeclared byte')
    for field in ('elf_sha256', 'observer_object_sha256'):
        require_hash(packet[field])
    for stream in ('stdout', 'stderr'):
        if type(packet[stream]) is not str or packet[stream + '_sha256'] != sha(packet[stream].encode()):
            raise ValueError('the C5 actual simulator stream changes')
    actual, marker = observations(packet['stdout'], declared)
    same(packet['observations'], actual, 'the C5 observations differ from the actual original simulator output')
    same(packet['marker'], marker, 'the C5 packet changes its actual complete invocation marker')
    simulator = packet['simulator']
    if (type(simulator) is not dict or set(simulator) != {'returncode', 'command'}
            or type(simulator['returncode']) is not int or simulator['returncode'] != 0
            or type(simulator['command']) is not list or len(simulator['command']) != 3
            or simulator['command'][:2] != [runtime.base_verifier.RUN, '--memory-region=0x01000000,128k']):
        raise ValueError('the C5 simulator has another command or an unsuccessful terminal')
    elf = Path(simulator['command'][2])
    if elf.name != 'harness.elf' or elf.parent.name != 'ignition-literal-consumers':
        raise ValueError('the C5 actual simulator executes another harness')
    private = elf.parent / 'consumed'
    command = [runtime.base_verifier.GCC, '-m2e', '-mb', '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
        '-I', str(private), f'-Wl,-Ttext-segment={max(runtime.base_verifier.DRIVER_TEXT_BASE, len(fixture) + 0x10000):#x}',
        '-Wl,--section-start=.rom=0', '-o', str(elf), str(private / SOURCES[0]),
        str(elf.parent / 'invoke.o'), str(elf.parent / 'fixture.o')]
    same(packet['command'], command, 'the C5 packet changes its actual source/observer/fixture compile command')
    toolchain = packet['toolchain']
    if (type(toolchain) is not dict or set(toolchain) != {'simulator_version', 'gcc_version', 'binaries'}
            or toolchain['simulator_version'] != '16.3' or toolchain['gcc_version'] != '13.3.0'
            or type(toolchain['binaries']) is not dict
            or set(toolchain['binaries']) != {'as', 'ld', 'objcopy', 'gcc', 'run'}):
        raise ValueError('the C5 capture lacks its exact pinned GNU toolchain')
    for identity in toolchain['binaries'].values():
        require_hash(identity)
    result = equations.require_observations(declared, actual)
    return dict(region=REGION, stock_sha256=sha(image), fixture_sha256=sha(fixture),
                elf_sha256=packet['elf_sha256'], observations=len(result['observations']),
                stdout_sha256=packet['stdout_sha256'], scope=result['scope'],
                reachability_proven=False, computed_consumer_absence_proven=False,
                stock_interpolation_body_executed=False, hardware_qualification=False)


def require_original(model, record):
    """Revalidate the shared original and current execution-source closure."""
    from kb.model import SymbolKey
    root = Path(model.root).resolve()
    symbol = model.symbols.get(SymbolKey('7mfk', 'ram', copy_evidence.MEMBERS['reader'][1]))
    failure = copy_evidence.failure(copy_evidence.item('reader'), symbol, model, 'identity', record=record)
    if failure:
        raise ValueError(failure)
    candidate = record['candidate']
    if candidate['complete'] is not True or candidate['mode'] != 'full':
        raise ValueError('the C5 witness requires the complete original shared primary')
    copy_evidence.terminal_check(record['terminal'])
    process = copy_evidence.read_output(root, record['process_path'])
    if sha(process) != record['process_sha256']:
        raise ValueError('the C5 original process receipt changes')
    original = json.loads(process)
    for key, value in original.items():
        if key not in ('stdout', 'stderr'):
            same(record['terminal'].get(key), value, 'the C5 original terminal disagrees with its receipt')
    streams = {}
    for stream in ('stdout', 'stderr'):
        data = copy_evidence.read_output(root, record['terminal'][stream])
        if sha(data) != record['terminal'][stream + '_sha256']:
            raise ValueError('the C5 original shared stream changes')
        streams[stream] = data
    if (record.get('native_model') != candidate.get('native_model')
            or record.get('native_inputs') != copy_evidence.digest(candidate['producer_inputs'])):
        raise ValueError('the C5 original lacks its independently finalized complete native provenance')
    current = execution_inputs(root)
    require_execution_inputs(candidate['producer_inputs'], current)
    lines = streams['stdout'].decode().splitlines()
    packets = [line[len(copy_evidence.MARKER):] for line in lines if line.startswith(copy_evidence.MARKER)]
    if packets != [test_contract.json_text(candidate)]:
        raise ValueError('the C5 witness differs from its unique original complete primary packet')
    if sum(line.startswith('VQ_SH_ELF_VERIFY status=PASS ') for line in lines) != 1:
        raise ValueError('the shared original lacks its unique complete pipeline success marker')
    return lines, current


def require_primary(model, record):
    """Bind the C5 witness to the exact complete existing primary and sources."""
    lines, current = require_original(model, record)
    root = Path(model.root).resolve()
    candidate = record['candidate']
    packet = candidate['witness'].get('ignition_literals')
    result = require_witness(model, packet, candidate['producer_inputs'])
    if (lines.count(packet['marker']) != 1
            or sum(line.startswith('VQ_SH_ELF_VERIFY status=PASS ') for line in lines) != 1):
        raise ValueError('the C5 original shared primary lacks complete unique success markers')
    same(execution_inputs(root), current, 'the C5 execution inputs change during consumption')
    return result
