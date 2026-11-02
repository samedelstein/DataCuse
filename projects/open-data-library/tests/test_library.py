import csv
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import unquote, urlsplit
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tools')]
import catalog
from download_arcgis import export

class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]
    def handle_starttag(self,tag,attrs):
        for name,value in attrs:
            if name in ('href','src'): self.links.append(value)

class CatalogTests(unittest.TestCase):
    def test_matching_id_and_normalized_url(self):
        self.assertEqual(catalog.membership('https://example.org/A%20B/FeatureServer/2','abc',{'https://example.org/a b/featureserver/2'},set()),'official-catalog')
        self.assertEqual(catalog.membership('https://x/FeatureServer/2','abc',set(),{('abc','2')}),'official-catalog')
        self.assertEqual(catalog.membership('https://x/FeatureServer/3','abc',set(),{('abc','2')}),'no-catalog-match')
    def test_years_not_hash_fragments(self):
        self.assertEqual(catalog.title_years('Route_2024_a2058b'),['2024'])
    def test_change_report(self):
        old={'datasets':[{'id':'one','availability':'available','membership':'no-catalog-match','fields':[{'name':'old'}]},{'id':'gone'}]}
        new={'datasets':[{'id':'one','availability':'unavailable','membership':'official-catalog','fields':[{'name':'new'}]}]}
        kinds={r['change'] for r in catalog.differences(old,new)}
        self.assertEqual(kinds,{'availability','membership','fields','not-listed-this-check'})
    def test_failed_refresh_preserves_baseline(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); baseline=root/'approved.json'; original='{"datasets": []}'
            baseline.write_text(original)
            with patch.object(catalog,'get',return_value={'error':'429 after retry budget'}):
                with self.assertRaises(SystemExit): catalog.collect(root/'candidate',baseline)
            self.assertEqual(baseline.read_text(),original)
            self.assertFalse((root/'candidate/catalog.json').exists())

class RetrievalTests(unittest.TestCase):
    def fake(self,mode='ok'):
        calls={'counts':0}
        def fetch(url,p):
            if not url.endswith('/query'): return {'objectIdField':'id','fields':[{'name':'id'},{'name':'value'}],'maxRecordCount':2}
            if p.get('returnCountOnly'):
                calls['counts']+=1
                return {'count':6 if mode=='changed' and calls['counts']>1 else 5}
            if p.get('returnIdsOnly'): return {'objectIds':[1,2,3,4,5]}
            ids=list(map(int,p['objectIds'].split(',')))
            if mode=='missing': ids=ids[:-1]
            if mode=='duplicate': ids=[ids[0]]*len(ids)
            return {'features':[{'attributes':{'id':i,'value':None if i==1 else i}} for i in ids], 'exceededTransferLimit':mode=='truncated'}
        return fetch
    def test_complete_and_bounded(self):
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)/'data.csv'
            self.assertTrue(export('https://x/0',['value'],'1=1',out,10,self.fake())['complete'])
            result=export('https://x/0',['value'],'1=1',out,3,self.fake())
            self.assertFalse(result['complete']); self.assertEqual(result['retrieved'],3)
    def test_incomplete_never_written_as_complete(self):
        for mode in ['missing','duplicate','truncated','changed']:
            with self.subTest(mode=mode),tempfile.TemporaryDirectory() as t:
                out=Path(t)/'data.csv'
                with self.assertRaises(RuntimeError): export('https://x/0',['value'],'1=1',out,10,self.fake(mode))
                self.assertFalse(out.exists())
    def test_unknown_field(self):
        with self.assertRaises(ValueError): export('https://x/0',['owner_name'],'1=1',Path('unused.csv'),10,self.fake())

class ArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.rows=json.loads((ROOT/'catalog-full.json').read_text(encoding='utf-8'))['datasets']
    def test_discovery_is_small_complete_and_resolvable(self):
        import gzip
        from urllib.parse import urlsplit
        data=(ROOT/'catalog.json').read_bytes()
        discovery=json.loads(data)
        # Regression budget: avoid shipping schemas/domains to discovery clients.
        self.assertLess(len(data),650000)
        self.assertLess(len(data),len((ROOT/'catalog-full.json').read_bytes())/5)
        self.assertEqual(discovery['dataset_count'],len(self.rows))
        self.assertEqual([r['id'] for r in discovery['datasets']],[r['id'] for r in self.rows])
        self.assertEqual(gzip.decompress((ROOT/'catalog-full.json.gz').read_bytes()),(ROOT/'catalog-full.json').read_bytes())
        for summary in discovery['datasets']:
            relative=urlsplit(summary['metadata_url']).path.split('/projects/open-data-library/',1)[1]
            meta=json.loads((ROOT/relative).read_text(encoding='utf-8'))
            self.assertEqual(summary['description'],meta['description'][:240])
            self.assertTrue(meta['fields'])
            for key in ('id','title','availability','membership','checked_at','coverage'):
                self.assertEqual(summary[key],meta[key])

    def test_machine_human_consistency(self):
        self.assertEqual(len(self.rows),len({r['id'] for r in self.rows}))
        for r in self.rows:
            meta=json.loads((ROOT/'datasets'/r['id']/'metadata.json').read_text(encoding='utf-8'))
            for key in r: self.assertEqual(meta[key],r[key],(r['id'],key))
            self.assertIn(r['source_url'],meta['prompt']) if r['format']=='ArcGIS API' else self.assertIn(r['download'],meta['prompt'])
    def test_csv_shapes_and_checksums(self):
        import hashlib
        for r in self.rows:
            if not r.get('download'): continue
            blob=(ROOT/r['download']).read_bytes()
            self.assertEqual(hashlib.sha256(blob).hexdigest(),r['download_sha256'])
            self.assertEqual(hashlib.sha256((ROOT/r['original']).read_bytes()).hexdigest(),r['source_sha256'])
            with (ROOT/r['download']).open(encoding='utf-8',newline='') as f:
                reader=csv.DictReader(f); records=list(reader)
            self.assertEqual(len(records),r['record_count'])
            self.assertEqual(reader.fieldnames,[f['name'] for f in r['fields']])
            self.assertTrue(all(None not in record for record in records))
    def test_water_source_values_and_units(self):
        with (ROOT/'downloads/water-2025-monthly-turbidity.csv').open(encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),24)
        self.assertEqual(rows[0]['maximum'],'0.46')
        self.assertEqual(rows[1]['average'],'0.47')
        self.assertEqual(rows[-1]['maximum'],'4.20')
        self.assertEqual({r['unit'] for r in rows},{'NTU'})
        self.assertEqual({r['pdf_page'] for r in rows},{'16'})
    def test_budget_periods_and_crb_total(self):
        with (ROOT/'downloads/budget-2026-general-fund.csv').open(encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f))
        self.assertEqual({r['value_type'] for r in rows},{'Actual','Budget','Estimate','Proposed'})
        self.assertEqual(next(r['value'] for r in rows if r['source_cell']=='N2'),'354521743')
        with (ROOT/'downloads/crb-rtk-arrest-count.csv').open(encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f))
        self.assertEqual(sum(int(r['n']) for r in rows),22947)
        self.assertIn('NA',{r['arrest_type'] for r in rows})
    def test_local_links_exist(self):
        missing=[]
        for p in ROOT.rglob('*.html'):
            if 'candidate' in p.parts: continue
            parser=Links(); parser.feed(p.read_text(encoding='utf-8'))
            for href in parser.links:
                url=urlsplit(href)
                if url.scheme or not url.path: continue
                target=(p.parent/unquote(url.path)).resolve()
                if not target.is_relative_to(ROOT.resolve()): continue
                if not target.exists(): missing.append((str(p.relative_to(ROOT)),href))
        self.assertEqual(missing,[])

if __name__=='__main__': unittest.main()
