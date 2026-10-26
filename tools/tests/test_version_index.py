"""Execution image checks and existing packaging version readers."""

import pytest

from tools import version_index


def test_machine_configuration_checks_do_not_read_markdown(monkeypatch):
    read = version_index._text

    def machine_input(path):
        assert not str(path).endswith(".md"), "documentation is not a version input"
        return read(path)

    monkeypatch.setattr(version_index, "_text", machine_input)
    assert version_index.main(["--check"]) == 0


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


def test_the_windows_installer_and_the_macos_build_read_their_pins():
    from tools.can_dashboard import package_macos, package_windows

    assert package_windows.PYTHON_VERSION == version_index.python_version()
    assert f"py -{package_windows.PYTHON_VERSION} -m venv" in (
        package_windows.INSTALL_CMD
    )
    assert package_macos.PYINSTALLER_VERSION == version_index.requirement_pin(
        package_macos.BUILD_REQUIREMENTS, "pyinstaller"
    )
