"""Execute opt-in high-RAM alias, default-off and original bus-error probes."""

import os
from pathlib import Path
import signal
import tempfile

import verify_map_switching as base


SOURCE = Path(__file__).with_name('harness-simulator-high-ram.c')
VARIABLE = 'VQ_SH_HIGH_RAM_BASE'
ALIAS = '0x01000000'
PASS = 'VQ_SH_HIGH_RAM_PROBE status=PASS'
BUS_CODE = int(signal.SIGBUS)
BUS_ERROR = f'signal {BUS_CODE} (Bus error)'
INVALID = 'VQ_SH_HIGH_RAM error=invalid_base'
BAD_BASES = ('', '0', '-65536', '+65536', ' 65536', '0x1000001',
             '0x40000000', '0xffffffffffff0000',
             '9999999999999999999999999999999999999', '0x1000000junk')


def environment(value=None):
    result = dict(os.environ)
    result.pop(VARIABLE, None)
    if value is not None:
        result[VARIABLE] = value
    return result


def require_result(elf, value=None, *, code=0, marker=PASS):
    result = base.run_command([base.RUN, elf], env=environment(value),
                              expected_returncode=code)
    output = result.stdout + result.stderr
    if marker not in output:
        raise base.VerificationError(f'high-RAM probe lacks {marker!r}: {output}')


def verify():
    """Require actual access semantics; source patterns do not qualify the alias."""
    with tempfile.TemporaryDirectory(prefix='vq-sh-high-ram-') as directory:
        directory = Path(directory)
        probes = {}
        for case in range(12):
            elf = directory / f'probe-{case}.elf'
            base.run_command([base.GCC, '-m2e', '-mb', '-O1',
                              f'-DPROBE_CASE={case}', SOURCE, '-o', elf])
            probes[case] = elf
        require_result(probes[0], ALIAS)
        for case in (0, 6, 7, 8, 9, 10):
            require_result(probes[case], code=BUS_CODE, marker=BUS_ERROR)
        for case in (1, 2, 3, 4, 5):
            require_result(probes[case], ALIAS, code=BUS_CODE, marker=BUS_ERROR)
        require_result(probes[11])
        require_result(probes[11], ALIAS)
        for value in BAD_BASES:
            require_result(probes[0], value, code=125, marker=INVALID)
    print('VQ_SH_HIGH_RAM_VERIFY status=PASS default=off '
          'widths=8,16,32 endian=big misalignment=bus_error '
          f'invalid_bases={len(BAD_BASES)}')


if __name__ == '__main__':
    verify()
