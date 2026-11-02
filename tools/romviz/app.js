(() => {
  "use strict";

  const root = document.getElementById("romviz");
  const atlas = JSON.parse(document.getElementById("romviz-data").textContent);
  const svgNS = "http://www.w3.org/2000/svg";
  const layerColors = {
    structure: "var(--structure)",
    maps: "var(--maps)",
    axes: "var(--axes)",
    diagnostics: "var(--diagnostics)",
    patches: "var(--patches)",
    integrity: "var(--integrity)",
  };
  const laneWeights = {
    structure: 1.05,
    maps: 0.9,
    axes: 0.72,
    diagnostics: 0.9,
    patches: 1.65,
    integrity: 0.92,
  };

  const elements = {
    romIdentity: document.getElementById("rom-identity"),
    headerStats: document.getElementById("header-stats"),
    romInfoContent: document.getElementById("rom-info-content"),
    romPickerLabel: document.getElementById("rom-picker-label"),
    romPicker: document.getElementById("rom-picker"),
    search: document.getElementById("search"),
    address: document.getElementById("address"),
    zoomIn: document.getElementById("zoom-in"),
    zoomOut: document.getElementById("zoom-out"),
    fullView: document.getElementById("full-view"),
    layerFilters: document.getElementById("layer-filters"),
    semanticOnly: document.getElementById("semantic-only"),
    overview: document.getElementById("overview"),
    searchStatus: document.getElementById("search-status"),
    viewportLabel: document.getElementById("viewport-label"),
    addressMap: document.getElementById("address-map"),
    addressMapDesc: document.getElementById("address-map-desc"),
    detailsEmpty: document.getElementById("details-empty"),
    detailsContent: document.getElementById("details-content"),
    detailKind: document.getElementById("detail-kind"),
    detailLabel: document.getElementById("detail-label"),
    detailRange: document.getElementById("detail-range"),
    detailBadges: document.getElementById("detail-badges"),
    detailMeta: document.getElementById("detail-meta"),
    detailDescription: document.getElementById("detail-description"),
    detailNote: document.getElementById("detail-note"),
    detailRelated: document.getElementById("detail-related"),
    detailSource: document.getElementById("detail-source"),
    closeDetails: document.getElementById("close-details"),
    warnings: document.getElementById("warnings"),
    warningList: document.getElementById("warning-list"),
    tooltip: document.getElementById("tooltip"),
    viewAddress: document.getElementById("view-address"),
    viewArchitecture: document.getElementById("view-architecture"),
    addressView: document.getElementById("address-view"),
  };

  const state = {
    view: "address",
    romIndex: 0,
    rom: null,
    objectById: new Map(),
    searchIndex: new Map(),
    rows: new Map(),
    rowCounts: new Map(),
    visibleLayers: new Set(atlas.layers.map((layer) => layer.id)),
    semanticOnly: false,
    query: "",
    matches: new Set(),
    orderedMatches: [],
    selectedId: null,
    viewStart: 0,
    viewEnd: 1,
    drag: null,
    overviewDrag: null,
    gestureScale: null,
    framePending: false,
  };

  function svgElement(name, attributes = {}) {
    const node = document.createElementNS(svgNS, name);
    for (const [key, value] of Object.entries(attributes)) {
      node.setAttribute(key, String(value));
    }
    return node;
  }

  function formatAddress(value, size = state.rom.size) {
    const width = Math.max(6, Math.ceil(Math.log2(Math.max(2, size)) / 4));
    return `0x${Math.round(value).toString(16).toUpperCase().padStart(width, "0")}`;
  }

  const infoLabels = {
    xmlid: "XML ID",
    internalidaddress: "Internal ID address",
    internalidstring: "Internal ID string",
    ecuid: "ECU ID",
    caseid: "Case ID",
    make: "Make",
    model: "Model",
    submodel: "Engine (submodel)",
    market: "Market",
    transmission: "Transmission",
    memmodel: "Memory model",
    endian: "Byte order",
    filesize: "File size",
    author: "Author",
    version: "Version",
    path: "Registry path",
    rom: "ROM",
    sha256: "SHA-256",
    note: "Note",
    family: "Family",
    kind: "Kind",
    members: "Members",
    canonical: "Canonical image",
    mcu: "MCU",
    flash_size: "Flash size",
    software_ids: "Software IDs",
    same_address_inheritance: "Same-address inheritance",
    direct_address_inheritance: "Direct address inheritance",
    layouts: "Layouts",
    calibration_region: "Calibration region",
    exact_ranges: "Exact ranges",
    evidence: "Evidence",
  };
  const proseInfoFields = new Set(["evidence", "note"]);

  function formatInfoValue(key, value) {
    if (key === "flash_size" && Number.isInteger(value)) {
      return `${formatAddress(value, value)} (${formatBytes(value)})`;
    }
    if (Array.isArray(value)) {
      return value.map((item) => formatInfoValue("", item)).join(", ");
    }
    if (typeof value === "boolean") {
      return value ? "yes" : "no";
    }
    if (value && typeof value === "object") {
      return Object.entries(value)
        .map(([name, item]) => `${name}: ${formatInfoValue("", item)}`)
        .join(", ");
    }
    return String(value);
  }

  function formatBytes(value) {
    if (value >= 1024 * 1024 && value % (1024 * 1024) === 0) {
      return `${value / (1024 * 1024)} MiB`;
    }
    if (value >= 1024) {
      const digits = value % 1024 === 0 ? 0 : 1;
      return `${(value / 1024).toFixed(digits)} KiB`;
    }
    return `${value} B`;
  }

  function clamp(value, minimum, maximum) {
    return Math.max(minimum, Math.min(maximum, value));
  }

  function normalizeQuery(value) {
    return value.trim().toLowerCase();
  }

  function parseAddress(value) {
    const match = value.trim().match(/^(?:0x)?([0-9a-f]+)$/i);
    if (!match) {
      return null;
    }
    const parsed = Number.parseInt(match[1], 16);
    return Number.isSafeInteger(parsed) ? parsed : null;
  }

  function searchableText(item) {
    const metadata = item.meta.map((entry) => `${entry.label} ${entry.value}`).join(" ");
    const binding = item.binding || {};
    return [
      item.label,
      item.description,
      item.note,
      item.source,
      item.kind,
      item.role,
      item.confidence,
      item.patch,
      item.patchStatus,
      item.tags.join(" "),
      metadata,
      binding.meaning,
      binding.name,
      binding.reference,
      ...(binding.former || []),
      ...(binding.symbols || []).map((symbol) => symbol.name || ""),
      formatAddress(item.start),
      item.start.toString(16),
    ].join(" ").toLowerCase();
  }

  function assignRows() {
    state.rows.clear();
    state.rowCounts.clear();
    for (const layer of atlas.layers) {
      const rowsEnd = [];
      const objects = state.rom.objects
        .filter((item) => item.layer === layer.id)
        .sort((left, right) => left.start - right.start || left.end - right.end);
      for (const item of objects) {
        let row = rowsEnd.findIndex((end) => end <= item.start);
        if (row < 0) {
          row = rowsEnd.length;
          rowsEnd.push(item.end);
        } else {
          rowsEnd[row] = item.end;
        }
        state.rows.set(item.id, row);
      }
      state.rowCounts.set(layer.id, Math.max(1, rowsEnd.length));
    }
  }

  function setupRom(index, preserveHash = false) {
    state.romIndex = clamp(index, 0, atlas.roms.length - 1);
    state.rom = atlas.roms[state.romIndex];
    state.objectById = new Map(state.rom.objects.map((item) => [item.id, item]));
    state.searchIndex = new Map(state.rom.objects.map((item) => [item.id, searchableText(item)]));
    state.selectedId = null;
    state.query = "";
    state.matches.clear();
    state.orderedMatches = [];
    state.viewStart = 0;
    state.viewEnd = state.rom.size;
    elements.romPicker.value = String(state.romIndex);
    elements.search.value = "";
    elements.address.value = "";
    assignRows();
    renderRomMetadata();
    renderLayerFilters();
    renderWarnings();
    clearDetails(false);
    architecture.setRom(state.rom);
    elements.viewArchitecture.disabled = !architectureAvailable();
    if (state.view === "architecture" && !architectureAvailable()) {
      showView("address", false);
    }
    if (preserveHash) {
      restoreHash();
    }
    scheduleRender();
  }

  function architectureAvailable() {
    const binding = state.rom.architecture;
    return Boolean(binding && atlas.architectures && atlas.architectures[binding.source]);
  }

  function showView(view, updateLocation = true) {
    const next = view === "architecture" && architectureAvailable() ? "architecture" : "address";
    const changed = next !== state.view;
    const showArchitecture = next === "architecture";
    state.view = next;
    root.dataset.view = next;
    elements.addressView.hidden = showArchitecture;
    elements.viewAddress.setAttribute("aria-selected", String(!showArchitecture));
    elements.viewArchitecture.setAttribute("aria-selected", String(showArchitecture));
    elements.viewAddress.tabIndex = showArchitecture ? -1 : 0;
    elements.viewArchitecture.tabIndex = showArchitecture ? 0 : -1;
    if (showArchitecture) {
      hideTooltip();
      architecture.activate();
    } else {
      architecture.deactivate();
      scheduleRender();
    }
    if (updateLocation && changed) {
      updateHash(true);
    }
  }

  function renderRomMetadata() {
    document.title = `${state.rom.id} ROM atlas`;
    const {Engine: engine, Vehicle: vehicle} = state.rom.metadata;
    elements.romIdentity.textContent = [state.rom.label, engine, vehicle].filter(Boolean).join(" | ");
    renderRomInfo();
    const stats = [
      ["Objects", state.rom.objects.length.toLocaleString()],
      ["Functions", `${state.rom.reviewedFunctions.toLocaleString()}/${state.rom.structuralFunctions.toLocaleString()}`],
      ["Maps", (state.rom.counts.maps || 0).toLocaleString()],
      ["Patches", (state.rom.counts.patches || 0).toLocaleString()],
    ];
    elements.headerStats.replaceChildren();
    for (const [label, value] of stats) {
      const wrapper = document.createElement("div");
      const term = document.createElement("dt");
      const definition = document.createElement("dd");
      term.textContent = label;
      definition.textContent = value;
      wrapper.append(term, definition);
      elements.headerStats.append(wrapper);
    }
  }

  function infoSection(title, entries) {
    const section = document.createElement("section");
    section.className = "rom-info-section";
    const heading = document.createElement("h2");
    heading.textContent = title;
    const list = document.createElement("dl");
    list.className = "rom-info-list";
    for (const [key, value] of entries) {
      const term = document.createElement("dt");
      const definition = document.createElement("dd");
      term.textContent = infoLabels[key] || key;
      definition.textContent = formatInfoValue(key, value);
      if (proseInfoFields.has(key)) definition.className = "rom-info-prose";
      list.append(term, definition);
    }
    section.append(heading, list);
    return section;
  }

  function renderRomInfo() {
    const rom = state.rom;
    const groups = [
      ["Identity", Object.entries(rom.identity)],
      ["Image", [
        ...Object.entries(rom.registry),
        ["Size", `${formatAddress(rom.size, rom.size)} (${formatBytes(rom.size)})`],
        ["Layout", rom.layout],
        ["Annotation source", rom.metadata["Annotation source"]],
      ]],
    ];
    if (rom.family) {
      groups.push([`Family ${rom.family.key}`, Object.entries(rom.family.fields)]);
      for (const relationship of rom.family.relationships) {
        groups.push([
          `Relationship with ${relationship.family}`,
          Object.entries(relationship).filter(([key]) => key !== "family"),
        ]);
      }
    } else {
      groups.push(["Family", [["Homology family", "none declared"]]]);
    }
    elements.romInfoContent.replaceChildren(...groups
      .map(([title, entries]) => [title, entries.filter(([, value]) => value !== "")])
      .filter(([, entries]) => entries.length)
      .map(([title, entries]) => infoSection(title, entries)));
  }

  function renderLayerFilters() {
    elements.layerFilters.replaceChildren();
    for (const layer of atlas.layers) {
      const label = document.createElement("label");
      label.className = "layer-filter";
      label.style.setProperty("--layer-color", layerColors[layer.id]);
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.checked = state.visibleLayers.has(layer.id);
      checkbox.dataset.layer = layer.id;
      const text = document.createElement("span");
      text.textContent = layer.label;
      const count = document.createElement("strong");
      count.textContent = (state.rom.counts[layer.id] || 0).toLocaleString();
      label.append(checkbox, text, count);
      elements.layerFilters.append(label);
    }
  }

  function renderWarnings() {
    elements.warningList.replaceChildren();
    elements.warnings.hidden = state.rom.warnings.length === 0;
    for (const warning of state.rom.warnings) {
      const item = document.createElement("li");
      item.textContent = warning;
      elements.warningList.append(item);
    }
  }

  function objectVisible(item) {
    if (!state.visibleLayers.has(item.layer)) {
      return false;
    }
    if (state.semanticOnly && item.kind === "function-structure") {
      return false;
    }
    return item.end > state.viewStart && item.start < state.viewEnd;
  }

  function scoreMatch(item, query, address) {
    let score = 100;
    const label = item.label.toLowerCase();
    if (address !== null) {
      if (item.start === address) score -= 70;
      else if (item.start <= address && item.end > address) score -= 55;
      else score += Math.min(30, Math.abs(item.start - address) / 4096);
    }
    if (label === query) score -= 45;
    else if (label.startsWith(query)) score -= 30;
    else if (label.includes(query)) score -= 18;
    if (item.reviewed) score -= 5;
    if (item.patch) score -= 2;
    return score;
  }

  function updateSearch() {
    state.query = normalizeQuery(elements.search.value);
    state.matches.clear();
    state.orderedMatches = [];
    if (!state.query) {
      elements.searchStatus.textContent = "";
      scheduleRender();
      return;
    }
    const address = parseAddress(state.query);
    const candidates = [];
    for (const item of state.rom.objects) {
      const textMatch = state.searchIndex.get(item.id).includes(state.query);
      const addressMatch = address !== null && (
        item.start === address || (item.start <= address && item.end > address)
      );
      if (textMatch || addressMatch) {
        state.matches.add(item.id);
        candidates.push([scoreMatch(item, state.query, address), item]);
      }
    }
    candidates.sort((left, right) => left[0] - right[0] || left[1].start - right[1].start);
    state.orderedMatches = candidates.map((entry) => entry[1].id);
    elements.searchStatus.textContent = `${state.matches.size.toLocaleString()} match${state.matches.size === 1 ? "" : "es"}`;
    scheduleRender();
  }

  function setView(start, end, updateLocation = true) {
    const minimumSpan = Math.min(0x80, state.rom.size);
    let span = clamp(end - start, minimumSpan, state.rom.size);
    let center = (start + end) / 2;
    center = clamp(center, span / 2, state.rom.size - span / 2);
    state.viewStart = Math.max(0, center - span / 2);
    state.viewEnd = Math.min(state.rom.size, state.viewStart + span);
    if (state.viewEnd - state.viewStart < span) {
      state.viewStart = state.viewEnd - span;
    }
    if (updateLocation) {
      updateHash();
    }
    scheduleRender();
  }

  function zoom(factor, anchor = (state.viewStart + state.viewEnd) / 2) {
    const span = state.viewEnd - state.viewStart;
    const nextSpan = clamp(span * factor, 0x80, state.rom.size);
    const ratio = span ? (anchor - state.viewStart) / span : 0.5;
    setView(anchor - nextSpan * ratio, anchor + nextSpan * (1 - ratio));
  }

  function zoomToObject(item) {
    const size = item.end - item.start;
    const span = clamp(Math.max(size * 18, 0x800), 0x800, Math.min(state.rom.size, 0x20000));
    const center = (item.start + item.end) / 2;
    setView(center - span / 2, center + span / 2);
  }

  function jumpToAddress(address, selectContaining = true) {
    if (address === null || address < 0 || address >= state.rom.size) {
      elements.address.setCustomValidity(`Enter an address from ${formatAddress(0)} to ${formatAddress(state.rom.size - 1)}.`);
      elements.address.reportValidity();
      return;
    }
    elements.address.setCustomValidity("");
    const currentSpan = state.viewEnd - state.viewStart;
    const span = currentSpan === state.rom.size ? Math.min(0x10000, state.rom.size) : currentSpan;
    setView(address - span / 2, address + span / 2);
    if (selectContaining) {
      const containing = state.rom.objects
        .filter((item) => item.start <= address && item.end > address)
        .sort((left, right) => {
          const reviewOrder = Number(right.reviewed) - Number(left.reviewed);
          return reviewOrder || (left.end - left.start) - (right.end - right.start);
        });
      if (containing.length) {
        selectObject(containing[0].id, false);
      }
    }
  }

  function updateHash(push = false) {
    const parameters = new URLSearchParams();
    parameters.set("rom", state.rom.id);
    parameters.set("start", Math.round(state.viewStart).toString(16));
    parameters.set("end", Math.round(state.viewEnd).toString(16));
    if (state.selectedId) {
      parameters.set("object", state.selectedId);
    }
    if (state.view === "architecture") {
      parameters.set("view", "arch");
      for (const [key, value] of architecture.hashParams()) {
        parameters.set(key, value);
      }
    }
    const hash = `#${parameters.toString()}`;
    if (hash === location.hash) {
      return;
    }
    if (push) {
      history.pushState(null, "", hash);
    } else {
      history.replaceState(null, "", hash);
    }
  }

  function restoreHash() {
    const parameters = new URLSearchParams(location.hash.slice(1));
    const requestedRom = parameters.get("rom");
    if (requestedRom && requestedRom !== state.rom.id) {
      const index = atlas.roms.findIndex((rom) => rom.id === requestedRom);
      if (index >= 0 && index !== state.romIndex) {
        setupRom(index, true);
        return;
      }
    }
    const start = Number.parseInt(parameters.get("start"), 16);
    const end = Number.parseInt(parameters.get("end"), 16);
    if (Number.isFinite(start) && Number.isFinite(end) && start < end) {
      setView(start, end, false);
    }
    const objectId = parameters.get("object");
    if (objectId && state.objectById.has(objectId)) {
      selectObject(objectId, false);
    } else if (state.selectedId) {
      clearDetails(false);
    }
    architecture.restore(parameters);
    showView(parameters.get("view") === "arch" ? "architecture" : "address", false);
    updateHash();
  }

  function niceStep(span, plotWidth) {
    const targetTicks = clamp(Math.floor(plotWidth / 115), 3, 9);
    const raw = span / targetTicks;
    const exponent = Math.floor(Math.log2(Math.max(1, raw)));
    const base = 2 ** exponent;
    const multiplier = raw / base;
    if (multiplier <= 1) return base;
    if (multiplier <= 2) return base * 2;
    if (multiplier <= 4) return base * 4;
    return base * 8;
  }

  function laneLayout(height) {
    const axisHeight = 38;
    const activeLayers = atlas.layers.filter((layer) => state.visibleLayers.has(layer.id));
    const totalWeight = activeLayers.reduce((sum, layer) => sum + laneWeights[layer.id], 0) || 1;
    const available = Math.max(100, height - axisHeight - 8);
    const result = new Map();
    let top = axisHeight;
    for (const layer of activeLayers) {
      const laneHeight = available * laneWeights[layer.id] / totalWeight;
      result.set(layer.id, {top, height: laneHeight});
      top += laneHeight;
    }
    return {axisHeight, lanes: result};
  }

  function renderDensity(group, objects, layer, lane, plotLeft, plotWidth, xScale) {
    const binWidth = 2;
    const binCount = Math.max(1, Math.floor(plotWidth / binWidth));
    const bins = new Uint16Array(binCount);
    let maximum = 0;
    for (const item of objects) {
      const index = clamp(Math.floor((xScale(item.start) - plotLeft) / binWidth), 0, binCount - 1);
      bins[index] += 1;
      maximum = Math.max(maximum, bins[index]);
    }
    const y = lane.top + 24;
    const height = Math.max(8, lane.height - 31);
    for (let index = 0; index < bins.length; index += 1) {
      if (!bins[index]) continue;
      const opacity = 0.14 + 0.7 * Math.sqrt(bins[index] / maximum);
      const mark = svgElement("rect", {
        x: plotLeft + index * binWidth,
        y,
        width: binWidth,
        height,
        fill: layerColors[layer.id],
        opacity: opacity.toFixed(3),
      });
      group.append(mark);
    }
    const label = svgElement("text", {
      x: plotLeft + 6,
      y: y + Math.min(height - 3, 13),
      class: "density-label",
    });
    label.textContent = `${objects.length.toLocaleString()} structures - zoom in for individual functions`;
    group.append(label);
  }

  function renderAddressMap() {
    const svg = elements.addressMap;
    const width = Math.max(1, Math.round(svg.clientWidth));
    const height = Math.max(360, Math.round(svg.clientHeight));
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    svg.replaceChildren();

    const plotLeft = width < 520 ? 112 : 148;
    const plotRight = 14;
    const plotWidth = Math.max(120, width - plotLeft - plotRight);
    const span = state.viewEnd - state.viewStart;
    const xScale = (address) => plotLeft + (address - state.viewStart) / span * plotWidth;
    const layout = laneLayout(height);

    const background = svgElement("rect", {
      x: plotLeft,
      y: layout.axisHeight,
      width: plotWidth,
      height: height - layout.axisHeight - 5,
      fill: "transparent",
    });
    svg.append(background);

    const step = niceStep(span, plotWidth);
    const firstTick = Math.ceil(state.viewStart / step) * step;
    for (let tick = firstTick; tick <= state.viewEnd; tick += step) {
      const x = xScale(tick);
      svg.append(svgElement("line", {
        x1: x,
        y1: layout.axisHeight - 7,
        x2: x,
        y2: height - 5,
        class: "tick-line",
      }));
      const label = svgElement("text", {
        x: clamp(x, plotLeft + 2, plotLeft + plotWidth - 2),
        y: 19,
        class: "tick-label",
        "text-anchor": x > plotLeft + plotWidth - 45 ? "end" : x < plotLeft + 45 ? "start" : "middle",
      });
      label.textContent = formatAddress(tick);
      svg.append(label);
    }
    svg.append(svgElement("line", {
      x1: plotLeft,
      y1: layout.axisHeight - 7,
      x2: plotLeft + plotWidth,
      y2: layout.axisHeight - 7,
      class: "axis-line",
    }));

    let visibleCount = 0;
    for (const layer of atlas.layers) {
      const lane = layout.lanes.get(layer.id);
      if (!lane) continue;
      svg.append(svgElement("line", {
        x1: 0,
        y1: lane.top + lane.height,
        x2: width,
        y2: lane.top + lane.height,
        class: "lane-divider",
      }));
      const laneLabel = svgElement("text", {
        x: 10,
        y: lane.top + 18,
        class: "lane-label",
      });
      laneLabel.textContent = layer.label;
      svg.append(laneLabel);

      const layerObjects = state.rom.objects.filter((item) => item.layer === layer.id && objectVisible(item));
      visibleCount += layerObjects.length;
      const group = svgElement("g", {"data-lane": layer.id});
      svg.append(group);
      const densityMode = layer.id === "structure" && layerObjects.length > 750 && !state.query;
      if (densityMode) {
        renderDensity(group, layerObjects, layer, lane, plotLeft, plotWidth, xScale);
        continue;
      }

      const rowCount = state.rowCounts.get(layer.id) || 1;
      const usableTop = lane.top + 24;
      const usableHeight = Math.max(10, lane.height - 29);
      const maxRows = Math.max(1, Math.floor(usableHeight / 11));
      const rowHeight = usableHeight / Math.min(rowCount, maxRows);
      for (const item of layerObjects) {
        const globalRow = state.rows.get(item.id) || 0;
        const row = globalRow % maxRows;
        const rawX = xScale(Math.max(item.start, state.viewStart));
        const rawEnd = xScale(Math.min(item.end, state.viewEnd));
        const pointWidth = item.exactExtent ? 1.5 : 3;
        const markWidth = Math.max(pointWidth, rawEnd - rawX);
        const markGap = markWidth >= 8 ? 2 : markWidth >= 4 ? 1 : 0;
        const markX = rawX + markGap / 2;
        const drawnWidth = Math.max(pointWidth, markWidth - markGap);
        const markHeight = clamp(rowHeight - 2, 4, 10);
        const y = usableTop + row * rowHeight + Math.max(0, (rowHeight - markHeight) / 2);
        const classes = ["mark"];
        const isMatch = state.matches.has(item.id);
        if (state.query && !isMatch) classes.push("is-muted");
        if (isMatch) classes.push("is-match");
        if (state.selectedId === item.id) classes.push("is-selected");
        const mark = svgElement("rect", {
          x: markX,
          y,
          width: Math.min(drawnWidth, plotLeft + plotWidth - markX),
          height: markHeight,
          rx: markWidth > 5 ? 1.5 : 0,
          class: classes.join(" "),
          "data-object-id": item.id,
          "data-layer": item.layer,
          "data-kind": item.kind,
          "data-patch": item.patch,
          "data-patch-status": item.patchStatus,
          "aria-label": `${item.label}, ${formatAddress(item.start)}`,
        });
        group.append(mark);
        if (drawnWidth >= 86 && markHeight >= 8 && !classes.includes("is-muted")) {
          const text = svgElement("text", {
            x: markX + 4,
            y: y + markHeight - 1.5,
            class: "mark-label",
          });
          const maximumCharacters = Math.max(6, Math.floor((drawnWidth - 8) / 6));
          text.textContent = item.label.length > maximumCharacters
            ? `${item.label.slice(0, maximumCharacters - 3)}...`
            : item.label;
          group.append(text);
        }
      }
    }

    const selected = state.objectById.get(state.selectedId);
    if (selected && selected.end > state.viewStart && selected.start < state.viewEnd) {
      const x = xScale(selected.start);
      svg.append(svgElement("line", {
        x1: x,
        y1: layout.axisHeight - 7,
        x2: x,
        y2: height - 5,
        class: "selection-guide",
      }));
    }

    elements.viewportLabel.textContent = `${formatAddress(state.viewStart)} - ${formatAddress(state.viewEnd)} | ${formatBytes(Math.round(span))}`;
    elements.addressMapDesc.textContent = `${visibleCount.toLocaleString()} visible objects from ${formatAddress(state.viewStart)} through ${formatAddress(state.viewEnd)}.`;
  }

  function cssColor(name) {
    return getComputedStyle(root).getPropertyValue(name).trim();
  }

  function drawOverview() {
    const canvas = elements.overview;
    const rect = canvas.getBoundingClientRect();
    const ratio = window.devicePixelRatio || 1;
    const width = Math.max(1, Math.round(rect.width * ratio));
    const height = Math.max(1, Math.round(rect.height * ratio));
    if (canvas.width !== width || canvas.height !== height) {
      canvas.width = width;
      canvas.height = height;
    }
    const context = canvas.getContext("2d");
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    const logicalWidth = rect.width;
    const logicalHeight = rect.height;
    context.clearRect(0, 0, logicalWidth, logicalHeight);
    context.fillStyle = cssColor("--bg");
    context.fillRect(0, 0, logicalWidth, logicalHeight);

    const rgb = cssColor("--overview-rgb");
    const pages = state.rom.pageMetrics.pages;
    const pageWidth = logicalWidth / pages.length;
    const entropyHeight = logicalHeight * 0.62;
    pages.forEach((page, index) => {
      const alpha = page.erased > 0.98 ? 0.025 : 0.08 + page.entropy * 0.76;
      context.fillStyle = `rgba(${rgb}, ${alpha.toFixed(3)})`;
      context.fillRect(index * pageWidth, 0, Math.max(1, pageWidth + 0.2), entropyHeight);
    });

    const patchY = entropyHeight + 4;
    const patchHeight = Math.max(7, logicalHeight - patchY - 11);
    const patchObjects = state.rom.objects.filter((item) => item.layer === "patches" && !["patch-hook", "patch-anchor", "patch-site"].includes(item.kind));
    for (const item of patchObjects) {
      const x = item.start / state.rom.size * logicalWidth;
      const end = item.end / state.rom.size * logicalWidth;
      context.globalAlpha = item.patchStatus === "candidate" ? 0.55 : item.kind === "patch-claim" ? 0.18 : 0.78;
      context.fillStyle = item.patchStatus === "candidate" ? cssColor("--candidate") : cssColor("--patches");
      context.fillRect(x, patchY, Math.max(1, end - x), patchHeight);
    }
    context.globalAlpha = 1;

    const viewportX = state.viewStart / state.rom.size * logicalWidth;
    const viewportEnd = state.viewEnd / state.rom.size * logicalWidth;
    context.fillStyle = "rgba(255,255,255,0.08)";
    context.fillRect(viewportX, 0, Math.max(2, viewportEnd - viewportX), logicalHeight - 10);
    context.strokeStyle = cssColor("--selection");
    context.lineWidth = 1;
    context.strokeRect(viewportX + 0.5, 0.5, Math.max(1, viewportEnd - viewportX - 1), logicalHeight - 11);

    const selected = state.objectById.get(state.selectedId);
    if (selected) {
      const selectedX = selected.start / state.rom.size * logicalWidth;
      context.strokeStyle = cssColor("--patches");
      context.beginPath();
      context.moveTo(selectedX + 0.5, 0);
      context.lineTo(selectedX + 0.5, logicalHeight - 10);
      context.stroke();
    }

    context.fillStyle = cssColor("--muted");
    context.font = `11px ${cssColor("--font-mono")}`;
    context.textBaseline = "bottom";
    context.fillText(formatAddress(0), 3, logicalHeight);
    const endLabel = formatAddress(state.rom.size);
    context.fillText(endLabel, logicalWidth - context.measureText(endLabel).width - 3, logicalHeight);
  }

  function scheduleRender() {
    if (state.framePending || state.view !== "address") return;
    state.framePending = true;
    requestAnimationFrame(() => {
      state.framePending = false;
      if (state.view !== "address") return;
      renderAddressMap();
      drawOverview();
    });
  }

  function badge(text) {
    const item = document.createElement("span");
    item.className = "badge";
    item.textContent = text;
    return item;
  }

  function selectObject(objectId, zoomTo = false) {
    const item = state.objectById.get(objectId);
    if (!item) return;
    state.selectedId = item.id;
    if (zoomTo) {
      zoomToObject(item);
    }
    elements.detailsEmpty.hidden = true;
    elements.detailsContent.hidden = false;
    elements.detailKind.textContent = [item.layer, item.kind].join(" / ");
    elements.detailLabel.textContent = item.label;
    const extent = item.exactExtent ? "" : " | extent unknown";
    elements.detailRange.textContent = `${formatAddress(item.start)} - ${formatAddress(item.end)} | ${formatBytes(item.end - item.start)}${extent}`;
    elements.detailBadges.replaceChildren();
    for (const text of [item.confidence, item.role, item.patch, item.patchStatus].filter(Boolean)) {
      elements.detailBadges.append(badge(text));
    }
    elements.detailMeta.replaceChildren();
    const metadata = [
      {label: "Start", value: formatAddress(item.start)},
      {label: "End", value: formatAddress(item.end)},
      {label: "Size", value: formatBytes(item.end - item.start)},
      ...item.meta,
      ...(item.binding ? [
        {label: "Meaning", value: item.binding.meaning},
        {label: "Symbol", value: item.binding.reference},
        {label: "Applicable images", value: item.binding.images.length
          ? item.binding.images.join(", ") : "all images of the layout"},
        ...item.binding.symbols.map((symbol) => ({label: symbol.layout,
          value: `${symbol.ref}${symbol.images.length ? ` (${symbol.images.join(", ")})` : ""}`})),
        ...item.binding.statuses.map((status) => ({label: status.layout,
          value: `${status.state}${status.note ? `: ${status.note}` : ""}`})),
        ...item.binding.analogs.map((analog) => ({label: "Analog", value: `${analog.to}: ${analog.note}`})),
      ] : []),
    ];
    for (const entry of metadata) {
      const term = document.createElement("dt");
      const definition = document.createElement("dd");
      term.textContent = entry.label;
      definition.textContent = entry.value;
      elements.detailMeta.append(term, definition);
    }
    elements.detailDescription.textContent = item.description;
    elements.detailDescription.hidden = !item.description;
    elements.detailNote.textContent = item.note;
    elements.detailNote.hidden = !item.note;
    elements.detailRelated.replaceChildren();
    for (const relation of item.related) {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = `${relation.label}: ${formatAddress(relation.address)}`;
      button.addEventListener("click", () => jumpToAddress(relation.address));
      elements.detailRelated.append(button);
    }
    elements.detailSource.textContent = `Source: ${item.source}`;
    updateHash();
    scheduleRender();
  }

  function clearDetails(updateLocation = true) {
    state.selectedId = null;
    elements.detailsEmpty.hidden = false;
    elements.detailsContent.hidden = true;
    if (updateLocation) updateHash();
    scheduleRender();
  }

  function showTooltip(item, event) {
    elements.tooltip.replaceChildren();
    const title = document.createElement("strong");
    const range = document.createElement("span");
    title.textContent = item.label;
    range.textContent = `${formatAddress(item.start)} - ${formatAddress(item.end)}`;
    elements.tooltip.append(title, range);
    elements.tooltip.hidden = false;
    const margin = 12;
    const tooltipRect = elements.tooltip.getBoundingClientRect();
    let left = event.clientX + 14;
    let top = event.clientY + 14;
    if (left + tooltipRect.width > window.innerWidth - margin) {
      left = event.clientX - tooltipRect.width - 14;
    }
    if (top + tooltipRect.height > window.innerHeight - margin) {
      top = event.clientY - tooltipRect.height - 14;
    }
    elements.tooltip.style.left = `${Math.max(margin, left)}px`;
    elements.tooltip.style.top = `${Math.max(margin, top)}px`;
  }

  function hideTooltip() {
    elements.tooltip.hidden = true;
  }

  function mapGeometry() {
    const rect = elements.addressMap.getBoundingClientRect();
    const plotLeft = rect.width < 520 ? 112 : 148;
    const plotRight = 14;
    return {rect, plotLeft, plotWidth: Math.max(120, rect.width - plotLeft - plotRight)};
  }

  function addressAtClientX(clientX) {
    const geometry = mapGeometry();
    const fraction = clamp((clientX - geometry.rect.left - geometry.plotLeft) / geometry.plotWidth, 0, 1);
    return state.viewStart + fraction * (state.viewEnd - state.viewStart);
  }

  function wheelPixels(value, mode, pageSize) {
    if (mode === 1) return value * 16;
    if (mode === 2) return value * pageSize;
    return value;
  }

  function panByPixels(deltaPixels) {
    const geometry = mapGeometry();
    const span = state.viewEnd - state.viewStart;
    const addressDelta = deltaPixels / geometry.plotWidth * span;
    setView(state.viewStart + addressDelta, state.viewEnd + addressDelta);
  }

  elements.layerFilters.addEventListener("change", (event) => {
    const checkbox = event.target.closest("input[data-layer]");
    if (!checkbox) return;
    if (checkbox.checked) state.visibleLayers.add(checkbox.dataset.layer);
    else state.visibleLayers.delete(checkbox.dataset.layer);
    scheduleRender();
  });

  elements.semanticOnly.addEventListener("change", () => {
    state.semanticOnly = elements.semanticOnly.checked;
    scheduleRender();
  });

  elements.search.addEventListener("input", updateSearch);
  elements.search.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && state.orderedMatches.length) {
      event.preventDefault();
      selectObject(state.orderedMatches[0], true);
    }
  });

  elements.address.addEventListener("input", () => elements.address.setCustomValidity(""));
  elements.address.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      jumpToAddress(parseAddress(elements.address.value));
    }
  });

  elements.zoomIn.addEventListener("click", () => zoom(0.5));
  elements.zoomOut.addEventListener("click", () => zoom(2));
  elements.fullView.addEventListener("click", () => setView(0, state.rom.size));
  elements.closeDetails.addEventListener("click", () => clearDetails());

  elements.addressMap.addEventListener("wheel", (event) => {
    event.preventDefault();
    const geometry = mapGeometry();
    let deltaX = wheelPixels(event.deltaX, event.deltaMode, geometry.rect.width);
    let deltaY = wheelPixels(event.deltaY, event.deltaMode, geometry.rect.height);
    if (event.shiftKey && Math.abs(deltaX) < Math.abs(deltaY)) {
      deltaX = deltaY;
      deltaY = 0;
    }
    const anchor = addressAtClientX(event.clientX);
    if (event.ctrlKey) {
      zoom(Math.exp(deltaY * 0.01), anchor);
    } else if (Math.abs(deltaX) > Math.abs(deltaY)) {
      panByPixels(deltaX);
    } else if (deltaY) {
      zoom(Math.exp(deltaY * 0.0015), anchor);
    }
  }, {passive: false});

  elements.addressMap.addEventListener("gesturestart", (event) => {
    event.preventDefault();
    state.gestureScale = event.scale || 1;
  }, {passive: false});

  elements.addressMap.addEventListener("gesturechange", (event) => {
    event.preventDefault();
    const scale = event.scale || 1;
    const previous = state.gestureScale || scale;
    state.gestureScale = scale;
    zoom(previous / scale, addressAtClientX(event.clientX));
  }, {passive: false});

  elements.addressMap.addEventListener("gestureend", () => {
    state.gestureScale = null;
  });

  elements.addressMap.addEventListener("pointerdown", (event) => {
    const mark = event.target.closest(".mark[data-object-id]");
    if (mark) {
      selectObject(mark.dataset.objectId);
      return;
    }
    const geometry = mapGeometry();
    state.drag = {
      pointerId: event.pointerId,
      clientX: event.clientX,
      start: state.viewStart,
      end: state.viewEnd,
      plotWidth: geometry.plotWidth,
    };
    elements.addressMap.setPointerCapture(event.pointerId);
    elements.addressMap.classList.add("is-dragging");
  });

  elements.addressMap.addEventListener("pointermove", (event) => {
    const mark = event.target.closest(".mark[data-object-id]");
    if (mark && !state.drag) {
      const item = state.objectById.get(mark.dataset.objectId);
      if (item) showTooltip(item, event);
    } else {
      hideTooltip();
    }
    if (!state.drag || state.drag.pointerId !== event.pointerId) return;
    const span = state.drag.end - state.drag.start;
    const delta = (event.clientX - state.drag.clientX) / state.drag.plotWidth * span;
    setView(state.drag.start - delta, state.drag.end - delta);
  });

  function endMapDrag(event) {
    if (!state.drag || state.drag.pointerId !== event.pointerId) return;
    state.drag = null;
    elements.addressMap.classList.remove("is-dragging");
    if (elements.addressMap.hasPointerCapture(event.pointerId)) {
      elements.addressMap.releasePointerCapture(event.pointerId);
    }
  }

  elements.addressMap.addEventListener("pointerup", endMapDrag);
  elements.addressMap.addEventListener("pointercancel", endMapDrag);
  elements.addressMap.addEventListener("pointerleave", hideTooltip);

  function overviewAddress(event) {
    const rect = elements.overview.getBoundingClientRect();
    const fraction = clamp((event.clientX - rect.left) / rect.width, 0, 1);
    return fraction * state.rom.size;
  }

  function centerOverviewAt(address) {
    const span = state.viewEnd - state.viewStart;
    setView(address - span / 2, address + span / 2);
  }

  elements.overview.addEventListener("pointerdown", (event) => {
    state.overviewDrag = event.pointerId;
    elements.overview.setPointerCapture(event.pointerId);
    centerOverviewAt(overviewAddress(event));
  });
  elements.overview.addEventListener("pointermove", (event) => {
    if (state.overviewDrag === event.pointerId) {
      centerOverviewAt(overviewAddress(event));
    }
  });
  function endOverviewDrag(event) {
    if (state.overviewDrag !== event.pointerId) return;
    state.overviewDrag = null;
    if (elements.overview.hasPointerCapture(event.pointerId)) {
      elements.overview.releasePointerCapture(event.pointerId);
    }
  }
  elements.overview.addEventListener("pointerup", endOverviewDrag);
  elements.overview.addEventListener("pointercancel", endOverviewDrag);

  const architecture = window.RomAtlasArchitecture.create({
    atlas,
    showAddress(address) {
      showView("address");
      jumpToAddress(address, true);
    },
    selectRom(id) {
      const index = atlas.roms.findIndex((rom) => rom.id === id);
      if (index < 0 || index === state.romIndex) return;
      setupRom(index);
      updateHash(true);
    },
    updateHash,
  });

  const familyGroups = new Map();
  for (const [index, rom] of atlas.roms.entries()) {
    const option = document.createElement("option");
    const details = [rom.identity.submodel, rom.identity.model].filter(Boolean);
    option.value = String(index);
    option.textContent = [rom.id, ...(details.length ? details : [rom.label])].join(" \u2013 ");
    if (!rom.family) {
      elements.romPicker.append(option);
      continue;
    }
    let group = familyGroups.get(rom.family.key);
    if (!group) {
      group = document.createElement("optgroup");
      group.label = [rom.family.key, rom.family.fields.kind].filter(Boolean).join(" \u2013 ");
      familyGroups.set(rom.family.key, group);
      elements.romPicker.append(group);
    }
    group.append(option);
  }
  elements.romPickerLabel.hidden = false;
  elements.romPicker.addEventListener("change", () => {
    setupRom(Number(elements.romPicker.value));
    updateHash();
  });

  const tabs = [elements.viewAddress, elements.viewArchitecture];
  for (const tab of tabs) {
    tab.addEventListener("click", () => {
      showView(tab === elements.viewArchitecture ? "architecture" : "address");
    });
    tab.addEventListener("keydown", (event) => {
      if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
      event.preventDefault();
      const next = event.key === "Home" ? tabs[0]
        : event.key === "End" ? tabs[tabs.length - 1]
          : tabs[(tabs.indexOf(tab) + 1) % tabs.length];
      if (next.disabled) return;
      next.focus();
      next.click();
    });
  }
  window.addEventListener("popstate", restoreHash);

  const resizeObserver = new ResizeObserver(scheduleRender);
  resizeObserver.observe(elements.addressMap);
  resizeObserver.observe(elements.overview);
  const theme = window.matchMedia("(prefers-color-scheme: dark)");
  theme.addEventListener?.("change", scheduleRender);

  setupRom(0, true);
})();
