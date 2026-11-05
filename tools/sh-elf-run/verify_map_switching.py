#!/usr/bin/env python3
"""Verify the complete JK08A map-switching implementation with GNU SH tools.

The verifier independently assembles every tracked source with GNU binutils,
requires byte identity with the SHA-locked Ghidra payloads, composes the exact
one-MiB verification fixture, and executes its behavioral harness in GNU
sh-elf-run. Startup and limiter commit paths have measured instruction coverage.
It also executes the exact failed Overlay 07 BRA/MOV.L pair at
its original addresses and requires the simulator's illegal-instruction stop.
The relocated runtime targets follow. ``--rom`` executes only the stages that
cover one ROM: the native stages for the exact family, or the target of one
relocated ROM.
"""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import traceback


ROOT = Path(__file__).resolve().parents[2]
TOOL_DIR = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from patches import apply_map_switching
from patches import map_switching_assembly as assembly_model
from patches import map_switching_compose as composer
from patches import map_switching_layout as layout_model
from patches import runtime_targets
from execution_report import stage
from elf_storage_layout import ELFStorageError, require_separate_storage


EXPECTED_SIMULATOR_VERSION = "16.3"
EXPECTED_COMPOSITION_SHA256 = (
    "ebfbb3cb1172b01dcc7252674477a44e60423f4ec4415069b8b1a19d6b7d7533"
)
EXPECTED_COMPOSITION_CHANGED_BYTES = 5803
EXPECTED_COMPOSITION_WRITE_BYTES = 6316
EXPECTED_INSTRUCTION_COUNT = 435
EXPECTED_CODE_ENTRY_COUNT = 12
TEST_RAM_BASE = 0x01000000
HIGH_RAM_BASE = 0xFFFE8000
ROM_SIZE = 0x00100000
DRIVER_TEXT_BASE = 0x00110000
RETURN_STUB = bytes.fromhex("000b0009")
INCIDENT_ADDRESS = 0x000D2314
INCIDENT_BRANCH_WORD = 0xAFAC
INCIDENT_UNSAFE_SLOT_WORD = 0xD304
INCIDENT_SAFE_SLOT_WORD = 0x0009
THROTTLE_CLUSTER_ORIGIN = 0x0007584C
THROTTLE_CLUSTER_WINDOWS = ((0x0007584E, 0x0007587A), (0x00075C32, 0x00075C48))
THROTTLE_CLUSTER_POOLS = ((0x00075938, 2), (0x0007593A, 2), (0x00075958, 4), (0x00075964, 4))
THROTTLE_CLUSTER_BOUNDARY = 0x0007587A

FUEL_CUT_ORIGIN = 0x0004F280
FUEL_CUT_START = 0x0004F282
FUEL_CUT_END = 0x0004F324
FUEL_CUT_POOLS = tuple(range(0x0004F460, 0x0004F474, 4))

THROTTLE_SCALAR_START = 0x00077AC0
THROTTLE_SCALAR_END = 0x00077ACE
THROTTLE_SCALAR_POOL = 0x00077BAC

AS = "sh-elf-as"
LD = "sh-elf-ld"
OBJCOPY = "sh-elf-objcopy"
GCC = "sh-elf-gcc"
RUN = "sh-elf-run"
NM = "sh-elf-nm"
# ELF metadata only; diagnostic branch display is excluded in gnu-disassembly.md.
OBJDUMP = "sh-elf-objdump"
PC_COVERAGE_UNITS = (
    "startup_wrapper", "limiter_commit", "selector_host",
    "cruise_feedback_wrapper", "cruise_feedback_engine",
)
PC_INVOKE_SYMBOLS = {"_invoke_r0", "_invoke_r4", "_invoke_throttle_scalar"}
ADAPTER_COVERAGE_UNITS = (
    "adapter_select_helper", "lookup_adapters", "full_dfco_adapter",
    "idle_ignition_adapter",
)


def _map_coverage_units(layout):
    return tuple(layout.assembly_unit_by_key) if layout is not None else PC_COVERAGE_UNITS


def _adapter_coverage_units(layout):
    return ADAPTER_COVERAGE_UNITS + tuple(
        key for key in ("secondary_cvtc_adapter", "ignition_state_adapter")
        if layout is not None and key in layout.assembly_unit_by_key
    )


class VerificationError(RuntimeError):
    """Raised when a tool or an executable verification contract fails."""


def run_command(
    command,
    *,
    cwd=None,
    input_text=None,
    expected_returncode=0,
    timeout=60,
    env=None,
):
    """Run one command and return its completed process or raise."""
    display = " ".join(str(item) for item in command)
    try:
        result = subprocess.run(
            [str(item) for item in command],
            cwd=cwd,
            input=input_text,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
            env=env,
        )
    except FileNotFoundError as error:
        raise VerificationError(f"required tool is missing: {command[0]}") \
            from error
    except subprocess.TimeoutExpired as error:
        raise VerificationError(
            f"command timed out after {timeout}s: {display}"
        ) from error
    if result.returncode != expected_returncode:
        details = "\n".join(
            part.rstrip()
            for part in (result.stdout, result.stderr)
            if part.strip()
        )
        raise VerificationError(
            f"command returned {result.returncode}, expected "
            f"{expected_returncode}: {display}"
            + (f"\n{details}" if details else "")
        )
    return result


def preprocess_gnu_source(source):
    """Translate the small Ghidra source dialect to GNU assembler syntax."""
    result = []
    for raw_line in assembly_model.expand_includes(source).splitlines():
        line = raw_line.split("//", 1)[0]
        match = re.match(r"^(\s*)\.align\s+(.+?)\s*$", line)
        if match:
            line = f"{match.group(1)}.balign {match.group(2)}"
        immediate = re.match(
            r"^(\s*)(add|and|cmp/eq|or|tst|xor)\s+"
            r"(?P<value>-?(?:0x[0-9a-f]+|[0-9]+)),",
            line,
            re.IGNORECASE,
        )
        if immediate:
            start, end = immediate.span("value")
            line = line[:start] + "#" + line[start:end] + line[end:]
        result.append(line)
    return "\n".join(result) + "\n"


def _source_value(statement):
    values = [item.strip() for item in statement.text.split(",")]
    if len(values) != 1:
        raise VerificationError(
            f"expected one value at {statement.address:#x}: "
            f"{statement.text}"
        )
    return int(values[0].replace("_", ""), 0)


def assemble_unit(unit, parsed, build_dir, source_text=None):
    """Assemble one absolute source and reconstruct its fill-aware blob."""
    source_path = ROOT / "patches" / unit.source
    object_path = build_dir / f"{unit.key}.o"
    elf_path = build_dir / f"{unit.key}.elf"
    binary_path = build_dir / f"{unit.key}.raw"
    if source_text is None:
        source_text = source_path.read_text(encoding="utf-8")
    source = preprocess_gnu_source(source_text)

    run_command(
        [AS, "--big", "--isa=sh2e", "-o", object_path, "-"],
        input_text=source,
    )
    run_command(
        [
            LD,
            "-EB",
            "-Ttext=0",
            "--entry=0",
            "-o",
            elf_path,
            object_path,
        ]
    )
    run_command([OBJCOPY, "-O", "binary", elf_path, binary_path])
    raw = binary_path.read_bytes()
    blob = bytearray([unit.fill] * unit.span.size)
    for statement in parsed.statements:
        source_end = statement.address + statement.size
        if source_end > len(raw):
            raise VerificationError(
                f"{unit.key}: GNU binary ends before {source_end:#x}"
            )
        destination = statement.address - unit.span.start
        blob[destination : destination + statement.size] = raw[
            statement.address : source_end
        ]
    return bytes(blob)


