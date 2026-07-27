# 23710-1ND3B

Stock ROM для V36 Skyline Coupe с VQ37VHR. Образ импортирован в проект
2026-07-15.

## Состав

- `11ND3B-20260715-stock.bin` – flash-ROM, 1 572 864 байт (`0x180000`);
- `11ND3B-20260715-stock.bin.md5` – MD5 sidecar.

Хеши ROM:

- SHA-256: `0e428cff9e601db74b380ae2e05d3c4ec0ff31313eb7d70aa3badd49a232ec7e`;
- MD5: `03e5c24d571c76685b998652e02ec073`.

## Идентификация

| Поле | Значение | Смещение в ROM |
|---|---|---:|
| ECM part # | `23710-1ND3B` | идентификация комплекта |
| Калибровка | `11ND3B00000` | `0x8204` |
| Идентификатор ПО | `8FZ35NEE6` | `0x6F09` |
| Класс EFI / MCU | `SH705927N` | `0x50D2` |

Флаг Developer Immobilizer находится по `0x8668`: stock `01`, immo-off `00`.
`patches/apply_immo_off.py --rom 1ND3B --verify-only` проверяет точный stock ROM,
SHA-256 и исходное значение байта. Производные образы для этого ROM не хранятся.
