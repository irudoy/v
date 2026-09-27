import tempfile
import unittest
from pathlib import Path

from kb import checks, compile, derive, match, names, repo, store
from kb.adapters import files
from kb.model import Builder, SymbolKey

APC_7MFK, APC_JK00D, APC_FORMER = 0xFFFF2022, 0xFFFF11F5, 0xFFFF206C
APC_STORE, APC_REGION, APC_MATCH = 0x4E070, 0x4E066, 0x4F9B0
HOOK, HOOK_TARGET = 0x203A0, 0xC7914
DID, DID_WORDS = 0x229E8, "ffff3346 00011e45"


def code_of(program, pools, layout="a", gram=4):
    """A Code of one function at the lowest address of `program`."""
    data = bytearray(0x400)
    for address, word in program.items():
        data[address:address + 2] = word.to_bytes(2, "big")
    for address, raw in pools:
        data[address:address + len(raw)] = raw
    data = bytes(data)
    body = sorted(program)
    pairs = derive.function_pairs(body[0], body, data)
    functions = {body[0]: match.Function(body[0], 2 * len(body), len(body), ("x", "m", "s"))}
    return match.Code(layout, data, {body[0]: body}, functions, (), pairs, (), gram)


def shifted(program, offset, pool_words=None):
    """The program at `offset` bytes higher, with the words of `pool_words`."""
    return {address + offset: (pool_words or {}).get(address, word)
            for address, word in program.items()}


# mov.l @(pool),r1; mov.b @(3,r1),r0; or #0x40,r0; mov.b r0,@(3,r1); four
# distinct fillers; rts; nop.
PROGRAM = {0x100: 0xD107, 0x102: 0x8413, 0x104: 0xCB40, 0x106: 0x8013, 0x108: 0x6103,
           0x10A: 0x7201, 0x10C: 0x7302, 0x10E: 0x7403, 0x110: 0x000B, 0x112: 0x0009}


# bsr 0x120; nop; bsr 0x124; nop; rts; nop.
CALLS = {0x100: 0xB00E, 0x102: 0x0009, 0x104: 0xB00E, 0x106: 0x0009, 0x108: 0x000B,
         0x10A: 0x0009}
# Functions of 7MFK and JK00D that one hash pairs uniquely on both layouts.
EXACT, MNEMONIC = (0x1400, 0x1400), (0x21714, 0x21790)


def builder():
    return Builder(repo.layouts(), compile.spaces(repo.config()),
                   {"7mfk": frozenset({HOOK_TARGET, HOOK_TARGET + 2})}, {})


def model_of(declare):
    b = builder()
    declare(b)
    model = b.finish()
    model.root, model.config = repo.ROOT, repo.config()
    return model


class MaskTest(unittest.TestCase):
    def test_masking_clears_address_displacements_only(self):
        for word, expected in ((0xD107, 0xD100), (0x920E, 0x9200), (0x8B03, 0x8B00),
                               (0xC703, 0xC700), (0xC105, 0xC100), (0xB19A, 0xB000),
                               (0xA123, 0xA000), (0xCB40, 0xCB40), (0xC840, 0xC840),
                               (0x8466, 0x8466), (0xCD01, 0xCD01)):
            self.assertEqual(match.masked(word), expected, hex(word))