def assemble_all_units(layout, parsed_by_unit, build_dir, verbose=False):
    """Build all units independently and require tracked payload identity."""
    tracked = apply_map_switching.load_payloads(layout)
    assembled = {}
    for unit in layout.assembly_units:
        blob = assemble_unit(unit, parsed_by_unit[unit.key], build_dir)
        digest = hashlib.sha256(blob).hexdigest()
        if blob != tracked[unit.key]:
            first = next(
                index
                for index, (actual, expected) in enumerate(
                    zip(blob, tracked[unit.key])
                )
                if actual != expected
            )
            raise VerificationError(
                f"{unit.key}: GNU output differs from the tracked payload "
                f"at ROM address {unit.span.start + first:#x}"
            )
        if digest != unit.expected_sha256:
            raise VerificationError(
                f"{unit.key}: GNU SHA-256 is {digest}, expected "
                f"{unit.expected_sha256}"
            )
        if verbose:
            print(
                f"GNU_ASSEMBLY unit={unit.key} bytes={len(blob)} "
                f"sha256={digest}"
            )
        assembled[unit.key] = blob
    return assembled


def require_composition(layout, blobs):
    """Build and lock the complete non-flashable verification composition."""
    result = composer.compose(layout=layout, blobs=blobs)
    expected = (
        EXPECTED_COMPOSITION_SHA256,
        EXPECTED_COMPOSITION_CHANGED_BYTES,
        EXPECTED_COMPOSITION_WRITE_BYTES,
        EXPECTED_INSTRUCTION_COUNT,
        EXPECTED_CODE_ENTRY_COUNT,
    )
    actual = (
        result.sha256,
        result.changed_bytes,
        result.permitted_write_bytes,
        result.instruction_count,
        result.code_entry_count,
    )
    if actual != expected:
        raise VerificationError(
            f"composition contract differs: actual={actual} expected={expected}"
        )
    return result


def alias_high_ram(value):
    """Map an exact ECU high-RAM address into simulator test RAM."""
    if value < HIGH_RAM_BASE or value > 0xFFFFFFFF:
        raise VerificationError(f"not a high-RAM address: {value:#x}")
    return TEST_RAM_BASE + (value & 0xFFFF)


def assemble_throttle_scalar_consumer(build_dir):
    """Reconstruct the clamp and the original observation-boundary bytes."""
    object_path = build_dir / "map-switching-throttle-scalar.o"
    elf_path = build_dir / "map-switching-throttle-scalar.elf"
    binary_path = build_dir / "map-switching-throttle-scalar.bin"
    run_command([
        AS, "--big", "--isa=sh2e", "-o", object_path,
        TOOL_DIR / "map_switching_throttle_scalar_consumer.s",
    ])
    run_command([
        LD, "-EB", f"-Ttext={THROTTLE_SCALAR_START:#x}",
        f"--entry={THROTTLE_SCALAR_START:#x}", "-o", elf_path, object_path,
    ])
    run_command([
        OBJCOPY, "-O", "binary", "--only-section=.text",
        elf_path, binary_path,
    ])
    return binary_path.read_bytes()


def require_throttle_scalar_consumer_bytes(stock, composed, reconstructed, layout):
    """Bind the unchanged clamp and the authoritative changed pool word."""
    if len(reconstructed) != THROTTLE_SCALAR_POOL + 4 - THROTTLE_SCALAR_START:
        raise VerificationError("throttle scalar reconstruction extent differs")
    extent = THROTTLE_SCALAR_END + len(RETURN_STUB) - THROTTLE_SCALAR_START
    for name, image in (("stock", stock), ("composed", composed)):
        if image[THROTTLE_SCALAR_START:THROTTLE_SCALAR_START + extent] != reconstructed[:extent]:
            raise VerificationError(f"throttle scalar {name} instructions differ")
    hook = next(row for row in layout.hooks if row.key == "rev_throttle_scalar_base")
    if hook.address != THROTTLE_SCALAR_POOL or hook.width != 4:
        raise VerificationError("throttle scalar pointer hook differs")
    offset = THROTTLE_SCALAR_POOL - THROTTLE_SCALAR_START
    expected = reconstructed[offset:offset + 4]
    if stock[THROTTLE_SCALAR_POOL:THROTTLE_SCALAR_POOL + 4] != expected:
        raise VerificationError("throttle scalar stock pool differs")
    if int.from_bytes(expected, "big") != hook.stock:
        raise VerificationError("throttle scalar stock pointer differs")
    if composed[THROTTLE_SCALAR_POOL:THROTTLE_SCALAR_POOL + 4] != hook.replacement.to_bytes(4, "big"):
        raise VerificationError("throttle scalar composed pool differs")


def prepare_throttle_scalar_fixture(fixture):
    """Translate the bound pointer and install only the outside return boundary."""
    value = int.from_bytes(fixture[THROTTLE_SCALAR_POOL:THROTTLE_SCALAR_POOL + 4], "big")
    fixture[THROTTLE_SCALAR_POOL:THROTTLE_SCALAR_POOL + 4] = alias_high_ram(value).to_bytes(4, "big")
    fixture[THROTTLE_SCALAR_END:THROTTLE_SCALAR_END + len(RETURN_STUB)] = RETURN_STUB


def verify_throttle_scalar_consumer_binding(layout, composition, build_dir):
    require_throttle_scalar_consumer_bytes(
        layout_model.validate_image(layout).data, composition.data,
        assemble_throttle_scalar_consumer(build_dir), layout,
    )


def assemble_fuel_cut_consumer(build_dir):
    """Reconstruct the consumer of the changed fuel-cut pointer independently."""
    object_path = build_dir / "map-switching-fuel-cut.o"
    elf_path = build_dir / "map-switching-fuel-cut.elf"
    binary_path = build_dir / "map-switching-fuel-cut.bin"
    run_command([
        AS, "--big", "--isa=sh2e", "-o", object_path,
        TOOL_DIR / "map_switching_fuel_cut_consumer.s",
    ])
    run_command([
        LD, "-EB", f"-Ttext={FUEL_CUT_ORIGIN:#x}",
        f"--entry={FUEL_CUT_START:#x}", "-o", elf_path, object_path,
    ])
    run_command([
        OBJCOPY, "-O", "binary", "--only-section=.text",
        elf_path, binary_path,
    ])
    return binary_path.read_bytes()


