import unittest
from unittest.mock import patch

from kb import checks, compile, levels, match, repo, vocab
from kb.model import Builder, SymbolKey

CANDIDATE, CODE, SILICON = (vocab.LEVEL_RANK[level] for level in ("candidate", "code", "silicon"))
# A function entry of the builder and an address where no function starts.
ENTRY, INSIDE = 0xC7914, 0xC7916
# The DID pointer table entry of 7MFK at 000229c8 holds ffff285c, which no L0
# reference names.
DID, SOURCE = 0x229C8, 0xFFFF285C
RAM = 0xFFFF1000
L0 = {"kind": "l0", "supports": "identity", "at": f"7mfk:{ENTRY:08x}"}
REGISTRY = {"kind": "registry", "supports": "identity", "path": "defs/JK08A.vars.csv"}


def model_of(declare):
    b = Builder(repo.layouts(), compile.spaces(repo.config()), {"7mfk": frozenset({ENTRY})}, {})
    declare(b)
    model = b.finish()
    model.root, model.config, model.functions = repo.ROOT, repo.config(), b.functions
    return model


def datum(b, address, level, evidence=(L0,), src="test", layout="7mfk", **props):
    """A `ram` symbol of its own meaning at `level`."""
    key = b.symbol(layout, "ram", address, src, group=("ram", address), evidence=list(evidence))
    b.props(key, {"level": level, **props}, src)
    return key


def function(b, address, level="code"):
    key = b.symbol("7mfk", "fn", address, "test", group=("fn", address), evidence=[L0])
    b.props(key, {"level": level, "role": "consumer"}, "test")
    return key


def messages(model):
    return {issue.subject: issue.message for issue in levels.check(model)}


class EquationTest(unittest.TestCase):
    def test_an_equation_holds_at_the_places_of_its_right_side(self):
        for value in ("16*50331*100000/(12.5*2^32)=1.49998", "6/1.49998=4.00005",
                      "(1+2)*-3=-9", "2^-2=0.25", "1/3=0.33", "1/3=0.3333"):
            with self.subTest(value=value):
                self.assertIsNone(levels.equation(value))
        self.assertEqual(levels.equation("1/3=0.34"),
                         "does not hold: the left side is 0.333333333333")
        self.assertEqual(levels.equation("1/3=0.334"),
                         "does not hold: the left side is 0.333333333333")

    def test_the_grammar_is_numbers_operators_and_parentheses(self):
        self.assertEqual(levels.evaluate("2*3+4*5"), 26)
        self.assertEqual(levels.evaluate("2^3^2"), 512)
        self.assertEqual(levels.evaluate("-2^2"), -4)
        self.assertEqual(levels.evaluate("1/(2^32)*2^32"), 1)
        for value, failure in (
                ("x+1=2", "does not evaluate: character 'x'"),
                ("1/0=1", "does not evaluate: division by zero"),
                ("2^0.5=1.41421", "does not evaluate: an exponent that is no integer"),
                ("(1+2=3", "does not evaluate: an unclosed parenthesis"),
                ("1+=2", "does not evaluate: a missing operand"),
                ("1 2=3", "does not evaluate: unexpected '2'"),
                ("1+2", "is no equation <expression>=<number>"),
                ("1=x", "is no equation <expression>=<number>")):
            with self.subTest(value=value):
                self.assertEqual(levels.equation(value), failure)


