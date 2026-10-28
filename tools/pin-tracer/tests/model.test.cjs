"use strict";

const assert = require("node:assert/strict");
const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const model = require("../model.js");

const SCHEMA = "vq-hr-ecu-pin-tracer/v1";
const topologyProfiles = {
  unknown: {},
  ignition: {},
  injector: {},
  analog: {},
  can: {}
};
const validationOptions = {
  schema: SCHEMA,
  topologyProfiles,
  createId: () => "generated-id"
};

function connection(overrides = {}) {
  return {
    id: "link-1",
    ecuPin: 20,
    mcuPin: 1,
    topology: "ignition",
    route: "ECM terminal -> buffer -> MCU pin",
    comment: "Q1",
    createdAt: "2026-07-28T00:00:00.000Z",
    updatedAt: "2026-07-28T00:00:00.000Z",
    ...overrides
  };
}

function payload(connections, preferences) {
  return {
    schema: SCHEMA,
    sources: { ...model.SOURCE_BINDINGS },
    connections,
    ...(preferences ? { preferences } : {})
  };
}

test("classifies representative MCU pin functions", () => {
  const cases = [
    ["AN8", "analog"],
    ["PD8/PULS0", "timer"],
    ["PB10/TxD4/HTxD0/TO8G", "timer"],
    ["PG1/IRQ1", "interrupt"],
    ["PE0/A0", "bus"],
    ["PK0", "gpio"],
    ["NMI", "system"],
    ["WDTOVF", "system"],
    ["Vcc", "system"]
  ];
  for (const [name, expected] of cases) {
    assert.equal(model.classifyMcuPin(name), expected, name);
  }
  assert.equal(model.isDefaultSelectable("analog"), true);
  assert.equal(model.isDefaultSelectable("system"), false);
  assert.equal(model.isDefaultSelectable("bus"), false);
  assert.deepEqual(
    model.mcuPinCategories("PD13/PULS6/HTxD0/HTxD1"),
    ["timer", "communication", "gpio"]
  );
  assert.deepEqual(
    model.mcuPinCategories("PB10/TxD4/HTxD0/TO8G"),
    ["timer", "communication", "gpio"]
  );
  assert.deepEqual(model.mcuPinCategories("PF14/BACK"), ["bus"]);
  assert.equal(model.mcuPinMatchesCategory("PD13/PULS6/HTxD0/HTxD1", "timer"), true);
  assert.equal(model.mcuPinMatchesCategory("PD13/PULS6/HTxD0/HTxD1", "communication"), true);
  assert.equal(model.isDefaultSelectable(["system", "analog"]), true);
});

test("toggles a selected ECM terminal or MCU pin on repeated clicks", () => {
  assert.equal(model.togglePinSelection(null, 20), 20);
  assert.equal(model.togglePinSelection(20, 20), null);
  assert.equal(model.togglePinSelection(20, 16), 16);
  assert.equal(model.togglePinSelection(null, 195), 195);
  assert.equal(model.togglePinSelection(195, 195), null);
});

test("assigns wider columns to the three wide-terminal groups shown in the source", () => {
  assert.deepEqual(
    model.connectorColumnKinds(1, 12, [1, 8]),
    [...Array(10).fill("standard"), "power", "power"]
  );
  assert.deepEqual(
    model.connectorColumnKinds(49, 12, [49, 56]),
    [...Array(10).fill("standard"), "power", "power"]
  );
  assert.deepEqual(
    model.connectorColumnKinds(97, 8, [121, 128]),
    ["power", "power", ...Array(6).fill("standard")]
  );
});

test("classifies ECM signals across every supported topology family", () => {
  const cases = [
    ["GNDA-TPS-B1", "ground"],
    ["E-PHASE#1", "timer"],
    ["BATT", "power"],
    ["INJ#3", "injector"],
    ["IGN#5", "ignition"],
    ["MOTOR1-B1", "hbridge"],
    ["VHECAN_H1", "can"],
    ["KLINE", "kline"],
    ["KNK1", "knock"],
    ["AF+1", "airFuel"],
    ["O2SR1", "oxygen"],
    ["QA1+", "analog"],
    ["AFH1", "lowSide"],
    ["POS", "timer"],
    ["APS1", "analog"],
    ["FTPRS", "analog"],
    ["CVTC#1", "lowSide"],
    ["MOTRLY-B1", "lowSide"],
    ["SSOFF", "lowSide"],
    ["CDCV", "lowSide"],
    ["TACHO", "logicOutput"],
    ["BRAKE", "switch"],
    ["", "unknown"]
  ];
  for (const [signal, expected] of cases) {
    assert.equal(model.classifyEcuSignal(signal), expected, signal);
  }
});

