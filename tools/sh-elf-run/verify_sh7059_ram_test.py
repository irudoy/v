"""Execute 24 stock SH7059 Service 0xA0/01 RAM-test iterations over Package 3 RAM."""

from __future__ import annotations

import os
from pathlib import Path

import verify_map_switching as base
import verify_runtime_targets as rt
from elf_storage_layout import ELFStorageError, require_separate_storage


TOOL_DIR = Path(__file__).resolve().parent
HARNESS_C = TOOL_DIR / "harness-sh7059-ram-test.c"
IRQ_ASM = TOOL_DIR / "sh7059_ram_test_irq.s"
EXPECTED_PASS = "VQ_SH_ELF_SH7059_RAM_TEST status=PASS cases=4 words=24 irq_hits=1"

# Exact stock Service 0xA0/01 witnesses per SH7059 layout family.
SPECS_BY_ROM = {
    "1ND0A": dict(
        entry=0x12604C,
        mode_cmp_pc=0x126314,
        chcr0_pc=0x126342,
        chcr1_pc=0x12636C,
        chcr2_pc=0x126378,
        cursor_addr=0xFFFEA3DC,
        ext_start=0xFFFF0F60,
        ext_end=0xFFFF0FC0,
        pattern_55_pc=0x1263EC,
        pattern_aa_pc=0x126434,
        restore_match_pc=0x12647A,
        unmask_pc=0x126480,
        expected_accept_pc=0x126484,
        cursor_store_pc=0x12648C,
        cursor_store_word=0xC2FB,
        chcr0_poll_pc=0x126490,
        return_pc=0x1270AC,
        completion_addr=0xFFFEB883,
        completion_mask=0x04,
        epilogue_clr0=(0xFFFEB826, 0x10),
        epilogue_clr1=(0xFFFEB834, 0x02),
        epilogue_clr2=(0xFFFEB817, 0x20),
        epilogue_clr3=(0x00000000, 0x00),
    ),
    "1ME3B": dict(
        entry=0x13339C,
        mode_cmp_pc=0x133664,
        chcr0_pc=0x133692,
        chcr1_pc=0x1336BC,
        chcr2_pc=0x1336C8,
        cursor_addr=0xFFFEA49C,
        ext_start=0xFFFF0F00,
        ext_end=0xFFFF0F60,
        pattern_55_pc=0x13373C,
        pattern_aa_pc=0x133784,
        restore_match_pc=0x1337CA,
        unmask_pc=0x1337D0,
        expected_accept_pc=0x1337D4,
        cursor_store_pc=0x1337DC,
        cursor_store_word=0xC2FC,
        chcr0_poll_pc=0x1337E0,
        return_pc=0x13441E,
        completion_addr=0xFFFEB9EB,
        completion_mask=0x80,
        epilogue_clr0=(0xFFFEB988, 0x02),
        epilogue_clr1=(0xFFFEB999, 0x40),
        epilogue_clr2=(0xFFFEB977, 0x20),
        epilogue_clr3=(0x00000000, 0x00),
    ),
    "1EK7A": dict(
        entry=0x154458,
        mode_cmp_pc=0x154720,
        chcr0_pc=0x154750,
        chcr1_pc=0x15477A,
        chcr2_pc=0x154786,
        cursor_addr=0xFFFEA67C,
        ext_start=0xFFFF5900,
        ext_end=0xFFFF5960,
        pattern_55_pc=0x1547FC,
        pattern_aa_pc=0x154848,
        restore_match_pc=0x154892,
        unmask_pc=0x154898,
        expected_accept_pc=0x15489C,
        cursor_store_pc=0x1548A4,
        cursor_store_word=0xC21D,
        chcr0_poll_pc=0x1548A8,
        return_pc=0x155526,
        completion_addr=0xFFFEBD89,
        completion_mask=0x04,
        epilogue_clr0=(0xFFFEBD2E, 0x04),
        epilogue_clr1=(0xFFFEBD18, 0x01),
        epilogue_clr2=(0xFFFEBD05, 0x20),
        epilogue_clr3=(0x00000000, 0x00),
    ),
}
SPECS_BY_ROM["1ND3B"] = SPECS_BY_ROM["1ND0A"]


