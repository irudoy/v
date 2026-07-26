# Контракт массового прохода (sweep)

Проход по каталогу карт: перечисление известных таблиц превращается в разметку. Оркестратор
прохода – механизм Claude Code **Dynamic Workflows**; имя инструмента в tool API – `Workflow`.
Параллельный набор обычных вызовов `Agent` его не заменяет. Архитектура Dynamic Workflow
задана в `map-flag-pipeline.md`, раздел 8.4; здесь – контракт прогона: единица работы, порядок
волн, ослепление пилота, схема заявки и ворота.

Вход – каталог после Stage 4 (форма и содержимое сняты, значения измерены по образу). Выход –
строки `defs/<rom>.findings.csv` и `defs/<rom>.axes.csv`, из которых загрузчик строит слой, а
генератор перевыпускает деф.

## 1. Единица работы – компонента, а не карта

Карту именует трейс её потребителя. Один аксессор читает несколько карт, и один трейс
обслуживает их все; при этом одну карту читают несколько аксессоров. Агент на карту означал бы,
что N агентов повторяют один трейс и заявляют разное об одном узле.

Единица – **связная компонента** двудольного графа "аксессор -> карта":

```cypher
MATCH p=(:Func {rom:$rom})-[:ACCESSES]->(:Map {rom:$rom})
WITH project(p) AS g
CALL weakly_connected_components.get(g) YIELD node, component_id
WITH component_id, collect(node) AS nodes
RETURN component_id,
       [n IN nodes WHERE 'Map'  IN labels(n) | n.addr] AS maps,
       [n IN nodes WHERE 'Func' IN labels(n) | n.addr] AS accessors
```

Свойства, ради которых выбрана эта единица:

- компоненты независимы **по построению**: две компоненты не делят ни карту, ни аксессор,
  поэтому агенты не конкурируют за узел и не спорят об одном факте;
- все свидетельства о карте лежат внутри одного агента: её аксессоры, их трейсы, её соседи по
  чтению.

### Focused-режим frozen worklist

Последовательное закрытие точных позиций immutable worklist использует один
`map-<addr>.md` как item Dynamic Workflow. Граница item совпадает с позицией партии, чтобы
синтез не захватывал соседние карты той же компоненты за пределами frozen slice. Сам артефакт
при этом несёт контекст всей связной компоненты: аксессоры, трейсы и соседние карты. Поэтому
граница свидетельства остаётся компонентной, а карта является только границей пакетирования и
записи результата. Несколько items одной компоненты могут повторять контекст; синтез принимает
только точный frozen worklist партии. Полные волны без позиционной границы используют компоненту
как item.

### Frozen backfill по свойствам

Evidence backfill фиксирует не строки целиком, а identity `(rom, label, addr, property)`.
Manifest `tools/sweep/evidence_backfill.py` привязывает каждую заявку к immutable git blob,
digest исходной строки и SHA-256 blind-артефакта. Для JK03A зафиксированы 78 заявок на 58
узлах: 52 `Map.confidence`, 20 `Map.scale_conf` и 6 `Axis.scale_conf`. Семантика карты и её
шкала разрешаются независимо: подтверждение одного свойства не подтверждает другое.

Map-focus сохраняет компонентный контекст одной frozen-карты. Axis-focus строит
`axis-<addr>.md` по всем непосредственно связанным картам и аксессорам; общая ось не получает
случайно выбранную карту-представителя. Два независимо собранных набора обязаны совпасть по
именам и SHA-256, пройти blind-аудит и покрыть все 58 узлов до запуска Workflow.

### Парный эксперимент семантики прямого вызывателя JK03A

`tools/sweep/caller_ab_experiment.py` задаёт отдельный read-only control plane для измерения
вклада заранее проверенной семантики прямого вызывателя в focused-анализ карты. У CLI нет
команды применения и записи в `defs/*.csv`. Private manifest, execution inputs, артефакты,
Workflow archives и отчёты хранятся вне git.

Frozen `selection-v1` содержит ровно 24 карты:

```text
0000a29a 0000ab4a 0000b23a 0000b33a 0000b71a 0000b81a
0000d78e 00011ede 00012262 000122b2 00012312 00012908
00012a32 00012a62 00012e1a 00012e3a 00012fc6 000131a2
00014114 0001462a 0001473a 0001488a 0001497a 00016f48
```

Адреса соединяются LF без завершающего LF; SHA-256 списка равен
`4e9b97f9e9a46d183d96d549403e8264856e1128209f363c6dd1a85bdf3bcc94`. Commit выбора –
`b02d3b7157d900a0654b1c63f2c200d8154d315b`, commit закрытого truth –
`849d76a6ea8f2fb931448bf7adb58b6739aa7a40`. Diversity objective равна
`(24,16,7,-4,-12)`, SHA-256 selection tie-break равен
`01889b5fbd018738bef760dd91cdd3fa8b4ef9660a4ed3923cee322d8ba77576`. Состав выборки: 21
уникальный direct caller, 22 exposed maps и 2 identical-input controls.

