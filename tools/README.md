# tools – RE-стек VQ HR ECU

Инфраструктура реверс-стека: **Ghidra + GhydraMCP -> Memgraph (MAGE) -> LLM-агент через MCP**
(замысел – см. `../AGENTS.md` и ноту "RE-стек и реверс таблиц" в Obsidian).

В git трекается только конфигурация и обёртки. Сами инструменты и Ghidra-проекты –
вне репозитория (крупные / машинно-локальные), их расположение указано ниже.

## Компоненты и расположение

| Компонент | Версия | Где | В git |
|-----------|--------|-----|-------|
| Ghidra | 12.1.2 (JDK 21, ARM-нативы) | `brew`; `GHIDRA_INSTALL_DIR=$(brew --prefix ghidra)/libexec` | нет |
| Плагин GhydraMCP | v3.0.0-rc.1 под ghidra12.1.2 | `.../libexec/Ghidra/Extensions/Ghydra` | нет |
| Мост / CLI GhydraMCP | v3.0.0-rc.1 | клон `~/tools/GhydraMCP` (venv `.venv`, Python 3.11) | нет |
| Memgraph MAGE + Lab | mage 3.11.0 | Docker (`memgraph/docker-compose.yml`) | **да** (compose) |
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

# 2. Ghidra (GUI) – поднимает HTTP-сервер плагина на 8192
ghidraRun    # brew-обёртка берёт JDK 21 сама
#    затем: открыть/создать проект, открыть программу в CodeBrowser,
#    File > Configure > Developer -> включить GhydraMCPPlugin (однократно).

# 3. Импорт дампа headless (SH-2E ядро -> вариант SH-2A с FPU, big-endian)
tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr \
  -import rom-images/1ND0A_Stock.bin \
  -processor "SuperH:BE:32:SH-2A" -loader BinaryLoader -loader-baseAddr 0x0
```

## Мост GhydraMCP в Claude Code

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
| `ghidra/DumpListing.java` | дизассемблинг окрестностей адреса с разрешёнными ссылками | `listing_<addr>.txt` |
| `ghidra/RenameFuncs.java` | применить курируемые имена (`symbols.csv`) к функциям проекта | Ghidra-проект |
| `ghidra/ImmoConfirm.java` | подтверждение immo-контура: декомпиляция registration/lock_setter, их callers, listing патч-сайтов; форсирует дизасм GBR-кода. Аргументы: `<reg_entry> <lock_entry> <site...>` | stdout |
| `ghidra/symbols.csv` | реестр имён функций (addr,name,note) – источник истины по реверсу | (в git) |
| `memgraph/load_graph.py` | `:Func` + `:CALLS`, Louvain (сообщества-подсистемы) | Memgraph |
| `memgraph/load_xrefs.py` | `:Reg` + `:USES`, immo-аналитика (CAN/SCI/RXPR) | Memgraph |

```bash
D=~/tools/ghidra-projects/export-1ND0A
tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr -process 1ND0A_Stock.bin \
  -noanalysis -scriptPath tools/ghidra -postScript ExportGraph.java "$D"
tools/ghidra/headless-analyze.sh ~/tools/ghidra-projects vq-hr -process 1ND0A_Stock.bin \
  -noanalysis -scriptPath tools/ghidra -postScript ExportXrefs.java "$D"
uv run --no-project --with neo4j python tools/memgraph/load_graph.py "$D" 1ND0A
uv run --no-project --with neo4j python tools/memgraph/load_xrefs.py "$D" 1ND0A
```

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
2. Скачать `Ghydra-*-ghidra12.1.2.zip` из релизов starsong-consulting/GhydraMCP,
   распаковать в `$(brew --prefix ghidra)/libexec/Ghidra/Extensions/`.
3. Клон GhydraMCP + `uv venv .venv && uv pip install -e .`; `claude mcp add` (см. выше).
4. `docker compose -f tools/memgraph/docker-compose.yml up -d`.

`ghidraVersion` в `extension.properties` плагина обязан совпадать с версией Ghidra;
после `brew upgrade ghidra` переустановить плагин под новую версию.
