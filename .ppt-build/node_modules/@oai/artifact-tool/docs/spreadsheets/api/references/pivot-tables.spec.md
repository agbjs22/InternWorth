# Pivot Tables

## Create and Summarize

```ts
const data = workbook.worksheets.add("Data");
const output = workbook.worksheets.add("Summary");
data.getRange("A1:C5").values = [
  ["Region", "Product", "Sales"],
  ["East", "A", 10],
  ["East", "B", 20],
  ["West", "A", 30],
  ["West", "B", 40],
];

const pivot = output.pivotTables.add(
  "SalesSummary",
  data.getRange("A1:C5"),
  output.getRange("A1"),
);
pivot.rowHierarchies.add(pivot.hierarchies.getItem("Region"));
pivot.columnHierarchies.add(pivot.hierarchies.getItem("Product"));
const sales = pivot.dataHierarchies.add(pivot.hierarchies.getItem("Sales"));
sales.summarizeBy = "Sum";
sales.name = "Revenue";
sales.numberFormat = "#,##0.00";
pivot.layout.layoutType = "Tabular";

sales.field.name;
pivot.layout.getDataBodyRange().values;
```

## Show Values As

```ts
sales.showAs = { calculation: "PercentOfGrandTotal" };
sales.numberFormat = "0.0%";

const region = pivot.hierarchies.getItem("Region").fields.getItem("Region");
sales.showAs = {
  calculation: "DifferenceFrom",
  baseField: region,
  baseItem: region.items.getItem("East"),
};
```

```ts
sales.showAs = { calculation: "RunningTotal", baseField: region };
sales.showAs = { calculation: "PercentRunningTotal", baseField: region };
sales.showAs = { calculation: "RankDecending", baseField: region };
sales.showAs = { calculation: "PercentOfParentRowTotal" };
sales.showAs = { calculation: "Index" };
```

## Layout, Subtotals, and Sorting

```ts
pivot.layout.layoutType = "Tabular";
pivot.layout.showRowGrandTotals = false;
pivot.layout.showColumnGrandTotals = false;
pivot.layout.subtotalLocation = "AtBottom"; // "AtTop" | "AtBottom" | "Off"
pivot.layout.repeatAllItemLabels(true);
pivot.layout.displayBlankLineAfterEachItem(false);
pivot.styleName = "PivotStyleMedium2";
pivot.layout.hideValuesRow = true;

region.subtotals = { automatic: false };
region.subtotals = { sum: true, average: true, count: true };
region.sortByLabels("Ascending");
region.sortByValues("Descending", sales);
```

```ts
const product = pivot.hierarchies.getItem("Product").fields.getItem("Product");
region.sortByValues("Descending", sales, [product.items.getItem("A")]);
```

## Filter Fields

```ts
region.applyFilter({ manualFilter: { selectedItems: ["East"] } });
region.applyFilter({ labelFilter: { condition: "BeginsWith", substring: "E" } });
region.applyFilter({
  valueFilter: { condition: "GreaterThan", comparator: 25, value: "Revenue" },
});
region.clearAllFilters();
```

```ts
region.getFilters();
region.isFiltered();
region.isFiltered("Value");
region.clearFilter("Value");
region.clearAllFilters();
```

## Edit Hierarchies and Items

```ts
const hierarchy = pivot.rowHierarchies.getItem("Region");
hierarchy.name = "Area";
hierarchy.position = 0;
sales.position = 0;
const item = region.items.getItem("East");
item.name = "Atlantic";
item.isExpanded = false;
item.visible = false;
```

## Read and Delete

```ts
pivot.refresh();
const existing = workbook.pivotTables.getItemOrNullObject("SalesSummary");
if (existing !== null) {
  existing.dataHierarchies.items;
  existing.layout.getDataBodyRange();
}
pivot.rowHierarchies.remove(hierarchy);
pivot.dataHierarchies.remove(sales);
workbook.pivotTables.getItem("SalesSummary").delete();
```
