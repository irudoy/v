"""Independent lower-knot selection, dimensionless ratio factor and counter comparison."""

from kb.byte_surface_semantics import axis_position


def cell(table, row_axis, column_axis, row, column):
    if len(table) != 16 or len(row_axis) != 4 or len(column_axis) != 4:
        raise ValueError('the counter-threshold equation needs its exact four-by-four byte grid')
    selected_row, _ = axis_position(row_axis, row)
    selected_column, _ = axis_position(column_axis, column)
    offset = selected_row * 4 + selected_column
    return dict(value=table[offset], row=selected_row, column=selected_column, reads=(offset,))


def caller(calibration, before):
    if type(before) is not bytes or len(before) != 65536 or set(calibration) != {0xAAFA, 0xAAEA, 0x12FEE, 0x12FF2}:
        raise ValueError('the counter-threshold equation lacks its exact grids, axes or complete RAM')
    word = int.from_bytes(before[0x40C6:0x40C8], 'big')
    column = min(word >> 2, 255)
    row = before[0x11AE]
    first = cell(calibration[0xAAFA], calibration[0x12FEE], calibration[0x12FF2], row, column)
    second = cell(calibration[0xAAEA], calibration[0x12FEE], calibration[0x12FF2], row, column)
    dividend = before[0x3448] * first['value']
    quotient = dividend // 10
    threshold = max(quotient, second['value'])
    counter = min(int.from_bytes(before[0x3446:0x3448], 'big') + 1, 65535)
    after = bytearray(before)
    after[0x351C], after[0x3449] = first['value'], second['value']
    after[0x3446:0x3448] = counter.to_bytes(2, 'big')
    return dict(memory=bytes(after), first=first, second=second, row=row, column=column,
                dividend=dividend, divisor=10, quotient=quotient, threshold=threshold, counter=counter,
                active=int(counter >= threshold), fault=bytes(after[0x9818:0x981C]))
