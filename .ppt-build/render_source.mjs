import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const source = "D:/my desktop/study/nlp/InternWorth.pptx";
const outDir = "D:/my desktop/study/nlp/internworth_mvp/InternWorth/.ppt-build/source-renders";
await fs.mkdir(outDir, { recursive: true });
const presentation = await PresentationFile.importPptx(await FileBlob.load(source));
for (let index = 0; index < presentation.slides.items.length; index += 1) {
  const png = await presentation.slides.items[index].export({ format: "png", scale: 1.5 });
  await fs.writeFile(path.join(outDir, `slide-${String(index + 1).padStart(2, "0")}.png`), new Uint8Array(await png.arrayBuffer()));
}
console.log(`Rendered ${presentation.slides.items.length} slides`);
