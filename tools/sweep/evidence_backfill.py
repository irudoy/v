#!/usr/bin/env python3
"""Воспроизводимый control plane для evidence backfill Map/Axis JK08A.

Helper фиксирует scope из immutable git-объектов, сверяет два независимых набора
blind-артефактов, проверяет полный результат Workflow и применяет проверенные
решения к canonical CSV с защитой от drift.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import copy
import csv
from difflib import unified_diff
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
MEMGRAPH = ROOT / "tools" / "memgraph"
if str(MEMGRAPH) not in sys.path:
    sys.path.insert(0, str(MEMGRAPH))

from provenance import PROCESS, ProvenanceError, parse_evidence  # noqa: E402

MANIFEST_SCHEMA = "vq.evidence-backfill-manifest/v1"
ARTIFACT_SCHEMA = "vq.evidence-backfill-artifacts/v1"
RESULT_SCHEMA = "vq.evidence-backfill-results/v1"
RUN_SET_SCHEMA = "vq.evidence-backfill-run-set/v1"
DECISION_SCHEMA = "vq.evidence-backfill-decisions/v1"

EXPECTED = {
    ("Map", "confidence"): 52,
    ("Map", "scale_conf"): 20,
    ("Axis", "scale_conf"): 6,
}
EXPECTED_CLAIMS = sum(EXPECTED.values())
EXPECTED_NODES = 58
SOURCE_PATHS = {
    "Map": "defs/{rom}.findings.csv",
    "Axis": "defs/{rom}.axes.csv",
}
EVIDENCE_FIELDS = {
    ("Map", "confidence"): "evidence",
    ("Map", "scale_conf"): "scale_evidence",
    ("Axis", "scale_conf"): "scale_evidence",
}
CLAIM_FIELDS = {
    ("Map", "confidence"): ("confidence", "role", "semantics", "units"),
    ("Map", "scale_conf"): ("scale_conf", "units", "scale_expr", "to_byte"),
    ("Axis", "scale_conf"): ("scale_conf", "units", "scale_expr", "to_byte"),
}
REVISION_FIELDS = {
    ("Map", "confidence"): frozenset({"role", "semantics"}),
    ("Map", "scale_conf"): frozenset({"units", "scale_expr", "to_byte"}),
    ("Axis", "scale_conf"): frozenset({"units", "scale_expr", "to_byte"}),
}
DISPOSITIONS = frozenset(
    {"writes", "consumer", "inline_comparison", "return", "dead_control_flow", "unresolved"}
)
MAP_ROLES = frozenset({"table", "threshold", "dead"})
FORBIDDEN_ARTIFACT_TEXT = ("Нет файла", "ЧТЕНИЕ НЕ УДАЛОСЬ")


class BackfillError(ValueError):
    """Нарушение frozen scope, схемы результата либо условий применения."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def stable_json_bytes(value, pretty=True) -> bytes:
    if pretty:
        text = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    else:
        text = json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
    return text.encode("utf-8")


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(stable_json_bytes(value))


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BackfillError(f"не удалось прочитать JSON {path}: {exc}") from exc


def parse_csv(data: bytes, path: str):
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BackfillError(f"{path}: CSV не является UTF-8") from exc
    reader = csv.DictReader(io.StringIO(text, newline=""))
    fields = list(reader.fieldnames or ())
    if not fields:
        raise BackfillError(f"{path}: нет заголовка CSV")
    rows = [dict(row) for row in reader]
    return fields, rows


def render_csv(fields, rows) -> bytes:
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode("utf-8")


def row_digest(fields, row) -> str:
    payload = [[field, row.get(field, "")] for field in fields]
    return sha256_bytes(stable_json_bytes(payload, pretty=False))


def run_git(repo: Path, *args, binary=False):
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=repo,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = ""
        if isinstance(exc, subprocess.CalledProcessError):
            detail = exc.stderr.decode("utf-8", "replace").strip()
        raise BackfillError(f"git {' '.join(args)}: {detail or exc}") from exc
    return proc.stdout if binary else proc.stdout.decode("utf-8").strip()


def git_source(repo: Path, commit: str, path: str) -> bytes:
    return run_git(repo, "show", f"{commit}:{path}", binary=True)


def claim_identity(rom: str, label: str, addr: str, prop: str) -> str:
    return f"{rom}:{label}:{addr}:{prop}"


def node_identity(rom: str, label: str, addr: str) -> str:
    return f"{rom}:{label}:{addr}"


def artifact_name(label: str, addr: str) -> str:
    return f"{label.lower()}-{addr}.md"


def _source_entry(label, path, oid, fields, data):
    return {
        "label": label,
        "path": path,
        "git_oid": oid,
        "sha256": sha256_bytes(data),
        "fields": list(fields),
    }


