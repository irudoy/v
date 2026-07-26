# defs – деф-файлы таблиц ЭБУ

Деф-файлы разметки таблиц ROM для проекта **VQ HR ECU** (см. `../AGENTS.md`).

- `reference/` – локальные референсные копии открытых RomRaider Nissan/Infiniti дефов,
  подключены как git submodules (в репозитории хранится только указатель: commit SHA +
  `.gitmodules`, сами XML не перепубликуются). Референс карт и структуры таблиц, **не**
  рабочие дефы под наш ROM: адреса привязаны к чужим ECUID и напрямую не переносятся.
- Свои дефы под целевые дампы (VQ25HR / VQ37VHR / VQ35HR) – по мере RE, отдельно от `reference/`.

## Submodules (`reference/`)

| Путь | Источник | Pinned SHA | Автор | Лицензия | Внутри |
|------|----------|-----------|-------|----------|--------|
| `reference/Pytrex-NissanDefinitions` | https://github.com/Pytrex/NissanDefinitions | `22d14dd` (tag `v1.1`+18) | Pytrex | нет (all rights reserved) | Канон RomRaider Nissan-дефов (~188 XML + мастер `A2L.xml` ~330 таблиц + `ScalingData.xml`, сборка `Combine All.bat`). SH7055 / SH7058, ~2001-2010, авто-генерация бинарным диффингом из заводского A2L. |
| `reference/a33b-NissanDefs` | https://github.com/a33b/NissanDefs | `d31d6a4` (master) | a33b | нет (all rights reserved) | 82 XML + `table_templates` (NISSAN_BASE). Предыдущий "most recent" до Pytrex; единственный источник VQ37VHR-дефов. |

Оба репозитория без файла лицензии (выложены для community-использования, юридически
нелицензированы). Модель submodule хранит в нашем репозитории только SHA-указатель на их
публичный коммит, поэтому вопрос перераспределения нелицензированных файлов не возникает.

Канон под Nissan-RomRaider (июль 2026) – `Pytrex/NissanDefinitions`, подтверждено автором
оригинальных дефов на форуме RomRaider. Инструмент (парсер дефов, алгоритмы checksum
`NissanChecksum.java`, тип `alt2` под HR) – в `RomRaider/RomRaider` (GPL v2), как submodule
не подключён; ссылка: https://github.com/RomRaider/RomRaider.

## Рабочие файлы (JK08A)

Канонический слой разметки собственного целевого ROM `JK08A` находится прямо в `defs/`,
отдельно от `reference/`:

- `JK08A.xml` – деф RomRaider (проекция графа + презентация, генератор `mapkit/emit_def.py`).
- `JK08A.maps.csv` – ledger каталога (проекция графа, `maps/build_tracker.py`).
- `JK08A.notes.md` – рукописный журнал реверса (обоснования, листинги, трейсы; в граф не
  грузится).
- `romraider/NissanImmoCoordinator.jar` – custom `ChecksumManager` для одного
  пользовательского переключателя L1+L2 always-ID-OK. Исходный код, сборка и тест –
  `../tools/romraider/`.
- Рукописные источники калибровочного слоя: `JK08A.interp.csv` (геометрия входов
  интерполяции), `JK08A.findings.csv` (находки о картах), `JK08A.axes.csv` (семантика
  осей), `JK08A.overrides.toml` (презентация дефа). Контракт –
  `../tools/map-flag-pipeline.md`.
- Эталонные цензы резолвера: `JK08A.map_inventory.{26944,26984,26b84}.csv`
  (`MapInventory` на ядро), `JK08A.direct_lookup_inventory.csv`
  (`DirectLookupInventory` на банк implicit-axis).
- `rom-inheritance.toml` – явная привязка exact-code ROM к каноническому набору
  аннотаций. Запись закрепляет SHA-256 обоих образов и побайтно проверяемые диапазоны
  исполняемого кода.

Живого набора `JK03A.*` в `defs/` нет. Донорский `JK03A` сохраняет собственный образ,
headless-экспорт и отдельный набор узлов в Memgraph, но получает структурные и
семантические аннотации из `JK08A` через `rom-inheritance.toml`. Загрузчик до ingest
проверяет SHA-256 и равенство объявленных диапазонов кода, а диапазоны значений и хеши
таблиц измеряет по собственному образу каждого ROM. Поэтому изменения `JK08A` попадают
в слой `JK03A` при следующем ingest без синхронизации копий. Исторические A/B-артефакты
читают прежние файлы `JK03A` только как commit-qualified git-объекты.

## Релевантность под целевые моторы

Идентификация дефа – по `romid` (ecuid/model/year/market/memmodel), не по имени мотора.