class AlignTest(unittest.TestCase):
    def setUp(self):
        self.home = code_of(PROGRAM, [(0x120, bytes.fromhex("ffff1000"))])
        # The copy loads its literal over another displacement from another pool.
        self.other = code_of(shifted(PROGRAM, 0x100, {0x100: 0xD10F}),
                             [(0x240, bytes.fromhex("ffff2000"))], layout="b")

    def test_touches_name_the_literal_and_the_accesses_through_it(self):
        self.assertEqual(self.home.touches(0x100), {(0xFFFF1000, "literal")})
        self.assertEqual(self.home.touches(0x106), {(0xFFFF1003, "store")})
        self.assertEqual(self.home.stores(0xFFFF1003), [0x106])
        self.assertEqual(self.home.ordinal(0x106), (0x100, 3))

    def test_a_unique_region_aligns_a_store_with_its_counterpart(self):
        region = self.home.aligned(0x106, self.other)
        self.assertEqual((region.start, region.match, region.words, region.offset),
                         (0x100, 0x200, 10, 3))
        self.assertEqual(self.other.touches(region.site), {(0xFFFF2003, "store")})

    def test_a_different_immediate_ends_the_region(self):
        other = code_of(shifted(PROGRAM, 0x100, {0x104: 0xCB08}),
                        [(0x220, bytes.fromhex("ffff2000"))], layout="b")
        region = self.home.aligned(0x106, other)
        self.assertEqual((region.start, region.match, region.words), (0x106, 0x206, 7))

    def test_a_repeated_region_aligns_nothing(self):
        twice = {**shifted(PROGRAM, 0x100), **shifted(PROGRAM, 0x180)}
        other = code_of(twice, [(0x220, bytes.fromhex("ffff2000")),
                                (0x2A0, bytes.fromhex("ffff2000"))], layout="b")
        regions = self.home.align(0x106, other)
        self.assertEqual([region.matches for region in regions], [2, 2])
        self.assertIsNone(self.home.aligned(0x106, other))

    def test_a_region_shorter_than_the_gram_aligns_nothing(self):
        other = code_of(shifted(PROGRAM, 0x100, {0x104: 0xCB08, 0x10A: 0x7209}),
                        [(0x220, bytes.fromhex("ffff2000"))], layout="b")
        self.assertIsNone(self.home.aligned(0x106, other))


    def test_calls_have_ordinals_among_the_calls_of_their_function(self):
        code = code_of(CALLS, [])
        self.assertEqual(code.touches(0x100), {(0x120, "call")})
        self.assertEqual(code.touches(0x104), {(0x124, "call")})
        self.assertEqual((code.call_ordinal(0x100), code.call_ordinal(0x104)),
                         ((0x100, 0), (0x100, 1)))
        self.assertIsNone(code.call_ordinal(0x102))


class FunctionMatchTest(unittest.TestCase):
    def model(self, *pairs):
        def declare(b):
            for number, (home, other) in enumerate(pairs):
                b.symbol("7mfk", "fn", home, "test", group=("fn", number))
                b.symbol("jk00d", "fn", other, "test", group=("fn", number))
        return model_of(declare)

    def verify(self, model, pair, **item):
        symbol = model.symbols[SymbolKey("jk00d", "fn", pair[1])]
        return match.verify(model, symbol, {
            "supports": "homology", "at": f"jk00d:{pair[1]:08x}", "to": f"7mfk:{pair[0]:08x}",
            **item})

    def test_a_unique_hash_pair_verifies(self):
        model = self.model(EXACT, MNEMONIC)
        self.assertIsNone(self.verify(model, MNEMONIC, kind="function-match", count=1,
                                      value="mnemonic"))
        self.assertIn("exact hashes", self.verify(model, MNEMONIC, kind="function-match",
                                                  count=1, value="exact"))
        self.assertIn("count 2", self.verify(model, EXACT, kind="function-match", count=2,
                                             value="exact"))

    def test_byte_identical_functions_carry_their_exact_hash(self):
        model = self.model(EXACT, MNEMONIC)
        digest = match.code("7mfk").functions[EXACT[0]].hashes[0]
        self.assertIsNone(self.verify(model, EXACT, kind="byte-identical", sha256=digest))
        self.assertIn("differ from sha256", self.verify(model, MNEMONIC, kind="byte-identical",
                                                        sha256=digest))

    def test_search_proposes_the_hash_pair(self):
        model = self.model(MNEMONIC)
        found = match.search(model, model.symbols[SymbolKey("7mfk", "fn", MNEMONIC[0])], "jk00d")
        best = max(found.candidates.values(), key=lambda candidate: candidate.votes)
        self.assertEqual(best.address, MNEMONIC[1])
        self.assertEqual((best.evidence["kind"], best.evidence["value"]),
                         ("function-match", "mnemonic"))


