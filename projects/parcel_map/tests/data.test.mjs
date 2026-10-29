import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile, stat } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { gunzipSync } from 'node:zlib';
import { toPack, compare, summarize, cohort, clean } from '../model.js';

const base = new URL('../data/', import.meta.url);
const read = async path => JSON.parse(await readFile(new URL(path, base), 'utf8'));
const manifest = await read('manifest.json');
const rows = await read('index.json');
const packs = await Promise.all(manifest.snapshots.map(async s => toPack(await read(`snapshots/${s.id}.json`))));

test('all snapshots, IDs and exclusions remain aligned', () => {
  assert.equal(manifest.snapshots.length, 13);
  assert.equal(new Set(rows.map(r => r[0])).size, rows.length);
  assert.equal(rows.length, 43288);
  assert.equal(packs[12].size, 41218);
  for (const [si, pack] of packs.entries()) {
    assert.equal(pack.size, manifest.snapshots[si].unique);
    for (const [i, values] of pack) {
      assert.ok(rows[i]);
      assert.equal(typeof rows[i][0], 'string');
      assert.equal(values.length, 7);
      assert.ok(!manifest.duplicates[manifest.snapshots[si].id][rows[i][0]]);
      if (!manifest.snapshots[si].unitsComparable) assert.equal(values[2], null);
    }
  }
});

test('endpoint narrative counts reconcile with the explorer cohorts', () => {
  const both = [...packs[0].keys()].filter(i => packs[12].has(i));
  assert.equal(both.length, 39781);
  const count = (from, to) => both.filter(i => manifest.uses[packs[0].get(i)[0]] === from && manifest.uses[packs[12].get(i)[0]] === to).length;
  assert.equal(count('SINGLE FAMILY', 'VACANT LAND'), 222);
  assert.equal(count('TWO FAMILY', 'VACANT LAND'), 185);
  assert.equal(count('VACANT LAND', 'SINGLE FAMILY'), 35);
  assert.equal(count('VACANT LAND', 'APARTMENT'), 1);
  for (const [name, stored] of Object.entries(manifest.summary)) {
    const hood = String(manifest.neighborhoods.indexOf(name));
    const stats = summarize(cohort(rows, packs[0], packs[12], { hood }), 'use');
    assert.equal(stats.comparable, stored.comparable, `${name}: denominator`);
    assert.equal(stats.same, stored.same, `${name}: same`);
  }
});

test('attribute-poor August 2024 cannot produce land-use changes', () => {
  for (const [i, value] of packs[7]) {
    assert.equal(value[0], -1);
    if (packs[12].has(i)) assert.equal(compare(value, packs[12].get(i)), 'unknown');
  }
});

test('featured property timelines support the published story', async () => {
  const specs = [
    ['31150011700000010010050000', [[0, 'VACANT LAND'], [1, 'COMMERCIAL'], [4, 'APARTMENT']], 112],
    ['31150009800200010050030000', [[4, 'VACANT LAND'], [5, 'PARKS']], 0],
    ['31150004300000010030000000', [[2, 'VACANT LAND'], [3, 'SINGLE FAMILY']], 1],
  ];
  for (const [id, expected, units] of specs) {
    const history = (await read(`histories/${id.slice(6, 9)}.json`))[id];
    assert.equal(history.length, 13);
    for (const [si, use] of expected) assert.equal(clean(history[si][0]), use);
    assert.equal(Number(history[6][2]), units);
    const geometry = (await read(`geometry/${id.slice(6, 9)}.json`))[id];
    assert.ok(geometry.length && geometry[0].length >= 4);
  }
});

test('source archives are exact original bytes, verified against recorded SHA-256', async () => {
  for (const s of manifest.snapshots) {
    const compressed = await readFile(new URL(`sources/${s.id}.geojson.gz`, base));
    const digest = createHash('sha256').update(gunzipSync(compressed)).digest('hex');
    assert.equal(digest, s.sha256, s.file);
  }
});

test('every indexed history and geometry shard is deployable', async () => {
  const shards = [...new Set(rows.map(r => r[0].slice(6,9)))];
  for (const shard of shards) {
    assert.ok((await stat(new URL(`histories/${shard}.json`, base))).size > 0);
    assert.ok((await stat(new URL(`geometry/${shard}.json`, base))).size > 0);
  }
  const blocks = await read('blocks.json');
  assert.equal(Object.values(blocks).reduce((n, b) => n + b.total, 0), 41218);
});

test('1315 Cumberland retains its reviewed owner across every usable observation', async () => {
  const id = '31150005600000090100010000', index = rows.findIndex(r => r[0] === id);
  assert.ok(manifest.ownerAliases[id]);
  for (let i = 0; i < packs.length; i++) {
    assert.equal(compare(packs[i].get(index), packs[12].get(index), 'owner'), i === 7 ? 'unknown' : 'same');
  }
  const history = (await read('histories/056.json'))[id];
  assert.equal(clean(history[0][3]), 'MEDICIS LIVING TRUST');
  assert.equal(clean(history[12][3]), 'LIVING MEDICIS');
});

test('owner audit separates formatting and uncertainty from different names', () => {
  const summary = summarize(cohort(rows,packs[0],packs[12]), 'owner');
  assert.equal(summary['name-format'], 16047);
  assert.equal(summary['possible-name'], 125);
  assert.equal(summary.same, 4000);
  assert.equal(summary.changed, 19576);
  assert.equal(summary.comparable, summary.same + summary.changed + summary['name-format'] + summary['possible-name']);
});

test('usable default unit interval shows actual changes and unchanged records', () => {
  const summary = summarize(cohort(rows,packs[6],packs[12]), 'units');
  assert.equal(summary.changed, 296);
  assert.equal(summary.same, 40220);
  assert.equal(summary.unknown, 18);
});

test('persistent vacancy cohorts require all observations, not just endpoints', async () => {
  assert.equal(manifest.persistentVacancy.land.indices.length, 3257);
  assert.equal(manifest.persistentVacancy.building.indices.length, 291);
  const histories = new Map();
  for (const shard of new Set(rows.map(r => r[0].slice(6,9)))) histories.set(shard, await read(`histories/${shard}.json`));
  for (const kind of ['land','building']) {
    const group = manifest.persistentVacancy[kind];
    assert.deepEqual(group.snapshots, [0,1,2,3,4,5,6,8,9,10,11,12]);
    const expected = rows.map((row,i) => ({row,i})).filter(({row}) => {
      const history = histories.get(row[0].slice(6,9))[row[0]];
      return group.snapshots.every(s => history[s] && (kind === 'land' ? clean(history[s][0]) === 'VACANT LAND' : ['Y','YES','RESIDENTIAL','COMMERCIAL'].includes(clean(history[s][5]))));
    }).map(({i}) => i);
    assert.deepEqual(group.indices, expected);
  }
});
