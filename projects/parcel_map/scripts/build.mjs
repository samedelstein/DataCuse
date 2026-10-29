import { mkdir, copyFile, cp, readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
const root = new URL('../', import.meta.url);
const manifest = JSON.parse(await readFile(new URL('data/manifest.json', root)));
if (manifest.snapshots.length !== 13 || manifest.version !== 2 || !manifest.persistentVacancy || !manifest.ownerAliases) throw new Error('Run npm run build:data first (the current interface requires manifest version 2).');
await mkdir(new URL('dist/', root), { recursive: true });
for (const file of ['index.html', 'styles.css', 'app.js', 'model.js']) {
  await copyFile(new URL(file, root), new URL(`dist/${file}`, root));
}
await cp(new URL('data/', root), new URL('dist/data/', root), { recursive: true });
console.log(`Static site built at ${fileURLToPath(new URL('dist/', root))}`);
