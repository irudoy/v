import copy
from dataclasses import fields
import pickle
import re
import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest.mock import patch

from kb import repo, store

EXAMPLE = re.compile(r"^`kb/(?P<kind>[a-z]+)/(?P<name>[a-z_]+)\.toml`:\n\n```toml\n(?P<text>.*?)```$",
                     re.M | re.S)


def canonical(kind, document):
    text = store.render(kind, document)
    return text, tomllib.loads(text)


class RenderTest(unittest.TestCase):
    def test_the_examples_of_the_specification_are_canonical(self):
        examples = list(EXAMPLE.finditer((repo.ROOT / "tools/kb/SPEC.md").read_text(
            encoding="utf-8")))
        self.assertGreaterEqual(len(examples), 2)
        for example in examples:
            with self.subTest(name=example["name"]):
                text = example["text"]
                self.assertEqual(store.render(example["kind"], tomllib.loads(text)), text)

    def test_keys_follow_the_schema_and_absent_keys_are_omitted(self):
        text, _ = canonical("tbl", {"storage": "uint8", "title": "A table", "cols": 4,
                                    "summary": "", "note": [], "level": "code"})
        self.assertEqual(text, 'title = "A table"\nlevel = "code"\ncols = 4\n'
                               'storage = "uint8"\n')

    def test_a_long_string_wraps_within_78_columns_and_keeps_its_value(self):
        summary = " ".join(["word"] * 40) + " [[normalized_bfs/ram]] closes it."
        text, document = canonical("ram", {"title": "t", "summary": summary})
        self.assertEqual(document["summary"], summary)
        lines = text.splitlines()
        self.assertEqual(lines[1], 'summary = """')
        self.assertTrue(all(len(line) <= store.WIDTH for line in lines))
        self.assertTrue(all(line.endswith(" \\") for line in lines[2:-1]))
        self.assertTrue(lines[-1].endswith('"""'))

    def test_a_string_of_72_characters_stays_on_one_line(self):
        title = "x" * store.SHORT
        text, _ = canonical("fn", {"title": title})
        self.assertEqual(text, f'title = "{title}"\n')

    def test_an_array_that_does_not_fit_puts_one_element_per_line(self):
        notes = ["first note " * 3, "second note " * 3, "third"]
        text, document = canonical("fn", {"title": "t", "note": notes})
        self.assertEqual(document["note"], notes)
        self.assertIn('note = [\n    "first note', text)
        self.assertIn('    "third",\n]\n', text)
        short, _ = canonical("fn", {"title": "t", "note": ["a", "b"]})
        self.assertIn('note = ["a", "b"]\n', short)

    def test_offsets_and_did_numbers_are_hexadecimal(self):
        text, document = canonical("did", {"title": "t", "number": 0x1234, "link": [
            {"type": "source", "to": "x/ram", "offset": 10}]})
        self.assertIn("number = 0x1234\n", text)
        self.assertIn("offset = 0xa\n", text)
        self.assertEqual(document["link"][0]["offset"], 10)

    def test_arrays_of_tables_sort_by_their_schema_keys(self):
        text, document = canonical("ram", {"title": "t", "symbol": [
            {"layout": "jk00d", "address": "ffff1050"},
            {"layout": "7mfk", "address": "ffff1048",
             "evidence": [{"kind": "l0", "supports": "identity", "at": "7mfk:0003bd5a"}]}],
            "status": [{"layout": "jk78c", "state": "absent"},
                       {"layout": "1nd", "state": "absent"}]})
        self.assertEqual([item["layout"] for item in document["symbol"]], ["7mfk", "jk00d"])
        self.assertEqual([item["layout"] for item in document["status"]], ["1nd", "jk78c"])
        self.assertLess(text.index("[[symbol.evidence]]"), text.index('layout = "jk00d"'))

    def test_keys_outside_the_schema_follow_in_alphabetical_order(self):
        text, document = canonical("feature", {
            "title": "Runtime", "target": [
                {"layout": "7mfk", "status": "supported", "rom_size": 1048576,
                 "hooks": {"b": {"hook": "b/hook", "replacement": "0000f000"},
                           "a": {"hook": "a/hook", "replacement": "0000e000"}}}]})
        self.assertEqual(list(document["target"][0]["hooks"]), ["a", "b"])
        self.assertLess(text.index("rom_size"), text.index("[target.hooks.a]"))
        self.assertEqual(store.render("feature", document), text)

    def test_the_presentation_of_a_field_follows_its_keys_and_its_feed_table_ends_it(self):
        dashboard = {"feed": {"step": 20, "maximum": 200, "minimum": 0, "format": "0.00",
                              "name": "VQ Probe", "key": "probe"},
                     "order": 40, "panel": "Air and fuel", "digits": 1, "label": "Probe",
                     "description": " ".join(["word"] * 30)}
        text, document = canonical("field", {
            "signed": False, "dashboard": dashboard, "width": 1, "origin": "ecu_ram",
            "source": "probe/ram", "signal": "probe/signal"})
        self.assertEqual(document["dashboard"], dashboard)
        lines = text.splitlines()
        self.assertEqual([line.split(" = ")[0] for line in lines if " = " in line],
                         ["signal", "source", "origin", "width", "signed", "label", "digits",
                          "panel", "order", "description", "key", "name", "format",
                          "minimum", "maximum", "step"])
        self.assertLess(text.index("\n\n[dashboard]\n"), text.index("\n\n[dashboard.feed]\n"))
        self.assertTrue(all(len(line) <= store.WIDTH for line in lines))
        self.assertEqual(store.render("field", document), text)

    def test_rendering_is_idempotent(self):
        document = {"title": "t", "summary": "s " * 50, "home": "7mfk", "width": 8,
                    "bit": [{"bit": 3, "name": "armed"}, {"bit": 0, "name": "active"}],
                    "link": [{"type": "writer", "to": "f/fn", "relies": "structure",
                              "via": ["g/fn", "h/fn"]}]}
        text = store.render("ram", document)
        self.assertEqual(store.render("ram", tomllib.loads(text)), text)


