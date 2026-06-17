import { createExtractorFromData } from 'node-unrar-js';
import fs from 'fs';
import path from 'path';

async function extractRar(buf, outDir) {
  const extractor = await createExtractorFromData({ data: buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength) });
  const { files } = extractor.extract();
  let n = 0;
  for (const f of files) {
    if (f.fileHeader.flags.directory) continue;
    const out = path.join(outDir, f.fileHeader.name);
    fs.mkdirSync(path.dirname(out), { recursive: true });
    if (f.extraction) { fs.writeFileSync(out, Buffer.from(f.extraction)); n++; }
  }
  return n;
}

async function main() {
  const src = process.argv[2], outDir = process.argv[3];
  fs.mkdirSync(outDir, { recursive: true });
  const n = await extractRar(fs.readFileSync(src), outDir);
  console.log('extracted', n, 'files to', outDir);
  // recurse into any nested .rar
  const walk = (d) => fs.readdirSync(d, { withFileTypes: true }).flatMap(e => {
    const p = path.join(d, e.name);
    return e.isDirectory() ? walk(p) : [p];
  });
  for (const p of walk(outDir)) {
    if (p.toLowerCase().endsWith('.rar')) {
      const sub = p.replace(/\.rar$/i, '_x');
      try { const m = await extractRar(fs.readFileSync(p), sub); console.log('  nested', path.basename(p), '->', m, 'files'); }
      catch (e) { console.log('  nested FAIL', path.basename(p), e.message); }
    }
  }
}
main().catch(e => { console.error(e); process.exit(1); });
