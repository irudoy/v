#!/usr/bin/env python3
"""Build and archive the native macOS PCAN dashboard application."""

from __future__ import annotations

import argparse
from importlib import metadata
import os
from pathlib import Path
import plistlib
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.can_dashboard import PRODUCT_NAME, PRODUCT_SLUG, __version__


APP_NAME = PRODUCT_NAME
APP_BUNDLE_NAME = f"{APP_NAME}.app"
BUNDLE_IDENTIFIER = "com.github.irudoy.vhrev.vq-can-telemetry"
TARGET_ARCHITECTURE = "arm64"
PYINSTALLER_VERSION = "6.21.0"
ENTRY_POINT = ROOT / "tools/can_dashboard/app.py"
DATA_FILES = (
    (ROOT / "patches/can-telemetry-profile.toml", "patches"),
    (ROOT / "patches/can-telemetry-schema.json", "patches"),
)


def pyinstaller_arguments(dist_path, work_path, spec_path):
    arguments = [
        "--name",
        APP_NAME,
        "--windowed",
        "--onedir",
        "--clean",
        "--noconfirm",
        "--noupx",
        "--log-level",
        "WARN",
        "--target-architecture",
        TARGET_ARCHITECTURE,
        "--osx-bundle-identifier",
        BUNDLE_IDENTIFIER,
        "--distpath",
        str(dist_path),
        "--workpath",
        str(work_path),
        "--specpath",
        str(spec_path),
        "--paths",
        str(ROOT),
        "--hidden-import",
        "can.interfaces.pcan",
        "--collect-submodules",
        "can.interfaces.pcan",
    ]
    for source, destination in DATA_FILES:
        arguments.extend(("--add-data", f"{source}:{destination}"))
    arguments.append(str(ENTRY_POINT))
    return arguments


def _require_build_environment():
    if sys.platform != "darwin":
        raise RuntimeError("the macOS application must be built on macOS")
    try:
        installed = metadata.version("pyinstaller")
    except metadata.PackageNotFoundError as error:
        raise RuntimeError(
            "PyInstaller is missing; use the dashboard-package-macos target"
        ) from error
    if installed != PYINSTALLER_VERSION:
        raise RuntimeError(
            f"PyInstaller {PYINSTALLER_VERSION} is required, found {installed}"
        )
    for source, _destination in DATA_FILES:
        if not source.is_file():
            raise FileNotFoundError(source)


def _run(command, *, cwd=ROOT, timeout=None):
    return subprocess.run(
        [str(item) for item in command],
        cwd=cwd,
        check=True,
        timeout=timeout,
    )


def _set_bundle_metadata(app_bundle):
    info_path = app_bundle / "Contents/Info.plist"
    with info_path.open("rb") as source:
        info = plistlib.load(source)
    info.update({
        "CFBundleDisplayName": APP_NAME,
        "CFBundleExecutable": APP_NAME,
        "CFBundleIdentifier": BUNDLE_IDENTIFIER,
        "CFBundleName": APP_NAME,
        "CFBundleShortVersionString": __version__,
        "CFBundleVersion": __version__,
        "LSApplicationCategoryType": "public.app-category.utilities",
        "NSHighResolutionCapable": True,
    })
    with info_path.open("wb") as destination:
        plistlib.dump(info, destination, sort_keys=True)


def _validate_app(app_bundle, *, run_smoke_test):
    app_bundle = Path(app_bundle).resolve()
    info_path = app_bundle / "Contents/Info.plist"
    executable = app_bundle / "Contents/MacOS" / APP_NAME
    if not info_path.is_file() or not executable.is_file():
        raise RuntimeError("PyInstaller did not produce a complete app bundle")
    if not os.access(executable, os.X_OK):
        raise RuntimeError(f"application executable is not executable: {executable}")
    with info_path.open("rb") as source:
        info = plistlib.load(source)
    expected = {
        "CFBundleDisplayName": APP_NAME,
        "CFBundleExecutable": APP_NAME,
        "CFBundleIdentifier": BUNDLE_IDENTIFIER,
        "CFBundleName": APP_NAME,
        "CFBundleShortVersionString": __version__,
        "CFBundleVersion": __version__,
    }
    for key, value in expected.items():
        if info.get(key) != value:
            raise RuntimeError(f"Info.plist {key} differs: {info.get(key)!r}")
    architecture = subprocess.check_output(
        ("lipo", "-archs", executable),
        text=True,
    ).strip()
    if architecture != TARGET_ARCHITECTURE:
        raise RuntimeError(
            f"application architecture differs: {architecture!r}"
        )
    _run(("codesign", "--verify", "--deep", "--strict", app_bundle))
    _run((executable, "--pcan-driver-check"), cwd=app_bundle.parent, timeout=10)
    if run_smoke_test:
        _run((executable, "--smoke-test"), cwd=app_bundle.parent, timeout=20)