class ApcOutputTest(unittest.TestCase):
    """The apc_output binding of JK00D: the stock store of JK08A aligns with
    the store of ffff11f5, and the former binding ffff206c contradicts it."""

    def model(self, jk00d):
        def declare(b):
            b.symbol("7mfk", "ram", APC_7MFK, "test", group=("ram", "apc"))
            b.symbol("jk00d", "ram", jk00d, "test", group=("ram", "apc"))
        return model_of(declare)

    def test_the_stock_store_aligns_with_the_jk00d_store(self):
        home, other = match.code("7mfk"), match.code("jk00d")
        region = home.aligned(APC_STORE, other)
        self.assertEqual((region.start, region.match, region.words), (APC_REGION, APC_MATCH, 14))
        self.assertIn((APC_JK00D, "store"), other.touches(region.site))

    def test_the_writer_gate_rejects_the_former_binding(self):
        self.assertEqual(match.writers(self.model(APC_JK00D)), [])
        found = {item.site: item.message for item in match.writers(self.model(APC_FORMER))}
        self.assertIn("jk00d:0004f9ba, which stores ffff11f5, not ffff206c",
                      found.pop(f"7mfk:{APC_STORE:08x}"))
        # The stores of ffff206c align with the stores of ffff1ff4 on 7MFK.
        self.assertTrue(found)
        self.assertTrue(all(site.startswith("jk00d:") and "stores ffff1ff4, not ffff2022" in message
                            for site, message in found.items()))

    def test_search_finds_the_jk00d_counterpart(self):
        model = self.model(APC_JK00D)
        found = match.search(model, model.symbols[SymbolKey("7mfk", "ram", APC_7MFK)], "jk00d")
        best = max(found.candidates.values(), key=lambda candidate: candidate.votes)
        self.assertEqual(best.address, APC_JK00D)
        self.assertEqual(best.evidence["kind"], "masked-match")

    def test_masked_match_evidence_verifies_against_l0(self):
        item = {"kind": "masked-match", "supports": "homology", "at": f"jk00d:{APC_MATCH:08x}",
                "to": f"7mfk:{APC_REGION:08x}", "count": 1, "value": 14}
        model = self.model(APC_JK00D)
        symbol = model.symbols[SymbolKey("jk00d", "ram", APC_JK00D)]
        self.assertIsNone(match.verify(model, symbol, item))
        self.assertIn("count 2", match.verify(model, symbol, {**item, "count": 2}))
        self.assertIn("differ", match.verify(model, symbol, {**item, "to": "7mfk:0004e068"}))
        former = self.model(APC_FORMER)
        self.assertIn("relates", match.verify(
            former, former.symbols[SymbolKey("jk00d", "ram", APC_FORMER)], item))


class TypedTest(unittest.TestCase):
    """The evidence of a definition row: JK00D 000104a2 and 7MFK 0000e98e are
    operands at one ordinal of the calls of homologous functions."""

    def model(self):
        def declare(b):
            b.symbol("7mfk", "tbl", 0xE98E, "test", group=("tbl", "row"))
            b.symbol("jk00d", "tbl", 0x104A2, "test", group=("tbl", "row"))
        return model_of(declare)

    def test_the_first_verified_item_of_the_first_kind_types_the_row(self):
        m = self.model()
        symbol = m.symbols[SymbolKey("jk00d", "tbl", 0x104A2)]
        other = m.symbols[SymbolKey("7mfk", "tbl", 0xE98E)]
        self.assertEqual(match.typed(m, symbol, other),
                         {"kind": "call-ordinal", "supports": "homology",
                          "at": "jk00d:00075c70", "to": "7mfk:000734d4", "count": 1, "value": 0})
        # The call at 000725cc precedes it, but no function that calls the
        # table on 7MFK at that ordinal is homologous to its caller.
        refuted = [item for item in match.homology_items(m, symbol, other)
                   if item["kind"] == "call-ordinal" and item["at"] == "jk00d:000725cc"]
        self.assertTrue(refuted)
        self.assertTrue(all("neither one meaning" in match.verify(m, symbol, item)
                            for item in refuted))

    def test_touching_lists_every_instruction_that_touches_the_storage(self):
        m = self.model()
        found = match.touching(m, m.symbols[SymbolKey("jk00d", "tbl", 0x104A2)])
        self.assertEqual(len(found), 25)
        self.assertEqual(found[:2], [0x725C2, 0x725CC])


