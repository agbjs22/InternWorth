# Lookup And Reference Formulas

Lookup and reference formulas locate values and return addresses or dimensions. Follow the main skill’s scalar-formula policy and the [XLSX compatibility guidance](../API_QUICK_START.md#known-formulaexport-limitations-not-exhaustive).

## Formula Pattern

```ts
const formulaBlock = sheet.getRange(outputRange).write({
  formulas: formulaMatrix,
});
workbook.recalculate();
const results = formulaBlock.values;
```

## Common Shapes

```ts
const formulas = [
  `=_xlfn.XLOOKUP(${lookupRef},${lookupRangeRef},${returnRangeRef})`,
  `=VLOOKUP(${lookupRef},${tableRangeRef},${columnIndexRef},${exactRef})`,
  `=INDEX(${rangeRef},${rowIndexRef},${columnIndexRef})`,
  `=MATCH(${lookupRef},${lookupRangeRef},${matchModeRef})`,
];
```
