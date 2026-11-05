"""Execute the optional SH-2E interrupt entry and return contract."""

import hashlib
import os
from pathlib import Path
import signal
import tempfile

import verify_map_switching as base
from elf_storage_layout import require_separate_storage


TOOL = Path(__file__).resolve().parent
VARIABLES = tuple('VQ_SH_IRQ_' + name for name in ('PC', 'COUNT', 'LEVEL', 'VECTOR', 'REPORT'))
MARKER = 'VQ_SH_IRQ_PROBE status=PASS '
CASES = {
    0: 'immediate', 1: 'masked', 2: 'bra', 3: 'delay_slot', 5: 'count',
    6: 'equal_priority', 15: 'fpu',
    16: 'inhibit_chain', 17: 'inhibiting_delay_slot',
    18: 'bt_s_taken', 19: 'bt_s_untaken', 20: 'bf_s_taken', 21: 'bf_s_untaken',
    22: 'jmp', 23: 'jsr', 24: 'braf', 25: 'bsrf', 26: 'rts', 27: 'bsr',
    29: 'vector_at_acceptance', 30: 'vbr_at_acceptance',
    31: 'replace_lower_priority',
    33: 'rte_delay_slot_sp',
    34: 'irq_inside_gnu_trap', 35: 'gnu_trap_inside_irq',
}


def environment(request=None):
    result = dict(os.environ)
    for name in VARIABLES:
        result.pop(name, None)
    for name in ('VQ_SH_PC_TRACE_FILE', 'VQ_SH_PC_TRACE_FORMAT',
                 'VQ_SH_PC_TRACE_RANGES', 'VQ_SH_HIGH_RAM_BASE'):
        result.pop(name, None)
    if request is not None:
        result.update({'VQ_SH_IRQ_' + key: str(value) for key, value in request.items()})
    return result


def symbols(elf):
    output = base.run_command(['sh-elf-nm', '-n', '--defined-only', elf]).stdout
    return {parts[2]: int(parts[0], 16) for line in output.splitlines()
            if len(parts := line.split()) == 3}


def read_values(output):
    rows = [line for line in output.splitlines() if line.startswith(MARKER)]
    if len(rows) != 1:
        raise base.VerificationError(f'IRQ probe lacks one terminal: {output}')
    return {key: int(value, 16) for word in rows[0][len(MARKER):].split()
            for key, value in (word.split('=', 1),)}


def run_probe(elf, request=None, *, code=0, terminal=True):
    original = elf.read_bytes()
    child = environment(request)
    trace = (Path(request['REPORT']).with_suffix('.trace') if request is not None
             else elf.with_suffix('.disabled.trace'))
    addresses = symbols(elf)
    child.update(VQ_SH_PC_TRACE_FILE=str(trace), VQ_SH_PC_TRACE_FORMAT='v1',
                 VQ_SH_PC_TRACE_RANGES=(f'{addresses["irq_probe"]:x}:'
                                        f'{addresses["irq_handler_end"]:x}'))
    try:
        result = base.run_command([base.RUN, elf], env=child,
                                  expected_returncode=code)
    except base.VerificationError:
        if request is not None:
            report = Path(request['REPORT'])
            print('IRQ failure report:', report.read_text() if report.exists() else 'absent', flush=True)
        if trace.exists():
            with trace.open('rb') as source:
                source.seek(max(0, trace.stat().st_size - 4096))
                print(source.read().decode(errors='replace'), flush=True)
        raise
    if elf.read_bytes() != original:
        raise base.VerificationError('IRQ probe ELF changes during execution')
    base.read_pc_trace(trace)
    return result, read_values(result.stdout) if terminal else {}


