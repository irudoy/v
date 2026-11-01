import unittest

from kb import refs
from kb.repo import KbError


def sym(name, kind, address, layout="7mfk", former=()):
    return {"key": f"{layout}-{address:08x}/{kind}", "name": name, "kind": kind,
            "layout": layout, "address": address, "former": list(former), "generated": name}


class Store:
    """Symbols and meanings as the queries of `refs` read them."""

    def __init__(self, symbols=(), meanings=(), owners=None):
        self.symbols = list(symbols)
        self.meanings = list(meanings)
        self.owners = owners or {}

    def row(self, node):
        return {"s": node, "m": self.owners.get(node["key"])}

    def run(self, query, **params):
        kind = "$kind" not in query or None
        if "WHERE s.key = $key" in query:
            return [self.row(node) for node in self.symbols if node["key"] == params["key"]]
        if "WHERE s.layout = $layout AND s.kind = $kind AND" in query:
            return [self.row(node) for node in self.symbols
                    if (node["layout"], node["kind"]) == (params["layout"], params["kind"])
                    and (node["name"] == params["name"] or params["name"] in node["former"])]
        if "WHERE s.layout = $layout AND s.address = $address" in query:
            return [self.row(node) for node in self.symbols
                    if (node["layout"], node["address"]) == (params["layout"], params["address"])]
        if "WHERE m.name = $name" in query:
            return [{"m": node} for node in self.meanings if node["name"] == params["name"]
                    and (kind or node["kind"] == params["kind"])]
        if "WHERE $name IN m.former" in query:
            return [{"m": node} for node in self.meanings if params["name"] in node["former"]
                    and (kind or node["kind"] == params["kind"])]
        if "WHERE $name IN s.former" in query:
            return [self.row(node) for node in self.symbols if params["name"] in node["former"]
                    and (kind or node["kind"] == params["kind"])]
        return []


class ResolveTest(unittest.TestCase):
    def assertCode(self, code, *args, **kwargs):
        with self.assertRaises(KbError) as raised:
            refs.resolve(*args, **kwargs)
        self.assertEqual(raised.exception.code, code)

    def test_usage_errors_and_unknown_entities_carry_their_exit_codes(self):
        store = Store()
        self.assertCode(5, store, "zz99:00001000")
        self.assertCode(2, store, "7mfk:00001000", layout="jk00d")
        self.assertCode(2, store, "name/bogus/7mfk")
        self.assertCode(5, store, "00001000")
        self.assertCode(5, store, "no_such_name")

    def test_a_location_without_a_symbol_resolves_to_the_location(self):
        found = refs.resolve(Store(), "7mfk:0x1000")
        self.assertEqual((found.kind, found.text), ("location", "7mfk:00001000"))
        found = refs.resolve(Store(), "1000", layout="jk00d")
        self.assertEqual((found.kind, found.text), ("location", "jk00d:00001000"))

    def test_a_location_resolves_to_its_symbol(self):
        store = Store([sym("coolant", "ram", 0xFFFF1079)])
        found = refs.resolve(store, "7mfk:ffff1079")
        self.assertEqual(found.text, "coolant/ram/7mfk-ffff1079")
        self.assertIsNone(found.note)

    def test_a_stale_full_reference_names_the_current_one(self):
        store = Store([sym("coolant", "ram", 0xFFFF1079, former=["old_coolant"])])
        found = refs.resolve(store, "old_coolant/ram/7mfk-ffff1079")
        self.assertEqual(found.text, "coolant/ram/7mfk-ffff1079")
        self.assertEqual(found.note, "stale reference old_coolant/ram/7mfk-ffff1079; "
                                     "current coolant/ram/7mfk-ffff1079")

    def test_a_name_of_several_meanings_is_ambiguous(self):
        store = Store(meanings=[{"key": "idle/ram", "name": "idle", "kind": "ram"},
                                {"key": "idle/fn", "name": "idle", "kind": "fn"}])
        with self.assertRaises(KbError) as raised:
            refs.resolve(store, "idle")
        self.assertEqual(raised.exception.code, 4)
        self.assertIn("idle/ram", str(raised.exception))
        self.assertEqual(refs.resolve(store, "idle/fn").text, "idle/fn")

    def test_a_former_name_after_a_semantic_rename_names_the_meaning(self):
        # The rename keeps the former meaning name and the former full
        # reference of the one symbol, whose name is the same.
        meaning = {"key": "trim_updater/fn", "name": "trim_updater", "kind": "fn",
                   "former": ["status_reporter"]}
        symbol = sym("trim_updater", "fn", 0x812FA, layout="1nd", former=["status_reporter"])
        store = Store([symbol], [meaning], owners={symbol["key"]: meaning})
        for text in ("status_reporter/fn", "status_reporter"):
            found = refs.resolve(store, text)
            self.assertEqual((found.kind, found.text), ("meaning", "trim_updater/fn"))
            self.assertEqual(found.note, "former name status_reporter; current trim_updater/fn")
        found = refs.resolve(store, "status_reporter/fn/1nd-000812fa")
        self.assertEqual((found.kind, found.text), ("symbol", "trim_updater/fn/1nd-000812fa"))

    def test_a_former_name_of_unrelated_entities_stays_ambiguous(self):
        meaning = {"key": "trim_updater/fn", "name": "trim_updater", "kind": "fn",
                   "former": ["status_reporter"]}
        other = {"key": "immo_gate/fn", "name": "immo_gate", "kind": "fn", "former": []}
        symbol = sym("immo_gate", "fn", 0x90000, layout="1nd", former=["status_reporter"])
        store = Store([symbol], [meaning, other], owners={symbol["key"]: other})
        with self.assertRaises(KbError) as raised:
            refs.resolve(store, "status_reporter/fn")
        self.assertEqual(raised.exception.code, 4)
        self.assertIn("trim_updater/fn", str(raised.exception))
        self.assertIn("immo_gate/fn/1nd-00090000", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