def _require_stock_witnesses(rom, stock, composed, fixture, spec, target):
    """Pin the full executed stock 0xA0/01 span and opcodes across stock, composed, and fixture."""
    cf_ram = target.map_layout.cruise_free.ram
    ee_ram = target.map_layout.eeprom_persistence.ram
    if cf_ram.start != spec["ext_start"] or cf_ram.end != ee_ram.start or ee_ram.end != spec["ext_end"]:
        raise rt.VerificationError(
            f"{rom}: 0xA0/01 extension span [{spec['ext_start']:#x}, {spec['ext_end']:#x}) "
            f"differs from layout CF/EE RAM [{cf_ram.start:#x}, {ee_ram.end:#x})"
        )
    span_start = spec["entry"]
    span_end = spec["return_pc"] + 4
    if stock[span_start:span_end] != composed[span_start:span_end]:
        raise rt.VerificationError(
            f"{rom}: composed image alters stock 0xA0/01 service [{span_start:#x}, {span_end:#x})"
        )
    if fixture[span_start:span_end] != stock[span_start:span_end]:
        raise rt.VerificationError(
            f"{rom}: simulator fixture alters stock 0xA0/01 service [{span_start:#x}, {span_end:#x})"
        )
    expected_words = (
        (spec["mode_cmp_pc"], 0x8801),
        (spec["chcr0_pc"], 0x5063),
        (spec["chcr1_pc"], 0x5053),
        (spec["chcr2_pc"], 0x5043),
        (spec["pattern_55_pc"], 0x2D82),
        (spec["pattern_aa_pc"], 0x2D72),
        (spec["restore_match_pc"], 0x2D22),
        (spec["unmask_pc"], 0x4D0E),
        (spec["cursor_store_pc"], spec["cursor_store_word"]),
        (spec["chcr0_poll_pc"], 0x5063),
        (spec["return_pc"], 0x000B),
    )
    for pc, expected_word in expected_words:
        actual_word = int.from_bytes(fixture[pc : pc + 2], "big")
        if actual_word != expected_word:
            raise rt.VerificationError(
                f"{rom}: 0xA0/01 witness at {pc:#x} is {actual_word:04x}, expected {expected_word:04x}"
            )


def _write_header(rom, spec, build_dir):
    header = build_dir / f"{rom.lower()}-a001-bindings.h"
    lines = [
        f"#define A001_ENTRY 0x{spec['entry']:08x}U",
        f"#define A001_CURSOR_ADDR 0x{spec['cursor_addr']:08x}U",
        f"#define A001_EXT_START 0x{spec['ext_start']:08x}U",
        f"#define A001_EXT_END 0x{spec['ext_end']:08x}U",
        f"#define A001_COMPLETION_ADDR 0x{spec['completion_addr']:08x}U",
        f"#define A001_COMPLETION_MASK 0x{spec['completion_mask']:02x}U",
        f"#define A001_EPILOGUE_CLR0_ADDR 0x{spec['epilogue_clr0'][0]:08x}U",
        f"#define A001_EPILOGUE_CLR0_MASK 0x{spec['epilogue_clr0'][1]:02x}U",
        f"#define A001_EPILOGUE_CLR1_ADDR 0x{spec['epilogue_clr1'][0]:08x}U",
        f"#define A001_EPILOGUE_CLR1_MASK 0x{spec['epilogue_clr1'][1]:02x}U",
        f"#define A001_EPILOGUE_CLR2_ADDR 0x{spec['epilogue_clr2'][0]:08x}U",
        f"#define A001_EPILOGUE_CLR2_MASK 0x{spec['epilogue_clr2'][1]:02x}U",
        f"#define A001_EPILOGUE_CLR3_ADDR 0x{spec['epilogue_clr3'][0]:08x}U",
        f"#define A001_EPILOGUE_CLR3_MASK 0x{spec['epilogue_clr3'][1]:02x}U",
    ]
    header.write_text("\n".join(lines) + "\n", encoding="ascii")
    return header.name


