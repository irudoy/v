"""A planning group shares compilation, never conversion decisions."""

from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace

import pytest

from kb import adapters, checks, compile, convert, fingerprint, lock, write
from kb.model import Model
from kb.repo import KbError


@pytest.fixture
def group(tmp_path, monkeypatch):
    source = tmp_path / "input.txt"
    source.write_text("accepted source", encoding="utf-8")
    registries = tuple(SimpleNamespace(__name__=f"kb.adapters.registry_{i}")
                       for i in range(9))
    core = SimpleNamespace(__name__="kb.adapters.core")
    monkeypatch.setattr(adapters, "CONVERTED", registries)
    monkeypatch.setattr(adapters, "ORDER", (core, *registries))
    monkeypatch.setattr(adapters, "ADAPTERS", (core,))
    monkeypatch.setattr(lock, "held", lambda root: nullcontext())
    monkeypatch.setattr(fingerprint, "compute", lambda root: (Path(root).resolve(),
                                                            source.read_bytes()))
    built, checked, projected, converted = [], [], [], []

    def build(root, overlay=None, order=None):
        model = Model({}, {}, {}, {}, [])
        model.root, model.overlay = root, dict(overlay or {})
        model.stash["adapter_order"] = tuple(item.__name__ for item in
                                            (adapters.ADAPTERS if order is None else order))
        built.append((model, order))
        return model

    def check(model):
        checked.append(model)
        if model.overlay.get(Path("reject.txt")):
            yield SimpleNamespace(check="controlled", subject="overlay", message="rejected")

    class Conversion:
        def __init__(self, adapter, before, root):
            self.adapter, self.before = adapter, before

        def run(self):
            converted.append(self.adapter.__name__)
            return {}

        def expected(self):
            return convert.dump(self.before)

    def projections(adapter, model):
        projected.append(adapter.__name__)
        return {}

    monkeypatch.setattr(compile, "build", build)
    monkeypatch.setattr(checks, "CHECKS", {"controlled": check})
    monkeypatch.setattr(checks, "audit", lambda model, sections: {})
    monkeypatch.setattr(convert, "Conversion", Conversion)
    monkeypatch.setattr(convert, "projections", projections)
    return SimpleNamespace(root=tmp_path, source=source, built=built, checked=checked,
                           converted=converted, projected=projected, core=core)


def test_nine_decisions_keep_distinct_before_models_and_one_checked_native_result(group):
    with convert.planning(group.root):
        results = [convert.plan(f"registry_{i}", group.root) for i in range(9)]
    assert len(group.built) == 10
    assert len({id(conversion.before) for conversion, _, _ in results}) == 9
    assert len({id(result) for _, _, result in results}) == 1
    assert len(group.checked) == 10
    assert group.converted == group.projected == [f"kb.adapters.registry_{i}" for i in range(9)]
    assert all(texts == {} for _, texts, _ in results)
    for i, (conversion, _, _) in enumerate(results):
        assert conversion.before.stash["adapter_order"] == ("kb.adapters.core",
                                                            f"kb.adapters.registry_{i}")
    convert.plan("registry_0", group.root)
    assert len(group.built) == 12
    assert len(group.checked) == 12


def test_an_overlay_gets_an_independent_model_and_original_refusals(group):
    with convert.planning(group.root):
        _, _, native = convert.plan("registry_0", group.root)
        overlay = {Path("reject.txt"): "new issue"}
        changed = convert._result(group.root, overlay)
        assert changed is not native
        assert changed.overlay == overlay
        refused = write.refusals(native, changed)
        assert [(issue.check, issue.subject, issue.message) for issue in refused] == [
            ("controlled", "overlay", "rejected")]
    assert len(group.built) == 3


def test_changed_sources_cannot_reuse_a_native_result(group):
    with pytest.raises(KbError, match="planning inputs change"):
        with convert.planning(group.root):
            convert.plan("registry_0", group.root)
            group.source.write_text("changed source", encoding="utf-8")
            convert.plan("registry_1", group.root)
    assert len(group.built) == 2
    with convert.planning(group.root):
        convert.plan("registry_1", group.root)
    assert len(group.built) == 4


def test_mutating_a_returned_model_refuses_the_group(group):
    with pytest.raises(KbError, match="shared conversion result changes"):
        with convert.planning(group.root):
            _, _, result = convert.plan("registry_0", group.root)
            result.stash["changed"] = True
            convert.plan("registry_1", group.root)