def build_manifest(rom: str, base_commit: str, sources) -> dict:
    """Построить manifest из уже прочитанных immutable CSV.

    sources: label -> {path, git_oid, data}.
    """
    claims = []
    source_entries = []
    for label in ("Map", "Axis"):
        source = sources[label]
        fields, rows = parse_csv(source["data"], source["path"])
        required = {"addr", "scale_conf", "scale_evidence"}
        if label == "Map":
            required |= {"confidence", "evidence", "role", "semantics"}
        missing = required - set(fields)
        if missing:
            raise BackfillError(
                f"{source['path']}: нет колонок {', '.join(sorted(missing))}"
            )
        source_entries.append(
            _source_entry(
                label, source["path"], source["git_oid"], fields, source["data"]
            )
        )
        seen = set()
        for row in rows:
            addr = (row.get("addr") or "").strip().lower()
            if len(addr) != 8 or any(ch not in "0123456789abcdef" for ch in addr):
                raise BackfillError(f"{source['path']}: неверный addr {addr!r}")
            if addr in seen:
                raise BackfillError(f"{source['path']}: повтор addr {addr}")
            seen.add(addr)
            properties = ("confidence", "scale_conf") if label == "Map" else ("scale_conf",)
            for prop in properties:
                evidence_field = EVIDENCE_FIELDS[(label, prop)]
                if row.get(prop, "").strip() != "code" or row.get(
                    evidence_field, ""
                ).strip():
                    continue
                values = {
                    field: row.get(field, "") for field in CLAIM_FIELDS[(label, prop)]
                }
                claims.append(
                    {
                        "identity": claim_identity(rom, label, addr, prop),
                        "node": node_identity(rom, label, addr),
                        "rom": rom,
                        "label": label,
                        "addr": addr,
                        "property": prop,
                        "evidence_field": evidence_field,
                        "source": source["path"],
                        "row_digest": row_digest(fields, row),
                        "claim_value": values,
                        "artifact": artifact_name(label, addr),
                    }
                )
    order = {"Map": 0, "Axis": 1}
    prop_order = {"confidence": 0, "scale_conf": 1}
    claims.sort(
        key=lambda item: (
            order[item["label"]],
            item["addr"],
            prop_order[item["property"]],
        )
    )
    nodes = []
    grouped = defaultdict(list)
    for claim in claims:
        grouped[claim["node"]].append(claim)
    for node in sorted(
        grouped,
        key=lambda value: (
            order[grouped[value][0]["label"]], grouped[value][0]["addr"]
        ),
    ):
        first = grouped[node][0]
        nodes.append(
            {
                "identity": node,
                "rom": rom,
                "label": first["label"],
                "addr": first["addr"],
                "artifact": first["artifact"],
                "properties": [claim["property"] for claim in grouped[node]],
            }
        )
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "rom": rom,
        "base_commit": base_commit,
        "sources": source_entries,
        "expected": {
            "claims": EXPECTED_CLAIMS,
            "nodes": EXPECTED_NODES,
            "breakdown": {
                f"{label}.{prop}": count
                for (label, prop), count in EXPECTED.items()
            },
        },
        "claims": claims,
        "nodes": nodes,
    }
    validate_manifest(manifest)
    return manifest


def freeze_manifest(repo: Path, rom: str, commit: str) -> dict:
    base_commit = run_git(repo, "rev-parse", f"{commit}^{{commit}}")
    sources = {}
    for label, template in SOURCE_PATHS.items():
        path = template.format(rom=rom)
        sources[label] = {
            "path": path,
            "git_oid": run_git(repo, "rev-parse", f"{base_commit}:{path}"),
            "data": git_source(repo, base_commit, path),
        }
    return build_manifest(rom, base_commit, sources)


def validate_manifest(manifest: dict) -> None:
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise BackfillError(f"неизвестная схема manifest: {manifest.get('schema')!r}")
    claims = manifest.get("claims")
    nodes = manifest.get("nodes")
    if not isinstance(claims, list) or not isinstance(nodes, list):
        raise BackfillError("manifest: claims/nodes обязаны быть массивами")
    identities = [item.get("identity") for item in claims]
    if len(identities) != len(set(identities)):
        raise BackfillError("manifest: повтор identity заявки")
    node_ids = [item.get("identity") for item in nodes]
    if len(node_ids) != len(set(node_ids)):
        raise BackfillError("manifest: повтор identity узла")
    counts = Counter((item.get("label"), item.get("property")) for item in claims)
    if counts != Counter(EXPECTED):
        raise BackfillError(
            f"frozen scope != 52/20/6: {dict(sorted(counts.items()))}"
        )
    if len(claims) != EXPECTED_CLAIMS or len(nodes) != EXPECTED_NODES:
        raise BackfillError(
            f"frozen scope: claims={len(claims)}, nodes={len(nodes)}; "
            f"ожидалось {EXPECTED_CLAIMS}/{EXPECTED_NODES}"
        )
    expected_nodes = {item["node"] for item in claims}
    if set(node_ids) != expected_nodes:
        raise BackfillError("manifest: nodes не совпадают с узлами claims")
    claims_by_node = defaultdict(list)
    for claim in claims:
        identity = claim_identity(
            claim.get("rom", ""),
            claim.get("label", ""),
            claim.get("addr", ""),
            claim.get("property", ""),
        )
        if claim.get("identity") != identity:
            raise BackfillError(f"manifest: несогласованный identity {claim.get('identity')}")
        if claim.get("node") != node_identity(
            claim["rom"], claim["label"], claim["addr"]
        ):
            raise BackfillError(f"manifest: несогласованный node {claim['identity']}")
        if claim.get("artifact") != artifact_name(claim["label"], claim["addr"]):
            raise BackfillError(f"manifest: неверный artifact {claim['identity']}")
        if (claim["label"], claim["property"]) not in EXPECTED:
            raise BackfillError(f"manifest: недопустимая заявка {claim['identity']}")
        claims_by_node[claim["node"]].append(claim["property"])
    for node in nodes:
        if node.get("properties") != claims_by_node[node["identity"]]:
            raise BackfillError(f"manifest: properties расходятся у {node['identity']}")


def manifest_sha256(path: Path, manifest=None) -> str:
    if manifest is None:
        return file_sha256(path)
    return sha256_bytes(stable_json_bytes(manifest))


