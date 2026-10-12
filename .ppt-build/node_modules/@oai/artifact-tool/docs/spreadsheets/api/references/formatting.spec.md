# Formatting, Validation, And Theme

Use range formatting for cell style, worksheet collections for validation and
conditional formatting, and `workbook.colorScheme` for workbook theme colors.

## Range Format

```ts
range.format = {
  fill: "#f8fafc",
  font: {
    name: "Aptos",
    bold: true,
    underline: "single",
    color: "#0f172a",
    size: 11,
  },
  borders: {
    bottom: { style: "thin", color: "#94a3b8" },
  },
  numberFormat: "$#,##0.00",
  horizontalAlignment: "center",
  verticalAlignment: "middle",
  wrapText: true,
  rowHeightPx: 28,
  columnWidthPx: 120,
};
```

### Cell fills

```ts
range.format.fill = {
  type: "gradient",
  angleDeg: 45,
  offsetScale: 100000,
  stops: [
    { offset: 0, color: "accent1" },
    { offset: 100000, color: "#ffffff" },
  ],
};
range.format.fill = {
  type: "solid",
  color: "#ffffff",
  pattern: { type: "lightGrid", color: "#64748b" },
};
```

### Reading mixed formatting

```ts
const summary = range.format.getSummary();
if (summary.font.bold.state === "uniform") {
  console.log(summary.font.bold.value);
}
range.format = { font: { bold: true } };
```

## Number Format

```ts
range.setNumberFormat("0.0%");
```

## Conditional Formatting

```ts
sheet.getRange("B2:B10").conditionalFormats.add("cellIs", {
  operator: "greaterThan",
  formula: 10,
  format: {
    fill: "#dcfce7",
    font: { bold: true, color: "#166534" },
  },
});
```

### Add and edit rules

```ts
const rule = sheet.conditionalFormattings.add({
  range: "C2:C20",
  rule: {
    type: "cellIs",
    operator: "greaterThan",
    formula: "=$B2",
    format: { font: { bold: true, underline: "single" }, numberFormat: "0.0%" },
  },
  stopIfTrue: true,
});
rule.assign({ ranges: ["C2:C20", "E2:E20"] });
rule.assign({ stopIfTrue: false });
const sameRule = sheet.conditionalFormattings.getItem(rule.id);
const matchingRules = sheet.conditionalFormattings.getIntersecting("C5");
rule.moveBefore(null); // Last priority.
```

### Edit rule formatting

```ts
rule.assign({
  formatPatch: {
    font: { bold: false, color: null }, // Reset the font color override.
    border: { bottom: { style: "double" } },
    numberFormat: "0.00%",
  },
});
rule.assign({ ranges: ["E4:E20"], formatPatch: { font: { italic: true } } });
```

### Text predicates

```ts
const textRule = sheet.conditionalFormattings.add({
  range: "A2:A20",
  rule: {
    type: "containsText",
    text: "ready",
    formula: '=AND(ISNUMBER(SEARCH("ready",A2)),B2>0)',
    format: { fill: "accent2" },
  },
});
textRule.assign({
  predicatePatch: { type: "containsText", text: "approved" },
  formatPatch: { font: { bold: true } },
  ranges: ["C4:C22"],
});
textRule.assign({
  predicatePatch: { type: "containsText", formula: null },
});
```

### Date-period formula overrides

```ts
const dates = sheet.conditionalFormattings.add({
  range: "B2:B20",
  rule: {
    type: "timePeriod",
    timePeriod: "last7Days",
    formula: "=AND(B2>=TODAY()-7,B2<=TODAY())",
    format: { fill: "accent2" },
  },
});
const dateConfig = dates.config;
if (dateConfig.supported && dateConfig.rule.type === "timePeriod") {
  dates.assign({ rule: { ...dateConfig.rule, formula: "=B2=TODAY()" } });
  dates.assign({ rule: { ...dateConfig.rule, formula: undefined } });
}
```

### Data bars

```ts
const bars = sheet.conditionalFormattings.add({
  range: "B2:B20",
  rule: {
    type: "dataBar",
    color: "accent1",
    gradient: false,
    showValue: true,
    minLength: 0,
    maxLength: 100,
    direction: "leftToRight", // "context" | "leftToRight" | "rightToLeft"
    axisPosition: "automatic", // "automatic" | "middle" | "none"
    border: true,
    borderColor: "accent1",
    negativeBarColorSameAsPositive: false,
    negativeFillColor: "accent2",
    negativeBarBorderColorSameAsPositive: false,
    negativeBorderColor: "accent2",
    axisColor: "text1",
    thresholds: [{ type: "autoMin" }, { type: "autoMax" }],
  },
});
const snapshot = bars.config;
if (snapshot.supported && snapshot.rule.type === "dataBar") {
  bars.assign({ rule: { ...snapshot.rule, showValue: false } });
}
```

### Icon sets

```ts
sheet.conditionalFormattings.add({
  range: "C2:C20",
  rule: {
    type: "iconSet",
    iconSet: "3Arrows",
    thresholds: [
      { type: "num", value: 0 },
      { type: "formula", value: "=$E$2", gte: false },
      { type: "formula", value: "=$E$3", gte: true },
    ],
  },
});
```

### Clear and delete rules

```ts
sheet.conditionalFormattings.clear("E5:E6");
rule.delete();
```

## Data Validation

```ts
sheet.getRange("A2:A10").dataValidation = {
  list: {
    source: ["Open", "Closed"],
    inCellDropDown: true,
  },
  allowBlank: true,
};
```

The range setter accepts list assignments or validation config
objects.

```ts
sheet.getRange("B2:B20").dataValidation = {
  rule: { type: "whole", operator: "between", formula1: 0, formula2: 100 },
  ignoreBlanks: true,
  prompt: { show: true, title: "Score", message: "Enter 0–100." },
  errorAlert: {
    show: true,
    style: "warning",
    message: "Outside the expected range.",
  },
};
sheet.getRange("B5").dataValidation.clear();
```

### Check cell values

```ts
const cell = sheet.getRange("B2");
const check = workbook.checkCellValue(sheet.name, "B2", 150);
const result = cell.setValueChecked(150);
if (
  !result.applied &&
  !result.validation.valid &&
  result.validation.style !== "stop"
) {
  // After the user confirms the warning/information message:
  cell.setValueChecked(150, { acceptWarning: true });
}
```

## Freeze Panes

```ts
sheet.freezePanes.freezeRows(1);
sheet.freezePanes.freezeColumns(1);
sheet.freezePanes.unfreeze();
```

## Theme

```ts
const current = workbook.colorScheme;
console.log(current.name, current.themeColors.accent1);

workbook.colorScheme = {
  name: "Workbook Theme",
  themeColors: {
    accent1: "#2563eb",
    accent2: "#0f766e",
    bg1: "#ffffff",
    tx1: "#0f172a",
  },
};
```

## Cookbook

```ts
const header = sheet.getRange("A1:C1");
header.format = {
  fill: "#0f172a",
  font: { bold: true, color: "#ffffff" },
  horizontalAlignment: "center",
};
sheet.freezePanes.freezeRows(1);
```
