// Запросы к графу: каталог, единица массового прохода, центральность, ворота.
//
// Файл - каталог, а не скрипт: запросы берутся отсюда поштучно. Он существует затем,
// чтобы числа раздела 11 спеки (tools/map-flag-pipeline.md) считались воспроизводимо, а
// не собирались в scratchpad заново на каждый прогон: они - ворота регрессии, и прогон,
// снизивший метрику, есть провал ворот, а не новая норма. Метрика, посчитанная разово и
// невоспроизводимо, воротами не работает.
//
// Якорь при метрике - её значение на JK03A на момент закрытия Stage 4. Он для сверки, а
// не источник: источник - граф, и расхождение запроса с якорем означает, что изменился
// граф (тогда правится якорь в разделе 11) либо запрос (тогда правится он).
//
// Параметр $rom - метка образа в графе (реестр rom-images/roms.csv). В графе два ROM
// (JK03A размечен, 1ND0A - только :Func и :Reg), и запрос без фильтра по rom считает по
// обоим.
//
// mgconsole:  :param rom "JK03A";
// драйвер:    session.run(q, rom="JK03A")
// mcp-memgraph run_query параметров не принимает - подставить метку в текст.
//
// ПРОЕКЦИЯ ОБЯЗАТЕЛЬНА для алгоритмов MAGE (раздел 8.2). Алгоритм без аргумента считает
// по всему storage, где :USES (42k рёбер) доминирует над :CALLS (6k), а :Reg связывает
// любые две функции, тронувшие общий адрес: сырой pagerank.get() выводит в топ
// RAM-регистры вместо кода, community_detection.get() схлопывает граф в мегакластер.
// Аналитические инструменты MCP (get_page_rank, get_betweenness_centrality) считают по
// всему storage - для этих запросов брать run_query с project().


// ════════════════════════════════════════════════════════════════════════════════════
// Раздел 7. Каталог
// ════════════════════════════════════════════════════════════════════════════════════

// Stage 2: каталог аксессоров одного ядра. Каталог - запрос к графу, а не обход CSV.
// $kernel: 00026944 | 00026984 | 00026b84 | ... (13 движков, см. :Interp {role:'kernel'})
MATCH (a:Func {rom:$rom})-[x:ACCESSES]->(m:Map {rom:$rom})-[:VIA]->(w:Interp {role:'wrapper'})
MATCH (w)-[:KERNEL]->(:Interp {role:'kernel', addr:$kernel})
RETURN a.addr AS accessor, w.width AS width, w.height AS height,
       m.addr AS table, x.callsite AS site
ORDER BY w.width DESC, table;

// Открытая работа разбора: candidate с пустой семантикой. Это и есть worklist sweep'а.
// Якорь: 410 из 419.
MATCH (m:Map {rom:$rom})
WHERE m.confidence = 'candidate' AND m.semantics = ''
RETURN m.addr AS table, m.family AS family, m.width AS width, m.height AS height,
       m.storagetype AS storagetype, m.vmin AS vmin, m.vmax AS vmax
ORDER BY m.width DESC, table;

// Плоские карты: одно значение на всю таблицу. Разбора стоят иначе, чем поверхность, и
// чаще кончаются ролью dead либо порогом. Сплошь 0xFF по форме не заключается: признак
// один и тот же у незапрограммированной флеши и у насыщенного предела - различает трейс.
// Якорь: 152 плоских, из них 18 сплошь 0xFF/0xFFFF.
MATCH (m:Map {rom:$rom})
WHERE m.vmin = m.vmax
RETURN m.addr AS table, m.width AS width, m.height AS height, m.storagetype AS storagetype,
       m.vmin AS value, m.confidence AS confidence, m.semantics AS semantics
ORDER BY value DESC, table;

