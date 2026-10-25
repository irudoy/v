"""Independent indexed raw-word and regulator-domain saturation equations."""

RAM_BASE = 0x01000000


def caller(memory, incoming_r4):
    if type(memory) is not bytes or len(memory) != 65536 or type(incoming_r4) is not int or not 0 <= incoming_r4 <= 0xFFFFFFFF:
        raise ValueError('the indexed reader lacks a complete typed RAM and channel input')
    index = incoming_r4 & 255
    source = 0x28BC + 2 * index
    destination = 0x387A + 2 * index
    word = int.from_bytes(memory[source:source+2], 'big')
    scaled = word * 16 + 8192
    saturated = scaled > 65535
    value = 65535 if saturated else scaled
    out = bytearray(memory)
    out[destination:destination+2] = value.to_bytes(2, 'big')
    return dict(index=index, source=RAM_BASE + source, destination=RAM_BASE + destination,
                word=word, sign_extended_word=word if word < 32768 else word - 65536,
                scaled=scaled, saturated=saturated, value=value, memory=bytes(out),
                owning_read=index == 1)


def exit_cpu(context, sp, continuation, sr_before, value):
    # The ordinary exit has R14..R0; SP is a separate observation field.
    registers = list(context[:15])
    registers[0] = 2 * value['index']
    registers[2] = RAM_BASE + 0x387A
    registers[3] = 0x01A2
    registers[5] = 2 * value['index']
    registers[6] = value['value']
    sr = (sr_before & ~1) | int(value['saturated'])
    return (sr, continuation, context[17], context[16], context[15], *reversed(registers))
