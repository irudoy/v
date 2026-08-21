from pathlib import Path
import tempfile
from unittest import mock

import pytest

from tools.mapkit import definition_targets, emit_def


def _fake_emitter(failing_rom=None):
    def emit(
        rom,
        romraider_path,
        tunerpro_path,
        facts_cache=None,
        display_paths=None,
    ):
        if rom == failing_rom:
            raise RuntimeError(f"failed {rom}")
        Path(romraider_path).write_text(f"xml {rom}\n", encoding="utf-8")
        Path(tunerpro_path).write_text(f"xdf {rom}\n", encoding="utf-8")

    return emit


def test_emit_all_generates_every_registered_target():
    with tempfile.TemporaryDirectory() as directory:
        output_dir = Path(directory)
        with mock.patch.object(
            emit_def, "emit_target", side_effect=_fake_emitter()
        ) as emitter:
            emit_def.emit_all(output_dir)

        targets = definition_targets.registered_targets()
        assert [call.args[0] for call in emitter.call_args_list] == list(targets)
        caches = [call.kwargs["facts_cache"] for call in emitter.call_args_list]
        assert all(cache is caches[0] for cache in caches)
        for rom in targets:
            assert (output_dir / f"{rom}.xml").read_text() == f"xml {rom}\n"
            assert (output_dir / f"{rom}.xdf").read_text() == f"xdf {rom}\n"


def test_emit_all_keeps_existing_outputs_when_one_target_fails():
    with tempfile.TemporaryDirectory() as directory:
        output_dir = Path(directory)
        targets = definition_targets.registered_targets()
        for rom in targets:
            (output_dir / f"{rom}.xml").write_text("old xml\n")
            (output_dir / f"{rom}.xdf").write_text("old xdf\n")

        with mock.patch.object(
            emit_def,
            "emit_target",
            side_effect=_fake_emitter(failing_rom="JK03B"),
        ):
            with pytest.raises(RuntimeError, match="failed JK03B"):
                emit_def.emit_all(output_dir)

        for rom in targets:
            assert (output_dir / f"{rom}.xml").read_text() == "old xml\n"
            assert (output_dir / f"{rom}.xdf").read_text() == "old xdf\n"


def test_no_argument_cli_selects_all_targets():
    with mock.patch.object(emit_def, "emit_all") as emit_all:
        emit_def.main([])
    emit_all.assert_called_once_with()
