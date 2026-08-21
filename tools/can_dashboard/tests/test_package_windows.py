from pathlib import Path
import tempfile
import unittest
import zipfile

from tools.can_dashboard import package_windows
from tools.can_dashboard import __version__


class WindowsPackageTest(unittest.TestCase):
    def test_package_has_complete_runtime_and_launchers(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "dashboard.zip"
            package_windows.build_package(output)
            self.assertTrue(output.is_file())
            with zipfile.ZipFile(output) as archive:
                names = set(archive.namelist())
                prefix = package_windows.PACKAGE_ROOT + "/"
                expected = {
                    prefix + "install.cmd",
                    prefix + "run-dashboard.cmd",
                    prefix + "run-dashboard-active.cmd",
                    prefix + "run-demo.cmd",
                    prefix + "convert-trc-to-mlg.cmd",
                    prefix + "VERSION.txt",
                    prefix + "requirements.txt",
                    prefix + "patches/can-telemetry-schema.json",
                    prefix + "tools/can_dashboard/app.py",
                    prefix + "tools/can_dashboard/recording.py",
                    prefix + "tools/logs/can_telemetry.py",
                    prefix + "tools/logs/can_telemetry_schema.py",
                    prefix + "tools/logs/mlvlg.py",
                    prefix + "tools/logs/peak_trc_audit.py",
                    prefix + "tools/logs/trc_to_mlg.py",
                }
                self.assertTrue(expected <= names)
                requirements = archive.read(
                    prefix + "requirements.txt"
                ).decode("utf-8")
                self.assertEqual(
                    requirements.splitlines(),
                    ["python-can[pcan]==4.6.1", "tzdata==2026.3"],
                )
                active = archive.read(
                    prefix + "run-dashboard-active.cmd"
                ).decode("utf-8")
                self.assertIn("--active", active)
                self.assertEqual(
                    archive.read(prefix + "VERSION.txt").decode("ascii"),
                    __version__ + "\n",
                )
                self.assertEqual(
                    package_windows.PACKAGE_ROOT,
                    f"vq-can-telemetry-v{__version__}",
                )
                self.assertTrue(
                    all(
                        item.date_time == (1980, 1, 1, 0, 0, 0)
                        for item in archive.infolist()
                    )
                )

            with self.assertRaises(FileExistsError):
                package_windows.build_package(output)
            first_package = output.read_bytes()
            package_windows.build_package(output, force=True)
            self.assertEqual(output.read_bytes(), first_package)


if __name__ == "__main__":
    unittest.main()
