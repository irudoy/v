"""Contracts of exact-image, reviewed primary preparation and output acceptance."""

import hashlib
import json
from pathlib import Path
import tomllib
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


@pytest.fixture
def dispatch_root(prepared_root):
    root, original = prepared_root
    data = bytearray(original)
    data[0x40:0x42] = bytes.fromhex("432b")
    data[0x80:0x88] = bytes.fromhex("0000004200000090")
    image = bytes(data)
    digest = hashlib.sha256(image).hexdigest()
    old = hashlib.sha256(original).hexdigest()
    (root / "rom-images/T1/T1.bin").write_bytes(image)
    catalog = root / repo.CATALOG
    catalog.write_text(catalog.read_text().replace(old, digest))
    path = root / prep.SEEDS / "t1.toml"
    path.write_text(path.read_text().replace(old, digest) + (
        '\n[[dispatch]]\nentry = "00000040"\nsite = "00000040"\n'
        'table = "00000080"\nformer_entry = "00000080"\nformer_end = "00000094"\n'
        f'former_instruction_sha256 = "{hashlib.sha256(image[0x80:0x94]).hexdigest()}"\n'
        'targets = ["00000042", "00000090"]\n'
        'ranges = [["00000040", "00000046"], ["00000090", "00000094"]]\n'
        f'instruction_sha256 = "{hashlib.sha256(image[0x40:0x46] + image[0x90:0x94]).hexdigest()}"\n'))
    return root, image


def test_dispatch_contract_binds_exact_data_targets_and_disjoint_code(dispatch_root, tmp_path):
    root, image = dispatch_root
    plan = prep.plan("t1", root)
    [dispatch] = plan.dispatches
    assert dispatch.targets == (0x42, 0x90)
    assert dispatch.sites == {0x40, 0x42, 0x44, 0x90, 0x92}
    assert dispatch.table_end == 0x88
    assert dispatch.bytes == 10
    assert dispatch.instruction_sha256 == hashlib.sha256(image[0x40:0x46] + image[0x90:0x94]).hexdigest()
    wire = tmp_path / "dispatch.tsv"
    prep.write_plan(plan, wire, root)
    text = wire.read_text()
    assert "dispatch\t00000040\t00000040\t00000080\t00000088\t00000080\t00000094" in text
    assert "dispatch_range\t00000040\t00000090\t00000094" in text
    assert "dispatch_target\t00000040\t00000042" in text
    assert "dispatch_target\t00000040\t00000090" in text


@pytest.mark.parametrize("before,after,message", [
    ('targets = ["00000042", "00000090"]', 'targets = ["00000044", "00000090"]', 'targets differ'),
    ('targets = ["00000042", "00000090"]', 'targets = ["00000042", "00000070"]', 'lie in its code'),
    ('table = "00000080"', 'table = "00000082"', 'invalid dispatch'),
    ('former_end = "00000094"', 'former_end = "00000088"', 'invalid dispatch'),
    ('["00000040", "00000046"]', '["00000040", "00000082"]', 'overlap data'),
    ('["00000090", "00000094"]', '["00000044", "00000048"]', 'each other'),
    ('["00000090", "00000094"]', '["00000091", "00000094"]', 'overlap data'),
    ('site = "00000040"', 'site = "00000042"', 'register jump'),
])
def test_dispatch_refuses_wrong_targets_ranges_and_prior_body(dispatch_root, before, after, message):
    root, _ = dispatch_root
    path = root / prep.SEEDS / "t1.toml"
    path.write_text(path.read_text().replace(before, after))
    with pytest.raises(KbError, match=message):
        prep.plan("t1", root)


def test_dispatch_prior_body_digest_must_match_registered_image(dispatch_root):
    root, _ = dispatch_root
    path = root / prep.SEEDS / "t1.toml"
    document = tomllib.loads(path.read_text())
    old = document["dispatch"][0]["former_instruction_sha256"]
    path.write_text(path.read_text().replace(old, "0" * 64))
    with pytest.raises(KbError, match="former dispatch body"):
        prep.plan("t1", root)


def test_dispatch_instruction_digest_must_match_declared_ranges(dispatch_root):
    root, _ = dispatch_root
    path = root / prep.SEEDS / "t1.toml"
    document = tomllib.loads(path.read_text())
    old = document["dispatch"][0]["instruction_sha256"]
    path.write_text(path.read_text().replace(old, "0" * 64))
    with pytest.raises(KbError, match="dispatch code differs"):
        prep.plan("t1", root)


def dispatch_export(plan, output):
    output.mkdir()
    seed, dispatch = plan.seeds[0], plan.dispatches[0]
    (output / "funcs.csv").write_text("addr\n00000100\n00000040\n")
    (output / "function_signatures.csv").write_text(
        "addr,size,instructions,exact_sha256\n"
        f"00000100,8,4,{seed.instruction_sha256}\n"
        f"00000040,10,5,{dispatch.instruction_sha256}\n")
    (output / "function_tokens.csv").write_text("func_addr,ins_addr\n" + "".join(
        f"{owner:08x},{site:08x}\n" for owner, sites in
        ((0x100, range(0x100, 0x108, 2)), (0x40, sorted(dispatch.sites))) for site in sites))
    (output / "function_references.csv").write_text(
        "func_addr,ins_addr,ref_addr,ref_type\n00000100,00000104,ffff1000,write\n"
        "00000040,00000040,00000042,computed_jump\n"
        "00000040,00000040,00000090,computed_jump\n")


