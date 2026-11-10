<!-- docsync:generated:v1 -->
# Frontend UI reference

Generated from HTML, CSS and JavaScript; do not edit manually.

Static inventory, not runtime inference or a full CSS/JavaScript syntax validator. Functionality comes from HTML data-doc and JavaScript @ui comments. Missing descriptions are Not Found. Raw source and field values are not published.

Source fingerprint: `dd7f8567a1e87b2af1601de27d82d758b5230174a2f144ab66a40a125ede1cde`

## <code>src/static/app.js</code>

[Source](../src/static/app.js)

### Named functions and classes

- <code>$</code>
- <code>api</code>
- <code>closeEditor</code>
- <code>deleteExpense</code>
- <code>element</code>
- <code>loadExpenses</code>
- <code>localDate</code>
- <code>money</code>
- <code>notify</code>
- <code>openDelete</code>
- <code>openEditor</code>
- <code>renderCharts</code>
- <code>renderRows</code>
- <code>saveExpense</code>

### Explicit functionality descriptions

<pre>Format exact integer cents with grouping, without floating-point currency arithmetic.</pre>
<pre>Return the device&#x27;s local calendar date rather than UTC.</pre>
<pre>Create text-only DOM nodes so expense descriptions cannot inject markup.</pre>
<pre>Show explicit storage/network failures or successful mutation confirmations.</pre>
<pre>Call same-origin Python JSON endpoints and reject non-success responses.</pre>
<pre>Draw accessible daily bars and category progress charts with exact values.</pre>
<pre>Render newest-first records and edit/delete controls without inline event handlers.</pre>
<pre>Refresh all dashboard surfaces together; ignore stale requests after filter changes.</pre>
<pre>Open a prefilled edit form or a new expense form with today&#x27;s local date.</pre>
<pre>Close the editor only when no mutation is in progress.</pre>
<pre>Persist validated form fields and keep errors/entered values visible on failure.</pre>
<pre>Ask for confirmation before removing a record from SQLite.</pre>
<pre>Delete only after explicit confirmation and retain the dialog on failure.</pre>

## <code>src/static/index.html</code>

[Source](../src/static/index.html)

### Page

<pre>Expense Tracker | Your spending, in focus</pre>
<pre>A private, local dashboard for your daily expenses.</pre>

### Headings

- <code>Spending overview</code>
- <code>Spending activity</code>
- <code>By category</code>
- <code>Transactions 0</code>
- <code>A fresh start</code>
- <code>Add expense</code>
- <code>Delete this expense?</code>

### Components and functionality

#### <code>Navigation</code>
<pre>Brand, dashboard navigation and local-storage status.</pre>
#### <code>Filters</code>
<pre>Month and category filters apply to transactions, summaries and charts together.</pre>
#### <code>Monthly summary</code>
<pre>Exact total, transaction count, average expense and largest category for the selected filters.</pre>
#### <code>Spending charts</code>
<pre>Accessible daily spending bars and category breakdown with exact amount labels and empty states.</pre>
#### <code>Transactions</code>
<pre>Newest-first expense table with category tags, exact amounts, edit/delete actions and loading, error and empty states.</pre>
#### <code>Expense editor</code>
<pre>Accessible add/edit dialog validates amount, category, description and date, persists through the Python API and reports failures without losing entered values.</pre>
#### <code>Delete confirmation</code>
<pre>Explicit confirmation before deleting an expense; failures stay visible and no optimistic data loss occurs.</pre>

### Controls

- <code>button #add-expense: Not Found</code>
- <code>input #month-filter: month</code>
- <code>select #category-filter: Not Found</code>
- <code>button #reset-filters: Not Found</code>
- <code>button #refresh: Not Found</code>
- <code>button #empty-add: Not Found</code>
- <code>dialog #expense-dialog: Not Found</code>
- <code>form #expense-form: Not Found</code>
- <code>button #close-dialog: button</code>
- <code>input #amount: text</code>
- <code>input #category: Not Found</code>
- <code>input #date: date</code>
- <code>input #description: Not Found</code>
- <code>button #cancel-expense: button</code>
- <code>button #save-expense: submit</code>
- <code>dialog #delete-dialog: Not Found</code>
- <code>button #cancel-delete: Not Found</code>
- <code>button #confirm-delete: Not Found</code>

### Linked assets

- <code>/app.js</code>
- <code>/styles.css</code>

## <code>src/static/styles.css</code>

[Source](../src/static/styles.css)

### Style selectors and responsive rules

