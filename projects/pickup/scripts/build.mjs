import { mkdir, copyFile } from 'node:fs/promises';
await mkdir('dist/for-ai',{recursive:true});
for (const file of ['index.html','style.css','app.mjs','lib.mjs','sources.json','openapi.json','llms.txt','for-ai.json','upstream-openapi.json','ai.mjs','for-ai/index.html']) await copyFile(file,`dist/${file}`);
console.log('Built dependency-free static app in dist/. Node API runs separately with npm start.');
