#!/usr/bin/env python3
"""Build deterministic function-correspondence candidates from Ghidra exports."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from dataclasses import dataclass
import hashlib
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
CALL_FIELDS = ("src", "dst")
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
EXACT_STORAGE_FIELDS = (
    "entity",
    "source",
    "target",
    "status",
    "bytes",
    "contracts",
    "source_sites",
    "target_sites",
)
STORAGE_ACCESSOR_FIELDS = (
    "source",
    "target",
    "status",
    "anchors",
    "contracts",
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


@dataclass(frozen=True)
class ExactStorageMatch:
    entity: str
    source: str
    target: str
    status: str
    bytes: int
    contracts: int
    source_sites: int
    target_sites: int


@dataclass(frozen=True)
class StorageAccessorMatch:
    source: str
    target: str
    status: str
    anchors: int
    contracts: int
    kind: str = "exact-map-storage-anchor"


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


def _read_calls(export_dir):
    path = Path(export_dir) / "calls.csv"
    try:
        with path.open(newline="", encoding="utf-8") as source:
            reader = csv.DictReader(source)
            if tuple(reader.fieldnames or ()) != CALL_FIELDS:
                raise CorrespondenceError(
                    f"{path}: header {reader.fieldnames}; expected {list(CALL_FIELDS)}"
                )
            rows = list(reader)
    except OSError as error:
        raise CorrespondenceError(f"call export cannot be read: {path}") from error

    outgoing = defaultdict(Counter)
    incoming = defaultdict(Counter)
    for row_number, row in enumerate(rows, 2):
        context = f"{path}:{row_number}"
        if not ADDRESS_RE.fullmatch(row["src"]) or not ADDRESS_RE.fullmatch(
            row["dst"]
        ):
            raise CorrespondenceError(f"{context}: invalid call address")
        outgoing[row["src"]][row["dst"]] += 1
        incoming[row["dst"]][row["src"]] += 1
    return outgoing, incoming


def _accessor_contract_rows(export_dir, entries):
    result = defaultdict(lambda: defaultdict(list))
    cache = {}
    for contract, entry in enumerate(entries):
        for row in _read_census(export_dir, entry["kernel"], cache):
            if row["wrapper"] == entry["wrapper"]:
                result[row["accessor"]][contract].append(row)
    return result


def _contract_call_signature(rows_by_contract):
    signature = []
    for contract, rows in sorted(rows_by_contract.items()):
        by_callsite = defaultdict(list)
        for row in rows:
            by_callsite[row["callsite"]].append(row)
        site_shape = tuple(
            sorted(
                (
                    len(site_rows),
                    tuple(sorted(row["branch"] for row in site_rows)),
                )
                for site_rows in by_callsite.values()
            )
        )
        signature.append((contract, site_shape))
    return tuple(signature)


def _fingerprint_digest(value):
    return hashlib.sha256(repr(value).encode("utf-8")).hexdigest()


def _add_mapping(mapping, kinds, digests, source, target, kind, digest):
    prior_target = mapping.get(source)
    if prior_target is not None and prior_target != target:
        raise CorrespondenceError(
            f"structural function {source} maps to both {prior_target} and {target}"
        )
    if prior_target == target:
        return
    prior_sources = [left for left, right in mapping.items() if right == target]
    if prior_sources and source not in prior_sources:
        raise CorrespondenceError(
            f"structural target {target} maps from both {prior_sources[0]} and {source}"
        )
    mapping[source] = target
    kinds[source] = kind
    digests[source] = digest


def _source_neighbor_fingerprint(function, outgoing, incoming, mapping):
    mapped_out = Counter()
    mapped_in = Counter()
    for neighbor, count in outgoing[function].items():
        if neighbor in mapping:
            mapped_out[mapping[neighbor]] += count
    for neighbor, count in incoming[function].items():
        if neighbor in mapping:
            mapped_in[mapping[neighbor]] += count
    return tuple(sorted(mapped_out.items())), tuple(sorted(mapped_in.items()))


def _target_neighbor_fingerprint(function, outgoing, incoming, mapped_targets):
    mapped_out = tuple(
        sorted(
            (neighbor, count)
            for neighbor, count in outgoing[function].items()
            if neighbor in mapped_targets
        )
    )
    mapped_in = tuple(
        sorted(
            (neighbor, count)
            for neighbor, count in incoming[function].items()
            if neighbor in mapped_targets
        )
    )
    return mapped_out, mapped_in


def match_structural_functions(
    source_export,
    target_export,
    source_interp,
    target_interp,
    function_matches,
    interp_correspondence=None,
    *,
    minimum_neighbor_anchors=2,
):
    """Extend hash matches with reviewed contracts and unique graph fingerprints."""
    if minimum_neighbor_anchors < 2:
        raise CorrespondenceError("structural matching needs at least two anchors")
    source_signatures = read_signatures(
        Path(source_export) / "function_signatures.csv"
    )
    target_signatures = read_signatures(
        Path(target_export) / "function_signatures.csv"
    )
    correspondence_rows = (
        read_interp_correspondence(interp_correspondence)
        if interp_correspondence is not None
        else None
    )
    pairs = pair_interp(
        read_interp(source_interp),
        read_interp(target_interp),
        correspondence_rows,
    )
    mapping = {}
    kinds = {}
    digests = {}
    for match in function_matches:
        _add_mapping(
            mapping,
            kinds,
            digests,
            match.source,
            match.target,
            match.kind,
            match.signature_sha256,
        )
    for source_entry, target_entry in pairs:
        for field in ("kernel", "wrapper"):
            source = source_entry[field]
            target = target_entry[field]
            _add_mapping(
                mapping,
                kinds,
                digests,
                source,
                target,
                "interpolation-contract",
                _fingerprint_digest((field, source, target)),
            )

    source_rows = _accessor_contract_rows(
        source_export, [source for source, _ in pairs]
    )
    target_rows = _accessor_contract_rows(
        target_export, [target for _, target in pairs]
    )
    source_by_signature = defaultdict(list)
    target_by_signature = defaultdict(list)
    for accessor, rows in source_rows.items():
        source_by_signature[_contract_call_signature(rows)].append(accessor)
    for accessor, rows in target_rows.items():
        target_by_signature[_contract_call_signature(rows)].append(accessor)
    for signature, sources in sorted(source_by_signature.items()):
        targets = target_by_signature.get(signature, ())
        if len(sources) == len(targets) == 1:
            _add_mapping(
                mapping,
                kinds,
                digests,
                sources[0],
                targets[0],
                "unique-interpolation-call-signature",
                _fingerprint_digest(signature),
            )

    source_out, source_in = _read_calls(source_export)
    target_out, target_in = _read_calls(target_export)
    while True:
        mapped_targets = set(mapping.values())
        source_index = defaultdict(list)
        target_index = defaultdict(list)
        for function in source_signatures:
            if function in mapping:
                continue
            fingerprint = _source_neighbor_fingerprint(
                function, source_out, source_in, mapping
            )
            if len(fingerprint[0]) + len(fingerprint[1]) >= minimum_neighbor_anchors:
                source_index[fingerprint].append(function)
        for function in target_signatures:
            if function in mapped_targets:
                continue
            fingerprint = _target_neighbor_fingerprint(
                function, target_out, target_in, mapped_targets
            )
            if len(fingerprint[0]) + len(fingerprint[1]) >= minimum_neighbor_anchors:
                target_index[fingerprint].append(function)
        additions = [
            (sources[0], target_index[fingerprint][0], fingerprint)
            for fingerprint, sources in sorted(source_index.items())
            if len(sources) == 1 and len(target_index.get(fingerprint, ())) == 1
        ]
        if not additions:
            break
        for source, target, fingerprint in additions:
            _add_mapping(
                mapping,
                kinds,
                digests,
                source,
                target,
                "unique-mapped-neighbor-fingerprint",
                _fingerprint_digest(fingerprint),
            )

    result = []
    for source, target in sorted(mapping.items()):
        if source not in source_signatures or target not in target_signatures:
            continue
        left = source_signatures[source]
        right = target_signatures[target]
        result.append(
            FunctionMatch(
                source=source,
                target=target,
                kind=kinds[source],
                source_size=left.size,
                target_size=right.size,
                instructions=left.instructions,
                signature_sha256=digests[source],
            )
        )
    return tuple(result)


def structural_accessor_matches(
    source_export,
    target_export,
    source_interp,
    target_interp,
    function_matches,
    interp_correspondence=None,
):
    """Keep injective structural function pairs that share reviewed contracts."""
    correspondence_rows = (
        read_interp_correspondence(interp_correspondence)
        if interp_correspondence is not None
        else None
    )
    pairs = pair_interp(
        read_interp(source_interp),
        read_interp(target_interp),
        correspondence_rows,
    )
    source_rows = _accessor_contract_rows(
        source_export, [source for source, _ in pairs]
    )
    target_rows = _accessor_contract_rows(
        target_export, [target for _, target in pairs]
    )
    result = []
    for match in function_matches:
        source_contracts = set(source_rows.get(match.source, ()))
        target_contracts = set(target_rows.get(match.target, ()))
        common = source_contracts & target_contracts
        if not common:
            continue
        result.append(
            StorageAccessorMatch(
                source=match.source,
                target=match.target,
                status="unique",
                anchors=len(common),
                contracts=len(common),
                kind=match.kind,
            )
        )
    return tuple(result)


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


def _storage_width(storage_type):
    if storage_type == "uint8":
        return 1
    if storage_type == "uint16":
        return 2
    raise CorrespondenceError(f"unsupported interpolation storage type {storage_type!r}")


def _operand_specs(interp):
    if interp["family"] != "explicit":
        return ()
    width = int(interp["width"])
    height = int(interp["height"]) if interp["height"] else 1
    specs = [
        ("Map", "df_r4", width * height * _storage_width(interp["storagetype"])),
        ("Axis", "df_r5", width * _storage_width(interp["axistype_x"])),
    ]
    if interp["height"]:
        specs.append(
            ("Axis", "df_r6", height * _storage_width(interp["axistype_y"]))
        )
    return tuple(specs)


def _operand_sites(rows, wrapper, field, image_size, byte_count):
    sites = defaultdict(int)
    for row in rows:
        value = row[field]
        if row["wrapper"] != wrapper or not _rom_address(value):
            continue
        address = int(value, 16)
        if address + byte_count <= image_size:
            sites[address] += 1
    return sites


def match_exact_storage(
    source_export,
    target_export,
    source_interp,
    target_interp,
    source_image,
    target_image,
    interp_correspondence=None,
):
    """Match exact operand bytes only within reviewed interpolation contracts."""
    source_bytes = Path(source_image).read_bytes()
    target_bytes = Path(target_image).read_bytes()
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
    caches = ({}, {})
    observations = defaultdict(lambda: defaultdict(set))
    site_counts = {}
    for source_entry, target_entry in interp_pairs:
        source_rows = _read_census(source_export, source_entry["kernel"], caches[0])
        target_rows = _read_census(target_export, target_entry["kernel"], caches[1])
        for entity, field, byte_count in _operand_specs(source_entry):
            source_sites = _operand_sites(
                source_rows,
                source_entry["wrapper"],
                field,
                len(source_bytes),
                byte_count,
            )
            target_sites = _operand_sites(
                target_rows,
                target_entry["wrapper"],
                field,
                len(target_bytes),
                byte_count,
            )
            target_by_bytes = defaultdict(list)
            for address in target_sites:
                target_by_bytes[target_bytes[address:address + byte_count]].append(address)
            contract = (
                source_entry["kernel"],
                source_entry["wrapper"],
                target_entry["kernel"],
                target_entry["wrapper"],
                byte_count,
            )
            for source_address in source_sites:
                value = source_bytes[source_address:source_address + byte_count]
                for target_address in target_by_bytes[value]:
                    observations[(entity, source_address)][target_address].add(contract)
                    site_counts[(entity, source_address, target_address, contract)] = (
                        source_sites[source_address],
                        target_sites[target_address],
                    )

    target_sources = defaultdict(set)
    for (entity, source_address), targets in observations.items():
        if len(targets) == 1:
            target_sources[(entity, next(iter(targets)))].add(source_address)

    result = []
    for (entity, source_address), targets in sorted(observations.items()):
        for target_address, contracts in sorted(targets.items()):
            if len(targets) != 1:
                status = "source-ambiguous"
            elif len(target_sources[(entity, target_address)]) != 1:
                status = "target-collision"
            else:
                status = "unique"
            byte_counts = {contract[-1] for contract in contracts}
            if len(byte_counts) != 1:
                raise CorrespondenceError(
                    f"{entity} {source_address:08x}/{target_address:08x} "
                    "matches contracts with different extents"
                )
            counts = [
                site_counts[(entity, source_address, target_address, contract)]
                for contract in contracts
            ]
            result.append(ExactStorageMatch(
                entity=entity,
                source=f"{source_address:08x}",
                target=f"{target_address:08x}",
                status=status,
                bytes=next(iter(byte_counts)),
                contracts=len(contracts),
                source_sites=sum(count[0] for count in counts),
                target_sites=sum(count[1] for count in counts),
            ))
    return tuple(result)


def match_storage_accessors(
    source_export,
    target_export,
    source_interp,
    target_interp,
    storage_matches,
    interp_correspondence=None,
):
    """Anchor accessor pairs through unique exact map-storage matches."""
    exact_maps = {
        (match.source, match.target)
        for match in storage_matches
        if match.entity == "Map" and match.status == "unique"
    }
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
    caches = ({}, {})
    observations = defaultdict(lambda: defaultdict(set))
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
        source_by_map = defaultdict(set)
        target_by_map = defaultdict(set)
        for row in source_rows:
            if _rom_address(row["df_r4"]):
                source_by_map[row["df_r4"]].add(row["accessor"])
        for row in target_rows:
            if _rom_address(row["df_r4"]):
                target_by_map[row["df_r4"]].add(row["accessor"])
        contract = (
            source_entry["kernel"],
            source_entry["wrapper"],
            target_entry["kernel"],
            target_entry["wrapper"],
        )
        for source_map, target_map in exact_maps:
            source_accessors = source_by_map.get(source_map, ())
            target_accessors = target_by_map.get(target_map, ())
            if len(source_accessors) != 1 or len(target_accessors) != 1:
                continue
            source_accessor = next(iter(source_accessors))
            target_accessor = next(iter(target_accessors))
            observations[source_accessor][target_accessor].add(
                (source_map, target_map, contract)
            )

    target_sources = defaultdict(set)
    for source, targets in observations.items():
        if len(targets) == 1:
            target_sources[next(iter(targets))].add(source)

    result = []
    for source, targets in sorted(observations.items()):
        for target, evidence in sorted(targets.items()):
            if len(targets) != 1:
                status = "source-ambiguous"
            elif len(target_sources[target]) != 1:
                status = "target-collision"
            else:
                status = "unique"
            result.append(StorageAccessorMatch(
                source=source,
                target=target,
                status=status,
                anchors=len({(item[0], item[1]) for item in evidence}),
                contracts=len({item[2] for item in evidence}),
            ))
    return tuple(result)


def _ordered_site_groups(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[row["callsite"]].append(row)
    return tuple(
        tuple(sorted(groups[callsite], key=lambda row: row["branch"]))
        for callsite in sorted(groups, key=lambda value: int(value, 16))
    )


def match_entities_by_call_order(
    source_export,
    target_export,
    source_interp,
    target_interp,
    accessor_matches,
    interp_correspondence=None,
):
    """Pair operands by wrapper-local call order in unique anchored functions."""
    function_by_source = {
        match.source: match
        for match in accessor_matches
        if match.status == "unique"
    }
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
    caches = ({}, {})
    observations = defaultdict(lambda: defaultdict(set))
    for source_entry, target_entry in interp_pairs:
        source_groups = defaultdict(list)
        target_groups = defaultdict(list)
        for row in _read_census(source_export, source_entry["kernel"], caches[0]):
            if row["wrapper"] == source_entry["wrapper"]:
                source_groups[row["accessor"]].append(row)
        for row in _read_census(target_export, target_entry["kernel"], caches[1]):
            if row["wrapper"] == target_entry["wrapper"]:
                target_groups[row["accessor"]].append(row)
        for source_accessor, source_rows in source_groups.items():
            function_match = function_by_source.get(source_accessor)
            if function_match is None:
                continue
            target_rows = target_groups.get(function_match.target, ())
            source_sites = _ordered_site_groups(source_rows)
            target_sites = _ordered_site_groups(target_rows)
            if len(source_sites) != len(target_sites) or not source_sites:
                continue
            if any(
                len(source_site) != len(target_site)
                for source_site, target_site in zip(source_sites, target_sites)
            ):
                continue
            operands = [("Map", "df_r4")]
            if source_entry["family"] == "explicit":
                operands.append(("Axis", "df_r5"))
                if source_entry["height"]:
                    operands.append(("Axis", "df_r6"))
            for site_index, (source_site, target_site) in enumerate(
                zip(source_sites, target_sites)
            ):
                for source_row, target_row in zip(source_site, target_site):
                    evidence = (
                        source_accessor,
                        source_entry["wrapper"],
                        site_index,
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
            result.append(EntityMatch(
                entity=entity,
                source=source,
                target=target,
                status=status,
                sites=len(evidence),
                function_kinds=";".join(
                    sorted({f"ordered-{item[3]}" for item in evidence})
                ),
            ))
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


def write_exact_storage_matches(path, matches):
    path = Path(path)
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(
            output,
            fieldnames=EXACT_STORAGE_FIELDS,
            lineterminator="\n",
        )
        writer.writeheader()
        for match in matches:
            writer.writerow({
                field: getattr(match, field)
                for field in EXACT_STORAGE_FIELDS
            })


def write_storage_accessor_matches(path, matches):
    path = Path(path)
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(
            output,
            fieldnames=STORAGE_ACCESSOR_FIELDS,
            lineterminator="\n",
        )
        writer.writeheader()
        for match in matches:
            writer.writerow({
                field: getattr(match, field)
                for field in STORAGE_ACCESSOR_FIELDS
            })


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
    parser.add_argument("--source-image", type=Path)
    parser.add_argument("--target-image", type=Path)
    parser.add_argument("--exact-storage-output", type=Path)
    parser.add_argument("--storage-accessor-output", type=Path)
    parser.add_argument("--ordered-entity-output", type=Path)
    parser.add_argument("--structural-function-output", type=Path)
    parser.add_argument("--structural-entity-output", type=Path)
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
    interp_options = (args.source_interp, args.target_interp)
    if args.entity_output is not None:
        if any(item is None for item in interp_options):
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
    structural_outputs = (
        args.structural_function_output,
        args.structural_entity_output,
    )
    if any(item is not None for item in structural_outputs):
        if any(item is None for item in interp_options):
            raise CorrespondenceError(
                "--source-interp and --target-interp are required with "
                "structural outputs"
            )
        structural_matches = match_structural_functions(
            args.source_export,
            args.target_export,
            args.source_interp,
            args.target_interp,
            matches,
            args.interp_correspondence,
        )
        kinds = Counter(match.kind for match in structural_matches)
        rendered_kinds = ",".join(
            f"{kind}={count}" for kind, count in sorted(kinds.items())
        )
        print(
            f"structural_functions={len(structural_matches)} "
            f"added={len(structural_matches) - len(matches)} "
            f"kinds={rendered_kinds}"
        )
        if args.structural_function_output is not None:
            write_matches(args.structural_function_output, structural_matches)
            print(f"output={args.structural_function_output}")
        if args.structural_entity_output is not None:
            structural_accessors = structural_accessor_matches(
                args.source_export,
                args.target_export,
                args.source_interp,
                args.target_interp,
                structural_matches,
                args.interp_correspondence,
            )
            structural_entities = match_entities_by_call_order(
                args.source_export,
                args.target_export,
                args.source_interp,
                args.target_interp,
                structural_accessors,
                args.interp_correspondence,
            )
            write_entities(args.structural_entity_output, structural_entities)
            structural_unique = sum(
                match.status == "unique" for match in structural_entities
            )
            print(
                f"structural_accessors={len(structural_accessors)} "
                f"structural_entities={len(structural_entities)} "
                f"unique={structural_unique} "
                f"ambiguous={len(structural_entities) - structural_unique} "
                f"output={args.structural_entity_output}"
            )
    storage_outputs = (
        args.exact_storage_output,
        args.storage_accessor_output,
        args.ordered_entity_output,
    )
    if any(item is not None for item in storage_outputs):
        exact_options = (
            args.source_interp,
            args.target_interp,
            args.source_image,
            args.target_image,
        )
        if any(item is None for item in exact_options):
            raise CorrespondenceError(
                "--source-interp, --target-interp, --source-image, "
                "and --target-image are required with storage-derived outputs"
            )
        storage_matches = match_exact_storage(
            args.source_export,
            args.target_export,
            args.source_interp,
            args.target_interp,
            args.source_image,
            args.target_image,
            args.interp_correspondence,
        )
        unique = sum(match.status == "unique" for match in storage_matches)
        if args.exact_storage_output is not None:
            write_exact_storage_matches(args.exact_storage_output, storage_matches)
            print(
                f"exact_storage={len(storage_matches)} unique={unique} "
                f"ambiguous={len(storage_matches) - unique} "
                f"output={args.exact_storage_output}"
            )
        accessor_matches = match_storage_accessors(
            args.source_export,
            args.target_export,
            args.source_interp,
            args.target_interp,
            storage_matches,
            args.interp_correspondence,
        )
        if args.storage_accessor_output is not None:
            write_storage_accessor_matches(
                args.storage_accessor_output, accessor_matches
            )
            accessor_unique = sum(
                match.status == "unique" for match in accessor_matches
            )
            print(
                f"storage_accessors={len(accessor_matches)} "
                f"unique={accessor_unique} "
                f"ambiguous={len(accessor_matches) - accessor_unique} "
                f"output={args.storage_accessor_output}"
            )
        if args.ordered_entity_output is not None:
            ordered_entities = match_entities_by_call_order(
                args.source_export,
                args.target_export,
                args.source_interp,
                args.target_interp,
                accessor_matches,
                args.interp_correspondence,
            )
            write_entities(args.ordered_entity_output, ordered_entities)
            ordered_unique = sum(
                match.status == "unique" for match in ordered_entities
            )
            print(
                f"ordered_entities={len(ordered_entities)} "
                f"unique={ordered_unique} "
                f"ambiguous={len(ordered_entities) - ordered_unique} "
                f"output={args.ordered_entity_output}"
            )
    if (
        any(item is not None for item in interp_options)
        and args.entity_output is None
        and not any(item is not None for item in storage_outputs)
        and not any(item is not None for item in structural_outputs)
    ):
        raise CorrespondenceError(
            "interpolation options require --entity-output or --exact-storage-output"
        )
    if (
        args.interp_correspondence is not None
        and args.entity_output is None
        and not any(item is not None for item in storage_outputs)
        and not any(item is not None for item in structural_outputs)
    ):
        raise CorrespondenceError(
            "--interp-correspondence requires interpolation entity output options"
        )


if __name__ == "__main__":
    main()
