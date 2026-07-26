#!/usr/bin/env python3
"""lock_setbit_scan.py -- консервативная sole-setter проверка immo Lock-бита (SH-2E).

Патч always-ID-OK глушит один сайт L1 (`or.b`, выставляющий Lock-бит). Корректность
опирается на то, что Lock-бит переводит в 1 ровно эта инструкция. Lock-байт при этом --
общий многобитный флаг immo (Lock -- лишь один бит; соседние -- registered ch1, статус),
и в него пишут несколько функций. Поэтому проверяется не "единственный писатель байта", а
"единственный, кто СТАВИТ Lock-бит (0->1)".

Метод (SH-2, big-endian, фикс. 16 бит; capstone не нужен -- декодируются нужные формы
одним forward-проходом с моделью регистров и gbr, сброс на rts). Пути записи в байт RAM:
  or.b #k,@(r0,gbr)       -- SET, если (k & mask)          <- единственный законный = L1
  xor.b #k,@(r0,gbr)      -- SET-capable, если (k & mask)  (тоггл поднимает из 0)
  and.b #k,@(r0,gbr)      -- CLEAR/preserve, бит не ставит
  mov.b R0,@(disp,gbr)    -- store (old & and_acc) | or_acc; SET только при (or_acc & mask)
  mov.b Rm,@Rn / @-Rn     -- store через абсолютный указатель
  mov.b Rm,@(r0,Rn)       -- индексный store через абсолютный указатель
  mov.b R0,@(disp,Rn)     -- store через base+disp
Для GBR-store провенанс r0 из old-байта трекается как (and_acc, or_acc).

Линейная модель не заменяет CFG/data-flow Ghidra: неизвестная кодогенерация или адрес,
который модель не разрешила, требуют отдельной проверки. Verdict означает чистоту
поддерживаемых форм и литералов, а не доказательство всех возможных SH-вычислений адреса.
На эталонных ROM проекта эти формы дают один setter L1, 0 опасных mov.b, 0 неразрешённых
GBR-записей и 0 непроверенных прямых литеральных записей. Прогон работает из любого cwd."""
import os
import struct

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROMDIR = os.path.join(SCRIPT_DIR, "..", "rom-images")

# lock -- адрес Lock-байта в RAM; mask -- бит Lock; site -- сток-сайт L1 (or.b, set).
# benign -- смещения RMW, где линейный (не learn-code/data) декодер ложно видит or/xor.b:
#   выверено дизасмом -- data/FP-регионы (`ff fe`=fmac, операнды `movi20`) либо r0 из
#   `movi20s` != disp Lock-байта. Не писатели Lock-бита. У 1.0-МиБ портов таких нет.
# benign_lit -- литерал-указатель на Lock-байт, чей единственный потребитель (registration)
#   ставит bit0 (registered) индексной записью `mov.b Rm,@(r0,Rn)`, а не Lock-бит.
# benign_store -- индексные mov.b в Lock-байт, для которых Ghidra listing/data-flow
#   подтверждает RMW только иных битов с сохранением mask. Расширенный scan_reg_stores
#   включён у exact-code пары JK03A/JK08A, где все кандидаты выверены адресно.
JK03A_BENIGN_STORES = {
    0x07795C,  # RMW bit7
    0x077EDC,  # RMW bit7
    0x087838,  # RMW bit0
    0x0CF3E8,  # clear bit3/bit5
    0x0CFA54,  # clear bit4
    0x0CFDD2,  # set bit4
    0x0D0348,  # set bit3
}

ROMS = [
    dict(name="1ND0A", path="1ND0A_Stock.bin", lock=0xFFFEB852, mask=0x02, site=0x0BF0C8,
         benign={0x04199A, 0x095072, 0x0B00BA, 0x0B24B6, 0x0B24CE, 0x0C46AA,
                 0x0C48F2, 0x0EF92A, 0x0EF92E, 0x0EF936, 0x11F2D2},
         benign_lit={0x0CD1D0}),
    dict(name="JK78C", path="JK78C.bin",        lock=0xFFFF4567, mask=0x02, site=0x0AF8A0),
    dict(name="JK03A", path="v36-vq25hr-jk03a/as7058.bin", lock=0xFFFF4201,
         mask=0x04, site=0x08D7C8, scan_reg_stores=True,
         benign_store=JK03A_BENIGN_STORES),
    dict(name="JK08A",
         path=("1JK08A_7MFKAVN86-20260726-064107/"
               "1JK08A_7MFKAVN86-20260726-064107.bin"),
         lock=0xFFFF4201, mask=0x04, site=0x08D7C8, scan_reg_stores=True,
         benign_store=JK03A_BENIGN_STORES),
    dict(name="JK00D",
         path="1JK00D_8MFK36N15-20260726-013734/1JK00D_8MFK36N15-20260726-013734.bin",
         lock=0xFFFF43B8, mask=0x08, site=0x092488),
]


