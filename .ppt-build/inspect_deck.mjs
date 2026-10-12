import fs from "node:fs/promises";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const source = "D:/my desktop/study/nlp/InternWorth.pptx";
const presentation = await PresentationFile.importPptx(await FileBlob.load(source));
const snapshot = await presentation.inspect({
  kind: "slide,textbox,shape,image,table,chart,notes,layout",
  maxChars: 60000,
});
await fs.writeFile("D:/my desktop/study/nlp/internworth_mvp/InternWorth/.ppt-build/inspection.ndjson", snapshot.ndjson);
console.log(snapshot.ndjson);
