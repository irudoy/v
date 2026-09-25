import unittest

from kb import compile, repo
from kb.model import Builder, SymbolKey


def builder():
    layouts = repo.layouts()
    return Builder(layouts, compile.spaces(repo.config()),
                   {"7mfk": frozenset({0x26740}), "jk00d": frozenset({0x27344})},
                   {"7mfk": (0x8200, 0x20000)})


class MeaningTest(unittest.TestCase):
    def test_a_group_joins_symbols_of_several_layouts_into_one_meaning(self):
        b = builder()
        left = b.symbol("7mfk", "ram", 0xFFFF102C, "a.csv", group=("ram", "key", "load"))
        right = b.symbol("jk00d", "ram", 0xFFFF1034, "b.csv", group=("ram", "key", "load"))
        b.name(("ram", "key", "load"), "normalized_load", "symbol_key", "b.csv")
        b.name(left, "load_curated", "curated", "a.csv")
        model = b.finish()
        meaning = model.meaning_of(left)
        self.assertIs(meaning, model.meaning_of(right))
        self.assertEqual((meaning.key, meaning.home), ("normalized_load/ram", "7mfk"))
        self.assertEqual(meaning.other_names, [("load_curated", "curated", "a.csv")])

    def test_a_group_refuses_a_symbol_of_another_kind(self):
        b = builder()
        key = b.symbol("7mfk", "tbl", 0xA4AA, "a.csv")
        b.group(("ram", "key", "load"), key)
        self.assertEqual([issue.check for issue in b.issues], ["schema"])

    def test_one_meaning_holds_one_symbol_per_layout(self):
        b = builder()
        first = b.symbol("7mfk", "ram", 0xFFFF102C, "a.csv", group=("ram", "key", "x"))
        second = b.symbol("7mfk", "ram", 0xFFFF1030, "a.csv", group=("ram", "key", "x"))
        model = b.finish()
        self.assertEqual([issue.check for issue in b.issues], ["audit"])
        self.assertIn("refused join", b.issues[0].message)
        self.assertIsNot(model.meaning_of(first), model.meaning_of(second))

    def test_a_stronger_join_wins_over_a_registry_key(self):
        b = builder()
        source = b.symbol("7mfk", "ram", 0xFFFF22E0, "a.csv", group=("ram", "key", "mask"))
        role = b.symbol("7mfk", "ram", 0xFFFF2497, "a.csv", group=("ram", "key", "cut"))
        target = b.symbol("jk00d", "ram", 0xFFFF235C, "b.csv", group=("ram", "key", "cut"))
        b.join(source, target, "c.csv")
        model = b.finish()
        self.assertIs(model.meaning_of(source), model.meaning_of(target))
        self.assertIsNot(model.meaning_of(role), model.meaning_of(target))
        self.assertEqual([issue.path for issue in b.issues], ["b.csv"])

    def test_a_yielding_status_gives_way_to_a_symbol(self):
        b = builder()
        key = b.symbol("7mfk", "tbl", 0x9A1A, "a.csv", group=("tbl", "key", "surface"))
        b.symbol("1nd", "tbl", 0x9980, "b.csv", group=("tbl", "key", "surface"))
        b.status(key, "1nd", "absent", "c.csv", yields=True)
        b.status(key, "jk78c", "absent", "c.csv", yields=True)
        meaning = b.finish().meaning_of(key)
        self.assertEqual(sorted(meaning.statuses), ["jk78c"])
        self.assertEqual(b.issues, [])

    def test_a_better_rank_names_the_meaning_within_a_tier(self):
        b = builder()
        key = b.symbol("7mfk", "fn", 0x26740, "a.csv")
        b.name(key, "startup_state_clear", "hook", "b.toml", rank=1)
        b.name(key, "startup_initializer", "hook", "a.toml", rank=0)
        meaning = b.finish().meaning_of(key)
        self.assertEqual(meaning.name, "startup_initializer")

    def test_disagreeing_facts_go_to_the_audit_and_prose_accumulates(self):
        b = builder()
        key = b.symbol("7mfk", "tbl", 0xA4AA, "a.csv")
        b.props(key, {"storage": "uint8", "summary": "first"}, "a.csv")
        b.props(key, {"storage": "uint16", "summary": "second"}, "b.csv")
        model = b.finish()
        meaning = model.meaning_of(key)
        self.assertEqual(meaning.props["storage"], "uint8")
        self.assertEqual((meaning.props["summary"], meaning.props["note"]), ("first", ["second"]))
        self.assertEqual([(issue.check, issue.path) for issue in b.issues], [("audit", "b.csv")])

    def test_a_symbol_key_lifts_from_the_home_symbol_and_a_difference_stays_an_override(self):
        b = builder()
        wrapper = b.symbol("7mfk", "fn", 0x2642C, "a.csv")
        kernel = b.symbol("7mfk", "fn", 0x26740, "a.csv")
        homolog = b.symbol("jk00d", "fn", 0x27030, "b.csv")
        b.join(kernel, b.symbol("jk00d", "fn", 0x27344, "b.csv"), "c.csv")
        b.join(wrapper, homolog, "c.csv")
        b.join(wrapper, b.symbol("1me3b", "fn", 0x2AA48, "d.csv"), "e.csv")
        b.keys(SymbolKey("1me3b", "fn", 0x2AA48), {"interp": {
            "kernel": SymbolKey("1me3b", "fn", 0x2AA48), "cols": 16}}, "d.csv")
        b.keys(homolog, {"interp": {"kernel": SymbolKey("jk00d", "fn", 0x27344), "cols": 16}},
               "b.csv")
        b.keys(wrapper, {"interp": {"kernel": kernel, "cols": 16}}, "a.csv")
        model = b.finish()
        meaning = model.meaning_of(wrapper)
        self.assertEqual(meaning.props["interp"], {"kernel": kernel, "cols": 16})
        self.assertNotIn("interp", meaning.symbols["jk00d"].props)
        self.assertEqual(meaning.symbols["1me3b"].props["interp"]["kernel"],
                         SymbolKey("1me3b", "fn", 0x2AA48))
        self.assertEqual(b.issues, [])