// Сайты с невыбранной базой (kind=sp): декомпилятор операнд не свернул, значение снял
// линейный резерв, и снятое - один элемент множества, а не факт. База там задана
// ветвлением. Полный набор - вход Stage 6, где ветвление становится :Flag{role:'selector'}.
// Якорь: 42 сайта по базе.
MATCH (a:Func {rom:$rom})-[x:ACCESSES]->(m:Map {rom:$rom})
WHERE x.kind = 'sp'
RETURN a.addr AS accessor, x.callsite AS site, m.addr AS table, x.r4 AS r4,
       x.kind5 AS kind5, x.kind6 AS kind6
ORDER BY accessor, site;

// Оси на резерве (уровень pattern): называет их только backtrack, и на осях он ошибается
// так же, как на базах. Ворота дефа их не пропускают. Якорь: 17 из 227, среди них 0x8000 -
// стёртая флешь, то есть ось, которой нет.
MATCH (m:Map {rom:$rom})-[e:AXIS_X|AXIS_Y]->(a:Axis {rom:$rom})
WHERE a.confidence = 'pattern'
RETURN a.addr AS axis, a.len AS len, a.storagetype AS storagetype,
       a.monotonic AS monotonic, collect(DISTINCT m.addr) AS tables
ORDER BY axis;

// Общие оси: одна ось на нескольких картах. Ключ - содержимое, а не адрес: точки лежат в
// узле целиком, и одинаковые оси сходятся сравнением списков без обращения к образу.
MATCH (m:Map {rom:$rom})-[:AXIS_X|AXIS_Y]->(a:Axis {rom:$rom})
WITH a, collect(DISTINCT m.addr) AS tables
WHERE size(tables) > 1
RETURN a.addr AS axis, a.len AS len, size(tables) AS n_tables, tables, a.values AS values
ORDER BY n_tables DESC, axis;

// Одинаковое содержимое у разных карт: сходятся хешем (значений карт в графе нет - 256
// ячеек в узле были бы содержимым образа, переписанным туда).
MATCH (m:Map {rom:$rom})
WITH m.values_hash AS h, collect(m.addr) AS tables
WHERE size(tables) > 1
RETURN h AS values_hash, size(tables) AS n, tables
ORDER BY n DESC, values_hash;


// ════════════════════════════════════════════════════════════════════════════════════
// Раздел 8.4. Единица массового прохода - компонента, а не карта
// ════════════════════════════════════════════════════════════════════════════════════

// Связные компоненты двудольного графа "аксессор -> карта" (контракт - tools/map-sweep.md,
// раздел 1). Компоненты независимы по построению: две не делят ни карту, ни аксессор,
// поэтому агенты не конкурируют за узел и не спорят об одном факте.
//
// Список компонент нигде не записан: граф меняется разметкой, и записанный список стал бы
// вторым источником правды (P5). Якорь: 171 компонента, 419 карт, 230 аксессоров.
MATCH p=(:Func {rom:$rom})-[:ACCESSES]->(:Map {rom:$rom})
WITH project(p) AS g
CALL weakly_connected_components.get(g) YIELD node, component_id
WITH component_id, collect(node) AS nodes
RETURN component_id,
       [n IN nodes WHERE 'Map'  IN labels(n) | n.addr] AS maps,
       [n IN nodes WHERE 'Func' IN labels(n) | n.addr] AS accessors;

// Распределение компонент по размеру: порядок волн (раздел 7 контракта). Крупные первыми -
// у них лучшее отношение имён к одному трейсу, и слабости харнесса проявятся там, а не на
// хвосте. Якорь: 13-20 карт: 3 компоненты; 8-12: 4; 4-7: 22; 2-3: 63; 1: 79.
MATCH p=(:Func {rom:$rom})-[:ACCESSES]->(:Map {rom:$rom})
WITH project(p) AS g
CALL weakly_connected_components.get(g) YIELD node, component_id
WITH component_id, collect(node) AS nodes
WITH size([n IN nodes WHERE 'Map' IN labels(n)]) AS n_maps,
     size([n IN nodes WHERE 'Func' IN labels(n)]) AS n_acc
