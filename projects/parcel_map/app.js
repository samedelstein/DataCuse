import { clean, title, fmt, money, percent, escapeHtml as esc, toPack, compare, ageGroup, numeric, reliableUnits, containsPoint, validInterval, cohort, summarize, unitInterval, unitTotals, statusLabel } from './model.js';

const $ = selector => document.querySelector(selector);
const COLORS = { same: '#6e8875', changed: '#bd633d', increase: '#b66538', decrease: '#497e9c', unknown: '#a8ac9f', 'earlier-only': '#957b9c', 'later-only': '#c49c4d', 'name-format': '#688eaa', 'possible-name': '#a989b1' };
const cache = new Map();
const state = { from: 0, to: 12, lens: 'use', hood: '', vacancy: '', group: '', groupType: 'block', filter: null, selected: null, page: 0, generation: 0 };
let manifest, rows, before, after, items = [], map, selectionVersion = 0;
const geometry = new Map();

async function get(path) {
  if (!cache.has(path)) {
    const promise = fetch(`data/${path}`).then(response => {
      if (!response.ok) throw new Error(`Could not load ${path} (${response.status}).`);
      return response.json();
    }).catch(error => { cache.delete(path); throw error; });
    cache.set(path, promise);
  }
  return cache.get(path);
}

async function pack(index) {
  return toPack(await get(`snapshots/${manifest.snapshots[index].id}.json`));
}

function showError(error, target = '#load-error') {
  const element = $(target);
  element.hidden = false;
  element.textContent = `${error.message} Reload the page to try again.`;
  console.error(error);
}

function bars(values, total, colors = false) {
  return values.map(([label, count], i) => `<div class="bar-row"><span>${esc(title(label))}</span><div class="bar-track"><div class="bar-fill" style="width:${total ? count / total * 100 : 0}%;${colors ? `background:${['#76917d', '#b7835b', '#99a88d', '#c4bf9c', '#aeb5a5'][i % 5]}` : ''}"></div></div><span class="bar-value">${percent(count, total)}</span></div>`).join('');
}

function vacancyStatus(value) {
  const flag = clean(value);
  if (['Y', 'YES', 'RESIDENTIAL', 'COMMERCIAL'].includes(flag)) return 'Vacant-building flag: yes';
  if (flag === 'N') return 'Vacant-building flag: no (occupancy not verified)';
  return 'Vacant-building flag: unknown / not provided';
}

function fillStory() {
  const latest = manifest.snapshots.at(-1);
  $('#headline-stats').innerHTML = [[fmt(latest.unique), 'Parcels in the latest snapshot'], ['13', 'Snapshots across nine years'], [fmt(manifest.endpoint.matched), 'Tax IDs shared by 2017 & 2026'], ['3', 'Property stories to start with']].map(([n, label]) => `<div class="fact"><strong>${n}</strong><span>${label}</span></div>`).join('');
  const eastwood = manifest.summary.EASTWOOD;
  $('#eastwood-rate').textContent = percent(eastwood.same, eastwood.comparable);
  $('#eastwood-detail').textContent = `${fmt(eastwood.same)} of ${fmt(eastwood.comparable)} comparable parcels retain the same broad land-use label between 2017 and 2026.`;
  $('#continuity-waffle').innerHTML = Array.from({ length: 100 }, (_, i) => `<span${i >= Math.round(100 * eastwood.same / eastwood.comparable) ? ' class="different"' : ''}></span>`).join('');
  const ages = Object.values(manifest.summary).reduce((acc, h) => acc.map((v, i) => v + h.ages[i]), [0, 0, 0, 0, 0]);
  const total = ages.reduce((a, b) => a + b, 0);
  $('#age-intro').textContent = `${fmt(ages[0] + ages[1])} of ${fmt(total - ages[4])} parcels with a positive recorded construction year predate 1940.`;
  $('#age-chart').innerHTML = bars(['Before 1900', '1900–1939', '1940–1979', '1980 onward', 'Unknown'].map((l, i) => [l, ages[i]]), total, true);
  const destinations = manifest.transitions.filter(([a]) => a === 'VACANT LAND').sort((a, b) => b[2] - a[2]);
  const max = destinations[0][2];
  $('#vacancy-branches').innerHTML = destinations.map(([a, b, n]) => `<button class="branch" data-from-use="${esc(a)}" data-to-use="${esc(b)}"><span class="branch-label">${b === a ? 'Vacant at both endpoints' : esc(title(b))}</span><span class="bar-track"><span class="bar-fill" style="display:block;width:${Math.max(2, n / max * 100)}%"></span></span><strong>${fmt(n)}</strong></button>`).join('');
  $('#homes-to-vacant').textContent = fmt(manifest.transitions.filter(([a, b]) => ['SINGLE FAMILY', 'TWO FAMILY'].includes(a) && b === 'VACANT LAND').reduce((n, t) => n + t[2], 0));
  for (const kind of ['land', 'building']) {
    const group = manifest.persistentVacancy[kind];
    $(`#persistent-${kind}-count`).textContent = fmt(group.indices.length);
    $(`#persistent-${kind}-description`).textContent = kind === 'land'
      ? `Parcels recorded as vacant land in all ${group.snapshots.length} usable snapshots, from 2017 through 2026. This is stricter than being vacant at just the two endpoints.`
      : `Parcels with a positive vacant-building flag in all ${group.snapshots.length} usable snapshots. These are building-vacancy records, separate from the land-use category “vacant land.”`;
  }
  $('#source-table').innerHTML = `<table class="source-table"><thead><tr><th>Snapshot / original file</th><th>Rows</th><th>Land use</th><th>Unit comparisons</th><th>Duplicate IDs excluded</th></tr></thead><tbody>${manifest.snapshots.map(s => `<tr><td><a href="${s.download}" download>${esc(s.label)} · GeoJSON.gz ↗</a></td><td>${fmt(s.rows)}</td><td>${s.useComparable ? 'Available' : 'Missing'}</td><td>${s.unitsComparable ? 'Available' : 'Excluded / unavailable'}</td><td>${Object.keys(manifest.duplicates[s.id]).length}</td></tr>`).join('')}</tbody></table><p class="small">Source downloads are losslessly compressed original GeoJSON files (35–108 MB when expanded). <a href="data/manifest.json">Download the field mapping, source checksums, and summary data</a>. Broad use labels are compared as recorded; classification changes such as schools becoming community services may reflect recoding.</p>`;
}

