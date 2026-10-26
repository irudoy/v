"""Execute redirected ignition lookup consumers against the composed patch image."""

import os
from pathlib import Path

from patches import ignition_literal_consumers as contract
from patches import rom_address_profiles

import verify_map_switching as base
from elf_storage_layout import require_separate_storage


TOOL_DIR = Path(__file__).resolve().parent
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
RETURN_BOUNDARY = bytes.fromhex('57f6472a000b0009')


def declaration(target):
    if target.rom != contract.ROM or target.map_layout.variant != 'sh7059-1me3b':
        raise ValueError('the ignition consumer gate requires the exact 1ME3B target')
    profile = rom_address_profiles.profile_for_rom(target.rom)
    code = target.map_layout.code_region_by_key
    adapter = code['ignition_adapter'].entry
    state_adapter = code['ignition_state_adapter'].entry
    contract.require_hooks(profile, adapter)
    contract.require_state_hooks(profile, state_adapter)
    image = bytes(target.stock_image.data)
    contract.require_consumers(image)
    contract.paired_state_loads(image, contract.STATE_BASES, contract.STATE_LITERALS)
    families = []
    for key in FAMILIES:
        family = target.map_layout.family_by_key[key]
        families.append(dict(canonical=family.canonical_address,
            pointers=family.pointer_table, slots=family.all_slot_addresses))
    by_address = {family['canonical']: index for index, family in enumerate(families)}
    if len(by_address) != len(FAMILIES) or any(len(family['slots']) != 5 for family in families):
        raise ValueError('the ignition consumers need distinct complete slot families')
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
            family=by_address[row.table], overwrites_fifth=int(row.stack_store is not None)))
    return dict(windows=windows, families=families,
        selector=target.map_layout.ram.selector.start,
        code=tuple((row.start, row.end) for row in rows),
        pools=tuple(sorted({value for row in rows for value in
            (row.literal, row.table_pool, row.first_axis_pool, row.second_axis_pool)})))


