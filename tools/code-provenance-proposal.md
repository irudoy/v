# Спецификация: слой понимания кода и провенанс заявок

Слой дополняет калибровочный граф Memgraph заявками о функциях, RAM-переменных, картах и
шкалах. Источник истины находится в `defs/*.csv`; свойства узлов и `:RESTS_ON` являются
пересобираемой проекцией. Локальная лестница уверенности едина для всех заявок:

```text
pattern -> candidate -> code -> silicon
```

Ground truth остаётся в кремнии. Граф фиксирует структуру довода, но не заменяет проверку на
стенде и CONSULT3P live-data.

## 1. Инварианты

- Факт меняется в git-источнике. Ручная правка свойств и `:RESTS_ON` в Memgraph запрещена.
- `note` и `defs/<rom>.notes.md` не парсятся в факты автоматически.
- Семантика, контракт и шкала являются разными заявками с независимыми уровнями.
- Имя и структурное сходство не дают уровень `code` без проверяемого свидетельства.
- Эффективная уверенность вычисляется из локальных уровней и не сохраняется вторым источником
  истины.
- Разметка испытуемой компоненты не попадает в артефакт прохода.

## 2. Идентичность заявки

Полная идентичность:

```text
(rom, label, addr, property)
```

Ранжируемые свойства:

| Метка | Свойства |
|-------|----------|
| `:Func` | `confidence`, `contract_conf` |
| `:Reg` | `confidence` |
| `:Map` | `confidence`, `scale_conf` |
| `:Axis` | `confidence`, `scale_conf` |

`Func.confidence` относится к системной семантике функции. `Func.contract_conf` относится к
операции над аргументами, возвращаемому значению и побочным эффектам. Контракт разрешён во
входе прохода, семантика функции запрещена как готовый ответ.

`structural` используется только как идентичность структурной цели. Это не уровень
уверенности: зависимость участвует в обратном impact и grounding, но не ограничивает
эффективный уровень.

## 3. Git-источники

| Файл | Claim-specific колонки |
|------|------------------------|
| `defs/<rom>.funcs.csv` | `confidence,evidence`; `contract_conf,contract_evidence` |
| `defs/<rom>.vars.csv` | `confidence,evidence` |
| `defs/<rom>.findings.csv` | `confidence,evidence`; `scale_conf,scale_evidence` |
| `defs/<rom>.axes.csv` | `scale_conf,scale_evidence` |

Полные заголовки проверяет `load_code.py`. `contract` и `contract_conf` обязательны парой.
Evidence без соответствующего уровня запрещён.

Механическое происхождение базы карты из резолвера не является ручным claim evidence. Оно
хранится отдельно в `Map.resolver_kinds`; значения `pool`, `slice`, `const`, `sp`, `gbrrel`,
`dyn` описывают способ разрешения операнда.

## 4. Грамматика evidence

Поле содержит токены через `;`. Адресная зависимость обязана назвать свойство цели:

```text
role:addr@target_prop
role:addr+offset@target_prop
```

Примеры:

```text
consumer:00085a70@confidence
homolog:00021f40@contract_conf
from_map:0001491a@structural
base:ffff3100+4@structural
```

Допустимые свойства цели:

```text
confidence
contract_conf
scale_conf
structural
```

Классы токенов:

| Класс | Значение | Действие |
|-------|----------|----------|
| `consumer`, `writes`, `indexed_by`, `selector`, `threshold`, `from_map`, `trace`, `homolog`, `base`, `match` | `addr[+offset]@target_prop` | проекция в `:RESTS_ON` |
| `rom_const`, `spec`, `registry`, `site` | непустое терминальное значение | grounding без узла |
| `wave`, `arg` | метаданные процесса | не являются свидетельством |

`from_map` всегда адресует `@structural`: чтение зависит от существования и геометрии карты,
а не от её семантического `Map.confidence`.

Строгий разбор запрещает:

- legacy-токен адреса без `@target_prop`;
- неизвестный класс или target property;
- пустое значение;
- повтор токена после нормализации;
- ссылку на отсутствующий узел или на отсутствующее ранжируемое свойство.

`from_map` и `match` на отсутствующий элемент каталога перечисляются отдельным пробелом при
разборе. Offline preflight, standalone-загрузчик и воспроизводимый ingest считают такой пробел
ошибкой до фиксации новой проекции.

## 5. Проекция `:RESTS_ON`

Ребро имеет свойства:

```text
RESTS_ON {
    source_prop,
    role,
    target_prop,
    ref
}
```

`source_prop` входит в ключ. Без него зависимости семантики и контракта между одной парой
адресов слились бы в одно ребро. `ref` сохраняет исходную форму ссылки, включая смещение.

Полный ключ проекции:

```text
source_label, source_addr, source_prop,
role,
target_label, target_addr, target_prop,
ref
```

`load_code.py` в одной транзакции:

1. проверяет строгие CSV-схемы и локальные ворота;
2. проверяет, что `load_maps.py` уже спроецировал узлы и уровни Map/Axis;
3. удаляет stale-аннотации слоя кода;
4. проецирует claim-specific свойства и точно сравнивает их с CSV;
5. разрешает все адресные токены по существующим узлам, нерезолвимая ссылка останавливает
   загрузку;
6. пересобирает все исходящие `:RESTS_ON` для `Func`, `Reg`, `Map`, `Axis`;
7. сравнивает ожидаемую и фактическую проекции рёбер с учётом missing, extra и duplicates;
8. коммитит транзакцию только после чистого exact audit.

