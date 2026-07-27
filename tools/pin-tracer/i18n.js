(function attachPinTracerI18n(root, factory) {
  const i18n = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = i18n;
  }
  root.PinTracerI18n = i18n;
})(typeof globalThis !== "undefined" ? globalThis : this, function createPinTracerI18n() {
  "use strict";

  const DEFAULT_LANGUAGE = "en";
  const SUPPORTED_LANGUAGES = Object.freeze(["en", "ru"]);

  const en = Object.freeze({
    "app.title": "VQ HR ECU Pin Tracer",
    "app.description": "Offline workspace for tracing VQ HR ECM connector terminals to Renesas SH7058 MCU pins.",
    "app.subtitle": "Trace ECM connector terminals to Renesas SH7058 FP-256H pins, record measured component paths, and keep preloaded hypotheses separate from physical board traces.",
    "stats.aria": "Workspace statistics",
    "stats.tracedPairs": "Traced pairs",
    "stats.listedTerminals": "Listed terminals",
    "toolbar.aria": "Workspace controls",
    "action.export": "Export JSON",
    "action.import": "Import JSON",
    "action.clearWorkspace": "Clear workspace",
    "action.showSavedLines": "Show saved lines",
    "action.enableAdvancedPins": "Enable MCU bus and infrastructure pins",
    "action.clearSelection": "Clear selection",
    "action.useTemplate": "Use template",
    "action.saveConnection": "Save connection",
    "action.updateConnection": "Update connection",
    "action.edit": "Edit",
    "action.delete": "Delete",
    "action.selectPin": "Select {pin}",
    "import.aria": "Import workspace JSON",
    "language.aria": "Interface language",
    "language.en": "English",
    "language.ru": "Russian",
    "legend.aria": "ECM and MCU pin category legend",
    "legend.analog": "Analog",
    "legend.timer": "Timer/PWM",
    "legend.communication": "Communication",
    "legend.interrupt": "Interrupt",
    "legend.gpio": "GPIO",
    "legend.bus": "Bus/system",
    "legend.wide": "Wide terminal",
    "diagram.aria": "ECM and MCU pin diagrams",
    "ecu.heading": "ECM connectors",
    "ecu.orientation": "Harness side, source orientation",
    "mcu.packageAria": "Renesas SH7058 MCU",
    "mcu.topAria": "MCU top edge pins",
    "mcu.leftAria": "MCU left edge pins",
    "mcu.rightAria": "MCU right edge pins",
    "mcu.bottomAria": "MCU bottom edge pins",
    "mcu.topView": "FP-256H, top view",
    "mcu.coreDescription": "Selectable pins are peripheral I/O candidates. Power, clock, debug, and external bus pins are dimmed by default. Pin functions use the SH7058 Rev. 3 column in the Renesas comparison appendix; actual multiplexing must be checked in firmware and on the board.",
    "inspector.heading": "Selection and connection editor",
    "connections.heading": "Recorded connections",
    "connections.empty": "No connections recorded. Select one ECM terminal and one enabled MCU pin to create the first trace.",
    "storage.saved": "Saved locally",
    "storage.empty": "Empty workspace",
    "storage.loadError": "Local data could not be loaded",
    "table.ecuTerminal": "ECM terminal",
    "table.mcuPin": "MCU pin",
    "table.topology": "Topology",
    "table.routeComment": "Route / comment",
    "table.actions": "Actions",
    "footer.note": "ECM terminal abbreviations and wire colors are transcribed from the supplied one-page pinout; expanded functions follow the 2007 G35 Sedan service manual. ECM colors indicate the expected MCU-side function class, not voltage or current rating. Wide-terminal markers follow the connector drawing and do not assert a current rating. Every preloaded MCU relationship and topology is a hypothesis, not an internal schematic fact. Board continuity, component marking, firmware port configuration, and bench behavior remain independent verification steps.",
    "connector.title": "{id} / source overview {alias}",
    "connector.meta": "{color}, terminals {start}-{end}",
    "connector.gridAria": "{id} connector terminal grid",
    "connector.color.Black": "Black",
    "connector.color.Brown": "Brown",
    "connector.color.Gray": "Gray",
    "connector.noun": "connector",
    "pin.ecuAria": "{connector} terminal {pin}, {signal}, {description}",
    "pin.ecuAriaUnlisted": "{connector} terminal {pin}, not listed in source",
    "pin.mcuAria": "MCU pin {pin}, {name}, {categories}",
    "common.notListedSource": "Not listed in source",
    "common.notListed": "Not listed",
    "common.notListedLower": "not listed",
    "common.unknown": "unknown",
    "common.notSelected": "Not selected",
    "wire.label": "Wire {code} ({color})",
    "selection.ecuTerminal": "ECM terminal",
    "selection.mcuPin": "MCU pin",
    "selection.selectEcu": "Select a terminal in the connector pinout.",
    "selection.selectMcu": "Select an enabled peripheral pin.",
    "selection.capabilities": "Capabilities: {categories}",
    "selection.serviceNotListed": "Not listed in service table",
    "selection.connector": "{color} connector",
    "inspector.empty": "Start from either side. Selecting an ECM terminal shows topology guidance and possible MCU targets. Selecting an MCU pin shows its peripheral functions and seeded hypotheses.",
    "inspector.possibleTopology": "Possible topology template",
    "inspector.genericPattern": "Generic engineering pattern only; inspect this board before recording a route.",
    "inspector.endpointModel": "Endpoint model:",
    "inspector.suggestedMcu": "Suggested MCU targets",
    "inspector.unverifiedCandidate": "Unverified candidate.",
    "inspector.genericCandidates": "All {categories} candidates are highlighted automatically. Select the measured endpoint.",
    "inspector.peripheralFunction": "Peripheral function",
    "inspector.compatibleEcu": "Compatible populated ECM terminals are highlighted automatically.",
    "inspector.preloadedHypotheses": "Preloaded hypotheses",
    "hypothesis.label": "Hypothesis",
    "hypothesis.unverified": "unverified",
    "hypothesis.none": "No connector-level hypothesis is seeded for this pin. Use peripheral type, firmware PFC setup, and continuity measurements.",
    "form.categoryMismatch": "The selected MCU capabilities ({actual}) differ from the usual {expected} endpoint classes for this ECM signal. This may be valid through an intermediate ASIC, but the observed route must explain it.",
    "form.topology": "Topology template",
    "form.observedPath": "Observed component path",
    "form.observedPathPlaceholder": "Record components and nets actually followed on this board.",
    "form.templateTitle": "Copy this generic template into the path field, then verify and edit it.",
    "form.comment": "Connection comment",
    "form.commentPlaceholder": "Example: passes through Q104 MOSFET, 100 ohm gate resistor, and D52 flyback clamp",
    "template.possible": "Possible template only: {route}",
    "confirm.replaceTemplate": "Replace the current observed component path with this generic template?",
    "alert.missingPath": "Record the component path observed on this board.",
    "confirm.replaceDuplicate": "A connection between these pins already exists. Replace it?",
    "confirm.deleteConnection": "Delete connection ECM {ecuPin} -> MCU {mcuPin}?",
    "confirm.importWorkspace": "Replace the current connection workspace with the imported file?",
    "alert.importFailed": "Could not import the selected JSON file.",
    "confirm.clearWorkspace": "Delete all recorded connections from this browser? Export first if they are needed.",
    "category.analog": "analog/ADC",
    "category.timer": "timer/PWM",
    "category.communication": "communication",
    "category.interrupt": "interrupt",
    "category.gpio": "GPIO",
    "category.bus": "external bus",
    "category.system": "system/infrastructure",
    "direction.output": "ECM output",
    "direction.input": "ECM input",
    "direction.bidirectional": "ECM input/output",
    "direction.reference": "Supply, ground, or sensor reference",
    "direction.manualConflict": "Sensor signal; service table direction column says Output",
    "generic.analog": "ADC channel behind the input conditioning",
    "generic.timer": "Timer capture or conditioned GPIO input",
    "generic.injector": "ATU-II one-shot or GPIO output behind an injector driver",
    "generic.ignition": "APC pulse, timer, or GPIO output behind an ignition buffer",
    "generic.hbridge": "PWM or GPIO control outputs behind an H-bridge driver",
    "generic.lowSide": "PWM or GPIO output behind a low-side driver",
    "generic.logicOutput": "Timer or GPIO output behind a buffer or open-drain stage",
    "generic.can": "HCAN transmit/receive pair behind a CAN transceiver",
    "generic.kline": "SCI transmit/receive pair behind a K-line transceiver",
    "generic.knock": "ADC or serial output of a knock-sensor front end",
    "generic.airFuel": "ADC or serial output of an A/F-sensor interface",
    "generic.oxygen": "ADC input behind oxygen-sensor conditioning",
    "generic.switch": "Conditioned GPIO, IRQ, or ADC input",
    "generic.power": "Supply network or monitored ADC input",
    "generic.ground": "Vss/AVss return network",
    "generic.unknown": "GPIO or intermediate ASIC interface",
    "evidence.firmwareCrossModel.label": "firmware + family pattern",
    "evidence.firmwareCrossModel.explanation": "The target firmware confirms the peripheral family. The exact pin and cylinder assignment is transferred or extended from an older Nissan SH7055 pattern and remains unverified.",
    "evidence.crossModel.label": "cross-model",
    "evidence.crossModel.explanation": "The signal-to-channel pair is documented on an older Nissan SH7055 ECU, not on this board.",
    "evidence.muxOnly.label": "MCU mux only",
    "evidence.muxOnly.explanation": "The Renesas manual permits this peripheral on these pins; firmware selection and board routing are unverified.",
    "topology.unknown.label": "Unknown / custom",
    "topology.unknown.route": "ECM terminal -> unknown component chain -> MCU pin",
    "topology.direct.label": "Direct logic / series resistor",
    "topology.direct.route": "ECM terminal -> ESD or clamp -> series resistor -> MCU GPIO",
    "topology.analog.label": "Analog sensor input",
    "topology.analog.route": "ECM terminal -> protection -> series resistor -> RC low-pass -> clamp -> MCU ADC",
    "topology.timer.label": "Powered crank/cam position input",
    "topology.timer.route": "ECM terminal -> protection -> pull-up or level conditioning -> Schmitt/comparator stage -> MCU timer capture or GPIO",
    "topology.switch.label": "Conditioned switch input",
    "topology.switch.route": "ECM terminal -> pull-up or divider -> RC filter -> clamp/Schmitt stage -> MCU GPIO or ADC",
    "topology.lowSide.label": "Low-side actuator driver",
    "topology.lowSide.route": "MCU timer/GPIO -> predriver -> low-side MOSFET -> flyback clamp and optional current sense -> ECM terminal",
    "topology.logicOutput.label": "Buffered or open-drain output",
    "topology.logicOutput.route": "MCU timer/GPIO -> series resistor -> logic buffer or open-drain transistor -> protection -> ECM terminal",
    "topology.injector.label": "Injector power driver",
    "topology.injector.route": "MCU ATU-II one-shot or GPIO -> injector driver ASIC or gate driver -> low-side MOSFET -> current sense and flyback clamp -> ECM terminal",
    "topology.ignition.label": "Ignition trigger path",
    "topology.ignition.route": "MCU APC pulse, timer, or GPIO -> series resistor and buffer or coil-driver interface -> ECM terminal",
    "topology.hbridge.label": "Throttle H-bridge",
    "topology.hbridge.route": "MCU PWM/direction outputs -> H-bridge driver -> power MOSFET bridge -> ECM motor terminal",
    "topology.can.label": "CAN transceiver",
    "topology.can.route": "ECM CANH/CANL -> optional ESD, common-mode choke, and termination -> CAN transceiver -> MCU HCAN TX/RX",
    "topology.can.endpoint": "CANH and CANL form one differential bus pair. Neither connector terminal maps one-to-one to an MCU TX or RX pin.",
    "topology.kline.label": "K-line transceiver",
    "topology.kline.route": "ECM K-line -> protection and series resistor -> K-line transceiver -> MCU SCI TX/RX",
    "topology.kline.endpoint": "One bidirectional K-line commonly reaches separate MCU TX and RX signals through the transceiver. Record each MCU branch only when it has been physically traced.",
    "topology.knock.label": "Knock analog front-end",
    "topology.knock.route": "ECM knock input -> protection -> band-pass/gain or knock ASIC -> MCU ADC/serial interface",
    "topology.airFuel.label": "A/F sensor interface",
    "topology.airFuel.route": "ECM A/F sensor terminal -> protection and filter -> A/F controller ASIC or differential amplifier -> MCU ADC or serial interface",
    "topology.oxygen.label": "Heated oxygen sensor signal input",
    "topology.oxygen.route": "ECM oxygen sensor terminal -> protection and RC filter -> clamp or amplifier -> MCU ADC",
    "topology.power.label": "Power supply / monitored supply",
    "topology.power.route": "ECM supply -> surge/reverse-polarity protection -> regulator or high-side switch -> MCU supply; optional divider -> ADC",
    "topology.power.endpoint": "A connector supply normally fans out into a power network. It is not expected to have one exclusive MCU endpoint.",
    "topology.ground.label": "Ground plane / reference",
    "topology.ground.route": "ECM ground terminal -> power or analog ground plane -> MCU Vss/AVss and local return network",
    "topology.ground.endpoint": "Ground is a shared return network, not a one-to-one signal connection.",
    "topology.customAsic.label": "Intermediate custom ASIC",
    "topology.customAsic.route": "ECM terminal -> analog/driver ASIC channel -> shared serial or parallel interface -> MCU",
    "topology.customAsic.endpoint": "The connector signal may terminate inside the ASIC and reach the MCU only through a shared interface."
  });

  const ru = Object.freeze({
    "app.title": "VQ HR ECU Pin Tracer",
    "app.description": "Автономный инструмент трассировки контактов ECM VQ HR до выводов MCU Renesas SH7058.",
    "app.subtitle": "Трассировка контактов разъёмов ECM до выводов Renesas SH7058 FP-256H с записью измеренных цепей компонентов и отделением исходных гипотез от фактических маршрутов платы.",
    "stats.aria": "Статистика рабочего пространства",
    "stats.tracedPairs": "Прозвоненные пары",
    "stats.listedTerminals": "Контакты ECM",
    "toolbar.aria": "Управление рабочим пространством",
    "action.export": "Экспорт JSON",
    "action.import": "Импорт JSON",
    "action.clearWorkspace": "Очистить данные",
    "action.showSavedLines": "Показать сохранённые линии",
    "action.enableAdvancedPins": "Включить шину и системные выводы MCU",
    "action.clearSelection": "Сбросить выбор",
    "action.useTemplate": "Вставить шаблон",
    "action.saveConnection": "Сохранить связь",
    "action.updateConnection": "Обновить связь",
    "action.edit": "Изменить",
    "action.delete": "Удалить",
    "action.selectPin": "Выбрать {pin}",
    "import.aria": "Импорт рабочего пространства из JSON",
    "language.aria": "Язык интерфейса",
    "language.en": "Английский",
    "language.ru": "Русский",
    "legend.aria": "Категории контактов ECM и выводов MCU",
    "legend.analog": "Analog",
    "legend.timer": "Timer/PWM",
    "legend.communication": "Communication",
    "legend.interrupt": "Interrupt",
    "legend.gpio": "GPIO",
    "legend.bus": "Bus/system",
    "legend.wide": "Wide terminal",
    "diagram.aria": "Схемы разъёмов ECM и корпуса MCU",
    "ecu.heading": "Разъёмы ECM",
    "ecu.orientation": "Со стороны жгута, ориентация источника",
    "mcu.packageAria": "Микроконтроллер Renesas SH7058",
    "mcu.topAria": "Верхняя сторона выводов MCU",
    "mcu.leftAria": "Левая сторона выводов MCU",
    "mcu.rightAria": "Правая сторона выводов MCU",
    "mcu.bottomAria": "Нижняя сторона выводов MCU",
    "mcu.topView": "FP-256H, вид сверху",
    "mcu.coreDescription": "Для выбора доступны выводы-кандидаты периферийного ввода-вывода. Выводы питания, тактирования, отладки и внешней шины по умолчанию приглушены. Функции выводов взяты из колонки SH7058 Rev. 3 сравнительного приложения Renesas; фактическую настройку мультиплексора необходимо проверить в прошивке и на плате.",
    "inspector.heading": "Выбор и редактор связи",
    "connections.heading": "Сохранённые связи",
    "connections.empty": "Связей пока нет. Выберите один контакт ECM и один доступный вывод MCU, чтобы записать первую трассу.",
    "storage.saved": "Сохранено локально",
    "storage.empty": "Рабочее пространство пусто",
    "storage.loadError": "Не удалось загрузить локальные данные",
    "table.ecuTerminal": "Контакт ECM",
    "table.mcuPin": "Вывод MCU",
    "table.topology": "Топология",
    "table.routeComment": "Маршрут / комментарий",
    "table.actions": "Действия",
    "footer.note": "Сокращения контактов ECM и цвета проводов перенесены из предоставленного одностраничного pinout; расшифровки функций основаны на сервисном руководстве G35 Sedan 2007. Цвета контактов ECM показывают ожидаемый класс функции на стороне MCU, а не номинал напряжения или тока. Маркеры широких контактов повторяют чертёж разъёма и не задают допустимый ток. Все исходные связи с MCU и топологии являются гипотезами, а не фактами внутренней схемы. Прозвонка платы, маркировка компонентов, конфигурация портов прошивки и поведение на стенде остаются независимыми этапами проверки.",
    "connector.title": "{id} / исходная схема {alias}",
    "connector.meta": "{color}, контакты {start}-{end}",
    "connector.gridAria": "Сетка контактов разъёма {id}",
    "connector.color.Black": "Чёрный",
    "connector.color.Brown": "Коричневый",
    "connector.color.Gray": "Серый",
    "connector.noun": "разъём",
    "pin.ecuAria": "{connector}, контакт {pin}, {signal}, {description}",
    "pin.ecuAriaUnlisted": "{connector}, контакт {pin}, не указан в источнике",
    "pin.mcuAria": "MCU, вывод {pin}, {name}, {categories}",
    "common.notListedSource": "Не указан в источнике",
    "common.notListed": "Не указан",
    "common.notListedLower": "не указан",
    "common.unknown": "неизвестно",
    "common.notSelected": "Не выбран",
    "wire.label": "Провод {code} ({color})",
    "selection.ecuTerminal": "Контакт ECM",
    "selection.mcuPin": "Вывод MCU",
    "selection.selectEcu": "Выберите контакт на схеме разъёма.",
    "selection.selectMcu": "Выберите доступный периферийный вывод.",
    "selection.capabilities": "Возможности: {categories}",
    "selection.serviceNotListed": "Не указан в таблице сервисного руководства",
    "selection.connector": "{color} разъём",
    "inspector.empty": "Начать можно с любой стороны. Выбор контакта ECM показывает типовую топологию и возможные выводы MCU. Выбор вывода MCU показывает его периферийные функции и исходные гипотезы.",
    "inspector.possibleTopology": "Возможный шаблон топологии",
    "inspector.genericPattern": "Только типовой схемотехнический вариант; перед записью маршрута проверьте фактическую плату.",
    "inspector.endpointModel": "Модель конечной точки:",
    "inspector.suggestedMcu": "Предлагаемые выводы MCU",
    "inspector.unverifiedCandidate": "Непроверенный кандидат.",
    "inspector.genericCandidates": "Все кандидаты категорий {categories} подсвечены автоматически. Выберите измеренную конечную точку.",
    "inspector.peripheralFunction": "Периферийная функция",
    "inspector.compatibleEcu": "Совместимые заполненные контакты ECM подсвечены автоматически.",
    "inspector.preloadedHypotheses": "Исходные гипотезы",
    "hypothesis.label": "Гипотеза",
    "hypothesis.unverified": "не проверено",
    "hypothesis.none": "Для этого вывода нет исходной гипотезы уровня разъёма. Используйте тип периферии, конфигурацию PFC в прошивке и прозвонку.",
    "form.categoryMismatch": "Возможности выбранного вывода MCU ({actual}) отличаются от обычных классов конечной точки для этого сигнала ECM ({expected}). Это допустимо при наличии промежуточного ASIC, но наблюдаемый маршрут должен объяснять такое соответствие.",
    "form.topology": "Шаблон топологии",
    "form.observedPath": "Наблюдаемый маршрут компонентов",
    "form.observedPathPlaceholder": "Запишите компоненты и цепи, фактически прослеженные на этой плате.",
    "form.templateTitle": "Скопировать типовой шаблон в поле маршрута для последующей проверки и редактирования.",
    "form.comment": "Комментарий к связи",
    "form.commentPlaceholder": "Пример: проходит через MOSFET Q104, резистор затвора 100 Ом и защитный диод D52",
    "template.possible": "Только возможный шаблон: {route}",
    "confirm.replaceTemplate": "Заменить текущий наблюдаемый маршрут этим типовым шаблоном?",
    "alert.missingPath": "Запишите маршрут компонентов, наблюдаемый на этой плате.",
    "confirm.replaceDuplicate": "Связь между этими выводами уже существует. Заменить её?",
    "confirm.deleteConnection": "Удалить связь ECM {ecuPin} -> MCU {mcuPin}?",
    "confirm.importWorkspace": "Заменить текущее рабочее пространство данными из импортируемого файла?",
    "alert.importFailed": "Не удалось импортировать выбранный JSON-файл.",
    "confirm.clearWorkspace": "Удалить все сохранённые связи из этого браузера? При необходимости сначала экспортируйте их.",
    "category.analog": "аналоговый/ADC",
    "category.timer": "таймер/PWM",
    "category.communication": "интерфейс связи",
    "category.interrupt": "прерывание",
    "category.gpio": "GPIO",
    "category.bus": "внешняя шина",
    "category.system": "системный/инфраструктурный",
    "direction.output": "Выход ECM",
    "direction.input": "Вход ECM",
    "direction.bidirectional": "Вход/выход ECM",
    "direction.reference": "Питание, земля или опорная цепь датчика",
    "direction.manualConflict": "Сигнал датчика; в колонке направления сервисной таблицы указано Output",
    "generic.analog": "Канал ADC после входной обработки",
    "generic.timer": "Вход захвата таймера или обработанный вход GPIO",
    "generic.injector": "Выход ATU-II one-shot или GPIO перед драйвером форсунки",
    "generic.ignition": "Импульс APC, таймер или GPIO перед буфером зажигания",
    "generic.hbridge": "Управляющие выходы PWM или GPIO перед H-мостом",
    "generic.lowSide": "Выход PWM или GPIO перед low-side драйвером",
    "generic.logicOutput": "Выход таймера или GPIO перед буфером либо каскадом с открытым стоком",
    "generic.can": "Пара передачи/приёма HCAN за CAN-трансивером",
    "generic.kline": "Пара передачи/приёма SCI за K-line трансивером",
    "generic.knock": "Выход ADC или последовательного интерфейса входного каскада детонации",
    "generic.airFuel": "Выход ADC или последовательного интерфейса контроллера A/F",
    "generic.oxygen": "Вход ADC после обработки сигнала кислородного датчика",
    "generic.switch": "Обработанный вход GPIO, IRQ или ADC",
    "generic.power": "Цепь питания или контролируемый вход ADC",
    "generic.ground": "Общая возвратная цепь Vss/AVss",
    "generic.unknown": "GPIO или интерфейс промежуточного ASIC",
    "evidence.firmwareCrossModel.label": "прошивка + семейный шаблон",
    "evidence.firmwareCrossModel.explanation": "Целевая прошивка подтверждает семейство периферии. Точный вывод и назначение цилиндра перенесены или продолжены по шаблону более старого Nissan SH7055 и остаются непроверенными.",
    "evidence.crossModel.label": "другая модель",
    "evidence.crossModel.explanation": "Пара сигнал-канал документирована для более старого ECM Nissan SH7055, но не для этой платы.",
    "evidence.muxOnly.label": "только mux MCU",
    "evidence.muxOnly.explanation": "Руководство Renesas допускает эту периферию на указанных выводах; выбор в прошивке и маршрут платы не проверены.",
    "topology.unknown.label": "Неизвестная / особая",
    "topology.unknown.route": "Контакт ECM -> неизвестная цепь компонентов -> вывод MCU",
    "topology.direct.label": "Прямая логика / последовательный резистор",
    "topology.direct.route": "Контакт ECM -> ESD-защита или ограничитель -> последовательный резистор -> GPIO MCU",
    "topology.analog.label": "Вход аналогового датчика",
    "topology.analog.route": "Контакт ECM -> защита -> последовательный резистор -> RC ФНЧ -> ограничитель -> ADC MCU",
    "topology.timer.label": "Вход датчика положения коленвала/распредвала с питанием",
    "topology.timer.route": "Контакт ECM -> защита -> подтяжка или согласование уровней -> триггер Шмитта/компаратор -> захват таймера MCU или GPIO",
    "topology.switch.label": "Обработанный дискретный вход",
    "topology.switch.route": "Контакт ECM -> подтяжка или делитель -> RC-фильтр -> ограничитель/триггер Шмитта -> GPIO или ADC MCU",
    "topology.lowSide.label": "Low-side драйвер исполнительного механизма",
    "topology.lowSide.route": "Таймер/GPIO MCU -> предрайвер -> low-side MOSFET -> flyback-ограничитель и возможный контроль тока -> контакт ECM",
    "topology.logicOutput.label": "Буферизованный выход или открытый сток",
    "topology.logicOutput.route": "Таймер/GPIO MCU -> последовательный резистор -> логический буфер или транзистор с открытым стоком -> защита -> контакт ECM",
    "topology.injector.label": "Силовой драйвер форсунки",
    "topology.injector.route": "ATU-II one-shot или GPIO MCU -> ASIC драйвера форсунки или драйвер затвора -> low-side MOSFET -> контроль тока и flyback-ограничитель -> контакт ECM",
    "topology.ignition.label": "Цепь запуска зажигания",
    "topology.ignition.route": "Импульс APC, таймер или GPIO MCU -> последовательный резистор и буфер либо интерфейс драйвера катушки -> контакт ECM",
    "topology.hbridge.label": "H-мост дросселя",
    "topology.hbridge.route": "Выходы PWM/направления MCU -> драйвер H-моста -> силовой MOSFET-мост -> контакт мотора ECM",
    "topology.can.label": "CAN-трансивер",
    "topology.can.route": "ECM CANH/CANL -> возможная ESD-защита, синфазный дроссель и терминация -> CAN-трансивер -> MCU HCAN TX/RX",
    "topology.can.endpoint": "CANH и CANL образуют одну дифференциальную пару шины. Ни один из контактов разъёма не соответствует напрямую и единственно выводу TX или RX MCU.",
    "topology.kline.label": "K-line трансивер",
    "topology.kline.route": "ECM K-line -> защита и последовательный резистор -> K-line трансивер -> MCU SCI TX/RX",
    "topology.kline.endpoint": "Одна двунаправленная K-line обычно приходит через трансивер на отдельные сигналы TX и RX MCU. Записывайте каждую ветвь MCU только после физической трассировки.",
    "topology.knock.label": "Аналоговый входной каскад детонации",
    "topology.knock.route": "Вход детонации ECM -> защита -> полосовой фильтр/усилитель или ASIC детонации -> ADC/последовательный интерфейс MCU",
    "topology.airFuel.label": "Интерфейс датчика A/F",
    "topology.airFuel.route": "Контакт датчика A/F ECM -> защита и фильтр -> ASIC контроллера A/F или дифференциальный усилитель -> ADC или последовательный интерфейс MCU",
    "topology.oxygen.label": "Вход сигнала подогреваемого кислородного датчика",
    "topology.oxygen.route": "Контакт кислородного датчика ECM -> защита и RC-фильтр -> ограничитель или усилитель -> ADC MCU",
    "topology.power.label": "Питание / контролируемое питание",
    "topology.power.route": "Питание ECM -> защита от выбросов и обратной полярности -> стабилизатор или high-side ключ -> питание MCU; возможный делитель -> ADC",
    "topology.power.endpoint": "Питание с контакта разъёма обычно разветвляется в общую силовую сеть. Для него не ожидается одна исключительная конечная точка MCU.",
    "topology.ground.label": "Земля / опорная плоскость",
    "topology.ground.route": "Контакт земли ECM -> силовая или аналоговая земля -> Vss/AVss MCU и локальные возвратные цепи",
    "topology.ground.endpoint": "Земля является общей возвратной сетью, а не связью один-к-одному.",
    "topology.customAsic.label": "Промежуточный специализированный ASIC",
    "topology.customAsic.route": "Контакт ECM -> аналоговый канал или драйвер ASIC -> общий последовательный или параллельный интерфейс -> MCU",
    "topology.customAsic.endpoint": "Сигнал разъёма может завершаться внутри ASIC и достигать MCU только через общий интерфейс."
  });

  const REFERENCE_TEXT_RU = Object.freeze({
    "The source overview marks terminal 53 as a 12 V bench supply point; the service table names it IGNSW.": "На исходной схеме контакт 53 отмечен как точка стендового питания 12 В; в сервисной таблице он называется IGNSW.",
    "The service table names this terminal BATT and describes it as a continuously supplied ECM input.": "В сервисной таблице контакт называется BATT и описан как вход ECM с постоянным питанием.",
    "The source overview marks this terminal CAN L.": "На исходной схеме этот контакт отмечен как CAN L.",
    "The source overview marks this terminal CAN H.": "На исходной схеме этот контакт отмечен как CAN H.",
    "The source overview marks this terminal ISO; the service table names it KLINE.": "На исходной схеме этот контакт отмечен как ISO; в сервисной таблице он называется KLINE.",
    "The source overview marks terminal 125 as a 12 V bench supply point; the service table names it VBR.": "На исходной схеме контакт 125 отмечен как точка стендового питания 12 В; в сервисной таблице он называется VBR.",
    "The source overview marks this terminal as ground.": "На исходной схеме этот контакт отмечен как земля.",
    "The service table prints Output in the direction column for the power steering pressure sensor. Its sensor-voltage role indicates an ECM input, so the printed direction should be treated as suspect.": "В колонке направления сервисной таблицы для датчика давления ГУР напечатано Output. Роль сигнала напряжения датчика указывает на вход ECM, поэтому указанное направление следует считать сомнительным.",
    "Possible IGN#1 timing output through a buffer or coil-driver interface.": "Возможный времязадающий выход IGN#1 через буфер или интерфейс драйвера катушки.",
    "Possible IGN#2 timing output through a buffer or coil-driver interface.": "Возможный времязадающий выход IGN#2 через буфер или интерфейс драйвера катушки.",
    "Possible IGN#3 timing output through a buffer or coil-driver interface.": "Возможный времязадающий выход IGN#3 через буфер или интерфейс драйвера катушки.",
    "Possible IGN#4 timing output through a buffer or coil-driver interface.": "Возможный времязадающий выход IGN#4 через буфер или интерфейс драйвера катушки.",
    "Possible IGN#5 timing output through a buffer or coil-driver interface.": "Возможный времязадающий выход IGN#5 через буфер или интерфейс драйвера катушки.",
    "Possible IGN#6 timing output through a buffer or coil-driver interface.": "Возможный времязадающий выход IGN#6 через буфер или интерфейс драйвера катушки.",
    "Possible APS1 ADC channel by analogy with an older documented Nissan SH7055 ECU.": "Возможный канал ADC для APS1 по аналогии с документированным более старым ECM Nissan на SH7055.",
    "Possible throttle position ADC channel by analogy with an older documented Nissan SH7055 ECU.": "Возможный канал ADC положения дросселя по аналогии с документированным более старым ECM Nissan на SH7055.",
    "Possible APS2 ADC channel by analogy with an older documented Nissan SH7055 ECU.": "Возможный канал ADC для APS2 по аналогии с документированным более старым ECM Nissan на SH7055.",
    "Possible knock-front-end ADC output by analogy with an older single-channel Nissan SH7055 ECU; this does not establish a direct endpoint for either bank on this board.": "Возможный выход ADC входного каскада детонации по аналогии с более старым одноканальным ECM Nissan на SH7055; это не устанавливает прямую конечную точку ни для одного банка на этой плате.",
    "Possible crank position timer input by analogy with an older documented Nissan SH7055 ECU.": "Возможный вход таймера положения коленвала по аналогии с документированным более старым ECM Nissan на SH7055.",
    "Possible cam position timer input by analogy with an older documented Nissan SH7055 ECU.": "Возможный вход таймера положения распредвала по аналогии с документированным более старым ECM Nissan на SH7055.",
    "Possible throttle H-bridge control output; exact bank and polarity are unknown.": "Возможный управляющий выход H-моста дросселя; точный банк и полярность неизвестны.",
    "Possible second throttle H-bridge control output; exact function is unknown.": "Возможный второй управляющий выход H-моста дросселя; точная функция неизвестна.",
    "Candidate HCAN transmit pin pair with MCU pin 158; verify PFC configuration.": "Кандидат вывода передачи HCAN в паре с выводом MCU 158; требуется проверить конфигурацию PFC.",
    "Candidate HCAN receive pin pair with MCU pin 157; verify PFC configuration.": "Кандидат вывода приёма HCAN в паре с выводом MCU 157; требуется проверить конфигурацию PFC.",
    "Possible K-line SCI1 transmit side through a K-line transceiver, based on similar Nissan ECUs.": "Возможная сторона передачи SCI1 для K-line через K-line трансивер по аналогии с похожими ECM Nissan.",
    "Possible K-line SCI1 receive side through a K-line transceiver, based on similar Nissan ECUs.": "Возможная сторона приёма SCI1 для K-line через K-line трансивер по аналогии с похожими ECM Nissan.",
    "Candidate HCAN receive input paired with an alternate transmit pin; verify PFC configuration.": "Кандидат входа приёма HCAN в паре с альтернативным выводом передачи; требуется проверить конфигурацию PFC.",
    "Possible INJ#1 timing output through an injector driver stage.": "Возможный времязадающий выход INJ#1 через каскад драйвера форсунки.",
    "Possible INJ#2 timing output through an injector driver stage.": "Возможный времязадающий выход INJ#2 через каскад драйвера форсунки.",
    "Possible INJ#3 timing output through an injector driver stage.": "Возможный времязадающий выход INJ#3 через каскад драйвера форсунки.",
    "Possible INJ#4 timing output through an injector driver stage.": "Возможный времязадающий выход INJ#4 через каскад драйвера форсунки.",
    "Possible INJ#5 timing output through an injector driver stage.": "Возможный времязадающий выход INJ#5 через каскад драйвера форсунки.",
    "Possible INJ#6 timing output through an injector driver stage.": "Возможный времязадающий выход INJ#6 через каскад драйвера форсунки.",
    "Candidate HCAN transmit pin for HCAN0 or HCAN1; verify PFC configuration and continuity.": "Кандидат вывода передачи HCAN0 или HCAN1; требуется проверить конфигурацию PFC и прозвонку.",
    "Candidate HCAN receive pin for HCAN0 or HCAN1; verify PFC configuration and continuity.": "Кандидат вывода приёма HCAN0 или HCAN1; требуется проверить конфигурацию PFC и прозвонку."
  });

  const SIGNAL_DESCRIPTIONS_RU = Object.freeze({
    GND: "Земля ECM",
    GNDA: "Сигнальная земля датчика положения распредвала банка 1 и датчика давления ГУР",
    EVAP: "Выход клапана продувки адсорбера EVAP",
    FPR: "Выход управления реле топливного насоса",
    SSOFF: "Выход управления реле ECM (самоотключение)",
    POS: "Сигнал датчика положения коленвала (POS)",
    "AVCC2-POS": "Питание 5 В датчика положения коленвала",
    "GND-POS": "Земля датчика положения коленвала",
    IGNSW: "Вход замка зажигания",
    TW: "Вход датчика температуры охлаждающей жидкости",
    "GNDA-KNK": "Сигнальная земля датчиков детонации",
    TO1: "Вход датчика температуры моторного масла",
    "GNDA-O2_TW_TO": "Сигнальная земля кислородных датчиков и датчиков температуры ОЖ и масла",
    PSPRES: "Вход датчика давления ГУР",
    "GNDA-E-PHS": "Сигнальная земля датчиков положения выпускного распредвала",
    CURSEN: "Вход датчика тока аккумулятора",
    "GND-PHASE#2": "Земля датчика положения распредвала банка 2",
    BATT: "Постоянное питание памяти ECM",
    "GNDA-CURSEN": "Земля датчика тока аккумулятора",
    ASCDSW: "Вход рулевого переключателя ICC или ASCD в зависимости от комплектации",
    FTPRS: "Вход датчика давления системы EVAP",
    PDPRES: "Вход датчика давления хладагента",
    TF: "Вход датчика температуры топлива в баке",
    "GNDA-ASCDSW": "Земля рулевого переключателя ICC или ASCD",
    "NEUT-H [A/T or M/T]": "Вход P/N для A/T или вход нейтрали для M/T",
    TACHO: "Выход сигнала частоты вращения двигателя",
    "AVCC2-FTPRS": "Питание 5 В датчика давления системы EVAP",
    "AVCC2-PDPRES": "Питание 5 В датчика давления хладагента",
    "GNDA-FTPRS": "Земля датчика давления системы EVAP",
    "GNDA-PDPRES": "Земля датчика давления хладагента",
    VHECAN_L1: "Низкая линия высокоскоростной шины CAN автомобиля",
    VHECAN_H1: "Высокая линия высокоскоростной шины CAN автомобиля",
    KLINE: "Двунаправленная диагностическая линия K-line",
    CDCV: "Выход клапана вентиляции адсорбера EVAP",
    BRAKE: "Вход выключателя стоп-сигналов",
    VBR: "Вход питания ECM от зажигания",
    BNCSW: "Вход выключателя тормоза ICC или ASCD в зависимости от комплектации",
    "AVCC1-PHASE#1": "Общее питание 5 В датчиков положения распредвалов банка 1 и датчика давления ГУР",
    "AVCC2-PHASE#2": "Общее питание 5 В датчиков положения распредвалов банка 2 и датчика тока аккумулятора"
  });

  const WIRE_COLORS_RU = Object.freeze({
    B: "чёрный",
    W: "белый",
    R: "красный",
    G: "зелёный",
    L: "синий",
    Y: "жёлтый",
    LG: "светло-зелёный",
    BR: "коричневый",
    O: "оранжевый",
    P: "розовый",
    V: "фиолетовый",
    SB: "голубой",
    GR: "серый",
    SHIELD: "экран"
  });

  const messages = Object.freeze({ en, ru });

  function normalizeLanguage(language) {
    const normalized = String(language || "").trim().toLowerCase().split(/[-_]/)[0];
    return SUPPORTED_LANGUAGES.includes(normalized) ? normalized : DEFAULT_LANGUAGE;
  }

  function translate(language, key, params) {
    const normalized = normalizeLanguage(language);
    const template = messages[normalized][key] ?? en[key] ?? key;
    const values = params && typeof params === "object" ? params : {};
    return template.replace(/\{([A-Za-z0-9_]+)\}/g, (match, name) =>
      Object.hasOwn(values, name) ? String(values[name]) : match
    );
  }

  function localizeReferenceText(language, text) {
    if (normalizeLanguage(language) !== "ru") return String(text || "");
    return REFERENCE_TEXT_RU[text] || String(text || "");
  }

  function localizeCandidateLabel(language, label) {
    if (normalizeLanguage(language) !== "ru") return String(label || "");
    const match = String(label || "").match(/^(.*?)(?: bank (\d))? candidate -> (.*)$/);
    if (!match) return String(label || "");
    let source = match[1];
    if (source === "CAN transceiver") source = "CAN-трансивер";
    if (source === "K-line") source = "K-line";
    if (match[2]) source = `${source}, банк ${match[2]}`;
    const target = match[3].replace(/ pair$/, " (пара)");
    return `${source}: кандидат -> ${target}`;
  }

  function describeEcuSignal(language, signal, fallback) {
    if (normalizeLanguage(language) !== "ru") return String(fallback || "");
    const value = String(signal || "").trim();
    if (!value) return "Сигнал не указан в источнике";
    if (SIGNAL_DESCRIPTIONS_RU[value]) return SIGNAL_DESCRIPTIONS_RU[value];

    let match = value.match(/^AFH(\d)$/);
    if (match) return `Выход нагревателя датчика A/F 1, банк ${match[1]}`;

    match = value.match(/^MOTOR([12])-B([12])$/);
    if (match) {
      const direction = match[1] === "1" ? "открытия" : "закрытия";
      return `Выход двигателя дросселя в направлении ${direction}, банк ${match[2]}`;
    }

    match = value.match(/^VMOT-B([12])$/);
    if (match) return `Питание двигателя дросселя от реле, банк ${match[1]}`;

    match = value.match(/^MOTRLY-B([12])$/);
    if (match) return `Выход управления реле двигателя дросселя, банк ${match[1]}`;

    match = value.match(/^EVTC#([12])$/);
    if (match) return `Выход магнитного замедлителя управления фазами выпуска, банк ${match[1]}`;

    match = value.match(/^CVTC#([12])$/);
    if (match) return `Выход клапана управления фазами впуска, банк ${match[1]}`;

    match = value.match(/^IGN#(\d)$/);
    if (match) return `Выход сигнала зажигания No. ${match[1]}`;

    match = value.match(/^INJ#(\d)$/);
    if (match) return `Выход управления форсункой No. ${match[1]}`;

    match = value.match(/^O2HR([12])$/);
    if (match) return `Выход нагревателя подогреваемого кислородного датчика 2, банк ${match[1]}`;

    match = value.match(/^TPS([12])-B([12])$/);
    if (match) return `Вход датчика положения дросселя ${match[1]}, банк ${match[2]}`;

    match = value.match(/^GNDA-TPS-B([12])$/);
    if (match) return `Земля датчиков положения дросселя, банк ${match[1]}`;

    match = value.match(/^AVCC\d-TPS-B([12])$/);
    if (match) return `Питание 5 В датчиков положения дросселя, банк ${match[1]}`;

    match = value.match(/^AF([+-])([12])$/);
    if (match) return `Вход сигнала ${match[1]} датчика A/F 1, банк ${match[2]}`;

    match = value.match(/^E-PHASE#([12])$/);
    if (match) return `Вход датчика положения выпускного распредвала, банк ${match[1]}`;

    match = value.match(/^PHASE#([12])$/);
    if (match) return `Вход датчика положения распредвала (PHASE), банк ${match[1]}`;

    match = value.match(/^AVCC\d-PHASE#([12])$/);
    if (match) return `Питание 5 В датчика положения распредвала, банк ${match[1]}`;

    match = value.match(/^TA\+?([12])$/);
    if (match) return `Вход датчика температуры воздуха, банк ${match[1]}`;

    match = value.match(/^GNDA-QA([12])_TA[12]$/);
    if (match) return `Земля датчиков расхода и температуры воздуха, банк ${match[1]}`;

    match = value.match(/^KNK([12])$/);
    if (match) return `Вход датчика детонации, банк ${match[1]}`;

    match = value.match(/^O2SR([12])$/);
    if (match) return `Вход сигнала подогреваемого кислородного датчика 2, банк ${match[1]}`;

    match = value.match(/^QA([12])\+$/);
    if (match) return `Вход датчика массового расхода воздуха, банк ${match[1]}`;

    match = value.match(/^APS([12])$/);
    if (match) return `Вход датчика положения педали акселератора ${match[1]}`;

    match = value.match(/^AVCC\d-APS([12])$/);
    if (match) return `Питание 5 В датчика положения педали акселератора ${match[1]}`;

    match = value.match(/^GNDA-APS([12])$/);
    if (match) return `Земля датчика положения педали акселератора ${match[1]}`;

    return String(fallback || value);
  }

  function describeWireColor(language, code, fallback) {
    if (normalizeLanguage(language) !== "ru") return String(fallback || "");
    const value = String(code || "").trim();
    if (!value) return translate("ru", "common.unknown");
    if (WIRE_COLORS_RU[value]) return WIRE_COLORS_RU[value];
    if (value.includes("/")) {
      return value.split("/").map(part => WIRE_COLORS_RU[part] || part).join(" / ");
    }
    return String(fallback || value);
  }

  function localizeValidationError(language, message) {
    const value = String(message || "");
    if (normalizeLanguage(language) !== "ru") return value;
    if (value === "Unsupported or invalid pin-tracer JSON.") {
      return "Неподдерживаемый или некорректный JSON pin-tracer.";
    }
    let match = value.match(/^Invalid connection at item (\d+)\.$/);
    if (match) return `Некорректная связь в элементе ${match[1]}.`;
    match = value.match(/^Invalid ECM terminal: (.+)$/);
    if (match) return `Некорректный контакт ECM: ${match[1]}`;
    match = value.match(/^Invalid MCU pin: (.+)$/);
    if (match) return `Некорректный вывод MCU: ${match[1]}`;
    match = value.match(/^Duplicate or empty connection identifier at item (\d+)\.$/);
    if (match) return `Повторяющийся или пустой идентификатор связи в элементе ${match[1]}.`;
    match = value.match(/^Duplicate ECM\/MCU endpoint pair at item (\d+)\.$/);
    if (match) return `Повторяющаяся пара ECM/MCU в элементе ${match[1]}.`;
    match = value.match(/^Missing component path at item (\d+)\.$/);
    if (match) return `Не указан маршрут компонентов в элементе ${match[1]}.`;
    return translate("ru", "alert.importFailed");
  }

  return Object.freeze({
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    messages,
    normalizeLanguage,
    translate,
    localizeReferenceText,
    localizeCandidateLabel,
    describeEcuSignal,
    describeWireColor,
    localizeValidationError
  });
});
