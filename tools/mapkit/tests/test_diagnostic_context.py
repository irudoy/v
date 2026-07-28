import unittest

from tools import diagnostic_context


class DiagnosticContextTest(unittest.TestCase):
    @staticmethod
    def binding_row(**updates):
        row = {
            "map_addr": "00001000",
            "diagnostic_label": "DiagnosticParameter",
            "diagnostic_key": "diagnostic-parameter:semantic:eng-speed",
            "diagnostic_name": "ENG SPEED",
            "confidence": "code",
            "applicability": "homologous_vq35hr",
            "priority": 90,
        }
        row.update(updates)
        return row

    def test_summary_is_prioritized_deduplicated_and_keeps_applicability(self):
        rows = [
            {
                "diagnostic_label": "DiagnosticParameter",
                "diagnostic_key": "diagnostic-parameter:semantic:eng-speed",
                "diagnostic_name": "ENG SPEED",
                "confidence": "code",
                "applicability": "homologous_vq35hr",
                "priority": 90,
            },
            {
                "diagnostic_label": "DtcCode",
                "diagnostic_key": "P0327",
                "diagnostic_name": "P0327",
                "confidence": "code",
                "applicability": "exact_rom",
                "priority": 40,
            },
            {
                "diagnostic_label": "DtcCode",
                "diagnostic_key": "P0327",
                "diagnostic_name": "P0327",
                "confidence": "code",
                "applicability": "exact_rom",
                "priority": 100,
            },
            {
                "diagnostic_label": "DtcCode",
                "diagnostic_key": "P0327",
                "diagnostic_name": "P0327",
                "confidence": "code",
                "applicability": "exact_rom",
                "priority": 100,
                "relation": "map_evidence",
            },
            {
                "diagnostic_label": "DiagnosticParameter",
                "diagnostic_key": (
                    "diagnostic-parameter:semantic:coolan-temp-s"
                ),
                "diagnostic_name": "COOLAN TEMP/S",
                "confidence": "candidate",
                "applicability": "homologous_vq35hr",
                "priority": 85,
                "relation": "map_evidence",
                "relation_roles": ["indexed_by"],
            },
        ]
        priority, summary = diagnostic_context.summarize(rows)
        self.assertEqual(priority, 100)
        self.assertEqual(
            summary,
            [
                "DTC P0327 [code, exact_rom]",
                "ENG SPEED [code, homologous_vq35hr]",
                (
                    "COOLAN TEMP/S [candidate, homologous_vq35hr, "
                    "via map evidence: indexed_by]"
                ),
            ],
        )

    def test_map_bindings_preserve_direct_and_provenance_paths(self):
        class Session:
            def __init__(self, responses):
                self.responses = iter(responses)
                self.calls = 0

            def run(self, _query, **_parameters):
                self.calls += 1
                return next(self.responses)

        session = Session([
            [self.binding_row()],
            [
                self.binding_row(
                    map_addr="00002000",
                    relation_roles=["indexed_by"],
                )
            ],
            [],
            [],
        ])
        result = diagnostic_context.map_bindings(session, "JK08A")
        self.assertEqual(session.calls, 4)
        self.assertEqual(result["00001000"][0]["relation"], "direct")
        self.assertEqual(
            result["00002000"][0]["relation_roles"], ["indexed_by"]
        )
        self.assertEqual(
            result["00002000"][0]["relation"], "map_evidence"
        )


if __name__ == "__main__":
    unittest.main()
