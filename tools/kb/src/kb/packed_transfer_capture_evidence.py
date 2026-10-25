"""Independent physical and complete-state binding of packed-transfer captures."""

import hashlib
import json
from pathlib import Path

from kb import copy_evidence, ignition_literal_evidence, packed_transfer_evidence as contract
from kb import packed_transfer_matrix as matrix, repo, test_contract, test_stock_abi

PREFIX = 'kb-packed-field-observation '
HEADER = 'packed-transfer-cases.h'
HARNESS = 'harness-packed-transfers.c'
OBSERVER = 'stock_oneshot_invoke.s'
BOUNDARY = bytes.fromhex('57f6472a000b0009')


def sha(value):
    return hashlib.sha256(value).hexdigest()


def same(actual, expected, reason):
    if not test_contract.exact(actual, expected):
        raise ValueError(reason)


def declaration(model, layout):
    declared = contract.descriptor(model.root)
    windows = [row for row in declared['window'] if row['layout'] == layout]
    fields = [row for row in declared['field'] if row['layout'] == layout]
    for field in fields:
        contract.bind_field(model, field)
        covered = {(row['read'], row['physical_width_bytes']) for row in field['transfer']}
        observed = {(row['site'], row['width_bytes']) for row in field['observed']}
        if covered != observed or any(row['mode'] not in ('load', 'read') for row in field['observed']):
            raise ValueError('the packed capture does not explain every exact wider-access question')
    return dict(schema=1, region=layout + '-packed-field-transfers', layout=layout,
        rom=contract.LAYOUTS[layout][0],
        descriptor_sha256=sha((Path(model.root) / contract.DESCRIPTOR).read_bytes()),
        windows=windows, fields=fields,
        cases=[dict(window=index, case=case) for index, window in enumerate(windows)
               for case in matrix.cases(declared, window['key'])],
        semantic_width_inference=False, publication_width_inference=False,
        natural_entry_inference=False, hardware_qualification=False, semantic_admission=False)


def header(declared):
    lines = ['/* Exact bounded inputs; semantic outputs are independently checked. */',
             '#define PACKED_REGION ' + json.dumps(declared['region']),
             'static const struct packed_window packed_windows[] = {']
    for window in declared['windows']:
        call = window.get('copy_callee', {})
        values = (window['start'], call.get('entry', 0), call.get('source', 0), call.get('destination', 0))
        lines.append('    {' + ','.join(f'0x{value:08x}U' for value in values) + '},')
    lines.extend(('};', 'static const struct packed_source packed_sources[] = {'))
    indices = {window['key']: index for index, window in enumerate(declared['windows'])}
    for field in declared['fields']:
        for row in field['transfer']:
            lines.append(f"    {{{indices[row['window']]}U,0x{row['source']:08x}U,{row['physical_width_bytes']}U}},")
    lines.extend(('};', 'static const struct packed_case packed_cases[] = {'))
    for row in declared['cases']:
        case = row['case']
        values = (row['window'], case['index'], case['pattern'], case['variant'], case['sr'])
        lines.append('    {' + ','.join(f'0x{value:x}U' for value in values) + '},')
    lines.extend(('};', ''))
    return '\n'.join(lines).encode()


