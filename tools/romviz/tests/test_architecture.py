"""Contract of the firmware architecture model, its gate, and its atlas binding."""

import json
import re

import pytest

from tools.romviz import architecture
from tools.romviz import build
from tools.romviz import model


SOURCE = architecture.DEFAULT_SOURCE

# One durable direction per chain family: the sign that an increase of the
# table has on the published output of the chain.
IMPACT_CLAIMS = (
    ("ignition-advance", "0000991a", "positive"),
    ("knock-retard", "00009b1a", "negative"),
    ("fuel-pulse", "0000a9aa", "positive"),
    ("intake-cvtc", "0000b43a", "positive"),
    ("idle-air", "0001465a", "positive"),
    ("electronic-throttle", "00013202", "negative"),
    # The same surface converts the pedal into a torque request and converts
    # requests back into an opening area, so its two paths disagree.
    ("electronic-throttle", "0000e98e", "mixed"),
)

# ROM: architecture mode, relocated tables and axes, unsupported tables and axes.
ROM_BINDINGS = {
    "1ME3B": ("reference", 40, 18),
    "1ND0A": ("reference", 40, 18),
    "1ND3B": ("reference", 40, 18),
    "JK00A": ("exact", 0, 0),
    "JK00C": ("projected", 283, 2),
    "JK00D": ("projected", 284, 2),
    "JK03A": ("exact", 0, 0),
    "JK03B": ("exact", 0, 0),
    "JK08A": ("exact", 0, 0),
    "JK78C": ("reference", 45, 16),
}


@pytest.fixture(scope="module")
def tracked():
    return architecture.load()


@pytest.fixture(scope="module")
def atlas():
    return model.build_atlas(["all"])


def _source_text():
    return SOURCE.read_text(encoding="utf-8")


def _rewritten(tmp_path, text):
    target = tmp_path / SOURCE.name
    target.write_text(text, encoding="utf-8")
    return architecture.Architecture(target)


def _singly_named_function(tracked, text):
    """Return a placed function whose address appears once in the source."""
    for block in tracked.blocks:
        for node_id in block.functions:
            addr = tracked.nodes[node_id].addr
            if text.count(f'"{addr}"') == 1:
                return addr
    raise AssertionError("every placed function is named more than once")


def _node_id(tracked, addr, kinds=("map", "axis")):
    return next(
        node.id
        for node in tracked.nodes.values()
        if node.addr == addr and node.kind in kinds
    )


def test_tracked_source_passes_the_gate(tracked):
    assert tracked.errors == []
    assert tracked.rom == "JK08A"
    assert tracked.stages and tracked.blocks and tracked.endpoints and tracked.chains
    for chain in tracked.chains:
        nodes = {node for step in chain.steps for node in (step.source, step.target)}
        assert chain.output in nodes
    supports = [step.support for chain in tracked.chains for step in chain.steps]
    assert set(supports) == {"ledger", "specification"}
    assert supports.count("ledger") > supports.count("specification") > 0


def test_every_reviewed_function_is_placed_once(tracked):
    placed = [node_id for block in tracked.blocks for node_id in block.functions]
    reviewed = {
        node.id for node in tracked.nodes.values() if node.kind == "function"
    }
    assert len(placed) == len(set(placed))
    assert set(placed) == reviewed


def test_a_function_without_a_block_fails_the_gate(tmp_path, tracked):
    text = _source_text()
    addr = _singly_named_function(tracked, text)
    broken = _rewritten(tmp_path, text.replace(f'"{addr}",', "", 1))
    assert any(f"reviewed function {addr} has no block" in item for item in broken.errors)
    assert any("suggest" in item for item in broken.errors)


def test_an_address_outside_the_ledgers_fails_the_gate(tmp_path, tracked):
    text = _source_text()
    addr = _singly_named_function(tracked, text)
    broken = _rewritten(tmp_path, text.replace(f'"{addr}"', '"0000dead"', 1))
    assert any("0000dead is not a reviewed" in item for item in broken.errors)


def test_specification_support_is_load_bearing(tmp_path, tracked):
    """Every step that no ledger relation covers names a specification."""
    text = _source_text()
    stripped = re.sub(r"(?m)^specs = \[[^\]]*\]\n", "", text)
    assert stripped != text
    broken = _rewritten(tmp_path, stripped)
    unsupported = [item for item in broken.errors if "has no ledger relation" in item]
    declared = [
        step
        for chain in tracked.chains
        for step in chain.steps
        if step.support == "specification"
    ]
    assert len(unsupported) == len(declared) > 0
    assert broken.errors == unsupported


def test_a_step_cycle_fails_the_gate(tmp_path, tracked):
    # An appended step table belongs to the last chain of the source.
    chain = tracked.chains[-1]
    step = chain.steps[0]
    reversed_step = (
        "\n[[chain.step]]\n"
        f'from = "{tracked.nodes[step.target].addr}"\n'
        f'to = "{tracked.nodes[step.source].addr}"\n'
        f'effect = "{step.effect}"\n'
        'sign = "none"\n'
        f'via = ["{tracked.nodes[step.via[0]].addr}"]\n'
    )
    broken = _rewritten(tmp_path, _source_text() + reversed_step)
    assert any("steps form a cycle" in item for item in broken.errors)


