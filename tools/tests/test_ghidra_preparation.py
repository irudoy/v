"""Contracts of exact-image, reviewed primary preparation and output acceptance."""

import hashlib
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from kb import repo
from kb.repo import KbError
from kb import ghidra_preparation as prep


@pytest.fixture
def prepared_root(tmp_path):
    root = tmp_path / "repo"
    (root / "rom-images/T1").mkdir(parents=True)
    data = bytearray(b"\x00\x09" * 256)
    data[0x20:0x24] = (0x100).to_bytes(4, "big")
    image = bytes(data)
    digest = hashlib.sha256(image).hexdigest()
    (root / "rom-images/T1/T1.bin").write_bytes(image)
    (root / repo.CATALOG).write_text(
        f"path,rom,sha256,note\nT1/T1.bin,T1,{digest},synthetic\n")
    (root / repo.HOMOLOGY).write_text(
        '[family.test]\nkind = "exact-code"\nmembers = ["T1"]\ncanonical = "T1"\n'
        'mcu = "SH7058"\nsame_address_inheritance = false\nlayouts = { t1 = "T1" }\n')
    (root / prep.SEEDS).mkdir(parents=True)
    (root / prep.MERGES).mkdir(parents=True)
    (root / prep.MERGES / "t1.csv").write_text(
        "entry,fragment,note\n00000100,00000104,reviewed fall-through\n")
    (root / repo.GHIDRA_PIN).write_text("GHIDRA_VERSION=12.1.4\n")
    for name in prep.SCRIPTS:
        (root / repo.GHIDRA_SCRIPTS / name).write_text(f"fixture {name}\n")
    for name in prep.BUILDERS:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"fixture {name}\n")
    output_scripts = (
        "ProgramSha256.java", "ExportGraph.java", "ExportXrefs.java",
        "ExportFunctionSignatures.java", "ExportFunctionTokens.java", "ResolveAccessors.java",
        "DecompileFuncs.java", "DumpFuncListing.java",
    )
    for name in output_scripts:
        (root / repo.GHIDRA_SCRIPTS / name).write_text(f"fixture {name}\n")
    (root / repo.CONFIG).parent.mkdir(parents=True, exist_ok=True)
    (root / repo.CONFIG).write_text(
        '[l0]\nscripts = ["ExportGraph.java"]\n'
        '[l0.census.t1]\ninterp = "tools/ghidra/census-input.csv"\n')
    (root / "tools/ghidra/census-input.csv").write_text(
        "family,kernel,wrapper\nexplicit,00000100,00000100\n")
    instruction_digest = hashlib.sha256(image[0x100:0x108]).hexdigest()
    fragment_digest = hashlib.sha256(image[0x104:0x108]).hexdigest()
    (root / prep.SEEDS / "t1.toml").write_text(
        'schema_version = 1\nlayout = "t1"\nimage = "T1"\n'
        f'image_sha256 = "{digest}"\nimage_size = 512\n'
        'forbidden_entries = ["00000110"]\n\n'
        '[[seed]]\nentry = "00000100"\nsites = ["00000104", "00000106"]\n'
        'bytes = 8\ninstructions = 4\nranges = 1\n'
        f'instruction_sha256 = "{instruction_digest}"\n\n'
        '[[seed.fragment]]\nentry = "00000104"\ninstructions = 2\n'
        f'instruction_sha256 = "{fragment_digest}"\n\n'
        '[[pin]]\naddress = "00000020"\nbytes = "00000100"\n\n'
        '[[pin]]\naddress = "00000100"\nbytes = "0009"\n\n'
        '[[reference]]\nowner = "00000100"\nsite = "00000104"\n'
        'target = "ffff1000"\ntype = "write"\n')
    return root, image


def test_plan_is_read_only_and_binds_primary_scripts(prepared_root):
    root, _ = prepared_root
    plan = prep.plan("t1", root)
    assert plan.layout == "t1"
    assert plan.seeds[0].entry == 0x100
    assert plan.seeds[0].fragments[0].entry == 0x104
    assert plan.joins == ((0x100, 0x104),)
    assert len(plan.digest) == 64
    assert plan.manifest == {"schema_version": 1, "inputs": plan.inputs}
    assert {str(repo.GHIDRA_SCRIPTS / name) for name in prep.SCRIPTS} <= plan.inputs.keys()
    assert not (root / repo.STATE).exists()


