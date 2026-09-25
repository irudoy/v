import unittest

from kb import refs
from kb.repo import KbError


def sym(name, kind, address, layout="7mfk", former=()):
    return {"key": f"{layout}-{address:08x}/{kind}", "name": name, "kind": kind,
            "layout": layout, "address": address, "former": list(former), "generated": name}


class Store:
    """Symbols and meanings as the queries of `refs` read them."""

    def __init__(self, symbols=(), meanings=()):
        self.symbols = list(symbols)
        self.meanings = list(meanings)

    def run(self, query, **params):
        if "WHERE s.key = $key" in query:
            return [{"s": node, "m": None} for node in self.symbols if node["key"] == params["key"]]
        if "WHERE s.layout = $layout AND s.kind = $kind AND" in query:
            return [{"s": node, "m": None} for node in self.symbols
                    if (node["layout"], node["kind"]) == (params["layout"], params["kind"])
                    and (node["name"] == params["name"] or params["name"] in node["former"])]
        if "WHERE s.layout = $layout AND s.address = $address" in query:
            return [{"s": node, "m": None} for node in self.symbols
                    if (node["layout"], node["address"]) == (params["layout"], params["address"])]
        if "WHERE m.name = $name" in query:
            return [{"m": node} for node in self.meanings if node["name"] == params["name"]
                    and ("$kind" not in query or node["kind"] == params["kind"])]
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


if __name__ == "__main__":
    unittest.main()
