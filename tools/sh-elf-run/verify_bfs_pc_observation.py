"""Optionally observe per-context signed-helper calls through the primary BFS API."""

from __future__ import annotations

import argparse
import hashlib
import dataclasses
import json
import os
from pathlib import Path
import re
import shutil
import sys


ROOT = Path(__file__).resolve().parents[2]
TOOL_DIR = ROOT / "tools/sh-elf-run"
sys.path.insert(0, str(TOOL_DIR))

import verify_stock_code as stock
from pc_observation import (function_block, parse_trace, require, segment_invocations,
                            sha256, symbols_from_nm, wrapper_bytes_from_elf)


KEY = "jk08a-bfs-rate"
CONTEXTS = 461
HELPER_START, HELPER_END = 0x224FA, 0x22508
HELPER_PCS = tuple(range(HELPER_START, HELPER_END, 2))
HELPER_WORDS = (0x4021, 0x4021, 0x4021, 0x4021, 0x4021, 0x000B, 0x4021)
HELPER_DELAYS = (0, 0, 0, 0, 0, 0, 1)
CORRECTION_EXPECTATIONS = (
    ("zero", 2),
    ("negative-single-count", 2),
    ("positive-single-count", 2),
    ("negative-stock-gain", 2),
    ("positive-stock-gain", 2),
    ("negative-quantum-below", 2),
    ("negative-quantum-at", 2),
    ("negative-quantum-above", 2),
    ("positive-quantum-below", 2),
    ("positive-quantum-at", 2),
    ("positive-quantum-above", 2),
    ("negative-cap-before", 2),
    ("negative-cap-at", 2),
    ("negative-cap-after", 1),
    ("positive-cap-before", 2),
    ("positive-cap-at", 2),
    ("positive-cap-after", 2),
    ("negative-wide-stock", 1),
    ("positive-wide-stock", 2),
    ("zero-gain", 2),
)
BLEND_EXPECTATIONS = (
    ("coefficient-zero", 0),
    ("coefficient-one", 0),
    ("coefficient-half", 0),
    ("coefficient-last", 0),
    ("equal-maximum", 0),
    ("descending-fraction", 0),
    ("ascending-fraction", 0),
)
SOURCE_SHA256 = {'tools/sh-elf-run/harness-stock-jk08a-bfs-rate.c': '4ae86a69d83faa2c4de55d4f2719cea8599c2ee36a926d1e729211f6a5b96383',
 'tools/sh-elf-run/stock-jk08a-bfs-rate-cases.h': 'de11095a0e37af0b527fb1986430e5bf416eaa6f237cb848c0049b308b938ce1',
 'tools/sh-elf-run/stock_jk08a_bfs_rate.s': 'a1728f00c571858a79fc1acaa965ecbbb5f6ceb3926fa4db761883aade8eb469'}