def compile_probe(directory, case, *, exit_code=0, name='', flags=()):
    elf = directory / f'irq-{case}-{exit_code}-{name}.elf'
    base.run_command([base.GCC, '-m2e', '-mb', '-O1', '-std=c11',
                      '-Wall', '-Wextra', '-Werror', f'-DPROBE_CASE={case}',
                      f'-DPROBE_EXIT={exit_code}', *flags, TOOL / 'harness-simulator-irq.c',
                      TOOL / 'harness-simulator-irq.S', '-o', elf])
    return elf


def request_for(elf, report, *, count=1, level=8, vector=80):
    return dict(PC=f'{symbols(elf)["irq_trigger"]:x}', COUNT=count, LEVEL=level,
                VECTOR=vector, REPORT=report)


def check_positive(elf, directory, case, count, level, vector, *, name=None):
    addresses = symbols(elf)
    name = name or CASES[case]
    report = directory / f'irq-{case}-{name}-{count}-{level}-{vector}.report'
    request = request_for(elf, report, count=count, level=level, vector=vector)
    if vector == 0:
        request['PC'] = '0x' + request['PC']
    _, values = run_probe(elf, request)
    expected = dict(triggered=addresses['irq_trigger'], accepted=addresses['irq_resume'],
                    handler=addresses['irq_handler_alt' if case in (29, 30) else 'irq_handler'],
                    sr={5: 0x302, 19: 0x302, 20: 0x302, 31: 0x333, 34: 0x383}.get(case, 0x303))
    rows = report.read_text().splitlines()
    if len(rows) != 2 or len(rows[0].split()) != len(expected):
        raise base.VerificationError('IRQ report lacks one entry and one return row')
    actual = {key: int(value, 16) for word in rows[0].split()
              for key, value in (word.split('=', 1),)}
    if actual != expected or values['hits'] != 1:
        raise base.VerificationError(f'IRQ entry differs: {actual}, {values}')
    return_values = {key: int(value, 16) for word in rows[1].split()
                     for key, value in (word.split('=', 1),)}
    if return_values != dict(returned=expected['accepted'], sp=values['expected_sp']):
        raise base.VerificationError(f'IRQ return report differs: {return_values}')
    if (values['saved_pc'] != expected['accepted'] or values['saved_sr'] != expected['sr']
            or values['handler_sr'] != ((expected['sr'] & ~0xF0) | level << 4)
            or values['after_sr'] != expected['sr'] or values['seen_value'] != 0x12345678):
        raise base.VerificationError(f'IRQ frame or RTE differs: {values}')
    if case in (1, 6, 29, 30) and values['seen_second'] != 0x89ABCDEF:
        raise base.VerificationError('IRQ observes an unfinished masked group')
    if case == 5 and values['seen_iterations'] != count:
        raise base.VerificationError(f'IRQ occurs at the wrong execution: {values}')
    if case == 33 and values['rte_sp'] != values['expected_sp']:
        raise base.VerificationError('RTE delay slot does not observe the restored stack pointer')
    if case == 34 and values['outer_resumed'] != 1:
        raise base.VerificationError('the surrounding GNU TRAPA does not return to its continuation')
    if case == 35 and values['trap_hits'] != 1:
        raise base.VerificationError('GNU TRAPA inside the injected handler does not return')
    if case == 0 and (values['after_r0'] != 0x12345678
                      or values['after_r1'] != addresses['_irq_value']):
        raise base.VerificationError('IRQ handler clobbers the interrupted registers')
    records = base.read_pc_trace(report.with_suffix('.trace'))
    handler = next(index for index, row in enumerate(records) if row[0] == expected['handler'])
    if sum(row[0] == expected['triggered'] for row in records[:handler]) != count:
        raise base.VerificationError('IRQ trace does not bind COUNT to completed instructions')
    returned = next(index for index in range(handler + 1, len(records))
                    if records[index][0] == expected['accepted'])
    slot = 0x21F2 if case == 33 else 0x0009
    if records[returned - 2][1] != 0x002B or records[returned - 1][1:] != (slot, 1):
        raise base.VerificationError('IRQ trace lacks RTE and its executed delay slot')
    if case in (34, 35):
        continuation = addresses['irq_outer_continuation' if case == 34 else 'irq_inner_continuation']
        resumed = next(index for index, row in enumerate(records) if row[0] == continuation)
        if (records[resumed - 2][1] != 0x002B or records[resumed - 1][1:] != (0x0009, 1)
                or sum(row[1] == 0x002B for row in records) != 2):
            raise base.VerificationError('GNU TRAPA return or its slot differs')
    print(f'VQ_SH_IRQ_CASE status=PASS name={name} count={count} '
          f'level={level} vector={vector} accepted={actual["accepted"]:08x} '
          'bytes_unchanged=true', flush=True)