Execution contract фиксирует:

- model `claude-opus-4-8`, effort `high`, один stochastic replicate и одинаковый
  platform-default token budget для одной response schema; model alias не используется;
- SHA-256 и полный embedded source трёх Workflow scripts
  `.claude/workflows/vq-caller-{prep,run,score}.js`, exact prompts и project agent
  `.claude/agents/vq-ab-blind-worker.md`;
- `tools: []` у blind worker и policy
  `embedded_artifact_no_tools_exact_single_structured_call`;
- fresh-only запуск с явной operator attestation, без resume, cache reuse, retry и fallback model;
- exact native Workflow root schema; если native output содержит phase records, они образуют
  canonical phase sequence; полный набор ожидаемых labels, ровно один `StructuredOutput` tool call
  на agent run, ненулевые aggregate totals и один resolved model
  из allowlist `claude-opus-4-8`/`claude-opus-4-8[1m]`;
- archive envelope из `runId`, фактического `scriptPath`, `scriptSha256`, `scriptSource`, exact
  `args`, `result`, полного native `workflowOutput`, `status` и `launch`. Persisted session copy
  Workflow script допустима только при точном совпадении source SHA-256 с runtime binding.
  Историческая проверка использует embedded source, а перед архивацией SHA-256 live
  agent/workflow обязан совпасть с execution input. Python preflight дополнительно связывает каждый
  embedded `artifact_text` с его `artifact_sha256`, а citation ranges/excerpts – с допустимыми code
  fences того же текста; saved Workflow не является самостоятельной криптографической границей
  доверия.

Workflow registry и реестр project agents загружаются при старте Claude Code. После первого
добавления или изменения definitions сессия перезапускается до smoke-test. Smoke-test проверяет
наличие `vq-ab-blind-worker`, фактические `tools: []`, ровно один вызов `StructuredOutput`,
отсутствие fallback/retry/cache и вызов всех трёх `vq-caller-*` через object и JSON-string args.
Отсутствие definition или несовпадение фактической native schema является блокирующим условием,
а не основанием для fallback на обычного агента с доступом к репозиторию.

Контракт фаз:

1. Focus-map builder двумя отдельными запусками собирает 24 исходных `map-<addr>.md` в
   разные каталоги штатной командой с `--audit-output`. `freeze` требует оба каталога и оба
   audit JSON, проверяет раздельность путей, exact inventory без stale files и byte-identical
   SHA-256 по каждому адресу. Каждый audit фиксирует embedded source и SHA-256 builder, Ghidra
   export directory, бюджеты ровно `8`/`24` и успешный blind gate. Отрицательные бюджеты CLI не
   принимает. Дополнительный консервативный literal/normalized scan повторно ищет private truth
   в обоих наборах.
2. `freeze` повторно выводит private schema v4 из pinned git blobs и frozen exports. Полный
   Ghidra export cohort root инвентаризируется рекурсивно: каждый обычный файл получает
   относительный путь, размер и SHA-256, symlink запрещены. Explicit `calls.csv`, `funcs.csv`,
   `decomp_*.c` и `accessors.*.csv` обязаны входить в этот inventory, а оба blind audit обязаны
   ссылаться на тот же root. Manifest хранит truth, `map -> accessor -> direct caller`, две
   artifact inventories, execution config, embedded builder и закрытое отображение условий.
   Condition, pair, job, card и score ids выводятся через HMAC-SHA256 с private 32-byte secret.
   Public worklists не содержат secret, truth или condition mapping.
3. `build-prep` формирует 21 caller-only artifact только из frozen Ghidra pseudocode и
   нейтральных `CALLS`. Comments и содержимое string/char literals удаляются с сохранением
   переносов. Human-authored function/data symbols и остальные содержательные identifiers
   детерминированно заменяются на адресные `FUN_`/`LAB_`/`DAT_` либо `ID_<n>`; это правило
   распространяется и на автоматические имена Ghidra с префиксами `param`, `local`, `uVar` и
   аналогичными. Текущие и исторические
   `Func.role`/`Func.semantics`, связь с выбранной картой и закрытые ответы запрещены. Адреса
   выборки и совпадения с private truth маскируются; literal/normalized leak scan работает
   fail-closed. Prep execution input удаляет `artifact_path` и встраивает назначенный
   `artifact_text` непосредственно в item. Opaque ids и hashes остаются у Workflow parent и
   присоединяются к structured result после ответа blind worker; в prompt модели они не входят.
