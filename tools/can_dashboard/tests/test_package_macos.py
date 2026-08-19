import os
from pathlib import Path
import plistlib
import stat
import tempfile
import unittest
from unittest import mock
import zipfile

from tools.can_dashboard import __version__
from tools.can_dashboard import package_macos


class MacosPackageTest(unittest.TestCase):
    @staticmethod
    def create_app(root):
        app = root / package_macos.APP_BUNDLE_NAME
        executable = app / "Contents/MacOS" / package_macos.APP_NAME
        resources = app / "Contents/Resources"
        frameworks = app / "Contents/Frameworks"
        executable.parent.mkdir(parents=True)
        resources.mkdir(parents=True)
        frameworks.mkdir(parents=True)
        executable.write_bytes(b"#!/bin/sh\nexit 0\n")
        executable.chmod(0o755)
        (resources / "schema.json").write_text("{}\n", encoding="ascii")
        (frameworks / "schema.json").symlink_to("../Resources/schema.json")
        with (app / "Contents/Info.plist").open("wb") as destination:
            plistlib.dump({
                "CFBundleDisplayName": package_macos.APP_NAME,
                "CFBundleExecutable": package_macos.APP_NAME,
                "CFBundleIdentifier": package_macos.BUNDLE_IDENTIFIER,
                "CFBundleName": package_macos.APP_NAME,
                "CFBundleShortVersionString": __version__,
                "CFBundleVersion": __version__,
            }, destination)
        return app

    def test_pyinstaller_contract_is_windowed_arm64_onedir(self):
        arguments = package_macos.pyinstaller_arguments(
            Path("dist"),
            Path("work"),
            Path("spec"),
        )
        self.assertIn("--windowed", arguments)
        self.assertIn("--onedir", arguments)
        self.assertIn("--target-architecture", arguments)
        self.assertIn(package_macos.TARGET_ARCHITECTURE, arguments)
        self.assertIn(package_macos.BUNDLE_IDENTIFIER, arguments)
        self.assertIn("can.interfaces.pcan", arguments)
        self.assertNotIn("tzdata", arguments)
        for source, destination in package_macos.DATA_FILES:
            self.assertIn(f"{source}:{destination}", arguments)

    def test_archive_preserves_bundle_modes_and_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            app = self.create_app(root)
            output = root / "dashboard.zip"
            package_macos.archive_app(app, output)
            first_package = output.read_bytes()
            package_macos.archive_app(app, output)
            self.assertEqual(output.read_bytes(), first_package)

            with zipfile.ZipFile(output) as archive:
                prefix = package_macos.APP_BUNDLE_NAME + "/"
                executable_name = prefix + "Contents/MacOS/" + package_macos.APP_NAME
                symlink_name = prefix + "Contents/Frameworks/schema.json"
                self.assertEqual(archive.testzip(), None)
                executable_mode = (
                    archive.getinfo(executable_name).external_attr >> 16
                )
                self.assertTrue(executable_mode & 0o111)
                symlink_mode = archive.getinfo(symlink_name).external_attr >> 16
                self.assertTrue(stat.S_ISLNK(symlink_mode))
                self.assertEqual(
                    archive.read(symlink_name),
                    b"../Resources/schema.json",
                )
                self.assertEqual(
                    archive.read(prefix + "Contents/Resources/schema.json"),
                    b"{}\n",
                )

    def test_bundle_metadata_uses_generic_product_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            app = self.create_app(Path(directory))
            package_macos._set_bundle_metadata(app)
            with (app / "Contents/Info.plist").open("rb") as source:
                info = plistlib.load(source)

        self.assertEqual(info["CFBundleDisplayName"], package_macos.APP_NAME)
        self.assertEqual(info["CFBundleExecutable"], package_macos.APP_NAME)
        self.assertEqual(info["CFBundleName"], package_macos.APP_NAME)
        self.assertEqual(
            info["CFBundleIdentifier"],
            package_macos.BUNDLE_IDENTIFIER,
        )

    def test_validation_resolves_relative_bundle_before_running_executable(self):
        temporary_root = package_macos.ROOT / "tmp"
        temporary_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temporary_root) as directory:
            app = self.create_app(Path(directory))
            relative = app.relative_to(package_macos.ROOT)
            with mock.patch.object(
                package_macos.subprocess,
                "check_output",
                return_value="arm64",
            ), mock.patch.object(package_macos, "_run") as run:
                package_macos._validate_app(
                    relative,
                    run_smoke_test=False,
                )

        driver_check = run.call_args_list[-1].args[0]
        self.assertTrue(Path(driver_check[0]).is_absolute())
        self.assertEqual(driver_check[-1], "--pcan-driver-check")

    def test_replace_app_preserves_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.create_app(root / "source")
            destination = root / "output" / package_macos.APP_BUNDLE_NAME
            destination.parent.mkdir()
            package_macos._replace_app(source, destination)
            link = destination / "Contents/Frameworks/schema.json"
            self.assertTrue(link.is_symlink())
            self.assertEqual(os.readlink(link), "../Resources/schema.json")

    def test_replace_app_validates_staging_before_replacing_existing_app(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.create_app(root / "source")
            destination = self.create_app(root / "destination")
            marker = destination / "Contents/Resources/existing.txt"
            marker.write_text("preserve", encoding="ascii")
            validated = []

            def reject(staging):
                validated.append(staging)
                raise RuntimeError("invalid copy")

            with self.assertRaisesRegex(RuntimeError, "invalid copy"):
                package_macos._replace_app(
                    source,
                    destination,
                    validate=reject,
                )

            self.assertEqual(marker.read_text(encoding="ascii"), "preserve")
            self.assertEqual(validated[0].suffix, ".app")
            self.assertFalse(
                destination.with_name(
                    f"{destination.stem}.staging{destination.suffix}"
                ).exists()
            )

    def test_archive_and_application_outputs_must_differ(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "same-output"
            with self.assertRaisesRegex(ValueError, "outputs must differ"):
                package_macos.build_package(output, app_output=output)


if __name__ == "__main__":
    unittest.main()