RETURN n_maps, count(*) AS components, sum(n_maps) AS maps, sum(n_acc) AS accessors
ORDER BY n_maps DESC;


// ════════════════════════════════════════════════════════════════════════════════════
// Раздел 8.2. Центральность на проекции call-графа
// ════════════════════════════════════════════════════════════════════════════════════

// Stage 1, независимая сверка ядра интерполяции: PageRank выводит библиотеку доступа в
// топ. Доступна до Stage 3 - косвенные вызовы с константной целью уже дают рёбра :CALLS.
// Сигнал независим от data-скана FindInterpCore.java, то есть сверка, а не тот же довод.
// Якорь JK03A: 0x26740, 0x26c78, 0x26370, 0x26944, 0x26388 в топе.
MATCH p=(:Func {rom:$rom})-[:CALLS]->(:Func {rom:$rom})
WITH project(p) AS g
CALL pagerank.get(g) YIELD node, rank
RETURN node.addr AS addr, node.name AS name, rank
ORDER BY rank DESC LIMIT 15;

// Betweenness на той же проекции: второй признак hub-слоя.
MATCH p=(:Func {rom:$rom})-[:CALLS]->(:Func {rom:$rom})
WITH project(p) AS g
CALL betweenness_centrality.get(g) YIELD node, betweenness_centrality
RETURN node.addr AS addr, node.name AS name, betweenness_centrality AS bc
ORDER BY bc DESC LIMIT 15;

// Дерево вызывателей аксессора (Stage 2): чем выше по дереву, тем ближе подсистема.
MATCH path = (c:Func {rom:$rom})-[:CALLS*1..3]->(a:Func {rom:$rom, addr:$accessor})
RETURN [n IN nodes(path) | n.addr] AS chain, length(path) AS depth
ORDER BY depth, chain;


// ════════════════════════════════════════════════════════════════════════════════════
// Раздел 7, Stage 5. Каталоги-эталоны
// ════════════════════════════════════════════════════════════════════════════════════

// Кандидаты каталога по геометрии. Ключ слаб намеренно: из трёх ключей матча (dims,
// scale-family, семантика осей) на стороне карты до Stage 4 есть только dims, и матч по
// одному dims свёл бы 37 двухосных записей с каждой картой dims=2 - это шум, а не
// подсказка (P6). Геометрия сужает: форму 16x16 несут 16 записей каталога. Реальный
// различитель - трейс входных RAM-сенсоров осей.
MATCH (m:Map {rom:$rom}), (e:A2LEntry {family:'HR'})
WHERE e.dims = m.dims
  AND e.shape = CASE WHEN m.height IS NULL THEN '1D-' + toString(m.width)
                     ELSE toString(m.width) + 'x' + toString(m.height) END
RETURN m.addr AS table, m.vmin AS vmin, m.vmax AS vmax, e.shape AS shape,
       collect(e.name) AS candidates
ORDER BY table;

// Схождение словарей: concept'ы, покрытые обоими вендорами. Соединяет словари свойство
// concept, а не имя: имена вербатим, и два словаря называют одно разными словами
// ("BFS Multiplier (K-Factor)" против "K - Fuel Multiplier"). Якорь: 26 из 50.
MATCH (e:VendorEntry {family:'HR'}) WHERE e.concept <> ''
WITH e.concept AS concept, collect(DISTINCT e.vendor) AS vendors,
     collect(DISTINCT e.name) AS names
WHERE size(vendors) > 1
RETURN concept, vendors, names
ORDER BY concept;

// Заводские записи вендорских словарей. origin=factory обязателен для разметки стокового
// ROM: 128 записей из 371 заводскими не являются - 126 описывают патчи самих вендоров
// (RaceROM у EcuTek, ARC у UpRev), то есть чужой код, которого в стоке нет. Матч стоковой
// карты к patch-записи был бы не слабой подсказкой, а неверной. Метка группы для фильтра
// непригодна: Rev Limit Per Gear Mode1-4 лежит под Limiters рядом с заводскими.
MATCH (e:VendorEntry {family:'HR', origin:'factory'})
RETURN e.vendor AS vendor, e.name AS name, e.group AS grp, e.dims AS dims,
       e.axis_x AS axis_x, e.axis_y AS axis_y, e.concept AS concept