class HardwareTest(unittest.TestCase):
    RECORDS = {"feature": {"pass": {"hardware_status": "pass"},
                           "fail": {"hardware_status": "functional_fail"},
                           "capture": {"result": "observed"}}}

    def failure(self, key):
        return levels.item_failure({"kind": "hardware", "key": key}, self.RECORDS)

    def test_a_hardware_item_names_a_passing_record(self):
        self.assertIsNone(self.failure("feature.pass"))
        self.assertEqual(self.failure("feature.fail"),
                         "hardware evidence names feature.fail, whose hardware_status is "
                         "'functional_fail', not 'pass'")
        self.assertEqual(self.failure("feature.capture"),
                         "hardware evidence names feature.capture, whose hardware_status is "
                         "None, not 'pass'")
        for key in ("feature.missing", "feature.pass.hardware_status", None):
            with self.subTest(key=key):
                self.assertEqual(self.failure(key),
                                 f"hardware evidence names {key}, which is no record of "
                                 "patches/hardware-results.toml")

    def test_historical_hardware_records_do_not_require_a_current_record(self):
        item = {"kind": "hardware", "key": "git:archive-tag:records.toml#old_record"}
        self.assertIsNone(levels.item_failure(item, {}))
        self.assertEqual(match.rank(item), -1)

    def test_a_silicon_claim_rests_on_a_passing_record_of_the_repository(self):
        def declare(key):
            return lambda b: datum(b, RAM, "silicon", evidence=[
                {"kind": "hardware", "supports": "identity", "key": key}])
        self.assertEqual(messages(model_of(declare("immo.developer_flag"))), {})
        found = [issue.message for issue in levels.check(model_of(declare("map_switching.marker")))]
        self.assertEqual(found, [
            "hardware evidence names map_switching.marker, whose hardware_status is None, "
            "not 'pass'",
            "the identity level silicon lacks grounding: its evidence grounds no level"])


class ClaimTest(unittest.TestCase):
    def test_archived_test_claims_remain_candidates_and_keep_other_grounding(self):
        archive = {"kind": "test", "supports": "identity",
                   "path": "git:archive/stock-proofs-2026-10-26:absent/test_case.py",
                   "key": "test_case"}
        for other, expected in (([], "candidate"), ([L0], "code")):
            with self.subTest(other=other):
                model = model_of(lambda b: datum(b, RAM, "code", evidence=[archive, *other]))
                result = levels.analyze(model)
                claim = next(claim for claim in result.claims if claim.name == "identity")
                self.assertEqual(result.level(claim), expected)
                self.assertIn(archive, model.symbols[SymbolKey("7mfk", "ram", RAM)].evidence)

    def test_indirect_metadata_alone_does_not_hold_a_storage_object(self):
        item = {"kind": "indirect", "mode": "optional-domain-access", "at": "7mfk:00000000"}
        model = model_of(lambda b: datum(b, RAM, "code", evidence=[item]))
        symbol = model.symbols[SymbolKey("7mfk", "ram", RAM)]
        with patch.object(levels.sites, "referenced", return_value=set()):
            self.assertFalse(levels.held(model, symbol))

    def test_retained_access_evidence_cannot_borrow_a_functions_existence(self):
        test = {"kind": "test", "path": "tools/kb/tests/test_tokens.py",
                "key": "test_a_dependency_names_address_offset_and_property"}
        cases = (
            ({"kind": "indirect", "supports": "identity", "mode": "optional-domain-access",
              "at": f"7mfk:{ENTRY:08x}"}, "candidate"),
            (test, "candidate"),
            ({**test, "supports": "scale"}, "candidate"),
            ({**test, "supports": "identity"}, "code"),
        )
        for item, expected in cases:
            with self.subTest(item=item):
                def declare(b):
                    ram = datum(b, RAM, "code", evidence=())
                    b.link(ram, "reader", function(b, ENTRY), "test",
                           props={"relies": "structure"}, evidence=[item])

                model = model_of(declare)
                result = levels.analyze(model)
                claim = next(claim for claim in result.claims if claim.subject == "7mfk-ffff1000/ram")
                self.assertEqual(result.level(claim), expected)
                self.assertEqual(result.effective[id(claim)], CODE)

    def test_a_candidate_claim_needs_evidence_and_a_code_claim_grounding(self):
        def declare(b):
            datum(b, RAM, "candidate", evidence=())
            datum(b, RAM + 2, "candidate", evidence=[REGISTRY])
            datum(b, RAM + 4, "code", evidence=[REGISTRY])
            datum(b, RAM + 6, "code", evidence=())
            datum(b, RAM + 8, "code")
        self.assertEqual(messages(model_of(declare)), {
            "7mfk-ffff1000/ram": "the identity level candidate lacks evidence",
            "7mfk-ffff1004/ram": "the identity level code lacks grounding: its evidence grounds "
                                 "candidate",
            "7mfk-ffff1006/ram": "the identity level code lacks grounding: its evidence grounds "
                                 "no level"})

    def test_an_arithmetic_item_that_does_not_hold_grounds_nothing(self):
        def declare(value):
            def run(b):
                datum(b, RAM, "code", evidence=[
                    L0, {"kind": "arithmetic", "supports": "scale", "value": value}],
                    scale="x/200", scale_level="code")
            return run
        self.assertEqual(messages(model_of(declare("1000/200=5"))), {})
        found = [issue.message for issue in levels.check(model_of(declare("1000/200=6")))]
        self.assertEqual(found, [
            "arithmetic evidence 1000/200=6 does not hold: the left side is 5",
            "the scale level code lacks grounding: its evidence grounds no level"])

    def test_an_owned_symbol_of_another_layout_takes_the_level_of_its_meaning(self):
        def declare(src):
            def run(b):
                home = datum(b, RAM, "code", src="kb/ram/probe.toml")
                b.symbol("jk00d", "ram", RAM + 0x10, src, group=("ram", RAM),
                         evidence=[{**REGISTRY, "path": "defs/JK00D.vars.csv"}])
                return home
            return run
        self.assertEqual(messages(model_of(declare("kb/ram/probe.toml"))), {
            "jk00d-ffff1010/ram": "the identity level code lacks grounding: its evidence grounds "
                                  "candidate"})
        self.assertEqual(messages(model_of(declare("defs/JK00D.vars.csv"))), {})


