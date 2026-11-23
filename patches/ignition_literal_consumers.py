"""Exact ignition lookup literals and their declared call windows.

These positive byte/operand obligations do not establish routine reachability
or exclude arbitrary computed consumers. Literal coverage must not depend on
classifying the earlier coordinator as unreachable.
"""

from dataclasses import dataclass


ROM = '1ME3B'
LOOKUP = 0x00029BA8
HOT = 0x0000A344
COLD = 0x0000A444
FIRST_AXIS = 0x00013716
SECOND_AXIS = 0x00013726
LITERALS = (0x00079420, 0x000796F4, 0x000799A4, 0x00079CAC, 0x00079E24)
STATE_LOOKUP = 0x000293D8
STATE_BASES = (0x0000A544, 0x0000A644, 0x0000A5C4, 0x0000A604)
STATE_LITERALS = (0x00079404, 0x00079994)


@dataclass(frozen=True)
class Consumer:
    load: int
    literal: int
    register: int
    call: int
    table_pool: int
    table: int
    first_axis_pool: int
    second_axis_pool: int
    first_axis_load: int | None = None
    stack_store: int | None = None

    @property
    def end(self):
        return self.call + 4

    @property
    def start(self):
        return self.load - 6 if self.first_axis_load is None else self.first_axis_load


# Each row states an observed MOV.L/JSR sequence explicitly. The register
# transfer is indirect; an intervening fifth-argument store is part of its
# window rather than an adjacent-call assumption.
CONSUMERS = (
    Consumer(0x79378, 0x79420, 1, 0x7937A, 0x7941C, COLD, 0x79414, 0x79418),
    Consumer(0x7939A, 0x79420, 13, 0x7939C, 0x7941C, COLD, 0x79414, 0x79418),
    Consumer(0x793CE, 0x79420, 1, 0x793D0, 0x79424, HOT, 0x79414, 0x79418),
    Consumer(0x7943A, 0x796F4, 13, 0x7943C, 0x796F0, HOT, 0x796E8, 0x796EC),
    Consumer(0x7951C, 0x796F4, 11, 0x7951E, 0x7971C, COLD, 0x796E8, 0x796EC),
    Consumer(0x79544, 0x796F4, 13, 0x79546, 0x7971C, COLD, 0x796E8, 0x796EC),
    Consumer(0x7957E, 0x796F4, 11, 0x79580, 0x7971C, COLD, 0x796E8, 0x796EC),
    Consumer(0x795A2, 0x796F4, 14, 0x795A4, 0x796F0, HOT, 0x796E8, 0x796EC),
    Consumer(0x795C4, 0x796F4, 11, 0x795C6, 0x7971C, COLD, 0x796E8, 0x796EC),
    Consumer(0x795E8, 0x796F4, 14, 0x795EC, 0x796F0, HOT, 0x796E8, 0x796EC,
             first_axis_load=0x795DC, stack_store=0x795EA),
    Consumer(0x79676, 0x796F4, 11, 0x79678, 0x796F0, HOT, 0x796E8, 0x796EC),
    Consumer(0x7969E, 0x796F4, 13, 0x796A0, 0x796F0, HOT, 0x796E8, 0x796EC),
    Consumer(0x796DA, 0x796F4, 11, 0x796DC, 0x796F0, HOT, 0x796E8, 0x796EC),
    Consumer(0x7975A, 0x799A4, 2, 0x7975C, 0x799A0, HOT, 0x79998, 0x7999C),
    Consumer(0x79A00, 0x79CAC, 1, 0x79A02, 0x79CA8, COLD, 0x79CA0, 0x79CA4),
    Consumer(0x79A22, 0x79CAC, 13, 0x79A24, 0x79CA8, COLD, 0x79CA0, 0x79CA4),
    Consumer(0x79A56, 0x79CAC, 1, 0x79A58, 0x79CB0, HOT, 0x79CA0, 0x79CA4),
    Consumer(0x79A78, 0x79CAC, 13, 0x79A7A, 0x79CB0, HOT, 0x79CA0, 0x79CA4),
    Consumer(0x79B5A, 0x79CAC, 11, 0x79B5C, 0x79CA8, COLD, 0x79CA0, 0x79CA4),
    Consumer(0x79B82, 0x79CAC, 13, 0x79B84, 0x79CA8, COLD, 0x79CA0, 0x79CA4),
    Consumer(0x79BBC, 0x79CAC, 11, 0x79BBE, 0x79CA8, COLD, 0x79CA0, 0x79CA4),
    Consumer(0x79BE0, 0x79CAC, 14, 0x79BE2, 0x79CB0, HOT, 0x79CA0, 0x79CA4),
    Consumer(0x79C02, 0x79CAC, 11, 0x79C04, 0x79CA8, COLD, 0x79CA0, 0x79CA4),
    Consumer(0x79C26, 0x79CAC, 14, 0x79C2A, 0x79CB0, HOT, 0x79CA0, 0x79CA4,
             first_axis_load=0x79C1A, stack_store=0x79C28),
    Consumer(0x79CF4, 0x79E24, 11, 0x79CF6, 0x79E20, HOT, 0x79E18, 0x79E1C),
    Consumer(0x79D1C, 0x79E24, 13, 0x79D1E, 0x79E20, HOT, 0x79E18, 0x79E1C),
    Consumer(0x79D58, 0x79E24, 11, 0x79D5A, 0x79E20, HOT, 0x79E18, 0x79E1C),
    Consumer(0x79D94, 0x79E24, 2, 0x79D96, 0x79E20, HOT, 0x79E18, 0x79E1C),
)

