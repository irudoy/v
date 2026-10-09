"""Final source precedence and ordered unsigned limits of whole feedback."""
from tools.kb.tests.closed_loop_feedback_model import Memory


def selected_source(initial, final, rom, bank):
    old, new = Memory(initial, rom), Memory(final, rom)
    assert bank in (0, 1)
    if not old.b(0xffff88ec) & 0x10:
        return 'initial-preservation'
    if new.b(0xffff88be + bank) != 1:
        return 'unlatched-neutral'
    if new.b(0xffff89da + bank):
        return 'first-override'
    if new.b(0xffff89dc + bank):
        return 'second-override'
    if new.b(0xffff8958 + bank):
        return 'transition-neutral'
    if new.b(0xffff8964):
        return 'shared-backup'
    if new.b(0xffff8967 + bank):
        return 'disabled-neutral'
    if new.b(0xffff8965 + bank):
        return 'neutral-ramp'
    if new.b(0xffff8969 + bank):
        return 'elapsed-ramp'
    return 'baseline'


def source_equation(initial, final, rom, bank):
    """Use arithmetic selectors, not the procedural final-selection model."""
    old, new = Memory(initial, rom), Memory(final, rom)
    word = lambda at: new.w(at + 2 * bank)
    nz = lambda value: min(1, value)
    latch = 1 - min(1, abs(new.b(0xffff88be + bank) - 1))
    first = nz(new.b(0xffff89da + bank))
    second = nz(new.b(0xffff89dc + bank))
    transition = nz(new.b(0xffff8958 + bank))
    backup = nz(new.b(0xffff8964))
    disabled = nz(new.b(0xffff8967 + bank))
    neutral = nz(new.b(0xffff8965 + bank))
    elapsed = nz(new.b(0xffff8969 + bank))
    value = elapsed * word(0xffff8926) + (1 - elapsed) * word(0xffff2898)
    value = neutral * word(0xffff8922) + (1 - neutral) * value
    value = disabled * 25600 + (1 - disabled) * value
    value = backup * new.w(0xffff8920) + (1 - backup) * value
    value = transition * 25600 + (1 - transition) * value
    value = second * word(0xffff1628) + (1 - second) * value
    value = first * word(0xffff2a1e) + (1 - first) * value
    value = latch * value + (1 - latch) * 25600
    initialized = (old.b(0xffff88ec) >> 4) & 1
    raw = initialized * value + (1 - initialized) * old.w(0xffff88b0 + 2 * bank)
    return dict(raw=raw, output=max(new.w(0x8fc4), min(new.w(0x8fc6), raw)))
