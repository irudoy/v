import copy
import unittest

from tools.sweep import agent_protocol as protocol


DIGEST = "0" * 64


def executor(model="fixture-model"):
    return {
        "schema": protocol.EXECUTOR_SCHEMA,
        "provider": "fixture-provider",
        "backend": "fixture-backend",
        "model": model,
        "effort": "high",
        "adapter": "fixture-native",
        "adapter_version": "1",
    }


def receipt(task_id, response):
    return {
        "invocation_id": f"invocation-{task_id.replace(':', '-')}",
        "fresh": True,
        "fallback": False,
        "retry_count": 0,
        "cache_reuse": False,
        "domain_tool_calls": 0,
        "input_tokens": 100,
        "output_tokens": 20,
        "duration_ms": 500,
        "cost_usd": None,
        "raw_output": response,
        "raw_output_sha256": protocol.value_sha256(response),
    }


def bundle(batch, responses, current_executor=None):
    current_executor = current_executor or executor()
    return {
        "schema": protocol.TASK_RESULTS_SCHEMA,
        "batch_sha256": protocol.value_sha256(batch),
        "executor": current_executor,
        "operator_attested": True,
        "results": [
            {
                "task_id": task["task_id"],
                "status": "completed",
                "response": responses[task["task_id"]],
                "receipt": receipt(task["task_id"], responses[task["task_id"]]),
            }
            for task in batch["tasks"]
        ],
    }


def prep_execution():
    return {
        "schema": "vq.caller-semantics-prep-execution/v4",
        "result_schema": "vq.caller-semantics-prep-results/v4",
        "execution_config_sha256": DIGEST,
        "protocol_binding": {
            "schema": protocol.PROTOCOL_SCHEMA,
            "protocol_path": "tools/sweep/agent_protocol.py",
            "protocol_sha256": protocol.protocol_source()["sha256"],
        },
        "private_manifest_sha256": "1" * 64,
        "worklist_sha256": "2" * 64,
        "prompts": {
            "analyze": "Analyze the assigned artifact.",
            "verify": "Verify the exact Analyze payload.",
        },
        "items": [
            {
                "experiment_id": "exp-" + "1" * 14,
                "condition_id": "cond-" + "2" * 14,
                "pair_id": "pair-" + "3" * 14,
                "job_id": "job-" + "4" * 14,
                "target_address": "00001000",
                "artifact_sha256": "3" * 64,
                "response_schema": "caller-role-semantics-with-citations/v3",
                "artifact_text": "line one\nline two",
            },
            {
                "experiment_id": "exp-" + "1" * 14,
                "condition_id": "cond-" + "2" * 14,
                "pair_id": "pair-" + "5" * 14,
                "job_id": "job-" + "6" * 14,
                "target_address": "00002000",
                "artifact_sha256": "4" * 64,
                "response_schema": "caller-role-semantics-with-citations/v3",
                "artifact_text": "other one\nother two",
            },
        ],
    }


def run_execution():
    item = prep_execution()["items"][0]
    return {
        "schema": "vq.caller-semantics-run-execution/v4",
        "result_schema": "vq.caller-semantics-run-results/v4",
        "execution_config_sha256": DIGEST,
        "protocol_binding": prep_execution()["protocol_binding"],
        "condition_id": item["condition_id"],
        "worklist_sha256": "2" * 64,
        "prompts": {
            "analyze": "Analyze the assigned map artifact.",
            "verify": "Verify the exact Analyze payload.",
        },
        "items": [
            {
                **item,
                "response_schema": "map-analysis-with-adversarial-verdict/v3",
            }
        ],
    }


def score_execution():
    return {
        "schema": "vq.caller-semantics-score-execution/v3",
        "result_schema": "vq.caller-semantics-score-results/v2",
        "execution_config_sha256": DIGEST,
        "protocol_binding": prep_execution()["protocol_binding"],
        "run_report_sha256": "1" * 64,
        "worklist_sha256": "2" * 64,
        "prompt": "Score semantic equivalence.",
        "items": [
            {
                "score_id": "score-" + "1" * 24,
                "candidate_sha256": "3" * 64,
                "reference_sha256": "4" * 64,
                "payload_sha256": "5" * 64,
                "candidate_semantics": "Returns one value.",
                "reference_semantics": "Produces one value.",
                "response_schema": "arm-blind-semantics-score/v1",
            }
        ],
    }


