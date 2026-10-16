"""Consumed sources, exact reconstruction and primary SID22 observations."""

import hashlib
import json
from pathlib import Path
import sys
import tomllib

TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parents[1]
sys.path.insert(0, str(ROOT / 'tools/kb/src'))
from kb import repo, sid22_evidence as proof, sid22_matrix as matrix

REGION = 'jk08a-sid22-pointer-read'
CONSUMED = (proof.DESCRIPTOR,
    'tools/sh-elf-run/stock_jk08a_sid22_pointer_read.s',
    'tools/sh-elf-run/harness-stock-jk08a-sid22-pointer-read.c',
    'tools/sh-elf-run/invoke-sid22-pointer-read.s',
    'tools/sh-elf-run/sid22-pointer-read-cases.h')


render_header = matrix.render_header


def image(root=ROOT):
    return repo.images(root)['JK08A'].path.read_bytes()


def region(Region, *, early=False):
    contract = proof.descriptor(ROOT)
    cases = matrix.cases(contract, image())
    tables = tuple((start, end - start) for _, start, end, _ in proof.TABLES)
    return Region(key=REGION, rom='JK08A', source='stock_jk08a_sid22_pointer_read.s',
        harness='harness-stock-jk08a-sid22-pointer-read.c', start=contract.body[0][0],
        end=contract.body[0][1], callees=contract.body[1:],
        pools=(*contract.pools, *tables), ram_literals=(),
        cases=len(matrix.early_indices(cases)) if early else len(cases), boundary=False,
        constants=(('EARLY_ONLY', int(early)),))


fixture = matrix.fixture


def snapshot(root, directory):
    consumed = {path: (root / path).read_bytes() for path in CONSUMED}
    contract = proof.descriptor(root, value=tomllib.loads(consumed[proof.DESCRIPTOR].decode()))
    stock = image(root)
    if consumed[CONSUMED[-1]] != render_header(contract, stock).encode():
        raise ValueError('the consumed SID22 header differs from its declared matrix')
    private = directory / 'sid22-consumed'
    for path, data in consumed.items():
        target = private / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return dict(consumed=consumed, contract=contract, image=stock,
                cases=matrix.cases(contract, stock), source_dir=private / 'tools/sh-elf-run')


def run_region(selected, directory, *, capture=None):
    import verify_stock_code as stock
    import verify_map_switching as base
    import can_latch_copy
    from elf_storage_layout import require_separate_storage
    execution_timeout = stock.stock_execution_timeout()
    captured = snapshot(ROOT, directory)
    source = captured['source_dir']
    original = captured['image']
    reconstruction = {}
    count = stock.require_reconstruction(selected, original, directory,
        source_path=source / selected.source, captured=reconstruction)
    fixture_bytes, aliases = fixture(original, captured['contract'])
    raw = directory / 'sid22-fixture.bin'
    raw.write_bytes(fixture_bytes)
    rom = directory / 'sid22-rom.o'
    base.run_command([base.OBJCOPY, '-I', 'binary', '-O', 'elf32-sh', '-B', 'sh',
        '--rename-section', '.data=.rom,alloc,load,code,data,contents', raw, rom])
    invoke = directory / 'sid22-invoke.o'
    base.run_command([base.AS, '--big', '--isa=sh2e', '-o', invoke,
                      source / 'invoke-sid22-pointer-read.s'])
    for section, kind, address, prefix in (('.sid_transport_stub', 1, 0x2ec9a, 2), ('.sid_error_stub', 2, 0x34114, 0)):
        stub = directory / (section + '.raw')
        base.run_command([base.OBJCOPY, '-O', 'binary', '--only-section=' + section, invoke, stub])
        if stub.read_bytes()[prefix:] != matrix.stub_bytes(kind, address):
            raise ValueError('the assembled helper observer differs from its explicit byte contract')
    stripped = directory / 'sid22-observer.o'
    base.run_command([base.OBJCOPY, '--remove-section=.sid_transport_stub',
                      '--remove-section=.sid_error_stub', invoke, stripped])
    output = directory / 'sid22-harness.elf'
    early = bool(dict(selected.constants).get('EARLY_ONLY'))
    text_base = max(base.DRIVER_TEXT_BASE, len(fixture_bytes) + 0x10000)
    base.run_command([base.GCC, '-m2e', '-mb', '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
        f'-DEARLY_ONLY={int(early)}', f'-Wl,-Ttext-segment={text_base:#x}',
        '-Wl,--section-start=.rom=0', '-o', output,
        source / selected.harness, stripped, rom], timeout=120)
    require_separate_storage(output, ((matrix.RAM_BASE, 65536),))
    executable = output.read_bytes()
    terminal = base.run_command([base.RUN, f'--memory-region={matrix.RAM_BASE:#x},64k', output],
                                timeout=execution_timeout)
    if output.read_bytes() != executable:
        raise ValueError('the actual SID22 executable changes during execution')
    prefix = 'SID22_CASE '
    observations = [json.loads(line[len(prefix):]) for line in terminal.stdout.splitlines() if line.startswith(prefix)]
    rows = captured['cases']
    tested = [rows[index] for index in matrix.early_indices(rows)] if early else rows
    if len(observations) != len(tested):
        raise ValueError('the SID22 execution omits or duplicates case observations')
    for case, observed in zip(tested, observations):
        matrix.validate_observation(case, observed)
    marker = (f'VQ_SH_ELF_SID22_SUBSET status=PASS region={REGION} cases={len(tested)} production=false'
              if early else f'VQ_SH_ELF_STOCK_CODE status=PASS region={REGION} cases={len(tested)}')
    if marker not in terminal.stdout.splitlines():
        raise ValueError('the SID22 execution lacks its exact terminal marker')
    if capture is not None:
        capture.update(region=REGION, cases=tested, observations=observations,
            consumed={path: value.hex() for path, value in captured['consumed'].items()},
            code=reconstruction['code'], pools=reconstruction['pools'], aliases=aliases,
            image_sha256=hashlib.sha256(original).hexdigest(), fixture_sha256=hashlib.sha256(fixture_bytes).hexdigest(),
            elf_sha256=hashlib.sha256(executable).hexdigest(), toolchain=can_latch_copy.toolchain())
    return count


def verify_early():
    import tempfile
    import verify_map_switching as base
    import verify_stock_code as stock
    from kb.test_evidence import json_text
    base.require_toolchain_version()
    before = proof.inputs(ROOT)
    selected = region(stock.Region, early=True)
    captured = {}
    with tempfile.TemporaryDirectory(prefix='vq-sh-elf-stock-') as directory:
        run_region(selected, Path(directory), capture=captured)
    if before != proof.inputs(ROOT):
        raise ValueError('SID22 consumed sources change during the subset run')
    print('kb-sid22-subset ' + json_text(dict(schema=proof.SCHEMA, key=proof.KEY,
        mode='early', complete=False, production=False, inputs=before, witness=captured)))
    print(f'VQ_SH_ELF_SID22_SUBSET status=PASS cases={len(captured["cases"])} production=false')


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write', '--write-cases', action='store_true')
    mode.add_argument('--check', action='store_true')
    args = parser.parse_args()
    contract = proof.descriptor(ROOT)
    target = TOOL_DIR / 'sid22-pointer-read-cases.h'
    expected = render_header(contract, image())
    if args.check:
        if target.read_text() != expected:
            raise SystemExit('the SID22 case header differs from its declared matrix')
    else:
        target.write_text(expected)
    print(f'SID22 matrix: {len(matrix.cases(contract, image()))} cases')


if __name__ == '__main__':
    main()
