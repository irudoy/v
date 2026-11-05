"""Execute the Rolling Launch dwell-veto kernel with the stock divider."""

from dataclasses import dataclass, replace
from pathlib import Path
import os
import re
import tempfile

import verify_map_switching as base
from elf_storage_layout import ELFStorageError, require_separate_storage
from patches import map_switching_assembly as instructions
from patches import map_switching_layout
from patches import rolling_launch as model
from patches import rolling_launch_assembly as assembly
from patches import rolling_launch_compose as compose
from patches import rolling_launch_layout as storage


TOOLS = Path(__file__).resolve().parent
ALIAS_BASE = 0x01000000
ALIAS_SIZE = 65536
KERNEL_UNITS = ("spark_cut", "spark_events")


@dataclass(frozen=True)
class CommandCase:
    name: str
    stock: int
    command: int
    fallback: bool
    publisher: bool
    candidate: int
    returned: int
    configuration: bytes
    before: bytes
    after: bytes


def command_cases(table):
    """Derive coherent command records independently of the SH implementation."""
    spark = model.SparkCutState(accumulators=model.SPARK_CYLINDER_OFFSETS)
    inputs = model.Inputs(button=model.BUTTON_CANCEL, speed=500, rpm_native=280,
                          pedal=100, coolant=150, hcan1_state=1,
                          port_input_state=0x80, speed_wire_word=5000)
    cases = []

    def configured(index, trim, floor, speed=False, observe=False):
        slots = tuple(model.Slot(integral_gain=2, max_trim_rpm=7*i,
                                max_trim_speed=7*i, floor_command=110 + 2*i,
                                launch_rpm_native=300,
                                launch_speed_threshold=50 if speed else 600,
                                launch_soft_width_native=40) for i in range(5))
        slots = tuple(replace(slot, max_trim_rpm=trim, max_trim_speed=trim,
                              floor_command=floor) if i == index else slot
                      for i, slot in enumerate(slots))
        calibration = model.Calibration(mode=model.Mode.OBSERVE if observe else model.Mode.HOLD,
                                        enable_mask=31, slots=slots,
                                        run_timeout_ticks=20, rearm_ticks=3)
        state = model.step(model.RuntimeState(), replace(inputs, active_index=index),
                           calibration, table).state
        if state.phase != model.Phase.ACTIVE:
            raise base.VerificationError("command fixture did not activate")
        return calibration, state

    def stock_projection(state, stock):
        return model._publish_actuation(replace(
            state, stock_command=stock & 255, effective_command=stock & 255,
            applied_trim=0, actuation_ready=False), table)

    def add(name, state, calibration, stock, *, fallback=False, publisher=False,
            candidate=0, corruption=None, floor_override=None):
        before = bytearray(b"".join(model.encode_state(state, spark)))
        configuration = bytearray(calibration.to_bytes())
        if corruption is not None:
            expected = stock_projection(state, stock)
            returned = stock
        elif publisher:
            delta = (candidate & 255) - (stock & 255)
            ready = (state.phase == model.Phase.ACTIVE
                     and state.active_mode_snapshot == model.Mode.HOLD
                     and bool(state.flags & model.Flag.CONFIG_VALID) and not fallback
                     and 0 <= delta <= min(40, state.active_max_trim))
            expected = model._publish_actuation(replace(
                state, stock_command=stock & 255,
                effective_command=(candidate if ready else stock) & 255,
                applied_trim=delta if ready else 0, actuation_ready=ready), table)
            returned = candidate if ready else stock
        else:
            reference = calibration
            if floor_override is not None:
                index = state.active_index_snapshot
                slots = tuple(replace(slot, floor_command=0) if i == index else slot
                              for i, slot in enumerate(calibration.slots))
                reference = replace(calibration, slots=slots)
                configuration[0x28 + 12*index + 4] = floor_override
            expected = model.ignition_step(state, stock, reference, table,
                                           apc_fallback=fallback)
            returned = expected.effective_command
        after = bytearray(b"".join(model.encode_state(expected, spark)))
        if corruption is not None:
            offset, value = corruption
            before[offset] = after[offset] = value
        cases.append(CommandCase(name, stock, expected.effective_command, fallback,
                                 publisher, candidate, returned,
                                 bytes(configuration), bytes(before), bytes(after)))

    ordinal = 0
    for stock in (60, 100, 110, 117, 119, 120, 121, 200, 237):
        for trim in (0, 1, 20, 40):
            for floor in (110, 117, 120):
                index, speed = ordinal % 5, bool(ordinal % 2)
                calibration, state = configured(index, trim, floor, speed)
                law = (0, 500, 1000)[ordinal % 3]
                state = replace(state, law_output=law,
                                torque_fraction=law if speed else 0)
                add(f"command-{ordinal}", state, calibration, stock)
                ordinal += 1
    calibration, active = configured(0, 20, 120)
    active = replace(active, law_output=500)
    cooldown = model.step(active, replace(inputs, button=model.BUTTON_RELEASED),
                          calibration, table).state
    observe_calibration, observe = configured(0, 20, 120, observe=True)
    for state, config, name in (
            (model.RuntimeState(flags=model.Flag.CONFIG_VALID), calibration, "idle"),
            (cooldown, calibration, "cooldown"),
            (observe, observe_calibration, "observe"),
            (replace(active, flags=active.flags & ~model.Flag.CONFIG_VALID), calibration, "uncached")):
        add(name, state, config, 100)
    add("fallback-active", active, calibration, 100, fallback=True)
    add("floor-invalid", active, calibration, 100, floor_override=121)
    for name, corruption in (("map-invalid", (4, 5)), ("trim-invalid", (0x1e, 41)),
                             ("mode-invalid", (5, 255)), ("phase-invalid", (0, 255))):
        add(name, active, calibration, 100, corruption=corruption)
    for state, name, fallback in ((active, "ready", False), (active, "fallback", True),
                                  (cooldown, "cooldown", False), (observe, "observe", False),
                                  (replace(active, flags=active.flags & ~model.Flag.CONFIG_VALID),
                                   "uncached", False)):
        add(f"publisher-{name}", state, calibration, 0x12340064, fallback=fallback,
            publisher=True, candidate=0x5678006e)
    for candidate in (90, 125, 151):
        add(f"publisher-trim-{candidate}", active, calibration, 100,
            publisher=True, candidate=candidate)
    return tuple(cases)


