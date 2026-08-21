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


def test_pair_interp_accepts_explicit_unsupported_source_entry():
    row = dict(zip(rom_correspondence.INTERP_FIELDS, (
        "explicit", "00001000", "00002000", "16", "16", "",
        "uint8", "uint8", "uint8",
    )))
    source = [row, dict(row, wrapper="00002010")]
    target = [dict(row, kernel="00003000", wrapper="00004000")]
    correspondence = [
        {
            "source_kernel": "00001000",
            "source_wrapper": "00002000",
            "target_kernel": "00003000",
            "target_wrapper": "00004000",
            "status": "mapped",
            "evidence": "reviewed-test-evidence",
        },
        {
            "source_kernel": "00001000",
            "source_wrapper": "00002010",
            "target_kernel": "",
            "target_wrapper": "",
            "status": "unsupported",
            "evidence": "complete-target-census",
        },
    ]

    assert rom_correspondence.pair_interp(
        source, target, correspondence
    ) == ((source[0], target[0]),)


def test_read_interp_correspondence_rejects_target_on_unsupported_row(tmp_path):
    path = tmp_path / "interp-correspondence.csv"
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(
            output,
            fieldnames=rom_correspondence.INTERP_CORRESPONDENCE_STATUS_FIELDS,
        )
        writer.writeheader()
        writer.writerow({
            "source_kernel": "00001000",
            "source_wrapper": "00002000",
            "target_kernel": "00003000",
            "target_wrapper": "00004000",
            "status": "unsupported",
            "evidence": "complete-target-census",
        })

    with pytest.raises(
        rom_correspondence.CorrespondenceError,
        match="unsupported source entry must not name a target",
    ):
        rom_correspondence.read_interp_correspondence(path)


def test_tracked_1nd_interp_correspondence_is_complete():
    root = Path(__file__).parents[2]
    source = rom_correspondence.read_interp(root / "defs" / "JK08A.interp.csv")
    target = rom_correspondence.read_interp(root / "defs" / "1ND0A.interp.csv")
    correspondence = rom_correspondence.read_interp_correspondence(
        root / "defs" / "JK08A-1ND0A.interp-correspondence.csv"
    )

    assert len(source) == 34
    assert len(target) == 36
    assert len(rom_correspondence.pair_interp(
        source, target, correspondence
    )) == 33
    mapped_targets = {
        (row["target_kernel"], row["target_wrapper"])
        for row in correspondence
        if row["status"] == "mapped"
    }
    assert len({
        (row["kernel"], row["wrapper"])
        for row in target
    } - mapped_targets) == 3
    assert [
        (row["source_kernel"], row["source_wrapper"])
        for row in correspondence
        if row["status"] == "unsupported"
    ] == [("00026944", "000261b8")]


def test_exact_storage_matches_only_unique_contract_operands(tmp_path):
    source_export = tmp_path / "source"
    target_export = tmp_path / "target"
    source_export.mkdir()
    target_export.mkdir()
    source_interp = tmp_path / "source.interp.csv"
    target_interp = tmp_path / "target.interp.csv"
    interp_row = {
        "family": "explicit",
        "kernel": "00001000",
        "wrapper": "00002000",
        "width": "2",
        "height": "2",
        "step": "",
        "storagetype": "uint8",
        "axistype_x": "uint8",
        "axistype_y": "uint8",
    }
    for path, row in (
        (source_interp, interp_row),
        (target_interp, dict(
            interp_row,
            kernel="00003000",
            wrapper="00004000",
        )),
    ):
        with path.open("w", newline="", encoding="utf-8") as output:
            writer = csv.DictWriter(
                output,
                fieldnames=rom_correspondence.INTERP_FIELDS,
            )
            writer.writeheader()
            writer.writerow(row)

    census_fields = (
        "kernel", "wrapper", "accessor", "callsite",
        "df_r4", "df_r5", "df_r6", "branch",
    )
    census_rows = (
        (
            source_export / "accessors.1000.csv",
            {
                "kernel": "00001000",
                "wrapper": "00002000",
                "accessor": "00005000",
                "callsite": "00005010",
                "df_r4": "00001100",
                "df_r5": "00001200",
                "df_r6": "00001210",
                "branch": "",
            },
        ),
        (
            target_export / "accessors.3000.csv",
            {
                "kernel": "00003000",
                "wrapper": "00004000",
                "accessor": "00006000",
                "callsite": "00006010",
                "df_r4": "00002100",
                "df_r5": "00002200",
                "df_r6": "00002210",
                "branch": "",
            },
        ),
    )
    for path, row in census_rows:
        with path.open("w", newline="", encoding="utf-8") as output:
            writer = csv.DictWriter(output, fieldnames=census_fields)
            writer.writeheader()
            writer.writerow(row)

    source_bytes = bytearray(0x3000)
    target_bytes = bytearray(0x3000)
    source_bytes[0x1100:0x1104] = b"map!"
    target_bytes[0x2100:0x2104] = b"map!"
    source_bytes[0x1200:0x1202] = b"x!"
    target_bytes[0x2200:0x2202] = b"x!"
    source_bytes[0x1210:0x1212] = b"y!"
    target_bytes[0x2210:0x2212] = b"y!"
    source_image = tmp_path / "source.bin"
    target_image = tmp_path / "target.bin"
    source_image.write_bytes(source_bytes)
    target_image.write_bytes(target_bytes)

    matches = rom_correspondence.match_exact_storage(
        source_export,
        target_export,
        source_interp,
        target_interp,
        source_image,
        target_image,
    )
    assert [
        (row.entity, row.source, row.target, row.status, row.bytes)
        for row in matches
    ] == [
        ("Axis", "00001200", "00002200", "unique", 2),
        ("Axis", "00001210", "00002210", "unique", 2),
        ("Map", "00001100", "00002100", "unique", 4),
    ]

    accessors = rom_correspondence.match_storage_accessors(
        source_export,
        target_export,
        source_interp,
        target_interp,
        matches,
    )
    assert [
        (row.source, row.target, row.status, row.anchors, row.contracts)
        for row in accessors
    ] == [("00005000", "00006000", "unique", 1, 1)]

    ordered = rom_correspondence.match_entities_by_call_order(
        source_export,
        target_export,
        source_interp,
        target_interp,
        accessors,
    )
    assert [
        (row.entity, row.source, row.target, row.status, row.sites)
        for row in ordered
    ] == [
        ("Axis", "00001200", "00002200", "unique", 1),
        ("Axis", "00001210", "00002210", "unique", 1),
        ("Map", "00001100", "00002100", "unique", 1),
    ]


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


