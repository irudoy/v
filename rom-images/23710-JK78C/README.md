# 23710-JK78C

Stock ROM для Infiniti G37 с VQ37VHR. Образ импортирован в проект 2026-07-15.

## Состав

- `1JK78C-20260715-stock.bin` – flash-ROM, 1 048 576 байт (`0x100000`);
- `1JK78C-20260715-stock.bin.md5` – MD5 sidecar.

Хеши ROM:

- SHA-256: `86387d1de1daa8bf5f98e071eb899be462b7a466cb43f88a96e4dc8b87892b8d`;
- MD5: `8844cec42335c7fccf3695e64dd5f64f`.

## Идентификация

| Поле | Значение | Смещение в ROM |
|---|---|---:|
| ECM part # | `23710-JK78C` | идентификация комплекта |
| Калибровка | `1JK78C00000` | `0x8204` |
| Основной номер | `7MFVH3NM1` | `0x6F09` |
| Идентификатор ПО | `7MFV68NV` | `0x7009` |
| Класс EFI / MCU | `SH705822N` | `0x50C6` |

Флаг Developer Immobilizer находится по `0x861C`: stock `01`, immo-off `00`.
`patches/apply_immo_off.py --rom JK78C --verify-only` проверяет точный stock ROM,
SHA-256 и исходное значение байта. Производные образы для этого ROM не хранятся.
