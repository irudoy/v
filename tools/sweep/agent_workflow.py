#!/usr/bin/env python3
"""Build and archive provider-neutral caller-semantics agent task batches."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import secrets
import sys

import agent_protocol


ROOT = Path(__file__).resolve().parents[2]


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise agent_protocol.ProtocolError(f"failed to read JSON {path}: {exc}") from exc


def ensure_runtime_path(path: Path) -> None:
    resolved = path.resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError:
        return
    raise agent_protocol.ProtocolError(
        f"runtime file must be outside the git repository: {resolved}"
    )


def write_json(path: Path, value) -> None:
    ensure_runtime_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = agent_protocol.stable_json_bytes(value, pretty=True)
    if path.exists() and path.read_bytes() != data:
        raise agent_protocol.ProtocolError(
            f"immutable file already exists with different content: {path}"
        )
    path.write_bytes(data)


def binding_from_execution(execution: dict) -> dict:
    binding = execution.get("protocol_binding")
    if binding is None:
        raise agent_protocol.ProtocolError(
            "execution does not contain a provider-neutral protocol binding"
        )
    if not isinstance(binding, dict):
        raise agent_protocol.ProtocolError("execution protocol_binding must be an object")
    return {
        "schema": binding.get("schema"),
        "sha256": binding.get("protocol_sha256"),
    }


def cmd_build_batch(args) -> None:
    execution = read_json(Path(args.execution))
    prior = read_json(Path(args.prior_results)) if args.prior_results else None
    batch = agent_protocol.build_batch(
        execution,
        args.phase,
        prior_results=prior,
        binding=binding_from_execution(execution),
    )
    output = Path(args.output)
    write_json(output, batch)
    print(f"agent task batch: {output.resolve()}")
    print(f"tasks={len(batch['tasks'])}, sha256={agent_protocol.value_sha256(batch)}")


def cmd_validate_results(args) -> None:
    batch = read_json(Path(args.batch))
    results = read_json(Path(args.results))
    executor = agent_protocol.validate_results_bundle(results, batch)
    print(
        "agent task results: valid, "
        f"tasks={len(results['results'])}, executor={agent_protocol.executor_label(executor)}"
    )


def cmd_archive(args) -> None:
    execution = read_json(Path(args.execution))
    result_bundles = [read_json(Path(path)) for path in args.results]
    run_id = args.run_id or f"ar_{secrets.token_hex(12)}"
    archive = agent_protocol.build_archive(
        execution,
        result_bundles,
        run_id=run_id,
        operator_attested=args.fresh_launch_attested,
        binding=binding_from_execution(execution),
    )
    output = Path(args.output)
    write_json(output, archive)
    task_count = sum(len(item["batch"]["tasks"]) for item in archive["batches"])
    print(f"agent-run archive: {output.resolve()}")
    print(
        f"run_id={run_id}, tasks={task_count}, "
        f"executor={agent_protocol.executor_label(archive['executor'])}"
    )


def cmd_validate_archive(args) -> None:
    execution = read_json(Path(args.execution))
    archive = read_json(Path(args.archive))
    executor = agent_protocol.validate_archive(
        archive,
        execution,
        binding=binding_from_execution(execution),
    )
    task_count = sum(len(item["batch"]["tasks"]) for item in archive["batches"])
    print(
        "agent-run archive: valid, "
        f"tasks={task_count}, executor={agent_protocol.executor_label(executor)}"
    )


def parser() -> argparse.ArgumentParser:
    current = argparse.ArgumentParser(description=__doc__)
    sub = current.add_subparsers(dest="command", required=True)

    batch = sub.add_parser(
        "build-batch",
        help="build one provider-neutral task batch",
    )
    batch.add_argument("--execution", required=True)
    batch.add_argument("--phase", choices=("analyze", "verify", "score"), required=True)
    batch.add_argument("--prior-results")
    batch.add_argument("--output", required=True)
    batch.set_defaults(func=cmd_build_batch)

    validate = sub.add_parser(
        "validate-results",
        help="validate one executor-produced task-results bundle",
    )
    validate.add_argument("--batch", required=True)
    validate.add_argument("--results", required=True)
    validate.set_defaults(func=cmd_validate_results)

    archive = sub.add_parser(
        "archive",
        help="assemble a complete provider-neutral agent-run archive",
    )
    archive.add_argument("--execution", required=True)
    archive.add_argument("--results", action="append", required=True)
    archive.add_argument("--run-id")
    archive.add_argument("--fresh-launch-attested", action="store_true", required=True)
    archive.add_argument("--output", required=True)
    archive.set_defaults(func=cmd_archive)

    validate_archive = sub.add_parser(
        "validate-archive",
        help="rederive and validate a complete provider-neutral archive",
    )
    validate_archive.add_argument("--execution", required=True)
    validate_archive.add_argument("--archive", required=True)
    validate_archive.set_defaults(func=cmd_validate_archive)
    return current


def main() -> None:
    args = parser().parse_args()
    try:
        args.func(args)
    except agent_protocol.ProtocolError as exc:
        raise SystemExit(f"agent workflow: {exc}") from exc


if __name__ == "__main__":
    sys.exit(main())
