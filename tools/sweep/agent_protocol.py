#!/usr/bin/env python3
"""Provider-neutral task protocol for the caller-semantics experiment.

The module does not launch an agent. It converts one frozen execution document into
isolated task batches, validates executor-supplied result bundles, and assembles a
provider-neutral run archive. Agent-specific launch code remains outside the protocol.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any


PROTOCOL_SCHEMA = "vq.agent-execution-protocol/v1"
TASK_BATCH_SCHEMA = "vq.agent-task-batch/v1"
TASK_RESULTS_SCHEMA = "vq.agent-task-results/v1"
EXECUTOR_SCHEMA = "vq.agent-executor/v1"
ARCHIVE_SCHEMA = "vq.agent-run-archive/v1"

PREP_EXECUTION_SCHEMAS = frozenset(
    {
        "vq.caller-semantics-prep-execution/v4",
    }
)
RUN_EXECUTION_SCHEMAS = frozenset(
    {
        "vq.caller-semantics-run-execution/v4",
    }
)
SCORE_EXECUTION_SCHEMAS = frozenset(
    {
        "vq.caller-semantics-score-execution/v3",
    }
)

PHASES = {
    "prep": ("analyze", "verify"),
    "run": ("analyze", "verify"),
    "score": ("score",),
}

TASK_POLICY = {
    "context": "isolated_per_task",
    "tools": "none",
    "structured_output": "json_schema",
    "fresh_invocation": True,
    "fallback": False,
    "retry_count": 0,
    "cache_reuse": False,
}

EXECUTOR_KEYS = frozenset(
    {
        "schema",
        "provider",
        "backend",
        "model",
        "effort",
        "adapter",
        "adapter_version",
    }
)
RECEIPT_KEYS = frozenset(
    {
        "invocation_id",
        "fresh",
        "fallback",
        "retry_count",
        "cache_reuse",
        "domain_tool_calls",
        "input_tokens",
        "output_tokens",
        "duration_ms",
        "cost_usd",
        "raw_output",
        "raw_output_sha256",
    }
)
ARCHIVE_KEYS = frozenset(
    {
        "schema",
        "runId",
        "protocolPath",
        "protocolSha256",
        "protocolSource",
        "args",
        "result",
        "executor",
        "executorSha256",
        "batches",
        "status",
        "launch",
    }
)

SHA256 = re.compile(r"^[0-9a-f]{64}$")
RUN_ID = re.compile(r"^ar_[a-z0-9-]{6,}$")
ASCII_IDENTITY = re.compile(r"^[\x21-\x7e]{1,160}$")


class ProtocolError(ValueError):
    """Provider-neutral protocol or archive violation."""


def stable_json_bytes(value: Any, *, pretty: bool = False) -> bytes:
    if pretty:
        text = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    else:
        text = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    return text.encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def value_sha256(value: Any) -> str:
    return sha256_bytes(stable_json_bytes(value))


def protocol_source(path: Path | None = None) -> dict[str, str]:
    source_path = (path or Path(__file__)).resolve()
    try:
        content = source_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ProtocolError(f"failed to read protocol source {source_path}: {exc}") from exc
    return {
        "path": str(source_path),
        "sha256": sha256_bytes(content.encode("utf-8")),
        "content": content,
    }


def execution_kind(execution: dict) -> str:
    schema = execution.get("schema") if isinstance(execution, dict) else None
    if schema in PREP_EXECUTION_SCHEMAS:
        return "prep"
    if schema in RUN_EXECUTION_SCHEMAS:
        return "run"
    if schema in SCORE_EXECUTION_SCHEMAS:
        return "score"
    raise ProtocolError(f"unsupported execution schema: {schema!r}")


def workflow_phases(execution: dict) -> tuple[str, ...]:
    return PHASES[execution_kind(execution)]


def numbered_text(text: str) -> str:
    return "\n".join(
        f"{index}|{line}" for index, line in enumerate(text.split("\n"), start=1)
    )


CITATION_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["line_start", "line_end", "excerpt"],
    "properties": {
        "line_start": {"type": "integer", "minimum": 1},
        "line_end": {"type": "integer", "minimum": 1},
        "excerpt": {"type": "string", "minLength": 1},
    },
}

PREP_ANALYSIS_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["role", "semantics", "citations"],
    "properties": {
        "role": {"type": "string", "minLength": 1},
        "semantics": {"type": "string", "minLength": 1},
        "citations": {"type": "array", "minItems": 1, "items": CITATION_SCHEMA},
    },
}

PREP_VERDICT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "mode",
        "verdict",
        "role",
        "semantics",
        "citations",
        "rationale",
    ],
    "properties": {
        "mode": {"type": "string", "enum": ["adversarial"]},
        "verdict": {"type": "string", "enum": ["accept", "refute"]},
        "role": {"type": "string", "minLength": 1},
        "semantics": {"type": "string", "minLength": 1},
        "citations": {"type": "array", "minItems": 1, "items": CITATION_SCHEMA},
        "rationale": {"type": "string", "minLength": 1},
    },
}

RUN_ANALYSIS_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "status",
        "decision",
        "role",
        "semantics",
        "disposition",
        "target",
        "evidence",
        "machine_references",
        "citations",
    ],
    "properties": {
        "status": {"type": "string", "enum": ["completed"]},
        "decision": {"type": "string", "enum": ["accept_code", "downgrade"]},
        "role": {"type": "string", "enum": ["table", "threshold", "dead"]},
        "semantics": {"type": "string", "minLength": 1},
        "disposition": {
            "type": "string",
            "enum": [
                "writes",
                "consumer",
                "inline_comparison",
                "return",
                "dead_control_flow",
                "unresolved",
            ],
        },
        "target": {"type": "string", "minLength": 1},
        "evidence": {"type": "string", "minLength": 1},
        "machine_references": {"type": "string", "minLength": 1},
        "citations": {"type": "array", "minItems": 1, "items": CITATION_SCHEMA},
    },
}

RUN_VERDICT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["mode", "verdict", "analysis", "rationale"],
    "properties": {
        "mode": {"type": "string", "enum": ["adversarial"]},
        "verdict": {"type": "string", "enum": ["accept", "refute"]},
        "analysis": RUN_ANALYSIS_SCHEMA,
        "rationale": {"type": "string", "minLength": 1},
    },
}

SCORE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["score", "rationale"],
    "properties": {
        "score": {"type": "number", "minimum": 0, "maximum": 1},
        "rationale": {"type": "string", "minLength": 1},
    },
}


def response_schema(kind: str, phase: str) -> dict:
    schemas = {
        ("prep", "analyze"): PREP_ANALYSIS_SCHEMA,
        ("prep", "verify"): PREP_VERDICT_SCHEMA,
        ("run", "analyze"): RUN_ANALYSIS_SCHEMA,
        ("run", "verify"): RUN_VERDICT_SCHEMA,
        ("score", "score"): SCORE_SCHEMA,
    }
    try:
        return schemas[(kind, phase)]
    except KeyError as exc:
        raise ProtocolError(f"unsupported task phase: {kind}/{phase}") from exc


def _require_execution_items(execution: dict) -> list[dict]:
    items = execution.get("items")
    if not isinstance(items, list) or not items or any(
        not isinstance(item, dict) for item in items
    ):
        raise ProtocolError("execution.items must be a non-empty array of objects")
    return items


def _analysis_prompt(kind: str, execution: dict, item: dict) -> str:
    if kind == "prep":
        prompt = execution.get("prompts", {}).get("analyze")
    elif kind == "run":
        prompt = execution.get("prompts", {}).get("analyze")
    else:
        raise ProtocolError(f"{kind} has no Analyze phase")
    artifact = item.get("artifact_text")
    if not isinstance(prompt, str) or not prompt or not isinstance(artifact, str):
        raise ProtocolError(f"{kind} execution lacks Analyze prompt or artifact text")
    return (
        f"{prompt}\n\n"
        "BEGIN ASSIGNED ARTIFACT\n"
        f"{numbered_text(artifact)}\n"
        "END ASSIGNED ARTIFACT"
    )


def _verify_prompt(kind: str, execution: dict, item: dict, analysis: dict) -> str:
    prompt = execution.get("prompts", {}).get("verify")
    artifact = item.get("artifact_text")
    if not isinstance(prompt, str) or not prompt or not isinstance(artifact, str):
        raise ProtocolError(f"{kind} execution lacks Verify prompt or artifact text")
    payload_label = "Analyze payload to verify exactly"
    payload = json.dumps(analysis, ensure_ascii=False, sort_keys=True, indent=2)
    return (
        f"{prompt}\n\n"
        f"{payload_label}:\n{payload}\n\n"
        "BEGIN ASSIGNED ARTIFACT\n"
        f"{numbered_text(artifact)}\n"
        "END ASSIGNED ARTIFACT"
    )


def _score_prompt(execution: dict, item: dict) -> str:
    prompt = execution.get("prompt")
    if not isinstance(prompt, str) or not prompt:
        raise ProtocolError("score execution lacks its frozen prompt")
    payload = {
        "reference_semantics": item.get("reference_semantics"),
        "candidate_semantics": item.get("candidate_semantics"),
    }
    if any(not isinstance(value, str) or not value for value in payload.values()):
        raise ProtocolError("score execution contains an invalid semantics payload")
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return (
        f"{prompt}\n\n"
        "BEGIN SCORING PAYLOAD JSON\n"
        f"{encoded}\n"
        "END SCORING PAYLOAD JSON"
    )


def _task_id(kind: str, phase: str, index: int) -> str:
    prefix = {
        ("prep", "analyze"): "prep-analyze",
        ("prep", "verify"): "prep-verify",
        ("run", "analyze"): "map-analyze",
        ("run", "verify"): "map-verify",
        ("score", "score"): "score",
    }[(kind, phase)]
    return f"{prefix}:{index}"


def build_batch(
    execution: dict,
    phase: str,
    *,
    prior_results: dict | None = None,
    binding: dict | None = None,
) -> dict:
    """Build one isolated task batch from a frozen execution document."""
    kind = execution_kind(execution)
    if phase not in PHASES[kind]:
        raise ProtocolError(f"phase {phase!r} is not valid for {kind}")
    items = _require_execution_items(execution)
    prior_by_id: dict[str, dict] = {}
    if phase == "verify":
        analyze_batch = build_batch(execution, "analyze", binding=binding)
        validate_results_bundle(prior_results, analyze_batch)
        prior_by_id = {
            item["task_id"]: item["response"] for item in prior_results["results"]
        }
    elif prior_results is not None:
        raise ProtocolError(f"phase {phase} must not receive prior results")

    tasks = []
    for index, item in enumerate(items, start=1):
        current_task_id = _task_id(kind, phase, index)
        if phase == "analyze":
            prompt = _analysis_prompt(kind, execution, item)
        elif phase == "verify":
            analyze_id = _task_id(kind, "analyze", index)
            prompt = _verify_prompt(kind, execution, item, prior_by_id[analyze_id])
        else:
            prompt = _score_prompt(execution, item)
        tasks.append(
            {
                "task_id": current_task_id,
                "prompt": prompt,
                "response_schema": response_schema(kind, phase),
            }
        )
    protocol_binding = binding or {
        "schema": PROTOCOL_SCHEMA,
        "sha256": protocol_source()["sha256"],
    }
    if (
        not isinstance(protocol_binding, dict)
        or protocol_binding.get("schema") != PROTOCOL_SCHEMA
        or not SHA256.fullmatch(protocol_binding.get("sha256", ""))
    ):
        raise ProtocolError("invalid protocol binding")
    return {
        "schema": TASK_BATCH_SCHEMA,
        "protocol": dict(protocol_binding),
        "execution_sha256": value_sha256(execution),
        "kind": kind,
        "phase": phase,
        "policy": dict(TASK_POLICY),
        "tasks": tasks,
    }


def _schema_type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return False


def validate_json_schema(value: Any, schema: dict, context: str = "response") -> None:
    """Validate the small JSON Schema subset used by this experiment."""
    expected_type = schema.get("type")
    if not _schema_type_matches(value, expected_type):
        raise ProtocolError(f"{context}: expected {expected_type}")
    if "enum" in schema and value not in schema["enum"]:
        raise ProtocolError(f"{context}: value is outside enum")
    if expected_type == "string":
        if len(value) < schema.get("minLength", 0):
            raise ProtocolError(f"{context}: string is too short")
        return
    if expected_type in {"number", "integer"}:
        if "minimum" in schema and value < schema["minimum"]:
            raise ProtocolError(f"{context}: value is below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            raise ProtocolError(f"{context}: value is above maximum")
        return
    if expected_type == "array":
        if len(value) < schema.get("minItems", 0):
            raise ProtocolError(f"{context}: array is too short")
        item_schema = schema.get("items")
        if item_schema is not None:
            for index, item in enumerate(value):
                validate_json_schema(item, item_schema, f"{context}[{index}]")
        return
    properties = schema.get("properties", {})
    required = set(schema.get("required", ()))
    if not required <= set(value):
        raise ProtocolError(f"{context}: required fields are missing")
    if schema.get("additionalProperties") is False and set(value) != set(properties):
        raise ProtocolError(f"{context}: object field set differs from schema")
    for name, item_schema in properties.items():
        if name in value:
            validate_json_schema(value[name], item_schema, f"{context}.{name}")


def validate_executor(executor: Any) -> dict:
    if not isinstance(executor, dict) or set(executor) != EXECUTOR_KEYS:
        raise ProtocolError("executor has a non-frozen field set")
    if executor.get("schema") != EXECUTOR_SCHEMA:
        raise ProtocolError("unknown executor schema")
    for field in EXECUTOR_KEYS - {"schema"}:
        value = executor.get(field)
        if not isinstance(value, str) or not ASCII_IDENTITY.fullmatch(value):
            raise ProtocolError(f"executor.{field} is not printable ASCII")
    return executor


def executor_sha256(executor: dict) -> str:
    validate_executor(executor)
    return value_sha256(executor)


def executor_label(executor: dict) -> str:
    validate_executor(executor)
    return (
        f"{executor['provider']}/{executor['backend']}/"
        f"{executor['model']}:{executor['effort']}"
        f"@{executor['adapter']}:{executor['adapter_version']}"
    )


def _optional_nonnegative_number(value: Any, context: str) -> None:
    if value is None:
        return
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or value < 0
    ):
        raise ProtocolError(f"{context} must be null or non-negative")


def _optional_nonnegative_integer(value: Any, context: str) -> None:
    if value is None:
        return
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ProtocolError(f"{context} must be null or a non-negative integer")


def validate_receipt(receipt: Any, context: str) -> None:
    if not isinstance(receipt, dict) or set(receipt) != RECEIPT_KEYS:
        raise ProtocolError(f"{context}: receipt has a non-frozen field set")
    if not isinstance(receipt.get("invocation_id"), str) or not ASCII_IDENTITY.fullmatch(
        receipt["invocation_id"]
    ):
        raise ProtocolError(f"{context}: invalid invocation_id")
    expected_policy = {
        "fresh": True,
        "fallback": False,
        "retry_count": 0,
        "cache_reuse": False,
        "domain_tool_calls": 0,
    }
    for field, expected in expected_policy.items():
        if receipt.get(field) != expected:
            raise ProtocolError(f"{context}: receipt violates {field} policy")
    _optional_nonnegative_integer(receipt.get("input_tokens"), f"{context}.input_tokens")
    _optional_nonnegative_integer(receipt.get("output_tokens"), f"{context}.output_tokens")
    _optional_nonnegative_integer(receipt.get("duration_ms"), f"{context}.duration_ms")
    _optional_nonnegative_number(receipt.get("cost_usd"), f"{context}.cost_usd")
    if receipt.get("raw_output_sha256") != value_sha256(receipt.get("raw_output")):
        raise ProtocolError(f"{context}: raw output SHA-256 mismatch")


def validate_results_bundle(
    bundle: Any,
    batch: dict,
    *,
    expected_executor: dict | None = None,
) -> dict:
    if not isinstance(bundle, dict) or set(bundle) != {
        "schema",
        "batch_sha256",
        "executor",
        "operator_attested",
        "results",
    }:
        raise ProtocolError("task results have a non-frozen field set")
    if bundle.get("schema") != TASK_RESULTS_SCHEMA:
        raise ProtocolError("unknown task-results schema")
    if bundle.get("batch_sha256") != value_sha256(batch):
        raise ProtocolError("task results belong to another batch")
    executor = validate_executor(bundle.get("executor"))
    if expected_executor is not None and executor != expected_executor:
        raise ProtocolError("task results use another executor")
    if bundle.get("operator_attested") is not True:
        raise ProtocolError("task results lack operator attestation")
    tasks = batch.get("tasks")
    expected = {item["task_id"]: item for item in tasks}
    results = bundle.get("results")
    if not isinstance(results, list) or any(not isinstance(item, dict) for item in results):
        raise ProtocolError("task results must be an array of objects")
    by_id = {item.get("task_id"): item for item in results}
    if len(by_id) != len(results) or set(by_id) != set(expected):
        raise ProtocolError("task results do not cover the exact batch")
    invocation_ids = set()
    for task_id, task in expected.items():
        item = by_id[task_id]
        if set(item) != {"task_id", "status", "response", "receipt"}:
            raise ProtocolError(f"{task_id}: result has a non-frozen field set")
        if item.get("status") != "completed":
            raise ProtocolError(f"{task_id}: task did not complete")
        validate_json_schema(item.get("response"), task["response_schema"], task_id)
        validate_receipt(item.get("receipt"), task_id)
        invocation_id = item["receipt"]["invocation_id"]
        if invocation_id in invocation_ids:
            raise ProtocolError("one invocation_id is used by multiple tasks")
        invocation_ids.add(invocation_id)
    return executor


def _results_by_id(bundle: dict) -> dict[str, dict]:
    return {item["task_id"]: item for item in bundle["results"]}


def _assemble_prep(execution: dict, bundles: dict[str, dict]) -> dict:
    analyses = _results_by_id(bundles["analyze"])
    verdicts = _results_by_id(bundles["verify"])
    output_analyses = []
    output_verdicts = []
    for index, item in enumerate(execution["items"], start=1):
        analysis = analyses[_task_id("prep", "analyze", index)]["response"]
        verdict = verdicts[_task_id("prep", "verify", index)]["response"]
        if (
            verdict["role"] != analysis["role"]
            or verdict["semantics"] != analysis["semantics"]
            or verdict["citations"] != analysis["citations"]
        ):
            raise ProtocolError("prep Verify did not copy the exact Analyze payload")
        output_analyses.append(
            {
                "job_id": item["job_id"],
                "artifact_sha256": item["artifact_sha256"],
                **analysis,
            }
        )
        output_verdicts.append(
            {
                "job_id": item["job_id"],
                "artifact_sha256": item["artifact_sha256"],
                **verdict,
            }
        )
    return {
        "schema": execution["result_schema"],
        "execution_config_sha256": execution["execution_config_sha256"],
        "private_manifest_sha256": execution["private_manifest_sha256"],
        "worklist_sha256": execution["worklist_sha256"],
        "analyses": output_analyses,
        "verdicts": output_verdicts,
    }


def _assemble_run(execution: dict, bundles: dict[str, dict]) -> dict:
    analyses = _results_by_id(bundles["analyze"])
    verdicts = _results_by_id(bundles["verify"])
    output_analyses = []
    output_verdicts = []
    for index, item in enumerate(execution["items"], start=1):
        analysis = analyses[_task_id("run", "analyze", index)]["response"]
        verdict = verdicts[_task_id("run", "verify", index)]["response"]
        if verdict["analysis"] != analysis:
            raise ProtocolError("run Verify did not copy the exact Analyze payload")
        full_analysis = {
            "job_id": item["job_id"],
            "condition_id": item["condition_id"],
            "pair_id": item["pair_id"],
            "target_address": item["target_address"],
            "artifact_sha256": item["artifact_sha256"],
            **analysis,
        }
        output_analyses.append(full_analysis)
        output_verdicts.append(
            {
                "job_id": item["job_id"],
                "condition_id": item["condition_id"],
                "artifact_sha256": item["artifact_sha256"],
                "mode": verdict["mode"],
                "verdict": verdict["verdict"],
                "analysis": {
                    "job_id": item["job_id"],
                    "condition_id": item["condition_id"],
                    "pair_id": item["pair_id"],
                    "target_address": item["target_address"],
                    "artifact_sha256": item["artifact_sha256"],
                    **verdict["analysis"],
                },
                "rationale": verdict["rationale"],
            }
        )
    return {
        "schema": execution["result_schema"],
        "execution_config_sha256": execution["execution_config_sha256"],
        "condition_id": execution["condition_id"],
        "worklist_sha256": execution["worklist_sha256"],
        "analyses": output_analyses,
        "verdicts": output_verdicts,
    }


def _assemble_score(execution: dict, bundles: dict[str, dict]) -> dict:
    scores = _results_by_id(bundles["score"])
    output_scores = []
    for index, item in enumerate(execution["items"], start=1):
        score = scores[_task_id("score", "score", index)]["response"]
        output_scores.append(
            {
                "score_id": item["score_id"],
                "candidate_sha256": item["candidate_sha256"],
                **score,
            }
        )
    return {
        "schema": execution["result_schema"],
        "execution_config_sha256": execution["execution_config_sha256"],
        "run_report_sha256": execution["run_report_sha256"],
        "worklist_sha256": execution["worklist_sha256"],
        "scores": output_scores,
    }


def build_archive(
    execution: dict,
    result_bundles: list[dict],
    *,
    run_id: str,
    operator_attested: bool,
    binding: dict | None = None,
    source_path: Path | None = None,
) -> dict:
    """Validate all phases and assemble an immutable provider-neutral archive."""
    if not isinstance(run_id, str) or not RUN_ID.fullmatch(run_id):
        raise ProtocolError("invalid fresh agent-run id")
    if operator_attested is not True:
        raise ProtocolError("agent-run archive lacks operator attestation")
    kind = execution_kind(execution)
    expected_phases = PHASES[kind]
    bundles_by_phase: dict[str, dict] = {}
    executor = None
    batch_records = []
    for phase in expected_phases:
        prior = bundles_by_phase.get("analyze") if phase == "verify" else None
        batch = build_batch(
            execution,
            phase,
            prior_results=prior,
            binding=binding,
        )
        matches = [
            bundle
            for bundle in result_bundles
            if isinstance(bundle, dict)
            and bundle.get("batch_sha256") == value_sha256(batch)
        ]
        if len(matches) != 1:
            raise ProtocolError(f"archive requires exactly one result bundle for {phase}")
        bundle = matches[0]
        current_executor = validate_results_bundle(
            bundle,
            batch,
            expected_executor=executor,
        )
        executor = current_executor
        bundles_by_phase[phase] = bundle
        batch_records.append({"batch": batch, "results": bundle})
    if len(result_bundles) != len(expected_phases):
        raise ProtocolError("archive contains an extra result bundle")
    if kind == "prep":
        result = _assemble_prep(execution, bundles_by_phase)
    elif kind == "run":
        result = _assemble_run(execution, bundles_by_phase)
    else:
        result = _assemble_score(execution, bundles_by_phase)
    source = protocol_source(source_path)
    archive = {
        "schema": ARCHIVE_SCHEMA,
        "runId": run_id,
        "protocolPath": source["path"],
        "protocolSha256": source["sha256"],
        "protocolSource": source["content"],
        "args": execution,
        "result": result,
        "executor": executor,
        "executorSha256": executor_sha256(executor),
        "batches": batch_records,
        "status": "completed",
        "launch": {
            "mode": "fresh",
            "resumeFromRunId": None,
            "cacheReuse": False,
            "fallback": False,
            "retryCount": 0,
            "operatorAttested": True,
        },
    }
    validate_archive(archive, execution, binding=binding)
    return archive


def validate_archive(
    archive: Any,
    execution: dict,
    *,
    expected_executor: dict | None = None,
    binding: dict | None = None,
) -> dict:
    if not isinstance(archive, dict) or set(archive) != ARCHIVE_KEYS:
        raise ProtocolError("agent-run archive has a non-frozen field set")
    if archive.get("schema") != ARCHIVE_SCHEMA:
        raise ProtocolError("unknown agent-run archive schema")
    if archive.get("args") != execution:
        raise ProtocolError("agent-run archive contains another execution document")
    if archive.get("status") != "completed":
        raise ProtocolError("agent-run archive is not completed")
    if not isinstance(archive.get("runId"), str) or not RUN_ID.fullmatch(archive["runId"]):
        raise ProtocolError("agent-run archive has an invalid run id")
    if archive.get("launch") != {
        "mode": "fresh",
        "resumeFromRunId": None,
        "cacheReuse": False,
        "fallback": False,
        "retryCount": 0,
        "operatorAttested": True,
    }:
        raise ProtocolError("agent-run archive violates the launch policy")
    source = archive.get("protocolSource")
    if (
        not isinstance(source, str)
        or archive.get("protocolSha256") != sha256_bytes(source.encode("utf-8"))
        or not isinstance(archive.get("protocolPath"), str)
        or not archive["protocolPath"]
    ):
        raise ProtocolError("agent-run archive has invalid embedded protocol source")
    if binding is not None and (
        archive.get("protocolSha256") != binding.get("sha256")
        or binding.get("schema") != PROTOCOL_SCHEMA
    ):
        raise ProtocolError("agent-run archive uses another protocol binding")
    executor = validate_executor(archive.get("executor"))
    if archive.get("executorSha256") != executor_sha256(executor):
        raise ProtocolError("agent-run archive has an invalid executor SHA-256")
    if expected_executor is not None and executor != expected_executor:
        raise ProtocolError("agent-run archive uses another executor")
    records = archive.get("batches")
    if not isinstance(records, list) or any(not isinstance(item, dict) for item in records):
        raise ProtocolError("agent-run archive batches must be an array")
    for record in records:
        if set(record) != {"batch", "results"}:
            raise ProtocolError("agent-run archive has an invalid batch record")
    kind = execution_kind(execution)
    expected_phases = PHASES[kind]
    if len(records) != len(expected_phases):
        raise ProtocolError("agent-run archive has an invalid phase count")
    bundles_by_phase = {}
    for phase, record in zip(expected_phases, records):
        prior = bundles_by_phase.get("analyze") if phase == "verify" else None
        expected_batch = build_batch(
            execution,
            phase,
            prior_results=prior,
            binding=binding,
        )
        if record["batch"] != expected_batch:
            raise ProtocolError(f"agent-run archive {phase} batch drift")
        validate_results_bundle(
            record["results"],
            expected_batch,
            expected_executor=executor,
        )
        bundles_by_phase[phase] = record["results"]
    if kind == "prep":
        expected_result = _assemble_prep(execution, bundles_by_phase)
    elif kind == "run":
        expected_result = _assemble_run(execution, bundles_by_phase)
    else:
        expected_result = _assemble_score(execution, bundles_by_phase)
    if archive.get("result") != expected_result:
        raise ProtocolError("agent-run archive result cannot be derived from task results")
    return executor
