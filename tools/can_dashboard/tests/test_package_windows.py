import ast
from pathlib import Path
import tempfile
import unittest
import zipfile

from tools.can_dashboard import package_locks
from tools.can_dashboard import package_windows
from tools.can_dashboard import __version__


def repository_imports(entries):
    """Return the repository files that the entry modules import, transitively."""
    root = package_windows.ROOT
    seen, pending = set(), list(entries)
    while pending:
        relative = pending.pop()
        if relative in seen:
            continue
        seen.add(relative)
        tree = ast.parse((root / relative).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert node.level == 0, f"{relative}: relative import"
                names = [node.module]
                names += [f"{node.module}.{alias.name}" for alias in node.names]
            else:
                continue
            for name in names:
                parts = name.split(".")
                for depth in range(1, len(parts) + 1):
                    stem = "/".join(parts[:depth])
                    for candidate in (f"{stem}.py", f"{stem}/__init__.py"):
                        if (root / candidate).is_file():
                            pending.append(candidate)
    return seen


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
                    prefix + "convert-trc-to-mlg.cmd",
                    prefix + "VERSION.txt",
                    prefix + "requirements.txt",
                    prefix + "bootstrap-requirements.txt",
                    prefix + "patches/can-telemetry-schema.json",
                    prefix + "tools/can_dashboard/app.py",
                    prefix + "tools/can_dashboard/feed_dialog.py",
                    prefix + "tools/can_dashboard/hero_picker.py",
                    prefix + "tools/can_dashboard/live_feed.py",
                    prefix + "tools/can_dashboard/recording.py",
                    prefix + "tools/can_dashboard/settings.py",
                    prefix + "tools/can_dashboard/sources.py",
                    prefix + "tools/can_dashboard/widgets.py",
                    prefix + "tools/logs/can_telemetry.py",
                    prefix + "tools/logs/can_telemetry_schema.py",
                    prefix + "tools/logs/mlvlg.py",
                    prefix + "tools/logs/peak_trc_audit.py",
                    prefix + "tools/logs/trc_to_mlg.py",
                }
                self.assertTrue(expected <= names)
                lock = (
                    package_windows.ROOT / package_locks.TARGET_BY_NAME["windows"].lock
                ).read_text(encoding="utf-8")
                self.assertEqual(
                    archive.read(prefix + "requirements.txt").decode("utf-8"), lock
                )
                bootstrap = archive.read(
                    prefix + "bootstrap-requirements.txt"
                ).decode("utf-8")
                self.assertEqual(
                    sorted(package_locks.parse_lock(bootstrap)), ["pip", "setuptools"]
                )
                launchers = {
                    name[len(prefix):]
                    for name in names
                    if name.endswith(".cmd")
                }
                self.assertEqual(
                    launchers,
                    {
                        "install.cmd",
                        "run-dashboard.cmd",
                        "convert-trc-to-mlg.cmd",
                    },
                )
                dashboard = archive.read(
                    prefix + "run-dashboard.cmd"
                ).decode("utf-8")
                self.assertNotIn("--listen-only", dashboard)
                self.assertNotIn("--active", dashboard)
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

    def test_the_package_holds_the_imported_modules_and_declared_files_only(self):
        expected = (
            repository_imports(package_windows.ENTRY_POINTS)
            | set(package_windows.DATA_FILES)
            | set(package_windows.DOCUMENTATION)
        )
        self.assertEqual(len(package_windows.SOURCE_FILES), len(expected))
        self.assertEqual(set(package_windows.SOURCE_FILES), expected)

    def test_the_installer_installs_the_lock_without_resolving(self):
        install = package_windows.INSTALL_CMD
        commands = [line for line in install.splitlines() if " -m pip " in line]
        self.assertEqual(len(commands), 3)
        bootstrap, lock, check = commands
        for command in (bootstrap, lock):
            self.assertIn("--require-hashes --no-deps", command)
            self.assertIn("--only-binary :all:", command)
        self.assertTrue(bootstrap.endswith("-r bootstrap-requirements.txt"))
        self.assertIn("--no-build-isolation", lock)
        self.assertIn("--no-binary uptime", lock)
        self.assertTrue(lock.endswith("-r requirements.txt"))
        self.assertTrue(check.endswith("-m pip check"))
        self.assertNotIn("--upgrade", install)


if __name__ == "__main__":
    unittest.main()
