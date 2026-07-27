"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const i18n = require("../i18n.js");
const model = require("../model.js");

const htmlPath = path.join(__dirname, "..", "index.html");
const html = fs.readFileSync(htmlPath, "utf8");
const inlineScript = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)]
  .map(match => match[1])
  .find(value => value.includes("const connectorDefinitions"));

function readInlineObject(startMarker, endMarker, variableName) {
  const context = {};
  const source = inlineScript
    .slice(inlineScript.indexOf(startMarker), inlineScript.indexOf(endMarker))
    .replace(startMarker, `var ${variableName}`);
  vm.runInNewContext(`${source};globalThis.result=${variableName}`, context);
  return context.result;
}

test("keeps complete RU and EN message catalogs", () => {
  const englishKeys = Object.keys(i18n.messages.en).sort();
  const russianKeys = Object.keys(i18n.messages.ru).sort();
  assert.deepEqual(russianKeys, englishKeys);

  const staticKeys = [...html.matchAll(/data-i18n(?:-(?:aria-label|title))?="([^"]+)"/g)]
    .map(match => match[1]);
  const literalDynamicKeys = [...html.matchAll(/\bt\("([^"]+)"/g)]
    .map(match => match[1])
    .filter(key => !key.includes("${"));
  for (const key of new Set([...staticKeys, ...literalDynamicKeys])) {
    assert.ok(i18n.messages.en[key], `missing EN message ${key}`);
    assert.ok(i18n.messages.ru[key], `missing RU message ${key}`);
  }

  for (const key of [
    "legend.analog",
    "legend.timer",
    "legend.communication",
    "legend.interrupt",
    "legend.gpio",
    "legend.bus",
    "legend.wide"
  ]) {
    assert.equal(i18n.messages.ru[key], i18n.messages.en[key], key);
  }
});

test("keeps the localized subtitle on one ellipsized line", () => {
  assert.match(
    html,
    /class="subtitle"[^>]*data-i18n-title="app\.subtitle"/
  );
  assert.match(
    html,
    /\.subtitle\s*\{[\s\S]*?overflow:\s*hidden;[\s\S]*?text-overflow:\s*ellipsis;[\s\S]*?white-space:\s*nowrap;/
  );
});

test("normalizes locale names and interpolates translated messages", () => {
  assert.equal(i18n.normalizeLanguage("ru-RU"), "ru");
  assert.equal(i18n.normalizeLanguage("EN_us"), "en");
  assert.equal(i18n.normalizeLanguage("de-DE"), "en");
  assert.equal(
    i18n.translate("ru", "confirm.deleteConnection", { ecuPin: 20, mcuPin: 1 }),
    "Удалить связь ECM 20 -> MCU 1?"
  );
  assert.equal(
    i18n.translate("en", "action.selectPin", { pin: 195 }),
    "Select 195"
  );
});

test("localizes every populated ECM signal description and wire color", () => {
  const ecuSignals = readInlineObject(
    "const ecuSignals",
    "const sourcePinNotes",
    "ecuSignals"
  );
  for (const [, signal] of Object.values(ecuSignals)) {
    const english = model.describeEcuSignal(signal);
    const russian = i18n.describeEcuSignal("ru", signal, english);
    assert.notEqual(russian, english, signal);
    assert.match(russian, /[А-Яа-яЁё]/, signal);
    assert.equal(i18n.describeEcuSignal("en", signal, english), english);
  }

  assert.equal(i18n.describeWireColor("ru", "BR", "brown"), "коричневый");
  assert.equal(
    i18n.describeWireColor("ru", "G/BR", "green / brown"),
    "зелёный / коричневый"
  );
  assert.equal(i18n.describeWireColor("en", "BR", "brown"), "brown");
});

test("localizes all source notes and seeded MCU hypotheses", () => {
  const sourcePinNotes = readInlineObject(
    "const sourcePinNotes",
    "const serviceDirections",
    "sourcePinNotes"
  );
  const mcuHypotheses = readInlineObject(
    "const mcuHypotheses",
    "const topologyProfiles",
    "mcuHypotheses"
  );
  const texts = [
    ...Object.values(sourcePinNotes),
    ...Object.values(mcuHypotheses).flat()
  ];
  for (const text of texts) {
    const russian = i18n.localizeReferenceText("ru", text);
    assert.notEqual(russian, text, text);
    assert.match(russian, /[А-Яа-яЁё]/, text);
    assert.equal(i18n.localizeReferenceText("en", text), text);
  }
});

test("covers every topology and evidence family in both languages", () => {
  const topologyFields = {
    unknown: ["label", "route"],
    direct: ["label", "route"],
    analog: ["label", "route"],
    timer: ["label", "route"],
    switch: ["label", "route"],
    lowSide: ["label", "route"],
    logicOutput: ["label", "route"],
    injector: ["label", "route"],
    ignition: ["label", "route"],
    hbridge: ["label", "route"],
    can: ["label", "route", "endpoint"],
    kline: ["label", "route", "endpoint"],
    knock: ["label", "route"],
    airFuel: ["label", "route"],
    oxygen: ["label", "route"],
    power: ["label", "route", "endpoint"],
    ground: ["label", "route", "endpoint"],
    customAsic: ["label", "route", "endpoint"]
  };
  for (const [topology, fields] of Object.entries(topologyFields)) {
    for (const field of fields) {
      const key = `topology.${topology}.${field}`;
      assert.ok(i18n.messages.en[key], key);
      assert.ok(i18n.messages.ru[key], key);
      assert.match(i18n.messages.ru[key], /[А-Яа-яЁё]/, key);
    }
  }

  for (const evidence of ["firmwareCrossModel", "crossModel", "muxOnly"]) {
    for (const field of ["label", "explanation"]) {
      const key = `evidence.${evidence}.${field}`;
      assert.ok(i18n.messages.en[key], key);
      assert.ok(i18n.messages.ru[key], key);
    }
  }
});

test("localizes candidate labels and import validation errors", () => {
  assert.equal(
    i18n.localizeCandidateLabel("ru", "TPS1 bank 1 candidate -> AN22"),
    "TPS1, банк 1: кандидат -> AN22"
  );
  assert.equal(
    i18n.localizeCandidateLabel("ru", "CAN transceiver candidate -> PL10/PL11 HCAN pair"),
    "CAN-трансивер: кандидат -> PL10/PL11 HCAN (пара)"
  );
  assert.equal(
    i18n.localizeValidationError("ru", "Missing component path at item 2."),
    "Не указан маршрут компонентов в элементе 2."
  );
  assert.equal(
    i18n.localizeValidationError("en", "Missing component path at item 2."),
    "Missing component path at item 2."
  );
  assert.equal(
    i18n.localizeValidationError("ru", "Unexpected token at position 4"),
    "Не удалось импортировать выбранный JSON-файл."
  );
});
