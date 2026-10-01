import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from provenance import (  # noqa: E402
    ClaimKey,
    Dependency,
    ProvenanceError,
    StructuralKey,
    analyze_claims,
    canonical_evidence_tokens,
    compare_projection,
    dependency_path,
    evidence_machine_anchor,
    format_evidence_token,
    parse_evidence,
    reverse_impact,
)


ROM = "TEST"


def claim(addr, prop="confidence", label="Func"):
    return ClaimKey(ROM, label, addr, prop)


def dep(source, target, role="consumer", target_prop="confidence", ref=None):
    return Dependency(
        source,
        role,
        target.label,
        target.addr,
        target_prop,
        ref or target.addr,
    )


class EvidenceTest(unittest.TestCase):
    def test_address_dependency_names_target_property(self):
        token = parse_evidence(
            "consumer:00000002@confidence", "confidence", "row"
        )[0]
        self.assertEqual(token.target_addr, "00000002")
        self.assertEqual(token.target_prop, "confidence")

    def test_offset_is_preserved_and_target_is_base(self):
        token = parse_evidence(
            "base:ffff1000+0x12@structural", "confidence", "row"
        )[0]
        self.assertEqual(token.value, "ffff1000+0x12")
        self.assertEqual(token.target_addr, "ffff1000")

    def test_from_map_must_be_structural(self):
        with self.assertRaisesRegex(ProvenanceError, "from_map"):
            parse_evidence(
                "from_map:00001000@confidence", "confidence", "row"
            )

    def test_legacy_address_token_is_rejected(self):
        with self.assertRaisesRegex(ProvenanceError, "@target_prop"):
            parse_evidence("consumer:00000002", "confidence", "row")

    def test_empty_terminal_is_not_evidence(self):
        with self.assertRaisesRegex(ProvenanceError, "empty value"):
            parse_evidence("spec:", "contract_conf", "row")

    def test_duplicate_token_is_rejected_after_normalization(self):
        with self.assertRaisesRegex(ProvenanceError, "duplicate"):
            parse_evidence("spec:body; spec: body", "confidence", "row")

    def test_canonical_round_trip_and_machine_anchors(self):
        text = (
            "consumer:00000002@confidence; spec:SH7058-HW; "
            "rom_const:000090ee=0x020c; site:00001000"
        )
        tokens = parse_evidence(text, "confidence", "row")
        self.assertEqual(
            [format_evidence_token(token) for token in tokens],
            canonical_evidence_tokens(text, "confidence", "row"),
        )
        self.assertEqual(
            [evidence_machine_anchor(token) for token in tokens],
            ["00000002", None, "000090ee", "00001000"],
        )
        self.assertEqual(
            canonical_evidence_tokens("spec: SH7058-HW", "confidence"),
            ["spec:SH7058-HW"],
        )

    def test_explicit_base_and_test_are_terminal_round_trip_tokens(self):
        text = ("base:ffff1000+0x12@structural; indirect_base:00020000+0x12; "
                "test:tools/memgraph/tests/test_provenance.py#test_offset_is_preserved_and_target_is_base")
        tokens = parse_evidence(text, "confidence", "row")
        self.assertEqual([token.is_dependency for token in tokens], [True, False, False])
        self.assertEqual([token.is_terminal for token in tokens], [False, True, True])
        self.assertEqual([token.target_addr for token in tokens], ["ffff1000", None, None])
        self.assertEqual([evidence_machine_anchor(token) for token in tokens],
                         ["ffff1000", "00020000", None])
        canonical = "; ".join(format_evidence_token(token) for token in tokens)
        self.assertEqual(canonical, text)
        self.assertEqual(parse_evidence(canonical, "confidence"), tokens)

    def test_explicit_terminals_require_nonnegative_offset_and_safe_test_reference(self):
        for text in ("indirect_base:00020000", "indirect_base:00020000+-1",
                     "indirect_base:00020000+0x-1", "indirect_base:0002000+2",
                     "indirect_base:00020000+2@structural", "test:../test.py#test_path",
                     "test:/test.py#test_path", "test:tools/../test.py#test_path",
                     "test:tools/test.py#test_path()", "test:tools/test.py#class"):
            with self.subTest(text=text), self.assertRaises(ProvenanceError):
                parse_evidence(text, "confidence", "row")
        for text in ("indirect_base:00020000+0", "indirect_base:00020000+0012"):
            self.assertEqual(canonical_evidence_tokens(text, "confidence"), [text])
        with self.assertRaisesRegex(ProvenanceError, "duplicate"):
            parse_evidence("indirect_base:00020000+2; indirect_base:00020000+2", "confidence")

    def test_empty_or_invalid_bound_rom_const_is_not_a_machine_anchor(self):
        for value in (
            "rom_const:00020000=",
            "rom_const:00020000=not-a-literal",
        ):
            token = parse_evidence(value, "confidence", "row")[0]
            self.assertIsNone(evidence_machine_anchor(token), msg=value)


