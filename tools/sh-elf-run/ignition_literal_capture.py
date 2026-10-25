"""C5 raw call-window capture inside the complete relocated-target producer.

The stock interpolation body is a simulator-only observation stub. This
capture establishes neither routine reachability nor hardware qualification.
Independent admission consumes the original primary terminal and these raw
observations, source snapshots, stock reconstruction and fixture identities.
"""

from dataclasses import asdict
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

from patches import ignition_literal_consumers as contract
from kb import targets as kb_targets

TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parents[1]
REGION = '1me3b-ignition-literal-consumers'
PREFIX = 'kb-ignition-literal-observation '
HEADER = 'ignition-consumer-cases.h'
SOURCES = (
    'harness-ignition-consumers.c', 'stock_1me3b_ignition_consumers.s',
    'stock_ignition_consumer_invoke.s', 'ignition_consumer_callee.s',
)
SELECTORS = (0, 1, 2, 3, 4, 5, 255)
INPUTS = (
    (0x00000000, 0x00000000, 0x000000FF, 0x000),
    (0x000000FF, 0x0000FFFF, 0x00000000, 0x001),
    (0x12345680, 0xFFFF8000, 0x0000007F, 0x0F0),
    (0xFFFFFF7F, 0xFFFF0001, 0x00000080, 0x0F1),
    (0x89ABCDEF, 0x80000000, 0x12345678, 0x300),
    (0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0x3F1),
)
FAMILIES = ('ignition_surface_hot', 'ignition_surface_cold',
            'ignition_surface_state_3', 'ignition_surface_state_4',
            'ignition_surface_state_5', 'ignition_surface_state_6_7')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def declaration(target):
    from patches import rom_address_profiles
    if target.rom != contract.ROM or target.map_layout.variant != 'sh7059-1me3b':
        raise ValueError('the C5 capture requires the exact 1ME3B target')
    profile = rom_address_profiles.profile_for_rom(target.rom)
    code = target.map_layout.code_region_by_key
    adapter = code['ignition_adapter'].entry
    state_adapter = code['ignition_state_adapter'].entry
    contract.require_hooks(profile, adapter)
    contract.require_state_hooks(profile, state_adapter)
    image = bytes(target.stock_image.data)
    contract.require_consumers(image)
    state_loads = contract.paired_state_loads(image, contract.STATE_BASES, contract.STATE_LITERALS)
    families = []
    for key in FAMILIES:
        family = target.map_layout.family_by_key[key]
        families.append(dict(key=key, canonical=family.canonical_address,
                             pointers=family.pointer_table, slots=list(family.all_slot_addresses)))
    by_address = {family['canonical']: index for index, family in enumerate(families)}
    if len(by_address) != len(FAMILIES) or any(len(family['slots']) != 5 for family in families):
        raise ValueError('the C5 capture requires six distinct five-slot family bindings')
    windows = []
    rows = sorted((*contract.CONSUMERS, *contract.STATE_REGION_CONSUMERS), key=lambda row: row.start)
    for row in rows:
        state = row.literal == 0x79404
        windows.append(dict(entry=row.start, load=row.load, call=row.call, end=row.end,
            literal=row.literal, table=row.table,
            axis6=0x13DC6 if state else contract.FIRST_AXIS,
            axis5=0x13DCE if state else contract.SECOND_AXIS,
            stock=contract.STATE_LOOKUP if state else contract.LOOKUP,
            adapter=state_adapter if state else adapter, target_register=row.register,
            family=by_address[row.table], overwrites_fifth=int(row.stack_store is not None),
            operands=asdict(row)))
    return dict(schema=1, kind=REGION, rom=target.rom, windows=windows, families=families,
                native_execution=dict(profile=json.loads(json.dumps(asdict(profile))),
                    canonical_symbols={feature:kb_targets.canonical_symbols(feature)
                        for feature in ('runtime', 'map_switching', 'rolling_launch', 'can_telemetry')}),
                selector=target.map_layout.ram.selector.start,
                selectors=list(SELECTORS), inputs=[list(row) for row in INPUTS],
                paired_state_loads=[list(row) for row in state_loads],
                call_observation=dict(address=0x01010000, words=24),
                context_size=80, observation_size=572,
                boundary=dict(bytes='57f6472a000b0009', scratch_register=7, return_stack_offset=24),
                reachability_proven=False, computed_consumer_absence_proven=False,
                semantic_admission=False)


