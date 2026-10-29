"""Build the public parcel story from local snapshots; Python standard library only."""
import collections
import gzip
import hashlib
import json
import math
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'data'
SOURCES = [
    ('2017-08', 'Aug 2017', 'Parcel_Data_August_2017.geojson'),
    ('2018-04', 'Apr 2018', 'Parcel_Data_April_2018.geojson'),
    ('2018-07', 'Jul 2018', 'July_2018_Parcels.geojson'),
    ('2019-10', 'Oct 2019', 'Parcel_Map_-_October_2019.geojson'),
    ('2020-q1', 'Q1 2020', '_QPD_Q1_2020_-7626913837114685751.geojson'),
    ('2023-11', 'Nov 2023', 'QPD_2023_11_20_L1_ODP_AGO_-313696415589235697.geojson'),
    ('2024-q1', 'Q1 2024', 'Syracuse_Parcel_Map_(Q1_2024).geojson'),
    ('2024-08', 'Aug 2024', 'QPD_2024_08_20_L1_ODP_-7368007751611310153.geojson'),
    ('2024-q4', 'Q4 2024', 'Syracuse_Parcel_Map_(2024_Q4).geojson'),
    ('2025-05', 'May 2025', 'QPD_2025_05_05_L1_ODP_view_4809303906059927032.geojson'),
    ('2025-q3', 'Q3 2025', 'Syracuse_Parcel_Map_(2025_Q3)_view_8155445872837257469.geojson'),
    ('2026-01', 'Jan 2026', 'QPD_2026_01_26_L1_ODP_view_2179787715194331046.geojson'),
    ('2026-10', 'Oct 2026', 'QPD_2026-10-19_L1-ODP.geojson'),
]
ALIASES = {
    'use': ['LUCat_Old', 'LandUse'], 'value': ['total_av', 'AssessedVa'],
    'units': ['n_ResUnits', 'Units'], 'owner': ['Owner'],
    'year': ['yr_built', 'YearBuilt'], 'vacancy': ['IPSVacant', 'VacantBuil'],
    'neighborhood': ['NHOOD', 'Nhood', 'Neighborho'],
    'address': ['FullAddres', 'FullAdd', 'FullName'],
}
FIELDS = list(ALIASES)
# Zero-unit records contradict residential classifications in these exports.
BAD_UNITS = {'2017-08', '2018-04', '2018-07', '2019-10'}
RESIDENTIAL = {'SINGLE FAMILY', 'TWO FAMILY', 'THREE FAMILY', 'APARTMENT', 'MULTIPLE RESIDENCE'}
LEGAL_QUALIFIERS = {'TRUST', 'LLC', 'INC', 'CORP', 'CORPORATION', 'LTD', 'INCORPORATED', 'LLP', 'LP', 'CO', 'COMPANY'}


def fingerprint(value):
    return hashlib.sha1(value.encode()).hexdigest()[:16] if value else None


def owner_keys(tax_id, owner, aliases):
    """Keep literal matches, token matches, possible qualifier changes, and reviews separate."""
    name = clean(owner)
    tokens = sorted(re.findall(r'[A-Z0-9]+', name.replace("'", '')))
    core = [t for t in tokens if t not in LEGAL_QUALIFIERS]
    review = aliases.get(tax_id)
    confirmed = f"review:{tax_id}" if review and name in review['names'] else ''
    return [fingerprint(name), fingerprint(' '.join(tokens)),
            fingerprint(' '.join(core)) if len(core) >= 2 else None, fingerprint(confirmed)]


def building_vacant(value):
    # Blank does not mean occupied. Unexplained codes are not positive evidence.
    return clean(value) in {'Y', 'YES', 'RESIDENTIAL', 'COMMERCIAL'}


def persistent_vacancy(histories, snapshots, ids):
    land_dates = [i for i, s in enumerate(snapshots) if s['useComparable']]
    building_dates = [i for i, s in enumerate(snapshots) if s['sourceFields']['vacancy']]
    return {
        'land': {'snapshots': land_dates, 'indices': [i for i, key in enumerate(ids)
                 if land_dates and all(histories[key][s] and clean(histories[key][s][0]) == 'VACANT LAND' for s in land_dates)]},
        'building': {'snapshots': building_dates, 'indices': [i for i, key in enumerate(ids)
                     if building_dates and all(histories[key][s] and building_vacant(histories[key][s][5]) for s in building_dates)]}
    }


def reliable_units(use, value, comparable):
    units = number(value)
    if not comparable or (clean(use) in RESIDENTIAL and units == 0):
        return None
    return units