class InterpContractTest(unittest.TestCase):
    """interp-contract evidence: two wrappers share the contract and call the
    entries of their kernels, and two kernels share the entry that a wrapper
    of one meaning calls on both layouts."""

    @classmethod
    def setUpClass(cls):
        cls.model = compile.cached(repo.ROOT)

    def verify(self, layout, address, to, key):
        symbol = self.model.symbols[SymbolKey(layout, "fn", address)]
        return match.verify(self.model, symbol, {"kind": "interp-contract", "supports": "homology",
                                                 "to": to, "key": key})

    def test_two_wrappers_share_the_contract_and_call_their_kernel_entries(self):
        self.assertIsNone(self.verify("jk00d", 0x26FF8, "7mfk:000263f4", "000263f4"))
        self.assertIn("is not the address of",
                      self.verify("jk00d", 0x26FF8, "7mfk:000263f4", "000263f8"))
        self.assertIn("`to` locates 000263f8",
                      self.verify("jk00d", 0x26FF8, "7mfk:000263f8", "000263f4"))

    def test_a_fused_wrapper_differs_from_a_wrapper_with_an_offset_entry(self):
        self.assertIn("the interpolation contracts differ in offset",
                      self.verify("1me3b", 0x2AA48, "7mfk:00026388", "00026388"))

    def test_two_kernels_share_an_entry_inside_their_functions(self):
        self.assertIsNone(self.verify("jk00d", 0x27664, "7mfk:00026a60", "00026a84"))
        self.assertIn("no wrapper of one meaning on jk00d and 7mfk calls the kernel entry "
                      "00026a90", self.verify("jk00d", 0x27664, "7mfk:00026a60", "00026a90"))


class ImageBytesTest(unittest.TestCase):
    def test_a_hook_word_names_its_target(self):
        def declare(target):
            def run(b):
                hook = b.symbol("7mfk", "hook", HOOK, "test", group=("hook", "vector"))
                fn = b.symbol("7mfk", "fn", target, "test", group=("fn", "handler"))
                b.link(hook, "target", fn, "test")
            return run
        self.assertEqual(checks.image_bytes(model_of(declare(HOOK_TARGET))), [])
        issues = checks.image_bytes(model_of(declare(HOOK_TARGET + 2)))
        self.assertEqual(len(issues), 4)
        self.assertIn("000c7914 at 000203a0", issues[0].message)

    def test_a_did_entry_lists_its_sources(self):
        def declare(words, source):
            def run(b):
                did = b.symbol("7mfk", "did", DID, "test", group=("did", "number", 1), evidence=[{
                    "kind": "did-table", "supports": "identity", "at": f"7mfk:{DID:08x}",
                    "value": words}])
                ram = b.symbol("7mfk", "ram", source, "test", group=("ram", "source"))
                b.link(did, "source", ram, "test", props={"offset": 0})
            return run
        self.assertEqual(checks.image_bytes(model_of(declare(DID_WORDS, 0xFFFF3346))), [])
        issues = checks.image_bytes(model_of(declare(DID_WORDS, 0xFFFF3347)))
        self.assertEqual([issue.message for issue in issues],
                         ["the entry ffff3346 00011e45 lacks the source "
                          "7mfk-ffff3347/ram at position 0"])
        issues = checks.image_bytes(model_of(declare("ffff3347 00011e45", 0xFFFF3347)))
        self.assertEqual([issue.message for issue in issues],
                         ["did-table evidence at 7mfk:000229e8: JK00A holds ffff3346 00011e45 "
                          "at 000229e8, not ffff3347 00011e45"])