function fillControls() {
  const hoods = manifest.neighborhoods.map((h, i) => `<option value="${i}">${esc(title(h))}</option>`).join('');
  $('#neighborhood').insertAdjacentHTML('beforeend', hoods);
  for (const name of ['compare-a', 'compare-b']) $(`#${name}`).innerHTML = hoods;
  $('#compare-a').value = manifest.neighborhoods.indexOf('EASTWOOD');
  $('#compare-b').value = manifest.neighborhoods.indexOf('NEAR WESTSIDE');
  for (const name of ['from-snapshot', 'to-snapshot']) {
    $(`#${name}`).innerHTML = manifest.snapshots.map((s, i) => `<option value="${i}">${esc(s.label)}</option>`).join('');
  }
  syncControls();
}

function syncControls() {
  if (state.lens !== 'units') $('#comparison-adjustment').hidden = true;
  $('#from-snapshot').value = state.from;
  $('#to-snapshot').value = state.to;
  $('#neighborhood').value = state.hood;
  $('#lens').value = state.lens;
  $('#vacancy-filter').value = state.vacancy;
  for (const [id, isFrom] of [['from-snapshot', true], ['to-snapshot', false]]) {
    for (const option of $(`#${id}`).options) {
      const index = +option.value, s = manifest.snapshots[index];
      const noUnits = state.lens === 'units' && !s.unitsComparable;
      option.disabled = noUnits || (isFrom ? index >= state.to : index <= state.from);
      option.textContent = `${s.label}${noUnits ? ' — unit counts unavailable' : ''}`;
    }
  }
}

async function update(fit = false) {
  const generation = ++state.generation;
  $('#map-progress').textContent = 'Reading comparison…';
  try {
    const loaded = await Promise.all([pack(state.from), pack(state.to)]);
    if (generation !== state.generation) return;
    [before, after] = loaded;
    items = cohort(rows, before, after, state);
    if (state.filter?.kind === 'transition') {
      const source = manifest.uses.indexOf(state.filter.source), destination = manifest.uses.indexOf(state.filter.destination);
      items = items.filter(({ a, b }) => a?.[0] === source && b?.[0] === destination);
    }
    if (state.vacancy) {
      const ids = new Set(manifest.persistentVacancy[state.vacancy].indices);
      items = items.filter(({ i }) => ids.has(i));
    }
    if (state.selected != null && !items.some(({ i }) => i === state.selected)) clearSelection();
    state.page = 0;
    renderSummary();
    renderSelectedComparison();
    renderList();
    map.setItems(items, fit);
    $('#map-progress').textContent = '';
  } catch (error) {
    if (generation === state.generation) showError(error, '#map-progress');
  }
}

function clearSelection() {
  selectionVersion++;
  state.selected = null;
  $('#address-search').value = '';
  const url = new URL(location.href);
  url.searchParams.delete('parcel');
  history.replaceState(null, '', url);
  $('#property-detail').innerHTML = '<p class="eyebrow">EVERY PARCEL HAS A TIMELINE</p><h3>Find a place<br>you know.</h3><p>Select a property in this view to follow its recorded history across the archive.</p>';
}

function renderSelectedComparison() {
  const target = $('#selected-comparison');
  if (!target || state.selected == null) return;
  const label = statusLabel(compare(before?.get(state.selected), after?.get(state.selected), state.lens), state.lens) || 'Unknown';
  target.textContent = `${$('#lens').selectedOptions[0].textContent} · ${manifest.snapshots[state.from].label} → ${manifest.snapshots[state.to].label}: ${label}`;
}

