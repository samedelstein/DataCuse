// Great-circle distance and initial bearing. No location leaves the browser.
const RAD = Math.PI / 180;
export const normalize = degrees => ((degrees % 360) + 360) % 360;
export function validPoint(point) {
  return Number.isFinite(point.lat) && Number.isFinite(point.lon) && Math.abs(point.lat) <= 90 && Math.abs(point.lon) <= 180;
}
export function distanceBearing(from, to) {
  if (!validPoint(from) || !validPoint(to)) throw new Error('Enter valid latitude and longitude.');
  const a = from.lat * RAD, b = to.lat * RAD, dlon = (to.lon - from.lon) * RAD;
  const h = Math.sin((b-a)/2)**2 + Math.cos(a)*Math.cos(b)*Math.sin(dlon/2)**2;
  const angle = 2*Math.atan2(Math.sqrt(Math.min(1,Math.max(0,h))),Math.sqrt(Math.max(0,1-h)));
  const bearing = angle < 1e-10 || Math.PI-angle < 1e-7 || Math.abs(from.lat)>89.999999 ? null : normalize(Math.atan2(Math.sin(dlon)*Math.cos(b),Math.cos(a)*Math.sin(b)-Math.sin(a)*Math.cos(b)*Math.cos(dlon))/RAD);
  return {distanceMetres:6371008.8*angle, bearing};
}
export function cardinal(bearing) {
  return ['north','northeast','east','southeast','south','southwest','west','northwest'][Math.round(normalize(bearing)/45)%8];
}
export function assessPosition(from, to, accuracy = 0) {
  const result = distanceBearing(from,to);
  const uncertainty = Number.isFinite(accuracy) && accuracy>=0 ? accuracy : Infinity;
  let state = 'ready';
  if (result.distanceMetres<=30 && uncertainty<=30) state='near';
  else if (result.distanceMetres<=Math.max(30,3*uncertainty)) state='uncertain';
  else if (result.bearing===null) state='ambiguous';
  return {...result,state,accuracy:uncertainty};
}
export function mercator(point) {
  const latitude=Math.max(-85.051129,Math.min(85.051129,point.lat));
  return [6378137*point.lon*RAD,6378137*Math.log(Math.tan(Math.PI/4+latitude*RAD/2))];
}
export function unmercator(x,y) {
  return {lon:x/6378137/RAD,lat:(2*Math.atan(Math.exp(y/6378137))-Math.PI/2)/RAD};
}
export function usableHeading(event, screenAngle=0) {
  // Restrict to a nearly flat handset; alpha alone is not a general tilted compass.
  if (!Number.isFinite(event.beta) || !Number.isFinite(event.gamma) || Math.abs(event.beta)>20 || Math.abs(event.gamma)>20) return null;
  if (Number.isFinite(event.webkitCompassHeading) && Number.isFinite(event.webkitCompassAccuracy) && event.webkitCompassAccuracy>=0 && event.webkitCompassAccuracy<=25) return normalize(event.webkitCompassHeading+screenAngle);
  if (event.absolute===true && Number.isFinite(event.alpha)) return normalize(360-event.alpha+screenAngle);
  return null;
}
