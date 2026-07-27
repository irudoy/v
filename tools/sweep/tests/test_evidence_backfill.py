import copy
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools" / "sweep"))

import evidence_backfill as backfill  # noqa: E402

BASE_COMMIT = "b02d3b7157d900a0654b1c63f2c200d8154d315b"


class FrozenManifestTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = backfill.freeze_manifest(ROOT, "JK03A", BASE_COMMIT)

    def test_frozen_scope_is_exact_and_stable(self):
        again = backfill.freeze_manifest(ROOT, "JK03A", BASE_COMMIT)
        self.assertEqual(self.manifest, again)
        self.assertEqual(len(self.manifest["claims"]), 78)
        self.assertEqual(len(self.manifest["nodes"]), 58)
        self.assertEqual(
            {
                key: value
                for key, value in self.manifest["expected"]["breakdown"].items()
            },
            {"Axis.scale_conf": 6, "Map.confidence": 52, "Map.scale_conf": 20},
        )
        self.assertEqual(
            backfill.stable_json_bytes(self.manifest),
            backfill.stable_json_bytes(again),
        )

    def test_row_digest_changes_with_claim_source(self):
        claim = self.manifest["claims"][0]
        source = next(
            item for item in self.manifest["sources"] if item["path"] == claim["source"]
        )
        fields = source["fields"]
        row = {field: "" for field in fields}
        row["addr"] = claim["addr"]
        before = backfill.row_digest(fields, row)
        row["note"] = "drift"
        self.assertNotEqual(before, backfill.row_digest(fields, row))


class BackfillControlPlaneTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(
            ["git", "config", "user.email", "tests@example.invalid"],
            cwd=self.repo,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Tests"], cwd=self.repo, check=True
        )
        (self.repo / "defs").mkdir()
        for name in ("JK03A.findings.csv", "JK03A.axes.csv"):
            data = backfill.git_source(ROOT, BASE_COMMIT, f"defs/{name}")
            (self.repo / "defs" / name).write_bytes(data)
        subprocess.run(["git", "add", "defs"], cwd=self.repo, check=True)
        subprocess.run(
            ["git", "commit", "-qm", "fixture"], cwd=self.repo, check=True
        )
        self.manifest = backfill.freeze_manifest(self.repo, "JK03A", "HEAD")
        self.manifest_path = self.repo / "manifest.json"
        backfill.write_json(self.manifest_path, self.manifest)

        self.left = self.repo / "artifacts-a"
        self.right = self.repo / "artifacts-b"
        self.left.mkdir()
        self.right.mkdir()
        for node in self.manifest["nodes"]:
            text = f"# Blind {node['identity']}\n"
            (self.left / node["artifact"]).write_text(text, encoding="utf-8")
            (self.right / node["artifact"]).write_text(text, encoding="utf-8")
        self.artifacts = backfill.verify_artifacts(
            self.manifest_path, self.left, self.right
        )
        self.artifact_path = self.repo / "artifacts.json"
        backfill.write_json(self.artifact_path, self.artifacts)
        self.inventory = {
            item["name"]: item["sha256"] for item in self.artifacts["files"]
        }
        self.results = self._results()
        self.results_path = self.repo / "results.json"
        backfill.write_json(self.results_path, self._archive(self.results))
        self.decisions = self._decisions()
        self.decisions_path = self.repo / "decisions.json"
        backfill.write_json(self.decisions_path, self.decisions)

    def _results(self):
        analyses = []
        for node in self.manifest["nodes"]:
            analyses.append(
                {
                    "node": node["identity"],
                    "artifact_sha256": self.inventory[node["artifact"]],
                    "properties": node["properties"],
                    "summary": "Independent blind fixture analysis.",
                }
            )
        verdicts = []
        for claim in self.manifest["claims"]:
            values = dict(claim["claim_value"])
            values.pop(claim["property"])
            verdict = {
                "identity": claim["identity"],
                "artifact_sha256": self.inventory[claim["artifact"]],
                "decision": "accept_code",
                "evidence": "site:test-fixture",
                "values": values,
                "trace": "Fixture complete machine trace.",
                "verifier_rationale": "The terminal site confirms the fixture claim.",
            }
            if claim["label"] == "Map" and claim["property"] == "confidence":
                dead = values["role"] == "dead"
                verdict["output_disposition"] = (
                    "dead_control_flow" if dead else "consumer"
                )
                verdict["target"] = "fixture-target"
            verdicts.append(verdict)
        return {
            "schema": backfill.RESULT_SCHEMA,
            "manifest_sha256": backfill.file_sha256(self.manifest_path),
            "artifact_set_sha256": self.artifacts["artifact_set_sha256"],
            "analyses": analyses,
            "verdicts": verdicts,
        }

    def _archive(self, result):
        return {
            "runId": "wf_test-fixture",
            "timestamp": "2026-07-25T00:00:00Z",
            "taskId": "fixture",
            "script": "return result",
            "scriptPath": "/tmp/fixture-workflow.js",
            "args": {
                "manifest_sha256": backfill.file_sha256(self.manifest_path),
                "artifact_set_sha256": self.artifacts["artifact_set_sha256"],
                "items": backfill.workflow_worklist(
                    self.manifest, self.artifacts, self.inventory
                ),
            },
            "result": result,
            "status": "completed",
        }

    def _decisions(self):
        verdicts = {item["identity"]: item for item in self.results["verdicts"]}
        notes = {}
        for node in self.manifest["nodes"]:
            claims = [claim for claim in self.manifest["claims"] if claim["node"] == node["identity"]]
            semantic = next(
                (claim for claim in claims if claim["property"] == "confidence"), None
            )
            if semantic:
                verdict = verdicts[semantic["identity"]]
                notes[node["identity"]] = (
                    f"Fixture. Result disposition: {verdict['output_disposition']}. "
                    f"Result target: {verdict['target']}. Scale trace: fixture."
                )
            else:
                notes[node["identity"]] = "Fixture. Scale trace: fixture."
        items = []
        for claim in self.manifest["claims"]:
            verdict = verdicts[claim["identity"]]
            item = {
                "identity": claim["identity"],
                "action": "accept",
                "evidence": verdict["evidence"],
                "note": notes[claim["node"]],
            }
            if claim["label"] == "Map" and claim["property"] == "confidence":
                item["output_disposition"] = verdict["output_disposition"]
                item["target"] = verdict["target"]
            items.append(item)
        return {
            "schema": backfill.DECISION_SCHEMA,
            "manifest_sha256": backfill.file_sha256(self.manifest_path),
            "artifact_set_sha256": self.artifacts["artifact_set_sha256"],
            "results_sha256": backfill.file_sha256(self.results_path),
            "decisions": items,
        }

    def _validated_decisions(self, decisions=None, results=None):
        results = results or self.results
        decisions = decisions or self.decisions
        return backfill.validate_decisions(
            self.manifest,
            results,
            decisions,
            self.manifest_path,
            self.artifacts,
            self.results_path,
        )

    def test_artifact_sets_must_be_complete_and_deterministic(self):
        target = self.right / self.manifest["nodes"][0]["artifact"]
        target.write_text("different\n", encoding="utf-8")
        with self.assertRaisesRegex(backfill.BackfillError, "nondeterministic"):
            backfill.verify_artifacts(self.manifest_path, self.left, self.right)

    def test_archive_requires_exact_frozen_worklist(self):
        archive = self._archive(self.results)
        archive["args"]["items"].pop()
        broken_path = self.repo / "wrong-worklist.json"
        backfill.write_json(broken_path, archive)
        with self.assertRaisesRegex(backfill.BackfillError, "frozen worklist"):
            backfill.validate_results(
                self.manifest_path, self.artifact_path, broken_path
            )

    def test_results_require_exact_78_identity_join(self):
        broken = copy.deepcopy(self.results)
        broken["verdicts"].pop()
        broken_path = self.repo / "broken-results.json"
        backfill.write_json(broken_path, self._archive(broken))
        with self.assertRaisesRegex(backfill.BackfillError, "missing="):
            backfill.validate_results(
                self.manifest_path, self.artifact_path, broken_path
            )

    def test_process_metadata_is_not_factual_evidence(self):
        broken = copy.deepcopy(self.results)
        broken["verdicts"][0]["evidence"] = "wave:fixture;arg:0"
        broken_path = self.repo / "process-only.json"
        backfill.write_json(broken_path, self._archive(broken))
        with self.assertRaisesRegex(backfill.BackfillError, "no factual evidence"):
            backfill.validate_results(
                self.manifest_path, self.artifact_path, broken_path
            )

    def test_verified_evidence_allows_audited_site_and_ram_normalization(self):
        results = copy.deepcopy(self.results)
        decisions = copy.deepcopy(self.decisions)
        verdict = next(
            item for item in results["verdicts"] if item["identity"].endswith(":confidence")
        )
        decision = next(
            item for item in decisions["decisions"] if item["identity"] == verdict["identity"]
        )
        verdict["evidence"] = (
            "consumer:00012345@confidence;writes:ffff1234@confidence;site:00000001"
        )
        decision["evidence"] = "site:00012345;site:00000001"
        decision["evidence_rewrites"] = {
            "consumer:00012345@confidence": "site:00012345",
            "writes:ffff1234@confidence": None,
        }
        self._validated_decisions(decisions=decisions, results=results)

    def test_verified_evidence_rejects_changed_site_address(self):
        results = copy.deepcopy(self.results)
        decisions = copy.deepcopy(self.decisions)
        verdict = next(
            item for item in results["verdicts"] if item["identity"].endswith(":confidence")
        )
        decision = next(
            item for item in decisions["decisions"] if item["identity"] == verdict["identity"]
        )
        verdict["evidence"] = "consumer:00012345@confidence"
        decision["evidence"] = "site:00012346"
        decision["evidence_rewrites"] = {
            "consumer:00012345@confidence": "site:00012346",
        }
        with self.assertRaisesRegex(backfill.BackfillError, "only be rewritten as ROM site"):
            self._validated_decisions(decisions=decisions, results=results)

    def test_semantics_revision_cannot_change_scale_units(self):
        decisions = copy.deepcopy(self.decisions)
        decision = next(
            item
            for item in decisions["decisions"]
            if item["identity"].endswith(":confidence")
        )
        decision["action"] = "revise"
        decision["values"] = {"units": "fixture units"}
        with self.assertRaisesRegex(backfill.BackfillError, "prohibited fields"):
            self._validated_decisions(decisions=decisions)

    def test_raw_identity_is_not_a_scale_claim(self):
        broken = copy.deepcopy(self.results)
        verdict = next(
            item for item in broken["verdicts"] if item["identity"].endswith(":scale_conf")
        )
        verdict["values"]["scale_expr"] = "x"
        with self.assertRaisesRegex(backfill.BackfillError, "raw identity"):
            self._validated_decisions(results=broken)

    def test_dead_role_requires_dead_control_flow(self):
        broken = copy.deepcopy(self.results)
        verdict = next(
            item
            for item in broken["verdicts"]
            if item.get("values", {}).get("role") == "dead"
            and item["identity"].endswith(":confidence")
        )
        verdict["output_disposition"] = "consumer"
        broken_path = self.repo / "dead-consumer.json"
        backfill.write_json(broken_path, self._archive(broken))
        with self.assertRaisesRegex(backfill.BackfillError, "dead_control_flow"):
            backfill.validate_results(
                self.manifest_path, self.artifact_path, broken_path
            )

    def test_downgraded_dead_role_does_not_require_disposition(self):
        claim = {
            "identity": "TEST:Map:00000010:confidence",
            "label": "Map",
            "property": "confidence",
            "evidence_field": "evidence",
        }
        row = {"confidence": "code", "role": "dead", "evidence": ""}
        decision = {"action": "downgrade", "note": "Fixture blocker."}
        updated = backfill._apply_to_frozen_row(row, [(claim, decision)])
        self.assertEqual(updated["confidence"], "candidate")
        self.assertEqual(updated["role"], "dead")

    def test_refuted_verdict_cannot_be_applied_as_code(self):
        results = copy.deepcopy(self.results)
        identity = results["verdicts"][0]["identity"]
        results["verdicts"][0] = {
            "identity": identity,
            "artifact_sha256": results["verdicts"][0]["artifact_sha256"],
            "decision": "downgrade",
            "blocker": "Fixture blocker.",
            "verifier_rationale": "The fixture check refuted the claim.",
        }
        with self.assertRaisesRegex(backfill.BackfillError, "cannot be accepted"):
            self._validated_decisions(results=results)

    def test_recovery_composition_replaces_only_full_frozen_node(self):
        node = self.manifest["nodes"][0]
        identities = [
            claim["identity"]
            for claim in self.manifest["claims"]
            if claim["node"] == node["identity"]
        ]
        recovery_result = {
            "schema": backfill.RESULT_SCHEMA,
            "manifest_sha256": backfill.file_sha256(self.manifest_path),
            "artifact_set_sha256": self.artifacts["artifact_set_sha256"],
            "analyses": [
                {
                    **next(
                        item
                        for item in self.results["analyses"]
                        if item["node"] == node["identity"]
                    ),
                    "summary": "Verified recovery analysis.",
                }
            ],
            "verdicts": [
                item for item in self.results["verdicts"] if item["identity"] in identities
            ],
        }
        recovery = self._archive(recovery_result)
        recovery["runId"] = "wf_recovery-fixture"
        recovery["scriptPath"] = "/tmp/recovery-fixture.js"
        expected_item = next(
            item
            for item in backfill.workflow_worklist(
                self.manifest, self.artifacts, self.inventory
            )
            if item["identity"] == node["identity"]
        )
        recovery["args"]["items"] = [expected_item]
        recovery["args"]["recovery_identities"] = identities
        recovery_path = self.repo / "recovery.json"
        backfill.write_json(recovery_path, recovery)

        run_set = backfill.compose_workflow_runs(
            self.manifest_path,
            self.artifact_path,
            self.results_path,
            [recovery_path],
        )
        self.assertEqual(run_set["recovered_identities"], identities)
        replaced = next(
            item
            for item in run_set["result"]["analyses"]
            if item["node"] == node["identity"]
        )
        self.assertEqual(replaced["summary"], "Verified recovery analysis.")

    def test_apply_is_idempotent_and_rejects_drift(self):
        backfill.validate_results(
            self.manifest_path, self.artifact_path, self.results_path
        )
        decisions = self._validated_decisions()
        changes = backfill.prepare_application(self.repo, self.manifest, decisions)
        self.assertTrue(any(before != after for before, after in changes.values()))
        for path, (_before, after) in changes.items():
            (self.repo / path).write_bytes(after)

        repeated = backfill.prepare_application(self.repo, self.manifest, decisions)
        self.assertTrue(all(before == after for before, after in repeated.values()))

        findings = self.repo / "defs" / "JK03A.findings.csv"
        text = findings.read_text(encoding="utf-8")
        findings.write_text(text.replace("Rev Limit", "Drift Limit", 1), encoding="utf-8")
        with self.assertRaisesRegex(backfill.BackfillError, "source drift"):
            backfill.prepare_application(self.repo, self.manifest, decisions)


if __name__ == "__main__":
    unittest.main()