function renderSummary() {
  const s = summarize(items, state.lens);
  const name = state.group ? `${state.groupType === 'street' ? 'Address group' : 'Tax block'} ${state.group}` : state.hood === '' ? 'Across Syracuse' : title(manifest.neighborhoods[+state.hood]);
  const metrics = s.comparable
    ? `<div class="summary-stats"><div><strong>${fmt(s.changed)}</strong><span>${state.lens === 'owner' ? 'DIFFERENT NAME' : state.lens === 'units' ? 'PARCELS WITH CHANGED COUNTS' : 'CHANGED'}</span></div><div><strong>${fmt(s.same)}</strong><span>${state.lens === 'owner' ? 'SAME NAME / CONFIRMED MATCH' : state.lens === 'units' ? 'PARCELS WITH SAME COUNTS' : 'SAME'}</span></div></div>`
    : `<h3>${items.length ? 'No comparable data' : 'No matching parcels'}</h3><p>${items.length ? 'Missing or unusable values prevent this comparison. This does not mean nothing changed.' : 'Try a different neighborhood or clear the vacancy filter.'}</p>`;
  const ownerNote = state.lens === 'owner' ? `<div class="owner-audit"><p><i class="swatch" style="background:${COLORS['name-format']}"></i><strong>${fmt(s['name-format'])}</strong> reordered / reformatted names</p><p><i class="swatch" style="background:${COLORS['possible-name']}"></i><strong>${fmt(s['possible-name'])}</strong> possible name matches</p><p>These two groups are separate from “different name.” Even a different name is <strong>not a verified ownership transfer</strong>. This view covers all parcel types, not just homes.</p></div>` : '';
  const units = state.lens === 'units' && s.comparable ? unitTotals(items) : null;
  const unitNote = units ? `<div class="units-totals"><p><strong>${fmt(units.increase)}</strong> parcels increased · <strong>${fmt(units.decrease)}</strong> decreased</p><p>Recorded units on comparable parcels:<br><strong>${fmt(units.before)} → ${fmt(units.after)}</strong></p><p>${units.after - units.before >= 0 ? '+' : ''}${fmt(units.after - units.before)} net recorded units. Revisions can change counts; this is not a construction tally.</p></div>` : '';
  $('#comparison-summary').innerHTML = `<p class="eyebrow">${esc(name)}</p>${metrics}${ownerNote}${unitNote}<p class="summary-notes">${fmt(s.comparable)} comparable records · ${fmt(s.unknown)} with unknown comparison<br>${fmt(s['earlier-only'])} earlier-only · ${fmt(s['later-only'])} later-only</p>`;
  const interval = `${manifest.snapshots[state.from].label} → ${manifest.snapshots[state.to].label}`;
  const notes = {
    use: 'Broad recorded land-use labels; changes can reflect recoding as well as physical change.',
    value: 'Nominal assessed values, not sale prices or inflation-adjusted measures. An assessment change does not establish investment.',
    owner: 'Owner-name records, not verified sales. Matching name words with changed order or punctuation are separated from different names. Changes only to legal qualifiers (such as TRUST or LLC) are possible matches, not assumed identities. Reviewed matches are scoped to a specific parcel and listed in its timeline.',
    units: 'Only dates with usable unit fields can be selected. Missing values and zero-unit residential contradictions are unknown. Q1 2020 uses an older Units field; 2024 onward uses n_ResUnits. Changes can reflect revised records or field definitions, not new construction.'
  };
  $('#comparison-note').textContent = `${interval}. ${notes[state.lens]}${state.from <= 4 && state.to >= 5 ? ' No snapshots are available between Q1 2020 and November 2023.' : ''}`;
  const keys = ['same', ...(state.lens === 'value' || state.lens === 'units' ? ['increase', 'decrease'] : ['changed']), ...(state.lens === 'owner' ? ['name-format', 'possible-name'] : []), 'unknown', 'earlier-only', 'later-only'];
  $('#map-legend').innerHTML = keys.map(k => `<span><i class="swatch" style="background:${COLORS[k]}"></i>${statusLabel(k, state.lens)}</span>`).join('');
  const vacancyLabel = state.vacancy === 'building' ? 'Vacant-building flag in every usable snapshot' : 'Vacant land in every usable snapshot';
  $('#vacancy-scope').textContent = state.vacancy ? `${vacancyLabel}: ${fmt(manifest.persistentVacancy[state.vacancy].indices.length)} citywide. All ${manifest.persistentVacancy[state.vacancy].snapshots.length} usable snapshots are checked, regardless of the comparison dates. Neighborhood filters narrow this group.` : 'This filter checks the entire 2017–2026 archive, independently of the two comparison dates.';
  const chip = $('#filter-chip');
  chip.hidden = !state.filter && !state.group && !state.vacancy;
  if (!chip.hidden) {
    chip.innerHTML = `${esc([state.group ? name : '', state.filter?.label, state.vacancy ? vacancyLabel : ''].filter(Boolean).join(' · '))} <button id="clear-filter" aria-label="Clear group or story filter">×</button>`;
    $('#clear-filter').onclick = () => { state.filter = null; state.group = ''; state.vacancy = ''; syncControls(); update(true); };
  }
}

