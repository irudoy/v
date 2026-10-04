"""Optional exact-PC capability probe for the separate GNU16.3 observer image."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from pc_observation import parse_trace, require, sha256, wrapper_bytes_from_elf


ROOT = Path(__file__).resolve().parents[2]
ROM = ROOT / "rom-images/23710-JK08A/1JK08A-20260726-stock.bin"
STOCK_SHA256 = "ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23"
HELPER_START, HELPER_END = 0x224FA, 0x22508
HELPER_WORDS = (0x4021, 0x4021, 0x4021, 0x4021, 0x4021, 0x000B, 0x4021)
ASM = r'''
    .section .text
    .global _probe
    .type _probe,@function
_probe:
    sts.l pr,@-r15
    mov r4,r0
    mov.l helper_target,r1
    jsr @r1
    nop
    lds.l @r15+,pr
    rts
    nop
    .size _probe,.-_probe
    .global _probe_end
_probe_end:
    .balign 4
helper_target:
    .long _trace_helper
    .section .helper,"ax"
    .global _trace_helper
_trace_helper:
    shar r0
    shar r0
    shar r0
    shar r0
    shar r0
    rts
    shar r0
'''
C = r'''
#include <errno.h>
#include <stdio.h>
#include <unistd.h>
extern int probe(int);
int main(void) {
    volatile int a=probe(-65), b=probe(64);
    int result, failed_errno;
    errno=0;
    result=close(-1);
    failed_errno=errno;
    if(a!=-2 || b!=1 || result!=-1 || failed_errno!=EBADF) return 1;
    printf("PC_OBSERVER_PROBE status=PASS values=-2,1 errno=%d\n", failed_errno);
    return 0;
}
'''


def probe(output, image_id):
    require(re.fullmatch(r"sha256:[0-9a-f]{64}", image_id) is not None,
            "supply the immutable image ID from the host Docker invocation")
    asm, c, obj, elf = (output / name for name in ("probe.s", "probe.c", "probe.o", "probe.elf"))
    helper, trace = output / "helper.bin", output / "trace.log"
    asm.write_text(ASM, encoding="ascii")
    c.write_text(C, encoding="ascii")
    env = {name: value for name, value in os.environ.items() if not name.startswith("VQ_SH_PC_TRACE_")}

    def run(args, request=None):
        return subprocess.run([str(arg) for arg in args], capture_output=True, text=True,
                              timeout=60, env=env if request is None else request)

    def command(args):
        result = run(args)
        require(result.returncode == 0, f"probe command failed: {result.stderr}")
        return result

    command(["sh-elf-as", "--big", "--isa=sh2e", "-o", obj, asm])
    command(["sh-elf-gcc", "-m2e", "-mb", "-O2", "-Wl,--section-start=.helper=0x224fa",
             "-Wl,-Ttext-segment=0x200000", "-o", elf, c, obj])
    elf_before = sha256(elf)
    command(["sh-elf-objcopy", "--dump-section", f".helper={helper}", elf])
    require(sha256(elf) == elf_before, "helper extraction changed the input ELF")
    stock = ROM.read_bytes()
    require(hashlib.sha256(stock).hexdigest() == STOCK_SHA256, "stock ROM identity differs")
    require(helper.read_bytes() == stock[HELPER_START:HELPER_END]
            == b"".join(word.to_bytes(2, "big") for word in HELPER_WORDS),
            "independent helper reconstruction differs from stock bytes")
    nm = command(["sh-elf-nm", "-n", elf]).stdout
    symbols = {}
    for line in nm.splitlines():
        fields = line.split()
        if len(fields) == 3 and fields[-1] in ("_probe", "_probe_end", "_trace_helper"):
            require(fields[-1] not in symbols, "duplicate probe ELF marker")
            symbols[fields[-1]] = int(fields[0], 16)
    require(set(symbols) == {"_probe", "_probe_end", "_trace_helper"}, "missing probe ELF marker")
    begin, end = symbols["_probe"], symbols["_probe_end"]
    require(end - begin == 16 and begin % 2 == 0 and symbols["_trace_helper"] == HELPER_START,
            "probe marker addresses differ")
    wrapper = wrapper_bytes_from_elf(elf, output, {"begin": begin, "end": end}, command)
    baseline = command(["sh-elf-run", elf])
    original = command(["/usr/bin/sh-elf-run", elf])
    require((baseline.returncode, baseline.stdout, baseline.stderr)
            == (original.returncode, original.stdout, original.stderr),
            "disabled observer differs from the original simulator")
    require(baseline.stdout == "PC_OBSERVER_PROBE status=PASS values=-2,1 errno=9\n"
            and not baseline.stderr, "probe lacks its exact values/errno assertion")
    enabled = env | {"VQ_SH_PC_TRACE_FILE": str(trace), "VQ_SH_PC_TRACE_FORMAT": "v1",
                     "VQ_SH_PC_TRACE_RANGES": f"224fa:22508,{begin:x}:{end:x}"}
    observed = run(["sh-elf-run", elf], enabled)
    require((observed.returncode, observed.stdout, observed.stderr)
            == (baseline.returncode, baseline.stdout, baseline.stderr),
            "enabled observer changes the probe result")
    records = parse_trace(trace.read_bytes(), observed.returncode)
    expected_pcs = [begin, begin + 2, begin + 4, begin + 6, begin + 8,
                    *range(HELPER_START, HELPER_END, 2), begin + 10, begin + 12, begin + 14]
    expected_delays = [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1]
    require([pc for pc, _, _ in records] == expected_pcs * 2
            and [delay for _, _, delay in records] == expected_delays * 2,
            "probe does not report both exact ordinary and delay-slot PC sequences")
    for pc, opcode, _ in records:
        offset, bound = (pc - begin, wrapper) if begin <= pc < end else (pc, stock)
        require(opcode == int.from_bytes(bound[offset:offset + 2], "big"),
                "observed probe opcode differs from stock/linked bytes")
    counts = Counter(pc for pc, _, _ in records)
    require(counts[HELPER_START] == counts[0x22504] == counts[0x22506] == 2 and len(records) == 30,
            "probe helper entry/return/delay counts differ")
    filtered_sha = sha256(trace)
    filtered_trace = output / "filtered-trace.log"
    filtered_trace.write_bytes(trace.read_bytes())
    unfiltered = run(["sh-elf-run", elf], {key: value for key, value in enabled.items()
                                         if key != "VQ_SH_PC_TRACE_RANGES"})
    require((unfiltered.returncode, unfiltered.stdout, unfiltered.stderr)
            == (baseline.returncode, baseline.stdout, baseline.stderr),
            "unfiltered observer changes the probe result")
    unfiltered_records = parse_trace(trace.read_bytes(), unfiltered.returncode)
    require(len(unfiltered_records) > 30
            and sum(pc == HELPER_START for pc, _, _ in unfiltered_records) == 2,
            "unfiltered probe lacks both helper entries")
    unfiltered_sha = sha256(trace)
    (output / "unfiltered-trace.log").write_bytes(trace.read_bytes())
    failures = []
    invalid = (
        ("unsupported-format", enabled | {"VQ_SH_PC_TRACE_FORMAT": "v2"}),
        ("missing-format", {key: value for key, value in enabled.items() if key != "VQ_SH_PC_TRACE_FORMAT"}),
        ("missing-path", {key: value for key, value in enabled.items() if key != "VQ_SH_PC_TRACE_FILE"}),
        ("open-failure", enabled | {"VQ_SH_PC_TRACE_FILE": str(output / "absent/trace.log")}),
        ("write-failure", enabled | {"VQ_SH_PC_TRACE_FILE": "/dev/full"}),
        ("empty-ranges", enabled | {"VQ_SH_PC_TRACE_RANGES": ""}),
        ("reversed-range", enabled | {"VQ_SH_PC_TRACE_RANGES": "22508:224fa"}),
        ("trailing-range", enabled | {"VQ_SH_PC_TRACE_RANGES": "224fa:22508,"}),
        ("range-overflow", enabled | {"VQ_SH_PC_TRACE_RANGES": "0:100000001"}),
        ("no-PC-records", enabled | {"VQ_SH_PC_TRACE_RANGES": "fffffffe:ffffffff"}),
    )
    for name, request in invalid:
        result = run(["sh-elf-run", elf], request)
        require(result.returncode == 125, f"observer request {name} did not fail closed")
        failures.append({"case": name, "exit": result.returncode, "stderr": result.stderr.strip()})
    simulator = Path(shutil.which("sh-elf-run")).resolve()
    report = {"status": "PASS", "container_image_id": image_id,
              "image_id_provenance": "immutable ID supplied by the host Docker invocation",
              "simulator_path": str(simulator), "simulator_sha256": sha256(simulator),
              "original_simulator_sha256": sha256("/usr/bin/sh-elf-run"),
              "stock_rom_sha256": STOCK_SHA256, "helper_sha256": sha256(helper),
              "elf_sha256": sha256(elf), "wrapper_sha256": hashlib.sha256(wrapper).hexdigest(),
              "trace_sha256": filtered_sha, "unfiltered_trace_sha256": unfiltered_sha,
              "ordinary_and_delay_records": len(records), "helper_entries": counts[HELPER_START],
              "unfiltered_records": len(unfiltered_records), "stdout": baseline.stdout.strip(),
              "fail_closed_cases": failures}
    (output / "probe-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image-id", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.output is None:
        with tempfile.TemporaryDirectory(prefix="vq-pctrace-probe-") as directory:
            probe(Path(directory), args.image_id)
    else:
        output = args.output.resolve()
        require(output == Path("/observation") or Path("/observation") in output.parents,
                "retained output must be inside the explicit /observation bind")
        output.mkdir(parents=True, exist_ok=True)
        require(not any(output.iterdir()), "retained output directory must be empty")
        probe(output, args.image_id)


if __name__ == "__main__":
    main()
