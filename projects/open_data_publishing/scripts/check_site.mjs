// Offline integration checks. This exercises page scripts and controls against
// a small DOM adapter; it does not replace a browser layout/accessibility check.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const read = (file) => fs.readFileSync(path.join(root, file), 'utf8');
const catalog = JSON.parse(read('data/catalog-analysis.json'));
const evidence = JSON.parse(read('data/evidence.json'));
assert.equal(catalog.datasets.length, 136);
assert.equal(new Set(catalog.datasets.map((r) => r.id)).size, 136);
assert.equal(catalog.summary.years.reduce((sum, row) => sum + row.created, 0), 136);
assert.equal(Object.values(catalog.summary.frequencies).reduce((a,b) => a+b, 0), 136);
assert.equal(Object.values(catalog.summary.freshness).reduce((a,b) => a+b, 0), 136);
assert.equal(evidence.directory.length, 350);
assert.equal(evidence.directory.filter((r) => !r.catalog_id).length, 218);
assert.equal(evidence.history.length, 75);
assert.equal(evidence.schemas.length, 136);
assert.deepEqual(evidence.comparisons.map((c) => [c.old_count,c.new_count]), [[16,9],[62,27],[27,69],[68,65],[57,65],[7,10]]);

function loadPage(file, search='', hash='') {
  const html = read(file);
  const elements = new Map();
  for (const match of html.matchAll(/<([a-z][a-z0-9-]*)\b[^>]*\bid="([^"]+)"[^>]*>/gi)) {
    const [, tag, id] = match;
    assert(!elements.has(id), `Duplicate ID ${id}`);
    const element = {
      tag, value:'', textContent:'', checked:false, disabled:false, events:{}, _html:'',
      addEventListener(name, callback) { this.events[name]=callback; },
      setAttribute(name, value) { this[name]=value; },
      removeAttribute(name) { delete this[name]; },
      set innerHTML(value) {
        this._html=value;
        if (this.tag === 'select') {
          const option=/<option(?:\s+value="([^"]*)")?[^>]*>([^<]*)/.exec(value);
          this.value=option ? option[1] ?? option[2] : '';
        }
      },
      get innerHTML() { return this._html; },
    };
    if (tag === 'select') element.innerHTML=html.slice(match.index + match[0].length).split('</select>')[0];
    elements.set(id,element);
  }
  const element = (id) => {assert(elements.has(id), `Missing DOM element ${id}`);return elements.get(id);};
  const events={};
  const context=vm.createContext({window:{location:{search,hash},addEventListener:(name,callback)=>{events[name]=callback;}}, document:{getElementById:element},URLSearchParams,console});
  for (const [,source] of html.matchAll(/<script[^>]*\bsrc="([^"]+)"[^>]*>/g)) vm.runInContext(read(source.split('?')[0]),context,{filename:source});
  return {element,context,fire:(id,event='input')=>element(id).events[event](),navigate:(hash)=>{context.window.location.hash=hash;events.hashchange();}};
}

const story=loadPage('index.html');
assert.equal((story.element('story-cohorts').innerHTML.match(/class="bar-column"/g)||[]).length,10);
assert(story.element('historical-cases').innerHTML.includes('Syracuse Lead Violations'));
const page=loadPage('dashboard.html');
assert.equal(page.element('history').hidden,false);
assert.equal(page.element('schema').hidden,true);
page.navigate('#services');
assert.equal(page.element('history').hidden,true);
assert.equal(page.element('services').hidden,false);
assert.equal(page.element('nav-services')['aria-current'],'location');
page.navigate('#history');
assert(page.element('result-count').textContent.startsWith('136 of 136'));
page.element('search').value='zz-no-matching-data';page.fire('search');
assert(page.element('dataset-rows').innerHTML.includes('No datasets'));
page.fire('reset','click');
page.element('frequency-filter').value='Daily';page.fire('frequency-filter');
assert(page.element('result-count').textContent.startsWith('5 of 136'));
page.fire('reset','click');
page.element('year-filter').value='2020';page.fire('year-filter');
assert(page.element('result-count').textContent.startsWith('0 of 136'));
page.element('chart-view').value='cumulative';page.fire('chart-view','change');
assert(page.element('same-period').disabled);
assert(page.element('chart-title').textContent.includes('not historical catalog totals'));
page.element('service-status').value='unmatched';page.fire('service-status');
assert(page.element('service-count').textContent.startsWith('218 of 350'));
page.element('service-search').value='2024_Fire';page.fire('service-search');
assert(page.element('service-count').textContent.startsWith('1 of 350'));
page.element('history-status').value='Permission denied';page.fire('history-status');
assert(page.element('history-count').textContent.startsWith('54 of 75'));
page.element('history-search').value='lead';page.fire('history-search');
assert(page.element('history-rows').innerHTML.includes('Syracuse Lead Violations'));
for (const comparison of evidence.comparisons) {
  page.element('comparison-select').value=comparison.key;page.fire('comparison-select','change');
  assert(page.element('schema-totals').innerHTML.includes(`<strong>${comparison.old_count}</strong>`));
  assert(page.element('schema-totals').innerHTML.includes(`<strong>${comparison.new_count}</strong>`));
}
const deepLink=loadPage('dashboard.html','?compare=parcel-dip');
assert(deepLink.element('comparison-note').innerHTML.includes('thinner Q3 2024'));
assert.equal(deepLink.element('schema').hidden,false);
const archiveLink=loadPage('dashboard.html','','#archive');
assert.equal(archiveLink.element('archive').hidden,false);
assert.equal(archiveLink.element('history').hidden,true);

let links=0;
for (const file of ['index.html','dashboard.html']) {
  const html=read(file);
  for (const [,href] of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
    const target=new URL(href,`https://local.test/projects/open_data_publishing/${file}`);
    if (target.origin !== 'https://local.test') continue;
    let local=path.resolve(root,'../..',decodeURIComponent(target.pathname.slice(1)));
    if (target.pathname.endsWith('/')) local=path.join(local,'index.html');
    assert(fs.existsSync(local),`${file}: missing ${href}`);
    if (target.hash && local.endsWith('.html')) assert(fs.readFileSync(local,'utf8').includes(`id="${target.hash.slice(1)}"`),`${file}: broken anchor ${href}`);
    links++;
  }
}
console.log(`PASS: inventory reconciliations, story rendering, dashboard controls, schema comparisons, deep links, and ${links} local links. Browser layout not covered.`);
