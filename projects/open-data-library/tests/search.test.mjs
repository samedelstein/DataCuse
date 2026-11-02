import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {filterRows,matches} from '../app.js';
const rows=JSON.parse(fs.readFileSync(new URL('../data/search-index.json',import.meta.url),'utf8'));
test('search fields and common language',()=>{
  assert(filterRows(rows,{q:'city spending',scope:'curated'}).length>0);
  assert(filterRows(rows,{q:'turbidity',scope:'curated'}).some(r=>r.id==='water-2025-monthly-turbidity'));
  assert(filterRows(rows,{q:'source_cell',scope:'curated'}).every(r=>r.id.startsWith('budget-')));
});
test('year, subject and format intersect',()=>{
  const result=filterRows(rows,{q:'',scope:'all',year:'2025',topic:'Water & environment',format:'CSV'});
  assert.equal(result.length,3);
  assert.equal(filterRows(rows,{q:'nothingmatchesxyz',scope:'all'}).length,0);
});
test('official and unavailable records leave selected collection',()=>{
  const source=rows[0];
  const variants=[{...source,id:'official',membership:'official-catalog'},{...source,id:'offline',availability:'unavailable'},{...source,id:'good'}];
  assert.deepEqual(filterRows(variants,{scope:'curated'}).map(r=>r.id),['good']);
  assert.equal(filterRows(variants,{scope:'all',availability:'unavailable'}).length,1);
});
