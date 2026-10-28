from pathlib import Path
import tempfile
from unittest import mock

import pytest

from tools.mapkit import definition_targets
from tools.maps import build_tracker


def test_report_names_unaccessed_maps_with_their_retained_disposition(capsys):
    rows = [dict(table="00000100", confidence="code", family="direct-row-major",
                 role="dead", semantics="", via="", accessors="", diagnostic_context="",
                 note="Retained unreferenced calibration data."),
            dict(table="00000200", confidence="candidate", family="direct-row-major",
                 role="table", semantics="", via="", accessors="", diagnostic_context="", note="")]
    build_tracker.report(rows, "defs/EXAMPLE.maps.csv")
    output = capsys.readouterr().out
    assert "00000100: role=dead, confidence=code; Retained unreferenced calibration data." in output
    assert "00000200: role=table, confidence=candidate; Review required: no reason recorded." in output
    assert "orphan graph nodes" not in output


def _fake_emitter(failing_rom=None):
    def emit(rom, tracker=None, display_tracker=None):
        if rom == failing_rom:
            raise RuntimeError(f"failed {rom}")
        Path(tracker).write_text(f"ledger {rom}\n", encoding="utf-8")

    return emit


def test_emit_all_generates_every_canonical_source():
    with tempfile.TemporaryDirectory() as directory:
        output_dir = Path(directory)
        with mock.patch.object(
            build_tracker, "emit_tracker", side_effect=_fake_emitter()
        ) as emitter:
            build_tracker.emit_all(output_dir)

        sources = definition_targets.registered_sources()
        assert [call.args[0] for call in emitter.call_args_list] == list(sources)
        for rom in sources:
            assert (output_dir / f"{rom}.maps.csv").read_text() == (
                f"ledger {rom}\n"
            )


def test_emit_all_keeps_existing_ledgers_when_one_source_fails():
    with tempfile.TemporaryDirectory() as directory:
        output_dir = Path(directory)
        sources = definition_targets.registered_sources()
        for rom in sources:
            (output_dir / f"{rom}.maps.csv").write_text("old ledger\n")

        with mock.patch.object(
            definition_targets,
            "registered_sources",
            return_value=("JK08A", "BROKEN"),
        ), mock.patch.object(
            build_tracker,
            "emit_tracker",
            side_effect=_fake_emitter(failing_rom="BROKEN"),
        ):
            with pytest.raises(RuntimeError, match="failed BROKEN"):
                build_tracker.emit_all(output_dir)

        for rom in sources:
            assert (output_dir / f"{rom}.maps.csv").read_text() == "old ledger\n"


def test_no_argument_cli_selects_all_sources():
    with mock.patch.object(build_tracker, "emit_all") as emit_all:
        build_tracker.main([])
    emit_all.assert_called_once_with()