function renderList() {
  const pages = Math.max(1, Math.ceil(items.length / 25));
  state.page = Math.min(state.page, pages - 1);
  const view = items.slice(state.page * 25, (state.page + 1) * 25);
  $('#list-count').textContent = `(${fmt(items.length)})`;
  $('#parcel-list-body').innerHTML = `<table class="parcel-table"><thead><tr><th>Address</th><th>Neighborhood</th><th>Comparison</th></tr></thead><tbody>${view.map(({ row, i, a, b }) => `<tr><td><button class="text-button" data-index="${i}">${esc(title(row[1]))}</button></td><td>${esc(title(manifest.neighborhoods[row[2]]))}</td><td>${statusLabel(compare(a, b, state.lens), state.lens) || 'Unknown'}</td></tr>`).join('') || '<tr><td colspan="3">No parcels match these selections.</td></tr>'}</tbody></table>`;
  $('#page-label').textContent = `${state.page + 1} / ${pages}`;
  $('#previous-page').disabled = state.page === 0;
  $('#next-page').disabled = state.page >= pages - 1;
}

async function loadGeometry(key) {
  const values = await get(`geometry/${key.slice(6, 9)}.json`);
  for (const [id, shape] of Object.entries(values)) geometry.set(id, shape);
  return geometry.get(key) || [];
}

function outlineSvg(shape) {
  const points = shape.flat();
  if (!points.length) return '';
  const xs = points.map(p => p[0]), ys = points.map(p => p[1]);
  const x = Math.min(...xs), y = Math.min(...ys), w = Math.max(...xs) - x, h = Math.max(...ys) - y;
  const pad = Math.max(w, h) * .12;
  const path = shape.map(ring => ring.map(([px, py], i) => `${i ? 'L' : 'M'}${px},${py}`).join('') + 'Z').join('');
  return `<svg viewBox="${x-pad} ${y-pad} ${w+2*pad} ${h+2*pad}" aria-hidden="true"><path d="${path}" fill-rule="evenodd"/></svg>`;
}

async function selectParcel(index, focus = true) {
  const version = ++selectionVersion;
  const row = rows[index];
  if (!row) return;
  state.selected = index;
  $('#search-results').hidden = true;
  $('#address-search').value = title(row[1]);
  const detail = $('#property-detail');
  detail.innerHTML = '<p role="status">Loading the property timeline…</p>';
  if (focus) map.focus(row);
  const url = new URL(location.href);
  url.searchParams.set('parcel', row[0]);
  history.replaceState(null, '', url);
  try {
    const [histories] = await Promise.all([get(`histories/${row[0].slice(6, 9)}.json`), loadGeometry(row[0])]);
    if (version !== selectionVersion) return;
    const observations = histories[row[0]];
    const latestIndex = observations.findLastIndex(Boolean), latest = observations[latestIndex];
    const year = numeric(latest[4]);
    const age = ageGroup(latest[4]);
    const review = manifest.ownerAliases[row[0]];
    const reviewNote = review ? `<div class="owner-review"><p class="eyebrow">REVIEWED OWNER-NAME MATCH</p><p><strong>${esc(title(review.displayName))}</strong></p><p>${review.names.map(n => esc(n)).join(' / ')} are treated as the same owner for this parcel.</p><p class="small">${esc(review.basis)}</p></div>` : '';
    detail.innerHTML = `<p class="eyebrow">${esc(title(manifest.neighborhoods[row[2]]))}</p><h3 tabindex="-1" id="property-heading">${esc(title(row[1]))}</h3><p class="small">Tax ID ${esc(row[0])}<br>Latest observation: ${esc(manifest.snapshots[latestIndex].label)}</p><dl class="property-metrics"><div><dt>RECORDED USE</dt><dd>${esc(title(latest[0]) || 'Unknown')}</dd></div><div><dt>ASSESSED VALUE</dt><dd>${money(numeric(latest[1]))}</dd></div><div><dt>BUILDING YEAR</dt><dd>${year ? `${year} · ${age}` : 'Unknown'}</dd></div><div><dt>HOUSING UNITS</dt><dd>${reliableUnits(latest[0], latest[2], manifest.snapshots[latestIndex].unitsComparable) ?? 'Not comparable'}</dd></div></dl><p id="selected-comparison" class="small" aria-live="polite"></p><div class="group-buttons"><button id="show-tax-block">Explore tax block</button>${row[6] ? '<button id="show-street-group">Explore address group</button>' : ''}<button id="find-similar">Find a block like this</button></div><div id="similar-results"></div>${reviewNote}<p class="eyebrow">OBSERVATIONS, NOT EVENT DATES</p><ol class="history">${observations.map((observation, si) => {
      const s = manifest.snapshots[si];
      const gap = si === 5 ? '<li class="history-gap">Q1 2020 → Nov 2023<br>No snapshots available between these observations.</li>' : '';
      if (!observation) return `${gap}<li><span class="date">${esc(s.label)}</span>${manifest.duplicates[s.id][row[0]] ? 'Duplicate ID excluded' : 'Not found in this snapshot'}</li>`;
      const [use, value, units, owner] = observation;
      const comparableUnits = reliableUnits(use, units, s.unitsComparable);
      return `${gap}<li><span class="date">${esc(s.label)}</span><strong>${esc(title(use) || 'Use not provided')}</strong><span class="detail">${numeric(value) == null ? 'Assessment not recorded' : `${money(numeric(value))} assessed`}<br>${comparableUnits !== null ? `${fmt(comparableUnits)} recorded units` : 'Unit count not comparable'}<br>${esc(title(owner) || 'Owner not provided')}<br>${esc(vacancyStatus(observation[5]))}</span><details><summary>Original fields & source</summary><dl>${manifest.fields.map((field, fi) => `<dt>${esc(s.sourceFields[field] || `${field} (field absent)`)}</dt><dd>${observation[fi] == null ? 'null / absent' : esc(JSON.stringify(observation[fi]))}</dd>`).join('')}</dl><a href="${s.download}" download>${esc(s.label)} original GeoJSON.gz ↗</a></details></li>`;
    }).join('')}</ol>`;
    $('#show-tax-block').onclick = () => selectGroup(row[5], 'block');
    if ($('#show-street-group')) $('#show-street-group').onclick = () => selectGroup(row[6], 'street');
    $('#find-similar').onclick = () => similarBlocks(row);
    renderSelectedComparison();
    map.draw();
  } catch (error) {
    if (version === selectionVersion) { detail.innerHTML = ''; showError(error, '#property-detail'); }
  }
}

