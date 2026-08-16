from pathlib import Path
import tempfile
import unittest
import zipfile

from tools.can_dashboard import package_windows


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
                    prefix + "requirements.txt",
                    prefix + "patches/can-telemetry-schema.json",
                    prefix + "tools/can_dashboard/app.py",
                    prefix + "tools/logs/can_telemetry.py",
                    prefix + "tools/logs/peak_trc_audit.py",
                }
                self.assertTrue(expected <= names)
                requirements = archive.read(
                    prefix + "requirements.txt"
                ).decode("utf-8")
                self.assertEqual(requirements.strip(), "python-can[pcan]==4.6.1")
                active = archive.read(
                    prefix + "run-dashboard-active.cmd"
                ).decode("utf-8")
                self.assertIn("--active", active)

            with self.assertRaises(FileExistsError):
                package_windows.build_package(output)
            first_package = output.read_bytes()
            package_windows.build_package(output, force=True)
            self.assertEqual(output.read_bytes(), first_package)


if __name__ == "__main__":
    unittest.main()
