"""Native identity does not supply an unbound engineering conversion."""

import pytest

from kb import compile, levels, repo


UNASSERTED = (
    "ignition_state_surface_axis_x/axis",
    "ignition_state_surface_axis_y/axis",
    "intake_cvtc_target_throttled_axis_x/axis",
    "intake_cvtc_target_throttled_axis_y/axis",
    "vvel_duration_hot_intake_idle_axis_x/axis",
    "vvel_duration_hot_intake_idle_axis_y/axis",
    "vvel_duration_hot_intake_idle_floor_axis/axis",
    "vvel_duration_model_hot_intake_idle_axis_x/axis",
    "vvel_duration_model_hot_intake_idle_axis_y/axis",
    "vvel_duration_throttled_axis/axis",
    "vvel_shaft_angle_axis/axis",
    "vvel_shaft_angle_limit_cvtc_axis/axis",
    "vvel_shaft_angle_limit_engine_speed_axis/axis",
    "vvel_shaft_angle_monitor_floor_a_axis/axis",
    "vvel_shaft_angle_monitor_floor_a_second_axis/axis",
    "vvel_shaft_angle_monitor_floor_b_axis/axis",
    "vvel_shaft_angle_monitor_floor_b_second_axis/axis",
    "vvel_shaft_angle_second_axis/axis",
    "fuel_compensation_alternate/tbl",
    "fuel_compensation_coefficient_curve/tbl",
    "fuel_compensation_coefficient_axis/axis",
    "ignition_surface_cold/tbl",
    "ignition_surface_hot/tbl",
    "ignition_surface_state_3/tbl",
    "ignition_surface_state_4/tbl",
    "ignition_surface_state_5/tbl",
    "ignition_surface_state_6_7/tbl",
    "intake_cvtc_target_cold/tbl",
    "intake_cvtc_target_running/tbl",
    "intake_cvtc_target_throttled/tbl",
    "vvel_duration_cold/tbl",
    "vvel_duration_hot_intake_idle/tbl",
    "vvel_duration_hot_intake_idle_floor/tbl",
    "vvel_duration_hot_intake_idle_knock/tbl",
    "vvel_duration_hot_intake_idle_knock_floor/tbl",
    "vvel_duration_mode_14/tbl",
    "vvel_duration_model_hot_intake_idle/tbl",
    "vvel_duration_model_hot_intake_idle_knock/tbl",
    "vvel_duration_running/tbl",
    "vvel_duration_startup/tbl",
    "vvel_duration_startup_blend/tbl",
    "vvel_duration_throttled/tbl",
    "vvel_shaft_angle_limit_cvtc/tbl",
    "vvel_shaft_angle_limit_engine_speed/tbl",
    "vvel_shaft_angle_monitor_floor_a/tbl",
    "vvel_shaft_angle_monitor_floor_a_second/tbl",
    "vvel_shaft_angle_monitor_floor_b/tbl",
    "vvel_shaft_angle_monitor_floor_b_second/tbl",
)


@pytest.mark.parametrize("ref", UNASSERTED)
def test_unasserted_native_conversion_preserves_identity_and_conversion_boundary(ref):
    meaning = next(item for item in compile.cached(repo.ROOT).meanings if item.key == ref)
    assert not {"unit", "scale", "to_raw", "scale_level"} & meaning.props.keys()
    assert meaning.props["level"] == "code"
    assert meaning.symbols
    for symbol in meaning.symbols.values():
        assert not {"unit", "scale", "to_raw", "scale_level"} & symbol.props.keys()
        assert symbol.value("storage") in {"uint8", "uint16"}
        assert symbol.evidence
        assert not any(item.get("supports") == "scale" for item in symbol.evidence)
        notes = symbol.value("note")
        notes = [notes] if isinstance(notes, str) else notes
        assert notes
        for note in notes:
            if ref in {
                "fuel_compensation_alternate/tbl",
                "fuel_compensation_coefficient_curve/tbl",
            }:
                assert "Editor values are stored counts" in note
                assert "neutral value are unestablished" in note
                assert "raw 128 is not qualified as neutral" in note
                assert "unconfirmed on every image" in note
            elif ref == "fuel_compensation_coefficient_axis/axis":
                assert (
                    "physical input and its engineering conversion remain unestablished"
                    in note
                )
                assert "Values are stored counts" in note
            else:
                assert "Engineering conversion is unestablished" in note
                assert "Retained hypothesis:" in note
                assert "proposed editor-grid inverse" in note
                assert "Origin:" in note


@pytest.mark.slow
@pytest.mark.parametrize("level, reason", [("candidate", "lacks evidence"),
                                          ("code", "lacks grounding")])
def test_identity_cannot_ground_a_restored_native_scale(monkeypatch, level, reason):
    model = compile.cached(repo.ROOT)
    meaning = next(item for item in model.meanings if item.key == UNASSERTED[0])
    monkeypatch.setattr(meaning, "props", {**meaning.props, "unit": "RPM", "scale": "x*50",
                                          "to_raw": "x/50", "scale_level": level})
    assert any(issue.subject == meaning.key and reason in issue.message
               for issue in levels.check(model, subjects={meaning.key}))
