"""Raw packed-field observations inside the original full runtime primary."""

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

from kb import packed_transfer_evidence as contract, packed_transfer_matrix as matrix

TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parents[1]
ROMS = {'1ME3B': '1me3b', '1ND0A': '1nd', 'JK78C': 'jk78c'}
HEADER = 'packed-transfer-cases.h'
HARNESS = 'harness-packed-transfers.c'
OBSERVER = 'stock_oneshot_invoke.s'
PREFIX = 'kb-packed-field-observation '


def sha(data):
    return hashlib.sha256(data).hexdigest()


def declaration(target):
    if target.rom not in ROMS:
        raise ValueError('the packed capture requires an exact canonical width-question image')
    layout = ROMS[target.rom]
    source = contract.descriptor(ROOT)
    windows = [row for row in source['window'] if row['layout'] == layout]
    fields = [row for row in source['field'] if row['layout'] == layout]
    return dict(schema=1, region=layout + '-packed-field-transfers', layout=layout, rom=target.rom,
        descriptor_sha256=sha((ROOT / contract.DESCRIPTOR).read_bytes()),
        windows=windows, fields=fields,
        cases=[dict(window=index, case=case) for index, window in enumerate(windows)
               for case in matrix.cases(source, window['key'])],
        semantic_width_inference=False, publication_width_inference=False,
        natural_entry_inference=False, hardware_qualification=False, semantic_admission=False)


def header(declared):
    lines = ['/* Exact bounded inputs; semantic outputs are independently checked. */',
             '#define PACKED_REGION ' + json.dumps(declared['region']),
             'static const struct packed_window packed_windows[] = {']
    for row in declared['windows']:
        callee = row.get('copy_callee', {})
        values = (row['start'], callee.get('entry', 0), callee.get('source', 0), callee.get('destination', 0))
        lines.append('    {' + ','.join(f'0x{value:08x}U' for value in values) + '},')
    lines.extend(('};', 'static const struct packed_source packed_sources[] = {'))
    by_key = {row['key']: index for index, row in enumerate(declared['windows'])}
    for field in declared['fields']:
        for row in field['transfer']:
            lines.append(f"    {{{by_key[row['window']]}U,0x{row['source']:08x}U,{row['physical_width_bytes']}U}},")
    lines.extend(('};', 'static const struct packed_case packed_cases[] = {'))
    for row in declared['cases']:
        case = row['case']
        values = (row['window'], case['index'], case['pattern'], case['variant'], case['sr'])
        lines.append('    {' + ','.join(f'0x{value:x}U' for value in values) + '},')
    lines.extend(('};', ''))
    return '\n'.join(lines).encode()


def region(declared, image, region_type):
    spans = [(row['start'], row['end']) for row in declared['windows']]
    spans.extend((row['copy_callee']['entry'], row['copy_callee']['end'])
                 for row in declared['windows'] if row['natural_copy_callee_required'])
    spans = sorted(set(spans))
    pools = set()
    for start, end in spans:
        for pc in range(start, end, 2):
            word = int.from_bytes(image[pc:pc + 2], 'big')
            if word >> 12 == 0xD:
                pools.add((pc & ~3) + 4 + (word & 255) * 4)
    source = Path(declared['windows'][0]['assembly']).name
    return region_type(key=declared['region'], rom=declared['rom'], source=source, harness=HARNESS,
        start=spans[0][0], end=spans[0][1], callees=tuple(spans[1:]),
        pools=tuple((address, 4) for address in sorted(pools)),
        ram_literals=tuple(address for address in sorted(pools)
                          if int.from_bytes(image[address:address + 4], 'big') >= 0xFFFE0000),
        cases=len(declared['cases']), boundary=True, return_address_offset=24, return_register=7)