FUNCTION_SHA256 = 'cc6604d67ad5b7b31df2f29633f5f4f119c27dffa1b05e4bd4ed24a740d6e4a8'
STOCK_SHA256 = "ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23"
FIXTURE_SHA256 = "d15d8a3ddb0ca0365673ba8178b17855920176bd7c4f6164f32cc6ec720b82e3"
EXPECTED_REGION = {'key': 'jk08a-bfs-rate',
 'rom': 'JK08A',
 'source': 'stock_jk08a_bfs_rate.s',
 'harness': 'harness-stock-jk08a-bfs-rate.c',
 'start': 244516,
 'end': 244614,
 'pools': [[33561, 2], [34394, 1], [36242, 1], [154520, 4], [244176, 8], [244514, 2], [244676, 40]],
 'ram_literals': [154520, 244176, 244180, 244680, 244688, 244692, 244712],
 'cases': 461,
 'boundary': True,
 'return_address_offset': 24,
 'return_register': 1,
 'base_load': None,
 'symbols': [['Q7_SOURCE', 'tall-quoll/ram'],
             ['SELECTED_SOURCE', 'fanatic-marten/ram'],
             ['COEFFICIENT', 'bfs_rate_coefficient/ram'],
             ['REFERENCE', 'flashy-elk/ram'],
             ['WORKING', 'elite-dormouse/ram'],
             ['BLENDED', 'wise-squirrel/ram'],
             ['CORRECTION', 'magenta-anaconda/ram'],
             ['FLAGS', 'bfs_state_flags/ram'],
             ['ALPHA', 'alpha_n_flow/ram'],
             ['ENABLE', 'burrowing-platypus/ram'],
             ['DIAGNOSTIC', 'busy-bird/ram'],
             ['WEIGHT', 'bfs_blend_weight/ram'],
             ['BLEND_PRIOR', 'nifty-otter/ram'],
             ['TIMER_FIRST', 'bfs_rate_timer_first/ram'],
             ['TIMER_SECOND', 'bfs_rate_timer_second/ram'],
             ['TIMER_THIRD', 'bfs_rate_timer_third/ram'],
             ['SOURCE_FIRST', 'slick-bullfinch/ram'],
             ['SOURCE_SECOND', 'macho-weasel/ram'],
             ['MONITOR', 'bfs_rate_timer_monitor/ram'],
             ['MODE', 'bfs_mode_flags/tbl'],
             ['CORRECTION_GAIN', 'bfs_correction_gain/tbl'],
             ['LATCH_SET', 'bfs_alpha_latch_set/tbl'],
             ['LATCH_CLEAR', 'bfs_alpha_latch_clear/tbl'],
             ['QUERY_RECORDS', 'hallowed-malkoha/ram'],
             ['QUERY_ENTRY', 'diagnostic_record_byte2_fault_predicate/fn']],
 'bits': [],
 'constants': [['PRIMARY_ENTRY', 243976],
               ['CORRECTION_ENTRY', 244408],
               ['BLEND_ENTRY', 244540],
               ['POST_QUERY_ENTRY', 244330],
               ['PRIMARY_BASE', 4294906132],
               ['MODE_BASE', 4294911072]],
 'callees': [[243976, 244108], [244184, 244514], [140538, 140552], [154084, 154130]]}
EXPECTED_DEFINES = {'REGION_ENTRY': 244516,
 'Q7_SOURCE': 4294905954,
 'SELECTED_SOURCE': 4294906204,
 'COEFFICIENT': 4294909744,
 'REFERENCE': 4294909446,
 'WORKING': 4294909422,
 'BLENDED': 4294909420,
 'CORRECTION': 4294905952,
 'FLAGS': 4294911153,
 'ALPHA': 4294906224,
 'ENABLE': 4294911074,
 'DIAGNOSTIC': 4294911165,
 'WEIGHT': 4294909665,
 'BLEND_PRIOR': 4294909444,
 'TIMER_FIRST': 4294909472,
 'TIMER_SECOND': 4294909511,
 'TIMER_THIRD': 4294909516,
 'SOURCE_FIRST': 4294911049,
 'SOURCE_SECOND': 4294918736,
 'MONITOR': 4294911054,
 'MODE': 36242,
 'CORRECTION_GAIN': 34394,
 'LATCH_SET': 33561,
 'LATCH_CLEAR': 33562,
 'QUERY_RECORDS': 4294924056,
 'QUERY_ENTRY': 154084,
 'PRIMARY_ENTRY': 243976,
 'CORRECTION_ENTRY': 244408,
 'BLEND_ENTRY': 244540,
 'POST_QUERY_ENTRY': 244330,
 'PRIMARY_BASE': 4294906132,
 'MODE_BASE': 4294911072}


def source_bindings():
    for relative, expected in SOURCE_SHA256.items():
        require(sha256(ROOT / relative) == expected, f"source identity differs: {relative}")
    block = function_block((TOOL_DIR / "stock_invoke.s").read_bytes(), "_stock_invoke_bfs_rate")
    require(hashlib.sha256(block).hexdigest() == FUNCTION_SHA256, "BFS invoker function differs")
    header = (TOOL_DIR / "stock-jk08a-bfs-rate-cases.h").read_text(encoding="ascii")
    def names(array):
        match = re.search(r"static const struct \w+ " + array + r"\[\] = \{(.*?)^\};",
                          header, re.M | re.S)
        require(match is not None, f"missing literal array: {array}")
        return re.findall(r'^\s*\{"([^"]+)"', match[1], re.M)
    require(len(names("rate_cases")) == 28, "correction ordinal requires 28 rate cases")
    require(names("correction_cases") == [name for name, _ in CORRECTION_EXPECTATIONS],
            "correction literal names or order differ")
    require(names("blend_cases") == [name for name, _ in BLEND_EXPECTATIONS],
            "blend literal names or order differ")
    return {**SOURCE_SHA256, "stock_invoke.s::_stock_invoke_bfs_rate": FUNCTION_SHA256}


