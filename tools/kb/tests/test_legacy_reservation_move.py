"""Fail-closed contracts of a primary legacy reservation-only move."""
from __future__ import annotations

from contextlib import nullcontext, redirect_stdout
import io
from types import SimpleNamespace
from unittest import mock

import pytest

from kb import cli, compile, legacy_reservation as writer, names, refs, repo, store
from kb.model import Builder, Meaning, Symbol, SymbolKey
from kb.repo import KbError
from tools.kb.tests.test_refs import Store, sym

OLD, NEW = 0x29588, 0x28EA2
SOURCE = "pastel-yak/fn/7mfk-00029588"
TARGET = "7mfk:00028ea2"
OLD_KEY, NEW_KEY = SymbolKey("7mfk", "fn", OLD), SymbolKey("7mfk", "fn", NEW)
ROW = names.Row("7mfk", "fn", OLD, "pastel-yak", ("former-heron",))


def model(rows=(ROW,), named=False):
    item = Symbol(NEW_KEY, {"level": "code"},
                  [{"kind": "l0", "supports": "identity", "at": TARGET}],
                  {"defs/JK08A.funcs.csv"}, implicit=False)
    meaning = Meaning("fn", props={"level": "code"}, symbols={"7mfk": item},
                      sources={"defs/JK08A.funcs.csv", "defs/JK08A.architecture.toml"})
    item.meaning = meaning
    if named:
        meaning.name, item.name, item.generated, item.former = "pastel-yak", "pastel-yak", "pastel-yak", ROW.former
    return SimpleNamespace(names=list(rows), symbols={NEW_KEY: item}, file_names={},
                           overlay={}, meanings=[meaning])


def test_dependency_only_function_is_not_a_corrected_legacy_owner():
    layout = repo.layout("7mfk")
    builder = Builder({"7mfk": layout}, compile.spaces(repo.config()),
                      {"7mfk": frozenset({NEW})}, {"7mfk": (0x8200, 0x20000)})
    key = builder.resolve("7mfk", NEW, ("fn",), "defs/JK08A.vars.csv")
    base = builder.finish()
    base.names = [ROW]
    assert key == NEW_KEY and OLD_KEY not in base.symbols
    assert base.symbols[key].implicit
    assert base.symbols[key].sources == {"defs/JK08A.vars.csv"}
    with mock.patch.object(writer, "reviewed_join") as joined, \
            mock.patch.object(writer.compile, "build") as built:
        with pytest.raises(KbError, match="corrected legacy owners") as failure:
            writer.plan_move(SOURCE, TARGET, base)
    assert failure.value.code == 3
    joined.assert_not_called()
    built.assert_not_called()


def planned(base=None):
    base = base or model()
    result = model((names.Row("7mfk", "fn", NEW, ROW.name, ROW.former),), True)
    with mock.patch.object(writer, "reviewed_join") as joined, \
            mock.patch.object(writer.compile, "build", return_value=result) as built, \
            mock.patch.object(writer.write, "refusals", return_value=[]):
        change, texts, actual = writer.plan_move(SOURCE, TARGET, base)
    return base, result, change, texts, actual, joined, built


def test_only_one_row_key_moves_without_adopting_or_drawing_a_name():
    base, result, change, texts, actual, joined, built = planned()
    assert set(texts) == {names.PATH}
    assert names.parse(texts[names.PATH]) == [names.Row("7mfk", "fn", NEW, ROW.name, ROW.former)]
    assert actual is result and base.names == [ROW]
    assert len(result.names) == len(base.names)
    assert "pastel-yak" in change.diff() and "00029588" in change.diff() and "00028ea2" in change.diff()
    assert joined.call_args.args[1:3] == (OLD, NEW)
    assert built.call_args.args[1] == {names.PATH: texts[names.PATH]}
    node = sym(ROW.name, "fn", NEW, former=ROW.former)
    resolved = refs.resolve(Store([node]), SOURCE)
    assert resolved.address == NEW and "stale reference" in resolved.note


@pytest.mark.parametrize("source,target,code", (
    ("pastel-yak/fn", TARGET, 2),
    ("pastel-yak/ram/7mfk-00029588", TARGET, 2),
    (SOURCE, "pastel-yak/fn", 2),
    (SOURCE, "1nd:00028ea2", 2),
    (SOURCE, "7mfk:00029588", 2),
    ("different-heron/fn/7mfk-00029588", TARGET, 3),
))
def test_bad_reference_and_cross_layout_moves_fail_before_writes(source, target, code):
    with mock.patch.object(writer, "reviewed_join") as joined, \
            mock.patch.object(writer.compile, "build") as built:
        with pytest.raises(KbError) as failure:
            writer.plan_move(source, target, model())
    assert failure.value.code == code
    joined.assert_not_called()
    built.assert_not_called()


