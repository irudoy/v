"""SH-2E instruction decoding for the L0 derivations.

`function_tokens.csv` folds the numbers of its shapes, so the derivations
decode the instruction word of the image at each instruction address.
"""

from dataclasses import dataclass

MASK = 0xFFFFFFFF
CALLER_SAVED = frozenset(range(8))


@dataclass(frozen=True)
class Access:
    """A memory operand: `base` is a register number or "gbr", `disp` a byte
    offset, `size` the width in bytes, and `mode` load, store, or update.
    `indexed` adds R0 to the base."""

    base: object
    disp: int
    size: int
    mode: str
    indexed: bool = False


@dataclass(frozen=True)
class Insn:
    """What one instruction word does to registers, memory, and control flow.

    `writes` lists the general registers the instruction sets. `value`
    states how `dest` gets its value when propagation can follow it:
    ("const", v), ("pool", address, size), ("mova", address), ("copy", m),
    ("addi", imm), ("add", m), ("sub", m), ("gbr",), ("extu", bits, m),
    ("exts", bits, m), or a shift of `dest` by `bits`: ("shl", bits),
    ("shr", bits), or ("sar", bits). `flow` is branch, cbranch, call, jump,
    or return; `target` is set when the word encodes it, and `delayed` marks
    a transfer with a delay slot. `gbr` is ("copy", m) for `ldc Rm,GBR` and
    ("unknown",) for any other GBR load.
    """

    word: int
    writes: frozenset = frozenset()
    dest: int | None = None
    value: tuple | None = None
    access: Access | None = None
    flow: str | None = None
    target: int | None = None
    delayed: bool = False
    gbr: tuple | None = None


def sext(value, bits):
    sign = 1 << (bits - 1)
    return (value & (sign - 1)) - (value & sign)


def _set(n, value=None):
    return {"writes": frozenset({n}), "dest": n, "value": value}


def _group0(word, n, m, low):
    if word == 0x000B or word == 0x002B:
        return Insn(word, flow="return", delayed=True)
    if low == 0x3 and m in (0x0, 0x2):
        return Insn(word, flow="call" if m == 0 else "jump", delayed=True)
    if low in (0x4, 0x5, 0x6):
        return Insn(word, access=Access(n, 0, 1 << (low - 0x4), "store", True))
    if low in (0xC, 0xD, 0xE):
        return Insn(word, access=Access(m, 0, 1 << (low - 0xC), "load", True), **_set(n))
    if low == 0xF:
        return Insn(word, writes=frozenset({n, m}), access=Access(m, 0, 4, "load"))
    if low == 0x2 and m == 0x1:
        return Insn(word, **_set(n, ("gbr",)))
    if low == 0x2 and m in (0x0, 0x2):
        return Insn(word, **_set(n))
    if low == 0xA and m in (0x0, 0x1, 0x2, 0x5, 0x6):
        return Insn(word, **_set(n))
    if low == 0x9 and m == 0x2:
        return Insn(word, **_set(n))
    return Insn(word)


def _group2(word, n, m, low):
    if low in (0x0, 0x1, 0x2):
        return Insn(word, access=Access(n, 0, 1 << low, "store"))
    if low in (0x4, 0x5, 0x6):
        size = 1 << (low - 0x4)
        return Insn(word, writes=frozenset({n}), dest=n, value=("addi", -size),
                    access=Access(n, -size, size, "store"))
    if low in (0x9, 0xA, 0xB, 0xD):
        return Insn(word, **_set(n))
    return Insn(word)


def _group3(word, n, m, low):
    if low == 0xC:
        return Insn(word, **_set(n, ("add", m)))
    if low == 0x8:
        return Insn(word, **_set(n, ("sub", m)))
    if low in (0x4, 0xA, 0xB, 0xE, 0xF):
        return Insn(word, **_set(n))
    return Insn(word)


# Register-only forms of group 4: low nibble and m field.
_G4_SET = {(0x0, 0x0), (0x1, 0x0), (0x4, 0x0), (0x5, 0x0), (0x8, 0x0),
           (0x9, 0x0), (0x0, 0x1), (0x8, 0x1), (0x9, 0x1), (0x0, 0x2),
           (0x1, 0x2), (0x4, 0x2), (0x5, 0x2), (0x8, 0x2), (0x9, 0x2)}
# The shifts among them: shll, shal, shll2, shll8, shll16, shlr, shlr2,
# shlr8, shlr16, and shar.
_G4_SHIFTS = {(0x0, 0x0): ("shl", 1), (0x0, 0x2): ("shl", 1), (0x8, 0x0): ("shl", 2),
              (0x8, 0x1): ("shl", 8), (0x8, 0x2): ("shl", 16), (0x1, 0x0): ("shr", 1),
              (0x9, 0x0): ("shr", 2), (0x9, 0x1): ("shr", 8), (0x9, 0x2): ("shr", 16),
              (0x1, 0x2): ("sar", 1)}


