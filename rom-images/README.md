# ROM images – манифест дампов

Ground-truth ROM-дампы проекта **VQ HR ECU**, происхождение – RomRaider forum.
Бинарники (`*.bin`, `*.zip`, `*.7z`) версионируются в git; этот файл – манифест
идентификации. Дамп опознаётся по `sha256`.

`1ND0A` / `1ND3B` (1.5 MiB, SH7059, JDM) и `JK78C` (1.0 MiB, SH7058, USDM) – **VQ37VHR**,
один мотор в двух поколениях ЭБУ, гомолог-пара для реверса. `JK03A` (1.0 MiB, SH7058, JDM) –
**VQ25HR** той же модели, что тестовая платформа проекта (V36 Skyline 250GT), комплект
`ROM + внешний SPI EEPROM` (единственный дамп с EEPROM). Блок самой платформы – `23710-JK08A`,
дампа с него нет (см. "Блок тестовой платформы"). Документация проекта – в Obsidian:
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

Префикс `23710` – Nissan/Infiniti part # для ECM (по каталогу parts.nissanusa).

`JK03A` – комплект в подкаталоге `v36-vq25hr-jk03a/`: главный флеш `as7058.bin` (SH7058) +
внешний **SPI EEPROM ST95320** `95320my_sinhro.bin` (4096 B, NATS synchro/adaptation store).
MCU (`SH705822N`), софт (`7MFKAVN86`) и калибровка (`1JK03A00000`) самоидентифицируются
строками внутри образа; immo-контур разобран в `../patches/immo-always-id-ok.md` (секция JK03A).

`*` Размеры флеша (1.0 / 1.5 MiB) и ядро **SH-2E** подтверждены даташитом Renesas;
конкретная модель чипа на плате (SH7058 vs SH7059) и шина CAN выведены из размера флеша
и семейства ЭБУ (Hitachi HR CAN) – финальная сверка дизассемблированием / маркировкой.
Перекрёстно: PCMflash Module 18 покрывает `EFI SH705927N (Hitachi SH7059/1.5MB)` –
класс `1ND`-дампов; USDM-серия в списке – `EFI SH70582xN (Hitachi SH7058/1MB)`
(класс `JK78C`). => `../refs/pcmflash-module-list.md`.

### sha256 (идентификация)

- `1ND0A_Stock.bin` – `650d3d3d5f1fdefdb310820a990d6e1a49baa1e072e51ee0019c0b69fd6da978`
- `1ND3B_Stock.bin` – `0e428cff9e601db74b380ae2e05d3c4ec0ff31313eb7d70aa3badd49a232ec7e`
- `JK78C.bin`       – `86387d1de1daa8bf5f98e071eb899be462b7a466cb43f88a96e4dc8b87892b8d`
- `v36-vq25hr-jk03a/as7058.bin`        – `f78929547c08dc5ecde256fb3a6f6f3ef6daa9010e1531b3eac99fd9509225b4`
- `v36-vq25hr-jk03a/95320my_sinhro.bin` – `68bb95f6ed70ec247f752a2d6817c83f14cdb7dc9db55c316852c0be0d362aaf`

Компрессированные копии (`1ND0A_Stock.zip`, `1ND3B_Stock.zip`, `JK78C.7z`) – архивы
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

## Блок тестовой платформы – 23710-JK08A

ЭБУ на самой тестовой платформе (V36 Skyline 250GT, VQ25HR) – **23710-JK08A**: part #
прочитан с блока диагностикой CONSULT-III Plus (Ver. 240.10), вкладка `ECU Identification`
раздела `ENGINE`. Прямое чтение с железа – уверенность выше, чем у forum- и catalog-grade
идентификаций дампов в таблице.

Дампа `JK08A` нет: канал чтения (KESS V2 по OBD) не заведён. Известен только part #; MCU,
размер флеша, SW-версия и калибровочная строка – TO-VERIFY по дампу. Дельта `JK03A` vs
`JK08A` (модельный год, комплектация, трансмиссия, ревизия калибровки) не установлена.

RE VQ25HR идёт по `JK03A` – тот же мотор, кузов и рынок, ближайший доступный образ. Все
адресные выводы проекта по VQ25HR (`../defs/JK03A.xml`, `../defs/JK03A.notes.md`,
`../defs/JK03A.maps.csv`, секция JK03A в `../patches/immo-always-id-ok.md`) описывают образ
`JK03A`. Перенос на `JK08A` – сверкой снятого дампа: внутри HR даже соседние калибровки
одной модели держат карты по разным адресам (`../defs/README.md`: EV15A vs EV18A, оба
350Z HR), поэтому общие мотор и кузов переносимости адресов не дают.
