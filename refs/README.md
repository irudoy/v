# refs – внешние даташиты и мануалы

Локальные копии первоисточников проекта **VQ HR ECU** (см. `../AGENTS.md`).
PDF-оригиналы и markitdown-конверсии `*.md` версионируются в git вместе с этим манифестом.
Конверсия: markitdown. Ноты в Obsidian ссылаются на эти файлы как `refs/<имя>.md` / `.pdf`.

## Документы

| Файл (`.pdf` + `.md`) | Стр | Тип | Что внутри |
|-----------------------|----:|-----|------------|
| `renesas-sh7059-sh7058s-hardware-manual` | 1050 | Renesas datasheet | SH7058S / SH7059 F-ZTAT HW manual: ядро **SH-2E**, flash (1.0 / 1.5 MB), RAM, on-chip **HCAN-II** (CAN 2.0B), FPU, периферия, регистры. |
| `pcmflash-module-list` | 18 | PCMflash list | Модули reflash. **Module 18 "Nissan/Infiniti CAN-bus"** – `EFI SH705927N (Hitachi SH7059/1.5MB) [RD/WR/CK]`; **Module 42 "Denso SH705X Bootloader"**. |
| `bosch-lsu-4.9-datasheet` | 4 | Bosch datasheet | Сенсор Bosch LSU 4.9 (планарный ZrO2, 5-провод, single-cell), основа AEM UEGO X-Series. |
| `nissan-ners-techinfo` | 9 | Nissan (first-party) | NERS (Nissan ECU Reprogramming Software) через J2534: только подписанные калибровки по part #, без сырого дампа. |
| `motec-m150-datasheet` | 7 | MoTeC datasheet | ЭБУ M150: I/O (10 half-bridge выходов и др.), спецификации. |
| `uprev/UpRev-Nissan-Tuning-Guide-Rev2` | 28 | UpRev (vendor) | Тюнинг-гайд Nissan/Infiniti (reflash стокового ЭБУ, boost, failsafes; контекст NATS / лицензии). `.pdf` + markitdown `.md`. |
| `uprev/UpRev-User-Guide-Rev2` | 12 | UpRev (vendor) | Руководство пользователя UpRev (тулинг reflash, workflow). Только `.pdf`. |
| `uprev/ECU-Bench-Harness-Pinouts` | 1 | UpRev (vendor) | Распиновка стендового bench-harness ЭБУ (одностраничник). Только `.pdf`. |

## sha256 (PDF-оригиналы)

- `renesas-sh7059-sh7058s-hardware-manual.pdf` – `6d8b0e3511ed583df0bec31d0d28641d1b06b23042985f41ad2d9df44fccd8ca`
- `pcmflash-module-list.pdf` – `3168d6e18d4d3de22d65a6926ce66c3019ed16252b325314a857223818520673`
- `bosch-lsu-4.9-datasheet.pdf` – `049837312a1edfb9e01e5fa767e86ab2a67697cc3fafd20c9b02674e51dac8c7`
- `nissan-ners-techinfo.pdf` – `5488a68bacd51bb4f77f0ad628184530d690abb9ab81ab3d06ba0801922b1b6a`
- `motec-m150-datasheet.pdf` – `ca9f400d314ebeecd7e3cdbd7c7a4bab9280737154519ab6c2286dbd4845910c`
- `uprev/UpRev-Nissan-Tuning-Guide-Rev2.pdf` – `e337931010c4c9996f7f9556947f63613c73fe847c66a5b810878a665e48707e`
- `uprev/UpRev-User-Guide-Rev2.pdf` – `f6ade3f275e234c6533c640ff0fadba4ceb3ffa212aa846c2b488ee83dd3d5bd`
- `uprev/ECU-Bench-Harness-Pinouts.pdf` – `335650facbc45a3a3d056e196fb78c715f8c352f4e92bad75c158fa425cbe4f8`

## Источники (URL)