class EscapeScanTest(unittest.TestCase):
    def test_ascii_controls_and_named_escapes_keep_their_literal_forms(self):
        named = {'"': '\\"', "\\": "\\\\", "\b": "\\b", "\t": "\\t", "\n": "\\n", "\f": "\\f",
                 "\r": "\\r"}
        for point in range(128):
            text = chr(point)
            expected = named.get(text, f"\\u{point:04x}" if point < 32 or point == 127 else text)
            with self.subTest(point=point):
                self.assertEqual(store.escape(text), expected)

    def test_unicode_and_long_mixed_strings_keep_content_and_return_type(self):
        samples = ["", "\u0085", "\u0416", "\u2028", "\U0001f600", "\ud800", "\udfff", "\U0010ffff",
                   "a" * 4096, "a" * 72 + '\\"', "\u0416" * 96 + "\x1f"]
        for text in samples:
            expected = "".join(store.ESCAPES.get(char, (
                f"\\u{ord(char):04x}" if ord(char) < 32 or ord(char) == 127 else char))
                for char in text)
            with self.subTest(text=repr(text)):
                result = store.escape(text)
                self.assertEqual(result, expected)
                self.assertIs(type(result), str)

    def test_subclasses_and_character_iterables_keep_their_string_result(self):
        class Text(str):
            pass
        factories = (lambda: Text('a"b'), lambda: ['a', '"', 'b'],
                     lambda: iter(['a', '"', 'b']), lambda: {'a': 1, '"': 2, 'b': 3})
        for make in factories:
            result = store.escape(make())
            self.assertEqual(result, 'a\\"b')
            self.assertIs(type(result), str)

    def test_invalid_inputs_keep_their_original_error_kind(self):
        cases = ((None, "not iterable"), (1, "not iterable"), ([None], "ord"),
                 (["ab"], "length 2"), (b"ab", "int"))
        for value, message in cases:
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(TypeError, message):
                    store.escape(value)

    def test_a_plain_string_does_not_probe_each_character_against_named_escapes(self):
        class ObservedEscapes(dict):
            probes = 0

            def __contains__(self, key):
                self.probes += 1
                return super().__contains__(key)

        observed = ObservedEscapes(store.ESCAPES)
        text = "plain " * 1000
        with patch.object(store, "ESCAPES", observed):
            self.assertEqual(store.escape(text), text)
        self.assertLessEqual(observed.probes, 64)