ORDER BY vendor, name;

// Документированные дефолты - единственный ключ каталога, работающий до Stage 3: ни
// резолвнутых операндов, ни семантики осей он не требует, ищется прямо в образе.
// Само совпадение значения даёт pattern, а не candidate: чем короче число, тем чаще оно
// встретится случайно. До candidate поднимает гомологичная сигнатура блока либо трейс.
// Поиск значения в дампе - вне Cypher: образа в графе нет (tools/mapkit/rom.py, scan()).
// Якорь: 22 факта kind=const, найден в образе сигнатурой блока 1 (K-Factor 26806).
MATCH (f:VendorFact {family:'HR', kind:'const'})
RETURN f.vendor AS vendor, f.subject AS subject, f.value AS value, f.units AS units,
       f.applies_to AS applies_to, f.anchor AS anchor, f.statement AS statement
ORDER BY subject;

// Границы применимости словарей. По умолчанию они уже: EcuTek документирует VQ37VHR
// (370Z, VVEL), донорский JK03A - VQ25HR без VVEL. Группа VVEL Valve Duration к JK03A
// неприменима вовсе, VTC Valve Advance применима.
// Якорь: vq37vhr=78, nissan=41, hr=15, racerom=1.
MATCH (f:VendorFact {family:'HR'})
RETURN f.applies_to AS applies_to, f.kind AS kind, count(*) AS facts
ORDER BY applies_to, kind;


// ════════════════════════════════════════════════════════════════════════════════════
// Раздел 11. Ворота эффективности - одним запросом
// ════════════════════════════════════════════════════════════════════════════════════

// Метрики раздела 11, считаемые из графа. Прогон, снизивший метрику, - провал ворот.
// Строка "факт" сверяется с колонкой якоря; расхождение разбирается, а не принимается.
//
// Здесь не все метрики раздела 11: якоря вендоров ищутся в образе, которого в графе нет
// (tools/mapkit/rom.py, scan()), и в этот запрос не входят.
//
// Считать НАДО через count(CASE WHEN ... THEN 1 END), а не через WHERE + count(*):
// WHERE отсеивает строки до агрегата, и метрика, равная нулю, возвращает не "0", а ноль
// строк - то есть исчезает из таблицы ровно тогда, когда ворота пройдены. Читалось бы это
// как "не измерено", и отличить пройденную метрику от сломанного запроса стало бы нельзя.
// Форма ниже всегда даёт строку на метрику.
//
// Pattern-предикат ((m)-[:WRITES]->()) внутри CASE WHEN Memgraph не поддерживает
// ("Not yet implemented"), поэтому наличие ребра считается через OPTIONAL MATCH.
MATCH (:Func {rom:$rom})-[r:ACCESSES]->()
WITH count(CASE WHEN r.r4 <> '' THEN 1 END) AS resolved, count(*) AS sites
RETURN 'Резолюция операндов' AS metric,
       toString(resolved) + '/' + toString(sites) AS fact,
       '551/554 (99.5%)' AS anchor, '>= 95%, 0 молча потерянных' AS gate
UNION ALL
MATCH (:Func {rom:$rom})-[r:ACCESSES]->()
WITH count(CASE WHEN r.verdict = 'conflict' THEN 1 END) AS n
RETURN 'Латентный брак каталога (bt != df)' AS metric,
       toString(n) AS fact,
       '18, все разобраны' AS anchor,
       'все разобраны' AS gate
UNION ALL
MATCH (:Func {rom:$rom})-[r:ACCESSES]->()
WITH count(CASE WHEN r.verdict = 'bt_only' THEN 1 END) AS n
RETURN 'Неухудшение vs backtrack' AS metric,
       toString(n) AS fact,
       '1, разобран (0x56cd8)' AS anchor,
       'все разобраны' AS gate
