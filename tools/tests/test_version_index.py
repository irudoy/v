"""The deployment table is a gated projection of the pins the project runs."""

import pytest

from tools import version_index
from tools.can_dashboard import __version__ as dashboard_version


def test_every_published_version_is_an_executed_pin():
    pinned = version_index.check_index()
    published = version_index.published_versions()
    assert set(pinned) <= set(published)
    assert pinned["CAN dashboard"] == (dashboard_version,)
    assert pinned["Memgraph Lab"] == pinned["Memgraph MAGE"]


def test_the_table_is_the_only_tool_document_publishing_a_version():
    version_index.check_repeats(version_index.check_index())
    version_index.check_launchers()


@pytest.mark.parametrize(
    "component, published, pinned",
    [
        ("Memgraph Lab", "3.11.0", "3.12.1"),
        ("`tzdata`", "2026.3", "2026.2"),
        ("CAN dashboard", "8.2.5", "8.2.6"),
        pytest.param(
            "`mcp-memgraph`",
            "0.4.1",
            "0.2.0",
            marks=pytest.mark.skipif(
                not (version_index.ROOT / ".mcp.json").is_file(),
                reason="the machine-local .mcp.json is absent, so the row is unchecked",
            ),
        ),
    ],
)
def test_a_table_row_that_leaves_its_pin_behind_fails(
    monkeypatch, component, published, pinned
):
    read = version_index._text

    def drifted(path):
        text = read(path)
        if path == "tools/README.md":
            return text.replace(
                f"| {component} | {published} |", f"| {component} | {pinned} |"
            )
        return text

    monkeypatch.setattr(version_index, "_text", drifted)
    with pytest.raises(version_index.VersionError) as error:
        version_index.check_index()
    assert component in str(error.value)
    assert published in str(error.value)


def test_a_missing_row_fails(monkeypatch):
    read = version_index._text

    def without_dashboard(path):
        text = read(path)
        if path == "tools/README.md":
            return "\n".join(
                line
                for line in text.splitlines()
                if not line.startswith("| CAN dashboard |")
            )
        return text

    monkeypatch.setattr(version_index, "_text", without_dashboard)
    with pytest.raises(version_index.VersionError) as error:
        version_index.check_index()
    assert "CAN dashboard" in str(error.value)


def test_a_machine_local_configuration_that_is_absent_leaves_its_row_unchecked(
    monkeypatch,
):
    monkeypatch.setattr(version_index, "mcp_memgraph_version", lambda: None)
    pinned = version_index.check_index()
    assert "`mcp-memgraph`" not in pinned
    assert "`mcp-memgraph`" in version_index.published_versions()


def _with_appended_dashboard_readme(monkeypatch, addition):
    """Append text to the dashboard README as the checkers read it."""
    documents = version_index._documents

    def appended():
        for path, text in documents():
            if path.name == "README.md" and path.parent.name == "can_dashboard":
                yield path, text + addition
            else:
                yield path, text

    monkeypatch.setattr(version_index, "_documents", appended)


def test_prose_that_repeats_a_published_version_fails(monkeypatch):
    _with_appended_dashboard_readme(
        monkeypatch, f"\nThe dashboard is {dashboard_version} today.\n"
    )
    with pytest.raises(version_index.VersionError) as error:
        version_index.check_repeats(version_index.check_index())
    assert "can_dashboard/README.md" in str(error.value)


def test_a_command_block_may_carry_a_version_prose_may_not(monkeypatch):
    _with_appended_dashboard_readme(
        monkeypatch, f"\n```bash\ncat vq-{dashboard_version}.zip\n```\n"
    )
    version_index.check_repeats(version_index.check_index())


def test_a_launcher_selector_that_leaves_the_pin_behind_fails(monkeypatch):
    _with_appended_dashboard_readme(
        monkeypatch, "\n```bash\npy -3.13 -m tools.can_dashboard.app\n```\n"
    )
    with pytest.raises(version_index.VersionError) as error:
        version_index.check_launchers()
    assert "py -3.13" in str(error.value)


def test_platform_packages_pin_one_python_can_version():
    pins = {
        path: version_index.requirement_pin(path, "python-can")
        for path in version_index.REQUIREMENTS
    }
    assert len(set(pins.values())) == 1


def test_the_windows_installer_and_the_macos_build_read_their_pins():
    from tools.can_dashboard import package_macos, package_windows

    assert package_windows.PYTHON_VERSION == version_index.python_version()
    assert f"py -{package_windows.PYTHON_VERSION} -m venv" in (
        package_windows.INSTALL_CMD
    )
    assert package_macos.PYINSTALLER_VERSION == version_index.requirement_pin(
        version_index.REQUIREMENTS[2], "pyinstaller"
    )
