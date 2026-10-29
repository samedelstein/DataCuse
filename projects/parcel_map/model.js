export const clean = value => value == null ? '' : String(value).trim().replace(/\s+/g, ' ').toUpperCase();
export const title = value => String(value || '').toLowerCase().replace(/\b\w/g, c => c.toUpperCase());
export const fmt = value => Number(value).toLocaleString('en-US');
export const money = value => value == null ? 'Not recorded' : new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value);
export const percent = (n, d) => d ? `${(100 * n / d).toFixed(1)}%` : '—';
export const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
export const toPack = rows => new Map(rows.map(([id, ...values]) => [id, values]));
export const numeric = value => value == null || clean(value) === '' || !Number.isFinite(Number(value)) || Number(value) < 0 ? null : Number(value);
export function reliableUnits(use, value, comparable) {
  const units = numeric(value);
  return !comparable || (['SINGLE FAMILY', 'TWO FAMILY', 'THREE FAMILY', 'APARTMENT', 'MULTIPLE RESIDENCE'].includes(clean(use)) && units === 0) ? null : units;
}

export function containsPoint(rings, x, y) {
  let inside = false;
  for (const ring of rings) {
    for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
      const [xi, yi] = ring[i], [xj, yj] = ring[j];
      if ((yi > y) !== (yj > y) && x < (xj - xi) * (y - yi) / (yj - yi) + xi) inside = !inside;
    }
  }
  return inside;
}

export function compare(before, after, lens = 'use') {
  if (!before && !after) return 'absent';
  if (!before) return 'later-only';
  if (!after) return 'earlier-only';
  const column = { use: 0, value: 1, units: 2, owner: 3 }[lens];
  const a = before[column], b = after[column];
  if (a == null || b == null || (column === 0 && (a < 0 || b < 0))) return 'unknown';
  if (a === b) return 'same';
  if (lens === 'owner') {
    if (before[6] && before[6] === after[6]) return 'same';
    if (before[4] && before[4] === after[4]) return 'name-format';
    if (before[5] && before[5] === after[5]) return 'possible-name';
  }
  if (lens === 'value' || lens === 'units') return b > a ? 'increase' : 'decrease';
  return 'changed';
}

export function ageGroup(year) {
  const n = numeric(year);
  return !n ? 'Unknown' : n < 1900 ? 'Before 1900' : n < 1940 ? '1900–1939' : n < 1980 ? '1940–1979' : '1980 onward';
}

export function validInterval(from, to) {
  return Number.isInteger(from) && Number.isInteger(to) && from >= 0 && from < to;
}

export function cohort(rows, before, after, { hood = '', group = '', groupType = 'block' } = {}) {
  return rows.map((row, i) => ({ row, i, a: before.get(i), b: after.get(i) })).filter(({ row, a, b }) =>
    (a || b) && (hood === '' || row[2] === Number(hood)) && (!group || row[groupType === 'street' ? 6 : 5] === group));
}

export function transition(rows, before, after, source, destination) {
  return rows.filter(({ i }) => before.get(i)?.[0] === source && after.get(i)?.[0] === destination);
}

export function summarize(items, lens) {
  const result = { total: items.length, comparable: 0, same: 0, changed: 0, unknown: 0, 'name-format': 0, 'possible-name': 0, 'earlier-only': 0, 'later-only': 0 };
  for (const { a, b } of items) {
    const status = compare(a, b, lens);
    if (['same', 'changed', 'increase', 'decrease'].includes(status)) {
      result.comparable++;
      result[status === 'same' ? 'same' : 'changed']++;
    } else if (status === 'name-format' || status === 'possible-name') {
      result.comparable++;
      result[status]++;
    } else if (status in result) result[status]++;
  }
  return result;
}

export function unitInterval(snapshots, from, to) {
  if (validInterval(from, to) && snapshots[from]?.unitsComparable && snapshots[to]?.unitsComparable) return { from, to, adjusted: false };
  const eligible = snapshots.map((s, i) => s.unitsComparable ? i : -1).filter(i => i >= 0);
  const preferred = snapshots.findIndex(s => s.id === '2024-q1');
  const end = eligible.at(-1);
  return { from: eligible.includes(preferred) && preferred < end ? preferred : eligible[0], to: end, adjusted: true };
}

export function unitTotals(items) {
  const result = { before: 0, after: 0, increase: 0, decrease: 0 };
  for (const { a, b } of items) {
    const status = compare(a, b, 'units');
    if (!['same', 'increase', 'decrease'].includes(status)) continue;
    result.before += a[2]; result.after += b[2];
    if (status === 'increase') result.increase++;
    if (status === 'decrease') result.decrease++;
  }
  return result;
}

export function statusLabel(status, lens) {
  if (lens === 'owner') return ({ same: 'Same name / confirmed match', changed: 'Different name — unverified', 'name-format': 'Reordered / reformatted name', 'possible-name': 'Possible name match' })[status] || ({ unknown: 'Unknown', 'earlier-only': 'Earlier only', 'later-only': 'Later only' })[status];
  return ({ same: 'Same', changed: 'Changed', increase: 'Increased', decrease: 'Decreased', unknown: 'Unknown', 'earlier-only': 'Earlier only', 'later-only': 'Later only' })[status];
}
