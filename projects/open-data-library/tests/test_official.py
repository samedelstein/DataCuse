import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import catalog
from official import augment, identity

class OfficialReferenceTests(unittest.TestCase):
    def test_reference_resolution_deduplicates_layers_and_reports_failures(self):
        entries=[{'identifier':'https://www.arcgis.com/home/item.html?id='+item+'&sublayer=0',
                  'landingPage':'https://data.syr.gov/datasets/'+item+'_0', 'title':title}
                 for item,title in [('a','Code Violations'),('a','Same layer alias'),('b','Portal page'),('c','Missing entry')]]
        self.assertEqual(identity(entries[0]),('a','0'))
        service={'url':'https://example.org/FeatureServer','id':'service','item_id':'a','name':'Code_Violations','layers':[{'id':0,'name':'Cases'}]}
        def fake(url,path):
            result={'checked_at':'2026-11-02T00:00:00Z','sha256':'fixture'}
            if '/items/a?' in url:
                result['data']={'type':'Feature Service','url':service['url'],'title':'Cases'}
            elif '/items/b?' in url:
                result['data']={'type':'Hub Page'}
            elif '/items/c?' in url:
                result['error']='Item unavailable'
            else:
                result['data']={'fields':[{'name':'ObjectId','type':'esriFieldTypeOID'}],'objectIdField':'ObjectId'}
            return result
        with tempfile.TemporaryDirectory() as temporary, patch.object(catalog,'get',side_effect=fake):
            rows, report=augment({'checked_at':'2026-11-02','data':{'dataset':entries}},[],[service],Path(temporary))
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['membership'],'official-catalog')
        self.assertEqual(rows[0]['portal_url'],entries[0]['landingPage'])
        self.assertEqual(len(rows[0]['portal_references']),2)
        self.assertEqual(rows[0]['fields'][0]['name'],'ObjectId')
        self.assertEqual(report['referenced_layers'],1)
        self.assertEqual(len(report['non_feature_resources']),1)
        self.assertEqual(report['failures'][0]['title'],'Missing entry')

if __name__=='__main__': unittest.main()