def test_reference_matching_uses_function_and_instruction_ordinal(tmp_path):
    source_export = tmp_path / "source"
    target_export = tmp_path / "target"
    source_export.mkdir()
    target_export.mkdir()
    fields = rom_correspondence.REFERENCE_FIELDS
    source_row = {
        "func_addr": "00001000",
        "ins_addr": "00001004",
        "ordinal": "2",
        "mnemonic": "mov.l",
        "ref_addr": "00001020",
        "width": "4",
        "value_hex": "00002000",
        "ref_type": "read",
    }
    target_row = {
        "func_addr": "00003000",
        "ins_addr": "00003008",
        "ordinal": "2",
        "mnemonic": "mov.l",
        "ref_addr": "00003024",
        "width": "4",
        "value_hex": "00004000",
        "ref_type": "read",
    }
    for directory, row in (
        (source_export, source_row),
        (target_export, target_row),
    ):
        with (directory / "function_references.csv").open(
            "w", newline="", encoding="utf-8"
        ) as output:
            writer = csv.DictWriter(output, fieldnames=fields)
            writer.writeheader()
            writer.writerow(row)
    function_match = rom_correspondence.FunctionMatch(
        source="00001000",
        target="00003000",
        kind="normalized-shape",
        source_size=8,
        target_size=10,
        instructions=4,
        signature_sha256="a" * 64,
    )

    matches = rom_correspondence.match_references(
        source_export, target_export, (function_match,)
    )
    assert len(matches) == 1
    assert matches[0].source_ref == "00001020"
    assert matches[0].target_ref == "00003024"
    assert matches[0].source_value == "00002000"
    assert matches[0].target_value == "00004000"


def test_reference_matching_accepts_direct_ram_targets(tmp_path):
    source_export = tmp_path / "source"
    target_export = tmp_path / "target"
    source_export.mkdir()
    target_export.mkdir()
    rows = (
        {
            "func_addr": "00001000",
            "ins_addr": "00001004",
            "ordinal": "2",
            "mnemonic": "mov.b",
            "ref_addr": "ffff1234",
            "width": "0",
            "value_hex": "",
            "ref_type": "read",
        },
        {
            "func_addr": "00003000",
            "ins_addr": "00003008",
            "ordinal": "2",
            "mnemonic": "mov.b",
            "ref_addr": "ffff5678",
            "width": "0",
            "value_hex": "",
            "ref_type": "read",
        },
    )
    for directory, row in zip((source_export, target_export), rows):
        with (directory / "function_references.csv").open(
            "w", newline="", encoding="utf-8"
        ) as output:
            writer = csv.DictWriter(
                output, fieldnames=rom_correspondence.REFERENCE_FIELDS
            )
            writer.writeheader()
            writer.writerow(row)
    function_match = rom_correspondence.FunctionMatch(
        source="00001000",
        target="00003000",
        kind="exact-bytes",
        source_size=8,
        target_size=8,
        instructions=4,
        signature_sha256="b" * 64,
    )

    matches = rom_correspondence.match_references(
        source_export, target_export, (function_match,)
    )
    assert len(matches) == 1
    assert matches[0].source_ref == "ffff1234"
    assert matches[0].target_ref == "ffff5678"
    assert matches[0].width == 0
