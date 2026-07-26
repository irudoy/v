#!/usr/bin/env python3
"""
apply_immo_patch.py -- патч immo-контура "always ID OK" для HR-ЭБУ (Hitachi, ядро SH-2E).

Цели (--rom):
  1ND0A  (SH7059, 1.5 MiB, JDM)                -- эталон, латч-сайты выверены дизасмом.
  JK78C  (SH7058, 1.0 MiB, USDM Infiniti G37)  -- структурный порт: независимый компайл,
         immo-латч разнесён по иным RAM-адресам (registered 0xffff4521 b0, Lock 0xffff4567 b1),
         локализован реверсом и выверен round-trip'ом. Обоснование -- immo-always-id-ok.md.
  JK03A  (SH7058, 1.0 MiB, JDM V36 Skyline VQ25HR)  -- структурный порт: независимый компайл,
         Lock кодируется bit2 (or.b #4, не #2), registered 0xffff41c1 b0, ch1 0xffff41c2 b6,
         Lock 0xffff4201 b2. Локализован реверсом (структурная гомология + counter-пороги
         0x0b/0x20), подтверждён Ghidra listing/декомпиляцией. Обоснование -- immo-always-id-ok.md.
  JK08A  (SH7058, 1.0 MiB, JDM V36 Skyline VQ25HR)  -- exact-code порт JK03A: области кода
         и пять patch-sites совпадают побайтно, RAM-модель и адреса сайтов неизменны.
  JK00D  (SH7058, 1.0 MiB, VQ35HR)  -- близкий структурный порт JK03A: registration имеет
         тот же размер и те же относительные патч-сайты; Lock кодируется bit3
         (0xffff43b8), registered 0xffff4374 b0, ch1 0xffff4375 b6. Локализован реверсом
         и подтверждён Ghidra listing/декомпиляцией. Обоснование -- immo-always-id-ok.md.

Читает stock-образ, применяет латч-патчи NATS-контура ECM и пишет патченый образ локально.

Модель B' (проверена реверсом): ECM не режет впрыск/искру локально по immo. Патч меняет
только состояние/отчёт immo-контура (registered / Lock / DTC). Итоговый эффект на старт
без married BCM определяется handshake BCM-стороны и проверяется на стенде.

По умолчанию checksum не пересчитывается и результат получает суффикс `_UNCHECKSUMMED`.
Флаг `--fix-checksums` доступен только для точных stock JK03A/JK08A с закреплённым SHA-256:
он пересчитывает runtime selftest A/B и две SUM16, проверяет результат и пишет
`_CHECKSUMMED`. Такой файл имеет уровень доказательства `code/offline`, не `silicon`.

Идемпотентность patch-sites: original-байты верифицируются перед записью; повторное
применение к уже патченому входу завершается ошибкой. Готовый output не перезаписывается:
совпадающий файл принимается как уже созданный, отличающийся файл блокирует запись.
"""
import argparse
import hashlib
import os
import struct
import sys
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROMDIR = os.path.join(SCRIPT_DIR, "..", "rom-images")