# The earlier region also loads state-family bases through 0x79404. Removing
# a region-based exclusion must cover this pointer as well as the 16x16 ones.
STATE_REGION_CONSUMERS = (
    Consumer(0x79220, 0x79404, 13, 0x79222, 0x79400, 0xA604, 0x793F8, 0x793FC),
    Consumer(0x79242, 0x79404, 13, 0x79244, 0x79400, 0xA604, 0x793F8, 0x793FC),
    Consumer(0x79276, 0x79404, 1, 0x79278, 0x79408, 0xA5C4, 0x793F8, 0x793FC),
    Consumer(0x79298, 0x79404, 13, 0x7929A, 0x79408, 0xA5C4, 0x793F8, 0x793FC),
    Consumer(0x792CC, 0x79404, 1, 0x792CE, 0x7940C, 0xA644, 0x793F8, 0x793FC),
    Consumer(0x792EE, 0x79404, 13, 0x792F0, 0x7940C, 0xA644, 0x793F8, 0x793FC),
    Consumer(0x79322, 0x79404, 1, 0x79324, 0x79410, 0xA544, 0x793F8, 0x793FC),
    Consumer(0x79344, 0x79404, 13, 0x79346, 0x79410, 0xA544, 0x793F8, 0x793FC),
)


# The two 1EK7A coordinators use a separate set of literal pools.
CONSUMERS_1EK7A = (
    Consumer(0x7AA60, 0x7AB08, 1, 0x7AA62, 0x7AB04, 0x0A4FC, 0x7AAFC, 0x7AB00),
    Consumer(0x7AA82, 0x7AB08, 13, 0x7AA84, 0x7AB04, 0x0A4FC, 0x7AAFC, 0x7AB00),
    Consumer(0x7AAB6, 0x7AB08, 1, 0x7AAB8, 0x7AB0C, 0x0A3FC, 0x7AAFC, 0x7AB00),
    Consumer(0x7AB22, 0x7ADDC, 13, 0x7AB24, 0x7ADD8, 0x0A3FC, 0x7ADD0, 0x7ADD4),
    Consumer(0x7AC04, 0x7ADDC, 11, 0x7AC06, 0x7AE04, 0x0A4FC, 0x7ADD0, 0x7ADD4),
    Consumer(0x7AC2C, 0x7ADDC, 13, 0x7AC2E, 0x7AE04, 0x0A4FC, 0x7ADD0, 0x7ADD4),
    Consumer(0x7AC66, 0x7ADDC, 11, 0x7AC68, 0x7AE04, 0x0A4FC, 0x7ADD0, 0x7ADD4),
    Consumer(0x7AC8A, 0x7ADDC, 14, 0x7AC8C, 0x7ADD8, 0x0A3FC, 0x7ADD0, 0x7ADD4),
    Consumer(0x7ACAC, 0x7ADDC, 11, 0x7ACAE, 0x7AE04, 0x0A4FC, 0x7ADD0, 0x7ADD4),
    Consumer(0x7ACD0, 0x7ADDC, 14, 0x7ACD4, 0x7ADD8, 0x0A3FC, 0x7ADD0, 0x7ADD4,
             first_axis_load=0x7ACC4, stack_store=0x7ACD2),
    Consumer(0x7AD5E, 0x7ADDC, 11, 0x7AD60, 0x7ADD8, 0x0A3FC, 0x7ADD0, 0x7ADD4),
    Consumer(0x7AD86, 0x7ADDC, 13, 0x7AD88, 0x7ADD8, 0x0A3FC, 0x7ADD0, 0x7ADD4),
    Consumer(0x7ADC2, 0x7ADDC, 11, 0x7ADC4, 0x7ADD8, 0x0A3FC, 0x7ADD0, 0x7ADD4),
    Consumer(0x7AE42, 0x7B08C, 2, 0x7AE44, 0x7B088, 0x0A3FC, 0x7B080, 0x7B084),
    Consumer(0x7B0E8, 0x7B394, 1, 0x7B0EA, 0x7B390, 0x0A4FC, 0x7B388, 0x7B38C),
    Consumer(0x7B10A, 0x7B394, 13, 0x7B10C, 0x7B390, 0x0A4FC, 0x7B388, 0x7B38C),
    Consumer(0x7B13E, 0x7B394, 1, 0x7B140, 0x7B398, 0x0A3FC, 0x7B388, 0x7B38C),
    Consumer(0x7B160, 0x7B394, 13, 0x7B162, 0x7B398, 0x0A3FC, 0x7B388, 0x7B38C),
    Consumer(0x7B242, 0x7B394, 11, 0x7B244, 0x7B390, 0x0A4FC, 0x7B388, 0x7B38C),
    Consumer(0x7B26A, 0x7B394, 13, 0x7B26C, 0x7B390, 0x0A4FC, 0x7B388, 0x7B38C),
    Consumer(0x7B2A4, 0x7B394, 11, 0x7B2A6, 0x7B390, 0x0A4FC, 0x7B388, 0x7B38C),
    Consumer(0x7B2C8, 0x7B394, 14, 0x7B2CA, 0x7B398, 0x0A3FC, 0x7B388, 0x7B38C),
    Consumer(0x7B2EA, 0x7B394, 11, 0x7B2EC, 0x7B390, 0x0A4FC, 0x7B388, 0x7B38C),
    Consumer(0x7B30E, 0x7B394, 14, 0x7B312, 0x7B398, 0x0A3FC, 0x7B388, 0x7B38C,
             first_axis_load=0x7B302, stack_store=0x7B310),
    Consumer(0x7B3DC, 0x7B50C, 11, 0x7B3DE, 0x7B508, 0x0A3FC, 0x7B500, 0x7B504),
    Consumer(0x7B404, 0x7B50C, 13, 0x7B406, 0x7B508, 0x0A3FC, 0x7B500, 0x7B504),
    Consumer(0x7B440, 0x7B50C, 11, 0x7B442, 0x7B508, 0x0A3FC, 0x7B500, 0x7B504),
    Consumer(0x7B47C, 0x7B50C, 2, 0x7B47E, 0x7B508, 0x0A3FC, 0x7B500, 0x7B504),
)

