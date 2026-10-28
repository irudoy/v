"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");
const model = require("../model.js");
const i18n = require("../i18n.js");

const STORAGE_KEY = "vq-hr-ecu-pin-tracer-v1";
const LANGUAGE_STORAGE_KEY = "vq-hr-ecu-pin-tracer-language";
const fixture = JSON.parse(fs.readFileSync(
  path.join(__dirname, "fixtures", "import-workspace.json"), "utf8"
));
const html = fs.readFileSync(path.join(__dirname, "..", "index.html"), "utf8");

function section(start, end) {
  const first = html.indexOf(start);
  const last = html.indexOf(end, first);
  assert.ok(first >= 0 && last > first, `${start} must precede ${end}`);
  return html.slice(first, last);
}

function browser(raw) {
  const values = new Map([[STORAGE_KEY, raw]]);
  const writes = [], handlers = {}, alerts = [], confirmations = [], downloads = [];
  const checkbox = name => ({ checked: false, addEventListener: (_event, fn) => { handlers[name] = fn; } });
  const refs = {
    storageState: {}, languageButtons: [], importFile: { value: "" },
    advancedPins: checkbox("advancedPins"), showSavedLines: checkbox("showSavedLines")
  };
  const context = {
    STORAGE_KEY, LANGUAGE_STORAGE_KEY, SCHEMA: fixture.schema, SOURCE_BINDINGS: model.SOURCE_BINDINGS,
    initialLanguage: "en", refs, confirmResult: false, Blob,
    normalizeLanguage: i18n.normalizeLanguage, translate: i18n.translate,
    localizeValidationError: i18n.localizeValidationError,
    validateModelPayload: model.validatePayload,
    formatLocalDate: model.formatLocalDate,
    topologyProfiles: { unknown: {}, ignition: {}, injector: {} }, createId: () => "test-id",
    findDuplicateConnection: model.findDuplicateConnection,
    isDefaultSelectable: model.isDefaultSelectable, mcuPinCategories: model.mcuPinCategories,
    console: { error() {} },
    renderConnectors() {}, renderMcuPins() {}, renderAllDynamic() {}, clearSelection() {},
    drawConnections() {}, requestAnimationFrame(fn) { fn(); },
    localStorage: {
      getItem: key => values.has(key) ? values.get(key) : null,
      setItem(key, value) { writes.push(key); values.set(key, String(value)); },
      removeItem: key => values.delete(key)
    },
    window: {
      alert: text => alerts.push(text),
      confirm: text => { confirmations.push(text); return context.confirmResult; },
      setTimeout: fn => fn()
    },
    document: {
      documentElement: {}, querySelector: () => null, querySelectorAll: () => [],
      body: { appendChild() {} },
      createElement: () => ({ click() {}, remove() {} })
    },
    URL: { createObjectURL: blob => { downloads.push(blob); return "blob:fixture"; }, revokeObjectURL() {} }
  };
  vm.runInNewContext([
    section("const state =", "const refs =").replace("const state =", "var state ="),
    section("function t(", "function signalDescription("),
    section("function applyStaticTranslations(", "function connectorForPin("),
    section("function saveConnection(", "function renderConnectionTable("),
    section("function renderStorageStatus(", "function topologyOptions("),
    section('refs.advancedPins.addEventListener("change"', "refs.languageButtons.forEach")
  ].join("\n"), context);
  return { context, values, writes, handlers, refs, alerts, confirmations, downloads };
}

test("requires every source SHA-256 and reports missing or foreign bindings", () => {
  for (const key of Object.keys(model.SOURCE_BINDINGS)) {
    for (const actual of [undefined, "0".repeat(64), "invalid"]) {
      const payload = structuredClone(fixture);
      if (actual === undefined) delete payload.sources[key];
      else payload.sources[key] = actual;
      assert.throws(() => model.validatePayload(payload, { schema: fixture.schema }), error => {
        assert.match(error.message, /Source SHA-256/);
        assert.ok(error.message.includes(key));
        assert.ok(error.message.includes(model.SOURCE_BINDINGS[key]));
        assert.ok(error.message.includes(actual ?? "<missing>"));
        assert.equal(i18n.localizeValidationError("ru", error.message), error.message);
        return true;
      });
    }
  }
  const missing = structuredClone(fixture);
  delete missing.sources;
  assert.throws(() => model.validatePayload(missing, { schema: fixture.schema }), /<missing>/);
});

