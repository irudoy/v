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
M95320_SCI2_VARIABLE = 'VQ_SH_M95320_SCI2_BASE'
M95320_CS_ADDR_VARIABLE = 'VQ_SH_M95320_CS_ADDR'
M95320_CS_MASK_VARIABLE = 'VQ_SH_M95320_CS_MASK'
SIM_ENV_VARS = (
    VARIABLE,
    LAYOUT_VARIABLE,
    M95320_VARIABLE,
    M95320_SCI2_VARIABLE,
    M95320_CS_ADDR_VARIABLE,
    M95320_CS_MASK_VARIABLE,
    'VQ_SH_PC_TRACE_FILE',
    'VQ_SH_PC_TRACE_FORMAT',
    'VQ_SH_PC_TRACE_RANGES',
)
ALIAS_BASE = 0x01000000
ALIAS_SIZE = 0x10000
M95320_BASE = 0x01010000
M95320_SIZE = 0x2000
DUAL_LOWER_BASE = 0x01020000
SH7058_DUAL_SIZE = 0x9000
DUAL_LOWER_AND_MMIO_SIZE = 0xA000
ALIAS = f'{ALIAS_BASE:#x}'
# Legacy probe writes a canary immediately beyond the 64 KiB aliased window;
# dual-bank/MMIO probes also use M95320 [0x01010000, 0x01012000) and
# lower-bank + MMIO + DMAC shadow [0x01020000, 0x0102A000).
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
M95320_INVALID_BASE = 'VQ_SH_M95320 error=invalid_base'
M95320_INVALID_REMAP = 'VQ_SH_M95320 error=invalid_remap'
BAD_BASES = ('', '0', '-65536', '+65536', ' 65536', '0x1000001',
             '0x40000000', '0xffff0000', '0x100000000',
             '0xffffffffffff0000',
             '9999999999999999999999999999999999999', '0x1000000junk')
BAD_LAYOUTS = ('', 'legacy', 'sh7058', 'sh7059', 'sh7059-mmio-extra')

FIRST_ACCESS_STUBS = {
    'ssr2_read': (
        '.text\n.global _start\n_start:\n'
        '    mov #-16,r4\n'
        '    shll8 r4\n'
        '    add #0x14,r4\n'
        '    mov.b @r4,r0\n'
        '    mov #1,r4\n'
        '    mov #0,r5\n'
        '    trapa #34\n'
        '    nop\n'
    ),
    'tdr2_write': (
        '.text\n.global _start\n_start:\n'
        '    mov #-16,r4\n'
        '    shll8 r4\n'
        '    add #0x13,r4\n'
        '    mov #6,r0\n'
        '    mov.b r0,@r4\n'
        '    mov #1,r4\n'
        '    mov #0,r5\n'
        '    trapa #34\n'
        '    nop\n'
    ),
    'pcdr_write': (
        '.text\n.global _start\n_start:\n'
        '    mov #-9,r4\n'
        '    shll8 r4\n'
        '    add #0x3e,r4\n'
        '    mov #0,r0\n'
        '    mov.w r0,@r4\n'
        '    mov #1,r4\n'
        '    mov #0,r5\n'
        '    trapa #34\n'
        '    nop\n'
    ),
}


def environment(value=None, *, layout=None, m95320_base=None, extra_env=None):
    result = dict(os.environ)
    for name in SIM_ENV_VARS:
        result.pop(name, None)
    if value is not None:
        result[VARIABLE] = value
    if layout is not None:
        result[LAYOUT_VARIABLE] = layout
    if m95320_base is not None:
        result[M95320_VARIABLE] = m95320_base
    if extra_env:
        result.update(extra_env)
    return result


def require_result(
    elf,
    value=None,
    *,
    layout=None,
    m95320_base=None,
    extra_env=None,
    code=0,
    marker=PASS,
    memory_args=(),
):
    cmd = [base.RUN, *memory_args, elf]
    result = base.run_command(
        cmd,
        env=environment(
            value, layout=layout, m95320_base=m95320_base, extra_env=extra_env
        ),
        expected_returncode=code,
    )
    output = result.stdout + result.stderr
    if marker not in output:
        raise base.VerificationError(f'high-RAM probe lacks {marker!r}: {output}')


def build_first_access_stubs(directory):
    """Build bare-metal first-data-access stubs with no C runtime prologue."""
    stubs = {}
    for name, asm_text in FIRST_ACCESS_STUBS.items():
        asm_path = directory / f'first-{name}.s'
        obj_path = directory / f'first-{name}.o'
        elf_path = directory / f'first-{name}.elf'
        asm_path.write_text(asm_text, encoding='ascii')
        base.run_command([base.AS, '--big', '--isa=sh2e', '-o', obj_path, asm_path])
        base.run_command([
            base.GCC, '-m2e', '-mb', '-nostdlib', '-e', '_start',
            '-Wl,-Ttext-segment=0x1000', '-o', elf_path, obj_path,
        ])
        require_separate_storage(elf_path, PROBE_RAM)
        nm_out = base.run_command([base.NM, '--defined-only', elf_path]).stdout
        start_addr = None
        for line in nm_out.splitlines():
            parts = line.split()
            if len(parts) >= 3 and parts[2] == '_start':
                start_addr = int(parts[0], 16)
                break
        if start_addr is None:
            raise base.VerificationError(f'first-access stub {name} lacks _start symbol')
        stubs[name] = (elf_path, start_addr)
    return stubs


