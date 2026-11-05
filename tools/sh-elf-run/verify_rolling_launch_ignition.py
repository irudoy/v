"""Execute the Rolling Launch dwell-veto kernel with the stock divider."""

from pathlib import Path
import os
import re
import tempfile

import verify_map_switching as base
from elf_storage_layout import ELFStorageError, require_separate_storage
from patches import map_switching_assembly as instructions
from patches import map_switching_layout
from patches import rolling_launch_assembly as assembly
from patches import rolling_launch_compose as compose
from patches import rolling_launch_layout as storage


TOOLS = Path(__file__).resolve().parent
ALIAS_BASE = 0x01000000
ALIAS_SIZE = 65536
KERNEL_UNITS = ("spark_cut", "spark_events")


def require_stock_reconstruction(directory):
    """Bind independently assembled stock instructions and literals to JK08A."""
    path = TOOLS / "stock_jk08a_rolling_ignition.s"
    parsed = instructions.parse_source(path, 0, 0x100000)
    targets = set()
    source = []
    for item in parsed.statements:
        source.append(f".org {item.address:#x}")
        source.append(f"vq_stock_pool_{item.address:08x}:")
        text = item.text if item.kind == "instruction" else f".{item.kind} {item.text}"
        match = re.search(r"@\((0x[0-9a-f]+),pc\)", text, re.IGNORECASE)
        if match:
            target = int(match.group(1), 16)
            targets.add(target)
            text = text[:match.start(1)] + f"vq_stock_pool_{target:08x}" + text[match.end(1):]
        source.append(text)
    if targets - set(parsed.statement_by_address):
        raise base.VerificationError("stock ignition literal lacks a reconstructed statement")
    obj, elf, raw = (directory / f"stock-ignition.{suffix}" for suffix in ("o", "elf", "raw"))
    base.run_command([base.AS, "--big", "--isa=sh2e", "-o", obj, "-"],
                     input_text=base.preprocess_gnu_source("\n".join(source)))
    base.run_command([base.LD, "-EB", "-Ttext=0", "--entry=0", "-o", elf, obj])
    base.run_command([base.OBJCOPY, "-O", "binary", elf, raw])
    assembled = raw.read_bytes()
    stock = map_switching_layout.validate_image().data
    for item in parsed.statements:
        start, end = item.address, item.address + item.size
        if assembled[start:end] != stock[start:end]:
            raise base.VerificationError(f"stock ignition reconstruction differs at {start:#x}: {item.text}")
    return parsed, stock


def require_storage(elf, fixture):
    """Exclude the fixture and every ELF storage extent from aliased RAM."""
    if len(fixture) > ALIAS_BASE:
        raise base.VerificationError("ignition fixture overlaps the alias window")
    require_separate_storage(elf, ((ALIAS_BASE, ALIAS_SIZE),))


def compile_harness(directory, rom, invoke, name, defines=()):
    elf = directory / f"{name}.elf"
    command = [base.GCC, "-m2e", "-mb", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
               f"-Wl,-Ttext-segment={base.DRIVER_TEXT_BASE:#x}", "-Wl,--section-start=.rom=0"]
    command.extend(f"-D{value}" for value in defines)
    if "VQ_ALIAS_COLLISION" in defines:
        command.append(f"-Wl,--section-start=.alias_collision={ALIAS_BASE:#x}")
    command.extend(["-o", elf, TOOLS / "harness-rolling-ignition.c", invoke, rom])
    base.run_command(command, timeout=120)
    return elf


def require_linked_fixture(elf, fixture):
    linked = elf.with_suffix(".rom")
    base.run_command([base.OBJCOPY, "-O", "binary", "--only-section=.rom", elf, linked])
    if linked.read_bytes() != fixture:
        raise base.VerificationError("linked ignition ROM differs from the composed fixture")


