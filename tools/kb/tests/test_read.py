from pathlib import Path
import tempfile
import unittest
from unittest import mock

from kb import graph, read, refs, vocab
from kb.refs import Ref
from kb.repo import KbError


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
    def test_analogs_are_separate_bidirectional_hints_with_their_notes(self):
        hint = {'to': 'foreign_output/ram', 'name': 'foreign_output',
                'note': 'Similar role; separate mechanism.'}
        store = mock.Mock()
        store.run.return_value = [hint, dict(hint)]
        self.assertEqual(read.analogs_of(store, {'key': 'output/ram'}), [hint])
        self.assertEqual(store.run.call_args.kwargs, {'key': 'output/ram'})

    def test_a_depends_link_reads_by_its_role(self):
        self.assertEqual(read.phrase("out", "DEPENDS", ["indexed_by"]), "depends on (indexed_by)")
        self.assertEqual(read.phrase("in", "DEPENDS", ["indexed_by"]), "needed by (indexed_by)")
        self.assertEqual(read.phrase("out", "DEPENDS", ["consumer"]), "needed by (consumer)")
        self.assertEqual(read.phrase("in", "DEPENDS", ["consumer"]), "depends on (consumer)")
        self.assertEqual(read.phrase("out", "DEPENDS", ["homolog"]), "homolog of")
        self.assertEqual(read.phrase("out", "READER"), "read by")
        self.assertEqual(read.phrase("in", "READER"), "reads")

    def test_every_relationship_of_an_entity_reads_both_ways(self):
        types = {kind for kind, _ in graph.ENTITY_LINKS.values()} | {"TARGETS"}
        types |= {kind.upper() for kind in vocab.LINK_TYPES}
        for kind in sorted(types - {"DEPENDS"}):
            self.assertTrue(read.phrase("out", kind) and read.phrase("in", kind), kind)


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


SNAPSHOT_HOOKS = {"snapshot": {"hook": "snapshot_call/hook", "replacement": "000d4280"}}


