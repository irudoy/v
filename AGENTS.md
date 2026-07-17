# VQ HR ECU Tuning – AGENTS.md

Реверс-инжиниринг и тюнинг CAN-ЭБУ моторов Nissan/Infiniti серии **HR** (ЭБУ Hitachi,
MCU Renesas SH7058 / SH7059, ядро SH-2E):

- **VQ37VHR** – VVEL + dual CVTC;
- **VQ35HR**, **VQ25HR** – dual CVTC, без VVEL.

Тестовая платформа – **V36 Skyline 250GT** (VQ25HR, в доступе), ЭБУ `23710-JK08A`; дампа с
него нет, RE VQ25HR идёт по донорскому `JK03A` (`rom-images/README.md`). Целевое применение –
**VQ35HR** и **VQ37VHR**. **P0-веха – отшитие NATS** (PoC). Reflash – **KESS V2**
(OBD); заводская диагностика – **CONSULT-III Plus** через **Nissan VCI WiFi**.

## Принцип работы: два контура

1. **Git-репозиторий** (`~/src/docs/vq`, этот каталог) – технические артефакты,
   машинно-ориентированное и бинарное: ROM-дампы, дизасм-экспорты, деф-файлы
   (XDF / RomRaider), скрипты чексумм (nissutils) и Ghidra/Memgraph, даталоги.
2. **Obsidian vault** – человеко-ориентированные документы: план, роадмап,
   прогресс, база знаний, решения, открытые вопросы. **Источник правды по
   планированию и знаниям.** Синхронизируется через iCloud, доступен с телефона.
   - Путь: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Vault/🎛️ Electronics/VQ HR ECU Tuning`
   - Точка входа (MOC): нота **`VQ HR ECU Tuning`**.

Планирование и знание пишутся в vault; работа с дампами и скриптами – в репозитории.

## RE-стек

Канонический путь – headless: **Ghidra** (декомп + экспорт call / xref / data-flow, Java
GhidraScript) -> **Memgraph** (граф структуры, гомология, персистентная память проекта) ->
**LLM-агент** (поверх графа и headless-артефактов). Пайплайн от GUI не зависит, идёт в
автономном/пакетном режиме.

Развёрнуто локально (arm64): Ghidra 12.1.2 (JDK 21, нативы) + Memgraph MAGE (Louvain /
Leiden). Граф агент читает через MCP-сервер `mcp-memgraph` (stdio, scope project, read-only) –
он headless-native и потому часть канонического пути; запись в граф остаётся за загрузчиками.
GhydraMCP (плагин + мост `ghydra`, stdio MCP в Claude Code) – опциональный интерактивный
ускоритель live-сессий реверса, требует открытый GUI, вне критического пути.
Версии, порты, команды поднятия и роли – `tools/README.md`, `tools/map-flag-pipeline.md`.

Дисциплина верификации: **ground truth – в кремнии.** Структура графа != семантика.
Любое техническое утверждение до заливки проверяется на железе (CONSULT3P live-data,
стенд) – результат заливается в мотор.

## Карта репозитория

- `rom-images/` – ROM-дампы (`*.bin` + архивы) с RomRaider forum, все VQ37VHR (гомолог-пара
  SH7058 USDM / SH7059 JDM), плюс immo-патченные варианты. Версионируются в git; манифест
  `rom-images/README.md` (sha256, part #, идентификация, источники). Дамп опознаётся по sha256.
- `refs/` – внешние даташиты / мануалы (Renesas SH7059 HW manual, PCMflash module list,
  Bosch LSU 4.9, NERS, MoTeC M150, UpRev) + зеркало NissanECU RE wiki (`refs/nissanecu-wiki/`).
  PDF-оригиналы, markitdown-конверсии `*.md` и манифест `refs/README.md` – всё в git.
- `tools/` – инфраструктура RE-стека: `memgraph/docker-compose.yml` (Memgraph MAGE + Lab),
  `ghidra/headless-analyze.sh` (обёртка `analyzeHeadless` с JDK 21), `README.md` (версии,
  порты, команды). Сами инструменты (Ghidra, GhydraMCP) и Ghidra-проекты – вне git.
- `AGENTS.md` – этот файл.
- `.gitignore` – правила игнора (мусор ОС, scratch, регенерируемые кэши Ghidra / Memgraph).
  Контентные артефакты (ROM, даташиты, дефы, зеркала) версионируются.
- `defs/` – деф-файлы таблиц. `defs/reference/` – submodules открытых RomRaider Nissan-дефов
  (Pytrex, a33b) как референс карт (манифест и релевантность – `defs/README.md`); свои дефы
  под целевой ROM – по мере RE.
- (по мере работы) `ghidra/` (экспорты графа), `logs/`.

## Конвенции

- Язык: русский, техническая точность, без изобретения фактов. Плохо переводимые
  термины – латиницей (`firmware`, `checksum`, `part #`).
- Тексты декларативны: описывают состояние, а не ход работы над ним.
- Форматирование (глобальный CLAUDE.md): en-dash `–`; ASCII-стрелки (`->`);
  ASCII-кавычки; `<=` / `>=`; `x` вместо знака умножения.
- Не коммитить и не пушить без явной просьбы. ROM-бинарники не коммитить (правила в
  `.gitignore`).

## Скоуп

P0 – отшитие NATS на тестовом ЭБУ (VQ25HR) и перенос метода на VQ35HR / VQ37VHR;
далее тюнинг. DIY-реверс – immo-рутина, чексумма, деф таблиц.

Открытая экосистема: RomRaider-дефы (submodules в `defs/reference/`, манифест
`defs/README.md`) покрывают VQ35HR (Pytrex `EV18A` – 190 таблиц; `CF92A` – кузов V36) и
поверхностно VQ37VHR (a33b `1NX4A` – 30 таблиц); под VQ25HR дефа нет. HR – класс late
K-line: дамп по K-line доступен, открытый reflash есть под SH7058, под SH7059 (наш JDM)
нет – закрывается KESS V2 по OBD. Immo-off / NATS в открытом виде отсутствует (NATS-ключи
в отдельном EEPROM, вне flash-ROM и вне дефов).
