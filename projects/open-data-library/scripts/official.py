"""Resolve official DCAT dataset references without copying city-hosted records."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import html
import json
from pathlib import Path
import re
from urllib.parse import parse_qs, urlsplit


def identity(entry):
    query = parse_qs(urlsplit(entry.get('identifier', '')).query)
    return query.get('id', [None])[0], query.get('sublayer', [None])[0]


def augment(feed, rows, services, raw):
    from catalog import get, normal, topic, title_years
    entries = feed['data']['dataset']
    item_ids = sorted({identity(e)[0] for e in entries if identity(e)[0]})
    def item_job(item_id):
        return item_id, get('https://www.arcgis.com/sharing/rest/content/items/' + item_id + '?f=json', raw / ('item-' + item_id + '.json'))
    with ThreadPoolExecutor(max_workers=5) as pool:
        items = dict(pool.map(item_job, item_ids))
    roots = {normal(s['url']): s for s in services}
    by_url = {normal(r['source_url']): r for r in rows}
    skipped, failures, jobs = [], [], []
    for entry in entries:
        item_id, layer_id = identity(entry)
        response = items.get(item_id, {})
        item = response.get('data', {})
        if response.get('error') or not item:
            failures.append({'title': entry['title'], 'url': entry.get('landingPage'), 'reason': response.get('error', 'No resolvable item ID')})
            for old in by_url.values():
                if old.get('item_id') == item_id:
                    old['official_reference_error'] = response.get('error', 'No resolvable item ID')
            continue
        if item.get('type') != 'Feature Service':
            skipped.append({'title': entry['title'], 'type': item.get('type'), 'url': entry.get('landingPage')})
            continue
        source = item.get('url', '').split('?')[0].rstrip('/')
        match = re.fullmatch(r'(https://.+/FeatureServer)(?:/(\d+))?', source, re.I)
        if not match:
            failures.append({'title': entry['title'], 'url': entry.get('landingPage'), 'reason': 'No supported FeatureServer URL', 'url': source})
            continue
        root_url, source_layer = match.groups()
        if layer_id is None:
            layer_id = source_layer
        service = roots.get(normal(root_url))
        if service is None:
            sid = hashlib.sha256(normal(root_url).encode()).hexdigest()[:16]
            root_response = get(root_url + '?f=json', raw / (sid + '.json'))
            meta = root_response.get('data', {})
            service = {'id': sid, 'name': item['title'], 'url': root_url, 'item_id': item_id,
                       'layers': meta.get('layers', []) + meta.get('tables', []),
                       'checked_at': root_response['checked_at'], 'availability': 'unavailable' if root_response.get('error') else 'available',
                       'membership': 'official-catalog', 'discovery': 'official-portal', 'error': root_response.get('error')}
            services.append(service)
            roots[normal(root_url)] = service
        layers = service['layers'] if layer_id is None else [{'id': int(layer_id), 'name': entry['title']}]
        if not layers:
            failures.append({'title': entry['title'], 'url': entry.get('landingPage'), 'reason': service.get('error') or 'No layers found'})
        for layer in layers:
            jobs.append((entry, service, layer, len(layers) > 1))
    # One record per source URL even when the feed references it more than once.
    grouped = {}
    for entry, service, layer, multiple in jobs:
        url = service['url'] + '/' + str(layer['id'])
        grouped.setdefault(normal(url), {'service': service, 'layer': layer, 'multiple': multiple, 'entries': []})['entries'].append(entry)
    def layer_job(pair):
        canonical, job = pair
        service, layer = job['service'], job['layer']
        entry = job['entries'][0]
        url = service['url'] + '/' + str(layer['id'])
        key = 'arcgis-' + service['id'] + '-' + str(layer['id'])
        prior = by_url.get(canonical)
        # Recheck metadata when adding a reference from a newer official feed.
        response = get(url + '?f=json', raw / (key + '.json'))
        meta = response.get('data', {})
        title = entry['title'] + (' · ' + layer['name'] if job['multiple'] else '')
        description = re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', ' ', entry.get('description') or meta.get('description') or ''))).strip()
        years = title_years(title)
        row = dict(prior) if prior else {
            'id': key, 'family': service['name'].replace('_', ' ').lower(), 'source_url': url,
            'service_id': service['id'], 'item_id': service['item_id'], 'layer_id': layer['id'],
            'format': 'ArcGIS API', 'curated': False, 'record_count': None,
            'coverage': ', '.join(years) + ' (source title; completeness unverified)' if years else 'See publisher description; record-level date range not verified', 'years': years,
        }
        row.update(title=title, description=description or 'City portal dataset; consult the publisher for scope.', topic=topic(title),
                   membership='official-catalog', source_page=entry['landingPage'], portal_url=entry['landingPage'],
                   portal_references=[{'title': e['title'], 'url': e['landingPage']} for e in job['entries']],
                   official_checked_at=feed['checked_at'], checked_at=response['checked_at'],
                   match_method='Official DCAT item ID and sublayer resolved through ArcGIS item metadata to the source URL.',
                   availability='unavailable' if response.get('error') else 'available', error=response.get('error'),
                   limitations=['City-hosted data: DataCuse indexes metadata and links to the original service; it does not mirror these records.',
                                'Portal membership does not establish completeness or currency. Source-check dates are not observation dates.',
                                'Related views and editions may overlap; do not add their counts.'])
        if response.get('error'):
            row['fields'] = row.get('fields', [])
            row['last_successful_check'] = prior.get('checked_at') if prior else None
        else:
            row.update(fields=[{k: f.get(k) for k in ('name', 'alias', 'type', 'length', 'nullable', 'domain')} for f in meta.get('fields', [])],
                       object_id_field=meta.get('objectIdField'), max_record_count=meta.get('maxRecordCount'),
                       query_capabilities=meta.get('advancedQueryCapabilities', {}),
                       date_fields_time_reference=meta.get('dateFieldsTimeReference'),
                       data_last_edit=meta.get('editingInfo', {}).get('dataLastEditDate'), source_sha256=response.get('sha256'))
        return canonical, row
    with ThreadPoolExecutor(max_workers=5) as pool:
        for canonical, row in pool.map(layer_job, grouped.items()):
            by_url[canonical] = row
    report = {'checked_at': feed['checked_at'], 'feed_entries': len(entries),
              'referenced_layers': len(grouped), 'non_feature_resources': skipped, 'failures': failures}
    return list(by_url.values()), report


if __name__ == '__main__':
    import argparse
    from catalog import FEED, get, write, feed_index, membership
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    baseline = json.loads((root / 'data/catalog.json').read_text(encoding='utf-8'))
    raw = args.output / 'evidence'
    feed = get(FEED, raw / 'official-catalog.json')
    if feed.get('error') or not feed.get('data', {}).get('dataset'):
        raise SystemExit('Official feed unavailable; approved catalog unchanged.')
    urls, ids = feed_index(feed['data'])
    for row in baseline['datasets']:
        row['membership'] = membership(row['source_url'], row.get('item_id'), urls, ids)
    baseline['datasets'], report = augment(feed, baseline['datasets'], baseline['services'], raw)
    baseline['official_entry_count'] = len(feed['data']['dataset'])
    baseline['official_checked_at'] = feed['checked_at']
    write(args.output / 'catalog.json', baseline)
    write(args.output / 'report.json', report)
    print(json.dumps({k: len(v) if isinstance(v, list) else v for k, v in report.items()}))