def _artifact_inventory(directory: Path, expected_names) -> dict:
    if not directory.is_dir():
        raise BackfillError(f"нет каталога артефактов {directory}")
    actual = {path.name for path in directory.glob("*.md") if path.is_file()}
    expected = set(expected_names)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing or extra:
        raise BackfillError(
            f"{directory}: missing={missing or '[]'}, extra={extra or '[]'}"
        )
    inventory = {}
    for name in sorted(expected):
        path = directory / name
        data = path.read_bytes()
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise BackfillError(f"{path}: артефакт не является UTF-8") from exc
        found = [marker for marker in FORBIDDEN_ARTIFACT_TEXT if marker in text]
        if found:
            raise BackfillError(f"{path}: запрещённые маркеры {found}")
        inventory[name] = sha256_bytes(data)
    return inventory


def verify_artifacts(manifest_path: Path, left: Path, right: Path) -> dict:
    manifest = read_json(manifest_path)
    validate_manifest(manifest)
    expected = [node["artifact"] for node in manifest["nodes"]]
    left_inventory = _artifact_inventory(left, expected)
    right_inventory = _artifact_inventory(right, expected)
    if left_inventory != right_inventory:
        changed = sorted(
            name
            for name in set(left_inventory) | set(right_inventory)
            if left_inventory.get(name) != right_inventory.get(name)
        )
        raise BackfillError(f"наборы артефактов недетерминированы: {changed}")
    files = [
        {"name": name, "sha256": left_inventory[name]} for name in sorted(left_inventory)
    ]
    set_sha = sha256_bytes(stable_json_bytes(files, pretty=False))
    return {
        "schema": ARTIFACT_SCHEMA,
        "manifest_sha256": file_sha256(manifest_path),
        "artifact_set_sha256": set_sha,
        "artifact_dir": str(left.resolve()),
        "count": len(files),
        "files": files,
    }


def validate_artifact_report(report: dict, manifest_path: Path, manifest: dict) -> dict:
    if report.get("schema") != ARTIFACT_SCHEMA:
        raise BackfillError("неизвестная схема отчёта артефактов")
    if report.get("manifest_sha256") != file_sha256(manifest_path):
        raise BackfillError("отчёт артефактов относится к другому manifest")
    files = report.get("files")
    if not isinstance(files, list):
        raise BackfillError("отчёт артефактов: files обязан быть массивом")
    inventory = {item.get("name"): item.get("sha256") for item in files}
    if len(inventory) != len(files):
        raise BackfillError("отчёт артефактов: повтор имени файла")
    expected = {node["artifact"] for node in manifest["nodes"]}
    if set(inventory) != expected:
        raise BackfillError("отчёт артефактов не покрывает frozen nodes")
    canonical = [
        {"name": name, "sha256": inventory[name]} for name in sorted(inventory)
    ]
    if report.get("artifact_set_sha256") != sha256_bytes(
        stable_json_bytes(canonical, pretty=False)
    ):
        raise BackfillError("неверный artifact_set_sha256")
    artifact_dir = report.get("artifact_dir")
    if not isinstance(artifact_dir, str) or not Path(artifact_dir).is_absolute():
        raise BackfillError("отчёт артефактов не содержит абсолютный artifact_dir")
    return inventory


def workflow_worklist(manifest: dict, artifact_report: dict, inventory: dict) -> list[dict]:
    root = Path(artifact_report["artifact_dir"])
    return [
        {
            "identity": node["identity"],
            "rom": node["rom"],
            "label": node["label"],
            "addr": node["addr"],
            "properties": node["properties"],
            "artifact": str((root / node["artifact"]).resolve()),
            "artifact_sha256": inventory[node["artifact"]],
        }
        for node in manifest["nodes"]
    ]


def normalize_workflow_run(
    archive: dict,
    manifest_path: Path,
    manifest: dict,
    artifact_report: dict,
    inventory: dict,
) -> tuple[dict, dict]:
    """Проверить Claude Code archive и вернуть его result payload."""
    if archive.get("status") != "completed":
        raise BackfillError(f"Workflow status={archive.get('status')!r}, нужен completed")
    for field in ("runId", "scriptPath"):
        if not isinstance(archive.get(field), str) or not archive[field].strip():
            raise BackfillError(f"Workflow archive не содержит {field}")
    args = archive.get("args")
    if not isinstance(args, dict):
        raise BackfillError("Workflow archive не содержит args")
    expected_anchors = {
        "manifest_sha256": file_sha256(manifest_path),
        "artifact_set_sha256": artifact_report["artifact_set_sha256"],
    }
    for field, expected in expected_anchors.items():
        if args.get(field) != expected:
            raise BackfillError(f"Workflow args: неверный {field}")
    expected_items = workflow_worklist(manifest, artifact_report, inventory)
    if args.get("items") != expected_items:
        raise BackfillError("Workflow args.items не совпадает с frozen worklist")
    result = archive.get("result")
    if not isinstance(result, dict):
        raise BackfillError("Workflow archive не содержит object result")
    return archive, result


def factual_evidence(text: str, prop: str, context: str):
    try:
        tokens = parse_evidence(text, prop, context)
    except ProvenanceError as exc:
        raise BackfillError(str(exc)) from exc
    factual = [token for token in tokens if token.role not in PROCESS]
    if not factual:
        raise BackfillError(f"{context}: нет factual evidence")
    return tokens