def test_unconfigured_layout_has_no_new_preparation_requirement(prepared_root):
    root, _ = prepared_root
    (root / prep.SEEDS / "t1.toml").unlink()
    assert prep.plan("t1", root) is None
    assert prep.session(None, "wire", "receipt", ["existing"], []) == ["existing"]


@pytest.mark.parametrize("before,after,match", [
    ('schema_version = 1', 'schema_version = 2', 'schema'),
    ('layout = "t1"', 'layout = "other"', 'another layout'),
    ('image = "T1"', 'image = "other"', 'another layout'),
    ('entry = "00000100"', 'entry = "100"', 'eight lowercase'),
    ('bytes = "0009"', 'bytes = "ffff"', 'pin'),
    ('bytes = "0009"', 'bytes = "bad"', 'pin bytes'),
    ('instructions = 4', 'instructions = 0', 'positive integer'),
    ('sites = ["00000104", "00000106"]', 'sites = ["00000105"]', 'aligned'),
    ('sites = ["00000104", "00000106"]', 'sites = ["00000104", "00000104"]', 'duplicate'),
    ('type = "write"', 'type = "data"', 'reference type'),
    ('site = "00000104"', 'site = "00000108"', 'seed/site owner'),
])
def test_registry_refuses_unreviewed_or_invalid_inputs(prepared_root, before, after, match):
    root, _ = prepared_root
    path = root / prep.SEEDS / "t1.toml"
    path.write_text(path.read_text().replace(before, after))
    with pytest.raises(KbError, match=match):
        prep.plan("t1", root)


def test_current_stock_image_must_match_the_catalog(prepared_root):
    root, image = prepared_root
    (root / "rom-images/T1/T1.bin").write_bytes(b"\xff" + image[1:])
    with pytest.raises(KbError, match="registered image bytes"):
        prep.plan("t1", root)


def test_seed_requires_pointer_prologue_and_matching_fragment_join(prepared_root):
    root, _ = prepared_root
    registry = root / prep.SEEDS / "t1.toml"
    original = registry.read_text()
    registry.write_text(original.replace('address = "00000100"', 'address = "00000102"'))
    with pytest.raises(KbError, match="prologue"):
        prep.plan("t1", root)
    registry.write_text(original.replace('bytes = "00000100"', 'bytes = "0000"'))
    with pytest.raises(KbError, match="entry-pointer"):
        prep.plan("t1", root)
    registry.write_text(original)
    (root / prep.MERGES / "t1.csv").write_text("entry,fragment,note\n")
    with pytest.raises(KbError, match="reviewed join"):
        prep.plan("t1", root)


def test_foreign_registry_is_not_silently_ignored(prepared_root):
    root, _ = prepared_root
    (root / prep.SEEDS / "other.toml").write_text("schema_version = 1\n")
    with pytest.raises(KbError, match="unknown layout"):
        prep.inputs(root)


def test_changed_primary_input_changes_the_direct_cache_binding(prepared_root):
    root, _ = prepared_root
    plan = prep.plan("t1", root)
    path = root / repo.GHIDRA_SCRIPTS / "RecoverFuncs.java"
    path.write_text("changed strict recovery\n")
    after = prep.plan("t1", root)
    assert after.digest != plan.digest
    assert after.inputs[str(path.relative_to(root))] != plan.inputs[str(path.relative_to(root))]


def test_session_plan_prepares_before_outputs_and_seals_after_them(prepared_root, tmp_path):
    root, _ = prepared_root
    plan = prep.plan("t1", root)
    wire, receipt = tmp_path / "plan.tsv", tmp_path / "receipt.json"
    prep.write_plan(plan, wire, root)
    text = wire.read_text()
    assert "seed\t00000100\t8\t4\t1" in text
    assert "fragment\t00000100\t00000104\t2" in text
    assert "join\t00000100\t00000104" in text
    assert "forbidden\t00000110" in text
    middle = ["-postScript", "ExportGraph.java", str(tmp_path)]
    result = prep.session(plan, wire, receipt, middle, ["funcs.csv", "calls.csv"])
    assert result[:3] == ["-postScript", "PrepareProgram.java", "prepare"]
    start = result.index("ExportGraph.java")
    seal = result.index("seal")
    assert start < seal
    assert result[5:7] == ["funcs.csv", "calls.csv"]
    assert result[-2:] == ["funcs.csv", "calls.csv"]