## 6. Эффективная уверенность

Для ранжируемой заявки:

```text
effective(claim) = min(
    local_level(claim),
    effective(каждой ranked-зависимости)
)
```

Structural-зависимость не входит в минимум. Локальный уровень остаётся верхней границей:
зависимость от `silicon` не повышает локальный `code` до `silicon`.

Циклы вычисляются безопасно:

1. алгоритм Tarjan находит strongly connected components;
2. SCC сворачиваются в DAG;
3. компонент получает минимум локальных уровней и внешних зависимостей;
4. grounding считается отдельно;
5. цикл без терминала, structural-опоры или заземлённой внешней зависимости не подтверждает
   себя и попадает в отчёт.

`tools/memgraph/provenance.py` реализует расчёт как чистую модель без Neo4j. Он же реализует
кратчайший путь к слабейшей заявке и обратный impact от полной claim identity. Изменение
`confidence`, `contract_conf`, `scale_conf` и `structural` не смешивается.

Read-only интерфейс:

```bash
uv run --no-project --with neo4j python \
  tools/memgraph/provenance_report.py audit JK03A
uv run --no-project --with neo4j python \
  tools/memgraph/provenance_report.py weakest JK03A Func 00021ce0 confidence
uv run --no-project --with neo4j python \
  tools/memgraph/provenance_report.py impact JK03A Map 0001495a structural
```

`audit` сверяет с CSV наличие source nodes, claim-specific свойства и рёбра; любое
несоответствие является ошибкой. `--strict` дополнительно делает ошибкой effective downgrade
и отсутствие grounding.

## 7. Ворота уровней

Для `Func.confidence`, `Func.contract_conf` и `Reg.confidence` уровни `code` и `silicon`
требуют хотя бы один фактический токен: адресную зависимость, structural-опору или терминал.
Одни `wave`/`arg` уровень не обосновывают.

Ворота Map/Axis работают в отчётном режиме до backfill. Причины:

- текущие `evidence` и `scale_evidence` калибровочного слоя пусты;
- автоматическое извлечение фактов из `note` запрещено;
- универсальное требование `INDEXED_BY + WRITES` неверно для inline-сравнений, возврата без
  RAM-write и доказанной dead-ветви;
- output disposition должен различать запись, потребителя, inline comparison, return и dead
  control-flow.

`attribute()` и другие эвристики могут создавать кандидатов и проверять ручные записи, но не
записывают результат в source-of-truth автоматически.

## 8. Воспроизводимый ingest

Владельцы узлов удаляют и пересоздают свои слои. Безопасный порядок фиксирован:

```text
load_graph.py
load_xrefs.py
load_maps.py
load_code.py
provenance_report.py audit
```

`load_code.py` всегда идёт последним из загрузчиков provenance targets. Иначе
`load_graph.py`, `load_xrefs.py` или `load_maps.py` удалит часть `:RESTS_ON` вместе со своими
узлами.

Исполняемый orchestrator выполняет offline preflight заголовков, форматов значений и внешних
ключей экспортов, ROM/SHA, полного набора цензов, claim grammar и разрешимости evidence до
первого destructive loader:

```bash
uv run --no-project --with neo4j python tools/memgraph/ingest.py JK03A
```

`--dry-run` выполняет preflight и печатает пять воспроизводимых команд через стабильный
`uv run`, не сохраняя путь временной Python-среды. `--strict` включает строгие
effective/grounding gates.

## 9. Состояние JK03A

Offline preflight канонических источников даёт:

| Метрика | Значение |
|---------|----------|
| `Func.confidence` | 166 заявок |
| `Func.contract_conf` | 31 заявка |
| `Reg.confidence` | 172 заявки |
| `Map.confidence` | 64 заявки |
| `Map.scale_conf` | 22 заявки |
| `Axis.scale_conf` | 11 заявок |
| Всего source claims | 466 |
| Уровень `code` | 426 |
| Ожидаемая проекция `:RESTS_ON` | 671 ребро, 0 нерезолвимых ссылок |
| Циклические SCC | 49 |
| `code` ниже declared по слабейшему звену | 109 |
| `code` без транзитивного grounding | 110 |
| Незаземлённые циклы | 10 |

Отчётные долги Map/Axis составляют 83 локальные заявки `code`:

- 54 `Map.confidence`;
- 20 `Map.scale_conf`;
- 9 `Axis.scale_conf`.

Их локальные уровни не меняются автоматически. После структурированного backfill нулевой долг
позволяет включить `--strict` как обязательный gate.

## 10. Ослепление и окружение прохода

Артефакт несёт контракт вызываемой функции, но не `Func.semantics`, `evidence`,
`contract_evidence` и разметку испытуемых Map/Axis. `verify_blind` сравнивает текст артефакта с
этими answer-only полями. Листинг неразмеченного ядра интерполяции разрешён: он содержит код
испытуемого пути, но не каталожную семантику.

Подача семантики окружения не включена. Роль и семантика вызывателя, а также соседние карты
открывают новый канал P6 и требуют отдельного A/B с тем же состязательным опровержением, что и
листинг ядра.

## 11. Silicon

Модель поддерживает `silicon` в локальном уровне, effective propagation, weakest path и reverse
impact. В канонических источниках JK03A заявок `silicon` нет. Первое стендовое свидетельство
записывается в соответствующий CSV с терминалом или адресной зависимостью; после ingest
read-only impact показывает все зависимые заявки для пересмотра. Сам граф не повышает вывод до
`silicon` и не считается внешним вводом истины.
