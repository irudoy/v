"""Contract of the firmware architecture model, its gate, and its atlas binding."""

import csv
import io
import json
import re

import pytest

from tools.romviz import architecture
from tools.romviz import build
from tools.romviz import model
from tools.romviz import graph_atlas
from kb.repo import KbError


SOURCE = architecture.DEFAULT_SOURCE
FINDINGS = architecture.ROOT / "defs" / "JK08A.findings.csv"
# An address that no ledger names.
FREE_MAP = "0001fff0"

# Declared table-to-output impact signs for the chain families.
IMPACT_CLAIMS = (
    ("ignition-advance", "0000991a", "positive"),
    ("knock-retard", "00009b1a", "negative"),
    ("fuel-pulse", "0000a9aa", "none"),
    ("intake-cvtc", "0000b43a", "positive"),
    ("idle-air", "0001465a", "positive"),
    ("electronic-throttle", "00013202", "negative"),
    # The same surface converts the pedal into a torque request and converts
    # requests back into an opening area, so its two paths disagree.
    ("electronic-throttle", "0000e98e", "mixed"),
)

# ROM: architecture mode, relocated tables and axes, unsupported tables and axes.
ROM_BINDINGS = {
    'JK08A': '7mfk', 'JK00A': '7mfk', 'JK03A': '7mfk', 'JK03B': '7mfk',
    'JK00C': 'jk00c', 'JK00D': 'jk00d', 'JK78C': 'jk78c',
    '1ND0A': '1nd', '1ND3B': '1nd', '1ME3B': '1me3b',
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


def _with_map(tmp_path, confidence, role, text=None):
    """Load the source over a findings ledger with a map that no code reads."""
    ledger = FINDINGS.read_text(encoding="utf-8")
    fields = next(csv.reader(io.StringIO(ledger)))
    row = io.StringIO()
    csv.DictWriter(row, fieldnames=fields, lineterminator="\n").writerow({
        **dict.fromkeys(fields, ""),
        "addr": FREE_MAP,
        "confidence": confidence,
        "role": role,
        "semantics": "Calibration without a reader.",
    })
    findings = tmp_path / FINDINGS.name
    findings.write_text(ledger + row.getvalue(), encoding="utf-8")
    text = text or _source_text()
    source = text.replace(
        'findings = "defs/JK08A.findings.csv"', f'findings = "{findings}"', 1
    )
    assert source != text
    return _rewritten(tmp_path, source)


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


def test_native_placed_maf_states_without_legacy_rows_are_reviewed(tracked):
    addresses = ("ffff1e00", "ffff1e02", "ffff1e08", "ffff1e0a", "ffff1e10",
                 "ffff1e14", "ffff1e18", "ffff1e1a", "ffff1e1c", "ffff1e1e",
                 "ffff1e30", "ffff1e32", "ffff1e34", "ffff43ca", "ffff43cb")
    for address in addresses:
        assert address not in tracked.ledgers.variables
        node = tracked.nodes["signal:" + address]
        assert node.reviewed and node.block == "airflow-load"
        assert node.meta["origin"] == "kb" and node.meta["layout"] == "7mfk"
        assert node.source.startswith("kb/ram/") and node.confidence == "code"


def test_native_placement_does_not_admit_an_unowned_signal(tmp_path):
    text = _source_text().replace('"ffff1e00"', '"ffffdead"', 1)
    broken = _rewritten(tmp_path, text)
    assert any("ffffdead is not a reviewed" in item for item in broken.errors)


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


@pytest.mark.parametrize(
    ("confidence", "role", "fails"),
    (
        ("code", "table", True),
        ("code", "threshold", True),
        ("code", "dead", False),
        ("candidate", "table", False),
    ),
)
def test_a_code_confidence_map_without_a_block_fails_the_gate(
    tmp_path, tracked, confidence, role, fails
):
    assert tracked.lookup(FREE_MAP) == []
    extended = _with_map(tmp_path, confidence, role)
    assert extended.nodes[f"map:{FREE_MAP}"].block is None
    unattributed = [
        item for item in extended.errors if f"map {FREE_MAP} has no block" in item
    ]
    assert len(unattributed) == int(fails)
    assert any("pin the map" in item for item in extended.errors) is fails
    assert len(extended.errors) == 2 * int(fails)


def test_a_pinned_map_passes_the_gate(tmp_path, tracked):
    existing_maps = set(tracked.block("crank-cam").maps)
    assert f"map:{FREE_MAP}" not in existing_maps
    text = _source_text()
    start = text.index('id = "crank-cam"\n')
    stop = text.index('[[block]]', start + 1)
    pinned = (text[:start] + text[start:stop].replace(
        'maps = [', f'maps = ["{FREE_MAP}", ', 1) + text[stop:])
    assert pinned != text
    extended = _with_map(tmp_path, "code", "table", pinned)
    assert extended.errors == []
    assert extended.nodes[f"map:{FREE_MAP}"].block == "crank-cam"
    assert set(extended.block("crank-cam").maps) == existing_maps | {f"map:{FREE_MAP}"}


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
    assert set(atlas['architectures']) == set(ROM_BINDINGS)
    home = atlas['architectures']['JK08A']
    assert len(home['blocks']) == len(tracked.blocks)
    assert len(home['endpoints']) == len(tracked.endpoints)
    assert len(home['chains']) == len(tracked.chains)
    assert sum(len(chain['steps']) for chain in home['chains']) == 387
    assert 'JK08A=47 blocks, 17 chains' in build.summary(atlas)
    document = build.render(atlas)
    assert '"architectures"' in document
    assert "arch-canvas" in document


def test_every_rom_binds_the_architecture(atlas):
    bindings = {rom["id"]: rom["architecture"] for rom in atlas["roms"]}
    assert set(bindings) == set(ROM_BINDINGS)
    for rom, layout in ROM_BINDINGS.items():
        assert bindings[rom] == {'source': rom, 'mode': 'layout', 'layout': layout, 'image': rom}
        view = atlas['architectures'][rom]
        assert view['id'] == view['image'] == rom and view['layout'] == layout
        for node in view['nodes']:
            binding = node['meta']['binding']
            assert binding['layout'] == layout
            assert binding['image'] == rom
            assert not binding['images'] or rom in binding['images']
            assert binding['symbol'] == f'{layout}-{node["addr"]}/{node["meta"]["kbKind"]}'
        for chain in view['chainAvailability']:
            if chain['missing']:
                assert chain['id'] not in {item['id'] for item in view['chains']}


def test_same_layout_images_keep_exact_mode_byte_applicability(atlas):
    for rom in ('JK08A', 'JK00A', 'JK03A', 'JK03B'):
        view = atlas['architectures'][rom]
        nodes = {node['meta']['binding']['meaning']: node for node in view['nodes']}
        assert ('bfs_mode_flags/tbl' in nodes) == (rom == 'JK08A')
        if rom == 'JK08A':
            assert nodes['bfs_mode_flags/tbl']['meta']['binding']['images'] == ['JK08A']
        assert 'bfs_upper_limit_raw/ram' in nodes
        objects = next(item['objects'] for item in atlas['roms'] if item['id'] == rom)
        for item in objects:
            binding = item.get('binding')
            if binding:
                assert binding['availability'] == 'bound'
                assert not binding['images'] or rom in binding['images']


def test_manifest_architecture_table_is_validated():
    valid = {'layout': '7mfk'}
    model._check_architecture_table("manifest.toml", valid)
    for table, message in (
        ([], "must be a table"),
        ({}, "fields differ"),
        ({**valid, "extra": 1}, "fields differ"),
        ({'layout': ' '}, "layout"),
        ({'layout': 7}, "layout"),
        ({'source': 'defs/JK08A.architecture.toml', 'mode': 'exact'}, "fields differ"),
    ):
        with pytest.raises(model.ModelError, match=message):
            model._check_architecture_table("manifest.toml", table)


def test_a_manifest_cannot_borrow_another_layout(tmp_path):
    manifest = model.ROOT / "tools" / "romviz" / "roms" / "JK00A.toml"
    text = manifest.read_text(encoding="utf-8")
    broken = tmp_path / manifest.name
    broken.write_text(
        text.replace('layout = "7mfk"', 'layout = "jk78c"'),
        encoding="utf-8",
    )
    with pytest.raises(model.ModelError, match="belongs to 7mfk, not to jk78c"):
        model.build_rom_model(broken)


def test_an_unavailable_graph_refuses_the_atlas_without_a_legacy_fallback(monkeypatch):
    def unavailable(*args, **kwargs):
        raise KbError('no graph answers', code=6)

    monkeypatch.setattr(graph_atlas, 'snapshot', unavailable)
    with pytest.raises(model.ModelError, match='no graph answers'):
        model.build_rom_model(model.resolve_manifest('JK78C'))


def test_command_line_reports_the_model(capsys, tracked):
    assert architecture.main(["check"]) == 0
    printed = capsys.readouterr().out
    assert "architecture JK08A" in printed
    assert "functions placed" in printed
    assert "chain steps" in printed
    pending = {
        block.id
        for block in tracked.blocks
        if block.stage == architecture.UNATTRIBUTED_STAGE
    }
    open_maps = [
        node
        for node in tracked.nodes.values()
        if node.kind == "map" and node.block in pending
    ]
    assert open_maps
    assert (
        f"maps without a functional role: {len(open_maps)} in stage unattributed"
        in printed
    )


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