STATE_CONSUMERS_1EK7A = (
    Consumer(0x7A908, 0x7AAEC, 13, 0x7A90A, 0x7AAE8, 0x0A6BC, 0x7AAE0, 0x7AAE4),
    Consumer(0x7A92A, 0x7AAEC, 13, 0x7A92C, 0x7AAE8, 0x0A6BC, 0x7AAE0, 0x7AAE4),
    Consumer(0x7A95E, 0x7AAEC, 1, 0x7A960, 0x7AAF0, 0x0A67C, 0x7AAE0, 0x7AAE4),
    Consumer(0x7A980, 0x7AAEC, 13, 0x7A982, 0x7AAF0, 0x0A67C, 0x7AAE0, 0x7AAE4),
    Consumer(0x7A9B4, 0x7AAEC, 1, 0x7A9B6, 0x7AAF4, 0x0A6FC, 0x7AAE0, 0x7AAE4),
    Consumer(0x7A9D6, 0x7AAEC, 13, 0x7A9D8, 0x7AAF4, 0x0A6FC, 0x7AAE0, 0x7AAE4),
    Consumer(0x7AA0A, 0x7AAEC, 1, 0x7AA0C, 0x7AAF8, 0x0A5FC, 0x7AAE0, 0x7AAE4),
    Consumer(0x7AA2C, 0x7AAEC, 13, 0x7AA2E, 0x7AAF8, 0x0A5FC, 0x7AAE0, 0x7AAE4),
    Consumer(0x7AF30, 0x7B07C, 13, 0x7AF32, 0x7B0B4, 0x0A6BC, 0x7B0AC, 0x7B0B0),
    Consumer(0x7AF52, 0x7B07C, 13, 0x7AF54, 0x7B0B4, 0x0A6BC, 0x7B0AC, 0x7B0B0),
    Consumer(0x7AF86, 0x7B07C, 1, 0x7AF88, 0x7B0B8, 0x0A67C, 0x7B0AC, 0x7B0B0),
    Consumer(0x7AFA8, 0x7B07C, 13, 0x7AFAA, 0x7B0B8, 0x0A67C, 0x7B0AC, 0x7B0B0),
    Consumer(0x7AFDC, 0x7B07C, 1, 0x7AFDE, 0x7B0BC, 0x0A6FC, 0x7B0AC, 0x7B0B0),
    Consumer(0x7AFFE, 0x7B07C, 13, 0x7B000, 0x7B0BC, 0x0A6FC, 0x7B0AC, 0x7B0B0),
    Consumer(0x7B032, 0x7B07C, 1, 0x7B034, 0x7B0C0, 0x0A5FC, 0x7B0AC, 0x7B0B0),
    Consumer(0x7B054, 0x7B07C, 13, 0x7B056, 0x7B0C0, 0x0A5FC, 0x7B0AC, 0x7B0B0),
)

