(() => {
  "use strict";

  const svgNS = "http://www.w3.org/2000/svg";
  const FLOW_KINDS = new Set(["data", "control"]);
  const CODE_KINDS = new Set(["function", "map", "axis", "rom"]);
  const DATA_KINDS = new Set(["signal", "register", "ram", "io"]);
  const KIND_ORDER = ["function", "map", "axis", "signal", "register", "ram", "io", "rom", "other"];
  const KIND_LABELS = {
    function: "Function",
    map: "Map",
    axis: "Axis",
    signal: "Signal",
    register: "Register",
    ram: "Unreviewed RAM",
    io: "Unreviewed I/O",
    rom: "Unreviewed ROM",
    other: "Unreviewed address",
  };
  const KIND_PLURALS = {
    function: "functions",
    map: "maps",
    axis: "axes",
    signal: "signals",
    register: "registers",
    ram: "RAM cells",
    io: "I/O registers",
    rom: "ROM items",
    other: "other",
  };
  const SIGN_GLYPHS = {positive: "+", negative: "-", none: "~", mixed: "+/-"};
  const SIGN_PHRASES = {
    positive: "increases",
    negative: "decreases",
    none: "has no established signed effect on",
    mixed: "has path-dependent effects on",
  };
  const MODE_LABELS = {layout: "Layout"};
  const TRACE_DEPTH = 16;
  // Initial scale of the detailed views: a wide diagram opens at a readable
  // scale on its input side, and Fit shows all of it.
  const READABLE_SCALE = 0.62;
  const NEIGHBOR_LIMIT = 28;
  const LIST_LIMIT = 12;

  function clamp(value, minimum, maximum) {
    return Math.max(minimum, Math.min(maximum, value));
  }

  function hex(value) {
    const digits = value > 0xFFFFFF ? 8 : 6;
    return `0x${value.toString(16).toUpperCase().padStart(digits, "0")}`;
  }

  function truncate(text, limit) {
    const value = String(text || "");
    return value.length > limit ? `${value.slice(0, Math.max(1, limit - 3))}...` : value;
  }

  function firstSentence(text, limit = 180) {
    const value = String(text || "").trim();
    const sentence = value.split(/(?<=[.!?])\s/)[0] || "";
    return truncate(sentence, limit);
  }

  function svg(name, attributes = {}, text = null) {
    const node = document.createElementNS(svgNS, name);
    for (const [key, value] of Object.entries(attributes)) {
      if (value !== null && value !== undefined && value !== false) {
        node.setAttribute(key, String(value));
      }
    }
    if (text !== null) node.textContent = text;
    return node;
  }

  function html(tag, attributes = {}, ...children) {
    const node = document.createElement(tag);
    for (const [key, value] of Object.entries(attributes)) {
      if (value === null || value === undefined || value === false) continue;
      if (key === "className") node.className = value;
      else if (key === "text") node.textContent = value;
      else if (key.startsWith("on")) node.addEventListener(key.slice(2), value);
      else node.setAttribute(key, String(value));
    }
    for (const child of children.flat()) {
      if (child === null || child === undefined || child === false) continue;
      node.append(child instanceof Node ? child : document.createTextNode(String(child)));
    }
    return node;
  }

  function pushTo(map, key, value) {
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(value);
  }

  function prepare(raw) {
    const nodes = raw.nodes;
    const count = nodes.length;
    const nodeById = new Map(nodes.map((node, index) => [node.id, index]));
    const relationOrigins = Array.from({length: count}, () => new Map());
    for (const edge of raw.edgeEvidence || []) {
      for (const id of [edge.from, edge.to]) {
        const index = nodeById.get(id);
        if (index === undefined) continue;
        for (const origin of edge.origins) {
          const counts = relationOrigins[index];
          counts.set(origin, (counts.get(origin) || 0) + 1);
        }
      }
    }
    const inFlow = Array.from({length: count}, () => []);
    const outFlow = Array.from({length: count}, () => []);
    const inOther = Array.from({length: count}, () => []);
    const outOther = Array.from({length: count}, () => []);
    for (const [source, target, kindIndex, roleIndex] of raw.edges) {
      const kind = raw.edgeKinds[kindIndex];
      const role = raw.edgeRoles[roleIndex];
      if (FLOW_KINDS.has(kind)) {
        outFlow[source].push({node: target, kind, role});
        inFlow[target].push({node: source, kind, role});
      } else {
        outOther[source].push({node: target, kind, role});
        inOther[target].push({node: source, kind, role});
      }
    }
    const blockCounts = new Map();
    for (const block of raw.blocks) {
      const counts = {};
      for (const member of block.members) {
        const kind = nodes[member].kind;
        counts[kind] = (counts[kind] || 0) + 1;
      }
      blockCounts.set(block.id, counts);
    }
    const chainsByNode = new Map();
    const chainBlocks = raw.chains.map(() => new Set());
    raw.chains.forEach((chain, chainIndex) => {
      const add = (node) => {
        if (!chainsByNode.has(node)) chainsByNode.set(node, new Set());
        chainsByNode.get(node).add(chainIndex);
        if (nodes[node].block) chainBlocks[chainIndex].add(nodes[node].block);
      };
      for (const step of chain.steps) {
        add(step.from);
        add(step.to);
        step.via.forEach(add);
      }
    });
    const endpointsByNode = new Map();
    for (const endpoint of raw.endpoints) {
      for (const node of [...endpoint.registers, ...endpoint.functions]) {
        pushTo(endpointsByNode, node, endpoint);
      }
    }
    const flowsOut = new Map();
    const flowsIn = new Map();
    for (const flow of raw.flows) {
      pushTo(flowsOut, flow.from, flow);
      pushTo(flowsIn, flow.to, flow);
    }
    // Shared kernels and the scheduler serve every block; a derived path
    // through them does not describe a data flow of the calling blocks.
    const generic = new Set(raw.blocks.filter((block) => block.generic).map((block) => block.id));
    const relays = nodes.map((node) => !(node.kind === "function" && generic.has(node.block)));
    return {
      raw,
      nodes,
      relays,
      inFlow,
      outFlow,
      inOther,
      outOther,
      nodeById,
      relationOrigins,
      blockById: new Map(raw.blocks.map((block) => [block.id, block])),
      stageById: new Map(raw.stages.map((stage) => [stage.id, stage])),
      endpointById: new Map(raw.endpoints.map((endpoint) => [endpoint.id, endpoint])),
      chainById: new Map(raw.chains.map((chain, index) => [chain.id, index])),
      blockCounts,
      chainsByNode,
      chainBlocks,
      endpointsByNode,
      flowsOut,
      flowsIn,
      searchText: nodes.map((node) => [
        node.label,
        node.addr,
        node.id,
        node.kind,
        node.block || "",
        node.role || "",
        node.units || "",
        node.text || "",
        node.meta?.binding?.meaning || "",
        node.meta?.binding?.name || "",
        node.meta?.binding?.reference || "",
        ...(node.meta?.binding?.former || []),
        ...(node.meta?.binding?.symbols || []).map((symbol) => symbol.name || ""),
      ].join(" ").toLowerCase()),
    };
  }

  function prepareBinding(binding, model) {
    const reverse = new Map();
    for (const [index, node] of model.nodes.entries()) {
      if (!reverse.has(node.addr)) reverse.set(node.addr, index);
    }
    return {...binding, reverse};
  }

  function bezier(a, b) {
    const ay = a.y + a.h / 2;
    const by = b.y + b.h / 2;
    let points;
    if (b.x >= a.x + a.w - 1) {
      const x1 = a.x + a.w;
      const x2 = b.x;
      const dx = Math.max(26, (x2 - x1) / 2);
      points = [[x1, ay], [x1 + dx, ay], [x2 - dx, by], [x2, by]];
    } else if (b.x + b.w <= a.x + 1) {
      const x1 = a.x;
      const x2 = b.x + b.w;
      const dx = Math.max(26, (x1 - x2) / 2);
      points = [[x1, ay], [x1 - dx, ay], [x2 + dx, by], [x2, by]];
    } else {
      const x1 = a.x + a.w;
      const x2 = b.x + b.w;
      const bulge = 34 + Math.min(140, Math.abs(by - ay) * 0.22);
      const xr = Math.max(x1, x2) + bulge;
      points = [[x1, ay], [xr, ay], [xr, by], [x2, by]];
    }
    const [p0, p1, p2, p3] = points;
    const mid = [
      (p0[0] + 3 * p1[0] + 3 * p2[0] + p3[0]) / 8,
      (p0[1] + 3 * p1[1] + 3 * p2[1] + p3[1]) / 8,
    ];
    const d = `M${p0[0].toFixed(1)},${p0[1].toFixed(1)} C${p1[0].toFixed(1)},${p1[1].toFixed(1)} ${p2[0].toFixed(1)},${p2[1].toFixed(1)} ${p3[0].toFixed(1)},${p3[1].toFixed(1)}`;
    return {d, mid};
  }

  // Longest-path layering with barycentric ordering; tall layers wrap into
  // several columns so that a wide block stays readable.
  function layered(items, links, options = {}) {
    const {
      first = new Set(),
      last = new Set(),
      columnGap = 88,
      rowGap = 14,
      maxPerColumn = 14,
    } = options;
    const index = new Map(items.map((item, position) => [item.key, position]));
    const successors = items.map(() => new Set());
    const predecessors = items.map(() => new Set());
    for (const link of links) {
      const source = index.get(link.from);
      const target = index.get(link.to);
      if (source === undefined || target === undefined || source === target) continue;
      if (first.has(link.to) || last.has(link.from)) continue;
      successors[source].add(target);
      predecessors[target].add(source);
    }
    const color = new Uint8Array(items.length);
    const back = new Set();
    for (let start = 0; start < items.length; start += 1) {
      if (color[start]) continue;
      const stack = [[start, [...successors[start]], 0]];
      color[start] = 1;
      while (stack.length) {
        const frame = stack[stack.length - 1];
        if (frame[2] >= frame[1].length) {
          color[frame[0]] = 2;
          stack.pop();
          continue;
        }
        const next = frame[1][frame[2]];
        frame[2] += 1;
        if (color[next] === 1) back.add(`${frame[0]}>${next}`);
        else if (!color[next]) {
          color[next] = 1;
          stack.push([next, [...successors[next]], 0]);
        }
      }
    }
    const layer = new Int32Array(items.length);
    const indegree = new Int32Array(items.length);
    const forward = items.map(() => []);
    successors.forEach((targets, source) => {
      for (const target of targets) {
        if (back.has(`${source}>${target}`)) continue;
        forward[source].push(target);
        indegree[target] += 1;
      }
    });
    const queue = [];
    indegree.forEach((value, position) => {
      if (!value) queue.push(position);
    });
    while (queue.length) {
      const node = queue.shift();
      for (const target of forward[node]) {
        layer[target] = Math.max(layer[target], layer[node] + 1);
        indegree[target] -= 1;
        if (!indegree[target]) queue.push(target);
      }
    }
    items.forEach((item, position) => {
      if (first.has(item.key)) layer[position] = 0;
      else if (first.size) layer[position] = Math.max(1, layer[position]);
    });
    let maximum = 0;
    items.forEach((item, position) => {
      if (!last.has(item.key)) maximum = Math.max(maximum, layer[position]);
    });
    items.forEach((item, position) => {
      if (last.has(item.key)) layer[position] = maximum + 1;
    });
    const layers = [];
    items.forEach((item, position) => {
      (layers[layer[position]] ||= []).push(position);
    });
    const compact = layers.filter(Boolean);
    const order = new Float64Array(items.length);
    compact.forEach((members) => members.forEach((node, position) => {
      order[node] = position;
    }));
    const sweep = (members, neighbors) => {
      const keyed = members.map((node) => {
        const values = [...neighbors[node]].map((other) => order[other]);
        const value = values.length
          ? values.reduce((sum, item) => sum + item, 0) / values.length
          : order[node];
        return [value, order[node], node];
      });
      keyed.sort((left, right) => left[0] - right[0] || left[1] - right[1]);
      keyed.forEach((entry, position) => {
        order[entry[2]] = position;
      });
      members.sort((left, right) => order[left] - order[right]);
    };
    for (let pass = 0; pass < 4; pass += 1) {
      for (let position = 1; position < compact.length; position += 1) {
        sweep(compact[position], predecessors);
      }
      for (let position = compact.length - 2; position >= 0; position -= 1) {
        sweep(compact[position], successors);
      }
    }
    const columns = [];
    for (const members of compact) {
      for (let offset = 0; offset < members.length; offset += maxPerColumn) {
        columns.push(members.slice(offset, offset + maxPerColumn));
      }
    }
    const heights = columns.map((members) => members.reduce(
      (sum, node, position) => sum + items[node].height + (position ? rowGap : 0),
      0,
    ));
    const height = Math.max(1, ...heights);
    const boxes = new Map();
    let x = 0;
    columns.forEach((members, column) => {
      const width = Math.max(...members.map((node) => items[node].width));
      let y = (height - heights[column]) / 2;
      for (const node of members) {
        const item = items[node];
        boxes.set(item.key, {x: x + (width - item.width) / 2, y, w: item.width, h: item.height});
        y += item.height + rowGap;
      }
      x += width + columnGap;
    });
    return {boxes, width: Math.max(1, x - columnGap), height};
  }

  function create(bridge) {
    const elements = {
      view: document.getElementById("arch-view"),
      crumbs: document.getElementById("arch-crumbs"),
      search: document.getElementById("arch-search"),
      results: document.getElementById("arch-results"),
      banner: document.getElementById("arch-banner"),
      chains: document.getElementById("arch-chains"),
      title: document.getElementById("arch-title"),
      subtitle: document.getElementById("arch-subtitle"),
      options: document.getElementById("arch-options"),
      support: document.getElementById("arch-support"),
      flowLimit: document.getElementById("arch-flow-limit"),
      flowLimitValue: document.getElementById("arch-flow-limit-value"),
      canvas: document.getElementById("arch-canvas"),
      legend: document.getElementById("arch-legend"),
      table: document.getElementById("arch-table"),
      details: document.getElementById("arch-details"),
      zoomIn: document.getElementById("arch-zoom-in"),
      zoomOut: document.getElementById("arch-zoom-out"),
      fit: document.getElementById("arch-fit"),
      tooltip: document.getElementById("tooltip"),
    };
    const models = new Map();
    const state = {
      active: false,
      rom: null,
      model: null,
      binding: null,
      route: {type: "system"},
      selection: null,
      transform: {x: 0, y: 0, k: 1},
      content: {width: 1, height: 1},
      fitPending: true,
      support: false,
      flowLimit: Number(elements.flowLimit.value) || 60,
      hoverChain: null,
      sceneLinks: new Map(),
      results: [],
      resultIndex: -1,
      pointers: new Map(),
      drag: null,
      pinch: null,
      viewport: null,
      tips: new Map(),
      framePending: false,
    };

    function model() {
      return state.model;
    }

    function node(index) {
      return state.model.nodes[index];
    }

    function blockName(blockId) {
      const block = blockId && state.model.blockById.get(blockId);
      return block ? block.name : "Unassigned";
    }

    function addressInfo(index) {
      const item = node(index);
      const value = Number.parseInt(item.addr, 16);
      const reference = hex(value);
      const inFlash = value < state.rom.size && CODE_KINDS.has(item.kind);
      return {text: reference, reference, jump: inFlash ? value : null, status: "bound"};
    }

    function nodeTitle(index) {
      return node(index).label;
    }

    function nodeSubtitle(index) {
      const item = node(index);
      const info = addressInfo(index);
      const block = item.block ? blockName(item.block) : KIND_LABELS[item.kind];
      return `${info.relocated ? info.text.split(",")[0] : info.reference} | ${block}`;
    }

    // Selection and routing.

    function selectionKey() {
      return state.selection;
    }

    function select(key, updateLocation = true) {
      state.selection = key;
      renderDetails();
      scheduleRender();
      if (updateLocation) bridge.updateHash(false);
    }

    function navigate(route, selection = null, push = true) {
      if (routeKey(route) === routeKey(state.route)) {
        if (selection !== state.selection) select(selection);
        hideResults();
        return;
      }
      state.route = route;
      state.selection = selection;
      state.fitPending = true;
      hideResults();
      renderChrome();
      renderDetails();
      scheduleRender();
      bridge.updateHash(push);
    }

    function routeKey(route) {
      if (route.type === "system") return "system";
      if (route.type === "trace") return `trace:${route.direction}:${state.model.nodes[route.node].id}`;
      if (route.type === "node") return `node:${state.model.nodes[route.node].id}`;
      return `${route.type}:${route.id}`;
    }

    function parseRoute(text) {
      if (!text || text === "system") return {type: "system"};
      const [type, ...rest] = text.split(":");
      const value = rest.join(":");
      if (type === "block" && state.model.blockById.has(value)) return {type, id: value};
      if (type === "chain" && state.model.chainById.has(value)) return {type, id: value};
      if (type === "node" && state.model.nodeById.has(value)) {
        return {type, node: state.model.nodeById.get(value)};
      }
      if (type === "trace") {
        const [direction, ...idParts] = rest;
        const nodeId = idParts.join(":");
        if ((direction === "down" || direction === "up") && state.model.nodeById.has(nodeId)) {
          return {type, direction, node: state.model.nodeById.get(nodeId)};
        }
      }
      return {type: "system"};
    }

    function encodeSelection(key) {
      if (!key) return null;
      const [type, ...rest] = key.split(":");
      if (type === "node") return `node:${state.model.nodes[Number(rest[0])].id}`;
      return key;
    }

    function decodeSelection(text) {
      if (!text) return null;
      const [type, ...rest] = text.split(":");
      const value = rest.join(":");
      if (type === "node") {
        const index = state.model.nodeById.get(value);
        return index === undefined ? null : `node:${index}`;
      }
      if (type === "block" && state.model.blockById.has(value)) return text;
      if (type === "endpoint" && state.model.endpointById.has(value)) return text;
      if (type === "chain" && state.model.chainById.has(value)) return text;
      if (type === "unavailable" && state.model.raw.chainAvailability?.some((chain) => chain.id === value)) return text;
      if (type === "flow" || type === "step" || type === "edge" || type === "ext") return text;
      return null;
    }

    // Chrome: banner, breadcrumbs, chain list, options.

    function renderChrome() {
      const binding = state.binding;
      const raw = state.model.raw;
      elements.banner.replaceChildren();
      elements.banner.dataset.mode = binding.mode;
      const lead = html("strong", {text: `${MODE_LABELS[binding.mode]}: `});
      const text = `${raw.layout}: ${raw.nodes.length.toLocaleString()} bound symbols for ${state.rom.id}. `
        + "Calculation chains require every binding for this image.";
      elements.banner.append(lead, text);

      elements.crumbs.replaceChildren();
      const crumbs = [["System map", {type: "system"}]];
      const route = state.route;
      if (route.type === "block") {
        const block = state.model.blockById.get(route.id);
        crumbs.push([state.model.stageById.get(block.stage)?.name || block.stage, null]);
        crumbs.push([block.name, route]);
      } else if (route.type === "chain") {
        crumbs.push(["Calculation chains", null]);
        crumbs.push([raw.chains[state.model.chainById.get(route.id)].name, route]);
      } else if (route.type === "node" || route.type === "trace") {
        const item = node(route.node);
        if (item.block) crumbs.push([blockName(item.block), {type: "block", id: item.block}]);
        crumbs.push([truncate(item.label, 48), {type: "node", node: route.node}]);
        if (route.type === "trace") {
          crumbs.push([route.direction === "down" ? "Trace to actuators" : "Trace from sensors", route]);
        }
      }
      crumbs.forEach(([label, target], position) => {
        const current = position === crumbs.length - 1;
        if (position) elements.crumbs.append(html("span", {className: "arch-crumb-separator", "aria-hidden": "true", text: "/"}));
        if (target && !current) {
          elements.crumbs.append(html("button", {
            type: "button",
            className: "arch-crumb",
            text: label,
            onclick: () => navigate(target),
          }));
        } else {
          elements.crumbs.append(html("span", {
            className: current ? "arch-crumb is-current" : "arch-crumb is-plain",
            "aria-current": current ? "page" : null,
            text: label,
          }));
        }
      });

      elements.chains.replaceChildren();
      if (raw.chains.length) {
        elements.chains.append(html("span", {className: "arch-chains-label", text: "Calculation chains"}));
        raw.chains.forEach((chain, chainIndex) => {
          const active = route.type === "chain" && route.id === chain.id;
          elements.chains.append(html("button", {
            type: "button",
            className: `arch-chain-chip${active ? " is-active" : ""}`,
            "aria-pressed": active ? "true" : "false",
            title: chain.summary,
            text: chain.name,
            onclick: () => navigate({type: "chain", id: chain.id}, `chain:${chain.id}`),
            onmouseenter: () => {
              state.hoverChain = chainIndex;
              if (state.route.type === "system") scheduleRender();
            },
            onmouseleave: () => {
              state.hoverChain = null;
              if (state.route.type === "system") scheduleRender();
            },
          }));
        });
      } else {
        elements.chains.append(html("span", {
          className: "arch-chains-label",
          text: "No complete calculation chains are bound on this layout.",
        }));
      }
      for (const chain of raw.chainAvailability || []) {
        if (state.model.chainById.has(chain.id)) continue;
        elements.chains.append(html("button", {
          type: "button", className: "arch-chain-chip",
          text: `${chain.name}: ${chain.bound}/${chain.total}`,
          title: chain.missing.map((binding) => {
            const status = binding.statuses.find((item) => item.layout === raw.layout);
            return `${binding.meaning}: ${status?.state || "unknown"}`;
          }).join("\n"),
          onclick: () => {
            state.selection = `unavailable:${chain.id}`;
            renderDetails();
            bridge.updateHash(true);
          },
        }));
      }
      elements.options.hidden = route.type !== "system";
    }

    // Scenes.

    function systemScene() {
      const raw = state.model.raw;
      const flowStages = raw.stages.filter((stage) => stage.lane === "flow");
      const supportStages = raw.stages.filter((stage) => stage.lane !== "flow");
      const blockWidth = 188;
      const blockHeight = 48;
      const endpointWidth = 166;
      const endpointHeight = 42;
      const gap = 10;
      const columnGap = 76;
      const headerHeight = 34;
      const boxes = new Map();
      const columns = [];
      let x = 0;
      const inputs = raw.endpoints.filter((endpoint) => endpoint.direction === "input");
      const outputs = raw.endpoints.filter((endpoint) => endpoint.direction !== "input");
      columns.push({label: "Sensors and inputs", width: endpointWidth, items: inputs.map((endpoint) => ({key: `endpoint:${endpoint.id}`, h: endpointHeight}))});
      for (const stage of flowStages) {
        const blocks = raw.blocks.filter((block) => block.stage === stage.id);
        columns.push({label: stage.name, stage, width: blockWidth, items: blocks.map((block) => ({key: `block:${block.id}`, h: blockHeight}))});
      }
      columns.push({label: "Actuators and links", width: endpointWidth, items: outputs.map((endpoint) => ({key: `endpoint:${endpoint.id}`, h: endpointHeight}))});
      let tallest = 0;
      for (const column of columns) {
        column.x = x;
        let y = headerHeight;
        for (const item of column.items) {
          boxes.set(item.key, {x, y, w: column.width, h: item.h});
          y += item.h + gap;
        }
        column.bottom = y;
        tallest = Math.max(tallest, y);
        x += column.width + columnGap;
      }
      const flowWidth = x - columnGap;
      const supportTop = tallest + 46;
      const supportLeft = columns[1] ? columns[1].x : 0;
      const supportWidth = Math.max(blockWidth, flowWidth - supportLeft);
      const perRow = Math.max(1, Math.floor((supportWidth + gap) / (blockWidth + gap)));
      const supportRows = [];
      let y = supportTop + 30;
      for (const stage of supportStages) {
        const blocks = raw.blocks.filter((block) => block.stage === stage.id);
        const rowTop = y;
        blocks.forEach((block, position) => {
          const column = position % perRow;
          const row = Math.floor(position / perRow);
          boxes.set(`block:${block.id}`, {
            x: supportLeft + column * (blockWidth + gap),
            y: rowTop + row * (blockHeight + gap),
            w: blockWidth,
            h: blockHeight,
          });
        });
        const rows = Math.max(1, Math.ceil(blocks.length / perRow));
        supportRows.push({stage, top: rowTop, height: rows * (blockHeight + gap) - gap});
        y = rowTop + rows * (blockHeight + gap) + 10;
      }
      const height = supportStages.length ? y : tallest;

      const supportIds = new Set(raw.blocks.filter((block) => {
        const stage = state.model.stageById.get(block.stage);
        return stage && stage.lane !== "flow";
      }).map((block) => block.id));
      const selected = state.selection || "";
      const selectedBlock = selected.startsWith("block:") ? selected.slice(6) : null;
      const selectedEndpoint = selected.startsWith("endpoint:") ? state.model.endpointById.get(selected.slice(9)) : null;
      const focusBlock = selectedBlock || selectedEndpoint?.block || null;
      const chainBlocks = state.hoverChain !== null ? state.model.chainBlocks[state.hoverChain] : null;

      const primary = raw.flows
        .filter((flow) => !supportIds.has(flow.from) && !supportIds.has(flow.to))
        .sort((left, right) => right.weight - left.weight)
        .slice(0, state.flowLimit);
      const secondary = state.support
        ? raw.flows
          .filter((flow) => supportIds.has(flow.from) || supportIds.has(flow.to))
          .sort((left, right) => right.weight - left.weight)
          .slice(0, state.flowLimit)
        : [];
      const visible = new Set([...primary, ...secondary]);
      if (focusBlock) {
        for (const flow of raw.flows) {
          if (flow.from === focusBlock || flow.to === focusBlock) visible.add(flow);
        }
      }
      if (selected.startsWith("flow:")) {
        const [from, to] = selected.slice(5).split(">");
        const flow = raw.flows.find((item) => item.from === from && item.to === to);
        if (flow) visible.add(flow);
      }
      const maximum = Math.max(1, ...raw.flows.map((flow) => flow.weight));

      function draw(group) {
        const layers = {
          bands: svg("g", {class: "arch-bands"}),
          flows: svg("g", {class: "arch-flows"}),
          links: svg("g", {class: "arch-links"}),
          boxes: svg("g", {class: "arch-boxes"}),
        };
        Object.values(layers).forEach((layer) => group.append(layer));
        for (const column of columns) {
          layers.bands.append(svg("text", {x: column.x, y: 14, class: "arch-column-label"}, column.label.toUpperCase()));
          if (column.stage) {
            layers.bands.append(svg("text", {x: column.x, y: 27, class: "arch-column-sub"}, truncate(column.stage.summary, 34)));
          }
        }
        if (supportStages.length) {
          layers.bands.append(svg("rect", {
            x: -16,
            y: supportTop,
            width: flowWidth + 32,
            height: height - supportTop + 8,
            rx: 10,
            class: "arch-support-band",
          }));
          layers.bands.append(svg("text", {x: 0, y: supportTop + 20, class: "arch-column-label"}, "SUPPORT SYSTEMS"));
          for (const row of supportRows) {
            layers.bands.append(svg("text", {x: 0, y: row.top + 20, class: "arch-row-label"}, row.stage.name));
            layers.bands.append(svg("text", {x: 0, y: row.top + 35, class: "arch-column-sub"}, truncate(row.stage.summary, 30)));
          }
        }
        const drawn = [...visible].sort((left, right) => left.weight - right.weight);
        for (const flow of drawn) {
          const a = boxes.get(`block:${flow.from}`);
          const b = boxes.get(`block:${flow.to}`);
          if (!a || !b) continue;
          const key = `flow:${flow.from}>${flow.to}`;
          const {d} = bezier(a, b);
          const touches = focusBlock && (flow.from === focusBlock || flow.to === focusBlock);
          const inChain = chainBlocks && chainBlocks.has(flow.from) && chainBlocks.has(flow.to);
          const classes = ["arch-flow"];
          if (supportIds.has(flow.from) || supportIds.has(flow.to)) classes.push("is-support");
          if (selected === key) classes.push("is-selected");
          else if (touches || inChain) classes.push("is-hot");
          else if (focusBlock || chainBlocks) classes.push("is-dimmed");
          const width = 1 + 5 * Math.sqrt(flow.weight / maximum);
          layers.flows.append(svg("path", {d, class: "arch-flow-hit", "data-key": key, "stroke-width": Math.max(10, width + 6)}));
          layers.flows.append(svg("path", {d, class: classes.join(" "), "stroke-width": width.toFixed(2), "marker-end": classes.includes("is-hot") || classes.includes("is-selected") ? "url(#arch-arrow-hot)" : "url(#arch-arrow)"}));
          state.tips.set(key, () => {
            const carriers = flow.carriers.slice(0, 6).map((carrier) => node(carrier).label);
            return [`${blockName(flow.from)} -> ${blockName(flow.to)}`, `${flow.weight} relations; ${carriers.join("; ")}${flow.carriers.length > 6 ? "; ..." : ""}`];
          });
        }
        for (const endpoint of raw.endpoints) {
          const a = boxes.get(`endpoint:${endpoint.id}`);
          const b = boxes.get(`block:${endpoint.block}`);
          if (!a || !b) continue;
          const {d} = endpoint.direction === "input" ? bezier(a, b) : bezier(b, a);
          const hot = focusBlock === endpoint.block || selected === `endpoint:${endpoint.id}`;
          layers.links.append(svg("path", {
            d,
            class: `arch-link${endpoint.direction === "bidirectional" ? " is-bidirectional" : ""}${hot ? " is-hot" : focusBlock ? " is-dimmed" : ""}`,
            "marker-end": hot ? "url(#arch-arrow-hot)" : "url(#arch-arrow)",
          }));
        }
        for (const endpoint of raw.endpoints) {
          const box = boxes.get(`endpoint:${endpoint.id}`);
          const key = `endpoint:${endpoint.id}`;
          const related = focusBlock === endpoint.block;
          drawBox(layers.boxes, box, {
            key,
            kind: `endpoint-${endpoint.direction}`,
            title: endpoint.name,
            subtitle: endpoint.peripheral,
            selected: selected === key,
            dimmed: Boolean(focusBlock) && !related && selected !== key,
            label: `${endpoint.name}, ${endpoint.direction} endpoint`,
          });
          state.tips.set(key, () => [endpoint.name, firstSentence(endpoint.summary)]);
        }
        for (const block of raw.blocks) {
          const box = boxes.get(`block:${block.id}`);
          if (!box) continue;
          const key = `block:${block.id}`;
          const counts = state.model.blockCounts.get(block.id) || {};
          const subtitle = [
            counts.function ? `${counts.function} fn` : "",
            counts.map ? `${counts.map} maps` : "",
            (counts.signal || 0) + (counts.register || 0) ? `${(counts.signal || 0) + (counts.register || 0)} signals` : "",
          ].filter(Boolean).join(" | ");
          const neighbor = focusBlock && raw.flows.some((flow) => (
            (flow.from === focusBlock && flow.to === block.id) || (flow.to === focusBlock && flow.from === block.id)
          ));
          const inChain = chainBlocks && chainBlocks.has(block.id);
          drawBox(layers.boxes, box, {
            key,
            kind: `block${block.generic ? " is-generic" : ""}${supportIds.has(block.id) ? " is-support" : ""}`,
            title: block.name,
            subtitle: subtitle || (block.generic ? "shared kernels" : ""),
            selected: selected === key,
            related: neighbor || inChain,
            dimmed: (focusBlock && block.id !== focusBlock && !neighbor) || (chainBlocks && !inChain),
            label: `${block.name} block`,
          });
          state.tips.set(key, () => [block.name, firstSentence(block.summary)]);
        }
      }

      return {
        width: flowWidth,
        height,
        draw,
        title: `${raw.id} system map`,
        subtitle: `${raw.blocks.length} blocks in ${raw.stages.length} stages; ${raw.endpoints.length} peripheral endpoints; `
          + `${visible.size} of ${raw.flows.length} inter-block flows drawn. Click a block to trace its flows; double-click to open it.`,
        legend: [
          ["swatch block", "Functional block"],
          ["swatch endpoint-input", "Sensor or input peripheral"],
          ["swatch endpoint-output", "Actuator or output peripheral"],
          ["line", "Data or control flow; width follows the relation count"],
        ],
      };
    }

    function blockScene(blockId) {
      const raw = state.model.raw;
      const block = state.model.blockById.get(blockId);
      const members = new Set(block.members);
      const functions = block.members.filter((index) => node(index).kind === "function");
      const internal = new Map();
      const incoming = new Map();
      const outgoing = new Map();
      const mapsOf = new Map();
      const add = (map, key, carrier) => {
        if (!map.has(key)) map.set(key, new Set());
        if (carrier !== null) map.get(key).add(carrier);
      };
      const ownerKey = (index) => {
        const owner = node(index).block;
        return owner ? `ext:${owner}` : "ext:unassigned";
      };
      for (const fn of functions) {
        const maps = [];
        for (const entry of state.model.inFlow[fn]) {
          const source = node(entry.node);
          if (source.kind === "map" || source.kind === "axis") {
            maps.push(entry.node);
            continue;
          }
          if (source.kind === "function") {
            if (members.has(entry.node)) add(internal, `${entry.node}>${fn}`, null);
            else add(incoming, `${ownerKey(entry.node)}>${fn}`, null);
            continue;
          }
          const writers = state.model.inFlow[entry.node].filter((writer) => node(writer.node).kind === "function");
          if (!writers.length) {
            const owner = source.block && source.block !== blockId ? `ext:${source.block}` : "ext:unassigned";
            add(incoming, `${owner}>${fn}`, entry.node);
            continue;
          }
          for (const writer of writers) {
            if (writer.node === fn) continue;
            if (members.has(writer.node)) add(internal, `${writer.node}>${fn}`, entry.node);
            else add(incoming, `${ownerKey(writer.node)}>${fn}`, entry.node);
          }
        }
        mapsOf.set(fn, maps.sort((left, right) => node(left).label.localeCompare(node(right).label)));
        for (const entry of state.model.outFlow[fn]) {
          const target = node(entry.node);
          if (target.kind === "function") {
            if (!members.has(entry.node)) add(outgoing, `${fn}>${ownerKey(entry.node)}`, null);
            continue;
          }
          const endpoints = state.model.endpointsByNode.get(entry.node) || [];
          for (const endpoint of endpoints) {
            if (endpoint.direction !== "input") add(outgoing, `${fn}>endpoint:${endpoint.id}`, entry.node);
          }
          for (const reader of state.model.outFlow[entry.node]) {
            if (node(reader.node).kind !== "function" || members.has(reader.node)) continue;
            add(outgoing, `${fn}>${ownerKey(reader.node)}`, entry.node);
          }
        }
      }
      const external = new Set();
      for (const key of incoming.keys()) external.add(key.split(">")[0]);
      const downstream = new Set();
      for (const key of outgoing.keys()) downstream.add(key.split(">")[1]);
      const upstreamKeys = [...external].map((key) => `in:${key}`);
      const downstreamKeys = [...downstream].map((key) => `out:${key}`);
      const itemFor = (key) => {
        if (key.startsWith("in:") || key.startsWith("out:")) return {key, width: 188, height: 44};
        const maps = mapsOf.get(Number(key)) || [];
        return {key, width: 224, height: 46 + 15 * Math.min(4, maps.length) + (maps.length > 4 ? 15 : 0)};
      };
      const items = [
        ...upstreamKeys.map(itemFor),
        ...functions.map((fn) => itemFor(String(fn))),
        ...downstreamKeys.map(itemFor),
      ];
      const links = [];
      for (const [key, carriers] of internal) {
        const [from, to] = key.split(">");
        links.push({from, to, carriers, kind: "internal", key: `edge:${from}>${to}`});
      }
      for (const [key, carriers] of incoming) {
        const [from, to] = key.split(">");
        links.push({from: `in:${from}`, to, carriers, kind: "incoming", key: `edge:in:${from}>${to}`});
      }
      for (const [key, carriers] of outgoing) {
        const [from, to] = key.split(">");
        links.push({from, to: `out:${to}`, carriers, kind: "outgoing", key: `edge:${from}>out:${to}`});
      }
      const layout = layered(items, links, {
        first: new Set(upstreamKeys),
        last: new Set(downstreamKeys),
        maxPerColumn: 12,
        columnGap: 76,
      });
      state.sceneLinks = new Map(links.map((link) => [link.key, link]));
      const selected = state.selection || "";
      const selectedNode = selected.startsWith("node:") ? String(selected.slice(5)) : null;

      function externalLabel(key) {
        const target = key.replace(/^(in|out):/, "");
        if (target === "ext:unassigned") return ["No reviewed writer", "unassigned or unreviewed code"];
        if (target.startsWith("endpoint:")) {
          const endpoint = state.model.endpointById.get(target.slice(9));
          return [endpoint.name, endpoint.peripheral];
        }
        const other = state.model.blockById.get(target.slice(4));
        return [other ? other.name : target, other ? state.model.stageById.get(other.stage)?.name || "" : ""];
      }

      function draw(group) {
        const edgeLayer = svg("g", {class: "arch-flows"});
        const boxLayer = svg("g", {class: "arch-boxes"});
        group.append(edgeLayer, boxLayer);
        const maximum = Math.max(1, ...links.map((link) => link.carriers.size || 1));
        for (const link of links) {
          const a = layout.boxes.get(link.from);
          const b = layout.boxes.get(link.to);
          if (!a || !b) continue;
          const {d} = bezier(a, b);
          const touches = selectedNode && (link.from === selectedNode || link.to === selectedNode);
          const classes = ["arch-flow", `is-${link.kind}`];
          if (selected === link.key) classes.push("is-selected");
          else if (touches) classes.push("is-hot");
          else if (selectedNode) classes.push("is-dimmed");
          const width = 1 + 3.5 * Math.sqrt((link.carriers.size || 1) / maximum);
          edgeLayer.append(svg("path", {d, class: "arch-flow-hit", "data-key": link.key, "stroke-width": Math.max(10, width + 6)}));
          edgeLayer.append(svg("path", {d, class: classes.join(" "), "stroke-width": width.toFixed(2), "marker-end": touches || selected === link.key ? "url(#arch-arrow-hot)" : "url(#arch-arrow)"}));
          state.tips.set(link.key, () => {
            const carriers = [...link.carriers].slice(0, 6).map((carrier) => node(carrier).label);
            return [link.kind === "internal" ? "Internal data" : link.kind === "incoming" ? "Block input" : "Block output", carriers.length ? carriers.join("; ") : "direct function relation"];
          });
        }
        for (const item of items) {
          const box = layout.boxes.get(item.key);
          if (item.key.startsWith("in:") || item.key.startsWith("out:")) {
            const [title, subtitle] = externalLabel(item.key);
            const target = item.key.replace(/^(in|out):/, "");
            const key = target.startsWith("endpoint:") ? target : target === "ext:unassigned" ? `ext:unassigned` : `block:${target.slice(4)}`;
            drawBox(boxLayer, box, {
              key,
              kind: target.startsWith("endpoint:") ? "endpoint-output" : "external",
              title,
              subtitle,
              selected: selected === key,
              label: `${title}, ${item.key.startsWith("in:") ? "upstream" : "downstream"}`,
            });
            state.tips.set(key, () => [title, subtitle]);
            continue;
          }
          const index = Number(item.key);
          const key = `node:${index}`;
          const maps = mapsOf.get(index) || [];
          const neighbor = selectedNode && links.some((link) => (
            (link.from === selectedNode && link.to === item.key) || (link.to === selectedNode && link.from === item.key)
          ));
          drawBox(boxLayer, box, {
            key,
            kind: "node kind-function",
            title: nodeTitle(index),
            subtitle: nodeSubtitle(index),
            selected: selected === key,
            related: neighbor,
            dimmed: selectedNode && selectedNode !== item.key && !neighbor,
            chips: [
              ...maps.slice(0, 4).map((map) => ({key: `node:${map}`, text: node(map).label, kind: node(map).kind})),
              ...(maps.length > 4 ? [{key: key, text: `+${maps.length - 4} more tables`, kind: "more"}] : []),
            ],
            label: `${nodeTitle(index)}, function`,
          });
          state.tips.set(key, () => [nodeTitle(index), `${nodeSubtitle(index)}${maps.length ? `; reads ${maps.length} tables` : ""}`]);
          for (const map of maps.slice(0, 4)) {
            state.tips.set(`node:${map}`, () => [node(map).label, nodeSubtitle(map)]);
          }
        }
      }

      const counts = state.model.blockCounts.get(blockId) || {};
      return {
        width: layout.width,
        height: layout.height,
        draw,
        title: block.name,
        subtitle: `${functions.length} functions, ${counts.map || 0} maps, ${(counts.signal || 0) + (counts.register || 0)} signals; `
          + `${upstreamKeys.length} upstream and ${downstreamKeys.length} downstream neighbors. Tables are listed inside the functions that read them.`,
        legend: [
          ["swatch kind-function", "Function of this block"],
          ["swatch kind-map", "Table read by the function"],
          ["swatch external", "Neighbor block or peripheral"],
          ["line", "Signals written by one side and read by the other"],
        ],
      };
    }

    function neighborhood(entries, limit) {
      const unique = new Map();
      for (const entry of entries) {
        if (!unique.has(entry.node)) unique.set(entry.node, new Set());
        unique.get(entry.node).add(entry.role);
      }
      const sorted = [...unique.entries()].sort((left, right) => {
        const a = node(left[0]);
        const b = node(right[0]);
        return KIND_ORDER.indexOf(a.kind) - KIND_ORDER.indexOf(b.kind)
          || String(a.block || "~").localeCompare(String(b.block || "~"))
          || a.label.localeCompare(b.label);
      });
      return {shown: sorted.slice(0, limit), hidden: Math.max(0, sorted.length - limit), total: sorted.length};
    }

    function nodeScene(index) {
      const predecessors = neighborhood(state.model.inFlow[index], NEIGHBOR_LIMIT);
      const successors = neighborhood(state.model.outFlow[index], NEIGHBOR_LIMIT);
      const items = [];
      const links = [];
      const center = `c:${index}`;
      items.push({key: center, width: 250, height: 54});
      for (const [other] of predecessors.shown) {
        items.push({key: `p:${other}`, width: 232, height: 44});
        links.push({from: `p:${other}`, to: center});
      }
      if (predecessors.hidden) {
        items.push({key: "p:more", width: 232, height: 34});
        links.push({from: "p:more", to: center});
      }
      for (const [other] of successors.shown) {
        items.push({key: `s:${other}`, width: 232, height: 44});
        links.push({from: center, to: `s:${other}`});
      }
      if (successors.hidden) {
        items.push({key: "s:more", width: 232, height: 34});
        links.push({from: center, to: "s:more"});
      }
      const first = new Set(items.filter((item) => item.key.startsWith("p:")).map((item) => item.key));
      const last = new Set(items.filter((item) => item.key.startsWith("s:")).map((item) => item.key));
      const layout = layered(items, links, {first, last, maxPerColumn: 14, columnGap: 110});
      const selected = state.selection || "";

      function draw(group) {
        const edgeLayer = svg("g", {class: "arch-flows"});
        const boxLayer = svg("g", {class: "arch-boxes"});
        group.append(edgeLayer, boxLayer);
        for (const link of links) {
          const a = layout.boxes.get(link.from);
          const b = layout.boxes.get(link.to);
          const {d} = bezier(a, b);
          const other = link.from === center ? link.to : link.from;
          const otherIndex = Number(other.slice(2));
          const hot = selected === `node:${otherIndex}`;
          edgeLayer.append(svg("path", {d, class: `arch-flow${hot ? " is-hot" : ""}`, "stroke-width": 1.6, "marker-end": hot ? "url(#arch-arrow-hot)" : "url(#arch-arrow)"}));
        }
        for (const item of items) {
          const box = layout.boxes.get(item.key);
          if (item.key.endsWith(":more")) {
            const side = item.key.startsWith("p:") ? predecessors : successors;
            drawBox(boxLayer, box, {
              key: `node:${index}`,
              kind: "more",
              title: `+${side.hidden} more ${item.key.startsWith("p:") ? "inputs" : "outputs"}`,
              subtitle: "listed in the details panel",
              label: "More relations",
            });
            continue;
          }
          const other = Number(item.key.slice(2));
          const key = `node:${other}`;
          drawBox(boxLayer, box, {
            key,
            kind: `node kind-${node(other).kind}${item.key.startsWith("c:") ? " is-center" : ""}`,
            title: nodeTitle(other),
            subtitle: nodeSubtitle(other),
            selected: selected === key,
            label: `${nodeTitle(other)}, ${KIND_LABELS[node(other).kind]}`,
          });
          state.tips.set(key, () => [nodeTitle(other), `${KIND_LABELS[node(other).kind]} | ${nodeSubtitle(other)}`]);
        }
      }

      return {
        width: layout.width,
        height: layout.height,
        draw,
        title: node(index).label,
        subtitle: `${KIND_LABELS[node(index).kind]} ${addressInfo(index).text}: ${predecessors.total} inputs and ${successors.total} outputs in the derived relation graph. Double-click a neighbor to move to it.`,
        legend: [
          ["swatch kind-function", "Function"],
          ["swatch kind-map", "Map"],
          ["swatch kind-signal", "Signal"],
          ["swatch kind-register", "Peripheral register"],
          ["swatch kind-ram", "Unreviewed address"],
        ],
      };
    }

    function chainScene(chainId) {
      const chainIndex = state.model.chainById.get(chainId);
      const chain = state.model.raw.chains[chainIndex];
      const nodes = new Set();
      chain.steps.forEach((step) => {
        nodes.add(step.from);
        nodes.add(step.to);
      });
      const items = [...nodes].map((index) => ({key: String(index), width: 240, height: 50}));
      const links = chain.steps.map((step, position) => ({from: String(step.from), to: String(step.to), step, position}));
      const layout = layered(items, links, {maxPerColumn: 9, columnGap: 124, rowGap: 22});
      const selected = state.selection || "";
      const selectedNode = selected.startsWith("node:") ? Number(selected.slice(5)) : null;

      function draw(group) {
        const edgeLayer = svg("g", {class: "arch-flows"});
        const labelLayer = svg("g", {class: "arch-edge-labels"});
        const boxLayer = svg("g", {class: "arch-boxes"});
        group.append(edgeLayer, labelLayer, boxLayer);
        for (const link of links) {
          const a = layout.boxes.get(link.from);
          const b = layout.boxes.get(link.to);
          const {d, mid} = bezier(a, b);
          const key = `step:${chainIndex}:${link.position}`;
          const touches = selectedNode !== null && (link.step.from === selectedNode || link.step.to === selectedNode);
          const classes = ["arch-flow", `sign-${link.step.sign}`];
          if (link.step.support !== "graph") classes.push("is-spec");
          if (selected === key) classes.push("is-selected");
          else if (touches) classes.push("is-hot");
          else if (selectedNode !== null) classes.push("is-dimmed");
          edgeLayer.append(svg("path", {d, class: "arch-flow-hit", "data-key": key, "stroke-width": 12}));
          edgeLayer.append(svg("path", {d, class: classes.join(" "), "stroke-width": 2, "marker-end": `url(#arch-arrow-${link.step.sign})`}));
          const text = `${link.step.effect} ${SIGN_GLYPHS[link.step.sign]}`;
          const width = text.length * 6.4 + 12;
          const label = svg("g", {class: `arch-edge-label sign-${link.step.sign}`, transform: `translate(${(mid[0] - width / 2).toFixed(1)},${(mid[1] - 9).toFixed(1)})`, "data-key": key});
          label.append(svg("rect", {width: width.toFixed(1), height: 18, rx: 9}));
          label.append(svg("text", {x: (width / 2).toFixed(1), y: 12.5, "text-anchor": "middle"}, text));
          labelLayer.append(label);
          state.tips.set(key, () => [`${node(link.step.from).label} -> ${node(link.step.to).label}`, `${link.step.effect}, sign ${link.step.sign}; ${link.step.note || "no note"}`]);
        }
        for (const item of items) {
          const index = Number(item.key);
          const key = `node:${index}`;
          const impact = chain.impact[String(index)];
          const isOutput = index === chain.output;
          drawBox(boxLayer, layout.boxes.get(item.key), {
            key,
            kind: `node kind-${node(index).kind}${isOutput ? " is-output" : ""}`,
            title: nodeTitle(index),
            subtitle: nodeSubtitle(index),
            selected: selected === key,
            dimmed: selectedNode !== null && selectedNode !== index && !chain.steps.some((step) => (
              (step.from === selectedNode && step.to === index) || (step.to === selectedNode && step.from === index)
            )),
            badge: isOutput ? {text: "OUT", sign: "output"} : impact ? {text: SIGN_GLYPHS[impact.sign], sign: impact.sign} : null,
            label: `${nodeTitle(index)}${isOutput ? ", chain output" : impact ? `, ${impact.sign} effect on ${chain.quantity}` : ""}`,
          });
          state.tips.set(key, () => [nodeTitle(index), isOutput ? `Output: ${chain.quantity}` : impact ? `Increase ${SIGN_PHRASES[impact.sign]} ${chain.quantity}` : "Delivery after the output"]);
        }
      }

      const graphSteps = chain.steps.filter((step) => step.support === "graph").length;
      const specSteps = chain.steps.filter((step) => step.support === "specification").length;
      const claimSteps = chain.steps.length - graphSteps - specSteps;
      return {
        width: layout.width,
        height: layout.height,
        draw,
        title: chain.name,
        subtitle: `${chain.steps.length} steps to ${node(chain.output).label} (${chain.quantity}); ${graphSteps} graph-connected, ${specSteps} specification-bound, ${claimSteps} declared. `
          + "A badge is the sign of the effect of an increase on the output.",
        legend: [
          ["sign sign-positive", "An increase raises the output"],
          ["sign sign-negative", "An increase lowers the output"],
          ["sign sign-none", "No established sign: selection, gate, index, or closed loop"],
          ["sign sign-mixed", "Paths with different signs"],
          ["line is-dashed", "Step without a visible graph relation"],
        ],
        table: (container) => renderStepTable(container, chainIndex),
      };
    }

    function traceTargets(direction) {
      const targets = new Map();
      for (const endpoint of state.model.raw.endpoints) {
        const matches = direction === "down"
          ? endpoint.direction !== "input"
          : endpoint.direction !== "output";
        if (!matches) continue;
        const members = endpoint.registers.length ? endpoint.registers : endpoint.functions;
        for (const member of [...members, ...endpoint.functions]) pushTo(targets, member, endpoint);
      }
      return targets;
    }

    function trace(index, direction) {
      const adjacency = direction === "down" ? state.model.outFlow : state.model.inFlow;
      const targets = traceTargets(direction);
      const relays = state.model.relays;
      const parent = new Map([[index, null]]);
      const distance = new Map([[index, 0]]);
      const reached = new Map();
      const queue = [index];
      while (queue.length) {
        const current = queue.shift();
        const depth = distance.get(current);
        for (const endpoint of targets.get(current) || []) {
          if (!reached.has(endpoint.id)) reached.set(endpoint.id, {endpoint, node: current, depth});
        }
        if (depth >= TRACE_DEPTH || (current !== index && !relays[current])) continue;
        for (const entry of adjacency[current]) {
          if (distance.has(entry.node)) continue;
          distance.set(entry.node, depth + 1);
          parent.set(entry.node, current);
          queue.push(entry.node);
        }
      }
      const paths = [...reached.values()].sort((left, right) => left.depth - right.depth).map((hit) => {
        const path = [];
        for (let cursor = hit.node; cursor !== null; cursor = parent.get(cursor)) path.push(cursor);
        return {...hit, path: direction === "down" ? path.reverse() : path};
      });
      return {paths, visited: distance.size};
    }

    function traceScene(index, direction) {
      const result = trace(index, direction);
      const nodes = new Set([index]);
      const edges = new Set();
      for (const hit of result.paths) {
        hit.path.forEach((item, position) => {
          nodes.add(item);
          if (position) edges.add(`${hit.path[position - 1]}>${item}`);
        });
      }
      const endpointKeys = result.paths.map((hit) => `endpoint:${hit.endpoint.id}`);
      const items = [
        ...[...nodes].map((item) => ({key: String(item), width: 232, height: 46})),
        ...endpointKeys.map((key) => ({key, width: 196, height: 42})),
      ];
      const links = [...edges].map((edge) => {
        const [from, to] = edge.split(">");
        return {from, to};
      });
      for (const hit of result.paths) {
        links.push(direction === "down"
          ? {from: String(hit.node), to: `endpoint:${hit.endpoint.id}`}
          : {from: `endpoint:${hit.endpoint.id}`, to: String(hit.node)});
      }
      const endpointSet = new Set(endpointKeys);
      const layout = layered(items, links, {
        first: direction === "up" ? endpointSet : new Set(),
        last: direction === "down" ? endpointSet : new Set(),
        maxPerColumn: 10,
        columnGap: 100,
      });
      const selected = state.selection || "";

      function draw(group) {
        const edgeLayer = svg("g", {class: "arch-flows"});
        const boxLayer = svg("g", {class: "arch-boxes"});
        group.append(edgeLayer, boxLayer);
        for (const link of links) {
          const a = layout.boxes.get(link.from);
          const b = layout.boxes.get(link.to);
          if (!a || !b) continue;
          edgeLayer.append(svg("path", {d: bezier(a, b).d, class: "arch-flow", "stroke-width": 1.8, "marker-end": "url(#arch-arrow)"}));
        }
        for (const item of items) {
          const box = layout.boxes.get(item.key);
          if (item.key.startsWith("endpoint:")) {
            const endpoint = state.model.endpointById.get(item.key.slice(9));
            drawBox(boxLayer, box, {
              key: item.key,
              kind: `endpoint-${endpoint.direction}`,
              title: endpoint.name,
              subtitle: endpoint.peripheral,
              selected: selected === item.key,
              label: endpoint.name,
            });
            state.tips.set(item.key, () => [endpoint.name, firstSentence(endpoint.summary)]);
            continue;
          }
          const other = Number(item.key);
          const key = `node:${other}`;
          drawBox(boxLayer, box, {
            key,
            kind: `node kind-${node(other).kind}${other === index ? " is-center" : ""}`,
            title: nodeTitle(other),
            subtitle: nodeSubtitle(other),
            selected: selected === key,
            label: nodeTitle(other),
          });
          state.tips.set(key, () => [nodeTitle(other), nodeSubtitle(other)]);
        }
      }

      const word = direction === "down" ? "actuator and link" : "sensor and input";
      return {
        width: layout.width,
        height: layout.height,
        draw,
        empty: result.paths.length ? null : `No derived relation path within ${TRACE_DEPTH} steps reaches a ${word} endpoint.`,
        title: `${direction === "down" ? "Trace to actuators" : "Trace from sensors"}: ${node(index).label}`,
        subtitle: `Shortest derived relation paths to ${result.paths.length} ${word} endpoints (${result.visited} nodes reachable within ${TRACE_DEPTH} steps). `
          + "Relations come from declared links, L0 calls, and L0 accesses and carry no sign; calculation signs come from declared steps.",
        legend: [
          ["swatch kind-function", "Function"],
          ["swatch kind-map", "Map"],
          ["swatch kind-signal", "Signal"],
          ["swatch endpoint-output", "Peripheral endpoint"],
        ],
        table: (container) => renderTraceTable(container, result, direction),
      };
    }

    function scene() {
      const route = state.route;
      if (route.type === "block") return blockScene(route.id);
      if (route.type === "chain") return chainScene(route.id);
      if (route.type === "node") return nodeScene(route.node);
      if (route.type === "trace") return traceScene(route.node, route.direction);
      return systemScene();
    }

    function drawBox(parent, box, options) {
      if (!box) return;
      const {key, kind, title, subtitle, selected, related, dimmed, badge, chips = [], label} = options;
      const classes = ["arch-box", ...String(kind).split(" ")];
      if (selected) classes.push("is-selected");
      if (related) classes.push("is-related");
      if (dimmed) classes.push("is-dimmed");
      const group = svg("g", {
        class: classes.join(" "),
        transform: `translate(${box.x.toFixed(1)},${box.y.toFixed(1)})`,
        "data-key": key,
        tabindex: 0,
        role: "button",
        "aria-label": label || [title, subtitle].filter(Boolean).join(", "),
      });
      const radius = String(kind).startsWith("endpoint") ? Math.min(box.h / 2, 16) : 7;
      group.append(svg("rect", {class: "arch-box-frame", width: box.w, height: box.h, rx: radius}));
      group.append(svg("rect", {class: "arch-box-bar", width: 4, height: box.h - 8, x: 4, y: 4, rx: 2}));
      const reserve = badge ? 34 : 12;
      const titleChars = Math.max(6, Math.floor((box.w - 16 - reserve) / 6.9));
      group.append(svg("text", {class: "arch-box-title", x: 14, y: 19}, truncate(title, titleChars)));
      if (subtitle) {
        group.append(svg("text", {class: "arch-box-sub", x: 14, y: 35}, truncate(subtitle, Math.floor((box.w - 22) / 6.3))));
      }
      if (badge) {
        const width = Math.max(22, badge.text.length * 7 + 10);
        const badgeGroup = svg("g", {class: `arch-badge sign-${badge.sign}`, transform: `translate(${box.w - width - 6},6)`});
        badgeGroup.append(svg("rect", {width, height: 18, rx: 9}));
        badgeGroup.append(svg("text", {x: width / 2, y: 13, "text-anchor": "middle"}, badge.text));
        group.append(badgeGroup);
      }
      chips.forEach((chip, position) => {
        const y = 44 + position * 15;
        const chipGroup = svg("g", {class: `arch-chip kind-${chip.kind}`, "data-key": chip.key, transform: `translate(14,${y})`});
        chipGroup.append(svg("rect", {class: "arch-chip-dot", width: 7, height: 7, y: 2, rx: 1.5}));
        chipGroup.append(svg("text", {x: 12, y: 9.5}, truncate(chip.text, Math.floor((box.w - 38) / 6.1))));
        group.append(chipGroup);
      });
      parent.append(group);
    }

    function defs() {
      const root = svg("defs");
      for (const [id, className] of [
        ["arch-arrow", "arrow"],
        ["arch-arrow-hot", "arrow is-hot"],
        ["arch-arrow-positive", "arrow sign-positive"],
        ["arch-arrow-negative", "arrow sign-negative"],
        ["arch-arrow-none", "arrow sign-none"],
      ]) {
        const marker = svg("marker", {
          id,
          viewBox: "0 0 10 10",
          refX: 9,
          refY: 5,
          markerWidth: 7,
          markerHeight: 7,
          markerUnits: "userSpaceOnUse",
          orient: "auto-start-reverse",
        });
        marker.append(svg("path", {d: "M0,0 L10,5 L0,10 z", class: `arch-${className}`}));
        root.append(marker);
      }
      return root;
    }

    function renderLegend(entries) {
      elements.legend.replaceChildren();
      for (const [className, text] of entries || []) {
        const mark = html("span", {className: `arch-legend-mark ${className}`, "aria-hidden": "true"});
        const sign = className.match(/^sign sign-(\w+)$/);
        if (sign) mark.textContent = SIGN_GLYPHS[sign[1]] || "";
        elements.legend.append(html("span", {className: "arch-legend-item"}, mark, text));
      }
    }

    function render() {
      if (!state.active || !state.model) return;
      const canvas = elements.canvas;
      const width = Math.max(1, Math.round(canvas.clientWidth));
      const height = Math.max(1, Math.round(canvas.clientHeight));
      canvas.setAttribute("viewBox", `0 0 ${width} ${height}`);
      state.tips.clear();
      const current = scene();
      const description = svg("desc", {id: "arch-canvas-desc"}, current.subtitle);
      const viewport = svg("g", {class: "arch-viewport"});
      canvas.replaceChildren(description, defs(), viewport);
      current.draw(viewport);
      if (current.empty) {
        viewport.append(svg("text", {x: 0, y: 24, class: "arch-empty"}, current.empty));
      }
      state.viewport = viewport;
      state.content = {width: Math.max(1, current.width), height: Math.max(1, current.height)};
      elements.title.textContent = current.title;
      elements.subtitle.textContent = current.subtitle;
      renderLegend(current.legend);
      elements.table.replaceChildren();
      elements.table.hidden = !current.table;
      if (current.table) current.table(elements.table);
      if (state.fitPending) {
        state.fitPending = false;
        fit(state.route.type === "system" ? 0 : READABLE_SCALE);
      } else {
        applyTransform();
      }
    }

    function scheduleRender() {
      if (!state.active || state.framePending) return;
      state.framePending = true;
      requestAnimationFrame(() => {
        state.framePending = false;
        render();
      });
    }

    // Pan and zoom.

    function applyTransform() {
      if (!state.viewport) return;
      const {x, y, k} = state.transform;
      state.viewport.setAttribute("transform", `translate(${x.toFixed(1)},${y.toFixed(1)}) scale(${k.toFixed(4)})`);
    }

    function fit(minimum = 0) {
      const rect = elements.canvas.getBoundingClientRect();
      const width = Math.max(1, rect.width);
      const height = Math.max(1, rect.height);
      const margin = width < 560 ? 12 : 28;
      const whole = Math.min(
        (width - 2 * margin) / state.content.width,
        (height - 2 * margin) / state.content.height,
      );
      const k = clamp(Math.max(whole, minimum), 0.12, 1.15);
      const drawnWidth = state.content.width * k;
      // The top edge stays in view: the canvas can extend below the fold.
      state.transform = {
        k,
        x: drawnWidth <= width - 2 * margin ? (width - drawnWidth) / 2 : margin,
        y: margin,
      };
      applyTransform();
    }

    function zoomAt(factor, clientX, clientY) {
      const rect = elements.canvas.getBoundingClientRect();
      const cx = clientX === undefined ? rect.width / 2 : clientX - rect.left;
      const cy = clientY === undefined ? rect.height / 2 : clientY - rect.top;
      const current = state.transform;
      const k = clamp(current.k * factor, 0.12, 3.2);
      const ratio = k / current.k;
      state.transform = {k, x: cx - (cx - current.x) * ratio, y: cy - (cy - current.y) * ratio};
      applyTransform();
    }

    function panBy(dx, dy) {
      state.transform = {...state.transform, x: state.transform.x + dx, y: state.transform.y + dy};
      applyTransform();
    }

    // Tooltip.

    function showTip(key, event) {
      const make = state.tips.get(key);
      if (!make) {
        hideTip();
        return;
      }
      const [title, detail] = make();
      elements.tooltip.replaceChildren(html("strong", {text: title}), html("span", {text: detail || ""}));
      elements.tooltip.hidden = false;
      const margin = 12;
      const rect = elements.tooltip.getBoundingClientRect();
      let left = event.clientX + 14;
      let top = event.clientY + 14;
      if (left + rect.width > window.innerWidth - margin) left = event.clientX - rect.width - 14;
      if (top + rect.height > window.innerHeight - margin) top = event.clientY - rect.height - 14;
      elements.tooltip.style.left = `${Math.max(margin, left)}px`;
      elements.tooltip.style.top = `${Math.max(margin, top)}px`;
    }

    function hideTip() {
      elements.tooltip.hidden = true;
    }

    // Activation.

    function activateKey(key, open = false) {
      if (!key) return;
      const [type, ...rest] = key.split(":");
      const value = rest.join(":");
      if (type === "block") {
        if (open || state.selection === key) {
          navigate({type: "block", id: value}, key);
        } else {
          select(key);
        }
        return;
      }
      if (type === "node") {
        const index = Number(value);
        if (open || state.selection === key) navigate({type: "node", node: index}, key);
        else select(key);
        return;
      }
      if (type === "endpoint" || type === "flow" || type === "step" || type === "edge" || type === "ext" || type === "chain") {
        select(key);
      }
    }

    function eventKey(event) {
      const target = event.target.closest?.("[data-key]");
      return target ? target.dataset.key : null;
    }

    elements.canvas.addEventListener("pointerdown", (event) => {
      state.pointers.set(event.pointerId, {x: event.clientX, y: event.clientY});
      if (state.pointers.size === 2) {
        const [first, second] = [...state.pointers.values()];
        state.pinch = {distance: Math.hypot(first.x - second.x, first.y - second.y) || 1};
        state.drag = null;
        return;
      }
      state.drag = {
        pointerId: event.pointerId,
        x: event.clientX,
        y: event.clientY,
        moved: false,
        key: eventKey(event),
      };
      elements.canvas.setPointerCapture(event.pointerId);
    });

    elements.canvas.addEventListener("pointermove", (event) => {
      if (state.pointers.has(event.pointerId)) {
        state.pointers.set(event.pointerId, {x: event.clientX, y: event.clientY});
      }
      if (state.pinch && state.pointers.size === 2) {
        const [first, second] = [...state.pointers.values()];
        const distance = Math.hypot(first.x - second.x, first.y - second.y) || 1;
        zoomAt(distance / state.pinch.distance, (first.x + second.x) / 2, (first.y + second.y) / 2);
        state.pinch.distance = distance;
        return;
      }
      const drag = state.drag;
      if (drag && drag.pointerId === event.pointerId) {
        const dx = event.clientX - drag.x;
        const dy = event.clientY - drag.y;
        if (!drag.moved && Math.hypot(dx, dy) > 4) {
          drag.moved = true;
          elements.canvas.classList.add("is-dragging");
          hideTip();
        }
        if (drag.moved) {
          panBy(dx, dy);
          drag.x = event.clientX;
          drag.y = event.clientY;
        }
        return;
      }
      const key = eventKey(event);
      if (key) showTip(key, event);
      else hideTip();
    });

    function endPointer(event) {
      state.pointers.delete(event.pointerId);
      if (state.pointers.size < 2) state.pinch = null;
      const drag = state.drag;
      if (!drag || drag.pointerId !== event.pointerId) return;
      state.drag = null;
      elements.canvas.classList.remove("is-dragging");
      if (elements.canvas.hasPointerCapture(event.pointerId)) {
        elements.canvas.releasePointerCapture(event.pointerId);
      }
      if (!drag.moved && event.type === "pointerup") {
        if (drag.key) activateKey(drag.key);
        else if (state.selection) select(null);
      }
    }

    elements.canvas.addEventListener("pointerup", endPointer);
    elements.canvas.addEventListener("pointercancel", endPointer);
    elements.canvas.addEventListener("pointerleave", hideTip);
    elements.canvas.addEventListener("dblclick", (event) => {
      const key = eventKey(event);
      if (key) activateKey(key, true);
    });
    elements.canvas.addEventListener("keydown", (event) => {
      if (event.key !== "Enter" && event.key !== " ") return;
      const key = eventKey(event);
      if (!key) return;
      event.preventDefault();
      activateKey(key, state.selection === key);
    });
    elements.canvas.addEventListener("wheel", (event) => {
      event.preventDefault();
      const scale = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? 400 : 1;
      const dx = event.deltaX * scale;
      const dy = event.deltaY * scale;
      if (event.ctrlKey || event.metaKey) {
        zoomAt(Math.exp(-dy * 0.01), event.clientX, event.clientY);
      } else if (event.shiftKey) {
        panBy(-(dx || dy), 0);
      } else if (Math.abs(dx) > Math.abs(dy)) {
        panBy(-dx, 0);
      } else {
        zoomAt(Math.exp(-dy * 0.0016), event.clientX, event.clientY);
      }
    }, {passive: false});
    elements.canvas.addEventListener("gesturestart", (event) => {
      event.preventDefault();
      state.gesture = event.scale || 1;
    }, {passive: false});
    elements.canvas.addEventListener("gesturechange", (event) => {
      event.preventDefault();
      const scale = event.scale || 1;
      zoomAt(scale / (state.gesture || scale), event.clientX, event.clientY);
      state.gesture = scale;
    }, {passive: false});
    elements.canvas.addEventListener("gestureend", () => {
      state.gesture = null;
    });
    elements.zoomIn.addEventListener("click", () => zoomAt(1.25));
    elements.zoomOut.addEventListener("click", () => zoomAt(0.8));
    elements.fit.addEventListener("click", () => fit());
    elements.support.addEventListener("change", () => {
      state.support = elements.support.checked;
      scheduleRender();
    });
    elements.flowLimit.addEventListener("input", () => {
      state.flowLimit = Number(elements.flowLimit.value) || 60;
      elements.flowLimitValue.textContent = String(state.flowLimit);
      scheduleRender();
    });

    // Search.

    function parseQueryAddress(text) {
      const match = text.trim().match(/^(?:(?:thunk_)?(?:fun|dat|lab)_|0x)?([0-9a-f]{3,8})$/i);
      return match ? match[1].toLowerCase().padStart(8, "0") : null;
    }

    function search(text) {
      const query = text.trim().toLowerCase();
      if (!query) return [];
      const results = [];
      const address = parseQueryAddress(query);
      const raw = state.model.raw;
      raw.blocks.forEach((block) => {
        const haystack = `${block.name} ${block.id} ${block.summary}`.toLowerCase();
        if (haystack.includes(query)) {
          results.push({score: block.name.toLowerCase().startsWith(query) ? 1 : 12, kind: "Block", label: block.name, detail: state.model.stageById.get(block.stage)?.name || "", key: `block:${block.id}`, route: {type: "block", id: block.id}});
        }
      });
      raw.chains.forEach((chain) => {
        const haystack = `${chain.name} ${chain.id} ${chain.quantity} ${chain.summary}`.toLowerCase();
        if (haystack.includes(query)) {
          results.push({score: 2, kind: "Chain", label: chain.name, detail: chain.quantity, key: `chain:${chain.id}`, route: {type: "chain", id: chain.id}});
        }
      });
      raw.endpoints.forEach((endpoint) => {
        const haystack = `${endpoint.name} ${endpoint.id} ${endpoint.peripheral} ${endpoint.summary}`.toLowerCase();
        if (haystack.includes(query)) {
          results.push({score: 6, kind: "Endpoint", label: endpoint.name, detail: endpoint.peripheral, key: `endpoint:${endpoint.id}`, route: {type: "system"}});
        }
      });
      if (address && state.binding.reverse.has(address)) {
        const index = state.binding.reverse.get(address);
        results.push({score: 0, kind: KIND_LABELS[node(index).kind], label: node(index).label, detail: `${state.rom.id} ${hex(Number.parseInt(address, 16))}`, key: `node:${index}`, route: {type: "node", node: index}});
      }
      state.model.searchText.forEach((textValue, index) => {
        const item = node(index);
        let score = null;
        if (address && item.addr === address) score = 0;
        else if (item.label.toLowerCase().startsWith(query)) score = 4;
        else if (textValue.includes(query)) score = 14 + KIND_ORDER.indexOf(item.kind);
        if (score === null) return;
        if (item.kind === "map" || item.kind === "function") score -= 1;
        results.push({score, kind: KIND_LABELS[item.kind], label: item.label, detail: nodeSubtitle(index), key: `node:${index}`, route: {type: "node", node: index}});
      });
      results.sort((left, right) => left.score - right.score || left.label.localeCompare(right.label));
      const seen = new Set();
      return results.filter((result) => {
        if (seen.has(result.key)) return false;
        seen.add(result.key);
        return true;
      }).slice(0, 14);
    }

    function hideResults() {
      elements.results.hidden = true;
      elements.results.replaceChildren();
      elements.search.setAttribute("aria-expanded", "false");
      state.results = [];
      state.resultIndex = -1;
    }

    function chooseResult(result) {
      if (!result) return;
      elements.search.value = "";
      if (result.key.startsWith("endpoint:")) navigate({type: "system"}, result.key);
      else navigate(result.route, result.key);
    }

    function renderResults() {
      elements.results.replaceChildren();
      state.results.forEach((result, position) => {
        const option = html("button", {
          type: "button",
          role: "option",
          id: `arch-result-${position}`,
          className: `arch-result${position === state.resultIndex ? " is-active" : ""}`,
          "aria-selected": position === state.resultIndex ? "true" : "false",
          onmousedown: (event) => event.preventDefault(),
          onclick: () => chooseResult(result),
        },
        html("span", {className: "arch-result-kind", text: result.kind}),
        html("span", {className: "arch-result-label", text: result.label}),
        html("span", {className: "arch-result-detail", text: result.detail}));
        elements.results.append(option);
      });
      elements.results.hidden = !state.results.length;
      elements.search.setAttribute("aria-expanded", state.results.length ? "true" : "false");
      if (state.resultIndex >= 0) elements.search.setAttribute("aria-activedescendant", `arch-result-${state.resultIndex}`);
      else elements.search.removeAttribute("aria-activedescendant");
    }

    elements.search.addEventListener("input", () => {
      state.results = search(elements.search.value);
      state.resultIndex = state.results.length ? 0 : -1;
      renderResults();
    });
    elements.search.addEventListener("keydown", (event) => {
      if (event.key === "ArrowDown" || event.key === "ArrowUp") {
        if (!state.results.length) return;
        event.preventDefault();
        const step = event.key === "ArrowDown" ? 1 : -1;
        state.resultIndex = (state.resultIndex + step + state.results.length) % state.results.length;
        renderResults();
      } else if (event.key === "Enter") {
        event.preventDefault();
        chooseResult(state.results[Math.max(0, state.resultIndex)]);
      } else if (event.key === "Escape") {
        hideResults();
      }
    });
    elements.search.addEventListener("blur", () => setTimeout(hideResults, 120));

    // Details.

    function section(title, ...content) {
      const items = content.flat().filter(Boolean);
      if (!items.length) return null;
      return html("section", {className: "arch-detail-section"}, html("h3", {text: title}), ...items);
    }

    function nodeButton(index, extra = "") {
      const item = node(index);
      return html("button", {
        type: "button",
        className: `arch-node-link kind-${item.kind}`,
        title: `${KIND_LABELS[item.kind]} ${addressInfo(index).text}`,
        onclick: () => navigate({type: "node", node: index}, `node:${index}`),
      }, html("span", {className: "arch-node-dot", "aria-hidden": "true"}), `${truncate(item.label, 64)}${extra}`);
    }

    function blockButton(blockId, extra = "") {
      return html("button", {
        type: "button",
        className: "arch-node-link kind-block",
        onclick: () => navigate({type: "block", id: blockId}, `block:${blockId}`),
      }, html("span", {className: "arch-node-dot", "aria-hidden": "true"}), `${blockName(blockId)}${extra}`);
    }

    function linkList(indices, limit = LIST_LIMIT, extra = () => "") {
      const list = html("div", {className: "arch-link-list"});
      indices.slice(0, limit).forEach((index) => list.append(nodeButton(index, extra(index))));
      if (indices.length > limit) {
        const more = html("button", {type: "button", className: "arch-more", text: `Show ${indices.length - limit} more`});
        more.addEventListener("click", () => {
          indices.slice(limit).forEach((index) => list.insertBefore(nodeButton(index, extra(index)), more));
          more.remove();
        });
        list.append(more);
      }
      return list;
    }

    function metaList(entries) {
      const list = html("dl", {className: "detail-meta"});
      for (const [label, value] of entries) {
        if (value === undefined || value === null || value === "") continue;
        list.append(html("dt", {text: label}), html("dd", {text: String(value)}));
      }
      return list.children.length ? list : null;
    }

    function actions(...buttons) {
      const items = buttons.filter(Boolean);
      return items.length ? html("div", {className: "arch-actions"}, ...items) : null;
    }

    function action(label, handler, primary = false) {
      return html("button", {type: "button", className: primary ? "is-primary" : "", text: label, onclick: handler});
    }

    function specList(specs) {
      if (!specs || !specs.length) return null;
      return html("ul", {className: "arch-spec-list"}, ...specs.map((spec) => html("li", {text: spec})));
    }

    function heading(eyebrow, title) {
      return html("div", {className: "details-heading"},
        html("div", {}, html("p", {className: "eyebrow", text: eyebrow}), html("h2", {text: title})),
        html("button", {type: "button", "aria-label": "Clear selection", text: "Clear", onclick: () => select(null)}));
    }

    function chainImpactSection(index) {
      const chains = [...(state.model.chainsByNode.get(index) || [])];
      if (!chains.length) return null;
      const items = chains.map((chainIndex) => {
        const chain = state.model.raw.chains[chainIndex];
        const impact = chain.impact[String(index)];
        let text;
        if (index === chain.output) text = `is the output: ${chain.quantity}.`;
        else if (impact) text = `an increase ${SIGN_PHRASES[impact.sign]} ${chain.quantity} (${impact.steps.length} steps).`;
        else text = `has no step path to the output ${node(chain.output).label}.`;
        return html("li", {className: impact ? `sign-${impact.sign}` : ""},
          html("button", {type: "button", className: "arch-inline-link", text: chain.name, onclick: () => navigate({type: "chain", id: chain.id}, `node:${index}`)}),
          impact ? html("span", {className: `arch-sign-pill sign-${impact.sign}`, text: SIGN_GLYPHS[impact.sign]}) : null,
          ` ${text}`);
      });
      return section("Calculation chains", html("ul", {className: "arch-impact-list"}, ...items));
    }

    function reachSection(index) {
      const result = trace(index, "down");
      if (!result.paths.length) return null;
      const list = html("ul", {className: "arch-reach-list"});
      for (const hit of result.paths.slice(0, 8)) {
        list.append(html("li", {}, html("strong", {text: hit.endpoint.name}), ` in ${hit.depth} relations via ${node(hit.node).label}`));
      }
      return section("Derived reach, unsigned",
        html("p", {className: "detail-copy secondary", text: "Shortest graph-relation paths to actuator and link registers. A relation records structural evidence; calculation signs come from declared steps."}),
        list,
        actions(action("Trace to actuators", () => navigate({type: "trace", direction: "down", node: index}, `node:${index}`))));
    }

    function bindingDetails(binding) {
      if (!binding) return null;
      return section("Meaning bindings", metaList([
        ["Meaning", binding.meaning], ["Selected layout", binding.layout],
        ["Selected image", binding.image],
        ["Applicable images", binding.images.length ? binding.images.join(", ")
          : binding.availability === "missing" ? "unknown" : "all images of the layout"],
        ["Symbol", binding.reference || (binding.availability === "image-excluded"
          ? `not applicable to ${binding.image}`
          : binding.statuses.find((item) => item.layout === binding.layout)?.state || "unknown")],
        ["Home layout", binding.home],
        ...binding.symbols.map((symbol) => [symbol.layout,
          `${symbol.ref}${symbol.level ? ` [${symbol.level}]` : ""}${symbol.images.length ? ` (${symbol.images.join(", ")})` : ""}`]),
        ...binding.statuses.map((status) => [status.layout,
          `${status.state}${status.stale ? " (stale search)" : ""}${status.note ? `: ${status.note}` : ""}`]),
      ]), binding.analogs.length ? html("ul", {className: "arch-reach-list"},
        ...binding.analogs.map((analog) => html("li", {},
          html("strong", {text: `Analog: ${analog.to}`}), ` ${analog.note || ""}`))) : null);
    }

    function nodeDetails(index) {
      const item = node(index);
      const info = addressInfo(index);
      const meta = item.meta || {};
      const inputs = neighborhood(state.model.inFlow[index], Infinity).shown.map(([other]) => other);
      const outputs = neighborhood(state.model.outFlow[index], Infinity).shown.map(([other]) => other);
      const calls = neighborhood(state.model.outOther[index].filter((entry) => entry.kind === "call"), Infinity).shown.map(([other]) => other);
      const callers = neighborhood(state.model.inOther[index].filter((entry) => entry.kind === "call"), Infinity).shown.map(([other]) => other);
      const endpoints = state.model.endpointsByNode.get(index) || [];
      const addressRows = [["Address", info.text]];
      if (meta.summaryLayout && meta.summaryLayout !== meta.binding?.layout) {
        addressRows.push(["Summary layout", meta.summaryLayout]);
      }
      if (item.note && meta.noteLayout && meta.noteLayout !== meta.binding?.layout) {
        addressRows.push(["Notes layout", meta.noteLayout]);
      }
      return [
        heading(`${KIND_LABELS[item.kind]}${item.block ? ` / ${blockName(item.block)}` : ""}`, item.label),
        html("p", {className: "detail-range", text: info.text}),
        html("div", {className: "detail-badges"}, ...[item.confidence, item.role, item.units, item.pinned ? "placed" : ""].filter(Boolean).map((text) => html("span", {className: "badge", text}))),
        metaList([
          ...addressRows,
          ["Block", item.block ? blockName(item.block) : ""],
          ["Category", meta.category],
          ["Dimension", meta.dimension],
          ["Storage", meta.storage],
          ["Scale", meta.scale],
          ["Scale confidence", meta.scaleConfidence],
          ["Family", meta.family],
          ["Contract confidence", meta.contractConfidence],
        ]),
        item.text ? html("p", {className: "detail-copy", text: item.text}) : null,
        item.note ? html("p", {className: "detail-copy secondary", text: item.note}) : null,
        bindingDetails(meta.binding),
        section("Relation origins", metaList([...state.model.relationOrigins[index]])),
        meta.contract ? section("Contract", html("p", {className: "detail-copy secondary", text: meta.contract})) : null,
        actions(
          state.route.type === "node" && state.route.node === index ? null : action("Open neighborhood", () => navigate({type: "node", node: index}, `node:${index}`), true),
          action("Trace to actuators", () => navigate({type: "trace", direction: "down", node: index}, `node:${index}`)),
          action("Trace from sensors", () => navigate({type: "trace", direction: "up", node: index}, `node:${index}`)),
          info.jump !== null ? action("Show in address map", () => bridge.showAddress(info.jump)) : null,
        ),
        chainImpactSection(index),
        endpoints.length ? section("Peripheral endpoints", html("ul", {className: "arch-reach-list"}, ...endpoints.map((endpoint) => html("li", {}, html("strong", {text: endpoint.name}), ` ${endpoint.peripheral}`)))) : null,
        reachSection(index),
        inputs.length ? section(`Inputs (${inputs.length})`, linkList(inputs)) : null,
        outputs.length ? section(`Outputs (${outputs.length})`, linkList(outputs)) : null,
        calls.length ? section(`Calls (${calls.length})`, linkList(calls)) : null,
        callers.length ? section(`Called by (${callers.length})`, linkList(callers)) : null,
        item.source ? html("p", {className: "detail-source", text: `Source: ${item.source}`}) : null,
      ];
    }

    function blockDetails(blockId) {
      const block = state.model.blockById.get(blockId);
      const counts = state.model.blockCounts.get(blockId) || {};
      const stage = state.model.stageById.get(block.stage);
      const upstream = (state.model.flowsIn.get(blockId) || []).slice().sort((left, right) => right.weight - left.weight);
      const downstream = (state.model.flowsOut.get(blockId) || []).slice().sort((left, right) => right.weight - left.weight);
      const members = block.members.slice();
      const byKind = (kind) => members.filter((index) => node(index).kind === kind);
      const chains = state.model.raw.chains.filter((_chain, chainIndex) => state.model.chainBlocks[chainIndex].has(blockId));
      const endpoints = state.model.raw.endpoints.filter((endpoint) => endpoint.block === blockId);
      const flowList = (flows, side) => html("div", {className: "arch-link-list"}, ...flows.slice(0, LIST_LIMIT).map((flow) => {
        const other = side === "in" ? flow.from : flow.to;
        return blockButton(other, ` (${flow.weight})`);
      }));
      return [
        heading(stage ? stage.name : block.stage, block.name),
        html("div", {className: "detail-badges"}, ...[block.generic ? "shared kernels" : "", `${block.members.length} members`].filter(Boolean).map((text) => html("span", {className: "badge", text}))),
        html("p", {className: "detail-copy", text: block.summary}),
        metaList(KIND_ORDER.filter((kind) => counts[kind]).map((kind) => [KIND_LABELS[kind], counts[kind]])),
        actions(
          state.route.type === "block" && state.route.id === blockId ? null : action("Open block diagram", () => navigate({type: "block", id: blockId}, `block:${blockId}`), true),
          state.route.type === "system" ? null : action("Show on system map", () => navigate({type: "system"}, `block:${blockId}`)),
        ),
        chains.length ? section("Calculation chains", html("div", {className: "arch-link-list"}, ...chains.map((chain) => html("button", {type: "button", className: "arch-node-link kind-chain", text: chain.name, onclick: () => navigate({type: "chain", id: chain.id}, `chain:${chain.id}`)})))) : null,
        endpoints.length ? section("Peripheral endpoints", html("ul", {className: "arch-reach-list"}, ...endpoints.map((endpoint) => html("li", {}, html("strong", {text: endpoint.name}), ` ${endpoint.direction}, ${endpoint.peripheral}`)))) : null,
        upstream.length ? section(`Receives from (${upstream.length})`, flowList(upstream, "in")) : null,
        downstream.length ? section(`Feeds (${downstream.length})`, flowList(downstream, "out")) : null,
        byKind("map").length ? section(`Maps (${byKind("map").length})`, linkList(byKind("map"))) : null,
        byKind("function").length ? section(`Functions (${byKind("function").length})`, linkList(byKind("function"))) : null,
        byKind("signal").length + byKind("register").length ? section(`Signals (${byKind("signal").length + byKind("register").length})`, linkList([...byKind("signal"), ...byKind("register")])) : null,
        byKind("axis").length ? section(`Axes (${byKind("axis").length})`, linkList(byKind("axis"))) : null,
        block.specs.length ? section("Specifications", specList(block.specs)) : null,
      ];
    }

    function endpointDetails(endpointId) {
      const endpoint = state.model.endpointById.get(endpointId);
      return [
        heading(`${endpoint.direction} endpoint`, endpoint.name),
        html("p", {className: "detail-range", text: endpoint.peripheral}),
        html("p", {className: "detail-copy", text: endpoint.summary}),
        actions(action("Open owning block", () => navigate({type: "block", id: endpoint.block}, `endpoint:${endpoint.id}`), true)),
        section("Owning block", html("div", {className: "arch-link-list"}, blockButton(endpoint.block))),
        endpoint.registers.length ? section(`Registers (${endpoint.registers.length})`, linkList(endpoint.registers)) : null,
        endpoint.functions.length ? section(`Functions (${endpoint.functions.length})`, linkList(endpoint.functions)) : null,
        endpoint.specs.length ? section("Specifications", specList(endpoint.specs)) : null,
      ];
    }

    function flowDetails(key) {
      const [from, to] = key.slice(5).split(">");
      const flow = state.model.raw.flows.find((item) => item.from === from && item.to === to);
      if (!flow) return null;
      return [
        heading("Inter-block flow", `${blockName(from)} -> ${blockName(to)}`),
        html("p", {className: "detail-copy", text: `${flow.weight} derived data and control relations cross from ${blockName(from)} to ${blockName(to)}. Carriers are ordered by relation count.`}),
        section("Blocks", html("div", {className: "arch-link-list"}, blockButton(from, " (source)"), blockButton(to, " (target)"))),
        section(`Carriers (${flow.carriers.length})`, linkList(flow.carriers, 20)),
      ];
    }

    function chainDetails(chainId) {
      const chainIndex = state.model.chainById.get(chainId);
      const chain = state.model.raw.chains[chainIndex];
      const impacts = Object.entries(chain.impact)
        .map(([index, value]) => [Number(index), value])
        .sort((left, right) => KIND_ORDER.indexOf(node(left[0]).kind) - KIND_ORDER.indexOf(node(right[0]).kind) || node(left[0]).label.localeCompare(node(right[0]).label));
      const tables = impacts.filter(([index]) => node(index).kind === "map" || node(index).kind === "axis");
      const others = impacts.filter(([index]) => node(index).kind !== "map" && node(index).kind !== "axis");
      const impactItem = ([index, value]) => html("li", {className: `sign-${value.sign}`},
        html("span", {className: `arch-sign-pill sign-${value.sign}`, text: SIGN_GLYPHS[value.sign]}),
        html("button", {type: "button", className: "arch-inline-link", text: node(index).label, onclick: () => select(`node:${index}`)}),
        ` ${SIGN_PHRASES[value.sign]} the output`);
      return [
        heading("Calculation chain", chain.name),
        html("p", {className: "detail-copy", text: chain.summary}),
        metaList([["Quantity", chain.quantity], ["Output", `${node(chain.output).label} (${addressInfo(chain.output).text})`], ["Steps", chain.steps.length]]),
        actions(state.route.type === "chain" && state.route.id === chainId ? null : action("Open chain", () => navigate({type: "chain", id: chainId}, `chain:${chainId}`), true)),
        tables.length ? section("Tables and axes: effect of an increase", html("ul", {className: "arch-impact-list"}, ...tables.map(impactItem))) : null,
        others.length ? section("Signals and functions: effect of an increase", html("ul", {className: "arch-impact-list"}, ...others.map(impactItem))) : null,
        chain.specs.length ? section("Specifications", specList(chain.specs)) : null,
      ];
    }

    function stepDetails(key) {
      const [, chainText, stepText] = key.split(":");
      const chain = state.model.raw.chains[Number(chainText)];
      const step = chain && chain.steps[Number(stepText)];
      if (!step) return null;
      return [
        heading(`${chain.name}, step ${Number(stepText) + 1}`, `${node(step.from).label} -> ${node(step.to).label}`),
        html("div", {className: "detail-badges"}, html("span", {className: "badge", text: step.effect}), html("span", {className: `badge sign-${step.sign}`, text: `sign ${step.sign}`}), html("span", {className: "badge", text: `${step.support}-bound`})),
        step.note ? html("p", {className: "detail-copy", text: step.note}) : null,
        section("From", html("div", {className: "arch-link-list"}, nodeButton(step.from))),
        section("To", html("div", {className: "arch-link-list"}, nodeButton(step.to))),
        step.via.length ? section("Performed by", linkList(step.via)) : null,
        step.specs.length ? section("Specifications", specList(step.specs)) : null,
      ];
    }

    function endName(end) {
      const target = end.replace(/^(in|out):/, "");
      if (target === "ext:unassigned") return "No reviewed writer";
      if (target.startsWith("endpoint:")) return state.model.endpointById.get(target.slice(9))?.name || target;
      if (target.startsWith("ext:")) return blockName(target.slice(4));
      return node(Number(target)).label;
    }

    function blockEdgeDetails(key) {
      const link = state.route.type === "block" && state.sceneLinks.get(key);
      if (!link) return null;
      const titles = {internal: "Internal data", incoming: "Block input", outgoing: "Block output"};
      const carriers = [...link.carriers];
      return [
        heading(titles[link.kind], `${endName(link.from)} -> ${endName(link.to)}`),
        html("p", {className: "detail-copy", text: carriers.length
          ? "The source writes these signals and the target reads them."
          : "A direct function relation without a reviewed carrier signal."}),
        carriers.length ? section(`Carriers (${carriers.length})`, linkList(carriers)) : null,
      ];
    }

    function overviewDetails() {
      const route = state.route;
      if (route.type === "chain") return chainDetails(route.id);
      if (route.type === "block") return blockDetails(route.id);
      if (route.type === "node" || route.type === "trace") return nodeDetails(route.node);
      const raw = state.model.raw;
      return [
        html("div", {className: "details-heading"}, html("div", {}, html("p", {className: "eyebrow", text: "Architecture"}), html("h2", {text: `${raw.id} firmware`}))),
        html("p", {className: "detail-copy", text: raw.summary}),
        metaList([
          ["Stages", raw.stages.length],
          ["Blocks", raw.blocks.length],
          ["Endpoints", raw.endpoints.length],
          ["Chains", raw.chains.length],
          ["Nodes", raw.nodes.length],
          ["Relations", raw.edges.length],
          ["Source", raw.source],
        ]),
        html("p", {className: "detail-copy secondary", text: "Select a block to see its flows, members, and specifications. A calculation chain shows how an increase of each table and signal moves the actuator command."}),
      ];
    }

    function renderDetails() {
      if (!state.model) return;
      const key = state.selection;
      let content = null;
      if (key) {
        const [type, ...rest] = key.split(":");
        const value = rest.join(":");
        if (type === "node") content = nodeDetails(Number(value));
        else if (type === "block") content = blockDetails(value);
        else if (type === "endpoint") content = endpointDetails(value);
        else if (type === "flow") content = flowDetails(key);
        else if (type === "chain") content = chainDetails(value);
        else if (type === "unavailable") {
          const chain = state.model.raw.chainAvailability.find((item) => item.id === value);
          if (chain) content = [heading("Unavailable calculation chain", chain.name),
            html("p", {className: "detail-copy", text: `${chain.bound} of ${chain.total} steps are bound on ${state.model.raw.layout}.`}),
            ...chain.missing.map((binding) => bindingDetails(binding))];
        }
        else if (type === "step") content = stepDetails(key);
        else if (type === "edge") content = blockEdgeDetails(key);
        else if (type === "ext") content = [heading("Upstream", "No bound writer"), html("p", {className: "detail-copy", text: "These symbols have no writer function bound in this layout's graph. The view does not establish their producer."})];
      }
      elements.details.replaceChildren(...(content || overviewDetails()).filter(Boolean));
    }

    // Tables below the diagram.

    function renderStepTable(container, chainIndex) {
      const chain = state.model.raw.chains[chainIndex];
      const table = html("table", {className: "arch-steps"});
      table.append(html("thead", {}, html("tr", {},
        ...["#", "From", "Effect", "To", "Sign", "Performed by", "Note"].map((text) => html("th", {scope: "col", text})))));
      const body = html("tbody");
      chain.steps.forEach((step, position) => {
        const key = `step:${chainIndex}:${position}`;
        const row = html("tr", {className: state.selection === key ? "is-selected" : ""},
          html("td", {text: String(position + 1)}),
          html("td", {}, nodeButton(step.from)),
          html("td", {text: step.effect}),
          html("td", {}, nodeButton(step.to)),
          html("td", {}, html("span", {className: `arch-sign-pill sign-${step.sign}`, text: SIGN_GLYPHS[step.sign], title: step.sign})),
          html("td", {}, ...step.via.map((via) => nodeButton(via))),
          html("td", {className: "arch-step-note"}, step.note, step.support !== "graph" ? html("span", {className: "badge", text: step.support === "specification" ? "specification" : "declared"}) : null));
        row.addEventListener("click", (event) => {
          if (!event.target.closest("button")) select(key);
        });
        body.append(row);
      });
      table.append(body);
      container.append(html("h3", {className: "arch-table-title", text: "Steps"}), html("div", {className: "arch-table-scroll"}, table));
    }

    function renderTraceTable(container, result, direction) {
      if (!result.paths.length) return;
      const list = html("ol", {className: "arch-trace-list"});
      for (const hit of result.paths) {
        list.append(html("li", {},
          html("strong", {text: hit.endpoint.name}),
          ` (${hit.depth} relations): `,
          ...hit.path.flatMap((item, position) => [position ? html("span", {className: "arch-trace-arrow", text: " -> "}) : null, nodeButton(item)])));
      }
      container.append(html("h3", {className: "arch-table-title", text: "Paths"}), list);
    }

    // Public interface.

    function setRom(rom) {
      state.rom = rom;
      const binding = rom.architecture;
      const available = Boolean(binding && atlasModels()[binding.source]);
      elements.view.dataset.available = available ? "true" : "false";
      if (!available) {
        state.model = null;
        state.binding = null;
        elements.banner.textContent = "No architecture model is declared for this ROM.";
        elements.canvas.replaceChildren();
        elements.details.replaceChildren();
        elements.chains.replaceChildren();
        elements.crumbs.replaceChildren();
        return;
      }
      if (!models.has(binding.source)) models.set(binding.source, prepare(atlasModels()[binding.source]));
      const next = models.get(binding.source);
      if (state.model !== next) {
        state.model = next;
        state.route = {type: "system"};
        state.selection = null;
      }
      state.binding = prepareBinding(binding, next);
      const flows = next.raw.flows.length;
      elements.flowLimit.max = String(Math.max(10, Math.ceil(flows / 10) * 10));
      if (state.flowLimit > Number(elements.flowLimit.max)) {
        state.flowLimit = Number(elements.flowLimit.max);
        elements.flowLimit.value = String(state.flowLimit);
        elements.flowLimitValue.textContent = String(state.flowLimit);
      }
      state.fitPending = true;
      renderChrome();
      renderDetails();
      scheduleRender();
    }

    function atlasModels() {
      return bridge.atlas.architectures || {};
    }

    function activate() {
      state.active = true;
      elements.view.hidden = false;
      state.fitPending = true;
      scheduleRender();
    }

    function deactivate() {
      state.active = false;
      elements.view.hidden = true;
      hideTip();
      hideResults();
    }

    function hashParams() {
      if (!state.model) return [];
      const entries = [["arch", routeKey(state.route)]];
      const selection = encodeSelection(state.selection);
      if (selection) entries.push(["sel", selection]);
      return entries;
    }

    function restore(parameters) {
      if (!state.model) return;
      state.route = parseRoute(parameters.get("arch"));
      state.selection = decodeSelection(parameters.get("sel"));
      state.fitPending = true;
      renderChrome();
      renderDetails();
      scheduleRender();
    }

    function resize() {
      scheduleRender();
    }

    new ResizeObserver(() => {
      if (state.active) scheduleRender();
    }).observe(elements.canvas);

    return {setRom, activate, deactivate, hashParams, restore, resize, get model() {
      return model();
    }};
  }

  window.RomAtlasArchitecture = {create, layered, bezier};
})();
