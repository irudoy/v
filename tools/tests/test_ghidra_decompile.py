"""Primary code-cache acceptance and rollback without a live Ghidra project."""

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from kb import repo
from kb.repo import KbError
from kb import ghidra_preparation as preparation
from tools.ghidra import decompile
from tools.tests.test_ghidra_preparation import prepared_root, receipt_of


def cached(target, key="accepted", text="// FUN_00000100 @ 00000100  size=8\naccepted\n"):
    target.mkdir(parents=True)
    (target / "decomp_00000100.c").write_text(text)
    (target / ".decompile-key").write_text(key + "\n")
    (target / ".decompile-files.json").write_text(json.dumps(
        {"schema_version": 1, "key": key, "files": {
            "decomp_00000100.c": hashlib.sha256(text.encode()).hexdigest()}}))


def disk_state(path):
    return {str(item.relative_to(path)): item.read_bytes()
            for item in path.rglob("*") if item.is_file()}


def runner(root, *, fail=None, change=None):
    """A primary process result whose prepared outputs are sealed together."""
    def run(command, **kwargs):
        arguments = list(command)
        assert "-readOnly" in arguments
        assert "-noanalysis" in arguments
        if fail == "process":
            return SimpleNamespace(returncode=1, stdout="", stderr="primary failed")
        sha_index = arguments.index("ProgramSha256.java") + 1
        sha_path = Path(arguments[sha_index])
        stage = sha_path.parent
        plan = preparation.plan("t1", root)
        sha_path.write_text(plan.image_sha256 + "\n")
        if fail == "image":
            sha_path.write_text("0" * 64 + "\n")
        if "DecompileFuncs.java" in arguments:
            index = arguments.index("DecompileFuncs.java") + 2
            while index < len(arguments) and arguments[index] != "-postScript":
                entry = arguments[index]
                text = f"// FUN_{entry} @ {entry}  size=8\nprepared\n"
                if fail == "decompiler":
                    text += "// decompile failed: rejected\n"
                if fail != "missing":
                    (stage / f"decomp_{entry}.c").write_text(text)
                index += 1
        if "DumpFuncListing.java" in arguments:
            index = arguments.index("DumpFuncListing.java") + 2
            while index < len(arguments) and arguments[index] != "-postScript":
                entry = arguments[index]
                (stage / f"funclisting_{entry}.txt").write_text(
                    f"// FUN_{entry} @ {entry}  size=8\n00000100 nop\n")
                index += 1
        if "PrepareProgram.java" in arguments and fail != "receipt":
            index = arguments.index("seal")
            wire, receipt = map(Path, arguments[index + 1:index + 3])
            outputs = [stage / name for name in arguments[index + 3:] if (stage / name).exists()]
            document = receipt_of(plan, outputs)
            document["wire_sha256"] = repo.sha256_file(wire)
            receipt.write_text(json.dumps(document))
        if change:
            change()
        return SimpleNamespace(returncode=0, stdout="primary prepared", stderr="")
    return run


@pytest.mark.parametrize("failure", ["process", "image", "receipt", "missing", "decompiler"])
def test_failed_primary_run_keeps_previous_cache_and_key(prepared_root, tmp_path, failure):
    root, _ = prepared_root
    target = tmp_path / "cache"
    cached(target)
    accepted = disk_state(target)
    with patch.object(decompile.program_name, "cache_key", return_value="prepared"), \
            patch.object(decompile.subprocess, "run", side_effect=runner(root, fail=failure)):
        with pytest.raises(KbError):
            decompile.decompile("T1", ["100"], project_dir=tmp_path, program="T1.bin",
                                outdir=target, root=root)
    assert disk_state(target) == accepted


def test_verified_primary_outputs_and_key_promote_together(prepared_root, tmp_path):
    root, _ = prepared_root
    target = tmp_path / "cache"
    cached(target)
    with patch.object(decompile.program_name, "cache_key", return_value="prepared"), \
            patch.object(decompile.subprocess, "run", side_effect=runner(root)) as run:
        paths = decompile.decompile("T1", ["100"], project_dir=tmp_path, program="T1.bin",
                                    outdir=target, listings=True, root=root)
        assert [path.name for path in paths] == ["decomp_00000100.c", "funclisting_00000100.txt"]
        assert "prepared" in paths[0].read_text()
        assert (target / ".decompile-key").read_text() == "prepared\n"
        again = decompile.decompile("T1", ["100"], project_dir=tmp_path, program="T1.bin",
                                    outdir=target, listings=True, root=root)
        assert again == paths
        assert run.call_count == 1


def test_modified_cached_output_is_rebuilt_not_served(prepared_root, tmp_path):
    root, _ = prepared_root
    target = tmp_path / "cache"
    cached(target, key="prepared")
    (target / "decomp_00000100.c").write_text("// FUN_00000100 @ 00000100  size=8\nmodified\n")
    with patch.object(decompile.program_name, "cache_key", return_value="prepared"), \
            patch.object(decompile.subprocess, "run", side_effect=runner(root)) as run:
        paths = decompile.decompile("T1", ["100"], project_dir=tmp_path, program="T1.bin",
                                    outdir=target, root=root)
        assert run.call_count == 1
        assert "modified" not in paths[0].read_text()


def test_changed_preparation_input_refuses_inflight_outputs(prepared_root, tmp_path):
    root, _ = prepared_root
    target = tmp_path / "cache"
    cached(target)
    accepted = disk_state(target)
    script = root / repo.GHIDRA_SCRIPTS / "RecoverFuncs.java"
    def change():
        script.write_text("changed after primary preparation\n")
    def key(*args, **kwargs):
        return preparation.plan("t1", root).digest
    with patch.object(decompile.program_name, "cache_key", side_effect=key), \
            patch.object(decompile.subprocess, "run", side_effect=runner(root, change=change)):
        with pytest.raises(KbError, match="key changed"):
            decompile.decompile("T1", ["100"], project_dir=tmp_path, program="T1.bin",
                                outdir=target, root=root)
    assert disk_state(target) == accepted