# The reference surface is called through the hooked state lookup in one
# coordinator and through an independent stock pool in the other.
REFERENCE_1EK7A = (
    Consumer(0x7AE2C, 0x7B07C, 2, 0x7AE2E, 0x7B078, 0x0A63C, 0x7B070, 0x7B074),
    Consumer(0x7B466, 0x7B528, 2, 0x7B468, 0x7B524, 0x0A63C, 0x7B51C, 0x7B520),
)


@dataclass(frozen=True)
class IgnitionBinding:
    variant: str
    lookup: int
    literals: tuple[int, ...]
    consumers: tuple[Consumer, ...]
    axes: tuple[int, int]
    state_lookup: int
    state_bases: tuple[int, ...]
    state_literals: tuple[int, ...]
    state_consumers: tuple[Consumer, ...]
    state_axes: tuple[int, int]
    stack_r7_displacement: int
    reference_consumers: tuple[Consumer, ...] = ()
    reference_axes: tuple[int, int] = (0, 0)


BINDINGS = {
    ROM: IgnitionBinding(
        'sh7059-1me3b', LOOKUP, LITERALS, CONSUMERS, (FIRST_AXIS, SECOND_AXIS),
        STATE_LOOKUP, STATE_BASES, STATE_LITERALS, STATE_REGION_CONSUMERS, (0x13DC6, 0x13DCE), 0x22,
    ),
    '1EK7A': IgnitionBinding(
        'sh7059-1ek7a', 0x2A73C, (0x7AB08, 0x7ADDC, 0x7B08C, 0x7B394, 0x7B50C),
        CONSUMERS_1EK7A, (0x13BC6, 0x13BD6), 0x29F6C, (0xA5FC, 0xA6FC, 0xA67C, 0xA6BC),
        (0x7AAEC, 0x7B07C), STATE_CONSUMERS_1EK7A, (0x1424E, 0x14256), 0x24,
        REFERENCE_1EK7A, (0x13BAE, 0x13BB6),
    ),
}


class LiteralConsumerError(ValueError):
    """The image or a declaration changes a required lookup-call operand."""