def require_fuel_cut_consumer_bytes(stock, composed, reconstructed, layout):
    """Bind every executed consumer instruction and pool to the owned image."""
    if len(reconstructed) != FUEL_CUT_POOLS[-1] + 4 - FUEL_CUT_ORIGIN:
        raise VerificationError("fuel-cut consumer reconstruction extent differs")
    start = FUEL_CUT_START - FUEL_CUT_ORIGIN
    end = FUEL_CUT_END - FUEL_CUT_ORIGIN
    instructions = reconstructed[start:end]
    for name, image in (("stock", stock), ("composed", composed)):
        if image[FUEL_CUT_START:FUEL_CUT_END] != instructions:
            raise VerificationError(f"fuel-cut consumer {name} instructions differ")
    hook = next(row for row in layout.hooks if row.key == "rev_fuel_cut_base")
    if hook.address != 0x0004F468 or hook.width != 4:
        raise VerificationError("fuel-cut consumer pointer hook differs")
    for address in FUEL_CUT_POOLS:
        offset = address - FUEL_CUT_ORIGIN
        expected = reconstructed[offset:offset + 4]
        if stock[address:address + 4] != expected:
            raise VerificationError(f"fuel-cut consumer stock pool differs at {address:#x}")
        if address == hook.address:
            if int.from_bytes(expected, "big") != hook.stock:
                raise VerificationError("fuel-cut consumer stock pointer differs")
            expected = hook.replacement.to_bytes(4, "big")
        if composed[address:address + 4] != expected:
            raise VerificationError(f"fuel-cut consumer composed pool differs at {address:#x}")


def relocate_fuel_cut_consumer_literals(fixture):
    """Translate three bound RAM data words; preserve all consumer instructions."""
    instructions = bytes(fixture[FUEL_CUT_START:FUEL_CUT_END])
    for address in (0x0004F460, 0x0004F468, 0x0004F46C):
        value = int.from_bytes(fixture[address:address + 4], "big")
        fixture[address:address + 4] = alias_high_ram(value).to_bytes(4, "big")
    if fixture[FUEL_CUT_START:FUEL_CUT_END] != instructions:
        raise VerificationError("fuel-cut RAM translation changes instructions")
    return 3


def verify_fuel_cut_consumer_binding(layout, composition, build_dir):
    require_fuel_cut_consumer_bytes(
        layout_model.validate_image(layout).data, composition.data,
        assemble_fuel_cut_consumer(build_dir), layout,
    )


def verify_throttle_cluster_binding(layout, composition, build_dir):
    """Independently assemble the bounded prefix, epilogue and boundary branch."""
    obj = build_dir / "throttle-cluster.o"
    elf = build_dir / "throttle-cluster.elf"
    binary = build_dir / "throttle-cluster.bin"
    run_command([AS, "--big", "--isa=sh2e", "-o", obj,
                 TOOL_DIR / "map_switching_throttle_cluster.s"])
    run_command([LD, "-EB", f"-Ttext={THROTTLE_CLUSTER_ORIGIN:#x}",
                 "--entry=0x7584e", "-o", elf, obj])
    run_command([OBJCOPY, "-O", "binary", "--only-section=.text", elf, binary])
    reconstructed = binary.read_bytes()
    require_throttle_cluster_bytes(layout_model.validate_image(layout).data,
                                   composition.data, reconstructed, layout)
    return reconstructed


def require_throttle_cluster_bytes(stock, composed, reconstructed, layout):
    """Bind original instructions and operands, keeping the boundary separate."""
    if len(reconstructed) != 0x75C48 - THROTTLE_CLUSTER_ORIGIN:
        raise VerificationError("throttle-cluster reconstruction extent differs")
    for start, end in THROTTLE_CLUSTER_WINDOWS:
        expected = reconstructed[start - THROTTLE_CLUSTER_ORIGIN:end - THROTTLE_CLUSTER_ORIGIN]
        for name, image in (("stock", stock), ("composed", composed)):
            if image[start:end] != expected:
                raise VerificationError(f"throttle-cluster {name} instructions differ at {start:#x}")
    hook = next(row for row in layout.hooks if row.key == "rev_throttle_cluster_base")
    if (hook.address, hook.width, hook.stock, hook.replacement) != (0x75964, 4, 0x9424, 0xFFFF5D20):
        raise VerificationError("throttle-cluster pointer hook differs")
    for address, width in THROTTLE_CLUSTER_POOLS:
        offset = address - THROTTLE_CLUSTER_ORIGIN
        expected = reconstructed[offset:offset + width]
        if stock[address:address + width] != expected:
            raise VerificationError(f"throttle-cluster stock pool differs at {address:#x}")
        if address == hook.address:
            expected = hook.replacement.to_bytes(width, "big")
        if composed[address:address + width] != expected:
            raise VerificationError(f"throttle-cluster composed pool differs at {address:#x}")
    address = THROTTLE_CLUSTER_BOUNDARY
    for image in (stock, composed):
        if image[address:address + 4] != bytes.fromhex("dc3be015"):
            raise VerificationError("throttle-cluster original boundary differs")
    boundary = reconstructed[address - THROTTLE_CLUSTER_ORIGIN:address + 4 - THROTTLE_CLUSTER_ORIGIN]
    word = int.from_bytes(boundary[:2], "big")
    displacement = word & 0xFFF
    if displacement & 0x800:
        displacement -= 0x1000
    if word >> 12 != 0xA or address + 4 + displacement * 2 != 0x75C32 or boundary[2:] != bytes.fromhex("0009"):
        raise VerificationError("throttle-cluster assembled boundary differs")


def install_throttle_cluster_fixture(fixture, reconstructed):
    """Translate bound data operands and install the sole enabled-body boundary."""
    for address in (0x75958, 0x75964):
        original = int.from_bytes(fixture[address:address + 4], "big")
        fixture[address:address + 4] = alias_high_ram(original).to_bytes(4, "big")
    address = THROTTLE_CLUSTER_BOUNDARY
    offset = address - THROTTLE_CLUSTER_ORIGIN
    fixture[address:address + 4] = reconstructed[offset:offset + 4]


def relocate_assembly_ram_literals(fixture, parsed_by_unit):
    """Relocate only validated assembly data literals, never instructions."""
    relocated = 0
    for parsed in parsed_by_unit.values():
        for statement in parsed.statements:
            if statement.kind != "long":
                continue
            value = _source_value(statement)
            if value < HIGH_RAM_BASE:
                continue
            encoded = value.to_bytes(4, "big")
            address = statement.address
            if fixture[address : address + 4] != encoded:
                raise VerificationError(
                    f"RAM literal at {address:#x} differs before relocation"
                )
            fixture[address : address + 4] = alias_high_ram(value).to_bytes(
                4, "big"
            )
            relocated += 1
    return relocated


def differentiate_map_copies(fixture, layout):
    """Give dynamic-only map copies distinct bytes to expose wrong slots."""
    changed = 0
    for family_index, family in enumerate(layout.families, 1):
        for slot_index, address in enumerate(family.copies, 1):
            for offset in range(family.byte_length):
                fixture[address + offset] = (
                    fixture[address + offset]
                    + family_index * 17
                    + slot_index * 29
                    + offset
                ) & 0xFF
                changed += 1
    return changed


