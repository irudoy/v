"""Interrupt rows of the GNU SH-2E gate of exact JK08A Rolling Launch.

The ignition publisher runs from the crank-tooth interrupt between any two
engine instructions outside a masked section. The rows run six engine passes
of rolling_launch_rows.interrupt_scenarios and inject one ignition
publication through the simulator interrupt hook. A publication observes the
memory of the pass, and the pass observes the publication, only through
memory accesses, so the interleavings of one publication with a pass are the
points after its first instruction and after each of its loads and stores.
A run without a request records the PC trace that binds each of these
instructions to its execution count and gives the expected acceptance point:
the first later instruction boundary with SR.I below the request level that
follows no delay slot and no LDC, STC, LDS or STS. One injected run follows
every store, inside and between the masked groups, and one more follows
each other acceptance point. Each injected run then requires:

- acceptance at that point, so a request inside a masked group is accepted
  only after the instruction that follows the LDC that lowers the mask;
- a returned handler, preserved r8..r14, stack pointer, GBR and SR, and
  unchanged observations of every other pass;
- the model publication of the observed record pair, and final records of a
  publication before or after the pass;
- in a steady ACTIVE pass, a ready publication of P at every boundary;
- in an RPM activation, at least one publication between the error pair and
  the publisher mask, and the stock command from each of them: the status
  view keeps kind NONE of the IDLE record until the masked wire views at the
  end of the pass;
- the store orders of the transitions: activation stores the phase first,
  the mode after the map, the law output before the kind and the trim of the
  run last; an abort and corrupt-state recovery leave ACTIVE with their first
  record store after the sample.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import os
from pathlib import Path
import re
import struct

import rolling_launch_rows
import verify_map_switching as base_verifier

model = rolling_launch_rows.model


TOOL_DIR = Path(__file__).resolve().parent
LEVEL = 8
VECTOR = 80
RETURNED = 0x52455445
SR_I = 0xF0
PUBLISHER_SR = 0x80
# `or #0xf0,r0` and `ldc r0,sr`, the masking pair of every section.
OR_MASK = 0xCBF0
LDC_R0_SR = 0x400E
PREFIX = "VQ_SH_ELF_ROLLING_IRQ "
DONE = "VQ_SH_ELF_ROLLING_IRQ status=DONE scenarios={count}"
LINE = re.compile(
    r"VQ_SH_ELF_ROLLING_IRQ case=(?P<case>\S+) hits=(?P<hits>\d+) returned=(?P<returned>[0-9a-f]{8})"
    r" preserved=(?P<preserved>[01]) sp=(?P<sp>[01]) gbr=(?P<gbr>[01]) sr=(?P<sr>[0-9a-f]{8})"
    r" irq_preserved=(?P<irq_preserved>[01]) irq_r4=(?P<irq_r4>[0-9a-f]{8})"
    r" irq_r5=(?P<irq_r5>[0-9a-f]{8}) irq_sr=(?P<irq_sr>[0-9a-f]{8})"
    r" seen=(?P<seen>[0-9a-f]{152}) published=(?P<published>[0-9a-f]{152})"
    r" final=(?P<final>[0-9a-f]{152})")
REPORT = re.compile(r"triggered=([0-9a-f]{8}) accepted=([0-9a-f]{8}) handler=([0-9a-f]{8})"
                    r" sr=([0-9a-f]{8})")
SPLIT = model.STATE_SIZE
# Fields that a pass stores before the phase of its transition: the sample of
# every pass, and the gate flags and abort reason of an IDLE pass.
ABORT_PRE_PHASE_FIELDS = rolling_launch_rows.SAMPLE_FIELDS
ACTIVATION_PRE_PHASE_FIELDS = rolling_launch_rows.SAMPLE_FIELDS | {"flags", "abort_reason"}


class InterruptError(base_verifier.VerificationError):
    """An interrupt row differs from its contract."""


@dataclass(frozen=True)
class Trigger:
    scenario: int
    pc: int
    count: int
    index: int
    accepted: int
    position: int
    deferred: bool
    after_ldc: bool
    store: bool


def stores(opcode):
    """True for an SH-2E instruction that writes memory."""
    high, low = opcode >> 12, opcode & 0xF
    return ((high == 0x2 and low in (0, 1, 2, 4, 5, 6)) or (high == 0x0 and low in (4, 5, 6))
            or high == 0x1 or opcode >> 8 in (0x80, 0x81, 0xC0, 0xC1, 0xC2, 0xCD, 0xCE, 0xCF)
            or (high == 0x4 and opcode & 0xFF in (0x02, 0x12, 0x22, 0x03, 0x13, 0x23, 0x1B)))


def loads(opcode):
    """True for an SH-2E instruction that reads data memory other than a PC literal."""
    high, low = opcode >> 12, opcode & 0xF
    return ((high == 0x6 and low in (0, 1, 2, 4, 5, 6)) or (high == 0x0 and low >= 0xC)
            or high == 0x5 or opcode >> 8 in (0x84, 0x85, 0xC4, 0xC5, 0xC6, 0xCC, 0xCD, 0xCE, 0xCF)
            or (high == 0x4 and (low == 0xF or opcode & 0xFF in (0x06, 0x16, 0x26, 0x07, 0x17,
                                                                 0x27, 0x1B))))


def inhibits(opcode):
    """True for LDC, LDC.L, STC, STC.L, LDS, LDS.L, STS, STS.L and FPU opcodes."""
    high, low = opcode >> 12, opcode & 0xFF
    return (high == 0xF
            or (high == 0x4 and low in (0x0E, 0x1E, 0x2E, 0x07, 0x17, 0x27,
                                        0x0A, 0x1A, 0x2A, 0x5A, 0x6A,
                                        0x06, 0x16, 0x26, 0x56, 0x66,
                                        0x03, 0x13, 0x23, 0x02, 0x12, 0x22, 0x52, 0x62))
            or (high == 0x0 and low in (0x02, 0x12, 0x22, 0x0A, 0x1A, 0x2A, 0x5A, 0x6A)))


def _loads_sr(opcode):
    return opcode & 0xF0FF in (0x400E, 0x4007)


def raises_mask(records, index):
    """True for an executed `ldc r0,sr` that follows `or #0xf0,r0`.

    Every RL, Map Switching and stock section of the passes masks with this
    pair; every other LDC to SR restores the SR that its section saved.
    """
    return (records[index][1] == LDC_R0_SR and index > 0
            and records[index - 1][1] == OR_MASK)


def levels(records, engine_level=0):
    """SR.I in effect before every trace record.

    The level is unknown before the first LDC to SR. A restoring LDC, as the
    LDC of the harness call helper, gives the engine level.
    """
    result, level = [], None
    for index, (_pc, opcode, _delay) in enumerate(records):
        result.append(level)
        if _loads_sr(opcode):
            level = 15 if raises_mask(records, index) else engine_level
    return result


def acceptance(records, trigger, before, level=LEVEL):
    """Return the trace index before which the hook accepts a request."""
    for index in range(trigger + 1, len(records)):
        if (not records[index][2] and not inhibits(records[index - 1][1])
                and before[index] is not None and before[index] < level):
            return index
    raise InterruptError(f"no acceptance point follows {records[trigger][0]:#010x}")


def triggers(records, engine, invoke_range):
    """Bind the entry, every load and every store of each engine pass to its
    execution count and acceptance."""
    before = levels(records)
    counts, result, scenario = {}, [], -1
    inside = False
    for index, (pc, opcode, _delay) in enumerate(records):
        counts[pc] = counts.get(pc, 0) + 1
        entry = pc == engine and not inside
        if entry:
            scenario += 1
            inside = True
        elif invoke_range[0] <= pc < invoke_range[1]:
            inside = False
        if not inside or not (entry or loads(opcode) or stores(opcode)):
            continue
        accepted = acceptance(records, index, before)
        deferred = any(before[position] == 15 for position in range(index + 1, accepted + 1))
        after_ldc = (deferred and _loads_sr(records[accepted - 2][1])
                     and not raises_mask(records, accepted - 2))
        result.append(Trigger(scenario, pc, counts[pc], index, records[accepted][0], accepted,
                              deferred, after_ldc, stores(opcode)))
    return result


def injections(found):
    """Every store, and the first other trigger of each further acceptance point."""
    covered = {item.position for item in found if item.store}
    result = []
    for item in found:
        if item.store or item.position not in covered:
            covered.add(item.position)
            result.append(item)
    return result


def parse(stdout, scenarios):
    lines = [line for line in stdout.splitlines() if line.startswith(PREFIX)]
    if not lines or lines[-1] != DONE.format(count=len(scenarios)):
        raise InterruptError("interrupt harness lacks its terminal" + (f"\n{stdout}" if stdout else ""))
    rows = []
    for line, scenario in zip(lines[:-1], scenarios, strict=True):
        match = LINE.fullmatch(line)
        if match is None or match["case"] != scenario.name:
            raise InterruptError(f"malformed interrupt row: {line}")
        rows.append(match.groupdict())
    return rows


def _records(text):
    data = bytes.fromhex(text)
    return data[:SPLIT], data[SPLIT:]


def _fields(records):
    return asdict(rolling_launch_rows._raw_state(*records))


def check_disabled(row, scenario):
    """An uninterrupted pass leaves the model records and observes nothing."""
    if (row["hits"] != "0" or int(row["returned"], 16) or row["preserved"] != "1"
            or row["sp"] != "1" or row["gbr"] != "1" or int(row["sr"], 16) & 0xF2):
        raise InterruptError(f"{scenario.name}: uninterrupted pass differs: {row}")
    expected = rolling_launch_rows.engine_pass((scenario.base, scenario.extension),
                                               scenario.inputs)[:2]
    if _records(row["final"]) != expected:
        raise InterruptError(f"{scenario.name}: uninterrupted records differ from the model")


def check_interrupted(row, scenario):
    """Check one injected publication and return its observed record pair."""
    name = scenario.name
    if (row["hits"] != "1" or int(row["returned"], 16) != RETURNED or row["preserved"] != "1"
            or row["sp"] != "1" or row["gbr"] != "1" or int(row["sr"], 16) & 0xF2
            or row["irq_preserved"] != "1" or int(row["irq_sr"], 16) != PUBLISHER_SR):
        raise InterruptError(f"{name}: the interrupt frame differs: {row}")
    seen = _records(row["seen"])
    publication = rolling_launch_rows.ignition_publication(
        seen, scenario.stock, scenario.effective, contract=False)
    if int(row["irq_r4"], 16) != publication.stock_wide:
        raise InterruptError(f"{name}: the publisher changes r4")
    if (_records(row["published"]) != (publication.base, publication.extension)
            or int(row["irq_r5"], 16) != publication.r5):
        raise InterruptError(f"{name}: the publication differs from the model of its record")
    final = _records(row["final"])
    orders = rolling_launch_rows.interrupt_finals(scenario)
    if final not in orders:
        raise InterruptError(
            f"{name}: the pass leaves records of no publication order; fields differ "
            + "; ".join(f"from order {index}: {_changed(final, order)}"
                        for index, order in enumerate(orders)))
    initial = _fields((scenario.base, scenario.extension))
    fields = _fields(seen)
    ready = publication.r5 == publication.effective_wide
    if scenario.kind == "steady" and (rolling_launch_rows._decode(*seen) is None or not ready):
        raise InterruptError(f"{name}: a steady ACTIVE record fails the publisher check")
    if scenario.kind == "abort":
        if fields["phase"] == model.Phase.ACTIVE:
            _require_unchanged(name, "the phase", fields, initial, ABORT_PRE_PHASE_FIELDS)
        elif ready:
            raise InterruptError(f"{name}: a record after the phase store publishes P")
    if scenario.kind == "recovery":
        if fields["phase"] == initial["phase"]:
            _require_unchanged(name, "the phase", fields, initial, frozenset())
        if ready:
            raise InterruptError(f"{name}: a rejected record publishes P")
    return seen, ready


def _changed(records, other):
    """Name every field of the two records that differs, with both values."""
    result = []
    for buffer, reference, region in zip(records, other, model.STATE_FIELDS):
        for field, offset, fmt in model.STATE_FIELDS[region]:
            size = struct.calcsize(">" + fmt)
            if buffer[offset:offset + size] != reference[offset:offset + size]:
                result.append(f"{field}={buffer[offset:offset + size].hex()}/"
                              f"{reference[offset:offset + size].hex()}")
    return ", ".join(result) or "none"


def _require_unchanged(name, store, fields, initial, allowed):
    changed = sorted(key for key in fields if key not in allowed and fields[key] != initial[key])
    if changed:
        raise InterruptError(f"{name}: {', '.join(changed)} precede {store}")


def check_activation_order(scenario, observed):
    """The phase first, the mode after the map, the law before the kind, the trim last."""
    name = scenario.name
    initial = _fields((scenario.base, scenario.extension))
    final = _fields(rolling_launch_rows.engine_pass(
        (scenario.base, scenario.extension), scenario.inputs)[:2])
    transition = ("active_index_snapshot", "active_mode_snapshot", "regulator_kind",
                  "law_output", "active_max_trim")
    if any(initial[key] == final[key] for key in ("phase", *transition)):
        raise InterruptError(f"{name}: an activation field keeps its value")
    seen = {key: False for key in transition}
    for records in observed:
        fields = _fields(records)
        if fields["phase"] == initial["phase"]:
            _require_unchanged(name, "the phase", fields, initial, ACTIVATION_PRE_PHASE_FIELDS)
        if (fields["active_mode_snapshot"] != initial["active_mode_snapshot"]
                and fields["active_index_snapshot"] != final["active_index_snapshot"]):
            raise InterruptError(f"{name}: the mode precedes the map")
        if (fields["regulator_kind"] != initial["regulator_kind"]
                and fields["law_output"] == initial["law_output"]):
            raise InterruptError(f"{name}: the kind precedes the law output")
        if fields["active_max_trim"] != initial["active_max_trim"] and (
                any(fields[key] != final[key] for key in ("phase", *transition[:3]))
                or fields["law_output"] == initial["law_output"]):
            raise InterruptError(f"{name}: the trim of the run precedes an activation store")
        for key in transition:
            seen[key] |= fields[key] != initial[key]
    if not all(seen.values()):
        raise InterruptError(f"{name}: no boundary observes {[k for k, v in seen.items() if not v]}")


def error_pair_end(records, regulator):
    """PC of the LDC that lowers the mask of the error pair, the first inside ``regulator``."""
    for index, (pc, opcode, _delay) in enumerate(records):
        if regulator[0] <= pc < regulator[1] and _loads_sr(opcode) and not raises_mask(records,
                                                                                         index):
            return pc
    raise InterruptError("the RPM regulator lowers no mask")


def run_interrupt_rows(fixture, build_dir, *, engine, regulator, definitions, invoke_object,
                       rom_object):
    """Build the interrupt harness, run its passes and every injected publication.

    ``regulator`` spans the RPM controller, its fraction and the control
    publisher. A publication of the RPM activation accepted inside it after
    the error pair and before the publisher mask is publication B.
    ``definitions`` are the compiler definitions of the layout addresses.
    """
    scenarios = rolling_launch_rows.interrupt_scenarios()
    include = build_dir / "rows-irq"
    include.mkdir()
    (include / "rolling_launch_irq_rows.h").write_text(
        rolling_launch_rows.render_interrupts(scenarios), encoding="utf-8")
    handler_object = build_dir / "rolling-launch-irq-handler.o"
    base_verifier.run_command([base_verifier.AS, "--big", "--isa=sh2e", "-o", handler_object,
                               TOOL_DIR / "irq_rolling.s"])
    elf = build_dir / "rolling-launch-irq.elf"
    base_verifier.run_command([
        base_verifier.GCC, "-m2e", "-mb", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
        *definitions, f"-I{include}", f"-Wl,-Ttext-segment={base_verifier.DRIVER_TEXT_BASE:#x}",
        "-Wl,--section-start=.rom=0", "-o", elf, TOOL_DIR / "rolling_launch_irq.c",
        handler_object, invoke_object, rom_object,
    ], timeout=120)
    ranges, _words = base_verifier._invoke_trace_bindings(
        elf, invoke_object, fixture, build_dir, names=frozenset({"_invoke_regs"}))
    symbols = {}
    for line in base_verifier.run_command([base_verifier.NM, "--defined-only", elf]).stdout.splitlines():
        parts = line.split()
        if len(parts) == 3:
            symbols[parts[2]] = int(parts[0], 16)
    handler = symbols["_irq_rolling_handler"]
    memory = f"--memory-region={base_verifier.TEST_RAM_BASE:#x},64k"
    clean = {key: value for key, value in os.environ.items()
             if not key.startswith(("VQ_SH_IRQ_", "VQ_SH_PC_TRACE_"))}
    trace = build_dir / "rolling-launch-irq.pc-trace"
    disabled = base_verifier.run_command([base_verifier.RUN, memory, elf], timeout=120, env={
        **clean, "VQ_SH_PC_TRACE_FILE": str(trace), "VQ_SH_PC_TRACE_FORMAT": "v1",
        "VQ_SH_PC_TRACE_RANGES": ",".join(
            f"{start:x}:{end:x}" for start, end in ((0, len(fixture)), *ranges))})
    baseline = parse(disabled.stdout, scenarios)
    for row, scenario in zip(baseline, scenarios):
        check_disabled(row, scenario)
    records = base_verifier.read_pc_trace(trace)
    found = triggers(records, engine, ranges[0])
    pair = error_pair_end(records, regulator)
    if {item.scenario for item in found} != set(range(len(scenarios))):
        raise InterruptError("an interrupt scenario has no instruction boundary")
    observed = {index: [] for index in range(len(scenarios))}
    publication_b = 0
    elf_bytes = elf.read_bytes()
    runs = injections(found)
    for number, item in enumerate(runs):
        report = build_dir / f"irq-{number}.report"
        result = base_verifier.run_command([base_verifier.RUN, memory, elf], timeout=60, env={
            **clean, "VQ_SH_IRQ_PC": f"{item.pc:x}", "VQ_SH_IRQ_COUNT": str(item.count),
            "VQ_SH_IRQ_LEVEL": str(LEVEL), "VQ_SH_IRQ_VECTOR": str(VECTOR),
            "VQ_SH_IRQ_REPORT": str(report)})
        lines = report.read_text(encoding="ascii").splitlines()
        match = REPORT.fullmatch(lines[0]) if len(lines) == 1 else None
        if match is None:
            raise InterruptError(f"{item.pc:#010x} #{item.count}: malformed report {lines}")
        triggered, accepted, entered, saved_sr = (int(value, 16) for value in match.groups())
        if (triggered, accepted, entered) != (item.pc, item.accepted, handler) or saved_sr & SR_I:
            raise InterruptError(
                f"{item.pc:#010x} #{item.count}: accepted {accepted:#010x} "
                f"handler {entered:#010x} sr {saved_sr:#010x}, expected {item.accepted:#010x}")
        rows = parse(result.stdout, scenarios)
        for index, (row, scenario) in enumerate(zip(rows, scenarios)):
            if index != item.scenario:
                if row != baseline[index]:
                    raise InterruptError(f"{scenario.name}: a publication in another pass "
                                         "changes its observations")
                continue
            try:
                seen, ready = check_interrupted(row, scenario)
            except InterruptError as error:
                raise InterruptError(f"{item.pc:#010x} #{item.count} accepted at "
                                     f"{item.accepted:#010x}: {error}") from error
            observed[index].append(seen)
            if (scenario.kind == "activation" and scenario.regulator == model.RegulatorKind.RPM
                    and pair < item.accepted < regulator[1]):
                if ready:
                    raise InterruptError(f"{item.pc:#010x} #{item.count} accepted at "
                                         f"{item.accepted:#010x}: publication B passes the check")
                publication_b += 1
    if elf.read_bytes() != elf_bytes:
        raise InterruptError("interrupt harness ELF changes during execution")
    for index, scenario in enumerate(scenarios):
        if scenario.kind == "activation":
            check_activation_order(scenario, observed[index])
    if not publication_b:
        raise InterruptError("no publication falls between the error pair of the RPM activation "
                             "and the publisher mask")
    deferred = sum(item.deferred for item in runs)
    after_ldc = sum(item.after_ldc for item in runs)
    if not deferred or not after_ldc:
        raise InterruptError("no instruction boundary falls inside a masked group")
    return (f"VQ_SH_ELF_ROLLING_IRQ status=PASS scenarios={len(scenarios)} "
            f"boundaries={len(found)} stores={sum(item.store for item in found)} "
            f"injections={len(runs)} deferred={deferred} after_ldc={after_ldc} "
            f"publication_b={publication_b} level={LEVEL}")
