import { mkdir, copyFile } from 'node:fs/promises';
await mkdir('dist',{recursive:true});
for (const file of ['index.html','style.css','app.mjs','lib.mjs','sources.json','openapi.json','llms.txt']) await copyFile(file,`dist/${file}`);
console.log('Built dependency-free static app in dist/. Node API runs separately with npm start.');