def verify():
    """Require actual access semantics; source patterns do not qualify the alias."""
    with tempfile.TemporaryDirectory(prefix='vq-sh-high-ram-') as directory:
        directory = Path(directory)
        probes = {}
        for case in range(26):
            elf = directory / f'probe-{case}.elf'
            base.run_command([base.GCC, '-m2e', '-mb', '-O1',
                              f'-DPROBE_CASE={case}', SOURCE, '-o', elf])
            require_separate_storage(elf, PROBE_RAM)
            probes[case] = elf
        first_stubs = build_first_access_stubs(directory)

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

        # Legacy overlap (EEPROM inside flat 64 KiB alias) and EEPROM without alias.
        require_result(
            probes[0], ALIAS, m95320_base=f'{ALIAS_BASE + 0xE000:#x}',
            code=125, marker=OVERLAP,
        )
        require_result(
            probes[11], None, m95320_base=f'{M95320_BASE:#x}',
            code=125, marker=M95320_INVALID_BASE,
        )

        # Dual-bank + MMIO layout probes (sh7058-mmio and sh7059-mmio).
        sh7059_args = (
            '--memory-region', f'{ALIAS_BASE:#x},{ALIAS_SIZE:#x}',
            '--memory-region', f'{M95320_BASE:#x},{M95320_SIZE:#x}',
            '--memory-region', f'{DUAL_LOWER_BASE:#x},{DUAL_LOWER_AND_MMIO_SIZE:#x}',
        )
        sh7058_args = (
            '--memory-region', f'{ALIAS_BASE:#x},{ALIAS_SIZE:#x}',
            '--memory-region', f'{M95320_BASE:#x},{M95320_SIZE:#x}',
            '--memory-region', f'{DUAL_LOWER_BASE:#x},{SH7058_DUAL_SIZE:#x}',
        )
        require_result(probes[12], ALIAS, layout='sh7059-mmio', memory_args=sh7059_args)
        require_result(probes[13], ALIAS, layout='sh7058-mmio', memory_args=sh7058_args)
        # Adjacent-disjoint EEPROM at [B+0x0C000, B+0x0E000) passes split layouts.
        require_result(
            probes[12], ALIAS, layout='sh7059-mmio',
            m95320_base=f'{ALIAS_BASE + 0xC000:#x}', memory_args=sh7059_args,
        )
        # sh7058-mmio must fault on lower bank (0xFFFE8511), DMAC, and ADC.
        for case in (5, 14, 15, 16, 19, 20, 21, 22, 23, 24, 25):
            require_result(
                probes[case], ALIAS, layout='sh7058-mmio',
                m95320_base=f'{M95320_BASE:#x}', memory_args=sh7058_args,
                code=BUS_CODE, marker=BUS_ERROR,
            )
        # sh7059-mmio must fault on unmapped MMIO, wrong width/direction, split hole,
        # below lower bank, and unapproved DMAC/ADC.
        for case in (14, 15, 16, 17, 19, 20, 21, 22, 23, 24, 25):
            require_result(
                probes[case], ALIAS, layout='sh7059-mmio',
                m95320_base=f'{M95320_BASE:#x}', memory_args=sh7059_args,
                code=BUS_CODE, marker=BUS_ERROR,
            )
        # Real SCI2 + PCDR peripheral probe under sh7059-mmio with M95320 model.
        require_result(
            probes[18], ALIAS, layout='sh7059-mmio',
            m95320_base=f'{M95320_BASE:#x}',
            extra_env={
                M95320_SCI2_VARIABLE: '0xfffff010',
                M95320_CS_ADDR_VARIABLE: '0xfffff73e',
                M95320_CS_MASK_VARIABLE: '0x0010',
            },
            memory_args=sh7059_args,
        )
        # Invalid layout values, missing base with layout, invalid remaps, and overlaps.
        for bad_layout in BAD_LAYOUTS:
            require_result(
                probes[12], ALIAS, layout=bad_layout, memory_args=sh7059_args,
                code=125, marker=INVALID_LAYOUT,
            )
        require_result(
            probes[12], None, layout='sh7059-mmio', memory_args=sh7059_args,
            code=125, marker=INVALID,
        )
        for bad_remap in (
            {M95320_SCI2_VARIABLE: '0xfffff020'},
            {M95320_CS_ADDR_VARIABLE: '0xfffff73c'},
            {M95320_CS_MASK_VARIABLE: '0x0020'},
        ):
            require_result(
                probes[18], ALIAS, layout='sh7059-mmio',
                m95320_base=f'{M95320_BASE:#x}', extra_env=bad_remap,
                memory_args=sh7059_args, code=125, marker=M95320_INVALID_REMAP,
            )
        # Explicit empty, signed, junk, or overflowing device tuple overrides must fail.
        for var_name in (
            M95320_SCI2_VARIABLE,
            M95320_CS_ADDR_VARIABLE,
            M95320_CS_MASK_VARIABLE,
        ):
            for bad_val in ('', '-1', '+16', '0xfffff010junk', '0x100000000'):
                require_result(
                    probes[18], ALIAS, layout='sh7059-mmio',
                    m95320_base=f'{M95320_BASE:#x}',
                    extra_env={var_name: bad_val},
                    memory_args=sh7059_args, code=125,
                    marker=f'VQ_SH_M95320 error=invalid_{var_name}',
                )
        for overlap_base in (
            f'{ALIAS_BASE:#x}',
            f'{ALIAS_BASE + 0xB000:#x}',
            f'{DUAL_LOWER_BASE:#x}',
            f'{DUAL_LOWER_BASE + 0x8000:#x}',
            f'{DUAL_LOWER_BASE + 0x9000:#x}',
        ):
            require_result(
                probes[12], ALIAS, layout='sh7059-mmio',
                m95320_base=overlap_base, memory_args=sh7059_args,
                code=125, marker=OVERLAP,
            )

        # First-data-access SSR2/TDR2/PCDR stubs:
        # 1) Positive control proves the bound _start range observes the entry and access PCs.
        # 2) Every invalid config exits 125 in eager preflight with flushed header and 0 PC lines.
        preflight_cases = (
            ('bad_layout', ALIAS, 'invalid', f'{M95320_BASE:#x}', {}, sh7059_args, INVALID_LAYOUT),
            ('short_backing', '0x3ffe0000', 'sh7059-mmio', f'{M95320_BASE:#x}', {}, sh7059_args, INVALID),
            ('short_m95320', ALIAS, 'sh7059-mmio', '0x3ffff000', {}, sh7059_args, M95320_INVALID_BASE),
            ('overlap_upper', ALIAS, 'sh7059-mmio', f'{ALIAS_BASE + 0xB000:#x}', {}, sh7059_args, OVERLAP),
            ('bad_remap', ALIAS, 'sh7059-mmio', f'{M95320_BASE:#x}', {M95320_SCI2_VARIABLE: '0xfffff020'}, sh7059_args, M95320_INVALID_REMAP),
        )
        for stub_name, (stub_elf, start_addr) in first_stubs.items():
            trace_range = f'{start_addr:x}:{start_addr + 0x40:x}'
            ok_trace = directory / f'preflight-{stub_name}-ok.trace'
            require_result(
                stub_elf, ALIAS, layout='sh7059-mmio',
                m95320_base=f'{M95320_BASE:#x}',
                extra_env={
                    'VQ_SH_PC_TRACE_FILE': str(ok_trace),
                    'VQ_SH_PC_TRACE_FORMAT': 'v1',
                    'VQ_SH_PC_TRACE_RANGES': trace_range,
                },
                code=0, marker='', memory_args=sh7059_args,
            )
            ok_records = base.read_pc_trace(ok_trace)
            if ok_records[0][0] != start_addr:
                raise base.VerificationError(
                    f'positive control {stub_name} first PC {ok_records[0][0]:#x} != _start {start_addr:#x}'
                )
            for case_name, base_val, lay_val, m_val, extra, mem_args, expected_err in preflight_cases:
                trace_file = directory / f'preflight-{stub_name}-{case_name}.trace'
                env_extra = {
                    **extra,
                    'VQ_SH_PC_TRACE_FILE': str(trace_file),
                    'VQ_SH_PC_TRACE_FORMAT': 'v1',
                    'VQ_SH_PC_TRACE_RANGES': trace_range,
                }
                require_result(
                    stub_elf, base_val, layout=lay_val, m95320_base=m_val,
                    extra_env=env_extra, code=125, marker=expected_err,
                    memory_args=mem_args,
                )
                if not trace_file.exists():
                    raise base.VerificationError(
                        f'preflight {stub_name}/{case_name} did not open PC trace file'
                    )
                lines = trace_file.read_text(encoding='ascii').splitlines()
                if not lines or lines[0] != 'VQ_SH_PC_TRACE version=1':
                    raise base.VerificationError(
                        f'preflight {stub_name}/{case_name} lacks flushed trace header'
                    )
                pc_lines = [line for line in lines if line.startswith('pc=')]
                if pc_lines:
                    raise base.VerificationError(
                        f'preflight {stub_name}/{case_name} executed guest instructions: {pc_lines[0]}'
                    )

    print('VQ_SH_HIGH_RAM_VERIFY status=PASS default=off '
          'layouts=legacy,sh7058-mmio,sh7059-mmio '
          'widths=8,16,32 endian=big misalignment=bus_error '
          f'invalid_bases={len(BAD_BASES)} invalid_layouts={len(BAD_LAYOUTS)} '
          f'first_access_preflight={len(FIRST_ACCESS_STUBS) * len(preflight_cases)}')


if __name__ == '__main__':
    verify()