def test_a_changed_default_adapter_order_refuses_reuse(group, monkeypatch):
    with pytest.raises(KbError, match="planning inputs change"):
        with convert.planning(group.root):
            convert.plan("registry_0", group.root)
            monkeypatch.setattr(adapters, "ADAPTERS", ())
            convert.plan("registry_1", group.root)


def test_another_root_does_not_share_the_native_model(group):
    with convert.planning(group.root):
        _, _, native = convert.plan("registry_0", group.root)
        other = convert._result(group.root / "other", {})
        assert other is not native
        assert other.root != native.root


def test_a_new_group_compiles_a_new_model_and_repeats_checks(group):
    models = []
    for _ in range(2):
        with convert.planning(group.root):
            models.append(convert.plan("registry_0", group.root)[2])
    assert models[0] is not models[1]
    assert len(group.built) == len(group.checked) == 4


def test_planning_groups_cannot_nest(group):
    with convert.planning(group.root):
        with pytest.raises(KbError, match="cannot nest"):
            with convert.planning(group.root):
                pass


def test_deep_cyclic_model_state_has_a_stable_complete_digest():
    model = Model({}, {}, {}, {}, [])
    cursor = model.stash
    for i in range(3000):
        cursor['next'] = {'value': i}
        cursor = cursor['next']
    cursor['cycle'] = model
    before = convert._model_digest(model)
    assert convert._model_digest(model) == before
    cursor['value'] = 'changed leaf'
    assert convert._model_digest(model) != before


def test_model_digest_binds_shared_objects_and_container_types():
    value = {'value': 1}
    model = SimpleNamespace(items=[value, value])
    before = convert._model_digest(model)
    model.items[1] = dict(value)
    assert convert._model_digest(model) != before
    before = convert._model_digest(model)
    model.items = tuple(model.items)
    assert convert._model_digest(model) != before


def test_an_unsupported_model_value_refuses_sharing():
    with pytest.raises(KbError, match='sharing does not support'):
        convert._model_digest(SimpleNamespace(callback=lambda: None))


def test_a_changed_projection_is_checked_against_the_shared_model(group, monkeypatch):
    path = group.root / 'projection.txt'
    path.write_text('generated', encoding='utf-8')
    monkeypatch.setattr(convert, 'projections', lambda adapter, model: {'projection.txt': 'generated'})
    with convert.planning(group.root):
        convert.plan('registry_0', group.root)
        path.write_text('stale projection', encoding='utf-8')
        with pytest.raises(KbError, match='projections of projection.txt differ'):
            convert.plan('registry_1', group.root)
    assert len(group.built) == 3


def test_a_shared_issue_is_compared_with_each_registrys_before_model(group, monkeypatch):
    def check(model):
        group.checked.append(model)
        if model.stash['adapter_order'] in (('kb.adapters.core',),
                                           ('kb.adapters.core', 'kb.adapters.registry_0')):
            yield SimpleNamespace(check='controlled', subject='native', message='existing issue',
                                  path='input.txt')
    monkeypatch.setattr(checks, 'CHECKS', {'controlled': check})
    with convert.planning(group.root):
        convert.plan('registry_0', group.root)
        with pytest.raises(KbError, match='conversion adds 1 issues'):
            convert.plan('registry_1', group.root)
    assert len(group.checked) == 3


class SlottedBase:
    __slots__ = ('base', '__private')

    def __init__(self):
        self.base = 'base value'
        self.__private = 'private value'


class SlottedChild(SlottedBase):
    __slots__ = ('child', 'unset', '__dict__')

    def __init__(self):
        super().__init__()
        self.child = 'child value'
        self.dictionary = 'dictionary value'


@pytest.mark.parametrize('slot', ['base', 'child', '_SlottedBase__private', 'unset'])
def test_only_mutating_a_slot_refuses_reuse_across_the_class_hierarchy(group, monkeypatch, slot):
    original_build = compile.build

    def build(*args, **kwargs):
        model = original_build(*args, **kwargs)
        model.stash['slotted'] = SlottedChild()
        return model

    monkeypatch.setattr(compile, 'build', build)
    with pytest.raises(KbError, match='shared conversion result changes'):
        with convert.planning(group.root):
            _, _, model = convert.plan('registry_0', group.root)
            value = model.stash['slotted']
            before = dict(vars(value))
            setattr(value, slot, None)
            assert vars(value) == before
            convert.plan('registry_1', group.root)