test("expands factory ECM signal labels into readable descriptions", () => {
  const cases = [
    ["SSOFF", "ECM relay control output (self shut-off)"],
    ["CDCV", "EVAP canister vent control valve output"],
    ["BNCSW", "ICC or ASCD brake switch input, depending on vehicle equipment"],
    ["MOTOR1-B2", "Throttle control motor open output, bank 2"],
    ["IGN#5", "Ignition signal No. 5 output"],
    ["E-PHASE#1", "Exhaust valve timing control position sensor input, bank 1"],
    ["EVTC#2", "Exhaust valve timing control magnet retarder output, bank 2"],
    ["TO1", "Engine oil temperature sensor input"],
    ["VHECAN_H1", "Vehicle high-speed CAN bus high"],
    ["AVCC1-PHASE#1", "Shared 5 V supply for camshaft and exhaust valve timing position sensors bank 1, and power steering pressure sensor"],
    ["NEUT-H [A/T or M/T]", "Park/neutral position switch input for A/T, or neutral switch input for M/T"]
  ];
  for (const [signal, expected] of cases) {
    assert.equal(model.describeEcuSignal(signal), expected, signal);
  }
  assert.equal(model.describeEcuSignal(""), "No signal listed in source");
  assert.match(model.describeEcuSignal("FUTURE"), /exact function not expanded/);
  assert.equal(model.describeWireColor("BR"), "brown");
  assert.equal(model.describeWireColor("G/BR"), "green / brown");
  assert.equal(model.describeWireColor(""), "unknown");
});

test("builds generic suggestions from the classified ECM signal", () => {
  assert.deepEqual(model.genericSuggestionForSignal("INJ#1"), {
    categories: ["timer", "gpio"],
    category: "timer",
    label: "ATU-II one-shot or GPIO output behind an injector driver",
    topology: "injector"
  });
  assert.equal(model.genericSuggestionForSignal("VHECAN_L1").category, "communication");
  assert.equal(model.genericSuggestionForSignal("GNDA").category, "system");
  assert.deepEqual(
    model.genericSuggestionForSignal("KNK1").categories,
    ["analog", "communication"]
  );
  assert.deepEqual(
    model.genericSuggestionForSignal("ASCDSW").categories,
    ["gpio", "interrupt", "analog"]
  );
});

test("matches ECM candidates when tracing from an MCU pin", () => {
  assert.equal(model.ecuSignalMatchesMcuPin("APS1", "AN8"), true);
  assert.equal(model.ecuSignalMatchesMcuPin("IGN#1", "PD8/PULS0"), true);
  assert.equal(
    model.ecuSignalMatchesMcuPin("VHECAN_L1", "PD13/PULS6/HTxD0/HTxD1"),
    true
  );
  assert.equal(model.ecuSignalMatchesMcuPin("BATT", "Vcc"), true);
  assert.equal(model.ecuSignalMatchesMcuPin("APS1", "PD8/PULS0"), false);
  assert.equal(model.ecuSignalMatchesMcuPin("", "AN8"), false);
});

test("normalizes optional workspace preferences", () => {
  assert.deepEqual(model.normalizePreferences(), {
    advancedPins: false,
    showSavedLines: false,
    language: "en"
  });
  assert.deepEqual(model.normalizePreferences({
    advancedPins: true,
    showSavedLines: true,
    language: "ru-RU",
    ignored: true
  }), {
    advancedPins: true,
    showSavedLines: true,
    language: "ru"
  });
  assert.deepEqual(model.normalizePreferences({
    advancedPins: 1,
    showSavedLines: "yes",
    language: "de"
  }), {
    advancedPins: false,
    showSavedLines: false,
    language: "en"
  });
});

test("validates and normalizes a complete workspace payload", () => {
  const result = model.validatePayload(payload([
    connection({
      route: "  ECM terminal -> Q1 -> MCU pin  ",
      comment: "  measured  "
    })
  ], {
    advancedPins: true,
    showSavedLines: true,
    language: "ru"
  }), validationOptions);

  assert.deepEqual(result.preferences, {
    advancedPins: true,
    showSavedLines: true,
    language: "ru"
  });
  assert.equal(result.connections[0].route, "ECM terminal -> Q1 -> MCU pin");
  assert.equal(result.connections[0].comment, "measured");
  assert.equal(result.connections[0].topology, "ignition");
  assert.equal(Object.hasOwn(result.connections[0], "status"), false);
});

