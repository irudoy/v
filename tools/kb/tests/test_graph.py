from functools import lru_cache
import os
import unittest

import pytest

from kb import compile, fingerprint, graph, l0graph, names, repo
from kb.model import Builder, SymbolKey


def model():
    return compile.cached(repo.ROOT)


@lru_cache(maxsize=None)
def l0(layout_id):
    m = model()
    layout = m.layouts[layout_id]
    return l0graph.l0_rows(layout, m.spaces[layout.mcu])


def accesses(rows, func, location):
    return {access["props"]["producer"]: access["props"] for access in rows["accesses"]
            if (access["from"], access["to"]) == (func, location)}


@pytest.mark.slow
class L0RowsTest(unittest.TestCase):
    def test_functions_and_calls_follow_the_l0_files(self):
        rows = l0("7mfk")
        entry = next(row for row in rows["functions"] if row["key"] == "7mfk:00026740")
        self.assertEqual((entry["address"], entry["producer"], entry["src"]),
                         (0x26740, "l0", "l0/7mfk/funcs.csv"))
        self.assertIn("shape_sha256", entry)
        call = next(row for row in rows["calls"]
                    if (row["from"], row["to"]) == ("7mfk:00000e14", "7mfk:00000e9a"))
        self.assertEqual(call["props"]["sites"], [0xE30])

    def test_a_pool_literal_and_its_paired_load_are_accesses_of_both_producers(self):
        found = accesses(l0("jk00d"), "jk00d:0004a430", "jk00d:ffff1034")
        self.assertEqual(found["l0"]["modes"], ["literal", "read"])
        self.assertIn({"site": 0x4A62A, "mode": "literal", "pool": 0x4A6FC},
                      found["l0"]["sites"])
        self.assertEqual(found["derived"]["modes"], ["load"])
        site = found["derived"]["sites"][0]
        self.assertEqual((site["site"], site["literal"], site["pool"], site["base"]),
                         (0x4A62E, 0xFFFF1034, 0x4A6FC, "r10"))

    def test_a_rom_pointer_reference_is_an_l0_access(self):
        found = accesses(l0("7mfk"), "7mfk:0004d2a6", "7mfk:0000a4aa")
        self.assertIn({"site": 0x4D464, "mode": "param"}, found["l0"]["sites"])

    def test_every_access_ends_at_a_location_of_a_space(self):
        rows = l0("7mfk")
        locations = {row["key"]: row for row in rows["locations"]}
        self.assertTrue(all(access["to"] in locations for access in rows["accesses"]))
        self.assertEqual({row["space"] for row in rows["locations"]}, {"rom", "ram", "io"})
        self.assertEqual(locations["7mfk:ffff106a"]["producer"], "l0")