def _objects(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('the packed original repeats a raw observation JSON key')
        result[key] = value
    return result


def observations(packet, declared):
    stdout = packet['stdout']
    actual = [json.loads(line[len(PREFIX):], object_pairs_hook=_objects)
              for line in stdout.splitlines() if line.startswith(PREFIX)]
    if len(actual) != len(declared['cases']):
        raise ValueError('the packed original omits or duplicates a real invocation')
    keys = {'schema', 'index', 'window', 'case', 'context', 'context_after', 'observation', 'ram_before', 'ram_after'}
    parsed = []
    for index, (row, wanted) in enumerate(zip(actual, declared['cases'])):
        if type(row) is not dict or set(row) != keys:
            raise ValueError('the packed original has another complete raw observation schema')
        identity = dict(schema=1, index=index, window=wanted['window'], case=wanted['case']['index'])
        same({key:row[key] for key in identity}, identity, 'the packed original changes typed case identity or order')
        context = test_stock_abi.raw(row['context'], 76)
        if test_stock_abi.raw(row['context_after'], 76) != context:
            raise ValueError('the packed original mutates its const input context')
        observed = test_stock_abi.raw(row['observation'], 572)
        window = declared['windows'][wanted['window']]
        parsed.append(dict(index=index, entry=window['start'], context=test_stock_abi.words(context),
            exit=test_stock_abi.words(observed[:80]), sp=int.from_bytes(observed[80:84], 'big'),
            continuation=int.from_bytes(observed[84:88], 'big'),
            abi_before=test_stock_abi.words(observed[88:136]), abi_after=test_stock_abi.words(observed[136:184]),
            frame_before=observed[184:376], frame_after=observed[376:568],
            sr_before=int.from_bytes(observed[568:572], 'big'),
            memory_before=(test_stock_abi.raw(row['ram_before'], contract.RAM_SIZE),),
            memory_after=(test_stock_abi.raw(row['ram_after'], contract.RAM_SIZE),)))
    same(packet['observations'], actual, 'the packed packet differs from its actual original raw stdout')
    marker = (f"VQ_SH_ELF_PACKED_TRANSFERS status=PASS region={declared['region']} "
              f"cases={len(parsed)} windows={len(declared['windows'])}")
    if stdout.splitlines().count(marker) != 1 or packet['marker'] != marker:
        raise ValueError('the packed original lacks its unique complete marker')
    return parsed


def require_witness(model, layout, packet, inputs):
    required = {'schema', 'declaration', 'semantic_admission', 'consumed', 'reconstruction',
        'image_sha256', 'fixture_sha256', 'elf_sha256', 'observer_object_sha256', 'aliases',
        'boundaries', 'command', 'simulator', 'stdout', 'stderr', 'stdout_sha256', 'stderr_sha256',
        'observations', 'marker', 'toolchain'}
    if type(packet) is not dict or set(packet) != required:
        raise ValueError('the packed original lacks its complete physical capture schema')
    same((packet['schema'], packet['semantic_admission']), (1, False),
         'the packed raw packet changes protocol or grants its own semantic admission')
    declared = declaration(model, layout)
    same(packet['declaration'], declared, 'the packed packet changes exact native width questions or bounded inputs')
    root = Path(model.root).resolve()
    image_entry = repo.images(root)[declared['rom']]
    image = image_entry.path.read_bytes()
    identity = sha(image)
    if (identity != image_entry.sha256 or packet['image_sha256'] != identity
            or any(row['image_sha256'] != identity for row in declared['windows'])):
        raise ValueError('the packed original changes its exact stock image identity')
    source = Path(declared['windows'][0]['assembly']).name
    consumed = packet['consumed']
    if type(consumed) is not dict or set(consumed) != {HARNESS, OBSERVER, source, HEADER}:
        raise ValueError('the packed original omits a private consumed executable input')
    for name in (HARNESS, OBSERVER, source):
        path = 'tools/sh-elf-run/' + name
        data = (root / path).read_bytes()
        if consumed[name] != data.hex() or inputs.get(path) != sha(data):
            raise ValueError('the packed original consumes another executable source snapshot')
    if consumed[HEADER] != header(declared).hex():
        raise ValueError('the packed private header changes exact entry, field or matrix inputs')
    for path in (contract.DESCRIPTOR, 'tools/sh-elf-run/packed_transfer_capture.py',
                 'tools/kb/src/kb/packed_transfer_evidence.py', 'tools/kb/src/kb/packed_transfer_matrix.py',
                 'tools/kb/src/kb/packed_transfer_capture_evidence.py'):
        if inputs.get(path) != sha((root / path).read_bytes()):
            raise ValueError('the packed original producer or independent-contract source is stale')
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
    pools = sorted(pools)
    reconstruction = dict(code=[dict(start=start, end=end, stock=image[start:end].hex(),
                                     reconstructed=image[start:end].hex()) for start, end in spans],
        pools=[dict(address=address, stock=image[address:address + 4].hex(),
                    reconstructed=image[address:address + 4].hex()) for address in pools])
    same(packet['reconstruction'], reconstruction, 'the packed GNU reconstruction changes exact stock code or pointer pools')
    aliases = []
    fixture = bytearray(image)
    for address in pools:
        original = int.from_bytes(image[address:address + 4], 'big')
        if original >= 0xFFFE0000:
            relocated = contract.alias(layout, original)
            fixture[address:address + 4] = relocated.to_bytes(4, 'big')
            aliases.append(dict(address=address, original=original, alias=relocated))
    boundaries = [dict(address=row['end'], bytes=BOUNDARY.hex()) for row in declared['windows']]
    for row in boundaries:
        address = row['address']
        if (any(address < end and start < address + len(BOUNDARY) for start, end in spans)
                or any(address < pool + 4 and pool < address + len(BOUNDARY) for pool in pools)):
            raise ValueError('a packed observation boundary changes tested stock instructions or data')
        fixture[address:address + len(BOUNDARY)] = BOUNDARY
    same(packet['aliases'], aliases, 'the packed original changes RAM bank, byte lane or declared pool relocation')
    same(packet['boundaries'], boundaries, 'the packed original changes observation-boundary state restoration')
    if packet['fixture_sha256'] != sha(fixture):
        raise ValueError('the packed fixture changes an undeclared stock byte')
    for name in ('elf_sha256', 'observer_object_sha256'):
        ignition_literal_evidence.require_hash(packet[name])
    for stream in ('stdout', 'stderr'):
        if type(packet[stream]) is not str or packet[stream + '_sha256'] != sha(packet[stream].encode()):
            raise ValueError('the packed actual simulator stream changes')
    simulator = packet['simulator']
    if (type(simulator) is not dict or set(simulator) != {'returncode', 'command'}
            or type(simulator['returncode']) is not int or simulator['returncode'] != 0
            or type(simulator['command']) is not list or len(simulator['command']) != 3
            or any(type(value) is not str for value in simulator['command'])):
        raise ValueError('the packed simulator changes its actual executable, memory domain or terminal')
    from kb.test_stock_capture import tool
    base = tool(root, 'verify_map_switching.py', '_kb_packed_base_verifier')
    if simulator['command'][:2] != [base.RUN, '--memory-region=0x01000000,64k']:
        raise ValueError('the packed original names another pinned simulator path')
    elf = Path(simulator['command'][2])
    if elf.name != 'harness.elf' or elf.parent.name != declared['region']:
        raise ValueError('the packed original executes another compiled harness')
    private = elf.parent / 'consumed'
    command = [base.GCC, '-m2e', '-mb', '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
        '-I', str(private), f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE, len(fixture) + 0x10000):#x}',
        '-Wl,--section-start=.rom=0', '-o', str(elf), str(private / HARNESS),
        str(elf.parent / 'invoke.o'), str(elf.parent / 'fixture.o')]
    same(packet['command'], command, 'the packed original changes its exact compiled sources, observer or fixture')
    toolchain = packet['toolchain']
    if (type(toolchain) is not dict or set(toolchain) != {'simulator_version', 'gcc_version', 'binaries'}
            or toolchain['simulator_version'] != '16.3' or toolchain['gcc_version'] != '13.3.0'
            or type(toolchain['binaries']) is not dict
            or set(toolchain['binaries']) != {'as', 'ld', 'objcopy', 'gcc', 'run'}):
        raise ValueError('the packed original has another actual GNU toolchain')
    for identity in toolchain['binaries'].values():
        ignition_literal_evidence.require_hash(identity)
    actual = observations(packet, declared)
    source_declared = contract.descriptor(root)
    support = {row['symbol']:[] for row in declared['fields']}
    for row, observed in zip(declared['cases'], actual):
        window = declared['windows'][row['window']]
        matrix.require_input(source_declared, window, row['case'], observed)
        result = contract.require_observation(window, image, observed)
        for field in declared['fields']:
            if any(transfer['window'] == window['key'] for transfer in field['transfer']):
                support[field['symbol']].extend(contract.require_lanes(field, window, result, observed['memory_before'][0]))
    return dict(region=declared['region'], image_sha256=sha(image), fixture_sha256=sha(fixture),
                elf_sha256=packet['elf_sha256'], stdout_sha256=packet['stdout_sha256'],
                observations=len(actual), fields=support, semantic_width_inference=False,
                publication_width_inference=False, natural_entry_inference=False, hardware_qualification=False)


def require_primary(model, record):
    """Use the same original primary; no separate producer or receipt exists."""
    ignition = ignition_literal_evidence.require_primary(model, record)
    captured = record['candidate']['witness'].get('packed_transfers')
    if type(captured) is not dict or set(captured) != set(contract.LAYOUTS):
        raise ValueError('the original full primary omits or duplicates a packed-transfer layout')
    inputs = record['candidate']['producer_inputs']
    outputs = {layout:require_witness(model, layout, captured[layout], inputs) for layout in contract.LAYOUTS}
    original = copy_evidence.read_output(model.root, record['terminal']['stdout']).decode().splitlines()
    if any(original.count(packet['marker']) != 1 for packet in captured.values()):
        raise ValueError('the original full primary lacks exact unique packed-transfer markers')
    return dict(ignition_literals=ignition, packed_transfers=outputs)
