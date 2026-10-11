"""Grammar programs preserve current canonical values and schema changes."""

from unittest import mock

from kb import store


def text(table, document):
    lines = []
    store._table(lines, (), document, table, None)
    return '\n'.join(lines) + '\n'


def test_repeated_shape_renders_current_values_in_schema_order():
    table = store.Table((('z', store.PLAIN), ('a', store.PLAIN)))
    document = {'a': 1, 'z': 'first'}
    assert text(table, document) == 'z = "first"\na = 1\n'
    document.update(z='second', a=2)
    assert text(table, document) == 'z = "second"\na = 2\n'
    assert len(table._programs[2]) == 1


def test_changed_key_tuple_rebuilds_the_program():
    table = store.Table((('z', store.PLAIN), ('a', store.PLAIN)))
    document = {'a': 1, 'z': 2}
    assert text(table, document) == 'z = 2\na = 1\n'
    object.__setattr__(table, 'keys', (('a', store.HEX), ('z', store.PLAIN)))
    assert text(table, document) == 'a = 0x1\nz = 2\n'
    assert table._programs[0] is table.keys


def test_nested_spec_changes_remain_live():
    child = store.Table((('value', store.PLAIN),))
    table = store.Table((('inner', child),))
    document = {'inner': {'value': 2}}
    assert text(table, document) == '[inner]\nvalue = 2\n'
    object.__setattr__(child, 'inline', True)
    assert text(table, document) == 'inner = {value = 2}\n'


def test_none_specs_retain_duplicate_order_and_infer_each_current_value():
    table = store.Table((('value', None),))
    assert text(table, {'value': 1}) == 'value = 1\nvalue = 1\n'
    assert text(table, {'value': {'inner': 2}}) == '[value]\ninner = 2\n\n[value]\ninner = 2\n'


def test_unknown_keys_preserve_dynamic_nested_inference_and_sorted_order():
    table = store.Table((('value', store.PLAIN),))
    assert text(table, {'z': 3, 'value': 1, 'a': 2}) == 'value = 1\na = 2\nz = 3\n'
    assert text(table, {'value': 1, 'extra': {'inner': 2}}) == 'value = 1\n\n[extra]\ninner = 2\n'


def test_changed_methods_execute_after_a_program_is_prepared():
    table = store.Table((('value', store.PLAIN),))
    assert text(table, {'value': 16}) == 'value = 16\n'
    with mock.patch.object(store.Table, 'spec', return_value=store.HEX) as lookup:
        assert text(table, {'value': 16}) == 'value = 0x10\n'
        assert lookup.called


def test_program_shapes_remain_bounded_and_revisit_evicted_shapes():
    table = store.Table(tuple((f'key{index}', store.PLAIN) for index in range(7)))
    for mask in range(80):
        document = {f'key{index}': 2 for index in range(7) if mask & (1 << index)}
        expected = ''.join(f'key{index} = 2\n' for index in range(7) if mask & (1 << index)) or '\n'
        assert text(table, document) == expected
        assert len(table._programs[2]) <= store._PROGRAM_SHAPES
    assert text(table, {}) == '\n'