test("accepts the source-bound browser import fixture and removes evidence statuses", () => {
  const fixturePath = path.join(__dirname, "fixtures", "import-workspace.json");
  const fixture = JSON.parse(fs.readFileSync(fixturePath, "utf8"));
  const result = model.validatePayload(fixture, validationOptions);

  assert.equal(result.connections.length, 2);
  assert.deepEqual(result.preferences, {
    advancedPins: true,
    showSavedLines: true,
    language: "en"
  });
  assert.deepEqual(
    result.connections.map(item => [item.ecuPin, item.mcuPin]),
    [
      [20, 1],
      [89, 195]
    ]
  );
  assert.equal(result.connections.every(item => !Object.hasOwn(item, "status")), true);
});

test("ignores obsolete or unknown evidence statuses during import", () => {
  const result = model.validatePayload(payload([
    connection({ status: "future-value" })
  ]), validationOptions);
  assert.equal(Object.hasOwn(result.connections[0], "status"), false);
});

test("generates an identifier and normalizes an unknown topology", () => {
  const result = model.validatePayload(payload([
    connection({ id: "", topology: "future-topology" })
  ]), validationOptions);
  assert.equal(result.connections[0].id, "generated-id");
  assert.equal(result.connections[0].topology, "unknown");
});

test("rejects malformed workspace data and broken connection invariants", () => {
  const cases = [
    [null, /Unsupported or invalid/],
    [{ schema: "wrong", connections: [] }, /Unsupported or invalid/],
    [payload([null]), /Invalid connection/],
    [payload([connection({ ecuPin: 0 })]), /Invalid ECM terminal/],
    [payload([connection({ ecuPin: 129 })]), /Invalid ECM terminal/],
    [payload([connection({ mcuPin: 0 })]), /Invalid MCU pin/],
    [payload([connection({ mcuPin: 257 })]), /Invalid MCU pin/],
    [payload([connection({ route: "  " })]), /Missing component path/],
    [payload([
      connection(),
      connection({ ecuPin: 16, mcuPin: 2 })
    ]), /Duplicate or empty connection identifier/],
    [payload([
      connection(),
      connection({ id: "link-2" })
    ]), /Duplicate ECM\/MCU endpoint pair/]
  ];
  for (const [value, pattern] of cases) {
    assert.throws(() => model.validatePayload(value, validationOptions), pattern);
  }
});

test("finds duplicate endpoint pairs while excluding an edited record", () => {
  const connections = [
    connection(),
    connection({ id: "link-2", ecuPin: 16, mcuPin: 2 })
  ];
  assert.equal(
    model.findDuplicateConnection(connections, connection({ id: "new-id" })).id,
    "link-1"
  );
  assert.equal(model.findDuplicateConnection(connections, connection()), null);
  assert.equal(
    model.findDuplicateConnection(connections, connection({
      id: "new-id",
      ecuPin: 99,
      mcuPin: 99
    })),
    null
  );
});

test("calculates traced-pair count and unique ECM coverage", () => {
  const connections = [
    connection({ id: "a" }),
    connection({ id: "b", mcuPin: 2 }),
    connection({ id: "c", ecuPin: 16, mcuPin: 3 })
  ];
  assert.deepEqual(model.calculateStats(connections, 100), {
    connections: 3,
    coverage: 2
  });
  assert.equal(model.calculateStats(connections, 0).coverage, 0);
});

test("formats export filenames with the local calendar date", () => {
  assert.equal(model.formatLocalDate(new Date(2026, 6, 8, 1, 2, 3)), "2026-07-08");
  assert.throws(() => model.formatLocalDate("not-a-date"), /Invalid date/);
});

test("escapes imported text before HTML interpolation", () => {
  assert.equal(
    model.escapeHtml(`<img src=x onerror="alert('x')">&`),
    "&lt;img src=x onerror=&quot;alert(&#039;x&#039;)&quot;&gt;&amp;"
  );
});

