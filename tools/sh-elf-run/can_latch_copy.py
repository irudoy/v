"""Inputs and observations for the primary bounded CAN copy executable gate."""

import hashlib
import json
from pathlib import Path
import shutil
import sys
import tomllib

TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parents[1]
sys.path.insert(0, str(ROOT / 'tools/kb/src'))
from kb import copy_evidence as proof, copy_matrix, copy_witness


def render_header(descriptor):
    rows = copy_matrix.cases(descriptor)
    text = ['/* Generated from JK08A.can-latch-copy.toml and kb.copy_matrix. */',
        'struct can_copy_case {',
        '    unsigned index, caller, source, destination, length, sr, carry;',
        '    uint32_t incoming[15], expected[15], gbr, mach, macl;',
        '    uint8_t bytes[16];', '};',
        'static const struct can_copy_case can_copy_cases[] = {']
    def array(values):
        return '{' + ','.join(f'0x{value:08x}U' for value in values) + '}'
    for row in rows:
        numbers = [row[key] for key in ('index', 'caller', 'source', 'destination', 'length', 'sr', 'carry')]
        text.append('    {' + ','.join(str(int(value)) + 'U' for value in numbers) + ','
            + array(row['incoming']) + ',' + array(copy_matrix.expected_registers(row)) + ','
            + ','.join(f'0x{row[key]:08x}U' for key in ('gbr', 'mach', 'macl')) + ','
            + array(copy_matrix.source_bytes(row) or [0]) + '},')
    text += ['};', 'static const unsigned can_copy_early_indices[] = {'
             + ','.join(str(value) + 'U' for value in copy_matrix.early_indices(rows)) + '};', '']
    return '\n'.join(text)


def case_count(root=ROOT):
    return len(copy_matrix.cases(proof.descriptor(root)))


def snapshot(root, directory):
    consumed = {path: (root / path).read_bytes() for path in copy_witness.CONSUMED}
    descriptor = tomllib.loads(consumed[proof.DESCRIPTOR].decode())
    if descriptor != proof.descriptor(root):
        raise ValueError('the consumed CAN descriptor differs from its stock binding')
    header = 'tools/sh-elf-run/can-latch-copy-cases.h'
    if consumed[header] != render_header(descriptor).encode():
        raise ValueError('the CAN case header differs from its declared matrix')
    private = directory / 'can-copy-consumed'
    for path, data in consumed.items():
        target = private / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return dict(consumed=consumed, descriptor=descriptor, cases=copy_matrix.cases(descriptor),
                source_dir=private / 'tools/sh-elf-run')


def boundary(observer, directory):
    import verify_map_switching as base
    output = directory / 'can-copy-boundary.raw'
    base.run_command([base.OBJCOPY, '-O', 'binary', '--only-section=.copy_boundary', observer, output])
    data = output.read_bytes()
    if data != copy_matrix.boundary_bytes():
        raise ValueError('the assembled CAN observer differs from its capture contract')
    return data


def observe(stdout, captured, *, early=False):
    observations = [json.loads(line[len('CAN_COPY_CASE '):]) for line in stdout.splitlines()
                    if line.startswith('CAN_COPY_CASE ')]
    cases = captured['cases']
    selected = [cases[index] for index in copy_matrix.early_indices(cases)] if early else cases
    if len(observations) != len(selected):
        raise ValueError('the GNU CAN run omits expected case observations')
    for case, observed in zip(selected, observations):
        copy_matrix.validate_observation(case, observed)
    return observations


def toolchain():
    import verify_map_switching as base
    simulator, gcc = base.require_toolchain_version()
    binaries = {}
    for name in ('as', 'ld', 'objcopy', 'gcc', 'run'):
        command = getattr(base, name.upper())
        path = shutil.which(str(command))
        if path is None:
            raise ValueError(f'the primary GNU tool {command} is absent')
        binaries[name] = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    return dict(simulator_version=simulator.split()[-1], gcc_version=gcc, binaries=binaries)


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-cases', action='store_true', required=True)
    parser.parse_args()
    target = TOOL_DIR / 'can-latch-copy-cases.h'
    target.write_text(render_header(proof.descriptor(ROOT)))
    print(f'{target.relative_to(ROOT)}: {case_count()} cases')


if __name__ == '__main__':
    main()
