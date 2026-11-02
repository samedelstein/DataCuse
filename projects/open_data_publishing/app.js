/* The page reads a saved public catalog snapshot; it makes no live API requests. */
'use strict';
const { summary, datasets, excluded } = window.CATALOG;
const el = (id) => document.getElementById(id);
const escapeHtml = (value) => String(value ?? '').replace(/[&<>"']/g, (c) => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c]));
const date = (value) => value ? value.slice(0, 10) : 'Unknown';
const currentYear = Number(summary.as_of.slice(0, 4));
const cutoff = summary.as_of.slice(5, 10);
let selectedMonth = '';

el('snapshot').textContent = `Snapshot: ${new Date(summary.as_of).toLocaleDateString('en-US', { year:'numeric', month:'long', day:'numeric', timeZone:'UTC' })} · Independent analysis · Not live`;
const thisYear = summary.years.find((y) => y.year === currentYear);
const lastYear = summary.years.find((y) => y.year === currentYear - 1);
const peak = summary.years.reduce((a, b) => a.created >= b.created ? a : b);
el('stats').innerHTML = [
  [summary.dataset_count, 'Current dataset entries', `${summary.catalog_entries} feed records; ${summary.excluded_count} excluded`],
  [thisYear.created, `Entries created in ${currentYear}`, `Through ${summary.as_of.slice(0, 10)}; ${lastYear.created_same_period} in the same period last year`],
  [peak.created, `Created in ${peak.year}`, 'Largest group among surviving entries'],
  [summary.freshness['Within 30 days'] || 0, 'Data edits in the past 30 days', `${summary.service_timestamp_count} datasets have usable service timestamps`],
].map(([value, label, note]) => `<div class="stat"><strong>${value}</strong><span>${label}</span><p>${note}</p></div>`).join('');
el('trend').textContent = `Of the ${summary.dataset_count} entries in this snapshot, ${peak.created} have a ${peak.year} creation date, the largest group. ${thisYear.created} were created in ${currentYear} through ${cutoff}, compared with ${lastYear.created_same_period} over the same period in ${lastYear.year}. Annual editions, replacement items, and backfills count separately. These counts cannot establish the total number published in each year.`;

function renderCharts() {
  const measure = el('date-measure').value;
  const cumulative = el('chart-view').value === 'cumulative';
  const samePeriod = el('same-period').checked;
  el('same-period').disabled = cumulative;
  const values = summary.years.map(({ year }) => ({ year, value:datasets.filter((r) => {
    const value = r[measure];
    return cumulative ? Number(value.slice(0, 4)) <= year : Number(value.slice(0, 4)) === year && (!samePeriod || value.slice(5, 10) <= cutoff);
  }).length }));
  const max = Math.max(...values.map((y) => y.value), 1);
  el('annual-chart').innerHTML = values.map(({ year, value }) => `<div class="bar-column"><span class="bar-value">${value}</span><div class="bar ${year === currentYear ? 'current' : ''}" style="height:${value / max * 85}%" title="${year}: ${value} entries"></div><span class="bar-label">${year}${year === currentYear ? '*' : ''}</span></div>`).join('');
  el('chart-title').textContent = cumulative ? 'Cumulative surviving entries — not historical catalog totals' : `Still-listed dataset entries by ${measure === 'created' ? 'creation' : 'metadata publication'} year`;
  const dateExplanation = measure === 'created' ? 'Item creation can predate public release.' : 'Uses formal publication, then formal creation, then item creation. Metadata dates are editable.';
  el('chart-caption').textContent = cumulative ? `Only entries still listed on ${summary.as_of.slice(0, 10)}, dated on or before each year. This is not the catalog size then. Missing historical entries are excluded; no complete removal history was recovered. ${dateExplanation} *${currentYear} is partial.` : `Of the entries still listed on ${summary.as_of.slice(0, 10)}, how many carry a date in each year? Missing historical entries are excluded. ${samePeriod ? `Each year: January 1–${cutoff}.` : `*${currentYear}: through ${cutoff}. Earlier years: full calendar years.`} ${dateExplanation}`;
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const counts = {};
  datasets.forEach((r) => { const key = r[measure].slice(0, 7); counts[key] = (counts[key] || 0) + 1; });
  const largest = Math.max(...Object.values(counts), 1);
  el('heatmap').innerHTML = '<span></span>' + months.map((m) => `<span class="heat-label">${m}</span>`).join('') + summary.years.map(({ year }) => `<span class="heat-label">${year}</span>` + months.map((m, index) => {
    const key = `${year}-${String(index + 1).padStart(2, '0')}`;
    const future = key > summary.as_of.slice(0, 7);
    const count = counts[key] || 0;
    const alpha = count ? .12 + count / largest * .73 : 0;
    return `<button class="month" data-month="${key}" ${future ? 'disabled' : ''} aria-pressed="${selectedMonth === key}" aria-label="${m} ${year}: ${future ? 'future month' : `${count} entries`}" title="${m} ${year}: ${count} entries" style="${count ? `background:rgba(39,94,73,${alpha});color:${alpha > .5 ? 'white' : 'var(--ink)'}` : ''}">${future ? '' : count}</button>`;
  }).join('')).join('');
  el('month-status').textContent = selectedMonth ? `Dataset list filtered to ${selectedMonth}. Select again to clear.` : 'No month selected.';
}

function horizontalChart(target, values, order) {
  const max = Math.max(...Object.values(values), 1);
  el(target).innerHTML = order.map((label) => `<div class="horizontal"><span>${label}</span><div class="track"><div class="fill" style="width:${(values[label] || 0) / max * 100}%"></div></div><strong>${values[label] || 0}</strong></div>`).join('');
}
horizontalChart('frequency-chart', summary.frequencies, Object.keys(summary.frequencies).sort((a,b) => summary.frequencies[b] - summary.frequencies[a]));
horizontalChart('freshness-chart', summary.freshness, ['Within 30 days','31–90 days','91–365 days','Over a year','Unknown', ...(summary.freshness['Future timestamp'] ? ['Future timestamp'] : [])]);
const daily = datasets.filter((r) => r.frequency === 'Daily');
const recentDaily = daily.filter((r) => r.freshness === 'Within 30 days');
el('maintenance-note').textContent = `${summary.frequencies['Not planned']} datasets explicitly declare no planned updates, and ${summary.frequencies['Not specified']} have no schedule in formal metadata. ${recentDaily.length} of ${daily.length} datasets marked daily show a data edit within 30 days. A single snapshot cannot verify that they actually update every day.`;
el('scope-note').textContent = `The DCAT feed contains ${summary.catalog_entries} records. We count ${summary.dataset_count} unique items confirmed as Feature Service by ArcGIS item metadata, including spatial layers and nonspatial tables. We exclude ${Object.entries(summary.excluded_types).map(([type, count]) => `${count} ${type} entries`).join(', ')}.`;
el('date-note').textContent = `${summary.formal_publication_dates} datasets have a formal publication date; ${summary.date_disagreements} differ from the feed’s issued calendar date. ${summary.data_dictionary_count} descriptions mention a data dictionary. The feed supplies no usable contact email addresses (${summary.contact_email_count} of ${summary.dataset_count}); this does not establish whether contacts exist elsewhere.`;
el('excluded').innerHTML = excluded.map((r) => `<p><a href="${escapeHtml(r.url)}">${escapeHtml(r.title)}</a> · ${escapeHtml(r.type)}</p>`).join('');
el('year-filter').innerHTML += [...summary.years].reverse().map(({ year }) => `<option value="${year}">${year}</option>`).join('');
el('frequency-filter').innerHTML += Object.keys(summary.frequencies).sort().map((f) => `<option>${f}</option>`).join('');

function renderTable() {
  const query = el('search').value.trim().toLowerCase();
  const year = el('year-filter').value;
  const frequency = el('frequency-filter').value;
  const measure = el('date-measure').value;
  const rows = datasets.filter((r) => (!query || `${r.title} ${r.tags.join(' ')}`.toLowerCase().includes(query)) && (!year || r[measure].startsWith(year)) && (!frequency || r.frequency === frequency) && (!selectedMonth || r[measure].startsWith(selectedMonth)));
  const sorting = el('sort').value;
  rows.sort((a,b) => sorting === 'title' ? a.title.localeCompare(b.title) : sorting === 'edited' ? (b.data_last_edit || '').localeCompare(a.data_last_edit || '') : sorting === 'oldest' ? a.created.localeCompare(b.created) : b.created.localeCompare(a.created));
  el('result-count').textContent = `${rows.length} of ${datasets.length} datasets · Year and month filters use ${measure === 'created' ? 'item creation' : 'metadata publication'} dates. Dates shown as YYYY-MM-DD.`;
  el('dataset-rows').innerHTML = rows.length ? rows.map((r) => `<tr><td><a href="${escapeHtml(r.url)}">${escapeHtml(r.title)} ↗</a><small><a href="${escapeHtml(r.service_url)}?f=pjson">Service metadata</a> · <a href="https://www.arcgis.com/sharing/rest/content/items/${r.id}?f=pjson">Item metadata</a></small></td><td>${date(r.created)}</td><td>${date(r.published)}<small>${escapeHtml(r.published_source)}${r.date_disagrees ? ' · differs from feed' : ''}</small></td><td>${date(r.data_last_edit)}<small>${escapeHtml(r.freshness)}</small></td><td>${escapeHtml(r.frequency)}</td></tr>`).join('') : '<tr><td colspan="5">No datasets match these filters.</td></tr>';
}
['date-measure','chart-view','same-period'].forEach((id) => el(id).addEventListener('change', () => { renderCharts(); renderTable(); }));
['search','year-filter','frequency-filter','sort'].forEach((id) => el(id).addEventListener('input', renderTable));
el('heatmap').addEventListener('click', (event) => { const button = event.target.closest('[data-month]'); if (!button || button.disabled) return; selectedMonth = selectedMonth === button.dataset.month ? '' : button.dataset.month; el('year-filter').value = ''; renderCharts(); renderTable(); });
el('reset').addEventListener('click', () => { selectedMonth = ''; ['search','year-filter','frequency-filter'].forEach((id) => { el(id).value = ''; }); el('sort').value = 'newest'; renderCharts(); renderTable(); });
renderCharts();
renderTable();