def render_header(declared):
    rows = ['/* Input bindings for the composed ignition lookup consumers. */',
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


def require_reconstruction(declared, image, directory, source):
    """Independently assemble every executed stock call window and its pools."""
    spans = (*declared['code'], *((at, at + 4) for at in declared['pools']))
    origin = min(start for start, end in spans) & ~3
    stem = directory / 'ignition-consumers'
    base.run_command([base.AS, '--big', '--isa=sh2e', '-o', stem.with_suffix('.o'), source])
    base.run_command([base.LD, '-EB', f'-Ttext={origin:#x}',
        f"--entry={declared['code'][0][0]:#x}", '-o', stem.with_suffix('.elf'), stem.with_suffix('.o')])
    base.run_command([base.OBJCOPY, '-O', 'binary', '--only-section=.text',
                      stem.with_suffix('.elf'), stem.with_suffix('.raw')])
    raw = stem.with_suffix('.raw').read_bytes()
    for start, end in spans:
        if start < origin or end > len(image) or raw[start - origin:end - origin] != image[start:end]:
            raise ValueError(f'ignition consumer reconstruction differs at {start:#x}..{end:#x}')


def assemble_callee(source, address, directory):
    stem = directory / f'callee-{address:08x}'
    base.run_command([base.AS, '--big', '--isa=sh2e',
        '--defsym', f'STOCK_LOOKUP_ENTRY={address}', '-o', stem.with_suffix('.o'), source])
    base.run_command([base.LD, '-EB', f'-Ttext={address:#x}',
        '--entry=ignition_consumer_callee', '-o', stem.with_suffix('.elf'), stem.with_suffix('.o')])
    base.run_command([base.OBJCOPY, '-O', 'binary', '--only-section=.text',
                      stem.with_suffix('.elf'), stem.with_suffix('.raw')])
    return stem.with_suffix('.raw').read_bytes()


def prepare_fixture(declared, image, baseline, callee_stubs):
    fixture = bytearray(baseline)
    code = declared['code']
    pools = tuple((at, at + 4) for at in declared['pools'])
    for window in declared['windows']:
        start, end = window['end'], window['end'] + len(RETURN_BOUNDARY)
        if end > len(fixture) or any(start < right and left < end for left, right in (*code, *pools)):
            raise ValueError('an ignition return boundary overlaps instructions or operands under test')
        fixture[start:end] = RETURN_BOUNDARY
    for address, data in callee_stubs.items():
        end = address + len(data)
        if address < 0 or end > len(fixture) or any(
                address < right and left < end for left, right in (*code, *pools)):
            raise ValueError('an unchanged lookup stub overlaps instructions or operands under test')
        fixture[address:end] = data
    for start, end in code:
        if fixture[start:end] != image[start:end]:
            raise ValueError('the ignition fixture changes a consumer instruction under test')
    for window in declared['windows']:
        at = window['literal']
        if fixture[at:at + 4] != window['adapter'].to_bytes(4, 'big'):
            raise ValueError('the ignition consumer does not use its actual composed adapter literal')
    return bytes(fixture)


def execution_timeout():
    name = 'VQ_SH_ELF_STOCK_TIMEOUT_SECONDS'
    value = os.environ.get(name, '120')
    if value not in ('120', '240'):
        raise ValueError(f'{name} must be 120 or 240')
    return int(value)


def verify(target, baseline_fixture, directory):
    """Run all declared consumers with their independent C state assertions."""
    directory = Path(directory) / 'ignition-literal-consumers'
    directory.mkdir()
    private = directory / 'consumed'
    private.mkdir()
    declared = declaration(target)
    image = bytes(target.stock_image.data)
    consumed = {name: (TOOL_DIR / name).read_bytes() for name in SOURCES}
    consumed[HEADER] = render_header(declared).encode()
    for name, data in consumed.items():
        (private / name).write_bytes(data)
    require_reconstruction(declared, image, directory, private / SOURCES[1])
    stubs = {address: assemble_callee(private / SOURCES[3], address, directory)
             for address in (contract.STATE_LOOKUP, contract.LOOKUP)}
    fixture = prepare_fixture(declared, image, baseline_fixture, stubs)
    observer = directory / 'invoke.o'
    base.run_command([base.AS, '--big', '--isa=sh2e', '-o', observer, private / SOURCES[2]])
    fixture_path, rom_object = directory / 'fixture.bin', directory / 'fixture.o'
    fixture_path.write_bytes(fixture)
    base.run_command([base.OBJCOPY, '-I', 'binary', '-O', 'elf32-sh', '-B', 'sh',
        '--rename-section', '.data=.rom,alloc,load,code,data,contents', fixture_path, rom_object])
    elf = directory / 'harness.elf'
    base.run_command([base.GCC, '-m2e', '-mb', '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
        '-DVQ_PATCH_GATE=1', '-I', private,
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE, len(fixture) + 0x10000):#x}',
        '-Wl,--section-start=.rom=0', '-o', elf, private / SOURCES[0], observer, rom_object], timeout=120)
    require_separate_storage(elf, ((0x01000000, 0x20000),))
    executable = elf.read_bytes()
    result = base.run_command([base.RUN, '--memory-region=0x01000000,128k', elf], timeout=execution_timeout())
    if elf.read_bytes() != executable or fixture_path.read_bytes() != fixture:
        raise ValueError('the ignition consumer ELF or fixture changes during execution')
    for name, data in consumed.items():
        if (private / name).read_bytes() != data or name != HEADER and (TOOL_DIR / name).read_bytes() != data:
            raise ValueError('an ignition consumer source changes during execution')
    count = len(declared['windows']) * len(SELECTORS) * len(INPUTS)
    marker = f"VQ_SH_ELF_IGNITION_LITERAL_CONSUMERS status=PASS cases={count} windows={len(declared['windows'])}"
    if result.stdout.splitlines() != [marker]:
        raise ValueError('the ignition consumer gate lacks its unique complete terminal marker')
    return marker