4. Один `vq-caller-prep` выполняет 21 `Analyze` и 21 adversarial `Verify`. Workflow показывает
   артефакт как `N|RAW_LINE`; structured citation хранит one-based диапазон и exact raw excerpt
   без префикса номера. Verify обязан вернуть role, semantics и citations дословно; это соответствие
   и привязка citation к embedded артефакту проверяются в Workflow и до записи completed archive.
   Verifier rationale проходит ту же arm-neutrality проверку. `validate-prep` принимает только полное
   покрытие, однострочные target-independent printable-ASCII-English `role`/`semantics`,
   ranges/excerpts внутри `Machine evidence` fence и отсутствие прямых либо HTML-кодированных arm
   markers `verified`, `placebo`, `baseline`, `treatment`, `enriched`. Результат этой команды имеет
   schema `vq.caller-card-candidates/v1`, а не является готовыми карточками. Каждый candidate
   содержит digest exact payload. Отдельный ручной просмотр сверяет свободный текст с cited frozen
   caller artifact и создаёт полный `vq.caller-card-approvals/v1` с exact payload digests,
   `manual_exact_payload_against_cited_frozen_artifact` и operator attestation. Команда
   `finalize-cards` отклоняет missing, reject и digest drift, повторно выводит candidates из
   immutable worklist, execution input и полного Workflow archive и только после этого создаёт
   `vq.caller-semantics-cards/v4`.
5. `build-conditions` принимает только finalized cards с повторно проверенными candidates и
   approvals и вставляет одинаково размеченный caller-card block в исходные map-артефакты. В закрытом условии `verified` exposed map получает frozen cards. В условии
   `placebo` те же card ids, число карточек и layout получают естественно сформулированные
   детерминированные нейтральные `role`/`semantics`, выбранные по opaque card id. Каждая control
   map получает одну и ту же neutral sham-card и полный byte-identical artifact в обоих
   условиях. Estimand равен наблюдаемому операционному контрасту проверенного caller text и
   neutral placebo, а не абстрактному эффекту семантики при tokenizer-identical вводе. Для
   каждого условия создаются две byte-identical `integrity_copies`; четыре каталога и их file
   sets обязаны быть различными. Это проверка файлов, а не дополнительные LLM-запуски.
   Исполняется только copy 1, `stochastic_replicates=1`. `verify-artifacts` проверяет exact
   schemas/inventory/SHA-256, отсутствие symlink, card inventory, байты вне block, точный block
   каждого условия и идентичность controls.
6. Один и тот же `vq-caller-run` запускается отдельно с двумя opaque execution inputs. Каждый
   item содержит embedded artifact text без пути и sibling condition; строки показываются модели
   как `N|RAW_LINE`. На условие требуются 24 `Analyze` и 24 adversarial `Verify`. Run schema v4
   хранит `machine_references`, а не направленный trace: это последовательность 8-hex адресов для
   проверки принадлежности и score coverage, текстовый порядок не создаёт ребро. Короткие scalar
   constants в этот набор не входят. Evidence разбирается только canonical parser из
   `tools/memgraph/provenance.py`. Поскольку текущий frozen artifact не имеет отдельного
   typed-support registry, dependency tokens `role:addr[+offset]@target_prop` в run response
   запрещены; raw machine location записывается как `site:addr`, а addressless terminals требуют
   case-sensitive literal boundary match в citation. `rom_const` требует форму `addr=value` с
   непустым canonical literal. Каждая evidence machine anchor, result target и machine reference
   обязана присутствовать и в artifact, и в exact непустой citation из fenced code block; unused
   citation отклоняется. Проверка не выводит directed edge из соседства строк или порядка адресов.
   `accept_code` требует минимум две уникальные machine references и resolved disposition;
   `accept_code + unresolved` запрещён. Семантическая правильность `role`, `disposition`, target и
   semantics остаётся предметом blind Analyze, adversarial Verify и закрытого scoring, а не
   эвристического разбора C по словам. Arm/condition markers во всех свободных строковых полях run
   payload и verifier rationale отклоняются до построения score worklist; проверка декодирует HTML,
   удаляет comments и Unicode format controls. Verifier возвращает полный Analyze object дословно; Workflow и pre-archive validator проверяют exact
   равенство. Если два fresh archive содержат native phase records, они обязаны образовывать
   canonical phase sequence. Frozen agent record type должен покрывать exact 48 labels, иметь ровно
   один вызов `StructuredOutput` на agent run, `totalToolCalls == agentCount`, ненулевой
   `totalTokens`, один resolved model из allowlist
   `claude-opus-4-8`/`claude-opus-4-8[1m]`, полное отсутствие fallback/retry/cache/error provenance
   в служебных полях и значениях и exact result. `archive-workflow` проверяет result schema, типы,
   anchors и полноту до записи completed archive. Prep, оба run и score обязаны иметь один resolved
   model. Report повторно выводится из исходных archives.
