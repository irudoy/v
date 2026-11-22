"""The census of a kernel that a change adds precedes the change: the refusal
of the `census` check names the export by the batch, and the export, the
apply, and the projection then hold one registry (SPEC section 8.4)."""

import contextlib
import csv
import io
from pathlib import Path
import sys

import pytest

from kb import adapters, checks, compile, l0, project, repo, store, write
from kb import ghidra_preparation as preparation
from kb.adapters import files as file_adapter
from kb.adapters import interp
from kb.repo import KbError
from tools.kb.tests import writer_sources

LAYOUT = "1me3b"
REGISTRY = "defs/PROBE1ME3B.interp.csv"
MEANING = "rev_fuel_cut_state_machine"
KERNEL = "00020008"
BATCH = """[[op]]
cmd = "set"
ref = "rev_fuel_cut_state_machine/fn"
layout = "1me3b"
keys = {{ interp = {{ access = "implicit", kernel = "rev_fuel_cut_state_machine/fn", cols = {cols}, step = 16 }} }}
"""


def table(header, *rows):
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    return out.getvalue()


@pytest.fixture
def root(tmp_path, monkeypatch):
    """Isolated sources whose registries name the images of their layouts, so
    the 1ME3B rows plan the census of `1me3b`; the graph is the model."""
    root = tmp_path / "repo"
    writer_sources.write_sources(root)
    monkeypatch.setattr(adapters, "ADAPTERS", (file_adapter,))
    config = root / repo.CONFIG
    text = config.read_text(encoding="utf-8")
    for layout in repo.layouts(root).values():
        registry = f"defs/{layout.image}.interp.csv"
        text = text.replace(f"defs/fixture-{layout.id}.interp.csv", registry)
        (root / registry).write_text("wrapper,kernel\n", encoding="utf-8")
    config.write_text(text, encoding="utf-8")
    for name in repo.config(root)["l0"]["scripts"]:
        target = root / repo.GHIDRA_SCRIPTS / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"class {Path(name).stem} {{}}\n", encoding="utf-8")
    (root / repo.GHIDRA_PIN).write_text("GHIDRA_VERSION=12.1.2\n", encoding="utf-8")
    (root / project.PATH).write_text((repo.ROOT / project.PATH).read_text(encoding="utf-8"),
                                     encoding="utf-8")
    monkeypatch.setattr(write.lock, "held", lambda root: contextlib.nullcontext())
    monkeypatch.setattr(write.graph, "fresh",
                        lambda *args, **keys: contextlib.nullcontext("isolated"))
    monkeypatch.setattr(write, "graph_resolver",
                        lambda session, model, *args: write.model_resolver(model))
    monkeypatch.setattr(write.graph, "sync_held", lambda *args, **keys: None)
    monkeypatch.setattr(l0, "review", lambda *args: [])
    compile.cached.cache_clear()
    yield root
    compile.cached.cache_clear()


def ghidra(sessions):
    """Headless sessions that write the outputs their scripts name: the core
    exports of the 1me3b function and one census file per kernel argument."""
    image = repo.images(sessions["root"])["PROBE1ME3B"].sha256

    def run(jobs, root, workers=1, log=print):
        for _, arguments, _ in jobs:
            sessions["arguments"].append(arguments)
            script = arguments[1]
            if script == "ProgramSha256.java":
                Path(arguments[2]).write_text(image + "\n")
                stage = Path(arguments[2]).parent
                for name, columns in l0.CORE.items():
                    rows = [(KERNEL, "2", "false", "false")] if name == "funcs.csv" else []
                    (stage / name).write_text(table([column for column, _ in columns], *rows))
            else:
                stage, kernel = Path(arguments[2]), arguments[3]
                # One call of the fused kernel, which reads a ROM table.
                (stage / l0.Census.file(kernel)).write_text(table(
                    [column for column, _ in l0.ACCESSORS],
                    (kernel, kernel, "", "", "00010000", "FUN_00010000", "", "", "",
                     "00030000", "", "", "", "pool", "none", "none", "none", "agree", "")))
    return run


def maps_reader(root, model, tmp_path):
    """The census validation of the graph loader of the maps of 1me3b over the
    registry that `model` renders: the boundary of a graph refresh."""
    sys.path.insert(0, str(repo.ROOT / "tools"))
    from memgraph import load_maps
    registry = tmp_path / Path(REGISTRY).name
    registry.write_text(interp.render_registries(model)[REGISTRY], encoding="utf-8")
    load_maps.read_censuses(str(root / repo.L0 / LAYOUT),
                            load_maps.read_registry(str(registry)), str(registry))