**VQ35HR** (SH7058, 1 MB, dual CVTC без VVEL) – наша HR-архитектура, ближайший донор структуры:
- `Pytrex-NissanDefinitions/Nissan Definitions/350Z/EV18A.xml` – ecuid `1EV18A`, 350Z HR 2007
  USDM, SH7058, **190 таблиц**. Самый глубокий деф: fuel (base schedule, target AFR, injector
  latency/mag, MAF, LTFT/STFT, per-cyl trims), ignition (main / high-octane / high-detonation
  16x16, cranking, retard), **dual CVTC (Intake / Exhaust / Cold / High-Detonation Cam Timing
  Maps)**, knock, torque, rev/speed limiters, idle, ETC-флаги, checksum `alt2`.
- `.../G35/CF92A.xml` – ecuid `CF92A`, Infiniti G35 **V36 sedan** 2007 USDM, SH705823 (7058),
  **146 таблиц**. Та же кузовная платформа V36, что тестовый Skyline (мотор VQ35HR, не VQ25HR).
- `.../350Z/EV15A.xml` (33 таблицы, частичный), `EV13B` / `EV16A` / `EV19B` (0 таблиц,
  romid-опознаватели ROM).
- `.../A2L.xml` (~330 таблиц, мастер-шаблон из заводского Nissan/Renault A2L) + `ScalingData.xml`
  – словарь таблиц и масштабов, база наследования остальных дефов.

**VQ37VHR** (SH7059, 1.5 MB, VVEL + dual CVTC) – класс MCU нашего JDM-таргета:
- `a33b-NissanDefs/1NX4A.xml` – ecuid `11NX4A`, Infiniti G37 S 2011, SH7059, **30 таблиц**
  (триммы топлива/зажигания, MAF/MAF2, per-cyl, knock slice, fuel cut/restore, idle, ECT,
  e-throttle/VVEL learning lattice). Базовых карт фаз ГРМ и карты VVEL нет.
- `a33b-NissanDefs/6GE2C.xml` – ecuid `16GE2C`, 370Z 2017, SH7059, только checksum
  (`flashmethod=nis-can`).
- `a33b-NissanDefs/table_templates/` – шаблон NISSAN_BASE.

**VQ25HR** (JDM V36 Skyline 250GT) – открытого дефа нет нигде. Не-VVEL dual-CVTC, класс
VQ35HR: в def-корпусе SH7059 только у VVEL VQ37VHR (`1NX4A`, `6GE2C`), весь не-VVEL VQ –
на SH7058 / более старых. Донор структуры – `EV18A` / `CF92A` (SH7058, та же Hitachi CAN +
dual CVTC). Донорский `JK03A` и собственный целевой `JK08A` самоидентифицируются как
**SH705822N (SH7058, 1 MiB)** и имеют один идентификатор ПО `7MFKAVN86`.
Их области `0x020000..0x0fffff` совпадают побайтно, но calibration/config отличается
на 121 байтовой позиции. В графе различаются измерения только четырех пока безымянных
candidate-кривых `0x15360`, `0x15380`, `0x19090`, `0x190b0`; все 229 осей и остальные
435 карт совпадают. Рабочий `JK08A.xml` содержит 138 таблиц, две оси-опоры и два
проверенных нативных checksum-обработчика RomRaider. Один TableSwitch управляет L1;
custom-менеджер синхронизирует L2 при сохранении. Порядок менеджеров:
`NissanImmoCoordinator` -> `alt` -> `alt2`. Это один элемент интерфейса, а не единый
бит ROM. Неизвестное состояние L1/L2 и неверный размер ROM отклоняются до пересчёта
checksum.
Собственный ROM стендового VQ35HR `JK00D` также подтверждает класс
**SH705822N / SH7058 / 1 MiB**.

Атрибут `flashmethod` в HR-дефах (`Nisprog` у SH7058 `EV18A`/`CF92A` и SH7059 `1NX4A`) –
ненадёжная метаданная: открытый nisprog/npkern флеш-бэкенда под SH7059 не имеет. Ценность
файлов – в разметке карт, не в этом теге.

## Инициализация и обновление

```
git submodule update --init defs/reference           # подтянуть содержимое по пину
# сдвинуть пин на новый upstream-коммит:
git -C defs/reference/Pytrex-NissanDefinitions fetch && \
  git -C defs/reference/Pytrex-NissanDefinitions checkout <sha>
git add defs/reference/Pytrex-NissanDefinitions       # зафиксировать новый gitlink
```

## Известный безвредный артефакт

Субмодуль `a33b-NissanDefs` на регистронезависимой ФС (macOS APFS / Windows) показывает
`CD800.xml` (или `cd800.xml`) как modified: в коммите одновременно есть оба пути,
различающиеся только регистром, и на такой ФС они мапятся в один файл. Это состояние
рабочего дерева субмодуля, на pinned SHA и на HR-дефы не влияет; на регистрочувствительной
ФС оба файла существуют корректно. Правкой не требует внимания.