def render_header(declared):
    rows = ['/* Exact 1ME3B input bindings consumed by the C5 driver. */',
            f"#define C5_SELECTOR_ADDRESS 0x{declared['selector']:08x}U",
            'static const struct c5_family c5_families[] = {']
    for family in declared['families']:
        slots = ','.join(f'0x{value:08x}U' for value in family['slots'])
        rows.append(f"    {{0x{family['canonical']:08x}U,0x{family['pointers']:08x}U,{{{slots}}}}},")
    rows.extend(('};', 'static const struct c5_window c5_windows[] = {'))
    fields = ('entry', 'load', 'call', 'literal', 'table', 'axis6', 'axis5',
              'stock', 'adapter', 'target_register', 'family', 'overwrites_fifth')
    for window in declared['windows']:
        rows.append('    {' + ','.join(f'0x{window[key]:x}U' for key in fields) + '},')
    rows.extend(('};', ''))
    return '\n'.join(rows)


def region(declared, region_type):
    rows = sorted((*contract.CONSUMERS, *contract.STATE_REGION_CONSUMERS), key=lambda row: row.start)
    pools = sorted({value for row in rows for value in
                    (row.literal, row.table_pool, row.first_axis_pool, row.second_axis_pool)})
    return region_type(key=REGION, rom='1ME3B', source=SOURCES[1], harness=SOURCES[0],
        start=rows[0].start, end=rows[0].end,
        pools=tuple((address, 4) for address in pools), ram_literals=(),
        cases=len(declared['windows']) * len(SELECTORS) * len(INPUTS),
        boundary=True, return_address_offset=24, return_register=7,
        callees=tuple((row.start, row.end) for row in rows[1:]))


def _objects(pairs):
    found = {}
    for key, value in pairs:
        if key in found:
            raise ValueError('the C5 original output repeats a JSON key')
        found[key] = value
    return found


def observe(stdout, declared):
    """Preserve actual source-order pairs; this parser grants no semantic fact."""
    observed = [json.loads(line[len(PREFIX):], object_pairs_hook=_objects)
                for line in stdout.splitlines() if line.startswith(PREFIX)]
    expected = [(window, selector, variant) for window in range(len(declared['windows']))
                for selector in SELECTORS for variant in range(len(INPUTS))]
    if len(observed) != len(expected):
        raise ValueError('the C5 original omits or duplicates a declared invocation')
    for index, (packet, (window, selector, variant)) in enumerate(zip(observed, expected)):
        if any(type(packet.get(key)) is not int or packet[key] != value for key, value in
               dict(schema=1, index=index, window=window, selector=selector, variant=variant).items()):
            raise ValueError('the C5 original changes its exact invocation identity or order')
    marker = (f'VQ_SH_ELF_IGNITION_LITERAL_CONSUMERS status=PASS cases={len(expected)} '
              f"windows={len(declared['windows'])}")
    if stdout.splitlines().count(marker) != 1:
        raise ValueError('the C5 original lacks its unique complete marker')
    return observed, marker


def _assemble_stub(base, source, address, directory):
    stem = directory / f'callee-{address:08x}'
    base.run_command([base.AS, '--big', '--isa=sh2e',
        '--defsym', f'STOCK_LOOKUP_ENTRY={address}', '-o', stem.with_suffix('.o'), source])
    base.run_command([base.LD, '-EB', f'-Ttext={address:#x}',
        '--entry=ignition_consumer_callee', '-o', stem.with_suffix('.elf'), stem.with_suffix('.o')])
    base.run_command([base.OBJCOPY, '-O', 'binary', stem.with_suffix('.elf'), stem.with_suffix('.raw')])
    return stem.with_suffix('.raw').read_bytes()


