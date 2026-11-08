"""Input binding of the actual primary output producers, independent of stages."""

import json
from pathlib import Path

import pytest

from kb import ghidra_preparation as prep, repo
from kb.repo import KbError
from tools.tests.test_ghidra_preparation import prepared_root

OUTPUTS = (
    "ProgramSha256.java", "ExportGraph.java", "ExportXrefs.java",
    "ExportFunctionSignatures.java", "ExportFunctionTokens.java", "ResolveAccessors.java",
    "DecompileFuncs.java", "DumpFuncListing.java",
)
CENSUS = "tools/ghidra/census-input.csv"
OTHER_CENSUS = "tools/ghidra/other-census-input.csv"


@pytest.fixture
def execution_root(prepared_root):
    root, _ = prepared_root
    (root / repo.CONFIG).parent.mkdir(parents=True, exist_ok=True)
    (root / repo.CONFIG).write_text(
        '[l0]\nscripts = ["ExportGraph.java"]\n'
        '[l0.census.t1]\ninterp = "' + CENSUS + '"\n'
        '[l0.census.other]\ninterp = "' + OTHER_CENSUS + '"\n')
    for name in OUTPUTS:
        (root / repo.GHIDRA_SCRIPTS / name).write_text("primary producer " + name + "\n")
    (root / CENSUS).write_text("family,kernel,wrapper\nexplicit,00000100,00000100\n")
    (root / OTHER_CENSUS).write_text("unselected registry\n")
    return root


def test_actual_output_producers_are_bound_even_when_the_declared_list_omits_them(execution_root):
    plan = prep.plan("t1", execution_root)
    wanted = {(repo.GHIDRA_SCRIPTS / name).as_posix() for name in OUTPUTS}
    assert wanted <= plan.inputs.keys()
    assert prep.CONFIG_INPUT in plan.inputs
    assert repo.CONFIG.as_posix() not in plan.inputs
    assert repo.CONFIG.as_posix() in prep.inputs(execution_root)
    assert CENSUS in plan.inputs
    assert OTHER_CENSUS not in plan.inputs


@pytest.mark.parametrize("name", OUTPUTS)
def test_plan_digest_follows_each_executed_output_producer(execution_root, name):
    before = prep.plan("t1", execution_root)
    path = execution_root / repo.GHIDRA_SCRIPTS / name
    path.write_text(path.read_text() + "changed output producer\n")
    after = prep.plan("t1", execution_root)
    assert after.digest != before.digest
    assert after.inputs[path.relative_to(execution_root).as_posix()] != before.inputs[
        path.relative_to(execution_root).as_posix()]


def test_plan_digest_follows_the_selected_census_registry(execution_root):
    before = prep.plan("t1", execution_root)
    target = execution_root / CENSUS
    target.write_text(target.read_text() + "# changed input\n")
    assert prep.plan("t1", execution_root).digest != before.digest


@pytest.mark.parametrize("extra", [
    '\n[guard]\ngit = ["show"]\n',
    '\n[budget]\nbrief = 100\n',
    '\n# configuration formatting\n',
])
def test_nonexport_settings_preserve_the_plan_and_kept_session(execution_root, tmp_path, extra):
    before = prep.plan("t1", execution_root)
    wire = tmp_path / 'plan.tsv'
    prep.write_plan(before, wire, execution_root)
    config = execution_root / repo.CONFIG
    config.write_text(config.read_text() + extra)
    after = prep.plan("t1", execution_root)
    assert after.inputs == before.inputs
    assert after.digest == before.digest
    prep.verify_wire(after, wire, execution_root)


def test_l0_configuration_changes_the_plan_and_refuses_a_kept_session(execution_root, tmp_path):
    before = prep.plan("t1", execution_root)
    wire = tmp_path / 'plan.tsv'
    prep.write_plan(before, wire, execution_root)
    config = execution_root / repo.CONFIG
    config.write_text(config.read_text().replace(
        '[l0.census.t1]', '[l0.census.t1]\ncopy_helpers = ["00000104"]'))
    after = prep.plan("t1", execution_root)
    assert after.inputs[prep.CONFIG_INPUT] != before.inputs[prep.CONFIG_INPUT]
    assert after.digest != before.digest
    with pytest.raises(KbError):
        prep.verify_wire(after, wire, execution_root)
    with pytest.raises(KbError):
        prep.write_plan(before, tmp_path / 'stale.tsv', execution_root)