def _group4(word, n, m, low):
    if low == 0xB:
        if m == 0x0:
            return Insn(word, flow="call", delayed=True)
        if m == 0x2:
            return Insn(word, flow="jump", delayed=True)
        if m == 0x1:
            return Insn(word, access=Access(n, 0, 1, "update"))
        return Insn(word)
    if low == 0xE and m == 0x1:
        return Insn(word, gbr=("copy", n))
    if low in (0x2, 0x3):
        return Insn(word, writes=frozenset({n}), dest=n, value=("addi", -4),
                    access=Access(n, -4, 4, "store"))
    if low in (0x6, 0x7):
        return Insn(word, writes=frozenset({n}), dest=n, value=("addi", 4),
                    access=Access(n, 0, 4, "load"),
                    gbr=("unknown",) if (low, m) == (0x7, 0x1) else None)
    if low == 0xF:
        return Insn(word, writes=frozenset({n, m}), access=Access(m, 0, 2, "load"))
    if (low, m) in _G4_SET:
        return Insn(word, **_set(n, _G4_SHIFTS.get((low, m))))
    return Insn(word)


def _group6(word, n, m, low):
    if low in (0x0, 0x1, 0x2):
        return Insn(word, access=Access(m, 0, 1 << low, "load"), **_set(n))
    if low == 0x3:
        return Insn(word, **_set(n, ("copy", m)))
    if low in (0x4, 0x5, 0x6):
        size = 1 << (low - 0x4)
        return Insn(word, writes=frozenset({n, m}), dest=n,
                    access=Access(m, 0, size, "load"))
    if low in (0xC, 0xD):
        return Insn(word, **_set(n, ("extu", 8 if low == 0xC else 16, m)))
    if low in (0xE, 0xF):
        return Insn(word, **_set(n, ("exts", 8 if low == 0xE else 16, m)))
    return Insn(word, **_set(n))


def _group8(word, pc, n, m, low):
    if n in (0x0, 0x1):
        size = 1 << n
        return Insn(word, access=Access(m, low * size, size, "store"))
    if n in (0x4, 0x5):
        size = 1 << (n - 0x4)
        return Insn(word, access=Access(m, low * size, size, "load"), **_set(0))
    if n in (0x9, 0xB, 0xD, 0xF):
        return Insn(word, flow="cbranch", target=(pc + 4 + sext(word & 0xFF, 8) * 2) & MASK,
                    delayed=n in (0xD, 0xF))
    return Insn(word)


def _group12(word, pc, n):
    disp = word & 0xFF
    if n in (0x0, 0x1, 0x2):
        size = 1 << n
        return Insn(word, access=Access("gbr", disp * size, size, "store"))
    if n in (0x4, 0x5, 0x6):
        size = 1 << (n - 0x4)
        return Insn(word, access=Access("gbr", disp * size, size, "load"), **_set(0))
    if n == 0x7:
        return Insn(word, **_set(0, ("mova", ((pc & ~3) + 4 + disp * 4) & MASK)))
    if n in (0x9, 0xA, 0xB):
        return Insn(word, **_set(0))
    if n == 0xC:
        return Insn(word, access=Access("gbr", 0, 1, "load", True))
    if n in (0xD, 0xE, 0xF):
        return Insn(word, access=Access("gbr", 0, 1, "update", True))
    return Insn(word)


def _group15(word, n, m, low):
    if low == 0x6:
        return Insn(word, access=Access(m, 0, 4, "load", True))
    if low == 0x7:
        return Insn(word, access=Access(n, 0, 4, "store", True))
    if low == 0x8:
        return Insn(word, access=Access(m, 0, 4, "load"))
    if low == 0x9:
        return Insn(word, writes=frozenset({m}), dest=m, value=("addi", 4),
                    access=Access(m, 0, 4, "load"))
    if low == 0xA:
        return Insn(word, access=Access(n, 0, 4, "store"))
    if low == 0xB:
        return Insn(word, writes=frozenset({n}), dest=n, value=("addi", -4),
                    access=Access(n, -4, 4, "store"))
    return Insn(word)


def decode(word, pc):
    """Decode the 16-bit instruction word at address `pc`."""
    top = word >> 12
    n = (word >> 8) & 0xF
    m = (word >> 4) & 0xF
    low = word & 0xF
    if top == 0x0:
        return _group0(word, n, m, low)
    if top == 0x1:
        return Insn(word, access=Access(n, low * 4, 4, "store"))
    if top == 0x2:
        return _group2(word, n, m, low)
    if top == 0x3:
        return _group3(word, n, m, low)
    if top == 0x4:
        return _group4(word, n, m, low)
    if top == 0x5:
        return Insn(word, access=Access(m, low * 4, 4, "load"), **_set(n))
    if top == 0x6:
        return _group6(word, n, m, low)
    if top == 0x7:
        return Insn(word, **_set(n, ("addi", sext(word & 0xFF, 8))))
    if top == 0x8:
        return _group8(word, pc, n, m, low)
    if top == 0x9:
        return Insn(word, **_set(n, ("pool", (pc + 4 + (word & 0xFF) * 2) & MASK, 2)))
    if top in (0xA, 0xB):
        return Insn(word, flow="branch" if top == 0xA else "call",
                    target=(pc + 4 + sext(word & 0xFFF, 12) * 2) & MASK, delayed=True)
    if top == 0xC:
        return _group12(word, pc, n)
    if top == 0xD:
        return Insn(word, **_set(n, ("pool", ((pc & ~3) + 4 + (word & 0xFF) * 4) & MASK, 4)))
    if top == 0xE:
        return Insn(word, **_set(n, ("const", sext(word & 0xFF, 8) & MASK)))
    return _group15(word, n, m, low)
