"""Exact 1ME3B ignition lookup literals and their declared call windows.

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


class LiteralConsumerError(ValueError):
    """The image or a declaration changes a required lookup-call operand."""


def _word(data, address, size=2):
    if type(address) is not int or address < 0 or address + size > len(data):
        raise LiteralConsumerError('1ME3B lookup consumer is outside the image')
    return int.from_bytes(data[address:address + size], 'big')


def _require_long_load(data, address, register, literal):
    displacement = literal - ((address & ~3) + 4)
    if displacement % 4 or not 0 <= displacement <= 1020:
        raise LiteralConsumerError('1ME3B lookup consumer has an invalid PC-relative operand')
    expected = 0xD000 | register << 8 | displacement // 4
    if _word(data, address) != expected:
        raise LiteralConsumerError(f'1ME3B lookup consumer at {address:#x} changes its literal or register')


def _require_call(data, consumer, first_axis, second_axis):
    _require_long_load(data, consumer.load, consumer.register, consumer.literal)
    _require_long_load(data, consumer.load - 2, 4, consumer.table_pool)
    _require_long_load(data, consumer.load - 4, 5, consumer.second_axis_pool)
    axis_load = consumer.load - 6 if consumer.first_axis_load is None else consumer.first_axis_load
    _require_long_load(data, axis_load, 6, consumer.first_axis_pool)
    if consumer.first_axis_load is not None and (
            axis_load != consumer.load - 12
            or tuple(_word(data, axis_load + offset) for offset in (2, 4, 6))
            != (0x6D0C, 0xE022, 0x07CD)):
        raise LiteralConsumerError('1ME3B lookup consumer changes its intervening argument preparation')
    for site, value in ((consumer.table_pool, consumer.table),
                        (consumer.first_axis_pool, first_axis),
                        (consumer.second_axis_pool, second_axis)):
        if _word(data, site, 4) != value:
            raise LiteralConsumerError(f'1ME3B lookup argument pool at {site:#x} changes its value')
    if consumer.stack_store is None:
        if consumer.call != consumer.load + 2:
            raise LiteralConsumerError('1ME3B lookup consumer omits its intervening instructions')
    elif (consumer.stack_store != consumer.load + 2
            or consumer.call != consumer.load + 4
            or _word(data, consumer.stack_store) != 0x2FD2):
        raise LiteralConsumerError('1ME3B lookup consumer changes its fifth-argument store')
    if (_word(data, consumer.call) != 0x400B | consumer.register << 8
            or _word(data, consumer.call + 2) != 0x677D):
        raise LiteralConsumerError('1ME3B lookup consumer changes its indirect call or delay slot')


def require_consumers(data):
    """Bind declared call operands; grant no reachability or execution verdict."""
    data = bytes(data)
    for literal in LITERALS:
        if _word(data, literal, 4) != LOOKUP:
            raise LiteralConsumerError(f'1ME3B lookup literal at {literal:#x} changes its stock target')
    for consumer in CONSUMERS:
        _require_call(data, consumer, FIRST_AXIS, SECOND_AXIS)
    # This is an encoding inventory, not an instruction-boundary derivation.
    # Every match has a declared independently executable call window.
    found = []
    for address in range(0, len(data) - 1, 2):
        word = _word(data, address)
        if word >> 12 == 0xD:
            literal = (address & ~3) + 4 + (word & 0xFF) * 4
            if literal in LITERALS:
                found.append((address, literal, (word >> 8) & 15))
        elif word >> 12 == 9 or word >> 8 == 0xC7:
            if word >> 12 == 9:
                literal, size = address + 4 + (word & 0xFF) * 2, 2
            else:
                literal, size = (address & ~3) + 4 + (word & 0xFF) * 4, 1
            if any(literal < site + 4 and site < literal + size for site in LITERALS):
                raise LiteralConsumerError('1ME3B lookup literal has an undeclared narrow or address reference')
    expected = [(row.load, row.literal, row.register) for row in CONSUMERS]
    if found != expected:
        raise LiteralConsumerError('1ME3B lookup literal-load encodings differ from the declared windows')


def require_hooks(profile, adapter_entry):
    """Require every declared site to redirect to the same existing adapter."""
    hooks = tuple(hook for hook in profile.map_hooks if hook.key.startswith('ignition_lookup_'))
    if (type(adapter_entry) is not int or adapter_entry <= 0 or adapter_entry % 2
            or profile.rom != ROM or tuple(sorted(hook.address for hook in hooks)) != LITERALS
            or any(hook.stock != LOOKUP for hook in hooks)
            or any(hook.replacement != adapter_entry for hook in hooks)):
        raise LiteralConsumerError('1ME3B lookup hooks do not cover the exact declared literal sites')


def paired_state_loads(data, bases, hook_sites):
    """Bind each encoded state-base load to an explicit hooked lookup load.

    Multiple copies of a family base are allowed when each has this positive
    operand relation. No region address supplies an exemption. The caller
    separately binds stock identity, hook replacement and executable coverage.
    """
    data = bytes(data)
    if tuple(sorted(bases)) != tuple(sorted(STATE_BASES)) or tuple(sorted(hook_sites)) != STATE_LITERALS:
        raise LiteralConsumerError('1ME3B state lookup coverage changes its exact bases or hook sites')
    for site in hook_sites:
        if _word(data, site, 4) != STATE_LOOKUP:
            raise LiteralConsumerError('1ME3B state lookup hook changes its stock ABI target')
    for consumer in STATE_REGION_CONSUMERS:
        _require_call(data, consumer, 0x13DC6, 0x13DCE)
    found = []
    for base in bases:
        needle = base.to_bytes(4, 'big')
        sites = tuple(address for address in range(0, len(data) - 3, 4)
                      if data[address:address + 4] == needle)
        for site in sites:
            loaders = []
            for pc in range(max(0, site - 1024), site, 2):
                word = _word(data, pc)
                if word >> 12 == 0xD and (pc & ~3) + 4 + (word & 255) * 4 == site:
                    loaders.append(pc)
            if not loaders:
                raise LiteralConsumerError('1ME3B state-family base lacks its declared PC-relative consumer')
            for pc in loaders:
                if _word(data, pc) >> 8 != 0xD4:
                    raise LiteralConsumerError('1ME3B state-family base is not the lookup R4 argument')
                word = _word(data, pc + 2)
                lookup_site = ((pc + 2) & ~3) + 4 + (word & 255) * 4
                register = word >> 8 & 15
                if (word >> 12 != 0xD or lookup_site not in hook_sites
                        or _word(data, pc + 4) != 0x400B | register << 8
                        or _word(data, pc + 6) != 0x677D):
                    raise LiteralConsumerError('1ME3B state-family consumer bypasses its declared lookup hook')
                found.append((base, site, pc, lookup_site, pc + 4))
        if not sites:
            raise LiteralConsumerError('1ME3B state-family base has no literal site')
    return tuple(found)


def require_state_hooks(profile, adapter_entry):
    """Bind both state lookup pointers without excluding the earlier region."""
    keys = ('ignition_state_lookup', 'ignition_state_lookup_earlier')
    hooks = tuple(hook for hook in profile.map_hooks if hook.key in keys)
    if (type(adapter_entry) is not int or adapter_entry <= 0 or adapter_entry % 2
            or profile.rom != ROM or tuple(sorted(hook.address for hook in hooks)) != STATE_LITERALS
            or {hook.key for hook in hooks} != set(keys)
            or any(hook.stock != STATE_LOOKUP or hook.replacement != adapter_entry for hook in hooks)):
        raise LiteralConsumerError('1ME3B state lookup hooks do not cover both declared literal sites')
