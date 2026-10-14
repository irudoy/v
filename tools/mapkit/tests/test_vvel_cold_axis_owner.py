"""Bind the live cold-axis owner separately from stock-code execution."""
from __future__ import annotations

import hashlib
from copy import deepcopy

import pytest

from kb import checks, compile, levels, match, repo
from kb.model import SymbolKey
from tools.mapkit.tests.test_vvel_cold_axis_scale import (
    assert_compiled_vvel_cold_axis_owner_contract,
)

OWNER = "kb/axis/vvel_cold_axis.toml"
TEST_PATH = "tools/mapkit/tests/test_vvel_cold_axis_scale.py"
TEST_KEY = "test_vvel_cold_axis_pid05_code_domain"
SPEC_PATH = "defs/VQ37.cold-axis-scale.md"
AXIS_BYTES = bytes.fromhex("0014001e00280032003c00460050005a")


@pytest.fixture(scope="module")
def model():
    return compile.build(repo.ROOT)


def axis_meaning(model):
    return model.symbols[SymbolKey("jk78c", "axis", 0x16AC4)].meaning


def scale_tests(symbol):
    return [item for item in symbol.evidence
            if item.get("kind") == "test" and item.get("supports") == "scale"
            and item.get("path") == TEST_PATH]


def test_live_compiled_owner_preserves_identity_and_editor_contract(model):
    assert_compiled_vvel_cold_axis_owner_contract(model)
    meaning = axis_meaning(model)
    assert OWNER in meaning.sources
    assert meaning.home == "jk78c"
    assert {key: meaning.props[key] for key in (
        "level", "quantity", "points", "storage", "unit", "scale", "to_raw", "scale_level"
    )} == {
        "level": "code", "quantity": "temp", "points": 8, "storage": "uint16",
        "unit": "degC", "scale": "x-50", "to_raw": "x+50", "scale_level": "code",
    }
    assert meaning.props["editor"] == {
        "name": "Coolant Temperature [degC]", "format": "0", "fine": 1, "coarse": 5,
    }
    assert not meaning.statuses
    assert {layout: symbol.address for layout, symbol in meaning.symbols.items()} == {
        "1me3b": 0x17176, "1nd": 0x170D2, "jk78c": 0x16AC4,
    }
    identities = {
        "1me3b": {"kind": "l0", "supports": "identity", "at": "1me3b:00063430"},
        "1nd": {"kind": "l0", "supports": "identity", "at": "1nd:0005f7b0"},
        "jk78c": {"kind": "indirect", "supports": "identity", "at": "jk78c:00056c88",
                  "value": 112, "mode": "base"},
    }
    for layout, symbol in meaning.symbols.items():
        assert [item for item in symbol.evidence
                if item.get("supports", "identity") == "identity"] == [identities[layout]]
        assert match.verify(model, symbol, identities[layout]) is None
        actual = scale_tests(symbol)
        assert len(actual) == 1 and actual[0]["key"] == TEST_KEY
        assert match.verify(model, symbol, actual[0]) is None
        assert any(item.get("kind") == "spec" and item.get("supports") == "scale"
                   and item.get("path") == SPEC_PATH for item in symbol.evidence)
    expected_links = {
        ("reader", "dangerous-cow/fn", "accessor"): [identities["jk78c"]],
        ("reader", "glaring-llama/fn", "accessor"): [identities["1nd"]],
        ("reader", "umber-doberman/fn", "accessor"): [identities["1me3b"]],
    }
    assert {(link.type, link.to.key, next(iter(link.roles)) if len(link.roles) == 1 else None): link.evidence
            for link in meaning.links if OWNER in link.sources} == expected_links
    subjects = {symbol.key.key for symbol in meaning.symbols.values()}
    assert not [issue for issue in checks.homology(model, subjects=subjects) if issue.subject in subjects]
    assert not [issue for issue in levels.check(model)
                if issue.subject == meaning.key and "scale" in issue.message]