class AgentProtocolTest(unittest.TestCase):
    def setUp(self):
        self.execution = prep_execution()
        self.binding = {
            "schema": protocol.PROTOCOL_SCHEMA,
            "sha256": protocol.protocol_source()["sha256"],
        }

    def analyze_responses(self, batch):
        return {
            task["task_id"]: {
                "role": "value coordinator",
                "semantics": "Combines machine values into one result.",
                "citations": [
                    {
                        "line_start": 1,
                        "line_end": 1,
                        "excerpt": "line one",
                    }
                ],
            }
            for task in batch["tasks"]
        }

    def test_batches_expose_only_worker_prompt_schema_and_index(self):
        batch = protocol.build_batch(
            self.execution,
            "analyze",
            binding=self.binding,
        )
        self.assertEqual(batch["kind"], "prep")
        self.assertEqual(batch["phase"], "analyze")
        self.assertEqual(len(batch["tasks"]), 2)
        serialized_prompts = "\n".join(task["prompt"] for task in batch["tasks"])
        for item in self.execution["items"]:
            self.assertNotIn(item["job_id"], serialized_prompts)
            self.assertNotIn(item["condition_id"], serialized_prompts)
        self.assertIn("1|line one", batch["tasks"][0]["prompt"])
        self.assertEqual(batch["policy"], protocol.TASK_POLICY)

    def test_verify_batch_is_bound_to_exact_analyze_results(self):
        analyze_batch = protocol.build_batch(
            self.execution,
            "analyze",
            binding=self.binding,
        )
        analyze_bundle = bundle(
            analyze_batch,
            self.analyze_responses(analyze_batch),
        )
        verify_batch = protocol.build_batch(
            self.execution,
            "verify",
            prior_results=analyze_bundle,
            binding=self.binding,
        )
        self.assertIn(
            '"semantics": "Combines machine values into one result."',
            verify_batch["tasks"][0]["prompt"],
        )
        changed = copy.deepcopy(analyze_bundle)
        changed["results"][0]["response"]["semantics"] = "Changed"
        with self.assertRaisesRegex(protocol.ProtocolError, "raw output SHA-256"):
            protocol.build_batch(
                self.execution,
                "verify",
                prior_results=changed,
                binding=self.binding,
            )

    def test_complete_prep_archive_is_provider_neutral(self):
        analyze_batch = protocol.build_batch(
            self.execution,
            "analyze",
            binding=self.binding,
        )
        analyses = self.analyze_responses(analyze_batch)
        analyze_bundle = bundle(analyze_batch, analyses)
        verify_batch = protocol.build_batch(
            self.execution,
            "verify",
            prior_results=analyze_bundle,
            binding=self.binding,
        )
        verdicts = {
            task["task_id"]: {
                "mode": "adversarial",
                "verdict": "accept",
                "role": analyses[f"prep-analyze:{index}"]["role"],
                "semantics": analyses[f"prep-analyze:{index}"]["semantics"],
                "citations": analyses[f"prep-analyze:{index}"]["citations"],
                "rationale": "The cited line entails the complete payload.",
            }
            for index, task in enumerate(verify_batch["tasks"], start=1)
        }
        verify_bundle = bundle(verify_batch, verdicts)
        archive = protocol.build_archive(
            self.execution,
            [analyze_bundle, verify_bundle],
            run_id="ar_fixture-run",
            operator_attested=True,
            binding=self.binding,
        )
        self.assertEqual(archive["schema"], protocol.ARCHIVE_SCHEMA)
        self.assertEqual(archive["executor"], executor())
        self.assertEqual(len(archive["result"]["analyses"]), 2)
        self.assertEqual(len(archive["result"]["verdicts"]), 2)
        protocol.validate_archive(
            archive,
            self.execution,
            expected_executor=executor(),
            binding=self.binding,
        )

    def test_archive_rejects_executor_change_between_phases(self):
        analyze_batch = protocol.build_batch(
            self.execution,
            "analyze",
            binding=self.binding,
        )
        analyses = self.analyze_responses(analyze_batch)
        analyze_bundle = bundle(analyze_batch, analyses)
        verify_batch = protocol.build_batch(
            self.execution,
            "verify",
            prior_results=analyze_bundle,
            binding=self.binding,
        )
        verdicts = {
            task["task_id"]: {
                "mode": "adversarial",
                "verdict": "accept",
                "role": analyses[f"prep-analyze:{index}"]["role"],
                "semantics": analyses[f"prep-analyze:{index}"]["semantics"],
                "citations": analyses[f"prep-analyze:{index}"]["citations"],
                "rationale": "Accepted.",
            }
            for index, task in enumerate(verify_batch["tasks"], start=1)
        }
        verify_bundle = bundle(
            verify_batch,
            verdicts,
            current_executor=executor("other-model"),
        )
        with self.assertRaisesRegex(protocol.ProtocolError, "another executor"):
            protocol.build_archive(
                self.execution,
                [analyze_bundle, verify_bundle],
                run_id="ar_fixture-run",
                operator_attested=True,
                binding=self.binding,
            )

    def test_results_reject_tools_retry_fallback_and_cache(self):
        batch_value = protocol.build_batch(
            self.execution,
            "analyze",
            binding=self.binding,
        )
        base = bundle(batch_value, self.analyze_responses(batch_value))
        for field, value in (
            ("domain_tool_calls", 1),
            ("retry_count", 1),
            ("fallback", True),
            ("cache_reuse", True),
            ("fresh", False),
        ):
            with self.subTest(field=field):
                changed = copy.deepcopy(base)
                changed["results"][0]["receipt"][field] = value
                with self.assertRaises(protocol.ProtocolError):
                    protocol.validate_results_bundle(changed, batch_value)

    def test_json_schema_rejects_extra_response_field(self):
        batch_value = protocol.build_batch(
            self.execution,
            "analyze",
            binding=self.binding,
        )
        responses = self.analyze_responses(batch_value)
        responses["prep-analyze:1"]["extra"] = True
        current = bundle(batch_value, responses)
        with self.assertRaisesRegex(protocol.ProtocolError, "field set"):
            protocol.validate_results_bundle(current, batch_value)

    def test_run_archive_preserves_exact_analyze_verify_link(self):
        execution = run_execution()
        analyze_batch = protocol.build_batch(
            execution,
            "analyze",
            binding=self.binding,
        )
        analysis = {
            "status": "completed",
            "decision": "downgrade",
            "role": "table",
            "semantics": "Returns one machine value.",
            "disposition": "return",
            "target": "register r0 at 00001000",
            "evidence": "site:00001000",
            "machine_references": "00001000; 00002000",
            "citations": [
                {
                    "line_start": 1,
                    "line_end": 1,
                    "excerpt": "line one",
                }
            ],
        }
        analyze_bundle = bundle(
            analyze_batch,
            {"map-analyze:1": analysis},
        )
        verify_batch = protocol.build_batch(
            execution,
            "verify",
            prior_results=analyze_bundle,
            binding=self.binding,
        )
        verify_bundle = bundle(
            verify_batch,
            {
                "map-verify:1": {
                    "mode": "adversarial",
                    "verdict": "accept",
                    "analysis": analysis,
                    "rationale": "The complete payload survives.",
                }
            },
        )
        archive = protocol.build_archive(
            execution,
            [analyze_bundle, verify_bundle],
            run_id="ar_run-fixture",
            operator_attested=True,
            binding=self.binding,
        )
        full = archive["result"]["analyses"][0]
        self.assertEqual(full["job_id"], execution["items"][0]["job_id"])
        self.assertEqual(archive["result"]["verdicts"][0]["analysis"], full)

    def test_score_archive_is_single_phase(self):
        execution = score_execution()
        score_batch = protocol.build_batch(
            execution,
            "score",
            binding=self.binding,
        )
        score_bundle = bundle(
            score_batch,
            {
                "score:1": {
                    "score": 0.75,
                    "rationale": "The operations are substantially equivalent.",
                }
            },
        )
        archive = protocol.build_archive(
            execution,
            [score_bundle],
            run_id="ar_score-fixture",
            operator_attested=True,
            binding=self.binding,
        )
        self.assertEqual(archive["result"]["scores"][0]["score"], 0.75)
        self.assertEqual(len(archive["batches"]), 1)


if __name__ == "__main__":
    unittest.main()