def registered_region(regions):
    matches = [region for region in regions if region.key == KEY]
    require(len(matches) == 1, "registered BFS region is missing or duplicated")
    region = matches[0]
    # JSON normalization compares the complete narrow dataclass, not unrelated regions.
    actual = json.loads(json.dumps(dataclasses.asdict(region)))
    require(actual == EXPECTED_REGION, "registered BFS Region contract differs")
    return region


def expectation_at(index):
    if 28 <= index < 48:
        name, count = CORRECTION_EXPECTATIONS[index - 28]
        return "correction", name, count
    if 48 <= index < 55:
        name, count = BLEND_EXPECTATIONS[index - 48]
        return "blend", name, count
    return "observed", None, None


def validate_records(records, markers, helper_bytes, wrapper_bytes):
    require(helper_bytes == b"".join(word.to_bytes(2, "big") for word in HELPER_WORDS),
            "stock helper bytes differ from the literal seven-instruction reconstruction")
    counts = segment_invocations(records, {**markers, "bytes": wrapper_bytes}, HELPER_START,
                                 helper_bytes, HELPER_DELAYS, CONTEXTS)
    frames = []
    for index, count in enumerate(counts):
        scope, name, expected = expectation_at(index)
        if expected is not None:
            require(count == expected,
                    f"context {index + 1} {scope}/{name}: observed {count}, expected {expected}")
        frames.append({"ordinal": index + 1, "scope": scope, "name": name,
                       "observed_helper_entries": count, "expected_helper_entries": expected,
                       "count_checked": expected is not None})
    require(sum(frame["count_checked"] for frame in frames) == 27, "literal expectation scope differs")
    return frames


def self_check():
    source_bindings()
    registered_region(stock.REGIONS)
    print("BFS_PC_OBSERVATION_CHECKER status=PREPARED source_contract=PASS firmware_executed=false")