- Renesas SH7059 / SH7058S HW manual (SH-2E, REJ09B0177): https://www.renesas.com/en/document/mah/sh-2e-sh7059-f-ztattm-sh7058s-f-ztattm-hardware-manual
- PCMflash module list: https://scanmatik.ru/downloads/PCM_module_list.pdf
- Bosch LSU 4.9 datasheet (зеркало): https://www.milspecwiring.com/DATA%20SHEETS/lambda/BoschLSU4.9Sensor.pdf
- Nissan NERS TechInfo: https://www.nissan-techinfo.com/documents/Nissan_TechInfo_Ners.pdf
- MoTeC M150 datasheet (зеркало): https://www.milspecwiring.com/DATA%20SHEETS/ECU/M150.pdf
- UpRev Nissan Tuning Guide: https://uprev.com/wp-content/uploads/2023/05/UpRev-Nissan-Tuning-Guide-Rev2.pdf
- NissanECU RE wiki (зеркало -> `nissanecu-wiki/`): https://nissanecu.miraheze.org/wiki/Main_Page
- EcuTek Support KB, 370Z ProECU (конверсия -> `ecutek/`): https://ecutek.atlassian.net/wiki/spaces/SUPPORT/pages/7143430

Восстановить локально: скачать PDF по URL в `refs/`, конвертировать markitdown в `*.md`.

## NissanECU RE wiki (локальное зеркало)

`nissanecu-wiki/` – полное зеркало community-вики реверса Nissan-ЭБУ (fenugrec),
**30 страниц + 34 изображения**, markdown-конверсия рендер-HTML (`?action=render` ->
html2text) с локальными картинками (`img/`). Источник: https://nissanecu.miraheze.org
(**CC BY-SA 4.0**), retrieved 2026-07-15. Индекс и P0-релевантность – `nissanecu-wiki/README.md`.
Ключевое: `Firmware_re` (SID-tree, seed-key SID27/36, LOADER/FID-метаданные), `Checksums`,
`Eeprom_code` / `Eeprom_dumps` (immo / NV вне flash), `Communication_Protocols` / `C2_14230` /
`Std_14230`, `Ecu_hw` / `Bootmode` (HW, boot-режим SH705x), размеченные референс-ROM
`Rom_an_cf43d` / `cf48d` / `al500`. В отличие от PDF-первоисточников, зеркало трекается в git
целиком (текст + мелкие изображения).

## EcuTek 370Z ProECU (локальная конверсия)

`ecutek/` – две страницы базы знаний EcuTek Support (Confluence, пространство `SUPPORT`,
раздел `Vehicle Specific Guides / Nissan / 370Z`), **173 изображения**, markdown-конверсия
рендер-HTML из публичного REST API (`body.export_view`) с локальными картинками, retrieved
2026-07-16. Трекается в git целиком, как и зеркало вики. Индекс, решения при конвертации и
два невосстановимых изображения – `ecutek/README.md`.

370Z несёт VQ37VHR (VVEL) – ту же HR-архитектуру, что и ROM `1ND0A` / `1ND3B`, поэтому
обе страницы релевантны напрямую. Там, где A2L даёт форму таблицы (геометрия, элемент,
scaling, семантика осей), это **вендорское описание смысла**: цепочка расчёта, условия выбора карт и
документированные дефолты – числа, которые ищутся прямо в дампе.

- `tuning-guide/` – таблицы ProECU по системам: `Ignition`, `Fuelling`, `Camshaft Timing`,
  `Boost Control`, `Accelerator and Throttle`, `Limiters`, `Sensor Scaling`, `Torque`, `Idle`.
- `racerom-supplement/` – функции RaceROM: `Map Switching`, `Launch Control`,
  `Per Gear Rev Limits`, `Flat Foot Shifting`, `Flex Fuel`, `Speed Density`, `Custom Maps`,
  `Failsafe`, CAN I/O, `Valet Mode`.