def command_header(cases):
    def array(data):
        return "{" + ",".join(f"0x{value:02x}" for value in data) + "}"
    rows = []
    for case in cases:
        values = (case.stock, case.command, int(case.fallback), int(case.publisher),
                  case.candidate, case.returned)
        rows.append("{" + ",".join(f"0x{value:08x}U" for value in values) + ","
                    + ",".join(array(data) for data in
                               (case.configuration, case.before, case.after)) + "}")
    return "static const struct command_case command_cases[] = {\n" + ",\n".join(rows) + "\n};\n"


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
               f"-I{directory}",
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


def require_private_trace(trace, fixture, parsed, keys):
    """Require exact instructions, branch outcomes and executed delay slots."""
    records = base.read_pc_trace(trace)
    words = {item.address: int.from_bytes(fixture[item.address:item.address + 2], "big")
             for key in keys for item in parsed[key].statements if item.kind == "instruction"}
    executed, branches, delayed = set(), {}, set()
    for key in keys:
        for item in parsed[key].statements:
            if item.kind != "instruction":
                continue
            mnemonic = instructions._mnemonic(item)
            if mnemonic in {"bt", "bf"}:
                branches[item.address] = {item.address + 2, instructions._source_target(parsed[key], item)}
            if mnemonic in {"bsr", "jsr", "jmp", "rts"}:
                delayed.add(item.address)
    observed = {pc: set() for pc in branches}
    for index, (pc, word, delay) in enumerate(records):
        if words.get(pc) != word:
            raise base.VerificationError(f"ignition trace has unbound instruction {pc:#x}")
        executed.add(pc)
        if pc in branches and index + 1 < len(records):
            observed[pc].add(records[index + 1][0])
        if pc in delayed and (index + 1 >= len(records) or records[index + 1][0::2] != (pc + 2, 1)):
            raise base.VerificationError(f"ignition trace lacks delay slot at {pc:#x}")
    if executed != set(words):
        missing = ",".join(hex(pc) for pc in sorted(set(words) - executed))
        raise base.VerificationError(f"ignition trace has unexecuted instructions: {missing}")
    for pc, required in branches.items():
        if observed[pc] != required:
            raise base.VerificationError(f"ignition branch outcomes differ at {pc:#x}")
    return f"instructions={len(executed)} branch_outcomes={2 * len(branches)} delays={len(delayed)}"


def verify_builders(directory, fixture, invoke, layout, parsed):
    """Compare both real builder paths with their stock consumer arguments."""
    table = model.EfficiencyTable.from_bytes(fixture[layout.efficiency.start:layout.efficiency.end])
    cases = command_cases(table)
    (directory / "rolling-ignition-cases.h").write_text(command_header(cases))
    working = bytearray(fixture)
    # Simulator-only upstream auxiliary gate: select the final-coordinate
    # source. This function is outside the reconstructed ignition paths.
    working[0x8C3FA:0x8C400] = bytes.fromhex("e000000b0009")
    rom = base.build_rom_object(bytes(working), directory)
    elf = compile_harness(directory, rom, invoke, "builders", ("VQ_BUILDERS",))
    require_storage(elf, working)
    require_linked_fixture(elf, working)
    before = elf.read_bytes()
    result = base.run_command([base.RUN, elf],
                              env={**os.environ, "VQ_SH_HIGH_RAM_BASE": hex(ALIAS_BASE)},
                              timeout=180)
    if elf.read_bytes() != before:
        raise base.VerificationError("ignition builders ELF changes during execution")
    rows = sum(1 if case.publisher else 30 for case in cases)
    if f"RL_IGNITION_BUILDERS status=PASS rows={rows}" not in result.stdout:
        raise base.VerificationError("ignition builders lack their complete row count")
    coverage = compile_harness(directory, rom, invoke, "builder-coverage",
                               ("VQ_BUILDERS", "VQ_BUILDER_COVERAGE"))
    require_storage(coverage, working)
    require_linked_fixture(coverage, working)
    trace = directory / "builder.pc-trace"
    unit = layout.assembly_unit_by_key["ignition_adapter"]
    environment = {**os.environ, "VQ_SH_HIGH_RAM_BASE": hex(ALIAS_BASE),
                   "VQ_SH_PC_TRACE_FILE": str(trace), "VQ_SH_PC_TRACE_FORMAT": "v1",
                   "VQ_SH_PC_TRACE_RANGES": f"{unit.span.start:x}:{unit.span.end:x}"}
    before = coverage.read_bytes()
    base.run_command([base.RUN, coverage], env=environment, timeout=180)
    if coverage.read_bytes() != before:
        raise base.VerificationError("ignition adapter coverage ELF changes during execution")
    metrics = require_private_trace(trace, fixture, parsed, ("ignition_adapter",))
    return result.stdout.strip() + " adapter_" + metrics


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
        kernel_marker = (result.stdout.strip() + f" instructions={len(executed)} "
                         f"branch_outcomes={2 * len(branches)} delays={len(delayed)} storage_negative=PASS")
        print(kernel_marker, flush=True)
        builders = verify_builders(directory, fixture, invoke, layout, parsed)
        return builders