def clean(value):
    return re.sub(r'\s+', ' ', str(value).strip()).upper() if value is not None else ''


def number(value):
    try:
        result = float(value)
        return result if math.isfinite(result) and result >= 0 else None
    except (TypeError, ValueError):
        return None


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, separators=(',', ':'), ensure_ascii=False), encoding='utf-8')


def rings(geometry):
    if not geometry:
        return []
    polygons = [geometry['coordinates']] if geometry['type'] == 'Polygon' else geometry['coordinates']
    return [[[round((p[0] + 76.3) * 100000), round((43.15 - p[1]) * 137000)] for p in ring]
            for polygon in polygons for ring in polygon]


def deduplicate(features):
    grouped = collections.defaultdict(list)
    for feature in features:
        key = clean(feature['properties'].get('TAX_ID'))
        if key:
            grouped[key].append(feature)
    unique = {key: values[0] for key, values in grouped.items() if len(values) == 1}
    duplicates = {key: len(values) for key, values in grouped.items() if len(values) > 1}
    return unique, duplicates


def build():
    histories, catalog, geometries, packs = {}, {}, {}, []
    aliases = json.loads((ROOT / 'scripts' / 'owner_aliases.json').read_text(encoding='utf-8'))
    manifest = {'version': 2, 'fields': FIELDS, 'snapshots': [], 'duplicates': {}, 'ownerAliases': aliases,
                'snapshotFields': ['indexPosition', 'useCode', 'assessedValue', 'reliableUnits',
                                   'ownerLiteral', 'ownerTokens', 'ownerCoreTokens', 'ownerConfirmed'],
                'geometryNote': 'Latest available outline for each tax ID; not historical boundaries.'}
    for si, (sid, label, filename) in enumerate(SOURCES):
        print('Reading', label, flush=True)
        source_bytes = (ROOT / filename).read_bytes()
        raw = json.loads(source_bytes.decode('utf-8-sig'))
        source_path = OUT / 'sources' / f'{sid}.geojson.gz'
        source_path.parent.mkdir(parents=True, exist_ok=True)
        with source_path.open('wb') as compressed:
            with gzip.GzipFile(filename='', mode='wb', fileobj=compressed, mtime=0) as stream:
                stream.write(source_bytes)
        features, duplicates = deduplicate(raw['features'])
        keys = set().union(*(f['properties'].keys() for f in features.values()))
        source_fields = {field: next((k for k in aliases if k in keys), None) for field, aliases in ALIASES.items()}
        snapshot = {'id': sid, 'label': label, 'file': filename, 'rows': len(raw['features']),
                    'unique': len(features), 'sourceFields': source_fields,
                    'unitsComparable': sid not in BAD_UNITS and source_fields['units'] is not None,
                    'useComparable': source_fields['use'] is not None,
                    'sha256': hashlib.sha256(source_bytes).hexdigest(),
                    'download': f'data/sources/{sid}.geojson.gz'}
        manifest['snapshots'].append(snapshot)
        manifest['duplicates'][sid] = duplicates
        pack = {}
        for key, feature in features.items():
            p = feature['properties']
            values = [p.get(source_fields[f]) if source_fields[f] else None for f in FIELDS]
            histories.setdefault(key, [None] * len(SOURCES))[si] = values
            use, value, units, owner, year, vacancy, hood, address = values
            record = catalog.setdefault(key, {'id': key})
            record.update(address=clean(address) or record.get('address', key),
                          hood={'HAWLEY GREEN': 'HAWLEY-GREEN', 'PARK AVE': 'PARK AVE.'}.get(clean(hood), clean(hood)) if source_fields['neighborhood'] else record.get('hood', ''), last=si,
                          block=clean(p.get('Sec_Block')) or key[:16],
                          street=clean(p.get('StName')) or record.get('street', ''),
                          num=clean(p.get('StNum')) or record.get('num', ''))
            geom = rings(feature.get('geometry'))
            if geom:
                geometries[key] = geom
                points = [point for ring in geom for point in ring]
                record['xy'] = [round(sum(p[i] for p in points) / len(points)) for i in (0, 1)]
            pack[key] = [clean(use) or None, number(value),
                         reliable_units(use, units, snapshot['unitsComparable']),
                         *owner_keys(key, owner, aliases)]
        packs.append(pack)
        del raw, features, source_bytes

    ids = sorted(catalog)
    index = {key: i for i, key in enumerate(ids)}
    hoods = sorted({r['hood'] for r in catalog.values()} - {''}) + ['UNASSIGNED']
    uses = sorted({p[0] for pack in packs for p in pack.values() if p[0]})
    manifest.update(neighborhoods=hoods, uses=uses, parcelCount=len(ids),
                    indexFields=['id', 'address', 'neighborhood', 'x', 'y', 'taxBlock', 'streetGroup', 'lastSnapshot'])
    rows = []
    geometry_shards = collections.defaultdict(dict)
    history_shards = collections.defaultdict(dict)
    summaries = {h: {'total': 0, 'matched': 0, 'comparable': 0, 'same': 0, 'uses': {}, 'ages': [0]*5} for h in hoods}
    transitions = collections.Counter()
    blocks = {}
    for key in ids:
        r = catalog[key]
        hood = r['hood'] or 'UNASSIGNED'
        n = re.match(r'\d+', r['num'])
        street_group = f"{int(n[0]) // 100 * 100} {r['street']}" if n and r['street'] else ''
        rows.append([key, r['address'], hoods.index(hood), *r.get('xy', [0, 0]), r['block'], street_group, r['last']])
        shard = key[6:9]
        geometry_shards[shard][key] = geometries.get(key, [])
        history_shards[shard][key] = histories[key]
        if key not in packs[-1]:
            continue
        summary = summaries[hood]
        summary['total'] += 1
        use = packs[-1][key][0] or 'UNKNOWN'
        summary['uses'][use] = summary['uses'].get(use, 0) + 1
        year = number(histories[key][-1][4])
        age_bin = 4 if not year else 0 if year < 1900 else 1 if year < 1940 else 2 if year < 1980 else 3
        summary['ages'][age_bin] += 1
        block = blocks.setdefault(r['block'], {'total': 0, 'uses': {}, 'ages': [0]*5, 'hood': hoods.index(hood)})
        block['total'] += 1
        block['uses'][use] = block['uses'].get(use, 0) + 1
        block['ages'][age_bin] += 1
        if key in packs[0]:
            summary['matched'] += 1
            before, after = packs[0][key][0], packs[-1][key][0]
            if before and after:
                summary['comparable'] += 1
                summary['same'] += before == after
                transitions[(before, after)] += 1

    write(OUT / 'index.json', rows)
    write(OUT / 'blocks.json', blocks)
    for (sid, _, _), pack in zip(SOURCES, packs):
        # Field order is documented by manifest.snapshotFields.
        write(OUT / 'snapshots' / f'{sid}.json', [[index[k], uses.index(v[0]) if v[0] else -1, *v[1:]] for k, v in sorted(pack.items())])
    for shard, values in history_shards.items():
        write(OUT / 'histories' / f'{shard}.json', values)
        write(OUT / 'geometry' / f'{shard}.json', geometry_shards[shard])
    manifest['summary'] = summaries
    manifest['transitions'] = [[a, b, count] for (a, b), count in sorted(transitions.items())]
    manifest['endpoint'] = {'matched': len(packs[0].keys() & packs[-1].keys()),
                            'oldOnly': len(packs[0].keys() - packs[-1].keys()),
                            'newOnly': len(packs[-1].keys() - packs[0].keys())}
    manifest['featured'] = ['31150011700000010010050000', '31150009800200010050030000', '31150004300000010030000000']
    manifest['persistentVacancy'] = persistent_vacancy(histories, manifest['snapshots'], ids)
    write(OUT / 'manifest.json', manifest)
    # A small, offline vector illustration made from actual parcel centroids.
    latest = [catalog[k] for k in packs[-1] if 'xy' in catalog[k]]
    xs, ys = zip(*(r['xy'] for r in latest))
    bounds = [min(xs)-100, min(ys)-100, max(xs)-min(xs)+200, max(ys)-min(ys)+200]
    cells = {}
    for r in latest:
        xy = tuple(round(v / 30) * 30 for v in r['xy'])
        key = r['id']
        changed = key in packs[0] and packs[0][key][0] and packs[-1][key][0] and packs[0][key][0] != packs[-1][key][0]
        cells[xy] = cells.get(xy, False) or bool(changed)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{" ".join(map(str,bounds))}"><title>Syracuse parcel pattern, 2017 to 2026</title>']
    for color, changed in [('#6f8d88', False), ('#f4ae77', True)]:
        path = ''.join(f'M{x},{y}h22v22h-22z' for (x,y), c in cells.items() if c == changed)
        svg.append(f'<path fill="{color}" d="{path}"/>')
    svg.append('</svg>')
    (OUT / 'city.svg').write_text(''.join(svg), encoding='utf-8')
    print(f'Built {len(ids):,} parcel histories, {len(hoods)} neighborhood groups; {len(cells):,} illustration cells.', flush=True)


if __name__ == '__main__':
    build()
