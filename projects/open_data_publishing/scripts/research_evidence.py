"""Read-only evidence collection for the publishing story. No individual records saved."""
import concurrent.futures
import datetime as dt
import json
import re
import sys
from pathlib import Path
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data' / 'research'
OUT.mkdir(parents=True, exist_ok=True)


def retrieve(name, url):
    parts = urllib.parse.urlsplit(url)
    url = urllib.parse.urlunsplit((parts.scheme, parts.netloc, urllib.parse.quote(parts.path, safe='/%:@()'), parts.query, parts.fragment))
    result = {'url': url, 'checked_at': dt.datetime.now(dt.timezone.utc).isoformat()}
    try:
        request = urllib.request.Request(url, headers={'User-Agent': 'DataCuse-public-metadata-research/1.0'})
        with urllib.request.urlopen(request, timeout=40) as response:
            result.update(status=response.status, final_url=response.url)
            body = response.read().decode('utf-8')
            try:
                result['data'] = json.loads(body)
            except json.JSONDecodeError:
                result['text'] = body
    except Exception as exc:
        result['error'] = str(exc)
    (OUT / f'{name}.json').write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps({'name': name, 'status': result.get('status'), 'error': result.get('error'),
                      'bytes': len(json.dumps(result))}))
    return result


def main():
    datasets = json.loads((ROOT / 'data/catalog-analysis.json').read_text(encoding='utf-8'))['datasets']
    catalog = json.loads((ROOT / 'data/raw/catalog.json').read_text(encoding='utf-8'))['dataset']
    if '--chatbot' in sys.argv:
        tree = json.loads((OUT / 'source-chatbot-tree.json').read_text(encoding='utf-8'))['data']['tree']
        for entry in tree:
            retrieve('chatbot-' + ('schema' if entry['path'].endswith('.yaml') else 'instructions'), entry['url'])
        return
    if '--followups' in sys.argv:
        jobs = [('source-chatbot-tree', 'https://api.github.com/repos/CityofSyracuse/code-violations-chatbot/git/trees/main?recursive=1')]
        for file in OUT.glob('directory-service-*.json'):
            prior = json.loads(file.read_text(encoding='utf-8'))
            if prior.get('error'):
                jobs.append((file.stem, prior['url']))
        services = json.loads((OUT / 'service-directory.json').read_text(encoding='utf-8'))['data']['services']
        for service in services:
            if service['name'] in ['2022_Fire_data_csv', '2023_Fire_Data_csv', '2024_Fire_Data_csv', '2021_Road_Rating', 'Potholes_filled_2018', 'Certificate_of_Compliance_(Housing)']:
                root = service['url']
                jobs.extend([('extra-layer-' + service['name'], root + '/0?f=json'), ('extra-count-' + service['name'], root + '/0/query?where=1%3D1&returnCountOnly=true&f=json')])
        # Only date strings are requested; no addresses or complaint descriptions.
        row = next(r for r in datasets if r['id'] == '6c1981e96f1940a99b201482c3b7b6a9')
        jobs.append(('cityline-date-format', row['service_url'] + '/query?' + urllib.parse.urlencode({'f':'json','where':'1=1','outFields':'Created_at_local','returnGeometry':'false','resultRecordCount':3})))
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(lambda job: retrieve(*job), jobs))
        return
    if '--remaining-captures' in sys.argv:
        for file in sorted(OUT.glob('capture-*.json')):
            prior = json.loads(file.read_text(encoding='utf-8'))
            if prior.get('error'):
                retrieve(file.stem, prior['url'])
        return
    if '--directory' in sys.argv:
        services = json.loads((OUT / 'service-directory.json').read_text(encoding='utf-8'))['data']['services']
        jobs = [(f'directory-service-{index:03}', service['url'] + '?f=json') for index, service in enumerate(services)]
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
            list(pool.map(lambda job: retrieve(*job), jobs))
        return
    if '--sources' in sys.argv:
        jobs = [
            ('source-auditor', 'https://www.syr.gov/Departments/Auditor-Office'),
            ('source-crb', 'https://www.syr.gov/Departments/Citizen-Review-Board-CRB/CRB-Reports'),
            ('source-budget', 'https://www.syr.gov/Departments/Budget/City-Budget'),
            ('source-water', 'https://www.syr.gov/Departments/Water/Water-Data-and-Reports'),
            ('source-police', 'https://www.syr.gov/Departments/Police/Public-Information/Annual-Reports'),
            ('source-sida', 'https://www.syr.gov/Boards-and-Commissions/Municipal-Boards/SIDA/SIDA-Financials-Annual-Reports'),
            ('source-budget-archives', 'https://www.syr.gov/Departments/Budget/Budget-Archives'),
            ('source-city-chatbot', 'https://api.github.com/repos/CityofSyracuse/code-violations-chatbot/readme'),
        ]
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(lambda job: retrieve(*job), jobs))
        return
    if '--retry-captures' in sys.argv:
        # Retry a small, relevant subset serially after a burst of archive connection failures.
        names = ['capture-slug-lead-violations', 'capture-slug-fire-incidents',
                 'capture-slug-potholes-filled-2018', 'capture-4130b44de91247fd883df15bfc0e97b1',
                 'capture-3f68d80ac391452fbbc1d5086f8fd9bb', 'capture-41c27a73cf144cb9831ced2b54920842']
        for name in names:
            prior = json.loads((OUT / f'{name}.json').read_text(encoding='utf-8'))
            retrieve(name, prior['url'])
        return
    if '--captures' in sys.argv:
        historic = json.loads((OUT / 'historic-candidates.json').read_text(encoding='utf-8'))
        jobs = [(f'capture-{item_id}', f"https://web.archive.org/web/{row['capture']}id_/{row['original']}") for item_id, row in historic.items()]
        archive = json.loads((OUT / 'archive-old-pages.json').read_text(encoding='utf-8'))['data'][1:]
        for stamp, url, mimetype in archive:
            for slug in ['lead-violations/data', 'fire-incidents/data', 'potholes-filled-2018', 'innovation-team-priority-area-voting']:
                if url.endswith('/' + slug):
                    jobs.append(('capture-slug-' + slug.split('/')[0], f'https://web.archive.org/web/{stamp}id_/{url}'))
        repos = json.loads((OUT / 'city-repos.json').read_text(encoding='utf-8'))['data']
        for repo in repos:
            names = ['index.html', 'README.md'] if repo['name'] == 'Open-Data-Library' else ['buildingpermitsdictionary.csv', 'LeadViolations_DataDictionary.csv', 'ParcelData_DataDictionary.csv', 'CityLineData_DataDictionary.csv'] if repo['name'] == 'OpenDataDictionaries' else []
            for name in names:
                jobs.append(('github-' + repo['name'] + '-' + name.replace('.', '-'), f"https://raw.githubusercontent.com/CityofSyracuse/{repo['name']}/{repo['default_branch']}/{name}"))
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            list(pool.map(lambda job: retrieve(*job), jobs))
        return
    if '--history' in sys.argv:
        archive = json.loads((OUT / 'archive-old-pages.json').read_text(encoding='utf-8'))['data'][1:]
        current_ids = {urllib.parse.parse_qs(urllib.parse.urlparse(d['identifier']).query)['id'][0] for d in catalog}
        historic = {}
        for stamp, url, mimetype in archive:
            match = re.search(r'/datasets/([a-f0-9]{32})', url)
            if match and match[1] not in current_ids:
                historic.setdefault(match[1], {'capture': stamp, 'original': url})
        (OUT / 'historic-candidates.json').write_text(json.dumps(historic, indent=2), encoding='utf-8')
        jobs = [(f'historic-item-{item_id}', f'https://www.arcgis.com/sharing/rest/content/items/{item_id}?f=json') for item_id in historic]
        repos = json.loads((OUT / 'city-repos.json').read_text(encoding='utf-8'))['data']
        for repo in repos:
            if repo['name'] in ['jkan', 'OpenDataDictionaries', 'Open-Data-Library']:
                jobs.append(('repo-tree-' + repo['name'], f"https://api.github.com/repos/CityofSyracuse/{repo['name']}/git/trees/{repo['default_branch']}?recursive=1"))
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
            list(pool.map(lambda job: retrieve(*job), jobs))
        return
    jobs = [
        ('service-directory', 'https://services6.arcgis.com/bdPqSfflsdgFRVVM/arcgis/rest/services?f=json'),
        ('city-repos', 'https://api.github.com/orgs/CityofSyracuse/repos?per_page=100'),
        ('archive-old-json', 'https://web.archive.org/cdx/search/cdx?' + urllib.parse.urlencode({'url': 'data.syrgov.net/*', 'output': 'json', 'filter': 'mimetype:application/json', 'collapse': 'urlkey', 'fl': 'timestamp,original,statuscode', 'limit': 3000})),
        ('archive-old-pages', 'https://web.archive.org/cdx/search/cdx?' + urllib.parse.urlencode({'url': 'data.syrgov.net/datasets/*', 'output': 'json', 'filter': 'statuscode:200', 'collapse': 'urlkey', 'fl': 'timestamp,original,mimetype', 'limit': 3000})),
        ('inaccessible-complaints', 'https://www.arcgis.com/sharing/rest/content/items/17246235b723443f8ecf69a65838f26b?f=json'),
        ('old-lead-link', 'https://data.syrgov.net/datasets/lead-violations'),
    ]
    for owner in ['admin_syr']:
        jobs.append(('item-search-' + owner, 'https://www.arcgis.com/sharing/rest/search?' + urllib.parse.urlencode({'q': f'owner:{owner} AND (lead OR permit OR cityline OR crime OR water)', 'num': 100, 'f': 'json'})))
    for entry in catalog:
        if entry['title'] in ['Project Archive', 'SYRCityline 2021-Present', 'Public Safety']:
            item_id = urllib.parse.parse_qs(urllib.parse.urlparse(entry['identifier']).query)['id'][0]
            jobs.append(('page-' + item_id, f'https://www.arcgis.com/sharing/rest/content/items/{item_id}/data?f=json'))
    for row in datasets:
        if row['title'] not in ['Permit Requests', 'Building Permits (2013-2019)', 'SYRCityline Requests (2021-January 2025)', 'Water Main Breaks (2022)', 'Crime Data 2025 Part 1 Offenses With Lat and Long Info']:
            continue
        service = json.loads((ROOT / 'data/raw' / f"service-{row['id']}.json").read_text(encoding='utf-8'))
        fields = [f for f in service.get('fields', []) if f['type'] == 'esriFieldTypeDate']
        stats = [{'statisticType': 'count', 'onStatisticField': service['objectIdField'], 'outStatisticFieldName': 'record_count'}]
        for index, field in enumerate(fields):
            for operation in ['min', 'max']:
                stats.append({'statisticType': operation, 'onStatisticField': field['name'], 'outStatisticFieldName': f'{operation}_date_{index}'})
        jobs.append(('coverage-' + row['id'], row['service_url'] + '/query?' + urllib.parse.urlencode({'f': 'json', 'where': '1=1', 'outStatistics': json.dumps(stats), 'returnGeometry': 'false'})))
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        list(pool.map(lambda job: retrieve(*job), jobs))


if __name__ == '__main__':
    main()
