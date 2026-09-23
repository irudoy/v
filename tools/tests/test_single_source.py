"""Repeated constants and published counts are gated projections of one owner."""

import pytest

from tools import single_source


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
    assert single_source.check_conversions() > 0
    single_source.check_stock_hashes()
    assert single_source.check_rom_registries() == len(
        single_source.registered_labels()
    )
    single_source.check_published(facts)


@pytest.mark.parametrize(
    "scale, conversion",
    [
        ("raw / 256 - 100 percent", (1 / 256, -100.0)),
        ("raw * 0.5 - 64 degCA", (0.5, -64.0)),
        ("raw * 100 / 255 percent", (100 / 255, 0.0)),
        ("raw - 50 degC", (1.0, -50.0)),
        ("candidate raw * 0.1 Nm", (0.1, 0.0)),
        ("Q14 factor", (2**-14, 0.0)),
        ("Q8 software state", (1 / 256, 0.0)),
        (
            "raw * 2 - 590 deg after intake TDC of the injected cylinder; "
            "raw * 2 degCA after the reference tooth",
            (2.0, -590.0),
        ),
        ("raw target coordinate", (1.0, 0.0)),
        ("identity", (1.0, 0.0)),
        ("110 - raw degBTDC", (-1.0, 110.0)),
        ("100 - raw / 2 percent", (-0.5, 100.0)),
        ("110 - raw + 3 deg", None),
        ("raw / 800 V above the learned closed position", (1 / 800, 0.0)),
        ("candidate raw * 0.002 A/F ADJ factor, bounded -1..1", (0.002, 0.0)),
        ("signed internal request coordinate", None),
        ("bit mask", None),
        ("unresolved physical conversion", None),
    ],
)
def test_a_scale_string_declares_its_conversion(scale, conversion):
    assert single_source.declared_conversion(scale) == conversion


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


def test_a_host_conversion_the_profile_does_not_declare_fails(monkeypatch):
    scales = single_source._profile_scales()
    scales["stft_b1_raw"] = {"Q8.8 percent"}
    monkeypatch.setattr(single_source, "_profile_scales", lambda: scales)
    with pytest.raises(single_source.SourceError) as error:
        single_source.check_conversions()
    assert "stft_b1_raw" in str(error.value)


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
            "binds 53 of the 60 ECU-RAM fields",
            "binds 56 of the 60 ECU-RAM fields",
        ),
        (
            "patches/rom-builder.md",
            "CAN bindings, and all 60 ECU-RAM\ntelemetry fields. 1ND3B",
            "CAN bindings, and all 63 ECU-RAM\ntelemetry fields. 1ND3B",
        ),
        (
            "patches/rom-address-profiles.toml",
            "54 of the 60 ECU-RAM fields bind to 1ND0A sources",
            "57 of the 60 ECU-RAM fields bind to 1ND0A sources",
        ),
        (
            "rom-images/support-matrix.md",
            "ECU RAM; 39 of those",
            "ECU RAM; 45 of those",
        ),
        (
            "rom-images/support-matrix.md",
            "mailbox 26; seven fields unavailable",
            "mailbox 26; five fields unavailable",
        ),
        (
            "patches/rom-builder.md",
            "JK00C and JK00D telemetry binds 58 of the 60",
            "JK00C and JK00D telemetry binds 60 of the 60",
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