class FeatureStore:
    """Telemetry fields of a load and of the index computed from it, a field
    of the Rolling Launch phase, the definitions that require the index on
    two targets, and a bundle that requires can_telemetry. The load has
    symbols on 7mfk and jk00c and a status on 1nd, and a proxy fills its
    field on jk78c; the phase has a stated allocation on 7mfk and jk00c."""

    LAYOUTS = ("1nd", "7mfk", "jk00c", "jk78c")
    ENTITIES = {
        "load_raw/field": {"key": "load_raw/field", "kind": "field", "slug": "load_raw",
                           "origin": "ecu_ram"},
        "phase/field": {"key": "phase/field", "kind": "field", "slug": "phase",
                        "origin": "rolling_launch", "source": "rolling_launch.phase"},
        "can_telemetry/feature": {"key": "can_telemetry/feature", "kind": "feature",
                                  "slug": "can_telemetry"},
        "rolling_launch/feature": {"key": "rolling_launch/feature", "kind": "feature",
                                   "slug": "rolling_launch"},
        "runtime/feature": {"key": "runtime/feature", "kind": "feature", "slug": "runtime"},
    }
    SYMBOLS = {
        "load/ram": [sym("load", "ram", 0xFFFF102C), sym("load", "ram", 0xFFFF1034, "jk00c")],
        "load_proxy/ram": [sym("load_proxy", "ram", 0xFFFF22F8, "jk78c")],
        "snapshot_call/hook": [sym("snapshot_call", "hook", 0x28090),
                               sym("snapshot_call", "hook", 0x28CF8, "jk00c")],
    }
    STATUSES = {"load/ram": {"1nd": {"state": "unresolved", "method": "masked-match",
                                     "target": "7mfk:ffff102c", "count": 0}}}
    CARRIES = [("index_raw/field", "load_index/ram"), ("load_raw/field", "load/ram")]
    REQUIRES = [("bundle/feature", "can_telemetry/feature", None),
                ("can_telemetry/feature", "index_raw/field", None),
                ("can_telemetry/feature", "load_raw/field", None),
                ("can_telemetry/feature", "phase/field", None),
                ("definitions/feature", "load_index/ram", ["jk00c", "jk78c"])]
    TARGETS = {
        "can_telemetry/feature": {
            layout: {"status": "supported", "hooks": SNAPSHOT_HOOKS,
                     "roles": {"load_raw": {"symbol": "load_proxy/ram"}}
                     if layout == "jk78c" else None}
            for layout in LAYOUTS},
        "rolling_launch/feature": {
            "7mfk": {"status": "supported", "allocations": {
                "phase": {"address": "ffff5d40", "width": 1}}},
            "jk00c": {"status": "supported", "allocations": {
                "phase": {"address": "ffff6040", "width": 1}}}},
        "runtime/feature": {
            "1nd": {"status": "supported", "ram_delta": -0x5100, "rom_delta": 0x60000},
            "7mfk": {"status": "supported", "injected_rom_start": "000d2108",
                     "injected_rom_end": "000d6000", "injected_ram_start": "ffff5d00",
                     "injected_ram_end": "ffff6000"},
            "jk00c": {"status": "supported", "ram_delta": 0x300, "rom_delta": 0xC700},
            "jk78c": {"status": "supported", "ram_delta": -0x5100}},
    }

    def run(self, query, **params):
        if "MATCH (m:Kb:Meaning) RETURN" in query:
            return [{"key": key, "kind": "ram", "name": key.partition("/")[0]}
                    for key in ("load/ram", "load_index/ram", "load_proxy/ram")]
        if "(a:Kb:Meaning)-[r]->(b:Kb:Meaning)" in query:
            return [{"a": "load_index/ram", "type": "INPUT", "b": "load/ram", "role": None,
                     "verified": None}]
        if "[:CARRIES]" in query:
            if "keys" in params:
                return [{"field": field, "meaning": meaning} for field, meaning in self.CARRIES
                        if meaning in params["keys"]]
            return [{"key": meaning} for field, meaning in self.CARRIES
                    if field == params["key"]]
        if "[r:REQUIRES]" in query:
            return [{"feature": feature, "required": key, "layouts": layouts}
                    for feature, key, layouts in self.REQUIRES if key in params["keys"]]
        if "[:SERVES]" in query:
            return [{"signal": "load/signal"}] if params["key"] == "load_raw/field" else []
        if "t.roles AS roles" in query:
            return [{"feature": feature.partition("/")[0], "layout": layout,
                     "roles": target.get("roles")}
                    for feature in params["features"]
                    for layout, target in self.TARGETS.get(feature, {}).items()]
        if "t.allocations AS allocations" in query:
            return [{"layout": layout, "allocations": target.get("allocations")}
                    for layout, target in self.TARGETS.get(params["key"], {}).items()]
        if "properties(t) AS target" in query:
            key = params.get("key", "runtime/feature")
            return [{"layout": layout, "target": target}
                    for layout, target in self.TARGETS.get(key, {}).items()]
        if "[r:STATUS]" in query:
            return [{"layout": layout, "status": status, "current": None}
                    for layout, status in self.STATUSES.get(params["key"], {}).items()]
        if "RETURN m.key AS meaning, s" in query:
            return [{"meaning": key, "s": node} for key in params["keys"]
                    for node in self.SYMBOLS.get(key, ())]
        if "[:HAS]->(s:Kb:Symbol) RETURN s" in query:
            return [{"s": node} for node in self.SYMBOLS.get(params["key"], ())]
        return []

    def resolve(self, graph, text, layout=None, root=None, many=False):
        if text in self.ENTITIES:
            return Ref("entity", self.ENTITIES[text])
        return Ref("meaning", {"key": text, "kind": "ram", "name": text.partition("/")[0]})