def receipt_of(plan, outputs):
    return {"schema_version": 1, "layout": plan.layout, "digest": plan.digest,
            "image_sha256": plan.image_sha256, "current_sha256": plan.image_sha256,
            "preserved": True, "complete": True,
            "outputs": {str(path.name): hashlib.sha256(path.read_bytes()).hexdigest()
                        for path in outputs}}


def test_receipt_refuses_successful_process_without_semantic_completion(prepared_root, tmp_path):
    root, _ = prepared_root
    plan = prep.plan("t1", root)
    receipt = tmp_path / "receipt.json"
    output = tmp_path / "funcs.csv"
    output.write_text("addr\n00000100\n")
    with pytest.raises(KbError, match="missing"):
        prep.verify_receipt(plan, receipt, [output.name])
    data = receipt_of(plan, [output])
    for key, wrong in (("complete", False), ("preserved", False), ("digest", "0" * 64),
                       ("image_sha256", "0" * 64), ("current_sha256", "0" * 64),
                       ("layout", "other")):
        receipt.write_text(json.dumps({**data, key: wrong}))
        with pytest.raises(KbError, match="stale or unsuccessful"):
            prep.verify_receipt(plan, receipt, [output.name])
    receipt.write_text(json.dumps(data))
    assert prep.verify_receipt(plan, receipt, [output.name]) == data
    output.write_text("changed\n")
    with pytest.raises(KbError, match="missing or changed"):
        prep.verify_receipt(plan, receipt, [output.name])


def test_receipt_does_not_accept_partial_output_sets(prepared_root, tmp_path):
    root, _ = prepared_root
    plan = prep.plan("t1", root)
    output = tmp_path / "funcs.csv"
    output.write_text("a\n")
    receipt = tmp_path / "receipt.json"
    receipt.write_text(json.dumps(receipt_of(plan, [output])))
    with pytest.raises(KbError, match="another output set"):
        prep.verify_receipt(plan, receipt, [output.name, "calls.csv"])


def test_directory_promotion_preserves_accepted_outputs_on_failure(tmp_path):
    source, target = tmp_path / "source", tmp_path / "accepted"
    source.mkdir()
    target.mkdir()
    (source / "value").write_text("prepared")
    (target / "value").write_text("accepted")
    original = Path.rename
    def rename(path, destination):
        if path.name == "replacement":
            raise OSError("injected replacement failure")
        return original(path, destination)
    with patch.object(Path, "rename", rename), pytest.raises(OSError, match="replacement failure"):
        prep.promote_directory(source, target)
    assert (target / "value").read_text() == "accepted"
    assert (source / "value").read_text() == "prepared"


def test_directory_promotion_copies_before_touching_accepted_target(tmp_path):
    source, target = tmp_path / "source", tmp_path / "accepted"
    source.mkdir()
    target.mkdir()
    (target / "value").write_text("accepted")
    with patch.object(prep.shutil, "copytree", side_effect=OSError("copy failure")):
        with pytest.raises(OSError, match="copy failure"):
            prep.promote_directory(source, target)
    assert (target / "value").read_text() == "accepted"


def test_directory_promotion_accepts_a_complete_verified_replacement(tmp_path):
    source, target = tmp_path / "source", tmp_path / "accepted"
    source.mkdir()
    target.mkdir()
    (source / "value").write_text("prepared")
    (target / "obsolete").write_text("accepted")
    prep.promote_directory(source, target)
    assert (target / "value").read_text() == "prepared"
    assert not (target / "obsolete").exists()


def test_prepared_export_requires_body_sites_references_and_entry_limits(prepared_root, tmp_path):
    root, _ = prepared_root
    plan = prep.plan("t1", root)
    output = tmp_path / "export"
    output.mkdir()
    seed = plan.seeds[0]
    (output / "funcs.csv").write_text("addr\n00000100\n")
    (output / "function_signatures.csv").write_text(
        "addr,size,instructions,exact_sha256\n"
        f"00000100,8,4,{seed.instruction_sha256}\n")
    (output / "function_tokens.csv").write_text(
        "func_addr,ins_addr\n00000100,00000100\n00000100,00000102\n"
        "00000100,00000104\n00000100,00000106\n")
    (output / "function_references.csv").write_text(
        "func_addr,ins_addr,ref_addr,ref_type\n00000100,00000104,ffff1000,write\n")
    prep.check_exports(plan, output, root)
    tokens = output / "function_tokens.csv"
    original_tokens = tokens.read_text()
    tokens.write_text(original_tokens.replace("00000100,00000102", "00000100,00000108"))
    with pytest.raises(KbError, match="instruction sites differ"):
        prep.check_exports(plan, output, root)
    tokens.write_text(original_tokens)
    (output / "funcs.csv").write_text("addr\n00000100\n00000110\n")
    with pytest.raises(KbError, match="outside-function"):
        prep.check_exports(plan, output, root)
    (output / "funcs.csv").write_text("addr\n00000100\n00000104\n")
    with pytest.raises(KbError, match="reviewed join"):
        prep.check_exports(plan, output, root)
    (output / "funcs.csv").write_text("addr\n00000100\n")
    (output / "function_references.csv").write_text("func_addr,ins_addr,ref_addr,ref_type\n")
    with pytest.raises(KbError, match="lacks write"):
        prep.check_exports(plan, output, root)