def verify_kernel():
    layout = storage.load_layout()
    parsed = assembly.validate_assembly_sources(layout)
    tracked = assembly.load_payloads(layout)
    with tempfile.TemporaryDirectory(prefix="vq-rolling-ignition-") as temporary:
        directory = Path(temporary)
        stock_parsed, stock = require_stock_reconstruction(directory)
        assembled = {}
        for unit in layout.assembly_units:
            blob = base.assemble_unit(unit, parsed[unit.key], directory)
            if blob != tracked[unit.key]:
                raise base.VerificationError(f"{unit.key}: GNU bytes differ from locked payload")
            assembled[unit.key] = blob
        assembly.validate_instruction_semantics(layout, parsed, assembled)
        composed = compose.compose(layout=layout, blobs=assembled)
        fixture = composed.data
        rom = base.build_rom_object(fixture, directory)
        invoke = directory / "ignition-invoke.o"
        base.run_command([base.AS, "--big", "--isa=sh2e", "-o", invoke,
                          TOOLS / "stock_ignition_consumer_invoke.s"])
        negative = compile_harness(directory, rom, invoke, "alias-collision", ("VQ_ALIAS_COLLISION",))
        try:
            require_storage(negative, fixture)
        except ELFStorageError:
            pass
        else:
            raise base.VerificationError("ignition alias collision did not refuse before execution")
        positive = compile_harness(directory, rom, invoke, "kernel")
        require_storage(positive, fixture)
        require_linked_fixture(positive, fixture)
        environment = {**os.environ, "VQ_SH_HIGH_RAM_BASE": hex(ALIAS_BASE)}
        before = positive.read_bytes()
        result = base.run_command([base.RUN, positive], env=environment, timeout=180)
        if positive.read_bytes() != before:
            raise base.VerificationError("ignition kernel ELF changes during execution")
        if "RL_DWELL_VETO_KERNEL status=PASS rows=53760" not in result.stdout:
            raise base.VerificationError("dwell veto kernel lacks its complete row count")
        coverage = compile_harness(directory, rom, invoke, "kernel-coverage", ("VQ_VETO_COVERAGE",))
        require_storage(coverage, fixture)
        require_linked_fixture(coverage, fixture)
        trace = directory / "kernel.pc-trace"
        environment.update({"VQ_SH_PC_TRACE_FILE": str(trace), "VQ_SH_PC_TRACE_FORMAT": "v1",
                            "VQ_SH_PC_TRACE_RANGES": ",".join(
                                f"{layout.assembly_unit_by_key[key].span.start:x}:"
                                f"{layout.assembly_unit_by_key[key].span.end:x}" for key in KERNEL_UNITS)})
        before = coverage.read_bytes()
        base.run_command([base.RUN, coverage], env=environment, timeout=180)
        if coverage.read_bytes() != before:
            raise base.VerificationError("ignition coverage ELF changes during execution")
        records = base.read_pc_trace(trace)
        words = {item.address: int.from_bytes(fixture[item.address:item.address + 2], "big")
                 for key in KERNEL_UNITS for item in parsed[key].statements if item.kind == "instruction"}
        executed = set()
        for pc, word, delay in records:
            if pc not in words or words[pc] != word:
                raise base.VerificationError(f"ignition kernel trace has unbound instruction {pc:#x}")
            executed.add(pc)
        if executed != set(words):
            missing = ",".join(hex(pc) for pc in sorted(set(words) - executed))
            raise base.VerificationError(f"ignition kernel has unexecuted instructions: {missing}")
        branches = {}
        delayed = set()
        for key in KERNEL_UNITS:
            for item in parsed[key].statements:
                if item.kind != "instruction":
                    continue
                mnemonic = instructions._mnemonic(item)
                if mnemonic in {"bt", "bf"}:
                    branches[item.address] = {
                        item.address + 2, instructions._source_target(parsed[key], item),
                    }
                if mnemonic in {"bsr", "jmp", "rts"}:
                    delayed.add(item.address)
        observed = {pc: set() for pc in branches}
        for index, (pc, word, delay) in enumerate(records):
            if pc in branches and index + 1 < len(records):
                observed[pc].add(records[index + 1][0])
            if pc in delayed and (
                    index + 1 >= len(records)
                    or records[index + 1][0::2] != (pc + 2, 1)):
                raise base.VerificationError(f"ignition kernel lacks its delay slot at {pc:#x}")
        for pc, required in branches.items():
            if observed[pc] != required:
                raise base.VerificationError(
                    f"ignition kernel branch outcomes differ at {pc:#x}: "
                    f"observed={sorted(observed[pc])} required={sorted(required)}")
        return (result.stdout.strip() + f" instructions={len(executed)} "
                f"branch_outcomes={2 * len(branches)} delays={len(delayed)} storage_negative=PASS")
