# 23710-1ND0A

Stock ROM для V36 Skyline Coupe с VQ37VHR. Образ импортирован в проект
2026-07-15.

## Состав

- `11ND0A-20260715-stock.bin` – flash-ROM, 1 572 864 байт (`0x180000`);
- `11ND0A-20260715-stock.bin.md5` – MD5 sidecar.

Хеши ROM:

- SHA-256: `650d3d3d5f1fdefdb310820a990d6e1a49baa1e072e51ee0019c0b69fd6da978`;
- MD5: `a2e4dc6b25390cb67517922f1c32d550`.

## Идентификация

| Поле | Значение | Смещение в ROM |
|---|---|---:|
| ECM part # | `23710-1ND0A` | идентификация комплекта |
| Калибровка | `11ND0A00000` | `0x8204` |
| Идентификатор ПО | `8FZ35NEE6` | `0x6F09` |
| Класс EFI / MCU | `SH705927N` | `0x50D2` |

Флаг Developer Immobilizer находится по `0x8668`: stock `01`, immo-off `00`.
`patches/apply_immo_off.py --rom 1ND0A --verify-only` проверяет точный stock ROM,
SHA-256 и исходное значение байта. Производные образы для этого ROM не хранятся.
