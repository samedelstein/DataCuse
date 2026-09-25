import test from 'node:test';
import assert from 'node:assert/strict';
import {distanceBearing,assessPosition,cardinal,mercator,unmercator,usableHeading} from '../content/5_geographic_center/analysis/compass-core.mjs';
const center={lat:43.04068526443205,lon:-76.14373201653156};
test('great-circle directions and a known equatorial arc',()=>{
  const east=distanceBearing({lat:0,lon:0},{lat:0,lon:1});
  assert.ok(Math.abs(east.distanceMetres-111195.08)<.1); assert.equal(east.bearing,90);
  assert.equal(distanceBearing({lat:0,lon:0},{lat:1,lon:0}).bearing,0);
  assert.equal(distanceBearing({lat:0,lon:0},{lat:-1,lon:0}).bearing,180);
  assert.equal(distanceBearing({lat:0,lon:0},{lat:0,lon:-1}).bearing,270);
});
test('dateline, coincident points, poles and antipodes',()=>{
  const across=distanceBearing({lat:0,lon:179},{lat:0,lon:-179});
  assert.ok(across.distanceMetres<223000); assert.equal(across.bearing,90);
  assert.equal(distanceBearing(center,center).bearing,null);
  assert.equal(distanceBearing({lat:0,lon:0},{lat:0,lon:180}).bearing,null);
  assert.equal(distanceBearing({lat:90,lon:0},center).bearing,null);
  assert.throws(()=>distanceBearing({lat:91,lon:0},center));
  assert.throws(()=>distanceBearing({lat:0,lon:NaN},center));
});
test('position uncertainty suppresses misleading bearings',()=>{
  assert.equal(assessPosition(center,center,5).state,'near');
  assert.equal(assessPosition(center,center,200).state,'uncertain');
  const nearby={lat:center.lat+.001,lon:center.lon};
  assert.equal(assessPosition(nearby,center,50).state,'uncertain');
  assert.equal(assessPosition(nearby,center,5).state,'ready');
  assert.equal(assessPosition(nearby,center,NaN).state,'uncertain');
  assert.equal(cardinal(359),'north');assert.equal(cardinal(225),'southwest');
});
test('map pin round trip preserves the selected location',()=>{
  for(const point of [center,{lat:43.1,lon:-76.2},{lat:-40,lon:140}]){
    const other=unmercator(...mercator(point));
    assert.ok(Math.abs(other.lat-point.lat)<1e-10);assert.ok(Math.abs(other.lon-point.lon)<1e-10);
  }
});
test('only usable north-referenced, flat-phone readings activate a compass',()=>{
  assert.equal(usableHeading({alpha:90,beta:0,gamma:0,absolute:false}),null);
  assert.equal(usableHeading({alpha:null,beta:0,gamma:0,absolute:true}),null);
  assert.equal(usableHeading({alpha:90,beta:60,gamma:0,absolute:true}),null);
  assert.equal(usableHeading({alpha:90,beta:0,gamma:0,absolute:true}),270);
  assert.equal(usableHeading({alpha:90,beta:0,gamma:0,absolute:true},90),0);
  assert.equal(usableHeading({webkitCompassHeading:42,webkitCompassAccuracy:10,beta:0,gamma:0}),42);
  assert.equal(usableHeading({webkitCompassHeading:42,webkitCompassAccuracy:-1,beta:0,gamma:0}),null);
});