def observe(output, image_id):
    require(re.fullmatch(r"sha256:[0-9a-f]{64}", image_id) is not None,
            "supply the immutable image ID from the host Docker invocation")
    require(output.is_absolute() and (output == Path("/observation") or Path("/observation") in output.parents),
            "retained output must be inside the authorized /observation bind")
    output.mkdir(parents=True, exist_ok=True)
    require(not any(output.iterdir()), "retained output directory must be empty")
    bindings = source_bindings()
    region = registered_region(stock.REGIONS)
    require(region.cases == CONTEXTS, "registered context count differs")
    image = stock.stock_image(region.rom)
    require(hashlib.sha256(image).hexdigest() == STOCK_SHA256, "stock ROM identity differs")
    require(stock.harness_defines(region, image) == EXPECTED_DEFINES, "native harness bindings differ")
    require(hashlib.sha256(stock.build_fixture(region, image)).hexdigest() == FIXTURE_SHA256,
            "registered fixture differs from the accepted byte-bound fixture")
    helper = image[HELPER_START:HELPER_END]
    build_dir = output / "registered-build"
    build_dir.mkdir()
    invoke = build_dir / "stock-invoke.o"
    base = stock.base_verifier
    original_command = base.run_command
    trace = output / "pc-trace.log"
    captured = {}
    saved_environment = {name: value for name, value in os.environ.items()
                         if name.startswith("VQ_SH_PC_TRACE_")}
    for name in saved_environment:
        del os.environ[name]
    try:
        version = original_command([base.RUN, "--version"])
        require("16.3" in version.stdout, "simulator version differs")
        simulator = Path(shutil.which(base.RUN)).resolve()
        original_command([base.AS, "--big", "--isa=sh2e", "-o", invoke, TOOL_DIR / "stock_invoke.s"])
        def observe_registered_command(command, **kwargs):
            if str(command[0]) != base.RUN:
                return original_command(command, **kwargs)
            require(not captured, "registered runner invoked more than once")
            elf = Path(command[-1])
            require(elf == build_dir / f"{KEY}-harness.elf", "registered ELF path differs")
            nm = original_command(["sh-elf-nm", "-S", "-n", elf])
            (output / "elf-symbols.txt").write_text(nm.stdout)
            markers = symbols_from_nm(nm.stdout, "_stock_invoke_bfs_rate", "L_bfs_rate_return",
                                      (HELPER_START, HELPER_END))
            wrapper = wrapper_bytes_from_elf(elf, output, markers, original_command, base.OBJCOPY)
            ranges = f"{HELPER_START:x}:{HELPER_END:x},{markers['begin']:x}:{markers['end']:x}"
            os.environ.update(VQ_SH_PC_TRACE_FILE=str(trace), VQ_SH_PC_TRACE_FORMAT="v1",
                              VQ_SH_PC_TRACE_RANGES=ranges)
            try:
                result = original_command(command, **kwargs)
            finally:
                for name in ("VQ_SH_PC_TRACE_FILE", "VQ_SH_PC_TRACE_FORMAT", "VQ_SH_PC_TRACE_RANGES"):
                    os.environ.pop(name, None)
            (output / "harness.stdout").write_text(result.stdout)
            (output / "harness.stderr").write_text(result.stderr)
            marker = f"VQ_SH_ELF_STOCK_CODE status=PASS region={KEY} cases={CONTEXTS}"
            require(result.returncode == 0 and result.stdout.splitlines().count(marker) == 1,
                    "registered harness lacks one exact complete PASS marker")
            records = parse_trace(trace.read_bytes(), result.returncode)
            frames = validate_records(records, markers, helper, wrapper)
            captured.update(markers=markers, ranges=ranges, records=len(records), frames=frames,
                            harness_marker=marker, elf_sha256=sha256(elf),
                            invocation_wrapper_sha256=hashlib.sha256(wrapper).hexdigest(),
                            fixture_sha256=sha256(build_dir / f"{KEY}.sim-fixture"))
            return result
        base.run_command = observe_registered_command
        instructions = stock.run_region(region, invoke, build_dir)
        require(captured.get("fixture_sha256") == FIXTURE_SHA256, "executed fixture identity differs")
        require(instructions == 310 and captured, "registered instruction count or execution differs")
        source_bindings()
        checked = [frame for frame in captured["frames"] if frame["count_checked"]]
        report = {"status": "PASS", "region": KEY, "container_image_id": image_id,
                  "image_id_provenance": "immutable ID supplied by the host Docker invocation", "registered_instructions": instructions,
                  "context_frames": CONTEXTS, "count_checked_contexts": len(checked),
                  "count_unchecked_contexts": CONTEXTS - len(checked),
                  "checked_helper_entries": sum(frame["observed_helper_entries"] for frame in checked),
                  "helper_stock_sha256": hashlib.sha256(helper).hexdigest(),
                  "stock_rom_sha256": hashlib.sha256(image).hexdigest(),
                  "source_sha256": bindings,
                  "observer_tool_sha256": {name: sha256(TOOL_DIR / name) for name in
                      ("gnu16.3-sh-pc-observer.patch", "Dockerfile.pctrace", "pc_observation.py",
                       "verify_bfs_pc_observation.py", "probe_pc_observation.py")},
                  "simulator_path": str(simulator),
                  "simulator_sha256": sha256(simulator), "trace_sha256": sha256(trace), **captured}
        (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        print("BFS_PC_OBSERVATION status=PASS context_frames=461 count_checked_contexts=27 checked_helper_entries=38")
    except BaseException as error:
        (output / "failure.txt").write_text(str(error) + "\n")
        raise
    finally:
        base.run_command = original_command
        for name in tuple(os.environ):
            if name.startswith("VQ_SH_PC_TRACE_"):
                del os.environ[name]
        os.environ.update(saved_environment)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--image-id")
    args = parser.parse_args()
    require(args.self_check != (args.output is not None), "choose only self-check or retained observation")
    if args.self_check:
        self_check()
    else:
        require(args.image_id is not None, "observation requires --image-id")
        observe(args.output.resolve(), args.image_id)


if __name__ == "__main__":
    main()