def install_stock_return_stubs(fixture, layout):
    """Replace only documented external stock callees with RTS/NOP."""
    keys = {
        "selector_host_call",
        "startup_initializer",
        "overrun_cut_lookup",
        "overrun_restore_lookup",
        "ignition_lookup_493e8",
        "ignition_lookup_4e1c0_a",
        "ignition_lookup_4e1c0_b",
        "fuel_compensation_lookup_2c648",
        "fuel_compensation_lookup_3be3c",
        "exhaust_cvtc_target_lookup",
        "idle_ignition_lookup",
        "cruise_feedback_serializer",
    }
    hooks = {hook.key: hook for hook in layout.hooks}
    if not keys <= hooks.keys():
        raise VerificationError(
            f"layout lacks stock-call hooks: {sorted(keys - hooks.keys())}"
        )
    targets = {hooks[key].stock for key in keys}
    for address in targets:
        fixture[address : address + len(RETURN_STUB)] = RETURN_STUB
    return len(targets)


def build_dynamic_fixture(composition, layout, parsed_by_unit, *, throttle_reconstruction=None):
    """Create a simulator-only fixture after the exact composition passes."""
    fixture = bytearray(composition.data)
    if len(fixture) != ROM_SIZE:
        raise VerificationError(
            f"composition size is {len(fixture)}, expected {ROM_SIZE}"
        )
    relocated = relocate_assembly_ram_literals(fixture, parsed_by_unit)
    relocated += relocate_fuel_cut_consumer_literals(fixture)
    differentiated = differentiate_map_copies(fixture, layout)
    if throttle_reconstruction is not None:
        install_throttle_cluster_fixture(fixture, throttle_reconstruction)
        relocated += 2
    stubs = install_stock_return_stubs(fixture, layout)
    prepare_throttle_scalar_fixture(fixture)
    relocated += 1
    stubs += 1
    if fixture[THROTTLE_SCALAR_START:THROTTLE_SCALAR_END] != composition.data[THROTTLE_SCALAR_START:THROTTLE_SCALAR_END]:
        raise VerificationError("throttle scalar simulator fixture changes instructions")
    if throttle_reconstruction is not None:
        for start, end in THROTTLE_CLUSTER_WINDOWS:
            if fixture[start:end] != composition.data[start:end]:
                raise VerificationError("throttle-cluster simulator fixture changes instructions")
    if fixture[FUEL_CUT_START:FUEL_CUT_END] != composition.data[FUEL_CUT_START:FUEL_CUT_END]:
        raise VerificationError("fuel-cut consumer simulator fixture changes instructions")
    if throttle_reconstruction is not None:
        address = THROTTLE_CLUSTER_BOUNDARY
        offset = address - THROTTLE_CLUSTER_ORIGIN
        if fixture[address:address + 4] != throttle_reconstruction[offset:offset + 4]:
            raise VerificationError("throttle-cluster simulator boundary differs after stubs")
    return bytes(fixture), relocated, differentiated, stubs


def build_rom_object(fixture, build_dir):
    fixture_path = build_dir / "map-switching.sim-fixture"
    object_path = build_dir / "map-switching-rom.o"
    fixture_path.write_bytes(fixture)
    run_command(
        [
            OBJCOPY,
            "-I",
            "binary",
            "-O",
            "elf32-sh",
            "-B",
            "sh",
            "--rename-section",
            ".data=.rom,alloc,load,code,data,contents",
            fixture_path,
            object_path,
        ]
    )
    return object_path


def read_pc_trace(path):
    """Require the observer's ordered, complete host-side instruction stream."""
    try:
        lines = Path(path).read_text(encoding="ascii").splitlines()
    except OSError as error:
        raise VerificationError("GNU PC observer did not produce its trace") from error
    if not lines or lines[0] != "VQ_SH_PC_TRACE version=1":
        raise VerificationError("GNU PC trace lacks its version header")
    terminal = re.fullmatch(r"VQ_SH_PC_TRACE end=complete records=([0-9]+)", lines[-1])
    if terminal is None:
        raise VerificationError("GNU PC trace lacks its complete terminal")
    records = []
    for line in lines[1:-1]:
        match = re.fullmatch(r"pc=([0-9a-f]{8}) opcode=([0-9a-f]{4}) delay=([01])", line)
        if match is None:
            raise VerificationError("malformed GNU PC trace record")
        pc, word, delay = (int(value, 16) for value in match.groups())
        if pc & 1:
            raise VerificationError(f"unaligned executed PC {pc:#010x}")
        records.append((pc, word, delay))
    if not records or len(records) != int(terminal.group(1)):
        raise VerificationError("GNU PC trace record count differs from its terminal")
    return records


def _trace_successor(records, index, delayed):
    pc = records[index][0]
    following = index + 1
    if delayed:
        if following >= len(records) or records[following][0::2] != (pc + 2, 1):
            raise VerificationError(f"missing executed delay slot at {pc + 2:#010x}")
        following += 1
    if following >= len(records) or records[following][2]:
        raise VerificationError(f"missing executed successor of {pc:#010x}")
    return records[following][0]


def require_map_fixture_bindings(fixture, composed_image, parsed_by_unit, layout):
    """Bind map instructions and ROM control operands before any execution."""
    if len(fixture) != len(composed_image):
        raise VerificationError("map fixture and composed image extents differ")

    def control_pool(parsed, statement, register):
        literal = assembly_model.PC_RELATIVE_RE.fullmatch(statement.text) if statement else None
        if literal is None or literal.group("width") != "l" or literal.group("register") != register:
            raise VerificationError("unbound map ROM control operand")
        pool = parsed.labels[literal.group("label")]
        expected = composed_image[pool:pool + 4]
        if len(expected) != 4 or fixture[pool:pool + 4] != expected:
            raise VerificationError(f"map ROM control pool differs at {pool:#010x}")

    for key in _map_coverage_units(layout):
        if key not in parsed_by_unit:
            raise VerificationError(f"missing typed map unit: {key}")
        parsed = parsed_by_unit[key]
        rows = [row for row in parsed.statements if row.kind == "instruction"]
        for row in rows:
            pc = row.address
            if fixture[pc:pc + 2] != composed_image[pc:pc + 2]:
                raise VerificationError(f"simulator changes payload instruction at {pc:#010x}")
            mnemonic = assembly_model._mnemonic(row)
            if mnemonic in {"jsr", "jmp"} and row.text in {"jsr @r0", "jmp @r0"}:
                control_pool(parsed, parsed.statement_by_address.get(pc - 2), "r0")
        if layout is not None and key in _adapter_coverage_units(layout):
            unit = layout.assembly_unit_by_key[key]
            for region_key in unit.code_regions:
                if region_key == "adapter_select_helper":
                    continue
                region = layout.code_region_by_key[region_key]
                first = parsed.statement_by_address.get(region.entry)
                literal = assembly_model.PC_RELATIVE_RE.fullmatch(first.text) if first else None
                if literal is None or literal.group("width") != "l" or literal.group("register") != "r3":
                    raise VerificationError(f"adapter lacks its entry R3 binding at {region.entry:#010x}")
                control_pool(parsed, first, "r3")


