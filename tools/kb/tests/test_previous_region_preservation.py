"""Historical checks reject changed descriptors, order, observers and fixture bytes."""

from dataclasses import replace
import importlib

import pytest


@pytest.mark.parametrize('name', [
    'closed_loop_publication_contract', 'closed_loop_conversion_contract',
    'closed_loop_adjustment_contract', 'closed_loop_feedback_contract',
    'fuel_cut_consumer_contract', 'main_rpm_fuel_cut_contract', 'vehicle_speed_fuel_cut_contract',
])
@pytest.mark.parametrize('mutation', ['descriptor', 'remove', 'reorder', 'fixture', 'observer'])
def test_appended_witnesses_do_not_allow_a_changed_historical_prefix(monkeypatch, name, mutation):
    contract = importlib.import_module('tools.kb.tests.' + name)
    module = contract.publication.stock_module()
    original = module.REGIONS
    monkeypatch.setattr(contract.publication, 'stock_module', lambda: module)
    if mutation == 'descriptor':
        changed = (replace(original[0], cases=original[0].cases + 1), *original[1:])
        monkeypatch.setattr(module, 'REGIONS', changed)
    elif mutation == 'remove':
        monkeypatch.setattr(module, 'REGIONS', original[1:])
    elif mutation == 'reorder':
        monkeypatch.setattr(module, 'REGIONS', (original[1], original[0], *original[2:]))
    elif mutation == 'observer':
        held = contract.contracts()
        observers = held.get('previous_observers', held.get('held_observers'))
        key = next(iter(observers))
        changed = {**module.REGION_OBSERVERS, key: 'changed-preserved-observer.s'}
        monkeypatch.setattr(module, 'REGION_OBSERVERS', changed)
    else:
        build = module.build_fixture

        def changed_fixture(region, image):
            data = bytearray(build(region, image))
            if region.key == original[0].key:
                data[0] ^= 1
            return bytes(data)

        monkeypatch.setattr(module, 'build_fixture', changed_fixture)
    with pytest.raises(AssertionError):
        function = {'fuel_cut_consumer_contract': 'all_regions_contract',
                    'main_rpm_fuel_cut_contract': 'earlier_region_contract',
                    'vehicle_speed_fuel_cut_contract': 'earlier_region_contract'}.get(name, 'previous_regions_contract')
        getattr(contract, function)()