def _bind_elf_and_handler(rom, elf, irq_obj, fixture, work):
    """Bind the linked ELF .rom section and IRQ handler bytes against their inputs."""
    rom_dump = work / f"{rom.lower()}-a001.rom.raw"
    text_dump = work / f"{rom.lower()}-a001.text.raw"
    irq_dump = work / f"{rom.lower()}-a001-irq.text.raw"
    base.run_command([base.OBJCOPY, "-O", "binary", "--only-section=.rom", elf, rom_dump])
    if rom_dump.read_bytes() != fixture:
        raise rt.VerificationError(f"{rom}: linked 0xA0/01 ELF .rom differs from fixture")
    base.run_command([base.OBJCOPY, "-O", "binary", "--only-section=.text", elf, text_dump])
    base.run_command([base.OBJCOPY, "-O", "binary", "--only-section=.text", irq_obj, irq_dump])

    text_vma = None
    for line in base.run_command([base.OBJDUMP, "-h", elf]).stdout.splitlines():
        fields = line.split()
        if len(fields) > 4 and fields[1] == ".text":
            text_vma = int(fields[3], 16)
            break
    if text_vma is None:
        raise rt.VerificationError(f"{rom}: linked 0xA0/01 ELF lacks .text section")

    elf_syms = {}
    for line in base.run_command([base.NM, "-S", "--defined-only", elf]).stdout.splitlines():
        parts = line.split()
        if len(parts) == 4 and parts[3] == "_a001_irq_handler":
            elf_syms[parts[3]] = (int(parts[0], 16), int(parts[1], 16))
    obj_syms = {}
    for line in base.run_command([base.NM, "-S", "--defined-only", irq_obj]).stdout.splitlines():
        parts = line.split()
        if len(parts) == 4 and parts[3] == "_a001_irq_handler":
            obj_syms[parts[3]] = (int(parts[0], 16), int(parts[1], 16))
    if "_a001_irq_handler" not in elf_syms or "_a001_irq_handler" not in obj_syms:
        raise rt.VerificationError(f"{rom}: 0xA0/01 ELF lacks _a001_irq_handler symbol")
    handler_addr, handler_size = elf_syms["_a001_irq_handler"]
    obj_off, obj_size = obj_syms["_a001_irq_handler"]
    if handler_size != obj_size or handler_size < 16 or handler_size % 2 != 0:
        raise rt.VerificationError(f"{rom}: _a001_irq_handler size mismatch")
    text_bytes = text_dump.read_bytes()
    linked_handler = text_bytes[handler_addr - text_vma : handler_addr - text_vma + handler_size]
    obj_handler = irq_dump.read_bytes()[obj_off : obj_off + obj_size]
    # Compare instruction prefix up to the 4 relocated 32-bit literal pool entries.
    code_prefix = handler_size - 16
    if linked_handler[:code_prefix] != obj_handler[:code_prefix]:
        raise rt.VerificationError(f"{rom}: linked _a001_irq_handler instructions differ")
    handler_words = {
        handler_addr + off: int.from_bytes(linked_handler[off : off + 2], "big")
        for off in range(0, code_prefix, 2)
    }
    rte_pcs = [pc for pc, word in handler_words.items() if word == 0x002B]
    if len(rte_pcs) != 1:
        raise rt.VerificationError(f"{rom}: _a001_irq_handler must contain exactly one RTE")
    return handler_addr, handler_size, handler_words, rte_pcs[0]