def binding_for_rom(rom):
    try:
        return BINDINGS[rom]
    except KeyError as error:
        raise LiteralConsumerError(f'{rom}: no exact ignition lookup consumer binding') from error


def _word(data, address, size=2):
    if type(address) is not int or address < 0 or address + size > len(data):
        raise LiteralConsumerError('ignition lookup consumer is outside the image')
    return int.from_bytes(data[address:address + size], 'big')


def _require_long_load(data, address, register, literal):
    displacement = literal - ((address & ~3) + 4)
    if displacement % 4 or not 0 <= displacement <= 1020:
        raise LiteralConsumerError('ignition lookup consumer has an invalid PC-relative operand')
    expected = 0xD000 | register << 8 | displacement // 4
    if _word(data, address) != expected:
        raise LiteralConsumerError(f'ignition lookup consumer at {address:#x} changes its literal or register')


def _require_call(data, consumer, axes, stack_r7_displacement=0):
    _require_long_load(data, consumer.load, consumer.register, consumer.literal)
    _require_long_load(data, consumer.load - 2, 4, consumer.table_pool)
    _require_long_load(data, consumer.load - 4, 5, consumer.second_axis_pool)
    axis_load = consumer.load - 6 if consumer.first_axis_load is None else consumer.first_axis_load
    _require_long_load(data, axis_load, 6, consumer.first_axis_pool)
    if consumer.first_axis_load is not None and (
            axis_load != consumer.load - 12
            or tuple(_word(data, axis_load + offset) for offset in (2, 4, 6))
            != (0x6D0C, 0xE000 | stack_r7_displacement, 0x07CD)):
        raise LiteralConsumerError('ignition lookup consumer changes its intervening argument preparation')
    for site, value in ((consumer.table_pool, consumer.table),
                        (consumer.first_axis_pool, axes[0]),
                        (consumer.second_axis_pool, axes[1])):
        if _word(data, site, 4) != value:
            raise LiteralConsumerError(f'ignition lookup argument pool at {site:#x} changes its value')
    if consumer.stack_store is None:
        if consumer.call != consumer.load + 2:
            raise LiteralConsumerError('ignition lookup consumer omits its intervening instructions')
    elif (consumer.stack_store != consumer.load + 2
            or consumer.call != consumer.load + 4
            or _word(data, consumer.stack_store) != 0x2FD2):
        raise LiteralConsumerError('ignition lookup consumer changes its fifth-argument store')
    if (_word(data, consumer.call) != 0x400B | consumer.register << 8
            or _word(data, consumer.call + 2) != 0x677D):
        raise LiteralConsumerError('ignition lookup consumer changes its indirect call or delay slot')


def require_consumers(data, rom=ROM):
    """Bind declared call operands; grant no reachability or execution verdict."""
    data = bytes(data)
    binding = binding_for_rom(rom)
    _require_lookup_words(data, binding.literals, binding.lookup)
    for consumer in binding.consumers:
        _require_call(data, consumer, binding.axes, binding.stack_r7_displacement)
    _require_literal_loads(data, binding.literals, binding.consumers)


def _require_lookup_words(data, literals, lookup):
    for literal in literals:
        if _word(data, literal, 4) != lookup:
            raise LiteralConsumerError(f'ignition lookup literal at {literal:#x} changes its stock target')


def _require_literal_loads(data, literals, consumers):
    # The encoding inventory is independent of instruction-boundary recovery.
    found = []
    for address in range(0, len(data) - 1, 2):
        word = _word(data, address)
        if word >> 12 == 0xD:
            literal = (address & ~3) + 4 + (word & 0xFF) * 4
            if literal in literals:
                found.append((address, literal, (word >> 8) & 15))
        elif word >> 12 == 9 or word >> 8 == 0xC7:
            if word >> 12 == 9:
                literal, size = address + 4 + (word & 0xFF) * 2, 2
            else:
                literal, size = (address & ~3) + 4 + (word & 0xFF) * 4, 1
            if any(literal < site + 4 and site < literal + size for site in literals):
                raise LiteralConsumerError('ignition lookup literal has an undeclared narrow or address reference')
    expected = sorted((row.load, row.literal, row.register) for row in consumers)
    if found != expected:
        raise LiteralConsumerError('ignition lookup literal-load encodings differ from the declared windows')


