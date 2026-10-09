"""Independent terminal-register equations of whole feedback 0005cbec."""

signed8 = lambda value: value - 256 if value & 128 else value
signed16 = lambda value: value - 65536 if value & 32768 else value


def expectations(ram):
    """Return the last publisher blocks and the fixed positive divider state.

    The final real divider consumes uint16 RAM[ffff40c2] with divisor 10.
    Its DIV0U sets M=0. The final ROTCL inserts T=1-Q as the quotient low
    bit, so Q=1-(quotient&1). Subsequent publisher loops set T=1 and retain
    M/Q. The incoming R8..R14, GBR, MACH, MACL and natural PR are preserved.
    """
    assert len(ram) == 65536
    word = lambda at: int.from_bytes(ram[at:at + 2], 'big')
    quotient = word(0x40c2) // 10
    return dict(r0=signed16(word(0x8912)) & 0xffffffff,
        r1=0x010022dc, r2=0x010040ac, r3=0x010028f8,
        r4=2, r5=2, r6=0x00006094,
        r7=signed8(ram[0x32ff]) & 0xffffffff,
        sr_held_mask=0xfffffcfe, exit_m=0, exit_q=1 - (quotient & 1), exit_t=1,
        incoming_gpr_preserved=list(range(8, 15)), gbr_preserved=True,
        mach_preserved=True, macl_preserved=True, natural_pr_preserved=True)
