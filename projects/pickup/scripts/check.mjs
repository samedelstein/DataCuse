import { execFileSync } from 'node:child_process';
import { readFile } from 'node:fs/promises';
for (const file of ['app.mjs','lib.mjs','server.mjs','scripts/check.mjs','scripts/build.mjs','tests/lookup.test.mjs']) {
  execFileSync(process.execPath,['--check',file],{stdio:'inherit'});
}
for (const file of ['sources.json','openapi.json','package.json']) JSON.parse(await readFile(file,'utf8'));
const html = await readFile('index.html','utf8');
const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map(m => m[1]);
if (new Set(ids).size !== ids.length) throw new Error('Duplicate HTML IDs');
const app = await readFile('app.mjs','utf8');
for (const match of app.matchAll(/\$\('([^']+)'\)/g)) if (!ids.includes(match[1])) throw new Error(`Missing element ${match[1]}`);
console.log('Syntax, JSON, and DOM references passed.');
