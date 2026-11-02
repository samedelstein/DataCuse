"""Normalize the saved metadata and build auditable publishing metrics (offline)."""
import collections
import csv
import datetime as dt
import json
from pathlib import Path
import urllib.parse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
FREQUENCIES = dict(zip(
    [f'{n:03}' for n in range(1, 13)],
    ['Continual', 'Daily', 'Weekly', 'Fortnightly', 'Monthly', 'Quarterly',
     'Twice yearly', 'Annually', 'As needed', 'Irregular', 'Not planned', 'Unknown']))


def read(name):
    return json.loads((RAW / name).read_text(encoding='utf-8'))


def iso(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).isoformat() if ms else None


def parse(value):
    return dt.datetime.fromisoformat(value.replace('Z', '+00:00')).replace(tzinfo=dt.timezone.utc)


def main():
    feed, retrieval = read('catalog.json'), read('retrieval.json')
    as_of = parse(retrieval['retrieved_at'])
    records, excluded = [], []
    for entry in feed['dataset']:
        item_id = urllib.parse.parse_qs(urllib.parse.urlparse(entry['identifier']).query)['id'][0]
        item = read(f'item-{item_id}.json')
        if item.get('type') != 'Feature Service':
            excluded.append({'id': item_id, 'title': entry['title'],
                             'type': item.get('type', 'Inaccessible item'), 'url': entry['landingPage']})
            continue
        metadata_file = RAW / f'metadata-{item_id}.xml'
        try:
            xml = ET.parse(metadata_file).getroot()
            metadata_status = 'Parsed'
        except (ET.ParseError, FileNotFoundError):
            xml = ET.Element('metadata')
            metadata_status = 'Unavailable'
        pub = xml.findtext('./dataIdInfo/idCitation/date/pubDate')
        created = xml.findtext('./dataIdInfo/idCitation/date/createDate')
        frequency = xml.find('./dataIdInfo/resMaint/maintFreq/MaintFreqCd')
        code = frequency.get('value') if frequency is not None else None
        service_path = RAW / f'service-{item_id}.json'
        service = json.loads(service_path.read_text(encoding='utf-8')) if service_path.exists() else {}
        edits = service.get('editingInfo', {})
        data_edit = iso(edits.get('dataLastEditDate'))
        age = (as_of - parse(data_edit)).total_seconds() / 86400 if data_edit else None
        bucket = ('Unknown' if age is None else 'Future timestamp' if age < 0 else
                  'Within 30 days' if age <= 30 else '31–90 days' if age <= 90 else
                  '91–365 days' if age <= 365 else 'Over a year')
        records.append({
            'id': item_id, 'title': entry['title'], 'url': entry['landingPage'],
            'service_url': next((d.get('accessURL') for d in entry.get('distribution', [])
                                 if d.get('format') == 'ArcGIS GeoServices REST API'), item.get('url')),
            'publisher': entry.get('publisher', {}).get('name'), 'owner': item.get('owner'),
            'tags': entry.get('keyword', []), 'created': iso(item.get('created')),
            'issued': entry.get('issued'), 'formal_published': pub, 'formal_created': created,
            'published': pub or created or iso(item.get('created')),
            'published_source': 'Formal publication date' if pub else 'Formal creation date' if created else 'Item creation date',
            'item_modified': iso(item.get('modified')), 'feed_modified': entry.get('modified'),
            'data_last_edit': data_edit, 'service_last_edit': iso(edits.get('lastEditDate')),
            'schema_last_edit': iso(edits.get('schemaLastEditDate')),
            'frequency_code': code, 'frequency': FREQUENCIES.get(code, 'Not specified'),
            'age_days': round(age, 1) if age is not None else None, 'freshness': bucket,
            'metadata_status': metadata_status,
            'has_data_dictionary': 'data dictionary' in entry.get('description', '').lower(),
            'has_contact_email': '@' in entry.get('contactPoint', {}).get('hasEmail', ''),
            'date_disagrees': bool(pub and pub[:10] != entry.get('issued', '')[:10]),
        })
    records.sort(key=lambda r: (r['created'], r['title']))
    years = []
    cumulative = 0
    for year in range(min(int(r['created'][:4]) for r in records), as_of.year + 1):
        cohort = [r for r in records if r['created'].startswith(str(year))]
        cumulative += len(cohort)
        cutoff = f'{year}-{as_of:%m-%d}'
        years.append({'year': year, 'created': len(cohort), 'cumulative_survivors': cumulative,
                      'published': sum(r['published'].startswith(str(year)) for r in records),
                      'created_same_period': sum(r['created'][:10] <= cutoff for r in cohort),
                      'active_months': len({r['created'][:7] for r in cohort})})
    summary = {
        'as_of': retrieval['retrieved_at'], 'catalog_entries': len(feed['dataset']),
        'dataset_count': len(records), 'excluded_count': len(excluded),
        'excluded_types': dict(collections.Counter(r['type'] for r in excluded)),
        'years': years, 'frequencies': dict(collections.Counter(r['frequency'] for r in records)),
        'freshness': dict(collections.Counter(r['freshness'] for r in records)),
        'formal_publication_dates': sum(bool(r['formal_published']) for r in records),
        'date_disagreements': sum(r['date_disagrees'] for r in records),
        'data_dictionary_count': sum(r['has_data_dictionary'] for r in records),
        'contact_email_count': sum(r['has_contact_email'] for r in records),
        'service_timestamp_count': sum(bool(r['data_last_edit']) for r in records),
    }
    result = {'summary': summary, 'datasets': records, 'excluded': excluded}
    target = ROOT / 'data' / 'catalog-analysis.json'
    target.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    # Embedding a local data script also supports opening index.html directly from disk.
    (ROOT / 'data' / 'catalog-data.js').write_text('window.CATALOG = ' + json.dumps(result, ensure_ascii=False).replace('</', '<\\/') + ';\n', encoding='utf-8')
    with (ROOT / 'data' / 'datasets.csv').open('w', newline='', encoding='utf-8-sig') as output:
        writer = csv.DictWriter(output, fieldnames=list(records[0]))
        writer.writeheader()
        for record in records:
            writer.writerow({**record, 'tags': '; '.join(record['tags'])})
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
