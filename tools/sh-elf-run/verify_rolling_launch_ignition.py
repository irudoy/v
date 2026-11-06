"""Execute coupled Rolling Launch ignition, recovery and publication boundaries."""

from dataclasses import dataclass, replace
from pathlib import Path
import re
import tempfile

import verify_map_switching as base
import verify_simulator_irq as irq
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
COUPLED_DWELLS = (0, 30, 60, *range(86, 95), 100, 110, 119, 120)


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
    # Representative commands from the stock-timing medians of the 2026-11-04
    # hardware record. The dwell matrix spans its 86..94 degree window; these
    # states do not replay the capture or claim measured output edges.
    for name, stock, rpm in (("regression-h9-window", 81, 710),
                             ("regression-h32-window", 82, 685)):
        config, state = configured(3, 20, 120, speed=True)
        add(name, replace(state, law_output=0, torque_fraction=0, rpm_sample_native=rpm),
            config, stock)
    return tuple(cases)


def command_header(cases):
    def array(data):
        return "{" + ",".join(f"0x{value:02x}" for value in data) + "}"
    rows = []
    for case in cases:
        values = (case.stock, case.command, int(case.fallback), int(case.publisher),
                  case.candidate, case.returned)
        ordinary = int(case.name.startswith(("command-", "regression-")))
        rows.append("{" + ",".join(f"0x{value:08x}U" for value in (*values, ordinary)) + ","
                    + ",".join(array(data) for data in
                               (case.configuration, case.before, case.after)) + "}")
    return ("static const struct command_case command_cases[] = {\n" + ",\n".join(rows) + "\n};\n"
            + "#ifdef VQ_COUPLED\nstatic const unsigned coupled_dwells[] = {"
            + ",".join(str(value) for value in COUPLED_DWELLS) + "};\n#endif\n")


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


def compile_harness(directory, rom, invoke, name, defines=(), *, collision_address=ALIAS_BASE):
    elf = directory / f"{name}.elf"
    command = [base.GCC, "-m2e", "-mb", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
               f"-I{directory}",
               f"-Wl,-Ttext-segment={base.DRIVER_TEXT_BASE:#x}", "-Wl,--section-start=.rom=0"]
    command.extend(f"-D{value}" for value in defines)
    if "VQ_ALIAS_COLLISION" in defines:
        command.append(f"-Wl,--section-start=.alias_collision={collision_address:#x}")
    if "VQ_COUPLED" in defines:
        command.extend(["-Wl,--section-start=.tooth_fixture=0x108400",
                        TOOLS / "rolling_ignition_tooth_fixture.s"])
    command.extend(["-o", elf, TOOLS / "harness-rolling-ignition.c", invoke, rom])
    base.run_command(command, timeout=120)
    return elf


def require_linked_fixture(elf, fixture):
    linked = elf.with_suffix(".rom")
    base.run_command([base.OBJCOPY, "-O", "binary", "--only-section=.rom", elf, linked])
    if linked.read_bytes() != fixture:
        raise base.VerificationError("linked ignition ROM differs from the composed fixture")


def require_fixture_changes(original, fixture, spans):
    """Confine simulator scaffolding to its declared stock-code exclusions."""
    allowed = {address for start, end in spans for address in range(start, end)}
    if len(original) != len(fixture):
        raise base.VerificationError("ignition fixture changes the ROM extent")
    changed = {address for address, (left, right) in enumerate(zip(original, fixture)) if left != right}
    if changed - allowed:
        raise base.VerificationError("ignition fixture changes an instruction outside its declared scaffolding")


