# ROM images – манифест дампов

Ground-truth ROM-дампы проекта **VQ HR ECU**: образы с RomRaider forum и собственное
чтение физического стендового ЭБУ.
Бинарники (`*.bin`, `*.zip`, `*.7z`) версионируются в git; этот файл – манифест
идентификации. Дамп опознаётся по `sha256`.

`1ND0A` / `1ND3B` (1.5 MiB, SH7059, JDM) и `JK78C` (1.0 MiB, SH7058, USDM) – **VQ37VHR**,
один мотор в двух поколениях ЭБУ, гомолог-пара для реверса. `JK03A` (1.0 MiB, SH7058, JDM) –
**VQ25HR** той же модели, что тестовая платформа проекта (V36 Skyline 250GT), комплект
`ROM + внешний SPI EEPROM` (единственный комплект с EEPROM). `JK00D` (1.0 MiB, SH7058) –
собственный ROM физического стендового ЭБУ **VQ35HR**. Целевой `23710-JK08A` машины
дампом не снят. Документация физических блоков – в Obsidian-проекте (`../AGENTS.md`).
Документация проекта – в Obsidian:
`🎛️ Electronics/VQ HR ECU Tuning` (см. `../AGENTS.md`).

Ядро MCU – **SH-2E** (SH-2 + single-precision FPU), подтверждено даташитом Renesas
(`../refs/renesas-sh7059-sh7058s-hardware-manual.pdf`). В Ghidra грузить вариантом
`SuperH:BE:32:SH-2A` (единственный штатный с FPU).

## Дампы

| Файл | Размер (байт) | Флеш / MCU | ECM part # | Авто | Мотор | Рынок | Шина |
|------|--------------:|-----------|-----------|------|-------|-------|------|
| `1ND0A_Stock.bin` | 1 572 864 (0x180000) | 1.5 MiB / SH7059 * | 23710-1ND0A | V36 Skyline Coupe (CKV36) | VQ37VHR | JDM | CAN * |
| `1ND3B_Stock.bin` | 1 572 864 (0x180000) | 1.5 MiB / SH7059 * | 23710-1ND3B | V36 Skyline Coupe (CKV36) | VQ37VHR | JDM | CAN * |
| `JK78C.bin`       | 1 048 576 (0x100000) | 1.0 MiB / SH7058 * | 23710-JK78C | Infiniti G37 (2008-09)     | VQ37VHR | USDM | CAN * |
| `v36-vq25hr-jk03a/as7058.bin` | 1 048 576 (0x100000) | 1.0 MiB / SH7058 | 23710-JK03A | V36 Skyline 250GT | VQ25HR | JDM | CAN * |
| `1JK00D_8MFK36N15-20260726-013734/1JK00D_8MFK36N15-20260726-013734.bin` | 1 048 576 (0x100000) | 1.0 MiB / SH7058 (`SH705822N`) | 23710-JK00D | стендовый ЭБУ | VQ35HR | не установлен | CAN |

Префикс `23710` – Nissan/Infiniti part # для ECM (по каталогу parts.nissanusa).

`JK03A` – комплект в подкаталоге `v36-vq25hr-jk03a/`: главный флеш `as7058.bin` (SH7058) +
внешний **SPI EEPROM ST95320** `95320my_sinhro.bin` (4096 B, NATS synchro/adaptation store).
MCU (`SH705822N`), софт (`7MFKAVN86`) и калибровка (`1JK03A00000`) самоидентифицируются
строками внутри образа; immo-контур разобран в `../patches/immo-always-id-ok.md` (секция JK03A).
Провенанс форумного поста – `v36-vq25hr-jk03a/README.md`.

`JK00D` – собственное чтение физического стендового ЭБУ от 2026-07-26. PCMFlash 1.2.0,
модуль 18 через Scanmatik-SM2 USB, сообщает `23710-JK00D`, калибровку `1JK00D00000`,
основной номер `8MFK36N15`, тип `SH705822N` и протокол Hitachi CAN. Те же калибровка,
основной номер и тип присутствуют строками в ROM по `0x8204`, `0x7009` и `0x50C6`.
Комплект не содержит чтения внешнего EEPROM; его наличие этим не опровергается.
Полный локальный провенанс – в
`1JK00D_8MFK36N15-20260726-013734/README.md`.

`*` Размеры флеша (1.0 / 1.5 MiB) и ядро **SH-2E** подтверждены даташитом Renesas;
конкретная модель чипа на плате (SH7058 vs SH7059) и шина CAN выведены из размера флеша
и семейства ЭБУ (Hitachi HR CAN) – финальная сверка дизассемблированием / маркировкой.
Перекрёстно: PCMflash Module 18 покрывает `EFI SH705927N (Hitachi SH7059/1.5MB)` –
класс `1ND`-дампов; USDM-серия в списке – `EFI SH70582xN (Hitachi SH7058/1MB)`
(класс `JK78C`). => `../refs/pcmflash-module-list.md`.

### sha256 (идентификация)

Реестр `roms.csv` (строка = файл дампа: путь, метка ROM в графе, sha256). Он машинный:
пайплайн карт берёт образ по метке и сверяет хеш перед чтением значений
(`../tools/mapkit/rom.py`, Stage 4), поэтому опознание дампа – условие прогона, а не
справка для человека. Метка пуста у образа, которого граф не несёт (EEPROM).

Компрессированные копии (`1ND0A_Stock.zip`, `1ND3B_Stock.zip`, `JK78C.7z`,
`v36-vq25hr-jk03a/as7058.bin.zip`, `v36-vq25hr-jk03a/95320my_sinhro.bin.zip`) – архивы
соответствующих `.bin`.

