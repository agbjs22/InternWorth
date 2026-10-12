# Worksheet Drawings

Worksheets support charts and shapes anchored to the cell grid.

## Units

- Anchor row and column indexes are zero-based.
- Offsets and extents use pixels.
- Use `rowOffsetPx`, `colOffsetPx`, `widthPx`, and `heightPx`.

## Chart From Source Cells

Bind charts to source ranges so edits update their data. Define shared axis
configs at the top level of the persistent JavaScript REPL:

```js
var chartStyle = {
  axisText: { typeface: "Arial", fontSize: 13, fill: "dk2" },
};
```

Inside a session callback:

```js
const chart = sheet.charts.add("bar", sourceRange);
chart.setPosition(startCell, endCell);
chart.xAxis = { textStyle: chartStyle.axisText };
chart.yAxis = { textStyle: chartStyle.axisText, numberFormatCode: "#,##0", numberFormatSourceLinked: false };
```

Apply the workbook's font, palette, units, and [chart guidance](../API_QUICK_START.md#charts).
For line charts, set the series line stroke explicitly. Use config-object chart
creation for custom series; range-backed charts are the default when cells hold
the source data. The common [spreadsheet quick start](../API_QUICK_START.md#charts) lists range binding
and XLSX chart-type limitations.

## Chart Inline Types

```ts
type WorksheetChartType =
  | "bar" | "line" | "area" | "pie" | "doughnut" | "scatter"
  | "bubble" | "radar" | "stock";

type WorksheetChartConfig = {
  from?: { row: number; col: number; rowOffsetPx?: number; colOffsetPx?: number };
  to?: { row: number; col: number; rowOffsetPx?: number; colOffsetPx?: number };
  extent?: { widthPx?: number; heightPx?: number };
  title?: string;
  titleTextStyle?: TextStyleConfig;
  categories?: string[];
  series?: Array<{ name: string; values?: number[]; categories?: string[]; fill?: FillConfig; line?: LineConfig }>;
  hasLegend?: boolean;
  legend?: { position?: "left" | "top" | "topRight" | "right" | "bottom"; overlay?: boolean; textStyle?: TextStyleConfig };
  xAxis?: ChartAxisConfig;
  yAxis?: ChartAxisConfig;
  dataLabels?: { showValue?: boolean; position?: "center" | "inEnd" | "outEnd"; textStyle?: TextStyleConfig };
  dataTable?: { visible?: boolean; showLegendKey?: boolean; textStyle?: TextStyleConfig };
};

type TextStyleConfig = {
  typeface?: string;
  bold?: boolean;
  italic?: boolean;
  fontSize?: number;
  color?: ColorConfig;
  fill?: FillConfig;
  alignment?: "left" | "center" | "right" | "justify";
};

type ChartAxisConfig = {
  title?: string | { text?: string; textStyle?: TextStyleConfig };
  min?: number;
  max?: number;
  numberFormatCode?: string;
  numberFormatSourceLinked?: boolean;
  position?: "left" | "right" | "top" | "bottom";
  tickLabelPosition?: "high" | "low" | "nextTo" | string;
  textStyle?: TextStyleConfig;
  line?: LineConfig;
  majorGridlines?: LineConfig | null;
  minorGridlines?: LineConfig | null;
};
```

## Chart From Range

```ts
const chart = sheet.charts.add(chartType, sourceRange, seriesBy);
chart.setPosition(startRange, endRange);
chart.width = widthPx;
chart.height = heightPx;
```

## Shape Config

```ts
const shape = sheet.shapes.add({
  geometry,
  anchor,
  fill,
  line,
  name,
});
```

## Shape Inline Type

```ts
type WorksheetShapeConfig = {
  geometry: string; // common: "rect", "roundRect", "ellipse", "textbox"; full list is the slide shape preset list
  anchor?: DrawingAnchorConfig;
  fill?: FillConfig;
  line?: LineConfig;
  name?: string;
};

type DrawingAnchorConfig = {
  from: { row: number; col: number; rowOffsetPx?: number; colOffsetPx?: number };
  to?: { row: number; col: number; rowOffsetPx?: number; colOffsetPx?: number };
  extent?: { widthPx?: number; heightPx?: number };
};
```

## Rebuild And Layout

For an authorized rebuild, delete only the drawings being replaced.

```ts
const drawings = [...sheet.charts.items, ...sheet.shapes.items];
sheet.autoLayoutDrawings(drawings, {
  direction,
  frame,
  gap,
  padding,
});
```

## Auto Layout Inline Type

```ts
type WorksheetDrawingAutoLayoutOptions = {
  direction?: "vertical" | "horizontal" | "grid";
  align?: "start" | "center" | "end";
  columns?: number; // used for grid
  gap?: number;
  padding?: number;
  frame?:
    | { left: number; top: number; width: number; height: number }
    | { startCell: string; width: number; height: number };
};
```
