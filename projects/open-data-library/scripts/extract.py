"""Reproducible, source-preserving extracts. Unknown source hashes stop publication."""
import argparse
import csv
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
MONTHS = 'January February March April May June July August September October November December'.split()

def sha(data):
    return hashlib.sha256(data).hexdigest()

def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

def sheets(path):
    """Read OOXML cached values without running formulas or modifying the workbook."""
    with zipfile.ZipFile(path) as z:
        strings = [''.join(t.itertext()) for t in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', NS)]
        rels = {r.get('Id'): r.get('Target') for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        styles = ET.fromstring(z.read('xl/styles.xml'))
        formats = {n.get('numFmtId'): n.get('formatCode') for n in styles.findall('m:numFmts/m:numFmt', NS)}
        xfs = [formats.get(n.get('numFmtId'), 'Excel built-in format ' + n.get('numFmtId')) for n in styles.findall('m:cellXfs/m:xf', NS)]
        for sheet in ET.fromstring(z.read('xl/workbook.xml')).findall('m:sheets/m:sheet', NS):
            target = rels[sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
            target = target.lstrip('/') if target.startswith('/') else 'xl/' + target
            rows = []
            for row in ET.fromstring(z.read(target)).findall('m:sheetData/m:row', NS):
                cells = {}
                for c in row:
                    v = c.findtext('m:v', default='', namespaces=NS)
                    if c.get('t') == 's' and v:
                        v = strings[int(v)]
                    elif c.get('t') == 'inlineStr':
                        v = ''.join(c.find('m:is', NS).itertext())
                    cells[re.sub(r'\d+', '', c.get('r'))] = {'cell': c.get('r'), 'value': v, 'formula': c.findtext('m:f', default='', namespaces=NS), 'number_format': xfs[int(c.get('s', '0'))], 'type': c.get('t', 'n')}
                rows.append((int(row.get('r')), cells))
            yield sheet.get('name'), rows

def save_table(output, source, key, title, rows, topic, coverage, limitations, provenance, family, years, description):
    assert rows, key
    headers = list(rows[0])
    assert len(headers) == len(set(headers)) and all(h for h in headers)
    target = output / 'downloads' / (key + '.csv')
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    with target.open(encoding='utf-8', newline='') as f:
        restored = list(csv.DictReader(f))
    assert restored == [{k: str(v) for k, v in r.items()} for r in rows], key + ': CSV round trip mismatch'
    def dtype(name):
        vals = [str(r[name]) for r in rows if str(r[name]) not in ('', 'NA')]
        return 'integer' if vals and all(re.fullmatch(r'-?\d+', v) for v in vals) else 'number' if vals and all(re.fullmatch(r'-?\d+(\.\d+)?', v) for v in vals) else 'string'
    return {'id': key, 'title': title, 'description': description, 'topic': topic, 'family': family, 'source_url': source['download'], 'source_page': source['source_page'], 'format': 'CSV', 'membership': 'document-source-no-match', 'match_method': 'Source file URL compared with official catalog. Related topics can exist in other datasets.', 'availability': 'available', 'curated': True, 'checked_at': source['checked_at'], 'coverage': coverage, 'years': years, 'fields': [{'name': h, 'alias': h.replace('_', ' '), 'type': dtype(h), 'nullable': True} for h in headers], 'record_count': len(rows), 'source_sha256': source['sha256'], 'download_sha256': sha(target.read_bytes()), 'download': 'downloads/' + target.name, 'original': 'sources/' + source['local_file'], 'limitations': limitations, 'provenance': provenance, 'validation': {'csv_round_trip': True, 'source_sha256_verified': True, 'row_count': len(rows), 'column_count': len(headers)}}

def budget(output, source):
    path = output / 'sources' / source['local_file']
    year = source['local_file'][:4]
    results = []
    all_sheets = dict(sheets(path))
    notes = '\n'.join(c['value'] for _, cells in all_sheets['Instructions & Notes'] for c in cells.values() if c['value'])
    (output / 'sources' / (year + '-budget-notes.txt')).write_text(notes, encoding='utf-8')
    for name, sheet in all_sheets.items():
        if name in ('Instructions & Notes', 'City Rates'):
            continue
        header = sheet[0][1]
        periods = {col: c['value'] for col, c in header.items() if re.search(r'FY\d{2}', c['value'])}
        assert len(periods) == 8, (name, periods)
        rows, context = [], {}
        for number, cells in sheet[1:]:
            labels = {col: c['value'] for col, c in cells.items() if col not in periods and c['value'] and c['type'] in ('s', 'inlineStr')}
            if not labels:
                continue
            left = min(labels)
            context = {k: v for k, v in context.items() if k < left}
            context.update(labels)
            for col, period in periods.items():
                cell = cells.get(col, {'cell': col + str(number), 'value': '', 'formula': '', 'number_format': '', 'type': 'n'})
                # Include missing values explicitly. Never turn a blank into zero.
                value = cell['value']
                if value and cell['type'] not in ('n',):
                    # A repeated heading or note, rather than a numeric observation.
                    continue
                if value:
                    Decimal(value)
                fy = re.search(r'FY(\d{2})\s+(.+)', period)
                rows.append({'sheet': name, 'source_row': number, 'source_cell': cell['cell'], 'label': ' | '.join(labels.values()), 'label_column': left, 'section_path': ' > '.join(context.values()), 'period_label': period.replace('\n', ' '), 'fiscal_year': '20' + fy[1], 'value_type': fy[2], 'value': value, 'source_formula': cell['formula'], 'source_number_format': cell['number_format']})
        key = f'budget-{year}-' + re.sub('[^a-z0-9]+', '-', name.lower()).strip('-')
        provenance = {'workbook': source['local_file'], 'sheet': name, 'version_note': notes.split('\nCity of Syracuse')[0], 'notes': 'sources/' + year + '-budget-notes.txt', 'method': 'OOXML cached numeric values, one source cell per row; no formulas recalculated; blank values retained.', 'excluded_sheets': ['Instructions & Notes (preserved as text)', 'City Rates (different units; original only)']}
        record = save_table(output, source, key, name + ' · ' + year + ' budget workbook', rows, 'City finances', min(r['fiscal_year'] for r in rows) + '–' + max(r['fiscal_year'] for r in rows) + ' fiscal years; mixed actual/budget/estimate/proposed', ['DataCuse extraction. Values and source rounding are preserved.', 'Includes totals, subtotals and detail. Do not sum all rows.', 'Actual, Budget, Estimate and Proposed are distinct measures; editions overlap.', 'Read source number formats and row labels for units; not every financial cell is additive.', 'Blank means no cached source value. Source formulas are text, not recalculated.', 'Auditor notes that source figures can differ due to rounding and mathematical errors.'], provenance, 'Budget workbooks', sorted({r['fiscal_year'] for r in rows}), 'Searchable values from the Auditor’s workbook, with fiscal-year labels, row context, and exact source cells.')
        # Independently confirm copied cells against the XML inventory, including cached totals.
        lookup = {c['cell']: c['value'] for _, cells in sheet for c in cells.values()}
        assert all(str(r['value']) == lookup.get(r['source_cell'], '') for r in rows)
        record['validation']['source_cells_checked'] = len(rows)
        record['validation']['cached_formula_values_preserved'] = sum(bool(r['source_formula']) for r in rows)
        results.append(record)
    return results

def crb(output, source):
    results = []
    with zipfile.ZipFile(output / 'sources' / source['local_file']) as z:
        inventory = [{'member': n, 'bytes': z.getinfo(n).file_size, 'sha256': sha(z.read(n))} for n in z.namelist()]
        dump(output / 'sources/crb-archive-inventory.json', inventory)
        main_name = 'Spreadsheets/Right_to_Know_Data_Joined_Cleaned.csv'
        main = list(csv.DictReader(io.StringIO(z.read(main_name).decode('utf-8-sig'))))
        years = sorted({r['annual'] for r in main if r['annual'] != 'NA'})
        quarters = sorted({r['rtk_quarter'] for r in main})
        for member in z.namelist():
            if not member.endswith('.csv'):
                continue
            reader = csv.DictReader(io.StringIO(z.read(member).decode('utf-8-sig')))
            rows = [{('source_row_index' if k == '' else k): v for k, v in r.items()} for r in reader]
            key = 'crb-' + Path(member).stem.lower().replace('_', '-')
            label = Path(member).stem.replace('rtk_', '').replace('_', ' ')
            record = save_table(output, source, key, 'Right to Know · ' + label, rows, 'Public safety', quarters[0] + '–' + quarters[-1] + ' in joined file; summary subsets vary', ['City-authored CSV extracted from ZIP. Only the unnamed index header was renamed source_row_index.', 'NA is preserved as the source missing-value marker; it does not mean no or zero.', 'Summary files overlap. Do not add their totals or infer population rates.', 'Category codes are preserved without guessed expansions.'], {'archive_member': member, 'archive_member_sha256': sha(z.read(member)), 'method': 'CSV parsed and written with identical field values; empty index header renamed.', 'joined_rows': len(main), 'quarters_present': quarters}, 'CRB Right to Know · October 2026', years, 'An individually downloadable table from the Citizen Review Board’s October 2026 Right-to-Know archive.')
            if 'n' in rows[0] and all(re.fullmatch(r'\d+', r['n']) for r in rows):
                total = sum(int(r['n']) for r in rows)
                record['validation'].update(sum_n=total, equals_joined_row_count=total == len(main))
            results.append(record)
    return results

def water(output, source):
    import fitz
    doc = fitz.open(output / 'sources' / source['local_file'])
    text = doc[15].get_text().split('Table 8 Syracuse')[1].split('Table 9 Number')[0]
    rows = []
    for index, month in enumerate(MONTHS):
        match = re.search(month + r'\s+' + r'\s+'.join([r'(\d+\.\d+)'] * 6), text)
        assert match, month
        values = match.groups()
        for intake, maximum, minimum, average in [(1, values[0], values[1], values[4]), (2, values[2], values[3], values[5])]:
            assert Decimal(minimum) <= Decimal(average) <= Decimal(maximum)
            rows.append({'year': '2025', 'month': str(index + 1), 'month_name': month, 'intake': str(intake), 'maximum': maximum, 'minimum': minimum, 'average': average, 'unit': 'NTU', 'source_table': '8', 'pdf_page': '16', 'printed_page': '10'})
    assert len(rows) == 24
    result = save_table(output, source, 'water-2025-monthly-turbidity', 'Raw water turbidity · 2025', rows, 'Water & environment', 'January–December 2025', ['DataCuse extraction of Table 8 only; this is raw intake water, not a tap-water compliance assessment.', 'The reported cumulative averages are 0.49 NTU (intake 1) and 0.67 NTU (intake 2); these are not recomputed from the rounded monthly values.'], {'pdf_page': 16, 'printed_page': '10', 'table': 8, 'method': 'Text-layer extraction; month rows and six measurement columns verified against rendered table.', 'cumulative_average_ntu': {'intake_1': '0.49', 'intake_2': '0.67'}}, 'Water quality report · 2025', ['2025'], 'Monthly maximum, minimum and average turbidity for each Skaneateles raw-water intake.')
    result['validation']['monthly_ranges_valid'] = True
    results = [result]
    text = doc[30].get_text()
    for table, title in [(19, 'Trihalomethanes'), (20, 'Haloacetic acids (5)')]:
        section = text.split('Table ' + str(table))[1]
        if table == 19:
            section = section.split('Table 20')[0]
        sites = ['4000 East Genesee St.' if table == 19 else '400 East Genesee St.', 'Fuel Hub Truck Stop', 'Functional Comm. Corp.', 'McChesney Center', 'Quarterly Average (All Sites)']
        rows = []
        for label, date in [('February 27', '2025-02-27'), ('May 20', '2025-05-20'), ('August 27', '2025-08-27'), ('December 10', '2025-12-10')]:
            match = re.search(label + r'\s+' + r'\s+'.join([r'(\d+\.\d+)'] * 5), section)
            assert match, (table, label)
            for site, value in zip(sites, match.groups()):
                rows.append({'sample_date': date, 'site_as_printed': site, 'measure': title, 'value': value, 'unit': 'ug/L', 'row_type': 'reported_average' if site == sites[-1] else 'site_measurement', 'source_table': str(table), 'pdf_page': '31', 'printed_page': '25'})
        annual = re.search(r'Locational\s+Annual\s+Average\s+' + r'\s+'.join([r'(\d+\.\d+)'] * 4), section)
        assert annual
        results.append(save_table(output, source, 'water-2025-table-' + str(table), title + ' · 2025', rows, 'Water & environment', 'Four sampling dates in 2025', ['DataCuse extraction. Reported site values and quarterly averages are separate row types.', 'Site address is preserved as printed: Table 19 says 4000 East Genesee; Table 20 says 400 East Genesee. No silent correction.', 'This table alone cannot establish current water safety.'], {'pdf_page': 31, 'printed_page': '25', 'table': table, 'method': 'Text-layer extraction with fixed table, dates, column counts and source-page review.', 'locational_annual_averages_ug_l': dict(zip(sites[:4], annual.groups())), 'footnote': '40/30 Certification Exemption per Disinfection Byproducts Rules: <40 ug/L' if table == 19 else 'No table-specific footnote printed.'}, 'Water quality report · 2025', ['2025'], 'Four sites and the report’s quarterly averages, with units and source table references.'))
    return results

def run(source_dir, manifest, output):
    sources = json.loads(manifest.read_text(encoding='utf-8'))
    reviewed = json.loads((ROOT / 'config/reviewed-sources.json').read_text(encoding='utf-8'))
    rows = []
    for source in sources:
        file = source_dir / source['local_file']
        digest = sha(file.read_bytes())
        if reviewed.get(source['local_file']) != digest:
            raise ValueError('Unreviewed source version: ' + source['local_file'] + '. Preserve approved extracts; inspect candidate first.')
        source['sha256'] = digest
        source.setdefault('checked_at', datetime.fromtimestamp(file.stat().st_mtime, timezone.utc).isoformat())
        dest = output / 'sources' / file.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if file.resolve() != dest.resolve():
            shutil.copy2(file, dest)
        rows.extend(budget(output, source) if file.suffix == '.xlsx' else crb(output, source) if file.suffix == '.zip' else water(output, source))
    dump(output / 'extracted.json', rows)
    dump(output / 'sources/manifest.json', sources)
    print(f'{len(rows)} verified tables; {sum(r["record_count"] for r in rows):,} rows (overlapping tables, not unique observations).')

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--source-dir', type=Path, default=ROOT / 'sources')
    p.add_argument('--manifest', type=Path, default=ROOT / 'sources/manifest.json')
    p.add_argument('--output', type=Path, default=ROOT)
    a = p.parse_args()
    run(a.source_dir, a.manifest, a.output)
