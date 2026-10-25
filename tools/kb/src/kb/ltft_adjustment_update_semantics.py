"""Independent wrapped trim steps, ordered bounds and actual native index1 publications."""


def word(memory, address):
    return int.from_bytes(memory[address:address + 2], 'big')


def signed_word(value):
    return value if value < 32768 else value - 65536


def caller(memory, calibration, context):
    if type(memory) is not bytes or len(memory) != 65536:
        raise ValueError('the trim updater equations require complete raw RAM')
    if (type(context) not in (list, tuple) or len(context) != 20
            or any(type(value) is not int or not 0 <= value <= 0xFFFFFFFF for value in context)
            or context[4] & 255 != 1 or context[18] & ~0x3F1):
        raise ValueError('the trim updater equations require the complete native index1 context')
    for address, size in ((0x878B, 1), (0x878C, 1), (0x878F, 1), (0x8790, 1),
                          (0x86BE, 1), (0x86BF, 1), (0x8FA6, 2), (0x8FA8, 2)):
        if type(calibration.get(address)) is not bytes or len(calibration[address]) != size:
            raise ValueError('the trim updater equations lose a complete physical ROM control')
    old = word(memory, 0x564A)
    diagnostic = word(memory, 0x2304)
    step_factor = calibration[0x878B][0]
    dividend = diagnostic * step_factor
    delta = dividend // 25600
    upper = calibration[0x86BE][0] * 256
    lower = calibration[0x86BF][0] * 256
    upper_error = calibration[0x878F][0] * 256
    lower_error = calibration[0x8790][0] * 256
    first_permit = bool(memory[0x22E1] & 2)
    second_permit = None if not first_permit else bool(memory[0x230E] & 2)
    permitted = bool(first_permit and second_permit)
    after = bytearray(memory)
    candidate = old
    timer_written = False
    reset_cleared = False
    signed_sum = None
    error = None
    measured = None
    selected = None
    increased = None
    decreased = None
    temperature = None
    temperature_upper = None
    temperature_lower = None
    temperature_step = None
    quiet_status = None
    quiet_permit = None
    active_status = bool(memory[0x3E30] & 2)
    local_flag = 0
    if not permitted:
        if memory[0x3082] & 2:
            reset_cleared = True
            after[0x3082] = memory[0x3082] & ~2
            if active_status:
                temperature = word(memory, 0x29E4)
                temperature_upper = word(calibration[0x8FA8], 0)
                if temperature < temperature_upper:
                    temperature_step = 16 * calibration[0x878C][0]
                    candidate = (old - temperature_step) & 65535
                    branch = 'disabled-temperature-decrease'
                else:
                    temperature_lower = word(calibration[0x8FA6], 0)
                    if temperature > temperature_lower:
                        temperature_step = 16 * calibration[0x878C][0]
                        candidate = (old + temperature_step) & 65535
                        branch = 'disabled-temperature-increase'
                    else:
                        branch = 'disabled-temperature-hold'
            else:
                branch = 'disabled-without-active-cell'
        else:
            branch = 'disabled-without-reset'
    elif memory[0x4498]:
        branch = 'timer-hold'
    else:
        timer_written = True
        after[0x4498] = 16
        if active_status:
            measured = word(memory, 0x1308)
            selected = word(memory, 0x2308)
            signed_sum = signed_word((measured + selected) & 65535)
            error = (signed_sum - 25600) & 65535
            increased = (old + delta) & 65535
            decreased = (old - delta) & 65535
            if error >= upper_error:
                candidate = min(increased, upper)
                local_flag = 1
                branch = 'active-upper-error-step'
            elif error <= lower_error:
                candidate = max(decreased, lower)
                local_flag = 1
                branch = 'active-lower-error-step'
            elif old >= 25600:
                candidate = max(decreased, 25600)
                local_flag = 1
                branch = 'active-return-to-neutral-from-above'
            else:
                candidate = min(increased, 25600)
                branch = 'active-return-to-neutral-from-below'
        else:
            quiet_status = bool(memory[0x3EA4] & 2)
            if quiet_status:
                quiet_permit = bool(memory[0x2461] & 8)
            if quiet_status and not quiet_permit:
                branch = 'quiet-status-hold'
            elif old > 25600:
                candidate = max((old - delta) & 65535, 25600)
                branch = 'quiet-return-to-neutral-from-above'
            elif old < 25600:
                candidate = min((old + delta) & 65535, 25600)
                branch = 'quiet-return-to-neutral-from-below'
            else:
                branch = 'quiet-neutral-hold'
    limited_upper = min(candidate, upper)
    limited = max(limited_upper, lower)
    diagnostic_neutral = bool(memory[0x5A94] & 128)
    control_neutral = None if diagnostic_neutral else bool(memory[0x41B5] & 1)
    neutral = bool(diagnostic_neutral or control_neutral)
    output = 25600 if neutral else limited
    status = (memory[0x12FE] | 2) if active_status else (memory[0x12FE] & ~2)
    after[0x564A:0x564C] = output.to_bytes(2, 'big')
    after[0x12FE] = status
    return dict(old=old, diagnostic=diagnostic, step_factor=step_factor, dividend=dividend, delta=delta,
                first_permit=first_permit, second_permit=second_permit, permitted=permitted,
                timer_written=timer_written, timer_before=memory[0x4498], timer_after=after[0x4498],
                reset_cleared=reset_cleared, reset_before=memory[0x3082], reset_after=after[0x3082],
                active_status=active_status, quiet_status=quiet_status, quiet_permit=quiet_permit,
                measured=measured, selected=selected, signed_sum=signed_sum, error=error,
                upper_error=upper_error, lower_error=lower_error, increased=increased, decreased=decreased,
                temperature=temperature, temperature_upper=temperature_upper, temperature_lower=temperature_lower,
                temperature_step=temperature_step, branch=branch, local_flag=local_flag, candidate=candidate,
                upper=upper, lower=lower, limited_upper=limited_upper, limited=limited,
                diagnostic_neutral=diagnostic_neutral, control_neutral=control_neutral, neutral=neutral,
                status=status, value=output, memory=bytes(after))
