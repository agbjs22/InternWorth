# Charts And Drawings

Worksheets expose drawing collections for charts, images, and shapes.

## Charts

```ts
const chart = sheet.charts.add("bar", {
  from: { row: 1, col: 4 },
  extent: { widthPx: 420, heightPx: 260 },
});
chart.title = "Values";
chart.categories = ["A", "B", "C"];
const series = chart.series.add("Value");
series.values = [3, 5, 8];
series.categories = chart.categories;
```

Charts can be resolved from inspect anchors:

```ts
const chart = workbook.resolve("ch/<chartId>");
```

### Edit The Chart Frame

```ts
chart.roundedCorners = true;
chart.roundedCorners = false;
chart.roundedCorners = null;
const roundedCorners = chart.roundedCorners;
```

### Edit Chart Family Options

```ts
histogram.apply({ histogramOptions: { binCount: 8, underflow: 0, overflow: 30 } });
histogram.apply({ histogramOptions: { binWidth: null, binCount: null } });
histogram.apply({ histogramOptions: { underflow: null, overflow: null } });
bubble.bubbleOptions = { scale: 150, sizeRepresents: "width" };
bubble.bubbleOptions = { scale: null, sizeRepresents: null };
const settings = bubble.bubbleOptions;
```

[Chart family options](../../../presentations/api/references/charts.spec.md#chart-family-options)

### Edit Error Bars

```ts
const errorBars = chart.series.getItemAt(0).errorBars;
errorBars.apply("y", { type: "fixedValue", value: 2 });
errorBars.apply("y", {
  display: "both",
  endStyle: "cap",
  line: { fill: "accent1", width: 1.5, style: "solid" },
});
const editableDirections = errorBars.directions;
const settings = errorBars.get("y");
errorBars.apply("y", { line: { width: null } });
errorBars.apply("y", { type: "none" });
```

### Edit Individual Trendlines

```ts
const trendlines = chart.series.getItemAt(0).trendlines;
const types = trendlines.supportedTypes;
const trendline = trendlines.add("linear", { name: "Forecast" });
trendline.apply({
  forecastForward: 2,
  displayEquation: true,
  line: { fill: "accent2", width: 2, style: "dashed" },
  label: {
    numberFormatCode: "0.00",
    numberFormatSourceLinked: false,
    textStyle: { fontSizePt: 12, typeface: "Arial", color: "accent2" },
    manualLayout: { x: 0.2, y: 0.3 },
    fill: "#FFFFFF",
    line: { fill: "accent2", width: 1 },
  },
});
trendline.apply({ forecastForward: null });
trendlines.deleteAt(0);
```

### Replace Chart Data

```ts
chart.setData("A1:C8");
chart.setData("'Source data'!A1:C8");
chart.setData(["'Source data'!A1:A8", "D1:D8", "G1:G8"]);
```

| Chart | Source columns |
| --- | --- |
| Bar, line, area, pie | Categories, then one column per series |
| Scatter | X values, then one Y column per series |
| Bubble | X, Y, Size per series |
| Treemap or sunburst | Outer-to-inner category levels, then values |
| Box and whisker or histogram | One numeric column per sample series |

### Empty Cells

```ts
chart.displayBlanksAs = "gap";
chart.displayBlanksAs = "zero";
chart.displayBlanksAs = "span";
chart.displayBlanksAs = null;
chart.displayBlanksAsOptions;
```

### Edit One Series Binding

```ts
const series = chart.series.getItemAt(0);
series.valuesSource = "'Source data'!D2:D8";
series.categoriesSource = "A2:A8";
series.xValuesSource = "B2:B8";
// Bubble charts:
series.bubbleSizesSource = "C2:C8";
// Treemap and sunburst charts:
series.categoryPathsSource = "A2:B8";
```

### Edit An Axis

```ts
const axes = chart.getAxisTargets(); // { axisId: number, axis: "x" | "y" }[]
const axisId = axes[0].axisId;
const axis = chart.getAxisById(axisId);
chart.applyAxis(axisId, {
  min: 0,
  max: 100,
  title: { text: "Value", textStyle: { bold: true } },
});
```

### Scoped Data Labels

```ts
const target = { scope: "point", seriesIndex: 0, pointIndex: 1 } as const;
const targetExists = chart.hasDataLabelTarget(target);
const labels = chart.getDataLabels(target);
chart.applyDataLabels(target, { textStyle: { bold: true }, separator: " / " });
chart.applyDataLabels(target, { showValue: false });
chart.applyDataLabels(target, { showValue: null }); // Restore the parent flag.
chart.applyDataLabels(target, null); // Remove the entire point override.
chart.applyDataLabels({ scope: "series", seriesIndex: 0 }, {
  showValue: true, numberFormatCode: "0.00",
});
chart.applyDataLabels({ scope: "chart" }, { position: "outEnd" });
```

### Series Markers And Bar Spacing

```ts
chart.applySeriesStyle(0, {
  marker: { symbol: "diamond", size: 8, fill: "#156082" },
});
chart.applySeriesStyle(0, { marker: { size: 12 } });
chart.applySeriesStyle(0, { stroke: { style: "dashed", compound: "double" } });
chart.applySeriesStyle(0, { stroke: { width: 3 } });
chart.format.apply({ barOptions: { gapWidth: 150, overlap: 0 } });
```

## Chart To Image

```ts
const result = await workbook.chartToImage(0, chart.id);
```

## Images

```ts
const image = sheet.images.add({
  blob: imageBytes,
  contentType: "image/png",
  anchor: {
    from: { row: 1, col: 2 },
    extent: { widthPx: 240, heightPx: 160 },
  },
});

image.id;
image.bytes;
image.contentType;
image.prompt;
image.uri;
```

## Shapes

```ts
const shape = sheet.shapes.add({
  geometry: "rect",
  anchor: {
    from: { row: 2, col: 3 },
    extent: { widthPx: 240, heightPx: 80 },
  },
  fill: "#f8fafc",
  line: { fill: "#334155", width: 1 },
});
shape.text = "Label";
shape.geometry = "roundRect";
shape.geometry; // "roundRect"
shape.borderRadius = 16;
shape.borderRadius;
shape.borderRadiusApplies;
```

## Sparklines

```ts
const group = sheet.sparklineGroups.add({
  targetRange: sheet.getRange("D2:D10"),
  sourceData: sheet.getRange("B2:C10"),
  type: "line",
});

group.apply({
  sourceData: "'Source data'!B2:C12",
  locationRange: "D2:D12",
  type: "line",
  lineWeight: 2,
  dateAxisRange: "'Source data'!B1:C1",
  displayHidden: false,
  axis: { manualMin: 0, manualMax: 100 },
});

group.apply({ axis: { manualMin: undefined, manualMax: undefined } });
group.apply({ dateAxisRange: undefined }); // Restore evenly spaced samples.

group.sourceAddress;
group.dateAxisAddress;
group.dateAxisFormula;
group.uid;
```

## Auto Layout

```ts
sheet.autoLayoutDrawings(sheet.charts.items, {
  direction: "vertical",
  frame: { startCell: "E2", width: 800, height: 1200 },
  gap: 16,
  padding: 24,
});
```

## Cookbook

```ts
sheet.getRange("A1:B4").values = [
  ["Name", "Value"],
  ["A", 3],
  ["B", 5],
  ["C", 8],
];

sheet.charts.add("bar", {
  from: { row: 1, col: 4 },
  extent: { widthPx: 420, heightPx: 260 },
});
```
