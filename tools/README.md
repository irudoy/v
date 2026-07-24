# tools – RE-стек VQ HR ECU

Инфраструктура реверс-стека. Канонический путь – **headless Ghidra -> Memgraph (MAGE) ->
LLM-агент**: детерминированные экстракторы (Java GhidraScript) пишут CSV, загрузчики строят
граф как систему записи; пайплайн от GUI не зависит и идёт в автономном/пакетном режиме.
Граф агент читает MCP-сервером `mcp-memgraph` (раздел "Memgraph MCP") – headless-native, в
каноническом пути. GhydraMCP – опциональный интерактивный ускоритель live-сессий реверса
(раздел "Мост GhydraMCP"), требует GUI, вне критического пути. Замысел, пайплайн карт/флагов
и роли – `../AGENTS.md`, `map-flag-pipeline.md`, нота "RE-стек и реверс таблиц" в Obsidian.
Массовый проход по каталогу карт – `map-sweep.md`: единица работы, порядок волн, ослепление
пилота, схема заявки и ворота.

В git трекается только конфигурация и обёртки. Сами инструменты и Ghidra-проекты –
вне репозитория (крупные / машинно-локальные), их расположение указано ниже.

## Компоненты и расположение

| Компонент | Версия | Где | В git |
|-----------|--------|-----|-------|
| Ghidra | 12.1.2 (JDK 21, ARM-нативы) | `brew`; `GHIDRA_INSTALL_DIR=$(brew --prefix ghidra)/libexec` | нет |
| Плагин GhydraMCP (опц., интерактив) | v3.0.0-rc.1 под ghidra12.1.2 | `.../libexec/Ghidra/Extensions/Ghydra` | нет |
| Мост / CLI GhydraMCP (опц., интерактив) | v3.0.0-rc.1 | клон `~/tools/GhydraMCP` (venv `.venv`, Python 3.11) | нет |
| Memgraph MAGE + Lab | mage 3.11.0 | Docker (`memgraph/docker-compose.yml`) | **да** (compose) |
| MCP `mcp-memgraph` (чтение графа агентом) | 0.2.0 (через `uv`, Python 3.13) | `.mcp.json` в корне репозитория | нет (глобальный gitignore) |
| Ghidra-проект | – | `~/tools/ghidra-projects/vq-hr` | нет |
| headless-обёртка | – | `ghidra/headless-analyze.sh` | **да** |

## Порты

