#!/usr/bin/env python3
"""
apply_immo_patch.py -- патч immo-контура "always ID OK" для HR-ЭБУ (Hitachi, ядро SH-2E).

Цели (--rom):
  1ND0A  (SH7059, 1.5 MiB, JDM)                -- эталон, латч-сайты выверены дизасмом.
  JK78C  (SH7058, 1.0 MiB, USDM Infiniti G37)  -- структурный порт: независимый компайл,
         immo-латч разнесён по иным RAM-адресам (registered 0xffff4521 b0, Lock 0xffff4567 b1),
         локализован реверсом и выверен round-trip'ом. Обоснование -- immo-always-id-ok.md.

Читает сток-образ, применяет латч-патчи NATS-контура ECM и пишет патченый образ ЛОКАЛЬНО.

Модель B' (проверена реверсом): ECM не режёт впрыск/искру локально по immo. Патч меняет
только состояние/репорт immo-контура (registered / Lock / DTC). Итоговый эффект на старт
без married BCM определяется handshake'ом BCM-стороны и проверяется на стенде.

Checksum НЕ пересчитывается -- образ не для прошивки. Для первой стендовой заливки checksum
корректирует KESS V2 при записи; независимая локализация хранимого слова отложена.

Идемпотентно: original-байты верифицируются перед записью; повторный прогон на уже патченом
образе -- ошибка верификации (защита от двойного применения).
"""
import argparse
import os
import struct
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROMDIR = os.path.join(SCRIPT_DIR, "..", "rom-images")

# Каждый сайт: (offset, original, patched, label). offset = file offset = memory addr (base 0).
ROMS = {
    "1ND0A": {
        "stock": "1ND0A_Stock.bin",
        # Ядро "always ID OK":
        "core": [
            (0x0BF0C8, b"\xcf\x02", b"\x00\x09",
             "L1  Lock-suppress    immo_lock_setter 000bf0ac: or.b #2,@(r0,gbr) -> nop  "
             "(0xFFFEB852 bit1 'Lock' больше не выставляется)"),
            (0x0CCFF6, b"\x8f\x05", b"\xa0\x05",
             "L2  registered-force immo_registration 000ccf08: bf/s 0xcd004 -> bra 0xcd004 "
             "(ветвь всегда в set-путь; 0xFFFEB852 bit0 'registered/married' липнет в 1)"),
        ],
        # Спутник: снять reset-clear registered (устойчивость к reset-пути 0xFFFEB8F7&2):
        "l2b": [
            (0x0CCF90, b"\xcd\xfe", b"\x00\x09",
             "L2b reset-clear-neuter immo_registration 000ccf08: and.b #254,@(r0,gbr) -> nop "
             "(reset-путь больше не сбрасывает 0xFFFEB852 bit0)"),
        ],
        "esc": [],
    },
    "JK78C": {
        "stock": "JK78C.bin",
        "core": [
            (0x0AF8A0, b"\xcf\x02", b"\x00\x09",
             "L1  Lock-suppress    immo_lock_setter FUN_0af800: or.b #2,@(r0,gbr) -> nop  "
             "(0xffff4567 bit1 'Lock' не выставляется; delay-slot безусл. bra 0xaf8a6 цел, "
             "clear-путь 0af8a4 and.b #253 не тронут)"),
            (0x0B4142, b"\x89\x09", b"\x00\x09",
             "L2  registered-force immo_registration FUN_0b3f28: bt 0xb4158 (skip set) -> nop "
             "(всегда fall-through в set-путь or.b #1 @0b4152 -> 0xffff4521 bit0 'registered' "
             "липнет в 1; set-путь идемпотентен по tst #1)"),
        ],
        # Спутник: снять reset-clear registered bit0 (устойчивость к reset-пути gbr+0xea&8):
        "l2b": [
            (0x0B3FA6, b"\xcd\xfe", b"\x00\x09",
             "L2b reset-clear-neuter immo_registration FUN_0b3f28: and.b #254,@(r0,gbr) -> nop "
             "(reset-путь больше не сбрасывает 0xffff4521 bit0)"),
        ],
        # Эскалация: 2-й канал регистрации (ch1, 0xffff4522 bit6). Добавлять, только если
        # marriage требует обоих каналов (проверяется на стенде).
        "esc": [
            (0x0B4118, b"\x89\x07", b"\x00\x09",
             "L2' reg-force ch1    immo_registration FUN_0b3f28: bt 0xb412a -> nop "
             "(force set-путь or.b #64 @0b4128 -> 0xffff4522 bit6)"),
            (0x0B3FA2, b"\xcd\xbf", b"\x00\x09",
             "L2b' reset-clear ch1 immo_registration FUN_0b3f28: and.b #191,@(r0,gbr) -> nop "
             "(reset-путь не сбрасывает 0xffff4522 bit6)"),
        ],
    },
}


