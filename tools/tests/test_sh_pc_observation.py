"""Refusal contracts for optional byte-bound GNU SH PC observations."""

import ast
from dataclasses import replace
import hashlib
import importlib.util
from pathlib import Path
import re
import sys
import tempfile
from types import SimpleNamespace
import unittest


ROOT = Path(__file__).resolve().parents[2]
TOOL_DIR = ROOT / "tools/sh-elf-run"
sys.path.insert(0, str(TOOL_DIR))

import pc_observation as observation

SPEC = importlib.util.spec_from_file_location("verify_bfs_pc_observation", TOOL_DIR / "verify_bfs_pc_observation.py")
verifier = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verifier)


VALID = (b"VQ_SH_PC_TRACE version=1\n"
         b"pc=000224fa opcode=4021 delay=0\n"
         b"VQ_SH_PC_TRACE end=complete records=1\n")
MARKERS = {"begin": 0x200000, "return": 0x200004, "size": 8, "end": 0x200008}
HELPER = b"".join(word.to_bytes(2, "big") for word in verifier.HELPER_WORDS)
WRAPPER = bytes.fromhex("2f8600092f060009")


def records_for(overrides=None, omitted=()):
    records = []
    for index in range(verifier.CONTEXTS):
        if index in omitted:
            continue
        records.extend([(MARKERS["begin"], 0x2F86, 0), (MARKERS["begin"] + 2, 0x0009, 0)])
        expected = verifier.expectation_at(index)[2]
        count = (overrides or {}).get(index, 0 if expected is None else expected)
        for _ in range(count):
            records.extend(zip(verifier.HELPER_PCS, verifier.HELPER_WORDS, verifier.HELPER_DELAYS))
        records.append((MARKERS["return"], 0x2F06, 0))
    return records


class TraceParserTest(unittest.TestCase):
    def test_complete_ascii_lf_bytes_are_required(self):
        self.assertEqual(observation.parse_trace(VALID, 0), [(0x224FA, 0x4021, 0)])
        for code in (1, -9, 125, None, False):
            with self.subTest(exit=code), self.assertRaises(ValueError):
                observation.parse_trace(VALID, code)
        with self.assertRaises(ValueError):
            observation.parse_trace(VALID.decode("ascii"), 0)

    def test_incomplete_or_alternative_line_framing_is_rejected(self):
        malformed = (
            VALID[:-1], VALID.replace(b"\n", b"\r\n"), VALID.replace(b"\n", b"\r"),
            VALID.replace(b"\n", b"\v"), VALID.replace(b"\n", b"\f"),
            VALID.replace(b"\n", b"\x1c"), VALID.replace(b"\n", b"\x85"),
            VALID + b"junk\n", b"\n" + VALID, VALID + b"\n",
            VALID.replace(b"opcode=4021", b"opcode=40\xff1"),
        )
        for data in malformed:
            with self.subTest(data=data), self.assertRaises(ValueError):
                observation.parse_trace(data, 0)

    def test_header_footer_version_and_record_count_are_exact(self):
        header, row, footer, _ = VALID.split(b"\n")
        malformed = (
            header + b"\n" + row + b"\n", row + b"\n" + footer + b"\n",
            header + b"\n" + footer + b"\n", header + b"\n" + VALID,
            VALID + footer + b"\n", VALID.replace(b"version=1", b"version=2"),
            VALID.replace(b"records=1", b"records=0"), VALID.replace(b"records=1", b"records=01"),
            VALID.replace(b"records=1", b"records=2"), VALID.replace(b"complete", b"partial"),
        )
        for data in malformed:
            with self.subTest(data=data), self.assertRaises(ValueError):
                observation.parse_trace(data, 0)

    def test_instruction_width_address_and_delay_grammar_are_exact(self):
        malformed = (
            VALID.replace(b"000224fa", b"224fa"), VALID.replace(b"000224fa", b"000224FA"),
            VALID.replace(b"000224fa", b"000224fb"), VALID.replace(b"000224fa", b"1000224fa"),
            VALID.replace(b"4021", b"04021"), VALID.replace(b"4021", b"zzzz"),
            VALID.replace(b"delay=0", b"delay=2"), VALID.replace(b"delay=0", b"delay=00"),
            VALID.replace(b"pc=", b" pc="), VALID.replace(b"opcode=", b" opcode="),
        )
        for data in malformed:
            with self.subTest(data=data), self.assertRaises(ValueError):
                observation.parse_trace(data, 0)