def require_payload_coverage(records, fixture, parsed_by_unit, invoke_words, *, composed_image, throttle_cluster=False, adapter_layout=None):
    """Measure the declared JK08A payload entries and optional bounded prefix."""
    require_map_fixture_bindings(fixture, composed_image, parsed_by_unit, adapter_layout)
    instructions, entries, outcomes, slots, call_targets = {}, set(), set(), set(), {}
    direct_targets, jump_targets, adapter_owners, stock_targets = {}, {}, {}, {}
    units = _map_coverage_units(adapter_layout)
    adapter_units = _adapter_coverage_units(adapter_layout)
    helper_entry = None
    if adapter_layout is not None:
        helper_entry = adapter_layout.code_region_by_key["adapter_select_helper"].entry
    for key in units:
        parsed = parsed_by_unit[key]
        rows = [row for row in parsed.statements if row.kind == "instruction"]
        if adapter_layout is None:
            entries.add(min(row.address for row in rows))
        else:
            unit = adapter_layout.assembly_unit_by_key[key]
            regions = [adapter_layout.code_region_by_key[name] for name in unit.code_regions]
            entries.update(region.entry for region in regions)
            if key in adapter_units:
                for region in regions:
                    owned = [row for row in rows if region.span.start <= row.address < region.span.end]
                    adapter_owners.update((row.address, region.entry) for row in owned)
                    if region.entry == helper_entry:
                        checked = owned
                    else:
                        first = owned[0]
                        literal = assembly_model.PC_RELATIVE_RE.fullmatch(first.text)
                        if (first.address != region.entry or literal is None
                                or literal.group("width") != "l" or literal.group("register") != "r3"):
                            raise VerificationError(f"adapter lacks its entry R3 binding at {region.entry:#010x}")
                        pool = parsed.labels[literal.group("label")]
                        stock_targets[region.entry] = int.from_bytes(composed_image[pool:pool + 4], "big")
                        if fixture[stock_targets[region.entry]:stock_targets[region.entry] + 4] != RETURN_STUB:
                            raise VerificationError("adapter stock boundary is not the declared RTS/NOP stub")
                        checked = owned[1:]
                    for row in checked:
                        if "r3" in assembly_model.REGISTER_RE.findall(row.text) and row.text != "jmp @r3":
                            raise VerificationError(f"unsupported adapter R3 use at {row.address:#010x}")
        for row in rows:
            pc = row.address
            instructions[pc] = int.from_bytes(fixture[pc:pc + 2], "big")
            mnemonic = assembly_model._mnemonic(row)
            if mnemonic in assembly_model.DELAYED_CONTROL_MNEMONICS:
                slots.add(pc + 2)
            if mnemonic == "bra":
                direct_targets[pc] = assembly_model._validate_direct_branch_encoding(parsed, row, instructions[pc])
            if key in adapter_units and adapter_layout is not None:
                if mnemonic in {"jsr", "bsr", "bsrf", "braf", "rts", "rte"}:
                    raise VerificationError(f"unsupported adapter transfer at {pc:#010x}")
                if mnemonic == "jmp":
                    if row.text == "jmp @r3":
                        jump_targets[pc] = None  # Inherited from the exact original adapter entry.
                    elif row.text == "jmp @r0":
                        previous = parsed.statement_by_address.get(pc - 2)
                        literal = assembly_model.PC_RELATIVE_RE.fullmatch(previous.text) if previous else None
                        if literal is None or literal.group("width") != "l" or literal.group("register") != "r0":
                            raise VerificationError(f"unbound adapter tail target at {pc:#010x}")
                        pool = parsed.labels[literal.group("label")]
                        target = int.from_bytes(composed_image[pool:pool + 4], "big")
                        if target != helper_entry:
                            raise VerificationError(f"adapter tail does not target its helper at {pc:#010x}")
                        jump_targets[pc] = target
                    else:
                        raise VerificationError(f"unsupported adapter JMP at {pc:#010x}")
            if mnemonic in {"bt", "bf", "bt/s", "bf/s"}:
                target = assembly_model._validate_direct_branch_encoding(parsed, row, instructions[pc])
                outcomes.update(((pc, target), (pc, pc + (4 if mnemonic.endswith("/s") else 2))))
            if mnemonic in {"jsr", "bsr"}:
                previous = parsed.statement_by_address.get(pc - 2)
                literal = assembly_model.PC_RELATIVE_RE.fullmatch(previous.text) if previous else None
                if (mnemonic != "jsr" or literal is None or literal.group("width") != "l"
                        or literal.group("register") != "r0" or row.text != "jsr @r0"):
                    raise VerificationError(f"unbound call target in bounded payload at {pc:#010x}")
                pool = parsed.labels[literal.group("label")]
                call_targets[pc] = int.from_bytes(composed_image[pool:pool + 4], "big")
    fixture_boundary_pcs = set()
    if throttle_cluster:
        entries.add(0x7584E)
        for start, end in (*THROTTLE_CLUSTER_WINDOWS, (0x7587A, 0x7587E)):
            for pc in range(start, end, 2):
                instructions[pc] = int.from_bytes(fixture[pc:pc + 2], "big")
                if start == THROTTLE_CLUSTER_BOUNDARY:
                    fixture_boundary_pcs.add(pc)
        outcomes.update(((0x7586E, 0x75870), (0x7586E, 0x7587A)))
        slots.update((0x75878, 0x7587C, 0x75C46))
    seen, observed_outcomes, observed_slots, returned, call_returns = set(), set(), set(), set(), set()
    frames = []
    for index, (pc, word, delay) in enumerate(records):
        if pc < len(fixture) - 1:
            expected = int.from_bytes(fixture[pc:pc + 2], "big")
        elif pc in invoke_words:
            expected = invoke_words[pc]
        else:
            raise VerificationError(f"executed PC outside the bound ROM and invoke code: {pc:#010x}")
        if word != expected:
            raise VerificationError(f"executed opcode differs at {pc:#010x}: {word:04x} != {expected:04x}")
        seen.add(pc)
        if delay:
            if not index or records[index - 1][0] != pc - 2 or records[index - 1][2]:
                raise VerificationError(f"orphan executed delay slot at {pc:#010x}")
            observed_slots.add(pc)
            continue
        if pc in adapter_owners:
            owner = adapter_owners[pc]
            if not frames or frames[-1][4] not in stock_targets:
                raise VerificationError(f"adapter lacks its originating invoke frame at {pc:#010x}")
            if owner != helper_entry and owner != frames[-1][4]:
                raise VerificationError(f"adapter enters a different R3 owner at {pc:#010x}")
            if pc in entries:
                frames[-1][3].add(pc)
        conditional = word & 0xFF00 in {0x8900, 0x8B00, 0x8D00, 0x8F00}
        if pc in instructions and conditional:
            observed_outcomes.add((pc, _trace_successor(records, index, word & 0xFF00 in {0x8D00, 0x8F00})))
        if pc + 2 in slots:
            successor = _trace_successor(records, index, True)
            if throttle_cluster and pc in (0x75876, 0x7587A) and successor != 0x75C32:
                raise VerificationError(f"throttle-cluster boundary successor differs at {pc:#x}")
        if pc in direct_targets:
            target = _trace_successor(records, index, True)
            if target != direct_targets[pc]:
                raise VerificationError(f"executed BRA successor differs at {pc:#010x}")
        if pc in jump_targets:
            target = _trace_successor(records, index, True)
            expected = jump_targets[pc]
            if expected is None:
                expected = stock_targets[frames[-1][4]]
            if target != expected:
                raise VerificationError(f"executed adapter JMP at {pc:#010x} reaches {target:#010x}, expected {expected:#010x}")
        is_call = word & 0xF0FF == 0x400B or word & 0xF000 == 0xB000
        if is_call:
            target = _trace_successor(records, index, True)
            if pc in call_targets and target != call_targets[pc]:
                raise VerificationError(f"executed call at {pc:#010x} reaches {target:#010x}, expected {call_targets[pc]:#010x}")
            if frames or pc in instructions or target in entries:
                frames.append((pc, target, pc + 4, {target} & entries,
                               target if target in stock_targets else None))
        elif word == 0x000B and (frames or pc in instructions):
            target = _trace_successor(records, index, True)
            if not frames:
                raise VerificationError(f"payload return lacks its executed call at {pc:#010x}")
            call, entry, continuation, visited, adapter_origin = frames.pop()
            if adapter_origin is not None and pc != stock_targets[adapter_origin]:
                raise VerificationError(f"adapter tail returns outside its stock boundary at {pc:#010x}")
            if target != continuation:
                raise VerificationError(f"executed return at {pc:#010x} reaches {target:#010x}, expected {continuation:#010x}")
            returned.update(visited)
            if entry in entries or call in instructions:
                call_returns.add((call, entry, continuation))
    for missing in sorted(entries - seen):
        raise VerificationError(f"uncovered entry {missing:#010x}")
    for pc, target in sorted(outcomes - observed_outcomes):
        raise VerificationError(f"uncovered branch outcome {pc:#010x}->{target:#010x}")
    for missing in sorted(instructions.keys() - seen):
        raise VerificationError(f"uncovered instruction {missing:#010x}")
    if frames or entries - returned or call_targets.keys() - {row[0] for row in call_returns}:
        raise VerificationError("uncovered payload call/return path")
    for missing in sorted(slots - observed_slots):
        raise VerificationError(f"uncovered delay slot {missing:#010x}")
    covered = dict(entries=len(entries & seen),
                   instructions=len((instructions.keys() - fixture_boundary_pcs) & seen),
                   outcomes=len(outcomes & observed_outcomes), delay_slots=len(slots & observed_slots),
                   call_return_paths=len(call_returns))
    if fixture_boundary_pcs:
        covered["fixture_boundary_instructions"] = len(fixture_boundary_pcs & seen)
    return covered


