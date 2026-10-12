# Presentation Quick Start (TypeScript)

## API Docs

API docs: `api/API_DOCS.md`

`Presentation` is the in-memory API object. A deck is the exported presentation
file. A slide is one page in the deck.

## Text formatting

Assign formatting to `shape.text.style`, or edit properties on `shape.text`:

```ts
shape.text.style = { fontSize: 24, color: "#123456", bold: true };
shape.text.fontSize = 28;
shape.text.color = "#2563eb";
```

Reading `shape.text.style` returns a style name or `undefined`. Use
`shape.text.fontSize` and `shape.text.color` to read or edit formatting.
Assign a config to `shape.text.style` to change several fields at once. See
[rich text](api/references/rich-text.spec.md#shape-text-style) for accepted fields
and types.

## Imports

```ts
import fs from "node:fs/promises";
import { FileBlob, Presentation, PresentationFile } from "@oai/artifact-tool";
```

## Create, Render, Export

This script creates an editable deck, renders each slide PNG, and exports PPTX.

```ts
import fs from "node:fs/promises";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

async function writeBlob(path: string, blob: Blob): Promise<void> {
  await fs.writeFile(path, new Uint8Array(await blob.arrayBuffer()));
}

async function main(): Promise<void> {
  await fs.mkdir("output", { recursive: true });

  const presentation = Presentation.create({
    slideSize: { width: 1280, height: 720 },
  });

  const slide = presentation.slides.add();
  slide.background.fill = "slate-50";

  // Every coordinate has a field name: left, top, width, and height.
  const page = { left: 72, top: 64, width: 1136, height: 592 };
  const gutter = 28;
  const leftCol = 430;
  const rightCol = page.width - leftCol - gutter;

  const eyebrow = slide.shapes.add({
    geometry: "textbox",
    position: { left: page.left, top: page.top, width: 280, height: 28 },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  eyebrow.text = "EDITABLE PRESENTATION";
  eyebrow.text.style = { fontSize: 12, bold: true, color: "slate-500" };

  const title = slide.shapes.add({
    geometry: "textbox",
    position: {
      left: page.left,
      top: page.top + 92,
      width: leftCol,
      height: 184,
    },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  title.text = "Build decks with editable objects";
  title.text.style = { fontSize: 42, bold: true, color: "slate-950" };

  const subtitle = slide.shapes.add({
    geometry: "textbox",
    position: {
      left: page.left,
      top: page.top + 292,
      width: leftCol,
      height: 96,
    },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  subtitle.text =
    "Rows, columns, grids, charts, tables, images, and text remain editable.";
  subtitle.text.style = { fontSize: 20, color: "slate-600" };

  const chartFrame = slide.shapes.add({
    geometry: "roundRect",
    name: "chart-frame",
    position: {
      left: page.left + leftCol + gutter,
      top: page.top + 92,
      width: rightCol,
      height: 388,
    },
    fill: "white",
    line: { style: "solid", fill: "slate-200", width: 1 },
    borderRadius: "rounded-2xl",
    shadow: "shadow-sm",
  });

  slide.charts.add("bar", {
    position: {
      left: chartFrame.position.left + 36,
      top: chartFrame.position.top + 52,
      width: chartFrame.position.width - 72,
      height: 280,
    },
    categories: ["Rows", "Grid", "Tokens"],
    series: [{ name: "Coverage", values: [3, 4, 5], fill: "accent1" }],
    hasLegend: false,
    dataLabels: { showValue: true, position: "outEnd" },
    yAxis: {
      majorGridlines: { style: "solid", fill: "slate-200", width: 1 },
    },
  });

  for (const [index, slide] of presentation.slides.items.entries()) {
    const stem = `slide-${String(index + 1).padStart(2, "0")}`;
    const png = await presentation.export({ slide, format: "png", scale: 1 });
    await writeBlob(`output/${stem}.png`, png);
  }

  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save("output/deck.pptx");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
```

Inspect every final slide at full size before delivery. After repairs, refresh
the affected slide previews, including slides affected by inherited changes.
Add the [optional inspection exports](#optional-inspection-exports) when needed.

Every line config requires `style`, including invisible lines such as
`{ style: "solid", fill: "none", width: 0 }`. Check the installed runtime's
docs for accepted fields before adapting a config from another library.

## Session callbacks

Edit the document through the callback's `presentation`. Declare helpers and
slide variables inside the callback. Use a loop, helper, or separate block for
each slide to reuse names such as `title` without redeclaring them in one scope.

Spaces' `inspect_artifact` and `execute_artifact_code` take a `code` string
containing one complete async function expression:
`(async ({ presentation }) => { ... })`. End it at the closing `}`. Omit a
trailing statement semicolon, imports, TypeScript types, and JSX. Include the
helpers and data needed by this call. Caller variables and declarations from
previous callbacks are outside its scope.

Pass style options to helpers as objects with named fields. For example,
`{ fontSize: 28, typeface: "Georgia", color: "#123456", bold: true }`
avoids passing a font name as the size or a boolean as the color. See
[text styles](api/references/rich-text.spec.md#shape-text-style).

When building the string in JavaScript, serialize data with `JSON.stringify`:

```js
const labels = ["Cost: $5", "First line\nSecond line", "A quoted \"label\""];
const code = `async ({ presentation }) => {
  const labels = ${JSON.stringify(labels)};
  for (const label of labels) {
    const slide = presentation.slides.add();
    const title = slide.shapes.add({
      geometry: "textbox",
      position: { left: 72, top: 64, width: 720, height: 96 },
      fill: "none",
      line: { style: "solid", fill: "none", width: 0 },
    });
    title.text = label;
    title.text.style = { fontSize: 28, color: "#123456" };
  }
  return { slides: presentation.slides.count };
}`;
// Pass code as the tool's code argument.
```

Use `JSON.stringify` for values containing quotes, backslashes, dollar signs,
or newlines. Use `String.raw` to preserve escape sequences in literal callback
source. Put slide code in separate functions or blocks. Splitting source with
a regex can break JavaScript syntax. When replacing source text, use
`source.replace(marker, () => replacement)` so `$&`, `$'`, and other replacement
tokens stay literal.

When Node is available, compile the assembled string before submitting it:

```js
import { Script } from "node:vm";

new Script("(\n" + code + "\n)"); // Compile only, without running the callback.
```

The local `artifactSession.run(async ({ presentation }) => { ... }, options)`
API takes a JavaScript function and can use variables from the same Node REPL.
Spaces takes the function as a string. Keep document reads and edits inside
the current callback for both APIs.

In Spaces, use the callback's `presentation` and `session`. The worker records
the edit and initializes CRDT state.

```js
async ({ presentation, session }) => {
  const slides = await presentation.inspect({
    select: "$.slides[*]",
    include: ["id", "index", "title"],
  });
  return { sessionId: session.sessionId, slides: slides.records };
}
```

`presentation.session` requires an attached local controller. Read `session`
from the callback parameter and leave controller and replica setup to the worker.

### Things to look out for

- Give elements explicit names such as `"headline"`. Names generated with
  `text.slice(0,32)` can differ from a later manually shortened lookup.
- Inspect current names or canonical IDs before an edit. Editing text can
  leave the element's name unchanged.
- Serialize callback values with `JSON.stringify` to preserve quotes,
  backslashes, dollar signs, and newlines.
- For literal text such as `"Cost: $5"`, use a JSONPath equality filter.
  Legacy `search` interprets regex characters, including `$`.
- Check that a lookup selects the intended element. For zero or multiple
  matches, inspect current names and text before editing.
- Use current inspect IDs for `resolve`/`delete`, raw layout IDs or exact
  layout names for slide creation, and current zero-based indexes for previews.

```js
const text = "Cost: $5";
await presentation.inspect({
  select: "$.slides[*].elements[?(@.text == " + JSON.stringify(text) + ")]",
  include: ["id", "name", "text"],
});
```

### Image sources in Spaces callbacks

For a remote Page edit, pass a selected Page or library image reference as
`path`. Local filesystem paths and embedded `blob` examples apply to local
authoring. The worker needs authorization or an upload through the Page owner
before it can render or commit a new source.

Use the source input field `path` when replacing an image reference:

```js
async ({ presentation }) => {
  const image = presentation.resolve("im/c3d4e5f6"); // ID from current inspect.
  image.replace({ path: "library-file:new-image-reference" });
}
```

An inspected `asset.uri` identifies the current source. Passing `uri` to
`replace` can leave that source unchanged. If the next tool call authorizes
only the new reference, hydration fails for the old source still in the deck.

Before previewing, inspect the current image sources. Set `hydrate_images: true`
and include each source needed by the preview in `image_references`. A montage
needs sources for the whole deck. A preview of selected slides needs their
sources. Each reference must resolve to accessible image bytes. See
[image replacement](api/references/images.spec.md#replace-source).

To replace a selected image and preview it, pass these tool arguments:

```js
const args = {
  page_id: pageId,
  idempotency_key: "replace-selected-image-01",
  hydrate_images: true,
  image_references: ["library-file:selected-image-reference"],
  code: String.raw`async ({ presentation }) => {
    const image = presentation.resolve("im/c3d4e5f6");
    image.replace({ path: "library-file:selected-image-reference" });
    await presentation.render({ slide: 0 });
  }`,
};
// Pass args to execute_artifact_code.
```

Use the current `pageId`, inspected image ID, and selected reference. This
example assumes slide zero needs only this source. Add any other sources on
that slide to `image_references`.

## JSX Compose Equivalent

Use JSX when the slide is naturally rows, columns, grids, or overlays.

```tsx
/** @jsxRuntime automatic */
/** @jsxImportSource @oai/artifact-tool/presentation-jsx */

const frame = { left: 72, top: 64, width: 1136, height: 592 };

slide.compose(
  <column name="content-frame" width="fill" height="fill" gap={28}>
    <row width="fill" height={72} align="center" justify="between">
      <paragraph name="eyebrow" className="text-slate-500 text-sm font-bold">
        EDITABLE PRESENTATION
      </paragraph>
      <paragraph className="text-slate-400 text-sm">Q2 planning</paragraph>
    </row>
    <row width="fill" height="fill" gap={28} align="stretch">
      <column width={430} height="fill" gap={18}>
        <paragraph
          name="primary-heading"
          className="text-slate-950 text-5xl font-bold leading-tight"
        >
          Build decks with editable objects
        </paragraph>
        <paragraph className="text-slate-600 text-xl leading-relaxed">
          Rows, columns, grids, charts, tables, images, and text remain
          editable.
        </paragraph>
      </column>
      <box
        name="chart-frame"
        width="fill"
        height="fill"
        className="bg-white rounded-2xl shadow-sm"
        line={{ style: "solid", fill: "slate-200", width: 1 }}
      >
        <chart
          name="coverage-chart"
          chartType="bar"
          categories={["Rows", "Grid", "Tokens"]}
          series={[{ name: "Coverage", values: [3, 4, 5], fill: "accent1" }]}
          hasLegend={false}
          width="fill"
          height="fill"
        />
      </box>
    </row>
  </column>,
  { frame, baseUnit: 8 },
);
```

## Import And Edit PPTX

Load a PPTX, inspect for stable ids, render the affected slide before and after
a focused edit, re-inspect, and export the edited PPTX.

```ts
const presentation = await PresentationFile.importPptx(
  await FileBlob.load("input.pptx"),
);

const before = await presentation.inspect({
  select: "$.slides[*].elements[?(search(@.text, 'Revenue'))]",
  include: ["id", "kind", "text", "position"],
});
console.log(before.ndjson);

const slide = presentation.resolve(slideIdFromInspect);
await writeBlob(
  "output/before-slide.png",
  await presentation.export({ slide, format: "png", scale: 1 }),
);

const target = presentation.resolve(anchorIdFromInspect);
target.text.replace("Revenue", "Updated revenue outlook");

await writeBlob(
  "output/after-slide.png",
  await presentation.export({ slide, format: "png", scale: 1 }),
);

const after = await presentation.inspect({
  select: "$.slides[*].elements[?(@.id == " + JSON.stringify(anchorIdFromInspect) + ")]",
  include: ["id", "kind", "text", "position"],
});
console.log(after.ndjson);

const pptx = await PresentationFile.exportPptx(presentation);
await pptx.save("output/edited-deck.pptx");
```

## Optional Inspection Exports

When investigating placement, export layout evidence for the affected slide
in the authoring process. Capture it before and after a change when comparison
is useful.

```ts
const layout = await slide.export({ format: "layout" });
await fs.writeFile("output/slide.layout.json", await layout.text());
```

For deck flow or changes affecting multiple slides, add an overview montage.
Continue to inspect individual slide PNGs at full size.

```ts
const montage = await presentation.export({
  format: "webp",
  montage: true,
});
await writeBlob("output/deck-montage.webp", montage);
```

## Local Image Bytes

Use byte-backed images for embedded PPTX assets.

```ts
async function readImageBlob(imagePath: string): Promise<ArrayBuffer> {
  const bytes = await fs.readFile(imagePath);
  return bytes.buffer.slice(
    bytes.byteOffset,
    bytes.byteOffset + bytes.byteLength,
  );
}

const imageBytes = await readImageBlob("assets/product.png");
slide.images.add({
  blob: imageBytes,
  contentType: "image/png",
  alt: "Product screenshot",
  fit: "cover",
  position: { left: 720, top: 96, width: 420, height: 280 },
  geometry: "roundRect",
  borderRadius: "rounded-xl",
});
```