class ClaimGraphTest(unittest.TestCase):
    def test_dependency_ref_must_address_target(self):
        source = claim("00000001")
        with self.assertRaisesRegex(ProvenanceError, "does not address"):
            Dependency(
                source, "consumer", "Func", "00000002",
                "confidence", "00000003",
            )

    def test_weaker_dependency_limits_code(self):
        a, b = claim("00000001"), claim("00000002")
        analysis = analyze_claims(
            {a: "code", b: "candidate"},
            [dep(a, b)],
            grounded_claims={b},
        )
        self.assertEqual(analysis.effective[a], "candidate")
        self.assertEqual(analysis.weakest[a], b)
        self.assertTrue(analysis.grounded[a])

    def test_structural_dependency_grounds_without_limiting(self):
        a = claim("00000001")
        m = claim("00001000", label="Map")
        structural = Dependency(
            a, "from_map", "Map", m.addr, "structural", m.addr
        )
        analysis = analyze_claims({a: "code", m: "candidate"}, [structural])
        self.assertEqual(analysis.effective[a], "code")
        self.assertTrue(analysis.grounded[a])

    def test_cycle_uses_external_weakest_link(self):
        a, b, c = claim("00000001"), claim("00000002"), claim("00000003")
        analysis = analyze_claims(
            {a: "code", b: "code", c: "pattern"},
            [dep(a, b), dep(b, a), dep(b, c)],
            grounded_claims={c},
        )
        self.assertEqual(analysis.effective[a], "pattern")
        self.assertEqual(analysis.effective[b], "pattern")
        self.assertTrue(analysis.grounded[a])
        self.assertEqual(len(analysis.cyclic_components), 1)
        self.assertFalse(analysis.ungrounded_cycles)

    def test_ungrounded_cycle_is_reported(self):
        a, b = claim("00000001"), claim("00000002")
        analysis = analyze_claims(
            {a: "code", b: "code"},
            [dep(a, b), dep(b, a)],
        )
        self.assertEqual(len(analysis.ungrounded_cycles), 1)
        self.assertFalse(analysis.grounded[a])

    def test_self_loop_is_a_cycle(self):
        a = claim("00000001")
        analysis = analyze_claims({a: "code"}, [dep(a, a)])
        self.assertEqual(analysis.cyclic_components, [(a,)])

    def test_dependency_path_reaches_weakest_claim(self):
        a, b, c = claim("00000001"), claim("00000002"), claim("00000003")
        dependencies = [dep(a, b), dep(b, c)]
        self.assertEqual(dependency_path(a, c, dependencies), [a, b, c])

    def test_contract_and_semantics_impacts_do_not_mix(self):
        target_sem = claim("00000002")
        target_contract = claim("00000002", "contract_conf")
        sem_user = claim("00000003")
        contract_user = claim("00000004", "contract_conf")
        dependencies = [
            dep(sem_user, target_sem),
            dep(contract_user, target_contract, target_prop="contract_conf"),
        ]
        sem_impact = reverse_impact(target_sem, dependencies)
        self.assertIn(sem_user, sem_impact)
        self.assertNotIn(contract_user, sem_impact)
        contract_impact = reverse_impact(target_contract, dependencies)
        self.assertIn(contract_user, contract_impact)
        self.assertNotIn(sem_user, contract_impact)

    def test_structural_identity_validates_address(self):
        with self.assertRaisesRegex(ProvenanceError, "eight hexadecimal digits"):
            StructuralKey(ROM, "Map", "1000")

    def test_structural_impact_has_own_identity(self):
        source = claim("00000001")
        dependency = Dependency(
            source, "from_map", "Map", "00001000", "structural", "00001000"
        )
        changed = StructuralKey(ROM, "Map", "00001000")
        self.assertEqual(reverse_impact(changed, [dependency])[source], 1)


class ProjectionTest(unittest.TestCase):
    def test_projection_reports_missing_extra_and_duplicates(self):
        diff = compare_projection(["a", "a", "b"], ["a", "c", "c"])
        self.assertEqual(diff.missing, {"a": 1, "b": 1})
        self.assertEqual(diff.extra, {"c": 2})
        self.assertEqual(diff.duplicate_expected, {"a": 2})
        self.assertEqual(diff.duplicate_actual, {"c": 2})
        self.assertFalse(diff.clean)


if __name__ == "__main__":
    unittest.main()