class CanonicalTest(unittest.TestCase):
    def test_the_check_names_a_file_that_differs_and_fmt_rewrites_it(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "kb" / "ram" / "loose_value.toml"
            path.parent.mkdir(parents=True)
            path.write_text('level = "code"\ntitle = "Loose"\n', encoding="utf-8")
            issues = store.canonical(root)
            self.assertEqual([(issue.path, issue.subject) for issue in issues],
                             [("kb/ram/loose_value.toml", "loose_value/ram")])
            self.assertEqual(store.fmt(root), [Path("kb/ram/loose_value.toml")])
            self.assertEqual(path.read_text(encoding="utf-8"), 'title = "Loose"\nlevel = "code"\n')
            self.assertEqual(store.canonical(root), [])

    def test_a_file_that_does_not_parse_fails_the_check(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "kb" / "fn" / "broken.toml"
            path.parent.mkdir(parents=True)
            path.write_text("title = \n", encoding="utf-8")
            (issue,) = store.canonical(root)
            self.assertTrue(issue.message.startswith("no TOML"))


class SchemaLookupTest(unittest.TestCase):
    def test_immutable_duplicate_keys_keep_the_first_object_and_none_spec(self):
        first, second = object(), object()
        table = store.Table((('a', first), ('a', second), ('b', None), ('b', second)))
        for _ in range(2):
            self.assertIs(table.spec('a'), first)
            self.assertIsNone(table.spec('b'))
            self.assertIsNone(table.spec('missing'))
        self.assertEqual(table.order({'a': 1, 'b': 2, 'missing': 3}), ['a', 'a', 'b', 'b', 'b', 'missing'])

    def test_mutable_key_containers_preserve_edits_and_first_match(self):
        for keys in ([('a', 'plain')], (['a', 'plain'],), [['a', 'plain']]):
            with self.subTest(keys=keys):
                table = store.Table(keys)
                self.assertEqual(table.spec('a'), 'plain')
                if isinstance(keys, list):
                    keys[0] = ('b', 'hex')
                else:
                    keys[0][:] = ['b', 'hex']
                self.assertIsNone(table.spec('a'))
                self.assertEqual(table.spec('b'), 'hex')

    def test_nonstandard_queries_keep_unhashable_equality_and_comparison_order(self):
        compared = []
        class Key(str):
            __hash__ = None
            def __eq__(self, other):
                compared.append(other)
                return other == 'b'
        table = store.Table((('a', 'plain'), ('b', 'hex')))
        self.assertEqual(table.spec('a'), 'plain')
        self.assertEqual(table.spec(Key('unrelated')), 'hex')
        self.assertEqual(compared, ['a', 'b'])
        for key in (None, 1, [], {}):
            with self.subTest(key=key):
                self.assertIsNone(table.spec(key))

    def test_table_subclasses_preserve_constructor_and_field_access_behavior(self):
        accessed = []
        class Table(store.Table):
            def __post_init__(self):
                raise AssertionError('Unexpected constructor hook')
            def __getattribute__(self, name):
                accessed.append(name)
                return super().__getattribute__(name)
        table = Table((('a', 'plain'),))
        accessed.clear()
        self.assertEqual(table.spec('a'), 'plain')
        self.assertEqual(accessed, ['spec', 'keys'])

    def test_malformed_keys_keep_lookup_errors_and_constructor_acceptance(self):
        for keys, exception, message in ((None, TypeError, "'NoneType' object is not iterable"),
                                         (7, TypeError, "'int' object is not iterable"),
                                         ((('a',),), ValueError, 'not enough values to unpack'),
                                         ((('a', None, None),), ValueError, 'too many values to unpack')):
            with self.subTest(keys=keys):
                table = store.Table(keys)
                for _ in range(2):
                    with self.assertRaises(exception) as error:
                        table.spec('a')
                    self.assertIn(message, str(error.exception))

    def test_replacing_the_key_tuple_preserves_current_specification_objects(self):
        old, current = object(), object()
        table = store.Table((('a', old),))
        self.assertIs(table.spec('a'), old)
        object.__setattr__(table, 'keys', (('b', current),))
        self.assertIsNone(table.spec('a'))
        self.assertIs(table.spec('b'), current)

    def test_copy_pickle_repr_hash_and_dataclass_fields_keep_their_contracts(self):
        table = store.Table((('a', store.Table((('b', 'plain'),))),), sort=('a',), inline=True)
        before = repr(table), hash(table)
        table.spec('a')
        self.assertEqual((repr(table), hash(table)), before)
        self.assertEqual([item.name for item in fields(table)], ['keys', 'sort', 'inline'])
        for clone in (copy.copy(table), copy.deepcopy(table), pickle.loads(pickle.dumps(table))):
            with self.subTest(clone=type(clone)):
                self.assertIs(clone.spec('a'), clone.keys[0][1])
                self.assertEqual(clone, table)
                self.assertEqual((repr(clone), hash(clone)), before)

    def test_independent_tables_keep_their_own_mutable_specification_references(self):
        first, second = {'value': 1}, {'value': 2}
        a, b = store.Table((('a', first),)), store.Table((('a', second),))
        self.assertIs(a.spec('a'), first)
        self.assertIs(b.spec('a'), second)
        first['value'] = 3
        self.assertIs(a.spec('a'), first)
        self.assertEqual(a.spec('a')['value'], 3)
        self.assertEqual(b.spec('a')['value'], 2)


class SchemaOrderTest(unittest.TestCase):
    def test_builtin_key_containers_keep_schema_order_and_sorted_unknowns(self):
        table = store.Table((('z', store.DID), ('a', store.PLAIN)))
        for make in (dict.fromkeys, list, tuple, set, frozenset):
            with self.subTest(container=make):
                result = table.order(make(('b', 'a', 'c', 'z')))
                self.assertIs(type(result), list)
                self.assertEqual(result, ['z', 'a', 'b', 'c'])
                result.append('local')
                self.assertEqual(table.order(make(('b', 'a', 'c', 'z'))), ['z', 'a', 'b', 'c'])

    def test_duplicate_names_and_a_first_none_spec_keep_duplicate_output_keys(self):
        table = store.Table((('a', None), ('z', store.DID), ('a', store.TEXT),
                             ('present', store.PLAIN)))
        self.assertEqual(table.order({'b': 1, 'a': 2, 'z': 3, 'present': 4}),
                         ['a', 'z', 'a', 'present', 'a', 'b'])

    def test_mutable_grammar_rows_and_key_containers_keep_current_values(self):
        for rows in ([('a', store.PLAIN)], (['a', store.PLAIN],), [['a', store.PLAIN]]):
            with self.subTest(rows=rows):
                table = store.Table(rows)
                self.assertEqual(table.order(['b', 'a']), ['a', 'b'])
                if isinstance(rows, list):
                    rows[0] = ('b', store.HEX)
                else:
                    rows[0][:] = ['b', store.HEX]
                self.assertEqual(table.order(['b', 'a']), ['b', 'a'])
        keys = ['b', 'a']
        table = store.Table((('a', store.PLAIN),))
        self.assertEqual(table.order(keys), ['a', 'b'])
        keys[:] = ['c']
        self.assertEqual(table.order(keys), ['c'])

    def test_replacing_the_immutable_grammar_discards_the_previous_index(self):
        table = store.Table((('a', store.PLAIN),))
        self.assertEqual(table.order({'a': 1, 'b': 2}), ['a', 'b'])
        object.__setattr__(table, 'keys', (('b', None), ('a', store.PLAIN)))
        self.assertEqual(table.order({'a': 1, 'b': 2}), ['b', 'a', 'b'])
        object.__setattr__(table, 'keys', (('b', store.HEX),))
        self.assertEqual(table.order({'a': 1, 'b': 2}), ['b', 'a'])

    def test_a_subclass_override_remains_the_source_of_unknown_key_classification(self):
        class Table(store.Table):
            def spec(self, key):
                return None if key == 'b' else super().spec(key)
        table = Table((('a', store.PLAIN), ('b', store.HEX)))
        self.assertEqual(table.order({'a': 1, 'b': 2, 'other': 3}), ['a', 'b', 'b', 'other'])

    def test_nonstandard_key_objects_keep_equality_and_output_identity(self):
        class Key(str):
            pass
        a, c = Key('a'), Key('c')
        table = store.Table((('a', store.PLAIN),))
        result = table.order([c, a])
        self.assertEqual(result, ['a', 'c'])
        self.assertIs(type(result[0]), str)
        self.assertIs(result[1], c)
        self.assertEqual(table.order(['a', 1]), ['a', 1])
        with self.assertRaises(TypeError):
            table.order(['a', 1, 'unknown'])

    def test_a_custom_key_container_preserves_membership_and_iteration_behavior(self):
        calls = []
        class Keys:
            def __contains__(self, key):
                calls.append(('contains', key))
                return key in ('a', 'b')
            def __iter__(self):
                calls.append(('iterate',))
                return iter(('b', 'a'))
            def __bool__(self):
                raise AssertionError('Custom truth testing is not part of ordering.')
        table = store.Table((('a', store.PLAIN), ('b', store.HEX)))
        self.assertEqual(table.order(Keys()), ['a', 'b'])
        self.assertEqual(calls, [('contains', 'a'), ('contains', 'b'), ('iterate',)])

    def test_empty_containers_leave_an_unused_grammar_index_uninitialized(self):
        for make in (dict, list, tuple, set, frozenset):
            with self.subTest(container=make):
                table = store.Table((('a', store.PLAIN),))
                self.assertEqual(table.order(make()), [])
                self.assertNotIn('_lookup', vars(table))


if __name__ == "__main__":
    unittest.main()