def check_pending(elf, directory, name, *, count=1, level=8, code=125):
    report = directory / f'{name}.report'
    _, values = run_probe(elf, request_for(elf, report, count=count, level=level), code=code)
    if values['hits'] or report.read_text() != 'status=PENDING\n':
        raise base.VerificationError(f'undelivered IRQ does not fail closed: {name}')
    base.read_pc_trace(report.with_suffix('.trace'))
    print(f'VQ_SH_IRQ_CASE status=PASS name={name} expected_exit={code}', flush=True)
    return 1


def check_invalid(elf, directory):
    invalid = {
        'PC': ('', '-2', '+2', ' 2', '2junk', '1', '100000000'),
        'COUNT': ('', '0', '-1', '+1', ' 1', '1junk', '0x1', '18446744073709551616'),
        'LEVEL': ('', '0', '16', '-1', 'one', '1junk'),
        'VECTOR': ('', '-1', '256', 'one', '1junk'),
        'REPORT': ('', str(directory / 'absent' / 'irq.report')),
    }
    checked = 0
    for key, values in invalid.items():
        for value in (*values, None):
            request = request_for(elf, directory / f'invalid-{checked}.report')
            if value is None:
                request.pop(key)
            else:
                request[key] = value
            result = base.run_command([base.RUN, elf], env=environment(request),
                                      expected_returncode=125)
            if 'VQ_SH_IRQ error=' not in result.stderr or MARKER in result.stdout:
                raise base.VerificationError(f'invalid IRQ setting executes: {key}={value!r}')
            checked += 1
    request = request_for(elf, Path('/dev/full'))
    result = base.run_command([base.RUN, elf], env=environment(request),
                              expected_returncode=125)
    if 'VQ_SH_IRQ error=report_write' not in result.stderr or MARKER in result.stdout:
        raise base.VerificationError('IRQ report write failure does not stop execution')
    checked += 1
    return checked


def check_stack(elf, disabled):
    size = symbols(elf)['irq_stack_bytes']
    sp = disabled['expected_sp']
    if sp & 3 or size != 16 or sp < size:
        raise base.VerificationError('IRQ probe declares an invalid stack frame')
    require_separate_storage(elf, ((sp - size, size),))


def check_original_signal(directory):
    elf = compile_probe(directory, 28)
    code = int(signal.SIGILL)
    control, _ = run_probe(elf, code=code, terminal=False)
    report = directory / 'original_signal.report'
    injected, _ = run_probe(elf, request_for(elf, report), code=code, terminal=False)
    if report.read_text() != 'status=PENDING\n':
        raise base.VerificationError('faulting probe accepts an IRQ under the mask')
    for result in (control, injected):
        if f'signal {code}' not in result.stdout + result.stderr or MARKER in result.stdout:
            raise base.VerificationError('IRQ hook masks the original target signal')
    print(f'VQ_SH_IRQ_CASE status=PASS name=original_signal expected_signal={code}', flush=True)
    return 1


