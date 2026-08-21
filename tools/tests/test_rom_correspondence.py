import csv
from pathlib import Path
import tempfile

import pytest

from tools import rom_correspondence


def _signature(addr, exact, shape, size=8, instructions=4, mnemonic="c" * 64):
    return rom_correspondence.Signature(
        addr=addr,
        size=size,
        instructions=instructions,
        exact_sha256=exact * 64,
        mnemonic_sha256=mnemonic,
        shape_sha256=shape * 64,
    )


def test_match_functions_prefers_exact_then_unique_shape():
    source = {
        "00001000": _signature("00001000", "a", "1"),
        "00002000": _signature("00002000", "b", "2", size=10),
        "00003000": _signature("00003000", "d", "3"),
    }
    target = {
        "00001100": _signature("00001100", "a", "9"),
        "00002200": _signature("00002200", "c", "2", size=12),
        "00003300": _signature("00003300", "e", "4"),
    }

    matches = rom_correspondence.match_functions(source, target)
    assert [(row.source, row.target, row.kind) for row in matches] == [
        ("00001000", "00001100", "exact-bytes"),
        ("00002000", "00002200", "normalized-shape"),
    ]


def test_nonunique_signatures_are_not_guessed():
    source = {
        "00001000": _signature("00001000", "a", "1"),
        "00002000": _signature("00002000", "a", "1"),
    }
    target = {
        "00001100": _signature("00001100", "a", "1"),
        "00002200": _signature("00002200", "a", "1"),
    }
    assert rom_correspondence.match_functions(source, target) == ()


def test_explain_candidates_keeps_strongest_kind_per_target():
    source = _signature("00001000", "a", "1")
    target = {
        "00001100": _signature("00001100", "a", "1"),
        "00002200": _signature("00002200", "b", "1"),
    }
    assert [
        (kind, row.addr)
        for kind, row in rom_correspondence.explain_candidates(source, target)
    ] == [
        ("exact-bytes", "00001100"),
        ("normalized-shape", "00002200"),
    ]


def test_pair_interp_requires_identical_nonaddress_contract():
    source = [
        dict(zip(rom_correspondence.INTERP_FIELDS, (
            "explicit", "00001000", "00002000", "16", "16", "",
            "uint8", "uint8", "uint8",
        )))
    ]
    target = [dict(source[0], kernel="00003000", wrapper="00004000")]
    assert rom_correspondence.pair_interp(source, target) == (
        (source[0], target[0]),
    )
    target[0]["width"] = "8"
    with pytest.raises(
        rom_correspondence.CorrespondenceError, match="differs outside addresses"
    ):
        rom_correspondence.pair_interp(source, target)


def test_pair_interp_uses_explicit_correspondence_and_allows_target_only_rows():
    source = [
        dict(zip(rom_correspondence.INTERP_FIELDS, (
            "explicit", "00001000", "00002000", "16", "16", "",
            "uint8", "uint8", "uint8",
        )))
    ]
    target = [
        dict(source[0], kernel="00003000", wrapper="00004000"),
        dict(source[0], kernel="00003000", wrapper="00005000"),
    ]
    correspondence = [{
        "source_kernel": "00001000",
        "source_wrapper": "00002000",
        "target_kernel": "00003000",
        "target_wrapper": "00004000",
        "evidence": "reviewed-test-evidence",
    }]
    assert rom_correspondence.pair_interp(
        source, target, correspondence
    ) == ((source[0], target[0]),)


def test_pair_interp_requires_full_source_coverage():
    row = dict(zip(rom_correspondence.INTERP_FIELDS, (
        "explicit", "00001000", "00002000", "16", "16", "",
        "uint8", "uint8", "uint8",
    )))
    source = [row, dict(row, wrapper="00002010")]
    target = [dict(row, kernel="00003000", wrapper="00004000")]
    correspondence = [{
        "source_kernel": "00001000",
        "source_wrapper": "00002000",
        "target_kernel": "00003000",
        "target_wrapper": "00004000",
        "evidence": "reviewed-test-evidence",
    }]
    with pytest.raises(
        rom_correspondence.CorrespondenceError, match="does not cover source entries"
    ):
        rom_correspondence.pair_interp(source, target, correspondence)


def test_signature_reader_rejects_duplicate_addresses():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "function_signatures.csv"
        with path.open("w", newline="", encoding="utf-8") as output:
            writer = csv.DictWriter(output, fieldnames=rom_correspondence.SIGNATURE_FIELDS)
            writer.writeheader()
            row = {
                "addr": "00001000",
                "size": "8",
                "instructions": "4",
                "exact_sha256": "a" * 64,
                "mnemonic_sha256": "b" * 64,
                "shape_sha256": "c" * 64,
            }
            writer.writerow(row)
            writer.writerow(row)
        with pytest.raises(
            rom_correspondence.CorrespondenceError, match="duplicate addr"
        ):
            rom_correspondence.read_signatures(path)