def require_hooks(profile, adapter_entry):
    """Require every declared site to redirect to the same existing adapter."""
    binding = binding_for_rom(profile.rom)
    hooks = tuple(hook for hook in profile.map_hooks if hook.key.startswith('ignition_lookup_'))
    if (type(adapter_entry) is not int or adapter_entry <= 0 or adapter_entry % 2
            or tuple(sorted(hook.address for hook in hooks)) != binding.literals
            or any(hook.stock != binding.lookup for hook in hooks)
            or any(hook.replacement != adapter_entry for hook in hooks)):
        raise LiteralConsumerError('ignition lookup hooks do not cover the exact declared literal sites')


def paired_state_loads(data, bases, hook_sites, rom=ROM):
    """Bind each encoded state-base load to an explicit hooked lookup load.

    Multiple copies of a family base are allowed when each has this positive
    operand relation. No region address supplies an exemption. The caller
    separately binds stock identity, hook replacement and executable coverage.
    """
    data = bytes(data)
    binding = binding_for_rom(rom)
    if (tuple(sorted(bases)) != tuple(sorted(binding.state_bases))
            or tuple(sorted(hook_sites)) != binding.state_literals):
        raise LiteralConsumerError('ignition state lookup coverage changes its exact bases or hook sites')
    _require_lookup_words(data, hook_sites, binding.state_lookup)
    for consumer in binding.state_consumers:
        _require_call(data, consumer, binding.state_axes)
    if binding.reference_consumers:
        for consumer in binding.reference_consumers:
            _require_call(data, consumer, binding.reference_axes)
        literals = set(hook_sites) | {row.literal for row in binding.reference_consumers}
        stock_sites = set(_aligned_literal_sites(data, binding.state_lookup))
        if stock_sites != literals:
            raise LiteralConsumerError('ignition state lookup changes its stock literal inventory')
        _require_literal_loads(data, literals, (*binding.state_consumers, *binding.reference_consumers))
    found = []
    for base in bases:
        sites = tuple(_aligned_literal_sites(data, base))
        for site in sites:
            loaders = []
            for pc in range(max(0, site - 1024), site, 2):
                word = _word(data, pc)
                if word >> 12 == 0xD and (pc & ~3) + 4 + (word & 255) * 4 == site:
                    loaders.append(pc)
            if not loaders:
                raise LiteralConsumerError('ignition state-family base lacks its declared PC-relative consumer')
            for pc in loaders:
                if _word(data, pc) >> 8 != 0xD4:
                    raise LiteralConsumerError('ignition state-family base is not the lookup R4 argument')
                word = _word(data, pc + 2)
                lookup_site = ((pc + 2) & ~3) + 4 + (word & 255) * 4
                register = word >> 8 & 15
                if (word >> 12 != 0xD or lookup_site not in hook_sites
                        or _word(data, pc + 4) != 0x400B | register << 8
                        or _word(data, pc + 6) != 0x677D):
                    raise LiteralConsumerError('ignition state-family consumer bypasses its declared lookup hook')
                found.append((base, site, pc, lookup_site, pc + 4))
        if not sites:
            raise LiteralConsumerError('ignition state-family base has no literal site')
    return tuple(found)


def _aligned_literal_sites(data, value):
    needle = value.to_bytes(4, 'big')
    position = data.find(needle)
    while position != -1:
        if position % 4 == 0:
            yield position
        position = data.find(needle, position + 1)


def require_state_hooks(profile, adapter_entry):
    """Bind both state lookup pointers without excluding the earlier region."""
    binding = binding_for_rom(profile.rom)
    keys = ('ignition_state_lookup', 'ignition_state_lookup_earlier')
    hooks = tuple(hook for hook in profile.map_hooks if hook.key in keys)
    if (type(adapter_entry) is not int or adapter_entry <= 0 or adapter_entry % 2
            or tuple(sorted(hook.address for hook in hooks)) != binding.state_literals
            or {hook.key for hook in hooks} != set(keys)
            or any(hook.stock != binding.state_lookup or hook.replacement != adapter_entry for hook in hooks)):
        raise LiteralConsumerError('ignition state lookup hooks do not cover both declared literal sites')
