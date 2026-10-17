"""Private source capture and primary execution of the bounded injection copy."""
import ast
import hashlib
import json
from pathlib import Path
import re
import sys

TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parents[1]
sys.path.insert(0, str(ROOT / 'tools/kb/src'))
from kb import injection_copy_matrix as matrix

REGION = 'jk08a-injection-snapshot'
DESCRIPTOR = 'defs/JK08A.injection-copy.toml'
HARNESS = 'harness-injection-snapshot-capture.c'
OBSERVER = 'stock_injection_start_delay_invoke.s'
PREFIX = 'kb-injection-snapshot-observation '
EARLY = (0, 1023, 1304, 1336, 1368, 1400, 1432, 1464, 1528, 1560, 1592, 1624)
CONSUMED = (DESCRIPTOR, 'tools/sh-elf-run/stock_jk08a_injection_snapshot.s',
    'tools/sh-elf-run/harness-stock-jk08a-injection-snapshot.c',
    'tools/sh-elf-run/injection-snapshot-cases.h',
    'tools/sh-elf-run/' + HARNESS, 'tools/sh-elf-run/' + OBSERVER)


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate actual observation key')
        result[key] = value
    return result


def snapshot(root, directory):
    from kb import injection_copy_evidence as proof
    consumed = {path: (root / path).read_bytes() for path in CONSUMED}
    descriptor = proof.descriptor(root)
    header = consumed['tools/sh-elf-run/injection-snapshot-cases.h'].decode('utf-8')
    body, = re.findall(r'snapshot_cases\[\] = \{(.*?)\n\};', header, re.S)
    body = re.sub(r'(0x[0-9a-f]+|\d+)U\b', r'\1', body)
    actual = ast.literal_eval('[' + body.replace('{', '[').replace('}', ']') + ']')
    if actual != matrix.cases():
        raise ValueError('the frozen C rows differ from independent copy expectations')
    early, = re.findall(r'snapshot_early_indices\[\] = \{(.*?)\};', header, re.S)
    if tuple(int(value) for value in re.findall(r'(\d+)U', early)) != EARLY:
        raise ValueError('the fixed feedback selection differs')
    private = directory / 'injection-copy-consumed'
    for path, data in consumed.items():
        target = private / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return dict(consumed=consumed, descriptor=descriptor, cases=actual,
                source_dir=private / 'tools/sh-elf-run')


def observe(stdout, captured, *, early=False):
    values = [json.loads(line[len(PREFIX):], object_pairs_hook=_object)
              for line in stdout.splitlines() if line.startswith(PREFIX)]
    indices = EARLY if early else range(len(captured['cases']))
    if len(values) != len(indices):
        raise ValueError('the original execution omits or duplicates copy observations')
    memory = None
    for index, observed in zip(indices, values):
        memory = matrix.validate_observation(index, captured['cases'][index], observed, memory)
    marker = 'VQ_SH_ELF_INJECTION_SNAPSHOT_CAPTURE cases=' + str(len(indices)) + ' early=' + ('true' if early else 'false')
    if stdout.splitlines().count(marker) != 1:
        raise ValueError('the original capture lacks its unique complete marker')
    return values


def run_region(region, directory, *, capture=None):
    import verify_map_switching as base
    import verify_stock_code as stock
    from can_latch_copy import toolchain
    if region.key != REGION:
        raise ValueError('the injection capture is bound to one stock region')
    copied = snapshot(ROOT, directory)
    source = copied['source_dir']
    observer = directory / 'injection-copy-invoke.o'
    base.run_command([base.AS, '--big', '--isa=sh2e', '-I', source,
                      '-o', observer, source / OBSERVER])
    image = stock.stock_image(region.rom)
    reconstructed = {}
    instructions = stock.require_reconstruction(region, image, directory,
        source_path=source / region.source, captured=reconstructed)
    fixture = stock.build_fixture(region, image)
    boundary = stock.return_stub(region)
    if boundary != bytes.fromhex('57f6472a000b0009'):
        raise ValueError('the declared SP+24/R7 observation boundary changes')
    fixture_path = directory / 'injection-copy.sim-fixture'
    fixture_path.write_bytes(fixture)
    rom = directory / 'injection-copy-rom.o'
    base.run_command([base.OBJCOPY, '-I', 'binary', '-O', 'elf32-sh', '-B', 'sh',
        '--rename-section', '.data=.rom,alloc,load,code,data,contents', fixture_path, rom])
    output = directory / 'injection-copy-harness.elf'
    defines = stock.harness_defines(region, image)
    base.run_command([base.GCC, '-m2e', '-mb', '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
        f'-DREGION_KEY="{region.key}"',
        *(f'-D{name}={value:#x}U' for name, value in defines.items()),
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE, len(fixture) + 0x10000):#x}',
        '-Wl,--section-start=.rom=0', '-o', output, source / HARNESS, observer, rom], timeout=120)
    stock.require_separate_storage(output, ((base.TEST_RAM_BASE, 65536),))
    executable = output.read_bytes()
    result = base.run_command([base.RUN, f'--memory-region={base.TEST_RAM_BASE:#x},64k', output],
                              timeout=stock.stock_execution_timeout())
    if output.read_bytes() != executable:
        raise ValueError('the actual injection ELF changes during execution')
    marker = f'VQ_SH_ELF_STOCK_CODE status=PASS region={region.key} cases={region.cases}'
    if result.stdout.splitlines().count(marker) != 1:
        raise ValueError('the checked stock harness lacks its unique complete PASS marker')
    early = bool(dict(region.constants).get('EARLY_ONLY'))
    observed = observe(result.stdout, copied, early=early)
    if early:
        print(result.stdout, end='')
    if capture is not None:
        capture.update(region=REGION, cases=copied['cases'], observations=observed,
            consumed={path: data.hex() for path, data in copied['consumed'].items()},
            code=reconstructed['code'], pools=reconstructed['pools'],
            image_sha256=hashlib.sha256(image).hexdigest(),
            fixture_sha256=hashlib.sha256(fixture).hexdigest(),
            elf_sha256=hashlib.sha256(executable).hexdigest(),
            aliases=[[0x213a0, 0xffff2330, 0x01002330], [0x213a4, 0xffff23bc, 0x010023bc]],
            boundary=dict(address=0x2131c, bytes=boundary.hex()),
            entry=dict(r11=0x22558, r12=140, caller=0x21314, callsite=0x21318,
                       delay_slot=0x2131a, source=0xffff23bc, destination=0xffff2330, length=140),
            toolchain=toolchain())
    return instructions


def verify_early():
    from dataclasses import replace
    import tempfile
    import verify_stock_code as stock
    region, = [value for value in stock.REGIONS if value.key == REGION]
    region = replace(region, cases=len(EARLY), constants=(('EARLY_ONLY', 1),))
    with tempfile.TemporaryDirectory(prefix='vq-injection-copy-feedback-') as directory:
        run_region(region, Path(directory))
    print(f'VQ_SH_ELF_INJECTION_COPY_SUBSET status=PASS cases={len(EARLY)} production=false')
