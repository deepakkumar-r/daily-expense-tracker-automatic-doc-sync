"use strict";

const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const assets = path.join(__dirname, "..", "src", "static");
const source = readFileSync(path.join(assets, "app.js"), "utf8");
const html = readFileSync(path.join(assets, "index.html"), "utf8");

class Node {
  constructor(tag = "div", text = "") {
    this.tagName = tag;
    this._text = String(text);
    this.children = [];
    this.listeners = {};
    this.attributes = {};
    this.value = "";
    this.className = "";
    this.hidden = false;
    this.disabled = false;
    this.isConnected = true;
    this.style = {};
    this.open = false;
    this.classList = { contains: (name) => this.className.split(" ").includes(name) };
  }
  get textContent() { return this._text + this.children.map((child) => child.textContent).join(""); }
  set textContent(value) { this._text = String(value); this.children = []; }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this._text = ""; this.children = children; }
  add(option) { this.append(option); }
  setAttribute(name, value) { this.attributes[name] = value; }
  addEventListener(type, handler) { (this.listeners[type] ||= []).push(handler); }
  async dispatch(type, event = {}) {
    for (const handler of this.listeners[type] || []) await handler({ preventDefault() {}, ...event });
  }
  focus() { this.focused = true; }
  showModal() { this.open = true; }
  close() { this.open = false; this.dispatch("close"); }
  reset() {}
}

function fixture() {
  return {
    expenses: [{ id: "9223372036854775806", amount: "12.50", amount_cents: "1250",
      category: "food", date: "2026-11-10", description: "<img src=x onerror=alert(1)>" }],
    categories: ["food"],
    summary: { total_cents: "1250", total: "12.50", count: 1, category_count: 1,
      by_category: [{ category: "food", amount_cents: "1250", amount: "12.50" }],
      by_day: [{ date: "2026-11-10", amount_cents: "1250", amount: "12.50" }] },
  };
}

