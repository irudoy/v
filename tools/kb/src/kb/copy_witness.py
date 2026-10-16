"""Producer provenance and independent finalization of the CAN GNU witness."""

import hashlib
import json
from pathlib import Path

from kb import copy_evidence as proof, copy_matrix, local_paths, repo, test_evidence

CONSUMED = (proof.DESCRIPTOR,
    'tools/sh-elf-run/stock_jk08a_can_latch_copy.s',
    'tools/sh-elf-run/harness-stock-jk08a-can-latch-copy.c',
    'tools/sh-elf-run/invoke-can-latch-copy.s',
    'tools/sh-elf-run/can-latch-copy-cases.h')


def provenance(root):
    """Native inputs and producer source bytes, separate from proof freshness.

    Feature composers, renderers and their assembly/header/configuration inputs
    execute in the complete primary pipeline. Shared Python tools include
    transitive imports beyond the compiler's own source closure. Test fixtures
    and human documentation do not belong to this producer source manifest.
    Runtime binaries, linked ELF and fixture identities remain execution data.
    """
    from kb import fingerprint
    paths = set(fingerprint.inputs(root)) | set(proof.EXECUTION_FILES)
    paths.update(path.relative_to(root).as_posix() for path in
                 (root / 'tools/sh-elf-run').rglob('*')
                 if path.is_file() and path.suffix in ('.py', '.c', '.s', '.h', '.sh'))
    for directory, suffixes in ((root / 'patches', {'.py', '.s', '.h', '.toml', '.json'}),
                                 (root / 'tools', {'.py'})):
        paths.update(path.relative_to(root).as_posix() for path in directory.rglob('*')
                     if path.is_file() and path.suffix in suffixes
                     and 'tests' not in path.relative_to(directory).parts)
    return {path: hashlib.sha256((root / path).read_bytes()).hexdigest() for path in sorted(paths)}


def begin(root=repo.ROOT):
    from kb import compile
    model = compile.build(root)
    proof.descriptor(root)
    return dict(schema=proof.SCHEMA, key=proof.KEY, mode='full', complete=False,
                scope=proof.scope_digest(model), inputs=proof.inputs(root),
                native_model=test_evidence.model_digest(model), producer_inputs=provenance(root))


def finish(candidate, witness, root=repo.ROOT):
    current = begin(root)
    if candidate != current:
        raise ValueError('copy execution source or native facts change during the primary gate')
    result = {**candidate, 'complete': True, 'witness': witness}
    validate(result, root)
    return result


def _sha(value):
    return type(value) is str and len(value) == 64 and all(char in '0123456789abcdef' for char in value)


