# ROM images – манифест дампов

Ground-truth ROM-дампы проекта **VQ HR ECU**: образы с RomRaider forum и собственные
чтения физических ЭБУ.
Исходные бинарники (`*.bin`) версионируются в git; дублирующие архивы не хранятся.
Этот файл – манифест идентификации. Дамп опознаётся по `sha256`.

## Структура и имена

На верхнем уровне находятся только каталоги ECM part # в формате `23710-XXXXX`,
общий манифест и машинный реестр:

```text
rom-images/
  23710-XXXXX/
    README.md
    <rom-id>-<YYYYMMDD>-stock.bin
    <rom-id>-<YYYYMMDD>-stock.bin.md5
    <прочие артефакты>
    mods/
      <short-desc>/
        README.md
        <rom-id>-<YYYYMMDD>-<short-desc>.bin
        <rom-id>-<YYYYMMDD>-<short-desc>.bin.md5
  README.md
  roms.csv
```

`rom-id` берётся из калибровочного идентификатора внутри ROM, например `1JK08A`
или `11ND0A`. Дата означает:

- дату чтения для собственного дампа;
- дату импорта в репозиторий для внешнего stock-образа;
- дату выпуска для модификации.

`short-desc` записывается строчными ASCII-словами через дефис. MD5 sidecar имеет
имя `<binary>.md5` и GNU-формат `<md5> *<filename>`. SHA-256 является основным
идентификатором и хранится в `roms.csv`, README каталога и README модификации.
Пустой `mods/` не хранится.

Структура, имена, `roms.csv` и MD5 sidecar-файлы проверяются командой:

```bash
python3 -m unittest patches.tests.test_rom_images_layout -v
```

`1ND0A` / `1ND3B` (1.5 MiB, SH7059, JDM) и `JK78C` (1.0 MiB, SH7058, USDM) – **VQ37VHR**,
один мотор в двух поколениях ЭБУ, гомолог-пара для реверса. `JK03A` и `JK08A` (1.0 MiB,
SH7058, JDM) – **VQ25HR** V36 Skyline 250GT: JK03A является форумным комплектом
`ROM + внешний SPI EEPROM`, JK08A – собственное чтение целевого ЭБУ машины без EEPROM.
`JK00D` (1.0 MiB, SH7058) – собственный ROM физического стендового ЭБУ **VQ35HR**.
Документация физических блоков и проекта находится в Obsidian:
`🎛️ Electronics/VQ HR ECU Tuning` (см. `../AGENTS.md`).

Ядро MCU – **SH-2E** (SH-2 + single-precision FPU), подтверждено даташитом Renesas
(`../refs/renesas-sh7059-sh7058s-hardware-manual.pdf`). В Ghidra грузить вариантом
`SuperH:BE:32:SH-2A` (единственный штатный с FPU).

## Дампы

| Файл | Размер (байт) | Флеш / MCU | ECM part # | Авто | Мотор | Рынок | Шина |
|------|--------------:|-----------|-----------|------|-------|-------|------|
| `23710-1ND0A/11ND0A-20260715-stock.bin` | 1 572 864 (0x180000) | 1.5 MiB / SH7059 * | 23710-1ND0A | V36 Skyline Coupe (CKV36) | VQ37VHR | JDM | CAN * |
| `23710-1ND3B/11ND3B-20260715-stock.bin` | 1 572 864 (0x180000) | 1.5 MiB / SH7059 * | 23710-1ND3B | V36 Skyline Coupe (CKV36) | VQ37VHR | JDM | CAN * |
| `23710-JK00D/1JK00D-20260726-stock.bin` | 1 048 576 (0x100000) | 1.0 MiB / SH7058 (`SH705822N`) | 23710-JK00D | стендовый ЭБУ | VQ35HR | не установлен | CAN |
| `23710-JK03A/1JK03A-20260715-stock.bin` | 1 048 576 (0x100000) | 1.0 MiB / SH7058 | 23710-JK03A | V36 Skyline 250GT | VQ25HR | JDM | CAN * |
| `23710-JK08A/1JK08A-20260726-stock.bin` | 1 048 576 (0x100000) | 1.0 MiB / SH7058 (`SH705822N`) | 23710-JK08A | V36 Skyline 250GT | VQ25HR | JDM | CAN |
| `23710-JK78C/1JK78C-20260715-stock.bin` | 1 048 576 (0x100000) | 1.0 MiB / SH7058 * | 23710-JK78C | Infiniti G37 (2008-09) | VQ37VHR | USDM | CAN * |

