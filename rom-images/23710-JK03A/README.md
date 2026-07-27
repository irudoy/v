# 23710-JK03A

Stock-комплект для V36 Skyline 250GT 2WD 5AT с VQ25HR. Главный ROM и внешний
SPI EEPROM импортированы в проект 2026-07-15.

## Состав

- `1JK03A-20260715-stock.bin` – flash-ROM, 1 048 576 байт (`0x100000`);
- `1JK03A-20260715-stock.bin.md5` – MD5 sidecar главного ROM;
- `ST95320-20260715-nats-sync.bin` – внешний SPI EEPROM, 4096 байт;
- `ST95320-20260715-nats-sync.bin.md5` – MD5 sidecar EEPROM.

Хеши главного ROM:

- SHA-256: `f78929547c08dc5ecde256fb3a6f6f3ef6daa9010e1531b3eac99fd9509225b4`;
- MD5: `52b9f9dcb2b0336d842eb29b66f9037e`.

Хеши EEPROM:

- SHA-256: `68bb95f6ed70ec247f752a2d6817c83f14cdb7dc9db55c316852c0be0d362aaf`;
- MD5: `e836c9331545113460eac37c5c3b6f82`.

## Идентификация

| Поле | Значение | Смещение в ROM |
|---|---|---:|
| ECM part # | `23710-JK03A` | идентификация комплекта |
| Калибровка | `1JK03A00000` | `0x8204` |
| Идентификатор ПО | `7MFKAVN86` | `0x6F09` |
| Класс EFI / MCU | `SH705822N` | `0x50C6` |

`ST95320-20260715-nats-sync.bin` содержит данные NATS synchronization/adaptation и
не является flash-ROM MCU. В `roms.csv` он присутствует без метки графа.

Флаг Developer Immobilizer главного ROM находится по `0x8725`: stock `01`,
immo-off `00`. JK03A и JK08A имеют побайтно одинаковый исполняемый код.
Производные образы JK03A не хранятся.