UNION ALL
MATCH (m:Map {rom:$rom})
RETURN 'Полнота каталога (:Map в графе)' AS metric,
       toString(count(*)) AS fact,
       '419 из 423' AS anchor,
       'все :Map в графе, вне - 4, за Stage 6' AS gate
UNION ALL
MATCH (m:Map {rom:$rom})
WITH count(CASE WHEN m.role = 'table' AND m.semantics <> '' AND m.scale_expr <> ''
                 AND m.confidence IN ['candidate', 'code', 'silicon'] THEN 1 END) AS n
RETURN 'Ворота дефа: выпускается таблиц' AS metric,
       toString(n) AS fact,
       '10' AS anchor,
       'растёт с разбором' AS gate
UNION ALL
MATCH (m:Map {rom:$rom})
WITH count(CASE WHEN m.role = 'table' AND m.semantics <> '' AND m.scale_expr <> ''
                 AND m.confidence = 'code' THEN 1 END) AS n
RETURN 'Ворота дефа: из них активных (code)' AS metric,
       toString(n) AS fact,
       '6' AS anchor,
       'активной эмитится только code' AS gate
UNION ALL
MATCH (m:Map {rom:$rom})
WITH count(CASE WHEN m.role = 'table' AND m.semantics <> '' AND m.scale_expr <> ''
                 AND m.confidence = 'candidate' THEN 1 END) AS n
RETURN 'Ворота дефа: помечено (candidate)' AS metric,
       toString(n) AS fact,
       '4' AS anchor,
       'суффикс (candidate) в категории' AS gate
UNION ALL
MATCH (m:Map {rom:$rom})
WITH count(CASE WHEN m.storagetype IS NULL OR m.storagetype = '' THEN 1 END) AS n
RETURN 'Геометрия каталога: :Map без storagetype' AS metric,
       toString(n) AS fact,
       '0' AS anchor,
       '0 - эмиссия без него невозможна' AS gate
UNION ALL
MATCH (m:Map {rom:$rom})
WITH count(CASE WHEN m.role = 'table' AND m.semantics <> '' AND m.scale_expr = ''
                THEN 1 END) AS n
RETURN 'Читаемость: семантика без шкалы' AS metric,
       toString(n) AS fact,
       '0 из 10 выпускаемых' AS anchor,
       '0 без шкалы, [cand] снимается трейсом' AS gate
UNION ALL
MATCH (a:Axis {rom:$rom})
WITH count(CASE WHEN a.confidence = 'pattern' THEN 1 END) AS n, count(*) AS t
RETURN 'Оси на резерве (уровень pattern)' AS metric,
       toString(n) + '/' + toString(t) AS fact,
       '17 из 227' AS anchor,
       '0, разбирает Stage 6' AS gate
UNION ALL
MATCH (a:Axis {rom:$rom})
WITH count(CASE WHEN a.monotonic = false THEN 1 END) AS n, count(*) AS t
RETURN 'Ось против кода ядра (monotonic=false)' AS metric,
       toString(n) + '/' + toString(t) AS fact,
       '1 из 227 (0x119b2)' AS anchor,
       '0' AS gate
UNION ALL
MATCH (m:Map {rom:$rom})
WITH count(CASE WHEN m.values_hash IS NULL OR m.values_hash = '' THEN 1 END) AS n,
     count(*) AS t
RETURN 'Слой измерен: :Map без значений' AS metric,
       toString(n) + '/' + toString(t) AS fact,
       '0 из 419' AS anchor,
       '0, промах чтения останавливает загрузку' AS gate
UNION ALL
MATCH (a:Axis {rom:$rom})
WITH count(CASE WHEN a.values IS NULL OR size(a.values) = 0 THEN 1 END) AS n,
     count(*) AS t
