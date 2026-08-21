#!/usr/bin/env python3
"""Build deterministic function-correspondence candidates from Ghidra exports."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
from dataclasses import dataclass
from pathlib import Path
import re


ADDRESS_RE = re.compile(r"^[0-9a-f]{8}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SIGNATURE_FIELDS = (
    "addr",
    "size",
    "instructions",
    "exact_sha256",
    "mnemonic_sha256",
    "shape_sha256",
)
OUTPUT_FIELDS = (
    "source",
    "target",
    "kind",
    "source_size",
    "target_size",
    "instructions",
    "signature_sha256",
)
INTERP_FIELDS = (
    "family",
    "kernel",
    "wrapper",
    "width",
    "height",
    "step",
    "storagetype",
    "axistype_x",
    "axistype_y",
)
INTERP_CORRESPONDENCE_FIELDS = (
    "source_kernel",
    "source_wrapper",
    "target_kernel",
    "target_wrapper",
    "evidence",
)
INTERP_CORRESPONDENCE_STATUS_FIELDS = (
    "source_kernel",
    "source_wrapper",
    "target_kernel",
    "target_wrapper",
    "status",
    "evidence",
)
INTERP_CORRESPONDENCE_STATUSES = {"mapped", "unsupported"}
ENTITY_FIELDS = (
    "entity",
    "source",
    "target",
    "status",
    "sites",
    "function_kinds",
)
SITE_FIELDS = ("func_addr", "ins_addr", "ordinal", "mnemonic")
REFERENCE_FIELDS = (
    "func_addr",
    "ins_addr",
    "ordinal",
    "mnemonic",
    "ref_addr",
    "width",
    "value_hex",
    "ref_type",
)
REFERENCE_OUTPUT_FIELDS = (
    "source_func",
    "target_func",
    "source_ins",
    "target_ins",
    "ordinal",
    "mnemonic",
    "source_ref",
    "target_ref",
    "width",
    "source_value",
    "target_value",
    "function_kind",
)


class CorrespondenceError(ValueError):
    """Raised when an export or correspondence candidate is inconsistent."""


@dataclass(frozen=True)
class Signature:
    addr: str
    size: int
    instructions: int
    exact_sha256: str
    mnemonic_sha256: str
    shape_sha256: str


@dataclass(frozen=True)
class FunctionMatch:
    source: str
    target: str
    kind: str
    source_size: int
    target_size: int
    instructions: int
    signature_sha256: str


@dataclass(frozen=True)
class EntityMatch:
    entity: str
    source: str
    target: str
    status: str
    sites: int
    function_kinds: str


@dataclass(frozen=True)
class InstructionReference:
    func_addr: str
    ins_addr: str
    ordinal: int
    mnemonic: str
    ref_addr: str
    width: int
    value_hex: str
    ref_type: str


@dataclass(frozen=True)
class ReferenceMatch:
    source_func: str
    target_func: str
    source_ins: str
    target_ins: str
    ordinal: int
    mnemonic: str
    source_ref: str
    target_ref: str
    width: int
    source_value: str
    target_value: str
    function_kind: str


def read_signatures(path):
    path = Path(path)
    try:
        with path.open(newline="", encoding="utf-8") as source:
            reader = csv.DictReader(source)
            if tuple(reader.fieldnames or ()) != SIGNATURE_FIELDS:
                raise CorrespondenceError(
                    f"{path}: header {reader.fieldnames}; expected {list(SIGNATURE_FIELDS)}"
                )
            raw_rows = list(reader)
    except OSError as error:
        raise CorrespondenceError(f"signature export cannot be read: {path}") from error

    rows = {}
    for row_number, row in enumerate(raw_rows, 2):
        context = f"{path}:{row_number}"
        if None in row or any(value is None for value in row.values()):
            raise CorrespondenceError(f"{context}: field count differs from header")
        addr = row["addr"]
        if not ADDRESS_RE.fullmatch(addr) or addr in rows:
            raise CorrespondenceError(f"{context}: invalid or duplicate addr {addr!r}")
        try:
            size = int(row["size"])
            instructions = int(row["instructions"])
        except ValueError as error:
            raise CorrespondenceError(f"{context}: size fields must be decimal") from error
        if size <= 0 or instructions <= 0:
            raise CorrespondenceError(f"{context}: size fields must be positive")
        for field in SIGNATURE_FIELDS[3:]:
            if not SHA256_RE.fullmatch(row[field]):
                raise CorrespondenceError(f"{context}: invalid {field}")
        rows[addr] = Signature(
            addr=addr,
            size=size,
            instructions=instructions,
            exact_sha256=row["exact_sha256"],
            mnemonic_sha256=row["mnemonic_sha256"],
            shape_sha256=row["shape_sha256"],
        )
    if not rows:
        raise CorrespondenceError(f"{path}: no function signatures")
    return rows


def _unique_index(rows, key):
    index = defaultdict(list)
    for row in rows.values():
        index[key(row)].append(row)
    return {
        signature: values[0]
        for signature, values in index.items()
        if len(values) == 1
    }


def match_functions(source, target):
    """Pair unique exact bytes first, then unique normalized instruction shape."""
    source_exact = _unique_index(source, lambda row: row.exact_sha256)
    target_exact = _unique_index(target, lambda row: row.exact_sha256)
    matches = {}
    used_targets = set()
    for digest in sorted(source_exact.keys() & target_exact.keys()):
        left, right = source_exact[digest], target_exact[digest]
        if left.instructions != right.instructions or left.size != right.size:
            continue
        matches[left.addr] = FunctionMatch(
            source=left.addr,
            target=right.addr,
            kind="exact-bytes",
            source_size=left.size,
            target_size=right.size,
            instructions=left.instructions,
            signature_sha256=digest,
        )
        used_targets.add(right.addr)

    unmatched_source = {
        addr: row for addr, row in source.items() if addr not in matches
    }
    unmatched_target = {
        addr: row for addr, row in target.items() if addr not in used_targets
    }
    source_shape = _unique_index(
        unmatched_source,
        lambda row: (row.instructions, row.shape_sha256),
    )
    target_shape = _unique_index(
        unmatched_target,
        lambda row: (row.instructions, row.shape_sha256),
    )
    for signature in sorted(source_shape.keys() & target_shape.keys()):
        left, right = source_shape[signature], target_shape[signature]
        matches[left.addr] = FunctionMatch(
            source=left.addr,
            target=right.addr,
            kind="normalized-shape",
            source_size=left.size,
            target_size=right.size,
            instructions=left.instructions,
            signature_sha256=left.shape_sha256,
        )
        used_targets.add(right.addr)

    if len({match.target for match in matches.values()}) != len(matches):
        raise CorrespondenceError("function matching produced duplicate targets")
    return tuple(matches[address] for address in sorted(matches))


def explain_candidates(source_row, target):
    """Return target candidates from strongest to weakest signature."""
    predicates = (
        (
            "exact-bytes",
            lambda row: (
                row.exact_sha256 == source_row.exact_sha256
                and row.size == source_row.size
                and row.instructions == source_row.instructions
            ),
        ),
        (
            "normalized-shape",
            lambda row: (
                row.shape_sha256 == source_row.shape_sha256
                and row.instructions == source_row.instructions
            ),
        ),
        (
            "mnemonic-sequence",
            lambda row: (
                row.mnemonic_sha256 == source_row.mnemonic_sha256
                and row.instructions == source_row.instructions
            ),
        ),
    )
    result = []
    seen = set()
    for kind, predicate in predicates:
        for row in sorted(target.values(), key=lambda item: item.addr):
            if row.addr not in seen and predicate(row):
                result.append((kind, row))
                seen.add(row.addr)
    return tuple(result)


def read_interp(path):
    path = Path(path)
    try:
        with path.open(newline="", encoding="utf-8") as source:
            reader = csv.DictReader(source)
            if tuple(reader.fieldnames or ()) != INTERP_FIELDS:
                raise CorrespondenceError(
                    f"{path}: header {reader.fieldnames}; expected {list(INTERP_FIELDS)}"
                )
            rows = list(reader)
    except OSError as error:
        raise CorrespondenceError(f"interpolation registry cannot be read: {path}") from error
    seen = set()
    for row_number, row in enumerate(rows, 2):
        context = f"{path}:{row_number}"
        for field in ("kernel", "wrapper"):
            if not ADDRESS_RE.fullmatch(row[field]):
                raise CorrespondenceError(f"{context}: invalid {field}")
        if row["wrapper"] in seen:
            raise CorrespondenceError(f"{context}: duplicate wrapper {row['wrapper']}")
        seen.add(row["wrapper"])
    if not rows:
        raise CorrespondenceError(f"{path}: no interpolation entries")
    return rows


def read_interp_correspondence(path):
    path = Path(path)
    try:
        with path.open(newline="", encoding="utf-8") as source:
            reader = csv.DictReader(source)
            header = tuple(reader.fieldnames or ())
            if header not in {
                INTERP_CORRESPONDENCE_FIELDS,
                INTERP_CORRESPONDENCE_STATUS_FIELDS,
            }:
                raise CorrespondenceError(
                    f"{path}: header {reader.fieldnames}; "
                    f"expected {list(INTERP_CORRESPONDENCE_FIELDS)} or "
                    f"{list(INTERP_CORRESPONDENCE_STATUS_FIELDS)}"
                )
            rows = list(reader)
    except OSError as error:
        raise CorrespondenceError(
            f"interpolation correspondence cannot be read: {path}"
        ) from error

    source_keys = set()
    target_keys = set()
    for row_number, row in enumerate(rows, 2):
        context = f"{path}:{row_number}"
        for field in ("source_kernel", "source_wrapper"):
            if not ADDRESS_RE.fullmatch(row[field]):
                raise CorrespondenceError(f"{context}: invalid {field}")
        status = row.get("status") or "mapped"
        row["status"] = status
        if status not in INTERP_CORRESPONDENCE_STATUSES:
            raise CorrespondenceError(
                f"{context}: unsupported correspondence status {status!r}"
            )
        if status == "mapped":
            for field in ("target_kernel", "target_wrapper"):
                if not ADDRESS_RE.fullmatch(row[field]):
                    raise CorrespondenceError(f"{context}: invalid {field}")
        elif row["target_kernel"] or row["target_wrapper"]:
            raise CorrespondenceError(
                f"{context}: unsupported source entry must not name a target"
            )
        source_key = (row["source_kernel"], row["source_wrapper"])
        target_key = (row["target_kernel"], row["target_wrapper"])
        if source_key in source_keys:
            raise CorrespondenceError(f"{context}: duplicate source entry")
        if status == "mapped" and target_key in target_keys:
            raise CorrespondenceError(f"{context}: duplicate target entry")
        if not row["evidence"]:
            raise CorrespondenceError(f"{context}: evidence is required")
        source_keys.add(source_key)
        if status == "mapped":
            target_keys.add(target_key)
    if not rows:
        raise CorrespondenceError(f"{path}: no interpolation correspondences")
    return rows


def _validate_interp_pair(source, target, context, kernel_pairs):
    compared = tuple(
        field for field in INTERP_FIELDS if field not in {"kernel", "wrapper"}
    )
    if any(source[field] != target[field] for field in compared):
        raise CorrespondenceError(f"interpolation entry {context} differs outside addresses")
    prior = kernel_pairs.setdefault(source["kernel"], target["kernel"])
    if prior != target["kernel"]:
        raise CorrespondenceError(
            f"source kernel {source['kernel']} maps to multiple targets"
        )


def pair_interp(source_rows, target_rows, correspondence_rows=None):
    """Pair reviewed interpolation registries with identical row semantics."""
    pairs = []
    kernel_pairs = {}
    if correspondence_rows is None:
        if len(source_rows) != len(target_rows):
            raise CorrespondenceError(
                "interpolation registries have different entry counts"
            )
        for index, (source, target) in enumerate(zip(source_rows, target_rows), 1):
            _validate_interp_pair(source, target, index, kernel_pairs)
            pairs.append((source, target))
        return tuple(pairs)

    source_index = {
        (row["kernel"], row["wrapper"]): row for row in source_rows
    }
    target_index = {
        (row["kernel"], row["wrapper"]): row for row in target_rows
    }
    mapped_sources = set()
    mapped_targets = set()
    for index, correspondence in enumerate(correspondence_rows, 1):
        source_key = (
            correspondence["source_kernel"],
            correspondence["source_wrapper"],
        )
        if source_key in mapped_sources:
            raise CorrespondenceError(
                f"interpolation correspondence {index} repeats a source entry"
            )
        if source_key not in source_index:
            raise CorrespondenceError(
                f"interpolation correspondence {index} has unknown source {source_key}"
            )
        if correspondence.get("status", "mapped") == "unsupported":
            mapped_sources.add(source_key)
            continue
        target_key = (
            correspondence["target_kernel"],
            correspondence["target_wrapper"],
        )
        if target_key in mapped_targets:
            raise CorrespondenceError(
                f"interpolation correspondence {index} repeats a target entry"
            )
        if target_key not in target_index:
            raise CorrespondenceError(
                f"interpolation correspondence {index} has unknown target {target_key}"
            )
        source = source_index[source_key]
        target = target_index[target_key]
        _validate_interp_pair(source, target, index, kernel_pairs)
        pairs.append((source, target))
        mapped_sources.add(source_key)
        mapped_targets.add(target_key)
    missing = sorted(set(source_index) - mapped_sources)
    if missing:
        rendered = ", ".join(f"{kernel}/{wrapper}" for kernel, wrapper in missing)
        raise CorrespondenceError(
            f"interpolation correspondence does not cover source entries: {rendered}"
        )
    return tuple(pairs)


def _read_census(export_dir, kernel, cache):
    path = Path(export_dir) / f"accessors.{int(kernel, 16):x}.csv"
    if path in cache:
        return cache[path]
    try:
        with path.open(newline="", encoding="utf-8") as source:
            rows = list(csv.DictReader(source))
    except OSError as error:
        raise CorrespondenceError(f"accessor census cannot be read: {path}") from error
    required = {"kernel", "wrapper", "accessor", "callsite", "df_r4", "df_r5", "df_r6", "branch"}
    header = set(rows[0]) if rows else set()
    if not required <= header:
        raise CorrespondenceError(
            f"{path}: census header lacks {sorted(required - header)}"
        )
    cache[path] = rows
    return rows


def read_function_sites(export_dir):
    path = Path(export_dir) / "function_sites.csv"
    try:
        with path.open(newline="", encoding="utf-8") as source:
            reader = csv.DictReader(source)
            if tuple(reader.fieldnames or ()) != SITE_FIELDS:
                raise CorrespondenceError(
                    f"{path}: header {reader.fieldnames}; expected {list(SITE_FIELDS)}"
                )
            rows = list(reader)
    except OSError as error:
        raise CorrespondenceError(f"function-site export cannot be read: {path}") from error
    sites = {}
    for row_number, row in enumerate(rows, 2):
        context = f"{path}:{row_number}"
        if not ADDRESS_RE.fullmatch(row["func_addr"]) or not ADDRESS_RE.fullmatch(row["ins_addr"]):
            raise CorrespondenceError(f"{context}: invalid address")
        try:
            ordinal = int(row["ordinal"])
        except ValueError as error:
            raise CorrespondenceError(f"{context}: ordinal must be decimal") from error
        if ordinal < 0 or row["mnemonic"] not in {"jsr", "bsr"}:
            raise CorrespondenceError(f"{context}: invalid site metadata")
        key = (row["func_addr"], row["ins_addr"])
        if key in sites:
            raise CorrespondenceError(f"{context}: duplicate function site")
        sites[key] = (ordinal, row["mnemonic"])
    return sites


def read_function_references(export_dir):
    path = Path(export_dir) / "function_references.csv"
    try:
        with path.open(newline="", encoding="utf-8") as source:
            reader = csv.DictReader(source)
            if tuple(reader.fieldnames or ()) != REFERENCE_FIELDS:
                raise CorrespondenceError(
                    f"{path}: header {reader.fieldnames}; "
                    f"expected {list(REFERENCE_FIELDS)}"
                )
            raw_rows = list(reader)
    except OSError as error:
        raise CorrespondenceError(
            f"function-reference export cannot be read: {path}"
        ) from error

    rows = []
    seen = {}
    for row_number, row in enumerate(raw_rows, 2):
        context = f"{path}:{row_number}"
        for field in ("func_addr", "ins_addr", "ref_addr"):
            if not ADDRESS_RE.fullmatch(row[field]):
                raise CorrespondenceError(f"{context}: invalid {field}")
        try:
            ordinal = int(row["ordinal"])
            width = int(row["width"])
        except ValueError as error:
            raise CorrespondenceError(
                f"{context}: ordinal and width must be decimal"
            ) from error
        if ordinal < 0 or width not in {0, 1, 2, 4}:
            raise CorrespondenceError(f"{context}: invalid ordinal or width")
        if not row["mnemonic"] or not row["ref_type"]:
            raise CorrespondenceError(f"{context}: missing reference metadata")
        expected_hex_length = width * 2
        value_hex = row["value_hex"]
        if (
            len(value_hex) != expected_hex_length
            or (value_hex and not re.fullmatch(r"[0-9a-f]+", value_hex))
        ):
            raise CorrespondenceError(f"{context}: invalid value_hex")
        key = (
            row["func_addr"],
            row["ins_addr"],
            row["ref_addr"],
            row["ref_type"],
        )
        normalized = (ordinal, row["mnemonic"], width, value_hex)
        if key in seen:
            if seen[key] == normalized:
                continue
            raise CorrespondenceError(
                f"{context}: conflicting duplicate reference"
            )
        seen[key] = normalized
        rows.append(
            InstructionReference(
                func_addr=row["func_addr"],
                ins_addr=row["ins_addr"],
                ordinal=ordinal,
                mnemonic=row["mnemonic"],
                ref_addr=row["ref_addr"],
                width=width,
                value_hex=value_hex,
                ref_type=row["ref_type"],
            )
        )
    return tuple(rows)


def match_references(source_export, target_export, function_matches):
    """Pair ROM references at equal instruction ordinals in matched functions."""
    source_rows = read_function_references(source_export)
    target_rows = read_function_references(target_export)
    functions = {match.source: match for match in function_matches}
    target_index = defaultdict(list)
    for row in target_rows:
        target_index[
            (
                row.func_addr,
                row.ordinal,
                row.mnemonic,
                row.width,
                row.ref_type,
            )
        ].append(row)

    result = []
    for source in source_rows:
        function = functions.get(source.func_addr)
        if function is None:
            continue
        peers = target_index.get(
            (
                function.target,
                source.ordinal,
                source.mnemonic,
                source.width,
                source.ref_type,
            ),
            (),
        )
        if len(peers) != 1:
            continue
        target = peers[0]
        result.append(
            ReferenceMatch(
                source_func=source.func_addr,
                target_func=target.func_addr,
                source_ins=source.ins_addr,
                target_ins=target.ins_addr,
                ordinal=source.ordinal,
                mnemonic=source.mnemonic,
                source_ref=source.ref_addr,
                target_ref=target.ref_addr,
                width=source.width,
                source_value=source.value_hex,
                target_value=target.value_hex,
                function_kind=function.kind,
            )
        )
    return tuple(result)


def _rom_address(value):
    return bool(ADDRESS_RE.fullmatch(value or "")) and 0x1000 <= int(value, 16) < 0x180000


def match_entities(
    source_export,
    target_export,
    source_interp,
    target_interp,
    function_matches,
    interp_correspondence=None,
):
    """Map calibration operands at equal call ordinals in homologous functions."""
    function_by_source = {match.source: match for match in function_matches}
    observations = defaultdict(lambda: defaultdict(set))
    caches = ({}, {})
    source_sites = read_function_sites(source_export)
    target_sites = read_function_sites(target_export)
    correspondence_rows = (
        read_interp_correspondence(interp_correspondence)
        if interp_correspondence is not None
        else None
    )
    interp_pairs = pair_interp(
        read_interp(source_interp),
        read_interp(target_interp),
        correspondence_rows,
    )
    for source_entry, target_entry in interp_pairs:
        source_rows = [
            row
            for row in _read_census(
                source_export, source_entry["kernel"], caches[0]
            )
            if row["wrapper"] == source_entry["wrapper"]
        ]
        target_rows = [
            row
            for row in _read_census(
                target_export, target_entry["kernel"], caches[1]
            )
            if row["wrapper"] == target_entry["wrapper"]
        ]
        target_index = defaultdict(list)
        for row in target_rows:
            target_index[row["accessor"]].append(row)
        source_groups = defaultdict(list)
        for row in source_rows:
            source_groups[row["accessor"]].append(row)

        for source_accessor, rows in source_groups.items():
            function_match = function_by_source.get(source_accessor)
            if function_match is None:
                continue
            peers = target_index.get(function_match.target, [])
            by_site = defaultdict(list)
            for row in peers:
                site = target_sites.get((row["accessor"], row["callsite"]))
                if site is not None:
                    by_site[(site, row["branch"])].append(row)
            for source_row in rows:
                site = source_sites.get(
                    (source_row["accessor"], source_row["callsite"])
                )
                if site is None:
                    continue
                peers_at_site = by_site.get((site, source_row["branch"]), [])
                if len(peers_at_site) != 1:
                    continue
                target_row = peers_at_site[0]
                operands = [("Map", "df_r4")]
                if source_entry["family"] == "explicit":
                    operands.append(("Axis", "df_r5"))
                    if source_entry["height"]:
                        operands.append(("Axis", "df_r6"))
                evidence = (
                    source_accessor,
                    source_row["callsite"],
                    function_match.kind,
                )
                for entity, field in operands:
                    left, right = source_row[field], target_row[field]
                    if _rom_address(left) and _rom_address(right):
                        observations[(entity, left)][right].add(evidence)

    target_sources = defaultdict(set)
    for (entity, source), targets in observations.items():
        if len(targets) == 1:
            target_sources[(entity, next(iter(targets)))].add(source)

    result = []
    for (entity, source), targets in sorted(observations.items()):
        for target, evidence in sorted(targets.items()):
            if len(targets) != 1:
                status = "source-ambiguous"
            elif len(target_sources[(entity, target)]) != 1:
                status = "target-collision"
            else:
                status = "unique"
            result.append(
                EntityMatch(
                    entity=entity,
                    source=source,
                    target=target,
                    status=status,
                    sites=len(evidence),
                    function_kinds=";".join(sorted({item[2] for item in evidence})),
                )
            )
    return tuple(result)


def write_matches(path, matches):
    path = Path(path)
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
        writer.writeheader()
        for match in matches:
            writer.writerow({field: getattr(match, field) for field in OUTPUT_FIELDS})


def write_entities(path, matches):
    path = Path(path)
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=ENTITY_FIELDS, lineterminator="\n")
        writer.writeheader()
        for match in matches:
            writer.writerow({field: getattr(match, field) for field in ENTITY_FIELDS})


def write_reference_matches(path, matches):
    path = Path(path)
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(
            output,
            fieldnames=REFERENCE_OUTPUT_FIELDS,
            lineterminator="\n",
        )
        writer.writeheader()
        for match in matches:
            writer.writerow(
                {
                    field: getattr(match, field)
                    for field in REFERENCE_OUTPUT_FIELDS
                }
            )


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Pair unique exact and normalized-shape Ghidra functions."
    )
    parser.add_argument("source_export", type=Path)
    parser.add_argument("target_export", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--source-interp", type=Path)
    parser.add_argument("--target-interp", type=Path)
    parser.add_argument("--interp-correspondence", type=Path)
    parser.add_argument("--entity-output", type=Path)
    parser.add_argument("--reference-output", type=Path)
    parser.add_argument(
        "--explain-address",
        action="append",
        default=[],
        help="show all exact, normalized-shape, and mnemonic candidates",
    )
    args = parser.parse_args(argv)

    source_path = args.source_export / "function_signatures.csv"
    target_path = args.target_export / "function_signatures.csv"
    source = read_signatures(source_path)
    target = read_signatures(target_path)
    matches = match_functions(source, target)
    exact = sum(match.kind == "exact-bytes" for match in matches)
    normalized = len(matches) - exact
    print(
        f"source={len(source)} target={len(target)} matched={len(matches)} "
        f"exact={exact} normalized_shape={normalized}"
    )
    for address in args.explain_address:
        key = address.lower().removeprefix("0x").rjust(8, "0")
        if key not in source:
            raise CorrespondenceError(f"source function {address} is absent")
        candidates = explain_candidates(source[key], target)
        rendered = ", ".join(
            f"{row.addr}:{kind}:size={row.size}"
            for kind, row in candidates
        )
        print(f"{key} -> {rendered or 'no signature candidate'}")
    if args.output is not None:
        write_matches(args.output, matches)
        print(f"output={args.output}")
    if args.reference_output is not None:
        references = match_references(
            args.source_export,
            args.target_export,
            matches,
        )
        write_reference_matches(args.reference_output, references)
        print(
            f"references={len(references)} "
            f"output={args.reference_output}"
        )
    entity_options = (args.source_interp, args.target_interp, args.entity_output)
    if any(item is not None for item in entity_options):
        if any(item is None for item in entity_options):
            raise CorrespondenceError(
                "--source-interp, --target-interp, and --entity-output are required together"
            )
        entities = match_entities(
            args.source_export,
            args.target_export,
            args.source_interp,
            args.target_interp,
            matches,
            args.interp_correspondence,
        )
        write_entities(args.entity_output, entities)
        unique = sum(match.status == "unique" for match in entities)
        print(
            f"entities={len(entities)} unique={unique} "
            f"ambiguous={len(entities) - unique} output={args.entity_output}"
        )
    elif args.interp_correspondence is not None:
        raise CorrespondenceError(
            "--interp-correspondence requires interpolation entity output options"
        )


if __name__ == "__main__":
    main()
