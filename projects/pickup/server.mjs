import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';
import { searchAddresses, lookupPoint, calendar, LookupError } from './lib.mjs';

const files = new Map([
  ['/', ['index.html','text/html']], ['/index.html',['index.html','text/html']],
  ['/app.mjs',['app.mjs','text/javascript']], ['/lib.mjs',['lib.mjs','text/javascript']],
  ['/style.css',['style.css','text/css']], ['/sources.json',['sources.json','application/json']],
  ['/llms.txt',['llms.txt','text/plain']], ['/api/openapi.json',['openapi.json','application/json']],
  ['/openapi.json',['openapi.json','application/json']]
]);
const root = new URL('./', import.meta.url);

export function createApp() {
  return createServer(async (req, res) => {
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('Referrer-Policy', 'no-referrer');
    const send = (status, value, type = 'application/json') => {
      res.writeHead(status, { 'Content-Type': `${type}; charset=utf-8`, 'Cache-Control': 'no-store' });
      res.end(type === 'application/json' && typeof value !== 'string' ? JSON.stringify(value) : value);
    };
    try {
      if (req.method !== 'GET') { res.setHeader('Allow','GET'); return send(405,{error:'Use GET.'}); }
      const url = new URL(req.url, 'http://localhost');
      if (url.pathname === '/api/health') return send(200, {status:'ok', service:'datacuse-pickup'});
      if (url.pathname === '/api/search') return send(200, {candidates: await searchAddresses(url.searchParams.get('q'))});
      if (['/api/lookup','/api/calendar.ics'].includes(url.pathname)) {
        const result = await lookupPoint(url.searchParams.get('lat'), url.searchParams.get('lon'));
        if (url.pathname === '/api/lookup') return send(200, result);
        if (result.status !== 'matched') return send(422,{error:'A single collection zone is required.'});
        if (!result.zones[0].trash.upcoming.length && !result.zones[0].recycling.upcoming.length) return send(422,{error:'No upcoming published dates.'});
        res.setHeader('Content-Disposition','attachment; filename="syracuse-pickup.ics"');
        return send(200,calendar(result.zones[0]),'text/calendar');
      }
      const entry = files.get(url.pathname);
      if (!entry) return send(404,{error:'Not found.'});
      return send(200,await readFile(new URL(entry[0], root),'utf8'),entry[1]);
    } catch (error) { send(error instanceof LookupError ? error.status : 500, {error: error instanceof LookupError ? error.message : 'Unable to complete this request.'}); }
  });
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const port = Number(process.env.PORT || 8767);
  const host = process.env.HOST || '127.0.0.1';
  createApp().listen(port, host, () => console.log(`Syracuse Pickup: http://${host}:${port}/`));
}