def validate(candidate, root):
    if (type(candidate['schema']) is not int or candidate['schema'] != proof.SCHEMA
            or candidate['key'] != proof.KEY or candidate['mode'] != 'full'
            or candidate['complete'] is not True):
        raise ValueError('only the complete registered CAN copy producer qualifies')
    descriptor = proof.descriptor(root)
    expected = copy_matrix.cases(descriptor)
    witness = candidate['witness']
    if witness['region'] != proof.REGION or proof.encode(witness['cases']) != proof.encode(expected):
        raise ValueError('wrong, skipped, reordered or incomplete copy case matrix')
    if len(witness['observations']) != len(expected):
        raise ValueError('copy execution lacks actual case observations')
    for case, observed in zip(expected, witness['observations']):
        copy_matrix.validate_observation(case, observed)
    if set(witness['consumed']) != set(CONSUMED):
        raise ValueError('copy execution omits consumed private source bytes')
    for path, data in witness['consumed'].items():
        if hashlib.sha256(bytes.fromhex(data)).hexdigest() != candidate['inputs'][path]:
            raise ValueError('copy execution consumes another source snapshot')
    image = repo.images(root)['JK08A']
    data = proof._read(root, image.path.relative_to(root).as_posix())
    if witness['image_sha256'] != hashlib.sha256(data).hexdigest():
        raise ValueError('copy execution uses another stock image')
    spans = [(0x21094, 0x2109a), (0x22558, 0x22590)]
    required = [dict(start=start, end=end, stock=data[start:end].hex(),
                     reconstructed=data[start:end].hex()) for start, end in spans]
    if witness['code'] != required:
        raise ValueError('stock instructions differ from their independent reconstruction')
    pools = [dict(address=row['address'], stock=row['value'].to_bytes(4, 'big').hex(),
                  reconstructed=row['value'].to_bytes(4, 'big').hex()) for row in descriptor['pool']]
    if sorted(witness['pools'], key=lambda row: row['address']) != sorted(pools, key=lambda row: row['address']):
        raise ValueError('the caller pointer pools differ from their reconstruction')
    if witness['aliases'] != [[0x2125c, 0xffff4194, 0x01004194]]:
        raise ValueError('wrong or undeclared simulator pointer relocation')
    if witness['entry'] != dict(r1=0x01004188, r11=0x22558, caller=0x21094,
                               callsite=0x21096, delay_slot=0x21098, length=12):
        raise ValueError('wrong bounded caller entry contract')
    if not _sha(witness['elf_sha256']) or not _sha(witness['fixture_sha256']):
        raise ValueError('missing compiled executable or fixture identity')
    boundary = copy_matrix.boundary_bytes()
    if witness['boundary'] != dict(address=0x2109a, bytes=boundary.hex()):
        raise ValueError('the observation boundary changes live state before capture')
    fixture = bytearray(data)
    fixture[0x2125c:0x21260] = (0x01004194).to_bytes(4, 'big')
    fixture[0x2109a:0x2109a + len(boundary)] = boundary
    if witness['fixture_sha256'] != hashlib.sha256(fixture).hexdigest():
        raise ValueError('the simulator fixture changes undeclared stock bytes')
    if witness['toolchain']['simulator_version'] != '16.3' or witness['toolchain']['gcc_version'] != '13.3.0':
        raise ValueError('wrong actual GNU toolchain')
    if set(witness['toolchain']['binaries']) != {'as', 'ld', 'objcopy', 'gcc', 'run'} or not all(
            _sha(value) for value in witness['toolchain']['binaries'].values()):
        raise ValueError('incomplete GNU executable provenance')


def finalize(process_path, stdout_path, stderr_path, root=repo.ROOT):
    from kb import lock
    with lock.held(root):
        return _finalize(process_path, stdout_path, stderr_path, root)


def _finalize(process_path, stdout_path, stderr_path, root):
    record = prepare(process_path, stdout_path, stderr_path, root)
    proof.publish(Path(root) / proof.RECEIPT, record)
    return record


def prepare(process_path, stdout_path, stderr_path, root=repo.ROOT):
    """Independently validate a completed original, without publishing a receipt.

    The caller holds the native source lock for this preparation. A coordinator
    publishing later separately fences sources and original output bytes.
    """
    root = Path(root).resolve()
    process_path = local_paths.owned(process_path, root).resolve()
    original = process_path.read_bytes()
    process = json.loads(original)
    proof.terminal_check(process)
    terminal = dict(process)
    streams = {}
    for stream, path in (('stdout', stdout_path), ('stderr', stderr_path)):
        path = local_paths.owned(path, root).resolve()
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != process[stream + '_sha256']:
            raise ValueError('the original bounded process stream hash disagrees')
        terminal[stream] = local_paths.relative(path, root)
        streams[stream] = data
    lines = streams['stdout'].decode('utf-8').splitlines()
    packets = [line[len(proof.MARKER):] for line in lines if line.startswith(proof.MARKER)]
    if len(packets) != 1 or sum(line.startswith('VQ_SH_ELF_VERIFY status=PASS ') for line in lines) != 1:
        raise ValueError('the primary full pipeline or its unique copy packet is absent')
    candidate = json.loads(packets[0])
    current = begin(root)
    if {key: candidate[key] for key in current} != {**current, 'complete': True}:
        raise ValueError('copy producer provenance disagrees with independent finalization')
    validate(candidate, root)
    record = dict(schema=proof.SCHEMA, candidate=candidate, terminal=terminal,
        process_path=local_paths.relative(process_path, root), process_sha256=hashlib.sha256(original).hexdigest(),
        native_model=candidate['native_model'], native_inputs=proof.digest(candidate['producer_inputs']))
    if process_path.read_bytes() != original:
        raise ValueError('the original process receipt changes before publication')
    for stream in ('stdout', 'stderr'):
        if (root / terminal[stream]).read_bytes() != streams[stream]:
            raise ValueError('the consumed terminal stream changes before publication')
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
    print('qualified CAN copy execution receipt published')


if __name__ == '__main__':
    main()
