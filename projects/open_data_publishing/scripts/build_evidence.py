"""Build the story's independently inspectable evidence from saved public responses."""
import base64
import collections
import csv
import datetime as dt
import html
import json
from pathlib import Path
import re
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
RESEARCH = DATA / 'research'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def normalize(url):
    return urllib.parse.unquote(url or '').lower().split('/featureserver')[0].rstrip('/') + '/featureserver'


def clean(text):
    return re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', ' ', text or ''))).strip()


def family(title):
    title = title.lower()
    patterns = [('Assessment final rolls', 'assessment final roll'), ('Assessment tentative rolls', 'assessment tentative'),
                ('Parcel maps', 'parcel map'), ('Pavement ratings', 'pavement rating|road rating'),
                ('Crime — Part 1', r'part 1|part i '), ('Crime — Part 2', 'part 2'),
                ('Permits', 'permit'), ('Cityline', 'cityline'), ('Water main breaks', 'water main break'),
                ('Fire incidents', 'fire incident'), ('Budgets and spending', 'budget|spending|expenses'),
                ('Education', 'kindergarten|ela proficiency')]
    return next((label for label, pattern in patterns if re.search(pattern, title)), 'Other datasets')


def csv_write(name, rows):
    with (DATA / name).open('w', encoding='utf-8-sig', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(value, ensure_ascii=False) if isinstance(value, (list, dict)) else value for key, value in row.items()})