def _invoke_trace_bindings(elf, invoke, fixture, build_dir, names=PC_INVOKE_SYMBOLS):
    """Bind the final ELF ROM and the named invoke functions to independently built bytes."""
    def section(path, name):
        output = build_dir / f"{path.stem}-{name}.raw"
        run_command([OBJCOPY, "-O", "binary", "--only-section", f".{name}", path, output])
        return output.read_bytes()

    def symbols(path):
        found = {}
        for line in run_command([NM, "-S", "--defined-only", path]).stdout.splitlines():
            match = re.fullmatch(r"([0-9a-f]+)\s+([0-9a-f]+)\s+\w\s+(\S+)", line)
            if match and match.group(3) in names:
                found[match.group(3)] = (int(match.group(1), 16), int(match.group(2), 16))
        if set(found) != set(names):
            raise VerificationError("ELF lacks exact invoke function extents")
        return found

    if section(elf, "rom") != fixture:
        raise VerificationError("final ELF ROM differs from the verified simulator fixture")
    text = section(elf, "text")
    original = section(invoke, "text")
    addresses = []
    for line in run_command([OBJDUMP, "-h", elf]).stdout.splitlines():
        fields = line.split()
        if len(fields) > 4 and fields[1] == ".text":
            addresses.append(int(fields[3], 16))
    if len(addresses) != 1:
        raise VerificationError("ELF lacks a unique text section")
    linked, assembled = symbols(elf), symbols(invoke)
    ranges, words = [], {}
    for name, (address, size) in linked.items():
        origin, expected_size = assembled[name]
        linked_bytes = text[address - addresses[0]:address - addresses[0] + size]
        if not size or size % 2 or size != expected_size or linked_bytes != original[origin:origin + size]:
            raise VerificationError(f"linked invoke instructions differ: {name}")
        ranges.append((address, address + size))
        words.update((address + offset, int.from_bytes(linked_bytes[offset:offset + 2], "big"))
                     for offset in range(0, size, 2))
    return ranges, words