def u32(d, o):
    return struct.unpack_from(">I", d, o)[0]


def s8(b):
    return b - 256 if b >= 128 else b


def scan(rom):
    with open(os.path.join(ROMDIR, rom["path"]), "rb") as handle:
        return scan_data(rom, handle.read())


def scan_data(rom, d):
    N, lock, mask = len(d), rom["lock"], rom["mask"]

    reg = [None] * 16       # последнее известное значение регистра
    old = [False] * 16      # регистр держит значение, производное от old Lock-байта
    aacc = [0xFF] * 16      # накопленный AND поверх old (для mov.b-store провенанса)
    oacc = [0x00] * 16      # накопленный OR поверх old
    gbr = None
    setters, dangers, unresolved, absptr = [], [], [], []

    def reset():
        nonlocal gbr
        for i in range(16):
            reg[i], old[i], aacc[i], oacc[i] = None, False, 0xFF, 0x00
        gbr = None

    off = 0
    while off + 1 < N:
        b0, b1 = d[off], d[off + 1]
        hn, ln = b0 >> 4, b0 & 0xF

        if b0 == 0x00 and b1 == 0x0B:                       # rts -> граница функции
            reset()
        elif hn == 0xE:                                     # mov #imm,Rn
            reg[ln] = s8(b1) & 0xFFFFFFFF; old[ln] = False
        elif hn == 0xD:                                     # mov.l @(disp,pc),Rn
            lit = ((off + 4) & ~3) + b1 * 4
            reg[ln] = u32(d, lit) if lit + 4 <= N else None; old[ln] = False
        elif hn == 0x9:                                     # mov.w @(disp,pc),Rn
            lit = (off + 4) + b1 * 2
            reg[ln] = (struct.unpack(">h", d[lit:lit + 2])[0] & 0xFFFFFFFF) if lit + 2 <= N else None
            old[ln] = False
        elif hn == 0x6 and (b1 & 0xF) == 0x3:               # mov Rm,Rn
            m = b1 >> 4
            reg[ln], old[ln], aacc[ln], oacc[ln] = reg[m], old[m], aacc[m], oacc[m]
        elif hn == 0x6 and (b1 & 0xF) in (0xC, 0xE):        # extu.b / exts.b Rm,Rn
            m = b1 >> 4
            reg[ln] = (reg[m] & 0xFF) if reg[m] is not None else None; old[ln] = False
        elif hn == 0x7:                                     # add #imm,Rn
            if reg[ln] is not None:
                reg[ln] = (reg[ln] + s8(b1)) & 0xFFFFFFFF
            old[ln] = False
        elif b0 == 0xC9:                                    # and #imm,r0
            if reg[0] is not None:
                reg[0] &= b1
            if old[0]:
                aacc[0] &= b1
        elif b0 == 0xCB:                                    # or #imm,r0
            if reg[0] is not None:
                reg[0] |= b1
            if old[0]:
                oacc[0] |= b1
        elif b0 == 0xCA:                                    # xor #imm,r0
            if reg[0] is not None:
                reg[0] ^= b1
            old[0] = False
        elif hn == 0x4 and b1 == 0x1E:                      # ldc Rm,gbr
            gbr = reg[ln]
        elif b0 == 0xC4:                                    # mov.b @(disp,gbr),r0 (загрузка old)
            eff = (gbr + b1) if gbr is not None else None
            reg[0] = None
            if eff == lock:
                old[0], aacc[0], oacc[0] = True, 0xFF, 0x00
            else:
                old[0] = False
        elif b0 in (0xCF, 0xCD, 0xCE):                      # or/and/xor.b #imm,@(r0,gbr)
            eff = (gbr + reg[0]) if (gbr is not None and reg[0] is not None) else None
            if eff is None and gbr is not None and 0 <= lock - gbr < 0x100:
                unresolved.append((off, {0xCF: "or.b", 0xCD: "and.b", 0xCE: "xor.b"}[b0], gbr))
            elif eff == lock:
                if b0 == 0xCF and (b1 & mask):
                    setters.append((off, f"or.b #{b1:#x}", gbr, reg[0]))
                elif b0 == 0xCE and (b1 & mask):
                    setters.append((off, f"xor.b #{b1:#x}", gbr, reg[0]))
                # and.b Lock-бит не ставит
        elif b0 == 0xC0:                                    # mov.b r0,@(disp,gbr)
            eff = (gbr + b1) if gbr is not None else None
            if eff == lock:
                if old[0]:
                    if oacc[0] & mask:
                        dangers.append((off, f"store old&{aacc[0]:#x}|{oacc[0]:#x}", "SET"))
                    # иначе: and_acc-бит=1 -> preserve, =0 -> clear; из 0 не поднимает
                elif reg[0] is not None:
                    if reg[0] & mask:
                        dangers.append((off, f"store #{reg[0] & 0xFF:#x}", "SET-const"))
                else:
                    unresolved.append((off, "mov.b(gbr) r0=?", gbr))
        elif (rom.get("scan_reg_stores") and hn == 0x8
              and (b1 & 0xF) == 0x0):                         # mov.b r0,@(disp,Rn)
            n, disp = ln, b1 >> 4
            eff = (reg[n] + disp) & 0xFFFFFFFF if reg[n] is not None else None
            if eff == lock:
                absptr.append((off, "mov.b r0,@(disp,Rn)", 0))
        elif hn == 0x2 and (b1 & 0xF) == 0x0:               # mov.b Rm,@Rn
            if reg[ln] == lock:
                absptr.append((off, "mov.b Rm,@Rn", b1 >> 4))
        elif rom.get("scan_reg_stores") and hn == 0x2 and (b1 & 0xF) == 0x4:  # mov.b Rm,@-Rn
            eff = (reg[ln] - 1) & 0xFFFFFFFF if reg[ln] is not None else None
            if eff == lock:
                absptr.append((off, "mov.b Rm,@-Rn", b1 >> 4))
            reg[ln] = eff
            old[ln] = False
        elif rom.get("scan_reg_stores") and hn == 0x0 and (b1 & 0xF) == 0x4:  # mov.b Rm,@(r0,Rn)
            eff = ((reg[0] + reg[ln]) & 0xFFFFFFFF
                   if reg[0] is not None and reg[ln] is not None else None)
            if eff == lock:
                absptr.append((off, "mov.b Rm,@(r0,Rn)", b1 >> 4))
        off += 2

    lit_hits = [o for o in range(0, N - 3, 2) if u32(d, o) == lock]
    return dict(setters=setters, dangers=dangers, unresolved=unresolved,
                absptr=absptr, lit_hits=lit_hits)