Префикс `23710` – Nissan/Infiniti part # для ECM (по каталогу parts.nissanusa).

`JK03A` – комплект в `23710-JK03A/`: главный flash
`1JK03A-20260715-stock.bin` и внешний **SPI EEPROM ST95320**
`ST95320-20260715-nats-sync.bin` (4096 B, NATS synchronization/adaptation).
MCU (`SH705822N`), софт (`7MFKAVN86`) и калибровка (`1JK03A00000`) самоидентифицируются
строками внутри образа; immo-контур разобран в
`../patches/immo-off-developer-flag.md`.
Подробный состав и хеши находятся в `23710-JK03A/README.md`.

`JK08A` – собственное чтение целевого ЭБУ V36 Skyline 250GT от 2026-07-26. PCMFlash
1.2.0, модуль 18 через Scanmatik-SM2 USB; внутри ROM находятся `1JK08A00000`,
`7MFKAVN86` и `SH705822N`. От JK03A отличается 121 байтовая позиция в
`0x008200..0x0190c9`, при этом `0x000000..0x0081ff` и весь `0x020000..0x0fffff`
совпадают побайтно. Код и флаг Developer Immobilizer по `0x8725` являются exact-match;
calibration/config данные не тождественны. Комплект не содержит EEPROM и снимка PCMFlash.
Полная локальная идентификация находится в `23710-JK08A/README.md`.

`JK00D` – собственное чтение физического стендового ЭБУ от 2026-07-26. PCMFlash 1.2.0,
модуль 18 через Scanmatik-SM2 USB, сообщает `23710-JK00D`, калибровку `1JK00D00000`,
основной номер `8MFK36N15`, тип `SH705822N` и протокол Hitachi CAN. Те же калибровка,
основной номер и тип присутствуют строками в ROM по `0x8204`, `0x7009` и `0x50C6`.
Комплект не содержит чтения внешнего EEPROM; его наличие этим не опровергается.
Полная локальная идентификация находится в `23710-JK00D/README.md`.

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
Производные образы в реестр stock-источников не входят; их хеши находятся в README
конкретного мода.

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
  уверенность**. Дамп EEPROM `ST95320-20260715-nats-sync.bin` из того же поста.
- `JK08A`: собственный физический целевой блок V36 Skyline 250GT. Part # и способ чтения
  подтверждены локальным provenance; идентификатор ПО, калибровка, SH7058-класс и размер
  flash подтверждены содержимым ROM – **высокая уверенность**. Внешний EEPROM не прочитан.
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

## Производный образ immo-off

`23710-JK08A/mods/immo-off/1JK08A-20260727-immo-off.bin` выпускается
`../patches/apply_immo_off.py` из точного stock JK08A. Изменяется только
`ROM[0x8725].bit0`: байт `01` -> `00`. Это заводской флаг Developer Immobilizer,
исполнительная цепочка которого описана в `../patches/immo-off-developer-flag.md`.

| Файл | Размер | Изменение | SHA-256 | Статус |
|---|---:|---|---|---|
| `23710-JK08A/mods/immo-off/1JK08A-20260727-immo-off.bin` | 1 048 576 | `0x8725: 01 -> 00` | `de7f99cfb592d1cd1d83706f08cbea99ad0aef8602090d009cb37e9d37080d8c` | код подтверждён, проверка запуска ожидается |

Хранимые checksum-поля совпадают со stock; штатную коррекцию выполняет флешер при
записи. Тест патчера побайтно проверяет, что производный файл отличается от stock
ровно одним битом.