class InvocationTest(unittest.TestCase):
    def validate(self, records, markers=MARKERS, helper=HELPER, wrapper=WRAPPER):
        return verifier.validate_records(records, markers, helper, wrapper)

    def test_valid_frames_have_independent_literal_expectations(self):
        frames = self.validate(records_for())
        checked = [frame for frame in frames if frame["count_checked"]]
        self.assertEqual(len(frames), 461)
        self.assertEqual(len(checked), 27)
        self.assertEqual(sum(frame["observed_helper_entries"] for frame in checked), 38)
        self.assertEqual(sum(not frame["count_checked"] for frame in frames), 434)

    def test_literal_zero_one_two_under_and_over_counts_are_rejected(self):
        for overrides in ({48: 1}, {41: 0}, {41: 2}, {28: 1}, {28: 3}):
            with self.subTest(overrides=overrides), self.assertRaises(ValueError):
                self.validate(records_for(overrides))

    def test_compensating_context_errors_cannot_preserve_acceptance(self):
        valid = records_for()
        total = sum(pc == verifier.HELPER_START for pc, _, _ in valid)
        # Each mutant retains the whole-run helper total while violating two caller contexts.
        for overrides in ({28: 1, 41: 2}, {28: 1, 48: 1}, {41: 0, 48: 1}):
            bad = records_for(overrides)
            self.assertEqual(sum(pc == verifier.HELPER_START for pc, _, _ in bad), total)
            with self.subTest(overrides=overrides), self.assertRaises(ValueError):
                self.validate(bad)

    def test_unchecked_contexts_are_labelled_without_invented_counts(self):
        frames = self.validate(records_for({0: 3}))
        self.assertFalse(frames[0]["count_checked"])
        self.assertIsNone(frames[0]["expected_helper_entries"])
        self.assertEqual(frames[0]["observed_helper_entries"], 3)

    def test_marker_frame_sequence_and_delay_corruption_are_rejected(self):
        records = records_for()
        mutations = (
            records[1:], records[:-1], records_for(omitted={48}), records + records[:3],
            [records[0], records[0], *records[1:]],
            [(records[0][0], records[0][1], 1), *records[1:]],
            [(pc, opcode, 0) for pc, opcode, _ in records],
            [(verifier.HELPER_START, verifier.HELPER_WORDS[0], 0), *records],
            [*records[:3], (verifier.HELPER_START, verifier.HELPER_WORDS[0], 0), *records[3:]],
        )
        for index, bad in enumerate(mutations):
            with self.subTest(mutation=index), self.assertRaises(ValueError):
                self.validate(bad)
        first = next(i for i, row in enumerate(records) if row[0] == verifier.HELPER_START)
        bad = records.copy()
        bad[first + 1], bad[first + 2] = bad[first + 2], bad[first + 1]
        with self.assertRaises(ValueError):
            self.validate(bad)
        with self.assertRaises(ValueError):
            self.validate(records[:first] + records[first + 1:])

    def test_all_wrapper_and_helper_opcodes_are_bound(self):
        records = records_for()
        indices = [0, 1, 2, next(i for i, row in enumerate(records) if row[0] == verifier.HELPER_START)]
        for index in indices:
            bad = records.copy()
            pc, opcode, delay = bad[index]
            bad[index] = (pc, opcode ^ 1, delay)
            with self.subTest(record=index), self.assertRaises(ValueError):
                self.validate(bad)
        with self.assertRaises(ValueError):
            self.validate(records, helper=b"\x00\x09" + HELPER[2:])
        with self.assertRaises(ValueError):
            self.validate(records, wrapper=WRAPPER[:-2])
        with self.assertRaises(ValueError):
            self.validate([(0x200001, 0x0009, 0), *records])
        with self.assertRaises(ValueError):
            self.validate([(0x300000, 0x0009, 0), *records])