def check_unreturned(directory):
    cases = ((36, 0, 125), (36, 7, 7), (37, 0, int(signal.SIGILL)))
    for case, target_exit, expected_exit in cases:
        elf = compile_probe(directory, case, exit_code=target_exit)
        _, disabled = run_probe(elf, code=target_exit)
        check_stack(elf, disabled)
        report = directory / f'unreturned-{case}-{target_exit}.report'
        run_probe(elf, request_for(elf, report), code=expected_exit, terminal=False)
        rows = report.read_text().splitlines()
        if (not rows[0].startswith('triggered=') or rows[-1] != 'status=UNRETURNED'
                or len(rows) != (3 if case == 37 else 2)):
            raise base.VerificationError(f'IRQ exit without return is not explicit: {rows}')
        print(f'VQ_SH_IRQ_CASE status=PASS name=unreturned_{case}_{target_exit} '
              f'expected_exit={expected_exit}', flush=True)
    return len(cases)


def inhibit_variants():
    registers = {
        'ldc': ('sr', 'gbr', 'vbr'), 'stc': ('sr', 'gbr', 'vbr'),
        'lds': ('mach', 'macl', 'pr', 'fpul', 'fpscr'),
        'sts': ('mach', 'macl', 'pr', 'fpul', 'fpscr'),
    }
    for stem, names in registers.items():
        for register in names:
            for long in (False, True):
                instruction = stem + ('.l' if long else '')
                if stem.startswith('ld'):
                    instruction += f' {"@r1+" if long else "r0"},{register}'
                else:
                    instruction += f' {register},{"@-r1" if long else "r0"}'
                flags = [f'-DIRQ_INHIBIT={instruction}']
                if stem == 'ldc' and register == 'sr':
                    flags.append('-DIRQ_VALUE_SR=1')
                if stem == 'ldc' and register == 'vbr':
                    flags.append('-DIRQ_VALUE_VECTOR=1')
                if long and stem.startswith('st'):
                    flags.append('-DIRQ_PREDECREMENT=1')
                yield f'{stem}_{register}' + ('_long' if long else ''), flags


def verify():
    positive = 0
    with tempfile.TemporaryDirectory(prefix='vq-sh-irq-') as directory:
        directory = Path(directory)
        probes = {}
        for case in (*CASES, 4):
            elf = compile_probe(directory, case)
            probes[case] = elf
            digest = hashlib.sha256(elf.read_bytes()).hexdigest()
            _, disabled = run_probe(elf)
            if disabled['hits']:
                raise base.VerificationError('IRQ injection is enabled by default')
            check_stack(elf, disabled)
            if case in CASES:
                for count in ((2, 3, 5) if case == 5 else (1,)):
                    for level in {0: (1, 8, 10, 15), 31: (4,), 34: (10,)}.get(case, (8,)):
                        for vector in ((0, 80, 255) if case == 0 else (80,)):
                            check_positive(elf, directory, case, count, level, vector)
                            positive += 1
            if hashlib.sha256(elf.read_bytes()).hexdigest() != digest:
                raise base.VerificationError('disabled and enabled runs use different ELF bytes')
        for name, flags in inhibit_variants():
            elf = compile_probe(directory, 7, name=name, flags=flags)
            _, disabled = run_probe(elf)
            if disabled['hits']:
                raise base.VerificationError('IRQ injection is enabled by default')
            check_stack(elf, disabled)
            check_positive(elf, directory, 7, 1, 8, 80, name=name)
            positive += 1
        failed = compile_probe(directory, 0, exit_code=7)
        pending = sum((
            check_pending(probes[4], directory, 'masked_pending', level=15),
            check_pending(probes[0], directory, 'unreached_count', count=2),
            check_pending(probes[0], directory, 'maximum_count', count=(1 << 64) - 1),
            check_pending(failed, directory, 'original_exit_preserved', count=2, code=7),
            check_original_signal(directory),
        ))
        invalid = check_invalid(probes[0], directory)
        unreturned = check_unreturned(directory)
    print(f'VQ_SH_IRQ_VERIFY status=PASS default=off positive={positive} '
          f'pending={pending} invalid={invalid} unreturned={unreturned}')


if __name__ == '__main__':
    verify()