def config_snapshot(wire):
    rows = [line.split('\t') for line in wire.read_text().splitlines()]
    [row] = [row for row in rows if row[0] == 'input' and row[1] == prep.CONFIG_INPUT]
    return row, Path(row[3])


def test_session_binds_a_checked_snapshot_of_only_the_export_configuration(execution_root, tmp_path):
    plan = prep.plan("t1", execution_root)
    wire = tmp_path / 'plan.tsv'
    prep.write_plan(plan, wire, execution_root)
    row, snapshot = config_snapshot(wire)
    assert snapshot != execution_root / repo.CONFIG
    assert json.loads(snapshot.read_text()) == repo.config(execution_root)['l0']
    assert repo.sha256_file(snapshot) == row[2] == plan.inputs[prep.CONFIG_INPUT]
    prep.verify_wire(plan, wire, execution_root)


@pytest.mark.parametrize('changed', ('missing', 'modified'))
def test_kept_session_refuses_a_missing_or_modified_configuration_snapshot(
        execution_root, tmp_path, changed):
    plan = prep.plan("t1", execution_root)
    wire = tmp_path / 'plan.tsv'
    prep.write_plan(plan, wire, execution_root)
    _, snapshot = config_snapshot(wire)
    if changed == 'missing':
        snapshot.unlink()
    else:
        snapshot.write_text('{}\n')
    with pytest.raises(KbError):
        prep.verify_wire(plan, wire, execution_root)


def test_a_different_layout_census_registry_is_not_a_preparation_input(execution_root):
    before = prep.plan("t1", execution_root)
    (execution_root / OTHER_CENSUS).write_text("changed unselected registry\n")
    assert prep.plan("t1", execution_root).digest == before.digest


def test_additional_declared_producer_is_bound(execution_root):
    path = execution_root / repo.GHIDRA_SCRIPTS / "AdditionalOutput.java"
    path.write_text("declared primary output\n")
    config = execution_root / repo.CONFIG
    config.write_text(config.read_text().replace(
        'scripts = ["ExportGraph.java"]',
        'scripts = ["ExportGraph.java", "AdditionalOutput.java"]'))
    plan = prep.plan("t1", execution_root)
    assert path.relative_to(execution_root).as_posix() in plan.inputs
    path.write_text("changed declared primary output\n")
    assert prep.plan("t1", execution_root).digest != plan.digest


@pytest.mark.parametrize("before,after", [
    ('[l0.census.t1]', '[l0.census.absent]'),
    ('interp = "' + CENSUS + '"', 'interp = "/tmp/foreign.csv"'),
    ('interp = "' + CENSUS + '"', 'interp = "../foreign.csv"'),
    ('scripts = ["ExportGraph.java"]', 'scripts = ["../Foreign.java"]'),
])
def test_plan_refuses_unbound_or_outside_execution_inputs(execution_root, before, after):
    config = execution_root / repo.CONFIG
    config.write_text(config.read_text().replace(before, after))
    with pytest.raises(KbError):
        prep.plan("t1", execution_root)


def test_a_proposed_registry_binds_the_bytes_that_the_change_writes(execution_root, tmp_path):
    tracked = prep.plan("t1", execution_root)
    proposed = tmp_path / "proposed.interp.csv"
    proposed.write_text("family,kernel,wrapper\nexplicit,00000100,00000100\n"
                        "implicit,00000200,00000200\n")
    plan = prep.plan("t1", execution_root, proposed)
    assert plan.inputs[CENSUS] == repo.sha256_file(proposed) != tracked.inputs[CENSUS]
    assert ({path: digest for path, digest in plan.inputs.items() if path != CENSUS}
            == {path: digest for path, digest in tracked.inputs.items() if path != CENSUS})
    wire = tmp_path / "plan.tsv"
    prep.write_plan(plan, wire, execution_root)
    [row] = [line.split("\t") for line in wire.read_text().splitlines()
             if line.startswith(f"input\t{CENSUS}\t")]
    assert row[2:] == [plan.inputs[CENSUS], str(proposed.resolve())]
    prep.verify_wire(plan, wire, execution_root)
    with pytest.raises(KbError):
        prep.verify_wire(tracked, wire, execution_root)
    # The registry that the change writes holds the sealed bytes.
    (execution_root / CENSUS).write_bytes(proposed.read_bytes())
    assert prep.plan("t1", execution_root).manifest == plan.manifest
