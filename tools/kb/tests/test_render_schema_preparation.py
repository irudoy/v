"""Private renderer grammar remains tied to current declarations."""

from unittest import mock

from kb import store


def test_public_schemas_remain_separate_from_prepared_renderer_state():
    first = store.schema('ram')
    assert store.render('ram', {'title': 'first'}) == 'title = "first"\n'
    object.__setattr__(first, 'keys', (('title', store.HEX),))
    assert store.schema('ram') is not first
    assert store.render('ram', {'title': 'second'}) == 'title = "second"\n'


def test_changed_native_key_tuple_replaces_prepared_lookup(monkeypatch):
    monkeypatch.setitem(store.KIND_KEYS, 'fn', (('offset', store.HEX),))
    assert 'offset = 0x10' in store.render('fn', {'offset': 16})
    monkeypatch.setitem(store.KIND_KEYS, 'fn', (('offset', store.PLAIN),))
    assert store.render('fn', {'offset': 16}) == 'offset = 16\n'


def test_changed_plain_spec_rebuilds_prepared_common_fields(monkeypatch):
    assert store.render('ram', {'title': 16}) == 'title = 16\n'
    monkeypatch.setattr(store, 'PLAIN', store.HEX)
    assert store.render('ram', {'title': 16}) == 'title = 0x10\n'


def test_changed_inline_descriptor_keeps_classifier_evaluation_count():
    table = store.Table((('value', store.PLAIN),))
    visits = []

    def inline(self):
        visits.append(self)
        return False

    with mock.patch.object(store.Table, 'inline', property(inline)):
        assert store._partition(['value'], {'value': table}) is None
        assert [store._is_table(table) for _ in range(2)] == [True, True]
    assert visits == [table, table]


def test_mutable_grammar_rows_execute_current_schema_every_time(monkeypatch):
    keys = (['offset', store.PLAIN],)
    monkeypatch.setitem(store.KIND_KEYS, 'fn', keys)
    assert store.render('fn', {'offset': 16}) == 'offset = 16\n'
    keys[0][1] = store.HEX
    assert store.render('fn', {'offset': 16}) == 'offset = 0x10\n'


def test_changed_schema_and_table_constructor_execute_each_render():
    with mock.patch.object(store, 'schema', return_value=store.Table((('value', store.HEX),))) as schema:
        for _ in range(2):
            assert store.render('ram', {'value': 16}) == 'value = 0x10\n'
        assert schema.call_count == 2
    original = store.Table.__init__
    calls = []

    def constructor(self, *args, **kwargs):
        calls.append(self)
        original(self, *args, **kwargs)

    with mock.patch.object(store.Table, '__init__', constructor):
        for _ in range(2):
            assert store.render('ram', {'title': 'source'}) == 'title = "source"\n'
    assert len(calls) == 2


def test_changed_classifier_and_custom_inference_keep_original_calls():
    table = store.Table((('value', store.PLAIN),))
    with mock.patch.object(store, '_is_table', wraps=store._is_table) as classified:
        lines = []
        store._table(lines, (), {'value': 16}, table, None)
        assert lines == ['value = 16'] and classified.call_count == 2
    custom = object()
    with mock.patch.object(store, '_infer', return_value=custom) as inferred:
        lines = []
        store._table(lines, (), {'value': 16}, store.Table(), None)
        assert lines == ['value = 16'] and inferred.call_count == 1