def require_private_trace(trace, fixture, parsed, keys):
    """Require exact instructions, branch outcomes and executed delay slots."""
    records = base.read_pc_trace(trace)
    words = {item.address: int.from_bytes(fixture[item.address:item.address + 2], "big")
             for key in keys for item in parsed[key].statements if item.kind == "instruction"}
    executed, branches, delayed, direct, calls, returns, external_calls = set(), {}, set(), {}, set(), set(), set()
    for key in keys:
        for item in parsed[key].statements:
            if item.kind != "instruction":
                continue
            mnemonic = instructions._mnemonic(item)
            if mnemonic in {"bt", "bf"}:
                branches[item.address] = {item.address + 2, instructions._source_target(parsed[key], item)}
            if mnemonic in {"bra", "bsr", "jsr", "jmp", "rts"}:
                delayed.add(item.address)
            if mnemonic in {"bra", "bsr"}:
                direct[item.address] = instructions._source_target(parsed[key], item)
            if mnemonic == "bsr":
                calls.add(item.address)
            if mnemonic == "rts":
                returns.add(item.address)
            if mnemonic == "jsr":
                external_calls.add(item.address)
    observed = {pc: set() for pc in branches}
    frames = []
    for index, (pc, word, delay) in enumerate(records):
        if words.get(pc) != word:
            raise base.VerificationError(f"ignition trace has unbound instruction {pc:#x}")
        executed.add(pc)
        if pc in branches and index + 1 < len(records):
            observed[pc].add(records[index + 1][0])
        if pc in delayed and (index + 1 >= len(records) or records[index + 1][0::2] != (pc + 2, 1)):
            raise base.VerificationError(f"ignition trace lacks delay slot at {pc:#x}")
        if pc in direct and (index + 2 >= len(records) or records[index + 2][0] != direct[pc]):
            raise base.VerificationError(f"ignition trace has a different direct target at {pc:#x}")
        if pc in calls:
            frames.append(pc + 4)
        if pc in returns and (not frames or index + 2 >= len(records)
                              or records[index + 2][0] != frames.pop()):
            raise base.VerificationError(f"ignition trace has an unmatched return at {pc:#x}")
        if pc in external_calls and (index + 2 >= len(records) or records[index + 2][0] != pc + 4):
            raise base.VerificationError(f"ignition trace lacks its external call return at {pc:#x}")
    if frames:
        raise base.VerificationError("ignition trace has an unreturned private call")
    if executed != set(words):
        missing = ",".join(hex(pc) for pc in sorted(set(words) - executed))
        raise base.VerificationError(f"ignition trace has unexecuted instructions: {missing}")
    for pc, required in branches.items():
        if observed[pc] != required:
            raise base.VerificationError(f"ignition branch outcomes differ at {pc:#x}")
    metrics = f"instructions={len(executed)} branch_outcomes={2 * len(branches)} delays={len(delayed)}"
    if keys == KERNEL_UNITS:
        labels = parsed["spark_cut"].labels
        reset_pc = parsed["spark_events"].labels["rolling_launch_spark_reset"]
        groups, segment = {}, []

        def finish(pcs):
            if not pcs:
                return
            present = set(pcs)
            if labels["rl_cut_cold"] in present:
                kind = "off_first"
                resets = 1
            elif labels["rl_cut_latch"] in present:
                kind = "off_latch"
                resets = 0
            elif labels["rl_cut_full"] not in present:
                if labels["rl_cut_active"] in present:
                    kind = "off_fast_observe"
                else:
                    kind = ("off_fast_warm" if labels["rl_cut_quiet_done"]-2 in present
                            else "off_fast_steady")
                resets = 0
            else:
                kind = "hold_admitted" if labels["rl_cut_commit"] in present else "hold_other"
                resets = int(labels["rl_cut_reset"] in present)
            if pcs.count(reset_pc) != resets:
                raise base.VerificationError("dwell reset repeats outside its first or HOLD-reset path")
            groups[kind] = max(groups.get(kind, 0), len(pcs))

        for pc, _word, _delay in records:
            if pc == labels["rolling_launch_spark_cut"]:
                finish(segment)
                segment = []
            segment.append(pc)
        finish(segment)
        if set(groups) != {"off_first", "off_latch", "off_fast_observe", "off_fast_warm",
                           "off_fast_steady", "hold_admitted", "hold_other"}:
            raise base.VerificationError("dwell timing trace lacks a required path")
        if groups["hold_admitted"] > 153:
            raise base.VerificationError("admitted HOLD path exceeds its 153-instruction budget")
        metrics += " " + " ".join(f"max_{key}={value}" for key, value in sorted(groups.items()))
    return metrics