7. `build-score` создаёт 48 opaque items. Blind scorer видит только один JSON-encoded объект с
   `reference_semantics` и `candidate_semantics`, без hashes, pair id, condition id, mapping и
   соседнего ответа. Строки трактуются как quoted data; JSON encoding не позволяет содержимому
   закрыть текстовый delimiter. Workflow parent присоединяет score id и candidate SHA-256 после
   ответа. `vq-caller-score` выполняет и сохраняет все 48 независимых вызовов. Даже byte-identical
   payload controls сохраняют два raw scorer observations: pooling, усреднение дубликатов и
   повторный вызов отсутствуют. Это позволяет controls наблюдать stochastic scorer drift при
   единственном replicate.
8. `compare` соединяет результаты только через private mapping. Reference factual evidence
   проецируется на тот же terminal-only run-домен: запрещённые dependency и process tokens не
   входят в denominator. Семь содержательных компонент
   сохраняются как raw scores; при verifier `refute` итоговый gated total равен нулю.
   Falsification gate проверяет каждый control и каждую компоненту отдельно: максимальный
   абсолютный delta среди `decision`, `role`, `disposition`, `target`, `factual_evidence`,
   `machine_reference_coverage`, `semantics`, `raw_total`, `verifier_accepted` и `total` обязан
   быть `<= 1/7`; любое расхождение `verifier_accepted` дополнительно делает gate invalid.
   Взаимное погашение control deltas не учитывается. При нарушении status равен
   `invalid_controls`, `observed_paired` равен `null`, raw output сохраняется для диагностики.
   При прохождении status равен `controls_passed`, а `observed_paired` содержит mean/median,
   wins/ties/losses и field deltas для 22 exposed maps. Один stochastic replicate не поддерживает
   причинную интерпретацию, поэтому `causal_claim=false`. Native output аттестует aggregate
   token/tool totals запуска, но не per-item monetary costs, поэтому costs отмечаются
   `measured=false`. `automatic_application=false` обязателен.

Полный запуск содержит 186 agent runs: 21 prep Analyze, 21 prep Verify, 48 map Analyze, 48 map
Verify и 48 blind semantics scores. Ручное approval карточек не создаёт LLM-запусков.
Независимый code review в это число не входит.

CLI предоставляет команды `freeze`, `build-prep`, `archive-workflow`, `validate-prep`,
`finalize-cards`, `build-conditions`, `verify-artifacts`, `validate-run`, `build-score`,
`validate-score`, `compare`, `status` и штатный `--help`; все пути задаются явно. `freeze` требует
`--map-artifacts`/`--blind-audit` и независимую пару
`--map-artifacts-replica`/`--blind-audit-replica`. Workflow получает содержимое
соответствующего `*-execution.json` через `args` как JSON object; saved workflows также принимают
полную JSON object string, но не путь к файлу. Перед первым `pipeline`/`agent` они проверяют exact
top-level/item schemas, counts, ids, prompts, runtime-binding paths и SHA-256 format. Exact live
source digests, execution-config digest и связь embedded artifact text с hash проверяет Python
control plane; этот слой остаётся доверенной границей локального запуска. Blind agent source обязан
иметь единственный top-level `tools: []` в YAML frontmatter; вложенная строка-приманка или строка в
теле definition не считается policy. `archive-workflow` принимает сохранённый native output, fresh
run id, фактический script path и обязательный `--fresh-launch-attested`, проверяет exact execution
schema, live execution-config digest, canonical runtime binding, native result
schema/types/completeness, citation ranges/excerpts против embedded artifacts, exact Analyze/Verify
linkage и progress provenance, затем встраивает
script source и его SHA-256. Эксперимент этим контрактом не считается запущенным.

Audit JSON, aggregate cohort digest и Workflow archive являются локальными воспроизводимыми
проверками, а не криптографической аттестацией доверенного runner. Operator attestation фиксирует
заявленный fresh launch, но не является независимой внешней аттестацией. Локальный пользователь с
правом изменять одновременно артефакты, audits, private manifest и native output остаётся внутри
trust boundary. Две независимые сборки ловят недетерминизм и случайный drift, но не защищают от
намеренной согласованной подделки всех локальных входов.

**Список компонент здесь не записан.** Он выводится из графа запросом на каждом прогоне: граф
меняется разметкой, и записанный список стал бы вторым источником правды (P5). Числа ниже –
состояние на момент закрытия Stage 4, они якорь для сверки, а не источник.