function selectGroup(group, groupType) {
  state.hood = ''; state.vacancy = ''; state.filter = null; state.group = group; state.groupType = groupType;
  syncControls(); update(true);
}

async function similarBlocks(row) {
  const result = $('#similar-results');
  result.textContent = 'Comparing tax-block land-use and age profiles…';
  try {
    const groups = await get('blocks.json');
    const target = groups[row[5]];
    if (!target || target.total < 5) { result.textContent = 'This tax block has fewer than five usable records, so a comparison would be too thin.'; return; }
    const useKeys = [...manifest.uses, 'UNKNOWN'];
    const candidates = Object.entries(groups).filter(([id, g]) => id !== row[5] && g.total >= 5).map(([id, g]) => ({ id, ...g, distance: (useKeys.reduce((n, u) => n + Math.abs((g.uses[u] || 0) / g.total - (target.uses[u] || 0) / target.total), 0) + g.ages.reduce((n, v, i) => n + Math.abs(v / g.total - target.ages[i] / target.total), 0)) / 4 })).sort((a, b) => a.distance - b.distance || a.id.localeCompare(b.id)).slice(0, 3);
    result.innerHTML = '<p class="small">Closest profiles among tax blocks with at least five records, weighting land-use shares and building-age shares equally, including unknowns. Tax blocks are not necessarily street blocks.</p>' + candidates.map(g => `<div class="similar-block"><button class="text-button" data-block="${esc(g.id)}">${esc(title(manifest.neighborhoods[g.hood]))} · ${esc(g.id)} ↗</button><p>${fmt(g.total)} parcels · ${Math.round((1 - g.distance) * 100)}% profile similarity</p></div>`).join('');
  } catch (error) { result.textContent = error.message; }
}

function neighborhoodCard(side) {
  const hood = +$(`#compare-${side}`).value;
  const name = manifest.neighborhoods[hood], summary = manifest.summary[name];
  const categories = ['SINGLE FAMILY', 'TWO FAMILY', 'APARTMENT', 'VACANT LAND'];
  const values = categories.map(k => [k, summary.uses[k] || 0]);
  values.push(['Other / unknown', summary.total - values.reduce((n, [, v]) => n + v, 0)]);
  $(`#neighborhood-${side}`).innerHTML = `<canvas class="mini-map" id="mini-${side}" aria-label="Parcel pattern in ${esc(title(name))}"></canvas><div class="summary-stats"><div><strong>${fmt(summary.total)}</strong><span>LATEST PARCELS</span></div><div><strong>${percent(summary.comparable - summary.same, summary.comparable)}</strong><span>CHANGED USE</span></div></div><p class="small">${fmt(summary.comparable)} comparable 2017–2026 records.</p><p class="subhead">LAND-USE MIX · OCTOBER 2026</p>${bars(values, summary.total)}<p class="subhead">RECORDED BUILDING AGE · OCTOBER 2026</p>${bars(['Before 1900', '1900–1939', '1940–1979', '1980 onward', 'Unknown'].map((l, i) => [l, summary.ages[i]]), summary.total, true)}<button class="text-button" data-neighborhood="${esc(name)}">Explore ${esc(title(name))} ↗</button>`;
  const canvas = $(`#mini-${side}`), ctx = canvas.getContext('2d');
  const width = canvas.clientWidth, height = 170, dpr = devicePixelRatio || 1;
  canvas.width = width * dpr; canvas.height = height * dpr; ctx.scale(dpr, dpr);
  const points = rows.filter(r => r[2] === hood && r[7] === 12);
  if (!points.length) return;
  const xs = points.map(r => r[3]), ys = points.map(r => r[4]);
  const xmin = Math.min(...xs), ymin = Math.min(...ys), xmax = Math.max(...xs), ymax = Math.max(...ys);
  const scale = Math.min((width-30) / (xmax-xmin || 1), (height-25) / (ymax-ymin || 1));
  ctx.fillStyle = '#507362';
  for (const r of points) ctx.fillRect((r[3]-(xmin+xmax)/2)*scale+width/2, (r[4]-(ymin+ymax)/2)*scale+height/2, 1.7, 1.7);
}

