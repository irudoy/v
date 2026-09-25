import unittest
from unittest import mock

from kb import read, refs
from kb.refs import Ref


def sym(name, kind, address, layout="7mfk"):
    return {"key": f"{layout}-{address:08x}/{kind}", "name": name, "kind": kind,
            "layout": layout, "address": address}


class LinkStore:
    """The symbols and links of one layout as the queries of LinkGraph read them."""

    def __init__(self, symbols, links):
        self.symbols = {node["name"]: node for node in symbols}
        self.links = [(self.symbols[a]["key"], kind, self.symbols[b]["key"], roles)
                      for a, kind, b, roles in links]

    def run(self, query, **params):
        if "RETURN s.key AS key" in query:
            return [dict(node) for node in self.symbols.values()
                    if node["layout"] == params["layout"]]
        if "-[r]->(b:Kb:Symbol)" in query:
            return [{"a": a, "type": kind, "b": b, "role": roles, "verified": None}
                    for a, kind, b, roles in self.links]
        return []

    def resolve(self, graph, text, layout=None, root=None, many=False):
        node = self.symbols[text]
        return Ref("symbol", node, None, node["layout"], node["address"])

    def ref(self, name):
        return refs.symbol_ref(self.symbols[name])


def dataflow():
    """coolant -> coolant_index -> selector -> target -> target_copy, with a
    table indexed by coolant, a consumer of the selector, a homolog, and a
    citation."""
    return LinkStore([
        sym("coolant", "ram", 0xFFFF0001), sym("coolant_index", "ram", 0xFFFF0002),
        sym("selector", "fn", 0x10000), sym("target", "ram", 0xFFFF0003),
        sym("target_copy", "ram", 0xFFFF0004), sym("consumer", "fn", 0x20000),
        sym("twin", "ram", 0xFFFF0005), sym("tracer", "fn", 0x30000),
        sym("map", "tbl", 0xA000),
    ], [
        ("coolant_index", "INPUT", "coolant", []),
        ("coolant_index", "READER", "selector", []),
        ("target", "WRITER", "selector", []),
        ("target_copy", "COPY", "target", []),
        ("selector", "DEPENDS", "consumer", ["consumer"]),
        ("twin", "DEPENDS", "coolant", ["homolog"]),
        ("tracer", "CITES", "coolant", None),
        ("map", "DEPENDS", "coolant", ["indexed_by"]),
    ])


def detour():
    """start -> hub -> goal in two links through a hub of 42 links, and
    start -> first -> second -> third -> goal in four links without one."""
    names = ["start", "hub", "goal", "first", "second", "third"]
    symbols = [sym(name, "ram", 0xFFFF0000 + index) for index, name in enumerate(names)]
    symbols += [sym(f"leaf{index}", "ram", 0xFFFF1000 + index) for index in range(40)]
    symbols += [sym(f"idle{index}", "ram", 0xFFFF2000 + index) for index in range(90)]
    links = [("hub", "INPUT", "start", []), ("goal", "INPUT", "hub", []),
             ("first", "INPUT", "start", []), ("second", "INPUT", "first", []),
             ("third", "INPUT", "second", []), ("goal", "INPUT", "third", [])]
    links += [(f"leaf{index}", "INPUT", "hub", []) for index in range(40)]
    return LinkStore(symbols, links)


class PhraseTest(unittest.TestCase):
    def test_a_depends_link_reads_by_its_role(self):
        self.assertEqual(read.phrase("out", "DEPENDS", ["indexed_by"]), "depends on (indexed_by)")
        self.assertEqual(read.phrase("in", "DEPENDS", ["indexed_by"]), "needed by (indexed_by)")
        self.assertEqual(read.phrase("out", "DEPENDS", ["consumer"]), "needed by (consumer)")
        self.assertEqual(read.phrase("in", "DEPENDS", ["consumer"]), "depends on (consumer)")
        self.assertEqual(read.phrase("out", "DEPENDS", ["homolog"]), "homolog of")
        self.assertEqual(read.phrase("out", "READER"), "read by")
        self.assertEqual(read.phrase("in", "READER"), "reads")


class LinkGraphTest(unittest.TestCase):
    def test_edges_run_from_what_a_change_starts_at(self):
        store = dataflow()
        links = read.LinkGraph(store, "7mfk")
        key = {name: node["key"] for name, node in store.symbols.items()}
        value = {parent: [child for child, *_ in children]
                 for parent, children in links.edges["value"].items()}
        self.assertEqual(value[key["coolant"]], sorted([key["coolant_index"], key["map"]]))
        self.assertEqual(value[key["target"]], [key["target_copy"]])
        self.assertEqual([c for c, *_ in links.edges["read"][key["coolant_index"]]],
                         [key["selector"]])
        self.assertEqual([c for c, *_ in links.edges["write"][key["selector"]]], [key["target"]])
        self.assertEqual([c for c, *_ in links.edges["call"][key["selector"]]], [key["consumer"]])
        self.assertEqual([c for c, *_ in links.edges["cite"][key["coolant"]]], [key["tracer"]])
        self.assertNotIn(key["twin"], links.degree)

    def test_a_node_above_the_percentile_of_its_kind_is_a_hub(self):
        store = detour()
        links = read.LinkGraph(store, "7mfk")
        self.assertTrue(links.hub(store.symbols["hub"]["key"]))
        self.assertFalse(links.hub(store.symbols["start"]["key"]))


