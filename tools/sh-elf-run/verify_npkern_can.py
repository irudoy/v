#!/usr/bin/env python3
"""Build and execute the SH7058/SH7059 npkern CAN verification fixture.

The production variants are linked at the exact factory loader addresses. The
dynamic fixtures link the exact cmd_parser, crc, and ISO-TP relocatable objects
from those builds at simulator-safe addresses. All final-code differences are
restricted to declared R_SH_DIR32 link-address literals; every other byte is
required to match the high-address production ELF.

HCAN and flash-controller registers cannot be modeled by GNU sh-elf-run. Their
drivers are built and statically audited here, but the resulting kernels remain
ineligible for hardware use until passive capture and bench validation close
that executable-verification gap.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
from pathlib import Path
import re
import subprocess
import sys
import tempfile


TOOL_DIR = Path(__file__).resolve().parent
HARNESS = TOOL_DIR / "npkern_can_harness.c"
FLASH_GUARD_HARNESS = TOOL_DIR / "npkern_flash_guard_harness.c"
EXPECTED_SIMULATOR_VERSION = "16.3"
FIXTURE_RX_ID = 0x700
FIXTURE_TX_ID = 0x708
DRIVER_TEXT_BASE = 0x00110000
FIXTURE_ADDRESS = 0x00180000

GCC = "sh-elf-gcc"
OBJCOPY = "sh-elf-objcopy"
# ELF metadata only; diagnostic branch display is excluded in gnu-disassembly.md.
OBJDUMP = "sh-elf-objdump"
NM = "sh-elf-nm"
RUN = "sh-elf-run"

COMMON_SOURCES = (
    "cmd_parser_pdu.c",
    "eep_funcs.c",
    "main.c",
    "crc.c",
    "wdt.c",
    "transport_hcan.c",
    "isotp.c",
    "mfg_nissan.c",
)
PLATFORM_SOURCES = ("platf_7055.c", "pl_flash_705x_180nm.c")
BOUND_OBJECTS = ("cmd_parser_pdu.o", "isotp.o")
LEGACY_SOURCES = (
    "cmd_parser.c",
    "eep_funcs.c",
    "main.c",
    "crc.c",
    "wdt.c",
    "mfg_nissan.c",
    "platf_7055.c",
    "pl_flash_705x_180nm.c",
)
LEGACY_PARSER_SHA256 = (
    "c2378cd60cfd543ad3459b066c278084fb58414aae6055af29608c40fc1a5208"
)
LEGACY_SH7058_BINARY_SHA256 = (
    "6d2c730338675a83c41beb046b2986305117c960978e84a3861fa93e67dea81b"
)


class VerificationError(RuntimeError):
    """Raised when an executable verification contract fails."""


@dataclass(frozen=True)
class Target:
    mcu: str
    read_only: bool
    origin: int
    boundary: int
    aligned_limit: int

    @property
    def suffix(self) -> str:
        return "CAN" if self.read_only else "CAN_RW"

    @property
    def name(self) -> str:
        return f"SH{self.mcu}_{self.suffix}"


TARGETS = (
    Target("7058", True, 0xFFFF84A0, 0xFFFFA314, 0x1E60),
    Target("7059", True, 0xFFFEDE24, 0xFFFF0608, 0x27E0),
    Target("7058", False, 0xFFFF84A0, 0xFFFFA314, 0x1E60),
    Target("7059", False, 0xFFFEDE24, 0xFFFF0608, 0x27E0),
)


@dataclass
class Build:
    target: Target
    directory: Path
    objects: dict[str, Path]
    elf: Path
    binary: Path
    symbols: dict[str, tuple[int, int | None, str]]
    digest: str
    binary_size: int
    payload_size: int


@dataclass
class LegacyBuild:
    digest: str
    binary_size: int
    payload_size: int


def run_command(
    command: list[object],
    *,
    cwd: Path | None = None,
    timeout: int = 120,
) -> subprocess.CompletedProcess[str]:
    display = " ".join(str(item) for item in command)
    try:
        result = subprocess.run(
            [str(item) for item in command],
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as error:
        raise VerificationError(f"required tool is missing: {command[0]}") \
            from error
    except subprocess.TimeoutExpired as error:
        raise VerificationError(
            f"command timed out after {timeout}s: {display}"
        ) from error
    if result.returncode != 0:
        details = "\n".join(
            part.rstrip()
            for part in (result.stdout, result.stderr)
            if part.strip()
        )
        raise VerificationError(
            f"command returned {result.returncode}: {display}"
            + (f"\n{details}" if details else "")
        )
    return result


def require_toolchain() -> tuple[str, str]:
    simulator = run_command([RUN, "--version"]).stdout.splitlines()[0]
    if not simulator.endswith(f" {EXPECTED_SIMULATOR_VERSION}"):
        raise VerificationError(
            f"simulator is {simulator!r}, expected {EXPECTED_SIMULATOR_VERSION}"
        )
    gcc = run_command([GCC, "-dumpfullversion"]).stdout.strip()
    return simulator, gcc


def common_definitions(target: Target) -> list[str]:
    definitions = [
        "-Dnpk",
        "-DNPK_TRANSPORT_HCAN",
        f"-DNPK_CAN_RX_ID={FIXTURE_RX_ID:#x}",
        f"-DNPK_CAN_TX_ID={FIXTURE_TX_ID:#x}",
        "-DNPK_HCAN_CHANNEL=1",
        f'-DPLATF="{target.name}"',
        f"-DSH{target.mcu}",
        f"-D{target.name}",
    ]
    if target.read_only:
        definitions.append("-DNPK_READ_ONLY")
    return definitions


def compile_c(source: Path, output: Path, includes: list[Path],
              definitions: list[str]) -> None:
    command: list[object] = [
        GCC,
        "-mb",
        "-m2",
        "-Os",
        "-ffunction-sections",
        "-Wall",
        "-Wextra",
        "-Wformat",
        "-Werror",
        "-std=gnu11",
        "-Wstrict-prototypes",
        "-Wsign-compare",
        "-Wredundant-decls",
        "-ffreestanding",
    ]
    command.extend(f"-I{include}" for include in includes)
    command.extend(definitions)
    command.extend(["-c", source, "-o", output])
    run_command(command)


def compile_assembly(source: Path, output: Path, includes: list[Path],
                     definitions: list[str]) -> None:
    command: list[object] = [
        GCC,
        "-mb",
        "-m2",
        "-x",
        "assembler-with-cpp",
    ]
    command.extend(f"-I{include}" for include in includes)
    command.extend(definitions)
    command.extend(["-c", source, "-o", output])
    run_command(command)


def read_symbols(elf: Path) -> dict[str, tuple[int, int | None, str]]:
    symbols: dict[str, tuple[int, int | None, str]] = {}
    output = run_command([NM, "-S", "-n", elf]).stdout
    for line in output.splitlines():
        fields = line.split()
        if len(fields) == 4 and re.fullmatch(r"[0-9A-Fa-f]+", fields[0]):
            address, size, kind, name = fields
            symbols[name] = (int(address, 16), int(size, 16), kind)
        elif (
            len(fields) == 3
            and re.fullmatch(r"[0-9A-Fa-f]+", fields[0])
        ):
            address, kind, name = fields
            symbols[name] = (int(address, 16), None, kind)
    return symbols


def require_symbol(symbols: dict[str, tuple[int, int | None, str]],
                   name: str) -> int:
    try:
        return symbols[name][0]
    except KeyError as error:
        raise VerificationError(f"required symbol is missing: {name}") \
            from error


def build_target(npkern: Path, target: Target, build_root: Path) -> Build:
    directory = build_root / target.name
    directory.mkdir()
    include_dir = directory / "include"
    include_dir.mkdir()
    (include_dir / "version.h").write_text(
        '#define NPK_COMMIT "sh-elf-run"\n', encoding="ascii"
    )
    includes = [include_dir, npkern]
    definitions = common_definitions(target)
    objects: dict[str, Path] = {}
    link_objects: list[Path] = []

    for name in COMMON_SOURCES:
        output = directory / f"{Path(name).stem}.o"
        compile_c(npkern / name, output, includes, definitions)
        objects[output.name] = output
        link_objects.append(output)

    start_object = directory / "start_705x.o"
    compile_assembly(
        npkern / "start_705x.s", start_object, includes, definitions
    )
    objects[start_object.name] = start_object
    link_objects.append(start_object)

    for name in PLATFORM_SOURCES:
        output = directory / f"{Path(name).stem}.o"
        compile_c(npkern / name, output, includes, definitions)
        objects[output.name] = output
        link_objects.append(output)

    elf = directory / f"npk_{target.name}.elf"
    linker = npkern / "ldscripts" / f"lkr_{target.mcu}_can.ld"
    run_command(
        [
            GCC,
            "-mb",
            "-m2",
            "-nostartfiles",
            "-Wl,-gc-sections",
            f"-Wl,-Map={directory / 'npkern.map'}",
            "-T",
            linker,
            "-o",
            elf,
            *link_objects,
        ]
    )
    binary = directory / f"npk_{target.name}.bin"
    run_command([OBJCOPY, "-O", "binary", elf, binary])

    symbols = read_symbols(elf)
    entry = require_symbol(symbols, "RAMjump_entry")
    end = require_symbol(symbols, "_endpayload")
    stack = require_symbol(symbols, "_stackinit")
    if entry != target.origin:
        raise VerificationError(
            f"{target.name}: entry is {entry:#x}, expected {target.origin:#x}"
        )
    if end > target.boundary:
        raise VerificationError(
            f"{target.name}: payload end {end:#x} exceeds "
            f"{target.boundary:#x}"
        )
    if stack != 0xFFFFBFFC:
        raise VerificationError(
            f"{target.name}: stack is {stack:#x}, expected 0xffffbffc"
        )
    binary_data = binary.read_bytes()
    marker = f"{target.name}-".encode("ascii")
    if marker not in binary_data:
        raise VerificationError(
            f"{target.name}: binary is missing target marker {marker!r}"
        )
    aligned_size = (len(binary_data) + 31) & ~31
    if aligned_size > target.aligned_limit:
        raise VerificationError(
            f"{target.name}: aligned binary is {aligned_size:#x}, limit is "
            f"{target.aligned_limit:#x}"
        )

    flash_symbols = {
        "_platf_flash_init",
        "_platf_flash_unprotect",
        "_platf_flash_eb",
        "_platf_flash_wb",
    }
    present = flash_symbols.intersection(symbols)
    if target.read_only and present:
        raise VerificationError(
            f"{target.name}: read-only image retains flash symbols {present}"
        )
    if not target.read_only and present != flash_symbols:
        missing = flash_symbols - present
        raise VerificationError(
            f"{target.name}: RW image is missing flash symbols {missing}"
        )

    digest = hashlib.sha256(binary_data).hexdigest()
    return Build(
        target=target,
        directory=directory,
        objects=objects,
        elf=elf,
        binary=binary,
        symbols=symbols,
        digest=digest,
        binary_size=len(binary_data),
        payload_size=end - target.origin,
    )


def build_legacy_sh7058(npkern: Path, build_root: Path) -> LegacyBuild:
    directory = build_root / "SH7058_KLINE"
    directory.mkdir()
    include_dir = directory / "include"
    include_dir.mkdir()
    (include_dir / "version.h").write_text(
        '#define NPK_COMMIT "sh-elf-run"\n', encoding="ascii"
    )
    includes = [include_dir, npkern]
    definitions = ["-Dnpk", "-DSH7058", '-DPLATF="SH7058"']
    objects: list[Path] = []
    for name in LEGACY_SOURCES:
        output = directory / f"{Path(name).stem}.o"
        compile_c(npkern / name, output, includes, definitions)
        objects.append(output)
    start_object = directory / "start_705x.o"
    compile_assembly(
        npkern / "start_705x.s", start_object, includes, definitions
    )
    objects.append(start_object)

    elf = directory / "npk_SH7058.elf"
    run_command(
        [
            GCC,
            "-mb",
            "-m2",
            "-nostartfiles",
            "-Wl,-gc-sections",
            "-T",
            npkern / "ldscripts" / "lkr_7055_7058.ld",
            "-o",
            elf,
            *objects,
        ]
    )
    binary = directory / "npk_SH7058.bin"
    run_command([OBJCOPY, "-O", "binary", elf, binary])
    symbols = read_symbols(elf)
    entry = require_symbol(symbols, "RAMjump_entry")
    end = require_symbol(symbols, "_endpayload")
    stack = require_symbol(symbols, "_stackinit")
    if entry != 0xFFFF8040:
        raise VerificationError(
            f"legacy SH7058 entry is {entry:#x}, expected 0xffff8040"
        )
    if end > 0xFFFFA040:
        raise VerificationError(
            f"legacy SH7058 payload end {end:#x} exceeds 0xffffa040"
        )
    if stack != 0xFFFFBFFC:
        raise VerificationError(
            f"legacy SH7058 stack is {stack:#x}, expected 0xffffbffc"
        )
    binary_data = binary.read_bytes()
    if b"SH7058-sh-elf-run" not in binary_data:
        raise VerificationError("legacy SH7058 binary is missing target marker")
    digest = hashlib.sha256(binary_data).hexdigest()
    if (
        LEGACY_SH7058_BINARY_SHA256 is not None
        and digest != LEGACY_SH7058_BINARY_SHA256
    ):
        raise VerificationError(
            "legacy SH7058 binary changed without an executable gate update: "
            f"{digest}"
        )
    return LegacyBuild(
        digest=digest,
        binary_size=len(binary_data),
        payload_size=end - entry,
    )


def object_functions(obj: Path) -> dict[str, tuple[str, int]]:
    functions: dict[str, tuple[str, int]] = {}
    output = run_command([OBJDUMP, "-t", obj]).stdout
    for line in output.splitlines():
        fields = line.split()
        if (
            len(fields) == 6
            and fields[2] == "F"
            and fields[3].startswith(".text.")
        ):
            functions[fields[5]] = (fields[3], int(fields[4], 16))
    return functions


def section_relocations(obj: Path, section: str) -> set[int]:
    output = run_command([OBJDUMP, "-r", "-j", section, obj]).stdout
    offsets: set[int] = set()
    for line in output.splitlines():
        fields = line.split()
        if len(fields) >= 3 and re.fullmatch(r"[0-9A-Fa-f]{8}", fields[0]):
            if fields[1] != "R_SH_DIR32":
                raise VerificationError(
                    f"{obj.name}:{section}: unsupported relocation "
                    f"{fields[1]}"
                )
            offsets.update(range(int(fields[0], 16), int(fields[0], 16) + 4))
    return offsets


def output_text(elf: Path, directory: Path) -> tuple[int, bytes]:
    headers = run_command([OBJDUMP, "-h", elf]).stdout
    base = None
    for line in headers.splitlines():
        fields = line.split()
        if len(fields) >= 4 and fields[1] == ".text":
            base = int(fields[3], 16)
            break
    if base is None:
        raise VerificationError(f"{elf.name}: .text section is missing")
    destination = directory / f"{elf.stem}.text"
    run_command([OBJCOPY, "--dump-section", f".text={destination}", elf])
    return base, destination.read_bytes()


def function_bytes(
    symbols: dict[str, tuple[int, int | None, str]],
    text_base: int,
    text: bytes,
    symbol: str,
    expected_size: int,
) -> bytes:
    if symbol not in symbols or symbols[symbol][1] is None:
        raise VerificationError(f"linked function is missing: {symbol}")
    address, size, _kind = symbols[symbol]
    if size != expected_size:
        raise VerificationError(
            f"{symbol}: linked size is {size}, object size is {expected_size}"
        )
    offset = address - text_base
    return text[offset : offset + expected_size]


def bind_production_bytes(
    build: Build,
    harness: Path,
    directory: Path,
    object_names: tuple[str, ...] = BOUND_OBJECTS,
) -> tuple[int, int, int]:
    high_base, high_text = output_text(build.elf, directory)
    low_base, low_text = output_text(harness, directory)
    low_symbols = read_symbols(harness)
    functions = 0
    exact_bytes = 0
    relocated_bytes = 0
    for object_name in object_names:
        obj = build.objects[object_name]
        for symbol, (section, size) in object_functions(obj).items():
            if symbol not in build.symbols or symbol not in low_symbols:
                continue
            high = function_bytes(
                build.symbols, high_base, high_text, symbol, size
            )
            low = function_bytes(low_symbols, low_base, low_text, symbol, size)
            relocations = section_relocations(obj, section)
            for offset, (production_byte, fixture_byte) in enumerate(
                zip(high, low)
            ):
                if offset in relocations:
                    relocated_bytes += 1
                    continue
                if production_byte != fixture_byte:
                    raise VerificationError(
                        f"{build.target.name}:{symbol}+{offset:#x}: "
                        "non-relocated production byte differs from fixture"
                    )
                exact_bytes += 1
            functions += 1
    if functions == 0 or exact_bytes == 0:
        raise VerificationError(
            f"{build.target.name}: no production functions were bound"
        )
    return functions, exact_bytes, relocated_bytes


def build_and_run_harness(npkern: Path, build: Build,
                          directory: Path) -> tuple[Path, str]:
    variant = "ro" if build.target.read_only else "rw"
    harness = directory / f"npkern-{variant}-harness.elf"
    run_command(
        [
            GCC,
            "-m2e",
            "-mb",
            "-std=c11",
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            f"-DEXPECT_READ_ONLY={1 if build.target.read_only else 0}",
            f"-I{npkern}",
            f"-Wl,-Ttext-segment={DRIVER_TEXT_BASE:#x}",
            f"-Wl,--section-start=.npkern_fixture={FIXTURE_ADDRESS:#x}",
            "-o",
            harness,
            HARNESS,
            build.objects["cmd_parser_pdu.o"],
            build.objects["crc.o"],
            build.objects["isotp.o"],
        ]
    )
    result = run_command([RUN, harness], timeout=120)
    output = result.stdout.strip()
    variant_name = "RO" if build.target.read_only else "RW"
    expected = f"NPKERN_CAN_HARNESS status=PASS variant={variant_name}"
    if expected not in output:
        raise VerificationError(
            f"{build.target.name}: harness omitted marker {expected!r}"
            + (f"\n{output}" if output else "")
        )
    if build.target.read_only and "NPKERN_ISOTP status=PASS cases=16" not in output:
        raise VerificationError("read-only harness omitted ISO-TP case marker")
    return harness, output


def build_and_run_flash_guard(
    npkern: Path, build: Build, directory: Path
) -> tuple[Path, str]:
    flash_max = 0x000FFFFF if build.target.mcu == "7058" else 0x0017FFFF
    harness = directory / f"npkern-{build.target.mcu}-flash-guard.elf"
    run_command(
        [
            GCC,
            "-m2e",
            "-mb",
            "-std=c11",
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            f"-DEXPECT_FLASH_MAX={flash_max:#x}",
            f"-I{npkern}",
            f"-Wl,-Ttext-segment={DRIVER_TEXT_BASE:#x}",
            "-Wl,--gc-sections",
            "-o",
            harness,
            FLASH_GUARD_HARNESS,
            build.objects["pl_flash_705x_180nm.o"],
        ]
    )
    output = run_command([RUN, harness], timeout=120).stdout.strip()
    expected = f"NPKERN_FLASH_GUARD status=PASS max={flash_max:#x} cases=5"
    if expected not in output:
        raise VerificationError(
            f"{build.target.name}: flash guard omitted marker {expected!r}"
            + (f"\n{output}" if output else "")
        )
    return harness, output


def require_source_contract(npkern: Path) -> None:
    legacy_parser = (npkern / "cmd_parser.c").read_bytes()
    legacy_digest = hashlib.sha256(legacy_parser).hexdigest()
    if legacy_digest != LEGACY_PARSER_SHA256:
        raise VerificationError(
            "legacy K-line parser changed without an executable gate update: "
            f"{legacy_digest}"
        )
    hcan = (npkern / "transport_hcan.c").read_text(encoding="utf-8")
    required_hcan = (
        "#error NPK_CAN_RX_ID must be set from a passive capture",
        "#error NPK_CAN_TX_ID must be set from a passive capture",
        "#error NPK_HCAN_CHANNEL must be set from firmware analysis and bench wiring",
        "#define NPK_HCAN HCAN1",
        "NPK_HCAN.BCR0.WORD",
        "NPK_HCAN.BCR1.WORD",
        "HCAN_MBC_RECEIVE 2U",
        "HCAN_MBC_TRANSMIT 0U",
        "NPK_HCAN.MCR.BIT.RSTRQ",
        "NPK_HCAN.MB[mailbox].LAFMH.WORD",
        "NPK_HCAN.MB[mailbox].TMSTP = 0",
        "NPK_HCAN.MB[mailbox].MSG_DATA[data_index] = 0",
        "while (result == ISOTP_ERR_TIMEOUT)",
    )
    missing = [token for token in required_hcan if token not in hcan]
    if missing:
        raise VerificationError(f"HCAN source contract is missing {missing}")
    if re.search(r"#define\s+NPK_CAN_(?:RX|TX)_ID\s+0x", hcan):
        raise VerificationError("HCAN source contains a fallback CAN ID")

    cmake = (npkern / "CMakeLists.txt").read_text(encoding="utf-8")
    required_cmake = (
        'option(NPK_BUILD_CAN "Build read-only HCAN/ISO-TP kernels" OFF)',
        'option(NPK_BUILD_CAN_WRITE "Build explicitly write-enabled CAN kernels" OFF)',
        "NPK_CAN_RX_ID and NPK_CAN_TX_ID must be explicit IDs from a passive trace",
        "NPK_HCAN_CHANNEL must be explicit (0 or 1) from firmware analysis and bench wiring",
        "lkr_7058_can.ld",
        "lkr_7059_can.ld",
        "NPK_READ_ONLY",
    )
    missing = [token for token in required_cmake if token not in cmake]
    if missing:
        raise VerificationError(f"CMake source contract is missing {missing}")


def verify(npkern: Path, verbose: bool = False) -> None:
    if not npkern.is_dir():
        raise VerificationError(f"npkern source directory is missing: {npkern}")
    require_source_contract(npkern)
    simulator, gcc_version = require_toolchain()
    with tempfile.TemporaryDirectory(prefix="vq-npkern-can-") as temp:
        build_root = Path(temp)
        builds = [build_target(npkern, target, build_root) for target in TARGETS]
        legacy = build_legacy_sh7058(npkern, build_root)
        primary = {
            build.target.read_only: build
            for build in builds
            if build.target.mcu == "7058"
        }
        bound_functions = 0
        bound_bytes = 0
        relocated_bytes = 0
        harness_outputs: list[str] = []
        for read_only in (True, False):
            build = primary[read_only]
            harness, output = build_and_run_harness(
                npkern, build, build_root
            )
            functions, exact, relocated = bind_production_bytes(
                build, harness, build_root
            )
            bound_functions += functions
            bound_bytes += exact
            relocated_bytes += relocated
            harness_outputs.append(output)

        for build in builds:
            if build.target.read_only:
                continue
            harness, output = build_and_run_flash_guard(
                npkern, build, build_root
            )
            functions, exact, relocated = bind_production_bytes(
                build,
                harness,
                build_root,
                ("pl_flash_705x_180nm.o",),
            )
            bound_functions += functions
            bound_bytes += exact
            relocated_bytes += relocated
            harness_outputs.append(output)

        for build in builds:
            print(
                "NPKERN_BUILD status=PASS"
                f" target={build.target.name}"
                f" binary_bytes={build.binary_size}"
                f" aligned_bytes={(build.binary_size + 31) & ~31}"
                f" payload_bytes={build.payload_size}"
                f" origin={build.target.origin:#x}"
                f" boundary={build.target.boundary:#x}"
                f" sha256={build.digest}"
            )
        print(
            "NPKERN_LEGACY_BUILD status=PASS target=SH7058_KLINE"
            f" binary_bytes={legacy.binary_size}"
            f" payload_bytes={legacy.payload_size}"
            f" sha256={legacy.digest}"
        )
        for output in harness_outputs:
            print(output)
        print(
            "NPKERN_CAN_VERIFY status=PASS"
            f" simulator={EXPECTED_SIMULATOR_VERSION}"
            f" gcc={gcc_version}"
            f" targets={len(builds)}"
            " legacy_targets=1"
            f" bound_functions={bound_functions}"
            f" exact_nonliteral_bytes={bound_bytes}"
            f" relocated_literal_bytes={relocated_bytes}"
            " flash_guard_cases=10"
            f" fixture_rx_id={FIXTURE_RX_ID:#x}"
            f" fixture_tx_id={FIXTURE_TX_ID:#x}"
            " hardware_ready=NO"
            " limitation=HCAN_and_flash_peripherals_not_executed"
        )
        if verbose:
            print(f"TOOLCHAIN {simulator}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("npkern", type=Path, help="path to the npkern source tree")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)
    try:
        verify(args.npkern.resolve(), verbose=args.verbose)
    except (OSError, ValueError, VerificationError) as error:
        print(f"NPKERN_CAN_VERIFY status=FAIL error={error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