# Каждый сайт: (offset, original, patched, label). offset = file offset = memory addr (base 0).
JK03A_CORE = [
    (0x08D7C8, b"\xcf\x04", b"\x00\x09",
     "L1  Lock-suppress    immo_lock_setter FUN_0008d724: or.b #4,@(r0,gbr) -> nop  "
     "(0xffff4201 bit2 'Lock' не выставляется; за counter-гейтом порога 0x20; delay-slot "
     "безусл. bra 0x8d7ce цел, clear-путь 0x8d7cc and.b #251 не тронут)"),
    (0x0938BE, b"\x89\x09", b"\x00\x09",
     "L2  registered-force immo_registration FUN_000937dc: bt 0x938d4 (skip set) -> nop "
     "(всегда fall-through в set-путь or.b #1 @0x938ce -> 0xffff41c1 bit0 'registered' "
     "липнет в 1; set-путь идемпотентен по tst #1; counter<0x0b гейт)"),
]
JK03A_L2B = [
    (0x09384A, b"\xcd\xfe", b"\x00\x09",
     "L2b reset-clear-neuter immo_registration FUN_000937dc: and.b #254,@(r0,gbr) -> nop "
     "(reset-путь больше не сбрасывает 0xffff41c1 bit0)"),
]
JK03A_ESC = [
    (0x093892, b"\x8d\x08", b"\x00\x09",
     "L2' reg-force ch1    immo_registration FUN_000937dc: bt/s 0x938a6 -> nop "
     "(force set-путь or.b #64 @0x938a4 -> 0xffff41c2 bit6)"),
    (0x093846, b"\xcd\xbf", b"\x00\x09",
     "L2b' reset-clear ch1 immo_registration FUN_000937dc: and.b #191,@(r0,gbr) -> nop "
     "(reset-путь не сбрасывает 0xffff41c2 bit6)"),
]

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
    "JK03A": {
        "stock": "v36-vq25hr-jk03a/as7058.bin",
        "sha256": "f78929547c08dc5ecde256fb3a6f6f3ef6daa9010e1531b3eac99fd9509225b4",
        "checksum": "sh7058-1m-hr",
        "core": JK03A_CORE,
        "l2b": JK03A_L2B,
        # L2' -- bt/s; delay-slot mov.l r6,@(8,r15) исполняется в обеих ветвях, nop его сохраняет.
        "esc": JK03A_ESC,
    },
    "JK08A": {
        "stock": (
            "1JK08A_7MFKAVN86-20260726-064107/"
            "1JK08A_7MFKAVN86-20260726-064107.bin"
        ),
        "sha256": "ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23",
        "checksum": "sh7058-1m-hr",
        "core": JK03A_CORE,
        "l2b": JK03A_L2B,
        "esc": JK03A_ESC,
    },
    "JK00D": {
        "stock": (
            "1JK00D_8MFK36N15-20260726-013734/"
            "1JK00D_8MFK36N15-20260726-013734.bin"
        ),
        "core": [
            (0x092488, b"\xcf\x08", b"\x00\x09",
             "L1  Lock-suppress    immo_lock_setter FUN_000923e4: or.b #8,@(r0,gbr) -> nop  "
             "(0xffff43b8 bit3 'Lock' не выставляется; за counter-гейтом порога 0x20; delay-slot "
             "безусл. bra 0x9248e цел, clear-путь 0x9248c and.b #247 не тронут)"),
            (0x0989EA, b"\x89\x09", b"\x00\x09",
             "L2  registered-force immo_registration FUN_00098908: bt 0x98a00 (skip set) -> nop "
             "(всегда fall-through в set-путь or.b #1 @0x989fa -> 0xffff4374 bit0 'registered' "
             "липнет в 1; set-путь идемпотентен по tst #1; counter<0x0b гейт)"),
        ],
        "l2b": [
            (0x098976, b"\xcd\xfe", b"\x00\x09",
             "L2b reset-clear-neuter immo_registration FUN_00098908: and.b #254,@(r0,gbr) -> nop "
             "(reset-путь больше не сбрасывает 0xffff4374 bit0)"),
        ],
        "esc": [
            (0x0989BE, b"\x8d\x08", b"\x00\x09",
             "L2' reg-force ch1    immo_registration FUN_00098908: bt/s 0x989d2 -> nop "
             "(force set-путь or.b #64 @0x989d0 -> 0xffff4375 bit6)"),
            (0x098972, b"\xcd\xbf", b"\x00\x09",
             "L2b' reset-clear ch1 immo_registration FUN_00098908: and.b #191,@(r0,gbr) -> nop "
             "(reset-путь не сбрасывает 0xffff4375 bit6)"),
        ],
    },
}

CHECKSUM_SIZE = 0x100000
CHECKSUM_FIELDS = {
    "sum16_a": (0x008200, 2),
    "sum16_b": (0x020000, 2),
    "self_a_xor": (0x0096D4, 4),
    "self_a_sum": (0x0096DC, 4),
    "self_b_sum": (0x020404, 4),
    "self_b_xor": (0x020408, 4),
}


def sha256(buf):
    return hashlib.sha256(bytes(buf)).hexdigest()