def test_primary_scripts_keep_recovery_bounded_and_check_current_bytes():
    root = Path(__file__).resolve().parents[2]
    recovery = (root / repo.GHIDRA_SCRIPTS / "RecoverFuncs.java").read_text()
    primary = (root / repo.GHIDRA_SCRIPTS / "PrepareProgram.java").read_text()
    assert 'args[0].equals("--seeds-only")' in recovery
    assert "!strict && pass <= MAX_PASS" in recovery
    assert "strict && displaced != null" in recovery
    assert "monitor.checkCancelled()" in recovery
    assert "extends HeadlessScript" in primary
    assert "ABORT_AND_DELETE" not in primary
    assert primary.index("preflight();") < primary.index("clearStageOutputs(receipt,")
    assert primary.index("clearStageOutputs(receipt,") < primary.index("prepare(receipt);")
    assert 'recover[0] = "--seeds-only"' in primary
    assert "getExecutableSHA256()" in primary
    assert "current program memory differs" in primary
    assert "owner.references.containsAll(old.references)" in primary
    assert "if (borrowedFrame) required.removeAll(old.stackReferences);" in primary
    assert "ref.getToAddress().isStackAddress()" in primary
    assert "!lostRequired.isEmpty()" in primary
    assert 'kept.add("removed_abstract_stack", removed)' in primary
    assert 'kept.add("added_abstract_stack", added)' in primary
    assert 'result.add("preservation", preservation)' in primary
    assert "ins.getFlowOverride()" in primary
    assert "preparation changes another function" in primary
    assert 'result.addProperty("complete", true)' in primary
    documentation = (root / repo.GHIDRA_SCRIPTS / "README.md").read_text()
    decompile = (root / repo.GHIDRA_SCRIPTS / "decompile.py").read_text()
    assert "A request under another key first removes" not in documentation
    assert "Stale code files are removed only from the staged replacement." in documentation
    assert decompile.index("preparation.verify_receipt(") < decompile.index('replacement = stage / "cache"')
    assert decompile.index("valid_output(stage / name, entry)") < decompile.index('replacement = stage / "cache"')
    assert decompile.index("path.unlink()") < decompile.index("preparation.promote_directory(replacement, target)")


def test_failed_rollback_retains_the_only_accepted_directory(tmp_path):
    source, target = tmp_path / "source", tmp_path / "accepted"
    source.mkdir()
    target.mkdir()
    (source / "value").write_text("prepared")
    (target / "value").write_text("accepted")
    original = Path.rename
    def rename(path, destination):
        if path.name in ("replacement", "accepted") and path.parent != tmp_path:
            raise OSError("injected rename failure")
        return original(path, destination)
    with patch.object(Path, "rename", rename), pytest.raises(KbError, match="accepted outputs remain"):
        prep.promote_directory(source, target)
    backup = list(tmp_path.glob(".accepted-promote-*/accepted/value"))
    assert len(backup) == 1
    assert backup[0].read_text() == "accepted"


@pytest.mark.parametrize("key,value", [("seed", True), ("pin", "invalid"), ("reference", [])])
def test_malformed_registry_arrays_fail_with_a_data_error(prepared_root, key, value):
    root, _ = prepared_root
    path = root / prep.SEEDS / "t1.toml"
    import tomllib
    document = tomllib.loads(path.read_text())
    document[key] = value
    original = tomllib.loads
    def loads(text, *args, **kwargs):
        return document if text == path.read_text() else original(text, *args, **kwargs)
    with patch.object(prep.tomllib, "loads", side_effect=loads):
        with pytest.raises(KbError, match="array of tables"):
            prep.plan("t1", root)