def main():
    rc = 0
    for rom in ROMS:
        r = scan(rom)
        benign = rom.get("benign", set())
        benign_lit = rom.get("benign_lit", set())
        benign_store = rom.get("benign_store", set())
        unresolved = [u for u in r["unresolved"] if u[0] not in benign]
        lit_hits = [o for o in r["lit_hits"] if o not in benign_lit]
        absptr = [item for item in r["absptr"] if item[0] not in benign_store]
        clean = (len(r["setters"]) == 1 and r["setters"][0][0] == rom["site"]
                 and not r["dangers"] and not unresolved and not absptr
                 and not lit_hits)
        verdict = "OK: единственный setter в модели = L1" if clean else "ВНИМАНИЕ: проверить находки"
        if not clean:
            rc = 1
        print(f"\n===== {rom['name']}  lock={rom['lock']:#010x} bit(mask={rom['mask']:#x}) "
              f"L1={rom['site']:#08x} -- {verdict} =====")
        print(f"  ставят Lock-бит (or/xor с маской): {len(r['setters'])}")
        for off, op, gbr, r0 in r["setters"]:
            tag = " <- L1" if off == rom["site"] else "  <<<< ЧУЖОЙ SETTER"
            print(f"    @{off:#08x} {op} via gbr={gbr:#x}+{r0:#x}{tag}")
        print(f"  mov.b-store, поднимающие бит из 0: {len(r['dangers'])}")
        for off, desc, kind in r["dangers"]:
            print(f"    @{off:#08x} {desc} [{kind}] <<<< ПОДНИМАЕТ")
        nb = f" (+{len(benign)} выверенных data/FP отсеяно)" if benign else ""
        print(f"  неразрешённый r0 у immo-базы: {len(unresolved)}{nb}")
        for off, op, gbr in unresolved:
            print(f"    @{off:#08x} {op} gbr={gbr:#x}")
        nl = f" (+{len(benign_lit)} выверенный: registered, не Lock)" if benign_lit else ""
        ns = (f" (+{len(benign_store)} выверенных Ghidra RMW иных битов)"
              if benign_store else "")
        print(f"  непроверенные mov.b на lock-адрес: {len(absptr)}{ns}  "
              f"(литерал==lock в пуле: {[hex(x) for x in lit_hits]}{nl})")
        for off, form, source in absptr:
            print(f"    @{off:#08x} {form}, source=r{source}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
