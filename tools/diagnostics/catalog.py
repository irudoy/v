"""Shared contracts for the diagnostic source catalogs.

The tracked CSV and JSONL files are reproducible source projections. Memgraph is
the integration and query layer. Every source-derived row carries a stable
dataset key and a source fragment identifier.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import tomllib
from pathlib import Path
from typing import Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]
REFS = ROOT / "refs" / "diagnostics"
ROM_IMAGES = ROOT / "rom-images"

DTC_RE = re.compile(r"\b([PBCU][0-9A-F]{4})\b", re.IGNORECASE)
DTC_RANGE_RE = re.compile(
    r"\b([PBCU])([0-9A-F]{4})\s*(?:-|TO)\s*(?:[PBCU])?([0-9A-F]{4})\b",
    re.IGNORECASE,
)
HEX_RE = re.compile(r"^(?:0x)?[0-9a-fA-F]+$")


class CatalogError(ValueError):
    """A source projection violates its deterministic contract."""


def require_pinned_snapshot(
    source_root: Path, revision: str, source_url: str, paths: Sequence[str],
    *, expected_license: str,
) -> None:
    """Validate the manifest and retained files of a repository snapshot."""
    manifest_path = source_root / "source.toml"
    if not manifest_path.exists():
        raise CatalogError(
            f"{manifest_path}: pinned source snapshot is unavailable; "
            "restore the source snapshot from this repository"
        )
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise CatalogError(f"{manifest_path}: expected a regular non-symlink file")
    try:
        with manifest_path.open("rb") as source:
            manifest = tomllib.load(source)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise CatalogError(f"{manifest_path}: cannot read source manifest: {error}") from error
    if type(manifest.get("schema")) is not int or manifest["schema"] != 1:
        raise CatalogError(f"{manifest_path}: expected source snapshot schema 1")
    if manifest.get("source_url") != source_url:
        raise CatalogError(f"{manifest_path}: source URL does not match {source_url}")
    if manifest.get("revision") != revision:
        raise CatalogError(f"{manifest_path}: revision does not match {revision}")
    if manifest.get("license") != expected_license:
        raise CatalogError(f"{manifest_path}: source license does not match {expected_license}")
    files = manifest.get("files")
    if not isinstance(files, dict) or set(files) != set(paths):
        raise CatalogError(f"{manifest_path}: file keys do not match the required source files")
    for relative, expected in files.items():
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts or path.as_posix() != relative:
            raise CatalogError(f"{manifest_path}: invalid source-relative path {relative!r}")
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise CatalogError(f"{manifest_path}: invalid SHA-256 for {relative}")
        source_path = source_root
        for part in path.parts:
            source_path = source_path / part
            if source_path.is_symlink():
                raise CatalogError(f"{source_path}: expected a non-symlink source path")
        if not source_path.is_file():
            raise CatalogError(f"{source_path}: required regular source file is missing")
        try:
            actual = sha256_file(source_path)
        except OSError as error:
            raise CatalogError(f"{source_path}: cannot read source file: {error}") from error
        if actual != expected:
            raise CatalogError(f"{source_path}: SHA-256 does not match the source manifest")


def require_pinned_git_tree(
    source_root: Path, revision: str, paths: Sequence[str]
) -> None:
    """Require the selected source files to match a pinned Git revision."""
    try:
        head = subprocess.run(
            ["git", "-C", str(source_root), "rev-parse", "HEAD"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ).stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError) as error:
        detail = getattr(error, "stderr", "") or str(error)
        raise CatalogError(
            f"{source_root}: cannot read git revision: {detail}"
        ) from error
    if head != revision:
        raise CatalogError(f"{source_root}: revision {head}, expected {revision}")

    try:
        difference = subprocess.run(
            [
                "git",
                "-C",
                str(source_root),
                "diff",
                "--quiet",
                "--no-ext-diff",
                revision,
                "--",
                *paths,
            ],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError as error:
        raise CatalogError(f"{source_root}: git command is unavailable") from error
    if difference.returncode == 1:
        raise CatalogError(
            f"{source_root}: pinned source files differ from revision {revision}"
        )
    if difference.returncode != 0:
        detail = difference.stderr.strip() or f"exit status {difference.returncode}"
        raise CatalogError(
            f"{source_root}: cannot compare pinned source files: {detail}"
        )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def slug(value: str) -> str:
    result = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not result:
        raise CatalogError(f"value has no stable slug: {value!r}")
    return result


def stable_id(*parts: object) -> str:
    values = [slug(str(part)) for part in parts if str(part).strip()]
    if not values:
        raise CatalogError("stable_id requires at least one non-empty component")
    return ":".join(values)


def keyed_slug(value: str) -> str:
    """Return a readable slug that remains unique across punctuation variants."""
    return f"{slug(value)}-{sha256_text(value)[:8]}"


def extract_dtc_codes(text: str) -> list[str]:
    """Return normalized codes, expanding short same-prefix ranges."""
    codes = {match.group(1).upper() for match in DTC_RE.finditer(text)}
    for match in DTC_RANGE_RE.finditer(text):
        prefix = match.group(1).upper()
        start = int(match.group(2), 16)
        end = int(match.group(3), 16)
        if end < start or end - start > 64:
            continue
        codes.update(f"{prefix}{value:04X}" for value in range(start, end + 1))
    return sorted(codes)


def normalize_hex(value: str, *, even: bool = True) -> str:
    result = value.strip().lower()
    if result.startswith("0x"):
        result = result[2:]
    result = re.sub(r"[\s:_-]", "", result)
    if not result or not HEX_RE.fullmatch(result):
        raise CatalogError(f"invalid hexadecimal value: {value!r}")
    if even and len(result) % 2:
        result = "0" + result
    return result


def write_csv(
    path: Path,
    fieldnames: Sequence[str],
    rows: Iterable[Mapping[str, object]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    materialized = list(rows)
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(
            destination,
            fieldnames=fieldnames,
            extrasaction="raise",
            lineterminator="\n",
        )
        writer.writeheader()
        for row in materialized:
            writer.writerow({name: scalar(row.get(name, "")) for name in fieldnames})


def write_jsonl(path: Path, rows: Iterable[Mapping[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as destination:
        for row in rows:
            destination.write(
                json.dumps(dict(row), ensure_ascii=False, sort_keys=True) + "\n"
            )


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def read_jsonl(path: Path) -> list[dict[str, object]]:
    rows = []
    with path.open(encoding="utf-8") as source:
        for number, line in enumerate(source, 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise CatalogError(f"{path}:{number}: {error}") from error
    return rows


def scalar(value: object) -> object:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple, set)):
        return ";".join(str(item) for item in value)
    return value


def require_unique(rows: Iterable[Mapping[str, object]], fields: Sequence[str]) -> None:
    seen: dict[tuple[object, ...], int] = {}
    for number, row in enumerate(rows, 2):
        key = tuple(row.get(field) for field in fields)
        if key in seen:
            raise CatalogError(
                f"duplicate key {fields}={key!r} at rows {seen[key]} and {number}"
            )
        seen[key] = number