class ParcelMap {
  constructor(canvas) {
    this.canvas = canvas; this.ctx = canvas.getContext('2d'); this.scale = 1; this.center = [0, 0]; this.items = []; this.drag = null; this.drawPending = false; this.geometryRequests = new Set();
    new ResizeObserver(() => { this.width = canvas.clientWidth; this.height = canvas.clientHeight; this.draw(); }).observe(canvas);
    canvas.addEventListener('pointerdown', e => { this.drag = { x: e.clientX, y: e.clientY, startX: e.clientX, startY: e.clientY, moved: false }; canvas.setPointerCapture(e.pointerId); });
    canvas.addEventListener('pointermove', e => {
      if (this.drag) { const dx = e.clientX-this.drag.x, dy = e.clientY-this.drag.y; this.drag.moved ||= Math.hypot(e.clientX-this.drag.startX, e.clientY-this.drag.startY)>4; this.center[0] -= dx/this.scale; this.center[1] -= dy/this.scale; this.drag.x = e.clientX; this.drag.y = e.clientY; this.draw(); }
      else this.hover(e);
    });
    canvas.addEventListener('pointerup', e => { const dragged = this.drag?.moved; this.drag = null; if (!dragged) { const found = this.hit(e); if (found) selectParcel(found.i); } });
    canvas.addEventListener('pointercancel', () => { this.drag = null; });
    canvas.addEventListener('pointerleave', () => { $('#map-tooltip').hidden = true; });
    canvas.addEventListener('wheel', e => { if (!e.ctrlKey && !e.metaKey) return; e.preventDefault(); this.zoom(e.deltaY < 0 ? 1.25 : .8); }, { passive: false });
    canvas.addEventListener('keydown', e => { const d = 60 / this.scale; const moves = { ArrowLeft: [-d, 0], ArrowRight: [d, 0], ArrowUp: [0, -d], ArrowDown: [0, d] }; if (moves[e.key]) { e.preventDefault(); this.center = this.center.map((v, i) => v + moves[e.key][i]); this.draw(); } else if (['+', '=', '-'].includes(e.key)) { e.preventDefault(); this.zoom(e.key === '-' ? .7 : 1.4); } });
    $('#zoom-in').onclick = () => this.zoom(1.6); $('#zoom-out').onclick = () => this.zoom(1/1.6); $('#reset-map').onclick = () => this.fit();
  }
  setItems(next, fit) { this.items = next; if (fit || !this.fitted) this.fit(); else this.draw(); }
  fit() {
    if (!this.items.length) { this.draw(); return; }
    const xs = this.items.map(p => p.row[3]), ys = this.items.map(p => p.row[4]);
    const xmin = Math.min(...xs), xmax = Math.max(...xs), ymin = Math.min(...ys), ymax = Math.max(...ys);
    this.width = this.canvas.clientWidth; this.height = this.canvas.clientHeight;
    this.center = [(xmin+xmax)/2, (ymin+ymax)/2];
    this.scale = Math.min((this.width-90)/(xmax-xmin || 100), (this.height-100)/(ymax-ymin || 100), 4);
    this.fitted = true; this.draw();
  }
  focus(row) { this.center = [row[3], row[4]]; this.scale = Math.max(this.scale, 1.1); this.draw(); }
  zoom(factor) { this.scale = Math.max(.015, Math.min(15, this.scale * factor)); this.draw(); }
  project(x, y) { return [(x-this.center[0])*this.scale+this.width/2, (y-this.center[1])*this.scale+this.height/2]; }
  hit(e) {
    const rect = this.canvas.getBoundingClientRect(), x = e.clientX-rect.left, y = e.clientY-rect.top;
    if (this.scale > .25) {
      const wx = (x-this.width/2)/this.scale+this.center[0], wy = (y-this.height/2)/this.scale+this.center[1];
      for (const item of this.items) {
        const shape = geometry.get(item.row[0]);
        if (shape && containsPoint(shape, wx, wy)) return item;
      }
    }
    let best = null, distance = 15;
    for (const item of this.items) { const [px, py] = this.project(item.row[3], item.row[4]); const d = Math.hypot(x-px, y-py); if (d < distance) { distance = d; best = item; } }
    return best;
  }
  hover(e) {
    const found = this.hit(e), tip = $('#map-tooltip'); tip.hidden = !found;
    if (found) { const rect = this.canvas.getBoundingClientRect(); tip.textContent = `${title(found.row[1])} · ${statusLabel(compare(found.a, found.b, state.lens), state.lens)}`; tip.style.left = `${Math.max(5, Math.min(this.width-230, e.clientX-rect.left+12))}px`; tip.style.top = `${Math.max(5, e.clientY-rect.top-36)}px`; }
  }
  draw() {
    if (this.drawPending) return;
    this.drawPending = true;
    requestAnimationFrame(() => { this.drawPending = false; this.render(); });
  }
  render() {
    const { ctx, canvas, width: w, height: h } = this;
    if (!w || !h) return;
    const dpr = Math.min(2, devicePixelRatio || 1);
    if (canvas.width !== w*dpr || canvas.height !== h*dpr) { canvas.width = w*dpr; canvas.height = h*dpr; }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, w, h);
    ctx.strokeStyle = '#d5dccd'; ctx.lineWidth = 1;
    for (let x = 0; x < w; x += 50) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke(); }
    for (let y = 0; y < h; y += 50) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke(); }
    const visible = [];
    for (const item of this.items) {
      const [x, y] = this.project(item.row[3], item.row[4]);
      if (x < -100 || y < -100 || x > w+100 || y > h+100) continue;
      visible.push(item);
      const status = compare(item.a, item.b, state.lens);
      ctx.fillStyle = COLORS[status] || COLORS.unknown;
      const shape = this.scale > .25 && geometry.get(item.row[0]);
      if (shape?.length) {
        ctx.beginPath();
        for (const ring of shape) { ring.forEach(([px, py], i) => { const point = this.project(px, py); if (i) ctx.lineTo(...point); else ctx.moveTo(...point); }); ctx.closePath(); }
        ctx.globalAlpha = status === 'same' ? .65 : .9; ctx.fill('evenodd'); ctx.globalAlpha = 1; ctx.strokeStyle = '#f0f1e4'; ctx.lineWidth = .65; ctx.stroke();
      } else { const size = Math.min(5, Math.max(1.8, this.scale*3)); ctx.fillRect(x-size/2, y-size/2, size, size); }
    }
    if (this.scale > .25) {
      const needed = new Map(visible.filter(p => !geometry.has(p.row[0])).map(p => [p.row[0].slice(6, 9), p.row[0]]));
      for (const [shard, key] of [...needed].slice(0, 8)) {
        if (this.geometryRequests.has(shard)) continue;
        this.geometryRequests.add(shard);
        loadGeometry(key).then(() => this.draw()).catch(error => { this.geometryRequests.delete(shard); $('#map-progress').textContent = `Outlines unavailable: ${error.message} Locations remain visible.`; });
      }
    }
    if (state.selected != null) {
      const row = rows[state.selected], [x,y] = this.project(row[3], row[4]);
      ctx.beginPath(); ctx.arc(x,y,8,0,Math.PI*2); ctx.fillStyle = '#fff9e5'; ctx.fill(); ctx.strokeStyle = '#233c30'; ctx.lineWidth = 2; ctx.stroke();
      if (x > 0 && x < w && y > 0 && y < h) { ctx.font = '11px Arial'; const label = title(row[1]); const tw = ctx.measureText(label).width; ctx.fillStyle = '#173d36'; const tx = Math.max(8, Math.min(w-tw-22, x+14)); ctx.fillRect(tx-6,y-12,tw+12,24); ctx.fillStyle = '#faf7e9'; ctx.fillText(label,tx,y+4); }
    }
    if (state.hood === '' && !state.group && this.scale < .15) {
      ctx.font = '10px Arial'; ctx.fillStyle = '#344f3d';
      for (const name of ['EASTWOOD', 'DOWNTOWN', 'SOUTH VALLEY', 'NORTHSIDE', 'TIPP HILL']) {
        const hood = manifest.neighborhoods.indexOf(name), points = this.items.filter(p => p.row[2] === hood);
        if (!points.length) continue;
        const [x,y] = this.project(points.reduce((n,p) => n+p.row[3],0)/points.length,points.reduce((n,p) => n+p.row[4],0)/points.length);
        ctx.fillStyle = '#f6f3ebdb'; const tw = ctx.measureText(name).width; ctx.fillRect(x-tw/2-4,y-12,tw+8,18); ctx.fillStyle = '#344f3d'; ctx.fillText(name,x-tw/2,y);
      }
    }
    $('#map-scale').textContent = this.scale > .25 ? 'LATEST OUTLINES · + / − TO ZOOM' : 'PARCEL LOCATIONS · + / − TO ZOOM';
  }
}