def normalized_verified_evidence(text, rewrites, prop, context):
    """Применить только проверяемые синтаксические правки evidence.

    Неразрешимую ссылку на ROM-адрес можно представить терминалом site с тем же
    адресом. Ссылку на RAM без ranked claim можно удалить. Любое иное изменение
    verified evidence запрещено.
    """
    raw_tokens = [raw.strip() for raw in text.split(";") if raw.strip()]
    tokens = factual_evidence(text, prop, context)
    if rewrites is None:
        return text
    if not isinstance(rewrites, dict) or not rewrites:
        raise BackfillError(f"{context}: evidence_rewrites обязан быть объектом")
    unknown = set(rewrites) - set(raw_tokens)
    if unknown:
        raise BackfillError(
            f"{context}: evidence_rewrites ссылается на отсутствующие токены "
            f"{sorted(unknown)}"
        )

    result = []
    for raw, token in zip(raw_tokens, tokens):
        replacement = rewrites.get(raw, raw)
        if raw in rewrites:
            if not token.is_dependency:
                raise BackfillError(
                    f"{context}: переписывать можно только адресную зависимость {raw!r}"
                )
            if replacement is None:
                if not token.target_addr.startswith("ffff"):
                    raise BackfillError(
                        f"{context}: удалить можно только RAM-зависимость {raw!r}"
                    )
                continue
            expected = f"site:{token.target_addr}"
            if replacement != expected or int(token.target_addr, 16) >= 0x01000000:
                raise BackfillError(
                    f"{context}: {raw!r} можно переписать только в ROM-site {expected!r}"
                )
        if replacement not in result:
            result.append(replacement)
    normalized = ";".join(result)
    factual_evidence(normalized, prop, context)
    return normalized


def _validate_result_item(item, claim, artifact_hash):
    identity = claim["identity"]
    if item.get("artifact_sha256") != artifact_hash:
        raise BackfillError(f"{identity}: результат относится к другому артефакту")
    decision = item.get("decision")
    if decision not in ("accept_code", "downgrade"):
        raise BackfillError(f"{identity}: неизвестное решение {decision!r}")
    if not isinstance(item.get("verifier_rationale"), str) or not item[
        "verifier_rationale"
    ].strip():
        raise BackfillError(f"{identity}: нет verifier_rationale")
    if decision == "downgrade":
        if not isinstance(item.get("blocker"), str) or not item["blocker"].strip():
            raise BackfillError(f"{identity}: downgrade без blocker")
        return
    evidence = item.get("evidence", "")
    factual_evidence(evidence, claim["property"], identity)
    values = item.get("values")
    required = set(CLAIM_FIELDS[(claim["label"], claim["property"])]) - {
        claim["property"]
    }
    if not isinstance(values, dict) or not required <= set(values):
        raise BackfillError(f"{identity}: proposal не содержит {sorted(required)}")
    if claim["property"] == "scale_conf":
        for field in ("units", "scale_expr", "to_byte"):
            if not isinstance(values.get(field), str) or not values[field].strip():
                raise BackfillError(f"{identity}: code scale без {field}")
    if claim["label"] == "Map" and claim["property"] == "confidence":
        disposition = item.get("output_disposition")
        target = item.get("target")
        if values.get("role") not in MAP_ROLES:
            raise BackfillError(f"{identity}: неверная role {values.get('role')!r}")
        if disposition not in DISPOSITIONS - {"unresolved"}:
            raise BackfillError(f"{identity}: неверная судьба выхода {disposition!r}")
        if not isinstance(target, str) or not target.strip():
            raise BackfillError(f"{identity}: не указан точный target")
        if values.get("role") == "dead" and disposition != "dead_control_flow":
            raise BackfillError(f"{identity}: role=dead без dead_control_flow")
    if not isinstance(item.get("trace"), str) or not item["trace"].strip():
        raise BackfillError(f"{identity}: нет полного trace")


def validate_results(
    manifest_path: Path, artifact_path: Path, results_path: Path
) -> tuple[dict, dict, dict]:
    manifest = read_json(manifest_path)
    validate_manifest(manifest)
    artifact_report = read_json(artifact_path)
    inventory = validate_artifact_report(artifact_report, manifest_path, manifest)
    archive = read_json(results_path)
    _archive, results = normalize_workflow_run(
        archive, manifest_path, manifest, artifact_report, inventory
    )
    if results.get("schema") != RESULT_SCHEMA:
        raise BackfillError(f"неизвестная схема результатов: {results.get('schema')!r}")
    if results.get("manifest_sha256") != file_sha256(manifest_path):
        raise BackfillError("Workflow использовал другой manifest")
    if results.get("artifact_set_sha256") != artifact_report.get(
        "artifact_set_sha256"
    ):
        raise BackfillError("Workflow использовал другой набор артефактов")

    analyses = results.get("analyses")
    verdicts = results.get("verdicts")
    if not isinstance(analyses, list) or not isinstance(verdicts, list):
        raise BackfillError("results: analyses/verdicts обязаны быть массивами")
    analyses_by_node = {item.get("node"): item for item in analyses}
    if len(analyses_by_node) != len(analyses):
        raise BackfillError("results: повтор node analysis")
    expected_nodes = {node["identity"]: node for node in manifest["nodes"]}
    if set(analyses_by_node) != set(expected_nodes):
        missing = sorted(set(expected_nodes) - set(analyses_by_node))
        extra = sorted(set(analyses_by_node) - set(expected_nodes))
        raise BackfillError(f"results analyses: missing={missing}, extra={extra}")
    for node_id, node in expected_nodes.items():
        item = analyses_by_node[node_id]
        if item.get("artifact_sha256") != inventory[node["artifact"]]:
            raise BackfillError(f"{node_id}: analysis относится к другому артефакту")
        if item.get("properties") != node["properties"]:
            raise BackfillError(f"{node_id}: analysis properties расходятся с manifest")
        if not isinstance(item.get("summary"), str) or not item["summary"].strip():
            raise BackfillError(f"{node_id}: пустой summary")

    verdict_by_id = {item.get("identity"): item for item in verdicts}
    if len(verdict_by_id) != len(verdicts):
        raise BackfillError("results: повтор verdict identity")
    expected_claims = {claim["identity"]: claim for claim in manifest["claims"]}
    if set(verdict_by_id) != set(expected_claims):
        missing = sorted(set(expected_claims) - set(verdict_by_id))
        extra = sorted(set(verdict_by_id) - set(expected_claims))
        raise BackfillError(f"results verdicts: missing={missing}, extra={extra}")
    for identity, claim in expected_claims.items():
        _validate_result_item(
            verdict_by_id[identity], claim, inventory[claim["artifact"]]
        )
    return manifest, artifact_report, results