class ImpactTest(unittest.TestCase):
    def impact(self, store, name, expand=()):
        with mock.patch.object(refs, "resolve", store.resolve):
            return read.impact(store, name, expand=expand)

    def test_values_close_transitively_and_functions_are_the_boundary(self):
        store = dataflow()
        found = self.impact(store, "coolant").data
        self.assertEqual({item["ref"] for item in found["data"]},
                         {store.ref("coolant_index"), store.ref("map")})
        self.assertEqual(set(found["readers"]), {store.ref("selector")})
        self.assertEqual(found["cites"],
                         [f"{store.ref('tracer')} cites {store.ref('coolant')}"])
        self.assertIn(f"{store.ref('map')} depends on (indexed_by) {store.ref('coolant')}",
                      [item["fact"] for item in found["data"]])

    def test_a_function_starts_at_what_it_writes(self):
        store = dataflow()
        found = self.impact(store, "selector").data
        self.assertEqual([(item["depth"], item["ref"]) for item in found["data"]],
                         [(1, store.ref("target")), (2, store.ref("target_copy"))])
        self.assertEqual(found["consumers"], [
            f"{store.ref('consumer')} depends on (consumer) {store.ref('selector')}"])

    def test_a_hub_is_listed_and_not_expanded(self):
        store = detour()
        found = self.impact(store, "start").data
        refs_found = {item["ref"] for item in found["data"]}
        self.assertIn(store.ref("hub"), refs_found)
        self.assertNotIn(store.ref("leaf0"), refs_found)
        self.assertEqual(found["hubs"], {store.ref("hub"): 42})
        found = self.impact(store, "start", expand=["hub"]).data
        self.assertIn(store.ref("leaf0"), {item["ref"] for item in found["data"]})


class PathTest(unittest.TestCase):
    def path(self, store, first, second, expand=()):
        with mock.patch.object(refs, "resolve", store.resolve):
            return read.path(store, first, second, expand=expand)

    def test_dataflow_passes_through_the_function_that_reads_and_writes(self):
        store = dataflow()
        found = self.path(store, "coolant", "target_copy").data
        self.assertEqual(found["search"], "dataflow")
        self.assertEqual(found["paths"], [[
            f"{store.ref('coolant_index')} computed from {store.ref('coolant')}",
            f"{store.ref('selector')} reads {store.ref('coolant_index')}",
            f"{store.ref('target')} written by {store.ref('selector')}",
            f"{store.ref('target_copy')} copy of {store.ref('target')}"]])

    def test_the_reverse_direction_is_the_second_search(self):
        store = dataflow()
        found = self.path(store, "target_copy", "coolant").data
        self.assertEqual((found["search"], found["from"], found["to"]),
                         ("reverse dataflow", store.ref("coolant"), store.ref("target_copy")))

    def test_a_shorter_path_through_a_hub_names_the_option_that_expands_it(self):
        store = detour()
        found = self.path(store, "start", "goal")
        self.assertEqual(len(found.data["paths"][0]), 4)
        self.assertEqual(found.data["through_hubs"],
                         {"search": "dataflow", "links": 2, "hubs": [store.ref("hub")]})
        self.assertIn(f"  --expand {store.ref('hub')} shows it", found.lines())
        found = self.path(store, "start", "goal", expand=["hub"]).data
        self.assertEqual(len(found["paths"][0]), 2)
        self.assertIsNone(found["through_hubs"])


class FindStore:
    def __init__(self, rows):
        self.rows = rows

    def run(self, query, **params):
        return self.rows if "MATCH (m:Kb:Meaning)" in query else []


def meaning(name, kind, title=None, summary=None, former=()):
    return {"key": f"{name}/{kind}", "name": name, "kind": kind, "home": "7mfk",
            "title": title, "summary": summary, "former": list(former),
            "symbols": [sym(name, kind, 0x1000 + len(name))]}


class FindTest(unittest.TestCase):
    def test_tiers_rank_exact_prefix_substring_then_words(self):
        rows = [meaning("slice_map", "tbl", title="Knock slice map",
                        summary="Per-channel threshold by engine speed."),
                meaning("base_knock_threshold_map", "tbl"),
                meaning("fuel_trim", "ram", summary="Long-term fuel trim."),
                meaning("knock_threshold_lookup", "fn"),
                meaning("knock_threshold", "ram")]
        found = read.find(FindStore(rows), ["knock", "threshold"]).data
        self.assertEqual([item["meaning"] for item in found["results"]],
                         ["knock_threshold/ram", "knock_threshold_lookup/fn",
                          "base_knock_threshold_map/tbl", "slice_map/tbl"])
        self.assertEqual([item["tier"] for item in found["results"]],
                         ["exact", "prefix", "substring", "words"])

    def test_close_scores_mark_the_query_ambiguous(self):
        rows = [meaning("idle_speed_target", "ram"), meaning("idle_speed_limit", "ram")]
        lines = read.find(FindStore(rows), ["idle"]).lines()
        self.assertIn("ambiguous: 2 matches score within 10 percent of the first", lines)


class EvidenceTest(unittest.TestCase):
    def test_items_that_differ_in_at_share_a_line(self):
        items = [{"kind": "l0", "supports": "identity", "at": f"7mfk:{address:08x}"}
                 for address in (0x4D464, 0x4D468)]
        items.append({"kind": "trace", "supports": "identity", "to": "7mfk-000261b8/fn",
                      "relies": "structure"})
        lines = read.evidence_lines(items, {"7mfk-000261b8/fn": "puffin/fn/7mfk-000261b8"})
        self.assertEqual(lines, [
            "l0  supports identity  at 7mfk:0004d464 0004d468",
            "trace  supports identity  to puffin/fn/7mfk-000261b8  relies structure"])


if __name__ == "__main__":
    unittest.main()