function bind() {
  for (const [id, key] of [['from-snapshot', 'from'], ['to-snapshot', 'to'], ['lens', 'lens'], ['neighborhood', 'hood']]) {
    $(`#${id}`).onchange = () => {
      const v = $(`#${id}`).value;
      state[key] = ['from', 'to'].includes(key) ? +v : v;
      if (!validInterval(state.from, state.to)) { state.from = 0; state.to = 12; }
      const notice = $('#comparison-adjustment');
      if (key === 'lens' || key === 'from' || key === 'to') notice.hidden = true;
      if (state.lens === 'units') {
        const interval = unitInterval(manifest.snapshots, state.from, state.to);
        if (interval.adjusted) {
          state.from = interval.from; state.to = interval.to;
          notice.textContent = `Housing units: switched to ${manifest.snapshots[state.from].label}–${manifest.snapshots[state.to].label} because the previous dates lack usable unit counts. Dates without reliable counts are disabled. The dates shown above are the ones being compared.`;
          notice.hidden = false;
        }
      }
      state.filter = null;
      if (key === 'hood') state.group = '';
      syncControls(); update(key === 'hood');
    };
  }
  $('#address-search').oninput = () => {
    const query = clean($('#address-search').value), list = $('#search-results');
    if (query.length < 2) { list.hidden = true; return; }
    const tokens = query.split(' ');
    const matches = rows.map((row, i) => ({ row, i })).filter(({ row }) => tokens.every(t => row[1].includes(t)) || row[0] === query).sort((a,b) => b.row[7]-a.row[7]).slice(0, 12);
    list.hidden = false;
    list.innerHTML = matches.map(({ row, i }) => `<li><button data-search-index="${i}">${esc(title(row[1]))}<small>${esc(title(manifest.neighborhoods[row[2]]))} · ${esc(row[0])}${row[7] !== 12 ? ' · Historical record' : ''}</small></button></li>`).join('') || '<li><p style="padding:12px">No matching address. Try a street name or tax ID.</p></li>';
  };
  $('#address-search').onkeydown = e => {
    if (e.key === 'Escape') $('#search-results').hidden = true;
    if (e.key === 'ArrowDown') { e.preventDefault(); $('#search-results button')?.focus(); }
    if (e.key === 'Enter') $('#search-results button')?.click();
  };
  document.addEventListener('click', async e => {
    const search = e.target.closest('[data-search-index]');
    const indexed = e.target.closest('[data-index]');
    const feature = e.target.closest('[data-parcel]');
    const neighborhood = e.target.closest('[data-neighborhood]');
    const branch = e.target.closest('[data-from-use]');
    const block = e.target.closest('[data-block]');
    const persistent = e.target.closest('[data-persistent]');
    if (search || feature) {
      const i = search ? +search.dataset.searchIndex : rows.findIndex(r => r[0] === feature.dataset.parcel);
      state.hood = ''; state.group = ''; state.vacancy = ''; state.filter = null;
      syncControls(); await update(false);
      if (feature) $('#explore').scrollIntoView();
      await selectParcel(i);
    } else if (indexed) { await selectParcel(+indexed.dataset.index); $('#property-heading')?.focus({ preventScroll: true }); }
    else if (neighborhood) { state.hood = String(manifest.neighborhoods.indexOf(neighborhood.dataset.neighborhood)); state.group = ''; state.vacancy = ''; state.filter = null; syncControls(); await update(true); $('#explore').scrollIntoView(); }
    else if (branch) {
      state.from = 0; state.to = 12; state.hood = ''; state.group = ''; state.vacancy = ''; state.lens = 'use';
      state.filter = { kind: 'transition', source: branch.dataset.fromUse, destination: branch.dataset.toUse, label: `${title(branch.dataset.fromUse)} → ${title(branch.dataset.toUse)}` };
      syncControls(); await update(true); $('#explore').scrollIntoView();
    } else if (persistent) {
      state.from = 0; state.to = 12; state.hood = ''; state.group = ''; state.filter = null; state.lens = 'use';
      state.vacancy = persistent.dataset.persistent;
      $('#comparison-adjustment').hidden = true;
      syncControls(); await update(true); $('#explore').scrollIntoView();
    } else if (block) selectGroup(block.dataset.block, 'block');
    else if (!e.target.closest('.search-control')) $('#search-results').hidden = true;
  });
  $('#previous-page').onclick = () => { state.page--; renderList(); };
  $('#next-page').onclick = () => { state.page++; renderList(); };
  for (const side of ['a', 'b']) $(`#compare-${side}`).onchange = () => neighborhoodCard(side);
  $('#vacancy-filter').onchange = () => {
    state.vacancy = $('#vacancy-filter').value;
    state.filter = null;
    update(true);
  };

}

async function init() {
  try {
    manifest = await get('manifest.json');
    fillStory(); fillControls();
    rows = await get('index.json');
    map = new ParcelMap($('#parcel-map'));
    bind(); neighborhoodCard('a'); neighborhoodCard('b');
    await update(true);
    const id = new URL(location.href).searchParams.get('parcel');
    if (id) { const i = rows.findIndex(r => r[0] === id); if (i >= 0) { await selectParcel(i); $('#explore').scrollIntoView(); } }
    const observer = new IntersectionObserver(entries => {
      if (!entries.some(e => e.isIntersecting)) return;
      observer.disconnect();
      manifest.featured.forEach((key, i) => loadGeometry(key).then(shape => $(`#portrait-${i}`).insertAdjacentHTML('beforeend', outlineSvg(shape))).catch(error => { $(`#portrait-${i}`).insertAdjacentHTML('beforeend', `<p class="small">${esc(error.message)}</p>`); }));
    }, { rootMargin: '500px' });
    observer.observe($('#biographies'));
  } catch (error) { showError(error); $('#map-progress').textContent = 'The archive could not load. See the message above.'; }
}

init();