`Map Switching` и `Limiters` описывают механику, которую пайплайн размечает как
`:Flag {role:'selector'}` и `threshold` (Stage 6, `tools/map-flag-pipeline.md`).

## vendor/ – словари в машинном виде

`vendor/` – извлечённое из вендорской документации, сведённое в CSV как опора пайплайна карт
(Stage 5). Первоисточники остаются выше (`ecutek/`, `uprev/`); здесь – их машинная проекция:
каталог имён (`catalog.csv`, 371 запись, из них 243 заводских) и якорные факты (`facts.csv`,
135: константы, единицы, механика, объявленные вендорами пробелы). Грузится в граф
`tools/memgraph/load_vendor.py` как `:VendorEntry`/`:VendorFact`. Метод, правило `origin` и
разметка `concept` – `vendor/README.md`.

Причина отдельного слоя: Map List обоих документов EcuTek – **скриншоты**, то есть каталог
имён недоступен ни grep, ни агенту по тексту; UpRev – сплошная проза без дерева карт.
Транскрипции рукописны (`proecu-maps.csv`, `uprev-maps.csv`), сводный каталог генерируем
(`tools/vendor/build_catalog.py`), и правятся первые, а не он.

## Внешние первоисточники (локально, вне репозитория)

Крупные проприетарные наборы, которые не копируются в `refs/` и не трекаются git;
подключаются как указатель на локальный путь (iCloud Drive). Применяются для точного
определения механики и логики узлов: штатная схемотехника, распиновка разъёмов,
описание работы систем.

- **Nissan ESM – 2007 Infiniti G35 Sedan (V36), мотор VQ35HR.** Полный заводской
  сервис-мануал, 56 PDF по всем системам. 2007 G35 Sedan несёт VQ35HR, поэтому раздел
  ECM служит референсом гомологичной архитектуры NATS в исследуемых HR firmware,
  включая `1ND*` VQ37VHR.
  Путь: `~/Library/Mobile Documents/com~apple~CloudDocs/Auto/Nissan/V36/scheme/2007_G35_Sedan/`
  Ключевые разделы для проекта:
  - `SECURITY CONTROL SYSTEM.pdf` – NATS / immobilizer (IMMU), master-логика BCM,
    security-ID, индикатор. SEC-41/42 задаёт ID-verification BCM с ECM и запрет
    запуска со стороны ECM при незарегистрированном ID; SEC-165 задаёт для
    B2192/B2193 fail-safe `Inhibit engine cranking`. SEC-41 определяет
    B2192/P1611 как `ID DISCORD, IMMU-ECM`: результат проверки ID между BCM и ECM
    равен NG. SEC-42 определяет B2193/P1612 как `CHAIN OF ECM-IMMU`: связь ECM с
    BCM неактивна.
  - `ENGINE CONTROL SYSTEM.pdf` – ECM VQ35HR: вход immo, разрешение запуска,
    входы/выходы. Таблица EC-525 называет P1610 `LOCK MODE` и направляет на SEC-37,
    где заголовок связывает P1610 с B2190 `NATS ANTENNA AMP`; поэтому имя P1610
    само по себе не связывается с конкретным RAM-битом Lock без проверки firmware.
  - `STARTING SYSTEM.pdf` – стартер / crank-permission; crank без запуска переводит
    диагностику в engine control / EC.
  - `BODY CONTROL SYSTEM.pdf` – BCM (master immo), интеграция с ключом/антенной.
  - `LAN SYSTEM.pdf` – топология CAN, gateway, распределение шин и CAN ID.
  - `POWER SUPPLY, GROUND & CIRCUIT ELEMENTS.pdf` – распиновка разъёмов, цепи питания/земли.
  - `METER, WARNING LAMP & INDICATOR.pdf` – security-индикатор (immo-blink), логика лампы.
  - `POWER CONTROL SYSTEM.pdf`, `STEERING CONTROL SYSTEM.pdf` – power/ignition mode, рулевой замок (где применимо).