def _require_sweep_trace_and_irq(
    rom, records, report_path, spec, fixture, handler_addr, handler_words, rte_pc, expected_words
):
    """Require bound opcodes, 3 DMA deferrals, exact ordered iterations, and deferred IRQ."""
    report_lines = report_path.read_text(encoding="ascii").splitlines()
    if len(report_lines) != 2:
        raise rt.VerificationError(f"{rom}: 0xA0/01 IRQ report lacks entry and return rows")
    entry_row = {
        k: int(v, 16)
        for item in report_lines[0].split()
        for k, v in (item.split("=", 1),)
    }
    ret_row = {
        k: int(v, 16)
        for item in report_lines[1].split()
        for k, v in (item.split("=", 1),)
    }
    if (
        entry_row.get("triggered") != spec["pattern_55_pc"]
        or entry_row.get("accepted") != spec["expected_accept_pc"]
        or entry_row.get("handler") != handler_addr
        or (entry_row.get("sr", 0xF0) & 0xF0) != 0
        or ret_row.get("returned") != spec["expected_accept_pc"]
        or (ret_row.get("sp", 1) & 3) != 0
    ):
        raise rt.VerificationError(
            f"{rom}: 0xA0/01 IRQ delivery differs: entry={entry_row} return={ret_row}"
        )

    # Bind every traced record's opcode and delay flag against fixture / IRQ handler bytes.
    for index, (pc, word, delay) in enumerate(records):
        if pc in handler_words:
            expected_word = handler_words[pc]
        elif pc < len(fixture) - 1:
            expected_word = int.from_bytes(fixture[pc : pc + 2], "big")
        else:
            raise rt.VerificationError(f"{rom}: 0xA0/01 traced PC outside bound code: {pc:#010x}")
        if word != expected_word:
            raise rt.VerificationError(
                f"{rom}: 0xA0/01 traced opcode differs at {pc:#010x}: {word:04x} != {expected_word:04x}"
            )
        if delay and (index == 0 or records[index - 1][0] != pc - 2 or records[index - 1][2]):
            raise rt.VerificationError(f"{rom}: 0xA0/01 orphan delay slot at {pc:#010x}")

    # Split the full trace into per-invocation windows [entry .. return_pc].
    invocations = []
    idx = 0
    while idx < len(records):
        if records[idx][0] == spec["entry"] and not records[idx][2]:
            end = idx + 1
            while end < len(records) and not (records[end][0] == spec["return_pc"] and not records[end][2]):
                end += 1
            if end >= len(records):
                raise rt.VerificationError(f"{rom}: 0xA0/01 invocation never reached return {spec['return_pc']:#010x}")
            invocations.append(records[idx : end + 1])
            idx = end + 1
        else:
            idx += 1

    if len(invocations) != 4:
        raise rt.VerificationError(
            f"{rom}: expected 4 0xA0/01 invocations (3 DMA deferrals + 1 sweep), got {len(invocations)}"
        )

    sweep_events = {
        spec["pattern_55_pc"],
        spec["pattern_aa_pc"],
        spec["restore_match_pc"],
        spec["unmask_pc"],
        spec["cursor_store_pc"],
        spec["chcr0_poll_pc"],
        handler_addr,
        rte_pc,
    }

    # Invocations 0..2: CHCR0.DE, CHCR1.DE, CHCR2.DE deferrals with zero pattern/IRQ events.
    defer_targets = (
        (spec["chcr0_pc"],),
        (spec["chcr0_pc"], spec["chcr1_pc"]),
        (spec["chcr0_pc"], spec["chcr1_pc"], spec["chcr2_pc"]),
    )
    for defer_idx, required_checks in enumerate(defer_targets):
        pcs = [pc for pc, _word, delay in invocations[defer_idx] if not delay]
        if set(pcs) & sweep_events:
            raise rt.VerificationError(
                f"{rom}: DMA deferral {defer_idx} unexpectedly entered pattern/IRQ window"
            )
        observed_chcr = [
            pc for pc in pcs if pc in (spec["chcr0_pc"], spec["chcr1_pc"], spec["chcr2_pc"])
        ]
        if tuple(observed_chcr) != required_checks:
            raise rt.VerificationError(
                f"{rom}: DMA deferral {defer_idx} CHCR sequence {[hex(p) for p in observed_chcr]} "
                f"!= {[hex(p) for p in required_checks]}"
            )

    # Invocation 3: exact expected_words iterations in strict order, IRQ ONLY after final restore+unmask.
    sweep_pcs = [
        pc for pc, _word, delay in invocations[3] if not delay and pc in sweep_events
    ]
    expected_seq = []
    for word_idx in range(expected_words):
        expected_seq.extend((
            spec["pattern_55_pc"],
            spec["pattern_aa_pc"],
            spec["restore_match_pc"],
            spec["unmask_pc"],
        ))
        if word_idx == expected_words - 1:
            expected_seq.extend((handler_addr, rte_pc))
        expected_seq.extend((
            spec["cursor_store_pc"],
            spec["chcr0_poll_pc"],
        ))
    if sweep_pcs != expected_seq:
        raise rt.VerificationError(
            f"{rom}: 0xA0/01 sweep event sequence differs for {expected_words} words "
            f"(got {len(sweep_pcs)} events, expected {len(expected_seq)})"
        )