def test_sign_composition():
    assert architecture.combine_sign("positive", "positive") == "positive"
    assert architecture.combine_sign("negative", "negative") == "positive"
    assert architecture.combine_sign("positive", "negative") == "negative"
    assert architecture.combine_sign("none", "positive") == "none"
    assert architecture.merge_signs(["positive", "positive"]) == "positive"
    assert architecture.merge_signs(["positive", "negative"]) == "mixed"
    assert architecture.merge_signs(["positive", "none"]) == "mixed"
    assert architecture.merge_signs([]) is None


@pytest.mark.parametrize("chain_id, addr, sign", IMPACT_CLAIMS)
def test_chain_impact_states_the_direction(tracked, chain_id, addr, sign):
    chain = next(item for item in tracked.chains if item.id == chain_id)
    impact = chain.impact[_node_id(tracked, addr)]
    assert impact["sign"] == sign
    steps = [chain.steps[index] for index in impact["steps"]]
    assert steps and all(step.effect in architecture.EFFECTS for step in steps)


def test_the_output_carries_no_impact_of_its_own(tracked):
    for chain in tracked.chains:
        assert chain.output not in chain.impact


def test_atlas_ships_the_gated_architecture(atlas, tracked):
    assert list(atlas["architectures"]) == ["JK08A"]
    assert atlas["architectures"]["JK08A"] == tracked.export()
    assert "architecture JK08A=" in build.summary(atlas)
    document = build.render(atlas)
    assert '"architectures"' in document
    assert "arch-canvas" in document


def test_every_rom_binds_the_architecture(atlas, tracked):
    bindings = {rom["id"]: rom["architecture"] for rom in atlas["roms"]}
    assert set(bindings) == set(ROM_BINDINGS)
    for rom, (mode, relocated, unsupported) in ROM_BINDINGS.items():
        binding = bindings[rom]
        assert binding["source"] == tracked.rom
        assert binding["mode"] == mode
        assert len(binding["relocation"]) == relocated
        assert len(binding["unsupported"]) == unsupported
        assert bool(binding["note"]) is (mode != "exact")
        for node_id in list(binding["relocation"]) + binding["unsupported"]:
            assert tracked.nodes[node_id].kind in ("map", "axis", "rom")


def test_manifest_architecture_table_is_validated():
    valid = {
        "source": "defs/JK08A.architecture.toml",
        "mode": "projected",
        "note": "Near-code relative.",
    }
    model._check_architecture_table("manifest.toml", valid)
    for table, message in (
        ([], "must be a table"),
        ({"mode": "exact"}, "fields differ"),
        ({**valid, "extra": 1}, "fields differ"),
        ({**valid, "source": " "}, "must name a tracked file"),
        ({**valid, "mode": "guess"}, "must be one of"),
        ({"source": valid["source"], "mode": "reference"}, "requires a note"),
        ({**valid, "note": ""}, "nonempty string"),
    ):
        with pytest.raises(model.ModelError, match=message):
            model._check_architecture_table("manifest.toml", table)


def test_exact_mode_requires_the_reviewed_function_ledger(tmp_path):
    manifest = model.ROOT / "tools" / "romviz" / "roms" / "JK00A.toml"
    text = manifest.read_text(encoding="utf-8")
    broken = tmp_path / manifest.name
    broken.write_text(
        text.replace('reviewed_functions = "defs/JK08A.funcs.csv"\n', ""),
        encoding="utf-8",
    )
    with pytest.raises(model.ModelError, match="exact mode requires reviewed_functions"):
        model.build_rom_model(broken)


def test_a_relocated_rom_cannot_claim_exact_mode(tmp_path):
    manifest = model.ROOT / "tools" / "romviz" / "roms" / "JK78C.toml"
    text = manifest.read_text(encoding="utf-8")
    broken = tmp_path / manifest.name
    broken.write_text(text.replace('mode = "reference"', 'mode = "exact"'), encoding="utf-8")
    with pytest.raises(model.ModelError, match="cannot use exact mode"):
        model.build_rom_model(broken)


def test_command_line_reports_the_model(capsys):
    assert architecture.main(["check"]) == 0
    printed = capsys.readouterr().out
    assert "architecture JK08A" in printed
    assert "functions placed" in printed
    assert "chain steps" in printed


def test_command_line_states_the_effect_of_a_table(capsys):
    assert architecture.main(["impact", "0x991a"]) == 0
    printed = capsys.readouterr().out
    assert "chain ignition-advance" in printed
    assert "positive" in printed


def test_command_line_walks_a_relation_path(capsys):
    assert architecture.main(["path", "0003de4c", "ffff1702"]) == 0
    printed = capsys.readouterr().out
    assert "-data/writes-> signal ffff1702" in printed


def test_command_line_ranks_blocks_for_a_function(capsys):
    assert architecture.main(["suggest", "0003de4c"]) == 0
    printed = capsys.readouterr().out
    assert "engine-speed" in printed


def test_command_line_exports_the_model(tmp_path, capsys):
    target = tmp_path / "architecture.json"
    assert architecture.main(["json", "--output", str(target)]) == 0
    exported = json.loads(target.read_text(encoding="utf-8"))
    assert exported["id"] == "JK08A"
    assert exported["blocks"] and exported["chains"] and exported["nodes"]
