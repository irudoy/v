"""Persistent presentation settings of the telemetry dashboard.

The file holds what the operator chose in the window: the color theme, the
ordered metric keys of the hero row, and the live value feed. It never holds
CAN connection parameters or anything that changes what is sent to the bus.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import sys
import tempfile

from tools.can_dashboard import live_feed


SETTINGS_VERSION = 1
THEMES = ("dark", "light")
DEFAULT_THEME = "dark"
HERO_LIMIT = 12
FILE_NAME = "settings.json"


@dataclass(frozen=True)
class FeedSettings:
    """Live value feed: whether it publishes, where, and the load reference."""

    enabled: bool = False
    host: str = live_feed.DEFAULT_HOST
    port: int = live_feed.DEFAULT_PORT
    bfs_reference: int | None = None


@dataclass(frozen=True)
class Settings:
    theme: str = DEFAULT_THEME
    hero: tuple[str, ...] = ()
    feed: FeedSettings = FeedSettings()


def default_path(product_name, product_slug, *, platform=None, environ=None):
    """Return the per-user settings file of this platform."""
    platform = sys.platform if platform is None else platform
    environ = os.environ if environ is None else environ
    home = Path(environ.get("HOME") or Path.home())
    if platform == "darwin":
        return home / "Library/Application Support" / product_name / FILE_NAME
    if platform.startswith("win"):
        base = environ.get("APPDATA")
        root = Path(base) if base else home / "AppData/Roaming"
        return root / product_name / FILE_NAME
    base = environ.get("XDG_CONFIG_HOME")
    root = Path(base) if base else home / ".config"
    return root / product_slug / FILE_NAME


def normalize_hero(keys, catalog, *, limit=HERO_LIMIT):
    """Keep known metric keys once each, in order, up to the row limit."""
    known = set(catalog)
    result = []
    for key in keys:
        if isinstance(key, str) and key in known and key not in result:
            result.append(key)
        if len(result) == limit:
            break
    return tuple(result)


def normalize_feed(document):
    """Build feed settings from a decoded JSON value of any shape."""
    if not isinstance(document, dict):
        return FeedSettings()
    defaults = FeedSettings()
    host = document.get("host")
    if not isinstance(host, str) or not host.strip():
        host = defaults.host
    port = document.get("port")
    if type(port) is not int or not 1 <= port <= 0xFFFF:
        port = defaults.port
    reference = document.get("bfs_reference")
    try:
        reference = live_feed.validate_bfs_reference(reference)
    except ValueError:
        reference = None
    return FeedSettings(
        enabled=document.get("enabled") is True,
        host=host.strip(),
        port=port,
        bfs_reference=reference,
    )


def normalize(document, *, catalog, default_hero, limit=HERO_LIMIT):
    """Build settings from a decoded JSON document of any shape."""
    if not isinstance(document, dict):
        document = {}
    theme = document.get("theme")
    if theme not in THEMES:
        theme = DEFAULT_THEME
    hero = document.get("hero")
    if not isinstance(hero, list):
        hero = default_hero
    return Settings(
        theme,
        normalize_hero(hero, catalog, limit=limit),
        normalize_feed(document.get("feed")),
    )


def load(path, *, catalog, default_hero, limit=HERO_LIMIT):
    """Read the settings file; a missing or damaged file gives the defaults."""
    document = None
    if path is not None:
        try:
            document = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            document = None
    return normalize(
        document,
        catalog=catalog,
        default_hero=default_hero,
        limit=limit,
    )


def save(path, settings):
    """Replace the settings file atomically."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    document = {
        "version": SETTINGS_VERSION,
        "theme": settings.theme,
        "hero": list(settings.hero),
        "feed": {
            "enabled": settings.feed.enabled,
            "host": settings.feed.host,
            "port": settings.feed.port,
            "bfs_reference": settings.feed.bfs_reference,
        },
    }
    handle, temporary = tempfile.mkstemp(
        prefix=path.name + ".",
        suffix=".tmp",
        dir=path.parent,
    )
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            json.dump(document, stream, indent=2)
            stream.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise
    return path
