"""Repeated constants and published counts are gated projections of one owner."""

import subprocess

import pytest

from tools import single_source


def test_new_non_ignored_sources_are_checked_before_staging(tmp_path, monkeypatch):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
    (tmp_path / "tracked.md").write_text("Image identities belong to the registry.\n")
    (tmp_path / ".gitignore").write_text("ignored.md\n")
    digest = "a" * 64
    (tmp_path / "new.md").write_text(f"Stock SHA-256: {digest}\n")
    (tmp_path / "ignored.md").write_text(f"Stock SHA-256: {digest}\n")
    subprocess.run(["git", "-C", str(tmp_path), "add", "tracked.md", ".gitignore"],
                   check=True, capture_output=True)
    monkeypatch.setattr(single_source, "ROOT", tmp_path)
    monkeypatch.setattr(single_source, "_image_rows", lambda: [
        {"sha256": digest, "path": "fixture.bin"},
    ])
    assert list(single_source._tracked(".md")) == ["new.md", "tracked.md"]
    with pytest.raises(single_source.SourceError, match="new.md repeats the SHA-256"):
        single_source.check_stock_hashes()
    subprocess.run(["git", "-C", str(tmp_path), "add", "new.md"],
                   check=True, capture_output=True)
    assert list(single_source._tracked(".md")) == ["new.md", "tracked.md"]
    with pytest.raises(single_source.SourceError, match="new.md repeats the SHA-256"):
        single_source.check_stock_hashes()
    (tmp_path / "new.md").write_text("See rom-images/roms.csv for image identity.\n")
    single_source.check_stock_hashes()


@pytest.fixture(scope="module")
def facts():
    return single_source.published_facts()


def _drift(monkeypatch, path, old, new):
    read = single_source._text

    def drifted(name):
        text = read(name)
        if name == path:
            assert old in text, f"{path} no longer carries {old!r}"
            return text.replace(old, new)
        return text

    monkeypatch.setattr(single_source, "_text", drifted)


def test_the_tree_matches_its_sources(facts):
    assert single_source.check_graph_endpoint() > 0
    assert single_source.check_export_root() == "~/tools/ghidra-projects"
    assert single_source.check_can_id() > 0
    single_source.check_product_identity()
    single_source.check_stock_hashes()
    assert single_source.check_kb_questions() == 13
    assert single_source.check_rom_registries() == len(
        single_source.registered_labels()
    )
    single_source.check_published(facts)


@pytest.mark.parametrize("expected", [None, [], ["["], [".*"]])
def test_benchmark_content_contracts_are_required_by_the_source_gate(monkeypatch, expected):
    read = single_source._toml
    config = read(single_source.KB_BENCH)
    config["question"][-1]["expect"] = expected
    monkeypatch.setattr(single_source, "_toml", lambda path: config
                        if path == single_source.KB_BENCH else read(path))
    with pytest.raises(single_source.SourceError, match="question 13: expect"):
        single_source.check_kb_questions()


