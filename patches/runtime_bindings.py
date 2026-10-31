"""Read generated numeric runtime bindings without loading the knowledge model."""

from functools import lru_cache
from pathlib import Path
import tomllib


DEFAULT_BINDINGS = Path(__file__).with_name("runtime-bindings.toml")
CANONICAL = "7mfk"


class RuntimeBindingsError(ValueError):
    """A runtime binding projection is absent or malformed."""


def _integer(value, context, maximum=0xFFFFFFFF):
    if type(value) is not int or not 0 <= value <= maximum:
        raise RuntimeBindingsError(f"{context}: expected an integer in 0..{maximum}")


def _table(value, context):
    if not isinstance(value, dict) or not value:
        raise RuntimeBindingsError(f"{context}: expected a nonempty table")
    return value


@lru_cache(maxsize=None)
def load(path=DEFAULT_BINDINGS):
    """Load and validate one complete machine projection."""
    try:
        with Path(path).open("rb") as source:
            found = tomllib.load(source)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise RuntimeBindingsError(f"runtime bindings cannot be loaded: {path}: {error}") from error
    expected = {"schema_version", "canonical_layout", "images", "canonical_symbols",
                "map_hook_keys", "ignition_state_template", "layouts"}
    if set(found) != expected or type(found.get("schema_version")) is not int or found["schema_version"] != 1:
        raise RuntimeBindingsError(f"{path}: unsupported runtime binding schema")
    if found["canonical_layout"] != CANONICAL:
        raise RuntimeBindingsError(f"{path}: canonical layout differs from {CANONICAL}")
    layouts = _table(found["layouts"], "layouts")
    if CANONICAL not in layouts:
        raise RuntimeBindingsError("layouts: canonical layout is absent")
    required = {"ascd_main_bit", "knock_surface_bit", "knock_surface_address"}
    fuel_cut = {"fuel_cut_active_bit", "fuel_cut_address"}
    for name, row in layouts.items():
        _table(row, f"layouts.{name}")
        extra = set(row) - required
        if (not required <= set(row) or extra - fuel_cut - {"fuel_inhibit_mask"}
                or (extra and not fuel_cut <= extra)):
            raise RuntimeBindingsError(f"layouts.{name}: runtime fields differ")
        for key, value in row.items():
            _integer(value, f"layouts.{name}.{key}", 7 if key.endswith("_bit") else 0xFFFFFFFF)
    for image, layout_id in _table(found["images"], "images").items():
        if not isinstance(image, str) or not isinstance(layout_id, str) or layout_id not in layouts:
            raise RuntimeBindingsError(f"images.{image}: unknown layout")
    symbols_by_feature = _table(found["canonical_symbols"], "canonical_symbols")
    if set(symbols_by_feature) != {"map_switching", "rolling_launch", "can_telemetry"}:
        raise RuntimeBindingsError("canonical_symbols: feature coverage differs")
    for feature, symbols in symbols_by_feature.items():
        for key, value in _table(symbols, f"canonical_symbols.{feature}").items():
            _integer(value, f"canonical_symbols.{feature}.{key}")
    if set(_table(found["map_hook_keys"], "map_hook_keys")) != set(layouts):
        raise RuntimeBindingsError("map_hook_keys: layout coverage differs")
    for layout_id, hooks in found["map_hook_keys"].items():
        if not isinstance(hooks, dict):
            raise RuntimeBindingsError(f"map_hook_keys.{layout_id}: expected a table")
        for address, key in hooks.items():
            if (len(address) != 8 or any(char not in "0123456789abcdef" for char in address)
                    or not isinstance(key, str) or not key):
                raise RuntimeBindingsError(f"map_hook_keys.{layout_id}: invalid hook binding")
    for key, pair in _table(found["ignition_state_template"], "ignition_state_template").items():
        if not isinstance(pair, list) or len(pair) != 2:
            raise RuntimeBindingsError(f"ignition_state_template.{key}: expected table and pointer addresses")
        for value in pair:
            _integer(value, f"ignition_state_template.{key}")
    return found


def layout_of(image):
    try:
        return load()["images"][image]
    except KeyError as error:
        raise RuntimeBindingsError(f"image {image}: no runtime layout") from error


def layout(layout_id):
    try:
        return dict(load()["layouts"][layout_id])
    except KeyError as error:
        raise RuntimeBindingsError(f"layout {layout_id}: no runtime bindings") from error


def canonical_symbols(feature):
    try:
        return dict(load()["canonical_symbols"][feature])
    except KeyError as error:
        raise RuntimeBindingsError(f"feature {feature}: no canonical runtime symbols") from error


def map_hook_keys(image):
    return {int(address, 16): key for address, key in
            load()["map_hook_keys"][layout_of(image)].items()}


def ignition_state_template():
    return {key: tuple(pair) for key, pair in load()["ignition_state_template"].items()}
