"""Signed SH branch evidence is independent of diagnostic objdump text."""

import ast
from pathlib import Path

import pytest

from patches import map_switching_assembly as assembly


ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("mnemonic,prefix", (
    ("bt", 0x8900), ("bf", 0x8b00), ("bt/s", 0x8d00), ("bf/s", 0x8f00),
))
@pytest.mark.parametrize("encoded,target", (
    (0x80, 0x0f04), (0xff, 0x1002), (0x00, 0x1004), (0x7f, 0x1102),
))
def test_conditional_target_boundaries_use_signed_instruction_bytes(mnemonic, prefix, encoded, target):
    statement = assembly.SourceStatement(1, 0x1000, "instruction", f"{mnemonic} target", 2)
    parsed = assembly.ParsedSource(Path("branch.s"), {"target": target}, (statement,))
    assert assembly._validate_direct_branch_encoding(parsed, statement, prefix | encoded) == target
    wrong = assembly.ParsedSource(parsed.path, {"target": target + 0x200}, parsed.statements)
    with pytest.raises(ValueError, match="targets .* expected"):
        assembly._validate_direct_branch_encoding(wrong, statement, prefix | encoded)


def test_backward_bf_receipt_example_targets_120_instead_of_320():
    statement = assembly.SourceStatement(1, 0x128, "instruction", "bf target", 2)
    parsed = assembly.ParsedSource(Path("branch.s"), {"target": 0x120}, (statement,))
    assert assembly._validate_direct_branch_encoding(parsed, statement, 0x8bfa) == 0x120


def test_firmware_gate_objdump_consumers_request_only_elf_metadata():
    found = set()
    for path in (ROOT / "tools/sh-elf-run").glob("*.py"):
        tree = ast.parse(path.read_text(), filename=str(path))
        for call in ast.walk(tree):
            if not isinstance(call, ast.Call) or not call.args:
                continue
            arguments = call.args[0]
            if not isinstance(arguments, (ast.List, ast.Tuple)) or not arguments.elts:
                continue
            command = arguments.elts[0]
            if not ((isinstance(command, ast.Name) and command.id == "OBJDUMP")
                    or (isinstance(command, ast.Constant) and command.value == "sh-elf-objdump")):
                continue
            options = [item.value for item in arguments.elts[1:]
                       if isinstance(item, ast.Constant) and isinstance(item.value, str)
                       and item.value.startswith("-")]
            assert options and options[0] in {"-h", "-t", "-r"}, path
            assert set(options) <= {"-h", "-t", "-r", "-j"}, path
            found.add(path.name)
    assert found == {"verify_map_switching.py", "verify_npkern_can.py"}