- `8192`+ – HTTP плагина GhydraMCP (первый CodeBrowser 8192, второй 8193, ...); авто-дискавери мостом.
- `7687` – Memgraph Bolt (драйвер `neo4j`, Lab); `7444` – стрим логов в Lab.
- `3000` – Memgraph Lab UI (http://localhost:3000).
- Memgraph-порты забиндены на `127.0.0.1` явно (IPv4-loopback), стек живёт в контексте
  Docker Desktop. Комплект в другом контексте (Lima/colima) занял бы `127.0.0.1`, вытеснив
  Docker Desktop на IPv6 (`::1`) – тогда `localhost` (IPv4-first) и Lab расходятся по данным.

## Поднять стек

```bash
# 1. Memgraph (MAGE: Louvain, Leiden) – ТОЛЬКО в контексте Docker Desktop
docker context use desktop-linux            # иначе второй комплект расщепит localhost
docker compose -f tools/memgraph/docker-compose.yml up -d
#    данные персистентны в bind-mount tools/memgraph/data/ (snapshots+WAL, git-ignored),
#    восстановление графа при старте автоматическое (--data-recovery-on-startup).
#    проверка Louvain:
#    docker exec -i vq-memgraph-mage mgconsole <<< "CALL mg.procedures() YIELD name WHERE name CONTAINS 'community_detection' RETURN name;"

# 2. (опц.) Ghidra GUI – только для интерактивного MCP (раздел "Мост GhydraMCP");
#    headless-пайплайн (шаг 3 и далее) от GUI не зависит. Поднимает HTTP-плагин на 8192.
ghidraRun    # brew-обёртка берёт JDK 21 сама
#    затем: открыть/создать проект, открыть программу в CodeBrowser,
#    File > Configure > Developer -> включить GhydraMCPPlugin (однократно).

# 3. Импорт дампа headless (SH-2E ядро -> вариант SH-2A с FPU, big-endian)
tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr \
  -import rom-images/1ND0A_Stock.bin \
  -processor "SuperH:BE:32:SH-2A" -loader BinaryLoader -loader-baseAddr 0x0
```

## Memgraph MCP (чтение графа агентом)

Агент ходит в граф MCP-сервером `mcp-memgraph`: stdio, scope project (`.mcp.json` в корне
репозитория; сам файл исключён глобальным gitignore, поэтому на новой машине создаётся
командой ниже). Сервер **headless-native** – Memgraph это сервер, GUI не нужен, поэтому MCP
годится и в автономных прогонах. Режим **read-only**: `CREATE/MERGE/DELETE/SET/DROP/REMOVE`
блокируются на его стороне, запись в граф идёт только загрузчиками `memgraph/load_*.py`.

```bash
claude mcp add memgraph --scope project \
  -e MCP_TRANSPORT=stdio -e MEMGRAPH_URL=bolt://localhost:7687 \
  -- uv run --with mcp-memgraph --python 3.13 mcp-memgraph
claude mcp list        # memgraph: ✔ Connected
```

Project-scope сервер требует одобрения при первом запуске (`claude` -> approve), иначе
`claude mcp list` показывает `⏸ Pending approval`. Инструменты: `run_query`, `get_schema`,
`get_configuration`, `get_index` / `get_constraint` / `get_storage` / `get_procedures`,
`get_page_rank`, `get_betweenness_centrality`, `get_node_neighborhood`, `search_node_vectors`.

Аналитические инструменты MCP считают по всему storage, где `:Reg`/`:USES` доминируют над
call-графом (сырой PageRank выводит в топ RAM-регистры) – осмысленный результат даёт
`run_query` с проекцией call-графа, см. `map-flag-pipeline.md`, раздел 8.2.

## Мост GhydraMCP в Claude Code (опциональный интерактив)

**Роль и границы.** GhydraMCP – ускоритель live-сессий реверса (человек+агент вскрывают
подсистему): интерактивная декомпиляция/xref/callgraph по живому проекту, секунды на запрос.
Плагин – HTTP-сервер внутри GUI CodeBrowser, поэтому **требует открытый проект с программой**
(иначе инструменты возвращают пусто); CLI-режим `ghydra` (ниже) – тот же клиент к тому же
плагину, та же зависимость от GUI. Отсюда MCP **не участвует в автономных/пакетных прогонах**
(workflow, cron, регрессия метрик) – там канонический headless. Полный low-level API
(`HighFunction`, сигнатуры CALLIND, register-context GBR – основа резолвера операндов
`map-flag-pipeline.md`) в наборе инструментов моста отсутствует, он headless-only. Частые
интерактивные вопросы без GUI закрывают параметризованные headless-скрипты
(`DecompileFuncs`/`PoolUsers`/`DumpListing`/`FindTableRefs` по адресу).

Зарегистрирован как stdio MCP-сервер `ghydra` (scope local, проект vq):

```bash
claude mcp add ghydra --env GHIDRA_HYDRA_HOST=localhost -- \
  ~/tools/GhydraMCP/.venv/bin/python ~/tools/GhydraMCP/bridge_mcp_hydra.py
claude mcp list        # ghydra: ✔ Connected
```

Инструменты (namespace `ghydra`): `instances_list` (сначала), `functions_list/decompile`,
`xrefs_list`, `analysis_get_callgraph`, `data_list_strings`, rename/аннотации и др.
Плагину нужен открытый CodeBrowser с программой – иначе инструменты вернут пусто.

CLI-альтернатива без MCP: `~/tools/GhydraMCP/.venv/bin/ghydra --json functions list`.

## Экспорт графа (headless)

Пайплайн Ghidra -> Memgraph без GUI: скрипты в `ghidra/` (Java GhidraScript, PyGhidra не
нужен) и `memgraph/` (загрузчики на драйвере `neo4j` Bolt). Прогон – через `headless-analyze.sh`.

| Скрипт | Назначение | Выход |
|--------|-----------|-------|
| `ghidra/ExportGraph.java` | call-граф (функции + CALLS) | `funcs.csv`, `calls.csv` |
| `ghidra/ExportXrefs.java` | обращения к периферии/RAM (`0xFFFE8000`+), literal-pool | `xrefs.csv` |
| `ghidra/DecompileFuncs.java` | C-псевдокод заданных функций | `decomp_<addr>.c` |
| `ghidra/ScanImmoAnchors.java` | скан immo-DTC констант (P1610-P1615, B2193), кластеры DTC-таблиц | `immo_anchors.csv`, `immo_tables.csv` |
| `ghidra/FindTableRefs.java` | кто адресует диапазон ROM (база таблицы): direct + literal-pool | `table_refs.csv` |
| `ghidra/MapInventory.java` | ценз карт от interp-kernel: слоты-значения -> обёртки -> call-сайты, `r4/r5/r6` линейным backtrack | `map_inventory.csv` |
| `ghidra/FindInterpCore.java` | детект ядер интерполяции и их входов data-сканом (Stage 1): слот с адресом кода + два уровня косвенности. Аргументы: `<outdir> [<min_wrappers>]` | `interp_core.csv` |
| `ghidra/ScanFlags.java` | детект gbr-флагов локально у аксессоров и guard-функций (Stage 6): тройка "загрузка – проверка бита – ветвление", роль по ветвям из CFG. Аргументы: `<outdir> <func_addr>...` | `flags.csv` |
| `ghidra/ResolveAccessors.java` | операнды аксессоров: data-flow декомпилятора против backtrack, восстановление функций под сайтами вне разметки, разворот операнда-множества (`MULTIEQUAL`) в строку на ветвь; прогон на ядро | `accessors.<kernel>.csv` |
| `ghidra/ProbeResolver.java` | headless-спайк условия А резолвера: снимает ли декомпилятор константные `r4/r5/r6` на CALLIND интерполятора (baseline vs форс сигнатуры `0x26320`); `-readOnly`-диагностика | stdout |
| `ghidra/DirectLookupInventory.java` | ценз банка implicit-axis форвард-сканом от слота, геометрия примитива по его коду; операнды – линейным backtrack | `direct_lookup_inventory.csv` |
| `ghidra/DumpListing.java` | дизассемблинг окрестностей адреса с разрешёнными ссылками | `listing_<addr>.txt` |
| `ghidra/DumpFuncListing.java` | дизассемблинг функции целиком, границу задаёт её тело. Для коротких функций, где предмет разбора – всё тело: библиотека арифметики передаёт аргументы регистрами, и соглашение читается только целиком. Аргументы: `<outdir> <addr...>` | `funclisting_<addr>.txt` |
| `ghidra/FuncAt.java` | функция, содержащая адрес (вход, размер, границы) – относит pool-слоты к функциям по границам Ghidra. Аргументы: `<addr...>` | stdout |
| `ghidra/RefsTo.java` | кто ссылается на адрес (инструкция, её функция, тип ссылки); владельца pool-слота даёт ссылающаяся инструкция. Аргументы: `<addr...>` | stdout |
| `ghidra/PoolUsers.java` | функция-владелец адреса (pool-слот/тело) + её декомпиляция + инструкции, ссылающиеся на адрес. Аргументы: `<outdir> <addr...>` | `decomp_<addr>.c` |
| `ghidra/RecoverFuncs.java` | разметка функциями кода вне функций (участки без прямых вызовов – их вызовы в граф не попадают, декомпилятор в них не работает) | Ghidra-проект |
| `ghidra/RenameFuncs.java` | применить курируемые имена (`symbols.csv`) к функциям проекта | Ghidra-проект |
| `ghidra/ImmoConfirm.java` | подтверждение immo-контура: декомпиляция registration/lock_setter, их callers, listing патч-сайтов; форсирует дизасм GBR-кода. Аргументы: `<reg_entry> <lock_entry> <site...>` | stdout |
| `ghidra/NatsGate.java` | поиск калибровочного master-enable над immo: подъём от immo-точек вверх по дереву вызовов, чтения делятся на RAM/CODE/`CALIB?`. Аргументы: `<entry...>` | stdout |
| `ghidra/symbols.csv` | реестр имён функций (addr,name,note) – источник истины по реверсу | (в git) |
| `memgraph/load_graph.py` | `:Func` + `:CALLS`, Louvain на проекции call-графа ROM | Memgraph |
| `memgraph/load_xrefs.py` | `:Reg` + `:USES`, immo-аналитика (CAN/SCI/RXPR) | Memgraph |
| `memgraph/load_maps.py` | калибровочный слой: переписи резолвера + реестр входов `defs/<rom>.interp.csv` + ручной слой карт `defs/<rom>.findings.csv` и осей `defs/<rom>.axes.csv` + значения из образа (Stage 4) -> `:Interp`/`:Map`/`:Axis` + `:ACCESSES`/`:VIA`/`:KERNEL`/`:AXIS_X`/`:AXIS_Y` | Memgraph |
| `memgraph/load_a2l.py` | `:A2LEntry` из `A2L.xml` – rom-независимый эталон семейства HR (карты, скаляры, switch'и), без адресов | Memgraph |
| `memgraph/load_code.py` | claim-specific слой: `funcs.csv`, `vars.csv`, `findings.csv`, `axes.csv` -> свойства заявок и точная проекция `:RESTS_ON`; `code`/`silicon` требует factual evidence для Func/Reg/Map/Axis; запускается последним после владельцев targets | Memgraph |
| `memgraph/ingest.py` | полный per-ROM ingest: offline preflight, затем `load_graph -> load_xrefs -> load_maps -> load_code -> provenance audit`; `--dry-run` не меняет граф, `--strict` дополнительно требует effective confidence и grounding | Memgraph |
| `memgraph/backup.py` | завершающий шаг агентского workflow: проверка 24-часового интервала, SMB mount, `DUMP DATABASE` + native snapshot + manifest и SHA-256 непосредственно на NAS | NAS |
| `memgraph/provenance_report.py` | read-only exact audit, weakest path и reverse impact по полной claim identity; `--strict` включает effective/grounding gates | stdout |
| `memgraph/queries.cypher` | каталог запросов: карты, компоненты sweep'а, центральность на проекции, каталоги-эталоны и отдельные структурные ворота. Claim-specific exact audit выполняет `provenance_report.py`. Параметр `$rom` | (в git) |
| `maps/build_tracker.py` | ledger `defs/<rom>.maps.csv` – проекция каталога из графа (worklist разбора) | (в git) |
| `sweep/build_artifacts.py` | blind-артефакты для массового прохода: компонента `comp-<addr>.md`, frozen-карта `map-<addr>.md` или общая ось `axis-<addr>.md`; Axis-focus агрегирует все связанные карты и аксессоры. Форма, значения, оси, псевдокод, листинги, операнды переписи и каталоги видимы; текущие ответы скрыты белым списком и проверяются каждым прогоном. Аргументы: `<outdir> [--accessor <addr>] [--min-maps N] [--focus-map <addr>] [--focus-axis <addr>]` | Markdown |
| `mapkit/rom.py` | образ: реестр `rom-images/roms.csv` со сверкой sha256, чтение массивов, их измерение. Библиотека – её зовут `load_maps.py` и скрипты пакета | (в git) |
| `mapkit/emit_def.py` | деф `defs/<rom>.xml` – проекция графа плюс презентационный слой `defs/<rom>.overrides.toml` (контракт – `map-flag-pipeline.md`, раздел 9) | (git, по мере коммита P5) |
| `mapkit/show.py` | карта либо ось в физических единицах: граф даёт форму, оси и шкалу, образ – значения. Аргументы: `[<rom>] <addr>...` | stdout |
| `mapkit/ptrscan.py` | кто указывает на адрес: скан образа по обеим формам константы (`mov.l` и `mov.w`), без Ghidra и проекта. Аргументы: `[<rom>] <addr> [<addr_hi>]` | stdout |

```bash
D=~/tools/ghidra-projects/export-1ND0A
tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr -process 1ND0A_Stock.bin \
  -noanalysis -scriptPath tools/ghidra -postScript ExportGraph.java "$D"
tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr -process 1ND0A_Stock.bin \
  -noanalysis -scriptPath tools/ghidra -postScript ExportXrefs.java "$D"
uv run --no-project --with neo4j python tools/memgraph/load_graph.py "$D" 1ND0A
uv run --no-project --with neo4j python tools/memgraph/load_xrefs.py "$D" 1ND0A
```

### Карты: разметка, резолюция операндов, граф

Ценз карт строится от общего движка интерполяции: слоты с его указателем дают обёртки,
call-ссылки на вход обёртки – сайты. Так устроены оба семейства доступа, и `ResolveAccessors`
покрывает их одним механизмом – примитив банка implicit-axis есть обёртка над своей цепочкой
сдвигов. Входы перечисляет реестр `defs/JK03A.interp.csv` (строка = вход: семейство, движок,
адрес входа и геометрия – элемент таблицы с кода входа у 1D и с кода finisher'а у 2D; число
точек оси и её элемент – с клэмпа её поиска, равного `(точек-1) * размер элемента`); прогон
идёт на каждый движок, файл на ценз.
Операнды (`r4` – база таблицы, `r5`/`r6` – оси explicit-axis) снимает data-flow декомпилятора,
рядом с линейным backtrack как эталоном ворот (механика – `map-flag-pipeline.md`, разделы 6-7):

```bash
D=~/tools/ghidra-projects/export-JK03A
# Функцией, а не переменной: в zsh неэкранированная $H на слова не разбивается, и вызов
# уходит в никуда молча.
H() { tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr \
        -process as7058.bin -noanalysis -scriptPath tools/ghidra "$@"; }
# 1. Разметка кода вне функций + экспорт графа – в ОДНОМ изменяющем запуске.
#    ExportXrefs читает сохранённую разметку отдельным read-only запуском.
H -postScript RecoverFuncs.java -postScript ExportGraph.java "$D"
H -readOnly -postScript ExportXrefs.java "$D"
# 2. Операнды: резолвер на каждый движок из реестра. ~100 сек на ценз.
for K in 26944 26984 26b84 26a5c 26a60 26a64 26a74 26a7c 26a80 26a84 26a88 26740 26c1c; do
  H -readOnly -postScript ResolveAccessors.java "$D" $K
done
# 3. Полный per-ROM ingest. Preflight проверяет заголовки, значения, внешние ключи,
#    цензы, ROM/SHA, разрешимость evidence и наличие factual evidence у каждого
#    Func/Reg/Map/Axis свойства уровня code/silicon до первого удаления узлов.
#    Порядок: graph -> xrefs -> maps -> code -> exact audit.
uv run --no-project --with neo4j python tools/memgraph/ingest.py JK03A --export-dir "$D"
# Только preflight и точные команды, без изменения графа:
uv run --no-project --with neo4j python tools/memgraph/ingest.py JK03A --export-dir "$D" --dry-run
# 4. Эталон каталога HR: rom-независим, грузится раз на семейство, не на дамп.
uv run --no-project --with neo4j python tools/memgraph/load_a2l.py
# 5. Генерируемые проекции после успешного аудита.
uv run --no-project --with neo4j python tools/maps/build_tracker.py JK03A
uv run --no-project --with neo4j python tools/mapkit/emit_def.py JK03A
```

### Резервное копирование Memgraph

Резервное копирование запускается только как завершающий шаг агентского workflow. Cron и
`launchd` не используются. Локальный конфиг создаётся из `memgraph/backup.example.toml` и
не входит в git:

```toml
smb_url = "smb://Junkyard/Backup"
mount_point = "/Volumes/Backup"
backup_subdir = "vq-memgraph"
minimum_interval_hours = 24
container_name = "vq-memgraph-mage"
mount_timeout_seconds = 30
command_timeout_seconds = 900
```

Проверка срока не подключает NAS:

```bash
python3 tools/memgraph/backup.py --status
```

Запуск при истёкшем интервале монтирует share через macOS Keychain и пишет комплект сразу в
`/Volumes/Backup/vq-memgraph/.<timestamp>.partial-*`. Готовый каталог публикуется rename
только после проверки gzip и SHA-256:

```bash
python3 tools/memgraph/backup.py --if-due
```

`minimum_interval_hours` не может быть меньше 24. Локальное
`memgraph/backup.state.json` содержит только время и путь последней успешной резервной копии.
Native snapshot привязан к версии Memgraph; `manifest.json` фиксирует image контейнера,
timestamp snapshot, числа узлов/рёбер/индексов, git commit и состояние worktree.

Разбор карты руками идёт теми же фактами, без Ghidra:

```bash
uv run --no-project --with neo4j python tools/mapkit/show.py b33a   # сетка в единицах + оси
uv run --no-project python tools/mapkit/ptrscan.py 11ebe 11ece      # кто указывает на массив
```

Загрузчик берёт все переписи каталога сразу, а не ядро на прогон: узлы слоя он пересоздаёт,
поэтому ценз на прогон означал бы, что загрузка второго ядра сносит карты первого. По той же
причине тем же прогоном идут ручной слой и Stage 4: и находка, и измерение живут на том же
узле, что и факт переписи. Перепись, которой в реестре нет, останавливает загрузку - модель
её оси неизвестна; так же останавливает и вход, через который перепись нашла таблицы, а
геометрия его не объявлена.

`load_code.py` идёт последним из владельцев provenance targets: предыдущие загрузчики удаляют
свои узлы вместе с исходящими и входящими `:RESTS_ON`. Он читает четыре канонических CSV,
сверяет наличие узлов и claim-specific свойства, требует factual evidence у каждого свойства
уровня `code`/`silicon`, строит 2712 claim-specific рёбер JK03A и выполняет exact
expected-vs-actual audit в одной транзакции. Локальные source gates проходят при нулевом долге
Map/Axis. Глобальный `--strict` является отдельной диагностикой: текущий JK03A содержит 114
заявок с effective confidence ниже declared и 13 заявок без grounding. Read-only проверка и
интерактивные запросы:

```bash
uv run --no-project --with neo4j python tools/memgraph/provenance_report.py audit JK03A
uv run --no-project --with neo4j python \
  tools/memgraph/provenance_report.py weakest JK03A Func 00021ce0 confidence
uv run --no-project --with neo4j python \
  tools/memgraph/provenance_report.py impact JK03A Map 0001495a structural
```

Значения таблиц и осей рукописным источником не объявляются - их говорит образ, и Stage 4
читает их оттуда каждым прогоном по адресу и форме из переписи. Образ берётся по метке ROM
из реестра `rom-images/roms.csv` со сверкой sha256: подмена дампа дала бы не отказ, а 229
осей правдоподобных чисел не из того образа. Ось несёт свои точки и монотонность, карта -
диапазон и хеш содержимого.

Эталонные цензы (`MapInventory.java` на ядро, `DirectLookupInventory.java` на банк) резолвер
воспроизводит сайт-в-сайт и строго покрывает по базам; они остаются точкой сравнения для
ворот раздела 7, а каталог строится по резолверу.

`load_a2l` кладёт в граф каталог `A2L.xml` (188 `:A2LEntry`: 106 карт, 36 скаляров, 46
switch'ей). Адресов в базовом дефе нет – каталог задаёт классы, а не размещение, и между
дампами переносится идентичность, а не смещения. Нотация RomRaider нормализуется по числу
осей (`2D` -> `dims=1`, `3D` -> `dims=2`), `shape` пишется словарём обёрток (`16x16`, `1D-8`).
Рёбра `:MATCHES` строятся после Stage 4: у `:Map` из ключей матча есть только `dims`, а
scale-family и семантику осей даёт разбор, не каталог.

`RecoverFuncs` под `-readOnly` считает и отчитывается, не сохраняя разметку (dry-run); без
`-readOnly` она идёт в проект, и её видит `ExportGraph`. JK03A: 38627 инструкций в 494 участках
-> 353 функции (1958 -> 2312), после чего обёртки `0x26100`/`0x26230` получают вызывателей.

JK03A, 13 цензов: 587 строк для 554 callsite; база в ROM снята data-flow на 551
callsite против 493 у backtrack. В графе – **439 карт** (248 explicit-axis, 188
implicit-axis, 3 ручных вне моделей доступа), 229 осей, 586 уникальных доступов, 47 узлов
интерполяции (34 обёртки + 13 движков). Один полный дубль строки ценза схлопывается ключом
ребра `ACCESSES`.

| семейство | движков | сайтов | `bt_r4` | `df_r4` | обёрток | карт |
|-----------|---------|--------|---------|---------|---------|------|
| explicit-axis | 3 | 327 | 288 | 326 | 24 | 232 |
| implicit-axis | 10 | 227 | 205 | 225 | 10 | 184 |

Источник базы по 554 callsite: 407 – слот пула, 102 – backward-slice, 27 – phi-узел
(59 строк по ветвям), 15 – резерв `SymbolicPropogator` (16 строк ценза), 3 не
сворачиваются (`dyn`). Семейства не пересекаются ни одной таблицей – загрузчик проверяет это
из своих строк. Плюс к 436 картам переписи ручной слой объявляет три вне обеих моделей
доступа: итог каталога – 439.

Обе переписи-эталона резолвер воспроизводит сайт-в-сайт (327 и 227) и покрывает по базам:
ни одна база эталона не потеряна, сверх них снято +13 таблиц на explicit-axis и +16 на банке.
Проверка новых данными: 12 из 16 монотонны, остальные четыре – полки и окна вида
`[0,0,0,0,0,0,255,255,255,255,0,0,0,0,0,0]`, то есть структура калибровки, а не шум.

Неснятые базы (3 сайта, `dyn`) молча не теряются – они помечены. У сайта `0x4a02c` пуст и
backtrack, то есть база динамическая, а не пропущенная. Указатель оси там снят (`0x15340`),
но узла не даёт: ось без карты – ось неизвестно чего, и в переписи значение сохранено, а
вернётся оно с базой на Stage 6.

Базу в граф даёт только data-flow. Линейный backtrack остаётся эталоном ворот и фактов не
даёт: на всех десяти базовых расхождениях каталога он неверен – поднимает ось вместо базы,
теряет арифметику delay slot либо берёт произвольный элемент селекторного множества. База не
свёрнута на 15 проецированных доступах с `kind=sp` (16 строк ценза до схлопывания полного
дубля), и снятая – один элемент множества, выбираемого ветвлением; полный набор снимает Stage
6.

На осях резерв ошибается так же: 256 проецированных доступов на 247 callsite несут
несвёрнутую ось (`kind5`/`kind6=sp`), и 14 осей из 229 стоят на нём одном – они помечены
уровнем `pattern` (`candidate` даёт любой свёрнутый сайт). Довод прямой: сайт `0x735ac`
объявляет осью `0x8000`, где лежит стёртая флешь. Тот же механизм даёт и неоднозначную
геометрию – у `0x14114` две оси на одном ребре (`0xE98E` и `0x8000`); ворота дефа такую карту
не пропускают, разбирает её Stage 6.

Элемент оси – свойство пары (обёртка, ось), а не движка: обёртка зовёт поиск на каждую ось
отдельно и может звать разные. `0x262E0` берёт байтовый `0x26A0C` для `r5` (клэмп 15) и
словесный `0x26984` для `r6` (клэмп 30), `0x26660` – ту же пару `0x26BC4`/`0x26B84`; таких
две из 22 двухосных обёрток. Клэмп в delay slot вызова равен `(точек-1) * размер элемента`,
и он же независимо подтверждает число точек у всех 24 обёрток. Расхождение нашло измерение
по образу, а не чтение кода: объявленные словесными оси `0x11D0C` и `0x18716` словами не
возрастают, а байтами дают одну и ту же лесенку нагрузки (`defs/JK03A.notes.md`, "Элемент
оси задаёт клэмп её поиска").

### Локализация immo по DTC-якорям

immo-статус ECM представлен как DTC (P1610-P1615, group `0x0d`). Путь от immo-DTC констант
к DTC-таблице и коду-адресатору (immo CAN ID публично не раскрыт – якоря числовые):

```bash
D=~/tools/ghidra-projects/export-1ND0A
H() { tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr \
        -process 1ND0A_Stock.bin -noanalysis -scriptPath tools/ghidra "$@"; }
H -postScript ScanImmoAnchors.java "$D"              # immo-DTC + кластер DTC-таблицы
H -postScript FindTableRefs.java  "$D" 1b000 1c400   # кто адресует таблицу
H -postScript DumpListing.java    "$D" <addr>...     # точки использования (ref -> value)
```

Результат на 1ND0A: DTC-таблица `0x1bdfc` (запись 12 байт, DTC@`+0x0a`), immo-блок idx
42-47, движок статуса `immo_dtc_status_engine` (`000b741e`) -> RAM DTC-статус `0xFFFED700+`.
Детали и остаток (гейт впрыска) – в ноте "Immo, NATS, клон ЭБУ" (Obsidian).

### Актуализация имён функций (реверс -> граф)

Имена подтверждённых функций (вместо `FUN_xxxxxxxx`) ведутся в git как единый источник
истины `tools/ghidra/symbols.csv` (`addr,name,note`). Ghidra и Memgraph – потребители:
скрипт применяет имена к проекту (нужны в декомпиляции), экспорт переносит их в граф.

```bash
D=~/tools/ghidra-projects/export-1ND0A
SYM=$(pwd)/tools/ghidra/symbols.csv
H() { tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr \
        -process 1ND0A_Stock.bin -noanalysis -scriptPath tools/ghidra "$@"; }
# 1-2. RenameFuncs + ExportGraph – в ОДНОМ headless-запуске: раздельные прогоны подряд
#       ловят гонку за lock проекта Ghidra (второй открывает read-only, имена не выгружаются).
H -postScript RenameFuncs.java "$SYM" -postScript ExportGraph.java "$D"   # имена -> проект -> funcs.csv
uv run --no-project --with neo4j python tools/memgraph/load_graph.py "$D" 1ND0A   # 3. -> граф
uv run --no-project --with neo4j python tools/memgraph/load_xrefs.py "$D" 1ND0A   #    (USES восстановить)
```

Направление одностороннее: правка `symbols.csv` -> Ghidra + Memgraph. Обратно (rename в
Lab или в GUI Ghidra) в git не возвращается и теряется при перезаливе – новые находки
дописывать в `symbols.csv`. `load_graph` пересоздаёт `:Func` (DETACH DELETE), поэтому
`load_xrefs` запускать следом, иначе рёбра `:USES` к периферии пропадут.

## Восстановление на новой машине

1. `brew install ghidra` (тянет openjdk@21 + собирает ARM-нативы).
2. `docker compose -f tools/memgraph/docker-compose.yml up -d`.
3. Memgraph MCP: `claude mcp add` (см. раздел "Memgraph MCP"), нужен `uv` в PATH; при первом
   запуске одобрить project-scope сервер.
4. (опц., интерактив) Скачать `Ghydra-*-ghidra12.1.2.zip` из релизов
   starsong-consulting/GhydraMCP, распаковать в `$(brew --prefix ghidra)/libexec/Ghidra/Extensions/`.
5. (опц., интерактив) Клон GhydraMCP + `uv venv .venv && uv pip install -e .`;
   `claude mcp add` (см. выше).

`ghidraVersion` в `extension.properties` плагина обязан совпадать с версией Ghidra;
после `brew upgrade ghidra` переустановить плагин под новую версию.