def test_kept_wire_and_receipt_bind_the_full_session_contract(prepared_root, tmp_path):
    root, _ = prepared_root
    plan = prep.plan("t1", root)
    wire, receipt = tmp_path / "wire.tsv", tmp_path / "receipt.json"
    output = tmp_path / "funcs.csv"
    output.write_text("addr\n00000100\n")
    prep.write_plan(plan, wire, root)
    document = {**receipt_of(plan, [output]), "wire_sha256": repo.sha256_file(wire)}
    receipt.write_text(json.dumps(document))
    prep.verify_receipt(plan, receipt, [output.name], wire=wire, root=root)
    wire.write_text(wire.read_text().replace("site\t00000100\t00000104", "site\t00000100\t00000108"))
    receipt.write_text(json.dumps({**document, "wire_sha256": repo.sha256_file(wire)}))
    with pytest.raises(KbError, match="contract is stale or changed"):
        prep.verify_receipt(plan, receipt, [output.name], wire=wire, root=root)


def test_previous_session_receipt_cannot_seal_another_run(prepared_root, tmp_path):
    root, _ = prepared_root
    plan = prep.plan("t1", root)
    wire, receipt = tmp_path / "wire.tsv", tmp_path / "receipt.json"
    output = tmp_path / "funcs.csv"
    output.write_text("addr\n00000100\n")
    prep.write_plan(plan, wire, root)
    receipt.write_text(json.dumps({**receipt_of(plan, [output]), "wire_sha256": repo.sha256_file(wire)}))
    prep.write_plan(plan, wire, root)
    with pytest.raises(KbError, match="another session"):
        prep.verify_receipt(plan, receipt, [output.name], wire=wire, root=root)


@pytest.mark.parametrize("text", ["[]", "null", "true", '"receipt"'])
def test_nonobject_receipt_is_a_data_refusal(prepared_root, tmp_path, text):
    root, _ = prepared_root
    receipt = tmp_path / "receipt.json"
    receipt.write_text(text)
    with pytest.raises(KbError, match="not an object"):
        prep.verify_receipt(prep.plan("t1", root), receipt, ["funcs.csv"])


def test_promotion_failure_without_old_output_does_not_create_a_partial_target(tmp_path):
    source, target = tmp_path / "source", tmp_path / "new-output"
    source.mkdir()
    (source / "value").write_text("prepared")
    original = Path.rename
    def rename(path, destination):
        if path.name == "replacement":
            raise OSError("injected rename failure")
        return original(path, destination)
    with patch.object(Path, "rename", rename), pytest.raises(OSError, match="rename failure"):
        prep.promote_directory(source, target)
    assert not target.exists()
    assert (source / "value").read_text() == "prepared"


def test_raw_stage_requires_an_independent_receipt_for_every_session(prepared_root, tmp_path):
    root, _ = prepared_root
    plan = prep.plan("t1", root)
    groups = [("funcs.csv", "calls.csv"), ("accessors.100.csv",), ("accessors.104.csv",)]
    for number, outputs in enumerate(groups, 1):
        files = [tmp_path / name for name in outputs]
        for path in files:
            path.write_text("sealed output\n")
        wire, receipt = (tmp_path / f"preparation-{number}.tsv",
                         tmp_path / f"preparation-{number}.json")
        prep.write_plan(plan, wire, root)
        receipt.write_text(json.dumps({**receipt_of(plan, files),
                                      "wire_sha256": repo.sha256_file(wire)}))
    prep.verify_stage(plan, tmp_path, groups, root)
    (tmp_path / "preparation-3.json").unlink()
    with pytest.raises(KbError, match="receipt is missing"):
        prep.verify_stage(plan, tmp_path, groups, root)


def test_raw_stage_cannot_bind_changed_builder_to_retained_outputs(prepared_root, tmp_path):
    root, _ = prepared_root
    plan = prep.plan("t1", root)
    output = tmp_path / "funcs.csv"
    output.write_text("sealed output\n")
    wire, receipt = tmp_path / "preparation-1.tsv", tmp_path / "preparation-1.json"
    prep.write_plan(plan, wire, root)
    receipt.write_text(json.dumps({**receipt_of(plan, [output]),
                                  "wire_sha256": repo.sha256_file(wire)}))
    builder = root / "tools/ghidra/decompile.py"
    builder.write_text("changed primary builder\n")
    with pytest.raises(KbError, match="stale or unsuccessful"):
        prep.verify_stage(prep.plan("t1", root), tmp_path, [(output.name,)], root)
