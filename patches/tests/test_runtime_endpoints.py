"""Runtime endpoint classification is scoped to the selected ROM."""

from dataclasses import replace
from functools import lru_cache

import pytest

from patches import runtime_endpoints
from patches import runtime_targets


@lru_cache(maxsize=None)
def target(rom):
    return runtime_targets.load_runtime_target(rom)


def installed_rolling_layer(rom, configuration):
    """Stock bytes with the current Rolling Launch units, hooks and DIDs."""
    layout = target(rom).rolling_layout
    data = bytearray(target(rom).stock_image.data)
    for unit in layout.assembly_units:
        data[unit.span.start : unit.span.end] = target(rom).rolling_payloads[unit.key]
    for hook in layout.hooks:
        data[hook.address : hook.address + hook.width] = hook.replacement.to_bytes(
            hook.width, layout.byte_order
        )
    for item in layout.diagnostics:
        data[item.pointer_address : item.pointer_address + 4] = item.target.to_bytes(
            4, layout.byte_order
        )
    data[layout.configuration.start : layout.configuration.end] = configuration
    return bytes(data)


def test_signature_keys_are_unique_and_name_supported_roms():
    keys = [endpoint.key for endpoint in runtime_endpoints.HISTORICAL_ROLLING_ENDPOINTS]
    assert len(keys) == len(set(keys))
    for endpoint in runtime_endpoints.HISTORICAL_ROLLING_ENDPOINTS:
        assert endpoint.roms
        assert set(endpoint.roms) <= set(runtime_targets.SUPPORTED_ROMS)


@pytest.mark.parametrize("rom", runtime_targets.EXACT_ROMS)
def test_every_signature_of_a_rom_describes_its_layout(rom):
    endpoints = runtime_endpoints.historical_endpoints(rom)
    assert endpoints
    assert all(rom in endpoint.roms for endpoint in endpoints)
    for endpoint in endpoints:
        runtime_endpoints._endpoint_binding(endpoint, target(rom).rolling_layout)


@pytest.mark.parametrize("rom", runtime_targets.RELOCATED_ROMS)
def test_a_relocated_rom_has_no_rolling_launch_endpoint(rom):
    assert target(rom).rolling_layout is None
    assert not runtime_endpoints.historical_endpoints(rom)


@pytest.mark.parametrize("rom", runtime_targets.EXACT_ROMS)
def test_corrupt_configuration_is_a_named_state_on_every_rom(rom):
    layout = target(rom).rolling_layout
    corrupt = bytes([0xA5]) * layout.configuration.size
    source = installed_rolling_layer(rom, corrupt)
    with pytest.raises(
        runtime_endpoints.EndpointError,
        match="partial or unknown Rolling Launch state",
    ):
        runtime_endpoints.require_coherent_rolling_endpoint(
            source, layout, target(rom).rolling_payloads, "corrupt", rom
        )


def test_signature_that_does_not_describe_its_layout_is_internal(monkeypatch):
    jk08a = runtime_endpoints.historical_endpoints("JK08A")[0]
    hooks = dict(jk08a.hook_values)
    moved = next(iter(hooks))
    misnamed = replace(
        jk08a, hook_values=tuple({**hooks, moved: 0x00FFFF00}.items())
    )
    monkeypatch.setattr(runtime_endpoints, "HISTORICAL_ROLLING_ENDPOINTS", (misnamed,))
    layout = target("JK08A").rolling_layout
    source = installed_rolling_layer("JK08A", bytes([0xA5]) * layout.configuration.size)
    with pytest.raises(runtime_endpoints.EndpointError,
                       match="does not describe the selected layout"):
        runtime_endpoints.require_coherent_rolling_endpoint(
            source, layout, target("JK08A").rolling_payloads, "misnamed", "JK08A"
        )
