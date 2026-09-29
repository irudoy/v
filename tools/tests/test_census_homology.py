import copy

import pytest

from tools import census_homology


def _images(source_cells, target_cells, size=0x9000):
    images = []
    for cells in (source_cells, target_cells):
        image = bytearray(size)
        for address, data in cells.items():
            image[address : address + len(data)] = data
        images.append(bytes(image))
    return tuple(images)


def test_geometry_size_follows_the_largest_reading():
    assert census_homology.geometry_bytes("16x16:uint8") == 256
    assert census_homology.geometry_bytes("8x1:uint16") == 16
    assert census_homology.geometry_bytes("8x1:uint8|16x1:uint16") == 32
    assert census_homology.geometry_bytes("16:uint16") == 32
    with pytest.raises(census_homology.CensusHomologyError, match="invalid geometry"):
        census_homology.geometry_bytes("16x16:float")


def test_implicit_element_type_follows_the_axis_limit():
    entry = {"family": "implicit", "width": "16", "height": "", "step": "16"}
    assert census_homology._map_geometry(entry) == "16x1:uint8:step16"
    entry["step"] = "4096"
    assert census_homology._map_geometry(entry) == "16x1:uint16:step4096"


def test_best_function_prefers_the_exact_pair_and_skips_reserved_targets():
    source_tokens = {"a": ("x", "y", "z", "w"), "b": ("x", "y", "z", "q")}
    target_tokens = {
        "t1": ("x", "y", "z", "w"),
        "t2": ("x", "y", "z", "q"),
        "t3": ("p", "p", "p", "p"),
    }
    exact = {"a": "t1"}
    assert census_homology.best_function(
        "a", source_tokens, target_tokens, exact, {"t1"}
    ) == (1.0, "t1")
    assert census_homology.best_function(
        "b", source_tokens, target_tokens, exact, {"t1"}
    ) == (1.0, "t2")
    assert (
        census_homology.best_function(
            "b", source_tokens, {"t3": target_tokens["t3"]}, exact, set()
        )
        is None
    )


def test_aligned_ordinals_skip_inserted_instructions():
    ordinals = census_homology.aligned_ordinals(
        ("a", "b", "c", "d"), ("a", "n", "b", "c", "d")
    )
    assert ordinals == {0: 0, 1: 2, 2: 3, 3: 4}


def test_build_ledger_classifies_every_target_entity():
    geometry = ("map", "4x1:uint8")
    source_entities = {
        0x8100: geometry,
        0x8110: geometry,
        0x8120: geometry,
        0x8130: geometry,
        0x8140: geometry,
    }
    target_entities = {
        0x8200: geometry,
        0x8210: geometry,
        0x8220: geometry,
        0x8230: geometry,
        0x8240: geometry,
        0x8250: geometry,
        0x8260: geometry,
    }
    images = _images(
        {
            0x8100: bytes((1, 2, 3, 4)),
            0x8110: bytes((5, 6, 7, 8)),
            0x8120: bytes((9, 9, 8, 8)),
            0x8130: bytes((9, 9, 8, 8)),
            0x8140: bytes((4, 4, 4, 5)),
        },
        {
            0x8200: bytes((1, 2, 3, 9)),
            0x8210: bytes((5, 6, 7, 8)),
            0x8220: bytes((7, 7, 7, 7)),
            0x8230: bytes((9, 9, 8, 8)),
            0x8240: bytes((3, 1, 4, 1)),
            0x8250: bytes((2, 7, 1, 8)),
            0x8260: bytes((1, 6, 1, 8)),
        },
    )
    votes = {
        0x8100: {0x8200: 3},
        0x8140: {0x8250: 1, 0x8260: 1},
    }
    rows = census_homology.build_ledger(
        source_entities,
        target_entities,
        {key: census_homology.Counter(value) for key, value in votes.items()},
        {0x8240: 0x8100},
        images,
    )
    by_target = {row["target"]: row for row in rows}

    assert by_target["00008200"]["method"] == "aligned-reference"
    assert by_target["00008200"]["bytes_equal"] == "no"
    assert by_target["00008210"]["method"] == "unique-exact-content"
    assert by_target["00008210"]["source"] == "00008110"
    assert by_target["00008220"]["note"] == "flat-content"
    assert by_target["00008230"]["note"] == "duplicate-content"
    # A published pair may reuse the source of an aligned pair.
    assert by_target["00008240"]["method"] == "published-registry"
    assert by_target["00008240"]["source"] == "00008100"
    assert by_target["00008250"]["status"] == "ambiguous"
    assert by_target["00008260"]["note"] == "00008140"
    census_homology.validate_ledger(rows, "1ND0A", "1ME3B", images)


