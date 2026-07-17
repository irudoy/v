# tools – RE-стек VQ HR ECU

Инфраструктура реверс-стека. Канонический путь – **headless Ghidra -> Memgraph (MAGE) ->
LLM-агент**: детерминированные экстракторы (Java GhidraScript) пишут CSV, загрузчики строят
граф как систему записи; пайплайн от GUI не зависит и идёт в автономном/пакетном режиме.
Граф агент читает MCP-сервером `mcp-memgraph` (раздел "Memgraph MCP") – headless-native, в
каноническом пути. GhydraMCP – опциональный интерактивный ускоритель live-сессий реверса
(раздел "Мост GhydraMCP"), требует GUI, вне критического пути. Замысел, пайплайн карт/флагов
и роли – `../AGENTS.md`, `map-flag-pipeline.md`, нота "RE-стек и реверс таблиц" в Obsidian.

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
| `ghidra/ResolveAccessors.java` | операнды аксессоров: data-flow декомпилятора против backtrack, восстановление функций под сайтами вне разметки | `accessors.csv` |
| `ghidra/DumpListing.java` | дизассемблинг окрестностей адреса с разрешёнными ссылками | `listing_<addr>.txt` |
| `ghidra/RecoverFuncs.java` | разметка функциями кода вне функций (участки без прямых вызовов – их вызовы в граф не попадают, декомпилятор в них не работает) | Ghidra-проект |
| `ghidra/RenameFuncs.java` | применить курируемые имена (`symbols.csv`) к функциям проекта | Ghidra-проект |
| `ghidra/ImmoConfirm.java` | подтверждение immo-контура: декомпиляция registration/lock_setter, их callers, listing патч-сайтов; форсирует дизасм GBR-кода. Аргументы: `<reg_entry> <lock_entry> <site...>` | stdout |
| `ghidra/symbols.csv` | реестр имён функций (addr,name,note) – источник истины по реверсу | (в git) |
| `memgraph/load_graph.py` | `:Func` + `:CALLS`, Louvain на проекции call-графа ROM | Memgraph |
| `memgraph/load_xrefs.py` | `:Reg` + `:USES`, immo-аналитика (CAN/SCI/RXPR) | Memgraph |
| `memgraph/load_maps.py` | калибровочный слой из `accessors.csv`: `:Interp`/`:Map`/`:Axis` + `:ACCESSES`/`:VIA`/`:KERNEL`/`:AXIS_X`/`:AXIS_Y` | Memgraph |

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

Ценз карт строится от общего interp-kernel; операнды аксессоров (`r4` – база таблицы,
`r5`/`r6` – оси) снимает `ResolveAccessors` – data-flow декомпилятора рядом с линейным
backtrack `MapInventory` как эталоном (механика и ворота – `map-flag-pipeline.md`, разделы 6-7):

```bash
D=~/tools/ghidra-projects/export-JK03A
H="tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr -process as7058.bin -noanalysis -scriptPath tools/ghidra"
# 1. разметка кода вне функций + экспорт графа – в ОДНОМ запуске (гонка за lock проекта)
$H -postScript RecoverFuncs.java -postScript ExportGraph.java "$D"
uv run --no-project --with neo4j python tools/memgraph/load_graph.py "$D" JK03A
# 2. операнды: ценз-эталон и резолвер (проект не меняют)
$H -readOnly -postScript MapInventory.java     "$D" 26944   # слоты -> обёртки -> сайты
$H -readOnly -postScript ResolveAccessors.java "$D" 26944   # data-flow против backtrack
# 3. калибровочный слой в граф (после load_graph: тот пересоздаёт :Func вместе с :ACCESSES)
uv run --no-project --with neo4j python tools/memgraph/load_maps.py "$D" JK03A 26944
```

`RecoverFuncs` под `-readOnly` считает и отчитывается, не сохраняя разметку (dry-run); без
`-readOnly` она идёт в проект, и её видит `ExportGraph`. JK03A: 38627 инструкций в 494 участках
-> 353 функции (1958 -> 2312), после чего обёртки `0x26100`/`0x26230` получают вызывателей.

JK03A (kernel `0x26944`, ~100 сек): 124 сайта, `df_r4` 124/124 против 106/124 у backtrack,
`bt_only`=0, 5 `conflict` – сайты, где база выбирается ветвлением (две карты). В графе – 104
карты, 110 осей, 128 доступов, 65 аксессоров.

### Локализация immo по DTC-якорям

immo-статус ECM представлен как DTC (P1610-P1615, group `0x0d`). Путь от immo-DTC констант
к DTC-таблице и коду-адресатору (immo CAN ID публично не раскрыт – якоря числовые):

```bash
D=~/tools/ghidra-projects/export-1ND0A
H="tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr -process 1ND0A_Stock.bin -noanalysis -scriptPath tools/ghidra"
$H -postScript ScanImmoAnchors.java "$D"              # immo-DTC + кластер DTC-таблицы
$H -postScript FindTableRefs.java  "$D" 1b000 1c400   # кто адресует таблицу
$H -postScript DumpListing.java    "$D" <addr>...     # точки использования (ref -> value)
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
H="tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr -process 1ND0A_Stock.bin -noanalysis -scriptPath tools/ghidra"
# 1-2. RenameFuncs + ExportGraph – в ОДНОМ headless-запуске: раздельные прогоны подряд
#       ловят гонку за lock проекта Ghidra (второй открывает read-only, имена не выгружаются).
$H -postScript RenameFuncs.java "$SYM" -postScript ExportGraph.java "$D"   # имена -> проект -> funcs.csv
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
