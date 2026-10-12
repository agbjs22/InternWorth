# Logical Formulas

Logical formulas branch, combine conditions, and handle error values. Follow the main skill’s formula policy and the [XLSX compatibility guidance](../API_QUICK_START.md#known-formulaexport-limitations-not-exhaustive).

## Formula Pattern

```ts
const formulaBlock = sheet.getRange(outputRange).write({
  formulas: formulaMatrix,
});
workbook.recalculate();
const results = formulaBlock.values;
```

## Boolean And Branching Shapes

```ts
const formulas = [
  `=TRUE()`,
  `=FALSE()`,
  `=NA()`,
  `=AND(${conditionRef1},${conditionRef2})`,
  `=OR(${conditionRef1},${conditionRef2})`,
  `=NOT(${conditionRef})`,
  `=XOR(${conditionRef1},${conditionRef2})`,
  `=IF(${conditionRef},${trueValueRef},${falseValueRef})`,
  `=_xlfn.IFS(${conditionRef1},${valueRef1},${conditionRef2},${valueRef2})`,
  `=SWITCH(${valueRef},${caseRef1},${resultRef1},${defaultRef})`,
];
```

## Error Handling Shapes

```ts
const formulas = [
  `=IFERROR(${valueRef},${replacementRef})`,
  `=IFNA(${valueRef},${replacementRef})`,
];
```
