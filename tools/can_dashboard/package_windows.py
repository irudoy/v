#!/usr/bin/env python3
"""Create a minimal source package for the Windows PCAN dashboard."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.can_dashboard import PRODUCT_NAME, PRODUCT_SLUG, __version__

PACKAGE_ROOT = f"{PRODUCT_SLUG}-v{__version__}"
SOURCE_FILES = (
    "patches/__init__.py",
    "patches/can_telemetry_profile.py",
    "patches/can-telemetry-profile.toml",
    "patches/can-telemetry-schema.json",
    "tools/logs/__init__.py",
    "tools/logs/can_telemetry.py",
    "tools/logs/mlvlg.py",
    "tools/logs/peak_trc_audit.py",
    "tools/logs/trc_to_mlg.py",
    "tools/can_dashboard/__init__.py",
    "tools/can_dashboard/app.py",
    "tools/can_dashboard/model.py",
    "tools/can_dashboard/recording.py",
    "tools/can_dashboard/sources.py",
    "tools/can_dashboard/README.md",
)

INSTALL_CMD = r"""@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher was not found. Install 64-bit Python 3.11 from python.org.
  pause
  exit /b 1
)
py -3.11 -m venv .venv
if errorlevel 1 goto :failed
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :failed
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :failed
echo.
echo Installation complete. Run run-demo.cmd, then run-dashboard.cmd.
pause
exit /b 0
:failed
echo.
echo Installation failed.
pause
exit /b 1
"""

RUN_CMD = rf"""@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\pythonw.exe" (
  echo Run install.cmd first.
  pause
  exit /b 1
)
start "{PRODUCT_NAME}" ".venv\Scripts\pythonw.exe" -m tools.can_dashboard.app --channel PCAN_USBBUS1 --bitrate 500000 --can-id 0x6F0 --profile tuning --tick-divisor 1
"""

RUN_ACTIVE_CMD = RUN_CMD.replace(
    "--tick-divisor 1", "--tick-divisor 1 --active"
)
RUN_DEMO_CMD = RUN_CMD.replace(
    "--channel PCAN_USBBUS1 --bitrate 500000 --can-id 0x6F0 --profile tuning --tick-divisor 1",
    "--can-id 0x6F0 --profile tuning --tick-divisor 1 --demo",
)

CONVERT_TRC_CMD = r"""@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run install.cmd first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m tools.logs.trc_to_mlg %*
if errorlevel 1 pause
"""


def _write_member(archive, name, content):
    member = zipfile.ZipInfo(
        f"{PACKAGE_ROOT}/{name}",
        date_time=(1980, 1, 1, 0, 0, 0),
    )
    member.compress_type = zipfile.ZIP_DEFLATED
    member.external_attr = 0o100644 << 16
    archive.writestr(member, content)


def build_package(output, *, force=False):
    output = Path(output)
    if output.exists() and not force:
        raise FileExistsError(f"output already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        prefix=output.name + ".",
        suffix=".tmp",
        dir=output.parent,
        delete=False,
    ) as temporary:
        temporary_path = Path(temporary.name)
    try:
        with zipfile.ZipFile(
            temporary_path,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        ) as archive:
            for relative in SOURCE_FILES:
                source = ROOT / relative
                if not source.is_file():
                    raise FileNotFoundError(source)
                _write_member(archive, relative, source.read_bytes())
            requirements = (
                ROOT / "tools/can_dashboard/requirements-windows.txt"
            ).read_text(encoding="utf-8")
            generated = {
                "requirements.txt": requirements,
                "install.cmd": INSTALL_CMD,
                "run-dashboard.cmd": RUN_CMD,
                "run-dashboard-active.cmd": RUN_ACTIVE_CMD,
                "run-demo.cmd": RUN_DEMO_CMD,
                "convert-trc-to-mlg.cmd": CONVERT_TRC_CMD,
                "VERSION.txt": __version__ + "\n",
            }
            for name, content in generated.items():
                _write_member(archive, name, content.encode("utf-8"))
        os.replace(temporary_path, output)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    output = build_package(args.output, force=args.force)
    print(f"status=PASS output={output} bytes={output.stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
