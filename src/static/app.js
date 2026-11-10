"use strict";

const $ = (id) => document.getElementById(id);
let records = [];
let editingId = null;
let deletingId = null;
let requestVersion = 0;
let mutationPending = false;
let opener = null;

/** @ui Format exact integer cents with grouping, without floating-point currency arithmetic. */
function money(cents) {
  const value = BigInt(cents);
  return `${(value / 100n).toLocaleString("en-US")}.${String(value % 100n).padStart(2, "0")}`;
}

/** @ui Return the device's local calendar date rather than UTC. */
function localDate() {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
}

/** @ui Create text-only DOM nodes so expense descriptions cannot inject markup. */
function element(tag, text = "", className = "") {
  const node = document.createElement(tag);
  node.textContent = text;
  node.className = className;
  return node;
}

/** @ui Show explicit storage/network failures or successful mutation confirmations. */
function notify(message, error = false) {
  $("notice").textContent = message;
  $("notice").className = error ? "error" : "";
  $("notice").hidden = false;
  $("notice").setAttribute("role", error ? "alert" : "status");
}

/** @ui Call same-origin Python JSON endpoints and reject non-success responses. */
async function api(path, method = "GET", data = null) {
  const options = { method, headers: { "X-Expense-Request": "1" } };
  if (data !== null) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(data);
  }
  const response = await fetch(path, options);
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || `Request failed (${response.status})`);
  return payload;
}

/** @ui Draw accessible daily bars and category progress charts with exact values. */
function renderCharts(summary) {
  const daily = $("daily-chart");
  const category = $("category-chart");
  daily.replaceChildren();
  category.replaceChildren();
  const max = summary.by_day.reduce((value, item) => {
    const cents = BigInt(item.amount_cents);
    return cents > value ? cents : value;
  }, 0n);
  for (const item of summary.by_day) {
    const label = `${item.date}: ${money(item.amount_cents)}`;
    const bar = element("div", "", "day-bar");
    bar.setAttribute("role", "listitem");
    bar.setAttribute("aria-label", label);
    bar.tabIndex = 0;
    bar.title = label;
    const track = element("div", "", "bar-track");
    const fill = element("div", "", "bar-fill");
    fill.style.height = `${Number(BigInt(item.amount_cents) * 10000n / max) / 100}%`;
    track.append(fill);
    const day = element("span", item.date.slice(8));
    day.setAttribute("aria-hidden", "true");
    bar.append(track, day);
    daily.append(bar);
  }
  for (const item of summary.by_category) {
    const row = element("div", "", "category-row");
    row.setAttribute("role", "listitem");
    const label = element("div", "", "category-label");
    label.append(element("span", item.category), element("strong", money(item.amount_cents)));
    const track = element("div", "", "category-track");
    const fill = element("div", "", "category-fill");
    fill.style.width = `${Number(BigInt(item.amount_cents) * 10000n / BigInt(summary.total_cents)) / 100}%`;
    track.append(fill);
    row.append(label, track);
    category.append(row);
  }
  if (!summary.by_day.length) daily.append(element("p", "Your spending activity will appear here.", "chart-empty"));
  if (!summary.by_category.length) category.append(element("p", "No category spending this month.", "chart-empty"));
}

/** @ui Render newest-first records and edit/delete controls without inline event handlers. */
function renderRows() {
  const rows = $("expense-rows");
  rows.replaceChildren();
  for (const record of [...records].reverse()) {
    const row = element("tr");
    const category = element("td");
    category.append(element("span", record.category, "category-tag"));
    const actions = element("td");
    const buttons = element("div", "", "row-actions");
    const edit = element("button", "Edit", "row-action");
    edit.setAttribute("aria-label", `Edit ${record.description}`);
    edit.addEventListener("click", () => openEditor(record));
    const remove = element("button", "Delete", "row-action delete");
    remove.setAttribute("aria-label", `Delete ${record.description}`);
    remove.addEventListener("click", () => openDelete(record));
    buttons.append(edit, remove);
    actions.append(buttons);
    row.append(element("td", record.description), category, element("td", record.date),
      element("td", money(record.amount_cents), "numeric"), actions);
    rows.append(row);
  }
  $("empty-state").hidden = records.length !== 0;
  $("record-count").textContent = `${records.length} expense${records.length === 1 ? "" : "s"}`;
  $("table-count").textContent = records.length;
}

