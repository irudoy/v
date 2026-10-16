"""Primary SID22 producer provenance and independent receipt finalization."""

import hashlib
import json
from pathlib import Path

from kb import copy_witness, local_paths, repo, sid22_evidence as proof, sid22_matrix as matrix
from kb.test_evidence import digest, encode, model_digest, publish

CONSUMED = (proof.DESCRIPTOR,
    'tools/sh-elf-run/stock_jk08a_sid22_pointer_read.s',
    'tools/sh-elf-run/harness-stock-jk08a-sid22-pointer-read.c',
    'tools/sh-elf-run/invoke-sid22-pointer-read.s',
    'tools/sh-elf-run/sid22-pointer-read-cases.h')


def begin(root=repo.ROOT):
    from kb import compile
    model = compile.build(root)
    proof.descriptor(root)
    return dict(schema=proof.SCHEMA, key=proof.KEY, mode='full', complete=False, production=True,
                scope=proof.scope_digest(model), inputs=proof.inputs(root),
                native_model=model_digest(model), producer_inputs=copy_witness.provenance(root))


def finish(candidate, witness, root=repo.ROOT):
    if candidate != begin(root):
        raise ValueError('SID22 execution sources or native facts change during the primary gate')
    result = {**candidate, 'complete': True, 'witness': witness}
    validate(result, root)
    return result


def validate(candidate, root):
    if (type(candidate['schema']) is not int or candidate['schema'] != proof.SCHEMA
            or candidate['key'] != proof.KEY or candidate['mode'] != 'full'
            or candidate['complete'] is not True or candidate['production'] is not True):
        raise ValueError('only the complete registered SID22 producer qualifies')
    contract = proof.descriptor(root)
    image = repo.images(root)['JK08A']
    stock = proof._read(root, image.path.relative_to(root).as_posix())
    cases = matrix.cases(contract, stock)
    witness = candidate['witness']
    if witness['region'] != proof.REGION or encode(witness['cases']) != encode(cases):
        raise ValueError('wrong, skipped, reordered or incomplete SID22 matrix')
    if len(witness['observations']) != len(cases):
        raise ValueError('SID22 execution lacks actual case observations')
    for case, observed in zip(cases, witness['observations']):
        matrix.validate_observation(case, observed)
    if set(witness['consumed']) != set(CONSUMED):
        raise ValueError('SID22 execution omits consumed private source bytes')
    for path, data in witness['consumed'].items():
        if hashlib.sha256(bytes.fromhex(data)).hexdigest() != candidate['inputs'][path]:
            raise ValueError('SID22 execution consumes another source snapshot')
    if bytes.fromhex(witness['consumed'][CONSUMED[-1]]) != matrix.render_header(contract, stock).encode():
        raise ValueError('the consumed SID22 header differs from its declared matrix')
    if witness['image_sha256'] != hashlib.sha256(stock).hexdigest():
        raise ValueError('SID22 execution uses another stock image')
    code = [dict(start=start, end=end, stock=stock[start:end].hex(), reconstructed=stock[start:end].hex())
            for start, end in contract.body]
    if witness['code'] != code:
        raise ValueError('SID22 instruction ranges differ from their independent reconstruction')
    pools = [dict(address=address, stock=stock[address:address + width].hex(),
                  reconstructed=stock[address:address + width].hex())
             for address, width in (*contract.pools, *((start, end - start) for _, start, end, _ in proof.TABLES))]
    if sorted(witness['pools'], key=lambda row: row['address']) != sorted(pools, key=lambda row: row['address']):
        raise ValueError('SID22 pools or pointer tables differ from their reconstruction')
    fixture, aliases = matrix.fixture(stock, contract)
    if witness['aliases'] != aliases or witness['fixture_sha256'] != hashlib.sha256(fixture).hexdigest():
        raise ValueError('SID22 fixture changes undeclared stock bytes')
    if not copy_witness._sha(witness['elf_sha256']):
        raise ValueError('SID22 execution lacks its actual executable identity')
    tools = witness['toolchain']
    if tools['simulator_version'] != '16.3' or tools['gcc_version'] != '13.3.0':
        raise ValueError('wrong actual SID22 GNU toolchain')
    if set(tools['binaries']) != {'as', 'ld', 'objcopy', 'gcc', 'run'} or not all(
            copy_witness._sha(value) for value in tools['binaries'].values()):
        raise ValueError('incomplete SID22 GNU executable provenance')


def finalize(process_path, stdout_path, stderr_path, root=repo.ROOT):
    from kb import lock
    with lock.held(root):
        return _finalize(process_path, stdout_path, stderr_path, root)


def _finalize(process_path, stdout_path, stderr_path, root):
    record = prepare(process_path, stdout_path, stderr_path, root)
    publish(Path(root) / proof.RECEIPT, record)
    return record


def prepare(process_path, stdout_path, stderr_path, root=repo.ROOT):
    """Validate the complete original under the caller's lock; do not publish."""
    root = Path(root).resolve()
    process_path = local_paths.owned(process_path, root).resolve()
    original = process_path.read_bytes()
    process = json.loads(original)
    proof.terminal_check(process)
    terminal, streams = dict(process), {}
    for stream, path in (('stdout', stdout_path), ('stderr', stderr_path)):
        path = local_paths.owned(path, root).resolve()
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != process[stream + '_sha256']:
            raise ValueError('the original SID22 bounded process stream hash disagrees')
        terminal[stream], streams[stream] = local_paths.relative(path, root), data
    lines = streams['stdout'].decode().splitlines()
    packets = [line[len(proof.MARKER):] for line in lines if line.startswith(proof.MARKER)]
    if len(packets) != 1 or sum(line.startswith('VQ_SH_ELF_VERIFY status=PASS ') for line in lines) != 1:
        raise ValueError('the full primary pipeline or unique SID22 packet is absent')
    candidate = json.loads(packets[0])
    current = begin(root)
    if {key: candidate[key] for key in current} != {**current, 'complete': True}:
        raise ValueError('SID22 producer provenance disagrees with independent finalization')
    validate(candidate, root)
    record = dict(schema=proof.SCHEMA, candidate=candidate, terminal=terminal,
        process_path=local_paths.relative(process_path, root), process_sha256=hashlib.sha256(original).hexdigest(),
        native_model=candidate['native_model'], native_inputs=digest(candidate['producer_inputs']))
    # Recheck live inputs and the exact consumed buffers before atomic publication.
    if current != begin(root) or process_path.read_bytes() != original:
        raise ValueError('SID22 source or original process changes before publication')
    if any((root / terminal[name]).read_bytes() != data for name, data in streams.items()):
        raise ValueError('the consumed SID22 stream changes before publication')
    return record


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['finalize'])
    parser.add_argument('--process', required=True)
    parser.add_argument('--stdout', required=True)
    parser.add_argument('--stderr', required=True)
    args = parser.parse_args(argv)
    finalize(args.process, args.stdout, args.stderr)
    print('qualified SID22 pointer-read execution receipt published')


if __name__ == '__main__':
    main()