| Карт в компоненте | Компонент | Карт | Аксессоров | Плоских карт |
|---|---:|---:|---:|---:|
| 13-20 | 3 | 55 | 29 | 21 |
| 8-12 | 5 | 47 | 6 | 12 |
| 4-7 | 23 | 113 | 41 | 36 |
| 2-3 | 66 | 150 | 75 | 60 |
| 1 | 74 | 74 | 79 | 33 |
| **итого** | **171** | **439** | **230** | **162** |

## 2. Агенты читают артефакты, а не граф

Агент прогона не имеет доступа к Memgraph. Что он видит, задаёт шаг подготовки: на каждую
компоненту готовится артефакт, и его состав – предмет контракта, а не выбор агента.

Это не ограничение ради ограничения. Ослепить агента, который сам ходит в граф, нельзя: слой
разметки лежит там же, где форма, и `run_query` вернёт ответ вместе с вопросом. Доступ через
артефакт делает ослепление структурным.

Артефакт компоненты несёт:

- карты: адрес, геометрия, элемент, значения (из образа), диапазон;
- оси: адрес, точки, монотонность, длина, элемент;
- аксессоры: адрес, C-псевдокод (`DecompileFuncs`), листинг (`DumpListing`), дерево вызовов
  вверх, обращения к RAM/периферии (`:USES`);
- код между картой и записью выхода: обёртка интерполяции, её ядро и finisher. Ядро, в
  функцию не выделенное (обёртка уходит в него `jmp`, а не `jsr`), идёт листингом –
  разметка функции нужна декомпилятору, а не дизассемблеру, и код ядра читается там же;
- операнды сайтов из переписи резолвера: что передано в `r4`/`r5`/`r6` и чем это снято
  (`pool`/`slice`/`const`/`sp`);
- привязку результата lookup к RAM-приёмнику. Локальная база адреса разрешается в позиции
  записи: повторно используемое декомпилятором имя не наследует последнее значение из другой
  ветви функции;
- контракты вызываемых функций из слоя кода (`:Func.contract`) плюс их листинг целиком
  (`DumpFuncListing`). Библиотека арифметики `0x21000..0x23000` принимает аргументы
  регистрами, а не по ABI: Ghidra соглашения не восстанавливает, вызов идёт через регистр из
  литерального пула и печатается как `(*pcVar)()` – адреса в псевдокоде нет вовсе. Величина
  карты входит в такую функцию именно так, и без контракта трейс на ней обрывается. Кого
  показанный код вызывает, даёт ребро `:CALLS`, а не разбор текста: цель разрешена на этапе
  анализа, а не при печати;
- каталоги-эталоны: кандидаты имён из `:A2LEntry` и `:VendorEntry` по геометрии и семантике
  осей, якорные факты `:VendorFact` (документированные дефолты, единицы, механика).

Артефакт **не несёт** разметочный слой карт самой компоненты – `semantics`, `role`, `units`,
`scale_expr`, `confidence`. Это и есть ответ, который агент обязан вывести сам. Оси
ослеплены так же: артефакт несёт их измерение, а не `kind`/`units`/`scale_expr`.

Слой кода ослеплён по тому же правилу и на уровне поля, а не файла: `:Func.contract` идёт в
артефакт, `:Func.semantics` и `:Func.note` – нет. Контракт описывает операцию и соглашение о
регистрах и от карт не зависит; `semantics` копит знание проекта со ссылками на конкретные
карты и константы, то есть содержит готовый ответ по той самой карте, которую агент
разбирает.

Ослепление сделано **белым списком** (`RETURN` запросов `build_artifacts.py`), а не чёрным:
разметка и измерение лежат на одном узле, и свойство, добавленное в него позже, обязано быть
невидимым по умолчанию, а чёрный список пропустил бы его молча. Второй слой – сверка на
каждом прогоне (`verify_blind`): текст артефакта сличается с той самой разметкой, которую он
нести не должен, что ловит и ошибку в `RETURN`, и утечку через чужое поле (имя функции из
`symbols.csv`, псевдокод). Утечкой считается разметка, у которой в артефакте нет
независимого источника: шкалу `x-64` A2L объявляет сам для своих троек 16x16, и разметка её
оттуда и взяла (в графе она стоит с пометкой `[cand]`), поэтому совпадение с каталогом
дословно утечкой не является – агент читает каталог, а не ответ.

Ключ матча к каталогу на ослеплённой стороне один – геометрия: из трёх ключей (`dims`,
scale-family, семантика осей) два последних сами суть разметка. Матч слаб, и артефакт это
говорит: форму 16x16 несут 16 записей каталога.

Документированный дефолт сверяется только с плоскими картами (`vmin == vmax`): в поверхности
из 256 ячеек встречается почти любой байт, и совпадение там не значит ничего – это ровно тот
вывод из формы данных, которым pattern-scan уже дважды ошибся (P6).

