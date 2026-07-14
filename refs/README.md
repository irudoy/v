# refs – внешние даташиты и мануалы

Локальные копии первоисточников проекта **VQ HR ECU** (см. `../AGENTS.md`).
PDF-оригиналы **git-ignored** (проприетарные, крупные); трекаются markitdown-конверсии
`*.md` (кроме крупного Renesas HW manual) и этот манифест. Конверсия: markitdown.
Ноты в Obsidian ссылаются на эти файлы как `refs/<имя>.md` / `.pdf`.

## Документы

| Файл (`.pdf` + `.md`) | Стр | Тип | Что внутри |
|-----------------------|----:|-----|------------|
| `renesas-sh7059-sh7058s-hardware-manual` | 1050 | Renesas datasheet | SH7058S / SH7059 F-ZTAT HW manual: ядро **SH-2E**, flash (1.0 / 1.5 MB), RAM, on-chip **HCAN-II** (CAN 2.0B), FPU, периферия, регистры. `.md` git-ignored (крупный). |
| `pcmflash-module-list` | 18 | PCMflash list | Модули reflash. **Module 18 "Nissan/Infiniti CAN-bus"** – `EFI SH705927N (Hitachi SH7059/1.5MB) [RD/WR/CK]`; **Module 42 "Denso SH705X Bootloader"**. |
| `bosch-lsu-4.9-datasheet` | 4 | Bosch datasheet | Сенсор Bosch LSU 4.9 (планарный ZrO2, 5-провод, single-cell), основа AEM UEGO X-Series. |
| `nissan-ners-techinfo` | 9 | Nissan (first-party) | NERS (Nissan ECU Reprogramming Software) через J2534: только подписанные калибровки по part #, без сырого дампа. |
| `motec-m150-datasheet` | 7 | MoTeC datasheet | ЭБУ M150: I/O (10 half-bridge выходов и др.), спецификации. |
| `uprev-nissan-tuning-guide` | 28 | UpRev (vendor) | Тюнинг-гайд Nissan/Infiniti (reflash стокового ЭБУ, boost, failsafes; контекст NATS / лицензии). |

## sha256 (PDF-оригиналы)

- `renesas-sh7059-sh7058s-hardware-manual.pdf` – `6d8b0e3511ed583df0bec31d0d28641d1b06b23042985f41ad2d9df44fccd8ca`
- `pcmflash-module-list.pdf` – `3168d6e18d4d3de22d65a6926ce66c3019ed16252b325314a857223818520673`
- `bosch-lsu-4.9-datasheet.pdf` – `049837312a1edfb9e01e5fa767e86ab2a67697cc3fafd20c9b02674e51dac8c7`
- `nissan-ners-techinfo.pdf` – `5488a68bacd51bb4f77f0ad628184530d690abb9ab81ab3d06ba0801922b1b6a`
- `motec-m150-datasheet.pdf` – `ca9f400d314ebeecd7e3cdbd7c7a4bab9280737154519ab6c2286dbd4845910c`
- `uprev-nissan-tuning-guide.pdf` – `e337931010c4c9996f7f9556947f63613c73fe847c66a5b810878a665e48707e`

## Источники (URL)

- Renesas SH7059 / SH7058S HW manual (SH-2E, REJ09B0177): https://www.renesas.com/en/document/mah/sh-2e-sh7059-f-ztattm-sh7058s-f-ztattm-hardware-manual
- PCMflash module list: https://scanmatik.ru/downloads/PCM_module_list.pdf
- Bosch LSU 4.9 datasheet (зеркало): https://www.milspecwiring.com/DATA%20SHEETS/lambda/BoschLSU4.9Sensor.pdf
- Nissan NERS TechInfo: https://www.nissan-techinfo.com/documents/Nissan_TechInfo_Ners.pdf
- MoTeC M150 datasheet (зеркало): https://www.milspecwiring.com/DATA%20SHEETS/ECU/M150.pdf
- UpRev Nissan Tuning Guide: https://uprev.com/wp-content/uploads/2023/05/UpRev-Nissan-Tuning-Guide-Rev2.pdf

Восстановить локально: скачать PDF по URL в `refs/`, конвертировать markitdown в `*.md`.
