import test from 'node:test';
import assert from 'node:assert/strict';
import { compare, cohort, summarize, numeric, validInterval, ageGroup, escapeHtml, reliableUnits, containsPoint, unitInterval, unitTotals } from '../model.js';

test('missing, absent, zero and unchanged values have distinct meanings', () => {
  assert.equal(compare([1, 0, null, 'a'], [1, 0, 2, 'a'], 'value'), 'same');
  assert.equal(compare([1, 0, null, 'a'], [1, 0, 2, 'a'], 'units'), 'unknown');
  assert.equal(compare([-1, null, null, null], [1, 5, 1, 'b']), 'unknown');
  assert.equal(compare(undefined, [1, 5, 1, 'b']), 'later-only');
  assert.equal(compare([1, 5, 1, 'b'], undefined), 'earlier-only');
  assert.equal(compare(undefined, undefined), 'absent');
  assert.equal(numeric(' '), null);
  assert.equal(numeric(null), null);
  assert.equal(numeric('0'), 0);
});

test('each lens compares only its own attribute', () => {
  const a = [1, 100, 2, 'owner-a'], b = [1, 200, 1, 'owner-b'];
  assert.equal(compare(a, b, 'use'), 'same');
  assert.equal(compare(a, b, 'value'), 'increase');
  assert.equal(compare(a, b, 'units'), 'decrease');
  assert.equal(compare(a, b, 'owner'), 'changed');
});

test('cohort filters preserve fixed geography and exclude IDs absent at both dates', () => {
  const rows = [['a','A',0,0,0,'block-a','100 MAIN'], ['b','B',1,0,0,'block-b','100 MAIN'], ['c','C',0,0,0,'block-a','200 MAIN']];
  const before = new Map([[0, [1, 1, 1, 'a']]]);
  const after = new Map([[0, [2, 2, 2, 'a']], [1, [-1, null, null, null]]]);
  assert.equal(cohort(rows, before, after).length, 2);
  assert.equal(cohort(rows, before, after, { hood: '0' }).length, 1);
  assert.equal(cohort(rows, before, after, { group: '100 MAIN', groupType: 'street' }).length, 2);
  const summary = summarize(cohort(rows, before, after), 'use');
  assert.equal(summary.changed, 1);
  assert.equal(summary.comparable, 1);
  assert.equal(summary['later-only'], 1);
});

test('unknown ages, invalid intervals, and unsafe markup are handled', () => {
  assert.equal(ageGroup(0), 'Unknown');
  assert.equal(ageGroup('1920'), '1900–1939');
  assert.equal(validInterval(4, 4), false);
  assert.equal(validInterval(5, 4), false);
  assert.equal(validInterval(0, 12), true);
  assert.equal(escapeHtml('<img onerror="x">'), '&lt;img onerror=&quot;x&quot;&gt;');
});

test('residential zeros are unknown, but zero units on a park are meaningful', () => {
  assert.equal(reliableUnits('Apartment', '0', true), null);
  assert.equal(reliableUnits('Single Family', 0, true), null);
  assert.equal(reliableUnits('Parks', 0, true), 0);
  assert.equal(reliableUnits('Apartment', 112, true), 112);
});

test('map hit testing selects polygon interiors while respecting holes', () => {
  const shape = [[[0,0],[20,0],[20,20],[0,20],[0,0]], [[5,5],[15,5],[15,15],[5,15],[5,5]]];
  assert.equal(containsPoint(shape, 2, 2), true);
  assert.equal(containsPoint(shape, 10, 10), false);
  assert.equal(containsPoint(shape, 30, 30), false);
});

test('owner naming variants and reviewed matches never silently become transfers', () => {
  const a = [1, 1, 1, 'literal-a', 'tokens-a', 'core-a', null];
  assert.equal(compare(a, [1,1,1,'literal-b','tokens-a','core-a',null], 'owner'), 'name-format');
  assert.equal(compare(a, [1,1,1,'literal-b','tokens-b','core-a',null], 'owner'), 'possible-name');
  assert.equal(compare(a, [1,1,1,'literal-b','tokens-b','core-b',null], 'owner'), 'changed');
  assert.equal(compare([...a.slice(0,6),'confirmed'], [1,1,1,'literal-b','tokens-b','core-b','confirmed'], 'owner'), 'same');
  assert.equal(compare(a, [1,1,1,null,null,null,null], 'owner'), 'unknown');
  const summary = summarize([{a,b:[1,1,1,'b','tokens-a','core-a',null]}, {a,b:[1,1,1,'b','b','core-a',null]}], 'owner');
  assert.equal(summary.changed, 0);
  assert.equal(summary.same, 0);
  assert.equal(summary['name-format'], 1);
  assert.equal(summary['possible-name'], 1);
  assert.equal(summary.comparable, 2);
});

test('unusable unit dates select the coherent 2024-onward series, preserving valid choices', () => {
  const snapshots = [{id:'2017-08',unitsComparable:false}, {id:'2020-q1',unitsComparable:true}, {id:'2024-q1',unitsComparable:true}, {id:'2024-08',unitsComparable:false}, {id:'2026-10',unitsComparable:true}];
  assert.deepEqual(unitInterval(snapshots, 0, 4), {from:2,to:4,adjusted:true});
  assert.deepEqual(unitInterval(snapshots, 2, 3), {from:2,to:4,adjusted:true});
  assert.deepEqual(unitInterval(snapshots, 1, 4), {from:1,to:4,adjusted:false});
});

test('unit totals use only comparable pairs and preserve increases and decreases', () => {
  const totals = unitTotals([{a:[1,0,1],b:[1,0,3]}, {a:[1,0,5],b:[1,0,4]}, {a:[1,0,null],b:[1,0,50]}, {a:undefined,b:[1,0,100]}]);
  assert.deepEqual(totals, {before:6,after:7,increase:1,decrease:1});
});
