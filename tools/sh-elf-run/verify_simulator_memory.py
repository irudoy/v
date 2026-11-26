"""Execute opt-in high-RAM alias, dual-bank/MMIO, default-off, and bus-error probes."""

import os
from pathlib import Path
import signal
import tempfile

import verify_map_switching as base
from elf_storage_layout import require_separate_storage


SOURCE = Path(__file__).with_name('harness-simulator-high-ram.c')
VARIABLE = 'VQ_SH_HIGH_RAM_BASE'
LAYOUT_VARIABLE = 'VQ_SH_HIGH_RAM_LAYOUT'
M95320_VARIABLE = 'VQ_SH_M95320_BASE'
ALIAS_BASE = 0x01000000
ALIAS_SIZE = 0x10000
M95320_BASE = 0x01010000
M95320_SIZE = 0x2000
DUAL_LOWER_BASE = 0x01020000
DUAL_LOWER_AND_MMIO_SIZE = 0x9000
ALIAS = f'{ALIAS_BASE:#x}'
# Legacy probe writes a canary immediately beyond the 64 KiB aliased window;
# dual-bank/MMIO probes also use M95320 [0x01010000, 0x01012000) and
# lower-bank + MMIO shadow [0x01020000, 0x01029000).
PROBE_RAM = (
    (ALIAS_BASE, ALIAS_SIZE),
    (M95320_BASE, M95320_SIZE),
    (DUAL_LOWER_BASE, DUAL_LOWER_AND_MMIO_SIZE),
)
PASS = 'VQ_SH_HIGH_RAM_PROBE status=PASS'
BUS_CODE = int(signal.SIGBUS)
BUS_ERROR = f'signal {BUS_CODE} (Bus error)'
INVALID = 'VQ_SH_HIGH_RAM error=invalid_base'
INVALID_LAYOUT = 'VQ_SH_HIGH_RAM error=invalid_layout'
OVERLAP = 'VQ_SH_HIGH_RAM error=overlap'
BAD_BASES = ('', '0', '-65536', '+65536', ' 65536', '0x1000001',
             '0x40000000', '0xffffffffffff0000',
             '9999999999999999999999999999999999999', '0x1000000junk')
BAD_LAYOUTS = ('', 'legacy', 'sh7058', 'sh7059', 'sh7059-mmio-extra')


def environment(value=None, *, layout=None, m95320_base=None):
    result = dict(os.environ)
    for name in (VARIABLE, LAYOUT_VARIABLE, M95320_VARIABLE):
        result.pop(name, None)
    if value is not None:
        result[VARIABLE] = value
    if layout is not None:
        result[LAYOUT_VARIABLE] = layout
    if m95320_base is not None:
        result[M95320_VARIABLE] = m95320_base
    return result


def require_result(
    elf,
    value=None,
    *,
    layout=None,
    m95320_base=None,
    code=0,
    marker=PASS,
    memory_args=(),
):
    cmd = [base.RUN, *memory_args, elf]
    result = base.run_command(
        cmd,
        env=environment(value, layout=layout, m95320_base=m95320_base),
        expected_returncode=code,
    )
    output = result.stdout + result.stderr
    if marker not in output:
        raise base.VerificationError(f'high-RAM probe lacks {marker!r}: {output}')


def verify():
    """Require actual access semantics; source patterns do not qualify the alias."""
    with tempfile.TemporaryDirectory(prefix='vq-sh-high-ram-') as directory:
        directory = Path(directory)
        probes = {}
        for case in range(19):
            elf = directory / f'probe-{case}.elf'
            base.run_command([base.GCC, '-m2e', '-mb', '-O1',
                              f'-DPROBE_CASE={case}', SOURCE, '-o', elf])
            require_separate_storage(elf, PROBE_RAM)
            probes[case] = elf
        # Legacy flat 64 KiB alias probes (layout unset).
        require_result(probes[0], ALIAS)
        for case in (0, 6, 7, 8, 9, 10):
            require_result(probes[case], code=BUS_CODE, marker=BUS_ERROR)
        for case in (1, 2, 3, 4, 5):
            require_result(probes[case], ALIAS, code=BUS_CODE, marker=BUS_ERROR)
        require_result(probes[11])
        require_result(probes[11], ALIAS)
        for value in BAD_BASES:
            require_result(probes[0], value, code=125, marker=INVALID)

        # Dual-bank + MMIO layout probes (sh7058-mmio and sh7059-mmio).
        dual_args = (
            '--memory-region', f'{ALIAS_BASE:#x},{ALIAS_SIZE:#x}',
            '--memory-region', f'{M95320_BASE:#x},{M95320_SIZE:#x}',
            '--memory-region', f'{DUAL_LOWER_BASE:#x},{DUAL_LOWER_AND_MMIO_SIZE:#x}',
        )
        require_result(probes[12], ALIAS, layout='sh7059-mmio', memory_args=dual_args)
        require_result(probes[13], ALIAS, layout='sh7058-mmio', memory_args=dual_args)
        # sh7058-mmio must fault on lower bank (0xFFFE8511).
        require_result(
            probes[5], ALIAS, layout='sh7058-mmio', memory_args=dual_args,
            code=BUS_CODE, marker=BUS_ERROR,
        )
        # Unmapped MMIO, wrong MMIO width, and below lower-bank base must fault.
        for case in (14, 15, 16, 17):
            require_result(
                probes[case], ALIAS, layout='sh7059-mmio', memory_args=dual_args,
                code=BUS_CODE, marker=BUS_ERROR,
            )
        for case in (14, 15, 16):
            require_result(
                probes[case], ALIAS, layout='sh7058-mmio', memory_args=dual_args,
                code=BUS_CODE, marker=BUS_ERROR,
            )
        # Real SCI2 + PCDR peripheral probe under sh7059-mmio with M95320 model.
        require_result(
            probes[18], ALIAS, layout='sh7059-mmio',
            m95320_base=f'{M95320_BASE:#x}', memory_args=dual_args,
        )
        # Invalid layout values, missing base with layout, and M95320 overlap.
        for bad_layout in BAD_LAYOUTS:
            require_result(
                probes[12], ALIAS, layout=bad_layout, memory_args=dual_args,
                code=125, marker=INVALID_LAYOUT,
            )
        require_result(
            probes[12], None, layout='sh7059-mmio', memory_args=dual_args,
            code=125, marker=INVALID,
        )
        for overlap_base in (f'{ALIAS_BASE:#x}', f'{DUAL_LOWER_BASE:#x}',
                             f'{DUAL_LOWER_BASE + 0x8000:#x}'):
            require_result(
                probes[12], ALIAS, layout='sh7059-mmio',
                m95320_base=overlap_base, memory_args=dual_args,
                code=125, marker=OVERLAP,
            )
    print('VQ_SH_HIGH_RAM_VERIFY status=PASS default=off '
          'layouts=legacy,sh7058-mmio,sh7059-mmio '
          'widths=8,16,32 endian=big misalignment=bus_error '
          f'invalid_bases={len(BAD_BASES)} invalid_layouts={len(BAD_LAYOUTS)}')


if __name__ == '__main__':
    verify()
