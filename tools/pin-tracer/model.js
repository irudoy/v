(function attachPinTracerModel(root, factory) {
  const model = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = model;
  }
  root.PinTracerModel = model;
})(typeof globalThis !== "undefined" ? globalThis : this, function createPinTracerModel() {
  "use strict";

  const DEFAULT_PREFERENCES = Object.freeze({
    advancedPins: false,
    showSavedLines: false
  });

  function mcuPinCategories(name) {
    const value = String(name || "");
    if (/^AN\d+$/.test(value)) return ["analog"];

    const categories = [];
    const externalBus = /^P[EFH]\d+\/[AD]\d+|\/CS\d|\/WR|\/RD|\/WAIT|\/BACK|\/BREQ/.test(value);
    if (/PULS|TIO|TO\d|TI\d|ADTO|ADTRG|TCLK/.test(value)) categories.push("timer");
    if (/HTxD|HRxD|TxD|RxD|SCK/.test(value)) categories.push("communication");
    if (/IRQ/.test(value)) categories.push("interrupt");
    if (externalBus) categories.push("bus");
    if (/^P[A-L]\d+/.test(value) && !externalBus) categories.push("gpio");
    return categories.length ? categories : ["system"];
  }

  function classifyMcuPin(name) {
    return mcuPinCategories(name)[0];
  }

  function mcuPinMatchesCategory(name, category) {
    return mcuPinCategories(name).includes(category);
  }

  function isDefaultSelectable(categoryOrCategories) {
    const categories = Array.isArray(categoryOrCategories)
      ? categoryOrCategories
      : [categoryOrCategories];
    return categories.some(category =>
      ["analog", "timer", "communication", "interrupt", "gpio"].includes(category)
    );
  }

  function togglePinSelection(selectedPin, clickedPin) {
    return selectedPin === clickedPin ? null : clickedPin;
  }

  function connectorColumnKinds(rangeStart, columnCount, wideTerminalRange) {
    const [wideStart, wideEnd] = wideTerminalRange;
    return Array.from({ length: columnCount }, (_, visualColumn) => {
      const sourceColumn = columnCount - 1 - visualColumn;
      const columnStart = rangeStart + sourceColumn * 4;
      const columnEnd = columnStart + 3;
      return columnEnd >= wideStart && columnStart <= wideEnd ? "power" : "standard";
    });
  }

  function classifyEcuSignal(signal) {
    if (!signal) return "unknown";
    if (/^GND|^GNDA/.test(signal)) return "ground";
    if (/^AVCC|^VMOT|^BATT$|^VBR$/.test(signal)) return "power";
    if (/^INJ#/.test(signal)) return "injector";
    if (/^IGN#/.test(signal)) return "ignition";
    if (/^MOTOR/.test(signal)) return "hbridge";
    if (/CAN/.test(signal)) return "can";
    if (/KLINE/.test(signal)) return "kline";
    if (/KNK/.test(signal)) return "knock";
    if (/^AF[+-]/.test(signal)) return "airFuel";
    if (/^O2SR/.test(signal)) return "oxygen";
    if (/^O2HR|^AFH/.test(signal)) return "lowSide";
    if (/^POS$|PHASE/.test(signal)) return "timer";
    if (/^TACHO$/.test(signal)) return "logicOutput";
    if (/TPS|APS|PRES|^FTPRS$|^TA|^TW$|^TO|^TF$|CURSEN|^QA\d\+/.test(signal)) return "analog";
    if (/^CVTC|^EVTC|^EVAP$|^FPR$|^CDCV$|^SSOFF$|^MOTRLY/.test(signal)) return "lowSide";
    if (/BRAKE|SW|NEUT/.test(signal)) return "switch";
    return "unknown";
  }

  const ECU_SIGNAL_DESCRIPTIONS = Object.freeze({
    GND: "ECM ground",
    GNDA: "Sensor ground for camshaft position sensor bank 1 and power steering pressure sensor",
    EVAP: "EVAP canister purge volume control solenoid valve output",
    FPR: "Fuel pump relay control output",
    SSOFF: "ECM relay control output (self shut-off)",
    POS: "Crankshaft position sensor (POS) signal",
    "AVCC2-POS": "5 V supply for crankshaft position sensor",
    "GND-POS": "Ground for crankshaft position sensor",
    IGNSW: "Ignition switch input",
    TW: "Engine coolant temperature sensor input",
    "GNDA-KNK": "Sensor ground for knock sensors",
    TO1: "Engine oil temperature sensor input",
    "GNDA-O2_TW_TO": "Sensor ground for oxygen, coolant, and oil temperature sensors",
    PSPRES: "Power steering pressure sensor input",
    "GNDA-E-PHS": "Sensor ground for exhaust valve timing position sensors",
    CURSEN: "Battery current sensor input",
    "GND-PHASE#2": "Ground for camshaft position sensor, bank 2",
    BATT: "ECM backup power supply",
    "GNDA-CURSEN": "Ground for battery current sensor",
    ASCDSW: "ICC or ASCD steering switch input, depending on vehicle equipment",
    FTPRS: "EVAP control system pressure sensor input",
    PDPRES: "Refrigerant pressure sensor input",
    TF: "Fuel tank temperature sensor input",
    "GNDA-ASCDSW": "Ground for ICC or ASCD steering switch",
    "NEUT-H [A/T or M/T]": "Park/neutral position switch input for A/T, or neutral switch input for M/T",
    TACHO: "Engine speed output signal",
    "AVCC2-FTPRS": "5 V supply for EVAP control system pressure sensor",
    "AVCC2-PDPRES": "5 V supply for refrigerant pressure sensor",
    "GNDA-FTPRS": "Ground for EVAP control system pressure sensor",
    "GNDA-PDPRES": "Ground for refrigerant pressure sensor",
    VHECAN_L1: "Vehicle high-speed CAN bus low",
    VHECAN_H1: "Vehicle high-speed CAN bus high",
    KLINE: "Bidirectional K-line diagnostic data link",
    CDCV: "EVAP canister vent control valve output",
    BRAKE: "Stop lamp switch input",
    VBR: "Ignition-switched ECM power supply input",
    BNCSW: "ICC or ASCD brake switch input, depending on vehicle equipment",
    "AVCC1-PHASE#1": "Shared 5 V supply for camshaft and exhaust valve timing position sensors bank 1, and power steering pressure sensor",
    "AVCC2-PHASE#2": "Shared 5 V supply for camshaft and exhaust valve timing position sensors bank 2, and battery current sensor"
  });

  function describeEcuSignal(signal) {
    const value = String(signal || "").trim();
    if (!value) return "No signal listed in source";
    if (ECU_SIGNAL_DESCRIPTIONS[value]) return ECU_SIGNAL_DESCRIPTIONS[value];

    let match = value.match(/^AFH(\d)$/);
    if (match) return `A/F sensor 1 heater output, bank ${match[1]}`;

    match = value.match(/^MOTOR([12])-B([12])$/);
    if (match) {
      const direction = match[1] === "1" ? "open" : "close";
      return `Throttle control motor ${direction} output, bank ${match[2]}`;
    }

    match = value.match(/^VMOT-B([12])$/);
    if (match) return `Throttle control motor relay power supply, bank ${match[1]}`;

    match = value.match(/^MOTRLY-B([12])$/);
    if (match) return `Throttle control motor relay control output, bank ${match[1]}`;

    match = value.match(/^EVTC#([12])$/);
    if (match) return `Exhaust valve timing control magnet retarder output, bank ${match[1]}`;

    match = value.match(/^CVTC#([12])$/);
    if (match) return `Intake valve timing control solenoid valve output, bank ${match[1]}`;

    match = value.match(/^IGN#(\d)$/);
    if (match) return `Ignition signal No. ${match[1]} output`;

    match = value.match(/^INJ#(\d)$/);
    if (match) return `Fuel injector No. ${match[1]} control output`;

    match = value.match(/^O2HR([12])$/);
    if (match) return `Heated oxygen sensor 2 heater output, bank ${match[1]}`;

    match = value.match(/^TPS([12])-B([12])$/);
    if (match) return `Throttle position sensor ${match[1]} input, bank ${match[2]}`;

    match = value.match(/^GNDA-TPS-B([12])$/);
    if (match) return `Ground for throttle position sensors, bank ${match[1]}`;

    match = value.match(/^AVCC\d-TPS-B([12])$/);
    if (match) return `5 V supply for throttle position sensors, bank ${match[1]}`;

    match = value.match(/^AF([+-])([12])$/);
    if (match) {
      return `A/F sensor 1 ${match[1]} signal input, bank ${match[2]}`;
    }

    match = value.match(/^E-PHASE#([12])$/);
    if (match) return `Exhaust valve timing control position sensor input, bank ${match[1]}`;

    match = value.match(/^PHASE#([12])$/);
    if (match) return `Camshaft position sensor (PHASE) input, bank ${match[1]}`;

    match = value.match(/^AVCC\d-PHASE#([12])$/);
    if (match) return `5 V supply for camshaft position sensor, bank ${match[1]}`;

    match = value.match(/^TA\+?([12])$/);
    if (match) return `Intake air temperature sensor input, bank ${match[1]}`;

    match = value.match(/^GNDA-QA([12])_TA[12]$/);
    if (match) {
      return `Ground for mass air flow and intake air temperature sensors, bank ${match[1]}`;
    }

    match = value.match(/^KNK([12])$/);
    if (match) return `Knock sensor input, bank ${match[1]}`;

    match = value.match(/^O2SR([12])$/);
    if (match) return `Heated oxygen sensor 2 signal input, bank ${match[1]}`;

    match = value.match(/^QA([12])\+$/);
    if (match) return `Mass air flow sensor input, bank ${match[1]}`;

    match = value.match(/^APS([12])$/);
    if (match) return `Accelerator pedal position sensor ${match[1]} input`;

    match = value.match(/^AVCC\d-APS([12])$/);
    if (match) return `5 V supply for accelerator pedal position sensor ${match[1]}`;

    match = value.match(/^GNDA-APS([12])$/);
    if (match) return `Ground for accelerator pedal position sensor ${match[1]}`;

    return "Factory signal label; exact function not expanded";
  }

  const WIRE_COLOR_DESCRIPTIONS = Object.freeze({
    B: "black",
    W: "white",
    R: "red",
    G: "green",
    L: "blue",
    Y: "yellow",
    LG: "light green",
    BR: "brown",
    O: "orange",
    P: "pink",
    V: "violet",
    SB: "sky blue",
    GR: "gray",
    SHIELD: "shield"
  });

  function describeWireColor(code) {
    const value = String(code || "").trim();
    if (!value) return "unknown";
    if (WIRE_COLOR_DESCRIPTIONS[value]) return WIRE_COLOR_DESCRIPTIONS[value];
    if (value.includes("/")) {
      return value.split("/").map(part => WIRE_COLOR_DESCRIPTIONS[part] || part).join(" / ");
    }
    return value;
  }

  function genericSuggestionForSignal(signal) {
    const topology = classifyEcuSignal(signal);
    const suggestions = {
      analog: {
        categories: ["analog"],
        label: "ADC channel behind the input conditioning"
      },
      timer: {
        categories: ["timer", "gpio"],
        label: "Timer capture or conditioned GPIO input"
      },
      injector: {
        categories: ["timer", "gpio"],
        label: "ATU-II one-shot or GPIO output behind an injector driver"
      },
      ignition: {
        categories: ["timer", "gpio"],
        label: "APC pulse, timer, or GPIO output behind an ignition buffer"
      },
      hbridge: {
        categories: ["timer", "gpio"],
        label: "PWM or GPIO control outputs behind an H-bridge driver"
      },
      lowSide: {
        categories: ["timer", "gpio"],
        label: "PWM or GPIO output behind a low-side driver"
      },
      logicOutput: {
        categories: ["timer", "gpio"],
        label: "Timer or GPIO output behind a buffer or open-drain stage"
      },
      can: {
        categories: ["communication"],
        label: "HCAN transmit/receive pair behind a CAN transceiver"
      },
      kline: {
        categories: ["communication"],
        label: "SCI transmit/receive pair behind a K-line transceiver"
      },
      knock: {
        categories: ["analog", "communication"],
        label: "ADC or serial output of a knock-sensor front end"
      },
      airFuel: {
        categories: ["analog", "communication"],
        label: "ADC or serial output of an A/F-sensor interface"
      },
      oxygen: {
        categories: ["analog"],
        label: "ADC input behind oxygen-sensor conditioning"
      },
      switch: {
        categories: ["gpio", "interrupt", "analog"],
        label: "Conditioned GPIO, IRQ, or ADC input"
      },
      power: {
        categories: ["system", "analog"],
        label: "Supply network or monitored ADC input"
      },
      ground: {
        categories: ["system"],
        label: "Vss/AVss return network"
      },
      unknown: {
        categories: ["gpio", "communication"],
        label: "GPIO or intermediate ASIC interface"
      }
    };
    const suggestion = suggestions[topology];
    return {
      ...suggestion,
      category: suggestion.categories[0],
      topology
    };
  }

  function ecuSignalMatchesMcuPin(signal, mcuName) {
    if (!String(signal || "").trim()) return false;
    const signalCategories = genericSuggestionForSignal(signal).categories;
    const pinCategories = mcuPinCategories(mcuName);
    return signalCategories.some(category => pinCategories.includes(category));
  }

  function normalizePreferences(preferences) {
    const value = preferences && typeof preferences === "object" ? preferences : {};
    return {
      advancedPins: value.advancedPins === true,
      showSavedLines: value.showSavedLines === true
    };
  }

  function validatePayload(payload, options) {
    const config = options || {};
    if (!payload || payload.schema !== config.schema || !Array.isArray(payload.connections)) {
      throw new Error("Unsupported or invalid pin-tracer JSON.");
    }
    const topologyKeys = new Set(Object.keys(config.topologyProfiles || {}));
    const createId = typeof config.createId === "function"
      ? config.createId
      : () => `link-${Date.now()}-${Math.random().toString(16).slice(2)}`;
    const connectionIds = new Set();
    const endpointPairs = new Set();
    const connections = payload.connections.map((item, index) => {
      if (!item || typeof item !== "object") {
        throw new Error(`Invalid connection at item ${index + 1}.`);
      }
      const ecuPin = Number(item.ecuPin);
      const mcuPin = Number(item.mcuPin);
      if (!Number.isInteger(ecuPin) || ecuPin < 1 || ecuPin > 128) {
        throw new Error(`Invalid ECM terminal: ${item.ecuPin}`);
      }
      if (!Number.isInteger(mcuPin) || mcuPin < 1 || mcuPin > 256) {
        throw new Error(`Invalid MCU pin: ${item.mcuPin}`);
      }
      const id = String(item.id || createId()).trim();
      if (!id || connectionIds.has(id)) {
        throw new Error(`Duplicate or empty connection identifier at item ${index + 1}.`);
      }
      connectionIds.add(id);
      const endpointPair = `${ecuPin}:${mcuPin}`;
      if (endpointPairs.has(endpointPair)) {
        throw new Error(`Duplicate ECM/MCU endpoint pair at item ${index + 1}.`);
      }
      endpointPairs.add(endpointPair);
      const route = String(item.route || "").trim();
      if (!route) {
        throw new Error(`Missing component path at item ${index + 1}.`);
      }
      return {
        id,
        ecuPin,
        mcuPin,
        topology: topologyKeys.has(item.topology) ? item.topology : "unknown",
        route,
        comment: String(item.comment || "").trim(),
        createdAt: String(item.createdAt || new Date().toISOString()),
        updatedAt: String(item.updatedAt || new Date().toISOString())
      };
    });
    return {
      connections,
      preferences: normalizePreferences(payload.preferences)
    };
  }

  function findDuplicateConnection(connections, connection) {
    return connections.find(item =>
      item.id !== connection.id
      && item.ecuPin === connection.ecuPin
      && item.mcuPin === connection.mcuPin
    ) || null;
  }

  function calculateStats(connections, sourcePinCount) {
    const usedEcuPins = new Set(connections.map(connection => connection.ecuPin));
    const count = Number.isFinite(sourcePinCount) && sourcePinCount > 0 ? sourcePinCount : 0;
    return {
      connections: connections.length,
      coverage: count ? Math.round((usedEcuPins.size / count) * 100) : 0
    };
  }

  function formatLocalDate(date) {
    const value = date instanceof Date ? date : new Date(date);
    if (Number.isNaN(value.getTime())) {
      throw new Error("Invalid date.");
    }
    const pad = number => String(number).padStart(2, "0");
    return `${value.getFullYear()}-${pad(value.getMonth() + 1)}-${pad(value.getDate())}`;
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  return Object.freeze({
    DEFAULT_PREFERENCES,
    mcuPinCategories,
    classifyMcuPin,
    mcuPinMatchesCategory,
    isDefaultSelectable,
    togglePinSelection,
    connectorColumnKinds,
    classifyEcuSignal,
    describeEcuSignal,
    describeWireColor,
    genericSuggestionForSignal,
    ecuSignalMatchesMcuPin,
    normalizePreferences,
    validatePayload,
    findDuplicateConnection,
    calculateStats,
    formatLocalDate,
    escapeHtml
  });
});