- <code>#amount</code>
- <code>#delete-dialog &gt; p</code>
- <code>#delete-dialog h2</code>
- <code>#loading</code>
- <code>#notice</code>
- <code>#notice.error</code>
- <code>*</code>
- <code>*, *::before, *::after</code>
- <code>.bar-fill</code>
- <code>.bar-track</code>
- <code>.brand</code>
- <code>.brand &gt; span:last-child</code>
- <code>.brand &gt; span:last-child, .nav-label, .sidebar-bottom</code>
- <code>.brand-dot</code>
- <code>.brand-icon</code>
- <code>.breadcrumb</code>
- <code>.breadcrumb span</code>
- <code>.button</code>
- <code>.button span</code>
- <code>.category-chart</code>
- <code>.category-chart &gt; .chart-empty</code>
- <code>.category-fill</code>
- <code>.category-label</code>
- <code>.category-label span:first-child</code>
- <code>.category-label strong</code>
- <code>.category-row</code>
- <code>.category-row:nth-child(2n) .category-fill</code>
- <code>.category-row:nth-child(3n) .category-fill</code>
- <code>.category-tag</code>
- <code>.category-track</code>
- <code>.chart-empty</code>
- <code>.charts-grid</code>
- <code>.content</code>
- <code>.count-badge</code>
- <code>.currency-note</code>
- <code>.daily-chart</code>
- <code>.danger</code>
- <code>.day-bar</code>
- <code>.day-bar:hover .bar-fill, .day-bar:focus-visible .bar-fill</code>
- <code>.day-bar:nth-child(3n) .bar-fill</code>
- <code>.dialog-actions</code>
- <code>.dialog-actions .button</code>
- <code>.dialog-heading</code>
- <code>.dialog-heading h2</code>
- <code>.empty-icon</code>
- <code>.empty-state</code>
- <code>.empty-state p</code>
- <code>.eyebrow</code>
- <code>.featured</code>
- <code>.featured strong, .featured .stat-label</code>
- <code>.filter-bar</code>
- <code>.filter-bar .button</code>
- <code>.filter-group</code>
- <code>.filter-group input, .filter-group select</code>
- <code>.filter-group label</code>
- <code>.filter-group select</code>
- <code>.form-error</code>
- <code>.form-grid</code>
- <code>.icon-button</code>
- <code>.legend</code>
- <code>.legend i</code>
- <code>.muted</code>
- <code>.nav-item</code>
- <code>.nav-item span</code>
- <code>.nav-item.active</code>
- <code>.nav-item:hover</code>
- <code>.nav-label</code>
- <code>.nav-label, .eyebrow</code>
- <code>.numeric</code>
- <code>.page-footer</code>
- <code>.page-heading</code>
- <code>.page-heading .button</code>
- <code>.page-heading .muted</code>
- <code>.panel</code>
- <code>.panel-heading</code>
- <code>.panel-heading .muted</code>
- <code>.primary</code>
- <code>.primary:hover</code>
- <code>.profile</code>
- <code>.row-action</code>
- <code>.row-action.delete</code>
- <code>.row-action:hover</code>
- <code>.row-actions</code>
- <code>.sidebar</code>
- <code>.sidebar-bottom</code>
- <code>.sidebar-bottom p</code>
- <code>.skip-link</code>
- <code>.skip-link:focus</code>
- <code>.sr-only</code>
- <code>.stat-card</code>
- <code>.stat-card .category-stat</code>
- <code>.stat-card p</code>
- <code>.stat-card strong</code>
- <code>.stat-icon</code>
- <code>.stat-label</code>
- <code>.stats-grid</code>
- <code>.status-dot</code>
- <code>.subtle</code>
- <code>.subtle:hover</code>
- <code>.table-footer</code>
- <code>.table-footer span:last-child, .page-footer span:last-child</code>
- <code>.table-scroll</code>
- <code>.topbar</code>
- <code>.transactions-panel</code>
- <code>.transactions-panel .panel-heading</code>
- <code>:focus-visible</code>
- <code>:root</code>
- <code>@media (max-width: 1150px)</code>
- <code>@media (max-width: 480px)</code>
- <code>@media (max-width: 700px)</code>
- <code>@media (max-width: 900px)</code>
- <code>@media (min-width: 1600px)</code>
- <code>@media (prefers-reduced-motion: reduce)</code>
- <code>[hidden]</code>
- <code>a</code>
- <code>body</code>
- <code>button</code>
- <code>button, a, input, select</code>
- <code>button, input, select</code>
- <code>button:disabled</code>
- <code>dialog</code>
- <code>dialog::backdrop</code>
- <code>form &gt; .muted</code>
- <code>form input</code>
- <code>form label</code>
- <code>h1</code>
- <code>h2</code>
- <code>h3</code>
- <code>input, select</code>
- <code>main</code>
- <code>p</code>
- <code>table</code>
- <code>td</code>
- <code>td.numeric</code>
- <code>td:first-child</code>
- <code>th</code>
- <code>th, td</code>
