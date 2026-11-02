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
from tools.can_dashboard.package_locks import (
    TARGET_BY_NAME,
    bootstrap_text,
    normalize,
    parse_lock,
)
from tools.version_index import python_version, requirement_pin


APP_NAME = PRODUCT_NAME
APP_BUNDLE_NAME = f"{APP_NAME}.app"
BUNDLE_IDENTIFIER = f"com.github.irudoy.vhrev.{PRODUCT_SLUG}"
TARGET_ARCHITECTURE = "arm64"
LOCK_TARGET = TARGET_BY_NAME["macos-build"]
BUILD_REQUIREMENTS = LOCK_TARGET.requirements
PYINSTALLER_VERSION = requirement_pin(BUILD_REQUIREMENTS, "pyinstaller")
ENTRY_POINT = ROOT / "tools/can_dashboard/app.py"
DATA_FILES = (
    (ROOT / "patches/can-telemetry-schema.json", "patches"),
    (ROOT / "patches/can-telemetry-configurations.json", "patches"),
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


def install_commands(interpreter, bootstrap):
    """Return the uv commands that install the build lock into an environment.

    The bootstrap wheels install first, so the pinned setuptools builds the
    source builds of the lock without build isolation; nothing is resolved
    beyond the lock.
    """
    common = (
        "uv",
        "pip",
        "install",
        "--no-config",
        "--python",
        str(interpreter),
        "--require-hashes",
        "--no-deps",
        "--only-binary",
        ":all:",
    )
    sources = []
    for name in LOCK_TARGET.sources:
        sources.extend(("--no-binary", name))
    return [
        (*common, "-r", str(bootstrap)),
        (
            *common,
            "--no-build-isolation",
            *sources,
            "-r",
            str(ROOT / LOCK_TARGET.lock),
        ),
    ]


def prepare_environment(path):
    """Create the build environment from the macOS build lock."""
    path = Path(path).resolve()
    if path.exists() or path.is_symlink():
        if not (path / "pyvenv.cfg").is_file():
            raise FileExistsError(f"not a virtual environment: {path}")
        shutil.rmtree(path)
    _run(("uv", "venv", "--no-config", "--python", python_version(), path))
    bootstrap = path / "bootstrap-requirements.txt"
    lock = (ROOT / LOCK_TARGET.lock).read_text(encoding="utf-8")
    bootstrap.write_text(bootstrap_text(LOCK_TARGET, lock), encoding="utf-8")
    interpreter = path / "bin/python"
    for command in install_commands(interpreter, bootstrap):
        _run(command)
    return interpreter


def environment_differences(installed, lock_text):
    """Describe how installed distributions differ from the lock entries."""
    locked = {
        name: entry.version for name, entry in parse_lock(lock_text).items()
    }
    differences = []
    for name in sorted(set(locked) | set(installed)):
        if name not in installed:
            differences.append(f"missing {name} {locked[name]}")
        elif name not in locked:
            differences.append(f"unlocked {name} {installed[name]}")
        elif installed[name] != locked[name]:
            differences.append(
                f"{name} {installed[name]} instead of {locked[name]}"
            )
    return differences


def _installed_distributions():
    return {
        normalize(distribution.metadata["Name"]): distribution.version
        for distribution in metadata.distributions()
    }


def _require_build_environment():
    if sys.platform != "darwin":
        raise RuntimeError("the macOS application must be built on macOS")
    running = f"{sys.version_info.major}.{sys.version_info.minor}"
    if running != python_version():
        raise RuntimeError(
            f"Python {python_version()} is required, found {running}"
        )
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
    differences = environment_differences(
        _installed_distributions(),
        (ROOT / LOCK_TARGET.lock).read_text(encoding="utf-8"),
    )
    if differences:
        raise RuntimeError(
            f"the build environment differs from {LOCK_TARGET.lock}: "
            + "; ".join(differences)
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
    parser.add_argument(
        "--prepare-environment",
        type=Path,
        metavar="PATH",
        help="create the build environment from the build lock and exit",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--app-output", type=Path)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--skip-smoke-test", action="store_true")
    args = parser.parse_args(argv)
    if args.prepare_environment is not None:
        interpreter = prepare_environment(args.prepare_environment)
        print(f"status=PASS environment={interpreter}")
        return 0
    if args.output is None:
        parser.error("--output is required")
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
