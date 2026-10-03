"""Input binding of the actual primary output producers, independent of stages."""

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
    assert repo.CONFIG.as_posix() in plan.inputs
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


@pytest.mark.parametrize("path", [repo.CONFIG.as_posix(), CENSUS])
def test_plan_digest_follows_configuration_and_the_selected_census_registry(execution_root, path):
    before = prep.plan("t1", execution_root)
    target = execution_root / path
    target.write_text(target.read_text() + "# changed input\n")
    assert prep.plan("t1", execution_root).digest != before.digest


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
