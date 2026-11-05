"""Images that carry a registered historical Rolling Launch endpoint.

Each image starts from a current build, restores the bytes below the current
Rolling Launch layer, and places the units, hook words, DID slots and record
of one endpoint at the endpoint's own addresses. Only the restoration reads
the current layout, so the images stay valid when that layout drops or moves
units, hooks, DIDs or record spans.
"""

from functools import lru_cache
import hashlib
from pathlib import Path
import tomllib

from patches import runtime_endpoints


FIXTURES = Path(__file__).parent / "data"
# Fixtures with the complete non-erased units of a registered endpoint.
UNIT_FIXTURES = {
    "schema-4-uniform-gain": "rolling-launch-schema-4.toml",
    "schema-5-fixed-trim": "rolling-launch-schema-5.toml",
}


def sha256(data):
    return hashlib.sha256(bytes(data)).hexdigest()


@lru_cache(maxsize=None)
def fixture(key):
    """Return the unit payloads and built-in record of a fixture endpoint."""
    with (FIXTURES / UNIT_FIXTURES[key]).open("rb") as source:
        raw = tomllib.load(source)
    units = {
        name: bytes.fromhex("".join(text.split()))
        for name, text in raw["units"].items()
    }
    return units, bytes.fromhex(raw["configuration"])


def record(key):
    """Return the built-in record of a fixture endpoint."""
    return fixture(key)[1]


@lru_cache(maxsize=1)
def fixture_payloads():
    """Return every fixture unit payload by its SHA-256."""
    return {
        sha256(payload): payload
        for key in UNIT_FIXTURES
        for payload in fixture(key)[0].values()
    }


def _endpoint(endpoint):
    if isinstance(endpoint, str):
        return runtime_endpoints.historical_endpoint(endpoint)
    return endpoint


def unit(endpoint, name):
    """Return the placed unit ``name`` of an endpoint."""
    return next(item for item in _endpoint(endpoint).units if item.key == name)


def hook(endpoint, name):
    """Return the placed hook ``name`` of an endpoint."""
    return next(item for item in _endpoint(endpoint).hooks if item.key == name)


def unit_payload(endpoint, name, payloads=()):
    """Return the payload of one endpoint unit from ``payloads`` or the
    fixtures, matched by its SHA-256."""
    placed = unit(endpoint, name)
    library = dict(fixture_payloads())
    library.update((sha256(payload), bytes(payload)) for payload in payloads)
    erased = bytes([0xFF]) * (placed.end - placed.start)
    if sha256(erased) == placed.sha256:
        return erased
    if placed.sha256 not in library:
        raise ValueError(
            f"no payload for unit {name} of {_endpoint(endpoint).key}"
        )
    return library[placed.sha256]


def telemetry_hooks(target, data):
    """Return the hook words whose value the CAN telemetry layer holds."""
    layout = target.telemetry_layout
    return {
        item.address
        for item in layout.hooks
        if int.from_bytes(
            data[item.address : item.address + item.width], layout.byte_order
        ) == item.replacement
    }


def without_rolling_layer(target, data):
    """Return ``data`` with the bytes below the current Rolling Launch layer:
    erased claimed ROM and records, and the stock hook words and DID slots.
    A hook word that the CAN telemetry layer holds keeps its value."""
    layout = target.rolling_layout
    owned = telemetry_hooks(target, data)
    source = bytearray(data)
    for span in (
        *layout.claimed_rom_ranges,
        layout.configuration,
        *layout.retired_configuration_spans,
    ):
        source[span.start : span.end] = bytes([0xFF]) * span.size
    for item in layout.hooks:
        if item.address not in owned:
            source[item.address : item.address + item.width] = item.stock.to_bytes(
                item.width, layout.byte_order
            )
    for item in layout.diagnostics:
        source[item.pointer_address : item.pointer_address + 4] = item.stock.to_bytes(
            4, layout.byte_order
        )
    return source


def with_endpoint(target, data, endpoint, configuration, payloads=()):
    """Return ``data`` with a registered endpoint, a key or a signature, in
    place of the current Rolling Launch layer. Each non-erased unit payload
    comes from ``payloads`` or the fixtures by its SHA-256. A hook word that
    the CAN telemetry layer holds keeps its value."""
    endpoint = _endpoint(endpoint)
    byte_order = endpoint.addresses.byte_order
    owned = telemetry_hooks(target, data)
    source = without_rolling_layer(target, data)
    for placed in endpoint.units:
        source[placed.start : placed.end] = unit_payload(
            endpoint, placed.key, payloads
        )
    for placed in endpoint.hooks:
        if placed.address not in owned:
            source[placed.address : placed.address + placed.width] = (
                placed.value.to_bytes(placed.width, byte_order)
            )
    for item in endpoint.dids:
        source[item.pointer_address : item.pointer_address + 4] = (
            item.target.to_bytes(4, byte_order)
        )
    span = endpoint.record
    if len(configuration) != span.size:
        raise ValueError(
            f"record of {endpoint.key} has {len(configuration)} bytes, "
            f"expected {span.size}"
        )
    source[span.start : span.end] = configuration
    return source
