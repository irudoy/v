"""Version checks consume machine pins and actual launch commands."""

import subprocess
import sys

import pytest

from tools import version_index


def test_machine_configuration_checks_do_not_read_markdown(monkeypatch):
    read = version_index._text

    def machine_input(path):
        assert not str(path).endswith(".md"), "documentation is not a version input"
        return read(path)

    monkeypatch.setattr(version_index, "_text", machine_input)
    assert version_index.main(["--check"]) == 0


def test_standalone_entry_point_works_outside_the_repository(tmp_path):
    script = version_index.ROOT / "tools/version_index.py"
    result = subprocess.run(
        [sys.executable, str(script), "--check"],
        cwd=tmp_path, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr


def test_absent_machine_local_configuration_has_no_server_pin(tmp_path, monkeypatch):
    monkeypatch.setattr(version_index, "ROOT", tmp_path)
    assert version_index.mcp_memgraph_version() is None


def test_execution_image_tag_follows_the_simulator_pin(monkeypatch):
    read = version_index._text
    path = version_index.IMAGE_SCRIPTS[0]
    current = version_index.simulator_version()

    def changed(name):
        text = read(name)
        return text.replace(f"vq-sh-elf-run:{current}", "vq-sh-elf-run:0.0") if name == path else text

    monkeypatch.setattr(version_index, "_text", changed)
    with pytest.raises(version_index.VersionError, match="the gate requires"):
        version_index.check_execution_image()


def test_toolchain_pins_are_required_in_the_actual_dockerfile(monkeypatch):
    read = version_index._text

    def missing_pin(path):
        text = read(path)
        if path == "tools/sh-elf-run/Dockerfile":
            return "\n".join(line for line in text.splitlines() if not line.startswith("ARG GCC_SH_ELF_VERSION="))
        return text

    monkeypatch.setattr(version_index, "_text", missing_pin)
    with pytest.raises(version_index.VersionError, match="GCC_SH_ELF_VERSION"):
        version_index.toolchain_versions()


def test_platform_packages_pin_one_python_can_version():
    pins = {
        path: version_index.requirement_pin(path, "python-can")
        for path in version_index.REQUIREMENTS
    }
    assert len(set(pins.values())) == 1


def test_inconsistent_python_can_pins_fail(monkeypatch):
    read = version_index.requirement_pin

    def changed(path, package):
        version = read(path, package)
        return version + ".different" if path == version_index.REQUIREMENTS[0] else version

    monkeypatch.setattr(version_index, "requirement_pin", changed)
    with pytest.raises(version_index.VersionError, match="different python-can versions"):
        version_index.python_can_version()


@pytest.mark.parametrize("command", ["echo no Python launcher", "py -0.0 -m venv .venv"])
def test_wrong_packaged_windows_selector_fails(monkeypatch, command):
    from tools.can_dashboard import package_windows

    monkeypatch.setattr(package_windows, "INSTALL_CMD", command)
    with pytest.raises(version_index.VersionError, match="Windows installer selects Python"):
        version_index.check_launchers()


def test_wrong_macos_build_tool_binding_fails(monkeypatch):
    from tools.can_dashboard import package_macos

    monkeypatch.setattr(package_macos, "PYINSTALLER_VERSION", "different")
    with pytest.raises(version_index.VersionError, match="macOS packager requires PyInstaller"):
        version_index.check_launchers()


def test_the_windows_installer_and_the_macos_build_read_their_pins():
    from tools.can_dashboard import package_macos, package_windows

    assert package_windows.PYTHON_VERSION == version_index.python_version()
    assert f"py -{package_windows.PYTHON_VERSION} -m venv" in (
        package_windows.INSTALL_CMD
    )
    assert package_macos.PYINSTALLER_VERSION == version_index.requirement_pin(
        version_index.REQUIREMENTS[2], "pyinstaller"
    )