class FeatureImpactTest(unittest.TestCase):
    def impact(self, text, layout=None):
        store = FeatureStore()
        with mock.patch.object(refs, "resolve", store.resolve), \
                mock.patch.object(read.repo, "layouts", lambda *args: store.LAYOUTS):
            return read.impact(store, text, layout)

    def test_the_fields_of_the_closure_and_the_features_that_require_them_follow(self):
        answer = self.impact("load/ram")
        lines = answer.text().splitlines()
        self.assertEqual(lines[0], "impact of load/ram: 1 data, 0 reading functions, "
                                   "2 fields, 3 features")
        self.assertEqual(lines[lines.index("fields") + 1:lines.index("features")], [
            "  index_raw/field carries load_index/ram", "  load_raw/field carries load/ram"])
        self.assertEqual(lines[lines.index("features") + 1:lines.index("insertion points")], [
            "  bundle/feature requires can_telemetry/feature",
            "  can_telemetry/feature requires index_raw/field",
            "  can_telemetry/feature requires load_raw/field",
            "  definitions/feature requires load_index/ram on jk00c, jk78c"])

    def test_the_insertion_points_of_a_meaning_state_every_layout(self):
        self.assertEqual(self.impact("load/ram").data["insertion_points"], [
            "  1nd    unresolved  masked-match  7mfk:ffff102c  count 0",
            "  7mfk   no L0 access of ffff102c",
            "  jk00c  no L0 access of ffff1034",
            "  jk78c  no symbol and no status"])

    def test_over_one_layout_the_requirements_of_other_targets_drop(self):
        store = FeatureStore()
        _, required = read.dependents(store, {"load_index/ram"}, "7mfk")
        self.assertEqual(required, [("bundle/feature", "can_telemetry/feature", None),
                                    ("can_telemetry/feature", "index_raw/field", None)])
        _, required = read.dependents(store, {"load_index/ram"}, "jk00c")
        self.assertIn(("definitions/feature", "load_index/ram", ["jk00c", "jk78c"]), required)

    def test_a_field_reads_its_role_its_symbol_or_the_status_of_its_source(self):
        answer = self.impact("load_raw/field")
        self.assertEqual(answer.text().splitlines()[0],
                         "impact of load_raw/field: 2 features, 1 signal")
        self.assertEqual(answer.data["signals"], ["load/signal"])
        self.assertEqual(answer.data["insertion_points"], [
            "  1nd    unavailable: load/ram unresolved  masked-match  7mfk:ffff102c  count 0",
            "  7mfk   load/ram/7mfk-ffff102c",
            "  jk00c  load/ram/jk00c-ffff1034",
            "  jk78c  load_proxy/ram/jk78c-ffff22f8 fills can_telemetry.load_raw"])

    def test_an_allocation_moves_by_the_runtime_where_no_target_states_it(self):
        self.assertEqual(self.impact("phase/field").data["insertion_points"], [
            "  1nd    rolling_launch.phase at ffff0c40, 1 byte  [derived] ram_delta -0x5100",
            "  7mfk   rolling_launch.phase at ffff5d40, 1 byte",
            "  jk00c  rolling_launch.phase at ffff6040, 1 byte",
            "  jk78c  rolling_launch.phase at ffff0c40, 1 byte  [derived] ram_delta -0x5100"])
        self.assertEqual(self.impact("phase/field", "jk78c").data["insertion_points"], [
            "  jk78c  rolling_launch.phase at ffff0c40, 1 byte  [derived] ram_delta -0x5100"])

    def test_a_feature_states_its_target_and_hook_sites_on_every_layout(self):
        answer = self.impact("can_telemetry/feature")
        self.assertEqual(answer.data["features"], [
            {"feature": "bundle/feature", "requires": "can_telemetry/feature", "layouts": None}])
        self.assertEqual(answer.data["insertion_points"][:4], [
            "  1nd    supported",
            "  1nd    snapshot at snapshot_call/hook, which has no symbol  replacement 000d4280",
            "  7mfk   supported",
            "  7mfk   snapshot at snapshot_call/hook/7mfk-00028090  replacement 000d4280"])
        self.assertEqual(self.impact("rolling_launch/feature").data["insertion_points"], [
            "  1nd    no target", "  7mfk   supported; no hook", "  jk00c  supported; no hook",
            "  jk78c  no target"])
        self.assertEqual(self.impact("runtime/feature").data["insertion_points"][1],
                         "  7mfk   supported; ROM 000d2108..000d6000; RAM ffff5d00..ffff6000; "
                         "no hook")


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
            "symbols": [sym(name, kind, 0x1000 + len(name))], "designed": False}