@pytest.mark.parametrize(
    "check, path, old, new",
    [
        (
            single_source.check_graph_endpoint,
            "tools/mapkit/show.py",
            'BOLT = "bolt://localhost:7687"',
            'BOLT = "bolt://localhost:7688"',
        ),
        (
            single_source.check_graph_endpoint,
            "tools/memgraph/README.md",
            "bolt://127.0.0.1:7687",
            "bolt://nas.local:7687",
        ),
        (
            single_source.check_export_root,
            "tools/ghidra/README.md",
            "~/tools/ghidra-projects",
            "~/ghidra-projects",
        ),
        (
            single_source.check_can_id,
            "tools/can_dashboard/model.py",
            "DEFAULT_CAN_ID = 0x6F0",
            "DEFAULT_CAN_ID = 0x6F2",
        ),
        (
            single_source.check_can_id,
            "tools/logs/README.md",
            "--can-id 0x6F0",
            "--can-id 0x6F2",
        ),
        (
            single_source.check_product_identity,
            "tools/can_dashboard/logfile.py",
            "LOGGER_NAME = PRODUCT_SLUG",
            'LOGGER_NAME = "vq-can-telemetry"',
        ),
        (
            single_source.check_product_identity,
            "Makefile",
            "tmp/$(CAN_DASHBOARD_NAME).app",
            "tmp/VQ CAN Telemetry.app",
        ),
        (
            single_source.check_stock_hashes,
            "defs/JK08A.can.md",
            "`../rom-images/roms.csv`",
            "`ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23`",
        ),
        (
            single_source.check_kb_questions,
            "tools/kb/SPEC.md",
            "| `kb impact 7mfk:0000a4aa` | 1500 | 2 |",
            "| `kb impact 7mfk:0000a4aa` | 1200 | 2 |",
        ),
        (
            single_source.check_kb_questions,
            "tools/kb/bench.toml",
            'command = "kb find knock threshold"\nbudget = 800\nstage = 2',
            'command = "kb find knock threshold"\nbudget = 800\nstage = 3',
        ),
        (
            single_source.check_rom_registries,
            "defs/rom-identities.toml",
            "[rom.JK08A]",
            "[rom.JK09A]\n[rom.JK08A]",
        ),
        (
            single_source.check_rom_registries,
            "rom-images/new-rom-intake.md",
            "homology.toml",
            "family registry",
        ),
    ],
)
def test_a_copy_that_leaves_its_owner_fails(monkeypatch, check, path, old, new):
    _drift(monkeypatch, path, old, new)
    with pytest.raises(single_source.SourceError) as error:
        check()
    assert path in str(error.value) or "unregistered" in str(error.value)


@pytest.mark.parametrize(
    "path, old, new",
    [
        (
            "defs/README.md",
            "hold the 38 codes it shares with",
            "hold the 31 codes it shares with",
        ),
        (
            "rom-images/new-rom-intake.md",
            "read from five onboarded families",
            "read from four onboarded families",
        ),
        (
            "README.md",
            "JK78C, 1ND0A, 1ND3B, and 1ME3B.",
            "JK78C, 1ND0A, and 1ND3B.",
        ),
        (
            "patches/rom-builder.md",
            "binds 56 of the 60 ECU-RAM fields",
            "binds 57 of the 60 ECU-RAM fields",
        ),
        (
            "patches/rom-builder.md",
            "CAN bindings, and all 60 ECU-RAM\ntelemetry fields. 1ND3B",
            "CAN bindings, and all 63 ECU-RAM\ntelemetry fields. 1ND3B",
        ),
        (
            "rom-images/support-matrix.md",
            "ECU RAM; 39 of those",
            "ECU RAM; 45 of those",
        ),
        (
            "patches/rom-builder.md",
            "JK00C and JK00D telemetry binds 60 of the 60",
            "JK00C and JK00D telemetry binds 58 of the 60",
        ),
        (
            "patches/can-telemetry.md",
            "2, profile ID 7, and CRC `0x6474`. A later",
            "2, profile ID 6, and CRC `0x6474`. A later",
        ),
        (
            "tools/can_dashboard/README.md",
            "profile ID 7 with CRC16 `0x6474`",
            "profile ID 7 with CRC16 `0x6475`",
        ),
        (
            "rom-images/23710-1ME3B/README.md",
            "records at `0x01BF58`",
            "records at `0x01BF64`",
        ),
        (
            "tools/can_dashboard/README.md",
            "has 88 channels",
            "has 87 channels",
        ),
        (
            "tools/logs/README.md",
            "contains 88 fields",
            "contains every field",
        ),
    ],
)
def test_a_published_fact_that_leaves_its_source_fails(
    monkeypatch, facts, path, old, new
):
    _drift(monkeypatch, path, old, new)
    with pytest.raises(single_source.SourceError) as error:
        single_source.check_published(facts)
    assert path in str(error.value)