def build_and_run_dynamic_harness(fixture, build_dir, *, parsed_by_unit, composed_image, layout):
    """Execute all map-switching behavior cases in the GNU simulator."""
    require_map_fixture_bindings(fixture, composed_image, parsed_by_unit, layout)
    rom_object = build_rom_object(fixture, build_dir)
    invoke_object = build_dir / "invoke.o"
    harness_elf = build_dir / "map-switching-harness.elf"
    source_path = TOOL_DIR / "map_switching_harness.c"
    source = source_path.read_text(encoding="utf-8")
    positive_source = build_dir / "map-switching-harness-positive.c"
    positive_source.write_text(source, encoding="utf-8")
    run_command([
        AS, "--big", "--isa=sh2e", "-o", invoke_object, TOOL_DIR / "invoke.s",
    ])
    command = [
            GCC,
            "-m2e",
            "-mb",
            "-std=c11",
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-DVERIFY_7MFK_FUEL_CUT",
            "-DVERIFY_7MFK_THROTTLE_SCALAR",
            "-DVERIFY_7MFK_THROTTLE_CLUSTER",
            "-DVERIFY_SELECTOR_FEEDBACK_GUARDS",
            f"-Wl,-Ttext-segment={DRIVER_TEXT_BASE:#x}",
            "-Wl,--section-start=.rom=0",
            "-o",
            harness_elf,
            positive_source,
            invoke_object,
            rom_object,
        ]
    run_command(command, timeout=120)
    try:
        require_separate_storage(harness_elf, ((TEST_RAM_BASE, 65536),))
    except (ELFStorageError, OSError) as error:
        raise VerificationError(f"map-switching: ELF storage separation: {error}") from error
    def execute(elf):
        require_map_fixture_bindings(fixture, composed_image, parsed_by_unit, layout)
        ranges, invoke_words = _invoke_trace_bindings(elf, invoke_object, fixture, build_dir)
        trace = build_dir / f"{elf.stem}.pc-trace"
        environment = {
            **os.environ,
            "VQ_SH_PC_TRACE_FILE": str(trace),
            "VQ_SH_PC_TRACE_FORMAT": "v1",
            "VQ_SH_PC_TRACE_RANGES": ",".join(
                f"{start:x}:{end:x}" for start, end in ((0, len(fixture)), *ranges)
            ),
        }
        before = elf.read_bytes()
        result = run_command([RUN, f"--memory-region={TEST_RAM_BASE:#x},64k", elf],
                             timeout=120, env=environment)
        if elf.read_bytes() != before:
            raise VerificationError("harness ELF changes during execution")
        return result, read_pc_trace(trace), invoke_words

    result, records, invoke_words = execute(harness_elf)
    covered = require_payload_coverage(records, fixture, parsed_by_unit, invoke_words,
                                       composed_image=composed_image, throttle_cluster=True, adapter_layout=layout)
    marker = "VQ_SH_ELF_MAP_SWITCHING status=PASS "
    if marker not in result.stdout:
        raise VerificationError(
            "dynamic harness returned zero without the semantic PASS marker"
            + (f"\n{result.stdout.rstrip()}" if result.stdout else "")
        )
    if not re.search(
        r"^VQ_SH_ELF_MAP_SWITCHING_FUEL_CUT status=PASS cases=[1-9][0-9]* entries=1$",
        result.stdout, re.MULTILINE,
    ):
        raise VerificationError("fuel-cut consumer completion marker is missing")
    if not re.search(
        r"^VQ_SH_ELF_MAP_SWITCHING_THROTTLE_SCALAR status=PASS cases=[1-9][0-9]* entries=1$",
        result.stdout, re.MULTILINE,
    ):
        raise VerificationError("throttle scalar completion marker is missing")
    if not re.search(
        r"^VQ_SH_ELF_MAP_SWITCHING_THROTTLE_CLUSTER status=PASS cases=[1-9][0-9]* entries=1$",
        result.stdout, re.MULTILINE,
    ):
        raise VerificationError("throttle-cluster prefix completion marker is missing")
    omissions = [("limiter", "if (!run_limiter_cases())", "uncovered entry 0x000d22a0",
                  "VQ_SH_ELF_PAYLOAD_COVERAGE_NEGATIVE")]
    omissions.append(("adapters", "if (!run_adapter_cases())",
                      f"uncovered entry {layout.code_region_by_key['adapter_select_helper'].entry:#010x}",
                      "VQ_SH_ELF_ADAPTER_COVERAGE_NEGATIVE"))
    omissions.extend((
        ("selector", "if (!run_selector_cases())",
         f"uncovered entry {parsed_by_unit['selector_host'].labels['selector_host']:#010x}",
         "VQ_SH_ELF_SELECTOR_COVERAGE_NEGATIVE"),
        ("feedback", "if (!run_feedback_cases(&feedback_invocations))",
         f"uncovered entry {parsed_by_unit['cruise_feedback_wrapper'].labels['cruise_feedback_wrapper']:#010x}",
         "VQ_SH_ELF_FEEDBACK_COVERAGE_NEGATIVE"),
    ))
    negative_markers, negative_sources = [], []
    for name, call, expected_reason, prefix in omissions:
        if source.count(call) != 1:
            raise VerificationError(f"negative harness lacks its unique {name}-case call")
        negative_source = build_dir / f"map-switching-no-{name}-cases.c"
        negative_text = source.replace(call, call.replace("if (", "if (0 && ", 1))
        negative_source.write_text(negative_text, encoding="utf-8")
        negative_sources.append((negative_source, negative_text))
        negative_elf = build_dir / f"map-switching-no-{name}-cases.elf"
        negative_command = list(command)
        negative_command[negative_command.index("-o") + 1] = negative_elf
        negative_command[negative_command.index(positive_source)] = negative_source
        run_command(negative_command, timeout=120)
        require_separate_storage(negative_elf, ((TEST_RAM_BASE, 65536),))
        negative, records, invoke_words = execute(negative_elf)
        if marker not in negative.stdout:
            raise VerificationError("negative harness does not preserve the existing semantic PASS marker")
        try:
            require_payload_coverage(records, fixture, parsed_by_unit, invoke_words,
                                     composed_image=composed_image, throttle_cluster=True, adapter_layout=layout)
        except VerificationError as error:
            if str(error) != expected_reason:
                raise VerificationError(f"negative harness fails outside its omitted entry: {error}") from error
        else:
            raise VerificationError(f"PC coverage accepts the omitted {name} cases")
        if negative_source.read_text(encoding="utf-8") != negative_text:
            raise VerificationError("negative harness source changes during verification")
        negative_markers.append(f"{prefix} status=PASS {expected_reason}")
    if (source_path.read_text(encoding="utf-8") != source
            or positive_source.read_text(encoding="utf-8") != source
            or any(path.read_text(encoding="utf-8") != expected for path, expected in negative_sources)):
        raise VerificationError("harness source changes during verification")
    scope = ",".join((*PC_COVERAGE_UNITS, *ADAPTER_COVERAGE_UNITS, "throttle_cluster_prefix"))
    coverage_marker = f"VQ_SH_ELF_PAYLOAD_COVERAGE status=PASS scope=JK08A:{scope} "
    coverage_marker += " ".join(f"{key}={value}" for key, value in covered.items())
    return "\n".join((result.stdout.strip(), coverage_marker, *negative_markers))


def build_delay_slot_probe(slot_word, name, build_dir):
    object_path = build_dir / f"delay-slot-{name}.o"
    elf_path = build_dir / f"delay-slot-{name}.elf"
    section_path = build_dir / f"delay-slot-{name}.incident"
    run_command(
        [
            AS,
            "--big",
            "--isa=sh2e",
            "--defsym",
            f"SLOT_WORD={slot_word:#x}",
            "-o",
            object_path,
            TOOL_DIR / "delay_slot_probe.s",
        ]
    )
    run_command(
        [
            GCC,
            "-m2e",
            "-mb",
            "-Wl,--section-start=.incident_target=0x000d2270",
            "-Wl,--section-start=.hardware_literal=0x000d2280",
            "-Wl,--section-start=.incident=0x000d2314",
            "-Wl,--section-start=.static_literal=0x000d2328",
            "-o",
            elf_path,
            TOOL_DIR / "delay_slot_main.c",
            object_path,
        ]
    )
    run_command(
        [
            OBJCOPY,
            "--dump-section",
            f".incident={section_path}",
            elf_path,
        ]
    )
    expected = INCIDENT_BRANCH_WORD.to_bytes(2, "big") + slot_word.to_bytes(
        2, "big"
    )
    actual = section_path.read_bytes()
    if actual != expected:
        raise VerificationError(
            f"{name} incident bytes are {actual.hex()}, expected "
            f"{expected.hex()}"
        )
    return elf_path


def verify_delay_slot_incident(build_dir):
    """Require safe control success and exact incident SIGILL behavior."""
    safe_elf = build_delay_slot_probe(
        INCIDENT_SAFE_SLOT_WORD, "safe", build_dir
    )
    unsafe_elf = build_delay_slot_probe(
        INCIDENT_UNSAFE_SLOT_WORD, "unsafe", build_dir
    )
    run_command([RUN, safe_elf])
    result = run_command(
        [RUN, unsafe_elf], expected_returncode=4, timeout=30
    )
    output = result.stdout + result.stderr
    if "signal 4 (Illegal instruction)" not in output:
        raise VerificationError(
            "unsafe delay-slot probe returned 4 without the SIGILL marker"
        )
    return 4