def designed(slug, kind, title=None, summary=None):
    return {"key": f"{slug}/{kind}", "name": slug, "kind": kind, "home": None, "title": title,
            "summary": summary, "former": [], "symbols": [], "designed": True}


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

    def test_designed_entities_rank_with_the_meanings(self):
        rows = [meaning("knock_threshold", "ram"),
                designed("knock", "block", title="Knock detection"),
                designed("knock_margin", "signal", title="Minimum knock threshold margin")]
        found = read.find(FindStore(rows), ["knock", "threshold"]).data
        self.assertEqual([(item.get("meaning"), item.get("entity"))
                          for item in found["results"]],
                         [("knock_threshold/ram", None), (None, "knock_margin/signal"),
                          (None, "knock/block")])

    def test_close_scores_mark_the_query_ambiguous(self):
        rows = [meaning("idle_speed_target", "ram"), meaning("idle_speed_limit", "ram")]
        lines = read.find(FindStore(rows), ["idle"]).lines()
        self.assertIn("ambiguous: 2 matches score within 10 percent of the first", lines)


class AllocationStore:
    """The `rolling_launch` allocations of `7mfk` as `allocations_at` reads them."""

    def run(self, query, **params):
        if "t.allocations" not in query or params["layout"] != "7mfk":
            return []
        return [{"feature": "rolling_launch", "allocations": {
            "phase_abort_reason": {"address": "ffff5d40", "width": 2},
            "rolling_launch_abort_reason": {"address": "ffff5d41", "width": 1}}}]


class AllocationTest(unittest.TestCase):
    def test_an_address_lies_in_every_allocation_that_spans_it(self):
        store = AllocationStore()
        self.assertEqual(read.allocations_at(store, "7mfk", 0xFFFF5D41),
                         [("rolling_launch.phase_abort_reason", 0xFFFF5D40, 2),
                          ("rolling_launch.rolling_launch_abort_reason", 0xFFFF5D41, 1)])
        self.assertEqual(read.allocations_at(store, "7mfk", 0xFFFF5D42), [])
        self.assertEqual(read.allocations_at(store, "jk00d", 0xFFFF5D40), [])


class StepTest(unittest.TestCase):
    def test_a_step_reads_with_its_chain_from_a_meaning_and_with_via_in_its_chain(self):
        row = {"chain": "engine_speed/chain", "order": 4, "from": "tooth_time/ram",
               "to": "rpm_12_5/ram", "effect": "converts", "sign": "negative",
               "via": ["rpm_12_5_producer/fn"], "note": "floor(0xA2C2 / ffff22bc)"}
        self.assertEqual(read.step_text(row, chain=True),
                         "engine_speed/chain #4  tooth_time/ram -> rpm_12_5/ram  "
                         "converts negative  floor(0xA2C2 / ffff22bc)")
        self.assertEqual(read.step_text(row),
                         "#4  tooth_time/ram -> rpm_12_5/ram  converts negative  "
                         "via rpm_12_5_producer/fn  floor(0xA2C2 / ffff22bc)")


class RoleStore:
    """The `fuel_inhibit` roles of `rolling_launch` as `roles_of` reads them."""

    def run(self, query, **params):
        if "[:HAS]" in query:
            return [{"key": f"{layout}-{address:08x}/ram"} for layout, address in
                    (("1nd", 0xFFFE92E4), ("7mfk", 0xFFFF22E0))
                    if params["key"] == "fuel_inhibit_mask/ram"]
        role = {"symbol": "fuel_inhibit_mask/ram", "note": "the final mask"}
        return [{"feature": "rolling_launch", "layout": layout,
                 "roles": {"fuel_inhibit": role}} for layout in ("1me3b", "1nd", "jk78c")]