def compose_workflow_runs(
    manifest_path: Path,
    artifact_path: Path,
    primary_path: Path,
    recovery_paths: list[Path],
) -> dict:
    """Собрать primary archive и точечные recovery archives без свободного merge."""
    manifest, artifact_report, primary_result = validate_results(
        manifest_path, artifact_path, primary_path
    )
    primary = read_json(primary_path)
    inventory = validate_artifact_report(artifact_report, manifest_path, manifest)
    expected_items = {
        item["identity"]: item
        for item in workflow_worklist(manifest, artifact_report, inventory)
    }
    claims_by_node = defaultdict(list)
    claims = {claim["identity"]: claim for claim in manifest["claims"]}
    for claim in manifest["claims"]:
        claims_by_node[claim["node"]].append(claim["identity"])

    combined = copy.deepcopy(primary_result)
    analyses = {item["node"]: item for item in combined["analyses"]}
    verdicts = {item["identity"]: item for item in combined["verdicts"]}
    recovered = set()
    runs = [{
        "role": "primary",
        "runId": primary["runId"],
        "scriptPath": primary["scriptPath"],
        "archive": str(primary_path.resolve()),
        "sha256": file_sha256(primary_path),
        "identities": [],
    }]

    for recovery_path in recovery_paths:
        recovery = read_json(recovery_path)
        if recovery.get("status") != "completed":
            raise BackfillError(
                f"recovery {recovery_path}: status={recovery.get('status')!r}"
            )
        for field in ("runId", "scriptPath"):
            if not isinstance(recovery.get(field), str) or not recovery[field].strip():
                raise BackfillError(f"recovery {recovery_path}: нет {field}")
        args = recovery.get("args")
        if not isinstance(args, dict):
            raise BackfillError(f"recovery {recovery_path}: нет args")
        if args.get("manifest_sha256") != file_sha256(manifest_path):
            raise BackfillError(f"recovery {recovery_path}: неверный manifest_sha256")
        if args.get("artifact_set_sha256") != artifact_report["artifact_set_sha256"]:
            raise BackfillError(f"recovery {recovery_path}: неверный artifact_set_sha256")
        items = args.get("items")
        if not isinstance(items, list) or not items:
            raise BackfillError(f"recovery {recovery_path}: пустой items")
        node_ids = [item.get("identity") for item in items]
        if len(node_ids) != len(set(node_ids)):
            raise BackfillError(f"recovery {recovery_path}: повтор node identity")
        for item in items:
            if expected_items.get(item.get("identity")) != item:
                raise BackfillError(
                    f"recovery {recovery_path}: item вне frozen worklist"
                )
        expected_identities = [
            identity for node in node_ids for identity in claims_by_node[node]
        ]
        recovery_identities = args.get("recovery_identities")
        if recovery_identities != expected_identities:
            raise BackfillError(
                f"recovery {recovery_path}: recovery_identities не покрывает полные узлы"
            )
        overlap = recovered & set(recovery_identities)
        if overlap:
            raise BackfillError(f"recovery identity повторён: {sorted(overlap)}")
        recovered.update(recovery_identities)

        result = recovery.get("result")
        if not isinstance(result, dict) or result.get("schema") != RESULT_SCHEMA:
            raise BackfillError(f"recovery {recovery_path}: неверный result schema")
        if result.get("manifest_sha256") != file_sha256(manifest_path):
            raise BackfillError(f"recovery {recovery_path}: result другого manifest")
        if result.get("artifact_set_sha256") != artifact_report["artifact_set_sha256"]:
            raise BackfillError(f"recovery {recovery_path}: result другого artifact set")
        recovery_analyses = result.get("analyses")
        recovery_verdicts = result.get("verdicts")
        if not isinstance(recovery_analyses, list) or not isinstance(
            recovery_verdicts, list
        ):
            raise BackfillError(f"recovery {recovery_path}: нет analyses/verdicts")
        if {item.get("node") for item in recovery_analyses} != set(node_ids):
            raise BackfillError(f"recovery {recovery_path}: analyses не совпадают с items")
        if {item.get("identity") for item in recovery_verdicts} != set(
            recovery_identities
        ):
            raise BackfillError(
                f"recovery {recovery_path}: verdicts не совпадают с identities"
            )
        recovery_analyses_by_node = {
            item["node"]: item for item in recovery_analyses
        }
        for node in node_ids:
            expected = next(item for item in manifest["nodes"] if item["identity"] == node)
            analysis = recovery_analyses_by_node[node]
            if analysis.get("artifact_sha256") != inventory[expected["artifact"]]:
                raise BackfillError(f"recovery {node}: другой artifact")
            if analysis.get("properties") != expected["properties"]:
                raise BackfillError(f"recovery {node}: properties расходятся")
            if not isinstance(analysis.get("summary"), str) or not analysis[
                "summary"
            ].strip():
                raise BackfillError(f"recovery {node}: пустой summary")
            analyses[node] = analysis
        for verdict in recovery_verdicts:
            claim = claims[verdict["identity"]]
            _validate_result_item(
                verdict, claim, inventory[claim["artifact"]]
            )
            verdicts[verdict["identity"]] = verdict
        runs.append({
            "role": "recovery",
            "runId": recovery["runId"],
            "scriptPath": recovery["scriptPath"],
            "archive": str(recovery_path.resolve()),
            "sha256": file_sha256(recovery_path),
            "identities": recovery_identities,
        })

    combined["analyses"] = [analyses[node["identity"]] for node in manifest["nodes"]]
    combined["verdicts"] = [verdicts[claim["identity"]] for claim in manifest["claims"]]
    return {
        "schema": RUN_SET_SCHEMA,
        "runId": primary["runId"],
        "timestamp": primary.get("timestamp", ""),
        "taskId": primary.get("taskId", ""),
        "script": primary.get("script", ""),
        "scriptPath": primary["scriptPath"],
        "args": primary["args"],
        "result": combined,
        "status": "completed",
        "runs": runs,
        "recovered_identities": sorted(recovered),
    }