def run(target, baseline_fixture, composition, map_blobs, directory, capture):
    """Execute within the original full primary; never a separate admission run."""
    import verify_map_switching as base
    import verify_stock_code as stock
    from elf_storage_layout import require_separate_storage
    directory = Path(directory) / 'ignition-literal-consumers'
    directory.mkdir()
    declared = declaration(target)
    selected = region(declared, stock.Region)
    private = directory / 'consumed'
    private.mkdir()
    consumed = {name: (TOOL_DIR / name).read_bytes() for name in SOURCES}
    consumed[HEADER] = render_header(declared).encode()
    for name, data in consumed.items():
        (private / name).write_bytes(data)
    reconstructed = {}
    stock.require_reconstruction(selected, bytes(target.stock_image.data), directory,
        source_path=private / SOURCES[1], captured=reconstructed)
    fixture = bytearray(baseline_fixture)
    boundaries = []
    for window in declared['windows']:
        end = window['end']
        boundary = stock.return_stub(SimpleNamespace(key=REGION, return_address_offset=24, return_register=7))
        if (boundary.hex() != declared['boundary']['bytes']
                or any(end < finish and start < end + len(boundary) for start, finish in selected.code_spans)
                or any(end < address + size and address < end + len(boundary) for address, size in selected.pools)):
            raise ValueError('a C5 observation boundary overlaps declared instruction or pool bytes')
        fixture[end:end + len(boundary)] = boundary
        boundaries.append(dict(address=end, bytes=boundary.hex()))
    stubs = []
    for address in (contract.STATE_LOOKUP, contract.LOOKUP):
        data = _assemble_stub(base, private / SOURCES[3], address, directory)
        if any(address < end and start < address + len(data) for start, end in selected.code_spans):
            raise ValueError('a C5 unchanged-stock stub overlaps instruction bytes under test')
        fixture[address:address + len(data)] = data
        stubs.append(dict(address=address, bytes=data.hex()))
    for start, end in selected.code_spans:
        if fixture[start:end] != bytes(target.stock_image.data)[start:end]:
            raise ValueError('the C5 fixture changes an instruction byte under test')
    for window in declared['windows']:
        at = window['literal']
        if fixture[at:at + 4] != window['adapter'].to_bytes(4, 'big'):
            raise ValueError('the C5 fixture does not use its actual composed lookup hook')
    observer = directory / 'invoke.o'
    base.run_command([base.AS, '--big', '--isa=sh2e', '-o', observer, private / SOURCES[2]])
    fixture_path, rom_object = directory / 'fixture.bin', directory / 'fixture.o'
    fixture_path.write_bytes(fixture)
    base.run_command([base.OBJCOPY, '-I', 'binary', '-O', 'elf32-sh', '-B', 'sh',
        '--rename-section', '.data=.rom,alloc,load,code,data,contents', fixture_path, rom_object])
    elf = directory / 'harness.elf'
    command = [base.GCC, '-m2e', '-mb', '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
        '-I', private, f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE, len(fixture) + 0x10000):#x}',
        '-Wl,--section-start=.rom=0', '-o', elf, private / SOURCES[0], observer, rom_object]
    base.run_command(command, timeout=120)
    require_separate_storage(elf, ((0x01000000, 0x20000),))
    executable = elf.read_bytes()
    result = base.run_command([base.RUN, '--memory-region=0x01000000,128k', elf],
                              timeout=stock.stock_execution_timeout())
    if elf.read_bytes() != executable or fixture_path.read_bytes() != fixture:
        raise ValueError('the actual C5 ELF or fixture changes during execution')
    for name in SOURCES:
        if (TOOL_DIR / name).read_bytes() != consumed[name] or (private / name).read_bytes() != consumed[name]:
            raise ValueError('the C5 execution source differs from its consumed snapshot')
    observations, marker = observe(result.stdout, declared)
    capture.update(schema=1, kind=REGION, declaration=declared, semantic_admission=False,
        consumed={name: data.hex() for name, data in consumed.items()},
        stock_sha256=sha(bytes(target.stock_image.data)), composition_sha256=composition.sha256,
        baseline_fixture_sha256=sha(baseline_fixture), fixture_sha256=sha(fixture),
        elf_sha256=sha(executable), observer_object_sha256=sha(observer.read_bytes()),
        map_blobs={key: data.hex() for key, data in map_blobs.items()},
        reconstruction=reconstructed, boundaries=boundaries, stubs=stubs,
        stdout=result.stdout, stderr=result.stderr, stdout_sha256=sha(result.stdout.encode()),
        stderr_sha256=sha(result.stderr.encode()), observations=observations,
        command=[str(part) for part in command], marker=marker,
        simulator=dict(returncode=result.returncode,
            command=[base.RUN, '--memory-region=0x01000000,128k', str(elf)]),
        toolchain=stock.can_latch_copy.toolchain())
    return marker
