import test from 'node:test';
import assert from 'node:assert/strict';
import { once } from 'node:events';
import { localDay, parseDates, normalizeZone, lookupPoint, searchAddresses, calendar } from '../lib.mjs';
import { createApp } from '../server.mjs';

// City Friday / A schedule sampled from layer 22 on 2026-11-10, including holiday shifts.
const attributes = {FID:1,Sanitation:'Friday',RecyclingW:'A',
  Schedule:'2026-11-13,2026-11-28,2026-12-11,2026-12-26\r\n',
  TrSchedule:'2026-11-13,2026-11-20,2026-11-28,2026-12-04,2026-12-11,2026-12-18,2026-12-26,2027-01-02'};
const json = value => async () => ({ok:true,json:async () => value});

test('Eastern day does not roll over at UTC midnight; handles DST seasons',() => {
  assert.equal(localDay(new Date('2026-11-11T02:00:00Z')),'2026-11-10');
  assert.equal(localDay(new Date('2026-07-11T03:00:00Z')),'2026-07-10');
});
test('schedule preserves holiday shifts, trims CRLF, and includes today',() => {
  const zone = normalizeZone(attributes,'2026-11-20');
  assert.equal(zone.trash.next,'2026-11-20');
  assert.equal(zone.recycling.next,'2026-11-28');
  assert.ok(!zone.recycling.upcoming.includes('2026-11-27'));
});
test('expired dates never turn into an invented recurring schedule',() => {
  const zone = normalizeZone(attributes,'2027-01-03');
  assert.equal(zone.recycling.next,null);
  assert.equal(zone.trash.status,'exhausted');
  assert.deepEqual(zone.trash.upcoming,[]);
});
test('malformed and impossible dates are flagged, duplicate dates removed',() => {
  assert.deepEqual(parseDates('2026-02-30,2026-11-28,2026-11-28,wat'),{dates:['2026-11-28'],rejected:['2026-02-30','wat']});
  assert.equal(normalizeZone({...attributes,Schedule:null}).recycling.status,'missing');
  assert.equal(normalizeZone({...attributes,Schedule:'wat'}).recycling.status,'invalid-source-dates');
});
test('point lookup queries the authoritative layer with exact spatial intersection',async () => {
  const response = await lookupPoint(43.05,-76.15,async url => {
    const parsed = new URL(url);
    assert.ok(parsed.pathname.endsWith('/22/query'));
    assert.equal(parsed.searchParams.get('geometry'),'-76.15,43.05');
    assert.equal(parsed.searchParams.get('spatialRel'),'esriSpatialRelIntersects');
    return {ok:true,json:async()=>({features:[{attributes}]})};
  },'2026-11-10');
  assert.equal(response.status,'matched');
  assert.equal(response.zones[0].day,'Friday');
});
test('no zones, overlapping zones, and incomplete results remain distinct',async () => {
  assert.equal((await lookupPoint(43.05,-76.15,json({features:[]}))).status,'outside-coverage');
  assert.equal((await lookupPoint(43.05,-76.15,json({features:[{attributes},{attributes:{...attributes,FID:2}}]}))).status,'ambiguous');
  await assert.rejects(lookupPoint(43.05,-76.15,json({features:[{attributes}],exceededTransferLimit:true})),/incomplete/);
});
test('bad coordinates fail before requesting data',async () => {
  for (const coords of [[null,null],['',''],['no',-76],[91,-76]]) await assert.rejects(lookupPoint(...coords),e => e.status === 400);
  assert.equal((await lookupPoint(40,-74,()=>{throw Error('must not fetch');})).status,'outside-coverage');
});
test('upstream error bodies and transport failures produce actionable errors',async () => {
  await assert.rejects(lookupPoint(43.05,-76.15,json({error:{code:500}})),/could not complete/);
  await assert.rejects(lookupPoint(43.05,-76.15,async()=>{throw Error('network');}),/could not be reached/);
});
test('search excludes weak matches, city centroids, and other municipalities',async () => {
  const candidate = {address:'233 E Washington St, Syracuse, NY',score:100,location:{x:-76.149,y:43.049},attributes:{Addr_type:'PointAddress',City:'Syracuse'}};
  const result = await searchAddresses('233 E Washington St',json({candidates:[candidate,{...candidate,score:79},{...candidate,attributes:{Addr_type:'Locality',City:'Syracuse'}},{...candidate,attributes:{Addr_type:'PointAddress',City:'DeWitt'}}]}));
  assert.equal(result.length,1);
  assert.equal(result[0].lat,43.049);
});
test('calendar contains explicit dates, stable IDs, exclusive end dates, no recurrence or address',() => {
  const output = calendar(normalizeZone(attributes,'2026-12-26'),new Date('2026-11-10T12:00:00Z'));
  assert.match(output,/DTSTART;VALUE=DATE:20270102\r\nDTEND;VALUE=DATE:20270103/);
  assert.match(output,/UID:pickup-1-recycling-2026-12-26@datacuse.com/);
  assert.equal((output.match(/BEGIN:VEVENT/g)||[]).length,3);
  assert.ok(!output.includes('RRULE'));
  assert.ok(!output.includes('LOCATION:'));
});
test('HTTP routes validate parameters and do not expose arbitrary local files',async t => {
  const server = createApp().listen(0,'127.0.0.1');
  await once(server,'listening');
  t.after(()=>server.close());
  const origin = `http://127.0.0.1:${server.address().port}`;
  assert.equal((await fetch(`${origin}/api/health`)).status,200);
  assert.equal((await fetch(`${origin}/api/lookup`)).status,400);
  assert.equal((await fetch(`${origin}/api/search?q=x`)).status,400);
  assert.equal((await fetch(`${origin}/server.mjs`)).status,404);
  assert.equal((await fetch(`${origin}/sources.json`,{method:'POST'})).status,405);
  assert.equal((await fetch(`${origin}/`)).status,200);
  for (const path of ['/for-ai/','/for-ai.json','/upstream-openapi.json','/llms.txt','/ai.mjs']) {
    assert.equal((await fetch(`${origin}${path}`)).status,200,path);
  }
  const manifest = await (await fetch(`${origin}/for-ai.json`)).json();
  assert.equal(manifest.hosted_convenience_api,null);
  assert.ok(manifest.operations.lookup_point.url.endsWith('/FeatureServer/22/query'));
});