@pytest.mark.parametrize("layout", ("1me3b", "1nd", "jk78c"))
def test_spec_evidence_cannot_replace_the_named_executable_item(model, layout):
    meaning = axis_meaning(model)
    symbol = meaning.symbols[layout]
    original = symbol.evidence
    try:
        actual = scale_tests(symbol)
        assert len(actual) == 1
        symbol.evidence = [item for item in original if item not in actual]
        assert any(item.get("kind") == "spec" and item.get("supports") == "scale"
                   and item.get("path") == SPEC_PATH for item in symbol.evidence)
        assert match.verify(model, symbol, original[0]) is None
        with pytest.raises(AssertionError):
            assert_compiled_vvel_cold_axis_owner_contract(model)
    finally:
        symbol.evidence = original
    assert_compiled_vvel_cold_axis_owner_contract(model)


@pytest.mark.parametrize("layout", ("1me3b", "1nd", "jk78c"))
def test_missing_top_level_scale_key_is_rejected(model, layout):
    symbol = axis_meaning(model).symbols[layout]
    original = symbol.evidence
    try:
        actual = scale_tests(symbol)
        assert len(actual) == 1
        missing = {**actual[0], "key": "test_missing_vvel_cold_axis_scale"}
        assert "defines no function" in match.verify(model, symbol, missing)
        symbol.evidence = [missing if item == actual[0] else item for item in original]
        assert any("test_missing_vvel_cold_axis_scale" in issue.message
                   for issue in checks.homology(model, subjects={symbol.key.key})
                   if issue.subject == symbol.key.key)
        with pytest.raises(AssertionError):
            assert_compiled_vvel_cold_axis_owner_contract(model)
    finally:
        symbol.evidence = original
    assert_compiled_vvel_cold_axis_owner_contract(model)


@pytest.mark.parametrize("image_index", (0, 1))
@pytest.mark.parametrize("token", (
    "nominal encoded-temperature", "T>=10", "x=T", "corresponding samples",
    "not a sensor inverse", "no hardware proof",
))
def test_each_1nd_image_note_requires_its_own_boundaries(model, image_index, token):
    symbol = axis_meaning(model).symbols["1nd"]
    original = symbol.props["note"]
    try:
        assert len(original) == 2 and all(token in note for note in original)
        changed = original.copy()
        changed[image_index] = changed[image_index].replace(token, "", 1)
        assert changed[1 - image_index] == original[1 - image_index]
        symbol.props["note"] = changed
        with pytest.raises(AssertionError, match="qualified nominal owner note"):
            assert_compiled_vvel_cold_axis_owner_contract(model)
    finally:
        symbol.props["note"] = original
    assert_compiled_vvel_cold_axis_owner_contract(model)


@pytest.mark.parametrize("image_index", (0, 1))
def test_1nd_image_note_labels_are_required(model, image_index):
    symbol = axis_meaning(model).symbols["1nd"]
    original = symbol.props["note"]
    try:
        changed = original.copy()
        changed[image_index] = changed[image_index].split(":", 1)[1]
        symbol.props["note"] = changed
        with pytest.raises(AssertionError, match="separate image-labelled owner notes"):
            assert_compiled_vvel_cold_axis_owner_contract(model)
    finally:
        symbol.props["note"] = original
    assert_compiled_vvel_cold_axis_owner_contract(model)


def test_identity_and_byte_homology_do_not_ground_the_scale(model):
    meaning = axis_meaning(model)
    home = meaning.symbols[meaning.home]
    originals = {layout: symbol.evidence for layout, symbol in meaning.symbols.items()}
    props = deepcopy(meaning.props)
    tables = deepcopy(meaning.tables)
    try:
        for symbol in meaning.symbols.values():
            symbol.evidence = [item for item in symbol.evidence if item.get("supports") != "scale"]
            if symbol is not home:
                item = {
                    "kind": "byte-identical", "supports": "homology",
                    "at": symbol.key.location, "to": home.key.location,
                    "sha256": hashlib.sha256(AXIS_BYTES).hexdigest(),
                }
                assert match.verify(model, symbol, item) is None
                symbol.evidence.append(item)
        assert all(rank >= levels.CODE for rank, _ in match.grounded(
            model, [symbol.key for symbol in meaning.symbols.values()]).values())
        assert any(issue.subject == meaning.key and "scale level code lacks grounding" in issue.message
                   for issue in levels.check(model))
        with pytest.raises(AssertionError):
            assert_compiled_vvel_cold_axis_owner_contract(model)
        assert meaning.props == props and meaning.tables == tables
    finally:
        for layout, symbol in meaning.symbols.items():
            symbol.evidence = originals[layout]
    assert_compiled_vvel_cold_axis_owner_contract(model)