class RoleTest(unittest.TestCase):
    def test_a_role_reads_from_the_meaning_that_fills_it_and_from_its_name(self):
        store = RoleStore()
        mask = read.roles_of(store, {"key": "fuel_inhibit_mask/ram", "name": "fuel_inhibit_mask"})
        state = read.roles_of(store, {"key": "fuel_inhibit/ram", "name": "fuel_inhibit"})
        self.assertEqual([read.role_text(row) for row in mask],
                         ["fills rolling_launch.fuel_inhibit on 1me3b, 1nd, jk78c"])
        self.assertEqual([read.role_text(row) for row in state],
                         ["rolling_launch.fuel_inhibit on 1me3b, 1nd, jk78c is "
                          "fuel_inhibit_mask/ram"])
        self.assertEqual(read.roles_of(store, {"key": "rpm/ram", "name": "rpm"}), [])



class GapStore:
    """Required meanings without a symbol: two telemetry sources of 1nd, one
    with a search and one absent, and one meaning a symbol of the family
    requires on jk00c."""

    L0 = "0123456789abcdef"
    FEATURE = [
        {"feature": "can_telemetry", "layout": "1nd", "field": "normalized_load_raw/field",
         "meaning": "normalized_load/ram", "current": L0, "status": {
             "state": "unresolved", "method": "masked-match", "target": "7mfk:0003bd1c",
             "count": 0, "l0": L0}},
        {"feature": "can_telemetry", "layout": "1nd", "field": "knock_timing_state_raw/field",
         "meaning": "knock_timing_state/ram", "current": L0, "status": {
             "state": "absent", "evidence": [{"kind": "registry"}, {
                 "kind": "l0", "supports": "identity", "at": "1nd:0004d464"}]}},
        {"feature": "can_telemetry", "layout": "jk78c", "field": "request_flow_raw/field",
         "meaning": "request_flow/ram", "current": "fedcba9876543210", "status": {
             "state": "unresolved", "method": "trace", "target": "request_flow/ram/7mfk",
             "count": 0, "l0": L0}},
    ]
    FAMILY = [{"feature": "family", "layout": "jk00c", "field": None,
               "meaning": "astute-toad/tbl", "current": L0,
               "status": {"state": "unknown", "required": ["family"]}}]

    def run(self, query, **params):
        if "slug: $feature" in query:
            return [{"key": "can_telemetry/feature"}] if params["feature"] == "can_telemetry" \
                else []
        rows = self.FEATURE if ":REQUIRES]" in query else self.FAMILY
        return [dict(row) for row in rows if params.get("layout") in (None, row["layout"])
                and params.get("feature") in (None, row["feature"])]


class GapsTest(unittest.TestCase):
    def test_a_feature_on_a_layout_lists_its_fields_by_status(self):
        answer = read.gaps(GapStore(), "can_telemetry", "1nd")
        self.assertEqual(answer.text(), (
            "can_telemetry on 1nd: 2 required meanings without a symbol\n"
            "unresolved: 1\n"
            "  normalized_load_raw/field  normalized_load/ram  masked-match  7mfk:0003bd1c  "
            "count 0\n"
            "absent: 1\n"
            "  knock_timing_state_raw/field  knock_timing_state/ram  l0  1nd:0004d464\n"))

    def test_without_a_feature_the_family_requirements_follow_and_a_stale_search_says_so(self):
        answer = read.gaps(GapStore())
        lines = answer.text().splitlines()
        self.assertEqual(lines[0], "4 required meanings without a symbol on 3 layouts "
                                   "(can_telemetry 3, family 1)")
        self.assertEqual(lines[1:3], ["unknown: 1", "  jk00c   family  astute-toad/tbl"])
        self.assertIn("  jk78c   can_telemetry  request_flow_raw/field  request_flow/ram  trace  "
                      "request_flow/ram/7mfk  count 0  stale", lines)
        self.assertEqual([gap["state"] for gap in answer.data["gaps"]],
                         ["absent", "unresolved", "unresolved", "unknown"])

    def test_an_unknown_feature_names_the_search(self):
        with self.assertRaises(read.KbError) as missing:
            read.gaps(GapStore(), "launch_control")
        self.assertEqual(missing.exception.code, 5)