## 3. Пилот – компонента аксессора `0x82C8A`

Первый прогон идёт на одной компоненте, и выбрана она из-за встроенного ключа ответов: из
14 её карт **6 уже уровня `code`**, снятых трейсом раньше.

| Карта | Значения | Элемент | Уровень | Семантика |
|---|---|---|---|---|
| `0000b61a` | 40..128 | uint8 | code | Порог монитора вращения [flag=clr] |
| `0000b71a` | 34..128 | uint8 | code | Порог монитора вращения [flag=set] |
| `0000b81a` | 33..63 | uint8 | code | Порог монитора вращения [always] |
| `0001261a` | 16..255 | uint8 | code | Граница классификатора нагрузки (верхняя) |
| `0001263a` | 15..42 | uint8 | code | Граница классификатора нагрузки (нижняя) |
| `00012cbe` | 15..42 | uint8 | code | Порог запрета диагностики (дубль `0x1263a`) |
| `00012026` | 0..0 | uint8 | candidate | – |
| `0001265a` | 255..255 | uint8 | candidate | – |
| `0001266a` | 254..254 | uint8 | candidate | – |
| `0001267a` | 253..253 | uint8 | candidate | – |
| `0001268a` | 252..252 | uint8 | candidate | – |
| `00012de2` | 43..255 | uint8 | candidate | – |
| `0001497a` | 33..33 | uint16 | candidate | – |
| `00014982` | 60..60 | uint16 | candidate | – |

Компонента прогоняет весь диапазон работы разом: поверхности, компараторы, плоские карты, оба
элемента и флаг (`flag=set`/`clr`), то есть задевает и Stage 6. Она же сталкивает разметку с
каталогами: тройку 16x16 у нас три, A2L даёт три и UpRev три, а ProECU насчитывает девять карт
зажигания (`refs/vendor/README.md`). Пилот снимает расхождение трейсом, а не подсчётом: тройка
`0xB61A/0xB71A/0xB81A` – не зажигание, а пороги монитора неравномерности вращения
(`defs/JK03A.notes.md`); имя "Ignition Adj Map" и шкала `x-64` пришли из A2L по совпадению
формы (P6) и трейсом опровергнуты. Тот же разбор уточнил границы пары `0x1261A`/`0x1263A`
(верхняя и нижняя в прежней разметке переставлены). Оба расхождения зафиксированы по правилу
раздела 6, а не разрешены голосованием.

Открытый предмет внутри компоненты: `0x1265A`, `0x1266A`, `0x1267A`, `0x1268A` – это 255, 254,
253, 252. Четыре плоские таблицы с константой, убывающей на единицу, четырьмя независимыми
находками не являются.

**Ослепление пилота.** Артефакт пилотной компоненты собирается по правилу раздела 2 – без
разметочного слоя её карт. Шесть известных ответов держатся вне прогона и сверяются с заявками
после него. Артефакт, собранный с семантикой, превращает калибровку в репетицию и обесценивает
единственный прогон, где харнесс можно проверить.

## 4. Форма прогона

Подготовка (headless, до workflow) – три шага:

```bash
D=~/tools/ghidra-projects/export-JK03A
H() {
  tools/ghidra/headless-analyze.sh "$HOME/tools/ghidra-projects" vq-hr \
    -process as7058.bin -noanalysis -scriptPath tools/ghidra "$@"
}
H -postScript DecompileFuncs.java "$D" <аксессоры волны>
H -postScript DumpListing.java    "$D" <сайты волны> <ядра волны без разметки>
uv run --no-project --with neo4j python tools/sweep/build_artifacts.py <out> --accessor <addr>
```

Аксессоры волны даёт запрос раздела 1, её сайты и неразмеченные ядра – запрос по ним; списком
они не хранятся по той же причине, что и компоненты:

```cypher
MATCH (f:Func {rom:$rom})-[x:ACCESSES]->(m:Map {rom:$rom})
WHERE f.addr IN $accessors
OPTIONAL MATCH (m)-[:VIA]->(:Interp {rom:$rom})-[:KERNEL]->(k:Interp {rom:$rom})
OPTIONAL MATCH (kf:Func {rom:$rom, addr:k.addr})
RETURN collect(DISTINCT f.addr) AS funcs, collect(DISTINCT x.callsite) AS sites,
       collect(DISTINCT CASE WHEN kf IS NULL THEN k.addr ELSE NULL END) AS bare_kernels
```

