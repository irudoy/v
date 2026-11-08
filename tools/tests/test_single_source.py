"""Executable constants and registry bindings use machine owners."""

import subprocess

import pytest

from tools import single_source


def test_new_non_ignored_sources_are_checked_before_staging(tmp_path, monkeypatch):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
    (tmp_path / "tracked.py").write_text("VALUE = 1\n")
    (tmp_path / ".gitignore").write_text("ignored.py\n")
    (tmp_path / "new.py").write_text("DEFAULT_CAN_ID = 0x6F2\n")
    (tmp_path / "ignored.py").write_text("DEFAULT_CAN_ID = 0x6F2\n")
    subprocess.run(["git", "-C", str(tmp_path), "add", "tracked.py", ".gitignore"],
                   check=True, capture_output=True)
    monkeypatch.setattr(single_source, "ROOT", tmp_path)
    monkeypatch.setattr(single_source, "telemetry_can_id", lambda: 0x6F0)
    assert list(single_source._tracked(".py")) == ["new.py", "tracked.py"]
    with pytest.raises(single_source.SourceError, match="new.py defaults"):
        single_source.check_can_id()
    subprocess.run(["git", "-C", str(tmp_path), "add", "new.py"],
                   check=True, capture_output=True)
    assert list(single_source._tracked(".py")) == ["new.py", "tracked.py"]
    with pytest.raises(single_source.SourceError, match="new.py defaults"):
        single_source.check_can_id()
    (tmp_path / "new.py").write_text("DEFAULT_CAN_ID = 0x6F0\n")
    single_source.check_can_id()


def _drift(monkeypatch, path, old, new):
    read = single_source._text

    def drifted(name):
        text = read(name)
        if name == path:
            assert old in text, f"{path} no longer carries {old!r}"
            return text.replace(old, new)
        return text

    monkeypatch.setattr(single_source, "_text", drifted)


@pytest.mark.slow
def test_the_tree_matches_its_machine_sources():
    assert single_source.check_graph_endpoint() > 0
    assert single_source.check_export_root() == "~/tools/ghidra-projects"
    assert single_source.check_can_id() > 0
    single_source.check_product_identity()
    single_source.check_kb_questions()
    assert single_source.check_rom_registries() == len(
        single_source.registered_labels()
    )


@pytest.mark.parametrize("expected", [None, [], ["["], [".*"]])
def test_benchmark_content_contracts_are_required_by_the_source_gate(monkeypatch, expected):
    read = single_source._toml
    config = read(single_source.KB_BENCH)
    config["question"][-1]["expect"] = expected
    monkeypatch.setattr(single_source, "_toml", lambda path: config
                        if path == single_source.KB_BENCH else read(path))
    with pytest.raises(single_source.SourceError, match="question .*: expect"):
        single_source.check_kb_questions()


@pytest.mark.parametrize("needs", ["ghidra", ["docker"], ["ghidra", "ghidra"]])
def test_benchmark_needs_name_known_capabilities_in_the_source_gate(monkeypatch, needs):
    read = single_source._toml
    config = read(single_source.KB_BENCH)
    config["question"][-1]["needs"] = needs
    monkeypatch.setattr(single_source, "_toml", lambda path: config
                        if path == single_source.KB_BENCH else read(path))
    with pytest.raises(single_source.SourceError, match="question .*: needs"):
        single_source.check_kb_questions()


@pytest.mark.parametrize(
    "check, path, old, new",
    [
        (
            single_source.check_graph_endpoint,
            "tools/memgraph/docker-compose.yml",
            '"127.0.0.1:7687:7687"',
            '"127.0.0.1:7688:7687"',
        ),
        (
            single_source.check_can_id,
            "tools/can_dashboard/model.py",
            "DEFAULT_CAN_ID = 0x6F0",
            "DEFAULT_CAN_ID = 0x6F2",
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
            single_source.check_rom_registries,
            "defs/rom-identities.toml",
            "[rom.JK08A]",
            "[rom.JK09A]\n[rom.JK08A]",
        ),
    ],
)
def test_a_copy_that_leaves_its_owner_fails(monkeypatch, check, path, old, new):
    _drift(monkeypatch, path, old, new)
    with pytest.raises(single_source.SourceError) as error:
        check()
    assert path in str(error.value) or "unregistered" in str(error.value)
def test_machine_checks_do_not_read_markdown(monkeypatch):
    read = single_source._text

    def machine_input(path):
        assert not str(path).endswith(".md"), "documentation is not a machine input"
        return read(path)

    monkeypatch.setattr(single_source, "_text", machine_input)
    assert single_source.main(["--check"]) == 0
