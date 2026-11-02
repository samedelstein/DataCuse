"""Read-only collection. Writes a candidate; never replaces the approved catalog."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import re
import time
from urllib.error import HTTPError
from urllib.parse import quote, unquote, urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
FEED = 'https://data.syr.gov/api/feed/dcat-us/1.1.json'
DIRECTORY = 'https://services6.arcgis.com/bdPqSfflsdgFRVVM/ArcGIS/rest/services'
CURATED = {'2021_Road_Rating', '2022_Fire_data_csv', '2023_Fire_Data_csv', '2024_Fire_Data_csv', 'Certificate_of_Compliance_(Housing)', 'Potholes_filled_2018'}

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def now():
    return datetime.now(timezone.utc).isoformat()

def normal(url):
    return unquote(url).lower().split('?')[0].rstrip('/')

def get(url, output, attempts=3):
    url = quote(url, safe=':/?=&%(),')
    result = {'url': url, 'checked_at': now()}
    for attempt in range(attempts):
        try:
            with urlopen(Request(url, headers={'User-Agent': 'DataCuse-open-data-library/1.0'}), timeout=35) as r:
                body = r.read()
                result.update(http_status=r.status, sha256=hashlib.sha256(body).hexdigest(), data=json.loads(body))
                if result['data'].get('error'):
                    raise ValueError(json.dumps(result['data']['error']))
            break
        except (OSError, ValueError) as exc:
            if isinstance(exc, HTTPError) and exc.code in (429, 502, 503, 504) and attempt + 1 < attempts:
                time.sleep(min(10, 2 ** attempt))
                continue
            result['error'] = str(exc)
            break
    write(output, result)
    return result

def feed_index(feed):
    urls, ids = set(), set()
    for row in feed['dataset']:
        serialized = json.dumps(row)
        for url in re.findall(r'https?[^\s"<>]+', serialized):
            match = re.search(r'https?://[^\s"<>]+?/FeatureServer(?:/\d+)?', url, re.I)
            if match:
                urls.add(normal(match.group()))
        identifier = row.get('identifier', '')
        match = re.search(r'id=([a-f0-9]{32})', identifier)
        layer = re.search(r'sublayer=(\d+)', identifier)
        if match:
            ids.add((match[1], layer[1] if layer else None))
    return urls, ids

def membership(url, item_id, feed_urls, feed_ids):
    root, _, layer = normal(url).rpartition('/')
    if normal(url) in feed_urls or root in feed_urls or (item_id, layer) in feed_ids or (item_id, None) in feed_ids:
        return 'official-catalog'
    return 'no-catalog-match'

def topic(name):
    name = name.lower()
    for words, label in [('fire police crime rtk', 'Public safety'), ('pothole road street sidewalk traffic', 'Streets'), ('housing compliance parcel property code vacant rental permit', 'Housing'), ('water lead watershed sewer', 'Water & environment'), ('budget fund finance', 'City finances')]:
        if any(w in name for w in words.split()):
            return label
    return 'City & neighborhoods'

def title_years(name):
    return sorted({year for year in re.findall(r'(?<![a-zA-Z0-9])(?:19|20)\d{2}(?![a-zA-Z0-9])', name) if int(year) <= datetime.now(timezone.utc).year + 1})

def differences(old, new):
    before = {r['id']: r for r in old.get('datasets', [])}
    changes = []
    for row in new['datasets']:
        prior = before.pop(row['id'], None)
        if prior is None:
            changes.append({'id': row['id'], 'change': 'discovered'})
            continue
        for field in ['availability', 'membership', 'fields', 'coverage', 'source_sha256']:
            if prior.get(field) != row.get(field):
                changes.append({'id': row['id'], 'change': field, 'before': prior.get(field), 'after': row.get(field)})
    for row in before.values():
        changes.append({'id': row['id'], 'change': 'not-listed-this-check', 'note': 'Absence does not establish deletion.'})
    return changes

def collect(output, baseline):
    raw = output / 'evidence'
    prior = json.loads(baseline.read_text(encoding='utf-8')) if baseline.exists() else {'datasets': []}
    feed = get(FEED, raw / 'official-catalog.json')
    directory = get(DIRECTORY + '?f=pjson', raw / 'directory.json')
    if feed.get('error') or directory.get('error') or not feed.get('data', {}).get('dataset') or not directory.get('data', {}).get('services'):
        write(output / 'report.json', {'status': 'failed', 'reason': 'Required inventory unavailable; approved catalog unchanged.'})
        raise SystemExit('Required inventory unavailable; candidate not built.')
    feed_urls, feed_ids = feed_index(feed['data'])
    services = directory['data']['services']
    def root_job(service):
        sid = hashlib.sha256(normal(service['url']).encode()).hexdigest()[:16]
        response = get(service['url'] + '?f=json', raw / (sid + '.json'))
        meta = response.get('data', {})
        layers = meta.get('layers', []) + meta.get('tables', [])
        return dict(service, id=sid, item_id=meta.get('serviceItemId'), checked_at=response['checked_at'], availability='unavailable' if response.get('error') else 'available', layers=layers, error=response.get('error'))
    with ThreadPoolExecutor(max_workers=5) as pool:
        roots = list(pool.map(root_job, services))
    jobs = []
    for service in roots:
        statuses = []
        for layer in service['layers']:
            url = service['url'] + '/' + str(layer['id'])
            state = membership(url, service['item_id'], feed_urls, feed_ids)
            statuses.append(state)
            if state != 'official-catalog' or any(r.get('source_url') == url for r in prior['datasets']):
                jobs.append((service, layer, state))
        service['membership'] = 'official-catalog' if statuses and all(s == 'official-catalog' for s in statuses) else 'no-catalog-match' if statuses else 'unknown'
    def layer_job(job):
        service, layer, state = job
        url = service['url'] + '/' + str(layer['id'])
        key = 'arcgis-' + service['id'] + '-' + str(layer['id'])
        response = get(url + '?f=json', raw / (key + '.json'))
        meta = response.get('data', {})
        curated = service['name'] in CURATED
        count = get(url + '/query?f=json&where=1%3D1&returnCountOnly=true', raw / (key + '-count.json')) if curated and not response.get('error') else {}
        years = title_years(service['name'])
        title = service['name'].replace('_', ' ')
        description = html.unescape(re.sub('<[^>]+>', ' ', meta.get('description') or ''))
        description = re.sub(r'\s+', ' ', description).strip()
        title += (' · ' + layer['name']) if len(service['layers']) > 1 else ''
        return {'id': key, 'title': title, 'description': description or 'Public ArcGIS layer. The source provides no description; scope needs review.', 'topic': topic(title), 'family': re.sub(r'\s+', ' ', re.sub(r'\b(?:19|20)\d{2}\b', '', service['name'].replace('_', ' '))).strip().lower(), 'source_url': url, 'source_page': url, 'service_id': service['id'], 'item_id': service['item_id'], 'layer_id': layer['id'], 'format': 'ArcGIS API', 'membership': state, 'match_method': 'DCAT item ID and layer or normalized service URL. Similar topics may exist under other names.', 'availability': 'unavailable' if response.get('error') else 'available', 'curated': curated, 'checked_at': response['checked_at'], 'coverage': ', '.join(years) + ' (source title; completeness unverified)' if years else 'Not documented', 'years': years, 'fields': [{k: f.get(k) for k in ('name', 'alias', 'type', 'length', 'nullable', 'domain')} for f in meta.get('fields', [])], 'record_count': count.get('data', {}).get('count'), 'object_id_field': meta.get('objectIdField'), 'max_record_count': meta.get('maxRecordCount'), 'query_capabilities': meta.get('advancedQueryCapabilities', {}), 'data_last_edit': meta.get('editingInfo', {}).get('dataLastEditDate'), 'source_sha256': response.get('sha256'), 'limitations': ['No catalog match found is a discovery result, not evidence that data was deliberately withheld.', 'Service edit dates do not establish observation coverage or regular publication.', 'Views and editions can overlap; do not add their record counts.'] + (['Fire dataset title does not establish that this includes all fire incidents.'] if 'Fire' in title else []), 'error': response.get('error')}
    with ThreadPoolExecutor(max_workers=5) as pool:
        rows = list(pool.map(layer_job, jobs))
    seen = {r['id'] for r in rows}
    for old in prior['datasets']:
        if old['id'] not in seen:
            root_state = next((s for s in roots if s['id'] == old.get('service_id')), None)
            unavailable = root_state is not None and root_state['availability'] == 'unavailable'
            rows.append(dict(old, availability='unavailable' if unavailable else 'not-listed-this-check', error=root_state.get('error') if unavailable else None, last_successful_check=old.get('last_successful_check') or old.get('checked_at'), checked_at=now()))
        elif next(r for r in rows if r['id'] == old['id'])['availability'] == 'unavailable':
            index = next(i for i, r in enumerate(rows) if r['id'] == old['id'])
            failed = rows[index]
            rows[index] = dict(old, availability='unavailable', checked_at=failed['checked_at'], error=failed.get('error'), last_successful_check=old.get('last_successful_check') or old['checked_at'], membership=failed['membership'])
    from official import augment
    rows, official_report = augment(feed, rows, roots, raw)
    write(output / 'official-report.json', official_report)
    candidate = {'official_checked_at': feed['checked_at'], 'version': 1, 'checked_at': now(), 'official_feed': FEED, 'directory_url': DIRECTORY, 'official_entry_count': len(feed['data']['dataset']), 'services': roots, 'datasets': rows}
    write(output / 'catalog.json', candidate)
    write(output / 'report.json', {'status': 'candidate-only', 'checked_at': candidate['checked_at'], 'changes': differences(prior, candidate), 'service_count': len(roots), 'layer_count': len(rows), 'errors': [r['id'] for r in rows if r['availability'] != 'available']})
    print(f'Candidate saved: {len(roots)} services, {len(rows)} layers. Approved data unchanged.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT / 'candidate')
    parser.add_argument('--baseline', type=Path, default=ROOT / 'data/catalog.json')
    args = parser.parse_args()
    collect(args.output, args.baseline)