def verify_builders(directory, fixture, invoke, layout, parsed):
    """Compare both real builder paths with their stock consumer arguments."""
    table = model.EfficiencyTable.from_bytes(fixture[layout.efficiency.start:layout.efficiency.end])
    cases = command_cases(table)
    (directory / "rolling-ignition-cases.h").write_text(command_header(cases))
    working = bytearray(fixture)
    # Simulator-only upstream auxiliary gate: select the final-coordinate
    # source. This function is outside the reconstructed ignition paths.
    working[0x8C3FA:0x8C400] = bytes.fromhex("e000000b0009")
    require_fixture_changes(fixture, working, ((0x8C3FA, 0x8C400),))
    rom = base.build_rom_object(bytes(working), directory)
    elf = compile_harness(directory, rom, invoke, "builders", ("VQ_BUILDERS",))
    require_storage(elf, working)
    require_linked_fixture(elf, working)
    before = elf.read_bytes()
    result = base.run_command([base.RUN, elf],
                              env={**irq.environment(), "VQ_SH_HIGH_RAM_BASE": hex(ALIAS_BASE)},
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
    environment = {**irq.environment(), "VQ_SH_HIGH_RAM_BASE": hex(ALIAS_BASE),
                   "VQ_SH_PC_TRACE_FILE": str(trace), "VQ_SH_PC_TRACE_FORMAT": "v1",
                   "VQ_SH_PC_TRACE_RANGES": f"{unit.span.start:x}:{unit.span.end:x}"}
    before = coverage.read_bytes()
    base.run_command([base.RUN, coverage], env=environment, timeout=180)
    if coverage.read_bytes() != before:
        raise base.VerificationError("ignition adapter coverage ELF changes during execution")
    metrics = require_private_trace(trace, fixture, parsed, ("ignition_adapter",))
    print(result.stdout.strip() + " adapter_" + metrics, flush=True)
    # Fixture-only boundaries outside the stock instructions under test:
    # select the bounded tooth context after the original prologue and leave
    # after the two countdown slots through the original interrupt epilogue.
    working[0x28ECC:0x28ED8] = bytes.fromhex("d001402b0009000900108400")
    working[0x295B8:0x295C4] = bytes.fromhex("d001402b0009000900108500")
    require_fixture_changes(fixture, working,
                            ((0x8C3FA, 0x8C400), (0x28ECC, 0x28ED8), (0x295B8, 0x295C4)))
    rom = base.build_rom_object(bytes(working), directory)
    coupled = compile_harness(directory, rom, invoke, "coupled", ("VQ_BUILDERS", "VQ_COUPLED"))
    require_storage(coupled, working)
    require_linked_fixture(coupled, working)
    before = coupled.read_bytes()
    result = base.run_command([base.RUN, coupled],
                              env={**irq.environment(), "VQ_SH_HIGH_RAM_BASE": hex(ALIAS_BASE)},
                              timeout=180)
    if coupled.read_bytes() != before:
        raise base.VerificationError("coupled ignition ELF changes during execution")
    coupled_rows = sum(case.name.startswith(("command-", "regression-"))
                       and 60 <= case.command <= 120 for case in cases) * len(COUPLED_DWELLS) * 3 * 2 * 4
    if f"RL_IGNITION_COUPLED status=PASS rows={coupled_rows}" not in result.stdout:
        raise base.VerificationError("coupled ignition lacks its complete row count")
    print(result.stdout.strip(), flush=True)
    late = bytearray(working)
    late[0x296C0:0x296C4] = (0x21CE0).to_bytes(4, "big")
    negative_rom = base.build_rom_object(bytes(late), directory)
    negative = compile_harness(directory, negative_rom, invoke, "late-veto-negative",
                               ("VQ_BUILDERS", "VQ_COUPLED", "VQ_LEGACY_LATE_VETO"))
    require_storage(negative, late)
    require_linked_fixture(negative, late)
    original_negative = negative.read_bytes()
    rejected = base.run_command([base.RUN, negative],
                                env={**irq.environment(), "VQ_SH_HIGH_RAM_BASE": hex(ALIAS_BASE)},
                                expected_returncode=1, timeout=30)
    if "successor dwell edge" not in rejected.stderr:
        raise base.VerificationError("late-veto negative does not fail on its physical dwell edge")
    if negative.read_bytes() != original_negative:
        raise base.VerificationError("late-veto negative ELF changes during execution")
    print("RL_IGNITION_LATE_VETO_NEGATIVE status=PASS P=120 dwell=90 rejected_edge=true", flush=True)
    # Rebuild the positive ROM object after the negative fixture.
    rom = base.build_rom_object(bytes(working), directory)
    return verify_engine_irqs(directory, working, rom, invoke, layout, parsed, cases)


def irq_values(output):
    rows = [line for line in output.splitlines() if line.startswith("RL_IGNITION_IRQ status=PASS ")]
    if len(rows) != 1:
        raise base.VerificationError("engine IRQ fixture lacks one terminal")
    return {key: int(value, 16 if key == "stack" or key.startswith("v") else 10)
            for item in rows[0].split()[2:] for key, value in (item.split("=", 1),)}


def verify_engine_irqs(directory, fixture, rom, invoke, layout, parsed, cases):
    """Interrupt each executed publication store and interrupt-mask boundary."""
    case_index = next(i for i, case in enumerate(cases)
                      if case.stock == 100 and case.command == 120 and case.before[44] == 1)
    words = {item.address: item for source in parsed.values()
             for item in source.statements if item.kind == "instruction"}
    ranges = (f"{min(unit.span.start for unit in layout.assembly_units):x}:"
              f"{max(unit.span.end for unit in layout.assembly_units):x}")
    ranges += ",28ea2:28ecc,2a294:2a2be,108400:108600"
    rows = 0
    for release in (0, 1):
        defines = ("VQ_BUILDERS", "VQ_COUPLED", "VQ_ENGINE_IRQ",
                   f"VQ_IRQ_CASE={case_index}", f"VQ_IRQ_RELEASE={release}")
        elf = compile_harness(directory, rom, invoke, f"engine-irq-{release}", defines)
        require_storage(elf, fixture)
        require_linked_fixture(elf, fixture)
        trace = directory / f"engine-irq-{release}.trace"
        environment = {**irq.environment(), "VQ_SH_HIGH_RAM_BASE": hex(ALIAS_BASE),
                       "VQ_SH_PC_TRACE_FILE": str(trace), "VQ_SH_PC_TRACE_FORMAT": "v1",
                       "VQ_SH_PC_TRACE_RANGES": ranges}
        original = elf.read_bytes()
        baseline = base.run_command([base.RUN, elf], env=environment, timeout=30)
        values = irq_values(baseline.stdout)
        if values["v12"]:
            raise base.VerificationError("disabled engine IRQ executes a handler")
        stack = ((values["stack"] - 4096, 4100),)
        stack_top = values["stack"]
        require_separate_storage(elf, stack)
        negative = compile_harness(directory, rom, invoke, f"irq-stack-collision-{release}",
                                   (*defines, "VQ_ALIAS_COLLISION"),
                                   collision_address=values["stack"] - 16)
        try:
            require_separate_storage(negative, stack)
        except ELFStorageError:
            pass
        else:
            raise base.VerificationError("IRQ stack collision does not refuse before execution")
        baseline_trace = base.read_pc_trace(trace)
        occurrences, requests, started = {}, [], False
        for pc, word, delay in baseline_trace:
            occurrences[pc] = occurrences.get(pc, 0) + 1
            started |= pc == 0xD38E4
            if pc not in words:
                continue
            item = words[pc]
            if int.from_bytes(fixture[pc:pc + 2], "big") != word:
                raise base.VerificationError("engine baseline trace has an unbound instruction")
            destination = item.text.split(",", 1)[-1].strip()
            store = (item.text.startswith(("mov.b ", "mov.w ", "mov.l "))
                     and destination.startswith("@") and "r15" not in destination)
            if started and (store or item.text.startswith("ldc ") and destination == "sr"):
                requests.append((pc, occurrences[pc]))
        if not requests:
            raise base.VerificationError("engine IRQ has no publication boundaries")
        for pc, count in requests:
            report = directory / f"irq-{release}-{pc:x}-{count}.report"
            child = {**environment, **{"VQ_SH_IRQ_" + key: str(value) for key, value in
                     dict(PC=f"{pc:x}", COUNT=count, LEVEL=8, VECTOR=84, REPORT=report).items()}}
            result = base.run_command([base.RUN, elf], env=child, timeout=30)
            values = irq_values(result.stdout)
            lines = report.read_text().splitlines()
            if len(lines) != 2 or any("status=" in line for line in lines):
                raise base.VerificationError("engine IRQ lacks a completed entry and return")
            entry, returned = ({key: int(value, 16) for item in line.split()
                                for key, value in (item.split("=", 1),)} for line in lines)
            if (entry["triggered"] != pc or entry["handler"] != 0x28EA2
                    or entry["sr"] & 0xf0 or returned != dict(returned=entry["accepted"], sp=values["v11"])):
                raise base.VerificationError(f"engine IRQ frame differs: {entry}, {returned}, {values}")
            if not stack_top - 4096 < values["v11"] <= stack_top:
                raise base.VerificationError("engine IRQ frame escapes its declared stack")
            active = values["v0"] == 1 and values["v1"] == 1
            q = values["v2"] if active else 0
            if active:
                expected = (1000 - values["v5"] if values["v4"] == 1
                            else model.cut_fraction(values["v5"], values["v6"]))
                if values["v3"] != 1 or q != expected:
                    raise base.VerificationError(f"engine IRQ observes a torn actuation tuple: {values}")
            if (values["v12"] != 1 or values["v8"] != q or values["v9"] != int(active)
                    or values["v10"] != int(q != 0)):
                raise base.VerificationError(f"engine IRQ consumes a different decision: {values}")
            records = base.read_pc_trace(trace)
            entered = next(i for i, record in enumerate(records) if record[0] == 0x28EA2)
            if sum(record[0] == pc for record in records[:entered]) != count:
                raise base.VerificationError("engine IRQ COUNT differs from its instruction trace")
            rte = next((i for i, record in enumerate(records)
                        if record[0] == 0x2A2BA and record[1] == 0x002b), None)
            if rte is None or records[rte + 1] != (0x2A2BC, 0x0009, 1):
                raise base.VerificationError("engine IRQ trace lacks the stock RTE and its executed slot")
            if elf.read_bytes() != original:
                raise base.VerificationError("engine IRQ ELF changes during execution")
            rows += 1
        print(f"RL_IGNITION_IRQ_ACTION status=PASS release={release} boundaries={len(requests)}", flush=True)
    return f"RL_IGNITION_IRQ_BOUNDARIES status=PASS rows={rows} stack_negative=PASS"


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
        environment = {**irq.environment(), "VQ_SH_HIGH_RAM_BASE": hex(ALIAS_BASE)}
        before = positive.read_bytes()
        result = base.run_command([base.RUN, positive], env=environment, timeout=180)
        if positive.read_bytes() != before:
            raise base.VerificationError("ignition kernel ELF changes during execution")
        if "RL_DWELL_VETO_KERNEL status=PASS rows=53761" not in result.stdout:
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
        metrics = require_private_trace(trace, fixture, parsed, KERNEL_UNITS)
        kernel_marker = result.stdout.strip() + f" {metrics} storage_negative=PASS"
        print(kernel_marker, flush=True)
        builders = verify_builders(directory, fixture, invoke, layout, parsed)
        return builders