async function setup() {
  const nodes = Object.fromEntries([...html.matchAll(/\bid="([^"]+)"/g)].map((match) => [match[1], new Node()]));
  const calls = [];
  let handler = async () => ({ ok: true, json: async () => fixture() });
  const context = vm.createContext({
    document: { getElementById: (id) => {
      assert.ok(nodes[id], `Missing HTML ID: ${id}`);
      return nodes[id];
    }, createElement: (tag) => new Node(tag), activeElement: nodes["add-expense"] },
    Option: class extends Node { constructor(text, value) { super("option", text); this.value = value; } },
    FormData: class {
      *[Symbol.iterator]() {
        for (const name of ["amount", "category", "description", "date"]) yield [name, nodes[name].value];
      }
    },
    URLSearchParams,
    fetch: async (...args) => { calls.push(args); return handler(...args); },
  });
  vm.runInContext(source, context);
  const flush = () => new Promise((resolve) => setImmediate(resolve));
  await flush();
  return { nodes, calls, context, flush, handle: (callback) => { handler = callback; },
    run: (script) => vm.runInContext(script, context) };
}

test("initial dashboard uses Python API, text-only rendering and precision-safe IDs", async () => {
  const app = await setup();
  assert.match(app.calls[0][0], /^\/api\/expenses\?month=/);
  assert.equal(app.nodes["total-spent"].textContent, "12.50");
  assert.equal(app.nodes["transaction-count"].textContent, "1");
  assert.equal(app.nodes["expense-rows"].children[0].children[0].textContent, fixture().expenses[0].description);
  assert.equal(app.nodes["daily-chart"].children.length, 1);
  assert.equal(app.nodes["category-chart"].children.length, 1);
  assert.equal(app.nodes.loading.hidden, true);
});

test("money and chart ratios preserve cents above JavaScript safe integer range", async () => {
  const app = await setup();
  assert.equal(app.run('money("900719925474099312")'), "9,007,199,254,740,993.12");
  const summary = fixture().summary;
  summary.total_cents = "900719925474099312";
  summary.by_category[0].amount_cents = summary.total_cents;
  summary.by_day[0].amount_cents = summary.total_cents;
  app.context.summary = summary;
  app.run("renderCharts(summary)");
  assert.equal(app.nodes["daily-chart"].children[0].children[0].children[0].style.height, "100%");
  assert.equal(app.nodes["category-chart"].children[0].children[1].children[0].style.width, "100%");
});

test("category/month filters refresh every surface and reset to current month", async () => {
  const app = await setup();
  app.nodes["month-filter"].value = "2026-10";
  app.nodes["category-filter"].value = "food";
  await app.nodes["category-filter"].dispatch("change");
  assert.match(app.calls.at(-1)[0], /month=2026-10&category=food/);
  await app.nodes["reset-filters"].dispatch("click");
  await app.flush();
  assert.equal(app.nodes["category-filter"].value, "");
  assert.match(app.nodes["month-filter"].value, /^\d{4}-\d{2}$/);
});

test("add dialog sends decimal strings and closes only after persistence", async () => {
  const app = await setup();
  await app.nodes["add-expense"].dispatch("click");
  assert.equal(app.nodes["expense-dialog"].open, true);
  for (const [name, value] of Object.entries({ amount: "0.30", category: "Food", description: "Lunch", date: "2026-11-11" })) app.nodes[name].value = value;
  await app.nodes["expense-form"].dispatch("submit");
  const call = app.calls.find(([, options]) => options.method === "POST");
  assert.equal(JSON.parse(call[1].body).amount, "0.30");
  assert.equal(call[1].headers["X-Expense-Request"], "1");
  assert.equal(app.nodes["expense-dialog"].open, false);
  assert.equal(app.nodes.notice.textContent, "Expense added.");
});

test("edit retains full ID and delete requires confirmation", async () => {
  const app = await setup();
  const buttons = app.nodes["expense-rows"].children[0].children[4].children[0].children;
  await buttons[0].dispatch("click");
  assert.equal(app.nodes.amount.value, "12.50");
  app.nodes.amount.value = "10.10";
  await app.nodes["expense-form"].dispatch("submit");
  assert.equal(app.calls.find(([, options]) => options.method === "PUT")[0], `/api/expenses/${fixture().expenses[0].id}`);
  await buttons[1].dispatch("click");
  assert.equal(app.calls.some(([, options]) => options.method === "DELETE"), false);
  await app.nodes["cancel-delete"].dispatch("click");
  assert.equal(app.nodes["delete-dialog"].open, false);
  await buttons[1].dispatch("click");
  await app.nodes["confirm-delete"].dispatch("click");
  assert.equal(app.calls.find(([, options]) => options.method === "DELETE")[0], `/api/expenses/${fixture().expenses[0].id}`);
  assert.equal(app.nodes["delete-dialog"].open, false);
});

test("failed mutations retain entered values and show errors", async () => {
  const app = await setup();
  app.handle(async () => ({ ok: false, json: async () => ({ error: "Database unavailable" }) }));
  await app.nodes["add-expense"].dispatch("click");
  app.nodes.amount.value = "1.25";
  app.nodes.description.value = "Keep this";
  await app.nodes["expense-form"].dispatch("submit");
  assert.equal(app.nodes["expense-dialog"].open, true);
  assert.equal(app.nodes.description.value, "Keep this");
  assert.equal(app.nodes["form-error"].textContent, "Database unavailable");
  assert.equal(app.nodes["save-expense"].disabled, false);
  app.context.record = fixture().expenses[0];
  app.run("openDelete(record)");
  await app.nodes["confirm-delete"].dispatch("click");
  assert.equal(app.nodes["delete-dialog"].open, true);
  assert.equal(app.nodes["delete-error"].textContent, "Database unavailable");
});

test("zero and malformed amounts are rejected without a write", async () => {
  const app = await setup();
  for (const amount of ["0", "00.00", "1e2", "-1", "1.001"]) {
    app.nodes.amount.value = amount;
    await app.nodes["expense-form"].dispatch("submit");
    assert.equal(app.nodes["form-error"].hidden, false, amount);
  }
  assert.equal(app.calls.some(([, options]) => options.method !== "GET"), false);
});

test("empty data renders empty states without division by zero", async () => {
  const app = await setup();
  const data = fixture();
  data.expenses = [];
  data.summary = { total_cents: "0", count: 0, category_count: 0, by_day: [], by_category: [] };
  app.handle(async () => ({ ok: true, json: async () => data }));
  await app.nodes.refresh.dispatch("click");
  assert.equal(app.nodes["empty-state"].hidden, false);
  assert.equal(app.nodes["total-spent"].textContent, "0.00");
  assert.equal(app.nodes["average-expense"].textContent, "0.00");
  assert.equal(app.nodes["expense-rows"].children.length, 0);
  assert.match(app.nodes["daily-chart"].textContent, /will appear here/);
});

test("load failures are explicit and retry clears the error", async () => {
  const app = await setup();
  app.handle(async () => { throw new Error("Offline"); });
  await app.nodes.refresh.dispatch("click");
  assert.match(app.nodes.notice.textContent, /Offline/);
  assert.equal(app.nodes.notice.className, "error");
  app.handle(async () => ({ ok: true, json: async () => fixture() }));
  await app.nodes.refresh.dispatch("click");
  assert.equal(app.nodes.notice.hidden, true);
});

test("out-of-order responses never overwrite newer filter results", async () => {
  const app = await setup();
  let release;
  app.handle(() => new Promise((resolve) => { release = resolve; }));
  const old = app.run("loadExpenses()");
  const newer = fixture();
  newer.summary.total_cents = "5000";
  app.handle(async () => ({ ok: true, json: async () => newer }));
  await app.run("loadExpenses()");
  release({ ok: true, json: async () => fixture() });
  await old;
  assert.equal(app.nodes["total-spent"].textContent, "50.00");
});