def sum32(buf):
    seg = bytes(buf)
    if len(seg) % 4:
        seg += b"\x00" * (4 - len(seg) % 4)
    return sum(struct.unpack(">%dI" % (len(seg) // 4), seg)) & 0xFFFFFFFF


def apply(patches, rom, verify_only=False):
    ok = True
    for off, orig, new, label in patches:
        cur = bytes(rom[off:off + len(orig)])
        match = cur == orig
        already = cur == new
        state = "OK" if match else ("ALREADY-PATCHED" if already else "MISMATCH")
        print(f"  @0x{off:06x}  {cur.hex(' ')} -> {new.hex(' ')}  [{state}]")
        print(f"             {label}")
        if not match:
            ok = False
            continue
        if not verify_only:
            rom[off:off + len(new)] = new
    return ok


def main():
    ap = argparse.ArgumentParser(description="Патч immo 'always ID OK' (1ND0A / JK78C)")
    ap.add_argument("--rom", choices=sorted(ROMS), default="1ND0A",
                    help="целевой образ (по умолчанию 1ND0A)")
    ap.add_argument("--with-l2b", action="store_true",
                    help="добавить L2b (снять reset-clear registered)")
    ap.add_argument("--with-esc", action="store_true",
                    help="добавить эскалацию 2-го канала (ch1); для JK78C -- L2'/L2b'")
    ap.add_argument("--out", default=None,
                    help="путь выходного образа (по умолчанию рядом со стоком)")
    ap.add_argument("--verify-only", action="store_true",
                    help="только проверить original-байты, не писать")
    args = ap.parse_args()

    cfg = ROMS[args.rom]
    stock = os.path.join(ROMDIR, cfg["stock"])
    rom = bytearray(open(stock, "rb").read())
    print(f"rom={args.rom}  stock: {stock}  size=0x{len(rom):x} ({len(rom)} B)")
    s_before = sum32(rom)

    if args.with_esc and not cfg["esc"]:
        print(f"\nПРИМЕЧАНИЕ: у {args.rom} нет эскалации ch1 (--with-esc игнорируется).")

    patches = list(cfg["core"])
    if args.with_l2b:
        patches += list(cfg["l2b"])
    if args.with_esc:
        patches += list(cfg["esc"])

    print(f"\napplying {len(patches)} patch site(s):")
    ok = apply(patches, rom, verify_only=args.verify_only)
    if not ok:
        print("\nОШИБКА: original-байты не совпали (не сток или уже патчено). Запись отменена.")
        return 2
    if args.verify_only:
        print("\nverify-only: original-байты совпали со стоком.")
        return 0

    s_after = sum32(rom)
    suffix = ("_l2b" if args.with_l2b else "") + ("_esc" if (args.with_esc and cfg["esc"]) else "")
    out = args.out or os.path.join(
        ROMDIR, "%s_immo-id-ok%s_UNCHECKSUMMED.bin" % (args.rom, suffix))
    open(out, "wb").write(rom)
    print(f"\nwrote: {out}")
    print(f"sum32 before=0x{s_before:08x}  after=0x{s_after:08x}  "
          f"delta=0x{(s_after - s_before) & 0xFFFFFFFF:08x}")
    print("ВНИМАНИЕ: checksum НЕ пересчитан. Образ не для прошивки (см. immo-always-id-ok.md).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