def validate_decisions(manifest, results, decisions, manifest_path, artifact_report, results_path):
    if decisions.get("schema") != DECISION_SCHEMA:
        raise BackfillError("неизвестная схема decisions")
    anchors = {
        "manifest_sha256": file_sha256(manifest_path),
        "artifact_set_sha256": artifact_report["artifact_set_sha256"],
        "results_sha256": file_sha256(results_path),
    }
    for key, expected in anchors.items():
        if decisions.get(key) != expected:
            raise BackfillError(f"decisions: неверный {key}")
    items = decisions.get("decisions")
    if not isinstance(items, list):
        raise BackfillError("decisions: поле decisions обязано быть массивом")
    by_id = {item.get("identity"): item for item in items}
    if len(by_id) != len(items):
        raise BackfillError("decisions: повтор identity")
    claims = {claim["identity"]: claim for claim in manifest["claims"]}
    verdicts = {item["identity"]: item for item in results["verdicts"]}
    if set(by_id) != set(claims):
        missing = sorted(set(claims) - set(by_id))
        extra = sorted(set(by_id) - set(claims))
        raise BackfillError(f"decisions: missing={missing}, extra={extra}")
    for identity, item in by_id.items():
        claim = claims[identity]
        verdict = verdicts[identity]
        action = item.get("action")
        if action not in ("accept", "revise", "downgrade"):
            raise BackfillError(f"{identity}: неизвестный action {action!r}")
        if verdict["decision"] == "downgrade" and action != "downgrade":
            raise BackfillError(f"{identity}: опровергнутый verdict нельзя принять как code")
        if (
            claim["property"] == "scale_conf"
            and verdict["decision"] == "accept_code"
            and verdict.get("values", {}).get("scale_expr", "").strip() == "x"
            and action != "downgrade"
        ):
            raise BackfillError(f"{identity}: raw identity x не является scale claim")
        note = item.get("note")
        if not isinstance(note, str) or not note.strip():
            raise BackfillError(f"{identity}: нет итогового note")
        if action == "downgrade":
            blocker = item.get("blocker", verdict.get("blocker", ""))
            if not isinstance(blocker, str) or not blocker.strip():
                raise BackfillError(f"{identity}: downgrade без blocker")
            continue
        if verdict["decision"] != "accept_code":
            raise BackfillError(f"{identity}: code без подтверждающего verdict")
        expected_evidence = normalized_verified_evidence(
            verdict.get("evidence", ""),
            item.get("evidence_rewrites"),
            claim["property"],
            identity,
        )
        if item.get("evidence") != expected_evidence:
            raise BackfillError(
                f"{identity}: evidence не является проверяемой нормализацией verdict"
            )
        factual_evidence(item["evidence"], claim["property"], identity)
        if claim["label"] == "Map" and claim["property"] == "confidence":
            for key in ("output_disposition", "target"):
                if item.get(key) != verdict.get(key):
                    raise BackfillError(f"{identity}: {key} отличается от verdict")
            if f"Судьба результата: {item['output_disposition']}" not in note:
                raise BackfillError(f"{identity}: note не содержит output disposition")
            if item["target"] not in note:
                raise BackfillError(f"{identity}: note не содержит target")
        if action == "accept" and item.get("values"):
            raise BackfillError(f"{identity}: accept не изменяет values")
        if action == "revise":
            values = item.get("values")
            allowed = REVISION_FIELDS[(claim["label"], claim["property"])]
            if not isinstance(values, dict) or not values:
                raise BackfillError(f"{identity}: revise без values")
            if not set(values) <= allowed:
                raise BackfillError(
                    f"{identity}: revise меняет запрещённые поля {sorted(set(values)-allowed)}"
                )
    notes_by_node = defaultdict(set)
    for identity, item in by_id.items():
        notes_by_node[claims[identity]["node"]].add(item["note"])
    inconsistent = sorted(node for node, notes in notes_by_node.items() if len(notes) != 1)
    if inconsistent:
        raise BackfillError(f"decisions: разные итоговые note для одного узла {inconsistent}")
    return by_id