class FileChecksTest(unittest.TestCase):
    """The homology and statuses checks over the files of `kb/` in a
    temporary tree, against the L0 and the images of the repository."""

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)

    def tearDown(self):
        self.directory.cleanup()

    def model(self, document):
        path = self.root / store.path_of("ram", "apc_probe")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(store.render("ram", {"title": "APC probe", "level": "code",
                                             "home": "7mfk", **document}), encoding="utf-8")
        b = builder()
        files.declare(b, self.root)
        files.relate(b, self.root)
        model = b.finish()
        names.assign(model, [])
        model.root, model.config = repo.ROOT, repo.config()
        return model

    def symbols(self, jk00d, anchor=True):
        home = {"layout": "7mfk", "address": f"{APC_7MFK:08x}"}
        if anchor:
            home["evidence"] = [{"kind": "l0", "supports": "identity",
                                 "at": f"7mfk:{APC_STORE:08x}"}]
        return [home, {"layout": "jk00d", "address": f"{jk00d:08x}", "evidence": [{
            "kind": "masked-match", "supports": "homology", "at": f"jk00d:{APC_MATCH:08x}",
            "to": f"7mfk:{APC_REGION:08x}", "count": 1, "value": 14}]}]

    def test_a_verified_chain_reaches_the_anchor(self):
        model = self.model({"symbol": self.symbols(APC_JK00D)})
        self.assertEqual(checks.homology(model), [])
        ranks = match.grounded(model, [SymbolKey("jk00d", "ram", APC_JK00D)])
        self.assertEqual(ranks[SymbolKey("jk00d", "ram", APC_JK00D)][0], 2)

    def test_evidence_that_l0_refutes_fails_and_grounds_nothing(self):
        model = self.model({"symbol": self.symbols(APC_FORMER)})
        messages = [issue.message for issue in checks.homology(model)]
        self.assertEqual(len(messages), 2, messages)
        self.assertIn("no aligned instruction relates", messages[0])
        self.assertIn("neither an anchor nor homologous", messages[1])

    def test_a_chain_without_an_anchor_grounds_nothing(self):
        model = self.model({"symbol": self.symbols(APC_JK00D, anchor=False)})
        subjects = sorted(issue.subject for issue in checks.homology(model))
        self.assertEqual(subjects, ["7mfk-ffff2022/ram", "jk00d-ffff11f5/ram"])

    def test_statuses_carry_their_search(self):
        current = match.l0_digest("jk78c")
        statuses = [
            {"layout": "jk78c", "state": "unresolved", "method": "masked-match",
             "target": "7mfk:ffff2022", "count": 0, "l0": current},
            {"layout": "1nd", "state": "unresolved", "method": "masked-match",
             "target": "apc_probe/ram", "count": 1, "l0": "0123456789abcdef"},
            {"layout": "1me3b", "state": "unresolved", "method": "masked-match"},
            {"layout": "jk00c", "state": "absent"},
        ]
        model = self.model({"symbol": self.symbols(APC_JK00D), "status": statuses})
        messages = sorted(f"{issue.subject}: {issue.message}" for issue in checks.statuses(model))
        self.assertEqual(messages, [
            "apc_probe/ram on 1me3b: an unresolved status without target, count, l0",
            "apc_probe/ram on 1nd: count 1; a search states 0 or more than 1 match",
            "apc_probe/ram on jk00c: an absent status without evidence",
        ])
        notes = checks.stale(model)
        self.assertEqual([note.subject for note in notes], ["apc_probe/ram on 1nd"])

    def test_the_evidence_of_a_status_holds_on_l0_and_the_images(self):
        def absent(layout, *items):
            return {"layout": layout, "state": "absent",
                    "evidence": [{"supports": "identity", **item} for item in items]}
        statuses = [
            absent("jk78c", {"kind": "rom-bytes", "at": "jk78c:0001c0d0",
                             "value": "3702000000000021"},
                   {"kind": "rom-bytes", "at": "jk78c:0001c0d0", "value": "3803"}),
            absent("1nd", {"kind": "l0", "at": "1nd:0010dd44"}),
            absent("1me3b", {"kind": "l0", "at": "1me3b:00119bf7"}),
            absent("jk00c", {"kind": "l0", "at": "jk78c:000e5942"}, {"kind": "rom-bytes",
                                                                     "at": "jk00c:0001c0d0"}),
        ]
        model = self.model({"symbol": self.symbols(APC_JK00D), "status": statuses})
        messages = sorted(f"{issue.subject}: {issue.message}" for issue in checks.statuses(model))
        self.assertEqual(messages, [
            "apc_probe/ram on 1me3b: l0 evidence at 1me3b:00119bf7: L0 of 1me3b holds no "
            "instruction at 00119bf7",
            "apc_probe/ram on jk00c: l0 evidence at jk78c:000e5942: `at` lies on jk78c, not "
            "on jk00c",
            "apc_probe/ram on jk00c: rom-bytes evidence at jk00c:0001c0d0: lacks value",
            "apc_probe/ram on jk78c: rom-bytes evidence at jk78c:0001c0d0: JK78C holds 3702 at "
            "0001c0d0, not 3803",
        ])
        self.assertEqual([issue.message for issue in checks.schema(model)],
                         ["rom-bytes evidence lacks value"])


if __name__ == "__main__":
    unittest.main()