test("failed stored workspaces survive language and both checkbox changes", () => {
  const foreign = structuredClone(fixture);
  foreign.sources.ecuPinoutSha256 = "0".repeat(64);
  for (const raw of ["", "{broken JSON", JSON.stringify(foreign)]) {
    const page = browser(raw);
    page.context.restore();
    assert.equal(page.context.state.restoreFailure.raw, raw);
    page.context.setLanguage("ru");
    for (const name of ["advancedPins", "showSavedLines"]) {
      page.refs[name].checked = true;
      page.handlers[name]();
    }
    assert.equal(page.values.get(STORAGE_KEY), raw);
    assert.equal(page.writes.includes(STORAGE_KEY), false);
    assert.equal(page.values.get(LANGUAGE_STORAGE_KEY), "ru");
    assert.equal(page.context.state.storageStatus, "storage.loadError");
    assert.ok(page.refs.storageState.textContent.includes(page.context.state.restoreFailure.message));
    page.context.saveConnection({ route: "new trace" });
    assert.equal(page.context.state.connections.length, 0);
    assert.equal(page.values.get(STORAGE_KEY), raw);
  }
});

test("exports an unrestored payload verbatim without replacing it", async () => {
  const raw = "{ original broken record\n";
  const page = browser(raw);
  page.context.restore();
  page.context.exportJson();
  assert.equal(await page.downloads[0].text(), raw);
  assert.equal(page.values.get(STORAGE_KEY), raw);
});

test("a source-bound stored workspace restores and persists its connections", () => {
  const page = browser(JSON.stringify(fixture));
  page.context.restore();
  assert.equal(page.context.state.restoreFailure, null);
  assert.equal(page.context.state.connections.length, fixture.connections.length);
  page.context.setLanguage("ru");
  const saved = JSON.parse(page.values.get(STORAGE_KEY));
  assert.deepEqual(saved.sources, fixture.sources);
  assert.equal(saved.preferences.language, "ru");
  assert.deepEqual(saved.connections.map(row => row.route), fixture.connections.map(row => row.route));
});

test("valid import replaces a failed restore only after explicit confirmation", async () => {
  const page = browser("broken record");
  page.context.restore();
  const file = { text: async () => JSON.stringify(fixture) };
  await page.context.importJson(file);
  assert.equal(page.confirmations.length, 1);
  assert.equal(page.values.get(STORAGE_KEY), "broken record");
  assert.ok(page.context.state.restoreFailure);
  page.context.confirmResult = true;
  await page.context.importJson(file);
  assert.equal(page.context.state.restoreFailure, null);
  assert.deepEqual(JSON.parse(page.values.get(STORAGE_KEY)).sources, fixture.sources);
  assert.equal(page.context.state.connections.length, fixture.connections.length);
  page.handlers.showSavedLines();
  assert.equal(page.context.state.storageStatus, "storage.saved");
});

test("a rejected recovery import retains the stored original and reports its hash", async () => {
  const page = browser("broken record");
  page.context.restore();
  page.context.setLanguage("ru");
  const invalid = structuredClone(fixture);
  delete invalid.sources.renesasManualSha256;
  await page.context.importJson({ text: async () => JSON.stringify(invalid) });
  assert.equal(page.values.get(STORAGE_KEY), "broken record");
  assert.match(page.alerts[0], /renesasManualSha256/);
  assert.equal(page.confirmations.length, 0);
});

test("discard requires confirmation even when a failed restore has no loaded connections", () => {
  const page = browser("broken record");
  page.context.restore();
  page.context.clearWorkspace();
  assert.equal(page.confirmations.length, 1);
  assert.equal(page.values.get(STORAGE_KEY), "broken record");
  page.context.confirmResult = true;
  page.context.clearWorkspace();
  assert.equal(page.context.state.restoreFailure, null);
  assert.equal(page.values.has(STORAGE_KEY), false);
  page.handlers.advancedPins();
  assert.deepEqual(JSON.parse(page.values.get(STORAGE_KEY)).sources, fixture.sources);
});