def _rows_by_addr(rows, path):
    result = {}
    for row in rows:
        addr = row.get("addr", "").strip().lower()
        if addr in result:
            raise BackfillError(f"{path}: повтор addr {addr}")
        result[addr] = row
    return result


def _apply_to_frozen_row(row, row_decisions):
    expected = dict(row)
    for claim, decision in sorted(
        row_decisions, key=lambda pair: 0 if pair[0]["property"] == "confidence" else 1
    ):
        prop = claim["property"]
        evidence_field = claim["evidence_field"]
        action = decision["action"]
        if action == "downgrade":
            expected[prop] = "candidate"
            expected[evidence_field] = ""
        else:
            expected[prop] = "code"
            expected[evidence_field] = decision["evidence"]
            if action == "revise":
                expected.update(decision["values"])
        expected["note"] = decision["note"]
        if claim["label"] == "Map" and prop == "confidence":
            if (
                expected.get("confidence") == "code"
                and expected.get("role") == "dead"
                and decision.get("output_disposition") != "dead_control_flow"
            ):
                raise BackfillError(
                    f"{claim['identity']}: итоговый role=dead без dead_control_flow"
                )
    return expected


def prepare_application(repo, manifest, decisions_by_id):
    sources = {entry["label"]: entry for entry in manifest["sources"]}
    claims = {claim["identity"]: claim for claim in manifest["claims"]}
    grouped = defaultdict(list)
    for identity, decision in decisions_by_id.items():
        claim = claims[identity]
        grouped[(claim["label"], claim["addr"])].append((claim, decision))

    changes = {}
    for label, source in sources.items():
        frozen_data = git_source(repo, manifest["base_commit"], source["path"])
        oid = run_git(repo, "rev-parse", f"{manifest['base_commit']}:{source['path']}")
        if oid != source["git_oid"]:
            raise BackfillError(f"{source['path']}: git object отличается от manifest")
        if sha256_bytes(frozen_data) != source.get("sha256"):
            raise BackfillError(f"{source['path']}: SHA-256 git blob отличается от manifest")
        frozen_fields, frozen_rows = parse_csv(frozen_data, source["path"])
        if frozen_fields != source["fields"]:
            raise BackfillError(f"{source['path']}: frozen header отличается от manifest")
        current_path = repo / source["path"]
        current_data = current_path.read_bytes()
        current_fields, current_rows = parse_csv(current_data, source["path"])
        if current_fields != frozen_fields:
            raise BackfillError(f"{source['path']}: текущий header отличается от frozen")
        frozen_by_addr = _rows_by_addr(frozen_rows, source["path"])
        current_by_addr = _rows_by_addr(current_rows, source["path"])
        if set(frozen_by_addr) != set(current_by_addr):
            raise BackfillError(f"{source['path']}: состав строк drifted")

        expected_by_addr = {}
        for (row_label, addr), row_decisions in grouped.items():
            if row_label != label:
                continue
            frozen = frozen_by_addr.get(addr)
            if frozen is None:
                raise BackfillError(f"{source['path']}: нет frozen строки {addr}")
            claim_digest = {claim["row_digest"] for claim, _ in row_decisions}
            if claim_digest != {row_digest(frozen_fields, frozen)}:
                raise BackfillError(f"{source['path']}:{addr}: row digest не совпал")
            expected_by_addr[addr] = _apply_to_frozen_row(frozen, row_decisions)

        for addr, current in current_by_addr.items():
            frozen = frozen_by_addr[addr]
            if addr not in expected_by_addr and current != frozen:
                raise BackfillError(f"{source['path']}:{addr}: обнаружен source drift")
        for addr, expected in expected_by_addr.items():
            current = current_by_addr[addr]
            frozen = frozen_by_addr[addr]
            if current != frozen and current != expected:
                raise BackfillError(f"{source['path']}:{addr}: обнаружен source drift")
            current_by_addr[addr] = expected
        output_rows = [current_by_addr[row["addr"].strip().lower()] for row in current_rows]
        expected_data = render_csv(current_fields, output_rows)
        changes[source["path"]] = (current_data, expected_data)
    return changes


def render_diff(changes) -> str:
    chunks = []
    for path in sorted(changes):
        before, after = changes[path]
        if before == after:
            continue
        chunks.extend(
            unified_diff(
                before.decode("utf-8").splitlines(keepends=True),
                after.decode("utf-8").splitlines(keepends=True),
                fromfile=f"a/{path}",
                tofile=f"b/{path}",
            )
        )
    return "".join(chunks)


def debt_status(repo: Path, rom: str):
    counts = Counter()
    for label, template in SOURCE_PATHS.items():
        path = repo / template.format(rom=rom)
        _fields, rows = parse_csv(path.read_bytes(), str(path))
        properties = ("confidence", "scale_conf") if label == "Map" else ("scale_conf",)
        for row in rows:
            for prop in properties:
                evidence_field = EVIDENCE_FIELDS[(label, prop)]
                if row.get(prop, "").strip() == "code" and not row.get(
                    evidence_field, ""
                ).strip():
                    counts[(label, prop)] += 1
    return {
        "Map.confidence": counts[("Map", "confidence")],
        "Map.scale_conf": counts[("Map", "scale_conf")],
        "Axis.scale_conf": counts[("Axis", "scale_conf")],
        "total": sum(counts.values()),
    }