def test_cache_promotion_failure_rolls_back_accepted_outputs(prepared_root, tmp_path):
    root, _ = prepared_root
    target = tmp_path / "cache"
    cached(target)
    accepted = disk_state(target)
    original = Path.rename
    def rename(path, destination):
        if path.name == "replacement":
            raise OSError("injected cache promotion failure")
        return original(path, destination)
    with patch.object(decompile.program_name, "cache_key", return_value="prepared"), \
            patch.object(decompile.subprocess, "run", side_effect=runner(root)), \
            patch.object(Path, "rename", rename):
        with pytest.raises(OSError, match="cache promotion"):
            decompile.decompile("T1", ["100"], project_dir=tmp_path, program="T1.bin",
                                outdir=target, root=root)
    assert disk_state(target) == accepted


def test_only_changed_key_removes_previous_accepted_code_after_verification(prepared_root, tmp_path):
    root, _ = prepared_root
    target = tmp_path / "cache"
    cached(target)
    (target / "decomp_00000104.c").write_text("// obsolete\n")
    (target / "notes.txt").write_text("unrelated local note\n")
    with patch.object(decompile.program_name, "cache_key", return_value="prepared"), \
            patch.object(decompile.subprocess, "run", side_effect=runner(root)):
        decompile.decompile("T1", ["100"], project_dir=tmp_path, program="T1.bin",
                            outdir=target, root=root)
    assert not (target / "decomp_00000104.c").exists()
    assert (target / "notes.txt").read_text() == "unrelated local note\n"


@pytest.mark.parametrize("raw", ["-1", "100000000", "invalid"])
def test_bad_entry_cannot_change_accepted_code_cache(prepared_root, tmp_path, raw):
    root, _ = prepared_root
    target = tmp_path / "cache"
    cached(target)
    accepted = disk_state(target)
    with patch.object(decompile.subprocess, "run") as run:
        with pytest.raises((KbError, ValueError)):
            decompile.decompile("T1", [raw], project_dir=tmp_path, program="T1.bin",
                                outdir=target, root=root)
    assert not run.called
    assert disk_state(target) == accepted


def test_symlink_cache_refuses_before_primary_run(prepared_root, tmp_path):
    root, _ = prepared_root
    actual, link = tmp_path / "actual", tmp_path / "link"
    cached(actual)
    link.symlink_to(actual, target_is_directory=True)
    accepted = disk_state(actual)
    with patch.object(decompile.subprocess, "run") as run:
        with pytest.raises(KbError, match="nonsymlink"):
            decompile.decompile("T1", ["100"], project_dir=tmp_path, program="T1.bin",
                                outdir=link, root=root)
    assert not run.called
    assert disk_state(actual) == accepted


def test_old_cache_metadata_array_is_rebuilt_instead_of_crashing(prepared_root, tmp_path):
    root, _ = prepared_root
    target = tmp_path / "cache"
    cached(target, key="prepared")
    (target / ".decompile-files.json").write_text("[]\n")
    with patch.object(decompile.program_name, "cache_key", return_value="prepared"), \
            patch.object(decompile.subprocess, "run", side_effect=runner(root)) as run:
        paths = decompile.decompile("T1", ["100"], project_dir=tmp_path, program="T1.bin",
                                    outdir=target, root=root)
    assert run.call_count == 1
    assert "prepared" in paths[0].read_text()


def test_unprepared_layout_uses_the_same_primary_runner_and_output_validation(prepared_root, tmp_path):
    root, _ = prepared_root
    target = tmp_path / "cache"
    prepared = preparation.plan("t1", root)
    def primary_run(command, **kwargs):
        assert "PrepareProgram.java" not in command
        sha = Path(command[command.index("ProgramSha256.java") + 1])
        sha.write_text(prepared.image_sha256 + "\n")
        (sha.parent / "decomp_00000100.c").write_text(
            "// FUN_00000100 @ 00000100  size=8\nprimary\n")
        return SimpleNamespace(returncode=0, stdout="primary", stderr="")
    with patch.object(decompile.preparation, "plan", return_value=None), \
            patch.object(decompile.program_name, "cache_key", return_value="primary"), \
            patch.object(decompile.subprocess, "run", side_effect=primary_run):
        paths = decompile.decompile("T1", ["100"], project_dir=tmp_path, program="T1.bin",
                                    outdir=target, root=root)
    assert "primary" in paths[0].read_text()


def test_failed_acceptance_keeps_the_original_primary_diagnostic(tmp_path, capsys):
    import tempfile
    original = tempfile.NamedTemporaryFile
    def output(*args, **kwargs):
        return original(*args, **{**kwargs, "dir": tmp_path})
    result = SimpleNamespace(returncode=0, stdout="primary script refused\n", stderr="exact reason\n")
    with patch.object(decompile.tempfile, "NamedTemporaryFile", side_effect=output), \
            patch.object(decompile.subprocess, "run", return_value=result):
        with pytest.raises(KbError, match="receipt refused"):
            with decompile.primary_result(["primary"], tmp_path):
                raise KbError("receipt refused")
    logs = list(tmp_path.glob("ghidra-decompile-*.log"))
    assert len(logs) == 1
    assert logs[0].read_text() == "primary script refused\nexact reason\n"
    assert str(logs[0]) in capsys.readouterr().err
