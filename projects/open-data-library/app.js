const escapeHtml = (text) => String(text ?? '').replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const synonyms = {rental:'housing compliance',landlord:'housing compliance',spending:'budget finances',money:'budget finances',drinking:'water',cloudy:'turbidity',stops:'right know crb',pavement:'road streets',firefighter:'fire'};
export function matches(row, query) {
  const haystack = `${row.title} ${row.description} ${row.topic} ${row.fields} ${row.coverage} ${row.family}`.toLowerCase();
  return query.toLowerCase().trim().split(/\s+/).filter(Boolean).every((word) => [word, ...(synonyms[word] || '').split(' ').filter(Boolean)].some((term) => haystack.includes(term)));
}
export function filterRows(rows, state) {
  return rows.filter((row) => (state.scope === 'all' || (state.scope === 'official' ? row.membership === 'official-catalog' : state.scope === 'additional' ? row.curated && row.membership !== 'official-catalog' && row.availability === 'available' : (row.curated || row.membership === 'official-catalog') && row.availability === 'available')) && (!state.topic || row.topic === state.topic) && (!state.year || row.years.includes(state.year)) && (!state.format || row.format === state.format) && (!state.availability || row.availability === state.availability) && matches(row, state.q || ''));
}
const form = typeof document === 'undefined' ? null : document.querySelector('#search-form');
if (form) {
  const results = document.querySelector('#results');
  const count = document.querySelector('#result-count');
  const controls = ['q','scope','topic','year','format','availability'];
  let rows = [], page = 1;
  const pageSize = 12;
  const state = () => Object.fromEntries(controls.map((key) => [key, form.elements.namedItem(key).value]));
  function render(updateUrl = true) {
    const current = state();
    const filtered = filterRows(rows, current);
    page = Math.min(page, Math.max(1, Math.ceil(filtered.length / pageSize)));
    count.textContent = `${filtered.length} ${filtered.length === 1 ? 'table or layer' : 'tables and layers'} · ${({all:'full directory',official:'city portal',additional:'additional selected sources',curated:'city portal + selected extras'})[current.scope]}`;
    results.innerHTML = filtered.slice((page - 1) * pageSize, page * pageSize).map((r) => `<article class="card"><div class="topic">${escapeHtml(r.topic)}</div><h3><a href="datasets/${r.id}/">${escapeHtml(r.title)}</a></h3><p>${escapeHtml(r.description)}</p><div class="meta">${escapeHtml(r.coverage)}</div><div class="foot"><span class="tag">${escapeHtml(r.format)}</span><span>${r.availability !== 'available' ? escapeHtml(r.availability) : r.membership === 'official-catalog' ? 'City portal' : r.curated ? 'Additional source' : 'Metadata only'} ↗</span></div></article>`).join('') || '<div class="empty"><h3>No matches yet.</h3><p>Try fewer words, clear a filter, or switch to the full directory.</p><button class="text-button" id="empty-reset">Clear filters</button></div>';
    document.querySelector('#page-label').textContent = `Page ${page} of ${Math.max(1, Math.ceil(filtered.length / pageSize))}`;
    document.querySelector('#previous').disabled = page === 1;
    document.querySelector('#next').disabled = page * pageSize >= filtered.length;
    if (updateUrl) {
      const params = new URLSearchParams(Object.entries(current).filter(([k,v]) => v && !(k === 'scope' && v === 'curated')));
      history.replaceState(null, '', `${location.pathname}${params.size ? '?' + params : ''}`);
    }
    document.querySelector('#empty-reset')?.addEventListener('click', reset);
  }
  function reset() { form.reset(); page = 1; render(); }
  form.addEventListener('submit', (event) => event.preventDefault());
  form.addEventListener('input', () => { page = 1; render(); });
  form.addEventListener('change', () => { page = 1; render(); });
  document.querySelector('#reset').addEventListener('click', reset);
  for (const direction of ['previous','next']) document.querySelector('#' + direction).addEventListener('click', () => { page += direction === 'next' ? 1 : -1; render(); count.scrollIntoView({block:'start'}); });
  document.querySelectorAll('[data-topic]').forEach((button) => button.addEventListener('click', () => { form.elements.topic.value = button.dataset.topic; page = 1; render(); }));
  try {
    const response = await fetch('data/search-index.json');
    if (!response.ok) throw new Error('Index unavailable');
    rows = await response.json();
    for (const [key, values] of [['topic', rows.map((r) => r.topic)], ['year', rows.flatMap((r) => r.years)], ['format', rows.map((r) => r.format)]]) {
      const select = form.elements.namedItem(key);
      [...new Set(values)].sort().forEach((value) => select.add(new Option(value, value)));
    }
    const params = new URLSearchParams(location.search);
    controls.forEach((key) => { if (params.has(key)) form.elements.namedItem(key).value = params.get(key); });
    if (!form.elements.scope.value) form.elements.scope.value = 'curated';
    render(false);
  } catch {
    count.textContent = 'Search could not load.';
    results.innerHTML = '<p>Use the <a href="directory/">static directory</a> to browse every dataset, or <a href="catalog.json">download the catalog</a>.</p>';
  }
}
(typeof document === 'undefined' ? [] : document.querySelectorAll('[data-copy]')).forEach((button) => button.addEventListener('click', async () => {
  const input = document.getElementById(button.dataset.copy);
  const status = document.getElementById(button.dataset.copy + '-status');
  try { await navigator.clipboard.writeText(input.value); status.textContent = 'Copied. Paste into your preferred assistant.'; }
  catch { input.focus(); input.select(); status.textContent = 'Select and copy the highlighted prompt.'; }
}));