class ClaimRowsTest(unittest.TestCase):
    def test_step_call_order_preserves_repeated_entries(self):
        b = Builder(repo.layouts(), compile.spaces(repo.config()), {}, {})
        source = b.symbol('7mfk', 'ram', 0xffff1000, 'fixture')
        target = b.symbol('7mfk', 'ram', 0xffff1002, 'fixture')
        first = b.symbol('7mfk', 'fn', 0x1000, 'fixture')
        second = b.symbol('7mfk', 'fn', 0x2000, 'fixture')
        for key, name in ((source, 'source'), (target, 'target'),
                          (first, 'first'), (second, 'second')):
            b.name(key, name, 'file', 'fixture')
        chain = b.entity('chain', 'ordered', 'fixture')
        chain.steps = [{'from': source, 'to': target, 'via': [first, second, first],
                        'effect': 'converts', 'sign': 'positive'}]
        compiled = b.finish()
        names.assign(compiled, [])
        rows = graph.claim_rows(compiled)['entity_links']
        self.assertEqual([(item['to'], item['props']['order'])
                          for item in rows['THROUGH', 'Step', 'Meaning']],
                         [('first/fn', 1), ('second/fn', 2), ('first/fn', 3)])
        self.assertEqual(rows['FROM', 'Step', 'Meaning'][0]['to'], 'source/ram')
        self.assertEqual(rows['TO', 'Step', 'Meaning'][0]['to'], 'target/ram')

    def test_meanings_symbols_and_links(self):
        rows = graph.claim_rows(model())
        self.assertEqual(len(rows["has"]), len(rows["symbols"]))
        self.assertEqual(set(rows["links"]), set(rows["symbol_links"]))
        self.assertTrue(all(kind.isupper() for kind in rows["links"]))
        writer = next(row for row in rows["symbol_links"]["WRITER"]
                      if row["from"] == "7mfk-ffff106a/ram")
        self.assertEqual((writer["to"], writer["props"]["layout"], writer["props"]["producer"]),
                         ("7mfk-00020dfe/fn", "7mfk", "derived"))
        symbol = next(row for row in rows["symbols"] if row["key"] == "7mfk-00020dfe/fn")
        self.assertEqual((symbol["layout"], symbol["address"]), ("7mfk", 0x20DFE))

    def test_a_required_meaning_without_a_symbol_or_a_status_is_unknown(self):
        rows = graph.claim_rows(model())
        unknown = {(row["from"], row["to"]): row["props"] for row in rows["statuses"]
                   if row["props"]["state"] == "unknown"}
        required = model().required()
        self.assertTrue(set(unknown) <= set(required))
        self.assertTrue(all(props["required"] == sorted(required[pair])
                            for pair, props in unknown.items()))
        claimed = {(row["from"], row["to"]) for row in rows["statuses"]
                   if row["props"]["producer"] == "claim"}
        self.assertEqual(set(required) - set(unknown), set(required) & claimed)
        requires = rows["entity_links"][("REQUIRES", "Entity", "Entity")]
        self.assertIn({"from": "can_telemetry/feature", "to": "normalized_load_raw/field"},
                      [{"from": row["from"], "to": row["to"]} for row in requires])

    def test_the_requires_of_targets_reach_their_meanings_with_their_layouts(self):
        rows = graph.claim_rows(model())
        requires = {row["to"]: row["props"]["layouts"]
                    for row in rows["entity_links"][("REQUIRES", "Entity", "Meaning")]
                    if row["from"] == "definitions/feature"}
        self.assertEqual(requires["intake_cvtc_target/tbl"],
                         ["1me3b", "1nd", "jk00c", "jk00d", "jk78c"])
        targets = [row for row in rows["targets"] if row["from"] == "definitions/feature"]
        self.assertTrue(targets and all("requires" not in row["props"] for row in targets))

    def test_the_key_tables_roles_hooks_and_requires_of_targets_are_required(self):
        m = model()
        rows = graph.claim_rows(m)
        requires = {(row["from"], row["to"]): row["props"]["layouts"]
                    for row in rows["entity_links"][("REQUIRES", "Entity", "Meaning")]}
        self.assertEqual(requires[("map_switching/feature", "rev_fuel_cut_state/ram")],
                         ["1me3b", "1nd", "jk78c"])
        self.assertIn("7mfk", requires[("map_switching/feature", "over_run_fuel_cut/tbl")])
        self.assertIn("7mfk", requires[("rolling_launch/feature", "fuel_inhibit/ram")])
        for (feature, layout), target in m.targets.items():
            for key in target.needs():
                meaning = m.meaning_of(key)
                if meaning is not None and meaning.name:
                    self.assertIn(layout, requires[(f"{feature}/feature", meaning.key)])

    def test_values_become_storable(self):
        stored = graph.properties({"to": SymbolKey("7mfk", "fn", 0x26740), "empty": [],
                                   "none": None, "set": {"b", "a"}, "nested": [{"x": None}]})
        self.assertEqual(stored, {"to": "7mfk-00026740/fn", "set": ["a", "b"],
                                  "nested": [{}]})


class ReadOnlyTest(unittest.TestCase):
    def test_write_clauses_are_refused_and_reads_pass(self):
        refused = ["MATCH (n) SET n.x = 1", "match (n) detach delete n", "CREATE INDEX ON :X(y)",
                   "FREE MEMORY", "LOAD CSV FROM '/x' WITH HEADER AS row RETURN row",
                   "MERGE (n:X {key: 1})"]
        for query in refused:
            self.assertIsNotNone(graph.refusal(query), query)
        passed = ["MATCH (n:Meaning) RETURN n.storage AS storage", "RETURN {set: 1}",
                  "RETURN 'CREATE (n)' AS text // DELETE", "CALL pagerank.get() YIELD node RETURN node"]
        for query in passed:
            self.assertIsNone(graph.refusal(query), query)
        self.assertIsNotNone(graph.refusal("CALL x.write()", {"x.write"}))


@unittest.skipUnless(os.environ.get("KB_TEST_BOLT"),
                     "set KB_TEST_BOLT to a scratch Memgraph server to run the load")
class LoadTest(unittest.TestCase):
    """Loads the whole model, about a minute, into the server of KB_TEST_BOLT,
    which the test clears."""

    def test_a_load_writes_meta_last_and_a_second_load_changes_nothing(self):
        os.environ["KB_BOLT"] = os.environ["KB_TEST_BOLT"]
        m = model()
        fp = fingerprint.compute()
        with graph.Graph() as session:
            summary = graph.load(session, m, fp, full=True, log=lambda text: None)
            self.assertEqual(set(summary), {*(f"l0 {layout}" for layout in m.layouts),
                                            "claims", "at"})
            self.assertFalse(graph.stale(graph.meta(session), fp))
            self.assertEqual(graph.load(session, m, fp, log=lambda text: None), {})
            verified = lambda data, fn: session.run(
                "MATCH (:Symbol {key: $data})-[r:WRITER]->(:Symbol {key: $fn}) "
                "RETURN r.verified AS verified", data=data, fn=fn)[0]["verified"]
            # A direct store verifies a writer; a block copy loads only the
            # destination address and needs indirect evidence.
            self.assertTrue(verified("7mfk-ffff1072/ram", "7mfk-0003e1da/fn"))
            self.assertFalse(verified("7mfk-ffff106a/ram", "7mfk-00020dfe/fn"))


if __name__ == "__main__":
    unittest.main()
