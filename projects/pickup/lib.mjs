export const LAYER = 'https://services6.arcgis.com/bdPqSfflsdgFRVVM/arcgis/rest/services/Recycling_Biweekly_and_Day/FeatureServer/22';
export const GEOCODER = 'https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer';
export const CITY_PAGE = 'https://www.syr.gov/Living/My-Home/Trash-and-Recycling/Recycling';
export const MAP = 'https://syr.maps.arcgis.com/apps/instant/lookup/index.html?appid=73be90dd8f2f47b1b85a1b2e01db72a7';

export class LookupError extends Error {
  constructor(message, status = 502) { super(message); this.status = status; }
}

export function localDay(date = new Date()) {
  const p = Object.fromEntries(new Intl.DateTimeFormat('en-US', {
    timeZone: 'America/New_York', year: 'numeric', month: '2-digit', day: '2-digit'
  }).formatToParts(date).map(part => [part.type, part.value]));
  return `${p.year}-${p.month}-${p.day}`;
}

export function parseDates(value) {
  const dates = [], rejected = [];
  for (const raw of String(value ?? '').split(',')) {
    const token = raw.trim();
    if (!token) continue;
    const valid = /^\d{4}-\d{2}-\d{2}$/.test(token) && Number.isFinite(Date.parse(`${token}T12:00:00Z`))
      && new Date(`${token}T12:00:00Z`).toISOString().slice(0, 10) === token;
    (valid ? dates : rejected).push(token);
  }
  return { dates: [...new Set(dates)].sort(), rejected };
}

export function normalizeZone(attributes, today = localDay()) {
  const day = attributes.Sanitation?.trim();
  const week = attributes.RecyclingW?.trim();
  if (!['Monday','Tuesday','Wednesday','Thursday','Friday'].includes(day) || !['A','B'].includes(week)) {
    throw new LookupError('The city returned an unrecognized collection zone. Please check the official map.');
  }
  const schedule = value => {
    const { dates, rejected } = parseDates(value);
    const upcoming = dates.filter(date => date >= today);
    return { next: upcoming[0] ?? null, upcoming, publishedThrough: dates.at(-1) ?? null,
      status: rejected.length ? 'invalid-source-dates' : upcoming.length ? 'available' : dates.length ? 'exhausted' : 'missing' };
  };
  return { id: attributes.FID, day, week, trash: schedule(attributes.TrSchedule), recycling: schedule(attributes.Schedule) };
}

async function arcgis(url, params, fetcher = fetch) {
  let response;
  try { response = await fetcher(`${url}?${new URLSearchParams({ f: 'json', ...params })}`, { signal: AbortSignal.timeout(12000) }); }
  catch { throw new LookupError('The city data service could not be reached. Please try again or open the official map.'); }
  if (!response.ok) throw new LookupError('The city data service is temporarily unavailable. Please try again.');
  let data;
  try { data = await response.json(); } catch { throw new LookupError('The city data service returned an unreadable response.'); }
  if (data.error) throw new LookupError('The city data service could not complete this lookup. Please try again.');
  return data;
}

export async function searchAddresses(query, fetcher = fetch) {
  query = String(query ?? '').trim();
  if (query.length < 5 || query.length > 200) throw new LookupError('Enter a street number and street name (5–200 characters).', 400);
  const data = await arcgis(`${GEOCODER}/findAddressCandidates`, {
    SingleLine: /syracuse/i.test(query) ? query : `${query}, Syracuse, NY`,
    outSR: '4326', outFields: 'Addr_type,City', maxLocations: '5', countryCode: 'USA',
    location: '-76.1474,43.0481', searchExtent: '-76.30,42.95,-76.02,43.16', forStorage: 'false'
  }, fetcher);
  if (!Array.isArray(data.candidates)) throw new LookupError('The address service returned an unexpected response.');
  return data.candidates.filter(c => c.score >= 80 && ['PointAddress','StreetAddress','Subaddress'].includes(c.attributes?.Addr_type)
    && /^Syracuse$/i.test(c.attributes?.City ?? '') && Number.isFinite(c.location?.x) && Number.isFinite(c.location?.y))
    .map(c => ({ address: c.address, score: c.score, lat: c.location.y, lon: c.location.x }));
}

export async function lookupPoint(lat, lon, fetcher = fetch, today = localDay()) {
  if (lat === null || lon === null || String(lat).trim() === '' || String(lon).trim() === '') throw new LookupError('Latitude and longitude are required.', 400);
  lat = Number(lat); lon = Number(lon);
  if (!Number.isFinite(lat) || !Number.isFinite(lon) || lat < -90 || lat > 90 || lon < -180 || lon > 180) {
    throw new LookupError('Enter valid latitude and longitude coordinates.', 400);
  }
  // Bound the query to the Syracuse area; never report a nearby polygon as a match.
  if (lat < 42.95 || lat > 43.16 || lon < -76.30 || lon > -76.02) return { status: 'outside-coverage', zones: [], asOf: today, source: LAYER };
  const data = await arcgis(`${LAYER}/query`, {
    geometry: `${lon},${lat}`, geometryType: 'esriGeometryPoint', inSR: '4326',
    spatialRel: 'esriSpatialRelIntersects', outFields: 'FID,Sanitation,RecyclingW,Schedule,TrSchedule', returnGeometry: 'false'
  }, fetcher);
  if (!Array.isArray(data.features) || data.exceededTransferLimit) throw new LookupError('The city returned an incomplete lookup. Please check the official map.');
  const zones = data.features.map(f => normalizeZone(f.attributes, today));
  return { status: zones.length === 1 ? 'matched' : zones.length ? 'ambiguous' : 'outside-coverage',
    zones, asOf: today, fetchedAt: new Date().toISOString(), source: LAYER };
}

export function calendar(zone, now = new Date()) {
  const lines = ['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//DataCuse//Syracuse Pickup//EN','CALSCALE:GREGORIAN','METHOD:PUBLISH',
    'X-WR-CALNAME:Syracuse pickup'];
  for (const kind of ['trash','recycling']) {
    for (const day of zone[kind].upcoming) {
      const next = new Date(`${day}T12:00:00Z`); next.setUTCDate(next.getUTCDate() + 1);
      lines.push('BEGIN:VEVENT', `UID:pickup-${zone.id}-${kind}-${day}@datacuse.com`,
        `DTSTAMP:${now.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}Z$/, 'Z')}`,
        `DTSTART;VALUE=DATE:${day.replaceAll('-', '')}`, `DTEND;VALUE=DATE:${next.toISOString().slice(0,10).replaceAll('-', '')}`,
        `SUMMARY:${kind === 'trash' ? 'Trash' : 'Recycling'} pickup`,
        'DESCRIPTION:City-published date. Check city notices for service changes.', `URL:${CITY_PAGE}`, 'END:VEVENT');
    }
  }
  return `${lines.concat('END:VCALENDAR').join('\r\n')}\r\n`;
}
