"""Download public Syracuse catalog evidence without third-party dependencies."""
import concurrent.futures
import datetime as dt
import json
import shutil
import sys
from pathlib import Path
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
RAW.mkdir(parents=True, exist_ok=True)


def fetch(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'DataCuse-public-metadata-research/1.0'})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode('utf-8')


def save_json(name, obj):
    (RAW / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding='utf-8')


def collect_item(item_id):
    base = f'https://www.arcgis.com/sharing/rest/content/items/{item_id}'
    item = json.loads(fetch(base + '?f=json'))
    save_json(f'item-{item_id}.json', item)
    try:
        xml = fetch(base + '/info/metadata/metadata.xml')
        (RAW / f'metadata-{item_id}.xml').write_text(xml, encoding='utf-8')
    except Exception as exc:
        (RAW / f'metadata-{item_id}.xml').write_text('<unavailable/>', encoding='utf-8')
        return {'id': item_id, 'metadata_error': str(exc)}
    return {'id': item_id}


def collect_service(record):
    item_id = urllib.parse.parse_qs(urllib.parse.urlparse(record['identifier']).query)['id'][0]
    item = json.loads((RAW / f'item-{item_id}.json').read_text(encoding='utf-8'))
    if item.get('type') != 'Feature Service':
        return None
    url = next((d.get('accessURL') for d in record.get('distribution', [])
                if d.get('format') == 'ArcGIS GeoServices REST API'), item.get('url'))
    if not url:
        return {'id': item_id, 'error': 'No service URL'}
    try:
        result = json.loads(fetch(url + ('&' if '?' in url else '?') + 'f=json'))
        save_json(f'service-{item_id}.json', result)
        return {'id': item_id, 'url': url, 'error': result.get('error')}
    except Exception as exc:
        save_json(f'service-{item_id}.json', {'error': {'message': str(exc)}})
        return {'id': item_id, 'url': url, 'error': str(exc)}


def services_and_archive():
    feed = json.loads((RAW / 'catalog.json').read_text(encoding='utf-8'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        results = [r for r in pool.map(collect_service, feed['dataset']) if r]
    save_json('service-retrieval.json', results)
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    snapshot_dir = ROOT / 'data' / 'snapshots'
    snapshot_dir.mkdir(exist_ok=True)
    shutil.make_archive(str(snapshot_dir / stamp), 'zip', RAW)
    print(json.dumps({'services': len(results), 'errors': [r for r in results if r.get('error')],
                      'snapshot': stamp}))


def main():
    if '--services-only' in sys.argv:
        services_and_archive()
        return
    # The raw directory represents the latest run; snapshot ZIPs preserve previous runs.
    retrieved = dt.datetime.now(dt.timezone.utc).isoformat()
    feed_url = 'https://data.syr.gov/api/feed/dcat-us/1.1.json'
    feed = json.loads(fetch(feed_url))
    save_json('catalog.json', feed)
    (RAW / 'homepage.html').write_text(fetch('https://data.syr.gov/'), encoding='utf-8')
    ids = sorted({urllib.parse.parse_qs(urllib.parse.urlparse(d['identifier']).query)['id'][0]
                  for d in feed['dataset']})
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(collect_item, ids))
    save_json('retrieval.json', {'retrieved_at': retrieved, 'feed_url': feed_url,
                               'catalog_records': len(feed['dataset']), 'item_count': len(ids),
                               'items': results})
    print(json.dumps({'retrieved_at': retrieved, 'records': len(feed['dataset']), 'items': len(ids)}))
    services_and_archive()


if __name__ == '__main__':
    main()
