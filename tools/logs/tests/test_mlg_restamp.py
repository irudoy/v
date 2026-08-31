from dataclasses import replace
from pathlib import Path
import tempfile
import unittest

from tools.can_dashboard import recording
from tools.logs import mlg_restamp, mlvlg


def stale_specs():
    """Return the field table as version 2.0.0 recordings declared it."""

    specs = []
    for binding in recording.build_bindings("tuning"):
        spec = binding.spec
        if "*" in spec.units:
            spec = replace(
                spec,
                name=spec.name + "*",
                units=spec.units.replace("*", ""),
            )
        if spec.units == "degCA":
            spec = replace(spec, transform=-64.0)
        specs.append(spec)
    specs.append(
        mlvlg.FieldSpec(
            "gps_lat", "deg", "GPS", mlvlg.MLG_F32, digits=6
        )
    )
    return tuple(specs)


def write_log(path, specs, records=3):
    with path.open("wb") as stream:
        writer = mlvlg.StreamWriter(stream, specs, 1_776_000_000)
        for index in range(records):
            writer.write(tuple(index + 1 for _ in specs), index * 0.01)
    return mlvlg.validate_mlg(path)


def data_blocks(path):
    data = Path(path).read_bytes()
    field_count = len(mlvlg.read_fields(path))
    return data[mlvlg.MLG_HEADER_SIZE + field_count * mlvlg.MLG_FIELD_SIZE :]


class MlgRestampTest(unittest.TestCase):
    def test_restamp_corrects_identity_and_scaling_without_touching_data(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "stale.mlg"
            specs = stale_specs()
            write_log(log, specs)
            before_blocks = data_blocks(log)

            summary = mlg_restamp.restamp(log)

            self.assertTrue(summary.written)
            self.assertEqual(summary.fields, len(specs))
            self.assertEqual(summary.unmatched, ("gps_lat",))
            self.assertGreater(len(summary.changed), 20)

            fields = mlvlg.read_fields(log)
            names = [field.name for field in fields]
            self.assertEqual(
                [name for name in names if "*" in name], []
            )
            self.assertIn("Intake CVTC actual B1", names)
            self.assertIn("gps_lat", names)
            for field in fields:
                if field.units == "degCA*":
                    self.assertEqual(field.transform, -128.0)
            self.assertEqual(data_blocks(log), before_blocks)
            mlvlg.validate_mlg(log)

    def test_restamp_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "stale.mlg"
            write_log(log, stale_specs())
            mlg_restamp.restamp(log)
            after_first = Path(log).read_bytes()

            summary = mlg_restamp.restamp(log)

            self.assertFalse(summary.written)
            self.assertEqual(summary.changed, ())
            self.assertEqual(Path(log).read_bytes(), after_first)

    def test_dry_run_reports_changes_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "stale.mlg"
            write_log(log, stale_specs())
            original = Path(log).read_bytes()

            summary = mlg_restamp.restamp(log, dry_run=True)

            self.assertFalse(summary.written)
            self.assertGreater(len(summary.changed), 20)
            self.assertEqual(Path(log).read_bytes(), original)

    def test_cli_reports_each_log(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "stale.mlg"
            write_log(log, stale_specs())
            self.assertEqual(mlg_restamp.main([str(log), "--dry-run"]), 0)
            self.assertEqual(mlg_restamp.main([str(log)]), 0)
            self.assertEqual(
                [
                    field.name
                    for field in mlvlg.read_fields(log)
                    if "*" in field.name
                ],
                [],
            )

    def test_invalid_log_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            broken = Path(directory) / "broken.mlg"
            broken.write_bytes(b"not an MLVLG file")
            with self.assertRaises(mlvlg.MlvlgError):
                mlg_restamp.restamp(broken)
            self.assertEqual(mlg_restamp.main([str(broken)]), 1)


if __name__ == "__main__":
    unittest.main()
