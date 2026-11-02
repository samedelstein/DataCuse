'use strict';
const evidence = window.EVIDENCE;
const schemas = new Map(evidence.schemas.map((row) => [row.id, row]));
const link = (url, label) => `<a href="${escapeHtml(url)}">${escapeHtml(label)}</a>`;
const serviceMetaUrl = (url) => `${url}?f=pjson`;

el('series-table').innerHTML = `<table><thead><tr><th>Dataset series</th>${Array.from({length:10}, (_,i) => `<th>${2017+i}</th>`).join('')}</tr></thead><tbody>${evidence.series.map((series) => `<tr><th scope="row">${escapeHtml(series.name)}</th>${Object.entries(series.years).map(([year, ids]) => `<td class="edition ${ids.length ? 'present' : ''}">${ids.length ? link(schemas.get(ids[0]).url, ids.length === 1 ? (series.ranges[ids[0]] ? 'Range' : '1 entry') : `${ids.length} entries`) : '<span aria-label="No matching titled edition">—</span>'}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
el('comparison-select').innerHTML = evidence.comparisons.map((c) => `<option value="${c.key}">${escapeHtml(c.title)}</option>`).join('') + '<option value="custom">Custom comparison</option>';
const options = [...evidence.schemas].sort((a,b) => a.title.localeCompare(b.title)).map((s) => `<option value="${s.id}">${escapeHtml(s.title)} (${s.field_count} fields)</option>`).join('');
el('schema-before').innerHTML = options;
el('schema-after').innerHTML = options;

function renderSchema() {
  const left = schemas.get(el('schema-before').value);
  const right = schemas.get(el('schema-after').value);
  const before = new Map(left.fields.map((f) => [f.name.toLowerCase(),f]));
  const after = new Map(right.fields.map((f) => [f.name.toLowerCase(),f]));
  const oldOnly = left.fields.filter((f) => !after.has(f.name.toLowerCase()));
  const newOnly = right.fields.filter((f) => !before.has(f.name.toLowerCase()));
  const shared = left.fields.filter((f) => after.has(f.name.toLowerCase()));
  const editorial = evidence.comparisons.find((c) => c.old === left.id && c.new === right.id);
  el('comparison-note').innerHTML = editorial ? `<strong>${escapeHtml(editorial.title)}.</strong> ${escapeHtml(editorial.meaning)}<p>${escapeHtml(editorial.caution)}</p>` : 'Custom comparison: name differences alone cannot distinguish removed concepts from renames, different scopes, or different source systems.';
  el('schema-totals').innerHTML = `<div><strong>${left.field_count}</strong>${link(left.url, left.title)}<small>${link(serviceMetaUrl(left.service_url), 'Inspect left schema')}</small></div><span aria-hidden="true">→</span><div><strong>${right.field_count}</strong>${link(right.url, right.title)}<small>${link(serviceMetaUrl(right.service_url), 'Inspect right schema')}</small></div><div><strong>${shared.length}</strong><span>Matched field names</span></div>`;
  const renderFields = (fields) => fields.length ? fields.map((f) => `<li><code>${escapeHtml(f.name)}</code><small>${escapeHtml(f.alias)} · ${escapeHtml(f.type.replace('esriFieldType',''))}</small></li>`).join('') : '<li>None</li>';
  el('fields-before').innerHTML = renderFields(oldOnly);
  el('fields-after').innerHTML = renderFields(newOnly);
  el('fields-common').innerHTML = `<table><thead><tr><th>Left name</th><th>Right name</th><th>Left type</th><th>Right type</th></tr></thead><tbody>${shared.map((f) => {const other=after.get(f.name.toLowerCase());return `<tr class="${f.type !== other.type ? 'type-change' : ''}"><td>${escapeHtml(f.name)}</td><td>${escapeHtml(other.name)}</td><td>${escapeHtml(f.type.replace('esriFieldType',''))}</td><td>${escapeHtml(other.type.replace('esriFieldType',''))}${f.type !== other.type ? ' · changed' : ''}</td></tr>`;}).join('')}</tbody></table>`;
}
function selectComparison() {
  const comparison = evidence.comparisons.find((c) => c.key === el('comparison-select').value);
  if (comparison) {el('schema-before').value=comparison.old;el('schema-after').value=comparison.new;}
  renderSchema();
}
el('comparison-select').addEventListener('change', selectComparison);
['schema-before','schema-after'].forEach((id) => el(id).addEventListener('change', () => {el('comparison-select').value='custom';renderSchema();}));
const requested = new URLSearchParams(window.location.search).get('compare');
if (evidence.comparisons.some((c) => c.key === requested)) el('comparison-select').value=requested;
selectComparison();

el('history-summary').textContent = `${evidence.summary.historical_ids} archived item links absent from the feed: ${evidence.summary.historical_statuses['Permission denied']} permission denied, ${evidence.summary.historical_statuses['Missing or inaccessible']} missing or inaccessible, ${evidence.summary.historical_statuses['Public item, absent from feed']} still public. Results reflect the October 27 check.`;
function renderHistory() {
  const query = el('history-search').value.toLowerCase();
  const rows=evidence.history.filter((r) => `${r.title} ${r.id}`.toLowerCase().includes(query) && (!el('history-status').value || r.status===el('history-status').value));
  el('history-count').textContent=`${rows.length} of ${evidence.history.length} historical items`;
  el('history-rows').innerHTML=rows.length ? rows.map((r) => `<tr><td>${escapeHtml(r.title)}<small>${r.id}</small></td><td>${r.capture_date}</td><td>${escapeHtml(r.status)}${r.service_matches.length ? `<small>${r.service_matches.map((url) => link(serviceMetaUrl(url), 'Service still reachable')).join(' · ')}</small>` : ''}</td><td>${link(r.archive_url,'Archived page')}<br>${link(r.current_url,'Current item response')}</td></tr>`).join('') : '<tr><td colspan="4">No matching historical items.</td></tr>';
}
['history-search','history-status'].forEach((id) => el(id).addEventListener('input',renderHistory));
renderHistory();
el('directory-summary').textContent = `${evidence.summary.directory_services} listed services: ${evidence.summary.directory_linked} match portal dataset links; ${evidence.summary.directory_not_linked} do not. Metadata was available for ${evidence.summary.directory_metadata_available}. Four portal services are hosted elsewhere.`;
function renderDirectory() {
  const query=el('service-search').value.toLowerCase();
  const filter=el('service-status').value;
  const rows=evidence.directory.filter((r) => `${r.name} ${r.layers.join(' ')}`.toLowerCase().includes(query) && (!filter || filter==='matched' && r.catalog_id || filter==='unmatched' && !r.catalog_id || filter==='unavailable' && r.status==='Metadata unavailable'));
  el('service-count').textContent=`${rows.length} of ${evidence.directory.length} listed services`;
  el('service-rows').innerHTML=rows.length ? rows.map((r) => `<tr><td>${link(serviceMetaUrl(r.url),r.name)}<small>${escapeHtml(r.layers.join('; '))}</small></td><td>${r.catalog_id ? link(schemas.get(r.catalog_id).url,r.catalog_title) : 'No matching dataset link'}</td><td>${r.status}</td><td>${r.layer_count} + ${r.table_count}</td></tr>`).join('') : '<tr><td colspan="4">No matching services.</td></tr>';
}
['service-search','service-status'].forEach((id) => el(id).addEventListener('input',renderDirectory));
renderDirectory();

// One topic at a time, with ordinary links for bookmarks and browser history.
const panelIds = ['history','maintenance','series','schema','archive','services','explorer','methods'];
function showPanel() {
  const requestedPanel = window.location.hash.slice(1);
  const active = panelIds.includes(requestedPanel) ? requestedPanel : requested ? 'schema' : 'history';
  panelIds.forEach((id) => {
    el(id).hidden = id !== active;
    if (id === active) el(`nav-${id}`).setAttribute('aria-current','location');
    else el(`nav-${id}`).removeAttribute('aria-current');
  });
}
window.addEventListener('hashchange', showPanel);
showPanel();