def test_the_census_export_by_the_batch_precedes_the_change(root, tmp_path, monkeypatch):
    batch = tmp_path / "change.toml"
    batch.write_text(BATCH.format(cols=16), encoding="utf-8")
    ops = write.read_batch(batch)
    meaning = root / store.path_of("fn", MEANING)
    before = meaning.read_bytes()
    with pytest.raises(KbError) as refused:
        write.apply(ops, root, dry_run=True, log=lambda line: None)
    assert refused.value.code == 3
    assert ("lacks accessors.20008.csv; with the change in a batch file, run "
            "tools/ghidra/export-l0.sh 1me3b --batch <file>, then kb apply <file>, "
            "kb project, and make check") in str(refused.value)

    sessions = {"root": root, "arguments": []}
    monkeypatch.setattr(l0, "resolve_program", lambda image, root: ("PROBE1ME3B.bin", None))
    monkeypatch.setattr(l0, "run_sessions", ghidra(sessions))
    sources = []
    planned = preparation.plan
    monkeypatch.setattr(preparation, "plan",
                        lambda layout_id, root, registry=None, **kwargs: sources.append(registry)
                        or planned(layout_id, root, registry, **kwargs))
    stage, lines = tmp_path / "stage", []
    assert l0.export(LAYOUT, stage=stage, batch=batch, root=root, log=lines.append)
    proposed = stage / l0.PROPOSED
    # The census session of the new kernel runs; the kernel is its own wrapper.
    assert ["-postScript", "ResolveAccessors.java", str(stage), "20008", "fused"] in \
        sessions["arguments"]
    assert f"census of {batch}: 1 kernels; new: {KERNEL}" in lines
    assert sources == [proposed, proposed]
    assert (root / repo.L0 / LAYOUT / l0.Census.file(KERNEL)).is_file()
    # The export plans the batch and writes no source.
    assert meaning.read_bytes() == before
    assert (root / REGISTRY).read_text(encoding="utf-8") == "wrapper,kernel\n"
    # A stage build with the same batch reproduces the export; another
    # change does not adopt the stage.
    assert l0.export(LAYOUT, check=True, from_stage=stage, batch=batch, root=root,
                     log=lambda line: None)
    other = tmp_path / "other.toml"
    other.write_text(BATCH.format(cols=8), encoding="utf-8")
    with pytest.raises(KbError, match="the stage holds the census registry of another change"):
        l0.export(LAYOUT, check=True, from_stage=stage, batch=other, root=root,
                  log=lambda line: None)

    # The graph loader refuses the exported census beside the registry of the
    # unwritten sources, so no write plans over a graph refresh until the
    # batch is written; the second export of a shared registry plans alike.
    with pytest.raises(SystemExit, match="censuses outside the registry: accessors.20008.csv"):
        maps_reader(root, compile.build(root), tmp_path)

    def refresh(*args, **keys):
        raise AssertionError("a graph refresh before the batch is written")

    monkeypatch.setattr(write.graph, "fresh", refresh)
    assert write.pending_censuses(root) == {LAYOUT: [KERNEL]}
    assert l0.proposed(LAYOUT, batch, root, log=lambda line: None).encode() == \
        proposed.read_bytes()
    unrelated = [{"cmd": "set", "ref": f"{MEANING}/fn", "keys": {"note": ["Probe note."]}}]
    with pytest.raises(KbError, match="the L0 of 1me3b holds accessors.20008.csv, which no "
                                      "registry row of the change plans") as early:
        write.apply(unrelated, root, dry_run=True, log=lambda line: None)
    assert early.value.code == 3
    synced = []
    monkeypatch.setattr(write.graph, "sync_held",
                        lambda root, full, log, model: synced.append(model))
    _, texts = write.apply(ops, root, log=lambda line: None)
    assert store.path_of("fn", MEANING) in texts
    # The graph loads the census with the model of the written batch.
    [model] = synced
    maps_reader(root, model, tmp_path)
    assert write.pending_censuses(root) == {LAYOUT: [KERNEL]}
    compile.cached.cache_clear()
    project.write(root, ["defs/*.interp.csv"])
    assert (root / REGISTRY).read_bytes() == proposed.read_bytes()
    assert write.pending_censuses(root) == {}
    assert checks.census_check(compile.build(root)) == []
    assert l0.check_all(root, only=[LAYOUT]) == []