RETURN 'Слой измерен: :Axis без значений' AS metric,
       toString(n) + '/' + toString(t) AS fact,
       '0 из 227' AS anchor,
       '0, промах чтения останавливает загрузку' AS gate
UNION ALL
MATCH (m:Map {rom:$rom}) WHERE m.confidence = 'code'
OPTIONAL MATCH (m)-[:AXIS_X|AXIS_Y]->(:Axis {rom:$rom})-[:INDEXED_BY]->(rin:Reg)
OPTIONAL MATCH (m)-[:WRITES]->(rout:Reg)
WITH m, count(rin) AS n_in, count(rout) AS n_out
WITH count(CASE WHEN n_in > 0 AND n_out > 0 THEN 1 END) AS closed, count(*) AS total
RETURN 'Замкнутость code (:INDEXED_BY и :WRITES)' AS metric,
       toString(closed) + '/' + toString(total) AS fact,
       'нет учёта' AS anchor,
       '100%' AS gate
UNION ALL
MATCH (m:Map {rom:$rom})
OPTIONAL MATCH (m)-[x:MATCHES]->(:A2LEntry)
OPTIONAL MATCH (m)-[h:HOMOLOG]->(:Map)
WITH m, count(x) + count(h) AS links
WITH count(CASE WHEN links > 0 THEN 1 END) AS linked, count(*) AS total
RETURN 'Покрытие идентичности (:MATCHES/:HOMOLOG)' AS metric,
       toString(linked) + '/' + toString(total) AS fact,
       '0' AS anchor,
       'подсказка, растёт' AS gate
UNION ALL
MATCH (m:Map {rom:$rom})
WITH count(CASE WHEN m.confidence = 'silicon' THEN 1 END) AS n,
     count(CASE WHEN m.confidence = 'code' THEN 1 END) AS c
RETURN 'Верификация: silicon из code' AS metric,
       toString(n) + '/' + toString(c) AS fact,
       'точечно' AS anchor,
       'по мере стенда' AS gate;


// ── Разбор провала ворот: метрики поштучно ──────────────────────────────────────────

// Сайты, где перепись резолвера разошлась с эталоном. Якорь: 18, все разобраны -
// 10 базовых (эталон неверен на всех), 3 недостижимая ветка и остаточные регистры,
// 5 константа mov.w, прочитанная эталоном как 32-битная.
MATCH (a:Func {rom:$rom})-[x:ACCESSES]->(m:Map {rom:$rom})
WHERE x.verdict = 'conflict'
RETURN a.addr AS accessor, x.callsite AS site, m.addr AS table, x.r4 AS r4,
       x.base AS base, x.kind AS kind
ORDER BY site;

// Карта, читаемая входами разной формы: форма, заданная двумя несовместимыми способами.
// Геометрия входа делает геометрию карты однозначной, и загрузчик держит это фактом.
// Якорь: 0 - ни одна карта не читается двумя входами.
MATCH (m:Map {rom:$rom})-[:VIA]->(w:Interp {rom:$rom})
WITH m, collect(DISTINCT w.addr) AS wrappers,
     collect(DISTINCT toString(w.width) + 'x' + coalesce(toString(w.height), '-')) AS shapes
WHERE size(shapes) > 1
RETURN m.addr AS table, wrappers, shapes;

// Непересечение цензов по таблицам: общая таблица у двух семейств доступа есть находка, а
// не разновидность нормы. Якорь: 0 - семейства не пересекаются ни одной таблицей.
MATCH (m:Map {rom:$rom})
WITH m.family AS family, collect(m.addr) AS tables
RETURN family, size(tables) AS n
ORDER BY family;

// Осиротевшие узлы: карта без входа и аксессора. Якорь: 0.
MATCH (m:Map {rom:$rom})
WHERE NOT (m)-[:VIA]->(:Interp) AND NOT (:Func)-[:ACCESSES]->(m)
RETURN m.addr AS table, m.family AS family, m.confidence AS confidence;
