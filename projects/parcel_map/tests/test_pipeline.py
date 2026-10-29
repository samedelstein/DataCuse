import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))
from build_data import deduplicate, number, rings, reliable_units, owner_keys, persistent_vacancy


class PipelineTests(unittest.TestCase):
    def test_duplicates_excluded_rather_than_silently_overwritten(self):
        records = [{'properties': {'TAX_ID': i}} for i in ['001', '001', '002', ' ']]
        unique, duplicate = deduplicate(records)
        self.assertEqual(list(unique), ['002'])
        self.assertEqual(duplicate, {'001': 2})

    def test_missing_and_nonfinite_values_are_not_zero(self):
        for value in [None, '', ' ', 'NaN', 'Infinity', -1]:
            self.assertIsNone(number(value))
        self.assertEqual(number('0'), 0)

    def test_polygon_holes_and_multipolygon_parts_are_retained(self):
        ring = [[-76.15, 43.05, 0], [-76.14, 43.05, 0], [-76.15, 43.06, 0], [-76.15, 43.05, 0]]
        self.assertEqual(len(rings({'type': 'Polygon', 'coordinates': [ring, ring]})), 2)
        self.assertEqual(len(rings({'type': 'MultiPolygon', 'coordinates': [[ring], [ring]]})), 2)
        self.assertEqual(rings(None), [])

    def test_zero_units_in_residential_record_are_not_comparable(self):
        self.assertIsNone(reliable_units('Apartment', '0', True))
        self.assertEqual(reliable_units('Parks', '0', True), 0)

    def test_owner_reordering_and_qualifiers_remain_distinct(self):
        a = owner_keys('1', 'SMITH JOHN', {})
        b = owner_keys('1', 'JOHN SMITH', {})
        c = owner_keys('1', 'JOHN SMITH TRUST', {})
        self.assertNotEqual(a[0], b[0])
        self.assertEqual(a[1], b[1])
        self.assertNotEqual(a[1], c[1])
        self.assertEqual(a[2], c[2])
        self.assertEqual(owner_keys('1', 'JOHN', {})[2], None)
        review = {'1': {'names': ['SMITH JOHN', 'JOHN SMITH TRUST']}}
        self.assertEqual(owner_keys('1', 'SMITH JOHN', review)[3], owner_keys('1', 'JOHN SMITH TRUST', review)[3])
        self.assertIsNone(owner_keys('2', 'SMITH JOHN', review)[3])
        self.assertIsNone(owner_keys('1', 'JANE SMITH', review)[3])

    def test_persistent_vacancy_excludes_missing_and_interrupted_histories(self):
        vacant = ['Vacant Land', None, None, None, None, 'Y']
        occupied = ['Single Family', None, None, None, None, 'N']
        blank = ['Vacant Land', None, None, None, None, ' ']
        history = {'all': [vacant]*3, 'interrupted': [vacant,occupied,vacant], 'missing': [vacant,None,vacant], 'blank': [vacant,blank,vacant]}
        snapshots = [{'useComparable': True, 'sourceFields': {'vacancy':'VacantBuil'}}]*3
        result = persistent_vacancy(history,snapshots,list(history))
        self.assertEqual(result['land']['indices'], [0,3])
        self.assertEqual(result['building']['indices'], [0])
        self.assertEqual(persistent_vacancy(history, [], list(history))['land']['indices'], [])


if __name__ == '__main__':
    unittest.main()