def cmd_freeze(args):
    manifest = freeze_manifest(Path(args.repo).resolve(), args.rom, args.commit)
    output = Path(args.output)
    write_json(output, manifest)
    print(f"manifest: {output}")
    print(f"sha256: {file_sha256(output)}")
    print(f"claims={len(manifest['claims'])}, nodes={len(manifest['nodes'])}")


def cmd_verify_artifacts(args):
    report = verify_artifacts(Path(args.manifest), Path(args.left), Path(args.right))
    output = Path(args.output)
    write_json(output, report)
    print(f"artifacts: {output}")
    print(f"sha256: {report['artifact_set_sha256']}")
    print(f"files={report['count']}")


def cmd_compose_results(args):
    output = Path(args.output)
    run_set = compose_workflow_runs(
        Path(args.manifest),
        Path(args.artifacts),
        Path(args.primary),
        [Path(path) for path in args.recovery],
    )
    write_json(output, run_set)
    _manifest, _artifacts, results = validate_results(
        Path(args.manifest), Path(args.artifacts), output
    )
    print(f"run set: {output}")
    print(f"sha256: {file_sha256(output)}")
    print(
        f"runs={len(run_set['runs'])}, recovered={len(run_set['recovered_identities'])}, "
        f"analyses={len(results['analyses'])}, verdicts={len(results['verdicts'])}"
    )


def cmd_validate_results(args):
    results_path = Path(args.results)
    _manifest, _artifacts, results = validate_results(
        Path(args.manifest), Path(args.artifacts), results_path
    )
    archive = read_json(results_path)
    counts = Counter(item["decision"] for item in results["verdicts"])
    print(f"runId={archive['runId']}, scriptPath={archive['scriptPath']}")
    print(f"analyses={len(results['analyses'])}, verdicts={len(results['verdicts'])}")
    print(", ".join(f"{key}={counts[key]}" for key in sorted(counts)))


def cmd_apply(args):
    manifest_path = Path(args.manifest)
    artifact_path = Path(args.artifacts)
    results_path = Path(args.results)
    manifest, artifact_report, results = validate_results(
        manifest_path, artifact_path, results_path
    )
    decisions = read_json(Path(args.decisions))
    decisions_by_id = validate_decisions(
        manifest,
        results,
        decisions,
        manifest_path,
        artifact_report,
        results_path,
    )
    repo = Path(args.repo).resolve()
    changes = prepare_application(repo, manifest, decisions_by_id)
    diff = render_diff(changes)
    changed = [path for path, (before, after) in changes.items() if before != after]
    if diff:
        sys.stdout.write(diff)
    if args.dry_run:
        print(f"dry-run: changed={len(changed)}")
        return
    for path in changed:
        (repo / path).write_bytes(changes[path][1])
    print(f"applied: changed={len(changed)}")


def cmd_status(args):
    status = debt_status(Path(args.repo).resolve(), args.rom)
    print(json.dumps(status, ensure_ascii=False, sort_keys=True))
    if args.require_zero and status["total"]:
        raise BackfillError(f"локальный evidence debt={status['total']}")


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)

    freeze = sub.add_parser("freeze", help="зафиксировать immutable scope из git")
    freeze.add_argument("--repo", default=str(ROOT))
    freeze.add_argument("--rom", default="JK08A")
    freeze.add_argument("--commit", required=True)
    freeze.add_argument("--output", required=True)
    freeze.set_defaults(func=cmd_freeze)

    artifacts = sub.add_parser(
        "verify-artifacts", help="сверить два независимых набора blind-артефактов"
    )
    artifacts.add_argument("--manifest", required=True)
    artifacts.add_argument("--left", required=True)
    artifacts.add_argument("--right", required=True)
    artifacts.add_argument("--output", required=True)
    artifacts.set_defaults(func=cmd_verify_artifacts)

    compose = sub.add_parser(
        "compose-results", help="собрать primary и точечные recovery Workflow archives"
    )
    compose.add_argument("--manifest", required=True)
    compose.add_argument("--artifacts", required=True)
    compose.add_argument("--primary", required=True)
    compose.add_argument("--recovery", action="append", default=[], required=True)
    compose.add_argument("--output", required=True)
    compose.set_defaults(func=cmd_compose_results)

    results = sub.add_parser("validate-results", help="проверить полный результат Workflow")
    results.add_argument("--manifest", required=True)
    results.add_argument("--artifacts", required=True)
    results.add_argument("--results", required=True)
    results.set_defaults(func=cmd_validate_results)

    apply = sub.add_parser("apply", help="применить проверенные решения к source CSV")
    apply.add_argument("--repo", default=str(ROOT))
    apply.add_argument("--manifest", required=True)
    apply.add_argument("--artifacts", required=True)
    apply.add_argument("--results", required=True)
    apply.add_argument("--decisions", required=True)
    apply.add_argument("--dry-run", action="store_true")
    apply.set_defaults(func=cmd_apply)

    status = sub.add_parser("status", help="показать локальный Map/Axis evidence debt")
    status.add_argument("--repo", default=str(ROOT))
    status.add_argument("--rom", default="JK08A")
    status.add_argument("--require-zero", action="store_true")
    status.set_defaults(func=cmd_status)
    return p


def main():
    args = parser().parse_args()
    try:
        args.func(args)
    except BackfillError as exc:
        raise SystemExit(f"evidence backfill: {exc}") from exc


if __name__ == "__main__":
    main()
