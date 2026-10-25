"""Independent native-index1 permit, threshold, timer and complete byte-publication equations."""


def caller(memory, calibration, context):
    if (type(memory) is not bytes or len(memory) != 65536 or len(context) != 20
            or context[4] != 1 or any(type(v) is not int or not 0 <= v <= 0xFFFFFFFF for v in context)):
        raise ValueError('the rest-position equations require complete RAM and the exact native full-word bank1 input')
    out = bytearray(memory)
    def control(at):
        raw = calibration[at]
        if type(raw) is not bytes or len(raw) != 1:
            raise ValueError('the rest-position equation loses an exact raw ROM byte')
        return raw[0]
    def set_byte(at, value):
        out[at] = value & 255
    mask = 2
    enabled = bool(context[5]) and memory[0x2327] == 128
    first_permit = memory[0x43C3] == 0 and memory[0x24AB] & 0x50 == 0x50
    second_permit = (memory[0x43C2] == 0 and memory[0x24AA] & 0x58 == 0x58
        and bool(memory[0x2458] & 0x20))
    first = second = None
    def reset_timers(high, low):
        set_byte(high, control(0x8E25))
        set_byte(low, control(0x8E1C))
    if not enabled:
        set_byte(0x3599, out[0x3599] & ~mask)
        set_byte(0x430B, control(0x871F))
        set_byte(0x42F7, control(0x855D))
        reset_timers(0x43C1, 0x43B7)
        reset_timers(0x43B5, 0x43AF)
    else:
        if not first_permit:
            set_byte(0x42F7, control(0x855D))
            set_byte(0x3599, out[0x3599] & ~mask)
        if not second_permit:
            set_byte(0x430B, control(0x871F))
            set_byte(0x3599, out[0x3599] & ~mask)
        def judge(counter, high_timer, low_timer, high_control, low_control):
            if out[counter]:
                reset_timers(high_timer, low_timer)
                return dict(counter=out[counter], measured=False, value=None, high=None, low=None,
                    outside=None, high_fault=False, low_fault=False)
            set_byte(0x3599, out[0x3599] | mask)
            value = out[0x16BB]
            high, low = 128 + control(high_control), 128 - control(low_control)
            outside = value > high or value < low
            high_fault = outside and out[high_timer] == 0
            low_fault = outside and out[low_timer] == 0
            if outside:
                if high_fault:
                    set_byte(0x358B, out[0x358B] | mask)
                if low_fault:
                    set_byte(0x3582, out[0x3582] | mask)
            else:
                reset_timers(high_timer, low_timer)
            return dict(counter=0, measured=True, value=value, high=high, low=low,
                outside=outside, high_fault=high_fault, low_fault=low_fault)
        first = judge(0x42F7, 0x43C1, 0x43B7, 0x8951, 0x8952)
        second = judge(0x430B, 0x43B5, 0x43AF, 0x8736, 0x8737)
    return dict(enabled=enabled, first_permit=first_permit, second_permit=second_permit,
        selected=memory[0x16BB], first=first, second=second, flags=tuple(out[at] for at in (0x3599, 0x358B, 0x3582)),
        first_counter=out[0x42F7], second_counter=out[0x430B],
        timers=tuple(out[at] for at in (0x43C1, 0x43B7, 0x43B5, 0x43AF)), memory=bytes(out))