class LinkTest(unittest.TestCase):
    def test_a_relation_stated_at_both_ends_is_one_link(self):
        b = builder()
        ram = b.symbol("7mfk", "ram", 0xFFFF106A, "vars.csv")
        fn = b.symbol("7mfk", "fn", 0x26740, "funcs.csv")
        b.link(ram, "writer", fn, "vars.csv", props={"relies": "structure"})
        b.link(ram, "writer", fn, "funcs.csv", props={"relies": "level"}, stated="to")
        b.link(ram, "reader", ram, "vars.csv")
        model = b.finish()
        [link] = model.links
        self.assertEqual((link.type, link.owner.kind, link.to.kind), ("writer", "ram", "fn"))
        self.assertEqual(link.props, {"relies": "structure", "reverse_relies": "level"})
        self.assertEqual(link.sources, {"vars.csv", "funcs.csv"})
        self.assertEqual(len(model.self_links), 1)

    def test_targets_resolve_to_registered_or_implicit_symbols(self):
        b = builder()
        b.symbol("7mfk", "axis", 0x125EA, "axes.csv")
        resolve = lambda address, kinds: b.resolve("7mfk", address, kinds, "t")
        self.assertEqual(resolve(0x125EA, ("tbl", "axis")), SymbolKey("7mfk", "axis", 0x125EA))
        self.assertEqual(resolve(0x26740, ("ram", "reg", "fn")), SymbolKey("7mfk", "fn", 0x26740))
        self.assertEqual(resolve(0xFFFF2458, ("ram", "reg", "fn")),
                         SymbolKey("7mfk", "ram", 0xFFFF2458))
        self.assertEqual(resolve(0xFFFFE80C, ("ram", "reg")), SymbolKey("7mfk", "reg", 0xFFFFE80C))
        self.assertEqual(resolve(0x12000, ("ram", "reg", "axis", "fn", "tbl")),
                         SymbolKey("7mfk", "tbl", 0x12000))
        self.assertEqual(resolve(0x30000, ("ram", "reg", "fn", "tbl", "const")),
                         SymbolKey("7mfk", "const", 0x30000))
        self.assertEqual(resolve(0x30004, ("tbl", "axis")), SymbolKey("7mfk", "tbl", 0x30004))
        self.assertEqual(resolve(0x30008, ("ram", "reg", "fn")), None)
        self.assertTrue(b.symbols[SymbolKey("7mfk", "fn", 0x26740)].implicit)
        self.assertFalse(b.symbols[SymbolKey("7mfk", "axis", 0x125EA)].implicit)


if __name__ == "__main__":
    unittest.main()
