// Exercise the actual public builder in a temporary root; leave public output alone.
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
import {buildStories} from '../../../scripts/story-lib.mjs';
const root=fileURLToPath(new URL('../../../',import.meta.url));
const temp=await fs.mkdtemp(path.join(os.tmpdir(),'datacuse-dc008-build-'));
await fs.copyFile(path.join(root,'index.html'),path.join(temp,'index.html'));
await fs.cp(path.join(root,'content'),path.join(temp,'content'),{recursive:true,filter:source=>{
  const rel=path.relative(path.join(root,'content'),source);
  if(!rel)return true;
  const parts=rel.split(path.sep);
  if(parts[0]==='existing-stories.json'||parts[0]==='stories')return true;
  if(!/^\d+_/.test(parts[0]))return false;
  return parts.length===1||parts[1]==='story'||parts[1]==='images';
}});
const result=await buildStories(temp);
const manifest=JSON.parse(await fs.readFile(path.join(temp,'stories/.generated.json'),'utf8'));
assert(!manifest.some(p=>p.includes('syracuse-most-streets-intersection')));
const source=await fs.readFile(path.join(root,'content/7_most_streets_intersection/story/index.md'),'utf8');
assert.match(source,/status: draft/);
const audit={...result,draftExcluded:true,sourceUnchanged:true,buildRoot:temp,checkedUtc:new Date().toISOString()};
await fs.writeFile(new URL('./site-validation.json',import.meta.url),JSON.stringify(audit,null,2)+'\n');
console.log(JSON.stringify(audit,null,2));