def require_toolchain_version():
    result = run_command([RUN, "--version"])
    first_line = result.stdout.splitlines()[0]
    if not first_line.endswith(f" {EXPECTED_SIMULATOR_VERSION}"):
        raise VerificationError(
            f"simulator version is {first_line!r}, expected "
            f"{EXPECTED_SIMULATOR_VERSION}"
        )
    gcc = run_command([GCC, "-dumpfullversion"]).stdout.strip()
    return first_line, gcc


def verify_simulator_memory():
    import verify_simulator_memory as simulator_memory
    try:
        simulator_memory.verify()
    except Exception as error:
        raise VerificationError(f'simulator memory gate failed: {error}') from error


def verify_simulator_irq():
    import verify_simulator_irq as simulator_irq
    try:
        simulator_irq.verify()
    except Exception as error:
        raise VerificationError(f'simulator IRQ gate failed: {error}') from error


def verify_rolling_ignition():
    import verify_rolling_launch_ignition
    try:
        return verify_rolling_launch_ignition.verify_kernel()
    except Exception as error:
        raise VerificationError(f"Rolling Launch ignition gate failed: {error}") from error


def verify(verbose=False, rom=None):
    """Execute the patch stages of every supported ROM, or of ``rom`` only.

    The native stages cover the exact family, whose members carry the same
    payloads at the same addresses; a relocated ROM runs its own target.
    """
    if rom is not None and rom not in runtime_targets.SUPPORTED_ROMS:
        raise VerificationError(
            f"unsupported ROM {rom!r}; supported ROMs: "
            f"{', '.join(runtime_targets.SUPPORTED_ROMS)}"
        )
    native = rom is None or rom in runtime_targets.EXACT_ROMS
    relocated_roms = (
        runtime_targets.RELOCATED_ROMS if rom is None
        else tuple(item for item in (rom,) if item in runtime_targets.RELOCATED_ROMS)
    )
    with stage('toolchain'):
        simulator, gcc_version = require_toolchain_version()
    with stage('simulator_memory'):
        verify_simulator_memory()
    with stage('simulator_irq'):
        verify_simulator_irq()
    with tempfile.TemporaryDirectory(prefix="vq-sh-elf-run-") as directory:
        build_dir = Path(directory)
        if native:
            with stage('reconstruction_fixture'):
                layout = layout_model.load_layout()
                parsed_by_unit = assembly_model.validate_assembly_sources(layout)
                blobs = assemble_all_units(
                    layout, parsed_by_unit, build_dir, verbose=verbose
                )
                audit = assembly_model.validate_instruction_semantics(
                    layout, parsed_by_unit, blobs
                )
                composition = require_composition(layout, blobs)
                verify_fuel_cut_consumer_binding(layout, composition, build_dir)
                verify_throttle_scalar_consumer_binding(layout, composition, build_dir)
                throttle_reconstruction = verify_throttle_cluster_binding(layout, composition, build_dir)
                fixture, relocated, differentiated, stubs = build_dynamic_fixture(
                    composition, layout, parsed_by_unit, throttle_reconstruction=throttle_reconstruction
                )
            with stage('map_switching'):
                dynamic_marker = build_and_run_dynamic_harness(
                    fixture, build_dir, parsed_by_unit=parsed_by_unit,
                    composed_image=composition.data, layout=layout,
                )
        with stage('delay_slot_probe'):
            incident_signal = verify_delay_slot_incident(build_dir)

    if native:
        print(dynamic_marker)
        try:
            import verify_rolling_launch

            with stage('rolling_launch'):
                rolling_result = verify_rolling_launch.verify(
                    verbose=verbose, check_toolchain=False
                )
        except Exception as error:
            raise VerificationError(
                f"Rolling Launch executable gate failed: {error}"
            ) from error
        with stage('rolling_ignition'):
            print(verify_rolling_ignition())
        try:
            import verify_can_telemetry

            with stage('can_telemetry'):
                telemetry_result = verify_can_telemetry.verify(
                    verbose=verbose, check_toolchain=False
                )
        except Exception as error:
            raise VerificationError(
                f"CAN telemetry executable gate failed: {error}"
            ) from error
    if relocated_roms:
        try:
            import verify_runtime_targets

            with stage('relocated_runtime_targets'):
                runtime_results = verify_runtime_targets.verify(
                    verbose=verbose, roms=relocated_roms
                )
        except Exception as error:
            raise VerificationError(
                f"relocated runtime-target executable gate failed: {error}"
            ) from error
    fields = [
        ("scope", "full" if rom is None else f"rom:{rom}"),
        ("simulator", EXPECTED_SIMULATOR_VERSION),
        ("gcc", gcc_version),
    ]
    if native:
        fields += [
            ("units", len(layout.assembly_units)),
            ("instructions", audit.instructions),
            ("delayed_transfers", audit.delayed_transfers),
            ("pc_relative_references", audit.pc_relative_references),
            ("direct_branches", audit.direct_branches),
            ("indirect_transfers", audit.indirect_transfers),
            ("composition_sha256", composition.sha256),
            ("rolling_launch_instructions", rolling_result['audit'].instructions),
            ("rolling_launch_cases", rolling_result['dynamic_cases']),
            ("can_telemetry_instructions", telemetry_result['audit'].instructions),
            ("can_telemetry_cases", telemetry_result['dynamic_cases']),
        ]
    if relocated_roms:
        fields += [
            ("runtime_targets", len(runtime_results)),
            ("runtime_target_cases",
             sum(item['dynamic_cases'] for item in runtime_results)),
        ]
    if native:
        fields += [
            ("ram_literals_relocated", relocated),
            ("differentiated_bytes", differentiated),
            ("stock_stubs", stubs),
        ]
    fields += [
        ("incident_address", f"{INCIDENT_ADDRESS:#x}"),
        ("unsafe_signal", incident_signal),
    ]
    print("VQ_SH_ELF_VERIFY status=PASS " + " ".join(
        f"{name}={value}" for name, value in fields
    ))
    if verbose:
        print(f"TOOLCHAIN {simulator}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="print each independently assembled unit digest",
    )
    parser.add_argument(
        "--rom",
        choices=runtime_targets.SUPPORTED_ROMS,
        help="execute only the patch stages that cover this ROM",
    )
    parser.add_argument(
        "--rolling-ignition", action="store_true",
        help="execute the coupled Rolling Launch ignition paths and simulator prerequisites",
    )
    args = parser.parse_args(argv)
    if args.rolling_ignition and args.rom:
        parser.error("--rolling-ignition excludes --rom")
    try:
        if args.rolling_ignition:
            with stage('toolchain'):
                require_toolchain_version()
            with stage('simulator_memory'):
                verify_simulator_memory()
            with stage('simulator_irq'):
                verify_simulator_irq()
            with stage('rolling_ignition'):
                print(verify_rolling_ignition())
        else:
            verify(verbose=args.verbose, rom=args.rom)
    except (OSError, ValueError, VerificationError) as error:
        traceback.print_exc(file=sys.stderr)
        print(f"VQ_SH_ELF_VERIFY status=FAIL error={error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