@pytest.mark.parametrize("mutation", ["false-entry", "data-instruction", "missing-flow", "overlap"])
def test_dispatch_export_rejects_executable_data_missing_flow_and_foreign_owners(
        dispatch_root, tmp_path, mutation):
    root, _ = dispatch_root
    plan = prep.plan("t1", root)
    output = tmp_path / "dispatch-export"
    dispatch_export(plan, output)
    prep.check_exports(plan, output, root)
    if mutation == "false-entry":
        path, extra = output / "funcs.csv", "00000080\n"
    elif mutation == "missing-flow":
        path = output / "function_references.csv"
        path.write_text(path.read_text().replace("00000040,00000040,00000090,computed_jump\n", ""))
        extra = ""
    else:
        path = output / "function_tokens.csv"
        extra = "00000200,00000080\n" if mutation == "data-instruction" else "00000200,00000042\n"
    path.write_text(path.read_text() + extra)
    with pytest.raises(KbError, match="dispatch"):
        prep.check_exports(plan, output, root)


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


def test_a_seed_without_fragments_joins_nothing(prepared_root):
    root, _ = prepared_root
    registry = root / prep.SEEDS / "t1.toml"
    text = registry.read_text()
    start = text.index("[[seed.fragment]]")
    registry.write_text(text[:start] + text[text.index("[[pin]]"):])
    (root / prep.MERGES / "t1.csv").write_text("entry,fragment,note\n")
    plan = prep.plan("t1", root)
    assert plan.seeds[0].fragments == ()
    assert plan.joins == ()


def callee_registry(root, image, reference):
    """The fixture registry with a callee seed at 00000108 and `reference`."""
    registry = root / prep.SEEDS / "t1.toml"
    digest = hashlib.sha256(image[0x108:0x10c]).hexdigest()
    registry.write_text(registry.read_text().replace(
        '[[pin]]\naddress = "00000020"',
        '[[seed]]\nentry = "00000108"\nsites = ["0000010a"]\n'
        'bytes = 4\ninstructions = 2\nranges = 1\n'
        f'instruction_sha256 = "{digest}"\n\n'
        '[[pin]]\naddress = "00000108"\nbytes = "0009"\n\n'
        '[[pin]]\naddress = "00000020"', 1) + reference)


def test_a_reviewed_call_of_another_seed_reaches_a_seed_entry(prepared_root):
    root, image = prepared_root
    callee_registry(root, image, '\n[[reference]]\nowner = "00000100"\nsite = "00000106"\n'
                                 'target = "00000108"\ntype = "call"\n')
    plan = prep.plan("t1", root)
    assert [seed.entry for seed in plan.seeds] == [0x100, 0x108]
    assert (0x100, 0x106, 0x108, "call") in plan.references


@pytest.mark.parametrize("reference", [
    "",
    '\n[[reference]]\nowner = "00000100"\nsite = "00000106"\n'
    'target = "00000108"\ntype = "read"\n',
    '\n[[reference]]\nowner = "00000108"\nsite = "0000010a"\n'
    'target = "00000108"\ntype = "call"\n',
], ids=["no reference", "read reference", "own call"])
def test_a_seed_without_pointer_pin_or_call_of_another_seed_is_refused(
        prepared_root, reference):
    root, image = prepared_root
    callee_registry(root, image, reference)
    with pytest.raises(KbError, match="seed 00000108 lacks an exact entry-pointer pin"):
        prep.plan("t1", root)


def test_preparation_admits_no_function_entry_outside_the_registry():
    root = Path(__file__).resolve().parents[2]
    primary = (root / repo.GHIDRA_SCRIPTS / "PrepareProgram.java").read_text()
    expected = primary.index("Set<String> expected = new HashSet<>(before.keySet());")
    assert primary.index("expected.addAll(Arrays.asList(entries));") > expected
    assert primary.index("if (!expected.equals(after.keySet())) {") > expected
    assert 'throw new IllegalStateException("preparation changes an unreviewed function entry");' \
        in primary
    assert 'throw new IllegalStateException("prepared body differs at " + row[1]);' in primary


def exact_ranges(family):
    return [tuple(int(bound, 16) for bound in item.split(":"))
            for item in family.get("exact_ranges", ())]


@pytest.mark.parametrize("path", sorted(
    (Path(__file__).resolve().parents[2] / prep.SEEDS).glob("*.toml")), ids=lambda p: p.stem)
def test_tracked_seed_registry_holds_family_bytes(path):
    """Every pin, seed entry, and cited site of a registry lies in the exact
    ranges of its family, whose member images carry the pinned bytes."""
    root = Path(__file__).resolve().parents[2]
    plan = prep.plan(path.stem, root)
    families = tomllib.loads((root / repo.HOMOLOGY).read_text())["family"]
    family = next(item for item in families.values()
                  if plan.image in item.get("layouts", {}).values())
    images = repo.images(root)
    members = [images[member].path.read_bytes() for member in family["members"]]
    if len(members) > 1:
        ranges = exact_ranges(family)
        spans = [(address, address + len(value)) for address, value in plan.pins]
        spans += [(seed.entry, seed.entry + 2) for seed in plan.seeds]
        spans += [(site, site + 2) for seed in plan.seeds for site in seed.sites]
        spans += [(site, site + 2) for _, site, _, _ in plan.references]
        outside = [f"{start:08x}" for start, end in spans
                   if not any(low <= start and end <= high for low, high in ranges)]
        assert outside == []
    for address, value in plan.pins:
        assert all(data[address:address + len(value)] == value for data in members)