class BriefStore(GapStore):
    uri = "bolt://fixture"

    def __init__(self, rows=None, family=None, degrees=None):
        self.FEATURE = self.FEATURE if rows is None else rows
        self.FAMILY = self.FAMILY if family is None else family
        self.degrees = degrees or {}

    def run(self, query, **params):
        if ":REQUIRES]" in query or "$family IN r.required" in query:
            return super().run(query, **params)
        if "count(r) AS degree" in query:
            return [{"key": key, "degree": self.degrees.get(key, 0)} for key in params["keys"]]
        if "RETURN m" in query and ":Meta" in query:
            return [{"m": {"fingerprint": "fixture", "commit": "fixture"}}]
        if "count(c) AS n" in query:
            return [{"n": 0}]
        if "r.state AS state" in query:
            grouped = {}
            unique = {(row["meaning"], row["layout"]): row
                      for row in self.FEATURE + self.FAMILY}
            for row in unique.values():
                key = row["layout"], (row["status"] or {}).get("state", "unknown")
                grouped[key] = grouped.get(key, 0) + 1
            return [{"layout": layout, "state": state, "n": count}
                    for (layout, state), count in grouped.items()]
        if "state: 'unresolved'" in query:
            return [{"key": row["meaning"], "layout": row["layout"],
                     "l0": row["status"].get("l0"), "current": row["current"]}
                    for row in self.FEATURE + self.FAMILY
                    if (row["status"] or {}).get("state") == "unresolved"]
        return []


class BriefTest(unittest.TestCase):
    def brief(self, source):
        with mock.patch.object(read.repo, "layouts", return_value={
                key: mock.Mock(family="fixture") for key in ("1nd", "jk78c", "jk00c")}), \
                mock.patch.object(read, "bench", return_value={"question": []}), \
                mock.patch.object(read.spec, "table", return_value=[]):
            return read.brief(source)

    def test_totals_equal_gaps_when_all_missing_bindings_are_unresolved_or_absent(self):
        source = BriefStore(family=[])
        full = read.gaps(source)
        brief = self.brief(source)
        self.assertEqual(brief.data["gaps"], full.data["gaps"])
        self.assertEqual(brief.data["gap_summary"], full.data["gap_summary"])
        self.assertEqual(brief.data["gap_summary"]["states"],
                         {"unknown": 0, "unresolved": 2, "absent": 1})
        self.assertIn("open gaps: 3 required meanings without a symbol on 2 layouts\n",
                      brief.text())
        self.assertIn("  by feature: can_telemetry 3\n", brief.text())
        self.assertIn("  by layout: 1nd 2, jk78c 1\n", brief.text())
        self.assertIn("  by state: unknown 0, unresolved 2, absent 1\n", brief.text())

    def test_feature_impact_precedes_degree_and_the_sample_keeps_complete_totals(self):
        row = GapStore.FEATURE[0]
        rows = [{**row, "meaning": "multi/ram"},
                {**row, "meaning": "multi/ram", "feature": "definitions", "field": None}]
        rows += [{**row, "meaning": f"single_{n}/ram", "feature": "definitions", "field": None}
                 for n in range(6)]
        degrees = {f"single_{n}/ram": 1000 for n in range(6)}
        degrees["astute-toad/tbl"] = 9999
        source = BriefStore(rows, degrees=degrees)
        answer = self.brief(source)
        self.assertEqual(answer.data["gap_summary"], read.gaps(source).data["gap_summary"])
        self.assertEqual(answer.data["gap_summary"]["total"], 9)
        self.assertEqual(len(answer.data["gaps"]), 9)
        ranked = answer.data["gap_priorities"]
        self.assertEqual(len(ranked), 5)
        self.assertEqual(ranked[0]["meaning"], "multi/ram")
        self.assertEqual(ranked[0]["features"], ["can_telemetry", "definitions"])
        self.assertEqual(ranked[0]["fields"], ["normalized_load_raw/field"])
        self.assertNotIn("astute-toad/tbl", [item["meaning"] for item in ranked])


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