Псевдокод и листинги берёт `build_artifacts.py` из `<D>`; отсутствие файла он объявляет в
артефакте, а не обходит молча – трейс без псевдокода не ведётся. Листинг снимается на адрес
сайта, а не функции: операнды резолвятся там, и окно `DumpListing` вокруг входа функции до
сайта не достаёт. Для ядра адрес и есть точка входа, и окно вокруг него накрывает ядро
целиком. У карты из ручного слоя вне переписи резолвера `callsite` отсутствует по построению:
такая карта может попасть в focused-артефакт соседним контекстом, но листинга сайта у неё не
существует, и это не пропуск подготовки.

GUI и GhydraMCP в прогоне не участвуют – плагин требует GUI и становится узким местом на
десятке параллельных агентов.

Сам прогон – один Dynamic Workflow, запускаемый инструментом `Workflow`; внутри него
`pipeline()` ведёт элементы по стадиям без барьера. Обычные вызовы `Agent`, в том числе
параллельные, не заменяют этот запуск и не являются источником результатов для синтеза. В
`args.items` передаётся точный frozen worklist волны; выход запуска связывается с его `runId`
и `scriptPath`.

1. **анализ** – агент стадии `Analyze` внутри Dynamic Workflow читает артефакт, ведёт трейс
   потребителя и возвращает заявки (Stage 4-6);
2. **состязательная проверка** – на каждую заявку уровня `code` отдельный агент стадии
   `Verify` внутри Dynamic Workflow получает задачу её **опровергнуть**: трейс ведёт к
   заявленной семантике? RAM сходится? При неуверенности заявка считается опровергнутой.
   Заявку, не пережившую проверку, понижает до `candidate`, а не выбрасывает.

Барьер между стадиями не нужен: компоненты независимы, и заявки компоненты A проверяются, пока
компонента B ещё анализируется.

Backfill JK03A выполнен 58 blind-анализами и 78 отдельными проверками конкретного свойства.
Recovery заменяет только полный frozen-узел со всеми его свойствами и обязан дочитать
назначенный артефакт до EOF; частичная замена одной identity запрещена control plane.

3. **синтез** – вне агентов (раздел 5).

## 5. Запись – вне агентов

Агенты Dynamic Workflow возвращают заявки; строки в `defs/<rom>.findings.csv` и
`defs/<rom>.axes.csv` пишет шаг синтеза после проверки. Синтез принимает только результат
запуска инструмента `Workflow`, для которого зафиксированы `runId`, `scriptPath`, полный
frozen worklist и число проверок `code`; свободные ответы обычных `Agent` входом этой стадии
не являются. Причин раздельной записи две: параллельные агенты дрались бы за один CSV, а
запись прямо в граф не пережила бы прогона – узлы слоя загрузчик пересоздаёт, и правка идёт
в источник.

Control plane принимает ровно одно решение на frozen identity: `accept`, доказанный `revise`
или `downgrade` с конкретным blocker. Verified evidence переносится без изменения. Допустима
только явно записанная синтаксическая нормализация: edge-токен ROM-адреса становится
`site:<тот-же-адрес>`, а неразрешимая RAM-зависимость без ranked claim удаляется. Адрес менять
или добавлять нельзя; итог повторно проходит parser factual evidence и offline preflight.

Цепочка после синтеза – обычная: `ingest.py` (`load_graph.py -> load_xrefs.py ->
load_maps.py -> load_code.py -> provenance_report.py audit`) -> `build_tracker.py` ->
`mapkit/emit_def.py`.

## 6. Схема заявки

Заявка о карте (колонки `findings.csv`; форму и аксессора уже несёт перепись, агент их не
переоткрывает):

| Поле | Смысл |
|---|---|
| `addr` | карта |
| `confidence` | `code` – трейс ведёт к семантике; `candidate` – совпадение или сходство |
| `evidence` | claim-specific токены, которые обосновывают семантику карты |
| `role` | `table` \| `threshold` \| `dead` |
| `semantics` | что это |
| `units`, `scale_expr`, `to_byte`, `scale_conf` | шкала и её уровень |
| `scale_evidence` | claim-specific токены, которые обосновывают шкалу |
| `note` | контекст трейса для человека; автоматически в evidence не преобразуется |

Заявка об оси – колонки `axes.csv` (`addr`, `kind`, `units`, `scale_expr`, `to_byte`,
`scale_conf`, `scale_evidence`, `note`). Заявка о флаге (Stage 6) – адрес, бит, роль
(`selector`/`gate`/`threshold`), семантика, уровень.

Structured output workflow дополнительно несёт судьбу выхода: `writes`, `consumer`,
`inline_comparison`, `return`, `dead_control_flow` либо `unresolved`, а также точный target.
Отдельной колонки CSV у неё нет: синтез проверяет по ней роль и атрибуцию, затем сохраняет
машинные опоры в `evidence`, а полный трейс – в `note`.

Правила уровня:

- каждое свойство Map/Axis уровня `code` или `silicon` обязано иметь собственное factual
  `evidence` либо `scale_evidence`; process-only токены `wave`/`arg` не проходят локальные
  source gates;