class DependencyTest(unittest.TestCase):
    def test_the_structure_of_an_l0_function_entry_does_not_bound(self):
        def declare(address):
            def run(b):
                ram = datum(b, RAM, "silicon", evidence=[
                    {"kind": "hardware", "supports": "identity", "key": "immo.developer_flag"}])
                b.link(ram, "reader", function(b, address), "test", props={"relies": "structure"})
            return run
        self.assertEqual(messages(model_of(declare(ENTRY))), {})
        self.assertEqual(messages(model_of(declare(INSIDE))), {
            "7mfk-ffff1000/ram": "the identity level silicon exceeds its effective level "
                                 "pattern: it rests on the structure of 7mfk-000c7916/fn, which "
                                 "neither L0 nor a DID table references (reader link)"})

    def test_a_did_table_entry_holds_its_source(self):
        def declare(entry):
            def run(b):
                fn = function(b, ENTRY)
                source = datum(b, SOURCE, "code")
                b.link(fn, "reader", source, "test", props={"relies": "structure"})
                if entry:
                    did = b.symbol("7mfk", "did", DID, "test", group=("did", DID), evidence=[{
                        "kind": "did-table", "supports": "identity", "at": f"7mfk:{DID:08x}",
                        "value": f"{SOURCE:08x}"}])
                    b.link(did, "source", source, "test", props={"offset": 0})
            return run
        self.assertEqual(messages(model_of(declare(True))), {})
        self.assertEqual(messages(model_of(declare(False))), {
            "7mfk-000c7914/fn": "the identity level code exceeds its effective level pattern: it "
                                "rests on the structure of 7mfk-ffff285c/ram, which neither L0 "
                                "nor a DID table references (reader link)"})

    def test_a_chain_ends_at_the_claim_that_keeps_its_declared_level(self):
        def declare(b):
            first, second, third = (datum(b, RAM + offset, level) for offset, level in
                                    ((0, "code"), (2, "code"), (4, "candidate")))
            b.link(first, "input", second, "test", props={"relies": "level"})
            b.link(second, "input", third, "test", props={"relies": "level"})
        self.assertEqual(messages(model_of(declare)), {
            "7mfk-ffff1000/ram": "the identity level code exceeds its effective level candidate: "
                                 "it rests on the level of 7mfk-ffff1002/ram (input link); the "
                                 "chain ends at 7mfk-ffff1004/ram, declared candidate",
            "7mfk-ffff1002/ram": "the identity level code exceeds its effective level candidate: "
                                 "it rests on the level of 7mfk-ffff1004/ram (input link), "
                                 "declared candidate"})

    def test_a_cycle_takes_the_minimum_of_its_members(self):
        def declare(bounded):
            def run(b):
                first, second = datum(b, RAM, "code"), datum(b, RAM + 2, "code")
                b.link(first, "input", second, "test", props={"relies": "level"})
                b.link(second, "input", first, "test", props={"relies": "level"})
                if bounded:
                    b.link(second, "input", datum(b, RAM + 4, "candidate"), "test",
                           props={"relies": "level"})
            return run
        self.assertEqual(messages(model_of(declare(False))), {})
        found = levels.analyze(model_of(declare(True)))
        self.assertEqual(sorted(found.effective.values()), [CANDIDATE] * 3)
        self.assertEqual(messages(model_of(declare(True)))["7mfk-ffff1000/ram"],
                         "the identity level code exceeds its effective level candidate: it "
                         "rests on the level of 7mfk-ffff1002/ram (input link); the chain ends "
                         "at 7mfk-ffff1004/ram, declared candidate")

    def test_a_dependency_grounds_up_to_code(self):
        def declare(level):
            def run(b):
                ram = datum(b, RAM, level, evidence=())
                b.link(ram, "input", datum(b, RAM + 2, "silicon", evidence=[
                    {"kind": "hardware", "supports": "identity", "key": "immo.developer_flag"}]),
                    "test", props={"relies": "level"})
            return run
        self.assertEqual(messages(model_of(declare("code"))), {})
        self.assertEqual(messages(model_of(declare("silicon"))), {
            "7mfk-ffff1000/ram": "the identity level silicon lacks grounding: its evidence "
                                 "grounds code"})

    def test_a_reverse_dependency_bounds_the_end_that_the_link_names(self):
        def declare(b):
            ram, other = datum(b, RAM, "code"), datum(b, RAM + 2, "candidate")
            b.link(other, "input", ram, "test", props={"reverse_relies": "level"})
        self.assertEqual(messages(model_of(declare)), {
            "7mfk-ffff1000/ram": "the identity level code exceeds its effective level candidate: "
                                 "it rests on the level of 7mfk-ffff1002/ram (input link of "
                                 "7mfk-ffff1002/ram), declared candidate"})


