"""The ignition-kernel scope retains prerequisites and fail-closed storage."""

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "sh-elf-run"))
import verify_map_switching as driver
import verify_rolling_launch_ignition as ignition
from patches import rolling_launch as model


@pytest.mark.parametrize("failure", (False, True))
def test_kernel_scope_runs_its_prerequisites_and_reports_failures(monkeypatch, capsys, failure):
    order = []
    monkeypatch.setattr(sys, "argv", ["verify", "--rolling-ignition"])
    monkeypatch.setattr(driver, "require_toolchain_version", lambda: order.append("toolchain"))
    monkeypatch.setattr(driver, "verify_simulator_memory", lambda: order.append("memory"))

    def execute():
        order.append("kernel")
        if failure:
            raise RuntimeError("missing kernel instruction")
        return "RL_DWELL_VETO_KERNEL status=PASS"

    monkeypatch.setattr(ignition, "verify_kernel", execute)
    assert driver.main() == int(failure)
    assert order == ["toolchain", "memory", "kernel"]
    captured = capsys.readouterr()
    if failure:
        assert "ignition kernel failed: missing kernel instruction" in captured.err
    else:
        assert "RL_DWELL_VETO_KERNEL status=PASS" in captured.out


def test_kernel_scope_excludes_a_rom_scope(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["verify", "--rolling-ignition", "--rom", "JK08A"])
    with pytest.raises(SystemExit) as error:
        driver.main()
    assert error.value.code == 2


def test_rom_fixture_collision_refuses_before_reading_the_elf(monkeypatch):
    calls = []
    monkeypatch.setattr(ignition, "require_separate_storage", lambda *args: calls.append(args))
    with pytest.raises(driver.VerificationError, match="fixture overlaps the alias"):
        ignition.require_storage("unopened.elf", bytes(ignition.ALIAS_BASE + 1))
    assert calls == []


def test_command_vectors_cover_the_shared_command_and_publisher_boundary():
    table = model.EfficiencyTable(tuple(1000 - 10*i for i in range(41)))
    cases = ignition.command_cases(table)
    names = {case.name for case in cases}
    assert {"idle", "cooldown", "observe", "uncached", "fallback-active",
            "floor-invalid", "map-invalid", "trim-invalid", "mode-invalid",
            "phase-invalid", "publisher-fallback", "publisher-ready"} <= names
    assert {case.stock for case in cases if not case.publisher} >= {119, 120, 121, 237}
    for case in cases:
        assert len(case.configuration) == 102
        assert len(case.before) == len(case.after) == 76
        assert case.after[44 + 8] == case.stock & 255
        assert case.after[44 + 9] == case.command
        if case.publisher and case.name != "publisher-ready":
            assert case.returned == case.stock
            assert case.after[44 + 11] == 0
    ready = next(case for case in cases if case.name == "publisher-ready")
    assert ready.returned == ready.candidate
    assert ready.after[44 + 11] == 1