def _objects(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('the packed original stdout repeats a JSON key')
        result[key] = value
    return result


def observe(stdout, declared):
    actual = [json.loads(line[len(PREFIX):], object_pairs_hook=_objects)
              for line in stdout.splitlines() if line.startswith(PREFIX)]
    if len(actual) != len(declared['cases']):
        raise ValueError('the packed original omits or duplicates an actual invocation')
    for index, (packet, row) in enumerate(zip(actual, declared['cases'])):
        wanted = dict(schema=1, index=index, window=row['window'], case=row['case']['index'])
        if any(type(packet.get(key)) is not int or packet[key] != value for key, value in wanted.items()):
            raise ValueError('the packed original changes its typed invocation identity or order')
    marker = (f"VQ_SH_ELF_PACKED_TRANSFERS status=PASS region={declared['region']} "
              f"cases={len(actual)} windows={len(declared['windows'])}")
    if stdout.splitlines().count(marker) != 1:
        raise ValueError('the packed original lacks its unique complete marker')
    return actual, marker


def run(target, directory, captured):
    import verify_map_switching as base
    import verify_stock_code as stock
    from elf_storage_layout import require_separate_storage
    declared = declaration(target)
    image = bytes(target.stock_image.data)
    selected = region(declared, image, stock.Region)
    directory = Path(directory) / declared['region']
    directory.mkdir()
    private = directory / 'consumed'
    private.mkdir()
    sources = (HARNESS, OBSERVER, selected.source)
    consumed = {name:(TOOL_DIR / name).read_bytes() for name in sources}
    consumed[HEADER] = header(declared)
    for name, data in consumed.items():
        (private / name).write_bytes(data)
    reconstruction = {}
    stock.require_reconstruction(selected, image, directory,
        source_path=private / selected.source, captured=reconstruction)
    fixture = bytearray(image)
    aliases = []
    for address in selected.ram_literals:
        original = int.from_bytes(image[address:address + 4], 'big')
        relocated = contract.alias(declared['layout'], original)
        fixture[address:address + 4] = relocated.to_bytes(4, 'big')
        aliases.append(dict(address=address, original=original, alias=relocated))
    boundary = stock.return_stub(SimpleNamespace(key=selected.key, return_address_offset=24, return_register=7))
    boundaries = []
    for row in declared['windows']:
        address = row['end']
        if (any(address < end and start < address + len(boundary) for start, end in selected.code_spans)
                or any(address < pool + size and pool < address + len(boundary) for pool, size in selected.pools)):
            raise ValueError('the packed observation boundary changes tested stock instructions or pools')
        fixture[address:address + len(boundary)] = boundary
        boundaries.append(dict(address=address, bytes=boundary.hex()))
    for start, end in selected.code_spans:
        if fixture[start:end] != image[start:end]:
            raise ValueError('the packed fixture changes an instruction under test')
    observer = directory / 'invoke.o'
    base.run_command([base.AS, '--big', '--isa=sh2e', '-o', observer, private / OBSERVER])
    fixture_path, rom_object = directory / 'fixture.bin', directory / 'fixture.o'
    fixture_path.write_bytes(fixture)
    base.run_command([base.OBJCOPY, '-I', 'binary', '-O', 'elf32-sh', '-B', 'sh',
        '--rename-section', '.data=.rom,alloc,load,code,data,contents', fixture_path, rom_object])
    elf = directory / 'harness.elf'
    command = [base.GCC, '-m2e', '-mb', '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
        '-I', private, f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE, len(fixture) + 0x10000):#x}',
        '-Wl,--section-start=.rom=0', '-o', elf, private / HARNESS, observer, rom_object]
    base.run_command(command, timeout=120)
    require_separate_storage(elf, ((contract.RAM_BASE, contract.RAM_SIZE),))
    executable = elf.read_bytes()
    simulator = [base.RUN, '--memory-region=0x01000000,64k', str(elf)]
    result = base.run_command(simulator, timeout=stock.stock_execution_timeout())
    if fixture_path.read_bytes() != fixture or elf.read_bytes() != executable:
        raise ValueError('the packed actual fixture or ELF changes during execution')
    for name in sources:
        if (TOOL_DIR / name).read_bytes() != consumed[name] or (private / name).read_bytes() != consumed[name]:
            raise ValueError('the packed consumed executable source changes during execution')
    actual, marker = observe(result.stdout, declared)
    captured.update(schema=1, declaration=declared, semantic_admission=False,
        consumed={name:data.hex() for name,data in consumed.items()}, reconstruction=reconstruction,
        image_sha256=sha(image), fixture_sha256=sha(fixture), elf_sha256=sha(executable),
        observer_object_sha256=sha(observer.read_bytes()), aliases=aliases, boundaries=boundaries,
        command=[str(part) for part in command], simulator=dict(command=simulator, returncode=result.returncode),
        stdout=result.stdout, stderr=result.stderr, stdout_sha256=sha(result.stdout.encode()),
        stderr_sha256=sha(result.stderr.encode()), observations=actual, marker=marker,
        toolchain=stock.can_latch_copy.toolchain())
    return marker