- заявка без трейса – `candidate`, а не `code`, каким бы убедительным ни было совпадение;
- узкая операционная семантика получает `code`, если полный трейс доказывает именно её: неизвестное
  физическое имя величины не понижает доказанную формулу, роль множителя или полярность порога;
- имя из каталога (A2L, вендор) даёт `candidate`-идентичность, не семантику (P6);
- **сплошь `0xFF` не заключается по форме**: признак один и тот же у незапрограммированной
  флеши и у насыщенного предела, различает трейс;
- `role=dead` требует `output_disposition=dead_control_flow`: ветвь отключена калибровкой,
  и это доказано трейсом ветвления. Запись в RAM без индексированных читателей остаётся
  `writes`, а не становится `dead`;
- тождество `x` в сырых единицах не является заявкой о шкале и не получает `scale_conf`:
  если raw-представление нужно сохранить, задаются `units=raw`, `scale_expr=x`, `to_byte=x`;
  если единица неизвестна, все поля шкалы остаются пустыми;
  преобразование с clamp либо условием остаётся в `note`, если его нельзя точно выразить
  обратимой арифметической парой `scale_expr`/`to_byte` из словаря загрузчика;
- расхождение источников фиксируется как расхождение, а не разрешается голосованием.

## 7. Порядок волн

Крупные компоненты первыми: у них лучшее отношение имён к одному трейсу, и слабости харнесса
проявятся там, а не на хвосте.

| Волна | Что | Компонент | Карт |
|---|---|---:|---:|
| 0 | пилот – компонента `0x82C8A` | 1 | 14 |
| 1 | компоненты >= 8 карт; сюда же стресс-случай – 19 карт на 22 аксессорах | 7 | 91 |
| 2 | компоненты 4-7 карт | 22 | 105 |
| 3 | компоненты 2-3 карты | 63 | 144 |
| 4 | одиночки | 79 | 79 |

Между волнами: синтез, перевыпуск дефа, чтение метрик раздела 11 спеки, решение о следующей.
Волна не запускается автоматически за предыдущей.

## 8. Ворота

**Локальный evidence gate.** `evidence_backfill.py status --require-zero` требует нулевой долг
по frozen-классам, а `ingest.py <rom> --dry-run` проверяет factual evidence и разрешимость
зависимостей до мутации графа. Для JK03A долг `52 + 20 + 6` равен нулю. Exact audit после
ingest отдельно требует `missing=extra=duplicate_expected=duplicate_actual=unresolved=0`.
Глобальный `--strict` не подменяет эти ворота: он дополнительно проверяет effective confidence
и grounding всего графа и остаётся отдельной диагностикой.

**Пилот.** Воспроизвёл ли харнесс шесть известных ответов. Промах разбирается, а не идёт автоматом
в минус харнессу: ключ ответов – это разметка, и часть её выведена из каталога (P6), а не из кода.
Промах на факте, снятом трейсом, обвиняет харнесс; промах на факте, взятом из имени каталога,
обвиняет ключ – и тогда действует правило раздела 6 (расхождение фиксируется, не разрешается
голосованием). Волна 1 не запускается до разбора.

Пилот пройден: харнесс воспроизвёл уровень (5 из 6) и роль (6 из 6) и обошёл ловушку шкалы `x-64`.
Семантику тройки `0xB61A/0xB71A/0xB81A` он не воспроизвёл, и разбор отнёс промах к ключу, не к
харнессу: "Ignition Adj Map" взято из A2L по совпадению формы (P6), а трейс потребителя относит
тройку к порогам монитора неравномерности вращения (`defs/JK03A.notes.md`). Ослепление на прогоне
выдержало: 318 обращений агентов, все в артефакт.

**Волны.** Ворота раздела 11 спеки, регрессионно: резолюция операндов не снижена, в активный
деф не впущена карта ниже `code`, доля заявок `code`, переживших состязательную проверку,
измерена и записана.

Прогон, снизивший метрику, – провал ворот, а не новая норма.

## 9. Чего прогон не делает

- **Не режет по плоскому слою.** 152 плоские карты идут поперёк компонент, и на вопрос "почему
  константа" отвечает тот же трейс потребителя, что и на вопрос "что за поверхность".
  Отличается вывод, а не работа: плоские карты идут внутри своей компоненты и чаще кончаются
  ролью `dead` или порогом.
- **Не режет по семействам доступа.** explicit-axis и implicit-axis различаются трактовкой
  операндов, но компонента может нести обе – 25 аксессоров работают с обоими семействами.
- **Не хардкодит список компонент** (раздел 1).
- **Не пишет из агентов** (раздел 5).
- **Не поднимает GUI** (раздел 4).
