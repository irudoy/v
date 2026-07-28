import unittest

from tools.diagnostics import extract_static_bindings as extract


class StaticBindingCandidateTest(unittest.TestCase):
    def test_request_did_accepts_only_service_22(self):
        self.assertEqual(extract.request_did("221201"), ("221201", "1201"))
        self.assertEqual(
            extract.request_did("22 12 01 00"),
            ("22120100", "1201"),
        )
        self.assertIsNone(extract.request_did("010c"))

    def test_exact_did_join_does_not_auto_bind_name_matches(self):
        definitions = {
            "1201": [{
                "request_hex": "221201",
                "did": "1201",
                "diagnostic_key": "diagnostic-parameter:request:221201",
                "name": "ENG SPEED",
                "source_applicability": "homologous_community",
                "source_verification": "community_measured",
                "source_dataset_id": "fixture",
                "source_claim_id": "fixture:eng-speed",
                "source_formula": "raw * 10",
                "source_factor": "",
                "source_addend": "",
                "source_unit": "rpm",
            }]
        }
        refs = [{
            "func_addr": "00001000",
            "site": "00001010",
            "source_kind": "rom_ref",
            "literal_addr": "00008000",
            "value_hex": "1201",
        }]
        rows = extract.build_candidates(
            definitions,
            refs,
            {"00001000": ["ffff11ae", "ffff1200"]},
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["did"], "1201")
        self.assertEqual(rows[0]["status"], "unresolved")
        self.assertEqual(rows[0]["function_did_count"], 1)
        self.assertEqual(rows[0]["ram_candidate_count"], 2)


if __name__ == "__main__":
    unittest.main()