### Происхождение и уверенность

- `1ND0A`: RomRaider тред t=22253 (CKV36, FID `8FZ35NEE6`). Мотор и авто – высокая
  уверенность; привязка part # -> CKV36 и FID – **forum-grade** (сверить чтением дампа).
- `1ND3B`: RomRaider тред t=22328 ("Does anyone have the CKV36 file? (237101ND3B)").
  Высокая; **forum-grade**.
- `JK78C`: RomRaider-треда не найдено; идентификация по каталогам part # (серия
  23710-JK7xC = 2008 Infiniti G37 3.7L). **Catalog-grade** (mintt / fs1inc; оригинал
  23710-JK78B в перечне замен указывает JK78C).
- `JK03A`: RomRaider тред t=11098 "Nissan stock ROM list" (Break_Neck, пост p=150228):
  Skyline V36 VQ25HR 2WD 5AT, 23710-JK03A, SW `7MFKAVN86`, 7058 MCU, "ROM + SPI EEPROM".
  Part # / SW / калибровка (`1JK03A00000`) подтверждены строками внутри образа – **высокая
  уверенность**. Дамп EEPROM (`95320my_sinhro`) из того же поста.
- `JK00D`: собственный физический стендовый блок. Part #, идентификатор ПО, калибровка,
  SH7058-класс, размер flash и CAN подтверждены чтением и идентификацией PCMFlash –
  **высокая уверенность**. Модель автомобиля и рынок исходного донора не установлены;
  внешний EEPROM не прочитан.
- Дельта `1ND0A` vs `1ND3B` (год / комплектация / ревизия) и точные модельные годы –
  не установлены.

### Источники

- 1ND0A: https://www.romraider.com/forum/viewtopic.php?f=65&t=22253
- 1ND3B: https://www.romraider.com/forum/viewtopic.php?f=65&t=22328
- V36 Coupe specs (11ND2A / VQ37VHR / JDM / 2008): https://www.romraider.com/forum/viewtopic.php?f=64&t=22280
- Эволюция флеша 1 MB -> 1.5 MB: https://www.romraider.com/forum/viewtopic.php?f=65&t=21905
- Nissan stock ROM list (Z34 VQ37VHR loader 705927): https://www.romraider.com/forum/viewtopic.php?f=65&t=11098
- JK03A (V36 VQ25HR 2WD 5AT, ROM + SPI EEPROM, Break_Neck): https://www.romraider.com/forum/viewtopic.php?p=150228#p150228
- JK7x = 2008 Infiniti G37 3.7L: https://www.fs1inc.com/23710-jk78a-2008-infiniti-g37-3-7l-pcm-engine-computer-ecm-ecu-programmed-plug-play.html
- 23710 = Nissan ECM part #: https://parts.nissanusa.com/parts/nissan-engine-control-module-ecm-23710zv24a
- Renesas SH7059 / SH7058S (ядро SH-2E, 1.5 / 1.0 MiB flash): https://www.renesas.com/en/document/mah/sh-2e-sh7059-f-ztattm-sh7058s-f-ztattm-hardware-manual
- PCMflash module list (Module 18 SH705927N / SH7059): https://scanmatik.ru/downloads/PCM_module_list.pdf
- VQ engine / VVEL: https://en.wikipedia.org/wiki/Nissan_VQ_engine

Ground truth – в железе; part # и тред – ориентир, финальная сверка дизассемблированием.

## Патченые образы (immo always-ID-OK)

Выходы `../patches/apply_immo_patch.py` (спека – `../patches/immo-always-id-ok.md`): форсируют
ECM-side "ID OK" и снимают immo-Lock. Суффикс `_UNCHECKSUMMED` – checksum не пересчитан
(пересчёт на стороне флешера, SM2PRO). Версионируются в git.

| Файл | База | Патч |
|------|------|------|
| `1ND0A_immo-id-ok_UNCHECKSUMMED.bin` | `1ND0A_Stock.bin` | L1+L2 (ядро) |
| `1ND0A_immo-id-ok_l2b_UNCHECKSUMMED.bin` | `1ND0A_Stock.bin` | L1+L2+L2b |
| `JK03A_immo-id-ok_UNCHECKSUMMED.bin` | `v36-vq25hr-jk03a/as7058.bin` | L1+L2 (ядро) |
| `JK03A_immo-id-ok_l2b_esc_UNCHECKSUMMED.bin` | `v36-vq25hr-jk03a/as7058.bin` | L1+L2+L2b+esc |
| `JK78C_immo-id-ok_l2b_esc_UNCHECKSUMMED.bin` | `JK78C.bin` | L1+L2+L2b+esc |

### sha256 (патченые)

- `1ND0A_immo-id-ok_UNCHECKSUMMED.bin` – `f860581a64517309b1e66c0b1e96024c250d28bc777e25c32a7fba615e730d35`
- `1ND0A_immo-id-ok_l2b_UNCHECKSUMMED.bin` – `d60828140946fd6c1cd5e5ca211252e338f952182293f296522ca5ad3bee3d13`
- `JK03A_immo-id-ok_UNCHECKSUMMED.bin` – `432ef461acad0373176244e1123c3c2b8a0908c48887ac3f1d32a2e204b6ba06`
- `JK03A_immo-id-ok_l2b_esc_UNCHECKSUMMED.bin` – `d39661b71def4a768280c46134cff2e378d7a55a36935d5609026bc0f55957d0`
- `JK78C_immo-id-ok_l2b_esc_UNCHECKSUMMED.bin` – `a7cf5b91789e934b5f4febd6579a15e8b609eb0d45b8261b13e61d5bef520cc9`