def main():
    catalog = read(DATA / 'catalog-analysis.json')
    datasets = catalog['datasets']
    by_id = {r['id']: r for r in datasets}
    by_root = {normalize(r['service_url']): r['id'] for r in datasets}
    schemas = []
    for row in datasets:
        service = read(DATA / 'raw' / f"service-{row['id']}.json")
        fields = [{key: field.get(key) for key in ['name', 'alias', 'type', 'length', 'nullable', 'domain']} for field in service.get('fields', [])]
        schemas.append({'id': row['id'], 'title': row['title'], 'family': family(row['title']), 'url': row['url'],
                        'service_url': row['service_url'], 'created': row['created'], 'geometry': service.get('geometryType'),
                        'fields': fields, 'field_count': len(fields)})
    directory = []
    for index, service in enumerate(read(RESEARCH / 'service-directory.json')['data']['services']):
        evidence = read(RESEARCH / f'directory-service-{index:03}.json')
        body = evidence.get('data', {})
        matched = by_root.get(normalize(service['url']))
        directory.append({'name': service['name'], 'url': service['url'], 'catalog_id': matched,
                          'catalog_title': by_id[matched]['title'] if matched else None,
                          'status': 'Metadata available' if body and not body.get('error') else 'Metadata unavailable',
                          'item_id': body.get('serviceItemId'),
                          'layer_count': len(body.get('layers', [])), 'table_count': len(body.get('tables', [])),
                          'layers': [x['name'] for x in body.get('layers', []) + body.get('tables', [])],
                          'capabilities': body.get('capabilities'), 'checked_at': evidence['checked_at']})
    candidates = read(RESEARCH / 'historic-candidates.json')
    history = []
    for item_id, archive in candidates.items():
        current = read(RESEARCH / f'historic-item-{item_id}.json')
        item = current.get('data', {})
        capture = read(RESEARCH / f'capture-{item_id}.json')
        match = re.search(r'<title[^>]*>(.*?)</title>', capture.get('text', ''), re.I | re.S)
        title = clean(match[1]) if match else ''
        if title in ['City of Syracuse', 'Open Data Syracuse']:
            title = ''
        title = title or item.get('title') or 'Title not recovered'
        error = item.get('error', {})
        service_matches = [s['url'] for s in directory if s['item_id'] == item_id and s['status'] == 'Metadata available']
        status = 'Public item, absent from feed' if item.get('id') else 'Permission denied' if error.get('code') == 403 else 'Missing or inaccessible' if error.get('code') == 400 else 'Check inconclusive'
        history.append({'id': item_id, 'title': title, 'capture_date': f"{archive['capture'][:4]}-{archive['capture'][4:6]}-{archive['capture'][6:8]}",
                        'original_url': archive['original'], 'archive_url': f"https://web.archive.org/web/{archive['capture']}/{archive['original']}",
                        'current_url': f'https://www.arcgis.com/sharing/rest/content/items/{item_id}?f=pjson',
                        'status': status, 'api_message': error.get('message', ''), 'current_type': item.get('type'),
                        'service_matches': service_matches, 'checked_at': current['checked_at']})
    history.sort(key=lambda r: (r['title'], r['id']))
    comparisons = [
        {'key': 'permits', 'title': 'Permits: fewer fields, different questions', 'old': 'a28cd0366cb64040a41112b5c6df508c', 'new': 'cf857fb2f72a448c8ef712cc667768c4', 'meaning': 'The older file includes project valuation, payment, application date and permit status. The newer schema has no equivalent named fields for those concepts. It adds owner and description of work. Application date and issue date describe different events.', 'caution': 'Different time ranges and workflows; this is a comparison of two editions available now, not proof that columns were deleted from one unchanged item. The old page explicitly links to the newer dataset.'},
        {'key': 'parcel-dip', 'title': 'Parcels: a thinner Q3 2024 edition', 'old': '1f2ff0241886433ab5b0bfe706d0bea9', 'new': 'd68de5fb5df14a86829980a195ff7a6c', 'meaning': 'The Q3 edition lacks fields such as Owner, total_av and land_av found in Q1. A reader cannot perform the same ownership and valuation analysis using that edition alone.', 'caution': 'The Q4 2024 edition returns to 69 total fields, including ownership and valuation. This is an uneven series, not a permanent loss of all parcel detail.'},
        {'key': 'parcel-recovery', 'title': 'Parcels: ownership and values return', 'old': 'd68de5fb5df14a86829980a195ff7a6c', 'new': 'addb85afc6a14daca340c4ae0077e998', 'meaning': 'The following quarterly edition restores ownership, assessed values, building characteristics and additional geography fields.', 'caution': 'Field presence does not establish that every row has a value. No claim about completeness is made from schema counts alone.'},
        {'key': 'parcel-latest', 'title': 'Parcels: a smaller change in the latest edition', 'old': 'b291716dbe4e4236adcd4532dd4547fa', 'new': 'ffe3f6b2d01448eba3b1b0426055be51', 'meaning': 'The three omitted columns are OBJECTID_1, LATITUDE and LONGITUDE. Polygon geometry is still available, so the missing coordinate columns do not mean that location data disappeared.', 'caution': 'Counts include identifier and geometry-derived columns. Fewer columns can reflect simplification, not a substantive loss of information.'},
        {'key': 'parcel-tax', 'title': 'Parcels: more columns does not guarantee the same detail', 'old': '121ac55c48f54c3db1c0160e1adf4b9c', 'new': 'ffe3f6b2d01448eba3b1b0426055be51', 'meaning': 'The 2017 schema includes TotTaxOwed, TaxYrsDeli and OverdueWat. Those fields have no direct named counterparts in the latest parcel schema, despite the higher overall field count.', 'caution': 'These concepts may be available through other city sources. This finding is limited to the compared portal schemas; it is not a citywide claim that tax or water-balance information is unavailable.'},
        {'key': 'crime-detail', 'title': 'Crime: more explicit columns in later editions', 'old': '00ea3cbd266f46d5aa013cf3c61bf2f9', 'new': '348b60d86ca84a0aab346725db7b08d9', 'meaning': 'The 2024 Part 1 edition adds explicit LAT, LONG and LarcenyCode columns compared with the archived 2018 edition. DATEEND is a typed date in 2024, compared with a string in the 2018 schema.', 'caution': 'Both layers have spatial geometry. Additional coordinate columns improve tabular convenience; they do not establish more precise locations. Crime locations are intentionally generalized.'},
    ]
    schema_by_id = {s['id']: s for s in schemas}
    for comparison in comparisons:
        old, new = schema_by_id[comparison['old']], schema_by_id[comparison['new']]
        before = {f['name'].lower(): f for f in old['fields']}
        after = {f['name'].lower(): f for f in new['fields']}
        comparison.update(old_count=len(before), new_count=len(after),
                          old_only=[f['name'] for k, f in before.items() if k not in after],
                          new_only=[f['name'] for k, f in after.items() if k not in before],
                          common_count=len(before.keys() & after.keys()))
    schema_rows = []
    for schema in schemas:
        for field in schema['fields']:
            schema_rows.append({'dataset_id': schema['id'], 'dataset': schema['title'], 'family': schema['family'],
                                'field': field['name'], 'alias': field['alias'], 'type': field['type'], 'source': schema['service_url']})
    series = []
    for name in ['Assessment final rolls', 'Assessment tentative rolls', 'Pavement ratings', 'Crime — Part 1', 'Crime — Part 2', 'Water main breaks', 'Fire incidents', 'Parcel maps']:
        members = [s for s in schemas if s['family'] == name]
        ranges = {}
        for member in members:
            match = re.search(r'\b(20\d{2})\s*(?:-|–|to)\s*(20\d{2})\b', member['title'], re.I)
            if match and int(match[1]) < int(match[2]):
                ranges[member['id']] = [int(match[1]), int(match[2])]
        series.append({'name': name, 'ranges': ranges, 'years': {str(year): [s['id'] for s in members if re.search(rf'\b{year}\b', s['title']) or s['id'] in ranges and ranges[s['id']][0] <= year <= ranges[s['id']][1]] for year in range(2017, 2027)}})
    statuses = dict(collections.Counter(r['status'] for r in history))
    linked_count = sum(bool(s['catalog_id']) for s in directory)
    notices = []
    for row in read(DATA / 'raw/catalog.json')['dataset']:
        text = clean(row['description'])
        if 'not currently updating correctly' in text:
            notices.append({'title': row['title'], 'url': row['landingPage'], 'notice': text[:text.find('Data Dictionary') if 'Data Dictionary' in text else 600]})
    result = {'summary': {'as_of': catalog['summary']['as_of'], 'directory_services': len(directory),
                          'directory_linked': linked_count, 'directory_not_linked': len(directory) - linked_count,
                          'directory_metadata_available': sum(s['status'] == 'Metadata available' for s in directory),
                          'historical_ids': len(history), 'historical_statuses': statuses,
                          'historical_titles_recovered': sum(h['title'] != 'Title not recovered' for h in history),
                          'assessment_backfills_2023': sum(s['family'] == 'Assessment final rolls' and s['created'].startswith('2023') and '(2023)' not in s['title'] for s in schemas)},
              'schemas': schemas, 'comparisons': comparisons, 'directory': directory, 'history': history,
              'series': series, 'notices': notices}
    (DATA / 'evidence.json').write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    (DATA / 'evidence-data.js').write_text('window.EVIDENCE = ' + json.dumps(result, ensure_ascii=False).replace('</', '<\\/') + ';\n', encoding='utf-8')
    csv_write('service-directory.csv', directory)
    csv_write('historical-items.csv', history)
    csv_write('schema-fields.csv', schema_rows)
    print(json.dumps(result['summary'], indent=2))


if __name__ == '__main__':
    main()