def test_published_pair_contradicting_a_census_pair_is_rejected():
    geometry = ("map", "4x1:uint8")
    images = _images({0x8100: bytes((1, 2, 3, 4))}, {0x8200: bytes((1, 2, 3, 4))})
    with pytest.raises(
        census_homology.CensusHomologyError, match="contradicts the published pair"
    ):
        census_homology.build_ledger(
            {0x8100: geometry, 0x8110: geometry},
            {0x8200: geometry},
            {0x8100: census_homology.Counter({0x8200: 1})},
            {0x8200: 0x8110},
            images,
        )


@pytest.fixture(scope="module")
def ledger():
    return census_homology.read_ledger(
        census_homology.ledger_path("1ND0A", "1ME3B")
    )


def test_1me3b_census_ledger_matches_the_stock_images(ledger):
    summary = census_homology.validate_ledger(ledger, "1ND0A", "1ME3B")

    assert summary["map"] == {
        "total": 768,
        "homolog": 589,
        "ambiguous": 5,
        "unpaired": 174,
        "aligned-reference": 500,
        "unique-exact-content": 82,
        "published-registry": 7,
        "bytes_equal": 558,
    }
    assert summary["axis"] == {
        "total": 432,
        "homolog": 357,
        "ambiguous": 2,
        "unpaired": 73,
        "aligned-reference": 310,
        "unique-exact-content": 40,
        "published-registry": 7,
        "bytes_equal": 346,
    }


def test_1me3b_census_ledger_carries_every_published_census_pair(ledger):
    by_target = {int(row["target"], 16): row for row in ledger}
    published = census_homology.published_pairs("1ND0A", "1ME3B")
    checked = 0
    for target, source in published.items():
        row = by_target.get(target)
        if row is None or row["status"] != "homolog":
            continue
        assert int(row["source"], 16) == source
        checked += 1
    assert checked >= 60

    # The resolver and the dispatcher of 1ME3B read separate copies of the one
    # hot-idle surface that both 1ND0A readers share.
    assert by_target[0x0000E17C]["source"] == "0000e748"
    assert by_target[0x0001027C]["source"] == "0000e748"
    assert by_target[0x0000E17C]["method"] == "published-registry"
    assert by_target[0x0001027C]["method"] == "aligned-reference"


def test_census_ledger_mutations_are_rejected(ledger):
    flipped = copy.deepcopy(ledger)
    row = next(item for item in flipped if item["bytes_equal"] == "yes")
    row["bytes_equal"] = "no"
    with pytest.raises(census_homology.CensusHomologyError, match="bytes_equal differs"):
        census_homology.validate_ledger(flipped, "1ND0A", "1ME3B")

    repeated = copy.deepcopy(ledger)
    automatic = [
        item
        for item in repeated
        if item["method"] == "aligned-reference" and item["bytes_equal"] == "yes"
    ]
    automatic[1]["source"] = automatic[0]["source"]
    with pytest.raises(
        census_homology.CensusHomologyError,
        match="pair one source with two targets",
    ):
        census_homology.validate_ledger(repeated, "1ND0A", "1ME3B")

    # The published mode-selected ignition pair is 0xA344 <- 0xA410.
    contradicted = copy.deepcopy(ledger)
    row = next(item for item in contradicted if item["target"] == "0000a344")
    assert row["source"] == "0000a410"
    row.update(source="0000a510", method="published-registry", bytes_equal="no")
    with pytest.raises(
        census_homology.CensusHomologyError,
        match="contradicts the published source 0000a410",
    ):
        census_homology.validate_ledger(contradicted, "1ND0A", "1ME3B")


def test_check_requires_the_ledger_that_l0_produces(tmp_path, capsys):
    tracked = census_homology.ledger_path("1ND0A", "1ME3B")
    ledger = tmp_path / tracked.name
    ledger.write_text(tracked.read_text(encoding="utf-8"), encoding="utf-8")
    assert census_homology.main(["--check", "--output", str(ledger)]) == 0
    lines = ledger.read_text(encoding="utf-8").splitlines(keepends=True)
    row = next(index for index, line in enumerate(lines) if ",homolog," in line)
    del lines[row]
    ledger.write_text("".join(lines), encoding="utf-8")
    assert census_homology.main(["--check", "--output", str(ledger)]) == 1
    assert "produce" in capsys.readouterr().err
