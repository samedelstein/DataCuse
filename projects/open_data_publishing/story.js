'use strict';
const storyEscape = (value) => String(value ?? '').replace(/[&<>"']/g, (c) => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[c]));
const storyYears = window.CATALOG.summary.years;
const storyMax = Math.max(...storyYears.map((row) => row.created), 1);
document.getElementById('story-cohorts').innerHTML = storyYears.map((row) => `<div class="bar-column"><span class="bar-value">${row.created}</span><div class="bar ${row.year === 2026 ? 'current' : ''}" style="height:${row.created / storyMax * 85}%"></div><span class="bar-label">${row.year}${row.year === 2026 ? '*' : ''}</span></div>`).join('');
document.getElementById('historical-cases').innerHTML = ['79a29e96092840168849bebcce7addf2', '1b68035420914afcb3021624e79b9c23'].map((id) => {
  const row = window.EVIDENCE.history.find((item) => item.id === id);
  if (!row) return '';
  return `<article class="finding"><h3>${storyEscape(row.title)}</h3><p>Archived ${row.capture_date}. Current item response: <strong>${storyEscape(row.status.toLowerCase())}</strong>.${row.service_matches.length ? ' An underlying service remains reachable.' : ' No replacement or reason established.'}</p><a href="${storyEscape(row.archive_url)}">Archived page</a> · <a href="${storyEscape(row.current_url)}">Current response</a></article>`;
}).join('');