def verify(target, map_fixture, composed_image, build_dir):
    """Run positive 24-word sweep + negative COUNT=23 early-stop control on SH7059."""
    rom = target.rom
    if rom not in SPECS_BY_ROM:
        raise rt.VerificationError(f"{rom}: unsupported ROM for SH7059 0xA0/01 gate")
    spec = SPECS_BY_ROM[rom]
    _require_stock_witnesses(
        rom, target.stock_image.data, composed_image, map_fixture, spec, target
    )

    work = Path(build_dir) / f"{rom.lower()}-a001"
    work.mkdir()
    header_name = _write_header(rom, spec, work)
    rom_obj = rt._build_rom_object(f"{rom}-a001", map_fixture, work)
    invoke_obj = work / "invoke.o"
    irq_obj = work / "a001-irq.o"
    base.run_command([base.AS, "--big", "--isa=sh2e", "-o", invoke_obj, TOOL_DIR / "invoke.s"])
    base.run_command([base.AS, "--big", "--isa=sh2e", "-o", irq_obj, IRQ_ASM])

    elf = work / f"{rom.lower()}-a001.elf"
    driver_text_base = max(base.DRIVER_TEXT_BASE, len(target.stock_image.data) + 0x10000)
    base.run_command([
        base.GCC, "-m2e", "-mb", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
        "-I", work, f'-DA001_BINDINGS_HEADER="{header_name}"',
        f"-Wl,-Ttext-segment={driver_text_base:#x}",
        "-Wl,--section-start=.rom=0",
        "-o", elf, HARNESS_C, invoke_obj, irq_obj, rom_obj,
    ], timeout=120)

    storage_regions = (
        (base.TEST_RAM_BASE, 65536),
        (base.M95320_BASE, base.M95320_SIZE),
        (rt.DUAL_BANK_MMIO_BASE, rt.SH7059_DUAL_BANK_MMIO_SIZE),
    )
    try:
        require_separate_storage(elf, storage_regions)
    except (ELFStorageError, OSError) as error:
        raise rt.VerificationError(f"{rom}.a001: ELF storage separation: {error}") from error

    handler_addr, handler_size, handler_words, rte_pc = _bind_elf_and_handler(
        rom, elf, irq_obj, map_fixture, work
    )
    trace_ranges = (
        f"{spec['entry']:x}:{spec['return_pc'] + 4:x},"
        f"{handler_addr:x}:{handler_addr + handler_size:x}"
    )

    def run_once(tag, count, *, expected_rc=0):
        trace = work / f"{tag}.pc-trace"
        report = work / f"{tag}.irq-report"
        env = rt._simulator_env(
            os.environ,
            trace_file=trace,
            trace_ranges=trace_ranges,
            dual_bank_mmio=True,
            sim_layout="sh7059-mmio",
            eeprom_layout=target.map_layout.eeprom_persistence,
        )
        env.update({
            "VQ_SH_IRQ_PC": f"{spec['pattern_55_pc']:x}",
            "VQ_SH_IRQ_COUNT": str(count),
            "VQ_SH_IRQ_LEVEL": "8",
            "VQ_SH_IRQ_VECTOR": "80",
            "VQ_SH_IRQ_REPORT": str(report),
        })
        cmd = [
            base.RUN,
            f"--memory-region={base.TEST_RAM_BASE:#x},64k",
            f"--memory-region={base.M95320_BASE:#x},8k",
            f"--memory-region={rt.DUAL_BANK_MMIO_BASE:#x},{rt.SH7059_DUAL_BANK_MMIO_SIZE // 1024}k",
            elf,
        ]
        before = elf.read_bytes()
        result = base.run_command(cmd, timeout=120, env=env, expected_returncode=expected_rc)
        if elf.read_bytes() != before:
            raise rt.VerificationError(f"{rom}: 0xA0/01 ELF changed during execution")
        return result, base.read_pc_trace(trace), report

    # Positive 24-word sweep.
    pos_result, pos_records, pos_report = run_once("pos24", 24, expected_rc=0)
    if EXPECTED_PASS not in pos_result.stdout:
        raise rt.VerificationError(
            f"{rom}: 0xA0/01 positive run lacks exact PASS marker:\n{pos_result.stdout.rstrip()}"
        )
    _require_sweep_trace_and_irq(
        rom, pos_records, pos_report, spec, map_fixture,
        handler_addr, handler_words, rte_pc, expected_words=24,
    )

    # Negative early-stop control (COUNT=23 must fail specifically on cursor == ext_end - 4).
    neg_result, neg_records, neg_report = run_once("neg23", 23, expected_rc=1)
    expected_neg = (
        f"VQ_SH_ELF_SH7059_RAM_TEST status=FAIL stage=sweep_24 field=cursor "
        f"actual={spec['ext_end'] - 4:08x} expected={spec['ext_end']:08x}"
    )
    if expected_neg not in neg_result.stdout:
        raise rt.VerificationError(
            f"{rom}: 0xA0/01 COUNT=23 negative did not fail with {expected_neg!r}:\n"
            f"{neg_result.stdout.rstrip()}"
        )
    _require_sweep_trace_and_irq(
        rom, neg_records, neg_report, spec, map_fixture,
        handler_addr, handler_words, rte_pc, expected_words=23,
    )

    return (
        f"{EXPECTED_PASS} rom={rom} ext_start={spec['ext_start']:#010x} "
        f"ext_end={spec['ext_end']:#010x} negative_count23=PASS"
    )