test("the HTML data set covers every connector and MCU package position", () => {
  const htmlPath = path.join(__dirname, "..", "index.html");
  const html = fs.readFileSync(htmlPath, "utf8");
  const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)]
    .map(match => match[1]);
  const script = scripts.find(value => value.includes("const connectorDefinitions"));
  assert.ok(script, "inline application script must exist");
  assert.doesNotThrow(() => new vm.Script(script));

  const context = {};
  let block = script
    .slice(script.indexOf("const connectorDefinitions"), script.indexOf("const ecuSignals"))
    .replace("const connectorDefinitions", "var connectorDefinitions");
  vm.runInNewContext(`${block};globalThis.connectors=connectorDefinitions`, context);

  block = script
    .slice(script.indexOf("const ecuSignals"), script.indexOf("const sourcePinNotes"))
    .replace("const ecuSignals", "var ecuSignals");
  vm.runInNewContext(`${block};globalThis.ecuSignalsOut=ecuSignals`, context);

  block = script
    .slice(script.indexOf("const serviceDirections"), script.indexOf("const mcuNames"))
    .replace("const serviceDirections", "var serviceDirections");
  vm.runInNewContext(
    `${block};globalThis.serviceDirectionsOut=serviceDirections`,
    context
  );

  block = script
    .slice(script.indexOf("const mcuNames"), script.indexOf("const mcuHypotheses"))
    .replace("const mcuNames", "var mcuNames");
  vm.runInNewContext(`${block};globalThis.mcuNamesOut=mcuNames`, context);

  block = script
    .slice(script.indexOf("const topologyProfiles"), script.indexOf("const state"))
    .replace("const topologyProfiles", "var topologyProfiles")
    .replace("const suggestionEvidence", "var suggestionEvidence")
    .replace("const exactSuggestions", "var exactSuggestions");
  vm.runInNewContext(
    `${block};globalThis.topologiesOut=topologyProfiles;globalThis.evidenceOut=suggestionEvidence;globalThis.exactOut=exactSuggestions`,
    context
  );

  const connectorPins = context.connectors.flatMap(connector =>
    Array.from(
      { length: connector.rangeEnd - connector.rangeStart + 1 },
      (_, index) => connector.rangeStart + index
    )
  );
  assert.equal(connectorPins.length, 128);
  assert.equal(new Set(connectorPins).size, 128);
  assert.equal(Math.min(...connectorPins), 1);
  assert.equal(Math.max(...connectorPins), 128);
  assert.equal(Object.keys(context.ecuSignalsOut).length, 102);
  assert.deepEqual(
    Object.keys(context.serviceDirectionsOut).sort((a, b) => Number(a) - Number(b)),
    Object.keys(context.ecuSignalsOut).sort((a, b) => Number(a) - Number(b))
  );
  assert.deepEqual(
    Object.values(context.serviceDirectionsOut).reduce((counts, direction) => {
      counts[direction] = (counts[direction] || 0) + 1;
      return counts;
    }, {}),
    {
      output: 30,
      input: 38,
      bidirectional: 3,
      reference: 30,
      manualConflict: 1
    }
  );
  for (const [, signal] of Object.values(context.ecuSignalsOut)) {
    assert.doesNotMatch(
      model.describeEcuSignal(signal),
      /exact function not expanded/,
      signal
    );
    assert.notEqual(
      model.classifyEcuSignal(signal),
      "unknown",
      `${signal} must have an explicit topology classification`
    );
  }
  assert.deepEqual(
    Array.from(context.connectors, connector => Array.from(connector.wideTerminalRange)),
    [[1, 8], [49, 56], [121, 128]]
  );

  const mcuNames = context.mcuNamesOut;
  assert.equal(mcuNames.length, 257);
  assert.equal(mcuNames.slice(1).includes("Unassigned"), false);
  const categories = mcuNames.slice(1).map(model.mcuPinCategories);
  assert.equal(categories.filter(model.isDefaultSelectable).length, 133);
  assert.equal(categories.filter(category => !model.isDefaultSelectable(category)).length, 123);
  assert.equal(mcuNames[45], "PF14/BACK");
  assert.equal(mcuNames[143], "PA14/TxD0");
  assert.equal(mcuNames[164], "PB15/PULS5/SCK2");
  assert.equal(mcuNames[223], "PL7/SCK2");
  assert.equal(mcuNames[228], "PL10/HTxD0/HTxD1/HTxD0&HTxD1");
  assert.equal(mcuNames[229], "PL11/HRxD0/HRxD1/HRxD0&HRxD1");
  assert.equal(
    mcuNames.slice(1).some(name => /(?:^|\/)(?:SSO|SSI|SSCK|SCS)\d/.test(name)),
    false,
    "SH7058 must not inherit SH7058S-only SSU functions"
  );

  for (const [ecuPin, suggestions] of Object.entries(context.exactOut)) {
    assert.ok(context.ecuSignalsOut[ecuPin], `suggested ECM terminal ${ecuPin} must be named`);
    for (const suggestion of suggestions) {
      assert.ok(context.topologiesOut[suggestion.topology], suggestion.topology);
      assert.ok(context.evidenceOut[suggestion.evidence], suggestion.evidence);
      assert.equal(Object.hasOwn(suggestion, "confidence"), false);
      const expectedCategories = {
        analog: ["analog"],
        timer: ["timer", "gpio"],
        ignition: ["timer", "gpio"],
        injector: ["timer", "gpio"],
        can: ["communication"],
        kline: ["communication"]
      }[suggestion.topology];
      assert.ok(expectedCategories, `category rule for ${suggestion.topology}`);
      for (const target of suggestion.targets) {
        assert.ok(target >= 1 && target <= 256, `MCU target ${target}`);
        assert.notEqual(mcuNames[target], "Unassigned");
        assert.equal(
          model.mcuPinCategories(mcuNames[target])
            .some(category => expectedCategories.includes(category)),
          true,
          `MCU ${target} cannot implement ${suggestion.topology}`
        );
      }
    }
  }

  assert.match(html, /id="showSavedLines"/);
  assert.match(html, /src="\.\/model\.js"/);
  assert.match(html, /src="\.\/i18n\.js"/);
  assert.match(html, /data-language="en"/);
  assert.match(html, /data-language="ru"/);
  assert.match(html, /button\.title =/);
  assert.match(html, /const localizedSignalDescription = signalDescription/);
  assert.match(html, /wireColorDescription\(signalData\[0\]\)/);
  assert.match(html, /selection-function.*signalDescription\(pin\.signal\)/);
  assert.match(html, /button\.dataset\.terminalSize =/);
  assert.ok(
    html.indexOf(".ecu-pin.selected") > html.indexOf(".ecu-pin.used"),
    "ECM selected styling must override the regular used-pin styling"
  );
  assert.match(html, /t\("inspector\.genericCandidates"/);
  assert.match(html, /t\("inspector\.compatibleEcu"\)/);
  assert.match(html, /id="useRouteTemplateButton"/);
  assert.match(html, /routeTextarea\.value = template/);
  assert.match(html, /t\("inspector\.possibleTopology"\)/);
  assert.match(html, /t\("form\.observedPath"\)/);
  assert.match(html, /t\("template\.possible"/);
  assert.match(html, /language:\s*state\.language/);
  assert.equal(model.SOURCE_BINDINGS.serviceManualSha256,
    "f34ae5e56df11de9e069b3dcd637d4fc509321ce8ac3f7eb0dfc3293e3ac55fc");
  assert.match(html, /Neither connector terminal maps one-to-one to an MCU TX or RX pin/);
  assert.match(html, /Ground is a shared return network, not a one-to-one signal connection/);
  assert.match(
    html,
    /!state\.advancedPins[\s\S]*state\.selectedMcu[\s\S]*!isDefaultSelectable[\s\S]*state\.selectedMcu = null/
  );
  assert.doesNotMatch(html, /Likely topology|Observed or expected component path/);
  assert.doesNotMatch(html, /applyTopologyDefault/);
  assert.doesNotMatch(html, /confidence:\s*"(?:high|medium|low)"/);
  assert.doesNotMatch(html, /id="highlightGeneric"/);
  assert.doesNotMatch(html, /id="connectionStatus"|<th>Status<\/th>|id="statConfirmed"/);

  const digest = value => crypto.createHash("sha256").update(value).digest("hex");
  const ecuReference = Object.entries(context.ecuSignalsOut)
    .sort(([left], [right]) => Number(left) - Number(right))
    .map(([pin, [wire, signal]]) => `${pin}|${wire}|${signal}`)
    .join("\n");
  const mcuReference = mcuNames.slice(1)
    .map((name, index) => `${index + 1}|${name}`)
    .join("\n");
  assert.equal(
    digest(ecuReference),
    "a437ff437d74878ead8aa7a2efef0d21bc8ebc36a7decdbcbeffcaff8e8f5979",
    "audited ECM pin transcription changed"
  );
  assert.equal(
    digest(mcuReference),
    "05afea9c78bc55c01c955fd93789a7efad9860d715cb6d238616dfce80ab9914",
    "audited SH7058 FP-256H pin transcription changed"
  );
});