/** @ui Refresh all dashboard surfaces together; ignore stale requests after filter changes. */
async function loadExpenses() {
  const version = ++requestVersion;
  $("loading").hidden = false;
  $("transactions").setAttribute("aria-busy", "true");
  const query = new URLSearchParams();
  if ($("month-filter").value) query.set("month", $("month-filter").value);
  if ($("category-filter").value) query.set("category", $("category-filter").value);
  try {
    const data = await api(`/api/expenses?${query}`);
    if (version !== requestVersion) return;
    records = data.expenses;
    const selected = $("category-filter").value;
    const categories = [...data.categories];
    if (selected && !categories.includes(selected)) categories.push(selected);
    $("category-filter").replaceChildren(new Option("All categories", ""));
    for (const category of categories) $("category-filter").add(new Option(category, category));
    $("category-filter").value = selected;
    const suggestions = new Set(["Food", "Transport", "Shopping", "Bills", "Health", "Entertainment", "Other", ...data.categories]);
    $("category-suggestions").replaceChildren(...[...suggestions].map((name) => new Option(name, name)));
    const summary = data.summary;
    $("total-spent").textContent = money(summary.total_cents);
    $("transaction-count").textContent = summary.count;
    const average = summary.count ? (BigInt(summary.total_cents) + BigInt(summary.count) / 2n) / BigInt(summary.count) : 0n;
    $("average-expense").textContent = money(average);
    $("period-label").textContent = $("month-filter").value || "All months";
    const top = summary.by_category.reduce((best, item) =>
      !best || BigInt(item.amount_cents) > BigInt(best.amount_cents) ? item : best, null);
    $("top-category").textContent = top ? top.category : "None yet";
    $("top-category-amount").textContent = top ? `${money(top.amount_cents)} across ${summary.category_count} categories` : "No spending yet";
    renderCharts(summary);
    renderRows();
    if ($("notice").classList.contains("error")) $("notice").hidden = true;
    return true;
  } catch (error) {
    if (version === requestVersion) {
      notify(`Could not load expenses. ${error.message} Use Refresh to retry. Displayed data may be out of date.`, true);
    }
    return false;
  } finally {
    if (version === requestVersion) {
      $("loading").hidden = true;
      $("transactions").setAttribute("aria-busy", "false");
    }
  }
}

/** @ui Open a prefilled edit form or a new expense form with today's local date. */
function openEditor(record = null) {
  opener = document.activeElement;
  editingId = record ? record.id : null;
  $("expense-form").reset();
  $("form-title").textContent = record ? "Edit expense" : "Add expense";
  $("save-expense").textContent = record ? "Save changes" : "Save expense";
  $("amount").value = record ? record.amount : "";
  $("category").value = record ? record.category : "";
  $("description").value = record ? record.description : "";
  $("date").value = record ? record.date : localDate();
  $("form-error").hidden = true;
  $("expense-dialog").showModal();
  $("amount").focus();
}

/** @ui Close the editor only when no mutation is in progress. */
function closeEditor() {
  if (!mutationPending) $("expense-dialog").close();
}

/** @ui Persist validated form fields and keep errors/entered values visible on failure. */
async function saveExpense(event) {
  event.preventDefault();
  if (mutationPending) return;
  const data = Object.fromEntries(new FormData($("expense-form")));
  if (!/^[0-9]+(?:\.[0-9]{1,2})?$/.test(data.amount) || /^0*(?:\.0{1,2})?$/.test(data.amount)) {
    $("form-error").textContent = "Enter a positive amount with at most two decimal places.";
    $("form-error").hidden = false;
    return;
  }
  mutationPending = true;
  $("save-expense").disabled = true;
  $("form-error").hidden = true;
  try {
    await api(editingId ? `/api/expenses/${editingId}` : "/api/expenses",
      editingId ? "PUT" : "POST", data);
    $("expense-dialog").close();
    notify(editingId ? "Expense updated." : "Expense added.");
    await loadExpenses();
  } catch (error) {
    $("form-error").textContent = error.message;
    $("form-error").hidden = false;
  } finally {
    mutationPending = false;
    $("save-expense").disabled = false;
  }
}

/** @ui Ask for confirmation before removing a record from SQLite. */
function openDelete(record) {
  opener = document.activeElement;
  deletingId = record.id;
  $("delete-description").textContent = `${record.description} - ${money(record.amount_cents)} on ${record.date}`;
  $("delete-error").hidden = true;
  $("delete-dialog").showModal();
  $("cancel-delete").focus();
}

/** @ui Delete only after explicit confirmation and retain the dialog on failure. */
async function deleteExpense() {
  if (mutationPending || !deletingId) return;
  mutationPending = true;
  $("confirm-delete").disabled = true;
  try {
    await api(`/api/expenses/${deletingId}`, "DELETE");
    $("delete-dialog").close();
    notify("Expense deleted.");
    await loadExpenses();
  } catch (error) {
    $("delete-error").textContent = error.message;
    $("delete-error").hidden = false;
  } finally {
    mutationPending = false;
    $("confirm-delete").disabled = false;
  }
}

$("month-filter").value = localDate().slice(0, 7);
$("add-expense").addEventListener("click", () => openEditor());
$("empty-add").addEventListener("click", () => openEditor());
$("close-dialog").addEventListener("click", closeEditor);
$("cancel-expense").addEventListener("click", closeEditor);
$("expense-form").addEventListener("submit", saveExpense);
$("confirm-delete").addEventListener("click", deleteExpense);
$("cancel-delete").addEventListener("click", () => { if (!mutationPending) $("delete-dialog").close(); });
for (const id of ["expense-dialog", "delete-dialog"]) {
  $(id).addEventListener("cancel", (event) => { if (mutationPending) event.preventDefault(); });
  $(id).addEventListener("close", () => { if (opener && opener.isConnected) opener.focus(); });
}
$("month-filter").addEventListener("change", loadExpenses);
$("category-filter").addEventListener("change", loadExpenses);
$("refresh").addEventListener("click", loadExpenses);
$("reset-filters").addEventListener("click", () => {
  $("month-filter").value = localDate().slice(0, 7);
  $("category-filter").value = "";
  loadExpenses();
});
loadExpenses();