def _build_app(build_root, *, run_smoke_test=True):
    _require_build_environment()
    build_root = Path(build_root).resolve()
    dist_path = build_root / "dist"
    work_path = build_root / "work"
    spec_path = build_root / "spec"
    for directory in (dist_path, work_path, spec_path):
        directory.mkdir(parents=True, exist_ok=True)
    _run((
        sys.executable,
        "-m",
        "PyInstaller",
        *pyinstaller_arguments(dist_path, work_path, spec_path),
    ))
    app_bundle = dist_path / APP_BUNDLE_NAME
    _set_bundle_metadata(app_bundle)
    _run(("codesign", "--force", "--deep", "--sign", "-", app_bundle))
    _validate_app(app_bundle, run_smoke_test=run_smoke_test)
    return app_bundle


def _zip_member(name, mode):
    member = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    member.create_system = 3
    member.external_attr = mode << 16
    member.compress_type = zipfile.ZIP_DEFLATED
    return member


def archive_app(app_bundle, output):
    app_bundle = Path(app_bundle)
    output = Path(output)
    with zipfile.ZipFile(
        output,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        paths = (app_bundle, *sorted(app_bundle.rglob("*")))
        for path in paths:
            relative = path.relative_to(app_bundle.parent).as_posix()
            details = path.lstat()
            if stat.S_ISDIR(details.st_mode):
                archive.writestr(
                    _zip_member(relative + "/", stat.S_IFDIR | 0o755),
                    b"",
                )
            elif stat.S_ISLNK(details.st_mode):
                archive.writestr(
                    _zip_member(relative, stat.S_IFLNK | 0o777),
                    os.readlink(path).encode("utf-8"),
                )
            elif stat.S_ISREG(details.st_mode):
                permissions = 0o755 if details.st_mode & 0o111 else 0o644
                archive.writestr(
                    _zip_member(relative, stat.S_IFREG | permissions),
                    path.read_bytes(),
                )
            else:
                raise RuntimeError(f"unsupported app bundle entry: {path}")


def _remove_path(path):
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)


def _replace_app(source, destination, *, validate=None):
    source = Path(source)
    destination = Path(destination)
    staging = destination.with_name(
        f"{destination.stem}.staging{destination.suffix}"
    )
    backup = destination.with_name(
        f"{destination.stem}.backup{destination.suffix}"
    )
    _remove_path(staging)
    _remove_path(backup)
    try:
        shutil.copytree(source, staging, symlinks=True)
        if validate is not None:
            validate(staging)
    except Exception:
        _remove_path(staging)
        raise

    had_destination = destination.exists() or destination.is_symlink()
    try:
        if had_destination:
            destination.replace(backup)
    except Exception:
        _remove_path(staging)
        raise
    try:
        staging.replace(destination)
    except Exception:
        if had_destination:
            backup.replace(destination)
        _remove_path(staging)
        raise
    else:
        _remove_path(backup)


def _validate_archive(archive_path, extraction_root):
    extraction_root = Path(extraction_root)
    extraction_root.mkdir(parents=True, exist_ok=True)
    _run(("ditto", "-x", "-k", archive_path, extraction_root))
    extracted_app = extraction_root / APP_BUNDLE_NAME
    _validate_app(extracted_app, run_smoke_test=False)


def build_package(output, *, app_output=None, force=False, run_smoke_test=True):
    output = Path(output)
    app_output = Path(app_output) if app_output is not None else None
    if app_output is not None and output.resolve() == app_output.resolve():
        raise ValueError("archive and application outputs must differ")
    if output.exists() and not force:
        raise FileExistsError(f"output already exists: {output}")
    if app_output is not None and app_output.exists() and not force:
        raise FileExistsError(f"app output already exists: {app_output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    if app_output is not None:
        app_output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=f"{PRODUCT_SLUG}-macos-",
        dir=output.parent,
    ) as directory:
        build_root = Path(directory)
        app_bundle = _build_app(
            build_root,
            run_smoke_test=run_smoke_test,
        )
        archive_path = build_root / output.name
        archive_app(app_bundle, archive_path)
        _validate_archive(archive_path, build_root / "archive-validation")
        if app_output is not None:
            _replace_app(
                app_bundle,
                app_output,
                validate=lambda app: _validate_app(
                    app,
                    run_smoke_test=False,
                ),
            )
        os.replace(archive_path, output)
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--app-output", type=Path)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--skip-smoke-test", action="store_true")
    args = parser.parse_args(argv)
    output = build_package(
        args.output,
        app_output=args.app_output,
        force=args.force,
        run_smoke_test=not args.skip_smoke_test,
    )
    app_detail = f" app={args.app_output}" if args.app_output else ""
    print(
        f"status=PASS output={output} bytes={output.stat().st_size}"
        f"{app_detail}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
