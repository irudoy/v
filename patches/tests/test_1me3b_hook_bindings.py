import copy
import tomllib

import pytest

from patches import ignition_literal_consumers, rom_address_profiles, runtime_targets
from tools import rom_homology


MISSING_EARLIER_HOOKS = (
    "ignition_lookup_3", "ignition_lookup_4", "ignition_lookup_5",
    "ignition_state_lookup_earlier",
)


def profile_document():
    with rom_address_profiles.DEFAULT_REGISTRY.open("rb") as source:
        return tomllib.load(source)


def test_1me3b_profile_binds_every_declared_lookup_literal():
    profile = rom_address_profiles.profile_for_rom("1ME3B")
    target = runtime_targets.load_runtime_target("1ME3B")
    adapter = target.map_layout.code_region_by_key["ignition_adapter"].entry
    ignition_literal_consumers.require_hooks(profile, adapter)
    ignition_literal_consumers.require_state_hooks(
        profile, profile.ignition_state_storage.adapter.start)
    data = rom_homology.load_images()["1ME3B"].data
    rom_address_profiles.validate_stock_profile(profile, data)


@pytest.mark.parametrize("key", MISSING_EARLIER_HOOKS)
def test_1me3b_parser_rejects_each_missing_earlier_hook(key):
    document = profile_document()
    del document["profile"]["1ME3B"]["map_hooks"][key]
    with pytest.raises(rom_address_profiles.AddressProfileError) as caught:
        rom_address_profiles.parse_registry(document, "controlled current projection")
    assert "[profile.1ME3B].map_hooks" in str(caught.value)
    assert f"missing=['{key}']" in str(caught.value)


def test_earlier_state_hook_is_rejected_on_a_variant_without_it():
    document = profile_document()
    hook = document["profile"]["1ME3B"]["map_hooks"]["ignition_state_lookup_earlier"]
    document["profile"]["JK78C"]["map_hooks"]["ignition_state_lookup_earlier"] = copy.deepcopy(hook)
    with pytest.raises(rom_address_profiles.AddressProfileError) as caught:
        rom_address_profiles.parse_registry(document, "controlled current projection")
    assert "[profile.JK78C].map_hooks" in str(caught.value)
    assert "extra=['ignition_state_lookup_earlier']" in str(caught.value)


def test_1me3b_image_stages_match_the_current_composition_locks():
    target = runtime_targets.load_runtime_target("1ME3B")
    locks = runtime_targets.load_payload_locks()["1ME3B"]
    runtime_targets.validate_relocated_target(target, locks)