class InterpolationIdentityTest(unittest.TestCase):
    ENTRIES = (0x26740, 0x26984, 0x26A60, 0x26AF8, 0x26B84, 0x26C1C)

    @classmethod
    def setUpClass(cls):
        cls.model = compile.cached()
        cls.homes = [cls.model.symbols[SymbolKey("7mfk", "fn", address)]
                     for address in cls.ENTRIES]
        cls.symbols = [symbol for home in cls.homes
                       for symbol in home.meaning.symbols.values()]

    def test_each_home_entry_supports_identity_not_only_the_contract(self):
        for symbol in self.homes:
            with self.subTest(address=symbol.address):
                self.assertIn(symbol.address, self.model.functions["7mfk"])
                self.assertTrue(any(item.get("kind") in ("l0", "l0-context")
                                    and item.get("supports") == "identity"
                                    and item.get("at") == f"7mfk:{symbol.address:08x}"
                                    for item in symbol.evidence))

    def test_the_home_identity_grounds_every_homologous_symbol(self):
        keys = [symbol.key for symbol in self.symbols]
        ranks = match.grounded(self.model, keys)
        for key in keys:
            with self.subTest(symbol=key.key):
                self.assertGreaterEqual(ranks[key][0], CODE)

    def test_contract_evidence_alone_does_not_ground_the_identity(self):
        broken = compile.build()
        for home in self.homes:
            symbol = broken.symbols[home.key]
            symbol.evidence[:] = [item for item in symbol.evidence
                                  if item.get("supports", "identity") != "identity"]
        # Ledger links supply independent structural identity routes. The
        # negative fixture retains only the interpolation contract route.
        homes = {broken.symbols[home.key].meaning for home in self.homes}
        links = [link for link in broken.links if link.owner not in homes and link.to not in homes]
        broken.links[:] = links
        for meaning in broken.meanings:
            meaning.links[:] = [link for link in meaning.links if link in links]
        subjects = {f"{home.meaning.name}/fn" for home in self.homes}
        subjects.update(symbol.key.key for symbol in self.symbols
                        if symbol.layout != "7mfk")
        missing = {issue.subject for issue in levels.check(broken)
                   if "identity level code lacks grounding" in issue.message}
        self.assertTrue(subjects <= missing)


class MailboxIdentityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = compile.cached()
        cls.address = 0xFFFFD800 + 0x108 + 26 * 0x20
        cls.symbols = cls.model.symbols[SymbolKey("7mfk", "reg", cls.address)].meaning.symbols

    def test_each_layout_cites_the_joint_manual_for_register_identity(self):
        self.assertEqual(set(self.symbols), set(self.model.layouts))
        for layout, symbol in self.symbols.items():
            with self.subTest(layout=layout):
                self.assertEqual(symbol.address, self.address)
                items = [item for item in symbol.evidence
                         if item.get("kind") == "manual"
                         and item.get("supports") == "identity"]
                self.assertTrue(items)
                for item in items:
                    self.assertEqual(item["key"], "SH7058S-HW-17.3.3")
                    self.assertNotIn("to", item)
                    self.assertEqual(match.rank(item, symbol, self.model), CODE)

    def test_manual_homology_stays_distinct_from_direct_identity(self):
        for layout, symbol in self.symbols.items():
            if layout == "7mfk":
                continue
            with self.subTest(layout=layout):
                items = [item for item in symbol.evidence
                         if item.get("supports") == "homology"]
                self.assertTrue(items)
                for item in items:
                    self.assertEqual(item["kind"], "manual")
                    self.assertEqual(item["to"], f"7mfk:{self.address:08x}")
                    self.assertEqual(match.rank(item, symbol, self.model), CANDIDATE)

    def test_manual_homology_alone_does_not_ground_code_identity(self):
        broken = compile.build()
        keys = [symbol.key for layout, symbol in self.symbols.items() if layout != "7mfk"]
        for key in keys:
            symbol = broken.symbols[key]
            symbol.evidence[:] = [item for item in symbol.evidence
                                  if item.get("supports") != "identity"]
        missing = {issue.subject for issue in levels.check(broken)
                   if "identity level code lacks grounding" in issue.message}
        self.assertTrue({key.key for key in keys} <= missing)


class AuditTest(unittest.TestCase):
    def test_levels_are_a_mandatory_model_gate(self):
        model = model_of(lambda b: datum(b, RAM, "candidate", evidence=()))
        self.assertIn("levels", checks.CHECKS)
        self.assertEqual(checks.CHECKS["levels"](model), levels.check(model))
        self.assertTrue(checks.CHECKS["levels"](model))

    def test_the_audit_computes_the_sections_it_is_asked_for(self):
        model = model_of(lambda b: datum(b, RAM, "candidate", evidence=()))
        self.assertEqual(list(checks.audit(model)), list(checks.AUDIT_SECTIONS))
        self.assertEqual(checks.audit(model, ("names",)), {"names": []})
        self.assertEqual([issue.message for issue in checks.audit(model, ("levels",))["levels"]],
                         ["the identity level candidate lacks evidence"])


if __name__ == "__main__":
    unittest.main()
