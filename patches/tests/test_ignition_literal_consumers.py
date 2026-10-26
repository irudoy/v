"""Refuse C5 operand changes independently of the region's reachability."""

from types import SimpleNamespace

import pytest

from patches import ignition_literal_consumers as contract
from tools.mapkit import rom as romkit


@pytest.fixture(scope='module')
def stock():
    return bytes(romkit.load('1ME3B').data)


def changed(data, address, value, size=2):
    result = bytearray(data)
    result[address:address + size] = value.to_bytes(size, 'big')
    return result


def test_exact_literal_call_contexts(stock):
    contract.require_consumers(stock)
    assert contract.CONSUMERS[0].table == contract.COLD
    assert contract.CONSUMERS[-1].table == contract.HOT
    assert {row.stack_store for row in contract.CONSUMERS if row.stack_store is not None} == {
        0x795EA, 0x79C28,
    }


@pytest.mark.parametrize('address,value,size', (
    (0x79420, 0x000293D8, 4),  # A different lookup ABI is not interchangeable.
    (0x79378, 0xD229, 2),       # The loaded register must be the actual call operand.
    (0x7937A, 0x420B, 2),
    (0x7937C, 0x677C, 2),       # A byte extension changes the call argument.
    (0x7941C, 0x0000A344, 4),  # The actual family is part of the call context.
    (0x79414, 0x00013726, 4),
    (0x795EA, 0x2FC2, 2),      # The fifth argument is written before the indirect call.
    (0x795DE, 0x6D0D, 2),
    (0x79C28, 0x0009, 2),
    (0x79D96, 0x412B, 2),      # JMP does not supply the JSR return path.
))
def test_changed_literal_or_call_abi_is_refused(stock, address, value, size):
    contract.require_consumers(stock)
    with pytest.raises(contract.LiteralConsumerError):
        contract.require_consumers(changed(stock, address, value, size))


def test_an_extra_reference_inside_the_earlier_region_is_refused(stock):
    contract.require_consumers(stock)
    # 0x793de is outside the declared call windows. Its location inside the
    # earlier region must not hide a new MOV.L reference to 0x79420.
    with pytest.raises(contract.LiteralConsumerError, match='encodings differ'):
        contract.require_consumers(changed(stock, 0x793DE, 0xD010))


@pytest.mark.parametrize('instruction', (0x901F, 0xC710))
def test_narrow_or_address_reference_requires_its_own_consumer(stock, instruction):
    contract.require_consumers(stock)
    with pytest.raises(contract.LiteralConsumerError, match='narrow or address reference'):
        contract.require_consumers(changed(stock, 0x793DE, instruction))


def hooks():
    return tuple(SimpleNamespace(key=f'ignition_lookup_{index}', address=site,
        stock=contract.LOOKUP, replacement=0x13C340)
        for index, site in enumerate(contract.LITERALS, 1))


@pytest.mark.parametrize('damage', ('missing', 'duplicate', 'lookup', 'adapter', 'all_adapters', 'layout'))
def test_literal_coverage_has_no_dead_region_exemption(damage):
    original = hooks()
    adapter = 0x13C340
    contract.require_hooks(SimpleNamespace(rom=contract.ROM, map_hooks=original), adapter)
    altered = list(original)
    rom = contract.ROM
    if damage == 'missing':
        altered.pop(0)
    elif damage == 'duplicate':
        altered.append(original[0])
    elif damage == 'layout':
        rom = '1ND0A'
    elif damage == 'all_adapters':
        altered = [SimpleNamespace(**{**vars(row), 'replacement': adapter + 4}) for row in altered]
    else:
        values = vars(altered[0]).copy()
        values['stock' if damage == 'lookup' else 'replacement'] ^= 4
        altered[0] = SimpleNamespace(**values)
    with pytest.raises(contract.LiteralConsumerError):
        contract.require_hooks(SimpleNamespace(rom=rom, map_hooks=tuple(altered),
            ignition_unreferenced_routine=SimpleNamespace(start=0x791A4, end=0x797CC)), adapter)


def test_both_state_lookup_pools_have_positive_call_relations(stock):
    rows = contract.paired_state_loads(stock, contract.STATE_BASES, contract.STATE_LITERALS)
    assert {row[0] for row in rows} == set(contract.STATE_BASES)
    assert {row[3] for row in rows} == set(contract.STATE_LITERALS)
    assert {(row.load - 2, row.literal, row.call) for row in contract.STATE_REGION_CONSUMERS} <= {
        (row[2], row[3], row[4]) for row in rows
    }


@pytest.mark.parametrize('address,value,size', (
    (0x79404, 0x00029BA8, 4),
    (0x7921E, 0xD51F, 2),
    (0x79220, 0xD12E, 2),
    (0x79222, 0x410B, 2),
    (0x79224, 0x677C, 2),
    (0x793F8, 0x00013DCE, 4),
    (0x79E3C, 0x0000A544, 4),
))
def test_state_pool_changes_need_positive_bound_consumers(stock, address, value, size):
    with pytest.raises(contract.LiteralConsumerError):
        contract.paired_state_loads(changed(stock, address, value, size),
                                    contract.STATE_BASES, contract.STATE_LITERALS)


@pytest.mark.parametrize('damage', ('missing', 'duplicate', 'stock', 'adapter', 'key'))
def test_state_lookup_coverage_cannot_exclude_the_earlier_region(damage):
    adapter = 0x13E080
    rows = [SimpleNamespace(key=key, address=site, stock=contract.STATE_LOOKUP,
                            replacement=adapter) for key, site in (
        ('ignition_state_lookup_earlier', 0x79404), ('ignition_state_lookup', 0x79994))]
    contract.require_state_hooks(SimpleNamespace(rom='1ME3B', map_hooks=rows), adapter)
    if damage == 'missing':
        rows.pop(0)
    elif damage == 'duplicate':
        rows.append(rows[0])
    else:
        values = vars(rows[0]).copy()
        if damage == 'key':
            values['key'] = 'ignition_state_lookup_uncovered'
        else:
            values['stock' if damage == 'stock' else 'replacement'] ^= 4
        rows[0] = SimpleNamespace(**values)
    with pytest.raises(contract.LiteralConsumerError):
        contract.require_state_hooks(SimpleNamespace(rom='1ME3B', map_hooks=rows), adapter)