@pytest.mark.parametrize("mutation", ("destination-reserved", "old-still-owned", "no-destination",
                                       "semantic-destination", "file-destination", "duplicate-old"))
def test_occupied_or_unmigrated_owners_are_refused(mutation):
    base = model()
    if mutation == "destination-reserved":
        base.names.append(names.Row("7mfk", "fn", NEW, "other-heron"))
    elif mutation == "old-still-owned":
        base.symbols[OLD_KEY] = Symbol(OLD_KEY)
    elif mutation == "no-destination":
        base.symbols.clear()
    elif mutation == "semantic-destination":
        base.symbols[NEW_KEY].meaning.semantic = True
    elif mutation == "file-destination":
        base.file_names[NEW_KEY] = ("pastel-yak", (), store.path_of("fn", "pastel-yak"))
    else:
        base.names.append(ROW)
    with mock.patch.object(writer, "reviewed_join") as joined:
        with pytest.raises(KbError) as failure:
            writer.plan_move(SOURCE, TARGET, base)
    assert failure.value.code == 3
    joined.assert_not_called()


@pytest.mark.parametrize("mutation", ("name", "former", "old-remains", "props", "evidence",
                                       "sources", "meaning-props", "meaning-tables", "issues"))
def test_compiled_identity_and_owner_facts_must_survive(mutation):
    base = model()
    result = model((names.Row("7mfk", "fn", NEW, ROW.name, ROW.former),), True)
    item = result.symbols[NEW_KEY]
    if mutation == "name":
        item.meaning.name = "other-heron"
    elif mutation == "former":
        item.former = ()
    elif mutation == "old-remains":
        result.symbols[OLD_KEY] = Symbol(OLD_KEY)
    elif mutation == "props":
        item.props["level"] = "pattern"
    elif mutation == "evidence":
        item.evidence.clear()
    elif mutation == "sources":
        item.sources.clear()
    elif mutation == "meaning-props":
        item.meaning.props["level"] = "pattern"
    elif mutation == "meaning-tables":
        item.meaning.tables["unexpected"] = {"level": "pattern"}
    issues = [SimpleNamespace(check="names", subject="unexpected", message="missing")] if mutation == "issues" else []
    with mock.patch.object(writer, "reviewed_join"), \
            mock.patch.object(writer.compile, "build", return_value=result), \
            mock.patch.object(writer.write, "refusals", return_value=issues):
        with pytest.raises(KbError) as failure:
            writer.plan_move(SOURCE, TARGET, base)
    assert failure.value.code == 3
    assert base.names == [ROW]


@pytest.mark.parametrize("dry_run", (False, True))
def test_primary_apply_locks_and_plans_before_any_graph_enrollment(dry_run):
    events = []
    base = model()
    planned_change, texts, result = SimpleNamespace(lines=[]), {names.PATH: "fixture\n"}, model(named=True)
    with mock.patch.object(writer.lock, "held", side_effect=lambda root: nullcontext()) as held, \
            mock.patch.object(writer.compile, "build", side_effect=lambda root: events.append("compile") or base), \
            mock.patch.object(writer, "plan_move", side_effect=lambda *args: events.append("plan") or (planned_change, texts, result)), \
            mock.patch.object(writer.store, "write", side_effect=lambda *args: events.append("write")), \
            mock.patch.object(writer.graph, "fresh") as fresh, \
            mock.patch.object(writer.graph, "sync_held", side_effect=lambda *args: events.append("sync")), \
            mock.patch.object(writer.compile.cached, "cache_clear"):
        assert writer.apply(SOURCE, TARGET, dry_run=dry_run) == (planned_change, texts)
    held.assert_called_once()
    fresh.assert_not_called()
    assert events == (["compile", "plan"] if dry_run else ["compile", "plan", "write", "sync"])


def test_cli_exposes_the_primary_mode_and_rejects_generic_move_arguments():
    change = SimpleNamespace(lines=["move legacy reservation"], diff=lambda texts: "diff\n")
    with mock.patch.object(writer, "apply", return_value=(change, {names.PATH: "fixture\n"})) as apply, \
            redirect_stdout(io.StringIO()) as out:
        assert cli.main(["move", SOURCE, TARGET, "--legacy-reservation", "--dry-run"]) == 0
    assert apply.call_args.kwargs["dry_run"] is True and "diff" in out.getvalue()
    with mock.patch.object(writer, "apply") as apply, mock.patch("sys.stderr", new_callable=io.StringIO):
        assert cli.main(["move", SOURCE, TARGET, "--legacy-reservation", "--level", "code"]) == 2
    apply.assert_not_called()
