import copy
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools" / "sweep"))

import caller_ab_experiment as experiment  # noqa: E402


MAP_ACCESSORS = {
    "0000a29a": ("0002c648", "0003be3c"),
    "0000ab4a": ("000bfdc0",),
    "0000b23a": ("000befb0",),
    "0000b33a": ("000bfdc0",),
    "0000b71a": ("00082c8a",),
    "0000b81a": ("00082c8a",),
    "0000d78e": ("0007a592",),
    "00011ede": ("0005651c",),
    "00012262": ("00094f26",),
    "000122b2": ("000b2096",),
    "00012312": ("0005d6ae", "00088bba"),
    "00012908": ("00046938",),
    "00012a32": ("000507ce",),
    "00012a62": ("000a543c",),
    "00012e1a": ("000793d2",),
    "00012e3a": ("000bcd44", "000bec52"),
    "00012fc6": ("000a643c",),
    "000131a2": ("0006205c",),
    "00014114": ("00073432",),
    "0001462a": ("000a0ee8",),
    "0001473a": ("00047a56",),
    "0001488a": ("00070e4c",),
    "0001497a": ("00082c8a",),
    "00016f48": ("0007a804",),
}
ACCESSOR_CALLERS = {
    "0002c648": "00027ce4",
    "0003be3c": "00027ce4",
    "000bfdc0": "000c21e6",
    "000befb0": "000bef6e",
    "00082c8a": "0007bfc4",
    "0007a592": "0007a7ac",
    "0005651c": "0005594a",
    "000b2096": "000b29b8",
    "0005d6ae": "0005cbec",
    "00088bba": "00088b30",
    "00046938": "00041e84",
    "000507ce": "0004ed88",
    "000a543c": "000a5904",
    "000793d2": "000797d0",
    "000bcd44": "0002c648",
    "000bec52": "000bd170",
    "000a643c": "000a66e8",
    "0006205c": "00060fb4",
    "00073432": "000730fc",
    "00047a56": "000481f4",
    "00070e4c": "00079d9c",
    "0007a804": "00079e24",
}


class CallerExperimentFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.runtime = Path(self.temp.name)
        self.exports = self.runtime / "exports"
        self.accessors = self.exports / "accessors"
        self.originals = self.runtime / "originals"
        self.originals_replica = self.runtime / "originals-replica"
        self.exports.mkdir()
        self.accessors.mkdir()
        self.originals.mkdir()
        self.originals_replica.mkdir()
        self.calls = self.exports / "calls.csv"
        self.id_secret = "11" * 32
        self._write_exports()
        self._write_originals()
        self.audit_path = self.runtime / "blind-audit.json"
        self.audit_replica_path = self.runtime / "blind-audit-replica.json"
        self._write_blind_audit(self.originals, self.audit_path)
        self._write_blind_audit(self.originals_replica, self.audit_replica_path)
        self.private_path = self.runtime / "private.json"
        self.manifest = experiment.build_private_manifest(
            ROOT,
            self.accessors,
            self.calls,
            self.exports,
            self.originals,
            self.audit_path,
            self.originals_replica,
            self.audit_replica_path,
            id_secret=self.id_secret,
        )
        experiment.write_json(self.private_path, self.manifest)

    def _write_exports(self):
        accessor_fields = ["accessor", "df_r4", "callsite", "verdict"]
        with (self.accessors / "accessors.fixture.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=accessor_fields, lineterminator="\n")
            writer.writeheader()
            index = 1
            for addr in experiment.ADDRESSES:
                for accessor in MAP_ACCESSORS[addr]:
                    writer.writerow(
                        {
                            "accessor": accessor,
                            "df_r4": addr,
                            "callsite": f"{index:08x}",
                            "verdict": "agree",
                        }
                    )
                    index += 1
        with self.calls.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=["src", "dst"], lineterminator="\n")
            writer.writeheader()
            for accessor, caller in sorted(ACCESSOR_CALLERS.items()):
                writer.writerow({"src": caller, "dst": accessor})
            for caller in sorted(set(ACCESSOR_CALLERS.values())):
                writer.writerow({"src": caller, "dst": "00020000"})
        (self.exports / "funcs.csv").write_text(
            "addr,name,size,is_thunk,is_external\n00020000,FUN_00020000,8,false,false\n",
            encoding="utf-8",
        )
        for caller in sorted(set(ACCESSOR_CALLERS.values())):
            (self.exports / f"decomp_{caller}.c").write_text(
                f"int FUN_{caller}(int input)\n{{\n  return input + 1;\n}}\n",
                encoding="utf-8",
            )

    def _write_originals(self):
        for directory in (self.originals, self.originals_replica):
            for addr in experiment.ADDRESSES:
                (directory / f"map-{addr}.md").write_text(
                    f"# Map `{addr}` (JK03A)\n\n"
                    "## Fixture machine data\n\n"
                    "```text\n"
                    f"site 00020000 reads map {addr}\n"
                    "trace 00020000 writes ffff0001\n"
                    "```\n",
                    encoding="utf-8",
                )

    def test_decomp_export_path_accepts_ghidra_unpadded_name(self):
        padded = self.exports / "decomp_0005594a.c"
        unpadded = self.exports / "decomp_5594a.c"
        padded.write_text("same\n", encoding="utf-8")
        unpadded.write_text("same\n", encoding="utf-8")
        self.assertEqual(experiment.decomp_export_path(self.exports, "0005594a"), unpadded)
        padded.unlink()
        self.assertEqual(experiment.decomp_export_path(self.exports, "0005594a"), unpadded)

    def test_decomp_export_path_rejects_conflicting_variants(self):
        padded = self.exports / "decomp_0005594a.c"
        unpadded = self.exports / "decomp_5594a.c"
        padded.write_text("padded\n", encoding="utf-8")
        unpadded.write_text("unpadded\n", encoding="utf-8")
        with self.assertRaisesRegex(experiment.ExperimentError, "conflicting decomp exports"):
            experiment.decomp_export_path(self.exports, "0005594a")

    def _write_blind_audit(self, directory, audit_path):
        builder = ROOT / "tools" / "sweep" / "build_artifacts.py"
        records = []
        for addr in experiment.ADDRESSES:
            path = (directory / f"map-{addr}.md").resolve()
            records.append(
                {
                    "target_address": addr,
                    "path": str(path),
                    "sha256": experiment.file_sha256(path),
                    "blind_verified": True,
                }
            )
        experiment.write_json(
            audit_path,
            {
                "schema": experiment.BLIND_AUDIT_SCHEMA,
                "rom": experiment.ROM,
                "mode": "focus-maps",
                "targets": list(experiment.ADDRESSES),
                "builder_path": str(builder.resolve()),
                "builder_sha256": experiment.file_sha256(builder),
                "export_dir": str(self.exports.resolve()),
                "max_readers": 8,
                "max_consumer_decomp": 24,
                "artifacts": records,
            },
        )

    def _build_prep(self):
        prep_dir = self.runtime / "prep"
        worklist_path = self.runtime / "prep-worklist.json"
        execution_path = self.runtime / "prep-execution.json"
        worklist = experiment.build_prep(
            self.private_path, prep_dir, worklist_path, execution_path
        )
        return prep_dir, worklist_path, execution_path, worklist

    def _workflow_output(self, workflow_kind, result, model="claude-opus-4-8"):
        labels = sorted(experiment.expected_workflow_labels(workflow_kind))
        return {
            "summary": f"Fixture native output for {workflow_kind}",
            "agentCount": len(labels),
            "logs": [],
            "result": result,
            "workflowProgress": [
                {
                    "type": "workflow_agent",
                    "label": label,
                    "state": "done",
                    "model": model,
                    "lastToolName": "StructuredOutput",
                    "toolCalls": 1,
                }
                for label in labels
            ],
            "totalTokens": len(labels) * 100,
            "totalToolCalls": len(labels),
        }

    def _fresh_launch(self):
        return {
            "mode": "fresh",
            "resumeFromRunId": None,
            "cacheReuse": False,
            "operatorAttested": True,
        }

    def _script_fields(self, workflow_kind):
        path = (ROOT / experiment.WORKFLOW_FILES[workflow_kind]).resolve()
        source = path.read_text(encoding="utf-8")
        return {
            "scriptPath": str(path),
            "scriptSha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
            "scriptSource": source,
        }

    def _run_saved_parser(self, kind, payload, *, json_string=False):
        source = (ROOT / experiment.WORKFLOW_FILES[kind]).read_text(encoding="utf-8")
        parse_start = source.index("const parseInput = value =>")
        helper_start = source.index("const requireValue =")
        start = min(parse_start, helper_start)
        end = source.index("\n\nconst input = parseInput", parse_start)
        parser = source[start:end]
        encoded = json.dumps(payload, separators=(",", ":"))
        value_expression = "process.argv[1]" if json_string else "JSON.parse(process.argv[1])"
        return subprocess.run(
            [
                "node",
                "--input-type=module",
                "-e",
                parser
                + "\nconst parsed = parseInput("
                + value_expression
                + "); process.stdout.write(JSON.stringify(parsed));",
                encoded,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def _saved_parser_payloads(self):
        digest = "0" * 64
        experiment_id = "exp-" + "1" * 14
        condition_id = "cond-" + "2" * 14
        config = experiment.execution_config(ROOT)

        def binding(kind):
            return {
                "blind_agent_path": experiment.BLIND_AGENT_FILE,
                "blind_agent_sha256": config["blind_agent"]["sha256"],
                "workflow_path": experiment.WORKFLOW_FILES[kind],
                "workflow_sha256": config["workflows"][kind]["sha256"],
            }

        def execution_items(count, response_schema):
            items = []
            for index in range(count):
                artifact_text = f"fixture machine artifact {index + 1}"
                items.append(
                    {
                        "experiment_id": experiment_id,
                        "condition_id": condition_id,
                        "pair_id": "pair-" + f"{index + 1:014x}",
                        "job_id": "job-" + f"{index + 1:014x}",
                        "target_address": f"{index + 1:08x}",
                        "artifact_sha256": experiment.sha256_bytes(
                            artifact_text.encode("utf-8")
                        ),
                        "response_schema": response_schema,
                        "artifact_text": artifact_text,
                    }
                )
            return items

        prep = {
            "schema": experiment.PREP_EXECUTION_SCHEMA,
            "result_schema": experiment.PREP_RESULT_SCHEMA,
            "execution_config_sha256": digest,
            "runtime_binding": binding("prep"),
            "private_manifest_sha256": digest,
            "worklist_sha256": digest,
            "prompts": {
                "analyze": experiment.PREP_ANALYZE_PROMPT,
                "verify": experiment.PREP_VERIFY_PROMPT,
            },
            "items": execution_items(21, experiment.PREP_RESPONSE_SCHEMA),
        }
        run = {
            "schema": experiment.RUN_EXECUTION_SCHEMA,
            "result_schema": experiment.RUN_RESULT_SCHEMA,
            "execution_config_sha256": digest,
            "runtime_binding": binding("run"),
            "condition_id": condition_id,
            "worklist_sha256": digest,
            "prompts": {
                "analyze": experiment.RUN_ANALYZE_PROMPT,
                "verify": experiment.RUN_VERIFY_PROMPT,
            },
            "items": execution_items(24, experiment.RUN_RESPONSE_SCHEMA),
        }
        score_items = []
        for index in range(48):
            candidate = f"candidate semantics {index + 1}"
            reference = f"reference semantics {index + 1}"
            score_items.append(
                {
                    "score_id": "score-" + f"{index + 1:024x}",
                    "candidate_sha256": experiment.sha256_bytes(
                        candidate.encode("utf-8")
                    ),
                    "reference_sha256": experiment.sha256_bytes(
                        reference.encode("utf-8")
                    ),
                    "payload_sha256": experiment.sha256_bytes(
                        experiment.stable_json_bytes(
                            {
                                "candidate_semantics": candidate,
                                "reference_semantics": reference,
                            },
                            pretty=False,
                        )
                    ),
                    "candidate_semantics": candidate,
                    "reference_semantics": reference,
                    "response_schema": experiment.SCORE_RESPONSE_SCHEMA,
                }
            )
        score = {
            "schema": experiment.SCORE_EXECUTION_SCHEMA,
            "result_schema": experiment.SCORE_RESULT_SCHEMA,
            "execution_config_sha256": digest,
            "runtime_binding": binding("score"),
            "run_report_sha256": digest,
            "worklist_sha256": digest,
            "prompt": experiment.SCORE_PROMPT,
            "items": score_items,
        }
        return {"prep": prep, "run": run, "score": score}

    def _prep_archive(self, worklist_path, execution_path, worklist):
        analyses = []
        verdicts = []
        for job in worklist["jobs"]:
            path = Path(job["artifact_path"])
            lines = path.read_text(encoding="utf-8").splitlines()
            line_number = next(i + 1 for i, line in enumerate(lines) if "return " in line)
            excerpt = lines[line_number - 1]
            citations = [
                {
                    "line_start": line_number,
                    "line_end": line_number,
                    "excerpt": excerpt,
                }
            ]
            analysis = {
                "job_id": job["job_id"],
                "artifact_sha256": job["artifact_sha256"],
                "role": "producer",
                "semantics": "Returns a normalized control value to its direct callee.",
                "citations": citations,
            }
            analyses.append(analysis)
            verdicts.append(
                {
                    "job_id": job["job_id"],
                    "artifact_sha256": job["artifact_sha256"],
                    "mode": "adversarial",
                    "verdict": "accept",
                    "role": analysis["role"],
                    "semantics": analysis["semantics"],
                    "citations": citations,
                    "rationale": "The exact machine line supports the target-independent claim.",
                }
            )
        result = {
            "schema": experiment.PREP_RESULT_SCHEMA,
            "execution_config_sha256": self.manifest["execution_config_sha256"],
            "private_manifest_sha256": experiment.file_sha256(self.private_path),
            "worklist_sha256": experiment.file_sha256(worklist_path),
            "analyses": analyses,
            "verdicts": verdicts,
        }
        return {
            "runId": "wf_prep-fixture",
            **self._script_fields("prep"),
            "args": experiment.read_json(execution_path),
            "result": result,
            "workflowOutput": self._workflow_output("prep", result),
            "status": "completed",
            "launch": self._fresh_launch(),
        }

    def _build_candidates(self):
        _prep_dir, worklist_path, execution_path, worklist = self._build_prep()
        archive_path = self.runtime / "prep-archive.json"
        experiment.write_json(
            archive_path, self._prep_archive(worklist_path, execution_path, worklist)
        )
        candidates_path = self.runtime / "card-candidates.json"
        candidates = experiment.validate_prep_results(
            self.private_path,
            worklist_path,
            execution_path,
            archive_path,
            candidates_path,
        )
        return candidates_path, candidates

    def _build_cards(self):
        candidates_path, candidates = self._build_candidates()
        approvals_path = self.runtime / "card-approvals.json"
        approvals = {
            "schema": experiment.CARD_APPROVALS_SCHEMA,
            "candidates_sha256": experiment.file_sha256(candidates_path),
            "review_policy": experiment.CARD_APPROVAL_POLICY,
            "operator_attested": True,
            "cards": [
                {
                    "card_id": item["card_id"],
                    "payload_sha256": item["payload_sha256"],
                    "decision": "approve",
                    "rationale": "Manual fixture approval of exact candidate payload.",
                }
                for item in candidates["cards"]
            ],
        }
        experiment.write_json(approvals_path, approvals)
        cards_path = self.runtime / "cards.json"
        cards = experiment.finalize_cards(
            self.private_path,
            candidates_path,
            approvals_path,
            cards_path,
        )
        return cards_path, cards

    def _build_conditions(self):
        cards_path, cards = self._build_cards()
        conditions_path = self.runtime / "conditions.json"
        conditions = experiment.build_conditions(
            self.private_path,
            cards_path,
            self.runtime / "condition-files",
            self.runtime / "public",
            self.runtime / "execution",
            conditions_path,
        )
        return cards_path, cards, conditions_path, conditions

    def _run_archive(self, condition):
        worklist_path = Path(condition["public_worklist"])
        worklist = experiment.read_json(worklist_path)
        truth_by_pair = {item["pair_id"]: item["truth"] for item in self.manifest["maps"]}
        exposed_by_pair = {
            item["pair_id"]: bool(item["direct_callers"]) for item in self.manifest["maps"]
        }
        condition_kind = self.manifest["condition_mapping"][condition["condition_id"]]
        analyses = []
        verdicts = []
        for job in worklist["jobs"]:
            truth = truth_by_pair[job["pair_id"]]
            artifact_lines = Path(job["artifact_path"]).read_text(encoding="utf-8").splitlines()
            site_line = next(
                index + 1
                for index, line in enumerate(artifact_lines)
                if line.startswith("site 00020000 reads map")
            )
            trace_line = next(
                index + 1
                for index, line in enumerate(artifact_lines)
                if line.startswith("trace 00020000 writes ffff0001")
            )
            citations = [
                {
                    "line_start": site_line,
                    "line_end": site_line,
                    "excerpt": artifact_lines[site_line - 1],
                },
                {
                    "line_start": trace_line,
                    "line_end": trace_line,
                    "excerpt": artifact_lines[trace_line - 1],
                },
            ]
            analyses.append(
                {
                    "job_id": job["job_id"],
                    "condition_id": job["condition_id"],
                    "pair_id": job["pair_id"],
                    "target_address": job["target_address"],
                    "artifact_sha256": job["artifact_sha256"],
                    "status": "completed",
                    "decision": "accept_code",
                    "role": truth["role"],
                    "semantics": (
                        "Caller-context fixture proposal for scoring."
                        if exposed_by_pair[job["pair_id"]] and condition_kind == "verified"
                        else "Neutral fixture proposal for scoring."
                    ),
                    "disposition": truth["disposition"] or "unresolved",
                    "target": "ffff0001",
                    "evidence": "site:00020000",
                    "machine_references": "00020000, ffff0001",
                    "citations": citations,
                }
            )
            verdicts.append(
                {
                    "job_id": job["job_id"],
                    "condition_id": job["condition_id"],
                    "artifact_sha256": job["artifact_sha256"],
                    "mode": "adversarial",
                    "verdict": "accept",
                    "analysis": copy.deepcopy(analyses[-1]),
                    "rationale": "Fixture verifier confirms the structured proposal.",
                }
            )
        result = {
            "schema": experiment.RUN_RESULT_SCHEMA,
            "execution_config_sha256": self.manifest["execution_config_sha256"],
            "condition_id": condition["condition_id"],
            "worklist_sha256": experiment.file_sha256(worklist_path),
            "analyses": analyses,
            "verdicts": verdicts,
        }
        return {
            "runId": "wf_run-" + condition["condition_id"],
            **self._script_fields("run"),
            "args": experiment.read_json(Path(condition["execution_input"])),
            "result": result,
            "workflowOutput": self._workflow_output("run", result),
            "status": "completed",
            "launch": self._fresh_launch(),
        }

    def _score_archive(self, run_report_path, worklist_path, execution_path):
        worklist = experiment.read_json(worklist_path)
        _expected, _execution, mapping = experiment.score_documents(
            self.private_path, run_report_path
        )
        kind_by_id = self.manifest["condition_mapping"]
        exposed_by_pair = {
            item["pair_id"]: bool(item["direct_callers"]) for item in self.manifest["maps"]
        }
        scores = []
        for item in worklist["items"]:
            mapped = mapping[item["score_id"]]
            value = (
                1.0
                if kind_by_id[mapped["condition_id"]] == "verified"
                and exposed_by_pair[mapped["pair_id"]]
                else 0.5
            )
            scores.append(
                {
                    "score_id": item["score_id"],
                    "candidate_sha256": item["candidate_sha256"],
                    "score": value,
                    "rationale": "Fixture arm-blind semantics score.",
                }
            )
        result = {
            "schema": experiment.SCORE_RESULT_SCHEMA,
            "execution_config_sha256": self.manifest["execution_config_sha256"],
            "run_report_sha256": experiment.file_sha256(run_report_path),
            "worklist_sha256": experiment.file_sha256(worklist_path),
            "scores": scores,
        }
        return {
            "runId": "wf_score-fixture",
            **self._script_fields("score"),
            "args": experiment.read_json(execution_path),
            "result": result,
            "workflowOutput": self._workflow_output("score", result),
            "status": "completed",
            "launch": self._fresh_launch(),
        }

    def test_frozen_selection_and_digest_are_exact_and_stable(self):
        again = experiment.build_private_manifest(
            ROOT,
            self.accessors,
            self.calls,
            self.exports,
            self.originals,
            self.audit_path,
            self.originals_replica,
            self.audit_replica_path,
            id_secret=self.id_secret,
        )
        self.assertEqual(self.manifest, again)
        self.assertEqual([item["addr"] for item in self.manifest["maps"]], list(experiment.ADDRESSES))
        self.assertEqual(len(self.manifest["maps"]), 24)
        self.assertEqual(len(self.manifest["callers"]), 21)
        self.assertEqual(
            self.manifest["export_cohort"]["root"], str(self.exports.resolve())
        )
        self.assertEqual(len(self.manifest["export_cohort"]["blind_audits"]), 2)
        self.assertEqual(
            {
                addr: item["sha256"]
                for addr, item in self.manifest["artifacts"]["original_maps"].items()
            },
            {
                addr: item["sha256"]
                for addr, item in self.manifest["artifacts"]["independent_maps"].items()
            },
        )
        self.assertEqual(
            hashlib.sha256("\n".join(experiment.ADDRESSES).encode()).hexdigest(),
            experiment.ADDRESS_LIST_SHA256,
        )
        self.assertEqual(
            self.manifest["selection_diversity_objective"],
            list(experiment.SELECTION_DIVERSITY_OBJECTIVE),
        )
        self.assertEqual(
            self.manifest["selection_tie_break_sha256"],
            experiment.SELECTION_TIE_BREAK_SHA256,
        )
        self.assertEqual(experiment.stable_json_bytes(self.manifest), experiment.stable_json_bytes(again))

    def test_private_manifest_is_rederived_from_frozen_sources(self):
        stale_schema = copy.deepcopy(self.manifest)
        stale_schema["schema"] = "vq.caller-semantics-private/v3"
        with self.assertRaisesRegex(experiment.ExperimentError, "private-manifest"):
            experiment.validate_private_manifest(stale_schema)

        stale_config = copy.deepcopy(self.manifest)
        stale_config["execution_config"]["schema"] = (
            "vq.caller-semantics-execution-config/v2"
        )
        with self.assertRaisesRegex(experiment.ExperimentError, "execution config"):
            experiment.validate_private_manifest(stale_config)

        forged_truth = copy.deepcopy(self.manifest)
        forged_truth["maps"][0]["truth"]["semantics"] = "Forged truth semantics."
        with self.assertRaisesRegex(experiment.ExperimentError, "frozen git blobs"):
            experiment.validate_private_manifest(forged_truth)

        forged_mapping = copy.deepcopy(self.manifest)
        forged_mapping["maps"][0]["direct_callers"] = forged_mapping["maps"][1][
            "direct_callers"
        ]
        with self.assertRaisesRegex(experiment.ExperimentError, "frozen git blobs"):
            experiment.validate_private_manifest(forged_mapping)

    def test_private_manifest_validation_uses_embedded_runtime_sources(self):
        builder_path = (ROOT / "tools" / "sweep" / "build_artifacts.py").resolve()
        original_read_text = Path.read_text

        def guarded_read_text(path, *args, **kwargs):
            if path.resolve() == builder_path:
                raise AssertionError("current builder source must not be read")
            return original_read_text(path, *args, **kwargs)

        with mock.patch.object(
            experiment,
            "execution_config",
            side_effect=AssertionError("current runtime files must not be read"),
        ), mock.patch.object(Path, "read_text", guarded_read_text):
            experiment.validate_private_manifest(self.manifest)

    def test_execution_inputs_embed_only_assigned_text_and_freeze_no_tools_policy(self):
        _prep, _worklist_path, execution_path, _worklist = self._build_prep()
        execution = experiment.read_json(execution_path)
        parsed = self._run_saved_parser("prep", execution)
        self.assertEqual(parsed.returncode, 0, msg=parsed.stderr)
        self.assertEqual(json.loads(parsed.stdout), execution)
        self.assertTrue(all("artifact_path" not in item for item in execution["items"]))
        self.assertTrue(all("artifact_text" in item for item in execution["items"]))
        for item in execution["items"]:
            self.assertEqual(item["artifact_text"].splitlines()[0], "# Caller context")
            for key in (
                "experiment_id",
                "condition_id",
                "pair_id",
                "job_id",
                "artifact_sha256",
            ):
                self.assertNotIn(item[key], item["artifact_text"])
        config = self.manifest["execution_config"]
        self.assertEqual(
            config["tool_policy"],
            "embedded_artifact_no_tools_exact_single_structured_call",
        )
        agent_text = (ROOT / experiment.BLIND_AGENT_FILE).read_text(encoding="utf-8")
        self.assertRegex(agent_text, r"(?m)^tools:\s*\[\]\s*$")
        for entry in config["workflows"].values():
            self.assertEqual(
                entry["sha256"], experiment.file_sha256(ROOT / entry["path"])
            )
        prep_workflow = (ROOT / experiment.WORKFLOW_FILES["prep"]).read_text(
            encoding="utf-8"
        )
        run_workflow = (ROOT / experiment.WORKFLOW_FILES["run"]).read_text(
            encoding="utf-8"
        )
        score_workflow = (ROOT / experiment.WORKFLOW_FILES["score"]).read_text(
            encoding="utf-8"
        )
        self.assertNotIn("Opaque job metadata", prep_workflow + run_workflow)
        for marker in (
            "${item.job_id}",
            "${item.condition_id}",
            "${item.pair_id}",
            "${item.target_address}",
            "${item.artifact_sha256}",
        ):
            self.assertNotIn(marker, prep_workflow + run_workflow)
        self.assertNotIn("${item.score_id}", score_workflow)
        self.assertNotIn("${item.candidate_sha256}", score_workflow)
        self.assertNotIn("${item.reference_semantics}", score_workflow)
        self.assertNotIn("${item.candidate_semantics}", score_workflow)
        self.assertIn("JSON.stringify({", score_workflow)
        self.assertIn("job_id: row.item.job_id", prep_workflow + run_workflow)
        self.assertIn("score_id: row.item.score_id", score_workflow)

    def test_no_tools_policy_requires_single_frontmatter_tools_key(self):
        malicious = (
            "---\n"
            "name: vq-ab-blind-worker\n"
            "tools: [Read]\n"
            "---\n\n"
            "Decoy policy text:\n"
            "tools: []\n"
        )
        self.assertFalse(experiment.blind_agent_has_no_tools(malicious))
        duplicated = (
            "---\n"
            "name: vq-ab-blind-worker\n"
            "tools: []\n"
            "tools: []\n"
            "---\n"
        )
        self.assertFalse(experiment.blind_agent_has_no_tools(duplicated))

        config = copy.deepcopy(self.manifest["execution_config"])
        config["blind_agent"]["content"] = malicious
        config["blind_agent"]["sha256"] = experiment.sha256_bytes(
            malicious.encode("utf-8")
        )
        with self.assertRaisesRegex(
            experiment.ExperimentError,
            "embedded source does not verify blind agent",
        ):
            experiment.validate_execution_config(config)

    def test_no_tools_policy_rejects_nested_tools_decoy(self):
        nested = (
            "---\n"
            "name: vq-ab-blind-worker\n"
            "metadata:\n"
            "  tools: []\n"
            "---\n"
        )
        self.assertFalse(experiment.blind_agent_has_no_tools(nested))

    def test_saved_workflow_input_parser_accepts_object_and_json_string(self):
        for kind, payload in self._saved_parser_payloads().items():
            for label, json_string in (("object", False), ("json-string", True)):
                completed = self._run_saved_parser(
                    kind,
                    payload,
                    json_string=json_string,
                )
                self.assertEqual(
                    completed.returncode,
                    0,
                    msg=f"{kind}/{label}: {completed.stderr}",
                )
                self.assertEqual(json.loads(completed.stdout), payload)

    def test_saved_workflow_preflight_rejects_non_frozen_execution(self):
        minimal = {
            "prep": {"items": [], "prompts": {}},
            "run": {"items": [], "prompts": {}},
            "score": {"items": [], "prompt": "fixture"},
        }
        for kind, payload in minimal.items():
            completed = self._run_saved_parser(kind, payload)
            self.assertNotEqual(completed.returncode, 0, msg=kind)

        for kind, payload in self._saved_parser_payloads().items():
            incomplete = copy.deepcopy(payload)
            incomplete["items"].pop()
            completed = self._run_saved_parser(kind, incomplete)
            self.assertNotEqual(completed.returncode, 0, msg=f"{kind}/incomplete")

            extra = copy.deepcopy(payload)
            extra["unexpected"] = True
            completed = self._run_saved_parser(kind, extra)
            self.assertNotEqual(completed.returncode, 0, msg=f"{kind}/extra")

    def test_archive_preflight_rejects_artifact_text_hash_mismatch(self):
        _prep, _worklist_path, execution_path, _worklist = self._build_prep()
        execution = experiment.read_json(execution_path)
        execution["items"][0]["artifact_text"] += "\nmutated"
        with self.assertRaisesRegex(
            experiment.ExperimentError,
            "frozen payload schema",
        ):
            experiment.validate_archive_execution_input(execution, "prep")

    def test_public_projection_has_no_private_mapping_or_answers(self):
        _prep, _path, _execution, worklist = self._build_prep()
        experiment.validate_public_projection(worklist)
        raw = experiment.stable_json_bytes(worklist).decode()
        self.assertNotIn("truth", raw)
        self.assertNotIn("direct_callers", raw)
        self.assertNotIn("accessors", raw)
        self.assertTrue(all(set(job) == experiment.PUBLIC_JOB_KEYS for job in worklist["jobs"]))

    def test_private_secret_hides_condition_mapping_from_public_inputs(self):
        legacy = {
            "cond-" + experiment.opaque_id(
                "condition", self.manifest["experiment_id"], kind
            )
            for kind in ("verified", "placebo")
        }
        self.assertTrue(legacy.isdisjoint(self.manifest["condition_mapping"]))
        _prep, _path, _execution, worklist = self._build_prep()
        raw = experiment.stable_json_bytes(worklist).decode()
        self.assertNotIn(self.id_secret, raw)
        expected = experiment.expected_ids(self.manifest)
        self.assertEqual(self.manifest["condition_mapping"], expected["condition_mapping"])

    def test_public_projection_rejects_null_and_descriptive_ids(self):
        _prep, _path, _execution, worklist = self._build_prep()
        null_id = copy.deepcopy(worklist)
        null_id["jobs"][0]["condition_id"] = None
        with self.assertRaisesRegex(experiment.ExperimentError, "must be a string"):
            experiment.validate_public_projection(null_id)
        descriptive = copy.deepcopy(worklist)
        descriptive["jobs"][0]["pair_id"] = "truth-table-private-answer"
        with self.assertRaisesRegex(experiment.ExperimentError, "opaque id"):
            experiment.validate_public_projection(descriptive)
        null_path = copy.deepcopy(worklist)
        null_path["jobs"][0]["artifact_path"] = None
        with self.assertRaisesRegex(experiment.ExperimentError, "must be a string"):
            experiment.validate_public_projection(null_path)

    def test_public_projection_allows_incidental_a_or_b_path_segments(self):
        _prep, _path, _execution, worklist = self._build_prep()
        allowed = copy.deepcopy(worklist)
        original_name = Path(allowed["jobs"][0]["artifact_path"]).name
        allowed["jobs"][0]["artifact_path"] = str(Path("/tmp/a") / original_name)
        experiment.validate_public_projection(allowed)

        descriptive = copy.deepcopy(worklist)
        descriptive["jobs"][0]["artifact_path"] = str(
            Path("/tmp/enriched") / original_name
        )
        with self.assertRaisesRegex(experiment.ExperimentError, "exposes a condition name"):
            experiment.validate_public_projection(descriptive)

    def test_sample_addresses_are_masked_in_common_forms(self):
        addr = experiment.ADDRESSES[0]
        text = f"{addr} 0x{addr} 0x{addr.lstrip('0')} DAT_{addr} PTR_DAT_{addr.upper()}"
        masked = experiment.mask_sample_addresses(text)
        self.assertNotIn(addr, masked.casefold())
        self.assertFalse(experiment.HEX8.search(masked))
        self.assertIn("DAT_XXXXXXXX", masked)

    def test_prep_neutralizes_human_authored_ghidra_function_names(self):
        funcs = self.runtime / "named-funcs.csv"
        funcs.write_text(
            "addr,name\n00010000,airflow_controller\n00020000,fuel_target_lookup\n",
            encoding="utf-8",
        )
        manifest = {
            "sources": [
                {
                    "kind": "ghidra_functions_export",
                    "path": str(funcs.resolve()),
                }
            ]
        }
        text = "int airflow_controller(void) { return fuel_target_lookup(); }"
        neutral = experiment.neutralize_function_names(text, manifest)
        self.assertEqual(
            neutral,
            "int FUN_00010000(void) { return FUN_00020000(); }",
        )
        self.assertNotIn("airflow", neutral)
        self.assertNotIn("fuel_target", neutral)

    def test_prep_neutralizes_data_symbols_comments_and_literals(self):
        funcs = self.runtime / "symbols-funcs.csv"
        funcs.write_text("addr,name\n00010000,FUN_00010000\n", encoding="utf-8")
        manifest = {
            "sources": [
                {
                    "kind": "ghidra_functions_export",
                    "path": str(funcs.resolve()),
                }
            ]
        }
        text = (
            'int FUN_00010000(void) { /* fuel target */ '
            'return fuel_target_table[airflow] + PTR_s_FUEL_TARGET_00020000[0]; }'
        )
        neutral = experiment.neutralize_function_names(text, manifest)
        self.assertNotIn("fuel", neutral.casefold())
        self.assertNotIn("airflow", neutral.casefold())
        self.assertIn("DAT_00020000", neutral)
        self.assertRegex(neutral, r"ID_\d{4}")

    def test_prep_neutralizes_semantic_auto_prefixed_locals(self):
        funcs = self.runtime / "auto-locals-funcs.csv"
        funcs.write_text("addr,name\n00010000,FUN_00010000\n", encoding="utf-8")
        manifest = {
            "sources": [
                {
                    "kind": "ghidra_functions_export",
                    "path": str(funcs.resolve()),
                }
            ]
        }
        text = (
            "int FUN_00010000(int paramFuelTarget, int param_fuel_target) { "
            "int localIgnitionLimit = local_airflow_limit + uVarFuel + param_1; "
            "return paramFuelTarget + localIgnitionLimit + param_1; }"
        )
        neutral = experiment.neutralize_function_names(text, manifest)
        for leaked in (
            "paramFuelTarget",
            "param_fuel_target",
            "localIgnitionLimit",
            "local_airflow_limit",
            "uVarFuel",
            "param_1",
        ):
            self.assertNotIn(leaked, neutral)
        identifiers = experiment.re.findall(r"ID_\d{4}", neutral)
        self.assertGreaterEqual(len(identifiers), 7)
        self.assertEqual(identifiers[0], identifiers[-3])

    def test_prep_is_deterministic_and_neutralizes_identifier_leaks(self):
        prep, worklist_path, execution_path, first = self._build_prep()
        second = experiment.build_prep(
            self.private_path, prep, worklist_path, execution_path
        )
        self.assertEqual(first, second)
        caller = self.manifest["callers"][0]
        path = Path(caller["decomp_path"])
        original = path.read_text(encoding="utf-8")
        secret_semantics = self.manifest["maps"][0]["truth"]["semantics"]
        path.write_text(
            original + "-".join(secret_semantics.split()) + "\n", encoding="utf-8"
        )
        leaky_manifest = experiment.build_private_manifest(
            ROOT,
            self.accessors,
            self.calls,
            self.exports,
            self.originals,
            self.audit_path,
            self.originals_replica,
            self.audit_replica_path,
            id_secret=self.id_secret,
        )
        leaky_private = self.runtime / "leaky-private.json"
        experiment.write_json(leaky_private, leaky_manifest)
        public = experiment.build_prep(
            leaky_private,
            self.runtime / "leaky-prep",
            self.runtime / "leaky-worklist.json",
            self.runtime / "leaky-execution.json",
        )
        rendered = "\n".join(
            Path(job["artifact_path"]).read_text(encoding="utf-8")
            for job in public["jobs"]
        )
        self.assertNotIn("-".join(secret_semantics.split()), rendered)

    def test_freeze_requires_matching_blind_audit_inventory(self):
        target = self.originals / f"map-{experiment.ADDRESSES[0]}.md"
        target.write_text(
            target.read_text(encoding="utf-8")
            + self.manifest["maps"][0]["truth"]["semantics"]
            + "\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(experiment.ExperimentError, "blind audit: SHA-256 drift"):
            experiment.build_private_manifest(
                ROOT,
                self.accessors,
                self.calls,
                self.exports,
                self.originals,
                self.audit_path,
                self.originals_replica,
                self.audit_replica_path,
                id_secret=self.id_secret,
            )

    def test_freeze_rejects_stale_map_artifact_outside_frozen_inventory(self):
        (self.originals / "map-deadbeef.md").write_text(
            "# stale fixture\n", encoding="utf-8"
        )
        with self.assertRaisesRegex(experiment.ExperimentError, "exact directory inventory"):
            experiment.build_private_manifest(
                ROOT,
                self.accessors,
                self.calls,
                self.exports,
                self.originals,
                self.audit_path,
                self.originals_replica,
                self.audit_replica_path,
                id_secret=self.id_secret,
            )

    def test_freeze_binds_blind_audit_to_caller_export_directory(self):
        audit = experiment.read_json(self.audit_path)
        audit["export_dir"] = str((self.runtime / "other-exports").resolve())
        wrong_audit = self.runtime / "wrong-export-audit.json"
        experiment.write_json(wrong_audit, audit)
        with self.assertRaisesRegex(experiment.ExperimentError, "Ghidra export directory"):
            experiment.build_private_manifest(
                ROOT,
                self.accessors,
                self.calls,
                self.exports,
                self.originals,
                wrong_audit,
                self.originals_replica,
                self.audit_replica_path,
                id_secret=self.id_secret,
            )

    def test_freeze_rejects_ghidra_source_outside_export_cohort(self):
        outside_calls = self.runtime / "outside-calls.csv"
        outside_calls.write_bytes(self.calls.read_bytes())
        with self.assertRaisesRegex(experiment.ExperimentError, "outside the shared cohort root"):
            experiment.build_private_manifest(
                ROOT,
                self.accessors,
                outside_calls,
                self.exports,
                self.originals,
                self.audit_path,
                self.originals_replica,
                self.audit_replica_path,
                id_secret=self.id_secret,
            )

    def test_freeze_rejects_symlink_in_recursive_export_inventory(self):
        link = self.exports / "linked-funcs.csv"
        link.symlink_to(self.exports / "funcs.csv")
        with self.assertRaisesRegex(experiment.ExperimentError, "cohort contains a symlink"):
            experiment.build_private_manifest(
                ROOT,
                self.accessors,
                self.calls,
                self.exports,
                self.originals,
                self.audit_path,
                self.originals_replica,
                self.audit_replica_path,
                id_secret=self.id_secret,
            )

    def test_freeze_requires_byte_identical_independent_builds(self):
        target = self.originals_replica / f"map-{experiment.ADDRESSES[0]}.md"
        target.write_text(
            target.read_text(encoding="utf-8") + "replica drift\n",
            encoding="utf-8",
        )
        replica_audit = self.runtime / "drifted-replica-audit.json"
        self._write_blind_audit(self.originals_replica, replica_audit)
        with self.assertRaisesRegex(experiment.ExperimentError, "not byte-identical"):
            experiment.build_private_manifest(
                ROOT,
                self.accessors,
                self.calls,
                self.exports,
                self.originals,
                self.audit_path,
                self.originals_replica,
                replica_audit,
                id_secret=self.id_secret,
            )

    def test_freeze_repeats_private_truth_leak_scan_for_both_builds(self):
        leaked = self.manifest["maps"][0]["truth"]["semantics"]
        for directory in (self.originals, self.originals_replica):
            target = directory / f"map-{experiment.ADDRESSES[0]}.md"
            target.write_text(
                target.read_text(encoding="utf-8") + leaked + "\n",
                encoding="utf-8",
            )
        primary_audit = self.runtime / "leaky-primary-audit.json"
        replica_audit = self.runtime / "leaky-replica-audit.json"
        self._write_blind_audit(self.originals, primary_audit)
        self._write_blind_audit(self.originals_replica, replica_audit)
        with self.assertRaisesRegex(experiment.ExperimentError, "private-truth leakage"):
            experiment.build_private_manifest(
                ROOT,
                self.accessors,
                self.calls,
                self.exports,
                self.originals,
                primary_audit,
                self.originals_replica,
                replica_audit,
                id_secret=self.id_secret,
            )

    def test_archive_workflow_embeds_native_output_and_script_source(self):
        _prep, worklist_path, execution_path, worklist = self._build_prep()
        fixture = self._prep_archive(worklist_path, execution_path, worklist)
        native_path = self.runtime / "prep-native-output.json"
        experiment.write_json(native_path, fixture["workflowOutput"])
        archive_path = self.runtime / "prep-native-archive.json"
        archive = experiment.build_workflow_archive(
            fixture["runId"],
            Path(fixture["scriptPath"]),
            execution_path,
            native_path,
            archive_path,
            True,
        )
        self.assertEqual(archive["scriptSource"], fixture["scriptSource"])
        self.assertEqual(archive["scriptSha256"], fixture["scriptSha256"])
        self.assertEqual(archive["workflowOutput"], fixture["workflowOutput"])
        experiment.validate_prep_results(
            self.private_path,
            worklist_path,
            execution_path,
            archive_path,
            self.runtime / "native-candidates.json",
        )

        persisted_script = self.runtime / "persisted-session-workflow.js"
        persisted_script.write_text(fixture["scriptSource"], encoding="utf-8")
        persisted_archive = self.runtime / "persisted-script-archive.json"
        experiment.build_workflow_archive(
            "wf_persisted-script",
            persisted_script,
            execution_path,
            native_path,
            persisted_archive,
            True,
        )
        self.assertTrue(persisted_archive.is_file())

        invalid_output = self.runtime / "invalid-run-id-archive.json"
        with self.assertRaisesRegex(experiment.ExperimentError, "invalid fresh runId"):
            experiment.build_workflow_archive(
                "wf-invalid",
                Path(fixture["scriptPath"]),
                execution_path,
                native_path,
                invalid_output,
                True,
            )
        self.assertFalse(invalid_output.exists())

        with self.assertRaisesRegex(
            experiment.ExperimentError, "fresh-launch attestation"
        ):
            experiment.build_workflow_archive(
                fixture["runId"],
                Path(fixture["scriptPath"]),
                execution_path,
                native_path,
                self.runtime / "unattested-archive.json",
                False,
            )

    def test_archive_rejects_self_consistent_alternate_runtime_binding(self):
        _prep, worklist_path, execution_path, worklist = self._build_prep()
        fixture = self._prep_archive(worklist_path, execution_path, worklist)
        native_path = self.runtime / "alternate-binding-native.json"
        experiment.write_json(native_path, fixture["workflowOutput"])

        alternate_script = ROOT / "tools" / "sweep" / "caller_ab_experiment.py"
        forged_execution = experiment.read_json(execution_path)
        forged_execution["runtime_binding"]["workflow_path"] = (
            alternate_script.relative_to(ROOT).as_posix()
        )
        forged_execution["runtime_binding"]["workflow_sha256"] = (
            experiment.file_sha256(alternate_script)
        )
        forged_execution_path = self.runtime / "alternate-binding-execution.json"
        experiment.write_json(forged_execution_path, forged_execution)
        output_path = self.runtime / "alternate-binding-archive.json"

        with self.assertRaisesRegex(
            experiment.ExperimentError, "runtime binding.*live frozen contract"
        ):
            experiment.build_workflow_archive(
                "wf_alternate-binding",
                alternate_script,
                forged_execution_path,
                native_path,
                output_path,
                True,
            )
        self.assertFalse(output_path.exists())

    def test_archive_rejects_unknown_workflow_progress_records(self):
        _prep, worklist_path, execution_path, worklist = self._build_prep()
        fixture = self._prep_archive(worklist_path, execution_path, worklist)
        native = copy.deepcopy(fixture["workflowOutput"])
        native["workflowProgress"].append(
            {"type": "workflow_error", "message": "worker failed"}
        )
        native_path = self.runtime / "workflow-error-native.json"
        output_path = self.runtime / "workflow-error-archive.json"
        experiment.write_json(native_path, native)

        with self.assertRaisesRegex(
            experiment.ExperimentError,
            "unknown progress record",
        ):
            experiment.build_workflow_archive(
                "wf_workflow-error",
                Path(fixture["scriptPath"]),
                execution_path,
                native_path,
                output_path,
                True,
            )
        self.assertFalse(output_path.exists())

    def test_archive_rejects_non_official_opus_model_names(self):
        _prep, worklist_path, execution_path, worklist = self._build_prep()
        fixture = self._prep_archive(worklist_path, execution_path, worklist)
        for index, model in enumerate(
            ("nonopus", "not-opus", "claude-sonnet-opus-compat"),
            start=1,
        ):
            native = self._workflow_output("prep", fixture["result"], model=model)
            native_path = self.runtime / f"non-opus-native-{index}.json"
            output_path = self.runtime / f"non-opus-archive-{index}.json"
            experiment.write_json(native_path, native)
            with self.assertRaisesRegex(
                experiment.ExperimentError,
                "official Claude Opus model",
            ):
                experiment.build_workflow_archive(
                    f"wf_non-opus-{index}",
                    Path(fixture["scriptPath"]),
                    execution_path,
                    native_path,
                    output_path,
                    True,
                )
            self.assertFalse(output_path.exists())

    def test_archive_rejects_unlisted_opus_model_versions(self):
        _prep, worklist_path, execution_path, worklist = self._build_prep()
        fixture = self._prep_archive(worklist_path, execution_path, worklist)
        models = (
            "claude-opus-999-1",
            "claude-opus-999-999",
            "claude-opus-0-0[0k]",
            "claude-opus-4-8[999m]",
        )
        for index, model in enumerate(models, start=1):
            native = self._workflow_output("prep", fixture["result"], model=model)
            native_path = self.runtime / f"unlisted-opus-native-{index}.json"
            output_path = self.runtime / f"unlisted-opus-archive-{index}.json"
            experiment.write_json(native_path, native)
            with self.assertRaisesRegex(
                experiment.ExperimentError,
                "official Claude Opus model",
            ):
                experiment.build_workflow_archive(
                    f"wf_unlisted-opus-{index}",
                    Path(fixture["scriptPath"]),
                    execution_path,
                    native_path,
                    output_path,
                    True,
                )
            self.assertFalse(output_path.exists())

    def test_archive_rejects_invalid_native_result_before_write(self):
        _prep, worklist_path, execution_path, worklist = self._build_prep()
        fixture = self._prep_archive(worklist_path, execution_path, worklist)
        cases = []

        wrong_schema = copy.deepcopy(fixture["workflowOutput"])
        wrong_schema["result"]["schema"] = "wrong"
        cases.append(("wrong-schema", wrong_schema))

        extra_field = copy.deepcopy(fixture["workflowOutput"])
        extra_field["result"]["unexpected"] = True
        cases.append(("extra-field", extra_field))

        incomplete = copy.deepcopy(fixture["workflowOutput"])
        incomplete["result"]["analyses"].pop()
        cases.append(("incomplete", incomplete))

        for label, native in cases:
            native_path = self.runtime / f"invalid-result-{label}.json"
            output_path = self.runtime / f"invalid-result-{label}-archive.json"
            experiment.write_json(native_path, native)
            with self.assertRaisesRegex(
                experiment.ExperimentError,
                "archive-workflow:.*result|prep analyses",
            ):
                experiment.build_workflow_archive(
                    f"wf_invalid-result-{label}",
                    Path(fixture["scriptPath"]),
                    execution_path,
                    native_path,
                    output_path,
                    True,
                )
            self.assertFalse(output_path.exists())

    def test_archive_rejects_malformed_prep_field_types_before_write(self):
        _prep, worklist_path, execution_path, worklist = self._build_prep()
        fixture = self._prep_archive(worklist_path, execution_path, worklist)
        native = copy.deepcopy(fixture["workflowOutput"])
        native["result"]["analyses"][0]["role"] = {"text": "producer"}
        native["result"]["verdicts"][0]["role"] = {"text": "producer"}
        native_path = self.runtime / "malformed-prep-field-native.json"
        output_path = self.runtime / "malformed-prep-field-archive.json"
        experiment.write_json(native_path, native)
        with self.assertRaisesRegex(experiment.ExperimentError, "prep payload"):
            experiment.build_workflow_archive(
                "wf_malformed-prep-field",
                Path(fixture["scriptPath"]),
                execution_path,
                native_path,
                output_path,
                True,
            )
        self.assertFalse(output_path.exists())

    def test_archive_rejects_prep_verify_payload_mismatch_before_write(self):
        _prep, worklist_path, execution_path, worklist = self._build_prep()
        fixture = self._prep_archive(worklist_path, execution_path, worklist)
        native = copy.deepcopy(fixture["workflowOutput"])
        native["result"]["verdicts"][0]["semantics"] = "Different claim."
        native_path = self.runtime / "prep-verify-mismatch-native.json"
        output_path = self.runtime / "prep-verify-mismatch-archive.json"
        experiment.write_json(native_path, native)
        with self.assertRaisesRegex(
            experiment.ExperimentError,
            "exact Analyze payload",
        ):
            experiment.build_workflow_archive(
                "wf_prep-verify-mismatch",
                Path(fixture["scriptPath"]),
                execution_path,
                native_path,
                output_path,
                True,
            )
        self.assertFalse(output_path.exists())

    def test_archive_rejects_whitespace_only_citation_before_write(self):
        _prep, worklist_path, execution_path, worklist = self._build_prep()
        fixture = self._prep_archive(worklist_path, execution_path, worklist)
        native = copy.deepcopy(fixture["workflowOutput"])
        for section in ("analyses", "verdicts"):
            native["result"][section][0]["citations"][0]["excerpt"] = "\n"
        native_path = self.runtime / "whitespace-citation-native.json"
        output_path = self.runtime / "whitespace-citation-archive.json"
        experiment.write_json(native_path, native)
        with self.assertRaisesRegex(experiment.ExperimentError, "prep payload"):
            experiment.build_workflow_archive(
                "wf_whitespace-citation",
                Path(fixture["scriptPath"]),
                execution_path,
                native_path,
                output_path,
                True,
            )
        self.assertFalse(output_path.exists())

    def test_archive_rejects_unbound_prep_citation_before_write(self):
        _prep, worklist_path, execution_path, worklist = self._build_prep()
        fixture = self._prep_archive(worklist_path, execution_path, worklist)
        native = copy.deepcopy(fixture["workflowOutput"])
        artifact_text = experiment.read_json(execution_path)["items"][0]["artifact_text"]
        forged = {
            "line_start": 1,
            "line_end": 1,
            "excerpt": artifact_text.splitlines()[0],
        }
        native["result"]["analyses"][0]["citations"] = [forged]
        native["result"]["verdicts"][0]["citations"] = [copy.deepcopy(forged)]
        native_path = self.runtime / "unbound-prep-citation-native.json"
        output_path = self.runtime / "unbound-prep-citation-archive.json"
        experiment.write_json(native_path, native)
        with self.assertRaisesRegex(
            experiment.ExperimentError,
            "citation is outside machine evidence",
        ):
            experiment.build_workflow_archive(
                "wf_unbound-prep-citation",
                Path(fixture["scriptPath"]),
                execution_path,
                native_path,
                output_path,
                True,
            )
        self.assertFalse(output_path.exists())

    def test_archive_rejects_failed_run_analysis_before_write(self):
        _cards_path, _cards, _conditions_path, conditions = self._build_conditions()
        condition = conditions["conditions"][0]
        fixture = self._run_archive(condition)
        native = copy.deepcopy(fixture["workflowOutput"])
        native["result"]["analyses"][0]["status"] = "failed"
        native["result"]["verdicts"][0]["analysis"]["status"] = "failed"
        native_path = self.runtime / "failed-run-native.json"
        output_path = self.runtime / "failed-run-archive.json"
        experiment.write_json(native_path, native)
        with self.assertRaisesRegex(experiment.ExperimentError, "adversarial verdict"):
            experiment.build_workflow_archive(
                "wf_failed-run-analysis",
                Path(fixture["scriptPath"]),
                Path(condition["execution_input"]),
                native_path,
                output_path,
                True,
            )
        self.assertFalse(output_path.exists())

    def test_archive_rejects_unbound_run_citation_before_write(self):
        _cards_path, _cards, _conditions_path, conditions = self._build_conditions()
        condition = conditions["conditions"][0]
        execution_path = Path(condition["execution_input"])
        fixture = self._run_archive(condition)
        native = copy.deepcopy(fixture["workflowOutput"])
        artifact_text = experiment.read_json(execution_path)["items"][0]["artifact_text"]
        analysis = native["result"]["analyses"][0]
        analysis["citations"] = [
            {
                "line_start": 1,
                "line_end": 1,
                "excerpt": artifact_text.splitlines()[0],
            }
        ]
        native["result"]["verdicts"][0]["analysis"] = copy.deepcopy(analysis)
        native_path = self.runtime / "unbound-run-citation-native.json"
        output_path = self.runtime / "unbound-run-citation-archive.json"
        experiment.write_json(native_path, native)
        with self.assertRaisesRegex(
            experiment.ExperimentError,
            "citation is outside machine evidence",
        ):
            experiment.build_workflow_archive(
                "wf_unbound-run-citation",
                Path(fixture["scriptPath"]),
                execution_path,
                native_path,
                output_path,
                True,
            )
        self.assertFalse(output_path.exists())

    def test_archive_rejects_run_verify_payload_mismatch_before_write(self):
        _cards_path, _cards, _conditions_path, conditions = self._build_conditions()
        condition = conditions["conditions"][0]
        fixture = self._run_archive(condition)
        native = copy.deepcopy(fixture["workflowOutput"])
        native["result"]["verdicts"][0]["analysis"]["semantics"] = (
            "Different verified payload."
        )
        native_path = self.runtime / "run-verify-mismatch-native.json"
        output_path = self.runtime / "run-verify-mismatch-archive.json"
        experiment.write_json(native_path, native)
        with self.assertRaisesRegex(
            experiment.ExperimentError,
            "exact Analyze payload",
        ):
            experiment.build_workflow_archive(
                "wf_run-verify-mismatch",
                Path(fixture["scriptPath"]),
                Path(condition["execution_input"]),
                native_path,
                output_path,
                True,
            )
        self.assertFalse(output_path.exists())

    def test_archive_rejects_arm_marker_in_prep_verifier_rationale_before_write(self):
        _prep, worklist_path, execution_path, worklist = self._build_prep()
        fixture = self._prep_archive(worklist_path, execution_path, worklist)
        native = copy.deepcopy(fixture["workflowOutput"])
        native["result"]["verdicts"][0]["rationale"] = (
            "The baseline arm confirms this payload."
        )
        native_path = self.runtime / "prep-rationale-arm-native.json"
        output_path = self.runtime / "prep-rationale-arm-archive.json"
        experiment.write_json(native_path, native)
        with self.assertRaisesRegex(
            experiment.ExperimentError,
            "payload exposes a condition name",
        ):
            experiment.build_workflow_archive(
                "wf_prep-rationale-arm",
                Path(fixture["scriptPath"]),
                execution_path,
                native_path,
                output_path,
                True,
            )
        self.assertFalse(output_path.exists())

    def test_archive_rejects_arm_marker_in_run_verifier_rationale_before_write(self):
        _cards_path, _cards, _conditions_path, conditions = self._build_conditions()
        condition = conditions["conditions"][0]
        fixture = self._run_archive(condition)
        native = copy.deepcopy(fixture["workflowOutput"])
        native["result"]["verdicts"][0]["rationale"] = (
            "The baseline arm confirms this payload."
        )
        native_path = self.runtime / "run-rationale-arm-native.json"
        output_path = self.runtime / "run-rationale-arm-archive.json"
        experiment.write_json(native_path, native)
        with self.assertRaisesRegex(
            experiment.ExperimentError,
            "payload exposes a condition name",
        ):
            experiment.build_workflow_archive(
                "wf_run-rationale-arm",
                Path(fixture["scriptPath"]),
                Path(condition["execution_input"]),
                native_path,
                output_path,
                True,
            )
        self.assertFalse(output_path.exists())

    def test_archive_rejects_retry_cache_aliases_in_agent_progress(self):
        _prep, worklist_path, execution_path, worklist = self._build_prep()
        fixture = self._prep_archive(worklist_path, execution_path, worklist)
        for index, (key, value) in enumerate(
            (
                ("retryCount", 1),
                ("retries", 1),
                ("cacheReuse", True),
                ("fallbackUsed", True),
            ),
            start=1,
        ):
            native = copy.deepcopy(fixture["workflowOutput"])
            native["workflowProgress"][0][key] = value
            native_path = self.runtime / f"provenance-alias-{index}.json"
            output_path = self.runtime / f"provenance-alias-{index}-archive.json"
            experiment.write_json(native_path, native)
            with self.assertRaisesRegex(
                experiment.ExperimentError,
                "fallback/retry/cache provenance",
            ):
                experiment.build_workflow_archive(
                    f"wf_provenance-alias-{index}",
                    Path(fixture["scriptPath"]),
                    execution_path,
                    native_path,
                    output_path,
                    True,
                )
            self.assertFalse(output_path.exists())

    def test_archive_rejects_retry_cache_fallback_in_progress_values(self):
        _prep, worklist_path, execution_path, worklist = self._build_prep()
        fixture = self._prep_archive(worklist_path, execution_path, worklist)
        cases = (
            ("source", "cache"),
            ("executionMode", "retry"),
            ("provenance", "fallback"),
            ("source", "resume"),
        )
        for index, (key, value) in enumerate(cases, start=1):
            native = copy.deepcopy(fixture["workflowOutput"])
            native["workflowProgress"][0][key] = value
            native_path = self.runtime / f"provenance-value-{index}.json"
            output_path = self.runtime / f"provenance-value-{index}-archive.json"
            experiment.write_json(native_path, native)
            with self.assertRaisesRegex(
                experiment.ExperimentError,
                "fallback/retry/cache provenance",
            ):
                experiment.build_workflow_archive(
                    f"wf_provenance-value-{index}",
                    Path(fixture["scriptPath"]),
                    execution_path,
                    native_path,
                    output_path,
                    True,
                )
            self.assertFalse(output_path.exists())

    def test_archive_rejects_noncanonical_phase_indexes(self):
        _prep, worklist_path, execution_path, worklist = self._build_prep()
        fixture = self._prep_archive(worklist_path, execution_path, worklist)
        phase_cases = (
            [
                {"type": "workflow_phase", "index": 1, "title": "Analyze"},
                {"type": "workflow_phase", "index": 1, "title": "Verify"},
            ],
            [
                {"type": "workflow_phase", "index": 2, "title": "Analyze"},
                {"type": "workflow_phase", "index": 1, "title": "Verify"},
            ],
            [
                {"type": "workflow_phase", "index": 1, "title": "Analyze"},
                {"type": "workflow_phase", "index": 3, "title": "Verify"},
            ],
        )
        for index, phases in enumerate(phase_cases, start=1):
            native = copy.deepcopy(fixture["workflowOutput"])
            native["workflowProgress"] = phases + native["workflowProgress"]
            native_path = self.runtime / f"phase-sequence-{index}.json"
            output_path = self.runtime / f"phase-sequence-{index}-archive.json"
            experiment.write_json(native_path, native)
            with self.assertRaisesRegex(
                experiment.ExperimentError,
                "frozen phase sequence",
            ):
                experiment.build_workflow_archive(
                    f"wf_phase-sequence-{index}",
                    Path(fixture["scriptPath"]),
                    execution_path,
                    native_path,
                    output_path,
                    True,
                )
            self.assertFalse(output_path.exists())

    def test_archive_rejects_fallback_extra_tools_retry_cache_and_nonfresh_launch(self):
        _prep, worklist_path, execution_path, worklist = self._build_prep()
        base = self._prep_archive(worklist_path, execution_path, worklist)
        cases = []

        fallback = copy.deepcopy(base)
        fallback["workflowOutput"]["workflowProgress"][0]["fallbackModel"] = (
            "claude-sonnet-fixture"
        )
        cases.append(("fallback", fallback, "fallback/retry/cache provenance"))

        fallback_null = copy.deepcopy(base)
        fallback_null["workflowOutput"]["workflowProgress"][0]["fallbackModel"] = None
        cases.append(
            ("fallback-null", fallback_null, "fallback/retry/cache provenance")
        )

        extra_tool = copy.deepcopy(base)
        extra_tool["workflowOutput"]["workflowProgress"][0]["toolCalls"] = 2
        cases.append(("extra-tool", extra_tool, "exactly one tool"))

        zero_tokens = copy.deepcopy(base)
        zero_tokens["workflowOutput"]["totalTokens"] = 0
        cases.append(("zero-tokens", zero_tokens, "totalTokens"))

        retry = copy.deepcopy(base)
        retry["workflowOutput"]["workflowProgress"][0]["attempt"] = 2
        cases.append(("retry", retry, "retry/cache provenance"))

        cache = copy.deepcopy(base)
        cache["workflowOutput"]["workflowProgress"][0]["cacheHit"] = False
        cases.append(("cache", cache, "retry/cache provenance"))

        for label, key, value in (
            ("root-retry", "retryCount", 1),
            ("root-cache", "cacheHit", False),
            ("root-fallback", "fallbackModel", "claude-sonnet-fixture"),
            ("root-unknown", "undocumentedField", "value"),
        ):
            root_extra = copy.deepcopy(base)
            root_extra["workflowOutput"][key] = value
            cases.append(
                (label, root_extra, "exact native-output schema")
            )

        nonfresh = copy.deepcopy(base)
        nonfresh["launch"]["operatorAttested"] = False
        cases.append(("nonfresh", nonfresh, "fresh-launch attestation"))

        for label, archive, message in cases:
            path = self.runtime / f"prep-{label}.json"
            experiment.write_json(path, archive)
            with self.assertRaisesRegex(experiment.ExperimentError, message):
                experiment.validate_prep_results(
                    self.private_path,
                    worklist_path,
                    execution_path,
                    path,
                    self.runtime / f"cards-{label}.json",
                )

    def test_status_handles_nonobject_json_roots_and_continues(self):
        paths = []
        for name, value in (
            ("array.json", []),
            ("scalar.json", 7),
            ("null.json", None),
            ("object.json", {"schema": "fixture/v1"}),
        ):
            path = self.runtime / name
            experiment.write_json(path, value)
            paths.append(str(path))
        paths.append(str(self.runtime / "missing.json"))

        with mock.patch("builtins.print") as printed:
            experiment.cmd_status(mock.Mock(path=paths))
        document = json.loads(printed.call_args.args[0])
        self.assertEqual(len(document), 5)
        self.assertEqual(
            [item.get("error") for item in document[:3]],
            ["JSON root is not an object"] * 3,
        )
        self.assertEqual(document[3]["schema"], "fixture/v1")
        self.assertFalse(document[4]["exists"])

    def test_live_runtime_binding_rejects_source_drift(self):
        runtime_repo = self.runtime / "runtime-binding"
        agent_path = runtime_repo / "agent.md"
        workflow_path = runtime_repo / "workflow.js"
        agent_path.parent.mkdir(parents=True)
        agent_path.write_text("tools: []\n", encoding="utf-8")
        workflow_path.write_text("return {}\n", encoding="utf-8")
        binding = {
            "blind_agent_path": "agent.md",
            "blind_agent_sha256": experiment.file_sha256(agent_path),
            "workflow_path": "workflow.js",
            "workflow_sha256": experiment.file_sha256(workflow_path),
        }
        experiment.validate_live_runtime_binding(binding, runtime_repo)
        workflow_path.write_text("return { drift: true }\n", encoding="utf-8")
        with self.assertRaisesRegex(experiment.ExperimentError, "live runtime source drift"):
            experiment.validate_live_runtime_binding(binding, runtime_repo)

    def test_validate_prep_freezes_candidates_and_rejects_ambiguity(self):
        _prep, worklist_path, execution_path, worklist = self._build_prep()
        archive = self._prep_archive(worklist_path, execution_path, worklist)
        archive_path = self.runtime / "prep-archive.json"
        experiment.write_json(archive_path, archive)
        candidates_path = self.runtime / "card-candidates.json"
        candidates = experiment.validate_prep_results(
            self.private_path,
            worklist_path,
            execution_path,
            archive_path,
            candidates_path,
        )
        self.assertEqual(candidates["schema"], experiment.CARD_CANDIDATES_SCHEMA)
        self.assertEqual(len(candidates["cards"]), 21)
        self.assertEqual(candidates, experiment.read_json(candidates_path))
        for item in candidates["cards"]:
            payload = {
                key: value for key, value in item.items() if key != "payload_sha256"
            }
            self.assertEqual(
                item["payload_sha256"],
                experiment.sha256_bytes(
                    experiment.stable_json_bytes(payload, pretty=False)
                ),
            )

        broken = copy.deepcopy(archive)
        broken["result"]["analyses"][0]["semantics"] = (
            "Possibly an unknown target-specific value."
        )
        broken["result"]["verdicts"][0]["semantics"] = broken[
            "result"
        ]["analyses"][0]["semantics"]
        broken_path = self.runtime / "ambiguous.json"
        experiment.write_json(broken_path, broken)
        with self.assertRaisesRegex(experiment.ExperimentError, "ambiguous"):
            experiment.validate_prep_results(
                self.private_path,
                worklist_path,
                execution_path,
                broken_path,
                self.runtime / "bad-candidates.json",
            )

        multiline = copy.deepcopy(archive)
        multiline["result"]["analyses"][0]["semantics"] = "First line.\nSecond line."
        multiline["result"]["verdicts"][0]["semantics"] = multiline[
            "result"
        ]["analyses"][0]["semantics"]
        multiline_path = self.runtime / "multiline.json"
        experiment.write_json(multiline_path, multiline)
        with self.assertRaisesRegex(experiment.ExperimentError, "single-line"):
            experiment.validate_prep_results(
                self.private_path,
                worklist_path,
                execution_path,
                multiline_path,
                self.runtime / "multiline-candidates.json",
            )

    def test_validate_prep_rejects_non_ascii_caller_cards(self):
        _prep, worklist_path, execution_path, worklist = self._build_prep()
        archive = self._prep_archive(worklist_path, execution_path, worklist)
        semantics = "Returns a naïve local value."
        archive["result"]["analyses"][0]["semantics"] = semantics
        archive["result"]["verdicts"][0]["semantics"] = semantics
        path = self.runtime / "non-ascii-card.json"
        candidates = self.runtime / "non-ascii-candidates.json"
        experiment.write_json(path, archive)

        with self.assertRaisesRegex(experiment.ExperimentError, "printable ASCII English"):
            experiment.validate_prep_results(
                self.private_path,
                worklist_path,
                execution_path,
                path,
                candidates,
            )
        self.assertFalse(candidates.exists())

    def test_validate_prep_rejects_arm_markers_in_card_text(self):
        _prep, worklist_path, execution_path, worklist = self._build_prep()
        for index, marker in enumerate(("verified", "placebo", "baseline", "treatment")):
            archive = self._prep_archive(worklist_path, execution_path, worklist)
            analysis = archive["result"]["analyses"][0]
            verdict = archive["result"]["verdicts"][0]
            analysis["role"] = f"{marker} producer"
            verdict["role"] = analysis["role"]
            path = self.runtime / f"arm-marker-{index}.json"
            experiment.write_json(path, archive)
            with self.assertRaisesRegex(
                experiment.ExperimentError, "exposes a condition name"
            ):
                experiment.validate_prep_results(
                    self.private_path,
                    worklist_path,
                    execution_path,
                    path,
                    self.runtime / f"arm-marker-candidates-{index}.json",
                )

    def test_validate_prep_rejects_html_encoded_arm_markers(self):
        _prep, worklist_path, execution_path, worklist = self._build_prep()
        archive = self._prep_archive(worklist_path, execution_path, worklist)
        encoded = "veri&#102;ied producer"
        archive["result"]["analyses"][0]["role"] = encoded
        archive["result"]["verdicts"][0]["role"] = encoded
        path = self.runtime / "html-arm-marker.json"
        experiment.write_json(path, archive)
        with self.assertRaisesRegex(
            experiment.ExperimentError,
            "exposes a condition name",
        ):
            experiment.validate_prep_results(
                self.private_path,
                worklist_path,
                execution_path,
                path,
                self.runtime / "html-arm-marker-candidates.json",
            )

    def test_finalize_cards_requires_complete_exact_manual_approvals(self):
        candidates_path, candidates = self._build_candidates()

        def approvals():
            return {
                "schema": experiment.CARD_APPROVALS_SCHEMA,
                "candidates_sha256": experiment.file_sha256(candidates_path),
                "review_policy": experiment.CARD_APPROVAL_POLICY,
                "operator_attested": True,
                "cards": [
                    {
                        "card_id": item["card_id"],
                        "payload_sha256": item["payload_sha256"],
                        "decision": "approve",
                        "rationale": "Reviewed against the cited caller artifact.",
                    }
                    for item in candidates["cards"]
                ],
            }

        approved_path = self.runtime / "approved.json"
        experiment.write_json(approved_path, approvals())
        cards_path = self.runtime / "final-cards.json"
        cards = experiment.finalize_cards(
            self.private_path,
            candidates_path,
            approved_path,
            cards_path,
        )
        self.assertEqual(cards["schema"], experiment.CARDS_SCHEMA)
        self.assertEqual(cards, experiment.read_json(cards_path))

        stale_cards = copy.deepcopy(cards)
        stale_cards["schema"] = "vq.caller-semantics-cards/v3"
        with self.assertRaisesRegex(experiment.ExperimentError, "unknown .*schema"):
            experiment.validate_cards(stale_cards, self.private_path, self.manifest)

        unattested = approvals()
        unattested["operator_attested"] = False
        unattested_path = self.runtime / "unattested-approval.json"
        experiment.write_json(unattested_path, unattested)
        with self.assertRaisesRegex(
            experiment.ExperimentError, "manual-review attestation"
        ):
            experiment.finalize_cards(
                self.private_path,
                candidates_path,
                unattested_path,
                self.runtime / "unattested-cards.json",
            )

        rejected = approvals()
        rejected["cards"][0]["decision"] = "reject"
        rejected_path = self.runtime / "rejected.json"
        experiment.write_json(rejected_path, rejected)
        with self.assertRaisesRegex(experiment.ExperimentError, "not approved"):
            experiment.finalize_cards(
                self.private_path,
                candidates_path,
                rejected_path,
                self.runtime / "rejected-cards.json",
            )

        missing = approvals()
        missing["cards"].pop()
        missing_path = self.runtime / "missing-approval.json"
        experiment.write_json(missing_path, missing)
        with self.assertRaisesRegex(experiment.ExperimentError, "do not cover"):
            experiment.finalize_cards(
                self.private_path,
                candidates_path,
                missing_path,
                self.runtime / "missing-cards.json",
            )

        drifted = approvals()
        drifted["cards"][0]["payload_sha256"] = "0" * 64
        drifted_path = self.runtime / "drifted-approval.json"
        experiment.write_json(drifted_path, drifted)
        with self.assertRaisesRegex(experiment.ExperimentError, "payload drift"):
            experiment.finalize_cards(
                self.private_path,
                candidates_path,
                drifted_path,
                self.runtime / "drifted-cards.json",
            )

    def test_prep_archive_rejects_extra_fields_and_recovery_metadata(self):
        _prep, worklist_path, execution_path, worklist = self._build_prep()
        archive = self._prep_archive(worklist_path, execution_path, worklist)

        extra = copy.deepcopy(archive)
        extra["result"]["extra"] = "not frozen"
        extra_path = self.runtime / "prep-extra.json"
        experiment.write_json(extra_path, extra)
        with self.assertRaisesRegex(experiment.ExperimentError, "frozen schema"):
            experiment.validate_prep_results(
                self.private_path,
                worklist_path,
                execution_path,
                extra_path,
                self.runtime / "extra-cards.json",
            )

        recovery = copy.deepcopy(archive)
        recovery["resumeFromRunId"] = "wf-previous"
        recovery_path = self.runtime / "prep-recovery.json"
        experiment.write_json(recovery_path, recovery)
        with self.assertRaisesRegex(
            experiment.ExperimentError, "frozen envelope|recovery/resume"
        ):
            experiment.validate_prep_results(
                self.private_path,
                worklist_path,
                execution_path,
                recovery_path,
                self.runtime / "recovery-cards.json",
            )

    def test_validate_prep_rejects_consistent_wrong_pair_id(self):
        _prep, worklist_path, execution_path, worklist = self._build_prep()
        forged = copy.deepcopy(worklist)
        forged["jobs"][0]["pair_id"] = "pair-" + "a" * 24
        forged_worklist = self.runtime / "forged-worklist.json"
        experiment.write_json(forged_worklist, forged)
        forged_execution = self.runtime / "forged-prep-execution.json"
        experiment.write_json(
            forged_execution,
            experiment.prep_execution_document(self.private_path, forged_worklist),
        )
        archive = self._prep_archive(forged_worklist, forged_execution, forged)
        archive["result"]["worklist_sha256"] = experiment.file_sha256(forged_worklist)
        forged_archive = self.runtime / "forged-prep-archive.json"
        experiment.write_json(forged_archive, archive)
        with self.assertRaisesRegex(experiment.ExperimentError, "frozen mapping"):
            experiment.validate_prep_results(
                self.private_path,
                forged_worklist,
                forged_execution,
                forged_archive,
                self.runtime / "forged-cards.json",
            )

    def test_build_conditions_revalidates_card_provenance(self):
        cards_path, cards = self._build_cards()
        forged = copy.deepcopy(cards)
        forged["cards"][0]["semantics"] = "Target-specific private interpretation."
        forged_path = self.runtime / "forged-cards.json"
        experiment.write_json(forged_path, forged)
        with self.assertRaisesRegex(
            experiment.ExperimentError, "approved frozen candidates"
        ):
            experiment.build_conditions(
                self.private_path,
                forged_path,
                self.runtime / "forged-condition-files",
                self.runtime / "forged-public",
                self.runtime / "forged-execution",
                self.runtime / "forged-conditions.json",
            )
        self.assertTrue(cards_path.is_file())

    def test_condition_placebos_are_neutral_and_only_card_blocks_differ(self):
        cards_path, _cards, conditions_path, conditions = self._build_conditions()
        by_kind = experiment.verify_condition_document(conditions, self.private_path, cards_path)
        self.assertEqual(conditions["placebo_contract"], experiment.PLACEBO_CONTRACT)
        self.assertTrue(
            all(item["stochastic_replicates"] == 1 for item in conditions["conditions"])
        )
        verified = {
            item["pair_id"]: item
            for item in by_kind["verified"]["integrity_copies"][0]["files"]
        }
        placebo = {
            item["pair_id"]: item
            for item in by_kind["placebo"]["integrity_copies"][0]["files"]
        }
        exposed = next(item for item in self.manifest["maps"] if item["direct_callers"])
        left = Path(verified[exposed["pair_id"]]["path"]).read_bytes()
        right = Path(placebo[exposed["pair_id"]]["path"]).read_bytes()
        lb, lc, la = experiment.split_card_block(left)
        rb, rc, ra = experiment.split_card_block(right)
        self.assertEqual((lb, la), (rb, ra))
        self.assertNotEqual(lc, rc)
        self.assertNotIn(b"xxxxx", rc)
        self.assertNotEqual(left, right)

        control = next(item for item in self.manifest["maps"] if not item["direct_callers"])
        control_left = Path(verified[control["pair_id"]]["path"]).read_bytes()
        control_right = Path(placebo[control["pair_id"]]["path"]).read_bytes()
        self.assertEqual(control_left, control_right)
        self.assertIn(b"role:", control_left)
        self.assertTrue(conditions_path.is_file())

    def test_condition_public_artifact_path_rejects_manifest_leak(self):
        cards_path, _cards, _conditions_path, conditions = self._build_conditions()
        forged = copy.deepcopy(conditions)
        condition = forged["conditions"][0]
        worklist = experiment.read_json(Path(condition["public_worklist"]))
        worklist["jobs"][0]["artifact_path"] = str(
            (self.runtime / f"leaked-{experiment.ADDRESSES[0]}.md").resolve()
        )
        forged_worklist = self.runtime / "forged-public-worklist.json"
        experiment.write_json(forged_worklist, worklist)
        condition["public_worklist"] = str(forged_worklist.resolve())
        condition["public_worklist_sha256"] = experiment.file_sha256(forged_worklist)
        with self.assertRaisesRegex(experiment.ExperimentError, "path leakage"):
            experiment.verify_condition_document(forged, self.private_path, cards_path)

    def test_integrity_copy_drift_is_rejected(self):
        cards_path, _cards, _conditions_path, conditions = self._build_conditions()
        target = Path(
            conditions["conditions"][0]["integrity_copies"][1]["files"][0]["path"]
        )
        target.write_bytes(target.read_bytes() + b"drift\n")
        with self.assertRaisesRegex(experiment.ExperimentError, "drift"):
            experiment.verify_condition_document(conditions, self.private_path, cards_path)

    def test_integrity_copy_and_file_schemas_are_exact(self):
        cards_path, _cards, _conditions_path, conditions = self._build_conditions()
        extra_copy_field = copy.deepcopy(conditions)
        extra_copy_field["conditions"][0]["integrity_copies"][0]["extra"] = True
        with self.assertRaisesRegex(experiment.ExperimentError, "frozen schema"):
            experiment.verify_condition_document(
                extra_copy_field, self.private_path, cards_path
            )

        extra_file_field = copy.deepcopy(conditions)
        extra_file_field["conditions"][0]["integrity_copies"][0]["files"][0][
            "extra"
        ] = True
        with self.assertRaisesRegex(experiment.ExperimentError, "frozen schema"):
            experiment.verify_condition_document(
                extra_file_field, self.private_path, cards_path
            )

    def test_integrity_copies_must_use_four_disjoint_directories(self):
        cards_path, _cards, _conditions_path, conditions = self._build_conditions()
        aliased = copy.deepcopy(conditions)
        first = aliased["conditions"][0]["integrity_copies"][0]
        aliased["conditions"][0]["integrity_copies"][1]["directory"] = first[
            "directory"
        ]
        aliased["conditions"][0]["integrity_copies"][1]["files"] = copy.deepcopy(
            first["files"]
        )
        with self.assertRaisesRegex(
            experiment.ExperimentError, "directory is duplicated|path is duplicated"
        ):
            experiment.verify_condition_document(
                aliased, self.private_path, cards_path
            )

    def test_run_requires_exact_24_analyses_and_verdicts_per_condition(self):
        cards_path, _cards, conditions_path, conditions = self._build_conditions()
        for condition in conditions["conditions"]:
            execution = experiment.read_json(Path(condition["execution_input"]))
            experiment.validate_archive_execution_input(execution, "run")
            parsed = self._run_saved_parser("run", execution)
            self.assertEqual(parsed.returncode, 0, msg=parsed.stderr)
            self.assertEqual(json.loads(parsed.stdout), execution)
        archives = []
        for index, condition in enumerate(conditions["conditions"]):
            archive = self._run_archive(condition)
            path = self.runtime / f"run-{index}.json"
            experiment.write_json(path, archive)
            archives.append(path)
        output = self.runtime / "runs.json"
        report = experiment.validate_runs(
            self.private_path, cards_path, conditions_path, archives, output
        )
        self.assertEqual([len(run["analyses"]) for run in report["runs"]], [24, 24])
        forged_report = copy.deepcopy(report)
        forged_report["runs"][0]["analyses"][0]["semantics"] = "Forged run report."
        forged_report_path = self.runtime / "forged-runs.json"
        experiment.write_json(forged_report_path, forged_report)
        with self.assertRaisesRegex(experiment.ExperimentError, "frozen Workflow archive"):
            experiment.score_documents(self.private_path, forged_report_path)
        empty_run_id = self._run_archive(conditions["conditions"][0])
        empty_run_id["runId"] = ""
        with self.assertRaisesRegex(experiment.ExperimentError, "invalid fresh runId"):
            experiment.validate_run_archive(
                empty_run_id, conditions["conditions"][0], self.private_path
            )
        wrong_script = self._run_archive(conditions["conditions"][0])
        wrong_script["scriptSource"] = self.calls.read_text(encoding="utf-8")
        wrong_script["scriptSha256"] = hashlib.sha256(
            wrong_script["scriptSource"].encode("utf-8")
        ).hexdigest()
        with self.assertRaisesRegex(experiment.ExperimentError, "another script"):
            experiment.validate_run_archive(
                wrong_script, conditions["conditions"][0], self.private_path
            )
        archived_path = self._run_archive(conditions["conditions"][0])
        archived_path["scriptPath"] = "/archived/session/path/no-longer-present.js"
        experiment.validate_run_archive(
            archived_path, conditions["conditions"][0], self.private_path
        )
        mixed_model = self._run_archive(conditions["conditions"][0])
        mixed_model["workflowOutput"]["workflowProgress"][0]["model"] = (
            "claude-other-fixture"
        )
        with self.assertRaisesRegex(experiment.ExperimentError, "mixes resolved models"):
            experiment.validate_run_archive(
                mixed_model, conditions["conditions"][0], self.private_path
            )
        changed_prompt = self._run_archive(conditions["conditions"][0])
        changed_prompt["args"]["prompts"]["analyze"] += " changed"
        with self.assertRaisesRegex(experiment.ExperimentError, "frozen execution input"):
            experiment.validate_run_archive(
                changed_prompt, conditions["conditions"][0], self.private_path
            )
        broken = self._run_archive(conditions["conditions"][0])
        broken["result"]["analyses"].pop()
        with self.assertRaisesRegex(experiment.ExperimentError, "run completeness"):
            experiment.validate_run_archive(broken, conditions["conditions"][0], self.private_path)
        recovery = self._run_archive(conditions["conditions"][0])
        recovery["args"]["recovery_identities"] = ["fixture"]
        with self.assertRaisesRegex(experiment.ExperimentError, "recovery"):
            experiment.validate_run_archive(recovery, conditions["conditions"][0], self.private_path)
        recovery_value = self._run_archive(conditions["conditions"][0])
        recovery_value["args"]["mode"] = "recovery"
        with self.assertRaisesRegex(experiment.ExperimentError, "recovery"):
            experiment.validate_run_archive(recovery_value, conditions["conditions"][0], self.private_path)
        nested = self._run_archive(conditions["conditions"][0])
        nested["args"]["metadata"] = {"mode": "resume"}
        with self.assertRaisesRegex(experiment.ExperimentError, "resume"):
            experiment.validate_run_archive(nested, conditions["conditions"][0], self.private_path)
        top_level = self._run_archive(conditions["conditions"][0])
        top_level["resumeFromRunId"] = "wf-previous"
        with self.assertRaisesRegex(experiment.ExperimentError, "frozen envelope|resume"):
            experiment.validate_run_archive(top_level, conditions["conditions"][0], self.private_path)
        extra_result = self._run_archive(conditions["conditions"][0])
        extra_result["result"]["extra"] = "not frozen"
        with self.assertRaisesRegex(experiment.ExperimentError, "frozen schema"):
            experiment.validate_run_archive(extra_result, conditions["conditions"][0], self.private_path)
        stale_result = self._run_archive(conditions["conditions"][0])
        stale_result["result"]["schema"] = "vq.caller-semantics-run-results/v3"
        with self.assertRaisesRegex(experiment.ExperimentError, "run-result schema"):
            experiment.validate_run_archive(
                stale_result, conditions["conditions"][0], self.private_path
            )
        legacy_trace = self._run_archive(conditions["conditions"][0])
        legacy_analysis = legacy_trace["result"]["analyses"][0]
        legacy_analysis["trace"] = legacy_analysis.pop("machine_references")
        legacy_trace["result"]["verdicts"][0]["analysis"] = copy.deepcopy(
            legacy_analysis
        )
        with self.assertRaisesRegex(experiment.ExperimentError, "completed-analysis"):
            experiment.validate_run_archive(
                legacy_trace, conditions["conditions"][0], self.private_path
            )
        extra_analysis = self._run_archive(conditions["conditions"][0])
        extra_analysis["result"]["analyses"][0]["extra"] = "not frozen"
        with self.assertRaisesRegex(experiment.ExperimentError, "completed-analysis"):
            experiment.validate_run_archive(extra_analysis, conditions["conditions"][0], self.private_path)
        extra_verdict = self._run_archive(conditions["conditions"][0])
        extra_verdict["result"]["verdicts"][0]["extra"] = "not frozen"
        with self.assertRaisesRegex(experiment.ExperimentError, "run-verdict"):
            experiment.validate_run_archive(extra_verdict, conditions["conditions"][0], self.private_path)
        changed_after_verify = self._run_archive(conditions["conditions"][0])
        changed_after_verify["result"]["analyses"][0]["semantics"] = (
            "A different but schema-valid semantics string."
        )
        with self.assertRaisesRegex(experiment.ExperimentError, "exact Analyze payload"):
            experiment.validate_run_archive(
                changed_after_verify, conditions["conditions"][0], self.private_path
            )
        multiline = self._run_archive(conditions["conditions"][0])
        multiline["result"]["analyses"][0]["semantics"] = "First line.\nSecond line."
        multiline["result"]["verdicts"][0]["analysis"] = copy.deepcopy(
            multiline["result"]["analyses"][0]
        )
        with self.assertRaisesRegex(experiment.ExperimentError, "one line"):
            experiment.validate_run_archive(
                multiline, conditions["conditions"][0], self.private_path
            )

    def test_run_rejects_arm_markers_before_blind_scoring(self):
        _cards_path, _cards, _conditions_path, conditions = self._build_conditions()
        condition = conditions["conditions"][0]
        for index, marker in enumerate(
            ("verified", "placebo", "baseline", "treatment", "enriched"),
            start=1,
        ):
            archive = self._run_archive(condition)
            analysis = archive["result"]["analyses"][0]
            analysis["semantics"] = f"{marker} arm output copied from context."
            archive["result"]["verdicts"][0]["analysis"] = copy.deepcopy(
                analysis
            )
            with self.assertRaisesRegex(
                experiment.ExperimentError,
                "payload exposes a condition name",
                msg=f"marker={marker}",
            ):
                experiment.validate_run_archive(
                    archive,
                    condition,
                    self.private_path,
                )

    def test_run_rejects_arm_markers_outside_semantics(self):
        _cards_path, _cards, _conditions_path, conditions = self._build_conditions()
        condition = conditions["conditions"][0]
        cases = (
            ("target", "verified arm output ffff0001"),
            ("machine_references", "placebo 00020000, ffff0001"),
            ("target", "veri&#102;ied arm output ffff0001"),
        )
        for field, value in cases:
            archive = self._run_archive(condition)
            analysis = archive["result"]["analyses"][0]
            analysis[field] = value
            archive["result"]["verdicts"][0]["analysis"] = copy.deepcopy(
                analysis
            )
            with self.assertRaisesRegex(
                experiment.ExperimentError,
                "payload exposes a condition name",
                msg=field,
            ):
                experiment.validate_run_archive(
                    archive,
                    condition,
                    self.private_path,
                )

    def test_run_rejects_unicode_format_controls_inside_arm_markers(self):
        _cards_path, _cards, _conditions_path, conditions = self._build_conditions()
        condition = conditions["conditions"][0]
        for index, value in enumerate(
            (
                "ver" + chr(0x200B) + "ified arm output.",
                "ver&#8203;ified arm output.",
            ),
            start=1,
        ):
            archive = self._run_archive(condition)
            analysis = archive["result"]["analyses"][0]
            analysis["semantics"] = value
            archive["result"]["verdicts"][0]["analysis"] = copy.deepcopy(
                analysis
            )
            with self.assertRaisesRegex(
                experiment.ExperimentError,
                "payload exposes a condition name",
                msg=f"case={index}",
            ):
                experiment.validate_run_archive(
                    archive,
                    condition,
                    self.private_path,
                )

    def test_run_rejects_unbound_machine_evidence(self):
        _cards_path, _cards, _conditions_path, conditions = self._build_conditions()
        condition = conditions["conditions"][0]

        outside_fence = self._run_archive(condition)
        analysis = outside_fence["result"]["analyses"][0]
        analysis["citations"] = [
            {"line_start": 1, "line_end": 1, "excerpt": "not machine evidence"}
        ]
        outside_fence["result"]["verdicts"][0]["analysis"] = copy.deepcopy(analysis)
        with self.assertRaisesRegex(
            experiment.ExperimentError, "citation is outside machine evidence"
        ):
            experiment.validate_run_archive(outside_fence, condition, self.private_path)

        forged_excerpt = self._run_archive(condition)
        analysis = forged_excerpt["result"]["analyses"][0]
        analysis["citations"][0]["excerpt"] = "forged machine line"
        forged_excerpt["result"]["verdicts"][0]["analysis"] = copy.deepcopy(analysis)
        with self.assertRaisesRegex(
            experiment.ExperimentError, "excerpt does not match"
        ):
            experiment.validate_run_archive(forged_excerpt, condition, self.private_path)

        outside_evidence = self._run_archive(condition)
        analysis = outside_evidence["result"]["analyses"][0]
        analysis["evidence"] = "site:deadbeef"
        outside_evidence["result"]["verdicts"][0]["analysis"] = copy.deepcopy(analysis)
        with self.assertRaisesRegex(
            experiment.ExperimentError, "evidence token refers outside"
        ):
            experiment.validate_run_archive(outside_evidence, condition, self.private_path)

        outside_trace = self._run_archive(condition)
        analysis = outside_trace["result"]["analyses"][0]
        analysis["machine_references"] = "00020000 -> deadbeef"
        outside_trace["result"]["verdicts"][0]["analysis"] = copy.deepcopy(analysis)
        with self.assertRaisesRegex(
            experiment.ExperimentError, "machine_references refers outside"
        ):
            experiment.validate_run_archive(outside_trace, condition, self.private_path)

        process_only = self._run_archive(condition)
        analysis = process_only["result"]["analyses"][0]
        analysis["evidence"] = "wave:00020000"
        process_only["result"]["verdicts"][0]["analysis"] = copy.deepcopy(analysis)
        with self.assertRaisesRegex(experiment.ExperimentError, "process-only evidence"):
            experiment.validate_run_archive(process_only, condition, self.private_path)

    def test_run_uses_canonical_evidence_grammar_and_address_coverage(self):
        _cards_path, _cards, _conditions_path, conditions = self._build_conditions()
        condition = conditions["conditions"][0]

        missing_property = self._run_archive(condition)
        analysis = missing_property["result"]["analyses"][0]
        analysis["evidence"] = "selector:00020000"
        missing_property["result"]["verdicts"][0]["analysis"] = copy.deepcopy(
            analysis
        )
        with self.assertRaisesRegex(experiment.ExperimentError, "@target_prop"):
            experiment.validate_run_archive(
                missing_property, condition, self.private_path
            )

        reordered = self._run_archive(condition)
        analysis = reordered["result"]["analyses"][0]
        analysis["machine_references"] = "ffff0001, 00020000"
        reordered["result"]["verdicts"][0]["analysis"] = copy.deepcopy(analysis)
        experiment.validate_run_archive(reordered, condition, self.private_path)

        target_without_address = self._run_archive(condition)
        analysis = target_without_address["result"]["analyses"][0]
        analysis["target"] = "downstream result"
        target_without_address["result"]["verdicts"][0]["analysis"] = copy.deepcopy(
            analysis
        )
        with self.assertRaisesRegex(
            experiment.ExperimentError, "result target contains no machine address"
        ):
            experiment.validate_run_archive(
                target_without_address, condition, self.private_path
            )

        uncited_target = self._run_archive(condition)
        analysis = uncited_target["result"]["analyses"][0]
        analysis["decision"] = "downgrade"
        analysis["machine_references"] = "00020000"
        analysis["citations"] = analysis["citations"][:1]
        uncited_target["result"]["verdicts"][0]["analysis"] = copy.deepcopy(analysis)
        with self.assertRaisesRegex(
            experiment.ExperimentError, "citations do not cover target address"
        ):
            experiment.validate_run_archive(
                uncited_target, condition, self.private_path
            )

        unresolved_accept = self._run_archive(condition)
        analysis = unresolved_accept["result"]["analyses"][0]
        analysis["disposition"] = "unresolved"
        unresolved_accept["result"]["verdicts"][0]["analysis"] = copy.deepcopy(
            analysis
        )
        with self.assertRaisesRegex(
            experiment.ExperimentError, "accept_code is incompatible with unresolved"
        ):
            experiment.validate_run_archive(
                unresolved_accept, condition, self.private_path
            )

    def test_run_evidence_accepts_addressless_terminal_and_raw_listing(self):
        artifact = self.runtime / "raw-machine-evidence.md"
        artifact.write_text(
            "00020000: mov.l @(0x10,r4),r1\n"
            "00020004: mov.l r1,@ffff0001\n"
            "Renesas SH7058-HW section 9.4\n",
            encoding="utf-8",
        )
        citations = [
            {"excerpt": "00020000: mov.l @(0x10,r4),r1"},
            {"excerpt": "00020004: mov.l r1,@ffff0001"},
            {"excerpt": "Renesas SH7058-HW section 9.4"},
        ]
        item = {
            "decision": "accept_code",
            "evidence": "spec:SH7058-HW;site:00020000",
            "machine_references": "00020000, 00020004, ffff0001",
            "target": "ffff0001",
        }
        unsupported_dependency = {
            **item,
            "evidence": "selector:00020000@confidence",
        }
        with self.assertRaisesRegex(
            experiment.ExperimentError, "without a frozen typed-support registry"
        ):
            experiment.validate_run_evidence_binding(
                unsupported_dependency,
                {"artifact_path": str(artifact)},
                citations,
                "raw-listing",
            )

        for terminal in ("spec:sh7058-hw", "spec:SH7058"):
            unsupported_terminal = {**item, "evidence": terminal}
            with self.assertRaisesRegex(
                experiment.ExperimentError, "terminal evidence"
            ):
                experiment.validate_run_evidence_binding(
                    unsupported_terminal,
                    {"artifact_path": str(artifact)},
                    citations,
                    "raw-listing",
                )

        canonical = experiment.validate_run_evidence_binding(
            item,
            {"artifact_path": str(artifact)},
            citations,
            "raw-listing",
        )
        self.assertEqual(canonical, "spec:SH7058-HW;site:00020000")

    def test_accept_code_requires_two_unique_machine_references(self):
        artifact = self.runtime / "one-machine-reference.md"
        artifact.write_text(
            "00020000: returns the local result\n",
            encoding="utf-8",
        )
        item = {
            "decision": "accept_code",
            "evidence": "site:00020000",
            "machine_references": "00020000, 00020000",
            "target": "00020000",
        }
        with self.assertRaisesRegex(
            experiment.ExperimentError, "at least two unique machine references"
        ):
            experiment.validate_run_evidence_binding(
                item,
                {"artifact_path": str(artifact)},
                [{"excerpt": "00020000: returns the local result"}],
                "duplicate-reference",
            )

    def test_scoring_projects_truth_evidence_to_terminal_run_domain(self):
        truth = {
            "confidence": "code",
            "role": "table",
            "disposition": "consumer",
            "target": "ffff0001",
            "evidence": (
                "site:00020000;rom_const:00020004=0x40;"
                "consumer:00020008@confidence"
            ),
            "trace": "00020000, 00020004, 00020008",
        }
        analysis = {
            "status": "completed",
            "decision": "accept_code",
            "role": "table",
            "disposition": "consumer",
            "target": "ffff0001",
            "evidence": "site:00020000;rom_const:00020004=0x40",
            "machine_references": "00020000, 00020004, 00020008",
        }
        scores = experiment.score_analysis(
            analysis,
            {"verdict": "accept"},
            truth,
            1.0,
        )
        self.assertEqual(scores["factual_evidence"], 1.0)
        self.assertEqual(scores["raw_total"], 1.0)

    def test_short_hex_scalars_are_not_machine_references(self):
        self.assertEqual(
            experiment.ordered_trace_addresses(
                "00020000 loads 0x40 then stores ffff0001"
            ),
            ["00020000", "ffff0001"],
        )

    def test_machine_reference_score_ignores_textual_order(self):
        truth = {
            "confidence": "code",
            "role": "table",
            "disposition": "writes",
            "target": "ffff0001",
            "evidence": "site:00020000",
            "trace": "00020000 -> ffff0001",
        }
        analysis = {
            "status": "completed",
            "decision": "accept_code",
            "role": "table",
            "semantics": "Fixture semantics.",
            "disposition": "writes",
            "target": "ffff0001",
            "evidence": "site:00020000",
            "machine_references": "ffff0001, 00020000",
        }
        score = experiment.score_analysis(
            analysis, {"verdict": "accept"}, truth, semantics_score=1.0
        )
        self.assertEqual(score["machine_reference_coverage"], 1.0)

    def test_refuted_analysis_has_zero_gated_total(self):
        truth = self.manifest["maps"][0]["truth"]
        analysis = {
            "status": "completed",
            "decision": "accept_code",
            "role": truth["role"],
            "semantics": truth["semantics"],
            "disposition": truth["disposition"],
            "target": truth["target"],
            "evidence": truth["evidence"],
            "machine_references": truth["trace"],
        }
        score = experiment.score_analysis(
            analysis, {"verdict": "refute"}, truth, semantics_score=1.0
        )
        self.assertGreater(score["raw_total"], 0)
        self.assertEqual(score["total"], 0)
        self.assertFalse(score["verifier_accepted"])

    def test_control_gate_rejects_cancellation_and_single_control_drift(self):
        def scores(**updates):
            value = {name: 0.0 for name in experiment.SCORE_METRIC_NAMES}
            value.update(updates)
            return value

        cancellation = [
            {
                "pair_id": "pair-control-1",
                "delta": 1.0,
                "scores": {
                    "verified": scores(role=1.0, total=1.0),
                    "placebo": scores(),
                },
            },
            {
                "pair_id": "pair-control-2",
                "delta": -1.0,
                "scores": {
                    "verified": scores(),
                    "placebo": scores(role=1.0, total=1.0),
                },
            },
        ]
        cancelled = experiment.summarize_control_gate(cancellation)
        self.assertEqual(cancelled["mean_delta"], 0.0)
        self.assertEqual(cancelled["max_abs_delta"], 1.0)
        self.assertFalse(cancelled["valid"])

        two_fields = [
            {
                "pair_id": "pair-control-1",
                "delta": 2 / 7,
                "scores": {
                    "verified": scores(
                        decision=1.0, role=1.0, raw_total=2 / 7, total=2 / 7
                    ),
                    "placebo": scores(),
                },
            },
            {
                "pair_id": "pair-control-2",
                "delta": 0.0,
                "scores": {"verified": scores(), "placebo": scores()},
            },
        ]
        drifted = experiment.summarize_control_gate(two_fields)
        self.assertEqual(
            [record["total_delta"] for record in drifted["records"]],
            [2 / 7, 0.0],
        )
        self.assertFalse(drifted["valid"])

        verifier_split = [
            {
                "pair_id": "pair-control-1",
                "delta": 0.0,
                "scores": {
                    "verified": scores(verifier_accepted=True),
                    "placebo": scores(verifier_accepted=False),
                },
            },
            {
                "pair_id": "pair-control-2",
                "delta": 0.0,
                "scores": {
                    "verified": scores(verifier_accepted=True),
                    "placebo": scores(verifier_accepted=True),
                },
            },
        ]
        split = experiment.summarize_control_gate(verifier_split)
        self.assertEqual(split["verifier_splits"], 1)
        self.assertTrue(split["records"][0]["verifier_split"])
        self.assertFalse(split["valid"])

    def test_paired_compare_reports_subgroups_costs_and_no_canonical_mutation(self):
        cards_path, _cards, conditions_path, conditions = self._build_conditions()
        archives = []
        for index, condition in enumerate(conditions["conditions"]):
            path = self.runtime / f"run-{index}.json"
            experiment.write_json(path, self._run_archive(condition))
            archives.append(path)
        runs_path = self.runtime / "runs.json"
        experiment.validate_runs(
            self.private_path, cards_path, conditions_path, archives, runs_path
        )
        score_worklist = self.runtime / "score-worklist.json"
        score_execution = self.runtime / "score-execution.json"
        experiment.build_score_inputs(
            self.private_path, runs_path, score_worklist, score_execution
        )
        score_execution_document = experiment.read_json(score_execution)
        experiment.validate_archive_execution_input(
            score_execution_document,
            "score",
        )
        parsed = self._run_saved_parser("score", score_execution_document)
        self.assertEqual(parsed.returncode, 0, msg=parsed.stderr)
        self.assertEqual(json.loads(parsed.stdout), score_execution_document)
        public_score = experiment.read_json(score_worklist)
        self.assertTrue(
            all(
                "pair_id" not in item and "condition_id" not in item
                for item in public_score["items"]
            )
        )
        score_archive = self.runtime / "score-archive.json"
        experiment.write_json(
            score_archive,
            self._score_archive(runs_path, score_worklist, score_execution),
        )
        semantics_path = self.runtime / "semantics.json"
        experiment.validate_score_archive(
            self.private_path,
            runs_path,
            score_worklist,
            score_execution,
            score_archive,
            semantics_path,
        )
        canonical = ROOT / "defs" / "JK08A.findings.csv"
        before = experiment.file_sha256(canonical)
        output = self.runtime / "comparison.json"
        result = experiment.compare_results(
            self.private_path, conditions_path, runs_path, semantics_path, output
        )
        self.assertEqual(result["summary"]["status"], "controls_passed")
        self.assertEqual(result["summary"]["raw"]["count"], 24)
        self.assertEqual(result["summary"]["observed_paired"]["count"], 22)
        self.assertEqual(result["summary"]["controls"]["count"], 2)
        self.assertGreater(result["summary"]["observed_paired"]["wins"], 0)
        self.assertFalse(result["summary"]["causal_claim"])
        self.assertFalse(result["automatic_application"])

        biased_archive = self._score_archive(runs_path, score_worklist, score_execution)
        _public, _execution, score_mapping = experiment.score_documents(
            self.private_path, runs_path
        )
        exposed_by_pair = {
            item["pair_id"]: bool(item["direct_callers"]) for item in self.manifest["maps"]
        }
        for score_item in biased_archive["result"]["scores"]:
            mapped = score_mapping[score_item["score_id"]]
            if (
                not exposed_by_pair[mapped["pair_id"]]
                and self.manifest["condition_mapping"][mapped["condition_id"]] == "verified"
            ):
                score_item["score"] = 1.0
        biased_archive_path = self.runtime / "biased-score-archive.json"
        experiment.write_json(biased_archive_path, biased_archive)
        biased_semantics = self.runtime / "biased-semantics.json"
        biased_document = experiment.validate_score_archive(
            self.private_path,
            runs_path,
            score_worklist,
            score_execution,
            biased_archive_path,
            biased_semantics,
        )
        control_scores = [
            item
            for item in biased_document["scores"]
            if not exposed_by_pair[item["pair_id"]]
        ]
        for pair_id in {item["pair_id"] for item in control_scores}:
            pair_scores = [
                item for item in control_scores if item["pair_id"] == pair_id
            ]
            self.assertEqual(len({item["score"] for item in pair_scores}), 2)
            self.assertTrue(
                all(
                    "pooled_score" not in item and "pool_size" not in item
                    for item in pair_scores
                )
            )
        biased_output = self.runtime / "biased-comparison.json"
        biased = experiment.compare_results(
            self.private_path,
            conditions_path,
            runs_path,
            biased_semantics,
            biased_output,
        )
        self.assertEqual(biased["summary"]["status"], "invalid_controls")
        self.assertFalse(biased["summary"]["controls"]["valid"])
        self.assertEqual(biased["summary"]["controls"]["max_abs_delta"], 0.5)
        self.assertIsNone(biased["summary"]["observed_paired"])
        self.assertFalse(biased["summary"]["causal_claim"])
        self.assertEqual(experiment.file_sha256(canonical), before)


class ClosureProfileTest(unittest.TestCase):
    def setUp(self):
        self.addCleanup(experiment.activate_profile, "full-v4")
        experiment.activate_profile("closure-v1")

    def test_frozen_scope_has_six_exposed_maps_and_two_controls(self):
        experiment.validate_address_scope()
        self.assertEqual(len(experiment.ADDRESSES), 8)
        self.assertEqual(experiment.EXPECTED_CALLER_COUNT, 5)
        self.assertEqual(experiment.EXPECTED_EXPOSED_COUNT, 6)
        self.assertEqual(experiment.EXPECTED_CONTROL_COUNT, 2)
        self.assertEqual(experiment.ROM, "JK08A")
        self.assertEqual(experiment.EXECUTION_MODE, "agent-protocol-v1")
        self.assertEqual(
            experiment.PREP_EXECUTION_SCHEMA,
            "vq.caller-semantics-prep-execution/v4",
        )

    def test_current_english_truth_extracts_complete_scoring_fields(self):
        data = experiment.git_source(
            ROOT,
            experiment.TRUTH_COMMIT,
            experiment.SOURCE_PATH,
        )
        _fields, rows = experiment.parse_csv_bytes(data, experiment.SOURCE_PATH)
        by_addr = {row["addr"]: row for row in rows}
        for addr in experiment.ADDRESSES:
            with self.subTest(addr=addr):
                truth = experiment.extract_truth(by_addr[addr])
                self.assertEqual(truth["confidence"], "code")
                self.assertIn(truth["role"], experiment.ROLES)
                self.assertIn(
                    truth["disposition"],
                    experiment.DISPOSITIONS - {"unresolved"},
                )
                self.assertTrue(truth["target"])
                self.assertTrue(truth["trace"])
                self.assertGreaterEqual(len(experiment.trace_addresses(truth["trace"])), 2)

    def test_execution_config_binds_protocol_without_agent_vendor(self):
        config = experiment.execution_config(ROOT)
        experiment.validate_execution_config(config)
        self.assertEqual(
            config["schema"],
            "vq.caller-semantics-execution-config/v4",
        )
        self.assertEqual(
            config["protocol"]["path"],
            "tools/sweep/agent_protocol.py",
        )
        self.assertNotIn("model", config)
        self.assertNotIn("workflows", config)
        self.assertNotIn("blind_agent", config)
        self.assertEqual(
            config["executor_policy"]["identity"],
            "same_exact_executor_all_phases_and_stages",
        )

    def test_control_plane_accepts_provider_neutral_prep_archive(self):
        protocol = experiment.agent_protocol
        config = experiment.execution_config(ROOT)
        binding = {
            "schema": protocol.PROTOCOL_SCHEMA,
            "protocol_path": config["protocol"]["path"],
            "protocol_sha256": config["protocol"]["sha256"],
        }
        artifact = (
            "# Caller context\n\n"
            "## Machine evidence\n\n"
            "```c\n"
            "return local_value;\n"
            "```\n"
        )
        execution = {
            "schema": experiment.PREP_EXECUTION_SCHEMA,
            "result_schema": experiment.PREP_RESULT_SCHEMA,
            "execution_config_sha256": experiment.execution_config_digest(config),
            "protocol_binding": binding,
            "private_manifest_sha256": "1" * 64,
            "worklist_sha256": "2" * 64,
            "prompts": {
                "analyze": experiment.PREP_ANALYZE_PROMPT,
                "verify": experiment.PREP_VERIFY_PROMPT,
            },
            "items": [
                {
                    "experiment_id": "exp-" + "1" * 14,
                    "condition_id": "cond-" + "2" * 14,
                    "pair_id": "pair-" + "3" * 14,
                    "job_id": "job-" + "4" * 14,
                    "target_address": "00001000",
                    "artifact_sha256": experiment.sha256_bytes(artifact.encode()),
                    "response_schema": experiment.PREP_RESPONSE_SCHEMA,
                    "artifact_text": artifact,
                }
            ],
        }
        normalized_binding = {
            "schema": binding["schema"],
            "sha256": binding["protocol_sha256"],
        }
        current_executor = {
            "schema": protocol.EXECUTOR_SCHEMA,
            "provider": "fixture-provider",
            "backend": "fixture-backend",
            "model": "fixture-model",
            "effort": "high",
            "adapter": "native-agent",
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
                "input_tokens": None,
                "output_tokens": None,
                "duration_ms": None,
                "cost_usd": None,
                "raw_output": response,
                "raw_output_sha256": protocol.value_sha256(response),
            }

        def result_bundle(batch, responses):
            return {
                "schema": protocol.TASK_RESULTS_SCHEMA,
                "batch_sha256": protocol.value_sha256(batch),
                "executor": current_executor,
                "operator_attested": True,
                "results": [
                    {
                        "task_id": task["task_id"],
                        "status": "completed",
                        "response": response,
                        "receipt": receipt(task["task_id"], response),
                    }
                    for task, response in zip(batch["tasks"], responses)
                ],
            }

        analysis = {
            "role": "machine value processor",
            "semantics": "Returns one locally computed machine value.",
            "citations": [
                {
                    "line_start": 6,
                    "line_end": 6,
                    "excerpt": "return local_value;",
                }
            ],
        }
        analyze_batch = protocol.build_batch(
            execution,
            "analyze",
            binding=normalized_binding,
        )
        analyze_results = result_bundle(analyze_batch, [analysis])
        verify_batch = protocol.build_batch(
            execution,
            "verify",
            prior_results=analyze_results,
            binding=normalized_binding,
        )
        verify_results = result_bundle(
            verify_batch,
            [
                {
                    "mode": "adversarial",
                    "verdict": "accept",
                    **analysis,
                    "rationale": "The cited return statement entails the payload.",
                }
            ],
        )
        archive = protocol.build_archive(
            execution,
            [analyze_results, verify_results],
            run_id="ar_control-plane-fixture",
            operator_attested=True,
            binding=normalized_binding,
        )
        manifest = {"execution_config": config}
        with mock.patch.object(
            experiment,
            "validate_archive_execution_input",
        ):
            resolved = experiment.validate_agent_archive_envelope(
                archive,
                manifest,
                "prep",
                execution,
            )
        self.assertEqual(resolved, protocol.executor_label(current_executor))


if __name__ == "__main__":
    unittest.main()