def sum32(buf):
    """Диагностическая сумма всего буфера, не ECU checksum."""
    seg = bytes(buf)
    if len(seg) % 4:
        seg += b"\x00" * (4 - len(seg) % 4)
    return sum(struct.unpack(">%dI" % (len(seg) // 4), seg)) & 0xFFFFFFFF


def sum16_be(buf, start, end):
    if start % 2 or end % 2 or not (0 <= start <= end <= len(buf)):
        raise ValueError(f"неверный u16-диапазон [{start:#x}, {end:#x})")
    return sum(struct.unpack_from(">H", buf, off)[0] for off in range(start, end, 2)) & 0xFFFF


def xor_sum32_be(buf, start, end, exclude=()):
    if start % 4 or end % 4 or not (0 <= start <= end <= len(buf)):
        raise ValueError(f"неверный u32-диапазон [{start:#x}, {end:#x})")
    excluded = set(exclude)
    xor_value = 0
    sum_value = 0
    for off in range(start, end, 4):
        if off in excluded:
            continue
        value = struct.unpack_from(">I", buf, off)[0]
        xor_value ^= value
        sum_value = (sum_value + value) & 0xFFFFFFFF
    return xor_value, sum_value


def calculated_checksums(buf):
    if len(buf) != CHECKSUM_SIZE:
        raise ValueError(f"checksum layout требует размер 0x{CHECKSUM_SIZE:x}, получен 0x{len(buf):x}")
    self_b_xor, self_b_sum = xor_sum32_be(buf, 0x02040C, 0x02259C)
    self_a_xor, self_a_sum = xor_sum32_be(
        buf,
        0x008204,
        0x100000,
        exclude=(0x0096D4, 0x0096DC, 0x020000),
    )
    return {
        "sum16_a": sum16_be(buf, 0x008202, 0x020000),
        "sum16_b": sum16_be(buf, 0x020002, 0x100000),
        "self_a_xor": self_a_xor,
        "self_a_sum": self_a_sum,
        "self_b_sum": self_b_sum,
        "self_b_xor": self_b_xor,
    }


def stored_checksums(buf):
    result = {}
    for name, (off, size) in CHECKSUM_FIELDS.items():
        fmt = ">H" if size == 2 else ">I"
        result[name] = struct.unpack_from(fmt, buf, off)[0]
    return result


def checksum_mismatches(buf):
    stored = stored_checksums(buf)
    calculated = calculated_checksums(buf)
    return {
        name: (stored[name], calculated[name])
        for name in CHECKSUM_FIELDS
        if stored[name] != calculated[name]
    }


def write_checksum(buf, name, value):
    off, size = CHECKSUM_FIELDS[name]
    fmt = ">H" if size == 2 else ">I"
    struct.pack_into(fmt, buf, off, value)


def fix_checksums(buf):
    """Пересчитать SH7058 1 MiB checksum в порядке зависимостей B -> A -> SUM16."""
    values = calculated_checksums(buf)
    write_checksum(buf, "self_b_sum", values["self_b_sum"])
    write_checksum(buf, "self_b_xor", values["self_b_xor"])

    values = calculated_checksums(buf)
    write_checksum(buf, "self_a_xor", values["self_a_xor"])
    write_checksum(buf, "self_a_sum", values["self_a_sum"])

    values = calculated_checksums(buf)
    write_checksum(buf, "sum16_a", values["sum16_a"])
    write_checksum(buf, "sum16_b", values["sum16_b"])

    mismatches = checksum_mismatches(buf)
    if mismatches:
        raise RuntimeError(f"checksum остались несогласованными: {mismatches}")
    return stored_checksums(buf)


def validate_exact_source(name, cfg, rom):
    if cfg.get("checksum") != "sh7058-1m-hr" or "sha256" not in cfg:
        raise ValueError(f"для {name} нет проверенного exact-layout checksum-профиля")
    problems = []
    if len(rom) != CHECKSUM_SIZE:
        problems.append(f"размер 0x{len(rom):x}, ожидался 0x{CHECKSUM_SIZE:x}")
    digest = sha256(rom)
    if digest != cfg["sha256"]:
        problems.append(f"SHA-256 {digest}, ожидался {cfg['sha256']}")
    if len(rom) == CHECKSUM_SIZE:
        mismatches = checksum_mismatches(rom)
        if mismatches:
            details = ", ".join(
                f"{key}=stored:{stored:#x}/calc:{calculated:#x}"
                for key, (stored, calculated) in mismatches.items()
            )
            problems.append(f"stock checksum не сходятся ({details})")
    if problems:
        raise ValueError("; ".join(problems))


def selected_patches(cfg, with_l2b=False, with_esc=False):
    patches = list(cfg["core"])
    if with_l2b:
        patches += list(cfg["l2b"])
    if with_esc:
        patches += list(cfg["esc"])
    return patches


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


def changed_offsets(before, after):
    if len(before) != len(after):
        raise ValueError("нельзя сравнить образы разного размера")
    return {off for off, (old, new) in enumerate(zip(before, after)) if old != new}


def allowed_offsets(patches, include_checksums=False):
    allowed = set()
    for off, orig, _new, _label in patches:
        allowed.update(range(off, off + len(orig)))
    if include_checksums:
        for off, size in CHECKSUM_FIELDS.values():
            allowed.update(range(off, off + size))
    return allowed


def write_output(path, stock, data):
    if os.path.realpath(path) == os.path.realpath(stock):
        raise ValueError("output совпадает со stock: запись запрещена")
    if os.path.exists(path):
        with open(path, "rb") as handle:
            existing = handle.read()
        if existing == bytes(data):
            return False
        raise FileExistsError(f"output уже существует и отличается: {path}")

    directory = os.path.dirname(os.path.abspath(path))
    prefix = os.path.basename(path) + "."
    fd, temporary = tempfile.mkstemp(prefix=prefix, suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        with open(temporary, "rb") as handle:
            written = handle.read()
        if written != bytes(data):
            raise OSError(f"проверка временного output не пройдена: {temporary}")
        # Hard link публикует готовый inode атомарно и, в отличие от os.replace(),
        # никогда не перезаписывает появившийся между проверками конечный путь.
        os.link(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return True


def print_checksums(values, prefix="checksum"):
    print(
        f"{prefix}: SUM16 A={values['sum16_a']:04x} B={values['sum16_b']:04x}; "
        f"selftest A XOR={values['self_a_xor']:08x} SUM={values['self_a_sum']:08x}; "
        f"B SUM={values['self_b_sum']:08x} XOR={values['self_b_xor']:08x}"
    )


def main(argv=None):
    ap = argparse.ArgumentParser(description="Патч immo 'always ID OK' для поддерживаемых HR ROM")
    ap.add_argument("--rom", choices=sorted(ROMS), default="1ND0A",
                    help="целевой образ (по умолчанию 1ND0A)")
    ap.add_argument("--with-l2b", action="store_true",
                    help="добавить L2b (снять reset-clear registered)")
    ap.add_argument("--with-esc", action="store_true",
                    help="добавить эскалацию 2-го канала (ch1), если она поддерживается ROM")
    ap.add_argument("--out", default=None,
                    help="путь выходного образа (по умолчанию рядом со stock)")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--verify-only", action="store_true",
                      help="только проверить original-байты, не писать")
    mode.add_argument("--fix-checksums", action="store_true",
                      help="пересчитать проверенные checksum JK03A/JK08A")
    args = ap.parse_args(argv)

    cfg = ROMS[args.rom]
    stock = os.path.join(ROMDIR, cfg["stock"])
    try:
        with open(stock, "rb") as handle:
            source = handle.read()
    except OSError as exc:
        print(f"ОШИБКА: не удалось прочитать stock: {exc}")
        return 2
    rom = bytearray(source)
    print(f"rom={args.rom}  stock: {stock}  size=0x{len(rom):x} ({len(rom)} B)")
    s_before = sum32(rom)

    if args.fix_checksums or (args.verify_only and cfg.get("checksum")):
        try:
            validate_exact_source(args.rom, cfg, rom)
        except ValueError as exc:
            print(f"ОШИБКА: {exc}")
            return 2
        print_checksums(stored_checksums(rom), prefix="stock checksum OK")

    if args.with_esc and not cfg["esc"]:
        print(f"\nПРИМЕЧАНИЕ: у {args.rom} нет эскалации ch1 (--with-esc игнорируется).")

    patches = selected_patches(cfg, args.with_l2b, args.with_esc)
    print(f"\napplying {len(patches)} patch site(s):")
    ok = apply(patches, rom, verify_only=args.verify_only)
    if not ok:
        print("\nОШИБКА: original-байты не совпали (не stock или уже патчено). Запись отменена.")
        return 2
    if args.verify_only:
        print("\nverify-only: original-байты и применимые checksum совпали со stock.")
        return 0

    if args.fix_checksums:
        values = fix_checksums(rom)
        print_checksums(values, prefix="output checksum OK")

    unexpected = changed_offsets(source, rom) - allowed_offsets(patches, args.fix_checksums)
    if unexpected:
        sample = ", ".join(f"0x{off:x}" for off in sorted(unexpected)[:16])
        print(f"ОШИБКА: изменены байты вне whitelist: {sample}")
        return 2

    s_after = sum32(rom)
    suffix = ("_l2b" if args.with_l2b else "") + ("_esc" if (args.with_esc and cfg["esc"]) else "")
    state = "CHECKSUMMED" if args.fix_checksums else "UNCHECKSUMMED"
    out = args.out or os.path.join(ROMDIR, f"{args.rom}_immo-id-ok{suffix}_{state}.bin")
    try:
        created = write_output(out, stock, rom)
    except (OSError, ValueError) as exc:
        print(f"ОШИБКА: {exc}")
        return 2

    action = "wrote" if created else "already matches"
    print(f"\n{action}: {out}")
    print(f"sha256={sha256(rom)}")
    print(f"sum32 before=0x{s_before:08x}  after=0x{s_after:08x}  "
          f"delta=0x{(s_after - s_before) & 0xFFFFFFFF:08x}")
    if args.fix_checksums:
        print("Checksum самосогласованы. Уровень проверки: code/offline; hardware-проверка не выполнена.")
    else:
        print("ВНИМАНИЕ: checksum не пересчитан. Образ не для записи (см. immo-always-id-ok.md).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
