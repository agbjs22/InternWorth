# Inspect and Help

`workbook.inspect({ select, include })` queries a semantic workbook tree with RFC 9535 JSONPath. The [JSON Schema](inspect.schema.json) describes the nodes and value semantics.

## Navigate before reading cells

```ts
const overview = await workbook.inspect({
  select: "$.sheets[*]",
  include: ["name", "range", "tables.name", "tables.range", "tables.columns.name"],
});
console.log(overview.records);

const statistics = await workbook.inspect({
  select: "$.sheets[?(@.name == 'Data')].columns[?(@.letter == 'B')].statistics",
  include: ["numericCount", "min", "max", "sum", "average", "errorCount"],
});
console.log(statistics.records);
```

The tree contains `sheets` and workbook-scoped `definedNames`. Sheets contain native `tables`, `charts`, `drawings`, `pivotTables`, `sparklines`, `slicers`, what-if `dataTables`, `threads`, classic `notes`, `dataValidations`, `conditionalFormats`, `mergedRanges`, `freezePanes`, and layout metadata. Select the fields needed for the decision. Objects retain public names, drawing IDs, or fully qualified A1 addresses for subsequent edits.

`regions` describes inferred data blocks separately from native tables. Each region bounds cells connected horizontally or vertically through nonblank values or formulas. Rectangles can contain blanks and can overlap; their statistics describe the full rectangle. Region column names are copied from text in the first row, without inferring a formal header or changing the workbook.

```ts
const regions = await workbook.inspect({
  select: "$.sheets[*].regions[*]",
  include: ["sheet", "range", "rowCount", "columnCount", "columns.name"],
});

const sources = await workbook.inspect({
  select: "$.sheets[*].charts[*]",
  include: ["sheet", "id", "title", "type", "series.name", "series.formula", "series.categoryFormula"],
});
```

Statistics use finite computed numbers. Numeric-looking strings, dates, booleans, blanks, and errors are counted separately. `min`, `max`, and `average` are `null` without numeric values; `sum` is zero. An overflowing sum is `null`. Native table column statistics exclude headers and totals. Sheet and inferred-region column statistics cover their reported ranges.

## Search content, formulas, and appearance

```ts
const matches = await workbook.inspect({
  select: "$.sheets[*].cells[?search(@.text, 'Revenue')]",
  include: ["sheet", "address", "text"],
});

const errors = await workbook.inspect({
  select: "$.sheets[*].cells[?(@.formula && @.valueType == 'error')]",
  include: ["sheet", "address", "formula", "error"],
});

const formatting = await workbook.inspect({
  select: "$.sheets[?(@.name == 'Data')].cells[?(@.row <= 10 && @.column <= 4)]",
  include: ["address", "value", "text", "computedStyle.numberFormat", "computedStyle.fillColor"],
});
```

Cells are sparse, sorted by row and column, and include materialized styled blanks. Untouched blank positions are absent; whole-row and whole-column layout spans are represented separately. Cell row/column numbers are one-based; sheet index is zero-based. `value` is JSON-safe, dates are ISO timestamps, and `valueType` distinguishes dates and errors from strings. Formulas include `=`. Follow the workbook calculation lifecycle: recalculate after formula/input edits before querying current computed results.

`text` is displayed text. `computedStyle` follows the renderer, including inheritance, table/pivot formatting, theme colors, number-format colors, and supported conditional effects. Fields contain format codes, readable alignments, point font sizes, and resolved colors. Conditional rule definitions are separately available, including visual effects such as data bars and icon sets.

Mixed rich text exposes resolved `runs`; `computedStyle.font` describes the cell default when runs differ. Cells also expose their `links`, applicable `validation`, and containing `mergedRange`. Sheet `layout` reports authored/default dimensions and hidden spans, without expanding entire rows or columns into blank cell records.

Filters run before exact projection. `include` is an array of fields on selected nodes; dotted paths project nested objects and arrays. JSONPath slices, unions, recursive traversal, and standard `match()`/`search()` functions work without another inspection language.

`match()` and `search()` are case-sensitive. For example, `search(@.text, '[Rr]evenue')` matches both `Revenue` and `revenue`. A legacy case-insensitive regex needs an explicit equivalent when moving to JSONPath.

## Complete results and sessions

```ts
const result = await workbook.inspect({
  select: "$.sheets[*].cells[?(@.formula)]",
  include: ["sheet", "address"],
  fileName: "formula-addresses.ndjson",
});
console.log(result.recordCount);
```

Files contain every selected record, with no hidden preview truncation. Narrow `select` and `include` to control size. `records` and `ndjson` remain available programmatically; ordinary result serialization returns count and output metadata. Return `result.records` explicitly from a session callback for a small immediate answer. Completed files are listed separately by the session runner.

```ts
type WorkbookInspectQueryOptions = {
  select: string;
  include?: readonly string[];
  fileName?: string;
};
```

The previous `kind`/`searchTerm` API remains a separate overload. JSONPath requests use `select`, `include`, and `fileName` only.

## Find cells and API guidance

```ts
const matches = workbook.findCells({
  searchTerm: "East", sheetId: "Data",
  options: { maxResults: 10, matchFormulas: true },
});
```

Result matches include sheet, address, value/formula match metadata, and total
count.

## Help

```ts
const help = workbook.help("*", {
  search: "colorScheme|worksheet.charts.add",
  include: ["index", "examples", "notes"],
  maxChars: 12000,
});
console.log(help.ndjson);
```

Common queries:

```text
*, workbook.colorScheme, worksheet.charts.add, formulas, enum.ChartType
```

## Navigate inspection results

Inspection IDs use each object's public navigation API. Select worksheets with `workbook.worksheets.getItem(id)`, cells with `sheet.getRange(address)`, and inferred regions with `sheet.getRange(range)`. Native table and slicer IDs are names for their sheet collections' `getItem(id)` methods; pivot IDs work with `workbook.pivotTables.getItem(id)`. Drawings retain their collection IDs. Include `sheet` when selecting objects across sheets.

Returned chart (`ch/<id>`) and thread (`th/<id>`) anchors work directly with `workbook.resolve`. Legacy worksheet anchors (`ws/<id>`) also continue to work; an inspection sheet's `id` is its public name, rather than a `ws/` anchor.

## Create/Edit Loop

```ts
const before = await workbook.inspect({
  select: "$.sheets[?(@.name == 'Data')].cells[?(@.row == 2 && @.column == 2)]",
  include: ["address", "value", "formula"],
});

const sheet = workbook.worksheets.getItem("Data");
sheet.getRange("B2").values = [["Closed"]];
workbook.recalculate();

const after = await workbook.inspect({
  select: "$.sheets[?(@.name == 'Data')].cells[?(@.row == 2 && @.column == 2)]",
  include: ["address", "value", "formula"],
});
```

## Inline Types

```ts
type WorkbookHelpOptions = {
  include?: string[] | string;
  search?: string;
  maxChars?: number;
};
```
