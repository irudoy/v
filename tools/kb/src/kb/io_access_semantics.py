"""Separate mailbox-field, descriptor-stride and captured-word equations."""


def mailbox(record, slot, prior, before):
    if (type(record) is not bytes or len(record) != 4 or type(slot) is not int or not 0 <= slot < 30
            or type(prior) is not int or not 0 <= prior <= 0xFFFFFFFF
            or type(before) is not bytes or len(before) != 65536):
        raise ValueError('the mailbox equation lacks its exact slot, record or native-storage state')
    kind, dlc, first, second = record
    format_bits = 2 if kind in (1, 2) else 0 if kind in (3, 4) else 7
    identifier = (((first << 8) | second) >> 1) & 0x7FF0
    words = ((0, identifier), (2, 0), (4, (format_bits << 8) | dlc), (6, 0), (16, 0), (18, 0))
    native = 0xFFFFD920 + slot * 32
    after = bytearray(before)
    for offset, value in words:
        address = (native & 65535) + offset
        after[address:address + 2] = value.to_bytes(2, 'big')
    mask = prior | (1 << (slot + 1)) if kind in (2, 4) else prior
    return dict(memory=bytes(after), address=native, words=words, mask=mask)


def capture(param, word):
    if any(type(value) is not int or not 0 <= value <= 0xFFFFFFFF for value in (param, word)):
        raise ValueError('the captured-word equation needs two exact uint32 inputs')
    return dict(raw_word=word, low_word=word & 65535, packed=((param & 65535) << 16) | (word & 65535))


def monitor(table, selector, word):
    if (type(table) is not bytes or len(table) != 392 or type(selector) is not int or selector not in (0, 6)
            or type(word) is not int or not 0 <= word <= 65535):
        raise ValueError('the monitor equation changes its exact selected entry or input word')
    offset = selector * 56
    pointer = int.from_bytes(table[offset:offset + 4], 'big')
    mask = int.from_bytes(table[offset + 4:offset + 6], 'big')
    if pointer != 0xFFFFF754 or mask != (0x0800 if selector == 0 else 0x0004):
        raise ValueError('the selected stock monitor changes its native pointer or mask')
    return dict(offset=offset, pointer=pointer, mask=mask, unmasked=(word & mask) == 0)