class SourceAndElfBindingTest(unittest.TestCase):
    def test_published_observation_counts_and_identity_follow_the_execution_sources(self):
        text = (TOOL_DIR / "README.md").read_text(encoding="utf-8")
        section = " ".join(text.split("## Optional exact PC observation\n", 1)[1]
                           .split("\n## ", 1)[0].split())
        corrections = verifier.CORRECTION_EXPECTATIONS
        blends = verifier.BLEND_EXPECTATIONS
        checked = len(corrections) + len(blends)
        entries = sum(count for _, count in (*corrections, *blends))
        for phrase in (
            f"all {verifier.CONTEXTS} cases", f"separates {verifier.CONTEXTS} caller frames",
            f"check {len(corrections)} correction contexts", f"{len(blends)} blend contexts",
            f"{entries} checked helper entries", f"other {verifier.CONTEXTS - checked} frames",
        ):
            self.assertIn(phrase, section)
        recipe = (TOOL_DIR / "Dockerfile.pctrace").read_text(encoding="ascii")
        archive_digest = re.findall(r"'([0-9a-f]{64})'", recipe)[0]
        self.assertIn(archive_digest, section)
        version = re.search(r"gdb-([0-9.]+)\.tar\.xz", recipe)[1]
        self.assertIn(f"GNU{version}", section)
        patch = (TOOL_DIR / "gnu16.3-sh-pc-observer.patch").read_text(encoding="ascii")
        ranges = int(re.search(r"vq_sh_pc_trace_ranges\[(\d+)\]", patch)[1])
        self.assertIn(f"up to {ranges} comma-separated", section)
        probe = ast.parse((TOOL_DIR / "probe_pc_observation.py").read_text(encoding="ascii"))
        invalid = [node.value for node in ast.walk(probe) if isinstance(node, ast.Assign)
                   and any(isinstance(target, ast.Name) and target.id == "invalid"
                           for target in node.targets)]
        self.assertEqual(len(invalid), 1)
        names = [item.elts[0].value for item in invalid[0].elts]
        self.assertEqual(len(names), len(set(names)))
        number_words = {10: "Ten"}
        self.assertIn(f"{number_words[len(names)]} malformed or unwritable requests", section)

    def test_unrelated_invokers_do_not_change_the_bfs_function_pin(self):
        source = (TOOL_DIR / "stock_invoke.s").read_bytes()
        block = observation.function_block(source, "_stock_invoke_bfs_rate")
        altered = source + b"\n    .global _unrelated\n_unrelated:\n    rts\n    nop\n"
        self.assertEqual(observation.function_block(altered, "_stock_invoke_bfs_rate"), block)
        self.assertEqual(hashlib.sha256(block).hexdigest(), verifier.FUNCTION_SHA256)
        for bad in (source + block, source.replace(b".size _stock_invoke_bfs_rate", b".size _other")):
            with self.assertRaises(ValueError):
                observation.function_block(bad, "_stock_invoke_bfs_rate")

    def test_narrow_source_and_region_contracts_allow_unrelated_registry_additions(self):
        verifier.source_bindings()
        region = verifier.registered_region(verifier.stock.REGIONS)
        self.assertIs(verifier.registered_region((*verifier.stock.REGIONS, replace(region, key="unrelated"))), region)
        for field in ("cases", "end", "return_register"):
            bad = replace(region, **{field: getattr(region, field) + 1})
            with self.subTest(field=field), self.assertRaises(ValueError):
                verifier.registered_region((bad,))
        for regions in ((), (region, region)):
            with self.assertRaises(ValueError):
                verifier.registered_region(regions)

    def test_elf_markers_refuse_missing_duplicate_odd_and_outside_addresses(self):
        valid = "00200000 00000008 T begin\n00200004 t returned\n"
        self.assertEqual(observation.symbols_from_nm(valid, "begin", "returned"), MARKERS)
        malformed = (valid + "00200004 t returned\n", valid.splitlines()[0],
                     valid.replace("00200004", "00200008"), valid.replace("00200004", "00200005"),
                     valid.replace("00000008", "00000000"), valid.replace("00000008", "00000007"))
        for text in malformed:
            with self.subTest(text=text), self.assertRaises(ValueError):
                observation.symbols_from_nm(text, "begin", "returned")
        with self.assertRaises(ValueError):
            observation.symbols_from_nm(valid, "begin", "returned", (0x200000, 0x200008))

    def test_linked_byte_extraction_is_separate_and_detects_input_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            elf = output / "input.elf"
            elf.write_bytes(b"original ELF")
            def command(args):
                if args[0] == "sh-elf-objdump":
                    return SimpleNamespace(stdout="  0 .text 00000008 00200000 00200000 00000100 2**2\n")
                self.assertNotEqual(Path(args[-1]), elf)
                Path(args[-1]).write_bytes(WRAPPER)
                return SimpleNamespace(stdout="")
            self.assertEqual(observation.wrapper_bytes_from_elf(elf, output, MARKERS, command), WRAPPER)
            def mutating_command(args):
                result = command(args)
                if args[0] != "sh-elf-objdump":
                    elf.write_bytes(b"changed ELF")
                return result
            with self.assertRaises(ValueError):
                observation.wrapper_bytes_from_elf(elf, output, MARKERS, mutating_command)

    def test_reviewed_observer_patch_and_build_source_hashes_are_exact(self):
        patch = (TOOL_DIR / "gnu16.3-sh-pc-observer.patch").read_bytes()
        self.assertEqual(hashlib.sha256(patch).hexdigest(),
                         "e10df675becfc427532ef6ba9ea7b056398f48db75ba231d4a720f7928fcc5cd")
        self.assertEqual([line for line in patch.splitlines() if line.startswith(b"+++ ")],
                         [b"+++ b/sim/sh/interp.c"])
        recipe = (TOOL_DIR / "Dockerfile.pctrace").read_text(encoding="ascii")
        for digest in (
            "bcfcd095528a987917acf9fff3f1672181694926cc18d609c99d0042c00224c5",
            "973ac1c5d193af70a5f1b8f7f0f2a4bd6aec957a0a3533ec878e795dbab9eb10",
            "99f809d2a5c710a7d3fe3f97aa19ed92c8ad00bf5ed0a153384457e7a5fa3a42",
            hashlib.sha256(patch).hexdigest(),
        ):
            self.assertIn(digest, recipe)
        self.assertIn("COPY --from=gnu-source gdb-16.3.tar.xz", recipe)
        self.assertIn("patch --batch --fuzz=0 -p1", recipe)
        self.assertIn("sha256sum -c /tmp/stock-toolchain.sha256", recipe)


if __name__ == "__main__":
    unittest.main()