class RawStore:
    """The symbols of one meaning as `kb raw` reads them."""

    def __init__(self, symbols):
        self.symbols = symbols

    def run(self, query, **params):
        if "-[:HAS]->(s:Kb:Symbol)" in query:
            return [{"s": node} for node in self.symbols]
        return []


class RawTest(unittest.TestCase):
    """A meaning whose file states its home symbol on 7mfk and whose symbol
    on 1nd a registry of curated names states."""

    FILE = 'name = "demo"\nkind = "fn"\n\n[[symbol]]\nlayout = "7mfk"\naddress = 0xc338a\n'
    MEANING = {"key": "demo/fn", "kind": "fn", "home": "7mfk",
               "src": ["kb/fn/demo.toml", "tools/ghidra/symbols/1nd.csv"]}
    HOME = {"name": "demo", "kind": "fn", "layout": "7mfk", "address": 0xC338A,
            "src": ["kb/fn/demo.toml"]}
    CURATED = {"name": "demo", "kind": "fn", "layout": "1nd", "address": 0x11363C,
               "src": ["tools/ghidra/symbols/1nd.csv"]}

    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name)
        for name, text in {
                "kb/fn/demo.toml": self.FILE,
                "kb/names.csv": "layout,kind,address,name,former\n"
                                "7mfk,ram,000c338a,other-name,\n1nd,fn,0011363c,old-name,\n",
                "tools/ghidra/symbols/1nd.csv": "# Curated function names\naddr,name,note\n"
                                                "0011363c,demo,init\n00200000,next,\n"}.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")

    def raw(self, ref):
        store = RawStore([self.HOME, self.CURATED])
        with mock.patch.object(read.refs, "resolve", lambda graph, text, root: ref):
            return read.raw(store, "demo", self.root)

    def test_a_meaning_shows_its_file_and_the_registry_rows_of_its_symbols(self):
        answer = self.raw(Ref("meaning", self.MEANING))
        self.assertEqual(answer.data["files"], {"kb/fn/demo.toml": self.FILE})
        self.assertEqual(answer.data["records"], [
            "  kb/names.csv:1: layout,kind,address,name,former",
            "  kb/names.csv:3: 1nd,fn,0011363c,old-name,",
            "  tools/ghidra/symbols/1nd.csv:2: addr,name,note",
            "  tools/ghidra/symbols/1nd.csv:3: 0011363c,demo,init"])
        lines = answer.text().splitlines()
        self.assertEqual(lines[:3], ["demo/fn", "--- kb/fn/demo.toml", 'name = "demo"'])
        self.assertIn("--- registry rows", lines)

    def test_a_symbol_shows_the_file_of_its_meaning_and_its_own_rows(self):
        answer = self.raw(Ref("symbol", self.HOME, self.MEANING, "7mfk", 0xC338A))
        self.assertEqual(answer.data["ref"], "demo/fn/7mfk-000c338a")
        self.assertEqual(answer.data["files"], {"kb/fn/demo.toml": self.FILE})
        self.assertEqual(answer.data["records"], [])

    def test_a_record_without_file_or_row_says_so(self):
        lone = {"name": "lone", "kind": "ram", "layout": "7mfk", "address": 0xFFFF8000,
                "src": []}
        answer = self.raw(Ref("symbol", lone, {"key": "lone/ram", "src": []}, "7mfk",
                              0xFFFF8000))
        self.assertEqual(answer.text().splitlines(),
                         ["lone/ram/7mfk-ffff8000", "  no file or registry row states it"])

    def test_a_location_holds_no_record(self):
        with self.assertRaises(KbError) as location:
            self.raw(Ref("location", layout="7mfk", address=0x8000))
        self.assertEqual(location.exception.code, 5)


if __name__ == "__main__":
    unittest.main()
